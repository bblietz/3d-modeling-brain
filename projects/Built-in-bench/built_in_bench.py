#!/usr/bin/env python
"""Built-in alcove bench: 66 x 28 in former wet bar, two full-width drawers on
Blum TANDEM 563H undermounts, solid maple top with a 3 in cushion.

Picks (Brian, 2026-10-06/07): wood top at 16 in, flush base, frameless with
full-overlay fronts, flat fronts built as a maple frame around a 1/2 walnut-ply
panel (back flush with the frame, face inset 1/4 in) on a tongue-and-groove bit set, 8 in brass bar pulls, 3/4 in overhang
with an eased edge, solid glued-up maple top set 3 in back from the pilaster
faces, one full-depth cushion, 21 in slides. Finish (2026-10-09): frames, plinth and
scribe strips painted white; walnut panels, top and shelves bare.

Axes: X across the alcove, Y depth (0 at the back wall, +Y toward the room),
Z up (0 at the floor). Right-handed, so X=0 is the pilaster wall on your RIGHT
when you face the bench from the room; the _l/_r instance suffixes are model
names, not room sides (the bench is symmetric, so nothing depends on it). Units mm; inch
constants are written as n * IN. One named solid per part in PARTS; every
placed instance in INST; hardware (slides, pulls, cushion) in HW for the
viewer only.

Run:  .venv/bin/python projects/Built-in-bench/built_in_bench.py
      SHOW=reset ...   push to the OCP viewer (scripts/cad-viewer.sh)
      TMP_STL=path ... export an STL for scripts/render_stl.py
      EXPORT=1 ...     write cutlist.md/.csv and the STEP
"""
import os
import sys

from build123d import *  # noqa: F403

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
sys.path.insert(0, f"{VAULT}/scripts")
from cutlist import inch_frac, write_cut_list  # noqa: E402

IN = 25.4


def inch(mm):
    return inch_frac(mm, 32)


# ---------------------------------------------------------------- the space
ALCOVE_W = 66 * IN          # between the pilasters (X, 0 at the wall on your right from the room)
ALCOVE_D = 28 * IN          # back wall to the pilaster faces (Y)
TOP_SETBACK = 3 * IN        # top front edge back from the pilaster faces

# ---------------------------------------------------------------- picks
SEAT_Z = 16 * IN            # top face of the wood top
CUSHION_H = 3 * IN
BASE_H = 4 * IN             # flush plinth, continues the 4 in baseboard line
OVERHANG_MIN = 0.75 * IN    # F2: 3/4 in overhang (actual is derived below)
GAP = 0.125 * IN            # reveal around the fronts
WALL_GAP = 0.375 * IN       # top to back wall, absorbs the top's movement
ROUND = 0.125 * IN          # eased front arrises of the top

# ---------------------------------------------------------------- stock (actual, MEASURE)
T18 = 18.0                  # 3/4 maple ply
T12 = 12.0                  # 1/2 Baltic birch (drawer sides, bottoms)
T6 = 6.35                   # 1/4 maple ply back (nominal; the groove is cut to the measured sheet)
TS = 0.75 * IN              # solid maple: top, plinth, scribe strips, nailer
FACE_T = T18                # everything in the front plane is milled to the ply

# ---------------------------------------------------------------- joinery
RABBET_D = 0.25 * IN        # case bottom in the ends; drawer ends in the sides
DADO_D = 0.25 * IN          # partition in the case bottom
BACK_GROOVE_D = 0.25 * IN   # 1/4 back in the ends and bottom
BACK_SET = 0.25 * IN        # back panel groove this far in from the rear edge
PLAY = 1.6                  # 1/16 in total play on housed panels
TONGUE_T = 0.25 * IN        # front frames: tongue-and-groove bit set
TONGUE_L = 0.375 * IN
PANEL_T = T12                # 1/2 walnut ply (measures 12 mm): back flush with the frame, face inset FACE_T - PANEL_T
STILE_W = 1.5 * IN          # maple frame width on the fronts
NAILER_H = 2.5 * IN
STRIP_CUT = 2.0 * IN        # scribe strips ripped at 2 in, scribed to STRIP_W

# ---------------------------------------------------------------- Blum TANDEM 563H, 21 in
SLIDE_LEN = 21 * IN
UM_WIDTH_LOSS = 42.0        # inside drawer width = opening - 42
UM_BOTTOM_CLEAR = 14.0      # opening bottom to drawer side bottom edge
UM_TOP_CLEAR = 7.0          # drawer side top edge to opening top (Blum 2022/2025: opening - 21)
UM_RECESS = 13.0            # drawer side bottom edge to underside of the bottom
UM_FRONT_GAP = 1.5          # box front behind the case front edge
UM_MIN_DEPTH = 557.0        # inside case depth for the 21 in runner
UM_HOOK_NOTCH_W, UM_HOOK_NOTCH_H = 35.0, 13.0   # from the side's inner face; flush with the bottom
UM_HOOK_BORE = (6.0, 10.0, 7.0, 24.0)   # dia, depth, from side inner face, above side bottom

# ---------------------------------------------------------------- figure-8 fasteners (nailer only)
FIG8_DIA = 0.625 * IN
FIG8_DEPTH = 0.125 * IN
FIG8_OFFSET = 0.25 * IN     # center this far in from the inner face (opens through it)

# ---------------------------------------------------------------- derived layout
X0 = 1.0 * IN               # first end panel outer face (1 in scribe space)
X1 = ALCOVE_W - X0          # other end panel outer face
CASE_W = X1 - X0            # 64 in
CASE_D = 23.5 * IN          # back wall to the case front edge
FACE_Y0 = CASE_D            # fronts, strips and plinth sit on the case front
FACE_Y1 = FACE_Y0 + FACE_T
TOP_Y1 = ALCOVE_D - TOP_SETBACK          # 25 in from the back wall
TOP_Y0 = WALL_GAP
OVERHANG = TOP_Y1 - FACE_Y1
TOP_Z0 = SEAT_Z - TS
BOT_Z0 = BASE_H
BOT_Z1 = BOT_Z0 + T18
OPEN_H = TOP_Z0 - BOT_Z1
XC = (X0 + X1) / 2                        # partition center
PART_X0 = XC - T18 / 2
END_IN_L = X0 + T18                       # end inner face at low X
END_IN_R = X1 - T18                       # end inner face at high X
OPEN_W = PART_X0 - END_IN_L               # one bay
STRIP_W = END_IN_L                        # covers the end's front edge, flush inside
FRONT_W = (END_IN_R - END_IN_L - 3 * GAP) / 2
FRONT_H = TOP_Z0 - GAP - BASE_H
FRONT_Z0 = BASE_H
PLINTH_H = BASE_H - GAP
BACK_Y0 = BACK_SET
BACK_Y1 = BACK_SET + T6
NAILER_Y0 = BACK_Y1
NAILER_Y1 = NAILER_Y0 + TS
NAILER_Z0 = TOP_Z0 - NAILER_H

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
PLY18 = "3/4 maple ply"
PLYBASE = "3/4 ply (any, hidden)"
PLY6 = "1/4 maple ply"
WALNUT = "1/2 walnut ply"
BB12 = "1/2 Baltic birch"

# ================================================================ base frame (ladder, 3/4 ply)
base_end = _box(X0, 0, 0, T18, CASE_D, BASE_H)
add("base_end_rail", base_end, 2, PLYBASE,
    "ladder base, 4 in tall; the end panels stand on these",
    inst=[("base_end_l", base_end), ("base_end_r", Pos(CASE_W - T18, 0, 0) * base_end)])
base_long = _box(END_IN_L, 0, 0, END_IN_R - END_IN_L, T18, BASE_H)
add("base_long_rail", base_long, 2, PLYBASE,
    "front and back rails between the end rails; pocket screws or glue and screws",
    inst=[("base_back", base_long), ("base_front", Pos(0, CASE_D - T18, 0) * base_long)])
base_mid = _box(PART_X0, T18, 0, T18, CASE_D - 2 * T18, BASE_H)
add("base_center_rail", base_mid, 1, PLYBASE, "under the partition")

# ================================================================ case
# ends: bottom in a rabbet, 1/4 back in a through groove
end_l = _box(X0, 0, BOT_Z0, T18, CASE_D, TOP_Z0 - BOT_Z0)
end_l -= _box(END_IN_L - RABBET_D, -1, BOT_Z0 - 1, RABBET_D + 1, CASE_D + 2, T18 + 1)
end_l -= _box(END_IN_L - BACK_GROOVE_D, BACK_Y0, BOT_Z0 - 1, BACK_GROOVE_D + 1, T6, TOP_Z0 - BOT_Z0 + 2)
end_r = mirror(end_l, Plane.YZ.offset(XC))
add("end", end_l, 2, PLY18,
    f"face grain vertical; {inch(RABBET_D)} x {inch(T18)} (measure) rabbet along the bottom inside edge "
    f"for the case bottom; {inch(BACK_GROOVE_D)} deep x 1/4 ply (measure) groove {inch(BACK_SET)} "
    "from the rear edge, through; mirror pair",
    inst=[("end_l", end_l), ("end_r", end_r)])

# bottom: between the ends in their rabbets, back groove, partition dado
BOT_X0 = END_IN_L - RABBET_D
BOT_X1 = END_IN_R + RABBET_D
bottom = _box(BOT_X0, 0, BOT_Z0, BOT_X1 - BOT_X0, CASE_D, T18)
bottom -= _box(BOT_X0 - 1, BACK_Y0, BOT_Z1 - BACK_GROOVE_D, BOT_X1 - BOT_X0 + 2, T6, BACK_GROOVE_D + 1)
bottom -= _box(PART_X0, BACK_Y1, BOT_Z1 - DADO_D, T18, CASE_D - BACK_Y1 + 1, DADO_D + 1)
add("bottom", bottom, 1, PLY18,
    f"face grain across the 64 in; {inch(BACK_GROOVE_D)} deep back groove {inch(BACK_SET)} from the rear edge; "
    f"{inch(DADO_D)} deep x 3/4 ply (measure) dado for the partition, centered, from the back groove to the front edge; "
    "front edge is covered by the drawer fronts")

# partition: in the bottom dado, stops at the back panel, notched for the nailer
PART_Z0 = BOT_Z1 - DADO_D
partition = _box(PART_X0, BACK_Y1, PART_Z0, T18, CASE_D - BACK_Y1, TOP_Z0 - PART_Z0)
partition -= _box(PART_X0 - 1, NAILER_Y0 - 1, NAILER_Z0, T18 + 2, TS + 1, NAILER_H + 1)
add("partition", partition, 1, PLY18,
    f"face grain vertical; sits in the bottom dado and against the back panel; notch the top rear corner "
    f"{inch(TS)} deep x {inch(NAILER_H)} tall for the nailer")

# nailer: solid maple on edge at the top back, figure-8s for the top, wall screws through it
nailer = _box(END_IN_L, NAILER_Y0, NAILER_Z0, END_IN_R - END_IN_L, TS, NAILER_H)
FIG8_XS = [X0 + CASE_W * f for f in (0.15, 0.37, 0.63, 0.85)]
FIG8_Y = NAILER_Y1 - FIG8_OFFSET
for xc in FIG8_XS:
    nailer -= Pos(xc, FIG8_Y, TOP_Z0 - FIG8_DEPTH) * Cylinder(FIG8_DIA / 2, FIG8_DEPTH + 1,
                                                              align=(Align.CENTER, Align.CENTER, Align.MIN))
add("nailer", nailer, 1, MAPLE,
    f"on edge against the back panel, through the partition notch; four {inch(FIG8_DIA)} figure-8 recesses "
    f"{inch(FIG8_DEPTH)} deep on the top edge, centered {inch(FIG8_OFFSET)} in from the front face; "
    "screw through it and the back into the wall studs")

# back: 1/4 ply in the grooves, nailed to the nailer
back = _box(BOT_X0 + PLAY / 2, BACK_Y0, PART_Z0 + PLAY / 2,
            BOT_X1 - BOT_X0 - PLAY, T6, TOP_Z0 - PART_Z0 - PLAY)
add("back", back, 1, PLY6, "plain rectangle; slides down the end grooves into the bottom groove; "
    "confirm the low receptacle on the back wall before cutting")

# scribe strips: solid maple on the ends' front edges, out to the walls
strip = _box(0, FACE_Y0, BASE_H, STRIP_W, FACE_T, TOP_Z0 - BASE_H)
add("scribe_strip", strip, 2, MAPLE,
    f"rip at {inch(STRIP_CUT)}, scribe to the wall so the inner edge lands flush with the inside of the end panel "
    f"(about {inch(STRIP_W)}); glue and biscuits to the end's front edge; mill to the ply thickness; painted white",
    inst=[("strip_l", strip), ("strip_r", mirror(strip, Plane.YZ.offset(ALCOVE_W / 2)))])

# plinth: solid maple, flush with the fronts, 1/8 reveal under them
plinth = _box(0, FACE_Y0, 0, ALCOVE_W, FACE_T, PLINTH_H)
add("plinth", plinth, 1, MAPLE,
    f"cut 4-1/4 tall and scribe to the floor so the top edge sits {inch(GAP)} under the fronts; "
    "scribe the ends to the walls; grain horizontal; mill to the ply thickness; screwed to the base front rail; painted white")

# ================================================================ top: solid maple, floats on the nailer figure-8s
top = _box(0, TOP_Y0, TOP_Z0, ALCOVE_W, TOP_Y1 - TOP_Y0, TS)
top = fillet(top.edges().filter_by(Axis.X).group_by(Axis.Y)[-1], ROUND)
add("top", top, 1, MAPLE,
    f"glue up from 4 or 5 boards, grain along the 66 in; {inch(ROUND)} roundover on both front arrises; "
    f"scribe the ends to the walls; {inch(WALL_GAP)} gap at the back wall; pocket screws up through the ends "
    "and partition near the front, figure-8s on the nailer at the back")

# ================================================================ drawer fronts: maple frame, walnut panel, T&G
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


FRONT_X0 = [END_IN_L + GAP, END_IN_L + GAP + FRONT_W + GAP]
_fl = front_parts(FRONT_X0[0])
_fr = front_parts(FRONT_X0[1])
add("front_stile", _fl[0], 4, MAPLE,
    f"{inch(TONGUE_T)} x {inch(TONGUE_L)} groove on the inner edge, through, front wall {inch(FACE_T - PANEL_T)} thick (set the fence from the panel ply); the rail tenons show on both ends (the top one is the visible one); painted white",
    inst=[("stile_ll", _fl[0]), ("stile_lr", _fl[1]), ("stile_rl", _fr[0]), ("stile_rr", _fr[1])])
add("front_rail", _fl[2], 4, MAPLE,
    f"{inch(TONGUE_T)} x {inch(TONGUE_L)} groove on the inner edge, through; {inch(TONGUE_T)} x {inch(TONGUE_L)} "
    f"stub tenon on both ends (same bit); length includes both tenons; painted white",
    inst=[("rail_lb", _fl[2]), ("rail_lt", _fl[3]), ("rail_rb", _fr[2]), ("rail_rt", _fr[3])])
add("front_panel", _fl[4], 2, WALNUT,
    f"{inch(TONGUE_T)} x {inch(TONGUE_L)} tongue on all four edges, flush with the show face (rabbet the BACK edges "
    f"{inch(PANEL_T - TONGUE_T)} deep); grain horizontal; size includes the tongues; back flush with the frame back, "
    f"face {inch(FACE_T - PANEL_T)} below the maple; glue in (plywood, no movement)",
    inst=[("panel_l", _fl[4]), ("panel_r", _fr[4])])

front_l = _fl[0] + _fl[1] + _fl[2] + _fl[3] + _fl[4]
assert len(front_l.solids()) == 1, "front frame and panel do not close up"
_bb = front_l.bounding_box()
assert abs(_bb.size.X - FRONT_W) < 1e-6 and abs(_bb.size.Z - FRONT_H) < 1e-6 and abs(_bb.size.Y - FACE_T) < 1e-6
# the panel face sits FACE_T - PANEL_T below the frame face, and its back is flush with the frame back
_pb = _fl[4].bounding_box()
assert abs(_pb.min.Y - FACE_Y0) < 1e-6 and abs((FACE_Y1 - _pb.max.Y) - (FACE_T - PANEL_T)) < 1e-6, "panel is not inset"
assert abs(_pb.max.Y - (GY0 + TONGUE_T)) < 1e-6, "tongue is not flush with the panel face"

# ================================================================ drawer boxes: Blum 563H
BOX_W = OPEN_W - UM_WIDTH_LOSS + 2 * T12
BOX_IN_W = OPEN_W - UM_WIDTH_LOSS
BOX_H = 9.5 * IN
BOX_D = SLIDE_LEN
BOX_Z0 = BOT_Z1 + UM_BOTTOM_CLEAR
BOX_Y1 = CASE_D - UM_FRONT_GAP
BOX_Y0 = BOX_Y1 - BOX_D
END_LEN = BOX_W - 2 * (T12 - RABBET_D)      # drawer front and back length (1/2 Baltic birch, in the side rabbets)
BOTTOM_D = BOX_D - 2 * T12 + RABBET_D        # bottom: 1/4 into the front groove, butted to the back (no back groove)


def make_drawer(bay_x0, sfx):
    xc = bay_x0 + OPEN_W / 2
    x0 = xc - BOX_W / 2
    z0, y0, y1 = BOX_Z0, BOX_Y0, BOX_Y1
    gz = z0 + UM_RECESS                      # underside of the bottom
    # side: rabbets at both ends on the inner face, bottom groove through
    side = _box(x0, y0, z0, T12, BOX_D, BOX_H)
    side -= _box(x0 + T12 - RABBET_D, y1 - T12, z0 - 1, RABBET_D + 1, T12 + 1, BOX_H + 2)
    side -= _box(x0 + T12 - RABBET_D, y0 - 1, z0 - 1, RABBET_D + 1, T12 + 1, BOX_H + 2)
    side -= _box(x0 + T12 - RABBET_D, y0 - 1, gz, RABBET_D + 1, BOX_D + 2, T12)
    side_r = mirror(side, Plane.YZ.offset(xc))
    # front: 1/2 birch between the sides, bottom groove
    ex0 = x0 + T12 - RABBET_D
    front = _box(ex0, y1 - T12, z0, END_LEN, T12, BOX_H)
    front -= _box(ex0 - 1, y1 - T12 - 1, gz, END_LEN + 2, RABBET_D + 1, T12)
    # back: 1/2 birch, no groove (the 10 mm hook bore leaves only 2 mm of a 12 mm back), Blum hook notches and bores
    backp = _box(ex0, y0, z0, END_LEN, T12, BOX_H)
    nw = UM_HOOK_NOTCH_W + RABBET_D              # back end sits in the rabbet; notch measured from the side's inner face
    for xe in (ex0, ex0 + END_LEN - nw):
        backp -= _box(xe, y0 - 1, z0 - 1, nw, T12 + 2, UM_HOOK_NOTCH_H + 1)
    dia, depth, off, up = UM_HOOK_BORE
    for xin in (x0 + T12, x0 + BOX_W - T12):          # sides' inner faces
        bx = xin + off if xin < xc else xin - off
        backp -= Pos(bx, y0 - 1, z0 + up) * Rot(-90, 0, 0) * Cylinder(dia / 2, depth + 1,
                                                                        align=(Align.CENTER, Align.CENTER, Align.MIN))
    # bottom: 1/2 Baltic birch in the side and front grooves, butted to the back
    bx0 = x0 + T12 - RABBET_D + PLAY / 2
    by0 = y0 + T12
    bot = _box(bx0, by0, gz, BOX_W - 2 * (T12 - RABBET_D) - PLAY, BOTTOM_D - PLAY / 2, T12)
    return side, side_r, front, backp, bot


_dl = make_drawer(END_IN_L, "l")
_dr = make_drawer(PART_X0 + T18, "r")
add("drawer_side", _dl[0], 4, BB12,
    f"{inch(RABBET_D)} deep x 1/2 BB (measure) rabbet across both ends on the inside face; "
    f"{inch(RABBET_D)} deep x 1/2 BB (measure) bottom groove, underside {inch(UM_RECESS)} up from the bottom edge, through",
    inst=[("dside_ll", _dl[0]), ("dside_lr", _dl[1]), ("dside_rl", _dr[0]), ("dside_rr", _dr[1])])
add("drawer_front", _dl[2], 2, BB12,
    f"box front, sits in the side rabbets; {inch(RABBET_D)} deep bottom groove to match the sides; "
    "the front screws to it from inside through 4 oversize holes: #8 x 7/8 in, pre-drilled, so the bite stays short of the "
    "face; the box front overlaps the top rail by 1-1/8 in (best bite) and the panel field, but the bottom rail by only 1/4 in",
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
for i, bay_x0 in enumerate((END_IN_L, PART_X0 + T18)):
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
cushion = _box(0.25 * IN, 0, SEAT_Z, ALCOVE_W - 0.5 * IN, TOP_Y1, CUSHION_H)
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
assert OVERHANG_MIN - 1e-6 <= OVERHANG <= OVERHANG_MIN + 1.5, OVERHANG
assert abs(FRONT_X0[0] - END_IN_L - GAP) < 1e-9 and abs(END_IN_R - (FRONT_X0[1] + FRONT_W) - GAP) < 1e-9
assert abs(FRONT_X0[1] - (FRONT_X0[0] + FRONT_W) - GAP) < 1e-9
assert abs(TOP_Z0 - (FRONT_Z0 + FRONT_H) - GAP) < 1e-9 and abs(FRONT_Z0 - PLINTH_H - GAP) < 1e-9
assert abs(STRIP_W - END_IN_L) < 1e-9

# Blum
assert abs(BOX_IN_W - (OPEN_W - UM_WIDTH_LOSS)) < 1e-6
assert abs(BOX_Z0 - BOT_Z1 - UM_BOTTOM_CLEAR) < 1e-6
assert TOP_Z0 - (BOX_Z0 + BOX_H) >= UM_TOP_CLEAR, "box too tall for the opening"
assert abs(BOX_D - SLIDE_LEN) < 1e-6
assert CASE_D - BACK_Y1 >= UM_MIN_DEPTH, "case too shallow for the 21 in runner"
assert BOX_Y0 > NAILER_Y1 and BOX_Y0 > BACK_Y1, "box hits the nailer or back"
assert T12 - UM_HOOK_BORE[1] >= 1.9, "hook bore would break through the back"   # a 2 mm skin; test-drill scrap first
# the bore is really there, in wood, and stops short of the groove
_dia, _depth, _off, _up = UM_HOOK_BORE
_bx = _dl[0].bounding_box().min.X + T12 + _off              # left box, left bore center
_probe_air = Pos(_bx, BOX_Y0 + 1, BOX_Z0 + _up) * Rot(-90, 0, 0) * Cylinder(_dia / 2 - 0.5, _depth - 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
assert vol(_probe_air & part("drawer_back")) < 1e-3, "hook bore not cut"
_probe_wood = _box(_bx - 1, BOX_Y0 + _depth + 0.3, BOX_Z0 + _up - 1, 2, T12 - _depth - 0.6, 2)
assert abs(vol(_probe_wood & part("drawer_back")) - _probe_wood.volume) < 1e-3, "no wood between the bore and the back's front face"

_sx = _dl[0].bounding_box().min.X + T12                     # left side inner face
_notch_air = _box(_sx + 0.5, BOX_Y0 + 0.5, BOX_Z0 + 0.5, UM_HOOK_NOTCH_W - 1, T12 - 1, UM_HOOK_NOTCH_H - 1)
assert vol(_notch_air & part("drawer_back")) < 1e-3, "rear notch not cut"
_notch_wood = _box(_sx + UM_HOOK_NOTCH_W + 0.3, BOX_Y0 + 0.5, BOX_Z0 + 0.5, 2, T12 - 1, UM_HOOK_NOTCH_H - 1)
assert abs(vol(_notch_wood & part("drawer_back")) - _notch_wood.volume) < 1e-3, "rear notch too wide"
assert abs((BOX_Z0 + UM_RECESS) - (BOX_Z0 + UM_HOOK_NOTCH_H)) < 1e-6, "notch not flush with the bottom"

# housed joints measured from the geometry
def housed(guest, host, probe):
    assert vol(probe & guest) > probe.volume * 0.999, "probe not inside guest"
    assert vol(probe & host) < 1e-6, "host not relieved for the guest"


housed(part("bottom"), part("end"), _box(BOT_X0 + 0.5, CASE_D / 2, BOT_Z0 + 0.5, RABBET_D - 1, 10, T18 - 1))
housed(part("partition"), part("bottom"), _box(PART_X0 + 0.5, CASE_D / 2, PART_Z0 + 0.5, T18 - 1, 10, DADO_D - 1))
housed(part("back"), part("end"), _box(BOT_X0 + PLAY / 2 + 0.2, BACK_Y0 + 0.5, TOP_Z0 / 2, 4, T6 - 1, 10))
housed(part("back"), part("bottom"), _box(XC - 5, BACK_Y0 + 0.5, PART_Z0 + PLAY / 2 + 0.2, 10, T6 - 1, 4))
housed(part("nailer"), part("partition"), _box(PART_X0 + 0.5, NAILER_Y0 + 0.5, NAILER_Z0 + 0.5, T18 - 1, TS - 1, 10))
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

assembly = Compound(children=[s for _, s in INST] + [s for _, s in HW])

# ================================================================ outputs
TMP = os.environ.get("TMP_STL")
if TMP:
    SUBSETS = {   # SUBSET=case|fronts|drawers|nocushion|drawer1 picks instances by name prefix for the renders
        "case": ("base_", "end_", "bottom", "partition", "nailer", "back", "strip_", "plinth"),
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
         "material": "hardware", "notes": "one pair per drawer; 90 lb dynamic; runner front sits 3/32 behind the case front edge"},
        {"part": "Blum locking devices T51.1901 R and L", "qty": 2, "unit": "pair", "material": "hardware",
         "notes": "front corners under the drawer bottom, screwed into the 1/2 box front: use #6 x 1/2 so the points stay inside it"},
        {"part": "Brass bar pull, 8 in", "qty": 2, "unit": "ea", "material": "hardware",
         "notes": "break-away machine screws long enough for 1/2 panel + 1/2 box front"},
        {"part": "Figure-8 tabletop fasteners", "qty": 4, "unit": "ea", "material": "hardware", "notes": "nailer to top"},
        {"part": "Pocket screws #8 x 1-1/4 fine", "qty": 6, "unit": "ea", "material": "hardware",
         "notes": "ends and partition to the top, near the front"},
        {"part": "Bench cushion", "qty": 1, "unit": "ea", "material": "soft goods",
         "notes": f"about {inch(ALCOVE_W - 0.5 * IN)} x {inch(TOP_Y1)} x {inch(CUSHION_H)}, boxed"},
    ]
    write_cut_list(PARTS, f"{PROJ}/cutlist.md", csv_path=f"{PROJ}/cutlist.csv",
                   title="Built-in bench 66 x 28 (frameless, two drawers)", units="in", denom=32,
                   extra_lines=HARDWARE_LINES)
    export_step(assembly, f"{PROJ}/built_in_bench.step")
    print("exported cutlist + step")

if os.environ.get("SHOW"):
    from ocp_vscode import show, set_port, Camera
    set_port(3939)
    show(*[s for _, s in INST + HW], names=[n for n, _ in INST + HW],
         reset_camera=(Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP))

print("OK  parts:", [p["name"] for p in PARTS])
print(f"case front {inch(CASE_D)}  fronts {inch(FRONT_W)} x {inch(FRONT_H)}  overhang {inch(OVERHANG)}  "
      f"opening {inch(OPEN_W)} x {inch(OPEN_H)}  box {inch(BOX_W)} x {inch(BOX_H)} x {inch(BOX_D)}  "
      f"top {inch(ALCOVE_W)} x {inch(TOP_Y1 - TOP_Y0)}")
