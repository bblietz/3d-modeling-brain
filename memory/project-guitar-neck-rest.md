---
name: project-guitar-neck-rest
description: "Printed bench neck rest for Brian's guitar and bass; BUILT 2026-11-23, not printed: open-frame rocker, rounded edges, cork pad seat, one channel for his 2 in rubber grip tape; one-plate 3MF 167.5 g / 2 h 21 PLA; waiting on his look in Studio"
metadata:
  node_type: memory
  type: project
  originSessionId: 61ead13b-5621-4652-9a82-a98acabf295e
  modified: 2026-11-23T21:19:05.395Z
---

Guitar neck rest (bench tool that holds the neck while the instrument lies on its back). Brainstormed 2026-11-22 to 23 under superpowers: rocker (round 1), open-frame body C1 (round 2), 4-3/8 in cradle kept over longer ones (round 3). 2026-11-23: go on the design, then three notes from Brian: the two cradle ends rounded over (confirmed by a question as the ends the neck passes over), a slight roundover on every other edge, and one recessed channel in the bottom for his 2 in wide rubber grip tape (replacing my two tread strips). Spec approved with "Yes, build it".

Built the same day in `projects/Guitar-neck-rest/`: `neck_rest.scad` (OpenSCAD, slices joined by hulls), `guitar-neck-rest.stl`, `guitar-neck-rest.3mf` (one plate, PLA, 2 walls, 15%, seam back, Textured PEI 65 C; 167.5 g, 2 h 21 min), checks in `pipeline/build.py` and `pipeline/make_print_3mf.py`. Size 5-7/8 x 3-1/8 x 4-1/4 in, neck at 3-3/4 in on a 1/16 in cork pad (cut 2-3/4 x 4-1/8 in), tape cut 2 x 5-1/2 in. My calls: 1/4 in and 1/16 in roundovers, channel 0.5 mm deep (his tape thickness is not known), cork, light-duty PLA. Page Version 6. Not printed, not opened in Studio by him. Committed to main 2026-11-23.

**Why:** Brian answers shape questions against pictures and leaves the rest to stated defaults; he keeps adding design notes after saying go, so a go from him is not the end of design input.

**How to apply:** Read `projects/Guitar-neck-rest/brief.md` ("The build") and `.claude/context-check/last-handoff.md` there first. Do not reopen the body or cradle length. Open items: his look at the plate-side 1/16 in roundover in Studio's preview (fallback a small bevel on that side), his tape's thickness against the 0.5 mm channel, then the print and measured fits into `knowledge/learnings/guitar-neck-rest.md`. Rebuild chain: constants in `neck_rest.scad`, `build.py`, `make_print_3mf.py`, `options_page.py`, republish. For his short ambiguous notes ask one plain-words question, then draw the answer. Follow [[feedback-html-visual-companion]]; roundover technique in [[feedback-roundovers-as-slices]].
