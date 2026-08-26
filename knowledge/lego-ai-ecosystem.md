---
tags: [reference, lego, ecosystem, mcp, skills]
researched: 2026-07-30
---

# LEGO + AI ecosystem survey

Four parallel research sweeps on 2026-07-30: Claude skills, MCP servers, LEGO CAD/data ecosystem, and printer control (the last in [[x2d-printer-control]]). Headline: **no LEGO-specific Claude skill exists anywhere** (Anthropic's skills repo, all marketplaces, GitHub code search). This vault's [[lego-geometry]] constants are ahead of anything published.

## Adopt now (high value, low effort)

- [Rebrickable CSV dumps](https://rebrickable.com/downloads/): the whole LEGO catalog (parts, sets, colors, inventories) as daily gzip CSVs, no auth. A local SQLite from these answers "what parts exist / what is in set X" offline. API is 1 req/s per key; use dumps for bulk.
- [LeoCAD](https://www.leocad.org/) (GPLv2, Linux): full headless CLI (`leocad -i out.png` with step ranges, camera angles, orthographic). Emit a trivial LDR file (type-1 lines on the 20-LDU grid, 1 LDU = 0.4 mm, -Y up) and get step-by-step instruction renders free. [LPub3D](https://trevorsandy.github.io/lpub3d/) adds PDF instructions and BOM pages.
- [brick-mcp](https://github.com/datakurre/brick-mcp): MCP that reads/writes BrickLink Studio .io and LDraw files (parts, BOMs, steps, edits). The only real "LEGO CAD for Claude" tool.
- [build123d-mcp](https://github.com/pzfreo/build123d-mcp): measurement, printability, and fit/alignment verification tools that freecad-mcp lacks; directly relevant to clutch-tolerance work.
- [bambu-printer-mcp](https://github.com/DMontgomery40/bambu-printer-mcp): closes design-to-print on the X2D; details in [[x2d-printer-control]].

## Ideas to steal (no code needed)

- **Clutch by compliance, not interference**: PELA Blocks puts flexure chambers inside studs/connectors; printpal Brick Builder uses 0.24 mm clamp ridges on cavity walls that grip stud sides. Both make clutch less sensitive to the exact +0.1 mm cavity compensation. Candidate upgrade for [[lego-geometry]].
- **Measured clutch target**: real LEGO stud separation is about 0.7 N per stud; 0.5 to 1 N is the acceptance window (Cambridge Design Science, CC BY, tested on FDM). A luggage-scale pull test makes this a verifiable criterion.
- **Labeled calibration ladders**: generate a test strip of cavities from loose to tight (lapinoo L5..T5 pattern; PELA calibration beam) instead of one-at-a-time fit tests.
- **Stability check with rollback**: BrickGPT (CMU, MIT license, 47k-structure dataset) validates physics during generation, 98.8 percent stable vs 24 percent without. A connectivity/stability gate would fit our verification loop.
- **Vision decomposition before building** (jarvis-onshape-mcp SKILL.md): structured image-to-feature decomposition with review before CAD; matches the Kelkom lesson in [[kelkom-button]].
- **Brickify the bulk** (faBrickation, CHI 2014): auto-substitute model volume with standard bricks, print only the special geometry; automatable with Rebrickable data + our constants.

## LDraw parts library (use with care)

17,052 parts, CC BY 4.0 / CC0, convertible to STL (LDView export is best quality; PrintABrick proved the pipeline at library scale with ADMesh repair). But the meshes are visual-grade open shells: no FDM compensation, studs hard-modeled at 4.8 mm, no inter-brick play. Use for exotic shapes not worth remodeling, then re-cut mating interfaces parametrically; [[lego-geometry]] stays the source of truth for fits.

## Watch

- [BrickBuilderMCP](https://github.com/jonx/BrickBuilderMCP): 57 tools, physics-validated LDraw building against a 24k-part catalog; new, ambitious, stud-only connections so far.
- [ldraw-mcp](https://github.com/musharna/ldraw-mcp): renders LDraw via Blender for visual verification; needs Blender.
- [spkane/freecad-addon-robust-mcp-server](https://github.com/spkane/freecad-addon-robust-mcp-server): 150+ tool rewrite of freecad-mcp, protocol compatible, native export_3mf; candidate upgrade to our bridge.
- [Kiln](https://github.com/codeofaxel/Kiln): 880-tool freemium print orchestrator; account gravity, X2D not listed yet.
- Prompt-to-Parts (arXiv 2512.15743): LLM + tools + LDraw producing valid assembly sequences at 3k-part scale; no public code yet, worth reading.

## Skip / avoid

- BrickLink Studio automation: Windows/macOS only, closed .io format, no CLI, no STL export.
- jhacksman/OpenSCAD-MCP-Server: 174 stars but a one-day experiment abandoned 2025-03.
- offthehook-implication870/bambu-printer-mcp: unattributed clone of the real one.
- Thingiverse MCP (dead), MakerWorld (no official API, scrapers only).
- License traps if models are ever sold: MachineBlocks is CC BY-NC-SA, flowful cad-skill is PolyForm Noncommercial, PELA is CC BY-SA (share-alike).

## Related

- [[lego-geometry]], [[x2d-printer-control]], [[printer-x2d]], [[lego-3d-test]]
