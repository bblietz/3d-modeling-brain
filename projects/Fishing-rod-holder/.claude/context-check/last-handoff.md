# Handoff: Fishing rod holder (2026-11-09, butt hook added)

## Where it stands

Two open-J rod hooks in one file, both 4 in tall and 3/8 thick on the same tab and screws, printed standing: the TIP hook (4 x 4, 7/8 slot leaning 35 degrees, blanks 1/4 to 5/8, as built 2026-11-07) and the BUTT hook (4-1/2 x 4, 2 in slot leaning 10 degrees for the grip, Brian's are about 1-7/8). `rod-hook.3mf` is ONE project file with TWO plates: plate 1 ten tip hooks (372.8 g, 8 h 10), plate 2 ten butt hooks (346.9 g, 7 h 46), 719.7 g and 15 h 56 in all, solid screw pads proven in the G-code on both plates (0.87 to 0.89 vs 0.14), round trip keeps both plates. Options page Version 6 (Decided banner, both hooks built and checked, two-board renders and drilling guide, the two-plate table): https://claude.ai/artifact/MuJqbgWZjUNzqSTMLFRt4H. Nothing printed. The OCP viewer window has both hooks pushed (tip on its stub, butt 8 in to the right with a 1-7/8 grip).

## Decisions already locked

- Pocket: deep hook (Brian, "use the deep hook design"), then reworked on his asks: an angled resting slot that leans AWAY from the wood (he corrected the first attempt, which sloped toward the board), and no top bar past the wood ("remove the top most part of the device that is not over the wood").
- Build: individual printed hooks screwed to the face of a 1x4 ("make individual deep hooks, that can be screwed into a 1x4 piece of wood").
- Count and pitch: "5 holders should fit in the 20 in, no space between each hook as it sits on the wood" (Brian). Hook height = 20 / 5 = 4 in; five butted, the top one at the joist bottom, bottoms at 4, 8, 12, 16, 20. Ten of each in the 3MF (two tip boards' worth and two butt boards' worth, or one of each plus spares; Brian's call).
- Two versions (Brian 2026-11-09): "There should be 2 versions of the holder. One that we already have is for the rod tip end. The rod butt end should be able to accommodate a 2 in rod handle. The rods I have are 1 7/8 in or so. Make it a 2 in opening." "Make both versions in the same file, vertical." "The holders will stack on top of each other, make sure there is 2 in of room to get the butt in." The butt hook's slot is 2.0 in wide; the gap between its lip tip and the hook stacked above is 2-1/4 in (asserted at 2 or more, `min_exit_gap`).
- Tip hook geometry as built: 4 x 4 x 3/8; tab 1-3/4 wide on the board, jaw 2-1/4 past the edge; slot 7/8 leaning 35 degrees, rounded bottom R 7/16 with its low point 5/8 up; ramp leaves the tab edge at 1-7/8; lip top 1-7/8 sloping to a 2-1/4 tip; 1/8 web off the wood. Lift to leave 1.57 in for 1/4 to 5/8 blanks.
- Butt hook geometry as built: 4-1/2 x 4 x 3/8; jaw 2-3/4 past the edge; slot 2 in leaning 10 degrees, rounded bottom R 1 with its low point 5/16 up; ramp leaves the tab edge at 1-5/8; lip top 1-5/8 sloping 1/8 to a 1-3/4 tip, lip 0.55 at its thinnest. The 4 in pitch set it: lip tip + grip + clearance <= 4, so the tip is at 1-3/4 (2-1/4 in gap), and 10 degrees is the most lean that leaves the lip a straight inner face above its R 1/8 corner (a 3/8 floor failed the fillet assert; 5/16 passes). Lift to leave 1.405 in for 1-1/2 to 1-7/8 grips; no hood on this one, the hold is all lift.
- Shared: two #8 x 1 screws 1 in from the board edge at 9/16 and 3-7/16 up, 5 mm holes with 10 mm countersinks (same drilling on both boards). Material and process: PETG, 2 walls, 15% gyroid, 0.30mm Standard, 0.6 nozzle, 2-loop skirt, no brim. Standing on the 4 in bottom edge, face vertical, holes horizontal; bottom corners square; overhang 35 degrees (tip) and 10 (butt).
- Checks: the pose-space hold check now has the hooks butted above and below and the board in the obstacle set for both versions; the tip hook's numbers did not change.
- Every screw hole has a 100% infill modifier pad (22 mm, inset 0.2 mm), proven on both plates.

## Files

- `rod_hook.py` (both hooks as `TIP` and `BUTT`, a `Hook` object each; asserts; SHOW viewer push), `rod-hook.stl` / `rod-hook-model.stl` / `rod-hook-report.json` / `rod-hook-slice-petg.json` (tip), `rod-hook-butt.stl` / `rod-hook-butt-model.stl` / `rod-hook-butt-report.json` / `rod-hook-butt-slice-petg.json` (butt), `rod-hook.3mf`, `rod-hook-3mf-report.json`
- `pipeline/concepts.py` (concept round), `pipeline/renders.py` (OpenSCAD scenes for both hooks and both boards, the two-board drilling guide), `pipeline/slice_stls.py`, `pipeline/options_page.py`, `pipeline/make_print_3mf.py` (two plates, a variant per plate)
- `images/` (hook-on-board, butt-hook-on-board, board-in-place, pocket-face-on, butt-pocket-face-on, board-layout, hook-check-views, butt-hook-check-views; `images/concepts/` for the options round)
- `options.html`, `brief.md`, `knowledge/learnings/fishing-rod-holder.md`

## Next

1. Brian opens `rod-hook.3mf` in Bambu Studio (two plates, ten standing hooks each, pads visible) and prints; if a standing hook lifts, add a brim in Studio.
2. Before printing ten butt hooks: measure the fattest grip (and any reel seat the hook lands on). The 2 in opening leaves 1/16 per side on a 1-7/8 grip; `slot_w` is one constant (2-1/8 costs 1/8 of lip reach).
3. After the print: real fits, the feel of the up-and-out motion overhead for both hooks, update the retrospective.
4. If a board needs hooks on both edges, export a mirrored STL (mirror about the x axis of the outline in `rod_hook.py`).
