---
tags: [project, infrastructure, setup]
status: migrated into this vault 2026-07-30; source directory retired
---

# FreeCAD setup project

The project that wired everything together: Claude driving FreeCAD over MCP with screenshot verification, plus the Bambu Studio slicing pipeline for the X2D. It lived at `~/ClaudeProjects/FreeCAD` (local-only git repo, 25 commits, 2026-07-26 to 2026-07-30) until 2026-07-30, when all durable content was migrated into this vault and the directory was cleared for deletion.

## Architecture (five components)

1. `FreeCADMCP` addon (from neka-nat/freecad-mcp) installed at `~/.local/share/FreeCAD/v1-1/Mod/FreeCADMCP/`, hosting an XML-RPC server on `localhost:9875` inside the FreeCAD GUI. Auto-starts via `~/.local/share/FreeCAD/v1-1/freecad_mcp_settings.json` (`auto_start_rpc: true`, localhost only).
2. MCP server `freecad` registered at user scope in `~/.claude.json`: `uvx freecad-mcp`, screenshots enabled. Available from any Claude Code session.
3. `/3d-model` skill: versioned at `skills/3d-model/SKILL.md` in this vault, symlinked from `~/.claude/skills/3d-model`. Encodes the whole workflow (brief, image recreation, build loop with screenshot inspection, X2D printability check, project-3MF export).
4. `projects/<Name>/` in this vault: brief plus CAD artifacts (FCStd, STL, 3MF) and reference images per model project.
5. Self-serve ops scripts in this vault's `scripts/`: `start-freecad-mcp.sh` (idempotent launcher, waits for RPC) and `smoke-test.py` (end-to-end health check via direct XML-RPC), plus `flatten_presets.py` and `postprocess_3mf.py` for the Bambu CLI pipeline.

The design spec and implementation plan live in this directory (`2026-07-26-freecad-3d-model-system-design.md`, `2026-07-26-freecad-3d-model-system.md`). The spec records the MCP server survey and why neka-nat/freecad-mcp won (per-mutation screenshots, active maintenance). The old repo's CLAUDE.md is kept as `freecad-repo-CLAUDE.md`; its content is superseded by this vault's CLAUDE.md and the skill.

## What moved where (2026-07-30)

| From `~/ClaudeProjects/FreeCAD` | To |
|---|---|
| `models/anthropic-mascot/` | `projects/Clawd-mascot/` |
| `models/kelkom-intercom-button/` (incl. `scripts/`) | `projects/Kelkom-button/` |
| `models/lego-rocket/`, `-mk2/`, `-mk3/` | `projects/Lego-3d-test/lego-rocket/`, `.../lego-rocket-mk2/`, `.../lego-rocket-mk3/` |
| `skills/3d-model/` | `skills/3d-model/` (symlink `~/.claude/skills/3d-model` re-pointed) |
| `scripts/` (launcher, smoke test, preset/3MF helpers) | `scripts/` |
| `docs/superpowers/` spec and plan | this directory |
| git log | [[git-history]] |
| last committed single-figure Clawd 3MF (`git show 9a164fc`) | `projects/Clawd-mascot/anthropic-mascot-single.3mf` |

Left behind as deletable: `.git` (log preserved in [[git-history]]; per-commit file contents are lost on deletion), the gitignored `vendor/freecad-mcp` clone (re-clone from GitHub when the addon needs updating), `.superpowers/` SDD working files (distilled into [[freecad-setup]]), `*.FCBak` autosaves, and `reference/` images (byte-identical copies already in the project `images/` dirs).

**Migration complete:** `models/lego-rocket-mk3/` was moved over by its own build session later on 2026-07-30 and verified byte-identical to commit `e306966` (its DESIGN.md is newer, carrying the as-built deviations). Nothing durable remains in `~/ClaudeProjects/FreeCAD`; it is safe to delete.

## Key paths

| Thing | Path |
|---|---|
| FreeCAD 1.1.3 AppImage | `~/Applications/FreeCAD_1.1.3-Linux-x86_64-py311.appimage` (symlink `~/.local/bin/freecad`) |
| Bambu Studio AppImage | `~/Applications/BambuStudio_ubuntu24.04-v02.08.01.55.AppImage` |
| Bambu presets | `~/.config/BambuStudio/system/BBL/` |
| Addon settings | `~/.local/share/FreeCAD/v1-1/freecad_mcp_settings.json` |
| Launcher / health check | `~/ClaudeProjects/3d-modeling-brain/scripts/start-freecad-mcp.sh`, `scripts/smoke-test.py` |

On a FreeCAD version upgrade, three version-pinned spots need updating: the `APPIMAGE` path and the `pgrep -f "FreeCAD_1.1.3-Linux"` pattern in the launcher, and the `~/.local/share/FreeCAD/v1-1/` data dir.

## Open items

- The vault now holds the CAD binaries but is not a git repo; the old repo's version control is gone. Consider `git init` here (or another backup).
- Delete `~/ClaudeProjects/FreeCAD` when convenient; everything durable is migrated.

## Related

- [[freecad-setup]] learnings note (setup retrospective and gotchas)
- [[git-history]]
- [[printer-x2d]]
