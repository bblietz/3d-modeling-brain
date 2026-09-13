"""Leader cards: flat PETG card for wrapping fishing leaders, plus the slot test coupon.

Spec: projects/Leader-cards/brief.md. Both parts print flat, chamfered edge on
the bed, 0.4 mm nozzle, PETG. The line wraps around the long (X) axis over the
two wavy short edges and locks in a hook-bend slot at each end. Every edge the
line can touch is rounded: the slot's outside corners in plan view, and the
slot walls where they meet the top (round) and bottom (chamfer) faces. On both
faces a 15 degree exit ramp runs from the pocket toward the wrap edge, so line
under wrap tension leaves the slot at a low angle instead of bending 90 degrees.

Run:  PART=coupon .venv/bin/python projects/Leader-cards/leader_card.py
      PART=card   .venv/bin/python projects/Leader-cards/leader_card.py
Env:  STAGE=1 builds only the blank with its wavy edges, STAGE=2 adds the slots, STAGE=3 (default)
      adds the card's recessed version label;
      a STAGE run exports a scratch STL (argv[1]) for the per-feature render.
      SHOW=1|reset pushes to the OCP viewer.
"""
import math
import os
import sys
import zipfile

from build123d import (Axis, Circle, Edge, Face, Kind, Mesher, Plane, Polygon, Pos, Rectangle, RectangleRounded, Rot,
                       Text, Vector, Wire, chamfer, export_stl, extrude, fillet, mirror, offset)

PROJECT = os.path.dirname(os.path.abspath(__file__))

# card
CARD_L = 76.2  # 3 in, along X; the line wraps over the short edges at x = +/- CARD_L / 2
CARD_W = 50.8  # 2 in
THICK = 3.0
CORNER_R = 2.9  # plan-view corner radius; leaves a 45.0 mm straight short edge, exactly 15 wave pitches
TOP_ROUND = 0.6  # every top edge, slot walls included; capped by the 1.09 mm wave peaks
BOT_CHAMFER = 0.6  # every bottom edge, 45 degrees, no feather lip at the bed

# wrap edge wave: alternating tangent arcs, rounded peaks and valleys
WAVE_PITCH = 3.0
WAVE_DEPTH = 0.6
WAVE_R = ((WAVE_PITCH / 2) ** 2 + WAVE_DEPTH ** 2) / (4 * WAVE_DEPTH)  # 1.0875

# corner lugs stand proud of the wrap edge so slack wraps cannot slide off its ends
LUG_H = 1.5  # how far the corners stand past the wave peaks; the overall size is unchanged
LUG_W = CORNER_R + WAVE_PITCH  # lug width along the edge, so its flank lands on a wave peak
LUG_ROUND = 0.8  # plan round where a lug flank meets the wave

# hook-bend slot, local frame: mouth on the long edge at the origin, lead-in runs +Y,
# pocket turns toward +X (the nearest short edge) and angles back toward the mouth
SLOT_INSET = 8.0  # lead-in centreline to the nearest short edge (card)
LEAD_DEPTH = 6.0  # lead-in depth for variants 1 to 4; each variant carries its own as lead_d
MOUTH_W = 2.4
FUNNEL = 1.0
MIN_WALL = 2.0  # pocket to long edge
R_PLAN = 0.8  # plan-view round on the slot's outside corners (hook tongue, funnel, mouth); must exceed TOP_ROUND
TIP_ROUND = 0.15  # pocket ends in this radius, a 0.3 mm gap, still narrower than 25 lb line
POCKET_PROBE = 1.5  # distance along the pocket where the open-slot probe sits

# exit ramp on both faces, from the pocket's exit wall (corner to tip) toward the wrap edge
RAMP_DEPTH = 0.7  # at the pocket wall, before the round; leaves about a 1.2 mm square pinch band
RAMP_ANGLE = 15.0  # degrees, along X, the direction the line leaves
RAMP_ROUND = 0.3  # round where the ramp meets the pocket wall, built into the cutter
MIN_BAND = 1.0  # square pinch band at mid-thickness must stay at least this tall
RAMP_MARGIN = 0.5  # ramp width past the outermost line stop
RAMP_START = 0.3  # cutter starts this far inside the pocket so it meets the wall cleanly
LINE_DIAS = (0.5, 0.7)  # 25 lb and 40 lb line

# coupon
COUPON_L = 52.0
COUPON_W = 17.8  # two exposed wave valleys between the corner lugs
COUPON_FIRST = 7.0  # first lead-in from the coupon's -X end, clear of the corner lug
COUPON_PITCH = 12.0

# exit +1: pocket and ramp point toward the nearest wrap edge; -1: mirrored, they point toward
# the card centre, the lead-in sits on the wrap-edge side, and wrap tension runs to the far edge
VARIANTS = [
    dict(lead_w=1.2, angle=30, pocket_w=1.0, lead_d=LEAD_DEPTH, pocket_l=4.5, exit=1),  # 1 brief baseline
    dict(lead_w=1.2, angle=30, pocket_w=0.8, lead_d=LEAD_DEPTH, pocket_l=4.5, exit=1),  # 2 tighter pocket
    dict(lead_w=1.2, angle=50, pocket_w=1.0, lead_d=LEAD_DEPTH, pocket_l=4.5, exit=1),  # 3 steeper hook
    dict(lead_w=1.6, angle=30, pocket_w=1.0, lead_d=LEAD_DEPTH, pocket_l=4.5, exit=1),  # 4 wider lead-in
    dict(lead_w=1.2, angle=30, pocket_w=1.0, lead_d=18.0, pocket_l=18.0, exit=-1),  # 5 mirrored, slot 3x longer (Brian 2026-09-12)
]
COUPON_SLOTS = (1, 2, 3, 4)  # variant numbers on the coupon, from its -X end
WINNER = 5  # variant 5 reversed, Brian 2026-09-12; printed directly, no coupon

NAMES = {"coupon": "leader-card-coupon", "card": "leader-card"}

# version label, recessed into the top face in the strip along the -Y long edge that the wraps never
# cover (they stay between the corner lugs); same material, so it reads by shadow
VERSION = "LC1"  # bump on every design change; the brief keeps the version log
LABEL_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LABEL_SIZE = 4.8  # font size (mm); the build fails if the text does not fit the strip
LABEL_DEPTH = 0.6  # three 0.2 mm layers
LABEL_X = -12.0  # label centre along the card, clear of the slot mouth near +X


def outline(length, width):
    """Rounded rectangle whose two short edges are a wave of tangent arcs."""
    xe, ye, cr, d, r = length / 2, width / 2, CORNER_R, WAVE_DEPTH, WAVE_R
    q = WAVE_PITCH / 4
    straight = width - 2 * cr
    n = round(straight / (2 * q)) - 1  # full arcs between the two half peaks
    assert abs((n + 1) * 2 * q - straight) < 1e-6 and n % 2 == 1, (straight, n)
    y0, y1 = -ye + cr, ye - cr
    phi = math.atan2(q, r - d / 2)  # sweep of the half peak at each end
    tan = lambda y: Vector(xe - d / 2, y)  # tangent points sit halfway down the wave
    k = math.sqrt(0.5)

    right = [Edge.make_three_point_arc(Vector(xe - cr, -ye), Vector(xe - cr + cr * k, y0 - cr * k), Vector(xe, y0))]
    right.append(Edge.make_three_point_arc(Vector(xe, y0), Vector(xe - r + r * math.cos(phi / 2), y0 + r * math.sin(phi / 2)), tan(y0 + q)))
    y = y0 + q
    for i in range(n):  # valley first, alternating, valley last
        right.append(Edge.make_three_point_arc(tan(y), Vector(xe - d if i % 2 == 0 else xe, y + q), tan(y + 2 * q)))
        y += 2 * q
    right.append(Edge.make_three_point_arc(tan(y), Vector(xe - r + r * math.cos(phi / 2), y1 - r * math.sin(phi / 2)), Vector(xe, y1)))
    right.append(Edge.make_three_point_arc(Vector(xe, y1), Vector(xe - cr + cr * k, y1 + cr * k), Vector(xe - cr, ye)))

    edges = [Edge.make_line(Vector(-xe + cr, -ye), Vector(xe - cr, -ye))]
    edges += right
    edges.append(Edge.make_line(Vector(xe - cr, ye), Vector(-xe + cr, ye)))
    edges += [Rot(0, 0, 180) * e for e in right]
    return Face(Wire(edges))


def pocket_points(v):
    """Pocket triangle, counterclockwise: lower base corner, tip, upper base corner.
    Clockwise winding flips the face normal and the extrude misses the part."""
    a = math.radians(v["angle"])
    u = (math.cos(a), -math.sin(a))
    n = (-u[1], u[0])
    pw = v["pocket_w"] / 2
    return (
        (-n[0] * pw, v["lead_d"] - n[1] * pw),
        (u[0] * v["pocket_l"], v["lead_d"] + u[1] * v["pocket_l"]),
        (n[0] * pw, v["lead_d"] + n[1] * pw),
    )


def slot_profile(v):
    hw, m = v["lead_w"] / 2, MOUTH_W / 2
    lead = Polygon((-m, -1), (m, -1), (m, 0), (hw, FUNNEL), (hw, v["lead_d"]),
                   (-hw, v["lead_d"]), (-hw, FUNNEL), (-m, 0), align=None)
    return lead + Pos(0, v["lead_d"]) * Circle(hw) + Polygon(*pocket_points(v), align=None)


def line_stops(v):
    """Local (x, y) where each line diameter wedges in the pocket taper."""
    a = math.radians(v["angle"])
    return [(math.cos(a) * s, v["lead_d"] - math.sin(a) * s)
            for s in (v["pocket_l"] * (1 - d / v["pocket_w"]) for d in LINE_DIAS)]


def ramp_geometry(v):
    """Exit wall x as a function of y (the pocket side from upper corner to tip),
    the ramp's y band, and its run length along X."""
    _, tip, upper = pocket_points(v)
    g = (tip[0] - upper[0]) / (tip[1] - upper[1])
    wall_x = lambda y: upper[0] + (y - upper[1]) * g
    ys = [p[1] for p in line_stops(v)]
    y_lo, y_hi = min(ys) - RAMP_MARGIN, upper[1] - 0.05
    assert y_lo > tip[1], ("ramp band runs past the pocket tip", v)
    run = RAMP_DEPTH / math.tan(math.radians(RAMP_ANGLE))
    return wall_x, y_lo, y_hi, run, g


def ramp_section(v):
    """The ramp across the exit wall: its slope in that section (steeper than
    RAMP_ANGLE, which is measured along X), the slope's secant, and the height
    where the square wall meets the round."""
    g = ramp_geometry(v)[4]
    kp = math.tan(math.radians(RAMP_ANGLE)) * math.sqrt(1 + g * g)
    sec = math.sqrt(1 + kp * kp)
    return kp, sec, THICK - RAMP_DEPTH + RAMP_ROUND * (kp - sec)


def ramp_cutter(v):
    """Top-face exit ramp in the slot's local frame. The section across the exit
    wall (square wall, RAMP_ROUND arc, ramp) is extruded along the wall and trimmed
    to the ramp band, so the round needs no fillet. Mirror about mid-thickness for
    the bottom face."""
    wall_x, y_lo, y_hi, run, g = ramp_geometry(v)
    kp, sec, zc = ramp_section(v)
    r, z0, top = RAMP_ROUND, THICK - RAMP_DEPTH, THICK + 1
    t2 = (r - r * kp / sec, zc + r / sec)  # where the arc meets the ramp
    bis = (-1 - kp / sec, 1 / sec)
    bl = math.hypot(*bis)
    mid = (r + r * bis[0] / bl, zc + r * bis[1] / bl)
    p_far = (top - z0) / kp
    P = lambda x, y: Vector(x, y)
    section = Face(Wire([
        Edge.make_line(P(-RAMP_START, zc), P(0, zc)),
        Edge.make_three_point_arc(P(0, zc), P(*mid), P(*t2)),
        Edge.make_line(P(*t2), P(p_far, top)),
        Edge.make_line(P(p_far, top), P(-RAMP_START, top)),
        Edge.make_line(P(-RAMP_START, top), P(-RAMP_START, zc)),
    ]))
    nl = math.sqrt(1 + g * g)  # section x runs across the wall toward +X, extrusion runs along the wall
    frame = Plane(origin=(wall_x(0), 0, 0), x_dir=(1 / nl, -g / nl, 0), z_dir=(-g / nl, -1 / nl, 0))
    body = extrude(frame.location * section, amount=30, both=True)

    x_far = wall_x(y_lo) + run + 0.2  # the ramp clears the top face before here at every y
    foot = Polygon((wall_x(y_lo) - RAMP_START, y_lo), (x_far, y_lo), (x_far, y_hi), (wall_x(y_hi) - RAMP_START, y_hi),
                   align=None)
    return body & (Pos(0, 0, -1) * extrude(foot, amount=THICK + 3))


def slot_places(which):
    """(mouth x, sign, variant): sign -1 is the slot turned 180 degrees onto the +Y edge."""
    if which == "coupon":
        return [(-COUPON_L / 2 + COUPON_FIRST + i * COUPON_PITCH, 1, VARIANTS[n - 1]) for i, n in enumerate(COUPON_SLOTS)]
    assert WINNER in range(1, len(VARIANTS) + 1), "set WINNER to the chosen variant before building the card"
    v = VARIANTS[WINNER - 1]
    return [(CARD_L / 2 - SLOT_INSET, 1, v), (-(CARD_L / 2 - SLOT_INSET), -1, v)]


def size(which):
    return (COUPON_L, COUPON_W) if which == "coupon" else (CARD_L, CARD_W)


def place(x0, s, width):
    return Pos(x0, -s * width / 2, 0) * Rot(0, 0, 0 if s > 0 else 180)


def oriented(shape, v):
    """Slot tools are drawn exiting toward local +X; a mirrored variant flips them across the lead-in."""
    return mirror(shape, about=Plane.YZ) if v["exit"] < 0 else shape


def card_outline(length, width):
    """The wavy outline set back LUG_H at each short end, with the four corners built back
    out to full size as lugs. Closing rounds the lug flanks into the wave, opening rounds
    the lug tips; both run before any slot is cut, since they would fill a narrow slot."""
    face = outline(length - 2 * LUG_H, width)
    full = RectangleRounded(length, width, CORNER_R)
    xa = length / 2 - LUG_H - 3.0  # lugs overlap the body by 3 mm so the union is clean
    for sx in (1, -1):
        for sy in (1, -1):
            lug = Pos(sx * (xa + length / 2) / 2, sy * (width - LUG_W) / 2) * Rectangle(length / 2 - xa, LUG_W)
            face += lug & full
    face = offset(offset(face, LUG_ROUND, kind=Kind.ARC), -LUG_ROUND, kind=Kind.ARC)
    return offset(offset(face, -R_PLAN, kind=Kind.ARC), R_PLAN, kind=Kind.ARC)


def plan_face(length, width, places=()):
    """Plan outline with the slots cut. Opening the face (shrink, then grow back by
    R_PLAN) rounds only the convex corners tighter than R_PLAN, which are the slot's
    tongue, funnel and mouth corners; the wave, card corners and pocket tip keep shape."""
    face = card_outline(length, width)
    for x0, s, v in places:
        face -= place(x0, s, width) * oriented(slot_profile(v), v)
    if places:
        # closing first (grow, then shrink back by TIP_ROUND) ends the pocket in a small radius:
        # at a sharp tip the rounds on the two pocket walls collide and the top round cannot build
        face = offset(offset(face, TIP_ROUND, kind=Kind.ARC), -TIP_ROUND, kind=Kind.ARC)
        face = offset(offset(face, -R_PLAN, kind=Kind.ARC), R_PLAN, kind=Kind.ARC)
    return face


def blank(length, width, places=()):
    part = extrude(plan_face(length, width, places), amount=THICK)
    part = fillet(part.edges().group_by(Axis.Z)[-1], TOP_ROUND)
    part = chamfer(part.edges().group_by(Axis.Z)[0], BOT_CHAMFER)
    if not places:
        return part
    for x0, s, v in places:
        top = oriented(ramp_cutter(v), v)
        part -= place(x0, s, width) * (top + mirror(top, about=Plane.XY.offset(THICK / 2)))
    return part


def label_sketch():
    """VERSION centred in the -Y edge strip: inside the edge round, outside the wrap zone."""
    y_lo = -CARD_W / 2 + TOP_ROUND + 0.5
    y_hi = -CARD_W / 2 + LUG_W - 0.5
    text = Text(VERSION, LABEL_SIZE, font_path=LABEL_FONT)
    c = text.bounding_box().center()
    text = Pos(LABEL_X - c.X, (y_lo + y_hi) / 2 - c.Y) * text
    bb = text.bounding_box()
    assert y_lo <= bb.min.Y and bb.max.Y <= y_hi, ("label does not fit the edge strip", bb.min, bb.max)
    return text


def build(which, stage=3):
    length, width = size(which)
    part = blank(length, width, slot_places(which) if stage >= 2 else ())
    if which == "card" and stage >= 3:
        part -= Pos(0, 0, THICK - LABEL_DEPTH) * extrude(label_sketch(), amount=LABEL_DEPTH + 1)
    return part


def check(part, which):
    length, width = size(which)
    assert len(part.solids()) == 1, "expected one solid"
    bb = part.bounding_box()
    assert abs(bb.size.X - length) < 0.01 and abs(bb.size.Y - width) < 0.01 and abs(bb.size.Z - THICK) < 0.01, bb.size
    assert abs(bb.min.Z) < 1e-6, "part must sit on the bed"

    places = slot_places(which)
    bands = []
    for idx, (x0, s, v) in enumerate(places):
        d = s * v["exit"]  # world X direction of the slot's local +X, where its pocket and ramp point
        world = lambda lx, ly, z=THICK / 2: Vector(x0 + d * lx, s * (-width / 2 + ly), z)
        pts = pocket_points(v)
        hw = v["lead_w"] / 2
        assert v["pocket_w"] <= v["lead_w"], v
        assert min(p[1] for p in pts) >= MIN_WALL, ("pocket wall", v)
        assert abs(x0 + d * pts[1][0]) <= length / 2 - LUG_H - WAVE_DEPTH - 2.0, ("pocket tip too near the wrap edge", v)
        a = math.radians(v["angle"])
        assert not part.is_inside(world(0, v["lead_d"] / 2)), ("lead-in closed", v)
        assert not part.is_inside(world(POCKET_PROBE * math.cos(a), v["lead_d"] - POCKET_PROBE * math.sin(a))), ("pocket closed", v)
        assert part.is_inside(world(2.0, 1.5)), ("no tongue between pocket and mouth", v)
        # the slot wall is square at mid-thickness but rounded away at both faces
        assert part.is_inside(world(hw + 0.1, v["lead_d"] / 2)), ("slot wall missing", v)
        for z in (THICK - 0.1, 0.1):
            assert not part.is_inside(world(hw + 0.1, v["lead_d"] / 2, z)), ("slot edge not rounded", v, z)

        # exit ramp: cut on both faces beside the exit wall, pinch band intact, face intact past the run
        wall_x, y_lo, y_hi, run, _ = ramp_geometry(v)
        ym = sum(p[1] for p in line_stops(v)) / 2
        for z in (THICK - 0.3, 0.3):
            assert not part.is_inside(world(wall_x(ym) + 0.5, ym, z)), ("exit ramp missing", v, z)
        assert part.is_inside(world(wall_x(ym) + 0.1, ym)), ("pinch band missing", v)
        for z in (THICK - 0.05, 0.05):
            assert part.is_inside(world(wall_x(ym) + run + 0.3, ym, z)), ("face not intact past the ramp", v, z)
        band = 2 * ramp_section(v)[2] - THICK
        assert band >= MIN_BAND, ("pinch band too thin", v, band)
        bands.append(band)
        far = wall_x(y_lo) + run + 0.2
        assert abs(x0 + d * far) <= length / 2 - LUG_H - WAVE_DEPTH - 0.3, ("ramp runs into the wrap edge", v)
        if which == "coupon":  # coupon slots share one edge; the card's are at opposite ends
            nxt = idx + (1 if d > 0 else -1)
            if 0 <= nxt < len(places):
                room = abs(places[nxt][0] - x0) - MOUTH_W / 2 - R_PLAN
                assert far <= room, ("ramp runs into the neighbouring slot", v)
                assert pts[1][0] + 2.0 <= room + R_PLAN, ("pocket too close to the neighbouring slot", v)

    valleys = round((width - 2 * LUG_W) / WAVE_PITCH)  # exposed between the corner lugs
    yb = -width / 2 + LUG_W
    xw = length / 2 - LUG_H - WAVE_DEPTH / 2
    for s in (1, -1):
        assert all(not part.is_inside(Vector(s * xw, s * (yb + WAVE_PITCH * (i + 0.5)), THICK / 2))
                   for i in range(valleys)), "wave valley filled"
        assert all(part.is_inside(Vector(s * xw, s * (yb + WAVE_PITCH * i), THICK / 2))
                   for i in range(valleys + 1)), "wave peak missing"
        for sy in (1, -1):
            assert part.is_inside(Vector(s * (length / 2 - 0.3), sy * (width / 2 - LUG_W / 2), THICK / 2)), "corner lug missing"
        assert not part.is_inside(Vector(s * (length / 2 - 0.3), 0, THICK / 2)), "wrap edge not set back behind the lugs"

    if which == "card":  # label: nothing left inside the letters, the floor under them intact, clear of the slot mouth
        text = label_sketch()
        letters = Pos(0, 0, THICK - LABEL_DEPTH) * extrude(text, amount=LABEL_DEPTH)
        floor = Pos(0, 0, THICK - LABEL_DEPTH - 0.3) * extrude(text, amount=0.3)
        assert letters.volume > 5 * LABEL_DEPTH, "label text is empty"
        assert (part & letters).volume < 1e-3, "label not recessed"
        assert abs((part & floor).volume - floor.volume) < 1e-3, "label floor not intact"
        mouth = min(abs(x0) for x0, _, _ in places) - MOUTH_W / 2 - R_PLAN
        assert text.bounding_box().max.X <= mouth - 2.0, "label too close to the slot mouth"

    # volume sanity: the slots remove at least their profile area times the thickness,
    # plus the ramps and the rounded corners and edges
    removed = blank(length, width).volume - part.volume
    expected = sum((slot_profile(v).area - MOUTH_W) * THICK for _, _, v in places)
    ratio = removed / expected
    assert 0.95 < ratio < 1.8, (removed, expected)
    return {"size": (round(bb.size.X, 3), round(bb.size.Y, 3), round(bb.size.Z, 3)), "volume_mm3": round(part.volume, 1),
            "valleys_per_edge": valleys, "slots": len(places), "slot_removal_ratio": round(ratio, 3),
            "pinch_band_mm": round(min(bands), 3), "label": VERSION if which == "card" else None}


def export(part, which):
    import trimesh

    length, width = size(which)
    stl = f"{PROJECT}/{NAMES[which]}.stl"
    threemf = f"{PROJECT}/{NAMES[which]}.3mf"
    export_stl(part, stl)
    m = Mesher()
    m.add_shape(part)
    m.write(threemf)

    mesh = trimesh.load_mesh(stl)
    assert mesh.is_watertight, "STL not watertight"
    ext = mesh.bounds[1] - mesh.bounds[0]
    assert abs(ext[0] - length) < 0.01 and abs(ext[1] - width) < 0.01 and abs(ext[2] - THICK) < 0.01, ext
    with zipfile.ZipFile(threemf) as z:
        model = z.read("3D/3dmodel.model").decode()
    assert model.count("<item ") == 1, "3MF should hold one build item"
    return stl, threemf


if __name__ == "__main__":
    which = os.environ.get("PART")
    assert which in NAMES, "set PART=coupon or PART=card"
    stage = int(os.environ.get("STAGE", "3"))
    part = build(which, stage)
    if "STAGE" in os.environ:
        out = sys.argv[1] if len(sys.argv) > 1 else f"/tmp/{NAMES[which]}-stage{stage}.stl"
        export_stl(part, out)
        print("stage", stage, "->", out, "bbox", part.bounding_box().size)
    else:
        report = check(part, which)
        stl, threemf = export(part, which)
        print("checks passed", report)
        print("exported", stl, threemf)

    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show

        show(part, names=[NAMES[which]], reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
