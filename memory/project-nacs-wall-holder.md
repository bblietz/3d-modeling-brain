---
name: project-nacs-wall-holder
description: Tesla Wall Connector wall holder - 2026-09-19 version on the wall and working; 2026-10-08 revision (deeper, crest lip, wordmark) built and sliced, not printed
metadata:
  type: project
---

Wall-mounted dock for Brian's Tesla Gen 3 Wall Connector charge handle: drum on a 4 in square
plate, flange with the Tesla T, wand out the drum's side hanging on a fixed cleat in the
connector's own lock pocket. **The 2026-09-19 print is mounted and working** ("charger holder is on
the wall and working great").

**Revision 2026-10-08, built and sliced, NOT printed:** drum 1 in deeper (100 mm) and 90 across,
cavity 1/2 in deeper (cleat 1.75 in from the opening), full-width "crest" lip 1.5 in above the
flange (shield sides, arched top) with a frame line, the T and the TESLA wordmark bent along the
arc, plain screw holes (top two behind the lip, driver at a 6 degree tilt). 8 h 37 min, 438 g.
Open: the grip's first 1/2 in now sits inside the opening with no Tesla CAD behind it; ask Brian
to measure the handle 1/2 in and 1 in behind the glossy housing before printing. Every pick was
made from rendered options on https://claude.ai/artifact/5u3wgRBUTWngnCdjFuPzKB; plan page
https://claude.ai/artifact/D2zPQ4v2W97wuq1hMqpYa6.

Project files and tools: `projects/NACS-wall-holder/` (brief.md "Revision of 2026-10-08",
`holder.scad` with `tab_style` / `emblem` / `top_mount` / `lip_text` options, `pipeline/insertion.py`
docking and hold check, `pipeline/depth_limit.py` cavity depth vs drum wall, `pipeline/rim_round.py`,
`pipeline/make_coupon_3mf.py holder`). Pipeline order after any cavity or drum change: zbudget.py,
rim_round.py, insertion.py, export, make_coupon_3mf.py. See
[[feedback-check-docking-and-hold-kinematics]] and [[feedback-html-visual-companion]].
