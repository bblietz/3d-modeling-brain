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
