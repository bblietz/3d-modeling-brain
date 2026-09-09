---
title: Small lettering on the X2D, turnkey recipe
type: technique
date: 2026-09-08
status: validated
tags: [x2d, lettering, petg, multi-color, recipe]
---

# Small lettering on the X2D, turnkey recipe

Validated on the Sharks name tags: 14 three-color PETG tags, raised white
letters 1.6-1.8 mm wide on a navy banner, 0.4 nozzle, printed 2026-08/09
with clean letters on every tag. Full history in
[[sharks-nametag]] (learnings) and [[brief]] (project log). Start here;
do not rediscover it.

## When this applies

Any raised or inlaid text or thin graphic whose strokes are narrower than
about 2.5 mm at the 0.4 nozzle (about 1.5 mm at 0.2). Symptom without the
recipe: pinprick marks and slivers exactly at crossbar/stem junctions
(A, N, T, R, S), clean straight strokes elsewhere.

## Why the marks happen

Two walls per side at 0.42 mm consume 1.68 mm, the whole stroke. The
arachne beads from both sides collide on the stroke's medial axis and
Studio patches the leftover slivers with gap fill. Nothing on the wall
side (seam, speed, flow, bead minimums, fillets, ironing) can fix a
geometry problem; the stroke has to be filled by continuous lines.

## The recipe (0.4 nozzle, 0.12 mm layers)

1. Locked process (`projects/Sharks-nametag/pipeline/flatten_04.py`
   `SMOOTH_TOP`): no ironing, 2 top walls, top speed 60, seam_gap 0%,
   small perimeters 30 (threshold 10), gap fill 40, arachne with
   wall_distribution_count 3, wall_transition_filter_deviation 50%,
   min_feature_size 10%, min_bead_width 50%, skirt 2 loops / 3 mm / 1
   layer (the skirt primes the nozzle; without it the first island fails),
   first layer 30 / 50 mm/s, prime tower brim 5 + rib wall + fillet wall.
2. Letter modifier part over the letters only (outlines buffered 0.3 mm,
   z from 0.04 below the letter tier to 0.08 above): `wall_loops 1`,
   `top_one_wall_type all top`, `top_surface_line_width 0.3`,
   `internal_solid_infill_line_width 0.3`, `infill_direction 90`.
   At 0.2 nozzle drop the two width keys (0.22 lines are already fine).
3. Object key `detect_narrow_internal_solid_infill 0` (object level via
   the CLI assemble list `print_params`; without it the letter cores
   revert to concentric beads and the marks return).
4. Parity check: solid fill alternates 90 degrees per layer, so verify on
   the real part's layer count that the top-layer lines run ALONG the
   stems (Sharks tag: 37 layers, direction 90). A coupon with a different
   parity gives the opposite verdict.
5. Side effect of the object key: every narrow internal-solid island in
   the object turns rectilinear (it hit the navy back inlay in layers
   2-4). Add a second modifier over such regions with
   `internal_solid_infill_pattern concentric`.
6. 3MF rules: per-part metadata holds region keys only and sits before
   `<mesh_stat/>`; object keys go through `print_params`; Studio resets
   any key missing from `different_settings_to_system`, so list every
   recipe key there.

## Procedure next time

1. Model as usual with `/3d-model`; keep letter strokes >= 1.5 mm at 0.4.
2. Build with the Sharks pattern: `pipeline/fillcore_mod.py` gives
   `letter_geometry`, `modifier_2d`, `extrude`, `inject_modifier`,
   `check_object`, `check_config`, `check_tower`, `patch_config`.
   `batch_roster.py` shows a single-object build, `plates.py` a
   multi-plate one.
3. Verify offline before printing: `pipeline/graft_slice.py` (slices a
   CLI export; needs the plate `model_instance`, `filament_map` Manual,
   and a tower clear of the part) then `pipeline/toolpath_voids.py
   --layout tag` (visible stacked voids 0.00, top fill direction along
   the stems) and `pipeline/gcode_features.py --baseline` to prove the
   modifier changed nothing outside the letters.
4. If the letters differ in scale, font, or nozzle, print ONE thin
   letters-only coupon plate (`pipeline/fillcore_coupons.py`: letters +
   0.24 mm of substrate on a 0.3-0.4 mm slab, control + two variants,
   15 min at 0.4) before the real part. Match its layer-count parity to
   the part. The metric rejects variants; the eye ranks the survivors
   (it keys on fill-line starts and dimples, not sub-0.15 mm slivers).
5. Print the part once as a gate, then the batch.

## Studio checklist (every print)

- Select the printer preset for the installed nozzle BEFORE opening the
  file (Studio silently re-profiles otherwise); machine preset and
  physical nozzle must match.
- Check the AMS mapping rows in the Send dialog (Sharks: white slot 4,
  navy 3, cyan 2); AMS sync overwrites project colors on connect.
- Flushing Volumes: Re-calculate. Studio's values for Bambu PETG Basic
  white / navy #00395E / cyan #31BAD6 (as printed 2026-08-26): from white
  223 to navy, 260 to cyan; from navy 629 to white, 430 to cyan; from
  cyan 492 to white, 182 to navy (mm3). CLI exports carry a 280
  placeholder in a 2 x 3 x 3 block; a 16-entry block makes Studio
  serialize NaN.
- Textured PEI 70 C, top vent open, chamber fan on cool (chamber settles
  at 42-44 C over a 70 C bed; fine for PETG).
- Real print time runs about 1.4x the slicer estimate on
  color-change-heavy plates.

## Do not retry

Ironing on PETG (pits and smears), seam gap / speed / flow tweaks,
min_feature_size and min_bead_width alone, outline micro-fillets, two
walls plus fill (worst variant), wider top lines, the connected monotonic
top pattern (plate-position sensitive), scaling the part up, the 0.6
nozzle, and the 0.2 nozzle as a first move (works, but 2.3x the time
plus a stringing tune; unnecessary with this recipe). PLA Basic softens
at 57 C: not for tags that live in sun or cars; PETG (HDT ~70 C) is the
floor, ASA if a hot dashboard is a hard requirement.

## Prime tower

Rule (asserted by `check_tower`): parts keep their slots; the tower takes
the free spot closest to the bed center; brim >= 12 mm from every part
and >= 15 mm from the bed edges; never the raw back-left corner (the one
place a tower peeled). Rib wall + fillet wall + 5 mm brim.

Related: [[printer-x2d]], [[feedback-raised-letters-recipe]],
[[feedback-minimal-test-coupons]].
