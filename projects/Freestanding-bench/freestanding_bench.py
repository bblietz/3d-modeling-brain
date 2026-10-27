#!/usr/bin/env python
"""Freestanding bench for the 66 x 28 in former wet-bar alcove: the built-in bench's drawers, all-white
frame-and-panel fronts, solid maple top and 3 in cushion carried on four proud solid maple corner posts, the way the
drawer bench (projects/Drawer-bench) is built, with CLEAR (5 in) of open floor under everything but the posts for the
robot vacuum. The client asked for a freestanding bench with room for the Roomba on 2026-10-26; the built-in design
stays untouched in projects/Built-in-bench in case they go back.

Posts (Brian's pick A from the leg options, 2026-10-26): 2-1/2 in square soft maple, floor to the underside of the
top, 3/8 in chamfer on all four vertical edges full length, straight to the floor. The painted 3/4 ply end panels and
the 1/2 ply back are housed in stopped grooves in the posts, 1/2 in behind the post faces, with the panels' bottom
corners notched so the housed tongue starts 1-1/2 in above the panel bottom and the groove end hides behind the
un-housed bottom (the drawer bench's detail). The drawer fronts run between the front posts 1/4 in behind their faces
with 1/8 reveals. The case bottom sits in rabbets in the ends and the back, notched around the posts. The drawer
runners mount the drawer bench's way on the post side (front screws into the post's inner face, Blum rear bracket on
the back) and the frameless way on the partition side.

Room: the top is 64 x 24-3/4 (1 in of air to each wall, rear edge 1/4 in off the back wall, front edge 3 in back from
the pilaster faces as before). The rear posts are notched at the floor for the alcove's baseboard and shoe (skip the
notch if the baseboard comes out, BASEBOARD_NOTCH = False). The 1/4 in wall gap and the 1/2 in back are what let the
21 in Blum runners keep their 557 mm inside depth behind fronts that sit 3 in back from the pilasters.

What carried over unchanged (Brian's locked picks): wood top at 14 in (seat 17 in), 1-1/2 in maple frames around 1/2
in paint-grade panels inset 1/4 in on the T&G bit set, all painted white, 8 in brass bar pulls, 3/4 in overhang past
the posts with eased arrises, one full-depth cushion, 21 in Blum TANDEM 563H, 1/2 in Baltic birch boxes 6-1/2 in
tall (the 5 in of clear floor come out of the drawers at the fixed seat height), Osmo Natural on the bare maple.

Axes as in built_in_bench.py: X across the alcove (0 at the wall on your RIGHT when you face the bench from the
room; _l/_r suffixes are model names, the bench is symmetric), Y depth (0 at the back wall, +Y toward the room),
Z up (0 at the floor). Units mm; inch constants are written as n * IN. One named solid per part in PARTS, every
placed instance in INST, hardware (slides, pulls, cushion) in HW for the viewer only.

Run:  .venv/bin/python projects/Freestanding-bench/freestanding_bench.py
      SHOW=reset ...   push to the OCP viewer (scripts/cad-viewer.sh)
      TMP_STL=path ... export an STL for scripts/render_stl.py
      EXPORT=1 ...     write cutlist.md/.csv and the STEP
"""
import os
import sys

from build123d import *  # noqa: F403

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Freestanding-bench"
sys.path.insert(0, f"{VAULT}/scripts")
from cutlist import inch_frac, write_cut_list  # noqa: E402

IN = 25.4


def inch(mm):
    return inch_frac(mm, 32)


# ---------------------------------------------------------------- the space
ALCOVE_W = 66 * IN          # between the pilasters (X, 0 at the wall on your right from the room)
ALCOVE_D = 28 * IN          # back wall to the pilaster faces (Y)
TOP_SETBACK = 3 * IN        # top front edge back from the pilaster faces (as the built-in)
BASEBOARD_H = 4 * IN        # the alcove's baseboard stays; it and its shoe stand about 1-1/4 in off the wall
BASEBOARD_T = 1.25 * IN
BASEBOARD_NOTCH = os.environ.get("BASEBOARD_NOTCH", "1") != "0"   # notch the rear posts over it (0 if it comes out)

# ---------------------------------------------------------------- picks
SEAT_Z = 14 * IN            # top face of the wood top (seat 17 in with the cushion, kept for the senior dog)
CUSHION_H = 3 * IN
CLEAR = 5 * IN              # floor to the underside of everything but the posts: the robot vacuum (tallest Roomba 3.9 in)
SIDE_AIR = 1.0 * IN         # top end to each wall, so the piece slides in and out
WALL_GAP = 0.25 * IN        # rear posts and top rear edge to the back wall
OVERHANG = 0.75 * IN        # top past the posts at the ends and the front; flush with the posts at the back
GAP = 0.125 * IN            # reveals: fronts to posts, between the fronts, under the top
ROUND = 0.125 * IN          # eased arrises of the top: front and both ends

# ---------------------------------------------------------------- stock (actual, MEASURE)
T18 = 18.0                  # 3/4 maple ply: ends, bottom, partition
T12 = 12.0                  # 1/2 Baltic birch (drawer boxes), 1/2 paint-grade panels, 1/2 maple ply back
TS = 0.75 * IN              # solid maple: top, cleat
FACE_T = T18                # the fronts are milled to the ply thickness

# ---------------------------------------------------------------- posts (the drawer bench's construction)
POST = 2.5 * IN             # square; soft maple, 12/4 or an 8/4 plus 4/4 glue-up
CHAMFER = 0.375 * IN        # the four vertical edges, full length
SETBACK = 0.5 * IN          # panel outer face behind the post face
GROOVE_D = 0.375 * IN       # panels housed this deep in the posts
NOTCH_H = 1.5 * IN          # panel bottom corners notched GROOVE_D x this: the housed tongue starts here
GROOVE_CLR = 0.75 * IN      # post groove ends this far below the tongue start, hidden behind the un-housed bottom
FRONT_SETBACK = 0.25 * IN   # drawer fronts behind the post faces
BB_NOTCH_D = 1.5 * IN       # rear posts: notch over the baseboard and shoe, from the rear face
BB_NOTCH_H = BASEBOARD_H + 0.5 * IN

# ---------------------------------------------------------------- joinery
RABBET_D = 0.25 * IN        # case bottom in the ends and the back; drawer ends in the sides
DADO_D = 0.25 * IN          # partition in the case bottom
PLAY = 1.6                  # 1/16 in total play on housed panels (drawer bottoms)
TONGUE_T = 0.25 * IN        # front frames: tongue-and-groove bit set
TONGUE_L = 0.375 * IN
PANEL_T = T12                # 1/2 panel (ply or MDF, measures 12 mm): back flush with the frame, face inset FACE_T - PANEL_T
STILE_W = 1.5 * IN          # maple frame width on the fronts
CLEAT_H = 2.5 * IN          # rear top cleat on the back's inner face: the top's figure-8s

# ---------------------------------------------------------------- Blum TANDEM 563H, 21 in
SLIDE_LEN = 21 * IN
RUNNER_LEN = 547.0          # the runner body is longer than the nominal box: 471 for the 18 in class (drawer bench);
                            # 547 assumes the same 14 mm for the 21 in class, VERIFY on the 563H5330B sheet
UM_WIDTH_LOSS = 42.0        # inside drawer width = opening - 42
UM_BOTTOM_CLEAR = 14.0      # opening bottom to drawer side bottom edge
UM_TOP_CLEAR = 7.0          # drawer side top edge to opening top (Blum 2022/2025: opening - 21)
UM_RECESS = 13.0            # drawer side bottom edge to underside of the bottom
UM_FRONT_GAP = 1.5          # box front behind the fronts' back faces
UM_MIN_DEPTH = 557.0        # inside depth from the fronts' back faces to the back's inner face, frameless side
UM_BRACKET_MIN, UM_BRACKET_MAX = 6.0, 48.0   # runner rear end to the back's inner face, rear-bracket side
UM_SCREW_Y = (7.0, 34.0)    # runner front screw holes behind the runner front, into the post's inner face
RUNNER_SETBACK = T12 + FACE_T - 11.5 + FRONT_SETBACK   # runner front behind the post face (Blum inset rule plus the setback)
UM_HOOK_NOTCH_W, UM_HOOK_NOTCH_H = 35.0, 13.0   # from the side's inner face; flush with the bottom
UM_HOOK_BORE = (6.0, 10.0, 7.0, 24.0)   # dia, depth, from side inner face, above side bottom

# ---------------------------------------------------------------- figure-8 fasteners (cleat only)
FIG8_DIA = 0.625 * IN
FIG8_DEPTH = 0.125 * IN
FIG8_OFFSET = 0.25 * IN     # center this far in from the inner face (opens through it)

# ---------------------------------------------------------------- derived layout
TOP_X0 = SIDE_AIR                         # the top: 64 in between 1 in of air at each wall
TOP_X1 = ALCOVE_W - SIDE_AIR
TOP_W = TOP_X1 - TOP_X0
TOP_Y0 = WALL_GAP
TOP_Y1 = ALCOVE_D - TOP_SETBACK           # 25 in from the back wall
TOP_D = TOP_Y1 - TOP_Y0
TOP_Z0 = SEAT_Z - TS
X0 = TOP_X0 + OVERHANG                    # post outer faces
X1 = TOP_X1 - OVERHANG
XC = (X0 + X1) / 2
POST_IN_L = X0 + POST                     # posts' inner faces: the drawer openings' outer sides
POST_IN_R = X1 - POST
YB0 = TOP_Y0                              # rear posts' rear faces, flush with the top's back edge
YF1 = TOP_Y1 - OVERHANG                   # front posts' faces
YF0 = YF1 - POST
FACE_Y1 = YF1 - FRONT_SETBACK             # the fronts' faces
FACE_Y0 = FACE_Y1 - FACE_T                # the fronts' back faces: the case front line
CASE_D = FACE_Y0
END_X0 = X0 + SETBACK                     # end panels: outer face
END_IN_L = END_X0 + T18                   # inner faces
END_IN_R = X1 - SETBACK - T18
END_Y0 = YB0 + POST - GROOVE_D            # housed in the rear post ...
END_Y1 = YF0 + GROOVE_D                   # ... and the front post
BACK_Y0 = YB0 + SETBACK                   # the 1/2 back: outer face
BACK_Y1 = BACK_Y0 + T12
BACK_X0 = POST_IN_L - GROOVE_D            # housed in the rear posts
BACK_X1 = POST_IN_R + GROOVE_D
BOT_Z0 = CLEAR                            # case bottom's underside: the clear floor
BOT_Z1 = BOT_Z0 + T18
OPEN_H = TOP_Z0 - BOT_Z1
PANEL_Z0 = CLEAR                          # ends and back: bottom edge
TONGUE_Z0 = PANEL_Z0 + NOTCH_H            # the housed tongue starts here
GROOVE_STOP = TONGUE_Z0 - GROOVE_CLR      # the post grooves stop here, open at the top
PART_X0 = XC - T18 / 2
OPEN_W = PART_X0 - POST_IN_L              # one bay: post inner face to the partition
FRONT_W = (POST_IN_R - POST_IN_L - 3 * GAP) / 2
FRONT_Z0 = CLEAR                          # fronts flush with the case underside
FRONT_H = TOP_Z0 - GAP - FRONT_Z0
FRONT_X0 = [POST_IN_L + GAP, POST_IN_L + 2 * GAP + FRONT_W]
CLEAT_Y0 = BACK_Y1
CLEAT_Y1 = CLEAT_Y0 + TS
CLEAT_Z0 = TOP_Z0 - CLEAT_H

PARTS = []
INST = []
HW = []


def _box(x, y, z, dx, dy, dz):
    return Pos(x, y, z) * Box(dx, dy, dz, align=(Align.MIN, Align.MIN, Align.MIN))


def vol(s):
    try:
        return s.volume
    except Exception:
        return 0.0


def part(name):
    return next(p["solid"] for p in PARTS if p["name"] == name)


def add(name, solid, qty, material, notes="", inst=None):
    assert len(solid.solids()) == 1, name
    PARTS.append({"name": name, "solid": solid, "qty": qty, "material": material, "notes": notes})
    for n, s in (inst or [(name, solid)]):
        INST.append((n, s))


MAPLE = "hard maple"
SOFT_MAPLE = "soft maple"
PLY18 = "3/4 maple ply"
PLY12 = "1/2 maple ply"
PAINT_PANEL = "1/2 paint-grade panel"   # MDF or paint-grade ply, painted white with the frames (Brian 2026-10-24)
BB12 = "1/2 Baltic birch"

# ================================================================ posts
# Chamfer the four vertical edges first, then cut the grooves, so the groove walls are clean. The end-panel groove is
# on the face toward the other post of the same end, SETBACK in from the outer face; the rear posts also take the
# back's groove on their inner face, SETBACK in from the rear face. Grooves stop at GROOVE_STOP and run out the top.
def make_post(x, y, front):
    """the low-X post; outer face at min X; front posts have their outer face at max Y, rear posts at min Y"""
    p = _box(x, y, 0, POST, POST, TOP_Z0)
    p = chamfer(p.edges().filter_by(Axis.Z), CHAMFER)
    gh = TOP_Z0 - GROOVE_STOP + 1
    gy = y - 1 if front else y + POST - GROOVE_D
    p -= _box(x + SETBACK, gy, GROOVE_STOP, T18, GROOVE_D + 1, gh)
    if not front:
        p -= _box(x + POST - GROOVE_D, y + SETBACK, GROOVE_STOP, GROOVE_D + 1, T12, gh)
        if BASEBOARD_NOTCH:
            p -= _box(x - 1, y - 1, -1, POST + 2, BB_NOTCH_D + 1, BB_NOTCH_H + 1)
    return p


post_fl = make_post(X0, YF0, True)
post_rl = make_post(X0, YB0, False)
post_fr = mirror(post_fl, Plane.YZ.offset(XC))
post_rr = mirror(post_rl, Plane.YZ.offset(XC))
_POST_NOTE = (f"{inch(POST)} square x {inch(TOP_Z0)} (12/4 stock or an 8/4 plus 4/4 glue-up); {inch(CHAMFER)} chamfer on all "
              f"four vertical edges, full length, cut before the grooves; end-panel groove {inch(T18)} wide (measure) x "
              f"{inch(GROOVE_D)} deep on the face toward the other post of that end, {inch(SETBACK)} in from the outer face, "
              f"from {inch(GROOVE_STOP)} up out the top (the end stays as the bit leaves it, the panel's notched bottom "
              "covers it); bare under Osmo; left/right mirrored")
add("post_front", post_fl, 2, SOFT_MAPLE,
    _POST_NOTE + f"; the Blum runner front screws into the inner face, holes {inch(UM_SCREW_Y[0] + RUNNER_SETBACK)} and "
    f"{inch(UM_SCREW_Y[1] + RUNNER_SETBACK)} behind the front face, #6 x 5/8",
    inst=[("post_fl", post_fl), ("post_fr", post_fr)])
add("post_rear", post_rl, 2, SOFT_MAPLE,
    _POST_NOTE + f"; plus the back's groove {inch(T12)} wide (measure) x {inch(GROOVE_D)} deep on the inner face, "
    f"{inch(SETBACK)} in from the rear face, same stop"
    + (f"; notch {inch(BB_NOTCH_D)} deep x {inch(BB_NOTCH_H)} tall across the rear face at the floor for the baseboard "
       "and shoe (skip it if the baseboard comes out)" if BASEBOARD_NOTCH else ""),
    inst=[("post_rl", post_rl), ("post_rr", post_rr)])

# the post is the box minus four chamfer prisms minus its grooves (and the notch): the chamfers never reach a groove
_post_box = POST ** 2 * TOP_Z0 - 4 * 0.5 * CHAMFER ** 2 * TOP_Z0
_gh = TOP_Z0 - GROOVE_STOP
assert abs(post_fl.volume - (_post_box - T18 * GROOVE_D * _gh)) < 1e-2, post_fl.volume
_notch = POST * BB_NOTCH_D * BB_NOTCH_H - 2 * 0.5 * CHAMFER ** 2 * BB_NOTCH_H if BASEBOARD_NOTCH else 0.0
assert abs(post_rl.volume - (_post_box - T18 * GROOVE_D * _gh - T12 * GROOVE_D * _gh - _notch)) < 1e-2, post_rl.volume
assert CHAMFER < SETBACK, "the chamfer would break into a groove"
assert BB_NOTCH_D >= BASEBOARD_T + 0.25 * IN - WALL_GAP and BB_NOTCH_H >= BASEBOARD_H + 0.25 * IN

# ================================================================ panels: ends (3/4) and back (1/2), housed in the posts
# Bottom corners notched GROOVE_D x NOTCH_H so the housed tongue starts NOTCH_H up and the un-housed bottom butts the
# post faces over the groove ends; a rabbet along the bottom inside edge takes the case bottom.
end_l = _box(END_X0, END_Y0, PANEL_Z0, T18, END_Y1 - END_Y0, TOP_Z0 - PANEL_Z0)
for _y in (END_Y0 - 1, END_Y1 - GROOVE_D):
    end_l -= _box(END_X0 - 1, _y, PANEL_Z0 - 1, T18 + 2, GROOVE_D + 1, NOTCH_H + 1)
end_l -= _box(END_IN_L - RABBET_D, -1, PANEL_Z0 - 1, RABBET_D + 1, ALCOVE_D + 2, T18 + 1)
end_r = mirror(end_l, Plane.YZ.offset(XC))
_NOTCH_NOTE = (f"both bottom corners notched {inch(GROOVE_D)} (from each end) x {inch(NOTCH_H)} tall: the housed tongue "
               f"starts {inch(GROOVE_CLR)} above the post groove's end and the panel's bottom {inch(NOTCH_H)} butts the post faces")
add("end", end_l, 2, PLY18,
    f"show face out, face grain vertical, painted white (bottom edge banded); housed {inch(GROOVE_D)} in each post, "
    f"outer face {inch(SETBACK)} behind the post faces, top edge flush with the post tops; " + _NOTCH_NOTE +
    f"; {inch(RABBET_D)} x {inch(T18)} (measure) rabbet along the bottom inside edge for the case bottom, through; "
    "mirror pair", inst=[("end_l", end_l), ("end_r", end_r)])

back = _box(BACK_X0, BACK_Y0, PANEL_Z0, BACK_X1 - BACK_X0, T12, TOP_Z0 - PANEL_Z0)
for _x in (BACK_X0 - 1, BACK_X1 - GROOVE_D):
    back -= _box(_x, BACK_Y0 - 1, PANEL_Z0 - 1, GROOVE_D + 1, T12 + 2, NOTCH_H + 1)
back -= _box(-1, BACK_Y1 - RABBET_D, PANEL_Z0 - 1, ALCOVE_W + 2, RABBET_D + 1, T18 + 1)
add("back", back, 1, PLY12,
    f"housed {inch(GROOVE_D)} in each rear post, outer face {inch(SETBACK)} behind their rear faces, top edge flush with "
    "the post tops; " + _NOTCH_NOTE + f"; {inch(RABBET_D)} x {inch(T18)} (measure) rabbet along the bottom inside edge "
    "for the case bottom, through; glued in (with no wall screws it is what keeps the case square); the Blum rear "
    "brackets screw to its inside face with #6 x 1/2")

# ================================================================ case bottom, partition, cleat
BOT_X0 = END_IN_L - RABBET_D
BOT_X1 = END_IN_R + RABBET_D
BOT_Y0 = BACK_Y1 - RABBET_D
bottom = _box(BOT_X0, BOT_Y0, BOT_Z0, BOT_X1 - BOT_X0, CASE_D - BOT_Y0, T18)
for _x0, _x1 in ((BOT_X0 - 1, POST_IN_L), (POST_IN_R, BOT_X1 + 1)):       # notched around the four posts
    bottom -= _box(_x0, YF0, BOT_Z0 - 1, _x1 - _x0, ALCOVE_D, T18 + 2)
    bottom -= _box(_x0, -1, BOT_Z0 - 1, _x1 - _x0, YB0 + POST + 1, T18 + 2)
bottom -= _box(PART_X0, BACK_Y1, BOT_Z1 - DADO_D, T18, CASE_D - BACK_Y1 + 1, DADO_D + 1)
add("bottom", bottom, 1, PLY18,
    f"face grain across the {inch(BOT_X1 - BOT_X0)}; sits {inch(RABBET_D)} into the rabbets of both ends and the back; "
    f"all four corners notched {inch(POST_IN_L - BOT_X0)} across x {inch(CASE_D - YF0)} (front) and "
    f"{inch(YB0 + POST - BOT_Y0)} (rear) around the posts; {inch(DADO_D)} deep x 3/4 ply (measure) dado for the "
    "partition, centered, from the back to the front edge; front edge covered by the drawer fronts")

PART_Z0 = BOT_Z1 - DADO_D
partition = _box(PART_X0, BACK_Y1, PART_Z0, T18, CASE_D - BACK_Y1, TOP_Z0 - PART_Z0)
partition -= _box(PART_X0 - 1, CLEAT_Y0 - 1, CLEAT_Z0, T18 + 2, TS + 1, CLEAT_H + 1)
add("partition", partition, 1, PLY18,
    f"face grain vertical; sits in the bottom dado and against the back; front edge on the fronts' back faces (the "
    f"partition-side runners mount to it the frameless way); notch the top rear corner {inch(TS)} deep x {inch(CLEAT_H)} "
    "tall for the cleat")

cleat = _box(POST_IN_L, CLEAT_Y0, CLEAT_Z0, POST_IN_R - POST_IN_L, TS, CLEAT_H)
FIG8_XS = [POST_IN_L + (POST_IN_R - POST_IN_L) * f for f in (0.15, 0.37, 0.63, 0.85)]
FIG8_Y = CLEAT_Y1 - FIG8_OFFSET
for xc in FIG8_XS:
    cleat -= Pos(xc, FIG8_Y, TOP_Z0 - FIG8_DEPTH) * Cylinder(FIG8_DIA / 2, FIG8_DEPTH + 1,
                                                             align=(Align.CENTER, Align.CENTER, Align.MIN))
add("cleat", cleat, 1, SOFT_MAPLE,
    f"on edge against the back's inside face at the top, between the rear posts, through the partition notch; four "
    f"{inch(FIG8_DIA)} figure-8 recesses {inch(FIG8_DEPTH)} deep on the top edge, centered {inch(FIG8_OFFSET)} in from the "
    "front face; glued and screwed to the back from inside (#8 x 1 countersunk, nothing through the back)")

# ================================================================ top: solid maple, pocket screws at the front, figure-8s at the back
top = _box(TOP_X0, TOP_Y0, TOP_Z0, TOP_W, TOP_D, TS)
_front = top.edges().filter_by(Axis.X).group_by(Axis.Y)[-1]
_ends = top.edges().filter_by(Axis.Y)
top = fillet(_front + _ends, ROUND)
add("top", top, 1, MAPLE,
    f"glue up from 4 or 5 boards, grain along the {inch(TOP_W)}; {inch(ROUND)} roundover on the front and both end "
    f"arrises, top and bottom (the back edge stays square against the wall); overhangs the posts {inch(OVERHANG)} at "
    "each end and the front, flush with their rear faces; pocket screws up through the ends and partition near the "
    "front, figure-8s on the cleat at the back")

# ================================================================ drawer fronts: maple frame, inset panel, T&G, all painted white
RL = FRONT_W - 2 * STILE_W + 2 * TONGUE_L     # rail length with stub tenons
PW, PH = RL, FRONT_H - 2 * STILE_W + 2 * TONGUE_L
GY0 = FACE_Y0 + PANEL_T - TONGUE_T            # groove / tongue plane: the groove front wall lands on the panel face


def front_parts(x0):
    z0 = FRONT_Z0
    stile = _box(x0, FACE_Y0, z0, STILE_W, FACE_T, FRONT_H)
    stile -= _box(x0 + STILE_W - TONGUE_L, GY0, z0 - 1, TONGUE_L + 1, TONGUE_T, FRONT_H + 2)
    stile_r = mirror(stile, Plane.YZ.offset(x0 + FRONT_W / 2))
    rail = _box(x0 + STILE_W - TONGUE_L, FACE_Y0, z0, RL, FACE_T, STILE_W)
    rail -= _box(x0 + STILE_W - TONGUE_L - 1, GY0, z0 + STILE_W - TONGUE_L, RL + 2, TONGUE_T, TONGUE_L + 1)
    for xe in (x0 + STILE_W - TONGUE_L, x0 + FRONT_W - STILE_W):
        rail -= _box(xe, FACE_Y0 - 1, z0 - 1, TONGUE_L, GY0 - FACE_Y0 + 1, STILE_W + 2)
        rail -= _box(xe, GY0 + TONGUE_T, z0 - 1, TONGUE_L, FACE_Y1 - GY0 - TONGUE_T + 1, STILE_W + 2)
    rail_top = mirror(rail, Plane.XY.offset(z0 + FRONT_H / 2))
    panel = _box(x0 + STILE_W - TONGUE_L, GY0, z0 + STILE_W - TONGUE_L, PW, TONGUE_T, PH)
    panel += _box(x0 + STILE_W, FACE_Y0, z0 + STILE_W, PW - 2 * TONGUE_L, PANEL_T, PH - 2 * TONGUE_L)
    return stile, stile_r, rail, rail_top, panel


_fl = front_parts(FRONT_X0[0])
_fr = front_parts(FRONT_X0[1])
add("front_stile", _fl[0], 4, MAPLE,
    f"{inch(TONGUE_T)} x {inch(TONGUE_L)} groove on the inner edge, through, front wall {inch(FACE_T - PANEL_T)} thick (set the fence from the panel ply); the rail tenons show on both ends (the top one is the visible one); painted white",
    inst=[("stile_ll", _fl[0]), ("stile_lr", _fl[1]), ("stile_rl", _fr[0]), ("stile_rr", _fr[1])])
add("front_rail", _fl[2], 4, MAPLE,
    f"{inch(TONGUE_T)} x {inch(TONGUE_L)} groove on the inner edge, through; {inch(TONGUE_T)} x {inch(TONGUE_L)} "
    f"stub tenon on both ends (same bit); length includes both tenons; painted white",
    inst=[("rail_lb", _fl[2]), ("rail_lt", _fl[3]), ("rail_rb", _fr[2]), ("rail_rt", _fr[3])])
add("front_panel", _fl[4], 2, PAINT_PANEL,
    f"{inch(TONGUE_T)} x {inch(TONGUE_L)} tongue on all four edges, flush with the show face (rabbet the BACK edges "
    f"{inch(PANEL_T - TONGUE_T)} deep); grain horizontal; size includes the tongues; back flush with the frame back, "
    f"face {inch(FACE_T - PANEL_T)} below the maple; glue in (plywood, no movement)",
    inst=[("panel_l", _fl[4]), ("panel_r", _fr[4])])

front_l = _fl[0] + _fl[1] + _fl[2] + _fl[3] + _fl[4]
assert len(front_l.solids()) == 1, "front frame and panel do not close up"
_bb = front_l.bounding_box()
assert abs(_bb.size.X - FRONT_W) < 1e-6 and abs(_bb.size.Z - FRONT_H) < 1e-6 and abs(_bb.size.Y - FACE_T) < 1e-6
_pb = _fl[4].bounding_box()
assert abs(_pb.min.Y - FACE_Y0) < 1e-6 and abs((FACE_Y1 - _pb.max.Y) - (FACE_T - PANEL_T)) < 1e-6, "panel is not inset"
assert abs(_pb.max.Y - (GY0 + TONGUE_T)) < 1e-6, "tongue is not flush with the panel face"

# ================================================================ drawer boxes: Blum 563H
BOX_W = OPEN_W - UM_WIDTH_LOSS + 2 * T12
BOX_IN_W = OPEN_W - UM_WIDTH_LOSS
BOX_H = 6.5 * IN            # the opening is 7-17/32; Blum allows opening minus 21 mm
BOX_D = SLIDE_LEN
BOX_Z0 = BOT_Z1 + UM_BOTTOM_CLEAR
BOX_Y1 = CASE_D - UM_FRONT_GAP
BOX_Y0 = BOX_Y1 - BOX_D
END_LEN = BOX_W - 2 * (T12 - RABBET_D)      # drawer front and back length (1/2 Baltic birch, in the side rabbets)
BOTTOM_D = BOX_D - 2 * T12 + RABBET_D        # bottom: 1/4 into the front groove, butted to the back (no back groove)
BITE_TOP = (BOX_Z0 + BOX_H) - (FRONT_Z0 + FRONT_H - STILE_W)   # box front overlap on the top rail
BITE_BOT = (FRONT_Z0 + STILE_W) - BOX_Z0                       # and on the bottom rail


def make_drawer(bay_x0, sfx):
    xc = bay_x0 + OPEN_W / 2
    x0 = xc - BOX_W / 2
    z0, y0, y1 = BOX_Z0, BOX_Y0, BOX_Y1
    gz = z0 + UM_RECESS                      # underside of the bottom
    side = _box(x0, y0, z0, T12, BOX_D, BOX_H)
    side -= _box(x0 + T12 - RABBET_D, y1 - T12, z0 - 1, RABBET_D + 1, T12 + 1, BOX_H + 2)
    side -= _box(x0 + T12 - RABBET_D, y0 - 1, z0 - 1, RABBET_D + 1, T12 + 1, BOX_H + 2)
    side -= _box(x0 + T12 - RABBET_D, y0 - 1, gz, RABBET_D + 1, BOX_D + 2, T12)
    side_r = mirror(side, Plane.YZ.offset(xc))
    ex0 = x0 + T12 - RABBET_D
    front = _box(ex0, y1 - T12, z0, END_LEN, T12, BOX_H)
    front -= _box(ex0 - 1, y1 - T12 - 1, gz, END_LEN + 2, RABBET_D + 1, T12)
    backp = _box(ex0, y0, z0, END_LEN, T12, BOX_H)
    nw = UM_HOOK_NOTCH_W + RABBET_D
    for xe in (ex0, ex0 + END_LEN - nw):
        backp -= _box(xe, y0 - 1, z0 - 1, nw, T12 + 2, UM_HOOK_NOTCH_H + 1)
    dia, depth, off, up = UM_HOOK_BORE
    for xin in (x0 + T12, x0 + BOX_W - T12):
        bx = xin + off if xin < xc else xin - off
        backp -= Pos(bx, y0 - 1, z0 + up) * Rot(-90, 0, 0) * Cylinder(dia / 2, depth + 1,
                                                                        align=(Align.CENTER, Align.CENTER, Align.MIN))
    bx0 = x0 + T12 - RABBET_D + PLAY / 2
    by0 = y0 + T12
    bot = _box(bx0, by0, gz, BOX_W - 2 * (T12 - RABBET_D) - PLAY, BOTTOM_D - PLAY / 2, T12)
    return side, side_r, front, backp, bot


_dl = make_drawer(POST_IN_L, "l")
_dr = make_drawer(PART_X0 + T18, "r")
add("drawer_side", _dl[0], 4, BB12,
    f"{inch(RABBET_D)} deep x 1/2 BB (measure) rabbet across both ends on the inside face; "
    f"{inch(RABBET_D)} deep x 1/2 BB (measure) bottom groove, underside {inch(UM_RECESS)} up from the bottom edge, through",
    inst=[("dside_ll", _dl[0]), ("dside_lr", _dl[1]), ("dside_rl", _dr[0]), ("dside_rr", _dr[1])])
add("drawer_front", _dl[2], 2, BB12,
    f"box front, sits in the side rabbets; {inch(RABBET_D)} deep bottom groove to match the sides; "
    "the front screws to it from inside through 4 oversize holes: #8 x 7/8 in, pre-drilled, so the bite stays short of the "
    f"face; the box front overlaps the top rail by {inch(BITE_TOP)} (best bite) and the panel field, but the bottom rail by only {inch(BITE_BOT)}",
    inst=[("dfront_l", _dl[2]), ("dfront_r", _dr[2])])
add("drawer_back", _dl[3], 2, BB12,
    f"box back, sits in the side rabbets; no bottom groove (a groove would break into the hook bores), the bottom butts "
    f"its front face; Blum notch {inch(UM_HOOK_NOTCH_W)} in from each side's inner face x {inch(UM_HOOK_NOTCH_H)} tall at both bottom corners; hook bores "
    f"{inch(UM_HOOK_BORE[0])} dia x {inch(UM_HOOK_BORE[1])} deep into the rear face, centered "
    f"{inch(UM_HOOK_BORE[2])} in from each side's inner face and {inch(UM_HOOK_BORE[3])} above the bottom edge (Blum 563H sheet)",
    inst=[("dback_l", _dl[3]), ("dback_r", _dr[3])])
add("drawer_bottom", _dl[4], 2, BB12,
    f"plain rectangle: {inch(RABBET_D)} into the side and front grooves, butted to the back and glued to it; the Blum locking devices sit flush under it at the front corners (their screws go into the box front)",
    inst=[("dbot_l", _dl[4]), ("dbot_r", _dr[4])])

# ================================================================ hardware and soft goods (viewer only)
for i, bay_x0 in enumerate((POST_IN_L, PART_X0 + T18)):
    for side_x in (bay_x0, bay_x0 + OPEN_W - 37.0):
        HW.append((f"slide_{i}_{'l' if side_x == bay_x0 else 'r'}",
                   _box(side_x, BOX_Y0, BOT_Z1, 37.0, BOX_D, UM_BOTTOM_CLEAR - 1.0)))
PULL_L, PULL_SQ, PULL_STAND = 8 * IN, 0.5 * IN, 1.0 * IN
for fx in FRONT_X0:
    cx, cz = fx + FRONT_W / 2, FRONT_Z0 + FRONT_H / 2
    bar = _box(cx - PULL_L / 2, FACE_Y1 + PULL_STAND, cz - PULL_SQ / 2, PULL_L, PULL_SQ, PULL_SQ)
    for px in (cx - 80, cx + 80):
        bar += Pos(px, FACE_Y1, cz) * Rot(-90, 0, 0) * Cylinder(4, PULL_STAND + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    HW.append((f"pull_{'l' if fx == FRONT_X0[0] else 'r'}", bar))
cushion = _box(TOP_X0 + 0.25 * IN, TOP_Y0, SEAT_Z, TOP_W - 0.5 * IN, TOP_D, CUSHION_H)
cushion = fillet(cushion.edges(), 0.75 * IN)
HW.append(("cushion", cushion))

# ================================================================ checks
for p in PARTS:
    assert len(p["solid"].solids()) == 1, p["name"]
for i, (na, a) in enumerate(INST):
    for nb, b in INST[i + 1:]:
        assert vol(a & b) < 1e-3, f"overlap {na} x {nb}"
for nh, h in HW:
    for na, a in INST:
        assert vol(h & a) < 1e-3, f"hardware overlap {nh} x {na}"

# layout
assert abs(TOP_Y1 - (ALCOVE_D - 3 * IN)) < 1e-9
assert abs(FRONT_X0[0] - POST_IN_L - GAP) < 1e-9 and abs(POST_IN_R - (FRONT_X0[1] + FRONT_W) - GAP) < 1e-9
assert abs(FRONT_X0[1] - (FRONT_X0[0] + FRONT_W) - GAP) < 1e-9
assert abs(TOP_Z0 - (FRONT_Z0 + FRONT_H) - GAP) < 1e-9 and abs(FRONT_Z0 - BOT_Z0) < 1e-9
assert abs(FACE_Y1 - (YF1 - FRONT_SETBACK)) < 1e-9
_all = Compound(children=[s for _, s in INST])
_bbw = _all.bounding_box()
assert abs(_bbw.min.X - TOP_X0) < 1e-6 and abs(_bbw.max.X - TOP_X1) < 1e-6, "the top is the widest part"
assert _bbw.min.X >= SIDE_AIR - 1e-6 and _bbw.max.X <= ALCOVE_W - SIDE_AIR + 1e-6, "air to the walls"
assert abs(_bbw.min.Y - WALL_GAP) < 1e-6 and abs(_bbw.max.Y - TOP_Y1) < 1e-6
assert abs(_bbw.min.Z) < 1e-6 and abs(_bbw.max.Z - SEAT_Z) < 1e-6

# the clear floor: everything but the posts starts at CLEAR; the posts stand on the floor and reach the top
POSTS = {"post_fl", "post_fr", "post_rl", "post_rr"}
for n, s in INST:
    bb = s.bounding_box()
    if n in POSTS:
        assert abs(bb.min.Z) < 1e-6 and abs(bb.max.Z - TOP_Z0) < 1e-6, n
    else:
        assert bb.min.Z >= CLEAR - 1e-6, f"{n} hangs below the clear floor"
assert X0 >= BASEBOARD_T + 0.25 * IN, "the end posts stand on the side walls' baseboards"
if BASEBOARD_NOTCH:   # the baseboard's envelope fits in the rear posts' notches
    _bb_air = _box(X0 - 1, -1, 0.5, POST + 2, WALL_GAP + BASEBOARD_T - 0.5, BASEBOARD_H - 1)
    assert vol(_bb_air & post_rl) < 1e-3, "baseboard notch too small"
# the housed tongues: inside the panel, in a relieved post, and the un-housed bottoms on the post faces
def housed(guest, host, probe):
    assert vol(probe & guest) > probe.volume * 0.999, "probe not inside guest"
    assert vol(probe & host) < 1e-6, "host not relieved for the guest"


housed(part("end"), part("post_front"), _box(END_X0 + 0.3, END_Y1 - GROOVE_D + 0.3, (TONGUE_Z0 + TOP_Z0) / 2, T18 - 0.6, GROOVE_D - 0.6, 10))
housed(part("end"), part("post_rear"), _box(END_X0 + 0.3, END_Y0 + 0.3, (TONGUE_Z0 + TOP_Z0) / 2, T18 - 0.6, GROOVE_D - 0.6, 10))
housed(part("back"), part("post_rear"), _box(BACK_X0 + 0.3, BACK_Y0 + 0.3, (TONGUE_Z0 + TOP_Z0) / 2, GROOVE_D - 0.6, T12 - 0.6, 10))
_butt = (end_l & _box(END_X0 - 1, -1, PANEL_Z0, T18 + 2, ALCOVE_D, NOTCH_H)).bounding_box()
assert abs(_butt.min.Y - (YB0 + POST)) < 1e-6 and abs(_butt.max.Y - YF0) < 1e-6, "end's bottom not on the post faces"
_butt = (back & _box(-1, BACK_Y0 - 1, PANEL_Z0, ALCOVE_W + 2, T12 + 2, NOTCH_H)).bounding_box()
assert abs(_butt.min.X - POST_IN_L) < 1e-6 and abs(_butt.max.X - POST_IN_R) < 1e-6, "back's bottom not on the post faces"
assert PANEL_Z0 <= GROOVE_STOP < TONGUE_Z0 and GROOVE_CLR >= T18 / 2 + 0.25 * IN
# the post groove ends below the tongue and above the panel bottom: wood below GROOVE_STOP, air above
_grv_air = _box(END_X0 + 0.3, END_Y1 - GROOVE_D + 0.3, GROOVE_STOP + 0.5, T18 - 0.6, GROOVE_D - 0.6, 2)
assert vol(_grv_air & post_fl) < 1e-6, "front post groove does not reach GROOVE_STOP"
_grv_wood = _box(END_X0 + 0.3, END_Y1 - GROOVE_D + 0.3, GROOVE_STOP - 2.5, T18 - 0.6, GROOVE_D - 0.6, 2)
assert abs(vol(_grv_wood & post_fl) - _grv_wood.volume) < 1e-3, "front post groove runs below GROOVE_STOP"
housed(part("bottom"), part("end"), _box(BOT_X0 + 0.5, (YB0 + POST + CASE_D) / 2, BOT_Z0 + 0.5, RABBET_D - 1, 10, T18 - 1))
housed(part("bottom"), part("back"), _box(XC - 5, BOT_Y0 + 0.5, BOT_Z0 + 0.5, 10, RABBET_D - 1, T18 - 1))
housed(part("partition"), part("bottom"), _box(PART_X0 + 0.5, CASE_D / 2, PART_Z0 + 0.5, T18 - 1, 10, DADO_D - 1))
housed(part("cleat"), part("partition"), _box(PART_X0 + 0.5, CLEAT_Y0 + 0.5, CLEAT_Z0 + 0.5, T18 - 1, TS - 1, 10))
# the bottom's notches clear the posts and the bottom reaches the posts' inner faces
for pn in ("post_fl", "post_rl"):
    assert vol(dict(INST)[pn] & bottom) < 1e-6
assert abs((bottom & _box(POST_IN_L - 1, YF0 + 1, BOT_Z0, 2, 5, T18)).volume - 1 * 5 * T18) < 1e-3, "bottom short of the post's inner face"

# Blum
assert abs(BOX_IN_W - (OPEN_W - UM_WIDTH_LOSS)) < 1e-6
assert abs(BOX_Z0 - BOT_Z1 - UM_BOTTOM_CLEAR) < 1e-6
assert TOP_Z0 - (BOX_Z0 + BOX_H) >= UM_TOP_CLEAR, "box too tall for the opening"
assert abs(BOX_D - SLIDE_LEN) < 1e-6
assert CASE_D - BACK_Y1 >= UM_MIN_DEPTH, f"case too shallow for the 21 in runner on the partition side: {CASE_D - BACK_Y1:.1f} < {UM_MIN_DEPTH}"
_runner_rear = YF1 - RUNNER_SETBACK - RUNNER_LEN
assert UM_BRACKET_MIN <= _runner_rear - BACK_Y1 <= UM_BRACKET_MAX, "rear bracket range on the post side"
assert UM_BRACKET_MIN <= (YF1 - RUNNER_SETBACK - SLIDE_LEN) - BACK_Y1 <= UM_BRACKET_MAX, "rear bracket range if the runner is nominal length"
assert UM_SCREW_Y[1] + RUNNER_SETBACK < POST, "runner front screws run past the post"
assert BOX_Y0 > CLEAT_Y1 and BOX_Y0 > BACK_Y1, "box hits the cleat or back"
assert T12 - UM_HOOK_BORE[1] >= 1.9, "hook bore would break through the back"   # a 2 mm skin; test-drill scrap first
_dia, _depth, _off, _up = UM_HOOK_BORE
_bx = _dl[0].bounding_box().min.X + T12 + _off
_probe_air = Pos(_bx, BOX_Y0 + 1, BOX_Z0 + _up) * Rot(-90, 0, 0) * Cylinder(_dia / 2 - 0.5, _depth - 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
assert vol(_probe_air & part("drawer_back")) < 1e-3, "hook bore not cut"
_probe_wood = _box(_bx - 1, BOX_Y0 + _depth + 0.3, BOX_Z0 + _up - 1, 2, T12 - _depth - 0.6, 2)
assert abs(vol(_probe_wood & part("drawer_back")) - _probe_wood.volume) < 1e-3, "no wood between the bore and the back's front face"
_sx = _dl[0].bounding_box().min.X + T12
_notch_air = _box(_sx + 0.5, BOX_Y0 + 0.5, BOX_Z0 + 0.5, UM_HOOK_NOTCH_W - 1, T12 - 1, UM_HOOK_NOTCH_H - 1)
assert vol(_notch_air & part("drawer_back")) < 1e-3, "rear notch not cut"
_notch_wood = _box(_sx + UM_HOOK_NOTCH_W + 0.3, BOX_Y0 + 0.5, BOX_Z0 + 0.5, 2, T12 - 1, UM_HOOK_NOTCH_H - 1)
assert abs(vol(_notch_wood & part("drawer_back")) - _notch_wood.volume) < 1e-3, "rear notch too wide"
assert abs((BOX_Z0 + UM_RECESS) - (BOX_Z0 + UM_HOOK_NOTCH_H)) < 1e-6, "notch not flush with the bottom"

housed(part("front_panel"), part("front_stile"),
       _box(FRONT_X0[0] + STILE_W - TONGUE_L + 0.3, GY0 + 0.3, FRONT_Z0 + FRONT_H / 2, TONGUE_L - 0.6, TONGUE_T - 0.6, 10))
housed(part("front_rail"), part("front_stile"),
       _box(FRONT_X0[0] + STILE_W - TONGUE_L + 0.3, GY0 + 0.3, FRONT_Z0 + 2, TONGUE_L - 0.6, TONGUE_T - 0.6, STILE_W - TONGUE_L - 4))
housed(part("front_panel"), part("front_rail"),
       _box(FRONT_X0[0] + FRONT_W / 2, GY0 + 0.3, FRONT_Z0 + STILE_W - TONGUE_L + 0.3, 10, TONGUE_T - 0.6, TONGUE_L - 0.6))
housed(part("drawer_front"), part("drawer_side"),
       _box(_dl[0].bounding_box().max.X - RABBET_D + 0.3, BOX_Y1 - T12 + 0.5, BOX_Z0 + BOX_H / 2, RABBET_D - 0.6, T12 - 1, 10))
housed(part("drawer_bottom"), part("drawer_side"),
       _box(_dl[0].bounding_box().max.X - RABBET_D + PLAY / 2 + 0.3, BOX_Y0 + BOX_D / 2, BOX_Z0 + UM_RECESS + 0.5,
            RABBET_D - PLAY / 2 - 0.6, 10, T12 - 1))
housed(part("drawer_bottom"), part("drawer_front"),
       _box(XC / 2, BOX_Y1 - T12 + 0.3, BOX_Z0 + UM_RECESS + 0.5, 10, RABBET_D - PLAY / 2 - 0.6, T12 - 1))
_bb_b, _bb_k = _dl[4].bounding_box(), _dl[3].bounding_box()
assert abs(_bb_b.min.Y - _bb_k.max.Y) < 1e-6, "bottom does not butt the back"

# volumes against analytic values
assert abs(part("front_stile").volume - (STILE_W * FACE_T * FRONT_H - TONGUE_L * TONGUE_T * FRONT_H)) < 1e-3
assert abs(part("front_panel").volume - (PW * PH * TONGUE_T + (PW - 2 * TONGUE_L) * (PH - 2 * TONGUE_L) * (PANEL_T - TONGUE_T))) < 1e-3
assert abs(part("drawer_bottom").volume - (BOX_W - 2 * (T12 - RABBET_D) - PLAY) * (BOTTOM_D - PLAY / 2) * T12) < 1e-3
_end_vol = (T18 * (END_Y1 - END_Y0) * (TOP_Z0 - PANEL_Z0) - 2 * GROOVE_D * T18 * NOTCH_H
            - RABBET_D * T18 * (END_Y1 - END_Y0 - 2 * GROOVE_D))
assert abs(part("end").volume - _end_vol) < 1e-3, part("end").volume

assembly = Compound(children=[s for _, s in INST] + [s for _, s in HW])

# ================================================================ outputs
TMP = os.environ.get("TMP_STL")
if TMP:
    SUBSETS = {   # SUBSET=case|posts|fronts|drawers|nocushion|drawer1 picks instances by name prefix for the renders
        "case": ("post_", "end_", "bottom", "partition", "cleat", "back"),
        "posts": ("post_",),
        "fronts": ("stile_", "rail_", "panel_"),
        "front1": ("stile_l", "rail_l", "panel_l"),
        "drawers": ("dside_", "dfront_", "dback_", "dbot_"),
        "drawer1": ("dside_l", "dfront_l", "dback_l", "dbot_l"),
        "nocushion": tuple(n for n, _ in INST + HW if n != "cushion"),
    }
    sel = SUBSETS.get(os.environ.get("SUBSET", ""), None)
    picked = [s for n, s in INST + HW if sel is None or n.startswith(sel)]
    export_stl(Compound(children=picked), TMP)

if os.environ.get("EXPORT"):
    HARDWARE_LINES = [
        {"part": "Blum TANDEM plus BLUMOTION 563H, 21 in (563H5330B)", "qty": 2, "unit": "pair",
         "material": "hardware", "notes": "one pair per drawer; 90 lb dynamic; runner fronts 3/32 behind the fronts' back faces"},
        {"part": "Blum rear mounting brackets 295.3750.02", "qty": 2, "unit": "ea", "material": "hardware",
         "notes": "post-side runners: the runner front screws into the post's inner face (#6 x 5/8), the rear sits on a "
                  "bracket screwed to the 1/2 back with #6 x 1/2; the partition-side runners mount to the partition as in a frameless case"},
        {"part": "Blum locking devices T51.1901 R and L", "qty": 2, "unit": "pair", "material": "hardware",
         "notes": "front corners under the drawer bottom, screwed into the 1/2 box front: use #6 x 1/2 so the points stay inside it"},
        {"part": "Brass bar pull, 8 in", "qty": 2, "unit": "ea", "material": "hardware",
         "notes": "break-away machine screws long enough for 1/2 panel + 1/2 box front"},
        {"part": "Figure-8 tabletop fasteners", "qty": 4, "unit": "ea", "material": "hardware", "notes": "cleat to top"},
        {"part": "Pocket screws #8 x 1-1/4 fine", "qty": 6, "unit": "ea", "material": "hardware",
         "notes": "ends and partition to the top, near the front"},
        {"part": "Wood screws #8 x 1", "qty": 6, "unit": "ea", "material": "hardware",
         "notes": "cleat to the back from inside, countersunk; bottom to the partition from below"},
        {"part": "Iron-on maple edge banding, 13/16", "qty": 1, "unit": "roll", "material": "hardware",
         "notes": f"the ends' bottom edges (about {inch(2 * (END_Y1 - END_Y0))} in all), painted with them"},
        {"part": "Bench cushion", "qty": 1, "unit": "ea", "material": "soft goods",
         "notes": f"about {inch(TOP_W - 0.5 * IN)} x {inch(TOP_D)} x {inch(CUSHION_H)}, boxed"},
    ]
    write_cut_list(PARTS, f"{PROJ}/cutlist.md", csv_path=f"{PROJ}/cutlist.csv",
                   title=f"Freestanding bench {inch(TOP_W)} x {inch(TOP_D)} on {inch(POST)} in posts (two drawers, {inch(CLEAR)} in clear floor)",
                   units="in", denom=32, extra_lines=HARDWARE_LINES)
    export_step(assembly, f"{PROJ}/freestanding_bench.step")
    print("exported cutlist + step")

if os.environ.get("SHOW"):
    from ocp_vscode import show, set_port, Camera
    set_port(3939)
    show(*[s for _, s in INST + HW], names=[n for n, _ in INST + HW],
         reset_camera=(Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP))

print("OK  parts:", [p["name"] for p in PARTS])
print(f"top {inch(TOP_W)} x {inch(TOP_D)} at {inch(SEAT_Z)}  posts {inch(POST)} sq x {inch(TOP_Z0)}, outer faces {inch(X1 - X0)} apart  "
      f"clear floor {inch(CLEAR)}  fronts {inch(FRONT_W)} x {inch(FRONT_H)}  opening {inch(OPEN_W)} x {inch(OPEN_H)}  "
      f"box {inch(BOX_W)} x {inch(BOX_H)} x {inch(BOX_D)} (inside height {inch(BOX_H - UM_RECESS - T12)})  "
      f"inside depth {CASE_D - BACK_Y1:.1f} mm (Blum 557)  bracket gap {YF1 - RUNNER_SETBACK - RUNNER_LEN - BACK_Y1:.1f} mm")
