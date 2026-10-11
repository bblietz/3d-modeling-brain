#!/usr/bin/env python
"""Evidence for the plate-corner break (Brian dropped the 2026-09-19 holder, a corner broke off, 2026-10-10).

Slices holder-print.3mf (same recipe as the first print) and draws, from the real G-code, the toolpaths of the
layer at mid plate height, colour by feature, so the solid screw pads and the sparse gyroid core of the plate are
visible. Also draws a true section of holder.stl through a screw hole along the plate's diagonal.

Run from anywhere: .venv/bin/python projects/NACS-wall-holder/pipeline/corner_check.py [sliced.3mf]
Writes images/corner-layer.png and images/corner-section.png and prints the plastic per feature in the corners.
"""
import math
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline"))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

BED_CENTRE = (108.0, 128.0)          # make_coupon_3mf.py JOBS["holder"]: the model origin (plate centre) lands here
PAD_R = 12.5
SCRATCH = os.environ.get("SCRATCH", "/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/612fec58-43f6-4bff-a4e8-46ee5353df03/scratchpad")


def scad_const(name):
    src = open(f"{PROJECT}/holder.scad").read()
    return float(re.search(rf"(?<![A-Za-z_]){name}\s*=\s*([-0-9.]+)\s*;", src).group(1))


def sliced_3mf():
    if len(sys.argv) > 1:
        return sys.argv[1]
    out = f"{SCRATCH}/corner-slice/sliced.3mf"
    if not os.path.exists(out):
        from graft_slice import graft_slice
        res = graft_slice(f"{PROJECT}/holder-print.3mf", out)
        assert res["rc"] == 0 and res["gcode"], res
    return out


def layer_paths(gcode, z_want):
    """Extrusion polylines of the layer nearest z_want, in model coordinates: list of (type, [(x, y), ...])."""
    zs = sorted({float(l.split(":")[1]) for l in gcode.splitlines() if l.startswith("; Z_HEIGHT:")})
    z_pick = min(zs, key=lambda z: abs(z - z_want))
    paths, z, feat, x, y = [], 0.0, "", 0.0, 0.0
    for line in gcode.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":")[1])
        elif line.startswith("; FEATURE:"):
            feat = line[10:].strip()
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, me = re.search(r" X([-0-9.]+)", line), re.search(r" Y([-0-9.]+)", line), re.search(r" E([-0-9.]+)", line)
            nx, ny = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if z == z_pick and me and float(me.group(1)) > 0 and (mx or my):
                if line[:3] in ("G2 ", "G3 "):
                    mi, mj = re.search(r" I([-0-9.]+)", line), re.search(r" J([-0-9.]+)", line)
                    cx, cy = x + (float(mi.group(1)) if mi else 0), y + (float(mj.group(1)) if mj else 0)
                    r = math.hypot(x - cx, y - cy)
                    a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
                    if line[:3] == "G2 ":          # clockwise
                        while a1 >= a0:
                            a1 -= 2 * math.pi
                    else:
                        while a1 <= a0:
                            a1 += 2 * math.pi
                    n = max(2, int(abs(a1 - a0) * r / 0.5))
                    pts = [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
                else:
                    pts = [(x, y), (nx, ny)]
                paths.append((feat, [(px - BED_CENTRE[0], py - BED_CENTRE[1]) for px, py in pts]))
            x, y = nx, ny
    return z_pick, paths


COLOURS = {"Sparse infill": "#e8a33d", "Internal solid infill": "#2b4c7e", "Outer wall": "#555555", "Inner wall": "#888888",
           "Top surface": "#2b4c7e", "Bottom surface": "#2b4c7e", "Gap infill": "#2b4c7e"}


def draw_layer(z, paths, hole_xy, w, out):
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.6))
    for ax, lim, title in ((axes[0], (-w / 2 - 3, w / 2 + 3, -w / 2 - 3, w / 2 + 3), f"whole plate, layer at z = {z:.1f} mm (mid plate)"),
                           (axes[1], (12, w / 2 + 2, 12, w / 2 + 2), "upper right corner, same layer")):
        for feat, pts in paths:
            xs, ys = zip(*pts)
            if max(xs) < lim[0] or min(xs) > lim[1] or max(ys) < lim[2] or min(ys) > lim[3]:
                continue
            ax.plot(xs, ys, color=COLOURS.get(feat, "#bbbbbb"), lw=0.9 if ax is axes[0] else 1.6, solid_capstyle="round")
        for hx, hy in hole_xy:
            ax.add_patch(plt.Circle((hx, hy), PAD_R, fill=False, ls="--", lw=1.2, color="#2b4c7e"))
        ax.add_patch(plt.Circle((0, 0), scad_const("drum_r") + scad_const("fillet_plate"), fill=False, ls=":", lw=1.2, color="#a33"))
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal"); ax.set_title(title, fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
    from matplotlib.lines import Line2D
    axes[0].legend([Line2D([], [], color="#e8a33d", lw=2), Line2D([], [], color="#666", lw=2),
                    Line2D([], [], color="#2b4c7e", ls="--"), Line2D([], [], color="#a33", ls=":")],
                   ["gyroid core: 100% inside the pads, 20% elsewhere", "walls (3 loops, 1.9 mm)", "screw pad modifier, 12.5 mm", "drum blend foot"],
                   loc="lower left", fontsize=8.5, framealpha=0.95, bbox_to_anchor=(0.0, 0.0))
    fig.tight_layout()
    fig.savefig(out, dpi=140)


def draw_section(hole_xy, out):
    mesh = trimesh.load(f"{PROJECT}/holder.stl")
    n = np.array([1.0, -1.0, 0.0]) / math.sqrt(2)
    segs = trimesh.intersections.mesh_plane(mesh, n, np.zeros(3))
    pad_u = math.hypot(*hole_xy[0])
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.axvspan(pad_u - PAD_R, pad_u + PAD_R, ymin=0, ymax=1, color="#2b4c7e", alpha=0.08, lw=0)
    for a, b in segs:
        ax.plot([(a[0] + a[1]) / math.sqrt(2), (b[0] + b[1]) / math.sqrt(2)], [a[2], b[2]], color="#222", lw=1.4)
    t = scad_const("plate_t")
    for y0, y1 in ((0, 0.9), (t - 0.9, t)):
        ax.axhspan(y0, y1, xmin=0.02, xmax=0.98, color="#2b4c7e", alpha=0.10, lw=0)
    ax.annotate("solid pad, 12.5 mm around the screw", (pad_u, -2.2), ha="center", fontsize=9, color="#2b4c7e")
    ax.annotate("3 skin layers top and bottom (0.9 mm each), 20% gyroid between", (34, t + 1.2), fontsize=9, color="#2b4c7e")
    ax.annotate("countersink: half the plate's thickness", (pad_u, t + 3.0), ha="center", fontsize=9)
    ax.annotate("", (pad_u - 2.5, t), (pad_u - 2.5, t + 2.8), arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.annotate("drum blend", (scad_const("drum_r") + 2, scad_const("plate_t") + scad_const("fillet_plate") + 1.5), fontsize=9)
    ax.set_xlim(28, 76); ax.set_ylim(-4, 24); ax.set_aspect("equal")
    ax.set_xlabel("along the plate's diagonal, mm from the drum axis"); ax.set_ylabel("off the wall, mm")
    ax.set_title("True section of holder.stl through a screw hole, along the plate's diagonal", fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=140)


def main():
    w, hole_in, t = scad_const("plate_w"), scad_const("hole_in"), scad_const("plate_t")
    off = w / 2 - hole_in
    holes = [(sx * off, sy * off) for sx in (-1, 1) for sy in (-1, 1)]
    path = sliced_3mf()
    z = zipfile.ZipFile(path)
    gname = [n for n in z.namelist() if n.endswith(".gcode")][0]
    gcode = z.read(gname).decode(errors="replace")
    z_pick, paths = layer_paths(gcode, t / 2)
    os.makedirs(f"{PROJECT}/images", exist_ok=True)
    draw_layer(z_pick, paths, holes, w, f"{PROJECT}/images/corner-layer.png")
    draw_section(holes, f"{PROJECT}/images/corner-section.png")
    # plastic per feature in the corner flaps (outside the drum blend's foot, inside the plate), in extrusion length
    foot = scad_const("drum_r") + scad_const("fillet_plate")
    tot = {}
    for feat, pts in paths:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if math.hypot(mx, my) > foot and abs(mx) < w / 2 and abs(my) < w / 2:
                tot[feat] = tot.get(feat, 0.0) + math.hypot(x1 - x0, y1 - y0)
    print(f"layer z = {z_pick}: extrusion length by feature in the four corner flaps (outside the blend foot at r = {foot:.0f}):")
    for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
        print(f"  {k:24s} {v:8.0f} mm")
    print(f"hole centres {off:.1f} from each edge = {math.hypot(off, off):.1f} from the axis; blend foot at {foot:.0f}; pad reaches {math.hypot(off, off) - PAD_R:.1f}..{math.hypot(off, off) + PAD_R:.1f} on the diagonal")
    e = w / 2
    print(f"along the plate's edge the pad covers y = {off - math.sqrt(PAD_R**2 - (e - off)**2):.1f}..{off + math.sqrt(PAD_R**2 - (e - off)**2):.1f}; the blend foot meets the edge at y = {math.sqrt(foot**2 - e**2):.1f}")
    print(f"countersink depth {(scad_const('csk_d') - scad_const('hole_d')) / 2:.2f} of the {t:.0f} mm plate")


if __name__ == "__main__":
    main()
