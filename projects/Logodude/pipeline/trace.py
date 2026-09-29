"""Trace logo-dude.png 1:1 into polygons (pixel coords, y down).

Iso-contour at 50% gray on the lightly blurred scan (subpixel boundary),
nested into shapely Polygons with holes. Paper specks below MIN_AREA_PX are
dropped; everything else, dry-brush streaks included, stays as drawn.
Writes traced.json: {"px_per_art_width": ..., "polys": [{"outer": [...], "holes": [[...]]}]}
"""
import json
import pathlib

import numpy as np
from contourpy import FillType, contour_generator
from PIL import Image, ImageFilter
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "images" / "logo-dude.png"
OUT = HERE.parent / "traced.json"
THRESH = 128          # 50% gray: ink boundary
BLUR_PX = 0.8         # just enough to kill scan grain; keeps brush edges
MIN_AREA_PX = 40      # paper specks; the smallest real flecks run ~60+ px


def trace():
    img = Image.open(SRC).convert("L").filter(ImageFilter.GaussianBlur(BLUR_PX))
    z = np.asarray(img, dtype=float)
    z = np.pad(z, 2, constant_values=255.0)          # close contours at the border
    gen = contour_generator(z=z, fill_type=FillType.OuterOffset)
    pts_list, offs_list = gen.filled(-1.0, THRESH)
    polys = []
    for pts, offs in zip(pts_list, offs_list):
        rings = [pts[offs[i]:offs[i + 1]] - 2.0 for i in range(len(offs) - 1)]
        p = Polygon(rings[0], rings[1:]).buffer(0)
        polys.extend(getattr(p, "geoms", [p]))
    polys = [p for p in polys if p.area >= MIN_AREA_PX]
    return unary_union(polys)


if __name__ == "__main__":
    art = trace()
    geoms = list(getattr(art, "geoms", [art]))
    data = {"source": str(SRC.name), "polys": [
        {"outer": list(g.exterior.coords), "holes": [list(h.coords) for h in g.interiors]}
        for g in geoms]}
    OUT.write_text(json.dumps(data))
    x0, y0, x1, y1 = art.bounds
    print(f"{len(geoms)} ink shapes, {sum(len(g.interiors) for g in geoms)} holes, "
          f"area {art.area:.0f} px2, bounds {x1 - x0:.0f} x {y1 - y0:.0f} px -> {OUT.name}")
