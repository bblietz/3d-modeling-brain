# FreeCAD 3D Model Generation Project

Claude generates 3D models here for Brian's Bambu Lab X2D printer.

## How it works
- The `/3d-model` skill (`skills/3d-model/SKILL.md`, symlinked into
  `~/.claude/skills/`) holds the full modeling workflow — use it for any
  model request.
- FreeCAD 1.1.3 AppImage + `FreeCADMCP` addon (RPC on localhost:9875,
  auto-starts with FreeCAD). MCP server `freecad` registered at user scope
  (`uvx freecad-mcp`).
- Start/ensure FreeCAD: `scripts/start-freecad-mcp.sh`
- Health check: `python3 scripts/smoke-test.py`

## Layout
- `models/<name>/` — `<name>.FCStd` + `<name>.stl` + `<name>.3mf`
  (+ `reference/` images when recreated from photos)
- `vendor/freecad-mcp/` — gitignored clone; to update the addon:
  `git -C vendor/freecad-mcp pull` then re-copy `addon/FreeCADMCP` to
  `~/.local/share/FreeCAD/v1-1/Mod/` and restart FreeCAD.
- `docs/superpowers/` — design spec and implementation plan.
- On a FreeCAD version upgrade, three version-pinned spots need updating:
  the `APPIMAGE` path and the `pgrep -f "FreeCAD_1.1.3-Linux"` pattern in
  `scripts/start-freecad-mcp.sh`, and the `~/.local/share/FreeCAD/v1-1/`
  data dir referenced above.

## Printer constraints (X2D)
Build volume 256×256×260mm (main nozzle) / 235.5×256×256mm (dual-nozzle
prints); 0.6mm high-flow nozzle installed (line width ~0.62mm, min wall
~1.24mm). AMS 2 Pro on the main nozzle: max 4 colors
per print. 2nd nozzle is for support material; usable as a lower-accuracy
5th color only when precision doesn't matter. Full printability rules
live in the skill.
