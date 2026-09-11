# Fork A: engine touches (Plan 3 Task 1) in the mirror

Files changed (mirror only): `.vault/scripts/cabvoice.py`, `.vault/scripts/test_cabvoice.py`, `.vault/knowledge/speaker-cab-voicing.md` (calibration table block only). `calibration_table.py` needed no path fix (`parents[3]` resolves to `.vault`).

## Symbols, file order (embed by name with `symbols` mode)

cabvoice.py, changed: `MIN_PORT_LENGTH_MM` (24.0), `Port` (fields `pinned: bool = False`, `fb_override_hz: float | None = None`), `port_dims` (clamp remedy text), `size_port` (new `pinned_mm` parameter and branch), `dims_for_volume` (floors over the limit: strict raises, non-strict records "width floor" / "height floor" conflicts and fixes the axis at the floor), `Constraints` (fields `port_tube_mm`, `fb_hz`; validation in `__post_init__`), `propose` (Fb override, pinned tube, floor blockers, pinned clamp warning), `render_markdown` (pinned tube label, Fb override line), `_build_parser` (`--port-count` on both modes, `--port-tube` and `--fb` on propose, `--port-tube` on evaluate), `main` (constraints from the flags; evaluate's port from `--port-tube`).
cabvoice.py, new: `tube_from_table(diameter_mm) -> float` (directly above `snap_tube_id`).

test_cabvoice.py, changed: `test_size_port_grows_when_too_short` (outcome moved, see deviations), `_matrix_params` and `test_evaluate_reproduces_propose` (sixth parameter `tube`, one pinned 101.5 row per speaker), comments in `test_propose_prediction_follows_clamped_port` and `test_propose_mono_2x12_uses_one_port_per_driver` (20 to 24).
test_cabvoice.py, new (appended under `# ---- Plan 3 Task 1: engine flags, port minimum, size-limit blockers ----`): `test_min_port_length_is_the_back_panel_plus_the_flange_ring`, `test_tube_from_table`, `test_constraints_validate_the_pinned_tube_and_fb`, `test_size_port_pinned_tube_neither_grows_nor_snaps`, `test_size_port_pinned_tube_clamps_a_short_port`, `test_propose_pinned_tube_sheet_and_clamp_warning`, `test_propose_pinned_tube_air_speed_warns_instead_of_growing`, `test_propose_fb_override_is_applied_and_recorded`, `test_propose_width_floor_over_the_limit_is_a_blocker`, `test_propose_height_floor_over_the_limit_is_a_blocker`, `test_cli_port_tube_fb_and_port_count`, `test_cli_evaluate_port_tube_is_a_validated_diameter`, `test_cli_width_floor_blocker_exits_2_with_the_sheet`, `test_cannabis_rex_roots_port_loop_cases`.

## Message formats (the skill and cabreport.py match on these)

- Sheet keys: `port.pinned` (true only with `--port-tube`, on propose and evaluate), `port.fb_override_hz` (the override or null). No port block on closed and open boxes.
- Too short (port_dims, unchanged trigger, corrected remedy): `port too short ({length:.1f} mm) for Fb {fb:.0f} Hz in {vb:.1f} L; clamped to 24 mm; a larger port, a lower Fb, or a smaller box lengthens it`
- Pinned clamp (propose, new): `port clamped at the 24 mm minimum with the pinned {tube:g} mm tube: tuned {fb_actual:.1f} Hz, target {fb:.1f} Hz; a larger tube, a lower Fb, or a smaller box lengthens it`
- Free clamp (propose, unchanged): `port clamped at the size cap: tuned {fb_actual:.1f} Hz, target {fb:.1f} Hz; lower Fb or use a smaller box`
- Air speed with a pinned tube (from `_port_report`, unchanged text): `port air speed {v:.1f} m/s above 17.0 m/s` (the growth message `... still above 17.0 m/s at the maximum port size` never appears for a pinned tube)
- Snap (unchanged): `port diameter snapped to the {tube:g} mm tube (from {solved:.1f} mm)`
- Width floor blockers (propose, exit 2, sheet written, box voiced at the floor): `width floor {w:.1f} mm internal (the driver-count minimum) exceeds the size limit {max:.1f} mm internal` and `width floor {w:.1f} mm internal (pinned width {p:g} mm external) exceeds the size limit {max:.1f} mm internal`
- Height floor blocker: `height floor {h:.1f} mm internal (the cutout minimum) exceeds the size limit {max:.1f} mm internal`. Direct `dims_for_volume` calls (strict) raise `ValueError` with the same text joined by "; ".
- Input errors (exit 1, nothing written): `port tube must be one of 52, 77.3, 101.5, 153.2 mm, not {x:g}`; `give a slot or a pinned tube, not both`; `give --port-tube or --port-diameter, not both`; `evaluate closed-ported needs --port-length and --port-tube, --port-diameter, or --port-slot`; `fb_hz must be positive`. `--port-count 3` is an argparse usage error (exit 2, "invalid choice").
- voicing.md: the Port line reads `round 78 mm (pinned 77.3 mm tube), area ...`; a pinned sheet with an override adds `- Fb override: 55.0 Hz in place of the engine's target`.

## CLI help (verbatim)

```
  --port-count {1,2}    ports per chamber (default one per driver in the chamber)
  --port-tube MM        pin one purchasable tube inside diameter (52, 77.3, 101.5, or 153.2 mm): no growth, no snap; a clamped length or a high air speed becomes a warning
  --fb HZ               tuning override in Hz in place of the engine's target (recorded on the sheet)
  --port-tube MM        the port's tube inside diameter from the table (52, 77.3, 101.5, or 153.2 mm), a validated --port-diameter   (evaluate)
```

## Test counts and commands

- `cd .vault/scripts && .venv/bin/python -m pytest test_cabvoice.py -q`: 397 passed before, 431 passed after (14 new functions, 20 new matrix cases).
- `./run_tests.sh`: 495 passed, 4 failed at first (all four in test_cabmodel.py asserting the 18-name check list while Fork B's port mouth check was already in cablayout.py); the re-run of `test_cablayout.py test_cabmodel.py` alone gives 71 passed, so the shared mirror is green as of this report.
- Calibration table: `.venv/bin/python .vault/projects/Speaker-cab-system/pipeline/calibration_table.py` rewrote the block; one row moved, eminence-red-white-and-blues Fb 74 to 73 Hz (its clamped port is now 24 mm) and its notes text carries the new clamp wording; the header date moved to the run date. `test_calibration_table_matches_engine` passes.

## Numbers the plan can quote (roots tone, min_power_w 30, Cannabis Rex 8 ohm, mirror layout with the fixture aesthetics)

- Default round: 153.2 mm tube (snapped from 113.2), 90.4 mm long, Fb 86.4 Hz; layout: `port fit blocker: chamber 0 port 0: no round port of 153.2 mm fits with 25 mm clearance; raise Fb, use a smaller tube or a larger box, or a front slot`, plus a `net volume` blocker (+5.9 percent, "port not built, so its tube and ring are missing from the inside parts").
- `--port-tube 101.5`: 24 mm, tuned 81.0 Hz against 86.4; layout `port fit pass` (x 82, z 214) and, from Fork B's new check, `port mouth warn: mouth 90 mm from the speaker 0 magnet (42 percent of the mouth), under one diameter (101.5 mm)`.
- `--port-tube 77.3`: 24 mm, tuned 68.4 Hz; port fit pass, no port mouth warning.
- `--port-slot 352 40`: shelf 54.7 mm, Fb 86.4, every check pass.
- `--port-tube 153.2 --fb 95`: 52.3 mm long and still `port fit blocker` (radial clearance, not length), so raising Fb does not rescue the big tube in this box.
- 2x12 mono default: both ports block the same way; the test driver's 60 L at 60 Hz case now grows to 104.7 mm and snaps to 153.2 (the 20 mm minimum stopped at 100 mm and the 101.5 tube).

## Deviations from the design, with reasons

1. `port_dims`'s clamp remedy said "reduce port area or lower Fb"; a smaller area shortens the length a tuning needs (L is proportional to A), which is why `size_port` grows the port on "too short". Corrected to "a larger port, a lower Fb, or a smaller box lengthens it" (Plan 1 text defect, in scope because the design says the clamp text follows the new minimum).
2. The height floor over the limit is a blocker like the width floor (the directive's extension), same non-strict path in `dims_for_volume`.
3. `tube_from_table` is a new helper so the table check lives in one place (Constraints, size_port, and the evaluate CLI share it).
4. `pinned` is true on evaluate sheets made with `--port-tube` (records intent; the design said "a validated --port-diameter", which it also is).
5. `test_size_port_grows_when_too_short` moved from the 101.5 tube to the 153.2 tube: with a 24 mm minimum the solved diameter is 104.7 mm and the locked snap-up rule takes it to 153.2.
6. A pinned clamped port carries two warnings (port_dims's "too short" and propose's "port clamped at the 24 mm minimum ..."), the same pair the free clamp already produced.

## Findings for the plan writer and Fork B

- The layout's `port fit` blocker does not name the longest tube that fits (design section 5 step 1 assumed it does; the Plan 2 addendum's check table claims it, the landed message only lists remedies). Either Fork B extends the blocker (a tube that does not fit at the 24 mm minimum cannot fit at all, so the layout can probe each smaller table tube at 24 mm) or the skill pins the next tube down the table (153.2 to 101.5 to 77.3 to 52, then the slot). Recommendation: the skill steps down the table; it is deterministic and needs no layout change.
- "Raise Fb with the larger tube" is not a remedy for the Cannabis Rex in the roots box (see the fb 95 probe); the slot-first order in the design's trade-off stands.
- `--fb` is uncapped by FB_MIN_HZ and FB_MAX_HZ, per the design's "no other rule"; the plan may want the skill to say what range it uses.
