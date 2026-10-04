---
type: handoff
project: Skateboard-wall-holder
date: 2026-10-04
---
# Skateboard-wall-holder handoff (2026-10-04, CAD complete, waiting for the 3MF go-ahead)

## State
- `skateboard_holder.py` builds and self-checks; `skateboard-holder.stl` exported (print orientation, 74 x 110 x 40). Model is in the OCP viewer (SHOW=1 after any edit).
- Checks passed: hold_check (lift 11.5 room / 8.25 side, drop-in free), sections viewed, renders in images/.
- Build report: https://claude.ai/artifact/Q9SgmT5dGhR47c1FfW84SQ. Design tool: https://claude.ai/artifact/KLEtv2Tq6MH1gkTuoyo6J6.

## Decisions locked
- Concept A, curved cradle (R20 over the hanger half-round, rims 65/45 deg), 40 mm wide, R27 bowl, reach 74, plate 6 x 110, two #8 countersunk screws, PETG on its side.

## Open
- Brian's OK on the shape, then write pipeline/make_print_3mf.py from projects/Desk-cable-storage/pipeline/make_print_3mf.py (STEM skateboard-holder, LABEL "Skateboard wall hook", wall_loops 3, 20% gyroid, skirt 2 loops, no brim) and slice-verify.
- Truck numbers are estimates; see brief.md Open 2.
