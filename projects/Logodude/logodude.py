"""Logo Dude, die-cut badge (style B, chosen 2026-09-29).

Ink: logo-dude.png traced 1:1 (pipeline/trace.py -> traced.json), cleaned to
solid strokes, scaled so the badge is TOTAL_H tall, raised INK_H on a backer
that follows the drawing with a MARGIN outline. All edges are smoothed
splines. Two colors, one color change: backer layers are all white, ink
layers all black. Print flat, ink up.
"""
import json
import os
import pathlib

import numpy as np
from build123d import Compound, Edge, Face, Pos, Vector, Wire, export_stl, extrude
from scipy.ndimage import gaussian_filter1d
from shapely.affinity import affine_transform
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

HERE = pathlib.Path(__file__).resolve().parent

TOTAL_H = 4 * 25.4   # mm, finished badge height, outline included (Brian 2026-09-29: "4 in tall")
BACKER_T = 3.0       # mm
INK_H = 1.0          # mm, raised above the backer
MARGIN = 3.5         # mm, backer outline past the ink
MARGIN_GROW = 5.0    # grown this far, then shrunk back to MARGIN: closes the gaps between strokes
MIN_MARGIN = 2.5     # mm, asserted: smoothing the outline never leaves less than this past the ink
# Solid lines (Brian 2026-09-29: "clean up the black lines so they are solid"):
# morphological close (fills dry-brush streaks) then open (trims the lumps
# they leave), in source px so the look does not depend on print size.
# Per shape: the hair strokes are ~58 px wide and take a strong pass; the
# face lines are ~16 px and keep a light one, since a stronger close fills
# the tapered eye corners and the channel under the doubled eyelid.
CLEAN_HAIR_PX = (14, 10)     # (close radius, open radius); 20/14 splits a stroke,
                             # 26+ fills the V gaps between the zigzag legs
CLEAN_FACE_PX = (3, 3)
MIN_PIECE_PX = 300           # loose brush slivers; the smallest real shape (nose) is 1700
# Right hair stroke, outer edge: its outermost streaks are fainter than the
# trace threshold, so the edge stepped in behind them (Brian: "a small gap on
# the right side"). A wide close fills that dent, applied only in this
# region right of the stroke centerline so the hook's inner V stays sharp.
RIGHT_EDGE_REGION_PX = [(1037, 150), (1120, 150), (1120, 520), (937, 520),
                        (978, 400), (1015, 300), (1037, 200)]
RIGHT_EDGE_CLOSE_PX = 60
# Smooth edges (Brian 2026-09-29: "smoothen all edges of the black lines",
# "the edge of the part ... should be smooth all the way around"): each ring
# is resampled by arc length and Gaussian-smoothed, then built as a periodic
# spline, so the edges carry no facets or bumps.
SMOOTH_HAIR_PX = 14          # sigma along the edge, source px; 6 left lumps (Brian: "too choppy")
SMOOTH_FACE_PX = 5
# Jaw (Brian 2026-09-29: "smooth out the bottom edge of the face, in the jaw
# area"): the face-outline stroke gets a stronger sigma on its lower part,
# ramped in between these source rows so the stroke ends keep their shape.
SMOOTH_JAW_PX = 40           # 16 left the bumps (6 mm long); 60 trips the thinning assert
JAW_RAMP_Y_PX = (1000, 1060)
SMOOTH_OUTLINE_MM = 2.5
INK_KNOT_MM = 0.3            # spline point spacing
OUTLINE_KNOT_MM = 1.0

# ---------------------------------------------------------------- traced ink, cleaned solid
_d = json.loads((HERE / "traced.json").read_text())
_px = unary_union([Polygon(p["outer"], p["holes"]) for p in _d["polys"]])


def _morph(g, close_r, open_r):
    g = g.buffer(close_r, quad_segs=16).buffer(-close_r, quad_segs=16)
    return g.buffer(-open_r, quad_segs=16).buffer(open_r, quad_segs=16)


def _resample(ring, step):
    L = ring.length
    n = max(int(round(L / step)), 16)
    return np.array([ring.interpolate(i * L / n).coords[0] for i in range(n)])


def _smooth_ring(ring, sigma, step):
    return gaussian_filter1d(_resample(ring, step), sigma / step, axis=0, mode="wrap")


def _smooth(g, sigma, step=0.5):
    out = [Polygon(_smooth_ring(p.exterior, sigma, step),
                   [_smooth_ring(h, sigma, step) for h in p.interiors]).buffer(0)
           for p in getattr(g, "geoms", [g])]
    return unary_union(out)


def _smooth_jaw(p, step=0.5):
    """Face-outline stroke: SMOOTH_FACE_PX above the jaw, SMOOTH_JAW_PX below, blended."""
    pts = _resample(p.exterior, step)
    lo = gaussian_filter1d(pts, SMOOTH_FACE_PX / step, axis=0, mode="wrap")
    hi = gaussian_filter1d(pts, SMOOTH_JAW_PX / step, axis=0, mode="wrap")
    t = np.clip((lo[:, 1] - JAW_RAMP_Y_PX[0]) / (JAW_RAMP_Y_PX[1] - JAW_RAMP_Y_PX[0]), 0, 1)
    w = (t * t * (3 - 2 * t))[:, None]                    # smoothstep: no kink at the ramp ends
    assert not p.interiors
    return Polygon(lo * (1 - w) + hi * w).buffer(0)


def _count(g):
    geoms = getattr(g, "geoms", [g])
    return len(geoms), sum(len(p.interiors) for p in geoms)


_pieces = [p for p in _px.geoms if p.area >= MIN_PIECE_PX]
_hair = max(_pieces, key=lambda p: p.area)
_face = unary_union([p for p in _pieces if p is not _hair])
_hair_c = _morph(_hair, *CLEAN_HAIR_PX)
_hair_c = _hair_c.union(_morph(_hair, RIGHT_EDGE_CLOSE_PX, 0).intersection(Polygon(RIGHT_EDGE_REGION_PX)))
_face_c = _morph(_face, *CLEAN_FACE_PX)
_face_parts = list(_face_c.geoms)                          # a list: .geoms makes new objects per access
_jaw_c = max(_face_parts, key=lambda p: p.area)           # the face-outline stroke
_hair_s = _smooth(_hair_c, SMOOTH_HAIR_PX)
_face_s = unary_union([_smooth_jaw(_jaw_c)] +
                      [_smooth(p, SMOOTH_FACE_PX) for p in _face_parts if p is not _jaw_c])
assert _count(_hair_s) == _count(_hair_c) == (1, 0), "hair cleanup split, merged, or holed"
assert _count(_face_s) == _count(_face_c) and _count(_face_c)[0] == len(_face.geoms), \
    "face cleanup merged, split, or lost an eye white"
assert abs(_face_s.area - _face_c.area) / _face_c.area < 0.03, "face smoothing thinned the lines"
assert abs(_face_s.area - sum(p.area for p in _face_s.geoms)) < 1e-6 and \
    len(_face_s.geoms) == len(_face_parts), "face pieces overlap (a piece was added twice)"
_solid = unary_union([_hair_s, _face_s])
assert _count(_solid) == (1 + len(_face.geoms), _count(_face_c)[1])
_x0, _y0, _x1, _y1 = _solid.bounds


def _pinches(g):
    rings = [r for p in getattr(g, "geoms", [g]) for r in (p.exterior, *p.interiors)]
    tree = STRtree(rings)
    pts = []
    for i, j in zip(*tree.query(rings, predicate="intersects")):
        if i < j:
            x = rings[i].intersection(rings[j])
            pts += [q for q in getattr(x, "geoms", [x]) if not q.is_empty]
    return pts


assert not _pinches(_solid), "two ink rings touch (non-manifold once extruded)"


def build_2d(k):
    """Ink and backer outlines at k mm/px: px (y down) -> mm (y up), art centered."""
    ink = affine_transform(_solid, [k, 0, 0, -k, -k * (_x0 + _x1) / 2, k * (_y0 + _y1) / 2])
    grown = ink.buffer(MARGIN_GROW, quad_segs=32).buffer(MARGIN - MARGIN_GROW, quad_segs=32)
    assert grown.geom_type == "Polygon", "die-cut outline is not one piece"
    backer = Polygon(_smooth_ring(grown.exterior, SMOOTH_OUTLINE_MM, 0.25))   # interior filled, like a sticker
    assert backer.is_valid
    assert ink.buffer(MIN_MARGIN).difference(backer).area < 1e-6, "outline smoothing ate the margin"
    return ink, backer


# solve the scale so the whole badge is TOTAL_H tall (the margin is fixed in mm)
K = TOTAL_H / (_y1 - _y0)
for _ in range(4):
    ink_2d, backer_2d = build_2d(K)
    _bx0, _by0, _bx1, _by1 = backer_2d.bounds
    K = (TOTAL_H - ((_by1 - _by0) - (_y1 - _y0) * K)) / (_y1 - _y0)
ink_2d, backer_2d = build_2d(K)


# OCC's area/volume integration is wrong on long periodic splines (0.8% on
# the outline face, 14% on its extrusion), so every check measures the
# tessellated mesh instead: that is also what the STL carries.
def _mesh(shape, tol=0.005):
    v, t = shape.tessellate(tol, 0.05)
    return np.array([[q.X, q.Y, q.Z] for q in v]), np.array(t)


def mesh_area(face):
    V, T = _mesh(face)
    return 0.5 * np.linalg.norm(np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]), axis=1).sum()


def mesh_volume(solid):
    V, T = _mesh(solid)
    return abs(np.einsum("ij,ij->i", V[T[:, 0]], np.cross(V[T[:, 1]], V[T[:, 2]])).sum()) / 6


def to_face(p, step):
    """Polygon -> Face whose rings are periodic splines through points every `step` mm."""
    def ring(r):
        return Wire([Edge.make_spline([Vector(x, y) for x, y in _resample(r, step)], periodic=True)])
    f = Face(ring(p.exterior), [ring(h) for h in p.interiors])
    a = mesh_area(f)
    assert abs(a - p.area) / p.area < 0.002, f"spline fit drifted: face {a:.2f} vs outline {p.area:.2f} mm2"
    return f


backer = extrude(to_face(backer_2d, OUTLINE_KNOT_MM), BACKER_T, dir=(0, 0, 1))
ink = Compound([Pos(0, 0, BACKER_T) * extrude(to_face(p, INK_KNOT_MM), INK_H, dir=(0, 0, 1))
                for p in getattr(ink_2d, "geoms", [ink_2d])])

# ---------------------------------------------------------------- checks
bb = backer.bounding_box(optimal=True)
ib = ink.bounding_box(optimal=True)
assert len(backer.solids()) == 1
assert len(ink.solids()) == len(getattr(ink_2d, "geoms", [ink_2d]))
assert abs(bb.size.Y - TOTAL_H) < 0.02, f"badge is {bb.size.Y:.3f} mm tall, want {TOTAL_H}"
assert abs(mesh_volume(backer) - backer_2d.area * BACKER_T) / (backer_2d.area * BACKER_T) < 2e-3
assert abs(sum(mesh_volume(x) for x in ink.solids()) - ink_2d.area * INK_H) / (ink_2d.area * INK_H) < 2e-3
assert abs(ib.min.Z - BACKER_T) < 1e-6 and abs(ib.max.Z - BACKER_T - INK_H) < 1e-6
assert bb.size.X <= 256 and bb.size.Y <= 256
print(f"backer {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.1f} mm "
      f"({bb.size.X / 25.4:.2f} x {bb.size.Y / 25.4:.2f} in); "
      f"ink {ib.size.X:.1f} x {ib.size.Y:.1f} mm, {len(ink.solids())} pieces, "
      f"{ink_2d.area:.0f} mm2; {K:.4f} mm/px")

# ---------------------------------------------------------------- exports
OUT = pathlib.Path(os.environ.get("OUT", HERE))
if os.environ.get("EXPORT"):
    import trimesh
    for name, part, vol in (("backer", backer, backer_2d.area * BACKER_T), ("ink", ink, ink_2d.area * INK_H)):
        f = OUT / f"logodude-{name}.stl"
        export_stl(part, str(f), tolerance=0.005, angular_tolerance=0.1)
        m = trimesh.load(f)
        assert m.is_watertight, f"{f.name} not watertight"
        assert abs(m.volume - vol) / vol < 0.002, f"{f.name} volume drift"
        print(f"{f.name}: {len(m.faces)} tris, watertight")

if os.environ.get("SHOW"):
    from ocp_vscode import show, Camera
    show(backer, ink, names=["backer (white)", "ink (black)"], colors=["#f4f4f2", "#1d1d1f"],
         reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
