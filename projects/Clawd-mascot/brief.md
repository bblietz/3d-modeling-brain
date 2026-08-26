---
tags: [project, mascot, two-color, voxel]
status: flush narrow-eye redesign 2026-08-04; kit rebuilt, GUI check + print pending
---

# Clawd mascot

Claw'd, the Anthropic pixel-crab mascot, as a two-color desk figure for the Bambu Lab X2D. Voxel model derived pixel-exact from the official sprite (8 x 5 cell grid, `images/clawd-sprite.jpg`): terracotta body with nub arms and four legs, plus separate black eye solids that inlay into sockets for two-color printing. A first attempt as a "logo starburst plushie" was rejected and rebuilt as this crab.

## Artifacts

- CAD and meshes: in this directory (FCStd, combined STL, split body/eyes STLs, two Bambu Studio project 3MFs)
- History: commits `877a673` (first version) through `9a164fc` (final resize), 9 commits on 2026-07-26/27 from the retired FreeCAD repo; full log preserved in [[git-history]]
- Reference sprite in `images/`

## Dimensions and features

| Feature | Value |
|---|---|
| Overall size | 69.85 x 49.2125 x 24.4 mm since 2026-08-04 (flush eyes; was 25.413 tall with proud eyes, nominal 2 3/4 x 1 15/16 x 1 inch) |
| Voxel cell | 8.73125 x 9.8425 mm (non-square: requested aspect differs from the sprite's 8:5 grid) |
| Body height | 24.4 mm; eyes sit FLUSH with the top since 2026-08-04 (historic: 1.013 mm proud, 25.413 mm total) |
| Eye inlay | FLUSH-NARROW 2026-08-04: sockets 4.1659 x 9.9057 mm x 3.0123 deep, width cut 1/3 from the wide 6.2488 ANCHORED ON THE INSIDE EDGES (socket X spans [17.8583, 22.0242] and [47.8004, 51.9663]; eye gap unchanged 25.78); recut in the FCStd (`BodyFlushEyes` feature, `BodyWideEyes` kept hidden), exported as `anthropic-mascot-body-flush.stl`. Historic: wide 6.2488 x 9.9057 (2026-07-31, doubled from 3.1244, centered); original 3.12 x 9.91 with print-proven keeper transform |
| Roundover | 1/32 in (0.79375 mm) on 84 body edges; eye top rims now a 0.2 mm edge break (2026-08-04; the 0.79 roundover suited proud eyes only) |
| Limb taper | 3 degrees on arm tops/bottoms and leg sides, narrowing to the tips |
| Colors | body #CC785C terracotta (extruder 1), eyes #141414 (extruder 2) |

Design rule that made the inlay work: eye-socket edges and eye vertical sides stay square (no fillet) so the two-color fit is exact; only exposed rims get the roundover. Model is a plain Part-workbench boolean tree (17 objects), not PartDesign.

## Print setup

`anthropic-mascot.3mf` and `anthropic-mascot-single.3mf` (single figure; regenerated 2026-07-31 from the updated CAD and round-trip verified, eye placement float32-identical to the print-proven 4-up): X2D 0.6 nozzle machine preset, 0.18 mm Balanced Quality, Bambu PLA Basic in both slots, filament colors #CC785C / #141414, 15% grid infill, no supports, prime tower on, Cool Plate.

`anthropic-mascot-4up-names.3mf` (4-up personalized plate, GUI-authored in Bambu Studio 2026-07-29/30; preserved copy of the pre-regeneration `anthropic-mascot.3mf`): four copies, each with an embossed name on the top face (`@tcharles`, `@jduval`, `@nsumrall`, `@bblietz`, Nimbus Mono PS, 2 mm thick, extruder 2), 0.30 mm Standard on Textured PEI Plate. The eyes carry a GUI-applied transform: +0.64 percent scale plus a 2.47 mm move toward the top of the head (the previously noted "1.026x" was a Bambu Studio metadata artifact, see [[clawd-mascot]]). Body sockets were re-cut on 2026-07-30 to conform exactly to the adjusted eyes, closing the seating gap. Not reproducible from the FCStd: the embossed text exists only in that GUI-saved file.

## Low-material variant (2026-07-31)

Keepsake needs no strength; quality stays priority, savings only where
invisible. Decision (grilled): body prints single-color and the eyes
become separate press-fit inlays, eliminating the 60 mm prime tower
(~25-30 g) and all purge waste; body infill drops 15% grid -> 5%
lightning (~5 g, interior only). Geometry, size, walls, shells, and the
smooth-top ironing package are unchanged. Old multi-color 3MFs kept as
the print-proven fallback; 4up-names untouched.

- `anthropic-mascot-kit.3mf` - ONE plate, THREE mascots, two object
  groups printed sequentially (`print_sequence` = by object): group 1
  "Eyes x6" (extruder 2, black, 4 mm tall, prints first), group 2
  "Clawd bodies x3" (extruder 1, terracotta). One filament change for
  the whole plate, no tower, no per-layer purge. Clusters 90 mm apart
  for sequential-print toolhead clearance. Global settings: lightning
  5%, smooth-top ironing package. Superseded: the earlier 3-plate kit
  layout (its plate 3 rendered EMPTY in the GUI despite passing a CLI
  round trip - GUI check is mandatory for authored plate structures).
- Coupon v1 result (2026-07-31): ALL clearance-based eyes too loose.
  Calipers: pocket printed 6.23 x 9.84, the 0.05 eye printed
  6.09 x 9.89. Deviations are asymmetric (pocket shrinks, eye X shrinks,
  eye Y grows from first-layer flare), so `eye_fit.py` now uses a
  measured zero-fit basis (FIT_X 6.2888, FIT_Y 9.7557) and coupon v2
  eyes carry TOTAL per-axis INTERFERENCE 0.02 / 0.08 / 0.14 mm
  (dots 1 / 2 / 3, snug slide -> firm press). Coupon v2 verdict: 1 dot
  (0.02 mm total per axis) fits great; FINAL_INTERFERENCE 0.02 baked,
  final eyes 6.3088 x 9.7757 x 4.0257.
- `eyes-final.stl` - regenerate after baking the coupon winner into
  `eye_fit.py`, then rebuild the kit.
- `eye_fit.py` - parametric build123d source, self-verifying against the
  wide-body mesh; sockets match the doubled eye at 0.0000 mm.
- NOTE: the old multi-color 3MFs still carry the NARROW eyes; they are
  the fallback for the original look only.

## Multi-color export lesson

Bambu Studio ignores object-level basematerials in standard 3MFs. The shipped file is a project 3MF assembled via the bambu-studio CLI (`--assemble`, per-part filament ids) with `filament_colour` patched, round-trip verified. X2D preset `inherits` chains also had to be flattened to self-contained JSONs because the CLI silently falls back to base values. Both procedures are recorded in the `/3d-model` skill.

## Infill revision after first kit print (2026-07-31)

First kit print: bodies came out visibly hollow - lightning 5% only
scaffolds top surfaces, so a display body sliced with it has an
essentially empty interior. Too weak, and the by-object grouping already
saves the filament, so the kit 3MF was revised in place:

- Bodies object: per-object overrides `sparse_infill_density` 20%,
  `sparse_infill_pattern` grid, as object metadata in
  `model_settings.config`. Eyes and global process keys untouched.
- Bottom-heavy, take 1 (FAILED - crashed the slicer): a
  `Metadata/layer_config_ranges.xml` height range with
  `sparse_infill_density` 100%. It loaded, round-tripped through the
  CLI, and survived GUI saves, then SEGFAULTED Bambu Studio
  02.08.01.55 at "Slicing mesh" (GUI and CLI alike). Bambu height
  ranges support ONLY `layer_height`; the same range with
  `layer_height` slices fine, which isolated the root cause. Lesson: a
  CLI round trip does not validate sliceability - always test-slice
  authored 3MFs (`bambu-studio --slice 1`).
- Bottom-heavy, take 2 (working): modifier part "Bottom ballast solid
  third" - a box mesh (object id 6 in `object_2.model`, ids are
  globally unique across sub-model files) added as a
  `subtype="modifier_part"` with per-part `sparse_infill_density`
  100%, spanning body z 0-8.13 mm of 24.4 mm. Verified by CLI slice:
  exit 0, filament 1 usage 88.7 g -> 134.3 g (+45.6 g ballast across
  3 bodies, ~15 g each net).
- User edits meanwhile (2026-07-31 GUI session): eyes removed from the
  kit (they printed before the cancelled first run), purple text
  `text_shape` parts on each body top (@tcharles, @jduval, @nsumrall,
  extruder 3), project config re-synced to live AMS (6 filaments,
  bodies now filament 1 orange #FF9016; terracotta #CC785C is gone).
  These edits were exonerated in the crash bisect.
- Backups in session scratchpad: `anthropic-mascot-kit.lightning-backup.3mf`
  (pre-infill), `kit-user.3mf` (user's crashing GUI save).

## Flush narrow eyes (2026-08-04)

User direction: eyes 1/3 narrower than the wide version, ANCHORED ON THE
INSIDE EDGE of each eye (material comes off the outboard sides, eye gap
unchanged), and FLUSH with the head top instead of 1.013 mm proud. Fit
relaxed without a new coupon: the filament manufacturer changed and the
print-validated +0.02 mm interference eyes went in smash-tight, so the
fit dropped one 0.06 coupon step to -0.04 mm total per axis (clearance);
if the printed fit misses, eyes are cheap to reprint a step tighter.

- Sockets: 4.1659 x 9.9057 x 3.0123 mm, X spans [17.8583, 22.0242] /
  [47.8004, 51.9663] (inside edges of the wide sockets preserved). Recut
  via the surgical pattern (conformal eye plugs fused back into
  `BodyFilleted`, then new pockets cut) as baked feature `BodyFlushEyes`
  in the FCStd; `BodyWideEyes` kept hidden as the wide fallback. Exported
  `anthropic-mascot-body-flush.stl` (watertight, sockets verified from
  section loops, exterior bit-identical bbox).
- Eyes: 4.1659 x 9.7157 x 3.0123 mm (zero-fit basis FIT_X 4.2059 /
  FIT_Y 9.7557, deviations transferred as absolute offsets from the
  6.25-wide coupons; FINAL_INTERFERENCE -0.04; 0.2 mm top-rim edge
  break). `eye_fit.py` updated, self-verifying; `eyes-final.stl`
  regenerated; the fit coupon regenerated at the new width with the
  dot ladder re-centered to -0.04 / 0.02 / 0.08 as the fallback.
- Kit: `anthropic-mascot-kit.3mf` rebuilt by mesh swap (the 3-body
  merged mesh and the 6-eye mesh replaced at identical placements; eye
  group item z 2.01285 -> 1.50615 for the shorter eyes; face counts
  updated; texts, ballast modifier, per-object settings untouched -
  only 4 zip entries changed, everything else byte-identical). CLI
  round trip preserves colours/extruders/diff-list; test slice exit 0:
  129.94 g total, filament 1 bodies 127.98 g, filament 2 eyes 0.87 g
  (was 1.26 g), filament 3 texts 1.09 g; eyes print first (layers
  0-15). Pre-swap kit backed up as
  `anthropic-mascot-kit.wide-eyes-backup.3mf` - it matches the ALREADY
  PRINTED wide-socket bodies, keep it.
- 2026-08-07: bed-adhesion learnings from [[sharks-nametag]] applied to
  the kit. `curr_bed_type` was already "Textured PEI Plate" (GUI
  session heritage) but the four PLA slots carried the flattened
  preset's 55C `textured_plate_temp[_initial_layer]`; patched to
  Bambu-stock 65 (support slots 5-6 untouched) with the temp keys
  listed in filament diff slots 1-4 so the GUI cannot silently reset
  them (slot layout [0]=process, [1..6]=filaments, [7]=machine).
  Round-trip verified, test slice exit 0 (same 129.94 g), and the
  sliced gcode commands M140/M190 S65. Pre-patch copy in the session
  scratchpad. Same shrinkage-stress rationale as the nametag disc: the
  ballast makes the body bottoms near-solid.
- Pending: GUI check of the rebuilt kit (mandatory for authored 3MFs),
  then print. NOZZLE CAVEAT before printing (lesson promoted to
  [[printer-x2d]]): the 0.4 nozzle went in on 2026-08-06 for the
  nametag; this kit targets the 0.6 - swap back and confirm Studio's
  Prepare machine matches, or Studio silently re-profiles the job.
  The flush fit also makes printed Z accuracy visible for the first
  time (a proud eye hid height error); check flushness on the first
  print.

## Open items

- 2026-08-04: flush narrow-eye kit rebuilt (section above); GUI check
  and print pending. Wide-eye print outcome so far: bodies printed
  2026-07-31 and the +0.02 wide eyes pressed in SMASH-TIGHT with the
  new filament brand (fit calibrations are filament-brand-specific).
  Record remaining wide-print results (bottom-heaviness, text finish)
  and the flush-print fit in the [[clawd-mascot]] retrospective.
- Previously: GUI check passed: the fixed kit sliced correctly and the
  3-body print started 2026-07-31 (orange bodies, purple name texts,
  solid bottom-third ballast).
- 2026-08-01: eyes grafted back into the kit (the user had deleted
  them to save print time on the body reprint; they were restored from
  the pre-edit Bambu-written round trip, final 0.02 mm interference,
  now object 7/mesh 8, extruder 2 = AMS black). Verified by CLI test
  slice: exit 0, filament 2 used 1.26 g, eyes print first (first
  by-object segment tops out at z 4.08 mm). GUI re-check pending. The
  eyes-less variant is backed up in the session scratchpad
  (`kit-noeyes-backup.3mf`).
- Previously: printed 2026-07-30 with flush eyes; the keeper eye transform is baked into the CAD (2026-07-31) and all single-figure artifacts regenerated from it. Note: the former Part::Fillet features are now baked Part::Feature solids, so a GUI recompute cannot resurrect the pre-fix geometry. Learnings: [[clawd-mascot]].

## Related

- [[printer-x2d]]
- [[freecad-setup]] (the project where this was built)
- [[clawd-mascot]] learnings note (to write after printing)
