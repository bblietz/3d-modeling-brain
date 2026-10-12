"""Dunlop Tortex Standard 1.0 mm pick, plain (no logo, no texture), PETG.

Outline: outline-dunlop.csv, traced from Brian's caliper photos of the real
pick by pipeline/trace_photo.py (IMG_1657 for the shape, calipers for the
size). outline-351.csv is the generic 351 from the Iron Age SVG pack, kept
only as the cross-check: the Dunlop tip is blunter (4.5 mm vs 3.4 mm radius).
"""
import os
from pathlib import Path
import numpy as np
import trimesh
from build123d import Face, Wire, extrude, export_stl

HERE = Path(__file__).resolve().parent

THICK = 1.0                  # nominal Tortex 1.0 mm; set from calipers when measured
WIDTH, LENGTH = 26.19, 30.38  # caliper readings 2026-10-11, asserted below

pts = [tuple(p) for p in np.loadtxt(HERE / "outline-dunlop.csv", delimiter=",")]
area2 = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
if area2 < 0:      # counter-clockwise winding gives a +Z face normal, so the pick extrudes up from Z=0
    pts.reverse()
pick = extrude(Face(Wire.make_polygon(pts, close=True)), THICK)

bb = pick.bounding_box()
assert len(pick.solids()) == 1
assert abs(bb.size.Z - THICK) < 1e-6 and abs(bb.min.Z) < 1e-6
assert abs(bb.size.X - WIDTH) < 0.02 and abs(bb.size.Y - LENGTH) < 0.02, bb.size

export_stl(pick, str(HERE / "guitar-pick.stl"))
m = trimesh.load(HERE / "guitar-pick.stl")
assert m.is_watertight, "STL not watertight"
print("OK", bb.size, "vol mm3", round(pick.volume, 1), "PETG g ~", round(pick.volume * 1.27e-3, 2))

if os.environ.get("SHOW"):
    from ocp_vscode import show, Camera
    show(pick, names=["pick"], reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
