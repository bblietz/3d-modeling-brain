# Fork B report: layout and CAD touches (Plan 3, design section 6 bullets 6 and 7, section 9 bullets 3 and 4)

Everything below lives in `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/`; the landed `scripts/` are untouched and nothing was committed.

## Symbols changed or added, in file order

- `scripts/cablayout.py`
  - New, directly above `check_layout` (all top-level, addressable by name): `_mouth_rect_overlaps(box, x0, x1, z0, z1)`, `MOUTH_GRID = 24`, `_mouth_coverage(points, inside)`, `_box_inside(box)`, `_circle_inside(cx, cz, r)`, `port_mouth_clearances(lay) -> list` of `(chamber, index, free_mm, obstruction, coverage, effective_diameter_mm)`.
  - Modified `check_layout`: a `# port mouth` block directly after the port fit block.
  - Modified `layout_report`: a local `from dataclasses import asdict` and the key `"aesthetics": asdict(spec.aesthetics)` after `baffle_mount`; the top-level `corner_joint` and `baffle_mount` stay.
- `scripts/cabmodel.py`: unchanged (the CAD layer needed nothing; its four checks follow the layout's fifteen).
- `scripts/test_cablayout.py`
  - Modified `CHECK_NAMES` (15 names, `port mouth` after `port fit`) and `test_matrix_every_configuration_lays_out_or_names_its_blocker` (a `port_mouth_warn` counter in `stats`, two added lines).
  - Appended under `# ---- Plan 3 Task 2: port mouth check, aesthetics block, fixture list ----`: `test_port_mouth_round_pass_and_warn`, `test_port_mouth_slot_no_port_and_unbuilt`, `test_port_mouth_site_default_fixture_warns_behind_the_magnet`, `test_report_carries_the_aesthetics_block`, `test_order_from_ignores_unknown_port_keys`.
- `scripts/test_cabmodel.py`
  - The `# === TASK 12 ===` block now holds `FIXTURE_ORDERS = ["site-default"]`, `DELIVERABLES` (cab.json, cab.step, cutlist.md, cutlist.csv, the five images), `_fixture_dir(name)`, `_run_fixture(name, out) -> (proc, report)`, and `test_site_default_fixture` rewritten on the helper with the 1 mm reproduction assertion kept.
  - Modified `CHECK_LINES` (19 names) and `test_cab_py_finds_the_vault_from_an_order_directory` (`CHECK_LINES[:15]`).
  - Appended under the same Plan 3 comment: `test_fixture_order_runs_clean_with_every_deliverable(name, tmp_path)`, parametrized over `FIXTURE_ORDERS` (exit 0, no blocker, the 19 check names in order, the ten design keys present in `aesthetics`, every deliverable on disk). The dry-run tasks add `"sample-roots-1x12"` and `"rex-roots-1x12"` to `FIXTURE_ORDERS` and nothing else.
- Fixture `projects/Speaker-cab-system/fixtures/site-default/`: regenerated with `EXPORT=1` from the mirror (cab.json with 19 checks and the aesthetics block, cutlist.md, cutlist.csv, images/); cab.step regenerated too but git-ignored by the mirror's `.gitignore`.

## The port mouth rule as implemented

For every built port: the free air along the port axis from the inner mouth to the first solid whose projection overlaps the mouth's cross-section, among the chamber's box parts (cleats, stiffeners, brace, shelf, cheeks) plus the divider and the basket and magnet envelope steps; else the baffle's back face (rear round port) or the back panel's inner face (front slot). A solid that starts behind a round port's mouth, or in front of a slot's, is beside the mouth and ignored. Effective diameter: the tube inside diameter, or the diameter of a circle with the slot's area. Warn when the free distance is under one effective diameter; never a blocker. Coverage, the fraction of the mouth the obstruction faces, is sampled on a 24 x 24 grid and reported for information only; it does not gate the warn.

Message formats:

- no port: `no port`
- port fit blocked (nothing placed): `no port placed (see port fit)`
- pass: `port mouth(s) clear: chamber 0 port 0: mouth 84 mm from the speaker 0 magnet (29 percent of the mouth), one diameter is 77.3 mm` (entries joined by `; `; a terminal face carries no coverage, e.g. `mouth 169 mm from the back panel, one diameter is 123.6 mm`)
- warn: `chamber 0 port 0: mouth 84 mm from the speaker 0 magnet (18 percent of the mouth), under one diameter (101.5 mm)` (a warn message has no prefix; each short entry says `under one diameter`)

Obstruction names: a part's blank name with spaces (`stiffener bottom`, `cleat back bottom`, `cleat back bottom 0` in a stereo chamber), `speaker N magnet` or `speaker N basket`, `baffle`, `back panel`.

## Aesthetics block

`cab.json["aesthetics"]` is `asdict(Aesthetics)`, 21 keys, tuples as lists: corner_joint, finger_width_mm, dovetail_slope, dovetail_pin_mm, dovetail_tail_mm, baffle_mount, handle, handle_screw_spacing_mm, recessed_handle_cutout_mm, jack_plate_cutout_mm, corners, corner_allowance_mm, piping, feet, foot_diameter_mm, foot_inset_mm, tolex_roll_in, head_width_mm, tolex_color, grill_cloth, finish. The design's ten keys are among them.

## Check order (19)

sheet, net volume, stereo balance, cutout, grill opening, port fit, port mouth, magnet to back, handle, head match, line, jack plate, stock, part count, spans, then interference, air volume, solid count, rectangularity. `cab.py` plain prints the first 15.

## Test counts

| Suite | Before | After |
|---|---|---|
| test_cablayout.py | 42 | 47 |
| test_cabmodel.py | 23 | 24 |
| test_cabvoice.py, test_cutlist.py | 397, 3 | untouched |

## Matrix results

- Layout matrix (1200 cases, 0.5 s): 150 engine power stops, 1026 clean, 24 blocked (port fit 24, net volume 22), worst clean net delta -1.10 percent (eminence-tonker, closed-ported 1x12 mono, hardwood). `port mouth` warns on 194 of the 1050 laid-out cases (325 port entries). By obstruction: every round-port warn names the magnet (129 entries: 54 to 76 mm free at 44 to 45 percent coverage with the 77.3 tube, 69 mm with the 101.5); slot warns name the floor-level back cleat (190 entries: 85 to 118 mm free against effective diameters of 123.6 mm and up, 46 percent coverage) or the bottom stiffener (6 entries: 0 to 12 mm, 5 to 8 percent coverage).
- CAD matrix, default 12 builds: 23 s; the whole `test_cabmodel.py` suite 70 s (was 63; the site default's cab.py now runs twice, once for the 1 mm test and once for the parametrized deliverables test).

## Commands run (from `.vault/scripts`, PY = the vault's `.venv/bin/python`)

```
PY -m pytest test_cablayout.py -q -s      -> 47 passed in 0.67s (matrix line above)
PY -m pytest test_cabmodel.py -q -s       -> 24 passed in 69.85s; cad matrix 12 builds in 23 s
cd ../projects/Speaker-cab-system/fixtures/site-default && EXPORT=1 PY cab.py   -> exit 0, 19 check lines (port mouth warn, spans warn)
CAB_FULL_MATRIX=1 PY -m pytest test_cabmodel.py -q -s -k cad_matrix   -> see the line at the end of this file
../../run_tests.sh                                                     -> see the line at the end of this file
```

## Deviations from the design, with reasons

1. **The site default warns on port mouth.** Design section 9 expected the site default to pass with its distance stated. Under the approved rule (any overlap, one diameter) its 101.5 mm tube, placed at x 107 beside the driver, has its mouth 84.4 mm behind the magnet's rear face while 18 percent of the mouth faces the magnet, so it warns. The fixture now carries two warns (spans, port mouth) and the fixture tests assert the warn. Not a defect in the rule; the site box is shallow.
2. **Coverage percent in the message.** Added so a partial obstruction reads as what it is (18 percent of the mouth versus 46). It is information only; the warn still triggers on any overlap under one diameter. Dropping it is a one-line change in `check_layout` and `port_mouth_clearances`.
3. **The 1x12 front slot warns on the bottom stiffener at 0 mm.** Plan 2 starts the bottom stiffener at the shelf's rear edge (`stiffener_blanks`: `yab = max(ya_default, fr.y_bf + fr.shelf_depth)`), flat on the floor, so its end face sits in the slot mouth's plane covering about 8 percent of the mouth. Every 1x12 slot whose bottom span exceeds 450 mm (the site box included) warns this way; only 6 matrix cases do because most proposed 1x12 boxes are narrower. Not changed here (a Plan 2 geometry rule, outside this fork's scope). Options for the plan writer: accept it with a sentence in the construction note; start the bottom stiffener one effective diameter behind the shelf (it then often drops under the 50 mm minimum length and the bottom panel goes unstiffened behind a slot); or gate the warn on a coverage threshold (a new rule Brian did not choose).
4. **Slots in shallow boxes warn on the back cleat.** The floor-level back cleat faces 46 percent of a 40 mm slot mouth; when the free depth behind the shelf is under the slot's effective diameter (about 124 mm for 300 x 40) the check warns. That is the rule working as approved; it is frequent (190 matrix entries) because tone-driven proposals are shallow.
5. **Parts that straddle the mouth plane count at 0 mm.** A part whose y range contains the mouth plane and whose projection overlaps the mouth would report 0 mm; port placement already keeps 25 mm radial clearance, so today only the stiffener case above reaches this.

## Open questions for the plan writer

- Both dry-run fixtures will very likely carry a port mouth warn: a site-box order with a rear tube (as the site default does) and a front slot in a box wide enough for a bottom stiffener (the rex-roots case). The answer sheet and the brief's Decisions locked block should expect a `port mouth` warn to judge, or the plan should pick one of the three options in deviation 3.
- Whether the coverage figure should stay informational (recommended) or gate the warn.
- `test_site_default_fixture` and the parametrized deliverables test both spawn the site default's `cab.py` (about 20 s each). Merging them would save 20 s per CAD run but moves the 1 mm assertion; left as the directive asked.

## Final runs

- `CAB_FULL_MATRIX=1 PY -m pytest test_cabmodel.py -q -s -k cad_matrix`: 60 builds in 97 s, 1 passed; layout blockers only `port fit` (12 cases) and `net volume` (10 cases), all closed-ported round Cannabis Rex cases as in Plan 2.
- `./run_tests.sh`: 505 passed in 69 s. That count includes Fork A's engine work, which landed in the mirror concurrently (`test_cabvoice.py` is at 431 from 397); this fork's own suites are 47 (`test_cablayout.py`) and 24 (`test_cabmodel.py`), re-run green against Fork A's engine. No `test_cabreport.py` exists yet.

## Addendum: the port fit blocker names the largest table tube that fits (coordinator's extension)

Symbols, `scripts/cablayout.py` (Task 6 unit):
- New, directly above `round_ports`: `largest_tube_at_minimum(env, sign, fr, obstacles, envelopes, tubes, below_id_mm) -> float | None`: the largest `cabvoice.PORT_TUBE_ID_MM` entry under the failed diameter that `_place_tube` seats at `cabvoice.MIN_PORT_LENGTH_MM` (24 mm) with the same obstacles, envelopes, and already-placed tubes. A tube that does not fit at the minimum cannot fit at any length, so the hint is a necessary condition only; the skill pins the named tube once and reads the next run's verdicts.
- Modified `round_ports`: the same-diameter length probe now steps 5 mm down from the sheet's length and always ends with the 24 mm minimum (before, it stopped above 24 unless a step landed on it); when no length fits, the blocker carries the table hint.
- Modified `slot_ports`: the shelf-depth blocker names the deepest shelf that fits, `floor(y_bi - y_bf - max(25, slot height))`, or says no shelf fits when that is under 24 mm.

Exact `port fit` messages (check level blocker; `cab.py` prints them after `port fit` and `blocker`; the layout note carries a `blocker: ` prefix in front of the same text):
- table tube named: `port fit: chamber 0 port 0: no round port of 153.2 mm fits with 25 mm clearance; the longest table tube that fits at the 24 mm minimum is 101.5 mm; raise Fb, use a smaller tube or a larger box, or a front slot`
- none fits: `port fit: chamber 0 port 0: no round port of 101.5 mm fits with 25 mm clearance; no table tube fits; use a front slot or a larger box`
- same diameter at a shorter length (unchanged text): `port fit: chamber 0 port 0: tube 77.3 x 250 mm reaches the baffle; longest tube that fits at this diameter is 155 mm; raise Fb, use a smaller tube or a larger box, or a front slot` (or `... finds no spot with 25 mm clearance; longest tube ...`)
- shelf too deep: `port fit: slot shelf 220 mm deep leaves 27 mm behind it, under the 40 mm the slot needs to breathe; the deepest shelf that fits is 207 mm; lower the slot height or use a round port`
- no shelf fits: `port fit: slot shelf 60 mm deep leaves -2 mm behind it, under the 40 mm the slot needs to breathe; no shelf fits; lower the slot height or use a round port`
- slot width blocker (unchanged): `port fit: chamber 0: 2 slots of 340 mm do not fit the 472 mm chamber with the 18 mm center cheek; narrow the slot or widen the box`
- multi-port chambers join entries with `; ` and each entry names its `chamber c port j`.

New tests (end of `test_cablayout.py`, under the Plan 3 comment): `test_port_fit_blocker_names_the_largest_table_tube_at_the_minimum` (the Cannabis Rex roots sheet proposed through the mirror engine with the module's `TONE`: default 153.2 mm blocks and names 101.5; the pinned 101.5 re-run at 24 mm passes port fit at x 82 z 214 and warns on port mouth), `test_port_fit_blocker_says_no_table_tube_fits` (360 x 457.2 x 192 mm box, 101.5 tube: nothing seats), `test_slot_shelf_blocker_names_the_deepest_shelf` (site box with a 220 mm shelf names 207 mm; a 90 mm deep box says no shelf fits through `slot_ports` directly).

Counts: `test_cablayout.py` 50 passed (42 landed, 5 from the first pass, 3 here); `test_cabmodel.py` 24 (unchanged; the CAD matrix asserts blocker names, not texts); `./run_tests.sh` 508 passed in 67 s (431 engine with Fork A's work, 3 cutlist, 50 layout, 24 CAD). Layout matrix unchanged (24 port-fit blockers, 22 net volume, 194 port mouth warns); every one of the 24 blockers is a Cannabis Rex or Swamp Thang round proposal and every one now names the 101.5 mm tube (42 port entries; 2x12 cases carry two).
