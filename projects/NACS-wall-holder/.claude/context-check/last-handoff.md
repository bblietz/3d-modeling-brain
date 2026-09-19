---
type: handoff
project: NACS-wall-holder
date: 2026-09-18
---

# NACS wall holder handoff (2026-09-18, v7 validated, full part sliced)

## State
- `holder.scad` v7: cavity is the swept room of grip-up docking (`dock_tilt = 12`, `dock_top = 0.1`), roof 0.5 mm over the tip, end wall leaning back 12 degrees, `mouth_z = 37.68`. `roof_extra`, `roof_relief`, `tight_len`, `bell_extra`, `cleat_scale` removed.
- `coupon.stl` / `coupon-print.3mf` regenerated (72 x 67 x 57 mm, 1 h 36 min, 59 g). Long-cleat coupon files removed (history: f0ea071).
- `pipeline/insertion.py`: WAY IN yes (wand grown 0.2 mm), HOLD 19.6 mm load rise, 1.87 of 3.57 mm edge engaged when hanging.
- Page: https://claude.ai/artifact/TzbzpN4voPdJoeMWF8jHRw (version 9). OCP viewer shows the new coupon.

## Decisions already locked
- Fixed cleat in the lock pocket on the lower wall, no spring tab; button up; wand 45 down, 15 off the wall; drum 75; cleat 1.25 in from the opening; Tesla T on the flange.
- Cleat stays the pocket-filling wedge (5.9 x 3.57 mm, 15 degree overhang); the 50% longer cleat is retired (Brian, 2026-09-18).
- v7 cavity, cleat and docking are validated by print and locked. Docking is grip up, nose in, grip down; the step roof is abandoned because it cannot both admit and hold the wand (brief.md, Cavity v7).
- OpenSCAD only; renders from the real model; run `pipeline/insertion.py` after any cavity, cleat or angle change.

## Done since
- v7 coupon printed: fits and holds (Brian: "the last coupon printed great. This is the one.").
- Full part: `holder.stl`, `holder-print.3mf` (150 mm base, solid screw pads verified in G-code, 7 h 47 min, 366 g, 3 walls, 20% gyroid), cavity cut stopped at the flange underside, page version 10, retrospective in knowledge/learnings/nacs-wall-holder.md.

## Open
- Brian to print the full part, mount it, try the wand in the deep opening with the cable on the drum.
- After the full print: add the result to the retrospective.
