---
type: project
project: Fishing-rod-holder
created: 2026-11-07
status: Two open-J hooks in one file, 4 in tall, five butted per 20 in board, printed standing; tip hook 4 x 4 (7/8 slot, 35 degrees) built 2026-11-07, butt hook 4-1/2 x 4 (2 in slot for the grip, 10 degrees, 2-1/4 in to get the butt in under the hook above) built 2026-11-09; 1/32 roundover on the front edges, back face and bottom edge flat (2026-11-09); rod-hook.3mf with solid pads, ONE plate, five pairs (359 g / 7 h 56); not printed.
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

Second version (Brian, 2026-11-09): "There should be 2 versions of the holder. One that we already have is for the rod tip end. The rod butt end should be able to accommodate a 2 in rod handle. The rods I have are 1 7/8 in or so. Make it a 2 in opening." Then: "make both versions in the same file, vertical." Then: "the holders will stack on top of each other, make sure there is 2 in of room to get the butt in" (the stacked gap over the butt hook's lip tip is 2-1/4; the script asserts it at 2 or more).

Count and edges (Brian, 2026-11-09, later): "there should only be 5 pairs" (five tip hooks and five butt hooks, all on one plate). "all edges should have a very slight roundover", then "do not add a round over to the back of the part. Use this flat surface to print the part vertically" (read as: the back face against the board and the bottom edge the standing print sits on stay flat and square; the 1/32 roundover goes on the front face's edges; if the second sentence meant lying the hook on its back to print, that is a layout change, 4 per plate on 3 plates, not a CAD one).

## What exists today (read from the photo)

- Unfinished garage ceiling: exposed joists with a plywood floor above, looks like 2x8 at 16 in on center (to confirm; the 7 in of board above the joist bottom matches a 7-1/4 in 2x8 almost exactly).
- Two wooden combs, each a flat 1x4 screwed to the side face of a joist and hanging straight down. The near one is 27 in overall, 20 in below the joist bottom, with four semicircular notches cut into one edge; the far one is shorter with three notches. The notches open sideways, about 1-1/4 in across, roughly 5 in apart.
- Rods lie horizontally across the two combs, resting in the notches, running across the joists.
- The open garage door sits below the combs, so the hang below the joist is bounded; the current 20 in is the known-good depth.

## Diagnosis

A half-round notch cut into a vertical edge has its lowest point at the board edge, so the rod rolls down the arc and rests at the mouth with nothing in front of it. Steady state holds by a sliver of slope; a bump on a neighbour frees it. The fix is a pocket whose floor sits inside the plate behind a lip at the mouth, so a rod has to rise before it can leave.

## Design as built (2026-11-07)

`rod_hook.py` (build123d, algebra mode; constants in inches, CAD in mm; the outline is one path of lines and true arcs, every corner fillet constructed as an arc, which the CAD builds exactly and the 2D checks sample, so both use the same geometry). One printed hook per rod, screwed to the face of a 1x4 that hangs from the joist like the wooden combs. An open J: a tab over the board and a jaw past its edge.

- Hook 4 x 4 x 3/8 in, corners R 1/4. The tab is 1-3/4 wide and 4 tall on the board face (20 in hang / 5 hooks, so five butted hooks fill the hang with no gap); its outer edge stands 1/8 past the board edge so no blank ever touches the wood. The jaw reaches 2-1/4 past the board edge.
- Slot: 7/8 wide, leaning 35 degrees from vertical away from the wood as it goes down, rounded bottom R 7/16 with its low point 5/8 above the hook's bottom edge. The slot's inner wall (the ramp) leaves the tab's outer edge at 1-7/8 up and runs down and outward; the rod drops in at the top, slides down the ramp away from the board and rests at the bottom, its centre 1.23 in out from the board edge, with the lip's top edge 0.035 in inboard of that centre. To leave it has to come back up the ramp toward the board, then over the lip tip.
- Lip: top 1-7/8 up at the slot, sloping up 3/8 to the tip at 2-1/4 (a rod set on the lip rolls in); 0.58 in thick beside the slot's bottom; tip and slot edges R 1/8.
- No top bar: the jaw stops at the lip top, the tab carries on to 4.
- Screws: two #8 x 1 in, 1 in from the board edge, 9/16 and 3-7/16 up from the hook's bottom edge; 5 mm through holes with a 90 degree countersink to 10 mm on the front face.
- Print orientation: standing on the 4 in bottom edge, face vertical, screw holes horizontal (Brian: print vertically so many fit one plate). Footprint 101.6 x 9.5 mm, 101.6 tall. The steepest overhang is the 35 degree slot lean (the script reads the exported STL layer by layer at 0.3 mm, the way the slicer does, and fails past 45); the bottom edge is flat and square so the print stands on a full strip; the 5 mm holes print as short bridges.
- Edges (2026-11-09): a 1/32 in roundover on the front face's outline and the countersink rims, in one kernel fillet over the true-arc outline; the back face (against the board) and the bottom strip are left square, as Brian asked. The exported STLs are re-saved without the zero-area triangles the fillet's tessellation leaves, so they stay watertight. `rod-hook.stl` is the standing print frame, `rod-hook-model.stl` the flat model frame for the renders. Tradeoff: layers run across the hook, so a sideways yank on the lip loads the layer bond; at rod loads the margin is about 3x.
- Board layout (drawn, `images/board-layout.png`): five hooks butted, the top one starting at the joist bottom, bottoms at 4, 8, 12, 16 and 20 in below the joist on the 27 in board (7 in up the joist, 20 in hang as now); rods rest about 3-3/16 in down, then every 4. Reels left on and in line would want a 5 in pitch, which means four hooks with gaps.
- Stacked, the hook above's bottom edge sits 1-3/4 in over the lip tip below it (4 minus 2-1/4), so a 5/8 blank still passes over the tip with 1-1/8 to spare, and the 1.57 in escape lift fits under it.

Checks baked into the script (all pass, `rod-hook-report.json`): one solid, bounding box, rods of 1/4, 3/8 and 5/8 in seated at the slot's low point touch neither the hook's walls nor the board, the hook sits flat on the board face, slot clears a 5/8 blank by 1/4, walls at or above 1.24 mm, exported STL watertight (63.7 cm3). Pose-space hold check (`escape_lift`): the rod centre must rise 1.57 in for every blank size before any path to the outside opens (1.00 on the plain deep hook, 1.24 on the first angled-floor attempt), and every size can get in and out with no height limit.

Rework history, same day: the first angled slot had its floor dropping toward the board (rod in the back corner, 30 degrees, lift 1.24); Brian wanted the opposite, so the slot became a channel leaning away from the wood.

### Butt hook (2026-11-09)

Same file, same tab, screws, thickness, height and print orientation; `rod_hook.py` now holds both as `TIP` and `BUTT` (a `Hook` object each; the shared numbers stay module constants). The butt hook holds the grip: 2 in opening for Brian's 1-7/8 in handles.

- The 4 in pitch rules the shape. A 1-7/8 grip has to pass between the lip tip and the hook butted 4 in above (the top hook has the joist there instead), so the lip tip can be at most 4 minus the grip minus clearance. Tip at 1-3/4: a 2-1/4 in gap, 3/8 to spare on a 1-7/8 grip and 1/4 on a 2 in one. The lip top starts at 1-5/8 at the slot and climbs 1/8 to the tip (a grip set on the lip still rolls in). What is left under that for the slot is 1-5/8: a 5/16 floor, the R 1 bottom, and a 10 degree lean, the most that leaves the lip a straight inner face above its R 1/8 corner (3/8 floor and 10 degrees left no room for that round; 35 degrees would need about 7 in of hook).
- Hook 4-1/2 x 4 x 3/8 in (jaw reach 2-3/4, lip 0.55 at its thinnest), 58.2 cm3 with the roundover (the tip hook 63.8). Seated 1-7/8 grip centre 1.25 in up and 1.19 in out from the board edge, 1/16 clear of each wall.
- Hold: pose-space lift 1.405 in for 1-1/2, 1-3/4 and 1-7/8 grips (the tip hook gives 1.571 for its blanks), the path being up the 10 degree channel, over the lip tip, under the hook above. The checks now put the hooks above and below and the board in the obstacle set for both versions (the tip hook's numbers did not move), and assert the gap over the tip at a quarter inch past the biggest rod.
- Standing print: footprint 114.3 x 9.5 mm, 101.6 tall; steepest overhang 10 degrees (the slot's outer wall); 30.9 g, 1 h 18 bare in PETG (the tip hook 33.2 g, 1 h 19: the 2 in pocket removes more than the extra half inch adds).
- The hood is gone on this one (the lip's top edge sits 0.96 in outboard of the grip centre): the hold is all lift, which is the only thing a near-vertical 2 in slot can offer in 4 in of height.

## Print

- PETG, 2 walls, 15% infill, 0.30mm Standard, 0.6 nozzle, 2-loop skirt: 33.2 g, 1 h 18 per bare tip hook and 30.9 g, 1 h 19 per bare butt hook standing alone (real slices, `rod-hook-slice-petg.json`, `rod-hook-butt-slice-petg.json`; the tip hook lying flat was 30.0 g, 39 min, so standing costs time per hook but packs ten on a plate).
- `rod-hook.3mf` (`pipeline/make_print_3mf.py`, default 5 copies per hook, report `rod-hook-3mf-report.json`): ONE Bambu project file, ONE plate, five pairs (Brian 2026-11-09: "make both versions in the same file, vertical", then "there should only be 5 pairs"). Plate 1 "tip hooks 1-5, butt hooks 1-5": one row of ten along the bed's y axis at 23 mm pitch, 13.5 mm between faces, the five tip hooks at the back (y 135 to 236) and the five butt hooks in front (y 20 to 121), each hook centred in x: 359.2 g, 7 h 56, 339 layers (35.9 g, 48 min per hook with pads). A 100% infill modifier pad (22 mm, axis along the horizontal hole, inset 0.2 mm from both faces, wholly inside the body: 0.0 mm3 outside against the CAD and the STL, built per variant since the butt hook's holes sit 1/2 in further along the standing part) at every screw hole; G-code proof in the core of the thickness 5 to 9.5 mm above and below each hole centre: 0.873 to 0.89 plastic per volume inside every pad against 0.14 in the plain hook. The plate is authored by the script from the file's own geometry (`PLATES` maps each hook to a plate; `{"tip": 1, "butt": 2}` gives the earlier two-plate layout). Round trip through `bambu-studio --arrange 0 --export-3mf` preserved 1 plate, 10 objects, 20 modifiers, the plate name, the overrides and `different_settings_to_system`. No brim; add one in Studio if a standing hook ever lifts. Brian opens it once in Bambu Studio to confirm the plate shows all ten. Earlier versions for the record: flat tip hooks on three plates 343 g / 7 h 48; standing tip hooks, ten on one plate 372.8 g / 8 h 10; two plates of ten (tip 372.8 g / 8 h 10, butt 346.9 g / 7 h 46) on 2026-11-09 before the count came down to five pairs.
- Mirrored hook: not built; one flag away if a board needs hooks on both edges.

## Options round (2026-11-07, kept for the record)

Published page: https://claude.ai/artifact/MuJqbgWZjUNzqSTMLFRt4H (Version 7: Decided banner with all of Brian's words, both hooks built with renders, the stacked-gap close-up, checks including the roundover and the flat back and bottom, the two-board drilling guide and the one-plate five-pair print file on top; concept round below). Concept slice quotes (PETG, 2 walls, 15%): three-piece printed comb 154 g / 3 h 08 per comb; cap over an existing notch 19.6 g / 28 min. Pocket options drawn: A hook (5/8 lift), B deep hook (1 in lift, picked), C snap clip. Build options drawn: A printed comb in three pieces, B caps on the wood combs; Brian took the blend.

## Open

1. Reels on or off (five butted hooks at 4 in assume reels off or staggered; with the butt hook holding the grip, a reel left on points away from the board), and the comb spacing along the rods. Hook count is settled at five per board, five of each in the 3MF.
1b. Grip sizes: the butt hook's 2 in opening leaves 1/16 per side on a 1-7/8 grip; a fatter foregrip or a reel seat over 2 in will not go in, and the 2-1/4 in gap over the lip tip is what a grip passes through on the way in. Measure the fattest grip before printing the five.
1c. Print orientation reading: "Use this flat surface to print the part vertically" was built as standing on the square bottom edge (one plate). If Brian meant the hooks lying on their flat backs, the 3MF goes to a 2 x 2 grid, 4 per plate, 3 plates, about 6-1/2 h in all, and the roundover on the bottom edge comes back.
2. Joist size (assumed 2x8) only matters for the board, which is Brian's.
3. Copy of the photo into `images/` (it exists only in the chat so far).
4. After the print: real blank fit in the 7/8 pocket and the feel of the 1 in lift (retrospective in `knowledge/learnings/fishing-rod-holder.md`).

## Files

- `rod_hook.py` (canonical CAD for both hooks with asserts and the SHOW viewer push), tip hook `rod-hook.stl` / `rod-hook-model.stl` / `rod-hook-report.json` / `rod-hook-slice-petg.json`, butt hook `rod-hook-butt.stl` / `rod-hook-butt-model.stl` / `rod-hook-butt-report.json` / `rod-hook-butt-slice-petg.json`, the one print file `rod-hook.3mf` with `rod-hook-3mf-report.json`
- `pipeline/concepts.py` (concept geometry and drawings), `pipeline/renders.py` (OpenSCAD scenes of the real STL and the board layout), `pipeline/slice_stls.py` (STL to grams and time), `pipeline/options_page.py` (page generator), `pipeline/make_print_3mf.py` (project 3MF with pads)
- `images/` (hook-on-board, butt-hook-on-board, board-in-place, pocket-face-on, butt-pocket-face-on, board-layout, hook-check-views, butt-hook-check-views), `images/concepts/` (options round)
- `options.html` (published page), `concepts-slice-petg.json`
- `knowledge/learnings/fishing-rod-holder.md` (retrospective), `.claude/context-check/last-handoff.md`
