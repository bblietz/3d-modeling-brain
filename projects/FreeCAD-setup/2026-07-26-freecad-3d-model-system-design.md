# FreeCAD 3D Model Generation System — Design

**Date:** 2026-07-26
**Status:** Approved pending user review
**Goal:** A system where the user asks Claude to generate 3D models (from a description or reference images), Claude builds them iteratively in FreeCAD with visual verification at each step, and finished models export as STL + 3MF for slicing in Bambu Studio for a Bambu Lab X2D printer.

## Context

- FreeCAD 1.1.3 AppImage at `~/Applications/FreeCAD_1.1.3-Linux-x86_64-py311.appimage`, symlinked as `~/.local/bin/freecad`. User config at `~/.config/FreeCAD/v1-1`, user data at `~/.local/share/FreeCAD/v1-1`.
- Linux with X display available; `uv`/`uvx` and Node installed.
- Model types: general-purpose — functional parts, household items, and artistic/organic pieces.
- Workflow choice: FreeCAD GUI open on the desktop; Claude drives it and self-checks screenshots; user watches live and can intervene.

## MCP server selection

**Chosen: [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp)** (~1,460 stars, actively maintained — commits merged 2026-07-26, v0.1.19 released 2026-07-06).

Rationale (from a survey of 7+ FreeCAD MCP servers):
- Best-in-class visual feedback loop: every mutating tool call automatically returns a screenshot of the 3D viewport; `get_view` provides on-demand captures with selectable view (front/top/right/axonometric/etc.).
- `execute_code` runs arbitrary Python inside FreeCAD — full access to Part, PartDesign, Sketcher, Mesh, Draft workbenches, including STL/3MF export.
- Most active maintenance and largest community of any FreeCAD MCP server; screenshot bugs on Linux/macOS/Windows all fixed during 2026.
- Clean pairing with AppImage installs: the addon is a folder copy into the user Mod dir (which the AppImage reads); the MCP server itself runs externally via `uvx freecad-mcp`.

Rejected alternatives:
- **spkane/freecad-addon-robust-mcp-server** — larger tool surface and native 3MF export, but open unfixed crashes against FreeCAD 1.1.x (the user's exact version) and maintenance stalled since 2026-05.
- **Code-first MCP (build123d/CadQuery/OpenSCAD)** — reliable and headless, but loses the live-FreeCAD experience and the editable feature tree. Documented fallback if the GUI dependency ever becomes a problem.
- Others (bonninr, contextform, jango-blockchained, theosib, ATOI-Ming) — abandoned, immature, missing screenshots, or missing arbitrary Python execution.

## Architecture

Five components:

1. **FreeCAD MCP addon** — `FreeCADMCP` from the neka-nat repo, installed at `~/.local/share/FreeCAD/v1-1/Mod/FreeCADMCP`. Runs an RPC server on `localhost:9875` inside the FreeCAD GUI. Configured to auto-start (via the addon's settings, persisted in `freecad_mcp_settings.json`) so no manual click is needed after first setup.

2. **MCP server registration** — `claude mcp add freecad --scope user -- uvx freecad-mcp`, registered at user scope so FreeCAD tools are available from any Claude Code session. Screenshot feedback stays enabled (no `--only-text-feedback`).

3. **`/3d-model` skill** — personal skill at `~/.claude/skills/3d-model/SKILL.md`. Encodes the entire modeling workflow (below): briefing, image-based recreation, feature-by-feature build with screenshot verification, X2D printability rules, export procedure, and error-handling rules.

4. **Project folder** — `~/ClaudeProjects/FreeCAD/` (git repo):
   - `models/<model-name>/<name>.FCStd` — editable parametric source
   - `models/<model-name>/<name>.stl` and `<name>.3mf` — print-ready exports
   - `models/<model-name>/reference/` — reference images when a model was recreated from photos
   - `docs/` — this spec and future plans

5. **Launcher helper** — `~/ClaudeProjects/FreeCAD/scripts/start-freecad-mcp.sh`: starts the AppImage if not already running (checked via `pgrep`), so Claude can self-serve when a session needs FreeCAD.

### Data flow

User request → skill loads → brief/image analysis → Claude drives FreeCAD via MCP tools (`execute_code`, `create_object`, `edit_object`, `get_view`, …) → each mutation returns a screenshot Claude inspects → user watches live in the FreeCAD window → printability check → export STL + 3MF → paths handed to user for Bambu Studio.

## Modeling workflow (the skill's content)

**Phase 1 — Brief.** Ask only load-bearing questions: critical dimensions, what the part attaches to or must fit, orientation/strength concerns. For artistic pieces: overall size and style references. State assumptions instead of interrogating.

**Phase 1b — Image-based recreation (when reference images are provided).**
- Inputs: pasted images or file paths — photos of physical parts, drawings, product screenshots, hand sketches. Multiple angles help; a ruler or known object in frame helps more.
- Scale calibration: photos carry no absolute scale, so at least one known dimension is required (e.g., "80mm wide" or "fits a 608 bearing"). If none is known, ask the user to measure one feature; remaining dimensions are proportionally estimated from the image.
- Analysis before building: produce a written geometry interpretation — primitive decomposition, symmetries, hole patterns, estimated dimension table — and show it to the user for correction before any FreeCAD work starts.
- During the build, compare FreeCAD screenshots against the reference image, matching `get_view` angles to the photo's viewpoint where possible, and course-correct proportions.
- Copy reference images into `models/<name>/reference/` for provenance.
- Stated limits: organic/sculptural photos reproduce approximately; flat-faced functional geometry reproduces well. Measured dimensions always override apparent photo proportions.

**Phase 2 — Plan.** Decompose the part into an ordered feature list (e.g., base plate → bosses → M4 through-holes → fillets). State intended print orientation up front — it drives overhang and strength decisions.

**Phase 3 — Build loop.** Per feature: execute via MCP → inspect returned screenshot → fix wrong geometry before continuing. Grab extra views at ambiguity points. PartDesign for parametric/functional work; Part booleans, lofts, and surfacing for organic shapes. Batch related Python into single `execute_code` calls so the loop costs one screenshot per feature, not per line.

**Phase 4 — Printability check (Bambu Lab X2D, 0.4mm nozzle).**
Figures below assume the stock 0.4mm nozzle (X2D supports 0.2/0.4/0.6/0.8mm; adjust wall-thickness multiples if the user says they run a different nozzle). Build volume confirmed from Bambu Lab's official X2D spec sheet.
- Wall thickness ≥ 0.84mm (2 perimeters at ~0.42mm line width)
- Flag unsupported overhangs > 45°
- Note small holes (print shrinkage; suggest drilling or compensation)
- Part fits the build volume: 256×256×260mm (main nozzle); 235.5×256×256mm when a print uses dual-nozzle/auxiliary mode
- Mating clearances: ~0.2mm snug fit, ~0.3mm free fit
- Report anything unfixable without changing requirements

**Phase 5 — Export & handoff.** Save `.FCStd`; export STL and 3MF via `Mesh.export` in `execute_code`; commit to git; report file paths and suggested print orientation.

## Error handling

- **MCP can't reach FreeCAD:** check `pgrep -f FreeCAD`; if not running, launch via `scripts/start-freecad-mcp.sh`; if running but RPC not started, tell the user to start it in the MCP Addon workbench (one-time if auto-start is configured).
- **Geometry failures** (failed booleans, over-constrained sketches): diagnose from the Python error plus screenshot. Never stack workarounds on broken geometry — delete the failed feature and rebuild differently.
- **Blank/stale screenshots:** known when the FreeCAD window is fully occluded; keep the window at least partially visible; re-request `get_view` on a blank capture.
- **Token cost:** automatic per-mutation screenshots are the point, but long builds are batched (Phase 3) to keep one screenshot per feature.

## Testing / verification

Setup is complete only when an end-to-end smoke test passes:
1. Create a new document via MCP
2. Create a 10mm cube
3. Capture a screenshot and confirm the cube is visible
4. Export STL to the scratchpad and verify the file exists and is a non-trivial valid mesh
5. Delete the test document/files

Each future modeling session self-verifies through the same loop: every feature's screenshot is inspected before proceeding, and exports are checked for existence and plausible file size.

## Out of scope

- Automatic slicing / sending prints to the X2D (user slices in Bambu Studio)
- Multi-material/AMS-aware model splitting (future enhancement)
- FEM/strength analysis (the MCP server exposes FEM tools; not part of this design)
