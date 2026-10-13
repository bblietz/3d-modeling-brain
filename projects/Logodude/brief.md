---
title: Logo Dude die-cut badge
type: project
status: CAD signed off; PETG 3MF sliced; not printed
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
- Material switched to PETG Basic white + black (Brian 2026-09-29, spools in the AMS); 0.4 nozzle, fill-core modifier recipe
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

## PETG reslice (2026-09-29)

- `pipeline/make_print_3mf.py` now uses `Bambu PETG Basic @BBL X2D 0.4 nozzle` (250 C, 245 C first layer),
  textured PEI 70 C. Slice: 1h 25m, 22.51 g white + 3.06 g black = 25.57 g, 33 layers, change at z 3.08.
- PETG type assumed Basic: the AMS saw spools in slots 2 and 3 but read no Bambu tag data (tray_is_bbl_bits 0),
  so Studio could not sync them. Fix: reseat the spools or set the slots by hand.
- Printer had the 0.6 HF nozzle mounted on 2026-09-29; this file needs the 0.4 swapped in.
- Printer IP moved to 192.168.1.50 (scripts/x2d-status.py default updated).

## Desk stand (style C, 2026-09-29)

- `logodude_stand.py`: a standee. The figure is the badge (same outline and ink) plus a 36 mm plain white tab
  under the jaw, with 2 mm neck fillets and 0.8 mm lead-in chamfers; the outline's lowest point sits 0.5 mm above
  the base top, so the whole face stays visible. Base: 80 x 34 x 12 mm black PETG stadium, 3 mm top fillet,
  slot 36.6 x 3.3 x 9 mm with a 0.8 mm lead-in, 4 R1 crush ribs 0.35 mm proud (friction-fits-x2d.md recipe:
  0.15 mm free per side, 0.20 mm interference). Standing height 114.1 mm (4.49 in).
- Fit measured from geometry probes and true-scale mesh sections (`images/stand-fit-sections.png`).
  The rib numbers are the PLA / 0.6 nozzle calibration; PETG is unproven: if the figure is loose or will not
  go in, change RIB_PROUD.
- A single periodic spline through the tab's sharp corners overshot (tab bottom sagged 0.018 mm), so the
  figure face is built by `cornered_face`: lines for straight runs, splines for curved runs.
- Print file: ONE `logodude.3mf`, TWO plates (2026-09-29, one-multi-plate rule). The earlier three-plate version
  opened fine in the GUI; Brian then combined the stand plates: "Edit the file to make the 2 items in the print have a
  border such that they print separately" and "make them print separately but on the same plate".
  - Plate 1 "Badge", by layer, unchanged: 1h 25m, 22.51 g white + 3.06 g black, 33 layers at 0.12, tower (40, 87.5).
  - Plate 2 "Stand", BY OBJECT (plate-level print_sequence; survives the CLI round trip), each object with its own
    skirt, Brian's GUI layout (figure upper right, base lower left, hulls 110.6 mm apart, 60 needed): the figure
    prints first at 0.12 layers (33, fill-core modifier + key), one change to black at z 3.08 flushed to the chute, then
    the base on black at 0.2 layers (60) with the approved 0.20mm Standard object keys (15% grid infill, 3 bottom
    shells, 1 mm top shell, bridge flow 1, classic walls, 0.20 Standard speeds). No prime tower. 1h 47m, 22.62 g white
    + 14.58 g black.
  - Built and verified by `pipeline/make_print_3mf.py` (the process stays 0.12mm High Quality + the locked recipe keys,
    not the 0.20mm Standard Studio switched to in Brian's GUI save); per-plate report in `logodude-slice.json`.
    Needs a GUI open to confirm plate 2 shows both objects with "By object" set.

## Luggage tag (2026-10-13)

Brian: "I want to create a luggage tag, where my name email and phone numbers
are on the back ... Alter the size accordingly. Create a new 3MF file,
preserving the work we have already done." Then: "this will be done with .6mm
nozzle", then "I can go with .4mm, but I need the print to take less than
1.25hrs". CAD signed off in the viewer ("cad looks good, create 3mf").

- `logodude_tag.py` (build123d) imports `logodude.py` for the traced, cleaned,
  smoothed ink and re-solves the scale: silhouette 3.00 in tall (face + hair,
  outline included), tag 78.3 x 85.2 mm overall (3.08 x 3.35 in) with the
  eyelet, 3.08 mm white backer + 0.96 mm black ink = 4.04 mm. Same 3.5 mm
  outline margin as the badge. Ink 71.9 x 69.7 mm, 0.0698 mm/px.
- Eyelet: a 13 mm round lobe on the backer's centroid axis (x 0.8) so the tag
  hangs straight, 6 mm hole (worm loops, cable loops, silicone straps), 3.5 mm
  wall, 4 mm fillet into the outline; the hole keeps 2.5 mm from the ink
  (asserted). It sits between the two central hair peaks.
- Back text, inlaid flush into the bottom face (black into white, the first
  3 layers, 0.52 mm deep), mirrored about YZ so it reads after flipping the
  tag over (asserted on the mirrored centroid; checked in
  `images/tag-front-back.png`). Russo One (installed in ~/.local/share/fonts):
  every stroke is 0.25 x cap height, so the lines are sized to the clean
  two-bead regime of the 0.4 nozzle (0.86 to 1.10 mm strokes, two 0.42 mm
  arachne beads, no fill-core modifier): BLIETZ 4.4 mm caps, the two phone
  numbers 4.0, the email 3.5. Block above the waist of the silhouette (the
  back is an hourglass: face, a waist where the hair arms leave it, the
  forehead band, the peaks), 2.5 mm inside the outline, 3 mm line gap,
  centred on the band's own axis. Letters 49 pieces, 317 mm2.
- Nozzle: 0.4. The 0.6 would need two 0.62 mm beads per stroke, i.e. 5 to
  6 mm caps and a 3.5 in tag (variant D on the options page); the face
  strokes at 3 in (0.92 mm thinnest) are two 0.42 beads at 0.4.
- Options drawn to scale from the geometry in `tag-options.html`
  (`pipeline/tag_options.py`, variants via `TAG_IN=`, `EYELET=hole|slot|punch`,
  `NOZZLE=0.6`): A built; B strap slot 14 x 3.2 (tag 3.24 in tall); C hole
  punched through the forehead (silhouette unchanged, text block moves into
  the face region); D 3.5 in for the 0.6 nozzle. Brian signed off A in the
  viewer before the page was needed.
- Exports: `logodude-tag-backer.stl`, `logodude-tag-ink.stl`,
  `logodude-tag-text.stl` (all watertight, same coordinates, on z = 0).
  `EXPORT=1` writes them, `SHOW=1` pushes to the viewer, `DUMP_2D=<json>`
  dumps the 2D geometry for the options page. The badge files are untouched.
- Print file `logodude-tag.3mf` (built and verified by `pipeline/make_tag_3mf.py`,
  report `logodude-tag-slice.json`): one plate, one object "Logo Dude luggage
  tag" with parts backer (white, filament 1), ink (black, 2), back text
  (black, 2); X2D 0.4 nozzle, `0.16mm Standard @BBL X2D` with arachne walls,
  skirt 2 loops, 100% zig-zag infill (solid, the eyelet gets yanked), no brim,
  elephant-foot compensation 0 (flush inlay edges), prime tower rib + fillet
  wall + 5 mm brim at (180, 112.5); PETG Basic white + black, textured PEI
  70 C, 250 C. Offline slice: 25 layers, 53 min (cap 75), 18.09 g white +
  2.41 g black = 20.5 g, 4 filament changes (starts on black for the letters:
  L1 to white, L2 black, L3 white, L20 black for the ink). G-code proofs: every
  black move in layers 1 to 3 inside the text footprint, every black move
  above z 3.08 inside the ink footprint, no black in layers 4 to 19, no white
  above the backer. Studio: select the 0.4 nozzle preset BEFORE opening the
  file, AMS white / black, Flushing Volumes: Re-calculate. Not printed.

## Luggage tag, 0.6-nozzle version (2026-10-13)

Brian printed `logodude-tag.3mf` (built for the 0.4) through the 0.6 nozzle by
mistake, then asked: "build the 3.5 in version for the .6".

- Same `logodude_tag.py` with `NOZZLE=0.6`: silhouette 3.50 in, tag 91.4 x
  97.3 mm overall (3.60 x 3.83 in), 3.0 mm backer + 0.9 mm ink on the 0.6
  grid (0.3 first layer + 0.18 layers: backer 0.3 + 15 x 0.18, ink 5 layers),
  text inlay 0.66 mm (3 layers). Face strokes 1.07 to 1.3 mm = two 0.62 beads.
- Back text in the two-bead regime of the 0.62 line (caps 4.4 to 6.2): BLIETZ
  6.2 mm caps (1.56 mm strokes), bblietz@gmail.com 5.0 (1.22), the phones
  5.4 (1.36). The email sits under the name because at 5 mm caps it is 66 mm
  wide and only fits the forehead band; the conventional order would push
  the name up into the notch between the hair peaks (asserted fit).
- Exports `logodude-tag-06-{backer,ink,text}.stl`, plot
  `images/tag-06-front-back.png`; pushed to the viewer 2026-10-13.
- Print file `logodude-tag-06.3mf` by `pipeline/make_tag_3mf.py` with
  `NOZZLE=0.6`: X2D 0.6 nozzle, `0.18mm Balanced Quality @BBL X2D 0.6 nozzle`,
  PETG Basic 0.6 white + black, same locked keys as the 0.4 build; report in
  `logodude-tag-06-slice.json`. The 0.6 machine's PETG preset is the
  unsuffixed `Bambu PETG Basic @BBL X2D` (250 / 245 C, textured PEI 70).
  Offline slice: 21 layers, 51 min (cap 75), 23.1 g white + 3.2 g black =
  26.3 g, 4 filament changes (L1 to white, L2 black, L3 white, L17 black),
  tower (185, 115). G-code proofs as for the 0.4 file (black only in the
  text footprint for layers 1 to 3 and the ink footprint above z 3.0, no
  white above the backer). Studio: select the 0.6 nozzle preset BEFORE
  opening the file. Not printed.
- Meanwhile the mis-print of the 0.4 file was running on the printer
  (Studio had re-profiled it to the 0.6's 0.30 mm process, 13 layers,
  38.7 g, seen in the device tab 2026-10-13 16:23); its letters and face
  lines were sliced under two 0.62 mm walls.
