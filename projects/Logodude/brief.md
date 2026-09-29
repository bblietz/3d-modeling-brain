---
title: Logo Dude die-cut badge
type: project
status: awaiting viewer sign-off (smooth jaw v4)
date: 2026-09-29
tags: [3d-print, logo, multi-color, x2d]
---

# Logo Dude die-cut badge

Brian's hand-inked "logo dude" drawing (brush-stroke zigzag hair over a
face with eyes, nose, mouth) as a two-color print.

## Source

- `images/logo-dude.png`, 1095 x 1166 px RGB scan of black ink on white,
  from Google Drive (`logo-dude.png`, fileId 1AA1bLM7tQxt-SXbMhv7ZE-v-0gFypozw;
  identical copies sit in several Logo Files folders, plus `logo-dude.sketch`
  and `logo-dude.xcf` sources).
- Traced 1:1 by `pipeline/trace.py`: 50% gray iso-contour (contourpy) on a
  0.8 px blur, specks under 40 px dropped. 10 ink shapes, 148 dry-brush
  holes; traced area within 0.1% of the thresholded scan. Output `traced.json`.

## Decisions

- Style B, die-cut outline (chosen 2026-09-29 from `options.html`, published
  at https://claude.ai/artifact/VCGQtaf81iee7eEn2dVSbT). A plaque and a desk
  stand were the other options.
- 4 in tall overall (Brian 2026-09-29): backer 104.20 x 101.60 x 3 mm
  (4.10 x 4.00 in), solved and asserted in `logodude.py`; ink 97.2 x 94.6 mm,
  3.5 mm outline margin, raised 1 mm. One color change at z = 3 mm.
- Solid lines (Brian 2026-09-29, "clean up the black lines so they are
  solid"; this overrides the keep-the-trace-exact default): dry-brush streaks
  filled by a per-shape morphological close/open in source px. Hair 14/10 px,
  face 3/3 px; stronger face values fill the tapered eye corners and the
  channel under the doubled eyelid, hair 20/14 splits a stroke. Loose
  slivers under 300 px dropped. Result: 6 solid shapes.
- Face lines about 1.2 to 1.5 mm at this scale.
- Right hair stroke fix (Brian 2026-09-29, "small gap on the right side"):
  its outer streaks are fainter than the trace threshold, so the edge
  stepped in; a 60 px close applied only right of that stroke's centerline
  fills it (a global close of 26+ px fills the zigzag V gaps).
- Smooth edges (Brian 2026-09-29, "smooth all the way around", "smoothen
  all edges of the black lines"): every ring Gaussian-smoothed along its
  arc length (hair sigma 14 px, face 5 px, outline 2.5 mm) and built as a
  periodic spline. Outline keeps at least 2.5 mm past the ink (asserted).
  Final: 4.11 x 4.00 in backer, ink 98.0 x 95.2 mm.
- Jaw (Brian 2026-09-29, "smooth out the bottom edge of the face, in the
  jaw area"): the face-outline stroke gets sigma 40 px below source row
  1060, ramped in from row 1000 (smoothstep), so its ends keep their shape.
  The bumps were about 6 mm long, so 16 px did nothing visible; 60 px trips
  the thinning assert. Gotcha: shapely `.geoms` returns new objects on
  every access, so `p is not x` over `.geoms` never excludes anything; the
  jaw was unioned back in unsmoothed until the piece list was materialized.
  An overlap assert now guards it.
- OCC area/volume integration is wrong on long periodic splines (0.8% on
  the outline face, 14% on its extrusion); all checks measure the
  tessellated mesh instead.
- Planned: 0.4 nozzle, PLA Basic white + black, fill-core modifier recipe
  over the thin face lines (knowledge/lettering-x2d.md).

## Build

- `logodude.py` (build123d): asserts on area, volume, Z tiers, one backer
  solid, ink inside the backer. `EXPORT=1` writes `logodude-backer.stl`
  and `logodude-ink.stl` (both watertight); `SHOW=1` pushes to the viewer.
- Fixes found on the way: shapely buffers flip ring winding, so extrudes
  pass `dir=(0, 0, 1)`; five streak holes touched the stroke edge at a
  single point (non-manifold once extruded), nicked with a 0.005 mm disk.

## Print file (2026-09-29)

- `logodude.3mf`: one object "Logo Dude badge", parts "backer (white)"
  (filament 1, #FFFFFF) and "ink (black)" (filament 2, #000000), plate
  center, Bambu PLA Basic @BBL X2D 0.4 nozzle for both, X2D 0.4 nozzle,
  `0.12mm High Quality @BBL X2D` with the locked lettering recipe keys
  ([[lettering-x2d]]), textured PEI 65 C (the preset says 55; vault rule
  [[printer-x2d]]). Built and verified by `pipeline/make_print_3mf.py`;
  slice summary in `logodude-slice.json`.
- Fill-core modifier over the five face strokes only (outline + 0.3 mm,
  z 2.96 to 4.08 = the nine ink layers), `infill_direction 0`; the hair
  (0.1% of it narrower than 2.5 mm) keeps the normal process. Object key
  `detect_narrow_internal_solid_infill 0`. No concentric modifier: the
  key's side effect stays in hidden layers.
- Offline slice: 33 layers, 1h 24m, 23.38 g white + 3.17 g black
  = 26.55 g; one change (T1) at the 3.08 layer, 280 mm3 flush
  (placeholder; re-calculate in Studio). Prime tower at (40, 87.5),
  left of the badge, brim 12.0 mm from it.
- Not printed yet. Face strokes are thinner (1.2 to 1.5 mm) than the
  Sharks letters the recipe was proven on; recipe step 4 suggests a
  thin coupon before the real part.
