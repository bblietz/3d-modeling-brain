---
title: Guitar pick, Dunlop Tortex Standard 1.0 mm
status: blended bevel edge built and sliced 2026-10-12, waiting on Brian's look, then the print
created: 2026-10-11
tags: [project, 3d-print, petg]
---

# Guitar pick (Dunlop Tortex Standard 1.0 mm)

A plain copy of the Jim Dunlop Tortex Standard 1.0 mm pick (351 shape): no
logo, no grip texture. PETG, 0.2 mm nozzle, printed flat. One pick first,
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

Since 2026-10-12 the side of the model is a smooth closed spline, not the
52-vertex polygon: the trace is resampled every 0.25 mm, Gaussian-smoothed
along the outline (sigma 0.6 mm), stretched back to the two readings and
splined. It stays within 0.06 mm of the trace and is convex (asserted). The
polygon had 1.7 mm facets, 0.08 mm deep at the tip, which the slicer would
have printed; and a spline straight through the hull vertices overshot the
trace by 0.21 mm at the shoulders, where the hull leaves 4.7 mm gaps.

## Edge profile (Brian 2026-10-12: "the pick edges should be tapered")

The first model extruded the outline with square edges. Brian wants the
edge tapered like the real pick's. Web research (Dunlop's copy, player
forums) says a new Tortex Standard is die-stamped Delrin with a square,
unbeveled edge and that the taper players feel is wear; only the Ultex
Flow has a moulded bevel. Nobody has published an edge measurement. So the
profile is Brian's call, and the pick prints flat, which limits the
underside: with 0.06 mm layers and a 0.22 mm outer wall, each layer's wall
can hang at most about half a line past the one below, so the underside
slope has to stay around 45 degrees or steeper. A shallow underside taper
is unprintable flat.

Options built by `pipeline/edge_options.py` (cross-sections and overhang
numbers in `edge-options.json`, close-ups in `images/edge-*.png`):

| profile | top face | underside | rim left | worst underside step |
|---|---|---|---|---|
| soft (built into the 3MF) | 1.5 mm wide, drops 0.35, crease blended R 5 | 45 degree flat, 0.35, crease blended R 0.35 | 0.30 mm | layer 2: 0.097 mm geometry, 0.112 in the G-code, 58 degrees |
| bevel (Flow style) | 1.5 mm wide, drops 0.35 | 45 degree flat, 0.35 | 0.30 mm | layer 2: 0.080 mm, 53 degrees |
| round | fillet R 0.45 | fillet R 0.45 | 0.10 mm | layer 2: 0.112 mm, 62 degrees off vertical, half a line |
| chamfer | 45 degree flat, 0.45 | 45 degree flat, 0.45 | 0.10 mm | layer 2: 0.080 mm, 53 degrees |

Brian's pick, 2026-10-12, after seeing the first three: "like the bevel,
but have no noticeable line, so the bevel should have a curved lead in".
That is `soft`: the bevel's crease with the flat face is filleted R 5 (a
blend about 1.1 mm wide, 0.57 mm each side of where the crease was, so the
slope now starts 2.07 mm from the rim), and the underside crease R 0.35.
Underneath the radius is capped by the print: R 0.5 hangs layer 2 by 0.12
mm, R 0.35 by 0.10, and R 0.25 fails in the kernel. The bevel is a taper on
the top face only; the underside keeps the 45 degree flat because the pick
prints flat. On the top slope the printer makes six 0.06 mm terraces about
0.26 mm wide, widening into the blend; that is inherent to a 13 degree
slope printed flat and the 0.2 nozzle is what keeps them this fine.

`elefant_foot_compensation` is 0 in the 3MF (the preset has 0.15): the
rounded underside already takes the foot, and shrinking layer 1 another
0.15 mm would leave layer 2's wall hanging 0.26 mm past it, more than a
line.

## Files

- `guitar_pick.py`: build123d source; `build(edge)` with `EDGES` = soft, bevel, round, chamfer, square (default soft, `EDGE=` env var picks another); asserts one solid, 26.19 x 30.38 x 1.0 mm on Z=0, spline within 0.1 mm of the trace and convex, watertight STL.
- `guitar-pick.stl`: current export, blended bevel (about 0.71 g PETG).
- `pipeline/edge_options.py`: builds the five edge variants, cuts the tip section, tabulates the per-layer underside overhang, renders `images/edge-*.png` with OpenSCAD (above and below); writes `edge-options.json` for the sign-off page.
- `images/pick-v5.png`: 4-view render of the current model (v4 round edge, v3 square, kept for the record).
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

Slice (`guitar-pick-slice.json`, blended bevel, 2026-10-12): 16 layers to z
1.0, 12 min 57 s estimated (0.2 nozzle estimates ran 1.4x under on the
Sharks tags, so expect about 18 min), 0.67 g, 0.22 m. Round trip through the CLI
and a real slice both pass. The verify step now also reads the outer wall's
tip position per layer from the G-code (arc moves evaluated properly: the
preset has arc fitting on, and a G2's endpoints sit above its lowest point)
and asserts no underside layer hangs more than 0.13 mm past the one below;
measured 0.112, 0.060, 0.063, 0.054, 0.047 mm for layers 2 to 6 on the
blended bevel (the 45 degree flat steps one layer height).

## Open

- Brian confirms the blended bevel on the sign-off page (built into the
  3MF; the knobs are bevel width 1.5, rim 0.30, lead-in R 5 in `EDGES`,
  then rerun `guitar_pick.py`, `edge_options.py`, `make_print_3mf.py`).
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
- Edges tapered, not square (Brian 2026-10-12), and specifically the wide bevel with a curved lead-in and no noticeable line (Brian, same day, after seeing round, chamfer and bevel). Built as `soft`.
- Smooth spline side instead of the traced polygon (2026-10-12), so the fillet has one edge loop and the print has no facets.
