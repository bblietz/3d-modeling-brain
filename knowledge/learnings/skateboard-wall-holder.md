---
title: Skateboard wall holder
type: learning
project: Skateboard-wall-holder
created: 2026-10-04
tags: [x2d, petg, wall-mount, skateboard, hook, build123d]
---
# Skateboard wall holder

Narrow wall hook that hangs a street skateboard by its top truck, trucks toward the wall. Brian's words: "narrow", "rest on the center circular part of the truck", then in the viewer "the tongue should have a curved shape, so the board doesnt slide off if it is bumped" and "make the tongue wider and teh curve deeper". Then "the front lip of the holder should also have a rounded dip, to cradle the truck". CAD and 3MF complete 2026-10-04 (1 h 4 min, 50.1 g PETG, solid screw pads); not printed.

## What worked
- The HTML design tool first (Skate Hook Studio): Brian answered the concept question by pasting its prompt back. Two text questions were never needed. [[feedback-html-visual-companion]]
- Research before geometry: the kingpin is nearly perpendicular to the deck and the nut stands only about 9 mm proud of the hanger's inboard rim, so the hold went on the hanger body, not the nut. That single fact decided the concept.
- Dish as a RULED loft of the saddle arc through stations along the cradle (the saddle carried along the curve, so the lip dips too). A smooth loft overshoots 1.1 mm where the arc meets the flat; ruled with 5 deg stations is exact to 0.02 mm. The earlier intersection bowl (floor = max of the two arcs) accepts a blockier hanger but leaves the lip flat.
- Hold check on 0.5 mm trimesh slices with shapely (3 s): rest, way in with the part grown 0.2, bump slack, lift to escape each way. [[feedback-check-docking-and-hold-kinematics]]
- True section figures from mesh slices in matplotlib; OpenSCAD preview sections (intersection or difference clip) collapse every part to one color.

## What failed
- The 3MF went out once without 100% pads at the screw holes; Brian's standing rule now: [[feedback-solid-infill-at-screw-holes]]. Adding the pad check then exposed a shaved plate face (the dish cutter started 1 mm inside the plate): a check for one thing catches another, so keep the mechanical checks even on simple parts.
- With a rounded-block hanger proxy, the carried-along dish collides (0.6 cm3) because the block's underside is flat across the width away from the bottom; with a dome proxy it nests. Keep both proxies and report both holds; the real hanger is between them.
- The tool's tangent point had a sign error (room side of the lowest point, not wall side); the CAD derivation caught it.
- 2D fillet on a 2.6 mm flat with a 3 mm radius fails with a misleading vertex in the error; size end fillets to the flat.
- Hold-check slice lattices must coincide: quarter-mm holder slices against half-mm truck slices found no collisions at all.
- 0.6 mm side chamfer failed at 30 mm width, succeeded at 40 with the intersection bowl, failed again with the loft rims; probes near an edge must sit inside a chamfer that may or may not exist.
- The Bambu CLI stored this mesh uncentred (the desk-trough recipe assumed centred); `recenter()` in the 3MF builder reads the file's own world bounds and moves the build item.

## Measured fits
| Feature | Modelled | Result |
|---|---|---|
| Cradle radial clearance | 2.0 mm | not printed |
| Washer over the wall-side shelf | 2.8 mm | not printed |
| Tongue end to baseplate | 2 mm | not printed |

## Settings used
- PETG Basic, 0.6 high-flow nozzle, 0.30 mm Standard, 3 walls, 20% gyroid, 100% modifier pads 25 mm around the screw holes, 2-loop skirt, no brim, on its side, no supports: 1 h 4 min, 50.1 g, 133 layers, 250/70 C.

## Open
- Print, fit, then measure the truck numbers listed in the brief and fill the fit table.
