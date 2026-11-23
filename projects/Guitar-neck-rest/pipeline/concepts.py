#!/usr/bin/env python
"""Concept geometry, renders and to-scale drawings for the guitar neck rest options page.

One parameter set (below) drives everything: it is written to params.scad, which concepts.scad
includes, and the matplotlib drawings read the same numbers. Outputs:
  pipeline/params.scad            the parameter set as OpenSCAD sees it
  images/concepts/<x>-shape.png   OpenSCAD picture of each concept, bare, on a 1 in grid
  images/concepts/<x>-use.png     the same with a neck stand-in on it
  images/concepts/<x>-extra.png   other height, parts apart, or the range
  images/concepts/<v>-pad-<m>.png the rocker close up with a cork, felt or TPU pad and tread (v = PAD_SHOWN)
  images/concepts/c1r-end.png     the kept body: one rounded-over cradle end close up
  images/concepts/end-section.png the same end cut through the middle, to scale, over the square end it replaces
  images/concepts/side-<v>.png    round 3: side view cut through each longer-cradle body, over the round 2 body dashed
  images/concepts/roll-empty.png  round 2: side view cut through the rocker, sitting empty
  images/concepts/roll-bass.png   round 2: the same, rolled under the bass
  images/concepts/fit.png         cross-section: the cradle with a bass and a guitar neck in it
  images/concepts/use.png         side elevation: what each rest height does to the instrument
  concepts/<part>.stl             concept solids in their print orientation (for the slice quotes)
  concepts-report.json            sizes, volumes, watertight flags, derived numbers

Run from the vault root:
  .venv/bin/python projects/Guitar-neck-rest/pipeline/concepts.py [--no-render] [--no-stl]
"""
import json
import math
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.patches import Polygon as MplPolygon
from shapely import affinity
from shapely.geometry import Point as ShPoint
from shapely.geometry import Polygon as ShPolygon
from shapely.geometry import box

VAULT = Path(__file__).resolve().parents[3]
PROJECT = VAULT / "projects" / "Guitar-neck-rest"
PIPE = PROJECT / "pipeline"
IMAGES = PROJECT / "images" / "concepts"
STLS = PROJECT / "concepts"
OPENSCAD = Path.home() / ".local/bin/openscad"
IN = 25.4

# ---- rest heights: bench to the back of the neck (inches) ---------------------------------
# Commercial solid-body rests run 2.6 to 4.2 in, acoustic ones 5 to 6.2 in (brief.md, research).
LOW = 2.5
HIGH = 3.75
TALL = 5.0
FLAT = 1.25          # neck back above the bench with a Fender-style body lying flat (estimate, see brief)

# ---- cradle (mm) ----------------------------------------------------------------------------
CW = 64.0            # cradle width at the rim, 2.5 in: commercial cradles are 2-3/8 to 2-1/2
CR = 45.3            # cradle radius: the rim tangent is 45 degrees, so the groove prints on a vertical wall
PAD_T = 2.0          # room left for a stick-on pad (cork or felt)
RR = 130.0           # rocker radius: more than the cradle height, so a loaded rocker rights itself
X_REST = 95.0        # rest centre, measured from the nut: between the 2nd and 3rd fret of a bass
C_WIDTH = 80.0       # rocker width across the neck: the cradle's groove plus a 5 mm shoulder each side

# ---- neck stand-ins (inches): nut width, width at fret 12, depth at fret 1, depth at fret 12, scale
NECKS = {
    # Width at 12 for the bass is interpolated from the 1.625 nut to the 2.5 heel, not a published figure.
    "bass": dict(w0=1.625, w1=2.20, d0=0.94, d1=0.99, scale=34.0, label="P-Bass stand-in"),
    "guitar": dict(w0=1.650, w1=2.075, d0=0.82, d1=0.87, scale=25.5, label="Strat stand-in"),
}
NECK_DRAW = 235.0    # how much neck the pictures show past the nut
HEAD_STUB = 45.0
TAIL_TO_NUT = 36.5   # bass, tail of the body to the nut (34 in scale plus an estimated 2.5 behind the bridge)
TAIL_TO_NUT_GUITAR = 31.5   # Strat-size stand-in: about 39 in overall less a 7.5 in headstock (estimate)
NECK_LOAD_KG = 1.6   # weight the rest carries: a 4 kg bass balanced near the neck joint (estimate)
BB_G_CM3 = 4.8       # steel BBs, loose: 7.85 g/cm3 at about 61% packing (estimate)
SAND_G_CM3 = 1.6     # dry sand (estimate)
BODY_T = 1.75
BODY_L = 20.0        # stand-in body length for the side elevation only
HEAD_L = 8.5         # stand-in headstock length for the side elevation only

F_LIFT = 20.0        # the pedestal's head is drawn this far above its lowest position (mm)

# ---- round 3: the open frame (c1) with a longer cradle ---------------------------------------
# Brian, 2026-11-22: "longer surface area for the neck to sit on, and the bottom rocker can either stay the same or
# even get smaller". Cradle length in inches, chord of the rocking arc in mm (150 is the round 2 rocker).
LONG = {
    "c1a": dict(top=6.0, chord=150.0),
    "c1b": dict(top=8.0, chord=150.0),
    "c1c": dict(top=8.0, chord=4.0 * IN),
}
REST_START = 19.0    # a long cradle is drawn starting 3/4 in from the nut, clear of the headstock and the tuners
# ---- the kept body with its edges rounded over ------------------------------------------------
# Brian, 2026-11-23: "the front and back edges closest to the neck should be rounded over" (the two cradle ends,
# confirmed by a question) and "all edges should have a slight roundover". The radii live in concepts.scad (R_END,
# R_EDGE) with the rest of the rocker's construction; c1r is c1 with them applied.
PAD_SHOWN = "c1r"    # the body the pad material pictures are drawn on (Brian kept round 2's C1, 2026-11-22)

CONCEPTS = ["a", "b", "c", "d", "e", "f", "c1", "c2", "c3", *LONG, "c1r"]
PARTS = ["a", "b", "c", "d_base", "d_cradle", "e", "f_base", "f_head", "c1", "c2", "c2_lid", "c3", *LONG, "c1r"]
PAD_MATERIALS = ["cork", "felt", "tpu"]
# camera per picture: look-at point (mm), rot_x, rot_z, distance. One distance per view, so the concepts compare in size.
CAMERA = {
    "shape": ((0, 0, 44), 68, 32, 620),
    "use": ((45, 0, 55), 70, 30, 800),
    "extra": ((0, 0, 44), 68, 32, 620),
    "pad": ((0, 0, 62), 58, 32, 470),
    "end": ((52, 0, 96), 62, 58, 250),
}
CAMERA_OVERRIDE = {
    ("a", "extra"): ((45, 0, 45), 70, 30, 800),
    ("d", "extra"): ((0, 0, 68), 68, 32, 700),
    ("b", "extra"): ((0, 0, 55), 66, 32, 900),
    ("f", "extra"): ((0, 0, 45), 68, 32, 700),
    ("e", "shape"): ((0, 0, 20), 62, 32, 680),
    ("e", "use"): ((45, 0, 25), 64, 30, 800),
    ("c2", "extra"): ((0, -25, 44), 68, 32, 660),
    ("c3", "extra"): ((45, 0, 45), 70, 30, 800),
    **{(k, "shape"): ((0, 0, 50), 68, 32, 640) for k in LONG},
    **{(k, "use"): ((20, 0, 58), 70, 30, 860) for k in LONG},
    **{(k, "pad"): ((0, 0, 58), 58, 32, 640) for k in LONG},
}
VIEWS = {"a": ("shape", "use", "extra"), "b": ("shape", "use", "extra"), "c": ("shape", "use"),
         "d": ("shape", "use", "extra"), "e": ("shape", "use"), "f": ("shape", "use", "extra"),
         "c1": ("shape", "use", "extra"), "c2": ("shape", "use", "extra"), "c3": ("shape", "use", "extra"),
         **{k: ("shape", "use") for k in LONG}, "c1r": ("shape", "use", "extra", "end")}


def frac(x_in, den=8):
    """Inches as a mixed fraction to the nearest 1/den: 3.75 -> 3-3/4."""
    f = Fraction(round(x_in * den), den)
    whole, rest = divmod(f, 1)
    return f"{whole}" if rest == 0 else (f"{whole}-{rest}" if whole else f"{rest}")


def tilt_deg(h_in, x_rest_in=X_REST / IN, tail=TAIL_TO_NUT):
    """Pitch of the instrument when the rest holds the neck back at h_in and the body's tail edge is on the bench."""
    return math.degrees(math.asin((h_in - FLAT) / (tail - x_rest_in)))


CD_MM = CR - math.sqrt(CR ** 2 - CW ** 2 / 4)          # cradle depth
C3_LOW_IN = (C_WIDTH - CD_MM) / IN                     # neck height on the two-way rocker's fixed side cradle
C3_SLOPES = {"bass": tilt_deg(C3_LOW_IN), "guitar": tilt_deg(C3_LOW_IN, tail=TAIL_TO_NUT_GUITAR)}
C3_SLOPE = sum(C3_SLOPES.values()) / 2                 # built into the fixed cradle: midway between the two


def frets(scale_in, n=12):
    return [scale_in * IN * (1 - 2 ** (-k / 12)) for k in range(1, n + 1)]


def long_rest(v):
    """Centre of a long cradle, mm from the nut."""
    return REST_START + v["top"] * IN / 2


def write_params(neck="bass", f_tilt_h=None):
    n = NECKS[neck]
    f_h = f_tilt_h if f_tilt_h is not None else HIGH
    lines = [
        "// Written by concepts.py. Do not edit: change the parameter set there.",
        f"IN = {IN};",
        f"LOW = {LOW * IN}; HIGH = {HIGH * IN}; TALL = {TALL * IN}; FLAT = {FLAT * IN};",
        f"CW = {CW}; CR = {CR}; PAD_T = {PAD_T}; RR = {RR}; X_REST = {X_REST};",
        f"NECK_W0 = {n['w0'] * IN}; NECK_W1 = {n['w1'] * IN}; NECK_D0 = {n['d0'] * IN}; NECK_D1 = {n['d1'] * IN};",
        f"NECK_L12 = {n['scale'] * IN / 2}; NECK_DRAW = {NECK_DRAW}; HEAD_STUB = {HEAD_STUB};",
        f"FRETS = {[round(x, 2) for x in frets(n['scale'])]};",
        f"TILT_LOW = {tilt_deg(LOW):.3f}; TILT_HIGH = {tilt_deg(HIGH):.3f}; TILT_TALL = {tilt_deg(TALL):.3f};",
        f"F_LIFT = {F_LIFT}; TILT_F = {tilt_deg(f_h):.3f};",
        f"YC = {C_WIDTH}; C3_SLOPE = {C3_SLOPE:.3f};",
        "LONG = [" + ", ".join(f'["{k}", {v["top"] * IN}, {v["chord"] / 2}, {long_rest(v):.2f}, {tilt_deg(HIGH, long_rest(v) / IN):.3f}]'
                               for k, v in LONG.items()) + "];",
    ]
    (PIPE / "params.scad").write_text("\n".join(lines) + "\n")


def openscad(args, name):
    r = subprocess.run([str(OPENSCAD), "--backend=Manifold", *args, str(PIPE / "concepts.scad")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit(f"openscad failed on {name}")
    return r.stderr


def derived():
    """The numbers concepts.scad derives (block sizes, pedestal range), read back from its echo."""
    out = openscad(["-D", 'MODE="part"', "-D", 'PART="none"', "-o", str(STLS / "_probe.echo")], "probe")
    text = (STLS / "_probe.echo").read_text() + out
    (STLS / "_probe.echo").unlink(missing_ok=True)
    m = re.search(r"DERIVED (.*?)\"", text)
    assert m, f"no DERIVED echo in:\n{text[-800:]}"
    return {k: float(v) for k, v in (kv.split("=") for kv in m.group(1).split())}


def export_stls(d):
    # print orientation back to standing: which way the STL's y runs up the standing rocker, and its offset
    Z_UP = {"c1": (-1, 0.0), "c2": (1, 0.0), "c3": (1, d["C3_ZS"]), **{k: (-1, 0.0) for k in LONG}, "c1r": (-1, 0.0)}
    report = {}
    for part in PARTS:
        stl = STLS / f"{part}.stl"
        openscad(["--export-format", "binstl", "-D", 'MODE="part"', "-D", f'PART="{part}"', "-o", str(stl)], part)
        mesh = trimesh.load(stl)
        size = mesh.extents
        assert mesh.is_watertight, f"{part}: STL is not watertight"
        assert abs(mesh.bounds[0][2]) < 0.01, f"{part}: does not sit on z = 0 (min z {mesh.bounds[0][2]:.3f})"
        assert len(mesh.split(only_watertight=False)) == 1, f"{part}: more than one solid"
        report[part] = {"size_mm": [round(float(s), 1) for s in size], "volume_cm3": round(float(mesh.volume) / 1000, 1)}
        if part in Z_UP:   # height of the centre of mass with the rocker standing (solid treated as uniform)
            sign, off = Z_UP[part]
            report[part]["cm_height_mm"] = round(sign * float(mesh.center_mass[1]) + off, 1)
        if part == "c1r":   # the solid itself, cut through the middle: level floor, then the roundover the drawings show
            r, xt, floor = d["R_END"], d["C1R_FLAT"] / 2, HIGH * IN - PAD_T
            mid = (math.pi / 2 + math.radians(d["C_LEAN"])) / 2
            # a ray dropped onto the centre plane from above the cradle (the standing rocker's up is the STL's -y)
            top_at = lambda x: -float(mesh.ray.intersects_location([[x, -300, C_WIDTH / 2]], [[0, 1, 0]])[0][:, 1].min())
            got = {"floor": top_at(xt - 2), "arc": top_at(xt + r * math.cos(mid))}
            want = {"floor": floor, "arc": floor - r + r * math.sin(mid)}
            assert all(abs(got[k] - want[k]) < 0.05 for k in got), f"c1r roundover: {got} against {want}"
            report[part]["roundover_check_mm"] = {k: [round(got[k], 2), round(want[k], 2)] for k in got}
        print(f"{part}: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm, {mesh.volume / 1000:.1f} cm3, watertight")
    return report


def render(concept, view, neck="bass", padmat="cork"):
    out = IMAGES / (f"{concept}-{view}-{padmat}.png" if view == "pad" else f"{concept}-{view}.png")
    (cx, cy, cz), rx, rz, dist = CAMERA_OVERRIDE.get((concept, view), CAMERA[view])
    openscad(["--preview", f"--camera={cx},{cy},{cz},{rx},0,{rz},{dist}", "--projection=p",
              "--colorscheme=Tomorrow", "--imgsize=1500,1000",
              "-D", 'MODE="scene"', "-D", f'PART="{concept}"', "-D", f'VIEW="{view}"', "-D", f'NECK="{neck}"',
              "-D", f'PADMAT="{padmat}"', "-o", str(out)], out.stem)
    return out


# ---------------------------------------------------------------- drawings
INK = "#1f2430"
MUTED = "#6b7280"
PRINT = "#4f83e6"
PADC = "#c9a26b"
WOOD = "#e6c992"
BOARD = "#4b3023"
ACCENT = "#d9480f"


def neck_outline(w, d, n=60):
    """Neck cross-section, back lowest point at (0, 0): half-ellipse back under a 1/4 in fretboard (mm)."""
    fb = 6.35
    t = np.linspace(math.pi, 2 * math.pi, n)
    back = np.column_stack([w / 2 * np.cos(t), (d - fb) + (d - fb) * np.sin(t)])
    return np.vstack([back, [w / 2, d], [-w / 2, d]])


def neck_at(neck, x_mm):
    n = NECKS[neck]
    f = x_mm / (n["scale"] * IN / 2)
    return (n["w0"] + (n["w1"] - n["w0"]) * f) * IN, (n["d0"] + (n["d1"] - n["d0"]) * f) * IN


def fig_fit():
    cd = CR - math.sqrt(CR ** 2 - CW ** 2 / 4)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), dpi=150)
    for ax, neck in zip(axes, ("bass", "guitar")):
        n = NECKS[neck]
        gr = CR + PAD_T
        gw = math.sqrt(gr ** 2 - (CR - cd) ** 2)
        y = np.linspace(-gw, gw, 120)
        body_top = CR - np.sqrt(gr ** 2 - y ** 2)
        blk = np.vstack([np.column_stack([y, body_top]), [gw + 4, cd], [gw + 4, -14], [-gw - 4, -14], [-gw - 4, cd]])
        ax.add_patch(MplPolygon(blk, closed=True, fc=PRINT, ec="#2b4f9e", lw=1.2))
        yp = np.linspace(-CW / 2 + 1, CW / 2 - 1, 120)
        pad_in = CR - np.sqrt(CR ** 2 - yp ** 2)
        pad_out = CR - np.sqrt(gr ** 2 - yp ** 2)
        ax.add_patch(MplPolygon(np.vstack([np.column_stack([yp, pad_in]), np.column_stack([yp[::-1], pad_out[::-1]])]),
                                closed=True, fc=PADC, ec="#8a6a3c", lw=0.8))
        w12, d12 = neck_at(neck, n["scale"] * IN / 2)
        ax.add_patch(MplPolygon(neck_outline(w12, d12), closed=True, fc="none", ec=MUTED, lw=1.3, ls="--"))
        w, d = neck_at(neck, X_REST)
        o = neck_outline(w, d)
        ax.add_patch(MplPolygon(o, closed=True, fc=WOOD, ec="#8a6a3c", lw=1.2))
        ax.add_patch(MplPolygon([[-w / 2, d - 6.35], [w / 2, d - 6.35], [w / 2, d], [-w / 2, d]], closed=True, fc=BOARD, ec=BOARD))
        ax.annotate("", xy=(-CW / 2, -19), xytext=(CW / 2, -19), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
        for sx in (-CW / 2, CW / 2):
            ax.plot([sx, sx], [-21, -15], color=INK, lw=0.8)
        ax.text(0, d12 + 4.5, f"{n['label']}: {w / IN:.2f} in wide where the rest sits,\n{w12 / IN:.2f} in at the 12th fret (dashed)",
                ha="center", va="bottom", fontsize=9.5, color=INK)
        ax.text(0, -21, f"cradle {CW / IN:.1f} in wide", ha="center", va="top", fontsize=9, color=INK)
        ax.text(0, -9, "printed body", ha="center", va="center", fontsize=9, color="white")
        ax.annotate("pad", xy=(CW / 2 - 6, CR - math.sqrt(CR ** 2 - (CW / 2 - 6) ** 2) - 1), xytext=(gw + 12, 2),
                    fontsize=9, color=INK, arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
        ax.set_xlim(-58, 62)
        ax.set_ylim(-27, 44)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(IMAGES / "fit.png", facecolor="white")
    plt.close(fig)


def fig_use():
    """Side elevation of the bass stand-in at each rest height, drawn to scale (inches). Headstock to the left, as in the 3D pictures."""
    rows = [("Lying flat, a long trough under the neck (shape E)", FLAT), (f"Rest at {LOW:g} in", LOW), (f"Rest at {HIGH:g} in", HIGH)]
    fig, axes = plt.subplots(len(rows), 1, figsize=(11, 6.6), dpi=150, gridspec_kw=dict(height_ratios=[4.6, 5.6, 7.2]))
    xr = TAIL_TO_NUT - X_REST / IN
    n = NECKS["bass"]
    out = {}
    for ax, (title, h), top_y in zip(axes, rows, (4.6, 5.6, 7.2)):
        t = math.radians(tilt_deg(h))
        rot = lambda p: (p[0] * math.cos(t) - p[1] * math.sin(t), p[0] * math.sin(t) + p[1] * math.cos(t))   # about the tail's bottom edge
        poly = lambda pts, **kw: ax.add_patch(MplPolygon([rot(p) for p in pts], closed=True, **kw))
        ax.plot([-3, 50], [0, 0], color=INK, lw=1.4)
        poly([(0, 0), (BODY_L, 0), (BODY_L, BODY_T), (0, BODY_T)], fc="#b9c2cf", ec=INK, lw=1)
        top = FLAT + n["d0"]
        poly([(BODY_L - 4, FLAT), (TAIL_TO_NUT, FLAT), (TAIL_TO_NUT, top), (BODY_L - 4, top + 0.05)], fc=WOOD, ec="#8a6a3c", lw=1)
        poly([(BODY_L - 4, top - 0.25), (TAIL_TO_NUT, top - 0.25), (TAIL_TO_NUT, top), (BODY_L - 4, top + 0.05)], fc=BOARD, ec=BOARD, lw=0.5)
        hs0, hs1 = FLAT + 0.19, FLAT + 0.19 + 0.57
        poly([(TAIL_TO_NUT, hs0), (TAIL_TO_NUT + HEAD_L, hs0), (TAIL_TO_NUT + HEAD_L, hs1), (TAIL_TO_NUT, hs1)], fc=WOOD, ec="#8a6a3c", lw=1)
        cx, cz = rot((xr, FLAT))
        half = 1.9 if h > FLAT + 1e-6 else 4.5
        ax.add_patch(MplPolygon([(cx - half, 0), (cx + half, 0), (cx + half, cz), (cx - half, cz)], closed=True, fc=PRINT, ec="#2b4f9e", lw=1))
        if h > FLAT + 1e-6:
            ax.annotate("", xy=(cx - 2.8, 0), xytext=(cx - 2.8, cz), arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.2))
            ax.text(cx - 3.1, cz / 2, f"{h:g} in", color=ACCENT, fontsize=10, va="center", ha="left")
        tip = rot((TAIL_TO_NUT + HEAD_L, hs0))
        ax.annotate("", xy=(tip[0] + 0.6, 0), xytext=(tip[0] + 0.6, tip[1]), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
        ax.text(tip[0] + 0.9, tip[1] / 2, f"{tip[1]:.1f} in under\nthe headstock", fontsize=9, va="center", ha="right", color=INK)
        ax.text(51.5, top_y - 0.1, title, fontsize=11, weight="bold", color=INK, va="top", ha="left")
        ax.text(51.5, top_y - 1.0, "body flat on the bench, neck level" if h <= FLAT + 1e-6 else
                f"body rides on its tail edge, instrument pitched {math.degrees(t):.1f} degrees", fontsize=9.5, color=MUTED, va="top", ha="left")
        ax.set_xlim(52, -3)        # reversed: headstock on the left
        ax.set_ylim(-0.3, top_y)
        ax.set_aspect("equal")
        ax.axis("off")
        out[f"{h:g}"] = {"tilt_deg": round(math.degrees(t), 2), "under_headstock_in": round(tip[1], 2)}
    fig.tight_layout()
    fig.savefig(IMAGES / "use.png", facecolor="white")
    plt.close(fig)
    return out


# ---------------------------------------------------------------- round 2: the rocker
def rocker_numbers(d):
    """What the rocker does under each instrument, and the sizes of the round 2 options."""
    dz = RR - HIGH * IN                    # the neck line sits this far below the centre of the rocking curve
    out = {"neck_line_below_centre_mm": round(dz, 2), "neck_load_kg": NECK_LOAD_KG, "radius_mm": RR,
           "guitar_tail_to_nut_in": TAIL_TO_NUT_GUITAR, "instruments": {}}
    for name, tail in (("bass", TAIL_TO_NUT), ("guitar", TAIL_TO_NUT_GUITAR)):
        t = math.radians(tilt_deg(HIGH, tail=tail))
        out["instruments"][name] = {
            "roll_deg": round(math.degrees(t), 2),
            "bench_contact_moves_mm": round(RR * t, 1),
            # a weightless rocker is in balance when the neck's push passes through the bench contact
            "load_off_pad_middle_mm": round(dz * math.sin(t), 2),
            "level_cradle_gap_mm": round(d["XC_TOP"] * math.tan(t), 1),
        }
    tb = math.radians(C3_SLOPES["bass"])   # room under the headstock, the same stand-in fig_use() draws
    out["fixed_side"] = {"height_in": round(C3_LOW_IN, 3), "slope_deg": round(C3_SLOPE, 2),
                         "pitch_deg": {k: round(v, 2) for k, v in C3_SLOPES.items()},
                         "under_headstock_in": round((TAIL_TO_NUT + HEAD_L) * math.sin(tb) + (FLAT + 0.19) * math.cos(tb), 2)}
    vol = d["C2_VOL"]
    out["ballast"] = {"pocket_cm3": round(vol), "steel_bb_g": round(vol * BB_G_CM3), "sand_g": round(vol * SAND_G_CM3),
                      "centre_height_mm": 30.0}
    return out


def rocker_section(d, top=None, half=None, deck=0.0, r_end=0.0):
    """Centre-plane section of the open rocker, the construction c_outline() and c1_body() use (mm).
    Defaults are the round 2 body (c1); round 3 passes its cradle length, half chord and deck depth. With r_end the two
    top corners are rounded that much, at the cradle floor and at the shoulders, as c1r_side() does for the kept body."""
    half, top, zc = half or d["C_CHORD"] / 2, top or d["XC_TOP"], HIGH * IN + CD_MM
    tm = math.asin(half / RR)
    arc = [(RR * math.sin(t), RR * (1 - math.cos(t))) for t in np.linspace(-tm, tm, 121)]
    ends = [(top / 2, zc - deck), (top / 2, zc), (-top / 2, zc), (-top / 2, zc - deck)] if deck else [(top / 2, zc), (-top / 2, zc)]
    sharp = ShPolygon(arc + ends)
    outline = sharp.buffer(-5).buffer(5)
    floor = HIGH * IN - PAD_T
    window = outline.buffer(-d["C_FR"], join_style=2).intersection(box(-200, 0, 200, floor - d["C_FR"])).buffer(-9).buffer(9)
    body = outline.intersection(box(-200, -5, 200, floor))
    rim = outline.intersection(box(-200, floor, 200, 200))
    if r_end:
        upper = box(-200, 60, 200, 300)   # the sides are straight here, so the two halves meet on them
        rounded = lambda g: g.buffer(-r_end, resolution=32).buffer(r_end, resolution=32).intersection(upper)
        body = body.difference(upper).union(rounded(sharp.intersection(box(-200, -5, 200, floor))))
        rim = rounded(sharp)              # the far shoulder; the body is drawn over its lower part
    pad = box(-top / 2 + 3, floor, top / 2 - 3, HIGH * IN)
    return body, window, rim, pad


def fig_roll(d, rk):
    """Side view through the middle of the open rocker: empty, then rolled under the bass. To scale, one picture each
    so the page can stack them on a phone."""
    body, window, rim, pad = rocker_section(d, r_end=d["R_END"])
    zb = HIGH * IN
    n = NECKS["bass"]
    neck = ShPolygon([(-160, zb), (230, zb), (230, zb + n["d1"] * IN), (-160, zb + n["d0"] * IN)])
    board = ShPolygon([(-160, zb + n["d0"] * IN - 6.35), (230, zb + n["d1"] * IN - 6.35), (230, zb + n["d1"] * IN), (-160, zb + n["d0"] * IN)])
    bass = rk["instruments"]["bass"]
    for name, t_deg in (("roll-empty", 0.0), ("roll-bass", bass["roll_deg"])):
        fig, ax = plt.subplots(figsize=(5.6, 2.9), dpi=170)
        shift = RR * math.radians(t_deg)
        put = lambda g: affinity.translate(affinity.rotate(g, -t_deg, origin=(0, RR)), shift, 0)
        draw = lambda g, **kw: ax.add_patch(MplPolygon(np.array(g.exterior.coords), closed=True, **kw))
        ax.plot([-185, 235], [0, 0], color=INK, lw=1.4)
        if t_deg:
            draw(body.union(rim), fc="none", ec=MUTED, lw=0.9, ls=(0, (4, 3)))
            draw(put(neck), fc=WOOD, ec="#8a6a3c", lw=1)
            draw(put(board), fc=BOARD, ec=BOARD, lw=0.5)
        else:
            draw(put(rim), fc="#b7cdf6", ec="#2b4f9e", lw=0.8)
        draw(put(body), fc=PRINT, ec="#2b4f9e", lw=1.2)
        draw(put(window), fc="white", ec="#2b4f9e", lw=1.2)
        draw(put(pad), fc=PADC, ec="#8a6a3c", lw=0.8)
        # centre of the rocking curve, and the line on the bench under it
        ax.plot([shift, shift], [0, RR], color=ACCENT, lw=0.9, ls=":")
        ax.plot(shift, RR, marker="+", color=ACCENT, ms=11, mew=1.6)
        ax.plot(shift, -3.5, marker="^", color=ACCENT, ms=8)
        if t_deg:
            ax.text(25, 172, f"Under the bass: rolled {t_deg:.1f} degrees", fontsize=11.5, weight="bold", color=INK, ha="center", va="top")
            ax.text(shift, -13, f"the contact line has moved {frac(bass['bench_contact_moves_mm'] / IN)} in along the bench",
                    fontsize=9.5, color=ACCENT, ha="center", va="top")
            ax.text(-178, 44, "dashed: where\nit sat empty", fontsize=9, color=MUTED, ha="left", va="center")
            ax.text(-150, 147, "toward the nut", fontsize=9, color=MUTED, ha="left", va="center")
            ax.text(232, 54, "toward the body", fontsize=9, color=MUTED, ha="right", va="center")
        else:
            ax.text(25, 172, "Empty: it sits level", fontsize=11.5, weight="bold", color=INK, ha="center", va="top")
            ax.text(shift + 9, RR, f"centre of the bottom curve,\n{frac(RR / IN)} in above the bench", fontsize=9.5, color=ACCENT, va="center", ha="left")
            ax.annotate("", xy=(-98, 0), xytext=(-98, zb), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
            ax.plot([-104, -55], [zb, zb], color=INK, lw=0.7)
            ax.text(-104, zb / 2, f"{frac(HIGH)} in\nto the pad", fontsize=9.5, color=INK, va="center", ha="right")
            ax.text(shift, -13, "one line of contact with the bench", fontsize=9.5, color=ACCENT, ha="center", va="top")
        ax.set_xlim(-185, 235)
        ax.set_ylim(-30, 176)
        ax.set_aspect("equal")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(IMAGES / f"{name}.png", facecolor="white")
        plt.close(fig)


# ---------------------------------------------------------------- the kept body: rounded edges
def round_numbers(d):
    """Sizes of the roundovers on the kept body (c1r), read back from concepts.scad."""
    return {"cradle_ends_mm": d["R_END"], "other_edges_mm": d["R_EDGE"], "end_face_lean_deg": round(d["C_LEAN"], 2),
            "level_floor_mm": round(d["C1R_FLAT"], 1), "pad_drawn_mm": d["XC_TOP"] - 6,
            "shoulder_flat_mm": round(C_WIDTH / 2 - d["R_EDGE"] - d["RIM_Y"], 2),
            "tread_lip_flat_mm": round(d["TR_IN"] - d["R_EDGE"], 2)}


def fig_end(d):
    """One cradle end, cut through the middle and drawn to scale: the roundover, the square end it replaces, the pad."""
    r = d["R_END"]
    body, _, _, pad = rocker_section(d, r_end=r)
    floor, zb = HIGH * IN - PAD_T, HIGH * IN
    a = math.radians(d["C_LEAN"])
    xt = d["C1R_FLAT"] / 2                                    # where the level floor ends and the roundover starts
    cz = floor - r                                            # the arc's centre is straight under that point
    mid = (math.pi / 2 + a) / 2                               # halfway round the arc
    assert pad.bounds[2] < xt, "the pad runs onto the roundover"
    assert body.exterior.distance(ShPoint(xt + r * math.cos(mid), cz + r * math.sin(mid))) < 0.05, \
        "concepts.scad's C1R_FLAT and this section disagree about where the roundover is"
    n = NECKS["bass"]
    fig, ax = plt.subplots(figsize=(5.6, 3.5), dpi=170)
    draw = lambda g, **kw: ax.add_patch(MplPolygon(np.array(g.exterior.coords), closed=True, **kw))
    x0, x1, z0, z1 = 26, 86, 77, 114
    ax.add_patch(MplPolygon([(x0 - 5, zb), (x1 + 5, zb), (x1 + 5, z1 + 5), (x0 - 5, z1 + 5)], closed=True, fc=WOOD, ec="#8a6a3c", lw=1))
    draw(body, fc=PRINT, ec="#2b4f9e", lw=1.2)
    draw(pad, fc=PADC, ec="#8a6a3c", lw=0.8)
    tl = r * math.tan((math.pi / 2 - a) / 2)                  # from the square corner to where the arc leaves each face
    ax.plot([xt, xt + tl, xt + tl + tl * math.sin(a)], [floor, floor, floor - tl * math.cos(a)], color=INK, lw=1.3, ls=(0, (3, 2)))
    ax.annotate("", xy=(xt + r * math.cos(mid), cz + r * math.sin(mid)), xytext=(xt, cz),
                arrowprops=dict(arrowstyle="->", color="white", lw=1.4))
    ax.text(xt - 1.2, cz - 0.3, f"{frac(r / IN)} in", fontsize=12, weight="bold", color="white", ha="right", va="center")
    ax.annotate("square end, before", xy=(xt + tl + 0.3, floor - 0.4), xytext=(xt + tl + 6, floor - 6), fontsize=10,
                color=INK, ha="left", va="center", arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
    ax.annotate("the pad stops where\nthe roundover starts", xy=(pad.bounds[2] - 0.3, zb - 0.9), xytext=(x0 + 3, zb + 9),
                fontsize=10, color=INK, ha="left", va="center", arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
    ax.text(x1 - 3, zb + 9, "neck", fontsize=10.5, color="#6b4f2a", ha="right", va="center")
    ax.text(x0 + 3, floor - 9, "printed body", fontsize=10.5, color="white", ha="left", va="center")
    ax.set_xlim(x0, x1)
    ax.set_ylim(z0, z1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout(pad=0.3)
    fig.savefig(IMAGES / "end-section.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- round 3: a longer cradle
def long_numbers(d):
    """What each longer cradle does under each instrument, and how much neck it carries."""
    assert abs(d["C_CHORD"] - 150.0) < 1e-6, "LONG's 150 mm chord is meant to be the round 2 rocker"
    dz = RR - HIGH * IN

    def entry(top, chord, start):
        xr = start + top / 2
        e = {"cradle_mm": round(top, 1), "rocker_chord_mm": round(chord, 1), "cradle_start_from_nut_mm": round(start, 1),
             "rest_centre_from_nut_mm": round(xr, 1), "roll_limit_deg": round(math.degrees(math.asin(chord / 2 / RR)), 1),
             "instruments": {}}
        for name, tail in (("bass", TAIL_TO_NUT), ("guitar", TAIL_TO_NUT_GUITAR)):
            t = math.radians(tilt_deg(HIGH, xr / IN, tail))
            e["instruments"][name] = {
                "roll_deg": round(math.degrees(t), 2),
                "bench_contact_moves_mm": round(RR * t, 1),
                "load_off_pad_middle_mm": round(dz * math.sin(t), 2),
                "level_cradle_gap_mm": round(top * math.tan(t), 1),
                "last_fret_over_cradle": sum(1 for x in frets(NECKS[name]["scale"]) if x <= start + top),
            }
        return e

    out = {"round2": entry(d["XC_TOP"], d["C_CHORD"], X_REST - d["XC_TOP"] / 2), "variants": {}}
    for k, v in LONG.items():
        out["variants"][k] = entry(v["top"] * IN, v["chord"], REST_START)
    return out


def fig_long(d):
    """Side view through the middle of each longer-cradle body, level, with the round 2 body dashed over it. To scale."""
    deck = CD_MM + PAD_T + d["C_FR"]
    zc = HIGH * IN + CD_MM
    ref_body, _, ref_rim, _ = rocker_section(d)
    ref = ref_body.union(ref_rim)
    for k, v in LONG.items():
        top, half = v["top"] * IN, v["chord"] / 2
        body, window, rim, pad = rocker_section(d, top, half, deck)
        fig, ax = plt.subplots(figsize=(4.6, 3.05), dpi=200)
        draw = lambda g, **kw: ax.add_patch(MplPolygon(np.array(g.exterior.coords), closed=True, **kw))
        ax.plot([-126, 126], [0, 0], color=INK, lw=1.4)
        draw(rim, fc="#b7cdf6", ec="#2b4f9e", lw=0.8)
        draw(body, fc=PRINT, ec="#2b4f9e", lw=1.2)
        draw(window, fc="white", ec="#2b4f9e", lw=1.2)
        draw(pad, fc=PADC, ec="#8a6a3c", lw=0.8)
        draw(ref, fc="none", ec=INK, lw=1.1, ls=(0, (4, 3)))
        for y, x0, x1, text, va, dy in ((zc + 9, -top / 2, top / 2, f"cradle {frac(top / IN)} in", "bottom", 3),
                                        (-11, -half, half, f"rocker {frac(2 * half / IN)} in", "top", -3)):
            ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.2))
            for x in (x0, x1):
                ax.plot([x, x], [y - 4, y + 4], color=ACCENT, lw=0.9)
            ax.text(0, y + dy, text, fontsize=11.5, color=ACCENT, ha="center", va=va, weight="bold")
        ax.set_xlim(-126, 126)
        ax.set_ylim(-31, zc + 27)
        ax.set_aspect("equal")
        ax.axis("off")
        fig.tight_layout(pad=0.3)
        fig.savefig(IMAGES / f"side-{k}.png", facecolor="white")
        plt.close(fig)


if __name__ == "__main__":
    IMAGES.mkdir(parents=True, exist_ok=True)
    STLS.mkdir(parents=True, exist_ok=True)
    write_params("bass")
    d = derived()
    # the pedestal is drawn F_LIFT above its lowest position: pitch the neck for that height
    write_params("bass", f_tilt_h=(d["F_MIN"] + F_LIFT) / IN)
    report = {"derived_mm": d, "heights_in": {"low": LOW, "high": HIGH, "tall": TALL, "flat": FLAT},
              "tilt_deg": {"low": round(tilt_deg(LOW), 2), "high": round(tilt_deg(HIGH), 2), "tall": round(tilt_deg(TALL), 2)},
              "pedestal_in": {"min": round(d["F_MIN"] / IN, 2), "max": round(d["F_MAX"] / IN, 2), "drawn": round((d["F_MIN"] + F_LIFT) / IN, 2)},
              "cradle": {"width_mm": CW, "radius_mm": CR, "depth_mm": round(d["CD"], 2), "pad_mm": PAD_T}}
    report["rocker"] = rocker_numbers(d)
    report["long"] = long_numbers(d)
    report["roundover"] = round_numbers(d)
    if "--no-stl" not in sys.argv:
        report["parts"] = export_stls(d)
    fig_fit()
    report["use"] = fig_use()
    fig_roll(d, report["rocker"])
    fig_end(d)
    fig_long(d)
    if "--no-render" not in sys.argv:
        only = [a.split("=")[1] for a in sys.argv if a.startswith("--only=")]
        for c in CONCEPTS:
            for v in VIEWS[c]:
                if not only or c in only:
                    print("rendered", render(c, v).name)
        if not only or PAD_SHOWN in only:
            for m in PAD_MATERIALS:
                print("rendered", render(PAD_SHOWN, "pad", padmat=m).name)
    old = json.loads((PROJECT / "concepts-report.json").read_text()) if (PROJECT / "concepts-report.json").exists() else {}
    old.update(report)
    (PROJECT / "concepts-report.json").write_text(json.dumps(old, indent=1))
    print(json.dumps({k: v for k, v in report.items() if k != "parts"}, indent=1))
