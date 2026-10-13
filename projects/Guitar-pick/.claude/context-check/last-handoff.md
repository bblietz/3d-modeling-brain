# Guitar pick handoff (2026-10-12)

Plain copy of the Dunlop Tortex Standard 1.0 mm pick, PETG, 0.2 mm nozzle.
CAD and print file are done and slice-verified: the mirrored 1.5 mm
blended bevel with a rounded rim, printed STANDING on a snap-off base
(Brian's call, same filament, no slicer support). Nothing is printed yet.

## State

- `projects/Guitar-pick/guitar_pick.py`: `build(edge)` from
  `outline-dunlop.csv` (traced from Brian's caliper photos by
  `pipeline/trace_photo.py`), side is a smooth spline (within 0.06 mm of the
  trace, convex), `EDGES` = mirror (default: 1.5 mm bevel dropping 0.35 on
  both faces, creases blended R 5, rim creases R 0.15, 0.30 rim) / sym /
  soft / bevel / round / chamfer / square; writes `guitar-pick-<edge>.stl`.
- `standup.py`: the pick tip-up on a 0.22 x 0.3 neck along the top edge
  and shoulders (to the 45 degree points), saddle block, 1 mm plate, 4 mm
  cooling column; 34.66 mm = 577 layers; a 2 micron seam strip down the
  +y face. Writes `guitar-pick.stl` (print STL) and `standup.json`. Asserts 26.19 x 30.38 x 1.0,
  one watertight solid on Z=0.
- `pipeline/edge_options.py`: the seven variants, tip cross-sections, the
  per-layer underside overhang table, OpenSCAD close-ups
  (`images/edge-*.png`), `edge-options.json` for the page.
- `guitar-pick.3mf` from `pipeline/make_standup_3mf.py`: paints the seam
  strip (`paint_seam="4"` on the strip's two floor triangles), checks in
  the real slice: 577 layers to 34.66, neck a single line, 0% overhang
  walls, every pick loop's seam on the rear face within 0.8 mm of the
  centre line, 2 h 11 min / 2.51 g. Numbers in `guitar-pick-slice.json`.
  Scarf seams produced nothing in the CLI and are not shipped.
  `pipeline/make_print_3mf.py` is the flat pipeline (sym variant,
  `guitar-pick-flat.3mf`), kept.
- Sign-off page (outline approved 2026-10-11; edge options added 2026-10-12):
  https://claude.ai/artifact/Xdy17d32z8uCNaQAHhxuis
- Retrospective: `knowledge/learnings/guitar-pick.md`.

## Next

1. Brian opens the 3MF in Bambu Studio (GUI ground truth), with the 0.2
   nozzle installed and the 0.2 machine selected in Studio; the seam
   paint should show on the rear face.
2. Print (2 h 11 min estimated; the 12 s minimum layer time is the lever
   if that is too long), cut the neck at the block, sand the rim flush.
3. Measure thickness; compare feel against the Tortex; report the thumb
   edge after sanding and whether the neck held.
4. Rebuild chain after any change: `guitar_pick.py` (EDGE=mirror),
   `standup.py`, `pipeline/make_standup_3mf.py`, `pipeline/edge_options.py`,
   `pipeline/make_compare_page.py`, publish to the page URL.

## Decisions already locked

- PETG, plain face (no logo, no texture), one pick first (Brian 2026-10-11).
- Outline: the measured Dunlop trace, not the generic 351 (tip radius 4.5
  vs 3.4 mm). Brian approved it on the sign-off page.
- Thickness 1.0 mm (Brian's calipers).
- 0.2 mm nozzle for smoothness (Brian 2026-10-11); layer_height 0.06 so the
  layers sum to exactly 1.0 mm.
- Edges tapered, not square (Brian 2026-10-12): the wide bevel with a
  curved lead-in and no noticeable line (his words after seeing round,
  chamfer and bevel), mirrored on both faces, NO support material, and the
  rim rounded too (all his words, same day). Research: a new Tortex
  Standard is die-stamped square and wears into a bevel, no numbers exist.
- Printed standing on a snap-off base that is part of the model (Brian,
  same day: "the standup version with a base, as this will give the
  smoothest surface for PETG"). A flat print caps the underside at about
  38 degrees, so flat and mirrored 1.5 mm are incompatible.
- 0.2 nozzle stays (Brian allowed a change; 0.06 layers are the smoothest).
- No ironing on the first pick (vault PETG rule; this pick is the coupon).
- Seam at the top centre, under the thumb.
- Design work runs on Fable 5.1 only; stop before building otherwise.

## Print status (2026-10-12)

Brian swapped in the 0.2 nozzle and started `guitar-pick.3mf`. First status check: RUNNING, layer 274/577, 53%, 250 C / 70 C, chamber 44 C, no HMS errors. Result pending; after it finishes record the real print time, whether the neck held, and the feel versus the Tortex in the retrospective.

Finished 22:47 (FINISH, no errors), pick layers at 12.4 s each, estimate accurate. Next: Brian cuts the neck at the block, sands the top rim flush on 400 then 800 grit, and reports feel vs the Tortex, the neck, the seam line and the sanded edge. Record those in the retrospective.
