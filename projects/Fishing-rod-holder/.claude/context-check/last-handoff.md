# Handoff: Fishing rod holder (2026-11-07, end of day)

## Where it stands

Open-J rod hook with a slot leaning away from the wood: designed, checked, exported, and packed into `rod-hook.3mf` (8 hooks, 2 plates, solid screw pads proven in G-code). Options page republished (Version 3) with the Decided banner and the built section: https://claude.ai/artifact/MuJqbgWZjUNzqSTMLFRt4H. Nothing printed. Brian has not yet given the rod count, reel situation or comb spacing; the hooks are individual, so those only set how many to print and the pitch on the board. The OCP viewer window has the current hook pushed (hook, 1x4 stub, 3/8 rod).

## Decisions already locked

- Pocket: deep hook (Brian, "use the deep hook design"), then reworked on his asks: an angled resting slot that leans AWAY from the wood (he corrected the first attempt, which sloped toward the board), and no top bar past the wood ("remove the top most part of the device that is not over the wood").
- Build: individual printed hooks screwed to the face of a 1x4 ("make individual deep hooks, that can be screwed into a 1x4 piece of wood").
- Geometry as built: hook 4 x 3-1/4 x 3/8; tab 1-3/4 wide on the board, jaw 2-1/4 past the edge; slot 7/8 wide leaning 35 degrees, rounded bottom R 7/16 with its low point 5/8 up; ramp leaves the tab edge at 1-7/8; lip top 1-7/8 sloping to a 2-1/4 tip; 1/8 web off the wood; two #8 x 1 screws 1 in from the board edge at 9/16 and 2-11/16 up, 5 mm holes with 10 mm countersinks. Lift to leave 1.57 in for 1/4 to 5/8 blanks.
- Material and process: PETG, 2 walls, 15% gyroid, 0.30mm Standard, 0.6 nozzle, 2-loop skirt. 26.2 g / 35 min per bare hook; 3MF 245 g / 5 h 40 for 8.
- Print orientation: flat, back face on the bed, countersinks up.
- Every screw hole has a 100% infill modifier pad (22 mm, inset 0.2 mm), proven at 0.87 vs 0.15 plastic per volume.

## Files

- `rod_hook.py` (canonical CAD, asserts, SHOW viewer push), `rod-hook.stl`, `rod-hook.3mf`, `rod-hook-report.json`, `rod-hook-slice-petg.json`, `rod-hook-3mf-report.json`
- `pipeline/concepts.py` (concept round), `pipeline/renders.py` (OpenSCAD scenes + board layout), `pipeline/slice_stls.py`, `pipeline/options_page.py`, `pipeline/make_print_3mf.py`
- `images/` (hook-on-board, board-in-place, pocket-face-on, board-layout, hook-check-views; `images/concepts/` for the options round)
- `options.html`, `brief.md`, `knowledge/learnings/fishing-rod-holder.md`

## Next

1. Brian opens `rod-hook.3mf` in Bambu Studio (two plates, pads visible), prints the hooks.
2. After the print: real blank fit, the feel of the up-the-ramp-then-out motion, update the retrospective.
3. If a board needs hooks on both edges, export a mirrored STL (mirror about the x axis of the outline in `rod_hook.py`).
4. Lean angle, lip height and slot width are single constants if Brian wants the hood deeper or the lift lower.
