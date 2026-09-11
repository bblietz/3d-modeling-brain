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
    assert L.SHELL_MARGIN_MM == 44.0 and L.CUTOUT_GAP_MM == 68.0 and L.CUTOUT_MARGIN_MM == 25.0
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
