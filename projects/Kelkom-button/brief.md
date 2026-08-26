---
tags: [project, replacement-part, snap-fit]
status: printed, awaiting fit test
---

# Kelkom intercom button

Reverse-engineered replacement for a Kelkom doorphone intercom pushbutton: a square two-tier white bezel with a center square through-hole for the lens/plunger, retained in the panel by two snap legs at diagonally opposite corners. Reference photos in `images/` (also copied to the FreeCAD model dir).

## Artifacts

- CAD, mesh, scripts: in this directory (FCStd, STL, 3MF; `scripts/rebuild.py` is the authoritative parametric source)
- History: commits `403cada` (v1), `b3e7ab0` (v2 corner legs) from the retired FreeCAD repo; full log preserved in [[git-history]]
- Model bounding box: 14.472 x 14.472 x 20.0 mm

## Measurements

User-measured with calipers (authoritative):

| Feature | Value |
|---|---|
| Layer 1 (outer cap) square | 13.6 mm |
| Layer 2 (inner body) square | 12.54 mm |
| Layer 1 / layer 2 thickness | 2.0 / 4.0 mm |
| Leg width / length | 6.0 / 14.0 mm |
| Leg wall thickness | 1.3 mm |
| Leg placement | diagonally opposite corners, curved section with slight inner radius |

Estimated from photos, never verified against the real part: center hole (6.5 mm square, R0.8 corners), recess rim 1.1 mm and depth 1.2 mm at 45 degrees, 0.5 mm top chamfer, leg arc R6.0 outer / R4.7 inner, barb protrusion 1.0 mm, tip lead-in chamfers.

## Open items

- Measure: center hole size, recess depth and rim width, barb protrusion, inner-face distance between legs across the center, and the panel cutout size.
- Clarify the leg-length datum: 14 mm from the cap underside (as modeled, 20 mm overall) or total?
- Fit-test the printed part: snap engagement in the panel cutout, plunger clearance in the center hole, barb retention. Record results here and in the learnings note.
- If the body is tight in the cutout, reprint with slicer XY compensation (-0.1 to -0.2 mm), keep CAD at nominal.
- For any reprint: top face down, legs up; PETG preferred over PLA (layer lines cross the leg flex axis). With 1.3 mm legs, prefer the 0.4 mm nozzle (0.6 nozzle two-perimeter minimum is 1.24 mm, only 0.06 mm margin).

## Related

- [[kelkom-button]] learnings note
- [[printer-x2d]]
