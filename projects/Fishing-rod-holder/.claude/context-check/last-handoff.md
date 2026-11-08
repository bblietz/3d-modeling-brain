# Handoff: Fishing rod holder (2026-11-07)

## Where it stands

Deep-hook rod hook designed, checked and exported; 3MF with solid screw pads being built by `pipeline/make_print_3mf.py`. Options page republished with a Decided banner and the built section: https://claude.ai/artifact/MuJqbgWZjUNzqSTMLFRt4H. Nothing printed yet. Brian has not yet given the rod count, reel situation or comb spacing; the hooks are individual, so those only set how many to print and the pitch on the board.

## Decisions already locked

- Pocket: deep hook (Brian, 2026-11-07, "use the deep hook design"). Lip 3/4 wide, 5/8 above the floor, mouth floor 3/8 higher than the lip (lift to leave 1 in), pocket 7/8, mouth 1-1/4 with 1/4 chamfers, back web 1/8.
- Build: individual printed hooks screwed to the face of a 1x4 (Brian, "make individual deep hooks, that can be screwed into a 1x4 piece of wood"). Hook 3-1/2 x 3-1/4 x 3/8, reaches 1-3/4 past the board edge, two #8 x 1 screws 1 in from the edge at 9/16 and 2-11/16 up from the hook bottom, 5 mm holes with 10 mm countersinks.
- Material: PETG recommended and sliced (Brian has not objected). 2 walls, 15% gyroid, 0.30 mm Standard, 0.6 nozzle, 2-loop skirt.
- Print orientation: flat, back face on the bed, countersinks up.
- Every screw hole gets a 100% infill modifier pad (Brian's standing rule), proven in the sliced G-code.

## Files

- `rod_hook.py` (canonical CAD, asserts, SHOW viewer push), `rod-hook.stl`, `rod-hook-report.json`, `rod-hook-slice-petg.json`
- `pipeline/concepts.py` (concept round), `pipeline/renders.py` (OpenSCAD scenes + board layout), `pipeline/slice_stls.py`, `pipeline/options_page.py`, `pipeline/make_print_3mf.py`
- `images/` (hook-on-board, board-in-place, pocket-face-on, board-layout, hook-check-views; `images/concepts/` for the options round)
- `options.html`, `brief.md`, `knowledge/learnings/fishing-rod-holder.md`

## Next

1. Brian opens `rod-hook.3mf` in Bambu Studio (plates and pads visible), prints the hooks.
2. After the print: measure fit on the real blanks, note the feel of the 1 in lift, update the retrospective.
3. If a board needs hooks on both edges, export a mirrored STL (one flag in `rod_hook.py`).
