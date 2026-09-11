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
