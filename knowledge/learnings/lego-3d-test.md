---
tags: [learnings, freecad, lego, multi-color, workflow]
source: Lego rocket sessions, 2026-07-30
---

# Learnings: Lego rocket kits (Mk1 and Mk2)

Mk1 (5-piece rocket) and Mk2 (22-piece multi-stage kit with launch pad and boosters) were modeled, rendered with build instructions, and exported as verified Bambu project 3MFs in a single clean session: the whole Mk2 kit took 8 `execute_code` calls with zero errors. Geometry constants: [[lego-geometry]]. Project state: [[brief]] in projects/Lego-3d-test.

## Modeling technique

- Scripted Part-workbench CSG throughout: `Part.makeBox/makeCylinder/makeCone/makeSphere`, polygon-face extrudes for fins and octagons, `makeLoft` for the taper, `.cut()/.fuse()`, `.removeSplitter()` after every part.
- One `execute_code` call = one complete self-contained part: imports, factory functions, geometry, `recompute()`, view, and an in-band validity print (`isValid()`, volume, BoundBox height). Do not split into micro-calls.
- Reusable factory functions (`brick_2x2()`, `stud(x,y,z)`, `fin()`) re-declared per call because MCP calls share no scope. Promote these into a persistent constants/factory module; retyping them is the biggest avoidable cost.
- Batch-fuse lists (`pad.fuse([60 studs])`) instead of chained pairwise fuses.
- Scatter unique parts on an XY grid in the parts document (one screenshot doubles as the kit-contents render); a separate assembly document re-places copies at stack heights with `Step<N>_` names so object order drives instruction steps.
- Provenance caveat: the saved FCStd files contain only baked `Part::Feature` solids, no sketches or feature tree, and are not editable in the GUI. The Python is the real parametric source; keep build scripts in the model directory.

## Instruction and documentation rendering

- Progressive-visibility loop inside FreeCAD, `view.saveImage(path, 900, 900, "White")`; exploded views by temporarily bumping `Placement.Base.z`, rendering, restoring.
- BUILD-INSTRUCTIONS.md template that proved out: kit-contents table (Qty, Part, Color, Size), printing section, assembly step table with images, design-data section with exact constants.
- Published HTML artifact self-contained via base64 image data URIs.

## Export pipeline (multi-color)

- Kit vs assembly distinction: `--assemble` merges all input STLs into one object at fixed relative positions, which is right for a single multi-color object only. For a kit of separately printed parts use `--arrange 1` and omit `--assemble`. Duplicate parts need one STL copy per bed instance because `--load-filament-ids` maps one id per input file.
- Flatten Bambu presets before CLI use; post-process the 3MF zip (`filament_colour`, friendly object names); round-trip verify through Bambu's own reader. The scripts for this (`flatten_presets.py`, `postprocess_3mf.py`) were session-scoped and nearly lost; both now live in `~/ClaudeProjects/3d-modeling-brain/scripts/`. `postprocess_3mf.py` was parameterized during the Mk3 build (args: 3mf path, colors list, stl=name mappings); `flatten_presets.py` still hardcodes the three X2D preset names.
- Wayland/glfw errors from the bambu-studio CLI are harmless (thumbnail rendering only); filter them out of error greps.

## Process

- Open with an explicit assumptions list instead of blocking questions; present a named plan; build to it.
- Keep prior versions intact (Mk2 was a new directory, Mk1 untouched); one atomic commit per model directory.
- The `/context-check` handoff with a "Decisions already locked" block preserved every constant, color, and CLI flag across a `/clear`. Standing convention now in CLAUDE.md.
- Gap this exposed: zero subagents across 313 messages and a 3.2 MB transcript, mostly screenshot payloads. The subagent-first policy exists to prevent exactly this.

## Mk3 (round-body redesign)

- Delegating the entire build to one subagent worked: 10 parts, 22-object assembly, verified kit 3MF, and commit in about 19 minutes with zero validity failures, and all screenshot payloads stayed out of the main context (the direct fix for the 3.2 MB transcript problem above).
- The builder caught two geometric impossibilities in the written spec: the taper's straight Ø30.2 x 8.4 cavity would have severed the cone's bottom skirt, and the R2 "wall touches the studs" clutch claim ignored that the studs reach radius 8.06, outside the Ø15.8 part. Lessons: when specifying round clutch geometry, radius-account every feature (stud extent vs cavity wall vs part outline) instead of asserting contact; explicitly authorize builder agents to challenge the spec; and record as-built deviations back into the spec file.
- Round-module constants promoted to [[lego-geometry]].

## Related

- [[lego-geometry]], [[printer-x2d]], [[kelkom-button]]
