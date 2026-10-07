#!/usr/bin/env python
"""Shop drawings for every cut-list part of the built-in alcove bench.

Same machinery as projects/Drawer-bench/part_drawings.py. Every cut is
written once as a world box from the constants in built_in_bench.py; that
box is probed against the real solid (a box 1 mm inside the cut must be
air, a 1 mm slab just past its floor must be wood, plus wall and run-out
probes where they apply) and the same box is projected onto the view, so a
drawing cannot show a cut the model does not have, or in another place.

Views are true projections of the blank: each names the world axis that
runs to the right and the one that runs up, and the blank's own bounding
box sets the zero, so every dimension reads from that part's edges.

Inches only, to the nearest 1/32 (Brian 2026-09-28). A width sized to a
sheet's thickness reads "3/4 ply (measure)" and is cut to the measured sheet.

Usage: .venv/bin/python projects/Built-in-bench/part_drawings.py
Writes projects/Built-in-bench/images/parts/<part>.png.
"""
import math
import os
import sys

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
sys.path.insert(0, PROJ)
sys.path.insert(0, f"{VAULT}/scripts")
from built_in_bench import *   # noqa: F401,F403  constants, solids and build123d names; runs the model's checks once
from built_in_bench import _box, part, vol, inch, PARTS  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402
from matplotlib.patches import Polygon as MplPolygon  # noqa: E402
from shapely import geometry as sg  # noqa: E402

OUT = f"{PROJ}/images/parts"
os.makedirs(OUT, exist_ok=True)
INK, PAPER, WOOD, CUT, HIDDEN, DIM = "#3b2f22", "#f6f1e8", "#efdcb8", "#d4bb8e", "#8a7d63", "#7a4a1a"
ROW = 16   # mm between callout rows above a blank (scaled with the view)
WRITTEN = []


def dt(mm):
    """Dimension text: inches to the nearest 1/32."""
    return inch(mm)


P18, P12, P6 = "3/4 ply (measure)", "1/2 BB (measure)", "1/4 ply (measure)"


def info(name):
    return next(p for p in PARTS if p["name"] == name)


# --- drawing model ------------------------------------------------------------
class View:
    """One orthographic view of a blank: w x h in mm, x right, y up, plus cuts,
    callouts, dimensions and edge labels in the same coordinates. Callouts sit
    in rows above the blank with a leader down to the feature. `shape` (a
    shapely polygon) replaces the plain rectangle for profiled blanks; notch()
    cuts the outline itself, so a corner notch reads as a notch."""

    def __init__(self, w, h, title, shape=None, size="main"):
        self.w, self.h, self.title, self.size = w, h, title, size
        self.shape = shape if shape is not None else sg.box(0, 0, w, h)
        self.ops = []
        self.rows = 0
        self.row_mm = max(ROW, 0.05 * max(w, h))
        self.k = max(1.0, max(w, h) / 800)      # dimension offsets grow with long parts

    def o(self, mm):
        return mm * self.k

    def groove(self, x, y, w, h):
        self.ops.append(("groove", (x, y, w, h)))

    def cutshape(self, geom):
        self.ops.append(("cutshape", geom))

    def notch(self, x, y, w, h):
        self.shape = self.shape.difference(sg.box(x, y, x + w, y + h))

    def hidden(self, x, y, w, h):
        self.ops.append(("hidden", (x, y, w, h)))

    def bore(self, cx, cy, r, hidden=False):
        self.ops.append(("bore", (cx, cy, r, hidden)))

    def mark(self, x0, y0, x1, y1):
        self.ops.append(("mark", (x0, y0, x1, y1)))

    def callout(self, px, py, text, row=None, ha=None):
        row = self.rows if row is None else row
        self.rows = max(self.rows, row + 1)
        self.ops.append(("callout", (px, py, row, ha), text))

    def top_y(self):
        """Y just above the callout rows, for the overall dimension."""
        return self.h + self.row_mm * (self.rows + 0.9)

    def dim_h(self, x0, x1, y, text=None):
        self.ops.append(("dim_h", (x0, x1, y), text))

    def dim_v(self, y0, y1, x, text=None):
        self.ops.append(("dim_v", (y0, y1, x), text))

    def edge(self, side, text, at=0.5):
        self.ops.append(("edge", (side, at), text))

    def note(self, x, y, text):
        self.ops.append(("note", (x, y), text))


def _polys(geom):
    return list(geom.geoms) if hasattr(geom, "geoms") else [geom]


def _draw(ax, v):
    for g in _polys(v.shape):
        ax.add_patch(MplPolygon(list(g.exterior.coords), closed=True, facecolor=WOOD, edgecolor=INK, lw=1.2, zorder=1))
        for hole in g.interiors:
            ax.add_patch(MplPolygon(list(hole.coords), closed=True, facecolor=PAPER, edgecolor=INK, lw=1.2, zorder=2))
    xs, ys = [0, v.w], [0, v.h]
    dash = (0, (4, 3))
    k = v.k
    for op in v.ops:
        kind, a = op[0], op[1]
        text = op[2] if len(op) > 2 else None
        if kind == "groove":
            ax.add_patch(Rectangle(a[:2], a[2], a[3], facecolor=CUT, edgecolor=INK, lw=0.8, hatch="////", zorder=2))
        elif kind == "cutshape":
            for g in _polys(a.intersection(v.shape)):
                if g.area > 0:
                    ax.add_patch(MplPolygon(list(g.exterior.coords), closed=True, facecolor=CUT, edgecolor=INK,
                                            lw=0.8, hatch="////", zorder=2))
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
            px, py, row, ha = a
            ty = v.h + v.row_mm * (row + 0.75)
            ax.plot([px, px], [py, ty - v.row_mm * 0.25], color=HIDDEN, lw=0.6, zorder=4)
            ax.plot([px], [py], marker="o", ms=2.2, color=HIDDEN, zorder=4)
            ha = ha or ("left" if px < v.w * 0.3 else ("right" if px > v.w * 0.7 else "center"))
            ax.text(px, ty, text, ha=ha, va="center", fontsize=6.5, color=INK, zorder=5,
                    bbox=dict(facecolor=PAPER, edgecolor="none", pad=1.0))
            ys.append(ty + v.row_mm * 0.5)
        elif kind == "dim_h":
            x0, x1, y = a
            above = y >= v.h / 2
            ye = v.h if above else 0
            for x in (x0, x1):
                ax.plot([x, x], [ye, y + (2 * k if above else -2 * k)], color=DIM, lw=0.5, zorder=4)
            ax.annotate("", xy=(x1, y), xytext=(x0, y), zorder=4,
                        arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.7, shrinkA=0, shrinkB=0, mutation_scale=7))
            ax.text((x0 + x1) / 2, y + (1.5 * k if above else -1.5 * k), text or dt(abs(x1 - x0)), ha="center",
                    va="bottom" if above else "top", fontsize=6.5, color=DIM, zorder=5)
            ys.append(y + (v.row_mm * 0.7 if above else -v.row_mm * 0.7))
        elif kind == "dim_v":
            y0, y1, x = a
            right = x >= v.w / 2
            xe = v.w if right else 0
            for y in (y0, y1):
                ax.plot([xe, x + (2 * k if right else -2 * k)], [y, y], color=DIM, lw=0.5, zorder=4)
            ax.annotate("", xy=(x, y1), xytext=(x, y0), zorder=4,
                        arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.7, shrinkA=0, shrinkB=0, mutation_scale=7))
            ax.text(x + (1.5 * k if right else -1.5 * k), (y0 + y1) / 2, text or dt(abs(y1 - y0)),
                    ha="left" if right else "right", va="center", fontsize=6.5, color=DIM, rotation=90, zorder=5)
            xs.append(x + (v.row_mm * 0.8 if right else -v.row_mm * 0.8))
        elif kind == "edge":
            side, at = a
            g = 2.5 * k
            if side == "bottom":
                ax.text(v.w * at, -g, text, ha="center", va="top", fontsize=6.5, color=INK, style="italic", zorder=5)
            elif side == "top":
                ax.text(v.w * at, v.h + g, text, ha="center", va="bottom", fontsize=6.5, color=INK, style="italic", zorder=5)
            elif side == "left":
                ax.text(-g, v.h * at, text, ha="right", va="center", fontsize=6.5, color=INK, style="italic", rotation=90, zorder=5)
            else:
                ax.text(v.w + g, v.h * at, text, ha="left", va="center", fontsize=6.5, color=INK, style="italic", rotation=90, zorder=5)
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
    gap, top, bottom = 0.3, 0.7, 0.42 if note else 0.15
    if stack:
        fw = max(b[0] for b in boxes) + 2 * gap
        fh = sum(b[1] for b in boxes) + gap * (len(boxes) - 1) + top + bottom
    else:
        fw = sum(b[0] for b in boxes) + gap * (len(boxes) + 1)
        fh = max(b[1] for b in boxes) + top + bottom
    fw = max(fw, 8.5)
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
    for t in [title, note or ""] + [v.title for v in views] + [o[2] for v in views for o in v.ops if len(o) > 2 and o[2]]:
        assert "—" not in t and " mm" not in t, (name, "metric or em dash in the text", t)
    png = f"{OUT}/{name}.png"
    fig.savefig(png, dpi=170, facecolor=PAPER)
    plt.close(fig)
    WRITTEN.append(png)


# --- projection: a face of the real blank as a View ------------------------------
class Face:
    """A view of the blank: `right` and `up` are signed world axes ('+y', '-x').
    The viewer looks along up x right, so the drawn face is a true projection,
    not a mirror image. u, v start at the blank's own edges (its bounding box);
    `win` = (u0, u1, v0, v1) crops a detail and shifts its origin."""

    def __init__(self, solid, right, up, win=None):
        bb = solid.bounding_box()
        self.lo = {"x": bb.min.X, "y": bb.min.Y, "z": bb.min.Z}
        self.hi = {"x": bb.max.X, "y": bb.max.Y, "z": bb.max.Z}
        self.right, self.up = right, up
        fw = self.hi[right[1]] - self.lo[right[1]]
        fh = self.hi[up[1]] - self.lo[up[1]]
        self.win = win or (0, fw, 0, fh)
        self.w = self.win[1] - self.win[0]
        self.h = self.win[3] - self.win[2]

    def _map(self, ax, a, b):
        k = ax[1]
        return (a - self.lo[k], b - self.lo[k]) if ax[0] == "+" else (self.hi[k] - b, self.hi[k] - a)

    def rect(self, b):
        """World box (x, y, z, dx, dy, dz) -> view rect (u, v, w, h), clipped to the view."""
        lo = dict(zip("xyz", b[:3]))
        sz = dict(zip("xyz", b[3:]))
        u0, u1 = self._map(self.right, lo[self.right[1]], lo[self.right[1]] + sz[self.right[1]])
        v0, v1 = self._map(self.up, lo[self.up[1]], lo[self.up[1]] + sz[self.up[1]])
        u0, u1 = max(u0 - self.win[0], 0), min(u1 - self.win[0], self.w)
        v0, v1 = max(v0 - self.win[2], 0), min(v1 - self.win[2], self.h)
        return (u0, v0, max(u1 - u0, 0), max(v1 - v0, 0))

    def pt(self, x, y, z):
        p = {"x": x, "y": y, "z": z}
        u = self._map(self.right, p[self.right[1]], p[self.right[1]])[0] - self.win[0]
        v = self._map(self.up, p[self.up[1]], p[self.up[1]])[0] - self.win[2]
        return u, v


def check_blank(name, x, y, z, dx, dy, dz):
    """The blank built from the constants is the one in the model."""
    bb = part(name).bounding_box()
    got = (bb.min.X, bb.min.Y, bb.min.Z, bb.size.X, bb.size.Y, bb.size.Z)
    assert all(abs(a - b) < 1e-6 for a, b in zip(got, (x, y, z, dx, dy, dz))), (name, "blank moved", got)


# --- probes: the drawn cuts must exist in the solid ----------------------------
def slab(x, y, z, dx, dy, dz, side):
    """A 1 mm slab just past `side` ('-x' ... '+z') of the box, inset 1 mm on the other axes."""
    lo = {"x": x, "y": y, "z": z}
    sz = {"x": dx, "y": dy, "z": dz}
    f = {k: (lo[k] + 1, sz[k] - 2) for k in "xyz"}
    ax = side[1]
    f[ax] = (lo[ax] - 1.5, 1.0) if side[0] == "-" else (lo[ax] + sz[ax] + 0.5, 1.0)
    return _box(f["x"][0], f["y"][0], f["z"][0], f["x"][1], f["y"][1], f["z"][1])


def runout(x, y, z, dx, dy, dz, side):
    """A box straddling the cut's end on `side` (2 mm outside, 1 mm inside): air if the cut runs out there."""
    lo = {"x": x, "y": y, "z": z}
    sz = {"x": dx, "y": dy, "z": dz}
    f = {k: (lo[k] + 1, sz[k] - 2) for k in "xyz"}
    ax = side[1]
    f[ax] = (lo[ax] - 2, 3.0) if side[0] == "-" else (lo[ax] + sz[ax] - 1, 3.0)
    return (_box(f["x"][0], f["y"][0], f["z"][0], f["x"][1], f["y"][1], f["z"][1]), "empty")


def cut_probes(x, y, z, dx, dy, dz, floor):
    """A box 1 mm inside the cut must be air; a 1 mm slab just past its floor must be wood."""
    inside = _box(x + 1, y + 1, z + 1, dx - 2, dy - 2, dz - 2)
    return [(inside, "empty"), (slab(x, y, z, dx, dy, dz, floor), "solid")]


def wood(x, y, z, dx, dy, dz, side):
    return (slab(x, y, z, dx, dy, dz, side), "solid")


def check(name, solid, probes):
    for box, expect in probes:
        v = vol(box & solid)
        if expect == "empty":
            assert v < 1e-6, (name, "drawn cut is not in the solid", v)
        else:
            assert abs(v - box.volume) < 1e-6, (name, "wood expected past the cut", v, box.volume)
    return len(probes)


def assert_plain(name):
    s = part(name)
    bb = s.bounding_box()
    assert abs(s.volume - bb.size.X * bb.size.Y * bb.size.Z) < 1e-3, (name, "drawn as a plain rectangle but the solid has cuts")


def head(name, text):
    p = info(name)
    return f"{name}  x{p['qty']}  |  {text}"


# --- parts -----------------------------------------------------------------------
def plain(name, right, up, title, note, sheet_note=None, edges=None):
    assert_plain(name)
    P = Face(part(name), right, up)
    v = View(P.w, P.h, title)
    v.callout(P.w / 2, P.h / 2, note)
    v.dim_h(0, P.w, v.top_y())
    v.dim_v(0, P.h, P.w + v.o(26))
    for side, t in (edges or {}).items():
        v.edge(side, t)
    return P, v


def base_rails():
    for name, right in (("base_end_rail", "+y"), ("base_long_rail", "+x"), ("base_center_rail", "+y")):
        P, v = plain(name, right, "+z", "face view", "hidden ladder base, any 3/4 ply; plain rectangle, no joinery",
                     edges={"bottom": "bottom edge (on the floor)"})
        use = {"base_end_rail": "front to back under each end panel; the end panels stand on these",
               "base_long_rail": "front and back rails, between the end rails; glue and screws or pocket screws",
               "base_center_rail": "between the long rails, under the partition"}[name]
        sheet(name, head(name, f"3/4 ply (any, hidden), {dt(P.h)} tall x {dt(P.w)} long"), [v], use)


def end_panel():
    name = "end"
    solid = part(name)
    H = TOP_Z0 - BOT_Z0
    check_blank(name, X0, 0, BOT_Z0, T18, CASE_D, H)
    rab = (END_IN_L - RABBET_D, 0, BOT_Z0, RABBET_D, CASE_D, T18)
    grv = (END_IN_L - BACK_GROOVE_D, BACK_Y0, BOT_Z0, BACK_GROOVE_D, T6, H)

    P = Face(solid, "+y", "+z")            # looking at the inside face: rear edge left, front edge right
    L = P.w
    v = View(L, H, "A  INSIDE face (toward the drawers); REAR edge at left, FRONT edge at right, bottom edge down")
    v.groove(*P.rect(rab))
    v.groove(*P.rect(grv))
    gu = P.rect(grv)[0]
    v.callout(L * 0.6, T18 / 2, f"rabbet along the bottom edge, runs out both ends: {P18} tall x {dt(RABBET_D)} deep; the case bottom sits in it")
    v.callout(gu + T6 / 2, H * 0.6, f"back groove, runs out top and bottom: {P6} wide x {dt(BACK_GROOVE_D)} deep, "
                                    f"{dt(BACK_SET)} in from the REAR edge", ha="left")
    v.dim_v(0, T18, L + v.o(26), P18)
    v.dim_v(0, H, L + v.o(60))
    v.dim_h(0, L, v.top_y())
    v.edge("left", "REAR edge")
    v.edge("right", "FRONT edge")

    S = Face(solid, "-x", "+z", win=(0, T18, 0, 50))       # front edge, looking back: inside face at left
    a = View(S.w, S.h, "B  front edge, bottom corner\n(inside face at left)", size="small")
    a.notch(*S.rect(rab))
    a.dim_h(0, RABBET_D, -8, dt(RABBET_D))
    a.dim_v(0, T18, T18 + 10, P18)
    a.edge("left", "inside face")
    a.edge("bottom", "bottom edge")

    T = Face(solid, "+y", "-x", win=(0, 40, 0, T18))       # top end from above: inside face along the bottom
    b = View(T.w, T.h, "C  top end from above, rear corner\n(inside face along the bottom)", size="small")
    b.notch(*T.rect(grv))
    b.dim_h(0, BACK_SET, T18 + 10)
    b.dim_h(BACK_SET, BACK_SET + T6, -10, P6)
    b.dim_v(0, BACK_GROOVE_D, T.w + 8, dt(BACK_GROOVE_D))
    b.edge("left", "REAR edge")
    b.edge("bottom", "inside face")

    sheet(name, head(name, f"3/4 maple ply, {dt(H)} tall x {dt(L)} deep, face grain vertical; mirror pair (the other end is drawn mirror image, front edge at left)"),
          [v, b, a], "Datums: the rear edge and the bottom edge. Cut the rabbet and the groove on the INSIDE face of each end; "
                     "the two ends come out as a left and a right.")
    pr = cut_probes(*rab, "-x")
    pr.append(wood(END_IN_L - RABBET_D, BACK_Y1 + 1, BOT_Z0, RABBET_D, CASE_D - BACK_Y1 - 1, T18, "+z"))   # wood above the rabbet
    pr += [runout(*rab, "-y"), runout(*rab, "+y")]
    pr += cut_probes(*grv, "-x")
    up = (grv[0], grv[1], BOT_Z0 + T18 + 1, grv[3], grv[4], H - T18 - 1)
    pr += [wood(*up, "-y"), wood(*up, "+y"), runout(*grv, "+z"), runout(*grv, "-z")]
    return check(name, solid, pr)


def bottom_panel():
    name = "bottom"
    solid = part(name)
    W = BOT_X1 - BOT_X0
    check_blank(name, BOT_X0, 0, BOT_Z0, W, CASE_D, T18)
    assert abs((BOT_X0 + BOT_X1) / 2 - XC) < 1e-9
    grv = (BOT_X0, BACK_Y0, BOT_Z1 - BACK_GROOVE_D, W, T6, BACK_GROOVE_D)
    dado = (PART_X0, BACK_Y1, BOT_Z1 - DADO_D, T18, CASE_D - BACK_Y1, DADO_D)

    P = Face(solid, "-x", "-y")            # plan from above, FRONT edge toward the viewer (down the page)
    D = P.h
    v = View(W, D, "A  TOP face, seen from above; FRONT edge along the bottom, REAR edge along the top")
    v.groove(*P.rect(grv))
    v.groove(*P.rect(dado))
    gv = P.rect(grv)[1]
    du, dv, _, dh = P.rect(dado)
    v.callout(W * 0.2, gv + T6 / 2, f"back groove, runs out both ends: {P6} wide x {dt(BACK_GROOVE_D)} deep, {dt(BACK_SET)} in from the REAR edge")
    v.callout(du + T18 / 2, D * 0.45, f"partition dado, centered on the length: {P18} wide x {dt(DADO_D)} deep; "
                                      "from the FRONT edge back into the back groove (stops there)")
    v.dim_h(0, du, -v.o(22))
    v.dim_h(du, du + T18, -v.o(46), P18)
    v.dim_v(0, dh, -v.o(22))
    v.dim_v(0, D, W + v.o(26))
    v.dim_h(0, W, v.top_y())
    v.edge("bottom", "FRONT edge (hidden behind the drawer fronts)", at=0.22)
    v.edge("left", "end: sits in the end panel's rabbet")
    v.edge("right", "end: sits in the end panel's rabbet")

    S = Face(solid, "-x", "+z")
    mid = S.pt(XC, 0, 0)[0]
    S = Face(solid, "-x", "+z", win=(mid - 40, mid + 40, 0, T18))
    a = View(S.w, S.h, "B  FRONT edge at the dado\n(seen from the front)", size="small")
    a.notch(*S.rect(dado))
    a.dim_h(40 - T18 / 2, 40 + T18 / 2, T18 + 8, P18)
    a.dim_v(T18 - DADO_D, T18, S.w + 8, dt(DADO_D))
    a.edge("bottom", "bottom face")

    E = Face(solid, "+y", "+z", win=(0, 40, 0, T18))
    b = View(E.w, E.h, "C  end, rear corner\n(seen from the end)", size="small")
    b.notch(*E.rect(grv))
    b.dim_h(0, BACK_SET, T18 + 8)
    b.dim_h(BACK_SET, BACK_SET + T6, -8, P6)
    b.dim_v(T18 - BACK_GROOVE_D, T18, E.w + 8, dt(BACK_GROOVE_D))
    b.edge("left", "REAR edge")

    sheet(name, head(name, f"3/4 maple ply, {dt(D)} deep x {dt(W)} long, face grain along the length"), [v, a, b],
          f"Both ends sit in the end panels' {dt(RABBET_D)} rabbets. Datums: the REAR edge and the left end. "
          "The dado is centered: mark it from the middle of the blank.")
    pr = cut_probes(*grv, "-z")
    left = (BOT_X0, BACK_Y0, grv[2], PART_X0 - BOT_X0 - 1, T6, BACK_GROOVE_D)
    pr += [wood(*left, "-y"), wood(*left, "+y"), runout(*grv, "-x"), runout(*grv, "+x")]
    pr += cut_probes(*dado, "-z")
    pr += [wood(*dado, "-x"), wood(*dado, "+x"), runout(*dado, "+y"), runout(*dado, "-y")]
    pr.append((_box(PART_X0 + 1, BACK_Y0 - 1.5, dado[2] + 1, T18 - 2, 1, DADO_D - 2), "solid"))   # stops at the groove
    return check(name, solid, pr)


def partition():
    name = "partition"
    solid = part(name)
    L, H = CASE_D - BACK_Y1, TOP_Z0 - PART_Z0
    check_blank(name, PART_X0, BACK_Y1, PART_Z0, T18, L, H)
    nt = (PART_X0, BACK_Y1, NAILER_Z0, T18, TS, NAILER_H)
    P = Face(solid, "+y", "+z")
    v = View(L, H, "side face (both faces are the same); REAR edge at left, FRONT edge at right")
    v.notch(*P.rect(nt))
    v.callout(TS / 2, H - NAILER_H / 2, f"notch the top REAR corner, through: {dt(TS)} deep x {dt(NAILER_H)} tall; the nailer passes through it", row=1)
    v.dim_h(0, TS, H + v.row_mm * 0.45)
    v.dim_v(H - NAILER_H, H, -v.o(22))
    v.dim_v(0, H, L + v.o(26))
    v.dim_h(0, L, v.top_y())
    v.edge("left", "REAR edge (against the back)")
    v.edge("right", "FRONT edge")
    v.edge("bottom", "bottom edge (in the dado)")
    sheet(name, head(name, f"3/4 maple ply, {dt(H)} tall x {dt(L)} deep, face grain vertical"), [v],
          f"The bottom edge sits {dt(DADO_D)} deep in the bottom panel's dado; the rear edge stops against the back panel. Datums: the REAR edge and the top edge.")
    pr = cut_probes(*nt, "+y")
    pr += [wood(*nt, "-z"), runout(*nt, "-y"), runout(*nt, "+z")]
    return check(name, solid, pr)


def nailer():
    name = "nailer"
    solid = part(name)
    L = END_IN_R - END_IN_L
    check_blank(name, END_IN_L, NAILER_Y0, NAILER_Z0, L, TS, NAILER_H)
    r = FIG8_DIA / 2
    chord = math.sqrt(r * r - FIG8_OFFSET ** 2)          # half-width of the opening on the front face

    P = Face(solid, "-x", "-y")            # top edge from above, FRONT face down the page
    t = View(L, TS, "A  TOP edge, seen from above; FRONT face along the bottom")
    us = []
    for xc in FIG8_XS:
        u, vv = P.pt(xc, FIG8_Y, TOP_Z0)
        us.append(u)
        t.cutshape(sg.Point(u, vv).buffer(r, 64))
    us.sort()
    t.callout(us[1], FIG8_OFFSET, f"4 figure-8 recesses: {dt(FIG8_DIA)} forstner, {dt(FIG8_DEPTH)} deep, "
                                  f"centered {dt(FIG8_OFFSET)} in from the front face so the recess opens through it", row=1)
    for i, u in enumerate(us):
        t.dim_h(0, u, -t.o(18 + 22 * i))
    t.dim_h(0, L, t.top_y())
    t.edge("top", "rear face (against the back panel)", at=0.86)
    t.edge("bottom", "FRONT face", at=0.95)

    F = Face(solid, "-x", "+z")            # front face, looking toward the back wall
    f = View(L, NAILER_H, "B  FRONT face (toward the drawers); top edge up")
    for xc in FIG8_XS:
        u, _ = F.pt(xc, 0, 0)
        f.groove(u - chord, NAILER_H - FIG8_DEPTH, 2 * chord, FIG8_DEPTH)
    f.callout(sorted(F.pt(x, 0, 0)[0] for x in FIG8_XS)[2], NAILER_H - FIG8_DEPTH / 2,
              f"each recess shows here as a {dt(2 * chord)} wide opening in the top edge")
    f.callout(L * 0.2, NAILER_H * 0.4, "wall screws through the nailer and the back into the studs: mark at install")
    f.dim_v(0, NAILER_H, L + f.o(26))
    f.dim_h(0, L, f.top_y())
    f.edge("bottom", "bottom edge")

    u0 = us[0]
    D = Face(solid, "-x", "-y", win=(u0 - 22, u0 + 22, 0, TS))
    d = View(D.w, D.h, "C  detail, one recess (top edge from above)", size="small")
    d.cutshape(sg.Point(22, FIG8_OFFSET).buffer(r, 64))
    d.mark(22, 0, 22, TS)
    d.dim_v(0, FIG8_OFFSET, -8, dt(FIG8_OFFSET))
    d.dim_h(22 - r, 22 + r, TS + 10, f"{dt(FIG8_DIA)} dia")
    d.dim_h(22 - chord, 22 + chord, -8, dt(2 * chord))
    d.edge("bottom", "FRONT face")

    sheet(name, head(name, f"hard maple {dt(TS)} thick, {dt(NAILER_H)} tall x {dt(L)} long, on edge at the top back"),
          [t, f, d], "Recess positions are from the left end of view A (the layout is symmetric, so either end works). "
                     "The recess must open through the FRONT face so the figure-8 swings out under the top.", stack=True)
    pr = []
    for xc in FIG8_XS:
        pr += cut_probes(xc - 3, FIG8_Y - 3, TOP_Z0 - FIG8_DEPTH, 6, 6, FIG8_DEPTH, "-z")
        pr.append((_box(xc - chord + 1, NAILER_Y1 - 1, TOP_Z0 - FIG8_DEPTH + 0.5, 2 * chord - 2, 3, FIG8_DEPTH), "empty"))  # opens through
        pr.append((_box(xc - 2, NAILER_Y0 + 0.5, TOP_Z0 - FIG8_DEPTH + 0.5, 4, 1, FIG8_DEPTH - 1), "solid"))              # rear wall
        pr.append((_box(xc + r + 0.5, FIG8_Y - 1, TOP_Z0 - FIG8_DEPTH + 0.5, 1, 2, FIG8_DEPTH - 1), "solid"))              # not wider
        pr.append((_box(xc + r - 1.5, FIG8_Y - 1, TOP_Z0 - FIG8_DEPTH + 0.5, 1, 2, FIG8_DEPTH), "empty"))                 # full dia
    return check(name, solid, pr)


def back_panel():
    name = "back"
    P, v = plain(name, "+x", "+z", "face view", "plain rectangle, no joinery")
    check_blank(name, BOT_X0 + PLAY / 2, BACK_Y0, PART_Z0 + PLAY / 2, BOT_X1 - BOT_X0 - PLAY, T6, TOP_Z0 - PART_Z0 - PLAY)
    v.edge("bottom", "bottom edge (in the bottom panel's groove)")
    sheet(name, head(name, f"1/4 maple ply, {dt(P.h)} tall x {dt(P.w)} long"), [v],
          f"Slides down the end grooves into the bottom groove; {dt(PLAY)} total play is already taken off both sizes. "
          "Confirm the low receptacle on the back wall before cutting.")
    return 0


def scribe_strip():
    name = "scribe_strip"
    assert_plain(name)
    H = TOP_Z0 - BASE_H
    check_blank(name, 0, FACE_Y0, BASE_H, STRIP_W, FACE_T, H)
    v = View(STRIP_CUT, H, "face view from the room; inner edge at left (the strip at the right-hand wall is its mirror)")
    v.mark(STRIP_W, 0, STRIP_W, H)
    v.callout(STRIP_CUT * 0.2, H * 0.6, f"rip at {dt(STRIP_CUT)}, scribe to the wall so the inner edge is flush with the inside of the end panel (about {dt(STRIP_W)})", ha="left")
    v.callout(STRIP_W, H * 0.3, "dashed: scribe line, about here; waste toward the wall", ha="left")
    v.dim_h(0, STRIP_CUT, v.top_y(), f"rip {dt(STRIP_CUT)}")
    v.dim_h(0, STRIP_W, -v.o(14), f"about {dt(STRIP_W)}")
    v.dim_v(0, H, STRIP_CUT + v.o(14))
    v.edge("left", "inner edge")
    v.edge("bottom", "bottom end")
    sheet(name, head(name, f"hard maple, {dt(H)} long, ripped {dt(STRIP_CUT)} wide, milled to the drawer-front panel's thickness (measure)"),
          [v], "Glue and biscuits to the end panel's front edge; the inner edge lands flush with the inside face of the end.")
    return 0


def plinth():
    name = "plinth"
    assert_plain(name)
    check_blank(name, 0, FACE_Y0, 0, ALCOVE_W, FACE_T, PLINTH_H)
    CUTH = 4.25 * IN
    v = View(ALCOVE_W, CUTH, "face view from the room; top edge up")
    v.mark(0, CUTH - PLINTH_H, ALCOVE_W, CUTH - PLINTH_H)
    v.callout(ALCOVE_W * 0.5, CUTH * 0.7, f"cut {dt(CUTH)} tall and scribe to the floor; top edge {dt(GAP)} under the fronts")
    v.callout(ALCOVE_W * 0.25, CUTH - PLINTH_H, f"dashed: floor scribe line, about {dt(PLINTH_H)} down from the top edge")
    v.dim_v(CUTH - PLINTH_H, CUTH, -v.o(14), f"about {dt(PLINTH_H)}")
    v.dim_v(0, CUTH, ALCOVE_W + v.o(14))
    v.dim_h(0, ALCOVE_W, v.top_y(), f"{dt(ALCOVE_W)}, scribe both ends to the walls")
    v.edge("bottom", "floor edge (scribed)")
    sheet(name, head(name, f"hard maple, cut {dt(CUTH)} x {dt(ALCOVE_W)}, grain horizontal, milled to the drawer-front panel's thickness (measure)"),
          [v], "Screwed to the base front rail; flush with the drawer fronts.")
    return 0


def top_slab():
    name = "top"
    solid = part(name)
    D = TOP_Y1 - TOP_Y0
    check_blank(name, 0, TOP_Y0, TOP_Z0, ALCOVE_W, D, TS)
    P = Face(solid, "-x", "-y")
    v = View(ALCOVE_W, D, "A  plan from above; FRONT edge along the bottom")
    v.mark(0, ROUND, ALCOVE_W, ROUND)
    v.callout(ALCOVE_W * 0.8, ROUND, f"{dt(ROUND)} roundover on both FRONT arrises (top and bottom); dashed: where it starts")
    v.dim_h(0, ALCOVE_W, v.top_y(), f"{dt(ALCOVE_W)}, scribe both ends to the walls")
    v.dim_v(0, D, ALCOVE_W + v.o(26))
    v.edge("bottom", "FRONT edge")
    v.edge("top", f"REAR edge: {dt(WALL_GAP)} gap to the back wall for wood movement")
    c = sg.box(0, 0, 40, TS)
    for cy in (ROUND, TS - ROUND):
        corner = sg.box(0, 0 if cy < TS / 2 else TS - ROUND, ROUND, ROUND if cy < TS / 2 else TS)
        c = c.difference(corner.difference(sg.Point(ROUND, cy).buffer(ROUND, 64)))
    s = View(40, TS, "B  section at the FRONT edge\n(front at left)", shape=c, size="small")
    s.dim_v(0, TS, 40 + 8)
    s.callout(1, TS - 1, f"{dt(ROUND)} R, top and bottom", ha="left")
    s.edge("left", "FRONT")
    sheet(name, head(name, f"hard maple {dt(TS)} thick, {dt(D)} deep x {dt(ALCOVE_W)} long"), [v, s],
          "Glue up from 4 or 5 boards, grain along the 66 in length. Floats: pocket screws up through the ends and the partition near the front, figure-8s on the nailer at the back.")
    pr = []
    for z in (TOP_Z0, TOP_Z0 + TS - 0.6):                              # the two front arrises are rounded
        pr.append((_box(1, TOP_Y1 - 0.6, z, ALCOVE_W - 2, 0.6, 0.6), "empty"))
    pr.append((_box(1, TOP_Y1 - ROUND - 1.5, TOP_Z0 + 1, ALCOVE_W - 2, 1, TS - 2), "solid"))           # behind the roundover
    pr.append((_box(1, TOP_Y1 - 0.6, TOP_Z0 + ROUND + 0.5, ALCOVE_W - 2, 0.6, TS - 2 * ROUND - 1), "solid"))   # not bigger
    pr.append((_box(1, TOP_Y0, TOP_Z0 + TS - 0.6, ALCOVE_W - 2, 0.6, 0.6), "solid"))                   # rear arris sharp
    return check(name, solid, pr)


def front_stile():
    name = "front_stile"
    solid = part(name)
    x0 = FRONT_X0[0]
    check_blank(name, x0, FACE_Y0, FRONT_Z0, STILE_W, FACE_T, FRONT_H)
    g = (x0 + STILE_W - TONGUE_L, GY0, FRONT_Z0, TONGUE_L, TONGUE_T, FRONT_H)

    F = Face(solid, "-x", "+z")            # show face from the room: inner edge at left
    f = View(STILE_W, FRONT_H, "A  FRONT (show) face\ninner edge at left", size="small")
    f.hidden(*F.rect(g))
    f.callout(TONGUE_L / 2, FRONT_H * 0.55, "dashed: groove in the inner edge", ha="left")
    f.dim_h(0, STILE_W, -10)
    f.dim_v(0, FRONT_H, STILE_W + 12)
    f.edge("left", "inner edge")

    E = Face(solid, "+y", "+z")            # inner edge: front face at right
    e = View(FACE_T, FRONT_H, "B  INNER edge\nfront face at right", size="small")
    e.groove(*E.rect(g))
    e.callout(FACE_T / 2, FRONT_H * 0.5, f"groove, through both ends: {dt(TONGUE_T)} wide x {dt(TONGUE_L)} deep, centered", ha="left")
    e.dim_v(0, FRONT_H, FACE_T + 26)
    e.edge("right", "FRONT face")

    T = Face(solid, "-x", "-y")            # top end from above
    s = View(STILE_W, FACE_T, "C  top end from above\n(front face down, inner edge at left)", size="small")
    gu, gv, gw, gh = T.rect(g)
    s.notch(gu, gv, gw, gh)
    s.dim_h(0, TONGUE_L, FACE_T + 8, dt(TONGUE_L))
    s.dim_v(gv, gv + gh, -8, dt(TONGUE_T))
    s.dim_v(0, FACE_T, STILE_W + 8, P18)
    s.edge("bottom", "FRONT face")

    sheet(name, head(name, f"hard maple, {dt(STILE_W)} x {dt(FRONT_H)}, thickness: {P18}"),
          [f, e, s], "All four the same; mill to the walnut panel's thickness. Groove centered on the thickness (tongue-and-groove bit set). The rail tenon shows on the top end; Brian is fine with that.")
    pr = cut_probes(*g, "-x")
    pr += [wood(*g, "-y"), wood(*g, "+y"), runout(*g, "-z"), runout(*g, "+z")]
    return check(name, solid, pr)


def front_rail():
    name = "front_rail"
    solid = part(name)
    xr0, z0 = FRONT_X0[0] + STILE_W - TONGUE_L, FRONT_Z0
    check_blank(name, xr0, FACE_Y0, z0, RL, FACE_T, STILE_W)
    g = (xr0, GY0, z0 + STILE_W - TONGUE_L, RL, TONGUE_T, TONGUE_L)
    ends = (xr0, xr0 + RL - TONGUE_L)
    cheeks = []
    for xe in ends:
        cheeks.append(((xe, FACE_Y0, z0, TONGUE_L, GY0 - FACE_Y0, STILE_W), "+y", xe))
        cheeks.append(((xe, GY0 + TONGUE_T, z0, TONGUE_L, FACE_Y1 - GY0 - TONGUE_T, STILE_W), "-y", xe))

    P = Face(solid, "-x", "+z")            # front face; the groove edge (inner edge) up
    L, H = RL, STILE_W
    v = View(L, H, "A  FRONT face; inner (grooved) edge up")
    for xe in ends:                                                     # corner above the tenon: no wood at all
        v.notch(*P.rect((xe, FACE_Y0, z0 + STILE_W - TONGUE_L, TONGUE_L, FACE_T, TONGUE_L)))
        v.groove(*P.rect((xe, FACE_Y0, z0, TONGUE_L, GY0 - FACE_Y0, STILE_W - TONGUE_L)))
    v.mark(TONGUE_L, H - TONGUE_L, L - TONGUE_L, H - TONGUE_L)
    v.callout(L * 0.5, H - TONGUE_L / 2, f"dashed: groove in the inner edge, through both ends: {dt(TONGUE_T)} wide x {dt(TONGUE_L)} deep, centered")
    v.callout(TONGUE_L / 2, H * 0.3, f"stub tenon both ends: {dt(TONGUE_T)} thick x {dt(TONGUE_L)} long, centered (same bit); the groove runs through it")
    v.dim_h(TONGUE_L, L - TONGUE_L, -v.o(20), f"{dt(L - 2 * TONGUE_L)} shoulder to shoulder")
    v.dim_h(0, L, v.top_y(), f"{dt(L)} overall, includes both tenons")
    v.dim_v(0, H, L + v.o(16))
    v.edge("bottom", "outer edge")

    E = Face(solid, "-y", "+z")            # tenon end, looking +x: front face at left
    e = View(FACE_T, H, "B  end view (tenon)\nfront face at left", size="small")
    e.notch(*E.rect(g))
    for b, _, xe in cheeks:
        if xe == ends[0]:
            e.groove(*E.rect(b))
    e.callout(FACE_T / 2, (H - TONGUE_L) / 2, "tenon", ha="center")
    gu = E.rect(g)[0]
    e.dim_h(gu, gu + TONGUE_T, -8, dt(TONGUE_T))
    e.dim_v(H - TONGUE_L, H, FACE_T + 8, dt(TONGUE_L))
    e.dim_v(0, H, FACE_T + 22)
    e.dim_h(0, FACE_T, -24, P18)
    e.edge("left", "FRONT face")

    C = Face(solid, "-x", "+z", win=(0, 60, 0, H))
    c = View(C.w, C.h, "C  detail, one end of the FRONT face\n(the other end is the same)", size="small")
    xe = ends[1]                           # the end at the left of this view
    c.notch(*C.rect((xe, FACE_Y0, z0 + STILE_W - TONGUE_L, TONGUE_L, FACE_T, TONGUE_L)))
    c.groove(*C.rect((xe, FACE_Y0, z0, TONGUE_L, GY0 - FACE_Y0, STILE_W - TONGUE_L)))
    c.mark(TONGUE_L, H - TONGUE_L, 60, H - TONGUE_L)
    c.dim_h(0, TONGUE_L, -8, f"{dt(TONGUE_L)} tenon")
    c.dim_v(H - TONGUE_L, H, -8, dt(TONGUE_L))
    c.dim_v(0, H, 60 + 8)

    sheet(name, head(name, f"hard maple, {dt(H)} x {dt(L)} including tenons, thickness: {P18}; all four the same"),
          [v, e, c], "Hatched: cut back to the tenon. The rail's tenon fills the stile groove; its own groove takes the panel tongue.")
    pr = cut_probes(*g, "-z")
    mid = (xr0 + TONGUE_L, GY0, g[2], RL - 2 * TONGUE_L, TONGUE_T, TONGUE_L)
    pr += [wood(*mid, "-y"), wood(*mid, "+y"), runout(*g, "-x"), runout(*g, "+x")]
    for b, floor, xe in cheeks:
        low = b[:5] + (STILE_W - TONGUE_L,)
        pr.append((_box(b[0] + 1, b[1] + 1, b[2] + 1, b[3] - 2, b[4] - 2, b[5] - 2), "empty"))
        pr.append(wood(*low, floor))                                    # tenon cheek
        pr.append(wood(*low, "+x" if xe == ends[0] else "-x"))          # shoulder
        pr.append(runout(*b, "-x" if xe == ends[0] else "+x"))
    return check(name, solid, pr)


def front_panel():
    name = "front_panel"
    solid = part(name)
    px0, pz0 = FRONT_X0[0] + STILE_W - TONGUE_L, FRONT_Z0 + STILE_W - TONGUE_L
    check_blank(name, px0, FACE_Y0, pz0, PW, FACE_T, PH)
    TL = TONGUE_L
    bands = [(px0, pz0, PW, TL), (px0, pz0 + PH - TL, PW, TL), (px0, pz0, TL, PH), (px0 + PW - TL, pz0, TL, PH)]
    P = Face(solid, "-x", "+z")
    v = View(PW, PH, "A  FRONT (show) face; grain horizontal")
    for bx, bz, bw, bh in bands:
        v.groove(*P.rect((bx, FACE_Y0, bz, bw, GY0 - FACE_Y0, bh)))
    v.callout(PW * 0.5, PH * 0.5, "full-thickness field; grain horizontal")
    v.callout(TL / 2, PH * 0.75, f"tongue on all four edges: {dt(TONGUE_T)} thick x {dt(TL)} long, centered (hatched)")
    v.dim_h(TL, PW - TL, -v.o(20), f"{dt(PW - 2 * TL)} field")
    v.dim_v(TL, PH - TL, -v.o(22), f"{dt(PH - 2 * TL)} field")
    v.dim_h(0, PW, v.top_y(), f"{dt(PW)} overall, includes tongues")
    v.dim_v(0, PH, PW + v.o(22), f"{dt(PH)} overall")
    v.edge("bottom", "bottom edge")

    S = Face(solid, "-y", "+z", win=(0, FACE_T, 0, 30))
    s = View(S.w, S.h, "B  section, bottom edge\n(front face at left)", size="small")
    for y0, dy in ((FACE_Y0, GY0 - FACE_Y0), (GY0 + TONGUE_T, FACE_Y1 - GY0 - TONGUE_T)):
        s.notch(*S.rect((px0 + PW / 2, y0, pz0, 1, dy, TL)))
    gu = S.rect((0, GY0, 0, 1, TONGUE_T, 1))[0]
    s.dim_h(gu, gu + TONGUE_T, -8, dt(TONGUE_T))
    s.dim_v(0, TL, FACE_T + 8, dt(TL))
    s.dim_h(0, FACE_T, 30 + 8, P18)
    s.edge("left", "FRONT")

    sheet(name, head(name, f"3/4 walnut ply, {dt(PH)} x {dt(PW)} including tongues, grain horizontal"), [v, s],
          "Cut the tongues with the same bit set as the frame. Glue in all round (plywood does not move). "
          "Mill the maple frame to this sheet's thickness.")
    pr = []
    for bx, bz, bw, bh in bands:
        for y0, dy, floor in ((FACE_Y0, GY0 - FACE_Y0, "+y"), (GY0 + TONGUE_T, FACE_Y1 - GY0 - TONGUE_T, "-y")):
            pr += cut_probes(bx, y0, bz, bw, dy, bh, floor)
    fx, fz, fw, fh = px0 + TL, pz0 + TL, PW - 2 * TL, PH - 2 * TL            # field shoulders
    pr += [wood(fx, FACE_Y0, pz0, fw, FACE_T, TL, "+z"), wood(fx, FACE_Y0, pz0 + PH - TL, fw, FACE_T, TL, "-z"),
           wood(px0, FACE_Y0, fz, TL, FACE_T, fh, "+x"), wood(px0 + PW - TL, FACE_Y0, fz, TL, FACE_T, fh, "-x")]
    return check(name, solid, pr)


def _box_x0():
    return END_IN_L + OPEN_W / 2 - BOX_W / 2      # left drawer, left side outer face


def drawer_side():
    name = "drawer_side"
    solid = part(name)
    x0 = _box_x0()
    check_blank(name, x0, BOX_Y0, BOX_Z0, T12, BOX_D, BOX_H)
    xi = x0 + T12 - RABBET_D
    rf = (xi, BOX_Y1 - T18, BOX_Z0, RABBET_D, T18, BOX_H)
    rb = (xi, BOX_Y0, BOX_Z0, RABBET_D, T18, BOX_H)
    gb = (xi, BOX_Y0, BOX_Z0 + UM_RECESS, RABBET_D, BOX_D, T12)
    P = Face(solid, "+y", "+z")            # inside face: rear end left, FRONT end right
    v = View(BOX_D, BOX_H, "A  INSIDE face (toward the inside of the box); REAR end at left, FRONT end at right")
    for b in (rb, rf, gb):
        v.groove(*P.rect(b))
    v.callout(T18 / 2, BOX_H * 0.7, f"rabbet across both ends: {P18} wide x {dt(RABBET_D)} deep; the box front and back sit in them", ha="left")
    v.callout(BOX_D * 0.5, UM_RECESS + T12 / 2, f"bottom groove, through: {P12} tall x {dt(RABBET_D)} deep, underside {dt(UM_RECESS)} up from the bottom edge")
    v.dim_h(0, T18, -v.o(22), P18)
    v.dim_h(BOX_D - T18, BOX_D, -v.o(22), P18)
    v.dim_v(0, UM_RECESS, -v.o(22))
    v.dim_v(UM_RECESS, UM_RECESS + T12, -v.o(50), P12)
    v.dim_h(0, BOX_D, v.top_y())
    v.dim_v(0, BOX_H, BOX_D + v.o(26))
    v.edge("bottom", "bottom edge")
    v.edge("left", "REAR end")
    v.edge("right", "FRONT end")
    S = Face(solid, "-x", "+z", win=(0, T12, 0, 45))
    s = View(S.w, S.h, "B  section, bottom edge\n(inside face at left)", size="small")
    s.notch(*S.rect(gb))
    s.dim_h(0, RABBET_D, -8, dt(RABBET_D))
    s.dim_v(UM_RECESS, UM_RECESS + T12, T12 + 8, P12)
    s.dim_v(0, UM_RECESS, T12 + 22)
    s.edge("left", "inside face")
    sheet(name, head(name, f"1/2 Baltic birch, {dt(BOX_H)} tall x {dt(BOX_D)} long; all four the same (turn end for end for the other side)"),
          [v, s], "Blum 563H box: the bottom groove sits up off the bottom edge so the runner fits under the bottom. "
                  "Datums: the bottom edge and the blank's ends.")
    pr = cut_probes(*rf, "-x") + cut_probes(*rb, "-x")
    above = BOX_Z0 + UM_RECESS + T12 + 1
    pr += [wood(rf[0], rf[1], above, RABBET_D, T18, BOX_Z0 + BOX_H - above, "-y"),
           wood(rb[0], rb[1], above, RABBET_D, T18, BOX_Z0 + BOX_H - above, "+y")]
    pr += [runout(*rf, "-z"), runout(*rf, "+z"), runout(*rb, "-z"), runout(*rb, "+z")]
    pr += cut_probes(*gb, "-x")
    mid = (xi, BOX_Y0 + T18 + 1, gb[2], RABBET_D, BOX_D - 2 * T18 - 2, T12)
    pr += [wood(*mid, "-z"), wood(*mid, "+z"), runout(*gb, "-y"), runout(*gb, "+y")]
    return check(name, solid, pr)


def drawer_front():
    name = "drawer_front"
    solid = part(name)
    ex0 = _box_x0() + T12 - RABBET_D
    L = END_LEN
    check_blank(name, ex0, BOX_Y1 - T18, BOX_Z0, L, T18, BOX_H)
    gf = (ex0, BOX_Y1 - T18, BOX_Z0 + UM_RECESS, L, RABBET_D, T12)
    P = Face(solid, "+x", "+z")            # inside face, looking toward the room
    v = View(L, BOX_H, "A  INSIDE face (toward the inside of the box); bottom edge down")
    v.groove(*P.rect(gf))
    hx, hz = 3 * IN, 2 * IN
    for u in (hx, L - hx):
        for w in (hz, BOX_H - hz):
            v.bore(u, w, 3 / 16 * IN / 2)
    v.callout(L * 0.5, UM_RECESS + T12 / 2, f"bottom groove, runs out both ends: {P12} tall x {dt(RABBET_D)} deep, underside {dt(UM_RECESS)} up from the bottom edge")
    v.callout(hx, BOX_H - hz, "4 oversize holes, 3/16 dia, through, for the screws into the walnut front", ha="left")
    v.dim_h(0, hx, -v.o(22))
    v.dim_h(L - hx, L, -v.o(22))
    v.dim_v(0, UM_RECESS, -v.o(22))
    v.dim_v(UM_RECESS, UM_RECESS + T12, -v.o(50), P12)
    v.dim_v(0, hz, L + v.o(22))
    v.dim_v(BOX_H - hz, BOX_H, L + v.o(22))
    v.dim_v(0, BOX_H, L + v.o(50))
    v.dim_h(0, L, v.top_y())
    v.edge("bottom", "bottom edge")
    v.edge("left", "end: sits in the side's rabbet")
    S = Face(solid, "-y", "+z", win=(0, T18, 0, 45))
    s = View(S.w, S.h, "B  section, bottom edge\n(inside face at right)", size="small")
    s.notch(*S.rect(gf))
    s.dim_h(T18 - RABBET_D, T18, -8, dt(RABBET_D))
    s.dim_v(UM_RECESS, UM_RECESS + T12, -8, P12)
    s.edge("right", "inside face")
    sheet(name, head(name, f"3/4 maple ply, {dt(BOX_H)} tall x {dt(L)} long (box front, behind the walnut front)"), [v, s],
          "Both ends sit in the sides' end rabbets. The holes are not in the model: drill them after the groove. "
          "Datums: the blank's own ends and bottom edge.")
    pr = cut_probes(*gf, "+y")
    pr += [wood(*gf, "-z"), wood(*gf, "+z"), runout(*gf, "-x"), runout(*gf, "+x")]
    return check(name, solid, pr)


def drawer_back():
    name = "drawer_back"
    solid = part(name)
    x0 = _box_x0()
    ex0 = x0 + T12 - RABBET_D
    L = END_LEN
    check_blank(name, ex0, BOX_Y0, BOX_Z0, L, T18, BOX_H)
    nw, nh = UM_HOOK_NOTCH_W + RABBET_D, UM_HOOK_NOTCH_H
    dia, depth, off, up = UM_HOOK_BORE
    notches = [(ex0, BOX_Y0, BOX_Z0, nw, T18, nh), (ex0 + L - nw, BOX_Y0, BOX_Z0, nw, T18, nh)]
    bxs = [x0 + T12 + off, x0 + BOX_W - T12 - off]          # from each side's inner face
    gk = (ex0, BOX_Y0 + T18 - DRAWER_BACK_GROOVE_D, BOX_Z0 + UM_RECESS, L, DRAWER_BACK_GROOVE_D, T12)

    P = Face(solid, "+x", "+z")            # REAR face, standing behind the drawer
    v = View(L, BOX_H, "A  REAR (outside) face, seen from behind the drawer; bottom edge down")
    for n in notches:
        v.notch(*P.rect(n))
    bu = []
    for bx in bxs:
        u, w = P.pt(bx, BOX_Y0, BOX_Z0 + up)
        bu.append(u)
        v.bore(u, w, dia / 2)
    v.hidden(*P.rect(gk))
    v.callout(nw / 2, nh / 2, f"Blum notch, both bottom corners, through: {dt(nw)} from the blank's end x {dt(nh)} tall", ha="left")
    v.callout(bu[1], up, f"Blum hook bore, both ends: {dt(dia)} dia x {dt(depth)} deep into this face", ha="right")
    v.callout(L * 0.5, UM_RECESS + T12 / 2,
              f"dashed: bottom groove on the INSIDE face, through: {P12} tall x {dt(DRAWER_BACK_GROOVE_D)} deep, underside {dt(UM_RECESS)} up")
    v.dim_v(UM_RECESS, UM_RECESS + T12, L + v.o(22), P12)
    v.dim_v(0, BOX_H, L + v.o(50))
    v.dim_h(0, L, v.top_y())
    v.edge("bottom", "bottom edge")

    C = Face(solid, "+x", "+z", win=(0, 70, 0, 45))
    c = View(C.w, C.h, "C  detail, left bottom corner (REAR face)\nright corner is the mirror image", size="small")
    c.notch(*C.rect(notches[0]))
    c.hidden(*C.rect(gk))
    c.bore(bu[0], up, dia / 2)
    c.dim_h(0, nw, -8)
    c.dim_h(0, bu[0], -22)
    c.dim_v(0, nh, -8)
    c.dim_v(0, up, -22)
    c.dim_v(UM_RECESS, UM_RECESS + T12, 70 + 8, P12)
    c.edge("left", "end")

    S = Face(solid, "+y", "+z", win=(0, T18, 0, 45))
    s = View(S.w, S.h, "B  section through a hook bore\n(rear face at left)", size="small")
    s.notch(0, 0, T18, nh)
    s.notch(*S.rect((bxs[0] - dia / 2, BOX_Y0, BOX_Z0 + up - dia / 2, dia, depth, dia)))
    s.notch(*S.rect(gk))
    s.dim_h(0, depth, 45 + 8, dt(depth))
    s.dim_h(depth, T18 - DRAWER_BACK_GROOVE_D, -8, dt(T18 - DRAWER_BACK_GROOVE_D - depth))
    s.dim_v(UM_RECESS, UM_RECESS + T12, T18 + 8, P12)
    s.dim_v(0, nh, -8)
    s.edge("left", "REAR face")

    sheet(name, head(name, f"3/4 maple ply, {dt(BOX_H)} tall x {dt(L)} long (box back)"), [v, c, s],
          f"The bottom groove is only {dt(DRAWER_BACK_GROOVE_D)} deep (not {dt(RABBET_D)}) so about {dt(T18 - DRAWER_BACK_GROOVE_D - depth)} of wood "
          "stays between each hook bore and the groove. Both ends sit in the sides' rabbets. Datums: the blank's own ends and bottom edge.")
    pr = []
    for n, toward in zip(notches, ("+x", "-x")):
        pr.append((_box(n[0] + 1, n[1] + 1, n[2] + 1, n[3] - 2, n[4] - 2, n[5] - 2), "empty"))
        pr.append(wood(n[0], n[1], n[2], n[3], T18 - DRAWER_BACK_GROOVE_D, n[5], "+z"))     # wood above, outside the groove
        pr.append(wood(*n, toward))                                                            # wood beside, toward the middle
        pr += [runout(*n, "-z"), runout(*n, "-x" if toward == "+x" else "+x")]
    for bx in bxs:
        pr += cut_probes(bx - 2, BOX_Y0, BOX_Z0 + up - 2, 4, depth, 4, "+y")
        pr.append(runout(bx - 2, BOX_Y0, BOX_Z0 + up - 2, 4, depth, 4, "-y"))
        pr.append((_box(bx + dia / 2 + 0.5, BOX_Y0 + 1, BOX_Z0 + up - 1, 1, depth - 2, 2), "solid"))
        pr.append((_box(bx + dia / 2 - 1.2, BOX_Y0 + 1, BOX_Z0 + up - 0.5, 0.8, depth - 2, 1), "empty"))
    pr += cut_probes(*gk, "-y")
    mid = (ex0 + nw + 1, gk[1], gk[2], L - 2 * nw - 2, gk[4], gk[5])
    pr += [wood(*mid, "-z"), wood(*mid, "+z"), runout(*gk, "-x"), runout(*gk, "+x")]
    return check(name, solid, pr)


def drawer_bottom():
    name = "drawer_bottom"
    P, v = plain(name, "-x", "-y", "plan view from above; FRONT edge along the bottom",
                 f"plain rectangle; all four edges sit in the box's grooves")
    v.edge("bottom", "FRONT edge")
    sheet(name, head(name, f"1/2 Baltic birch, {dt(P.h)} front to back x {dt(P.w)} wide"), [v],
          f"Sizes already take off {dt(PLAY)} total play each way. The Blum locking devices go under it at the front corners.")
    return 0


if __name__ == "__main__":
    n = 0
    base_rails()
    n += end_panel()
    n += bottom_panel()
    n += partition()
    n += nailer()
    n += back_panel()
    n += scribe_strip()
    n += plinth()
    n += top_slab()
    n += front_stile()
    n += front_rail()
    n += front_panel()
    n += drawer_side()
    n += drawer_front()
    n += drawer_back()
    drawer_bottom()
    names = sorted(os.path.splitext(os.path.basename(p))[0] for p in WRITTEN)
    assert names == sorted(p["name"] for p in PARTS), ("not one sheet per part", names)
    for p in WRITTEN:
        print("wrote", os.path.relpath(p, VAULT))
    print(f"{len(WRITTEN)} sheets; {n} probes against the solids: OK")
