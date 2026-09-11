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
