"""Cabinet bench 36x24x20in, two stacked full-width drawers, undermount slides.

Frameless 18mm ply carcass, laminated 36mm seat slab, 12mm ply drawer
boxes on 21in undermount soft-close slides, dado/rabbet joinery (6mm).
Coordinates: X=width (0 at left), Y=depth (0 at front of drawer faces),
Z=height (0 at floor). All mm.
"""

import os
from build123d import *

IN = 25.4

# Overall envelope (user-specified)
W = 36 * IN            # 914.4
D = 24 * IN            # 609.6
H = 20 * IN            # 508.0

# Stock (nominal; MEASURE actual before cutting joinery)
T18 = 18.0             # 3/4" ply: carcass, slab, faces
T12 = 12.0             # 1/2" ply: drawer boxes + bottoms
T3 = 3.0               # 1/8" ply: back panel (batches run ~2.7-3.2)
DADO = 6.0             # dado/rabbet depth throughout

# Carcass
SLAB_T = 2 * T18                 # 36, two laminated layers
SIDE_H = H - SLAB_T              # 472
UM_FRONT_GAP = 1.5               # Blum front gap: faces' backs to the carcass front edge
SIDE_Y0 = T18 + UM_FRONT_GAP     # 19.5 carcass front edge
CARCASS_D = D - SIDE_Y0          # 590.1 (faces are 18 proud, plus the gap)
BACK_INSET = 12.0                # solid material behind the back groove
BACK_Y0 = SIDE_Y0 + CARCASS_D - BACK_INSET - T3   # 594.6, back front face

# Undermount slide geometry (Blum 563H installation sheet, checked 2026-08-24)
SLIDE_LEN = 21 * IN              # 533.4 box depth (Blum drawer length), exactly
RUNNER_LEN = 548.0               # 563H5330B runner, longer than the box
UM_WIDTH_LOSS = 42.0 - 2 * T12   # 18: Blum inside width = opening - 42 (10 was the 5/8 in side value)
UM_RECESS = 12.7                 # underside of drawer bottom above box bottom edge
UM_INSTALL_CLEAR = 6.0           # Blum minimum top clearance (max box height = opening - 20)

# Drawer opening
OPEN_W = W - 2 * T18             # 878.4
BOX_W = OPEN_W - UM_WIDTH_LOSS   # 860.4
BOX_D = SLIDE_LEN                # 533.4

# Reveals / face split. 20mm floor shadow gap keeps the bottom face off
# rugs and uneven floor; boxes are unchanged, only the face shortens.
REV_FLOOR, REV_MID, REV_TOP, REV_SIDE = 20.0, 3.0, 2.0, 2.0
FACE_W = W - 2 * REV_SIDE                      # 910.4
FACE_BOT_H = 257.0
FACE_TOP_H = SIDE_H - REV_FLOOR - REV_MID - REV_TOP - FACE_BOT_H  # 190
BOX_BOT_H = 240.0
BOX_TOP_H = 150.0

PARTS = []  # {"name", "solid", "qty", "material"} - cut list + assembly source


def _box(x, y, z, dx, dy, dz):
    """Box with min corner at (x, y, z)."""
    return Pos(x, y, z) * Box(dx, dy, dz, align=(Align.MIN, Align.MIN, Align.MIN))


# --- Part: side (qty 2, mirrored) -----------------------------------------
# 18 x 590.1 x 460. Sits in a 6mm-deep rabbet in the bottom panel (lower
# edge at Z=12); 3x6 groove on the inner face for the back, inset 12
# from the rear edge, running the full height.
side = _box(0, SIDE_Y0, T18 - DADO, T18, CARCASS_D, SIDE_H - (T18 - DADO))
side -= _box(T18 - DADO, BACK_Y0, T18 - DADO - 1, DADO + 1, T3, SIDE_H + 2)
PARTS.append({"name": "side", "solid": side, "qty": 2, "material": "ply 18mm"})

side_r = mirror(side, Plane.YZ.offset(W / 2))

# --- Part: bottom (18mm platform at the floor) -----------------------------
# Full width; sides sit in 6mm-deep x 18-wide rabbets in the top face at
# each end. Depth STOPS at the back's front face so the back slides down
# past it into the side/slab dados; back is then fastened to this rear
# edge. All carcass loads bear down onto this panel.
BOT_W = W                                # 914.4
BOT_D = BACK_Y0 - SIDE_Y0                # 575.1
bottom = _box(0, SIDE_Y0, 0, BOT_W, BOT_D, T18)
bottom -= _box(-1, SIDE_Y0 - 1, T18 - DADO, T18 + 1, BOT_D + 2, DADO + 1)
bottom -= _box(W - T18, SIDE_Y0 - 1, T18 - DADO, T18 + 1, BOT_D + 2, DADO + 1)
PARTS.append({"name": "bottom", "solid": bottom, "qty": 1, "material": "ply 18mm"})

# --- Part: back (3mm ply, dados in sides + slab, slides past the bottom) ---
# Slides down the side grooves past the bottom's rear edge; top edge
# captured by the slab groove, bottom edge glued/bradded to the bottom's
# rear edge. Glued in = racking shear panel, dresser-style.
BACK_W = W - 2 * T18 + 2 * DADO          # 890.4
back = _box(T18 - DADO, BACK_Y0, T18 - DADO,
            BACK_W, T3, SIDE_H + DADO - (T18 - DADO))
PARTS.append({"name": "back", "solid": back, "qty": 1, "material": "ply 3mm"})

# --- Parts: top slab (two laminated 18mm layers, full footprint) -----------
# Overhangs the carcass front by 18 to land flush over the drawer faces.
# Lower layer carries a stopped 3x6 groove in its underside for the back;
# upper layer is a plain blank, so the two are separate parts.
slab_lower = _box(0, 0, SIDE_H, W, D, T18)
slab_lower -= _box(T18 - DADO, BACK_Y0, SIDE_H - 1,
                   W - 2 * (T18 - DADO), T3, DADO + 1)
slab_upper = _box(0, 0, SIDE_H + T18, W, D, T18)
PARTS.append({"name": "slab_lower", "solid": slab_lower, "qty": 1, "material": "ply 18mm"})
PARTS.append({"name": "slab_upper", "solid": slab_upper, "qty": 1, "material": "ply 18mm"})

# --- Drawer boxes (12mm ply, undermount geometry) --------------------------
# Sides run full box depth; front/back captured in 6mm end rabbets in the
# sides; 12mm bottom in 6mm grooves all around, underside at UM_RECESS.
SLIDE_STANDOFF = 14.0  # Blum bottom clearance: box side bottom edge above the
                       # mounting surface (563H installation sheet)
BOX_X0 = (W - BOX_W) / 2
END_LEN = BOX_W - 2 * (T12 - DADO)       # 856.4 drawer front/back length


def make_drawer(box_h, z0, sfx):
    """Build one drawer box in place; register parts, return visual solid."""
    x0, y0 = BOX_X0, T18             # box front against the face's back, ahead of the carcass edge
    s = _box(x0, y0, z0, T12, BOX_D, box_h)
    s -= _box(x0 + T12 - DADO, y0 - 1, z0 - 1, DADO + 1, T12 + 1, box_h + 2)
    s -= _box(x0 + T12 - DADO, y0 + BOX_D - T12, z0 - 1, DADO + 1, T12 + 1, box_h + 2)
    s -= _box(x0 + T12 - DADO, y0 - 1, z0 + UM_RECESS, DADO + 1, BOX_D + 2, T12)

    end = _box(x0 + T12 - DADO, y0, z0, END_LEN, T12, box_h)
    end -= _box(x0 + T12 - DADO - 1, y0 + T12 - DADO, z0 + UM_RECESS,
                END_LEN + 2, DADO + 1, T12)

    bot = _box(x0 + T12 - DADO, y0 + T12 - DADO, z0 + UM_RECESS,
               END_LEN, BOX_D - 2 * (T12 - DADO), T12)

    PARTS.append({"name": f"drawer_side_{sfx}", "solid": s, "qty": 2, "material": "ply 12mm"})
    PARTS.append({"name": f"drawer_end_{sfx}", "solid": end, "qty": 2, "material": "ply 12mm",
                  "notes": "the BACK needs Blum rear-hook prep (35 x 13 corner notches, 6 x 10 bores 7 in "
                           "from the side and 24 up, bottom groove stopped 35 from each side), not modeled here; "
                           "see Drawer-bench drawer_back"})
    PARTS.append({"name": f"drawer_bottom_{sfx}", "solid": bot, "qty": 1, "material": "ply 12mm"})

    s_r = mirror(s, Plane.YZ.offset(W / 2))
    end_r = mirror(end, Plane(origin=(0, y0 + BOX_D / 2, 0),
                              x_dir=(1, 0, 0), z_dir=(0, 1, 0)))
    return s + s_r + end + end_r + bot


BOX_BOT_Z0 = T18 + SLIDE_STANDOFF        # 32
drawer_bot = make_drawer(BOX_BOT_H, BOX_BOT_Z0, "bot")

# Top drawer: face spans Z 280..470; box rides its slides ~10 above face bottom
FACE_BOT_Z0 = REV_FLOOR                          # 20
FACE_TOP_Z0 = FACE_BOT_Z0 + FACE_BOT_H + REV_MID  # 280
BOX_TOP_Z0 = BOX_BOT_Z0 + BOX_BOT_H + SLIDE_STANDOFF + UM_INSTALL_CLEAR   # 292: upper runner + top clearance
drawer_top = make_drawer(BOX_TOP_H, BOX_TOP_Z0, "top")

# --- Parts: drawer faces (18mm full overlay, 18 proud of carcass) ----------
face_bot = _box(REV_SIDE, 0, FACE_BOT_Z0, FACE_W, T18, FACE_BOT_H)
face_top = _box(REV_SIDE, 0, FACE_TOP_Z0, FACE_W, T18, FACE_TOP_H)
PARTS.append({"name": "face_bot", "solid": face_bot, "qty": 1, "material": "ply 18mm"})
PARTS.append({"name": "face_top", "solid": face_top, "qty": 1, "material": "ply 18mm"})

assembly = (side + side_r + bottom + back + slab_lower + slab_upper
            + drawer_bot + drawer_top + face_bot + face_top)

# --- checks ---------------------------------------------------------------
bb = assembly.bounding_box()
assert abs(bb.size.X - W) < 1e-6, bb.size
assert abs(bb.size.Y - D) < 1e-6, bb.size
assert abs(bb.size.Z - H) < 1e-6, bb.size
for p in PARTS:
    assert len(p["solid"].solids()) == 1, p["name"]

# Undermount geometry probed from the solids, not just the constants
_bside = next(p for p in PARTS if p["name"] == "drawer_side_bot")["solid"]
_bbot = next(p for p in PARTS if p["name"] == "drawer_bottom_bot")["solid"]
assert abs(_bbot.bounding_box().min.Z - _bside.bounding_box().min.Z - UM_RECESS) < 1e-6
_box_outer_w = W - 2 * _bside.bounding_box().min.X   # mirrored about W/2
assert abs(OPEN_W - _box_outer_w - UM_WIDTH_LOSS) < 1e-6
assert abs(_bside.bounding_box().size.Y - SLIDE_LEN) < 1e-6
assert BOX_TOP_Z0 - (BOX_BOT_Z0 + BOX_BOT_H) >= SLIDE_STANDOFF + UM_INSTALL_CLEAR   # upper runner sits below its box
assert SIDE_H - (BOX_TOP_Z0 + BOX_TOP_H) >= UM_INSTALL_CLEAR
# Boxes clear their faces vertically and sit behind them
assert BOX_BOT_Z0 > FACE_BOT_Z0 and BOX_BOT_Z0 + BOX_BOT_H < FACE_BOT_Z0 + FACE_BOT_H
assert BOX_TOP_Z0 > FACE_TOP_Z0 and BOX_TOP_Z0 + BOX_TOP_H < FACE_TOP_Z0 + FACE_TOP_H
# Slide length fits the interior depth (front edge to back panel)
assert BACK_Y0 - SIDE_Y0 >= RUNNER_LEN + 3.0 + 6.0   # Blum frameless: runner + 3 setback + 6
# Back is housed: spans side-groove floor (Z12) to slab-groove floor
# (Z478), and its front face is flush with the bottom's rear edge so it
# slides past during assembly
_back = next(p for p in PARTS if p["name"] == "back")["solid"]
_bot = next(p for p in PARTS if p["name"] == "bottom")["solid"]
assert abs(_back.bounding_box().min.Z - (T18 - DADO)) < 1e-6
assert abs(_back.bounding_box().max.Z - (SIDE_H + DADO)) < 1e-6
assert abs(_back.bounding_box().size.Y - T3) < 1e-6
assert abs(_bot.bounding_box().max.Y - BACK_Y0) < 1e-6
# Sides seat in the bottom's 6mm rabbets, bottom spans full width
_side = next(p for p in PARTS if p["name"] == "side")["solid"]
assert abs(_side.bounding_box().min.Z - (T18 - DADO)) < 1e-6
assert abs(_bot.bounding_box().size.X - W) < 1e-6
# Faces + reveals exactly fill the front (floor to slab underside)
assert abs(REV_FLOOR + FACE_BOT_H + REV_MID + FACE_TOP_H + REV_TOP - SIDE_H) < 1e-6

# --- exports --------------------------------------------------------------
TMP = os.environ.get("TMP_STL")
if TMP:
    export_stl(assembly, TMP)

if os.environ.get("EXPORT"):
    import sys
    sys.path.insert(0, "/home/brian/ClaudeProjects/3d-modeling-brain/scripts")
    from cutlist import write_cut_list

    PROJ = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Cabinet-bench"
    write_cut_list(
        PARTS,
        f"{PROJ}/cutlist.md",
        csv_path=f"{PROJ}/cutlist.csv",
        title="Cabinet Bench 36x24x20",
    )
    export_step(assembly, f"{PROJ}/cabinet_bench.step")
    print("exported cutlist + step")

if os.environ.get("SHOW"):
    from ocp_vscode import show, set_port, Camera
    set_port(3939)
    show(side, side_r, bottom, back, slab_lower, slab_upper,
         drawer_bot, drawer_top, face_bot, face_top,
         names=["side_l", "side_r", "bottom", "back", "slab_lower",
                "slab_upper", "drawer_bot", "drawer_top", "face_bot",
                "face_top"],
         reset_camera=(Camera.RESET if os.environ["SHOW"] == "reset"
                       else Camera.KEEP))

print("OK  parts:", [p["name"] for p in PARTS])
