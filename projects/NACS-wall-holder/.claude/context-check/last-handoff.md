---
type: handoff
project: NACS-wall-holder
date: 2026-09-19
---

# NACS wall holder handoff (2026-09-19, PROJECT CLOSED)

## State
Done. Brian: "charger holder is on the wall and working great." The mounted part is the
final one committed in 9585fc0: v7 cavity (grip up, nose in, grip down docking on a fixed
cleat), 4 in base, round flange, 1/16 in roundovers on every outside edge except the plate's
back and the screw holes. `holder.scad`, `holder.stl`, `holder-print.3mf` on disk match what
was printed. Full history in brief.md; final result in knowledge/learnings/nacs-wall-holder.md.

## Decisions locked (all confirmed by the real print)
- Fixed cleat in the lock pocket on the lower wall, no spring tab; button up; wand 45 down,
  15 off the wall; drum 75 long, radius 40; cleat 1.25 in from the opening; round flange
  diameter 104; Tesla T on the flange.
- Cavity is the swept room of grip-up docking (`dock_tilt = 12`); sides and roof flare 0.1
  per mm past the nose shoulder; the floor keeps Tesla's line and does not flare.
- Base 4 in square, body shrunk round the unchanged cavity; solid infill round the screw
  holes; every outside edge has a 1/16 in rolling-ball roundover except the plate's back and
  the screw holes (`pipeline/rim_round.py` for the mouth's rim).
- Reusable tools for any future revision: `pipeline/insertion.py` (docking/hold check),
  `pipeline/zbudget.py` (depth budget), `pipeline/rim_round.py` (rim roundover), `render.sh` /
  `renders_page.py` (page at https://claude.ai/artifact/TzbzpN4voPdJoeMWF8jHRw).

## Open
None. Project closed. If Brian asks for a change, treat it as a new request against this
locked baseline, not a resumption of open work.
