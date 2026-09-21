"""iPhone 15 Pro Max slim case + glue-on camera guard ring, Bambu TPU 95A HF, X2D 0.4 nozzle. Canonical CAD source (build123d).

Every phone dimension is from Apple's dimensional drawing, transcribed in
reference/iphone-15-pro-max-dimensions.md (A = printed on the drawing, V = measured from its vectors).

Frame: looking at the screen, x to the right, y to the top of the phone, z toward the viewer.
Origin at the product centre in x and y; z = 0 is the print bed = the outside of the case back.
So the Action and volume buttons are at -x, the side button and the camera at +x.
The guard ring is modelled where it is glued (z from 0 down to -RING_H) and exported turned over, glue face on the bed.

Every rounded edge is a ruled loft through outlines generated at explicit insets (squircle()): OCCT's own 2D offset turns
the 8-edge spline outline into 44 edges, which will not loft, and fillets on spline edges are slow and fragile.

Run:  .venv/bin/python projects/iPhone-15-Pro-Max-case/iphone-15-pro-max-case.py      (SHOW=1 or SHOW=reset pushes to the viewer)
"""
import math
import os

from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = f"{HERE}/build"

# ---- phone (Apple drawing) ----
PH_W, PH_L, PH_T = 76.73, 159.86, 8.25
# plan corner, all four: a along one edge from the virtual corner, b inset from the other edge (A; 10, 5 and 14 are V points)
BODY_CORNER = [(17.24, 0.0), (14.0, 0.01), (12.36, 0.05), (10.0, 0.30), (7.58, 0.90), (5.0, 2.23), (3.48, 3.48)]
BODY_CORNER_CHECK = [(6.0, 1.63), (7.0, 1.15), (8.0, 0.78), (9.0, 0.50), (11.0, 0.16), (12.0, 0.08), (13.0, 0.03)]   # V, +/- 0.05
# edge cross-section, all sides, same front and back: (inset from the side surface, depth below the glass plane).
# Apple gives five points (A); the three between 0.81 and 2.41 are my quadratic ease, there only to stop the spline overshooting.
EDGE_PROFILE = [(0.0, 1.665), (0.06, 1.055), (0.32, 0.505), (0.81, 0.135), (1.2, 0.077), (1.6, 0.035), (2.0, 0.009), (2.41, 0.0)]
BTN_W, BTN_OUT, BTN_Z = 2.66, 0.45, 4.125                 # width across the band, protrusion, centreline above the back glass
# (centre from the top edge, length): Action, volume up, volume down on the -x side; side button on the +x side
ACTION, VOL_UP, VOL_DN, SIDE_BTN = (31.67, 6.04), (45.22, 11.20), (59.42, 11.20), (56.17, 17.70)
# bottom edge, Apple's front-frame X from the volume-button edge: hole groups (first, last hole centre), hole dia, USB-C keepout
HOLES_L, HOLES_R, HOLE_D = (20.40, 27.17), (49.56, 60.84), 1.35
USB_KEEPOUT = (12.45, 6.60, 14.0)                          # Apple's recommended connector keepout: w, h, clear outward
# camera, REAR frame in the note: X_r from the side-button edge, Y from the top edge
CAM_XR, CAM_Y = (1.04, 45.22), (1.04, 46.54)              # plateau outer boundary (base of the ramp, on the back glass)
CAM_TOP_XR, CAM_TOP_Y = (4.70, 41.56), (4.70, 42.88)      # plateau top flat
CAM_CORNER = [(17.47, 0.0), (14.0, 0.02), (12.0, 0.14), (10.0, 0.49), (8.0, 1.15), (6.0, 2.20), (5.0, 2.92), (3.90, 3.90)]      # V
CAM_TOP_CORNER = [(13.81, 0.0), (11.0, 0.01), (9.0, 0.09), (7.0, 0.44), (5.0, 1.23), (4.0, 1.84), (2.83, 2.83)]                 # V
CAM_H, LENS_H, LENS_D = 2.05, 4.07, 16.20                 # plateau and lens glass above the back glass, lens ring diameter
LENSES = [(14.17, 14.17), (14.17, 33.41), (32.16, 23.79)]  # (X_r, Y)
FLASH, REAR_SENSOR = (32.16, 10.22), (32.16, 38.22)
LENS_CLEAR_MIN = 0.85                                      # ADG 5.1.1: exposed glass at least this far off a flat surface

# ---- case ----
WALL = 1.5            # side walls (Brian)
BACK_T = 1.6          # back panel: 8 layers at 0.20
CLR = 0.10            # cavity larger than the phone by this per side; printed TPU cavities come out a little small, and a case should grip
LIP_IN = 0.85         # the lip stops this far in from the housing edge: the glass starts at 1.00 and Apple says do not touch it
LIP_GAP = 0.05        # gap, normal to the surface, between the lip's 45 degree underside and the phone's shoulder
CASE_H = 10.8         # 54 layers; the lip stands 0.95 proud of the glass (Apple: 0.85 min, 1.00 ideal)
BOT_CH = 0.5          # 45 degree chamfer on the bed edge of the outside
TOP_R = 1.0           # round on the outside top edge
LIP_R = 0.4           # round on the lip's inside top edge
FLOOR_R = 0.8         # round where the inside wall meets the floor (the phone's own edge curve leaves room for it)
WIN_H, WIN_FLARE = 5.0, 0.75      # button windows: height at the inside of the wall; 45 degree flare over the outer part of the wall, top and bottom only
WIN_END = 1.0         # window runs this far past each end of its button(s)
USB_W, USB_H = 13.0, 7.0          # Apple: at least 12.35 x 6.50, should be 12.45 x 6.60 plus margin
PORT_OFFSET = 2.0     # ADG 5.2.3 thin case: acoustic openings at least this far from the edge of any port
CAM_CLR = 0.4         # horizontal clearance between the case floor and the camera's glass ramp (straight-ramp proxy, which errs large)
FLOOR_EDGE_T = 0.2    # the floor runs in over the ramp, its phone side sloped parallel to the ramp, until it is this thin (1 layer; the ring backs it)
# ---- guard ring ----
# Brian, 2026-09-20, on the first ring (on the plateau's OUTER boundary, the base of the glass ramp, 4 mm off the raised island):
# "the guard around it is too big. It should be snug around the camera." On the second (snug, 5.1 mm wide, Apple's flash and
# rear-sensor cones cut out of it): "the ring is too thick and there are cutouts in the top right and bottom right. Not good".
# So: slim, snug, plain. Its inside wall is the camera opening's own edge, which also locates it for gluing.
RING_TOP = 5.0        # ring top above the back glass: lens glass at 4.07, so 0.93 clear
RING_W = 2.5          # ring width
RING_CH = 1.5         # 45 degree bevel on the inside, all round (Brian: "the guard should also be a bevel on the inside"): the most a
                      # 2.5 mm ring allows with a flat rim left on top, and the most a slim ring can do for the flash and lens cones
RING_R = 0.5          # round on the ring's outside top edge

ZG = BACK_T + PH_T                 # front glass plane
ZMID = BACK_T + BTN_Z              # centreline of every button and bottom port
RING_H = RING_TOP - BACK_T
RAMP_W = CAM_TOP_XR[0] - CAM_XR[0]                                   # 3.66: the glass ramp between the plateau's outer boundary and its top flat
FLOOR_EDGE = (BACK_T - FLOOR_EDGE_T) * RAMP_W / CAM_H - CAM_CLR      # how far in from the outer boundary the floor's edge reaches
RING_IN = FLOOR_EDGE                                                 # the ring's inside wall: flush with the floor's edge
N_ARC = 6                          # sections per quarter round


def fx(x_f):
    """Apple's front-frame X (from the volume-button edge) to model x."""
    return x_f - PH_W / 2


def rx(x_r):
    """Apple's rear-frame X (from the side-button edge) to model x."""
    return PH_W / 2 - x_r


def ty(y_top):
    """Apple's Y (from the top edge, downward) to model y."""
    return PH_L / 2 - y_top


def corner_curve(corner):
    """Apple's corner in its own frame (a, b), splined; the curve is symmetric about the diagonal."""
    half = corner + [(b, a) for a, b in reversed(corner[:-1])]
    return Spline(*half, tangents=((-1, 0), (0, 1)))


def squircle(w, h, corner, inset=0.0, n=24):
    """Centred w x h face with Apple's corner curve, moved inward by inset (outward if negative) along the curve's normals.
    Always 4 splines + 4 lines, whatever the inset, so sections loft together and booleans stay light."""
    c, t = corner_curve(corner), corner[0][0]
    pts = []
    for i in range(n + 1):
        p, tg = c @ (i / n), c % (i / n)
        nx, ny = -tg.Y, tg.X
        if nx + ny < 0:                                # the phone's centre is on the +a, +b side of the curve
            nx, ny = -nx, -ny
        pts.append((p.X + inset * nx, p.Y + inset * ny))
    edges = []
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        edges.append(Spline(*[(sx * (w / 2 - a), sy * (h / 2 - b)) for a, b in pts], tangents=((sx, 0), (0, -sy))))
    ww, hh = w / 2 - inset, h / 2 - inset
    edges += [Line((-(w / 2 - t), s * hh), (w / 2 - t, s * hh)) for s in (1, -1)]
    edges += [Line((s * ww, -(h / 2 - t)), (s * ww, h / 2 - t)) for s in (1, -1)]
    return Face(Wire(edges))


def stack(w, h, corner, levels, at=(0, 0)):
    """Ruled loft through squircle outlines: levels = [(z, inset), ...] from the bottom up."""
    return loft([Pos(at[0], at[1], z) * squircle(w, h, corner, i) for z, i in levels], ruled=True)


def quarter(n=N_ARC):
    """(sin, 1 - cos) pairs along a quarter round, 0 to 90 degrees."""
    return [(math.sin(math.pi / 2 * k / n), 1 - math.cos(math.pi / 2 * k / n)) for k in range(n + 1)]


def body(levels):
    return stack(PH_W, PH_L, BODY_CORNER, levels)


# ---- phone proxy ----
_c = corner_curve(BODY_CORNER)
_samples = [_c @ (i / 4000) for i in range(4001)]
for a, b in BODY_CORNER_CHECK:
    got = min(_samples, key=lambda p: abs(p.X - a)).Y
    assert abs(got - b) <= 0.05, f"body corner at a={a}: {got:.3f} vs Apple's {b}"
assert min(p.Y for p in _samples) > -0.002, "the corner spline bulges outside the body's straight edge"

_prof = Spline(*EDGE_PROFILE, tangents=((0, -1), (1, 0)))
PROFILE = [((_prof @ (i / 60)).X, (_prof @ (i / 60)).Y) for i in range(61)]            # (inset, depth below the glass plane)
assert all(b[0] >= a[0] - 1e-6 and b[1] <= a[1] + 1e-6 for a, b in zip(PROFILE, PROFILE[1:])), "edge profile is not monotone"
assert min(d for _, d in PROFILE) > -1e-3, "edge profile overshoots the glass plane"


def phone_body():
    prof = PROFILE[::5]                                                 # 13 sections per edge
    lower = [(max(d, 0.0), i) for i, d in prof][::-1]                   # from the back glass plane out to the flat side
    return body([(BACK_T + d, i) for d, i in lower] + [(ZG - d, i) for d, i in lower[::-1]])


def button(centre_top, length, side):
    """Stadium button standing BTN_OUT proud of the housing; side = -1 for the volume side, +1 for the side-button side."""
    pl = Plane(origin=(side * PH_W / 2, ty(centre_top), ZMID), x_dir=(0, 1, 0), z_dir=(side, 0, 0))
    return pl * extrude(Pos(0, 0, -1) * SlotOverall(length, BTN_W), 1 + BTN_OUT)


CAM_AT = ((rx(CAM_XR[0]) + rx(CAM_XR[1])) / 2, (ty(CAM_Y[0]) + ty(CAM_Y[1])) / 2)
CAM_SIZE = (CAM_XR[1] - CAM_XR[0], CAM_Y[1] - CAM_Y[0])
CAM_TOP_SIZE = (CAM_TOP_XR[1] - CAM_TOP_XR[0], CAM_TOP_Y[1] - CAM_TOP_Y[0])


def camera():
    # straight ramp from the outer boundary to the top flat: the real ramp is a concave fillet, so this proxy errs large
    ramp = loft([Pos(*CAM_AT, BACK_T + 0.5) * squircle(*CAM_SIZE, CAM_CORNER), Pos(*CAM_AT, BACK_T) * squircle(*CAM_SIZE, CAM_CORNER),
                 Pos(*CAM_AT, BACK_T - CAM_H) * squircle(*CAM_TOP_SIZE, CAM_TOP_CORNER)], ruled=True)
    lenses = [Pos(rx(xr), ty(y), BACK_T - LENS_H) * Cylinder(LENS_D / 2, LENS_H, align=(Align.CENTER, Align.CENTER, Align.MIN)) for xr, y in LENSES]
    return ramp + lenses


phone = phone_body() + [button(*ACTION, -1), button(*VOL_UP, -1), button(*VOL_DN, -1), button(*SIDE_BTN, 1)] + camera()
_bb = phone_body().bounding_box()
assert abs(_bb.size.X - PH_W) < 0.01 and abs(_bb.size.Y - PH_L) < 0.01 and abs(_bb.size.Z - PH_T) < 0.01, _bb.size
assert len(phone.solids()) == 1, len(phone.solids())

# ---- case shell: outside, cavity, screen opening ----
# lip underside: a 45 degree plane z = ZG + inset + K, LIP_GAP off the phone's shoulder at the one point where the shoulder slopes 45 degrees
K = max(-d - i for i, d in PROFILE) + LIP_GAP * math.sqrt(2)
Z1 = ZG + K - CLR                  # where the 45 degree underside leaves the cavity wall
Z2 = ZG + K + LIP_IN               # the lip's tip
OUT = CLR + WALL

outside = body([(0, -OUT + BOT_CH), (BOT_CH, -OUT)]
               + [(CASE_H - TOP_R + TOP_R * s, -OUT + TOP_R * c) for s, c in quarter()])
_big = LIP_IN + CLR + 0.3          # carry the 45 degree underside past the lip's tip so the screen opening trims it, no coincident faces
cavity = body([(BACK_T + FLOOR_R * c, -CLR + FLOOR_R * (1 - s)) for s, c in quarter()]
              + [(Z1, -CLR), (Z1 + _big, -CLR + _big)])
screen = body([(Z1 - 0.5, LIP_IN)] + [(CASE_H - LIP_R + LIP_R * s, LIP_IN - LIP_R * c) for s, c in quarter()] + [(CASE_H + 1, LIP_IN - LIP_R - 1)])
shell = outside - cavity - screen

# ---- camera opening: the floor's phone side slopes up over the glass ramp, CAM_CLR off it; the outer FLOOR_EDGE_T is a plain edge ----
cam_open = stack(*CAM_SIZE, CAM_CORNER, [(-1, FLOOR_EDGE), (FLOOR_EDGE_T, FLOOR_EDGE), (BACK_T, -CAM_CLR), (BACK_T + 1, -CAM_CLR)], CAM_AT)


# ---- windows ----
def window(length, height, plane, flare=0.0):
    """Stadium window through a wall. plane: origin on the cavity wall at the window centre, x_dir along the wall, z_dir outward.
    flare widens the height only (45 degrees over the outer part of the wall), so the posts between windows keep their width."""
    cut = extrude(Pos(0, 0, -1) * SlotOverall(length, height), WALL + 2)
    if flare:
        grow = 2 * (flare + 0.5)
        cut += loft([Pos(0, 0, WALL - flare) * SlotOverall(length, height), Pos(0, 0, WALL + 0.5) * SlotOverall(length, height + grow)])
    return plane * cut


def side_plane(side, y):
    return Plane(origin=(side * (PH_W / 2 + CLR), y, ZMID), x_dir=(0, 1, 0), z_dir=(side, 0, 0))


def bottom_plane(x):
    return Plane(origin=(x, -(PH_L / 2 + CLR), ZMID), x_dir=(1, 0, 0), z_dir=(0, -1, 0))


def span(first, last):
    """(centre from the top edge, length) of a window over the buttons first..last, WIN_END past each end."""
    y0, y1 = first[0] - first[1] / 2 - WIN_END, last[0] + last[1] / 2 + WIN_END
    return (y0 + y1) / 2, y1 - y0


def slot_x(holes):
    """(centre x, length) of an acoustic slot: PORT_OFFSET clear of the edge of the first and last hole."""
    x0, x1 = holes[0] - HOLE_D / 2 - PORT_OFFSET, holes[1] + HOLE_D / 2 + PORT_OFFSET
    return fx((x0 + x1) / 2), x1 - x0


WINDOWS = {   # name: (length, cutter)
    "action": (span(ACTION, ACTION)[1], window(span(ACTION, ACTION)[1], WIN_H, side_plane(-1, ty(span(ACTION, ACTION)[0])), WIN_FLARE)),
    "volume": (span(VOL_UP, VOL_DN)[1], window(span(VOL_UP, VOL_DN)[1], WIN_H, side_plane(-1, ty(span(VOL_UP, VOL_DN)[0])), WIN_FLARE)),
    "side button": (span(SIDE_BTN, SIDE_BTN)[1], window(span(SIDE_BTN, SIDE_BTN)[1], WIN_H, side_plane(1, ty(span(SIDE_BTN, SIDE_BTN)[0])), WIN_FLARE)),
    "usb-c": (USB_W, window(USB_W, USB_H, bottom_plane(0))),
    "mic slot": (slot_x(HOLES_L)[1], window(slot_x(HOLES_L)[1], HOLE_D + 2 * PORT_OFFSET, bottom_plane(slot_x(HOLES_L)[0]))),
    "speaker slot": (slot_x(HOLES_R)[1], window(slot_x(HOLES_R)[1], HOLE_D + 2 * PORT_OFFSET, bottom_plane(slot_x(HOLES_R)[0]))),
}

with_camera = shell - cam_open
case = with_camera - [w for _, w in WINDOWS.values()]

# ---- Apple's keepout cones (sheet 2; r(h) from the note) ----
def cone(at, r0, r1, h0, h1):
    """Keepout cone around an axis at (X_r, Y): radius r0 at height h0 above the back glass growing to r1 at h1 (it opens away from the phone)."""
    c = Cone(r1, r0, h1 - h0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(rx(at[0]), ty(at[1]), BACK_T - h1) * c


_h1 = RING_TOP + 0.3
KEEPOUTS = {
    "camera 1": cone(LENSES[0], 1.842 * (0.1 - 0.03), 1.842 * (_h1 - 0.03), 0.1, _h1),
    "camera 2": cone(LENSES[1], 0.933 * (0.0 + 0.52), 0.933 * (_h1 + 0.52), 0.0, _h1),
    "camera 3": cone(LENSES[2], 0.2135 * (0.0 + 12.85), 0.2135 * (_h1 + 12.85), 0.0, _h1),
    "flash inner": cone(FLASH, 1.483 * (0.2 - 0.10), 1.483 * (4.11 - 0.10), 0.2, 4.11),
    "flash outer": cone(FLASH, 5.95, 5.95 + 4.915 * (_h1 - 4.11), 4.11, _h1),
    "rear sensor": cone(REAR_SENSOR, 7.31, 7.31 + 0.850 * (_h1 - CAM_H), CAM_H, _h1),
}
RING_MAY_CROSS = ("flash outer", "rear sensor")     # Brian's call: a snug plain ring cannot clear these two (no cutaways wanted)

# ---- guard ring (as glued: z from 0 down to -RING_H) ----
_ring_levels = [(-RING_H + RING_R - RING_R * s, RING_R * c) for s, c in quarter()][::-1] + [(0.0, 0.0)]      # rounded top edge, from the top down to the glue face
ring_blank = stack(*CAM_SIZE, CAM_CORNER, [(z, RING_IN - RING_W + i) for z, i in _ring_levels], CAM_AT)
ring_bore = stack(*CAM_SIZE, CAM_CORNER, [(-RING_H - 1, RING_IN - RING_CH - 1), (-RING_H + RING_CH, RING_IN), (1, RING_IN)], CAM_AT)
ring = ring_blank - ring_bore
ring_print = Rot(0, 180, 0) * ring                                          # turned over (a rotation, not a mirror): glue face on the bed


# ---- checks ----
def vol(shape):
    return sum(s.volume for s in shape.solids()) if shape else 0.0


if __name__ == "__main__":
    os.makedirs(BUILD, exist_ok=True)
    report = {}
    assert len(case.solids()) == 1 and len(ring.solids()) == 1, (len(case.solids()), len(ring.solids()))
    bb = case.bounding_box()
    want = (PH_W + 2 * OUT, PH_L + 2 * OUT, CASE_H)
    assert all(abs(g - w) < 0.02 for g, w in zip((bb.size.X, bb.size.Y, bb.size.Z), want)), (bb.size, want)
    assert abs(bb.min.Z) < 1e-4 and abs(ring_print.bounding_box().min.Z) < 1e-4 and abs(ring_print.bounding_box().size.Z - RING_H) < 1e-4
    report["case size"] = [round(v, 2) for v in (bb.size.X, bb.size.Y, bb.size.Z)]
    report["case cm3"], report["ring cm3"] = round(case.volume / 1000, 2), round(ring.volume / 1000, 2)
    # the phone, buttons and camera included, touches nothing
    report["phone x case mm3"], report["phone x ring mm3"] = round(vol(phone & case), 3), round(vol(phone & ring), 3)
    assert report["phone x case mm3"] < 0.01 and report["phone x ring mm3"] < 0.01, report
    # measured on the solids: the snug ring and the floor's sloped edge both stay off the camera's glass (straight-ramp proxy)
    report["ring to phone, nearest"] = round(ring.distance_to(phone), 3)
    report["case floor to camera ramp, nearest"] = round((case & Pos(*CAM_AT, 0) * Box(60, 60, 2 * BACK_T - 0.02)).distance_to(camera()), 3)
    assert report["ring to phone, nearest"] >= 0.15 and report["case floor to camera ramp, nearest"] >= 0.15, report
    report["ring: inside wall to the camera's raised flat / width = glue land"] = [round(RAMP_W - RING_IN, 2), RING_W]
    # the ring sits on the back; the case clears every Apple keepout cone, the ring every cone but the two Brian accepted
    assert vol(ring & case) < 0.01, vol(ring & case)
    for name, k in KEEPOUTS.items():
        assert vol(k & case) < 0.001, f"{name} keepout cone is blocked by the case: {vol(k & case):.3f} mm3"
        if name in RING_MAY_CROSS:
            report[f"ring inside Apple's {name} cone, mm3 (accepted)"] = round(vol(k & ring), 1)
        else:
            assert vol(k & ring) < 0.001, f"{name} keepout cone is blocked by the ring: {vol(k & ring):.3f} mm3"
    assert RING_TOP - LENS_H >= LENS_CLEAR_MIN, RING_TOP - LENS_H
    report["lens glass to a flat surface"] = round(RING_TOP - LENS_H, 2)
    # Apple's USB-C connector keepout passes through the wall untouched
    usb = bottom_plane(0) * extrude(Pos(0, 0, -0.5) * SlotOverall(USB_KEEPOUT[0], USB_KEEPOUT[1]), USB_KEEPOUT[2])
    assert vol(usb & case) < 0.001, vol(usb & case)
    # lip: stands proud of the glass, stops short of it in plan, and its tip is above the phone's surface there
    report["lip above glass"] = round(CASE_H - ZG, 2)
    report["lip underside leaves the wall at z"], report["lip tip z"] = round(Z1, 3), round(Z2, 3)
    assert CASE_H - ZG >= LENS_CLEAR_MIN and LIP_IN < 1.0 and Z2 > ZG
    report["window bridges mm (flat top, inside of wall)"] = {n: round(l - (WIN_H if n in ("action", "volume", "side button") else USB_H if n == "usb-c" else HOLE_D + 2 * PORT_OFFSET), 2) for n, (l, _) in WINDOWS.items()}
    _a, _v = span(ACTION, ACTION), span(VOL_UP, VOL_DN)
    report["post between action and volume windows"] = round((_v[0] - _v[1] / 2) - (_a[0] + _a[1] / 2), 2)
    report["posts beside usb-c"] = [round(-USB_W / 2 - (slot_x(HOLES_L)[0] + slot_x(HOLES_L)[1] / 2), 2), round(slot_x(HOLES_R)[0] - slot_x(HOLES_R)[1] / 2 - USB_W / 2, 2)]

    for name, shape in (("stage1-shell", shell), ("stage2-camera", with_camera), ("phone-proxy", phone)):
        export_stl(shape, f"{BUILD}/{name}.stl", tolerance=0.01, angular_tolerance=0.2)
    export_stl(case, f"{HERE}/iphone-15-pro-max-case.stl", tolerance=0.01, angular_tolerance=0.2)
    export_stl(ring_print, f"{HERE}/camera-guard-ring.stl", tolerance=0.01, angular_tolerance=0.2)
    export_stl(ring, f"{BUILD}/ring-as-glued.stl", tolerance=0.01, angular_tolerance=0.2)

    import trimesh
    for f in ("iphone-15-pro-max-case.stl", "camera-guard-ring.stl"):
        m = trimesh.load(f"{HERE}/{f}")
        assert m.is_watertight and len(m.split()) == 1, f"{f}: watertight {m.is_watertight}, bodies {len(m.split())}"
        report[f] = f"{len(m.faces)} triangles, watertight"
        # printability: faces off the bed that face down more than 47 degrees from vertical (45 plus facet margin).
        # Flat ones are the window roofs (bridges); anything else steep is the rounded ends of the windows.
        down = (m.face_normals[:, 2] < -math.sin(math.radians(47))) & (m.triangles_center[:, 2] > 0.01)
        flat = down & (m.face_normals[:, 2] < -0.999)
        roofs = {}
        for z, a in zip(m.triangles_center[flat][:, 2], m.area_faces[flat]):
            roofs[round(float(z), 2)] = round(roofs.get(round(float(z), 2), 0.0) + float(a), 1)
        report[f + " bridges, mm2 by z"] = roofs
        report[f + " other steep overhang mm2"] = round(float(m.area_faces[down & ~flat].sum()), 1)
    for k, v in report.items():
        print(f"{k}: {v}")

    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show
        show(case, ring, phone, names=["case", "guard ring (as glued)", "phone (Apple drawing)"], colors=["#2f6f4f", "#c9772b", "#9aa0a6"],
             reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
