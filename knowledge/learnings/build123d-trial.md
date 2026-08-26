---
tags: [learnings, build123d, tooling]
---

# Build123d trial (project box + friction-fit lid)

2026-07-30. Benchmark build to qualify build123d as the default backend
for [[3d-model]] work. Outcome: qualified; decision recorded in
[[code-cad-vs-freecad]].

## What worked

- 6 of 6 feature stages (base, cavity, foot chamfer, lid plate, plug,
  lead-in chamfer) passed on the first try; zero build123d API errors in
  the entire build.
- Edge-selector fillets and chamfers, the FreeCAD pain point, were clean:
  `edges().filter_by(Axis.Z)` for corner fillets,
  `edges().group_by(Axis.Z)[0]` / `[-1]` for full bottom/top loops.
- Self-verifying source: assertions measured the lid clearance at
  0.200 mm per side from geometry probes, confirmed watertight STLs via
  trimesh, checked walls and overhangs. Re-running the file reproduces
  identical numbers.
- Headless render loop (`scripts/render_stl.py` + viewing the PNG)
  replaced the FreeCAD screenshot loop one for one.

## What failed, and fixes (both measurement bugs, not modeling bugs)

- Cavity-measurement probe slab poked past the rounded outer corners, so
  four slivers survived the boolean and inflated the measured bbox. Fix:
  measure the largest resulting solid only.
- Strict 45-degree overhang assert flagged 152 facets on the conical
  chamfer bands at rounded corners: the exact B-rep angle is 45.0 but STL
  facet normals tilt up to ~0.9 degrees past it. Fix: allow ~2 degrees of
  mesh margin, or check B-rep face angles where exactness matters.
- Side note: trimesh cannot load 3MF without networkx; verify 3MFs by
  parsing `3D/3dmodel.model` inside the zip.
- OCP CAD Viewer gotchas (root-caused with a live browser): the
  standalone server does not replay a past `show()` to newly connected
  clients, so a page opened after the push shows only demo content. Push
  after the page is open, and use `reset_camera=Camera.RESET` on the
  first push or the kept camera may frame nothing recognizable. Browser
  support: in this Chrome Remote Desktop session (virtual display, no
  GPU GL) plain Chrome cannot create a WebGL context at all (llvmpipe,
  "BindToCurrentSequence failed") - this hit the chrome-devtools MCP
  browser AND the user's desktop Chrome, which showed a half-initialized
  viewer UI. Working flag set (2026-08-02): `--use-gl=angle
  --use-angle=vulkan --ignore-gpu-blocklist` routes WebGL to the RTX
  3060 through NVIDIA Vulkan, which works even on the CRD virtual
  display where GLX is software-only. Do NOT add
  `--enable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan` - that
  combination kills context creation entirely. The earlier SwiftShader
  fallback (`--enable-unsafe-swiftshader --use-angle=swiftshader-webgl`)
  also worked but rendered on the CPU and was extremely slow (context
  losses, ReadPixels stalls in the console logs). `scripts/cad-viewer.sh`
  launches a separate-profile Chrome with the Vulkan flags (and starts
  the viewer server if down); the playwright MCP browser doubles as the
  agent's eyes on the rendered viewer. Agent-side geometry checks stay
  on `scripts/render_stl.py` PNGs.

## Measured results

- Box 80.000 x 50.000 x 30.000 mm, cavity 75.200 x 45.200 mm; lid
  80.000 x 50.000 x 5.000 mm, plug 74.800 x 44.800 mm; clearance
  0.200 mm per side in X and Y; walls >= 2.4 mm everywhere (0.6 high-flow
  nozzle minimum is 1.24 mm); no overhang beyond 45 degrees + 2-degree
  mesh margin; both STLs watertight; one solid per part.
## Print result (2026-07-31)

- Printed project-box-ironing.3mf (0.18 mm, PLA, 0.6 high-flow nozzle).
- Fit FAILED as a friction fit: at 0.2 mm clearance per side the lid
  seats but has no friction; it has slight play and can slide around.
  The [[printer-x2d]] "0.2 snug" rule does not hold for a full-perimeter
  vertical plug fit; the plug engages only 1.2 mm of straight wall
  (2.0 mm plug minus 0.8 mm lead-in), so there is no compliance to grab.
- Iteration v2: PLUG_CLEAR 0.2 -> 0.1 (plug 75.0 x 45.0). Printed
  better but still a tiny amount of movement; not a friction fit.
- Caliper calibration on the v2 print (width direction): cavity 44.98 vs
  45.2 designed (-0.22), plug 44.67 vs 45.0 designed (-0.33). Net: the
  as-printed gap runs ~0.055 mm per side LOOSER than designed, so a
  plain-clearance friction fit would need ~0.05 mm per side of designed
  interference - jam territory for a rigid full-perimeter fit.
  Measurement technique matters: inside-jaw pressure at mid-span of the
  long walls bowed them out and first read 45.8 (+0.6!); remeasuring
  near the stiff end walls gave the credible 44.98.
- Iteration v3 (current): crush ribs instead of tighter clearance. Plug
  body relaxed to 0.15 mm clearance per side; 8 ribs (2 per side, R1
  half-embedded cylinders, 0.35 mm proud, 0.5 mm top lead-in) overlap
  the cavity 0.2 mm per side by design, predicted ~0.145 mm actual
  crush after process offsets. Reprint file lid-ribs-ironing.3mf; box
  still unchanged.
- v3 print result: crush ribs WORK. The lid fits very snug with no
  movement; ribs at 0.2 mm design overlap per side (~0.145 predicted
  actual crush) grip firmly on the X2D in PLA.
- New learning from v3: design for removal. A snug lid that is flush
  with the box and has a flat top is too hard to open barehanded (needed
  an improvised handle); any friction-fit lid needs an opening feature
  (fingernail scoop, lip, notch, or handle) designed in from the start.
- Iteration v4 (current): fingernail scoops, ribs kept at 0.35. Two
  45-degree coves cut into the plug-side plate face at the short ends
  (25 mm wide, 1.5 mm gap at the edge tapering to zero while still over
  the box rim, 1.5 mm plate left under the cove). A nail slips between
  lid and rim and peels one end up, which beats the ribs' static
  friction far more easily than a flat pull. Prints without support.
  Reprint file lid-ribs-scoops-ironing.3mf. Record the v4 result here
  after printing.
- v4 correction, caught in user review before printing: the first cut
  went into the print-orientation bed face, which is the box TOP after
  the installation flip - cosmetic dips, no nail gap. Learning: this lid
  FLIPS to install, so every functional face must be mapped into the
  in-use orientation before cutting; removal features belong in the
  in-use mating face (here the plug-side plate face). Verified the fix
  in the OCP viewer with an assembled "lid installed on box" object,
  which makes orientation mistakes visually obvious - do that for any
  flipped part from the start.

## Files and settings

- `projects/Build123d-trial/project_box.py` (canonical parametric
  source), `box.stl`, `lid.stl`, `project-box.3mf` (both parts, 10 mm
  gap), `images/final-*.png`, `brief.md`.
- Print orientation: box floor on bed, lid plate on bed with plug up; no
  supports needed.

Related: [[printer-x2d]]
