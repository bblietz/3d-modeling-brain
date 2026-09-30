"""Logo Dude desk stand (style C, Brian 2026-09-29: "also make C - Desk Stand").

A standee: the badge art (logodude.py, unchanged: same outline, ink, size) plus
a plain white TAB under the jaw, standing in a black PETG BASE whose slot grips
the tab with crush ribs (knowledge/friction-fits-x2d.md: free body clearance,
the ribs own the fit). The whole face stays above the base.

Print: the figure flat, ink up, like the badge (two colors); the base upright,
slot up, one color, no supports. Two print files.
"""
import os
import pathlib
import runpy

import numpy as np

from build123d import (Align, Axis, Box, Cone, Cylinder, Edge, Face, Pos, Rot, SlotOverall, Vector, Wire, chamfer,
                       export_stl, extrude, fillet)
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

HERE = pathlib.Path(__file__).resolve().parent

# the badge, built without its own exports or viewer push
_env = {k: os.environ.pop(k) for k in ("EXPORT", "SHOW") if k in os.environ}
B = runpy.run_path(str(HERE / "logodude.py"))
os.environ.update(_env)
T, INK_H = B["BACKER_T"], B["INK_H"]

TAB_W = 36.0          # mm, tab width along the base
SLOT_DEPTH = 9.0      # mm, tab length inside the base
JAW_GAP = 0.5         # mm, lowest point of the outline above the base top (the tab bottoms out, not the outline)
NECK_R = 2.0          # mm, fillet where the tab meets the curved outline
TAB_CHAMFER = 0.8     # mm, tab bottom corners: lead-in
BASE_L, BASE_W, BASE_H = 80.0, 34.0, 12.0
BASE_TOP_FILLET = 3.0
BASE_FOOT_CHAMFER = 0.4   # elephant foot
# fit (friction-fits-x2d.md): body free 0.15 per side, R1 ribs 0.35 proud -> 0.20 interference per side.
# Those numbers are a PLA / 0.6 nozzle calibration; PETG invalidates them (recipe says coupon first).
SLOT_CLEAR = 0.15     # per side, across the plate
SLOT_END_CLEAR = 0.3  # per end, free
RIB_R, RIB_PROUD, RIB_TOP_CHAMFER = 1.0, 0.35, 0.5
SLOT_LEADIN = 0.8     # 45 degree chamfer at the slot mouth
RIB_X = (-TAB_W * 0.3, TAB_W * 0.3)   # 2 ribs per long wall

# ---------------------------------------------------------------- figure (2D, badge frame, y up)
outline, ink_2d = B["backer_2d"], B["ink_2d"]
_bx0, _by0, _bx1, _by1 = outline.bounds
BASE_TOP_Y = _by0 - JAW_GAP                      # base top, in figure coordinates
TAB_BOTTOM_Y = BASE_TOP_Y - SLOT_DEPTH
_tab = box(-TAB_W / 2, TAB_BOTTOM_Y, TAB_W / 2, _by0 + 8.0)
_joined = outline.union(_tab)
# fillet only the two concave necks where the tab meets the outline
_neck_zone = box(-TAB_W / 2 - 3 * NECK_R, TAB_BOTTOM_Y - 1.0, TAB_W / 2 + 3 * NECK_R, _by0 + 6.0)   # reaches below the
# neck so the fillet tapers out along the tab side (a zone cut at the base top left a 0.007 mm ledge)
_closed = _joined.buffer(NECK_R, quad_segs=24).buffer(-NECK_R, quad_segs=24)
figure_2d = _joined.union(_closed.intersection(_neck_zone))
# lead-in chamfers on the tab's bottom corners
for sx in (-1, 1):
    x = sx * TAB_W / 2
    figure_2d = figure_2d.difference(Polygon([(x, TAB_BOTTOM_Y - 0.01), (x - sx * TAB_CHAMFER, TAB_BOTTOM_Y - 0.01),
                                               (x + sx * 0.01, TAB_BOTTOM_Y + TAB_CHAMFER)]))
figure_2d = Polygon(figure_2d.exterior)
assert figure_2d.is_valid and figure_2d.geom_type == "Polygon"
assert outline.difference(figure_2d).area < 1e-6, "figure lost part of the badge outline"
assert ink_2d.bounds[1] - BASE_TOP_Y > 3.0, "ink would sit at or below the base top"
# the tab is a plain rectangle through the straight part of the slot (the neck fillets start at the lead-in)
_in_slot = figure_2d.intersection(box(-50, TAB_BOTTOM_Y + TAB_CHAMFER, 50, BASE_TOP_Y - SLOT_LEADIN))
assert abs(_in_slot.bounds[2] - _in_slot.bounds[0] - TAB_W) < 0.02, _in_slot.bounds   # fillet tail (0.0065 mm) faces
# a slot end, which is SLOT_END_CLEAR free



def cornered_face(poly, step, corner_deg=30.0):
    """Polygon -> Face: split the ring at sharp corners; straight runs become lines, curved runs splines.
    (One periodic spline through the tab's corners overshoots them: the tab bottom sagged 0.018 mm.)"""
    pts = np.asarray(poly.exterior.coords)[:-1]
    n = len(pts)
    v_in, v_out = pts - np.roll(pts, 1, axis=0), np.roll(pts, -1, axis=0) - pts
    cosang = np.einsum("ij,ij->i", v_in, v_out) / (np.linalg.norm(v_in, axis=1) * np.linalg.norm(v_out, axis=1))
    corners = [i for i in range(n) if cosang[i] < np.cos(np.radians(corner_deg))]
    assert len(corners) >= 2, corners
    edges = []
    for k, i0 in enumerate(corners):
        i1 = corners[(k + 1) % len(corners)]
        run = np.vstack([pts[i0:i1 + 1]] if i1 > i0 else [pts[i0:], pts[:i1 + 1]])
        a, b = run[0], run[-1]
        chord = b - a
        off = np.abs(chord[0] * (run[:, 1] - a[1]) - chord[1] * (run[:, 0] - a[0])) / np.linalg.norm(chord)
        if off.max() < 1e-6:
            edges.append(Edge.make_line(Vector(*a), Vector(*b)))
        else:
            ls = LineString(run)
            m = max(int(round(ls.length / step)), 3)
            knots = [ls.interpolate(j * ls.length / m).coords[0] for j in range(m + 1)]
            edges.append(Edge.make_spline([Vector(*q) for q in knots]))
    f = Face(Wire(edges))
    a = B["mesh_area"](f)
    assert abs(a - poly.area) / poly.area < 0.002, f"cornered face {a:.2f} vs outline {poly.area:.2f} mm2"
    return f, len(corners)


_fig_face, _n_corners = cornered_face(figure_2d, B["OUTLINE_KNOT_MM"])
assert _n_corners == 4, _n_corners        # the two ends of each tab-bottom chamfer
figure_backer = extrude(_fig_face, T, dir=(0, 0, 1))
ink = B["ink"]                                   # identical to the badge's ink

# ---------------------------------------------------------------- base (print orientation, z up, slot along x)
SLOT_W = T + 2 * SLOT_CLEAR
SLOT_L = TAB_W + 2 * SLOT_END_CLEAR
base = extrude(SlotOverall(BASE_L, BASE_W), BASE_H)
base = fillet(base.edges().group_by(Axis.Z)[-1], BASE_TOP_FILLET)
base = chamfer(base.edges().group_by(Axis.Z)[0], BASE_FOOT_CHAMFER)
base -= Pos(0, 0, BASE_H - SLOT_DEPTH) * Box(SLOT_L, SLOT_W, SLOT_DEPTH + 1,
                                              align=(Align.CENTER, Align.CENTER, Align.MIN))
# 45 degree lead-in around the slot mouth
_mouth = [e for e in base.edges().filter_by(Axis.Z, reverse=True) if abs(e.center().Z - BASE_H) < 1e-6
          and abs(e.center().X) <= SLOT_L / 2 + 1e-6 and abs(e.center().Y) <= SLOT_W / 2 + 1e-6]
assert len(_mouth) == 4, len(_mouth)
base = chamfer(_mouth, SLOT_LEADIN)
_rib_top = BASE_H - SLOT_LEADIN - RIB_TOP_CHAMFER
_rib_len = _rib_top - (BASE_H - SLOT_DEPTH)
for x in RIB_X:
    for sy in (-1, 1):
        y = sy * (SLOT_W / 2 + RIB_R - RIB_PROUD)             # axis behind the wall: crest RIB_PROUD into the slot
        rib = Pos(x, y, BASE_H - SLOT_DEPTH) * Cylinder(RIB_R, _rib_len, align=(Align.CENTER, Align.CENTER, Align.MIN))
        rib += Pos(x, y, _rib_top) * Cone(RIB_R, RIB_R - RIB_TOP_CHAMFER, RIB_TOP_CHAMFER,
                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
        base += rib
assert len(base.solids()) == 1


# ---------------------------------------------------------------- fit checks from geometry probes
def gap_y(shape, x, z):
    """Open width across the slot at (x, z): distance between the solid material on either side."""
    probe = Pos(x, 0, z) * Box(0.05, BASE_W + 10, 0.05)
    parts = (shape & probe).solids()
    inner = sorted([(p.bounding_box().min.Y, p.bounding_box().max.Y) for p in parts])
    left = max(hi for lo, hi in inner if hi < 0.5)
    right = min(lo for lo, hi in inner if lo > -0.5)
    return right - left


_zmid = BASE_H - SLOT_DEPTH / 2
body_gap = gap_y(base, 0.0, _zmid)
crest_gap = gap_y(base, RIB_X[1], _zmid)
assert abs(body_gap - SLOT_W) < 1e-3, body_gap
assert abs((T - crest_gap) / 2 - (RIB_PROUD - SLOT_CLEAR)) < 1e-3, crest_gap
print(f"slot {body_gap:.3f} mm across for a {T:.1f} mm tab ({(body_gap - T) / 2:.3f} free per side); "
      f"rib crests {crest_gap:.3f} mm ({(T - crest_gap) / 2:.3f} interference per side)")

# ---------------------------------------------------------------- assembled (in-use): figure upright, ink toward -Y
_up = Rot(90, 0, 0)                               # figure y -> z, figure z (thickness, ink side) -> -y
_lift = (BASE_H - SLOT_DEPTH) - TAB_BOTTOM_Y
_shift_y = T / 2                                  # backer centered on the slot
fig_backer_asm = Pos(0, _shift_y, _lift) * (_up * figure_backer)
fig_ink_asm = Pos(0, _shift_y, _lift) * (_up * ink)
_fb = fig_backer_asm.bounding_box(optimal=True)
assert abs(_fb.min.Z - (BASE_H - SLOT_DEPTH)) < 1e-3, f"tab bottom at z {_fb.min.Z:.4f}, slot floor {BASE_H - SLOT_DEPTH}"
assert abs(_fb.min.Y + T / 2) < 1e-3 and abs(_fb.max.Y - T / 2) < 1e-3
assert fig_ink_asm.bounding_box(optimal=True).min.Z > BASE_H + 3.0, "ink too close to the base top"
_hb = _fb
height_in = _hb.max.Z / 25.4
print(f"figure {figure_backer.bounding_box().size.X:.1f} x {figure_backer.bounding_box().size.Y:.1f} mm flat; "
      f"base {BASE_L:.0f} x {BASE_W:.0f} x {BASE_H:.0f} mm; standing height {_hb.max.Z:.1f} mm ({height_in:.2f} in)")

# ---------------------------------------------------------------- exports (print orientation)
OUT = pathlib.Path(os.environ.get("OUT", HERE))
if os.environ.get("EXPORT"):
    import trimesh
    for name, part in (("stand-figure-backer", figure_backer), ("stand-base", base)):
        f = OUT / f"logodude-{name}.stl"
        export_stl(part, str(f), tolerance=0.005, angular_tolerance=0.1)
        m = trimesh.load(f)
        assert m.is_watertight, f"{f.name} not watertight"
        print(f"{f.name}: {len(m.faces)} tris, watertight, {m.volume / 1000:.1f} cm3")
    fm = trimesh.load(OUT / "logodude-stand-figure-backer.stl")
    assert abs(fm.volume - figure_2d.area * T) / (figure_2d.area * T) < 2e-3

if os.environ.get("SHOW"):
    from ocp_vscode import Camera, show
    show(fig_backer_asm, fig_ink_asm, base, names=["figure (white)", "ink (black)", "base (black)"],
         colors=["#f4f4f2", "#1d1d1f", "#3a3a3d"],
         reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
