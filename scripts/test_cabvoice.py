"""Tests for the speaker cabinet voicing engine."""
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

import cabvoice

FIXTURE_NOTE = """---
name: test-driver
type: speaker
brand: Test
model: Driver 12
diameter_in: 12
impedance_ohm: [8, 16]
power_w: 60
sensitivity_db: 100
magnet: ceramic
fs_hz: 75
re_ohm: 6.7
le_mh: 0.8
qts: 0.4
qes: 0.45
qms: 4.0
vas_l: 60
xmax_mm: 1.0
sd_cm2: 530
cutout_mm: 283
bolt_circle_mm: 297
bolt_count: 4
depth_mm: 135
weight_kg: 4.7
displacement_l: 1.5
data_status: datasheet
sources: [https://example.com/datasheet]
status: unverified-starting-values
---

# Test Driver 12

Body text.
"""


@pytest.fixture()
def speakers_dir(tmp_path):
    (tmp_path / "test-driver.md").write_text(FIXTURE_NOTE)
    return tmp_path


@pytest.fixture()
def drv(speakers_dir):
    return cabvoice.load_speaker("test-driver", speakers_dir)


def test_parse_frontmatter_returns_mapping():
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    assert meta["name"] == "test-driver"
    assert meta["impedance_ohm"] == [8, 16]
    assert meta["qts"] == 0.4


def test_parse_frontmatter_rejects_missing_block():
    with pytest.raises(ValueError):
        cabvoice.parse_frontmatter("# no frontmatter here\n")


def test_validate_speaker_ok():
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    assert cabvoice.validate_speaker(meta) == []


def test_validate_speaker_reports_missing_and_bad_values():
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    del meta["power_w"]
    meta["data_status"] = "guess"
    meta["qts"] = -1
    errors = cabvoice.validate_speaker(meta)
    assert any("power_w" in e for e in errors)
    assert any("data_status" in e for e in errors)
    assert any("qts" in e for e in errors)


def test_validate_speaker_allows_null_ts_when_missing():
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    meta["data_status"] = "missing"
    for key in cabvoice.TS_FIELDS:
        meta[key] = None
    assert cabvoice.validate_speaker(meta) == []


def test_validate_speaker_requires_ts_when_datasheet():
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    meta["vas_l"] = None
    errors = cabvoice.validate_speaker(meta)
    assert any("vas_l" in e for e in errors)


def test_validate_speaker_rejects_bad_displacement():
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    meta["displacement_l"] = -1.5
    errors = cabvoice.validate_speaker(meta)
    assert any("displacement_l" in e for e in errors)


def test_load_speaker_builds_driver(drv):
    assert drv.slug == "test-driver"
    assert drv.has_ts()
    assert drv.sd_m2 == pytest.approx(0.0530)
    assert drv.vas_m3 == pytest.approx(0.060)
    assert drv.xmax_m == pytest.approx(0.001)
    assert drv.impedance_ohm == [8, 16]


def test_load_speaker_unknown_slug_raises(speakers_dir):
    with pytest.raises(FileNotFoundError):
        cabvoice.load_speaker("nope", speakers_dir)


def test_list_speakers(speakers_dir):
    assert cabvoice.list_speakers(speakers_dir) == ["test-driver"]


# ---- Task 2: closed box -------------------------------------------------

def test_closed_box_for_qtc_matches_textbook(drv):
    # Vb = Vas / ((Qtc/Qts)^2 - 1); Qts 0.4, Vas 60 L, Qtc 0.707 -> 28.25 L
    vb = cabvoice.closed_box_for_qtc(drv, 0.707)
    assert vb == pytest.approx(28.25, abs=0.05)


def test_closed_box_roundtrip(drv):
    vb = cabvoice.closed_box_for_qtc(drv, 0.9)
    res = cabvoice.closed_box(drv, vb)
    assert res.qtc == pytest.approx(0.9, abs=1e-6)
    assert res.alpha == pytest.approx(60 / vb)
    assert res.fc_hz == pytest.approx(75 * (0.9 / 0.4))


def test_closed_response_is_minus_3db_at_fc_for_butterworth():
    assert cabvoice.closed_response_db(100.0, 0.7071, 100.0) == pytest.approx(-3.01, abs=0.02)
    assert cabvoice.closed_response_db(100.0, 0.7071, 1000.0) == pytest.approx(0.0, abs=0.05)
    assert cabvoice.closed_response_db(100.0, 0.7071, 50.0) == pytest.approx(-12.3, abs=0.2)


def test_closed_box_f3_and_response_table(drv):
    vb = cabvoice.closed_box_for_qtc(drv, 0.7071)
    res = cabvoice.closed_box(drv, vb)
    assert res.f3_hz == pytest.approx(res.fc_hz, rel=0.03)
    freqs = [f for f, _ in res.response]
    assert freqs[0] == 20.0 and freqs[-1] == 400.0
    assert len(freqs) == len(cabvoice.RESPONSE_FREQS)


def test_closed_box_rejects_driver_without_ts(drv):
    drv.qts = None
    with pytest.raises(ValueError):
        cabvoice.closed_box(drv, 40.0)


@pytest.mark.parametrize("qtc,expected", [
    (0.5, "lean"), (0.6, "tight"), (0.79, "tight"), (0.8, "balanced"),
    (0.99, "balanced"), (1.0, "big"), (1.19, "big"), (1.2, "peaky"), (1.5, "peaky"),
])
def test_closed_character_thresholds(qtc, expected):
    assert cabvoice.closed_character(qtc) == expected
