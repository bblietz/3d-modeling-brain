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
FIXTURES = next(p / "projects" / "Speaker-cab-system" / "fixtures" for p in (HERE, *HERE.parents)
                if (p / "projects" / "Speaker-cab-system" / "fixtures" / "tone-roots.json").exists())
SITE_DEFAULT = (HERE / "fixtures" / "site-default") if (HERE / "fixtures" / "site-default" / "cab.py").exists() else FIXTURES / "site-default"
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
    assert L.SHELL_MARGIN_MM == cabvoice.SHELL_MARGIN_MM == 44.0
    assert L.CUTOUT_GAP_MM == cabvoice.CUTOUT_GAP_MM == 68.0
    assert L.PORT_TUBE_OD_MM == cabvoice.PORT_TUBE_OD_MM and set(L.PORT_TUBE_OD_MM) == {52.0, 77.3, 101.5, 153.2}
    assert not hasattr(L, "FOOT_DEFAULT_INSET_MM")     # the inset lives in Aesthetics.foot_inset_mm


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
    # layout() notes the dado on every shell row it cuts, plus the cross-grain glue rule on hardwood
    dado = "; 6 mm deep x 18 mm dado for the baffle, front face 20 mm behind the front edge"
    shell = ("side_left", "side_right", "top", "bottom")
    notes = {p.name: p.notes for p in L.layout(spec).parts if p.name in shell}
    assert len(notes) == 4 and all(n.endswith(dado) for n in notes.values())
    hw = spec_for(line="hardwood", species="black walnut", aesthetics=L.Aesthetics(baffle_mount="fixed"))
    notes = {p.name: p.notes for p in L.layout(hw).parts if p.name in shell}
    assert all(n.endswith(dado + "; glued in the front 100 mm only") for n in notes.values())
    notes = {p.name: p.notes for p in L.layout(slot).parts if p.name in shell}
    assert "dado" not in notes["bottom"] and all("dado" in notes[n] for n in ("side_left", "side_right", "top"))
    assert all("dado" not in p.notes for p in L.layout(spec_for()).parts if p.name in shell)


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
    assert blanks[0].blank_mm == pytest.approx((5.8, 88.9, 40.0))     # wall x OD x length on the cut list
    assert "planed" not in blanks[1].notes
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
    assert blk and blk[0].endswith("raise Fb, use a smaller tube or a larger box, or a front slot")
    assert "no round port of 153.2 mm" in blk[0]
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
    assert "no tube" in blanks[0].notes and "planed to 8 mm" in blanks[0].notes


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


def test_round_port_blocker_remedy_shortens_the_tube():
    # the engine's port length grows as Fb falls and as the tube widens
    # (cabvoice.port_length_m), so the remedy must point the other way
    spec = spec_for(port="round")
    fr = L.frame(spec)
    _, cutouts, _ = L.baffle_and_cutouts(spec, fr)
    envs = L.speaker_envelopes(spec, fr, cutouts)
    s = sheet(port="round")
    s["port"]["length_mm"] = 240.0                  # stays behind the baffle, finds no spot
    _, _, _, blockers = L.round_ports(L.order_from(s, L.Aesthetics()), fr, envs, [])
    tail = "raise Fb, use a smaller tube or a larger box, or a front slot"
    assert blockers[0].endswith(tail) and "lower Fb" not in blockers[0]
    s["port"]["length_mm"] = 250.0                  # reaches the baffle: the same tail
    _, _, _, blockers = L.round_ports(L.order_from(s, L.Aesthetics()), fr, envs, [])
    assert blockers[0].endswith(tail)


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
    # the outboard scan runs out of wall; the below scan stops where the second
    # ring clears the first ring edge to edge (148.9 mm), not just the first tube
    assert (x0, z0) == pytest.approx((69.45, 228.6)) and (x1, z1) == pytest.approx((0.0, 94.15))
    assert math.hypot(x1 - x0, z1 - z0) >= 88.9 + 25.0 - 1e-9        # tube to tube, 25 mm clear
    assert math.hypot(x1 - x0, z1 - z0) >= 74.45 + 44.45 - 1e-9      # ring over the other tube
    assert math.hypot(x1 - x0, z1 - z0) >= 74.45 + 74.45 - 1e-9      # ring to ring, edge to edge


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
    assert all("glued up from 18 mm birch" in b.notes for b in blanks[1:])      # 86 mm cheeks
    flush = sheet(port="slot")
    flush["port"]["slot_w_mm"] = 436.0                                         # 18 mm cheeks: one thickness
    _, blanks, _ = L.slot_ports(L.order_from(flush, L.Aesthetics()), fr)
    assert [b.name for b in blanks] == ["shelf", "cheek_left", "cheek_right"]
    assert all("glued up" not in b.notes for b in blanks)
    two = spec_for(drivers=2, port="slot", external=(722.0 + 36.0, 457.2, 279.4))
    slots, blanks, blockers = L.slot_ports(two, L.frame(two))
    assert blockers == [] and len(slots) == 2 and "cheek_center_0" in [b.name for b in blanks]
    assert all("glued up" not in b.notes for b in blanks if b.name.startswith("cheek_center"))
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
               "port mouth", "magnet to back", "handle", "head match", "line", "jack plate", "stock",
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
    assert rep["external_in"] == [20.0, 18.0, 11.0] and rep["internal_mm"] == [472.0, 421.2, 229.4]
    assert rep["volumes"]["gross_l"] == [round(lay.chambers[0].gross_l, 3)]
    assert rep["mass"]["com_mm"] == [round(v, 3) for v in lay.com_mm]
    assert rep["speakers"] == ["celestion-g12h-30-anniversary"] and rep["tolex"]["roll_in"] == 54
    assert {c["name"] for c in rep["checks"]} == set(CHECK_NAMES)
    assert rep["prediction_status"] == "unverified, ears only" and "generated" in rep


def test_fixture_site_default_lays_out():
    path = SITE_DEFAULT / "voicing.json"
    if not path.exists():
        pytest.skip("fixture sheet not written yet")
    spec = L.order_from(L.load_voicing(path), L.Aesthetics(tolex_color="British Style Red"))
    lay = L.layout(spec)
    by = {c.name: c for c in L.check_layout(lay, spec)}
    assert lay.spec.external_mm == (508.0, 457.2, 279.4)
    assert all(by[n].level != "blocker" for n in CHECK_NAMES), [(n, by[n].message) for n in CHECK_NAMES if by[n].level == "blocker"]


# --- matrix: every catalog speaker x enclosure x configuration x line, on live proposals
TONE = json.loads((FIXTURES / "tone-roots.json").read_text())
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
    stats = {"cases": 0, "engine_blocked": 0, "clean": 0, "blocked": 0, "port_mouth_warn": 0}
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
                    if by["port mouth"].level == "warn":
                        stats["port_mouth_warn"] += 1
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


# ---- Plan 3 Task 2: port mouth check, aesthetics block, fixture list ----
def test_port_mouth_round_pass_and_warn():
    # 77.3 tube, 40 mm long: the mouth sits 84.4 mm behind the magnet's rear face (y 155)
    # with a 29 percent slice of it facing the magnet: over one diameter, pass
    spec = spec_for(port="round", net=42.5)
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port mouth"].level == "pass"
    assert by["port mouth"].message == ("port mouth(s) clear: chamber 0 port 0: mouth 84 mm from the "
                                        "speaker 0 magnet (29 percent of the mouth), one diameter is 77.3 mm")
    # the 101.5 tube at the same length: 84 mm is under one diameter
    s = sheet(port="round", net=42.5)
    s["port"]["diameter_mm"] = 101.5
    spec = L.order_from(s, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port mouth"].level == "warn"
    assert by["port mouth"].message == ("chamber 0 port 0: mouth 84 mm from the speaker 0 magnet "
                                        "(18 percent of the mouth), under one diameter (101.5 mm)")
    # a tube ending at the 25 mm axial standoff, inside the magnet footprint: warns and names the magnet
    s = sheet(port="round", net=42.5)
    s["port"]["length_mm"] = 99.0
    spec = L.order_from(s, L.Aesthetics())
    lay = L.layout(spec)
    (c, j, free, what, cover, d_eff), = L.port_mouth_clearances(lay)
    assert (c, j, what, d_eff) == (0, 0, "speaker 0 magnet", 77.3)
    assert free == pytest.approx(25.4) and 0.25 < cover < 0.33
    by = {ch.name: ch for ch in L.check_layout(lay, spec)}
    assert by["port mouth"].level == "warn"
    assert by["port mouth"].message.startswith("chamber 0 port 0: mouth 25 mm from the speaker 0 magnet")


def test_port_mouth_slot_no_port_and_unbuilt():
    # 1x12 slot: the bottom stiffener starts at the shelf's rear edge, so it faces the mouth at 0 mm
    spec = spec_for(port="slot", net=42.5)
    lay = L.layout(spec)
    (c, j, free, what, cover, d_eff), = L.port_mouth_clearances(lay)
    assert (c, j, free, what) == (0, 0, 0.0, "stiffener bottom")
    assert d_eff == pytest.approx(math.sqrt(4 * 300 * 40 / math.pi)) and 0.05 < cover < 0.1
    by = {ch.name: ch for ch in L.check_layout(lay, spec)}
    assert by["port mouth"].level == "warn"
    assert by["port mouth"].message == ("chamber 0 port 0: mouth 0 mm from the stiffener bottom "
                                        "(8 percent of the mouth), under one diameter (123.6 mm)")
    # a mono 2x12 with two slots: the brace splits the bottom span so there is no stiffener; the back
    # cleat is the first solid behind the mouth, 169 mm away (shelf rear edge y 80, cleat at y 249.4)
    s = sheet(external=(760.0, 457.2, 279.4), drivers=2, port="slot", net=80.0)
    s["port"]["slot_w_mm"] = 340.0
    spec = L.order_from(s, L.Aesthetics())
    by = {ch.name: ch for ch in L.check_layout(L.layout(spec), spec)}
    assert by["port mouth"].level == "pass"
    assert by["port mouth"].message.startswith(
        "port mouth(s) clear: chamber 0 port 0: mouth 169 mm from the cleat back bottom "
        "(46 percent of the mouth), one diameter is 131.6 mm; chamber 0 port 1: mouth 169 mm")
    # no port at all, and a port the layout could not place
    closed = spec_for(enclosure="closed", net=42.5)
    assert {c.name: c for c in L.check_layout(L.layout(closed), closed)}["port mouth"].message == "no port"
    s = sheet(port="round", net=42.5)
    s["port"]["length_mm"] = 250.0
    spec = L.order_from(s, L.Aesthetics())
    by = {ch.name: ch for ch in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "blocker"
    assert by["port mouth"].level == "pass" and by["port mouth"].message == "no port placed (see port fit)"


def test_port_mouth_site_default_fixture_warns_behind_the_magnet():
    path = SITE_DEFAULT / "voicing.json"
    assert path.exists(), f"fixture sheet missing: {path}"
    spec = L.order_from(L.load_voicing(path), L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "pass"
    assert by["port mouth"].level == "warn"
    assert by["port mouth"].message == ("chamber 0 port 0: mouth 84 mm from the speaker 0 magnet "
                                        "(18 percent of the mouth), under one diameter (101.5 mm)")


def test_report_carries_the_aesthetics_block():
    aest = L.Aesthetics(corner_joint="dovetail", baffle_mount="fixed", handle="recessed-side", corners="none",
                        piping=True, feet="tilt-back", tolex_roll_in=32, tolex_color="Fender Style Tweed",
                        grill_cloth="Fender Style Oxblood", head_width_mm=500.0)
    spec = spec_for(line="hardwood", species="black walnut", port="round", net=42.5, aesthetics=aest)
    lay = L.layout(spec)
    rep = L.layout_report(lay, L.check_layout(lay, spec))
    json.dumps(rep)
    block = rep["aesthetics"]
    assert len(block) == 21
    assert {k: block[k] for k in ("corner_joint", "baffle_mount", "handle", "corners", "piping", "feet",
                                  "tolex_roll_in", "tolex_color", "grill_cloth", "head_width_mm")} == {
        "corner_joint": "dovetail", "baffle_mount": "fixed", "handle": "recessed-side", "corners": "none",
        "piping": True, "feet": "tilt-back", "tolex_roll_in": 32, "tolex_color": "Fender Style Tweed",
        "grill_cloth": "Fender Style Oxblood", "head_width_mm": 500.0}
    assert block["jack_plate_cutout_mm"] == [110.0, 70.0]      # every Aesthetics field travels, tuples as lists
    assert rep["corner_joint"] == "dovetail" and rep["baffle_mount"] == "fixed"


def test_order_from_ignores_unknown_port_keys():
    plain = sheet(port="round", net=42.5)
    extra = copy.deepcopy(plain)
    extra["port"]["pinned"] = True
    extra["port"]["fb_override_hz"] = 70.0
    a, b = L.order_from(plain, L.Aesthetics()), L.order_from(extra, L.Aesthetics())
    assert a == b
    ra = L.layout_report(L.layout(a), L.check_layout(L.layout(a), a))
    rb = L.layout_report(L.layout(b), L.check_layout(L.layout(b), b))
    assert ra == rb


def test_port_fit_blocker_names_the_largest_table_tube_at_the_minimum():
    # the Cannabis Rex under the roots tone: the default proposal snaps to the 153.2 mm tube, which
    # seats nowhere in its box; the blocker names the largest table tube that fits at 24 mm
    drv = cabvoice.load_speaker("eminence-cannabis-rex")
    z = drv.impedance_ohm[0]
    v = cabvoice.propose([drv], [z], "closed-ported", TONE, "mono", cabvoice.Constraints(line="tolex"), "rex").to_dict()
    assert v["blockers"] == [] and v["port"]["diameter_mm"] == 153.2
    spec = L.order_from(v, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "blocker"
    assert by["port fit"].message == (
        "port fit: chamber 0 port 0: no round port of 153.2 mm fits with 25 mm clearance; "
        "the longest table tube that fits at the 24 mm minimum is 101.5 mm; "
        "raise Fb, use a smaller tube or a larger box, or a front slot")
    assert by["port mouth"].message == "no port placed (see port fit)"
    # the skill's next step: pin the named tube and read the next run's verdicts
    pinned = cabvoice.propose([drv], [z], "closed-ported", TONE, "mono",
                              cabvoice.Constraints(line="tolex", port_tube_mm=101.5), "rex").to_dict()
    assert pinned["port"]["pinned"] is True and pinned["port"]["length_mm"] == 24.0
    spec = L.order_from(pinned, L.Aesthetics())
    lay = L.layout(spec)
    by = {c.name: c for c in L.check_layout(lay, spec)}
    assert by["port fit"].level == "pass" and lay.round_ports[0].id_mm == 101.5
    assert by["port mouth"].level == "warn" and "under one diameter (101.5 mm)" in by["port mouth"].message


def test_port_fit_blocker_says_no_table_tube_fits():
    # a narrow, shallow box: the 24 mm tube's span overlaps the magnet's axial standoff, so every
    # direction of the scan runs into a wall or a cleat before the radial requirement is met
    s = sheet(external=(360.0, 457.2, 192.0), port="round", net=15.0)
    s["port"]["diameter_mm"] = 101.5
    spec = L.order_from(s, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["magnet to back"].level == "pass"
    assert by["port fit"].message == (
        "port fit: chamber 0 port 0: no round port of 101.5 mm fits with 25 mm clearance; "
        "no table tube fits; use a front slot or a larger box")


def test_slot_shelf_blocker_names_the_deepest_shelf():
    s = sheet(port="slot", net=42.5)
    s["port"]["length_mm"] = 220.0            # the site box: 267.4 - 20 - 40 leaves a 207 mm shelf at most
    spec = L.order_from(s, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].message == (
        "port fit: slot shelf 220 mm deep leaves 27 mm behind it, under the 40 mm the slot needs to "
        "breathe; the deepest shelf that fits is 207 mm; lower the slot height or use a round port")
    shallow = sheet(external=(508.0, 457.2, 90.0), port="slot", net=10.0)     # 40 mm of internal depth
    spec = L.order_from(shallow, L.Aesthetics())
    _, _, blockers = L.slot_ports(spec, L.frame(spec))
    assert blockers == ["port fit: slot shelf 60 mm deep leaves -2 mm behind it, under the 40 mm the slot "
                        "needs to breathe; no shelf fits; lower the slot height or use a round port"]


def test_slot_a_hair_wider_than_the_chamber_is_trimmed_to_full_width():
    # the skill's slot re-run pins the width, so a slot can land a hair over its chamber from
    # rounding; up to SLOT_TRIM_MM over, the layout trims it to the full width instead of blocking
    s = sheet(port="slot", net=42.5)                       # 472 mm chamber, one slot: avail is the chamber
    s["port"]["slot_w_mm"] = 472.0 + 0.5
    spec = L.order_from(s, L.Aesthetics())
    fr = L.frame(spec)
    slots, blanks, blockers = L.slot_ports(spec, fr)
    assert blockers == [] and len(slots) == 1
    assert (slots[0].x0, slots[0].x1) == pytest.approx((-236.0, 236.0))
    assert slots[0].cheek_w_mm == pytest.approx(0.0)
    assert [b.name for b in blanks] == ["shelf"]                    # no side cheek parts
    assert blanks[0].size == (472.0, 60.0, 18.0)                    # the shelf spans the full chamber
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "pass"
    assert by["port fit"].message == "slot port(s) built: chamber 0 slot 472 x 40 mm, shelf 60 mm"


def test_slot_over_the_trim_tolerance_still_blocks():
    s = sheet(port="slot", net=42.5)
    s["port"]["slot_w_mm"] = 472.0 + 1.5
    spec = L.order_from(s, L.Aesthetics())
    _, blanks, blockers = L.slot_ports(spec, L.frame(spec))
    assert blockers == ["port fit: chamber 0: 1 slot of 474 mm do not fit the 472 mm chamber; "
                        "narrow the slot or widen the box"]
    assert blanks == []
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "blocker"


# ---- hardwood shell panels take no stiffener ----
SHELL_STIFFENERS = {"stiffener_top", "stiffener_bottom", "stiffener_side_left", "stiffener_side_right"}


def test_hardwood_site_box_has_no_shell_stiffeners():
    assert L.NO_SHELL_STIFFENER_LINES == cabvoice.NO_SHELL_STIFFENER_LINES == ("hardwood",)
    drv = cabvoice.load_speaker(SPEAKER["slug"])
    for enclosure in ("open", "closed"):
        for line, species in (("tolex", None), ("hardwood", "black walnut")):
            c = cabvoice.Constraints(line=line, species=species)
            v = cabvoice.evaluate([drv], [16], enclosure, TONE, (472.0, 421.2, 229.4), constraints=c).to_dict()
            spec = L.order_from(v, L.Aesthetics())
            lay = L.layout(spec)
            by = {ch.name: ch for ch in L.check_layout(lay, spec)}
            case = (enclosure, line)
            shell = {p.name for p in lay.parts} & SHELL_STIFFENERS
            spans = by["spans"].message
            if line == "tolex":
                assert shell == {"stiffener_top", "stiffener_bottom"}, case
                assert "top panel span 472 mm" in spans and "bottom panel span 472 mm" in spans, case
            else:
                assert shell == set(), case
                assert all(panel not in spans for panel in ("top panel", "bottom panel", "side panel")), case
            assert any(p.name == "stiffener_back" for p in lay.parts) == (enclosure == "closed"), case
            assert by["spans"].level == ("pass" if case == ("open", "hardwood") else "warn"), case
            assert by["net volume"].level == "pass", (case, by["net volume"].message)
            assert L.layout_inside_parts_l(lay) == pytest.approx(spec.sheet_inside_parts_l, abs=0.02), case


def test_hardwood_tall_box_has_no_side_stiffeners():
    for line, species, names in (("tolex", None, ["stiffener_side_left", "stiffener_side_right"]),
                                 ("hardwood", "black walnut", [])):
        tall = spec_for(external=(470.0, 520.0, 279.4), line=line, species=species)
        parts, notes = L.stiffener_blanks(tall, L.frame(tall))
        assert [p.name for p in parts] == names and len(notes) == (1 if names else 0), line
