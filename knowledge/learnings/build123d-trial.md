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

## Back-applying six weeks of learnings (2026-09-10)

v4 was still unprinted, and the project files had drifted behind what the
rest of the vault had learned since 2026-07-31. What the audit found, and
what changed:

- **The recipe was trapped in this retrospective.** The crush-rib fit is
  general knowledge, not a fact about one box, and there was no turnkey
  note for it. Promoted to [[friction-fits-x2d]] following the
  `<topic>-x2d.md` pattern; this file stays as the history.
- **Fit constants were being read as constants.** `PLUG_CLEAR` and
  `RIB_PROUD` are one calibration - 0.6 high-flow, classic wall
  generator, PLA Basic, one spool. [[clawd-mascot]] had already shown a
  coupon-validated interference going smash-tight after a filament brand
  change. The provenance and the re-coupon triggers now sit in the source
  next to the numbers.
- **The nozzle assumption was stale and invisible.** The source declared
  "0.6 mm high-flow" in a docstring and hardcoded `MIN_WALL = 1.24`. Now a
  `NOZZLE` constant drives `MIN_WALL` off the floor table
  {0.2: 0.44, 0.4: 0.84, 0.6: 1.24}, and the pre-flight (confirm with
  `scripts/x2d-status.py`, pick the printer preset in Studio BEFORE
  opening) is written into the file and the brief.
- **The note about the nozzle was stale too, and nearly shipped as an
  instruction.** The memory note said 0.2 in both positions since
  2026-08-23, so the first pass wrote "swap back to the 0.6 high-flow"
  into the source, the brief and the handoff. Querying the printer on
  2026-09-10 showed 0.6 HH01 already mounted on the main nozzle. The
  vault's own rule - trust the printer readout, not the inventory - was
  followed one step too late, because `scripts/x2d-status.py` was failing
  on a truncated Studio config and the note got used as the fallback. A
  broken pre-flight check is worse than no check: it silently promotes a
  note to ground truth.
- **The min-wall rule changed meaning.** It was a quality preference in
  July. Since the Sharks prints it is a hard slicer floor: the stock X2D
  quality presets run the classic generator with thin-wall detection off,
  so under two perimeters prints *nothing*, silently.
- **Asserts measured the B-rep; the slicer eats the mesh.** Added a
  re-measure of cavity, plug body and rib envelope on the exported STL.
  Result: tessellating the R3.45 / R3.60 fillets costs the rib envelope
  0.001 mm (75.599 vs 75.600). The fit survives - now as a measured fact
  with an assert behind it, where before it was an assumption.
- **The 3MF was written and never checked.** Now parsed back out of the
  zip (build items, meshes, bounding boxes, Z=0, gap), since trimesh
  cannot read 3MF without networkx.
- **Print settings were hand-made and unreproducible.** Layer height and
  ironing existed nowhere in code; the ironing 3MFs were one-off GUI
  saves. Now `pipeline/make_print_3mf.py` builds the print file from the
  STLs plus a text settings template, per [[project-keep-tools-in-vault]].
- **Two live defects in the old print file.** `project-box-ironing.3mf`
  carried the textured plate at **55 C** (the flattened-preset value;
  Bambu stock PLA on textured PEI wants 65) and had an **empty filament
  diff slot**, so the GUI would silently reset the temperature on open.
  The Cool Plate / 35 C version of that same bug shredded a Sharks print
  on 2026-08-07. Both fixed in the new file.
- **`different_settings_to_system` is positional and scope-aware:**
  [0] process, [1..N] the N filaments, [N+1] machine. Bed temps are
  filament-scope. `scripts/apply_smooth_top.py` only ever writes slot 0,
  which is why the new pipeline handles the slots itself rather than
  calling it.
- **The flattener was avoided, not used.** `scripts/flatten_presets.py`
  still reads the stale 02.07.00.08 bundle and never merges the machine
  preset's `include` gcode. The settings template is instead the
  `project_settings.config` Studio 02.08.02.61 wrote for this project,
  kept as JSON so it is diffable.

Still open: **v4 has never been printed.** v3 (ribs, no scoops) is the
last fit-validated print. The scoops are modelled and asserted but their
nail gap is unproven, and the fit numbers were calibrated on a nozzle that
is not currently installed.

## Files and settings

- `projects/Build123d-trial/project_box.py` (canonical parametric
  source), `box.stl`, `lid.stl`, `project-box.3mf` (geometry only, both
  parts, 10 mm gap), `images/final-*.png`, `brief.md`.
- `projects/Build123d-trial/pipeline/make_print_3mf.py` +
  `x2d-pla-0.6-settings.json` build `project-box-print.3mf`, the print
  file: X2D 0.6 nozzle 0.18 mm presets, Textured PEI Plate at 65 C, PLA
  smooth-top ironing package, Manual filament map.
- The `lid-*-ironing.3mf` files and `project-box-ironing.3mf` are
  superseded history, not print files. `result.json` is a Bambu Studio
  CLI artifact, dropped in the output directory on every export.
- Print orientation: box floor on bed, lid plate on bed with plug up; no
  supports needed.

Related: [[printer-x2d]], [[friction-fits-x2d]]
