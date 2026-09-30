---
name: 3d-model
description: Use when the user asks to design, generate, create, or modify a 3D model or 3D-printable part, including recreating a part from photos, drawings, or sketches, for the Bambu Lab X2D printer. For guitar speaker cabinets, use the speaker-cab skill.
---

# Generate 3D Models (Bambu Lab X2D)

Build models feature-by-feature, visually verifying each step via
screenshots, then export STL + 3MF for slicing in Bambu Studio. Two
backends: code-CAD with build123d (default) and FreeCAD via MCP
(escalation).

## Backend choice

Default to **build123d**. Escalate to **FreeCAD MCP** when at least one
holds:
- The task edits an existing .FCStd, or the user wants a GUI-editable
  PartDesign feature tree to tweak afterwards.
- FEM is requested (`run_fem_analysis`), or a part comes from the FreeCAD
  parts library (`insert_part_from_library`).
- A build123d operation failed twice on the same feature with no clear fix.

(Live viewing is NOT an escalation reason: the build123d path has its own
interactive viewer, below.)

Both backends share Phases 1, 2, 4, and 5; only the build loop and export
mechanics differ. State the chosen backend and why in one line before
building.

## Prerequisites (check before modeling)

### build123d (default)

- Interpreter: `/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python`
  (Python 3.12 venv with build123d, trimesh, matplotlib; recreate with
  `uv venv .venv` then
  `uv pip install --python .venv/bin/python build123d trimesh matplotlib shapely`
  from the vault root).
- Headless screenshots (run from the vault root):
  `.venv/bin/python scripts/render_stl.py <model.stl> <out.png> [elev,azim ...]`
  renders shaded iso/front/top/right views; view the PNG file after each
  render.
- Interactive viewer for the user (iteration + sign-off): OCP CAD Viewer,
  installed in the venv. Open it with `scripts/cad-viewer.sh`: it starts
  the standalone server (port 3939) if needed and launches the viewer in
  a Chrome window with GPU WebGL via ANGLE-on-Vulkan (see the script for
  the exact flags; do not revert to SwiftShader, it renders on the CPU
  and is extremely slow). NEVER just hand the user the URL:
  the regular desktop Chrome cannot create a WebGL context in this Chrome
  Remote Desktop session (llvmpipe, "BindToCurrentSequence failed") and
  shows a half-initialized viewer. The standalone server
  does NOT replay a past `show()` to newly connected clients (they get
  demo content), and it delivers pushes ONLY to its EARLIEST-connected
  client: every later client (extra tab, second window, playwright)
  shows demo content forever. So: exactly ONE viewer client may exist -
  before pushing, close stale viewer windows/tabs (`wmctrl -l -G` to
  find "OCP CAD Viewer" windows, `wmctrl -ic <id>` to close; a window
  left from a previous session that reconnects first will steal every
  push from the freshly launched one). Push AFTER the user's page is
  open, re-push after any reload. Agent notes: do NOT use a browser
  client (playwright or chrome-devtools) to verify what the user sees -
  it connects late, shows the demo, and never updates; verify with a
  desktop screenshot instead (`scrot <out.png>` on DISPLAY=:20, then
  view it; `wmctrl -i -a <id>` raises the viewer window first). PNG
  renders remain the primary agent-side check.
- No GUI and no MCP tools needed for the modeling itself.

### FreeCAD MCP (escalation)

1. **FreeCAD running + RPC up:** run
   `/home/brian/ClaudeProjects/3d-modeling-brain/scripts/start-freecad-mcp.sh`
   (idempotent; exit 0 means ready).
2. **MCP tools available:** the `freecad` MCP server provides `execute_code`,
   `get_view`, `create_object`, `edit_object`, `get_objects`, etc. If these
   tools are NOT in the session, either ask the user to restart the session,
   or fall back to direct XML-RPC from Bash (same backend):
   ```python
   import xmlrpc.client
   srv = xmlrpc.client.ServerProxy("http://127.0.0.1:9875", allow_none=True)
   srv.execute_code("...")                          # {"success":..., "message"/"error":...}
   b64 = srv.get_active_screenshot("Isometric", 800, 600)  # base64 PNG; decode, save, then view the file
   ```
3. **Health doubt?** run `python3 /home/brian/ClaudeProjects/3d-modeling-brain/scripts/smoke-test.py`.

## Phase 1 — Brief

Ask ONLY load-bearing questions (batch them; don't interrogate):
- Critical dimensions; what the part attaches to / must fit
- Orientation or strength concerns; aesthetic preferences for decorative parts
State every assumption you make instead of asking about it.

## Phase 1b — Recreating from images

When the user provides photos/drawings/sketches:
- **Scale first:** a photo has no absolute scale. Require at least one known
  dimension ("80mm wide", "fits a 608 bearing"). If none, ask the user to
  measure ONE feature; estimate the rest proportionally from the image.
- **Analyze before building:** write out your geometry interpretation —
  primitive decomposition, symmetries, hole patterns, estimated dimension
  table — and get the user's corrections BEFORE any CAD work.
- **During the build:** match screenshot angles (renderer views or
  `get_view`) to the photo's viewpoint and compare side by side;
  course-correct proportions.
- Copy reference images into `projects/<Name>/images/` in the vault.
- Set expectations: flat-faced functional geometry reproduces well; organic
  shapes reproduce approximately. Measured dimensions ALWAYS override
  apparent photo proportions.

## Phase 2 — Plan

- Decompose into an ordered feature list (base solid → bosses/pockets →
  holes → fillets/chamfers). Present it briefly.
- State intended PRINT ORIENTATION up front — it drives overhang and
  strength decisions (layer lines are the weak direction). For cosmetic
  parts, orient the presentation face as an ironed TOP where geometry
  allows: the textured PEI plate molds a random texture into bed-side
  faces (knowledge/smooth-surfaces-x2d.md).

## Phase 3 — Build loop (the core discipline)

Either backend: build ONE feature at a time, inspect a screenshot after
each, fix wrong geometry NOW. Never stack features on broken geometry.

### build123d loop (default)

Grow ONE parametric source file `projects/<Name>/<name>.py` from the
start: named dimension constants at the top, exports and assertion checks
at the end. That .py file is the canonical CAD artifact on this path
(there is no .FCStd).

Per feature: add it to the source, run the file (with `SHOW=1` when a
viewer session is open), export a temp STL to the scratchpad, render it
with `scripts/render_stl.py`, and view the PNG before adding the next
feature.

User iteration and sign-off: end every model file with a SHOW-gated
viewer push, and re-run with `SHOW=1` whenever the user should look:

```python
if os.environ.get("SHOW"):
    from ocp_vscode import show, Camera
    show(part_a, part_b, names=["box", "lid"],
         reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
```

First look after the user's page opens: run with `SHOW=reset` so the
camera frames the parts. While a viewer session is open, EVERY edit to
the model file is followed by a `SHOW=1` re-run: the server never
replays old pushes, so an edit without a re-push leaves the user's
viewer silently showing stale geometry. `SHOW=1` keeps the user's
viewpoint between pushes. On parts with fit or aesthetic stakes, get the
user's sign-off in the viewer before Phase 5 export.

Bake verification into the file as asserts so every re-run self-checks:
bounding boxes, one solid per part, volume sanity, watertight exported
STLs (trimesh), and mating clearances measured from the geometry (probe
solids), not only from the constants.

API notes that save iterations:
- Algebra mode is the predictable core: `Box(...)`, `Pos(...) * part`,
  `+` / `-`, `fillet(part.edges().filter_by(Axis.Z), radius)`.
- `align=(Align.CENTER, Align.CENTER, Align.MIN)` places a part on Z=0,
  print-plate placement for free.
- `edges().group_by(Axis.Z)[0]` / `[-1]` grabs the complete bottom/top
  edge loop, fillet arcs included, ready for a chamfer.
- Extend cutting tools ~1 mm past coincident faces to avoid coplanar
  boolean artifacts.
- Overhang checks on the tessellated mesh need ~2 degrees of margin past
  45; facet normals on curved chamfer bands tilt past the exact B-rep
  angle. Where exactness matters, check B-rep face angles instead.
- When measuring a cavity via a probe-solid boolean, keep only the
  largest resulting solid; corner slivers survive the subtraction.

### FreeCAD loop (escalation)

For each feature:
1. Execute it (`execute_code` with a batched, self-contained Python block —
   one feature per call, not one line per call; each mutating MCP call
   returns a screenshot automatically).
2. **Inspect the returned screenshot before continuing.** Wrong geometry is
   fixed NOW, not later. Never stack features on broken geometry — delete
   the failed feature and rebuild it differently.
3. At ambiguity points, grab extra views: `get_view` with `Front`, `Top`,
   `Right`, `Isometric`. Blank screenshot → FreeCAD window is occluded; ask
   the user to un-minimize it, then re-request.

Workbench choice:
- **PartDesign** (Body → Sketch → Pad/Pocket/...) for functional parametric
  parts — produces an editable feature tree the user can tweak in the GUI.
- **Part** primitives + booleans for quick composed shapes.
- Lofts/sweeps/surfacing for organic forms.
- Always `doc.recompute()` after mutations; check for recompute errors in
  the returned message.

## Phase 4 — Printability check (X2D, before export)

| Check | Rule (0.6mm high-flow nozzle normally installed; user also owns 0.4mm and 0.6mm hardened steel — with 0.4mm, min wall drops to 0.84mm; prefer 0.4mm for thin flexing features under ~1.5mm) |
|---|---|
| Wall thickness | ≥ 1.24mm (2 perimeters × ~0.62mm line width) |
| Overhangs | flag > 45° unsupported; suggest chamfer/orientation fix |
| Small holes | note shrinkage; suggest +0.1–0.2mm compensation or drilling |
| Build volume | ≤ 256×256×260mm (main nozzle); ≤ 235.5×256×256mm if dual-nozzle/multi-material print |
| Mating clearance | ~0.2mm snug fit, ~0.3mm free fit |
| First layer | prefer a flat face on the bed; note elephant-foot on precision bores; the textured PEI plate molds its texture into bed-side faces — presentation faces go up |

**Color capacity (AMS 2 Pro).** The main nozzle feeds from an AMS 2 Pro:
max 4 colors per print — design multi-color models for ≤ 4 colors. The
2nd nozzle is dedicated to support material; it can serve as a 5th color
only where accuracy doesn't matter (its placement accuracy is lower), and
never for precision or mating features. Ask before designing a 5-color part.

Report anything unfixable without changing requirements — don't silently
alter user-specified dimensions.

## Phase 5 — Export & handoff

### build123d export

```python
# end of projects/<Name>/<name>.py — every part in print orientation, sitting on Z=0
export_stl(part, "/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/<name>.stl")
export_step(part, "/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/<name>.step")  # only when CAD interop matters
m = Mesher()
m.add_shape(part_a)  # one add_shape per part; lay parts out side by side with ~10 mm gaps
m.add_shape(part_b)
m.write("/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/<name>.3mf")
```
- STL and 3MF are required deliverables; STEP only when interop matters.
- ONE 3MF per project (Brian 2026-09-29): every printable part goes on its own plate of a
  single multi-plate `<name>.3mf`, never separate per-part 3MF files; per-part STLs stay
  as fallbacks. See "Multi-plate kits" below.
- Save the final 4-view renders to `projects/<Name>/images/`.
- Verify the 3MF by parsing `3D/3dmodel.model` inside the zip (object
  count, bounding boxes); trimesh cannot load 3MF without networkx.

### FreeCAD export

```python
# via execute_code — <Name> = the vault project directory, <name> = kebab-case model name
import FreeCAD, Mesh
doc = FreeCAD.ActiveDocument
doc.saveAs("/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/<name>.FCStd")
objs = [o for o in doc.Objects if o.TypeId.startswith(("Part::", "PartDesign::")) and o.Visibility]
Mesh.export(objs, "/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/<name>.stl")
Mesh.export(objs, "/home/brian/ClaudeProjects/3d-modeling-brain/projects/<Name>/<name>.3mf")
```
- `mkdir -p` the project dir first; verify both export files exist and are
  plausibly sized afterwards.

**Multi-color models — MANDATORY Bambu project 3MF** (applies to BOTH
backends; build123d's Mesher writes only object-level `basematerials`
colors, which Bambu ignores the same way). FreeCAD's
`Mesh.export` 3MF writer emits geometry only, and Bambu Studio IGNORES
object-level `basematerials` colors in generic 3MFs — its standard-3MF
color import only parses per-vertex/per-face colors (and converts even
those to paint). A generic 3MF always opens all-green. Ship a Bambu
Studio PROJECT 3MF instead, built with the locally installed CLI
(`bambu-studio` on PATH; presets in `~/.config/BambuStudio/system/BBL`):
1. Export ONE STL per color from the active backend, all in the same
   model coordinates (these double as the fallback `<name>-body.stl`, … files).
2. **Flatten the presets first.** The CLI cannot resolve `inherits`
   chains for X2D presets (its bundled profiles predate the X2D) and
   silently falls back to wrong base values (e.g. layer_height). For
   each preset to load (machine/process/filament, from
   `~/.config/BambuStudio/system/BBL/<kind>/<name>.json`): recursively
   follow `inherits`, merge dicts base-first so children override,
   drop `inherits`, keep the child's `name`, write one self-contained
   JSON. `scripts/flatten_presets.py <outdir>` does all of this and also
   injects the smooth-top ironing defaults into the process preset
   (knowledge/smooth-surfaces-x2d.md). Current hardware presets: machine
   `Bambu Lab X2D 0.6 nozzle`,
   process `0.18mm Balanced Quality @BBL X2D 0.6 nozzle` (finest for
   0.6), filament `Bambu PLA Basic @BBL X2D`.
3. ```bash
   bambu-studio --arrange 0 --assemble \
     --load-settings "flat-machine.json;flat-process.json" \
     --load-filaments "flat-filament1.json;flat-filament2.json" \
     --load-filament-ids "1,2" \
     --export-3mf <name>.3mf --outputdir <dir> color1.stl color2.stl
   ```
   `--load-filament-ids` takes one filament number PER INPUT FILE, in
   order. `--assemble` merges the files into ONE object with per-part
   filament assignments at their original relative positions — required
   for a single multi-color OBJECT; without it each file becomes a
   separate object that Bambu drops to the bed independently, breaking
   z-alignment. For a KIT of separately printed parts, instead use
   `--arrange 1` and OMIT `--assemble` so each part is its own bed
   object; duplicate parts need one STL copy per bed instance since
   filament ids map per input file. Wayland/glfw
   errors in the output are harmless (thumbnail rendering only).
   Afterwards check `Metadata/project_settings.config` has the expected
   `layer_height` and `nozzle_diameter` — wrong values mean a preset
   didn't flatten correctly.
4. Post-process the zip: in `Metadata/project_settings.config` set
   `filament_colour` to the real hex colors (the CLI writes default
   green); in `Metadata/model_settings.config` replace the STL filenames
   with friendly object/part names. Then run
   `scripts/apply_smooth_top.py <name>.3mf` (smooth-top defaults plus
   their diff-list entries). Any settings key changed inside a project
   3MF MUST also be listed in `different_settings_to_system[0]`, or
   Bambu Studio's GUI silently resets it to the named system preset on
   open; the CLI reader does not do this normalization, so a CLI round
   trip alone cannot catch the mistake.
5. Verify with a round trip through Bambu's own reader:
   `bambu-studio --arrange 0 --export-3mf out.3mf <name>.3mf` must
   preserve `filament_colour`, the per-part `extruder` values, and
   `different_settings_to_system`. GUI ground truth still requires the
   user opening the file in Bambu Studio once.
Opening the project 3MF shows the real colors; filaments 1..N map to AMS
slots in Bambu Studio. Keep the per-color STLs as fallback.

**Multi-plate kits (one file, one plate per part group).** The CLI cannot
assign plates; author them by post-processing a single-plate export:
1. CLI-load all STLs onto one plate with per-file `--load-filament-ids`.
2. In `Metadata/model_settings.config`, replace the single `<plate>` block
   with one `<plate>` per group (`plater_id` 1..N, one `<model_instance>`
   per object: object_id, instance_id 0, unique identify_id; copy the
   other plate metadata keys verbatim).
3. In `3D/3dmodel.model`, shift each build item's transform X (10th
   number) by `(plate - 1) * 307.2` (plate stride = 256 x 1.2 mm).
4. Round-trip through `bambu-studio --arrange 0 --export-3mf` must
   preserve the plate count; the user opening it in the GUI is ground
   truth and is MANDATORY - a hand-authored plate 3 once passed the CLI
   round trip yet rendered empty in the GUI. Often better than plates:
   one plate with one multi-shell STL per part group (each STL = one
   object), `print_sequence` = `by object` so groups print sequentially
   with one filament change, clusters spaced 90+ mm for toolhead
   clearance. Working example:
   `projects/Clawd-mascot/anthropic-mascot-kit.3mf`.

**Per-object and per-volume settings in authored 3MFs.** Per-object
overrides (e.g. `sparse_infill_density`, `sparse_infill_pattern`) are
extra `<metadata key=... value=.../>` lines on the `<object>` in
`Metadata/model_settings.config`; they round trip, slice correctly, and
need no `different_settings_to_system` entry. For region-scoped
settings (e.g. a solid bottom third for ballast), add a MODIFIER PART:
a box mesh as a new object in the object's `3D/Objects/*.model` file
(object ids are globally unique across all sub-model files), a
`<component>` referencing it, and a `<part subtype="modifier_part">`
carrying the setting metadata (e.g. `sparse_infill_density` 100% =
solid). NEVER put anything except `layer_height` in
`Metadata/layer_config_ranges.xml`: Bambu Studio height ranges support
ONLY layer height — any other opt_key (e.g. `sparse_infill_density`)
loads fine, survives CLI round trips AND GUI saves, then SEGFAULTS the
slicer at "Slicing mesh" (GUI and CLI both crash). A CLI round trip
does NOT validate sliceability — verify authored 3MFs with an actual
CLI slice: `bambu-studio --slice 1 --export-3mf out.3mf kit.3mf` must
exit 0, and check `used_g` in the output's `Metadata/slice_info.config`
to confirm settings took effect. (Ranges gotcha kept for layer_height
use: the object id in `layer_config_ranges.xml` is the 1-based
sequential model-object index, not the 3dmodel resource id; wrong id =
silently dropped.)

- Record paths, key dimensions, and outcomes in `projects/<Name>/brief.md`
  in the 3d-modeling-brain vault.
- Hand the user both file paths + suggested print orientation. The user
  slices in Bambu Studio — never claim the part was sent to the printer.
  For single-color parts sliced in the GUI, suggest the user preset
  `0.18mm Balanced Ironing @BBL X2D 0.6 nozzle` (smooth-top default,
  knowledge/smooth-surfaces-x2d.md).

## Error handling

- build123d: failures are plain Python exceptions. Kernel-level fillet or
  boolean failures → reduce the radius, reorder features, or tighten the
  edge selection; never retry the identical failing call blindly. Two
  unexplained kernel failures on the same feature → switch to the FreeCAD
  escalation path.
- `execute_code` returns `{"success": false, "error": ...}` → diagnose from
  the error plus a fresh screenshot; simplify the operation; never retry the
  identical failing call blindly.
- RPC unreachable → run the launcher script; if still down, tell the user to
  open FreeCAD and check the "MCP Addon" workbench → Start RPC Server.
- Boolean/sketch failures: reduce to simpler primitives, or rebuild the
  sketch fully-constrained; over-constrained sketches must be fixed, not
  ignored.
