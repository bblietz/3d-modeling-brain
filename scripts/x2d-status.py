#!/usr/bin/env python
"""Read-only status snapshot of the Bambu Lab X2D over LAN MQTT.

Sends ONLY status requests (pushing.pushall, info.get_version). Never a
control command. Works with the printer in cloud mode; Developer Mode is
not needed for reads (verified 2026-08-20).

Credentials: the LAN access code is read from Bambu Studio's live config
(~/.config/BambuStudioBeta/BambuStudio.conf, key access_code.<serial>);
override with env X2D_ACCESS_CODE. IP and serial default to the printer
discovered 2026-08-20 (knowledge/x2d-printer-control.md); override with
X2D_IP / X2D_SERIAL.

Usage (vault root):
  .venv/bin/python scripts/x2d-status.py            # summary
  .venv/bin/python scripts/x2d-status.py --raw DIR  # also dump raw JSON
  .venv/bin/python scripts/x2d-status.py --seconds 25
Needs paho-mqtt (installed in the vault .venv).
"""
import argparse, json, os, ssl, sys, time
from pathlib import Path

import paho.mqtt.client as mqtt

DEFAULT_IP = "192.168.1.68"
DEFAULT_SERIAL = "20P6AJ641301478"
CONF = Path.home() / ".config/BambuStudioBeta/BambuStudio.conf"


def access_code(serial):
    code = os.environ.get("X2D_ACCESS_CODE")
    if code:
        return code
    try:
        conf = json.load(open(CONF))
    except Exception as e:
        sys.exit(f"cannot read {CONF}: {e}; set X2D_ACCESS_CODE")
    code = conf.get("access_code", {}).get(serial)
    if not code:
        sys.exit(f"no access_code.{serial} in {CONF}; set X2D_ACCESS_CODE")
    return code


def decode_nozzle(t):
    flow = {"S": "standard flow", "H": "high flow"}.get(t[1:2], "?")
    mat = {"00": "stainless steel", "01": "hardened steel"}.get(t[2:4], "?")
    return f"{t} ({mat}, {flow})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", metavar="DIR", help="dump every raw message as JSON into DIR")
    ap.add_argument("--seconds", type=float, default=15.0)
    a = ap.parse_args()
    ip = os.environ.get("X2D_IP", DEFAULT_IP)
    serial = os.environ.get("X2D_SERIAL", DEFAULT_SERIAL)
    code = access_code(serial)
    msgs = []

    def on_connect(c, u, flags, rc, props=None):
        if getattr(rc, "is_failure", False) or rc not in (0,) and not hasattr(rc, "is_failure"):
            print(f"connect failed: {rc}")
            return
        c.subscribe(f"device/{serial}/report")
        time.sleep(0.5)
        for p in ({"pushing": {"sequence_id": "0", "command": "pushall", "version": 1, "push_target": 1}},
                  {"info": {"sequence_id": "0", "command": "get_version"}}):
            c.publish(f"device/{serial}/request", json.dumps(p))

    def on_message(c, u, m):
        try:
            msgs.append(json.loads(m.payload.decode("utf-8", "replace")))
        except Exception:
            pass

    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"x2d-status-{os.getpid()}", protocol=mqtt.MQTTv311)
    c.username_pw_set("bblp", code)
    c.tls_set(cert_reqs=ssl.CERT_NONE)
    c.tls_insecure_set(True)
    c.on_connect, c.on_message = on_connect, on_message
    try:
        c.connect(ip, 8883, keepalive=30)
    except Exception as e:
        sys.exit(f"MQTT connect to {ip}:8883 failed: {e!r}")
    c.loop_start()
    time.sleep(a.seconds)
    c.loop_stop()
    c.disconnect()

    if a.raw:
        os.makedirs(a.raw, exist_ok=True)
        for i, d in enumerate(msgs):
            json.dump(d, open(os.path.join(a.raw, f"report-{i:03d}.json"), "w"), indent=1)

    ver = next((d["info"] for d in msgs if "info" in d and "module" in d["info"]), None)
    st = next((d["print"] for d in reversed(msgs) if "print" in d and "ams" in d["print"]), None)
    if ver:
        mods = {m.get("name"): m.get("sw_ver") for m in ver["module"]}
        print("firmware:", ", ".join(f"{k} {v}" for k, v in mods.items() if k in ("ota", "ams/0", "ahb")))
    if not st:
        sys.exit(f"no full status received in {a.seconds}s ({len(msgs)} msgs)")
    print(f"state: {st.get('gcode_state')}  job: {st.get('subtask_name')!r}  progress: {st.get('mc_percent')}%  layer {st.get('layer_num')}/{st.get('total_layer_num')}")
    dev = st.get("device", {})
    # X2D firmware reports the chamber under device.ctc (chamber temperature control), not chamber_temper
    chamber = st.get("chamber_temper", dev.get("ctc", {}).get("info", {}).get("temp"))
    print(f"temps: bed {st.get('bed_temper')}/{st.get('bed_target_temper')}  nozzle {st.get('nozzle_temper')}/{st.get('nozzle_target_temper')}  chamber {chamber}")
    for n in dev.get("nozzle", {}).get("info", []):
        role = {0: "auxiliary (Bowden, support)", 1: "main (direct drive, AMS)"}.get(n.get("id"), "?")
        print(f"nozzle id {n.get('id')} {role}: {n.get('diameter')} mm {decode_nozzle(n.get('type', ''))}")
    print("plate:", dev.get("plate"), " airduct mode:", dev.get("airduct", {}).get("modeCur"), "(0 = cool/strong cooling)")
    ams = st.get("ams", {})
    print(f"AMS: exist_bits {ams.get('ams_exist_bits')}  tray_now {ams.get('tray_now')} (255 = nothing loaded)")
    for unit in ams.get("ams", []):
        print(f"  AMS {unit.get('id')}: humidity level {unit.get('humidity')}  temp {unit.get('temp')} C")
        for t in unit.get("tray", []):
            print(f"    slot {int(t.get('id', 0)) + 1}: {t.get('tray_type')} / {t.get('tray_sub_brands')} / {t.get('tray_info_idx')} / #{t.get('tray_color')} / remain {t.get('remain')}%")
    for t in st.get("vt_tray", []) if isinstance(st.get("vt_tray"), list) else [st.get("vt_tray")] if st.get("vt_tray") else []:
        print(f"  external slot {t.get('id')}: {t.get('tray_type')} / {t.get('tray_info_idx')} / #{t.get('tray_color')}")
    hms = st.get("hms", [])
    print(f"hms entries: {len(hms)}  print_error: {st.get('print_error')}  wifi: {st.get('wifi_signal')}")
    up = st.get("upgrade_state", {})
    if up.get("new_version_state") == 1:
        print(f"firmware update available: ota {up.get('ota_new_version_number', '?')}  ams {up.get('ams_new_version_number', '?')}")


if __name__ == "__main__":
    main()
