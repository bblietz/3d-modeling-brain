# Guitar pick handoff (2026-10-12)

Plain copy of the Dunlop Tortex Standard 1.0 mm pick, PETG, 0.2 mm nozzle.
CAD and print file are done and slice-verified with a ROUNDED edge; nothing
is printed yet. Brian still has to pick the edge profile.

## State

- `projects/Guitar-pick/guitar_pick.py`: `build(edge)` from
  `outline-dunlop.csv` (traced from Brian's caliper photos by
  `pipeline/trace_photo.py`), side is a smooth spline (within 0.06 mm of the
  trace, convex), `EDGES` = square / round / chamfer / bevel, default round
  (fillet R 0.45 top and bottom, 0.10 mm rim). Asserts 26.19 x 30.38 x 1.0,
  one watertight solid on Z=0.
- `pipeline/edge_options.py`: the four variants, tip cross-sections, the
  per-layer underside overhang table, OpenSCAD close-ups
  (`images/edge-*.png`), `edge-options.json` for the page.
- `guitar-pick.3mf` from `pipeline/make_print_3mf.py` (round edge,
  elephant-foot compensation 0, arc-aware G-code check of the underside
  steps): 16 layers to z 1.0, seam at the top centre, solid, skirt,
  13 min 13 s / 0.69 g. Numbers in `guitar-pick-slice.json`.
- Sign-off page (outline approved 2026-10-11; edge options added 2026-10-12):
  https://claude.ai/artifact/Xdy17d32z8uCNaQAHhxuis
- Retrospective: `knowledge/learnings/guitar-pick.md`.

## Next

1. Brian picks the edge profile on the page (round is in the 3MF; chamfer
   or bevel = change the default in `guitar_pick.py`, rerun it, then
   `make_print_3mf.py`).
2. Brian opens the 3MF in Bambu Studio (GUI ground truth), with the 0.2
   nozzle installed and the 0.2 machine selected in Studio.
3. Print; measure thickness; compare feel against the Tortex.
4. If the top is not smooth enough: second pick with ironing (coupon).

## Decisions already locked

- PETG, plain face (no logo, no texture), one pick first (Brian 2026-10-11).
- Outline: the measured Dunlop trace, not the generic 351 (tip radius 4.5
  vs 3.4 mm). Brian approved it on the sign-off page.
- Thickness 1.0 mm (Brian's calipers).
- 0.2 mm nozzle for smoothness (Brian 2026-10-11); layer_height 0.06 so the
  layers sum to exactly 1.0 mm.
- Edges tapered, not square (Brian 2026-10-12). Research: a new Tortex
  Standard is die-stamped square and wears into a bevel, no numbers exist.
  Printed flat, so the underside slope stays about 45 degrees or steeper.
- No ironing on the first pick (vault PETG rule; this pick is the coupon).
- Seam at the top centre, under the thumb.
- Design work runs on Fable 5.1 only; stop before building otherwise.
