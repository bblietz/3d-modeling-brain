"""Leader card LC3: flat PETG card for wrapping fishing leaders.

Spec: projects/Leader-cards/brief.md (LC2 decisions). Prints flat, chamfered edge on
the bed, 0.4 mm nozzle, PETG. Both wrap edges are a comb of identical straight
tapered slots, 3/8 in deep, from a 1.2 mm mouth to closed, and the +Y long edge has
three of the same slots at 25, 50 and 75 percent of the length for starting and
finishing the leader. Each line size wedges at its own depth, 10 lb deepest. Slot face edges are
rounded (0.6 mm top round, 0.6 mm bottom chamfer), and slot mouths and comb tooth
tips are rounded in plan. A recessed version label sits in the long-edge strip that
the wraps never cross, plus a recessed "leader" / "board" wordmark filling most of the
open interior between the two combs. The wordmark was picked from four to-scale
options on a comparison page (prototype/text_options.py); Brian chose the tight,
maximal-scale layout at 80% of the width that layout could fully fill. LC1 (hook
slots, wavy edges) is in git history and prototype/.

Run:  .venv/bin/python projects/Leader-cards/leader_card.py
Env:  STAGE=1 builds only the blank, STAGE=2 adds the slots, STAGE=3 adds the small
      reference label, STAGE=4 (default) adds the "leader board" wordmark; a STAGE
      run exports a scratch STL (argv[1]) for the per-feature render.
      SHOW=1|reset pushes to the OCP viewer.
Out:  leader-card-<VERSION>.stl and .3mf; then make_plate.py leader-card-<VERSION>.
"""
import math
import os
import sys
import zipfile

from build123d import (Axis, Kind, Mesher, Polygon, Pos, RectangleRounded, Rot, Text, Vector, chamfer, export_stl,
                       extrude, fillet, offset)

PROJECT = os.path.dirname(os.path.abspath(__file__))
IN = 25.4

VERSION = "LC3"  # file/version-log identifier AND the on-card recessed reference text; bump both
                  # together on every design change, see the brief's version log
NAME = f"leader-card-{VERSION}"

# card
CARD_L = 3 * IN  # along X; the line wraps over the short (wrap) edges at x = +/- CARD_L / 2
CARD_W = 1.5 * IN
THICK = 3.0
CORNER_R = 2.9
TOP_ROUND = 0.6  # every top edge, slot walls included
BOT_CHAMFER = 0.6  # every bottom edge, 45 degrees, no feather lip at the bed
R_PLAN = 0.8  # plan round on slot mouths and comb tooth tips; must exceed TOP_ROUND

# slots: one taper everywhere
SLOT_D = 3 / 8 * IN
SLOT_W = 1.2  # mouth width, tapering to closed at SLOT_D
TIP_ROUND = 0.1  # the taper ends in a 0.2 mm gap, narrower than 10 lb line; a sharp end stops the top round building
COMB_PITCH = 3.0
COMB_N = 9  # per wrap edge, as many as fit between the label strips
SIDE_SLOTS = (0.25, 0.50, 0.75)  # fractions of the length along the +Y long edge, opposite the label
LINES = {"10 lb": 0.28, "25 lb": 0.50, "40 lb": 0.70}  # typical mono diameters, mm

# version label, recessed into the top face in the -Y long-edge strip outside the comb's span
LABEL_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LABEL_SIZE = 4.8  # font size, mm; the build fails if the text does not fit the strip
LABEL_DEPTH = 0.6  # three 0.2 mm layers
LABEL_X = 0.0  # label centred along the card

# "leader board" wordmark: the tight-leading, even-weight layout from the comparison page,
# scaled to 80% of the width that layout could fill (Brian, 2026-09-12: "go with 4, but
# reduce the font by 20%"). Same font and recess depth as the small reference label.
WORDMARK_FONT = LABEL_FONT
WORDMARK_GAP_FRAC = 0.08  # tight leading: lines almost touching
WORDMARK_SCALE = 0.8  # of the full interior clear width, matching Brian's "reduce by 20%"
WORDMARK_TARGET_W = WORDMARK_SCALE * (CARD_L - 2 * SLOT_D)
WORDMARK_MARGIN = 1.0  # clearance kept above the reference label and below the side-slot band
WORDMARK_DEPTH = LABEL_DEPTH
LABEL_STRIP_TOP = CARD_W / 2 - (max((i - (COMB_N - 1) / 2) * COMB_PITCH for i in range(COMB_N)) + SLOT_W / 2) - 0.5  # strip top, measured up from the -Y edge


def taper():
    """One slot in its own frame: mouth on the X axis, running +Y into the card, closed at SLOT_D."""
    h = SLOT_W / 2
    return Polygon((-h, -1), (h, -1), (h, 0), (0, SLOT_D), (-h, 0), align=None)


def stop_depth(dia):
    """Depth from the mouth where a line of this diameter wedges."""
    return SLOT_D * (1 - dia / SLOT_W)


def comb_ys():
    return [(i - (COMB_N - 1) / 2) * COMB_PITCH for i in range(COMB_N)]


def slot_places():
    """(mouth x, mouth y, rotation) per slot; the rotation turns the slot's local +Y into the card."""
    places = [(CARD_L / 2, y, 90) for y in comb_ys()] + [(-CARD_L / 2, y, -90) for y in comb_ys()]
    return places + [(-CARD_L / 2 + f * CARD_L, CARD_W / 2, 180) for f in SIDE_SLOTS]


def plan_face(slots=True):
    face = RectangleRounded(CARD_L, CARD_W, CORNER_R)
    if not slots:
        return face
    for x, y, r in slot_places():
        face -= Pos(x, y) * Rot(0, 0, r) * taper()
    # closing ends each taper in TIP_ROUND; opening rounds the mouths and tooth tips to R_PLAN
    face = offset(offset(face, TIP_ROUND, kind=Kind.ARC), -TIP_ROUND, kind=Kind.ARC)
    return offset(offset(face, -R_PLAN, kind=Kind.ARC), R_PLAN, kind=Kind.ARC)


def label_sketch():
    """VERSION centred in the -Y edge strip: inside the edge round, outside the comb's span."""
    y_lo = -CARD_W / 2 + TOP_ROUND + 0.5
    y_hi = -CARD_W / 2 + LABEL_STRIP_TOP
    text = Text(VERSION, LABEL_SIZE, font_path=LABEL_FONT)
    c = text.bounding_box().center()
    text = Pos(LABEL_X - c.X, (y_lo + y_hi) / 2 - c.Y) * text
    bb = text.bounding_box()
    assert y_lo <= bb.min.Y and bb.max.Y <= y_hi, ("label does not fit the edge strip", bb.min, bb.max)
    return text


def wordmark_sketch():
    """'leader' over 'board', tight leading, both at the font size that fills WORDMARK_TARGET_W.
    Centred in the band between the small version label and the side-slot band (conservative: this
    stays clear of all three side slots regardless of x, not just the one at x=0)."""
    probe = Text("leader", 10, font_path=WORDMARK_FONT)
    fs = 10 * WORDMARK_TARGET_W / probe.bounding_box().size.X
    top, bot = Text("leader", fs, font_path=WORDMARK_FONT), Text("board", fs, font_path=WORDMARK_FONT)
    ht, hb = top.bounding_box().size.Y, bot.bounding_box().size.Y
    gap = WORDMARK_GAP_FRAC * (ht + hb) / 2
    total_h = ht + gap + hb

    y_lo = label_sketch().bounding_box().max.Y + WORDMARK_MARGIN
    y_hi = (CARD_W / 2 - SLOT_D) - WORDMARK_MARGIN
    assert total_h <= y_hi - y_lo, ("wordmark too tall for the clear band", total_h, y_hi - y_lo)
    y0 = (y_lo + y_hi) / 2

    yt = y0 + (total_h / 2 - ht / 2)
    yb = y0 - (total_h / 2 - hb / 2)
    top = Pos(-top.bounding_box().center().X, yt - top.bounding_box().center().Y) * top
    bot = Pos(-bot.bounding_box().center().X, yb - bot.bounding_box().center().Y) * bot
    return top + bot


def build(stage=4):
    part = extrude(plan_face(slots=stage >= 2), amount=THICK)
    part = fillet(part.edges().group_by(Axis.Z)[-1], TOP_ROUND)
    part = chamfer(part.edges().group_by(Axis.Z)[0], BOT_CHAMFER)
    if stage >= 3:
        part -= Pos(0, 0, THICK - LABEL_DEPTH) * extrude(label_sketch(), amount=LABEL_DEPTH + 1)
    if stage >= 4:
        part -= Pos(0, 0, THICK - WORDMARK_DEPTH) * extrude(wordmark_sketch(), amount=WORDMARK_DEPTH + 1)
    return part


def check(part):
    assert len(part.solids()) == 1, "expected one solid"
    bb = part.bounding_box()
    assert abs(bb.size.X - CARD_L) < 0.01 and abs(bb.size.Y - CARD_W) < 0.01 and abs(bb.size.Z - THICK) < 0.01, bb.size
    assert abs(bb.min.Z) < 1e-6, "part must sit on the bed"

    # layout
    assert COMB_PITCH - SLOT_W >= 2 * R_PLAN, "comb teeth narrower than their plan rounds"
    assert max(comb_ys()) + SLOT_W / 2 + R_PLAN <= CARD_W / 2 - CORNER_R, "comb runs into the corner round"
    side_x = [abs(-CARD_L / 2 + f * CARD_L) for f in SIDE_SLOTS]
    assert max(side_x) + SLOT_W / 2 + R_PLAN <= CARD_L / 2 - SLOT_D - 2.0, "side slot too close to a comb"
    assert CARD_W / 2 - SLOT_D >= -CARD_W / 2 + LABEL_STRIP_TOP + 2.0, "side slot reaches the label strip"
    closed = SLOT_D * (1 - 2 * TIP_ROUND / SLOT_W)  # depth where the taper's closed end begins
    thinnest = min(LINES.values())
    assert stop_depth(thinnest) <= closed - 0.3, "thinnest line would reach the closed end"

    # every slot: open at the mouth and where the thinnest line stops, solid past its end,
    # square wall at mid-thickness, rounded away at both faces
    wall = SLOT_W / 2 * (1 - 2.0 / SLOT_D) + 0.1  # 0.1 mm inside the wall, 2 mm deep
    for x, y, r in slot_places():
        c, s = math.cos(math.radians(r)), math.sin(math.radians(r))
        at = lambda lx, ly, z=THICK / 2: Vector(x + lx * c - ly * s, y + lx * s + ly * c, z)
        assert not part.is_inside(at(0, 1.0)), ("slot mouth closed", x, y)
        assert not part.is_inside(at(0, stop_depth(thinnest))), ("slot closed before the thinnest line stops", x, y)
        assert part.is_inside(at(0, SLOT_D + 0.5)), ("slot runs past its depth", x, y)
        assert part.is_inside(at(wall, 2.0)), ("slot wall missing", x, y)
        for z in (THICK - 0.1, 0.1):
            assert not part.is_inside(at(wall, 2.0, z)), ("slot face edge not rounded", x, y, z)
    ys = comb_ys()
    for sx in (1, -1):
        for ym in [(a + b) / 2 for a, b in zip(ys, ys[1:])]:
            assert part.is_inside(Vector(sx * (CARD_L / 2 - 1.5), ym, THICK / 2)), ("comb tooth missing", sx, ym)

    # label: nothing left inside the letters, the floor under them intact, clear of the combs
    text = label_sketch()
    letters = Pos(0, 0, THICK - LABEL_DEPTH) * extrude(text, amount=LABEL_DEPTH)
    floor = Pos(0, 0, THICK - LABEL_DEPTH - 0.3) * extrude(text, amount=0.3)
    assert letters.volume > 5 * LABEL_DEPTH, "label text is empty"
    assert (part & letters).volume < 1e-3, "label not recessed"
    assert abs((part & floor).volume - floor.volume) < 1e-3, "label floor not intact"
    lb = text.bounding_box()
    assert max(abs(lb.min.X), abs(lb.max.X)) <= CARD_L / 2 - SLOT_D - 2.0, "label runs into a comb"

    # wordmark: same checks as the label, plus a real overlap test against every slot cut
    # (the label check above already confirms the wordmark clears the label's own footprint,
    # since wordmark_sketch() is built above label_sketch()'s top edge with WORDMARK_MARGIN)
    word = wordmark_sketch()
    wletters = Pos(0, 0, THICK - WORDMARK_DEPTH) * extrude(word, amount=WORDMARK_DEPTH)
    wfloor = Pos(0, 0, THICK - WORDMARK_DEPTH - 0.3) * extrude(word, amount=0.3)
    assert wletters.volume > 50 * WORDMARK_DEPTH, "wordmark text is empty"
    assert (part & wletters).volume < 1e-3, "wordmark not recessed"
    assert abs((part & wfloor).volume - wfloor.volume) < 1e-3, "wordmark floor not intact"
    assert (word - plan_face()).area < 1e-6, "wordmark overlaps a slot cut"

    # volume sanity: the slots remove at least their taper area times the thickness, plus the
    # mouth rounds, edge rounds, label and wordmark
    removed = build(stage=1).volume - part.volume
    expected = len(slot_places()) * 0.5 * SLOT_W * SLOT_D * THICK
    ratio = removed / expected
    assert 0.9 < ratio < 2.0, (removed, expected)
    return {"size": (round(bb.size.X, 3), round(bb.size.Y, 3), round(bb.size.Z, 3)), "volume_mm3": round(part.volume, 1),
            "slots": len(slot_places()), "comb_per_edge": COMB_N, "removal_ratio": round(ratio, 3),
            "stops_mm": {k: round(stop_depth(d), 2) for k, d in LINES.items()}, "label": VERSION}


def export(part):
    import trimesh

    stl = f"{PROJECT}/{NAME}.stl"
    threemf = f"{PROJECT}/{NAME}.3mf"
    export_stl(part, stl)
    m = Mesher()
    m.add_shape(part)
    m.write(threemf)

    mesh = trimesh.load_mesh(stl)
    assert mesh.is_watertight, "STL not watertight"
    ext = mesh.bounds[1] - mesh.bounds[0]
    assert abs(ext[0] - CARD_L) < 0.01 and abs(ext[1] - CARD_W) < 0.01 and abs(ext[2] - THICK) < 0.01, ext
    with zipfile.ZipFile(threemf) as z:
        model = z.read("3D/3dmodel.model").decode()
    assert model.count("<item ") == 1, "3MF should hold one build item"
    return stl, threemf


if __name__ == "__main__":
    stage = int(os.environ.get("STAGE", "4"))
    part = build(stage)
    if "STAGE" in os.environ:
        out = sys.argv[1] if len(sys.argv) > 1 else f"/tmp/{NAME}-stage{stage}.stl"
        export_stl(part, out)
        print("stage", stage, "->", out, "bbox", part.bounding_box().size)
    else:
        report = check(part)
        stl, threemf = export(part)
        print("checks passed", report)
        print("exported", stl, threemf)

    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show

        show(part, names=[NAME], reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
