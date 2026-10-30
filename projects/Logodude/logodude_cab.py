"""Logo Dude for the front of the walnut 1x12 (Cab-Blietz-1x12-hardwood), size samples.

Brian 2026-10-30: "create a 2.5, 3 and 3.5 in version of the logo dude and I will
pick the size I want." Each is the badge (logodude.py: traced, cleaned, smoothed
ink on a die-cut white backer) rescaled so the backer is WIDTH in wide, with the
outline margin scaled along with the art so every size keeps the badge's look.
Plain backs: the screw mount (cab-logo-options.html, A or B) goes onto the size
Brian picks, since its spots depend on the size. 0.4 nozzle grid like the tag:
0.2 first layer + 0.16 layers. Print flat, ink up, two colours, one change.

WIDTHS=2.5,3,3.5 (default) builds every size; EXPORT=1 writes
logodude-cab-<w>-{backer,ink}.stl per size, each centred on its own origin;
SHOW=1 pushes all of them side by side to the viewer."""
import os
import pathlib
import sys

from build123d import Compound, Pos, extrude

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
EXPORT, SHOW = os.environ.pop("EXPORT", None), os.environ.pop("SHOW", None)   # not for logodude.py's own blocks
import logodude as L  # noqa: E402  (builds the 4 in badge on import)

WIDTHS_IN = [float(w) for w in os.environ.get("WIDTHS", "2.5,3,3.5").split(",")]
BADGE_W = 104.5          # mm, the 4 in badge's width: the margin reference (3.5 mm at this width)
BACKER_T = 3.08          # mm, 0.2 + 18 x 0.16
INK_H = 0.96             # mm raised, 6 x 0.16
GAP = 12.0               # mm between samples in the viewer layout


def build(w_in):
    """One sample: (backer solid, ink compound, ink_2d, backer_2d, K, s), centred at the origin."""
    W = w_in * 25.4
    s = W / BADGE_W
    L.MARGIN, L.MARGIN_GROW, L.MIN_MARGIN, L.SMOOTH_OUTLINE_MM = 3.5 * s, 5.0 * s, 2.5 * s, 2.5 * s
    K = L.K * s
    for _ in range(4):
        ink_2d, backer_2d = L.build_2d(K)
        x0, _, x1, _ = backer_2d.bounds
        K *= W / (x1 - x0)
    ink_2d, backer_2d = L.build_2d(K)
    backer = extrude(L.to_face(backer_2d, L.OUTLINE_KNOT_MM * s), BACKER_T, dir=(0, 0, 1))
    pieces = list(getattr(ink_2d, "geoms", [ink_2d]))
    ink = Compound([Pos(0, 0, BACKER_T) * extrude(L.to_face(p, L.INK_KNOT_MM * s), INK_H, dir=(0, 0, 1))
                    for p in pieces])
    # checks (tessellated mesh, see logodude.py on OCC and periodic splines)
    bb, ib = backer.bounding_box(optimal=True), ink.bounding_box(optimal=True)
    assert len(backer.solids()) == 1 and len(ink.solids()) == len(pieces) == 6
    assert abs(bb.size.X - W) < 0.02, f"{w_in} in sample is {bb.size.X:.3f} mm wide, want {W}"
    assert abs(L.mesh_volume(backer) - backer_2d.area * BACKER_T) / (backer_2d.area * BACKER_T) < 2e-3
    assert abs(sum(L.mesh_volume(x) for x in ink.solids()) - ink_2d.area * INK_H) / (ink_2d.area * INK_H) < 2e-3
    assert abs(ib.min.Z - BACKER_T) < 1e-6 and abs(ib.max.Z - BACKER_T - INK_H) < 1e-6
    assert ink_2d.buffer(2.5 * s - 0.01).difference(backer_2d).area < 1e-6, "ink too close to the outline"
    print(f"{w_in:g} in: backer {bb.size.X:.1f} x {bb.size.Y:.1f} x {BACKER_T} mm, ink {ib.size.X:.1f} x {ib.size.Y:.1f} mm, "
          f"margin {3.5 * s:.2f} mm, face strokes {1.2 * s:.2f} to {1.5 * s:.2f} mm (the badge's 1.2 to 1.5 scaled), "
          f"{K:.4f} mm/px, "
          f"about {(backer_2d.area * BACKER_T + ink_2d.area * INK_H) / 1000 * 1.27:.0f} g")
    return backer, ink, ink_2d, backer_2d, K, s


samples = {w: build(w) for w in WIDTHS_IN}

OUT = pathlib.Path(os.environ.get("OUT", HERE))
if EXPORT:
    import trimesh
    from build123d import export_stl
    for w, (backer, ink, ink_2d, backer_2d, K, s) in samples.items():
        tag = f"{w:g}".replace(".", "")
        for name, part, vol in (("backer", backer, backer_2d.area * BACKER_T), ("ink", ink, ink_2d.area * INK_H)):
            f = OUT / f"logodude-cab-{tag}-{name}.stl"
            export_stl(part, str(f), tolerance=0.005, angular_tolerance=0.1)
            m = trimesh.load(f)
            assert m.is_watertight, f"{f.name} not watertight"
            assert abs(m.volume - vol) / vol < 0.002, f"{f.name} volume drift"
            print(f"{f.name}: {len(m.faces)} tris, watertight")

if SHOW:
    from ocp_vscode import show, Camera
    parts, names, colors = [], [], []
    x = 0.0
    for w, (backer, ink, *_) in samples.items():
        half = w * 25.4 / 2
        x += half
        parts += [Pos(x, 0, 0) * backer, Pos(x, 0, 0) * ink]
        names += [f"{w:g} in backer (white)", f"{w:g} in ink (black)"]
        colors += ["#f4f4f2", "#1d1d1f"]
        x += half + GAP
    show(*parts, names=names, colors=colors,
         reset_camera=Camera.RESET if SHOW == "reset" else Camera.KEEP)
