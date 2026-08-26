Continuing work on the FreeCAD Lego rocket kits (repo: /home/brian/ClaudeProjects/FreeCAD; session cwd: /home/brian/ClaudeProjects/Lego-3d-test, not a git repo). Done so far:
- Mk1: 5-piece Lego-compatible rocket kit (commit fb204e7) in models/lego-rocket/.
- Mk2: 22-piece multi-stage rocket (commit 1be0c85) in models/lego-rocket-mk2/: launch pad with engine-bell well, 4 bells, finned tail, 2x 4x4 bodies, porthole brick, 4x4→2x2 taper, 3 octagonal 2x2 bricks, nose cone, 4 corner boosters. 10 unique STLs + verified Bambu project 3MF (22 objects, filaments 1=red/2=white/3=gray, 0.18mm, X2D 0.6 nozzle) + BUILD-INSTRUCTIONS.md + step renders.
- Build-instructions artifact (both versions published to same URL): https://claude.ai/code/artifact/309a59b6-86e7-4f89-9531-f0ba86a2499d

Current state: everything committed; FreeCAD running with docs lego_rocket, lego_rocket_mk2, mk2_assembly open; scratchpad (flattened Bambu presets, template HTML) is session-scoped and will be gone — regenerate flat presets per the 3d-model skill if another 3MF export is needed.

Files that matter:
- /home/brian/ClaudeProjects/FreeCAD/models/lego-rocket-mk2/ — all Mk2 deliverables (FCStd, STLs, 3mf, instructions).
- /home/brian/ClaudeProjects/FreeCAD/models/lego-rocket/ — Mk1 kit, kept intact.
- /home/brian/.claude/skills/3d-model/ — workflow incl. preset-flattening and 3MF post-processing steps.

Decisions already locked: standard Lego geometry (8mm pitch; 2x2=15.8, 4x4=31.8; brick 9.6; studs Ø4.8×1.7; solid tubes Ø6.5; cavities +0.1mm FDM compensation, walls 1.45); octagonal bricks use 4.0mm outer / 3.0mm cavity corner chamfers to keep clutch; colors #D32F2F red, #F2F2F2 white, #555555 gray; no supports, studs-up printing, elephant-foot compensation ~0.15mm in slicer rather than modeled chamfers; kit 3MFs use --arrange 1 without --assemble.

Next action: none pending — await user direction (e.g., print-fit feedback, part tweaks, or a new model).
