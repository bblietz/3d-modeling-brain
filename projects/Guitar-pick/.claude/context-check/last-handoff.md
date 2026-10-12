# Guitar pick handoff (2026-10-12)

Plain copy of the Dunlop Tortex Standard 1.0 mm pick, PETG, 0.2 mm nozzle.
CAD and print file are done and slice-verified with a mirrored 38 degree
bevel (the widest a flat print carries without support); the mirrored 1.5
mm bevel Brian asked for exists as CAD only. Nothing is printed yet.

## State

- `projects/Guitar-pick/guitar_pick.py`: `build(edge)` from
  `outline-dunlop.csv` (traced from Brian's caliper photos by
  `pipeline/trace_photo.py`), side is a smooth spline (within 0.06 mm of the
  trace, convex), `EDGES` = sym / mirror / soft / bevel / round / chamfer /
  square, default sym (0.45 mm bevel dropping 0.35, 38 degrees, on both
  faces, creases blended R 0.35, 0.30 mm rim). `mirror` is the 1.5 mm
  bevel on both faces (`guitar-pick-mirror.stl`), unprintable flat: 0.26
  mm per layer underneath, in air. Asserts 26.19 x 30.38 x 1.0,
  one watertight solid on Z=0.
- `pipeline/edge_options.py`: the seven variants, tip cross-sections, the
  per-layer underside overhang table, OpenSCAD close-ups
  (`images/edge-*.png`), `edge-options.json` for the page.
- `guitar-pick.3mf` from `pipeline/make_print_3mf.py` (sym edge,
  elephant-foot compensation 0, arc-aware G-code check of the underside
  steps, seam check = top edge and aligned): 16 layers to z 1.0, seam at
  the top edge's left shoulder, solid, skirt, 13 min 12 s / 0.68 g.
  Numbers in `guitar-pick-slice.json`.
- Sign-off page (outline approved 2026-10-11; edge options added 2026-10-12):
  https://claude.ai/artifact/Xdy17d32z8uCNaQAHhxuis
- Retrospective: `knowledge/learnings/guitar-pick.md`.

## Next

1. Brian picks on the page: the mirrored 38 degree bevel (in the 3MF),
   the 1.5 mm bevel on top only (`soft`), or a stand-up print on a
   snap-off base for the full mirrored bevel (not built; support by
   another name). Change the default in `EDGES`, rerun `guitar_pick.py`,
   `edge_options.py`, `make_print_3mf.py`, `make_compare_page.py`.
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
- Edges tapered, not square (Brian 2026-10-12): the wide bevel with a
  curved lead-in and no noticeable line (his words after seeing round,
  chamfer and bevel), mirrored on both faces, and NO support material (his
  words, same day). Research: a new Tortex Standard is die-stamped square
  and wears into a bevel, no numbers exist. Printed flat, the underside
  carries about 38 degrees at most (lead-in R 0.35 max there), so the
  mirrored print file is the 0.45 mm bevel.
- No ironing on the first pick (vault PETG rule; this pick is the coupon).
- Seam at the top centre, under the thumb.
- Design work runs on Fable 5.1 only; stop before building otherwise.
