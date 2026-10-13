# Handoff: P-Bass pickup height gauge (2026-10-13)

## State

- CAD source `projects/Pickup-height-gauge/pickup_height_gauge.py` (build123d), STL and
  Bambu 3MF built and slice-verified by `pipeline/make_print_3mf.py`:
  0.2 nozzle, PETG Basic, 0.10mm Standard, 50 layers, 1 h 14 min, 7.2 g.
- Renders in `images/`; `brief.md` has Fender's spec table with sources,
  the pickup geometry behind the arm size, print settings and usage.
- Viewer had the model pushed on 2026-10-13 (window "OCP CAD Viewer").
- Not printed. Brian has not looked yet.

## Decisions already locked

- Four arms, one per Fender starting point: 2.0, 2.4, 2.8, 3.2 mm
  (5/64, 6/64, 7/64, 8/64 in), opposite arms paired (2.0 + 2.8 standard
  P, 2.4 + 3.2 vintage and noiseless).
- Arm goes in ACROSS the string from the outer edge of the pickup half so
  it rests on the two poles that flank the string (P-Bass poles flank
  each string, 9.5 mm apart).
- Printed flat on 0.1 mm layers so every thickness is a whole number of
  layers; the pipeline asserts each arm's top layer in the G-code.
- Labels debossed on the hub, numbers only (the 2.4 value is a treble
  value on one Fender page and a bass value on the other).
- Brian's bass is getting Fender '62 reissue pickups (Brian 2026-10-13):
  Fender's "Vintage style" row, so his pair is 3.2 (E) and 2.4 (G). The
  other two arms stay as the next step closer.

## Open

- Caliper check of the arms after the first print.
