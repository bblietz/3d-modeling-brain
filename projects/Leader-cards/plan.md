---
title: Leader cards implementation plan
type: project-plan
created: 2026-09-12
tags: [fishing, tackle, petg, leader, x2d, plan]
---

# Leader Cards Implementation Plan

> **Superseded 2026-09-12.** Written before the rounded slot edges, 0.3 mm pocket tip, exit ramps, corner lugs and Brian's pick of variant 5 reversed. Brian chose to print the card directly with no coupon. The current source is `leader_card.py` (verified copy in `prototype/`); the decisions are in [[brief]]. Kept for history only; do not execute.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Modeling work also follows the `/3d-model` skill (build123d backend, per-feature render, printability check, STL plus 3MF export).

**Goal:** Build and print a slot test coupon, then one 3 x 2 in (76.2 x 50.8 mm), 3 mm thick white PETG leader card with wavy wrap edges and hook-bend line slots, per [[brief]].

**Architecture:** One parametric build123d source, `leader_card.py`, builds either part (`PART=coupon` or `PART=card`) from shared geometry: a rounded outline whose short edges are a wave of tangent arcs, a top round and bottom chamfer, and hook-bend slot tools cut through the thickness. Inline asserts verify every feature. A second script, `make_plate.py`, turns the exported STL into a Bambu Studio print 3MF (0.4 nozzle, PETG Basic, Textured PEI) and proves it by a real slice. Every piece of code below was run end to end in the scratchpad on 2026-09-12 and produced the outputs quoted.

**Tech Stack:** Python 3.12.13 in the vault `.venv`, build123d 0.11.1, trimesh 4.12.2, Bambu Studio CLI (`bambu-studio`), `scripts/render_stl.py`, `projects/Sharks-nametag/pipeline/graft_slice.py`.

## Global Constraints

- Nozzle: 0.4 mm. Confirm the installed nozzle AND the Bambu Studio machine profile both read 0.4 before any print ([[printer-x2d]]).
- Material: Bambu PETG Basic, white. Plate: Textured PEI. Chamber fan on cool.
- Presets: `Bambu Lab X2D 0.4 nozzle`, `0.20mm Standard @BBL X2D`, `Bambu PETG Basic @BBL X2D 0.4 nozzle`.
- Print flat, chamfered edge on the bed, no supports.
- All files live in `projects/Leader-cards/`. Notes are Obsidian markdown with YAML frontmatter and wikilinks. No em dashes in any note.
- Run every command from the vault root `/home/brian/ClaudeProjects/3d-modeling-brain`.
- Commit only paths you created or changed with `git commit -- <paths>`; the working tree carries an unrelated modified `projects/Build123d-trial/project-box.3mf` that must not be swept in. Push to origin main after each milestone commit. Never commit the printer access code.
- Never tell Brian a part was sent to the printer. Hand over file paths and orientation; he prints.
- Two stops for Brian: after the coupon (he tests and picks a variant) and after the card (he checks fit and wraps a real rig). Do not start the next task before his answer.

## File Structure

| File | Responsibility |
|---|---|
| `projects/Leader-cards/leader_card.py` | Geometry, feature checks, STL and plain 3MF export for both parts |
| `projects/Leader-cards/make_plate.py` | Print 3MF with presets and plate patched, verified by a real slice |
| `projects/Leader-cards/leader-card-coupon.stl`, `.3mf`, `-print.3mf` | Coupon outputs |
| `projects/Leader-cards/leader-card.stl`, `.3mf`, `-print.3mf` | Card outputs |
| `projects/Leader-cards/images/final-*.png` | Final renders |
| `projects/Leader-cards/brief.md` | Status and recorded outcomes (modify) |
| `knowledge/learnings/leader-cards.md` | Retrospective (Task 4) |
| `memory/project-leader-cards.md`, `memory/MEMORY.md` | Project memory (Task 4) |

---

### Task 1: Coupon geometry source with feature checks

**Files:**
- Create: `projects/Leader-cards/leader_card.py`
- Create: `projects/Leader-cards/leader-card-coupon.stl`, `projects/Leader-cards/leader-card-coupon.3mf` (generated)
- Create: `projects/Leader-cards/images/final-coupon.png`, `projects/Leader-cards/images/final-coupon-slot.png` (generated)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `build(which: str, stage: int = 2) -> Part`, `check(part, which: str) -> dict`, `export(part, which: str) -> (stl_path, threemf_path)`, constants `VARIANTS` (list of 4 dicts), `WINNER` (None until Task 3), `NAMES = {"coupon": "leader-card-coupon", "card": "leader-card"}`. Env interface: `PART`, `STAGE`, `SHOW`.

- [ ] **Step 1: Confirm the interpreter**

Run: `.venv/bin/python -c "import build123d, trimesh, sys; print(sys.version.split()[0], 'build123d', build123d.__version__, 'trimesh', trimesh.__version__)"`
Expected: `3.12.13 build123d 0.11.1 trimesh 4.12.2`

- [ ] **Step 2: Create the source file**

Create `projects/Leader-cards/leader_card.py` with exactly this content:

```python
"""Leader cards: flat PETG card for wrapping fishing leaders, plus the slot test coupon.

Spec: projects/Leader-cards/brief.md. Both parts print flat, chamfered edge on
the bed, 0.4 mm nozzle, PETG. The line wraps around the long (X) axis over the
two wavy short edges and locks in a hook-bend slot at each end.

Run:  PART=coupon .venv/bin/python projects/Leader-cards/leader_card.py
      PART=card   .venv/bin/python projects/Leader-cards/leader_card.py
Env:  STAGE=1 builds only the blank with its wavy edges, STAGE=2 adds the slots;
      a STAGE run exports a scratch STL (argv[1]) for the per-feature render.
      SHOW=1|reset pushes to the OCP viewer.
"""
import math
import os
import sys
import zipfile

from build123d import Axis, Circle, Edge, Face, Mesher, Polygon, Pos, Rot, Vector, Wire, chamfer, export_stl, extrude, fillet

PROJECT = os.path.dirname(os.path.abspath(__file__))

# card
CARD_L = 76.2  # 3 in, along X; the line wraps over the short edges at x = +/- CARD_L / 2
CARD_W = 50.8  # 2 in
THICK = 3.0
CORNER_R = 2.9  # plan-view corner radius; leaves a 45.0 mm straight short edge, exactly 15 wave pitches
TOP_ROUND = 0.6  # capped by the 1.09 mm wave peaks
BOT_CHAMFER = 0.6  # 45 degrees, no feather lip at the bed

# wrap edge wave: alternating tangent arcs, rounded peaks and valleys
WAVE_PITCH = 3.0
WAVE_DEPTH = 0.6
WAVE_R = ((WAVE_PITCH / 2) ** 2 + WAVE_DEPTH ** 2) / (4 * WAVE_DEPTH)  # 1.0875

# hook-bend slot, local frame: mouth on the long edge at the origin, lead-in runs +Y,
# pocket turns toward +X (the nearest short edge) and angles back toward the mouth
SLOT_INSET = 8.0  # lead-in centreline to the nearest short edge (card)
LEAD_DEPTH = 6.0
MOUTH_W = 2.4
FUNNEL = 1.0
MIN_WALL = 2.0  # pocket to long edge
POCKET_PROBE = 1.5  # distance along the pocket where the open-slot probe sits

# coupon
COUPON_L = 52.0
COUPON_W = 11.8  # 6.0 mm straight short edge, exactly 2 wave pitches
COUPON_FIRST = 6.0  # first lead-in from the coupon's -X end
COUPON_PITCH = 12.0

VARIANTS = [  # variant 1 is nearest the coupon's -X end
    dict(lead_w=1.2, angle=30, pocket_w=1.0, pocket_l=4.5),  # 1 brief baseline
    dict(lead_w=1.2, angle=30, pocket_w=0.8, pocket_l=4.5),  # 2 tighter pocket
    dict(lead_w=1.2, angle=50, pocket_w=1.0, pocket_l=4.5),  # 3 steeper hook
    dict(lead_w=1.6, angle=30, pocket_w=1.0, pocket_l=4.5),  # 4 wider lead-in
]
WINNER = None  # 1-4 from Brian's coupon test; PART=card refuses to build until set

NAMES = {"coupon": "leader-card-coupon", "card": "leader-card"}


def outline(length, width):
    """Rounded rectangle whose two short edges are a wave of tangent arcs."""
    xe, ye, cr, d, r = length / 2, width / 2, CORNER_R, WAVE_DEPTH, WAVE_R
    q = WAVE_PITCH / 4
    straight = width - 2 * cr
    n = round(straight / (2 * q)) - 1  # full arcs between the two half peaks
    assert abs((n + 1) * 2 * q - straight) < 1e-6 and n % 2 == 1, (straight, n)
    y0, y1 = -ye + cr, ye - cr
    phi = math.atan2(q, r - d / 2)  # sweep of the half peak at each end
    tan = lambda y: Vector(xe - d / 2, y)  # tangent points sit halfway down the wave
    k = math.sqrt(0.5)

    right = [Edge.make_three_point_arc(Vector(xe - cr, -ye), Vector(xe - cr + cr * k, y0 - cr * k), Vector(xe, y0))]
    right.append(Edge.make_three_point_arc(Vector(xe, y0), Vector(xe - r + r * math.cos(phi / 2), y0 + r * math.sin(phi / 2)), tan(y0 + q)))
    y = y0 + q
    for i in range(n):  # valley first, alternating, valley last
        right.append(Edge.make_three_point_arc(tan(y), Vector(xe - d if i % 2 == 0 else xe, y + q), tan(y + 2 * q)))
        y += 2 * q
    right.append(Edge.make_three_point_arc(tan(y), Vector(xe - r + r * math.cos(phi / 2), y1 - r * math.sin(phi / 2)), Vector(xe, y1)))
    right.append(Edge.make_three_point_arc(Vector(xe, y1), Vector(xe - cr + cr * k, y1 + cr * k), Vector(xe - cr, ye)))

    edges = [Edge.make_line(Vector(-xe + cr, -ye), Vector(xe - cr, -ye))]
    edges += right
    edges.append(Edge.make_line(Vector(xe - cr, ye), Vector(-xe + cr, ye)))
    edges += [Rot(0, 0, 180) * e for e in right]
    return Face(Wire(edges))


def blank(length, width):
    part = extrude(outline(length, width), amount=THICK)
    part = fillet(part.edges().group_by(Axis.Z)[-1], TOP_ROUND)
    return chamfer(part.edges().group_by(Axis.Z)[0], BOT_CHAMFER)


def pocket_points(v):
    """Pocket triangle, counterclockwise: base corner, tip, base corner.
    Clockwise winding flips the face normal and the extrude misses the part."""
    a = math.radians(v["angle"])
    u = (math.cos(a), -math.sin(a))
    n = (-u[1], u[0])
    pw = v["pocket_w"] / 2
    return (
        (-n[0] * pw, LEAD_DEPTH - n[1] * pw),
        (u[0] * v["pocket_l"], LEAD_DEPTH + u[1] * v["pocket_l"]),
        (n[0] * pw, LEAD_DEPTH + n[1] * pw),
    )


def slot_profile(v):
    hw, m = v["lead_w"] / 2, MOUTH_W / 2
    lead = Polygon((-m, -1), (m, -1), (m, 0), (hw, FUNNEL), (hw, LEAD_DEPTH),
                   (-hw, LEAD_DEPTH), (-hw, FUNNEL), (-m, 0), align=None)
    return lead + Pos(0, LEAD_DEPTH) * Circle(hw) + Polygon(*pocket_points(v), align=None)


def slot_places(which):
    """(mouth x, sign, variant): sign -1 is the slot turned 180 degrees onto the +Y edge."""
    if which == "coupon":
        return [(-COUPON_L / 2 + COUPON_FIRST + i * COUPON_PITCH, 1, v) for i, v in enumerate(VARIANTS)]
    assert WINNER in (1, 2, 3, 4), "set WINNER from the coupon test before building the card"
    v = VARIANTS[WINNER - 1]
    return [(CARD_L / 2 - SLOT_INSET, 1, v), (-(CARD_L / 2 - SLOT_INSET), -1, v)]


def size(which):
    return (COUPON_L, COUPON_W) if which == "coupon" else (CARD_L, CARD_W)


def build(which, stage=2):
    length, width = size(which)
    part = blank(length, width)
    if stage < 2:
        return part
    for x0, s, v in slot_places(which):
        tool = Pos(0, 0, -1) * extrude(slot_profile(v), amount=THICK + 2)
        part -= Pos(x0, -s * width / 2, 0) * Rot(0, 0, 0 if s > 0 else 180) * tool
    return part


def check(part, which):
    length, width = size(which)
    assert len(part.solids()) == 1, "expected one solid"
    bb = part.bounding_box()
    assert abs(bb.size.X - length) < 0.01 and abs(bb.size.Y - width) < 0.01 and abs(bb.size.Z - THICK) < 0.01, bb.size
    assert abs(bb.min.Z) < 1e-6, "part must sit on the bed"

    world = lambda x0, s, lx, ly: Vector(x0 + s * lx, s * (-width / 2 + ly), THICK / 2)
    for x0, s, v in slot_places(which):
        pts = pocket_points(v)
        assert v["pocket_w"] <= v["lead_w"], v
        assert min(p[1] for p in pts) >= MIN_WALL, ("pocket wall", v)
        assert abs(x0 + s * pts[1][0]) <= length / 2 - WAVE_DEPTH - 2.0, ("pocket tip too near the short edge", v)
        a = math.radians(v["angle"])
        assert not part.is_inside(world(x0, s, 0, LEAD_DEPTH / 2)), ("lead-in closed", v)
        assert not part.is_inside(world(x0, s, POCKET_PROBE * math.cos(a), LEAD_DEPTH - POCKET_PROBE * math.sin(a))), ("pocket closed", v)
        assert part.is_inside(world(x0, s, 2.0, 1.5)), ("no tongue between pocket and mouth", v)
    if which == "coupon":
        gaps = [b[0] - a[0] for a, b in zip(slot_places(which), slot_places(which)[1:])]
        assert all(g - MOUTH_W / 2 - pocket_points(v)[1][0] >= 2.0 for g, v in zip(gaps, VARIANTS)), "slots too close"

    valleys = round((width - 2 * CORNER_R) / WAVE_PITCH)
    yb = -width / 2 + CORNER_R
    for s in (1, -1):
        assert all(not part.is_inside(Vector(s * (length / 2 - WAVE_DEPTH / 2), s * (yb + WAVE_PITCH * (i + 0.5)), THICK / 2))
                   for i in range(valleys)), "wave valley filled"
        assert all(part.is_inside(Vector(s * (length / 2 - WAVE_DEPTH / 2), s * (yb + WAVE_PITCH * i), THICK / 2))
                   for i in range(valleys + 1)), "wave peak missing"

    # volume sanity: the slots remove their in-part profile area times the thickness,
    # a little less where they cross the edge round and chamfer
    removed = blank(length, width).volume - part.volume
    expected = sum((slot_profile(v).area - MOUTH_W) * THICK for _, _, v in slot_places(which))
    assert 0.95 * expected < removed < expected, (removed, expected)
    return {"size": (bb.size.X, bb.size.Y, bb.size.Z), "volume_mm3": round(part.volume, 1),
            "valleys_per_edge": valleys, "slots": len(slot_places(which))}


def export(part, which):
    import trimesh

    length, width = size(which)
    stl = f"{PROJECT}/{NAMES[which]}.stl"
    threemf = f"{PROJECT}/{NAMES[which]}.3mf"
    export_stl(part, stl)
    m = Mesher()
    m.add_shape(part)
    m.write(threemf)

    mesh = trimesh.load_mesh(stl)
    assert mesh.is_watertight, "STL not watertight"
    ext = mesh.bounds[1] - mesh.bounds[0]
    assert abs(ext[0] - length) < 0.01 and abs(ext[1] - width) < 0.01 and abs(ext[2] - THICK) < 0.01, ext
    with zipfile.ZipFile(threemf) as z:
        model = z.read("3D/3dmodel.model").decode()
    assert model.count("<item ") == 1, "3MF should hold one build item"
    return stl, threemf


if __name__ == "__main__":
    which = os.environ.get("PART")
    assert which in NAMES, "set PART=coupon or PART=card"
    stage = int(os.environ.get("STAGE", "2"))
    part = build(which, stage)
    if "STAGE" in os.environ:
        out = sys.argv[1] if len(sys.argv) > 1 else f"/tmp/{NAMES[which]}-stage{stage}.stl"
        export_stl(part, out)
        print("stage", stage, "->", out, "bbox", part.bounding_box().size)
    else:
        report = check(part, which)
        stl, threemf = export(part, which)
        print("checks passed", report)
        print("exported", stl, threemf)

    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show

        show(part, names=[NAMES[which]], reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
```

- [ ] **Step 3: Prove the checks catch a missing slot (red)**

Run the checks against the stage 1 blank, which has no slots yet:

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0, 'projects/Leader-cards')
import leader_card as lc
lc.check(lc.build('coupon', 1), 'coupon')" 2>&1 | tail -1
```

Expected: `AssertionError: ('lead-in closed', {'lead_w': 1.2, 'angle': 30, 'pocket_w': 1.0, 'pocket_l': 4.5})`

- [ ] **Step 4: Feature 1 render, blank with wavy edges**

Run, with `$S` set to the session scratchpad directory:

```bash
PART=coupon STAGE=1 .venv/bin/python projects/Leader-cards/leader_card.py $S/coupon-stage1.stl
.venv/bin/python scripts/render_stl.py $S/coupon-stage1.stl $S/coupon-stage1.png 90,-90 35,-60
```

Expected: `stage 1 -> ... bbox Vector: (X=52, Y=11.8, Z=3)` and `rendered 2 views`. Open the PNG: a rounded strip, both short ends showing two small rounded valleys, no slots.

- [ ] **Step 5: Feature 2 render, slots**

```bash
PART=coupon STAGE=2 .venv/bin/python projects/Leader-cards/leader_card.py $S/coupon-stage2.stl
.venv/bin/python scripts/render_stl.py $S/coupon-stage2.stl $S/coupon-stage2.png 90,-90 35,-60
```

Expected: `stage 2 -> ... bbox Vector: (X=52, Y=11.8, Z=3)`. Open the PNG: four slots entering the -Y long edge, each turning toward +X into a pocket that angles back toward the edge; slot 3 has the steepest hook, slot 4 the widest lead-in.

- [ ] **Step 6: Full build, checks and export (green)**

Run: `PART=coupon .venv/bin/python projects/Leader-cards/leader_card.py`
Expected:
```
checks passed {'size': (52.0000002, 11.800000000000004, 3.0000000000000018), 'volume_mm3': 1653.4, 'valleys_per_edge': 2, 'slots': 4}
exported .../projects/Leader-cards/leader-card-coupon.stl .../projects/Leader-cards/leader-card-coupon.3mf
```

- [ ] **Step 7: Printability check**

Confirm against the `/3d-model` printability table with the 0.4 nozzle: thinnest solid is the pocket wall, at least 2.0 mm (asserted, above the 0.84 mm minimum); slot walls are vertical through cuts, so no overhangs; the 45 degree bottom chamfer is the only sloped underside and is exactly at the limit; first layer is the flat bottom face (asserted `bb.min.Z == 0`). Record "printability: pass" for the brief in Task 2.

- [ ] **Step 8: Final renders**

```bash
.venv/bin/python scripts/render_stl.py projects/Leader-cards/leader-card-coupon.stl projects/Leader-cards/images/final-coupon.png
.venv/bin/python -c "
import sys; sys.path.insert(0, 'projects/Leader-cards')
from leader_card import *
from build123d import Align, Box
p = build('coupon')
crop = p & (Pos(-COUPON_L / 2, -COUPON_W / 2 - 1, -1) * Box(16, COUPON_W + 2, THICK + 2, align=(Align.MIN, Align.MIN, Align.MIN)))
export_stl(crop, '$S/coupon-slot.stl')"
.venv/bin/python scripts/render_stl.py $S/coupon-slot.stl projects/Leader-cards/images/final-coupon-slot.png 90,-90 40,-35
```

Expected: `rendered 4 views` then `rendered 2 views`. Open `final-coupon-slot.png`: the wavy -X end and slot 1 with its funnel, lead-in, hook pocket, and solid tongue are clearly visible.

- [ ] **Step 9: Commit**

```bash
git add projects/Leader-cards/leader_card.py projects/Leader-cards/leader-card-coupon.stl projects/Leader-cards/leader-card-coupon.3mf projects/Leader-cards/images/final-coupon.png projects/Leader-cards/images/final-coupon-slot.png
git commit -m "Leader cards task 1: coupon geometry with feature checks, STL and 3MF" -- projects/Leader-cards
```

---

### Task 2: Coupon print file, real slice, and handoff (STOP for Brian)

**Files:**
- Create: `projects/Leader-cards/make_plate.py`
- Create: `projects/Leader-cards/leader-card-coupon-print.3mf` (generated)
- Modify: `projects/Leader-cards/brief.md` (frontmatter `status`, new `## Outcomes` section at the end)

**Interfaces:**
- Consumes: `projects/Leader-cards/leader-card-coupon.stl` from Task 1; `graft_slice(src, dst, plate=1) -> dict(rc, layers, time, seconds, gcode)` from `projects/Sharks-nametag/pipeline/graft_slice.py`.
- Produces: `make_plate.py coupon|card` CLI writing `<name>-print.3mf` and printing `{'minutes': int, 'grams': float}`. Task 3 reuses it with `card`.

- [ ] **Step 1: Create the plate script**

Create `projects/Leader-cards/make_plate.py` with exactly this content:

```python
"""Bambu Studio print 3MF for one leader-card part, verified by a real slice.

Adapted from projects/Garmin-943-helm-panel/make_plate.py; see its docstring for
why: the CLI writes "Cool Plate" and leaves the part off the plate, and any key
changed in a project 3MF must be listed in different_settings_to_system or
Studio's GUI resets it on open.
X2D 0.4 nozzle, 0.20mm Standard, Bambu PETG Basic, Textured PEI Plate.

Usage:  .venv/bin/python projects/Leader-cards/make_plate.py coupon|card
Writes: projects/Leader-cards/<name>-print.3mf and prints real minutes and grams.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Sharks-nametag", "pipeline"))
from graft_slice import graft_slice  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")

MACHINE = "Bambu Lab X2D 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL X2D"
FILAMENT = "Bambu PETG Basic @BBL X2D 0.4 nozzle"

BED_CENTRE = (128.0, 128.0)
OVERRIDES = {"curr_bed_type": "Textured PEI Plate"}
NAMES = {"coupon": "leader-card-coupon", "card": "leader-card"}


def load(kind, name):
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
    """Resolve the inherits chain; the CLI cannot do this for X2D presets."""
    chain = [load(kind, name)]
    while "inherits" in chain[-1]:
        chain.append(load(kind, chain[-1]["inherits"]))
    merged = {}
    for layer in reversed(chain):
        merged.update(layer)
    merged.pop("inherits", None)
    merged["name"] = name
    return merged


def write_presets(d):
    for kind, name, fn in (
        ("machine", MACHINE, "machine.json"),
        ("process", PROCESS, "process.json"),
        ("filament", FILAMENT, "filament.json"),
    ):
        with open(f"{d}/{fn}", "w") as f:
            json.dump(flatten(kind, name), f)


def patch(src, dst, label):
    """Centre the single build item on the plate and apply the overrides."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                s = data.decode()
                assert s.count("<item ") == 1, "expected one build item"
                s = re.sub(r'(<item [^>]*?)transform="[^"]*"',
                           r'\1transform="1 0 0 0 1 0 0 0 1 %g %g 0"' % BED_CENTRE, s, count=1)
                data = s.encode()
            elif item.filename == "Metadata/project_settings.config":
                cfg = json.loads(data)
                cfg.update(OVERRIDES)
                diff = cfg.get("different_settings_to_system") or [""]
                existing = [x for x in diff[0].split(";") if x]
                diff[0] = ";".join(sorted(set(existing) | set(OVERRIDES)))
                cfg["different_settings_to_system"] = diff
                data = json.dumps(cfg, indent=4).encode()
            elif item.filename == "Metadata/model_settings.config":
                # the CLI names the object after the input file; keep it readable
                data = re.sub(r'value="[^"]*\.stl"', f'value="{label}"', data.decode()).encode()
            zout.writestr(item, data)
    zin.close()


def verify(path, tmp):
    """Slice it for real; a CLI round trip alone does not prove sliceability."""
    cfg = json.loads(zipfile.ZipFile(path).read("Metadata/project_settings.config"))
    for k, v in OVERRIDES.items():
        assert cfg[k] == v, f"{k} did not stick: {cfg[k]}"
    assert set(OVERRIDES) <= set(cfg["different_settings_to_system"][0].split(";"))
    assert cfg["printer_settings_id"] == MACHINE, cfg["printer_settings_id"]
    assert cfg["filament_settings_id"] == [FILAMENT], cfg["filament_settings_id"]

    # The CLI cannot slice its own project files (rc 156); graft_slice adds the
    # GUI-only keys to a throwaway copy, so the shipped file stays unpatched.
    out = f"{tmp}/sliced.3mf"
    res = graft_slice(path, out)
    assert res.get("rc") == 0 and os.path.exists(out), f"slice failed rc={res.get('rc')}"
    info = zipfile.ZipFile(out).read("Metadata/slice_info.config").decode()
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
    return {"minutes": round(int(grab("prediction")) / 60), "grams": round(float(grab("weight")), 1)}


def main(which):
    name = NAMES[which]
    with tempfile.TemporaryDirectory() as tmp:
        write_presets(tmp)
        shutil.copy(f"{HERE}/{name}.stl", f"{tmp}/{name}.stl")
        # --export-3mf must be a bare filename; an absolute path alongside
        # --outputdir makes the CLI exit 243 without writing anything.
        r = subprocess.run(
            ["bambu-studio", "--arrange", "1",
             "--load-settings", "machine.json;process.json",
             "--load-filaments", "filament.json",
             "--export-3mf", "raw.3mf", "--outputdir", ".", f"{name}.stl"],
            cwd=tmp, capture_output=True, text=True, timeout=600)
        assert os.path.exists(f"{tmp}/raw.3mf"), f"CLI export failed rc={r.returncode}"
        final = f"{HERE}/{name}-print.3mf"
        patch(f"{tmp}/raw.3mf", final, name)
        result = verify(final, tmp)
    print(final, result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

- [ ] **Step 2: Build and slice the coupon print file**

Run: `.venv/bin/python projects/Leader-cards/make_plate.py coupon`
Expected: `.../projects/Leader-cards/leader-card-coupon-print.3mf {'minutes': 5, 'grams': 1.6}`
If it fails, the assertion message names the stage (CLI export, override, preset id, or slice rc). Fix the cause; do not bypass the slice.

- [ ] **Step 3: Check which nozzle is mounted**

Run: `.venv/bin/python scripts/x2d-status.py`
Expected: output that names the mounted nozzle. If it is not 0.4 mm, tell Brian the 0.4 must be installed before printing; do not change the design.

- [ ] **Step 4: Record the outcome in the brief**

In `projects/Leader-cards/brief.md` set the frontmatter `status:` line to:

```
status: coupon built and sliced 2026-09-12 (5 min, 1.6 g). Waiting on Brian's real-line test to pick a slot variant
```

and append at the end of the file (use the real minutes and grams from Step 2 if they differ):

```markdown
## Outcomes

### Coupon (2026-09-12)

- Files: `leader-card-coupon.stl`, `leader-card-coupon.3mf`, `leader-card-coupon-print.3mf` (open this one in Bambu Studio), renders `images/final-coupon.png` and `images/final-coupon-slot.png`.
- Real slice: 5 min, 1.6 g, 0.20mm Standard, Bambu PETG Basic, 0.4 nozzle, Textured PEI.
- Printability: pass. Thinnest wall 2.0 mm pocket wall, no overhangs past the 45 degree bottom chamfer.
- How to read it: hold the coupon with the slot mouths toward you and the hooks pointing right. Variant 1 is leftmost. 1 baseline (1.2 mm lead-in, 30 degree hook, 1.0 mm pocket), 2 tighter pocket (0.8 mm), 3 steeper hook (50 degrees), 4 wider lead-in (1.6 mm).
```

- [ ] **Step 5: Commit and push**

```bash
git add projects/Leader-cards/make_plate.py projects/Leader-cards/leader-card-coupon-print.3mf projects/Leader-cards/brief.md
git commit -m "Leader cards task 2: coupon print 3MF verified by real slice" -- projects/Leader-cards
git push origin main
```

- [ ] **Step 6: Hand off to Brian and STOP**

Tell Brian, in plain words: the file to open (`projects/Leader-cards/leader-card-coupon-print.3mf`), orientation (flat, as loaded), the sliced time and grams, that the 0.4 nozzle must be installed and selected, how to read the variants (mouths toward you, hooks right, variant 1 leftmost), and the six pass criteria from the brief's Test coupon section. Ask him which variant wins, and whether the 3 mm wave held a slack wrap. Do not start Task 3 until he answers. Do not say the part was sent to the printer.

---

### Task 3: The card with the winning slot (STOP for Brian)

Precondition: Brian has named a winning variant (1 to 4) and confirmed the wave holds. If no variant held 25 lb line, or the wave did not hold a slack wrap, stop and reopen the design with Brian (TPU slot inserts, or the 5 mm wave) instead of doing this task.

**Files:**
- Modify: `projects/Leader-cards/leader_card.py` (the `WINNER = None` line only)
- Create: `projects/Leader-cards/leader-card.stl`, `leader-card.3mf`, `leader-card-print.3mf`, `images/final-card.png`, `images/final-card-corner.png` (generated)
- Modify: `projects/Leader-cards/brief.md` (status, Outcomes)

**Interfaces:**
- Consumes: `build`, `check`, `export`, `WINNER` from Task 1; `make_plate.py card` from Task 2.
- Produces: the card deliverables.

- [ ] **Step 1: Prove the card refuses to build without a winner (red)**

Run: `PART=card .venv/bin/python projects/Leader-cards/leader_card.py 2>&1 | tail -1`
Expected: `AssertionError: set WINNER from the coupon test before building the card`

- [ ] **Step 2: Set the winner**

In `projects/Leader-cards/leader_card.py` replace the line

```python
WINNER = None  # 1-4 from Brian's coupon test; PART=card refuses to build until set
```

with (N is Brian's pick, and the date is the test date)

```python
WINNER = N  # Brian's coupon test, <YYYY-MM-DD>
```

- [ ] **Step 3: Feature renders**

```bash
PART=card STAGE=1 .venv/bin/python projects/Leader-cards/leader_card.py $S/card-stage1.stl
.venv/bin/python scripts/render_stl.py $S/card-stage1.stl $S/card-stage1.png 90,-90 35,-60
PART=card STAGE=2 .venv/bin/python projects/Leader-cards/leader_card.py $S/card-stage2.stl
.venv/bin/python scripts/render_stl.py $S/card-stage2.stl $S/card-stage2.png 90,-90 35,-60
```

Expected: both print `bbox Vector: (X=76.2, Y=50.8, Z=3)`. Open each PNG: stage 1 is the plain card with wavy short edges; stage 2 adds one slot on the -Y edge near +X and one on the +Y edge near -X, each hooking toward its nearest short edge.

- [ ] **Step 4: Full build, checks and export (green)**

Run: `PART=card .venv/bin/python projects/Leader-cards/leader_card.py`
Expected (verified with `WINNER = 1`; the volume changes slightly for other winners, everything else is identical):
```
checks passed {'size': (76.2000002, 50.8000001, 3.0000000000000004), 'volume_mm3': 11385.3, 'valleys_per_edge': 15, 'slots': 2}
exported .../projects/Leader-cards/leader-card.stl .../projects/Leader-cards/leader-card.3mf
```

- [ ] **Step 5: Final renders**

```bash
.venv/bin/python scripts/render_stl.py projects/Leader-cards/leader-card.stl projects/Leader-cards/images/final-card.png
.venv/bin/python -c "
import sys; sys.path.insert(0, 'projects/Leader-cards')
from leader_card import *
from build123d import Align, Box
p = build('card')
crop = p & (Pos(CARD_L / 2 - 11, -CARD_W / 2 - 1, -1) * Box(12, 16, THICK + 2, align=(Align.MIN, Align.MIN, Align.MIN)))
export_stl(crop, '$S/card-corner.stl')"
.venv/bin/python scripts/render_stl.py $S/card-corner.stl projects/Leader-cards/images/final-card-corner.png 90,-90 40,-35
```

Expected: `rendered 4 views` then `rendered 2 views`. Open `final-card-corner.png`: rounded wave along the +X edge, the slot with funnel, lead-in, hook pocket, and tongue.

- [ ] **Step 6: Print file and real slice**

Run: `.venv/bin/python projects/Leader-cards/make_plate.py card`
Expected (verified with `WINNER = 1`): `.../projects/Leader-cards/leader-card-print.3mf {'minutes': 14, 'grams': 9.0}`

- [ ] **Step 7: Record the outcome in the brief**

Set the frontmatter `status:` line to:

```
status: card built and sliced (14 min, 9.0 g) with slot variant N. Waiting on Brian's tackle box fit and 36 in wrap test
```

and append under `## Outcomes` (real numbers from Steps 4 and 6):

```markdown
### Card

- Winning slot: variant N, chosen by Brian on <YYYY-MM-DD>. His coupon notes: <his words on each variant and on the wave>.
- Files: `leader-card.stl`, `leader-card.3mf`, `leader-card-print.3mf` (open this one), renders `images/final-card.png` and `images/final-card-corner.png`.
- Real slice: 14 min, 9.0 g, same settings as the coupon.
```

- [ ] **Step 8: Commit and push**

```bash
git add projects/Leader-cards/leader_card.py projects/Leader-cards/leader-card.stl projects/Leader-cards/leader-card.3mf projects/Leader-cards/leader-card-print.3mf projects/Leader-cards/images/final-card.png projects/Leader-cards/images/final-card-corner.png projects/Leader-cards/brief.md
git commit -m "Leader cards task 3: card with slot variant N, print 3MF verified by real slice" -- projects/Leader-cards
git push origin main
```

- [ ] **Step 9: Hand off to Brian and STOP**

Tell Brian the file to open (`projects/Leader-cards/leader-card-print.3mf`), orientation (flat, as loaded), sliced time and grams, and the 0.4 nozzle requirement. Ask him to check that it fits the tackle box and to wrap a real 36 in rig: start slot just past the swivel, wraps in the valleys, finish slot near the lure. Do not start Task 4 until he reports. If the fit or wrap fails, reopen the design with him instead.

---

### Task 4: Retrospective and memory

Precondition: Brian has reported the card fit and wrap result.

**Files:**
- Create: `knowledge/learnings/leader-cards.md`
- Create: `memory/project-leader-cards.md`
- Modify: `memory/MEMORY.md` (one line appended)
- Modify: `projects/Leader-cards/brief.md` (status)

**Interfaces:**
- Consumes: the brief's Locked decisions and Outcomes; Brian's reports from the two stops.
- Produces: durable notes only.

- [ ] **Step 1: Write the retrospective**

Create `knowledge/learnings/leader-cards.md`. The structure and the facts already known are below; the lines marked "from Brian" must quote or summarise what he actually reported at the two stops, never an assumption.

```markdown
---
title: Leader cards retrospective
type: learning
created: <YYYY-MM-DD>
tags: [fishing, tackle, petg, x2d, slots, retrospective]
---

# Leader cards retrospective

Project: [[brief]] in `projects/Leader-cards/`. Printed PETG card that replaces cardboard for wrapping 36 in fishing leaders.

## Decisions locked

- One universal card, holds line only; hooks and lures hang free.
- Hook-bend slots (lead-in, then a pocket that turns toward the nearest short edge and angles back toward the mouth) instead of a bump detent: no flexing of stiff 3 mm PETG, so print tolerance matters little.
- 3 mm wave on the wrap edges, 0.6 mm deep, arc radius 1.0875 mm; top round and bottom chamfer capped at 0.6 mm by the wave peaks.
- White PETG Basic, 0.4 nozzle, 0.20mm Standard, Textured PEI.
- Winning slot variant: N (from Brian).

## What worked

- Prototyping the plan's code in the scratchpad before writing the plan caught a clockwise pocket polygon whose extrude went below the part and cut nothing. Point-in-solid probes (`is_inside`) at the lead-in, pocket, tongue, valleys and peaks now guard every feature.
- <from Brian: what held on the coupon and the card>

## What failed

- <from Brian: variants that slipped, crimped, or wore; anything about the wave or fit>

## Measured and sliced

- Coupon 52 x 11.8 x 3 mm: 5 min, 1.6 g. Card 3 x 2 in (76.2 x 50.8 x 3 mm): 14 min, 9.0 g.
- <from Brian: tackle box fit, wraps per 36 in rig, line sizes tested>

## Reuse

- `leader_card.py` `outline()` makes any rounded rectangle with a tangent-arc wave on its short edges; `make_plate.py` is a single-part, 0.4 nozzle PETG version of the helm panel plate script.
```

- [ ] **Step 2: Write the project memory**

Create `memory/project-leader-cards.md`:

```markdown
---
name: project-leader-cards
description: Leader cards status: PETG card for wrapping fishing leaders, hook-bend slots and 3 mm wavy wrap edges, see projects/Leader-cards
metadata:
  type: project
---

Leader cards (projects/Leader-cards) replace cardboard for wrapping 25 to 40 lb fishing leaders up to 36 in. Card 3 x 2 in (76.2 x 50.8 x 3 mm) white PETG, hook-bend slot variant N, 3 mm wave on the wrap edges. Status as of <YYYY-MM-DD>: <from Brian's final report>.

**Why:** cardboard slits tore and the card went soft when rigs were stored wet.

**How to apply:** for more cards, reprint `leader-card-print.3mf`; for a new size, change CARD_L and CARD_W in `leader_card.py` (width minus 2 x CORNER_R must be a whole number of 3 mm wave pitches, the outline asserts it). Retrospective: knowledge/learnings/leader-cards.md. Related: [[feedback-minimal-test-coupons]], [[marine-materials]].
```

Append this line to `memory/MEMORY.md`:

```
- [Leader cards](project-leader-cards.md) - PETG leader wrap card, hook-bend slots plus 3 mm wavy edges; status and reprint path
```

- [ ] **Step 3: Close the brief**

Set the brief's frontmatter `status:` line to `status: complete <YYYY-MM-DD>. Retrospective in knowledge/learnings/leader-cards.md`.

- [ ] **Step 4: Commit and push**

```bash
git add knowledge/learnings/leader-cards.md memory/project-leader-cards.md memory/MEMORY.md projects/Leader-cards/brief.md
git commit -m "Leader cards task 4: retrospective and project memory" -- knowledge/learnings/leader-cards.md memory/project-leader-cards.md memory/MEMORY.md projects/Leader-cards/brief.md
git push origin main
```
