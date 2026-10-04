"""Docking and hold check for the skateboard hook against the truck proxy mesh
(memory/feedback-check-docking-and-hold-kinematics.md: name the way in and what the hanging load does).

Docking motion: the board is lowered straight down (-y) until the hanger's center body rests in the cradle.
Load motion: the board's weight pulls -y, the same direction, so the load drives the part in; the only way
out is a lift (+y). This script measures, frictionless, on 2D slices across the holder's width:
  REST      how far the proxy settles from its nominal pose
  WAY IN    the lowering path is collision free with the truck grown 0.2 mm
  PLAY      how far the docked board can move toward the room and sideways without lifting (bump slack)
  HOLD      the lift needed before a straight path toward the room, or sideways, becomes collision free

Slices: the holder across its width every 0.5 mm, the truck at z in [-60, 60] every 0.5 mm (a sideways move
of dz pairs holder slice z with truck slice z - dz). Collision = overlap area over EPS at any slice.

Usage: .venv/bin/python projects/Skateboard-wall-holder/pipeline/hold_check.py   (run skateboard_holder.py first)
Writes build/hold-check.json
"""
import json
import pathlib
import sys

import numpy as np
import trimesh
from shapely.affinity import translate
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union

PROJ = pathlib.Path(__file__).resolve().parent.parent
B = PROJ / "build"
EPS = 0.3            # mm^2; chord-vs-arc tessellation of touching curved faces overlaps by far less
STEP = 0.5           # slice spacing
GROW = 0.2           # docking margin


def slices(mesh, zs):
    out = {}
    for z in zs:
        s = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if s is None:
            out[round(z, 2)] = Polygon()
            continue
        p2, _ = (s.to_2D if hasattr(s, 'to_2D') else s.to_planar)(to_2D=np.eye(4))
        out[round(z, 2)] = unary_union([Polygon(p.exterior.coords, [h.coords for h in p.interiors]) for p in p2.polygons_full])
    assert any(not p.is_empty for p in out.values()), "no slice had any area"
    return out


holder = trimesh.load(B / "holder-design.stl")
truck = trimesh.util.concatenate([trimesh.load(B / "truck.stl"), trimesh.load(B / "nut.stl")])
half_w = holder.bounds[1][2]
zh = np.round(np.arange(-round(half_w) + STEP, round(half_w) - STEP / 2, STEP), 2)   # inside the holder, on the truck's 0.5 lattice
zt = np.round(np.arange(-60, 60 + STEP / 2, STEP), 2)
HS = slices(holder, zh)
TS = slices(truck, zt)
TS_GROWN = {z: p.buffer(GROW, join_style=2) for z, p in TS.items()}


def collides(dx, dy, dz, grown=False):
    src = TS_GROWN if grown else TS
    for z in zh:
        key = round(z - dz, 2)
        t = src.get(key)
        if t is None or t.is_empty:
            continue
        if HS[z].intersection(translate(t, dx, dy)).area > EPS:
            return True
    return False


def free_path(dy, axis, span, step=1.0):
    """Straight path from the docked pose along axis ('x' or 'z') over span mm, collision free at lift dy."""
    for d in np.arange(0, span + step / 2, step):
        if collides(d if axis == "x" else 0, dy, d if axis == "z" else 0):
            return False
    return True


res = {}
# REST: lowest lift (can be negative) at which the nominal pose is free
dy = 3.0
while dy > -3 and not collides(0, dy, 0):
    dy -= 0.05
res["rest_mm"] = round(dy + 0.05, 2)
rest = res["rest_mm"]
assert abs(rest) < 0.3, f"the proxy does not rest where the model put it: {rest}"

# WAY IN: lowering from 60 mm above to just above rest, truck grown by GROW
blocked = [round(h, 2) for h in np.arange(60, 0.25, -0.5) if collides(0, rest + h, 0, grown=True)]
res["way_in_blocked_at_lift_mm"] = blocked
assert not blocked, f"lowering path blocked at lifts {blocked[:5]}"

# PLAY: bump slack without lifting
play_x = next((d for d in np.arange(0, 20, 0.1) if collides(d, rest, 0)), 20.0)
play_z = next((d for d in np.arange(0, 20, 0.1) if collides(0, rest, d)), 20.0)
res["play_toward_room_mm"] = round(play_x, 1)
res["play_sideways_mm"] = round(play_z, 1)

# HOLD: lift needed before a straight escape is free
hold = {}
for name, axis, span in (("hold_toward_room_mm", "x", 60), ("hold_sideways_mm", "z", 45)):
    hold[name] = None
    for h in np.arange(0, 16, 0.25):
        if free_path(rest + h, axis, span):
            hold[name] = round(float(h), 2)
            break
res.update(hold)
assert res["hold_toward_room_mm"] is not None and res["hold_sideways_mm"] is not None, res
(B / "hold-check.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res))
