---
type: retrospective
project: Guitar-neck-rest
created: 2026-11-23
status: modelled and sliced, not printed
tags: [learnings, 3d-print, guitar, openscad, roundover, bambu-3mf]
---

# Guitar neck rest: retrospective (model, 2026-11-23)

Open-frame rocker that holds a guitar or bass neck on the bench. Project: [[projects/Guitar-neck-rest/brief|brief]], spec [[2026-11-23-guitar-neck-rest-design]], plan [[2026-11-23-guitar-neck-rest-plan]]. Printer: [[printer-x2d]]. To be extended after the first print.

## Decisions locked

- Brian 2026-11-22: rocker shape; open-frame body (round 2's C1); cradle 4-3/8 in long, unchanged after he looked at 6 in and 8 in.
- Brian 2026-11-23: go on the design; the two cradle ends rounded over; a slight roundover on every other edge; spec approved; one recessed channel in the bottom for his 2 in wide rubber grip tape.
- My calls, open to change: 1/4 in and 1/16 in roundovers; 1/16 in cork pad; channel 0.5 mm deep; PLA, 2 walls, 15% infill; neck at 3-3/4 in.

## What worked

- **Roundovers as slices, not fillets.** The body prints on its side, so it is modelled as slices across the neck: each slice is the side outline with its top at the cradle's height there and its two top corners rounded 1/4 in; the 1/16 in rim round is part of that height curve; at the faces the outline shrinks through a quarter circle; chained `hull()` joins the slices. Smooth everywhere, 4 s to render, and exactly what the nozzle draws. A rolling-ball fillet cannot do this: a 1/4 in ball cannot follow a 1/16 in rim round the cradle end, so the kernel either fails or leaves a crease.
- **Checks on the mesh.** `build.py` drops rays on the STL for the cradle floor, the arc, the channel and the gap under two stand-in necks, and sorts down-facing facets by where they are. It caught nothing wrong in the geometry, and it caught my own bad first check (sampling section vertices instead of casting a ray).
- **Seam by orientation.** With the part lying cradle-to-the-back and `seam_position = back`, all 533 outer loops start on the cradle side or inside the top of the opening, none on the rocking curve. Proven from the G-code by where each "Outer wall" feature starts.
- **One plain-words question for an ambiguous note.** "The front and back edges closest to the neck" had two readings; one question settled it before anything was drawn.

## What failed or cost time

- **Mirroring a half onto itself.** Two centre slices 0.02 mm apart left slivers that the STL's 32 bit vertices could not keep closed (trimesh: not watertight, 5 bodies). Fix: one chain of slices from face to face, the centre slice once.
- **ASCII STLs.** OpenSCAD's default STL was 53 MB for 172k facets. `--export-format binstl` gives 8 MB.
- **The 45 degree rim claim.** The cradle radius was chosen so the rim is 45 degrees at the pad surface; the cut for the pad seat is deeper, so the printed rim is 45.6 degrees. Harmless, but the page said 45 for three versions.
- **A roundover on the plate-side face.** "All edges" includes the face on the plate, where a roundover starts as an overhang on the first layers. Not solved, only flagged: Brian looks at the preview, and the fallback is a small bevel on that side.

## Settings used

X2D, 0.6 mm nozzle, `0.30mm Standard @BBL X2D 0.6 nozzle`, `Bambu PLA Basic @BBL X2D 0.6 nozzle`, 2 walls, 15% grid infill, no supports, 2-loop skirt, no brim, Textured PEI at 65 C, seam back. Slice: 167.5 g, 2 h 21 min, 267 layers.

## Measured fits

None yet: nothing is printed. To measure on the first print: the cork pad in its 1.6 mm seat, the 2 in tape in the 51.6 mm channel and how far it stands proud of the 0.5 mm depth, and whether the rest slides on the bench.
