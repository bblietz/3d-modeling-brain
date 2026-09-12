"""Tests for cabmodel.py (Plan 2 Tasks 8 to 12). Run from the mirror root:
.venv/bin/python -m pytest test_cabmodel.py -q  (CAB_FULL_MATRIX=1 for all sixty builds)"""
import copy
import json
import math
import os
import subprocess
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
import cabmodel as M  # noqa: E402

# === TASK 8 ===
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


def _union(solids):
    u = solids[0]
    for s in solids[1:]:
        u = u + s
    return u


@pytest.mark.parametrize("line,species,joint", [("tolex", None, "finger"),
                                                ("hardwood", "black walnut", "finger"),
                                                ("hardwood", "black walnut", "dovetail")])
def test_shell_solids_match_the_layout_and_interleave(line, species, joint):
    spec = spec_for(line=line, species=species, aesthetics=L.Aesthetics(corner_joint=joint))
    blanks = L.shell_blanks(spec)
    solids = [M.blank_solid(b) for b in blanks]
    for b, s in zip(blanks, solids):
        assert len(s.solids()) == 1 and s.label == b.name
        # every finger or tail present: the CAD volume equals the analytic blank volume
        assert abs(s.volume - L.blank_volume_mm3(b)) < 1.0, b.name
    W, H, D = spec.external_mm
    t = spec.shell_mm
    full = 2 * t * D * H + 2 * t * D * W
    corner_blocks = 4 * t * t * D
    union = _union(solids)
    assert len(union.solids()) == 1
    assert abs(union.volume - (full - corner_blocks)) < 1.0
    assert abs(union.volume - sum(s.volume for s in solids)) < 1.0    # no overlap anywhere


def test_feature_tools_grow_past_blank_faces():
    b = L.Blank("probe", 1, "baltic birch 18 mm", 680.0, pos=(0.0, 0.0, 0.0), size=(100.0, 50.0, 18.0),
                features=[{"type": "notch", "box": ((0.0, 0.0, 0.0), (10.0, 10.0, 18.0))},
                          {"type": "rect_hole", "axis": "y", "center": (50.0, 9.0), "w": 20.0, "h": 6.0},
                          {"type": "holes", "centers": [(80.0, 9.0)], "d": 6.5}])
    s = M.blank_solid(b)
    expected = 100 * 50 * 18 - 10 * 10 * 18 - 20 * 6 * 50 - math.pi / 4 * 6.5 ** 2 * 50
    assert abs(s.volume - expected) < 0.5
    assert abs(s.volume - L.blank_volume_mm3(b)) < 0.5
    bb = s.bounding_box()
    assert abs(bb.min.X) < 1e-6 and abs(bb.max.X - 100.0) < 1e-6   # tools never scar the outside


def test_tube_and_ring_solids():
    tube = L.Blank("port_tube_0_0", 1, "PVC 3 in sch 40", 1400.0, shape="tube",
                   pos=(0.0, 200.0, 100.0), size=(88.9, 60.0, 77.3), blank_mm=(0.0, 88.9, 60.0))
    ring = L.Blank("port_ring_0_0", 1, "baltic birch 12 mm", 680.0, shape="ring",
                   pos=(0.0, 248.0, 100.0), size=(148.9, 12.0, 88.9), blank_mm=(12.0, 148.9, 148.9))
    for b in (tube, ring):
        s = M.blank_solid(b)
        assert abs(s.volume - L.blank_volume_mm3(b)) < 1.0
        bb = s.bounding_box()
        assert abs(bb.min.Y - b.pos[1]) < 1e-6 and abs(bb.max.Y - (b.pos[1] + b.size[1])) < 1e-6


def test_part_entry_carries_blank_dims_for_the_cut_list():
    spec = spec_for()
    b = L.shell_blanks(spec)[0]
    e = M.part_entry(b, M.blank_solid(b))
    assert e["dims"] == b.blank_mm and e["length_axis"] == "Y" and e["material"] == b.material
    assert "finger joint" in e["notes"]


def test_render_writes_a_png(tmp_path):
    spec = spec_for()
    png = M.render([M.blank_solid(b) for b in L.shell_blanks(spec)], tmp_path / "shell.png",
                   views=[(30, -60)])
    assert png.exists() and png.stat().st_size > 10_000


# === TASK 9 ===
def _layout_2x12_slot():
    spec = spec_for(drivers=2, port="slot", net=74.0, external=(760.0, 480.0, 300.0))
    return spec, L.layout(spec)


def test_interior_solids_match_their_blanks_and_never_overlap():
    spec, lay = _layout_2x12_slot()
    inter = M.interior_solids(lay)
    names = sorted(inter)
    assert {"baffle", "brace", "shelf", "cheek_center_0", "cheek_left", "cheek_right",
            "grill_top", "grill_bottom", "grill_left", "grill_right",
            "cleat_baffle_top", "cleat_baffle_left", "cleat_baffle_right",
            "cleat_back_top", "cleat_back_bottom", "cleat_back_left", "cleat_back_right",
            "stiffener_back"} == set(names)
    by = {p.name: p for p in lay.parts}
    for name, s in inter.items():
        assert len(s.solids()) == 1, name
        assert abs(s.volume - L.blank_volume_mm3(by[name])) < 1.0, name
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert M.assert_no_overlap(inter[a], inter[b]) <= 1.0, (a, b)


def test_baffle_volume_with_cutouts_and_bolts_is_analytic():
    spec, lay = _layout_2x12_slot()
    baffle = next(p for p in lay.parts if p.name == "baffle")
    s = M.blank_solid(baffle)
    dx, dy, dz = baffle.size
    holes = sum(len(f["centers"]) for f in baffle.features if f["type"] == "holes")
    cutouts = [f["d"] for f in baffle.features if f["type"] == "cutout"]
    expected = dx * dy * dz - sum(math.pi / 4 * d ** 2 * dy for d in cutouts) \
        - holes * math.pi / 4 * L.BOLT_HOLE_MM ** 2 * dy
    assert len(cutouts) == 2 and holes == 8
    assert abs(s.volume - expected) < 1.0


def test_brace_notch_and_grill_half_laps():
    spec, lay = _layout_2x12_slot()
    by = {p.name: p for p in lay.parts}
    brace = M.blank_solid(by["brace"])
    bw, bd = L.BRACE_MM
    _, _, bz = by["brace"].size
    notch = bw * (L.CLEAT_MM - L.BRACE_SETBACK_MM) * L.CLEAT_MM     # top cleat notch only (slot: no bottom cleat)
    assert abs(brace.volume - (bw * bd * bz - notch)) < 1.0
    strips = {n: M.blank_solid(by[n]) for n in ("grill_top", "grill_bottom", "grill_left", "grill_right")}
    union = _union(list(strips.values()))
    assert len(union.solids()) == 1
    assert abs(union.volume - sum(s.volume for s in strips.values())) < 1.0
    t, w = L.GRILL_STRIP_T_MM, L.GRILL_STRIP_W_MM
    lap = w * w * t / 2.0
    top = by["grill_top"]
    assert abs(strips["grill_top"].volume - (top.size[0] * t * w - 2 * lap)) < 1.0


def test_overlap_volume_reports_real_collisions():
    a = M._box(0, 0, 0, 10, 10, 10)
    b = M._box(5, 0, 0, 15, 10, 10)
    c = M._box(10, 0, 0, 20, 10, 10)
    assert abs(M.overlap_volume(a, b) - 500.0) < 1e-6
    assert M.assert_no_overlap(a, c) < 1e-6
    with pytest.raises(AssertionError, match="unlabeled overlaps unlabeled by 500.0 mm3"):
        M.assert_no_overlap(a, b)


def test_overlap_volume_surfaces_a_failed_boolean(monkeypatch):
    a = M._box(0, 0, 0, 10, 10, 10).solids()[0]
    b = M._box(5, 0, 0, 15, 10, 10).solids()[0]
    monkeypatch.setattr(type(a), "intersect", lambda self, *args, **kw: None)
    assert M.overlap_volume(a, b) == 0.0        # None is build123d's "no intersection", not a failure

    def failing(self, *args, **kw):
        raise RuntimeError("forced boolean failure")
    monkeypatch.setattr(type(a), "intersect", failing)
    with pytest.raises(RuntimeError, match="forced boolean failure"):
        M.overlap_volume(a, b)
    with pytest.raises(RuntimeError, match="forced boolean failure"):
        M.assert_no_overlap(a, b)


# === TASK 10 ===
def test_back_and_port_solids_site_box():
    spec = spec_for(port="round")
    lay = L.layout(spec)
    backs, ports = M.back_solids(lay), M.port_solids(lay)
    assert set(backs) == {"back"} and set(ports) == {"port_tube_0_0", "port_ring_0_0"}
    by = {p.name: p for p in lay.parts}
    for name, s in list(backs.items()) + list(ports.items()):
        assert abs(s.volume - L.blank_volume_mm3(by[name])) < 1.0, name
    rp = lay.round_ports[0]
    back = backs["back"]
    W, H, D = spec.external_mm
    # the back carries the tube hole and the jack plate hole
    plate_w, plate_h = spec.aesthetics.jack_plate_cutout_mm
    full = (W - 36.0) * L.BACK_MM * (H - 36.0)
    expected = full - math.pi / 4 * rp.od_mm ** 2 * L.BACK_MM - plate_w * plate_h * L.BACK_MM
    assert abs(back.volume - expected) < 1.0
    for p in ports.values():
        assert M.assert_no_overlap(back, p) < 1.0


def test_open_back_panels():
    spec = spec_for(enclosure="open", port=None, open_fraction=0.4)
    lay = L.layout(spec)
    backs = M.back_solids(lay)
    assert set(backs) == {"back_upper", "back_lower"}
    h_p = L.open_panel_height(spec, L.frame(spec))
    for name, s in backs.items():
        bb = s.bounding_box()
        assert abs((bb.max.Z - bb.min.Z) - h_p) < 1e-6
    assert M.assert_no_overlap(backs["back_upper"], backs["back_lower"]) < 1e-6


def test_envelope_stepped_cylinder_and_components():
    spec = spec_for(port="round")
    lay = L.layout(spec)
    env = lay.envelopes[0]
    s = M.envelope_solid(env)
    expected = (math.pi / 4 * env.basket_d ** 2 * env.basket_len
                + math.pi / 4 * env.magnet_d ** 2 * env.magnet_len
                + math.pi / 4 * env.flange_d ** 2 * env.flange_t)
    assert abs(s.volume - expected) < 1.0
    bb = s.bounding_box()
    assert abs(bb.min.Y - (env.y0 - env.flange_t)) < 1e-6
    assert abs(bb.max.Y - (env.y0 + env.basket_len + env.magnet_len)) < 1e-6
    comps = M.component_solids(lay)
    assert {"speaker_0", "jack_plate_0", "strap_handle", "foot_0", "foot_1", "foot_2", "foot_3"} == set(comps)
    spec2 = spec_for(port="round", aesthetics=L.Aesthetics(handle="recessed-side"))
    comps2 = M.component_solids(L.layout(spec2))
    assert {"recessed_handle_left", "recessed_handle_right"} <= set(comps2)


# === TASK 11 ===
def _site_layout(**aest):
    a = L.Aesthetics(tolex_color="Fender Style Black", **aest)
    return L.layout(L.order_from(sheet(port="round"), a))


def test_build_air_volume_matches_the_layout_and_nothing_collides():
    lay = _site_layout()
    cab = M.build(lay)
    assert len(cab.parts) == len(lay.parts) == cab.assembly.solids().__len__()
    assert [e["name"] for e in cab.parts] == [b.name for b in lay.parts]
    by = {c.name: c for c in M.check_build(cab, lay)}
    assert set(by) == {"interference", "air volume", "solid count", "rectangularity"}
    assert by["interference"].level == "pass", by["interference"].message
    assert by["air volume"].level == "pass", by["air volume"].message
    assert by["solid count"].level == "pass"
    measured = cab.air[0].volume / 1e6 - lay.chambers[0].displacement_l
    assert abs(measured - lay.net_l[0]) / lay.net_l[0] < 0.001
    assert "baffle" in by["rectangularity"].message


def test_check_build_reports_a_collision():
    lay = _site_layout()
    cab = M.build(lay)
    # push the back panel 5 mm into the box: it must hit the back cleats
    idx = next(i for i, e in enumerate(cab.parts) if e["name"] == "back")
    cab.parts[idx]["solid"] = M.Pos(0, -5.0, 0) * cab.parts[idx]["solid"]
    cab.parts[idx]["solid"].label = "back"
    by = {c.name: c for c in M.check_build(cab, lay)}
    assert by["interference"].level == "blocker" and "back" in by["interference"].message


def test_exploded_moves_every_part_outward():
    lay = _site_layout()
    cab = M.build(lay)
    ex = M.exploded(cab, factor=0.6)
    bb, ab = ex.bounding_box(), cab.assembly.bounding_box()
    assert bb.max.X - bb.min.X > (ab.max.X - ab.min.X) * 1.8
    assert len(ex.solids()) == len(cab.parts) + len(cab.components)


def test_export_writes_every_deliverable(tmp_path):
    lay = _site_layout()
    cab = M.build(lay)
    checks = L.check_layout(lay, lay.spec) + M.check_build(cab, lay)
    files = M.export(cab, lay, checks, tmp_path)
    assert files["step"] == "cab.step" and files["cab_json"] == "cab.json" and files["images"][0] == "images/cab-iso.png"
    for key in ("step", "cutlist_md", "cutlist_csv", "cab_json"):
        assert (tmp_path / files[key]).exists(), key
    assert len(files["images"]) == 5 and all((tmp_path / p).exists() for p in files["images"])
    report = json.loads((tmp_path / "cab.json").read_text())
    assert report["files"] == files and report["external_in"] == [20.0, 18.0, 11.0]
    assert {c["name"] for c in report["checks"]} >= {"sheet", "interference", "air volume"}
    md = (tmp_path / "cutlist.md").read_text()
    assert "## Materials not cut" in md and "tolex wrap" in md and "Fender Style Black" in md
    assert "finger joint" in md
    # hardwood: no tolex line
    spec = L.order_from(sheet(line="hardwood", species="black walnut", port="round"),
                        L.Aesthetics(corner_joint="dovetail"))
    lay2 = L.layout(spec)
    cab2 = M.build(lay2)
    M.export(cab2, lay2, L.check_layout(lay2, spec), tmp_path / "hw")
    md2 = (tmp_path / "hw" / "cutlist.md").read_text()
    assert "Materials not cut" not in md2 and "through dovetail" in md2


# --- CAD matrix: live proposals through layout and build
TONE = json.loads((FIXTURES / "tone-roots.json").read_text())
TONE["min_power_w"] = 30
MATRIX_SPEAKER = "eminence-cannabis-rex"
ENCLOSURES = [("closed", None), ("closed-ported", None), ("closed-ported", "slot"), ("open", None), ("semi-open", None)]
CONFIGS = [(1, "mono"), (2, "mono"), (2, "mono-parallel-out"), (2, "stereo")]
LINES = [("tolex", None, "finger"), ("hardwood", "black walnut", "finger"), ("hardwood", "black walnut", "dovetail")]
DEFAULT_CASES = [
    # enclosure, slot, drivers, jack, line index, extra aesthetics
    ("closed", None, 1, "mono", 0, {}),
    ("closed-ported", None, 1, "mono", 0, {}),
    ("closed-ported", "slot", 1, "mono", 1, {}),
    ("open", None, 1, "mono", 0, {"handle": "recessed-side"}),
    ("semi-open", None, 1, "mono", 2, {}),
    ("closed", None, 2, "mono", 0, {}),
    ("closed-ported", None, 2, "mono", 1, {"baffle_mount": "fixed"}),
    ("closed-ported", "slot", 2, "mono", 0, {}),
    ("closed", None, 2, "stereo", 2, {}),
    ("closed-ported", None, 2, "stereo", 0, {}),
    ("open", None, 2, "mono-parallel-out", 0, {}),
    ("semi-open", None, 2, "stereo", 0, {"baffle_mount": "fixed"}),
]


def _matrix_cases():
    if os.environ.get("CAB_FULL_MATRIX"):
        return [(enc, slot, n, jack, li, {}) for enc, slot in ENCLOSURES for n, jack in CONFIGS
                for li in range(len(LINES))]
    return DEFAULT_CASES


def _sheet_for(drv, enclosure, slot, n, jack, line, species):
    z = drv.impedance_ohm[0]
    c = cabvoice.Constraints(line=line, species=species, port_slot_mm=(300.0, 40.0) if slot else None)
    v = cabvoice.propose([drv] * n, [z] * n, enclosure, TONE, jack, c, "cad-matrix").to_dict()
    if slot and n == 2 and jack != "stereo":
        # two slots spanning the chamber, split only by the 18 mm center cheek (no end cheek slivers);
        # the width comes from the layout frame, not the engine's internal width (2 mm wider on hardwood)
        xa, xb = L.frame(L.order_from(v, L.Aesthetics())).chambers[0]
        c.port_slot_mm = (((xb - xa) - L.DIVIDER_MM) / 2.0, 40.0)
        v = cabvoice.propose([drv] * n, [z] * n, enclosure, TONE, jack, c, "cad-matrix").to_dict()
    return v


def test_cad_matrix_solids_agree_with_the_layout(tmp_path):
    t0 = time.time()
    drv = cabvoice.load_speaker(MATRIX_SPEAKER)
    cases = _matrix_cases()
    layout_blockers = {}
    for k, (enclosure, slot, n, jack, li, extra) in enumerate(cases):
        line, species, joint = LINES[li]
        v = _sheet_for(drv, enclosure, slot, n, jack, line, species)
        assert not v["blockers"], (enclosure, slot, n, jack, line, v["blockers"])
        spec = L.order_from(v, L.Aesthetics(corner_joint=joint, **extra))
        lay = L.layout(spec)
        for c in L.check_layout(lay, spec):
            if c.level == "blocker":
                layout_blockers.setdefault(c.name, []).append((enclosure, slot, n, jack, line))
                assert c.name in ("port fit", "net volume"), (enclosure, slot, n, jack, line, c.message)
        cab = M.build(lay)
        by = {c.name: c for c in M.check_build(cab, lay)}
        label = (enclosure, slot, n, jack, line, joint, extra)
        assert by["interference"].level == "pass", (label, by["interference"].message)
        assert by["air volume"].level == "pass", (label, by["air volume"].message)
        assert by["solid count"].level == "pass", label
        step = tmp_path / f"case{k}.step"
        M.export_step(cab.assembly, str(step))
        assert step.exists() and step.stat().st_size > 1000
    print(f"\ncad matrix {len(cases)} builds in {time.time() - t0:.0f} s; layout blockers {layout_blockers}")


# === TASK 12 ===
FIXTURE_ORDERS = ["site-default", "sample-roots-1x12"]
DELIVERABLES = ["cab.json", "cab.step", "cutlist.md", "cutlist.csv", "images/cab-iso.png", "images/cab-front.png",
                "images/cab-top.png", "images/cab-right.png", "images/cab-exploded.png"]


def _fixture_dir(name: str) -> Path:
    return SITE_DEFAULT if name == "site-default" else FIXTURES / name


def _run_fixture(name: str, out: Path) -> tuple:
    """Run a fixture order's cab.py with EXPORT=1 into out; (process, cab.json dict or None)."""
    env = dict(os.environ, EXPORT="1", CAB_OUT=str(out))
    if (HERE / "cabvoice.py").exists():          # mirror run: the template's sys.path points at scripts/
        env["PYTHONPATH"] = str(HERE)
    proc = subprocess.run([sys.executable, str(_fixture_dir(name) / "cab.py")], env=env,
                          capture_output=True, text=True)
    report = json.loads((out / "cab.json").read_text()) if (out / "cab.json").exists() else None
    return proc, report


def test_site_default_fixture(tmp_path):
    proc, report = _run_fixture("site-default", tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    for got, want in zip(report["external_mm"], (508.0, 457.2, 279.4)):
        assert abs(got - want) <= 1.0
    assert (tmp_path / "cab.step").exists() and (tmp_path / "images" / "cab-exploded.png").exists()
    assert all(c["level"] != "blocker" for c in report["checks"])
    assert "interference" in proc.stdout and "exported" in proc.stdout


CHECK_LINES = ["sheet", "net volume", "stereo balance", "cutout", "grill opening", "port fit", "port mouth",
               "magnet to back", "handle", "head match", "line", "jack plate", "stock", "part count", "spans",
               "interference", "air volume", "solid count", "rectangularity"]


def _order_dir(tmp_path):
    """The template copied to the design's per-order depth, projects/Cab-<order>/,
    in a scratch vault whose scripts/ is this suite's module directory."""
    vault = tmp_path / "vault"
    order = vault / "projects" / "Cab-probe"
    order.mkdir(parents=True)
    (vault / "scripts").symlink_to(HERE, target_is_directory=True)
    for name in ("cab.py", "voicing.json"):
        (order / name).write_bytes((SITE_DEFAULT / name).read_bytes())
    return order


def test_cab_py_finds_the_vault_from_an_order_directory(tmp_path):
    order = _order_dir(tmp_path)
    env = {k: v for k, v in os.environ.items() if k not in ("EXPORT", "TMP_STL", "SHOW", "PYTHONPATH")}
    proc = subprocess.run([sys.executable, "cab.py"], cwd=order, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    printed = [line[:16].strip() for line in proc.stdout.splitlines()]
    assert printed == CHECK_LINES[:15] and not (order / "cab.json").exists()
    proc = subprocess.run([sys.executable, str(order / "cab.py")], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_cab_py_exits_2_on_a_blocker_and_still_exports(tmp_path):
    order = _order_dir(tmp_path)
    v = json.loads((order / "voicing.json").read_text())
    v["volumes"]["net_total_l"] *= 1.3
    v["volumes"]["per_chamber_net_l"] *= 1.3
    (order / "voicing.json").write_text(json.dumps(v, indent=2))
    out = tmp_path / "out"
    env = dict(os.environ, EXPORT="1", CAB_OUT=str(out))
    env.pop("PYTHONPATH", None)
    proc = subprocess.run([sys.executable, str(order / "cab.py")], env=env, capture_output=True, text=True)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    lines = proc.stdout.splitlines()
    assert [line[:16].strip() for line in lines if not line.startswith("exported")] == CHECK_LINES
    assert any(line.startswith("net volume") and " blocker " in line for line in lines)
    report = json.loads((out / "cab.json").read_text())
    assert report["files"]["cab_json"] == "cab.json" and (out / "cab.step").exists()
    assert [c["level"] for c in report["checks"] if c["name"] == "net volume"] == ["blocker"]


# ---- Plan 3 Task 2: port mouth check, aesthetics block, fixture list ----
@pytest.mark.parametrize("name", FIXTURE_ORDERS)
def test_fixture_order_runs_clean_with_every_deliverable(name, tmp_path):
    proc, report = _run_fixture(name, tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    blockers = [c for c in report["checks"] if c["level"] == "blocker"]
    assert blockers == [], blockers
    assert [c["name"] for c in report["checks"]] == CHECK_LINES
    assert set(report["aesthetics"]) >= {"corner_joint", "baffle_mount", "handle", "corners", "piping", "feet",
                                         "tolex_roll_in", "tolex_color", "grill_cloth", "head_width_mm"}
    missing = [d for d in DELIVERABLES if not (tmp_path / d).exists()]
    assert missing == [], missing
