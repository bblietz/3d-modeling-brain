# Guitar pick handoff (2026-10-11)

Plain copy of the Dunlop Tortex Standard 1.0 mm pick, PETG, 0.2 mm nozzle.
CAD and print file are done and slice-verified; nothing is printed yet.

## State

- `projects/Guitar-pick/guitar_pick.py` builds the pick from
  `outline-dunlop.csv` (traced from Brian's caliper photos by
  `pipeline/trace_photo.py`); asserts 26.19 x 30.38 x 1.0 mm, one
  watertight solid on Z=0. STL exported.
- `guitar-pick.3mf` from `pipeline/make_print_3mf.py`, verified by CLI
  round trip and a real slice: 16 layers to z 1.0, seam at the top centre,
  solid, skirt, 13 min 27 s / 0.7 g. Numbers in `guitar-pick-slice.json`.
- Sign-off page (Brian approved the outline on it):
  https://claude.ai/artifact/Xdy17d32z8uCNaQAHhxuis
- Retrospective: `knowledge/learnings/guitar-pick.md`.

## Next

1. Brian opens the 3MF in Bambu Studio (GUI ground truth), with the 0.2
   nozzle installed and the 0.2 machine selected in Studio.
2. Print; measure thickness; compare feel against the Tortex.
3. If the top is not smooth enough: second pick with ironing (coupon).

## Decisions already locked

- PETG, plain face (no logo, no texture), one pick first (Brian 2026-10-11).
- Outline: the measured Dunlop trace, not the generic 351 (tip radius 4.5
  vs 3.4 mm). Brian approved it on the sign-off page.
- Thickness 1.0 mm (Brian's calipers).
- 0.2 mm nozzle for smoothness (Brian 2026-10-11); layer_height 0.06 so the
  layers sum to exactly 1.0 mm.
- No ironing on the first pick (vault PETG rule; this pick is the coupon).
- Seam at the top centre, under the thumb.
- Design work runs on Fable 5.1 only; stop before building otherwise.
