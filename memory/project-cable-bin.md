---
name: project-cable-bin
description: "Stackable 16.75 x 4 x 4 in cable bin split into two dovetailed halves for the X2D; CAD, renders, two-plate PETG 3MF built 2026-10-25; awaiting Brian's sign-off and the joint coupon print"
metadata:
  node_type: memory
  type: project
  originSessionId: 57f36788-c5ae-4c4a-b01f-4b0e50546282
  modified: 2026-10-25T18:32:44.197Z
---

Cable bin (projects/Cable-bin/): Brian asked 2026-10-25 for four stackable
cable bins, 16.75 x 4 x 4 in, split to fit the X2D. Built the same day:
half A (dovetail tails) and half B (sockets) on one plate, four runs for four
bins; crush-rib friction hold on the top 12 mm of each tail (PLA numbers,
PETG unvalidated, so plate 2 is a ten-minute joint coupon to print first);
stacking by a 45 degree foot flare on a lip chamfer, drop 5 mm, pitch 3.80 in.
Sign-off page options.html asks: friction vs CA drop, plain ends vs finger
scallop, 3.80 vs 4.00 in pitch, 3-line vs 2-line walls, colour. Not printed.

**Why:** the joint and stack are the two decisions that cost a reprint if
wrong; both are proven in geometry but the rib fit in PETG is not.

**How to apply:** before any change read projects/Cable-bin/brief.md and
knowledge/learnings/cable-bin.md; the model is `cable_bin.py` (self-checking,
run it after every edit), renders via `pipeline/renders.py`, 3MF via
`pipeline/make_print_3mf.py`. Record the coupon fit in the learnings note.
See [[feedback-friction-fit-recipe]], [[feedback-one-multiplate-3mf]],
[[feedback-html-visual-companion]].
