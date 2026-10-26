---
name: project-cable-bin
description: "Stackable 16.75 x 4 x 4 in cable bin split into two dovetailed halves for the X2D; decisions taken 2026-10-25 (friction hold, scallop ends, 3.80 in pitch, slotted walls, 8 mm posts, PLA, 2-line walls); joint fit set from the printed ladder (pair 4: body 0.25, crush 0.10, ribs 6 mm); two-plate 3MF 4 h 50 min / 240 g per bin; design closed, colour picked in Studio; no bin printed yet"
metadata:
  node_type: memory
  type: project
  originSessionId: 57f36788-c5ae-4c4a-b01f-4b0e50546282
  modified: 2026-10-26T01:10:00.000Z
---

Cable bin (projects/Cable-bin/): Brian asked 2026-10-25 for four stackable
cable bins, 16.75 x 4 x 4 in, split to fit the X2D. Built the same day:
half A (dovetail tails) and half B (sockets) on one plate, four runs for four
bins; crush-rib friction hold on the top 6 mm of each tail; stacking by a
45 degree foot flare on a lip chamfer, drop 5 mm, pitch 3.80 in. Weight
history: 3-line PETG 368 g / 7 h 02; Brian said that was a lot (drawer bin,
three sides against its walls, no load) and asked for PLA: 2-line walls
285 g / 4 h 58; then he took both cuts: 13 vertical 6 x 64 mm slots per long
wall per half, 8 mm joint posts, plus the finger scallop ends he picked:
240 g / 4 h 54 min per bin, 965 g and 19 h 48 min for four. Friction hold
and 3.80 in pitch confirmed. Brian printed the first joint coupon: TOO
TIGHT at body 0.15 / crush 0.20 (Arachne 0.30 mm is a new calibration, and
four ribs over 11.5 mm is five times the recipe's contact). Bin now body
0.25 / crush 0.10; plate 2 is a four-pair fit ladder (1 to 4 notches:
crush 0.15 / 0.10 / 0.05 at 12 mm ribs, 0.10 at 6 mm) with bed chamfers.
Brian printed the ladder and picked pair 4 ("4 works the best"): RIB_LEN 12
to 6, bin 4 h 50 min / 240 g, four bins 19 h 18 min / 960 g. Brian picks
the colour in Bambu Studio, so the design is closed; no bin printed yet.

**Why:** the joint and stack are the two decisions that cost a reprint if
wrong; both are proven in geometry. Every design decision is now Brian's.

**How to apply:** before any change read projects/Cable-bin/brief.md and
knowledge/learnings/cable-bin.md; the model is `cable_bin.py` (self-checking,
run it after every edit), renders via `pipeline/renders.py`, 3MF via
`pipeline/make_print_3mf.py`, figures via `pipeline/fill_numbers.py`,
per-layer-band times via `pipeline/layer_times.py`. Record the coupon fit in
the learnings note. See [[feedback-friction-fit-recipe]],
[[feedback-one-multiplate-3mf]], [[feedback-html-visual-companion]],
[[feedback-ask-load-case-before-walls]],
[[feedback-small-perimeter-threshold-radius]].
