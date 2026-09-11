"""Build task1.md, task2.md, task3.md from the mirror files by symbol extraction,
so every code block is byte-identical to the mirror (and to what lands)."""
import ast
import re
from pathlib import Path

M = Path(__file__).resolve().parent
ENGINE = M / ".vault/scripts/cabvoice.py"
TESTS = M / ".vault/scripts/test_cabvoice.py"
CUTLIST = M / ".vault/scripts/cutlist.py"
TEST_CUTLIST = M / ".vault/scripts/test_cutlist.py"
FIELDS = M / ".vault/projects/Speaker-cab-system/pipeline/catalog_fields.py"
CALIB = M / ".vault" / "plan" / "calibration_table.md"


def symbol(path: Path, name: str) -> str:
    """Source text of a top-level def or class, decorators included."""
    src = path.read_text()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name:
            start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
            return "".join(lines[start:node.end_lineno])
    raise KeyError(name)


def between(path: Path, start: str, end: str, include_end: bool = False) -> str:
    """Source text from the line starting with `start` up to (not including) the
    line starting with `end`."""
    text = path.read_text()
    i = text.index(start)
    j = text.index(end, i + len(start))
    if include_end:
        j = text.index("\n", j) + 1
    return text[i:j]


def block(code: str, lang: str = "python") -> str:
    return f"```{lang}\n{code.rstrip()}\n```\n"


def check(code: str, path: Path):
    assert code.rstrip() in path.read_text(), f"block not verbatim in {path.name}: {code[:60]!r}"


VAULT_RUN = "cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q"

# ---------------------------------------------------------------- Task 1
t1_tests = between(TESTS, "# ---- Plan 2 Task 1:", "# ---- Plan 2 Task 2:")
t1_engine = [
    ("REQUIRED_FIELDS", between(ENGINE, "REQUIRED_FIELDS = (", "# May be null only when")),
    ("POSITIVE_FIELDS", between(ENGINE, "POSITIVE_FIELDS = (", "\n\ndef parse_frontmatter")),
    ("validate_speaker", symbol(ENGINE, "validate_speaker")),
    ("Driver", symbol(ENGINE, "Driver")),
    ("driver_from_meta", symbol(ENGINE, "driver_from_meta")),
    ("_speaker_summary", symbol(ENGINE, "_speaker_summary")),
]
for _, code in t1_engine + [("tests", t1_tests)]:
    check(code, ENGINE if code is not t1_tests else TESTS)
fields_src = FIELDS.read_text()

task1 = f"""### Task 1: Catalog frame and magnet diameters

**Files:**
- Create: `projects/Speaker-cab-system/pipeline/catalog_fields.py`
- Modify: `knowledge/speakers/*.md` (all 20 notes, through the script)
- Modify: `scripts/cabvoice.py` (`REQUIRED_FIELDS`, `POSITIVE_FIELDS`, `validate_speaker`, `Driver`, `driver_from_meta`, `_speaker_summary`)
- Modify: `scripts/test_cabvoice.py` (`FIXTURE_NOTE`, new Task 1 tests)
- Mirror source (byte-identical, for transcription): `projects/Speaker-cab-system/pipeline/plan2-mirror/.vault/scripts/cabvoice.py`, `.vault/scripts/test_cabvoice.py`, `.vault/projects/Speaker-cab-system/pipeline/catalog_fields.py`

**Interfaces:**
- Consumes: the 20 catalog notes as landed by Plan 1 (every note has `depth_mm:` in its frontmatter and a `## Data notes` bullet list before `## Field notes`); the values in `knowledge/research/speaker-envelopes-and-port-stock.md` Part A.
- Produces: frontmatter keys `frame_diameter_mm` (float, required), `magnet_diameter_mm` (float or null, optional), `magnet_diameter_estimated` (bool, default false) on every note; `Driver.frame_diameter_mm: float`, `Driver.magnet_diameter_mm: float | None`, `Driver.magnet_diameter_estimated: bool`; the same three keys in every `voicing.json` `speakers[]` entry. Task 4 (`cablayout.order_from`) reads them from the sheet.

Every note gains the three keys directly after `depth_mm` and one flagged bullet at the end of its Data notes list. Estimated magnet diameters are the conservative top of the research band. The generator's speaker envelope (design section 4) uses `magnet_diameter_mm + 12` (185 mm when null) behind the baffle and `frame_diameter_mm` for the flange disc in front of it.

- [ ] **Step 1: Write the failing tests**

In `scripts/test_cabvoice.py`, add the three frontmatter lines to `FIXTURE_NOTE` directly after `weight_kg: 4.7`:

```yaml
frame_diameter_mm: 309
magnet_diameter_mm: 156
magnet_diameter_estimated: false
```

Append at the end of the file:

{block(t1_tests)}
- [ ] **Step 2: Run the tests to verify they fail**

Run: `{VAULT_RUN} -k "envelope or frame_diameter"`
Expected: FAIL (`frame_diameter_mm` missing from `Driver`, notes without the keys).

- [ ] **Step 3: Engine fields**

In `scripts/cabvoice.py` replace each of these symbols with the version below (full text; the rest of the file is unchanged).

{"".join(f"`{name}`:{chr(10)}{chr(10)}{block(code)}{chr(10)}" for name, code in t1_engine)}
- [ ] **Step 4: The catalog script**

Create `projects/Speaker-cab-system/pipeline/catalog_fields.py`:

{block(fields_src)}
- [ ] **Step 5: Apply it to the catalog**

Run from the vault root:

```bash
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py --apply
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py --apply
```

Expected: the first run lists 20 notes as `patched` and ends `20 note(s) would change`; the second writes them (`20 note(s) written`); the third ends `0 note(s) written` (idempotent). Check one published and one estimated note, for example `knowledge/speakers/celestion-vintage-30.md` (three new frontmatter lines after `depth_mm: 135`, the Data notes bullet "Frame diameter 309 mm and magnet diameter 156 mm from the maker's drawing", and the Voice Coil bullet since its sources cite `2019/10/141.pdf`) and `knowledge/speakers/eminence-tonker.md` (`magnet_diameter_estimated: true`, bullet "Magnet diameter 181 mm is estimated").

- [ ] **Step 6: Run the tests to verify they pass**

Run: `{VAULT_RUN}`
Expected: 356 passed (351 from Plan 1 plus 5).

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cabvoice.py scripts/test_cabvoice.py projects/Speaker-cab-system/pipeline/catalog_fields.py knowledge/speakers/*.md
git commit -m "Speaker cab plan 2 task 1: frame and magnet diameters in the catalog and the engine"
```
"""

# ---------------------------------------------------------------- Task 2
t2_tests_new = between(TESTS, "# ---- Plan 2 Task 2:", "\nZZZ_END") if "\nZZZ_END" in TESTS.read_text() else TESTS.read_text()[TESTS.read_text().index("# ---- Plan 2 Task 2:"):]
t2_tests_mod = [symbol(TESTS, n) for n in (
    "test_size_port_grows_when_too_short", "test_dims_for_volume_min_width_for_two_drivers",
    "test_propose_closed_ported_1x12", "test_propose_stereo_2x12_closed",
    "test_propose_stereo_volumes_reconcile", "test_propose_impossible_box_presents_tradeoff",
    "test_evaluate_site_default_closed", "test_evaluate_ported_reports_tuning_from_port",
    "_matrix_params", "test_evaluate_reproduces_propose",
    "test_propose_mono_2x12_uses_one_port_per_driver")]
t2_engine = [
    ("port constants (replace the two lines `MIN_PORT_LENGTH_MM = 20.0` and `MAX_PORT_DIAMETER_MM = 150.0`)",
     between(ENGINE, "MIN_PORT_LENGTH_MM = 20.0", "\n\n@dataclass\nclass Port")),
    ("`snap_tube_id` (new, directly above `size_port`)", symbol(ENGINE, "snap_tube_id")),
    ("`size_port`", symbol(ENGINE, "size_port")),
    ("box constants (replace the block from `MM_PER_INCH` to `BASE_EXTERNAL_IN`)",
     between(ENGINE, "MM_PER_INCH = 25.4", "\n\n@dataclass\nclass Box")),
    ("`min_internal_width_mm`", symbol(ENGINE, "min_internal_width_mm")),
    ("`min_internal_height_mm` (new)", symbol(ENGINE, "min_internal_height_mm")),
    ("`dims_for_volume`", symbol(ENGINE, "dims_for_volume")),
    ("`_port_inside_l` and `inside_parts_l` (new, directly above the tone target section)",
     symbol(ENGINE, "_port_inside_l") + "\n\n" + symbol(ENGINE, "inside_parts_l")),
    ("`Constraints`", symbol(ENGINE, "Constraints")),
    ("`_volumes`", symbol(ENGINE, "_volumes")),
    ("`propose`", symbol(ENGINE, "propose")),
    ("`evaluate`", symbol(ENGINE, "evaluate")),
    ("`render_markdown` (two rows in the Volumes table: replace the `| Port |` line and add the inside parts row after `| Divider |`)",
     between(ENGINE, '        f"| Port air inside the box |', '        f"| Gross internal |')),
    ("`_build_parser`", symbol(ENGINE, "_build_parser")),
]
for _, code in t2_engine:
    check(code, ENGINE)
for code in t2_tests_mod + [t2_tests_new]:
    check(code, TESTS)
calib = CALIB.read_text()

task2 = f"""### Task 2: Engine touches: tube table, shell margins, height floor

**Files:**
- Modify: `scripts/cabvoice.py` (port constants, `snap_tube_id`, `size_port`, box and inside-part constants, `min_internal_width_mm`, `min_internal_height_mm`, `dims_for_volume`, `_port_inside_l`, `inside_parts_l`, `Constraints`, `_volumes`, `propose`, `evaluate`, `render_markdown`, `_build_parser`)
- Modify: `scripts/test_cabvoice.py` (ten existing tests and the `_matrix_params` helper, new Task 2 tests)
- Modify: `knowledge/speaker-cab-voicing.md` (calibration table regenerated)
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan2-mirror/.vault/scripts/cabvoice.py`, `.vault/scripts/test_cabvoice.py`, `plan2-mirror/.vault/plan/calibration_table.md`

**Interfaces:**
- Consumes: Task 1's engine (frame and magnet fields present).
- Produces: `PORT_TUBE_ID_MM = (52.0, 77.3, 101.5, 153.2)`, `PORT_TUBE_OD_MM` dict, `MAX_PORT_DIAMETER_MM = 153.2`, `DEFAULT_PORT_DIAMETER_MM = 77.3`, `snap_tube_id(diameter_mm) -> float`, `SHELL_MARGIN_MM = 44.0`, `CUTOUT_GAP_MM = 68.0`, `CUTOUT_MARGIN_MM = 25.0` (kept), `HARDWOOD_FLOOR_EXTRA_MM = 2.0`, the inside-part constants (`CLEAT_MM`, `STIFFENER_MM`, `SPAN_MAX_MM`, `BRACE_MM`, `JACK_PLATE_H_MM`, `JACK_CLEAR_MM`, `FLANGE_RING_T_MM`, `FLANGE_RING_EXTRA_MM`, `TUBE_WALL_FALLBACK_MM`), `min_internal_width_mm(driver_count, cutout_mm)`, `min_internal_height_mm(cutout_mm, slot_h_mm=None)`, `dims_for_volume(..., max_external_mm=None, min_internal_height_mm=None, strict=True, ...)`, `inside_parts_l(internal_mm, enclosure, driver_count, chambers, jack_config, port, line, port_count=None, panel_mm=PANEL_MM) -> float`, and a `volumes.inside_parts_l` key in every sheet with the identity gross = net + displacement + brace + port + divider + inside_parts, where `volumes.port_l` is the port air inside the box (a tube's length through the back panel and a slot's through the baffle are outside it; `port.volume_l` stays the whole port). Every round port in a `voicing.json` has `port.diameter_mm` in the tube table; `cablayout` (Task 4) imports the constants and `PORT_TUBE_OD_MM` for the tube outside diameter, and its measured net must land within 1.5 percent of `volumes.net_total_l`.

Changes to Plan 1 starting values, all recorded in the construction and voicing notes by Task 13: `MAX_PORT_DIAMETER_MM` 150 to 153.2 (the 6 inch tube), the round port start 75 to 77.3 mm (the 3 inch tube), the shell margin 25 to 44 mm, the 2x12 cutout gap 25 to 68 mm (so the 2x12 width floor moves from 641 to 722 mm internal, and the stereo floor no longer adds the divider separately), a new height floor, and 2 mm on both floors for the hardwood line (its 19 mm panels take 1 mm per side from the 18 mm voicing box). A round port is snapped up to the next tube after the air-speed loop and re-solved, the sheet's prediction follows the tube (the fix-wave rule), and a warning names the snap. `dims_for_volume` re-applies the floors after every rescale (before this a width floor could shrink the height under its own floor on rescale), and both floors are checked against the size limit (a floor above the limit raises, as the pinned width already did). The volumes identity gains `inside_parts_l`, the cleats, stiffeners, mono 2x12 brace, slot shelf and cheeks, tube wall and flange ring that the generator builds inside the air box, estimated the way `scripts/cablayout.py` lays them out, and `port_l` becomes the port air inside the box; both change every sheet's net (the site box drops from 44.1 to 42.5 L closed) so the whole calibration table moves.

- [ ] **Step 1: Write the failing tests**

In `scripts/test_cabvoice.py` replace these tests (and the `_matrix_params` helper) with the versions below:

{"".join(block(c) + chr(10) for c in t2_tests_mod)}
Append at the end of the file:

{block(t2_tests_new)}
- [ ] **Step 2: Run the tests to verify they fail**

Run: `{VAULT_RUN} -k "snap or floor or height or purchasable or tube_start or min_internal or too_short or two_drivers or stereo_2x12 or one_port_per_driver"`
Expected: FAIL (`snap_tube_id` undefined, old constants).

- [ ] **Step 3: Engine changes**

In `scripts/cabvoice.py` replace each of these with the version below (full text).

{"".join(f"{name}:{chr(10)}{chr(10)}{block(code)}{chr(10)}" for name, code in t2_engine)}
- [ ] **Step 4: Run the tests (calibration test still fails)**

Run: `{VAULT_RUN}`
Expected: 396 passed, 1 failed (`test_calibration_table_matches_engine`, the note still holds the Plan 1 table).

- [ ] **Step 5: Regenerate the calibration table**

Run from the vault root: `.venv/bin/python projects/Speaker-cab-system/pipeline/calibration_table.py`
Expected: `wrote 20 rows to .../knowledge/speaker-cab-voicing.md`. Every row changes against Plan 1: the site box net drops from 44.1 (43.6, 43.4 on the Eminence rows) to 42.5 (42.0, 41.8) L with the inside parts deducted, every closed Qtc rises by about 0.006 to 0.01 and three closed F3 values by 1 Hz, the Heritage G12H(55) closed character moves from lean to tight (Qtc 0.599 to 0.605 across the 0.6 threshold), and the Eminence Red White and Blues notes read "port too short (6.5 mm)" and "tuned 74.4 Hz" (its clamped port now stops at the 153.2 mm tube). Proposed ported net and Fb columns are unchanged. The section must read (the date is the run date):

{block(calib, "markdown")}
- [ ] **Step 6: Run the tests to verify they pass**

Run: `{VAULT_RUN}`
Expected: 397 passed.

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cabvoice.py scripts/test_cabvoice.py knowledge/speaker-cab-voicing.md
git commit -m "Speaker cab plan 2 task 2: port tube table, shell margins, height floor"
```
"""

# ---------------------------------------------------------------- Task 3
wcl = symbol(CUTLIST, "write_cut_list")
check(wcl, CUTLIST)
task3 = f"""### Task 3: Cut list emitter: materials not cut

**Files:**
- Modify: `scripts/cutlist.py` (`write_cut_list`)
- Create: `scripts/test_cutlist.py`
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan2-mirror/.vault/scripts/cutlist.py`, `.vault/scripts/test_cutlist.py`

**Interfaces:**
- Consumes: the Plan 1 emitter (`write_cut_list(parts, md_path, csv_path=None, title="Cut list")`, `cut_list_rows`, `_measure` which already prefers a part's `dims` over its `solid`).
- Produces: `write_cut_list(parts, md_path, csv_path=None, title="Cut list", extra_lines=None)`; `extra_lines` is a list of `{{"part": str, "qty": float, "unit": str, "material": str, "notes": str}}`; each entry becomes a bullet under a `## Materials not cut` section after the totals and one CSV row `[qty, part, "", "", "", material, notes]`. Task 11 (`cabmodel.export`) passes the tolex yardage line this way. Nothing else in the emitter changes, so the furniture models keep their output.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_cutlist.py`:

{block(TEST_CUTLIST.read_text())}
- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cutlist.py -q`
Expected: 2 failed (`extra_lines` is not an argument), 1 passed.

- [ ] **Step 3: Implement**

In `scripts/cutlist.py` replace `write_cut_list` with:

{block(wcl)}
- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cutlist.py -q`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cutlist.py scripts/test_cutlist.py
git commit -m "Speaker cab plan 2 task 3: cut list materials-not-cut lines"
```
"""

for name, text in (("task1.md", task1), ("task2.md", task2), ("task3.md", task3)):
    assert "—" not in text, name
    (M / ".vault" / "plan" / name).write_text(text)
    print(name, len(text), "bytes")
