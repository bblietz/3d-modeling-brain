---
tags: [reference, printer, x2d, automation, mcp]
researched: 2026-07-30
---

# X2D printer control from software

Researched 2026-07-30 (X2D firmware 01.02.00.00 released the same day). The X2D is fully controllable on LAN once **LAN-Only Mode + Developer Mode** are enabled on the printer. It speaks the same network API as the P2S/H2D generation, so "P2S/H2D support" in a library is the real compatibility signal; an explicit "X2D" line item is rare.

## Protocols (verified)

| Channel | Details |
|---|---|
| Control/telemetry | MQTT over TLS, port 8883, user `bblp`, password = LAN access code; telemetry on `device/<serial>/report` (~1 s), commands to `device/<serial>/request` |
| File upload | FTPS (implicit TLS), port 990, same credentials |
| Camera | `rtsps://bblp:<access-code>@<ip>:322/streaming/live/1` (needs LAN Mode Liveview; about one concurrent client) |
| Print start | MQTT `print.project_file` with `url: file:///mnt/sdcard/<file>.3mf`, `param: Metadata/plate_N.gcode`, `use_ams`, `ams_mapping` (see OpenBambuAPI docs) |

## Auth situation (dated)

- Jan 2025: Bambu introduced the Authorization Control System (Bambu Connect); cloud mode became effectively read-only for third parties. After backlash, **Developer Mode** became the sanctioned third-party path: a toggle inside LAN-Only Mode that re-opens raw MQTT/FTPS/stream. Unsupported by Bambu but present in every firmware through X2D 01.02.00.00.
- X2D firmware 01.01.00.00+ supports LAN-only print-to-built-in-storage (no USB stick needed). Bambu Studio 2.5.3.60+ profiles required for X2D features.
- If integration uptime matters, disable printer auto-updates; a future firmware could narrow Developer Mode.

## Practical recipe (agent slices, uploads, prints, monitors)

1. On the printer once: enable LAN-Only Mode, then Developer Mode, then LAN Mode Liveview. Record serial + access code.
2. Slice with the `bambu-studio` CLI to a `.gcode.3mf` (pre-sliced is the verified path; CLI profile flattening per [[lego-3d-test]] learnings).
3. Upload via FTPS 990; start via MQTT `print.project_file`; monitor `device/<serial>/report`.
4. Dual-nozzle caution: `ams_mapping` for the second nozzle is the ecosystem-wide soft spot (open bugs in bambulabs_api #153 and Bambuddy #318; OpenBambuAPI does not document the dual-nozzle fields yet). Reliable route today: embed the filament mapping in the sliced 3MF and send that.

## Building blocks, ranked

| Tool | What | Verdict |
|---|---|---|
| [bambu-printer-mcp](https://github.com/DMontgomery40/bambu-printer-mcp) (npm, ~40 tools, pushed 2026-07-30) | MCP: status, FTPS upload, print_3mf, pause/resume/cancel, AMS incl. RFID auto-match and drying, camera snapshots, HMS diagnostics, STL ops | Top pick; has H2-generation fixes (AMS mapping serialization, FTP double-path). Configure with the P2S/H2D profile |
| [Bambuddy](https://github.com/maziggy/bambuddy) (2.7k stars, active) | Self-hosted Docker command center: queue, server-side slicing, camera relay, REST/webhooks, explicit X2D support | Heaviest but most complete; REST API an agent can drive |
| [ha-bambulab](https://github.com/greghesp/ha-bambulab) (2.3k stars) | Home Assistant integration; X2D supported since v2.2.22 (2026-05-12) | Best telemetry surface if HA is already running |
| [OpenBambuAPI](https://github.com/Doridian/OpenBambuAPI) | Protocol documentation (MQTT/FTPS/camera/x509) | Read before writing raw MQTT; a zero-dependency client is ~200 lines of paho-mqtt + ftplib |
| [bambulabs_api](https://github.com/BambuTools/bambulabs_api) (PyPI) | Python client with start_print | Fine for single-nozzle jobs; dual-nozzle AMS mapping untested/broken (issue #153) |

Skip: cloud-side APIs (read-only since Jan 2025), bambu-cli (archived), pybambu on PyPI (frozen; live code is vendored in ha-bambulab), unvetted marketplace skills (bambu-studio-ai, @versatly/bambu) until their code is inspected.

## Brian's X2D on the LAN (verified 2026-08-20)

- Printer "Mr Poopy", model code N6, serial 20P6AJ641301478, IP 192.168.1.50 since at least 2026-09-29 (was 192.168.1.68; wlan0, MAC 50:31:23:13:49:e6; DHCP, so the IP can move - SSDP re-finds it: printers NOTIFY on UDP 2021, or M-SEARCH `urn:bambulab-com:device:3dprinter:1` to 239.255.255.250:1990). Cloud mode (DevConnect cloud, DevBind occupied). Firmware 01.01.01.00 on 2026-08-20 with 01.02.00.00 offered.
- Open ports: 8883 MQTT TLS, 990 FTPS, 6000, 3000; 322 RTSP closed (LAN liveview off).
- LAN access code: Bambu Studio keeps it under `access_code.<serial>` in its config. Do not copy it into the vault. **The printer is the canonical source** - it is shown on the touchscreen under the network settings, and can be regenerated there (regenerating invalidates the old one, so re-pair Studio afterwards). Studio only caches whatever you typed in. On 2026-09-10 `~/.config/BambuStudioBeta/BambuStudio.conf` was found **truncated to 0 bytes** (mtime 2026-09-09 03:22), taking the cached code with it; the older `~/.config/BambuStudio/BambuStudio.conf` still held a working code. `scripts/x2d-status.py` now tries the Beta config then falls back to the older one. An empty Beta config means Studio Beta lost more than the code - check that printer bindings and custom presets are still there.
- Read-only MQTT works in cloud mode WITHOUT Developer Mode: user `bblp` + access code, TLS with cert check off, subscribe `device/<serial>/report`, publish `pushing.pushall` and `info.get_version`. `scripts/x2d-status.py` does exactly that and prints firmware, job state, temps, both nozzles, plate, AMS trays (paho-mqtt lives in the vault `.venv`). The chamber temperature is reported under `device.ctc.info.temp` on this firmware (not `chamber_temper`); `scripts/x2d-chamber-watch.sh [ALERT_C] [LOG]` polls the status every 5 min during a print and emits start / chamber-high / progress / finish lines (run it under a Monitor). Observed 2026-08-24 with PETG, bed 70 C, top vent open, chamber fan on cool: 30 C cold start, 40 C after 20 min, steady 41 C from layer 7 on. Control commands still need Developer Mode per the auth notes above (untested).
- Studio config dirs: the live 02.08.01.55 AppImage (`~/.local/bin/bambu-studio`) uses `~/.config/BambuStudioBeta/` (system bundle 02.08.00.04). `~/.config/BambuStudio/` is a stale 02.07.00.08 bundle that `scripts/flatten_presets.py` and `projects/Sharks-nametag/pipeline/flatten_04.py` still read. For the X2D 0.4 "Direct Drive Standard" variant the two bundles agreed on 2026-08-20 (02.08 only adds E3D high-flow variant slots and drops PETG `overhang_fan_speed` 90 -> 50); point the flatteners at the Beta dir when they are next touched.
- Nozzles read from the printer 2026-09-10 (firmware now ota 01.02.00.00, up from 01.01.01.00): main/direct-drive id 1 = **0.6 mm HH01, hardened steel high flow**; auxiliary/Bowden id 0 = 0.6 mm HS01. This contradicted the hardware memory note, which still said 0.2 in both positions from 2026-08-23 and had already been written into a project's pre-flight as "swap back to 0.6". Query the printer; never quote a note for what is mounted.
- Decoding the report: `device.nozzle.info[].type` "HS01" = hardened steel, standard flow (char 1 S/H = standard/high flow, chars 2-3 00/01 = stainless/hardened); extruder id 1 = main direct-drive nozzle (AMS), id 0 = auxiliary Bowden nozzle (support; printable X starts at 20.5 mm, hence the 235.5 mm dual-nozzle width); `airduct.modeCur` 0 = cool/strong cooling; AMS `tray_now` 255 = nothing loaded; `device.plate.cur_id` (e.g. P0101) is not decoded yet, so plate type cannot be confirmed remotely.
- The flow type (H/S) is a setting on the printer, not sensed from the physical nozzle: on 2026-09-12 the main 0.4 nozzle read HH01 (high flow), then HS01 (standard flow) a few hours later after Brian corrected the printer's own setting to match his actual hardware (no high-flow 0.4 owned). Both readings were accurate for their moment. Query the printer for the current setting, but if it seems to mismatch what should be mounted, ask Brian to check the printer's own nozzle-type setting rather than assuming the report is unreliable.

## Related

- [[printer-x2d]], [[lego-ai-ecosystem]], [[lego-3d-test]]
