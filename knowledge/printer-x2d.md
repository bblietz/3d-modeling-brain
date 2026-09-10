---
tags: [printer, hardware, reference]
---

# Bambu Lab X2D profile

## Machine

- Build volume: 256 x 256 x 260 mm with the main nozzle; 235.5 x 256 x 256 mm when a print uses both nozzles (dual-nozzle or multi-material).
- AMS 2 Pro feeds the main nozzle: max 4 colors per print. The second nozzle is dedicated to support material; it can act as a 5th color only where placement accuracy does not matter, never for precision or mating features.
- Chamber fan has a cool/heat mode switch on the printer (set to cool as of 2026-08-08). Cool vents the chamber and is correct for PLA and PETG, whose Bambu filament presets command `chamber_temperatures` 0; heat holds chamber warmth and is only for high-temp materials (ABS/ASA/PC/PA). A heated chamber with PETG invites heat creep and stringing.

## Nozzle inventory

| Nozzle | Line width (approx) | Min wall (2 perimeters) | Use for |
|---|---|---|---|
| 0.2 mm hardened steel (2 owned, arrived Aug 2026) | 0.22 mm | 0.44 mm | Hairline detail, tiny raised text; PETG capped at 2 mm3/s by Bambu's preset, so budget 3 to 4x the 0.4 print time |
| 0.4 mm hardened steel | 0.42 mm | 0.84 mm | Fine detail, small text, tight tolerances |
| 0.6 mm hardened steel | 0.62 mm | 1.24 mm | General purpose, abrasive filaments |
| 0.6 mm hardened steel high-flow ("speed nozzle") | 0.62 mm | 1.24 mm | Fast large prints; normally installed |

Hardened steel handles abrasive filaments (CF, GF, glow) but has slightly worse thermal conductivity than brass; no design impact at normal speeds.

Before printing fine-detail work, verify BOTH the physically installed nozzle AND Bambu Studio's Prepare-tab machine match the design's target nozzle (0.6 high-flow is the resident). If Studio's machine matches the installed nozzle but not the file, it silently adapts the imported project to that profile and re-slices - NO mismatch warning fires anywhere, and a 0.4-sliced design printed as 0.6 globally fattens every fine feature into illegible mush ([[sharks-nametag]] first test print, 2026-08-06). Same check applies at the filament-mapping screen: confirm the AMS slots actually hold the intended colors, not the previous project's load.

## Design rules

- CLI-composed project 3MFs: `bambu-studio` CLI exports default
  `curr_bed_type` to "Cool Plate" (35C bed). On the textured PEI plate
  that means PLA prints ~30C too cold and edges peel mid-print
  (Sharks-nametag 2026-08-07). Always set `curr_bed_type`
  "Textured PEI Plate" + `textured_plate_temp[_initial_layer]` 65C for
  PLA in the post-process step, with the temp keys listed in the
  FILAMENT diff slots (different_settings_to_system[1..3]); check the
  bed temp readout at print start ([[sharks-nametag]]).
- Multi-plate project 3MFs: Bambu Studio lays plates out in a TWO-COLUMN
  grid whose rows run in NEGATIVE Y, not in a single row along X. Plate p
  (0-indexed) sits at `((p % 2) * 307.2, -(p // 2) * 307.2)`, stride
  256 x 1.2. A single row is indistinguishable from this for the first two
  plates, which is why the earlier single-row note looked correct; with four
  plates it puts plates 3 and 4 off-grid, and they round trip cleanly while
  rendering EMPTY in the GUI and failing `--slice` with rc 206 "no object
  fully inside the print volume". Probed 2026-09-09 against three candidate
  layouts; see `projects/Garmin-943-helm-panel/make_multiplate.py`.
- Authoring plates: the CLI does not keep objects in input order, so map each
  object id by the source filename it carries in `model_settings.config`, not
  by document position. Mapping by position silently scatters parts onto the
  wrong plates.
- `bambu-studio --export-3mf` exits 243 and writes nothing when handed an
  absolute path while `--outputdir` is also set. Pass a bare filename.
- Walls: at least 2 perimeters wide (see table above). This is a hard
  floor, not a quality preference: Bambu's stock X2D quality presets
  (e.g. 0.12mm High Quality) use the CLASSIC wall generator with
  detect_thin_wall off, which silently prints NOTHING for any feature
  under 2 perimeters - no warning at slice time (Sharks-nametag test
  print 2026-08-07: all 0.17-0.65 mm ball line art absent). Raised line
  art on the 0.4 nozzle needs >= 0.9 mm; measure traced art layers
  numerically (erosion test) against this floor before the first print
  ([[sharks-nametag]]).
  Exception: with `wall_generator` arachne in the process preset, single
  variable-width beads print down to ~0.45 mm, so raised line art can go
  to ~0.6 mm on the 0.4 nozzle (Sharks-nametag v3.23, 2026-08-20; unvalidated
  until its PETG test print). List the key in `different_settings_to_system[0]`.
- Overhangs: flag anything past 45 degrees unsupported; prefer chamfers or reorientation over supports.
- Small holes shrink: add 0.1 to 0.2 mm to the diameter or plan to drill.
- Mating clearance: about 0.2 mm for a snug fit, 0.3 mm for a free fit.
  Measured 2026-07-31 ([[build123d-trial]], PLA, 0.6 high-flow nozzle):
  on a full-perimeter vertical plug-in-cavity fit, cavities print ~0.2 mm
  under design but plugs ~0.3 mm under, so the real gap comes out ~0.05 mm
  per side looser than designed; 0.2 and 0.1 mm per side both printed with
  play, and a designed-clearance friction fit would need slight designed
  interference. For friction fits use crush ribs instead: loose body
  clearance (~0.15 mm per side) plus ribs ~0.35 mm proud. Validated
  2026-07-31: ribs 0.35 mm proud (0.2 mm design overlap per side) grip
  very snug in PLA. Corollary: a snug flush lid is too hard to open
  barehanded, so always pair a friction fit with an opening feature
  (fingernail scoop, lip, or handle).
  Second data point (2026-07-31, [[clawd-mascot]] eye coupon, small parts):
  a 6.25 x 9.91 mm pocket printed -0.02 / -0.07 mm under nominal, and a
  ~6 x 10 mm inlay printed -0.06 mm in one axis but +0.08 mm in the other
  (first-layer flare on the bed side). Deviations are ASYMMETRIC per axis,
  so design press-fit inserts from a measured zero-fit basis (print one
  coupon, caliper pocket and insert, set basis = pocket_nom + pocket_dev -
  insert_dev per axis) and add 0.02-0.14 mm total interference on top;
  clearance-band guessing cannot find fits when the zero point sits
  outside the band. Validated: at the measured basis, 0.02 mm total
  interference per axis gave a print-confirmed "fits great" press fit
  (coupon v2, 1-dot eye).
- First layer: put a flat face on the bed; expect elephant-foot on precision bores at the bed.
- Layer lines are the weak direction: orient parts so load runs along layers, not across them.
- Thin flexing features (snap legs, clips) under about 1.5 mm: use the 0.4 mm nozzle, and print in PETG rather than PLA.
- Press/panel fits: tune with slicer XY compensation (-0.1 to -0.2 mm), never by rescaling the model.

## Related

- Modeling workflow: the `/3d-model` skill (FreeCAD via MCP, exports to `projects/<Name>/` in this vault).
- Controlling the printer from software: [[x2d-printer-control]]
- Ecosystem survey (skills, MCPs, LEGO data): [[lego-ai-ecosystem]]
- Per-project outcomes: [[lego-3d-test]], [[kelkom-button]]
