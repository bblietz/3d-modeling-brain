---
type: learning
project: Fishing-rod-holder
date: 2026-11-07
status: CAD complete, 3MF built, not printed
tags: [3d-print, retention, hooks, garage, petg]
---

# Fishing rod holder: retrospective (round one, 2026-11-07)

Garage joist rod storage. Brian's two notched 1x4 combs dropped a rod whenever a neighbour was bumped. The replacement is a printed deep-hook pocket, one per rod, screwed to the face of a 1x4 that hangs from the joist as before. See [[../../projects/Fishing-rod-holder/brief|the brief]].

## What worked

- **Diagnose the geometry before drawing fixes.** A half-round notch cut into a vertical edge has its lowest point at the edge, so the rod rests at the mouth with nothing in front of it. Steady state holds by a sliver of slope; any bump frees it. Once that was said in one drawing, every option followed from "put the floor inside the plate behind a lip".
- **One parameter set, three outputs.** `pipeline/concepts.py` held the pocket numbers and drew the to-scale elevations (matplotlib), the concept solids (build123d) and the OpenSCAD scene renders from the same constants; `rod_hook.py` then reused the same numbers for the real part. Nothing on the page disagreed with the CAD.
- **Pose-space hold check as an assert.** `escape_lift(d)` erodes the free space by the rod radius (shapely) and binary-searches the lowest ceiling on the rod centre that still connects the seat to the outside. It returned 1.00 in for 1/4, 3/8 and 5/8 blanks, matching the designed mouth height, and it would have caught a lip that was secretly a ramp. Cost: a few lines. Gotcha: the seat point must sit a hair (0.002 in) above the arc's low point, because the arc is a polygon and the eroded region's lowest vertex lands about 1e-5 above the exact value.
- **OpenSCAD renders of the real STL** (import + context cubes + `rotate([90,0,0])` so model y is up) gave Brian clean pictures of the part on its board and on the joist. The matplotlib iso renders from `render_stl.py` stay as the agent-side check only: a 6 in rod stub made the comb a sliver inside a huge gridded axis box.
- **Real slice numbers on the options page** (`pipeline/slice_stls.py`: flatten presets, CLI export, graft, read `slice_info.config`) settled the material and build decisions without estimates: comb 154 g vs caps 20 g each vs hook 24.6 g.
- **Brian's pick was a blend, not a card.** He took the deep hook (option B) and combined build options A and B into individual hooks on a plain 1x4. Offering the cheap retrofit honestly beside the full print made the hybrid visible.

## What did not

- The first comb concept needed three spliced pieces because 256 mm is 10 in; the hybrid on a wood backbone made the splice problem disappear. Long hanging parts should start from "what carries the length" (wood, rail, extrusion) before a splice design.
- A late `Edit` that appended a function in the middle of `main()` silently swallowed the following block into the new function (indentation). Re-read the tail of a file after inserting a `def` into it.

## Numbers

- Hook 3-1/2 x 3-1/4 x 3/8 in; pocket 7/8 wide, lip 3/4 wide, lift to leave 1 in (lip 5/8 plus a 3/8 slope to the mouth), mouth 1-1/4 tall with 1/4 chamfers, back web 1/8 in so the rod never touches the board. Screws #8 x 1, 1 in from the board edge, 9/16 and 2-11/16 up from the hook bottom, 5 mm holes with a 10 mm 90 degree countersink.
- PETG, 2 walls, 15% infill, 0.30 mm layers, 0.6 nozzle: 24.6 g, 33 min per hook (real slice). Eight hooks 197 g, 4 h 24 min.
- Board layout drawn: hooks at 4 in pitch, bottoms at 4-5/8, 8-5/8, 12-5/8, 16-5/8 in below the joist on the 27 in board; 5 in pitch if reels stay on and line up.

## Still to learn (after the print)

- Does a 3/8 in PETG hook on two #8 screws shrug off a yank on a snagged rod? Expectation: yes by a wide margin.
- Does the 1 in lift feel right overhead, or is the plain 5/8 hook (option A) easier to live with?
- Rod blank diameters at the hook positions, and whether the 7/8 pocket wants to be wider for butt sections.
