---
title: Garmin 943xsv helm panel
type: project-brief
status: template built, awaiting print and test fit
created: 2026-09-08
tags: [boat, helm, garmin, starboard, router-template]
---

# Garmin GPSMAP 943xsv helm panel

Flat black King Starboard panel that replaces the hinged clear cover over the helm compartment directly behind the steering wheel. The 943xsv flush mounts through it. The old clear cover is the router pattern for the panel outline, so the only designed part is one 3D printed router template that locates the cutout and the four mounting holes.

## Locked decisions

- Panel replaces the hinged cover and is fixed in place. Hinges come off. Compartment access is by unmounting the unit.
- Material: black or charcoal King Starboard (HDPE). 3/8" (9.5 mm) unless the opening spans more than 450 mm, then 1/2" (12.7 mm).
- Mount style: Garmin flush mount, screws through the bezel edge into the HDPE. No printed bezel frame.
- Nothing else on the panel. One cutout only.
- Panel outline and perimeter fastening are copied from the old clear cover with a bearing bit. Not designed here.
- Exposure: under a hardtop. Stainless perimeter hardware.
- Compartment depth exceeds 110 mm everywhere, so the cutout position is free.
- Cutting: table saw or track saw for the perimeter, jigsaw rough cut inside the window, router with a bearing-guided flush-trim or pattern bit against the printed template.

## Garmin data (from Garmin install manual and 1:1 template, see [[#Sources]])

| Item | Value |
|---|---|
| Unit outside, bezel | 233.0 x 162.3 x 75.8 mm |
| Flush cutout | 222.4 x 139.0 mm labeled; drawn line 222.7 x 139.15 on center, 222.0 x 138.4 inside the 0.7 mm stroke |
| Mounting holes | four, on a 190.9 x 150.5 mm rectangle, NOT centered on the cutout: the pattern sits 1.24 mm toward the unit's bottom, so the top holes are 4.5 mm above the cutout edge and the bottom holes 7.0 mm below it (measured from the template vectors 2026-09-09) |
| Nut plate pin holes | 3 mm, 10.0 mm inboard of each screw hole in the same rows (171.1 x 150.5 mm pattern), only for the nut plate option |
| Screw pilot in plastic or wood | 2.3 mm |
| Bezel overlap past the cutout, as drawn with trim caps | 5.6 mm each side, 12.4 mm top, 14.9 mm bottom (bezel is centered on the hole pattern, not the cutout) |
| Cutout corners as drawn | 3.7 mm radius; the template calls for a 7.4 mm (5/16 in) relief drill, the manual says 8 mm |
| Rear clearance | 75.8 mm housing plus 33.2 mm cables, about 110 mm |
| Gasket | foam gasket on the back of the bezel, supplied |
| Flush kit | in the box; spare is Garmin 010-12991-01 |

## Panel

- Outline: rout from the old cover. Roundover the outside edges to taste.
- Cutout: 222.4 x 139.0 mm, centered left to right on the outline. Vertical position: centered unless the wheel rim blocks the lower screen from the seat, then shifted up. Brian decides at layout with the unit held in place.
- Corner radius left by the router equals the bit radius. Garmin's drawn cutout corners are 3.7 mm radius, so a 1/4" (6.35 mm) bit leaves 3.2 mm corners that need no squaring. A 5/16" bit would be 0.3 mm proud in the corners; avoid it.
- The cutout is not symmetric top to bottom because the screw holes sit 1.24 mm toward the unit's bottom. Lay out with the unit's top up and the template's TOP mark up.
- Mounting holes: 2.3 mm pilots drilled through the template guides, then the Garmin flat-head screws go straight into the HDPE. If the screws strip or feel soft in 3/8" stock, switch to Garmin's nut-plate option (3.5 mm clearance holes and M3 nut plates behind).

## Printed router template

- One part, PLA, 0.6 high-flow nozzle, 3 perimeters, 30 percent infill, textured PEI at 65 C.
- Window: exactly 222.4 x 139.0 mm, sharp corners. No offset, because the bearing rides on the template edge.
- Frame: 15 mm on the sides, 25 mm top and bottom, so the outside is 252.4 x 189.0 mm. Fits the 256 x 256 bed with the long edge on X.
- Thickness 12 mm, so a bearing up to about 10 mm tall rides fully on the template.
- Four drill guides for the mounting holes on the 190.9 x 150.5 mm pattern, shifted 1.24 mm toward the unit's bottom exactly as Garmin draws it (4.5 mm above the window at the top, 7.0 mm below it at the bottom). Modeled 2.8 mm so they print about 2.5 mm and clear a 2.3 to 2.4 mm bit. Each has a 6 mm counterbore 6 mm deep from the top face, so the guide is 6 mm long and a standard jobber bit reaches through the panel. A 7 mm counterbore would leave only 1.0 mm to the window at the top row.
- Registration: V notches on the outside edges at the four centerline points, to line up with centerlines drawn on the panel.
- Fixing: double-sided tape plus edge clamps. Two optional 4 mm screw holes on the vertical centerline, 6 mm outside the top and bottom window edges, land under the bezel overlap if screws are preferred.
- 0.6 mm chamfer on the bed-side window edge so elephant foot cannot narrow the window.
- TOP is debossed 0.8 mm into the counterbored face. The template is symmetric left to right only, so it still works on the front face with a top-bearing pattern bit or on the back face with a bottom-bearing flush-trim bit, as long as TOP points to the unit's top. Drill the pilots from the counterbored face.

## Process

1. Print the template. Measure the window with calipers. Expected 222.4 x 139.0 mm within 0.3 mm. Adjust slicer XY compensation if outside that, never rescale.
2. Rout the panel blank from the old cover. Roundover the outside edges.
3. Draw the cutout centerlines on the panel. Register the template notches on them with TOP toward the unit's top, fix it with tape and clamps.
4. Drill the four 2.3 mm pilots through the guides.
5. Drill an 8 mm relief hole inside each window corner, rough cut the window with a jigsaw leaving about 2 mm.
6. Rout the window flush to the template.
7. Test fit the 943xsv without screws. Bezel must sit flat on all four sides with the gasket compressed and the four bezel screw holes over the pilots.
8. Mount the panel, mount the unit, fit the trim caps.

Rout a scrap of the same stock first if any scrap is available.

## Deliverables (this folder)

- `brief.md` (this file).
- `router-template.py` (build123d source, self-checking), `router-template.stl`, `router-template.3mf`, `images/router-template-4view.png`.
- Retrospective in `knowledge/learnings/garmin-943-helm-panel.md` after the install.

## Open inputs from Brian

- Vertical placement of the cutout, decided at layout.
- Whether to add 3 mm pin guides for the nut plate option. Not in the template; add only if the wood screws fail.

## Sources

- Garmin install instructions, GPSMAP 7x3/9x3/12x3/16x3: https://www8.garmin.com/manuals/webhelp/GUID-BF2FF273-008A-482A-A96F-362ADA8996BA/EN-US/GPSMAP_7x3_9x3_12x3_16x3_Install_EN-US.pdf
- Garmin 9x3 flush mount template, 1:1: https://static.garmin.com/pumac/GPSMAP_9x3_flush_template.pdf
- Amped Up Marine KB article (hosts the same Garmin PDF, 190-02761-05_0D, July 2022, checked 2026-09-09): https://ampedupmarine.zohodesk.com/portal/en/kb/articles/garmin-gpsmap-9x3-mounting-template
- Note: the Garmin FAQ page lists "190.9 x 150.5 x 139.0 mm" as a cutout size. That is the hole pitch and cutout height run together, not a cutout. The template governs.

## Build results, 2026-09-09

Built with build123d from `router-template.py`. Every run re-checks the geometry: bounding box 252.4 x 189.0 x 12.0 mm, one solid, window probes prove the opening is 222.4 x 139.0 within 0.05 mm, all four guides clear, counterbores open, notches 2 mm deep, watertight STL, 3MF mesh matches the STL.

| Item | Value |
|---|---|
| Outside | 252.4 x 189.0 x 12.0 mm |
| Window | 222.4 x 139.0 mm, sharp corners, 0.6 mm chamfer on the bed side |
| Guides | 2.8 mm modeled, 6 x 6 mm counterbore, rows at +74.0 and -76.5 mm from the window center, wall to window edge 1.51 mm at the top row |
| TOP mark | 8 mm letters debossed 0.8 mm in the top band at x = 40 |
| Fixing holes | 4.0 mm at (0, +75.5) and (0, -75.5) |
| Notches | 90 degree V, 2 mm deep, at the four outer edge midpoints |
| Volume | 200 cm3 |

Print settings, 0.6 high-flow nozzle, Bambu PLA Basic, textured PEI at 65 C, brim off (the part leaves only 1.8 mm to the bed edge on X, so a brim would not fit). Center the part on the plate after import. Counterbored face up. Times from a real CLI slice with grafted Studio settings:

| Preset | Time | Filament |
|---|---|---|
| 0.18mm Balanced Quality, ironing off | 1 h 37 min (rev A slice) | 93 g |
| 0.30mm Standard | see slice log (rev B re-slice) | n/a |

Either works. Layer height does not change the window accuracy, so 0.30mm Standard is the sensible choice.

Slicer note for future sessions: `bambu-studio --arrange 1` placed this 252 mm part off the plate at y = -145.7, and the slice failed with "no object fully inside the print volume". Rewriting the build item transform to 128, 128, 0 in `3D/3dmodel.model` before `graft_slice.py` fixed it.

Revision B, 2026-09-09: checked against the template hosted by Amped Up Marine (Garmin's own 190-02761-05_0D PDF, unchanged). Found that the hole pattern is offset 1.24 mm toward the unit's bottom; revision A had it centered, which put every guide 1.24 mm too high. Guides moved, counterbore reduced to 6 mm, TOP deboss added. The check() function now also asserts that a pin at the old centered position hits material.

Next: print, measure the window with calipers, test the drill guides, rout the panel from the old cover, rough cut and rout the window, test fit the unit, install. Then the retrospective.

## Dimensions in inches

Decimal inches from the mm values, fractions rounded to the nearest 1/64. The mm values govern; Garmin's own template labels the cutout 8 3/4 x 5 1/2, but 139.0 mm is 5.472 in, so the 5 1/2 label is rounded by about 0.7 mm.

| Item | mm | Decimal in | Nearest fraction |
|---|---|---|---|
| Unit outside, bezel | 233.0 x 162.3 x 75.8 | 9.173 x 6.390 x 2.984 | 9 11/64 x 6 25/64 x 2 63/64 |
| Flush cutout | 222.4 x 139.0 | 8.756 x 5.472 | 8 3/4 x 5 15/32 |
| Mounting hole pattern | 190.9 x 150.5 | 7.516 x 5.925 | 7 33/64 x 5 59/64 |
| Hole offset from cutout edge, top row | 4.51 | 0.178 | 11/64 |
| Hole offset from cutout edge, bottom row | 6.99 | 0.275 | 9/32 |
| Hole pattern shift toward the unit's bottom | 1.24 | 0.049 | 3/64 |
| Hole offset from cutout edge, sides | 15.75 | 0.620 | 5/8 |
| Bezel overlap, each side | 5.6 | 0.220 | 7/32 |
| Bezel overlap, top | 12.4 | 0.488 | 31/64 |
| Bezel overlap, bottom | 14.9 | 0.587 | 19/32 |
| Cutout corner radius as drawn | 3.7 | 0.146 | 9/64 |
| Rear clearance, housing plus cables | 109.0 | 4.291 | 4 19/64 |
| Pilot drill | 2.3 | 0.091 | 3/32 |
| Corner relief drill, template label | 7.4 | 0.291 | 19/64 |
| Template outside | 252.4 x 189.0 x 12.0 | 9.937 x 7.441 x 0.472 | 9 15/16 x 7 7/16 x 15/32 |
| Template frame, sides | 15.0 | 0.591 | 19/32 |
| Template frame, top and bottom | 25.0 | 0.984 | 63/64 |
| Drill guide as printed | 2.5 | 0.098 | 3/32 |
| Guide counterbore, dia x depth | 6.0 x 6.0 | 0.236 x 0.236 | 15/64 x 15/64 |
| Fixing holes, dia | 4.0 | 0.157 | 5/32 |
| Fixing holes, from center | 75.5 | 2.972 | 2 31/32 |
| V notch, deep x wide | 2.0 x 4.0 | 0.079 x 0.157 | 5/64 x 5/32 |
| Corner radius from a 1/4 in bit | 3.2 | 0.126 | 1/8 |
| Jigsaw allowance | 2.0 | 0.079 | 5/64 |
| Panel span for 1/2 in stock | 450 | 17.717 | 17 23/32 |
