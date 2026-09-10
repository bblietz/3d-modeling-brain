---
name: user-printer-hardware
description: "Brian's printer is a Bambu Lab X2D with AMS 2 Pro; nozzles owned 0.2, 0.4, 0.6 and 0.6 high-flow (all hardened steel); pick the nozzle when advising on best results"
metadata: 
  node_type: memory
  type: user
  originSessionId: 5c1de18d-a9c6-4689-9468-bd56351ceced
  modified: 2026-09-10T16:00:22.907Z
---

Brian prints on a Bambu Lab X2D with an AMS 2 Pro (max 4 colors per print). Nozzles owned: 0.2 mm, 0.4 mm, 0.6 mm, and 0.6 mm high-flow ("speed nozzle"), all hardened steel. The 0.6 high-flow is normally installed; the 0.4 was installed for the Sharks nametag (Aug 2026); the 0.2 mm nozzles arrived Aug 2026.

**How to apply:** when suggesting how to get the best result, say which nozzle fits the job and why, using all four: 0.2 for hairline detail and small raised text when a 3 to 4x print time is acceptable (Bambu caps PETG at 2 mm3/s there), 0.4 for fine detail at normal speed (arachne walls get raised art down to ~0.5 mm), 0.6 / 0.6 HF for speed and strength on coarse parts. Full rules and per-nozzle floors: knowledge/printer-x2d.md. See also [[feedback-agentic-os-conventions]].

**Installed now (printer-verified 2026-09-10):** main/direct-drive nozzle id 1 is **0.6 mm HH01, hardened steel HIGH FLOW**; auxiliary/Bowden nozzle id 0 is 0.6 mm HS01, hardened steel standard flow. Was 0.2 in both from 2026-08-23, 0.4 from 2026-08-06 (Sharks nametag), 0.6 high-flow before that.

**Never state the installed nozzle from this note alone - it goes stale.** Run `scripts/x2d-status.py` and read `device.nozzle.info[].type`. That check caught this note being a full nozzle generation out of date on 2026-09-10, after it had already been written into a project's pre-flight as "swap back to 0.6".
