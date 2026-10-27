#!/usr/bin/env python
"""Freestanding bench for the 66 x 28 in former wet-bar alcove: the built-in bench's case (two drawers on Blum
TANDEM 563H undermounts, all-white frame-and-panel fronts on a tongue-and-groove bit set, solid maple top, 3 in
cushion) lifted onto a base that leaves CLEAR (5 in) of open floor under it for the robot vacuum, with finished ends,
1 in of air to each wall and the alcove's baseboard left in place, so it slides in and out as a piece of furniture.
The client asked for this on 2026-10-26; the built-in design stays untouched in projects/Built-in-bench in case they
go back to it.

What carried over unchanged (Brian's locked picks): wood top at 14 in (seat 17 in with the cushion), frameless case,
full-overlay fronts built as a 1-1/2 in maple frame around a 1/2 in paint-grade panel inset 1/4 in, all painted
white, 8 in brass bar pulls, 3/4 in overhang with an eased edge, solid glued-up maple top whose front edge is 3 in
back from the pilaster faces, one full-depth cushion, 21 in slides, 1/2 in Baltic birch boxes, Osmo Natural on the
bare maple. What changed: no plinth, no scribe strips, no wall screws; the case is 62-1/2 wide under a 64 in top
(3/4 overhang at both ends), the back is 1/2 in from the wall, the ends are show faces (painted white, edges banded),
the drawer boxes are 6-1/2 in tall instead of 8-1/2 (the 5 in of clear floor come out of the drawers, the seat
height stays for the senior dog), and the base is one of three (BASE env var, default legs):

  legs    four 2 in square solid maple legs 2-1/2 in in from the ends in a C-frame of 3/4 x 2-1/2 maple rails: an
          end rail front to back at each end and one back rail, no front rail, so the robot drives in under the
          whole front; the legs sit 2 in inside the case back, clear of the baseboard and its shoe
  blades  two 1-1/2 in solid maple blades on edge, front to back under the ends, with the same back rail
  gables  the end panels run to the floor (notched at the back for the baseboard) with a stretcher at the back

Axes as in built_in_bench.py: X across the alcove (0 at the wall on your RIGHT when you face the bench from the
room; _l/_r suffixes are model names, the bench is symmetric), Y depth (0 at the back wall, +Y toward the room),
Z up (0 at the floor). Units mm; inch constants are written as n * IN. One named solid per part in PARTS, every
placed instance in INST, hardware (slides, pulls, cushion) in HW for the viewer only.

Run:  .venv/bin/python projects/Freestanding-bench/freestanding_bench.py
      BASE=legs|blades|gables ...   pick the base (default legs)
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
BASE = os.environ.get("BASE", "legs")
assert BASE in ("legs", "blades", "gables"), BASE


def inch(mm):
    return inch_frac(mm, 32)


# ---------------------------------------------------------------- the space
ALCOVE_W = 66 * IN          # between the pilasters (X, 0 at the wall on your right from the room)
ALCOVE_D = 28 * IN          # back wall to the pilaster faces (Y)
TOP_SETBACK = 3 * IN        # top front edge back from the pilaster faces (as the built-in)
BASEBOARD_H = 4 * IN        # the alcove's baseboard stays; it and its shoe stand about 1-1/4 in off the wall
BASEBOARD_T = 1.25 * IN

# ---------------------------------------------------------------- picks
SEAT_Z = 14 * IN            # top face of the wood top (seat 17 in with the cushion, kept for the senior dog)
CUSHION_H = 3 * IN
CLEAR = 5 * IN              # floor to the underside of the case: the robot vacuum (tallest Roomba about 3.9 in)
SIDE_AIR = 1.0 * IN         # top end to each wall, so the piece slides in and out
WALL_GAP = 0.5 * IN         # case back and top rear edge to the back wall
OVERHANG_MIN = 0.75 * IN    # 3/4 in overhang at the front (actual is derived below)
END_OVERHANG = 0.75 * IN    # top past each case end
GAP = 0.125 * IN            # reveal between the fronts and under the top
END_REVEAL = 0.0625 * IN    # the fronts stop this short of the case ends
ROUND = 0.125 * IN          # eased arrises of the top: front and both ends

# ---------------------------------------------------------------- stock (actual, MEASURE)
T18 = 18.0                  # 3/4 maple ply
T12 = 12.0                  # 1/2 Baltic birch (drawer sides, bottoms) and the 1/2 paint-grade panels
T6 = 6.35                   # 1/4 maple ply back (nominal; the groove is cut to the measured sheet)
TS = 0.75 * IN              # solid maple: top, nailer, base rails
FACE_T = T18                # everything in the front plane is milled to the ply

# ---------------------------------------------------------------- joinery
RABBET_D = 0.25 * IN        # case bottom in the ends; drawer ends in the sides
DADO_D = 0.25 * IN          # partition in the case bottom
BACK_GROOVE_D = 0.25 * IN   # 1/4 back in the ends and bottom
BACK_SET = 0.25 * IN        # back panel groove this far in from the rear edge
PLAY = 1.6                  # 1/16 in total play on housed panels
TONGUE_T = 0.25 * IN        # front frames: tongue-and-groove bit set
TONGUE_L = 0.375 * IN
PANEL_T = T12                # 1/2 panel (ply or MDF, measures 12 mm): back flush with the frame, face inset FACE_T - PANEL_T
STILE_W = 1.5 * IN          # maple frame width on the fronts
NAILER_H = 2.5 * IN

# ---------------------------------------------------------------- base
LEG_SQ = 2.0 * IN           # legs: solid maple, square
LEG_IN_X = 2.5 * IN         # leg (or blade) outer face in from the case end
LEG_IN_FRONT = 2.0 * IN     # leg front face behind the case front edge
LEG_IN_BACK = 2.0 * IN      # leg rear face in from the case back (clears the baseboard and shoe)
RAIL_H = 2.5 * IN           # base rails: 3/4 x 2-1/2 maple on edge, top edges flush with the leg tops
RAIL_T = TS
BLADE_T = 1.5 * IN          # blades: solid maple on edge
NOTCH_D = BASEBOARD_T       # gables: notch at the rear bottom corner for the baseboard and shoe
NOTCH_H = BASEBOARD_H + 0.5 * IN

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
TOP_X0 = SIDE_AIR                         # the top: 64 in between 1 in of air at each wall
TOP_X1 = ALCOVE_W - SIDE_AIR
TOP_W = TOP_X1 - TOP_X0
X0 = TOP_X0 + END_OVERHANG                # end panel outer faces: 62-1/2 in case
X1 = TOP_X1 - END_OVERHANG
CASE_W = X1 - X0
CASE_Y0 = WALL_GAP                        # case back (rear face of the ends and bottom)
CASE_D = 23.5 * IN                        # back wall to the case front edge (as the built-in)
FACE_Y0 = CASE_D                          # fronts sit on the case front
FACE_Y1 = FACE_Y0 + FACE_T
TOP_Y1 = ALCOVE_D - TOP_SETBACK           # 25 in from the back wall
TOP_Y0 = WALL_GAP                         # flush with the case back (a rear overhang would cost Blum its 557 mm)
TOP_D = TOP_Y1 - TOP_Y0
OVERHANG = TOP_Y1 - FACE_Y1
TOP_Z0 = SEAT_Z - TS
BOT_Z0 = CLEAR                            # case bottom's underside: the clear floor
BOT_Z1 = BOT_Z0 + T18
OPEN_H = TOP_Z0 - BOT_Z1
END_Z0 = 0.0 if BASE == "gables" else CLEAR
XC = (X0 + X1) / 2                        # partition center
PART_X0 = XC - T18 / 2
END_IN_L = X0 + T18                       # end inner face at low X
END_IN_R = X1 - T18                       # end inner face at high X
OPEN_W = PART_X0 - END_IN_L               # one bay
FRONT_W = (CASE_W - 2 * END_REVEAL - GAP) / 2
FRONT_Z0 = CLEAR                          # fronts cover the case bottom's edge, flush with its underside
FRONT_H = TOP_Z0 - GAP - FRONT_Z0
FRONT_X0 = [X0 + END_REVEAL, X0 + END_REVEAL + FRONT_W + GAP]
BACK_Y0 = CASE_Y0 + BACK_SET
BACK_Y1 = BACK_Y0 + T6
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
PLY6 = "1/4 maple ply"
PAINT_PANEL = "1/2 paint-grade panel"   # MDF or paint-grade ply, painted white with the frames (Brian 2026-10-24)
BB12 = "1/2 Baltic birch"

# ================================================================ case
# ends: show faces now (painted white, front and bottom edges banded); bottom in a rabbet (a dado on a gable),
# 1/4 back in a groove, through at the top
end_l = _box(X0, CASE_Y0, END_Z0, T18, CASE_D - CASE_Y0, TOP_Z0 - END_Z0)
if BASE == "gables":
    end_l -= _box(END_IN_L - RABBET_D, CASE_Y0 - 1, BOT_Z0, RABBET_D + 1, CASE_D - CASE_Y0 + 2, T18)
    end_l -= _box(END_IN_L - BACK_GROOVE_D, BACK_Y0, BOT_Z0, BACK_GROOVE_D + 1, T6, TOP_Z0 - BOT_Z0 + 2)
    end_l -= _box(X0 - 1, CASE_Y0 - 1, -1, T18 + 2, NOTCH_D + 1, NOTCH_H + 1)
    END_NOTE = (f"gable to the floor, face grain vertical; {inch(RABBET_D)} deep x {inch(T18)} (measure) dado across "
                f"the inside face with its bottom {inch(BOT_Z0)} up for the case bottom; {inch(BACK_GROOVE_D)} deep x "
                f"1/4 ply (measure) groove {inch(BACK_SET)} from the rear edge from the dado up through the top; notch "
                f"{inch(NOTCH_D)} x {inch(NOTCH_H)} at the rear bottom corner for the baseboard and shoe; band the "
                "front and bottom edges; painted white; mirror pair")
else:
    end_l -= _box(END_IN_L - RABBET_D, CASE_Y0 - 1, BOT_Z0 - 1, RABBET_D + 1, CASE_D - CASE_Y0 + 2, T18 + 1)
    end_l -= _box(END_IN_L - BACK_GROOVE_D, BACK_Y0, BOT_Z0 - 1, BACK_GROOVE_D + 1, T6, TOP_Z0 - BOT_Z0 + 2)
    END_NOTE = (f"show face out, face grain vertical; {inch(RABBET_D)} x {inch(T18)} (measure) rabbet along the bottom "
                f"inside edge for the case bottom; {inch(BACK_GROOVE_D)} deep x 1/4 ply (measure) groove {inch(BACK_SET)} "
                "from the rear edge, through; iron-on maple band on the front and bottom edges; painted white; mirror pair")
end_r = mirror(end_l, Plane.YZ.offset(XC))
add("end", end_l, 2, PLY18, END_NOTE, inst=[("end_l", end_l), ("end_r", end_r)])

# bottom: between the ends in their rabbets, back groove, partition dado
BOT_X0 = END_IN_L - RABBET_D
BOT_X1 = END_IN_R + RABBET_D
bottom = _box(BOT_X0, CASE_Y0, BOT_Z0, BOT_X1 - BOT_X0, CASE_D - CASE_Y0, T18)
bottom -= _box(BOT_X0 - 1, BACK_Y0, BOT_Z1 - BACK_GROOVE_D, BOT_X1 - BOT_X0 + 2, T6, BACK_GROOVE_D + 1)
bottom -= _box(PART_X0, BACK_Y1, BOT_Z1 - DADO_D, T18, CASE_D - BACK_Y1 + 1, DADO_D + 1)
add("bottom", bottom, 1, PLY18,
    f"face grain across the {inch(CASE_W)}; {inch(BACK_GROOVE_D)} deep back groove {inch(BACK_SET)} from the rear edge; "
    f"{inch(DADO_D)} deep x 3/4 ply (measure) dado for the partition, centered, from the back groove to the front edge; "
    "front edge is covered by the drawer fronts; the base screws to its underside")

# partition: in the bottom dado, stops at the back panel, notched for the nailer
PART_Z0 = BOT_Z1 - DADO_D
partition = _box(PART_X0, BACK_Y1, PART_Z0, T18, CASE_D - BACK_Y1, TOP_Z0 - PART_Z0)
partition -= _box(PART_X0 - 1, NAILER_Y0 - 1, NAILER_Z0, T18 + 2, TS + 1, NAILER_H + 1)
add("partition", partition, 1, PLY18,
    f"face grain vertical; sits in the bottom dado and against the back panel; notch the top rear corner "
    f"{inch(TS)} deep x {inch(NAILER_H)} tall for the nailer")

# nailer: solid maple on edge at the top back; figure-8s for the top; it ties the ends and stiffens the back
nailer = _box(END_IN_L, NAILER_Y0, NAILER_Z0, END_IN_R - END_IN_L, TS, NAILER_H)
FIG8_XS = [X0 + CASE_W * f for f in (0.15, 0.37, 0.63, 0.85)]
FIG8_Y = NAILER_Y1 - FIG8_OFFSET
for xc in FIG8_XS:
    nailer -= Pos(xc, FIG8_Y, TOP_Z0 - FIG8_DEPTH) * Cylinder(FIG8_DIA / 2, FIG8_DEPTH + 1,
                                                              align=(Align.CENTER, Align.CENTER, Align.MIN))
add("nailer", nailer, 1, MAPLE,
    f"on edge against the back panel, through the partition notch; four {inch(FIG8_DIA)} figure-8 recesses "
    f"{inch(FIG8_DEPTH)} deep on the top edge, centered {inch(FIG8_OFFSET)} in from the front face; "
    "glued to the back, screwed through the ends into its ends (no wall screws: the piece is freestanding)")

# back: 1/4 ply in the grooves, glued in (it is the shear panel that keeps a freestanding case square)
back = _box(BOT_X0 + PLAY / 2, BACK_Y0, PART_Z0 + PLAY / 2,
            BOT_X1 - BOT_X0 - PLAY, T6, TOP_Z0 - PART_Z0 - PLAY)
add("back", back, 1, PLY6, "plain rectangle; slides down the end grooves into the bottom groove; glued in all round "
    "(with no wall screws it is what keeps the case square)")

# ================================================================ top: solid maple, pocket screws at the front, figure-8s at the back
top = _box(TOP_X0, TOP_Y0, TOP_Z0, TOP_W, TOP_D, TS)
_front = top.edges().filter_by(Axis.X).group_by(Axis.Y)[-1]
_ends = top.edges().filter_by(Axis.Y)
top = fillet(_front + _ends, ROUND)
add("top", top, 1, MAPLE,
    f"glue up from 4 or 5 boards, grain along the {inch(TOP_W)}; {inch(ROUND)} roundover on the front and both end "
    f"arrises, top and bottom (the back edge stays square against the wall); overhangs the case {inch(END_OVERHANG)} at "
    f"each end and {inch(OVERHANG)} at the front, flush with the case back; pocket screws up through the ends and "
    "partition near the front, figure-8s on the nailer at the back")

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
BOX_H = 6.5 * IN            # was 8.5 in the built-in: the opening is 7-17/32 now, Blum allows opening minus 21 mm
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


_dl = make_drawer(END_IN_L, "l")
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

# ================================================================ base
BASE_NAMES = set()
if BASE == "legs":
    LEG_X = [X0 + LEG_IN_X, X1 - LEG_IN_X - LEG_SQ]                       # min X of the low-X and high-X legs
    LEG_Y = [CASE_Y0 + LEG_IN_BACK, CASE_D - LEG_IN_FRONT - LEG_SQ]       # min Y of the back and front legs
    leg = _box(LEG_X[0], LEG_Y[1], 0, LEG_SQ, LEG_SQ, CLEAR)
    _dx, _dy = LEG_X[1] - LEG_X[0], LEG_Y[0] - LEG_Y[1]
    add("leg", leg, 4, MAPLE,
        f"{inch(LEG_SQ)} square, {inch(CLEAR)} tall; bare maple under Osmo like the top; glued and screwed to the case "
        "bottom with two #8 x 2 down through it (under the drawer boxes), rails pocket-screwed into them",
        inst=[("leg_lf", leg), ("leg_lb", Pos(0, _dy, 0) * leg), ("leg_rf", Pos(_dx, 0, 0) * leg),
              ("leg_rb", Pos(_dx, _dy, 0) * leg)])
    _ry0, _ry1 = LEG_Y[0] + LEG_SQ, LEG_Y[1]
    _rx = LEG_X[0] + LEG_SQ / 2 - RAIL_T / 2
    end_rail = _box(_rx, _ry0, CLEAR - RAIL_H, RAIL_T, _ry1 - _ry0, RAIL_H)
    add("base_end_rail", end_rail, 2, MAPLE,
        f"on edge between the front and back legs, centered on them, top edge flush with the leg tops; glue and two pocket "
        "screws into each leg from the inside face; three pocket screws up into the case bottom",
        inst=[("brail_end_l", end_rail), ("brail_end_r", Pos(_dx, 0, 0) * end_rail)])
    _bx0, _bx1 = LEG_X[0] + LEG_SQ, LEG_X[1]
    _by = LEG_Y[0] + LEG_SQ / 2 - RAIL_T / 2
    back_rail = _box(_bx0, _by, CLEAR - RAIL_H, _bx1 - _bx0, RAIL_T, RAIL_H)
    add("base_back_rail", back_rail, 1, MAPLE,
        "on edge between the two back legs, centered on them, top edge flush with the leg tops; glue and two pocket "
        "screws into each leg from the front face; four pocket screws up into the case bottom; no front rail, the "
        "robot vacuum drives in under the fronts", inst=[("brail_back", back_rail)])
    BASE_NAMES = {"leg_lf", "leg_lb", "leg_rf", "leg_rb", "brail_end_l", "brail_end_r", "brail_back"}
elif BASE == "blades":
    _bx = X0 + LEG_IN_X
    _by0, _by1 = CASE_Y0 + LEG_IN_BACK, CASE_D - LEG_IN_FRONT
    blade = _box(_bx, _by0, 0, BLADE_T, _by1 - _by0, CLEAR)
    add("blade", blade, 2, MAPLE,
        f"{inch(BLADE_T)} thick, {inch(CLEAR)} tall, on edge front to back, outer face {inch(LEG_IN_X)} in from the case "
        "end; bare maple under Osmo like the top; glued and screwed to the case bottom with four #8 x 2 down through it",
        inst=[("blade_l", blade), ("blade_r", mirror(blade, Plane.YZ.offset(XC)))])
    _rx0, _rx1 = _bx + BLADE_T, X1 - LEG_IN_X - BLADE_T
    _by = _by0 + 1.0 * IN
    back_rail = _box(_rx0, _by, CLEAR - RAIL_H, _rx1 - _rx0, RAIL_T, RAIL_H)
    add("base_back_rail", back_rail, 1, MAPLE,
        "on edge between the blades 1 in in from their rear ends, top edge flush with the blade tops; glue and two pocket "
        "screws into each blade; four pocket screws up into the case bottom", inst=[("brail_back", back_rail)])
    BASE_NAMES = {"blade_l", "blade_r", "brail_back"}
else:   # gables: the ends themselves; a stretcher between them at the bottom back
    _by = CASE_Y0 + NOTCH_D + 0.5 * IN
    back_rail = _box(END_IN_L, _by, CLEAR - RAIL_H, END_IN_R - END_IN_L, RAIL_T, RAIL_H)
    add("base_back_rail", back_rail, 1, MAPLE,
        "stretcher on edge between the gables under the case bottom, behind the baseboard notch; glue and pocket screws "
        "into the gables and up into the case bottom", inst=[("brail_back", back_rail)])
    BASE_NAMES = {"brail_back"}

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
assert OVERHANG_MIN - 1e-6 <= OVERHANG <= OVERHANG_MIN + 1.5, OVERHANG
assert abs(FRONT_X0[0] - X0 - END_REVEAL) < 1e-9 and abs(X1 - (FRONT_X0[1] + FRONT_W) - END_REVEAL) < 1e-9
assert abs(FRONT_X0[1] - (FRONT_X0[0] + FRONT_W) - GAP) < 1e-9
assert abs(TOP_Z0 - (FRONT_Z0 + FRONT_H) - GAP) < 1e-9 and abs(FRONT_Z0 - BOT_Z0) < 1e-9
_all = Compound(children=[s for _, s in INST])
_bbw = _all.bounding_box()
assert abs(_bbw.min.X - TOP_X0) < 1e-6 and abs(_bbw.max.X - TOP_X1) < 1e-6, "the top is the widest part"
assert _bbw.min.X >= SIDE_AIR - 1e-6 and _bbw.max.X <= ALCOVE_W - SIDE_AIR + 1e-6, "air to the walls"
assert abs(_bbw.min.Y - WALL_GAP) < 1e-6 and abs(_bbw.max.Y - TOP_Y1) < 1e-6
assert abs(_bbw.min.Z) < 1e-6 and abs(_bbw.max.Z - SEAT_Z) < 1e-6

# the clear floor: everything except the base starts at CLEAR; the base meets the case bottom; the rails stay high
for n, s in INST:
    bb = s.bounding_box()
    if n in BASE_NAMES:
        assert abs(bb.max.Z - CLEAR) < 1e-6, f"{n} does not meet the case bottom"
        assert bb.min.Z >= -1e-6, n
        assert bb.min.Y >= CASE_Y0 + BASEBOARD_T - 1e-6, f"{n} stands on the baseboard"
    elif BASE == "gables" and n.startswith("end_"):
        assert abs(bb.min.Z) < 1e-6, n
    else:
        assert bb.min.Z >= CLEAR - 1e-6, f"{n} hangs below the clear floor"
for n, s in INST:
    if n.startswith("brail_"):
        assert abs(s.bounding_box().min.Z - (CLEAR - RAIL_H)) < 1e-6, n
if BASE == "legs":
    assert LEG_Y[0] >= CASE_Y0 + BASEBOARD_T + 0.5 * IN, "back legs too close to the baseboard"
    assert LEG_X[0] > TOP_X0 and LEG_X[1] + LEG_SQ < TOP_X1
    # the leg screw spots are under the drawer boxes, not under the runners
    assert LEG_X[0] > END_IN_L + 37.0 and LEG_X[1] + LEG_SQ < END_IN_R - 37.0, "a leg top sits under a runner"
if BASE == "gables":
    _notch_air = _box(X0 + 0.5, CASE_Y0 + 0.5, 0.5, T18 - 1, NOTCH_D - 1, NOTCH_H - 1)
    assert vol(_notch_air & part("end")) < 1e-3, "baseboard notch not cut"
    assert NOTCH_H >= BASEBOARD_H + 0.25 * IN and NOTCH_D >= BASEBOARD_T

# Blum
assert abs(BOX_IN_W - (OPEN_W - UM_WIDTH_LOSS)) < 1e-6
assert abs(BOX_Z0 - BOT_Z1 - UM_BOTTOM_CLEAR) < 1e-6
assert TOP_Z0 - (BOX_Z0 + BOX_H) >= UM_TOP_CLEAR, "box too tall for the opening"
assert abs(BOX_D - SLIDE_LEN) < 1e-6
assert CASE_D - BACK_Y1 >= UM_MIN_DEPTH, "case too shallow for the 21 in runner"
assert BOX_Y0 > NAILER_Y1 and BOX_Y0 > BACK_Y1, "box hits the nailer or back"
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


# housed joints measured from the geometry
def housed(guest, host, probe):
    assert vol(probe & guest) > probe.volume * 0.999, "probe not inside guest"
    assert vol(probe & host) < 1e-6, "host not relieved for the guest"


housed(part("bottom"), part("end"), _box(BOT_X0 + 0.5, CASE_D / 2, BOT_Z0 + 0.5, RABBET_D - 1, 10, T18 - 1))
housed(part("partition"), part("bottom"), _box(PART_X0 + 0.5, CASE_D / 2, PART_Z0 + 0.5, T18 - 1, 10, DADO_D - 1))
housed(part("back"), part("end"), _box(BOT_X0 + PLAY / 2 + 0.2, BACK_Y0 + 0.5, (BOT_Z1 + TOP_Z0) / 2, 4, T6 - 1, 10))
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
if BASE == "legs":
    assert abs(part("leg").volume - LEG_SQ * LEG_SQ * CLEAR) < 1e-3

assembly = Compound(children=[s for _, s in INST] + [s for _, s in HW])

# ================================================================ outputs
TMP = os.environ.get("TMP_STL")
if TMP:
    SUBSETS = {   # SUBSET=case|base|fronts|drawers|nocushion|drawer1 picks instances by name prefix for the renders
        "case": ("end_", "bottom", "partition", "nailer", "back"),
        "base": ("leg_", "brail_", "blade_"),
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
    BASE_LINES = {
        "legs": [{"part": "Pocket screws #8 x 1-1/4 fine", "qty": 20, "unit": "ea", "material": "hardware",
                  "notes": "base rails into the legs (2 per joint, 12) and up into the case bottom (10)"},
                 {"part": "Wood screws #8 x 2", "qty": 8, "unit": "ea", "material": "hardware",
                  "notes": "down through the case bottom into the leg tops, two per leg, under the drawer boxes"}],
        "blades": [{"part": "Pocket screws #8 x 1-1/4 fine", "qty": 8, "unit": "ea", "material": "hardware",
                    "notes": "back rail into the blades (4) and up into the case bottom (4)"},
                   {"part": "Wood screws #8 x 2", "qty": 8, "unit": "ea", "material": "hardware",
                    "notes": "down through the case bottom into the blades' top edges, four per blade"}],
        "gables": [{"part": "Pocket screws #8 x 1-1/4 fine", "qty": 8, "unit": "ea", "material": "hardware",
                    "notes": "stretcher into the gables (4) and up into the case bottom (4)"}],
    }
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
        *BASE_LINES[BASE],
        {"part": "Iron-on maple edge banding, 13/16", "qty": 1, "unit": "roll", "material": "hardware",
         "notes": f"the ends' front and bottom edges (about {inch(2 * ((TOP_Z0 - END_Z0) + (CASE_D - CASE_Y0)))} in all), painted with them"},
        {"part": "Bench cushion", "qty": 1, "unit": "ea", "material": "soft goods",
         "notes": f"about {inch(TOP_W - 0.5 * IN)} x {inch(TOP_D)} x {inch(CUSHION_H)}, boxed"},
    ]
    write_cut_list(PARTS, f"{PROJ}/cutlist.md", csv_path=f"{PROJ}/cutlist.csv",
                   title=f"Freestanding bench {inch(TOP_W)} x {inch(TOP_D)} (two drawers, {inch(CLEAR)} clear floor, {BASE})",
                   units="in", denom=32, extra_lines=HARDWARE_LINES)
    export_step(assembly, f"{PROJ}/freestanding_bench.step")
    print("exported cutlist + step")

if os.environ.get("SHOW"):
    from ocp_vscode import show, set_port, Camera
    set_port(3939)
    show(*[s for _, s in INST + HW], names=[n for n, _ in INST + HW],
         reset_camera=(Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP))

print("OK  base:", BASE, " parts:", [p["name"] for p in PARTS])
print(f"top {inch(TOP_W)} x {inch(TOP_D)} at {inch(SEAT_Z)}  case {inch(CASE_W)} x {inch(CASE_D - CASE_Y0)} x {inch(TOP_Z0 - BOT_Z0)}  "
      f"clear floor {inch(CLEAR)}  fronts {inch(FRONT_W)} x {inch(FRONT_H)}  overhang {inch(OVERHANG)}  "
      f"opening {inch(OPEN_W)} x {inch(OPEN_H)}  box {inch(BOX_W)} x {inch(BOX_H)} x {inch(BOX_D)} "
      f"(inside height {inch(BOX_H - UM_RECESS - T12)})")
