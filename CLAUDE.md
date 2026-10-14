# 3D Modeling Brain

Agentic OS and second brain for designing and printing 3D models on a Bambu Lab X2D.

## Layout

- `projects/<Name>/` - one directory per model project: brief, reference images, decisions, and the CAD artifacts (FCStd, STL, 3MF).
- `scripts/` - ops scripts: FreeCAD launcher (`start-freecad-mcp.sh`), health check (`smoke-test.py`), Bambu preset/3MF helpers.
- `skills/` - the `/3d-model`, `/furniture`, and `/speaker-cab` skill sources, symlinked from `~/.claude/skills/`.
- `knowledge/` - distilled, reusable notes (printer profile, materials, techniques). `knowledge/learnings/` holds per-project retrospectives.
- `memory/` - Claude persistent memory. This is the canonical location; `~/.claude/projects/-home-brian-ClaudeProjects-3d-modeling-brain/memory` is a symlink pointing here so Obsidian indexes every memory file. Do not break this symlink.
- This folder is an Obsidian vault (`.obsidian/`). Write all notes as Obsidian markdown: YAML frontmatter plus `[[wikilinks]]`.

## Environment (check at the start of every session)

Before using or ruling out any tool, confirm it against this list. Never say a tool is not installed after checking only the system `python3`.

- Python: the vault venv `.venv/bin/python` (3.12) has build123d, trimesh, matplotlib, shapely. The system `python3` does not.
- Bambu Studio CLI: `~/.local/bin/bambu-studio` (wrapper for `~/Applications/BambuStudio_ubuntu24.04-v02.08.02.61.AppImage`). STL to Bambu 3MF: `--export-3mf <bare name> --outputdir <dir> --arrange 1 <stl>`, as in `projects/Build123d-trial/pipeline/make_print_3mf.py`.
- OpenSCAD: `~/.local/bin/openscad` (AppImage 2026.01 nightly in `~/Applications`, Manifold backend). Headless: `openscad --backend=Manifold --preview --viewall --camera=ex,ey,ez,cx,cy,cz -o out.png file.scad`; STL with `-o out.stl`.
- FreeCAD: `~/Applications/FreeCAD_1.1.3-Linux-x86_64-py311.appimage`, reached over MCP after `scripts/start-freecad-mcp.sh`. There is no `freecadcmd`, so `execute_code_headless` fails.
- Before building a new approach, look for an existing script in `scripts/` or `projects/*/pipeline/`.

## Modeling workflow

- Always use the `/3d-model` skill for 3D-printing work (visual verification per feature, printability check, STL + 3MF export), the `/furniture` skill for furniture/woodworking work (same build discipline; buildability check and cut list via `scripts/cutlist.py` instead of printability and 3MF), and the `/speaker-cab` skill for guitar speaker cabinet orders (voicing engine, generator, check table, and customer proposal, with two stops for Brian).
- Per that skill, CAD artifacts (FCStd, STL, 3MF) live in `projects/<Name>/` alongside the notes (migrated from the retired `~/ClaudeProjects/FreeCAD` repo on 2026-07-30). Record paths and outcomes in `projects/<Name>/` notes.
- After each completed model or print, write a retrospective in `knowledge/learnings/<name>.md`: what worked, what failed, measured fits, settings used.
- At milestones and before any `/clear`, persist a handoff to `.claude/context-check/last-handoff.md` in the active project directory, including a "Decisions already locked" block; promote locked decisions into the retrospective so they outlive the handoff.

## Printer: Bambu Lab X2D

- Nozzles owned: 0.2 mm, 0.4 mm, 0.6 mm, and 0.6 mm high-flow ("speed nozzle"), all hardened steel. The 0.6 high-flow is normally installed (the 0.2 was in on 2026-10-12 for the guitar pick's first print; printer-verified 2026-10-14: 0.6 high-flow back in the main hotend, so the pick reprint needs the 0.2 swapped in again); confirm with `scripts/x2d-status.py` before applying wall-thickness rules if the choice matters, and when advising on best results say which nozzle fits the job (0.2 hairline detail at 3 to 4x time, 0.4 fine detail, 0.6 speed).
- Minimum wall = 2 perimeters: about 1.24 mm with a 0.6 nozzle, about 0.84 mm with the 0.4 nozzle.
- Build volume 256 x 256 x 260 mm (235.5 x 256 x 256 mm for dual-nozzle prints). AMS 2 Pro: max 4 colors per print; the second nozzle is for support material and is only a low-accuracy 5th color.
- Clearances: about 0.2 mm snug fit, 0.3 mm free fit.
- Full profile and per-nozzle design rules: [[printer-x2d]].

## Agent policy

- Use subagents whenever possible: codebase or file exploration, reference-image inspection, transcript mining, research, and independent parallel builds. Keep the main context lean; only conclusions belong in the main thread.
- Batch independent subagents in parallel.
- Heavy local jobs (slicer runs, G-code region passes, renders, anything over about 1 GB or one core each) never run as a bare shell loop. Cap the concurrency (`xargs -P`) and wrap the batch in a memory-capped scope so an overrun kills only those jobs, never the desktop or the trading services: `systemd-run --user --scope -p MemoryMax=44G -p MemoryHigh=40G -p MemorySwapMax=2G -p OOMPolicy=continue -- sh -c '...'`. On 2026-10-12 a loop of 28 region passes at 9.7 GB each OOM-killed the whole box, including brian's user manager and the live trading daemon.
