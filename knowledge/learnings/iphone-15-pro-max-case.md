---
type: learning
project: iPhone-15-Pro-Max-case
date: 2026-09-20
status: design retrospective; print results pending (add measured fit, bridge quality and glue-joint notes after the first print)
tags: [x2d, tpu, petg, snap-fit, phone-case, build123d, bambu-cli]
---

# iPhone 15 Pro Max case: retrospective (design phase)

Project: `projects/iPhone-15-Pro-Max-case/` (brief, source, 3MF). Materials note: [[tpu-x2d]]. Printer: [[printer-x2d]].

## Decisions locked (promoted from the handoff)

- iPhone 15 Pro Max, 1.5 mm walls, open cutout windows (no button covers), 0.4 nozzle, Bambu TPU 95A HF.
- Camera guard required; two pieces (Brian chose this over printing screen-side down on supports). First a TPU ring bonded with flexible CA; then "the guard should be petg and snap into place": rigid PETG, no glue.
- Guard SNUG around the raised camera island, not around Apple's plateau outer boundary; SLIM (rim 3.0 mm), PLAIN (no cutaways), with a 1.5 mm 45 degree bevel on the inside of the rim.
- NO bevel inside the case around the camera: plain square cutout; the ring carries a plug that goes into it. The snap's groove is buried in the cutout's wall, so the inside still reads as a plain hole.
- Print 3MF: two plates, one per material ("one for the guard and one for the case").

- MagSafe pocket in the phone side of the back for Brian's standard 0.4 mm ring; locates by the 46 ID, takes 54 to 56.5 OD.

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
- **The third ring hid its cost inside the case.** To carry a slim snug ring I sloped the case floor in over the glass ramp, down to a one-layer feather edge. Brian: "the inside of the case, around the camera should not have a bevel, only the guard has a bevel". Fourth ring: plain square cutout in the case, and a square plug under the ring's rim that drops into it. Better in every way: no feather edge, the ring locates itself for gluing, it bonds in shear on the plug's wall, and it prints as glued (rim face down, plug up) with only two 45 degree overhangs. Rule: when a mating part needs relief around an awkward feature, put the relief on the small add-on part, not on the main body.
- **Rigid ring, soft case: the snap belongs in the case's thickness (fifth ring).** A PETG part cannot flex, so the TPU must. There is no room behind the back for a flange (the phone's glass lies on the floor and the camera's glass ramp starts 0.4 mm inside the cutout), and on two sides the cutout runs 0.74 mm from the walls. So: a barb all round the plug, a groove for it buried in the cutout's 1.6 mm wall, and the 0.6 mm of back under the groove (the flap) as the spring. The flap ends up captive in the ring's own groove between the rim's land and the barb, which is what holds: a flat holding face square to the pull, no cam-out. Way in: 45 degree lead-in, hook the two wall-side edges first, then work the free edges over like a button. UNPROVEN until printed; first numbers: neck -0.05, barb 0.40 over a 0.6 x 0.5 flap.
- **The slicer cuts at mid layer, so design overhang steps on its planes.** The ring prints rim down and the barb's holding face is an overhang. A 45 degree root chamfer of one layer looked right in CAD, but sampled at mid layer it prints as steps of 0.10 then 0.35 (the 0.35 line 17% carried). Building the root as a square step gives 0.20 then 0.25, each line about half carried. Check: section the STL at the slicer's planes (layer mid heights) and print the outline width per layer.
- **OCCT booleans pollute their inputs.** A probe boolean with nearly coincident faces (the ring pushed 0.1 mm into the case) grew the tolerances of the shared solids, and every later `ring & case` returned rubbish (0.0 or 210 mm3 for a true 22). Run such probes on `copy.deepcopy()` of both solids, and keep test positions off planes where faces coincide.
- **A cone cut alone left a 0.45 mm tongue** under the rear-sensor cone's base (the cone starts at the plateau's height with a 7.31 radius). Carried the cutaway straight down through the glue face. Found only in the section render.
- **`pkill -f <script>` killed its own shell** (the pattern matched the command line running it). Use a PID, or `pkill -f` from a command line that does not contain the pattern.

## Bambu CLI pipeline findings (apply to every project's make_plate script)

- **X2D machine presets keep ALL their G-code in `include` templates** (`Bambu Lab X2D 0.4 nozzle template machine_start_gcode.json` and four more), and X2D filament presets `include` the six-variant filament template. The vault's older `flatten()` (Garmin, NACS, Leader-cards, NACS-organizer `make_plate.py`) follows only `inherits`, so their verification slices ran with a generic fallback start G-code (prime lines, M109 S205) and under-report time (7 min 39 s vs 12 min on a small probe). The shipped 3MFs were fine because Studio's GUI re-resolves the system preset on open. `projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py` merges includes: includes first, then the preset's own keys, base of the chain first. Assert `"X2D start gcode" in gcode`.
- **The CLI does not re-centre meshes on `--export-3mf`**: a part's place on the bed is item transform + the STL's own bounds. Centring by the item transforms alone put the plate 28 mm off in y. The slicer's output does re-centre, so its transforms are the real part centres (useful for a check).
- **Bambu keeps the "Sparse infill" label at 100% density.** Check solidity by weight: sliced grams vs mesh volume x `filament_density` (got 29.3 vs 29.5 g).
- Two TPU parts on one plate, `--arrange 1`, land 2 to 3 mm apart: short travel between them.
- **Two plates, two materials, one project: use the CLI's own assembler** (`--load-assemble-list`, as in `projects/Sharks-nametag/pipeline/plates.py`), one plate entry per material with `"filaments": [n]`. It writes the plates, the plate-2 offset (307.2) and the per-part `extruder` itself. `pos_x/pos_y` place the STL's ORIGIN (plate-relative), so subtract the part's own bbox centre. Every object is named `assemble_1`: rename by each part's `source_file`. Then patch: `filament_colour`, `filament_map`, `filament_nozzle_map` to one entry per filament (the CLI leaves one); `flush_multiplier` one per extruder and `flush_volumes_matrix` = extruders x filaments^2 entries, or the slice dies with "Flush volumes matrix do not match"; `filament_map_mode` Manual in the config and in each plate block (+ `filament_maps`). With the include-merging `flatten()` the per-variant filament keys come out right (2 x 6 values) with no extra work. Slice each plate with `graft_slice(plate=n)`; `slice_info` lists only the plate's own filament, `group_id="0"` = extruder 1. A `T1` in Bambu G-code selects filament 2, not extruder 2.
- **PETG Basic's flow ratio is 0.95**: the slicer weighs what it extrudes, so a solid PETG part weighs mesh volume x density x 0.95 in `slice_info` (TPU 95A HF: 1.0).
- **OpenSCAD makes better headless pictures than matplotlib**: `color() import(stl)` scenes with `--preview --camera=...`, a third of a second each, z-buffered and coloured per part (`pipeline/renders.py`).

## Settings used (unvalidated until printed)

X2D 0.4 nozzle, `0.20mm Standard @BBL X2D`, Textured PEI, Arachne, 4 wall loops, 100% zig-zag infill, avoid crossing walls, 2-loop skirt, 30 mm/s first layer; both filaments on extruder 1. Plate 1, case: `Bambu TPU 95A HF @BBL X2D 0.4 nozzle` (230 C, plate 35 C, 12 mm3/s), 54 min, 27.5 g, 54 layers. Plate 2, ring: `Bambu PETG Basic @BBL X2D 0.4 nozzle` (250 C, plate 70 C), 11 min, 2.0 g, 23 layers.

## Still to measure on the first print

Cavity fit at 0.10 per side, lip hold and insertion effort, sag on the 22 mm volume-window bridge, stringing across the cavity, button reach through the windows (faces 1.15 mm below the surface), ring fit around the island. The snap: effort to get the ring in, whether it stays in through a week of pockets and through taking the case off the phone, how the barb's two overhang steps printed, neck fit (rattle or squeeze). These will be the vault's first snap-fit numbers: promote them to a `knowledge/snap-fits-x2d.md`.
