"""Top-surface coverage analyzer: rasterize the extrusions of one G-code
layer (with the slicer's LINE_WIDTH hints, arcs included) and compare them
with the exposed white top regions from the STLs, to see WHERE the white
tops are left unfilled (Brian 2026-08-23: SANTA CRUZ, CITY, stars and
ball patches show gaps).

Usage: top_coverage.py <plate_1.gcode> <out_dir> [cx cy]
  cx, cy = world position of the tag center (default 128 128).
Writes PNGs (extrusions colored by feature over the white polygon
outlines; uncovered pixels in red) and prints coverage stats per window.
"""
import os
import re
import sys
import math

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
from shapely.ops import unary_union

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Sharks-nametag"
gcode, out_dir = sys.argv[1], sys.argv[2]
CX, CY = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (128.0, 128.0)
os.makedirs(out_dir, exist_ok=True)
PX = 0.02  # mm per pixel

COLORS = {"Outer wall": (220, 40, 40), "Inner wall": (240, 140, 40), "Top surface": (40, 170, 60),
          "Gap infill": (200, 40, 200), "Internal solid infill": (60, 90, 220), "Bridge": (40, 190, 200),
          "Bottom surface": (120, 120, 40), "Sparse infill": (160, 160, 160)}

# ------------------------------------------------------------ parse gcode
layers = {}   # z -> list of (x0,y0,x1,y1,w,feature)
x = y = 0.0
z = None
w = 0.42
feat = "?"
with open(gcode, errors="ignore") as f:
    for line in f:
        if line.startswith("; Z_HEIGHT:"):
            z = round(float(line.split(":")[1]), 2)
        elif line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line.startswith("; LINE_WIDTH:"):
            w = float(line.split(":")[1])
        elif line[:3] in ("G1 ", "G0 ", "G2 ", "G3 "):
            parts = line.split(";")[0].split()
            vals = {p[0]: float(p[1:]) for p in parts[1:] if p[0] in "XYZEIJ" and len(p) > 1}
            nx, ny = vals.get("X", x), vals.get("Y", y)
            e = vals.get("E", 0.0)
            if e > 0 and z is not None:
                if parts[0] in ("G2", "G3") and ("I" in vals or "J" in vals):
                    cx, cy = x + vals.get("I", 0.0), y + vals.get("J", 0.0)
                    r = math.hypot(x - cx, y - cy)
                    a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
                    if parts[0] == "G2":           # clockwise
                        while a1 >= a0:
                            a1 -= 2 * math.pi
                    else:
                        while a1 <= a0:
                            a1 += 2 * math.pi
                    n = max(2, int(abs(a1 - a0) * r / 0.15) + 1)
                    px, py = x, y
                    for i in range(1, n + 1):
                        a = a0 + (a1 - a0) * i / n
                        qx, qy = cx + r * math.cos(a), cy + r * math.sin(a)
                        layers.setdefault(z, []).append((px, py, qx, qy, w, feat))
                        px, py = qx, qy
                else:
                    layers.setdefault(z, []).append((x, y, nx, ny, w, feat))
            x, y = nx, ny
print("layers parsed:", len(layers), "| top z:", max(layers))

# -------------------------------------------------- exposed white regions
# STL_DIR=<dir> to analyze a different build (files wip-<color>.stl, as the
# model writes them with SCRATCH=<dir>); default = the canonical STLs
_sd = os.environ.get("STL_DIR")
_stl = (lambda c: f"{_sd}/wip-{c}.stl") if _sd else (lambda c: f"{PROJ}/sharks-nametag-{c}.stl")
white = trimesh.load(_stl("white"))
navy = trimesh.load(_stl("navy"))
cyan = trimesh.load(_stl("cyan"))


def polys_at(mesh, zz):
    sec = mesh.section(plane_origin=[0, 0, zz], plane_normal=[0, 0, 1])
    if sec is None:
        return []
    p2, _ = sec.to_2D(to_2D=np.eye(4))
    return [Polygon(np.asarray(p.exterior.coords)[:, :2],
                    [np.asarray(i.coords)[:, :2] for i in p.interiors]) for p in p2.polygons_full]


zs = sorted(set(round(v[2], 2) for v in white.vertices))
top2 = max(zs)                      # tier-2 tops (letters, CITY, frame)
base_top = max(zz for zz in zs if zz < top2 - 0.5)   # disc top (stars, ball patches)
tier2 = unary_union(polys_at(white, top2 - 0.05))
disc = unary_union(polys_at(white, base_top - 0.05))
covered = unary_union(polys_at(navy, base_top + 0.3) + polys_at(cyan, base_top + 0.3) + polys_at(white, base_top + 0.3))
exposed_disc = disc.difference(covered)
print(f"white tier-2 top z {top2} area {tier2.area:.1f} mm2 | disc top z {base_top}, exposed area {exposed_disc.area:.1f} mm2")

WINDOWS = {  # name: (model x0, x1, y0, y1, layer z, region)
    "banner_city": (-29, 29, -21, -2, top2, tier2),
    # every letter layer below the top (tier-2 art is 5 layers): a slot in
    # a lower layer shows as a groove even when the top layer covers it
    **{f"banner_L{i}": (-29, 29, -21, -2, round(top2 - 0.12 * i, 2), tier2) for i in range(1, 5)},
    "stars_left": (-38, -12, -5, 30, base_top, exposed_disc),
    "ball": (-20, 20, -3, 30, base_top, exposed_disc),
    "stars_right": (12, 38, -5, 30, base_top, exposed_disc),
}

try:
    from scipy import ndimage
except ImportError:
    ndimage = None

for name, (x0, x1, y0, y1, lz, region) in WINDOWS.items():
    W, H = int((x1 - x0) / PX), int((y1 - y0) / PX)
    img = Image.new("RGB", (W, H), (25, 25, 25))
    dr = ImageDraw.Draw(img)
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)

    def to_px(px, py):
        return ((px - CX - x0) / PX, (y1 - (py - CY)) / PX)   # y up

    # the 0.2 mm first layer shifts the 0.12 grid by 0.08, so the slicer's
    # layer under a design height h is the highest Z_HEIGHT <= h + 0.005
    lz = max(zz for zz in layers if zz <= lz + 0.005)
    segs = layers.get(lz, [])
    n_in = 0
    for sx, sy, ex, ey, sw, sf in segs:
        if not (x0 - 2 <= sx - CX <= x1 + 2 and y0 - 2 <= sy - CY <= y1 + 2):
            continue
        n_in += 1
        p0, p1 = to_px(sx, sy), to_px(ex, ey)
        wp = max(1, int(round(sw / PX)))
        col = COLORS.get(sf, (200, 200, 200))
        dr.line([p0, p1], fill=col, width=wp)
        dm.line([p0, p1], fill=255, width=wp)
        for p in (p0, p1):
            dr.ellipse([p[0] - wp / 2, p[1] - wp / 2, p[0] + wp / 2, p[1] + wp / 2], fill=col)
            dm.ellipse([p[0] - wp / 2, p[1] - wp / 2, p[0] + wp / 2, p[1] + wp / 2], fill=255)
    # region mask + outlines
    rmask = Image.new("L", (W, H), 0)
    dr2 = ImageDraw.Draw(rmask)
    geoms = list(region.geoms) if hasattr(region, "geoms") else [region]
    for g in geoms:
        if g.is_empty or not g.bounds or g.bounds[2] < x0 or g.bounds[0] > x1 or g.bounds[3] < y0 or g.bounds[1] > y1:
            continue
        ext = [((px - x0) / PX, (y1 - py) / PX) for px, py in g.exterior.coords]
        dr2.polygon(ext, fill=255)
        dr.line(ext + [ext[0]], fill=(255, 255, 255), width=1)
        for ring in g.interiors:
            pts = [((px - x0) / PX, (y1 - py) / PX) for px, py in ring.coords]
            dr2.polygon(pts, fill=0)
            dr.line(pts + [pts[0]], fill=(255, 255, 255), width=1)
    r = np.asarray(rmask) > 0
    e = np.asarray(mask) > 0
    # shrink the region by 1 px ring so the outline itself does not count
    unc = r & ~e
    area_r = r.sum() * PX * PX
    area_u = unc.sum() * PX * PX
    # paint uncovered in red
    arr = np.asarray(img).copy()
    arr[unc] = (255, 0, 0)
    Image.fromarray(arr).save(f"{out_dir}/{name}_z{lz}.png")
    feats = {}
    for sx, sy, ex, ey, sw, sf in segs:
        if x0 - 2 <= sx - CX <= x1 + 2 and y0 - 2 <= sy - CY <= y1 + 2:
            feats[sf] = feats.get(sf, 0) + math.hypot(ex - sx, ey - sy)
    print(f"\n[{name}] layer z {lz}: {n_in} segments; feature lengths mm: " + ", ".join(f"{k} {v:.0f}" for k, v in sorted(feats.items(), key=lambda kv: -kv[1])))
    print(f"  region area {area_r:.1f} mm2, UNCOVERED {area_u:.2f} mm2 = {100*area_u/max(area_r,1e-9):.1f}%")
    if ndimage is not None and unc.any():
        lab, n = ndimage.label(unc)
        sizes = ndimage.sum(unc, lab, range(1, n + 1))
        big = [(i + 1, s * PX * PX) for i, s in enumerate(sizes) if s * PX * PX >= 0.05]
        big.sort(key=lambda t: -t[1])
        print(f"  {n} uncovered blobs, {len(big)} >= 0.05 mm2; largest:")
        for lab_id, a in big[:12]:
            ys, xs = np.where(lab == lab_id)
            bx0, bx1 = xs.min() * PX + x0, xs.max() * PX + x0
            by0, by1 = y1 - ys.max() * PX, y1 - ys.min() * PX
            print(f"    {a:5.2f} mm2  model x {bx0:6.1f}..{bx1:6.1f}  y {by0:6.1f}..{by1:6.1f}  ({bx1-bx0:.2f} x {by1-by0:.2f})")
