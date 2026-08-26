# Handoff: build123d backend trial + skill update (2026-07-30)

## State

- build123d stack installed: `.venv/` at the vault root (uv, Python 3.12,
  build123d 0.11.1, trimesh, matplotlib); `scripts/render_stl.py` added
  for headless 4-view verification renders.
- Trial part built, verified, and exported in `projects/Build123d-trial/`
  (project_box.py, box.stl, lid.stl, project-box.3mf, images/, brief.md).
  Re-running project_box.py self-verifies all assertions.
- `skills/3d-model/SKILL.md` updated: build123d is the default backend,
  FreeCAD MCP is the escalation tier; comprehension-tested.
- Notes written: `knowledge/code-cad-vs-freecad.md` (decision),
  `knowledge/learnings/build123d-trial.md` (retrospective).

## Decisions already locked

- build123d is the default backend for /3d-model; FreeCAD MCP escalates
  per the predicates in the skill's "Backend choice" section (FCStd
  editing, GUI feature tree, FEM, parts library, live GUI viewing, or two
  unexplained kernel failures).
- On the code path the canonical CAD artifact is the parametric .py in
  `projects/<Name>/`; STL + 3MF exports and assertion checks live at the
  end of that file.
- Verification discipline unchanged from FreeCAD path: one feature at a
  time, render + inspect before the next, printability rules per
  [[printer-x2d]].
- Interactive user sign-off on the code path: OCP CAD Viewer standalone,
  opened via `scripts/cad-viewer.sh` (starts the server on port 3939 if
  down and launches a SwiftShader-flagged Chrome; plain desktop Chrome
  has no WebGL in this Chrome Remote Desktop session and shows a broken
  viewer). The server does not replay pushes to
  new clients: push AFTER the user's page is open, `SHOW=reset` first
  (frames the camera), `SHOW=1` for iterations. Live viewing is no
  longer a FreeCAD escalation reason. Verify the rendered viewer with
  the playwright MCP browser (chrome-devtools Chrome has no WebGL).

## Next

- Print projects/Build123d-trial/project-box-ironing.3mf (smooth-top
  ironing defaults baked in) to validate BOTH the 0.2 mm friction fit
  and the ironed top finish; record results in
  knowledge/learnings/build123d-trial.md. Settings decision:
  knowledge/smooth-surfaces-x2d.md.
