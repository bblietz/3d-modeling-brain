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
  photo_match.py soffit F  z-buffers only the dropped soffit and its two downlights onto
                           picture F (a Gemini output at its own size) and writes
                           F-soffit-overlay.png, the guide for render_in_room.py soffit

Usage: .venv/bin/python projects/Built-in-bench/photo_match.py [check <image> | soffit <image>]
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
from build123d import Cylinder, Pos  # noqa: E402

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
CEILING_IN = 98.5                             # measured through the camera: the pilaster tops (y 124) give 98.6 in, the back
                                              # wall's top edge 98.0; at 96 a strip of ceiling showed above the soffit's face

# ---------------------------------------------------------------- shelves (not in the cut list; picture only)
SHELF_D = 10 * IN
SHELF_T = 1.5 * IN
SHELF_Z0 = [SEAT_Z + CUSHION_H + 20 * IN + i * 14 * IN for i in range(3)]   # undersides: 20 in over the cushion, 14 apart

# ---------------------------------------------------------------- dropped soffit with downlights (picture only)
# a bulkhead flush with the pilaster faces, as in the client's concept picture: one band across the top of the alcove and
# of both pilasters (they stop at its underside like posts under a lintel), running on to the right over the hallway
# opening past the edge of the frame; the door recess to the left keeps its full-height ceiling. Brian 2026-10-23: "the
# soffit is flush with the front and then extends over the hallway"; a box between the pilasters, set back, was wrong.
SOFFIT_DROP = 12 * IN                           # below the ceiling: about 7 ft 2-1/2 in clear inside the alcove
PILASTER_W = 6 * IN                             # each pilaster's face, read off the photo (55 px at 9.4 px per in)
HALL_RUN = 36 * IN                              # how far it runs on past the right pilaster (the frame edge is 14 in past it)
SOFFIT_X0 = -PILASTER_W                         # CAD x: from the left pilaster's outer edge ...
SOFFIT_W = ALCOVE_W + 2 * PILASTER_W + HALL_RUN # ... to beyond the right edge of the picture, 28 in deep throughout
LIGHT_DIA = 4 * IN
LIGHT_X = [ALCOVE_W / 4, 3 * ALCOVE_W / 4]      # two recessed downlights in the underside, over the alcove only
LIGHT_Y = ALCOVE_D / 2

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
    print(f"check: the {CEILING_IN:.1f} in ceiling projects to y {v:.0f} at the back wall, photo shows {CEIL_Y} "
          f"({(CEIL_Y - v) * (D + ALCOVE_D_IN) / F:+.1f} in at the back wall)")


# ---------------------------------------------------------------- what to draw
PAINT = (246, 244, 238)
PANEL_PAINT = (234, 231, 223)   # the painted panel a shade below the frame so its recess reads in the overlay
WALNUT = (88, 58, 38)
MAPLE = (224, 198, 152)
LINEN = (206, 194, 172)
BRASS = (198, 152, 82)
SHADOW = (58, 52, 46)        # case and boxes: only seen in the reveals, read as shadow lines
LAMP = (255, 250, 228)
COLOR = {
    "stile_": PAINT, "rail_": PAINT, "plinth": PAINT, "strip_": PAINT,
    "panel_": PANEL_PAINT, "top": MAPLE, "cushion": LINEN, "pull_": BRASS, "shelf_": MAPLE,   # all-white fronts, maple top and shelves, Brian 2026-10-24
    "soffit": PAINT, "light_": LAMP,
}
LIGHT = np.array([-0.3, -0.55, 0.78])     # toward the light, in (X, d, Z): from the room, above, a little left
LIGHT /= np.linalg.norm(LIGHT)


def color_of(name):
    for k, c in COLOR.items():
        if name == k or name.startswith(k):
            return c
    return SHADOW


def soffit_scene():
    z0 = CEILING_IN * IN - SOFFIT_DROP
    items = [("soffit", _box(SOFFIT_X0, 0, z0, SOFFIT_W, ALCOVE_D, SOFFIT_DROP))]
    for i, x in enumerate(LIGHT_X):     # trim rings standing 1/4 in proud of the underside, so they z-buffer in front of it
        items.append((f"light_{i}", Pos(x, LIGHT_Y, z0 + 0.25 * IN) * Cylinder(LIGHT_DIA / 2, IN)))
    return items


def scene():
    items = list(INST) + list(HW)
    for i, z0 in enumerate(SHELF_Z0):
        items.append((f"shelf_{i}", _box(0, 0, z0, ALCOVE_W, SHELF_D, SHELF_T)))
    return items + soffit_scene()


def render(photo, items=None, sx=1.0, sy=1.0):
    """flat-shaded z-buffer render of the items (default: the whole scene) over the photo; sx, sy scale the
    projection when the photo is a Gemini output at its own size rather than space-photo.png. Returns the RGB array."""
    img = np.asarray(photo.convert("RGB")).astype(np.float32)
    H, W, _ = img.shape
    zbuf = np.full((H, W), np.inf, dtype=np.float32)
    ntri = 0
    for name, solid in (scene() if items is None else items):
        base = np.array(color_of(name), dtype=np.float32)
        verts, tris = solid.tessellate(0.4, 0.3)
        P = np.array([cad_to_cam((v.X, v.Y, v.Z)) for v in verts])          # (X, d, Z) inches
        UV = np.array([project(*p) for p in P]) * (sx, sy)
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
            if name == "soffit":    # painted drywall, nearly unshaded: Gemini keeps the overlay's colors, and a face
                shade = 0.98 if abs(n[2]) < 0.5 else 0.92   # turned away from LIGHT came out as a grey-blue ceiling
            else:
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
    zs = CEILING_IN - SOFFIT_DROP / IN
    xs0, xs1 = xl + SOFFIT_X0 / IN, xl + (SOFFIT_X0 + SOFFIT_W) / IN
    lines["soffit face"] = [(xs0, 0, zs), (xs1, 0, zs), (xs1, 0, CEILING_IN), (xs0, 0, CEILING_IN), (xs0, 0, zs)]
    lines["soffit underside back"] = [(xs0, ALCOVE_D_IN, zs), (xs1, ALCOVE_D_IN, zs)]
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
        top_exp, bot_exp = pts[2][1], pts[0][1]
        # a quarter in from either end (clear of the brass pull); keep the column with the longest walnut run, since a
        # throw or a paw hanging over one end leaves only a stripe of it there
        best = (None, None, None)
        for frac in (0.25, 0.75):
            u = int(round(pts[0][0] + (pts[1][0] - pts[0][0]) * frac))
            bot, top = dark_rows(arr, u, int(top_exp) - 60, int(bot_exp) + 60)   # dark rows: first is the panel top
            if bot is not None and (best[0] is None or top - bot > best[2] - best[1]):
                best = (u, bot, top)
        u, bot, top = best
        if bot is None or (top - bot) / s_face < (FRONT_H - 2 * STILE_W) / IN / 2:
            print(f"panel {i}: no walnut run of panel size a quarter in from either end (painted panels?), the pull check applies")
            continue
        print(f"panel {i} at x {u}: top y {bot} (projected {top_exp:.0f}, {(top_exp - bot) / s_face:+.2f} in), "
              f"bottom y {top} (projected {bot_exp:.0f}, {(bot_exp - top) / s_face:+.2f} in); "
              f"panel height {(top - bot) / s_face:.2f} in, designed {(FRONT_H - 2 * STILE_W) / IN:.2f}")
    # the brass pulls, 8 in long and centered on each front: a true-scale check that works when the panels are painted
    for i in range(len(FRONT_X0)):
        fp = lines[f"front {i}"]
        Xc, Zc = (fp[0][0] + fp[1][0]) / 2, (fp[0][2] + fp[2][2]) / 2
        d_pull = fp[0][1] - 1.25                      # the bar stands 1 in off the face and is 1/2 in square
        uc, vc = project(Xc, d_pull, Zc)
        s_pull = F / (D + d_pull)
        u0, u1 = project(Xc - 4, d_pull, Zc)[0], project(Xc + 4, d_pull, Zc)[0]
        run = brass_run(arr, int(vc) - 6, int(vc) + 6, int(u0) - 30, int(u1) + 30)
        if run is None:
            print(f"pull {i}: no brass found near the projected bar")
            continue
        v, ua, ub = run
        print(f"pull {i}: bar at y {v} from x {ua} to {ub} (projected y {vc:.0f}, x {u0:.0f} to {u1:.0f}; "
              f"{(vc - v) / s_pull:+.2f} in up, {((ua + ub) / 2 - uc) / s_pull:+.2f} in across); "
              f"length {(ub - ua + 1) / s_pull:.2f} in, designed 8.00")
    print(f"scale at the drawer faces: {s_face:.2f} px per in; 1 in of height error is {s_face:.0f} px")


def brass_run(arr, v_lo, v_hi, u_lo, u_hi):
    """the longest row-wise run of brass-colored pixels in the window; returns (row, u_start, u_end) or None. Gemini's
    brass is a dull antique tone, about (170, 119, 98): red well above blue, green a little above it, mid-bright.
    Walnut (about (130, 69, 61)) fails the brightness test, white paint and oatmeal linen fail the red-over-blue test."""
    best = None
    for v in range(v_lo, v_hi + 1):
        row = arr[v, u_lo:u_hi].astype(int)
        ok = (row[:, 0] > row[:, 2] + 40) & (row[:, 1] > row[:, 2] + 12) & (row.mean(axis=1) > 100)
        start = None
        for j, flag in enumerate(list(ok) + [False]):
            if flag and start is None:
                start = j
            elif not flag and start is not None:
                if best is None or j - start > best[2] - best[1] + 1:
                    best = (v, u_lo + start, u_lo + j - 1)
                start = None
    return best


def topedge(dst_path, src_path, out_path, up=4, down=3, feather=1.5):
    """copy the band of the top's front edge (the projected quad between the top's front edge and its underside, wall
    to wall) from src into dst and write out: restores a stage's correct edge after a later Gemini pass washed it out
    (the white-fronts pass turned the maple edge near white). up/down widen the band in photo pixels to take in the
    roundover's highlight above and the shadow line on the frames below; feather is the mask blur in photo pixels.
    Both pictures must be the same size and from the same chain, so every other pixel already agrees."""
    from PIL import ImageFilter
    dst, src = Image.open(dst_path).convert("RGB"), Image.open(src_path).convert("RGB")
    assert dst.size == src.size, (dst.size, src.size)
    photo = Image.open(PHOTO)
    sx, sy = dst.width / photo.width, dst.height / photo.height
    lines = bench_outline()
    (ul, vl), (ur, vr) = [project(*p) for p in lines["wood top front edge"]]
    (bl, wl), (br, wr) = [project(*p) for p in lines["top underside"]]
    poly = [(ul * sx, (vl - up) * sy), (ur * sx, (vr - up) * sy), (br * sx, (wr + down) * sy), (bl * sx, (wl + down) * sy)]
    mask = Image.new("L", dst.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather * sy))
    Image.composite(src, dst, mask).save(out_path)
    m = np.asarray(mask) > 128
    for label, im in (("before", dst), ("source", src), ("after", Image.open(out_path))):
        c = np.asarray(im)[m].mean(axis=0)
        print(f"{label}: band mean RGB ({c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f})")
    print(f"band rows {min(vl, vr) - up:.0f} to {max(wl, wr) + down:.0f} at photo scale, {int(m.sum())} px replaced; wrote",
          os.path.relpath(out_path, VAULT))


if __name__ == "__main__":
    report_camera()
    if len(sys.argv) > 2 and sys.argv[1] == "check":
        check(sys.argv[2])
        sys.exit()
    if len(sys.argv) > 4 and sys.argv[1] == "topedge":
        topedge(sys.argv[2], sys.argv[3], sys.argv[4])
        sys.exit()
    if len(sys.argv) > 2 and sys.argv[1] == "soffit":
        pic = Image.open(sys.argv[2]).convert("RGB")
        photo = Image.open(PHOTO)
        out = render(pic, soffit_scene(), pic.width / photo.width, pic.height / photo.height)
        dst = f"{os.path.splitext(sys.argv[2])[0]}-soffit-overlay.png"
        Image.fromarray(out).save(dst)
        print("wrote", os.path.relpath(dst, VAULT))
        sys.exit()
    photo = Image.open(PHOTO)
    wireframe(photo).save(WIREFRAME)
    print("wrote", os.path.relpath(WIREFRAME, VAULT))
    Image.fromarray(render(photo)).save(OVERLAY)
    print("wrote", os.path.relpath(OVERLAY, VAULT))
