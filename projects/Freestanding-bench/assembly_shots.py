#!/usr/bin/env python
"""Assembly images for the shop page, captured from the OCP CAD viewer
(`scripts/cad-viewer.sh` must have the GPU Chrome tab open).

Writes images/assembly/exploded.png (the whole bench pulled apart), one
step-NN.png per assembly step (parts added in that step in wood colors,
everything already in place in pale grey), and three sub-assembly explosions
(one end with its two posts, drawer box, drawer front). STEPS is also
imported by make_cutlist_page.py, so the text and the pictures cannot drift
apart. The bench stands on four proud corner posts (Brian's pick A,
2026-10-26: the drawer bench's construction).

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
from freestanding_bench import INST, HW, inch  # noqa: E402

OUT_DIR = f"{PROJ}/images/assembly"
SETTLE = float(os.environ.get("SETTLE", "2.5"))

# (file stem, title, instance-name prefixes added in this step, shop text); the numbers come from the model
STEPS = [
    ("step-01", "Posts",
     ("post_",),
     f"Four {inch(POST)} square soft maple posts, {inch(TOP_Z0)} long. Chamfer the four vertical edges {inch(CHAMFER)} "
     f"first, full length, then cut the stopped grooves: the end-panel groove on the face toward the other post of that "
     f"end, {inch(SETBACK)} in from the outer face, {inch(GROOVE_D)} deep, from {inch(GROOVE_STOP)} up and out the top; "
     f"the rear posts also take the back's groove on the inner face, {inch(SETBACK)} in from the rear face, same stop. "
     f"Notch the rear posts {inch(BB_NOTCH_D)} x {inch(BB_NOTCH_H)} across the rear face at the floor for the baseboard "
     f"and shoe (skip it if the baseboard comes out). Drill the front posts' Blum runner screw holes on the inner face, "
     f"{inch(UM_SCREW_Y[0] + RUNNER_SETBACK)} and {inch(UM_SCREW_Y[1] + RUNNER_SETBACK)} behind the front face."),
    ("step-02", "End assemblies",
     ("end_",),
     f"Glue each end panel into its front and rear post: tongues in the grooves above the {inch(NOTCH_H)} notches, the "
     f"notched bottom on the post faces, top edge flush with the post tops, show face out. Check that each end is square "
     f"and both posts stand plumb before the glue sets."),
    ("step-03", "Back and cleat",
     ("back", "cleat"),
     f"Slide the 1/2 back down the rear posts' grooves to join the two end assemblies, notched bottom on the post faces, "
     f"and glue it: with no wall screws it is what keeps the case square. Glue the cleat inside along the back's top edge "
     f"between the rear posts and screw it from the inside (#8 x 1, countersunk, nothing through the back)."),
    ("step-04", "Bottom",
     ("bottom",),
     f"Slide the case bottom in from the front into the {inch(RABBET_D)} rabbets of both ends and the back, its corner "
     f"notches around the four posts, and glue it. Its underside is the ceiling of the {inch(CLEAR)} in of clear floor; "
     f"screw up through it into the partition after the next step."),
    ("step-05", "Partition",
     ("partition",),
     f"Drop the partition into the dado in the bottom, against the back, with its notch at the top rear around the cleat "
     f"and its front edge on the fronts' back-face line, {inch(FRONT_SETBACK + FACE_T)} behind the post faces. Screw up "
     f"through the bottom."),
    ("step-06", "Slides and brackets",
     ("slide_",),
     f"Post-side runners: front screws into the posts' inner faces (#6 x 5/8), rears on Blum brackets screwed to the back "
     f"with #6 x 1/2. Partition-side runners: screwed to the partition the frameless way. All four level on the case "
     f"bottom, fronts {inch(UM_FRONT_GAP)} behind the fronts' back-face line."),
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
     f"the ends white. Hang the fronts between the front posts: {inch(GAP)} to each post, {inch(GAP)} between them, "
     f"{inch(GAP)} under the top, bottoms flush with the case underside, faces {inch(FRONT_SETBACK)} behind the post "
     "faces, screwed from inside the box through oversize holes. Center the pulls."),
    ("step-09", "Top",
     ("top",),
     f"Set the {inch(TOP_W)} x {inch(TOP_D)} top overhanging the posts {inch(OVERHANG)} at each end and the front, flush "
     f"with their rear faces. Pocket screws up into it through the ends and partition near the front; figure-8s on the "
     "cleat at the back so it can move. Osmo Natural on the top and the posts."),
    ("step-10", "Cushion",
     ("cushion",),
     f"Cushion on. Slide the bench into the alcove with its back {inch(WALL_GAP)} off the wall, the rear posts over the "
     "baseboard. Done."),
]

# exploded offsets (mm) by instance name or prefix
EXPLODE = {
    "cushion": (0, 0, 480), "top": (0, 0, 300), "cleat": (0, 0, 140), "partition": (0, 0, 160),
    "back": (0, -180, 0), "end_l": (-160, 0, 0), "end_r": (160, 0, 0),
    "post_fl": (-180, 0, 0), "post_rl": (-180, 0, 0), "post_fr": (180, 0, 0), "post_rr": (180, 0, 0),
    "stile_": (0, 500, 0), "rail_": (0, 500, 0), "panel_": (0, 500, 0), "pull_": (0, 580, 0),
    "dside_": (0, 220, 0), "dfront_": (0, 220, 0), "dback_": (0, 220, 0), "dbot_": (0, 220, 0),
}

COLORS = {
    "hard maple": "#e2c48f", "soft maple": "#e2c48f", "3/4 maple ply": "#e9d9b0", "1/2 maple ply": "#ecdfbc",
    "1/2 paint-grade panel": "#d9cbb0", "1/2 Baltic birch": "#efe2bd",
}
HW_COLORS = {"slide": "#8c8f94", "pull": "#b8903f", "cushion": "#c9bda8"}
PAINTED = {"front_stile", "front_rail", "front_panel", "end", "back"}   # painted white; the ends are show faces
PAINT_WHITE = "#fbfbf8"
DONE = "#dedad2"      # already in place
STEM = {   # instance name (exact, or <stem>_...) -> registry part
    "post_fl": "post_front", "post_fr": "post_front", "post_rl": "post_rear", "post_rr": "post_rear",
    "end": "end", "bottom": "bottom", "partition": "partition", "cleat": "cleat", "back": "back", "top": "top",
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
    # one end: its two posts spread along Y so the stopped grooves face the viewer, the panel in place
    off = {"post_fl": (0, 120, 0), "post_rl": (0, -120, 0), "end_l": (0, 0, 0)}
    items = [(n, Pos(*o) * D[n] if any(o) else D[n]) for n, o in off.items()]
    c = D["end_l"].bounding_box().center()
    t = (c.X, c.Y, c.Z - 40)
    capture(items, [wood_color(n) for n in off], f"{OUT_DIR}/end-exploded.png",
            (t[0] - 1300, t[1] + 900, t[2] + 700), t, 1.4)     # from outside the low-X end, a little toward the room
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
