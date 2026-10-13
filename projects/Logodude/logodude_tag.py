"""Logo Dude luggage tag (2026-10-13).

The die-cut badge (logodude.py: traced, cleaned, smoothed ink on a 3.5 mm
outline backer) scaled to TAG_H tall, with an eyelet lobe on the hanging
axis and Brian's name, phone numbers and email INLAID flush into the back
(bottom) face in black. Prints flat, ink up: the back text is the first
layers (two colours), the backer white, the ink black on top.
Parts: backer (white), ink (black, raised), text (black, inlaid).
"""
import os
import pathlib
import sys

import numpy as np
from build123d import (Align, Compound, FontStyle, Plane, Pos, Text, export_stl, extrude,
                       mirror)
from shapely.affinity import translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_held = {k: os.environ.pop(k) for k in ("SHOW", "EXPORT", "OUT") if k in os.environ}
import logodude as L  # noqa: E402  the badge's traced, cleaned, smoothed ink (its 4 in self-checks run, 9 s)
os.environ.update(_held)

# Brian 2026-10-13: 0.6 nozzle, or 0.4 if the print stays under 1 h 15 min. Built for
# the 0.4 nozzle: at 3 in the face strokes scale to 0.9 to 1.1 mm = two 0.42 mm beads
# (clean, no fill-core modifier needed); at 0.6 the tag would have to grow to 3.5 in.
TAG_H = float(os.environ.get("TAG_IN", 3.0)) * 25.4   # mm, silhouette height (face + hair, outline included), eyelet not counted
BACKER_T = 3.08         # mm, on the 0.4-nozzle 0.16 layer grid (0.2 first layer + 18 x 0.16)
INK_H = 0.96            # mm raised, 6 layers of 0.16 (the badge has 1.0)
MIN_MARGIN = L.MIN_MARGIN
# Eyelet: a round lobe on the backer's centroid axis so the tag hangs straight,
# a hole for a strap loop, blended into the outline with a fillet.
HOLE_D = 6.0            # mm, fits standard worm loops, cable loops and silicone straps
LOBE_R = 6.5            # mm, so the wall past the hole is 3.5 mm like the outline margin
LOBE_FILLET = 4.0       # mm, concave blend between lobe and outline
# Back text, inlaid flush into the bottom face (the first layers). Sized for the
# 0.4 nozzle: Russo One keeps every stroke at 0.25 x cap height, so caps of 3.5 to
# 4.4 mm give 0.9 to 1.1 mm strokes = two 0.42 mm beads, no fill core needed.
FONT = "/home/brian/.local/share/fonts/RussoOne-Regular.ttf"
TEXT_D = 0.52           # mm deep: first layer 0.2 + 2 x 0.16
TEXT_MARGIN = 2.5       # mm, text keeps this far inside the outline (the inlay is only TEXT_D deep)
LINE_GAP = 3.0          # mm, between the lines' bounding boxes
TEXT_TOP_FRAC = 0.87    # top of the name line, as a fraction of TAG_H up from the silhouette bottom
# (text, cap height mm)
LINES = [("BLIETZ", 4.4), ("408.829.5860", 4.0), ("415.407.5201", 4.0), ("bblietz@gmail.com", 3.5)]
if os.environ.get("NOZZLE") == "0.6":   # the 0.6-nozzle alternative (options page only): two 0.62 beads = caps 4.4 to 6.2
    LINES = [("BLIETZ", 6.2), ("bblietz@gmail.com", 5.0), ("408.829.5860", 5.4), ("415.407.5201", 5.4)]
    LINE_GAP, TEXT_TOP_FRAC = 2.2, 0.843
CAP_PER_SIZE = Text("H", font_size=10, font_path=FONT).bounding_box().size.Y / 10

# ---------------------------------------------------------------- scale the badge to TAG_H
K = TAG_H / (L._y1 - L._y0)
for _ in range(4):
    ink_2d, backer_2d = L.build_2d(K)
    _bx0, _by0, _bx1, _by1 = backer_2d.bounds
    K = (TAG_H - ((_by1 - _by0) - (L._y1 - L._y0) * K)) / (L._y1 - L._y0)
ink_2d, sil_2d = L.build_2d(K)
assert abs((sil_2d.bounds[3] - sil_2d.bounds[1]) - TAG_H) < 0.02

# ---------------------------------------------------------------- eyelet
# EYELET=hole (default): round lobe with a HOLE_D hole; =slot: stadium lobe with a
# SLOT_W x SLOT_H slot for buckle straps; =punch: no lobe, the hole punched through
# the forehead between the hair strokes (the silhouette stays as drawn).
EYELET = os.environ.get("EYELET", "hole")
SLOT_W, SLOT_H = 14.0, 3.2
XC = sil_2d.centroid.x                      # hanging axis
_half = (SLOT_W / 2 if EYELET == "slot" else LOBE_R) + MIN_MARGIN + 0.5    # the opening's reach past the axis
_near = ink_2d.intersection(box(XC - _half, sil_2d.bounds[1], XC + _half, sil_2d.bounds[3] + 50))
if EYELET == "punch":
    # highest hole centre on the axis whose MIN_MARGIN ring clears the ink, inside the silhouette
    HOLE_Y = sil_2d.bounds[3]
    while HOLE_Y > sil_2d.bounds[1] and not (Point(XC, HOLE_Y).buffer(HOLE_D / 2 + MIN_MARGIN).within(sil_2d) and
                                             Point(XC, HOLE_Y).buffer(HOLE_D / 2 + MIN_MARGIN).intersection(ink_2d).is_empty):
        HOLE_Y -= 0.25
    hole_2d = Point(XC, HOLE_Y).buffer(HOLE_D / 2, quad_segs=64)
    _outline = sil_2d
elif EYELET == "slot":
    HOLE_Y = _near.bounds[3] + MIN_MARGIN + SLOT_H / 2
    hole_2d = LineString([(XC - SLOT_W / 2 + SLOT_H / 2, HOLE_Y), (XC + SLOT_W / 2 - SLOT_H / 2, HOLE_Y)]).buffer(SLOT_H / 2, quad_segs=32)
    lobe_2d = hole_2d.buffer(LOBE_R - HOLE_D / 2, quad_segs=32)        # same 3.5 mm wall as the round lobe
    _outline = unary_union([sil_2d, lobe_2d]).buffer(LOBE_FILLET, quad_segs=32).buffer(-LOBE_FILLET, quad_segs=32)
else:
    HOLE_Y = _near.bounds[3] + MIN_MARGIN + HOLE_D / 2
    hole_2d = Point(XC, HOLE_Y).buffer(HOLE_D / 2, quad_segs=64)
    lobe_2d = Point(XC, HOLE_Y).buffer(LOBE_R, quad_segs=64)
    _outline = unary_union([sil_2d, lobe_2d]).buffer(LOBE_FILLET, quad_segs=32).buffer(-LOBE_FILLET, quad_segs=32)
assert hole_2d.buffer(MIN_MARGIN).intersection(ink_2d).is_empty, "strap hole runs into the ink"
assert _outline.geom_type == "Polygon" and not _outline.interiors
backer_2d = Polygon(_outline.exterior, [hole_2d.exterior])
assert backer_2d.is_valid
assert hole_2d.buffer(LOBE_R - HOLE_D / 2 - 0.01).within(_outline) if EYELET == "hole" else hole_2d.buffer(2.5).within(_outline), "eyelet wall too thin"
assert ink_2d.buffer(MIN_MARGIN).difference(backer_2d).area < 1e-6, "ink margin lost at the lobe blend"

# ---------------------------------------------------------------- back text (laid out as seen from the back, then mirrored)
# The back is an hourglass: wide face, a waist where the hair arms leave the
# face, a wide forehead band, then the peaks. The block sits above the waist,
# its top at TEXT_TOP, lines centred on the band's own axis.
inner_2d = backer_2d.buffer(-TEXT_MARGIN)
inner_back = Polygon([(-x, y) for x, y in inner_2d.exterior.coords])   # back view: x mirrored
TEXT_TOP = sil_2d.bounds[1] + TEXT_TOP_FRAC * TAG_H
if EYELET == "punch":                       # the hole sits in the forehead: the block moves under it
    TEXT_TOP, LINE_GAP = HOLE_Y - HOLE_D / 2 - TEXT_MARGIN - 0.5, 1.6


def _text(txt, cap):
    return Text(txt, font_size=cap / CAP_PER_SIZE, font_path=FONT, font_style=FontStyle.BOLD,
                align=(Align.CENTER, Align.MIN))


def _poly(comp, n=24):
    out = []
    for f in comp.faces():
        def ring(w):
            pts = []
            for e in w.edges():
                pts += [(p.X, p.Y) for p in e.positions(np.linspace(0, 1, n, endpoint=False))]
            return pts
        out.append(Polygon(ring(f.outer_wire()), [ring(w) for w in f.inner_wires()]).buffer(0))
    return unary_union(out)


def _span(y):
    """Usable x interval of the inner outline at height y (back view), the one on the hanging axis."""
    seg = inner_back.intersection(LineString([(inner_back.bounds[0] - 1, y), (inner_back.bounds[2] + 1, y)]))
    hit = [g for g in getattr(seg, "geoms", [seg]) if not g.is_empty and g.bounds[0] <= -XC <= g.bounds[2]]
    assert hit, f"no usable width at y {y:.1f}"
    return hit[0].bounds[0], hit[0].bounds[2]


_texts, _polys, text_y = [], [], []
_top = TEXT_TOP
for txt, cap in LINES:
    t = _text(txt, cap)
    p = _poly(t)
    _texts.append(t)
    _polys.append(p)
    text_y.append(_top - (p.bounds[3] - p.bounds[1]))
    _top = text_y[-1] - LINE_GAP
TEXT_BLOCK = (text_y[-1] + _polys[-1].bounds[1], TEXT_TOP)
_spans = [_span(y) for y in np.linspace(TEXT_BLOCK[0], TEXT_BLOCK[1], 25)]
XC_BACK = float(np.mean([(a + b) / 2 for a, b in _spans]))          # text axis: centre of the block's own band
for (txt, cap), p, ty in zip(LINES, _polys, text_y):
    x0, y0, x1, y1 = p.bounds
    assert inner_back.contains(box(x0 + XC_BACK, y0 + ty, x1 + XC_BACK, y1 + ty)), f"{txt} does not fit at y {ty:.1f}"

text_back_2d = unary_union([translate(p, XC_BACK, ty) for p, ty in zip(_polys, text_y)])
text_2d = unary_union([Polygon([(-x, yy) for x, yy in g.exterior.coords], [[(-x, yy) for x, yy in h.coords] for h in g.interiors])
                       for g in text_back_2d.geoms])                       # front/model view
assert text_2d.difference(inner_2d).area < 1e-6, "text leaves the text margin"
assert len(text_back_2d.geoms) == sum(len(p.geoms) for p in _polys), "letters merged"

# 3D: faces positioned in back view, mirrored about YZ into model coordinates
_placed = [Pos(XC_BACK, ty, 0) * t for t, ty in zip(_texts, text_y)]
_faces = [f for t in _placed for f in mirror(t, about=Plane.YZ).faces()]
text = Compound([extrude(f, TEXT_D, dir=(0, 0, 1)) for f in _faces])
_cutter = Compound([Pos(0, 0, -1) * extrude(f, TEXT_D + 1, dir=(0, 0, 1)) for f in _faces])

# ---------------------------------------------------------------- solids
backer = extrude(L.to_face(backer_2d, L.OUTLINE_KNOT_MM), BACKER_T, dir=(0, 0, 1)) - _cutter
ink = Compound([Pos(0, 0, BACKER_T) * extrude(L.to_face(p, L.INK_KNOT_MM), INK_H, dir=(0, 0, 1))
                for p in getattr(ink_2d, "geoms", [ink_2d])])

# ---------------------------------------------------------------- checks
bb = backer.bounding_box(optimal=True)
ib = ink.bounding_box(optimal=True)
tb = text.bounding_box(optimal=True)
assert len(backer.solids()) == 1
assert len(ink.solids()) == len(getattr(ink_2d, "geoms", [ink_2d]))
assert len(text.solids()) == len(_faces) == len(text_back_2d.geoms)
_v_backer = backer_2d.area * BACKER_T - text_2d.area * TEXT_D
assert abs(L.mesh_volume(backer) - _v_backer) / _v_backer < 3e-3, "backer volume drift"
assert abs(sum(L.mesh_volume(x) for x in ink.solids()) - ink_2d.area * INK_H) / (ink_2d.area * INK_H) < 2e-3
assert abs(sum(L.mesh_volume(x) for x in text.solids()) - text_2d.area * TEXT_D) / (text_2d.area * TEXT_D) < 5e-3
assert abs(ib.min.Z - BACKER_T) < 1e-6 and abs(ib.max.Z - BACKER_T - INK_H) < 1e-6
assert abs(tb.min.Z) < 1e-6 and abs(tb.max.Z - TEXT_D) < 1e-6
assert bb.size.X <= 256 and bb.size.Y <= 256
assert abs(tb.center().X + text_back_2d.centroid.x) < 0.5, "text was not mirrored into model coordinates"
print(f"tag {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm ({bb.size.X / 25.4:.2f} x {bb.size.Y / 25.4:.2f} in), "
      f"silhouette {TAG_H / 25.4:.2f} in; ink {ib.size.X:.1f} x {ib.size.Y:.1f} mm, {K:.4f} mm/px; "
      f"hole {HOLE_D} at ({XC:.1f}, {HOLE_Y:.1f}); text block y {TEXT_BLOCK[0]:.1f} to {TEXT_BLOCK[1]:.1f} on x {-XC_BACK:.1f}, "
      f"{len(text.solids())} letters, {text_2d.area:.0f} mm2")
for (txt, cap), p, ty in zip(LINES, _polys, text_y):
    a, b = _span(ty + (p.bounds[3] - p.bounds[1]) / 2)
    print(f"  {txt:20s} cap {cap:.1f} mm  width {p.bounds[2] - p.bounds[0]:.1f} of {b - a:.1f} mm usable  bottom y {ty:.1f}")

# ---------------------------------------------------------------- 2D dump for the options page (pipeline/tag_options.py)
if os.environ.get("DUMP_2D"):
    import json

    def _rings(g):
        return [{"outer": list(p.exterior.coords), "holes": [list(h.coords) for h in p.interiors]}
                for p in getattr(g, "geoms", [g])]

    def _stem(g):
        a0 = g.area
        for r in np.arange(0.05, 3.0, 0.01):
            if g.buffer(-r).area < 0.02 * a0:
                return 2 * r

    _face = [p for p in ink_2d.geoms if p is not max(ink_2d.geoms, key=lambda q: q.area)]
    _fw = sorted(2 * p.area / p.length for p in _face)       # typical stroke width of each face piece
    json.dump({"bounds": backer_2d.bounds, "backer": _rings(backer_2d), "ink": _rings(ink_2d), "text": _rings(text_2d),
               "thick": BACKER_T + INK_H, "hole": f"{SLOT_W:.0f} x {SLOT_H:.1f} mm slot" if EYELET == "slot" else f"{HOLE_D:.0f} mm",
               "face_strokes": (_fw[0], _fw[-1]), "eyelet": EYELET, "tag_in": TAG_H / 25.4,
               "lines": [(txt, cap, p.bounds[2] - p.bounds[0], _stem(p)) for (txt, cap), p in zip(LINES, _polys)]},
              open(os.environ["DUMP_2D"], "w"))

# ---------------------------------------------------------------- exports
OUT = pathlib.Path(os.environ.get("OUT", HERE))
if os.environ.get("EXPORT"):
    import trimesh
    for name, part, vol in (("backer", backer, _v_backer), ("ink", ink, ink_2d.area * INK_H),
                            ("text", text, text_2d.area * TEXT_D)):
        f = OUT / f"logodude-tag-{name}.stl"
        export_stl(part, str(f), tolerance=0.005, angular_tolerance=0.1)
        m = trimesh.load(f)
        assert m.is_watertight, f"{f.name} not watertight"
        assert abs(m.volume - vol) / vol < 0.005, f"{f.name} volume drift {m.volume:.1f} vs {vol:.1f}"
        print(f"{f.name}: {len(m.faces)} tris, watertight")

if os.environ.get("SHOW"):
    from ocp_vscode import show, Camera
    show(backer, ink, text, names=["backer (white)", "ink (black)", "back text (black)"],
         colors=["#f4f4f2", "#1d1d1f", "#1d1d1f"],
         reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
