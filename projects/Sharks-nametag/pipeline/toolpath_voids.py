"""Stacked-void metric on the SANTA letter tier of a sliced plate.

Rasterizes the extrusion paths of the letter-tier layers at 0.02 mm/px
(line width from the G-code `; LINE_WIDTH:` hints, arcs included, round
ends) and measures, inside the SANTA letter outlines of each coupon:
  visible  = pixels uncovered in >= 3 of the top 5 letter layers, opened
             with a 0.13 mm disk (mm2); the "stacked void" that shows
  top int  = uncovered area of the top layer inside a 0.30 mm inset (mm2)
  starts   = extrusion path starts inside the letters on the top layer
             (and the mean over the top 5 letter layers)
Reference values (full W1 coupons, 2026-08-24): 0.2 V0 0.03/0.31, V7o
0.00/0.02, V3 0.06/0.05; 0.4 C0 0.23/0.34, C7 0.00/0.00, C8 0.00/0.15.
Those were measured WITHOUT the S (the W1 window cuts the S at x -22 and
the old tool dropped the fragments): this tool reproduces them on the
same slices with `--clip-x -20.5` (S excluded); the full-outline numbers
include the S. The top layer's fill direction alternates with the layer
count parity (see fillcore_coupons.py), so C7/C8 swap roles between the
18-layer W1 plate and the 9-layer thin plate (the thin plate has the
real tag's parity).

Fill direction (2026-08-25, C7 bake): per measured layer the length-
weighted dominant direction of the top-surface / internal-solid fill
segments inside the letter outlines (deg, 0 = along x, 90 = along y = along
the letter stems) and the length fraction within 15 deg of it. The tag must
reproduce the judged coupon's top-layer direction (layer-count parity).

Usage: toolpath_voids.py <sliced.3mf | plate_1.gcode> --layout thin|w1|tag --nozzle 0.2|0.4
         [--png out.png] [--clip-x -22] [--xs 58,128,198]
  layout thin = fillcore_coupons.py plates (x 58/128/198, letters-only window)
  layout w1   = the full W1 coupons (exports/fillcore-coupons-02/04.3mf)
  layout tag  = a real tag (batch_roster.py single at plate center, --xs 128):
                all nine SANTA CRUZ letters, tag z as is
  --clip-x X  = restrict the outlines to tag x >= X (w1 clips the S at -22;
                pass -22 on a thin plate for a like-for-like comparison)
"""
import argparse
import math
import os
import re
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.affinity import translate
from shapely.geometry import Point, box
from shapely.ops import unary_union

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)
import fillcore_coupons as fc  # noqa: E402
import fillcore_mod as fm  # noqa: E402

PX = 0.02          # mm per pixel
OPEN_DISK = 0.13   # mm, opening disk diameter for the visible metric
INSET = 0.30       # mm, top-interior inset
STACK_MIN = 3      # of the top 5 letter layers
W1 = (-22.0, 4.0, -17.0, 11.0)   # x0, x1, y0, y1 of the full coupons' window (coupons02.py)
UNDER_ART_W1 = 1.0
ANGLE_FEATS = ("Top surface", "Internal solid infill")
ANGLE_TOL = 15.0   # deg
COLORS = {"Outer wall": (220, 40, 40), "Inner wall": (240, 140, 40), "Top surface": (40, 170, 60),
          "Gap infill": (200, 40, 200), "Internal solid infill": (60, 90, 220), "Bridge": (40, 190, 200),
          "Bottom surface": (120, 120, 40), "Sparse infill": (160, 160, 160)}


def load_gcode(path):
    if path.endswith(".3mf"):
        with zipfile.ZipFile(path) as z:
            return z.read("Metadata/plate_1.gcode").decode(errors="ignore")
    with open(path, errors="ignore") as f:
        return f.read()


def parse_layers(gcode):
    """z -> list of segments (x0, y0, x1, y1, width, feature, is_start)."""
    layers = {}
    x = y = 0.0
    z = None
    w = 0.42
    feat = "?"
    extruding = False
    for line in gcode.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = round(float(line.split(":")[1]), 3)
            extruding = False
        elif line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line.startswith("; LINE_WIDTH:") or line.startswith("; WIDTH:"):
            w = float(line.split(":")[1])
        elif line[:3] in ("G1 ", "G0 ", "G2 ", "G3 "):
            parts = line.split(";")[0].split()
            vals = {}
            for p in parts[1:]:
                if p[0] in "XYZEIJ" and len(p) > 1:
                    try:
                        vals[p[0]] = float(p[1:])
                    except ValueError:
                        pass
            nx, ny = vals.get("X", x), vals.get("Y", y)
            e = vals.get("E", 0.0)
            moved = ("X" in vals) or ("Y" in vals)
            if e > 0 and moved and z is not None:
                segs = layers.setdefault(z, [])
                start = not extruding
                if parts[0] in ("G2", "G3") and ("I" in vals or "J" in vals):
                    cx, cy = x + vals.get("I", 0.0), y + vals.get("J", 0.0)
                    r = math.hypot(x - cx, y - cy)
                    a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
                    if parts[0] == "G2":
                        while a1 >= a0:
                            a1 -= 2 * math.pi
                    else:
                        while a1 <= a0:
                            a1 += 2 * math.pi
                    n = max(2, int(abs(a1 - a0) * r / 0.15) + 1)
                    px_, py_ = x, y
                    for i in range(1, n + 1):
                        a = a0 + (a1 - a0) * i / n
                        qx, qy = cx + r * math.cos(a), cy + r * math.sin(a)
                        segs.append((px_, py_, qx, qy, w, feat, start))
                        start = False
                        px_, py_ = qx, qy
                else:
                    segs.append((x, y, nx, ny, w, feat, start))
                extruding = True
            elif moved or e < 0 or parts[0] == "G0":
                extruding = False
            x, y = nx, ny
    return layers


def coupon_layouts(layout, xs, nozzle, plate_y=128.0):
    """Per coupon: plate offset (tag -> plate = tag + off) and z tiers."""
    if layout == "tag":
        G = fm.letter_geometry(fm.BANNER_BOX, 9, window_checks=False)
        cx, cy, z_shift = 0.0, 0.0, 0.0
    else:
        G = fc.letter_geometry()
        if layout == "thin":
            cx, cy = G["center"]
            z_shift = G["banner_top"] - fc.STUB - fc.SLAB[nozzle]
        elif layout == "w1":
            cx, cy = (W1[0] + W1[1]) / 2, (W1[2] + W1[3]) / 2
            z_shift = G["disc_top"] - UNDER_ART_W1
        else:
            raise ValueError(layout)
    return G, [dict(x=x, off=(x - cx, plate_y - cy)) for x in xs], G["banner_top"] - z_shift, G["letter_top"] - z_shift


def disk(diam_mm):
    r = max(1, int(round(diam_mm / PX / 2)))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return (xx * xx + yy * yy) <= r * r


def rasterize(segs, x0, y1, W, H, mask_only=False):
    img = None if mask_only else Image.new("RGB", (W, H), (25, 25, 25))
    dr = None if mask_only else ImageDraw.Draw(img)
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)
    x1, y0 = x0 + W * PX, y1 - H * PX
    for sx, sy, ex, ey, sw, sf, _ in segs:
        if max(sx, ex) < x0 - 1 or min(sx, ex) > x1 + 1 or max(sy, ey) < y0 - 1 or min(sy, ey) > y1 + 1:
            continue
        p0 = ((sx - x0) / PX, (y1 - sy) / PX)
        p1 = ((ex - x0) / PX, (y1 - ey) / PX)
        wp = max(1, int(round(sw / PX)))
        dm.line([p0, p1], fill=255, width=wp)
        for p in (p0, p1):
            dm.ellipse([p[0] - wp / 2, p[1] - wp / 2, p[0] + wp / 2, p[1] + wp / 2], fill=255)
        if dr is not None:
            col = COLORS.get(sf, (200, 200, 200))
            dr.line([p0, p1], fill=col, width=wp)
            for p in (p0, p1):
                dr.ellipse([p[0] - wp / 2, p[1] - wp / 2, p[0] + wp / 2, p[1] + wp / 2], fill=col)
    return np.asarray(mask) > 0, img


def poly_mask(geom, x0, y1, W, H, draw_outline=None):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for g in (geom.geoms if hasattr(geom, "geoms") else [geom]):
        if g.is_empty:
            continue
        ext = [((px - x0) / PX, (y1 - py) / PX) for px, py in g.exterior.coords]
        d.polygon(ext, fill=255)
        if draw_outline is not None:
            draw_outline.line(ext + [ext[0]], fill=(255, 255, 255), width=1)
        for ring in g.interiors:
            pts = [((px - x0) / PX, (y1 - py) / PX) for px, py in ring.coords]
            d.polygon(pts, fill=0)
            if draw_outline is not None:
                draw_outline.line(pts + [pts[0]], fill=(255, 255, 255), width=1)
    return np.asarray(m) > 0


def fill_direction(segs, lmask, x0, y1, W, H):
    """Length-weighted dominant direction (deg, 0..180) of the fill segments
    whose midpoint lies inside the letter mask, the length fraction within
    ANGLE_TOL of it, and the total fill length (mm)."""
    c = s_ = tot = 0.0
    kept = []
    for sx, sy, ex, ey, _, sf, _ in segs:
        if sf not in ANGLE_FEATS:
            continue
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        px, py = int((mx - x0) / PX), int((y1 - my) / PX)
        if not (0 <= px < W and 0 <= py < H and lmask[py, px]):
            continue
        L = math.hypot(ex - sx, ey - sy)
        if L < 1e-6:
            continue
        a = math.atan2(ey - sy, ex - sx)
        c += L * math.cos(2 * a)
        s_ += L * math.sin(2 * a)
        tot += L
        kept.append((a, L))
    if tot == 0:
        return None, 0.0, 0.0
    dom = math.degrees(math.atan2(s_, c) / 2) % 180
    if dom > 179.5:
        dom -= 180
    near = sum(L for a, L in kept if min(abs((math.degrees(a) - dom) % 180), 180 - abs((math.degrees(a) - dom) % 180)) <= ANGLE_TOL)
    return dom, near / tot, tot


def measure(gcode, layout, xs, nozzle, labels=None, clip_x=None, png=None, top_n=5):
    layers = parse_layers(gcode)
    G, coupons, banner_top, letter_top = coupon_layouts(layout, xs, nozzle)
    letters_tag = unary_union(G["letters"])
    if layout == "w1":
        letters_tag = letters_tag.intersection(box(W1[0], W1[2], W1[1], W1[3]))
    if clip_x is not None:
        letters_tag = letters_tag.intersection(box(clip_x, -1e3, 1e3, 1e3))
    zs = sorted(layers)
    # letter-tier layers: slice center above the banner top (layer height from consecutive z)
    tier = []
    for i, z in enumerate(zs):
        h = z - zs[i - 1] if i else z
        if z - h / 2 > banner_top + 1e-6:
            tier.append(z)
    top = tier[-top_n:]
    results = []
    panels = []
    for ci, c in enumerate(coupons):
        off = c["off"]
        letters = translate(letters_tag, off[0], off[1])
        inset = letters.buffer(-INSET)
        b = letters.bounds
        x0, y1 = b[0] - 1.0, b[3] + 1.0
        W, H = int((b[2] - b[0] + 2.0) / PX), int((b[3] - b[1] + 2.0) / PX)
        lmask = poly_mask(letters, x0, y1, W, H)
        imask = poly_mask(inset, x0, y1, W, H) if not inset.is_empty else np.zeros_like(lmask)
        near = letters.buffer(0.1)
        stack = np.zeros((H, W), int)
        per_layer = []
        top_img = None
        top_unc = None
        for z in top:
            segs = layers.get(z, [])
            cov, img = rasterize(segs, x0, y1, W, H, mask_only=(z != top[-1] or png is None))
            unc = lmask & ~cov
            stack += unc
            starts = sum(1 for s in segs if s[6] and x0 <= s[0] <= x0 + W * PX and y1 - H * PX <= s[1] <= y1
                         and near.contains(Point(s[0], s[1])))
            per_layer.append((z, unc.sum() * PX * PX, starts) + fill_direction(segs, lmask, x0, y1, W, H))
            if z == top[-1]:
                top_img, top_unc = img, unc
        vis = ndimage.binary_opening(stack >= STACK_MIN, structure=disk(OPEN_DISK))
        vis_area = vis.sum() * PX * PX
        top_int = (top_unc & imask).sum() * PX * PX
        label = labels[ci] if labels else f"x{c['x']:.0f}"
        results.append(dict(label=label, visible=vis_area, top_interior=top_int, starts_top=per_layer[-1][2],
                            starts_mean=sum(p[2] for p in per_layer) / len(per_layer),
                            angle_top=per_layer[-1][3], along_frac_top=per_layer[-1][4], fill_len_top=per_layer[-1][5],
                            per_layer=per_layer, letter_area=lmask.sum() * PX * PX))
        if png:
            dr = ImageDraw.Draw(top_img)
            poly_mask(letters, x0, y1, W, H, draw_outline=dr)
            arr = np.asarray(top_img).copy()
            arr[top_unc] = (255, 120, 0)
            arr[vis] = (255, 0, 0)
            im = Image.fromarray(arr)
            d = ImageDraw.Draw(im)
            ang = per_layer[-1][3]
            d.text((6, 4), f"{label}  z {top[-1]:.2f}  visible {vis_area:.2f} mm2  top interior {top_int:.2f} mm2  starts {per_layer[-1][2]}"
                   + (f"  fill dir {ang:.0f} deg ({per_layer[-1][4]*100:.0f}% within {ANGLE_TOL:.0f})" if ang is not None else ""),
                   fill=(255, 255, 255))
            panels.append(im)
    if png and panels:
        Wt = max(p.width for p in panels)
        Ht = sum(p.height for p in panels) + 4 * (len(panels) - 1)
        sheet = Image.new("RGB", (Wt, Ht), (0, 0, 0))
        yy = 0
        for p in panels:
            sheet.paste(p, (0, yy))
            yy += p.height + 4
        sheet.save(png)
    return dict(tier=tier, top=top, banner_top=banner_top, letter_top=letter_top, results=results, n_layers=len(zs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--layout", choices=["thin", "w1", "tag"], required=True)
    ap.add_argument("--nozzle", choices=["0.2", "0.4"], required=True)
    ap.add_argument("--png")
    ap.add_argument("--clip-x", type=float, default=None)
    ap.add_argument("--xs", default=None, help="coupon/tag plate x list (default 58,128,198; tag 128)")
    a = ap.parse_args()
    xs = [float(v) for v in (a.xs or ("128" if a.layout == "tag" else "58,128,198")).split(",")]
    labels = ["tag"] if a.layout == "tag" else \
        ([v[0] for v in fc.NOZZLES[a.nozzle]["variants"]][:len(xs)] if len(xs) == 3 else None)
    gcode = load_gcode(a.path)
    r = measure(gcode, a.layout, xs, a.nozzle, labels=labels, clip_x=a.clip_x, png=a.png)
    print(f"{os.path.basename(a.path)}: {r['n_layers']} layers, letter tier {len(r['tier'])} layers "
          f"(z {r['tier'][0]:.2f}..{r['tier'][-1]:.2f}, banner top {r['banner_top']:.2f}), top {len(r['top'])} = {', '.join(f'{z:.2f}' for z in r['top'])}"
          + (f"; outlines clipped to tag x >= {a.clip_x}" if a.clip_x is not None else ""))
    print(f"{'coupon':8} {'visible':>8} {'top int':>8} {'starts':>7} {'mean5':>6}   per-layer uncovered mm2 (starts)")
    for c in r["results"]:
        pl = "  ".join(f"{u:.2f}({s})" for _, u, s, *_ in c["per_layer"])
        print(f"{c['label']:8} {c['visible']:8.2f} {c['top_interior']:8.2f} {c['starts_top']:7d} {c['starts_mean']:6.0f}   {pl}")
    print(f"fill direction inside the letters (deg, 0 = along x, 90 = along the stems; length fraction within {ANGLE_TOL:.0f} deg; fill mm):")
    for c in r["results"]:
        pl = "  ".join((f"z{z:.2f}: {ang:.0f} deg {fr*100:.0f}% {L:.0f}mm" if ang is not None else f"z{z:.2f}: no fill")
                       for z, _, _, ang, fr, L in c["per_layer"])
        print(f"{c['label']:8} {pl}")


if __name__ == "__main__":
    main()
