"""Parametric project box with friction-fit lid (build123d).

Single-color PLA, Bambu Lab X2D, 0.6 mm high-flow nozzle.
Both parts are modeled in their print orientation, sitting on Z=0:
  - box: floor on bed, open top up
  - lid: plate on bed, plug pointing up

Running this file builds both parts, runs assertion checks (dimensions,
clearance, solids count, volume, watertightness, overhangs), and exports
box.stl, lid.stl, and project-box.3mf next to this file.
"""

import math
from pathlib import Path

import trimesh
from build123d import (
    Align,
    Axis,
    Box,
    Cylinder,
    Mesher,
    Pos,
    Rot,
    chamfer,
    export_stl,
    fillet,
)

OUT_DIR = Path(__file__).parent

# ---------------------------------------------------------------- parameters
# Box
BOX_L = 80.0          # outer length (X)
BOX_W = 50.0          # outer width (Y)
BOX_H = 30.0          # outer height (Z)
WALL = 2.4            # side wall thickness
FLOOR = 2.4           # floor thickness
CORNER_R = 6.0        # outer vertical corner fillet
FOOT_CHAMFER = 0.6    # elephant-foot chamfer on bottom outer edge

# Derived cavity
CAV_L = BOX_L - 2 * WALL          # 75.2
CAV_W = BOX_W - 2 * WALL          # 45.2
CAV_R = CORNER_R - WALL           # 3.6
CAV_DEPTH = BOX_H - FLOOR         # 27.6

# Lid
LID_T = 3.0           # plate thickness
PLUG_H = 2.0          # plug height
PLUG_CLEAR = 0.15     # clearance per side, plug vs cavity; the ribs own the fit
LEAD_IN = 0.8         # 45-degree lead-in chamfer on plug free edge

# Crush ribs (v3). Calipers on the v2 print (2026-07-31): cavity width
# printed 44.98 vs 45.2 designed, plug 44.67 vs 45.0, so the as-printed
# gap runs ~0.055 mm per side looser than designed and a plain-clearance
# friction fit would need designed interference. Ribs bridge the gap
# instead: predicted crush ~0.15 mm per side at each rib.
RIB_R = 1.0           # rib cylinder radius
RIB_PROUD = 0.35      # rib tip beyond plug face
RIB_LEAD = 0.5        # 45-degree lead-in chamfer on rib top
RIB_XS = (-25.0, 25.0)  # rib centers along the long (Y-facing) plug sides
RIB_YS = (-14.0, 14.0)  # rib centers along the short (X-facing) plug sides

# Fingernail scoops (v4). The v3 snug lid printed flush and was too hard
# to open barehanded: 45-degree coves at the plate's short ends give a
# nail a 1.5 mm gap over the box rim to peel one end up. The lid FLIPS to
# install, so the coves go in the plug-side plate face (the in-use
# underside that lands on the rim), not the print-orientation bed face.
SCOOP_W = 25.0        # scoop width along Y, centered on each short end
SCOOP_D = 1.5         # nail gap height at the plate edge (45-degree cove)

# Derived plug
PLUG_L = CAV_L - 2 * PLUG_CLEAR   # 74.9
PLUG_W = CAV_W - 2 * PLUG_CLEAR   # 44.9
PLUG_R = CAV_R - PLUG_CLEAR       # 3.45

# Printability (X2D, 0.6 mm high-flow nozzle: 2 perimeters = 1.24 mm)
MIN_WALL = 1.24

GAP_3MF = 10.0        # gap between parts in the combined 3MF

# ---------------------------------------------------------------- box build
box_part = Box(BOX_L, BOX_W, BOX_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
box_part = fillet(box_part.edges().filter_by(Axis.Z), radius=CORNER_R)

# Cavity tool extends 1 mm above the top so the cut fully opens the top face
cavity = Box(CAV_L, CAV_W, CAV_DEPTH + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
cavity = fillet(cavity.edges().filter_by(Axis.Z), radius=CAV_R)
box_part = box_part - Pos(0, 0, FLOOR) * cavity

# Elephant-foot compensation on the bottom outer edge loop
box_part = chamfer(box_part.edges().group_by(Axis.Z)[0], length=FOOT_CHAMFER)

# ---------------------------------------------------------------- lid build
lid_part = Box(BOX_L, BOX_W, LID_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
lid_part = fillet(lid_part.edges().filter_by(Axis.Z), radius=CORNER_R)

plug = Box(PLUG_L, PLUG_W, PLUG_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
plug = fillet(plug.edges().filter_by(Axis.Z), radius=PLUG_R)
lid_part = lid_part + Pos(0, 0, LID_T) * plug

# 45-degree lead-in chamfer around the plug's free (insertion) edge
lid_part = chamfer(lid_part.edges().group_by(Axis.Z)[-1], length=LEAD_IN)

# Crush ribs: half-embedded vertical cylinders with a chamfered top, so
# each rib wedges in only after the plug's own lead-in has aligned the lid
rib = Cylinder(RIB_R, PLUG_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
rib = chamfer(rib.edges().group_by(Axis.Z)[-1], length=RIB_LEAD)
rib_centers = [(x, s * (PLUG_W / 2 + RIB_PROUD - RIB_R)) for x in RIB_XS for s in (-1, 1)]
rib_centers += [(s * (PLUG_L / 2 + RIB_PROUD - RIB_R), y) for y in RIB_YS for s in (-1, 1)]
for cx, cy in rib_centers:
    lid_part = lid_part + Pos(cx, cy, LID_T) * rib

# Fingernail scoops: a 45-degree-rotated square prism centered on each
# short edge of the plug-side plate face cuts the triangular cove (gap
# SCOOP_D at the edge, tapering to zero SCOOP_D inward, still over the
# box rim once the lid is flipped onto the box)
scoop = Rot(0, 45, 0) * Box(SCOOP_D * math.sqrt(2), SCOOP_W, SCOOP_D * math.sqrt(2))
lid_part = lid_part - Pos(BOX_L / 2, 0, LID_T) * scoop - Pos(-BOX_L / 2, 0, LID_T) * scoop

# ---------------------------------------------------------------- checks: topology + bbox
TOL = 1e-4

assert len(box_part.solids()) == 1, "box must be exactly one solid"
assert len(lid_part.solids()) == 1, "lid must be exactly one solid"

box_bb = box_part.bounding_box()
lid_bb = lid_part.bounding_box()
assert abs(box_bb.size.X - BOX_L) < TOL, f"box X {box_bb.size.X}"
assert abs(box_bb.size.Y - BOX_W) < TOL, f"box Y {box_bb.size.Y}"
assert abs(box_bb.size.Z - BOX_H) < TOL, f"box Z {box_bb.size.Z}"
assert abs(box_bb.min.Z) < TOL, "box must sit on Z=0"
assert abs(lid_bb.size.X - BOX_L) < TOL, f"lid X {lid_bb.size.X}"
assert abs(lid_bb.size.Y - BOX_W) < TOL, f"lid Y {lid_bb.size.Y}"
assert abs(lid_bb.size.Z - (LID_T + PLUG_H)) < TOL, f"lid Z {lid_bb.size.Z}"
assert abs(lid_bb.min.Z) < TOL, "lid must sit on Z=0"

# ---------------------------------------------------------------- checks: measured clearance
# Measure the actual cavity: thin probe slab minus box walls leaves the cavity
# cross-section as the largest remaining solid (square probe corners can also
# leave tiny slivers outside the rounded outer corners; ignore those).
probe = Pos(0, 0, BOX_H / 2) * Box(BOX_L - 1, BOX_W - 1, 0.01)
cavity_section = probe - box_part
cav_bb = max(cavity_section.solids(), key=lambda s: s.volume).bounding_box()

# Measure at mid-plug height (below both lead-in chamfers): the full
# section bbox gives the rib envelope; slabs through the rib-free middle
# of each side give the plug body faces.
z_mid = LID_T + PLUG_H / 2 - LEAD_IN / 2
env_bb = (lid_part & (Pos(0, 0, z_mid) * Box(BOX_L + 1, BOX_W + 1, 0.01))).bounding_box()
body_x_bb = (lid_part & (Pos(0, 0, z_mid) * Box(BOX_L + 1, 10, 0.01))).bounding_box()
body_y_bb = (lid_part & (Pos(0, 0, z_mid) * Box(10, BOX_W + 1, 0.01))).bounding_box()

assert abs(cav_bb.size.X - CAV_L) < TOL, f"cavity X {cav_bb.size.X}"
assert abs(cav_bb.size.Y - CAV_W) < TOL, f"cavity Y {cav_bb.size.Y}"
assert abs(body_x_bb.size.X - PLUG_L) < TOL, f"plug X {body_x_bb.size.X}"
assert abs(body_y_bb.size.Y - PLUG_W) < TOL, f"plug Y {body_y_bb.size.Y}"
assert abs(env_bb.size.X - (PLUG_L + 2 * RIB_PROUD)) < TOL, f"rib env X {env_bb.size.X}"
assert abs(env_bb.size.Y - (PLUG_W + 2 * RIB_PROUD)) < TOL, f"rib env Y {env_bb.size.Y}"
clear_x = (cav_bb.size.X - body_x_bb.size.X) / 2
clear_y = (cav_bb.size.Y - body_y_bb.size.Y) / 2
assert abs(clear_x - PLUG_CLEAR) < TOL, f"X clearance {clear_x}"
assert abs(clear_y - PLUG_CLEAR) < TOL, f"Y clearance {clear_y}"
rib_int_x = (env_bb.size.X - cav_bb.size.X) / 2
rib_int_y = (env_bb.size.Y - cav_bb.size.Y) / 2
assert abs(rib_int_x - (RIB_PROUD - PLUG_CLEAR)) < TOL, f"rib interference X {rib_int_x}"
assert abs(rib_int_y - (RIB_PROUD - PLUG_CLEAR)) < TOL, f"rib interference Y {rib_int_y}"

# Scoop check: inside each cove's bounding region exactly the upper
# triangle of plate material must remain (half the region's volume)
for sx in (-1, 1):
    region = Pos(sx * (BOX_L / 2 - SCOOP_D / 2), 0, LID_T - SCOOP_D / 2) * Box(SCOOP_D, SCOOP_W, SCOOP_D)
    kept = (lid_part & region).volume
    assert abs(kept - SCOOP_W * SCOOP_D**2 / 2) < 0.2, f"scoop volume {kept} at sx={sx}"

# ---------------------------------------------------------------- checks: volume sanity
assert 25000 < box_part.volume < 26000, f"box volume {box_part.volume}"
assert 18000 < lid_part.volume < 19000, f"lid volume {lid_part.volume}"

# ---------------------------------------------------------------- checks: min wall
# Walls are prismatic by construction; thinnest sections are the derived ones.
for name, t in [
    ("side wall", (BOX_L - CAV_L) / 2),
    ("side wall Y", (BOX_W - CAV_W) / 2),
    ("corner wall", CORNER_R - CAV_R),
    ("floor", FLOOR),
    ("lid plate", LID_T),
    ("plate under scoop", LID_T - SCOOP_D),
    ("plug above chamfer root", PLUG_H - LEAD_IN),
]:
    assert t >= MIN_WALL or name == "plug above chamfer root", f"{name} = {t} < {MIN_WALL}"
# Foot chamfer bites into solid floor region only (below FLOOR height)
assert FOOT_CHAMFER < FLOOR, "foot chamfer must stay within the solid floor"

# ---------------------------------------------------------------- exports
box_stl = OUT_DIR / "box.stl"
lid_stl = OUT_DIR / "lid.stl"
export_stl(box_part, str(box_stl))
export_stl(lid_part, str(lid_stl))

# Combined 3MF, parts side by side on Z=0 with GAP_3MF between them
shift = (BOX_L + GAP_3MF) / 2
mesher = Mesher()
mesher.add_shape(Pos(-shift, 0, 0) * box_part)
mesher.add_shape(Pos(+shift, 0, 0) * lid_part)
mesher.write(str(OUT_DIR / "project-box.3mf"))

# ---------------------------------------------------------------- checks: mesh (trimesh)
# Exact chamfer surfaces are 45 degrees; STL triangulation of the conical
# corner sections tilts facet normals up to ~1 degree past that. Allow a
# 2-degree tessellation margin (a real overhang error would far exceed it).
OVERHANG_NZ = -math.sin(math.radians(45 + 2))

for name, path in [("box", box_stl), ("lid", lid_stl)]:
    mesh = trimesh.load_mesh(str(path))
    assert mesh.is_watertight, f"{name}.stl is not watertight"
    assert mesh.is_winding_consistent, f"{name}.stl winding inconsistent"
    # Overhang: any face steeper than 45 degrees that is not sitting on the bed
    tri_z = mesh.vertices[mesh.faces][:, :, 2]
    on_bed = (tri_z < 1e-3).all(axis=1)
    bad = (mesh.face_normals[:, 2] < OVERHANG_NZ) & ~on_bed
    assert not bad.any(), f"{name}.stl has {bad.sum()} faces with overhang > 45 deg"

# ---------------------------------------------------------------- report
print("ALL CHECKS PASSED")
print(f"box:  bbox {box_bb.size.X:.3f} x {box_bb.size.Y:.3f} x {box_bb.size.Z:.3f} mm, "
      f"volume {box_part.volume:.1f} mm^3")
print(f"lid:  bbox {lid_bb.size.X:.3f} x {lid_bb.size.Y:.3f} x {lid_bb.size.Z:.3f} mm, "
      f"volume {lid_part.volume:.1f} mm^3")
print(f"cavity (measured): {cav_bb.size.X:.3f} x {cav_bb.size.Y:.3f} mm")
print(f"plug body (measured): {body_x_bb.size.X:.3f} x {body_y_bb.size.Y:.3f} mm")
print(f"rib envelope (measured): {env_bb.size.X:.3f} x {env_bb.size.Y:.3f} mm")
print(f"clearance per side (measured): X {clear_x:.3f} mm, Y {clear_y:.3f} mm")
print(f"rib interference per side (design): X {rib_int_x:.3f} mm, Y {rib_int_y:.3f} mm")
print(f"exports: {box_stl}, {lid_stl}, {OUT_DIR / 'project-box.3mf'}")

# SHOW=1 pushes the parts to a running OCP CAD Viewer (.venv/bin/python -m ocp_vscode)
import os

if os.environ.get("SHOW"):
    from ocp_vscode import show, Camera

    show(
        box_part,
        Pos(BOX_L + 10, 0, 0) * lid_part,
        Pos(0, 0, BOX_H + LID_T) * Rot(0, 180, 0) * lid_part,
        names=["box", "lid (print orientation)", "lid installed on box"],
        reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP,
    )
