#!/usr/bin/env python
"""Full-bench image for the top of the cut-list page, captured from the OCP
CAD viewer (Brian's rule: the shop page opens with a full image of the piece
from the viewer, never the matplotlib STL render).

Needs the viewer open in the GPU Chrome (`scripts/cad-viewer.sh`). Pushes
every placed part in wood tones by material (painted parts white) plus the
hardware, from a front-left view a little above seat height, and writes
images/hero.png (HERO_OUT to write elsewhere). With CUSHION=0 the cushion is
left out so the top shows. BASE=legs|blades|gables picks the base, as for the
model. Compare the byte count with the previous capture: an identical count
means the viewer tab has stopped taking pushes (restart it with
`pkill -f cad-viewer-chrome` and `scripts/cad-viewer.sh`).

Usage: .venv/bin/python projects/Freestanding-bench/hero_shot.py
"""
import os
import sys
import time

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Freestanding-bench"
sys.path.insert(0, PROJ)
from freestanding_bench import INST, HW, PARTS, TOP_X0, TOP_W, TOP_Y0, TOP_Y1, SEAT_Z  # noqa: E402
from ocp_vscode import Camera, save_screenshot, set_port, show  # noqa: E402

OUT = os.environ.get("HERO_OUT", f"{PROJ}/images/hero.png")
COLORS = {
    "hard maple": "#e2c48f",
    "soft maple": "#e2c48f",
    "3/4 maple ply": "#e9d9b0",
    "1/2 maple ply": "#ecdfbc",
    "1/2 paint-grade panel": "#d9cbb0",
    "1/2 Baltic birch": "#efe2bd",
}
HW_COLORS = {"slide": "#8c8f94", "pull": "#b8903f", "cushion": "#c9bda8"}
PAINTED = {"front_stile", "front_rail", "front_panel", "end", "back"}   # painted white; the ends are show faces now
PAINT_WHITE = "#fbfbf8"

# instance name -> registry part (names are built as <part stem>_<l|r|...>, the posts by exact name)
STEM = {
    "post_fl": "post_front", "post_fr": "post_front", "post_rl": "post_rear", "post_rr": "post_rear",
    "end": "end", "bottom": "bottom", "partition": "partition", "cleat": "cleat", "back": "back", "top": "top",
    "stile": "front_stile", "rail": "front_rail", "panel": "front_panel",
    "dside": "drawer_side", "dfront": "drawer_front", "dback": "drawer_back", "dbot": "drawer_bottom",
}
MATERIAL = {p["name"]: p["material"] for p in PARTS}


def color(name):
    for stem, partname in STEM.items():
        if name == stem or name.startswith(stem + "_"):
            return PAINT_WHITE if partname in PAINTED else COLORS[MATERIAL[partname]]
    raise KeyError(name)


items = list(INST) + [(n, s) for n, s in HW if os.environ.get("CUSHION", "1") != "0" or n != "cushion"]
colors = [color(n) if any(n == x for x, _ in INST) else HW_COLORS[n.split("_")[0]] for n, _ in items]

# the bench front is +Y; the camera sits at low X, which is the viewer's right when facing the bench
TARGET = (TOP_X0 + TOP_W / 2, (TOP_Y0 + TOP_Y1) / 2, SEAT_Z / 2)
POSITION = (TARGET[0] - 1500, TARGET[1] + 2700, TARGET[2] + float(os.environ.get("CAM_UP", "650")))
ZOOM = float(os.environ.get("ZOOM", "1.35"))

set_port(3939)
show(*[s for _, s in items], names=[n for n, _ in items], colors=colors,
     grid=(False, False, False), axes=False, axes0=False,
     reset_camera=Camera.RESET, position=POSITION, target=TARGET, zoom=ZOOM)
time.sleep(float(os.environ.get("SETTLE", "2.5")))   # let the viewer apply the colors before the capture
save_screenshot(OUT)
print("wrote", os.path.relpath(OUT, VAULT), os.path.getsize(OUT), "bytes")
