# Handoff: Cable bin (2026-10-25)

Resume with Fable 5.1 (design work). Read `projects/Cable-bin/brief.md` and
`knowledge/learnings/cable-bin.md` first.

## State

- `cable_bin.py` builds half A (tails), half B (sockets), two coupons; all
  asserts pass; STLs exported beside it.
- `pipeline/renders.py` writes the 16 inspection PNGs in `images/` through
  OpenSCAD.
- `pipeline/make_print_3mf.py` builds `cable-bin.3mf` (plate 1 bin, plate 2
  joint coupon) and `cable-bin-slice.json` with per-plate time and grams.
- `options.html` is the sign-off page (published as a private artifact:
  https://claude.ai/artifact/3QZNtCDUcGY7G7snwYpHRs).

## Decisions already locked

- Two halves per bin split at mid-length; A and B share one plate; four runs.
- Vertical sliding dovetails on internal posts; crush ribs on the top 12 mm
  of each tail; sockets closed at the bottom by B's floor; dovetail
  centreline 0.25 mm inboard of the lip's inner face.
- Stacking by the 45 degree foot flare on the lip chamfer; drop 5 mm; pitch
  3.80 in; posts stop 7 mm below the rim.
- PLA Basic, 0.6 high-flow nozzle, 0.30 mm Standard, 2-line walls and floor
  (WALL 1.24), wall_loops 3 for the lip and posts, 20 % infill, 2-loop
  skirt, no brim, no ironing. (Brian 2026-10-25: drawer bin, no real load,
  PLA; the 3-line PETG version was 368 g / 7 h 02 min.)
- Joint coupon on plate 2, printed before any bin.

## Waiting on Brian

- Options page answers: friction vs CA drop; plain ends vs finger scallop;
  3.80 vs 4.00 in pitch; weight (285 g as built, or slotted long walls about
  30 g less and/or posts 12 to 8 mm about 15 g less); PLA colour.
- Coupon fit report (firm thumb push over the last 12 mm, holds when lifted
  by either piece). Loose or jammed: change `RIB_PROUD` by 0.1 mm, rerun
  `cable_bin.py`, then `pipeline/make_print_3mf.py`.
- One GUI open of the 3MF to confirm both plates render.

## If a change is asked

Edit the constants at the top of `cable_bin.py`, run it (asserts), run
`pipeline/renders.py`, run `pipeline/make_print_3mf.py`, fill the numbers in
`options.html` and `brief.md`, republish the artifact with the same file
path, commit.
