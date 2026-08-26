# Lego Rocket Mk3 - Build Instructions

Round-body redesign of the Mk2 multi-stage rocket kit: 22 pieces, 10 unique
parts, 3 colors. Round Ø34 (R4) and Ø15.8 (R2) modules replace the Mk2 square
bodies and octagonal approximations. Fully Lego-clutch compatible (stud pitch
8.0, stud Ø4.8 x 1.7, tube Ø6.5, +0.1 mm FDM compensation on cavities).

Assembled height: 125.6 mm on a 63.8 x 63.8 mm pad.

## Kit contents (22 pieces)

| Qty | Part | Color | Size (mm) |
|---|---|---|---|
| 1 | Launch Pad | Gray `#555555` | 63.8 x 63.8 x 12.9 |
| 4 | Engine Bell | Gray `#555555` | Ø7.2 x 7.7 |
| 1 | Tail (finned R4) | Red `#D32F2F` | 52.0 x 52.0 x 19.2 |
| 2 | Body (plain R4) | White `#F2F2F2` | Ø34.0 x 11.3 |
| 1 | Porthole (R4 + windows) | White `#F2F2F2` | Ø34.0 x 11.3 |
| 1 | Taper (Ø34 to Ø15.8 cone) | Red `#D32F2F` | Ø34.0 x 20.9 |
| 3 | Stage (R2) | White `#F2F2F2` | Ø15.8 x 11.3 |
| 1 | Nose Cone | Red `#D32F2F` | Ø15.8 x 28.0 |
| 4 | Booster Body (R2 tall) | White `#F2F2F2` | Ø15.8 x 20.9 |
| 4 | Booster Cone | Red `#D32F2F` | Ø15.8 x 13.2 |

## Printing

Open `lego-rocket-mk3.3mf` in Bambu Studio - it is a print-ready kit project
(22 arranged bed objects, per-object filament assignments).

- Printer: Bambu Lab X2D, 0.6 mm nozzle
- Process: 0.18 mm Balanced Quality @BBL X2D 0.6 nozzle
- Filaments (AMS): 1 = Bambu PLA Basic Red `#D32F2F`, 2 = White `#F2F2F2`,
  3 = Gray `#555555`
- Orientation: every part prints flat on the bed exactly as arranged - bricks
  cavity-down / studs-up, cones skirt-down / tips-up. No supports.
- Walls clear the 2-perimeter minimum: R4 1.9 mm, R2 1.4 mm, fins 1.6 mm.
- Enable elephant-foot compensation (~0.15 mm) in the slicer; it is not
  modeled in.

Per-part STLs (`pad.stl`, `bell.stl`, `tail.stl`, `body.stl`, `porthole.stl`,
`taper.stl`, `stage.stl`, `nose.stl`, `boosterbody.stl`, `boostercone.stl`)
are included as fallback, all origin-placed.

## Assembly order

World z is the height of the part's bottom face above the pad underside.

| Step | Part | Where | z |
|---|---|---|---|
| 1 | Launch Pad | on the table, platform up | 0 |
| 2-5 | Engine Bell x4 | hang into the platform well at (+-4,+-4), grip studs up | 5.2 |
| 6 | Tail | onto the platform's 8-stud ring; bells clip into its tubes; fins along the axes | 11.2 |
| 7 | Body A | onto the Tail | 20.8 |
| 8 | Porthole | onto Body A, windows facing +-Y | 30.4 |
| 9 | Body B | onto the Porthole | 40.0 |
| 10 | Taper | onto Body B | 49.6 |
| 11-13 | Stage x3 | stacked onto the Taper's 4 studs | 68.8 / 78.4 / 88.0 |
| 14 | Nose Cone | onto the top Stage (tip reaches 125.6) | 97.6 |
| 15-18 | Booster Body x4 | onto the pad corners at (+-24,+-24) | 3.2 |
| 19-22 | Booster Cone x4 | onto the Booster Bodies | 22.4 |

## Design data

- Source of truth: `DESIGN.md`. Parametric source: `scripts/01..12_*.py`
  (Part-workbench CSG; the FCStd files contain baked solids only).
- `lego_rocket_mk3.FCStd` - the 10 unique parts on a scatter grid.
- `lego_rocket_mk3_assembly.FCStd` - all 22 pieces at stack positions
  (`Step01_Pad` ... `Step22_BoosterCone4`).
- Documented deviations from DESIGN.md (geometric necessity, see script
  headers): Taper underside keeps the full Ø30.2 clutch band only over the
  stud zone (z 0..1.9) then chamfers to Ø22 - a full-depth Ø30.2 cavity would
  sever the cone's bottom skirt; R2 modules and skirts add four Ø4.9 x 2.0
  stud-relief notches at (+-4,+-4) - without them the Ø13 cavity wall would
  land on the stud crescents (studs reach r8.06 > wall r6.5) and round parts
  could never seat on 2x2 stud groups.
