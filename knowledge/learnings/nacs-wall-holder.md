---
title: NACS wall holder (Tesla Wall Connector Gen 3)
type: learning
project: NACS-wall-holder
created: 2026-09-18
tags: [x2d, petg, openscad, nacs, tesla, fixed-cleat, docking-kinematics, dual-nozzle-support]
---

# NACS wall holder

Wall dock for the Tesla Gen 3 Wall Connector handle: a drum on a square plate, the wand
out of the drum's side at 45 degrees down and 15 degrees off the wall, hanging on a FIXED
cleat in the connector's own lock pocket. Status 2026-09-18: **v7 fit coupon printed, the
wand docks and holds** (Brian: "the last coupon printed great. This is the one."). Status
2026-09-19: **DONE.** The full part (4 in base, round flange, 1/16 in roundovers) is printed,
mounted on the wall and in daily use (Brian: "charger holder is on the wall and working
great"). Project notes: [[NACS-wall-holder/brief]].

## What worked

- **Tesla's own CAD for every mating surface.** Nose outline, lock pocket section and the
  housing behind the shoulder all come from sections of Tesla's NACS STEP
  (`pipeline/bell_sections.py`). Profile plus 0.5 mm all round was called "the correct size"
  on the first coupon.
- **Cleat cut to the pocket.** The pocket's own cross-section less 0.45 mm, 5.9 mm long,
  3.57 mm tall, ramp at 31 degrees from the mouth side to a sharp edge, back face
  overhanging 15 degrees. Tesla's pocket (6.5 x 4.0 mm at the mouth) takes nothing bigger.
- **Cavity as the swept room of the docking motion.** Each 2.5 mm piece of the snug cavity
  hulled with itself tilted 6 and 12 degrees about the nose tip's lower corner. That gives a
  roof 0.5 mm over the tip opening at 12 degrees, and an end wall leaning back 12 degrees,
  with no hand-tuned relief numbers. Docking is grip up, nose in to the stop, grip down.
- **A pose-space check instead of judgement** (`pipeline/insertion.py`): side-view slices of
  the holder against Tesla's real housing mesh, a grid over slide, lift and tilt, a path
  search for the WAY IN (wand grown 0.2 mm) and a HOLD number (how far the hanging load
  must be raised before the wand can come off, frictionless). v7: way in yes, hold 19.6 mm,
  1.87 of 3.57 mm of edge engaged when hanging. It runs in about two minutes.
- **Minimal coupon in the real print orientation.** Nose cavity and cleat only, 3 mm walls,
  0.9 mm base, cut just past the nose shoulder: 1 h 36 min, 59 g. It predicted the full part's
  supports and surface because it printed the same way up.
- **Dual-nozzle support recipe from the CLI.** PETG Basic on nozzle 1, Support For PLA/PETG
  as interface on nozzle 2, Bambu's recommended tree parameters. The project 3MF needs the
  per-variant filament keys expanded, one flush multiplier per extruder, and the prime tower
  moved onto the bed (`pipeline/make_coupon_3mf.py`; details in its comments).

- **Region settings by modifier part, checked in the G-code.** Four cylinders at the screw holes,
  `sparse_infill_density` 100%, injected with the Sharks helpers (`fillcore_mod.inject_modifier`).
  Bambu keeps the "Sparse infill" label at 100% and writes gyroid as G2/G3 arcs, so verify by
  plastic per volume in a window (pads 0.92, plain plate 0.18), not by feature labels.

- **Smoothing the entry without touching the hang.** The ledge inside the mouth became a steady
  0.1 per mm flare on the sides and roof from the nose shoulder to the rim. The floor was left on
  Tesla's line: flaring it too moved the hanging pose from 3.0 to 5.5 degrees of droop in
  `insertion.py`, while the floor-kept version reproduced the validated numbers exactly. A
  volume diff of new against old cavity (room added 2678 mm3, room lost 29 mm3, all in one known
  place) is a quick proof that a "cosmetic" cavity edit only adds room.
- **Shrinking the body round a fixed cavity.** Every body number (plate, drum radius, flange,
  logo) is a parameter and the cavity is placed from the drum surface inward by `cleat_depth`,
  so the 150 mm to 4 in change was five numbers plus `zbudget.py` for `mouth_z`, and the docking
  check came back identical.

- **A rolling-ball roundover on a 3D rim, in OpenSCAD.** The mouth's rim crosses a cylinder and a
  torus and its wedge angle runs from 56 to 157 degrees, so offset tricks give the wrong radius.
  `pipeline/rim_round.py` lets OpenSCAD cut "body shrunk by r minus cavity grown by r", takes that
  solid's rim as the ball-centre curve, settles each centre at exactly r from both real surfaces,
  and writes stations; the model cuts a convex kite (edge, touch, centre, touch) between stations
  and unions the balls back, clipped to the sharp part. Check it on the finished mesh: every new
  surface sample should sit at r from the centre curve (it did, within 0.04 mm).

## What failed

- **Six cavity versions that could not work.** The nose was to be lifted over the cleat under
  a stepped roof. The hanging load levers the wand about the mouth's lip, tip up, which is
  that lift run backwards: any snug-roof length short enough to let the wand in (under
  3.9 mm) let its weight take it out, any longer locked it out. Brian reported "the cleat is
  too small" twice; the cleat was never the problem. A docked-pose clash check and close-up
  renders all passed. See [[feedback-check-docking-and-hold-kinematics]].
- **A hook that was a draft** (v1 to v5): the undercut leaned the wrong way and was invisible
  in whole-cavity renders. See [[feedback-verify-retention-features-closeup]].
- **Treating the nose as a prism.** Tesla's nose tapers about 0.75 mm toward its tip, top and
  bottom. A rectangle model said no design could work; the real mesh found the margin.
- **build123d and hand-drawn plans** for a compound-angle part. Moved to OpenSCAD with renders
  of the real model on Brian's instruction ([[feedback-openscad-for-complex-designs]]).
- **`--preview` section renders.** The docked ghost's clip plane paints over the holder's cut
  face; `--render` is required. And a coupon export without `-D show_wall=false` carries the
  render's 320 mm wall plane into the STL (the slice fails with rc 206).
- **The 50% longer cleat** (requested, built as a separate coupon, retired the same day): it
  overlaps the wand in Tesla's CAD by 31 mm3.

- **A modifier that overhangs the part.** Pads 2.5 mm past the plate edge grew the object's
  outline, the skirt crossed x = 20 mm, and the dual-nozzle slice failed (rc 152). On the X2D the
  two nozzles share x 20 to 256 only; clip modifiers to the part and keep skirts inside that.

- **A clearance step just inside the mouth.** Extra room for the unmodelled grip was added as a
  1.5 mm jump where Tesla's CAD ends, which landed a visible ledge right at the opening (Brian:
  "the entry is rough. It steps in."). Add unknown-shape allowance as a taper from the last known
  section, never as a step, and look at the mouth from the user's side before exporting.
- **A prime tower that only the GUI complained about.** The 150 mm file sliced clean in the CLI
  with the tower's box 9.4 mm from the plate; Brian's Studio session showed "Prime Tower is too
  close to others" and a G-code path conflict at layer 17. His session had been changed (four
  filaments, unsaved edits), so the cause is not proven, but the pipeline now measures the gap from
  the G-code and the holder job wants 15 mm or more. It paid off one change later: with the
  round flange a tree support trunk rooted 20 mm outside the part, 9.3 mm from the tower's base.
  Tree supports roam, so place the tower by the measured gap, not by the part's outline.

- **Two traps in the roundover work.** `use <file.scad>` does not carry the file's `$fn`, so
  helper exports had coarse facets until the scratch file set `$fn` itself. And creased walls put
  the real edge up to 1 mm from where two flat faces would meet, which left a detached sliver;
  pushing the cut's edge corner 3 mm out into the air fixed it (count the bodies after every build).
- **Rounding a load-bearing lip moves the load.** The floor lip is a 67 degree wedge, so a 1/16 in
  ball touches the floor 2.4 mm in from the lip and the hanging wand's rest point moved with it:
  3.0 to 3.5 degrees of droop, 1.87 to 1.75 mm of cleat engaged. Small, but it was only visible
  because the docking check was rerun after a "cosmetic" change.

## Measured fits

| Feature | Modelled | Result |
|---|---|---|
| Nose profile clearance, sides, floor and roof over the tip | 0.5 mm | fits, "the correct size" |
| Cleat in the lock pocket | pocket section less 0.45 mm | catches and holds on the v7 coupon |
| Docking tilt the roof allows | 12 degrees (path needs 9) | docks |
| Nose tip to end wall when hanging | 2.5 mm | over-travel is enough |

## Settings used (coupon, and the same for the full part)

X2D, 0.6 nozzle, `0.30mm Standard @BBL X2D 0.6 nozzle`, Bambu PETG Basic, textured PEI,
plate down. Tree supports (hybrid, 35 degree threshold, top Z distance 0, interlaced
rectilinear interface, spacing 0) with Bambu Support For PLA/PETG as the interface filament on
the second nozzle. Full part adds 3 walls, 20% gyroid and a modifier part that makes the plate
solid for 12.5 mm around each screw hole. 4 in base, drum 80, round flange 104, 1/16 in
roundovers: 5 h 32 min, 241 g (233 g PETG, 9 g support interface), 267 layers, prime tower at
(212, 180). The earlier 150 mm base, drum 100 version was 7 h 47 min, 366 g.

## Result (2026-09-19)

Full print mounted and working (Brian: "charger holder is on the wall and working great"),
holding the wand with its cable wrapped on the drum. This confirms, in daily use, everything
that was untested in the coupon: the housing and grip fit in the deep opening (the last 48 mm
was never covered by a coupon, only by Tesla's CAD plus a 1.6 mm flare estimate), the 4 in
body holds the docking geometry unchanged, the round flange, and the rounded floor lip's small
shift in the hang (3.5 degrees, 1.75 mm of the cleat's edge engaged, computed HOLD 20.4 mm).

## Open

None. The project is closed. Any further change is a new request.
