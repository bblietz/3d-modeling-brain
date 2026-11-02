---
title: Logodude handoff
date: 2026-11-01
---

# Logodude handoff (2026-11-01, speaker cab logo size samples, resized)

State: three size samples, now 1.5, 1.75 and 2 in wide (Brian 2026-11-01:
"those seem too big" about 2.5 to 3.5), built in `logodude_cab.py`, exported,
and shipped in ONE one-plate `logodude-cab.3mf` (47 min, 18.4 g, one filament
change, every G-code proof passing, per stroke included). NOT printed. Brian
picks the size from the prints; the mount comes after.

## Decisions already locked
- The cab: the walnut 1x12 of projects/Cab-Blietz-1x12-hardwood (20 x 18 in,
  Salt and Pepper cloth on a 12 x 40 mm frame, 5 mm cloth-to-baffle gap).
  Front is grille cloth; "logo should screw on" (Brian 2026-10-28).
- Sizes 1.5, 1.75 and 2 in WIDE (Brian 2026-11-01), after 5 to 7 in was "WAY
  too big", 3 to 4 in was drawn, and 2.5 to 3.5 in "seem too big". Backer
  width is the size; margin scales with the art (1.28 / 1.49 / 1.70 mm).
- 0.4 nozzle, 0.16mm Standard, 3.08 backer + 0.96 ink, PETG Basic white +
  black, the tag's locked keys; one plate, three objects, plain backs. Face
  strokes print as two thin arachne beads (0.27 mm at 1.5 in, 0.34 at 2 in,
  measured in the slice); the 0.2 nozzle is the fallback if they look rough.
- Mount not chosen. Options page (https://claude.ai/artifact/HSRyEMiocqN1SwRhsBAMQ8,
  `pipeline/cab_logo_options.py`, still drawn at 3 to 4 in): A hidden M3
  inserts screwed from behind the frame strip (my pick), B #4 black heads in
  the hair into the strip, C through the cloth to the baffle with 5 mm
  standoffs. A and B need the logo to overlap the 40 mm strip band: the
  top-left corner, 10 mm in. At 1.5 to 2 in a 5.5 mm #4 head no longer fits
  in the hair strokes, so B likely drops out; check when the size is picked.
- Badge, stand and tag files untouched.

## Next
- Brian prints logodude-cab.3mf (0.4 nozzle preset selected first, AMS
  white / black, Flushing Volumes: Re-calculate) and picks a size.
- Then: add the mount to `logodude_cab.py` for that size (A: two bosses with
  M3 heat-set insert holes on the back, spots from cab_logo_options.py's band
  logic, redrawn at the picked size; ask whether Brian has inserts), confirm
  the grille position, a mounted close-up render, one 3MF for the final logo,
  retrospective knowledge/learnings/logodude.md after the print.
