#!/usr/bin/env python
"""Drawer construction diagrams (Brian 2026-11-25: "Draw a detailed construction diagram to show me the
steps of the drawer assembly"), all cut from the model's own solids so they cannot drift from it.

  images/drawer/elevation.png   the drawer front from the room, parts named, hidden tongues and tenons dashed
  images/drawer/section.png     section A-A through the front and the box front, with the top joint enlarged
  images/drawer/machining.png   the three cuts: frame groove, rail stub tenon, panel back rabbet
  images/drawer/step-NN.png     3D steps from the OCP viewer (scripts/cad-viewer.sh must be up), one color per part

Usage: .venv/bin/python projects/Freestanding-bench/drawer_construction.py   (ONLY=2d|3d)
"""
import os
import sys

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
PROJ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJ)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MPoly, Rectangle as MRect  # noqa: E402
from shapely.geometry import LineString  # noqa: E402
from shapely.ops import polygonize, unary_union  # noqa: E402
from freestanding_bench import *  # noqa: E402,F403
from freestanding_bench import INST, HW, inch  # noqa: E402

OUT = f"{PROJ}/images/drawer"
os.makedirs(OUT, exist_ok=True)
D = dict(list(INST) + list(HW))

# one color per part, used in every picture and in the page legend
C = {"rail_lt": "#5b8ec9", "rail_lb": "#6fb36a", "stile_ll": "#e8a44a", "stile_lr": "#e8a44a", "panel_l": "#d9776f",
     "dfront_l": "#9b86c4", "dback_l": "#78b0ad", "dside_ll": "#cdb88f", "dside_lr": "#cdb88f", "dbot_l": "#e3cf7a",
     "pull_l": "#b8903f"}
NAME = {"rail_lt": "top rail", "rail_lb": "bottom rail", "stile_ll": "stile", "stile_lr": "stile", "panel_l": "panel",
        "dfront_l": "box front", "dback_l": "box back", "dside_ll": "box side", "dside_lr": "box side",
        "dbot_l": "box bottom", "pull_l": "pull"}
INK, DIM = "#2b2520", "#7a4a1c"
BG = "#f6f1e9"
FX0 = FRONT_X0[0]
XC = FX0 + FRONT_W / 2


def f(mm):
    return inch(mm)


def section_polys(solid, plane, to2d):
    """the solid cut by a plane, as shapely polygons in the drawing's 2D coordinates"""
    sk = section(solid, section_by=plane)
    lines = []
    for e in sk.edges():
        n = 2 if e.geom_type == GeomType.LINE else 24
        pts = [tuple(round(c, 4) for c in to2d(e.position_at(i / (n - 1)))) for i in range(n)]   # exact nodes
        lines.append(LineString(pts))
    return list(polygonize(unary_union(lines)))


def fill(ax, polys, color, lw=1.2, alpha=1.0, z=2):
    for p in polys:
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=color, ec=INK, lw=lw, alpha=alpha, zorder=z))


def label(ax, xy, text, xytext, ha="left", fs=10):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=INK, ha=ha, va="center", zorder=10,
                arrowprops=dict(arrowstyle="-", color="#6b6259", lw=0.8, shrinkA=2, shrinkB=0),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))


def dim(ax, a, b, text, vertical=False, fs=9):
    ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.9, shrinkA=0, shrinkB=0))
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ax.text(mx, my, text, color=DIM, fontsize=fs, ha="center", va="center", rotation=90 if vertical else 0,
            bbox=dict(boxstyle="round,pad=0.15", fc=BG, ec="none"))


def finish(fig, ax, name):
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    fig.savefig(f"{OUT}/{name}.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("wrote", f"images/drawer/{name}.png")


# ------------------------------------------------------------------ elevation: the front seen from the room
def elevation():
    to2d = lambda v: (v.X - FX0, v.Z - FRONT_Z0)          # noqa: E731
    yc = FACE_Y1 - 0.3                                       # just behind the show face: rails, stiles, panel field
    pl = Plane(origin=(0, yc, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    yt = GY0 + TONGUE_T / 2                                  # the tongue / groove plane
    pt = Plane(origin=(0, yt, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    fig, ax = plt.subplots(figsize=(14, 5.6))
    for n in ("stile_ll", "stile_lr", "rail_lt", "rail_lb"):
        fill(ax, section_polys(D[n], pl, to2d), C[n])
    pf = Plane(origin=(0, FACE_Y0 + 1, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))     # the panel's field sits 1/4 deeper
    fill(ax, [p for p in section_polys(D["panel_l"], pf, to2d)], C["panel_l"], z=1)
    for n in ("panel_l", "rail_lt", "rail_lb"):              # the panel's tongues and the rails' tenons, hidden
        for p in section_polys(D[n], pt, to2d):
            ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fill=False, ec=INK, lw=1.0, ls=(0, (4, 3)), zorder=4))
    W, H = FRONT_W, FRONT_H
    label(ax, (W * 0.90, H - STILE_W / 2), "TOP RAIL (poplar)", (W * 0.88, H + 40))
    label(ax, (W * 0.70, STILE_W / 2), "BOTTOM RAIL (poplar), the same part as the top rail", (W * 0.60, -100))
    label(ax, (STILE_W / 2, H * 0.6), "STILE (poplar)", (-150, H * 0.6), ha="right")
    label(ax, (W - STILE_W / 2, H * 0.6), "STILE", (W + 120, H * 0.6))
    label(ax, (W * 0.45, H * 0.5), "PANEL (1/2 plywood), its face 1/4 in below the frame", (W * 0.25, H * 0.5))
    label(ax, (W * 0.30, H - STILE_W + TONGUE_L / 2), "dashed: the panel's TOP tongue, hidden inside the top rail's groove",
          (W * 0.02, H + 58))
    label(ax, (W * 0.30, STILE_W - TONGUE_L / 2), "dashed: the bottom tongue, inside the bottom rail's groove",
          (W * 0.02, -58))
    label(ax, (STILE_W - TONGUE_L / 2, H - STILE_W / 2), "rail tenon in the stile's groove", (-150, H + 10), ha="right")
    xa = FRONT_X0[0] + FRONT_W / 2 - 80 - FX0                 # section A-A at a pull post
    ax.plot([xa, xa], [-25, H + 25], color="#b03a2e", lw=1.4, ls=(0, (10, 3, 2, 3)), zorder=6)
    for yy, va in ((-30, "top"), (H + 30, "bottom")):
        ax.text(xa, yy, "A", color="#b03a2e", fontsize=13, fontweight="bold", ha="center", va=va, zorder=12)
    dim(ax, (0, H + 95), (W, H + 95), f"{f(W)}")
    dim(ax, (W + 60, 0), (W + 60, H), f"{f(H)}", vertical=True)
    dim(ax, (-60, H - STILE_W), (-60, H), f"{f(STILE_W)}", vertical=True)
    ax.set_xlim(-330, W + 260)
    ax.set_ylim(-125, H + 120)
    ax.set_title("1  The drawer front from the room: a frame of four poplar pieces around a plywood panel",
                 loc="left", fontsize=12, color=INK)
    finish(fig, ax, "elevation")


# ------------------------------------------------------------------ section A-A
def section_view():
    xa = XC - 80                                              # through a pull post
    pl = Plane(origin=(xa, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    to2d = lambda v: (FACE_Y1 - v.Y, v.Z - FRONT_Z0)          # noqa: E731  0 at the show face, the room to the left
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(15, 8.2), gridspec_kw=dict(width_ratios=[1, 1]))
    parts = ("rail_lt", "rail_lb", "panel_l", "dfront_l", "dbot_l", "pull_l")
    for a in (ax, bx):
        for n in parts:
            fill(a, section_polys(D[n], pl, to2d), C[n], lw=1.0 if a is ax else 1.4)
    H = FRONT_H
    yb = FACE_Y1 - (BOX_Y1 - T12)                             # the box front's inside face, from the show face
    # pull screw through the panel and the box front
    pz = FRONT_H / 2
    for a in (ax,):
        a.plot([-PULL_STAND, yb + 3], [pz, pz], color="#555", lw=2.2, zorder=7)
        label(a, (yb - 2, pz), "pull screw through the panel and the box front", (yb + 40, pz - 15))
    # box-front screws as built: 2 in from the box front's top and bottom edges, into the panel field
    for zz in (BOX_Z0 + 2 * IN - FRONT_Z0, BOX_Z0 + BOX_H - 2 * IN - FRONT_Z0):
        x1 = yb + 4
        ax.plot([x1, x1 - 7 / 8 * IN], [zz, zz], color="#1d5fa8", lw=2.4, zorder=7)
    label(ax, (yb - 5, BOX_Z0 + BOX_H - 2 * IN - FRONT_Z0), "#8 x 7/8 from inside the box\n(4 per drawer, into the panel)",
          (yb + 40, H + 25))
    label(ax, (-PULL_STAND - 6, pz), "PULL", (-PULL_STAND - 50, pz + 30), ha="right")
    label(ax, (FACE_T / 2, H - 10), "TOP RAIL", (-60, H + 30), ha="right")
    label(ax, (FACE_T / 2, 12), "BOTTOM RAIL", (-60, -25), ha="right")
    label(ax, (FACE_T - PANEL_T / 2 - 2, H * 0.33), "PANEL", (-60, H * 0.22), ha="right")
    label(ax, (yb - T12 / 2, BOX_H * 0.6 + BOX_Z0 - FRONT_Z0), "BOX FRONT (1/2 Baltic birch)",
          (yb + 40, BOX_H * 0.62 + BOX_Z0 - FRONT_Z0 + 10))
    label(ax, (yb + 60, BOX_Z0 + UM_RECESS + T12 / 2 - FRONT_Z0), "BOX BOTTOM, in the box front's groove",
          (yb + 40, BOX_Z0 - FRONT_Z0 - 30))
    ax.set_xlim(-140, yb + 200)
    ax.set_ylim(-60, H + 60)
    ax.set_title("2  Section A-A, cut top to bottom through a pull post\n(the room to the left, the drawer box to the right)",
                 loc="left", fontsize=12, color=INK)
    ax.add_patch(MRect((-6, H - STILE_W - 12), FACE_T + 12 + 20, STILE_W + 18, fill=False, ec="#b03a2e", lw=1.2,
                           ls="--", zorder=8))
    ax.text(FACE_T + 30, H - STILE_W - 10, "B", color="#b03a2e", fontsize=13, fontweight="bold", va="top")

    # B: the top joint, enlarged
    z0 = H - STILE_W - 11
    bx.set_xlim(-8, FACE_T + 26)
    bx.set_ylim(z0, H + 8)
    gb = FACE_T - PANEL_T                                     # groove front wall
    label(bx, (FACE_T / 2, H - 6), "TOP RAIL", (FACE_T + 4, H + 3))
    label(bx, (gb + TONGUE_T / 2, H - STILE_W + TONGUE_L / 2), "the panel's TOP TONGUE\nfills the rail's groove (glued)",
          (FACE_T + 4, H - STILE_W + TONGUE_L + 6))
    label(bx, (FACE_T - 2, H - STILE_W - 2), "rabbet on the panel's BACK\nmakes the tongue",
          (FACE_T + 4, H - STILE_W - 2))
    label(bx, (gb / 2, H - STILE_W + 2), "groove's front wall", (-7, H - STILE_W - 9.3), ha="left")
    label(bx, (FACE_T + 4, z0 + 3), "box front (behind)", (FACE_T + 10, z0 + 5))
    dim(bx, (gb, H - STILE_W - 3.2), (gb + TONGUE_T, H - STILE_W - 3.2), f(TONGUE_T))
    dim(bx, (-4, H - STILE_W), (-4, H - STILE_W + TONGUE_L), f(TONGUE_L), vertical=True)
    dim(bx, (0, H - STILE_W - 7), (gb, H - STILE_W - 7), f(gb))
    dim(bx, (gb + TONGUE_T, H - STILE_W - 7), (FACE_T, H - STILE_W - 7), f(PANEL_T - TONGUE_T))
    bx.set_title("B  The top joint, enlarged: the panel's top edge is what goes in the top rail",
                 loc="left", fontsize=12, color=INK)
    for a in (ax, bx):
        a.set_aspect("equal")
        a.axis("off")
    fig.patch.set_facecolor(BG)
    fig.tight_layout()
    fig.savefig(f"{OUT}/section.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("wrote images/drawer/section.png")


# ------------------------------------------------------------------ the three cuts
def machining():
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.2), gridspec_kw=dict(width_ratios=[1, 1.3, 1]))
    # a: rail cross-section mid-length (groove)
    xm = XC
    pl = Plane(origin=(xm, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    to2d = lambda v: (FACE_Y1 - v.Y, v.Z - FRONT_Z0)          # noqa: E731
    a = axs[0]
    fill(a, section_polys(D["rail_lb"], pl, to2d), C["rail_lb"], lw=1.5)
    gb = FACE_T - PANEL_T
    label(a, (gb + TONGUE_T / 2, STILE_W - TONGUE_L / 2), "groove 1/4 wide x 3/8 deep,\nwhole length, inner edge",
          (FACE_T + 6, STILE_W + 4))
    dim(a, (0, -3), (FACE_T, -3), f(FACE_T))
    dim(a, (-3, 0), (-3, STILE_W), f(STILE_W), vertical=True)
    dim(a, (0, STILE_W + 3), (gb, STILE_W + 3), f(gb))
    a.text(FACE_T / 2, -9, "show face at left", ha="center", fontsize=9, color=INK)
    a.set_xlim(-8, FACE_T + 40)
    a.set_ylim(-12, STILE_W + 12)
    a.set_title("a  All 4 rails and 4 stiles:\ngroove the inner edge", loc="left", fontsize=11, color=INK)
    # b: rail end from above (stub tenon)
    b = axs[1]
    zp = FRONT_Z0 + STILE_W / 2
    plz = Plane(origin=(0, 0, zp), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
    tz = lambda v: (v.X - FX0, FACE_Y1 - v.Y)                 # noqa: E731
    fill(b, section_polys(D["rail_lb"], plz, tz), C["rail_lb"], lw=1.5)
    fill(b, section_polys(D["stile_ll"], plz, tz), C["stile_ll"], lw=1.5, alpha=0.55)
    x_t = STILE_W - TONGUE_L
    label(b, (x_t + TONGUE_L / 2, gb + TONGUE_T / 2), "stub tenon 1/4 thick x 3/8 long,\nboth ends (same bit set)",
          (STILE_W + 14, -10))
    label(b, (STILE_W / 2, FACE_T - 2), "stile (faded): its groove takes the tenon", (STILE_W + 14, FACE_T + 8))
    dim(b, (x_t, -4), (STILE_W, -4), f(TONGUE_L))
    b.set_xlim(-6, STILE_W + 110)
    b.set_ylim(-16, FACE_T + 16)
    b.set_title("b  All 4 rails: cut a stub tenon on both ends\n(seen from above, the left end)", loc="left",
                fontsize=11, color=INK)
    # c: panel edge (rabbet on the back)
    c = axs[2]
    fill(c, section_polys(D["panel_l"], pl, to2d), C["panel_l"], lw=1.5)
    zt = FRONT_H - STILE_W + TONGUE_L                          # top of the panel
    c.set_xlim(gb - 8, FACE_T + 40)
    c.set_ylim(zt - 30, zt + 6)
    label(c, (FACE_T - 1, zt - TONGUE_L - 1), "rabbet the BACK, all four edges:\n7/32 deep x 3/8 wide",
          (FACE_T + 5, zt - TONGUE_L - 8))
    label(c, (gb + TONGUE_T / 2, zt - 3), "1/4 tongue left, flush\nwith the painted face", (FACE_T + 5, zt - 1))
    dim(c, (gb, zt + 3), (gb + TONGUE_T, zt + 3), f(TONGUE_T))
    dim(c, (gb - 4, zt - TONGUE_L), (gb - 4, zt), f(TONGUE_L), vertical=True)
    c.text(FACE_T + 5, zt - 24, "the panel's top edge, show face at left", ha="left", fontsize=9, color=INK)
    c.set_title("c  Panel: rabbet the back on\nall four edges", loc="left", fontsize=11, color=INK)
    for a in axs:
        a.set_aspect("equal")
        a.axis("off")
    fig.patch.set_facecolor(BG)
    fig.tight_layout()
    fig.savefig(f"{OUT}/machining.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("wrote images/drawer/machining.png")


# ------------------------------------------------------------------ 3D steps from the viewer
FRONT = ("stile_ll", "stile_lr", "rail_lb", "rail_lt", "panel_l")
BOX = ("dside_ll", "dside_lr", "dfront_l", "dback_l", "dbot_l")


def shots():
    sys.argv = sys.argv[:1]
    from assembly_shots import capture
    tf = (FX0 + FRONT_W / 2, FACE_Y1, FRONT_Z0 + FRONT_H / 2)
    cam_f = lambda t: ((t[0] - 450, t[1] + 1300, t[2] + 750), t)   # noqa: E731  from the room, left, above

    def go(name, offs, cam, zoom, keys=FRONT):
        items = [(n, Pos(*offs.get(n, (0, 0, 0))) * D[n]) for n in keys]
        capture(items, [C[n] for n in keys], f"{OUT}/{name}.png", cam[0], cam[1], zoom)

    up = 260
    go("step-01", {"stile_ll": (-110, 0, 0), "stile_lr": (110, 0, 0), "rail_lt": (0, 0, up + 120),
                   "rail_lb": (0, 0, -90), "panel_l": (0, 0, up - 60)}, cam_f((tf[0], tf[1], tf[2] + 170)), 1.9)
    go("step-02", {"rail_lt": (0, 0, up + 120), "panel_l": (0, 0, up - 60)}, cam_f((tf[0], tf[1], tf[2] + 170)), 1.9)
    go("step-03", {"rail_lt": (0, 0, 160)}, cam_f((tf[0], tf[1], tf[2] + 60)), 2.5)
    go("step-04", {}, cam_f(tf), 2.7)
    tb = (FX0 + FRONT_W / 2, BOX_Y0 + BOX_D / 2, BOX_Z0 + BOX_H / 2)
    cam_b = ((tb[0] - 1000, tb[1] + 1400, tb[2] + 900), (tb[0], tb[1], tb[2] - 30))
    go("step-05", {"dside_ll": (-130, 0, 0), "dside_lr": (130, 0, 0), "dfront_l": (0, 150, 0),
                   "dback_l": (0, -150, 0), "dbot_l": (0, 0, -120)}, cam_b, 1.5, keys=BOX)
    cam_r = ((tb[0] + 1100, tb[1] - 1500, tb[2] + 900), (tb[0], tb[1], tb[2]))     # from behind, to see the back
    go("step-06", {}, cam_r, 1.6, keys=BOX)
    keys = BOX + FRONT + ("pull_l",)
    t7 = (tb[0], (BOX_Y1 + FACE_Y1) / 2 + 100, tb[2])
    go("step-07", {**{n: (0, 260, 0) for n in FRONT}, "pull_l": (0, 420, 0)},
       ((t7[0] - 900, t7[1] + 1700, t7[2] + 800), t7), 1.2, keys=keys)
    go("step-08", {}, ((tb[0] - 900, tb[1] + 1700, tb[2] + 800), (tb[0], tb[1] + 100, tb[2])), 1.35, keys=keys)


if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only in (None, "2d"):
        elevation()
        section_view()
        machining()
    if only in (None, "3d"):
        shots()
