"""Narrow skateboard wall hook, concept A (Brian's Skate Hook Studio prompt, 2026-10-04).

The board hangs nose-up with its trucks toward the wall. The top truck's hanger center body
rests in a curved cradle on a narrow tongue (Brian: "the tongue should have a curved shape, so
the board doesn't slide off if it is bumped"); the kingpin nut sits above it as a locator, not
as the load path. The lower wheels rest on the wall.

Cradle: in side view an arc of CRADLE_R around a center 2 mm above the hanger's half-round
center, so the hanger drops in and nests with a rim toward the room (the bump stop) and a lower
rim toward the wall (the wall and wheels stop that side anyway). Across the width the whole
tongue top is hollowed to a SADDLE_R arc carried along the cradle, so the lip dips too and the
hanger's dome is cradled at the lip as well as at the floor (see the dish section).

Design frame: x from the wall face toward the room, y up the deck, z across the board
(the holder's width). The hanging truck's axle is at y = 0. The print frame lays the part
on its side (design z becomes print Z), so the tongue's bending load runs along the layers.

Run:  .venv/bin/python projects/Skateboard-wall-holder/skateboard_holder.py
      SHOW=reset ... pushes to the OCP viewer (scripts/cad-viewer.sh first); SHOW=1 keeps the camera.
Writes skateboard-holder.stl (print orientation, on Z = 0) and the design-frame scene STLs in build/
(holder-design, truck, nut, wheels, deck, bulb) for pipeline/hold_check.py and pipeline/renders.py.
"""
import math
import os

import trimesh
from build123d import *  # noqa: F403

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

# ---- holder (Brian's spec, tongue reworked to a cradle 2026-10-04) ----
W = 40.0                                   # width across the board (Brian 2026-10-04: wider than the 30 first drawn)
PLATE_T, PLATE_H, PLATE_ABOVE = 6.0, 110.0, 30.0
REACH = 74.0                               # 2 mm short of the baseplate
TONGUE_T = 12.0                            # at the cradle bottom
CRADLE_CLEAR = 2.0                         # cradle radius over the hanger's half-round
RIM_ROOM_DEG, RIM_WALL_DEG = 65.0, 45.0
RIM_ROOM_DEG_I, RIM_WALL_DEG_I = 65, 45    # cradle arc span each side of its bottom (deeper, Brian 2026-10-04); wall side limited by the washer clearance
SADDLE_R = 27.0
GUSSET = 18.0
ROUND, SMALL_ROUND, SIDE_CHAMFER = 3.0, 2.0, 0.6
SCREW_D, CSK_D, CSK_DEPTH, SCREW_INSET = 5.0, 10.0, 2.5, 10.0   # #8 countersunk, NACS holder convention

# ---- truck and board (tool defaults: Independent-size estimates, not yet measured) ----
DECK_T, DECK_W = 10.5, 210.0
TRUCK_H, WHEEL_D, WHEEL_W, HANGER_W, AXLE_W = 55.0, 54.0, 33.0, 139.0, 203.0
BULB_W, BULB_TOP, BULB_BOT, BULB_IN, BULB_OUT, BOSS_R = 53.0, 10.0, 46.0, 42.0, 10.0, 12.0
BASE_LEN, BASE_W, BASE_T = 82.0, 60.0, 6.0
NUT_DEPTH, NUT_IN, KP_DEG, NUT_AF, NUT_H, WASHER_D = 55.0, 20.0, 15.0, 14.3, 6.7, 23.0
WALL_GAP = 0.0

# ---- derived ----
DECK_X = TRUCK_H + WHEEL_D / 2 + WALL_GAP          # deck underside from the wall
AXLE_X = DECK_X - TRUCK_H
RB = (BULB_BOT - BULB_TOP) / 2                      # the body's inboard end is a half-round of its depth
BULB_X0, BULB_X1 = DECK_X - BULB_BOT, DECK_X - BULB_TOP
BULB_CX, BULB_CY = BULB_X0 + RB, -(BULB_IN - RB)   # center of the half-round; lowest point (BULB_CX, -BULB_IN)
CRADLE_R = RB + CRADLE_CLEAR
CRADLE_C = (BULB_CX, BULB_CY + CRADLE_CLEAR)       # cradle bottom touches the hanger's lowest point
BOTTOM_R = CRADLE_R + TONGUE_T                     # tongue underside, concentric
SAG = SADDLE_R - math.sqrt(SADDLE_R ** 2 - (W / 2) ** 2)              # rim height above the dish center
X_RIM_ROOM = CRADLE_C[0] + CRADLE_R * math.sin(math.radians(RIM_ROOM_DEG))
X_RIM_WALL = CRADLE_C[0] - CRADLE_R * math.sin(math.radians(RIM_WALL_DEG))
assert X_RIM_ROOM < REACH - 1.5, (X_RIM_ROOM, REACH)


def y_top(x):
    """Tongue top along the center line (dish bottom): cradle arc with flat tails."""
    x = min(max(x, X_RIM_WALL), X_RIM_ROOM)
    return CRADLE_C[1] - math.sqrt(CRADLE_R ** 2 - (x - CRADLE_C[0]) ** 2)


Y_ROOT, Y_RIM_ROOM, Y_BOTTOM = y_top(PLATE_T), y_top(REACH), CRADLE_C[1] - BOTTOM_R
PLATE_TOP = Y_ROOT + PLATE_ABOVE
PLATE_BOT = PLATE_TOP - PLATE_H
SCREW_YS = (PLATE_TOP - SCREW_INSET, PLATE_BOT + SCREW_INSET)
HOLD_ROOM = Y_RIM_ROOM + BULB_IN                   # lift to carry the hanger's lowest point over the room rim
HOLD_WALL = Y_ROOT + BULB_IN
TOP_UP = SAG + 1.0                                 # profile top above the dish center line; the dish cut sets the rims

# ---- side profile: plate, gusset, scoop tongue (counterclockwise) ----
E_END = (REACH, CRADLE_C[1] - math.sqrt(BOTTOM_R ** 2 - (REACH - CRADLE_C[0]) ** 2))   # tongue end on the bottom arc
ang_mid = math.asin((REACH - CRADLE_C[0]) / BOTTOM_R) / 2
E_MID = (CRADLE_C[0] + BOTTOM_R * math.sin(ang_mid), CRADLE_C[1] - BOTTOM_R * math.cos(ang_mid))
A = (0.0, PLATE_BOT)
B = (PLATE_T, PLATE_BOT)
Cg = (PLATE_T, Y_BOTTOM - GUSSET)
D = (PLATE_T + GUSSET, Y_BOTTOM)
E0 = (CRADLE_C[0], Y_BOTTOM)                       # bottom arc starts tangent to the flat underside
F = (REACH, Y_RIM_ROOM + TOP_UP)
G = (X_RIM_ROOM, y_top(X_RIM_ROOM) + TOP_UP)
G_MID = (CRADLE_C[0], CRADLE_C[1] - CRADLE_R + TOP_UP)
H = (X_RIM_WALL, y_top(X_RIM_WALL) + TOP_UP)
I = (PLATE_T, Y_ROOT + TOP_UP)
J = (PLATE_T, PLATE_TOP)
K = (0.0, PLATE_TOP)

with BuildLine() as outline:
    Polyline(A, B, Cg, D, E0)
    ThreePointArc(E0, E_MID, E_END)
    Polyline(E_END, F, G)
    ThreePointArc(G, G_MID, H)
    Polyline(H, I, J, K, A)
profile = make_face(outline.wire())


def vert_at(shape, pt, tol=0.05):
    for v in shape.vertices():
        if abs(v.X - pt[0]) < tol and abs(v.Y - pt[1]) < tol:
            return v
    raise KeyError(pt)


profile = fillet(ShapeList([vert_at(profile, p) for p in (B, D, E_END, J)]), ROUND)
profile = fillet(ShapeList([vert_at(profile, p) for p in (H, I)]), SMALL_ROUND)
END_FLAT = REACH - X_RIM_ROOM                      # short flat between the room rim and the tongue end
profile = fillet(ShapeList([vert_at(profile, F)]), min(ROUND, END_FLAT * 0.55))
profile = fillet(ShapeList([vert_at(profile, G)]), min(SMALL_ROUND, END_FLAT * 0.3))
holder = extrude(profile, amount=W / 2, both=True)

# ---- dish: the saddle arc (SADDLE_R across the width) carried along the side-view top line, so every
# cross-section is the same arc with its bottom on the cradle: the lip toward the room has the same rounded
# dip as the floor (Brian 2026-10-04: "the front lip of the holder should also have a rounded dip, to cradle
# the truck"). Built as a loft of those arcs through stations along x.
Y_FLOOR = y_top(CRADLE_C[0])
ZD = W / 2 + 2.0                                   # the arc runs past the side faces
H_ZD = SADDLE_R - math.sqrt(SADDLE_R ** 2 - ZD ** 2)
# the first station sits exactly on the plate's front face: one station further in shaved the plate above the
# tongue to 5 mm and left the upper countersink shallow (caught by the 3MF's screw-pad check, 2026-10-04)
stations = sorted(set([PLATE_T, REACH + 1.0, X_RIM_WALL, X_RIM_ROOM]
                      + [PLATE_T + i * 5.0 for i in range(1, 8) if PLATE_T + i * 5.0 < X_RIM_WALL - 1]
                      + [CRADLE_C[0] + CRADLE_R * math.sin(math.radians(a)) for a in range(-RIM_WALL_DEG_I + 5, RIM_ROOM_DEG_I, 5)]))
sections = []
for x in stations:
    yt = y_top(x)
    pl = Plane(origin=(x, 0, 0), x_dir=(0, 0, -1), z_dir=(1, 0, 0))      # local x = -z, local y = y
    with BuildLine(pl) as sec:
        ThreePointArc((-ZD, yt + H_ZD), (0, yt), (ZD, yt + H_ZD))
        Polyline((ZD, yt + H_ZD), (ZD, yt + 40), (-ZD, yt + 40), (-ZD, yt + H_ZD))
    sections.append(make_face(sec.wire()))
dish = loft(sections, ruled=True)                 # ruled: no spline overshoot where the arc meets the flats
assert len(dish.solids()) == 1
holder = holder - dish

# screw holes with 90 degree countersinks on the room face
for ys in SCREW_YS:
    holder -= Pos(PLATE_T / 2, ys, 0) * Rot(0, 90, 0) * Cylinder(SCREW_D / 2, PLATE_T + 4)
    cone = Cone(CSK_D / 2, SCREW_D / 2, CSK_DEPTH + 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN))
    holder -= Pos(PLATE_T + 0.01, ys, 0) * Rot(0, -90, 0) * cone

# light chamfer on the two side faces (bed face and top face in the print)
side_chamfer_ok = True
try:
    side_edges = ShapeList([e for f in holder.faces().filter_by(Axis.Z) for e in f.edges()])
    holder = chamfer(side_edges, SIDE_CHAMFER)
except Exception as exc:  # noqa: BLE001
    side_chamfer_ok = False
    print("side chamfer skipped:", exc)

# ---- truck proxy (design frame, docked pose) ----
deck = Pos(DECK_X + DECK_T / 2, -75, 0) * Box(DECK_T, 450, DECK_W)
base = Pos(DECK_X - BASE_T / 2, 0, 0) * Box(BASE_T, BASE_LEN, BASE_W)
boss = Pos(AXLE_X, 0, 0) * Cylinder(BOSS_R, HANGER_W)
axle = Pos(AXLE_X, 0, 0) * Cylinder(4, AXLE_W)
wheels = Part() + [Pos(AXLE_X, 0, s * (HANGER_W / 2 + 1 + WHEEL_W / 2)) * Cylinder(WHEEL_D / 2, WHEEL_W) for s in (-1, 1)]
pivot = Pos((AXLE_X + DECK_X - BASE_T) / 2, 18, 0) * Box(DECK_X - BASE_T - AXLE_X, 32, 24)
bulb_profile = (Pos((BULB_X0 + BULB_X1) / 2, (BULB_CY + BULB_OUT) / 2, 0) * Box(BULB_X1 - BULB_X0, BULB_OUT - BULB_CY, BULB_W)
                + Pos(BULB_CX, BULB_CY, 0) * Cylinder(RB, BULB_W))
lateral_round = Pos((BULB_X0 + BULB_X1) / 2, -BULB_IN + BULB_W / 2, 0) * Rot(0, 90, 0) * Cylinder(BULB_W / 2, BULB_X1 - BULB_X0 + 2)
bulb_block = bulb_profile & lateral_round          # rounded block: half-round side profile, half-round across, both extruded


def y_hanger(x):
    """Underside of the hanger's half-round at x (center line)."""
    return BULB_CY - math.sqrt(max(0.0, RB ** 2 - (x - BULB_CX) ** 2))


RL = BULB_W / 2                                    # lateral half-round of the hanger's underside
dome_sections = []
for a in range(-90, 91, 6):                        # stations clustered toward the half-round's ends
    x = BULB_CX + RB * math.sin(math.radians(a))
    yh = y_hanger(x)
    pl = Plane(origin=(x, 0, 0), x_dir=(0, 0, -1), z_dir=(1, 0, 0))
    with BuildLine(pl) as sec:
        ThreePointArc((-RL, yh + RL), (0, yh), (RL, yh + RL))
        Polyline((RL, yh + RL), (RL, BULB_OUT), (-RL, BULB_OUT), (-RL, yh + RL))
    dome_sections.append(make_face(sec.wire()))
bulb = loft(dome_sections, ruled=True)             # dome: rounded both ways at once, the shape the dish is cut for
assert len(bulb.solids()) == 1
truck = base + boss + axle + pivot + bulb
truck_block = base + boss + axle + pivot + bulb_block

NUT_AC = NUT_AF / math.cos(math.radians(30))
u_back = (math.cos(math.radians(KP_DEG)), -math.sin(math.radians(KP_DEG)), 0)   # from the nut top toward the deck
nut_top = (DECK_X - NUT_DEPTH, -NUT_IN, 0)
orient = Rot(0, 0, -KP_DEG) * Rot(0, 90, 0)
nut = Pos(*nut_top) * orient * extrude(RegularPolygon(NUT_AC / 2, 6), NUT_H)
washer = Pos(*(nut_top[i] + NUT_H * u_back[i] for i in range(3))) * orient * Cylinder(WASHER_D / 2, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
stack = nut + washer

# ---- checks ----
assert len(holder.solids()) == 1, len(holder.solids())
bb = holder.bounding_box()
assert abs(bb.min.X) < 1e-3 and abs(bb.max.X - REACH) < 1e-3 and abs(bb.max.Z - W / 2) < 1e-3, bb
assert 55e3 < holder.volume < 90e3, holder.volume


def top_at(x, z):
    col = (holder & Pos(x, y_top(x) + 2, z) * Box(0.2, 40, 0.02)).bounding_box()
    return col.max.Y


ZR = W / 2 - 1.0                                   # rim probe inside the side chamfer
for x, z, expect in ((CRADLE_C[0], 0.0, y_top(CRADLE_C[0])), (CRADLE_C[0], ZR, y_top(CRADLE_C[0]) + SADDLE_R - math.sqrt(SADDLE_R ** 2 - ZR ** 2)),
                     (20.0, 0.0, Y_ROOT), (REACH - 1.0, 0.0, Y_RIM_ROOM), (X_RIM_ROOM - 6, 0.0, y_top(X_RIM_ROOM - 6)),
                     (REACH - 1.0, ZR, Y_RIM_ROOM + SADDLE_R - math.sqrt(SADDLE_R ** 2 - ZR ** 2))):   # the lip dips too
    got = top_at(x, z)
    assert abs(got - expect) < 0.15, (x, z, got, expect)
# the plate keeps its full thickness above the tongue root (the dish must not cut into the plate's front face)
plate_probe = holder & Pos(PLATE_T - 0.25, (PLATE_TOP + Y_ROOT + SAG) / 2, 0) * Box(0.5, PLATE_TOP - Y_ROOT - SAG - 4, W - 4)
_full = 0.5 * (PLATE_TOP - Y_ROOT - SAG - 4) * (W - 4)                # the upper countersink takes about 12% of it
assert plate_probe.volume > 0.8 * _full, (plate_probe.volume, _full)   # a 1 mm shave would leave nothing
for ys in SCREW_YS:   # screw holes go through
    assert (holder & Pos(PLATE_T / 2, ys, 0) * Rot(0, 90, 0) * Cylinder(SCREW_D / 2 - 0.05, PLATE_T + 2)).volume < 1e-3
clash = (holder & (truck + stack)).volume        # docked truck touches the cradle but does not cut into it
assert clash < 0.05, clash
gap = holder.distance_to(bulb)
assert gap < 0.05, gap
assert holder.distance_to(stack) > 2.0, holder.distance_to(stack)   # nut and washer stay clear of the tongue

# ---- exports ----
print_part = Pos(0, 0, W / 2) * holder                # on its side: design z is print Z, bottom on Z = 0
STL = os.path.join(HERE, "skateboard-holder.stl")
export_stl(print_part, STL)
m = trimesh.load(STL)
assert m.is_watertight and abs(m.volume - holder.volume) < 80, (m.is_watertight, m.volume)
for name, shape in (("holder-design", holder), ("truck", truck), ("truck-block", truck_block), ("nut", stack),
                    ("wheels", wheels), ("deck", deck), ("bulb", bulb)):
    export_stl(shape, os.path.join(BUILD, f"{name}.stl"))

if __name__ == "__main__":
    print(f"deck underside {DECK_X:.1f} from the wall; cradle R{CRADLE_R:g} bottom at ({CRADLE_C[0]:.1f}, {y_top(CRADLE_C[0]):.1f}); "
          f"rims x {X_RIM_WALL:.1f} (y {Y_ROOT:.1f}) and {X_RIM_ROOM:.1f} (y {Y_RIM_ROOM:.1f}); "
          f"hold toward the room {HOLD_ROOM:.1f}, toward the wall {HOLD_WALL:.1f}, sideways {SAG:.2f}; "
          f"plate {PLATE_BOT:.1f}..{PLATE_TOP:.1f}; screws at {SCREW_YS[0]:.1f}, {SCREW_YS[1]:.1f}; "
          f"nut clearance {holder.distance_to(stack):.1f}; volume {holder.volume / 1000:.1f} cm3; "
          f"print box {m.extents.round(1)}; side chamfer {side_chamfer_ok}")
    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, set_port, show
        set_port(3939)
        show(holder, truck, stack, wheels, deck, names=["holder", "truck", "nut", "wheels", "deck"],
             colors=["#f28c28", "#aab2bc", "#f6c453", "#f3efe2", "#c9a06a"], alphas=[1, 1, 1, 0.5, 0.6],
             reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
