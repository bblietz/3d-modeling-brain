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


# ---- Task 3: ported box -------------------------------------------------

CU_FT_L = 28.3168


def _driver(**overrides):
    meta = cabvoice.parse_frontmatter(FIXTURE_NOTE)
    meta.update(overrides)
    return cabvoice.driver_from_meta(meta)


BETA_12A2 = dict(name="eminence-beta-12a-2", fs_hz=47, qts=0.46, qes=0.50, qms=6.00,
                 vas_l=120.1, sd_cm2=538.9, xmax_mm=4.4, re_ohm=5.0, le_mh=0.64,
                 power_w=250, sensitivity_db=98.0)
DELTA_12A = dict(name="eminence-delta-12a", fs_hz=55, qts=0.43, qes=0.46, qms=5.27,
                 vas_l=81.3, sd_cm2=519.5, xmax_mm=2.4, re_ohm=6.3, le_mh=0.74,
                 power_w=400, sensitivity_db=98.3)


def test_vented_coeffs_b4_alignment_is_butterworth():
    # Qts 0.383, alpha sqrt(2), h 1, lossless: 2.613, 3.414, 2.613
    a1, a2, a3 = cabvoice.vented_coeffs(0.383, math.sqrt(2), 1.0, ql=1e9)
    assert a1 == pytest.approx(2.611, abs=0.01)
    assert a2 == pytest.approx(3.414, abs=0.01)
    assert a3 == pytest.approx(2.611, abs=0.01)
    assert cabvoice.vented_response_db(100.0, (a1, a2, a3), 100.0) == pytest.approx(-3.01, abs=0.02)
    assert cabvoice.vented_response_db(100.0, (a1, a2, a3), 1000.0) == pytest.approx(0.0, abs=0.05)


@pytest.mark.parametrize("params,vb_cuft,fb,f3_expected", [
    (BETA_12A2, 1.75, 54.15, 64.18),
    (BETA_12A2, 1.25, 60.0, 73.47),
    (DELTA_12A, 0.75, 110.0, 100.2),
])
def test_ported_box_matches_eminence_designs(params, vb_cuft, fb, f3_expected):
    drv = _driver(**params)
    res = cabvoice.ported_box(drv, vb_cuft * CU_FT_L, fb)
    assert res.f3_hz == pytest.approx(f3_expected, rel=0.05)
    assert res.fb_hz == fb
    assert res.alpha == pytest.approx(params["vas_l"] / (vb_cuft * CU_FT_L))


def test_closed_box_matches_eminence_sealed_design():
    drv = _driver(**BETA_12A2)
    res = cabvoice.closed_box(drv, 0.904 * CU_FT_L)
    assert res.f3_hz == pytest.approx(92.1, rel=0.10)


def test_ported_box_reports_peak_and_character():
    drv = _driver(**DELTA_12A)
    small = cabvoice.ported_box(drv, 0.75 * CU_FT_L, 110.0)
    assert small.peak_db > 1.0
    assert small.character in ("punchy", "boomy")
    assert small.response[-1][0] == 400.0


def test_ported_box_rejects_driver_without_ts(drv):
    drv.vas_l = None
    with pytest.raises(ValueError):
        cabvoice.ported_box(drv, 40.0, 60.0)


@pytest.mark.parametrize("peak,expected", [
    (0.0, "flat"), (0.99, "flat"), (1.0, "punchy"), (2.9, "punchy"), (3.0, "boomy"), (6.0, "boomy"),
])
def test_ported_character_thresholds(peak, expected):
    assert cabvoice.ported_character(peak) == expected
