"""Wall trough for the cord slack under the closet desk (concept D, decided 2026-09-26).

One piece across the X2D bed: 254 mm (10.00 in) wide, 6 in front to back, 6 in deep,
front and side walls 4.5 in, back wall 6 in, one full-width cavity, two screw holes near the top of the back wall.
Printed floor down, open top up, no supports.

Run:  .venv/bin/python projects/Desk-cable-storage/trough.py            (exports STL, self-checks)
      SHOW=reset .venv/bin/python projects/Desk-cable-storage/trough.py (also pushes to the OCP viewer)
      STAGES=<dir> ...                                                  (also writes one STL per build stage)
"""
import os
import pathlib

import trimesh
from build123d import (Align, Axis, Box, Cylinder, Pos, Rot, chamfer, export_stl, fillet)

HERE = pathlib.Path(__file__).resolve().parent
OUT_STL = HERE / "trough.stl"

IN = 25.4
# ---------------- dimensions, mm ----------------
L = 254.0                 # width across the bed, 10.00 in (bed is 256; no exclusion zone on the X2D)
DEPTH = 6 * IN            # front to back, 152.4. Brian, 2026-09-29, after sign-off: "if I print again the container can be a bit narrower from front to back"; try 5 in
H = 6 * IN                # back wall, 152.4
H_FRONT = 4.5 * IN        # front and side walls, 114.3 (75 percent of H; Brian: sides the same height as the face)
T = 2.4                   # floor, front and side walls
T_BACK = 3.2              # back wall, carries the screws
R_OUT = 6.0               # vertical outer corner radius
CH_BOTTOM = 0.8           # chamfer on the bed edge against elephant foot
HOLE_D = 5.0              # #8 screw in a drywall anchor: 4.5 nominal plus print shrink
HOLE_PITCH = 7 * IN       # 177.8, so 1.5 in from each end (Brian: 9 in apart was too close to the ends; 16 in was the wish)
HOLE_DOWN = 0.75 * IN     # hole centres 19.05 below the top edge

MIN = (Align.CENTER, Align.CENTER, Align.MIN)
stages = {}

# 1. outer block with rounded vertical corners
outer = Box(L, DEPTH, H, align=MIN)
outer = fillet(outer.edges().filter_by(Axis.Z), R_OUT)
stages["1-block"] = outer

# 2. one full-width cavity, open at the top
cav = Box(L - 2 * T, DEPTH - T - T_BACK, H, align=MIN)
cav = fillet(cav.edges().filter_by(Axis.Z), R_OUT - T)
cav = Pos(0, (T - T_BACK) / 2, T) * cav
part = outer - cav
stages["2-cavity"] = part

# 3. front and side walls down to 4.5 in; only the back wall keeps the full height
front_cut = Pos(0, (-1 - T_BACK) / 2, H_FRONT) * Box(L + 2, DEPTH + 1 - T_BACK, H, align=MIN)
part = part - front_cut
stages["3-front-wall"] = part

# 4. two screw holes through the back wall
for x in (-HOLE_PITCH / 2, HOLE_PITCH / 2):
    hole = Pos(x, DEPTH / 2 - T_BACK / 2, H - HOLE_DOWN) * Rot(90, 0, 0) * Cylinder(HOLE_D / 2, T_BACK + 2)
    part = part - hole
stages["4-holes"] = part

# 5. bottom chamfer on the bed edge
part = chamfer(part.edges().group_by(Axis.Z)[0], CH_BOTTOM)
stages["5-chamfer"] = part

# ---------------- self-checks ----------------
bb = part.bounding_box()
size = bb.size
assert abs(size.X - L) < 0.01 and abs(size.Y - DEPTH) < 0.01 and abs(size.Z - H) < 0.01, size
assert len(part.solids()) == 1, len(part.solids())
assert size.X <= 256 and size.Y <= 256 and size.Z <= 260, "does not fit the X2D bed"
vol = part.volume
assert 300_000 < vol < 450_000, vol                      # about 390 cm3 of walls
# the cavity is clear: a probe just inside the walls meets no material
probe = Box(L - 2 * T - 0.1, DEPTH - T - T_BACK - 0.1, H - T - 0.1, align=MIN)
probe = Pos(0, (T - T_BACK) / 2, T + 0.05) * fillet(probe.edges().filter_by(Axis.Z), R_OUT - T - 0.05)
assert (part & probe).volume < 1.0, (part & probe).volume
# the front wall really stops at H_FRONT and the back wall reaches H
front_probe = Pos(0, -DEPTH / 2 + T / 2, H_FRONT + 0.05) * Box(L - 2 * R_OUT - 2, T - 0.2, H - H_FRONT - 0.1, align=MIN)
assert (part & front_probe).volume < 1.0, "front wall not cut down"
for sx in (-(L / 2 - T / 2), L / 2 - T / 2):   # side walls stop at the front wall height too
    side_probe = Pos(sx, (T - T_BACK) / 2, H_FRONT + 0.05) * Box(T - 0.2, DEPTH - 2 * R_OUT - T_BACK - 2, H - H_FRONT - 0.1, align=MIN)
    assert (part & side_probe).volume < 1.0, "side wall not cut down"
back_probe = Pos(0, DEPTH / 2 - T_BACK / 2, H - 1) * Box(L - 2 * R_OUT - 2, T_BACK - 0.2, 0.9, align=MIN)
assert abs((part & back_probe).volume - back_probe.volume) < 5, "back wall not full height"
# both holes go through
for x in (-HOLE_PITCH / 2, HOLE_PITCH / 2):
    pin = Pos(x, DEPTH / 2 - T_BACK / 2, H - HOLE_DOWN) * Rot(90, 0, 0) * Cylinder(HOLE_D / 2 - 0.3, T_BACK + 4)
    assert (part & pin).volume < 0.5, "hole blocked"

# ---------------- exports ----------------
export_stl(part, str(OUT_STL))
m = trimesh.load(str(OUT_STL))
assert m.is_watertight, "STL not watertight"
assert abs(m.volume - vol) / vol < 0.01, (m.volume, vol)
if os.environ.get("STAGES"):
    d = pathlib.Path(os.environ["STAGES"]); d.mkdir(parents=True, exist_ok=True)
    for name, s in stages.items():
        export_stl(s, str(d / f"trough-{name}.stl"))
print(f"trough.stl  {size.X:.1f} x {size.Y:.1f} x {size.Z:.1f} mm  volume {vol / 1000:.0f} cm3  "
      f"({vol / 1000 * 1.27:.0f} g PETG)  holes {HOLE_PITCH / IN:.0f} in apart, {HOLE_D} mm")

if os.environ.get("SHOW"):
    from ocp_vscode import Camera, show
    show(part, names=["trough"], reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
