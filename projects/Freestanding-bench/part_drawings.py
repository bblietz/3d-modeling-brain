#!/usr/bin/env python
"""Shop drawings for every cut-list part of the freestanding alcove bench (post and panel, Brian's pick A 2026-10-26).

Same machinery as projects/Built-in-bench/part_drawings.py. Every cut is
written once as a world box from the constants in freestanding_bench.py; that
box is probed against the real solid (a box 1 mm inside the cut must be
air, a 1 mm slab just past its floor must be wood, plus wall and run-out
probes where they apply) and the same box is projected onto the view, so a
drawing cannot show a cut the model does not have, or in another place.

Views are true projections of the blank: each names the world axis that
runs to the right and the one that runs up, and the blank's own bounding
box sets the zero, so every dimension reads from that part's edges.

Inches only, to the nearest 1/32 (Brian 2026-09-28). A width sized to a
sheet's thickness reads "3/4 ply (measure)" and is cut to the measured sheet.

Usage: .venv/bin/python projects/Freestanding-bench/part_drawings.py
Writes projects/Freestanding-bench/images/parts/<part>.png: the four corner posts, the housed ends and back,
the notched case bottom, the partition and cleat, the top, the fronts and the drawer boxes.
"""
import math
import os
import sys

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Freestanding-bench"
sys.path.insert(0, PROJ)
sys.path.insert(0, f"{VAULT}/scripts")
from freestanding_bench import *   # noqa: F401,F403  constants, solids and build123d names; runs the model's checks once
from freestanding_bench import _box, part, vol, inch, PARTS  # noqa: E402

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


P18, P12, P12M = "3/4 ply (measure)", "1/2 BB (measure)", "1/2 ply (measure)"
PW12 = "1/2 MDF or paint-grade ply (measure)"
UM_SCREW_Z = (25.0, 37.0)   # Blum 563H runner front screw holes above the opening bottom (the drawer bench's values from the Blum sheet); not in the model


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


def _post_plan(P):
    """plan outline of a post seen from its top end: the square less the four chamfers"""
    c, w, h = CHAMFER, P.w, P.h
    return sg.Polygon([(c, 0), (w - c, 0), (w, c), (w, h - c), (w - c, h), (c, h), (0, h - c), (0, c)])


def _chamfer_probes(x, y, z0, z1):
    """all four chamfers between z0 and z1: a 2 mm box hugging each corner edge is air, a 1 mm box just past the
    chamfer face is wood (and clear of every groove: the grooves start SETBACK in, past CHAMFER)"""
    pr = []
    for cx, sx in ((x, 1), (x + POST, -1)):
        for cy, sy in ((y, 1), (y + POST, -1)):
            pr.append((_box(cx if sx > 0 else cx - 2, cy if sy > 0 else cy - 2, z0 + 1, 2, 2, z1 - z0 - 2), "empty"))
            d = CHAMFER + 1.5
            pr.append((_box(cx + d if sx > 0 else cx - d - 1, cy + 0.5 if sy > 0 else cy - 1.5, z0 + 1, 1, 1, z1 - z0 - 2), "solid"))
    return pr


def _groove_probes(g, floor, walls):
    """a stopped post groove running out the top: air inside, wood past its floor, wood on both walls, wood below
    its stopped end, air past the top end"""
    pr = cut_probes(*g, floor)
    pr += [wood(*g, w) for w in walls]
    pr.append(wood(*g, "-z"))
    pr.append(runout(*g, "+z"))
    return pr


def post_front():
    name = "post_front"
    solid = part(name)
    x, y, H = X0, YF0, TOP_Z0
    check_blank(name, x, y, 0, POST, POST, H)
    g = (x + SETBACK, y, GROOVE_STOP, T18, GROOVE_D, H - GROOVE_STOP)        # end-panel groove in the REAR face
    holes = [(YF1 - RUNNER_SETBACK - dy, BOT_Z1 + dz) for dy, dz in zip(UM_SCREW_Y, UM_SCREW_Z)]

    P = Face(solid, "+z", "-y")            # the INNER face, lying down: bottom end left, top end right, FRONT face along the bottom
    a = View(H, POST, "A  INNER face (toward the drawers), lying down: bottom end at left, top end at right, FRONT face along the bottom")
    for vv in (CHAMFER, POST - CHAMFER):
        a.mark(0, vv, H, vv)
    hs = [P.pt(x + POST, hy, hz) for hy, hz in holes]
    for u, vv in hs:
        a.bore(u, vv, 1.6, hidden=True)
    a.callout(hs[1][0], hs[1][1], "dashed: the Blum runner's two front screw holes, #6 x 5/8, not in the model (see the note)", ha="center")
    a.callout(H * 0.25, CHAMFER, f"dashed lines: the {dt(CHAMFER)} chamfers, all four vertical edges, full length", ha="left")
    a.dim_h(0, hs[0][0], -a.o(20))
    a.dim_h(0, hs[1][0], -a.o(44))
    a.dim_v(0, hs[0][1], H + a.o(22))
    a.dim_v(0, hs[1][1], H + a.o(46))
    a.dim_v(0, POST, H + a.o(72))
    a.dim_h(0, H, a.top_y())
    a.edge("left", "bottom end (on the floor)")
    a.edge("right", "top end (under the top)")
    a.edge("bottom", "FRONT face")
    a.edge("top", "REAR face (grooved for the end panel)", at=0.85)

    R = Face(solid, "+z", "-x")            # the REAR face (toward the rear post), lying down: outer face along the top
    b = View(H, POST, "B  REAR face (toward the rear post), lying down: bottom end at left, top end at right, OUTER face along the top")
    b.groove(*R.rect(g))
    for vv in (CHAMFER, POST - CHAMFER):
        b.mark(0, vv, H, vv)
    gu, gv, gw, gh = R.rect(g)
    b.callout(gu + 55, gv + gh / 2, f"end-panel groove, stopped: {P18} x {dt(GROOVE_D)} deep, {dt(SETBACK)} from the OUTER face, out the top end",
              ha="center")
    b.dim_h(0, gu, -b.o(20))
    b.dim_v(gv + gh, POST, H + b.o(22))
    b.dim_v(gv, gv + gh, H + b.o(46), P18)
    b.dim_v(0, POST, H + b.o(72))
    b.dim_h(0, H, b.top_y())
    b.edge("left", "bottom end")
    b.edge("top", "OUTER face (toward the wall)", at=0.85)
    b.edge("bottom", "INNER face")

    T = Face(solid, "-x", "-y")            # top end from above: front face along the bottom, outer face at the right
    c = View(POST, POST, "C  top end from above\n(FRONT face along the bottom, OUTER face at right)", shape=_post_plan(T), size="small")
    c.notch(*T.rect(g))
    tu, tv, tw, th = T.rect(g)
    c.dim_h(0, CHAMFER, -8, dt(CHAMFER))
    c.dim_h(tu + tw, POST, -8, dt(SETBACK))
    c.dim_h(tu, tu + tw, -20, P18)
    c.dim_v(tv, tv + th, POST + 8, dt(GROOVE_D))
    c.edge("bottom", "FRONT face")
    c.edge("right", "OUTER face")

    sheet(name, head(name, f"soft maple {dt(POST)} x {dt(POST)} x {dt(H)} long (12/4, or 8/4 plus 4/4 glued up); left and right are mirror images"),
          [a, b, c], "Drawn: the post at the right-hand end as you face the bench; the other front post is its mirror image (groove and holes "
                     "on the opposite faces). Chamfer first, then rout the stopped groove: its end hides behind the end panel's un-housed "
                     f"bottom, so it needs no squaring. Runner holes (Blum 563H sheet, drilled with the runner in hand): {dt(RUNNER_SETBACK + UM_SCREW_Y[0])} "
                     f"and {dt(RUNNER_SETBACK + UM_SCREW_Y[1])} behind the FRONT face, {dt(UM_SCREW_Z[0])} and {dt(UM_SCREW_Z[1])} above the case "
                     f"bottom's top face ({dt(BOT_Z1)} up). Bare under Osmo like the top.", stack=True)
    pr = _chamfer_probes(x, y, 0, H) + _groove_probes(g, "+y", ("-x", "+x"))
    return check(name, solid, pr)


def post_rear():
    name = "post_rear"
    solid = part(name)
    assert BASEBOARD_NOTCH, "the sheet draws the baseboard notch; run without BASEBOARD_NOTCH=0"
    x, y, H = X0, YB0, TOP_Z0
    check_blank(name, x, y, 0, POST, POST, H)
    ge = (x + SETBACK, y + POST - GROOVE_D, GROOVE_STOP, T18, GROOVE_D, H - GROOVE_STOP)   # end-panel groove in the FRONT face
    gb = (x + POST - GROOVE_D, y + SETBACK, GROOVE_STOP, GROOVE_D, T12, H - GROOVE_STOP)   # back groove in the INNER face
    nt = (x, y, 0, POST, BB_NOTCH_D, BB_NOTCH_H)                                            # baseboard notch across the REAR face

    P = Face(solid, "+z", "-y")            # the INNER face, lying down: front face along the bottom, rear face along the top
    a = View(H, POST, "A  INNER face (toward the drawers), lying down: bottom end at left, top end at right, FRONT face along the bottom")
    a.notch(*P.rect(nt))
    a.groove(*P.rect(gb))
    a.mark(0, CHAMFER, H, CHAMFER)
    a.mark(BB_NOTCH_H, POST - CHAMFER, H, POST - CHAMFER)
    gu, gv, gw, gh = P.rect(gb)
    nu, nv, nw, nh = P.rect(nt)
    a.callout(gu + 55, gv + gh / 2, f"back groove, stopped: {P12M} x {dt(GROOVE_D)} deep, {dt(SETBACK)} from the REAR face, out the top end",
              ha="center")
    a.callout(nw * 0.5, nv + nh / 2, f"baseboard notch across the REAR face: {dt(BB_NOTCH_D)} deep x {dt(BB_NOTCH_H)} tall (skip it if the "
              "baseboard comes out)", ha="left")
    a.dim_h(0, nw, -a.o(20))
    a.dim_h(0, gu, -a.o(44))
    a.dim_v(nv, POST, -a.o(22))
    a.dim_v(gv + gh, POST, H + a.o(22))
    a.dim_v(gv, gv + gh, H + a.o(46), P12M)
    a.dim_v(0, POST, H + a.o(72))
    a.dim_h(0, H, a.top_y())
    a.edge("left", "bottom end (on the floor)")
    a.edge("right", "top end (under the top)")
    a.edge("bottom", "FRONT face (grooved for the end panel)")
    a.edge("top", "REAR face (toward the wall)", at=0.85)

    F = Face(solid, "+z", "+x")            # the FRONT face (toward the front post), lying down: outer face along the bottom
    b = View(H, POST, "B  FRONT face (toward the front post), lying down: bottom end at left, top end at right, OUTER face along the bottom")
    b.groove(*F.rect(ge))
    for vv in (CHAMFER, POST - CHAMFER):
        b.mark(0, vv, H, vv)
    eu, ev, ew, eh = F.rect(ge)
    b.callout(eu + 55, ev + eh / 2, f"end-panel groove, stopped: {P18} x {dt(GROOVE_D)} deep, {dt(SETBACK)} from the OUTER face, out the top end",
              ha="center")
    b.dim_h(0, eu, -b.o(20))
    b.dim_v(0, ev, H + b.o(22))
    b.dim_v(ev, ev + eh, H + b.o(46), P18)
    b.dim_v(0, POST, H + b.o(72))
    b.dim_h(0, H, b.top_y())
    b.edge("left", "bottom end")
    b.edge("bottom", "OUTER face (toward the wall)")
    b.edge("top", "INNER face", at=0.85)

    T = Face(solid, "-x", "-y")            # top end from above: front face along the bottom, outer face at the right
    c = View(POST, POST, "C  top end from above\n(FRONT face along the bottom, OUTER face at right)", shape=_post_plan(T), size="small")
    c.notch(*T.rect(ge))
    c.notch(*T.rect(gb))
    tu, tv, tw, th = T.rect(ge)
    bu, bv, bw, bh = T.rect(gb)
    c.dim_h(0, CHAMFER, -8, dt(CHAMFER))
    c.dim_h(tu + tw, POST, -8, dt(SETBACK))
    c.dim_h(tu, tu + tw, -20, P18)
    c.dim_v(tv, tv + th, POST + 8, dt(GROOVE_D))
    c.dim_v(bv + bh, POST, -8, dt(SETBACK))
    c.dim_v(bv, bv + bh, -20, P12M)
    c.edge("bottom", "FRONT face")
    c.edge("right", "OUTER face")
    c.edge("left", "INNER face")

    sheet(name, head(name, f"soft maple {dt(POST)} x {dt(POST)} x {dt(H)} long; same blank and chamfer as post_front; left and right are mirror images"),
          [a, b, c], "Drawn: the post at the right-hand end as you face the bench; the other rear post is its mirror image. Chamfer first, "
                     "then rout the two stopped grooves; their ends hide behind the panels' un-housed bottoms and stay as the bit leaves them. "
                     "The back groove is sized to the 1/2 maple ply, the end groove to the 3/4. The baseboard notch runs across the full rear "
                     f"face at the floor; the bench stands {dt(WALL_GAP)} off the back wall with the notch over the baseboard and shoe. "
                     "Bare under Osmo.", stack=True)
    pr = _chamfer_probes(x, y, BB_NOTCH_H, H)
    pr += _groove_probes(ge, "-y", ("-x", "+x")) + _groove_probes(gb, "-x", ("-y", "+y"))
    pr.append((_box(x + 1, y + 1, 1, POST - 2, BB_NOTCH_D - 2, BB_NOTCH_H - 2), "empty"))
    pr.append(wood(*nt, "+y"))
    pr.append((_box(x + CHAMFER + 1, y + 1, BB_NOTCH_H + 0.5, POST - 2 * CHAMFER - 2, BB_NOTCH_D - 2, 1), "solid"))   # wood above, clear of the chamfers
    pr += [runout(*nt, "-x"), runout(*nt, "+x"), runout(*nt, "-z"), runout(*nt, "-y")]
    return check(name, solid, pr)


def end_panel():
    name = "end"
    solid = part(name)
    H = TOP_Z0 - PANEL_Z0
    L = END_Y1 - END_Y0
    check_blank(name, END_X0, END_Y0, PANEL_Z0, T18, L, H)
    rab = (END_IN_L - RABBET_D, END_Y0, PANEL_Z0, RABBET_D, L, T18)
    notches = [(END_X0, END_Y0, PANEL_Z0, T18, GROOVE_D, NOTCH_H), (END_X0, END_Y1 - GROOVE_D, PANEL_Z0, T18, GROOVE_D, NOTCH_H)]
    tz = TONGUE_Z0 - PANEL_Z0

    P = Face(solid, "+y", "+z")            # looking at the inside face: rear edge left, front edge right
    v = View(L, H, "A  INSIDE face (toward the drawers); REAR edge at left, FRONT edge at right, bottom edge down")
    for n in notches:
        v.notch(*P.rect(n))
    ru = P.rect(rab)
    v.cutshape(sg.box(ru[0], ru[1], ru[0] + ru[2], ru[1] + ru[3]))
    v.callout(L * 0.6, T18 / 2, f"rabbet along the bottom edge, through (it runs out through the notches): {P18} tall x {dt(RABBET_D)} deep; the case bottom sits in it")
    v.callout(GROOVE_D / 2, NOTCH_H / 2, f"both bottom corners notched {dt(GROOVE_D)} x {dt(NOTCH_H)}: above the notch the end is housed {dt(GROOVE_D)} "
              "in the post, below it the un-housed bottom butts the post face", ha="left")
    v.dim_h(0, GROOVE_D, -v.o(20))
    v.dim_v(0, NOTCH_H, -v.o(22))
    v.dim_v(0, T18, L + v.o(26), P18)
    v.dim_v(0, H, L + v.o(60))
    v.dim_h(0, L, v.top_y())
    v.edge("left", "REAR edge (in the rear post)")
    v.edge("right", "FRONT edge (in the front post)")

    S = Face(solid, "-x", "+z", win=(0, T18, 0, 50))       # the bottom edge, seen from the front: inside face at left
    a = View(S.w, S.h, "B  section near the bottom edge\n(inside face at left)", size="small")
    a.notch(*S.rect(rab))
    a.dim_h(0, RABBET_D, -8, dt(RABBET_D))
    a.dim_v(0, T18, T18 + 10, P18)
    a.edge("left", "inside face")
    a.edge("bottom", "bottom edge")

    N = Face(solid, "+y", "+z", win=(0, 70, 0, 60))        # the rear bottom corner of the inside face
    c = View(N.w, N.h, "C  rear bottom corner, inside face\n(the front corner is the same)", size="small")
    c.notch(*N.rect(notches[0]))
    ru = N.rect(rab)
    c.cutshape(sg.box(ru[0], ru[1], ru[0] + ru[2], ru[1] + ru[3]))
    c.mark(0, GROOVE_STOP - PANEL_Z0, GROOVE_D, GROOVE_STOP - PANEL_Z0)
    c.dim_h(0, GROOVE_D, -8, dt(GROOVE_D))
    c.dim_v(0, NOTCH_H, -8)
    c.dim_v(0, T18, 70 + 8, P18)
    c.dim_v(GROOVE_STOP - PANEL_Z0, tz, 70 + 22, dt(GROOVE_CLR))
    c.edge("left", "REAR edge")

    sheet(name, head(name, f"3/4 maple ply, {dt(H)} tall x {dt(L)} long, face grain vertical, show face OUT; mirror pair (the other end is the mirror image)"),
          [v, a, c], f"Housed {dt(GROOVE_D)} in each post with its outer face {dt(SETBACK)} behind the post faces and its top edge flush with the post "
                     f"tops; the post grooves end {dt(GROOVE_CLR)} below the notch tops (dashed in C), behind the un-housed bottom, so nothing is "
                     "squared. Datums: the rear edge and the bottom edge. Cut the rabbet on the INSIDE face; the two ends come out as a left and a "
                     "right. Iron-on maple band on the BOTTOM edge (the front and rear edges sit inside the posts), then paint white.")
    pr = []
    for n, inward in zip(notches, ("+y", "-y")):
        pr.append((_box(n[0] + 1, n[1] + 1, n[2] + 1, n[3] - 2, n[4] - 2, n[5] - 2), "empty"))
        pr.append(wood(*n, "+z"))                                                                       # wood above the notch
        ny = n[1] + GROOVE_D + 0.5 if inward == "+y" else n[1] - 1.5
        pr.append((_box(END_X0 + 1, ny, PANEL_Z0 + T18 + 1, T18 - 2, 1, NOTCH_H - T18 - 2), "solid"))    # wood beside it, above the rabbet
        pr += [runout(*n, "-x"), runout(*n, "+x"), runout(*n, "-z"), runout(*n, "-y" if inward == "+y" else "+y")]
        pr.append((_box(END_X0 + 1, n[1] + 1, TONGUE_Z0 + 1, T18 - 2, GROOVE_D - 2, 20), "solid"))        # the housed tongue above
    mid = (rab[0], END_Y0 + GROOVE_D + 1, rab[2], rab[3], L - 2 * GROOVE_D - 2, rab[5])
    pr += cut_probes(*mid, "-x")
    pr += [wood(*mid, "+z"), runout(*rab, "-y"), runout(*rab, "+y")]
    return check(name, solid, pr)


def bottom_panel():
    name = "bottom"
    solid = part(name)
    W = BOT_X1 - BOT_X0
    D = CASE_D - BOT_Y0
    check_blank(name, BOT_X0, BOT_Y0, BOT_Z0, W, D, T18)
    assert abs((BOT_X0 + BOT_X1) / 2 - XC) < 1e-9
    across = POST_IN_L - BOT_X0
    fd, rd = CASE_D - YF0, YB0 + POST - BOT_Y0
    notches = [(BOT_X0, YF0, BOT_Z0, across, fd, T18), (BOT_X0, BOT_Y0, BOT_Z0, across, rd, T18),
               (POST_IN_R, YF0, BOT_Z0, across, fd, T18), (POST_IN_R, BOT_Y0, BOT_Z0, across, rd, T18)]
    dado = (PART_X0, BACK_Y1, BOT_Z1 - DADO_D, T18, CASE_D - BACK_Y1, DADO_D)

    P = Face(solid, "-x", "-y")            # plan from above, FRONT edge toward the viewer (down the page)
    v = View(W, D, "A  TOP face, seen from above; FRONT edge along the bottom, REAR edge along the top")
    for n in notches:
        v.notch(*P.rect(n))
    v.groove(*P.rect(dado))
    du, dv, _, dh = P.rect(dado)
    v.callout(W - across / 2, fd / 2, f"all four corners notched around the posts: {dt(across)} across x {dt(fd)} at the FRONT corners, "
                                      f"{dt(rd)} at the REAR corners", ha="right")
    v.callout(du + T18 / 2, D * 0.45, f"partition dado, centered on the length: {P18} wide x {dt(DADO_D)} deep; "
                                      f"from the FRONT edge back to {dt(RABBET_D)} short of the REAR edge (the strip that sits in the back's rabbet)")
    v.dim_h(W - across, W, -v.o(22))
    v.dim_v(0, fd, W + v.o(26))
    v.dim_v(D - rd, D, W + v.o(26))
    v.dim_h(0, du, -v.o(22))
    v.dim_h(du, du + T18, -v.o(46), P18)
    v.dim_v(dv, dv + dh, -v.o(22))
    v.dim_v(0, D, W + v.o(50))
    v.dim_h(0, W, v.top_y())
    v.edge("bottom", "FRONT edge (hidden behind the drawer fronts)", at=0.22)
    v.edge("top", f"REAR edge: sits {dt(RABBET_D)} in the back's rabbet")
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

    sheet(name, head(name, f"3/4 maple ply, {dt(D)} deep x {dt(W)} long, face grain along the length"), [v, a],
          f"Both ends sit in the end panels' {dt(RABBET_D)} rabbets and the rear edge in the back's; the corner notches clear the posts "
          "(the rear ones also take in the strip in the back's rabbet). Datums: the FRONT edge and the left end. "
          "The dado is centered: mark it from the middle of the blank.")
    pr = cut_probes(*dado, "-z")
    pr += [wood(*dado, "-x"), wood(*dado, "+x"), runout(*dado, "+y")]
    pr.append((_box(PART_X0 + 1, BOT_Y0 + 1, dado[2] + 1, T18 - 2, RABBET_D - 2, DADO_D - 2), "solid"))   # stops short of the rear edge
    for n in notches:
        pr.append((_box(n[0] + 1, n[1] + 1, n[2] + 1, n[3] - 2, n[4] - 2, n[5] - 2), "empty"))
        inx = "+x" if n[0] < XC else "-x"
        iny = "-y" if n[1] > CASE_D / 2 else "+y"
        pr += [wood(*n, inx), wood(*n, iny)]
        pr += [runout(*n, "-x" if inx == "+x" else "+x"), runout(*n, "+y" if iny == "-y" else "-y"), runout(*n, "-z"), runout(*n, "+z")]
    return check(name, solid, pr)


def partition():
    name = "partition"
    solid = part(name)
    L, H = CASE_D - BACK_Y1, TOP_Z0 - PART_Z0
    check_blank(name, PART_X0, BACK_Y1, PART_Z0, T18, L, H)
    nt = (PART_X0, BACK_Y1, CLEAT_Z0, T18, TS, CLEAT_H)
    P = Face(solid, "+y", "+z")
    v = View(L, H, "side face (both faces are the same); REAR edge at left, FRONT edge at right")
    v.notch(*P.rect(nt))
    v.callout(TS / 2, H - CLEAT_H / 2, f"notch the top REAR corner, through: {dt(TS)} deep x {dt(CLEAT_H)} tall; the cleat passes through it", row=1)
    v.dim_h(0, TS, H + v.row_mm * 0.45)
    v.dim_v(H - CLEAT_H, H, -v.o(22))
    v.dim_v(0, H, L + v.o(26))
    v.dim_h(0, L, v.top_y())
    v.edge("left", "REAR edge (against the back)")
    v.edge("right", "FRONT edge (on the fronts' back faces: the runners mount to it)")
    v.edge("bottom", "bottom edge (in the dado)")
    sheet(name, head(name, f"3/4 maple ply, {dt(H)} tall x {dt(L)} deep, face grain vertical"), [v],
          f"The bottom edge sits {dt(DADO_D)} deep in the bottom panel's dado; the rear edge stops against the back panel. The partition-side "
          "Blum runners mount to its faces the frameless way, fronts 3/32 behind its front edge. Datums: the REAR edge and the top edge.")
    pr = cut_probes(*nt, "+y")
    pr += [wood(*nt, "-z"), runout(*nt, "-y"), runout(*nt, "+z")]
    return check(name, solid, pr)


def cleat():
    name = "cleat"
    solid = part(name)
    L = POST_IN_R - POST_IN_L
    check_blank(name, POST_IN_L, CLEAT_Y0, CLEAT_Z0, L, TS, CLEAT_H)
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
    f = View(L, CLEAT_H, "B  FRONT face (toward the drawers); top edge up")
    for xc in FIG8_XS:
        u, _ = F.pt(xc, 0, 0)
        f.groove(u - chord, CLEAT_H - FIG8_DEPTH, 2 * chord, FIG8_DEPTH)
    f.callout(sorted(F.pt(x, 0, 0)[0] for x in FIG8_XS)[2], CLEAT_H - FIG8_DEPTH / 2,
              f"each recess shows here as a {dt(2 * chord)} wide opening in the top edge")
    f.callout(L * 0.1, CLEAT_H * 0.4, "both ends butt the rear posts' inner faces", ha="left")
    f.callout(L * 0.5, CLEAT_H * 0.6, "glued to the back and screwed from this face: #8 x 1 countersunk, nothing through the back", ha="center")
    f.dim_v(0, CLEAT_H, L + f.o(26))
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

    sheet(name, head(name, f"soft maple {dt(TS)} thick, {dt(CLEAT_H)} tall x {dt(L)} long, on edge at the top back between the rear posts"),
          [t, f, d], "Recess positions are from the left end of view A (the layout is symmetric, so either end works). "
                     "The recess must open through the FRONT face so the figure-8 swings out under the top. It passes through the "
                     "partition's notch.", stack=True)
    pr = []
    for xc in FIG8_XS:
        pr += cut_probes(xc - 3, FIG8_Y - 3, TOP_Z0 - FIG8_DEPTH, 6, 6, FIG8_DEPTH, "-z")
        pr.append((_box(xc - chord + 1, CLEAT_Y1 - 1, TOP_Z0 - FIG8_DEPTH + 0.5, 2 * chord - 2, 3, FIG8_DEPTH), "empty"))   # opens through
        pr.append((_box(xc - 2, CLEAT_Y0 + 0.5, TOP_Z0 - FIG8_DEPTH + 0.5, 4, 1, FIG8_DEPTH - 1), "solid"))               # rear wall
        pr.append((_box(xc + r + 0.5, FIG8_Y - 1, TOP_Z0 - FIG8_DEPTH + 0.5, 1, 2, FIG8_DEPTH - 1), "solid"))              # not wider
        pr.append((_box(xc + r - 1.5, FIG8_Y - 1, TOP_Z0 - FIG8_DEPTH + 0.5, 1, 2, FIG8_DEPTH), "empty"))                 # full dia
    return check(name, solid, pr)


def back_panel():
    name = "back"
    solid = part(name)
    H = TOP_Z0 - PANEL_Z0
    L = BACK_X1 - BACK_X0
    check_blank(name, BACK_X0, BACK_Y0, PANEL_Z0, L, T12, H)
    rab = (BACK_X0, BACK_Y1 - RABBET_D, PANEL_Z0, L, RABBET_D, T18)
    notches = [(BACK_X0, BACK_Y0, PANEL_Z0, GROOVE_D, T12, NOTCH_H), (BACK_X1 - GROOVE_D, BACK_Y0, PANEL_Z0, GROOVE_D, T12, NOTCH_H)]
    brackets = [(POST_IN_L, BACK_Y1 - 1, BOT_Z1, 37.0, 1, 45.0), (POST_IN_R - 37.0, BACK_Y1 - 1, BOT_Z1, 37.0, 1, 45.0)]

    P = Face(solid, "-x", "+z")            # the inside face, seen from the room: the low-X end (your right) at the right
    v = View(L, H, "A  INSIDE face (toward the drawers), seen from the room; bottom edge down")
    for n in notches:
        v.notch(*P.rect(n))
    ru = P.rect(rab)
    v.cutshape(sg.box(ru[0], ru[1], ru[0] + ru[2], ru[1] + ru[3]))
    for b in brackets:
        v.hidden(*P.rect(b))
    bu = P.rect(brackets[0])
    v.callout(L * 0.4, T18 / 2, f"rabbet along the bottom edge, through (it runs out through the notches): {P18} tall x {dt(RABBET_D)} deep; the case bottom sits in it")
    v.callout(GROOVE_D / 2, NOTCH_H / 2, f"both bottom corners notched {dt(GROOVE_D)} x {dt(NOTCH_H)}: housed {dt(GROOVE_D)} in the rear posts "
              "above the notch, the un-housed bottom butts their inner faces", ha="left")
    v.callout(bu[0] + bu[2] / 2, bu[1] + bu[3] / 2, "dashed: Blum rear bracket 295.3750.02 for each post-side runner, set from the runner (see the note)",
              ha="right")
    v.dim_h(0, GROOVE_D, -v.o(20))
    v.dim_v(0, NOTCH_H, -v.o(22))
    v.dim_v(0, T18, L + v.o(26), P18)
    v.dim_v(0, H, L + v.o(60))
    v.dim_h(0, L, v.top_y())
    v.edge("bottom", "bottom edge")
    v.edge("left", "end (in a rear post)")
    v.edge("right", "end (in a rear post)")

    S = Face(solid, "+y", "+z", win=(0, T12, 0, 50))       # the bottom edge seen from an end: inside face at right
    a = View(S.w, S.h, "B  section near the bottom edge\n(inside face at right)", size="small")
    a.notch(*S.rect(rab))
    a.dim_h(T12 - RABBET_D, T12, -8, dt(RABBET_D))
    a.dim_v(0, T18, T12 + 10, P18)
    a.dim_h(0, T12, 50 + 8, P12M)
    a.edge("right", "inside face")
    a.edge("bottom", "bottom edge")

    N = Face(solid, "-x", "+z", win=(0, 70, 0, 60))
    c = View(N.w, N.h, "C  bottom corner, inside face\n(the other end is the same)", size="small")
    c.notch(*N.rect(notches[1]))
    ru = N.rect(rab)
    c.cutshape(sg.box(ru[0], ru[1], ru[0] + ru[2], ru[1] + ru[3]))
    c.mark(0, GROOVE_STOP - PANEL_Z0, GROOVE_D, GROOVE_STOP - PANEL_Z0)
    c.dim_h(0, GROOVE_D, -8, dt(GROOVE_D))
    c.dim_v(0, NOTCH_H, -8)
    c.dim_v(0, T18, 70 + 8, P18)
    c.dim_v(GROOVE_STOP - PANEL_Z0, NOTCH_H, 70 + 22, dt(GROOVE_CLR))
    c.edge("left", "end (in the rear post)")

    sheet(name, head(name, f"1/2 maple ply, {dt(H)} tall x {dt(L)} long, face grain vertical"), [v, a, c],
          f"Housed {dt(GROOVE_D)} in each rear post, outer face {dt(SETBACK)} behind their rear faces, top edge flush with the post tops; "
          f"the post grooves end {dt(GROOVE_CLR)} below the notch tops (dashed in C). Glue it in all round: with no wall screws it is what "
          "keeps the case square. The cleat glues to this face along the top edge between the posts. The two rear brackets go on this face "
          "at the rear of each post-side runner, located from the runner itself (not pre-drilled), #6 x 1/2 so the points stay inside the "
          "1/2 ply. Datums: either end and the bottom edge.")
    pr = []
    for n, inward in zip(notches, ("+x", "-x")):
        pr.append((_box(n[0] + 1, n[1] + 1, n[2] + 1, n[3] - 2, n[4] - 2, n[5] - 2), "empty"))
        pr.append(wood(*n, "+z"))                                                                      # wood above the notch
        nx = n[0] + GROOVE_D + 0.5 if inward == "+x" else n[0] - 1.5
        pr.append((_box(nx, BACK_Y0 + 1, PANEL_Z0 + T18 + 1, 1, T12 - 2, NOTCH_H - T18 - 2), "solid"))   # wood beside it, above the rabbet
        pr += [runout(*n, "-y"), runout(*n, "+y"), runout(*n, "-z"), runout(*n, "-x" if inward == "+x" else "+x")]
        pr.append((_box(n[0] + 1, BACK_Y0 + 1, TONGUE_Z0 + 1, GROOVE_D - 2, T12 - 2, 20), "solid"))       # the housed tongue above
    mid = (BACK_X0 + GROOVE_D + 1, rab[1], rab[2], L - 2 * GROOVE_D - 2, rab[4], rab[5])
    pr += cut_probes(*mid, "-y")
    pr += [wood(*mid, "+z"), runout(*rab, "-x"), runout(*rab, "+x")]
    return check(name, solid, pr)


def top_slab():
    name = "top"
    solid = part(name)
    D = TOP_D
    check_blank(name, TOP_X0, TOP_Y0, TOP_Z0, TOP_W, D, TS)
    P = Face(solid, "-x", "-y")
    v = View(TOP_W, D, "A  plan from above; FRONT edge along the bottom")
    v.mark(0, ROUND, TOP_W, ROUND)
    v.mark(ROUND, 0, ROUND, D)
    v.mark(TOP_W - ROUND, 0, TOP_W - ROUND, D)
    v.callout(TOP_W * 0.8, ROUND, f"{dt(ROUND)} roundover on the FRONT and BOTH END arrises, top and bottom; dashed: where it starts. The REAR arrises stay square")
    v.dim_h(0, TOP_W, v.top_y())
    v.dim_v(0, D, TOP_W + v.o(26))
    v.edge("bottom", "FRONT edge")
    v.edge("top", "REAR edge: square, flush with the rear posts")
    v.edge("left", f"end: overhangs the posts {dt(OVERHANG)}")
    v.edge("right", f"end: overhangs the posts {dt(OVERHANG)}")
    c = sg.box(0, 0, 40, TS)
    for cy in (ROUND, TS - ROUND):
        corner = sg.box(0, 0 if cy < TS / 2 else TS - ROUND, ROUND, ROUND if cy < TS / 2 else TS)
        c = c.difference(corner.difference(sg.Point(ROUND, cy).buffer(ROUND, 64)))
    s = View(40, TS, "B  section at the FRONT edge\n(front at left; both ends the same)", shape=c, size="small")
    s.dim_v(0, TS, 40 + 8)
    s.callout(1, TS - 1, f"{dt(ROUND)} R, top and bottom", ha="left")
    s.edge("left", "FRONT")
    sheet(name, head(name, f"hard maple {dt(TS)} thick, {dt(D)} deep x {dt(TOP_W)} long"), [v, s],
          f"Glue up from 4 or 5 boards, grain along the {dt(TOP_W)} length. Overhangs the posts {dt(OVERHANG)} at each end and at "
          f"the front, flush with their rear faces; {dt(SIDE_AIR)} of air to each wall. Floats: pocket screws up "
          "through the ends and the partition near the front, figure-8s on the cleat at the back.")
    xi, wi = TOP_X0 + ROUND + 0.5, TOP_W - 2 * ROUND - 1                 # the length clear of the end roundovers
    pr = []
    for z in (TOP_Z0, TOP_Z0 + TS - 0.6):                              # the two front arrises are rounded
        pr.append((_box(xi, TOP_Y1 - 0.6, z, wi, 0.6, 0.6), "empty"))
        for x in (TOP_X0, TOP_X1 - 0.6):                               # and both end arrises, top and bottom
            pr.append((_box(x, TOP_Y0 + 1, z, 0.6, D - 2, 0.6), "empty"))
    pr.append((_box(xi, TOP_Y1 - ROUND - 1.5, TOP_Z0 + 1, wi, 1, TS - 2), "solid"))           # behind the front roundover
    pr.append((_box(xi, TOP_Y1 - 0.6, TOP_Z0 + ROUND + 0.5, wi, 0.6, TS - 2 * ROUND - 1), "solid"))   # not bigger
    for x in (TOP_X0, TOP_X1 - 0.6):
        pr.append((_box(x, TOP_Y0 + 1, TOP_Z0 + ROUND + 0.5, 0.6, D - ROUND - 2, TS - 2 * ROUND - 1), "solid"))   # ends not bigger
    pr.append((_box(xi, TOP_Y0, TOP_Z0 + TS - 0.6, wi, 0.6, 0.6), "solid"))                   # rear arris sharp
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
    e.callout(FACE_T / 2, FRONT_H * 0.5, f"groove, through both ends: {dt(TONGUE_T)} wide x {dt(TONGUE_L)} deep", ha="left")
    e.dim_h(E.rect(g)[0] + E.rect(g)[2], FACE_T, -8, dt(FACE_T - PANEL_T))
    e.dim_v(0, FRONT_H, FACE_T + 26)
    e.edge("right", "FRONT face")

    T = Face(solid, "-x", "-y")            # top end from above
    s = View(STILE_W, FACE_T, "C  top end from above\n(front face down, inner edge at left)", size="small")
    gu, gv, gw, gh = T.rect(g)
    s.notch(gu, gv, gw, gh)
    s.dim_h(0, TONGUE_L, FACE_T + 8, dt(TONGUE_L))
    s.dim_v(gv, gv + gh, -8, dt(TONGUE_T))
    s.dim_v(0, gv, -8, dt(FACE_T - PANEL_T))
    s.dim_v(0, FACE_T, STILE_W + 8, P18)
    s.edge("bottom", "FRONT face")

    sheet(name, head(name, f"hard maple, {dt(STILE_W)} x {dt(FRONT_H)}, thickness: {P18}"),
          [f, e, s], "All four the same; mill to the 3/4 maple ply's thickness so the fronts sit flush with the case ends' edges. Set the groove from the 1/2 panel stock: the groove's front wall is the panel's inset, so test-cut on scrap and measure. The rail tenon shows on the top end; Brian is fine with that. Painted white.")
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
    v.callout(L * 0.5, H - TONGUE_L / 2, f"dashed: groove in the inner edge, through both ends: {dt(TONGUE_T)} wide x {dt(TONGUE_L)} deep")
    v.callout(TONGUE_L / 2, H * 0.3, f"stub tenon both ends: {dt(TONGUE_T)} thick x {dt(TONGUE_L)} long (same bit); the groove runs through it")
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
    e.dim_h(0, gu, -8, dt(FACE_T - PANEL_T))
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
    check_blank(name, px0, FACE_Y0, pz0, PW, PANEL_T, PH)
    TL = TONGUE_L
    bands = [(px0, pz0, PW, TL), (px0, pz0 + PH - TL, PW, TL), (px0, pz0, TL, PH), (px0 + PW - TL, pz0, TL, PH)]
    P = Face(solid, "+x", "+z")            # looking at the BACK face
    v = View(PW, PH, "A  BACK face; grain horizontal")
    for bx, bz, bw, bh in bands:
        v.groove(*P.rect((bx, FACE_Y0, bz, bw, GY0 - FACE_Y0, bh)))
    v.callout(PW * 0.5, PH * 0.5, "full-thickness field; the show face is the other side; grain horizontal")
    v.callout(TL / 2, PH * 0.75, f"hatched: rabbet the BACK edges {dt(PANEL_T - TONGUE_T)} deep x {dt(TL)} wide, leaving a {dt(TONGUE_T)} tongue flush with the show face")
    v.dim_h(TL, PW - TL, -v.o(20), f"{dt(PW - 2 * TL)} field")
    v.dim_v(TL, PH - TL, -v.o(22), f"{dt(PH - 2 * TL)} field")
    v.dim_h(0, PW, v.top_y(), f"{dt(PW)} overall, includes tongues")
    v.dim_v(0, PH, PW + v.o(22), f"{dt(PH)} overall")
    v.edge("bottom", "bottom edge")

    S = Face(solid, "-y", "+z", win=(0, PANEL_T, 0, 30))
    s = View(S.w, S.h, "B  section, bottom edge\n(front face at left)", size="small")
    s.notch(*S.rect((px0 + PW / 2, FACE_Y0, pz0, 1, GY0 - FACE_Y0, TL)))
    gu = S.rect((0, GY0, 0, 1, TONGUE_T, 1))[0]
    s.dim_h(gu, gu + TONGUE_T, -8, dt(TONGUE_T))
    s.dim_v(0, TL, PANEL_T + 8, dt(TL))
    s.dim_h(0, PANEL_T, 30 + 8, PW12)
    s.edge("left", "SHOW face")

    sheet(name, head(name, f"1/2 MDF or paint-grade ply, {dt(PH)} x {dt(PW)} including tongues, painted white with the frame"), [v, s],
          "Rabbet the back edges with a straight bit or the bit set's tongue cutter so the tongue stays flush with the show face. "
          "The back goes in flush with the back of the frame. Glue in all round (plywood does not move).")
    pr = []
    for bx, bz, bw, bh in bands:
        pr += cut_probes(bx, FACE_Y0, bz, bw, GY0 - FACE_Y0, bh, "+y")
    fx, fz, fw, fh = px0 + TL, pz0 + TL, PW - 2 * TL, PH - 2 * TL            # field shoulders
    pr += [wood(fx, FACE_Y0, pz0, fw, PANEL_T, TL, "+z"), wood(fx, FACE_Y0, pz0 + PH - TL, fw, PANEL_T, TL, "-z"),
           wood(px0, FACE_Y0, fz, TL, PANEL_T, fh, "+x"), wood(px0 + PW - TL, FACE_Y0, fz, TL, PANEL_T, fh, "-x")]
    return check(name, solid, pr)


def _box_x0():
    return POST_IN_L + OPEN_W / 2 - BOX_W / 2      # left drawer, left side outer face (the bay starts at the post's inner face)


def drawer_side():
    name = "drawer_side"
    solid = part(name)
    x0 = _box_x0()
    check_blank(name, x0, BOX_Y0, BOX_Z0, T12, BOX_D, BOX_H)
    xi = x0 + T12 - RABBET_D
    rf = (xi, BOX_Y1 - T12, BOX_Z0, RABBET_D, T12, BOX_H)
    rb = (xi, BOX_Y0, BOX_Z0, RABBET_D, T12, BOX_H)
    gb = (xi, BOX_Y0, BOX_Z0 + UM_RECESS, RABBET_D, BOX_D, T12)
    P = Face(solid, "+y", "+z")            # inside face: rear end left, FRONT end right
    v = View(BOX_D, BOX_H, "A  INSIDE face (toward the inside of the box); REAR end at left, FRONT end at right")
    for b in (rb, rf, gb):
        v.groove(*P.rect(b))
    v.callout(T12 / 2, BOX_H * 0.7, f"rabbet across both ends: {P12} wide x {dt(RABBET_D)} deep; the box front and back sit in them", ha="left")
    v.callout(BOX_D * 0.5, UM_RECESS + T12 / 2, f"bottom groove, through: {P12} tall x {dt(RABBET_D)} deep, underside {dt(UM_RECESS)} up from the bottom edge")
    v.dim_h(0, T12, -v.o(22), P12)
    v.dim_h(BOX_D - T12, BOX_D, -v.o(22), P12)
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
    pr += [wood(rf[0], rf[1], above, RABBET_D, T12, BOX_Z0 + BOX_H - above, "-y"),
           wood(rb[0], rb[1], above, RABBET_D, T12, BOX_Z0 + BOX_H - above, "+y")]
    pr += [runout(*rf, "-z"), runout(*rf, "+z"), runout(*rb, "-z"), runout(*rb, "+z")]
    pr += cut_probes(*gb, "-x")
    mid = (xi, BOX_Y0 + T12 + 1, gb[2], RABBET_D, BOX_D - 2 * T12 - 2, T12)
    pr += [wood(*mid, "-z"), wood(*mid, "+z"), runout(*gb, "-y"), runout(*gb, "+y")]
    return check(name, solid, pr)


def drawer_front():
    name = "drawer_front"
    solid = part(name)
    ex0 = _box_x0() + T12 - RABBET_D
    L = END_LEN
    check_blank(name, ex0, BOX_Y1 - T12, BOX_Z0, L, T12, BOX_H)
    gf = (ex0, BOX_Y1 - T12, BOX_Z0 + UM_RECESS, L, RABBET_D, T12)
    P = Face(solid, "+x", "+z")            # inside face, looking toward the room
    v = View(L, BOX_H, "A  INSIDE face (toward the inside of the box); bottom edge down")
    v.groove(*P.rect(gf))
    hx, hz = 3 * IN, 2 * IN
    for u in (hx, L - hx):
        for w in (hz, BOX_H - hz):
            v.bore(u, w, 3 / 16 * IN / 2)
    v.callout(L * 0.5, UM_RECESS + T12 / 2, f"bottom groove, runs out both ends: {P12} tall x {dt(RABBET_D)} deep, underside {dt(UM_RECESS)} up from the bottom edge")
    v.callout(hx, BOX_H - hz, "4 oversize holes, 3/16 dia, through, for the #8 x 7/8 screws into the front", ha="left")
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
    S = Face(solid, "-y", "+z", win=(0, T12, 0, 45))
    s = View(S.w, S.h, "B  section, bottom edge\n(inside face at right)", size="small")
    s.notch(*S.rect(gf))
    s.dim_h(T12 - RABBET_D, T12, -8, dt(RABBET_D))
    s.dim_v(UM_RECESS, UM_RECESS + T12, -8, P12)
    s.edge("right", "inside face")
    sheet(name, head(name, f"{P12}, {dt(BOX_H)} tall x {dt(L)} long (box front, behind the front)"), [v, s],
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
    check_blank(name, ex0, BOX_Y0, BOX_Z0, L, T12, BOX_H)
    nw, nh = UM_HOOK_NOTCH_W + RABBET_D, UM_HOOK_NOTCH_H
    dia, depth, off, up = UM_HOOK_BORE
    notches = [(ex0, BOX_Y0, BOX_Z0, nw, T12, nh), (ex0 + L - nw, BOX_Y0, BOX_Z0, nw, T12, nh)]
    bxs = [x0 + T12 + off, x0 + BOX_W - T12 - off]          # from each side's inner face

    P = Face(solid, "+x", "+z")            # REAR face, standing behind the drawer
    v = View(L, BOX_H, "A  REAR (outside) face, seen from behind the drawer; bottom edge down")
    for n in notches:
        v.notch(*P.rect(n))
    bu = []
    for bx in bxs:
        u, w = P.pt(bx, BOX_Y0, BOX_Z0 + up)
        bu.append(u)
        v.bore(u, w, dia / 2)
    v.callout(nw / 2, nh / 2, f"Blum notch, both bottom corners, through: {dt(nw)} from the blank's end x {dt(nh)} tall", ha="left")
    v.callout(bu[1], up, f"Blum hook bore, both ends: {dt(dia)} dia x {dt(depth)} deep into this face", ha="right")
    v.callout(L * 0.5, UM_RECESS + T12 / 2, f"no bottom groove: the bottom butts this part's front (inside) face")
    v.dim_v(0, BOX_H, L + v.o(50))
    v.dim_h(0, L, v.top_y())
    v.edge("bottom", "bottom edge")

    C = Face(solid, "+x", "+z", win=(0, 70, 0, 45))
    c = View(C.w, C.h, "C  detail, left bottom corner (REAR face)\nright corner is the mirror image", size="small")
    c.notch(*C.rect(notches[0]))
    c.bore(bu[0], up, dia / 2)
    c.dim_h(0, nw, -8)
    c.dim_h(0, bu[0], -22)
    c.dim_v(0, nh, -8)
    c.dim_v(0, up, -22)
    c.edge("left", "end")

    S = Face(solid, "+y", "+z", win=(0, T12, 0, 45))
    s = View(S.w, S.h, "B  section through a hook bore\n(rear face at left)", size="small")
    s.notch(0, 0, T12, nh)
    s.notch(*S.rect((bxs[0] - dia / 2, BOX_Y0, BOX_Z0 + up - dia / 2, dia, depth, dia)))
    s.dim_h(0, depth, 45 + 8, dt(depth))
    s.dim_h(depth, T12, -8, dt(T12 - depth))
    s.dim_v(0, nh, -8)
    s.edge("left", "REAR face")

    sheet(name, head(name, f"{P12}, {dt(BOX_H)} tall x {dt(L)} long (box back)"), [v, c, s],
          f"No bottom groove: the bottom butts this part's front face, and each hook bore leaves only a {dt(T12 - depth)} skin of wood behind it, "
          "so test-drill scrap first. Both ends sit in the sides' rabbets. Datums: the blank's own ends and bottom edge.")
    pr = []
    for n, toward in zip(notches, ("+x", "-x")):
        pr.append((_box(n[0] + 1, n[1] + 1, n[2] + 1, n[3] - 2, n[4] - 2, n[5] - 2), "empty"))
        pr.append(wood(*n, "+z"))                                                            # wood above
        pr.append(wood(*n, toward))                                                            # wood beside, toward the middle
        pr += [runout(*n, "-z"), runout(*n, "-x" if toward == "+x" else "+x")]
    for bx in bxs:
        pr += cut_probes(bx - 2, BOX_Y0, BOX_Z0 + up - 2, 4, depth, 4, "+y")
        pr.append(runout(bx - 2, BOX_Y0, BOX_Z0 + up - 2, 4, depth, 4, "-y"))
        pr.append((_box(bx + dia / 2 + 0.5, BOX_Y0 + 1, BOX_Z0 + up - 1, 1, depth - 2, 2), "solid"))
        pr.append((_box(bx + dia / 2 - 1.2, BOX_Y0 + 1, BOX_Z0 + up - 0.5, 0.8, depth - 2, 1), "empty"))
    return check(name, solid, pr)


def drawer_bottom():
    name = "drawer_bottom"
    P, v = plain(name, "-x", "-y", "plan view from above; FRONT edge along the bottom",
                 f"plain rectangle; the rear edge butts the back's front face (glued), the other three edges sit {dt(RABBET_D)} deep in the front and side grooves")
    v.edge("bottom", "FRONT edge")
    sheet(name, head(name, f"1/2 Baltic birch, {dt(P.h)} front to back x {dt(P.w)} wide"), [v],
          f"Sizes already take off {dt(PLAY)} total play each way (the front-to-back size takes half, the rear edge butts the back). The Blum locking devices go under it at the front corners.")
    return 0


if __name__ == "__main__":
    n = 0
    n += post_front()
    n += post_rear()
    n += end_panel()
    n += bottom_panel()
    n += partition()
    n += cleat()
    n += back_panel()
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
