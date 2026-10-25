---
name: project-cable-bin
description: "Stackable 16.75 x 4 x 4 in cable bin split into two dovetailed halves for the X2D; CAD, renders, two-plate PLA 3MF (2-line walls, 285 g / 4 h 58 min per bin) built 2026-10-25; awaiting Brian's sign-off and the joint coupon print"
metadata:
  node_type: memory
  type: project
  originSessionId: 57f36788-c5ae-4c4a-b01f-4b0e50546282
  modified: 2026-10-25T21:00:00.000Z
---

Cable bin (projects/Cable-bin/): Brian asked 2026-10-25 for four stackable
cable bins, 16.75 x 4 x 4 in, split to fit the X2D. Built the same day:
half A (dovetail tails) and half B (sockets) on one plate, four runs for four
bins; crush-rib friction hold on the top 12 mm of each tail; stacking by a
45 degree foot flare on a lip chamfer, drop 5 mm, pitch 3.80 in. First
version was 3-line walls in PETG, 368 g / 7 h 02 min; Brian said that was a
lot, the bins sit in a drawer with three sides against its walls and no real
load, and asked for PLA: now 2-line walls (1.24 mm) in PLA Basic, 285 g /
4 h 58 min per bin, 1144 g for four. Plate 2 is a 14-minute joint coupon to
print first (the rib numbers are PLA-calibrated, so it is confirmation).
Sign-off page options.html asks: friction vs CA drop, plain ends vs finger
scallop, 3.80 vs 4.00 in pitch, weight (285 g, or slots about 30 g less,
shorter posts about 15 g less), PLA colour. Not printed.

**Why:** the joint and stack are the two decisions that cost a reprint if
wrong; both are proven in geometry. The weight was Brian's first objection.

**How to apply:** before any change read projects/Cable-bin/brief.md and
knowledge/learnings/cable-bin.md; the model is `cable_bin.py` (self-checking,
run it after every edit), renders via `pipeline/renders.py`, 3MF via
`pipeline/make_print_3mf.py`, figures via `pipeline/fill_numbers.py`. Record
the coupon fit in the learnings note. See [[feedback-friction-fit-recipe]],
[[feedback-one-multiplate-3mf]], [[feedback-html-visual-companion]],
[[feedback-ask-load-case-before-walls]].
