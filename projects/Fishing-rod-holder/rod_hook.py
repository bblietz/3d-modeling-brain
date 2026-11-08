#!/usr/bin/env python
"""Rod hook: one printed deep-hook that screws to the face of a 1x4.

Brian's picks, 2026-11-07: "use the deep hook design ... make individual deep
hooks that can be screwed into a 1x4 piece of wood." Then: "make the bottom
resting part of the hook have a slot that is angled to help keep the rod there
better" and "remove the top most part of the device that is not over the wood."

Then: "you did the opposite angle for the slot. The slot should angle away from
the wood."

So the hook is an open J: a tab that screws to the board face (two #8), and a
jaw that reaches past the board edge carrying a slot that leans away from the
wood as it goes down (SLOT_LEAN from vertical). The rod drops in at the top,
slides down the ramp away from the board and comes to rest under the lip's
hood; to leave it has to come back up the ramp toward the board and then over
the lip tip. The lip top slopes up toward its tip so a rod set on it rolls in.
The rod lies beside the wood in the slot and never touches the board. The board
hangs from the joist the way the wooden combs do.

Coordinates (inches in the constants, mm in the CAD): x along the board width,
x = 0 at the board edge the jaw reaches past, positive onto the board; y up,
y = 0 at the hook's bottom edge; z the hook thickness, z = 0 against the board.
The rod runs along z. Print orientation: as modelled, back face on the bed.

Run from the vault root:
  .venv/bin/python projects/Fishing-rod-holder/rod_hook.py          # build, check, export
  SHOW=reset .venv/bin/python projects/Fishing-rod-holder/rod_hook.py  # also push to the OCP viewer
"""
import json
import math
import os
from pathlib import Path

from build123d import Box, Cone, Cylinder, Polygon, Pos, export_stl, extrude
from shapely.geometry import Point, Polygon as SPoly, box as sbox

PROJECT = Path(__file__).resolve().parent
IN = 25.4

# ---- the board (a 1x4 on edge, as Brian's combs) -------------------------------
BOARD_W = 3.5
BOARD_T = 0.75

# ---- the hook --------------------------------------------------------------------
T = 0.375          # hook thickness (3/8)
TAB = 1.75         # how far the tab reaches onto the board face (screws live here)
H = 3.25           # tab height, over the board
WEB = 0.125        # the tab's outer edge past the board edge, so the rod never rubs the wood
SLOT_W = 0.875     # slot width, measured across the slot; blanks are 1/4 to 5/8
SLOT_LEAN = 35.0   # degrees from vertical; the slot's bottom sits away from the wood
BELOW = 0.625      # material under the slot's lowest point
Y_LIP = 1.875      # lip top at its inner edge (where the slot opens)
LIP_SLOPE = 0.375  # lip top climbs this much toward its tip: a rod set on the lip rolls in
LIP_MIN = 0.5      # lip thickness at its thinnest, beside the slot's bottom
CORNER_R = 0.25    # outside corners
TIP_R = 0.125      # lip tip and the slot's top edges
RAMP_R = 0.125     # where the tab edge turns into the slot's ramp

X_BACK = -WEB                          # the tab's outer edge
R_SLOT = SLOT_W / 2
PHI = math.radians(SLOT_LEAN)
Y_C = BELOW + R_SLOT                   # centre of the slot's rounded bottom
# the slot's inner wall (the ramp) leaves the tab edge at Y_LIP and leans outward going down
S_IN = (Y_LIP - Y_C + R_SLOT * math.sin(PHI)) / math.cos(PHI)     # ramp length from the bottom tangent to the tab edge
X_C = X_BACK - R_SLOT * math.cos(PHI) - S_IN * math.sin(PHI)      # slot bottom centre, x
S_OUT = (Y_LIP - Y_C - R_SLOT * math.sin(PHI)) / math.cos(PHI)    # outer wall length to the lip top
X_LIP_TOP = X_C + S_OUT * math.sin(PHI) - R_SLOT * math.cos(PHI)  # lip's inner top edge
CANT = -(X_C - R_SLOT) + LIP_MIN       # jaw reach past the board edge
CANT = math.ceil(CANT * 8) / 8         # to the next 1/8
W = CANT + TAB                         # overall width
Y_REST = BELOW                         # the rod's lowest contact
Y_TIP = Y_LIP + LIP_SLOPE              # lip top at the tip: the lift to leave is about Y_TIP - rest
HOOD = X_LIP_TOP - X_C                 # how far the lip's top edge reaches inboard of the resting rod's centre

# ---- screws: two #8, countersunk, 1 in from the board edge --------------------------
SCREW_X = 1.0
SCREW_Y = (0.5625, H - 0.5625)         # 9/16 up from the bottom, 9/16 down from the top
HOLE_D = 5.0                           # mm, #8 clearance
CSK_D = 10.0                           # mm, 90 degree countersink at the front face
CSK_DEPTH = (CSK_D - HOLE_D) / 2       # 2.5 mm

ROD_DIAS = (0.25, 0.375, 0.625)        # blanks the slot must hold and release
MIN_LIFT = 1.4                         # the hold check: no escape below this rise (the plain deep hook gave 1.00)


def slot_arc(n=32):
    """The slot's rounded bottom, from the ramp's tangent point around the low point to the outer wall's."""
    a0 = -PHI                          # the inner (ramp) tangent, measured from +x
    a1 = -PHI - math.pi                # the outer tangent
    return [(X_C + R_SLOT * math.cos(a0 + (a1 - a0) * k / n), Y_C + R_SLOT * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def outline_points():
    """Sharp outline (inches, y up), counterclockwise from the jaw's bottom tip.
    Returns the points and the fillet radius to apply at each (0 for the arc)."""
    pts = [(-CANT, 0.0), (TAB, 0.0), (TAB, H), (X_BACK, H), (X_BACK, Y_LIP)]
    radii = [CORNER_R, CORNER_R, CORNER_R, CORNER_R, RAMP_R]
    arc = slot_arc()
    pts += arc
    radii += [0.0] * len(arc)
    pts += [(X_LIP_TOP, Y_LIP), (-CANT, Y_TIP)]
    radii += [TIP_R, TIP_R]
    return pts, radii


def mm(pts):
    return [(x * IN, y * IN) for x, y in pts]


def final_outline():
    pts, radii = outline_points()
    return rounded_outline(pts, {i: r for i, r in enumerate(radii) if r > 0})


def build_hook():
    hook = extrude(Polygon(*mm(final_outline()), align=None), T * IN)
    for y in SCREW_Y:
        hook -= Pos(SCREW_X * IN, y * IN, T * IN / 2) * Cylinder(HOLE_D / 2, T * IN + 2)
        cone_h = CSK_D / 2 + 0.3
        hook -= Pos(SCREW_X * IN, y * IN, T * IN + 0.3 - cone_h / 2) * Cone(0.0, cone_h, cone_h)
    return hook


def board_stub(length=6.0):
    """A piece of the 1x4 behind the hook: x from 0 to BOARD_W, z from -BOARD_T to 0."""
    return Pos(BOARD_W / 2 * IN, H / 2 * IN, -BOARD_T / 2 * IN) * Box(BOARD_W * IN, length * IN, BOARD_T * IN)


# ---- 2D geometry for the checks and the drawings --------------------------------------
def rounded_outline(pts, radii, n=24):
    """Replace each filleted vertex by its tangent points and arc (convex or concave alike),
    the same construction the CAD's fillet() performs, so the 2D checks match the solid."""
    out = []
    count = len(pts)
    for i, p in enumerate(pts):
        r = radii.get(i, 0.0)
        if r <= 0:
            out.append(p)
            continue
        p0, p1 = pts[i - 1], pts[(i + 1) % count]
        v0 = (p0[0] - p[0], p0[1] - p[1])
        v1 = (p1[0] - p[0], p1[1] - p[1])
        l0, l1 = math.hypot(*v0), math.hypot(*v1)
        v0 = (v0[0] / l0, v0[1] / l0)
        v1 = (v1[0] / l1, v1[1] / l1)
        alpha = math.acos(max(-1.0, min(1.0, v0[0] * v1[0] + v0[1] * v1[1])))
        t = r / math.tan(alpha / 2)
        assert t < l0 and t < l1, f"fillet {r} too big at vertex {i}"
        a = (p[0] + v0[0] * t, p[1] + v0[1] * t)
        b = (p[0] + v1[0] * t, p[1] + v1[1] * t)
        bis = (v0[0] + v1[0], v0[1] + v1[1])
        lb = math.hypot(*bis)
        c = (p[0] + bis[0] / lb * r / math.sin(alpha / 2), p[1] + bis[1] / lb * r / math.sin(alpha / 2))
        ang_a = math.atan2(a[1] - c[1], a[0] - c[0])
        ang_b = math.atan2(b[1] - c[1], b[0] - c[0])
        delta = (ang_b - ang_a + math.pi) % (2 * math.pi) - math.pi
        out += [(c[0] + r * math.cos(ang_a + delta * k / n), c[1] + r * math.sin(ang_a + delta * k / n)) for k in range(n + 1)]
    return out


def solid_2d():
    """The hook outline as a shapely polygon: the very points the CAD extrudes."""
    return SPoly(final_outline()).buffer(0)


def free_space(r):
    big = sbox(-CANT - 4, -4, TAB + 4, H + 4)
    return big.difference(solid_2d()).buffer(-r)


def seat_point(d):
    """Lowest position of the centre of a rod of diameter d anywhere inside the slot."""
    r = d / 2
    free = free_space(r)
    slot = sbox(-CANT, 0, X_BACK, Y_LIP)
    inside = free.intersection(slot)
    assert not inside.is_empty, f"a {d} in rod does not fit the slot"
    lowest = None
    for g in getattr(inside, "geoms", [inside]):
        for x, y in g.exterior.coords:
            if lowest is None or y < lowest[1]:
                lowest = (x, y)
    return lowest


def escape_lift(d):
    """Smallest rise of the rod centre that lets a rod of diameter d reach the outside.
    The centre of a disc of radius r can be anywhere the free space survives an erosion by r.
    Binary-search the ceiling on the centre's height."""
    r = d / 2
    free = free_space(r)
    sx, sy = seat_point(d)
    seat = Point(sx, sy + 0.002)
    outside = Point(-CANT - 2.5, sy)

    def connected(limit):
        region = free.intersection(sbox(-CANT - 4, -4, TAB + 4, limit))
        for g in getattr(region, "geoms", [region]):
            if g.contains(seat) and g.contains(outside):
                return True
        return False

    assert connected(H + 4), f"a {d} in rod cannot get out of the slot at all"
    lo, hi = 0.0, 4.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if connected(seat.y + mid):
            hi = mid
        else:
            lo = mid
    return hi


def rod_probe(d, length=6.0):
    """A rod seated at the lowest point of the slot, running along z through the hook and past the board."""
    sx, sy = seat_point(d)
    return Pos(sx * IN, sy * IN, 0) * Cylinder(d / 2 * IN, length * IN)


def checks(hook):
    report = {}
    assert len(hook.solids()) == 1, "hook is not one solid"
    bb = hook.bounding_box()
    size = (bb.size.X / IN, bb.size.Y / IN, bb.size.Z / IN)
    assert abs(size[0] - W) < 0.01 and abs(size[1] - H) < 0.01 and abs(size[2] - T) < 0.01, size
    report["size_in"] = [round(s, 3) for s in size]
    report["volume_cm3"] = round(hook.volume / 1000, 1)
    report["jaw_height_in"] = {"at the lip": round(Y_LIP, 4), "at the tip": round(Y_TIP, 4)}
    report["jaw_reach_in"] = CANT
    report["slot_lean_deg"] = SLOT_LEAN
    report["hood_in"] = round(HOOD, 3)
    report["lip_min_in"] = round(CANT + (X_C - R_SLOT), 3)
    assert CANT + (X_C - R_SLOT) >= LIP_MIN - 1e-6
    # the rod touches nothing: not the hook when seated (beyond a hair of contact), never the board
    board = board_stub()
    report["seat_in"] = {}
    for d in ROD_DIAS:
        rod = rod_probe(d)
        overlap = (rod & hook).volume
        assert overlap < 2.0, f"{d} in rod intersects the hook when seated ({overlap:.2f} mm3)"
        assert (rod & board).volume < 1e-3, f"{d} in rod touches the board"
        report["seat_in"][str(d)] = [round(v, 3) for v in seat_point(d)]
    assert (hook & board).volume < 1e-3, "hook intersects the board"
    # slot takes the biggest blank with room
    assert SLOT_W >= ROD_DIAS[-1] + 0.25, "slot too narrow for a 5/8 blank"
    # pose-space hold: every blank needs at least MIN_LIFT of rise before it can leave
    report["escape_lift_in"] = {}
    for d in ROD_DIAS:
        lift = escape_lift(d)
        report["escape_lift_in"][str(d)] = round(lift, 3)
        assert lift >= MIN_LIFT, f"{d} in rod escapes with only {lift:.2f} in of lift"
    # wall minimums for the 0.6 nozzle (2 perimeters = 1.24 mm)
    assert WEB * IN >= 1.24 and LIP_MIN * IN >= 1.24 and BELOW * IN >= 1.24
    report["lift_to_leave_in"] = round(Y_TIP - Y_REST, 3)
    report["screws_mm"] = {"hole": HOLE_D, "countersink": CSK_D, "depth": CSK_DEPTH,
                           "positions_in": [[SCREW_X, y] for y in SCREW_Y]}
    return report


if __name__ == "__main__":
    hook = build_hook()
    report = checks(hook)
    stl = PROJECT / "rod-hook.stl"
    export_stl(hook, str(stl))
    import trimesh
    m = trimesh.load(str(stl))
    assert m.is_watertight, "exported STL is not watertight"
    report["stl"] = str(stl)
    report["stl_volume_cm3"] = round(m.volume / 1000, 1)
    (PROJECT / "rod-hook-report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show
        show(hook, board_stub(), rod_probe(0.375), names=["hook", "1x4", "rod 3/8"],
             colors=["#2f6fe4", "#c9a46e", "#333333"],
             reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
