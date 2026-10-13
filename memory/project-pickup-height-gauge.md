---
name: project-pickup-height-gauge
description: "Fender P-Bass pickup height gauge, four-arm feeler cross with Fender's 2.0/2.4/2.8/3.2 mm values; CAD and slice-verified 3MF built 2026-10-13, not printed"
metadata:
  node_type: memory
  type: project
  originSessionId: f9d9239e-61d5-4ad8-8b6e-eb35a206f5da
  modified: 2026-10-13T22:07:45.187Z
---

Four-arm feeler gauge for setting P-Bass pickup height, built 2026-10-13 in
`projects/Pickup-height-gauge/`. Arms 2.0 / 2.4 / 2.8 / 3.2 mm (Fender's
5/64 to 8/64 in starting points, bottom of string to pole top, strings
fretted at the last fret), opposite arms paired (2.0 + 2.8 standard P,
2.4 + 3.2 vintage and noiseless). Arm goes in across the string so it rests
on the two poles that flank it. 3MF for the 0.2 nozzle, PETG, 0.1 mm layers
(every thickness a whole number of layers, asserted in the sliced G-code),
1 h 14 min, 7.2 g. Not printed; Brian has not looked yet. Brian's bass is
getting Fender '62 reissue pickups (said 2026-10-13): Fender's "Vintage
style" row, so his pair is 3.2 mm under the E and 2.4 mm under the G. The
bass itself is a 2002 Mexican-made Standard Precision.

**Why:** Fender's two support pages disagree by one 64th on a standard P's
bass side (7/64 vs 6/64), so the gauge carries all four values instead of
committing to one pair.

**How to apply:** when Brian reports the print, caliper the arms and write
the retrospective in `knowledge/learnings/pickup-height-gauge.md`. Layer
heights of 0.1 or 0.2 mm keep the arms exact; the 0.18 mm balanced profile
does not. See [[feedback-keep-skirt]] and [[feedback-check-environment-first]].
