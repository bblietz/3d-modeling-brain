---
name: speaker-cab-plan-2
description: Retrospective for Plan 2 of the speaker cab system (layout kernel cablayout.py, CAD layer cabmodel.py, engine and catalog touches, site-default fixture), with the open items for Plan 3
type: learning
status: complete
created: 2026-09-11
tags: [learning, speaker-cab, generator, cad, retrospective]
---

# Speaker cab Plan 2 retrospective

Plan: [[plan-2-generator]]. Design: [[2026-09-10-plan-2-generator-design]] (approved 2026-09-10, section 13 amendments). Executed 2026-09-10 to 2026-09-11 on main, range e7931ab..7f2c09a, subagent-driven: implementers Sonnet 5 (Task 2 on Fable 5.1), every review Fable 5.1, controller Fable 5.1.

## What was built

- `scripts/cablayout.py` and `scripts/test_cablayout.py` (42 tests including a 1200-case matrix on live engine proposals: 1026 clean, 24 port-fit blockers, 150 engine power stops, worst clean net delta 1.1 percent on a hardwood shell).
- `scripts/cabmodel.py` and `scripts/test_cabmodel.py` (23 tests; CAD matrix 12 builds default, 60 with `CAB_FULL_MATRIX=1`; no-exemption interference with every glued pair measuring 0.0 mm3; air within 0.01 L of the layout).
- Engine touches in `scripts/cabvoice.py` (397 tests): `PORT_TUBE_ID_MM` and `snap_tube_id` in `size_port`, `SHELL_MARGIN_MM 44`, `CUTOUT_GAP_MM 68`, `HARDWOOD_FLOOR_EXTRA_MM 2`, `min_internal_height_mm`, floors re-applied after every rescale, `inside_parts_l` in `volumes`, `port_l` as the port air inside the box, the grow loop settling on parts and floors; calibration table regenerated (every row moved with the inside-parts allowance; Heritage G12H(55) reads tight at Qtc 0.605).
- `scripts/cutlist.py` `extra_lines` (3 tests); twenty catalog notes with `frame_diameter_mm`, `magnet_diameter_mm`, `magnet_diameter_estimated` through `projects/Speaker-cab-system/pipeline/catalog_fields.py`.
- Fixture `projects/Speaker-cab-system/fixtures/site-default/`: the 20 x 18 x 11 in closed-ported tolex 1x12 with a G12H Anniversary, reproduced at 0 mm off, 18 checks pass with one informational spans warn, port 101.5 x 40 mm, Fb 67.4 Hz, net 42.08 L equal to the sheet, mass 17.0 kg, tolex 0.92 yd.
- Full landed suite 465 passed in about one minute.

## Process: plan first as tested code

The plan's code was developed and tested in a mirror (`projects/Speaker-cab-system/pipeline/plan2-mirror/`) by three Fable 5.1 forks before the plan was written, then embedded by `pipeline/embed_plan_code.py` (`--check` proves the plan equals the mirror). Execution was transcription plus review. Every task's transcription was byte-exact; every defect the reviews found was a defect in the plan's own code, fixed in the landed file, the mirror, and the plan together, so the three stayed identical to the end. This is the process to repeat: the pre-flight is by construction, and a fix wave is a mirror edit plus a re-embed.

## What the reviews caught (all plan-code defects, none transcription)

- Task 2: the size-limited propose branch broke the gross identity because the grow loop settled on the box before the parts; root cause a silent 0.1 percent tolerance in `dims_for_volume`. Fixed with a parts-and-floors settle criterion and the net following the box; six limited cases now reconcile within 0.001 L.
- Task 4: a missing port key raised `KeyError` instead of `ValueError`; only three of the mirrored engine constants were asserted. Fixed; the `sheet` check now warns when the sheet's `prediction_status` differs from the engine's.
- Task 6: the round port placement tested radial clearance only while the tube overlapped the envelope axially, so a tube ending up to 25 mm behind the magnet could sit inside its footprint. Fixed with an axial standoff on the magnet's rear face (the basket's rear annulus keeps the strict test because the basket cylinder is a bounding model); a baffle guard added. Second round: the blocker's remedy text pointed the wrong way ("lower Fb, larger tube" lengthens a port); corrected to "raise Fb, use a smaller tube or a larger box, or a front slot" in the code and the construction note; ring-to-ring clearance added for multi-port chambers.
- Task 7: the mirror's fixture paths depended on the file's depth; replaced by `FIXTURES` and `SITE_DEFAULT` lookups that resolve from scripts/ and from the mirror.
- Task 9: `overlap_volume` swallowed boolean exceptions into a clean pass; now failures propagate (a `None` from `Solid & Solid` is the library's no-intersection answer in build123d 0.11.1); `assert_no_overlap` raises explicitly; the 2x12 slot demo and the matrix helper lost their 1 mm cheek slivers.

## Starting values set during execution

- Fixture tone `min_power_w` 45 (the site's 30 W speaker against the shared 60 W target is a power stop); fixture port 101.5 mm at 40 mm because the 77.3 mm tube cannot tune the site box above the 20 mm minimum.
- Demo configurations for the render CLI use eminence-cannabis-rex at 8 ohm on tone-roots with `min_power_w` 30.
- Engine `TUBE_WALL_FALLBACK_MM`, `JACK_PLATE_H_MM`, and the inside-parts constants mirror the layout's values; `--brace-l` now means extra bracing beyond the modeled center brace.

## Deviations from the design

All recorded in the design addendum's section 13, plus: the CAD layer's STEP and renders carry the components (speaker envelopes, plates, handle, feet) as labeled solids while the cut list and part count use parts only; `overlap_volume` is the non-asserting form the checks use; the `sheet` check's `prediction_status` warn; the exploded view places parts by centroid offset, so the speaker envelope ends behind the exploded baffle rather than in front of it.

## Known limits

- Round-port closed-ported cases whose port snaps to the 153.2 mm tube (Cannabis Rex and similar in small boxes) end in `port fit` and `net volume` blockers; the skill's loop (Plan 3) re-runs the voicing with a higher Fb, a smaller tube, a larger box, or a front slot.
- The engine's hardwood internal width is 2 mm over the layout's chamber (18 versus 19 mm shell terms); the floors carry the difference and the volume check absorbs it.
- The port mouth clearance rule (about one port diameter from the magnet face) is not modeled; the 25 mm standoff is a mechanical margin only.

## Final whole-branch review

Fable 5.1, range e7931ab..857d23c on the landed paths, verdict "with fixes", no Critical; the fix wave landed as 7f2c09a and the re-review found nothing new: the three layers close on the fixture to the last digit (inside parts 1.8043 L in the sheet and the layout, air within 0.00 percent), the 1200-case matrix proves the engine floors and the layout margins agree on both lines, and nothing a builder would cut was wrong. Important findings, all fixed in the final wave: the fixed-baffle dado was attached as a feature but never noted on the shell cut list rows; the `cab.py` template found the vault by a fixed depth (`HERE.parents[3]`) and would fail at the design's per-order path, and no test pinned the exit-2 contract; the construction note contradicted the code on PVC mass, the site box net (44 L stale against 42.5 closed and 42.1 ported), and the slot port dropping the bottom dado. Minor items folded into the same wave: the no-fit port blocker's remedy tail, unused imports and `globals()` lookups in the CAD layer, relative paths and `cab_json` in the `files` block, a duplicate `part count` check name, the three Task 2 constants asserted against the engine, the tube row's wall thickness, ring and cheek note wording, float noise in the report. The review triaged every per-task Minor: the rest is left for Plan 3 or moot, listed in the ledger.

Design-level items the review raised for Brian, not encoded:

- Every closed-ported round proposal for the Cannabis Rex under the roots tone solves a 113 mm port, snaps up to the 153.2 mm tube (area nearly doubles), and the layout rightly blocks it in every configuration probed (1x12, 2x12 mono, 2x12 stereo); the next tube down clamps at 20 mm and detunes. The tolex line's headline speaker with a tight low end has no buildable round port from the default proposal; the front slot is the answer. Plan 3's loop must handle this from its first order, and the engine could report both candidate tubes (snapped down with its detune, snapped up with its length) so the loop can choose.
- `MIN_PORT_LENGTH_MM` 20 sits below the layout's natural minimum of 24 (back 12 plus ring 12), which is why an 8 mm planed ring can appear; raising the engine minimum to 24 removes the case.
- A port mouth 25 mm behind a magnet inside its footprint is allowed; common practice keeps one port diameter clear. Decide before the first ported build.

## Open items

- **Plan 3 (skill):** done, see [[speaker-cab-plan-3]].
- **Later:** per-impedance catalog sets; measured finger width, flange thickness, corner leg length, and jack plate cutout from purchased parts; a vertical 2x12; a tolex-line dovetail if asked; a port mouth clearance rule; the magnet-to-back check to include the back stiffener's 18 mm and the open and semi-open panels; the strap handle check to report the center-of-mass offset from the panel center (today the handle is placed at the center of mass, so the check cannot fail).

## Decisions already locked

- Finger joints on both lines; through dovetail as the hardwood option; no corner posts.
- Finger width half the panel thickness, odd count, full fingers both ends, front finger on top and bottom.
- Dovetail: tails on the sides, pins on top and bottom, half-pins, 1:8, pin half thickness, tail 30 mm target.
- Layout kernel plus CAD layer; `cab.py` thin; `cab.json` is Plan 3's input.
- Grill frame on the flanges, 12 x 40 strips, 20 mm recess kept, 44 mm shell margin, 25 mm brace and divider margin, 68 mm between 2x12 cutouts, engine floors follow (2x12 minimum 29.8 in external), hardwood floors plus 2 mm.
- Baffle mount parameter, floating default, fixed in a 6 mm dado.
- Strap handle default on both lines; handle type a parameter.
- Tube table 52.0, 77.3, 101.5, 153.2 mm snapped in the engine; hard maximum 153.2; default start 77.3.
- Two-step speaker envelope (basket at the cutout diameter, then the magnet plus 12 mm cover allowance, 185 mm fallback; flange disc from the frame field); axial standoff on the magnet's rear face only.
- Divider without cleats; the baffle and back screw into its edges.
- `inside_parts_l` in the engine's volumes restates the layout's part rules (accepted duplication, engine must not import the layout); `port_l` is the port air inside the gross box.
- Execution on main with explicit-path commits; implementers use their own session's attribution trailer.
