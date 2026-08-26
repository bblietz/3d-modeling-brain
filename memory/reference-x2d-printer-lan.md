---
name: x2d-printer-lan-access
description: Brian's X2D is readable over LAN MQTT (IP 192.168.1.68, serial 20P6AJ641301478); scripts/x2d-status.py gives nozzles, AMS trays, plate, firmware read-only
metadata:
  type: reference
---

The X2D ("Mr Poopy", serial 20P6AJ641301478) answers read-only LAN MQTT at 192.168.1.68:8883 even in cloud mode (no Developer Mode needed). `scripts/x2d-status.py` (vault .venv, paho-mqtt) prints firmware, job state, both nozzles (type + diameter), plate id, AMS tray contents. The access code is read at runtime from `~/.config/BambuStudioBeta/BambuStudio.conf` (`access_code.<serial>`), never stored in the vault. Full notes: knowledge/x2d-printer-control.md, section "Brian's X2D on the LAN". Use it for the nozzle + filament pre-flight before fine-detail prints ([[user-printer-hardware]], [[printer-x2d]]). Chamber temperature lives in `device.ctc.info.temp` on this firmware; `scripts/x2d-chamber-watch.sh` (run under a Monitor, 5 min polls) watches a print for chamber-high / progress / finish events (Brian asked for chamber monitoring during PETG prints on 2026-08-24; PETG with the vent open settles about 41 C).
