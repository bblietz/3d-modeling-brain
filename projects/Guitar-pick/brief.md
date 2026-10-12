---
title: Guitar pick, Dunlop Tortex Standard 1.0 mm
status: standing print built and sliced 2026-10-12 (mirrored 1.5 mm bevel, rounded rim, on a snap-off base), waiting on the print
created: 2026-10-11
tags: [project, 3d-print, petg]
---

# Guitar pick (Dunlop Tortex Standard 1.0 mm)

A plain copy of the Jim Dunlop Tortex Standard 1.0 mm pick (351 shape): no
logo, no grip texture. PETG, 0.2 mm nozzle, printed STANDING on its top
edge on a snap-off base (Brian 2026-10-12). One pick first, more once the
shape is right.

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
| mirror (SHIPPED, printed standing) | 1.5 mm wide, drops 0.35, crease blended R 5, rim creases R 0.15 | the same | 0.30 mm, rounded | flat it would be layer 2: 0.46 mm, band 0.26 mm per layer, in air |
| sym (flat alternative) | 0.45 mm wide, drops 0.35 (38 deg), crease blended R 0.35 | the same | 0.30 mm | layer 2: 0.109 mm geometry, 0.127 in the G-code, then 0.077 per layer |
| soft | 1.5 mm wide, drops 0.35, crease blended R 5 | 45 degree flat, 0.35, crease blended R 0.35 | 0.30 mm | layer 2: 0.097 mm geometry, 0.112 in the G-code, 58 degrees |
| bevel (Flow style) | 1.5 mm wide, drops 0.35 | 45 degree flat, 0.35 | 0.30 mm | layer 2: 0.080 mm, 53 degrees |
| round | fillet R 0.45 | fillet R 0.45 | 0.10 mm | layer 2: 0.112 mm, 62 degrees off vertical, half a line |
| chamfer | 45 degree flat, 0.45 | 45 degree flat, 0.45 | 0.10 mm | layer 2: 0.080 mm, 53 degrees |

Brian's pick, 2026-10-12, after seeing the first three: "like the bevel,
but have no noticeable line, so the bevel should have a curved lead in".
That is `soft`: the bevel's crease with the flat face is filleted R 5 (a
blend about 1.1 mm wide, 0.57 mm each side of where the crease was, so the
slope now starts 2.07 mm from the rim), and the underside crease R 0.35.
Underneath the radius is capped by the print: R 0.5 hangs layer 2 by 0.12
mm, R 0.35 by 0.10, and R 0.25 fails in the kernel. On the top slope the
printer makes six 0.06 mm terraces about 0.26 mm wide, widening into the
blend; that is inherent to a 13 degree slope printed flat and the 0.2
nozzle is what keeps them this fine.

Then (same day): "the top should be mirrored on the bottom as well" and
"the design must not require support material". `mirror` is that CAD
(`guitar-pick-mirror.stl`, kept as the true shape) and it cannot print
flat: the 13 degree underside asks each 0.06 mm layer to sit 0.26 mm past
the one below (118% of a 0.22 line, laid in air) and the lead-in puts
layer 2 at 0.46 mm. Thinner layers do not rescue it (0.04 mm layers still
step 0.17). The steepest slope the underside carries without support is
about 38 degrees, measured on symmetric candidates: 0.45 wide (38 deg)
layer 2 0.109 then 0.077 per layer; 0.52 wide (34 deg) 0.121 then 0.089;
0.60 wide (30 deg) 0.137 then 0.103. `sym` = 0.45 wide, 0.35 drop, R 0.35
blends, on both faces, 0.30 rim, was the flat print file for an hour. Brian
then chose the stand-up print ("this will give the smoothest surface for
PETG") and asked for the rim rounded too: `mirror` now has `rim_r` 0.15 on
the two rim creases (each fillet reaches 0.12 along the 0.30 rim, 0.06
flat left), and it is the shipped shape.

## Standing print (`standup.py`, `pipeline/make_standup_3mf.py`, 2026-10-12)

The pick stands tip-up on its top edge. Standing, the faces and bevels are
walls; only the top edge arc and the shoulder rounds up to the 45 degree
point (x -10.9 to 10.95, 3.55 mm above the apex) face down, and they sit on
a one-line neck (0.22 wide, 0.30 tall) on a saddle-topped block (26 mm
long, 7 wide, 3.975 at the centre, running 2 mm past the neck ends). A 4 mm
square column 24 mm off centre, tied in by a 1 mm plate, gives the nozzle
somewhere to go each layer so the tip's thin cross-sections cool. Height
34.66 mm = 0.1 + 576 x 0.06 exactly (the base height is derived from
that). One solid; the neck overlaps 0.1 into the pick and block for the
union; the pick's own volume is unchanged (asserted).

Seam: `seam_position back` alone put every loop's start at the end of the
face's flat run, 2 mm in from the edge, walking inward toward the tip as
the outline narrows. So the +y face carries a 1.5 mm wide, 2 micron deep
recess down its centre (far below the slicer's 0.012 mm resolution) whose
two floor triangles are painted `paint_seam="4"` (one unsplit triangle in
the enforcer state) in the 3MF's object mesh; the paint survives the CLI
round trip and the G-code shows all 402 pick loops starting on the rear
face within -0.8..+0.64 mm of the centre line. Scarf seams
(`seam_slope_type external`) produced zero ramp moves in the CLI slice,
on this file and on the flat pick, so they are not shipped.

Slice (`guitar-pick-slice.json`): 577 layers, top at 34.66, 2.51 g (0.68 g
of pick), 2 h 11 min estimated (the PETG preset's 12 s minimum layer time
dominates: 577 layers x 12 s), seam as above, neck wall 0.000 off the
mid-plane, overhang walls 0% of the outer wall, no support generated.
Expect longer in practice (0.2 nozzle estimates ran 1.4x under before).

After the print: cut the neck at the block (flush cutter or blade), sand
the top edge's rim flush on 400 then 800 grit on a flat surface. The rim is
0.3 wide, the neck remnant 0.22.

`elefant_foot_compensation` is 0 in the 3MF (the preset has 0.15): the
rounded underside already takes the foot, and shrinking layer 1 another
0.15 mm would leave layer 2's wall hanging 0.26 mm past it, more than a
line.

## Files

- `guitar_pick.py`: build123d source; `build(edge)` with `EDGES` = mirror (default), sym, soft, bevel, round, chamfer, square; writes `guitar-pick-<edge>.stl`; asserts one solid, 26.19 x 30.38 x 1.0 mm on Z=0, spline within 0.1 mm of the trace and convex, watertight STL. `outline()` exposes the trace, spline and a dense sample for standup.py.
- `standup.py`: the pick standing on its neck, block, plate and column, one solid; writes `guitar-pick.stl` (the print STL) and `standup.json` (heights, neck, held span, seam strip) for the pipeline and the page.
- `guitar-pick-mirror.stl`: the pick alone (mirrored 1.5 mm bevel, rounded rim). `guitar-pick-sym.stl`: the flat-printable alternative.
- `pipeline/make_standup_3mf.py`: the shipped 3MF (standing); paints the seam strip, checks the neck, seam, overhang and layer count in the real slice. `pipeline/make_print_3mf.py`: the flat pipeline, now pointed at `guitar-pick-sym.stl` and `guitar-pick-flat.3mf`, kept for the flat variants.
- `pipeline/edge_options.py`: builds the seven edge variants, cuts the tip section, tabulates the per-layer underside overhang, renders `images/edge-*.png` with OpenSCAD (above and below); writes `edge-options.json` for the sign-off page.
- `images/standup-iso.png`, `images/standup-neck.png`, `images/standup-tip.png`: OpenSCAD renders of the standing print. `images/pick-v6.png`: 4-view render of the flat sym model (v5 blended bevel, v4 round edge, v3 square, kept for the record).
- `pipeline/trace_photo.py`: photo trace; writes `outline-dunlop.csv` and `images/trace-overlay.png`.
- `pipeline/make_compare_page.py`: the sign-off page (published 2026-10-11: https://claude.ai/artifact/Xdy17d32z8uCNaQAHhxuis).
- `images/pick-v3.png`: 4-view render of the current model (v1 teardrop and v2 generic 351 kept for the record).

## Print file (flat, built 2026-10-11; superseded by the standing print above)

`guitar-pick-flat.3mf` from `pipeline/make_print_3mf.py` (not regenerated since the switch): machine `Bambu Lab X2D
0.2 nozzle`, process `0.08mm High Quality @BBL X2D 0.2 nozzle` with
layer_height 0.06 (0.1 first layer + 15 x 0.06 = 1.0 mm exactly; the stock
0.08 would print 0.98), filament `Bambu PETG Basic @BBL X2D 0.2 nozzle`,
Textured PEI 70 C, 250 C nozzle. Solid (100% zig-zag; the preset's gyroid is
refused at 100% by the CLI), arachne walls, seam at the top centre
(`seam_position` back; the slicer put it at the top centre on the round
and soft profiles and at the left shoulder of the top edge, x 121.0 y
141.5, on the sym profile; the check now asks for the top edge and an
aligned seam, within 2 mm between layers, rather than the exact centre), no ironing, skirt 2 loops /
3 mm / 1 layer, no brim. Centred on the bed, tip toward the front.

Slice (`guitar-pick-slice.json`, mirrored 38 degree bevel, 2026-10-12): 16
layers to z 1.0, 13 min 12 s estimated (0.2 nozzle estimates ran 1.4x
under on the Sharks tags, so expect about 18 min), 0.68 g, 0.22 m. Round trip through the CLI
and a real slice both pass. The verify step now also reads the outer wall's
tip position per layer from the G-code (arc moves evaluated properly: the
preset has arc fitting on, and a G2's endpoints sit above its lowest point)
and asserts no underside layer hangs more than 0.13 mm past the one below;
measured 0.127, 0.078, 0.068, 0.071, 0.068 mm for layers 2 to 6 on the
mirrored 38 degree bevel (0.01 to 0.02 above the geometry, as before).

## Open

- Open `guitar-pick.3mf` in Bambu Studio once (GUI ground truth), with the
  0.2 nozzle installed and the 0.2 machine selected in Studio; check the
  seam paint shows on the rear face in the preview.
- Print (about 2 h 11 min estimated, likely longer), cut the neck, sand the
  rim, then measure thickness and compare the feel against the Tortex.
- If the 2 h is too long: the PETG preset's 12 s minimum layer time is the
  lever (8 s would be about 1 h 20 min; the column keeps the tip cooling
  either way). Brian's call.
- If the neck tears or the pick wobbles: thicker neck (0.3) or a shorter
  one (0.2), both in `standup.py`.

## Decisions already locked

- PETG, plain face, one pick for the first print (Brian 2026-10-11).
- Measured outline over the generic 351 (tip radius differs by 1.1 mm); Brian approved the outline on the sign-off page 2026-10-11.
- Thickness 1.0 mm (measured).
- 0.2 mm nozzle, Brian's call 2026-10-11, for the smoothest edge and faces. (The 0.6 nozzle was never an option: a 1.0 mm pick is below its 1.24 mm two-wall minimum.)
- Edges tapered, not square (Brian 2026-10-12), and specifically the wide bevel with a curved lead-in and no noticeable line (Brian, same day, after seeing round, chamfer and bevel), then mirrored on both faces, no support material, and the rim rounded too (all Brian, same day).
- Printed standing on a snap-off base (Brian 2026-10-12: "the standup version with a base, as this will give the smoothest surface for PETG"; a nozzle change was allowed but the 0.2 stays). The base is part of the model, same filament, no slicer support.
- Smooth spline side instead of the traced polygon (2026-10-12), so the fillet has one edge loop and the print has no facets.
