# Fork C report: report module and proposal template (Plan 3 Task 5) in the mirror

Files created (mirror only, nothing committed, landed `scripts/` and `skills/` untouched):

| File | Lines |
|---|---|
| `.vault/scripts/cabreport.py` | 343 |
| `.vault/scripts/test_cabreport.py` | 268 |
| `.vault/skills/speaker-cab/templates/proposal.md` | 65 |

Zero em dashes in all three. The module imports only the standard library and `cabvoice` (`PORT_V_MAX`, and the sheet's `prediction_status` is read from `cab.json`). Embed the two Python files with `all`; every piece is a top-level constant, dataclass, or def.

## Symbols, file order

`cabreport.py`: `SCRIPTS`, `VAULT`, `DEFAULT_TEMPLATE`, `KG_TO_LB`, `STOCK_SHEET_MM`, `STOCK_HARDWOOD_MM`, `NOT_CUT_STOCK`, `LEAD_TIME`, `SWATCHES`, `NO_SWATCH`, `OPERATOR_ROWS`, `ENGINE_ROWS`, `OPERATOR`, `POWER_VERDICT`, `BACK_TYPE`, `CONFIGURATION`, `SLOTS`, `FACT_KEYS`, `SLOT_RE`, `TOKEN_RE`, `class Row(name, value, verdict)`, `load_order(order_dir) -> (voicing, cab)`, `_fmt_in`, `_external(cab) -> (inches, mm)`, `_mass(cab) -> (kg, lb)`, `_thickness(parts, names)`, `_stock_yield(cab)`, `check_rows(voicing, cab) -> list[Row]`, `write_checks(rows, path, name) -> pending`, `swatch(name) -> str`, `_speaker_label(voicing)`, `_hardware(cab)`, `facts(voicing, cab, customer) -> dict`, `render_proposal(template_text, facts) -> str`, `verify_proposal(text, facts) -> list[str]`, `main(argv) -> int`.

`test_cabreport.py` (10 tests, `FIXTURE_ORDERS = ["site-default"]` at module level, resolved from `<vault>/projects/Speaker-cab-system/fixtures/<name>` where `<vault>` is the parent of the test's directory, so the same file works in the vault and in the mirror): `test_check_rows_follow_the_files_in_order[name]`, `test_site_default_rows_are_the_expected_verdicts`, `test_site_default_facts`, `test_hardwood_two_driver_open_back_labels`, `test_main_writes_checks_and_proposal_then_verifies[name]`, `test_proposal_is_written_once_and_verify_writes_nothing`, `test_verify_fails_on_an_edited_fact_and_an_emptied_slot`, `test_no_swatch_on_file_warns_and_still_writes`, `test_input_errors_exit_1_and_write_nothing`, `test_template_tokens_all_have_facts`. The dry-run tasks add `"sample-roots-1x12"` and `"rex-roots-1x12"` to `FIXTURE_ORDERS` and nothing else; the two parametrized tests then run on every fixture.

## checks.md for the site default (34 rows)

Frontmatter `type: checks`, `order: site-default`, `generated: <date>`; heading `# Check table - site-default`; columns `Check | Value | Verdict`; then the line `7 row(s) still read `operator`: replace each with a verdict line judged against the brief; the file is final when none remains.`

| Check | Verdict |
|---|---|
| sheet, net volume, stereo balance, cutout, grill opening, port fit | pass |
| port mouth | warn (Fork B's message verbatim) |
| magnet to back, handle, head match, line, jack plate, stock, part count | pass |
| spans | warn |
| interference, air volume, solid count, rectangularity | pass |
| power | warn (`handling 30 W is under the 45 W target (1.5 x amp power)`) |
| wiring | pass (`single, 16 ohm: Single driver, 16 ohm`) |
| port air speed | pass (`2.0 m/s against the 17 m/s limit`) |
| alignment | info (`punchy; Fb 67 Hz, F3 69 Hz`) |
| engine warning x 3 | warn (the sheet's three warnings verbatim) |
| stock thickness | operator (`tolex line: shell 18 mm, baffle 18 mm, back 12 mm`) |
| grain and show face | pass (`n/a, tolex line`) |
| joinery fit | operator (`finger corners, floating baffle`) |
| stock yield | operator (`22 blanks, 1.12 m2 of blanks, 0.4 sheets of 2440 x 1220 mm at 100 percent without nesting`) |
| wood movement | operator (`n/a; the climate comes from the brief`) |
| transport | operator (`20 x 18 x 11 in W x H x D, 37.5 lb; the vehicle and doorway come from the brief`) |
| weight vs limit | operator (`17.0 kg (37.5 lb); the limit comes from the brief`) |
| size vs limit | operator (`508 x 457 x 279 mm (20 x 18 x 11 in) W x H x D; the limits come from the brief`) |

Row rules: `power` maps the engine's `ok`, `warning`, `stop` to pass, warn, blocker; `wiring` is warn when the recommended option does not match a tap or the sheet has none; `port air speed` is `n/a`, pass for a box without a port; `alignment` shows the character with Fb and F3 (ported), F3 (closed), the cancellation frequency (open, semi-open), or Fb alone (rule-of-thumb); on hardwood `grain and show face` reads `<species>: book-matched panels, show face out, grain front to back on every shell panel (see the plan)` with verdict operator, and `stock yield` counts glue-ups of 3050 x 600 mm. Yield excludes PVC or ABS tube blanks. A `|` inside a message is written as `/`.

## facts for the site default (`--customer "Site Default"`)

`customer` Site Default; `order` site-default; `generated` the run date (not verified); `line_label` Tolex 1x12; `configuration` 1x12; `back_type` closed-back, ported; `speaker_label` Celestion G12H Anniversary; `wiring` Single driver, 16 ohm; `external_in` 20 x 18 x 11 in; `external_mm` 508 x 457 x 279 mm; `mass_kg` 17.0; `mass_lb` 37.5; `finish` Fender Style Black; `grill_cloth` British Small Weave Cane; `hardware` Black corners, strap handle, recessed metal jack plate, no piping, rubber feet.; `swatch_finish` `![Fender Style Black](images/fender-black.jpg)`; `swatch_cloth` `![British Small Weave Cane](images/cane.jpg)`; `lead_time` 8 to 12 weeks from confirmed order; `status_line` Every figure in this proposal is a design target, not a measurement. Prediction status: unverified, ears only.

Other values: `configuration` is `2x12 mono`, `2x12 with parallel out`, or `2x12 stereo` from `enclosure.jack_config`; `speaker_label` is `2 x Brand Model` for two identical drivers or `A and B`; `finish` on hardwood is the species title-cased (`Black Walnut`) and its swatch comes from the wood table; `external_in` drops a trailing `.0` per axis (`18.3` stays). `--verify` checks the 17 keys of `FACT_KEYS` (not `order` or `generated`).

## CLI help (verbatim)

```
usage: cabreport.py [-h] [--customer NAME] [--proposal-template PATH]
                    [--verify]
                    order_dir

Check table and proposal facts for a speaker cab order.

positional arguments:
  order_dir             order directory holding voicing.json and cab.json

options:
  -h, --help            show this help message and exit
  --customer NAME       customer name for the proposal (required to write or
                        verify it)
  --proposal-template PATH
                        proposal template (default skills/speaker-
                        cab/templates/proposal.md)
  --verify              verify the existing proposal.md instead of writing;
                        exit 2 on a failure
```

Run output: `<order>/checks.md: 34 rows, 7 still read operator` then `<order>/proposal.md: written` (or `left alone (delete it to regenerate)`); a verify run prints each problem (`missing fact external_in: 20 x 18 x 11 in`, `slot alternatives empty`, `slot designed_to_do missing`) and `<order>/proposal.md: verified` or `N problem(s)`; input errors print `input error: ...` (`--customer is required to write proposal.md`, `--customer is required to verify the proposal`, `<path> not found`, `<path> unreadable: ...`, `proposal template <path> not found`, `template tokens with no fact: ...`). The no-swatch warning on stderr: `warning: no swatch on file for the grill cloth` (or `finish`).

## Commands and results (from `.vault/scripts`, PY the vault venv python)

- `PY -m pytest test_cabreport.py -q`: 10 passed in 0.03 s.
- `../../run_tests.sh` (all suites, run_tests.sh picks the new file up): 519 passed in 73.79 s.
- `PY cabreport.py ../projects/Speaker-cab-system/fixtures/site-default --customer "Site Default"`: exit 0, the two files above; both read well and were deleted afterwards, so the site-default fixture carries only what Fork B regenerated (a golden `checks.md` and `proposal.md` belong to the dry-run fixtures, which are whole orders).

## Deviations from the design, with reasons

1. **A `--verify` run writes nothing.** The design says checks.md is written on every run; the skill edits checks.md by hand (replacing `operator` rows) and then runs `--verify` on the proposal, so a verify run that rewrote checks.md would clobber the judged verdicts. Non-verify runs still write checks.md every time (a re-run after a new build is meant to regenerate it), and the skill's Phase 5 text ("writes checks.md on every run") stays true for the run it describes. Fork E's SKILL.md Phase 6 step 3 runs `--verify` after Phase 5's judging, which is exactly the case this protects.
2. **`--customer` is also required with `--verify`** (the customer name is one of the verified facts and lives in neither JSON file); SKILL.md already passes it on the verify command.
3. **The template puts the configuration on its own line** (`- Cabinet: Tolex 1x12, closed-back, ported` then `- Configuration: 1x12`) because `line_label` already carries the count and the design's single Cabinet line rendered "Tolex 1x12, 1x12, closed-back, ported".
4. **`alignment` shows Fb and F3 for a ported box** rather than F3 alone, since Fb is the number the port loop's decisions turn on; predicted frequencies still never enter the proposal (the facts are tested to carry none).
5. **Module length 343 lines** with its docstring, above the 300 the directive named; the eight operator rows and the fact formatting are what it takes.
6. **Yield excludes PVC or ABS tube blanks** (they are not sheet stock) and counts the flange ring; the design did not say either way.

## Open questions for the plan writer

- The proposal's `hardware` sentence takes the jack plate wording from the cab.json hardware item's first clause with "plate" replaced by "jack plate" (`recessed metal jack plate`, `recessed brass jack plate`); if Plan 2's note text for the plate changes, the sentence follows.
- `wood movement` keeps verdict `operator` on the tolex line (`n/a; the climate comes from the brief`), per the design's list; if Brian would rather see it pass on plywood the way grain does, it is a one-line change in `check_rows`.
- The dry-run fixtures will ship a judged `checks.md` (no `operator` left) and a filled `proposal.md`; the report tests only render into a temporary copy, so they never touch those files.
