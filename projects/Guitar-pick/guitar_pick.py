"""Dunlop Tortex Standard 1.0 mm pick, plain (no logo, no texture), PETG.

Outline: outline-dunlop.csv, traced from Brian's caliper photos of the real
pick by pipeline/trace_photo.py (IMG_1657 for the shape, calipers for the
size). outline-351.csv is the generic 351 from the Iron Age SVG pack, kept
only as the cross-check: the Dunlop tip is blunter (4.5 mm vs 3.4 mm radius).

Edge: not square (Brian 2026-10-12): a 1.5 mm bevel with a curved lead-in
so there is no line to feel, the same on both faces ("mirror"). Printed
standing on its top edge on a snap-off base (standup.py), so the faces and
bevels are walls; the flat-print variants (sym and the rest) are kept.
The side is a smooth closed spline through the trace (no facets) and both
edge loops get the profile in EDGE. Printed flat, so the underside profile must
stay steep enough for the 0.06 mm layers to support each other (see
pipeline/edge_options.py for the per-layer overhang numbers).

    EDGE=mirror|sym|soft|round|chamfer|bevel|square .venv/bin/python guitar_pick.py   (default mirror; writes guitar-pick-<edge>.stl)
"""
import os
from pathlib import Path
import numpy as np
import trimesh
from build123d import Axis, Face, Spline, Vector, Wire, chamfer, export_stl, extrude, fillet
from shapely.geometry import Point, Polygon

HERE = Path(__file__).resolve().parent

THICK = 1.0                  # Brian's calipers 2026-10-11: 1.0 mm
WIDTH, LENGTH = 26.19, 30.38  # caliper readings 2026-10-11, asserted below
SMOOTH_SIGMA = 0.6           # mm, Gaussian along the outline; stays within 0.06 mm of the trace, kills the 1.7 mm facets

EDGES = {                    # profile on each face edge: (top, bottom); 1.0 mm thick, so the flat left at the rim = 1 - top - bottom
    "square":  None,
    "round":   {"kind": "fillet", "r": 0.45},                                     # R 0.45 both faces, 0.10 mm rim
    "chamfer": {"kind": "chamfer", "top": (0.45, 0.45), "bottom": (0.45, 0.45)},  # 45 degree flats both faces, 0.10 rim
    "bevel":   {"kind": "chamfer", "top": (1.5, 0.35), "bottom": (0.35, 0.35)},   # 1.5 mm Flow-style bevel on top, 45 underneath, 0.30 rim
    # Brian 2026-10-12: like the bevel but no noticeable line, so each crease is blended with a tangent arc. Top: R 5
    # (blend about 1.1 mm wide). Underneath only R 0.35: the pick prints flat, and a wider arc hangs the second layer
    # too far past the first (R 0.5 gives 0.12 mm, R 0.35 gives 0.10, the 45 degree flat beyond it 0.06).
    "soft":    {"kind": "soft", "top": (1.5, 0.35), "top_lead_r": 5.0, "bottom": (0.35, 0.35), "bottom_lead_r": 0.35},
    # Brian 2026-10-12: the top mirrored underneath. The pick's true shape; it cannot print flat (the underside bevel
    # steps each 0.06 mm layer about 0.3 mm past the one below, more than a 0.22 mm line), so it prints standing.
    # rim_r (Brian 2026-10-12, "round off the edges too"): the two creases where the bevels meet the rim are rounded
    # R 0.15, each fillet reaching 0.12 along the rim (R tan 39.7 deg on a 100.6 degree crease), 0.19 flat left.
    # Rim 0.44 (drop 0.28 per face, 10.6 degrees) since 2026-10-13: the first print's 0.30 rim was a single 0.22 mm
    # line at every layer's two ends, so the slicer closed the wall loop there and, where the snap-off neck joined,
    # printed the neck as a separate bead ending on that spot; the shoulders came out with chunks missing. At 0.44
    # the rim is two lines and the wall loop runs straight through the edge and the neck (standup.py).
    "mirror":  {"kind": "soft", "top": (1.5, 0.28), "top_lead_r": 5.0, "bottom": (1.5, 0.28), "bottom_lead_r": 5.0, "rim_r": 0.15},
    # The widest symmetric bevel the flat print carries without support (Brian 2026-10-12: mirrored, no support
    # material): 38 degrees, 0.45 wide, 0.35 drop on both faces, creases blended R 0.35. Underneath, layer 2 sits
    # 0.11 mm past layer 1 (half a line, the same as the round profile) and the band's layers 0.077 (a third of a
    # line). 0.52 wide (34 degrees) measured 0.121 and 0.089; 0.6 wide (30 degrees) 0.137 and 0.103, too far.
    "sym":     {"kind": "soft", "top": (0.45, 0.35), "top_lead_r": 0.35, "bottom": (0.45, 0.35), "bottom_lead_r": 0.35},
}


def smooth_outline(raw, step=0.25, sigma=SMOOTH_SIGMA, n_out=160):
    """Resample the traced polygon every `step` mm, Gaussian-smooth along arc length, stretch to the caliper readings."""
    seg = np.roll(raw, -1, 0) - raw
    s = np.concatenate([[0], np.cumsum(np.hypot(*seg.T))])
    u = np.arange(0, s[-1], step)
    closed = np.vstack([raw, raw[:1]])
    dense = np.column_stack([np.interp(u, s, closed[:, 0]), np.interp(u, s, closed[:, 1])])
    k = int(np.ceil(3 * sigma / step))
    w = np.exp(-0.5 * (np.arange(-k, k + 1) * step / sigma) ** 2)
    w /= w.sum()
    sm = np.column_stack([np.convolve(np.r_[dense[-k:, i], dense[:, i], dense[:k, i]], w, mode="valid") for i in range(2)])
    out = sm[np.linspace(0, len(sm), n_out, endpoint=False).astype(int)]
    out[:, 0] *= WIDTH / (out[:, 0].max() - out[:, 0].min())
    ymin, ymax = out[:, 1].min(), out[:, 1].max()
    out[:, 1] = (out[:, 1] - ymax) * LENGTH / (ymax - ymin)      # top edge back at y = 0, tip at y = -LENGTH
    return out


def outline():
    """The smooth closed outline: (raw trace, its spline, a dense sample of the spline as (x, y) with the top edge at y = 0)."""
    raw = np.loadtxt(HERE / "outline-dunlop.csv", delimiter=",")
    nxt = np.roll(raw, -1, 0)
    if (raw[:, 0] * nxt[:, 1] - nxt[:, 0] * raw[:, 1]).sum() < 0:    # shoelace: clockwise trace
        raw = raw[::-1]          # counter-clockwise winding gives a +Z face normal, so the pick extrudes up from Z=0
    pts = smooth_outline(raw)
    side = Spline(*[Vector(x, y, 0) for x, y in pts], periodic=True)
    samp = np.array([(v.X, v.Y) for v in (side.position_at(t) for t in np.linspace(0, 1, 4000, endpoint=False))])
    return raw, side, samp


def build(edge="mirror"):
    raw, side, samp = outline()

    # the spline stays close to the trace and convex (no wiggles between the trace points)
    trace = Polygon(raw)
    dev = max(trace.exterior.distance(Point(p)) for p in samp)
    assert dev < 0.1, f"spline strays {dev:.3f} mm from the trace"
    hull_gap = 1 - Polygon(samp).area / Polygon(samp).convex_hull.area
    assert hull_gap < 1e-4, f"outline is not convex (hull gap {hull_gap:.2e})"

    pick = extrude(Face(Wire([side])), THICK)
    spec = EDGES[edge]
    if spec and spec["kind"] == "fillet":
        pick = fillet(pick.edges().group_by(Axis.Z)[0] + pick.edges().group_by(Axis.Z)[-1], spec["r"])
    elif spec:
        (bt, bs), (tt, ts) = spec["bottom"], spec["top"]
        pick = chamfer(pick.edges().group_by(Axis.Z)[0], bt, bs, reference=pick.faces().sort_by(Axis.Z)[0])
        pick = chamfer(pick.edges().group_by(Axis.Z)[-1], tt, ts, reference=pick.faces().sort_by(Axis.Z)[-1])
        if spec["kind"] == "soft":   # round off the crease where each chamfer meets its face (the face's outer edge loop)
            pick = fillet(pick.faces().sort_by(Axis.Z)[0].edges(), spec["bottom_lead_r"])
            pick = fillet(pick.faces().sort_by(Axis.Z)[-1].edges(), spec["top_lead_r"])
        if spec.get("rim_r"):        # round the rim's two creases: the rim is the (near-)vertical face centred at half height
            rim = min(pick.faces(), key=lambda f: abs(f.center().Z - THICK / 2))
            pick = fillet(rim.edges(), spec["rim_r"])

    bb = pick.bounding_box()
    assert len(pick.solids()) == 1
    assert abs(bb.size.Z - THICK) < 1e-6 and abs(bb.min.Z) < 1e-6
    assert abs(bb.size.X - WIDTH) < 0.02 and abs(bb.size.Y - LENGTH) < 0.02, bb.size
    return pick


if __name__ == "__main__":
    edge = os.environ.get("EDGE", "mirror")
    pick = build(edge)
    export_stl(pick, str(HERE / f"guitar-pick-{edge}.stl"))      # the print STL (pick on its base) comes from standup.py
    m = trimesh.load(HERE / f"guitar-pick-{edge}.stl")
    assert m.is_watertight, "STL not watertight"
    bb = pick.bounding_box()
    print("OK", edge, bb.size, "vol mm3", round(pick.volume, 1), "PETG g ~", round(pick.volume * 1.27e-3, 2))

    if os.environ.get("SHOW"):
        from ocp_vscode import show, Camera
        show(pick, names=["pick"], reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
