---
title: Logodude handoff
date: 2026-09-29
---

# Logodude handoff (2026-09-29)

State: CAD signed off ("go"); print file built and slice-verified; NOT printed.

## Decisions already locked
- Source: Drive logo-dude.png, traced 1:1 (pipeline/trace.py -> traced.json).
- Style B die-cut badge, 4.00 in tall (101.60 mm) x 4.11 in; 3 mm white backer, black ink raised 1 mm, 3.5 mm outline margin (min 2.5 asserted).
- Solid lines: per-shape close/open (hair 14/10 px, face 3/3), right-stroke outer-edge fill (60 px close in a region), edge smoothing (hair sigma 14 px, face 5, jaw 40 below row 1060, outline 2.5 mm), periodic-spline faces.
- Print: 0.4 nozzle, PETG Basic white + black (switched from PLA 2026-09-29), 0.12 mm layers, Sharks fill-core recipe modifier over the 5 face shapes (infill_direction 0), textured PEI 70 C, 250 C, tower at (40, 87.5).
- Slice: 1h 25m, 22.51 g white + 3.06 g black; one color change at z 3.08.
- Printer at 192.168.1.50; had the 0.6 HF nozzle mounted (swap to 0.4); AMS slots 2-3 hold the PETG but tags read empty.

## Next
- Brian opens logodude.3mf in Bambu Studio (0.4 nozzle preset selected first), Flushing Volumes: Re-calculate, check AMS mapping, prints.
- Brian declined the thin-stroke coupon: print the whole badge.
- After the print: retrospective in knowledge/learnings/logodude.md.
