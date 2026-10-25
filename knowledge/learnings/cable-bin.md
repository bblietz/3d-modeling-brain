---
title: Cable bin retrospective
type: learning
date: 2026-10-25
status: CAD and slice done, not printed
tags: [bin, split-print, dovetail, crush-ribs, stacking, build123d, pla]
---

# Cable bin: what the build taught

Project: [[brief|Cable-bin brief]]. Stackable 16.75 x 4 x 4 in bin split into
two halves for the X2D, four bins.

## Decisions already locked

- Two halves per bin, split at mid-length, A (tails) and B (sockets) on one
  plate; four runs of that plate.
- Vertical sliding dovetails on internal posts, crush ribs on the top 12 mm
  of each tail, sockets closed at the bottom by B's floor.
- Stacking by a 45 degree foot flare seating on a 45 degree lip chamfer,
  drop 5 mm, pitch 3.80 in.
- PLA Basic, 0.6 high-flow nozzle, 0.30 mm Standard, 2-line walls and floor
  (1.24 mm), wall_loops 3 so the lip and posts stay solid (Brian 2026-10-25:
  drawer bin, no real load; PETG and 3-line walls until then).
- Joint coupon on plate 2, printed first.

## What worked

- **Uniform shell by `offset()`** on a filleted-and-chamfered outer body gives
  the flared foot and its matching inner chamfer in one step; the inner
  chamfer falls out of the maths (c = FLARE - FLOOR + WALL(sqrt2 - 1)) and
  needs no separate feature.
- **Joint posts clipped by the envelope** (`post & outer`) instead of
  positioning them clear of the flare; the dovetail then starts above the
  flare zone (z = 10) and the post below it fills the inner chamfer corner.
- **Geometry proofs instead of constants**: an empty intersection of the
  ribless A with B proves the body clearance; the ribbed overlap matches the
  analytic circular-segment volume; pressing the stacked pair 0.05 mm proves
  the seat; sweeping the tail profile from above the rim proves the insertion
  path. The sweep check caught the one real defect (below).
- **OpenSCAD for inspection renders of build123d chunks**: export the chunk
  STLs, import them in a generated .scad with a colour per half, render with
  `--preview --viewall --autocenter`. Proper hidden-surface removal, two
  colours, 6 s for 16 views. The matplotlib renderer hides every concave
  detail of a joint.

## What failed and the fix

- First dovetail position left the tail head 1 mm outboard of the lip's
  inner face. The socket cut (which runs up through the open top) then
  notched B's lip, and the tail would have hit the lip on the way in. Fix:
  centreline set from the lip's inner face minus a 0.25 mm gap, post made
  15.5 mm deep to keep the inner cheek. Lesson: a drop-in feature must clear
  everything ABOVE its seat, not just its socket; sweep it.
- An 8 mm bottom chamfer cannot wrap an R3 vertical corner (the cone turns
  inside out); the corner radius must exceed the chamfer. R10 ends.
- The build123d empty intersection returns None, not an empty shape; wrap
  volumes in a None-safe helper before asserting on them.
- The first tails had a flat underside at z = 10: a 5 x 9 mm cantilever
  printed over air, on the very face that seats the joint. The slice report
  showed it only as 4 mm of "Overhang wall", easy to wave off. Fix: the
  underside slopes at 50 degrees back to the joint face and B's socket gets
  the matching sloped floor, so the hard stop is face to face and nothing in
  A overhangs. Lesson: any feature that protrudes past a part's own
  footprint needs a printable underside, and the bottom of the socket must
  then stay a full wall away from the outer skin (asserted now).
- A vertical sliding dovetail on an internal post sits inside the foot flare
  zone at the bottom; start it above the flare or check the skin thickness
  at its lowest outer corner.

## Ask the load case before picking walls and material

I defaulted a 17 in bin to 3-line walls and PETG for stiffness and put 368 g
on the page; Brian's first reaction was that 368 g is a lot. The bins sit in
a drawer with three sides against its walls and carry no torsional load, so
2-line walls (the printer minimum) and PLA were right: 285 g and 4 h 58 min,
23 % lighter and 30 % faster, with the same geometry proofs passing. Lesson:
for storage parts ask where it lives and what it carries before choosing the
wall count and the material, and put the grams on the page as a decision,
not a footnote. Where the material goes in this bin (solid CAD volumes at
1.24 mm): walls 50 %, floor 17 %, joint posts 26 %, lip 8 %; the slicer
hollows the posts, so in the print they are closer to a fifth.

## Walls that are exactly N lines wide: use Arachne

A 1.86 mm wall is exactly three 0.62 mm lines. The classic wall generator
(the X2D stock presets) sat on that knife edge and printed two loops plus a
loop of gap fill per layer: gap infill at 50 mm/s was half the outer-wall
length and the inner wall only 0.4 of it. `wall_generator` arachne gives
three clean beads, zero gap fill, and 8 h 18 min became 7 h 02 min for the
same plate. Either pick wall thicknesses a little OVER an integer number of
lines (1.9 for three) or set Arachne, and read the feature breakdown of the
slice before quoting a time. The 2-line 1.24 mm wall sliced under Arachne
with wall_loops still 3 also shows zero gap fill: Arachne fits two beads and
leaves the three-loop setting to the lip and posts.

## A theorem worth remembering

A joint assembled by one straight motion cannot positively lock against
that motion's reverse with rigid geometry alone. Hermaphroditic halves make
it worse (any Z-stop contradicts the mating stop). So: positive stop one
way, friction (crush ribs), glue, a snap, or a pin the other way. Decide
which and say so on the sign-off page.

## Measured fits

None yet. The crush-rib numbers (0.15 mm clearance, ribs 0.35 mm proud) are
the PLA calibration from [[friction-fits-x2d]] and the bin is PLA, so the
coupon on plate 2 is a confirmation; record the result here.
