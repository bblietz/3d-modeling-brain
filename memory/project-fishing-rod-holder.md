---
name: project-fishing-rod-holder
description: "Garage joist rod storage; Brian picked individual deep hooks on a 1x4 (2026-11-07), then had the slot lean AWAY from the wood, the top bar removed, five hooks butted per 20 in board, printed standing; open-J PETG hook built (4 x 4 x 3/8, lift 1.57 in), 10 hooks on one plate with solid pads (373 g); not printed"
metadata:
  node_type: memory
  type: project
  originSessionId: 3f3590ae-4308-446d-b672-0d51f52c10fb
  modified: 2026-11-08T06:55:16.600Z
---

Brian's garage has two wooden combs (1x4 on edge, screwed to the side face of exposed 2x8-looking joists, 27 in long, 20 in hang, half-round 1-1/4 in notches at about 5 in) holding rods horizontally above the open garage door. Rods stay at rest but any bump while pulling a neighbour drops one: a half-round in a vertical edge has its low point at the board edge.

Decided 2026-11-07: "use the deep hook design", "make individual deep hooks, that can be screwed into a 1x4 piece of wood" (a blend of the printed comb and the caps-on-wood option); then "make the bottom resting part of the hook have a slot that is angled", "remove the top most part of the device that is not over the wood", correcting my first attempt, "the slot should angle away from the wood", and "5 holders should fit in the 20 in, no space between each hook as it sits on the wood". Built the same day: `projects/Fishing-rod-holder/rod_hook.py`, an open J 4 x 4 x 3/8 in (height = 20 in hang / 5): tab on the board with two #8 x 1 screws 1 in from the edge, jaw 2-1/4 past the edge with a 7/8 slot leaning 35 degrees away from the wood (rod slides down the ramp outward and rests under the lip's edge; to leave it comes back up toward the board then over the 2-1/4 in tip); lift to leave 1.57 in for 1/4 to 5/8 blanks (pose-space check in the script). PETG 2 walls 15%: `rod-hook.3mf` with all 10 hooks standing in a row on ONE plate, 373 g / 8 h 10 (37 g, 49 min each with pads), pads proven 0.88 vs 0.14. Options page https://claude.ai/artifact/MuJqbgWZjUNzqSTMLFRt4H (Version 5) carries the built section and the concept round. Not printed; five butted hooks per board (bottoms 4, 8, 12, 16, 20 below the joist) assume reels off or staggered; comb spacing still unknown.

Printed standing on the 4 in bottom edge (Brian: "print these vertically so there can be much more in a single print"), ten to a plate; `rod-hook.stl` is the standing frame, `rod-hook-model.stl` the flat one for renders; max overhang 35 degrees, bottom corners square.

**How to apply:** when Brian says a slot or hook is "angled", state which way the low end goes before building (this cost one cycle). After the print, record the real blank fit and the feel of the up-and-out motion in `knowledge/learnings/fishing-rod-holder.md`; a mirrored hook is one line away if a board needs both edges. Related: [[feedback-html-visual-companion]], [[feedback-ask-load-case-before-walls]], [[feedback-check-docking-and-hold-kinematics]], [[feedback-verify-retention-features-closeup]], [[feedback-solid-infill-at-screw-holes]].
