"""Parametric project box with friction-fit lid (build123d).

Single-color PLA, Bambu Lab X2D. Target nozzle is set by NOZZLE below.
Both parts are modeled in their print orientation, sitting on Z=0:
  - box: floor on bed, open top up
  - lid: plate on bed, plug pointing up

Running this file builds both parts, runs assertion checks (dimensions,
clearance, solids count, volume, watertightness, overhangs, and a
re-measure of the fit on the tessellated meshes), and exports box.stl,
lid.stl, and project-box.3mf next to this file.

project-box.3mf carries geometry only. The print-ready file with the
X2D presets, bed type, plate temps and ironing package baked in is built
by pipeline/make_print_3mf.py.
"""

import math
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from trimesh.intersections import mesh_plane
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
# instead: predicted crush ~0.145 mm per side at each rib.
#
# CALIBRATION PROVENANCE - PLUG_CLEAR and RIB_PROUD are not portable
# constants, they are the result of one calibration:
#   nozzle 0.6 high-flow | wall generator classic (X2D stock preset)
#   PLA Basic, the spool loaded 2026-07-31 | 0.18 mm layers
# Any of these changing invalidates the fit, so re-run a coupon first:
#   - filament brand or line: a coupon-validated +0.02 mm interference
#     printed smash-tight after a manufacturer change (clawd-mascot).
#   - nozzle: changes the extrusion width the 0.35 mm crest is built from.
#   - wall generator: classic can absorb a sub-line-width crest into the
#     perimeter; arachne gives it its own variable-width bead.
# See knowledge/friction-fits-x2d.md.
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

# ------------------------------------------------------------- target profile
# NOZZLE is the nozzle this part is designed to be printed with. The box is
# a coarse part with 2.4 mm walls and a flat ironed lid top, so 0.6 high-flow
# is the right nozzle: full speed and strength, and the ironing package in
# pipeline/make_print_3mf.py is a set of 0.6 numbers (0.55 top line width).
#
# PRE-FLIGHT, every time (knowledge/printer-x2d.md):
#   1. Resident nozzle is 0.2 mm in BOTH positions since 2026-08-23, so
#      printing this part needs a physical swap back to the 0.6 high-flow.
#   2. Confirm what is actually mounted with scripts/x2d-status.py (reads
#      the printer over LAN), not from memory.
#   3. Select the 0.6 printer preset in Studio's Prepare tab BEFORE opening
#      the project. Studio silently re-profiles an imported project to the
#      resident machine and re-slices; no mismatch warning fires anywhere.
NOZZLE = 0.6
LAYER_H = 0.18        # target process preset layer height
FIRST_LAYER_H = 0.3   # first layer shifts the whole layer grid

# Minimum printable wall = 2 perimeters. This is a hard slicer floor, not a
# quality preference: the stock X2D quality presets use the CLASSIC wall
# generator with detect_thin_wall off, so anything thinner is silently not
# printed at all and no slice-time warning appears.
MIN_WALL_BY_NOZZLE = {0.2: 0.44, 0.4: 0.84, 0.6: 1.24}
MIN_WALL = MIN_WALL_BY_NOZZLE[NOZZLE]

# Tessellation band for re-measuring the fit on the exported meshes. Source
# features that pass at 0.88-0.90 mm have measured 0.80-0.83 mm on the mesh
# (sharks-nametag), and 0.15 mm clearance is inside the band where the
# faceting of the r=3.45 / r=3.60 corner fillets matters.
MESH_BAND = 0.05

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
three_mf = OUT_DIR / "project-box.3mf"
mesher = Mesher()
mesher.add_shape(Pos(-shift, 0, 0) * box_part)
mesher.add_shape(Pos(+shift, 0, 0) * lid_part)
mesher.write(str(three_mf))

# ---------------------------------------------------------------- checks: mesh (trimesh)
# Exact chamfer surfaces are 45 degrees; STL triangulation of the conical
# corner sections tilts facet normals up to ~1 degree past that. Allow a
# 2-degree tessellation margin (a real overhang error would far exceed it).
OVERHANG_NZ = -math.sin(math.radians(45 + 2))

meshes = {}
for name, path in [("box", box_stl), ("lid", lid_stl)]:
    mesh = trimesh.load_mesh(str(path))
    meshes[name] = mesh
    assert mesh.is_watertight, f"{name}.stl is not watertight"
    assert mesh.is_winding_consistent, f"{name}.stl winding inconsistent"
    # Overhang: any face steeper than 45 degrees that is not sitting on the bed
    tri_z = mesh.vertices[mesh.faces][:, :, 2]
    on_bed = (tri_z < 1e-3).all(axis=1)
    bad = (mesh.face_normals[:, 2] < OVERHANG_NZ) & ~on_bed
    assert not bad.any(), f"{name}.stl has {bad.sum()} faces with overhang > 45 deg"


# --------------------------------------------------- checks: fit on the mesh
# The asserts above measure the B-rep at 1e-4. What actually gets printed is
# the tessellation, where the chorded corner fillets cut inside the true
# surface. Re-measure the fit on the exported STLs and confirm it survives.
def section_xy(mesh, z):
    """XY points where the mesh crosses the Z=z plane."""
    segs = mesh_plane(mesh, plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
    assert len(segs), f"no section at z={z}"
    return segs.reshape(-1, 3)[:, :2]


# Box cavity: at mid height the section has two loops. Cavity points are the
# only ones inside both design half-extents; every point on the outer loop
# (including the corner arcs) breaks at least one.
box_pts = section_xy(meshes["box"], BOX_H / 2)
inner = box_pts[
    (np.abs(box_pts[:, 0]) <= CAV_L / 2 + 0.3) & (np.abs(box_pts[:, 1]) <= CAV_W / 2 + 0.3)
]
assert len(inner), "no cavity loop found in the box mesh section"
m_cav_x, m_cav_y = np.ptp(inner[:, 0]), np.ptp(inner[:, 1])

# Lid at mid-plug height: full section is the rib envelope; the rib-free
# middle of each side gives the plug body faces (same windows as the B-rep).
lid_pts = section_xy(meshes["lid"], z_mid)
m_env_x, m_env_y = np.ptp(lid_pts[:, 0]), np.ptp(lid_pts[:, 1])
m_body_x = np.ptp(lid_pts[np.abs(lid_pts[:, 1]) < 5][:, 0])
m_body_y = np.ptp(lid_pts[np.abs(lid_pts[:, 0]) < 5][:, 1])

for label, measured, design in [
    ("cavity X", m_cav_x, CAV_L),
    ("cavity Y", m_cav_y, CAV_W),
    ("plug body X", m_body_x, PLUG_L),
    ("plug body Y", m_body_y, PLUG_W),
    ("rib envelope X", m_env_x, PLUG_L + 2 * RIB_PROUD),
    ("rib envelope Y", m_env_y, PLUG_W + 2 * RIB_PROUD),
]:
    assert abs(measured - design) < MESH_BAND, (
        f"mesh {label} = {measured:.3f} vs design {design:.3f} "
        f"(over the {MESH_BAND} mm tessellation band)"
    )

m_clear_x = (m_cav_x - m_body_x) / 2
m_clear_y = (m_cav_y - m_body_y) / 2
m_rib_x = (m_env_x - m_cav_x) / 2
m_rib_y = (m_env_y - m_cav_y) / 2
# The ribs own the fit, so the interference is the number that must survive
# tessellation; a mesh that ate half of it would print loose.
for label, measured in [("X", m_rib_x), ("Y", m_rib_y)]:
    assert measured > (RIB_PROUD - PLUG_CLEAR) * 0.8, (
        f"mesh rib interference {label} = {measured:.3f} mm, "
        f"under 80% of the designed {RIB_PROUD - PLUG_CLEAR:.3f} mm"
    )

# ------------------------------------------------------------- checks: 3MF
# trimesh cannot load 3MF without networkx, so verify by parsing the model
# part inside the zip. The 3MF is what goes to the slicer; nothing else here
# would catch a Mesher that wrote the wrong object count or placement.
NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
with zipfile.ZipFile(three_mf) as zf:
    model = ET.fromstring(zf.read("3D/3dmodel.model"))

# Mesher also emits an empty component wrapper per shape; the build items are
# what the slicer places, and they point at the mesh objects.
items = model.findall(".//m:build/m:item", NS)
assert len(items) == 2, f"3MF has {len(items)} build items, expected 2"

by_id = {o.get("id"): o for o in model.findall(".//m:resources/m:object", NS)}
obj_bounds = []
for item in items:
    obj = by_id[item.get("objectid")]
    verts = np.array(
        [
            [float(v.get("x")), float(v.get("y")), float(v.get("z"))]
            for v in obj.findall(".//m:mesh/m:vertices/m:vertex", NS)
        ]
    )
    assert len(verts), f"3MF build item points at object {obj.get('id')} with no mesh"
    obj_bounds.append((verts.min(axis=0), verts.max(axis=0)))

# Identify by size rather than document order (object order is not guaranteed)
obj_bounds.sort(key=lambda b: (b[1] - b[0])[2])
lid_lo, lid_hi = obj_bounds[0]
box_lo, box_hi = obj_bounds[1]
for label, lo, hi, size in [
    ("3MF box", box_lo, box_hi, (BOX_L, BOX_W, BOX_H)),
    ("3MF lid", lid_lo, lid_hi, (BOX_L, BOX_W, LID_T + PLUG_H)),
]:
    got = hi - lo
    assert np.allclose(got, size, atol=MESH_BAND), f"{label} bbox {got} vs {size}"
    assert abs(lo[2]) < MESH_BAND, f"{label} does not sit on Z=0 (min Z {lo[2]:.3f})"
gap = lid_lo[0] - box_hi[0] if lid_lo[0] > box_hi[0] else box_lo[0] - lid_hi[0]
assert abs(gap - GAP_3MF) < MESH_BAND, f"3MF part gap {gap:.3f} vs {GAP_3MF}"

# ---------------------------------------------------------------- report
print("ALL CHECKS PASSED")
print(f"target: {NOZZLE} mm nozzle, {LAYER_H} mm layers, min wall {MIN_WALL} mm")
print(f"box:  bbox {box_bb.size.X:.3f} x {box_bb.size.Y:.3f} x {box_bb.size.Z:.3f} mm, "
      f"volume {box_part.volume:.1f} mm^3")
print(f"lid:  bbox {lid_bb.size.X:.3f} x {lid_bb.size.Y:.3f} x {lid_bb.size.Z:.3f} mm, "
      f"volume {lid_part.volume:.1f} mm^3")
print(f"cavity (measured): {cav_bb.size.X:.3f} x {cav_bb.size.Y:.3f} mm")
print(f"plug body (measured): {body_x_bb.size.X:.3f} x {body_y_bb.size.Y:.3f} mm")
print(f"rib envelope (measured): {env_bb.size.X:.3f} x {env_bb.size.Y:.3f} mm")
print(f"clearance per side (measured): X {clear_x:.3f} mm, Y {clear_y:.3f} mm")
print(f"rib interference per side (design): X {rib_int_x:.3f} mm, Y {rib_int_y:.3f} mm")
print("on the exported mesh:")
print(f"  cavity {m_cav_x:.3f} x {m_cav_y:.3f} mm, plug body {m_body_x:.3f} x {m_body_y:.3f} mm, "
      f"rib envelope {m_env_x:.3f} x {m_env_y:.3f} mm")
print(f"  clearance per side X {m_clear_x:.3f} mm, Y {m_clear_y:.3f} mm; "
      f"rib interference X {m_rib_x:.3f} mm, Y {m_rib_y:.3f} mm")

# Layer grid: a FIRST_LAYER_H first layer over LAYER_H layers offsets the
# whole grid, so a designed Z that is an exact multiple of the layer height
# does not land on a slice plane. Advisory: the slicer rounds to the layer
# below, which shortens the feature by up to one layer.
print(f"layer grid ({FIRST_LAYER_H} mm first layer, {LAYER_H} mm layers):")
for label, z in [
    ("lid plate top / plug root", LID_T),
    ("plug tip", LID_T + PLUG_H),
    ("scoop root (thinnest plate)", LID_T - SCOOP_D),
    ("box rim", BOX_H),
    ("cavity floor", FLOOR),
]:
    n = (z - FIRST_LAYER_H) / LAYER_H
    off = (round(n) - n) * LAYER_H
    flag = "on a layer" if abs(off) < 1e-6 else f"{abs(off):.3f} mm off the nearest layer"
    print(f"  z {z:5.2f} -> layer {n:6.2f}: {flag}")

print(f"exports: {box_stl}, {lid_stl}, {three_mf}")

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
