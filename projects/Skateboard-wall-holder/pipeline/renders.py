"""Check figures and report images for the skateboard hook, from the exported scene STLs in build/.

Design frame is y-up; OpenSCAD is z-up, so the scene is wrapped in rotate([90,0,0]):
design (x, y, z) -> scad (x, -z, y). Cameras below are in scad coordinates.

Usage: .venv/bin/python projects/Skateboard-wall-holder/pipeline/renders.py   (run skateboard_holder.py first)
Writes images/*.png
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PROJ = HERE.parent
sys.path.insert(0, str(HERE))
from render_scene import render  # noqa: E402

B = PROJ / "build"
IMG = PROJ / "images"
HOLDER, TRUCK, NUT, WHEELS, DECK = (str(B / f"{n}.stl") for n in ("holder-design", "truck", "nut", "wheels", "deck"))
C_HOLDER, C_TRUCK, C_NUT, C_WHEEL, C_DECK = "#f28c28", "#aab2bc", "#f6c453", "#f3efe2", "#c9a06a"
WRAP = "rotate([90,0,0])"
# remove design z >= 0, i.e. scad y <= 0, and look at the cut face from scad -y
HALF = "translate([-500,-500,-500]) cube([1000,500,1000]);"

scene = [(HOLDER, C_HOLDER, None), (TRUCK, C_TRUCK, None), (NUT, C_NUT, None), (WHEELS, C_WHEEL, 0.45), (DECK, C_DECK, 0.55)]
solid = [(HOLDER, C_HOLDER, None), (TRUCK, C_TRUCK, None), (NUT, C_NUT, None), (WHEELS, C_WHEEL, None), (DECK, C_DECK, None)]

jobs = {
    "docked-iso": dict(parts=scene, camera="260,-300,170,45,0,-45", wrap=WRAP),
    "docked-side": dict(parts=solid, camera="45,-420,-40,45,0,-40", wrap=WRAP, clip=HALF, projection="ortho"),
    "cradle-detail": dict(parts=solid, camera="52,-150,-38,52,0,-38", wrap=WRAP, clip=HALF, projection="ortho"),
    "from-room": dict(parts=[p for p in scene if p[0] != DECK], camera="500,0,-45,40,0,-45", wrap=WRAP, projection="ortho"),
    "holder-iso": dict(parts=[(HOLDER, C_HOLDER, None)], camera="230,-230,120,36,0,-60", wrap=WRAP),
    "holder-top": dict(parts=[(HOLDER, C_HOLDER, None)], camera="36,0,300,36,0,-60", wrap=WRAP, projection="ortho"),
    "print-bed": dict(parts=[(str(PROJ / "skateboard-holder.stl"), C_HOLDER, None)], camera="230,-300,200,36,-60,15"),
}
for name, kw in jobs.items():
    out = render(IMG / f"{name}.png", imgsize=(1200, 1000), **kw)
    print("wrote", out.relative_to(PROJ))
