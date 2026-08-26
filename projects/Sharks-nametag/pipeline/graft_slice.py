"""Offline slice of a Sharks-nametag 3MF with the Bambu CLI ("graft", mode B).

The CLI-assembled 3MFs (coupons02.py, fillcore_coupons.py, plates.py) carry
a flattened preset config that Studio completes on load; `bambu-studio
--slice` does not, and refuses the file (rc 156 or an empty gcode) until the
missing pieces are there. The graft keeps the file's OWN project_settings
(so a 0.2 file slices with its 0.2 presets) and adds only the keys that are
missing or empty compared with a config Studio itself saved
(`pipeline/studio-live-settings.json`: host, notes, gcode placeholders, bed
areas, extruder stats, filament_colour_type, ...), reshapes filament_map and
filament_nozzle_map to one entry per filament, and makes sure the plate
block of model_settings.config lists a <model_instance> per object. Then
`bambu-studio --slice 1 --export-3mf out.3mf in.3mf` (absolute paths).

A harmless "could not found extruder_type Bowden" log error can appear.

Usage: graft_slice.py <in.3mf> <out.3mf> [--plate N]   (out.3mf holds Metadata/plate_N.gcode, N = 1)
Module: graft_slice(src, dst, plate=1) -> dict(rc, layers, time, seconds, gcode)
"""
import json
import os
import re
import subprocess
import sys
import zipfile

PIPE = os.path.dirname(os.path.abspath(__file__))
LIVE = f"{PIPE}/studio-live-settings.json"


def _empty(v):
    return v is None or v == "" or v == []


def graft_config(cfg, live):
    """Return (patched cfg, list of added keys)."""
    added = []
    for k, v in live.items():
        if k not in cfg or _empty(cfg[k]):
            if _empty(v) and k in cfg:
                continue
            cfg[k] = v
            added.append(k)
    n = len(cfg["filament_colour"])
    for k in ("filament_map", "filament_nozzle_map"):
        cur = cfg.get(k)
        if not isinstance(cur, list) or len(cur) != n:
            lv = live.get(k)
            if isinstance(lv, list) and len(lv) == n:
                cfg[k] = list(lv)
            else:
                cfg[k] = [(cur[0] if isinstance(cur, list) and cur else "1")] * n
            added.append(k)
    return cfg, added


def ensure_instances(model):
    """Add a <model_instance> to the plate block for every object missing one."""
    ids = re.findall(r'<object id="(\d+)">', model)
    listed = re.findall(r'<metadata key="object_id" value="(\d+)"/>', model)
    missing = [i for i in ids if i not in listed]
    if not missing:
        return model, 0
    used = [int(x) for x in re.findall(r'<metadata key="identify_id" value="(\d+)"/>', model)]
    nxt = (max(used) + 1) if used else 113
    block = ""
    for i in missing:
        block += ("    <model_instance>\n"
                  f'      <metadata key="object_id" value="{i}"/>\n'
                  '      <metadata key="instance_id" value="0"/>\n'
                  f'      <metadata key="identify_id" value="{nxt}"/>\n'
                  "    </model_instance>\n")
        nxt += 1
    assert "  </plate>" in model, "no plate block"
    model = model.replace("  </plate>", block + "  </plate>", 1)
    return model, len(missing)


def parse_gcode_header(gcode):
    """total layer number and total estimated time from a Bambu plate gcode."""
    head = gcode[:20000]
    m_layers = re.search(r"; total layer number:\s*(\d+)", head)
    m_time = re.search(r"; total estimated time:\s*([^;\n]+)", head)
    layers = int(m_layers.group(1)) if m_layers else None
    tstr = m_time.group(1).strip() if m_time else None
    secs = None
    if tstr:
        secs = 0
        for val, unit in re.findall(r"(\d+)\s*([dhms])", tstr):
            secs += int(val) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[unit]
    return layers, tstr, secs


def graft_slice(src, dst, keep_grafted=False, plate=1):
    src, dst = os.path.abspath(src), os.path.abspath(dst)
    work = os.path.dirname(dst)
    os.makedirs(work, exist_ok=True)
    with open(LIVE) as f:
        live = json.load(f)
    grafted = os.path.join(work, os.path.basename(dst).replace(".3mf", "") + "-grafted.3mf")
    with zipfile.ZipFile(src) as zin:
        cfg = json.loads(zin.read("Metadata/project_settings.config"))
        cfg, added = graft_config(cfg, live)
        model = zin.read("Metadata/model_settings.config").decode()
        model, n_inst = ensure_instances(model)
        with zipfile.ZipFile(grafted, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "Metadata/project_settings.config":
                    zout.writestr(item, json.dumps(cfg, indent=4))
                elif item.filename == "Metadata/model_settings.config":
                    zout.writestr(item, model)
                else:
                    zout.writestr(item, zin.read(item.filename))
    if os.path.exists(dst):
        os.remove(dst)
    r = subprocess.run(["bambu-studio", "--slice", str(plate), "--export-3mf", dst, grafted],
                       capture_output=True, text=True, timeout=1800, cwd=work)
    log = dst.replace(".3mf", "") + "-slice.log"
    with open(log, "w") as f:
        f.write(r.stdout)
        f.write("\n--- stderr ---\n")
        f.write(r.stderr)
    res = {"rc": r.returncode, "added_keys": added, "instances_added": n_inst, "log": log,
           "layers": None, "time": None, "seconds": None, "gcode": None, "out": dst}
    if r.returncode == 0 and os.path.exists(dst):
        with zipfile.ZipFile(dst) as z:
            names = z.namelist()
            if f"Metadata/plate_{plate}.gcode" in names:
                g = z.read(f"Metadata/plate_{plate}.gcode").decode(errors="ignore")
                res["layers"], res["time"], res["seconds"] = parse_gcode_header(g)
                res["gcode"] = f"Metadata/plate_{plate}.gcode"
    if not keep_grafted:
        os.remove(grafted)
    return res


if __name__ == "__main__":
    args = sys.argv[1:]
    plate = 1
    if "--plate" in args:
        i = args.index("--plate")
        plate = int(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    res = graft_slice(args[0], args[1], plate=plate)
    print(f"rc {res['rc']}  layers {res['layers']}  total estimated time {res['time']}  "
          f"(+{len(res['added_keys'])} keys grafted, {res['instances_added']} instances added)  log {res['log']}")
    if res["rc"] != 0 or not res["gcode"]:
        sys.exit(1)
