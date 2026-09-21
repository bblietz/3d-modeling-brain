"""Section close-ups of the case with the phone docked and the guard ring glued on, cut from the real exported meshes.

Usage:  .venv/bin/python projects/iPhone-15-Pro-Max-case/pipeline/sections.py
Reads iphone-15-pro-max-case.stl and build/{phone-proxy,ring-as-glued,magsafe-pieces}.stl; writes images/section-*.png.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

PH_W, PH_L, BACK_T, PH_T = 76.73, 159.86, 1.6, 8.25
ZG = BACK_T + PH_T
PARTS = [("case", f"{PROJECT}/iphone-15-pro-max-case.stl", "#2f6f4f"),
         ("guard ring", f"{PROJECT}/build/ring-as-glued.stl", "#c9772b"),
         ("MagSafe ring 0.4 thick + alignment piece", f"{PROJECT}/build/magsafe-pieces.stl", "#3b6ea8"),
         ("phone (Apple drawing)", f"{PROJECT}/build/phone-proxy.stl", "#b9bec5")]
MESHES = [(n, trimesh.load(p), c) for n, p, c in PARTS]


def cut(mesh, axis, at):
    """Even-odd filled region of the mesh on the plane axis = at, as a shapely geometry in the other two axes (z vertical)."""
    normal = [0, 0, 0]
    normal[axis] = 1
    origin = [0, 0, 0]
    origin[axis] = at
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return None
    keep = [i for i in range(3) if i != axis]
    region = None
    for loop in sec.discrete:
        p = Polygon(loop[:, keep])
        if p.is_valid and p.area > 1e-9:
            region = p if region is None else region.symmetric_difference(p)
    return region


def draw(ax, geom, colour, label):
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for k, poly in enumerate(p for p in polys if p.geom_type == "Polygon"):
        verts, codes = [], []
        for ring in [poly.exterior, *poly.interiors]:
            xy = list(ring.coords)
            verts += xy
            codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), facecolor=colour, edgecolor="black", linewidth=0.6, label=label if k == 0 else None))


def figure(name, title, axis, at, xlim, ylim, notes=(), lines=(), size=(11, 7), ylabel="z (mm), bed at 0"):
    fig, ax = plt.subplots(figsize=size)
    for label, mesh, colour in MESHES:
        g = cut(mesh, axis, at)
        if g is not None and not g.is_empty:
            draw(ax, g, colour, label)
    for (x0, y0, x1, y1), colour, label in lines:
        ax.plot([x0, x1], [y0, y1], color=colour, linewidth=1.0, linestyle="--", label=label)
    for (x, y), (tx, ty_), text in notes:
        ax.annotate(text, xy=(x, y), xytext=(tx, ty_), fontsize=9, arrowprops=dict(arrowstyle="->", linewidth=0.7))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    ax.set_xlabel("xyz"[[i for i in range(3) if i != axis][0]] + " (mm)"); ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11); ax.grid(True, linewidth=0.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8, frameon=False)
    os.makedirs(f"{PROJECT}/images", exist_ok=True)
    fig.savefig(f"{PROJECT}/images/{name}.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def cone_lines(y_axis, r0, h0, slope, h1, label, colour):
    """Both edges of a keepout cone in a y-z section through its axis: radius r0 at h0 above the back glass, growing by slope per mm."""
    out = []
    for s in (-1, 1):
        out.append(((y_axis + s * r0, BACK_T - h0, y_axis + s * (r0 + slope * (h1 - h0)), BACK_T - h1), colour, label if s < 0 else None))
    return out


if __name__ == "__main__":
    xw = -(PH_W / 2)
    figure("section-lip", "Screen lip, volume-button side wall, cut at mid length (y = 0): phone docked", 1, 0.0, (xw - 2.6, xw + 3.6), (6.6, 11.4),
           notes=[((xw + 0.30, ZG - 0.52), (xw + 1.5, 7.4), "holding face: 45 degrees, leaning in over the phone;\n0.05 mm off the shoulder where the shoulder is also at 45"),
                  ((xw + 0.85, ZG + 0.5), (xw + 1.6, 10.9), "lip tip 0.85 in from the housing edge\n(glass starts at 1.00: never touched)"),
                  ((xw + 2.6, ZG), (xw + 1.9, 8.6), "front glass plane z = 9.85;\nlip stands 0.95 above it")])
    figure("section-full", "Full cross-section at mid length (y = 0)", 1, 0.0, (-42, 42), (-1, 12), size=(14, 4))
    yv = PH_L / 2 - 45.22
    figure("section-volume-window", "Volume window, cut through the volume-up button (45.22 from the top edge)", 1, yv, (xw - 2.6, xw + 3.6), (-0.4, 11.4),
           notes=[((xw - 0.2, 5.725), (xw + 1.2, 3.2), "button stands 0.45 proud, inside the window;\nits face is 1.15 below the case surface"),
                  ((xw - 1.3, 8.6), (xw + 0.9, 10.6), "45 degree flare top and bottom:\nfinger room, and only the inner 0.75 mm of the roof is a bridge")])
    xs = PH_W / 2 - 32.16                        # the plane through the flash, camera 3 and the rear sensor
    yf, ys = PH_L / 2 - 10.22, PH_L / 2 - 38.22
    figure("section-camera", "Camera guard, cut through the flash, camera 3 and the rear sensor (guard ring glued on)", 0, xs, (26, 84), (-5.2, 11.6), size=(14, 5.5),
           lines=cone_lines(yf, 5.95, 4.11, 4.915, 5.3, "flash outer keepout cone (Apple)", "#d62728")
           + cone_lines(ys, 7.31, 2.05, 0.850, 5.3, "rear sensor keepout cone (Apple)", "#1f77b4")
           + [((26, BACK_T - 5.0 - 0.0, 84, BACK_T - 5.0), "#555555", "table, case lying on its back")],
           notes=[((PH_L / 2 - 23.79, BACK_T - 4.07), (44, -1.0), "lens glass 4.07 above the back glass:\n0.93 mm off the table (Apple: 0.85 min)")])
    yb = -(PH_L / 2)
    figure("section-usb", "USB-C window, cut on the centreline (x = 0)", 0, 0.0, (yb - 2.6, yb + 5.0), (-0.4, 11.4),
           lines=[((yb - 2.6, 5.725 + 3.3, yb + 0.5, 5.725 + 3.3), "#d62728", "Apple connector keepout 12.45 x 6.60"), ((yb - 2.6, 5.725 - 3.3, yb + 0.5, 5.725 - 3.3), "#d62728", None)])
    figure("section-magsafe", "MagSafe pocket close-up, cut on the centreline where it crosses the ring (phone docked)", 0, 0.0, (-30.5, -20.5), (-0.3, 3.0), size=(11, 4.4),
           notes=[((-25.0, 1.0), (-24.2, 2.55), "ring 0.40 thick, 0.40 below the floor's surface:\noff the phone's glass, held in by the phone"),
                  ((-27.2, 0.4), (-29.3, 0.12), "0.8 mm of back (4 layers) behind the pocket"),
                  ((-22.85, 1.2), (-22.6, 0.45), "located by its inside edge, 0.25 clear")])
    figure("plan-magsafe", "Looking into the empty case from the screen side, cut through the pocket (z = 1.2)", 2, 1.2, (-42, 42), (-84, 84), size=(6.2, 11.5), ylabel="y (mm), top of the phone up",
           notes=[((0, 27.2), (-38, 38), "ring pocket 57.0 / 45.5, centred on the phone's centre:\ntakes 46 ID rings from 54 to 56.5 OD"),
                  ((0, -41), (-38, -62), "clocking magnet pocket:\n6.00 x 19.31 + 0.25, toward the bottom edge"),
                  ((15, 56), (-38, 74), "camera opening")])
    print("wrote", sorted(f for f in os.listdir(f"{PROJECT}/images") if f.startswith(("section-", "plan-"))))
