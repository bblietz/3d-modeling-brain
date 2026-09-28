"""Drawer bench: maple post-and-panel kitchen bench, two graduated drawers.

3 in soft-maple corner posts, 3/4 ply sides/back housed in post grooves,
hidden maple front frame, 1/2 ply grooved bottom, two continuous maple
drawer fronts on 18 in undermount slides, maple butcherblock top matched
to the Boos island. Coordinates: X = width (0 at the left edge of the
TOP), Y = depth (0 at the front edge of the TOP), Z = height (0 at the
floor). All mm. Every dimension is provisional; see design.md
"Provisional inputs". Nothing is cut from this file until measured.
"""

import os
from math import pi
from build123d import *

IN = 25.4

# --- Provisional inputs (design.md table; MEASURE before cutting) ----------
TOP_W = 40 * IN            # 1016.0  the TOP is 40 x 24 (locked convention; measured, Brian 2026-09-17)
TOP_D = 24 * IN            # 609.6
H = (19 + 5 / 8) * IN      # 498.475  overall height, top surface to floor (measured, Brian 2026-09-17)
TOP_T = 1.75 * IN          # 44.45  Boos island match (measured, Brian 2026-09-27)
OH = 1.25 * IN             # 31.75  top overhang past the posts, measure
T18 = 18.0                 # 3/4 ply actual
T12 = 12.0                 # 1/2 ply actual
T6 = 6.0                   # 1/4 ply actual (drawer-box bottoms only; measure at cut time)
SLIDE_LEN = 18 * IN        # 457.2  drawer length class (Blum 563H4570B); runner = RUNNER_LEN

# --- Locked design values --------------------------------------------------
POST = 3 * IN              # 76.2   post square
CHAMFER = 0.375 * IN       # 9.525  post vertical edges, full length
SETBACK = 0.5 * IN         # 12.7   panel outer face behind the post face
GROOVE_D = 0.375 * IN      # 9.525  groove depth in the posts
# GROOVE_STOP (where the panel grooves and the panels stop above the floor) is
# tied to FLOOR_GAP below
# FRAME_SETBACK (front frame plane) is derived below the slide block: fronts + Blum front gap
FRONT_SETBACK = 0.25 * IN  # 6.35   drawer fronts behind the post face
FRONT_T = 0.75 * IN        # 19.05  drawer front thickness (solid maple)
RAIL_T = T18               # rails milled to the measured ply thickness so
                           # their stub tenons fill the same grooves
RAIL_TOP_H = 1.0 * IN      # 25.4
RAIL_MID_H = 1.0 * IN      # 25.4
RAIL_BOT_H = 1.5 * IN      # 38.1
RAIL_REAR_H = 1.5 * IN     # 38.1   rear top rail, figure-8 landing
FLOOR_GAP = 0.75 * IN      # 19.05  shadow gap under the bottom front
GROOVE_STOP = FLOOR_GAP    # 19.05  side/back bottoms on the drawer-front line (Brian 2026-09-27; was 1-1/2 in)
REV_TOP = 0.125 * IN       # 3.175  under the top
REV_MID = 0.25 * IN        # 6.35   between the fronts
REV_SIDE = 0.125 * IN      # 3.175  front to post
FRONT_TOP_H = 5.625 * IN   # 142.875  front zone re-split ~1:2 for the new height (design.md rule)
FRONT_BOT_H = 11.125 * IN  # 282.575  same ~1.98:1 ratio as the original 5-3/4 / 11-3/8
BOT_GROOVE = 0.25 * IN     # 6.35   bottom-panel groove depth
BOT_TOP_Z = 2.25 * IN      # 57.15  top face of the bottom panel
DADO = 0.25 * IN           # 6.35   drawer-box rabbets and bottom grooves
DOWEL_DIA = 0.375 * IN     # 9.525  front-rail dowel joints (was stub tenons into mortises)
DOWEL_DEPTH = 1.0 * IN     # 25.4   embedment into post and rail, each side

# --- Undermount slide geometry (Blum TANDEM plus BLUMOTION 563H, from the
# 563H/563 installation sheet, 2016 ed.; face-frame application, inset fronts,
# rear mounting brackets 295.3750.02 on the back panel) ----------------------
UM_WIDTH_LOSS = 42.0 - 2 * T12   # 18: inside drawer width = opening - 42, so the
                                 # outside width loses 42 minus two side thicknesses
UM_RECESS = 12.7           # drawer bottom underside above box side bottom edge (13 on the sheet = 1/2 in)
UM_BOTTOM_CLEAR = 14.0     # box side bottom edge above the bottom of the opening (rail top)
UM_TOP_CLEAR = 6.0         # minimum free height above the box; max box height = opening - 20
RUNNER_LEN = 471.0         # 563H4570B runner for the 18 in drawer class (longer than the box)
RUNNER_SETBACK = T12 + FRONT_T - 11.5 + FRONT_SETBACK   # 25.9 runner front behind the post
                                 # face: Blum inset rule (sub-front + front - 11.5) + our reveal
UM_BRACKET_MIN, UM_BRACKET_MAX = 6.0, 48.0   # inside depth = runner + setback + [6..48]
UM_SCREW_Y = (7.0, 34.0)   # runner front screw holes, behind the runner front, into the post
UM_SCREW_Z = (25.0, 37.0)  # and above the bottom of the opening
UM_SCREW_LEN = 16.0        # #6 x 5/8 screws into the post's inner face
UM_FRONT_GAP = 1.5         # between the fronts' back faces and the frame; the runner stop closes the drawer
UM_HOOK_NOTCH_W, UM_HOOK_NOTCH_H = 35.0, 13.0   # rear-hook notches in the back's bottom corners
UM_HOOK_BORE = (6.0, 10.0, 7.0, 24.0)   # dia, depth from the rear face, from the side's inner face, above the back's bottom edge
FRAME_SETBACK = FRONT_SETBACK + FRONT_T + UM_FRONT_GAP   # 26.9 front frame face behind the post face

# --- Derived ---------------------------------------------------------------
FOOT_W = TOP_W - 2 * OH             # 850.9  post outer faces
FOOT_D = TOP_D - 2 * OH             # 546.1
POST_H = H - TOP_T                  # 463.55
OPEN_W = FOOT_W - 2 * POST          # 698.5  between the posts
X0, Y0 = OH, OH                     # front-left post min corner
XR, YB = OH + FOOT_W, OH + FOOT_D   # right post outer face, rear post outer face
PANEL_H = POST_H - GROOVE_STOP      # 425.45 side panels, groove stop to top
BACK_H = PANEL_H - RAIL_REAR_H      # 387.35 back panel, under the rear rail
RAIL_L = OPEN_W + 2 * GROOVE_D      # 717.55 opening + two stub tenons
REV_MID_Z0 = FLOOR_GAP + FRONT_BOT_H                      # 307.975 reveal bottom
RAIL_BOT_Z0 = FLOOR_GAP                                   # 19.05
RAIL_MID_Z0 = REV_MID_Z0 + REV_MID / 2 - RAIL_MID_H / 2   # 298.45 centered on the reveal
RAIL_TOP_Z0 = POST_H - RAIL_TOP_H                         # 438.15
RAIL_ZH = ((RAIL_BOT_Z0, RAIL_BOT_H), (RAIL_MID_Z0, RAIL_MID_H), (RAIL_TOP_Z0, RAIL_TOP_H))
# Blum's maximum box height is each rail-to-rail opening minus the bottom and
# top clearances; computed here (not a locked constant) since it depends on
# the rail positions just derived above, which move with FRONT_BOT_H/FRONT_TOP_H.
BOX_TOP_H = (RAIL_TOP_Z0 - (RAIL_MID_Z0 + RAIL_MID_H)) - (UM_BOTTOM_CLEAR + UM_TOP_CLEAR)
BOX_BOT_H = (RAIL_MID_Z0 - (RAIL_BOT_Z0 + RAIL_BOT_H)) - (UM_BOTTOM_CLEAR + UM_TOP_CLEAR)
BOT_Z0 = BOT_TOP_Z - T12                     # 45.15 bottom panel underside
BOT_X0 = X0 + SETBACK + T18 - BOT_GROOVE     # into the side-panel groove
BOT_W = FOOT_W - 2 * (SETBACK + T18 - BOT_GROOVE)   # 802.2
DOWEL_VOL = pi * (DOWEL_DIA / 2) ** 2 * (DOWEL_DEPTH + 1)   # one dowel bore, post or rail side

PARTS = []   # {"name", "solid", "qty", "material", "notes"}: cut list + assembly
INST = []    # (name, solid) for every PLACED instance: overlap check


def _box(x, y, z, dx, dy, dz):
    """Box with min corner at (x, y, z)."""
    return Pos(x, y, z) * Box(dx, dy, dz, align=(Align.MIN, Align.MIN, Align.MIN))


def vol(shape):
    """Volume of a boolean result; 0 for an empty one."""
    try:
        return 0.0 if shape is None else shape.volume
    except Exception:
        return 0.0


def part(name):
    return next(p for p in PARTS if p["name"] == name)["solid"]


def assert_housed(guest, host, probe):
    """`probe` is the slice of `guest` that must sit inside a groove in `host`:
    the guest fills it, the host is cut away there, and the two never overlap."""
    assert abs(vol(probe & guest) - probe.volume) < 1e-3, "guest does not fill the groove"
    assert vol(probe & host) < 1e-3, "host not cut away in the groove"
    assert vol(guest & host) < 1e-3, "guest overlaps host"


def mirror_x(solid):
    """Left-side part to its right-side twin (bench is symmetric about X)."""
    return mirror(solid, Plane.YZ.offset(TOP_W / 2))


def _dowel(xc, yc, zc):
    """Round dowel-joint bore centered on the joint face at (xc, yc, zc),
    DOWEL_DEPTH deep into material on each side (the far side is usually
    open air once the piece is subtracted; the overshoot is harmless)."""
    length = 2 * (DOWEL_DEPTH + 1)
    return Pos(xc, yc, zc) * Rot(0, 90, 0) * Cylinder(DOWEL_DIA / 2, length)


# --- Parts: posts (qty 4: 2 front, 2 rear; right side mirrored) --------------
# Chamfer the four vertical edges first, then cut the grooves, so the groove
# walls are clean. Side-panel groove: on the face toward the other post of
# that side, SETBACK behind the outer face, stopped at GROOVE_STOP, open at
# the top. Front posts get three round dowel bores on the inner face
# (FRAME_SETBACK behind the front face) at the rail centerlines, so the face
# is solid between the rails, where the slide's front tab screws in and where
# a groove would show with a drawer open; rear posts get the back-panel
# groove on the inner face (SETBACK behind the rear face, stopped at
# GROOVE_STOP).
def make_post(x, y, front):
    p = _box(x, y, 0, POST, POST, POST_H)
    p = chamfer(p.edges().filter_by(Axis.Z), CHAMFER)
    gh = POST_H - GROOVE_STOP + 1                      # open at the top
    gy = y + POST - GROOVE_D if front else y - 1
    p -= _box(x + SETBACK, gy, GROOVE_STOP, T18, GROOVE_D + 1, gh)
    if front:   # three dowel bores for the rail joints, 1 in behind the face
        for _z, _h in RAIL_ZH:
            p -= _dowel(x + POST, y + FRAME_SETBACK + RAIL_T / 2, _z + _h / 2)
    else:
        p -= _box(x + POST - GROOVE_D, y + POST - SETBACK - T18, GROOVE_STOP,
                  GROOVE_D + 1, T18, gh)
    return p


post_fl = make_post(X0, Y0, True)
post_rl = make_post(X0, YB - POST, False)
post_fr = mirror_x(post_fl)
post_rr = mirror_x(post_rl)
PARTS.append({"name": "post_front", "solid": post_fl, "qty": 2, "material": "soft maple",
              "notes": "one of 2 FRONT posts, left/right mirrored, grooves on the inner faces; "
                       "glue-up of two 8/4 pieces milled to 1-1/2; "
                       "3/8 chamfer x4 edges full length; "
                       "side groove T18 (measured ply) x 3/8 at 1/2 from the outer face, "
                       f"stopped {GROOVE_STOP / IN:g} above the floor, open at top"
                       "; grain vertical, glue-up seam on a side face; "
                       f"three {DOWEL_DIA:g} dia x {DOWEL_DEPTH:g} deep dowel bores on the inner "
                       "face 1 in behind the front face, centered on the rail joints at Z "
                       f"{RAIL_BOT_Z0 + RAIL_BOT_H / 2:.2f}, "
                       f"{RAIL_MID_Z0 + RAIL_MID_H / 2:.2f}, "
                       f"{RAIL_TOP_Z0 + RAIL_TOP_H / 2:.2f}"})
PARTS.append({"name": "post_rear", "solid": post_rl, "qty": 2, "material": "soft maple",
              "notes": "one of 2 REAR posts, left/right mirrored, grooves on the inner faces; "
                       "same blank and chamfer as post_front; side groove as post_front; "
                       "back groove T18 x 3/8 on the inner face at 1/2 from the rear face, "
                       f"stopped {GROOVE_STOP / IN:g} above the floor, open at top; no mortises"
                       "; grain vertical"})
INST += [("post_fl", post_fl), ("post_fr", post_fr), ("post_rl", post_rl), ("post_rr", post_rr)]

# Post asserts: envelope, single solid, and volume = box - 4 chamfer prisms -
# grooves (proves the chamfers never reach a groove and grooves are stopped)
_post_box = POST ** 2 * POST_H - 4 * 0.5 * CHAMFER ** 2 * POST_H
_front_vol = (_post_box - T18 * GROOVE_D * (POST_H - GROOVE_STOP)
              - 3 * DOWEL_VOL)
_rear_vol = _post_box - 2 * T18 * GROOVE_D * (POST_H - GROOVE_STOP)
assert abs(post_fl.volume - _front_vol) < 1e-2, post_fl.volume
assert abs(post_rl.volume - _rear_vol) < 1e-3, post_rl.volume
assert CHAMFER < SETBACK and CHAMFER < FRAME_SETBACK
for _p in (post_fl, post_fr, post_rl, post_rr):
    _bb = _p.bounding_box()
    assert abs(_bb.size.Z - POST_H) < 1e-6 and abs(_bb.size.X - POST) < 1e-6
assert abs(post_fr.bounding_box().max.X - XR) < 1e-6
assert abs(post_rl.bounding_box().max.Y - YB) < 1e-6

# --- Parts: side panels (qty 2), back panel, rear top rail -----------------
# Sides: outer face SETBACK behind the post face, housed GROOVE_D in each
# post, bottom edge on the groove stop, top edge flush with the post tops.
# Back: same, but stops under the rear top rail, which is tenoned into the
# same groove line and takes the figure-8 fasteners for the top.
SIDE_Y0 = Y0 + POST - GROOVE_D
SIDE_L = FOOT_D - 2 * POST + 2 * GROOVE_D            # 412.75
side_l = _box(X0 + SETBACK, SIDE_Y0, GROOVE_STOP, T18, SIDE_L, PANEL_H)
# Bottom-panel groove run THROUGH, full length (Brian, 2026-09-27; was stopped
# at the posts): its ends sit inside the post grooves, above their stop.
side_l -= _box(BOT_X0, SIDE_Y0 - 1, BOT_Z0, BOT_GROOVE + 1, SIDE_L + 2, T12)
BACK_X0 = X0 + POST - GROOVE_D
BACK_Y0 = YB - SETBACK - T18
back = _box(BACK_X0, BACK_Y0, GROOVE_STOP, RAIL_L, T18, BACK_H)
back -= _box(BACK_X0 - 1, BACK_Y0 - 1, BOT_Z0, RAIL_L + 2, BOT_GROOVE + 1, T12)
rail_rear = _box(BACK_X0, BACK_Y0, POST_H - RAIL_REAR_H, RAIL_L, RAIL_T, RAIL_REAR_H)

side_r = mirror_x(side_l)
_BOT_GROOVE_NOTE = (f"through groove {BOT_GROOVE:g} deep x {T12:g} (T12) on the inner face for the bottom, "
                    f"full length, lower wall {BOT_Z0 - GROOVE_STOP:.2f} above the bottom edge")
PARTS.append({"name": "side", "solid": side_l, "qty": 2, "material": "ply 18mm",
              "notes": "face grain vertical on the show face; housed 3/8 in each post"
                       "; " + _BOT_GROOVE_NOTE})
PARTS.append({"name": "back", "solid": back, "qty": 1, "material": "ply 18mm",
              "notes": "housed 3/8 in each post; top edge under the rear rail"
                       "; " + _BOT_GROOVE_NOTE})
PARTS.append({"name": "rail_rear", "solid": rail_rear, "qty": 1, "material": "soft maple",
              "notes": "REAR top rail, thickness = measured ply (T18): stub tenons 3/8 each end, "
                       "full section; figure-8 fasteners on top"})
INST += [("side_l", side_l), ("side_r", side_r), ("back", back), ("rail_rear", rail_rear)]

# Housed edges probed from the solids. The panel probes leave out the through
# groove for the bottom, which runs out of the panel ends inside the posts.
def _side_probe(y):
    p = _box(X0 + SETBACK, y, GROOVE_STOP, T18, GROOVE_D, PANEL_H)
    return p - _box(BOT_X0, y - 1, BOT_Z0, BOT_GROOVE + 1, GROOVE_D + 2, T12)


def _back_probe(x):
    p = _box(x, BACK_Y0, GROOVE_STOP, GROOVE_D, T18, BACK_H)
    return p - _box(x - 1, BACK_Y0 - 1, BOT_Z0, GROOVE_D + 2, BOT_GROOVE + 1, T12)


assert_housed(side_l, post_fl, _side_probe(SIDE_Y0))
assert_housed(side_l, post_rl, _side_probe(YB - POST))
assert_housed(back, post_rl, _back_probe(BACK_X0))
assert_housed(rail_rear, post_rl, _box(BACK_X0, BACK_Y0, POST_H - RAIL_REAR_H, GROOVE_D, RAIL_T, RAIL_REAR_H))
assert_housed(back, post_rr, _back_probe(XR - POST))
assert_housed(rail_rear, post_rr, _box(XR - POST, BACK_Y0, POST_H - RAIL_REAR_H, GROOVE_D, RAIL_T, RAIL_REAR_H))
# The bottom grooves run the full panel length (volume identity)
assert abs(side_l.volume - (T18 * SIDE_L * PANEL_H - BOT_GROOVE * T12 * SIDE_L)) < 1e-3, side_l.volume
assert abs(back.volume - (T18 * RAIL_L * BACK_H - BOT_GROOVE * T12 * RAIL_L)) < 1e-3, back.volume
assert abs(side_l.bounding_box().min.X - X0 - SETBACK) < 1e-6
assert abs(YB - back.bounding_box().max.Y - SETBACK) < 1e-6
assert abs(side_l.bounding_box().max.Z - POST_H) < 1e-6
assert abs(back.bounding_box().max.Z - rail_rear.bounding_box().min.Z) < 1e-6
assert abs(rail_rear.bounding_box().max.Z - POST_H) < 1e-6

# --- Parts: front frame rails (hidden behind the drawer fronts) ------------
# Front face FRAME_SETBACK behind the post faces; dowel joints, not tenons
# (Brian, 2026-09-18: was stub-tenoned into post mortises) - rails butt flush
# against the post inner faces, length = opening exactly. Top rail under the
# top, mid rail centered on the reveal between the fronts, bottom rail from
# the floor gap up (its top face is the bottom panel's top face). The bottom
# rail's rear-top edge is rabbeted for the bottom panel, full length (no
# tenon to run through any more).
RAIL_X0 = X0 + POST                  # front post's inner face; dowel butt joint
RAIL_Y0 = Y0 + FRAME_SETBACK
FRAME_RAIL_L = OPEN_W                # 698.5  opening only (was + 2 * GROOVE_D for the old tenons)


def make_front_rail(z0, h):
    """Front rail: butts flush into the post faces, one dowel each end."""
    r = _box(RAIL_X0, RAIL_Y0, z0, FRAME_RAIL_L, RAIL_T, h)
    yc, zc = RAIL_Y0 + RAIL_T / 2, z0 + h / 2
    r -= _dowel(RAIL_X0, yc, zc)
    r -= _dowel(RAIL_X0 + FRAME_RAIL_L, yc, zc)
    return r


rail_top = make_front_rail(RAIL_TOP_Z0, RAIL_TOP_H)
rail_mid = make_front_rail(RAIL_MID_Z0, RAIL_MID_H)
rail_bot = make_front_rail(RAIL_BOT_Z0, RAIL_BOT_H)
rail_bot -= _box(RAIL_X0 - 1, RAIL_Y0 + RAIL_T - BOT_GROOVE, BOT_Z0, FRAME_RAIL_L + 2, BOT_GROOVE + 1, T12 + 1)

PARTS.append({"name": "rail_top", "solid": rail_top, "qty": 1, "material": "soft maple",
              "notes": f"FRONT top rail, thickness = measured ply (T18): butts flush into the post "
                       f"faces, {DOWEL_DIA:g} dia x {DOWEL_DEPTH:g} deep dowel each end; figure-8 "
                       "fasteners on top"})
PARTS.append({"name": "rail_mid", "solid": rail_mid, "qty": 1, "material": "soft maple",
              "notes": f"FRONT mid rail, thickness = measured ply (T18): butts flush into the post "
                       f"faces, {DOWEL_DIA:g} dia x {DOWEL_DEPTH:g} deep dowel each end; carries the "
                       "top drawer slides"})
PARTS.append({"name": "rail_bot", "solid": rail_bot, "qty": 1, "material": "soft maple",
              "notes": f"FRONT bottom rail, thickness = measured ply (T18): butts flush into the "
                       f"post faces, {DOWEL_DIA:g} dia x {DOWEL_DEPTH:g} deep dowel each end; rabbet "
                       f"{BOT_GROOVE:g} x {T12:g} (T12) on the rear-top edge, full length, for the "
                       "bottom panel; glue and screw the bottom into it (no lip above)"})
INST += [("rail_top", rail_top), ("rail_mid", rail_mid), ("rail_bot", rail_bot)]

# Dowel joints: rails butt flush against the post inner faces (no tenon
# reach); volume identity proves each bore removes exactly one dowel's worth
# of material, landing once each and not clipped by an edge or another bore.
assert abs(rail_top.volume - (FRAME_RAIL_L * RAIL_T * RAIL_TOP_H - 2 * DOWEL_VOL)) < 1e-2, rail_top.volume
assert abs(rail_mid.volume - (FRAME_RAIL_L * RAIL_T * RAIL_MID_H - 2 * DOWEL_VOL)) < 1e-2, rail_mid.volume
assert abs(rail_bot.volume - (FRAME_RAIL_L * RAIL_T * RAIL_BOT_H - 2 * DOWEL_VOL
                               - FRAME_RAIL_L * BOT_GROOVE * T12)) < 1e-2, rail_bot.volume
for _r in (rail_top, rail_mid, rail_bot):
    assert abs(_r.bounding_box().min.X - RAIL_X0) < 1e-6
    assert abs(_r.bounding_box().max.X - (RAIL_X0 + FRAME_RAIL_L)) < 1e-6
assert abs(rail_bot.bounding_box().max.Z - BOT_TOP_Z) < 1e-6
assert abs(rail_top.bounding_box().max.Z - POST_H) < 1e-6
assert abs(rail_top.bounding_box().min.Y - Y0 - FRAME_SETBACK) < 1e-6
# mid rail is centered on the reveal
assert abs((RAIL_MID_Z0 + RAIL_MID_H / 2) - (REV_MID_Z0 + REV_MID / 2)) < 1e-6

# --- Part: bottom (1/2 ply dust panel / slide-bracket landing) ---------------
# Between the posts it spans into the side-panel grooves; ahead of and behind
# the posts it narrows to the opening width and runs into the bottom-rail
# rabbet and the back-panel groove. So: a rectangle with four corner notches
# the size of the post footprint minus the groove reach.
BOT_Y0 = RAIL_Y0 + RAIL_T - BOT_GROOVE       # into the rail rabbet
BOT_Y1 = BACK_Y0 + BOT_GROOVE                # into the back groove
bottom = _box(BOT_X0, Y0 + POST, BOT_Z0, BOT_W, FOOT_D - 2 * POST, T12)
bottom += _box(X0 + POST, BOT_Y0, BOT_Z0, OPEN_W, Y0 + POST - BOT_Y0, T12)
bottom += _box(X0 + POST, YB - POST, BOT_Z0, OPEN_W, BOT_Y1 - (YB - POST), T12)
PARTS.append({"name": "bottom", "solid": bottom, "qty": 1, "material": "ply 12mm",
              "notes": f"notch the four corners {X0 + POST - BOT_X0:.2f} wide x "
                       f"{Y0 + POST - BOT_Y0:.2f} (front) / {BOT_Y1 - (YB - POST):.2f} (rear) "
                       "for the posts; edges in the side/back grooves and the rail_bot rabbet "
                       "(glue and screw the front edge)"})
INST.append(("bottom", bottom))

assert len(bottom.solids()) == 1
assert abs(bottom.bounding_box().max.Z - BOT_TOP_Z) < 1e-6
_bp = _box(BOT_X0, Y0 + POST, BOT_Z0, BOT_GROOVE, FOOT_D - 2 * POST, T12)
assert_housed(bottom, side_l, _bp)
assert_housed(bottom, side_r, mirror_x(_bp))
assert_housed(bottom, back, _box(X0 + POST, BACK_Y0, BOT_Z0, OPEN_W, BOT_GROOVE, T12))
assert_housed(bottom, rail_bot, _box(X0 + POST, BOT_Y0, BOT_Z0, OPEN_W, BOT_GROOVE, T12))

# --- Parts: drawer fronts (continuous soft maple, modeled blank) -------------
# FRONT_SETBACK behind the post faces, REV_SIDE to each post, REV_MID between
# them, FLOOR_GAP below, REV_TOP under the top. Their backs land exactly on
# the frame plane, so the boxes start there.
FRONT_X0 = X0 + POST + REV_SIDE
FRONT_W = OPEN_W - 2 * REV_SIDE                 # 692.15
FRONT_Y0 = Y0 + FRONT_SETBACK
FRONT_TOP_Z0 = REV_MID_Z0 + REV_MID             # 314.325
front_bot = _box(FRONT_X0, FRONT_Y0, FLOOR_GAP, FRONT_W, FRONT_T, FRONT_BOT_H)
front_top = _box(FRONT_X0, FRONT_Y0, FRONT_TOP_Z0, FRONT_W, FRONT_T, FRONT_TOP_H)
PARTS.append({"name": "front_bot", "solid": front_bot, "qty": 1, "material": "soft maple",
              "notes": "grain along the length; screwed to the box from inside through "
                       "slotted holes (cross-grain 11-3/8 wide); pull undecided; "
                       "leave about 1.5 mm between the back face and the rails (Blum front gap)"})
PARTS.append({"name": "front_top", "solid": front_top, "qty": 1, "material": "soft maple",
              "notes": "grain along the length; screwed to the box from inside; pull undecided; "
                       "leave about 1.5 mm between the back face and the rails (Blum front gap), "
                       "the runner setback sets the closed position"})
INST += [("front_bot", front_bot), ("front_top", front_top)]

# Fronts plus reveals exactly fill the front zone
assert abs(FLOOR_GAP + FRONT_BOT_H + REV_MID + FRONT_TOP_H + REV_TOP - POST_H) < 1e-6
_fb, _ft = front_bot.bounding_box(), front_top.bounding_box()
assert abs(_fb.min.Z - FLOOR_GAP) < 1e-6
assert abs(_ft.min.Z - _fb.max.Z - REV_MID) < 1e-6
assert abs(POST_H - _ft.max.Z - REV_TOP) < 1e-6
assert abs(_fb.min.Y - Y0 - FRONT_SETBACK) < 1e-6
assert abs(RAIL_Y0 - _fb.max.Y - UM_FRONT_GAP) < 1e-6        # Blum front gap to the frame
assert abs(_fb.min.X - (X0 + POST) - REV_SIDE) < 1e-6
assert abs((XR - POST) - _fb.max.X - REV_SIDE) < 1e-6
for _a, _b in ((_ft.min.X, _fb.min.X), (_ft.max.X, _fb.max.X), (_ft.min.Y, _fb.min.Y), (_ft.max.Y, _fb.max.Y)):
    assert abs(_a - _b) < 1e-6          # top front aligned over the bottom front

# --- Drawer boxes (1/2 ply, undermount geometry as in cabinet_bench) --------
# Sides run the full box depth; front/back captured in DADO end rabbets in
# the sides; T12 bottom in DADO grooves all round, underside at UM_RECESS.
# Box front face on the frame plane (behind the drawer front).
BOX_W = OPEN_W - UM_WIDTH_LOSS               # 680.5
BOX_D = SLIDE_LEN                            # 457.2, the Blum drawer length for the 18 in class
BOX_X0 = X0 + POST + UM_WIDTH_LOSS / 2
BOX_Y0 = Y0 + FRONT_SETBACK + FRONT_T         # 57.15 box front on the fronts' back faces
END_LEN = BOX_W - 2 * (T12 - DADO)           # 677.2 drawer front/back length


def make_drawer(box_h, z0, sfx):
    """Build one drawer box in place; register parts, return the visual solid."""
    x0, y0 = BOX_X0, BOX_Y0
    y_back = y0 + BOX_D - T12                      # back panel's front face
    s = _box(x0, y0, z0, T12, BOX_D, box_h)
    s -= _box(x0 + T12 - DADO, y0 - 1, z0 - 1, DADO + 1, T12 + 1, box_h + 2)
    s -= _box(x0 + T12 - DADO, y_back, z0 - 1, DADO + 1, T12 + 1, box_h + 2)
    s -= _box(x0 + T12 - DADO, y0 - 1, z0 + UM_RECESS, DADO + 1, BOX_D + 2, T6)

    front = _box(x0 + T12 - DADO, y0, z0, END_LEN, T12, box_h)
    front -= _box(x0 + T12 - DADO - 1, y0 + T12 - DADO, z0 + UM_RECESS,
                  END_LEN + 2, DADO + 1, T6)

    # Back (Blum rear-hook preparation, 563H sheet p.2): bottom groove stopped
    # UM_HOOK_NOTCH_W from each side's inner face so the 10-deep hook bores stay
    # in solid ply; 35 x 13 notches at both bottom corners for the hooks.
    back = _box(x0 + T12 - DADO, y_back, z0, END_LEN, T12, box_h)
    back -= _box(x0 + T12 + UM_HOOK_NOTCH_W, y_back - 1, z0 + UM_RECESS,
                 BOX_W - 2 * T12 - 2 * UM_HOOK_NOTCH_W, DADO + 1, T6)
    for _nx in (x0 + T12 - DADO - 1, x0 + BOX_W - T12 - UM_HOOK_NOTCH_W):
        back -= _box(_nx, y_back - 1, z0 - 1, UM_HOOK_NOTCH_W + DADO + 1, T12 + 2,
                     UM_HOOK_NOTCH_H + 1)

    bot = _box(x0 + T12 - DADO, y0 + T12 - DADO, z0 + UM_RECESS,
               END_LEN, BOX_D - 2 * (T12 - DADO), T6)
    for _nx in (x0 + T12 - DADO - 1, x0 + BOX_W - T12 - UM_HOOK_NOTCH_W):   # rear corners
        bot -= _box(_nx, y_back, z0 + UM_RECESS - 1, UM_HOOK_NOTCH_W + DADO + 1,
                    DADO + 1, T12 + 2)

    # The hook bores (not modeled) must land in solid back, clear of the bottom
    _d, _dep, _in, _up = UM_HOOK_BORE
    for _bx in (x0 + T12 + _in, x0 + BOX_W - T12 - _in):
        _bp = _box(_bx - _d / 2, y_back + T12 - _dep, z0 + _up - _d / 2, _d, _dep, _d)
        assert abs(vol(_bp & back) - _bp.volume) < 1e-3, (sfx, "hook bore breaks out of the back")
        assert vol(_bp & bot) < 1e-3, (sfx, "hook bore hits the drawer bottom")

    PARTS.append({"name": f"drawer_side_{sfx}", "solid": s, "qty": 2, "material": "ply 12mm",
                  "notes": f"end rabbets {DADO:g} deep x {T12:g} (T12); bottom groove {DADO:g} "
                           f"deep x {T6:g} (T6) with its top at {UM_RECESS + T6:g} above the "
                           "bottom edge"})
    PARTS.append({"name": f"drawer_front_{sfx}", "solid": front, "qty": 1, "material": "ply 12mm",
                  "notes": f"box front (sub-front): bottom groove {DADO:g} deep x {T6:g} (T6) with "
                           f"its top at {UM_RECESS + T6:g} above the bottom edge; locking devices "
                           "bored with the Blum T65.1600.01 template"})
    PARTS.append({"name": f"drawer_back_{sfx}", "solid": back, "qty": 1, "material": "ply 12mm",
                  "notes": f"box back, datums from the blank's ends: bottom groove {DADO:g} deep x "
                           f"{T6:g} (T6) with its top at {UM_RECESS + T6:g} above the bottom edge, "
                           f"STOPPED {UM_HOOK_NOTCH_W + DADO:g} from each end (= {UM_HOOK_NOTCH_W:g} from "
                           f"the side's inner face); rear-hook notches {UM_HOOK_NOTCH_W + DADO:g} from "
                           f"each end x {UM_HOOK_NOTCH_H:g} tall at both bottom corners; rear-hook bores "
                           f"{_d:g} dia x {_dep:g} deep from the rear face, centred {_in + DADO:g} from "
                           f"each end (= {_in:g} from the side's inner face) and {_up:g} above the bottom "
                           f"edge (Blum T65.1600.01 template)"})
    PARTS.append({"name": f"drawer_bottom_{sfx}", "solid": bot, "qty": 1, "material": "ply 6mm",
                  "notes": f"rear corners notched {UM_HOOK_NOTCH_W + DADO:g} (from each end) x {DADO:g} "
                           "deep where the back groove is stopped"})

    s_r = mirror_x(s)
    INST.extend([(f"drawer_side_{sfx}_l", s), (f"drawer_side_{sfx}_r", s_r),
                 (f"drawer_front_{sfx}", front), (f"drawer_back_{sfx}", back),
                 (f"drawer_bottom_{sfx}", bot)])
    return s + s_r + front + back + bot


BOX_BOT_Z0 = BOT_TOP_Z + UM_BOTTOM_CLEAR                   # 71.15  above the bottom rail top
BOX_TOP_Z0 = RAIL_MID_Z0 + RAIL_MID_H + UM_BOTTOM_CLEAR    # 337.85 above the mid rail top
drawer_bot = make_drawer(BOX_BOT_H, BOX_BOT_Z0, "bot")
drawer_top = make_drawer(BOX_TOP_H, BOX_TOP_Z0, "top")

# Undermount geometry probed from the solids, not just the constants
for _sfx, _below, _above, _front in (("bot", BOT_TOP_Z, RAIL_MID_Z0, front_bot),
                                     ("top", RAIL_MID_Z0 + RAIL_MID_H, RAIL_TOP_Z0, front_top)):
    _sb = part(f"drawer_side_{_sfx}").bounding_box()
    _bb = part(f"drawer_bottom_{_sfx}").bounding_box()
    _frb = _front.bounding_box()
    assert abs(_bb.min.Z - _sb.min.Z - UM_RECESS) < 1e-6, _sfx
    assert abs(OPEN_W - (TOP_W - 2 * _sb.min.X) - UM_WIDTH_LOSS) < 1e-6, _sfx
    assert abs(_sb.size.Y - SLIDE_LEN) < 1e-6, _sfx
    assert abs(_sb.min.Z - _below - UM_BOTTOM_CLEAR) < 1e-6, _sfx   # Blum bottom clearance
    assert _above - _sb.max.Z >= UM_TOP_CLEAR, (_sfx, _above - _sb.max.Z)
    assert _sb.size.Z <= (_above - _below) - 20.0 + 1e-6, _sfx      # max box = opening - 20
    # the runner's front screws land on solid post (the mortises are elsewhere)
    _sp = _box(X0 + POST - UM_SCREW_LEN, Y0 + RUNNER_SETBACK + UM_SCREW_Y[0] - 2,
               _below + UM_SCREW_Z[0] - 3, UM_SCREW_LEN,
               UM_SCREW_Y[1] - UM_SCREW_Y[0] + 4, UM_SCREW_Z[1] - UM_SCREW_Z[0] + 6)
    assert abs(vol(_sp & post_fl) - _sp.volume) < 1e-3, (_sfx, "runner screws hit a mortise")
    assert abs(vol(mirror_x(_sp) & post_fr) - _sp.volume) < 1e-3, _sfx
    assert _sb.min.Z > _frb.min.Z and _sb.max.Z < _frb.max.Z, _sfx   # hidden behind its front
    assert abs(_sb.min.Y - _frb.max.Y) < 1e-6, _sfx                 # starts at the front's back
    _rabbet_floor_r = TOP_W - _sb.min.X - (T12 - DADO)
    for _nm in ("front", "back", "bottom"):
        assert abs(part(f"drawer_{_nm}_{_sfx}").bounding_box().max.X - _rabbet_floor_r) < 1e-6, (_sfx, _nm)
# Depth: Blum inset rule, inside depth measured from the post face to the back panel
_inside = BACK_Y0 - Y0
assert RUNNER_LEN + RUNNER_SETBACK + UM_BRACKET_MIN <= _inside <= RUNNER_LEN + RUNNER_SETBACK + UM_BRACKET_MAX, _inside
assert RUNNER_LEN > BOX_D   # the runner overhangs the box at the back, into the bracket

# --- Part: top (maple butcherblock matched to the Boos island) --------------
# Provisional thickness and overhang; edge profile copied from the island
# once measured. Figure-8 fasteners into rail_top and rail_rear, no glue.
top = _box(0, 0, POST_H, TOP_W, TOP_D, TOP_T)
PARTS.append({"name": "top", "solid": top, "qty": 1, "material": "maple butcherblock (Boos match)",
              "notes": "provisional 1-3/4 thick, 1-1/4 overhang all round; edge profile to match "
                       "the island; figure-8 fasteners into rail_top and rail_rear, no glue"})
INST.append(("top", top))
assert abs(top.bounding_box().min.X + OH - X0) < 1e-6
assert abs(top.bounding_box().max.Z - H) < 1e-6

# --- assembly ---------------------------------------------------------------
assembly = (post_fl + post_fr + post_rl + post_rr
            + side_l + side_r + back + rail_rear
            + rail_top + rail_mid + rail_bot + bottom
            + front_bot + front_top + drawer_bot + drawer_top + top)
bb = assembly.bounding_box()
assert abs(bb.size.X - TOP_W) < 1e-6, bb.size
assert abs(bb.size.Y - TOP_D) < 1e-6, bb.size
assert abs(bb.size.Z - H) < 1e-6, bb.size
assert abs(bb.min.Z) < 1e-6
assert len(INST) == 25, len(INST)

# --- global checks ----------------------------------------------------------
for p in PARTS:
    assert len(p["solid"].solids()) == 1, p["name"]
for i, (na, a) in enumerate(INST):
    for nb, b in INST[i + 1:]:
        assert vol(a & b) < 1e-3, f"overlap {na} x {nb}"

# --- exports ----------------------------------------------------------------
TMP = os.environ.get("TMP_STL")
if TMP:
    export_stl(assembly, TMP)

if os.environ.get("EXPORT"):
    import sys
    sys.path.insert(0, "/home/brian/ClaudeProjects/3d-modeling-brain/scripts")
    from cutlist import write_cut_list

    PROJ = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Drawer-bench"
    write_cut_list(PARTS, f"{PROJ}/cutlist.md", csv_path=f"{PROJ}/cutlist.csv",
                   title="Drawer Bench 40x24x19-5/8 (provisional)")
    export_step(assembly, f"{PROJ}/drawer_bench.step")
    print("exported cutlist + step")

if os.environ.get("SHOW"):
    from ocp_vscode import show, set_port, Camera
    set_port(3939)
    show(*[s for _, s in INST], names=[n for n, _ in INST],
         reset_camera=(Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP))

print("OK  parts:", [p["name"] for p in PARTS])
