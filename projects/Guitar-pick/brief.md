---
title: Guitar pick, Dunlop Tortex Standard 1.0 mm
status: outline measured, waiting on thickness and sign-off
created: 2026-10-11
tags: [project, 3d-print, petg]
---

# Guitar pick (Dunlop Tortex Standard 1.0 mm)

A plain copy of the Jim Dunlop Tortex Standard 1.0 mm pick (351 shape): no
logo, no grip texture. PETG, 0.4 mm nozzle, printed flat. One pick first,
more once the shape is right.

## Measured (Brian's calipers, 2026-10-11)

- Width 26.19 mm (`images/IMG_1656.jpg`), length 30.38 mm (`images/IMG_1657.jpg`).
- Thickness: not measured yet; model assumes 1.0 mm.
- Tip radius 4.5 mm (circle fit on the traced edge; 4.60 from IMG_1657, 4.47 from IMG_1656).
- Widest point 7.9 mm below the top edge.

## Outline source

`outline-dunlop.csv` is traced from IMG_1657 (whole pick visible between the
jaws) by `pipeline/trace_photo.py`: blue pick segmented from the wood and
steel on saturation, subpixel contour, scaled so the extent across the jaws
equals the caliper reading, symmetrized about the pick's axis, smoothed,
convex hull, then stretched to the two readings exactly. IMG_1656 has the
top of the pick hidden under the caliper beam, so it only cross-checks the
tip.

`outline-351.csv` is the generic 351 from the Iron Age Accessories free SVG
pack, kept as the cross-check: at the same width and length it has a 3.4 mm
tip and sits about 0.9 mm inside the Dunlop per side in the lower third.
The Dunlop is blunter and fuller, so the measured outline is the one used.

## Files

- `guitar_pick.py`: build123d source; asserts one solid, 26.19 x 30.38 x 1.0 mm on Z=0, watertight STL.
- `guitar-pick.stl`: current export (about 0.74 g PETG).
- `pipeline/trace_photo.py`: photo trace; writes `outline-dunlop.csv` and `images/trace-overlay.png`.
- `pipeline/make_compare_page.py`: the sign-off page (published 2026-10-11: https://claude.ai/artifact/Xdy17d32z8uCNaQAHhxuis).
- `images/pick-v3.png`: 4-view render of the current model (v1 teardrop and v2 generic 351 kept for the record).

## Open

- Thickness reading from Brian.
- Brian's look at the outline against the pick.
- Bambu 3MF: one pick, PETG, 0.4 mm nozzle, skirt on (not built yet).

## Decisions already locked

- PETG, plain face, one pick for the first print (Brian 2026-10-11).
- Measured outline over the generic 351 (tip radius differs by 1.1 mm).
- 0.4 mm nozzle: a 1.0 mm pick is below the 0.6 nozzle's 1.24 mm two-wall minimum.
