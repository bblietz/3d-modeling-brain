---
title: Stackable cable bin
type: project
status: CAD complete, 3MF sliced, decisions taken 2026-10-25, awaiting the colour and the coupon print
printer: Bambu Lab X2D, 0.6 high-flow nozzle
material: PLA Basic (PETG until 2026-10-25)
tags: [bin, storage, stackable, dovetail, crush-ribs, pla, x2d]
---

# Stackable cable bin

Brian's ask (2026-10-25): a bin for cables, 16.75 in long x 4 in wide x 4 in
tall, stackable, split so it fits the X2D, four bins total.

Sign-off page: [[options]] (`options.html`, published as a private artifact:
https://claude.ai/artifact/3QZNtCDUcGY7G7snwYpHRs).

## Design as built

- **Overall** 425.45 x 101.6 x 101.6 mm (16.75 x 4 x 4 in), open top.
- **Split** once at mid-length into two 212.725 mm halves: half A (dovetail
  tails) and half B (sockets). One plate holds A and B, so one print is one
  bin. Four runs of plate 1 give the four bins.
- **Shell** 1.24 mm walls and floor (2 lines of the 0.6 nozzle, the printer
  minimum; 1.86 mm until Brian said 2026-10-25 the bins sit in a drawer with
  three sides against its walls and carry no real load), R10 outer
  vertical corners at the closed ends, uniform shell via `offset()`.
- **Foot** the bottom 8 mm is a 45 degree flare (horizontal inset 8 mm). It is
  the stacking foot: it seats on the lip chamfer of the bin below.
- **Lip** top band 4.0 mm thick x 6 mm tall with a 45 degree transition under
  it and a 1 mm 45 degree chamfer on the inner top edge. The chamfer is the
  seat; the band stiffens the 17 in rim.
- **Stacking** drop 5.0 mm, pitch 96.6 mm = 3.80 in; four bins 15.4 in tall.
  Posts stop 7 mm below the rim so the foot above clears them by 2 mm.
- **Joint** two vertical dovetails (neck 5, head 9, depth 5 mm) on internal
  posts 8 mm long x 15.5 mm deep (12 until the weight cut), up to 7 mm below the rim. The tail's
  underside slopes at 50 degrees from z = 6.0 at the joint face to z = 12 at
  the tip, so it prints unsupported off A's joint face; B's socket has the
  matching sloped floor and is otherwise open at the top: A drops onto B to
  a hard stop, floors flush. The socket's lowest corner keeps 2.29 mm of
  wall to the flare skin (asserted). Body clearance 0.25 mm per side (0.15
  until Brian's first coupon came back too tight, 2026-10-25); two crush ribs
  per tail (R1 half-embedded cylinders, 0.35 mm proud = 0.10 mm crush, 0.5 mm
  lead-in) on the top 12 mm only, so the crush stroke is short. Dovetail centreline
  set 0.25 mm inboard of the lip's inner face so the tail passes the lip on
  the way in (first version notched B's lip; caught by the sweep check).
- **Holds** pull-apart and shear positively; lifting by B's end carries A on
  the socket floors; lifting by A's end relies on rib friction. A drop of CA
  in each socket makes it permanent (Brian's call, see options page).
- **Lightening** (Brian took both cuts 2026-10-25): 13 vertical slots per
  long wall per half, 6 x 64 mm with rounded ends on a 14 mm pitch (8 mm
  webs), z 18 to 82, starting 10 mm past the joint post and stopping 10 mm
  short of the end corners; a finger scallop in each end wall, 52 mm wide x
  18 mm deep (R28 centred 10 mm above the rim, Brian picked it over plain
  ends); joint posts 8 mm instead of 12. A cable end can poke through a slot
  if pushed, harmless in a drawer. The floor, lip band and foot stay solid; the stack seats on the long
  lips and the end corners.
- **Fit ladder** (plate 2). Brian's first coupon, body 0.15 and crush 0.20
  from [[friction-fits-x2d]] (calibrated with the classic generator at
  0.18 mm layers, eight ribs engaged over about 1 mm), was too tight here
  (Arachne, 0.30 mm layers, four ribs engaged over 11.5 mm). Plate 2 now
  carries four coupon pairs, 14.5 mm slices of the joint with the bed edges
  chamfered 0.5 mm against the elephant foot and 1 to 4 notches on the wall
  stubs: (1) body 0.25 / crush 0.15 / ribs 12 mm, (2) 0.25 / 0.10 / 12, the
  bin as built, (3) 0.25 / 0.05 / 12, (4) 0.25 / 0.10 / 6. Brian reports the
  pair that takes firm thumb pressure and holds; `DT_CLR`, `RIB_CRUSH` and
  `RIB_LEN` move to that rung (an assert keeps the bin on a rung).

## Checks baked into `cable_bin.py`

Bounding boxes of both halves and the assembled bin; one solid per part;
tail and socket bodies clear (0 mm3 overlap without ribs); rib interference
volume matches the analytic lens area (7.57 vs 7.52 mm3); tail rests on the
socket's sloped floor (lowering A 0.05 mm collides); the socket's bottom
corner keeps a full wall of flare skin outside it; the tail's full insertion path from
above the rim sweeps B without touching, lip included; B's lip intact at the
joint; stacked pair clears at the pitch and collides when pressed 0.05 mm
further (seat proven); the slot cut removes exactly the analytic slot area
times the wall (within 1 %) and touches no post; each end wall's rim is gone
over the scoop width and no more; STLs watertight with mesh volume within
1 % of B-rep.

## Print

- Process `0.30mm Standard @BBL X2D 0.6 nozzle`, filament `Bambu PLA Basic
  @BBL X2D 0.6 nozzle` (220 C, textured PEI 55 C, 21 mm3/s), Arachne walls,
  wall_loops 3 (the lip and posts get three lines; Arachne fits two beads in
  the 1.24 mm wall with zero gap fill), 20 % gyroid, 2-loop skirt, no brim,
  no ironing. Built by `pipeline/make_print_3mf.py`. History: the classic
  generator sliced the first version's exactly-three-line 1.86 mm wall as two
  loops plus a loop of 50 mm/s gap fill per layer (8 h 18 min); Arachne made
  it 7 h 02 min / 368 g in PETG; 2-line walls in PLA gave 4 h 58 min / 285 g;
  the slots first sliced at 6 h 41 min because the PETG recipe's
  `small_perimeter_threshold` 10 is a radius and slowed every slot web to
  30 mm/s (see the retrospective); that override is gone.
- Plate 1 (Half A + Half B): 4 h 49 min, 240 g. Plate 2 (coupons):
  28 min, 17 g. Four bins: 19 h 46 min, 976 g.
- Orientation: floor down as modelled; nothing past 45 degrees.
- Assembly: stand B, hold A level above with the tails over the sockets, push
  straight down until the rims are flush. Separate with a straight pull up.

## Files

- `cable_bin.py` parametric source (build123d), self-checking, SHOW=1 pushes
  to the viewer.
- `cable-bin-half-a.stl`, `cable-bin-half-b.stl`, `cable-bin-coupon-a.stl`,
  `cable-bin-coupon-b.stl`.
- `cable-bin.3mf` (plate 1 bin, plate 2 coupon), `cable-bin-slice.json`.
- `pipeline/renders.py` (OpenSCAD renders into `images/`),
  `pipeline/make_print_3mf.py`.
- `options.html` sign-off page.

## Open

- PLA colour. Everything else was decided 2026-10-25: friction hold (no
  CA), scallop ends, 3.80 in pitch, both weight cuts.
- Fit ladder print and the pair that fits (the bin is pair 2 until then),
  then the first bin.
- Open the 3MF in Bambu Studio once to confirm both plates render (GUI is
  ground truth for hand-authored plates).
