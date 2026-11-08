#!/usr/bin/env python
"""Concept geometry and to-scale drawings for the rafter rod holder options page.

Everything here is drawn from one parameter set (inches, converted to mm for
CAD). Outputs:
  images/concepts/*.png   to-scale elevations (matplotlib) and iso renders
  <scratch>/concepts/*.stl concept solids for the renders and the slice quotes

Run from the vault root:
  .venv/bin/python projects/Fishing-rod-holder/pipeline/concepts.py
"""
import math
import os
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon as MplPolygon, Rectangle
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

VAULT = Path("/home/brian/ClaudeProjects/3d-modeling-brain")
PROJECT = VAULT / "projects" / "Fishing-rod-holder"
IMAGES = PROJECT / "images" / "concepts"
SCRATCH = Path(os.environ.get("SCRATCH", "/tmp/claude-1000/-home-brian--claude-spares-spare-OJ6Ifx/3f3590ae-4308-446d-b672-0d51f52c10fb/scratchpad")) / "concepts"
IN = 25.4

# ---- the garage (from Brian's photo, 2026-11-07) ----------------------------
JOIST_D = 7.25      # 2x8 depth (the 7 in of board above the joist bottom matched it)
JOIST_T = 1.5
JOIST_OC = 16.0
PLY = 0.75          # floor above the joists
WOOD_W = 3.5        # existing comb: a 1x4 on edge
WOOD_T = 0.75
WOOD_HANG = 20.0    # below the joist bottom
WOOD_LEN = 27.0
WOOD_NOTCH_D = 1.25
WOOD_NOTCH_PITCH = 5.0
WOOD_FIRST_NOTCH = 5.0  # notch centre below the joist bottom

# ---- the printed comb --------------------------------------------------------
W = 2.5             # plate width, along the joist
T = 0.5             # plate thickness
OVERLAP = 4.5       # mount on the joist side face
MOUNT_BELOW = 2.0   # mount module below the joist bottom (hosts the first lap)
LAP = 1.5           # half-lap length
PITCH = 4.0         # rod to rod
ROD_D = 0.375       # blank drawn at the comb; real range 1/4 to 5/8
ROD_RANGE = (0.25, 0.625)
END_MARGIN = 0.8    # plate below the last pocket floor

# pocket A: hook pocket, level channel
LIP_W = 0.75
LIP_H = 0.625       # lift needed to leave the pocket
POCKET_W = 0.875
CHANNEL_H = 1.25
MOUTH_R = 0.25

# pocket B: deep hook, sloped channel (mouth higher than the lip)
LIP_H_B = 1.0

# pocket C: snap clip
CLIP_ID = 0.42
CLIP_WALL = 0.09
CLIP_GAP = 0.30

# retrofit cap on the wood comb
CAP_H = 3.25
CAP_W = 2.75
CAP_T = 0.375
CAP_PROUD = 1.0     # cap mouth past the wood edge

SCREW_D = 0.164     # #8


def arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def pocket_a(c, lip_h=LIP_H, slope=0.0):
    """Void polygon of a hook pocket for a rod whose centre is c below the
    joist. Coordinates: u from the mouth edge inward, v = depth below the
    joist (positive down). `slope` raises the mouth floor above the lip."""
    v_floor = c + ROD_D / 2
    r = POCKET_W / 2
    v_arc = v_floor - r
    v_lip = v_floor - lip_h              # lip top at the pocket
    v_mouth = v_lip - slope              # channel floor at the mouth
    v_ceil = v_mouth - CHANNEL_H
    u_back = LIP_W + POCKET_W
    ch = MOUTH_R                          # chamfer at both mouth corners
    pts = [(-0.5, v_ceil - ch), (0.0, v_ceil - ch), (ch, v_ceil), (u_back, v_ceil), (u_back, v_arc)]
    pts += arc(LIP_W + r, v_arc, r, 0, 180)        # down through the floor
    pts += [(LIP_W, v_lip), (ch, v_mouth), (0.0, v_mouth + ch), (-0.5, v_mouth + ch)]
    return Polygon(pts)


def pocket_c(c):
    """Snap clip: a cavity with a C spring that grips the blank."""
    r_in = CLIP_ID / 2
    r_out = r_in + CLIP_WALL
    cx = LIP_W + 0.55
    cavity = Polygon([(-0.5, c - 1.0), (cx + r_out + 0.35, c - 1.0),
                      (cx + r_out + 0.35, c + 0.75), (-0.5, c + 0.75)])
    from shapely.geometry import Point
    ring = Point(cx, c).buffer(r_out, 64).difference(Point(cx, c).buffer(r_in, 64))
    ring = ring.difference(box(cx - r_out - 0.1, c - CLIP_GAP / 2, cx - r_in * 0.6, c + CLIP_GAP / 2))
    # flared lead-ins: short straight fingers angled outward from the opening
    u0 = cx - math.sqrt(max(r_out ** 2 - (CLIP_GAP / 2) ** 2, 0.0))
    lead_top = Polygon([(u0 + 0.02, c - CLIP_GAP / 2 + 0.01), (u0 - 0.28, c - CLIP_GAP / 2 - 0.22),
                        (u0 - 0.28, c - CLIP_GAP / 2 - 0.22 - CLIP_WALL), (u0 + 0.02 + CLIP_WALL, c - CLIP_GAP / 2 - 0.08)])
    lead_bot = Polygon([(x, 2 * c - y) for x, y in lead_top.exterior.coords])
    stem = box(cx + r_in, c - 0.12, cx + r_out + 0.36, c + 0.12)
    spring = unary_union([g.buffer(0) for g in (ring, lead_top, lead_bot, stem)]).buffer(0)
    return cavity, spring


def wood_notch(c, edge_u=0.0):
    """The existing semicircular notch: diameter WOOD_NOTCH_D cut into the edge."""
    r = WOOD_NOTCH_D / 2
    pts = [(edge_u - 0.5, c - r), (edge_u, c - r)] + arc(edge_u, c, r, 90, -90)[::-1] + [(edge_u, c + r), (edge_u - 0.5, c + r)]
    # arc from (edge, c-r) around the inside to (edge, c+r)
    pts = [(edge_u - 0.5, c - r)] + [(edge_u + r * math.cos(math.radians(a)), c - r * math.sin(math.radians(a)))
                                     for a in [90 - 180 * i / 24 for i in range(25)]] + [(edge_u - 0.5, c + r)]
    return Polygon(pts)


# ---- module layout -------------------------------------------------------------
def layout(n_rods=4):
    """Return rod centres (depth below the joist) and module spans.
    Mount: +OVERLAP above the joist bottom to MOUNT_BELOW below, lap at its foot.
    Modules: 2 rods each, LAP at the top (and at the foot unless it is the end)."""
    rods = []
    modules = []
    top = MOUNT_BELOW - LAP          # module top overlaps the mount's lap
    c = top + LAP + 0.3 + CHANNEL_H + LIP_H - ROD_D / 2  # first pocket clears the lap by 0.3
    # simplify: fixed first rod at 4.0 below the joist (checked below)
    c = 4.0
    n_mod = math.ceil(n_rods / 2)
    for m in range(n_mod):
        rods_here = [c + PITCH * (2 * m + k) for k in range(2) if 2 * m + k < n_rods]
        rods += rods_here
        bottom = rods_here[-1] + ROD_D / 2 + END_MARGIN if m == n_mod - 1 else top + 9.5
        modules.append((top, bottom, m == n_mod - 1))
        top = bottom - LAP
    return rods, modules


def plate_polygon(top, bottom):
    return box(0.0, top, W, bottom)


def comb_2d(pocket, n_rods=4):
    """Shapely polygons for a whole comb (mount + modules), with pockets cut."""
    rods, modules = layout(n_rods)
    mount = box(0.0, -OVERLAP, W, MOUNT_BELOW)
    pieces = [mount]
    for top, bottom, is_end in modules:
        p = plate_polygon(top, bottom)
        if is_end:  # round the foot corners, keep the lap end square
            rounded = p.buffer(-0.5, join_style=2).buffer(0.5, join_style=1, quad_segs=16)
            p = unary_union([rounded, box(0, top, W, top + 1.0)])
        pieces.append(p)
    voids = [pocket(c) for c in rods]
    return pieces, voids, rods, modules


# ---- drawing helpers -----------------------------------------------------------
WOOD = "#d8b98a"
WOOD_EDGE = "#8a6a3c"
PLY_C = "#e8d6b3"
PRINT = "#5b8def"
PRINT_EDGE = "#2b4f9e"
ROD = "#333333"
VOID = "#ffffff"
ACCENT = "#d9480f"
INK = "#1f2430"
MUTED = "#6b7280"


def poly(ax, p, fc, ec, lw=1.0, z=2, alpha=1.0):
    if p.is_empty:
        return
    geoms = getattr(p, "geoms", [p])
    for g in geoms:
        ax.add_patch(MplPolygon(list(g.exterior.coords), closed=True, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha))
        for ring in g.interiors:
            ax.add_patch(MplPolygon(list(ring.coords), closed=True, fc="white", ec=ec, lw=lw, zorder=z + 0.1))


def rod(ax, u, v, d=ROD_D, z=5, color=ROD):
    ax.add_patch(Circle((u, v), d / 2, fc=color, ec="black", lw=0.8, zorder=z))


def dim_v(ax, x, v0, v1, text, side=1, color=INK, fs=9):
    ax.annotate("", xy=(x, v0), xytext=(x, v1), arrowprops=dict(arrowstyle="<->", color=color, lw=0.9), zorder=8)
    ax.text(x + 0.12 * side, (v0 + v1) / 2, text, color=color, fontsize=fs, va="center",
            ha="left" if side > 0 else "right", zorder=9)


def dim_h(ax, v, u0, u1, text, above=True, color=INK, fs=9):
    ax.annotate("", xy=(u0, v), xytext=(u1, v), arrowprops=dict(arrowstyle="<->", color=color, lw=0.9), zorder=8)
    ax.text((u0 + u1) / 2, v - 0.15 if above else v + 0.15, text, color=color, fontsize=fs, ha="center",
            va="bottom" if above else "top", zorder=9)


def joist_band(ax, u0, u1):
    """Looking along the rods: the joist side face is a band, plywood above."""
    ax.add_patch(Rectangle((u0, -JOIST_D - PLY), u1 - u0, PLY, fc=PLY_C, ec=WOOD_EDGE, lw=0.8, zorder=0, hatch="//"))
    ax.add_patch(Rectangle((u0, -JOIST_D), u1 - u0, JOIST_D, fc=WOOD, ec=WOOD_EDGE, lw=1.0, zorder=0))


def finish(ax, u0, u1, v0, v1):
    ax.set_xlim(u0, u1)
    ax.set_ylim(v1, v0)  # depth grows downward
    ax.set_aspect("equal")
    ax.axis("off")


def label(ax, u, v, text, color=INK, fs=9, ha="left", va="center", weight="normal"):
    ax.text(u, v, text, color=color, fontsize=fs, ha=ha, va=va, zorder=10, weight=weight)


# ---- figure 1: why the wood notch drops rods, and the hook pocket -----------------
def fig_why():
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.6), dpi=160)
    # left: wood notch, rod at the mouth
    ax = axes[0]
    c = 2.0
    board = box(0, 0, WOOD_W, 4.0).difference(wood_notch(c))
    poly(ax, board, WOOD, WOOD_EDGE)
    # rod sits at the lowest point of the arc: at the mouth, c + r - rod/2... the arc bottom is at the edge
    r = WOOD_NOTCH_D / 2
    rod(ax, ROD_D / 2 * 0.0 + 0.0 + 0.19, c + r - ROD_D / 2 - 0.02)
    ax.annotate("", xy=(-0.35, c + 0.35), xytext=(0.6, c + 0.35), arrowprops=dict(arrowstyle="->", color=ACCENT, lw=2), zorder=9)
    label(ax, 0.75, c + 0.95, "lowest point of the arc\nis the board edge", color=ACCENT, fs=9)
    label(ax, 0.2, 0.35, "your 1x4 comb, 1-1/4 in notch", color=INK, fs=9)
    label(ax, -0.9, c + 0.1, "nothing\nin front\nof the rod", color=MUTED, fs=8, ha="center")
    finish(ax, -1.4, WOOD_W + 0.3, -0.1, 4.2)
    ax.set_title("Now: a half-round in a vertical edge", fontsize=11, color=INK, loc="left")
    # right: hook pocket
    ax = axes[1]
    c = 2.0
    plate = box(0, 0, W, 4.0).difference(pocket_a(c))
    poly(ax, plate, PRINT, PRINT_EDGE)
    rod(ax, LIP_W + POCKET_W / 2, c)
    v_floor = c + ROD_D / 2
    v_lip = v_floor - LIP_H
    dim_v(ax, LIP_W + POCKET_W + 0.15, v_floor, v_lip, f'lift {frac(LIP_H)} in\nto leave', side=1, color=ACCENT)
    # path in: arrow along the channel then down
    ax.annotate("", xy=(LIP_W + POCKET_W / 2, c - 0.45), xytext=(-0.5, v_lip - 0.55),
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.4, connectionstyle="arc3,rad=-0.25"), zorder=9)
    label(ax, -0.95, v_lip + 0.45, "slide in,\nlet it drop", color=INK, fs=8, ha="center")
    label(ax, 0.1, 3.6, f"lip {frac(LIP_W)} wide, pocket {frac(POCKET_W)}", color="white", fs=8)
    dim_v(ax, -0.35, v_lip, v_lip - CHANNEL_H, f"mouth\n{frac(CHANNEL_H)} tall", side=-1, fs=8)
    finish(ax, -1.6, W + 1.2, -0.1, 4.2)
    ax.set_title("Hook pocket: the floor is inside, a lip at the mouth", fontsize=11, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(IMAGES / "why.png", facecolor="white")
    plt.close(fig)


def frac(x):
    """Inches to the nearest 1/16 as a plain fraction string."""
    whole = int(x)
    rem = x - whole
    n = round(rem * 16)
    if n == 16:
        whole += 1
        n = 0
    if n == 0:
        return str(whole)
    d = 16
    while n % 2 == 0:
        n //= 2
        d //= 2
    return f"{whole}-{n}/{d}" if whole else f"{n}/{d}"


# ---- figure 2: the comb in place, looking along the rods -------------------------
def fig_scene(pocket=pocket_a, name="scene-a.png", n_rods=4, title="Option A in place"):
    pieces, voids, rods, modules = comb_2d(pocket, n_rods)
    fig, ax = plt.subplots(figsize=(6.2, 9.2), dpi=160)
    joist_band(ax, -3.5, W + 4.5)
    whole = unary_union(pieces)
    for pc in pieces:
        poly(ax, pc.difference(unary_union(voids)), PRINT, PRINT_EDGE, lw=1.0)
    # laps: show the boundary lines
    for top, bottom, is_end in modules:
        ax.plot([0, W], [top, top], color=PRINT_EDGE, lw=0.8, ls=":", zorder=6)
        ax.plot([0, W], [top + LAP, top + LAP], color=PRINT_EDGE, lw=0.8, ls=":", zorder=6)
    for c in rods:
        rod(ax, LIP_W + POCKET_W / 2, c)
    # screws into the joist
    for (u, v) in [(0.6, -3.4), (W - 0.6, -3.4), (W / 2, -1.0)]:
        ax.add_patch(Circle((u, v), SCREW_D / 2 + 0.06, fc="#e5e7eb", ec=INK, lw=0.8, zorder=6))
        ax.plot([u - 0.08, u + 0.08], [v - 0.08, v + 0.08], color=INK, lw=0.8, zorder=7)
        ax.plot([u - 0.08, u + 0.08], [v + 0.08, v - 0.08], color=INK, lw=0.8, zorder=7)
    # lap bolts
    for top, bottom, is_end in modules:
        for v in (top + 0.4, top + LAP - 0.4):
            ax.add_patch(Circle((W / 2, v), 0.08, fc="#e5e7eb", ec=INK, lw=0.7, zorder=6))
    hang = modules[-1][1]
    dim_v(ax, W + 0.6, 0, hang, f"hang {frac(hang)} in\n(now 20)", side=1)
    dim_v(ax, -0.6, 0, rods[0], f"{frac(rods[0])}", side=-1, fs=8)
    dim_v(ax, -0.6, rods[0], rods[1], f"pitch {frac(PITCH)}", side=-1, fs=8)
    dim_h(ax, -JOIST_D - PLY - 0.4, 0, W, f"{frac(W)} wide, {frac(T)} thick", above=True, fs=8)
    label(ax, W + 0.3, -JOIST_D / 2, "2x8 joist\n(side face)", color=WOOD_EDGE, fs=8)
    label(ax, W + 0.3, MOUNT_BELOW - LAP / 2, "half-lap,\ntwo M4 bolts", color=PRINT_EDGE, fs=7.5)
    label(ax, -0.2, -OVERLAP + 0.5, f"three #8 x 1-1/2\ninto the joist", color=INK, fs=7.5, ha="right")
    vm = rods[2] - 1.1  # inside the third pocket's mouth
    label(ax, -3.4, vm - 0.9, "mouth faces the\nsame way as\nyour notches", color=MUTED, fs=8)
    ax.annotate("", xy=(0.3, vm), xytext=(-1.6, vm), arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.2), zorder=9)
    finish(ax, -3.5, W + 4.5, -JOIST_D - PLY - 0.9, hang + 0.6)
    ax.set_title(title, fontsize=11, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(IMAGES / name, facecolor="white")
    plt.close(fig)
    return rods, modules, hang


# ---- figure 3: pocket close-ups at one scale --------------------------------------
def fig_pockets():
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.4), dpi=160)
    c = 2.1
    specs = [
        ("A  Hook pocket", lambda cc: pocket_a(cc), f"lift {frac(LIP_H)} in to leave", "level mouth, rod drops in"),
        ("B  Deep hook", lambda cc: pocket_a(cc, LIP_H, slope=LIP_H_B - LIP_H), f"lift {frac(LIP_H_B)} in to leave", "mouth higher than the lip:\nthe rod rolls in by itself"),
        ("C  Snap clip", None, "grips every way", f"fits {frac(CLIP_ID - 0.1)} to {frac(CLIP_ID)} blanks only"),
    ]
    for ax, (ttl, fn, big, small) in zip(axes, specs):
        if fn is not None:
            void = fn(c)
            plate = box(0, 0, W, 4.2).difference(void)
            poly(ax, plate, PRINT, PRINT_EDGE)
            rod(ax, LIP_W + POCKET_W / 2, c)
            v_floor = c + ROD_D / 2
            lip = LIP_H if "A" in ttl else LIP_H_B
            mouth_floor = v_floor - lip
            # escape arrow
            ax.annotate("", xy=(LIP_W + POCKET_W / 2, v_floor - lip - 0.35), xytext=(LIP_W + POCKET_W / 2, c - 0.1),
                        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.6), zorder=9)
            dim_v(ax, LIP_W + POCKET_W + 0.2, v_floor, mouth_floor, big, side=1, color=ACCENT, fs=9)
            if "B" in ttl:
                ax.annotate("", xy=(LIP_W + 0.2, mouth_floor + 0.2), xytext=(-0.3, mouth_floor - 0.1),
                            arrowprops=dict(arrowstyle="->", color=INK, lw=1.2), zorder=9)
        else:
            cavity, spring = pocket_c(c)
            plate = box(0, 0, W, 4.2).difference(cavity).union(spring).buffer(0)
            poly(ax, plate, PRINT, PRINT_EDGE)
            rod(ax, LIP_W + 0.55, c, d=0.40)
            ax.annotate("", xy=(LIP_W + 0.55 - CLIP_ID / 2 - 0.05, c), xytext=(-0.6, c),
                        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.6), zorder=9)
            label(ax, -0.65, c - 0.3, "push in", color=ACCENT, fs=8, ha="left")
            label(ax, LIP_W + 1.3, c - 0.9, "PETG spring\n0.09 in wall", color=INK, fs=8)
        label(ax, 0.1, 4.0, small, color="white", fs=8, va="bottom")
        finish(ax, -1.0, W + 1.6, -0.1, 4.3)
        ax.set_title(ttl, fontsize=11, color=INK, loc="left", weight="bold")
    fig.tight_layout()
    fig.savefig(IMAGES / "pockets.png", facecolor="white")
    plt.close(fig)


# ---- figure 4: build options: spliced print vs caps on the wood ------------------
def fig_build():
    fig, axes = plt.subplots(1, 2, figsize=(10, 8.6), dpi=160)
    # left: exploded modules
    ax = axes[0]
    pieces, voids, rods, modules = comb_2d(pocket_a, 4)
    gap = 1.2
    shift = 0.0
    allv = unary_union(voids)
    for i, pc in enumerate(pieces):
        p = pc.difference(allv)
        # translate down by cumulative gap
        from shapely.affinity import translate
        poly(ax, translate(p, 0, shift), PRINT, PRINT_EDGE)
        minv, maxv = p.bounds[1], p.bounds[3]
        if i > 0:
            top = modules[i - 1][0]
            ax.add_patch(Rectangle((0, top + shift), W, LAP, fc="none", ec=ACCENT, lw=1.2, ls="--", zorder=7))
        if i < len(pieces) - 1:
            foot = (MOUNT_BELOW if i == 0 else modules[i - 1][1])
            ax.add_patch(Rectangle((0, foot - LAP + shift), W, LAP, fc="none", ec=ACCENT, lw=1.2, ls="--", zorder=7))
        name = "mount" if i == 0 else ("end module, 2 rods" if modules[i - 1][2] else "module, 2 rods")
        length = maxv - minv
        label(ax, W + 0.25, (minv + maxv) / 2 + shift, f"{name}\n{frac(length)} in", color=PRINT_EDGE, fs=8.5)
        shift += gap
    label(ax, 0, -OVERLAP - 0.9, "A  Printed comb in three pieces", color=INK, fs=11, weight="bold")
    label(ax, 0, -OVERLAP - 0.4, "dashed = half-laps, two M4 bolts each; every piece lies flat on the bed", color=MUTED, fs=8)
    finish(ax, -0.6, W + 3.6, -OVERLAP - 1.3, modules[-1][1] + shift + 0.3)
    # right: caps on the wood comb
    ax = axes[1]
    joist_band(ax, -2.5, WOOD_W + 3.0)
    notches = [WOOD_FIRST_NOTCH + WOOD_NOTCH_PITCH * i for i in range(4)]
    board = box(0, -JOIST_D + 0.25, WOOD_W, WOOD_HANG)
    for c in notches:
        board = board.difference(wood_notch(c))
    poly(ax, board, WOOD, WOOD_EDGE)
    for c in notches:
        # cap: mouth CAP_PROUD past the wood edge, pocket floor at the notch centre height
        cap = box(-CAP_PROUD, c - CAP_H * 0.62, -CAP_PROUD + CAP_W, c + CAP_H * 0.38)
        void = pocket_a(c - ROD_D / 2)  # pocket floor at c
        from shapely.affinity import translate
        void = translate(void, -CAP_PROUD, 0)
        cap = cap.difference(void)
        poly(ax, cap, PRINT, PRINT_EDGE, alpha=0.92, z=4)
        rod(ax, -CAP_PROUD + LIP_W + POCKET_W / 2, c - ROD_D / 2, z=6)
        for v in (c - CAP_H * 0.62 + 0.45, c + CAP_H * 0.38 - 0.45):
            ax.add_patch(Circle((-CAP_PROUD + CAP_W - 0.5, v), 0.09, fc="#e5e7eb", ec=INK, lw=0.7, zorder=7))
    label(ax, -2.4, -JOIST_D - PLY - 1.0, "B  Printed caps on your wood combs", color=INK, fs=11, weight="bold")
    label(ax, -2.4, -JOIST_D - PLY - 0.45, f"one cap per notch, {frac(CAP_W)} x {frac(CAP_H)} x {frac(CAP_T)}, two #8 screws into the board", color=MUTED, fs=8)
    label(ax, WOOD_W + 0.2, WOOD_HANG - 2, "the board, its\nnotches and the\n20 in hang stay", color=WOOD_EDGE, fs=8)
    dim_h(ax, notches[0] - CAP_H * 0.62 - 0.35, -CAP_PROUD, 0, f"{frac(CAP_PROUD)} in proud", above=True, fs=7.5)
    finish(ax, -2.5, WOOD_W + 3.0, -JOIST_D - PLY - 1.5, WOOD_HANG + 0.6)
    fig.tight_layout()
    fig.savefig(IMAGES / "build.png", facecolor="white")
    plt.close(fig)


# ---- figure 5: side view across the rods: two combs, a 7 ft rod, reels --------------
def fig_side():
    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=160)
    # joists as cross sections, 16 in OC, plywood above
    span = 96.0
    ax.add_patch(Rectangle((-6, -JOIST_D - PLY), span + 12, PLY, fc=PLY_C, ec=WOOD_EDGE, lw=0.8, zorder=0, hatch="//"))
    for i in range(7):
        x = i * JOIST_OC
        ax.add_patch(Rectangle((x - JOIST_T / 2, -JOIST_D), JOIST_T, JOIST_D, fc=WOOD, ec=WOOD_EDGE, lw=0.8, zorder=1))
    rods, modules, hang = (lambda r: (r[2], r[3], r[3][-1][1]))(comb_2d(pocket_a, 4))
    comb_x = [JOIST_OC * 1 + JOIST_T / 2, JOIST_OC * 4 + JOIST_T / 2]  # on the side face of joists 1 and 4
    for x in comb_x:
        ax.add_patch(Rectangle((x, -OVERLAP), T, OVERLAP + hang, fc=PRINT, ec=PRINT_EDGE, lw=0.9, zorder=3))
    # rods: 84 in long, butt at the left, reel 14 in from the butt hanging below (spinning)
    rod_len = 84.0
    butt_x = comb_x[0] - 22.0
    for i, c in enumerate(rods):
        y = c
        ax.plot([butt_x, butt_x + rod_len], [y, y], color=ROD, lw=2.2 - 0.3 * i, zorder=4, solid_capstyle="round")
        ax.plot([butt_x, butt_x + 11], [y, y], color="#111111", lw=5, zorder=4, solid_capstyle="round")  # grip
        # spinning reel hanging below, 14 in from the butt
        rx = butt_x + 14
        reel = Polygon([(rx - 1.2, y + 0.3), (rx + 1.2, y + 0.3), (rx + 1.8, y + 3.2), (rx + 0.2, y + 4.6), (rx - 1.6, y + 4.4), (rx - 2.0, y + 2.6)])
        poly(ax, reel, "#9ca3af", "#374151", lw=0.8, z=4, alpha=0.9)
    dim_h(ax, hang + 1.0, comb_x[0], comb_x[1], "comb spacing: yours is ?", above=False)
    tip_x = butt_x + rod_len
    dim_v(ax, tip_x + 1.5, rods[0], rods[1], f"{frac(PITCH)} in pitch. A spinning reel is\nabout 4-1/2 in tall, so reels\nstacked in line touch the\nrod below. If reels stay on:\nstagger the handles a foot,\nor go to a 5 in pitch.", side=1, fs=8, color=ACCENT)
    label(ax, butt_x - 1, rods[0] - 1.6, "7 ft rod, butt here", color=INK, fs=8.5)
    label(ax, butt_x - 0.2, rods[1] + 2.0, "spinning reels,\nif left on", color="#374151", fs=8)
    label(ax, 0, -JOIST_D - PLY - 0.9, "Looking across the rods (along the joists). Combs on the side face of two joists, 16 in on centre.", color=INK, fs=10)
    finish(ax, -6, span + 14, -JOIST_D - PLY - 1.4, hang + 3.2)
    fig.tight_layout()
    fig.savefig(IMAGES / "side.png", facecolor="white")
    plt.close(fig)


# ---- 3D concept solids (build123d) for the iso renders and the slice quotes ----------
def build_solids():
    from build123d import (Axis, Box, Cylinder, Location, Mesher, Part, Plane, Pos, Polyline, Rot,
                           extrude, export_stl, make_face)

    def solid_from_poly(p, thickness):
        """Extrude a shapely polygon (inches, (u, depth)) into a plate of `thickness` inches.
        u -> X, depth -> -Y (so the joist is at the top), thickness -> Z."""
        parts = None
        for g in getattr(p, "geoms", [p]):
            pts = [(u * IN, -v * IN, 0.0) for u, v in list(g.exterior.coords)[:-1]]
            face = make_face(Polyline(*pts, close=True))
            s = extrude(face, thickness * IN)
            for ring in g.interiors:
                hpts = [(u * IN, -v * IN, 0.0) for u, v in list(ring.coords)[:-1]]
                s = s - extrude(make_face(Polyline(*hpts, close=True)), thickness * IN)
            parts = s if parts is None else parts + s
        return parts

    pieces, voids, rods, modules = comb_2d(pocket_a, 4)
    allv = unary_union(voids)
    solids = []
    for i, pc in enumerate(pieces):
        p = pc.difference(allv)
        s = solid_from_poly(p, T)
        # half-laps: mount keeps the front half (Z high) at its foot; modules keep the back half at the top
        if i == 0:
            foot = MOUNT_BELOW
            s = s - Box(W * IN + 2, LAP * IN + 0.01, T * IN / 2 + 0.01).moved(
                Location((W * IN / 2, -(foot - LAP / 2) * IN, T * IN / 4)))
            for (u, v) in [(0.6, -3.4), (W - 0.6, -3.4), (W / 2, -1.0)]:
                s = s - Cylinder(SCREW_D * IN / 2 + 0.2, T * IN + 2).moved(Location((u * IN, -v * IN, T * IN / 2)))
        else:
            top, bottom, is_end = modules[i - 1]
            s = s - Box(W * IN + 2, LAP * IN + 0.01, T * IN / 2 + 0.01).moved(
                Location((W * IN / 2, -(top + LAP / 2) * IN, 3 * T * IN / 4)))
            if not is_end:
                s = s - Box(W * IN + 2, LAP * IN + 0.01, T * IN / 2 + 0.01).moved(
                    Location((W * IN / 2, -(bottom - LAP / 2) * IN, T * IN / 4)))
        # lap bolt holes (M4 clearance 4.4)
        for top, bottom, is_end in modules:
            for v in (top + 0.4, top + LAP - 0.4):
                s = s - Cylinder(2.2, T * IN + 2).moved(Location((W * IN / 2, -v * IN, T * IN / 2)))
        solids.append(s)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    names = ["mount", "module", "end-module"]
    for s, n in zip(solids, names):
        # print orientation: flat, back face on the bed. Move to Z=0 and XY positive.
        bb = s.bounding_box()
        s_print = s.moved(Location((-bb.min.X, -bb.min.Y, -bb.min.Z)))
        export_stl(s_print, str(SCRATCH / f"comb-{n}.stl"))
        assert len(s_print.solids()) == 1, n
        print(f"{n}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, {s.volume/1000:.1f} cm3")
    # assembled comb and rod stubs, in assembly coordinates, for the OpenSCAD scene renders
    assembled = solids[0]
    for s in solids[1:]:
        assembled = assembled + s
    export_stl(assembled, str(SCRATCH / "scene-comb.stl"))
    stubs = None
    for c in rods:
        cyl = Cylinder(ROD_D * IN / 2, 10 * IN).moved(Location(((LIP_W + POCKET_W / 2) * IN, -c * IN, T * IN / 2)))
        stubs = cyl if stubs is None else stubs + cyl
    export_stl(stubs, str(SCRATCH / "scene-rods.stl"))
    # cap
    cap2d = box(0, 0, CAP_W, CAP_H).difference(pocket_a(CAP_H * 0.62 - ROD_D / 2).buffer(0))
    cap = solid_from_poly(cap2d, CAP_T)
    for v in (0.45, CAP_H - 0.45):
        cap = cap - Cylinder(SCREW_D * IN / 2 + 0.2, CAP_T * IN + 2).moved(Location(((CAP_W - 0.5) * IN, -v * IN, CAP_T * IN / 2)))
    bb = cap.bounding_box()
    cap_print = cap.moved(Location((-bb.min.X, -bb.min.Y, -bb.min.Z)))
    export_stl(cap_print, str(SCRATCH / "cap.stl"))
    # cap in assembly coordinates: mouth CAP_PROUD past the wood edge (X=0), notch centre at Y=0
    c0 = CAP_H * 0.62 - ROD_D / 2
    cap_scene = cap.moved(Location((-CAP_PROUD * IN, (c0 + ROD_D / 2) * IN, 0)))
    export_stl(cap_scene, str(SCRATCH / "scene-cap.stl"))
    rod_stub = Cylinder(ROD_D * IN / 2, 6 * IN).moved(
        Location(((-CAP_PROUD + LIP_W + POCKET_W / 2) * IN, (ROD_D / 2) * IN, CAP_T * IN / 2)))
    export_stl(rod_stub, str(SCRATCH / "scene-cap-rod.stl"))
    print(f"cap: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, {cap.volume/1000:.1f} cm3")
    return rods, modules


OPENSCAD = Path.home() / ".local/bin/openscad"


def scad_render(name, body, camera, size=(1400, 1000)):
    """Write a .scad that imports the scene STLs with context geometry, render a PNG."""
    scad = SCRATCH / f"{name}.scad"
    scad.write_text(body)
    out = IMAGES / f"{name}.png"
    cmd = [str(OPENSCAD), "--backend=Manifold", "--preview", "--viewall", "--autocenter",
           f"--camera={camera}", "--colorscheme=Tomorrow", f"--imgsize={size[0]},{size[1]}",
           "-o", str(out), str(scad)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(f"openscad failed on {name}")
    return out


def render_scenes():
    s = str(SCRATCH)
    # Rotate the assembly so depth (-Y) becomes down (-Z): the joist is at the top of the picture.
    comb_scene = f"""
rotate([90, 0, 0]) {{
  color("#d8b98a") translate([-110, 0, -{JOIST_T * IN}]) cube([300, {JOIST_D * IN}, {JOIST_T * IN}]);   // joist, side face at Z=0
  color("#e8d6b3") translate([-110, {JOIST_D * IN}, -200]) cube([300, {PLY * IN}, 400]);               // floor above
  color("#5b8def") import("{s}/scene-comb.stl");
  color("#333333") import("{s}/scene-rods.stl");
}}
"""
    scad_render("render-comb", comb_scene, "0,0,0,100,0,-35,0")
    # close-up of one pocket: clip the scene to the second pocket
    pocket_scene = f"""
rotate([90, 0, 0]) intersection() {{
  union() {{
    color("#5b8def") import("{s}/scene-comb.stl");
    color("#333333") import("{s}/scene-rods.stl");
  }}
  translate([-20, -{(8.0 + 2.2) * IN}, -200]) cube([120, {4.2 * IN}, 400]);
}}
"""
    scad_render("render-pocket", pocket_scene, "0,0,0,95,0,-30,0", size=(1200, 900))
    cap_scene = f"""
rotate([90, 0, 0]) {{
  // the 1x4 comb, on edge, with its half-round notch; wood behind the cap (Z < 0)
  color("#d8b98a") difference() {{
    translate([0, -{3.0 * IN}, -{WOOD_T * IN}]) cube([{WOOD_W * IN}, {6.0 * IN}, {WOOD_T * IN}]);
    translate([0, 0, -{WOOD_T * IN} - 1]) cylinder(h={WOOD_T * IN} + 2, d={WOOD_NOTCH_D * IN}, $fn=64);
  }}
  color("#5b8def") import("{s}/scene-cap.stl");
  color("#333333") import("{s}/scene-cap-rod.stl");
}}
"""
    scad_render("render-cap", cap_scene, "0,0,0,95,0,-35,0", size=(1200, 900))


def render(stl, png, views):
    subprocess.run([str(VAULT / ".venv/bin/python"), str(VAULT / "scripts/render_stl.py"), str(stl), str(png), *views], check=True)


if __name__ == "__main__":
    IMAGES.mkdir(parents=True, exist_ok=True)
    fig_why()
    rods, modules, hang = fig_scene()
    fig_pockets()
    fig_build()
    fig_side()
    print("rods below joist (in):", [round(r, 2) for r in rods])
    print("modules (top, bottom, end):", [(round(a, 2), round(b, 2), e) for a, b, e in modules])
    print("hang (in):", round(hang, 2))
    if "--no-3d" not in sys.argv:
        build_solids()
        render(SCRATCH / "cap.stl", IMAGES / "check-cap.png", ["30,-60"])
    if "--no-render" not in sys.argv:
        render_scenes()
    print("done")
