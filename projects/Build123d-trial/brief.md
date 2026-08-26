---
tags: [project]
created: 2026-07-30
status: v3 fit validated (very snug); v4 adds fingernail scoops, reprint pending
tool: build123d 0.11.1
printer: Bambu Lab X2D
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
reprints. Details in [[build123d-trial]] learnings.

## Files

- `projects/Build123d-trial/project_box.py` - parametric source; running it
  rebuilds, re-checks, and re-exports everything
- `projects/Build123d-trial/box.stl`, `lid.stl` - each part in print
  orientation on Z=0
- `projects/Build123d-trial/project-box.3mf` - both parts side by side,
  10 mm gap, ready for Bambu Studio
- `projects/Build123d-trial/lid-ribs-scoops-ironing.3mf` - lid only (v4,
  crush ribs + fingernail scoops), X2D 0.6 nozzle 0.18 mm presets with
  smooth-top ironing baked in; the current reprint file
- `projects/Build123d-trial/lid-ribs-ironing.3mf` - lid v3 (ribs, no
  scoops); fit validated but too hard to open, superseded
- `projects/Build123d-trial/lid-ironing.3mf` - lid v2 (0.1 mm clearance,
  no ribs); superseded, printed loose
- `projects/Build123d-trial/images/final-box.png`, `final-lid.png`,
  `final-both.png` - 4-view renders

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
  above the 1.24 mm two-perimeter minimum for the 0.6 mm high-flow nozzle

## Print notes

- No supports needed in the given orientations
- Elephant-foot chamfer is on the box only; the lid's bottom face is the
  plate underside - if the first layer squishes, the plug fit is unaffected
  (plug is at the top of the print)
