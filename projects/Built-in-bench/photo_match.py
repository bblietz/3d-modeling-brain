#!/usr/bin/env python
"""Project the CAD bench into the photo of the empty alcove at true scale.

The photo is camera-matched from the four floor corners of the alcove (a pinhole
camera solved in closed form: the 66 x 28 in opening gives the distance, focal
length, height and lateral offset of the camera). Every instance in the CAD, the
cushion and three floating shelves are tessellated, projected through that camera
and z-buffered onto the photo with flat shading. The result is a geometrically
exact guide that Gemini only has to make photoreal (render_in_room.py, job
`guided`), instead of asking it to hold "14 inches" from words.

  photo_match.py           writes images/alcove-overlay.png (the guide) and
                           images/alcove-wireframe.png (the camera check: alcove
                           box and bench outline drawn over the photo)
  photo_match.py check F   draws the projected bench outline over Gemini's output F
                           (resized to the photo) and measures where the walnut
                           panels and the bench's bottom edge landed, in pixels and
                           inches, against the projection

Usage: .venv/bin/python projects/Built-in-bench/photo_match.py [check <image>]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
sys.path.insert(0, PROJ)
from built_in_bench import *  # noqa: E402,F403
from built_in_bench import INST, HW, _box  # noqa: E402

PHOTO = f"{PROJ}/images/space-photo.png"
OVERLAY = f"{PROJ}/images/alcove-overlay.png"
WIREFRAME = f"{PROJ}/images/alcove-wireframe.png"

# ---------------------------------------------------------------- the photo (pixels, measured 2026-10-23)
# the baseboard's bottom edge at the alcove's four floor corners, read off 4x crops of space-photo.png
FRONT_L, FRONT_R = (277, 1050), (897, 1051)   # pilaster inner corners at the floor: the 66 in opening, depth 0
BACK_L, BACK_R = (319, 971), (808, 968)       # back wall corners at the floor, 28 in deeper
CEIL_Y = 243                                  # the back wall's top edge (ceiling "about 8 ft" per the brief)
ALCOVE_W_IN = ALCOVE_W / IN
ALCOVE_D_IN = ALCOVE_D / IN
CEILING_IN = 96.0

# ---------------------------------------------------------------- shelves (not in the cut list; picture only)
SHELF_D = 10 * IN
SHELF_T = 1.5 * IN
SHELF_Z0 = [SEAT_Z + CUSHION_H + 20 * IN + i * 14 * IN for i in range(3)]   # undersides: 20 in over the cushion, 14 apart

# ---------------------------------------------------------------- camera
# pinhole camera looking straight into the alcove: u = cx + f (X - Xc) / (D + d), v = cy + f (h - Z) / (D + d)
# with X lateral from the alcove center (in, + to the right), d depth behind the pilaster plane, Z height.
wf = FRONT_R[0] - FRONT_L[0]
wb = BACK_R[0] - BACK_L[0]
D = ALCOVE_D_IN * wb / (wf - wb)            # camera to the pilaster plane
F = wf * D / ALCOVE_W_IN                    # focal length, px
yf = (FRONT_L[1] + FRONT_R[1]) / 2
yb = (BACK_L[1] + BACK_R[1]) / 2
r = (D + ALCOVE_D_IN) / D
CY = (yf - r * yb) / (1 - r)
HCAM = (yf - CY) * D / F                    # camera height above the floor
mf = (FRONT_L[0] + FRONT_R[0]) / 2
mb = (BACK_L[0] + BACK_R[0]) / 2
XC = -(mf - mb) / (F * (1 / D - 1 / (D + ALCOVE_D_IN)))   # camera lateral offset from the alcove center
CX = mf + F * XC / D


def project(X, d, Z):
    """inches (lateral from center, depth behind the pilaster plane, height) -> photo pixels"""
    s = F / (D + d)
    return CX + s * (X - XC), CY + s * (HCAM - Z)


def cad_to_cam(p):
    """CAD mm (x across from the right wall, y from the back wall, z up) -> (X, d, Z) inches"""
    return (p[0] / IN - ALCOVE_W_IN / 2, ALCOVE_D_IN - p[1] / IN, p[2] / IN)


def report_camera():
    print(f"camera: {D:.1f} in from the pilaster faces, {HCAM:.1f} in up, {XC:+.1f} in from center; "
          f"f {F:.0f} px, principal point ({CX:.0f}, {CY:.0f})")
    _, v = project(0, ALCOVE_D_IN, CEILING_IN)
    print(f"check: 8 ft ceiling projects to y {v:.0f}, photo shows {CEIL_Y} "
          f"({(CEIL_Y - v) * (D + ALCOVE_D_IN) / F:+.1f} in at the back wall)")


# ---------------------------------------------------------------- what to draw
PAINT = (246, 244, 238)
WALNUT = (88, 58, 38)
MAPLE = (224, 198, 152)
LINEN = (206, 194, 172)
BRASS = (198, 152, 82)
SHADOW = (58, 52, 46)        # case and boxes: only seen in the reveals, read as shadow lines
COLOR = {
    "stile_": PAINT, "rail_": PAINT, "plinth": PAINT, "strip_": PAINT,
    "panel_": WALNUT, "top": MAPLE, "cushion": LINEN, "pull_": BRASS, "shelf_": MAPLE,
}
LIGHT = np.array([-0.3, -0.55, 0.78])     # toward the light, in (X, d, Z): from the room, above, a little left
LIGHT /= np.linalg.norm(LIGHT)


def color_of(name):
    for k, c in COLOR.items():
        if name == k or name.startswith(k):
            return c
    return SHADOW


def scene():
    items = list(INST) + list(HW)
    for i, z0 in enumerate(SHELF_Z0):
        items.append((f"shelf_{i}", _box(0, 0, z0, ALCOVE_W, SHELF_D, SHELF_T)))
    return items


def render(photo):
    """flat-shaded z-buffer render of the scene over the photo; returns the RGB array"""
    img = np.asarray(photo.convert("RGB")).astype(np.float32)
    H, W, _ = img.shape
    zbuf = np.full((H, W), np.inf, dtype=np.float32)
    ntri = 0
    for name, solid in scene():
        base = np.array(color_of(name), dtype=np.float32)
        verts, tris = solid.tessellate(0.4, 0.3)
        P = np.array([cad_to_cam((v.X, v.Y, v.Z)) for v in verts])          # (X, d, Z) inches
        UV = np.array([project(*p) for p in P])
        depth = D + P[:, 1]
        for a, b, c in tris:
            ntri += 1
            n = np.cross(P[b] - P[a], P[c] - P[a])
            ln = np.linalg.norm(n)
            if ln < 1e-9:
                continue
            n /= ln
            view = np.array([XC, -D, HCAM]) - P[a]      # surface to camera
            if np.dot(n, view) < 0:
                n = -n
            shade = 0.58 + 0.42 * max(0.0, float(np.dot(n, LIGHT)))
            col = np.clip(base * shade, 0, 255)
            (u0, v0), (u1, v1), (u2, v2) = UV[a], UV[b], UV[c]
            x0, x1 = int(max(0, math.floor(min(u0, u1, u2)))), int(min(W - 1, math.ceil(max(u0, u1, u2))))
            y0, y1 = int(max(0, math.floor(min(v0, v1, v2)))), int(min(H - 1, math.ceil(max(v0, v1, v2))))
            if x1 < x0 or y1 < y0:
                continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            area = (u1 - u0) * (v2 - v0) - (u2 - u0) * (v1 - v0)
            if abs(area) < 1e-9:
                continue
            w0 = ((u1 - xs) * (v2 - ys) - (u2 - xs) * (v1 - ys)) / area
            w1 = ((u2 - xs) * (v0 - ys) - (u0 - xs) * (v2 - ys)) / area
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
            if not inside.any():
                continue
            z = w0 * depth[a] + w1 * depth[b] + w2 * depth[c]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            hit = inside & (z < sub)
            sub[hit] = z[hit]
            img[y0:y1 + 1, x0:x1 + 1][hit] = col
    print(f"rendered {ntri} triangles")
    return img.astype(np.uint8)


# ---------------------------------------------------------------- outlines for the checks
def bench_outline():
    """key edges of the design as polylines in (X, d, Z) inches, for drawing over a picture"""
    xl, xr = -ALCOVE_W_IN / 2, ALCOVE_W_IN / 2
    d_front = ALCOVE_D_IN - TOP_Y1 / IN            # the top's front edge
    d_face = ALCOVE_D_IN - (CASE_D + FACE_T) / IN  # the drawer fronts' faces
    z_top = SEAT_Z / IN
    z_cush = (SEAT_Z + CUSHION_H) / IN
    lines = {
        "cushion top front": [(xl, d_front, z_cush), (xr, d_front, z_cush)],
        "wood top front edge": [(xl, d_front, z_top), (xr, d_front, z_top)],
        "top underside": [(xl, d_front, z_top - TS / IN), (xr, d_front, z_top - TS / IN)],
        "floor": [(xl, d_face, 0), (xr, d_face, 0)],
    }
    for i, x0 in enumerate(FRONT_X0):
        X0 = x0 / IN - ALCOVE_W_IN / 2
        z0 = FRONT_Z0 / IN
        w, h = FRONT_W / IN, FRONT_H / IN
        lines[f"front {i}"] = [(X0, d_face, z0), (X0 + w, d_face, z0), (X0 + w, d_face, z0 + h),
                               (X0, d_face, z0 + h), (X0, d_face, z0)]
        s = STILE_W / IN
        lines[f"panel {i}"] = [(X0 + s, d_face, z0 + s), (X0 + w - s, d_face, z0 + s),
                               (X0 + w - s, d_face, z0 + h - s), (X0 + s, d_face, z0 + h - s), (X0 + s, d_face, z0 + s)]
    for i, z0 in enumerate(SHELF_Z0):
        dz = ALCOVE_D_IN - SHELF_D / IN
        lines[f"shelf {i}"] = [(xl, dz, z0 / IN), (xr, dz, z0 / IN), (xr, dz, (z0 + SHELF_T) / IN),
                               (xl, dz, (z0 + SHELF_T) / IN), (xl, dz, z0 / IN)]
    return lines


def draw_lines(im, lines, color, width=2):
    d = ImageDraw.Draw(im, "RGBA")
    for pts in lines.values():
        d.line([project(*p) for p in pts], fill=color, width=width)


def wireframe(photo):
    im = photo.convert("RGB").copy()
    W, Dp = ALCOVE_W_IN / 2, ALCOVE_D_IN
    box = {
        "front floor": [(-W, 0, 0), (W, 0, 0)], "back floor": [(-W, Dp, 0), (W, Dp, 0)],
        "side l": [(-W, 0, 0), (-W, Dp, 0)], "side r": [(W, 0, 0), (W, Dp, 0)],
        "back ceiling": [(-W, Dp, CEILING_IN), (W, Dp, CEILING_IN)],
        "corner l": [(-W, Dp, 0), (-W, Dp, CEILING_IN)], "corner r": [(W, Dp, 0), (W, Dp, CEILING_IN)],
        "base l": [(-W, 0, 0), (-W, 0, 4)], "base r": [(W, 0, 0), (W, 0, 4)],   # the 4 in pilaster baseboards
    }
    draw_lines(im, box, (0, 160, 255, 255), 2)
    draw_lines(im, bench_outline(), (255, 40, 40, 255), 2)
    return im


# ---------------------------------------------------------------- measuring Gemini's output
def dark_rows(arr, u, v_lo, v_hi):
    """rows between v_lo..v_hi at column u that look like walnut (dark, warm)"""
    col = arr[v_lo:v_hi, u].astype(int)
    lum = col.mean(axis=1)
    warm = (col[:, 0] > col[:, 2] + 28)      # brown, not the neutral grey of a shadow on white paint
    ok = (lum < 140) & warm
    # the longest contiguous run: a one-row shadow line under the top's overhang is also dark and warm
    best, start = (0, 0), None
    for i, v in enumerate(list(ok) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start > best[1] - best[0]:
                best = (start, i)
            start = None
    return (v_lo + best[0], v_lo + best[1] - 1) if best[1] > best[0] else (None, None)


def check(path):
    photo = Image.open(PHOTO)
    out = Image.open(path).convert("RGB").resize(photo.size, Image.LANCZOS)
    arr = np.asarray(out)
    lines = bench_outline()
    im = out.copy()
    draw_lines(im, lines, (255, 40, 40, 170), 2)
    dst = f"{os.path.splitext(path)[0]}-check.png"
    im.save(dst)
    print("wrote", os.path.relpath(dst, VAULT))
    s_face = F / (D + ALCOVE_D_IN - (CASE_D + FACE_T) / IN)     # px per inch at the drawer faces
    for i in range(len(FRONT_X0)):
        pts = [project(*p) for p in lines[f"panel {i}"]]
        u = int(round(pts[0][0] + (pts[1][0] - pts[0][0]) / 4))   # a quarter across: clear of the brass pull
        top_exp, bot_exp = pts[2][1], pts[0][1]
        bot, top = dark_rows(arr, u, int(top_exp) - 60, int(bot_exp) + 60)   # dark rows: first is the panel top
        if bot is None:
            print(f"panel {i}: no walnut found at column {u}")
            continue
        print(f"panel {i} at x {u}: top y {bot} (projected {top_exp:.0f}, {(top_exp - bot) / s_face:+.2f} in), "
              f"bottom y {top} (projected {bot_exp:.0f}, {(bot_exp - top) / s_face:+.2f} in); "
              f"panel height {(top - bot) / s_face:.2f} in, designed {(FRONT_H - 2 * STILE_W) / IN:.2f}")
    print(f"scale at the drawer faces: {s_face:.2f} px per in; 1 in of height error is {s_face:.0f} px")


if __name__ == "__main__":
    report_camera()
    if len(sys.argv) > 2 and sys.argv[1] == "check":
        check(sys.argv[2])
        sys.exit()
    photo = Image.open(PHOTO)
    wireframe(photo).save(WIREFRAME)
    print("wrote", os.path.relpath(WIREFRAME, VAULT))
    Image.fromarray(render(photo)).save(OVERLAY)
    print("wrote", os.path.relpath(OVERLAY, VAULT))
