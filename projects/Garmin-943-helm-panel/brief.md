---
title: Garmin 943xsv helm panel
type: project-brief
status: spec-approved, building template
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
| Flush cutout | 222.4 x 139.0 mm, sharp corners |
| Mounting holes | four, on a 190.9 x 150.5 mm rectangle centered on the cutout |
| Screw pilot in plastic or wood | 2.3 mm |
| Bezel overlap past the cutout | 5.3 mm each side, 11.65 mm top and bottom |
| Rear clearance | 75.8 mm housing plus 33.2 mm cables, about 110 mm |
| Gasket | foam gasket on the back of the bezel, supplied |
| Flush kit | in the box; spare is Garmin 010-12991-01 |

## Panel

- Outline: rout from the old cover. Roundover the outside edges to taste.
- Cutout: 222.4 x 139.0 mm, centered left to right on the outline. Vertical position: centered unless the wheel rim blocks the lower screen from the seat, then shifted up. Brian decides at layout with the unit held in place.
- Corner radius left by the router equals the bit radius. Use a 1/4" (6.35 mm) diameter bit so the corners are 3.2 mm radius. After the test fit, square the corners with a file only if the housing binds.
- Mounting holes: 2.3 mm pilots drilled through the template guides, then the Garmin flat-head screws go straight into the HDPE. If the screws strip or feel soft in 3/8" stock, switch to Garmin's nut-plate option (3.5 mm clearance holes and M3 nut plates behind).

## Printed router template

- One part, PLA, 0.6 high-flow nozzle, 3 perimeters, 30 percent infill, textured PEI at 65 C.
- Window: exactly 222.4 x 139.0 mm, sharp corners. No offset, because the bearing rides on the template edge.
- Frame: 15 mm on the sides, 25 mm top and bottom, so the outside is 252.4 x 189.0 mm. Fits the 256 x 256 bed with the long edge on X.
- Thickness 12 mm, so a bearing up to about 10 mm tall rides fully on the template.
- Four drill guides for the mounting holes: 2.5 mm through holes on the 190.9 x 150.5 mm pattern.
- Registration: V notches on the outside edges at the four centerline points, to line up with centerlines drawn on the panel.
- Fixing: double-sided tape plus edge clamps. Two optional 4 mm screw holes on the vertical centerline, 6 mm outside the top and bottom window edges, land under the bezel overlap if screws are preferred.
- 0.6 mm chamfer on the bed-side window edge so elephant foot cannot narrow the window.
- The template is symmetric about both centerlines, so it works on the front face with a top-bearing pattern bit or on the back face with a bottom-bearing flush-trim bit.

## Process

1. Print the template. Measure the window with calipers. Expected 222.4 x 139.0 mm within 0.3 mm. Adjust slicer XY compensation if outside that, never rescale.
2. Rout the panel blank from the old cover. Roundover the outside edges.
3. Draw the cutout centerlines on the panel. Register the template notches on them, fix it with tape and clamps.
4. Drill the four 2.3 mm pilots through the guides.
5. Drill an 8 mm relief hole inside each window corner, rough cut the window with a jigsaw leaving about 2 mm.
6. Rout the window flush to the template.
7. Test fit the 943xsv without screws. Bezel must sit flat on all four sides with the gasket compressed. Square corners with a file only if needed.
8. Mount the panel, mount the unit, fit the trim caps.

Rout a scrap of the same stock first if any scrap is available.

## Deliverables (this folder)

- `brief.md` (this file).
- `router-template.FCStd`, `router-template.stl`, `router-template.3mf`.
- Retrospective in `knowledge/learnings/garmin-943-helm-panel.md` after the install.

## Open inputs from Brian

- Vertical placement of the cutout, decided at layout. Nothing blocks the template build.

## Sources

- Garmin install instructions, GPSMAP 7x3/9x3/12x3/16x3: https://www8.garmin.com/manuals/webhelp/GUID-BF2FF273-008A-482A-A96F-362ADA8996BA/EN-US/GPSMAP_7x3_9x3_12x3_16x3_Install_EN-US.pdf
- Garmin 9x3 flush mount template, 1:1: https://static.garmin.com/pumac/GPSMAP_9x3_flush_template.pdf
- Note: the Garmin FAQ page lists "190.9 x 150.5 x 139.0 mm" as a cutout size. That is the hole pitch and cutout height run together, not a cutout. The template governs.
