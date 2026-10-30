---
title: Logodude handoff
date: 2026-10-30
---

# Logodude handoff (2026-10-30, speaker cab logo size samples)

State: three size samples (2.5, 3, 3.5 in wide) built in `logodude_cab.py`,
pushed to the viewer, exported, and shipped in ONE one-plate `logodude-cab.3mf`
(1 h 42 min, 51.5 g, one filament change, every G-code proof passing). NOT
printed. Brian picks the size from the prints; the mount comes after.

## Decisions already locked
- The cab: the walnut 1x12 of projects/Cab-Blietz-1x12-hardwood (20 x 18 in,
  Salt and Pepper cloth on a 12 x 40 mm frame, 5 mm cloth-to-baffle gap).
  Front is grille cloth; "logo should screw on" (Brian 2026-10-28).
- Sizes 2.5, 3 and 3.5 in WIDE (Brian 2026-10-30), after 5 to 7 in was "WAY
  too big" and 3 to 4 in was drawn. Backer width is the size; margin scales
  with the art (2.13 / 2.55 / 2.98 mm).
- 0.4 nozzle, 0.16mm Standard, 3.08 backer + 0.96 ink, PETG Basic white +
  black, the tag's locked keys; one plate, three objects, plain backs.
- Mount not chosen. Options page (https://claude.ai/artifact/HSRyEMiocqN1SwRhsBAMQ8,
  `pipeline/cab_logo_options.py`): A hidden M3 inserts screwed from behind
  the frame strip (my pick), B #4 black heads in the hair into the strip,
  C through the cloth to the baffle with 5 mm standoffs. A and B need the
  logo to overlap the 40 mm strip band: the top-left corner, 10 mm in.
- Badge, stand and tag files untouched.

## Next
- Brian prints logodude-cab.3mf (0.4 nozzle preset selected first, AMS
  white / black, Flushing Volumes: Re-calculate) and picks a size.
- Then: add the mount to `logodude_cab.py` for that size (A: two 10 mm bosses
  with M3 heat-set insert holes on the back, spots from cab_logo_options.py's
  band logic; ask whether Brian has inserts), confirm the grille position,
  a mounted close-up render, one 3MF for the final logo, retrospective
  knowledge/learnings/logodude.md after the print.
