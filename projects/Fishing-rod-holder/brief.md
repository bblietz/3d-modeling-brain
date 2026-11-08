---
type: project
project: Fishing-rod-holder
created: 2026-11-07
status: Open-J hook, 4 x 4 x 3/8, slot leaning away from the wood, five butted per 20 in board, printed standing; built, checked and exported 2026-11-07 (rod_hook.py, rod-hook.stl); rod-hook.3mf with solid pads, 10 hooks on ONE plate, 373 g / 8 h 10; not printed.
printer: Bambu Lab X2D
material: PETG
tags: [3d-print, garage, fishing, storage]
---

# Fishing rod holder (garage rafter)

## Request (Brian, 2026-11-07)

"Lets create a new project for a fishing rod holder." "The holder will hang from a rafter in my garage." Then a photo of the current wooden holders: "This is a picture of the wooden ones I have now. They don't work well at all. The longer one is 20 in from the bottom of the rafter, 27 in overall."

What fails (Brian, same day): "rods fall out when minimal force is applied. They stay in at steady state. They fall out when I am trying to get other rods out of the holder. Any bump on another rod makes it fall out."

Picks (Brian, same day, from the options page): "use the deep hook design. For decision 2, combine the approach. Make individual deep hooks, that can be screwed into a 1x4 piece of wood."

Rework (Brian, same day, after seeing the first hook): "make the bottom resting part of the hook have a slot that is angled to help keep the rod there better" and "remove the top most part of the device that is not over the wood. It isn't needed." Then, on the first attempt: "you did the opposite angle for the slot. The slot should angle away from the wood." Then: "5 holders should fit in the 20 in. There should be no space between each hook as it sits on the wood." Then: "can you print these vertically so there can be much more in a single print."

## What exists today (read from the photo)

- Unfinished garage ceiling: exposed joists with a plywood floor above, looks like 2x8 at 16 in on center (to confirm; the 7 in of board above the joist bottom matches a 7-1/4 in 2x8 almost exactly).
- Two wooden combs, each a flat 1x4 screwed to the side face of a joist and hanging straight down. The near one is 27 in overall, 20 in below the joist bottom, with four semicircular notches cut into one edge; the far one is shorter with three notches. The notches open sideways, about 1-1/4 in across, roughly 5 in apart.
- Rods lie horizontally across the two combs, resting in the notches, running across the joists.
- The open garage door sits below the combs, so the hang below the joist is bounded; the current 20 in is the known-good depth.

## Diagnosis

A half-round notch cut into a vertical edge has its lowest point at the board edge, so the rod rolls down the arc and rests at the mouth with nothing in front of it. Steady state holds by a sliver of slope; a bump on a neighbour frees it. The fix is a pocket whose floor sits inside the plate behind a lip at the mouth, so a rod has to rise before it can leave.

## Design as built (2026-11-07)

`rod_hook.py` (build123d, algebra mode; constants in inches, CAD in mm; the outline is one polygon with every fillet constructed as an arc, so the 2D checks use the very points the CAD extrudes). One printed hook per rod, screwed to the face of a 1x4 that hangs from the joist like the wooden combs. An open J: a tab over the board and a jaw past its edge.

- Hook 4 x 4 x 3/8 in, corners R 1/4. The tab is 1-3/4 wide and 4 tall on the board face (20 in hang / 5 hooks, so five butted hooks fill the hang with no gap); its outer edge stands 1/8 past the board edge so no blank ever touches the wood. The jaw reaches 2-1/4 past the board edge.
- Slot: 7/8 wide, leaning 35 degrees from vertical away from the wood as it goes down, rounded bottom R 7/16 with its low point 5/8 above the hook's bottom edge. The slot's inner wall (the ramp) leaves the tab's outer edge at 1-7/8 up and runs down and outward; the rod drops in at the top, slides down the ramp away from the board and rests at the bottom, its centre 1.23 in out from the board edge, with the lip's top edge 0.035 in inboard of that centre. To leave it has to come back up the ramp toward the board, then over the lip tip.
- Lip: top 1-7/8 up at the slot, sloping up 3/8 to the tip at 2-1/4 (a rod set on the lip rolls in); 0.58 in thick beside the slot's bottom; tip and slot edges R 1/8.
- No top bar: the jaw stops at the lip top, the tab carries on to 4.
- Screws: two #8 x 1 in, 1 in from the board edge, 9/16 and 3-7/16 up from the hook's bottom edge; 5 mm through holes with a 90 degree countersink to 10 mm on the front face.
- Print orientation: standing on the 4 in bottom edge, face vertical, screw holes horizontal (Brian: print vertically so many fit one plate). Footprint 101.6 x 9.5 mm, 101.6 tall. The steepest unsupported surface is the 35 degree slot lean (the script measures it on the exported STL and fails past 45); the bottom corners are square because a rounded bottom edge is an overhang when standing; the 5 mm holes print as short bridges. `rod-hook.stl` is the standing print frame, `rod-hook-model.stl` the flat model frame for the renders. Tradeoff: layers run across the hook, so a sideways yank on the lip loads the layer bond; at rod loads the margin is about 3x.
- Board layout (drawn, `images/board-layout.png`): five hooks butted, the top one starting at the joist bottom, bottoms at 4, 8, 12, 16 and 20 in below the joist on the 27 in board (7 in up the joist, 20 in hang as now); rods rest about 3-3/16 in down, then every 4. Reels left on and in line would want a 5 in pitch, which means four hooks with gaps.
- Stacked, the hook above's bottom edge sits 1-3/4 in over the lip tip below it (4 minus 2-1/4), so a 5/8 blank still passes over the tip with 1-1/8 to spare, and the 1.57 in escape lift fits under it.

Checks baked into the script (all pass, `rod-hook-report.json`): one solid, bounding box, rods of 1/4, 3/8 and 5/8 in seated at the slot's low point touch neither the hook's walls nor the board, the hook sits flat on the board face, slot clears a 5/8 blank by 1/4, walls at or above 1.24 mm, exported STL watertight (63.7 cm3). Pose-space hold check (`escape_lift`): the rod centre must rise 1.57 in for every blank size before any path to the outside opens (1.00 on the plain deep hook, 1.24 on the first angled-floor attempt), and every size can get in and out with no height limit.

Rework history, same day: the first angled slot had its floor dropping toward the board (rod in the back corner, 30 degrees, lift 1.24); Brian wanted the opposite, so the slot became a channel leaning away from the wood.

## Print

- PETG, 2 walls, 15% infill, 0.30mm Standard, 0.6 nozzle, 2-loop skirt: 33.2 g, 1 h 19 per bare hook standing alone (real slice, `rod-hook-slice-petg.json`; the same hook lying flat was 30.0 g, 39 min, so standing costs time per hook but packs ten on a plate).
- `rod-hook.3mf` (`pipeline/make_print_3mf.py`, default 10 copies, report `rod-hook-3mf-report.json`): Bambu project file, ten hooks (two boards of five) standing in one row along the bed's y axis on ONE plate, 23 mm pitch, 13.5 mm between faces: 372.8 g, 8 h 10 min, 339 layers (37.3 g and 49 min per hook, pads included). Earlier flat version for comparison: three plates, 343 g, 7 h 48. A 100% infill modifier pad (22 mm, axis along the horizontal hole, inset 0.2 mm from both faces, wholly inside the body: 0.0 mm3 outside against the CAD and the STL) at every screw hole; G-code proof in the core of the thickness 5 to 9.5 mm above and below each hole centre: 0.875 to 0.89 plastic per volume inside every pad against 0.14 in the plain hook. Round trip through `bambu-studio --arrange 0 --export-3mf` preserved the plate, 10 objects, 20 modifiers, the overrides and `different_settings_to_system`. No brim; add one in Studio if a standing hook ever lifts. Brian opens it once in Bambu Studio to confirm the plate shows.
- Mirrored hook: not built; one flag away if a board needs hooks on both edges.

## Options round (2026-11-07, kept for the record)

Published page: https://claude.ai/artifact/MuJqbgWZjUNzqSTMLFRt4H (Version 5: Decided banner, the built hook with renders, checks, drilling guide and the one-plate print file on top; concept round below). Concept slice quotes (PETG, 2 walls, 15%): three-piece printed comb 154 g / 3 h 08 per comb; cap over an existing notch 19.6 g / 28 min. Pocket options drawn: A hook (5/8 lift), B deep hook (1 in lift, picked), C snap clip. Build options drawn: A printed comb in three pieces, B caps on the wood combs; Brian took the blend.

## Open

1. Reels on or off (five butted hooks at 4 in assume reels off or staggered), and the comb spacing along the rods. Hook count is settled at five per board, ten in the 3MF.
2. Joist size (assumed 2x8) only matters for the board, which is Brian's.
3. Copy of the photo into `images/` (it exists only in the chat so far).
4. After the print: real blank fit in the 7/8 pocket and the feel of the 1 in lift (retrospective in `knowledge/learnings/fishing-rod-holder.md`).

## Files

- `rod_hook.py` (canonical CAD with asserts and the SHOW viewer push), `rod-hook.stl`, `rod-hook.3mf`, `rod-hook-report.json`, `rod-hook-slice-petg.json`, `rod-hook-3mf-report.json`
- `pipeline/concepts.py` (concept geometry and drawings), `pipeline/renders.py` (OpenSCAD scenes of the real STL and the board layout), `pipeline/slice_stls.py` (STL to grams and time), `pipeline/options_page.py` (page generator), `pipeline/make_print_3mf.py` (project 3MF with pads)
- `images/` (hook-on-board, board-in-place, pocket-face-on, board-layout, hook-check-views), `images/concepts/` (options round)
- `options.html` (published page), `concepts-slice-petg.json`
- `knowledge/learnings/fishing-rod-holder.md` (retrospective), `.claude/context-check/last-handoff.md`
