#!/usr/bin/env python
"""Shop drawings for every cut-list part of the drawer bench.

Each sheet is laid out from the same constants that build the solid in
drawer_bench.py, and every groove, rabbet, notch and bore drawn is probed
against the real solid before the sheet is written (a box inside the cut
must be air, a box just past its floor must be wood; a "through" cut is
probed at the blank's end, a "stopped" one just beyond its stop). So a
drawing cannot show a cut the model does not have, or in another place.

Dimensions read inches to the nearest 1/32 (no metric on the cut list,
Brian 2026-09-28), from the blank's own edges and ends; a cut sized to
plywood says so and is cut to the measured sheet. Faces are drawn as the machining face
seen from inside the cabinet or drawer box; long parts lie lengthwise.

Usage: .venv/bin/python projects/Drawer-bench/part_drawings.py
Writes projects/Drawer-bench/images/parts/<part>.png.
"""
import os
import sys

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Drawer-bench"
sys.path.insert(0, PROJ)
sys.path.insert(0, f"{VAULT}/scripts")
from drawer_bench import *   # noqa: F401,F403  constants, solids and build123d names; runs the model's checks once
from drawer_bench import _box  # noqa: E402
from cutlist import inch_frac  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

OUT = f"{PROJ}/images/parts"
os.makedirs(OUT, exist_ok=True)
INK, PAPER, WOOD, CUT, HIDDEN, DIM = "#3b2f22", "#f6f1e8", "#efdcb8", "#d4bb8e", "#8a7d63", "#7a4a1a"
ROW = 16   # mm between callout rows above a blank (scaled with the view)


def dt(mm):
    """Dimension text: inches to the nearest 1/32."""
    return inch_frac(mm, 32)


PLY18, PLY12, PLY6 = "3/4 ply (measure)", "1/2 ply (measure)", "1/4 ply (measure)"


# --- drawing model ------------------------------------------------------------
class View:
    """One orthographic view of a blank: w x h in mm, x right, y up, plus cuts,
    callouts, dimensions and edge labels in the same coordinates. Callouts sit
    in rows above the blank with a leader down to the feature; dimensions go
    where each part's function puts them (usually below and to the sides)."""

    def __init__(self, w, h, title, outline=None, size="main"):
        self.w, self.h, self.title, self.outline, self.size = w, h, title, outline, size
        self.ops = []
        self.rows = 0
        self.row_mm = max(ROW, 0.05 * max(w, h))

    def groove(self, x, y, w, h):
        self.ops.append(("groove", (x, y, w, h)))

    def notch(self, x, y, w, h):
        self.ops.append(("notch", (x, y, w, h)))

    def hidden(self, x, y, w, h):
        self.ops.append(("hidden", (x, y, w, h)))

    def bore(self, cx, cy, r, hidden=False):
        self.ops.append(("bore", (cx, cy, r, hidden)))

    def mark(self, x0, y0, x1, y1):
        self.ops.append(("mark", (x0, y0, x1, y1)))

    def callout(self, px, py, text, row=None):
        row = self.rows if row is None else row
        self.rows = max(self.rows, row + 1)
        self.ops.append(("callout", (px, py, row), text))

    def top_y(self):
        """Y just above the callout rows, for the overall dimension."""
        return self.h + self.row_mm * (self.rows + 0.9)

    def dim_h(self, x0, x1, y, text=None):
        self.ops.append(("dim_h", (x0, x1, y), text))

    def dim_v(self, y0, y1, x, text=None):
        self.ops.append(("dim_v", (y0, y1, x), text))

    def edge(self, side, text):
        self.ops.append(("edge", side, text))

    def note(self, x, y, text):
        self.ops.append(("note", (x, y), text))


def _draw(ax, v):
    pts = v.outline or [(0, 0), (v.w, 0), (v.w, v.h), (0, v.h)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=WOOD, edgecolor=INK, lw=1.2, zorder=1))
    xs, ys = [0, v.w], [0, v.h]
    dash = (0, (4, 3))
    for op in v.ops:
        kind, a = op[0], op[1]
        text = op[2] if len(op) > 2 else None
        if kind == "groove":
            ax.add_patch(Rectangle(a[:2], a[2], a[3], facecolor=CUT, edgecolor=INK, lw=0.8, hatch="////", zorder=2))
        elif kind == "notch":
            ax.add_patch(Rectangle(a[:2], a[2], a[3], facecolor=PAPER, edgecolor=INK, lw=1.2, zorder=2))
        elif kind == "hidden":
            ax.add_patch(Rectangle(a[:2], a[2], a[3], fill=False, edgecolor=HIDDEN, lw=0.9, ls=dash, zorder=3))
        elif kind == "bore":
            cx, cy, r, hid = a
            ax.add_patch(Circle((cx, cy), r, fill=False, edgecolor=HIDDEN if hid else INK, lw=0.9,
                                ls=dash if hid else "-", zorder=3))
            ax.plot([cx - r * 1.4, cx + r * 1.4], [cy, cy], color=HIDDEN, lw=0.4, zorder=3)
            ax.plot([cx, cx], [cy - r * 1.4, cy + r * 1.4], color=HIDDEN, lw=0.4, zorder=3)
        elif kind == "mark":
            ax.plot([a[0], a[2]], [a[1], a[3]], color=HIDDEN, lw=0.7, ls=(0, (3, 3)), zorder=3)
        elif kind == "callout":
            px, py, row = a
            ty = v.h + v.row_mm * (row + 0.75)
            ax.plot([px, px], [py, ty - v.row_mm * 0.25], color=HIDDEN, lw=0.6, zorder=4)
            ax.plot([px], [py], marker="o", ms=2.2, color=HIDDEN, zorder=4)
            ha = "left" if px < v.w * 0.3 else ("right" if px > v.w * 0.7 else "center")
            ax.text(px, ty, text, ha=ha, va="center", fontsize=6.5, color=INK, zorder=5,
                    bbox=dict(facecolor=PAPER, edgecolor="none", pad=1.0))
            ys.append(ty + v.row_mm * 0.5)
        elif kind == "dim_h":
            x0, x1, y = a
            above = y >= v.h / 2
            ye = v.h if above else 0
            for x in (x0, x1):
                ax.plot([x, x], [ye, y + (2 if above else -2)], color=DIM, lw=0.5, zorder=4)
            ax.annotate("", xy=(x1, y), xytext=(x0, y), zorder=4,
                        arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.7, shrinkA=0, shrinkB=0, mutation_scale=7))
            ax.text((x0 + x1) / 2, y + (1.5 if above else -1.5), text or dt(abs(x1 - x0)), ha="center",
                    va="bottom" if above else "top", fontsize=6.5, color=DIM, zorder=5)
            ys.append(y + (v.row_mm * 0.7 if above else -v.row_mm * 0.7))
        elif kind == "dim_v":
            y0, y1, x = a
            right = x >= v.w / 2
            xe = v.w if right else 0
            for y in (y0, y1):
                ax.plot([xe, x + (2 if right else -2)], [y, y], color=DIM, lw=0.5, zorder=4)
            ax.annotate("", xy=(x, y1), xytext=(x, y0), zorder=4,
                        arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.7, shrinkA=0, shrinkB=0, mutation_scale=7))
            ax.text(x + (1.5 if right else -1.5), (y0 + y1) / 2, text or dt(abs(y1 - y0)), ha="left" if right else "right",
                    va="center", fontsize=6.5, color=DIM, rotation=90, zorder=5)
            xs.append(x + (v.row_mm * 0.8 if right else -v.row_mm * 0.8))
        elif kind == "edge":
            side = a
            if side == "bottom":
                ax.text(v.w / 2, -2.5, text, ha="center", va="top", fontsize=6.5, color=INK, style="italic", zorder=5)
            elif side == "top":
                ax.text(v.w / 2, v.h + 2.5, text, ha="center", va="bottom", fontsize=6.5, color=INK, style="italic", zorder=5)
            elif side == "left":
                ax.text(-2.5, v.h / 2, text, ha="right", va="center", fontsize=6.5, color=INK, style="italic", rotation=90, zorder=5)
            else:
                ax.text(v.w + 2.5, v.h / 2, text, ha="left", va="center", fontsize=6.5, color=INK, style="italic", rotation=90, zorder=5)
        elif kind == "note":
            ax.text(a[0], a[1], text, ha="left", va="center", fontsize=6.5, color=INK, zorder=5,
                    bbox=dict(facecolor=PAPER, edgecolor="none", pad=1.0, alpha=0.9))
    pad = max(0.05 * max(v.w, v.h), 10)
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(v.title, fontsize=7.5, color=INK, loc="left", pad=3)


def sheet(name, title, views, note=None, stack=False):
    """One PNG: the views side by side (or stacked, for long parts with several
    views), each at its own scale (main views wide, small views compact), a
    title line and an optional note."""
    boxes = []
    for v in views:
        ext_w = v.w + 2 * (0.25 * v.w + 40)
        ext_h = v.h + v.row_mm * (v.rows + 2) + 0.35 * v.h + 40
        cap_w, cap_h = (7.6, 4.6) if v.size == "main" else (2.8, 2.8)
        s = min(cap_w / ext_w, cap_h / ext_h)
        boxes.append((max(ext_w * s, 1.6), max(ext_h * s, 1.4)))
    gap, top, bottom = 0.3, 0.5, 0.42 if note else 0.15
    if stack:
        fw = max(b[0] for b in boxes) + 2 * gap
        fh = sum(b[1] for b in boxes) + gap * (len(boxes) - 1) + top + bottom
    else:
        fw = sum(b[0] for b in boxes) + gap * (len(boxes) + 1)
        fh = max(b[1] for b in boxes) + top + bottom
    fig = plt.figure(figsize=(fw, fh))
    fig.patch.set_facecolor(PAPER)
    x, y = gap, fh - top
    for v, (bw, bh) in zip(views, boxes):
        if stack:
            y -= bh
            ax = fig.add_axes([gap / fw, y / fh, bw / fw, bh / fh])
            y -= gap
        else:
            ax = fig.add_axes([x / fw, bottom / fh, bw / fw, bh / fh])
            x += bw + gap
        ax.set_facecolor(PAPER)
        _draw(ax, v)
    fig.text(gap / fw, 1 - 0.2 / fh, title, fontsize=8.5, color=INK, weight="bold", va="center", wrap=True)
    if note:
        fig.text(gap / fw, 0.16 / fh, note, fontsize=6.5, color=HIDDEN, va="center", wrap=True)
    png = f"{OUT}/{name}.png"
    fig.savefig(png, dpi=170, facecolor=PAPER)
    plt.close(fig)
    print("drew", os.path.relpath(png, VAULT))


# --- probes: the drawn cuts must exist in the solid ----------------------------
def cut_probes(x, y, z, dx, dy, dz, floor):
    """Probes for a rectangular cut with min corner (x, y, z) and size (dx, dy, dz):
    a box 1 mm inside it must be air; a 1 mm slab just past its floor must be wood.
    `floor` names the floor side: '-x', '+x', '-y', '+y', '-z' or '+z'."""
    inside = _box(x + 1, y + 1, z + 1, dx - 2, dy - 2, dz - 2)
    sign, ax = floor[0], floor[1]
    lo = {"x": x, "y": y, "z": z}
    sz = {"x": dx, "y": dy, "z": dz}
    f = {k: (lo[k] + 1, sz[k] - 2) for k in "xyz"}
    f[ax] = (lo[ax] - 1.5, 1.0) if sign == "-" else (lo[ax] + sz[ax] + 0.5, 1.0)
    past = _box(f["x"][0], f["y"][0], f["z"][0], f["x"][1], f["y"][1], f["z"][1])
    return [(inside, "empty"), (past, "solid")]


def check(name, solid, probes):
    for box, expect in probes:
        v = vol(box & solid)
        if expect == "empty":
            assert v < 1e-6, (name, "drawn cut is not in the solid", v)
        else:
            assert abs(v - box.volume) < 1e-6, (name, "wood expected past the cut", v, box.volume)


# --- parts -----------------------------------------------------------------------
def post(front):
    name = "post_front" if front else "post_rear"
    solid = part(name)
    y0 = Y0 if front else YB - POST
    views, probes = [], []

    # A: the face with the side-panel groove, lengthwise, floor end at the left,
    # outer face along the bottom of the view
    v = View(POST_H, POST, "A  side-groove face (faces the other post on this side); floor end at left, OUTER face along the bottom")
    v.groove(GROOVE_STOP, SETBACK, POST_H - GROOVE_STOP, T18)
    v.mark(0, CHAMFER, POST_H, CHAMFER)
    v.mark(0, POST - CHAMFER, POST_H, POST - CHAMFER)
    v.mark(PANEL_Z0, 0, PANEL_Z0, POST)
    v.mark(TONGUE_Z0, 0, TONGUE_Z0, POST)
    v.callout(POST_H * 0.55, SETBACK + T18 / 2, f"side-panel groove: {PLY18} wide x {dt(GROOVE_D)} deep, "
                                                 f"stopped {dt(GROOVE_STOP)} from the floor end, runs out the top end")
    v.callout(TONGUE_Z0, SETBACK + T18 * 0.8, f"dashed lines across: the panel's bottom edge ({dt(PANEL_Z0)}) and where its housed tongue starts ({dt(TONGUE_Z0)})")
    v.callout(GROOVE_STOP, SETBACK + T18 * 0.2, f"leave the groove's end as the tool cuts it: full depth from {dt(TONGUE_Z0)} up, nothing below {dt(PANEL_Z0)}")
    v.callout(POST_H * 0.2, CHAMFER, f"dashed along: where the {dt(CHAMFER)} chamfers start (all four long edges)")
    v.dim_v(0, SETBACK, -22)
    v.dim_v(SETBACK, SETBACK + T18, -50, PLY18)
    v.dim_h(0, GROOVE_STOP, -22)
    v.dim_h(0, TONGUE_Z0, -50)
    v.dim_h(0, POST_H, v.top_y())
    v.edge("left", "floor end")
    v.edge("right", "top end")
    v.edge("bottom", "OUTER face")
    views.append(v)
    gy = y0 + POST - GROOVE_D if front else y0
    probes += cut_probes(X0 + SETBACK, gy, GROOVE_STOP, T18, GROOVE_D, POST_H - GROOVE_STOP, "-y" if front else "+y")
    probes.append((_box(X0 + SETBACK + 1, gy + 1, GROOVE_STOP - 4, T18 - 2, GROOVE_D - 2, 2.5), "solid"))   # stopped
    probes.append((_box(X0 + SETBACK + 1, gy + 1, POST_H - 3, T18 - 2, GROOVE_D - 2, 4), "empty"))         # open at top

    if front:
        v = View(POST_H, POST, "B  face toward the drawer opening; floor end at left, FRONT face along the bottom")
        yc = FRAME_SETBACK + RAIL_T / 2
        zs = [z + h / 2 for z, h in RAIL_ZH]
        for zc in zs:
            v.bore(zc, yc, DOWEL_DIA / 2)
            probes += cut_probes(X0 + POST - DOWEL_DEPTH, Y0 + yc - 2, zc - 2, DOWEL_DEPTH, 4, 4, "-x")
        v.callout(zs[1], yc, f"dowel bores x3 for the rails: {dt(DOWEL_DIA)} dia x {dt(DOWEL_DEPTH)} deep, "
                             f"{dt(yc)} from the front face")
        for i, zc in enumerate(zs):
            v.dim_h(0, zc, -22 - 26 * i)
        v.dim_v(0, yc, POST_H + 26)
        v.dim_h(0, POST_H, v.top_y())
        v.edge("left", "floor end")
        v.edge("bottom", "FRONT face")
        views.append(v)
    else:
        v = View(POST_H, POST, "B  face toward the other rear post; floor end at left, REAR face along the top")
        gx = POST - SETBACK - T18
        v.groove(GROOVE_STOP, gx, POST_H - GROOVE_STOP, T18)
        v.mark(PANEL_Z0, 0, PANEL_Z0, POST)
        v.mark(TONGUE_Z0, 0, TONGUE_Z0, POST)
        v.callout(POST_H * 0.55, gx + T18 / 2, f"back-panel groove: {PLY18} wide x {dt(GROOVE_D)} deep, "
                                                f"{dt(SETBACK)} from the REAR face, stopped {dt(GROOVE_STOP)} from the floor end")
        v.callout(TONGUE_Z0, gx + T18 * 0.3, f"dashed lines and the groove's end: as in view A ({dt(PANEL_Z0)} and {dt(TONGUE_Z0)})")
        v.dim_v(gx + T18, POST, -22)
        v.dim_v(gx, gx + T18, -50, PLY18)
        v.dim_h(0, GROOVE_STOP, -22)
        v.dim_h(0, POST_H, v.top_y())
        v.edge("left", "floor end")
        v.edge("top", "REAR face")
        v.edge("bottom", "front face")
        views.append(v)
        probes += cut_probes(X0 + POST - GROOVE_D, YB - SETBACK - T18, GROOVE_STOP, GROOVE_D, T18, POST_H - GROOVE_STOP, "-x")
        probes.append((_box(X0 + POST - GROOVE_D + 1, YB - SETBACK - T18 + 1, GROOVE_STOP - 4, GROOVE_D - 2, T18 - 2, 2.5), "solid"))

    c = CHAMFER
    octo = [(c, 0), (POST - c, 0), (POST, c), (POST, POST - c), (POST - c, POST), (c, POST), (0, POST - c), (0, c)]
    v = View(POST, POST, "end view from above; front along the bottom", outline=octo, size="small")
    if front:
        v.groove(SETBACK, POST - GROOVE_D, T18, GROOVE_D)
        v.hidden(POST - DOWEL_DEPTH, FRAME_SETBACK + RAIL_T / 2 - DOWEL_DIA / 2, DOWEL_DEPTH, DOWEL_DIA)
        v.note(c + 2, c + 4, "outside corner")
    else:
        v.groove(SETBACK, 0, T18, GROOVE_D)
        v.groove(POST - GROOVE_D, POST - SETBACK - T18, GROOVE_D, T18)
        v.note(c + 2, POST - c - 4, "outside corner")
    v.callout(c / 2, c / 2, f"{dt(c)} chamfer x4")
    v.dim_v(0, POST, POST + 14)
    v.dim_h(0, POST, -12)
    v.edge("left", "OUTER face")
    views.append(v)

    sheet(name, f"{name}  x2, left post shown, right post is the mirror image  |  3 x 3 x {dt(POST_H)} soft maple, glued from two 8/4 pieces",
          views, "Datums: outer face and floor end. Chamfer all four long edges first, then cut the grooves so the walls stay clean. "
                 "The groove ends need no squaring: the panels are notched to clear them.",
          stack=True)
    check(name, solid, probes)


def panel(name):
    solid = part(name)
    is_side = name == "side"
    L, H = (SIDE_L, PANEL_H) if is_side else (RAIL_L, BACK_H)
    gb = BOT_Z0 - PANEL_Z0                         # groove's lower wall above the panel's bottom edge
    to_wall = abs(NOTCH_H - (gb + T12)) < 1e-6     # notch top on the groove's top wall (the shop datum)
    v = View(L, H, "inner face (toward the cabinet); bottom edge along the bottom")
    v.groove(0, gb, L, T12)
    for x in (0, L - GROOVE_D):
        v.notch(x, 0, GROOVE_D, NOTCH_H)
    v.mark(GROOVE_D, NOTCH_H, GROOVE_D, H)
    v.mark(L - GROOVE_D, NOTCH_H, L - GROOVE_D, H)
    v.callout(L * 0.5, gb + T12 / 2, f"groove for the bottom panel, runs out both ends: {PLY12} tall x {dt(BOT_GROOVE)} deep, top wall {dt(gb + T12)} up")
    v.callout(GROOVE_D / 2, NOTCH_H / 2, f"bottom corners notched {dt(GROOVE_D)} x {dt(NOTCH_H)}{', up to the groove' + chr(39) + 's top wall' if to_wall else ''}; "
                                         "the tongue above clears the post groove's end")
    v.callout(GROOVE_D, H * 0.75, f"dashed: {dt(GROOVE_D)} at each end, above the notch, sits in a post groove")
    if not is_side:
        v.hidden(GROOVE_D, H - CLEAT_H, L - 2 * GROOVE_D, CLEAT_H)
        v.callout(L * 0.75, H - CLEAT_H / 2, f"cleat_rear ({dt(CLEAT_H)} tall) glued and screwed here, top edge flush")
    v.dim_v(0, gb + T12, -22)
    v.dim_v(gb, gb + T12, -50, PLY12)
    v.dim_h(0, GROOVE_D, -22)
    v.dim_h(0, L, v.top_y())
    v.dim_v(0, NOTCH_H, L + 26)
    v.dim_v(0, H, L + 54)
    v.edge("bottom", f"bottom edge ({dt(PANEL_Z0)} off the floor)")
    v.edge("left", "front end" if is_side else "left end")
    e = View(T18, 70, "section, bottom edge", size="small")
    e.groove(T18 - BOT_GROOVE, gb, BOT_GROOVE, T12)
    e.callout(T18 - BOT_GROOVE / 2, gb + T12 / 2, f"{dt(BOT_GROOVE)} deep")
    e.dim_h(0, T18, -12, PLY18)
    e.edge("left", "show face")
    e.edge("right", "inner face")
    sheet(name, f"{name}  {'x2, left shown, right is the mirror image' if is_side else 'x1'}  |  {PLY18}, {dt(L)} long x {dt(H)} tall, face grain vertical",
          [v, e], "The groove runs out both ends. Above the notches the ends sit 3/8 deep in the post grooves; below them the panel "
                  "butts the post face and covers the groove's end, so nothing shows.")
    # The groove's floor is probed between the notches; at each end a box
    # straddling the notch boundary proves the groove runs into the notch.
    if is_side:
        x_in = X0 + SETBACK + T18 - BOT_GROOVE
        probes = cut_probes(x_in, SIDE_Y0 + GROOVE_D, BOT_Z0, BOT_GROOVE, SIDE_L - 2 * GROOVE_D, T12, "-x")
        probes.append((_box(x_in + 1, SIDE_Y0 + GROOVE_D - 1, BOT_Z0 + 1, BOT_GROOVE - 2, 3, T12 - 2), "empty"))
        probes.append((_box(x_in + 1, SIDE_Y0 + SIDE_L - GROOVE_D - 2, BOT_Z0 + 1, BOT_GROOVE - 2, 3, T12 - 2), "empty"))
        for y, beside in ((SIDE_Y0, SIDE_Y0 + GROOVE_D + 0.5), (SIDE_Y0 + SIDE_L - GROOVE_D, SIDE_Y0 + SIDE_L - GROOVE_D - 1.5)):
            probes.append((_box(X0 + SETBACK + 1, y + 1, PANEL_Z0 + 1, T18 - 2, GROOVE_D - 2, NOTCH_H - 2), "empty"))          # notch
            probes.append((_box(X0 + SETBACK + 1, y + 1, PANEL_Z0 + NOTCH_H + 0.5, T18 - 2, GROOVE_D - 2, 1), "solid"))       # tongue above it
            probes.append((_box(X0 + SETBACK + 1, beside, PANEL_Z0 + 1, T18 - BOT_GROOVE - 2, 1, NOTCH_H - 2), "solid"))      # panel beside it
    else:
        probes = cut_probes(BACK_X0 + GROOVE_D, BACK_Y0, BOT_Z0, RAIL_L - 2 * GROOVE_D, BOT_GROOVE, T12, "+y")
        probes.append((_box(BACK_X0 + GROOVE_D - 1, BACK_Y0 + 1, BOT_Z0 + 1, 3, BOT_GROOVE - 2, T12 - 2), "empty"))
        probes.append((_box(BACK_X0 + RAIL_L - GROOVE_D - 2, BACK_Y0 + 1, BOT_Z0 + 1, 3, BOT_GROOVE - 2, T12 - 2), "empty"))
        for x, beside in ((BACK_X0, BACK_X0 + GROOVE_D + 0.5), (BACK_X0 + RAIL_L - GROOVE_D, BACK_X0 + RAIL_L - GROOVE_D - 1.5)):
            probes.append((_box(x + 1, BACK_Y0 + 1, PANEL_Z0 + 1, GROOVE_D - 2, T18 - 2, NOTCH_H - 2), "empty"))
            probes.append((_box(x + 1, BACK_Y0 + 1, PANEL_Z0 + NOTCH_H + 0.5, GROOVE_D - 2, T18 - 2, 1), "solid"))
            probes.append((_box(beside, BACK_Y0 + BOT_GROOVE + 1, PANEL_Z0 + 1, 1, T18 - BOT_GROOVE - 2, NOTCH_H - 2), "solid"))
    check(name, solid, probes)


def rail(name):
    solid = part(name)
    h = {"rail_top": RAIL_TOP_H, "rail_mid": RAIL_MID_H, "rail_bot": RAIL_BOT_H, "cleat_rear": CLEAT_H}[name]
    L = OPEN_W
    has_dowels = name != "cleat_rear"
    has_fig8 = name in ("rail_top", "cleat_rear")
    z0 = {"rail_top": RAIL_TOP_Z0, "rail_mid": RAIL_MID_Z0, "rail_bot": RAIL_BOT_Z0, "cleat_rear": POST_H - CLEAT_H}[name]
    inner = "rear" if name != "cleat_rear" else "front"
    views, probes = [], []

    v = View(L, h, "face view" + (" from the REAR (the rabbet is on this face)" if name == "rail_bot" else ""))
    if has_dowels:
        for x in (0, L - DOWEL_DEPTH):
            v.hidden(x, h / 2 - DOWEL_DIA / 2, DOWEL_DEPTH, DOWEL_DIA)
        v.callout(DOWEL_DEPTH / 2, h / 2, f"dowel bore in each end, centered on the end: {dt(DOWEL_DIA)} dia x {dt(DOWEL_DEPTH)} deep")
        yc, zc = RAIL_Y0 + RAIL_T / 2, z0 + h / 2
        probes += cut_probes(RAIL_X0, yc - 2, zc - 2, DOWEL_DEPTH, 4, 4, "+x")
        probes += cut_probes(RAIL_X0 + L - DOWEL_DEPTH, yc - 2, zc - 2, DOWEL_DEPTH, 4, 4, "-x")
    if name == "rail_bot":
        v.groove(0, h - T12, L, T12)
        v.callout(L * 0.6, h - T12 / 2, f"rabbet on the rear-top edge, full length: {PLY12} tall x {dt(BOT_GROOVE)} deep; the bottom panel sits in it")
        v.dim_v(h - T12, h, L + 26, PLY12)
        yr = RAIL_Y0 + RAIL_T - BOT_GROOVE
        probes += cut_probes(RAIL_X0, yr, BOT_Z0, L, BOT_GROOVE, T12, "-y")
        probes.append((_box(RAIL_X0 - 2, yr + 1, BOT_Z0 + 1, 3, BOT_GROOVE - 2, T12 - 2), "empty"))
        probes.append((_box(RAIL_X0 + L - 1, yr + 1, BOT_Z0 + 1, 3, BOT_GROOVE - 2, T12 - 2), "empty"))
    v.dim_h(0, L, v.top_y())
    v.dim_v(0, h, -22)
    v.edge("bottom", "bottom edge")
    views.append(v)

    if has_fig8:
        t = View(L, RAIL_T, f"top edge seen from above; {inner.upper()} face (inside the cabinet) along the bottom")
        xs = [x - RAIL_X0 for x in FIG8_XS]
        for x in xs:
            t.bore(x, FIG8_OFFSET, FIG8_DIA / 2)
        t.callout(xs[1], FIG8_OFFSET, f"figure-8 recess x3: {dt(FIG8_DIA)} forstner, {dt(FIG8_DEPTH)} deep, "
                                      f"center {dt(FIG8_OFFSET)} from the {inner} face so it opens through it")
        for i, x in enumerate(xs):
            t.dim_h(0, x, -22 - 26 * i)
        t.dim_v(0, FIG8_OFFSET, L + 26)
        t.edge("bottom", f"{inner.upper()} face")
        t.edge("top", "front face (drawer side)" if name == "rail_top" else "rear face (glued to the back)")
        views.append(t)
        yc = RAIL_Y0 + RAIL_T - FIG8_OFFSET if name == "rail_top" else BACK_Y0 - RAIL_T + FIG8_OFFSET
        y_out = RAIL_Y0 if name == "rail_top" else BACK_Y0 - 1.5
        for xm in FIG8_XS:
            probes += cut_probes(xm - 2, yc - 2, POST_H - FIG8_DEPTH, 4, 4, FIG8_DEPTH, "-z")
            probes.append((_box(xm - 2, y_out + 0.5, POST_H - FIG8_DEPTH + 0.5, 4, 1, FIG8_DEPTH - 1), "solid"))   # outer wall intact

    e = View(RAIL_T, h, "end view; front along the left" if name != "cleat_rear" else "end view; inner face along the left", size="small")
    if name == "rail_bot":
        e.outline = [(0, 0), (RAIL_T, 0), (RAIL_T, h - T12), (RAIL_T - BOT_GROOVE, h - T12), (RAIL_T - BOT_GROOVE, h), (0, h)]
        e.callout(RAIL_T - BOT_GROOVE / 2, h - T12 / 2, "rabbet")
    if has_dowels:
        e.bore(RAIL_T / 2, h / 2, DOWEL_DIA / 2)
    if has_fig8:
        xr = RAIL_T - FIG8_OFFSET if name == "rail_top" else FIG8_OFFSET
        x0 = max(xr - FIG8_DIA / 2, 0)
        e.groove(x0, h - FIG8_DEPTH, min(xr + FIG8_DIA / 2, RAIL_T) - x0, FIG8_DEPTH)
        e.callout(xr, h - FIG8_DEPTH / 2, "recess")
    e.dim_h(0, RAIL_T, -12)
    e.dim_v(0, h, RAIL_T + 12)
    e.edge("left", "front" if name != "cleat_rear" else "inner (front)")
    views.append(e)

    what = {"rail_top": "FRONT top rail", "rail_mid": "FRONT mid rail", "rail_bot": "FRONT bottom rail", "cleat_rear": "REAR top cleat"}[name]
    sheet(name, f"{name}  x1  |  {what}, {dt(RAIL_T)} soft maple, {dt(h)} tall x {dt(L)} long",
          views, "Rails butt flush into the front posts on the dowels; the mid rail carries the top drawer's slides."
          if has_dowels else "Glued to the inside face of the back, top edge flush with the post tops; clamp with #8 x 1-1/4 screws from this face.",
          stack=has_fig8)
    check(name, solid, probes)


def bottom_panel():
    solid = part("bottom")
    W = BOT_W
    D = BOT_Y1 - BOT_Y0
    nf, nr = Y0 + POST - BOT_Y0, BOT_Y1 - (YB - POST)     # notch depths front / rear
    nw = X0 + POST - BOT_X0                                  # notch width
    v = View(W, D, "plan view from above; FRONT edge along the bottom")
    for x in (0, W - nw):
        v.notch(x, 0, nw, nf)
        v.notch(x, D - nr, nw, nr)
    v.callout(nw / 2, nf / 2, f"front corner notches: {dt(nw)} wide x {dt(nf)} deep; the front tab goes into the bottom rail's rabbet (glue and screw)")
    v.callout(W - nw / 2, D - nr / 2, f"rear corner notches: {dt(nw)} wide x {dt(nr)} deep; the rear tab goes into the back's groove")
    v.dim_h(0, nw, -22)
    v.dim_v(0, nf, -22)
    v.dim_v(D - nr, D, -22)
    v.dim_h(0, W, v.top_y())
    v.dim_v(0, D, W + 26)
    v.edge("bottom", "FRONT edge")
    v.edge("left", "left edge, into the side groove")
    sheet("bottom", f"bottom  x1  |  {PLY12}, {dt(W)} x {dt(D)} overall, four corners notched around the posts",
          [v], "Notch datums are the blank's edges. Pre-join to the back off the bench (see design.md, assembly order).")
    probes = []
    for x, beside in ((BOT_X0, BOT_X0 + nw + 0.5), (BOT_X0 + W - nw, BOT_X0 + W - nw - 1.5)):
        probes.append((_box(x + 1, BOT_Y0 + 1, BOT_Z0 + 1, nw - 2, nf - 2, T12 - 2), "empty"))
        probes.append((_box(x + 1, BOT_Y1 - nr + 1, BOT_Z0 + 1, nw - 2, nr - 2, T12 - 2), "empty"))
        probes.append((_box(x + 1, BOT_Y0 + nf + 0.5, BOT_Z0 + 1, nw - 2, 1, T12 - 2), "solid"))     # wood above the front notch
        probes.append((_box(beside, BOT_Y0 + 1, BOT_Z0 + 1, 1, nf - 2, T12 - 2), "solid"))          # wood beside it, toward the middle
    check("bottom", solid, probes)


def plain(name, L, H, T, note):
    v = View(L, H, "face view")
    v.callout(L / 2, H / 2, note)
    v.dim_h(0, L, v.top_y())
    v.dim_v(0, H, L + 26)
    v.edge("bottom", "bottom edge")
    sheet(name, f"{name}  x1  |  {dt(T)} soft maple, {dt(H)} tall x {dt(L)} long", [v])


def drawer_side(sfx):
    name = f"drawer_side_{sfx}"
    solid = part(name)
    box_h = BOX_BOT_H if sfx == "bot" else BOX_TOP_H
    z0 = BOX_BOT_Z0 if sfx == "bot" else BOX_TOP_Z0
    v = View(BOX_D, box_h, "inner face (toward the inside of the box); FRONT end at left")
    v.groove(0, 0, T12, box_h)
    v.groove(BOX_D - T12, 0, T12, box_h)
    v.groove(T12, UM_RECESS, BOX_D - 2 * T12, T6)
    v.callout(T12 / 2, box_h * 0.7, f"end rabbets, both ends: {PLY12} wide x {dt(DADO)} deep; the box front and back sit in them")
    v.callout(BOX_D / 2, UM_RECESS + T6 / 2, f"bottom groove, runs out both ends: {PLY6} tall x {dt(DADO)} deep, underside {dt(UM_RECESS)} up")
    v.dim_h(0, T12, -22, PLY12)
    v.dim_v(0, UM_RECESS, -22)
    v.dim_v(UM_RECESS, UM_RECESS + T6, -50, PLY6)
    v.dim_h(0, BOX_D, v.top_y())
    v.dim_v(0, box_h, BOX_D + 26)
    v.edge("bottom", "bottom edge")
    v.edge("left", "FRONT end")
    e = View(T12, min(box_h, 60), "section, bottom edge", size="small")
    e.groove(T12 - DADO, UM_RECESS, DADO, T6)
    e.callout(T12 - DADO / 2, UM_RECESS + T6 / 2, f"{dt(DADO)} deep")
    e.edge("right", "inner face")
    e.dim_h(0, T12, -12, PLY12)
    sheet(name, f"{name}  x2, left shown, right is the mirror image  |  {PLY12}, {dt(box_h)} tall x {dt(BOX_D)} long",
          [v, e], "Undermount box: the bottom groove sits 1/2 in up so the Blum runner clears under the bottom.")
    xg = BOX_X0 + T12 - DADO
    probes = cut_probes(xg, BOX_Y0, z0, DADO, T12, box_h, "-x")
    probes += cut_probes(xg, BOX_Y0 + BOX_D - T12, z0, DADO, T12, box_h, "-x")
    probes += cut_probes(xg, BOX_Y0, z0 + UM_RECESS, DADO, BOX_D, T6, "-x")
    check(name, solid, probes)


def drawer_end(sfx, back):
    name = f"drawer_{'back' if back else 'front'}_{sfx}"
    solid = part(name)
    box_h = BOX_BOT_H if sfx == "bot" else BOX_TOP_H
    z0 = BOX_BOT_Z0 if sfx == "bot" else BOX_TOP_Z0
    L = END_LEN
    x_blank = BOX_X0 + T12 - DADO
    stop = UM_HOOK_NOTCH_W + DADO
    v = View(L, box_h, "inner face (toward the inside of the box)")
    if back:
        v.groove(0, UM_RECESS, L, T6)
        for x in (0, L - stop):
            v.notch(x, 0, stop, UM_HOOK_NOTCH_H)
        d, dep, inset, up = UM_HOOK_BORE
        for x in (inset + DADO, L - inset - DADO):
            v.bore(x, up, d / 2, hidden=True)
        v.callout(L / 2, UM_RECESS + T6 / 2, f"bottom groove, runs out both ends: {PLY6} tall x {dt(DADO)} deep, underside {dt(UM_RECESS)} up")
        v.callout(stop / 2, UM_HOOK_NOTCH_H / 2, f"rear-hook notches, both bottom corners: {dt(stop)} wide x {dt(UM_HOOK_NOTCH_H)} tall")
        v.callout(L - inset - DADO, up, f"rear-hook bores (dashed, from the REAR face): {dt(d)} dia x {dt(dep)} deep, Blum T65.1600.01 template")
        v.dim_h(0, stop, -22)
        v.dim_v(0, UM_HOOK_NOTCH_H, -22)
        v.dim_h(L - inset - DADO, L, -22)
        v.dim_v(0, UM_RECESS, L + 26)
        v.dim_v(UM_RECESS, UM_RECESS + T6, L + 54, PLY6)
        v.dim_v(0, up, L + 82)
        v.dim_v(0, box_h, L + 110)
    else:
        v.groove(0, UM_RECESS, L, T6)
        v.callout(L / 2, UM_RECESS + T6 / 2, f"bottom groove, runs out both ends: {PLY6} tall x {dt(DADO)} deep, underside {dt(UM_RECESS)} up")
        v.callout(L * 0.25, box_h * 0.7, "Blum locking devices: bore with the T65.1600.01 template")
        v.dim_v(0, UM_RECESS, -22)
        v.dim_v(UM_RECESS, UM_RECESS + T6, -50, PLY6)
        v.dim_v(0, box_h, L + 26)
    v.dim_h(0, L, v.top_y())
    v.edge("bottom", "bottom edge")
    v.edge("left", "left end, into the side's rabbet")
    sheet(name, f"{name}  x1  |  {PLY12}, {dt(box_h)} tall x {dt(L)} long  ({'box back' if back else 'box front, behind the maple front'})",
          [v], "Both ends sit in the sides' end rabbets. Datums: the blank's own ends and bottom edge.")
    y_face = BOX_Y0 + BOX_D - T12 if back else BOX_Y0 + T12 - DADO
    if back:
        probes = cut_probes(x_blank, y_face, z0 + UM_RECESS, L, DADO, T6, "+y")
        probes.append((_box(x_blank - 2, y_face + 1, z0 + UM_RECESS + 1, 3, DADO - 2, T6 - 2), "empty"))            # runs out
        probes.append((_box(x_blank + L - 1, y_face + 1, z0 + UM_RECESS + 1, 3, DADO - 2, T6 - 2), "empty"))
        for x in (x_blank, x_blank + L - stop):
            probes.append((_box(x + 1, y_face + 1, z0 + 1, stop - 2, T12 - 2, UM_HOOK_NOTCH_H - 2), "empty"))      # hook notch
            probes.append((_box(x + 1, y_face + DADO + 1, z0 + UM_HOOK_NOTCH_H + 0.5, stop - 2, T12 - DADO - 2, 1), "solid"))   # wood above it, behind the groove
    else:   # the box front's groove is on its rear (inner) face, so its floor is toward the front
        probes = cut_probes(x_blank, y_face, z0 + UM_RECESS, L, DADO, T6, "-y")
        probes.append((_box(x_blank - 2, y_face + 1, z0 + UM_RECESS + 1, 3, DADO - 2, T6 - 2), "empty"))
    check(name, solid, probes)


def drawer_bottom(sfx):
    name = f"drawer_bottom_{sfx}"
    solid = part(name)
    z0 = BOX_BOT_Z0 if sfx == "bot" else BOX_TOP_Z0
    L, D = END_LEN, BOX_D - 2 * (T12 - DADO)
    v = View(L, D, "plan view; FRONT edge along the bottom, REAR edge along the top")
    v.callout(L / 2, D / 2, f"plain rectangle, no joinery; all four edges sit {dt(DADO)} deep in the box's grooves")
    v.dim_h(0, L, v.top_y())
    v.dim_v(0, D, L + 26)
    v.edge("bottom", "FRONT edge")
    sheet(name, f"{name}  x1  |  {PLY6}, {dt(D)} x {dt(L)}", [v],
          "Sits in the 1/4 in grooves of the sides, front and back, 1/2 in above the box's bottom edges.")
    assert abs(solid.volume - L * D * T6) < 1e-6, (name, "drawn as a plain rectangle but the solid has cuts")


def top_slab():
    v = View(TOP_W, TOP_D, "plan view from above; FRONT edge along the bottom")
    for x in (X0, XR - POST):
        for y in (Y0, YB - POST):
            v.hidden(x, y, POST, POST)
    v.callout(X0 + POST / 2, Y0 + POST / 2, f"dashed: the four post tops, {dt(OH)} inside the edges (provisional overhang); "
                                            "figure-8 screw holes are marked from the fasteners at assembly")
    v.dim_h(0, OH, -22)
    v.dim_h(0, TOP_W, v.top_y())
    v.dim_v(0, TOP_D, TOP_W + 26)
    v.edge("bottom", "FRONT edge")
    sheet("top", f"top  x1  |  butcherblock {dt(TOP_T)} thick, {dt(TOP_D)} x {dt(TOP_W)}", [v],
          "Purchased to match the Boos island; edge profile and overhang still to be measured there.")


if __name__ == "__main__":
    post(True)
    post(False)
    panel("side")
    panel("back")
    for r in ("rail_top", "rail_mid", "rail_bot", "cleat_rear"):
        rail(r)
    bottom_panel()
    plain("front_bot", FRONT_W, FRONT_BOT_H, FRONT_T, "solid maple, grain along the length; no joinery; screwed to the box from inside through slotted holes")
    plain("front_top", FRONT_W, FRONT_TOP_H, FRONT_T, "solid maple, grain along the length, cut in sequence with front_bot from one board; no joinery")
    for sfx in ("bot", "top"):
        drawer_side(sfx)
        drawer_end(sfx, back=False)
        drawer_end(sfx, back=True)
        drawer_bottom(sfx)
    top_slab()
    print("all drawings probed against the solids: OK")
