---
title: P-Bass pickup height gauge
status: CAD and 3MF built and slice-verified 2026-10-13, waiting on Brian's look; not printed
created: 2026-10-13
tags: [project, 3d-print, petg, bass, setup-tool]
---

# P-Bass pickup height gauge

A four-arm feeler gauge for setting the pickup height on Brian's Fender
Precision Bass. Each arm is one of Fender's published starting points for
the gap between the bottom of the string and the top of the pole piece.
Slip an arm under the string, raise or lower that half of the pickup until
the string just touches the arm.

![[images/gauge-in-use-iso.png]]

## Fender's spec (read 2026-10-13)

Both numbers come from Fender's support site. The procedure, verbatim from
"How do I set up my bass guitar properly?" (updated 2026-07-20): "Depress
strings at last fret. Using a 6" (150 mm) ruler, measure the distance from
the bottom of the first and fourth strings to top of the pole piece. A good
rule of thumb is that the distance should be greatest at the fourth-string
neck pickup position and closest at the first-string bridge pickup
position. Follow the measurement guidelines from the chart below as
starting points." Fender calls these "minimum specifications that are
meant as a guide".

| Pickup type (Fender's row) | Bass side (E string) | Treble side (G string) |
|---|---|---|
| Vintage style | 8/64 in (3.2 mm) | 6/64 in (2.4 mm) |
| Noiseless series | 8/64 in (3.2 mm) | 6/64 in (2.4 mm) |
| Standard "J" or "P" | 7/64 in (2.8 mm) | 5/64 in (2.0 mm) |
| Special Design humbuckers | 7/64 in (2.8 mm) | 5/64 in (2.0 mm) |

Fender's other page, "What are factory setup specs?", gives American and
Mexican Standard basses 6/64 in (2.4 mm) on the bass side and 5/64 in
(2.0 mm) on the treble side, so the two Fender pages disagree by one 64th
on the bass side of a standard P. The gauge carries all four values, so
either page can be followed. Heavier strings and five-strings get more
clearance; the final height is by ear.

Sources:
- https://support.fender.com/hc/en-gb/articles/42584762257819-How-do-I-set-up-my-bass-guitar-properly
- https://support.fender.com/hc/en-us/articles/42507226762651-What-are-factory-setup-specs

## How a P-Bass pickup is laid out (why the arms are this size)

Spec sheets (StewMac, Nordstrand, Amplified Parts) agree: each half-cover is
about 55.5 x 27 mm, the pole pieces are 4.95 mm (0.195 in) rods, and every
string runs BETWEEN a pair of poles 9.5 mm apart. String pairs are 19 mm
apart and the outer string sits about 18 mm from the end of its half.
Fender's vintage-style pickups have flush pole pieces; some aftermarket
pickups raise them.

So the arm goes in ACROSS the string, from the outer edge of the pickup
(bass edge for the E string on the neck-side half, treble edge for the G
string on the bridge-side half). The 10 mm wide arm then spans both poles
of the pair with the string in the middle, exactly where Fender stands the
ruler. The 28 mm arm reaches 8 mm past the string while the 5 mm thick hub
is still outside the cover end.

![[images/gauge-in-use-end.png]]

## The part

- `pickup_height_gauge.py` is the CAD source (build123d); `pickup-height-gauge.stl`
  and `pickup-height-gauge.3mf` are the deliverables.
- Hub 26 x 26 x 5 mm, corners R 6, top edges chamfered 0.6 mm. Four arms
  10 mm wide, 28 mm long, tip corners R 2.5, tip top edge chamfered 0.6 mm
  so it slides under the string.
- Arm thicknesses 2.0, 2.4, 2.8 and 3.2 mm, each debossed 0.6 mm into the
  hub top at the arm's root, reading upright when that arm points away
  from you. Opposite arms are a pair: 2.0 and 2.8 (standard P), 2.4 and
  3.2 (vintage and noiseless).
- 82 x 82 x 5 mm overall, 6.0 cm3, one solid. The model asserts the
  bounding box, one solid, and a probe at each arm tip at its nominal
  thickness.

![[images/gauge-4view.png]]
![[images/gauge-hub-labels.png]]

## Print

- PETG Basic, 0.2 mm nozzle (installed on 2026-10-13 per `scripts/x2d-status.py`),
  process `0.10mm Standard @BBL X2D 0.2 nozzle` with the vault's PETG
  overrides (no ironing, two top walls, arachne, 100% zig-zag infill,
  2-loop skirt). Flat on the textured plate, labels up.
- Why 0.1 mm layers: 0.1 first layer plus n x 0.1 lands every arm
  thickness and the 5 mm hub exactly on a layer boundary. The pipeline
  reads the sliced G-code and checks the last extruded layer near each
  arm tip: 2.0 / 2.4 / 2.8 / 3.2 exactly (`pickup-height-gauge-slice.json`).
- Slice (CLI, `pipeline/make_print_3mf.py`): 50 layers, 1 h 14 min, 7.2 g,
  250 C nozzle, 70 C bed.
- On the 0.4 nozzle the same file would print in about a third of the
  time with `0.20mm Standard @BBL X2D` (0.2 first layer plus n x 0.2
  also lands on every value); the 0.18 mm balanced profile on the 0.6
  nozzle does not, so keep to 0.1 or 0.2 mm layers.
- First print check: measure each arm with calipers. Z on this printer
  usually lands within 0.05 mm; Fender's values are rounded 64ths
  (5/64 in is 1.98 mm, 8/64 in is 3.18 mm), so that is inside the spec's
  own rounding.

## Using it

1. Fret all four strings at the last fret (a capo there frees both hands).
2. Bass side: slide the chosen arm across under the E string from the bass
   edge of the neck-side half until the arm rests on both poles of the
   E pair. Raise or lower that half with its two screws until the E
   string just touches the arm.
3. Treble side: same with the G string from the treble edge of the
   bridge-side half.
4. Standard P: 2.8 under the E, 2.0 under the G. Vintage or noiseless:
   3.2 and 2.4. Fender's factory-specs page would use 2.4 and 2.0.
5. Listen; back off if the E and A warble or the attack goes wolfy
   (magnetic pull), raise if the bass side is weak.

## Page

`gauge-page.html` (renders, spec table, usage) is published privately at
https://claude.ai/artifact/7fBtPeEGbjEZiQmq3z3zQv

## Brian's pickups (2026-10-13)

Brian is waiting on new Fender '62 reissue P-Bass pickups. Those are
Fender's "Vintage style" row: start at 3.2 mm (8/64 in) under the E and
2.4 mm (6/64 in) under the G. The '62 reissue has flush pole pieces, so the
arm rests on the cover and the poles together, which is the same plane.
The 2.8 and 2.0 arms stay on the gauge as the next step closer if the
vintage spacing sounds weak.

## Open

- Not printed yet; the viewer had the model on 2026-10-13 for a look.
- Pipeline tools: `pipeline/make_print_3mf.py` (3MF + verified slice),
  `pipeline/closeup.py` (close-up renders), `pipeline/usage_scene.py`
  (gauge on a mock pickup half).
