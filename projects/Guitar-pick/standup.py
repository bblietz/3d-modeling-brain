"""The pick standing on its top edge on a snap-off base, for a flat-free print (Brian 2026-10-12: the mirrored
1.5 mm bevel on both faces, no support material, printed standing for the smoothest PETG surfaces).

Standing, the faces and bevels are walls. Only the top edge arc and the shoulder rounds up to the 45 degree point
face down, and those sit on a two-line neck (0.40 x 0.3 mm) on a saddle-topped block. A column beside the pick
gives the nozzle somewhere to go each layer so the thin tip cross-sections cool. Everything is one solid.

Why two lines (2026-10-13, after the first print): on the shoulders the neck sits beside the pick's edge in every
layer, so a one-line neck was a spur off the end of the pick's wall loop. The slicer printed that spur as its own
0.3 to 1.3 mm bead, started and ended on the pick's edge, and put the loop's seam there as well, at every one of
the 55 shoulder layers; the corners came out with chunks missing. With the rim two lines wide (0.44, guitar_pick.py)
and the neck two lines wide, the outer wall runs along the pick's faces, straight along the neck's sides and into
the block, one closed loop with no spur and no path end on the pick (checked in pipeline/make_standup_3mf.py).

    .venv/bin/python projects/Guitar-pick/standup.py      -> guitar-pick.stl (the print STL), standup.json
"""
import json
import os
from pathlib import Path

import numpy as np
import trimesh
from build123d import Axis, Box, Face, Pos, Rot, Vector, Wire, export_stl, extrude

import guitar_pick as gp

HERE = Path(__file__).resolve().parent
EDGE = "mirror"
FIRST_LAYER, LAYER = 0.1, 0.06
NECK_T, NECK_H = 0.40, 0.30       # two 0.2-nozzle lines wide (a hair under the 0.44 rim so it, not the rim, breaks); snap off, sand the rim flush
SUPPORT_DEG = 45                  # the neck holds the outline up to where it is this steep; above that it self-supports
BLOCK_W, BLOCK_MARGIN = 7.0, 2.0  # block width (pick thickness direction) and how far it runs past the neck ends
OVERLAP = 0.1                     # the neck reaches this far into the pick and the block so the union is one solid
TOWER, TOWER_X = 4.0, 24.0        # cooling column, square, centred at this x (pick half-width is 13.1)
SEAM_STRIP, SEAM_DEPTH = 0.75, 0.002   # a 1.5 mm wide, 2 micron deep strip down the +y face: its own mesh triangles, which
                                       # the 3MF paints as the seam region; far below the slicer's 0.012 mm resolution
PLATE_W, PLATE_H = 6.0, 1.0       # the plate on the bed that ties the column to the block


def build():
    pick = gp.build(EDGE)                            # flat: x width, y 0 (top edge) to -30.385 (tip), z 0..1
    raw, side, samp = gp.outline()
    length = -samp[:, 1].min()

    # total height on a layer boundary: 0.1 first layer, then 0.06 layers to the tip
    n_layers = round((4.0 + NECK_H + length - FIRST_LAYER) / LAYER)
    height = FIRST_LAYER + n_layers * LAYER
    base_h = height - NECK_H - length                # block height under the top edge centre

    # stand it up: tip to +z, top edge centre at z = base_h + NECK_H, thickness centred on y = 0
    pick = Pos(0, -gp.THICK / 2, base_h + NECK_H) * (Rot(X=-90) * pick)

    # the top edge and shoulders up to SUPPORT_DEG, as (x, z) in the standing frame, left to right
    d = np.roll(samp, -1, 0) - samp
    ang = np.degrees(np.arctan2(np.abs(d[:, 1]), np.abs(d[:, 0])))
    held = samp[(samp[:, 1] > -9) & (ang < SUPPORT_DEG)]
    held = held[np.argsort(held[:, 0])]
    arc = np.column_stack([held[:, 0], -held[:, 1] + base_h + NECK_H])
    xl, zl = arc[0]
    xr, zr = arc[-1]

    def sheet(top, bottom, thick):
        pts = [Vector(x, 0, z) for x, z in top] + [Vector(x, 0, z) for x, z in bottom[::-1]]
        return extrude(Face(Wire.make_polygon(pts, close=True)), thick / 2, both=True)

    neck = sheet(arc + [0, OVERLAP], arc - [0, NECK_H + OVERLAP], NECK_T)
    block_top = np.vstack([[xl - BLOCK_MARGIN, zl - NECK_H], arc - [0, NECK_H], [xr + BLOCK_MARGIN, zr - NECK_H]])
    block = sheet(block_top, np.array([[xl - BLOCK_MARGIN, 0.0], [xr + BLOCK_MARGIN, 0.0]]), BLOCK_W)
    tower = Pos(TOWER_X, 0, height / 2) * Box(TOWER, TOWER, height)
    plate = Pos((xr + TOWER_X) / 2, 0, PLATE_H / 2) * Box(TOWER_X - xr + TOWER / 2, PLATE_W, PLATE_H)

    part = pick + neck + block + plate + tower
    # the seam strip: a 2 micron recess down the middle of the +y face, inside the flat part of the face (clear of
    # the lead-in bands), so the STL carries triangles that lie wholly in |x| < SEAM_STRIP for the 3MF's seam paint
    z0, z1 = base_h + NECK_H + 2.8, height - 2.8
    part = part - Pos(0, gp.THICK / 2, (z0 + z1) / 2) * Box(2 * SEAM_STRIP, 2 * SEAM_DEPTH, z1 - z0)
    bb = part.bounding_box()
    assert len(part.solids()) == 1, len(part.solids())
    assert abs(bb.max.Z - height) < 1e-3 and abs(bb.min.Z) < 1e-6, (bb.min.Z, bb.max.Z)
    assert abs(height - (FIRST_LAYER + n_layers * LAYER)) < 1e-9
    pb = pick.bounding_box()
    assert abs(pb.min.Z - (base_h + NECK_H)) < 1e-3 and abs(pb.size.Y - gp.THICK) < 1e-6
    # the neck only touches the pick along its outline: the pick's volume is unchanged by the union
    assert abs((part & pick).volume - pick.volume) < 0.5, (part & pick).volume - pick.volume
    strip = [f for f in part.faces() if abs(f.center().Y - (gp.THICK / 2 - SEAM_DEPTH)) < 1e-6]
    assert len(strip) == 1 and abs(strip[0].area - 2 * SEAM_STRIP * (z1 - z0)) < 1e-3, "the seam strip floor is missing"
    assert abs((part & pick).volume - pick.volume) < 0.5
    info = {"height": round(height, 3), "layers": 1 + n_layers, "base_h": round(base_h, 3), "neck": [NECK_T, NECK_H],
            "held_span_x": [round(float(xl), 2), round(float(xr), 2)], "held_drop": round(float(zl - (base_h + NECK_H)), 2),
            "support_deg": SUPPORT_DEG, "block": [round(float(xr - xl + 2 * BLOCK_MARGIN), 1), BLOCK_W, round(float(zl - NECK_H), 2)],
            "tower": [TOWER, TOWER_X], "seam_strip": SEAM_STRIP, "seam_depth": SEAM_DEPTH, "seam_strip_z": [round(z0, 3), round(z1, 3)],
            "volume_mm3": round(part.volume, 1), "pick_mm3": round(pick.volume, 1),
            "arc_xz": [[round(float(x), 3), round(float(z), 3)] for x, z in arc[::20]]}
    return part, pick, info


if __name__ == "__main__":
    part, pick, info = build()
    export_stl(part, str(HERE / "guitar-pick.stl"))
    m = trimesh.load(HERE / "guitar-pick.stl")
    assert m.is_watertight, "STL not watertight"
    (HERE / "standup.json").write_text(json.dumps(info, indent=1))
    print("OK", info["height"], "mm tall,", info["layers"], "layers, base", info["base_h"], "held x", info["held_span_x"],
          "drop", info["held_drop"], "PETG g ~", round(part.volume * 1.27e-3, 2), "of which pick", round(pick.volume * 1.27e-3, 2))
    if os.environ.get("SHOW"):
        from ocp_vscode import show, Camera
        show(part, names=["pick on base"], reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
