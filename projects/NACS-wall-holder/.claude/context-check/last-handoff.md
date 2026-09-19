---
type: handoff
project: NACS-wall-holder
date: 2026-09-18
---

# NACS wall holder handoff (2026-09-18, 4 in base, round flange, step-free entry, 1/16 in roundovers, sliced)

## State
- `holder.scad`: v7 cavity (swept room of grip-up docking, `dock_tilt = 12`, `dock_top = 0.1`), sides and roof flaring 0.1 per mm from the nose shoulder to the rim (`flare(a)`), floor kept on Tesla's line to the end of the housing CAD then a 4 mm ramp (`floor_knee`). Body: `plate_w = 101.6`, `plate_r = 10`, `drum_r = 40`, round flange diameter 104 (no point, no driver hole), `mouth_z = 37.92`, `cut_top = 68.4`. Roundovers `edge_r = 25.4 / 16`: plate top edge, both flange rims (in `drum_profile()`), and the mouth's rim from the generated `rim_round.scad` (`pipeline/rim_round.py`).
- `holder.stl` (104 x 104 x 80 mm, one watertight body, 370 cm3) and `holder-print.3mf`: 5 h 32 min, 241 g, 267 layers, pads 0.89 to 0.90, plain plate 0.19, prime tower at (212, 180), 26.6 mm from the part and its tree supports.
- `pipeline/insertion.py` on this model: WAY IN yes (wand grown 0.2 mm, tilt 0 to +9), hanging tip 3.37 mm from the end wall, tilt -3.5, 1.75 of 3.57 mm engaged, HOLD 20.4 mm. Before the floor lip was rounded these were the printed coupon's numbers exactly (3.20, -3.0, 1.87, 19.6).
- Page: https://claude.ai/artifact/TzbzpN4voPdJoeMWF8jHRw. OCP viewer was pushed the 4 in holder.
- `coupon.stl` / `coupon-print.3mf` are the printed, validated coupon and were NOT regenerated; the coupon renders in `images/scad/` come from the current model.

## Decisions already locked
- Fixed cleat in the lock pocket on the lower wall, no spring tab; button up; wand 45 down, 15 off the wall; drum 75 long; cleat 1.25 in from the opening; Tesla T on the flange.
- Cleat stays the pocket-filling wedge (5.9 x 3.57 mm, 15 degree overhang); the 50% longer cleat is retired (Brian, 2026-09-18).
- v7 cavity, cleat and docking are validated by print and locked (Brian: "preserve the wand holder size, as this is perfect"). Docking is grip up, nose in, grip down.
- The cavity floor is a functional surface: it carries the hanging wand. Do not flare or relieve it inside the end of Tesla's housing CAD; doing so changes the hang (brief.md, Smooth entry).
- Base 4 in square (Brian, 2026-09-18), body shrunk round the true-size cavity; solid infill round the screw holes.
- Flange is round, no pointed corner (Brian, 2026-09-18).
- Every outside edge rounded at least 1/16 in except the plate's back edge and the screw holes (Brian, 2026-09-18). The cleat and the T's outline stay sharp (my call, reported to him).
- After any change to the cavity, drum, blends or `edge_r`: `zbudget.py`, then `rim_round.py`, then `insertion.py`.
- OpenSCAD only; renders from the real model; run `pipeline/insertion.py` after any cavity, cleat or angle change.
- Do not open or close Bambu Studio windows unless Brian asks.

## Open
- Brian to confirm the reading of "reduce the size" (drum 80 and flange 104, not only a smaller plate).
- Brian to accept or reject the small change in the hang from the rounded floor lip (3.5 degrees, 1.75 mm engaged); the alternative is to leave the floor stretch of the rim sharp.
- Brian's Studio session had the 150 mm `holder-print.3mf` open (title with unsaved changes); the file on disk is now the 4 in version, so it must be reopened, not saved over.
- Brian to print the 4 in part, mount it, try the wand with the cable on the drum; then add the result to the retrospective.
