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


# ---- Task 4: ports ------------------------------------------------------

def test_port_length_hand_computed():
    # Vb 40 L, Fb 60 Hz, d 75 mm: A = 4.418e-3 m2
    # L = c^2 A / (4 pi^2 Fb^2 Vb) - 0.85 d = 91.44 mm - 63.75 mm = 27.7 mm
    p = cabvoice.port_dims(40.0, 60.0, diameter_mm=75.0)
    assert p.shape == "round"
    assert p.area_cm2 == pytest.approx(44.18, abs=0.05)
    assert p.length_mm == pytest.approx(27.7, abs=0.2)
    assert p.volume_l == pytest.approx(0.1224, abs=0.002)


def test_port_tuning_inverts_length():
    fb = cabvoice.port_tuning_hz(0.040, 4.418e-3, 0.02769)
    assert fb == pytest.approx(60.0, abs=0.1)


def test_slot_port_uses_effective_diameter():
    p = cabvoice.port_dims(40.0, 60.0, slot_mm=(200.0, 22.09))
    assert p.shape == "slot"
    assert p.area_cm2 == pytest.approx(44.18, abs=0.05)
    assert p.length_mm == pytest.approx(27.7, abs=0.3)


def test_port_dims_requires_exactly_one_shape():
    with pytest.raises(ValueError):
        cabvoice.port_dims(40.0, 60.0)
    with pytest.raises(ValueError):
        cabvoice.port_dims(40.0, 60.0, diameter_mm=75.0, slot_mm=(200.0, 20.0))


def test_port_air_speed_worst_case(drv):
    # v = Sd Xmax 2 pi Fb / A = 0.053 * 0.001 * 376.99 / 4.418e-3 = 4.52 m/s
    v = cabvoice.port_air_speed(drv, 60.0, 44.18)
    assert v == pytest.approx(4.52, abs=0.05)


def test_size_port_grows_until_under_limit(drv):
    drv.xmax_mm = 10.0
    p = cabvoice.size_port(drv, 40.0, 60.0, diameter_mm=75.0)
    assert p.air_speed_ms <= cabvoice.PORT_V_MAX
    assert p.diameter_mm > 75.0
    assert p.length_mm > 0


def test_size_port_grows_when_too_short(drv):
    # 60 L at 60 Hz: a 75 mm port needs a negative length, about 100 mm works
    p = cabvoice.size_port(drv, 60.0, 60.0, diameter_mm=75.0)
    assert p.diameter_mm == pytest.approx(100.0, abs=3.0)
    assert p.length_mm >= cabvoice.MIN_PORT_LENGTH_MM
    assert not any("too short" in w for w in p.warnings)


def test_size_port_keeps_warning_at_max_size(drv):
    # 100 L at 100 Hz would need a port over 360 mm across
    p = cabvoice.size_port(drv, 100.0, 100.0, diameter_mm=75.0)
    assert p.diameter_mm == cabvoice.MAX_PORT_DIAMETER_MM
    assert p.length_mm == cabvoice.MIN_PORT_LENGTH_MM
    assert any("too short" in w for w in p.warnings)


def test_size_port_slot_stops_at_max_area(drv):
    p = cabvoice.size_port(drv, 100.0, 100.0, slot_mm=(200.0, 22.09))
    max_area_cm2 = math.pi * (cabvoice.MAX_PORT_DIAMETER_MM / 20.0) ** 2
    assert p.area_cm2 == pytest.approx(max_area_cm2, abs=1e-6)
    assert p.slot_h_mm == pytest.approx(max_area_cm2 * 100.0 / 200.0, abs=1e-6)
    assert any("too short" in w for w in p.warnings)


# ---- Task 5: open back --------------------------------------------------

def test_open_back_site_default_box():
    # internal 472 x 421.2 x 229.4 mm: path = 0.2294 + 0.236 = 0.4654 m
    # f_cancel = 343 / (2 * 0.4654) = 368.5 Hz
    res = cabvoice.open_back(472.0, 421.2, 229.4, 0.40)
    assert res.path_m == pytest.approx(0.4654, abs=0.001)
    assert res.f_cancel_hz == pytest.approx(368.5, abs=1.0)
    assert res.panel_height_mm == pytest.approx(126.4, abs=0.1)  # (1 - 0.4) * 421.2 / 2


def test_open_back_response_rolls_off_6db_per_octave():
    res = cabvoice.open_back(472.0, 421.2, 229.4, 0.40)
    table = dict(res.response)
    assert table[400.0] == pytest.approx(0.0)
    half = res.f_cancel_hz / 2
    db = cabvoice.open_back_relative_db(res.f_cancel_hz, half)
    assert db == pytest.approx(-6.02, abs=0.05)


def test_open_fraction_table():
    assert cabvoice.OPEN_FRACTION["open"] == 0.40
    assert cabvoice.OPEN_FRACTION["semi-open"] == 0.25


def test_open_back_rejects_bad_fraction():
    with pytest.raises(ValueError):
        cabvoice.open_back(472.0, 421.2, 229.4, 1.5)


def test_open_back_rejects_non_positive_dimensions():
    with pytest.raises(ValueError, match="dimensions"):
        cabvoice.open_back(472.0, 421.2, 0.0, 0.40)
    with pytest.raises(ValueError, match="dimensions"):
        cabvoice.open_back(472.0, 421.2, -300.0, 0.40)


# ---- Task 6: wiring and power -------------------------------------------

def test_wiring_two_sixteens_parallel_to_eight():
    res = cabvoice.wiring([16, 16], [4, 8, 16], "mono")
    names = {o.name: o for o in res.options}
    assert names["parallel"].impedance_ohm == pytest.approx(8.0)
    assert names["parallel"].matches_tap
    assert names["series"].impedance_ohm == pytest.approx(32.0)
    assert not names["series"].matches_tap
    assert res.recommended.name == "parallel"
    assert res.warnings == []


def test_wiring_two_eights_prefers_parallel_when_both_match():
    res = cabvoice.wiring([8, 8], [4, 8, 16], "mono")
    assert res.recommended.name == "parallel"
    assert res.recommended.impedance_ohm == pytest.approx(4.0)


def test_wiring_single_driver_no_matching_tap():
    res = cabvoice.wiring([16], [8], "mono")
    assert res.recommended is None
    assert any("no wiring option matches" in w for w in res.warnings)


def test_wiring_unequal_impedances_warn():
    res = cabvoice.wiring([8, 16], [4, 8, 16], "mono")
    assert any("unequal" in w for w in res.warnings)
    assert res.recommended is None


def test_wiring_sensitivity_mismatch_warns():
    res = cabvoice.wiring([16, 16], [8], "mono", sensitivities=[100.0, 97.0])
    assert any("sensitivity" in w for w in res.warnings)


def test_wiring_stereo_one_option_per_side():
    res = cabvoice.wiring([8, 8], [8], "stereo")
    assert [o.name for o in res.options] == ["stereo side 1", "stereo side 2"]
    assert res.recommended is not None
    with pytest.raises(ValueError):
        cabvoice.wiring([8], [8], "stereo")


def test_wiring_parallel_out_adds_note():
    res = cabvoice.wiring([16, 16], [8], "mono-parallel-out")
    assert any("Parallel out" in w for w in res.warnings)


def test_wiring_rejects_bad_config_and_count():
    with pytest.raises(ValueError):
        cabvoice.wiring([8], [8], "quad")
    with pytest.raises(ValueError):
        cabvoice.wiring([8, 8, 8], [8], "mono")


def test_power_check_rule():
    stop = cabvoice.power_check([15], 30)
    assert stop.status == "stop" and stop.min_power_w == 45
    warn = cabvoice.power_check([15, 15], 30)
    assert warn.status == "warning"
    accepted = cabvoice.power_check([15, 15], 30, breakup="early", accept_low_headroom=True)
    assert accepted.status == "ok" and "accepted" in accepted.message
    not_accepted = cabvoice.power_check([15, 15], 30, breakup="clean", accept_low_headroom=True)
    assert not_accepted.status == "warning"
    ok = cabvoice.power_check([60], 30)
    assert ok.status == "ok" and ok.total_handling_w == 60
