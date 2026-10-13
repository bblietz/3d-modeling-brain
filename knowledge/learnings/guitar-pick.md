---
title: Guitar pick retrospective (Dunlop Tortex 1.0 copy)
date: 2026-10-12
status: first standing print 2026-10-12 lost its top-edge corners; rim and neck made two lines wide, second file sliced 2026-10-13, not printed
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
  base) is support by another name and needs the user's say-so. Brian
  gave it: see the stand-up design below.
- **Standing a thin part on a designed base.** What worked: the base is
  part of the model (same filament, one solid), a thin neck (0.3 mm tall)
  holds the outline wherever it faces down (the top edge arc and
  the shoulder rounds up to 45 degrees; above that the outline is steep
  enough to self-support), the block's top is the outline shifted down
  by the neck height so every layer of the neck sits on the layer below,
  and a 4 mm column of the same height beside the part makes the nozzle
  leave the thin tip cross-sections every layer. Land the total height on
  a layer boundary by deriving the base height from the part length. The
  neck held through all 577 layers of the first print. Its width is the
  catch, next bullet.
- **A snap-off neck beside a part's edge must be two lines wide, and so
  must the edge.** The first print (0.22 mm neck under a 0.30 mm rim) came
  off with chunks missing from both rounded corners of the top edge. On a
  sloped outline the neck ribbon sits BESIDE the part's edge in every
  layer, and a one-line rim is where the two face walls merge into one
  bead, so the neck was a spur off the end of that bead. Arachne printed
  the spur as its own 0.3 to 1.3 mm path, starting at the block and
  ending on the part's edge, laid the wall loop's U-turn over the spur's
  end, and put the loop's seam within 0.2 mm of it, on all 55 shoulder
  layers per side. Rim 0.44 and neck 0.40 (two 0.22 lines each, the neck a
  hair narrower so it breaks first) make the layer polygon two beads wide
  from the face along the neck into the block: one closed loop, no spur,
  no path end on the part. The loop's seam then wants the inside corner
  where the neck meets the block, so paint the block's rear face as a
  seam enforcer as well. Check it in the G-code with path starts and ends
  (`pipeline/toolpath.py`), not just loop starts: the first pipeline's
  "neck is a single line" and "all loops seam on the face" both passed on
  the bad file. Rule for any break-away tab on the X2D 0.2: tab and the
  edge it meets both at least 2 x 0.187 = 0.37 mm (the slicer's 85%
  minimum bead), the tab a little narrower than the edge. Brian's photos
  showed the bites deepest in the stretch the neck held and fading out
  about 2.5 mm above its end: damage at a junction propagates upward for
  a few dozen layers before the self-supporting stubs recover, so hold the
  outline a little further than the overhang rule alone requires (the neck
  now runs to the 60 degree point, 0.035 mm steps above it).
- **Arachne splits a loop at a rounded tip now and then.** With R 0.15
  creases on a 0.44 rim the strip's end dips below two beads for its last
  0.1 mm; on about 2 of 450 layers the slicer emits that as a one-layer
  break in the outer wall (a seam point on the edge, 0.06 mm tall). The
  0.30 rim did it on 3 layers. Tolerated and counted, not chased.
- **Pin the seam with paint, not with seam_position.** On a standing thin
  part the "back" seam sat at the end of the face's flat run and walked
  toward the tip with the outline; "aligned" would have gone to the rim.
  A 1.5 mm wide, 2 micron deep recess down the face gives the mesh its
  own triangles, and painting them `paint_seam="4"` in the 3MF object
  mesh (one unsplit enforcer triangle; the CLI keeps it through a round
  trip) put all 402 loops within 0.8 mm of the centre line. Splitting
  the solid with planes and fusing back without clean() does NOT keep the
  imprint in build123d (the fuse unified the faces and came back invalid).
  Scarf seams (`seam_slope_type external`) produced no ramp moves at all
  in the 02.08 CLI, on two different files; do not ship them unverified.
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

## Settings used (standing print, shipped)

0.2 nozzle, `0.08mm High Quality @BBL X2D 0.2 nozzle` with layer_height
0.06, `Bambu PETG Basic @BBL X2D 0.2 nozzle` (250 C / 70 C textured PEI),
solid zig-zag (the slicer still labels the column's fill "Sparse infill"
at 100%), arachne, four wall loops (the 1.0 mm body is four 0.25 lines),
seam back plus a painted seam strip on the rear face (and, since the
second slice, the block's rear face), no ironing, skirt
2 / 3 / 1, no brim, elephant foot at the preset's 0.15 (only the base
touches the bed). Edge, first print: 1.5 mm bevel dropping 0.35 on both
faces, creases blended R 5, rim creases R 0.15, 0.30 mm rim, 0.22 neck:
577 layers to 34.66 mm, 2 h 11 min estimated, 2.51 g of which 0.68 g is
the pick. Second print (2026-10-13): drop 0.28, rim 0.44, neck 0.40 run to
the 60 degree point, otherwise the same; 577 layers, 2 h 13 min
estimated, 2.74 g.

The flat alternative (`guitar-pick-sym.stl`, 0.45 mm symmetric bevel at 38
degrees) sliced to 16 layers, 13 min, 0.68 g, with the second layer 0.127
mm past the first; kept, not shipped.

## Pending

- The second standing print: are the corners clean, does the 0.40 neck
  break before the 0.44 rim, how the sanded thumb edge looks.
- Print result: thickness by calipers, edge smoothness, feel against the
  Tortex.
- Ironing coupon on a second pick if the 0.22 mm top lines show; the vault
  PETG rule is no ironing until a coupon says otherwise.
- Bottom finish comes from the plate; a Smooth PEI plate is the only route
  to a smooth bottom.

## Print (2026-10-12)

- Printed on the 0.2 mm nozzle, PETG Basic black, 250 C / 70 C, chamber 42 C, textured PEI, no slicer support, no ironing, 2-loop skirt. Finished 22:47 in the FINISH state with no HMS errors (read-only MQTT watch via `scripts/x2d-chamber-watch.sh`).
- The pick layers ran at 12.4 s per layer (281 layers in 58 min), which is the 12 s PETG minimum layer time plus travel to the cooling column. When the minimum layer time dominates, the slicer estimate is accurate; the 1.4x under-run seen on the flat 0.2 slices does not apply.
- Result (Brian, 2026-10-13): the neck held and the rim did not tear on removal, but "the outline of the pick was messed up at the top of the pick (the edge that was on the stand). The rounded corners had small chunks missing", "it was a bad print". His photos (`images/IMG_1659.jpg`, `IMG_1660.jpg`): the whole top edge ragged, both corners bitten to about 6 mm above the apex, the painted seam a faint centre line on the rear face, white scuffs on that face's upper left (unexplained; sanding or stringing). Root cause and fix above (two-line neck and rim, neck to 60 degrees); second file built and slice-verified the same day, not printed.
