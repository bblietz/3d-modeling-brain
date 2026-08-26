---
tags: [tooling, decision, reference]
---

# Code-CAD (build123d) vs FreeCAD MCP

Decision (2026-07-30): **build123d is the default modeling backend** for
[[3d-model]] skill work; **FreeCAD via MCP is the escalation tier**. The
skill's "Backend choice" section holds the operative predicates.

## Why build123d as default

- Deterministic: the parametric .py file IS the model; re-running it
  reproduces identical geometry and re-checks every assertion. No stateful
  GUI session to drift, no topological-naming fragility on edits.
- Fully headless: plain Python in `.venv/`, no MCP server, no window that
  can be occluded. Failures are ordinary exceptions instead of RPC error
  dicts.
- Same B-rep kernel as FreeCAD (OCCT), so real fillets, chamfers, lofts,
  and STEP export are all available, unlike OpenSCAD.
- Edge selectors (`filter_by`, `group_by`, `sort_by`) replace fragile
  edge-index picking for fillets and chamfers.
- Visual verification preserved: `scripts/render_stl.py` renders shaded
  4-view PNGs with trimesh + matplotlib, no GPU or display needed.

## When FreeCAD still wins

- GUI-editable PartDesign feature tree for hand-tweaking, editing existing
  .FCStd files, parts library inserts.
- FEM (`run_fem_analysis`), TechDraw, assemblies.

## Alternatives considered

- **OpenSCAD (+BOSL2):** great agent ergonomics (text-first, headless,
  deterministic) but CSG-only, mesh-only exports, and weak arbitrary-edge
  fillets. build123d keeps the same ergonomics with a B-rep kernel, so it
  dominates for this vault. Not installed.
- **Status quo (FreeCAD MCP only):** works, but the agentic loop is the
  fragile part: stateful session, screenshot occlusion, edge-index
  fillets, verbose API with more first-try errors.

## Trial evidence

Benchmark build in `projects/Build123d-trial/` (details in
[[build123d-trial]]): 80 x 50 x 30 mm project box + friction-fit lid.
Six feature stages, every one passed on the first try; zero build123d API
errors over the whole build; watertight exports; 0.200 mm per-side lid
clearance measured from geometry, not constants.

## Stack

- `.venv/` at the vault root: uv-managed Python 3.12, build123d 0.11.1,
  trimesh, matplotlib.
- `scripts/render_stl.py`: headless 4-view STL renderer for agent-side
  verification.
- OCP CAD Viewer (`ocp_vscode`, in the venv): interactive browser viewer
  at http://localhost:3939/viewer for human iteration and sign-off. Open
  via `scripts/cad-viewer.sh` (desktop Chrome's WebGL is broken in the
  Chrome Remote Desktop session; the script launches a SwiftShader-flagged
  instance);
  model scripts push to it when run with `SHOW=reset` (first look,
  frames the camera) or `SHOW=1` (iterations, keeps the viewpoint).
  Push only while the page is open; the server does not replay to new
  clients. Replaces the FreeCAD GUI's live-viewing role on the default
  path.
- Skill: `skills/3d-model/SKILL.md` (backend choice, build loop, exports).

Related: [[printer-x2d]]
