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
