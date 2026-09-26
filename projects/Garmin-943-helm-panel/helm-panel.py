"""Helm panel for the Garmin GPSMAP 943xsv.

Two builds from one source, differing ONLY in thickness:
  default   one piece routed from 1/2 in (12.7 mm) black King Starboard
  TILES=1   four interlocking tiles printed in 3/8 in (9.525 mm) ASA

Replaces the hinged clear cover behind the wheel. The 943xsv flush mounts
through the window; the window and its pilot holes come from garmin_9x3.py,
the same numbers the router template uses.

PROVISIONAL: PANEL_W and PANEL_H are Brian's 2026-09-09 estimate (18.5 x 11.5
in). Exact measurements and photos to follow. Change those two constants and
the tiles, the joints and every check regenerate.

SPLIT: 469.9 x 292.1 mm does not fit the 256 mm bed in any orientation, and
292.1 > 256 forces a split in Y as well as X, so four tiles is the minimum.
The seams cross at the window, which is a hole, so no four tiles ever meet in
solid material. Tiles join with loose bowtie keys dropped in from the back:
a 2x2 grid cannot be assembled with integral dovetails, because each tile
would have to slide two directions at once.

Print each tile flat, FRONT FACE UP (the perimeter roundover is then a clean
top fillet, and the presentation face can be ironed). Keys print flat too.
ASA, not PLA: a dark panel at a helm passes the PLA softening point.

Run:  .venv/bin/python projects/Garmin-943-helm-panel/helm-panel.py
Env:  STAGE=n builds only the first n panel features (1..5). SHOW=1|reset
      pushes to the OCP viewer. TILES=1 builds the printed ASA panel at
      3/8 in: four interlocking tiles plus ten bowtie keys. TILES=1 never
      overwrites the routed one-piece STL/STEP.
"""
import os
import sys

from build123d import *

from garmin_9x3 import (
    BEZEL_OVER_BOTTOM,
    BEZEL_OVER_SIDE,
    BEZEL_OVER_TOP,
    CUTOUT_H,
    CUTOUT_W,
    HOLE_PITCH_X,
    HOLE_Y,
    PILOT_DRILL,
)

IN = 25.4

# Which build. TILES=1 is the printed ASA panel, anything else the routed
# Starboard one-piece. Thickness is the only geometric difference.
ASA = os.environ.get("TILES") == "1"

# ---- Panel, provisional until Brian measures ----
PANEL_W = 18.5 * IN  # 469.9
PANEL_H = 11.5 * IN  # 292.1
# HDPE is softer than printed ASA AND creeps, so Starboard needs one size up to
# reach the same deflection: 1/2 in Starboard lands where 3/8 in printed ASA
# does. Printing that extra 3.2 mm would cost a third more time and filament
# for stiffness the analysis says is not needed. See brief.md for the numbers.
PANEL_T = (0.375 if ASA else 0.5) * IN  # 9.525 ASA / 12.7 Starboard
CORNER_R = 0.5 * IN  # 12.7, ASSUMPTION: confirm against the old cover
EDGE_ROUND = 0.125 * IN  # 3.175, 1/8 in roundover on the front face only

# ---- Window ----
CUTOUT_R = 0.25 * IN / 2  # 3.175
CUTOUT_DY = 0.0  # positive moves the window toward the panel top
PILOT_DEPTH = 7.0 if ASA else 10.0  # blind, ~2.5 mm of stock left behind it

# ---- Split and interlock ----
BED = 256.0
BED_CLEAR = 6.0  # margin each side for a brim on ASA
SEAM_CHAMFER = 0.5  # front-face seam edges, so the joint reads as a panel line

KEY_L = 36.0  # bowtie length, across the seam
KEY_WAIST = 12.0  # width at the seam
KEY_END = 20.0  # width at the ends
KEY_DEPTH = 6.0  # pocket depth from the BACK face; 3.5 mm front skin at 3/8 in
KEY_CLEAR = 0.2  # per face, the vault's snug fit
KEY_T = KEY_DEPTH - 0.2  # key sits 0.2 mm below the back face

PROJECT = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Garmin-943-helm-panel"
NAME = "helm-panel"

# Guards, so changing PANEL_T fails loudly instead of quietly cutting through
assert KEY_DEPTH + 2.0 <= PANEL_T, "pocket leaves under 2 mm of front skin"
assert PILOT_DEPTH + 2.0 <= PANEL_T, "pilot leaves under 2 mm behind it"
assert EDGE_ROUND < PANEL_T / 2, "roundover eats more than half the thickness"

ON_BED = (Align.CENTER, Align.CENTER, Align.MIN)
CENTERED = (Align.CENTER, Align.CENTER, Align.CENTER)


# --------------------------------------------------------------- panel

def build(upto=5):
    # 1. blank
    part = Box(PANEL_W, PANEL_H, PANEL_T, align=ON_BED)
    if upto < 2:
        return part

    # 2. rounded corners
    part = fillet(part.edges().filter_by(Axis.Z), CORNER_R)
    if upto < 3:
        return part

    # 3. window, corners radiused as the router bit leaves them
    window = extrude(RectangleRounded(CUTOUT_W, CUTOUT_H, CUTOUT_R), PANEL_T + 2)
    part -= Pos(0, CUTOUT_DY, -1) * window
    if upto < 4:
        return part

    # 4. four blind pilots, on Garmin's offset pattern
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * HOLE_PITCH_X / 2, HOLE_Y[sy] + CUTOUT_DY
            part -= Pos(x, y, PANEL_T - PILOT_DEPTH) * Cylinder(
                PILOT_DRILL / 2, PILOT_DEPTH + 1, align=ON_BED
            )
    if upto < 5:
        return part

    # 5. roundover on the front face perimeter only; the window edge stays
    #    sharp and flat so the bezel gasket seats
    outer_top = part.faces().sort_by(Axis.Z)[-1].outer_wire().edges()
    part = fillet(outer_top, EDGE_ROUND)
    return part


# --------------------------------------------------- split and interlock

def _spread(a, b, n):
    """n evenly spaced positions strictly inside [a, b]."""
    return [a + (b - a) * (i + 1) / (n + 1) for i in range(n)]


# seam segments: the seams exist only where there is material, so the
# vertical seam lives in the top and bottom webs and the horizontal seam
# in the left and right webs. The window interrupts both.
WEB_TOP = (CUTOUT_DY + CUTOUT_H / 2, PANEL_H / 2)
WEB_BOTTOM = (-PANEL_H / 2, CUTOUT_DY - CUTOUT_H / 2)
WEB_LEFT = (-PANEL_W / 2, -CUTOUT_W / 2)
WEB_RIGHT = (CUTOUT_W / 2, PANEL_W / 2)

# (x, y, rotation) of every bowtie. rot 0 spans X (vertical seam),
# rot 90 spans Y (horizontal seam).
KEYS = (
    [(0.0, y, 0) for y in _spread(*WEB_TOP, 2)]
    + [(0.0, y, 0) for y in _spread(*WEB_BOTTOM, 2)]
    + [(x, 0.0, 90) for x in _spread(*WEB_LEFT, 3)]
    + [(x, 0.0, 90) for x in _spread(*WEB_RIGHT, 3)]
)


def bowtie(shrink=0.0):
    """Bowtie profile, waist on the seam. Spans X, centred on the origin."""
    hl, hw, he = KEY_L / 2, KEY_WAIST / 2, KEY_END / 2
    pts = [(-hl, -he), (0, -hw), (hl, -he), (hl, he), (0, hw), (-hl, he)]
    face = make_face(Polyline(*pts, close=True))
    return offset(face, -shrink) if shrink else face


def cut_pockets(panel):
    """Bowtie pockets in the BACK face (z=0), straddling every seam."""
    for x, y, rot in KEYS:
        panel -= Pos(x, y, -1) * Rot(0, 0, rot) * extrude(bowtie(), KEY_DEPTH + 1)
    return panel


def key_part():
    return extrude(bowtie(KEY_CLEAR), KEY_T)


def split(panel):
    """Four quadrant tiles, still in panel coordinates."""
    big = 4 * max(PANEL_W, PANEL_H)
    out = {}
    for name, sx, sy in (("TL", -1, 1), ("TR", 1, 1), ("BL", -1, -1), ("BR", 1, -1)):
        hx = Pos(sx * big / 2, 0, 0) * Box(big, 2 * big, big, align=CENTERED)
        hy = Pos(0, sy * big / 2, 0) * Box(2 * big, big, big, align=CENTERED)
        out[name] = panel & hx & hy
    return out


def _on_seam(edge, axis):
    a, b = edge @ 0, edge @ 1
    return abs(getattr(a, axis)) < 1e-6 and abs(getattr(b, axis)) < 1e-6


def chamfer_seam(tile):
    """Break the front-face seam edges so the joint reads as a panel line."""
    top = tile.faces().sort_by(Axis.Z)[-1]
    es = [e for e in top.edges() if _on_seam(e, "X") or _on_seam(e, "Y")]
    if not es:
        return tile, 0
    return chamfer(es, SEAM_CHAMFER), len(es)


def to_print_pose(tile):
    """Recentre a tile over the origin, sitting on z=0, front face up."""
    bb = tile.bounding_box()
    return Pos(-bb.center().X, -bb.center().Y, 0) * tile


# ------------------------------------------------------------- checks

def probe_volume(part, solid):
    hit = part & solid
    return hit.volume if hit and hit.volume else 0.0


def check_panel(part):
    size = part.bounding_box().size
    assert abs(size.X - PANEL_W) < 1e-3 and abs(size.Y - PANEL_H) < 1e-3, size
    assert abs(size.Z - PANEL_T) < 1e-3, size
    assert len(part.solids()) == 1, len(part.solids())

    small = Pos(0, CUTOUT_DY, 1) * extrude(
        RectangleRounded(CUTOUT_W - 0.1, CUTOUT_H - 0.1, CUTOUT_R), PANEL_T - 2
    )
    assert probe_volume(part, small) < 1e-6, "window undersize"
    big = Pos(0, CUTOUT_DY, 1) * extrude(
        RectangleRounded(CUTOUT_W + 0.1, CUTOUT_H + 0.1, CUTOUT_R), PANEL_T - 2
    )
    assert probe_volume(part, big) > 1.0, "window oversize"
    sq = Pos(CUTOUT_W / 2 - 0.4, CUTOUT_DY + CUTOUT_H / 2 - 0.4, PANEL_T / 2) * Box(
        0.5, 0.5, 1, align=CENTERED
    )
    assert probe_volume(part, sq) > 0.2, "window corner not radiused"

    for sx in (-1, 1):
        for sy in (-1, 1):
            tip = Pos(sx * (PANEL_W / 2 - 1), sy * (PANEL_H / 2 - 1), PANEL_T / 2) * Box(
                1, 1, 1, align=CENTERED
            )
            assert probe_volume(part, tip) < 1e-6, "corner not rounded"
            x, y = sx * HOLE_PITCH_X / 2, HOLE_Y[sy] + CUTOUT_DY
            bore = Pos(x, y, PANEL_T - PILOT_DEPTH + 0.05) * Cylinder(
                PILOT_DRILL / 2 - 0.05, PILOT_DEPTH - 0.05, align=ON_BED
            )
            assert probe_volume(part, bore) < 1e-6, "pilot blocked"
            behind = Pos(x, y, 0) * Cylinder(PILOT_DRILL / 2, PANEL_T - PILOT_DEPTH - 0.1, align=ON_BED)
            assert probe_volume(part, behind) > 1e-3, "pilot breaks through the back"

    margins = {
        "side": PANEL_W / 2 - (CUTOUT_W / 2 + BEZEL_OVER_SIDE),
        "top": PANEL_H / 2 - (CUTOUT_DY + CUTOUT_H / 2 + BEZEL_OVER_TOP),
        "bottom": PANEL_H / 2 + (CUTOUT_DY - CUTOUT_H / 2 - BEZEL_OVER_BOTTOM),
    }
    for k, v in margins.items():
        assert v > 20.0, f"only {v:.1f} mm of panel beyond the bezel at {k}"
    return margins


def check_tiles(tiles, key, panel_volume, raw_volume):
    report = {}
    total = 0.0
    for name, t in tiles.items():
        assert len(t.solids()) == 1, f"{name} is {len(t.solids())} solids, not one"
        size = t.bounding_box().size
        assert size.X <= BED - 2 * BED_CLEAR, f"{name} too wide for the bed: {size.X:.1f}"
        assert size.Y <= BED - 2 * BED_CLEAR, f"{name} too deep for the bed: {size.Y:.1f}"
        assert abs(size.Z - PANEL_T) < 1e-3, f"{name} wrong thickness"
        total += t.volume
        report[name] = (round(size.X, 1), round(size.Y, 1))

    # before chamfering, the four tiles account for the whole panel less the
    # pockets, exactly. A butt split adds and removes nothing else.
    pockets = len(KEYS) * bowtie().area * KEY_DEPTH
    assert abs((raw_volume + pockets) - panel_volume) < 1.0, (raw_volume + pockets, panel_volume)

    # chamfering the seams then removes a small, predictable sliver: a 45 deg
    # triangle of SEAM_CHAMFER^2/2 along every seam edge on every tile.
    seam_len = 2 * (2 * (PANEL_H / 2 - CUTOUT_DY - CUTOUT_H / 2)) + 2 * (2 * (PANEL_W / 2 - CUTOUT_W / 2))
    expect = seam_len * SEAM_CHAMFER**2 / 2
    removed = raw_volume - total
    assert 0.8 * expect < removed < 1.5 * expect, (removed, expect)
    report["seam_chamfer_mm3"] = round(removed, 1)

    # every pocket half is real material removed, and none reaches the front face
    for x, y, rot in KEYS:
        at_waist = Pos(x, y, KEY_DEPTH / 2) * Box(2, 2, 2, align=CENTERED)
        assert probe_volume(sum_solids(tiles), at_waist) < 1e-6, "pocket missing"
        skin = Pos(x, y, PANEL_T - (PANEL_T - KEY_DEPTH) / 2) * Box(2, 2, PANEL_T - KEY_DEPTH - 0.2, align=CENTERED)
        got = probe_volume(sum_solids(tiles), skin)
        assert got > 0.9 * 2 * 2 * (PANEL_T - KEY_DEPTH - 0.2), "pocket broke the front skin"

    # The key is a true perpendicular offset of the pocket, so the gap is
    # KEY_CLEAR on every face. (Its bounding box shrinks by MORE than that at
    # the corners, which is why this is not a bounding-box check.)
    pocket_f, key_f = bowtie(), bowtie(KEY_CLEAR)
    outside = key_f - pocket_f
    assert (outside.area if outside else 0.0) < 1e-6, "key not inside the pocket footprint"
    perim = sum(e.length for e in pocket_f.edges())
    delta = pocket_f.area - key_f.area
    assert abs(delta - perim * KEY_CLEAR) < 0.05 * perim * KEY_CLEAR, (delta, perim * KEY_CLEAR)
    assert key.bounding_box().size.Z < KEY_DEPTH, "key stands proud of the back face"

    # the real test: drop every key into its actual pocket in the actual
    # tiles and confirm it touches nothing
    solid = sum_solids(tiles)
    for x, y, rot in KEYS:
        placed = Pos(x, y, 0) * Rot(0, 0, rot) * key
        assert probe_volume(solid, placed) < 1e-6, f"key at {x:.0f},{y:.0f} fouls the tiles"
        # and it spans the seam, so it actually ties two tiles together
        assert placed.bounding_box().min.X < -1 and placed.bounding_box().max.X > 1 if rot == 0 else True

    kb = key.bounding_box().size
    report["front_skin_mm"] = round(PANEL_T - KEY_DEPTH, 2)
    report["keys"] = len(KEYS)
    report["key_mm"] = (round(kb.X, 2), round(kb.Y, 2), round(kb.Z, 2))
    report["key_gap_mm"] = KEY_CLEAR
    return report


def sum_solids(tiles):
    it = iter(tiles.values())
    acc = next(it)
    for t in it:
        acc = acc + t
    return acc


# ------------------------------------------------------------- exports

def export(part, name):
    stl = f"{PROJECT}/{name}.stl"
    export_stl(part, stl)
    import trimesh

    mesh = trimesh.load_mesh(stl)
    assert mesh.is_watertight, f"{name} STL not watertight"
    return stl


if __name__ == "__main__":
    stage = int(os.environ.get("STAGE", "5"))
    panel = build(stage)

    if stage < 5:
        out = sys.argv[1] if len(sys.argv) > 1 else f"/tmp/{NAME}-stage{stage}.stl"
        export_stl(panel, out)
        print("stage", stage, "->", out, "bbox", panel.bounding_box().size)
        raise SystemExit

    margins = check_panel(panel)
    panel_volume = panel.volume
    print("panel ok  %.1f x %.1f x %.2f mm  %.0f cm3  (%s)"
          % (PANEL_W, PANEL_H, PANEL_T, panel_volume / 1000, "ASA tiles" if ASA else "Starboard"))
    print("  bezel margin mm:", {k: round(v, 1) for k, v in margins.items()})

    # The routed Starboard one-piece is the deliverable, so it alone owns
    # helm-panel.stl/.step. Under TILES=1 the one-piece is only an intermediate
    # at ASA thickness and must NOT overwrite those files.
    if not ASA:
        export_step(panel, f"{PROJECT}/{NAME}.step")
        export(panel, NAME)
        raise SystemExit

    pocketed = cut_pockets(panel)
    tiles = split(pocketed)
    raw_volume = sum(t.volume for t in tiles.values())
    chamfered = {}
    for name, t in tiles.items():
        t, n = chamfer_seam(t)
        chamfered[name] = t
        print(f"  {name}: {n} seam edges chamfered")
    tiles = chamfered

    key = key_part()
    report = check_tiles(tiles, key, panel_volume, raw_volume)
    print("tiles ok", report)

    for name, t in tiles.items():
        export(to_print_pose(t), f"{NAME}-tile-{name}")
    export(key, f"{NAME}-key")
    export_step(sum_solids(tiles), f"{PROJECT}/{NAME}-tiles.step")
    print("exported 4 tiles + key to", PROJECT)

    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show

        show(
            *tiles.values(),
            names=list(tiles),
            reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP,
        )
