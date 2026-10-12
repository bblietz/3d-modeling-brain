---
name: project-guitar-pick
description: "Dunlop Tortex Standard 1.0 pick copy; outline traced from caliper photos, rounded edge added 2026-10-12, PETG 0.2-nozzle 3MF slice-verified, Brian to pick the edge profile, not printed"
metadata:
  node_type: memory
  type: project
  originSessionId: 436656c6-ca45-4497-873c-df44f48e28f5
  modified: 2026-10-12T22:30:00.000Z
---

Plain PETG copy of the Dunlop Tortex Standard 1.0 mm pick (351 shape), `projects/Guitar-pick/`. On 2026-10-11 Brian measured it at 26.19 x 30.38 x 1.0 mm; the outline was traced from his two caliper photos (`pipeline/trace_photo.py`) and he approved it on the sign-off page. The measured tip radius is 4.5 mm; the generic 351 SVG outline is 3.4 mm, so the generic shape is NOT a stand-in for the Dunlop.

On 2026-10-12 Brian rejected the square edge ("the pick edges should be tapered"). `guitar_pick.build(edge)` now has round (fillet R 0.45 both faces, built into the 3MF), chamfer (45 degrees both faces) and bevel (1.5 mm Flow-style taper on top, 45 degrees underneath); the side is a smooth spline. Research: a new Tortex Standard is die-stamped square and wears into a bevel; no published edge numbers. Brian has not yet said which profile he wants.

Print file `guitar-pick.3mf` (`pipeline/make_print_3mf.py`): 0.2 mm nozzle, 0.06 mm layers so 16 layers sum to exactly 1.0 mm, solid zig-zag (gyroid is refused at 100%), seam at the top centre, no ironing, skirt, elephant-foot compensation 0 (the rounded underside takes the foot). Slice: 13 min 13 s, 0.69 g. Not printed as of 2026-10-12.

**Why:** Brian wants it as smooth as possible, hence the 0.2 nozzle; the first pick doubles as the PETG ironing coupon. The pick prints flat, so any underside taper must stay about 45 degrees or steeper (each 0.06 layer's wall can hang about half a 0.22 line past the one below); a shallow bevel is top-face only.

**How to apply:** next steps are Brian's edge pick on the page (https://claude.ai/artifact/Xdy17d32z8uCNaQAHhxuis), the GUI open with the 0.2 machine selected, the print, then a thickness and feel check against the Tortex; an ironed second pick only if the top lines show. Retrospective in `knowledge/learnings/guitar-pick.md` (includes the G2/G3 arc lesson for G-code checks). Related: [[feedback-model-dispatch]], [[feedback-keep-skirt]], [[user-printer-hardware]].
