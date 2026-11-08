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

- **"Angled" has a direction.** Brian asked for an angled resting slot; I sloped the floor down toward the board (rod in the back corner). He meant the slot should lean away from the wood (rod tucked outward under the lip, coming back up the ramp to leave). Before building a tilt, state which way the low end goes in one sentence or draw both and ask. The rework cost one full cycle (CAD, renders, slice, page).
- A build123d `fillet()` loop on hand-picked vertical edges worked but made the 2D check approximate its radii; constructing every fillet as an arc in the outline polygon (`rounded_outline`) and extruding that gave one source of truth for the CAD, the STL and the shapely checks. With a leaning slot the geometry is a handful of trig lines (`S_IN`, `X_C`, `S_OUT`, `X_LIP_TOP`), all derived from the lean, the slot width and the lip height.
- The 3MF builder ran while the STL kept changing. Because it reads the constants and the STL at run time, re-running it on the final hook took 12 s plus the proof slice. Keep print-file builders parameter-free and re-runnable; never bake geometry numbers into them.

## Numbers

- Hook 4 x 4 x 3/8 in (tab 1-3/4 wide and 4 tall on the board so five butted hooks fill the 20 in hang, jaw 2-1/4 past the edge). Slot 7/8 wide leaning 35 degrees from vertical away from the wood, rounded bottom R 7/16 with its low point 5/8 up; ramp leaves the tab edge 1-7/8 up; lip top 1-7/8 sloping to a 2-1/4 tip, lip 0.58 at its thinnest; 1/8 web keeps the rod off the wood. Lift to leave 1.57 in for 1/4, 3/8 and 5/8 blanks (plain deep hook 1.00; the wrong-way angled floor 1.24). Screws #8 x 1, 1 in from the board edge, 9/16 and 3-7/16 up from the hook bottom, 5 mm holes with a 10 mm 90 degree countersink.
- PETG, 2 walls, 15% gyroid, 0.30 mm layers, 0.6 nozzle: 30.0 g, 39 min per bare hook; in the 3MF with pads 34.3 g. `rod-hook.3mf`: 10 hooks on 3 plates (4, 4, 2), 137.3 g / 3 h 06, 137.3 g / 3 h 05, 68.7 g / 1 h 36, total 343 g / 7 h 48. Pads: 0.85 plastic per volume vs 0.15 plain, all 20.
- Board layout drawn: five hooks butted, the top one at the joist bottom, bottoms at 4, 8, 12, 16, 20 in below the joist on the 27 in board (rods about 3-3/16 down, then every 4); reels on and in line would want 5 in, i.e. four hooks with gaps.
- Brian sizes by the board: "5 holders should fit in the 20 in, no space between each hook" fixed the hook height at hang / count. Ask for the count and the hang before fixing a tab height; the pitch falls out of it.

## Still to learn (after the print)

- Does a 3/8 in PETG hook on two #8 screws shrug off a yank on a snagged rod? Expectation: yes by a wide margin.
- Does the up-the-ramp-then-out motion (1.57 in of lift) feel right overhead, or is it fiddly with a reel on?
- Rod blank diameters at the hook positions, and whether the 7/8 pocket wants to be wider for butt sections.
