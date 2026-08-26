# Lego Rocket Mk3 - round-body redesign

Mk2 architecture (22 pieces, 10 unique parts, 3 colors) with round cross-sections replacing the square 4x4 bodies and octagonal 2x2 approximations. Mk2 stays intact in `models/lego-rocket-mk2/`.

## Why these numbers (derivations)

- A round underside cavity must swallow the outer stud ring of the brick below. 4x4-grid outer studs (at +-12,+-4 and +-4,+-12) reach radius 15.05 mm, so the round cavity is Ø30.2 (2 x 15.05 = 30.1 spec, +0.1 FDM compensation). At the Lego 4x4 width Ø31.8 that leaves a 0.75 mm wall, below even the 0.4 nozzle minimum, so the round module outer diameter is Ø34.0 (wall 1.9 mm).
- Corner studs (+-12,+-12, radius 16.97, stud edge to 19.37) cannot coexist with any round Ø34 part above them: round tops carry 12 studs (4x4 grid minus the 4 corners), and the pad platform drops its 4 corner studs.
- Clutch works exactly like the square bricks: studs pinched between tubes (Ø6.5 solid, center gaps between studs are 6.51 tangent) and the cavity wall (outer stud edge 15.05 vs wall 15.1, 0.05 per side).
- Round 2x2: real-Lego geometry. Outer Ø15.8, cavity Ø13.0 (12.9 spec + 0.1), center tube Ø6.5 pinches the 4 studs from inside, wall touches them at 4 points. Wall 1.4 mm. Note: top studs at (+-4,+-4) overhang the Ø15.8 face by 0.16 mm on the diagonal; accepted (micro-lip, prints fine).

## Shared constants (from knowledge/lego-geometry.md in the 3d-modeling-brain vault)

Stud pitch 8.0; stud Ø4.8 x 1.7; tube Ø6.5 solid; brick height 9.6; plate 3.2; cavity depth 8.4; roof 1.2; shallow grip cavity 2.0 deep; +0.1 FDM compensation on cavity dimensions (already applied in numbers below).

## Round modules

**R4 (Ø34 round brick), height 9.6:** outer cylinder Ø34.0; underside cavity Ø30.2 x 8.4 deep; 9 tubes Ø6.5 at the (-8, 0, +8) grid, cavity roof to bottom; roof 1.2; top 12 studs at (+-12,+-4), (+-4,+-12), (+-4,+-4).

**R2 (Ø15.8 round brick), height 9.6 (or 19.2 for boosters):** outer cylinder Ø15.8; cavity Ø13.0 x 8.4; center tube Ø6.5; roof 1.2; top 4 studs at (+-4,+-4).

## Parts (10 unique, 22 pieces)

| # | Part | Qty | Color | Geometry |
|---|---|---|---|---|
| 1 | Pad | 1 | gray | As Mk2: 8x8 plate 63.8 x 63.8 x 3.2, raised 31.8 x 31.8 platform to z 11.2, 19 x 19 x 14 through-well. Outer stud field on the plate where grid coords in {+-4,+-12,+-20,+-28} and max(abs x, abs y) >= 20. Platform ring: ONLY 8 studs at (+-12,+-4) and (+-4,+-12) - corner studs dropped vs Mk2. |
| 2 | Bell | 4 | gray | As Mk2: cone r3.6 to r2.6 x 6.0 tall, exhaust recess Ø5.0 x 2.5 deep from bottom, grip stud Ø4.8 x 1.7 on top. |
| 3 | Tail | 1 | red | R4 body (12-stud top, cavity with 9 tubes) + 4 radial fins 90 degrees apart along +-X and +-Y: about 1.6 mm thick, swept-back triangular profile, root on the Ø34 wall, tip out to roughly r 26 at the base, base flat at local z 0, rising to about local z 19.2; any fin material above local z 9.6 must keep radial clearance >= 17.15 from the axis (0.15 mm to the Ø34 body stacked above). |
| 4 | Body | 2 | white | Plain R4. |
| 5 | Porthole | 1 | white | R4 + porthole windows: Ø8 horizontal cuts along the Y axis at local (x = -4, z = 4.8), cutting the WALL ONLY - two cut cylinders spanning roughly y 11.5 to 18 and y -18 to -11.5 (tubes reach only to abs(y) 11.25, so wall-only cuts clear all tubes). Do not cut through the interior. |
| 6 | Taper | 1 | red | Solid loft, circle Ø34 at local z 0 to circle Ø15.8 at z 19.2; R4 cavity (Ø30.2 x 8.4 + 9 tubes) cut into the underside; top face 4 studs at (+-4,+-4). |
| 7 | Stage | 3 | white | R2, height 9.6. |
| 8 | Nose | 1 | red | Round skirt Ø15.8 x 3.2 with shallow grip cavity Ø13.0 x 2.0, then cone r7.9 to r2.6 over 17.8, collar r2.6 x 2.0, mast r1.5 x 5.0, sphere tip r1.5 (tip apex about local z 28). |
| 9 | BoosterBody | 4 | white | R2 at height 19.2 (cavity Ø13.0 x 8.4 at the bottom, center tube, roof, 4 studs on top). |
| 10 | BoosterCone | 4 | red | Round skirt Ø15.8 x 3.2 with grip cavity Ø13.0 x 2.0, cone r7.9 to r2.0 over 10.0, sphere tip r2.0 (apex about local z 13.2). |

## Assembly placements (world z of part origin)

Pad 0; Bells at (+-4,+-4), z 5.2 (hanging into the well); Tail 11.2; Body A 20.8; Porthole 30.4; Body B 40.0; Taper 49.6; Stage x3 at 68.8 / 78.4 / 88.0; Nose 97.6 (tip about 125.6). Boosters at (+-24,+-24): bodies z 3.2 (on the plate studs), cones z 22.4.

## Colors (single source of truth - use for BOTH FreeCAD viewport and 3MF filament colors)

Red `#D32F2F` (Tail, Taper, Nose, BoosterCone), White `#F2F2F2` (Body, Porthole, Stage, BoosterBody), Gray `#555555` (Pad, Bell).

## As-built deviations (build of 2026-07-30, see script headers and BUILD-INSTRUCTIONS.md)

1. Taper cavity: a straight Ø30.2 x 8.4 cavity is impossible (the cone wall crosses r 15.1 at z about 4). As built: full Ø30.2 clutch band over z 0 to 1.9, 45 degree chamfer to Ø22 by z 6.0, Ø22 core to the 8.4 roof. Clutch unchanged.
2. R2 module: the "wall touches the studs at 4 points" claim above is geometrically impossible (studs at (+-4,+-4) reach r 8.06, outside the Ø15.8 part itself). As built: four Ø4.9 x 2.0 stud-relief notches at (+-4,+-4), real round-Lego style; the clutch is the Ø6.5 center-tube pinch alone.
3. Nose and booster tips: sphere caps are included within the stated apex heights (apexes land at exactly 28.0 and 13.2).

## Print

Every part flat on bed, studs up, no supports; cones skirt-down, tips up. 0.18 mm layers, X2D 0.6 nozzle, Bambu PLA Basic. Walls: R4 1.9 mm, R2 1.4 mm, fins 1.6 mm - all above the 1.24 mm two-perimeter minimum. Elephant-foot compensation about 0.15 mm in the slicer, not modeled.
