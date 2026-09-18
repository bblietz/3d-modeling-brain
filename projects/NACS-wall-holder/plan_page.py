#!/usr/bin/env python3
"""Draw the NACS wall holder design plan as a to-scale HTML page (plan.html).

The nose outline comes from Tesla's NACS STEP (reference/nose_outline_30mm.csv);
every other number is a design constant below or derived from one.

    .venv/bin/python projects/NACS-wall-holder/plan_page.py
"""
import math
import os

import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))

# connector facts: Tesla TS-0023666 rev 1.1 and the 500V STEP
NOSE_LEN = 32.5
NOSE_H = 35.52          # at 30 mm from the tip
NOTCH_A, NOTCH_B = 17.13, 23.35   # notch walls from the tip, at the notch floor
NOTCH_D = 3.96
NOTCH_W_FLOOR, NOTCH_W_MOUTH = 9.71, 11.5
HANDLE_LEN = 194.5
CABLE_OD = 14.5
CABLE_LEN = 5500

# design constants
THETAS = (20, 25, 30)
THETA = 25
CLEAR = 0.5
CLEAT_PROUD = 2.2
CLEAT_W = 8.0
CLEAT_A, CLEAT_C, CLEAT_B = 18.3, 20.3, 22.5   # root start, crown end, chamfer end (from the floor)
MOUTH = 33.0            # outer lip above the floor: the pivot for the insertion swing
BACK_WALL = 42.0
SWING = math.degrees(math.atan((CLEAT_PROUD + CLEAR) / (MOUTH - CLEAT_C)))
FLOOR_RELIEF = MOUTH * math.tan(math.radians(SWING))
WALL_T = 4.0
PLATE_T = 5.0
PLATE_W = 115.0
PLATE_H = 240.0
FLOOR_Z = 18.0
BACK_GAP = 4.5
SADDLE_Z, SADDLE_D, SADDLE_T, LIP_H, SADDLE_W, CROWN_R = 200.0, 80.0, 12.0, 18.0, 105.0, 80.0
RIB_YS = (-50, -20, 20, 50)
COIL_D = 300.0
LOOPS = math.ceil(CABLE_LEN / (math.pi * COIL_D))
CG_FROM_TIP = 100.0

HALF = NOSE_H / 2
HC = HALF + CLEAR


def outline():
    pts = np.loadtxt(os.path.join(HERE, "reference", "nose_outline_30mm.csv"), delimiter=",", comments="#")
    return Polygon([tuple(p) for p in pts])


def frame(theta):
    t = math.radians(theta)
    up = np.array([math.sin(t), math.cos(t)])
    n_out = np.array([math.cos(t), -math.sin(t)])
    T = np.array([BACK_GAP + HC * math.cos(t), FLOOR_Z])
    return up, n_out, T


def P(fr, s, q):
    up, n_out, T = fr
    return T + s * up + q * n_out


def poly(fr, pts):
    return Polygon([tuple(P(fr, s, q)) for s, q in pts])


def handle_env(fr):
    top = [(0, HALF - 1.65), (1.5, HALF), (NOSE_LEN, HALF), (46, HALF + 7), (60, HALF + 8), (150, HALF + 8), (HANDLE_LEN, HALF + 2)]
    bot = [(HANDLE_LEN, -HALF - 4), (150, -HALF - 10), (70, -HALF - 6), (46, -HALF), (1.5, -HALF), (0, -HALF + 1.65)]
    return poly(fr, top + bot)


def nose_notched(fr):
    a = NOTCH_A - NOTCH_D * math.tan(math.radians(0.5))
    b = NOTCH_B + NOTCH_D * math.tan(math.radians(3))
    return poly(fr, [(0, HALF - 1.65), (1.5, HALF), (NOSE_LEN, HALF), (NOSE_LEN, -HALF), (b, -HALF), (NOTCH_B, -HALF + NOTCH_D),
                     (NOTCH_A, -HALF + NOTCH_D), (a, -HALF), (1.5, -HALF), (0, -HALF + 1.65)])


def socket_geometry(fr):
    prism = poly(fr, [(0, -HC), (MOUTH, -HC), (MOUTH, HC), (0, HC)])
    lip = tuple(P(fr, MOUTH, HC))
    tip = tuple(P(fr, 0, 0))
    test = rotate(prism, 5, origin=lip)
    sgn = 1 if test.centroid.x > prism.centroid.x else -1
    swept = unary_union([rotate(prism, sgn * a, origin=lip) for a in np.linspace(0, SWING, 13)])
    swung = rotate(handle_env(fr), sgn * SWING, origin=lip)
    back = poly(fr, [(MOUTH - 1, -HC - WALL_T), (BACK_WALL, -HC - WALL_T), (BACK_WALL, -HC), (MOUTH - 1, -HC)])
    body = unary_union([swept.buffer(WALL_T, join_style=1), back])
    x_front = body.bounds[2]
    z_top = P(fr, MOUTH, HC + WALL_T)[1]
    body = unary_union([body, Polygon([(0, 0), (x_front, 0), (x_front, z_top), (0, z_top)])])
    cleat = poly(fr, [(CLEAT_A, -HC), (CLEAT_B, -HC), (CLEAT_C, -HC + CLEAT_PROUD), (CLEAT_A, -HC + CLEAT_PROUD)])
    return swept, swung, body, cleat, lip, tip


class View:
    def __init__(self, k, x0, x1, z0, z1, pad=14):
        self.k, self.x0, self.z1, self.pad = k, x0, z1, pad
        self.w = (x1 - x0) * k + 2 * pad
        self.h = (z1 - z0) * k + 2 * pad

    def pt(self, x, z):
        return (self.pad + (x - self.x0) * self.k, self.pad + (self.z1 - z) * self.k)

    def d(self, geom):
        parts = []
        polys = geom.geoms if hasattr(geom, "geoms") else [geom]
        for pg in polys:
            for ring in [pg.exterior, *pg.interiors]:
                cs = [self.pt(x, z) for x, z in ring.coords]
                parts.append("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in cs) + " Z")
        return " ".join(parts)

    def path(self, geom, cls, extra=""):
        return f'<path class="{cls}" d="{self.d(geom)}" {extra}/>'

    def line(self, a, b, cls="dim"):
        (x1, y1), (x2, y2) = self.pt(*a), self.pt(*b)
        return f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'

    def text(self, p, s, cls="lbl", dx=0, dy=0, anchor="start"):
        x, y = self.pt(*p)
        return f'<text class="{cls}" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}">{s}</text>'

    def circle(self, p, r_mm, cls):
        x, y = self.pt(*p)
        return f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r_mm * self.k:.1f}"/>'

    def svg(self, body, label):
        return (f'<svg viewBox="0 0 {self.w:.0f} {self.h:.0f}" width="{self.w:.0f}" height="{self.h:.0f}" role="img" aria-label="{label}">'
                + "".join(body) + "</svg>")


def side_view(theta):
    fr = frame(theta)
    swept, swung, body, cleat, lip, tip = socket_geometry(fr)
    handle = handle_env(fr)
    grip = P(fr, HANDLE_LEN, 0)
    v = View(1.55, -24, 196, -112, PLATE_H + 26)
    b = []
    b.append(v.path(Polygon([(-22, -112), (-PLATE_T, -112), (-PLATE_T, PLATE_H + 24), (-22, PLATE_H + 24)]), "wall"))
    b.append(v.path(Polygon([(-PLATE_T, 0), (0, 0), (0, PLATE_H), (-PLATE_T, PLATE_H)]), "plate"))
    ribs = Polygon([(0, SADDLE_Z - SADDLE_T - SADDLE_D), (SADDLE_D, SADDLE_Z - SADDLE_T), (0, SADDLE_Z - SADDLE_T)])
    b.append(v.path(ribs, "rib"))
    saddle = unary_union([Polygon([(0, SADDLE_Z - SADDLE_T), (SADDLE_D, SADDLE_Z - SADDLE_T), (SADDLE_D, SADDLE_Z), (0, SADDLE_Z)]),
                          Polygon([(SADDLE_D - 8, SADDLE_Z), (SADDLE_D, SADDLE_Z), (SADDLE_D, SADDLE_Z + LIP_H), (SADDLE_D - 8, SADDLE_Z + LIP_H)])])
    b.append(v.path(saddle, "body"))
    b.append(v.path(body, "body"))
    b.append(v.path(swept, "cavity"))
    b.append(v.path(cleat, "cleat"))
    b.append(v.path(swung, "swung"))
    b.append(v.path(handle, "nose"))
    b.append(v.path(nose_notched(fr), "noseline"))
    loops = Polygon([(SADDLE_D - 8 - CABLE_OD, SADDLE_Z), (SADDLE_D - 8, SADDLE_Z), (SADDLE_D - 8, SADDLE_Z - COIL_D), (SADDLE_D - 8 - CABLE_OD, SADDLE_Z - COIL_D)])
    b.append(v.path(loops, "coil"))
    c1 = grip + 35 * fr[0]
    end = np.array([SADDLE_D - 20, SADDLE_Z + CABLE_OD / 2])
    c2 = np.array([end[0] + 45, end[1] + 70])
    p0, p1, p2, p3 = (v.pt(*grip), v.pt(*c1), v.pt(*c2), v.pt(*end))
    b.append(f'<path class="cable" d="M{p0[0]:.1f} {p0[1]:.1f} C{p1[0]:.1f} {p1[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} {p3[0]:.1f} {p3[1]:.1f}"/>')
    b.append(v.circle((SADDLE_D - 8 - CABLE_OD / 2, SADDLE_Z + CABLE_OD / 2), CABLE_OD / 2, "cablesec"))
    for z in (15, 230):
        b.append(v.path(Polygon([(-PLATE_T - 1, z - 2.2), (1, z - 2.2), (1, z + 2.2), (-PLATE_T - 1, z + 2.2)]), "screw"))
    gx = grip[0]
    b.append(v.line((0, PLATE_H + 14), (gx, PLATE_H + 14)))
    b.append(v.text((gx / 2, PLATE_H + 14), f"grip end {gx:.0f} mm from the plate", dy=-4, anchor="middle"))
    xf = body.bounds[2]
    b.append(v.line((0, -8), (xf, -8)))
    b.append(v.text((xf / 2, -8), f"socket {xf:.0f} mm deep", dy=12, anchor="middle"))
    b.append(v.line((-PLATE_T - 12, 0), (-PLATE_T - 12, PLATE_H)))
    b.append(v.text((-PLATE_T - 12, PLATE_H / 2), f"{PLATE_H:.0f}", dx=-4, anchor="end"))
    b.append(v.text((SADDLE_D, SADDLE_Z + LIP_H), "cable saddle", dx=6, dy=-2))
    b.append(v.text((SADDLE_D - 8, SADDLE_Z - COIL_D / 2), f"{LOOPS} loops, edge on", dx=6))
    b.append(v.text((-PLATE_T - 6, -100), "wall", anchor="end"))
    b.append(v.text(tuple(P(fr, 12, HC + WALL_T + 6)), "socket", dx=6))
    b.append(v.text(tuple(P(fr, 110, HALF + 12)), "handle, docked", dx=4))
    b.append(v.text((gx + 6, grip[1] - 28), f"dashed: {SWING:.0f}&#176; tilt to insert", cls="lbl swunglbl"))
    return v.svg(b, f"side view at {theta} degrees")


def front_view():
    fr = frame(THETA)
    v = View(1.3, -170, 235, -112, PLATE_H + 26)
    b = []
    hw = PLATE_W / 2
    b.append(f'<rect class="plate" x="{v.pt(-hw, PLATE_H)[0]:.1f}" y="{v.pt(-hw, PLATE_H)[1]:.1f}" width="{PLATE_W * v.k:.1f}" height="{PLATE_H * v.k:.1f}" rx="{8 * v.k:.1f}"/>')
    for y in RIB_YS:
        b.append(v.path(Polygon([(y - 3, SADDLE_Z - SADDLE_T - SADDLE_D), (y + 3, SADDLE_Z - SADDLE_T - SADDLE_D), (y + 3, SADDLE_Z), (y - 3, SADDLE_Z)]), "rib"))
    ys = np.linspace(-SADDLE_W / 2, SADDLE_W / 2, 41)
    crown = [(y, SADDLE_Z - y * y / (2 * CROWN_R)) for y in ys]
    b.append(v.path(Polygon(crown + [(y, z - SADDLE_T) for y, z in reversed(crown)]), "body"))
    b.append(v.path(Polygon([(y, z + LIP_H) for y, z in crown] + [(y, z) for y, z in reversed(crown)]), "lip"))
    bw = HC + WALL_T
    z_block = P(fr, BACK_WALL, -HC)[1]
    b.append(v.path(Polygon([(-bw - 3, 0), (bw + 3, 0), (bw + 3, z_block), (-bw - 3, z_block)]), "body"))
    z_lip = P(fr, MOUTH, HC)[1]
    b.append(v.path(Polygon([(-HC, z_lip - 4), (HC, z_lip - 4), (HC, z_block), (-HC, z_block)]), "cavity"))
    z_grip = P(fr, HANDLE_LEN, 0)[1]
    b.append(f'<rect class="nose" x="{v.pt(-20.75, z_grip)[0]:.1f}" y="{v.pt(-20.75, z_grip)[1]:.1f}" width="{41.5 * v.k:.1f}" height="{(z_grip - z_lip + 6) * v.k:.1f}" rx="{6 * v.k:.1f}"/>')
    b.append(v.circle((0, z_grip - 12), CABLE_OD / 2, "cablesec"))
    for i in range(LOOPS):
        y = (i - (LOOPS - 1) / 2) * CABLE_OD
        b.append(v.circle((y, SADDLE_Z - COIL_D / 2), COIL_D / 2, "coilring"))
    for y in (-40, 40):
        b.append(v.circle((y, 230), 5, "screw"))
        b.append(v.path(Polygon([(y - 2.5, 220), (y + 2.5, 220), (y + 2.5, 230), (y - 2.5, 230)]), "screw"))
    for y in (-42, 42):
        b.append(v.circle((y, 15), 2.5, "screw"))
    b.append(v.line((-hw, -12), (hw, -12)))
    b.append(v.text((0, -12), f"{PLATE_W:.0f} mm wide, {PLATE_H:.0f} tall", dy=12, anchor="middle"))
    b.append(v.text((0, PLATE_H + 14), f"saddle {SADDLE_W:.0f} wide for {LOOPS} loops of {CABLE_OD} mm cable", anchor="middle"))
    b.append(v.text((-hw, 230), "keyhole slots", dx=-6, anchor="end"))
    b.append(v.text((-hw, 15), "screws", dx=-6, anchor="end"))
    b.append(v.text((COIL_D / 2 + 45, SADDLE_Z - COIL_D / 2), f"coil, &#216;{COIL_D:.0f} loops", dx=0))
    b.append(v.text((24, 110), "handle", dx=6))
    return v.svg(b, "front view")


def cleat_detail(pull_release):
    v = View(22, 13.5, 26.5, -HC - 1.6, -HALF + 5.4)
    a = NOTCH_A - NOTCH_D * math.tan(math.radians(0.5))
    bb = NOTCH_B + NOTCH_D * math.tan(math.radians(3))
    nose = Polygon([(13.5, -HALF + 5.4), (26.5, -HALF + 5.4), (26.5, -HALF), (bb, -HALF), (NOTCH_B, -HALF + NOTCH_D), (NOTCH_A, -HALF + NOTCH_D), (a, -HALF), (13.5, -HALF)])
    body = Polygon([(13.5, -HC), (26.5, -HC), (26.5, -HC - 1.6), (13.5, -HC - 1.6)])
    if pull_release:
        cleat = Polygon([(CLEAT_A, -HC), (CLEAT_B, -HC), (CLEAT_C, -HC + CLEAT_PROUD), (CLEAT_A + CLEAT_PROUD, -HC + CLEAT_PROUD)])
    else:
        cleat = Polygon([(CLEAT_A, -HC), (CLEAT_B, -HC), (CLEAT_C, -HC + CLEAT_PROUD), (CLEAT_A, -HC + CLEAT_PROUD)])
    b = [v.path(body, "body"), v.path(cleat, "cleat"), v.path(nose, "nose"), v.path(nose, "noseline")]
    b.append(v.line((NOTCH_A, -HALF + NOTCH_D + 0.6), (NOTCH_B, -HALF + NOTCH_D + 0.6)))
    b.append(v.text(((NOTCH_A + NOTCH_B) / 2, -HALF + NOTCH_D + 0.6), f"notch {NOTCH_B - NOTCH_A:.1f} long, {NOTCH_D:.2f} deep", dy=-4, anchor="middle"))
    b.append(v.line((NOTCH_A, -HC - 1.1), (CLEAT_A, -HC - 1.1)))
    b.append(v.text(((NOTCH_A + CLEAT_A) / 2, -HC - 1.1), f"{CLEAT_A - NOTCH_A:.2f}", dy=-3, anchor="middle"))
    b.append(v.line((CLEAT_B, -HC - 1.1), (NOTCH_B, -HC - 1.1)))
    b.append(v.text(((CLEAT_B + NOTCH_B) / 2, -HC - 1.1), f"{NOTCH_B - CLEAT_B:.2f}", dy=-3, anchor="middle"))
    b.append(v.line((CLEAT_A - 1.2, -HC), (CLEAT_A - 1.2, -HC + CLEAT_PROUD)))
    b.append(v.text((CLEAT_A - 1.2, -HC + CLEAT_PROUD / 2), f"{CLEAT_PROUD} proud", dx=-4, dy=4, anchor="end"))
    b.append(v.text((CLEAT_B, -HC + CLEAT_PROUD / 2), "45&#176; lead-in", dx=4, dy=4))
    b.append(v.text((23.9, -HALF + 2.0), "nose", dx=2))
    b.append(v.text((13.7, -HALF + 2.0), "tip side", dx=2))
    b.append(v.text((26.3, -HC - 1.25), "socket wall", anchor="end"))
    b.append(v.text((13.7, -HALF - 0.25), f"{CLEAR} gap", dx=2, dy=3))
    return v.svg(b, "cleat detail")


def cross_section():
    o = outline()
    oc = o.buffer(CLEAR, join_style=1)
    cav_notch = unary_union([oc, translate(oc, 0, (MOUTH - 20.25) * math.tan(math.radians(SWING)))]).convex_hull
    cav_floor = unary_union([oc, translate(oc, 0, FLOOR_RELIEF)]).convex_hull
    hm, hf = NOTCH_W_MOUTH / 2, NOTCH_W_FLOOR / 2
    notch = Polygon([(-hm, -HALF - 1), (hm, -HALF - 1), (hf, -HALF + NOTCH_D), (-hf, -HALF + NOTCH_D)])
    nose = o.difference(notch)
    cleat = Polygon([(-CLEAT_W / 2, -HC), (CLEAT_W / 2, -HC), (CLEAT_W / 2, -HC + CLEAT_PROUD), (-CLEAT_W / 2, -HC + CLEAT_PROUD)])
    v = View(4.6, -34, 34, -25, 33)
    b = [v.path(cav_floor, "cavfloor"), v.path(cav_notch, "cavity"), v.path(nose, "nose"), v.path(nose, "noseline"), v.path(cleat, "cleat")]
    b.append(v.text((0, HALF + FLOOR_RELIEF + 1), f"cavity at the floor: +{FLOOR_RELIEF:.1f} mm outward", dy=-4, anchor="middle"))
    b.append(v.text((0, HALF - 3), "cavity at the notch", anchor="middle", cls="lbl on"))
    b.append(v.text((0, 0), f"nose {o.bounds[2] - o.bounds[0]:.1f} x {o.bounds[3] - o.bounds[1]:.1f}", anchor="middle", cls="lbl on"))
    b.append(v.text((hm + 1, -HC + 1.2), f"cleat {CLEAT_W:.0f} wide", dy=3))
    b.append(v.text((-hm - 1, -HALF + 1.5), f"notch {NOTCH_W_FLOOR} wide", anchor="end"))
    b.append(v.text((0, -HC - 4), "wall side", anchor="middle"))
    b.append(v.text((0, HALF + FLOOR_RELIEF + 6.5), "button side, away from the wall", dy=-4, anchor="middle"))
    return v.svg(b, "cross section")


def numbers(theta):
    fr = frame(theta)
    _, _, body, _, _, _ = socket_geometry(fr)
    grip = P(fr, HANDLE_LEN, 0)
    lipx = P(fr, MOUTH, HC + WALL_T)[0]
    wedge = (CG_FROM_TIP - MOUTH) * math.sin(math.radians(theta)) / (MOUTH - 8)
    return dict(theta=theta, grip=grip[0], grip_z=grip[1], mouth=lipx, front=body.bounds[2], wedge=wedge,
                tilt_move=(HANDLE_LEN - MOUTH) * math.sin(math.radians(SWING)))


def main():
    sides = "".join(f'<div class="side" data-theta="{t}" {"" if t == THETA else "hidden"}>{side_view(t)}</div>' for t in THETAS)
    rows = "".join(
        f"<tr><td>{n['theta']}&#176;</td><td>{n['grip']:.0f}</td><td>{n['grip_z']:.0f}</td><td>{n['front']:.0f}</td><td>{n['wedge']:.2f} W</td><td>{n['tilt_move']:.0f}</td></tr>"
        for n in (numbers(t) for t in THETAS))
    radios = "".join(f'<label><input type="radio" name="theta" id="theta{t}" value="{t}" {"checked" if t == THETA else ""}> {t}&#176;</label>' for t in THETAS)
    html = f"""<title>NACS Holster Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#f6f4ef;--ink:#1f2a33;--muted:#5d6b76;--rule:#d7d2c7;--body:#c9c3b6;--body-ink:#7a7262;--cavity:#f6f4ef;--nose:#9fc3dc;--nose-ink:#2c6a94;--cleat:#d9772b;--coil:#e0d8c4;--accent:#b8541c;--wall:#e6e1d6;--card:#fbfaf7}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#171a1d;--ink:#e8e4dc;--muted:#a19b90;--rule:#3a3f45;--body:#5a5f66;--body-ink:#c7cbd1;--cavity:#171a1d;--nose:#3f7ca3;--nose-ink:#a9d3ee;--cleat:#e8863a;--coil:#3a3a35;--accent:#e8863a;--wall:#24282c;--card:#1f2327}}}}
:root[data-theme="dark"]{{--bg:#171a1d;--ink:#e8e4dc;--muted:#a19b90;--rule:#3a3f45;--body:#5a5f66;--body-ink:#c7cbd1;--cavity:#171a1d;--nose:#3f7ca3;--nose-ink:#a9d3ee;--cleat:#e8863a;--coil:#3a3a35;--accent:#e8863a;--wall:#24282c;--card:#1f2327}}
body{{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.5;margin:0;padding-block:24px 48px;padding-inline:20px}}
main{{max-width:1100px;margin:0 auto}}
h1{{font-size:1.9rem;font-weight:600;margin:0 0 4px;text-wrap:balance}}
h2{{font-size:1.15rem;font-weight:600;margin:36px 0 10px;padding-top:14px;border-top:1px solid var(--rule)}}
p{{max-width:68ch;margin:6px 0}}
.lead{{color:var(--muted)}}
.row{{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start}} .row>figure{{flex:0 1 auto;min-width:0}}
figure{{margin:0;background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:10px;overflow-x:auto;max-width:100%}}
figcaption{{font-size:.85rem;color:var(--muted);margin-top:6px;max-width:60ch}}
svg{{display:block;max-width:100%;height:auto}}
.wall{{fill:var(--wall)}} .plate{{fill:var(--body);stroke:var(--body-ink);stroke-width:1}}
.body{{fill:var(--body);stroke:var(--body-ink);stroke-width:1;fill-rule:evenodd}} .rib{{fill:var(--body);opacity:.55}}
.lip{{fill:var(--body);stroke:var(--body-ink);stroke-width:1;opacity:.85}}
.cavity{{fill:var(--cavity);stroke:var(--body-ink);stroke-width:1;fill-rule:evenodd}} .cavfloor{{fill:none;stroke:var(--body-ink);stroke-width:1;stroke-dasharray:4 3}}
.nose{{fill:var(--nose);stroke:none;opacity:.9}} .noseline{{fill:none;stroke:var(--nose-ink);stroke-width:1.2}}
.swung{{fill:none;stroke:var(--nose-ink);stroke-width:1;stroke-dasharray:5 4;opacity:.8}}
.cleat{{fill:var(--cleat);stroke:none}} .coil{{fill:var(--coil);opacity:.8}} .coilring{{fill:none;stroke:var(--body-ink);stroke-width:1;opacity:.5}}
.cable{{fill:none;stroke:var(--ink);stroke-width:3;opacity:.6;stroke-linecap:round}} .cablesec{{fill:var(--coil);stroke:var(--ink);stroke-width:1}}
.screw{{fill:var(--bg);stroke:var(--body-ink);stroke-width:1}}
.dim{{stroke:var(--muted);stroke-width:.8}} .lbl{{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11px;fill:var(--muted)}} .lbl.on{{fill:var(--ink)}}
.swunglbl{{fill:var(--nose-ink)}}
table{{border-collapse:collapse;font-variant-numeric:tabular-nums;font-size:.92rem}} th,td{{text-align:right;padding:6px 12px;border-bottom:1px solid var(--rule)}} th:first-child,td:first-child{{text-align:left}}
th{{font-weight:500;color:var(--muted);letter-spacing:.02em}}
.opts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}
.opt{{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:12px 14px}}
.opt h3{{margin:0 0 6px;font-size:1rem;font-weight:600}} .opt p{{font-size:.92rem}}
.pick{{color:var(--accent);font-weight:500}}
.radios{{display:flex;gap:16px;margin:8px 0 12px;font-size:.95rem}} .radios label{{cursor:pointer}}
ul{{padding-left:20px;max-width:68ch}} li{{margin:4px 0}}
.src{{font-size:.85rem;color:var(--muted)}}
</style>
<main>
<h1>NACS Holster Plan</h1>
<p class="lead">Wall dock for the Tesla Gen 3 Wall Connector handle: nose down, held by a fixed cleat in the connector's own lock notch, with a saddle for the {CABLE_LEN / 1000:.1f} m cable. Every drawing is to scale from Tesla's NACS spec and STEP model.</p>

<h2>1. The unit</h2>
<div class="radios">Socket angle from vertical: {radios}</div>
<div class="row">
<figure>{sides}<figcaption>Side view, section through the middle. Blue is the handle docked; the dashed outline is the tilt you use to lift the nose over the cleat (orange). The handle beyond the bell is drawn as an envelope: Tesla's CAD stops at the bell.</figcaption></figure>
<figure>{front_view()}<figcaption>Front view. The saddle is crowned so the loops spread out and self-center; the loops hang around the docked handle, and the last loop runs down to the grip.</figcaption></figure>
</div>

<h2>2. How it holds</h2>
<p>The nose slides down a socket that fits it to {CLEAR} mm on three sides. On the wall side sits a fixed {CLEAT_W:.0f} mm wide cleat, {CLEAT_PROUD} mm proud, placed where the car's lock pin goes. The socket's open side is relieved into a wedge, {FLOOR_RELIEF:.1f} mm wider at the floor, so you can tilt the grip {SWING:.0f}&#176; toward the wall and lower the nose past the cleat. Let go and the handle's own weight levers the tip against the wall side (about {numbers(THETA)['wedge']:.1f} times the handle weight at {THETA}&#176;), which drops the cleat into the notch. The tip rests on the floor; the cleat only blocks a pull straight out.</p>
<div class="row">
<figure>{cleat_detail(False)}<figcaption>Cleat and notch, 22:1. Square face toward the tip blocks pull-out; the 45&#176; face toward the mouth is the lead-in. Axial slack {CLEAT_A - NOTCH_A:.1f} and {NOTCH_B - CLEAT_B:.1f} mm covers the spec tolerances (&#177;0.2) and print error.</figcaption></figure>
<figure>{cross_section()}<figcaption>Looking down the socket. The cleat sits in the {NOTCH_W_FLOOR} mm notch with room on both sides; the cavity is the nose profile plus {CLEAR} mm, stretched outward toward the floor.</figcaption></figure>
</div>

<h2>3. Numbers by socket angle</h2>
<table><thead><tr><th>angle</th><th>grip end from plate, mm</th><th>grip end height, mm</th><th>socket depth from plate, mm</th><th>force holding the cleat in</th><th>grip moves for the tilt, mm</th></tr></thead><tbody>{rows}</tbody></table>
<p class="src">Force uses the handle's weight W with its balance point about {CG_FROM_TIP:.0f} mm from the tip (not published). Steeper is more compact; flatter holds harder and sticks out more.</p>

<h2>4. Your calls</h2>
<div class="opts">
<div class="opt"><h3>Socket angle</h3><p><span class="pick">25&#176;</span> is drawn. 20&#176; is more compact and holds a little less; 30&#176; sticks out {numbers(30)['grip'] - numbers(25)['grip']:.0f} mm more.</p></div>
<div class="opt"><h3>Releasing the handle</h3><p><span class="pick">Tilt and lift</span> is drawn: the square cleat face means a straight pull is blocked, so a bump or the cable's weight cannot unseat it. The alternative is a 45&#176; face on both sides, so a firm straight pull cams the nose out.</p></div>
<div class="opt"><h3>One piece or two</h3><p><span class="pick">One piece</span>, {PLATE_W:.0f} &#215; {PLATE_H:.0f} mm, prints standing up (well inside the 260 mm height) with a brim. Two pieces (socket and saddle on their own plates) print flat and let you put the saddle anywhere, for instance above the Wall Connector.</p></div>
<div class="opt"><h3>Saddle</h3><p>{SADDLE_W:.0f} mm wide for {LOOPS} side-by-side loops of &#216;{COIL_D:.0f} mm, {SADDLE_D:.0f} mm deep, on four 45&#176; ribs so it prints without support. Say if you coil larger or want it deeper.</p></div>
</div>

<h2>5. Build and print</h2>
<ul>
<li>build123d from this page's constants; the nose profile comes from Tesla's STEP, so the cavity is the real shape.</li>
<li>Material PETG (holds the wedge load, no creep in a warm garage), 0.6 mm high-flow nozzle, 0.30 mm layers, 4 walls, with the Sharks PETG settings.</li>
<li>Printed standing on the plate's bottom edge and the socket block: every overhang is under 30&#176;, the saddle rides on its ribs.</li>
<li>First print: a 20 mm tall coupon of the socket floor, cleat and notch region to check the fit on the real handle before the full part.</li>
</ul>
<p class="src">Sources: Tesla TS-0023666 rev 1.1 (nose length 32.49 p14, lock pocket p25, pin p24), Tesla 48A AC connector datasheet (handle 41.5 &#215; 35.1 &#215; 194.5, cable &#216;14.5, under 90 N), Tesla NACS-500V-Connector-and-Inlet.stp (nose profile, notch 17.13 to 23.35 from the tip).</p>
</main>
<script>
document.querySelectorAll('input[name="theta"]').forEach(function (r) {{
  r.addEventListener('change', function () {{
    document.querySelectorAll('.side').forEach(function (d) {{ d.hidden = d.dataset.theta !== r.value; }});
  }});
}});
</script>
"""
    out = os.path.join(HERE, "plan.html")
    with open(out, "w") as f:
        f.write(html)
    print(out, f"swing {SWING:.1f} deg, floor relief {FLOOR_RELIEF:.1f} mm, loops {LOOPS}")
    for t in THETAS:
        print({k: round(float(x), 1) for k, x in numbers(t).items()})


if __name__ == "__main__":
    main()
