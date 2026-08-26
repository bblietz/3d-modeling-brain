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
from build123d import *

IN = 25.4

# --- Provisional inputs (design.md table; MEASURE before cutting) ----------
TOP_W = 36 * IN            # 914.4  the TOP is 36 x 24 (locked convention)
TOP_D = 24 * IN            # 609.6
H = 20 * IN                # 508.0  overall height
TOP_T = 1.75 * IN          # 44.45  Boos island match, measure
OH = 1.25 * IN             # 31.75  top overhang past the posts, measure
T18 = 18.0                 # 3/4 ply actual
T12 = 12.0                 # 1/2 ply actual
SLIDE_LEN = 18 * IN        # 457.2  undermount slide class, see spec sheet

# --- Locked design values --------------------------------------------------
POST = 3 * IN              # 76.2   post square
CHAMFER = 0.375 * IN       # 9.525  post vertical edges, full length
SETBACK = 0.5 * IN         # 12.7   panel outer face behind the post face
GROOVE_D = 0.375 * IN      # 9.525  groove depth in the posts
GROOVE_STOP = 1.5 * IN     # 38.1   panel grooves stop this far above floor
FRAME_SETBACK = 1.0 * IN   # 25.4   front frame front face behind post face
FRONT_SETBACK = 0.25 * IN  # 6.35   drawer fronts behind the post face
FRONT_T = 0.75 * IN        # 19.05  drawer front thickness (solid maple)
RAIL_T = T18               # rails milled to the measured ply thickness so
                           # their stub tenons fill the same grooves
RAIL_TOP_H = 1.0 * IN      # 25.4
RAIL_MID_H = 1.0 * IN      # 25.4
RAIL_BOT_H = 1.5 * IN      # 38.1
RAIL_REAR_H = 1.5 * IN     # 38.1   rear top rail, figure-8 landing
FLOOR_GAP = 0.75 * IN      # 19.05  shadow gap under the bottom front
REV_TOP = 0.125 * IN       # 3.175  under the top
REV_MID = 0.25 * IN        # 6.35   between the fronts
REV_SIDE = 0.125 * IN      # 3.175  front to post
FRONT_TOP_H = 5.75 * IN    # 146.05
FRONT_BOT_H = 11.375 * IN  # 288.925
BOT_GROOVE = 0.25 * IN     # 6.35   bottom-panel groove depth
BOT_TOP_Z = 2.25 * IN      # 57.15  top face of the bottom panel
DADO = 0.25 * IN           # 6.35   drawer-box rabbets and bottom grooves

# --- Undermount slide geometry (Blum Tandem 563H class; VERIFY vs spec) -----
UM_WIDTH_LOSS = 10.0       # box outer width = opening - 10
UM_RECESS = 12.7           # drawer bottom underside above box side bottom edge
UM_INSTALL_CLEAR = 20.0    # free height above each box to tilt it onto slides
UM_REAR_CLEAR = 9.0        # interior depth >= slide length + this
SLIDE_STANDOFF = 8.0       # box bottom edge above its mounting rail (jig value)
BOX_TOP_H = 3.25 * IN      # 82.55  fits the 4-1/2 in opening with clearance
BOX_BOT_H = 8.25 * IN      # 209.55 fits the 9-1/2 in opening with clearance

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


# --- Parts: posts (qty 4: 2 front, 2 rear; right side mirrored) --------------
# Chamfer the four vertical edges first, then cut the two grooves, so the
# groove walls are clean. Side-panel groove: on the face toward the other
# post of that side, SETBACK behind the outer face, stopped at GROOVE_STOP,
# open at the top. Front posts also get the front-frame groove on the inner
# face (FRAME_SETBACK behind the front face, stopped at FLOOR_GAP so the
# bottom rail's tenon is housed); rear posts get the back-panel groove on
# the inner face (SETBACK behind the rear face, stopped at GROOVE_STOP).
def make_post(x, y, front):
    p = _box(x, y, 0, POST, POST, POST_H)
    p = chamfer(p.edges().filter_by(Axis.Z), CHAMFER)
    gh = POST_H - GROOVE_STOP + 1                      # open at the top
    gy = y + POST - GROOVE_D if front else y - 1
    p -= _box(x + SETBACK, gy, GROOVE_STOP, T18, GROOVE_D + 1, gh)
    if front:
        p -= _box(x + POST - GROOVE_D, y + FRAME_SETBACK, FLOOR_GAP,
                  GROOVE_D + 1, T18, POST_H - FLOOR_GAP + 1)
    else:
        p -= _box(x + POST - GROOVE_D, y + POST - SETBACK - T18, GROOVE_STOP,
                  GROOVE_D + 1, T18, gh)
    return p


post_fl = make_post(X0, Y0, True)
post_rl = make_post(X0, YB - POST, False)
post_fr = mirror_x(post_fl)
post_rr = mirror_x(post_rl)
PARTS.append({"name": "post_front", "solid": post_fl, "qty": 2, "material": "soft maple",
              "notes": "glue-up of two 8/4 pieces milled to 1-1/2; 3/8 chamfer x4 edges; "
                       "side groove 3/4 x 3/8 at 1/2 from outer face, stopped 1-1/2 above floor; "
                       "front-frame groove 3/4 x 3/8 at 1 from front face, stopped 3/4 above floor"})
PARTS.append({"name": "post_rear", "solid": post_rl, "qty": 2, "material": "soft maple",
              "notes": "as post_front but back groove 3/4 x 3/8 at 1/2 from rear face on the "
                       "inner face, stopped 1-1/2 above floor; no frame groove"})
INST += [("post_fl", post_fl), ("post_fr", post_fr), ("post_rl", post_rl), ("post_rr", post_rr)]

# Post asserts: envelope, single solid, and volume = box - 4 chamfer prisms -
# grooves (proves the chamfers never reach a groove and grooves are stopped)
_post_box = POST ** 2 * POST_H - 4 * 0.5 * CHAMFER ** 2 * POST_H
_front_vol = (_post_box - T18 * GROOVE_D * (POST_H - GROOVE_STOP)
              - T18 * GROOVE_D * (POST_H - FLOOR_GAP))
_rear_vol = _post_box - 2 * T18 * GROOVE_D * (POST_H - GROOVE_STOP)
assert abs(post_fl.volume - _front_vol) < 1e-3, post_fl.volume
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
BACK_X0 = X0 + POST - GROOVE_D
BACK_Y0 = YB - SETBACK - T18
back = _box(BACK_X0, BACK_Y0, GROOVE_STOP, RAIL_L, T18, BACK_H)
rail_rear = _box(BACK_X0, BACK_Y0, POST_H - RAIL_REAR_H, RAIL_L, RAIL_T, RAIL_REAR_H)

side_r = mirror_x(side_l)
PARTS.append({"name": "side", "solid": side_l, "qty": 2, "material": "ply 18mm",
              "notes": "face grain vertical on the show face; housed 3/8 in each post"})
PARTS.append({"name": "back", "solid": back, "qty": 1, "material": "ply 18mm",
              "notes": "housed 3/8 in each post; top edge under the rear rail"})
PARTS.append({"name": "rail_rear", "solid": rail_rear, "qty": 1, "material": "soft maple",
              "notes": "stub tenons 3/8 each end are the full section; figure-8 fasteners on top"})
INST += [("side_l", side_l), ("side_r", side_r), ("back", back), ("rail_rear", rail_rear)]

# Housed edges probed from the solids
assert_housed(side_l, post_fl, _box(X0 + SETBACK, SIDE_Y0, GROOVE_STOP, T18, GROOVE_D, PANEL_H))
assert_housed(side_l, post_rl, _box(X0 + SETBACK, YB - POST, GROOVE_STOP, T18, GROOVE_D, PANEL_H))
assert_housed(back, post_rl, _box(BACK_X0, BACK_Y0, GROOVE_STOP, GROOVE_D, T18, BACK_H))
assert_housed(rail_rear, post_rl, _box(BACK_X0, BACK_Y0, POST_H - RAIL_REAR_H, GROOVE_D, RAIL_T, RAIL_REAR_H))
assert abs(side_l.bounding_box().min.X - X0 - SETBACK) < 1e-6
assert abs(YB - back.bounding_box().max.Y - SETBACK) < 1e-6
assert abs(side_l.bounding_box().max.Z - POST_H) < 1e-6
assert abs(back.bounding_box().max.Z - rail_rear.bounding_box().min.Z) < 1e-6
assert abs(rail_rear.bounding_box().max.Z - POST_H) < 1e-6

# --- Parts: front frame rails (hidden behind the drawer fronts) ------------
# Front face FRAME_SETBACK behind the post faces; stub tenons GROOVE_D each
# end into the front-post grooves. Top rail under the top, mid rail centered
# on the reveal between the fronts, bottom rail from the floor gap up (its
# top face is the bottom panel's top face).
RAIL_X0 = X0 + POST - GROOVE_D
RAIL_Y0 = Y0 + FRAME_SETBACK
REV_MID_Z0 = FLOOR_GAP + FRONT_BOT_H                  # 307.975 reveal bottom
RAIL_MID_Z0 = REV_MID_Z0 + REV_MID / 2 - RAIL_MID_H / 2   # 298.45
rail_top = _box(RAIL_X0, RAIL_Y0, POST_H - RAIL_TOP_H, RAIL_L, RAIL_T, RAIL_TOP_H)
rail_mid = _box(RAIL_X0, RAIL_Y0, RAIL_MID_Z0, RAIL_L, RAIL_T, RAIL_MID_H)
rail_bot = _box(RAIL_X0, RAIL_Y0, FLOOR_GAP, RAIL_L, RAIL_T, RAIL_BOT_H)

PARTS.append({"name": "rail_top", "solid": rail_top, "qty": 1, "material": "soft maple",
              "notes": "stub tenons 3/8 each end, full section"})
PARTS.append({"name": "rail_mid", "solid": rail_mid, "qty": 1, "material": "soft maple",
              "notes": "stub tenons 3/8 each end, full section; carries the top drawer slides"})
PARTS.append({"name": "rail_bot", "solid": rail_bot, "qty": 1, "material": "soft maple",
              "notes": "stub tenons 3/8 each end, full section"})
INST += [("rail_top", rail_top), ("rail_mid", rail_mid), ("rail_bot", rail_bot)]

for _r, _z, _h in ((rail_top, POST_H - RAIL_TOP_H, RAIL_TOP_H),
                   (rail_mid, RAIL_MID_Z0, RAIL_MID_H),
                   (rail_bot, FLOOR_GAP, RAIL_BOT_H)):
    assert_housed(_r, post_fl, _box(RAIL_X0, RAIL_Y0, _z, GROOVE_D, RAIL_T, _h))
assert abs(rail_bot.bounding_box().max.Z - BOT_TOP_Z) < 1e-6
assert abs(rail_top.bounding_box().max.Z - POST_H) < 1e-6
assert abs(rail_top.bounding_box().min.Y - Y0 - FRAME_SETBACK) < 1e-6
# mid rail is centered on the reveal
assert abs((RAIL_MID_Z0 + RAIL_MID_H / 2) - (REV_MID_Z0 + REV_MID / 2)) < 1e-6

# --- assembly ---------------------------------------------------------------
assembly = (post_fl + post_fr + post_rl + post_rr
            + side_l + side_r + back + rail_rear
            + rail_top + rail_mid + rail_bot)

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
                   title="Drawer Bench 36x24x20 (provisional)")
    export_step(assembly, f"{PROJ}/drawer_bench.step")
    print("exported cutlist + step")

if os.environ.get("SHOW"):
    from ocp_vscode import show, set_port, Camera
    set_port(3939)
    show(*[s for _, s in INST], names=[n for n, _ in INST],
         reset_camera=(Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP))

print("OK  parts:", [p["name"] for p in PARTS])
