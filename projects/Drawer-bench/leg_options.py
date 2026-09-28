#!/usr/bin/env python
"""Leg design options for the drawer bench, drawn from the model's own constants.

Builds the visible shell of the bench (posts, panels, fronts, top) with one
post edge treatment and one foot/leg-exposure treatment, then renders maple
shaded views plus a to-scale plan section of the post for the visual
companion page (leg-options.html). Nothing here feeds the cut list; the
chosen option is applied in drawer_bench.py afterwards.

Usage: TMP_DIR=<scratch> .venv/bin/python projects/Drawer-bench/leg_options.py
Writes projects/Drawer-bench/images/legs/*.png and options.json.
"""
import json
import math
import os
import sys
import tempfile

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Drawer-bench"
sys.path.insert(0, PROJ)
sys.path.insert(0, f"{VAULT}/scripts")
from drawer_bench import *   # noqa: F401,F403  constants and build123d names; runs the model's checks once
from drawer_bench import _box   # star import skips underscore names

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.patches import Polygon, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from render_stl import facet_shade, vertex_shade

OUT = f"{PROJ}/images/legs"
os.makedirs(OUT, exist_ok=True)
TMP = os.environ.get("TMP_DIR", tempfile.gettempdir())
MAPLE = np.array([0.93, 0.79, 0.57])
FLOOR_RGB = np.array([0.80, 0.78, 0.75])
FLOOR_T = 3.0              # floor slab under the renders, for the gap to read against
PAPER = "#f6f1e8"
INK = "#3b2f22"

# --- options ------------------------------------------------------------------
# Edge treatments: "outer" is the post's outside corner edge, "reveal" the two
# edges beside the panel setback and the drawer-front reveal (and the hidden
# inside corner). Sizes on the reveal edges must stay under SETBACK (1/2 in) or
# the cut breaks into the panel groove.
EDGES = {
    "E1": ("3/8 in chamfer, all four edges", "current CAD",
           {"outer": ("chamfer", CHAMFER), "reveal": ("chamfer", CHAMFER)}),
    "E2": ("Square, edges only eased", "crispest; closest to a plain Boos leg",
           {"outer": None, "reveal": None}),
    "E3": ("3/8 in roundover, all four edges", "softer, Shaker feel",
           {"outer": ("fillet", CHAMFER), "reveal": ("fillet", CHAMFER)}),
    "E4": ("3/4 in chamfer on the outer corner, 3/8 in on the reveal edges", "heavier corner",
           {"outer": ("chamfer", 0.75 * IN), "reveal": ("chamfer", CHAMFER)}),
    "E5": ("3/4 in roundover on the outer corner, reveal edges crisp", "one soft corner",
           {"outer": ("fillet", 0.75 * IN), "reveal": None}),
}
# Foot / leg exposure: floor gap under the fronts, groove stop under the panels,
# and whether the edge treatment stops above the foot.
FEET = {
    "F1": ("Straight to the floor", "current CAD: panels 1-1/2 in and fronts 3/4 in off the floor",
           dict(floor_gap=FLOOR_GAP, groove_stop=GROOVE_STOP, stopped=False)),
    "F2": ("Stopped edge, square foot", "edge treatment stops at the panel line, 1-1/2 in up; square block below",
           dict(floor_gap=FLOOR_GAP, groove_stop=GROOVE_STOP, stopped=True)),
    "F3": ("3 in of leg showing", "panels and fronts both stop 3 in above the floor",
           dict(floor_gap=3 * IN, groove_stop=3 * IN, stopped=False)),
    "F4": ("4-1/2 in of leg showing", "panels and fronts both stop 4-1/2 in above the floor",
           dict(floor_gap=4.5 * IN, groove_stop=4.5 * IN, stopped=False)),
}


# --- geometry -----------------------------------------------------------------
def _is_outer(e):
    return e.center().X < X0 + 0.5 and e.center().Y < Y0 + 0.5


def _is_reveal(e):
    c = e.center()
    return abs(c.X - (X0 + POST)) < 0.5 or abs(c.Y - (Y0 + POST)) < 0.5


def _treat(p, ops):
    for sel, op in ((_is_outer, ops["outer"]), (_is_reveal, ops["reveal"])):
        if op is None:
            continue
        kind, size = op
        es = [e for e in p.edges().filter_by(Axis.Z) if sel(e)]
        p = chamfer(es, size) if kind == "chamfer" else fillet(es, size)
    return p


def fl_post(ops, groove_stop, stopped):
    """Front-left post; the other three are mirrors of it."""
    if stopped:
        upper = _treat(_box(X0, Y0, groove_stop, POST, POST, POST_H - groove_stop), ops)
        return upper + _box(X0, Y0, 0, POST, POST, groove_stop)
    return _treat(_box(X0, Y0, 0, POST, POST, POST_H), ops)


def shell(edge_key, foot_key):
    ops = EDGES[edge_key][2]
    f = FEET[foot_key][2]
    floor_gap, groove_stop = f["floor_gap"], f["groove_stop"]
    fl = fl_post(ops, groove_stop, f["stopped"])
    rl = mirror(fl, Plane(origin=(0, TOP_D / 2, 0), z_dir=(0, 1, 0)))
    posts = fl + mirror_x(fl) + rl + mirror_x(rl)
    panel_h = POST_H - groove_stop
    side = _box(X0 + SETBACK, SIDE_Y0, groove_stop, T18, SIDE_L, panel_h)
    back = _box(BACK_X0, BACK_Y0, groove_stop, RAIL_L, T18, panel_h)
    zone = POST_H - REV_TOP - floor_gap - REV_MID          # the two fronts, re-split by the design rule
    bot_h = zone * FRONT_BOT_H / (FRONT_BOT_H + FRONT_TOP_H)
    top_h = zone - bot_h
    fb = _box(FRONT_X0, FRONT_Y0, floor_gap, FRONT_W, FRONT_T, bot_h)
    ft = _box(FRONT_X0, FRONT_Y0, floor_gap + bot_h + REV_MID, FRONT_W, FRONT_T, top_h)
    rail = _box(RAIL_X0, RAIL_Y0, floor_gap, FRAME_RAIL_L, RAIL_T, RAIL_BOT_H)   # seen through the floor gap
    top = _box(0, 0, POST_H, TOP_W, TOP_D, TOP_T)
    floor = _box(-120, -120, -FLOOR_T, TOP_W + 240, TOP_D + 240, FLOOR_T)
    solid = posts + side + mirror_x(side) + back + fb + ft + rail + top + floor
    # Blum maximum box heights follow the rails, which follow the fronts
    mid_z0 = floor_gap + bot_h + REV_MID / 2 - RAIL_MID_H / 2
    box_top = (RAIL_TOP_Z0 - (mid_z0 + RAIL_MID_H)) - (UM_BOTTOM_CLEAR + UM_TOP_CLEAR)
    box_bot = (mid_z0 - (floor_gap + RAIL_BOT_H)) - (UM_BOTTOM_CLEAR + UM_TOP_CLEAR)
    return solid, dict(front_bot_in=bot_h / IN, front_top_in=top_h / IN,
                       box_bot_in=box_bot / IN, box_top_in=box_top / IN)


def clip(solid, size, zmax, zmin=-FLOOR_T - 1):
    return solid & _box(-60, -60, zmin, size + 60, size + 60, zmax - zmin + 1)


# --- rendering ----------------------------------------------------------------
def render(solid, png, elev, azim, inches=6.0, dpi=150):
    stl = os.path.join(TMP, "leg_scene.stl")
    export_stl(solid, stl)
    # Finer triangles keep matplotlib's painter's-algorithm sort honest on the
    # big flat faces (the top slab streaked at the raw tessellation).
    mesh = trimesh.load_mesh(stl).subdivide_to_size(45.0)
    tris = mesh.vertices[mesh.faces]
    # Light from just off the post's outer corner: a 45 degree chamfer or a
    # roundover then shades brighter than either face beside it instead of
    # matching one of them.
    light = np.array([-0.55, -0.7, 0.45])
    light /= np.linalg.norm(light)
    # Per-face normals: these boxes have too few vertices for the vertex-normal
    # smoothing in render_stl (every corner normal is a diagonal), which
    # flattens a chamfer into its neighbours; a fillet's strip still reads.
    shade = facet_shade(mesh, 0.5 + 0.5 * np.clip(mesh.face_normals @ light, 0, 1))
    colors = np.outer(shade, MAPLE)
    colors[mesh.triangles_center[:, 2] < 0.5] = FLOOR_RGB * 0.9   # the floor slab, top face at z = 0
    lo, hi = mesh.bounds
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 * 1.02
    fig = plt.figure(figsize=(inches, inches))
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tris, facecolors=colors, edgecolors=colors,
                                         linewidths=0.7, antialiased=True))
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.patch.set_alpha(0)
    fig.savefig(png, dpi=dpi, bbox_inches="tight", pad_inches=0.02, transparent=True)
    plt.close(fig)
    print("rendered", os.path.relpath(png, VAULT))


def _corner_pts(cx, cy, dx_in, dy_out, op):
    """Outline points replacing the corner (cx, cy): arriving along dx_in (unit
    step of the incoming edge), leaving along dy_out (unit step of the outgoing)."""
    if op is None:
        return [(cx, cy)]
    kind, s = op
    a = (cx - dx_in[0] * s, cy - dx_in[1] * s)
    b = (cx + dy_out[0] * s, cy + dy_out[1] * s)
    if kind == "chamfer":
        return [a, b]
    ctr = (a[0] + dy_out[0] * s, a[1] + dy_out[1] * s)   # fillet center, s in from both faces
    t0 = math.atan2(a[1] - ctr[1], a[0] - ctr[0])
    t1 = math.atan2(b[1] - ctr[1], b[0] - ctr[0])
    if t1 - t0 > math.pi:
        t1 -= 2 * math.pi
    if t0 - t1 > math.pi:
        t1 += 2 * math.pi
    return [(ctr[0] + s * math.cos(t), ctr[1] + s * math.sin(t))
            for t in np.linspace(t0, t1, 10)]


def plan_section(edge_key, png, inches=3.6, dpi=150):
    """To-scale plan of the front-left post with the side panel and drawer
    front stubs, model X to the right and model Y (toward the back) up."""
    ops = EDGES[edge_key][2]
    corners = [((X0, Y0), ops["outer"]), ((X0 + POST, Y0), ops["reveal"]),
               ((X0 + POST, Y0 + POST), ops["reveal"]), ((X0, Y0 + POST), ops["reveal"])]
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]      # edge directions, counterclockwise
    pts = []
    for i, ((cx, cy), op) in enumerate(corners):
        pts += _corner_pts(cx, cy, dirs[i - 1], dirs[i], op)
    stub = 2.4 * IN
    fig, ax = plt.subplots(figsize=(inches, inches))
    ax.add_patch(Rectangle((X0 + SETBACK, Y0 + POST - GROOVE_D), T18, GROOVE_D + stub,
                           facecolor="#d9c7a8", edgecolor=INK, linewidth=0.8))
    ax.add_patch(Rectangle((X0 + POST + REV_SIDE, Y0 + FRONT_SETBACK), stub, FRONT_T,
                           facecolor="#e8d9bd", edgecolor=INK, linewidth=0.8))
    ax.add_patch(Polygon(pts, closed=True, facecolor="#efdcb8", edgecolor=INK, linewidth=1.2))
    ax.text(X0 + POST / 2, Y0 + POST / 2, "post\n3 x 3", ha="center", va="center",
            fontsize=8, color=INK)
    ax.text(X0 + SETBACK + T18 / 2, Y0 + POST + stub / 2, "side panel", ha="center", va="center",
            fontsize=7, color=INK, rotation=90)
    ax.text(X0 + POST + REV_SIDE + stub / 2, Y0 + FRONT_SETBACK + FRONT_T / 2, "drawer front",
            ha="center", va="center", fontsize=7, color=INK)
    ax.text(X0 + POST / 2, Y0 - 4, "front of the bench", ha="center", va="top", fontsize=7,
            color=INK, alpha=0.7)
    pad = 6
    ax.set_xlim(X0 - pad, X0 + POST + REV_SIDE + stub + pad)
    ax.set_ylim(Y0 - 14, Y0 + POST + stub + pad)
    ax.set_aspect("equal")
    ax.set_axis_off()
    fig.patch.set_alpha(0)
    fig.savefig(png, dpi=dpi, bbox_inches="tight", pad_inches=0.02, transparent=True)
    plt.close(fig)
    print("drew", os.path.relpath(png, VAULT))


if __name__ == "__main__":
    CORNER = float(os.environ.get("CORNER", 210))   # mm of the front-left corner in the close-ups
    views = os.environ.get("VIEWS")                 # "elev,azim" to try camera angles on the corner
    info = {"edges": {}, "feet": {}}
    for k, (name, note, _) in EDGES.items():
        solid, _ = shell(k, "F1")
        e, a = (14, -128) if not views else map(float, views.split(","))
        render(clip(solid, CORNER, H, zmin=POST_H - 9 * IN), f"{OUT}/{k}-corner.png", e, a)
        plan_section(k, f"{OUT}/{k}-plan.png")
        info["edges"][k] = {"name": name, "note": note}
    for k, (name, note, f) in FEET.items():
        solid, nums = shell("E1", k)
        render(solid, f"{OUT}/{k}-bench.png", 16, -128)
        render(clip(solid, CORNER, 9 * IN), f"{OUT}/{k}-foot.png", 10, -128)
        info["feet"][k] = {"name": name, "note": note,
                           "floor_gap_in": f["floor_gap"] / IN, "panel_gap_in": f["groove_stop"] / IN,
                           **{kk: round(v, 3) for kk, v in nums.items()}}
    with open(f"{OUT}/options.json", "w") as fh:
        json.dump(info, fh, indent=1)
    print(json.dumps(info["feet"], indent=1))
