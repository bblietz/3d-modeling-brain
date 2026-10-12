---
title: Guitar pick retrospective (Dunlop Tortex 1.0 copy)
date: 2026-10-12
status: modelled and sliced with a mirrored 38 degree bevel, print pending
tags: [learning, 3d-print, petg, 0.2-nozzle, photo-trace]
---

# Guitar pick retrospective

A plain 1:1 copy of the Dunlop Tortex Standard 1.0 mm pick in PETG on the
0.2 mm nozzle. Project: [[projects/Guitar-pick/brief]].

## What worked

- **Caliper photos as the scan.** Brian had no scanner. A phone photo of the
  pick clamped in digital calipers gives the scale for free: the part's
  extent across the jaws IS the caliper reading, so no ruler and no DPI
  guess. `pipeline/trace_photo.py` segments the pick on colour saturation
  (the Tortex blue is s >= 0.6, the steel jaws reflect a dull blue at
  s <= 0.4, so hue alone leaks into the jaws), takes a subpixel contour,
  aligns by PCA, symmetrizes, smooths, hulls, then stretches to the two
  readings. A 665 px wide photo gave about 0.17 mm per pixel; two photos
  agreed on the tip radius within 0.15 mm.
- **Measuring instead of trusting the generic shape.** The Iron Age 351 SVG
  looked right and matched the published 26 x 30 mm size, but a circle fit
  on the traced tip showed the Dunlop at 4.5 mm radius against the SVG's
  3.4 mm, with the lower sides about 0.9 mm fuller per side. That is the
  part a player feels. The tip-radius and widest-point metrics are cheap
  and worth keeping for any traced outline.
- **Reusing the Skateboard 3MF pipeline.** Copy, drop the pads, swap the
  presets, adapt the checks. The include-merging flattener and graft_slice
  verification carried over unchanged.

## What failed or surprised

- **Wrong model for design work.** A Sonnet 5.5 session built two outlines
  (a teardrop from guesses, then the generic SVG) before Brian noticed.
  Rule saved to memory: design work stops on a non-Fable model before
  anything is built.
- **A photo with the part under the caliper beam is clipped.** In IMG_1656
  the pick's top sat under the beam and the trace lost 2 mm of length,
  which silently skewed the PCA alignment. Keep the part between the jaws
  with nothing else over it; cross-check the trace's free axis against the
  other photo's reading, which is how the clip was caught.
- **Gyroid is refused at 100%.** The 0.2 presets use gyroid sparse infill;
  with `sparse_infill_density` 100% the CLI exits 238 ("Param values in
  3mf/config error: sparse_infill_pattern: gyroid doesn't work at 100%
  density"). Set `sparse_infill_pattern` zig-zag with it. The detail line
  comes after the "Param values" line in the CLI output.
- **A square edge on a handheld part.** The first model extruded the
  outline as-is and Brian caught the 90 degree edge on the render. Anything
  held or stroked (picks, handles, lips) needs its edge profile decided in
  Phase 2, not left to the extrusion. Research found the real Tortex
  Standard is die-stamped square and wears into a bevel, so there was no
  number to copy; the profile became a sign-off choice (round, chamfer,
  bevel) drawn at scale. Brian chose the bevel but with "no noticeable
  line": a crease between a face and a bevel is felt even at 13 degrees,
  so the crease got a R 5 fillet (chamfer first, then fillet the face's
  new outer edge loop; OCC takes a 5 mm fillet on a 167 degree edge along
  a convex spline without complaint). Lesson: when a hand touches a
  transition, blend it; a chamfer alone is never the finished answer.
- **Mirrored edges and a flat print do not mix.** Brian then wanted the
  1.5 mm bevel on both faces and no support material. The underside of a
  flat print can carry about 38 degrees at most (0.06 mm layers, 0.22 mm
  line: layer 2 at half a line, the band at a third); a 13 degree band
  needs 0.26 mm per layer, laid in air, and thinner layers do not fix it
  (0.04 mm still steps 0.17). So a symmetric edge profile on a flat print
  is at most about 0.45 mm wide for a 0.35 mm drop. Decide the edge
  profile AND the print orientation together in Phase 2 for anything
  symmetric and thin; the alternative (standing the part on a snap-off
  base) is support by another name and needs the user's say-so.
- **The "back" seam is not always the centre.** Bambu's rear seam landed
  at the top centre on two profiles and at the top edge's left shoulder on
  a third, with nothing changed but the edge profile. A G-code seam check
  should ask for the region (the top edge, aligned within 2 mm) rather
  than an exact point.
- **A flat print cannot carry a shallow taper underneath.** With 0.06 mm
  layers and a 0.22 mm wall, each layer's outer wall can hang about half a
  line past the one below, so the underside slope must be about 45 degrees
  or steeper. A 1.5 mm wide bevel (13 degrees) is fine on top and prints in
  air underneath; a R 0.45 fillet costs one 62 degree layer at the very
  bottom. Elephant-foot compensation (0.15 in the presets) shrinks layer 1
  on top of that and would have pushed layer 2 past a full line: set it to
  0 whenever the underside edge is rounded.
- **G2/G3 arcs hide the toolpath extremes.** The 0.2 presets have arc
  fitting on, so the tip of the pick is drawn as arcs whose endpoints sit
  up to 0.15 mm above the arc's lowest point. A G-code check that reads
  only endpoints produced nonsense per-layer steps (negative, oscillating).
  Any geometry check on Bambu G-code must evaluate G2/G3 (centre from I/J,
  test whether the sweep passes the extreme angle).
- **Splining straight through convex-hull vertices overshoots.** The trace
  polygon's hull leaves gaps up to 4.7 mm between vertices on the top edge,
  and a periodic interpolating spline through them bulged 0.21 mm past the
  trace at the shoulders. Resample the polygon every 0.25 mm, Gaussian
  smooth along the outline (sigma 0.6 mm), then spline: within 0.06 mm of
  the trace, convex, and no 1.7 mm facets (the polygon's facets were 0.08
  mm deep at the tip and would have printed).
- **Stock 0.2 layer heights do not divide a 1.0 mm part.** 0.1 first layer
  + 11 x 0.08 = 0.98; the slicer drops the partial top layer, so the pick
  would print 2% thin. 0.06 (15 layers) or 0.10 (9 layers) land on 1.0
  exactly. The pipeline asserts the layer count and the top Z from the
  G-code.

## Settings used

0.2 nozzle, `0.08mm High Quality @BBL X2D 0.2 nozzle` with layer_height
0.06, `Bambu PETG Basic @BBL X2D 0.2 nozzle` (250 C / 70 C textured PEI),
solid zig-zag, arachne, seam back (proven at the top centre from the outer
wall start points in the G-code), no ironing, two top walls
(`top_one_wall_type` not apply), skirt 2 / 3 / 1, no brim, elephant-foot
compensation 0 (rounded underside). Edge: 0.45 mm bevel dropping 0.35 (38
degrees) on both faces, creases blended R 0.35, 0.30 mm rim. 16 layers,
13 min 12 s estimated, 0.68 g. Underside steps from the G-code: 0.127 mm
at layer 2, then 0.07 to 0.08 per layer up the band.

## Pending

- Brian's pick between the mirrored 38 degree bevel (built), the 1.5 mm
  bevel on top only, and a stand-up print for the full mirrored bevel.
- Print result: thickness by calipers, edge smoothness, feel against the
  Tortex, the real print time against the estimate.
- Ironing coupon on a second pick if the 0.22 mm top lines show; the vault
  PETG rule is no ironing until a coupon says otherwise.
- Bottom finish comes from the plate; a Smooth PEI plate is the only route
  to a smooth bottom.
