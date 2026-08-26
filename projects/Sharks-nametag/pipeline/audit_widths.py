#!/usr/bin/env python
"""Report sub-printable raised-art members in the crisp Sharks-nametag STLs.

The 0.12 mm Bambu preset uses the CLASSIC wall generator with thin-wall
detection off: raised members narrower than 2 perimeters (0.84 mm at 0.42
line width) are silently dropped at slice time. Per Brian (2026-08-07,
v3.20) the source artwork is NOT adapted to this floor - hairline detail
is knowingly left to drop. This script keeps that decision informed: run
it after any geometry change to see exactly what will not print.

Usage: .venv/bin/python projects/Sharks-nametag/pipeline/audit_widths.py
Report-only; exit 0 always.
"""
import os
import numpy as np
import trimesh
from shapely.geometry import Polygon as SPoly
from shapely.ops import polygonize, unary_union

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOOR = 0.50          # v3.23: arachne single-bead floor (the classic-wall floor was 0.84)
RULE = 0.55           # audit threshold (SEAM_W 0.6 nominal minus tessellation slack)
# z-bands of the raised art (crisp): navy/cyan tier 4.2-4.8, white tier
# and surfer 4.2-5.4. Inlays (YSC 3.96-4.2, back text 0-0.6) are flush
# and exempt by design.
BANDS = [("white", 5.1), ("navy", 4.5), ("cyan", 4.5)]


def section(path, z):
    m = trimesh.load_mesh(path)
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return None
    rings = [SPoly(np.asarray(d)[:, :2]).buffer(0) for d in s.discrete if len(d) >= 4]
    faces = list(polygonize(unary_union([r.exterior for r in rings if not r.is_empty])))
    mat = [f for f in faces
           if sum(1 for r in rings if r.contains(f.representative_point())) % 2 == 1]
    return unary_union(mat).buffer(0)


def eff_w(p):
    return 2 * p.area / p.length if p.length else 0.0


def report(g, label):
    opened = g.buffer(-RULE / 2, quad_segs=16).buffer(RULE / 2, quad_segs=16)
    thin = g.difference(opened)
    pieces = sorted((p for p in getattr(thin, "geoms", [thin])
                     if p.area >= 0.05 and eff_w(p) >= 0.10), key=lambda p: -p.area)
    if not pieces:
        print(f"[{label}] all raised members >= {RULE} mm")
        return
    print(f"[{label}] {len(pieces)} sub-{RULE} pieces (will drop or print ragged):")
    for p in pieces[:20]:
        c = p.representative_point()
        b = p.bounds
        ext = max(b[2] - b[0], b[3] - b[1])
        print(f"    area={p.area:6.2f}  eff_w={eff_w(p):.2f}  ext={ext:5.1f}  "
              f"at ({c.x:+6.2f},{c.y:+6.2f})")
    if len(pieces) > 20:
        print(f"    ... and {len(pieces) - 20} more")


for stem, z in BANDS:
    path = f"{PROJ}/sharks-nametag-{stem}.stl"
    g = section(path, z)
    if g is None or g.is_empty:
        print(f"[{stem}@{z}] no material at this z")
        continue
    report(g, f"{stem}@{z}")
