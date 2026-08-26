# 3D Modeling Brain

Second brain and agentic workspace for 3D printing on the Bambu Lab X2D.

## Open in Obsidian

This folder is a ready-made vault: in Obsidian choose "Open folder as vault" and select
`~/ClaudeProjects/3d-modeling-brain`. Everything, including Claude's persistent memory
in `memory/`, is then indexed and searchable, and `[[wikilinks]]` resolve across
memory and knowledge notes.

## Layout

| Folder | Purpose |
|---|---|
| `projects/` | One directory per model project (briefs, reference images, decisions, CAD artifacts) |
| `knowledge/` | Reusable notes: printer profile, techniques, per-project learnings |
| `memory/` | Claude's persistent memory (canonical; symlinked from `~/.claude`) |
| `scripts/` | FreeCAD/Bambu ops scripts (launcher, smoke test, preset flattening) |
| `skills/` | `/3d-model` skill source (symlinked from `~/.claude/skills`) |

CAD artifacts (FCStd, STL, 3MF) live inside each project directory under `projects/`,
exported there by the `/3d-model` skill.
