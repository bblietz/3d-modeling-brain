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
    # Eminence's sealed Beta-12A-2 design (0.904 cu ft) publishes F3 92.1 Hz; the
    # engine reads 86.0 Hz (6.6 percent low, see the voicing note's model limits).
    drv = _driver(**BETA_12A2)
    res = cabvoice.closed_box(drv, 0.904 * CU_FT_L)
    assert res.f3_hz == pytest.approx(86.0, abs=1.0)


def test_ported_box_reports_peak_and_character():
    drv = _driver(**DELTA_12A)
    small = cabvoice.ported_box(drv, 0.75 * CU_FT_L, 110.0)
    assert small.peak_db == pytest.approx(5.81, abs=0.1)
    assert small.character == "boomy"
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


def test_size_port_warns_still_above_limit(drv):
    drv.xmax_mm = 30.0
    p = cabvoice.size_port(drv, 100.0, 100.0, diameter_mm=75.0)
    assert p.diameter_mm == cabvoice.MAX_PORT_DIAMETER_MM
    assert p.air_speed_ms > cabvoice.PORT_V_MAX
    assert any("still above" in w for w in p.warnings)


def test_port_dims_rejects_non_positive_geometry():
    with pytest.raises(ValueError, match="diameter"):
        cabvoice.port_dims(40.0, 60.0, diameter_mm=0.0)
    with pytest.raises(ValueError, match="slot"):
        cabvoice.port_dims(40.0, 60.0, slot_mm=(200.0, -5.0))


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


def test_power_check_rejects_non_positive_amp_power():
    with pytest.raises(ValueError, match="amp_power_w"):
        cabvoice.power_check([30.0], 0.0)
    with pytest.raises(ValueError, match="amp_power_w"):
        cabvoice.power_check([30.0], -30.0)


# ---- Task 7: box geometry -----------------------------------------------

def test_site_default_box_dimensions():
    box = cabvoice.site_default_box()
    assert box.external_mm == pytest.approx((508.0, 457.2, 279.4))
    assert box.internal_mm == pytest.approx((472.0, 421.2, 229.4))
    assert box.gross_l == pytest.approx(45.6, abs=0.05)


def test_internal_external_roundtrip():
    ext = (600.0, 500.0, 300.0)
    assert cabvoice.external_from_internal(cabvoice.internal_from_external(ext)) == pytest.approx(ext)


def test_make_box_rejects_non_positive_internals():
    with pytest.raises(ValueError, match="positive"):
        cabvoice.make_box((472.0, 0.0, 229.4))


def test_dims_for_volume_reproduces_base():
    box = cabvoice.dims_for_volume(45.6)
    assert box.internal_mm == pytest.approx((472.0, 421.2, 229.4), abs=0.5)


def test_dims_for_volume_pinned_width_keeps_h_d_ratio():
    box = cabvoice.dims_for_volume(60.0, pinned_external_width_mm=508.0)
    w, h, d = box.internal_mm
    assert w == pytest.approx(472.0)
    assert h / d == pytest.approx(421.2 / 229.4, rel=1e-6)
    assert box.gross_l == pytest.approx(60.0, abs=0.01)


def test_dims_for_volume_min_width_for_two_drivers():
    min_w = cabvoice.min_internal_width_mm(2, 283.0)
    assert min_w == pytest.approx(641.0)
    box = cabvoice.dims_for_volume(90.0, min_internal_width_mm=min_w)
    assert box.internal_mm[0] == pytest.approx(641.0)
    assert box.gross_l == pytest.approx(90.0, abs=0.01)


def test_dims_for_volume_clamps_to_max_external():
    box = cabvoice.dims_for_volume(60.0, max_external_mm=(600.0, 457.2, 400.0))
    w, h, d = box.internal_mm
    assert h == pytest.approx(421.2)
    assert box.external_mm[0] <= 600.0 and box.external_mm[2] <= 400.0
    assert box.gross_l == pytest.approx(60.0, abs=0.01)


def test_dims_for_volume_raises_when_limits_too_small():
    with pytest.raises(ValueError, match="cannot reach"):
        cabvoice.dims_for_volume(60.0, max_external_mm=(508.0, 457.2, 279.4))


def test_dims_for_volume_non_strict_returns_the_box_that_fits():
    box = cabvoice.dims_for_volume(60.0, max_external_mm=(508.0, 457.2, 279.4), strict=False)
    assert box.gross_l == pytest.approx(45.6, abs=0.05)
    assert any(w.startswith("cannot reach 60.0 L") for w in box.warnings)


def test_dimension_ratio_warnings():
    assert cabvoice.dimension_ratio_warnings((472.0, 400.0, 300.0)) == []
    assert any("2:1" in w for w in cabvoice.dimension_ratio_warnings((472.0, 421.2, 229.4)))
    assert any("1:1" in w for w in cabvoice.dimension_ratio_warnings((400.0, 400.0, 300.0)))


def test_dims_for_volume_warns_when_pinned_width_below_minimum():
    box = cabvoice.dims_for_volume(60.0, pinned_external_width_mm=508.0, min_internal_width_mm=641.0)
    assert box.internal_mm[0] == pytest.approx(641.0)
    assert any("pinned width" in w for w in box.warnings)


def test_dims_for_volume_rejects_fixed_width_over_limit():
    with pytest.raises(ValueError, match="size limit"):
        cabvoice.dims_for_volume(90.0, pinned_external_width_mm=700.0, max_external_mm=(600.0, 457.2, 400.0))
    with pytest.raises(ValueError, match="size limit"):
        cabvoice.dims_for_volume(90.0, min_internal_width_mm=641.0, max_external_mm=(600.0, 457.2, 400.0))


def test_dims_for_volume_rejects_non_positive_volume():
    with pytest.raises(ValueError, match="gross_l"):
        cabvoice.dims_for_volume(0.0)
    with pytest.raises(ValueError, match="gross_l"):
        cabvoice.dims_for_volume(-10.0)


# ---- Task 8: tone target and propose ------------------------------------

TONE_FIXTURE = Path(__file__).parent.parent / "projects/Speaker-cab-system/fixtures/tone-roots.json"


@pytest.fixture()
def tone():
    return json.loads(TONE_FIXTURE.read_text())


def test_validate_tone_target_ok(tone):
    assert cabvoice.validate_tone_target(tone) == []


def test_validate_tone_target_reports_bad_values(tone):
    tone["low_end"] = "huge"
    tone["min_power_w"] = 0
    del tone["impedance_options_ohm"]
    errors = cabvoice.validate_tone_target(tone)
    assert any("low_end" in e for e in errors)
    assert any("min_power_w" in e for e in errors)
    assert any("impedance_options_ohm" in e for e in errors)


def test_per_driver_net_uses_alpha_and_clamps(drv):
    net, method, warns = cabvoice.per_driver_net_l(drv, "closed-ported", "balanced")
    assert method == "thiele-small" and net == pytest.approx(60.0) and warns == []
    net, _, warns = cabvoice.per_driver_net_l(drv, "closed-ported", "big")
    assert net == pytest.approx(cabvoice.NET_L_RANGE[1])
    assert any("clamped" in w for w in warns)
    net, method, _ = cabvoice.per_driver_net_l(drv, "open", "big")
    assert method == "rule-of-thumb" and net == cabvoice.RULE_OF_THUMB_NET_L["big"]


def test_per_driver_net_without_ts_is_rule_of_thumb(drv):
    drv.qts = None
    net, method, warns = cabvoice.per_driver_net_l(drv, "closed", "tight")
    assert method == "rule-of-thumb" and net == 34.0
    assert any("no Thiele-Small" in w for w in warns)


def test_ported_targets_grows_then_lowers_fb():
    # Qts 1.0, Vas 20 L: boomy at every step, so the box grows in 10 percent
    # steps to the last one under 68 L (64.3 L), then Fb drops 5 Hz at a time to 45.
    d = _driver(qts=1.0, vas_l=20.0)
    vb, fb, res, warns = cabvoice.ported_targets(d, 30.0, "balanced")
    assert vb == pytest.approx(64.3, abs=0.05) and fb == 45.0
    assert res.character == "boomy"
    assert any("stays boomy" in w for w in warns)


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
        v.volumes["net_total_l"] + v.volumes["displacement_l"] + v.volumes["port_l"], abs=0.05)
    assert v.prediction_status == "unverified, ears only"


def test_propose_open_2x12_mono(drv, tone):
    v = cabvoice.propose([drv, drv], [16, 16], "open", tone, jack_config="mono")
    assert v.enclosure["chambers"] == 1 and v.enclosure["driver_count"] == 2
    assert v.enclosure["open_fraction"] == 0.40
    assert v.volumes["method"] == "rule-of-thumb"
    assert v.box["internal_mm"][0] >= cabvoice.min_internal_width_mm(2, 283.0)
    assert v.port is None
    assert "f_cancel_hz" in v.prediction
    assert v.wiring["recommended"]["name"] == "parallel"


def test_propose_stereo_2x12_closed(drv, tone):
    tone["impedance_options_ohm"] = [16]
    v = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="stereo")
    assert v.enclosure["chambers"] == 2
    assert v.volumes["divider_l"] > 0
    assert len(v.wiring["options"]) == 2
    assert len(v.power["per_side"]) == 2
    assert v.prediction["model"] == "thiele-small closed"
    assert v.box["chamber_internal_width_mm"] >= cabvoice.min_internal_width_mm(1, drv.cutout_mm)


def test_propose_stereo_volumes_reconcile(drv, tone):
    tone["impedance_options_ohm"] = [16]
    v = cabvoice.propose([drv, drv], [16, 16], "closed-ported", tone, jack_config="stereo")
    vol = v.volumes
    parts = vol["net_total_l"] + vol["displacement_l"] + vol["brace_l"] + vol["port_l"] + vol["divider_l"]
    assert vol["gross_l"] == pytest.approx(parts, abs=0.01)
    assert vol["port_l"] == pytest.approx(2 * v.port["volume_l"], abs=1e-6)


def test_propose_without_ts_degrades(drv, tone):
    for key in cabvoice.TS_FIELDS:
        setattr(drv, key, None)
    drv.data_status = "missing"
    v = cabvoice.propose([drv], [16], "closed-ported", tone)
    assert v.volumes["method"] == "rule-of-thumb"
    assert v.prediction["model"] == "rule-of-thumb"
    assert v.port is not None
    assert any("no Thiele-Small" in w for w in v.warnings)
    assert any("assumed Sd" in w for w in v.warnings)


def test_propose_blocks_on_taps_and_power(drv, tone):
    tone["impedance_options_ohm"] = [4]
    tone["min_power_w"] = 300
    v = cabvoice.propose([drv], [16], "closed", tone)
    assert any("impedance taps" in b for b in v.blockers)
    assert any("below the amp" in b for b in v.blockers)


def test_propose_honours_pinned_width(drv, tone):
    c = cabvoice.Constraints(pinned_external_width_mm=660.0)
    v = cabvoice.propose([drv], [16], "closed", tone, constraints=c)
    assert v.box["external_mm"][0] == pytest.approx(660.0)


def test_propose_impossible_box_presents_tradeoff(drv, tone, speakers_dir, tmp_path):
    tone["low_end"] = "big"                  # 68 L per driver against the site's 45.6 L box
    c = cabvoice.Constraints(max_external_mm=(508.0, 457.2, 279.4))
    v = cabvoice.propose([drv], [16], "closed", tone, constraints=c)
    assert v.volumes["gross_l"] == pytest.approx(45.6, abs=0.05)
    assert v.prediction["qtc"] == pytest.approx(cabvoice.closed_box(drv, v.volumes["per_driver_net_l"]).qtc)
    blocker = next(b for b in v.blockers if "cannot fit the size limit" in b)
    assert "69.5 L" in blocker and "45.6 L" in blocker and "Qtc" in blocker
    assert not any("cannot reach" in w for w in v.warnings)
    big_tone = tmp_path / "tone.json"
    big_tone.write_text(json.dumps(tone))
    out = tmp_path / "out"
    rc = cabvoice.main(["propose", "--speakers-dir", str(speakers_dir), "--speaker", "test-driver",
                        "--impedance", "16", "--enclosure", "closed", "--tone", str(big_tone),
                        "--max-external", "508", "457.2", "279.4", "--out", str(out)])
    assert rc == 2
    assert "cannot fit the size limit" in json.loads((out / "voicing.json").read_text())["blockers"][0]


def test_propose_rejects_bad_inputs(drv, tone):
    with pytest.raises(ValueError):
        cabvoice.propose([drv], [16], "bandpass", tone)
    with pytest.raises(ValueError):
        cabvoice.propose([drv], [16], "closed", tone, jack_config="stereo")
    tone["top"] = "sparkly"
    with pytest.raises(ValueError):
        cabvoice.propose([drv], [16], "closed", tone)


# ---- Task 9: evaluate, writers, CLI -------------------------------------

SITE_INTERNAL = (472.0, 421.2, 229.4)


def test_evaluate_site_default_closed(drv, tone):
    v = cabvoice.evaluate([drv], [16], "closed", tone, SITE_INTERNAL, name="site-closed")
    assert v.mode == "evaluate"
    assert v.volumes["gross_l"] == pytest.approx(45.6, abs=0.05)
    assert v.volumes["net_total_l"] == pytest.approx(44.1, abs=0.05)
    # alpha = 60 / 44.1 = 1.36, Qtc = 0.4 * sqrt(2.36) = 0.614
    assert v.prediction["qtc"] == pytest.approx(0.614, abs=0.005)
    assert v.prediction["character"] == "tight"
    assert v.box["external_in"] == pytest.approx((20.0, 18.0, 11.0), abs=0.01)


def test_evaluate_ported_reports_tuning_from_port(drv, tone):
    port = cabvoice.port_dims(44.0, 70.0, diameter_mm=100.0)
    port.length_mm = 23.0
    v = cabvoice.evaluate([drv], [16], "closed-ported", tone, SITE_INTERNAL, port=port)
    assert 65.0 < v.prediction["fb_hz"] < 75.0
    assert v.volumes["port_l"] == pytest.approx(0.18, abs=0.01)
    assert v.port["length_mm"] == 23.0
    assert v.port["air_speed_ms"] > 0
    assert v.port["volume_l"] == pytest.approx(v.volumes["port_l"], abs=1e-6)


def test_evaluate_requires_port_for_ported(drv, tone):
    with pytest.raises(ValueError, match="port"):
        cabvoice.evaluate([drv], [16], "closed-ported", tone, SITE_INTERNAL)


def test_evaluate_surfaces_port_warnings(drv, tone):
    port = cabvoice.port_dims(44.0, 70.0, diameter_mm=100.0)
    port.length_mm = 23.0
    port.warnings = ["port note from sizing"]
    v = cabvoice.evaluate([drv], [16], "closed-ported", tone, SITE_INTERNAL, port=port)
    assert "port note from sizing" in v.warnings


def test_evaluate_rejects_port_on_closed(drv, tone):
    port = cabvoice.port_dims(44.0, 70.0, diameter_mm=100.0)
    with pytest.raises(ValueError, match="closed enclosure"):
        cabvoice.evaluate([drv], [16], "closed", tone, SITE_INTERNAL, port=port)


def test_evaluate_open_back(drv, tone):
    v = cabvoice.evaluate([drv], [16], "open", tone, SITE_INTERNAL)
    assert v.prediction["f_cancel_hz"] == pytest.approx(368.5, abs=1.0)


def test_write_voicing_and_markdown(drv, tone, tmp_path):
    v = cabvoice.propose([drv], [16], "closed-ported", tone, name="Cab-Test-1x12-tolex")
    json_path, md_path = cabvoice.write_voicing(v, tmp_path)
    data = json.loads(json_path.read_text())
    assert data["name"] == "Cab-Test-1x12-tolex"
    assert data["prediction_status"] == "unverified, ears only"
    md = md_path.read_text()
    assert md.startswith("---\nname: cab-test-1x12-tolex-voicing\n")
    assert "unverified, ears only" in md
    assert "## Wiring" in md and "## Prediction" in md
    assert "Port" in md


def test_cli_propose_and_list(speakers_dir, tmp_path):
    out = tmp_path / "out"
    cmd = [sys.executable, str(Path(cabvoice.__file__)), "propose",
           "--speakers-dir", str(speakers_dir), "--speaker", "test-driver",
           "--impedance", "16", "--enclosure", "closed-ported",
           "--tone", str(TONE_FIXTURE), "--name", "cli-test", "--out", str(out)]
    run = subprocess.run(cmd, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert (out / "voicing.json").exists() and (out / "voicing.md").exists()
    listed = subprocess.run([sys.executable, str(Path(cabvoice.__file__)), "list",
                             "--speakers-dir", str(speakers_dir)],
                            capture_output=True, text=True)
    assert listed.stdout.strip() == "test-driver"


def test_voicing_json_has_construction_block(drv, tone, tmp_path):
    c = cabvoice.Constraints(pinned_external_width_mm=660.0, brace_l=0.3)
    v = cabvoice.propose([drv], [16], "closed-ported", tone, constraints=c)
    json_path, _ = cabvoice.write_voicing(v, tmp_path)
    con = json.loads(json_path.read_text())["construction"]
    assert con == {"panel_mm": 18.0, "back_mm": 12.0, "baffle_mm": 18.0, "recess_mm": 20.0,
                   "brace_l": 0.3, "pinned_external_width_mm": 660.0, "max_external_mm": None,
                   "port_count": 1}
    closed = cabvoice.propose([drv], [16], "closed", tone)
    assert closed.construction["port_count"] is None


def test_cli_evaluate_ported(speakers_dir, tmp_path):
    out = tmp_path / "out"
    cmd = [sys.executable, str(Path(cabvoice.__file__)), "evaluate",
           "--speakers-dir", str(speakers_dir), "--speaker", "test-driver",
           "--impedance", "16", "--enclosure", "closed-ported", "--tone", str(TONE_FIXTURE),
           "--internal", "472", "421.2", "229.4", "--port-diameter", "100", "--port-length", "23",
           "--out", str(out)]
    run = subprocess.run(cmd, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    data = json.loads((out / "voicing.json").read_text())
    assert data["mode"] == "evaluate" and 65.0 < data["prediction"]["fb_hz"] < 75.0
    assert data["port"]["count"] == 1 and data["port"]["location"] == "rear"
    assert "16 ohm" in (out / "voicing.md").read_text()


def test_cli_exit_code_2_on_blockers(speakers_dir, tmp_path):
    blocked_tone = tmp_path / "tone.json"
    blocked_tone.write_text(json.dumps({
        "low_end": "tight", "mids": "neutral", "top": "smooth", "breakup": "clean",
        "dispersion": "focused", "placement": "floor", "min_power_w": 60,
        "impedance_options_ohm": [4]}))
    out = tmp_path / "out"
    cmd = [sys.executable, str(Path(cabvoice.__file__)), "propose",
           "--speakers-dir", str(speakers_dir), "--speaker", "test-driver",
           "--impedance", "16", "--enclosure", "closed", "--tone", str(blocked_tone),
           "--out", str(out)]
    run = subprocess.run(cmd, capture_output=True, text=True)
    assert run.returncode == 2
    assert (out / "voicing.json").exists()


# ---- Task 15: catalog ---------------------------------------------------

CATALOG = Path(__file__).parent.parent / "knowledge/speakers"


def test_catalog_has_twenty_valid_notes():
    slugs = cabvoice.list_speakers(CATALOG)
    assert len(slugs) >= 20
    for slug in slugs:
        text = (CATALOG / f"{slug}.md").read_text()
        meta = cabvoice.parse_frontmatter(text)
        assert cabvoice.validate_speaker(meta) == [], slug
        assert meta["name"] == slug, slug
        assert "## Field notes" in text and "## Character" in text, slug
        drv = cabvoice.load_speaker(slug, CATALOG)
        assert drv.cutout_mm > 270 and drv.bolt_circle_mm > drv.cutout_mm, slug


def test_catalog_analog_notes_point_at_existing_notes():
    slugs = set(cabvoice.list_speakers(CATALOG))
    for slug in slugs:
        drv = cabvoice.load_speaker(slug, CATALOG)
        if drv.data_status == "analog":
            assert drv.analog_of in slugs, slug


# Mirrors the amp-family and genre row labels in knowledge/speaker-cab-voicing.md.
AMP_FAMILIES = ("Blackface Fender", "Tweed Fender", "Marshall", "Vox", "Modern high gain",
                "Boutique clean", "Modeling and solid state")
GENRES = ("Roots, country, alt-country", "Blues", "Classic rock", "Indie and alternative", "Jazz",
          "Metal and modern high gain", "Worship and pop", "Funk and R&B")


def test_catalog_best_with_uses_table_labels():
    voicing = (Path(__file__).parent.parent / "knowledge/speaker-cab-voicing.md").read_text()
    for label in AMP_FAMILIES + GENRES:
        assert f"| {label} |" in voicing, label
    for slug in cabvoice.list_speakers(CATALOG):
        text = (CATALOG / f"{slug}.md").read_text()
        best_with = text.split("## Best with", 1)[1].split("\n## ", 1)[0]
        line = next(l for l in best_with.splitlines() if l.startswith("- Amp families:"))
        assert any(f in line for f in AMP_FAMILIES), slug
        assert any(g in line for g in GENRES), slug
        assert "[[speaker-cab-voicing]]" in line, slug


def test_every_catalog_speaker_proposes_without_exception(tone):
    for slug in cabvoice.list_speakers(CATALOG):
        drv = cabvoice.load_speaker(slug, CATALOG)
        z = 16 if 16 in drv.impedance_ohm else drv.impedance_ohm[0]
        for enclosure in cabvoice.ENCLOSURE_TYPES:
            v = cabvoice.propose([drv], [z], enclosure, tone, name=slug)
            assert v.volumes["gross_l"] > v.volumes["net_total_l"] > 0, (slug, enclosure)


# ---- Final review: propose versus evaluate, calibration table -----------

def _matrix_params():
    return [pytest.param(slug, enclosure, jack, n, id=f"{slug}-{enclosure}-{jack}-{n}")
            for slug in cabvoice.list_speakers(CATALOG)
            for enclosure in cabvoice.ENCLOSURE_TYPES
            for jack, n in (("mono", 1), ("mono", 2), ("stereo", 2))]


def _port_from_json(port_dict):
    if port_dict is None:
        return None
    slot = None if port_dict["shape"] == "round" else (port_dict["slot_w_mm"], port_dict["slot_h_mm"])
    port = cabvoice.port_dims(1.0, 1.0, diameter_mm=port_dict["diameter_mm"], slot_mm=slot)
    port.length_mm = port_dict["length_mm"]
    port.warnings = []
    return port


@pytest.mark.parametrize("slug,enclosure,jack,n", _matrix_params())
def test_evaluate_reproduces_propose(tone, slug, enclosure, jack, n):
    d = cabvoice.load_speaker(slug, CATALOG)
    z = 16 if 16 in d.impedance_ohm else d.impedance_ohm[0]
    p = cabvoice.propose([d] * n, [z] * n, enclosure, tone, jack_config=jack, name=slug)
    e = cabvoice.evaluate([d] * n, [z] * n, enclosure, tone, p.box["internal_mm"],
                          jack_config=jack, port=_port_from_json(p.port), name=slug)
    for key, tol in (("fb_hz", 0.05), ("f3_hz", 0.05), ("peak_db", 0.01), ("qtc", 0.01)):
        a, b = p.prediction.get(key), e.prediction.get(key)
        assert (a is None) == (b is None), key
        if a is not None:
            assert a == pytest.approx(b, abs=tol), key
    assert p.prediction["character"] == e.prediction["character"]
    assert p.volumes["per_driver_net_l"] == pytest.approx(e.volumes["per_driver_net_l"], abs=0.05)


def test_propose_prediction_follows_clamped_port(tone):
    # Fs 111 Hz puts the tight Fb at the 90 Hz cap; Vas 90 L gives a 60 L box, where
    # even a 150 mm port needs less than 20 mm and is clamped, so the port tunes lower.
    d = _driver(fs_hz=111.0, vas_l=90.0)
    v = cabvoice.propose([d], [16], "closed-ported", tone)
    assert v.port["diameter_mm"] == cabvoice.MAX_PORT_DIAMETER_MM
    assert v.port["length_mm"] == cabvoice.MIN_PORT_LENGTH_MM
    actual = cabvoice.port_tuning_hz(v.volumes["per_chamber_net_l"] / 1e3,
                                     v.port["area_cm2"] / 1e4, v.port["length_mm"] / 1e3)
    assert actual < 89.0
    assert v.prediction["fb_hz"] == pytest.approx(actual, abs=1e-9)
    assert any(w.startswith("port clamped at the size cap: tuned") for w in v.warnings)


CANNABIS_REX = dict(name="cannabis-rex-like", fs_hz=96, qts=0.64, qes=0.69, qms=9.28, vas_l=45.48,
                    xmax_mm=0.8, sd_cm2=532.4, re_ohm=6.56, power_w=50, sensitivity_db=101.8,
                    cutout_mm=281.2, bolt_circle_mm=294.4, bolt_count=8, displacement_l=2.0)


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
    assert single.port["count"] == 1 and single.port["diameter_mm"] > two.port["diameter_mm"]


def _calibration_module():
    import importlib.util
    path = Path(__file__).parent.parent / "projects/Speaker-cab-system/pipeline/calibration_table.py"
    spec = importlib.util.spec_from_file_location("calibration_table", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_calibration_table_matches_engine():
    cal = _calibration_module()
    text = (Path(__file__).parent.parent / "knowledge/speaker-cab-voicing.md").read_text()
    section = text.split("## Calibration table", 1)[1].split("\n## ", 1)[0]
    assert f'prediction_status "{cabvoice.PREDICTION_STATUS}"' in section
    assert cal.note_rows(text) == cal.calibration_rows()
