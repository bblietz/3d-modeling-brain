#!/usr/bin/env python
"""Assembly images for the shop page, captured from the OCP CAD viewer
(`scripts/cad-viewer.sh` must have the GPU Chrome tab open).

Writes images/assembly/exploded.png (the whole bench pulled apart), one
step-NN.png per assembly step (parts added in that step in wood colors,
everything already in place in pale grey), and two sub-assembly explosions
(drawer box, drawer front). STEPS is also imported by make_cutlist_page.py,
so the text and the pictures cannot drift apart.

Usage: .venv/bin/python projects/Built-in-bench/assembly_shots.py
"""
import os
import subprocess
import sys
import time

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
sys.path.insert(0, PROJ)
from built_in_bench import *  # noqa: E402,F403
from built_in_bench import INST, HW  # noqa: E402

OUT_DIR = f"{PROJ}/images/assembly"
SETTLE = float(os.environ.get("SETTLE", "2.5"))

# (file stem, title, instance-name prefixes added in this step, shop text)
STEPS = [
    ("step-01", "Base ladder",
     ("base_",),
     "Glue and screw the five rails into a 64 x 23-1/2 ladder, 4 in tall. Set it in the alcove with its front edge "
     "23-1/2 in from the back wall, level it on shims and screw it to the floor."),
    ("step-02", "Ends and bottom",
     ("end_", "bottom"),
     "Stand the two end panels on the base end rails, rabbets and grooves facing in, grooves at the rear. Glue the "
     "case bottom into the rabbets along the bottom of both ends and screw up through the base. Check for square."),
    ("step-03", "Back",
     ("back",),
     "Slide the 1/4 back down the end grooves until it seats in the bottom groove. No glue; the nailer pins it later."),
    ("step-04", "Partition",
     ("partition",),
     "Drop the partition into the dado in the bottom with its notch at the top rear, front edge flush with the ends. "
     "Screw up through the bottom."),
    ("step-05", "Nailer",
     ("nailer",),
     "Slide the nailer in on edge through the partition notch, tight against the back and flush with the panel tops. "
     "Screw through the ends into its ends, then through the nailer and the back into the wall studs."),
    ("step-06", "Scribe strips and plinth",
     ("strip_", "plinth"),
     "Scribe both strips to the walls and glue them to the ends' front edges with biscuits, inner edges flush with "
     "the inside of the ends. Scribe the plinth to the floor and screw it to the base front rail with its top edge "
     "1/8 below the case bottom."),
    ("step-07", "Slides",
     ("slide_",),
     "Screw the Blum cabinet members to the ends and the partition, sitting on the case bottom, fronts 3/32 behind "
     "the case front edge. Use the five marked holes per runner."),
    ("step-08", "Drawer boxes",
     ("dside_", "dfront_", "dback_", "dbot_"),
     "Glue each box up around its bottom: front and back in the side rabbets, bottom in the grooves with its "
     "underside 1/2 above the side edges, notches and hook bores at the rear. Clip the locking devices under the "
     "bottom at the front corners and set the boxes on the runners."),
    ("step-09", "Fronts and pulls",
     ("stile_", "rail_", "panel_", "pull_"),
     "Glue up each walnut panel in its maple frame (groove every piece first, then cut the tongues and tenons to "
     "fit). Hang the fronts with 1/8 reveals all round, screwed from inside the box through oversize holes. "
     "Center the pulls."),
    ("step-10", "Top",
     ("top",),
     "Set the top with its front edge 25 in from the back wall (3 in back from the pilaster faces) and 3/8 off the "
     "back wall. Pocket screws up into it through the ends and partition near the front; figure-8s on the nailer "
     "at the back so it can move toward the wall."),
    ("step-11", "Cushion",
     ("cushion",),
     "Cushion on. Done."),
]

# exploded offsets (mm) by instance prefix
EXPLODE = {
    "cushion": (0, 0, 480), "top": (0, 0, 300), "nailer": (0, 0, 140), "partition": (0, 0, 160),
    "back": (0, -180, 0), "end_l": (-160, 0, 0), "end_r": (160, 0, 0), "base_": (0, 0, -200),
    "strip_l": (-160, 500, 0), "strip_r": (160, 500, 0), "plinth": (0, 500, 0),
    "stile_": (0, 500, 0), "rail_": (0, 500, 0), "panel_": (0, 500, 0), "pull_": (0, 580, 0),
    "dside_": (0, 220, 0), "dfront_": (0, 220, 0), "dback_": (0, 220, 0), "dbot_": (0, 220, 0),
}

COLORS = {
    "hard maple": "#e2c48f", "3/4 maple ply": "#e9d9b0", "1/4 maple ply": "#ecdfbc",
    "3/4 ply (any, hidden)": "#cdbb94", "3/4 walnut ply": "#5a3a24", "1/2 Baltic birch": "#efe2bd",
}
HW_COLORS = {"slide": "#8c8f94", "pull": "#b8903f", "cushion": "#c9bda8"}
DONE = "#dedad2"      # already in place
STEM = {
    "base_end": "base_end_rail", "base_back": "base_long_rail", "base_front": "base_long_rail",
    "base_center_rail": "base_center_rail", "end": "end", "bottom": "bottom", "partition": "partition",
    "nailer": "nailer", "back": "back", "strip": "scribe_strip", "plinth": "plinth", "top": "top",
    "stile": "front_stile", "rail": "front_rail", "panel": "front_panel",
    "dside": "drawer_side", "dfront": "drawer_front", "dback": "drawer_back", "dbot": "drawer_bottom",
}
MATERIAL = {p["name"]: p["material"] for p in PARTS}
ALL = list(INST) + list(HW)
IS_HW = {n for n, _ in HW}


def wood_color(name):
    if name in IS_HW:
        return HW_COLORS[name.split("_")[0]]
    for stem, partname in STEM.items():
        if name == stem or name.startswith(stem + "_"):
            return COLORS[MATERIAL[partname]]
    raise KeyError(name)


def prefixed(name, prefixes):
    return any(name == p or name.startswith(p) for p in prefixes)


def capture(items, colors, out, position, target, zoom):
    from ocp_vscode import Camera, save_screenshot, set_port, show
    set_port(3939)
    show(*[s for _, s in items], names=[n for n, _ in items], colors=colors,
         grid=(False, False, False), axes=False, axes0=False,
         reset_camera=Camera.RESET, position=position, target=target, zoom=zoom)
    try:   # park the pointer in the screen corner so the viewer's hover highlight does not tint a face
        subprocess.run(["xdotool", "mousemove", "2", "2"], check=False, timeout=5)
    except Exception:
        pass
    time.sleep(SETTLE)
    save_screenshot(out)
    print("wrote", os.path.relpath(out, VAULT))


TARGET = (ALCOVE_W / 2, TOP_Y1 / 2, SEAT_Z / 2)
POS = (TARGET[0] - 1500, TARGET[1] + 2300, TARGET[2] + 1500)   # a little higher than the hero, to see inside


def step_images():
    placed = []
    for stem, title, prefixes, text in STEPS:
        new = [(n, s) for n, s in ALL if prefixed(n, prefixes)]
        assert new, f"step {stem} adds nothing: {prefixes}"
        items = placed + new
        colors = [DONE] * len(placed) + [wood_color(n) for n, _ in new]
        capture(items, colors, f"{OUT_DIR}/{stem}.png", POS, TARGET, 1.2)
        placed = items
    assert len(placed) == len(ALL), "steps do not cover every placed part"


def exploded():
    items, colors = [], []
    for n, s in ALL:
        off = next((v for k, v in EXPLODE.items() if prefixed(n, (k,))), (0, 0, 0))
        items.append((n, Pos(*off) * s if any(off) else s))
        colors.append(wood_color(n))
    t = (TARGET[0], TARGET[1] + 160, TARGET[2] + 160)
    capture(items, colors, f"{OUT_DIR}/exploded.png", (t[0] - 1700, t[1] + 2600, t[2] + 1500), t, 1.05)


def sub_assemblies():
    D = dict(ALL)
    # drawer box: sides out, front and back forward/back, bottom down
    off = {"dside_ll": (-120, 0, 0), "dside_lr": (120, 0, 0), "dfront_l": (0, 140, 0), "dback_l": (0, -140, 0),
           "dbot_l": (0, 0, -110)}
    items = [(n, Pos(*o) * D[n]) for n, o in off.items()]
    bb = D["dside_ll"].bounding_box()
    t = (BOX_W / 2 + bb.min.X, BOX_Y0 + BOX_D / 2, BOX_Z0 + BOX_H / 2 - 40)
    capture(items, [wood_color(n) for n in off], f"{OUT_DIR}/drawer-exploded.png",
            (t[0] - 900, t[1] + 1300, t[2] + 800), t, 1.5)
    # drawer front: stiles out, rails up and down, panel forward
    off = {"stile_ll": (-90, 0, 0), "stile_lr": (90, 0, 0), "rail_lt": (0, 0, 90), "rail_lb": (0, 0, -90),
           "panel_l": (0, 120, 0)}
    items = [(n, Pos(*o) * D[n]) for n, o in off.items()]
    t = (FRONT_X0[0] + FRONT_W / 2, FACE_Y1 + 60, FRONT_Z0 + FRONT_H / 2)
    capture(items, [wood_color(n) for n in off], f"{OUT_DIR}/front-exploded.png",
            (t[0] - 500, t[1] + 1400, t[2] + 600), t, 1.5)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    only = os.environ.get("ONLY")          # ONLY=exploded|steps|subs to redo one group
    if only in (None, "exploded"):
        exploded()
    if only in (None, "steps"):
        step_images()
    if only in (None, "subs"):
        sub_assemblies()
    print("assembly images done")
