# 3D Modeling Brain

Agentic OS and second brain for designing and printing 3D models on a Bambu Lab X2D.

## Layout

- `projects/<Name>/` - one directory per model project: brief, reference images, decisions, and the CAD artifacts (FCStd, STL, 3MF).
- `scripts/` - ops scripts: FreeCAD launcher (`start-freecad-mcp.sh`), health check (`smoke-test.py`), Bambu preset/3MF helpers.
- `skills/` - the `/3d-model` and `/furniture` skill sources, symlinked from `~/.claude/skills/`.
- `knowledge/` - distilled, reusable notes (printer profile, materials, techniques). `knowledge/learnings/` holds per-project retrospectives.
- `memory/` - Claude persistent memory. This is the canonical location; `~/.claude/projects/-home-brian-ClaudeProjects-3d-modeling-brain/memory` is a symlink pointing here so Obsidian indexes every memory file. Do not break this symlink.
- This folder is an Obsidian vault (`.obsidian/`). Write all notes as Obsidian markdown: YAML frontmatter plus `[[wikilinks]]`.

## Modeling workflow

- Always use the `/3d-model` skill for 3D-printing work (visual verification per feature, printability check, STL + 3MF export) and the `/furniture` skill for furniture/woodworking work (same build discipline; buildability check and cut list via `scripts/cutlist.py` instead of printability and 3MF).
- Per that skill, CAD artifacts (FCStd, STL, 3MF) live in `projects/<Name>/` alongside the notes (migrated from the retired `~/ClaudeProjects/FreeCAD` repo on 2026-07-30). Record paths and outcomes in `projects/<Name>/` notes.
- After each completed model or print, write a retrospective in `knowledge/learnings/<name>.md`: what worked, what failed, measured fits, settings used.
- At milestones and before any `/clear`, persist a handoff to `.claude/context-check/last-handoff.md` in the active project directory, including a "Decisions already locked" block; promote locked decisions into the retrospective so they outlive the handoff.

## Printer: Bambu Lab X2D

- Nozzles owned: 0.2 mm, 0.4 mm, 0.6 mm, and 0.6 mm high-flow ("speed nozzle"), all hardened steel. The 0.6 high-flow is normally installed (0.4 installed since 2026-08-06 for the Sharks nametag); confirm before applying wall-thickness rules if the choice matters, and when advising on best results say which nozzle fits the job (0.2 hairline detail at 3 to 4x time, 0.4 fine detail, 0.6 speed).
- Minimum wall = 2 perimeters: about 1.24 mm with a 0.6 nozzle, about 0.84 mm with the 0.4 nozzle.
- Build volume 256 x 256 x 260 mm (235.5 x 256 x 256 mm for dual-nozzle prints). AMS 2 Pro: max 4 colors per print; the second nozzle is for support material and is only a low-accuracy 5th color.
- Clearances: about 0.2 mm snug fit, 0.3 mm free fit.
- Full profile and per-nozzle design rules: [[printer-x2d]].

## Agent policy

- Use subagents whenever possible: codebase or file exploration, reference-image inspection, transcript mining, research, and independent parallel builds. Keep the main context lean; only conclusions belong in the main thread.
- Batch independent subagents in parallel.
