---
name: project-guitar-pick
description: "Dunlop Tortex Standard 1.0 pick copy; outline traced from caliper photos, PETG 0.2-nozzle 3MF slice-verified 2026-10-11, not printed"
metadata:
  node_type: memory
  type: project
  originSessionId: 436656c6-ca45-4497-873c-df44f48e28f5
  modified: 2026-10-12T06:07:08.238Z
---

Plain PETG copy of the Dunlop Tortex Standard 1.0 mm pick (351 shape), `projects/Guitar-pick/`. On 2026-10-11 Brian measured it at 26.19 x 30.38 x 1.0 mm; the outline was traced from his two caliper photos (`pipeline/trace_photo.py`) and he approved it on the sign-off page. The measured tip radius is 4.5 mm; the generic 351 SVG outline is 3.4 mm, so the generic shape is NOT a stand-in for the Dunlop.

Print file `guitar-pick.3mf` (`pipeline/make_print_3mf.py`, copied from the Skateboard pipeline): 0.2 mm nozzle, 0.06 mm layers so 16 layers sum to exactly 1.0 mm, solid zig-zag (gyroid is refused at 100%), seam at the top centre, no ironing, skirt. Slice: 13 min 27 s, 0.7 g. Not printed as of 2026-10-11.

**Why:** Brian wants it as smooth as possible, hence the 0.2 nozzle; the first pick doubles as the PETG ironing coupon.

**How to apply:** next steps are the GUI open with the 0.2 machine selected, the print, then a thickness and feel check against the Tortex; an ironed second pick only if the top lines show. Retrospective in `knowledge/learnings/guitar-pick.md`. Related: [[feedback-model-dispatch]], [[feedback-keep-skirt]], [[user-printer-hardware]].
