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
