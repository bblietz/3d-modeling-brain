---
tags: [project, lego, kit, multi-color]
status: modeled and exported, no print-fit feedback yet
---

# Lego rocket kits (Mk1, Mk2, Mk3)

Lego-compatible rocket kits: Mk1 is a 5-piece 2-color rocket (63.6 mm tall), Mk2 a 22-piece 3-color multi-stage rocket with launch pad, engine bells, and corner boosters (127 mm on pad). Mk3 is the round-body redesign of Mk2: same 22-piece architecture with cylindrical bodies (125.6 mm on pad).

## Artifacts

- Mk1: `lego-rocket/` in this directory (STLs, 3MF, FCStd, BUILD-INSTRUCTIONS.md, step renders, `lego_rocket_assembly.FCStd`)
- Mk2: `lego-rocket-mk2/` in this directory: 10 unique STLs, verified Bambu project 3MF (22 objects, red/white/gray, 0.18 mm, X2D 0.6 nozzle), BUILD-INSTRUCTIONS.md, step renders, `mk2_assembly.FCStd`
- Mk3: `lego-rocket-mk3/` in this directory: DESIGN.md spec (with as-built deviations), 10 unique STLs, verified kit 3MF (22 objects, red/white/gray, 0.18 mm, X2D 0.6 nozzle), BUILD-INSTRUCTIONS.md, parametric `scripts/01..12`, parts + assembly FCStd
- History: commits `fb204e7` (Mk1), `1be0c85` (Mk2), `e306966` (Mk3) from the retired FreeCAD repo; full log preserved in [[git-history]]
- Build-instructions artifact: https://claude.ai/code/artifact/309a59b6-86e7-4f89-9531-f0ba86a2499d
- Session handoff with locked decisions: `.claude/context-check/last-handoff.md` in this directory

## Locked decisions

- All geometry constants and tolerances: [[lego-geometry]]
- Print studs-up, flat on bed, no supports; elephant-foot compensation about 0.15 mm in the slicer, not modeled
- Kit 3MFs use `--arrange 1` without `--assemble`

## Open items

- No print has been fit-tested; record feedback against [[lego-geometry]] when it happens.
- Mk3's round clutch (Ø30.2 cavity with tube pinch, R2 center-tube pinch with relief notches) is new, unproven geometry: print one Body and one Stage first and test-fit on a real Lego brick before committing to the whole kit.

## Related

- [[lego-3d-test]] learnings note, [[printer-x2d]]
