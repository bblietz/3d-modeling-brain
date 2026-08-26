---
tags: [reference, lego, design-rules]
---

# Lego-compatible geometry (locked)

Constants proven across the lego-rocket Mk1 and Mk2 kits. Treat as the default for any future Lego-compatible part; change only with print-fit evidence.

| Parameter | Value |
|---|---|
| Stud pitch | 8.0 mm |
| 2x2 footprint | 15.8 x 15.8 mm |
| 4x4 footprint | 31.8 x 31.8 mm |
| 8x8 plate footprint | 63.8 x 63.8 mm |
| Brick height / plate height | 9.6 / 3.2 mm |
| Stud | 4.8 mm dia x 1.7 mm tall; positions +-4 (2x2), +-12 and +-4 (4x4) |
| Internal tube | 6.5 mm dia, solid (not hollow); positions -8, 0, +8 grid |
| Cavity 2x2 | 12.9 mm sq x 8.4 deep (spec 12.8 plus 0.1 FDM compensation) |
| Cavity 4x4 | 28.9 mm sq x 8.4 deep |
| Shallow grip cavity (plates, skirts) | 2.0 mm deep |
| Wall / roof thickness | 1.45 / 1.2 mm |

## Tolerances and fit

- +0.1 mm FDM compensation on every underside cavity dimension.
- Elephant-foot compensation about 0.15 mm in the slicer, deliberately not modeled: underside cavities are the fit surfaces and a squished first layer makes them tight.
- Octagonal bricks: 4.0 mm outer corner chamfer, 3.0 mm cavity chamfer, keeps at least 1.34 mm diagonal wall and full clutch.
- Adjacent-part clearance (fins rising past the brick above): 0.15 mm.
- Fit remediation: too tight, sand stud tops or scale studs down 1 percent; too loose, reprint at 100.5 percent XY.

## Print and color

- Studs up, flat on bed, no supports; 0.18 mm layers, X2D 0.6 nozzle, Bambu PLA Basic.
- Kit filament colors: #D32F2F red, #F2F2F2 white, #555555 gray. Caution: the FreeCAD viewport colors diverged from these (#D91A1A, #EBEBEB, #59595E); keep one source of truth and derive the other.

## Round modules (Mk3, unproven until fit-tested)

- R4 round brick: outer Ø34.0 x 9.6, NOT Ø31.8: a round cavity must swallow the outer stud ring (radius 15.05), and Ø31.8 would leave a 0.75 mm wall. Cavity Ø30.2 x 8.4, nine Ø6.5 tubes, roof 1.2, twelve studs (4x4 grid minus corners; corner studs cannot exist on round parts).
- R2 round brick: outer Ø15.8, cavity Ø13.0, the Ø6.5 center tube is the clutch (pinched between the 4 studs), plus four Ø4.9 x 2.0 stud-relief notches at (+-4,+-4) because studs reach radius 8.06, outside the part's own 7.9.
- Round parts only stack on stud fields without corner studs; the Mk3 pad platform ring keeps 8 studs.
- Round cavities in tapered parts: keep the full-diameter clutch band only for the bottom ~2 mm, then chamfer inward at 45 degrees; a full-depth wide cavity breaks through sloped walls.

## Related

- [[lego-3d-test]], [[printer-x2d]]
