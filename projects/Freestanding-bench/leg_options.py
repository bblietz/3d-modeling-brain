#!/usr/bin/env python
"""Leg options for the freestanding bench, built the way the drawer bench's legs are (Brian 2026-10-26: "look at
the legs for the other bench we designed and let's start there"): proud solid maple corner posts, floor to the
underside of the top, 3/8 in chamfer on the four vertical edges, the end and back panels housed in stopped grooves
in the posts 1/2 in behind the post faces, the drawer fronts running between the front posts 1/4 in behind their
faces. Everything but the posts stops CLEAR (5 in) above the floor for the robot vacuum.

Builds the visible shell (posts, panels, fronts, pulls, top, a floor slab) for each option and captures a full view
and a foot close-up from the OCP viewer (scripts/cad-viewer.sh must have the GPU Chrome tab open). Nothing here
feeds the cut list; the chosen option goes into freestanding_bench.py afterwards.

Usage: .venv/bin/python projects/Freestanding-bench/leg_options.py [A B ...]
Writes projects/Freestanding-bench/images/legs/<opt>-bench.png and <opt>-foot.png.
"""
import os
import subprocess
import sys
import time

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Freestanding-bench"
sys.path.insert(0, PROJ)
from freestanding_bench import *  # noqa: E402,F403
from freestanding_bench import _box, part  # noqa: E402
from build123d import Rectangle, loft, Plane, Pos, chamfer, mirror, Axis, Compound  # noqa: E402

OUT = f"{PROJ}/images/legs"
os.makedirs(OUT, exist_ok=True)

# the drawer bench's post construction (projects/Drawer-bench/drawer_bench.py)
CHAMFER = 0.375 * IN        # post vertical edges, full length
SETBACK = 0.5 * IN          # panel outer face behind the post face
GROOVE_D = 0.375 * IN       # panels housed this deep in the posts
FRONT_SETBACK = 0.25 * IN   # drawer fronts behind the post faces
OH = OVERHANG            # top past the posts, ends and front (3/4); flush at the back
TAPER_TO = 2.0 * IN         # option E: the foot tapers on its two inside faces to this at the floor

OPTIONS = {
    "A": ("2-1/2 in posts", dict(size=2.5 * IN, foot="straight")),
    "B": ("3 in posts, as the drawer bench", dict(size=3.0 * IN, foot="straight")),
    "C": ("3-1/2 in posts", dict(size=3.5 * IN, foot="straight")),
    "D": ("3 in posts, chamfer stopped above a square foot", dict(size=3.0 * IN, foot="stopped")),
    "E": ("3 in posts, foot tapered on the inside faces", dict(size=3.0 * IN, foot="taper")),
}

MAPLE = "#e2c48f"
WHITE = "#fbfbf8"
BRASS = "#b8903f"
FLOOR = "#b9ada0"


def front_post(size, foot, x, y):
    """the low-X front post: outer faces at min X and max Y; the others are mirrors of it"""
    upper_z0 = CLEAR if foot != "straight" else 0.0
    upper = _box(x, y, upper_z0, size, size, TOP_Z0 - upper_z0)
    upper = chamfer(upper.edges().filter_by(Axis.Z), CHAMFER)
    if foot == "straight":
        return upper
    if foot == "stopped":
        return upper + _box(x, y, 0, size, size, CLEAR)
    # taper: the outer faces stay plumb, the two inside faces lean in to TAPER_TO at the floor
    bottom = Pos(x + TAPER_TO / 2, y + size - TAPER_TO / 2, 0) * Rectangle(TAPER_TO, TAPER_TO)
    top = Pos(x + size / 2, y + size / 2, CLEAR) * Rectangle(size, size)
    return upper + loft([bottom, top])


def shell(size, foot):
    X0p, X1p = TOP_X0 + OH, TOP_X1 - OH                 # post outer faces
    Yb, Yf = TOP_Y0, TOP_Y1 - OH - size                 # rear post min Y, front post min Y
    ymid = (Yb + Yf + size) / 2
    pfl = front_post(size, foot, X0p, Yf)
    pfr = mirror(pfl, Plane.YZ.offset((X0p + X1p) / 2))
    ymirror = Plane(origin=(0, ymid, 0), z_dir=(0, 1, 0))     # Plane.XZ's normal points to -Y, so name the plane
    prl = mirror(pfl, ymirror)
    prr = mirror(pfr, ymirror)
    items = [("post_fl", pfl, MAPLE), ("post_fr", pfr, MAPLE), ("post_rl", prl, MAPLE), ("post_rr", prr, MAPLE)]
    # end panels, housed in the posts, 1/2 in behind the post faces
    end = _box(X0p + SETBACK, Yb + size - GROOVE_D, CLEAR, T18, (Yf + GROOVE_D) - (Yb + size - GROOVE_D), TOP_Z0 - CLEAR)
    items += [("end_l", end, WHITE), ("end_r", mirror(end, Plane.YZ.offset((X0p + X1p) / 2)), WHITE)]
    back = _box(X0p + size - GROOVE_D, Yb + SETBACK, CLEAR, (X1p - size + GROOVE_D) - (X0p + size - GROOVE_D), T18, TOP_Z0 - CLEAR)
    items.append(("back", back, WHITE))
    # fronts between the front posts, 1/8 reveals, faces 1/4 behind the post faces, recessed white panels
    open_x0, open_x1 = X0p + size, X1p - size
    fw = (open_x1 - open_x0 - 3 * GAP) / 2
    fh = TOP_Z0 - GAP - CLEAR
    fy1 = Yf + size - FRONT_SETBACK
    for i, fx in enumerate((open_x0 + GAP, open_x0 + 2 * GAP + fw)):
        f = _box(fx, fy1 - FACE_T, CLEAR, fw, FACE_T, fh)
        f -= _box(fx + STILE_W, fy1 - (FACE_T - PANEL_T), CLEAR + STILE_W, fw - 2 * STILE_W, FACE_T - PANEL_T + 1, fh - 2 * STILE_W)
        items.append((f"front_{i}", f, WHITE))
        cx, cz = fx + fw / 2, CLEAR + fh / 2
        bar = _box(cx - PULL_L / 2, fy1 + PULL_STAND, cz - PULL_SQ / 2, PULL_L, PULL_SQ, PULL_SQ)
        items.append((f"pull_{i}", bar, BRASS))
    bottom = _box(X0p + SETBACK + T18, Yb + SETBACK + T18, CLEAR, X1p - X0p - 2 * (SETBACK + T18), fy1 - FACE_T - (Yb + SETBACK + T18), T18)
    items.append(("bottom", bottom, WHITE))
    items.append(("top", part("top"), MAPLE))
    floor = _box(TOP_X0 - 150, TOP_Y0 - 150, -20, TOP_W + 300, TOP_D + 300, 20)
    items.append(("floor", floor, FLOOR))
    return items, dict(X0p=X0p, Yf=Yf, size=size, open_w=open_x1 - open_x0, front_w=fw)


def capture(items, out, position, target, zoom):
    from ocp_vscode import Camera, save_screenshot, set_port, show
    set_port(3939)
    show(*[s for _, s, _ in items], names=[n for n, _, _ in items], colors=[c for _, _, c in items],
         grid=(False, False, False), axes=False, axes0=False,
         reset_camera=Camera.RESET, position=position, target=target, zoom=zoom)
    try:
        subprocess.run(["xdotool", "mousemove", "2", "2"], check=False, timeout=5)
    except Exception:
        pass
    time.sleep(float(os.environ.get("SETTLE", "2.5")))
    save_screenshot(out)
    print("wrote", os.path.relpath(out, VAULT), os.path.getsize(out), "bytes")


if __name__ == "__main__":
    keys = sys.argv[1:] or list(OPTIONS)
    for k in keys:
        name, kw = OPTIONS[k]
        items, g = shell(**kw)
        t = (TOP_X0 + TOP_W / 2, (TOP_Y0 + TOP_Y1) / 2, SEAT_Z / 2)
        capture([it for it in items if it[0] != "floor"], f"{OUT}/{k}-bench.png",
                (t[0] - 1500, t[1] + 2700, t[2] + 650), t, float(os.environ.get("ZOOM", "1.35")))
        # foot close-up: the low-X front post from the room side, a little above the case line
        ft = (g["X0p"] + g["size"] / 2 + 60, g["Yf"] + g["size"] / 2, CLEAR * 0.7)
        capture(items, f"{OUT}/{k}-foot.png", (ft[0] - 650, ft[1] + 900, ft[2] + 330), ft,
                float(os.environ.get("FOOT_ZOOM", "4.5")))
        print(k, name, f"opening {inch(g['open_w'])}, fronts {inch(g['front_w'])} wide")
    print("done")
