"""Router template for the Garmin GPSMAP 943xsv flush cutout.

Bearing-guided bit rides the window edge, so the window is exactly the
Garmin cutout. Four drill guides locate the bezel screw pilots. Print flat,
counterbored face up. +Y is the unit's top; the template says TOP on the
counterbored face. See brief.md for the source of every Garmin number.

Run:  .venv/bin/python projects/Garmin-943-helm-panel/router-template.py
Env:  STAGE=n builds only the first n features (1..7) and exports a scratch
      STL for the per-feature render. SHOW=1|reset pushes to the OCP viewer.
"""
import os
import sys
import zipfile

from build123d import *

# ---- Garmin 9x3 flush template 190-02761-05_0D (mm), shared with helm-panel.py ----
from garmin_9x3 import CUTOUT_H, CUTOUT_W, HOLE_PITCH_X, HOLE_PITCH_Y, HOLE_SHIFT, HOLE_Y, PILOT_DRILL

# ---- Template design (mm) ----
FRAME_SIDE = 15.0  # frame width left and right
FRAME_TOPBOT = 25.0  # frame width top and bottom
THICK = 12.0  # bearing up to about 10 mm rides fully on the edge
GUIDE_DIA = 2.8  # prints about 2.5, clears a 2.3 to 2.4 mm bit
CBORE_DIA = 6.0  # 7.0 would leave only 1.0 mm between the top counterbores and the window
CBORE_DEPTH = 6.0  # leaves a 6 mm guide at the panel side
FIX_HOLE_DIA = 4.0
FIX_HOLE_OFFSET = 6.0  # outside the window edge, under the bezel overlap
NOTCH_DEPTH = 2.0  # 90 degree V at each outer edge midpoint
EF_CHAMFER = 0.6  # bed-side window edge, elephant foot relief
TEXT_DEPTH = 0.8  # TOP deboss on the counterbored face
TEXT_SIZE = 8.0

OUTER_W = CUTOUT_W + 2 * FRAME_SIDE  # 252.4
OUTER_H = CUTOUT_H + 2 * FRAME_TOPBOT  # 189.0
BED = 256.0

PROJECT = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Garmin-943-helm-panel"
NAME = "router-template"

ON_BED = (Align.CENTER, Align.CENTER, Align.MIN)


def build(upto=7):
    # 1. base plate on Z=0
    part = Box(OUTER_W, OUTER_H, THICK, align=ON_BED)
    if upto < 2:
        return part

    # 2. window, cutter extended past both faces
    part -= Pos(0, 0, -1) * Box(CUTOUT_W, CUTOUT_H, THICK + 2, align=ON_BED)
    if upto < 3:
        return part

    # 3. elephant foot chamfer on the bed-side window edge loop only
    inner_bottom = [
        e
        for e in part.edges().group_by(Axis.Z)[0]
        if abs(e.center().X) <= CUTOUT_W / 2 + 0.1 and abs(e.center().Y) <= CUTOUT_H / 2 + 0.1
    ]
    assert len(inner_bottom) == 4, len(inner_bottom)
    part = chamfer(inner_bottom, EF_CHAMFER)
    if upto < 4:
        return part

    # 4. drill guides with counterbore from the top, pattern shifted toward the unit's bottom
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * HOLE_PITCH_X / 2, HOLE_Y[sy]
            part -= Pos(x, y, -1) * Cylinder(GUIDE_DIA / 2, THICK + 2, align=ON_BED)
            part -= Pos(x, y, THICK - CBORE_DEPTH) * Cylinder(CBORE_DIA / 2, CBORE_DEPTH + 1, align=ON_BED)
    if upto < 5:
        return part

    # 5. optional fixing holes on the vertical centerline
    for sy in (-1, 1):
        y = sy * (CUTOUT_H / 2 + FIX_HOLE_OFFSET)
        part -= Pos(0, y, -1) * Cylinder(FIX_HOLE_DIA / 2, THICK + 2, align=ON_BED)
    if upto < 6:
        return part

    # 6. registration V notches, 90 degrees, at the four outer edge midpoints
    s = 6.0  # rotated square side; half diagonal = s / sqrt(2)
    half_diag = s / 2**0.5
    for x, y in ((0, OUTER_H / 2), (0, -OUTER_H / 2), (OUTER_W / 2, 0), (-OUTER_W / 2, 0)):
        d = half_diag - NOTCH_DEPTH
        ux, uy = (0, 1) if x == 0 else (1, 0)
        cx, cy = x + ux * d * (1 if x + y > 0 else -1), y + uy * d * (1 if x + y > 0 else -1)
        part -= Pos(cx, cy, -1) * Rot(0, 0, 45) * Box(s, s, THICK + 2, align=ON_BED)
    if upto < 7:
        return part

    # 7. TOP deboss in the top band, clear of the fixing hole and the guides
    label = extrude(Text("TOP", TEXT_SIZE, align=(Align.CENTER, Align.CENTER)), TEXT_DEPTH + 1)
    part -= Pos(40, CUTOUT_H / 2 + FRAME_TOPBOT / 2 + 2, THICK - TEXT_DEPTH) * label
    return part


def probe_volume(part, box):
    """Volume of the intersection between part and a probe solid."""
    hit = part & box
    return hit.volume if hit and hit.volume else 0.0


def check(part):
    bb = part.bounding_box()
    size = bb.size
    assert abs(size.X - OUTER_W) < 1e-3 and abs(size.Y - OUTER_H) < 1e-3 and abs(size.Z - THICK) < 1e-3, size
    assert size.X <= BED and size.Y <= BED, "does not fit the bed"
    assert len(part.solids()) == 1, len(part.solids())

    # window is exactly the Garmin cutout: a probe 0.05 smaller must be clear,
    # a probe 0.05 larger on each side must hit material
    mid = Pos(0, 0, 1) * Box(CUTOUT_W - 0.1, CUTOUT_H - 0.1, THICK - 2, align=ON_BED)
    assert probe_volume(part, mid) < 1e-6, "window undersize"
    big = Pos(0, 0, 1) * Box(CUTOUT_W + 0.1, CUTOUT_H + 0.1, THICK - 2, align=ON_BED)
    assert probe_volume(part, big) > 1.0, "window oversize"

    # each drill guide is clear through the full thickness at the shifted position,
    # and a pin at the old centered position hits material (the shift really happened)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * HOLE_PITCH_X / 2, HOLE_Y[sy]
            pin = Pos(x, y, 0) * Cylinder(GUIDE_DIA / 2 - 0.05, THICK, align=ON_BED)
            assert probe_volume(part, pin) < 1e-6, "guide blocked"
            old = Pos(x, sy * HOLE_PITCH_Y / 2, 0) * Cylinder(GUIDE_DIA / 2 - 0.05, THICK - CBORE_DEPTH - 0.1, align=ON_BED)
            assert probe_volume(part, old) > 0.5, "guide not shifted"
    # geometry of the shift, as Garmin draws it: 4.5 above the top edge, 7.0 below the bottom edge
    assert abs((HOLE_Y[1] - CUTOUT_H / 2) - 4.51) < 0.02 and abs((-CUTOUT_H / 2 - HOLE_Y[-1]) - 6.99) < 0.02

    # counterbore is open from the top face down to CBORE_DEPTH, guide below it is solid around a 4 mm probe
    x, y = HOLE_PITCH_X / 2, HOLE_Y[1]
    cb = Pos(x, y, THICK - CBORE_DEPTH + 0.05) * Cylinder(CBORE_DIA / 2 - 0.05, CBORE_DEPTH - 0.05, align=ON_BED)
    assert probe_volume(part, cb) < 1e-6, "counterbore blocked"
    ring = Pos(x, y, 0) * Cylinder(2.0, THICK - CBORE_DEPTH - 0.05, align=ON_BED)
    assert probe_volume(part, ring) > 1.0, "guide bore too large"

    # V notches: empty 1.5 mm inside each outer edge midpoint, solid 2.5 mm inside
    for x, y, nx, ny in ((0, OUTER_H / 2, 0, 1), (0, -OUTER_H / 2, 0, -1), (OUTER_W / 2, 0, 1, 0), (-OUTER_W / 2, 0, -1, 0)):
        tip = Pos(x - nx * 1.5, y - ny * 1.5, 0) * Box(0.2, 0.2, THICK, align=ON_BED)
        assert probe_volume(part, tip) < 1e-6, "notch missing"
        root = Pos(x - nx * 2.5, y - ny * 2.5, 0) * Box(0.2, 0.2, THICK, align=ON_BED)
        assert probe_volume(part, root) > 1e-3, "notch too deep"

    # TOP deboss removed material from the top face and nothing below it
    tx, ty = 40, CUTOUT_H / 2 + FRAME_TOPBOT / 2 + 2
    slab = Pos(tx, ty, THICK - TEXT_DEPTH + 0.05) * Box(20, TEXT_SIZE, TEXT_DEPTH - 0.05, align=ON_BED)
    assert probe_volume(part, slab) < 20 * TEXT_SIZE * (TEXT_DEPTH - 0.05) * 0.9, "TOP deboss missing"
    under = Pos(tx, ty, 0) * Box(20, TEXT_SIZE, THICK - TEXT_DEPTH - 0.05, align=ON_BED)
    assert abs(probe_volume(part, under) - 20 * TEXT_SIZE * (THICK - TEXT_DEPTH - 0.05)) < 1e-3, "deboss too deep"

    # minimum wall between the top counterbores and the window edge (the tight side)
    wall = HOLE_Y[1] - CUTOUT_H / 2 - CBORE_DIA / 2
    assert wall >= 1.24, wall

    # volume sanity: frame minus holes, within 3 percent of the analytic frame volume
    frame = (OUTER_W * OUTER_H - CUTOUT_W * CUTOUT_H) * THICK
    assert 0.97 * frame < part.volume < frame, (part.volume, frame)
    return {"size": (size.X, size.Y, size.Z), "volume_cm3": part.volume / 1000, "guide_wall_mm": wall,
            "hole_y": HOLE_Y}


def export(part):
    stl = f"{PROJECT}/{NAME}.stl"
    threemf = f"{PROJECT}/{NAME}.3mf"
    export_stl(part, stl)
    m = Mesher()
    m.add_shape(part)
    m.write(threemf)

    import trimesh

    mesh = trimesh.load_mesh(stl)
    assert mesh.is_watertight, "STL not watertight"
    ext = mesh.bounds[1] - mesh.bounds[0]
    assert abs(ext[0] - OUTER_W) < 0.01 and abs(ext[1] - OUTER_H) < 0.01 and abs(ext[2] - THICK) < 0.01, ext
    with zipfile.ZipFile(threemf) as z:
        model = z.read("3D/3dmodel.model").decode()
    # Mesher writes the mesh object plus a components wrapper; one build item is the real check
    assert model.count("<item ") == 1, "3MF should hold one build item"
    assert model.count("<triangle ") == len(mesh.faces), "3MF mesh differs from STL"
    return stl, threemf


if __name__ == "__main__":
    stage = int(os.environ.get("STAGE", "7"))
    part = build(stage)
    if stage < 7:
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
