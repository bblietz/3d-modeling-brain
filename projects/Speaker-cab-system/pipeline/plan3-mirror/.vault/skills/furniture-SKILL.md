---
name: furniture
description: Use when the user asks to design furniture or a woodworking project (shelf, bookcase, table, cabinet, bench, desk, workbench), modify such a design, or produce a cut list, lumber list, or shop drawings from one. For 3D-printable parts, use the 3d-model skill instead.
---

# Design Furniture (cut list workflow)

Design furniture as a parametric assembly with ONE NAMED SOLID PER PART,
visually verifying each step via screenshots, then run a buildability
check and export a cut list + STEP. Forked from the 3d-model skill:
Phases 1-3 are the same discipline; Phases 4-5 are woodworking-specific
(no printability check, no STL/3MF deliverables). All modeling in mm;
the cut list also prints inches (nearest 1/16) for lumber shopping.

## Backend choice

Default to **build123d**. Escalate to **FreeCAD MCP** when at least one
holds:
- The task edits an existing .FCStd, or the user wants a GUI-editable
  feature tree to tweak afterwards.
- Dimensioned shop drawings are requested (TechDraw). TechDraw is
  untested in this vault: treat it as an experiment and verify the
  output page by eye before handing it over.
- A build123d operation failed twice on the same feature with no clear fix.

State the chosen backend and why in one line before building.

## Prerequisites (check before modeling)

Same environment as the 3d-model skill:

### build123d (default)

- Interpreter: `/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python`
  (Python 3.12 venv with build123d, trimesh, matplotlib; recreate with
  `uv venv .venv` then
  `uv pip install --python .venv/bin/python build123d trimesh matplotlib`
  from the vault root).
- Headless screenshots (run from the vault root):
  `.venv/bin/python scripts/render_stl.py <model.stl> <out.png> [elev,azim ...]`
  renders shaded iso/front/top/right views; view the PNG file after each
  render.
- Interactive viewer for the user (iteration + sign-off): OCP CAD Viewer,
  opened with `scripts/cad-viewer.sh`. All the warnings in the 3d-model
  skill apply verbatim: never just hand the user the URL (desktop Chrome
  here has no WebGL), push AFTER the user's page is open, re-push after
  any reload, use the playwright MCP browser (not chrome-devtools) when
  you need to see what the user sees. PNG renders remain the primary
  agent-side check.
- No GUI and no MCP tools needed for the modeling itself.

### FreeCAD MCP (escalation)

1. **FreeCAD running + RPC up:** run
   `/home/brian/ClaudeProjects/3d-modeling-brain/scripts/start-freecad-mcp.sh`
   (idempotent; exit 0 means ready).
2. **MCP tools available:** the `freecad` MCP server provides
   `execute_code`, `get_view`, etc. If not loaded in the session, fall
   back to direct XML-RPC from Bash on `http://127.0.0.1:9875` (see the
   3d-model skill for the snippet).
3. **Health doubt?** run
   `python3 /home/brian/ClaudeProjects/3d-modeling-brain/scripts/smoke-test.py`.

## Phase 1 - Brief

Ask ONLY load-bearing questions (batch them; don't interrogate):
- Overall dimensions and the space it must fit (alcove width, ceiling
  height, wall it stands against). Measured beats estimated; record
  provenance in the brief.
- Load and use: books vs display, seating weight, will it be moved often.
- Material preference and what stock/tools are actually available;
  joinery capability (pocket screws only? dados? just butt joints?).
- Which faces show (drives grain direction and material choice).
State every assumption you make instead of asking about it.

## Phase 1b - Recreating from images

When the user provides photos/drawings/sketches:
- **Scale first:** a photo has no absolute scale. Require at least one
  known dimension; furniture photos often contain one (a 2440mm ceiling,
  a standard 720mm counter height). If none, ask the user to measure ONE
  feature; estimate the rest proportionally.
- **Analyze before building:** write out your interpretation - part
  breakdown, joinery guesses, estimated dimension table - and get the
  user's corrections BEFORE any CAD work.
- Copy reference images into `projects/<Name>/images/` in the vault.
- Measured dimensions ALWAYS override apparent photo proportions.

## Phase 2 - Plan

- Decompose into an ordered part list (carcass/frame first, then
  shelves/panels, then details). Present it briefly.
- State GRAIN DIRECTION and SHOW FACES up front (the furniture analog of
  print orientation): solid wood runs length along grain; sheet goods
  get face grain oriented consistently on show faces.
- State the JOINERY per connection (butt + screws, dado, rabbet, pocket
  hole) before modeling: joinery changes part dimensions (a shelf housed
  in 6mm dados is 12mm longer than a butt-jointed one), so it must be
  decided before the cut list can be right.

## Phase 3 - Build loop (the core discipline)

Either backend: build ONE part/feature at a time, inspect a screenshot
after each, fix wrong geometry NOW. Never stack features on broken
geometry.

### build123d loop (default)

Grow ONE parametric source file `projects/<Name>/<name>.py` from the
start: named dimension constants at the top, a PARTS registry plus
exports and assertion checks at the end. That .py file is the canonical
CAD artifact on this path.

Keep a PARTS registry that both the visual assembly AND the cut list
consume, so the cut list can never drift from the geometry:

```python
PARTS = [
    {"name": "side", "solid": side, "qty": 2, "material": PLY_18},
    {"name": "shelf", "solid": shelf, "qty": 3, "material": PLY_18},
]
```

Model each part once in its final assembled position; place qty>1
copies with `Pos(...) * part` for the visual assembly only (the
registry holds one solid + qty). Each registry solid must be a single
part, never the whole assembly.

Per feature: add it to the source, run the file (with `SHOW=1` when a
viewer session is open), export a temp STL to the scratchpad, render it
with `scripts/render_stl.py`, and view the PNG before adding the next
feature. End the file with the SHOW-gated viewer push exactly as in the
3d-model skill (same server caveats: re-push after every edit, first
look with `SHOW=reset`). Get the user's viewer sign-off before Phase 5
on anything with fit or aesthetic stakes.

Bake verification into the file as asserts so every re-run self-checks:
bounding boxes, one solid per registry entry, volume sanity, and joint
fits measured from the geometry (probe solids), not only from the
constants.

API notes that save iterations (same as 3d-model):
- Algebra mode is the predictable core: `Box(...)`, `Pos(...) * part`,
  `+` / `-`.
- `align=(Align.CENTER, Align.CENTER, Align.MIN)` places a part on Z=0,
  floor placement for free.
- Extend cutting tools ~1 mm past coincident faces to avoid coplanar
  boolean artifacts.
- When measuring a cavity via a probe-solid boolean, keep only the
  largest resulting solid; corner slivers survive the subtraction.

### FreeCAD loop (escalation)

Same as the 3d-model skill: one self-contained feature per
`execute_code` call, inspect the returned screenshot before continuing,
extra `get_view` angles at ambiguity points, `doc.recompute()` after
mutations. Use PartDesign for parametric parts the user will tweak,
Part primitives + booleans for quick carcasses. Keep one FreeCAD object
per furniture part with a sensible Label (the cut list needs per-part
dimensions).

## Phase 4 - Buildability check (before export)

| Check | Rule |
|---|---|
| Stock thickness | Every panel thickness matches a stock size in `knowledge/woodworking-stock.md`. Nominal is not actual: the user must MEASURE actual stock before cutting joinery sized to it. |
| Rectangularity | The cut list assumes rectangular blanks. The emitter flags parts whose volume is < 98% of their bounding box; those need a drawing or template, not just a table row. |
| Grain / show face | Solid wood: length along grain. Sheet goods: face grain consistent on show faces, as stated in the Phase 2 plan. |
| Joinery fit | Dados/grooves sized to measured stock thickness (test cut first). Sliding parts ~+0.5mm; drawer boxes ~1mm gap per side. Starting values; refine from retrospectives. |
| Stock yield | Each part fits available stock: standard sheet 2440 x 1220mm, board lengths per `knowledge/woodworking-stock.md`, with ~3mm kerf between parts. |
| Wood movement | Solid-wood panels move across the grain. No rigid cross-grain attachment over ~150mm; use slotted holes, buttons, or figure-8 fasteners. Sheet goods are stable. |
| Transport & assembly | Fits through a ~750mm doorway (or design knock-down). Walk the assembly order: can every part physically be inserted last? |

Report anything unfixable without changing requirements - don't
silently alter user-specified dimensions.

## Phase 5 - Export & cut list

```python
# end of projects/<Name>/<name>.py
import sys
sys.path.insert(0, "/home/brian/ClaudeProjects/3d-modeling-brain/scripts")
from cutlist import write_cut_list

write_cut_list(
    PARTS,
    "/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/cutlist.md",
    csv_path="/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/cutlist.csv",
    title="<Name>",
)
export_step(assembly, "/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/<name>.step")
```

- Deliverables: `cutlist.md` (+ CSV), `<name>.step`, final 4-view
  renders in `projects/<Name>/images/`. STL is only a temp render input
  in the scratchpad, not a deliverable. No 3MF, no slicing.
- The emitter merges identical blanks (same rounded dims + material +
  notes; parts that differ only in machining stay separate) into one row, prints mm and inches (nearest 1/16), totals face area
  per material, and flags non-rectangular parts.
- FreeCAD path: the emitter measures build123d solids only; pass
  explicit `"dims": (t, w, l)` per part, read from `obj.Shape.BoundBox`.
- Sheet nesting / cut layout is OUT OF SCOPE for the emitter: lay out
  manually from the cut list or suggest a dedicated nesting tool.
- Record paths, key dimensions, joinery decisions, and outcomes in
  `projects/<Name>/brief.md`. After the build, write the retrospective
  in `knowledge/learnings/<name>.md` and promote measured stock values
  (actual plywood thickness, real kerf) into
  `knowledge/woodworking-stock.md`.

## Error handling

- build123d: failures are plain Python exceptions. Kernel-level boolean
  failures: reduce to simpler primitives, reorder features, extend
  cutting tools past coincident faces; never retry the identical
  failing call blindly. Two unexplained kernel failures on the same
  feature: switch to the FreeCAD escalation path.
- `execute_code` returns `{"success": false, "error": ...}`: diagnose
  from the error plus a fresh screenshot; simplify the operation.
- RPC unreachable: run the launcher script; if still down, tell the
  user to open FreeCAD and check the "MCP Addon" workbench, Start RPC
  Server.
