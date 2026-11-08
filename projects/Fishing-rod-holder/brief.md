---
type: project
project: Fishing-rod-holder
created: 2026-11-07
status: Deep hook on a 1x4 built, checked and exported 2026-11-07 (rod_hook.py, rod-hook.stl, PETG 24.6 g per hook); 3MF with solid pads built by pipeline/make_print_3mf.py; not printed.
printer: Bambu Lab X2D
material: PETG
tags: [3d-print, garage, fishing, storage]
---

# Fishing rod holder (garage rafter)

## Request (Brian, 2026-11-07)

"Lets create a new project for a fishing rod holder." "The holder will hang from a rafter in my garage." Then a photo of the current wooden holders: "This is a picture of the wooden ones I have now. They don't work well at all. The longer one is 20 in from the bottom of the rafter, 27 in overall."

What fails (Brian, same day): "rods fall out when minimal force is applied. They stay in at steady state. They fall out when I am trying to get other rods out of the holder. Any bump on another rod makes it fall out."

Picks (Brian, same day, from the options page): "use the deep hook design. For decision 2, combine the approach. Make individual deep hooks, that can be screwed into a 1x4 piece of wood."

## What exists today (read from the photo)

- Unfinished garage ceiling: exposed joists with a plywood floor above, looks like 2x8 at 16 in on center (to confirm; the 7 in of board above the joist bottom matches a 7-1/4 in 2x8 almost exactly).
- Two wooden combs, each a flat 1x4 screwed to the side face of a joist and hanging straight down. The near one is 27 in overall, 20 in below the joist bottom, with four semicircular notches cut into one edge; the far one is shorter with three notches. The notches open sideways, about 1-1/4 in across, roughly 5 in apart.
- Rods lie horizontally across the two combs, resting in the notches, running across the joists.
- The open garage door sits below the combs, so the hang below the joist is bounded; the current 20 in is the known-good depth.

## Diagnosis

A half-round notch cut into a vertical edge has its lowest point at the board edge, so the rod rolls down the arc and rests at the mouth with nothing in front of it. Steady state holds by a sliver of slope; a bump on a neighbour frees it. The fix is a pocket whose floor sits inside the plate behind a lip at the mouth, so a rod has to rise before it can leave.

## Design as built (2026-11-07)

`rod_hook.py` (build123d, algebra mode; constants in inches, CAD in mm). One printed hook per rod, screwed to the face of a 1x4 that hangs from the joist like the wooden combs.

- Hook 3-1/2 x 3-1/4 x 3/8 in, corners R 1/4. It reaches 1-3/4 in past the board edge; the rod lies in the pocket beside the wood with a 1/8 in web between the pocket's back wall and the board edge, so no blank ever touches the board.
- Deep-hook pocket: pocket 7/8 wide (U bottom R 7/16), floor 5/8 above the hook's bottom edge; lip 3/4 wide, its top 5/8 above the floor; the channel floor slopes up 3/8 from the lip to the mouth, so the mouth floor is 1 in above the pocket floor (the lift to leave) and a rod rolls into the pocket by itself; mouth 1-1/4 tall at the mouth; 1/4 in chamfers at both mouth corners.
- Screws: two #8 x 1 in, 1 in from the board edge, 9/16 and 2-11/16 up from the hook's bottom edge; 5 mm through holes with a 90 degree countersink to 10 mm on the front face.
- Print orientation: flat, back face on the bed, countersinks up. No overhangs.
- Board layout (drawn, `images/board-layout.png`): hooks at 4 in pitch, bottoms at 4-5/8, 8-5/8, 12-5/8 and 16-5/8 in below the joist on the 27 in board (7 in up the joist, 20 in hang as now). 5 in pitch if reels stay on and line up.

Checks baked into the script (all pass, `rod-hook-report.json`): one solid, bounding box, seated rods of 1/4, 3/8 and 5/8 in intersect neither the hook nor the board, the hook sits flat on the board face, mouth clears a 5/8 blank by 5/8, walls at or above 1.24 mm, exported STL watertight (50.8 cm3). Pose-space hold check (`escape_lift`): the rod centre must rise 1.00 in for every blank size before any path to the outside opens, and every size can get in and out with no height limit.

## Print

- PETG, 2 walls, 15% infill, 0.30mm Standard, 0.6 nozzle, 2-loop skirt: 24.6 g, 33 min per hook (real slice, `rod-hook-slice-petg.json`). Eight hooks 197 g, 4 h 24 min.
- `rod-hook.3mf`: Bambu project file, eight hooks, a 100% infill modifier pad (22 mm) at every screw hole, proven in the sliced G-code (`rod-hook-3mf-report.json`). Brian opens it once in Bambu Studio to confirm the plates.
- Mirrored hook: not built; one flag away if a board needs hooks on both edges.

## Options round (2026-11-07, kept for the record)

Published page: https://claude.ai/artifact/MuJqbgWZjUNzqSTMLFRt4H (now with the Decided banner and the built section on top). Concept slice quotes (PETG, 2 walls, 15%): three-piece printed comb 154 g / 3 h 08 per comb; cap over an existing notch 19.6 g / 28 min. Pocket options drawn: A hook (5/8 lift), B deep hook (1 in lift, picked), C snap clip. Build options drawn: A printed comb in three pieces, B caps on the wood combs; Brian took the blend.

## Open

1. Rod inventory: how many hooks to print, reels on or off (sets the pitch), comb spacing along the rods.
2. Joist size (assumed 2x8) only matters for the board, which is Brian's.
3. Copy of the photo into `images/` (it exists only in the chat so far).
4. After the print: real blank fit in the 7/8 pocket and the feel of the 1 in lift (retrospective in `knowledge/learnings/fishing-rod-holder.md`).

## Files

- `rod_hook.py` (canonical CAD with asserts and the SHOW viewer push), `rod-hook.stl`, `rod-hook.3mf`, `rod-hook-report.json`, `rod-hook-slice-petg.json`, `rod-hook-3mf-report.json`
- `pipeline/concepts.py` (concept geometry and drawings), `pipeline/renders.py` (OpenSCAD scenes of the real STL and the board layout), `pipeline/slice_stls.py` (STL to grams and time), `pipeline/options_page.py` (page generator), `pipeline/make_print_3mf.py` (project 3MF with pads)
- `images/` (hook-on-board, board-in-place, pocket-face-on, board-layout, hook-check-views), `images/concepts/` (options round)
- `options.html` (published page), `concepts-slice-petg.json`
- `knowledge/learnings/fishing-rod-holder.md` (retrospective), `.claude/context-check/last-handoff.md`
