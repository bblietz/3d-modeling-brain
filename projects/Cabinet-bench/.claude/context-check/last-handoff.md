# Handoff - Cabinet Bench (2026-08-04)

Milestone: design complete (Phases 1-5 of /furniture done). Not built.

## State

- Canonical CAD: `projects/Cabinet-bench/cabinet_bench.py` (build123d;
  run with `.venv/bin/python`, env `EXPORT=1` regenerates cutlist + STEP,
  `TMP_STL=<path>` writes a render STL, `SHOW=1` pushes to OCP viewer).
- Deliverables exported: `cutlist.md`, `cutlist.csv`,
  `cabinet_bench.step`, `images/final-4view.png`. All asserts pass.
- Retrospective: `knowledge/learnings/cabinet-bench.md`.

## Decisions already locked

- 36 x 24 x 20 in overall (914.4 x 609.6 x 508 mm), user-specified.
- Two STACKED full-width drawers (user choice; maximizes storage).
- 3/4" ply carcass/slab/faces, 1/2" ply drawer boxes, 1/8" (3mm) ply
  back (user revisions 2026-08-04).
- Joinery: dados and rabbets, 6mm deep (user choice).
- Slides: 21" undermount soft-close, Blum Tandem 563H class (user
  choice). Geometry: box = opening - 10mm wide, 533.4mm deep, 12.7mm
  bottom recess, face - box >= 25mm. VERIFY against purchased spec.
- Frameless full-overlay, no toe kick, laminated 36mm seat slab
  overhanging the carcass front flush over the faces; no front rail.
- Reveals: 20 floor shadow gap / 3 mid / 2 top / 2 sides. Faces
  257 + 190 tall (floor gap raised after viewer review, user flagged
  near-flush bottom face; boxes unchanged, no storage lost).
- Platform bottom + housed back (user structural calls, 2026-08-04):
  bottom is 18 x 576.6 x 914.4 on the floor, sides (18 x 460 x 591.6)
  seat in 6mm rabbets in its top face. Back is 3 x 466 x 890.4 in 6mm
  dados in the sides and slab underside, inset 12mm from the rear; the
  bottom stops at the back's front face so the back slides down past
  it, then glue/brads into the bottom's rear edge. All asserted in the
  model (side min Z == 12, back spans Z12-478, bottom rear == back
  front face).
- Sheets: 2x 18mm + 1x 12mm + one 1/8" quarter sheet for the back.

## Next steps (if resumed)

- User viewer sign-off if desired (`scripts/cad-viewer.sh` + SHOW=1).
- Before cutting: measure ply actuals + slide spec; re-run with updated
  constants; regenerate cutlist.
- Decide pulls and finish. Build, then promote measured values into
  knowledge/woodworking-stock.md and update the retrospective.
