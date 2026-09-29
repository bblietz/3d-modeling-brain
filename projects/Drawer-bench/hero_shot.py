#!/usr/bin/env python
"""Full-bench image for the top of the cut-list page, captured from the OCP
CAD viewer (Brian, 2026-09-28: the shop page always starts with a full
image of the piece, taken from the viewer, not the matplotlib STL render).

Needs the viewer open in the GPU Chrome (`scripts/cad-viewer.sh`). Pushes
every placed part in wood tones by material with a fixed front-left view,
asks the viewer for a screenshot and writes images/hero.png. The viewer is
left showing that view; the next `SHOW=1 drawer_bench.py` restores the
default colors.

Usage: .venv/bin/python projects/Drawer-bench/hero_shot.py
"""
import os
import sys

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Drawer-bench"
sys.path.insert(0, PROJ)
from drawer_bench import INST, PARTS, TOP_W, TOP_D, H  # noqa: E402  runs the model's checks once
from ocp_vscode import Camera, save_screenshot, set_port, show  # noqa: E402

OUT = f"{PROJ}/images/hero.png"
COLORS = {
    "soft maple": "#d3ae6e",
    "3/4 ply": "#e8d7ad",
    "1/2 ply": "#e8d7ad",
    "1/4 ply": "#ecdfbc",
    "maple butcherblock (Boos match)": "#c79a62",
}
MATERIAL = {p["name"]: p["material"] for p in PARTS}


def material(inst_name):
    """Placed-instance name to its registry part's material (post_fl -> post_front,
    side_l -> side, drawer_side_bot_r -> drawer_side_bot)."""
    if inst_name.startswith("post_"):
        return MATERIAL["post_front" if inst_name[5] == "f" else "post_rear"]
    base = inst_name[:-2] if inst_name.endswith(("_l", "_r")) else inst_name
    return MATERIAL[base]


# Front-left three-quarter view from a little above; the model's front is -Y,
# its left is -X, Z is up.
TARGET = (TOP_W / 2, TOP_D / 2, H / 2)
POSITION = (TARGET[0] - 1700, TARGET[1] - 2300, TARGET[2] + 950)
ZOOM = 1.3   # the canvas is the viewer window; this fills it with the bench

set_port(3939)
show(*[s for _, s in INST], names=[n for n, _ in INST],
     colors=[COLORS[material(n)] for n, _ in INST],
     grid=(False, False, False), axes=False, axes0=False,
     reset_camera=Camera.RESET, position=POSITION, target=TARGET, zoom=ZOOM)
save_screenshot(OUT)
print("wrote", os.path.relpath(OUT, VAULT), os.path.getsize(OUT), "bytes")
