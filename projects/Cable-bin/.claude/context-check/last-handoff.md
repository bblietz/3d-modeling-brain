# Handoff: Cable bin (2026-10-25)

Resume with Fable 5.1 (design work). Read `projects/Cable-bin/brief.md` and
`knowledge/learnings/cable-bin.md` first.

## State

- `cable_bin.py` builds half A (tails) and half B (sockets); all asserts
  pass; STLs exported beside it. The fit-ladder coupons were removed
  2026-10-25 (design final); the ladder is in the retrospective.
- `pipeline/renders.py` writes the 15 inspection PNGs in `images/` through
  OpenSCAD.
- `pipeline/make_print_3mf.py` builds `cable-bin.3mf` (one plate, both
  halves) and `cable-bin-slice.json` with time and grams.
- `options.html` is the sign-off page (published as a private artifact:
  https://claude.ai/artifact/3QZNtCDUcGY7G7snwYpHRs).

## Decisions already locked

- Two halves per bin split at mid-length; A and B share one plate; four runs.
- Vertical sliding dovetails on internal posts; crush ribs on the top 6 mm
  of each tail; sockets closed at the bottom by B's floor; dovetail
  centreline 0.25 mm inboard of the lip's inner face.
- Stacking by the 45 degree foot flare on the lip chamfer; drop 5 mm; pitch
  3.80 in; posts stop 7 mm below the rim.
- PLA Basic, 0.6 high-flow nozzle, 0.30 mm Standard, 2-line walls and floor
  (WALL 1.24), wall_loops 3 for the lip and posts, 20 % infill, 2-loop
  skirt, no brim, no ironing. (Brian 2026-10-25: drawer bin, no real load,
  PLA; the 3-line PETG version was 368 g / 7 h 02 min.)
- Lightening, Brian took both cuts 2026-10-25: 13 vertical 6 x 64 mm slots
  per long wall per half at 14 mm pitch (z 18 to 82), finger scallop 52 x
  18 mm in each end wall, joint posts 8 mm. Friction hold (no CA), scallop
  ends and 3.80 in pitch confirmed the same day.
- Joint fit: ladder pair 4 (body 0.25, crush 0.10, ribs 6 mm), Brian's pick
  2026-10-25 from the printed four-pair ladder. First coupon at body 0.15 /
  crush 0.20 was too tight; pair 2 (same crush, 12 mm ribs) was the guess.
- No small_perimeter override in the 3MF (the PETG recipe's threshold 10 is
  a radius and slowed every slot web to 30 mm/s: 1 h 43 min per bin).

## Waiting on Brian

- Nothing in the design. Colour is Brian's pick in Bambu Studio (display
  colour in the 3MF is black; any PLA Basic slot prints it).
- The first bin print. If the full joint feels different from the coupon,
  move `DT_CLR`, `RIB_CRUSH` or `RIB_LEN` and rebuild; the ladder that set
  them is in knowledge/learnings/cable-bin.md.
- One GUI open of the 3MF to confirm the plate renders.

## If a change is asked

Edit the constants at the top of `cable_bin.py`, run it (asserts), run
`pipeline/renders.py`, run `pipeline/make_print_3mf.py`, fill the numbers in
`options.html` and `brief.md`, republish the artifact with the same file
path, commit.
