---
name: drawer-bench-learnings
description: Design-phase retrospective for the maple post-and-panel drawer bench (CAD built and reviewed, provisional dimensions)
date: 2026-08-24
status: design-only
---

# Drawer bench - retrospective (design phase)

Project: [[drawer-bench-brief]] / [[drawer-bench-design]] /
[[drawer-bench-plan]] in `projects/Drawer-bench/`. Designed, modeled and
reviewed, not built; update with measured fits after the build.

## What worked

- Post-and-panel in build123d: chamfer the post's four vertical edges
  first, then cut the grooves and mortises; assert the post volume equals
  box minus chamfer prisms minus grooves minus mortises. That one number
  proves the chamfers never reach a groove and every cut is stopped where
  the constants say.
- `assert_housed(guest, host, probe)`: a probe box the size of the housed
  slice must be fully inside the guest, fully outside the host, and the
  two must not overlap. Reused for every panel edge, rail tenon and the
  bottom, on BOTH ends. The first pass probed only the left end; five
  mutations (rail 5 mm short, box 20 mm narrow, top front shifted, bottom
  5 mm narrow, drawer ends 4 mm short) passed silently until the
  right-hand probes were added. Probe mirrored parts explicitly.
- A pairwise-intersection loop over every placed instance (25 solids,
  300 pairs, about 4 s) as the global no-overlap check.
- Writing the design as prose first exposed seven inconsistencies only
  when the CAD forced a value (drawer opening height, groove stop vs
  bottom rail tenon, rear rail vs back panel height, rail thickness vs
  groove width, groove vs rabbet for the bottom, an open groove where the
  slide tab lands, a 7 mm ply lip). Record such resolutions in design.md,
  not only in the code.
- Registry notes are the cut list: the emitter prints bounding-box blanks
  and merges identical rows, so every note must be self-identifying
  (FRONT/REAR, left/right mirrored) and every number in a note must be an
  f-string of the constants (through `inch()`, since 2026-09-28) or it
  goes stale on the measured re-run.
- Cut-list rows must be machining-specific: the emitter used to merge
  parts with identical blanks and materials (drawer front with drawer
  back, plain rail with rabbeted rail), hiding which one gets the Blum
  prep. `scripts/cutlist.py` now merges only when the notes agree too.
  And notes on a flat part must give datums from the blank's ends (the
  back's notches are 41.35 from each end), not from the assembled side
  face (35 from the side's inner face); give both when the sheet uses the
  assembled one.
- Shop drawings that cannot lie (2026-09-27, `part_drawings.py`): each
  part's sheet is laid out from the same constants that build the solid,
  and before a sheet is written every drawn groove, rabbet, notch and
  bore is probed against the real solid (a box 1 mm inside the cut must
  be air, a 1 mm slab past its floor must be wood, plus "runs out the
  end" and "stopped" probes). The first run caught a real defect the
  volume asserts had absorbed: the dowel helper bored 1 mm deeper than
  the documented 1 in on both sides. Draw from constants, verify against
  solids; the two disagree exactly where the model is wrong.
- Stopped groove plus notched panel (Brian, 2026-09-28): a stopped
  groove whose end must be squared to seat a panel is chisel work at
  every post; notching the panel's corner instead puts the tolerance in
  the notch, so the groove may round or ramp out anywhere in a window
  (here 3/4 to 2-1/4 in from the floor end) and the panel's un-housed
  bottom covers it. Model the window as a clearance constant and assert
  it (at least the bit radius plus 1/4 in), keep the tongue's start out
  of any other groove band (a 0.7 mm sliver otherwise), and probe the
  clearance zone as air on both sides with the post solid below it.
- Cut list in inches only, 1/32 (Brian, 2026-09-28): once the mm column
  goes, the fraction carries all the precision, and 1/16 is too coarse
  for blanks derived from metric ply (a drawer end came out 0.67 mm
  long at 1/16, 0.12 mm at 1/32). Cuts sized to plywood print "3/4 ply
  (measure)" rather than a fraction: 18 mm prints as 23/32, which reads
  as a number to hit. Give the datum that is a clean inch (the bottom
  groove's top wall at 1-1/2, not its lower wall at 1-1/32).
- Re-check a constraint when its input changes (2026-09-28): the
  drawer-back groove was stopped because a 1/2 in bottom's groove hit the
  Blum hook bores; the bottoms went to 1/4 in ten days earlier and nobody
  asked whether the stop still had a reason. Brian caught it from the
  drawing ("why is the dado not all the way across?"). The bore probe
  that guards the real constraint was there all along; the stop was a
  hand-coded consequence, not a derived one. Assert the constraint and
  let the geometry be the simple default.
- Subagent-driven build: one implementer per task with the complete code
  in the brief, one reviewer per task that mutation-tests the asserts, a
  whole-file review at the end. The per-task reviews found only Minor
  items; the whole-file review found the cut-list and right-hand gaps
  that mattered. Keep the final review.

## Decisions locked (promoted from the handoff and design.md)

- 40 x 24 is the TOP (measured, Brian 2026-09-17; was 36 x 24
  provisional), floor to top surface 19-5/8 in (was 20 in); posts inset
  by the 1-1/4 in overhang, itself still provisional pending the Boos
  island (footprint 37-1/2 x 21-1/2, opening 31-1/2 at the current
  numbers).
- 3 in posts glued from 8/4, 3/8 chamfer, no taper; 3/4 ply sides and
  back 1/2 in behind the post faces in T18 x 3/8 grooves stopped 1-1/2
  in above the floor with their ends left as the tool cuts them: the
  panels' bottom corners are notched 3/8 x 1-1/2 in, so the housed
  tongue starts 2-1/4 in up, 3/4 in clear of the groove's end, and the
  panel's bottom 1-1/2 in butts the post face over it (Brian,
  2026-09-28). Panel bottoms on the bottom drawer front's line, 3/4 in
  above the floor (was 1-1/2 in until 2026-09-27, when Brian revisited
  the legs against a rendered options page and kept the 3/8 chamfer,
  E1, but wanted the panels to end on the same line as the drawer);
  hidden front frame 1 in behind the post faces, rails
  1 / 1 / 1-1/2 in tall from plain 3/4 in stock (milled to T18 for the
  tenons until 2026-09-27), dowel-jointed into the front
  posts (two 3/8 in dowels per rail, one each end, 1 in deep; was
  stub-tenoned into three stopped mortises per front post until
  2026-09-18); no rear rail since 2026-09-27: the back runs full height
  like the sides (17-1/8 in) and a 3/4 x 1-1/2 in maple cleat glued and
  screwed inside its top edge takes the rear figure-8s (the tenoned
  1-1/2 in rail had only ever been a solid landing for them); 1/2 ply
  bottom, top face 2-1/4 in above the
  floor, in 1/4 in grooves run through the sides and back full length
  (Brian, 2026-09-27; were stopped at the posts) and a rabbet at the
  front rail.
- Fronts 3/4 in maple, 1/4 in behind the post faces, 5-5/8 over 11-1/8
  (was 5-3/4 / 11-3/8 before the 2026-09-17 height measurement; the
  front zone is re-split ~1:2 by that rule, not scaled, whenever the
  overall height changes) with 1/8 side, 1/4 mid, 1/8 top reveals and a
  3/4 in floor gap.
- Drawer-box bottoms are 1/4 in (6 mm) ply, not 1/2 in (Brian,
  2026-09-17; landed here after briefly trying 1/8 in); sides, front
  and back stay 1/2 in. The housing groove keeps its 1/4 in reach -
  only its height (the `T6` constant) changed to match the thinner
  panel.
- Front rails are dowel-jointed, not stub-tenoned into post mortises
  (Brian, 2026-09-18): two 3/8 in dowels per rail, one each end, 1 in
  deep into post and rail; rails now butt flush at the post face
  (length = opening exactly). The post's box mortises became round
  bores at the same rail-centerline heights; the volume-identity asserts
  moved from box to cylinder volumes and passed clean on the first
  re-run. The rear top rail was unaffected then, and dropped altogether
  on 2026-09-27 (see above).
- 18 in undermount slides (Blum 563H4570B, 471 mm runner), box heights
  computed from the rail-to-rail openings minus Blum's clearances (14 mm
  bottom, 6 mm top) rather than fixed - a hard-coded pair of "Blum
  maximum" constants left over from the original opening sizes silently
  went stale the first time the front-zone split changed (see
  drawer-bench-design's "Resolutions from the CAD", 2026-09-17); outer
  width opening minus 18 mm (inside = opening minus 42), 12.7 mm bottom
  recess, runner front screws into the posts between the mortises, rear
  brackets on the back panel. Drawer-back bottom grooves run through
  (Brian, 2026-09-28; the stop that kept them out of the hook bores dated
  from the 1/2 in bottoms) and the box bottoms are plain rectangles.
- Butcherblock top matched to the Boos island, 1-3/4 in thick (confirmed
  by measurement, Brian 2026-09-27; the provisional value was right),
  figure-8 fasteners, no glue.
- Pulls and finish out of scope until the build.

- The "verified from the sheet" lesson: the undermount numbers copied
  from [[cabinet-bench-learnings]] were labeled unverified and three of
  them were wrong (width rule for 12 mm sides, bottom and top clearance).
  Reading the vendor sheet cost ten minutes and changed the cut list.
  Do it before the first export, not after. The second pass over the
  same sheet found three more (front gap, rear-hook notches, a bore that
  breaks into a 12 mm back's groove): read the whole sheet, not the table
  you came for.

## Open items for the build

- Measure: the space, the Boos island (edge profile, overhang; thickness
  done 2026-09-27), actual 3/4 and 1/2 ply, the purchased slide spec. Re-run
  `EXPORT=1 .venv/bin/python projects/Drawer-bench/drawer_bench.py`.
- Brian to review the seven CAD resolutions in design.md, in particular
  the 58 mm interior height of the top drawer. (The 7 mm ply lip under
  the bottom groove resolved itself on 2026-09-27: lowering the panels
  to the drawer-front line made it 26 mm.)
- Confirm the purchased slides are 563H4570B (or re-enter the runner
  length and setback rule from that sheet).
- Decide pulls (routed finger pull vs hardware) and finish.
- After the build: promote measured kerf, ply thickness and undermount
  clearances into [[woodworking-stock]].
