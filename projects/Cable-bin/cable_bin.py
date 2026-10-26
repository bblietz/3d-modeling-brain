"""Stackable cable bin, 16.75 x 4 x 4 in, split into two halves for the X2D.

Half A carries two vertical dovetail tails at the joint, half B the matching
sockets (closed at the bottom by B's floor, open at the top). A drops onto B.
Crush ribs on the top RIB_LEN of each tail give the friction hold
(knowledge/friction-fits-x2d.md); the dovetails take pull-apart and shear.

Stacking: the bottom FLARE mm of every bin is a 45 degree chamfer; it seats on
the matching 45 degree chamfer of the lip at the top of the bin below, dropping
DROP mm in. No overhang anywhere past 45 degrees.

Lightening (Brian 2026-10-25, drawer bin): vertical rounded slots through both
long walls, a finger scallop in each end wall, and 8 mm joint posts.

Run:  .venv/bin/python projects/Cable-bin/cable_bin.py   (SHOW=1 pushes to the viewer)
Writes STLs and renders beside this file; asserts self-check every run.
"""
import math
import os

from build123d import (Align, Axis, Box, Cylinder, Plane, Polygon, Pos, RectangleRounded, Rot,
                       chamfer, export_stl, extrude, fillet, offset)

HERE = os.path.dirname(os.path.abspath(__file__))
IN = 25.4

# ---- overall (Brian 2026-10-25) --------------------------------------------
L = 16.75 * IN          # 425.45 overall length
W = 4.0 * IN            # 101.6 overall width
H = 4.0 * IN            # 101.6 overall height, foot bottom to rim top
HALF_L = L / 2          # 212.725 per half, fits the 256 mm bed

# ---- shell -----------------------------------------------------------------
WALL = 1.24             # 2 perimeters of the 0.6 nozzle, the printer minimum; floor is the same. Drawer bin, light duty (Brian 2026-10-25)
R_CORNER = 10.0         # outer vertical corner radius at the closed ends (must exceed FLARE)
FLARE = 8.0             # 45 degree foot chamfer height = horizontal inset

# ---- top lip (stiffening band, also the stacking seat) ---------------------
LIP_T = 4.0             # total wall thickness over the top band
LIP_H = 6.0             # height of the full-thickness band
LIP_C = LIP_T - WALL    # 45 degree transition under the band
LIP_EDGE = 1.0          # 45 degree chamfer on the inner top edge = the seat
# foot half-width at height z above its bottom is W/2 - FLARE + z; the lip chamfer's
# top corner sits at half-width W/2 - LIP_T + LIP_EDGE, so the bin drops in by:
DROP = FLARE - LIP_T + LIP_EDGE
STACK_PITCH = H - DROP

# ---- joint -----------------------------------------------------------------
POST_L = 8.0            # post length along the bin (behind the joint face); 12 until 2026-10-25, weight
POST_D = 15.5           # post depth into the bin from the wall's inner face
POST_TOP_GAP = 7.0      # posts stop this far below the rim: the foot above needs DROP + 2
SOCKET_Z = 12.0         # bottom of the tail TIP; the underside slopes down to the joint face
TAIL_UNDER_DEG = 50.0   # underside slope, past 45 for margin: the tail prints over air without support
DT_NECK = 5.0           # dovetail neck width at the joint face
DT_HEAD = 9.0           # dovetail head width
DT_DEPTH = 5.0          # dovetail length past the joint face
DT_CLR = 0.25           # body clearance per side over the 88 mm slide; the ribs own the fit (0.15 until the first coupon)
RIB_R = 1.0             # half-embedded cylinder rib
RIB_CRUSH = 0.10        # designed rib interference per side (0.20 was too tight: Brian's first coupon, 2026-10-25)
RIB_PROUD = DT_CLR + RIB_CRUSH   # rib crest above the tail flank
RIB_LEN = 6.0           # ribs only on the top RIB_LEN of the tail: short crush stroke (12 until Brian's ladder pick, 2026-10-25)
RIB_LEADIN = 0.5
# The fit above is pair 4 of the printed ladder (2026-10-25: body 0.25 throughout, crush 0.15 / 0.10 / 0.05 at 12 mm ribs
# and 0.10 at 6 mm; the first coupon at 0.15 / 0.20 was too tight). Coupons removed once the design was final; see
# knowledge/learnings/cable-bin.md for the ladder.

# ---- lightening: wall slots and end scallops (Brian 2026-10-25) ------------
SLOT_W = 6.0            # slot width
SLOT_PITCH = 14.0       # 8 mm web between slots
SLOT_Z0 = 18.0          # slot bottom, clear of the inner foot chamfer
SLOT_Z1 = 82.0          # slot top, clear of the lip's transition
SLOT_X_MARGIN = 10.0    # web between the first slot and the post, and the last slot and the end corner
SCOOP_R = 28.0          # finger scallop: a circle this big, centred SCOOP_RISE above the rim, in each end wall
SCOOP_RISE = 10.0
SCOOP_W = 2 * math.sqrt(SCOOP_R**2 - SCOOP_RISE**2)   # 52.3 wide at the rim
SCOOP_DEPTH = SCOOP_R - SCOOP_RISE                    # 18 deep

INNER_FLARE_TOP = FLARE + WALL * (math.sqrt(2) - 1)   # where the shell's inner foot chamfer meets the inner wall
assert POST_L - DT_DEPTH - DT_CLR >= 2.5, "not enough post behind the socket head"
assert SLOT_PITCH - SLOT_W >= 8.0, "slot webs under 8 mm"
assert SLOT_Z0 >= INNER_FLARE_TOP + 8.0, "slots run into the foot"
assert SLOT_Z1 <= H - LIP_H - (LIP_T - WALL) - 8.0, "slots run into the lip"
assert SCOOP_W < W - 2 * R_CORNER - 10, "scallop runs into the end corners"
assert POST_TOP_GAP >= DROP + 2.0, "posts would hit the foot of the bin stacked above"
assert R_CORNER > FLARE, "the foot chamfer must fit inside the corner radius"
assert TAIL_UNDER_DEG > 45 + 2, "tail underside must be steeper than 45 degrees to print unsupported"

POST_TOP = H - POST_TOP_GAP
WEDGE_DROP = DT_DEPTH * math.tan(math.radians(TAIL_UNDER_DEG))
TAIL_BOTTOM = SOCKET_Z - WEDGE_DROP            # underside height at the joint face (x = 0)
TAIL_H = POST_TOP - TAIL_BOTTOM
Y_WALL_IN = W / 2 - WALL                      # wall inner face
Y_POST_IN = Y_WALL_IN - POST_D                # post inner face
Y_LIP_IN = W / 2 - LIP_T                      # lip inner face: the tail must pass it on the way in
LIP_GAP = 0.25                                # socket stays this far inboard of the lip
_SLOPE = (DT_HEAD - DT_NECK) / 2 / DT_DEPTH
SOCKET_HALF_HEAD = DT_NECK / 2 + _SLOPE * (DT_DEPTH + DT_CLR) + DT_CLR * math.sqrt(1 + _SLOPE**2)
DT_YC = Y_LIP_IN - LIP_GAP - SOCKET_HALF_HEAD   # dovetail centreline


def plan_outline():
    return RectangleRounded(L, W, R_CORNER)


def outer_body():
    body = Box(L, W, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = fillet(body.edges().filter_by(Axis.Z), R_CORNER)
    body = chamfer(body.edges().group_by(Axis.Z)[0], FLARE)
    return body


def full_bin():
    """Whole 16.75 in bin, before the joint cut: uniform shell plus the lip."""
    outer = outer_body()
    top = outer.faces().sort_by(Axis.Z)[-1]
    shell = offset(outer, -WALL, openings=top)

    inner_plan = offset(plan_outline(), -(WALL - 0.5))     # overlaps the wall by 0.5
    lip_plan = offset(plan_outline(), -LIP_T)
    ring = inner_plan - lip_plan
    lip = extrude(ring, LIP_H + LIP_C)
    lip = Pos(0, 0, H - LIP_H - LIP_C) * lip

    grown = offset(lip_plan, 0.5)              # inner-loop edge centres lie on lip_plan's boundary

    def inner_loop(edges):
        c = [e for e in edges if grown.is_inside((e.center().X, e.center().Y, 0))]
        assert len(c) == 8, f"lip inner loop: expected 8 edges, got {len(c)}"
        return c

    lip = chamfer(inner_loop(lip.edges().group_by(Axis.Z)[0]), LIP_C)
    lip = chamfer(inner_loop(lip.edges().group_by(Axis.Z)[-1]), LIP_EDGE)
    return shell + lip, outer


def slot_cutter():
    """Vertical rounded slots through both long walls of both halves, one solid; also the slot count per wall."""
    x_lo, x_hi = POST_L + SLOT_X_MARGIN, HALF_L - R_CORNER - SLOT_X_MARGIN
    n = int((x_hi - x_lo - SLOT_W) // SLOT_PITCH) + 1
    x0 = x_lo + (x_hi - x_lo - ((n - 1) * SLOT_PITCH + SLOT_W)) / 2 + SLOT_W / 2   # group centred in the zone
    straight = SLOT_Z1 - SLOT_Z0 - SLOT_W
    cap = Rot(90, 0, 0) * Cylinder(SLOT_W / 2, W + 2)                  # axis along Y, through both walls
    one = Box(SLOT_W, W + 2, straight) + Pos(0, 0, straight / 2) * cap + Pos(0, 0, -straight / 2) * cap
    cutter = None
    for i in range(n):
        for sx in (+1, -1):
            s = Pos(sx * (x0 + i * SLOT_PITCH), 0, (SLOT_Z0 + SLOT_Z1) / 2) * one
            cutter = s if cutter is None else cutter + s
    return cutter, n


def scallops():
    """Finger scallop in each end wall: a cylinder along X, centred SCOOP_RISE above the rim."""
    scoop = Rot(0, 90, 0) * Cylinder(SCOOP_R, 40)
    return Pos(-L / 2, 0, H + SCOOP_RISE) * scoop + Pos(L / 2, 0, H + SCOOP_RISE) * scoop


def post(side, x0, x1, outer):
    """Solid post inside the wall at y side (+1/-1), clipped to the bin envelope."""
    y_out = Y_WALL_IN + 0.5
    p = Box(x1 - x0, y_out - Y_POST_IN, POST_TOP - 0.5,
            align=(Align.MIN, Align.MIN, Align.MIN))
    p = Pos(x0, Y_POST_IN, 0.5) * p
    if side < 0:
        p = p.mirror(Plane.XZ)
    return p & outer


def tail_profile(clr):
    """Dovetail in plan, neck at x=0, head at x=DT_DEPTH, offset outward by clr."""
    slope = (DT_HEAD - DT_NECK) / 2 / DT_DEPTH
    n = clr * math.sqrt(1 + slope * slope)        # perpendicular offset of the flanks
    x0, x1 = -1.0, DT_DEPTH + clr
    y0 = DT_NECK / 2 + slope * x0 + n
    y1 = DT_NECK / 2 + slope * x1 + n
    return Polygon((x0, -y0), (x1, -y1), (x1, y1), (x0, y0), align=None)


def rib_centres(proud=RIB_PROUD):
    """(x, y) of the rib axes on the +y flank and -y flank of a tail centred on y=0."""
    slope = (DT_HEAD - DT_NECK) / 2 / DT_DEPTH
    xm = DT_DEPTH / 2
    ym = DT_NECK / 2 + slope * xm
    nrm = math.hypot(slope, 1)
    nx, ny = -slope / nrm, 1 / nrm             # outward normal of the +y flank
    d = RIB_R - proud                           # axis sits this far inside the flank
    return [(xm - d * nx, ym - d * ny), (xm - d * nx, -(ym - d * ny))]


def under_wedge():
    """Everything below the tails' sloped underside, in joint-local coordinates: the plane
    rises from TAIL_BOTTOM at the joint face to SOCKET_Z at the tail tip."""
    t = math.tan(math.radians(TAIL_UNDER_DEG))
    x0, x1 = -2.0, DT_DEPTH + 2.0
    poly = Polygon((x0, -1.0), (x1, -1.0), (x1, TAIL_BOTTOM + x1 * t), (x0, TAIL_BOTTOM + x0 * t), align=None)
    return extrude(Plane.XZ * poly, 15, both=True)


def dovetail_prism(clr, top):
    """Dovetail profile (offset by clr) from the sloped underside up to z = top, centred on y = 0."""
    p = Pos(0, 0, TAIL_BOTTOM) * extrude(tail_profile(clr), top - TAIL_BOTTOM)
    return p - under_wedge()


def tail(side, with_ribs=True, proud=RIB_PROUD, rib_len=RIB_LEN):
    t = dovetail_prism(0.0, POST_TOP)
    if with_ribs:
        for (rx, ry) in rib_centres(proud):
            rib = Cylinder(RIB_R, rib_len, align=(Align.CENTER, Align.CENTER, Align.MIN))
            rib = chamfer(rib.edges().group_by(Axis.Z)[0], RIB_LEADIN)
            t = t + Pos(rx, ry, POST_TOP - rib_len) * rib
    t = Pos(0, DT_YC, 0) * t
    if side < 0:
        t = t.mirror(Plane.XZ)
    return t


def socket(side, clr=DT_CLR):
    """Socket in B: the tail's clearance envelope, open at the top, floored by the same slope."""
    s = Pos(0, DT_YC, 0) * dovetail_prism(clr, H + 1)
    if side < 0:
        s = s.mirror(Plane.XZ)
    return s


def halves(with_ribs=True, clr=DT_CLR, proud=RIB_PROUD, rib_len=RIB_LEN):
    """The two halves; the fit parameters default to the bin's own."""
    whole, outer = full_bin()
    whole = whole - slot_cutter()[0] - scallops()
    cut_a = Pos(0, 0, -1) * Box(L + 2, W + 2, H + 3, align=(Align.MAX, Align.CENTER, Align.MIN))
    cut_b = Pos(0, 0, -1) * Box(L + 2, W + 2, H + 3, align=(Align.MIN, Align.CENTER, Align.MIN))
    half_a = whole & cut_a
    half_b = whole & cut_b
    for side in (+1, -1):
        half_a = half_a + post(side, -POST_L, 0, outer) + tail(side, with_ribs, proud, rib_len)
        half_b = half_b + post(side, 0, POST_L, outer)
    for side in (+1, -1):
        half_b = half_b - socket(side, clr)
    return half_a, half_b, whole, outer


def vol(shape):
    """Volume of a boolean result; an empty intersection comes back as None."""
    return 0.0 if shape is None else shape.volume


def one_solid(shape, name):
    solids = shape.solids()
    assert len(solids) == 1, f"{name}: expected one solid, got {len(solids)}"
    return solids[0]


def main():
    half_a, half_b, whole, outer = halves()
    half_a = one_solid(half_a, "half A")
    half_b = one_solid(half_b, "half B")

    # ---- checks on the halves ------------------------------------------
    bb_a, bb_b = half_a.bounding_box(), half_b.bounding_box()
    assert abs(bb_a.min.X + HALF_L) < 0.01 and abs(bb_a.max.X - DT_DEPTH) < 0.01, bb_a
    assert abs(bb_b.min.X) < 0.01 and abs(bb_b.max.X - HALF_L) < 0.01, bb_b
    for bb in (bb_a, bb_b):
        assert abs(bb.max.Y - W / 2) < 0.01 and abs(bb.min.Y + W / 2) < 0.01, bb
        assert abs(bb.min.Z) < 0.01 and abs(bb.max.Z - H) < 0.01, bb
    assert bb_b.size.X <= 256 and bb_b.size.Y <= 256 and bb_b.size.Z <= 260

    # the halves' bodies clear each other; only the ribs interfere, by the designed amount
    half_a_plain, _, _, _ = halves(with_ribs=False)
    half_a_plain = one_solid(half_a_plain, "half A (no ribs)")
    body_overlap = vol(half_a_plain & half_b)
    assert body_overlap < 1e-3, f"tail/socket bodies interfere: {body_overlap:.4f} mm3"
    def rib_overlap_expected(h, rib_len):
        seg = RIB_R**2 * math.acos((RIB_R - h) / RIB_R) - (RIB_R - h) * math.sqrt(2 * RIB_R * h - h * h)
        return 4 * seg * (rib_len - RIB_LEADIN), 4 * seg * RIB_LEADIN   # lead-in chamfer shortens the full-depth crush
    overlap = vol(half_a & half_b)
    expected, slack = rib_overlap_expected(RIB_CRUSH, RIB_LEN)
    assert 0.9 * expected < overlap < 1.1 * expected + slack, (overlap, expected)

    # tail seats on B's floor: lowering A by 0.05 must collide with B's socket floor
    a_low = Pos(0, 0, -0.05) * half_a_plain
    assert vol(a_low & half_b) > 0.5, "tail does not rest on the socket floor"

    # the tail's whole insertion path (straight down from above the rim) is free of B,
    # including B's lip, and B's lip is intact at the joint
    for side in (+1, -1):
        path = Pos(0, DT_YC, 0) * dovetail_prism(0.0, H + 40)   # the tail swept straight up
        if side < 0:
            path = path.mirror(Plane.XZ)
        assert vol(path & half_b) < 1e-3, f"tail path blocked on side {side}"
    lip_probe = Pos(0, Y_LIP_IN, H - LIP_H) * Box(6, LIP_T - WALL, LIP_H, align=(Align.MIN, Align.MIN, Align.MIN))
    skin = (W / 2 - FLARE + TAIL_BOTTOM) - (DT_YC + SOCKET_HALF_HEAD)   # flare skin outside the socket's bottom corner
    assert skin >= WALL, f"socket breaks through the foot flare: {skin:.2f} mm of skin"
    lip_expect = 6 * ((LIP_T - WALL) * LIP_H - LIP_EDGE**2 / 2)   # band minus its top edge chamfer
    lip_got = vol(lip_probe & half_b)
    assert lip_got > 0.98 * lip_expect, f"B's lip is notched at the joint: {lip_got:.1f} of {lip_expect:.1f} mm3"

    # ---- lightening cuts -----------------------------------------------
    plain_whole, _ = full_bin()
    cutter, n_slots = slot_cutter()
    slot_area = SLOT_W * (SLOT_Z1 - SLOT_Z0 - SLOT_W) + math.pi * (SLOT_W / 2)**2
    slots_removed = vol(plain_whole & cutter)
    slots_expect = 4 * n_slots * slot_area * WALL          # two halves, two walls, flat wall there
    assert abs(slots_removed - slots_expect) < 0.01 * slots_expect, (slots_removed, slots_expect)
    assert vol(cutter & (half_a + half_b)) < 1e-3, "a slot cuts a post or the slot cut did not take"
    scoop_removed = vol(plain_whole & scallops())
    assert scoop_removed > 0, "scallops missed the end walls"
    for hx, half in ((-1, half_a), (+1, half_b)):      # each end wall's rim is gone over the scoop width, no more
        rim = Pos(hx * (HALF_L - 1.0), 0, H - 0.5) * Box(2.0, W, 1.0)
        kept, full = vol(rim & half), vol(rim & plain_whole)
        assert abs(kept - (full - 2.0 * 1.0 * SCOOP_W)) < 0.02 * full, (kept, full)

    # ---- stacking ------------------------------------------------------
    bin_lower = half_a + half_b
    bin_upper = Pos(0, 0, STACK_PITCH) * bin_lower
    stack_overlap = vol(bin_upper & bin_lower)
    assert stack_overlap < 1e-3, f"stacked bins interfere: {stack_overlap:.4f} mm3"
    bin_pressed = Pos(0, 0, STACK_PITCH - 0.05) * bin_lower
    assert vol(bin_pressed & bin_lower) > 1.0, "upper bin does not seat on the lip"
    # the upper bin's foot sits inside the lower lip with the 45 degree faces touching
    bb_whole = bin_lower.bounding_box()
    assert abs(bb_whole.size.X - L) < 0.01 and abs(bb_whole.size.Y - W) < 0.01 and abs(bb_whole.size.Z - H) < 0.01

    parts = {"cable-bin-half-a": half_a, "cable-bin-half-b": half_b}
    import trimesh
    if os.environ.get("NO_EXPORT"):
        parts = {}
    for name, p in parts.items():
        path = os.path.join(HERE, f"{name}.stl")
        export_stl(p, path, tolerance=0.02, angular_tolerance=0.1)
        m = trimesh.load_mesh(path)
        assert m.is_watertight, f"{name}.stl not watertight"
        assert abs(m.volume - p.volume) / p.volume < 0.01, (name, m.volume, p.volume)

    vol_bin = half_a.volume + half_b.volume
    print(f"half A {half_a.volume/1000:.1f} cm3, half B {half_b.volume/1000:.1f} cm3, "
          f"bin {vol_bin/1000:.1f} cm3 = {vol_bin/1000*1.26:.0f} g PLA at 100%")
    print(f"drop {DROP:.2f} mm, stack pitch {STACK_PITCH:.2f} mm = {STACK_PITCH/IN:.3f} in, "
          f"4 stacked = {(3*STACK_PITCH + H)/IN:.2f} in")
    print(f"rib interference volume {overlap:.2f} mm3 (expected about {expected:.2f})")
    print(f"{n_slots} slots per wall, {slots_removed/1000:.1f} cm3 = {slots_removed/1000*1.26:.0f} g removed; "
          f"scallops {SCOOP_W:.1f} wide x {SCOOP_DEPTH:.0f} deep, {scoop_removed/1000:.1f} cm3")
    print(f"tail {TAIL_H:.1f} mm tall at the joint face (underside {TAIL_BOTTOM:.2f} to {SOCKET_Z:.1f} at the tip), "
          f"socket centre y = {DT_YC:.2f}, flare skin outside the socket {skin:.2f} mm")

    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show
        show(half_a, half_b, Pos(0, 0, STACK_PITCH) * half_a, Pos(0, 0, STACK_PITCH) * half_b,
             names=["half A", "half B", "upper A", "upper B"],
             reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
    return half_a, half_b, parts, whole


if __name__ == "__main__":
    main()
