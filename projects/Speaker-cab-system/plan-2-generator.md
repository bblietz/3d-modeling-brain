---
name: plan-2-generator
description: Plan 2 implementation plan for the parametric cabinet generator (scripts/cablayout.py, scripts/cabmodel.py) with the engine, cut list, and catalog touches it needs; complete code per task, embedded from the tested mirror
type: plan
status: ready
created: 2026-09-10
tags: [project, speaker-cab, plan, generator, cad]
---

# Speaker Cab Plan 2: Parametric Cabinet Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** From an approved `voicing.json` and an aesthetics block, produce the builder package for one cabinet (STEP assembly, renders, cut list with tolex yardage, and `cab.json` with every check verdict) for 1x12 and 2x12 cabinets in the tolex and hardwood lines, closed, closed-ported (round rear or front slot), open, and semi-open.

**Architecture:** A numeric layout kernel (`scripts/cablayout.py`) turns the sheet plus aesthetics into every blank, position, joinery schedule, hardware position, envelope, chamber, and derived number, and runs the analytic checks. A CAD layer (`scripts/cabmodel.py`, build123d) places one named solid per blank from that layout, proves the solids agree with it (measured air volume, boolean interference, part count), and exports STEP, renders, cut list, and `cab.json`. A thin per-order `cab.py` wires the two behind the furniture env gates. Three small touches to shared code make the sheet buildable as written: the engine snaps port diameters to purchasable tubes and gains width and height floors plus frame and magnet diameters in the speakers block; the cut list emitter gains a "materials not cut" line; the twenty catalog notes gain the two diameters.

**Tech Stack:** Python 3.12 at `.venv/bin/python` (build123d, trimesh, matplotlib, PyYAML already installed), pytest, `scripts/render_stl.py`, `scripts/cutlist.py`, `scripts/cabvoice.py`.

**Spec:** [[2026-09-10-plan-2-generator-design]] (sections 3 to 10), which amends Unit 2 of [[2026-09-08-speaker-cab-system-design]]; open items from [[speaker-cab-plan-1]]; research in [[guitar-cab-joinery-survey]] and [[speaker-envelopes-and-port-stock]].

## Global Constraints

- Millimetres everywhere. Sheet tuples are (width, height, depth) as in voicing.json. The cab frame is X width centered at 0, Y depth with the external front face at 0 and positive toward the back, Z height with the floor at 0; blank positions are (x, y, z) min corners in that frame.
- Locked engine values that the layout mirrors: `BAFFLE_MM 18.0`, `BACK_MM 12.0`, `RECESS_MM 20.0`, `CUTOUT_MARGIN_MM 25.0`, `MM_PER_INCH 25.4` (each asserted against `cabvoice` at import) and `PREDICTION_STATUS "unverified, ears only"` (not asserted at import: the `sheet` check mirrors it and warns when the sheet's value differs from the engine's).
- New engine values (Task 2): `PORT_TUBE_ID_MM (52.0, 77.3, 101.5, 153.2)`, `PORT_TUBE_OD_MM {52.0: 60.3, 77.3: 88.9, 101.5: 114.3, 153.2: 168.3}`, `MAX_PORT_DIAMETER_MM 153.2` (was 150.0), `DEFAULT_PORT_DIAMETER_MM 77.3` (was 75.0), `SHELL_MARGIN_MM 44.0`, `CUTOUT_GAP_MM 68.0`, `HARDWOOD_FLOOR_EXTRA_MM 2.0`; `min_internal_width_mm(n, cutout) = n * cutout + (n - 1) * 68 + 2 * 44`; `min_internal_height_mm(cutout, slot_h) = cutout + 88 (+ slot_h + 18 with a slot)`; both floors plus 2 on hardwood and re-applied after every rescale; `volumes.inside_parts_l` (cleats, stiffeners, shelf, cheeks, brace, tube wall, flange ring) added to gross like `brace_l`; `volumes.port_l` is the port air inside the gross box.
- Layout constants (Task 4, names exact): `PANEL_MM {"tolex": 18.0, "hardwood": 19.0}`, `CLEAT_MM 18.0`, `GRILL_STRIP_T_MM 12.0`, `GRILL_STRIP_W_MM 40.0`, `GRILL_CLEARANCE_MM 2.0`, `FLANGE_T_MM 5.0`, `SPACER_MM 5.0`, `BRACE_MM (18.0, 60.0)`, `DIVIDER_MM 18.0`, `STIFFENER_MM (18.0, 40.0)`, `SPAN_MAX_MM 450.0`, `BOLT_HOLE_MM 6.5`, `DADO_MM 6.0`, `BASKET_LEN_MM 100.0`, `COVER_MM 12.0`, `GENERIC_MAGNET_MM 185.0`, `CLEARANCE_MM 25.0`, `JACK_CLEAR_MM 25.0`, `HARDWARE_KG 1.0`, `TOLEX_WASTE 1.15`, `ROLL_MM {54: 1371.6, 32: 812.8}`, `STOCK_SHEET_MM (2440.0, 1220.0)`, `STOCK_HARDWOOD_MM (3050.0, 600.0)`, `FLANGE_RING_T_MM 12.0`, `FLANGE_RING_EXTRA_MM 60.0`, `BIRCH_DENSITY 680.0`, `SPECIES_DENSITY {"black walnut": 610.0, "black cherry": 560.0, "hard maple": 705.0, "sapele": 670.0}`.
- Joinery: fingers half the shell thickness, odd count, both ends full, front finger on top and bottom, sides start with a gap; dovetails hardwood only, tails on the sides, pins on top and bottom, half-pins both ends, slope 1:8, pin half the thickness, tails about 30 mm. Cut list rows for comb panels are rectangular blanks (`dims`) with the schedule in the note.
- Margins: 44 mm cutout edge to shell, 25 mm to brace or divider, 68 mm between the two cutouts of a 2x12; 25 mm from any envelope part to port, back, cleats, shelf, stiffeners, brace, divider.
- Checks are verdict lines (name, level pass | warn | blocker, message); `cab.py` exits 0 on pass or warn, 1 on an input error with nothing written, 2 on any blocker with files still written.
- Grill frame 12 x 40 strips resting on 5 mm flanges and 5 mm corner spacers in the 20 mm recess; a strip may cover a flange but clears every cutout by 2 mm.
- build123d rules from the furniture skill: algebra mode, one named solid per part, `align=(Align.CENTER, Align.CENTER, Align.MIN)` idiom where a box is placed by its base, cutting tools extended 1 mm past coincident faces, keep the largest solid after a probe boolean. Two identical build123d failures on one feature escalate to FreeCAD via the MCP tools.
- Every CAD task renders its feature with `scripts/render_stl.py` to a temporary PNG and the implementer views it with the Read tool before claiming the step done; the reviewer views the same render.
- Vault conventions: notes have YAML frontmatter, wikilinks, no em dashes, English only, mm.
- Tests live at `scripts/test_cablayout.py`, `scripts/test_cabmodel.py`, `scripts/test_cutlist.py`, `scripts/test_cabvoice.py`. Full run from the vault root: `.venv/bin/python -m pytest scripts/test_cabvoice.py scripts/test_cutlist.py scripts/test_cablayout.py scripts/test_cabmodel.py -q`.
- The mirror `projects/Speaker-cab-system/pipeline/plan2-mirror/` is the tested oracle every code block was embedded from (`projects/Speaker-cab-system/pipeline/embed_plan_code.py --check` proves the plan matches it). Transcribe from the plan; when a block fails, diff against the mirror before changing anything, and report every deviation to the reviewer.
- Commit after every task with explicit paths and the attribution trailers from the session; never stage files outside the task's list (another session shares this tree and has its own uncommitted files, currently `projects/Build123d-trial/project-box.3mf`). Ledger: append one line per event to `.superpowers/sdd/progress.md`.
- Model dispatch: implementers Sonnet 5 except Task 2 (engine cross-mode logic) on Fable 5.1; every review Fable 5.1; controller Fable 5.1.

## File Structure

| File | Responsibility |
|---|---|
| `knowledge/speakers/<slug>.md` (20 notes) | Task 1: `frame_diameter_mm`, `magnet_diameter_mm`, `magnet_diameter_estimated` in the frontmatter plus a flagged Data notes sentence |
| `projects/Speaker-cab-system/pipeline/catalog_fields.py` | Task 1: idempotent script that applies those fields |
| `scripts/cabvoice.py` | Task 1: `Driver` fields, validator, speakers block. Task 2: tube table and snap, margins and floors, `dims_for_volume` height floor, defaults |
| `scripts/test_cabvoice.py` | Tasks 1 and 2: updated and new tests |
| `knowledge/speaker-cab-voicing.md` | Task 2: calibration table regenerated |
| `scripts/cutlist.py` | Task 3: `extra_lines` argument |
| `scripts/test_cutlist.py` | Task 3: emitter tests |
| `scripts/cablayout.py` | Tasks 4 to 7: constants, dataclasses, sheet loading, joinery schedules, shell; baffle, cutouts, cleats, grill, brace, divider, stiffeners; backs, ports, hardware, envelopes; chambers, volumes, mass, tolex, checks, report, `layout()` |
| `scripts/test_cablayout.py` | Tasks 4 to 7: unit tests and the 1200-case layout matrix |
| `scripts/cabmodel.py` | Tasks 8 to 11: shell solids with combs; baffle, brace, divider, cleats, grill; backs, ports, envelopes, plates; assembly, air volume, interference, exploded view, exports, `cab.json` |
| `scripts/test_cabmodel.py` | Tasks 8 to 11: per-feature tests, the CAD matrix (12 default, 60 with `CAB_FULL_MATRIX=1`), the fixture test |
| `projects/Speaker-cab-system/fixtures/site-default/` | Task 12: `voicing.json`, `voicing.md`, `cab.py` (the template every order copies), committed outputs minus STEP and STL |
| `knowledge/speaker-cab-construction.md` | Task 13: revised note |
| `projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md` | Task 13: pointer line at Unit 2 |
| `knowledge/learnings/speaker-cab-plan-1.md`, `knowledge/learnings/speaker-cab-plan-2.md` | Task 13: open item superseded; new retrospective |
| `memory/project-speaker-cab-system.md`, `memory/MEMORY.md` | Task 13: project memory |

---

<!-- include: .vault/plan/task1.md -->
### Task 1: Catalog frame and magnet diameters

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

```python
# ---- Plan 2 Task 1: frame and magnet diameters --------------------------

def test_validate_speaker_accepts_envelope_fields():
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    assert cabvoice.validate_speaker(meta) == []
    meta["magnet_diameter_mm"] = None            # optional: the generator falls back to 185 mm
    assert cabvoice.validate_speaker(meta) == []


def test_validate_speaker_requires_frame_diameter_and_bool_flag():
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    del meta["frame_diameter_mm"]
    assert any("frame_diameter_mm" in e for e in cabvoice.validate_speaker(meta))
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    meta["magnet_diameter_estimated"] = "yes"
    assert any("magnet_diameter_estimated" in e for e in cabvoice.validate_speaker(meta))
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    meta["magnet_diameter_mm"] = -5
    assert any("magnet_diameter_mm" in e for e in cabvoice.validate_speaker(meta))


def test_driver_carries_envelope_fields(drv):
    assert drv.frame_diameter_mm == 309
    assert drv.magnet_diameter_mm == 156
    assert drv.magnet_diameter_estimated is False
    assert _driver(magnet_diameter_mm=None).magnet_diameter_mm is None
    assert _driver(magnet_diameter_estimated=True).magnet_diameter_estimated is True


def test_voicing_speakers_block_carries_envelope_fields(drv, tone, tmp_path):
    v = cabvoice.propose([drv], [16], "closed", tone)
    cabvoice.write_voicing(v, tmp_path)
    s = json.loads((tmp_path / "voicing.json").read_text())["speakers"][0]
    assert s["frame_diameter_mm"] == 309
    assert s["magnet_diameter_mm"] == 156
    assert s["magnet_diameter_estimated"] is False


def test_catalog_notes_carry_envelope_fields():
    for slug in cabvoice.list_speakers(CATALOG):
        d = cabvoice.load_speaker(slug, CATALOG)
        assert 300.0 < d.frame_diameter_mm < 320.0, slug
        assert d.magnet_diameter_mm is not None and 120.0 <= d.magnet_diameter_mm <= 190.0, slug
        text = (CATALOG / f"{slug}.md").read_text()
        data_notes = text.split("## Data notes", 1)[1].split("\n## ", 1)[0]
        assert "[[speaker-envelopes-and-port-stock]]" in data_notes, slug
        assert ("is estimated" in data_notes) == d.magnet_diameter_estimated, slug
        if "2019/10/141.pdf" in text.split("\n---\n", 1)[0]:
            assert "Voice Coil magazine" in data_notes, slug
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q -k "envelope or frame_diameter"`
Expected: FAIL (`frame_diameter_mm` missing from `Driver`, notes without the keys).

- [ ] **Step 3: Engine fields**

In `scripts/cabvoice.py` replace each of these symbols with the version below (full text; the rest of the file is unchanged).

`REQUIRED_FIELDS`:

```python
REQUIRED_FIELDS = (
    "name", "type", "brand", "model", "diameter_in", "impedance_ohm",
    "power_w", "sensitivity_db", "magnet", "fs_hz", "re_ohm",
    "cutout_mm", "bolt_circle_mm", "bolt_count", "depth_mm", "weight_kg",
    "frame_diameter_mm", "data_status", "sources", "status",
)
```

`POSITIVE_FIELDS`:

```python
POSITIVE_FIELDS = (
    "diameter_in", "power_w", "sensitivity_db", "fs_hz", "re_ohm",
    "cutout_mm", "bolt_circle_mm", "bolt_count", "depth_mm", "weight_kg", "le_mh",
    "displacement_l", "frame_diameter_mm", "magnet_diameter_mm",
) + TS_FIELDS
```

`validate_speaker`:

```python
def validate_speaker(meta: dict) -> list[str]:
    """Return a list of problems with a speaker note's frontmatter (empty = ok)."""
    errors = []
    for key in REQUIRED_FIELDS:
        if key not in meta or meta[key] is None:
            errors.append(f"missing required field {key}")
    if meta.get("type") != "speaker":
        errors.append("type must be 'speaker'")
    status = meta.get("data_status")
    if status not in DATA_STATUS_VALUES:
        errors.append(f"data_status must be one of {DATA_STATUS_VALUES}, got {status!r}")
    if meta.get("magnet") not in MAGNET_VALUES:
        errors.append(f"magnet must be one of {MAGNET_VALUES}")
    imps = meta.get("impedance_ohm")
    if not isinstance(imps, list) or not imps or not all(isinstance(z, (int, float)) and z > 0 for z in imps):
        errors.append("impedance_ohm must be a non-empty list of positive numbers")
    if not isinstance(meta.get("sources"), list) or not meta.get("sources"):
        errors.append("sources must be a non-empty list of URLs")
    for key in TS_FIELDS:
        if meta.get(key) is None and status != "missing":
            errors.append(f"{key} is required unless data_status is 'missing'")
    for key in POSITIVE_FIELDS:
        val = meta.get(key)
        if val is not None and (not isinstance(val, (int, float)) or val <= 0):
            errors.append(f"{key} must be a positive number, got {val!r}")
    if status == "analog" and not meta.get("analog_of"):
        errors.append("analog_of is required when data_status is 'analog'")
    est = meta.get("magnet_diameter_estimated")
    if est is not None and not isinstance(est, bool):
        errors.append(f"magnet_diameter_estimated must be true or false, got {est!r}")
    return errors
```

`Driver`:

```python
@dataclass
class Driver:
    slug: str
    brand: str
    model: str
    diameter_in: float
    impedance_ohm: list
    power_w: float
    sensitivity_db: float
    magnet: str
    fs_hz: float
    re_ohm: float
    qts: float | None
    qes: float | None
    qms: float | None
    vas_l: float | None
    xmax_mm: float | None
    sd_cm2: float | None
    le_mh: float | None
    cutout_mm: float
    bolt_circle_mm: float
    bolt_count: int
    depth_mm: float
    weight_kg: float
    displacement_l: float
    displacement_estimated: bool
    frame_diameter_mm: float
    magnet_diameter_mm: float | None
    magnet_diameter_estimated: bool
    data_status: str
    analog_of: str | None
    sources: list = field(default_factory=list)

    def has_ts(self) -> bool:
        return all(v is not None for v in (self.qts, self.vas_l, self.fs_hz))

    @property
    def sd_m2(self) -> float:
        return self.sd_cm2 / 1e4

    @property
    def vas_m3(self) -> float:
        return self.vas_l / 1e3

    @property
    def xmax_m(self) -> float:
        return self.xmax_mm / 1e3
```

`driver_from_meta`:

```python
def driver_from_meta(meta: dict) -> Driver:
    errors = validate_speaker(meta)
    if errors:
        raise ValueError(f"{meta.get('name')}: " + "; ".join(errors))
    disp = meta.get("displacement_l")
    return Driver(
        slug=meta["name"], brand=meta["brand"], model=meta["model"],
        diameter_in=meta["diameter_in"], impedance_ohm=list(meta["impedance_ohm"]),
        power_w=meta["power_w"], sensitivity_db=meta["sensitivity_db"],
        magnet=meta["magnet"], fs_hz=meta["fs_hz"], re_ohm=meta["re_ohm"],
        qts=meta.get("qts"), qes=meta.get("qes"), qms=meta.get("qms"),
        vas_l=meta.get("vas_l"), xmax_mm=meta.get("xmax_mm"),
        sd_cm2=meta.get("sd_cm2"), le_mh=meta.get("le_mh"),
        cutout_mm=meta["cutout_mm"], bolt_circle_mm=meta["bolt_circle_mm"],
        bolt_count=meta["bolt_count"], depth_mm=meta["depth_mm"],
        weight_kg=meta["weight_kg"],
        displacement_l=disp if disp is not None else DEFAULT_DISPLACEMENT_L,
        displacement_estimated=disp is None,
        frame_diameter_mm=meta["frame_diameter_mm"],
        magnet_diameter_mm=meta.get("magnet_diameter_mm"),
        magnet_diameter_estimated=bool(meta.get("magnet_diameter_estimated", False)),
        data_status=meta["data_status"], analog_of=meta.get("analog_of"),
        sources=list(meta["sources"]),
    )
```

`_speaker_summary`:

```python
def _speaker_summary(driver: Driver, impedance) -> dict:
    return {"slug": driver.slug, "brand": driver.brand, "model": driver.model,
            "impedance_ohm": impedance, "power_w": driver.power_w,
            "sensitivity_db": driver.sensitivity_db, "data_status": driver.data_status,
            "analog_of": driver.analog_of, "cutout_mm": driver.cutout_mm,
            "bolt_circle_mm": driver.bolt_circle_mm, "bolt_count": driver.bolt_count,
            "depth_mm": driver.depth_mm, "weight_kg": driver.weight_kg,
            "displacement_l": driver.displacement_l,
            "displacement_estimated": driver.displacement_estimated,
            "frame_diameter_mm": driver.frame_diameter_mm,
            "magnet_diameter_mm": driver.magnet_diameter_mm,
            "magnet_diameter_estimated": driver.magnet_diameter_estimated}
```


- [ ] **Step 4: The catalog script**

Create `projects/Speaker-cab-system/pipeline/catalog_fields.py`:

```python
"""Add frame and magnet diameters to the speaker catalog notes (Plan 2, Task 1).

Inserts frame_diameter_mm, magnet_diameter_mm, and magnet_diameter_estimated
into each note's YAML frontmatter directly after depth_mm, and appends one
flagged bullet to the note's Data notes list. Values and their basis come from
knowledge/research/speaker-envelopes-and-port-stock.md; estimated magnet
diameters use the conservative top of the research band. Idempotent: a second
run changes nothing.

Run from the vault root:
  .venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py            (dry run)
  .venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py --apply
"""
import argparse
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
DEFAULT_SPEAKERS_DIR = VAULT / "knowledge" / "speakers"
SEE = "See [[speaker-envelopes-and-port-stock]]."
VOICE_COIL = ("- The 141.pdf source is Voice Coil magazine (February 2015), "
              "not a Celestion spec sheet.")

# slug: (frame_diameter_mm, magnet_diameter_mm, estimated, basis or None)
EMINENCE_38 = "top of the 135 to 150 mm band from the published magnet weight and ferrite density"
EMINENCE_59 = "top of the 163 to 181 mm band from the published magnet weight and ferrite density"
WGS_G12M = "by analogy to the Celestion G12M it clones, 145 to 150 mm band"
WGS_V30 = "by analogy to the Celestion Vintage 30 it clones"
FIELDS = {
    "celestion-blue": (309, 128, False, None),
    "celestion-cream": (309, 128, False, None),
    "celestion-gold": (309, 128, False, None),
    "celestion-g12-65-heritage": (309, 145, False, None),
    "celestion-g12m-25-greenback": (309, 150, False, None),
    "celestion-g12m-65-creamback": (309, 150, False, None),
    "celestion-vintage-30": (309, 156, False, None),
    "celestion-g12h-30-anniversary": (309, 156, False, None),
    "celestion-g12h-75-creamback": (309, 168, False, None),
    "celestion-heritage-g12h55": (309, 168, False, None),
    "jensen-c12n": (307.0, 134.0, False, None),
    "jensen-p12n": (307.0, 160.0, False, None),
    "eminence-cannabis-rex": (305.6, 150, True, EMINENCE_38),
    "eminence-red-white-and-blues": (305.6, 150, True, EMINENCE_38),
    "eminence-texas-heat": (305.6, 150, True, EMINENCE_38),
    "eminence-swamp-thang": (305.6, 181, True, EMINENCE_59),
    "eminence-tonker": (305.6, 181, True, EMINENCE_59),
    "wgs-et65": (309.6, 150, True, WGS_G12M),
    "wgs-green-beret": (309.6, 150, True, WGS_G12M),
    "wgs-veteran-30": (309.6, 156, True, WGS_V30),
}


def _bullet(frame, magnet, estimated, basis) -> str:
    if estimated:
        return (f"- Magnet diameter {magnet:g} mm is estimated ({basis}); "
                f"frame diameter {frame:g} mm is published. {SEE}")
    return (f"- Frame diameter {frame:g} mm and magnet diameter {magnet:g} mm "
            f"from the maker's drawing. {SEE}")


def patch_note(text: str, slug: str) -> str:
    frame, magnet, estimated, basis = FIELDS[slug]
    head, body = text.split("\n---\n", 1)
    lines = head.split("\n")
    if not any(line.startswith("frame_diameter_mm:") for line in lines):
        idx = next(i for i, line in enumerate(lines) if line.startswith("depth_mm:"))
        lines[idx + 1:idx + 1] = [f"frame_diameter_mm: {frame:g}",
                                  f"magnet_diameter_mm: {magnet:g}",
                                  f"magnet_diameter_estimated: {'true' if estimated else 'false'}"]
    head = "\n".join(lines)
    section, rest = body.split("\n## Field notes", 1)
    if SEE not in section:
        section = section.rstrip("\n") + "\n" + _bullet(frame, magnet, estimated, basis) + "\n"
    if "2019/10/141.pdf" in head and VOICE_COIL not in section:
        section = section.rstrip("\n") + "\n" + VOICE_COIL + "\n"
    return head + "\n---\n" + section + "\n## Field notes" + rest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--speakers-dir", default=str(DEFAULT_SPEAKERS_DIR))
    ap.add_argument("--apply", action="store_true", help="write the notes (default: dry run)")
    args = ap.parse_args(argv)
    speakers = Path(args.speakers_dir)
    changed = 0
    for slug in sorted(FIELDS):
        path = speakers / f"{slug}.md"
        if not path.exists():
            print(f"{slug}: MISSING note")
            continue
        old = path.read_text()
        new = patch_note(old, slug)
        state = "unchanged" if new == old else "patched"
        frame, magnet, estimated, _ = FIELDS[slug]
        print(f"{slug}: {state}, frame {frame:g}, magnet {magnet:g}"
              f"{' (estimated)' if estimated else ''}")
        if new != old:
            changed += 1
            if args.apply:
                path.write_text(new)
    print(f"{changed} note(s) {'written' if args.apply else 'would change'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Apply it to the catalog**

Run from the vault root:

```bash
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py --apply
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py --apply
```

Expected: the first run lists 20 notes as `patched` and ends `20 note(s) would change`; the second writes them (`20 note(s) written`); the third ends `0 note(s) written` (idempotent). Check one published and one estimated note, for example `knowledge/speakers/celestion-vintage-30.md` (three new frontmatter lines after `depth_mm: 135`, the Data notes bullet "Frame diameter 309 mm and magnet diameter 156 mm from the maker's drawing", and the Voice Coil bullet since its sources cite `2019/10/141.pdf`) and `knowledge/speakers/eminence-tonker.md` (`magnet_diameter_estimated: true`, bullet "Magnet diameter 181 mm is estimated").

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q`
Expected: 356 passed (351 from Plan 1 plus 5).

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cabvoice.py scripts/test_cabvoice.py projects/Speaker-cab-system/pipeline/catalog_fields.py knowledge/speakers/*.md
git commit -m "Speaker cab plan 2 task 1: frame and magnet diameters in the catalog and the engine"
```
<!-- /include -->

---

<!-- include: .vault/plan/task2.md -->
### Task 2: Engine touches: tube table, shell margins, height floor

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

```python
def test_size_port_grows_when_too_short(drv):
    # 60 L at 60 Hz: a 75 mm port needs a negative length, about 100 mm works,
    # which snaps up to the 101.5 mm (4 inch) tube
    p = cabvoice.size_port(drv, 60.0, 60.0, diameter_mm=75.0)
    assert p.diameter_mm == 101.5
    assert p.length_mm >= cabvoice.MIN_PORT_LENGTH_MM
    assert not any("too short" in w for w in p.warnings)
    assert any(w.startswith("port diameter snapped to the 101.5 mm tube") for w in p.warnings)
```

```python
def test_dims_for_volume_min_width_for_two_drivers():
    min_w = cabvoice.min_internal_width_mm(2, 283.0)
    assert min_w == pytest.approx(722.0)
    box = cabvoice.dims_for_volume(90.0, min_internal_width_mm=min_w)
    assert box.internal_mm[0] == pytest.approx(722.0)
    assert box.gross_l == pytest.approx(90.0, abs=0.01)
```

```python
def test_propose_closed_ported_1x12(drv, tone):
    tone["low_end"] = "balanced"
    tone["min_power_w"] = 90              # a 60 W amp
    v = cabvoice.propose([drv], [16], "closed-ported", tone, name="test-1x12")
    assert v.mode == "propose" and v.name == "test-1x12"
    assert v.volumes["method"] == "thiele-small"
    assert v.volumes["per_driver_net_l"] == pytest.approx(60.0)
    assert v.port is not None and v.port["shape"] == "round"
    assert v.prediction["model"] == "thiele-small vented"
    assert v.prediction["fb_hz"] == pytest.approx(60.0)
    assert v.wiring["recommended"]["impedance_ohm"] == 16
    assert v.blockers == []
    assert v.power["status"] == "warning"          # 60 W handling under the 90 W target
    assert v.box["external_mm"][0] > v.box["internal_mm"][0]
    assert v.volumes["gross_l"] == pytest.approx(
        v.volumes["net_total_l"] + v.volumes["displacement_l"] + v.volumes["port_l"]
        + v.volumes["inside_parts_l"], abs=0.05)
    assert v.volumes["inside_parts_l"] > 1.0        # cleats and stiffeners of a 1x12
    assert v.prediction_status == "unverified, ears only"
```

```python
def test_propose_stereo_2x12_closed(drv, tone):
    tone["impedance_options_ohm"] = [16]
    v = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="stereo")
    assert v.enclosure["chambers"] == 2
    assert v.volumes["divider_l"] > 0
    assert len(v.wiring["options"]) == 2
    assert len(v.power["per_side"]) == 2
    assert v.prediction["model"] == "thiele-small closed"
    # each chamber: 44 mm to its shell wall, the cutout, 25 mm to the divider
    assert v.box["chamber_internal_width_mm"] >= (
        drv.cutout_mm + cabvoice.SHELL_MARGIN_MM + cabvoice.CUTOUT_MARGIN_MM - 1e-6)
```

```python
def test_propose_stereo_volumes_reconcile(drv, tone):
    tone["impedance_options_ohm"] = [16]
    v = cabvoice.propose([drv, drv], [16, 16], "closed-ported", tone, jack_config="stereo")
    vol = v.volumes
    parts = (vol["net_total_l"] + vol["displacement_l"] + vol["brace_l"] + vol["port_l"]
             + vol["divider_l"] + vol["inside_parts_l"])
    assert vol["gross_l"] == pytest.approx(parts, abs=0.01)
    # port_l is the air inside the box: the tube's length through the back panel is outside
    inside = v.port["area_cm2"] / 1e4 * (v.port["length_mm"] - cabvoice.BACK_MM)
    assert vol["port_l"] == pytest.approx(2 * inside, abs=1e-6)
    assert vol["port_l"] < 2 * v.port["volume_l"]
```

```python
def test_propose_impossible_box_presents_tradeoff(drv, tone, speakers_dir, tmp_path):
    tone["low_end"] = "big"                  # 68 L per driver against the site's 45.6 L box
    c = cabvoice.Constraints(max_external_mm=(508.0, 457.2, 279.4))
    v = cabvoice.propose([drv], [16], "closed", tone, constraints=c)
    assert v.volumes["gross_l"] == pytest.approx(45.6, abs=0.05)
    assert v.prediction["qtc"] == pytest.approx(cabvoice.closed_box(drv, v.volumes["per_driver_net_l"]).qtc)
    blocker = next(b for b in v.blockers if "cannot fit the size limit" in b)
    assert "71.1 L" in blocker and "45.6 L" in blocker and "Qtc" in blocker
    assert not any("cannot reach" in w for w in v.warnings)
    big_tone = tmp_path / "tone.json"
    big_tone.write_text(json.dumps(tone))
    out = tmp_path / "out"
    rc = cabvoice.main(["propose", "--speakers-dir", str(speakers_dir), "--speaker", "test-driver",
                        "--impedance", "16", "--enclosure", "closed", "--tone", str(big_tone),
                        "--max-external", "508", "457.2", "279.4", "--out", str(out)])
    assert rc == 2
    assert "cannot fit the size limit" in json.loads((out / "voicing.json").read_text())["blockers"][0]
```

```python
def test_evaluate_site_default_closed(drv, tone):
    v = cabvoice.evaluate([drv], [16], "closed", tone, SITE_INTERNAL, name="site-closed")
    assert v.mode == "evaluate"
    assert v.volumes["gross_l"] == pytest.approx(45.6, abs=0.05)
    # 45.6 gross, 1.5 L driver, 1.58 L of cleats and stiffeners (inside_parts_l)
    assert v.volumes["inside_parts_l"] == pytest.approx(1.58, abs=0.01)
    assert v.volumes["net_total_l"] == pytest.approx(42.5, abs=0.05)
    # alpha = 60 / 42.5 = 1.41, Qtc = 0.4 * sqrt(2.41) = 0.621
    assert v.prediction["qtc"] == pytest.approx(0.621, abs=0.005)
    assert v.prediction["character"] == "tight"
    assert v.box["external_in"] == pytest.approx((20.0, 18.0, 11.0), abs=0.01)
```

```python
def test_evaluate_ported_reports_tuning_from_port(drv, tone):
    port = cabvoice.port_dims(44.0, 70.0, diameter_mm=100.0)
    port.length_mm = 23.0
    v = cabvoice.evaluate([drv], [16], "closed-ported", tone, SITE_INTERNAL, port=port)
    assert 65.0 < v.prediction["fb_hz"] < 75.0
    assert v.port["volume_l"] == pytest.approx(0.18, abs=0.01)      # the whole 23 mm tube
    assert v.volumes["port_l"] == pytest.approx(0.086, abs=0.005)   # the 11 mm inside the box
    assert v.port["length_mm"] == 23.0
    assert v.port["air_speed_ms"] > 0
```

```python
def _matrix_params():
    rows = [(enclosure, jack, n, None) for enclosure in cabvoice.ENCLOSURE_TYPES
            for jack, n in (("mono", 1), ("mono", 2), ("stereo", 2))]
    rows.append(("closed-ported", "mono", 1, (352.0, 40.0)))    # a slot port, evaluated as built
    return [pytest.param(slug, enclosure, jack, n, slot,
                         id=f"{slug}-{enclosure}-{jack}-{n}" + ("-slot" if slot else ""))
            for slug in cabvoice.list_speakers(CATALOG)
            for enclosure, jack, n, slot in rows]
```

```python
@pytest.mark.parametrize("slug,enclosure,jack,n,slot", _matrix_params())
def test_evaluate_reproduces_propose(tone, slug, enclosure, jack, n, slot):
    d = cabvoice.load_speaker(slug, CATALOG)
    z = 16 if 16 in d.impedance_ohm else d.impedance_ohm[0]
    c = cabvoice.Constraints(port_slot_mm=slot)
    p = cabvoice.propose([d] * n, [z] * n, enclosure, tone, jack_config=jack, constraints=c,
                         name=slug)
    e = cabvoice.evaluate([d] * n, [z] * n, enclosure, tone, p.box["internal_mm"],
                          jack_config=jack, port=_port_from_json(p.port), constraints=c, name=slug)
    for key, tol in (("fb_hz", 0.05), ("f3_hz", 0.05), ("peak_db", 0.01), ("qtc", 0.01)):
        a, b = p.prediction.get(key), e.prediction.get(key)
        assert (a is None) == (b is None), key
        if a is not None:
            assert a == pytest.approx(b, abs=tol), key
    assert p.prediction["character"] == e.prediction["character"]
    assert p.volumes["per_driver_net_l"] == pytest.approx(e.volumes["per_driver_net_l"], abs=0.05)
    for vol in (p.volumes, e.volumes):
        parts = (vol["net_total_l"] + vol["displacement_l"] + vol["brace_l"] + vol["port_l"]
                 + vol["divider_l"] + vol["inside_parts_l"])
        assert vol["gross_l"] == pytest.approx(parts, abs=0.05)
```

```python
def test_propose_mono_2x12_uses_one_port_per_driver(tone):
    d = _driver(**CANNABIS_REX)
    one = cabvoice.propose([d], [16], "closed-ported", tone)
    two = cabvoice.propose([d, d], [16, 16], "closed-ported", tone, jack_config="mono")
    assert two.port["count"] == 2 and one.port["count"] == 1
    assert two.construction["port_count"] == 2
    assert not any("too short" in w or "port clamped" in w for w in two.warnings)
    assert two.port["diameter_mm"] == pytest.approx(one.port["diameter_mm"])
    assert two.port["length_mm"] == pytest.approx(one.port["length_mm"])
    assert two.port["air_speed_ms"] == pytest.approx(one.port["air_speed_ms"])
    assert two.volumes["port_l"] == pytest.approx(2 * one.volumes["port_l"])
    assert two.prediction["fb_hz"] == pytest.approx(one.prediction["fb_hz"], abs=1e-6)
    single = cabvoice.propose([d, d], [16, 16], "closed-ported", tone, jack_config="mono",
                              constraints=cabvoice.Constraints(port_count=1))
    # one shared port: the same largest tube cannot be long enough for twice the
    # drivers, so it is clamped at 20 mm, tunes low, and moves more air per area
    assert single.port["count"] == 1
    assert single.port["diameter_mm"] >= two.port["diameter_mm"]
    assert single.port["air_speed_ms"] > two.port["air_speed_ms"]
    assert any("port clamped at the size cap" in w for w in single.warnings)
```


Append at the end of the file:

```python
# ---- Plan 2 Task 2: tube table, margins, floors -------------------------

def test_snap_tube_id_table():
    assert cabvoice.PORT_TUBE_ID_MM == (52.0, 77.3, 101.5, 153.2)
    assert set(cabvoice.PORT_TUBE_OD_MM) == set(cabvoice.PORT_TUBE_ID_MM)
    assert cabvoice.MAX_PORT_DIAMETER_MM == 153.2
    assert cabvoice.DEFAULT_PORT_DIAMETER_MM == 77.3
    for solved, tube in ((40.0, 52.0), (52.0, 52.0), (75.0, 77.3), (77.3, 77.3),
                         (100.0, 101.5), (120.0, 153.2), (200.0, 153.2)):
        assert cabvoice.snap_tube_id(solved) == tube, solved


def test_size_port_snaps_round_ports_and_leaves_slots(drv):
    p = cabvoice.size_port(drv, 40.0, 60.0, diameter_mm=75.0)
    assert p.diameter_mm == 77.3
    assert any(w == "port diameter snapped to the 77.3 mm tube (from 75.0 mm)" for w in p.warnings)
    q = cabvoice.size_port(drv, 40.0, 60.0, diameter_mm=77.3)
    assert q.diameter_mm == 77.3 and not any("snapped" in w for w in q.warnings)
    s = cabvoice.size_port(drv, 40.0, 60.0, slot_mm=(200.0, 30.0))
    assert s.shape == "slot" and s.slot_w_mm == 200.0
    assert not any("snapped" in w for w in s.warnings)


def test_propose_port_is_a_purchasable_tube(drv, tone):
    v = cabvoice.propose([drv], [16], "closed-ported", tone)
    assert v.port["diameter_mm"] in cabvoice.PORT_TUBE_ID_MM
    tuned = cabvoice.port_tuning_hz(v.volumes["per_chamber_net_l"] / 1e3,
                                    v.port["area_cm2"] / 1e4, v.port["length_mm"] / 1e3)
    assert v.prediction["fb_hz"] == pytest.approx(tuned, abs=1e-9)


def test_cli_port_diameter_default_is_the_tube_start():
    args = cabvoice._build_parser().parse_args(
        ["propose", "--speaker", "x", "--impedance", "8", "--enclosure", "closed",
         "--tone", "t.json", "--out", "o"])
    assert args.port_diameter == cabvoice.DEFAULT_PORT_DIAMETER_MM
    assert cabvoice.Constraints().port_diameter_mm == cabvoice.DEFAULT_PORT_DIAMETER_MM


def test_min_internal_width_and_height():
    assert cabvoice.SHELL_MARGIN_MM == 44.0 and cabvoice.CUTOUT_GAP_MM == 68.0
    assert cabvoice.CUTOUT_MARGIN_MM == 25.0
    assert cabvoice.min_internal_width_mm(1, 283.0) == pytest.approx(371.0)
    assert cabvoice.min_internal_width_mm(2, 283.0) == pytest.approx(722.0)
    assert cabvoice.min_internal_height_mm(283.0) == pytest.approx(371.0)
    assert cabvoice.min_internal_height_mm(283.0, None) == pytest.approx(371.0)
    assert cabvoice.min_internal_height_mm(283.0, 40.0) == pytest.approx(429.0)


def test_dims_for_volume_height_floor():
    box = cabvoice.dims_for_volume(30.0, min_internal_height_mm=429.0)
    assert box.internal_mm[1] == pytest.approx(429.0)
    assert box.gross_l == pytest.approx(30.0, abs=0.01)
    free = cabvoice.dims_for_volume(30.0)
    assert box.internal_mm[0] < free.internal_mm[0] and box.internal_mm[2] < free.internal_mm[2]
    with pytest.raises(ValueError, match="height"):
        cabvoice.dims_for_volume(60.0, min_internal_height_mm=429.0,
                                 max_external_mm=(600.0, 457.2, 400.0))
    with pytest.raises(ValueError, match="width"):      # the width floor gets the same guard
        cabvoice.dims_for_volume(90.0, min_internal_width_mm=722.0,
                                 max_external_mm=(700.0, 600.0, 400.0))


def test_propose_stereo_and_mono_2x12_share_the_width_floor(drv, tone):
    tone["impedance_options_ohm"] = [16]
    floor = cabvoice.min_internal_width_mm(2, drv.cutout_mm)
    mono = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="mono")
    stereo = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="stereo")
    assert mono.box["internal_mm"][0] == pytest.approx(floor)
    assert stereo.box["internal_mm"][0] == pytest.approx(floor)
    assert stereo.box["chamber_internal_width_mm"] == pytest.approx((floor - cabvoice.PANEL_MM) / 2)


def test_propose_slot_port_raises_the_height_floor(drv, tone):
    c = cabvoice.Constraints(port_slot_mm=(472.0, 40.0), pinned_external_width_mm=508.0)
    v = cabvoice.propose([drv], [16], "closed-ported", tone, constraints=c)
    assert v.port["shape"] == "slot"
    floor = cabvoice.min_internal_height_mm(drv.cutout_mm, v.port["slot_h_mm"])
    assert floor >= 429.0
    assert v.box["internal_mm"][1] >= floor - 1e-6
    plain = cabvoice.propose([drv], [16], "closed", tone,
                             constraints=cabvoice.Constraints(pinned_external_width_mm=508.0))
    assert plain.box["internal_mm"][1] < 429.0


def test_propose_hardwood_floors_add_two_mm(drv, tone):
    tone["impedance_options_ohm"] = [16]
    floor_w = cabvoice.min_internal_width_mm(2, drv.cutout_mm)
    for line, extra in (("tolex", 0.0), ("hardwood", cabvoice.HARDWOOD_FLOOR_EXTRA_MM)):
        v = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="mono",
                             constraints=cabvoice.Constraints(line=line))
        assert v.box["internal_mm"][0] == pytest.approx(floor_w + extra)
    # a 30 L box pinned 700 mm wide would scale to about 300 mm tall: the height floor holds it
    small = _driver(vas_l=20.0)
    for line, extra in (("tolex", 0.0), ("hardwood", cabvoice.HARDWOOD_FLOOR_EXTRA_MM)):
        v = cabvoice.propose([small], [16], "closed", tone,
                             constraints=cabvoice.Constraints(line=line, pinned_external_width_mm=700.0))
        assert v.box["internal_mm"][1] == pytest.approx(cabvoice.min_internal_height_mm(283.0) + extra)
        assert v.box["internal_mm"][1] >= 371.0 + extra - 1e-6


def test_propose_2x12_slot_holds_both_floors(drv, tone):
    tone["impedance_options_ohm"] = [16]
    for line, extra in (("tolex", 0.0), ("hardwood", cabvoice.HARDWOOD_FLOOR_EXTRA_MM)):
        for jack in ("mono", "stereo"):
            c = cabvoice.Constraints(port_slot_mm=(352.0, 40.0), line=line)
            v = cabvoice.propose([drv, drv], [16, 16], "closed-ported", tone, jack_config=jack,
                                 constraints=c)
            w, h, _ = v.box["internal_mm"]
            assert w >= cabvoice.min_internal_width_mm(2, drv.cutout_mm) + extra - 1e-6, (line, jack)
            floor_h = cabvoice.min_internal_height_mm(drv.cutout_mm, v.port["slot_h_mm"]) + extra
            assert h >= floor_h - 1e-6, (line, jack, h, floor_h)
            assert v.volumes["gross_l"] == pytest.approx(
                v.volumes["net_total_l"] + v.volumes["displacement_l"] + v.volumes["port_l"]
                + v.volumes["divider_l"] + v.volumes["inside_parts_l"], abs=0.01)


def test_inside_parts_site_box_by_hand():
    site = (472.0, 421.2, 229.4)
    # 1x12 closed: baffle cleats 2 x 472 x 18 x 18 + 2 x (421.2 - 36) x 18 x 18 = 0.555 L,
    # the same again at the back = 0.555 L, top and bottom stiffeners (472 > 450)
    # 2 x 18 x 40 x (229.4 - 36) = 0.278 L, back stiffener 18 x 40 x (421.2 - 156) = 0.191 L
    closed = cabvoice.inside_parts_l(site, "closed", 1, 1, "mono", None, "tolex")
    assert closed == pytest.approx(0.555 + 0.555 + 0.278 + 0.191, rel=0.05)
    # a 101.5 mm tube 40 mm long adds its wall inside the box (28 mm) and the ring:
    # pi/4 (114.3^2 - 101.5^2) x 28 = 0.061 L, pi/4 (174.3^2 - 114.3^2) x 12 = 0.163 L
    port = cabvoice.port_dims(1.0, 1.0, diameter_mm=101.5)
    port.length_mm = 40.0
    ported = cabvoice.inside_parts_l(site, "closed-ported", 1, 1, "mono", port, "tolex")
    assert ported == pytest.approx(closed + 0.061 + 0.163, rel=0.05)
    assert ported == pytest.approx(1.80, rel=0.05)
    # a mono 2x12 at the floor width adds the brace and loses the top and bottom stiffeners
    wide = (722.0, 421.2, 229.4)
    two = cabvoice.inside_parts_l(wide, "closed", 2, 1, "mono", None, "tolex")
    one_wide = cabvoice.inside_parts_l(wide, "closed", 1, 1, "mono", None, "tolex")
    assert two - one_wide == pytest.approx(18 * 60 * 421.2 / 1e6 - 2 * 18 * 40 * 193.4 / 1e6, abs=0.01)
    # a slot: shelf full width x length x 18 less its 18 mm through the baffle (the shelf
    # starts at the baffle face), no bottom baffle cleat, shorter side cleats
    slot = cabvoice.port_dims(1.0, 1.0, slot_mm=(472.0, 40.0))
    slot.length_mm = 120.0
    slotted = cabvoice.inside_parts_l(site, "closed-ported", 1, 1, "mono", slot, "tolex")
    shelf = 472 * (120 - 18) * 18 / 1e6
    lost_cleats = (472 * 18 * 18 + 2 * 40 * 18 * 18) / 1e6      # bottom cleat, 40 mm off each side cleat
    lost_bottom_stiffener = 18 * 40 * (193.4 - (229.4 - 120.0)) / 1e6
    assert slotted == pytest.approx(closed + shelf - lost_cleats - lost_bottom_stiffener, abs=0.01)
    # a narrower slot adds two 60 mm cheeks, the same 102 mm inside the box
    narrow = cabvoice.port_dims(1.0, 1.0, slot_mm=(352.0, 40.0))
    narrow.length_mm = 120.0
    cheeked = cabvoice.inside_parts_l(site, "closed-ported", 1, 1, "mono", narrow, "tolex")
    assert cheeked - slotted == pytest.approx(2 * 60 * (120 - 18) * 40 / 1e6, abs=1e-9)


def test_evaluate_site_box_reports_inside_parts(drv, tone):
    port = cabvoice.port_dims(1.0, 1.0, diameter_mm=101.5)
    port.length_mm = 40.0
    v = cabvoice.evaluate([drv], [16], "closed-ported", tone, SITE_INTERNAL, port=port)
    assert v.volumes["inside_parts_l"] == pytest.approx(1.80, abs=0.02)
    assert v.volumes["port_l"] == pytest.approx(0.008091 * 28.0, abs=0.002)
    assert v.volumes["net_total_l"] == pytest.approx(42.1, abs=0.05)
    md = cabvoice.render_markdown(v)
    assert "| Inside parts (cleats, stiffeners, shelf, ring) | 1.80 L |" in md


@pytest.mark.parametrize("jack,n,slot,max_external", [
    pytest.param("mono", 1, None, (508.0, 457.2, 279.4), id="1x12-round"),
    pytest.param("mono", 2, None, (800.0, 500.0, 350.0), id="mono-2x12-round"),
    pytest.param("stereo", 2, None, (800.0, 500.0, 350.0), id="stereo-2x12-round"),
    pytest.param("mono", 1, (472.0, 25.0), (508.0, 457.2, 279.4), id="1x12-slot"),
    pytest.param("mono", 2, (352.0, 40.0), (800.0, 500.0, 350.0), id="mono-2x12-slot"),
    pytest.param("stereo", 2, (352.0, 40.0), (800.0, 500.0, 350.0), id="stereo-2x12-slot"),
])
def test_propose_limited_ported_volumes_reconcile(drv, tone, jack, n, slot, max_external):
    # "big" asks 68 L per driver, more than these limits hold: the size limit wins and the
    # net must follow the port and inside parts as finally sized, not the previous pass's
    tone["low_end"] = "big"
    tone["impedance_options_ohm"] = [16]
    c = cabvoice.Constraints(max_external_mm=max_external, port_slot_mm=slot)
    v = cabvoice.propose([drv] * n, [16] * n, "closed-ported", tone, jack_config=jack, constraints=c)
    assert any("cannot fit the size limit" in b for b in v.blockers)
    vol = v.volumes
    parts = (vol["net_total_l"] + vol["displacement_l"] + vol["brace_l"] + vol["port_l"]
             + vol["divider_l"] + vol["inside_parts_l"])
    assert vol["gross_l"] == pytest.approx(parts, abs=0.01)
    # the port is tuned for the chamber net as reported
    tuned = cabvoice.port_tuning_hz(vol["per_chamber_net_l"] / v.port["count"] / 1e3,
                                    v.port["area_cm2"] / 1e4, v.port["length_mm"] / 1e3)
    assert v.prediction["fb_hz"] == pytest.approx(tuned, abs=1e-9)
    # both floors hold against the port as finally sized
    w, h, _ = v.box["internal_mm"]
    assert w >= cabvoice.min_internal_width_mm(n, drv.cutout_mm) - 1e-6
    slot_h = v.port["slot_h_mm"] if v.port["shape"] == "slot" else None
    assert h >= cabvoice.min_internal_height_mm(drv.cutout_mm, slot_h) - 1e-6


def test_size_port_clamps_the_start_to_the_largest_tube(drv):
    p = cabvoice.size_port(drv, 40.0, 60.0, diameter_mm=200.0)
    assert p.diameter_mm == 153.2
    assert not any("snapped" in w for w in p.warnings)      # clamped before the loop, not snapped down


def test_inside_parts_tube_wall_tolerates_float_noise():
    site = (472.0, 421.2, 229.4)
    exact = cabvoice.port_dims(1.0, 1.0, diameter_mm=101.5)
    noisy = cabvoice.port_dims(1.0, 1.0, diameter_mm=101.5 + 1e-6)
    exact.length_mm = noisy.length_mm = 40.0
    a = cabvoice.inside_parts_l(site, "closed-ported", 1, 1, "mono", exact, "tolex")
    b = cabvoice.inside_parts_l(site, "closed-ported", 1, 1, "mono", noisy, "tolex")
    assert b == pytest.approx(a, abs=1e-6)


def test_inside_parts_uses_the_divider_thickness(drv, tone):
    wide = (722.0, 421.2, 229.4)
    thin = cabvoice.inside_parts_l(wide, "closed", 2, 2, "stereo", None, "tolex")
    thick = cabvoice.inside_parts_l(wide, "closed", 2, 2, "stereo", None, "tolex", panel_mm=19.0)
    # a 19 mm divider takes 0.5 mm off each of the eight 18 x 18 cleat runs across the chambers
    assert thin - thick == pytest.approx(8 * 0.5 * 18 * 18 / 1e6, abs=1e-9)
    tone["impedance_options_ohm"] = [16]
    v = cabvoice.evaluate([drv, drv], [16, 16], "closed", tone, wide, jack_config="stereo",
                          constraints=cabvoice.Constraints(panel_mm=19.0))
    assert v.volumes["inside_parts_l"] == pytest.approx(thick, abs=1e-9)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q -k "snap or floor or height or purchasable or tube_start or min_internal or too_short or two_drivers or stereo_2x12 or one_port_per_driver"`
Expected: FAIL (`snap_tube_id` undefined, old constants).

- [ ] **Step 3: Engine changes**

In `scripts/cabvoice.py` replace each of these with the version below (full text).

port constants (replace the two lines `MIN_PORT_LENGTH_MM = 20.0` and `MAX_PORT_DIAMETER_MM = 150.0`):

```python
MIN_PORT_LENGTH_MM = 20.0
# Purchasable round port tubes: Schedule 40 PVC or ABS inside diameters for
# 2, 3, 4, and 6 inch nominal pipe, with their outside diameters. Starting
# values (see speaker-cab-construction); the hard maximum is the largest tube.
PORT_TUBE_ID_MM = (52.0, 77.3, 101.5, 153.2)
PORT_TUBE_OD_MM = {52.0: 60.3, 77.3: 88.9, 101.5: 114.3, 153.2: 168.3}
MAX_PORT_DIAMETER_MM = 153.2
DEFAULT_PORT_DIAMETER_MM = 77.3
```

`snap_tube_id` (new, directly above `size_port`):

```python
def snap_tube_id(diameter_mm: float) -> float:
    """Smallest purchasable tube inside diameter not below diameter_mm, else the largest."""
    for tube in PORT_TUBE_ID_MM:
        if tube >= diameter_mm - 1e-9:
            return tube
    return PORT_TUBE_ID_MM[-1]
```

`size_port`:

```python
def size_port(driver: Driver, vb_l: float, fb_hz: float,
              diameter_mm: float = DEFAULT_PORT_DIAMETER_MM,
              slot_mm: tuple | None = None) -> Port:
    """Port for (vb, fb), enlarged in 10 percent area steps until the
    worst-case air speed is under PORT_V_MAX and the physical length is at
    least MIN_PORT_LENGTH_MM. A round start above MAX_PORT_DIAMETER_MM is
    clamped to it first. Stops at the MAX_PORT_DIAMETER_MM equivalent area
    and leaves the warnings in place for the caller. A round port is then
    snapped up to the next purchasable tube (PORT_TUBE_ID_MM) and re-solved,
    so the sheet describes a tube that can be bought."""
    max_area_cm2 = math.pi * (MAX_PORT_DIAMETER_MM / 20.0) ** 2
    if not slot_mm:
        diameter_mm = min(diameter_mm, MAX_PORT_DIAMETER_MM)

    def build(dia, slot):
        p = port_dims(vb_l, fb_hz, diameter_mm=None if slot else dia, slot_mm=slot)
        p.air_speed_ms = port_air_speed(driver, fb_hz, p.area_cm2)
        return p

    port = build(diameter_mm, slot_mm)
    for _ in range(60):
        too_fast = port.air_speed_ms > PORT_V_MAX
        too_short = any("too short" in w for w in port.warnings)
        if not (too_fast or too_short) or port.area_cm2 >= max_area_cm2 - 1e-9:
            break
        if slot_mm:
            slot_mm = (slot_mm[0], min(slot_mm[1] * 1.1, max_area_cm2 * 100.0 / slot_mm[0]))
        else:
            diameter_mm = min(diameter_mm * math.sqrt(1.1), MAX_PORT_DIAMETER_MM)
        port = build(diameter_mm, slot_mm)
    if not slot_mm:
        solved = port.diameter_mm
        tube = snap_tube_id(solved)
        port = build(tube, None)
        if abs(tube - solved) > 0.05:
            port.warnings.append(f"port diameter snapped to the {tube:g} mm tube "
                                 f"(from {solved:.1f} mm)")
    if port.air_speed_ms > PORT_V_MAX:
        port.warnings.append(f"port air speed {port.air_speed_ms:.1f} m/s still above "
                             f"{PORT_V_MAX} m/s at the maximum port size")
    return port
```

box constants (replace the block from `MM_PER_INCH` to `BASE_EXTERNAL_IN`):

```python
MM_PER_INCH = 25.4
PANEL_MM = 18.0
BACK_MM = 12.0
BAFFLE_MM = 18.0
RECESS_MM = 20.0
CUTOUT_MARGIN_MM = 25.0    # cutout edge to brace or divider
SHELL_MARGIN_MM = 44.0     # cutout edge to shell inner face: grill strip 40 + 2 clearance + 2
CUTOUT_GAP_MM = 68.0       # between the two cutouts of a 2x12: brace or divider 18 + 2 x 25
HARDWOOD_FLOOR_EXTRA_MM = 2.0   # the hardwood line's 19 mm panels take 1 mm per side from the 18 mm box
BASE_EXTERNAL_IN = (20.0, 18.0, 11.0)
# Parts the generator builds inside the air box (knowledge/speaker-cab-construction):
CLEAT_MM = 18.0                 # 18 x 18 cleats along the baffle and the back
STIFFENER_MM = (18.0, 40.0)     # 18 proud, 40 flat, across any span over SPAN_MAX_MM
SPAN_MAX_MM = 450.0
BRACE_MM = (18.0, 60.0)         # center brace on a mono 2x12
JACK_PLATE_H_MM = 70.0          # jack plate cutout height; the back stiffener stops above it
JACK_CLEAR_MM = 25.0
FLANGE_RING_T_MM = 12.0         # plywood flange ring on the inside of the back for a round port
FLANGE_RING_EXTRA_MM = 60.0     # ring outside diameter = tube outside diameter + 60
TUBE_WALL_FALLBACK_MM = 5.5     # wall assumed for a tube diameter outside PORT_TUBE_ID_MM
```

`min_internal_width_mm`:

```python
def min_internal_width_mm(driver_count: int, cutout_mm: float) -> float:
    """Cutouts side by side, 44 mm to each shell wall and a 68 mm gap between
    two (the brace or divider plus 25 mm each side); the same floor for a mono
    and a stereo 2x12 because the divider replaces the brace."""
    return driver_count * cutout_mm + (driver_count - 1) * CUTOUT_GAP_MM + 2 * SHELL_MARGIN_MM
```

`min_internal_height_mm` (new):

```python
def min_internal_height_mm(cutout_mm: float, slot_h_mm: float | None = None) -> float:
    """Cutout plus 44 mm top and bottom; a front slot port adds its height and
    the 18 mm shelf under the baffle."""
    extra = (slot_h_mm + BAFFLE_MM) if slot_h_mm else 0.0
    return cutout_mm + 2 * SHELL_MARGIN_MM + extra
```

`dims_for_volume`:

```python
def dims_for_volume(gross_l: float, pinned_external_width_mm: float | None = None,
                    min_internal_width_mm: float | None = None,
                    max_external_mm: tuple | None = None,
                    min_internal_height_mm: float | None = None, strict: bool = True,
                    **panel_kwargs) -> Box:
    """Internal dimensions for a gross volume, starting from the site box
    proportions. Fixed axes come from a pinned width, the driver minimum
    width, the minimum height, or external limits; free axes scale together
    to hit the volume. When the limits cannot hold the volume, strict raises;
    otherwise the largest box that fits comes back with a "cannot reach" warning."""
    if gross_l <= 0:
        raise ValueError("gross_l must be positive")
    target = gross_l * 1e6
    base = list(site_default_box(**panel_kwargs).internal_mm)
    scale = (target / (base[0] * base[1] * base[2])) ** (1.0 / 3.0)
    dims = [x * scale for x in base]
    fixed = [False, False, False]
    conflicts = []
    if pinned_external_width_mm is not None:
        dims[0] = internal_from_external((pinned_external_width_mm, 0, 0), **panel_kwargs)[0]
        fixed[0] = True
    if min_internal_width_mm is not None and dims[0] < min_internal_width_mm:
        if fixed[0]:
            conflicts.append(
                f"pinned width {pinned_external_width_mm:g} mm external is below the "
                f"{min_internal_width_mm:g} mm internal minimum for the driver count; using the minimum")
        dims[0] = min_internal_width_mm
        fixed[0] = True
    max_internal = None
    if max_external_mm is not None:
        max_internal = internal_from_external(max_external_mm, **panel_kwargs)
        if fixed[0] and dims[0] > max_internal[0]:
            raise ValueError(
                f"width {dims[0]:.1f} mm internal (pinned or the driver-count minimum) "
                f"exceeds the size limit {max_internal[0]:.1f} mm internal")
        if min_internal_width_mm is not None and min_internal_width_mm > max_internal[0] + 1e-9:
            raise ValueError(
                f"width {min_internal_width_mm:.1f} mm internal (the driver-count minimum) "
                f"exceeds the size limit {max_internal[0]:.1f} mm internal")
        if min_internal_height_mm is not None and min_internal_height_mm > max_internal[1] + 1e-9:
            raise ValueError(
                f"height {min_internal_height_mm:.1f} mm internal (the cutout minimum) "
                f"exceeds the size limit {max_internal[1]:.1f} mm internal")

    def rescale():
        free = [i for i in range(3) if not fixed[i]]
        if not free:
            return
        fixed_prod = 1.0
        for i in range(3):
            if fixed[i]:
                fixed_prod *= dims[i]
        free_prod = 1.0
        for i in free:
            free_prod *= dims[i]
        k = (target / fixed_prod / free_prod) ** (1.0 / len(free))
        for i in free:
            dims[i] *= k

    def apply_floors() -> bool:
        """Lift any free axis that fell under its floor; True when one moved."""
        moved = False
        for i, floor in ((0, min_internal_width_mm), (1, min_internal_height_mm)):
            if floor is not None and not fixed[i] and dims[i] < floor - 1e-9:
                dims[i] = floor
                fixed[i] = True
                moved = True
        return moved

    for _ in range(3):   # a floor on one axis shrinks the others on rescale; settle both
        rescale()
        if not apply_floors():
            break
    for _ in range(3):
        if max_internal is None:
            break
        changed = False
        for i in range(3):
            if not fixed[i] and dims[i] > max_internal[i]:
                dims[i] = max_internal[i]
                fixed[i] = True
                changed = True
        if not changed:
            break
        rescale()
    achieved = dims[0] * dims[1] * dims[2]
    if abs(achieved - target) / target > 0.001:
        message = (f"cannot reach {gross_l:.1f} L within the internal size limit; "
                   f"achievable {achieved / 1e6:.1f} L")
        if strict:
            raise ValueError(message)
        conflicts.append(message)
    box = make_box(tuple(dims), **panel_kwargs)
    box.warnings = conflicts + box.warnings
    return box
```

`_port_inside_l` and `inside_parts_l` (new, directly above the tone target section):

```python
def _port_inside_l(port: Port) -> float:
    """Port air inside the internal box, liters: a round tube's length through
    the back panel and a slot's length through the baffle lie outside the box."""
    panel = BAFFLE_MM if port.shape == "slot" else BACK_MM
    return port.area_cm2 / 1e4 * max(port.length_mm - panel, 0.0)


def inside_parts_l(internal_mm, enclosure: str, driver_count: int, chambers: int,
                   jack_config: str, port: Port | None, line: str,
                   port_count: int | None = None, panel_mm: float = PANEL_MM) -> float:
    """Liters taken by the parts the generator builds inside the air box,
    estimated the way scripts/cablayout.py builds them: 18 x 18 cleats along
    the baffle (top, bottom unless a slot port, two outer sides) and the back
    (closed: a full frame; open: top, bottom, and the panel-height side
    cleats), the modeled center brace of a mono 2x12 (Constraints.brace_l and
    --brace-l mean extra bracing beyond it), 18 x 40 stiffeners across any
    shell or back span over 450 mm between glued members (the back one stops
    above the jack plate), the slot shelf and cheeks behind the baffle (the
    shelf starts at the baffle face, so its 18 mm through the baffle lies
    outside the box), and a round port's tube wall and flange ring. The
    divider and the port air have their own volume terms. Every part is birch
    on both lines; line and jack_config are accepted for symmetry with the
    callers and unused. panel_mm is the divider thickness of a stereo box."""
    w, h, d = internal_mm
    per_chamber = driver_count // chambers
    count = port_count or per_chamber
    closed = enclosure in ("closed", "closed-ported")
    slot = port is not None and port.shape == "slot"
    slot_h = port.slot_h_mm if slot else 0.0
    shelf = port.length_mm if slot else 0.0
    w_c = (w - panel_mm) / 2.0 if chambers == 2 else w
    c2 = CLEAT_MM ** 2
    total = 0.0
    # baffle cleats (floating baffle, the default)
    total += chambers * w_c * c2
    if not slot:
        total += chambers * w_c * c2
    side_len = h - CLEAT_MM - ((slot_h + BAFFLE_MM) if slot else CLEAT_MM)
    total += 2 * side_len * c2
    # back cleats
    total += 2 * chambers * w_c * c2
    if closed:
        total += 2 * (h - 2 * CLEAT_MM) * c2
    else:
        h_p = (1.0 - OPEN_FRACTION[enclosure]) * h / 2.0
        total += 4 * (h_p - CLEAT_MM) * c2
    # center brace, bottom end on the shelf with a slot
    if driver_count == 2 and chambers == 1:
        total += BRACE_MM[0] * BRACE_MM[1] * (h - ((slot_h + BAFFLE_MM) if slot else 0.0))
    # stiffeners
    sw, sd = STIFFENER_MM
    if chambers == 2:
        segs = [w_c, w_c]
    elif driver_count == 2:
        segs = [(w - BRACE_MM[0]) / 2.0] * 2
    else:
        segs = [w]
    top_len = d - 2 * CLEAT_MM
    bot_len = (d - max(shelf, 2 * CLEAT_MM)) if slot else top_len
    for span in segs:
        if span > SPAN_MAX_MM:
            if top_len > 50.0:
                total += sw * sd * top_len
            if bot_len > 50.0:
                total += sw * sd * bot_len
    if closed:
        back_len = h - CLEAT_MM - (CLEAT_MM + JACK_CLEAR_MM + JACK_PLATE_H_MM + CUTOUT_MARGIN_MM)
        if w_c > SPAN_MAX_MM and back_len > 50.0:
            total += chambers * sw * sd * back_len
    side_span = max(slot_h, h - slot_h - BAFFLE_MM) if slot else h
    if side_span > SPAN_MAX_MM:
        total += 2 * sw * sd * top_len
    # slot shelf, end cheeks, center cheeks
    if slot:
        avail = w_c - (count - 1) * PANEL_MM
        cheek = (avail - count * port.slot_w_mm) / 2.0
        inside = max(shelf - BAFFLE_MM, 0.0)      # the shelf's run through the baffle is outside
        per_chamber_parts = w_c * inside * BAFFLE_MM + (count - 1) * PANEL_MM * inside * slot_h
        if cheek > 0.5:
            per_chamber_parts += 2 * cheek * inside * slot_h
        total += chambers * per_chamber_parts
    # round port: tube wall inside the box and the flange ring (the ring is the
    # whole port when the tube would not reach past the back panel)
    if port is not None and port.shape == "round":
        id_mm, length = port.diameter_mm, port.length_mm
        od = next((od for tube, od in PORT_TUBE_OD_MM.items() if abs(tube - id_mm) < 0.05),
                  id_mm + 2 * TUBE_WALL_FALLBACK_MM)
        ring_od = od + FLANGE_RING_EXTRA_MM
        if length > 2 * BACK_MM:
            tube = math.pi / 4.0 * (od ** 2 - id_mm ** 2) * (length - BACK_MM)
            ring = math.pi / 4.0 * (ring_od ** 2 - od ** 2) * FLANGE_RING_T_MM
        else:
            tube = 0.0
            ring = math.pi / 4.0 * (ring_od ** 2 - id_mm ** 2) * max(length - BACK_MM, 0.0)
        total += chambers * count * (tube + ring)
    return total / 1e6
```

`Constraints`:

```python
@dataclass
class Constraints:
    pinned_external_width_mm: float | None = None
    max_external_mm: tuple | None = None
    panel_mm: float = PANEL_MM
    back_mm: float = BACK_MM
    baffle_mm: float = BAFFLE_MM
    recess_mm: float = RECESS_MM
    brace_l: float = 0.0               # extra bracing beyond the modeled mono 2x12 center brace
    port_diameter_mm: float = DEFAULT_PORT_DIAMETER_MM
    port_slot_mm: tuple | None = None
    port_count: int | None = None      # None: one port per driver in the chamber
    line: str = "tolex"
    species: str | None = None
    accept_low_headroom: bool = False

    def __post_init__(self):
        if self.line not in LINES:
            raise ValueError(f"line must be one of {', '.join(LINES)}")
        if self.species is not None:
            self.species = self.species.strip() or None

    def panel_kwargs(self) -> dict:
        return dict(panel_mm=self.panel_mm, back_mm=self.back_mm,
                    baffle_mm=self.baffle_mm, recess_mm=self.recess_mm)
```

`_volumes`:

```python
def _volumes(method, per_driver_net, per_chamber_drivers, chambers, displacement, brace_l,
             port_l_total, divider_l, inside_l, gross_l) -> dict:
    """gross = net + displacement + brace + port (air inside the box) + divider
    + inside_parts; port.volume_l on the port dict is the whole port."""
    chamber_net = per_driver_net * per_chamber_drivers
    return {"method": method, "per_driver_net_l": per_driver_net,
            "per_chamber_net_l": chamber_net, "net_total_l": chamber_net * chambers,
            "displacement_l": displacement, "brace_l": brace_l, "port_l": port_l_total,
            "divider_l": divider_l, "inside_parts_l": inside_l, "gross_l": gross_l}
```

`propose`:

```python
def propose(drivers: list, impedances: list, enclosure: str, tone: dict,
            jack_config: str = "mono", constraints: Constraints | None = None,
            name: str = "cab") -> Voicing:
    c = constraints or Constraints()
    lead, count, chambers, per_chamber_drivers, warnings = _setup(
        drivers, impedances, enclosure, tone, jack_config)
    blockers = []
    low_end = tone["low_end"]
    per_driver_net, method, w = per_driver_net_l(lead, enclosure, low_end)
    warnings.extend(w)
    fb = None
    if enclosure == "closed-ported":
        per_driver_net, fb, _, w = ported_targets(lead, per_driver_net, low_end)
        warnings.extend(w)
    chamber_net = per_driver_net * per_chamber_drivers
    net_total = chamber_net * chambers
    displacement = _displacement(drivers, warnings)
    cutout = max(d.cutout_mm for d in drivers)
    floor_extra = HARDWOOD_FLOOR_EXTRA_MM if c.line == "hardwood" else 0.0
    min_w = min_internal_width_mm(count, cutout) + floor_extra
    pk = c.panel_kwargs()
    port_count = c.port_count or per_chamber_drivers
    net_target = net_total
    port, port_l, divider_l, inside_l, box, limited = None, 0.0, 0.0, 0.0, None, False
    last = None   # (gross, parts) of the previous pass
    for _ in range(10):   # until the box and its parts settle: port, divider, and inside parts
                          # depend on the box, and the net follows them when the size limit wins
        gross = net_total + displacement + c.brace_l + port_l * chambers + divider_l + inside_l
        slot_h = None
        if enclosure == "closed-ported" and c.port_slot_mm:
            slot_h = port.slot_h_mm if port is not None else c.port_slot_mm[1]
        box = dims_for_volume(gross, c.pinned_external_width_mm, min_w, c.max_external_mm,
                              min_internal_height_mm=min_internal_height_mm(cutout, slot_h) + floor_extra,
                              strict=False, **pk)
        w_int, h_int, d_int = box.internal_mm
        divider_l = _divider_l(chambers, h_int, d_int, c)
        if any(w.startswith("cannot reach") for w in box.warnings):
            # The size limit wins: voice the box that fits and present the trade-off.
            box.warnings = [w for w in box.warnings if not w.startswith("cannot reach")]
            limited = True
        if abs(box.gross_l - gross) > 0.001:
            # The net is what the box holds when the limit pins it under the request
            # (dims_for_volume passes a shortfall under 0.1 percent without the warning).
            net_total = (box.gross_l - displacement - c.brace_l - port_l * chambers - divider_l
                         - inside_l)
            chamber_net = net_total / chambers
            per_driver_net = chamber_net / per_chamber_drivers
        if enclosure == "closed-ported":
            port = size_port(_air_speed_driver(lead, per_chamber_drivers / port_count, warnings),
                             chamber_net / port_count, fb, diameter_mm=c.port_diameter_mm,
                             slot_mm=c.port_slot_mm)
            port_l = _port_inside_l(port) * port_count
        inside_l = inside_parts_l(box.internal_mm, enclosure, count, chambers, jack_config, port,
                                  c.line, port_count, panel_mm=c.panel_mm)
        parts = port_l * chambers + divider_l + inside_l
        floor_held = slot_h is None or abs(port.slot_h_mm - slot_h) < 1e-9
        if (last is not None and floor_held and abs(box.gross_l - last[0]) < 0.001
                and abs(parts - last[1]) < 0.001):
            break
        last = (box.gross_l, parts)
    warnings.extend(box.warnings)
    chamber_w = _chamber_w(chambers, w_int, c)
    port_dict = None
    if port is not None:
        fb_actual, port_dict = _port_report(lead, per_chamber_drivers, chamber_net, port,
                                            port_count, warnings)
        if abs(fb_actual - fb) > 0.5:
            warnings.append(f"port clamped at the size cap: tuned {fb_actual:.1f} Hz, target "
                            f"{fb:.1f} Hz; lower Fb or use a smaller box")
        fb = fb_actual   # the prediction follows the port as built
    prediction = _predict(lead, enclosure, per_driver_net, fb, chamber_w, h_int, d_int)
    if limited:
        target_gross = (net_target + displacement + c.brace_l + port_l * chambers + divider_l
                        + inside_l)
        blockers.append(f"target {target_gross:.1f} L cannot fit the size limit; achievable "
                        f"{box.gross_l:.1f} L gives {_prediction_summary(prediction)}")
    wiring_dict, power_dict = _electrical(drivers, impedances, tone, jack_config, c,
                                          warnings, blockers)
    volumes = _volumes(method, per_driver_net, per_chamber_drivers, chambers, displacement,
                       c.brace_l, port_l * chambers, divider_l, inside_l, box.gross_l)
    return _assemble(name, "propose", tone, drivers, impedances, enclosure, jack_config, chambers,
                     count, volumes, box, chamber_w, port_dict, prediction, wiring_dict,
                     power_dict, warnings, blockers, c)
```

`evaluate`:

```python
def evaluate(drivers: list, impedances: list, enclosure: str, tone: dict,
             internal_mm: tuple, jack_config: str = "mono", port: Port | None = None,
             constraints: Constraints | None = None, name: str = "cab") -> Voicing:
    """Voicing of an existing box. A supplied port is one of constraints.port_count
    identical ports per chamber (default one per driver, as in propose)."""
    c = constraints or Constraints()
    lead, count, chambers, per_chamber_drivers, warnings = _setup(
        drivers, impedances, enclosure, tone, jack_config)
    if enclosure == "closed-ported" and port is None:
        raise ValueError("closed-ported evaluate needs a port (from port_dims) with its length")
    if enclosure != "closed-ported" and port is not None:
        raise ValueError(f"a port does not apply to a {enclosure} enclosure")
    blockers = []
    box = make_box(tuple(internal_mm), **c.panel_kwargs())
    warnings.extend(box.warnings)
    w_int, h_int, d_int = box.internal_mm
    divider_l = _divider_l(chambers, h_int, d_int, c)
    displacement = _displacement(drivers, warnings)
    port_count = c.port_count or per_chamber_drivers
    port_l = 0.0
    if port is not None:
        port_l = _port_inside_l(port) * port_count
    inside_l = inside_parts_l(box.internal_mm, enclosure, count, chambers, jack_config, port,
                              c.line, port_count, panel_mm=c.panel_mm)
    net_total = (box.gross_l - displacement - c.brace_l - port_l * chambers - divider_l
                 - inside_l)
    if net_total <= 0:
        raise ValueError("box has no net volume left after displacement, brace, port, divider, "
                         "and inside parts")
    chamber_net = net_total / chambers
    per_driver_net = chamber_net / per_chamber_drivers
    chamber_w = _chamber_w(chambers, w_int, c)
    fb, port_dict = None, None
    if enclosure == "closed-ported":
        fb, port_dict = _port_report(lead, per_chamber_drivers, chamber_net, port, port_count,
                                     warnings)
    if not lead.has_ts() and enclosure in ("closed", "closed-ported"):
        detail = "tuning reported, " if enclosure == "closed-ported" else ""
        warnings.append(f"{lead.slug}: no Thiele-Small data ({lead.data_status}); "
                        f"{detail}no response prediction")
    prediction = _predict(lead, enclosure, per_driver_net, fb, chamber_w, h_int, d_int)
    wiring_dict, power_dict = _electrical(drivers, impedances, tone, jack_config, c,
                                          warnings, blockers)
    volumes = _volumes("evaluate", per_driver_net, per_chamber_drivers, chambers, displacement,
                       c.brace_l, port_l * chambers, divider_l, inside_l, box.gross_l)
    return _assemble(name, "evaluate", tone, drivers, impedances, enclosure, jack_config, chambers,
                     count, volumes, box, chamber_w, port_dict, prediction, wiring_dict,
                     power_dict, warnings, blockers, c)
```

`render_markdown` (two rows in the Volumes table: replace the `| Port |` line and add the inside parts row after `| Divider |`):

```python
        f"| Port air inside the box | {vol['port_l']:.2f} L |",
        f"| Divider | {vol['divider_l']:.2f} L |",
        f"| Inside parts (cleats, stiffeners, shelf, ring) | {vol['inside_parts_l']:.2f} L |",
```

`_build_parser`:

```python
def _build_parser():
    import argparse
    ap = argparse.ArgumentParser(description="Guitar speaker cabinet voicing engine")
    sub = ap.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--speakers-dir", default=str(SPEAKERS_DIR))
        p.add_argument("--speaker", action="append", required=True, help="slug, repeat for two drivers")
        p.add_argument("--impedance", action="append", type=float, required=True)
        p.add_argument("--enclosure", choices=ENCLOSURE_TYPES, required=True)
        p.add_argument("--tone", required=True, help="tone target JSON file")
        p.add_argument("--jack", choices=JACK_CONFIGS, default="mono")
        p.add_argument("--brace-l", type=float, default=0.0,
                       help="liters of extra bracing beyond the modeled mono 2x12 center brace, "
                            "which the inside parts already carry")
        p.add_argument("--line", choices=LINES, default="tolex")
        p.add_argument("--species", default=None)
        p.add_argument("--accept-low-headroom", action="store_true")
        p.add_argument("--name", default="cab")
        p.add_argument("--out", required=True, help="directory for voicing.json and voicing.md")

    pp = sub.add_parser("propose")
    common(pp)
    pp.add_argument("--pinned-width", type=float, help="external width mm")
    pp.add_argument("--max-external", type=float, nargs=3, metavar=("W", "H", "D"))
    pp.add_argument("--port-diameter", type=float, default=DEFAULT_PORT_DIAMETER_MM,
                    help="round port start in mm, snapped up to the tube table")
    pp.add_argument("--port-slot", type=float, nargs=2, metavar=("W", "H"))

    pe = sub.add_parser("evaluate")
    common(pe)
    pe.add_argument("--internal", type=float, nargs=3, required=True, metavar=("W", "H", "D"))
    pe.add_argument("--port-diameter", type=float)
    pe.add_argument("--port-slot", type=float, nargs=2, metavar=("W", "H"))
    pe.add_argument("--port-length", type=float)

    pl = sub.add_parser("list")
    pl.add_argument("--speakers-dir", default=str(SPEAKERS_DIR))
    return ap
```


- [ ] **Step 4: Run the tests (calibration test still fails)**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q`
Expected: 396 passed, 1 failed (`test_calibration_table_matches_engine`, the note still holds the Plan 1 table).

- [ ] **Step 5: Regenerate the calibration table**

Run from the vault root: `.venv/bin/python projects/Speaker-cab-system/pipeline/calibration_table.py`
Expected: `wrote 20 rows to .../knowledge/speaker-cab-voicing.md`. Every row changes against Plan 1: the site box net drops from 44.1 (43.6, 43.4 on the Eminence rows) to 42.5 (42.0, 41.8) L with the inside parts deducted, every closed Qtc rises by about 0.006 to 0.01 and three closed F3 values by 1 Hz, the Heritage G12H(55) closed character moves from lean to tight (Qtc 0.599 to 0.605 across the 0.6 threshold), and the Eminence Red White and Blues notes read "port too short (6.5 mm)" and "tuned 74.4 Hz" (its clamped port now stops at the 153.2 mm tube). Proposed ported net and Fb columns are unchanged. The section must read (the date is the run date):

```markdown
## Calibration table

Calibration table, every number prediction_status "unverified, ears only". Generated 2026-09-10 with `evaluate` (closed, site box 472 x 421.2 x 229.4 mm internal) and `propose` (closed-ported, low_end balanced), 16 ohm where the note lists it (voiced with the note's 8 ohm T/S set, see Model limits), amp 40 W.

| Speaker | Data | Net L in site box | Closed Qtc | Closed character | Closed F3 Hz | Proposed ported net L | Fb Hz | Ported character | Notes |
|---|---|---|---|---|---|---|---|---|---|
| [[celestion-blue]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) | speaker handling 15 W is below the amp's 40 W |
| [[celestion-cream]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12-65-heritage]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 68 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12h-30-anniversary]] | analog | 42.5 | 0.755 | tight | 105 | 30.0 | 68 | punchy | speaker handling 30 W is below the amp's 40 W; celestion-g12h-30-anniversary: Thiele-Small volume 29.5 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L |
| [[celestion-g12h-75-creamback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12m-25-greenback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) | speaker handling 25 W is below the amp's 40 W |
| [[celestion-g12m-65-creamback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-gold]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-heritage-g12h55]] | third-party | 42.5 | 0.605 | tight | 109 | 68.0 | 45 | flat | speaker handling 30 W is below the amp's 40 W; celestion-heritage-g12h55: Thiele-Small volume 71.3 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 68.0 L |
| [[celestion-vintage-30]] | analog | 42.5 | 0.701 | tight | 105 | 37.9 | 60 | flat |  |
| [[eminence-cannabis-rex]] | datasheet | 42.0 | 0.924 | balanced | 115 | 45.5 | 77 | punchy |  |
| [[eminence-red-white-and-blues]] | datasheet | 42.0 | 1.040 | big | 114 | 66.0 | 74 | punchy | port too short (6.5 mm) for Fb 78 Hz in 66.0 L; clamped to 20 mm, reduce port area or lower Fb; port clamped at the size cap: tuned 74.4 Hz, target 78.0 Hz; lower Fb or use a smaller box |
| [[eminence-swamp-thang]] | datasheet | 41.8 | 0.747 | tight | 131 | 41.3 | 78 | flat |  |
| [[eminence-texas-heat]] | datasheet | 42.0 | 0.967 | balanced | 95 | 50.9 | 63 | punchy |  |
| [[eminence-tonker]] | datasheet | 41.8 | 0.633 | tight | 138 | 34.1 | 71 | flat |  |
| [[jensen-c12n]] | datasheet | 42.5 | 1.262 | peaky | 102 | 64.3 | 45 | boomy | jensen-c12n: Thiele-Small volume 22.6 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L; ported alignment stays boomy at the practical limits; consider a closed back or a lower-Qts driver |
| [[jensen-p12n]] | datasheet | 42.5 | 1.037 | big | 95 | 67.4 | 62 | punchy |  |
| [[wgs-et65]] | estimated | 42.5 | 1.235 | peaky | 98 | 63.4 | 49 | punchy |  |
| [[wgs-green-beret]] | estimated | 42.5 | 1.454 | peaky | 109 | 64.3 | 45 | boomy | speaker handling 25 W is below the amp's 40 W; wgs-green-beret: Thiele-Small volume 22.0 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L; ported alignment stays boomy at the practical limits; consider a closed back or a lower-Qts driver |
| [[wgs-veteran-30]] | estimated | 42.5 | 1.023 | big | 103 | 62.5 | 71 | punchy |  |
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q`
Expected: 397 passed.

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cabvoice.py scripts/test_cabvoice.py knowledge/speaker-cab-voicing.md
git commit -m "Speaker cab plan 2 task 2: port tube table, shell margins, height floor"
```
<!-- /include -->

---

<!-- include: .vault/plan/task3.md -->
### Task 3: Cut list emitter: materials not cut

**Files:**
- Modify: `scripts/cutlist.py` (`write_cut_list`)
- Create: `scripts/test_cutlist.py`
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan2-mirror/.vault/scripts/cutlist.py`, `.vault/scripts/test_cutlist.py`

**Interfaces:**
- Consumes: the Plan 1 emitter (`write_cut_list(parts, md_path, csv_path=None, title="Cut list")`, `cut_list_rows`, `_measure` which already prefers a part's `dims` over its `solid`).
- Produces: `write_cut_list(parts, md_path, csv_path=None, title="Cut list", extra_lines=None)`; `extra_lines` is a list of `{"part": str, "qty": float, "unit": str, "material": str, "notes": str}`; each entry becomes a bullet under a `## Materials not cut` section after the totals and one CSV row `[qty, part, "", "", "", material, notes]`. Task 11 (`cabmodel.export`) passes the tolex yardage line this way. Nothing else in the emitter changes, so the furniture models keep their output.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_cutlist.py`:

```python
"""Tests for the cut list emitter (dims-based parts, no CAD needed)."""
import csv

import cutlist

PARTS = [
    {"name": "side_left", "dims": (18.0, 279.4, 457.2), "qty": 1, "material": "baltic birch 18 mm",
     "notes": "finger joint"},
    {"name": "side_right", "dims": (18.0, 279.4, 457.2), "qty": 1, "material": "baltic birch 18 mm",
     "notes": "finger joint"},
    {"name": "back", "dims": (12.0, 421.2, 472.0), "qty": 1, "material": "baltic birch 12 mm"},
]
TOLEX = [{"part": "tolex wrap", "qty": 1.9, "unit": "yd", "material": "British Style Red, 54 in roll",
          "notes": "six external faces x 1.15 for wrap and waste"}]


def test_dims_parts_merge_and_sort(tmp_path):
    rows = cutlist.write_cut_list(PARTS, tmp_path / "cut.md")
    assert [(r["name"], r["qty"]) for r in rows] == [("back", 1), ("side_left/side_right", 2)]
    text = (tmp_path / "cut.md").read_text()
    assert "| 2 | side_left/side_right | 18 x 279.4 x 457.2 |" in text
    assert "## Totals by material" in text
    assert "## Materials not cut" not in text


def test_extra_lines_in_markdown_and_csv(tmp_path):
    cutlist.write_cut_list(PARTS, tmp_path / "cut.md", csv_path=tmp_path / "cut.csv",
                           title="site-default", extra_lines=TOLEX)
    text = (tmp_path / "cut.md").read_text()
    assert text.index("## Materials not cut") > text.index("## Totals by material")
    assert ("- 1.9 yd tolex wrap: British Style Red, 54 in roll. "
            "six external faces x 1.15 for wrap and waste") in text
    with open(tmp_path / "cut.csv", newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["qty", "part", "thickness_mm", "width_mm", "length_mm", "material", "notes"]
    assert rows[-1] == ["1.9", "tolex wrap", "", "", "", "British Style Red, 54 in roll",
                        "six external faces x 1.15 for wrap and waste"]
    assert len(rows) == 1 + 2 + 1


def test_no_extra_section_when_none(tmp_path):
    cutlist.write_cut_list(PARTS, tmp_path / "cut.md", csv_path=tmp_path / "cut.csv", extra_lines=None)
    assert "Materials not cut" not in (tmp_path / "cut.md").read_text()
    with open(tmp_path / "cut.csv", newline="") as f:
        assert len(list(csv.reader(f))) == 3
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cutlist.py -q`
Expected: 2 failed (`extra_lines` is not an argument), 1 passed.

- [ ] **Step 3: Implement**

In `scripts/cutlist.py` replace `write_cut_list` with:

```python
def write_cut_list(parts, md_path, csv_path=None, title="Cut list", extra_lines=None):
    """Write the cut list markdown (and optional CSV); return the rows.

    extra_lines: optional materials that are not cut parts (tolex yardage,
    grill cloth), each {"part", "qty", "unit", "material", "notes"}; they
    appear under "Materials not cut" in the markdown and as CSV rows with
    empty dimensions."""
    rows = cut_list_rows(parts)
    lines = ["---", "type: cutlist", f"project: {title}", "---", "",
             f"# Cut list - {title}", "",
             "| Qty | Part | T x W x L (mm) | T x W x L (in) | Material | Notes |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        mm = f"{_fmt(r['t'])} x {_fmt(r['w'])} x {_fmt(r['l'])}"
        inch = f"{inch_frac(r['t'])} x {inch_frac(r['w'])} x {inch_frac(r['l'])}"
        lines.append(f"| {r['qty']} | {r['name']} | {mm} | {inch} "
                     f"| {r['material']} | {r['notes']} |")
    lines += ["", "Inches rounded to the nearest 1/16.", "",
              "## Totals by material", ""]
    totals = {}
    for r in rows:
        mat = r["material"] or "(unspecified)"
        qty, area = totals.get(mat, (0, 0.0))
        totals[mat] = (qty + r["qty"], area + r["qty"] * r["w"] * r["l"] / 1e6)
    for mat, (qty, area) in sorted(totals.items()):
        unit = "part" if qty == 1 else "parts"
        lines.append(f"- {mat}: {qty} {unit}, {area:.2f} m2 face area "
                     "(no kerf/waste allowance)")
    if extra_lines:
        lines += ["", "## Materials not cut", ""]
        for x in extra_lines:
            lines.append(f"- {x['qty']:g} {x['unit']} {x['part']}: {x['material']}. {x['notes']}")
    with open(md_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    if csv_path:
        with open(csv_path, "w", newline="") as f:
            writer = _csv.writer(f)
            writer.writerow(["qty", "part", "thickness_mm", "width_mm",
                             "length_mm", "material", "notes"])
            for r in rows:
                writer.writerow([r["qty"], r["name"], _fmt(r["t"]), _fmt(r["w"]),
                                 _fmt(r["l"]), r["material"], r["notes"]])
            for x in extra_lines or ():
                writer.writerow([x["qty"], x["part"], "", "", "", x["material"], x["notes"]])
    return rows
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cutlist.py -q`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cutlist.py scripts/test_cutlist.py
git commit -m "Speaker cab plan 2 task 3: cut list materials-not-cut lines"
```
<!-- /include -->

---

### Task 4: Layout kernel, part 1: constants, dataclasses, sheet loading, joinery schedules, shell blanks

**Files:**
- Create: `scripts/cablayout.py`
- Create: `scripts/test_cablayout.py`

**Interfaces:**
- Consumes: `scripts/cabvoice.py` constants `MM_PER_INCH`, `BAFFLE_MM`, `BACK_MM`, `RECESS_MM` (Task 2 state) and a voicing dict shaped like `Voicing.to_dict()` with the Task 1 speaker fields.
- Produces: the constants in Global Constraints; dataclasses `Aesthetics` (with `validate() -> list[str]`), `Speaker`, `PortSpec`, `CabSpec` (property `shell_mm`), `Blank`, `Cutout`, `RoundPort`, `SlotPort`, `Hardware`, `Envelope`, `Chamber`, `Check`, `Layout`; functions `species_density(name) -> float | None`, `load_voicing(path) -> dict`, `order_from(voicing, aesthetics) -> CabSpec`, `finger_schedule(depth_mm, thickness_mm, width_hint_mm) -> (count, width)`, `dovetail_schedule(depth_mm, t_top_mm, pin_mm, tail_target_mm, slope) -> dict`, `shell_blanks(spec) -> list[Blank]`. The feature vocabulary on `Blank.features`: `edge_cuts` (x range plus YZ quads), `cutout`, `holes`, `rect_hole` (axis y or x), `notch` (box).

The shell is four blanks: sides t x D x H at x = +-(W/2 - t), top and bottom t x D x W. The four corner blocks are shared; the side's `edge_cuts` and the top's `edge_cuts` over a block are exact complements, which the tests prove by summing the removed areas. A sheet with blockers, a missing key, a dovetail on the tolex line, or invalid aesthetics raises `ValueError` from `order_from`; nothing parses warning text.

- [ ] **Step 1: Write the failing tests**

<!-- code: test_cablayout.py unit 4 -->
```python
"""Tests for cablayout.py (Plan 2 Tasks 4 to 7). Run from the mirror root:
.venv/bin/python -m pytest test_cablayout.py -q"""
import copy
import json
import math
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
SCRIPTS = HERE.parents[3] / "scripts"
if not (HERE / "cabvoice.py").exists() and str(SCRIPTS) not in sys.path:
    sys.path.insert(1, str(SCRIPTS))

import cabvoice  # noqa: E402
import cablayout as L  # noqa: E402

# === TASK 4 ===
SPEAKER = {"slug": "celestion-g12h-30-anniversary", "cutout_mm": 283, "bolt_circle_mm": 297,
           "bolt_count": 4, "depth_mm": 135, "weight_kg": 4.7, "displacement_l": 1.5,
           "frame_diameter_mm": 309, "magnet_diameter_mm": 156, "magnet_diameter_estimated": False}


def sheet(external=(508.0, 457.2, 279.4), enclosure="closed-ported", drivers=1, chambers=1,
          jack="mono", line="tolex", species=None, port=None, net=43.5, open_fraction=None):
    W, H, D = external
    internal = [W - 36.0, H - 36.0, D - 50.0]
    if port == "round":
        port = {"shape": "round", "diameter_mm": 77.3, "slot_w_mm": None, "slot_h_mm": None,
                "length_mm": 40.0, "location": "rear", "count": drivers // chambers}
    elif port == "slot":
        port = {"shape": "slot", "diameter_mm": None, "slot_w_mm": 300.0, "slot_h_mm": 40.0,
                "length_mm": 60.0, "location": "front", "count": drivers // chambers}
    return {"name": "test", "blockers": [], "prediction_status": "unverified, ears only",
            "enclosure": {"type": enclosure, "driver_count": drivers, "chambers": chambers,
                          "jack_config": jack, "open_fraction": open_fraction},
            "box": {"external_mm": list(external), "internal_mm": internal},
            "construction": {"panel_mm": 18.0, "back_mm": 12.0, "baffle_mm": 18.0, "recess_mm": 20.0,
                             "line": line, "species": species,
                             "wall_material": "baltic birch plywood" if line == "tolex" else species},
            "volumes": {"net_total_l": net, "per_chamber_net_l": net / chambers},
            "speakers": [dict(SPEAKER) for _ in range(drivers)], "port": port}


def spec_for(**kw):
    aest = kw.pop("aesthetics", None) or L.Aesthetics()
    return L.order_from(sheet(**kw), aest)


def test_constants_match_engine():
    assert L.RECESS_MM == cabvoice.RECESS_MM == 20.0
    assert L.BAFFLE_MM == cabvoice.BAFFLE_MM == 18.0
    assert L.BACK_MM == cabvoice.BACK_MM == 12.0
    assert L.CUTOUT_MARGIN_MM == cabvoice.CUTOUT_MARGIN_MM == 25.0
    assert L.MM_PER_INCH == cabvoice.MM_PER_INCH == 25.4
    assert L.SHELL_MARGIN_MM == 44.0 and L.CUTOUT_GAP_MM == 68.0
    assert set(L.PORT_TUBE_OD_MM) == {52.0, 77.3, 101.5, 153.2}


def test_finger_schedule_is_odd_with_full_ends():
    n, w = L.finger_schedule(279.4, 18.0)
    assert n == 31 and abs(w - 9.013) < 0.01
    assert L.finger_schedule(279.4, 18.0, 18.0)[0] == 15
    assert L.finger_schedule(20.0, 18.0)[0] == 3
    for depth in (100.0, 250.0, 300.0, 333.3):
        n, w = L.finger_schedule(depth, 19.0)
        assert n % 2 == 1 and abs(n * w - depth) < 1e-9


def test_finger_polys_tile_the_corner_block():
    n = 31
    side = L._finger_polys(279.4, n, 457.2, 439.2, True)
    top = L._finger_polys(279.4, n, 457.2, 439.2, False)
    assert len(side) == 16 and len(top) == 15
    spans = sorted([(p[0][0], p[1][0]) for p in side + top])
    assert abs(spans[0][0]) < 1e-9 and abs(spans[-1][1] - 279.4) < 1e-9
    for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
        assert abs(a1 - b0) < 1e-9
    assert side[0][0][0] == 0.0          # the side gives up the front segment
    assert all(p[0][1] == 457.2 and p[2][1] == 439.2 for p in side)


def test_dovetail_schedule_widths_and_tiling():
    s = L.dovetail_schedule(279.4, 19.0, 9.5, 30.0, 8.0)
    assert s["count"] == 7 and abs(s["tail_w"] - 29.057) < 0.01 and abs(s["flare"] - 2.375) < 1e-9
    assert len(s["pins"]) == 6 and s["half_pins"] == [(0.0, 9.5), (269.9, 279.4)]
    covered = [s["half_pins"][0]] + [x for pair in zip(s["tails"], s["pins"] + [None]) for x in pair if x] + [s["half_pins"][1]]
    for (a0, a1), (b0, b1) in zip(covered, covered[1:]):
        assert abs(a1 - b0) < 1e-9
    with pytest.raises(ValueError):
        L.dovetail_schedule(30.0, 19.0, 9.5, 30.0, 8.0)


def test_dovetail_polys_are_complements_at_both_faces():
    s = L.dovetail_schedule(279.4, 19.0, 9.5, 30.0, 8.0)
    side = L._dovetail_polys(s, 279.4, 457.2, 438.2, "tails")
    top = L._dovetail_polys(s, 279.4, 457.2, 438.2, "pins")
    for z in (457.2, 438.2):
        spans = []
        for poly in side + top:
            ys = [y for (y, zz) in poly if abs(zz - z) < 1e-9]
            spans.append((min(ys), max(ys)))
        spans.sort()
        assert abs(spans[0][0]) < 1e-9 and abs(spans[-1][1] - 279.4) < 1e-9
        for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
            assert abs(a1 - b0) < 1e-9, (z, a1, b0)
    # pins narrow at the outer face, wide at the shoulder
    pin = side[1]
    assert (pin[1][0] - pin[0][0]) < (pin[2][0] - pin[3][0])


def test_species_density_aliases():
    assert L.species_density("Walnut") == 610.0
    assert L.species_density("Black Cherry") == 560.0
    assert L.species_density("hard maple") == 705.0 and L.species_density("Sapele") == 670.0
    assert L.species_density("oak") is None and L.species_density(None) is None


def test_aesthetics_validate():
    assert L.Aesthetics().validate() == []
    bad = L.Aesthetics(corner_joint="miter", baffle_mount="glued", handle="none", corners="gold",
                       feet="casters", tolex_roll_in=48, finger_width_mm=-1.0,
                       jack_plate_cutout_mm=(110.0,))
    errors = bad.validate()
    assert len(errors) == 8


def test_order_from_errors():
    good = sheet(port="round")
    with pytest.raises(ValueError, match="blockers"):
        L.order_from({**good, "blockers": ["power stop"]}, L.Aesthetics())
    missing = copy.deepcopy(good)
    del missing["speakers"][0]["frame_diameter_mm"]
    with pytest.raises(ValueError, match="frame_diameter_mm"):
        L.order_from(missing, L.Aesthetics())
    with pytest.raises(ValueError, match="hardwood"):
        L.order_from(good, L.Aesthetics(corner_joint="dovetail"))
    with pytest.raises(ValueError, match="aesthetics"):
        L.order_from(good, L.Aesthetics(handle="rope"))
    two = sheet(drivers=2)
    two["speakers"] = two["speakers"][:1]
    with pytest.raises(ValueError, match="speaker entries"):
        L.order_from(two, L.Aesthetics())
    spec = L.order_from(good, L.Aesthetics())
    assert spec.shell_mm == 18.0 and spec.port.count == 1 and spec.closed


def test_order_from_port_missing_key_is_a_value_error():
    bad = sheet(port="round")
    del bad["port"]["count"]
    with pytest.raises(ValueError, match="count"):
        L.order_from(bad, L.Aesthetics())


def test_shell_blanks_tolex_and_hardwood():
    parts = L.shell_blanks(spec_for())
    assert [p.name for p in parts] == ["side_left", "side_right", "top", "bottom"]
    side, top = parts[0], parts[2]
    assert side.blank_mm == (18.0, 457.2, 279.4) and top.blank_mm == (18.0, 508.0, 279.4)
    assert side.pos == (-254.0, 0.0, 0.0) and side.size == (18.0, 279.4, 457.2)
    assert top.pos == (-254.0, 0.0, 439.2) and top.size == (508.0, 279.4, 18.0)
    assert "31 fingers of 9.0 mm" in side.notes and "grain" not in side.notes
    assert side.features[0]["x"] == (-254.0, -236.0) and top.features[1]["x"] == (236.0, 254.0)
    hw = L.shell_blanks(spec_for(line="hardwood", species="walnut",
                                 aesthetics=L.Aesthetics(corner_joint="dovetail")))
    assert hw[0].material == "black walnut 19 mm" and hw[0].density == 610.0
    assert hw[0].blank_mm[0] == 19.0 and "through dovetail" in hw[0].notes
    assert L.HARDWOOD_GRAIN_NOTE in hw[0].notes
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest scripts/test_cablayout.py -q`
Expected: collection error, `ModuleNotFoundError: No module named 'cablayout'`

- [ ] **Step 3: Implement**

Create `scripts/cablayout.py` with exactly this content:

<!-- code: cablayout.py unit 4 -->
```python
"""cablayout.py: numeric layout kernel for MaximoCabs guitar speaker cabinets.

Reads an approved voicing.json (scripts/cabvoice.py output) plus an
aesthetics block and computes every part blank with its position, joinery
schedule, cutouts, ports, hardware positions, speaker envelopes, chamber
volumes, mass, center of mass, and tolex yardage. No CAD here:
scripts/cabmodel.py builds build123d solids from the Layout this returns.

Coordinate frame: X width centered at 0, Y depth with the external front
face at 0 and positive toward the back, Z height with the floor at 0.
Dimension tuples copied from voicing.json are (width, height, depth);
blank positions and sizes are (x, y, z) in the cab frame.

Every number below is a starting value recorded in
knowledge/speaker-cab-construction.md unless the design marks it locked.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import cabvoice  # noqa: E402  (sibling module: constants and port_dims)

# === TASK 4 ===
MM_PER_INCH = 25.4
PANEL_MM = {"tolex": 18.0, "hardwood": 19.0}   # shell thickness per line
BACK_MM = 12.0
BAFFLE_MM = 18.0
RECESS_MM = 20.0          # baffle front face behind the front edge (locked)
CLEAT_MM = 18.0
GRILL_STRIP_T_MM = 12.0
GRILL_STRIP_W_MM = 40.0
GRILL_CLEARANCE_MM = 2.0
FLANGE_T_MM = 5.0
SPACER_MM = 5.0
SHELL_MARGIN_MM = 44.0    # cutout edge to shell inner face
CUTOUT_MARGIN_MM = 25.0   # cutout edge to brace or divider
CUTOUT_GAP_MM = 68.0      # between the two cutouts of a 2x12 (18 + 2 x 25)
BRACE_MM = (18.0, 60.0)
DIVIDER_MM = 18.0
STIFFENER_MM = (18.0, 40.0)
SPAN_MAX_MM = 450.0
BOLT_HOLE_MM = 6.5
DADO_MM = 6.0
BASKET_LEN_MM = 100.0
COVER_MM = 12.0
GENERIC_MAGNET_MM = 185.0
CLEARANCE_MM = 25.0
HARDWARE_KG = 1.0
TOLEX_WASTE = 1.15
ROLL_MM = {54: 1371.6, 32: 812.8}
STOCK_SHEET_MM = (2440.0, 1220.0)
STOCK_HARDWOOD_MM = (3050.0, 600.0)
FLANGE_RING_T_MM = 12.0
FLANGE_RING_EXTRA_MM = 60.0
BIRCH_DENSITY = 680.0
PVC_DENSITY = 1400.0
SPECIES_DENSITY = {"black walnut": 610.0, "black cherry": 560.0,
                   "hard maple": 705.0, "sapele": 670.0}
PORT_TUBE_OD_MM = {52.0: 60.3, 77.3: 88.9, 101.5: 114.3, 153.2: 168.3}
PORT_TUBE_NOMINAL = {52.0: "2 in", 77.3: "3 in", 101.5: "4 in", 153.2: "6 in"}
TUBE_WALL_FALLBACK_MM = 5.5
JACK_CLEAR_MM = 25.0
BAFFLE_CLEARANCE_MM = 1.0     # floating baffle side clearance
BRACE_SETBACK_MM = 2.0        # brace front face behind the baffle back face
FOOT_DEFAULT_INSET_MM = 32.0
GRILL_FRONT_MM = 3.0          # grill frame face behind the front edge
YARD_M = 0.9144

assert RECESS_MM == cabvoice.RECESS_MM
assert BAFFLE_MM == cabvoice.BAFFLE_MM
assert BACK_MM == cabvoice.BACK_MM
assert CUTOUT_MARGIN_MM == cabvoice.CUTOUT_MARGIN_MM
assert MM_PER_INCH == cabvoice.MM_PER_INCH

JOINTS = ("finger", "dovetail")
BAFFLE_MOUNTS = ("floating", "fixed")
HANDLES = ("strap", "recessed-side")
CORNERS = ("black", "chrome", "none")
FEET = ("rubber", "tilt-back")


@dataclass
class Aesthetics:
    corner_joint: str = "finger"
    finger_width_mm: float | None = None
    dovetail_slope: float = 8.0
    dovetail_pin_mm: float | None = None
    dovetail_tail_mm: float = 30.0
    baffle_mount: str = "floating"
    handle: str = "strap"
    handle_screw_spacing_mm: float = 228.6
    recessed_handle_cutout_mm: tuple = (140.0, 90.0)
    jack_plate_cutout_mm: tuple = (110.0, 70.0)
    corners: str | None = None
    corner_allowance_mm: float = 50.0
    piping: bool = False
    feet: str = "rubber"
    foot_diameter_mm: float = 40.0
    foot_inset_mm: float = 32.0
    tolex_roll_in: int = 54
    head_width_mm: float | None = None
    tolex_color: str = ""
    grill_cloth: str = ""
    finish: str = ""

    def validate(self) -> list:
        errors = []
        if self.corner_joint not in JOINTS:
            errors.append(f"corner_joint must be one of {', '.join(JOINTS)}")
        if self.baffle_mount not in BAFFLE_MOUNTS:
            errors.append(f"baffle_mount must be one of {', '.join(BAFFLE_MOUNTS)}")
        if self.handle not in HANDLES:
            errors.append(f"handle must be one of {', '.join(HANDLES)}")
        if self.corners is not None and self.corners not in CORNERS:
            errors.append(f"corners must be one of {', '.join(CORNERS)}")
        if self.feet not in FEET:
            errors.append(f"feet must be one of {', '.join(FEET)}")
        if self.tolex_roll_in not in ROLL_MM:
            errors.append("tolex_roll_in must be 54 or 32")
        for name in ("finger_width_mm", "dovetail_pin_mm", "head_width_mm"):
            v = getattr(self, name)
            if v is not None and not v > 0:
                errors.append(f"{name} must be positive or None")
        for name in ("dovetail_slope", "dovetail_tail_mm", "handle_screw_spacing_mm",
                     "foot_diameter_mm"):
            if not getattr(self, name) > 0:
                errors.append(f"{name} must be positive")
        for name in ("corner_allowance_mm", "foot_inset_mm"):
            if getattr(self, name) < 0:
                errors.append(f"{name} must not be negative")
        for name in ("recessed_handle_cutout_mm", "jack_plate_cutout_mm"):
            v = getattr(self, name)
            if len(v) != 2 or not all(x > 0 for x in v):
                errors.append(f"{name} must be (width, height) in mm, both positive")
        return errors


@dataclass
class Speaker:
    slug: str
    cutout_mm: float
    bolt_circle_mm: float
    bolt_count: int
    depth_mm: float
    weight_kg: float
    displacement_l: float
    frame_diameter_mm: float
    magnet_diameter_mm: float | None
    magnet_diameter_estimated: bool


@dataclass
class PortSpec:
    shape: str
    diameter_mm: float | None
    slot_w_mm: float | None
    slot_h_mm: float | None
    length_mm: float
    location: str
    count: int


@dataclass
class CabSpec:
    name: str
    line: str
    species: str | None
    wall_material: str
    external_mm: tuple
    internal_mm: tuple
    panel_mm: float
    back_mm: float
    baffle_mm: float
    recess_mm: float
    enclosure_type: str
    driver_count: int
    chambers: int
    jack_config: str
    open_fraction: float | None
    speakers: list
    port: PortSpec | None
    net_total_l: float
    per_chamber_net_l: float
    prediction_status: str
    aesthetics: Aesthetics
    sheet_inside_parts_l: float | None = None   # the sheet's allowance for cleats, stiffeners, shelf, ring

    @property
    def shell_mm(self) -> float:
        return PANEL_MM[self.line]

    @property
    def closed(self) -> bool:
        return self.enclosure_type in ("closed", "closed-ported")


@dataclass
class Blank:
    name: str
    qty: int
    material: str
    density: float
    shape: str = "box"
    pos: tuple = (0.0, 0.0, 0.0)
    size: tuple = (0.0, 0.0, 0.0)
    blank_mm: tuple = (0.0, 0.0, 0.0)
    features: list = field(default_factory=list)
    notes: str = ""
    chamber: int | None = None
    length_axis: str | None = None

    @property
    def box(self) -> tuple:
        """((x0, y0, z0), (x1, y1, z1)) for box blanks; the enclosing box for tubes."""
        if self.shape == "box":
            x0, y0, z0 = self.pos
            dx, dy, dz = self.size
            return ((x0, y0, z0), (x0 + dx, y0 + dy, z0 + dz))
        cx, y0, cz = self.pos
        od, length, _ = self.size
        r = od / 2.0
        return ((cx - r, y0, cz - r), (cx + r, y0 + length, cz + r))


@dataclass
class Cutout:
    speaker: int
    chamber: int
    center: tuple
    diameter: float
    bolt_circle: float
    bolt_count: int
    bolt_centers: list


@dataclass
class RoundPort:
    chamber: int
    center: tuple
    id_mm: float
    od_mm: float
    length_mm: float
    ring_od_mm: float
    y0: float
    y1: float


@dataclass
class SlotPort:
    chamber: int
    x0: float
    x1: float
    slot_h_mm: float
    shelf_depth_mm: float
    cheek_w_mm: float


@dataclass
class Hardware:
    item: str
    position: tuple
    cutout: tuple | None
    panel: str
    notes: str


@dataclass
class Envelope:
    speaker: int
    chamber: int
    center: tuple
    y0: float
    basket_d: float
    basket_len: float
    magnet_d: float
    magnet_len: float
    flange_d: float
    flange_t: float


@dataclass
class Chamber:
    index: int
    box: tuple
    port_air: list
    gross_l: float
    net_l: float
    displacement_l: float
    sheet_net_l: float


@dataclass
class Check:
    name: str
    level: str
    message: str


@dataclass
class Layout:
    spec: CabSpec
    parts: list
    cutouts: list
    round_ports: list
    slot_ports: list
    hardware: list
    envelopes: list
    chambers: list
    gross_l: float
    net_l: list
    mass_kg: dict
    com_mm: tuple
    tolex: dict | None
    part_count: int
    notes: list

    def to_dict(self) -> dict:
        from dataclasses import asdict
        d = asdict(self)
        d["spec"]["aesthetics"] = asdict(self.spec.aesthetics)
        return _plain(d)


def _plain(obj):
    """Tuples to lists, recursively, so json.dumps output is stable."""
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    return obj


@dataclass
class Frame:
    """Derived frame numbers every builder needs (internal helper)."""
    W: float
    H: float
    D: float
    t: float
    x0: float
    x1: float
    z0: float
    z1: float
    y_bf: float          # baffle front face
    y_bb: float          # baffle back face
    y_bi: float          # back panel inner face (open backs too: the engine's internal depth)
    closed: bool
    slot_h: float        # 0 without a slot port
    shelf_depth: float   # 0 without a slot port
    chambers: list       # [(xa, xb), ...] chamber x ranges
    z_vis0: float        # visible baffle bottom (shelf top with a slot)
    x_b0: float          # baffle blank extents
    x_b1: float
    z_b0: float
    z_b1: float

    @property
    def chamber_centers(self) -> list:
        return [(a + b) / 2.0 for a, b in self.chambers]

    @property
    def shelf_top(self) -> float:
        return self.z0 + self.slot_h + BAFFLE_MM


def species_density(name) -> float | None:
    if not name:
        return None
    key = str(name).strip().lower()
    if key in SPECIES_DENSITY:
        return SPECIES_DENSITY[key]
    for word, canonical in (("walnut", "black walnut"), ("cherry", "black cherry"),
                            ("maple", "hard maple"), ("sapele", "sapele")):
        if word in key:
            return SPECIES_DENSITY[canonical]
    return None


def species_name(name) -> str:
    key = str(name).strip().lower()
    for word, canonical in (("walnut", "black walnut"), ("cherry", "black cherry"),
                            ("maple", "hard maple"), ("sapele", "sapele")):
        if word in key:
            return canonical
    return key


def load_voicing(path) -> dict:
    return json.loads(Path(path).read_text())


def _speaker_from(s: dict) -> Speaker:
    return Speaker(
        slug=s["slug"], cutout_mm=float(s["cutout_mm"]),
        bolt_circle_mm=float(s["bolt_circle_mm"]), bolt_count=int(s["bolt_count"]),
        depth_mm=float(s["depth_mm"]), weight_kg=float(s["weight_kg"]),
        displacement_l=float(s["displacement_l"]),
        frame_diameter_mm=float(s["frame_diameter_mm"]),
        magnet_diameter_mm=(None if s["magnet_diameter_mm"] is None
                            else float(s["magnet_diameter_mm"])),
        magnet_diameter_estimated=bool(s["magnet_diameter_estimated"]))


def _port_from(p: dict) -> PortSpec:
    return PortSpec(
        shape=p["shape"],
        diameter_mm=None if p["diameter_mm"] is None else float(p["diameter_mm"]),
        slot_w_mm=None if p["slot_w_mm"] is None else float(p["slot_w_mm"]),
        slot_h_mm=None if p["slot_h_mm"] is None else float(p["slot_h_mm"]),
        length_mm=float(p["length_mm"]), location=p["location"],
        count=int(p["count"]))


def order_from(voicing: dict, aesthetics: Aesthetics) -> CabSpec:
    """CabSpec from a voicing.json dict and the aesthetics block.
    ValueError on sheet blockers, missing keys, a dovetail on the tolex line,
    or invalid aesthetics. Never reads warning text."""
    errors = aesthetics.validate()
    if errors:
        raise ValueError("aesthetics: " + "; ".join(errors))
    try:
        blockers = voicing["blockers"]
        status = voicing["prediction_status"]
        enc = voicing["enclosure"]
        box = voicing["box"]
        con = voicing["construction"]
        vols = voicing["volumes"]
        line, species, wall = con["line"], con["species"], con["wall_material"]
        external = tuple(float(v) for v in box["external_mm"])
        internal = tuple(float(v) for v in box["internal_mm"])
        speakers = [_speaker_from(s) for s in voicing["speakers"]]
        driver_count = int(enc["driver_count"])
        chambers = int(enc["chambers"])
        enclosure_type = enc["type"]
        jack_config = enc["jack_config"]
        open_fraction = enc["open_fraction"]
        port = voicing["port"]
        port_spec = None if port is None else _port_from(port)
        net_total = float(vols["net_total_l"])
        per_chamber = float(vols["per_chamber_net_l"])
        inside = vols.get("inside_parts_l")
        inside = None if inside is None else float(inside)
        name = voicing["name"]
        panel_mm, back_mm = float(con["panel_mm"]), float(con["back_mm"])
        baffle_mm, recess_mm = float(con["baffle_mm"]), float(con["recess_mm"])
    except KeyError as e:
        raise ValueError(f"voicing.json lacks {e.args[0]}") from None
    if blockers:
        raise ValueError("voicing sheet has blockers: " + "; ".join(blockers))
    if line not in PANEL_MM:
        raise ValueError(f"line must be tolex or hardwood, not {line!r}")
    if aesthetics.corner_joint == "dovetail" and line != "hardwood":
        raise ValueError("dovetail corners are a hardwood line option")
    if len(speakers) != driver_count:
        raise ValueError(f"{len(speakers)} speaker entries for {driver_count} drivers")
    if enclosure_type not in cabvoice.ENCLOSURE_TYPES:
        raise ValueError(f"unknown enclosure type {enclosure_type!r}")
    if (back_mm, baffle_mm, recess_mm) != (BACK_MM, BAFFLE_MM, RECESS_MM):
        raise ValueError("sheet construction thicknesses differ from the layout constants")
    if port_spec is not None:
        if port_spec.shape == "slot" and (port_spec.slot_w_mm is None or port_spec.slot_h_mm is None):
            raise ValueError("slot port without slot dimensions")
        if port_spec.shape == "round" and port_spec.diameter_mm is None:
            raise ValueError("round port without a diameter")
    return CabSpec(
        name=name, line=line, species=species, wall_material=wall,
        external_mm=external, internal_mm=internal, panel_mm=panel_mm,
        back_mm=back_mm, baffle_mm=baffle_mm, recess_mm=recess_mm,
        enclosure_type=enclosure_type, driver_count=driver_count, chambers=chambers,
        jack_config=jack_config, open_fraction=open_fraction, speakers=speakers,
        port=port_spec, net_total_l=net_total, per_chamber_net_l=per_chamber,
        prediction_status=status, aesthetics=aesthetics, sheet_inside_parts_l=inside)


def frame(spec: CabSpec) -> Frame:
    W, H, D = spec.external_mm
    t = spec.shell_mm
    x0, x1, z0, z1 = -W / 2 + t, W / 2 - t, t, H - t
    y_bf, y_bb = RECESS_MM, RECESS_MM + BAFFLE_MM
    y_bi = D - BACK_MM      # open-back panels sit in the same plane; the air box stops there
    slot_h = shelf_depth = 0.0
    if spec.port is not None and spec.port.shape == "slot":
        slot_h, shelf_depth = spec.port.slot_h_mm, spec.port.length_mm
    if spec.chambers == 2:
        chambers = [(x0, -DIVIDER_MM / 2), (DIVIDER_MM / 2, x1)]
    else:
        chambers = [(x0, x1)]
    z_vis0 = z0 + slot_h + BAFFLE_MM if slot_h else z0
    if spec.aesthetics.baffle_mount == "floating":
        x_b0, x_b1 = x0 + BAFFLE_CLEARANCE_MM, x1 - BAFFLE_CLEARANCE_MM
        z_b0 = z_vis0 if slot_h else z0 + BAFFLE_CLEARANCE_MM
        z_b1 = z1 - BAFFLE_CLEARANCE_MM
    else:
        x_b0, x_b1 = x0 - DADO_MM, x1 + DADO_MM
        z_b0 = z_vis0 if slot_h else z0 - DADO_MM
        z_b1 = z1 + DADO_MM
    return Frame(W, H, D, t, x0, x1, z0, z1, y_bf, y_bb, y_bi, spec.closed,
                 slot_h, shelf_depth, chambers, z_vis0, x_b0, x_b1, z_b0, z_b1)


def finger_schedule(depth_mm: float, thickness_mm: float,
                    width_hint_mm: float | None = None) -> tuple:
    """(count, width): an odd count nearest depth / hint so both ends are full
    fingers; hint defaults to half the thickness. Count is at least 3."""
    hint = width_hint_mm or thickness_mm / 2.0
    raw = depth_mm / hint
    n = int(round(raw))
    if n % 2 == 0:
        n = n - 1 if abs(raw - (n - 1)) <= abs(raw - (n + 1)) else n + 1
    n = max(3, n)
    return n, depth_mm / n


def dovetail_schedule(depth_mm: float, t_top_mm: float, pin_mm: float,
                      tail_target_mm: float, slope: float) -> dict:
    """Through dovetail along one edge of length depth_mm. Tails on the side
    panel, pins on the top or bottom panel, half-pins at both ends. Widths
    are at the outer face; every pin widens by 2 * flare toward the
    shoulder (half-pins by one flare, inward only) and every tail narrows
    by the same."""
    flare = t_top_mm / slope
    n = max(2, int(round((depth_mm - pin_mm) / (tail_target_mm + pin_mm))))
    while n >= 2:
        tail_w = (depth_mm - (n + 1) * pin_mm) / n
        if tail_w - 2 * flare > 5.0:
            break
        n -= 1
    if n < 2:
        raise ValueError(f"no dovetail layout fits a {depth_mm:g} mm edge with {pin_mm:g} mm pins")
    tails, pins = [], []
    y = pin_mm
    for i in range(n):
        tails.append((y, y + tail_w))
        y += tail_w
        if i < n - 1:
            pins.append((y, y + pin_mm))
            y += pin_mm
    return {"count": n, "tail_w": tail_w, "pin_w": pin_mm, "flare": flare,
            "slope": slope, "tails": tails, "pins": pins,
            "half_pins": [(0.0, pin_mm), (depth_mm - pin_mm, depth_mm)]}


def _rect(y0, y1, z_out, z_sh) -> list:
    return [(y0, z_out), (y1, z_out), (y1, z_sh), (y0, z_sh)]


def _finger_polys(depth, n, z_out, z_sh, gaps_even: bool) -> list:
    w = depth / n
    ks = range(0, n, 2) if gaps_even else range(1, n, 2)
    return [_rect(k * w, (k + 1) * w, z_out, z_sh) for k in ks]


def _dovetail_polys(sch: dict, depth, z_out, z_sh, role: str) -> list:
    """Removal quads in the YZ plane for one corner. role 'tails' removes the
    pin shapes (the side panel keeps its tails); role 'pins' removes the tail
    shapes (the top or bottom panel keeps its pins)."""
    d = sch["flare"]
    polys = []
    if role == "tails":
        a, b = sch["half_pins"][0]
        polys.append([(a, z_out), (b, z_out), (b + d, z_sh), (a, z_sh)])
        for (y0, y1) in sch["pins"]:
            polys.append([(y0, z_out), (y1, z_out), (y1 + d, z_sh), (y0 - d, z_sh)])
        a, b = sch["half_pins"][1]
        polys.append([(a, z_out), (b, z_out), (b, z_sh), (a - d, z_sh)])
    else:
        for (y0, y1) in sch["tails"]:
            polys.append([(y0, z_out), (y1, z_out), (y1 - d, z_sh), (y0 + d, z_sh)])
    return polys


def shell_material(spec: CabSpec) -> tuple:
    """(material name, density) for the shell panels."""
    if spec.line == "tolex":
        return f"baltic birch {PANEL_MM['tolex']:g} mm", BIRCH_DENSITY
    dens = species_density(spec.species)
    name = species_name(spec.species) if spec.species else "hardwood, species not set"
    return f"{name} {PANEL_MM['hardwood']:g} mm", (dens if dens is not None else BIRCH_DENSITY)


HARDWOOD_GRAIN_NOTE = "grain front to back on all four panels, book-matched, show face out"
HARDWOOD_CLEAT_NOTE = "screwed through slotted holes, glued at the center 100 mm only"


def birch(t: float) -> str:
    return f"baltic birch {t:g} mm"


def shell_blanks(spec: CabSpec) -> list:
    """Top, bottom, and two sides as full-size blanks with the comb removals
    at the four corner blocks as edge_cuts features."""
    fr = frame(spec)
    W, H, D, t = fr.W, fr.H, fr.D, fr.t
    a = spec.aesthetics
    material, density = shell_material(spec)
    if a.corner_joint == "finger":
        n, w = finger_schedule(D, t, a.finger_width_mm)
        note = (f"finger joint, {n} fingers of {w:.1f} mm, both ends full, "
                "front finger on top and bottom")
        side_top = _finger_polys(D, n, H, H - t, True)
        side_bot = _finger_polys(D, n, 0.0, t, True)
        top_polys = _finger_polys(D, n, H, H - t, False)
        bot_polys = _finger_polys(D, n, 0.0, t, False)
    else:
        sch = dovetail_schedule(D, t, a.dovetail_pin_mm or t / 2.0, a.dovetail_tail_mm,
                                a.dovetail_slope)
        note = (f"through dovetail, {sch['count']} tails of {sch['tail_w']:.1f} mm, "
                f"pins {sch['pin_w']:.1f} mm, slope 1:{sch['slope']:g}, half-pins both ends, "
                "tails on the sides")
        side_top = _dovetail_polys(sch, D, H, H - t, "tails")
        side_bot = _dovetail_polys(sch, D, 0.0, t, "tails")
        top_polys = _dovetail_polys(sch, D, H, H - t, "pins")
        bot_polys = _dovetail_polys(sch, D, 0.0, t, "pins")
    if spec.line == "hardwood":
        note += "; " + HARDWOOD_GRAIN_NOTE
    left = (-W / 2, -W / 2 + t)
    right = (W / 2 - t, W / 2)
    parts = [
        Blank("side_left", 1, material, density, pos=(-W / 2, 0.0, 0.0), size=(t, D, H),
              blank_mm=(t, H, D), length_axis="Y", notes=note,
              features=[{"type": "edge_cuts", "x": left, "polys": side_top},
                        {"type": "edge_cuts", "x": left, "polys": side_bot}]),
        Blank("side_right", 1, material, density, pos=(W / 2 - t, 0.0, 0.0), size=(t, D, H),
              blank_mm=(t, H, D), length_axis="Y", notes=note,
              features=[{"type": "edge_cuts", "x": right, "polys": side_top},
                        {"type": "edge_cuts", "x": right, "polys": side_bot}]),
        Blank("top", 1, material, density, pos=(-W / 2, 0.0, H - t), size=(W, D, t),
              blank_mm=(t, W, D), length_axis="Y", notes=note,
              features=[{"type": "edge_cuts", "x": left, "polys": top_polys},
                        {"type": "edge_cuts", "x": right, "polys": top_polys}]),
        Blank("bottom", 1, material, density, pos=(-W / 2, 0.0, 0.0), size=(W, D, t),
              blank_mm=(t, W, D), length_axis="Y", notes=note,
              features=[{"type": "edge_cuts", "x": left, "polys": bot_polys},
                        {"type": "edge_cuts", "x": right, "polys": bot_polys}]),
    ]
    return parts
```
<!-- /code -->

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest scripts/test_cablayout.py -q`
Expected: `10 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/cablayout.py scripts/test_cablayout.py
git commit -m "cablayout: constants, dataclasses, sheet loading, finger and dovetail schedules, shell blanks" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 5: Layout kernel, part 2: baffle, cutouts and bolts, cleats, grill frame, brace, divider, stiffeners

**Files:**
- Modify: `scripts/cablayout.py` (append after the Task 4 unit)
- Modify: `scripts/test_cablayout.py` (append after the Task 4 tests)

**Interfaces:**
- Consumes: Task 4 dataclasses and constants.
- Produces: builder functions the Task 7 orchestrator calls in order and the tests call directly: `frame(spec) -> Frame` (the internal box and reference planes every builder shares), `cutout_centers(spec, fr)` (1x12 at x 0; mono 2x12 at +-(cutout + 68)/2; stereo 44 mm from the shell and 25 mm from the divider at the floor, surplus split evenly), `baffle_and_cutouts(spec, fr) -> (Blank, list[Cutout], dados)` (floating or fixed, shortened for a slot, bolt centers first at twelve o'clock), `cleat_blanks`, `grill_frame_blanks` (four 12 x 40 strips with half-lap notches, y from 3 to 15, covering only the baffle above a slot shelf), `brace_blank`, `divider_blank` (no cleats on the divider: the baffle and back screw into its edges), `stiffener_blanks -> (blanks, notes)`. Exact signatures are in the code below.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_cablayout.py`:

<!-- code: test_cablayout.py unit 5 -->
```python
# === TASK 5 ===
def test_baffle_floating_dims_and_bolts():
    spec = spec_for()
    fr = L.frame(spec)
    baffle, cutouts, dados = L.baffle_and_cutouts(spec, fr)
    assert baffle.pos == (-235.0, 20.0, 19.0) and baffle.size == (470.0, 18.0, 419.2)
    assert dados == {}
    co = cutouts[0]
    assert co.center == (0.0, 228.6) and co.diameter == 283 and co.chamber == 0
    assert co.bolt_centers[0] == pytest.approx((0.0, 228.6 + 148.5))
    assert len(co.bolt_centers) == 4
    assert baffle.features[0] == {"type": "cutout", "center": (0.0, 228.6), "d": 283}
    assert "floating" in baffle.notes and "T-nuts" in baffle.notes


def test_baffle_fixed_dados():
    spec = spec_for(aesthetics=L.Aesthetics(baffle_mount="fixed"))
    fr = L.frame(spec)
    baffle, _, dados = L.baffle_and_cutouts(spec, fr)
    assert baffle.size == (484.0, 18.0, 433.2) and baffle.pos == (-242.0, 20.0, 12.0)
    assert set(dados) == {"side_left", "side_right", "top", "bottom"}
    assert dados["side_left"]["box"] == ((-242.0, 20.0, 12.0), (-236.0, 38.0, 445.2))
    slot = spec_for(port="slot", aesthetics=L.Aesthetics(baffle_mount="fixed"))
    _, _, dados = L.baffle_and_cutouts(slot, L.frame(slot))
    assert "bottom" not in dados


def test_2x12_cutout_spacing_and_stereo_centers():
    spec = spec_for(drivers=2)
    _, cutouts, _ = L.baffle_and_cutouts(spec, L.frame(spec))
    assert [c.center[0] for c in cutouts] == [-175.5, 175.5]
    assert (cutouts[1].center[0] - 141.5) - (cutouts[0].center[0] + 141.5) == pytest.approx(68.0)
    st = spec_for(external=(800.0, 457.2, 279.4), drivers=2, chambers=2, jack="stereo")
    fr = L.frame(st)
    assert fr.chambers == [(-382.0, -9.0), (9.0, 382.0)]
    _, cutouts, _ = L.baffle_and_cutouts(st, fr)
    assert [c.center[0] for c in cutouts] == pytest.approx([-186.0, 186.0]) and [c.chamber for c in cutouts] == [0, 1]
    tight = spec_for(external=(722.0 + 36.0, 457.2, 279.4), drivers=2, chambers=2, jack="stereo")
    _, cutouts, _ = L.baffle_and_cutouts(tight, L.frame(tight))
    assert cutouts[0].center[0] + 141.5 == pytest.approx(-9.0 - 25.0)   # 25 mm to the divider
    assert cutouts[0].center[0] - 141.5 == pytest.approx(-361.0 + 44.0)  # 44 mm to the shell


def test_cleats_by_mount_port_and_chambers():
    spec = spec_for()
    names = [p.name for p in L.cleat_blanks(spec, L.frame(spec))]
    assert names == ["cleat_baffle_top", "cleat_baffle_bottom", "cleat_baffle_left", "cleat_baffle_right",
                     "cleat_back_top", "cleat_back_bottom", "cleat_back_left", "cleat_back_right"]
    top = L.cleat_blanks(spec, L.frame(spec))[0]
    assert top.pos == (-236.0, 38.0, 421.2) and top.size == (472.0, 18.0, 18.0) and top.chamber == 0
    slot = spec_for(port="slot")
    assert "cleat_baffle_bottom" not in [p.name for p in L.cleat_blanks(slot, L.frame(slot))]
    fixed = spec_for(aesthetics=L.Aesthetics(baffle_mount="fixed"))
    assert all(p.name.startswith("cleat_back") for p in L.cleat_blanks(fixed, L.frame(fixed)))
    st = spec_for(external=(800.0, 457.2, 279.4), drivers=2, chambers=2, jack="stereo")
    st_names = [p.name for p in L.cleat_blanks(st, L.frame(st))]
    assert "cleat_baffle_right_0" not in st_names and "cleat_baffle_left_1" not in st_names
    assert "cleat_baffle_left_0" in st_names and "cleat_baffle_right_1" in st_names
    hw = spec_for(line="hardwood", species="cherry")
    assert L.HARDWOOD_CLEAT_NOTE in L.cleat_blanks(hw, L.frame(hw))[0].notes
    op = spec_for(enclosure="open", port=None, open_fraction=0.4)
    op_names = [p.name for p in L.cleat_blanks(op, L.frame(op))]
    assert "cleat_back_left_upper" in op_names and "cleat_back_right_lower" in op_names


def test_grill_frame_geometry():
    spec = spec_for()
    strips = L.grill_frame_blanks(spec, L.frame(spec))
    assert [s.name for s in strips] == ["grill_top", "grill_bottom", "grill_left", "grill_right"]
    top, left = strips[0], strips[2]
    assert top.pos == (-234.0, 3.0, 397.2) and top.size == (468.0, 12.0, 40.0)
    assert left.pos == (-234.0, 3.0, 20.0) and left.size == (40.0, 12.0, 417.2)
    assert len(top.features) == 2 and len(left.features) == 2
    assert top.features[0]["box"][0][1] == 3.0 and top.features[0]["box"][1][1] == 9.0
    assert left.features[0]["box"][0][1] == 9.0 and left.features[0]["box"][1][1] == 15.0
    assert all(s.chamber is None for s in strips)
    slot = spec_for(port="slot")
    fr = L.frame(slot)
    bottom = L.grill_frame_blanks(slot, fr)[1]
    assert bottom.pos[2] == pytest.approx(fr.shelf_top + 2.0)


def test_brace_and_divider():
    assert L.brace_blank(spec_for(), L.frame(spec_for())) == []
    two = spec_for(drivers=2)
    (brace,) = L.brace_blank(two, L.frame(two))
    assert brace.pos == (-9.0, 40.0, 18.0) and brace.size == (18.0, 60.0, 421.2)
    assert len(brace.features) == 2 and brace.features[0]["box"] == ((-9.0, 40.0, 421.2), (9.0, 56.0, 439.2))
    fixed = spec_for(drivers=2, aesthetics=L.Aesthetics(baffle_mount="fixed"))
    assert L.brace_blank(fixed, L.frame(fixed))[0].features == []
    slot = spec_for(drivers=2, port="slot")
    fr = L.frame(slot)
    b = L.brace_blank(slot, fr)[0]
    assert b.pos[2] == pytest.approx(fr.shelf_top) and len(b.features) == 1
    st = spec_for(external=(800.0, 457.2, 279.4), drivers=2, chambers=2, jack="stereo")
    assert L.brace_blank(st, L.frame(st)) == []
    (div,) = L.divider_blank(st, L.frame(st))
    assert div.pos == (-9.0, 38.0, 18.0) and div.size == pytest.approx((18.0, 229.4, 421.2)) and div.chamber is None
    assert L.divider_blank(two, L.frame(two)) == []


def test_stiffeners_follow_the_span_rule():
    spec = spec_for()
    parts, notes = L.stiffener_blanks(spec, L.frame(spec))
    assert [p.name for p in parts] == ["stiffener_top", "stiffener_bottom", "stiffener_back"]
    top = parts[0]
    assert top.pos == pytest.approx((-20.0, 56.0, 421.2)) and top.size == pytest.approx((40.0, 193.4, 18.0))
    back = parts[2]
    assert back.pos[2] == pytest.approx(18.0 + 18.0 + 25.0 + 70.0 + 25.0)
    narrow = spec_for(external=(470.0, 457.2, 279.4))
    assert L.stiffener_blanks(narrow, L.frame(narrow)) == ([], [])
    two = spec_for(drivers=2)      # brace halves the top and bottom spans, not the back
    names = [p.name for p in L.stiffener_blanks(two, L.frame(two))[0]]
    assert names == ["stiffener_back"]
    tall = spec_for(external=(470.0, 520.0, 279.4))
    names = [p.name for p in L.stiffener_blanks(tall, L.frame(tall))[0]]
    assert names == ["stiffener_side_left", "stiffener_side_right"]
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest scripts/test_cablayout.py -q`
Expected: the Task 5 tests fail with `AttributeError: module 'cablayout' has no attribute ...`; the Task 4 tests still pass.

- [ ] **Step 3: Implement**

Append to `scripts/cablayout.py`:

<!-- code: cablayout.py unit 5 -->
```python
# === TASK 5 ===
def _suffix(spec: CabSpec, c: int) -> str:
    return f"_{c}" if spec.chambers == 2 else ""


def _blank_dims(t: float, a: float, b: float) -> tuple:
    return (t, min(a, b), max(a, b))


def cutout_centers(spec: CabSpec, fr: Frame) -> list:
    """[(x, chamber)] per driver. 1x12 at the chamber center; mono 2x12 at
    +-(cutout + 68) / 2; stereo 44 mm outboard and 25 mm inboard of the
    divider at the minimum width, the surplus split evenly beyond that."""
    if spec.driver_count == 1:
        return [(fr.chamber_centers[0], 0)]
    if spec.chambers == 2:
        out = []
        for i, (xa, xb) in enumerate(fr.chambers):
            cut = spec.speakers[i].cutout_mm
            surplus = (xb - xa) - (cut + SHELL_MARGIN_MM + CUTOUT_MARGIN_MM)
            off = DIVIDER_MM / 2.0 + CUTOUT_MARGIN_MM + cut / 2.0 + surplus / 2.0
            out.append((-off if i == 0 else off, i))
        return out
    c0, c1 = spec.speakers[0].cutout_mm, spec.speakers[1].cutout_mm
    return [(-(c0 / 2.0 + CUTOUT_GAP_MM / 2.0), 0), (c1 / 2.0 + CUTOUT_GAP_MM / 2.0, 0)]


def baffle_and_cutouts(spec: CabSpec, fr: Frame) -> tuple:
    """(baffle Blank, cutouts, dados) where dados maps a shell blank name to
    the notch feature a fixed baffle needs on that panel."""
    a = spec.aesthetics
    dx, dz = fr.x_b1 - fr.x_b0, fr.z_b1 - fr.z_b0
    zc = (fr.z_vis0 + fr.z1) / 2.0
    centers = cutout_centers(spec, fr)
    cutouts, features = [], []
    for i, (xc, chamber) in enumerate(centers):
        s = spec.speakers[i]
        r = s.bolt_circle_mm / 2.0
        bolts = []
        for k in range(s.bolt_count):
            ang = math.radians(90.0 - k * 360.0 / s.bolt_count)
            bolts.append((xc + r * math.cos(ang), zc + r * math.sin(ang)))
        cutouts.append(Cutout(i, chamber, (xc, zc), s.cutout_mm, s.bolt_circle_mm,
                              s.bolt_count, bolts))
        features.append({"type": "cutout", "center": (xc, zc), "d": s.cutout_mm})
        features.append({"type": "holes", "centers": bolts, "d": BOLT_HOLE_MM})
    if a.baffle_mount == "floating":
        note = ("floating baffle: 1 mm clearance per side, felt strips on the cleats, "
                "screwed through the cleats, removable")
    else:
        note = "fixed baffle: glued into 6 mm dados, blank 12 mm oversize"
        if spec.line == "hardwood":
            note += "; glued in the front 100 mm of each dado only (cross-grain rule)"
    if fr.slot_h:
        note += "; bottom edge rests on the slot port shelf"
    mounts = ", ".join(f"{s.bolt_count} bolts on a {s.bolt_circle_mm:g} mm circle"
                       for s in spec.speakers)
    note += f"; speakers front-mounted on T-nuts, {mounts}"
    baffle = Blank("baffle", 1, birch(BAFFLE_MM), BIRCH_DENSITY,
                   pos=(fr.x_b0, fr.y_bf, fr.z_b0), size=(dx, BAFFLE_MM, dz),
                   blank_mm=_blank_dims(BAFFLE_MM, dz, dx), features=features, notes=note)
    dados = {}
    if a.baffle_mount == "fixed":
        y0, y1 = fr.y_bf, fr.y_bb
        zlo = fr.z_b0
        dados["side_left"] = {"type": "notch", "box": ((fr.x0 - DADO_MM, y0, zlo), (fr.x0, y1, fr.z1 + DADO_MM))}
        dados["side_right"] = {"type": "notch", "box": ((fr.x1, y0, zlo), (fr.x1 + DADO_MM, y1, fr.z1 + DADO_MM))}
        dados["top"] = {"type": "notch", "box": ((fr.x0 - DADO_MM, y0, fr.z1), (fr.x1 + DADO_MM, y1, fr.z1 + DADO_MM))}
        if not fr.slot_h:
            dados["bottom"] = {"type": "notch", "box": ((fr.x0 - DADO_MM, y0, fr.z0 - DADO_MM), (fr.x1 + DADO_MM, y1, fr.z0))}
    return baffle, cutouts, dados


def _cleat(name, pos, size, axis, chamber, note) -> Blank:
    length = {"X": size[0], "Y": size[1], "Z": size[2]}[axis]
    return Blank(name, 1, birch(CLEAT_MM), BIRCH_DENSITY, pos=pos, size=size,
                 blank_mm=(CLEAT_MM, CLEAT_MM, length), notes=note, chamber=chamber,
                 length_axis=axis)


def cleat_blanks(spec: CabSpec, fr: Frame) -> list:
    """Baffle cleats (floating baffle only) and back cleats, per chamber, on
    the shell faces. The divider carries no cleats: the baffle and the back
    screw into its edges."""
    parts = []
    base = "18 x 18 birch cleat, screws every 150 mm"
    if spec.line == "hardwood":
        base += "; " + HARDWOOD_CLEAT_NOTE
    bnote = base + "; felt strip between cleat and baffle"
    y_cleat = fr.D - BACK_MM - CLEAT_MM
    for c, (xa, xb) in enumerate(fr.chambers):
        sfx = _suffix(spec, c)
        if spec.aesthetics.baffle_mount == "floating":
            zlo = fr.z_vis0 if fr.slot_h else fr.z0 + CLEAT_MM
            parts.append(_cleat(f"cleat_baffle_top{sfx}", (xa, fr.y_bb, fr.z1 - CLEAT_MM),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, bnote))
            if not fr.slot_h:
                parts.append(_cleat(f"cleat_baffle_bottom{sfx}", (xa, fr.y_bb, fr.z0),
                                    (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, bnote))
            if xa == fr.x0:
                parts.append(_cleat(f"cleat_baffle_left{sfx}", (xa, fr.y_bb, zlo),
                                    (CLEAT_MM, CLEAT_MM, fr.z1 - CLEAT_MM - zlo), "Z", c, bnote))
            if xb == fr.x1:
                parts.append(_cleat(f"cleat_baffle_right{sfx}", (xb - CLEAT_MM, fr.y_bb, zlo),
                                    (CLEAT_MM, CLEAT_MM, fr.z1 - CLEAT_MM - zlo), "Z", c, bnote))
        if spec.closed:
            parts.append(_cleat(f"cleat_back_top{sfx}", (xa, y_cleat, fr.z1 - CLEAT_MM),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, base))
            parts.append(_cleat(f"cleat_back_bottom{sfx}", (xa, y_cleat, fr.z0),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, base))
            if xa == fr.x0:
                parts.append(_cleat(f"cleat_back_left{sfx}", (xa, y_cleat, fr.z0 + CLEAT_MM),
                                    (CLEAT_MM, CLEAT_MM, fr.z1 - fr.z0 - 2 * CLEAT_MM), "Z", c, base))
            if xb == fr.x1:
                parts.append(_cleat(f"cleat_back_right{sfx}", (xb - CLEAT_MM, y_cleat, fr.z0 + CLEAT_MM),
                                    (CLEAT_MM, CLEAT_MM, fr.z1 - fr.z0 - 2 * CLEAT_MM), "Z", c, base))
        else:
            h_p = open_panel_height(spec, fr)
            parts.append(_cleat(f"cleat_back_top{sfx}", (xa, y_cleat, fr.z1 - CLEAT_MM),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, base))
            parts.append(_cleat(f"cleat_back_bottom{sfx}", (xa, y_cleat, fr.z0),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, base))
            for side, x_c in (("left", xa), ("right", xb - CLEAT_MM)):
                if (side == "left" and xa != fr.x0) or (side == "right" and xb != fr.x1):
                    continue
                parts.append(_cleat(f"cleat_back_{side}_upper{sfx}", (x_c, y_cleat, fr.z1 - h_p),
                                    (CLEAT_MM, CLEAT_MM, h_p - CLEAT_MM), "Z", c, base))
                parts.append(_cleat(f"cleat_back_{side}_lower{sfx}", (x_c, y_cleat, fr.z0 + CLEAT_MM),
                                    (CLEAT_MM, CLEAT_MM, h_p - CLEAT_MM), "Z", c, base))
    return parts


def open_panel_height(spec: CabSpec, fr: Frame) -> float:
    f = spec.open_fraction if spec.open_fraction is not None else cabvoice.OPEN_FRACTION.get(spec.enclosure_type, 0.4)
    return (1.0 - f) * (fr.z1 - fr.z0) / 2.0


def grill_frame_blanks(spec: CabSpec, fr: Frame) -> list:
    """Four 12 x 40 strips with half-lap corners, 2 mm inside the opening,
    face 3 mm behind the front edge, resting on the flanges and 5 mm felt
    corner spacers. Covers only the baffle above the shelf with a slot port."""
    t, w = GRILL_STRIP_T_MM, GRILL_STRIP_W_MM
    xg0, xg1 = fr.x0 + GRILL_CLEARANCE_MM, fr.x1 - GRILL_CLEARANCE_MM
    zg0, zg1 = fr.z_vis0 + GRILL_CLEARANCE_MM, fr.z1 - GRILL_CLEARANCE_MM
    y0, ym, y1 = GRILL_FRONT_MM, GRILL_FRONT_MM + t / 2.0, GRILL_FRONT_MM + t
    note = ("grill frame strip 12 x 40 birch, half-lap corners, cloth wrapped and stapled "
            "at the back, rests on the speaker flanges and 5 mm felt corner spacers, "
            "hook and loop to the baffle")
    mat = birch(GRILL_STRIP_T_MM)
    corners_x = ((xg0, xg0 + w), (xg1 - w, xg1))
    corners_z = ((zg0, zg0 + w), (zg1 - w, zg1))
    horiz_notches = [{"type": "notch", "box": ((cx[0], y0, cz[0]), (cx[1], ym, cz[1]))}
                     for cx in corners_x for cz in corners_z]
    vert_notches = [{"type": "notch", "box": ((cx[0], ym, cz[0]), (cx[1], y1, cz[1]))}
                    for cx in corners_x for cz in corners_z]
    top = Blank("grill_top", 1, mat, BIRCH_DENSITY, pos=(xg0, y0, zg1 - w), size=(xg1 - xg0, t, w),
                blank_mm=(t, w, xg1 - xg0), length_axis="X", notes=note,
                features=[n for n in horiz_notches if n["box"][0][2] == zg1 - w])
    bottom = Blank("grill_bottom", 1, mat, BIRCH_DENSITY, pos=(xg0, y0, zg0), size=(xg1 - xg0, t, w),
                   blank_mm=(t, w, xg1 - xg0), length_axis="X", notes=note,
                   features=[n for n in horiz_notches if n["box"][0][2] == zg0])
    left = Blank("grill_left", 1, mat, BIRCH_DENSITY, pos=(xg0, y0, zg0), size=(w, t, zg1 - zg0),
                 blank_mm=(t, w, zg1 - zg0), length_axis="Z", notes=note,
                 features=[n for n in vert_notches if n["box"][0][0] == xg0])
    right = Blank("grill_right", 1, mat, BIRCH_DENSITY, pos=(xg1 - w, y0, zg0), size=(w, t, zg1 - zg0),
                  blank_mm=(t, w, zg1 - zg0), length_axis="Z", notes=note,
                  features=[n for n in vert_notches if n["box"][0][0] == xg1 - w])
    return [top, bottom, left, right]


def brace_blank(spec: CabSpec, fr: Frame) -> list:
    """Center brace 18 x 60 on a mono 2x12, 2 mm behind the baffle, between
    the bottom (or the shelf) and the top, notched around the baffle cleats."""
    if not (spec.driver_count == 2 and spec.chambers == 1):
        return []
    bw, bd = BRACE_MM
    zb0 = fr.z_vis0 if fr.slot_h else fr.z0
    y0 = fr.y_bb + BRACE_SETBACK_MM
    features = []
    if spec.aesthetics.baffle_mount == "floating":
        features.append({"type": "notch", "box": ((-bw / 2, y0, fr.z1 - CLEAT_MM), (bw / 2, fr.y_bb + CLEAT_MM, fr.z1))})
        if not fr.slot_h:
            features.append({"type": "notch", "box": ((-bw / 2, y0, fr.z0), (bw / 2, fr.y_bb + CLEAT_MM, fr.z0 + CLEAT_MM))})
    note = ("center brace 18 x 60 birch, glued to top and bottom"
            + (" (bottom end on the slot shelf)" if fr.slot_h else "")
            + (", notched around the baffle cleats" if features else ""))
    return [Blank("brace", 1, birch(bw), BIRCH_DENSITY, pos=(-bw / 2, y0, zb0),
                  size=(bw, bd, fr.z1 - zb0), blank_mm=(bw, bd, fr.z1 - zb0),
                  features=features, notes=note, chamber=0, length_axis="Z")]


def divider_blank(spec: CabSpec, fr: Frame) -> list:
    if spec.chambers != 2:
        return []
    note = ("full-height divider 18 mm birch glued to top, bottom, and back; the baffle "
            "screws into its front edge over a felt strip and the back panel into its "
            "rear edge; two sealed chambers")
    return [Blank("divider", 1, birch(DIVIDER_MM), BIRCH_DENSITY,
                  pos=(-DIVIDER_MM / 2, fr.y_bb, fr.z0),
                  size=(DIVIDER_MM, fr.y_bi - fr.y_bb, fr.z1 - fr.z0),
                  blank_mm=_blank_dims(DIVIDER_MM, fr.y_bi - fr.y_bb, fr.z1 - fr.z0),
                  notes=note, chamber=None)]


def _chamber_of(fr: Frame, x: float) -> int:
    for c, (xa, xb) in enumerate(fr.chambers):
        if xa <= x <= xb:
            return c
    return 0


def stiffener_blanks(spec: CabSpec, fr: Frame) -> tuple:
    """(blanks, span notes): one 18 x 40 stiffener glued flat across the
    middle of any shell or back panel span over 450 mm between glued members.
    Open-back panels are left alone (short and removable)."""
    sw, sd = STIFFENER_MM       # 18 proud, 40 flat on the panel
    floating = spec.aesthetics.baffle_mount == "floating"
    y_cleat = fr.D - BACK_MM - CLEAT_MM
    ya_default = fr.y_bb + (CLEAT_MM if floating else 0.0)
    if spec.chambers == 2:
        segs = list(fr.chambers)
    elif spec.driver_count == 2:
        segs = [(fr.x0, -BRACE_MM[0] / 2), (BRACE_MM[0] / 2, fr.x1)]
    else:
        segs = [(fr.x0, fr.x1)]
    parts, notes = [], []
    note = "stiffener 18 x 40 birch glued flat across the middle of a span over 450 mm"
    mat = birch(sw)
    for (xa, xb) in segs:
        span = xb - xa
        if span <= SPAN_MAX_MM:
            continue
        xc = (xa + xb) / 2.0
        c = _chamber_of(fr, xc)
        sfx = _suffix(spec, c)
        ya, yb = ya_default, y_cleat
        if yb - ya > 50.0:
            parts.append(Blank(f"stiffener_top{sfx}", 1, mat, BIRCH_DENSITY,
                               pos=(xc - sd / 2, ya, fr.z1 - sw), size=(sd, yb - ya, sw),
                               blank_mm=(sw, sd, yb - ya), notes=note, chamber=c, length_axis="Y"))
            notes.append(f"top panel span {span:.0f} mm over {SPAN_MAX_MM:.0f}: stiffener added")
        yab = max(ya_default, fr.y_bf + fr.shelf_depth) if fr.slot_h else ya_default
        if yb - yab > 50.0:
            parts.append(Blank(f"stiffener_bottom{sfx}", 1, mat, BIRCH_DENSITY,
                               pos=(xc - sd / 2, yab, fr.z0), size=(sd, yb - yab, sw),
                               blank_mm=(sw, sd, yb - yab), notes=note, chamber=c, length_axis="Y"))
            notes.append(f"bottom panel span {span:.0f} mm over {SPAN_MAX_MM:.0f}: stiffener added")
    # back panel: spans split by the divider only
    if spec.closed:
        back_segs = list(fr.chambers)
        h_plate = spec.aesthetics.jack_plate_cutout_mm[1]
        for (xa, xb) in back_segs:
            span = xb - xa
            if span <= SPAN_MAX_MM:
                continue
            xc = (xa + xb) / 2.0
            c = _chamber_of(fr, xc)
            sfx = _suffix(spec, c)
            za = fr.z0 + CLEAT_MM + JACK_CLEAR_MM + h_plate + CLEARANCE_MM
            zb = fr.z1 - CLEAT_MM
            if zb - za > 50.0:
                parts.append(Blank(f"stiffener_back{sfx}", 1, mat, BIRCH_DENSITY,
                                   pos=(xc - sd / 2, fr.y_bi - sw, za), size=(sd, sw, zb - za),
                                   blank_mm=(sw, sd, zb - za), notes=note + "; stops above the jack plate",
                                   chamber=c, length_axis="Z"))
                notes.append(f"back panel span {span:.0f} mm over {SPAN_MAX_MM:.0f}: stiffener added")
    # side panels: span along z, split by the shelf with a slot port
    side_span = max(fr.slot_h, fr.z1 - fr.z_vis0) if fr.slot_h else fr.z1 - fr.z0
    if side_span > SPAN_MAX_MM:
        zc = (fr.z_vis0 + fr.z1) / 2.0 if fr.slot_h else (fr.z0 + fr.z1) / 2.0
        ya, yb = ya_default, y_cleat
        for side, x_c, c in (("left", fr.x0, 0), ("right", fr.x1 - sw, len(fr.chambers) - 1)):
            parts.append(Blank(f"stiffener_side_{side}", 1, mat, BIRCH_DENSITY,
                               pos=(x_c, ya, zc - sd / 2), size=(sw, yb - ya, sd),
                               blank_mm=(sw, sd, yb - ya), notes=note, chamber=c, length_axis="Y"))
        notes.append(f"side panel span {side_span:.0f} mm over {SPAN_MAX_MM:.0f}: stiffeners added")
    return parts, notes
```
<!-- /code -->

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest scripts/test_cablayout.py -q`
Expected: `17 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/cablayout.py scripts/test_cablayout.py
git commit -m "cablayout: baffle, cutouts and bolts, cleats, grill frame, brace, divider, stiffeners" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 6: Layout kernel, part 3: backs, round port placement, slot port, jack plates, handle, feet, envelopes

**Files:**
- Modify: `scripts/cablayout.py` (append after the Task 5 unit)
- Modify: `scripts/test_cablayout.py` (append after the Task 5 tests)

**Interfaces:**
- Consumes: Tasks 4 and 5, including Task 5's `open_panel_height(spec, fr)` (called by `back_blanks` and `jack_plates`).
- Produces: `back_blanks(spec, fr, ...)` (closed 12 mm flush with the rear edge, or two open-back panels), `jack_plates(spec, fr, ...) -> (hardware, features_by_panel, warnings)`, `speaker_envelopes(spec, fr, cutouts) -> list[Envelope]`, `tube_geometry(id_mm)`, `round_ports(spec, fr, envelopes, obstacles) -> (ports, blanks, back_features, blockers)` (placement scans outward 5 mm per step in the order outboard at driver height, below, lower outboard corner, above; `_envelope_segments(env)` builds the stepped envelope once and pushes its rearmost face back by 25 mm, an axial standoff, so a tube ending within 25 mm behind the magnet clears it radially; a tube that reaches the baffle, or finds no spot, is a blocker naming the longest tube that fits; ports of 20 to 24 mm are the flange ring alone), `slot_ports(spec, fr) -> (slots, blanks, blockers)` (shelf, cheeks, center cheek for a mono 2x12), `handle_hardware(spec, fr, com)`, `trim_hardware(spec, fr)` (feet or tilt-back legs, corners, piping, grill cloth). Exact signatures are in the code below.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_cablayout.py`:

<!-- code: test_cablayout.py unit 6 -->
```python
# === TASK 6 ===
def test_back_panels_closed_and_open():
    spec = spec_for()
    (back,) = L.back_blanks(spec, L.frame(spec))
    assert back.pos == (-236.0, 267.4, 18.0) and back.size == (472.0, 12.0, 421.2)
    op = spec_for(enclosure="open", port=None, open_fraction=0.4)
    upper, lower = L.back_blanks(op, L.frame(op))
    assert upper.size[2] == pytest.approx(126.36) and lower.pos[2] == 18.0
    assert upper.pos[2] == pytest.approx(439.2 - 126.36)
    semi = spec_for(enclosure="semi-open", port=None, open_fraction=0.25)
    assert L.back_blanks(semi, L.frame(semi))[0].size[2] == pytest.approx(157.95)


def test_jack_plates_positions_and_fit():
    spec = spec_for()
    hw, feats, warn = L.jack_plates(spec, L.frame(spec))
    assert len(hw) == 1 and hw[0].position == (0.0, 279.4, 96.0) and hw[0].cutout == (110.0, 70.0)
    assert feats["back"][0] == {"type": "rect_hole", "axis": "y", "center": (0.0, 96.0), "w": 110.0, "h": 70.0}
    assert warn == [] and "one 1/4 in jack" in hw[0].notes
    st = spec_for(external=(800.0, 457.2, 279.4), drivers=2, chambers=2, jack="stereo")
    hw, feats, _ = L.jack_plates(st, L.frame(st))
    assert [h.position[0] for h in hw] == [-195.5, 195.5] and len(feats["back"]) == 2
    short = spec_for(external=(508.0, 300.0, 279.4), enclosure="open", port=None, open_fraction=0.4)
    _, feats, warn = L.jack_plates(short, L.frame(short))
    assert "back_lower" in feats and warn and "does not fit" in warn[0]


def test_envelopes_two_step():
    spec = spec_for()
    fr = L.frame(spec)
    _, cutouts, _ = L.baffle_and_cutouts(spec, fr)
    (env,) = L.speaker_envelopes(spec, fr, cutouts)
    assert (env.basket_d, env.basket_len, env.magnet_d, env.magnet_len) == (283, 100.0, 168.0, 35.0)
    assert env.flange_d == 309 and env.flange_t == 5.0 and env.y0 == 20.0
    s = sheet()
    s["speakers"][0].update({"magnet_diameter_mm": None, "magnet_diameter_estimated": True, "depth_mm": 165})
    spec2 = L.order_from(s, L.Aesthetics())
    _, cutouts, _ = L.baffle_and_cutouts(spec2, fr)
    (env2,) = L.speaker_envelopes(spec2, fr, cutouts)
    assert env2.magnet_d == 185.0 and env2.magnet_len == 65.0


def test_round_port_placement_and_blockers():
    spec = spec_for(port="round")
    fr = L.frame(spec)
    _, cutouts, _ = L.baffle_and_cutouts(spec, fr)
    envs = L.speaker_envelopes(spec, fr, cutouts)
    ports, blanks, feats, blockers = L.round_ports(spec, fr, envs, [])
    assert blockers == [] and len(ports) == 1
    p = ports[0]
    assert p.center == pytest.approx((44.45 + 25.0, 228.6)) and p.od_mm == 88.9 and p.ring_od_mm == 148.9
    assert [b.name for b in blanks] == ["port_tube_0_0", "port_ring_0_0"]
    assert blanks[0].shape == "tube" and blanks[0].size == (88.9, 40.0, 77.3) and blanks[0].chamber == 0
    assert blanks[1].size == pytest.approx((148.9, 12.0, 88.9)) and blanks[1].pos == pytest.approx((p.center[0], 255.4, 228.6))
    assert feats == [{"type": "cutout", "center": p.center, "d": 88.9}]
    # a tube reaching the magnet must stand off by the magnet radius
    s = sheet(port="round")
    s["port"]["length_mm"] = 150.0
    spec2 = L.order_from(s, L.Aesthetics())
    ports2, _, _, _ = L.round_ports(spec2, fr, envs, [])
    assert ports2[0].center[0] == pytest.approx(84.0 + 25.0 + 44.45)
    # a center obstacle pushes the tube outward along the same direction
    wall = ((-20.0, 249.4, 156.0), (20.0, 267.4, 421.2))
    ports3, _, _, _ = L.round_ports(spec, fr, envs, [wall])
    assert ports3[0].center[0] >= 20.0 + 25.0 + 44.45 - 1e-9 and ports3[0].center[1] == 228.6
    # too long for the box: blocker names the longest tube that fits
    s["port"]["length_mm"] = 260.0
    spec3 = L.order_from(s, L.Aesthetics())
    _, _, _, blockers = L.round_ports(spec3, fr, envs, [])
    assert len(blockers) == 1 and blockers[0].startswith("port fit: chamber 0 port 0: tube 77.3 x 260 mm")
    assert "longest tube that fits at this diameter is" in blockers[0]
    # smallest box the cutout allows: a 6 in tube fits nowhere, a 3 in tube fits behind the magnet
    tiny = sheet(external=(371.0 + 36.0, 371.0 + 36.0, 279.4), port="round")
    tiny["port"]["diameter_mm"] = 153.2
    big = L.order_from(tiny, L.Aesthetics())
    frt = L.frame(big)
    _, cut_t, _ = L.baffle_and_cutouts(big, frt)
    env_t = L.speaker_envelopes(big, frt, cut_t)
    _, _, _, blk = L.round_ports(big, frt, env_t, [])
    assert blk and blk[0].endswith("use a front slot") and "no round port of 153.2 mm" in blk[0]
    tiny["port"]["diameter_mm"] = 77.3
    small = L.order_from(tiny, L.Aesthetics())
    ports_s, _, _, blk = L.round_ports(small, frt, env_t, [])
    assert blk == [] and ports_s[0].center[0] > 0


def test_round_port_short_length_uses_the_ring_alone():
    s = sheet(port="round")
    s["port"]["length_mm"] = 20.0
    spec = L.order_from(s, L.Aesthetics())
    fr = L.frame(spec)
    _, cutouts, _ = L.baffle_and_cutouts(spec, fr)
    envs = L.speaker_envelopes(spec, fr, cutouts)
    ports, blanks, feats, blockers = L.round_ports(spec, fr, envs, [])
    assert [b.name for b in blanks] == ["port_ring_0_0"]
    assert blanks[0].size == (148.9, 8.0, 77.3) and feats[0]["d"] == 77.3
    assert "no tube" in blanks[0].notes


def test_round_port_stands_off_behind_the_magnet():
    # the envelope's rearmost face carries a 25 mm axial standoff: a tube ending
    # within 25 mm behind the magnet (rear face y 155) must clear it radially
    spec = spec_for(port="round")
    fr = L.frame(spec)
    _, cutouts, _ = L.baffle_and_cutouts(spec, fr)
    envs = L.speaker_envelopes(spec, fr, cutouts)
    s = sheet(port="round")
    s["port"]["length_mm"] = 124.4                  # tube front at y 155.0, flush with the magnet
    ports, _, _, blockers = L.round_ports(L.order_from(s, L.Aesthetics()), fr, envs, [])
    assert blockers == [] and ports[0].center == pytest.approx((84.0 + 25.0 + 44.45, 228.6))
    s["port"]["length_mm"] = 99.0                   # tube front at y 180.4, past the standoff
    ports, _, _, _ = L.round_ports(L.order_from(s, L.Aesthetics()), fr, envs, [])
    assert ports[0].center == pytest.approx((44.45 + 25.0, 228.6))


def test_round_port_longer_than_the_box_reaches_the_baffle():
    spec = spec_for(port="round")
    fr = L.frame(spec)
    _, cutouts, _ = L.baffle_and_cutouts(spec, fr)
    envs = L.speaker_envelopes(spec, fr, cutouts)
    s = sheet(port="round")
    s["port"]["length_mm"] = 250.0                  # the box is 241.4 mm deep behind the baffle
    ports, blanks, _, blockers = L.round_ports(L.order_from(s, L.Aesthetics()), fr, envs, [])
    assert ports == [] and blanks == [] and len(blockers) == 1
    assert blockers[0].startswith("port fit: chamber 0 port 0: tube 77.3 x 250 mm reaches the baffle")
    assert "longest tube that fits at this diameter is 155 mm" in blockers[0]
    s["port"]["length_mm"] = 240.0                  # stops 1.4 mm short of the baffle: no spot instead
    _, _, _, blockers = L.round_ports(L.order_from(s, L.Aesthetics()), fr, envs, [])
    assert "tube 77.3 x 240 mm finds no spot with 25 mm clearance" in blockers[0]
    assert "longest tube that fits at this diameter is 155 mm" in blockers[0]


def test_round_port_takes_the_below_direction_in_a_narrow_box():
    # 371 mm wide inside: outboard at the magnet standoff hits the wall, so the
    # tube drops below the driver at the same radial distance
    s = sheet(external=(407.0, 600.0, 279.4), port="round")
    s["port"]["length_mm"] = 150.0
    spec = L.order_from(s, L.Aesthetics())
    fr = L.frame(spec)
    _, cutouts, _ = L.baffle_and_cutouts(spec, fr)
    envs = L.speaker_envelopes(spec, fr, cutouts)
    ports, _, _, blockers = L.round_ports(spec, fr, envs, [])
    assert blockers == [] and envs[0].center == (0.0, 300.0)
    assert ports[0].center == pytest.approx((0.0, 300.0 - 153.45))


def test_round_port_count_two_second_tube_clears_the_first():
    s = sheet(port="round")
    s["port"]["count"] = 2
    spec = L.order_from(s, L.Aesthetics())
    fr = L.frame(spec)
    _, cutouts, _ = L.baffle_and_cutouts(spec, fr)
    envs = L.speaker_envelopes(spec, fr, cutouts)
    ports, blanks, feats, blockers = L.round_ports(spec, fr, envs, [])
    assert blockers == [] and len(ports) == 2 and len(feats) == 2
    assert [b.name for b in blanks] == ["port_tube_0_0", "port_ring_0_0", "port_tube_0_1", "port_ring_0_1"]
    (x0, z0), (x1, z1) = ports[0].center, ports[1].center
    assert (x0, z0) == pytest.approx((69.45, 228.6)) and (x1, z1) == pytest.approx((0.0, 129.15))
    assert math.hypot(x1 - x0, z1 - z0) >= 88.9 + 25.0 - 1e-9        # tube to tube, 25 mm clear
    assert math.hypot(x1 - x0, z1 - z0) >= 74.45 + 44.45 - 1e-9      # ring over the other tube


def test_tube_geometry_non_stock_fallback():
    assert L.tube_geometry(77.3) == (88.9, "PVC 3 in sch 40", "")
    od, mat, note = L.tube_geometry(60.0)
    assert od == 71.0 and mat == "tube 60.0 mm ID" and "not a stock tube size" in note


def test_slot_port_cheeks_center_and_blockers():
    spec = spec_for(port="slot")
    fr = L.frame(spec)
    slots, blanks, blockers = L.slot_ports(spec, fr)
    assert blockers == [] and len(slots) == 1
    assert slots[0].x0 == pytest.approx(-150.0) and slots[0].cheek_w_mm == pytest.approx(86.0)
    assert [b.name for b in blanks] == ["shelf", "cheek_left", "cheek_right"]
    assert blanks[0].pos == (-236.0, 20.0, 58.0) and blanks[0].size == (472.0, 60.0, 18.0)
    two = spec_for(drivers=2, port="slot", external=(722.0 + 36.0, 457.2, 279.4))
    slots, blanks, blockers = L.slot_ports(two, L.frame(two))
    assert blockers == [] and len(slots) == 2 and "cheek_center_0" in [b.name for b in blanks]
    assert slots[1].x0 - slots[0].x1 == pytest.approx(18.0)
    narrow = spec_for(drivers=2, port="slot")     # two 300 mm slots in a 472 mm chamber
    _, _, blockers = L.slot_ports(narrow, L.frame(narrow))
    assert blockers and "do not fit" in blockers[0] and "center cheek" in blockers[0]
    s = sheet(port="slot")
    s["port"]["length_mm"] = 230.0
    deep = L.order_from(s, L.Aesthetics())
    _, _, blockers = L.slot_ports(deep, L.frame(deep))
    assert blockers and "breathe" in blockers[0]


def test_handle_strap_and_recessed():
    spec = spec_for()
    fr = L.frame(spec)
    hw, feats, warn = L.handle_hardware(spec, fr, (0.0, 108.0, 229.0))
    assert hw[0].item == "strap handle" and hw[0].position == (0.0, 108.0, 457.2) and feats == {} and warn == []
    hw, _, _ = L.handle_hardware(spec, fr, (0.0, 10.0, 229.0))
    assert hw[0].position[1] == 50.0
    rec = spec_for(aesthetics=L.Aesthetics(handle="recessed-side"))
    hw, feats, warn = L.handle_hardware(rec, fr, (0.0, 108.0, 229.0))
    assert [h.item for h in hw] == ["recessed handle", "recessed handle"] and warn == []
    assert hw[0].position == pytest.approx((-254.0, 151.0, 298.8)) and feats["side_left"][0]["axis"] == "x"
    shallow = spec_for(external=(508.0, 457.2, 200.0), aesthetics=L.Aesthetics(handle="recessed-side"))
    _, _, warn = L.handle_hardware(shallow, L.frame(shallow), (0.0, 80.0, 229.0))
    assert warn and "use a strap handle" in warn[0]


def test_trim_hardware():
    spec = spec_for()
    items = [h.item for h in L.trim_hardware(spec, L.frame(spec))]
    assert items.count("foot") == 4 and items.count("corner") == 8 and "grill cloth" in items
    feet = [h for h in L.trim_hardware(spec, L.frame(spec)) if h.item == "foot"]
    assert feet[0].position == (-202.0, 52.0, 0.0)
    hw = spec_for(line="hardwood", species="sapele", aesthetics=L.Aesthetics(feet="tilt-back", piping=True))
    items = [h.item for h in L.trim_hardware(hw, L.frame(hw))]
    assert "corner" not in items and items.count("tilt-back leg") == 2 and "piping" in items
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest scripts/test_cablayout.py -q`
Expected: the Task 6 tests fail with `AttributeError`; earlier tests still pass.

- [ ] **Step 3: Implement**

Append to `scripts/cablayout.py`:

<!-- code: cablayout.py unit 6 -->
```python
# === TASK 6 ===
def back_blanks(spec: CabSpec, fr: Frame) -> list:
    """Closed: one 12 mm back flush with the rear edge. Open and semi-open:
    two 12 mm panels top and bottom sized from the open fraction."""
    mat = birch(BACK_MM)
    w = fr.x1 - fr.x0
    if spec.closed:
        note = "12 mm birch back, removable, screwed to the cleats every 150 mm"
        if spec.chambers == 2:
            note += " and into the divider's rear edge"
        return [Blank("back", 1, mat, BIRCH_DENSITY, pos=(fr.x0, fr.D - BACK_MM, fr.z0),
                      size=(w, BACK_MM, fr.z1 - fr.z0),
                      blank_mm=_blank_dims(BACK_MM, fr.z1 - fr.z0, w), notes=note)]
    h_p = open_panel_height(spec, fr)
    f = 1.0 - 2.0 * h_p / (fr.z1 - fr.z0)
    note = (f"open back panel 12 mm birch, {h_p:.0f} mm tall "
            f"((1 - {f:.2f}) x internal height / 2), screwed to the cleats")
    return [Blank("back_upper", 1, mat, BIRCH_DENSITY, pos=(fr.x0, fr.D - BACK_MM, fr.z1 - h_p),
                  size=(w, BACK_MM, h_p), blank_mm=_blank_dims(BACK_MM, h_p, w), notes=note),
            Blank("back_lower", 1, mat, BIRCH_DENSITY, pos=(fr.x0, fr.D - BACK_MM, fr.z0),
                  size=(w, BACK_MM, h_p), blank_mm=_blank_dims(BACK_MM, h_p, w),
                  notes=note + "; carries the jack plate")]


def _attach(parts: list, name: str, features: list) -> None:
    for p in parts:
        if p.name == name:
            p.features.extend(features)
            return
    raise KeyError(f"no blank named {name}")


def jack_plates(spec: CabSpec, fr: Frame) -> tuple:
    """(hardware, features by panel name, warnings): one recessed plate per
    chamber at the bottom center of the back (or the lower open panel),
    25 mm above the cleat."""
    w, h = spec.aesthetics.jack_plate_cutout_mm
    panel = "back" if spec.closed else "back_lower"
    z_p = fr.z0 + CLEAT_MM + JACK_CLEAR_MM + h / 2.0
    text = {"mono": "one 1/4 in jack",
            "mono-parallel-out": "two 1/4 in jacks wired in parallel on one plate",
            "stereo": "one 1/4 in jack per chamber plate"}.get(spec.jack_config, spec.jack_config)
    finish = "brass" if spec.line == "hardwood" else "metal"
    hardware, features, warnings = [], {panel: []}, []
    for c, xc in enumerate(fr.chamber_centers):
        hardware.append(Hardware("jack plate", (xc, fr.D, z_p), (w, h), panel,
                                 f"recessed {finish} plate, cutout {w:g} x {h:g} mm, {text}"))
        features[panel].append({"type": "rect_hole", "axis": "y", "center": (xc, z_p), "w": w, "h": h})
    if not spec.closed:
        top = fr.z0 + open_panel_height(spec, fr)
        if z_p + h / 2.0 + 10.0 > top:
            warnings.append(f"jack plate cutout {h:g} mm tall does not fit the "
                            f"{top - fr.z0:.0f} mm lower open-back panel with 25 mm above the cleat")
    return hardware, features, warnings


def speaker_envelopes(spec: CabSpec, fr: Frame, cutouts: list) -> list:
    out = []
    for co in cutouts:
        s = spec.speakers[co.speaker]
        basket_len = min(BASKET_LEN_MM, s.depth_mm)
        magnet_len = max(0.0, s.depth_mm - BASKET_LEN_MM)
        magnet_d = (s.magnet_diameter_mm + COVER_MM if s.magnet_diameter_mm is not None
                    else GENERIC_MAGNET_MM)
        out.append(Envelope(co.speaker, co.chamber, co.center, fr.y_bf, s.cutout_mm, basket_len,
                            magnet_d, magnet_len, s.frame_diameter_mm, FLANGE_T_MM))
    return out


def _overlap(a0, a1, b0, b1) -> bool:
    return min(a1, b1) - max(a0, b0) > 1e-9


def _circle_box_gap(cx, cz, r, box) -> float:
    (x0, _, z0), (x1, _, z1) = box
    dx = max(x0 - cx, 0.0, cx - x1)
    dz = max(z0 - cz, 0.0, cz - z1)
    return math.hypot(dx, dz) - r


def _envelope_segments(env: Envelope) -> list:
    """[(y_front, y_rear, radius)] steps of the envelope: basket, then magnet
    when there is one. The rearmost face is pushed back by CLEARANCE_MM (an
    axial standoff) so a tube ending within that distance behind the driver
    must also clear it radially."""
    segs = [(env.y0, env.y0 + env.basket_len, env.basket_d / 2.0)]
    if env.magnet_len > 0:
        segs.append((env.y0 + env.basket_len, env.y0 + env.basket_len + env.magnet_len,
                     env.magnet_d / 2.0))
    s0, s1, er = segs[-1]
    segs[-1] = (s0, s1 + CLEARANCE_MM, er)
    return segs


def _tube_clear(center, r, ya, yb, chamber, fr, obstacles, envelopes, tubes) -> bool:
    """True when a tube of radius r along y in [ya, yb] at center (x, z)
    keeps CLEARANCE_MM from every obstacle box, envelope segment, other tube,
    and the chamber walls."""
    cx, cz = center
    xa, xb = fr.chambers[chamber]
    need = CLEARANCE_MM - 1e-6
    if cx - r - xa < need or xb - (cx + r) < need:
        return False
    if cz - r - fr.z0 < need or fr.z1 - (cz + r) < need:
        return False
    for box in obstacles:
        if _overlap(ya, yb, box[0][1], box[1][1]) and _circle_box_gap(cx, cz, r, box) < need:
            return False
    for env in envelopes:
        ex, ez = env.center
        for (s0, s1, er) in _envelope_segments(env):
            if _overlap(ya, yb, s0, s1) and math.hypot(cx - ex, cz - ez) - r - er < need:
                return False
    for (tx, tz, tr, ty0, ty1) in tubes:
        if _overlap(ya, yb, ty0, ty1) and math.hypot(cx - tx, cz - tz) - r - tr < need:
            return False
    return True


def _ring_clear(center, rr, yb, chamber, fr, obstacles, tubes) -> bool:
    """The flange ring (radius rr, glued to the back over [yb - 12, yb]) must
    not overlap a cleat, stiffener, plate keep-out, another tube, or a wall."""
    if rr <= 0:
        return True
    cx, cz = center
    xa, xb = fr.chambers[chamber]
    ya = yb - FLANGE_RING_T_MM
    if cx - rr < xa - 1e-6 or cx + rr > xb + 1e-6 or cz - rr < fr.z0 - 1e-6 or cz + rr > fr.z1 + 1e-6:
        return False
    for box in obstacles:
        if _overlap(ya, yb, box[0][1], box[1][1]) and _circle_box_gap(cx, cz, rr, box) < -1e-6:
            return False
    for (tx, tz, tr, ty0, ty1) in tubes:
        if _overlap(ya, yb, ty0, ty1) and math.hypot(cx - tx, cz - tz) - rr - tr < -1e-6:
            return False
    return True


def _radial_requirement(env: Envelope, ya, yb, r) -> float:
    need = 0.0
    for (s0, s1, er) in _envelope_segments(env):
        if _overlap(ya, yb, s0, s1):
            need = max(need, er)
    return need + CLEARANCE_MM + r


PLACE_STEP_MM = 5.0


def _place_tube(env: Envelope, sign: float, r, ya, yb, fr, obstacles, envelopes, tubes, ring_r=0.0):
    """First clear spot for a tube of radius r beside its driver: outboard at
    driver height, below, lower outboard diagonal, above, each direction
    scanned outward from the radial requirement in 5 mm steps until the
    chamber wall stops it."""
    xd, zd = env.center
    req = _radial_requirement(env, ya, yb, r)
    xa, xb = fr.chambers[env.chamber]
    inv = 1.0 / math.sqrt(2.0)
    for (ux, uz) in ((sign, 0.0), (0.0, -1.0), (sign * inv, -inv), (0.0, 1.0)):
        dist = req
        while True:
            cand = (xd + ux * dist, zd + uz * dist)
            if not (xa <= cand[0] <= xb and fr.z0 <= cand[1] <= fr.z1):
                break
            if (_tube_clear(cand, r, ya, yb, env.chamber, fr, obstacles, envelopes, tubes)
                    and _ring_clear(cand, ring_r, yb, env.chamber, fr, obstacles, tubes)):
                return cand
            dist += PLACE_STEP_MM
    return None


def tube_geometry(id_mm: float) -> tuple:
    """(od, material, note) for a tube inside diameter."""
    if id_mm in PORT_TUBE_OD_MM:
        return PORT_TUBE_OD_MM[id_mm], f"PVC {PORT_TUBE_NOMINAL[id_mm]} sch 40", ""
    od = id_mm + 2 * TUBE_WALL_FALLBACK_MM
    return od, f"tube {id_mm:.1f} mm ID", "not a stock tube size; wall assumed 5.5 mm"


def round_ports(spec: CabSpec, fr: Frame, envelopes: list, obstacles: list) -> tuple:
    """(RoundPorts, blanks, back features, blockers). One port per driver in
    the chamber (spec.port.count per chamber), each beside its driver."""
    port = spec.port
    if port is None or port.shape != "round":
        return [], [], [], []
    id_mm, L = port.diameter_mm, port.length_mm
    od, mat, tube_note = tube_geometry(id_mm)
    r = od / 2.0
    ring_od = od + FLANGE_RING_EXTRA_MM
    ports, blanks, feats, blockers = [], [], [], []
    tubes = []
    by_chamber = {}
    for env in envelopes:
        by_chamber.setdefault(env.chamber, []).append(env)
    for c in range(len(fr.chambers)):
        envs = by_chamber.get(c, [])
        count = port.count
        for j in range(count):
            env = envs[min(j, len(envs) - 1)] if envs else None
            if env is None:
                blockers.append(f"port fit: chamber {c} has no driver to place a port beside")
                continue
            sign = -1.0 if env.center[0] < 0 else 1.0
            ya, yb = fr.D - L, fr.D - BACK_MM
            rr = ring_od / 2.0
            reaches = ya < fr.y_bb - 1e-6      # the tube must stay behind the baffle
            spot = None if reaches else _place_tube(env, sign, r, ya, yb, fr, obstacles, envelopes, tubes, rr)
            if spot is None:
                fit = None
                Lf = L - 5.0
                while Lf >= 2 * BACK_MM:
                    if (fr.D - Lf >= fr.y_bb - 1e-6
                            and _place_tube(env, sign, r, fr.D - Lf, yb, fr, obstacles, envelopes, tubes, rr)):
                        fit = Lf
                        break
                    Lf -= 5.0
                why = ("reaches the baffle" if reaches
                       else f"finds no spot with {CLEARANCE_MM:.0f} mm clearance")
                if fit is None:
                    blockers.append(f"port fit: chamber {c} port {j}: no round port of "
                                    f"{id_mm:.1f} mm fits with {CLEARANCE_MM:.0f} mm clearance; use a front slot")
                else:
                    blockers.append(f"port fit: chamber {c} port {j}: tube {id_mm:.1f} x {L:.0f} mm "
                                    f"{why}; longest tube that fits at this diameter is {fit:.0f} mm; "
                                    "lower Fb, use a larger tube, or a front slot")
                continue
            cx, cz = spot
            tubes.append((cx, cz, r, ya, yb))
            sfx = f"_{c}_{j}"
            has_tube = L > 2 * BACK_MM
            if has_tube:
                blanks.append(Blank(f"port_tube{sfx}", 1, mat, PVC_DENSITY, shape="tube",
                                    pos=(cx, fr.D - L, cz), size=(od, L, id_mm),
                                    blank_mm=(0.0, od, L), chamber=c,
                                    notes=f"cut to {L:.0f} mm, {id_mm:.1f} mm inside diameter, glued "
                                          "through the back panel and the flange ring"
                                          + ("; " + tube_note if tube_note else "")))
                ring_t, ring_id = FLANGE_RING_T_MM, od
                hole = od
            else:
                ring_t, ring_id = L - BACK_MM, id_mm
                hole = id_mm
            blanks.append(Blank(f"port_ring{sfx}", 1, birch(BACK_MM), BIRCH_DENSITY, shape="ring",
                                pos=(cx, fr.D - BACK_MM - ring_t, cz), size=(ring_od, ring_t, ring_id),
                                blank_mm=(ring_t, ring_od, ring_od), chamber=c,
                                notes="flange ring cut from 12 mm ply, glued to the inside face of the back"
                                      + ("" if has_tube else f"; the ring is the port ({ring_t:.0f} mm beyond the panel), no tube")))
            feats.append({"type": "cutout", "center": (cx, cz), "d": hole})
            ports.append(RoundPort(c, (cx, cz), id_mm, od, L, ring_od, fr.D - L, fr.D))
    return ports, blanks, feats, blockers


def slot_ports(spec: CabSpec, fr: Frame) -> tuple:
    """(SlotPorts, blanks, blockers): full-chamber-width slot under the
    baffle, an 18 mm shelf sets the port length, cheeks fill a narrower slot,
    a mono 2x12 gets two slots split by an 18 mm center cheek."""
    port = spec.port
    if port is None or port.shape != "slot":
        return [], [], []
    s_w, s_h, L = port.slot_w_mm, port.slot_h_mm, port.length_mm
    slots, blanks, blockers = [], [], []
    free = fr.y_bi - (fr.y_bf + L)
    if free < max(CLEARANCE_MM, s_h):
        blockers.append(f"port fit: slot shelf {L:.0f} mm deep leaves {free:.0f} mm behind it, "
                        f"under the {max(CLEARANCE_MM, s_h):.0f} mm the slot needs to breathe; "
                        "lower the slot height or use a round port")
        return slots, blanks, blockers
    mat18 = birch(BAFFLE_MM)
    for c, (xa, xb) in enumerate(fr.chambers):
        n = port.count
        avail = (xb - xa) - (n - 1) * DIVIDER_MM
        if n * s_w > avail + 1e-6:
            blockers.append(f"port fit: chamber {c}: {n} slot{'s' if n > 1 else ''} of {s_w:.0f} mm "
                            f"do not fit the {xb - xa:.0f} mm chamber"
                            + (" with the 18 mm center cheek" if n > 1 else "")
                            + "; narrow the slot or widen the box")
            continue
        cheek = (avail - n * s_w) / 2.0
        sfx = _suffix(spec, c)
        blanks.append(Blank(f"shelf{sfx}", 1, mat18, BIRCH_DENSITY, pos=(xa, fr.y_bf, fr.z0 + s_h),
                            size=(xb - xa, L, BAFFLE_MM), blank_mm=(BAFFLE_MM, L, xb - xa),
                            chamber=c, length_axis="X",
                            notes="slot port shelf 18 mm birch: front edge flush with the baffle face, "
                                  f"depth {L:.0f} mm equals the port length, doubles as the bottom "
                                  "cleat, glued to the sides"))
        if cheek > 0.5:
            for side, x_c in (("left", xa), ("right", xb - cheek)):
                blanks.append(Blank(f"cheek_{side}{sfx}", 1, mat18, BIRCH_DENSITY, pos=(x_c, fr.y_bf, fr.z0),
                                    size=(cheek, L, s_h), blank_mm=_blank_dims(cheek, L, s_h),
                                    chamber=c, notes="slot cheek, fills the slot end, glued"))
        x = xa + cheek
        for j in range(n):
            slots.append(SlotPort(c, x, x + s_w, s_h, L, cheek))
            x += s_w
            if j < n - 1:
                blanks.append(Blank(f"cheek_center{sfx}_{j}", 1, mat18, BIRCH_DENSITY,
                                    pos=(x, fr.y_bf, fr.z0), size=(DIVIDER_MM, L, s_h),
                                    blank_mm=_blank_dims(DIVIDER_MM, L, s_h), chamber=c,
                                    notes="center cheek between the two slots, in line with the brace"))
                x += DIVIDER_MM
    return slots, blanks, blockers


def handle_hardware(spec: CabSpec, fr: Frame, com: tuple) -> tuple:
    """(hardware, features by panel, warnings). Strap: screw pair on the top
    at the loaded center of mass. Recessed side handles: one per side at the
    depth center of mass, upper third, between the cleats."""
    a = spec.aesthetics
    xm, ym, zm = com
    hardware, features, warnings = [], {}, []
    allow = a.corner_allowance_mm
    if a.handle == "strap":
        y_h = min(max(ym, allow), fr.D - allow)
        half = a.handle_screw_spacing_mm / 2.0
        if abs(xm) + half > fr.W / 2.0 - allow:
            warnings.append("strap handle screws fall inside the corner allowance; shorten the spacing")
        hardware.append(Hardware("strap handle", (xm, y_h, fr.H), None, "top",
                                 f"screw pair {a.handle_screw_spacing_mm:g} mm apart on the width axis, "
                                 "centered on the loaded center of mass, T-nuts inside"))
        return hardware, features, warnings
    w, h = a.recessed_handle_cutout_mm
    y_lo = fr.y_bb + CLEAT_MM + CLEARANCE_MM + w / 2.0
    y_hi = fr.D - BACK_MM - CLEAT_MM - CLEARANCE_MM - w / 2.0
    z_h = fr.z0 + (fr.z1 - fr.z0) * 2.0 / 3.0
    z_lo = fr.z0 + CLEAT_MM + CLEARANCE_MM + h / 2.0
    z_hi = fr.z1 - CLEAT_MM - CLEARANCE_MM - h / 2.0
    if y_lo > y_hi or z_lo > z_hi:
        warnings.append("recessed handle does not fit between the baffle and back cleats; use a strap handle")
        y_h = (y_lo + y_hi) / 2.0
    else:
        y_h = min(max(ym, y_lo), y_hi)
    z_h = min(max(z_h, z_lo), z_hi) if z_lo <= z_hi else z_h
    for side, x_c, panel in (("left", -fr.W / 2.0, "side_left"), ("right", fr.W / 2.0, "side_right")):
        hardware.append(Hardware("recessed handle", (x_c, y_h, z_h), (w, h), panel,
                                 f"recessed side handle, cutout {w:g} x {h:g} mm, at the depth center of mass"))
        features[panel] = [{"type": "rect_hole", "axis": "x", "center": (y_h, z_h), "w": w, "h": h}]
    return hardware, features, warnings


def trim_hardware(spec: CabSpec, fr: Frame) -> list:
    a = spec.aesthetics
    out = []
    if a.feet == "rubber":
        inset = a.foot_inset_mm + a.foot_diameter_mm / 2.0
        for sx in (-1.0, 1.0):
            for y in (inset, fr.D - inset):
                out.append(Hardware("foot", (sx * (fr.W / 2.0 - inset), y, 0.0), None, "bottom",
                                    f"rubber foot {a.foot_diameter_mm:g} mm, one central screw"))
    else:
        for sx in (-1.0, 1.0):
            out.append(Hardware("tilt-back leg", (sx * fr.W / 2.0, 100.0, 100.0), None,
                                "side_left" if sx < 0 else "side_right",
                                "tilt-back leg pivot screws 100 mm from the front and bottom edges; "
                                "legs not modeled"))
    corners = a.corners if a.corners is not None else ("black" if spec.line == "tolex" else "none")
    if corners != "none":
        for sx in (-1.0, 1.0):
            for y in (0.0, fr.D):
                for z in (0.0, fr.H):
                    out.append(Hardware("corner", (sx * fr.W / 2.0, y, z), None, "",
                                        f"metal corner, {corners}; keep-out {a.corner_allowance_mm:g} mm "
                                        "for every cutout"))
    if a.piping:
        out.append(Hardware("piping", (0.0, 0.0, fr.H / 2.0), None, "",
                            "piping glued into the corner between grill frame and shell"))
    out.append(Hardware("grill cloth", (0.0, GRILL_FRONT_MM, fr.H / 2.0), None, "grill frame",
                        a.grill_cloth or "grill cloth not chosen"))
    return out
```
<!-- /code -->

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest scripts/test_cablayout.py -q`
Expected: `30 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/cablayout.py scripts/test_cablayout.py
git commit -m "cablayout: backs, round and slot ports, jack plates, handle, feet, speaker envelopes" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 7: Layout kernel, part 4: chambers and volumes, mass and center of mass, tolex, checks, report, `layout()`, the layout matrix

**Files:**
- Modify: `scripts/cablayout.py` (append after the Task 6 unit)
- Modify: `scripts/test_cablayout.py` (append after the Task 6 tests)

**Interfaces:**
- Consumes: Tasks 4 to 6; `cabvoice.propose` and `knowledge/speakers/` for the matrix; `projects/Speaker-cab-system/fixtures/tone-roots.json`.
- Produces: `chamber_volumes`, `mass_and_com`, `tolex_yardage`, `blank_volume_mm3(blank, clip_to=None)`, `layout(spec) -> Layout` (the orchestrator), `check_layout(layout, spec) -> list[Check]` with the check names in this order: `sheet`, `net volume`, `stereo balance`, `cutout`, `grill opening`, `port fit`, `magnet to back`, `handle`, `head match`, `line`, `jack plate`, `stock`, `part count`, `spans`; `layout_report(layout, checks) -> dict` (the `cab.json` body without `files`); `Layout.to_dict()`. `Layout.notes` carries strings prefixed `blocker: `, `warn: `, `span: ` that `check_layout` reads; `Chamber.port_air` entries are dicts of type `box` or `cylinder`.

The matrix is this plan's propose-versus-evaluate lesson: every catalog speaker x five enclosures x four driver and jack configurations x three line and joint pairs on a live `cabvoice.propose`, about 1200 cases; each lays out clean or returns a blocker from the named set, and every clean layout's net volume per chamber agrees with its sheet within 5 percent.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_cablayout.py`:

<!-- code: test_cablayout.py unit 7 -->
```python
# === TASK 7 ===
def test_site_box_volumes_hand_computed():
    spec = spec_for(external=(476.0, 457.2, 279.4), enclosure="closed", net=40.0)
    lay = L.layout(spec)
    gross = 440.0 * 421.2 * 229.4 / 1e6
    cleats = (4 * 440.0 * 18.0 * 18.0 + 4 * (421.2 - 36.0) * 18.0 * 18.0) / 1e6
    assert lay.gross_l == pytest.approx(gross)
    assert lay.net_l[0] == pytest.approx(gross - cleats - 1.5, abs=1e-6)
    assert lay.chambers[0].port_air == [] and lay.chambers[0].displacement_l == 1.5


def test_port_air_and_inside_parts_reduce_net():
    closed = L.layout(spec_for(enclosure="closed"))
    ported = L.layout(spec_for(port="round"))
    tube_wall = math.pi / 4 * (88.9 ** 2 - 77.3 ** 2) * 28.0 / 1e6
    ring = math.pi / 4 * (148.9 ** 2 - 88.9 ** 2) * 12.0 / 1e6
    bore = math.pi / 4 * 77.3 ** 2 * 28.0 / 1e6
    assert closed.net_l[0] - ported.net_l[0] == pytest.approx(tube_wall + ring + bore, abs=1e-6)
    assert ported.chambers[0].port_air[0]["type"] == "cylinder"
    slot = L.layout(spec_for(port="slot"))
    assert slot.chambers[0].port_air[0]["type"] == "box"
    assert slot.net_l[0] < closed.net_l[0]


def test_mass_and_com():
    lay = L.layout(spec_for(port="round"))
    assert abs(lay.com_mm[0]) < 2.0 and lay.com_mm[1] < 279.4 / 2 and 200 < lay.com_mm[2] < 260
    assert lay.mass_kg["speakers"] == 4.7 and lay.mass_kg["hardware"] == 1.0
    assert lay.mass_kg["total"] == pytest.approx(lay.mass_kg["parts"] + 5.7)
    assert 10.0 < lay.mass_kg["parts"] < 13.0
    hw = L.layout(spec_for(line="hardwood", species="cherry", port="round"))
    assert hw.mass_kg["parts"] < lay.mass_kg["parts"] + 0.5     # cherry is lighter than birch


def test_tolex_yardage():
    t54 = L.tolex_yardage(spec_for())
    assert t54["area_m2"] == pytest.approx(1.003869) and t54["length_m"] == pytest.approx(0.84168, abs=1e-4)
    assert t54["length_yd"] == pytest.approx(0.84168 / 0.9144, abs=1e-4)
    t32 = L.tolex_yardage(spec_for(aesthetics=L.Aesthetics(tolex_roll_in=32)))
    assert t32["length_m"] == pytest.approx(1.42030, abs=1e-4)
    assert L.tolex_yardage(spec_for(line="hardwood", species="walnut")) is None
    lay = L.layout(spec_for(aesthetics=L.Aesthetics(tolex_color="British Style Red")))
    tolex = [h for h in lay.hardware if h.item == "tolex"][0]
    assert "British Style Red" in tolex.notes and "0.84 m" in tolex.notes


CHECK_NAMES = ["sheet", "net volume", "stereo balance", "cutout", "grill opening", "port fit",
               "magnet to back", "handle", "head match", "line", "jack plate", "stock",
               "part count", "spans"]


def test_check_names_and_site_box_verdicts():
    spec = spec_for(port="round", net=42.5)
    lay = L.layout(spec)
    checks = L.check_layout(lay, spec)
    assert [c.name for c in checks] == CHECK_NAMES
    by = {c.name: c for c in checks}
    assert by["net volume"].level == "pass" and by["port fit"].level == "pass"
    assert by["cutout"].level == "pass" and by["grill opening"].level == "pass"
    assert by["magnet to back"].level == "pass" and "112.4" in by["magnet to back"].message
    assert by["spans"].level == "warn" and by["stock"].level == "pass"
    assert by["part count"].message == f"{lay.part_count} parts"


def test_sheet_check_warns_when_prediction_status_differs():
    spec = spec_for(port="round", net=42.5)
    assert {c.name: c for c in L.check_layout(L.layout(spec), spec)}["sheet"].level == "pass"
    stale = sheet(port="round", net=42.5)
    stale["prediction_status"] = "calibrated 2026-09-10"
    spec = L.order_from(stale, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["sheet"].level == "warn"
    assert by["sheet"].message == (f"sheet prediction_status 'calibrated 2026-09-10' differs "
                                   f"from the engine's '{cabvoice.PREDICTION_STATUS}'")


def test_checks_catch_violations():
    small = spec_for(external=(360.0, 360.0, 279.4), enclosure="closed", net=15.0)
    by = {c.name: c for c in L.check_layout(L.layout(small), small)}
    assert by["cutout"].level == "blocker" and "shell" in by["cutout"].message
    assert by["grill opening"].level == "blocker"
    wrong = spec_for(enclosure="closed", net=60.0)
    by = {c.name: c for c in L.check_layout(L.layout(wrong), wrong)}
    assert by["net volume"].level == "blocker"
    shallow = spec_for(external=(508.0, 457.2, 180.0), enclosure="closed", net=30.0)
    by = {c.name: c for c in L.check_layout(L.layout(shallow), shallow)}
    assert by["magnet to back"].level == "blocker"
    head = spec_for(enclosure="closed", net=42.5, aesthetics=L.Aesthetics(head_width_mm=520.0))
    by = {c.name: c for c in L.check_layout(L.layout(head), head)}
    assert by["head match"].level == "warn"
    oak = spec_for(line="hardwood", species="oak", enclosure="closed", net=42.0)
    by = {c.name: c for c in L.check_layout(L.layout(oak), oak)}
    assert by["line"].level == "blocker" and "oak" in by["line"].message


def test_stereo_layout_balances():
    st = spec_for(external=(800.0, 457.2, 279.4), drivers=2, chambers=2, jack="stereo", port="round", net=80.0)
    lay = L.layout(st)
    by = {c.name: c for c in L.check_layout(lay, st)}
    assert by["stereo balance"].level == "pass" and lay.net_l[0] == pytest.approx(lay.net_l[1])
    assert len(lay.round_ports) == 2 and lay.round_ports[0].center[0] < 0 < lay.round_ports[1].center[0]
    assert [p.name for p in lay.parts if p.name.startswith("cleat_baffle_top")] == ["cleat_baffle_top_0", "cleat_baffle_top_1"]


def test_report_and_to_dict_are_json():
    spec = spec_for(port="round", net=42.5)
    lay = L.layout(spec)
    checks = L.check_layout(lay, spec)
    rep = L.layout_report(lay, checks)
    json.dumps(rep)
    json.dumps(lay.to_dict())
    assert rep["external_in"] == [20.0, 18.0, 11.0] and rep["internal_mm"] == pytest.approx([472.0, 421.2, 229.4])
    assert rep["speakers"] == ["celestion-g12h-30-anniversary"] and rep["tolex"]["roll_in"] == 54
    assert {c["name"] for c in rep["checks"]} == set(CHECK_NAMES)
    assert rep["prediction_status"] == "unverified, ears only" and "generated" in rep


def test_fixture_site_default_lays_out():
    path = HERE / "fixtures" / "site-default" / "voicing.json"
    if not path.exists():
        pytest.skip("fixture sheet not written yet")
    spec = L.order_from(L.load_voicing(path), L.Aesthetics(tolex_color="British Style Red"))
    lay = L.layout(spec)
    by = {c.name: c for c in L.check_layout(lay, spec)}
    assert lay.spec.external_mm == (508.0, 457.2, 279.4)
    assert all(by[n].level != "blocker" for n in CHECK_NAMES), [(n, by[n].message) for n in CHECK_NAMES if by[n].level == "blocker"]


# --- matrix: every catalog speaker x enclosure x configuration x line, on live proposals
TONE = json.loads((HERE.parents[1] / "fixtures" / "tone-roots.json").read_text())
TONE["min_power_w"] = 10          # so low-power speakers pass the power check and reach the layout
ENCLOSURES = [("closed", None), ("closed-ported", None), ("closed-ported", (300.0, 40.0)),
              ("open", None), ("semi-open", None)]
CONFIGS = [(1, "mono"), (2, "mono"), (2, "mono-parallel-out"), (2, "stereo")]
LINES = [("tolex", None, "finger"), ("hardwood", "black walnut", "finger"), ("hardwood", "black walnut", "dovetail")]
ALLOWED_BLOCKERS = {"port fit", "net volume", "magnet to back"}


def test_matrix_every_configuration_lays_out_or_names_its_blocker():
    t0 = time.time()
    slugs = cabvoice.list_speakers()
    assert len(slugs) == 20
    stats = {"cases": 0, "engine_blocked": 0, "clean": 0, "blocked": 0}
    reasons = {}
    worst = (0.0, None)
    for slug in slugs:
        drv = cabvoice.load_speaker(slug)
        z = drv.impedance_ohm[0]
        for enclosure, slot in ENCLOSURES:
            for n, jack in CONFIGS:
                for line, species, joint in LINES:
                    stats["cases"] += 1
                    c = cabvoice.Constraints(line=line, species=species, port_slot_mm=slot)
                    v = cabvoice.propose([drv] * n, [z] * n, enclosure, TONE, jack, c, "matrix").to_dict()
                    aest = L.Aesthetics(corner_joint=joint)
                    if v["blockers"]:
                        stats["engine_blocked"] += 1
                        with pytest.raises(ValueError):
                            L.order_from(v, aest)
                        continue
                    # the engine must hold its own floors (hardwood floors carry the 2 mm extra)
                    w_int, h_int, _ = v["box"]["internal_mm"]
                    cut = max(s["cutout_mm"] for s in v["speakers"])
                    slot_h = v["port"]["slot_h_mm"] if (v["port"] and v["port"]["shape"] == "slot") else None
                    extra = cabvoice.HARDWOOD_FLOOR_EXTRA_MM if line == "hardwood" else 0.0
                    assert w_int >= cabvoice.min_internal_width_mm(n, cut) + extra - 1e-6, (slug, enclosure, n, jack, line)
                    assert h_int >= cabvoice.min_internal_height_mm(cut, slot_h) + extra - 1e-6, (slug, enclosure, n, jack, line)
                    spec = L.order_from(v, aest)
                    assert spec.sheet_inside_parts_l is not None
                    lay = L.layout(spec)
                    checks = L.check_layout(lay, spec)
                    blockers = [ch for ch in checks if ch.level == "blocker"]
                    by = {ch.name: ch for ch in checks}
                    # the engine's floors and the layout's margins agree everywhere, both lines
                    assert by["cutout"].level == "pass", (slug, enclosure, n, jack, line, by["cutout"].message)
                    assert by["grill opening"].level == "pass", (slug, enclosure, n, jack, line)
                    assert by["stereo balance"].level == "pass", (slug, enclosure, n, jack, line)
                    assert by["line"].level == "pass"
                    if blockers:
                        stats["blocked"] += 1
                        for b in blockers:
                            assert b.name in ALLOWED_BLOCKERS, (slug, enclosure, n, jack, line, b.name, b.message)
                            reasons[b.name] = reasons.get(b.name, 0) + 1
                    else:
                        stats["clean"] += 1
                        assert by["net volume"].level == "pass"
                        for ch in lay.chambers:
                            delta = (ch.net_l - ch.sheet_net_l) / ch.sheet_net_l * 100.0
                            assert abs(delta) <= 5.0
                            if abs(delta) > abs(worst[0]):
                                worst = (delta, (slug, enclosure, slot is not None, n, jack, line))
    print(f"\nmatrix {stats} reasons {reasons} worst net delta {worst[0]:+.2f} percent at {worst[1]} in {time.time() - t0:.1f} s")
    assert stats["cases"] == 1200
    assert stats["clean"] > 0
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest scripts/test_cablayout.py -q`
Expected: the Task 7 tests fail with `AttributeError`; earlier tests still pass.

- [ ] **Step 3: Implement**

Append to `scripts/cablayout.py`:

<!-- code: cablayout.py unit 7 -->
```python
# === TASK 7 ===
def _clip(box, cb):
    """Intersection of two ((x0,y0,z0),(x1,y1,z1)) boxes, or None."""
    lo = tuple(max(a, b) for a, b in zip(box[0], cb[0]))
    hi = tuple(min(a, b) for a, b in zip(box[1], cb[1]))
    if any(h - l <= 0 for l, h in zip(lo, hi)):
        return None
    return (lo, hi)


def _vol(box) -> float:
    if box is None:
        return 0.0
    return math.prod(h - l for l, h in zip(box[0], box[1]))


def _poly_area(poly) -> float:
    s = 0.0
    for i in range(len(poly)):
        y0, z0 = poly[i]
        y1, z1 = poly[(i + 1) % len(poly)]
        s += y0 * z1 - y1 * z0
    return abs(s) / 2.0


def feature_volume_mm3(blank: Blank, feat: dict, clip_to=None) -> float:
    """Material a feature removes from a box blank (clipped to a box when given)."""
    box = blank.box if clip_to is None else _clip(blank.box, clip_to)
    if box is None:
        return 0.0
    dx, dy, dz = (h - l for l, h in zip(box[0], box[1]))
    kind = feat["type"]
    if kind == "edge_cuts":
        x0, x1 = feat["x"]
        return sum(_poly_area(p) for p in feat["polys"]) * (x1 - x0)
    if kind == "cutout":
        return math.pi / 4.0 * feat["d"] ** 2 * dy
    if kind == "holes":
        return len(feat["centers"]) * math.pi / 4.0 * feat["d"] ** 2 * dy
    if kind == "rect_hole":
        return feat["w"] * feat["h"] * (dy if feat["axis"] == "y" else dx)
    if kind == "notch":
        return _vol(_clip(feat["box"], box))
    return 0.0


def blank_volume_mm3(blank: Blank, clip_to=None) -> float:
    """Solid volume of a blank after its features, optionally clipped to a box."""
    if blank.shape == "box":
        box = blank.box if clip_to is None else _clip(blank.box, clip_to)
        if box is None:
            return 0.0
        return _vol(box) - sum(feature_volume_mm3(blank, f, clip_to) for f in blank.features)
    cx, y0, cz = blank.pos
    od, length, id_mm = blank.size
    ya, yb = y0, y0 + length
    if clip_to is not None:
        ya, yb = max(ya, clip_to[0][1]), min(yb, clip_to[1][1])
        if yb <= ya:
            return 0.0
    return math.pi / 4.0 * (od ** 2 - id_mm ** 2) * (yb - ya)


def chamber_volumes(spec: CabSpec, fr: Frame, parts: list, rports: list, slots: list) -> list:
    out = []
    for c, (xa, xb) in enumerate(fr.chambers):
        cb = ((xa, fr.y_bb, fr.z0), (xb, fr.y_bi, fr.z1))
        gross = _vol(cb)
        inside = sum(blank_volume_mm3(p, cb) for p in parts if p.chamber == c)
        port_air, air = [], 0.0
        for s in slots:
            if s.chamber != c:
                continue
            box = ((s.x0, fr.y_bf, fr.z0), (s.x1, fr.y_bf + s.shelf_depth_mm, fr.z0 + s.slot_h_mm))
            port_air.append({"type": "box", "box": box})
            air += _vol(_clip(box, cb))
        for rp in rports:
            if rp.chamber != c:
                continue
            y0, y1 = max(rp.y0, fr.y_bb), fr.y_bi
            port_air.append({"type": "cylinder", "center": rp.center, "d": rp.id_mm, "y": (y0, y1)})
            air += math.pi / 4.0 * rp.id_mm ** 2 * max(0.0, y1 - y0)
        disp = sum(spec.speakers[i].displacement_l for i in range(spec.driver_count)
                   if _chamber_of(fr, _cutout_x(spec, fr, i)) == c)
        net = (gross - inside - air) / 1e6 - disp
        out.append(Chamber(c, cb, port_air, gross / 1e6, net, disp, spec.per_chamber_net_l))
    return out


def _cutout_x(spec: CabSpec, fr: Frame, i: int) -> float:
    return cutout_centers(spec, fr)[i][0]


def mass_and_com(spec: CabSpec, fr: Frame, parts: list, cutouts: list) -> tuple:
    """(mass dict, center of mass): blank volumes times density, speakers at
    the baffle at the cutout centers, 1 kg of hardware at the cab center."""
    total, mx, my, mz = 0.0, 0.0, 0.0, 0.0
    parts_kg = 0.0
    for p in parts:
        m = blank_volume_mm3(p) * p.density / 1e9
        (x0, y0, z0), (x1, y1, z1) = p.box
        cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
        parts_kg += m
        total += m
        mx, my, mz = mx + m * cx, my + m * cy, mz + m * cz
    speakers_kg = 0.0
    for co in cutouts:
        m = spec.speakers[co.speaker].weight_kg
        speakers_kg += m
        total += m
        mx += m * co.center[0]
        my += m * (fr.y_bf + BAFFLE_MM / 2.0)
        mz += m * co.center[1]
    total += HARDWARE_KG
    my += HARDWARE_KG * fr.D / 2.0
    mz += HARDWARE_KG * fr.H / 2.0
    com = (mx / total, my / total, mz / total)
    return {"parts": parts_kg, "speakers": speakers_kg, "hardware": HARDWARE_KG, "total": total}, com


def tolex_yardage(spec: CabSpec) -> dict | None:
    if spec.line != "tolex":
        return None
    W, H, D = spec.external_mm
    area = 2.0 * (W * H + W * D + H * D) / 1e6
    roll = ROLL_MM[spec.aesthetics.tolex_roll_in] / 1e3
    length = area * TOLEX_WASTE / roll
    return {"roll_in": spec.aesthetics.tolex_roll_in, "area_m2": area,
            "length_m": length, "length_yd": length / YARD_M}


def layout(spec: CabSpec) -> Layout:
    fr = frame(spec)
    parts = shell_blanks(spec)
    baffle, cutouts, dados = baffle_and_cutouts(spec, fr)
    for name, feat in dados.items():
        _attach(parts, name, [feat])
    parts.append(baffle)
    parts += cleat_blanks(spec, fr)
    parts += grill_frame_blanks(spec, fr)
    parts += brace_blank(spec, fr)
    parts += divider_blank(spec, fr)
    stiff, span_notes = stiffener_blanks(spec, fr)
    parts += stiff
    parts += back_blanks(spec, fr)
    envelopes = speaker_envelopes(spec, fr, cutouts)
    plates, plate_feats, plate_warn = jack_plates(spec, fr)
    for panel, feats in plate_feats.items():
        _attach(parts, panel, feats)
    slots, slot_blanks, slot_blockers = slot_ports(spec, fr)
    parts += slot_blanks
    obstacles = [p.box for p in parts
                 if p.shape == "box" and (p.chamber is not None or p.name == "divider")]
    for hw in plates:
        w, h = hw.cutout
        x, _, z = hw.position
        obstacles.append(((x - w / 2, fr.D - 40.0, z - h / 2), (x + w / 2, fr.D, z + h / 2)))
    rports, port_blanks, back_feats, port_blockers = round_ports(spec, fr, envelopes, obstacles)
    parts += port_blanks
    if back_feats:
        _attach(parts, "back", back_feats)
    chambers = chamber_volumes(spec, fr, parts, rports, slots)
    mass, com = mass_and_com(spec, fr, parts, cutouts)
    handles, handle_feats, handle_warn = handle_hardware(spec, fr, com)
    for panel, feats in handle_feats.items():
        _attach(parts, panel, feats)
    hardware = plates + handles + trim_hardware(spec, fr)
    tolex = tolex_yardage(spec)
    if tolex is not None:
        hardware.append(Hardware("tolex", (0.0, fr.D / 2.0, fr.H / 2.0), None, "",
                                 f"{spec.aesthetics.tolex_color or 'tolex color not chosen'}, "
                                 f"{tolex['roll_in']} in roll: {tolex['length_m']:.2f} m "
                                 f"({tolex['length_yd']:.2f} yd), six faces x 1.15"))
    notes = ([f"blocker: {b}" for b in slot_blockers + port_blockers]
             + [f"warn: {w}" for w in plate_warn + handle_warn]
             + [f"span: {s}" for s in span_notes])
    return Layout(spec=spec, parts=parts, cutouts=cutouts, round_ports=rports, slot_ports=slots,
                  hardware=hardware, envelopes=envelopes, chambers=chambers,
                  gross_l=sum(ch.gross_l for ch in chambers), net_l=[ch.net_l for ch in chambers],
                  mass_kg=mass, com_mm=com, tolex=tolex, part_count=len(parts), notes=notes)


def layout_inside_parts_l(lay: Layout) -> float:
    """Cleats, stiffeners, shelf, cheeks, brace, tube and ring inside the air
    boxes: gross minus net minus displacement minus port air, all chambers."""
    total = 0.0
    for ch in lay.chambers:
        air = 0.0
        for pa in ch.port_air:
            if pa["type"] == "box":
                air += _vol(_clip(pa["box"], ch.box))
            else:
                y0, y1 = pa["y"]
                air += math.pi / 4.0 * pa["d"] ** 2 * max(0.0, y1 - y0)
        total += ch.gross_l - ch.net_l - ch.displacement_l - air / 1e6
    return total


def _stock_fits(blank: Blank, spec: CabSpec) -> bool:
    if blank.shape != "box":
        return True
    t, w, l = blank.blank_mm
    limit = STOCK_HARDWOOD_MM if (spec.line == "hardwood" and "birch" not in blank.material
                                  and "PVC" not in blank.material) else STOCK_SHEET_MM
    long_, short = max(limit), min(limit)
    a, b = max(w, l), min(w, l)
    return a <= long_ + 1e-6 and b <= short + 1e-6


def check_layout(lay: Layout, spec: CabSpec) -> list:
    fr = frame(spec)
    checks = []
    if spec.prediction_status == cabvoice.PREDICTION_STATUS:
        checks.append(Check("sheet", "pass", f"prediction {spec.prediction_status}; no blockers on the sheet"))
    else:
        checks.append(Check("sheet", "warn", f"sheet prediction_status '{spec.prediction_status}' differs "
                                             f"from the engine's '{cabvoice.PREDICTION_STATUS}'"))
    # net volume
    msgs, level = [], "pass"
    for ch in lay.chambers:
        delta = (ch.net_l - ch.sheet_net_l) / ch.sheet_net_l * 100.0
        msgs.append(f"chamber {ch.index} net {ch.net_l:.1f} L vs sheet {ch.sheet_net_l:.1f} L ({delta:+.1f} percent)")
        if abs(delta) > 5.0:
            level = "blocker"
    inside = layout_inside_parts_l(lay)
    if spec.sheet_inside_parts_l is not None:
        msgs.append(f"inside parts {inside:.2f} L vs sheet allowance {spec.sheet_inside_parts_l:.2f} L")
    else:
        msgs.append(f"inside parts {inside:.2f} L (sheet carries no allowance)")
    if any(n.startswith("blocker: port fit") for n in lay.notes):
        msgs.append("port not built, so its tube and ring are missing from the inside parts")
    checks.append(Check("net volume", level, "; ".join(msgs)))
    if len(lay.chambers) == 2:
        n0, n1 = lay.chambers[0].net_l, lay.chambers[1].net_l
        diff = abs(n0 - n1) / ((n0 + n1) / 2.0) * 100.0
        checks.append(Check("stereo balance", "pass" if diff <= 1.0 else "blocker",
                            f"chambers {n0:.2f} and {n1:.2f} L differ by {diff:.2f} percent"))
    else:
        checks.append(Check("stereo balance", "pass", "single chamber"))
    # cutout margins
    problems = []
    brace = spec.driver_count == 2 and spec.chambers == 1
    for co in lay.cutouts:
        xa, xb = fr.chambers[co.chamber]
        xc, zc = co.center
        r = co.diameter / 2.0
        s = spec.speakers[co.speaker]
        if abs(co.diameter - s.cutout_mm) > 1e-6:
            problems.append(f"cutout {co.speaker} diameter {co.diameter:g} differs from the note")
        for side, gap, wall in (("left", xc - r - xa, xa == fr.x0), ("right", xb - (xc + r), xb == fr.x1)):
            need = SHELL_MARGIN_MM if wall else CUTOUT_MARGIN_MM
            what = "shell" if wall else "divider"
            if gap < need - 1e-6:
                problems.append(f"cutout {co.speaker}: {gap:.1f} mm to the {side} {what}, {need:g} needed")
        if brace:
            gap = abs(xc) - r - BRACE_MM[0] / 2.0
            if gap < CUTOUT_MARGIN_MM - 1e-6:
                problems.append(f"cutout {co.speaker}: {gap:.1f} mm to the brace, {CUTOUT_MARGIN_MM:g} needed")
        low, high = zc - r - fr.z_vis0, fr.z1 - (zc + r)
        if low < SHELL_MARGIN_MM - 1e-6:
            problems.append(f"cutout {co.speaker}: {low:.1f} mm to the baffle bottom, {SHELL_MARGIN_MM:g} needed")
        if high < SHELL_MARGIN_MM - 1e-6:
            problems.append(f"cutout {co.speaker}: {high:.1f} mm to the top, {SHELL_MARGIN_MM:g} needed")
    if len(lay.cutouts) == 2 and spec.chambers == 1:
        a, b = lay.cutouts
        gap = (b.center[0] - b.diameter / 2.0) - (a.center[0] + a.diameter / 2.0)
        if gap < CUTOUT_GAP_MM - 1e-6:
            problems.append(f"cutouts {gap:.1f} mm apart, {CUTOUT_GAP_MM:g} needed")
    checks.append(Check("cutout", "blocker" if problems else "pass",
                        "; ".join(problems) if problems else
                        f"{len(lay.cutouts)} cutout(s) at the note diameter with {SHELL_MARGIN_MM:g} mm shell margins"))
    # grill opening
    inner_x0, inner_x1 = fr.x0 + GRILL_CLEARANCE_MM + GRILL_STRIP_W_MM, fr.x1 - GRILL_CLEARANCE_MM - GRILL_STRIP_W_MM
    inner_z0, inner_z1 = fr.z_vis0 + GRILL_CLEARANCE_MM + GRILL_STRIP_W_MM, fr.z1 - GRILL_CLEARANCE_MM - GRILL_STRIP_W_MM
    problems = []
    for co in lay.cutouts:
        xc, zc = co.center
        r = co.diameter / 2.0
        if (xc - r - inner_x0 < GRILL_CLEARANCE_MM - 1e-6 or inner_x1 - (xc + r) < GRILL_CLEARANCE_MM - 1e-6
                or zc - r - inner_z0 < GRILL_CLEARANCE_MM - 1e-6 or inner_z1 - (zc + r) < GRILL_CLEARANCE_MM - 1e-6):
            problems.append(f"grill strip covers cutout {co.speaker}")
    checks.append(Check("grill opening", "blocker" if problems else "pass",
                        "; ".join(problems) if problems else "strip inner edges clear every cutout by 2 mm"))
    # port fit
    port_blockers = [n[len("blocker: "):] for n in lay.notes if n.startswith("blocker: port fit")]
    if spec.port is None:
        checks.append(Check("port fit", "pass", "no port"))
    elif port_blockers:
        checks.append(Check("port fit", "blocker", "; ".join(port_blockers)))
    elif spec.port.shape == "round":
        pos = ", ".join(f"chamber {p.chamber} at x {p.center[0]:.0f} z {p.center[1]:.0f} ({p.id_mm:g} x {p.length_mm:.0f} mm)"
                        for p in lay.round_ports)
        checks.append(Check("port fit", "pass", f"round port(s) placed with {CLEARANCE_MM:g} mm clearance: {pos}"))
    else:
        pos = ", ".join(f"chamber {s.chamber} slot {s.x1 - s.x0:.0f} x {s.slot_h_mm:g} mm, shelf {s.shelf_depth_mm:.0f} mm"
                        for s in lay.slot_ports)
        checks.append(Check("port fit", "pass", f"slot port(s) built: {pos}"))
    # magnet to back
    if spec.closed:
        problems, best = [], None
        for env in lay.envelopes:
            gap = fr.y_bi - (env.y0 + env.basket_len + env.magnet_len)
            best = gap if best is None else min(best, gap)
            if gap < CLEARANCE_MM - 1e-6:
                problems.append(f"speaker {env.speaker} magnet {gap:.1f} mm from the back, {CLEARANCE_MM:g} needed")
        checks.append(Check("magnet to back", "blocker" if problems else "pass",
                            "; ".join(problems) if problems else f"at least {best:.1f} mm behind every magnet"))
    else:
        checks.append(Check("magnet to back", "pass", "open back"))
    # handle
    handle_warn = [n[len("warn: "):] for n in lay.notes if n.startswith("warn: ") and "handle" in n]
    straps = [h for h in lay.hardware if h.item == "strap handle"]
    if straps:
        off = abs(straps[0].position[0] - lay.com_mm[0])
        level = "pass" if off <= 15.0 and not handle_warn else "warn"
        checks.append(Check("handle", level, f"strap handle {off:.1f} mm from the center of mass on the width axis"
                            + ("; " + "; ".join(handle_warn) if handle_warn else "")))
    else:
        checks.append(Check("handle", "warn" if handle_warn else "pass",
                            "; ".join(handle_warn) if handle_warn else "recessed side handles at the depth center of mass"))
    # head match
    head = spec.aesthetics.head_width_mm
    if head is None:
        checks.append(Check("head match", "pass", "no head width given"))
    else:
        d = fr.W - head
        checks.append(Check("head match", "pass" if 0.0 <= d <= 10.0 else "warn",
                            f"external width {fr.W:.0f} mm is head width {head:g} mm {d:+.0f} mm"))
    # line
    problems = []
    if spec.aesthetics.corner_joint == "dovetail" and spec.line != "hardwood":
        problems.append("dovetail corners are a hardwood option")
    if spec.line == "hardwood" and species_density(spec.species) is None:
        problems.append(f"species density unknown for {spec.species!r}")
    checks.append(Check("line", "blocker" if problems else "pass",
                        "; ".join(problems) if problems else f"{spec.line} line, {spec.wall_material}"))
    # jack plate fit
    plate_warn = [n[len("warn: "):] for n in lay.notes if n.startswith("warn: jack plate")]
    checks.append(Check("jack plate", "warn" if plate_warn else "pass",
                        "; ".join(plate_warn) if plate_warn else "plates fit above the cleat"))
    # stock
    over = [p.name for p in lay.parts if not _stock_fits(p, spec)]
    checks.append(Check("stock", "warn" if over else "pass",
                        "over stock: " + ", ".join(over) if over else "every blank fits the stock limits"))
    checks.append(Check("part count", "pass", f"{lay.part_count} parts"))
    spans = [n[len("span: "):] for n in lay.notes if n.startswith("span: ")]
    checks.append(Check("spans", "warn" if spans else "pass",
                        "; ".join(spans) if spans else f"no panel span over {SPAN_MAX_MM:.0f} mm"))
    return checks


def layout_report(lay: Layout, checks: list) -> dict:
    spec = lay.spec
    fr = frame(spec)
    W, H, D = spec.external_mm
    return {
        "name": spec.name,
        "generated": date.today().isoformat(),
        "line": spec.line, "species": spec.species,
        "corner_joint": spec.aesthetics.corner_joint,
        "baffle_mount": spec.aesthetics.baffle_mount,
        "external_mm": [W, H, D],
        "external_in": [round(v / MM_PER_INCH, 2) for v in (W, H, D)],
        "internal_mm": [fr.x1 - fr.x0, fr.z1 - fr.z0, fr.y_bi - fr.y_bb],
        "enclosure": {"type": spec.enclosure_type, "driver_count": spec.driver_count,
                      "chambers": spec.chambers, "jack_config": spec.jack_config,
                      "open_fraction": spec.open_fraction},
        "speakers": [s.slug for s in spec.speakers],
        "volumes": {"gross_l": [ch.gross_l for ch in lay.chambers],
                    "net_l": [ch.net_l for ch in lay.chambers],
                    "sheet_net_l": [ch.sheet_net_l for ch in lay.chambers],
                    "delta_pct": [(ch.net_l - ch.sheet_net_l) / ch.sheet_net_l * 100.0 for ch in lay.chambers],
                    "inside_parts_l": layout_inside_parts_l(lay),
                    "sheet_inside_parts_l": spec.sheet_inside_parts_l},
        "mass": {"total_kg": lay.mass_kg["total"], "parts_kg": lay.mass_kg["parts"],
                 "speakers_kg": lay.mass_kg["speakers"], "hardware_kg": lay.mass_kg["hardware"],
                 "com_mm": list(lay.com_mm)},
        "hardware": [{"item": h.item, "position_mm": list(h.position),
                      "cutout_mm": None if h.cutout is None else list(h.cutout),
                      "panel": h.panel, "notes": h.notes} for h in lay.hardware],
        "tolex": lay.tolex,
        "parts": [{"name": p.name, "qty": p.qty, "blank_mm": list(p.blank_mm),
                   "material": p.material, "notes": p.notes} for p in lay.parts],
        "checks": [{"name": c.name, "level": c.level, "message": c.message} for c in checks],
        "prediction_status": spec.prediction_status,
    }
```
<!-- /code -->

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest scripts/test_cablayout.py -q`
Expected: `41 passed` in under 60 seconds.

- [ ] **Step 5: Commit**

```bash
git add scripts/cablayout.py scripts/test_cablayout.py
git commit -m "cablayout: chambers, volumes, mass, tolex, checks, report, layout(), 1200-case matrix" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 8: CAD layer, part 1: blanks to solids, finger and dovetail combs

**Files:**
- Create: `scripts/cabmodel.py`
- Create: `scripts/test_cabmodel.py`

**Interfaces:**
- Consumes: `cablayout.Blank` (shape box, tube, ring; pos, size, features) and the feature vocabulary (`edge_cuts`, `cutout`, `holes`, `rect_hole`, `notch`); `cablayout.shell_blanks`, `finger_schedule`, `dovetail_schedule` for the tests.
- Produces: `feature_tool(blank, feat)` (one cutting tool per feature, grown 1 mm past the blank's faces, quads forced counter-clockwise), `blank_solid(blank)` (a build123d solid for one blank with every feature subtracted), `part_entry(blank, solid) -> dict` (the furniture `PARTS` shape with `dims` set to `blank.blank_mm`), `compound_of(solids)`, `render(solids, png_path, views=None)` (writes a temporary STL and calls `render_stl.py` next to the module), and the demo machinery `demo(name)` (`site-box`, `2x12-mono-slot`, `2x12-stereo-dovetail`, `open-1x12`, each a live engine call on eminence-cannabis-rex), `render_kind(kind, layout, png_path)`, `main(argv=None)`; the `__main__` guard lands with Task 11, so until then the render steps call `main` directly. Exact signatures are in the code below.

The tests build the four shell blanks of the site box in tolex finger, hardwood finger, and hardwood dovetail form and prove the union of the four solids has exactly the shell volume with no overlaps (union volume equals the sum of the blank volumes minus the four corner blocks) and that every finger or tail is present (solid volume of each panel equals its blank volume minus the schedule's removed area times the thickness).

- [ ] **Step 1: Write the failing tests**

<!-- code: test_cabmodel.py unit 8 -->
```python
"""Tests for cabmodel.py (Plan 2 Tasks 8 to 12). Run from the mirror root:
.venv/bin/python -m pytest test_cabmodel.py -q  (CAB_FULL_MATRIX=1 for all sixty builds)"""
import copy
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
SCRIPTS = HERE.parents[3] / "scripts"
if not (HERE / "cabvoice.py").exists() and str(SCRIPTS) not in sys.path:
    sys.path.insert(1, str(SCRIPTS))

import cabvoice  # noqa: E402
import cablayout as L  # noqa: E402
import cabmodel as M  # noqa: E402

# === TASK 8 ===
SPEAKER = {"slug": "celestion-g12h-30-anniversary", "cutout_mm": 283, "bolt_circle_mm": 297,
           "bolt_count": 4, "depth_mm": 135, "weight_kg": 4.7, "displacement_l": 1.5,
           "frame_diameter_mm": 309, "magnet_diameter_mm": 156, "magnet_diameter_estimated": False}


def sheet(external=(508.0, 457.2, 279.4), enclosure="closed-ported", drivers=1, chambers=1,
          jack="mono", line="tolex", species=None, port=None, net=43.5, open_fraction=None):
    W, H, D = external
    internal = [W - 36.0, H - 36.0, D - 50.0]
    if port == "round":
        port = {"shape": "round", "diameter_mm": 77.3, "slot_w_mm": None, "slot_h_mm": None,
                "length_mm": 40.0, "location": "rear", "count": drivers // chambers}
    elif port == "slot":
        port = {"shape": "slot", "diameter_mm": None, "slot_w_mm": 300.0, "slot_h_mm": 40.0,
                "length_mm": 60.0, "location": "front", "count": drivers // chambers}
    return {"name": "test", "blockers": [], "prediction_status": "unverified, ears only",
            "enclosure": {"type": enclosure, "driver_count": drivers, "chambers": chambers,
                          "jack_config": jack, "open_fraction": open_fraction},
            "box": {"external_mm": list(external), "internal_mm": internal},
            "construction": {"panel_mm": 18.0, "back_mm": 12.0, "baffle_mm": 18.0, "recess_mm": 20.0,
                             "line": line, "species": species,
                             "wall_material": "baltic birch plywood" if line == "tolex" else species},
            "volumes": {"net_total_l": net, "per_chamber_net_l": net / chambers},
            "speakers": [dict(SPEAKER) for _ in range(drivers)], "port": port}


def spec_for(**kw):
    aest = kw.pop("aesthetics", None) or L.Aesthetics()
    return L.order_from(sheet(**kw), aest)


def _union(solids):
    u = solids[0]
    for s in solids[1:]:
        u = u + s
    return u


@pytest.mark.parametrize("line,species,joint", [("tolex", None, "finger"),
                                                ("hardwood", "black walnut", "finger"),
                                                ("hardwood", "black walnut", "dovetail")])
def test_shell_solids_match_the_layout_and_interleave(line, species, joint):
    spec = spec_for(line=line, species=species, aesthetics=L.Aesthetics(corner_joint=joint))
    blanks = L.shell_blanks(spec)
    solids = [M.blank_solid(b) for b in blanks]
    for b, s in zip(blanks, solids):
        assert len(s.solids()) == 1 and s.label == b.name
        # every finger or tail present: the CAD volume equals the analytic blank volume
        assert abs(s.volume - L.blank_volume_mm3(b)) < 1.0, b.name
    W, H, D = spec.external_mm
    t = spec.shell_mm
    full = 2 * t * D * H + 2 * t * D * W
    corner_blocks = 4 * t * t * D
    union = _union(solids)
    assert len(union.solids()) == 1
    assert abs(union.volume - (full - corner_blocks)) < 1.0
    assert abs(union.volume - sum(s.volume for s in solids)) < 1.0    # no overlap anywhere


def test_feature_tools_grow_past_blank_faces():
    b = L.Blank("probe", 1, "baltic birch 18 mm", 680.0, pos=(0.0, 0.0, 0.0), size=(100.0, 50.0, 18.0),
                features=[{"type": "notch", "box": ((0.0, 0.0, 0.0), (10.0, 10.0, 18.0))},
                          {"type": "rect_hole", "axis": "y", "center": (50.0, 9.0), "w": 20.0, "h": 6.0},
                          {"type": "holes", "centers": [(80.0, 9.0)], "d": 6.5}])
    s = M.blank_solid(b)
    expected = 100 * 50 * 18 - 10 * 10 * 18 - 20 * 6 * 50 - math.pi / 4 * 6.5 ** 2 * 50
    assert abs(s.volume - expected) < 0.5
    assert abs(s.volume - L.blank_volume_mm3(b)) < 0.5
    bb = s.bounding_box()
    assert abs(bb.min.X) < 1e-6 and abs(bb.max.X - 100.0) < 1e-6   # tools never scar the outside


def test_tube_and_ring_solids():
    tube = L.Blank("port_tube_0_0", 1, "PVC 3 in sch 40", 1400.0, shape="tube",
                   pos=(0.0, 200.0, 100.0), size=(88.9, 60.0, 77.3), blank_mm=(0.0, 88.9, 60.0))
    ring = L.Blank("port_ring_0_0", 1, "baltic birch 12 mm", 680.0, shape="ring",
                   pos=(0.0, 248.0, 100.0), size=(148.9, 12.0, 88.9), blank_mm=(12.0, 148.9, 148.9))
    for b in (tube, ring):
        s = M.blank_solid(b)
        assert abs(s.volume - L.blank_volume_mm3(b)) < 1.0
        bb = s.bounding_box()
        assert abs(bb.min.Y - b.pos[1]) < 1e-6 and abs(bb.max.Y - (b.pos[1] + b.size[1])) < 1e-6


def test_part_entry_carries_blank_dims_for_the_cut_list():
    spec = spec_for()
    b = L.shell_blanks(spec)[0]
    e = M.part_entry(b, M.blank_solid(b))
    assert e["dims"] == b.blank_mm and e["length_axis"] == "Y" and e["material"] == b.material
    assert "finger joint" in e["notes"]


def test_render_writes_a_png(tmp_path):
    spec = spec_for()
    png = M.render([M.blank_solid(b) for b in L.shell_blanks(spec)], tmp_path / "shell.png",
                   views=[(30, -60)])
    assert png.exists() and png.stat().st_size > 10_000
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: collection error, `ModuleNotFoundError: No module named 'cabmodel'`

- [ ] **Step 3: Implement**

Create `scripts/cabmodel.py` with exactly this content:

<!-- code: cabmodel.py unit 8 -->
```python
"""cabmodel.py: build123d CAD layer for MaximoCabs guitar speaker cabinets.

Places one named solid per blank from a cablayout.Layout, proves the solids
agree with the layout (measured air volume, boolean interference, part
count), and exports STEP, renders, the cut list with the tolex line, and
cab.json. The numbers all live in cablayout.py; nothing here decides a
dimension.

Coordinate frame as in cablayout: X width centered at 0, Y depth with the
external front face at 0 and positive toward the back, Z height from the
floor. Algebra mode throughout; every cutting tool is grown 1 mm past a
blank face it coincides with.

Per-feature renders during a build: scripts/cabmodel.py --render shell
--demo site-box --out /tmp/cab-shell.png (also interior, rear, assembly,
exploded; demos site-box, 2x12-mono-slot, 2x12-stereo-dovetail, open-1x12).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from build123d import (Align, Box, Compound, Cylinder, Plane, Polygon, Pos, Rot,
                       export_step, export_stl, extrude)

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import cablayout as L  # noqa: E402
import cabvoice  # noqa: E402
import cutlist  # noqa: E402

# === TASK 8 ===
TOOL_EXTRA_MM = 1.0                     # cutting tools grow past coincident faces
RENDER_SCRIPT = HERE / "render_stl.py"
RENDER_VIEWS = {"iso": (30, -60), "front": (0, -90), "top": (90, -90), "right": (0, 0)}
MIN_ALIGN = (Align.MIN, Align.MIN, Align.MIN)
SHELL_NAMES = ("side_left", "side_right", "top", "bottom")
INTERIOR_PREFIXES = ("baffle", "cleat_", "grill_", "brace", "divider", "stiffener_", "shelf", "cheek_")
BACK_PREFIX = "back"
PORT_PREFIXES = ("port_tube", "port_ring")


def _box(x0, y0, z0, x1, y1, z1):
    """Axis-aligned box between two corners."""
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN_ALIGN)


def _cyl_y(cx, cz, d, y0, y1):
    """Cylinder of diameter d along +Y from y0 to y1, axis through (cx, cz)."""
    return Pos(cx, y0, cz) * Rot(X=-90) * Cylinder(d / 2.0, y1 - y0,
                                                    align=(Align.CENTER, Align.CENTER, Align.MIN))


def _ccw(poly):
    """Counter-clockwise vertex order, so the extrusion follows the plane normal."""
    area = 0.0
    for i in range(len(poly)):
        y0, z0 = poly[i]
        y1, z1 = poly[(i + 1) % len(poly)]
        area += y0 * z1 - y1 * z0
    return list(poly) if area > 0 else list(reversed(poly))


def _prism_x(polys, x0, x1):
    """Union of prisms along X over [x0, x1] from quadrilaterals in the YZ plane."""
    tool = None
    for poly in polys:
        p = Pos(x0, 0.0, 0.0) * extrude(Plane.YZ * Polygon(*_ccw(poly), align=None), amount=x1 - x0)
        tool = p if tool is None else tool + p
    return tool


def _grown(lo, hi, blank_lo, blank_hi):
    """Extend a tool range 1 mm past every blank face it reaches."""
    eps = 1e-6
    lo2 = lo - TOOL_EXTRA_MM if lo <= blank_lo + eps else lo
    hi2 = hi + TOOL_EXTRA_MM if hi >= blank_hi - eps else hi
    return lo2, hi2


def _grow_polys(polys, blank):
    """Push each quad's outer-face vertices 1 mm past the blank's z faces,
    following the slope of the edge that leads to the shoulder (so a dovetail
    pin keeps its flare), and its end vertices 1 mm past the blank's y faces."""
    (_, y0, z0), (_, y1, z1) = blank.box
    eps = 1e-6
    out = []
    for poly in polys:
        n = len(poly)
        q = []
        for i, (y, z) in enumerate(poly):
            y2, z2 = y, z
            outer = z <= z0 + eps or z >= z1 - eps
            if outer:
                # the neighbor at the shoulder sets the direction to extend along
                for j in (i - 1, i + 1):
                    ny, nz = poly[j % n]
                    if abs(nz - z) > eps:
                        dz = -TOOL_EXTRA_MM if z <= z0 + eps else TOOL_EXTRA_MM
                        y2 = y + (y - ny) / (z - nz) * dz
                        z2 = z + dz
                        break
            if y <= y0 + eps:
                y2 = y2 - TOOL_EXTRA_MM
            elif y >= y1 - eps:
                y2 = y2 + TOOL_EXTRA_MM
            q.append((y2, z2))
        out.append(q)
    return out


def feature_tool(blank, feat):
    """The build123d solid a feature removes from a box blank."""
    (bx0, by0, bz0), (bx1, by1, bz1) = blank.box
    kind = feat["type"]
    if kind == "edge_cuts":
        x0, x1 = _grown(feat["x"][0], feat["x"][1], bx0, bx1)
        return _prism_x(_grow_polys(feat["polys"], blank), x0, x1)
    if kind == "cutout":
        cx, cz = feat["center"]
        return _cyl_y(cx, cz, feat["d"], by0 - TOOL_EXTRA_MM, by1 + TOOL_EXTRA_MM)
    if kind == "holes":
        tool = None
        for (cx, cz) in feat["centers"]:
            h = _cyl_y(cx, cz, feat["d"], by0 - TOOL_EXTRA_MM, by1 + TOOL_EXTRA_MM)
            tool = h if tool is None else tool + h
        return tool
    if kind == "rect_hole":
        w, h = feat["w"], feat["h"]
        if feat["axis"] == "y":
            cx, cz = feat["center"]
            return _box(cx - w / 2, by0 - TOOL_EXTRA_MM, cz - h / 2, cx + w / 2, by1 + TOOL_EXTRA_MM, cz + h / 2)
        cy, cz = feat["center"]
        return _box(bx0 - TOOL_EXTRA_MM, cy - w / 2, cz - h / 2, bx1 + TOOL_EXTRA_MM, cy + w / 2, cz + h / 2)
    if kind == "notch":
        (x0, y0, z0), (x1, y1, z1) = feat["box"]
        x0, x1 = _grown(x0, x1, bx0, bx1)
        y0, y1 = _grown(y0, y1, by0, by1)
        z0, z1 = _grown(z0, z1, bz0, bz1)
        return _box(x0, y0, z0, x1, y1, z1)
    raise ValueError(f"unknown feature type {kind!r} on {blank.name}")


def _largest_solid(shape):
    solids = shape.solids()
    if not solids:
        raise ValueError("boolean left no solid")
    return max(solids, key=lambda s: s.volume)


def blank_solid(blank):
    """One build123d solid for a cablayout.Blank (box, tube, or ring) with
    every feature subtracted; keeps the largest solid after the booleans."""
    if blank.shape == "box":
        (x0, y0, z0), (x1, y1, z1) = blank.box
        solid = _box(x0, y0, z0, x1, y1, z1)
        for feat in blank.features:
            solid = solid - feature_tool(blank, feat)
    else:
        cx, y0, cz = blank.pos
        od, length, id_mm = blank.size
        solid = _cyl_y(cx, cz, od, y0, y0 + length)
        if id_mm > 0:
            solid = solid - _cyl_y(cx, cz, id_mm, y0 - TOOL_EXTRA_MM, y0 + length + TOOL_EXTRA_MM)
    out = _largest_solid(solid)
    out.label = blank.name
    return out


def part_entry(blank, solid):
    """Furniture PARTS registry entry: the cut list reads dims (the rectangular
    blank), the assembly and STEP read the solid."""
    entry = {"name": blank.name, "solid": solid, "dims": tuple(blank.blank_mm),
             "qty": blank.qty, "material": blank.material, "notes": blank.notes}
    if blank.length_axis:
        entry["length_axis"] = blank.length_axis
    return entry


def compound_of(solids):
    return Compound(children=list(solids))


def render(solids, png_path, views=None):
    """Write a temporary STL of the solids and render it with render_stl.py.
    views: list of (elev, azim); None renders the script's four default views."""
    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        stl = Path(tmp) / "render.stl"
        export_stl(compound_of(solids), str(stl))
        cmd = [sys.executable, str(RENDER_SCRIPT), str(stl), str(png_path)]
        if views:
            cmd += [f"{e},{a}" for e, a in views]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    return png_path


def _vault_root() -> Path:
    """First ancestor holding the speaker cab fixtures (the vault root; in the
    Plan 2 mirror the mirror's own .vault copy)."""
    rel = Path("projects/Speaker-cab-system/fixtures/tone-roots.json")
    for base in (HERE / ".vault", HERE, *HERE.parents):
        if (base / rel).exists():
            return base
    raise FileNotFoundError(f"no {rel} above {HERE}")


DEMO_SPEAKER = "eminence-cannabis-rex"
DEMO_AMP_W = 30.0


def _tone() -> dict:
    tone = json.loads((_vault_root() / "projects/Speaker-cab-system/fixtures/tone-roots.json").read_text())
    tone["min_power_w"] = DEMO_AMP_W       # a 30 W amp: the demo speaker passes the power check clean
    return tone


def demo(name: str):
    """A cablayout.Layout for a named demo configuration, voiced live by the
    engine on the Cannabis Rex: site-box (evaluate, 1x12 closed-ported round
    101.5 x 40 mm), 2x12-mono-slot, 2x12-stereo-dovetail, open-1x12."""
    tone = _tone()
    drv = cabvoice.load_speaker(DEMO_SPEAKER)
    z = drv.impedance_ohm[0]
    aest = L.Aesthetics(tolex_color="Fender Style Black", grill_cloth="British Small Weave Cane")
    if name == "site-box":
        port = cabvoice.port_dims(1.0, 1.0, diameter_mm=101.5)
        port.length_mm, port.warnings = 40.0, []
        v = cabvoice.evaluate([drv], [z], "closed-ported", tone, (472.0, 421.2, 229.4), "mono",
                              port, cabvoice.Constraints(line="tolex"), "site-box")
    elif name == "2x12-mono-slot":
        c = cabvoice.Constraints(line="tolex", port_slot_mm=(300.0, 40.0))
        first = cabvoice.propose([drv, drv], [z, z], "closed-ported", tone, "mono", c, name)
        w_int = first.to_dict()["box"]["internal_mm"][0]
        c.port_slot_mm = ((w_int - L.DIVIDER_MM) / 2.0 - 1.0, 40.0)
        v = cabvoice.propose([drv, drv], [z, z], "closed-ported", tone, "mono", c, name)
    elif name == "2x12-stereo-dovetail":
        c = cabvoice.Constraints(line="hardwood", species="black walnut")
        v = cabvoice.propose([drv, drv], [z, z], "closed", tone, "stereo", c, name)
        aest = L.Aesthetics(corner_joint="dovetail", finish="oil")
    elif name == "open-1x12":
        v = cabvoice.propose([drv], [z], "open", tone, "mono", cabvoice.Constraints(line="tolex"), name)
    else:
        raise ValueError(f"unknown demo {name!r}; use site-box, 2x12-mono-slot, 2x12-stereo-dovetail, open-1x12")
    return L.layout(L.order_from(v.to_dict(), aest))


RENDER_KINDS = ("shell", "interior", "rear", "assembly", "exploded")


def render_kind(kind: str, layout, png_path):
    """Per-feature renders for the build loop; later kinds need the later
    task units (interior_solids, back_solids, build, exploded)."""
    g = globals()
    if kind == "shell":
        solids = [blank_solid(b) for b in layout.parts if b.name in SHELL_NAMES]
        return render(solids, png_path, views=[(30, -60), (20, -150)])
    if kind == "interior":
        return render(list(g["interior_solids"](layout).values()), png_path, views=[(25, -60), (15, 120)])
    if kind == "rear":
        solids = list(g["back_solids"](layout).values()) + list(g["port_solids"](layout).values())
        comps = g["component_solids"](layout)
        solids += [v for k, v in comps.items() if k.startswith("speaker_") or k.startswith("jack_plate_")]
        solids += [blank_solid(b) for b in layout.parts if b.name in ("brace", "divider")]
        return render(solids, png_path, views=[(20, 140), (0, 90)])
    if kind == "assembly":
        cab = g["build"](layout)
        return render([e["solid"] for e in cab.parts] + list(cab.components.values()), png_path)
    if kind == "exploded":
        cab = g["build"](layout)
        return render([g["exploded"](cab)], png_path, views=[(30, -60)])
    raise ValueError(f"unknown render kind {kind!r}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Per-feature renders of a demo cabinet")
    ap.add_argument("--render", choices=RENDER_KINDS, required=True)
    ap.add_argument("--demo", default="site-box")
    ap.add_argument("--out", required=True, help="PNG path")
    args = ap.parse_args(argv)
    png = render_kind(args.render, demo(args.demo), args.out)
    print(f"rendered {args.render} of {args.demo} -> {png}")
    return 0
```
<!-- /code -->

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: `7 passed`

- [ ] **Step 5: Render and view**

Run (the `__main__` guard lands with Task 11, so call `main` directly until then): `.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); import cabmodel as M; M.main(['--render', 'shell', '--demo', 'site-box', '--out', '/tmp/cab-shell.png'])"` and `.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); import cabmodel as M; M.main(['--render', 'shell', '--demo', '2x12-stereo-dovetail', '--out', '/tmp/cab-shell-dovetail.png'])"`
Then view the PNG with the Read tool. Expected: four panels forming an open box, fingers visible at all four corners (or dovetails, tails on the sides, when the aesthetics say so), no gaps, no doubled material at the corners.

- [ ] **Step 6: Commit**

```bash
git add scripts/cabmodel.py scripts/test_cabmodel.py
git commit -m "cabmodel: blanks to solids, finger and dovetail combs, render helper" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 9: CAD layer, part 2: baffle with cutouts and bolt holes, cleats, grill frame, brace, divider, stiffeners

**Files:**
- Modify: `scripts/cabmodel.py` (append after the Task 8 unit)
- Modify: `scripts/test_cabmodel.py` (append after the Task 8 tests)

**Interfaces:**
- Consumes: Task 8 `blank_solid`; Task 5 builders.
- Produces: `is_interior(name)`, `is_back(name)`, `is_port(name)` (blank-name classifiers), `interior_solids(layout) -> dict` for every interior blank (baffle, cleats, grill strips, brace, divider, stiffeners, shelf, cheeks) keyed by blank name, `overlap_volume(a, b) -> float` (bounding-box prefilter, then the boolean intersection volume) and `assert_no_overlap(a, b, tol_mm3=1.0) -> float` (asserts and returns it) used by every later interference check. Exact signatures are in the code below.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_cabmodel.py`:

<!-- code: test_cabmodel.py unit 9 -->
```python
# === TASK 9 ===
def _layout_2x12_slot():
    spec = spec_for(drivers=2, port="slot", net=74.0, external=(760.0, 480.0, 300.0))
    return spec, L.layout(spec)


def test_interior_solids_match_their_blanks_and_never_overlap():
    spec, lay = _layout_2x12_slot()
    inter = M.interior_solids(lay)
    names = sorted(inter)
    assert {"baffle", "brace", "shelf", "cheek_center_0", "cheek_left", "cheek_right",
            "grill_top", "grill_bottom", "grill_left", "grill_right",
            "cleat_baffle_top", "cleat_baffle_left", "cleat_baffle_right",
            "cleat_back_top", "cleat_back_bottom", "cleat_back_left", "cleat_back_right",
            "stiffener_back"} == set(names)
    by = {p.name: p for p in lay.parts}
    for name, s in inter.items():
        assert len(s.solids()) == 1, name
        assert abs(s.volume - L.blank_volume_mm3(by[name])) < 1.0, name
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert M.assert_no_overlap(inter[a], inter[b]) <= 1.0, (a, b)


def test_baffle_volume_with_cutouts_and_bolts_is_analytic():
    spec, lay = _layout_2x12_slot()
    baffle = next(p for p in lay.parts if p.name == "baffle")
    s = M.blank_solid(baffle)
    dx, dy, dz = baffle.size
    holes = sum(len(f["centers"]) for f in baffle.features if f["type"] == "holes")
    cutouts = [f["d"] for f in baffle.features if f["type"] == "cutout"]
    expected = dx * dy * dz - sum(math.pi / 4 * d ** 2 * dy for d in cutouts) \
        - holes * math.pi / 4 * L.BOLT_HOLE_MM ** 2 * dy
    assert len(cutouts) == 2 and holes == 8
    assert abs(s.volume - expected) < 1.0


def test_brace_notch_and_grill_half_laps():
    spec, lay = _layout_2x12_slot()
    by = {p.name: p for p in lay.parts}
    brace = M.blank_solid(by["brace"])
    bw, bd = L.BRACE_MM
    _, _, bz = by["brace"].size
    notch = bw * (L.CLEAT_MM - L.BRACE_SETBACK_MM) * L.CLEAT_MM     # top cleat notch only (slot: no bottom cleat)
    assert abs(brace.volume - (bw * bd * bz - notch)) < 1.0
    strips = {n: M.blank_solid(by[n]) for n in ("grill_top", "grill_bottom", "grill_left", "grill_right")}
    union = _union(list(strips.values()))
    assert len(union.solids()) == 1
    assert abs(union.volume - sum(s.volume for s in strips.values())) < 1.0
    t, w = L.GRILL_STRIP_T_MM, L.GRILL_STRIP_W_MM
    lap = w * w * t / 2.0
    top = by["grill_top"]
    assert abs(strips["grill_top"].volume - (top.size[0] * t * w - 2 * lap)) < 1.0


def test_overlap_volume_reports_real_collisions():
    a = M._box(0, 0, 0, 10, 10, 10)
    b = M._box(5, 0, 0, 15, 10, 10)
    c = M._box(10, 0, 0, 20, 10, 10)
    assert abs(M.overlap_volume(a, b) - 500.0) < 1e-6
    assert M.assert_no_overlap(a, c) < 1e-6
    with pytest.raises(AssertionError):
        M.assert_no_overlap(a, b)
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: the Task 9 tests fail with `AttributeError`; Task 8 tests still pass.

- [ ] **Step 3: Implement**

Append to `scripts/cabmodel.py`:

<!-- code: cabmodel.py unit 9 -->
```python
# === TASK 9 ===
def is_interior(name: str) -> bool:
    return name.startswith(INTERIOR_PREFIXES)


def is_back(name: str) -> bool:
    return name.startswith(BACK_PREFIX)


def is_port(name: str) -> bool:
    return name.startswith(PORT_PREFIXES)


def _solids_for(layout, keep) -> dict:
    out = {}
    for blank in layout.parts:
        if keep(blank.name):
            out[blank.name] = blank_solid(blank)
    return out


def interior_solids(layout) -> dict:
    """Solids for every interior blank (baffle, cleats, grill strips, brace,
    divider, stiffeners, shelf, cheeks), keyed by blank name."""
    return _solids_for(layout, is_interior)


def overlap_volume(a, b) -> float:
    """Boolean intersection volume of two shapes, 0 for an empty result."""
    try:
        cut = a & b
    except Exception:
        return 0.0
    if cut is None:
        return 0.0
    try:
        return float(cut.volume)
    except Exception:
        return 0.0


def _bbox_overlap(a, b, margin=0.5) -> bool:
    ba, bb = a.bounding_box(), b.bounding_box()
    return (ba.min.X < bb.max.X + margin and bb.min.X < ba.max.X + margin
            and ba.min.Y < bb.max.Y + margin and bb.min.Y < ba.max.Y + margin
            and ba.min.Z < bb.max.Z + margin and bb.min.Z < ba.max.Z + margin)


def assert_no_overlap(a, b, tol_mm3=1.0) -> float:
    """Intersection volume of a and b; AssertionError above tol_mm3. Touching
    faces intersect in a zero-volume sliver, so 1 mm3 is the working tolerance."""
    if not _bbox_overlap(a, b):
        return 0.0
    v = overlap_volume(a, b)
    assert v <= tol_mm3, f"{getattr(a, 'label', '?')} overlaps {getattr(b, 'label', '?')} by {v:.1f} mm3"
    return v
```
<!-- /code -->

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: `11 passed`

- [ ] **Step 5: Render and view**

Run: `.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); import cabmodel as M; M.main(['--render', 'interior', '--demo', '2x12-mono-slot', '--out', '/tmp/cab-interior.png'])"`
Then view the PNG with the Read tool. Expected: a 2x12 mono baffle with two cutouts and bolt holes, the center brace behind it notched around the cleats, the grill frame strips in front with half-lap corners, cleats along all four edges.

- [ ] **Step 6: Commit**

```bash
git add scripts/cabmodel.py scripts/test_cabmodel.py
git commit -m "cabmodel: baffle, cutouts, bolt holes, cleats, grill frame, brace, divider, stiffeners" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 10: CAD layer, part 3: backs, port tubes and flange rings, slot shelf, speaker envelopes, jack plate and handle components

**Files:**
- Modify: `scripts/cabmodel.py` (append after the Task 9 unit)
- Modify: `scripts/test_cabmodel.py` (append after the Task 9 tests)

**Interfaces:**
- Consumes: Tasks 8 and 9; Task 6 builders.
- Produces: `back_solids(layout) -> dict`, `port_solids(layout) -> dict` (tubes and rings from tube and ring blanks), `envelope_solid(env)` (the stepped cylinder plus the flange disc in front of the baffle), `component_solids(layout) -> dict` (speaker envelopes, jack plates as 2 mm plates in their cutouts, the strap handle or 12 mm recessed handle blocks, feet; placeholders for the render and the interference checks, never in the cut list). Exact signatures are in the code below.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_cabmodel.py`:

<!-- code: test_cabmodel.py unit 10 -->
```python
# === TASK 10 ===
def test_back_and_port_solids_site_box():
    spec = spec_for(port="round")
    lay = L.layout(spec)
    backs, ports = M.back_solids(lay), M.port_solids(lay)
    assert set(backs) == {"back"} and set(ports) == {"port_tube_0_0", "port_ring_0_0"}
    by = {p.name: p for p in lay.parts}
    for name, s in list(backs.items()) + list(ports.items()):
        assert abs(s.volume - L.blank_volume_mm3(by[name])) < 1.0, name
    rp = lay.round_ports[0]
    back = backs["back"]
    W, H, D = spec.external_mm
    # the back carries the tube hole and the jack plate hole
    plate_w, plate_h = spec.aesthetics.jack_plate_cutout_mm
    full = (W - 36.0) * L.BACK_MM * (H - 36.0)
    expected = full - math.pi / 4 * rp.od_mm ** 2 * L.BACK_MM - plate_w * plate_h * L.BACK_MM
    assert abs(back.volume - expected) < 1.0
    for p in ports.values():
        assert M.assert_no_overlap(back, p) < 1.0


def test_open_back_panels():
    spec = spec_for(enclosure="open", port=None, open_fraction=0.4)
    lay = L.layout(spec)
    backs = M.back_solids(lay)
    assert set(backs) == {"back_upper", "back_lower"}
    h_p = L.open_panel_height(spec, L.frame(spec))
    for name, s in backs.items():
        bb = s.bounding_box()
        assert abs((bb.max.Z - bb.min.Z) - h_p) < 1e-6
    assert M.assert_no_overlap(backs["back_upper"], backs["back_lower"]) < 1e-6


def test_envelope_stepped_cylinder_and_components():
    spec = spec_for(port="round")
    lay = L.layout(spec)
    env = lay.envelopes[0]
    s = M.envelope_solid(env)
    expected = (math.pi / 4 * env.basket_d ** 2 * env.basket_len
                + math.pi / 4 * env.magnet_d ** 2 * env.magnet_len
                + math.pi / 4 * env.flange_d ** 2 * env.flange_t)
    assert abs(s.volume - expected) < 1.0
    bb = s.bounding_box()
    assert abs(bb.min.Y - (env.y0 - env.flange_t)) < 1e-6
    assert abs(bb.max.Y - (env.y0 + env.basket_len + env.magnet_len)) < 1e-6
    comps = M.component_solids(lay)
    assert {"speaker_0", "jack_plate_0", "strap_handle", "foot_0", "foot_1", "foot_2", "foot_3"} == set(comps)
    spec2 = spec_for(port="round", aesthetics=L.Aesthetics(handle="recessed-side"))
    comps2 = M.component_solids(L.layout(spec2))
    assert {"recessed_handle_left", "recessed_handle_right"} <= set(comps2)
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: the Task 10 tests fail with `AttributeError`; earlier tests still pass.

- [ ] **Step 3: Implement**

Append to `scripts/cabmodel.py`:

<!-- code: cabmodel.py unit 10 -->
```python
# === TASK 10 ===
FOOT_H_MM = 16.0
PLATE_T_MM = 2.0
STRAP_T_MM = 25.0
STRAP_W_MM = 25.0
STRAP_EXTRA_MM = 40.0
RECESSED_DEPTH_MM = 12.0


def back_solids(layout) -> dict:
    """Closed back or the two open-back panels, keyed by blank name."""
    return _solids_for(layout, is_back)


def port_solids(layout) -> dict:
    """Port tubes and flange rings, keyed by blank name."""
    return _solids_for(layout, is_port)


def envelope_solid(env) -> object:
    """Stepped cylinder behind the baffle (basket, then magnet with its cover
    allowance) plus the flange disc in front of it."""
    solid = _cyl_y(env.center[0], env.center[1], env.basket_d, env.y0, env.y0 + env.basket_len)
    if env.magnet_len > 0:
        y0 = env.y0 + env.basket_len
        solid = solid + _cyl_y(env.center[0], env.center[1], env.magnet_d, y0, y0 + env.magnet_len)
    solid = solid + _cyl_y(env.center[0], env.center[1], env.flange_d, env.y0 - env.flange_t, env.y0)
    return _largest_solid(solid)


def component_solids(layout) -> dict:
    """Placeholders for the render and the interference checks, never in the
    cut list: speaker envelopes, jack plates, the handle, the feet."""
    spec = layout.spec
    fr = L.frame(spec)
    out = {}
    for env in layout.envelopes:
        s = envelope_solid(env)
        s.label = f"speaker_{env.speaker}"
        out[s.label] = s
    n_plate = 0
    for hw in layout.hardware:
        if hw.item == "jack plate":
            w, h = hw.cutout
            x, _, z = hw.position
            s = _box(x - w / 2, fr.D - PLATE_T_MM, z - h / 2, x + w / 2, fr.D, z + h / 2)
            s.label = f"jack_plate_{n_plate}"
            out[s.label] = s
            n_plate += 1
        elif hw.item == "strap handle":
            x, y, z = hw.position
            half = spec.aesthetics.handle_screw_spacing_mm / 2.0 + STRAP_EXTRA_MM / 2.0
            s = _box(x - half, y - STRAP_W_MM / 2, z, x + half, y + STRAP_W_MM / 2, z + STRAP_T_MM)
            s.label = "strap_handle"
            out[s.label] = s
        elif hw.item == "recessed handle":
            w, h = hw.cutout
            x, y, z = hw.position
            if x < 0:
                s = _box(x, y - w / 2, z - h / 2, x + RECESSED_DEPTH_MM, y + w / 2, z + h / 2)
                s.label = "recessed_handle_left"
            else:
                s = _box(x - RECESSED_DEPTH_MM, y - w / 2, z - h / 2, x, y + w / 2, z + h / 2)
                s.label = "recessed_handle_right"
            out[s.label] = s
        elif hw.item == "foot":
            x, y, _ = hw.position
            s = Pos(x, y, -FOOT_H_MM) * Cylinder(spec.aesthetics.foot_diameter_mm / 2.0, FOOT_H_MM,
                                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
            s.label = f"foot_{len([k for k in out if k.startswith('foot_')])}"
            out[s.label] = s
    return out
```
<!-- /code -->

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: `14 passed`

- [ ] **Step 5: Render and view**

Run: `.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); import cabmodel as M; M.main(['--render', 'rear', '--demo', 'site-box', '--out', '/tmp/cab-rear.png'])"`
Then view the PNG with the Read tool. Expected: the site box from the rear with the back panel, the tube bore with its flange ring, the jack plate cutout at the bottom center, and the speaker envelope's stepped cylinder behind the baffle.

- [ ] **Step 6: Commit**

```bash
git add scripts/cabmodel.py scripts/test_cabmodel.py
git commit -m "cabmodel: backs, port tubes and rings, slot shelf, speaker envelopes, hardware components" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 11: CAD layer, part 4: `build`, air volume, interference, `check_build`, exploded view, exports, `cab.json`, the CAD matrix

**Files:**
- Modify: `scripts/cabmodel.py` (append after the Task 10 unit)
- Modify: `scripts/test_cabmodel.py` (append after the Task 10 tests)

**Interfaces:**
- Consumes: Tasks 8 to 10; `cablayout.layout`, `check_layout`, `layout_report`; `cutlist.write_cut_list(..., extra_lines=...)` (Task 3); `scripts/render_stl.py`.
- Produces: `CabBuild` (`parts` registry in the furniture shape with `dims`, `components`, `assembly`, `air` per chamber, `layout`), `build(layout) -> CabBuild` (each chamber's air is the chamber box minus every solid in that chamber minus its port air, kept whole because a shelf or tube can split it), `check_build(cab, layout) -> list` (`interference` with the worst pair, `air volume`, `part count`, `rectangularity`), `exploded(cab, factor=EXPLODE_FACTOR)` (each solid moved by 2 x factor x its bounding-box-center offset from the assembly center), `tolex_line(layout) -> dict | None`, `export(cab, layout, checks, out_dir) -> dict` (writes `cab.step` with the components as labeled solids beside the parts, `images/cab-iso.png`, `cab-front.png`, `cab-top.png`, `cab-right.png`, `cab-exploded.png`, `cutlist.md`, `cutlist.csv` with the tolex line, `cab.json`; returns the files dict), and the `__main__` guard for `--render`. Exact signatures are in the code below.

The CAD matrix: twelve representative configurations by default (every enclosure, both driver counts, all three line and joint pairs at least once, one stereo, one slot, one open), all sixty with `CAB_FULL_MATRIX=1`; each proves measured air minus displacement within 1 percent of the layout's net, no interference, part count equal to the layout's, STEP written.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_cabmodel.py`:

<!-- code: test_cabmodel.py unit 11 -->
```python
# === TASK 11 ===
def _site_layout(**aest):
    a = L.Aesthetics(tolex_color="Fender Style Black", **aest)
    return L.layout(L.order_from(sheet(port="round"), a))


def test_build_air_volume_matches_the_layout_and_nothing_collides():
    lay = _site_layout()
    cab = M.build(lay)
    assert len(cab.parts) == len(lay.parts) == cab.assembly.solids().__len__()
    assert [e["name"] for e in cab.parts] == [b.name for b in lay.parts]
    by = {c.name: c for c in M.check_build(cab, lay)}
    assert set(by) == {"interference", "air volume", "part count", "rectangularity"}
    assert by["interference"].level == "pass", by["interference"].message
    assert by["air volume"].level == "pass", by["air volume"].message
    assert by["part count"].level == "pass"
    measured = cab.air[0].volume / 1e6 - lay.chambers[0].displacement_l
    assert abs(measured - lay.net_l[0]) / lay.net_l[0] < 0.001
    assert "baffle" in by["rectangularity"].message


def test_check_build_reports_a_collision():
    lay = _site_layout()
    cab = M.build(lay)
    # push the back panel 5 mm into the box: it must hit the back cleats
    idx = next(i for i, e in enumerate(cab.parts) if e["name"] == "back")
    cab.parts[idx]["solid"] = M.Pos(0, -5.0, 0) * cab.parts[idx]["solid"]
    cab.parts[idx]["solid"].label = "back"
    by = {c.name: c for c in M.check_build(cab, lay)}
    assert by["interference"].level == "blocker" and "back" in by["interference"].message


def test_exploded_moves_every_part_outward():
    lay = _site_layout()
    cab = M.build(lay)
    ex = M.exploded(cab, factor=0.6)
    bb, ab = ex.bounding_box(), cab.assembly.bounding_box()
    assert bb.max.X - bb.min.X > (ab.max.X - ab.min.X) * 1.8
    assert len(ex.solids()) == len(cab.parts) + len(cab.components)


def test_export_writes_every_deliverable(tmp_path):
    lay = _site_layout()
    cab = M.build(lay)
    checks = L.check_layout(lay, lay.spec) + M.check_build(cab, lay)
    files = M.export(cab, lay, checks, tmp_path)
    for key in ("step", "cutlist_md", "cutlist_csv", "cab_json"):
        assert Path(files[key]).exists(), key
    assert len(files["images"]) == 5 and all(Path(p).exists() for p in files["images"])
    report = json.loads((tmp_path / "cab.json").read_text())
    assert report["external_in"] == [20.0, 18.0, 11.0]
    assert {c["name"] for c in report["checks"]} >= {"sheet", "interference", "air volume"}
    md = (tmp_path / "cutlist.md").read_text()
    assert "## Materials not cut" in md and "tolex wrap" in md and "Fender Style Black" in md
    assert "finger joint" in md
    # hardwood: no tolex line
    spec = L.order_from(sheet(line="hardwood", species="black walnut", port="round"),
                        L.Aesthetics(corner_joint="dovetail"))
    lay2 = L.layout(spec)
    cab2 = M.build(lay2)
    M.export(cab2, lay2, L.check_layout(lay2, spec), tmp_path / "hw")
    md2 = (tmp_path / "hw" / "cutlist.md").read_text()
    assert "Materials not cut" not in md2 and "through dovetail" in md2


# --- CAD matrix: live proposals through layout and build
TONE = json.loads((HERE.parents[1] / "fixtures" / "tone-roots.json").read_text())
TONE["min_power_w"] = 30
MATRIX_SPEAKER = "eminence-cannabis-rex"
ENCLOSURES = [("closed", None), ("closed-ported", None), ("closed-ported", "slot"), ("open", None), ("semi-open", None)]
CONFIGS = [(1, "mono"), (2, "mono"), (2, "mono-parallel-out"), (2, "stereo")]
LINES = [("tolex", None, "finger"), ("hardwood", "black walnut", "finger"), ("hardwood", "black walnut", "dovetail")]
DEFAULT_CASES = [
    # enclosure, slot, drivers, jack, line index, extra aesthetics
    ("closed", None, 1, "mono", 0, {}),
    ("closed-ported", None, 1, "mono", 0, {}),
    ("closed-ported", "slot", 1, "mono", 1, {}),
    ("open", None, 1, "mono", 0, {"handle": "recessed-side"}),
    ("semi-open", None, 1, "mono", 2, {}),
    ("closed", None, 2, "mono", 0, {}),
    ("closed-ported", None, 2, "mono", 1, {"baffle_mount": "fixed"}),
    ("closed-ported", "slot", 2, "mono", 0, {}),
    ("closed", None, 2, "stereo", 2, {}),
    ("closed-ported", None, 2, "stereo", 0, {}),
    ("open", None, 2, "mono-parallel-out", 0, {}),
    ("semi-open", None, 2, "stereo", 0, {"baffle_mount": "fixed"}),
]


def _matrix_cases():
    if os.environ.get("CAB_FULL_MATRIX"):
        return [(enc, slot, n, jack, li, {}) for enc, slot in ENCLOSURES for n, jack in CONFIGS
                for li in range(len(LINES))]
    return DEFAULT_CASES


def _sheet_for(drv, enclosure, slot, n, jack, line, species):
    z = drv.impedance_ohm[0]
    c = cabvoice.Constraints(line=line, species=species, port_slot_mm=(300.0, 40.0) if slot else None)
    v = cabvoice.propose([drv] * n, [z] * n, enclosure, TONE, jack, c, "cad-matrix").to_dict()
    if slot and n == 2 and jack != "stereo":
        w_int = v["box"]["internal_mm"][0]
        c.port_slot_mm = ((w_int - L.DIVIDER_MM) / 2.0 - 1.0, 40.0)
        v = cabvoice.propose([drv] * n, [z] * n, enclosure, TONE, jack, c, "cad-matrix").to_dict()
    return v


def test_cad_matrix_solids_agree_with_the_layout(tmp_path):
    t0 = time.time()
    drv = cabvoice.load_speaker(MATRIX_SPEAKER)
    cases = _matrix_cases()
    layout_blockers = {}
    for k, (enclosure, slot, n, jack, li, extra) in enumerate(cases):
        line, species, joint = LINES[li]
        v = _sheet_for(drv, enclosure, slot, n, jack, line, species)
        assert not v["blockers"], (enclosure, slot, n, jack, line, v["blockers"])
        spec = L.order_from(v, L.Aesthetics(corner_joint=joint, **extra))
        lay = L.layout(spec)
        for c in L.check_layout(lay, spec):
            if c.level == "blocker":
                layout_blockers.setdefault(c.name, []).append((enclosure, slot, n, jack, line))
                assert c.name in ("port fit", "net volume"), (enclosure, slot, n, jack, line, c.message)
        cab = M.build(lay)
        by = {c.name: c for c in M.check_build(cab, lay)}
        label = (enclosure, slot, n, jack, line, joint, extra)
        assert by["interference"].level == "pass", (label, by["interference"].message)
        assert by["air volume"].level == "pass", (label, by["air volume"].message)
        assert by["part count"].level == "pass", label
        step = tmp_path / f"case{k}.step"
        M.export_step(cab.assembly, str(step))
        assert step.exists() and step.stat().st_size > 1000
    print(f"\ncad matrix {len(cases)} builds in {time.time() - t0:.0f} s; layout blockers {layout_blockers}")
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: the Task 11 tests fail with `AttributeError`; earlier tests still pass.

- [ ] **Step 3: Implement**

Append to `scripts/cabmodel.py`:

<!-- code: cabmodel.py unit 11 -->
```python
# === TASK 11 ===
AIR_TOL_PCT = 1.0
OVERLAP_TOL_MM3 = 1.0
RECT_RATIO_MIN = 0.98
EXPLODE_FACTOR = 0.6


@dataclass
class CabBuild:
    layout: object
    parts: list                      # furniture PARTS entries, one per blank, in layout order
    components: dict                 # placeholders: speakers, plates, handle, feet
    assembly: object                 # Compound of the part solids
    air: list = field(default_factory=list)   # one shape per chamber (air with the parts removed)

    def solids(self) -> list:
        return [e["solid"] for e in self.parts]


def _port_air_tool(entry: dict):
    if entry["type"] == "box":
        (x0, y0, z0), (x1, y1, z1) = entry["box"]
        return _box(x0, y0, z0, x1, y1, z1)
    cx, cz = entry["center"]
    y0, y1 = entry["y"]
    return _cyl_y(cx, cz, entry["d"], y0, y1)


def build(layout) -> CabBuild:
    """Every blank as one named solid, the component placeholders, the
    assembly, and one air shape per chamber (the chamber box minus every
    solid the layout puts inside it minus its port air)."""
    parts = [part_entry(b, blank_solid(b)) for b in layout.parts]
    components = component_solids(layout)
    assembly = compound_of(e["solid"] for e in parts)
    air = []
    for ch in layout.chambers:
        (x0, y0, z0), (x1, y1, z1) = ch.box
        shape = _box(x0, y0, z0, x1, y1, z1)
        for entry, blank in zip(parts, layout.parts):
            if blank.chamber == ch.index:
                shape = shape - entry["solid"]
        for pa in ch.port_air:
            shape = shape - _port_air_tool(pa)
        air.append(shape)
    return CabBuild(layout=layout, parts=parts, components=components, assembly=assembly, air=air)


def check_build(cab: CabBuild, layout) -> list:
    """What only CAD can prove: interference, measured air volume, part
    count, rectangularity. Same Check shape as cablayout.check_layout."""
    checks = []
    named = [(e["name"], e["solid"]) for e in cab.parts] + list(cab.components.items())
    worst, worst_pair, collisions = 0.0, None, []
    for i, (na, a) in enumerate(named):
        for nb, b in named[i + 1:]:
            if not _bbox_overlap(a, b):
                continue
            v = overlap_volume(a, b)
            if v > worst:
                worst, worst_pair = v, (na, nb)
            if v > OVERLAP_TOL_MM3:
                collisions.append(f"{na} x {nb} {v:.0f} mm3")
    if collisions:
        checks.append(L.Check("interference", "blocker", "; ".join(collisions)))
    else:
        checks.append(L.Check("interference", "pass",
                              f"{len(named)} solids, no pair overlaps by more than {OVERLAP_TOL_MM3:g} mm3"
                              + (f" (worst {worst_pair[0]} x {worst_pair[1]} {worst:.2f} mm3)" if worst_pair else "")))
    msgs, level = [], "pass"
    for ch, shape in zip(layout.chambers, cab.air):
        measured = shape.volume / 1e6 - ch.displacement_l
        delta = (measured - ch.net_l) / ch.net_l * 100.0
        msgs.append(f"chamber {ch.index} measured {measured:.2f} L vs layout {ch.net_l:.2f} L ({delta:+.2f} percent)")
        if abs(delta) > AIR_TOL_PCT:
            level = "blocker"
    checks.append(L.Check("air volume", level, "; ".join(msgs)))
    n_cad, n_lay = len(cab.parts), len(layout.parts)
    checks.append(L.Check("part count", "pass" if n_cad == n_lay else "blocker",
                          f"{n_cad} solids for {n_lay} blanks"))
    shaped = []
    for e in cab.parts:
        bb = e["solid"].bounding_box()
        bbox = (bb.max.X - bb.min.X) * (bb.max.Y - bb.min.Y) * (bb.max.Z - bb.min.Z)
        ratio = e["solid"].volume / bbox if bbox > 0 else 1.0
        if ratio < RECT_RATIO_MIN:
            shaped.append(f"{e['name']} {ratio:.0%}")
    checks.append(L.Check("rectangularity", "pass",
                          ("blanks below 98 percent of their bounding box (cut list uses the blank dims): "
                           + ", ".join(shaped)) if shaped else "every part is a plain rectangular blank"))
    return checks


def exploded(cab: CabBuild, factor: float = EXPLODE_FACTOR):
    """Every part and component moved away from the assembly center along
    its own centroid offset, 2 x factor x that offset, so the outer parts
    travel about factor times the external dimension on each axis."""
    bb = cab.assembly.bounding_box()
    cx, cy, cz = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2
    moved = []
    for solid in cab.solids() + list(cab.components.values()):
        sb = solid.bounding_box()
        ox, oy, oz = (sb.min.X + sb.max.X) / 2 - cx, (sb.min.Y + sb.max.Y) / 2 - cy, (sb.min.Z + sb.max.Z) / 2 - cz
        m = Pos(2 * factor * ox, 2 * factor * oy, 2 * factor * oz) * solid
        m.label = getattr(solid, "label", "")
        moved.append(m)
    return compound_of(moved)


def tolex_line(layout) -> dict | None:
    t = layout.tolex
    if t is None:
        return None
    color = layout.spec.aesthetics.tolex_color or "color not chosen"
    return {"part": "tolex wrap", "qty": round(t["length_yd"], 2), "unit": "yd",
            "material": f"tolex {color}, {t['roll_in']} in roll",
            "notes": f"{t['area_m2']:.2f} m2 external area x 1.15; {t['length_m']:.2f} m"}


def export(cab: CabBuild, layout, checks: list, out_dir) -> dict:
    """cab.step, four renders plus the exploded view under images/, the cut
    list with the tolex line, and cab.json. Returns the files dict."""
    out_dir = Path(out_dir)
    images = out_dir / "images"
    images.mkdir(parents=True, exist_ok=True)
    everything = cab.solids() + list(cab.components.values())
    step = out_dir / "cab.step"
    export_step(compound_of(everything), str(step))
    files = {"step": str(step), "images": []}
    for view, (elev, azim) in RENDER_VIEWS.items():
        png = render(everything, images / f"cab-{view}.png", views=[(elev, azim)])
        files["images"].append(str(png))
    png = render([exploded(cab)], images / "cab-exploded.png", views=[(30, -60)])
    files["images"].append(str(png))
    extra = [tolex_line(layout)] if layout.tolex else None
    md, csv = out_dir / "cutlist.md", out_dir / "cutlist.csv"
    cutlist.write_cut_list(cab.parts, str(md), csv_path=str(csv), title=layout.spec.name, extra_lines=extra)
    files["cutlist_md"], files["cutlist_csv"] = str(md), str(csv)
    report = L.layout_report(layout, checks)
    report["files"] = files
    (out_dir / "cab.json").write_text(json.dumps(report, indent=2) + "\n")
    files["cab_json"] = str(out_dir / "cab.json")
    return files


if __name__ == "__main__":
    sys.exit(main())
```
<!-- /code -->

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: `19 passed` (default matrix; `CAB_FULL_MATRIX=1` runs all sixty builds and is not required for the commit)

- [ ] **Step 5: Render and view**

Run: `.venv/bin/python scripts/cabmodel.py --render assembly --demo site-box --out /tmp/cab-assembly.png` and `.venv/bin/python scripts/cabmodel.py --render exploded --demo open-1x12 --out /tmp/cab-exploded.png`
Then view both PNGs with the Read tool. Expected: the assembled site box with the grill frame in the recess, corners finger-jointed, strap handle and feet; the exploded open-back 1x12 with every part separated along its centroid direction, the two open-back panels, cleats, and the speaker envelope in front of the baffle.

- [ ] **Step 6: Commit**

```bash
git add scripts/cabmodel.py scripts/test_cabmodel.py
git commit -m "cabmodel: build, air volume, interference, exploded view, exports, cab.json, CAD matrix" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 12: Fixture order `site-default` and the 1 mm reproduction test

**Files:**
- Create: `projects/Speaker-cab-system/fixtures/site-default/tone.json`, `voicing.json`, `voicing.md` (the sheet regenerated by the landed engine)
- Create: `projects/Speaker-cab-system/fixtures/site-default/cab.py` (the template every order copies)
- Create: outputs `cab.json`, `cutlist.md`, `cutlist.csv`, `images/*.png` (committed); `cab.step` and `*.stl` (ignored)
- Modify: `.gitignore` (STEP and STL under fixtures)
- Modify: `scripts/test_cabmodel.py` (append the fixture test)

**Interfaces:**
- Consumes: Tasks 2, 7, 11; `scripts/cabvoice.py` CLI.
- Produces: the reference order; `test_site_default_fixture` proving external dimensions within 1 mm of 508 x 457.2 x 279.4 and exit code 0.

- [ ] **Step 1: Regenerate the fixture sheet with the landed engine**

Run from the vault root:

```bash
mkdir -p projects/Speaker-cab-system/fixtures/site-default
cat > projects/Speaker-cab-system/fixtures/site-default/tone.json <<'JSON'
{
  "low_end": "tight",
  "mids": "neutral",
  "top": "smooth",
  "breakup": "moderate",
  "dispersion": "focused",
  "placement": "floor",
  "min_power_w": 45,
  "impedance_options_ohm": [
    8,
    16
  ]
}
JSON
.venv/bin/python scripts/cabvoice.py evaluate --speaker celestion-g12h-30-anniversary --impedance 16 --enclosure closed-ported --tone projects/Speaker-cab-system/fixtures/site-default/tone.json --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40 --line tolex --name site-default --out projects/Speaker-cab-system/fixtures/site-default; echo "exit $?"
```

Expected: exit 0, `voicing.json` with `"external_mm": [508.0, 457.2, 279.4]`, `"blockers": []`, a round port of 101.5 mm inside diameter and 40 mm length (Fb 66 Hz, punchy). The fixture carries its own tone file: tone-roots with `min_power_w` 45, because the site's 30 W G12H against the shared 60 W target is a power blocker and the sheet must be blocker-free; the 77.3 mm tube cannot tune this box at any length above the 20 mm minimum, which is why the fixture uses the 101.5 mm tube.

- [ ] **Step 2: Write the failing fixture test**

Append to `scripts/test_cabmodel.py`:

<!-- code: test_cabmodel.py unit 12 -->
```python
# === TASK 12 ===
def test_site_default_fixture(tmp_path):
    fixture = HERE / "fixtures" / "site-default"
    env = dict(os.environ, EXPORT="1", CAB_OUT=str(tmp_path))
    if (HERE / "cabvoice.py").exists():          # mirror run: the template's sys.path points at scripts/
        env["PYTHONPATH"] = str(HERE)
    proc = subprocess.run([sys.executable, str(fixture / "cab.py")], env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads((tmp_path / "cab.json").read_text())
    for got, want in zip(report["external_mm"], (508.0, 457.2, 279.4)):
        assert abs(got - want) <= 1.0
    assert (tmp_path / "cab.step").exists() and (tmp_path / "images" / "cab-exploded.png").exists()
    assert all(c["level"] != "blocker" for c in report["checks"])
    assert "interference" in proc.stdout and "exported" in proc.stdout
```
<!-- /code -->

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q -k site_default`
Expected: FAIL, `cab.py` not found.

- [ ] **Step 3: Write `cab.py`**

Create `projects/Speaker-cab-system/fixtures/site-default/cab.py` with exactly this content:

<!-- code: fixtures/site-default/cab.py all -->
```python
"""Site-default order: the 20 x 18 x 11 in 1x12 closed-ported tolex cab.
Copy this file into a new order directory next to its voicing.json, edit the
aesthetics constants, then run it from anywhere:

    python cab.py                 layout and checks only (prints every verdict)
    TMP_STL=/tmp/cab.stl python cab.py   also writes an STL for render_stl.py
    EXPORT=1 python cab.py        also builds the CAD, runs the CAD checks, and
                                  exports cab.step, images/, cutlist, cab.json
                                  (into CAB_OUT when set, else next to this file)
    SHOW=1 python cab.py          also opens the OCP viewer when installed

Exit 0 when every check passes or warns, 1 on an input error (nothing
written), 2 when any check is a blocker (files still written under EXPORT).
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parents[3]
sys.path.insert(0, str(VAULT / "scripts"))
import cablayout as L  # noqa: E402

# --- aesthetics block (from the intake) --------------------------------------
AESTHETICS = L.Aesthetics(
    corner_joint="finger",          # "dovetail" on the hardwood line only
    baffle_mount="floating",        # or "fixed" (glued into 6 mm dados)
    handle="strap",                 # or "recessed-side"
    corners="black",                # "black", "chrome", or "none"
    piping=False,
    feet="rubber",                  # or "tilt-back"
    tolex_roll_in=54,               # 54 for British and Fender black, 32 for tweed
    tolex_color="Fender Style Black",
    grill_cloth="British Small Weave Cane",
    head_width_mm=None,             # set to match a head: external width = head + 0 to 10 mm
)

try:
    spec = L.order_from(L.load_voicing(HERE / "voicing.json"), AESTHETICS)
except ValueError as e:
    print(f"input error: {e}")
    sys.exit(1)
lay = L.layout(spec)
checks = L.check_layout(lay, spec)

if os.environ.get("TMP_STL") or os.environ.get("EXPORT") or os.environ.get("SHOW"):
    import cabmodel as M
    cab = M.build(lay)
    checks += M.check_build(cab, lay)
    if os.environ.get("TMP_STL"):
        from build123d import export_stl
        export_stl(M.compound_of(cab.solids() + list(cab.components.values())), os.environ["TMP_STL"])
    if os.environ.get("EXPORT"):
        out = Path(os.environ.get("CAB_OUT") or HERE)
        files = M.export(cab, lay, checks, out)
        print(f"exported {files['step']} and {len(files['images'])} renders")
    if os.environ.get("SHOW"):
        from ocp_vscode import show
        show(*cab.solids(), names=[e["name"] for e in cab.parts])

for c in checks:
    print(f"{c.name:16s} {c.level:8s} {c.message}")
sys.exit(2 if any(c.level == "blocker" for c in checks) else 0)
```
<!-- /code -->

- [ ] **Step 4: Build the fixture and ignore its heavy outputs**

Append to `.gitignore`:

```
# Speaker cab fixtures: STEP and STL are regenerated by cab.py
projects/Speaker-cab-system/fixtures/**/*.step
projects/Speaker-cab-system/fixtures/**/*.stl
```

Run: `EXPORT=1 .venv/bin/python projects/Speaker-cab-system/fixtures/site-default/cab.py; echo "exit $?"`
Expected: every check line `pass` or `warn`, `exit 0`, and the files `cab.json`, `cab.step`, `cutlist.md`, `cutlist.csv`, `images/cab-iso.png`, `cab-front.png`, `cab-top.png`, `cab-right.png`, `cab-exploded.png` present. View `images/cab-iso.png` and `images/cab-exploded.png` with the Read tool.

- [ ] **Step 5: Run the fixture test**

Run: `.venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: `20 passed`

- [ ] **Step 6: Commit**

```bash
git add .gitignore scripts/test_cabmodel.py projects/Speaker-cab-system/fixtures/site-default/tone.json projects/Speaker-cab-system/fixtures/site-default/voicing.json projects/Speaker-cab-system/fixtures/site-default/voicing.md projects/Speaker-cab-system/fixtures/site-default/cab.py projects/Speaker-cab-system/fixtures/site-default/cab.json projects/Speaker-cab-system/fixtures/site-default/cutlist.md projects/Speaker-cab-system/fixtures/site-default/cutlist.csv projects/Speaker-cab-system/fixtures/site-default/images
git commit -m "Speaker cab fixture: site-default order reproduces the 20 x 18 x 11 in box within 1 mm" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
```

---

### Task 13: Vault updates: construction note, spec pointer, retrospectives, handoff, memory, push

**Files:**
- Modify: `knowledge/speaker-cab-construction.md` (full replacement)
- Modify: `projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md` (one pointer line under the Unit 2 heading)
- Modify: `knowledge/learnings/speaker-cab-plan-1.md` (the Plan 2 open item line)
- Create: `knowledge/learnings/speaker-cab-plan-2.md`
- Modify: `memory/project-speaker-cab-system.md`, `memory/MEMORY.md`
- Create: `projects/Speaker-cab-system/.claude/context-check/last-handoff.md` (git-ignored)

**Interfaces:**
- Consumes: everything landed; the ledger `.superpowers/sdd/progress.md` for the facts (commit hashes, test counts, review findings).
- Produces: the vault state Plan 3 starts from.

- [ ] **Step 1: Replace the construction note**

Write `knowledge/speaker-cab-construction.md` with exactly this content:

<!-- code: .vault/knowledge/speaker-cab-construction.md all -->
````markdown
---
name: speaker-cab-construction
description: Construction rules and starting values for MaximoCabs guitar speaker cabinets (tolex and hardwood lines, 1x12 and 2x12, closed, closed-ported and open-back)
type: reference
status: unverified-starting-values
created: 2026-09-09
updated: 2026-09-10
tags: [knowledge, speaker-cab, woodworking, reference]
---

# Speaker cabinet construction

Starting values for the `/speaker-cab` skill and the cabinet generator, in
the same locked-constants spirit as [[woodworking-stock]]: change only with
evidence from a build, then record the change in the retrospective. Nothing
here has been verified against Brian's shop practice yet. Product facts come
from the MaximoCabs site content (`~/ClaudeProjects/MaximoCabs/src/content/cabinets/`);
everything else is general builder practice unless a source is given. The
2026-09-10 revision follows [[2026-09-10-plan-2-generator-design]]: finger
joints on both lines, a dovetail option on hardwood, no corner posts, the
grill frame on the speaker flanges, and margins the generator can assert.

## Materials

| Material | Use | Thickness | Density | Source |
|---|---|---|---|---|
| Baltic birch plywood, 13-ply | Tolex line shell, baffle, cleats, brace, divider, shelf | 18 mm (3/4 in nominal) | 680 kg/m3 | site content; density is the common trade figure, unverified |
| Baltic birch plywood | Back panels, open-back panels, grill frame strips, port flange rings | 12 mm (1/2 in nominal) | 680 kg/m3 | starting value |
| Black walnut, resawn | Hardwood line shell | 19 mm | 610 kg/m3 | https://www.wood-database.com/black-walnut/ |
| Black cherry, resawn | Hardwood line shell | 19 mm | 560 kg/m3 | https://www.wood-database.com/black-cherry/ |
| Hard maple, resawn | Hardwood line shell | 19 mm | 705 kg/m3 | https://www.wood-database.com/hard-maple/ |
| Sapele, resawn | Hardwood line shell | 19 mm | 670 kg/m3 | https://www.wood-database.com/sapele/ |
| PVC or ABS pipe, Schedule 40 | Rear round port tubes | inside 52.0, 77.3, 101.5, 153.2 mm (outside 60.3, 88.9, 114.3, 168.3) | ignored in mass | [[speaker-envelopes-and-port-stock]]; which size Brian buys is not settled |

Sheet stock is 2440 x 1220 mm with a 3 mm kerf for yield, as in [[woodworking-stock]]. Hardwood shell panels are glued up from resawn boards; the generator's stock check uses 3050 x 600 mm per panel as a starting limit.

## Shell per line

- **Both lines**: top, bottom, and two sides joined at the four front-to-back corner edges. The tolex line gets finger joints; the hardwood line gets finger joints by default or through dovetails as the option. The generator models the joint so renders and STEP are truthful; the cut list keeps each panel as a rectangular blank with the joint schedule in the note.
- **Tolex line**: 18 mm birch. Recessed metal jack plate. Metal corners, black or chrome, or none. Site: "13-ply void-free Baltic birch, hand-cut finger joints".
- **Hardwood line**: 19 mm resawn, book-matched panels, show face out. Recessed brass jack plate. No metal corners by default. Oil finish. The site copy still says "through-tenon corner posts glued + pinned" while the site's own renders show finger joints; the copy is wrong and is a site fix outside this vault.
- **Joinery survey**: finger joints are the plurality at the top of the market and the vintage-correct choice; the through dovetail is the only structural peer for solid wood; miters and rabbets are styling or budget choices. Details and sources in [[guitar-cab-joinery-survey]].

## Joinery conventions

- **Fingers**: width half the panel thickness (9 mm on 18 mm birch, 9.5 mm on 19 mm hardwood), count the nearest odd integer to depth / width so both ends are full fingers, width recomputed as depth / count. The top and bottom panels carry a full finger at the front edge; the sides start with a gap. Trade practice runs 1/4 in fingers; the width is a parameter.
- **Dovetails** (hardwood only): tails on the side panels so a lift by the top handle loads the joint in its locked direction, pins on top and bottom, half-pins at both ends, slope 1:8, pin width half the panel thickness at the outer face, tails about 30 mm.
- **Wood movement (hardwood line)**: grain runs front to back on all four shell panels so every panel moves along the depth axis together; expect roughly 2.6 mm (cherry), 2.8 (sapele), 2.9 (walnut), 3.7 mm (hard maple) of depth change per 4-point moisture swing flatsawn, about half quartersawn. Every cleat on the hardwood line runs across the grain, so cleats are screwed through slotted holes and glued only at their center 100 mm, and a fixed baffle is glued in the front 100 mm of its dado only. The intake's "where it lives" answer sets the expected humidity swing.

## Baffle

- 18 mm birch on both lines. Front face 20 mm behind the front edge of the shell (the recess that holds the grill frame). Driver mounts from the front of the baffle onto T-nuts fitted from the back. Bolts M6 or 1/4-20, 6.5 mm holes on the note's bolt circle, first hole at twelve o'clock.
- **Floating (default)**: 1 mm clearance to each side, on 18 x 18 mm cleats glued to the shell, felt strip between cleat and baffle, held with screws through the cleats, removable. Site: "floating 3/4 in birch with felt isolation".
- **Fixed (option)**: glued into a 6 mm deep dado in all four shell panels, blank 12 mm larger in width and height, no baffle cleats. On hardwood see the cross-grain rule above.
- Driver cutout, bolt circle, bolt count, frame diameter, and magnet diameter come from the speaker note. Typical: Celestion 283 mm cutout on a 297 mm circle, Eminence 281 mm on 294 mm, Jensen 277 mm on 293.5 mm; frames 306 to 310 mm, so the flange overhangs the cutout by 11 to 15 mm; flange thickness 5 mm starting value.
- **Margins**: at least 44 mm from a cutout edge to any shell panel (grill strip 40 plus 2 mm clearance plus 2), 25 mm from a cutout edge to the brace or divider, so the two cutouts of a 2x12 sit 68 mm apart (18 plus 2 x 25). Minimum internal width = n x cutout + (n - 1) x 68 + 2 x 44, the same for mono and stereo since the divider replaces the brace (2x12 with 283 mm cutouts: 722 mm internal, 758 mm external, 29.8 in). Minimum internal height = cutout + 88, plus slot height + 18 with a front slot port.
- **Speaker envelope** (for clearance checks): behind the baffle a basket cylinder at the cutout diameter for the first 100 mm from the baffle front face, then the magnet cylinder at the note's magnet diameter plus 12 mm cover allowance (185 mm when the note has none), total length the note's depth. At least 25 mm from any envelope part to the back panel, a port tube, a cleat, a shelf, a stiffener, the brace, or the divider.

## Bracing and dividers

- Mono 2x12: one vertical 18 x 60 mm birch brace between top and bottom at the center of the baffle span, its front face 2 mm behind the baffle back, glued to top and bottom, notched around the baffle cleats (no notch with a fixed baffle).
- Stereo 2x12: a full-height 18 mm birch divider from the baffle back face to the back panel inner face replaces the brace and splits the box into two equal chambers, sealed with glue on top and bottom. The divider carries no cleats: the baffle and the back screw into its front and rear edges (cleats on its faces would crowd the 25 mm cutout margin). Each chamber's cutout sits 44 mm from the shell and 25 mm from the divider at the minimum width, any surplus split evenly. Each chamber gets its own jack plate and, when ported, its own port.
- Any shell or back panel span over 450 mm between glued members gets one 18 x 40 mm stiffener across its middle, glued flat to the panel (on a mono 2x12 that is the back panel).

## Backs and ports

- **Closed**: 12 mm birch back panel, flush with the rear edge, screwed to 18 x 18 mm cleats every 150 mm, removable. The jack plate sits in the back panel.
- **Closed-ported, rear round port**: a Schedule 40 PVC or ABS tube through the back panel with a 12 mm plywood flange ring (outside diameter tube plus 60 mm) glued to the inside face; inside diameter snapped by the voicing engine to the tube table above, length from the voicing sheet measured through the back panel, one per driver in the chamber (a mono 2x12 gets two identical ports, each sized as a 1x12 port in half the chamber; the sheet's `port.count` and `construction.port_count` say how many). Placement order: outboard of the driver at driver height, below the driver, lower outboard corner, above the driver; the first spot with 25 mm clearance to the speaker envelope, walls, cleats, brace, divider, and jack plate wins. When no spot fits, the generator names the longest tube that does; the voicing is then re-run with a larger diameter or a slot.
- **Closed-ported, front slot port**: the baffle stops short of the bottom panel by the slot height plus an 18 mm shelf; the shelf's front edge is flush with the baffle face, its depth equals the port length, and it doubles as the bottom baffle cleat. A slot narrower than the chamber gets two cheeks; a mono 2x12 gets two slots split by an 18 mm center cheek in line with the brace. The shelf must leave at least max(25 mm, slot height) of free depth behind it. Round rear tubes are a bass-cab convention; the published vented guitar cabs (EV TL806, Mesa Thiele) use the front slot.
- **Open-back**: two horizontal 12 mm panels, top and bottom, each (1 - open fraction) x internal height / 2 tall, screwed to cleats. Open fraction 0.40 for open, 0.25 for semi-open (from [[speaker-cab-voicing]]). The jack plate sits in the lower panel. Stereo keeps the divider and one plate per chamber.

## Grill

- Frame from 12 x 40 mm birch strips with half-lap corners, outer size the recess opening minus 2 mm per side, cloth wrapped around the frame and stapled at the back. The frame rests on the speaker flanges and on 5 mm felt spacers at its corners, so its face sits 3 mm behind the front edge; a strip may cover a flange but must clear every cutout by 2 mm. With a front slot port the frame covers only the baffle above the shelf.
- Retained with hook-and-loop strips to the baffle. Piping (optional) is glued into the corner between grill frame and shell.

## Hardware

- **Jack plate**: recessed dish plate, metal on the tolex line, brass on the hardwood line. Cutout is measured from the plate purchased; starting value 110 x 70 mm (the Marshall-style CJP-1 dish cuts 76.2 x 87.3 mm, so reconcile against the part bought). Placed at the bottom center of the back panel or lower open-back panel, 25 mm above the cleat, one per chamber. Mono: one 1/4 in jack. Mono with parallel out: two jacks on one plate wired in parallel. Stereo: one plate per chamber.
- **Handle**: top-center strap handle by default on both lines (the site shows a strap on the hardwood cab too), screw pair 228.6 mm apart (Marshall style; Fender style 203.2 mm), centered on the loaded center of mass in width and depth, kept 50 mm inside the edges. Recessed side handles as the option, one per side at the depth center of mass in the upper third, cutout 140 x 90 mm starting value (Penn Elcom H7154Z flange 161 x 107 mm, dish 8.5 mm). The handle check: within 15 mm of the loaded center of mass on the width axis.
- **Feet**: four rubber feet, 40 mm, inset 32 mm from the bottom corners. Tilt-back legs on the tolex line when the intake says placement is tilted: pivot screws 100 mm from the front and bottom edges, a hardware line only.
- **Corners**: metal corners on the tolex line by default (black or chrome), none on hardwood. Leg length is unpublished by every supplier, so every cutout keeps 50 mm from the external corners.
- Hardware dimensions and sources: [[speaker-envelopes-and-port-stock]].

## Tolex

- Roll widths from the site's material list: 54 in (1371.6 mm) for the British and Fender black styles, 32 in (812.8 mm) for tweed.
- Yardage = external surface area (all six faces) x 1.15 for wrap and waste, divided by the roll width, reported in metres and yards. The cut list carries this as a line item under "Materials not cut", not a part.
- Seams run along the bottom panel. Contact cement.

## Weight and center of mass

- Cabinet mass = sum over parts of volume x density (table above; the four shared corner blocks counted once) + speaker mass from the note + 1 kg hardware allowance.
- Center of mass = mass-weighted mean of part centroids, with the speaker mass placed at the baffle at the cutout center. The handle check compares its center to this point on the width axis (15 mm tolerance).
- Site reference: tolex 1x12 about 32 lb (14.5 kg) loaded, hardwood 1x12 about 38 lb (17.2 kg).

## Site defaults (calibration)

- External 20 x 18 x 11 in (508 x 457.2 x 279.4 mm), 1x12 closed-ported.
- Internal with the rules above: 472 x 421.2 x 229.4 mm, gross 45.6 L, net about 44 L after one driver.
- The engine voices both lines with the tolex line's 18 mm walls; the hardwood line's 19 mm panels take about 1 percent more of the same external size, inside the model's error, so no separate voicing. The line and species travel in voicing.json's construction block so the generator picks the density and joinery.
- A slot-ported 1x12 on the site box grows from 18.0 to 18.3 in tall through the engine's height floor; a 2x12 starts at 29.8 in wide.
````
<!-- /code -->

- [ ] **Step 2: Point the spec's Unit 2 at the addendum**

In `projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md`, directly after the line `## Unit 2: Parametric cabinet generator`, insert a blank line and then:

```markdown
> Amended 2026-09-10 by [[2026-09-10-plan-2-generator-design]]: finger joints on both lines with a dovetail option on hardwood (no corner posts), a layout kernel plus CAD layer, the grill frame on the flanges with 44 mm margins, a baffle mount option, tube-snapped port diameters, and speaker envelopes from new catalog fields. Where this section and the addendum differ, the addendum governs.
```

- [ ] **Step 3: Mark the Plan 1 open item superseded**

In `knowledge/learnings/speaker-cab-plan-1.md`, replace the text `model the hardwood line's 19 mm shell and corner posts and compare with the 18 mm voicing (1 to 2 percent of volume)` with `model the hardwood line's 19 mm finger-jointed shell (corner posts dropped on 2026-09-10, see [[2026-09-10-plan-2-generator-design]]) and compare with the 18 mm voicing (about 1 percent of volume)`.

- [ ] **Step 4: Write the Plan 2 retrospective**

Create `knowledge/learnings/speaker-cab-plan-2.md` from this skeleton, replacing every bracketed field from the ledger (commit hashes, dates, test counts, review findings, deviations); the controller writes this file, not an implementer:

````markdown
---
name: speaker-cab-plan-2
description: Retrospective for Plan 2 of the speaker cab system (layout kernel, CAD layer, engine and catalog touches), with the open items for Plan 3
type: learning
status: complete
created: [date]
tags: [learning, speaker-cab, generator, cad, retrospective]
---

# Speaker cab Plan 2 retrospective

Plan: [[plan-2-generator]]. Design: [[2026-09-10-plan-2-generator-design]]. Range [first commit]..[last commit] on main.

## What was built

- `scripts/cablayout.py` and `scripts/test_cablayout.py` ([n] tests, [m]-case matrix), `scripts/cabmodel.py` and `scripts/test_cabmodel.py` ([n] tests, CAD matrix 12 default / 60 full), engine touches ([symbols]), `scripts/cutlist.py` extra lines, twenty catalog notes with frame and magnet diameters, fixture `projects/Speaker-cab-system/fixtures/site-default/` reproducing the site box within [x] mm.

## What worked

- [from the ledger]

## What failed or was fixed in review

- [every review finding and its fix, by task]

## Starting values set during execution

- [any number chosen while building that the design did not fix]

## Deviations from the design

- [each, with the reason]

## Open items

- **Plan 3 (skill):** `--port-count` CLI flag; Fb override; the build loop that re-runs voicing on a port blocker with the longest tube that fits; proposal template from `cab.json`; the check table rows from the design's section 5.
- **Later:** per-impedance catalog sets; measured finger width, flange thickness, corner leg length, and jack plate cutout from purchased parts; vertical 2x12; tolex-line dovetail if asked; site copy fix (corner posts, closed-back wording).

## Decisions already locked

[copy the Decisions locked block from the design addendum, plus anything ruled during execution]
````

- [ ] **Step 5: Update memory**

Rewrite `memory/project-speaker-cab-system.md` with this content, correcting the bracketed facts from the ledger:

```markdown
---
name: project-speaker-cab-system
description: Custom guitar speaker cab capability for MaximoCabs; plan 1 (knowledge base + cabvoice.py) built 2026-09-09, plan 2 (cablayout.py + cabmodel.py generator, engine and catalog touches) built [date]; plan 3 (the skill) next
metadata:
  type: project
---

Brian is adding a guitar speaker cabinet design capability to the vault for his MaximoCabs custom cab business (site repo at ~/ClaudeProjects/MaximoCabs, quote-only Astro site, dormant since 2026-07-26). Spec approved 2026-09-09 at projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md, amended for Unit 2 by projects/Speaker-cab-system/2026-09-10-plan-2-generator-design.md. Locked: 1x12 and 2x12 (mono or stereo), closed, closed-ported and open-back; Thiele-Small voicing in scripts/cabvoice.py; finger joints on both lines with a through-dovetail option on hardwood (no corner posts, the site copy is wrong); ears-only validation; builder package plus customer proposal; no pricing, no site configurator.

Plan 1 done 2026-09-09: cabvoice.py propose/evaluate, knowledge notes, twenty speaker notes. Plan 2 done [date]: scripts/cablayout.py (numeric layout kernel, [n] tests with a [m]-case matrix), scripts/cabmodel.py (build123d layer, CAD matrix), engine touches (tube-snapped ports, 44 mm shell margin, 68 mm 2x12 cutout gap, height floor, frame and magnet diameters), cutlist extra lines, fixture order projects/Speaker-cab-system/fixtures/site-default/. Retrospectives at knowledge/learnings/speaker-cab-plan-1.md and speaker-cab-plan-2.md.

**Why:** the site promises rig-specific volume, port, and baffle design; Plans 1 and 2 give it the acoustics and the geometry. Every construction number is a starting value (status unverified-starting-values) until a build measures it.

**How to apply:** for any cab order, use the /speaker-cab skill once Plan 3 builds it; until then run cabvoice.py, copy the fixture's cab.py, edit its aesthetics constants, and run it with EXPORT=1. Plan documents live in projects/Speaker-cab-system/; the Plan 2 mirror in its pipeline/plan2-mirror/ is the oracle the plan's code came from. Confirm construction defaults with Brian before trusting them. See [[reference-vault-github-repo]] for commit and push habits.
```

In `memory/MEMORY.md`, replace the Speaker cab system line with:

```markdown
- [Speaker cab system](project-speaker-cab-system.md) - MaximoCabs guitar cab capability; plan 1 (voicing engine) and plan 2 (layout kernel + CAD generator) built; plan 3 (skill) next, open items in knowledge/learnings/speaker-cab-plan-2.md
```

- [ ] **Step 6: Handoff, commit, push**

Write `projects/Speaker-cab-system/.claude/context-check/last-handoff.md` in the form of the Plan 1 handoff (what is done, current state with the last commit hash and the exact test command, files that matter, a Decisions already locked block copied from the retrospective, and the next action: brainstorm Plan 3, the `/speaker-cab` skill, from the spec's Unit 3 and the Plan 2 retrospective's open items). Then:

```bash
git add knowledge/speaker-cab-construction.md projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md knowledge/learnings/speaker-cab-plan-1.md knowledge/learnings/speaker-cab-plan-2.md memory/project-speaker-cab-system.md memory/MEMORY.md
git commit -m "Speaker cab plan 2 complete: construction note, spec pointer, retrospective, memory" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Nsicw1Ym9Qd2U9xig5RBDc"
git push origin main
```

Expected: push accepted; `git status --short` shows only the other session's files.

---

## Self-review notes (written with the plan)

- **Spec coverage.** Design section 3.1 (layout kernel) is Tasks 4 to 7; 3.2 (CAD layer) Tasks 8 to 11; 3.3 (`cab.py`) and section 8 (files) Task 12; 3.4 (`cab.json`) Task 7's `layout_report` plus Task 11's `export`; section 4 (geometry rules) Tasks 4 to 6 with the CAD in 8 to 10; section 5 (checks) Task 7 (`check_layout`) and Task 11 (`check_build`); section 6 (shared touches) Tasks 1 to 3; section 7 (tests) the per-task tests, the 1200-case layout matrix in Task 7, the CAD matrix in Task 11, the fixture test in Task 12; section 9 (vault updates) Task 13; section 13 (amendments found while writing this plan) is already inside the embedded code. Section 10's process rules are the Global Constraints.
- **Pre-flight, done by construction.** Every code block was embedded by `projects/Speaker-cab-system/pipeline/embed_plan_code.py` from the mirror `projects/Speaker-cab-system/pipeline/plan2-mirror/`, where the suites run green: engine and cut list 371 (351 Plan 1 plus 5 Task 1 plus 12 Task 2 plus 3 Task 3), layout 34 with the strict 1200-case matrix (1026 clean, 24 named `port fit` blockers, all the 153.2 mm tube that no chamber holds, 150 engine power stops; worst clean net delta 1.1 percent on a hardwood 19 mm shell), CAD 20 (default matrix 127 s; all sixty builds 227 s with `CAB_FULL_MATRIX=1`). `embed_plan_code.py --check` reports the plan in sync, and each file's task units concatenate back to the mirror file exactly. The expected counts per task come from those runs.
- **Placeholder scan.** No TBD, TODO, "similar to Task", or unfilled token remains; every code step shows the code.
- **Type consistency.** The four layout units and the five CAD units are slices of two files that import and test as a whole, so names agree across tasks by construction; the prose Interfaces blocks were checked against the mirror's definitions (every backticked call names a real function or constant).
- **Deviations from the design, all recorded in the addendum's section 13:** divider without cleats and the stereo cutout placement; hardwood floors plus 2 mm; floors re-applied after every rescale; `volumes.inside_parts_l` and the new meaning of `volumes.port_l`; the 5 mm port placement scan; the `jack plate` check; stiffeners skipping open-back panels; the fixture's 101.5 mm tube and its own tone file. From the CAD layer: the STEP and renders carry the components (speaker envelopes, plates, handle, feet) as labeled solids while the cut list and part count use parts only; `overlap_volume` is the non-asserting form `check_build` uses; the demo tone lowers `min_power_w` to 30 so the Cannabis Rex passes the power check.
- **Locked values that changed from Plan 1**, listed in Task 2 for the reviewer: `MAX_PORT_DIAMETER_MM` 150 to 153.2, the port start 75 to 77.3, the cutout margins (25 everywhere) to 44 to the shell and 68 between 2x12 cutouts, and every calibration row moving with the inside-parts allowance (site-box net 44.1 to 42.5 L; Heritage G12H(55) reads tight instead of lean at Qtc 0.605).
- **Warnings for implementers.** Task 1's tests fail until the catalog script has patched the notes (`frame_diameter_mm` is required). Quads handed to `extrude` must be counter-clockwise or build123d extrudes toward minus X; trapezoid tools are grown along their slope; `Polygon(..., align=None)` or the polygon recenters; `Rot(X=-90)` turns a Z cylinder into a +Y one; a compound is `Compound(children=[...])`; `render_stl.py` renders one PNG per call at about 1.5 s. The CAD suite takes about two minutes and the Task 12 test spawns `cab.py` with `EXPORT=1` (about 20 s). Every closed-ported round Cannabis Rex case in the matrices ends with the layout blockers `port fit` and `net volume` (the 153.2 mm tube fits nowhere); that is engine and skill territory and the CAD checks still pass there.
- **After execution.** Plan 1's `sync_plan_code.py` is bound to Plan 1; for this plan, copy any review fix landed in `scripts/` back into the mirror file (same path under `plan2-mirror/` or `.vault/`) and run `embed_plan_code.py` so the plan and the mirror stay the record of what shipped.
