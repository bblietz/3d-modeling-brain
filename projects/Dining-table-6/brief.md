---
tags: [project, furniture, table]
status: sample-design
date: 2026-08-03
---

# Dining table for 6 (Shaker style)

Sample dining table, requested as "a sample table that can seat 6
comfortably", upgraded on request to medium-high woodworking skill:
Shaker style with real joinery. Built with the `/furniture` skill,
build123d backend. v1 (2x4 pine, pocket screws) is in git-less history
only; this file describes v2, the current `dining-table.py`.

## Seating and dimensions (unchanged from v1)

- Top 1800 x 900 x 26 at 740 mm height. Seats 6 as 2 per long side
  (~770 mm each, 1560 mm between legs) + 1 per end. Knee clearance
  614 mm.
- Assumed material: red oak (4/4 aprons at 22, 5/4 top at 26, 8/4
  glue-up legs milled to 80 sq). Not in [[woodworking-stock]], which
  only lists construction lumber; lumberyard stock, mill to listed
  thicknesses.

## Joinery

Revised 2026-08-04: the user replaced mortise-and-tenon with corner
braces. The base is now knock-down.

- Legs taper 80 -> 48 on the two INNER faces only, starting 20 mm
  below the aprons (z 594). One M8 hanger bolt per leg, 45 deg into
  the flatted inner-corner arris, 30 mm below the top; drill before
  tapering.
- Aprons: square butt ends (1560 / 660), 12 mm reveal from leg faces.
  Corner braces 22 x 60, 45 deg ends (long face 186, short face 142),
  screwed to both aprons (2 x #10 x 45 per end); the bolt crosses a
  6 mm gap to the leg so the nut pulls the leg tight. Model-verified:
  flush bearing on both aprons, gap 6 +-0.5, zero collisions.
- Top: glued panel with 70 mm breadboard ends on a 12 mm stopped
  tongue (stopped 30 mm from edges). Glue the CENTER 100 mm only;
  outer pegs (not modeled) get elongated holes so the 900 mm panel can
  move ~9 mm seasonally.
- Top attachment: 8 shop-made buttons riding a 6 x 6 groove inside all
  four aprons (groove top 12 mm below apron top), one screw each into
  the top. No slots needed; buttons slide with the wood.

## Verification

`dining-table.py` self-checks every run: overall dims, knee clearance,
all 8 tenons housed with matching mortise volume, tongue exactly fills
each breadboard groove, button lips inside groove voids, and zero
part-to-part intersections (17 solids). 4-view render inspected at
each build stage; viewer sign-off pending.

## Buildability (Phase 4)

Blanks: aprons 1560/660 square-ended, braces 190 (45 deg ends), top
panel blank 1720 (incl. tongues) + 2 breadboards 900, legs 714. Legs,
breadboards, and buttons flagged "needs drawing" by the emitter;
aprons are now plain blanks. Base passes a 750 mm doorway and knocks
down flat with a wrench; top detaches with the buttons. Assembly:
brace the apron rectangle, bolt in the legs, square to 1 mm on the
diagonals, tighten, drop top, button it down.

## Artifacts

- `dining-table.py` (canonical source), `cutlist.md`/`cutlist.csv`
  (7 rows, 23 parts), `dining-table.step`,
  `images/dining-table-views.png`, `build-instructions.html`.

## Open items

- Sample only. Before a real build: measure dressed stock, decide
  species/finish, drawbore or peg the breadboards, and get viewer
  sign-off on proportions (taper rate, apron width, breadboard width
  are the taste knobs).
