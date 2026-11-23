#!/usr/bin/env python
"""Build and check the guitar neck rest: neck_rest.scad -> guitar-neck-rest.stl, pictures, build-report.json.

Every check runs on the exported mesh, not on the constants: rays dropped on it, planes cut through it, its facet
normals. The constants are read back from neck_rest.scad's DERIVED echo, so nothing is typed twice.

Print frame of the STL: x along the neck, y up the standing rocker (0 at the bench, the cradle at the top, which is the
back of the plate), z from the plate (0) to the top face (80). The centre plane of the rocker is z = 40.

Run from the vault root:
  .venv/bin/python projects/Guitar-neck-rest/pipeline/build.py [--no-channel] [--no-render]
--no-channel builds the body before the grip tape channel is cut (build step 1) into the scratch file only.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon as MplPolygon

PROJECT = Path(__file__).resolve().parents[1]
SCAD = PROJECT / "neck_rest.scad"
STL = PROJECT / "guitar-neck-rest.stl"
IMAGES = PROJECT / "images"
OPENSCAD = Path.home() / ".local/bin/openscad"
IN = 25.4
CHANNEL = "--no-channel" not in sys.argv
# Neck stand-ins (inches), the ones the options page used: width and depth at the nut and at the 12th fret.
NECKS = {"bass": dict(w0=1.625, w1=2.20, d0=0.94, d1=0.99), "guitar": dict(w0=1.650, w1=2.075, d0=0.82, d1=0.87)}
OVERHANG_DEG = 47.0      # 45 plus the 2 degrees of facet tilt the 3d-model skill allows on a tessellated mesh
INK, PRINT, PADC, TAPEC, WOOD = "#1f2430", "#4f83e6", "#c9a26b", "#2a2e36", "#e6c992"


def openscad(*args):
    r = subprocess.run([str(OPENSCAD), "--backend=Manifold", *args, str(SCAD)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-3000:]
    return r.stderr


def export():
    out = STL if CHANNEL else PROJECT / "pipeline" / "_no-channel.stl"
    log = openscad("--export-format", "binstl", "-D", 'MODE="part"', "-D", f"CHANNEL={'true' if CHANNEL else 'false'}", "-o", str(out))   # binary: 9 MB, not 53
    m = re.search(r"DERIVED (.*?)\"", log)
    assert m, log[-800:]
    d = {k: float(v) for k, v in (kv.split("=") for kv in m.group(1).split())}
    return trimesh.load(out), d


def frac(x_in, den=16):
    from fractions import Fraction
    f = Fraction(round(x_in * den), den)
    whole, rest = divmod(f, 1)
    return f"{whole}" if rest == 0 else (f"{whole}-{rest}" if whole else f"{rest}")


def check_solid(mesh):
    assert mesh.is_watertight, "not watertight"
    assert len(mesh.split(only_watertight=False)) == 1, "more than one body"
    assert abs(mesh.bounds[0][2]) < 1e-6, f"does not sit on the plate: min z {mesh.bounds[0][2]}"
    size = mesh.extents
    want = (148.7, 108.5, 80.0)
    assert all(abs(a - b) < 0.2 for a, b in zip(size, want)), f"size {size} against {want}"
    return {"size_mm": [round(float(s), 2) for s in size], "size_in": " x ".join(frac(s / IN, 8) for s in (size[0], size[2], size[1])),
            "volume_cm3": round(float(mesh.volume) / 1000, 1), "facets": int(len(mesh.faces))}


def top(mesh, x, z):
    """Height of the body's top at (x, z): a ray dropped from above."""
    return float(mesh.ray.intersects_location([[x, 300.0, z]], [[0, -1, 0]])[0][:, 1].max())


def bottom(mesh, x, z):
    """Height of the body's underside at (x, z): a ray sent up from below."""
    return float(mesh.ray.intersects_location([[x, -300.0, z]], [[0, 1, 0]])[0][:, 1].min())


def check_cradle(mesh, d):
    mid_z = d["YC"] / 2
    r, xt, floor = d["R_END"], d["FLAT"] / 2, d["FLOOR"]
    mid = (math.pi / 2 + math.radians(d["C_LEAN"])) / 2
    got = {"floor_at_centre": top(mesh, 0, mid_z), "floor_at_roundover_start": top(mesh, xt - 0.5, mid_z),
           "end_arc_middle": top(mesh, xt + r * math.cos(mid), mid_z), "other_end_arc_middle": top(mesh, -xt - r * math.cos(mid), mid_z),
           "shoulder": top(mesh, 0, mid_z + (d["RIM_Y"] + d["YC"] / 2 - d["R_EDGE"]) / 2),
           "rim_roundover_middle": top(mesh, 0, mid_z + d["RIM_Y"] - d["R_EDGE"] * math.sin(math.radians(22.5)))}
    arc = floor - r + r * math.sin(mid)
    want = {"floor_at_centre": floor, "floor_at_roundover_start": floor, "end_arc_middle": arc, "other_end_arc_middle": arc,
            "shoulder": d["ZC"], "rim_roundover_middle": d["ZC"] - d["R_EDGE"] * (1 - math.cos(math.radians(22.5)))}
    for k in got:
        assert abs(got[k] - want[k]) < 0.05, f"cradle {k}: {got[k]:.3f} against {want[k]:.3f}"
    assert abs(floor - (d["HIGH"] - d["PAD_T"])) < 1e-9
    return {k: [round(got[k], 3), round(want[k], 3)] for k in got} | {"level_floor_mm": round(d["FLAT"], 2)}


def check_channel(mesh, d):
    mid_z, half = d["YC"] / 2, d["CH_W"] / 2
    got = {"in_channel_centre": bottom(mesh, 0, mid_z), "in_channel_near_wall": bottom(mesh, 0, mid_z + half - 0.3),
           "on_lip": bottom(mesh, 0, mid_z + half + 0.3), "on_other_lip": bottom(mesh, 0, mid_z - half - 0.3)}
    want = {"in_channel_centre": d["TAPE_D"], "in_channel_near_wall": d["TAPE_D"], "on_lip": 0.0, "on_other_lip": 0.0}
    for k in got:
        assert abs(got[k] - want[k]) < 0.02, f"channel {k}: {got[k]:.3f} against {want[k]:.3f}"
    # along the curve: just inside the closed end the channel is there, just past it the curve is whole
    rr, a = d["RR"], math.radians(d["CH_A"])
    inside, past = a - 0.01, a + 0.01
    curve = lambda t, r: (r * math.sin(t), rr - r * math.cos(t))
    xi, yi = curve(inside, rr - d["TAPE_D"])
    xp, yp = curve(past, rr)
    assert abs(bottom(mesh, xi, mid_z) - yi) < 0.03 and abs(bottom(mesh, xp, mid_z) - yp) < 0.03, "the channel's end is not where CH_A says"
    lip = (d["YC"] - d["CH_W"]) / 2
    assert lip - d["R_EDGE"] > 10, "the lips are too narrow to stand on"
    floor_arc = 2 * a * (rr - d["TAPE_D"])
    assert floor_arc - d["TAPE_L"] > 2 and d["CH_W"] - d["TAPE_W"] > 0.5, "the tape does not drop in with clearance"
    return {k: [round(got[k], 3), round(want[k], 3)] for k in got} | {
        "width_mm": round(d["CH_W"], 2), "depth_mm": d["TAPE_D"], "length_on_floor_mm": round(floor_arc, 1),
        "tape_cut_in": f"{frac(d['TAPE_W'] / IN)} x {frac(d['TAPE_L'] / IN)}", "lip_each_side_mm": round(lip, 2),
        "end_clearance_mm": round((floor_arc - d["TAPE_L"]) / 2, 2), "side_clearance_mm": round((d["CH_W"] - d["TAPE_W"]) / 2, 2)}


def check_pad(d):
    """The cork as cut against the seat: inside the level floor lengthwise, clear of the rim roundovers across."""
    seat_arc = 2 * d["GR"] * math.asin(d["RIM_YG"] / d["GR"])
    end_margin = (d["FLAT"] - d["PAD_L"]) / 2
    side_margin = (seat_arc - d["PAD_W"]) / 2
    assert end_margin > 0.5 and side_margin > 1.0, f"pad does not fit its seat: ends {end_margin:.2f}, sides {side_margin:.2f}"
    chord = 2 * d["CR"] * math.sin(d["PAD_W"] / 2 / (d["GR"] - d["PAD_T"] / 2))
    return {"cut_in": f"{frac(d['PAD_W'] / IN)} x {frac(d['PAD_L'] / IN)}", "end_margin_mm": round(end_margin, 2),
            "side_margin_mm": round(side_margin, 2), "width_at_pad_surface_in": round(chord / IN, 2)}


def check_neck(mesh, d):
    """Each stand-in neck lying on the pad, at its nut size and its 12th fret size: the smallest gap between the neck's
    back and the printed body, from rays dropped under the neck. It should be the pad thickness, on the centre line."""
    out = {}
    xs = np.linspace(-72, 72, 49)
    for name, n in NECKS.items():
        for where, (w, dep) in (("nut", (n["w0"] * IN, n["d0"] * IN)), ("fret12", (n["w1"] * IN, n["d1"] * IN))):
            b = dep - 6.35                              # the rounded back under a 1/4 in fretboard
            us = np.linspace(-w / 2 * 0.999, w / 2 * 0.999, 41)
            under = d["HIGH"] + b - b * np.sqrt(1 - (2 * us / w) ** 2)
            worst = (9e9, 0, 0)
            for x in xs:
                hits = mesh.ray.intersects_location([[x, 300.0, d["YC"] / 2 - u] for u in us], [[0, -1, 0]] * len(us))
                tops = np.full(len(us), -1e9)
                np.maximum.at(tops, hits[1], hits[0][:, 1])
                gap = under - tops
                i = int(np.argmin(gap))
                if gap[i] < worst[0]:
                    worst = (float(gap[i]), float(x), float(us[i]))
            assert worst[0] > d["PAD_T"] - 0.05, f"{name} {where}: the neck comes within {worst[0]:.2f} mm of the plastic at x {worst[1]:.0f}, y {worst[2]:.1f}"
            out[f"{name}_{where}"] = {"min_gap_mm": round(worst[0], 2), "at_x_mm": round(worst[1], 1), "off_centre_mm": round(worst[2], 1)}
    return out


def check_overhangs(mesh, d):
    """Facets facing down more than OVERHANG_DEG from upright, in the print frame, by where they are."""
    n, c, area = mesh.face_normals, mesh.triangles_center, mesh.area_faces
    steep = (-n[:, 2] > math.sin(math.radians(OVERHANG_DEG))) & (c[:, 2] > 1e-4)
    plate_band = steep & (c[:, 2] < d["R_EDGE"] + 0.05)
    wall_z = d["YC"] / 2 + d["CH_W"] / 2
    channel = steep & (np.abs(c[:, 2] - wall_z) < 0.05) & (c[:, 1] < 30)
    other = steep & ~plate_band & ~channel
    assert area[other].sum() < 0.5, f"unexpected overhang: {area[other].sum():.1f} mm2 around {c[other].mean(axis=0)}"
    down = -n[:, 2]
    cradle = (c[:, 1] > d["FLOOR"] - 1) & (c[:, 2] > d["YC"] / 2) & (c[:, 2] < d["YC"] / 2 + d["RIM_Y"]) & (np.abs(c[:, 0]) < 40)
    rim = math.degrees(math.asin(down[cradle].max()))
    assert rim < OVERHANG_DEG, f"the cradle's upper rim overhangs {rim:.1f} degrees"
    return {"limit_deg": OVERHANG_DEG, "plate_side_roundover_mm2": round(float(area[plate_band].sum()), 1),
            "channel_down_facing_wall_mm2": round(float(area[channel].sum()), 1), "channel_wall_ledge_mm": d["TAPE_D"],
            "elsewhere_mm2": round(float(area[other].sum()), 2), "cradle_upper_rim_deg": round(rim, 1)}


def cut(mesh, origin, normal, axes):
    seg = trimesh.intersections.mesh_plane(mesh, plane_normal=normal, plane_origin=origin)
    return seg[:, :, axes]


def fig_sections(mesh, d):
    """Two cuts through the real mesh, to scale: one cradle end on the centre plane, and straight across the neck."""
    IMAGES.mkdir(exist_ok=True)
    floor, high, r, xt = d["FLOOR"], d["HIGH"], d["R_END"], d["FLAT"] / 2
    # --- cradle end
    seg = cut(mesh, [0, 0, d["YC"] / 2], [0, 0, 1], [0, 1])
    fig, ax = plt.subplots(figsize=(5.6, 3.5), dpi=170)
    x0, x1, z0, z1 = 26, 86, 77, 114
    ax.add_patch(MplPolygon([(x0 - 5, high), (x1 + 5, high), (x1 + 5, z1 + 5), (x0 - 5, z1 + 5)], closed=True, fc=WOOD, ec="#8a6a3c", lw=1))
    ax.add_patch(MplPolygon([(x0 - 5, floor), (d["PAD_L"] / 2, floor), (d["PAD_L"] / 2, high), (x0 - 5, high)], closed=True, fc=PADC, ec="#8a6a3c", lw=0.8))
    ax.add_collection(LineCollection(seg, colors="#2b4f9e", linewidths=2.2))
    ax.annotate("", xy=(xt + r * math.cos(math.radians(50)), floor - r + r * math.sin(math.radians(50))), xytext=(xt, floor - r),
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.3))
    ax.text(xt - 1.2, floor - r - 0.3, f"{frac(r / IN)} in", fontsize=12, weight="bold", color=INK, ha="right", va="center")
    ax.text(x0 + 3, high + 9, "neck", fontsize=10.5, color="#6b4f2a", ha="left", va="center")
    ax.text(x0 + 3, (floor + high) / 2, "cork", fontsize=8.5, color="#3b2c12", ha="left", va="center")
    ax.text(x0 + 3, floor - 9, "printed body", fontsize=10.5, color="#2b4f9e", ha="left", va="center")
    ax.text(x1 - 2, floor - 12, "blue line: the model,\ncut through the middle", fontsize=9, color="#2b4f9e", ha="right", va="center")
    ax.set_xlim(x0, x1), ax.set_ylim(z0, z1), ax.set_aspect("equal"), ax.axis("off")
    fig.tight_layout(pad=0.3)
    fig.savefig(IMAGES / "neck-rest-section-end.png", facecolor="white")
    plt.close(fig)
    # --- across the neck, at the middle of the rest
    seg = cut(mesh, [0, 0, 0], [1, 0, 0], [2, 1])
    seg = seg - [d["YC"] / 2, 0]
    fig, ax = plt.subplots(figsize=(5.6, 4.1), dpi=170)
    n = NECKS["bass"]
    w, dep = (n["w0"] + (n["w1"] - n["w0"]) * 95 / (17 * IN)) * IN, n["d0"] * IN
    b = dep - 6.35
    t = np.linspace(math.pi, 2 * math.pi, 60)
    neck = np.vstack([np.column_stack([w / 2 * np.cos(t), high + b + b * np.sin(t)]), [w / 2, high + dep], [-w / 2, high + dep]])
    ax.add_patch(MplPolygon(neck, closed=True, fc=WOOD, ec="#8a6a3c", lw=1))
    a = d["PAD_W"] / 2 / (d["GR"] - d["PAD_T"] / 2)
    th = np.linspace(-a, a, 80)
    za = high + d["CR"]
    pad = np.vstack([np.column_stack([d["GR"] * np.sin(th), za - d["GR"] * np.cos(th)]),
                     np.column_stack([d["CR"] * np.sin(th[::-1]), za - d["CR"] * np.cos(th[::-1])])])
    ax.add_patch(MplPolygon(pad, closed=True, fc=PADC, ec="#8a6a3c", lw=0.8))
    tw, td = d["TAPE_W"] / 2, d["TAPE_D"]
    ax.add_patch(MplPolygon([(-tw, td), (tw, td), (tw, td - 1.0), (-tw, td - 1.0)], closed=True, fc=TAPEC, ec=TAPEC))
    ax.add_collection(LineCollection(seg, colors="#2b4f9e", linewidths=2.0))
    ax.plot([-70, 70], [td - 1.0, td - 1.0], color=INK, lw=1.2)
    ax.annotate(f"cork pad, {frac(d['PAD_W'] / IN)} in wide", xy=(d["GR"] * math.sin(a * 0.8), za - d["GR"] * math.cos(a * 0.8) + 0.6),
                xytext=(47, high + 26), fontsize=9.5, color=INK, ha="left", arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
    ax.annotate(f"grip tape, {frac(d['TAPE_W'] / IN)} in wide,\nin a channel {td:g} mm deep", xy=(tw - 4, td - 0.5), xytext=(47, 16),
                fontsize=9.5, color=INK, ha="left", arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
    ax.text(0, high + dep / 2, "bass neck", fontsize=10, color="#6b4f2a", ha="center", va="center")
    ax.text(47, 60, "blue line: the model,\ncut across the neck", fontsize=9, color="#2b4f9e", ha="left", va="center")
    ax.annotate("", xy=(-58, td - 1.0), xytext=(-58, high), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
    ax.text(-60, high / 2, f"{frac(high / IN)} in", fontsize=10, color=INK, ha="right", va="center", rotation=90)
    ax.plot([-62, -30], [high, high], color=INK, lw=0.7)
    ax.set_xlim(-72, 112), ax.set_ylim(-8, 126), ax.set_aspect("equal"), ax.axis("off")
    fig.tight_layout(pad=0.3)
    fig.savefig(IMAGES / "neck-rest-section-across.png", facecolor="white")
    plt.close(fig)


VIEWS = {   # name: (look-at, rot_x, rot_z, distance, extra -D)
    "hero": ((0, 0, 50), 66, 32, 480, []),
    "end": ((52, 0, 92), 62, 58, 270, []),
    "under": ((0, 0, 52), 62, 32, 480, ["-D", "FLIP=true"]),
    "bare": ((0, 0, 50), 66, 32, 480, ["-D", "SOFT=false"]),
}


def render(only=None):
    IMAGES.mkdir(exist_ok=True)
    for name, ((cx, cy, cz), rx, rz, dist, extra) in VIEWS.items():
        if only and name not in only:
            continue
        out = IMAGES / f"neck-rest-{name}.png" if CHANNEL else PROJECT / "pipeline" / f"_no-channel-{name}.png"
        openscad("--preview", f"--camera={cx},{cy},{cz},{rx},0,{rz},{dist}", "--projection=p", "--colorscheme=Tomorrow",
                 "--imgsize=1500,1000", "-D", 'MODE="scene"', "-D", f"CHANNEL={'true' if CHANNEL else 'false'}", *extra, "-o", str(out))
        print("rendered", out.name)


if __name__ == "__main__":
    mesh, d = export()
    report = {"solid": check_solid(mesh), "cradle_mm_got_want": check_cradle(mesh, d)}
    if CHANNEL:
        report["channel"] = check_channel(mesh, d)
        report["pad"] = check_pad(d)
        report["neck_clearance"] = check_neck(mesh, d)
        report["overhangs"] = check_overhangs(mesh, d)
        report["derived_mm"] = d
        fig_sections(mesh, d)
        (PROJECT / "build-report.json").write_text(json.dumps(report, indent=1))
    if "--no-render" not in sys.argv:
        render(["bare", "end"] if not CHANNEL else None)
    print(json.dumps({k: v for k, v in report.items() if k != "derived_mm"}, indent=1))
