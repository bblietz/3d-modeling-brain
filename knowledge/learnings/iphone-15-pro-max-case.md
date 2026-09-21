---
type: learning
project: iPhone-15-Pro-Max-case
date: 2026-09-20
status: design retrospective; print results pending (add measured fit, bridge quality and glue-joint notes after the first print)
tags: [x2d, tpu, phone-case, build123d, bambu-cli]
---

# iPhone 15 Pro Max case: retrospective (design phase)

Project: `projects/iPhone-15-Pro-Max-case/` (brief, source, 3MF). Materials note: [[tpu-x2d]]. Printer: [[printer-x2d]].

## Decisions locked (promoted from the handoff)

- iPhone 15 Pro Max, 1.5 mm walls, open cutout windows (no button covers), 0.4 nozzle, Bambu TPU 95A HF.
- Camera guard required; two pieces: ring printed flat and bonded with flexible CA (Brian chose this over printing screen-side down on supports).
- Guard SNUG around the raised camera island, not around Apple's plateau outer boundary; SLIM (2.5 mm), PLAIN (no cutaways), with a 1.5 mm 45 degree bevel on the inside.

- MagSafe pocket in the phone side of the back, to Apple's case-array geometry until Brian's own pieces are measured.

## What worked

- **Apple publishes dimensioned drawings.** developer.apple.com/accessories/dimensional-drawings/ has a PDF per iPhone (since ADG R30 they are no longer inside the guidelines PDF). Corners and the edge profile are splines given as ordinate points; buttons, ports, camera plateau, lens heights and keepout cones are all dimensioned. A research subagent read sheet 1 (no text layer) at 600 to 2400 dpi and cross-checked every value against the PDF's vector geometry (agreed within 0.02 mm).
- **Phone proxy solid first.** Building the phone from the drawing (body, buttons, plateau, lenses) and asserting `phone & case == 0` and `phone & ring == 0` on every run caught real errors and makes every later change safe.
- **Apple's keepout cones as solids.** Asserting the six camera, flash and rear-sensor cones against the ring caught a 0.03 mm3 violation I had reasoned away: the plateau's corner curve comes within 8.25 mm of the rear-sensor axis, not the straight run's 8.32. For the snug ring the same cone solids became the cutters (grown 0.15 mm).
- **Section close-ups from the real meshes** (`pipeline/sections.py`, trimesh section + shapely even-odd fill + matplotlib): crisp, to scale, annotated. Far better than shaded matplotlib 3D views for lips, windows and clearances. Reusable for any project.
- **Apple's MagSafe case array is fully dimensioned** in ADG chapter 42 (Fig 42-2 to 42-4): ring 54.10 / 46.00 x 0.55, clocking magnet 6.00 x 19.31 from 31.18 to 50.49 below the ring centre (toward the bottom edge), centred on the product centre within 0.30, at most 0.85 of case between magnets and the outside, back 2.1 max. Apple buries the magnets 0.55 under the inside surface; for insert-after-printing, an open pocket on the phone side with the pieces 0.25 below the surface does the same job.
- **A real slice as the last check.** It caught two things the geometry could not: the ring's sparse core, and the wrong plate centring.

## What failed, and the fix

- **OCCT 2D `offset()` of a spline outline returns 44 edges (from 8).** Lofts between such outlines fail (`StdFail_NotDone`) or hang (my first run sat for 10 minutes on an 82-section loft). Fix: generate every inset or outset outline myself by moving sampled points of the corner curve along its normals and re-splining (`squircle(w, h, corner, inset)`), always 4 splines + 4 lines. Areas match OCCT's offset within 0.1 mm2. Then every round, chamfer and taper is a ruled loft through explicit `(z, inset)` levels: no `fillet()` on spline edges at all, the whole model builds in 10 s.
- **A spline through sparse profile points overshoots.** Apple's edge profile has a long shallow last span; the spline dipped past the glass plane. Added three eased points on that span and asserted monotonic and non-negative.
- **The first guard ring was sized to the wrong feature.** I used Apple's "plateau outer boundary" (the base of the glass ramp). Brian: "the guard around it is too big. It should be snug around the camera." People see the raised island, not the ramp's base. Rule: fit guards and openings to the feature the eye reads; use the drawing's outer keepouts only as clearance limits.
- **The second ring over-served the guideline and under-served the eye.** Snug but 5.1 mm wide (flush to the case edge for glue land and alignment), with Apple's flash and LiDAR cones cut out as dished cutaways. Brian: "the ring is too thick and there are cutouts in the top right and bottom right. Not good", then "the guard should also be a bevel on the inside". Third ring: 2.5 mm, plain, bevelled, its inside wall flush with the camera opening (which gives the alignment and the glue land back without the width). Rule: on a cosmetic part, state a guideline tradeoff in one line and let Brian choose BEFORE building the compliant-but-ugly version; and show the viewer early, all three corrections came within minutes of him seeing the model.
- **A cone cut alone left a 0.45 mm tongue** under the rear-sensor cone's base (the cone starts at the plateau's height with a 7.31 radius). Carried the cutaway straight down through the glue face. Found only in the section render.
- **`pkill -f <script>` killed its own shell** (the pattern matched the command line running it). Use a PID, or `pkill -f` from a command line that does not contain the pattern.

## Bambu CLI pipeline findings (apply to every project's make_plate script)

- **X2D machine presets keep ALL their G-code in `include` templates** (`Bambu Lab X2D 0.4 nozzle template machine_start_gcode.json` and four more), and X2D filament presets `include` the six-variant filament template. The vault's older `flatten()` (Garmin, NACS, Leader-cards, NACS-organizer `make_plate.py`) follows only `inherits`, so their verification slices ran with a generic fallback start G-code (prime lines, M109 S205) and under-report time (7 min 39 s vs 12 min on a small probe). The shipped 3MFs were fine because Studio's GUI re-resolves the system preset on open. `projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py` merges includes: includes first, then the preset's own keys, base of the chain first. Assert `"X2D start gcode" in gcode`.
- **The CLI does not re-centre meshes on `--export-3mf`**: a part's place on the bed is item transform + the STL's own bounds. Centring by the item transforms alone put the plate 28 mm off in y. The slicer's output does re-centre, so its transforms are the real part centres (useful for a check).
- **Bambu keeps the "Sparse infill" label at 100% density.** Check solidity by weight: sliced grams vs mesh volume x `filament_density` (got 29.4 vs 29.7 g).
- Two TPU parts on one plate, `--arrange 1`, land 2 to 3 mm apart: short travel between them.

## Settings used (unvalidated until printed)

X2D 0.4 nozzle, `0.20mm Standard @BBL X2D`, `Bambu TPU 95A HF @BBL X2D 0.4 nozzle` (230 C, textured plate 35 C, 12 mm3/s), Textured PEI, Arachne, 4 wall loops, 100% zig-zag infill, avoid crossing walls. 53 min, 29.4 g, 54 layers.

## Still to measure on the first print

Cavity fit at 0.10 per side, lip hold and insertion effort, sag on the 22 mm volume-window bridge, stringing across the cavity, button reach through the windows (faces 1.15 mm below the surface), ring fit around the island, CA bond after a week of use.
