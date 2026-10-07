#!/usr/bin/env python
"""Assembly images for the shop page, captured from the OCP CAD viewer
(`scripts/cad-viewer.sh` must have the GPU Chrome tab open).

Writes images/assembly/exploded.png (the whole bench pulled apart), one
step-NN.png per assembly step (parts added in that step in wood colors,
everything already in place in pale grey) and three sub-assembly explosions
(a side frame, the back with its cleat and the bottom, a drawer box). STEPS
is also imported by make_cutlist_page.py, so the text and the pictures
cannot drift apart. The order is design.md's "Assembly order".

Usage: .venv/bin/python projects/Drawer-bench/assembly_shots.py
       ONLY=exploded|steps|subs to redo one group
"""
import os
import subprocess
import sys
import time

for _k in ("SHOW", "EXPORT", "TMP_STL"):
    os.environ.pop(_k, None)
VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Drawer-bench"
sys.path.insert(0, PROJ)
from drawer_bench import *  # noqa: E402,F403  runs the model's checks once
from drawer_bench import INST, PARTS  # noqa: E402

OUT_DIR = f"{PROJ}/images/assembly"
SETTLE = float(os.environ.get("SETTLE", "2.5"))

# (file stem, title, instance-name prefixes added in this step, shop text)
STEPS = [
    ("step-01", "Side frames",
     ("post_fl", "post_rl", "side_l"),
     "Glue each side panel into its front and rear posts: the 3/8 tongues above the notches go into the stopped "
     "grooves, glue on both faces of each tongue. Stand the posts and the panel on the bench with a 3/4 block "
     "under the panel's bottom edge; that puts the panel's top edge flush with the post tops. Check flush with a "
     "straightedge before clamping. Make both sides now: the left one stands up first, the right one closes the "
     "case in step 4."),
    ("step-02", "Back, cleat and bottom",
     ("back", "cleat_rear", "bottom"),
     "Off the bench, glue the cleat inside the back's top edge, flush with the top, figure-8 recesses up, and "
     "clamp it with the #8 x 1-1/4 screws from the cleat side. Push the bottom's rear edge into the back's "
     "groove with glue. Stand the left side frame and slide the pair in from the right, both at once: the back's "
     "tongue into the rear post's groove, the bottom's side edge into the side panel's groove."),
    ("step-03", "Front rails",
     ("rail_",),
     "Dowel the three rails into the left front post, two 3/8 dowels each, glue. The bottom's front edge sits in "
     "the bottom rail's rabbet, flush with the rail's top: glue it and screw down through the bottom into the "
     "rail. The top rail's figure-8 recesses face up and open toward the inside."),
    ("step-04", "Close the right side",
     ("post_fr", "post_rr", "side_r"),
     "Bring the right side frame in over the back's tongue, the bottom's edge and the three rails' dowels at "
     "once, all glued. Clamp across the case side to side at the posts, check the front frame square and the "
     "post tops level, and leave it until the glue cures."),
    ("step-05", "Slides and drawer boxes",
     ("drawer_",),
     "Glue each box up around its bottom: front and back in the sides' end rabbets, the 1/4 bottom in the "
     "grooves with its underside 1/2 above the sides' bottom edges, hook notches and bores at the rear. Screw "
     "the Blum runners to the posts' inner faces and the rear brackets to the back, clip the locking devices "
     "under the box fronts and set the boxes on the runners."),
    ("step-06", "Drawer fronts",
     ("front_",),
     "Screw the fronts to the box fronts from inside through oversize holes: 1/8 to the posts, 1/8 under the "
     "top, 1/4 between the two, the bottom one 3/4 off the floor. Pulls once chosen."),
    ("step-07", "Top",
     ("top",),
     "Set the top with 1-1/4 overhang all round and fix it with the six figure-8 fasteners on the top rail and "
     "the cleat, #8 x 5/8 screws. No glue; the fasteners let it move."),
]

# exploded offsets (mm) by instance prefix; the model's front is -Y, its left is -X
EXPLODE = {
    "top": (0, 0, 450),
    "post_fl": (-260, 0, 0), "post_rl": (-260, 0, 0), "side_l": (-260, 0, 0),
    "post_fr": (260, 0, 0), "post_rr": (260, 0, 0), "side_r": (260, 0, 0),
    "back": (0, 220, 0), "cleat_rear": (0, 220, 140), "bottom": (0, 0, -150),
    "rail_": (0, -200, 0), "front_": (0, -650, 0), "drawer_": (0, -330, 0),
}

COLORS = {
    "soft maple": "#d3ae6e",
    "3/4 ply": "#e8d7ad",
    "1/2 ply": "#e8d7ad",
    "1/4 ply": "#ecdfbc",
    "maple butcherblock (Boos match)": "#c79a62",
}
DONE = "#dedad2"      # already in place
MATERIAL = {p["name"]: p["material"] for p in PARTS}


def material(inst_name):
    """Placed-instance name to its registry part's material (post_fl -> post_front,
    side_l -> side, drawer_side_bot_r -> drawer_side_bot); same rule as hero_shot.py."""
    if inst_name.startswith("post_"):
        return MATERIAL["post_front" if inst_name[5] == "f" else "post_rear"]
    base = inst_name[:-2] if inst_name.endswith(("_l", "_r")) else inst_name
    return MATERIAL[base]


def wood_color(name):
    return COLORS[material(name)]


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


# Front-RIGHT view from above: the right side closes last, so the open right
# side shows the back, bottom, rails and boxes going in.
TARGET = (TOP_W / 2, TOP_D / 2, H / 2)
POS = (TARGET[0] + 1500, TARGET[1] - 2300, TARGET[2] + 1400)


def fit_radius(items):
    """The radius the viewer fits its camera to (three-cad-viewer: the bounding
    sphere of the shown parts, or the bbox center's distance from the origin if
    larger); the zoom is relative to it, so scaling by it keeps one scale across
    steps that show different amounts of the bench."""
    bb = None
    for _, s in items:
        b = s.bounding_box()
        bb = b if bb is None else bb.add(b)
    return max(bb.diagonal / 2, bb.center().length)


def step_images():
    placed = []
    r_full = fit_radius(INST)
    for stem, title, prefixes, text in STEPS:
        new = [(n, s) for n, s in INST if prefixed(n, prefixes)]
        assert new, f"step {stem} adds nothing: {prefixes}"
        items = placed + new
        colors = [DONE] * len(placed) + [wood_color(n) for n, _ in new]
        capture(items, colors, f"{OUT_DIR}/{stem}.png", POS, TARGET, 1.2 * fit_radius(items) / r_full)
        placed = items
    assert len(placed) == len(INST), "steps do not cover every placed part"


def exploded():
    items, colors = [], []
    for n, s in INST:
        off = next((v for k, v in EXPLODE.items() if prefixed(n, (k,))), (0, 0, 0))
        items.append((n, Pos(*off) * s if any(off) else s))
        colors.append(wood_color(n))
    t = (TARGET[0], TARGET[1] - 150, TARGET[2] + 60)
    capture(items, colors, f"{OUT_DIR}/exploded.png", (t[0] + 1700, t[1] - 2600, t[2] + 2000), t, 1.2)


def sub_assemblies():
    D = dict(INST)
    # left side frame: posts pulled off the panel's ends along Y, seen from inside (the +X side)
    off = {"post_fl": (0, -140, 0), "post_rl": (0, 140, 0), "side_l": (0, 0, 0)}
    items = [(n, Pos(*o) * D[n]) for n, o in off.items()]
    t = (X0 + SETBACK + T18, TOP_D / 2, POST_H / 2)
    capture(items, [wood_color(n) for n in off], f"{OUT_DIR}/side-exploded.png",
            (t[0] + 1500, t[1] - 900, t[2] + 500), t, 1.3)
    # back with its cleat and the bottom: cleat lifted, bottom pulled forward and down, seen from the front
    off = {"back": (0, 0, 0), "cleat_rear": (0, 0, 150), "bottom": (0, -160, -120)}
    items = [(n, Pos(*o) * D[n]) for n, o in off.items()]
    t = (TOP_W / 2, BACK_Y0 - 80, POST_H / 2 - 40)
    capture(items, [wood_color(n) for n in off], f"{OUT_DIR}/rear-exploded.png",
            (t[0] + 900, t[1] - 1500, t[2] + 700), t, 1.3)
    # bottom drawer box: sides out, front and back forward/back, bottom down
    off = {"drawer_side_bot_l": (-120, 0, 0), "drawer_side_bot_r": (120, 0, 0), "drawer_front_bot": (0, -140, 0),
           "drawer_back_bot": (0, 140, 0), "drawer_bottom_bot": (0, 0, -110)}
    items = [(n, Pos(*o) * D[n]) for n, o in off.items()]
    t = (TOP_W / 2, BOX_Y0 + BOX_D / 2, BOX_BOT_Z0 + BOX_BOT_H / 2 - 40)
    capture(items, [wood_color(n) for n in off], f"{OUT_DIR}/drawer-exploded.png",
            (t[0] + 900, t[1] - 1300, t[2] + 800), t, 1.5)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    only = os.environ.get("ONLY")
    if only in (None, "exploded"):
        exploded()
    if only in (None, "steps"):
        step_images()
    if only in (None, "subs"):
        sub_assemblies()
    print("assembly images done")
