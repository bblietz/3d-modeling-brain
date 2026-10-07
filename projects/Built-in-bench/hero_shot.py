#!/usr/bin/env python
"""Full-bench image for the top of the cut-list page, captured from the OCP
CAD viewer (Brian's rule: the shop page opens with a full image of the piece
from the viewer, never the matplotlib STL render).

Needs the viewer open in the GPU Chrome (`scripts/cad-viewer.sh`). Pushes
every placed part in wood tones by material plus the hardware, from a
front-left view a little above seat height, and writes images/hero.png.
With CUSHION=0 the cushion is left out so the top shows.

Usage: .venv/bin/python projects/Built-in-bench/hero_shot.py
"""
import os
import sys
import time

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
sys.path.insert(0, PROJ)
from built_in_bench import INST, HW, PARTS, ALCOVE_W, ALCOVE_D, SEAT_Z, TOP_Y1  # noqa: E402
from ocp_vscode import Camera, save_screenshot, set_port, show  # noqa: E402

OUT = os.environ.get("HERO_OUT", f"{PROJ}/images/hero.png")
COLORS = {
    "hard maple": "#e2c48f",
    "3/4 maple ply": "#e9d9b0",
    "1/4 maple ply": "#ecdfbc",
    "3/4 ply (any, hidden)": "#cdbb94",
    "3/4 walnut ply": "#5a3a24",
    "1/2 Baltic birch": "#efe2bd",
}
HW_COLORS = {"slide": "#8c8f94", "pull": "#b8903f", "cushion": "#c9bda8"}

# instance name -> registry part (names are built as <part stem>_<l|r|...>)
STEM = {
    "base_end": "base_end_rail", "base_back": "base_long_rail", "base_front": "base_long_rail",
    "base_center_rail": "base_center_rail", "end": "end", "bottom": "bottom", "partition": "partition",
    "nailer": "nailer", "back": "back", "strip": "scribe_strip", "plinth": "plinth", "top": "top",
    "stile": "front_stile", "rail": "front_rail", "panel": "front_panel",
    "dside": "drawer_side", "dfront": "drawer_front", "dback": "drawer_back", "dbot": "drawer_bottom",
}
MATERIAL = {p["name"]: p["material"] for p in PARTS}


def color(name):
    for stem, partname in STEM.items():
        if name == stem or name.startswith(stem + "_"):
            return COLORS[MATERIAL[partname]]
    raise KeyError(name)


items = list(INST) + [(n, s) for n, s in HW if os.environ.get("CUSHION", "1") != "0" or n != "cushion"]
colors = [color(n) if any(n == x for x, _ in INST) else HW_COLORS[n.split("_")[0]] for n, _ in items]

# the bench front is +Y, its left is -X; look from the front-left, a little above the seat
TARGET = (ALCOVE_W / 2, TOP_Y1 / 2, SEAT_Z / 2)
POSITION = (TARGET[0] - 1500, TARGET[1] + 2700, TARGET[2] + 800)
ZOOM = float(os.environ.get("ZOOM", "1.35"))

set_port(3939)
show(*[s for _, s in items], names=[n for n, _ in items], colors=colors,
     grid=(False, False, False), axes=False, axes0=False,
     reset_camera=Camera.RESET, position=POSITION, target=TARGET, zoom=ZOOM)
time.sleep(float(os.environ.get("SETTLE", "2.5")))   # let the viewer apply the colors before the capture
save_screenshot(OUT)
print("wrote", os.path.relpath(OUT, VAULT), os.path.getsize(OUT), "bytes")
