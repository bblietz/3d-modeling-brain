#!/usr/bin/env python
"""Rod hook: one printed deep-hook pocket that screws to the face of a 1x4.

Brian's pick, 2026-11-07: "use the deep hook design ... make individual deep
hooks that can be screwed into a 1x4 piece of wood." The board hangs from the
joist the way the wooden combs do; each hook screws to the board face with two
#8 screws and cantilevers past the board edge, so the rod lies beside the wood
in the printed pocket and never touches the board.

Coordinates (inches in the constants, mm in the CAD): x along the board width,
x = 0 at the board edge the hooks hang past, positive onto the board; y up,
y = 0 at the hook's bottom edge; z the hook thickness, z = 0 against the board.
The rod runs along z. Print orientation: as modelled, back face on the bed.

Run from the vault root:
  .venv/bin/python projects/Fishing-rod-holder/rod_hook.py          # build, check, export
  SHOW=reset .venv/bin/python projects/Fishing-rod-holder/rod_hook.py  # also push to the OCP viewer
"""
import json
import os
from pathlib import Path

from build123d import (Align, Axis, Box, Circle, Cone, Cylinder, Polygon, Pos, RectangleRounded,
                       export_stl, extrude)
from shapely.geometry import Point, Polygon as SPoly, box as sbox
from shapely.ops import unary_union

PROJECT = Path(__file__).resolve().parent
IN = 25.4

# ---- the board (a 1x4 on edge, as Brian's combs) -------------------------------
BOARD_W = 3.5
BOARD_T = 0.75

# ---- the hook --------------------------------------------------------------------
T = 0.375          # hook thickness (3/8). 1/2 is the stiffer alternative; both pass the checks
TAB = 1.75         # how far the hook reaches onto the board face (screws live here)
LIP_W = 0.75       # lip between the mouth and the pocket
LIP_H = 0.625      # lip top above the pocket floor, at the pocket side
SLOPE = 0.375      # the mouth floor is this much higher than the lip top: the rod rolls in
POCKET_W = 0.875   # pocket width; blanks are 1/4 to 5/8
CHANNEL_H = 1.25   # mouth height, measured at the mouth
WEB = 0.125        # pocket back wall to the board edge, so the rod never rubs the wood
BELOW = 0.625      # material under the pocket floor
ABOVE = 0.375      # material over the channel ceiling
CHAMFER = 0.25     # at both mouth corners
CORNER_R = 0.25    # outline corners

CANT = LIP_W + POCKET_W + WEB          # cantilever past the board edge: 1-3/4
W = CANT + TAB                         # hook width: 3-1/2
Y_FLOOR = BELOW
R_POCKET = POCKET_W / 2
X_ARC = -WEB - R_POCKET                # pocket centreline
Y_ARC = Y_FLOOR + R_POCKET
Y_LIP = Y_FLOOR + LIP_H
Y_MOUTH = Y_LIP + SLOPE                # 1 in above the pocket floor: the lift to leave
Y_CEIL = Y_MOUTH + CHANNEL_H
H = Y_CEIL + ABOVE                     # hook height: 3-1/4

# ---- screws: two #8, countersunk, 1 in from the board edge --------------------------
SCREW_X = 1.0
SCREW_Y = (0.5625, H - 0.5625)         # 9/16 up from the bottom, 9/16 down from the top
HOLE_D = 5.0                           # mm, #8 clearance
CSK_D = 10.0                           # mm, 90 degree countersink at the front face
CSK_DEPTH = (CSK_D - HOLE_D) / 2       # 2.5 mm

ROD_DIAS = (0.25, 0.375, 0.625)        # blanks the pocket must hold and release
MIN_LIFT = 0.95                        # the hold check: no escape below this rise


def pocket_void_points():
    """Channel polygon (inches, y up), mouth at x = -CANT, open past the mouth."""
    ch = CHAMFER
    return [
        (-CANT - 0.5, Y_MOUTH - ch), (-CANT, Y_MOUTH - ch), (-CANT + ch, Y_MOUTH),
        (-WEB - POCKET_W, Y_LIP),                     # floor slopes down to the lip's inner edge
        (-WEB - POCKET_W, Y_ARC), (-WEB, Y_ARC),      # the pocket walls, down to the arc centre
        (-WEB, Y_CEIL), (-CANT + ch, Y_CEIL), (-CANT, Y_CEIL + ch), (-CANT - 0.5, Y_CEIL + ch),
    ]


def mm(pts):
    return [(x * IN, y * IN) for x, y in pts]


def build_hook():
    outline = Pos((W / 2 - CANT) * IN, H / 2 * IN) * RectangleRounded(W * IN, H * IN, CORNER_R * IN)
    channel = Polygon(*mm(pocket_void_points()), align=None)
    arc = Pos(X_ARC * IN, Y_ARC * IN) * Circle(R_POCKET * IN)
    face = outline - channel - arc
    hook = extrude(face, T * IN)
    for y in SCREW_Y:
        hook -= Pos(SCREW_X * IN, y * IN, T * IN / 2) * Cylinder(HOLE_D / 2, T * IN + 2)
        cone_h = CSK_D / 2 + 0.3
        hook -= Pos(SCREW_X * IN, y * IN, T * IN + 0.3 - cone_h / 2) * Cone(0.0, cone_h, cone_h)
    return hook


def board_stub(length=6.0):
    """A piece of the 1x4 behind the hook: x from 0 to BOARD_W, z from -BOARD_T to 0."""
    return Pos(BOARD_W / 2 * IN, H / 2 * IN, -BOARD_T / 2 * IN) * Box(BOARD_W * IN, length * IN, BOARD_T * IN)


def rod_probe(d, length=6.0):
    """A rod seated on the pocket floor, running along z through the hook and past the board."""
    return Pos(X_ARC * IN, (Y_FLOOR + d / 2) * IN, 0) * Cylinder(d / 2 * IN, length * IN)


# ---- 2D pose-space hold check --------------------------------------------------------
def solid_2d():
    outline = sbox(-CANT, 0, TAB, H).buffer(-CORNER_R, join_style=2).buffer(CORNER_R, quad_segs=16)
    void = unary_union([SPoly(pocket_void_points()), Point(X_ARC, Y_ARC).buffer(R_POCKET, 64)])
    return outline.difference(void)


def escape_lift(d, solid=None):
    """Smallest rise of the rod centre that lets a rod of diameter d reach the outside.
    The centre of a disc of radius r can be anywhere the free space survives an erosion by r.
    Binary-search the ceiling on the centre's height."""
    solid = solid or solid_2d()
    r = d / 2
    big = sbox(-CANT - 4, -4, TAB + 4, H + 4)
    free = big.difference(solid).buffer(-r)
    seat = Point(X_ARC, Y_FLOOR + r + 0.002)   # a hair above the floor: the arc is a polygon
    outside = Point(-CANT - 2.5, Y_FLOOR + r)

    def connected(limit):
        region = free.intersection(sbox(-CANT - 4, -4, TAB + 4, limit))
        for g in getattr(region, "geoms", [region]):
            if g.contains(seat) and g.contains(outside):
                return True
        return False

    assert connected(H + 4), f"a {d} in rod cannot get out of the pocket at all"
    lo, hi = 0.0, 3.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if connected(seat.y + mid):
            hi = mid
        else:
            lo = mid
    return hi


def checks(hook):
    report = {}
    assert len(hook.solids()) == 1, "hook is not one solid"
    bb = hook.bounding_box()
    size = (bb.size.X / IN, bb.size.Y / IN, bb.size.Z / IN)
    assert abs(size[0] - W) < 0.01 and abs(size[1] - H) < 0.01 and abs(size[2] - T) < 0.01, size
    report["size_in"] = [round(s, 3) for s in size]
    report["volume_cm3"] = round(hook.volume / 1000, 1)
    # the rod touches nothing: not the hook when seated, never the board
    board = board_stub()
    for d in ROD_DIAS:
        rod = rod_probe(d)
        assert (rod & hook).volume < 1e-3, f"{d} in rod intersects the hook when seated"
        assert (rod & board).volume < 1e-3, f"{d} in rod touches the board"
    # nothing of the hook pokes into the board (the hook sits flat on its face)
    assert (hook & board).volume < 1e-3, "hook intersects the board"
    # mouth takes the biggest blank with room
    assert CHANNEL_H >= ROD_DIAS[-1] + 0.5, "mouth too low for a 5/8 blank"
    # pose-space hold: every blank needs at least MIN_LIFT of rise before it can leave
    solid = solid_2d()
    report["escape_lift_in"] = {}
    for d in ROD_DIAS:
        lift = escape_lift(d, solid)
        report["escape_lift_in"][str(d)] = round(lift, 3)
        assert lift >= MIN_LIFT, f"{d} in rod escapes with only {lift:.2f} in of lift"
    # wall minimums for the 0.6 nozzle (2 perimeters = 1.24 mm)
    assert WEB * IN >= 1.24 and LIP_W * IN >= 1.24 and BELOW * IN >= 1.24 and ABOVE * IN >= 1.24
    report["lift_to_leave_in"] = round(Y_MOUTH - Y_FLOOR, 3)
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
