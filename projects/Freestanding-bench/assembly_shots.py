#!/usr/bin/env python
"""Assembly images for the shop page, captured from the OCP CAD viewer
(`scripts/cad-viewer.sh` must have the GPU Chrome tab open).

Writes images/assembly/exploded.png (the whole bench pulled apart), one
step-NN.png per assembly step (parts added in that step in wood colors,
everything already in place in pale grey), and three sub-assembly explosions
(base frame, drawer box, drawer front). STEPS is also imported by
make_cutlist_page.py, so the text and the pictures cannot drift apart.
BASE=legs|blades|gables picks the base, as for the model; the STEPS text
describes the legs base, which is what the shop page documents.

Usage: .venv/bin/python projects/Freestanding-bench/assembly_shots.py
       ONLY=exploded|steps|subs to redo one group
"""
import os
import subprocess
import sys
import time

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Freestanding-bench"
sys.path.insert(0, PROJ)
from freestanding_bench import *  # noqa: E402,F403
from freestanding_bench import INST, HW, BASE_NAMES, inch  # noqa: E402

OUT_DIR = f"{PROJ}/images/assembly"
SETTLE = float(os.environ.get("SETTLE", "2.5"))

# (file stem, title, instance-name prefixes added in this step, shop text); the numbers come from the model
STEPS = [
    ("step-01", "Ends and bottom",
     ("end_", "bottom"),
     f"Glue the case bottom into the rabbets along the bottom of both ends, rabbets and grooves facing in, grooves at "
     f"the rear, show faces out: a {inch(CASE_W)} x {inch(CASE_D - CASE_Y0)} case, {inch(TOP_Z0 - BOT_Z0)} tall. Check for square."),
    ("step-02", "Back",
     ("back",),
     "Slide the 1/4 back down the end grooves until it seats in the bottom groove and glue it all round. With no "
     "wall screws it is what keeps the case square."),
    ("step-03", "Partition",
     ("partition",),
     "Drop the partition into the dado in the bottom with its notch at the top rear, front edge flush with the ends. "
     "Screw up through the bottom."),
    ("step-04", "Nailer",
     ("nailer",),
     "Slide the nailer in on edge through the partition notch, tight against the back and flush with the panel tops. "
     "Glue it to the back and screw through the ends into its ends. No wall screws: the piece is freestanding."),
    ("step-05", "Base frame",
     ("leg_", "brail_"),
     f"Glue and pocket-screw the two {inch(RAIL_H)} in end rails between the front and back legs, centered on the legs "
     f"with their top edges flush with the leg tops, and the back rail between the two back legs; no front rail. Turn "
     f"the case over and set the frame on the case bottom: legs' outer faces {inch(LEG_IN_X)} in from the case ends, "
     f"front legs {inch(LEG_IN_FRONT)} in behind the case front edge, back legs {inch(LEG_IN_BACK)} in inside the case "
     f"back. Pocket screws up into the bottom, then two #8 x 2 down through the bottom into each leg top (they land under "
     f"the drawer boxes). Turn it upright: {inch(CLEAR)} in of clear floor under the case."),
    ("step-06", "Slides",
     ("slide_",),
     "Screw the Blum cabinet members to the ends and the partition, sitting on the case bottom, fronts 3/32 behind "
     "the case front edge. Use the five marked holes per runner."),
    ("step-07", "Drawer boxes",
     ("dside_", "dfront_", "dback_", "dbot_"),
     f"Glue each 1/2 birch box up around its bottom, {inch(BOX_H)} in tall: front and back in the side rabbets, bottom in "
     f"the side and front grooves with its underside {inch(UM_RECESS)} above the side edges, butted to the back and "
     "glued to it. Notches and hook bores at the rear (drill scrap first: the bore leaves a thin skin). Clip the "
     "locking devices under the bottom at the front corners with #6 x 1/2 screws and set the boxes on the runners."),
    ("step-08", "Fronts and pulls",
     ("stile_", "rail_", "panel_", "pull_"),
     f"Glue up each 1/2 panel in its maple frame, back faces flush so the panel sits {inch(FACE_T - PANEL_T)} below "
     f"the maple (groove every piece first, then cut the tongues and tenons to fit). Prime and paint the fronts and "
     f"the case ends white. Hang the fronts {inch(END_REVEAL)} in from each case end, {inch(GAP)} apart and "
     f"{inch(GAP)} under the top, bottoms flush with the case underside, screwed from inside the box through oversize "
     "holes. Center the pulls."),
    ("step-09", "Top",
     ("top",),
     f"Set the {inch(TOP_W)} x {inch(TOP_D)} top flush with the case back, overhanging {inch(END_OVERHANG)} at each "
     f"end and {inch(OVERHANG)} at the front. Pocket screws up into it through the ends and partition near the front; "
     "figure-8s on the nailer at the back so it can move. Osmo Natural on the top, legs and rails."),
    ("step-10", "Cushion",
     ("cushion",),
     "Cushion on. Slide the bench into the alcove with its back 1/2 off the wall. Done."),
]

# exploded offsets (mm) by instance prefix
EXPLODE = {
    "cushion": (0, 0, 480), "top": (0, 0, 300), "nailer": (0, 0, 140), "partition": (0, 0, 160),
    "back": (0, -180, 0), "end_l": (-160, 0, 0), "end_r": (160, 0, 0),
    "leg_": (0, 0, -220), "brail_": (0, 0, -220), "blade_": (0, 0, -220),
    "stile_": (0, 500, 0), "rail_": (0, 500, 0), "panel_": (0, 500, 0), "pull_": (0, 580, 0),
    "dside_": (0, 220, 0), "dfront_": (0, 220, 0), "dback_": (0, 220, 0), "dbot_": (0, 220, 0),
}

COLORS = {
    "hard maple": "#e2c48f", "3/4 maple ply": "#e9d9b0", "1/4 maple ply": "#ecdfbc",
    "1/2 paint-grade panel": "#d9cbb0", "1/2 Baltic birch": "#efe2bd",
}
HW_COLORS = {"slide": "#8c8f94", "pull": "#b8903f", "cushion": "#c9bda8"}
PAINTED = {"front_stile", "front_rail", "front_panel", "end"}   # painted white; the ends are show faces now
PAINT_WHITE = "#fbfbf8"
DONE = "#dedad2"      # already in place
STEM = {
    "end": "end", "bottom": "bottom", "partition": "partition", "nailer": "nailer", "back": "back", "top": "top",
    "stile": "front_stile", "rail": "front_rail", "panel": "front_panel",
    "dside": "drawer_side", "dfront": "drawer_front", "dback": "drawer_back", "dbot": "drawer_bottom",
    "leg": "leg", "brail_end": "base_end_rail", "brail_back": "base_back_rail", "blade": "blade",
}
MATERIAL = {p["name"]: p["material"] for p in PARTS}
ALL = list(INST) + list(HW)
IS_HW = {n for n, _ in HW}


def wood_color(name):
    if name in IS_HW:
        return HW_COLORS[name.split("_")[0]]
    for stem, partname in STEM.items():
        if name == stem or name.startswith(stem + "_"):
            return PAINT_WHITE if partname in PAINTED else COLORS[MATERIAL[partname]]
    raise KeyError(name)


def prefixed(name, prefixes):
    return any(name == p or name.startswith(p) for p in prefixes)


def coverage():
    """every placed part and hardware item belongs to exactly one step"""
    for n, _ in ALL:
        hits = [stem for stem, _t, prefixes, _x in STEPS if prefixed(n, prefixes)]
        assert len(hits) == 1, f"{n} is in {len(hits)} steps: {hits}"
    for n, _ in ALL:
        wood_color(n)


coverage()


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
    print("wrote", os.path.relpath(out, VAULT), os.path.getsize(out), "bytes")


TARGET = (TOP_X0 + TOP_W / 2, (TOP_Y0 + TOP_Y1) / 2, SEAT_Z / 2)
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
    t = (TARGET[0], TARGET[1] + 160, TARGET[2] + 60)
    capture(items, colors, f"{OUT_DIR}/exploded.png", (t[0] - 1700, t[1] + 2600, t[2] + 1500), t, 1.05)


def sub_assemblies():
    D = dict(ALL)
    # base frame: legs (or blades) spread out along X, rails dropped
    off = {}
    for n in sorted(BASE_NAMES):
        if n.startswith("brail_"):
            off[n] = (0, 0, -120)
        else:
            off[n] = (-120 if D[n].bounding_box().center().X < XC else 120, 0, 0)
    items = [(n, Pos(*o) * D[n]) for n, o in off.items()]
    base = Compound(children=[D[n] for n in off]).bounding_box()
    t = (base.center().X, base.center().Y, base.center().Z - 60)
    capture(items, [wood_color(n) for n in off], f"{OUT_DIR}/base-exploded.png",
            (t[0] - 1500, t[1] + 1800, t[2] + 900), t, 1.2)
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
