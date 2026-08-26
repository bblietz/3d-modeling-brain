"""Dining table for 6 - Shaker style with corner-brace joinery.

Tapered legs; square-ended aprons pulled tight by 45-degree corner
braces with hanger bolts into the legs (knock-down base). Breadboard-
ended top held by buttons in apron grooves. Hardwood (red oak assumed).
Floor at Z=0, length along X, centered at origin.
"""
import os
import sys
from build123d import *

# --- Locked design constants (mm) ---
TABLE_H = 740
TOP_T = 26               # 5/4 stock, dressed
TOP_L = 1800
TOP_W = 900
BREADBOARD_W = 70        # per end; glued panel is 1660 long
PANEL_L = TOP_L - 2 * BREADBOARD_W

LEG_SQ = 80              # square at top (8/4 glue-up milled to size)
FOOT_SQ = 48             # square at floor after two-face taper
LEG_H = TABLE_H - TOP_T  # 714

INSET = 40               # top overhang past leg outer faces
REVEAL = 12              # apron face set back from leg outer face
APRON_T = 22             # 4/4 stock, dressed heavy
APRON_W = 100

BRACE_T = 22             # 4/4 stock, on edge across the corner
BRACE_H = 60
BRACE_GAP = 6            # leg corner to brace face (bolt pulls across it)

GROOVE = 6               # button groove: square section, inner apron face
GROOVE_TOP_DROP = 12     # groove top this far below apron/leg top
TONGUE_T = 12            # breadboard tongue thickness
TONGUE_STOP = 30         # tongue stops this far from each top edge

TAPER_DROP = 20          # taper starts this far below apron bottom

FRAME_X = TOP_L - 2 * INSET             # 1720
FRAME_Y = TOP_W - 2 * INSET             # 820
LONG_APRON_L = FRAME_X - 2 * LEG_SQ     # 1560, butt ends at leg faces
SHORT_APRON_L = FRAME_Y - 2 * LEG_SQ    # 660
APRON_TOP = LEG_H
APRON_BOT = APRON_TOP - APRON_W         # 614
TAPER_START = APRON_BOT - TAPER_DROP    # 594
KNEE_MIN = 610

apron_center_off = REVEAL + APRON_T / 2  # apron centerline from leg outer face
SQ2 = 2 ** 0.5


def tapered_leg(sx, sy):
    """Leg for corner (sx, sy in +-1): outer faces plumb, inner tapered."""
    ox, oy = sx * FRAME_X / 2, sy * FRAME_Y / 2  # outer corner
    leg = Box(LEG_SQ, LEG_SQ, LEG_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    leg = Pos(ox - sx * LEG_SQ / 2, oy - sy * LEG_SQ / 2, 0) * leg
    cut = LEG_SQ - FOOT_SQ
    # taper wedges span the whole frame; they only cut this leg's box
    inner_x = ox - sx * LEG_SQ
    wedge_x = extrude(make_face(Plane.XZ * Polyline(
        (inner_x, TAPER_START), (inner_x, 0), (inner_x + sx * cut, 0),
        (inner_x, TAPER_START))), amount=FRAME_Y, dir=(0, 1, 0), both=True)
    inner_y = oy - sy * LEG_SQ
    wedge_y = extrude(make_face(Plane.YZ * Polyline(
        (inner_y, TAPER_START), (inner_y, 0), (inner_y + sy * cut, 0),
        (inner_y, TAPER_START))), amount=FRAME_X, dir=(1, 0, 0), both=True)
    return leg - wedge_x - wedge_y


legs = [tapered_leg(sx, sy) for sx in (-1, 1) for sy in (-1, 1)]


def apron(length, along_x, center_line):
    """Square-ended apron on edge with the button groove, no tenons."""
    if along_x:
        a = Box(length, APRON_T, APRON_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
        groove_y = -APRON_T / 2 if center_line > 0 else APRON_T / 2
        groove = Box(length, 2 * GROOVE, GROOVE,
                     align=(Align.CENTER, Align.CENTER, Align.MAX))
        groove = Pos(0, groove_y, APRON_W - GROOVE_TOP_DROP) * groove
        return Pos(0, center_line, APRON_BOT) * (a - groove)
    a = Box(APRON_T, length, APRON_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
    groove_x = -APRON_T / 2 if center_line > 0 else APRON_T / 2
    groove = Box(2 * GROOVE, length, GROOVE,
                 align=(Align.CENTER, Align.CENTER, Align.MAX))
    groove = Pos(groove_x, 0, APRON_W - GROOVE_TOP_DROP) * groove
    return Pos(center_line, 0, APRON_BOT) * (a - groove)


long_apron_y = FRAME_Y / 2 - apron_center_off
short_apron_x = FRAME_X / 2 - apron_center_off
long_aprons = [apron(LONG_APRON_L, True, y) for y in (-long_apron_y, long_apron_y)]
short_aprons = [apron(SHORT_APRON_L, False, x) for x in (-short_apron_x, short_apron_x)]

# --- Corner braces: 45-degree bars bearing on both apron inner faces ---
# The interior prism bounded by the apron inner faces trims the raw bar
# to flush 45-degree bearing ends.
interior = Pos(0, 0, 500) * Box(2 * (short_apron_x - APRON_T / 2),
                                2 * (long_apron_y - APRON_T / 2), 400,
                                align=(Align.CENTER, Align.CENTER, Align.MIN))
BRACE_Z = APRON_TOP - BRACE_H / 2

braces = []
brace_raw_bars = []
for sx in (-1, 1):
    for sy in (-1, 1):
        corner = Vector(sx * (FRAME_X / 2 - LEG_SQ),
                        sy * (FRAME_Y / 2 - LEG_SQ), 0)  # leg inner corner
        center_off = (BRACE_GAP + BRACE_T / 2) / SQ2
        cx, cy = corner.X - sx * center_off, corner.Y - sy * center_off
        bar = Rot(0, 0, -45 * sx * sy) * Box(400, BRACE_T, BRACE_H)
        bar = Pos(cx, cy, BRACE_Z) * bar
        brace_raw_bars.append(bar)
        braces.append(bar & interior)

base = legs + long_aprons + short_aprons + braces

# --- Top: glued panel with breadboard ends (tongue and groove) ---
TONGUE_L = 30
TONGUE_W = TOP_W - 2 * TONGUE_STOP
tongue = Box(TONGUE_L, TONGUE_W, TONGUE_T,
             align=(Align.CENTER, Align.CENTER, Align.CENTER))
tongue_z = LEG_H + TOP_T / 2
tongues = [Pos(s * (PANEL_L + TONGUE_L) / 2, 0, tongue_z) * tongue
           for s in (-1, 1)]
panel = Box(PANEL_L, TOP_W, TOP_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
panel = Pos(0, 0, LEG_H) * panel + tongues[0] + tongues[1]

bb_board = Box(BREADBOARD_W, TOP_W, TOP_T,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
breadboards = [
    Pos(s * (PANEL_L + BREADBOARD_W) / 2, 0, LEG_H) * bb_board - tongues[i]
    for i, s in enumerate((-1, 1))
]

# --- Buttons: lip rides the apron groove, body screws to the top ---
BTN_BODY_L = 40   # along the apron
BTN_BODY_D = 30   # out from the apron face
BTN_H = 20
BTN_LIP = GROOVE


def button(cx, cy, toward):
    """toward = unit direction from button body toward its apron face."""
    dx, dy = toward
    body = Box(BTN_BODY_L if dy else BTN_BODY_D,
               BTN_BODY_D if dy else BTN_BODY_L,
               BTN_H, align=(Align.CENTER, Align.CENTER, Align.MAX))
    body = Pos(cx, cy, LEG_H) * body
    lip = Box(BTN_BODY_L if dy else BTN_LIP,
              BTN_LIP if dy else BTN_BODY_L,
              GROOVE, align=(Align.CENTER, Align.CENTER, Align.MAX))
    lip = Pos(cx + dx * (BTN_BODY_D + BTN_LIP) / 2,
              cy + dy * (BTN_BODY_D + BTN_LIP) / 2,
              APRON_BOT + APRON_W - GROOVE_TOP_DROP) * lip
    return body + lip


long_face_y = long_apron_y - APRON_T / 2      # inner face of +y long apron
short_face_x = short_apron_x - APRON_T / 2
buttons = (
    [button(x, long_face_y - BTN_BODY_D / 2, (0, 1)) for x in (-500, 0, 500)]
    + [button(x, -(long_face_y - BTN_BODY_D / 2), (0, -1)) for x in (-500, 0, 500)]
    + [button(short_face_x - BTN_BODY_D / 2, 0, (1, 0))]
    + [button(-(short_face_x - BTN_BODY_D / 2), 0, (-1, 0))]
)

assembly = Compound(children=list(base) + [panel] + breadboards + buttons)

# --- Self-checks ---
bb = assembly.bounding_box()
assert abs(bb.size.Z - TABLE_H) < 0.01, bb.size
assert abs(bb.size.X - TOP_L) < 0.01 and abs(bb.size.Y - TOP_W) < 0.01, bb.size
knee = APRON_BOT
assert knee >= KNEE_MIN, knee
# aprons butt the legs without overlapping anything
for a in long_aprons + short_aprons:
    for l in legs:
        assert (a & l).volume < 1e-6, "apron intersects leg"
# braces: flush bearing on both aprons, bounded gap to the leg corner
for i, brace in enumerate(braces):
    sx, sy = (-1, 1)[i // 2], (-1, 1)[i % 2]
    assert len(brace.solids()) == 1
    assert 150_000 < brace.volume < 350_000, brace.volume
    for other in legs + long_aprons + short_aprons:
        assert (brace & other).volume < 1e-6, "brace collision"
    raw = brace_raw_bars[i]
    la = long_aprons[0 if sy < 0 else 1]
    sa = short_aprons[0 if sx < 0 else 1]
    assert (raw & la).volume > 1e3 and (raw & sa).volume > 1e3, \
        "brace does not bear on both aprons"
    leg = legs[(i // 2) * 2 + i % 2]
    toward = ((sx * (BRACE_GAP + 0.5)) / SQ2, (sy * (BRACE_GAP + 0.5)) / SQ2, 0)
    away = ((sx * (BRACE_GAP - 0.5)) / SQ2, (sy * (BRACE_GAP - 0.5)) / SQ2, 0)
    assert (Pos(*toward) * brace & leg).volume > 1e-6, "gap too large"
    assert (Pos(*away) * brace & leg).volume < 1e-6, "gap too small"
# breadboard tongue/groove: zero-clearance by construction, prove it
for i in (0, 1):
    assert (panel & breadboards[i]).volume < 1e-6
    assert abs((tongues[i] & breadboards[i]).volume) < 1e-6  # groove is empty
# top parts sit on the base without intersecting it
for t in [panel] + breadboards:
    for b in base:
        assert (t & b).volume < 1e-6, "top intersects base"
# button lips live inside the grooves, bodies clear of everything
for btn in buttons:
    for other in base + [panel] + breadboards:
        assert (btn & other).volume < 1e-6, "button collision"

# --- Registry: one solid per part ---
PARTS = [
    {"name": "leg", "solid": legs[0], "qty": 4,
     "material": "8/4 red oak, milled to 80 sq",
     "notes": "taper two inner faces 80->48 below z594; hanger bolt in corner"},
    {"name": "long apron", "solid": long_aprons[0], "qty": 2,
     "material": "4/4 red oak",
     "notes": "square butt ends; 6mm button groove, top 12 below edge"},
    {"name": "short apron", "solid": short_aprons[0], "qty": 2,
     "material": "4/4 red oak",
     "notes": "square butt ends; 6mm button groove, top 12 below edge"},
    {"name": "corner brace", "dims": (BRACE_T, BRACE_H, 190), "qty": 4,
     "material": "4/4 red oak",
     "notes": "ends cut 45; bolt hole mid-height; 2 screws per end into aprons"},
    {"name": "top panel", "solid": panel, "qty": 1,
     "material": "5/4 red oak",
     "notes": "edge-glue to 900 wide; 12mm tongue both ends, stopped 30 from edges"},
    {"name": "breadboard", "solid": breadboards[0], "qty": 2,
     "material": "5/4 red oak",
     "notes": "groove matches tongue; glue CENTER 100mm only, elongate outer peg holes"},
    {"name": "button", "solid": buttons[0], "qty": 8,
     "material": "hardwood scrap",
     "notes": "lip 6x6 rides apron groove; one screw each into top, slot-free movement"},
]

if __name__ == "__main__":
    print(f"table {bb.size.X:g} x {bb.size.Y:g} x {bb.size.Z:g}, knee {knee}, "
          f"taper {LEG_SQ}->{FOOT_SQ}, braces 4x {BRACE_T}x{BRACE_H} @45deg "
          f"gap {BRACE_GAP}, breadboards {BREADBOARD_W}, buttons {len(buttons)}")
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out:
        export_stl(assembly, out)
    if os.environ.get("EXPORT"):
        proj = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Dining-table-6"
        sys.path.insert(0, "/home/brian/ClaudeProjects/3d-modeling-brain/scripts")
        from cutlist import write_cut_list
        rows = write_cut_list(PARTS, f"{proj}/cutlist.md",
                              csv_path=f"{proj}/cutlist.csv",
                              title="Dining table for 6 (Shaker, corner braces)")
        export_step(assembly, f"{proj}/dining-table.step")
        print(f"exported cut list ({len(rows)} rows) + STEP")
    if os.environ.get("SHOW"):
        from ocp_vscode import show, Camera
        show(assembly, names=["dining-table-6"],
             reset_camera=Camera.RESET if os.environ["SHOW"] == "reset"
             else Camera.KEEP)
