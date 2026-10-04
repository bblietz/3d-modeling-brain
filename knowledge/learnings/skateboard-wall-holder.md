---
title: Skateboard wall holder
type: learning
project: Skateboard-wall-holder
created: 2026-10-04
tags: [x2d, petg, wall-mount, skateboard, hook, build123d]
---
# Skateboard wall holder

Narrow wall hook that hangs a street skateboard by its top truck, trucks toward the wall. Brian's words: "narrow", "rest on the center circular part of the truck", then in the viewer "the tongue should have a curved shape, so the board doesnt slide off if it is bumped" and "make the tongue wider and teh curve deeper". CAD complete 2026-10-04; not printed.

## What worked
- The HTML design tool first (Skate Hook Studio): Brian answered the concept question by pasting its prompt back. Two text questions were never needed. [[feedback-html-visual-companion]]
- Research before geometry: the kingpin is nearly perpendicular to the deck and the nut stands only about 9 mm proud of the hanger's inboard rim, so the hold went on the hanger body, not the nut. That single fact decided the concept.
- Dish as floor = max(cradle arc, saddle arc): the side-view cradle extruded across the width, intersected with the width-wise cylinder. Two booleans, accepts a dome or a rounded block.
- Hold check on 0.5 mm trimesh slices with shapely (3 s): rest, way in with the part grown 0.2, bump slack, lift to escape each way. [[feedback-check-docking-and-hold-kinematics]]
- True section figures from mesh slices in matplotlib; OpenSCAD preview sections (intersection or difference clip) collapse every part to one color.

## What failed
- A loft of saddle arcs along the cradle curve carved the side walls higher than the hanger proxy and collided by 0.6 cm3; a translational surface is not what a loft makes.
- The tool's tangent point had a sign error (room side of the lowest point, not wall side); the CAD derivation caught it.
- 2D fillet on a 2.6 mm flat with a 3 mm radius fails with a misleading vertex in the error; size end fillets to the flat.
- Hold-check slice lattices must coincide: quarter-mm holder slices against half-mm truck slices found no collisions at all.
- 0.6 mm side chamfer failed at 30 mm width and succeeded at 40; probes near an edge must sit inside the chamfer.

## Measured fits
| Feature | Modelled | Result |
|---|---|---|
| Cradle radial clearance | 2.0 mm | not printed |
| Washer over the wall-side shelf | 2.8 mm | not printed |
| Tongue end to baseplate | 2 mm | not printed |

## Settings used
- Planned: PETG Basic, 0.6 high-flow nozzle, 0.30 mm Standard, 3 walls, 20% gyroid, on its side, no supports.

## Open
- Brian's go-ahead, 3MF, print, then measure the truck numbers listed in the brief.
