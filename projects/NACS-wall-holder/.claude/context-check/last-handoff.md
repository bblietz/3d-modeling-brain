---
type: handoff
project: NACS-wall-holder
date: 2026-10-12
---

# NACS wall holder handoff (2026-10-12, filament budget options out, waiting on Brian's pick)

## State
The 2026-10-11 file (4.5 in plate, solid base and face, 90 drum, crest lip, wordmark inlay) slices at 10 h 19 min and
564.1 g of body PETG (580.4 g with the interface and inlay spools). Brian wants the body under 500 g so two holders come
off one 1000 g spool. `pipeline/filament_budget.py` reads the G-code back by filament, feature and region (sum matches
the slicer to 0.1 g): the part is 382 g (solid face 97, core 97, walls 76, solid base 75, shells 36), the rest is
thrown away (lip support block 83, flange-ring trees 46, cavity trees 22, prime tower 30). 36 setting variants sliced
(`filament-variants.json`, ten seconds each). Options page https://claude.ai/artifact/59PbyNyw5qRfGKi6yD4M7N:
A hybrid supports, comb 5 mm, single-wall trees, 15% core = 488.0 g, 8 h 55 (recommended); B same with 10% core =
465.1 g, 8 h 34; C slim single-wall trees, 15% = 453.2 g, 8 h 38 (not recommended). Nothing in holder.scad or the
print file has changed yet. Evidence page https://claude.ai/artifact/QCeo4UdoVNbcSQv3je5xm4, plan page
https://claude.ai/artifact/D2zPQ4v2W97wuq1hMqpYa6, base options https://claude.ai/artifact/5YuDCMozLvJvJUdhwWxwJk.

## Decisions already locked (Brian)
- 2026-10-12: body PETG under 500 g (two holders per 1000 g spool). Pick pending (A, B or C on the options page).
- 2026-10-11: the face solid like the base; every modifier wholly inside the body; plate 4.5 in (pick A), same screw
  pattern, foot on flat plate and flange inside the plate (asserted).
- 2026-10-10: plate 1/4 in AND solid. `mouth_z` 61.43 and `cut_top` 93.8 stay.
- 2026-10-08: drum 1 in deeper, 90 across, flange 104, cleat_depth 44.45, tip_gap 5, undercut 20, crest lip 1.5 in,
  inlaid T, wordmark and frame in filament 3, plain top screw holes, skirt kept.
- Everything from 2026-09-19 stays: v7 cavity and cleat, grip-up docking, 45 / 15 degree wand, 1/16 in roundovers.

## Pipeline notes
- When Brian picks: put the settings into `make_coupon_3mf.py` JOBS["holder"] EXTRA (A: `support_base_pattern_spacing`
  "5", `tree_support_wall_count` "1", `sparse_infill_density` "15%"; B: "10%"; C: `support_style` "tree_slim" too),
  update its docstring and the SPARSE windows' expectation if the core changes (0.18/0.21 were at 20%), run
  `pipeline/run_all.sh`, then `filament_budget.py breakdown` on the new slice to confirm the grams, republish plan.html
  and the options page with a "Picked" line.
- `filament_budget.py variant <name> key=value ...` slices a settings variant of holder-print.3mf into $SCRATCH/fil/<name>
  (vector keys stay vectors; `mod:`/`base:`/`face:` prefixes patch the modifiers); `table` merges the per-variant
  result.json files (never a shared file: the parallel slices raced on one); `regions <sliced>` needs the unsliced
  print.3mf beside it (the sliced file bakes the part offsets into the mesh). Run region passes up to 16 at a time:
  since the chunked containment fix (2026-10-14) each peaks at about 0.5 GB and takes about 15 s; before it each peaked at
  9.7 GB and 28 at once OOM-killed the whole box (2026-10-12). For a big batch wrap the loop so an overrun kills only slicer
  jobs: `systemd-run --user --scope -p MemoryMax=44G -p MemoryHigh=40G -p MemorySwapMax=2G -p OOMPolicy=continue -- sh -c '...'`.
- `filament_figures.py section|layer|bars` draws the toolpaths by region; `filament_options_page.py` builds the page.
- Known dead ends: tower width does nothing; `wipe_tower_no_sparse_layers` is refused ("relative position of the model and
  the prime tower") with the tower beside the part, and at y 5 the tower is off the printable area; hollow and lightning
  support bases bridge the lip's full depth just under it.
- `corner_check.py` re-slices when its cached slice is older than holder-print.3mf (it reused an Oct 10 slice on
  2026-10-11) and no longer prints the pad-reach line when the pad does not reach the plate's edge.
- Order after a cavity, drum or plate change: `pipeline/run_all.sh` (zbudget, rim_round, insertion, exports, 3MF with
  both modifiers, renders, modifier figures, corner figures, pages), then republish the pages.

## Open
- Brian's pick on the filament page, then the rebuild above.
- Print `holder-print.3mf` (plate down; a second PETG colour in the AMS slot for filament 3). Not sent to the printer.
- Grip fit in the extra 1/2 in of opening is unproven (ask for the handle's width and height 1/2 in and 1 in behind the
  glossy housing, plus the button height; adjust `grip_flare` if needed).
