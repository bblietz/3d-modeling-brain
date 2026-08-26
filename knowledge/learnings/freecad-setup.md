---
tags: [learnings, infrastructure]
date: 2026-07-26
---

# FreeCAD setup retrospective

Setup of the Claude + FreeCAD + Bambu Studio pipeline (see [[FreeCAD-setup/brief|the setup project brief]]). Built 2026-07-26 via subagent-driven development against a written plan: 7 tasks, each reviewed, final review "with fixes", all fixes verified live.

## What worked

- neka-nat/freecad-mcp was the right MCP server pick: every mutating call returns a screenshot, which makes the per-feature visual verification loop cheap. Chosen over 7+ alternatives (survey in the design spec).
- Pre-seeding `freecad_mcp_settings.json` with `auto_start_rpc: true` means FreeCAD launch alone brings up the RPC server; no manual workbench click.
- Registering the MCP server at user scope (`uvx freecad-mcp`) makes the tools available from any project directory.
- Keeping the skill versioned in a repo and symlinking it into `~/.claude/skills/` (survives edits, stays browsable). The symlink now points into this vault.
- Verifying through direct XML-RPC (`localhost:9875`) from Bash when MCP tools are not loaded in the current session; MCP tools only appear after a session restart, so setup-time verification must bypass MCP. The pattern lives on in `projects/Kelkom-button/scripts/fc.py`.

## Gotchas (hard-won)

- Bambu Studio ignores object-level `basematerials` colors in generic 3MFs; they always open all-green. Multi-color models must ship a Bambu Studio project 3MF built with the `bambu-studio` CLI (`--assemble`, per-part filament ids) with `filament_colour` patched into `Metadata/project_settings.config` afterward. Full procedure in the `/3d-model` skill Phase 5.
- The bambu-studio CLI cannot resolve preset `inherits` chains for X2D profiles (its bundled profiles predate the printer) and silently falls back to wrong base values such as layer_height. Flatten presets to self-contained JSONs first (`scripts/flatten_presets.py`).
- `--assemble` vs `--arrange 1`: assemble merges input STLs into one multi-color object at fixed relative positions; without it, parts drop to the bed independently and z-alignment breaks. Kits of separate parts want `--arrange 1` and no `--assemble`.
- Blank MCP screenshots mean the FreeCAD window is occluded or minimized; keep it visible and re-request.
- A failed smoke test originally leaked open documents in live FreeCAD; the fix (pre-close stale docs plus `try/finally` cleanup) is a good template for any script that mutates live FreeCAD state.
- Wayland/glfw errors from the bambu-studio CLI are harmless thumbnail-rendering noise; do not treat them as failures.

## Verified facts

- X2D build volume 256 x 256 x 260 mm (main nozzle), 235.5 x 256 x 256 mm dual-nozzle, confirmed against the official Bambu spec sheet PDF, not folklore.

## Related

- [[printer-x2d]]
- [[git-history]] (full commit log of the setup repo)
