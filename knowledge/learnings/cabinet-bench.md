---
name: cabinet-bench-learnings
description: Design-phase retrospective for the 36x24x20 cabinet bench with undermount drawers
date: 2026-08-04
status: design-only
---

# Cabinet bench - retrospective (design phase)

Project: [[cabinet-bench-brief]] in `projects/Cabinet-bench/`. Designed,
not yet built; update this note with measured fits after the build.

## What worked

- Laminated double-18mm seat slab instead of a front rail: frees the
  entire front face for drawers (the storage-maximizing move) and stiffens
  the 876mm span without hidden framing.
- PARTS registry + geometry-probe asserts (recess measured from solids,
  not constants) caught a stale bounding-box assert immediately when the
  slab went on.
- Manual nesting check before recommending sheet counts: totals said
  "one 18mm sheet" (2.61 of 2.98 m2) but the two 910mm drawer faces
  cannot nest with the rest; two sheets required. Area totals alone
  mislead at >85% yield.
- Viewer review caught a real mistake: the bottom face sat 3mm off the
  floor, which would scrape rugs/uneven floors. Fix (20mm shadow gap,
  shorten only the face) cost ZERO box storage. Check floor clearance
  on any floor-standing drawer design.

## Correction 2026-08-24: values checked against the Blum 563H sheet

Checked against the Blum 563H/563 installation instructions (2016 ed.)
while answering a Drawer-bench question; `cabinet_bench.py`, its cut list
and STEP were corrected and re-exported the same day:

- Box outer width = opening minus (42 minus two side thicknesses):
  minus 18 with 12 mm sides. "Minus 10" is only right for 5/8 in sides.
- Box side bottom edge 14 mm above the mounting surface (bottom
  clearance), minimum 6 mm free above the box, maximum box height =
  opening minus 20. The 20 mm "tilt" allowance was over-conservative.
- The runner is longer than the drawer: 548 mm for the 21 in class,
  471 mm for 18 in. Frameless depth rule: inside depth >= runner + 3 + 6.
- 12.7 mm bottom recess and the drawer-length-equals-class rule hold.
- 1.5 mm front gap between the faces' backs and the carcass edge; the
  upper drawer's runner needs 14 mm below its box, so stacked boxes need
  14 + 6 = 20 mm between them (the file had 18).
- Drawer backs need Blum rear-hook prep (35 x 13 corner notches, 6 x 10
  bores 7 in from the side and 24 up); with a 12 mm back the bore breaks
  into a full-length bottom groove, so stop the groove 35 from each side.
  Modeled in Drawer-bench (`drawer_back_*`), only noted here.

## Undermount slide geometry used (ORIGINAL, superseded by the correction above)

First undermount design in the vault; nothing here was in
[[woodworking-stock]]. Values used, all Blum Tandem 563H class, to be
verified against the spec sheet of the actually purchased slides before
cutting:

- Box outer width = opening width - 10mm
- Box depth = slide nominal length EXACTLY (21" = 533.4mm)
- Drawer bottom underside recessed 12.7mm above box side bottom edge
- >= 20mm clear above each box (to the next structure) to tilt it onto
  its slides. Earlier draft used "face height - box height >= 25mm";
  that proxy breaks once a face has a tall floor shadow gap.
- Interior depth >= slide length + 9mm rear clearance
- Sides/bottom 12mm ply (Tandem rear hooks want <= 5/8" sides)
- Box bottom rides ~8mm above the mounting surface (from install jig)

Note: the generic "1mm gap per side" drawer rule in
[[woodworking-stock]] is a wooden-runner value and is WRONG for
mechanical slides; undermounts use the spec numbers above.

## Open items for the build

- Measure actual 18/12mm ply thickness; size all dados/rabbets to it.
- Verify slide spec numbers; consider Blum Movento 550mm (+17mm depth).
- Decide pulls (hardware vs routed finger pull) and finish.
- After build: promote measured kerf, ply thickness, and real undermount
  clearances into [[woodworking-stock]].
