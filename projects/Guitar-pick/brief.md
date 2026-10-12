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
- Thickness 1.0 mm (Brian's calipers, confirmed in chat 2026-10-11).
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

## Print file (built 2026-10-11)

`guitar-pick.3mf` from `pipeline/make_print_3mf.py`: machine `Bambu Lab X2D
0.2 nozzle`, process `0.08mm High Quality @BBL X2D 0.2 nozzle` with
layer_height 0.06 (0.1 first layer + 15 x 0.06 = 1.0 mm exactly; the stock
0.08 would print 0.98), filament `Bambu PETG Basic @BBL X2D 0.2 nozzle`,
Textured PEI 70 C, 250 C nozzle. Solid (100% zig-zag; the preset's gyroid is
refused at 100% by the CLI), arachne walls, seam at the top centre
(`seam_position` back, proven in the G-code: every outer wall loop starts
at x 129.1, y 142.9 on a top edge at y 143.2), no ironing, skirt 2 loops /
3 mm / 1 layer, no brim. Centred on the bed, tip toward the front.

Slice (`guitar-pick-slice.json`): 16 layers to z 1.0, 13 min 27 s estimated
(0.2 nozzle estimates ran 1.4x under on the Sharks tags, so expect about 20
min), 0.7 g, 0.23 m. Round trip through the CLI and a real slice both pass.

## Open

- Open `guitar-pick.3mf` in Bambu Studio once (GUI ground truth), with the
  0.2 nozzle installed and the 0.2 machine selected in Studio.
- Print, then measure thickness and compare the feel against the Tortex.
- If the top texture (0.22 mm lines) is not smooth enough: a second pick
  with ironing is the next coupon. A Smooth PEI plate would give a smooth
  bottom; the textured plate molds its texture in.

## Decisions already locked

- PETG, plain face, one pick for the first print (Brian 2026-10-11).
- Measured outline over the generic 351 (tip radius differs by 1.1 mm); Brian approved the outline on the sign-off page 2026-10-11.
- Thickness 1.0 mm (measured).
- 0.2 mm nozzle, Brian's call 2026-10-11, for the smoothest edge and faces. (The 0.6 nozzle was never an option: a 1.0 mm pick is below its 1.24 mm two-wall minimum.)
