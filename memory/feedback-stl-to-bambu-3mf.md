---
name: feedback-stl-to-bambu-3mf
description: "At every session start, look up the vault environment (CLAUDE.md Environment section). Converting an STL to a Bambu 3MF uses the vault .venv tooling and the Bambu Studio CLI, never FreeCAD or a bare mesh writer"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 506fbb0a-36a5-4411-bd97-64325ff2c036
  modified: 2026-09-16T17:25:34.332Z
---

Convert STLs to Bambu 3MFs with `~/.local/bin/bambu-studio --export-3mf <bare name> --outputdir <dir> --arrange 1 <stl>`, then set the object name and `filament_map_mode` to Manual, as `projects/Build123d-trial/pipeline/make_print_3mf.py` does. Python tooling (build123d and the rest) lives in the vault `.venv`: run `.venv/bin/python`, never the system `python3`.

**Why:** On 2026-09-16 I checked only the system python, said build123d wasn't installed, and used FreeCAD. Brian had already set this up for several projects and was frustrated. A FreeCAD or Mesher 3MF also lacks the plate entries Bambu Studio needs.

**How to apply:** At the start of every session, check the Environment section of the project CLAUDE.md before choosing or ruling out any tool. Brian called this mistake unacceptable. Before saying a tool is missing, check `.venv/bin/python` and the existing `projects/*/pipeline` scripts. See [[feedback-agentic-os-conventions]].
