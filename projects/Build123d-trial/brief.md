---
tags: [project]
created: 2026-07-30
updated: 2026-09-10
status: v3 fit validated (very snug); v4 adds fingernail scoops, never printed
tool: build123d 0.11.1
printer: Bambu Lab X2D
nozzle: 0.6 mm high-flow (NOT the resident nozzle - see Before printing)
material: PLA, single color
---

# Build123d trial: parametric project box + friction-fit lid

Benchmark of the code-CAD workflow (build123d instead of FreeCAD MCP). One
parametric source file builds both parts, self-verifies with assertions, and
exports STL + 3MF. Printer rules per [[printer-x2d]].

## Part spec

**Box** (print orientation: floor on bed, open top up)

- Outer 80 x 50 x 30 mm, wall 2.4 mm, floor 2.4 mm
- Vertical corner fillets R6 outside, R3.6 inside the cavity
- 0.6 mm chamfer on the bottom outer edge (elephant-foot compensation)
- Cavity 75.2 x 45.2 mm, 27.6 mm deep

**Lid** (print orientation: plate on bed, plug up; flip to install)

- Plate 80 x 50 x 3 mm, R6 corner fillets
- Plug 74.9 x 44.9 x 2 mm, R3.45 corner fillets
- 0.8 mm 45-degree lead-in chamfer around the plug's free edge
- 8 crush ribs (2 per side): R1 half-embedded vertical cylinders standing
  0.35 mm proud of the plug face, 0.5 mm lead-in chamfer on top
- 2 fingernail scoops (v4): 45-degree coves in the plug-side plate face
  at the short ends (the in-use underside once the lid is flipped onto
  the box), 25 mm wide, 1.5 mm nail gap at the edge tapering to zero over
  the box rim; peel one end up to open (v3 printed too hard to open flush)

**Fit** (v3, crush ribs): plug body at a free 0.15 mm clearance per side;
the ribs overlap the cavity by 0.2 mm per side by design and crush to fit.
Calipers on the v2 print: cavity prints ~0.22 mm under design, plug
~0.33 mm under, so plain clearance came out ~0.055 mm per side looser than
designed (v1 at 0.2 and v2 at 0.1 both had play). Predicted actual crush
~0.145 mm per rib. Box unchanged across all versions; only the lid
reprints. Details in [[build123d-trial]] learnings, recipe in
[[friction-fits-x2d]].

**The fit numbers are one calibration, not constants.** `PLUG_CLEAR` and
`RIB_PROUD` were validated on 0.6 high-flow, the classic wall generator,
PLA Basic, the spool loaded 2026-07-31. Change the nozzle, the wall
generator or the filament brand and they need re-validating: a
coupon-proven +0.02 mm interference went smash-tight after a filament
manufacturer change on another project.

## Files

- `projects/Build123d-trial/project_box.py` - parametric source; running it
  rebuilds, re-checks, and re-exports everything
- `projects/Build123d-trial/box.stl`, `lid.stl` - each part in print
  orientation on Z=0
- `projects/Build123d-trial/project-box.3mf` - geometry only, both parts
  side by side with a 10 mm gap. No print profile; not the file to print.
- `projects/Build123d-trial/pipeline/make_print_3mf.py` - builds the
  print-ready file from the STLs plus the settings template
- `projects/Build123d-trial/pipeline/x2d-pla-0.6-settings.json` - the
  `project_settings.config` Bambu Studio 02.08.02.61 itself wrote for this
  project, kept as text so it is diffable. Patched, not replaced, at build
  time. Deliberately NOT produced by `scripts/flatten_presets.py`, which
  still reads the stale 02.07.00.08 preset bundle and never merges the
  machine preset's `include` gcode.
- `projects/Build123d-trial/project-box-print.3mf` - **the current print
  file**: both parts, X2D 0.6 nozzle 0.18 mm presets, Textured PEI Plate
  at 65 C, PLA smooth-top ironing package, Manual filament map
- `projects/Build123d-trial/images/final-box.png`, `final-lid.png`,
  `final-both.png` - 4-view renders

Superseded, kept as history - do not print any of these:

- `project-box-ironing.3mf` - box only (the lid was deleted from the plate
  on 2026-09-10), textured plate at 55 C, and its filament diff slot is
  empty so the GUI resets the plate temp on open
- `lid-ribs-scoops-ironing.3mf` - lid only, v4; was the reprint file before
  `project-box-print.3mf` existed. Same 55 C bed issue.
- `lid-ribs-ironing.3mf` - lid v3 (ribs, no scoops); fit validated but too
  hard to open
- `lid-ironing.3mf` - lid v2 (0.1 mm clearance, no ribs); printed loose
- `result.json` - a Bambu Studio CLI artifact. The CLI drops one in its
  output directory on every export; it says nothing about this project.

## Verification results (assertions in project_box.py, all passing)

- Box bbox 80.000 x 50.000 x 30.000 mm on Z=0; lid bbox 80.000 x 50.000 x
  5.000 mm on Z=0
- Measured cavity 75.200 x 45.200 mm; plug body 74.900 x 44.900 mm; rib
  envelope 75.600 x 45.600 mm; body clearance 0.150 mm per side and rib
  interference 0.200 mm per side in X and Y (measured from geometry cross
  sections, not from the constants)
- Scoop probes confirm each cove removes exactly the intended triangle
  of plate material (1.5 mm of plate left under the cove, over the
  1.24 mm minimum)
- Exactly one solid per part; box volume 25521.7 mm^3, lid 18490.3 mm^3
- Both STLs watertight and winding-consistent (trimesh)
- No overhang steeper than 45 degrees in print orientation (mesh normal
  check with a documented 2-degree tessellation margin; the only 45-degree
  faces are the two intentional chamfers)
- Min wall 2.4 mm everywhere (straight walls, corner walls, floor, plate),
  above the 1.24 mm two-perimeter minimum for the 0.6 mm high-flow nozzle.
  That floor is a hard slicer limit, not a quality preference: the stock
  X2D quality presets run the classic wall generator with thin-wall
  detection off, so anything thinner is silently not printed at all.
- **The fit re-measured on the exported mesh**, because the tessellation is
  what actually gets sliced: cavity 75.200 x 45.200 mm, plug body 74.900 x
  44.900 mm, rib envelope 75.599 x 45.599 mm. Clearance 0.150 mm per side
  and rib interference 0.200 mm per side, i.e. faceting the R3.45 / R3.60
  corner fillets costs the rib envelope 0.001 mm and the fit survives it.
- **The exported 3MF is parsed back** out of the zip (trimesh cannot read
  3MF without networkx): 2 build items pointing at real meshes, both
  bounding boxes correct, both on Z=0, 10 mm apart.

## Before printing

1. **Swap the nozzle.** This part is designed for the 0.6 high-flow. The
   resident nozzle has been 0.2 mm in both positions since 2026-08-23.
2. **Confirm what is mounted** with `scripts/x2d-status.py`, from the
   printer, not from memory.
3. **Select the 0.6 nozzle printer preset in Studio's Prepare tab BEFORE
   opening the project.** Studio silently re-profiles an imported project
   to the resident machine and re-slices it. No mismatch warning fires
   anywhere, and a 0.4-designed file opened as 0.6 has already cost one
   ruined print on another project.
4. **Open `project-box-print.3mf` in Studio and look at the plate.** A
   hand-patched 3MF has passed a CLI round trip and still rendered empty.
   CLI slicing is not an alternative check here: it only succeeds on
   Studio-saved projects and fails on CLI-composed ones with "No valid
   nozzle found".

## Print notes

- No supports needed in the given orientations
- Elephant-foot chamfer is on the box only; the lid's bottom face is the
  plate underside - if the first layer squishes, the plug fit is unaffected
  (plug is at the top of the print)
