"""Bambu Studio project 3MF for Logo Dude: ONE file, one plate per part (Brian 2026-09-29: one multi-plate 3MF per project).

  plate 1 "Badge"         object "Logo Dude badge":        backer (white, f1, z 0..3) + ink (black, f2, z 3..4) + face-stroke modifier
  plate 2 "Stand figure"  object "Logo Dude stand figure": the badge outline plus a tab (logodude_stand.py), same ink + modifier
  plate 3 "Stand base"    object "Logo Dude stand base":   black (f2) only, 0.20mm Standard values as object keys, no tower

Filament 1 = Bambu PETG Basic #FFFFFF, filament 2 = Bambu PETG Basic #000000. X2D 0.4 nozzle, 0.12 mm layers, textured PEI,
both filaments on extruder 1 (direct drive). Route: the CLI's own multi-plate assembler (--load-assemble-list, as in
Sharks-nametag/pipeline/plates.py and the iPhone case), which authors the plates, places the parts, sets the per-part filament
and carries the per-object keys (print_params). Built on the validated small-lettering recipe (knowledge/lettering-x2d.md) with
the Sharks-nametag tooling (fillcore_mod, graft_slice, gcode_features, toolpath_voids), imported unchanged:
  - process: the locked SMOOTH_TOP keys of Sharks flatten_04.py (no ironing, 2 top walls, arachne, skirt, tower brim ...),
    every one listed in different_settings_to_system[0]; project-wide, so the base gets them too
  - filament: PETG Basic's own preset (250 C, 245 C first layer); bed textured PEI 70 C, the preset's own value and
    the Sharks PETG setting, still written and listed in the filament diff slots (Brian 2026-09-29: PETG, not PLA)
  - plates 1 and 2: fill-core MODIFIER over the five thin face strokes only (outline + 0.3 mm, z band = the ink-only layers)
    with the recipe's region keys; infill_direction chosen from the strokes' own direction (they run mostly along x, the
    Sharks stems ran along y); the hair (about 5 mm wide) keeps the normal process; OBJECT key
    detect_narrow_internal_solid_infill 0
  - plate 3: OBJECT keys BASE_KEYS = the 0.20mm Standard values the base was proven with (layer_height 0.2, 15% grid
    infill, shells, bridge flow, classic walls, speeds); the first layer is 0.2 on every plate
  - prime tower per plate (wipe_tower_x/y vectors) at the free spot closest to the bed center: brim >= 12 mm from the part,
    >= 15 mm from the bed edges. Plate 3 prints one filament, so no tower prints there; its slot gets a legal spot anyway.

Verification (all offline): authored-file and CLI round-trip checks, then real CLI slices of every plate of the file (A), and
of plates 1 and 2 of the file without the modifiers (B, proves the modifier changes nothing outside the face strokes) and
without the object key (C, recipe step 5 side effect). Writes logodude.3mf and logodude-slice.json next to the STLs.

Findings baked in (2026-09-29): infill_direction 0. 33 layers, so the top layer runs at infill_direction itself (same
parity as the 37-layer Sharks tag; asserted on the slice). A one-off sweep of the modifier direction on this file gave
face-top line starts 0: 532, 45: 654, 90: 918, 135: 791, all with 0.00 mm2 stacked voids; fewest starts along the
strokes is what won the Sharks coupon by eye. B shows the modifier also stops Studio from running white top surface
under the black face strokes (the white top re-phases, same coverage) and gives the lower four ink layers of the
strokes a sparse core; both hidden. C shows the key's side effect stays in hidden layers and does not lose coverage,
so there is no concentric modifier.

Usage: .venv/bin/python projects/Logodude/pipeline/make_print_3mf.py
"""
import ast
import json
import math
import os
import re
import sys
import zipfile

import numpy as np
import trimesh
from scipy import ndimage
from shapely.affinity import translate
from shapely.geometry import Point, box
from shapely.ops import unary_union

PIPE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(PIPE)
BUILD = f"{PIPE}/build"
SHARKS = os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline")
sys.path.insert(0, SHARKS)
import fillcore_mod as fm  # noqa: E402
import gcode_features as gf  # noqa: E402
import toolpath_voids as tv  # noqa: E402
from graft_slice import graft_slice  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")
MACHINE = "Bambu Lab X2D 0.4 nozzle"
PROCESS = "0.12mm High Quality @BBL X2D"          # the unsuffixed X2D processes are the 0.4 nozzle ones
FILAMENT = "Bambu PETG Basic @BBL X2D 0.4 nozzle"
COLOURS = ["#FFFFFF", "#000000"]                   # filament n = position in this list
# Stand base: back on the settings it was proven with standalone (0.20mm Standard @BBL X2D, 26 min / 11.6 g), as
# per-object keys over the project's 0.12 HQ + SMOOTH_TOP process. Vector keys carry one value per extruder variant.
# Accelerations are print-wide and cannot be set per object, so the plate slices a little slower than the standalone file.
BASE_KEYS = {"layer_height": "0.2",
             "sparse_infill_density": "15%", "sparse_infill_pattern": "grid",
             "bottom_shell_layers": "3", "top_shell_thickness": "1",
             "bridge_flow": "1", "wall_generator": "classic",
             "inner_wall_speed": "300,600,600,200,200,200", "outer_wall_speed": "200,500,500,50,50,50",
             "sparse_infill_speed": "270,600,600,200,200,200", "internal_solid_infill_speed": "250,600,600,200,200,200",
             "bridge_speed": "50,50,50,50,200,200"}
PLATES = [  # the first part of each object is its anchor (placement, footprint); filaments are 1-based
    {"plate": "Badge", "object": "Logo Dude badge", "fillcore": True, "keys": fm.C7_OBJECT_KEYS,
     "parts": [{"stl": "logodude-backer.stl", "name": "backer (white)", "filament": 1},
               {"stl": "logodude-ink.stl", "name": "ink (black)", "filament": 2}]},
    {"plate": "Stand figure", "object": "Logo Dude stand figure", "fillcore": True, "keys": fm.C7_OBJECT_KEYS,
     "parts": [{"stl": "logodude-stand-figure-backer.stl", "name": "backer (white)", "filament": 1},
               {"stl": "logodude-ink.stl", "name": "ink (black)", "filament": 2}]},
    {"plate": "Stand base", "object": "Logo Dude stand base", "fillcore": False, "keys": BASE_KEYS,
     "parts": [{"stl": "logodude-stand-base.stl", "name": "base (black)", "filament": 2}]},
]
OUT = f"{PROJECT}/logodude.3mf"
CENTER = (128.0, 128.0)
PLATE_STRIDE = 307.2             # CLI plate pitch (256 * 1.2); 3 plates sit in 2 columns
BED_TYPE = "Textured PEI Plate"
BED_TEMP = "70"                  # PETG Basic on textured PEI (preset value; Sharks tags printed at 70)
NOZZLE_TEMP = "250"              # PETG Basic preset
BED_KEYS = ("textured_plate_temp", "textured_plate_temp_initial_layer")
FILAMENT_MAP = ["1", "1"]        # both filaments on extruder 1, the direct drive
BACKER_TOP, INK_TOP = 3.0, 4.0
NARROW = 2.5                     # recipe: strokes narrower than about 2.5 mm at the 0.4 nozzle need the fill core
DIRECTIONS = (0, 45, 90, 135)    # infill_direction candidates
# Layer-1 wipe tower brim relative to wipe_tower_x/y (x0, y0, x1, y1): measured on this file's own slice (2 filaments,
# one change, 5 mm brim, rib + fillet wall); the slice check asserts it still holds.
BRIM_OFFSETS = (-5.02, -5.04, 35.0, 33.67)   # 40.0 x 38.7 mm (Sharks 3-filament tower: fm.BRIM_OFFSETS, 51.5 x 52.6)


def locked_process_keys():
    """The SMOOTH_TOP dict of Sharks flatten_04.py, read without running that script."""
    src = open(f"{SHARKS}/flatten_04.py").read()
    node = next(n for n in ast.parse(src).body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SMOOTH_TOP")
    return ast.literal_eval(node.value)


SMOOTH_TOP = locked_process_keys()


def load(kind, name):
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
    """inherits chain plus include templates (copied from projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py)."""
    chain = [load(kind, name)]
    while "inherits" in chain[-1]:
        chain.append(load(kind, chain[-1]["inherits"]))
    merged = {}
    for layer in reversed(chain):
        for inc in layer.get("include", []):
            merged.update({k: v for k, v in load(kind, inc).items() if k not in ("name", "type", "from", "instantiation")})
        merged.update(layer)
    merged.pop("inherits", None)
    merged.pop("include", None)
    merged["name"] = name
    return merged


def plate_origin(n):
    """World xy of plate n's origin (1-based): the CLI lays plates out in rows of 2, rows going to -y."""
    return ((n - 1) % 2 * PLATE_STRIDE, -((n - 1) // 2) * PLATE_STRIDE)


# ------------------------------------------------------------------ geometry
def geometry(p):
    """Ink footprint split into the hair and the five face strokes, the backer outline, the fill direction, the z band."""
    backer = trimesh.load(f"{PROJECT}/{p['parts'][0]['stl']}")
    ink = trimesh.load(f"{PROJECT}/{p['parts'][1]['stl']}")
    assert backer.is_watertight and ink.is_watertight
    assert abs(backer.bounds[0][2]) < 1e-6 and abs(backer.bounds[1][2] - BACKER_TOP) < 1e-6
    assert abs(ink.bounds[0][2] - BACKER_TOP) < 1e-6 and abs(ink.bounds[1][2] - INK_TOP) < 1e-6
    polys = sorted(fm.section_polys(ink, (BACKER_TOP + INK_TOP) / 2), key=lambda q: -q.area)
    assert len(polys) == 6, len(polys)
    for z in (BACKER_TOP + 0.05, INK_TOP - 0.05):   # straight prisms: same outline over the whole ink height
        assert abs(sum(q.area for q in fm.section_polys(ink, z)) - sum(q.area for q in polys)) < 0.5, z
    # share of each shape narrower than NARROW (what an opening at NARROW / 2 removes)
    narrow = [1 - q.buffer(-NARROW / 2).buffer(NARROW / 2).intersection(q).area / q.area for q in polys]
    hair, face = polys[0], polys[1:]
    assert narrow[0] < 0.02 and min(narrow[1:]) > 0.5, narrow      # the hair is wide, every face shape is mostly narrow
    assert min(hair.distance(f) for f in face) > 2 * fm.MOD_BUFFER + 1, "the face modifier would reach the hair"
    # infill_direction: the candidate the face strokes run along most (length-weighted outline edges; for a thin
    # stroke the outline runs along the stroke)
    edges = np.vstack([np.diff(np.asarray(r.coords)[:, :2], axis=0) for q in face for r in (q.exterior, *q.interiors)])
    length, angle = np.hypot(edges[:, 0], edges[:, 1]), np.degrees(np.arctan2(edges[:, 1], edges[:, 0]))
    along = {d: float((length * (np.abs((angle - d + 90) % 180 - 90) <= 30)).sum() / length.sum()) for d in DIRECTIONS}
    direction = max(along, key=along.get)
    bsec = fm.section_polys(backer, BACKER_TOP / 2)
    assert len(bsec) == 1
    first = float(PROCESS_CFG["initial_layer_print_height"])
    layer = float(PROCESS_CFG["layer_height"])
    z0, z1, n_layers, tier = fm.modifier_z_band(BACKER_TOP, INK_TOP, first, layer)
    return dict(backer=bsec[0], hair=hair, face=face, narrow=narrow, along=along, direction=direction,
                mod_keys=dict(fm.C7_MOD_KEYS, infill_direction=str(direction)),
                z0=z0, z1=z1, n_layers=n_layers, tier=tier, first=first, layer=layer)


def footprint(mesh):
    """Plan outline of a part standing on z = 0: union of its sections near the bottom, middle and top."""
    h = mesh.bounds[1][2]
    return unary_union([q for z in (0.1, h / 2, h - 0.1) for q in fm.section_polys(mesh, z)])


def tower_spot(part_on_plate):
    """wipe_tower_x/y of the free spot closest to the bed center (the Sharks rule, with the real part outline in
    place of fm.check_tower's disc): brim >= fm.TOWER_DISC_MIN from the part, >= fm.TOWER_EDGE_MIN from the edges."""
    cx, cy = (BRIM_OFFSETS[0] + BRIM_OFFSETS[2]) / 2, (BRIM_OFFSETS[1] + BRIM_OFFSETS[3]) / 2
    grid = [(float(x), float(y)) for x in np.arange(0, fm.BED, 0.5) for y in np.arange(0, fm.BED, 0.5)]
    for t in sorted(grid, key=lambda t: math.hypot(t[0] + cx - CENTER[0], t[1] + cy - CENTER[1])):
        if check_tower(t, part_on_plate, strict=False):
            return t
    raise AssertionError("no tower spot")


def check_tower(tower, part_on_plate, strict=True):
    x0, y0, x1, y1 = (tower[0] + BRIM_OFFSETS[0], tower[1] + BRIM_OFFSETS[1],
                      tower[0] + BRIM_OFFSETS[2], tower[1] + BRIM_OFFSETS[3])
    edge = min(x0, y0, fm.BED - x1, fm.BED - y1)
    part = box(x0, y0, x1, y1).distance(part_on_plate)
    ok = edge >= fm.TOWER_EDGE_MIN and part >= fm.TOWER_DISC_MIN
    assert ok or not strict, f"tower {tower}: brim {part:.2f} mm from the part, {edge:.2f} mm from a bed edge"
    return (round(part, 2), round(edge, 2)) if ok else None


# ------------------------------------------------------------------- build
def build():
    os.makedirs(BUILD, exist_ok=True)
    for f in os.listdir(BUILD):
        os.remove(f"{BUILD}/{f}")
    proc = dict(PROCESS_CFG)
    for k, v in SMOOTH_TOP.items():   # list keys: one value per extruder variant, as many as the preset has
        proc[k] = [v[0]] * len(proc[k]) if isinstance(v, list) else v
    for fname, data in (("machine.json", flatten("machine", MACHINE)), ("process.json", proc),
                        ("filament.json", flatten("filament", FILAMENT))):
        with open(f"{BUILD}/{fname}", "w") as f:
            json.dump(data, f, indent=1)
    # pos_x/pos_y place the STLs' shared origin, plate-relative; the CLI adds the plate's origin
    spec = {"plates": [{"plate_name": p["plate"], "need_arrange": False, "plate_params": {"curr_bed_type": BED_TYPE},
                        "objects": [{"path": f"{PROJECT}/{q['stl']}", "count": 1, "filaments": [q["filament"]],
                                     "assemble_index": [1], "pos_x": [p["pos"][0]], "pos_y": [p["pos"][1]], "pos_z": [0]}
                                    for q in p["parts"]],
                        "assembled_params": [{"assemble_index": 1, "print_params": p["keys"]}]} for p in PLATES]}
    with open(f"{BUILD}/assemble.json", "w") as f:
        json.dump(spec, f, indent=1)
    fm.cli(["--arrange", "0", "--load-assemble-list", "assemble.json", "--load-settings", "machine.json;process.json",
            "--load-filaments", "filament.json;filament.json", "--export-3mf", "raw.3mf", "--outputdir", "."], BUILD, "assemble")

    with zipfile.ZipFile(f"{BUILD}/raw.3mf") as zin:
        cfg = json.loads(zin.read("Metadata/project_settings.config"))
        patch_config(cfg)
        model = zin.read("Metadata/model_settings.config").decode()
        model3d = zin.read("3D/3dmodel.model").decode()
        objfiles = {n: zin.read(n).decode() for n in zin.namelist() if n.startswith("3D/Objects/")}
        next_id = fm.next_object_id(model3d, objfiles)
        blocks = list(re.finditer(r'<object id="(\d+)">.*?</object>', model, re.S))
        assert len(blocks) == len(PLATES), len(blocks)
        out, pos = [], 0
        for m in blocks:
            oid, block = m.group(1), m.group(0)
            p = plate_of(block)
            block = re.sub(r'(<object id="\d+">\s*<metadata key="name" value=")[^"]*"', rf'\g<1>{p["object"]}"', block, count=1)
            if len(p["parts"]) == 1:   # single-filament object: the object-level extruder follows its part (the iPhone case fix)
                block = re.sub(r'(<object id="\d+">\s*<metadata key="name" value="[^"]*"/>)(\s*<metadata key="extruder" value="\d+"/>)?',
                               rf'\1\n    <metadata key="extruder" value="{p["parts"][0]["filament"]}"/>', block, count=1)
            for q in p["parts"]:   # each part is named after its STL by the CLI
                block, n = re.subn(rf'(<part id="\d+" subtype="normal_part"[^>]*>\s*<metadata key="name" value=")[^"]*("/>(?:(?!</part>).)*?value="{re.escape(q["stl"])}")',
                                   rf'\g<1>{q["name"]}\g<2>', block, flags=re.S)
                assert n == 1, (q["stl"], n)
            p["opos"] = fm.object_pos(model3d, oid, p["anchor_center"])
            if p["fillcore"]:
                G = p["geo"]
                mod_c, mod_center = fm.centered(fm.extrude(fm.modifier_2d(G["face"]), G["z0"], G["z1"]))
                assert mod_c.is_watertight
                name = "MOD face strokes fill-core: " + ", ".join(f"{k} {v}" for k, v in G["mod_keys"].items())
                block, model3d = fm.inject_modifier(block, model3d, objfiles, oid, next_id, name, "mod-face-strokes.stl",
                                                    mod_c, mod_center, p["opos"], G["mod_keys"])
                next_id += 1
            out += [model[pos:m.start()], block]
            pos = m.end()
        model = "".join(out) + model[pos:]
        model = re.sub(r'( *)<metadata key="filament_map_mode" value="[^"]*"/>',
                       lambda k: f'{k.group(1)}<metadata key="filament_map_mode" value="Manual"/>\n'
                                 f'{k.group(1)}<metadata key="filament_maps" value="{" ".join(FILAMENT_MAP)}"/>', model)
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = {"Metadata/project_settings.config": json.dumps(cfg, indent=4), "Metadata/model_settings.config": model,
                        "3D/3dmodel.model": model3d}.get(item.filename, objfiles.get(item.filename))
                zout.writestr(item, data if data is not None else zin.read(item.filename))


def plate_of(block):
    """The PLATES entry whose anchor STL is this object's first part."""
    hits = [p for p in PLATES if re.search(rf'key="source_file" value="{re.escape(p["parts"][0]["stl"])}"', block.split("</part>", 1)[0])]
    assert len(hits) == 1, [p["plate"] for p in hits]
    return hits[0]


def patch_config(cfg):
    """The CLI export's fixes (reference-two-material-two-plate-3mf): colours, per-filament vectors, the flush block
    (extruders x filaments^2), extruder map; plus bed, per-plate towers and every changed key in different_settings_to_system."""
    nf, ne = len(COLOURS), len(cfg["nozzle_diameter"])
    cfg["filament_colour"] = cfg["filament_multi_colour"] = list(COLOURS)
    cfg["filament_map_mode"], cfg["filament_map"], cfg["filament_nozzle_map"] = "Manual", FILAMENT_MAP, FILAMENT_MAP
    cfg["flush_multiplier"], cfg["flush_multiplier_fast"] = ["1"] * ne, ["1.2"] * ne
    # 280 mm3 placeholder (as every vault CLI build); Studio's "Re-calculate" sets the colour-based value
    cfg["flush_volumes_matrix"] = ["0" if a == b else "280" for _ in range(ne) for a in range(nf) for b in range(nf)]
    cfg["flush_volumes_vector"] = ["140"] * (ne * nf)
    cfg["curr_bed_type"] = BED_TYPE
    for k in BED_KEYS:
        cfg[k] = [BED_TEMP] * nf
    cfg["wipe_tower_x"], cfg["wipe_tower_y"] = tower_vectors()
    diff = cfg["different_settings_to_system"]
    assert len(diff) == nf + 2, diff    # [process, filament 1..n, machine]
    diff[0] = ";".join(sorted(set(x for x in diff[0].split(";") if x) | set(SMOOTH_TOP)))
    for i in range(1, nf + 1):
        diff[i] = ";".join(sorted(set(x for x in diff[i].split(";") if x) | set(BED_KEYS)))
    return cfg


def tower_vectors():
    return [f"{p['tower'][0]:g}" for p in PLATES], [f"{p['tower'][1]:g}" for p in PLATES]


# ------------------------------------------------------------------ checks
def check_file(path, label):
    with zipfile.ZipFile(path) as z:
        cfg = json.loads(z.read("Metadata/project_settings.config"))
        ms = z.read("Metadata/model_settings.config").decode()
        m3 = z.read("3D/3dmodel.model").decode()
    assert cfg["printer_settings_id"] == MACHINE and cfg["print_settings_id"] == PROCESS, label
    assert cfg["filament_settings_id"] == [FILAMENT] * 2 and cfg["filament_type"] == ["PETG", "PETG"], label
    assert cfg["nozzle_diameter"][0] == "0.4" and cfg["layer_height"] == "0.12", (label, cfg["layer_height"])
    assert cfg["filament_colour"] == COLOURS, (label, cfg["filament_colour"])
    assert cfg["filament_map"] == FILAMENT_MAP and cfg["filament_map_mode"] == "Manual", label
    assert cfg["curr_bed_type"] == BED_TYPE and all(cfg[k] == [BED_TEMP] * 2 for k in BED_KEYS), label
    for k, v in SMOOTH_TOP.items():
        got = cfg[k]
        assert (set(got) == {v[0]} if isinstance(v, list) else got == v), f"{label}: {k} = {got}"
    diff = cfg["different_settings_to_system"]
    assert set(SMOOTH_TOP) <= set(diff[0].split(";")), f"{label}: process keys missing from the diff list"
    assert all(set(BED_KEYS) <= set(diff[i].split(";")) for i in (1, 2)), f"{label}: bed keys missing from the filament diff slots"
    assert (cfg["wipe_tower_x"], cfg["wipe_tower_y"]) == tower_vectors(), (label, cfg["wipe_tower_x"], cfg["wipe_tower_y"])
    ne = len(cfg["nozzle_diameter"])
    assert len(cfg["flush_volumes_matrix"]) == ne * 4 and cfg["flush_volumes_matrix"][:4] == ["0", "280", "280", "0"], label
    assert cfg["print_sequence"] == "by layer" and cfg["enable_prime_tower"] == "1", label
    # plates: count, names, membership, per-plate bed type and extruder map
    objs = {oid: body for oid, body in re.findall(r'<object id="(\d+)">(.*?)</object>', ms, re.S)}
    assert len(objs) == len(PLATES), (label, len(objs))
    names = {oid: re.search(r'<metadata key="name" value="([^"]*)"', body).group(1) for oid, body in objs.items()}
    plates = re.findall(r"<plate>(.*?)</plate>", ms, re.S)
    got = [(re.search(r'key="plater_name" value="([^"]*)"', b).group(1), [names[i] for i in re.findall(r'key="object_id" value="(\d+)"', b)])
           for b in plates]
    assert got == [(p["plate"], [p["object"]]) for p in PLATES], (label, got)
    for b in plates:
        assert 'key="filament_map_mode" value="Manual"' in b and f'key="filament_maps" value="{" ".join(FILAMENT_MAP)}"' in b, label
        assert 'key="bed_type" value="Textured PEI Plate"' in b, label
    # per object: object keys in the head, per-part filaments and names, modifier and its keys, components, placement
    main_items = dict(re.findall(r'<item objectid="(\d+)"[^>]*transform="([^"]*)"', m3))
    for n, p in enumerate(PLATES, 1):
        oid = next(i for i, nm in names.items() if nm == p["object"])
        body = objs[oid]
        head = body.split("<part ", 1)[0]
        for k in set(fm.C7_OBJECT_KEYS) | set(BASE_KEYS):
            assert (f'key="{k}"' in head) == (k in p["keys"]), f"{label}: {p['object']} object key {k}"
        mkeys = p["geo"]["mod_keys"] if p["fillcore"] else None
        want_parts = (len(p["parts"]), 1 if p["fillcore"] else 0)
        if len(p["parts"]) == 1:
            # one-part object: Studio keeps the filament on the object and drops the part's copy on a round trip
            fil = str(p["parts"][0]["filament"])
            assert re.search(r'<metadata key="extruder" value="(\d+)"', head).group(1) == fil, label
            assert set(re.findall(r'"extruder" value="(\d+)"', body.split("<part ", 1)[1])) <= {fil}, label
            assert all(f'<metadata key="{k}" value="{v}"/>' in head for k, v in p["keys"].items()), label
            assert body.count('subtype="normal_part"') == 1 and "modifier_part" not in body, label
        else:
            assert fm.check_object(body, p["keys"], mkeys, [str(q["filament"]) for q in p["parts"]], label) == want_parts, label
        pnames = re.findall(r'<part id="\d+" subtype="normal_part"[^>]*>\s*<metadata key="name" value="([^"]*)"', body)
        assert pnames == [q["name"] for q in p["parts"]], (label, pnames)
        comps = re.search(rf'<object id="{oid}" [^>]*>\s*<components>(.*?)</components>', m3, re.S).group(1)
        assert len(re.findall(r"<component ", comps)) == sum(want_parts), (label, p["object"])
        tf = main_items[oid].split()
        opos = fm.object_pos(m3, oid, p["anchor_center"])
        ox, oy = plate_origin(n)
        # world = item transform + component transform; how the offset splits between them is the writer's choice
        world = [float(tf[9 + i]) + opos[i] + p["anchor_center"][i] for i in range(3)]
        assert abs(world[0] - ox - CENTER[0]) < 0.01 and abs(world[1] - oy - CENTER[1]) < 0.01, (label, p["plate"], world)
        assert abs(world[2] - p["anchor_center"][2]) < 1e-6, (label, p["plate"], world)
    return cfg


def slice_plate(src, tag, n):
    res = graft_slice(src, f"{BUILD}/sliced-{tag}.3mf", plate=n)
    assert res["rc"] == 0 and res["gcode"], f"slice {tag} failed rc={res['rc']}, log {res['log']}"
    with zipfile.ZipFile(res["out"]) as z:
        info = z.read("Metadata/slice_info.config").decode()
        gcode = z.read(res["gcode"]).decode(errors="ignore")
    blocks = [b for b in re.findall(r"<plate>(.*?)</plate>", info, re.S) if re.search(rf'key="index" value="{n}"', b)]
    assert len(blocks) == 1, f"slice {tag}: no slice_info block for plate {n}"
    res["info"] = blocks[0]
    res["g"] = gcode
    return res


def variant(tag, strip_modifier=False, strip_key=False):
    """The authored file without the modifiers (B) or without the fill-core object key (C), everything else identical."""
    dst = f"{BUILD}/variant-{tag}.3mf"
    if strip_modifier:
        fm.strip_recipe(OUT, dst, keep_object_key=True)
        return dst
    with zipfile.ZipFile(OUT) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "Metadata/model_settings.config" and strip_key:
                data, n = re.subn(rb'\s*<metadata key="detect_narrow_internal_solid_infill" value="0"/>', b"", data)
                assert n == sum(p["fillcore"] for p in PLATES), n
            zout.writestr(item, data)
    return dst


def zone_px(geom):
    b = geom.bounds
    x0, y1 = b[0] - 1.0, b[3] + 1.0
    W, H = int((b[2] - b[0] + 2.0) / tv.PX), int((b[3] - b[1] + 2.0) / tv.PX)
    return x0, y1, W, H, tv.poly_mask(geom, x0, y1, W, H)


def face_metrics(layers, face, ink_layers):
    """toolpath_voids' tag metrics on the face strokes: stacked visible voids over the top 5 ink layers, top-layer
    interior gaps, line starts, and per layer the fill direction, line widths and wall features inside the strokes."""
    x0, y1, W, H, lmask = zone_px(face)
    imask = tv.poly_mask(face.buffer(-tv.INSET), x0, y1, W, H)
    top = ink_layers[-5:]
    stack = np.zeros((H, W), int)
    per = []
    for z in ink_layers:
        segs = layers[z]
        inside = [s for s in segs if face.contains(Point((s[0] + s[2]) / 2, (s[1] + s[3]) / 2))]
        ang, frac, flen = tv.fill_direction(segs, lmask, x0, y1, W, H)
        row = dict(z=z, fill_deg=None if ang is None else round(ang, 1), along_frac=round(frac, 2), fill_mm=round(flen),
                   widths={f: sorted({round(s[4], 2) for s in inside if s[5] == f}) for f in ("Top surface", "Internal solid infill")},
                   inner_wall_mm=round(sum(math.hypot(s[2] - s[0], s[3] - s[1]) for s in inside if s[5] == "Inner wall"), 1))
        if z in top:
            cov, _ = tv.rasterize(segs, x0, y1, W, H, mask_only=True)
            unc = lmask & ~cov
            stack += unc
            row["uncovered_mm2"] = round(unc.sum() * tv.PX ** 2, 2)
            if z == top[-1]:
                row["top_interior_mm2"] = round((unc & imask).sum() * tv.PX ** 2, 2)
                row["starts"] = sum(1 for s in segs if s[6] and face.buffer(0.1).contains(Point(s[0], s[1])))
        per.append(row)
    vis = ndimage.binary_opening(stack >= tv.STACK_MIN, structure=tv.disk(tv.OPEN_DISK))
    return dict(visible_mm2=round(vis.sum() * tv.PX ** 2, 2), layers=per)


def uncovered(layers, z, zone):
    x0, y1, W, H, m = zone_px(zone)
    cov, _ = tv.rasterize(layers[z], x0, y1, W, H, mask_only=True)
    return round((m & ~cov).sum() * tv.PX ** 2, 2)


def outside_diff(ma, mb, zone):
    """{feature: layers, segments only in A, only in B} for extrusion segments with both ends outside `zone`
    (gcode_features.compare's segment key, over every layer, with a prepared zone for speed)."""
    from collections import Counter
    from shapely.prepared import prep
    pz = prep(zone)

    def keys(moves):
        return Counter((m[0], m[1], round(m[3], 3), round(m[4], 3), round(m[5], 3), round(m[6], 3), round(m[7], 5))
                       for m in moves if m[1] not in gf.PSEUDO
                       and not (pz.intersects(Point(m[3], m[4])) or pz.intersects(Point(m[5], m[6]))))
    ka, kb = keys(ma), keys(mb)
    out = {}
    for side, d in (("only_A", ka - kb), ("only_B", kb - ka)):
        for k, n in d.items():
            f = out.setdefault(k[1], {"layers": [], "only_A": 0, "only_B": 0})
            f[side] += n
            if k[0] not in f["layers"]:
                f["layers"] = sorted(f["layers"] + [k[0]])
    return out


def tool_changes(g):
    """(start tool, [(z, tool)] for every filament change after the start G-code). T0/T1 pick filament 1/2; "T1 H-1" is a
    load, T65279 and the like are unloads."""
    is_t = lambda line: re.match(r"\s*T\d+( |$)", line) and int(line.split()[0][1:]) < 16
    i = g.index("; Z_HEIGHT:")
    start = [line.split()[0] for line in g[:i].splitlines() if is_t(line)]
    assert start, "no tool selected in the start G-code"
    tools, z_now, changes = [start[-1]], None, []
    for line in g[i:].splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z_now = round(float(line.split(":")[1]), 3)
        elif is_t(line):
            t = line.split()[0]
            if tools[-1] != t:
                changes.append((z_now, t))
            tools.append(t)
    flush = [float(v) for v in re.findall(r"^M620\.10 A1 \S+ L([0-9.]+)", g[i:], re.M)]
    return start[-1], changes, flush


def grams_by_feature(g):
    per = gf.feature_split(gf.parse_moves(g), gf.header(g))[0]
    return {k: round(v, 2) for k, v in sorted(per.items(), key=lambda kv: -kv[1]) if v >= 0.005}


def verify_plate(n, p, A):
    """Checks every plate gets: filaments, extruder, temperatures, layers, filament changes, tower, placement, bed bounds."""
    g, info = A["g"], A["info"]
    used = {int(i): float(v) for i, v in re.findall(r'<filament id="(\d+)"[^>]*?used_g="([^"]*)"', info)}
    groups = set(re.findall(r'<filament id="\d+"[^>]*?group_id="(\d+)"', info))
    pred = int(re.search(r'key="prediction" value="(\d+)"', info).group(1))
    want_fil = sorted({q["filament"] for q in p["parts"]})
    assert sorted(used) == want_fil and groups == {"0"}, (p["plate"], used, groups)
    assert "X2D start gcode" in g, "machine include templates did not merge"
    assert re.search(r"^; filament_map = 1,1$", g, re.M), p["plate"]
    assert re.search(rf"^\s*M1[49]0 S{BED_TEMP}\b", g, re.M), f"{p['plate']}: bed temperature"
    assert re.search(rf"^\s*M10[49] S{NOZZLE_TEMP}\b", g, re.M), f"{p['plate']}: nozzle temperature (PETG Basic 250)"
    layers = tv.parse_layers(g)
    zs = sorted(layers)
    steps = sorted({round(b - a, 3) for a, b in zip(zs, zs[1:])})
    layer_h = float(p["keys"].get("layer_height", PROCESS_CFG["layer_height"]))
    first = float(PROCESS_CFG["initial_layer_print_height"])
    height = p["anchor"].bounds[1][2] if len(p["parts"]) == 1 else INK_TOP
    assert A["layers"] == len(zs) == len(fm.layer_centers(first, layer_h, height)), (p["plate"], A["layers"], len(zs))
    assert zs[0] == first and steps == [layer_h] and abs(zs[-1] - height) <= layer_h / 2, (p["plate"], zs[:3], zs[-1], steps)
    start, changes, flush = tool_changes(g)
    feats = {s[5] for z in zs for s in layers[z]}
    assert "Brim" not in feats and "Skirt" in feats, (p["plate"], feats)
    xy = [min(min(s[0], s[2]) for z in zs for s in layers[z]), min(min(s[1], s[3]) for z in zs for s in layers[z]),
          max(max(s[0], s[2]) for z in zs for s in layers[z]), max(max(s[1], s[3]) for z in zs for s in layers[z])]
    assert xy[0] >= 0 and xy[1] >= 0 and xy[2] <= fm.BED and xy[3] <= fm.BED, (p["plate"], "toolpaths leave the bed", xy)
    walls = [s for s in layers[zs[0]] if s[5] == "Outer wall"]
    wb = (min(s[0] for s in walls), min(s[1] for s in walls), max(s[0] for s in walls), max(s[1] for s in walls))
    assert abs((wb[0] + wb[2]) / 2 - CENTER[0]) < 0.5 and abs((wb[1] + wb[3]) / 2 - CENTER[1]) < 0.5, (p["plate"], wb)
    row = {"object": p["object"], "rc": A["rc"], "time_estimate": A["time"], "prediction_s": pred, "minutes": round(pred / 60, 1),
           "layers": A["layers"], "first_layer_mm": zs[0], "layer_mm": steps[0], "top_z_mm": zs[-1],
           "grams": {COLOURS[i - 1] + (" white" if i == 1 else " black"): used[i] for i in sorted(used)},
           "grams_total": round(sum(used.values()), 2), "nozzle_C": int(NOZZLE_TEMP), "bed_C": int(BED_TEMP),
           "start_tool": start, "toolpath_xy_mm": [round(v, 2) for v in xy]}
    tw = [s for s in layers[zs[0]] if s[5] in ("Prime tower", "Wipe tower")]
    if len(want_fil) == 1:   # one filament: no change, no flush, no tower on any layer
        assert start == f"T{want_fil[0] - 1}" and changes == [] and flush == [], (p["plate"], start, changes, flush)
        assert not feats & {"Prime tower", "Wipe tower"}, (p["plate"], feats)
        row.update({"filament_changes": [], "tower": None})
        return row, layers, zs
    # exactly one filament change, white -> black, at the first ink layer
    first_ink = min(z for z in zs if z - layer_h / 2 > BACKER_TOP)
    assert start == "T0" and changes == [(first_ink, "T1")] and len(flush) == 1, (p["plate"], start, changes, flush)
    # the tower: layer-1 brim inside the predicted rectangle, clear of the part and the bed edges
    assert tw, "no tower on layer 1"
    T = p["tower"]
    tb = (min(min(s[0], s[2]) for s in tw), min(min(s[1], s[3]) for s in tw), max(max(s[0], s[2]) for s in tw), max(max(s[1], s[3]) for s in tw))
    meas = tuple(round(v - T[i % 2], 2) for i, v in enumerate(tb))
    pred_brim = (T[0] + BRIM_OFFSETS[0], T[1] + BRIM_OFFSETS[1], T[0] + BRIM_OFFSETS[2], T[1] + BRIM_OFFSETS[3])
    assert all(tb[i] >= pred_brim[i] - 0.5 for i in (0, 1)) and all(tb[i] <= pred_brim[i] + 0.5 for i in (2, 3)), (meas, BRIM_OFFSETS)
    part = box(*tb).distance(p["footprint_plate"])
    edge = min(tb[0], tb[1], fm.BED - tb[2], fm.BED - tb[3])
    assert part >= fm.TOWER_DISC_MIN and edge >= fm.TOWER_EDGE_MIN, (part, edge)
    row.update({"filament_changes": [{"z": changes[0][0], "tool": changes[0][1], "flush_mm": flush[0],
                                      "flush_mm3": round(flush[0] * math.pi * 0.875 ** 2)}],
                "tower": {"wipe_tower_xy": list(T), "layer1_bbox": [round(v, 2) for v in tb], "bbox_minus_xy": meas,
                          "clear_of_part_mm": round(part, 2), "clear_of_bed_edge_mm": round(edge, 2)}})
    return row, layers, zs


def verify_fillcore(p, A, B, C, layers, zs):
    """The fill-core recipe on one plate: modifier keys in effect in the face strokes, the hair untouched, and the B/C
    comparisons (every extrusion segment outside the face strokes + 1 mm, per layer and feature)."""
    G, opos = p["geo"], p["opos"]
    g = A["g"]
    first_ink = min(z for z in zs if z - G["layer"] / 2 > BACKER_TOP)
    ink_layers = [z for z in zs if z - G["layer"] / 2 > BACKER_TOP]
    face_plate = translate(unary_union(G["face"]), *opos[:2])
    hair_plate = translate(G["hair"], *opos[:2])
    fmA = face_metrics(layers, face_plate, ink_layers)
    top = fmA["layers"][-1]
    # modifier keys in effect inside the face strokes: 0.3 top / internal solid lines, one wall, fill along the strokes
    for row in fmA["layers"]:
        for f, ws in row["widths"].items():
            assert all(abs(w - 0.3) <= 0.03 for w in ws), (row["z"], f, ws)   # 0.3 lines (Studio adjusts spacing a little)
        assert row["inner_wall_mm"] < 1.0, (row["z"], row["inner_wall_mm"])
    assert top["fill_deg"] is not None and min(abs(top["fill_deg"] - G["direction"]), 180 - abs(top["fill_deg"] - G["direction"])) <= 15, top
    dirs = [r["fill_deg"] for r in fmA["layers"][-5:]]
    hair_top = {round(s[4], 2) for s in layers[zs[-1]] if s[5] == "Top surface" and hair_plate.contains(Point((s[0] + s[2]) / 2, (s[1] + s[3]) / 2))}
    assert hair_top == {0.42}, hair_top

    zone = face_plate.buffer(1.0)
    mA = gf.parse_moves(g)
    diffB, diffC = outside_diff(mA, gf.parse_moves(B["g"]), zone), outside_diff(mA, gf.parse_moves(C["g"]), zone)
    layersB, layersC = tv.parse_layers(B["g"]), tv.parse_layers(C["g"])
    fmB, fmC = face_metrics(layersB, face_plate, ink_layers), face_metrics(layersC, face_plate, ink_layers)
    # B: the modifier leaves every visible surface outside the face strokes alone. Layer 1 and all walls are identical;
    # the white top layer (last backer layer) only re-phases its lines, because without the modifier Studio also runs
    # top surface under the black strokes; the rest is hidden infill.
    last_backer = max(z for z in zs if z < first_ink)
    white = translate(G["backer"].buffer(-0.5), *opos[:2]).difference(translate(unary_union(G["face"] + [G["hair"]]), *opos[:2]).buffer(0.5))
    hidden = {"Internal solid infill", "Sparse infill", "Bridge", "Gap infill", "Floating vertical shell"}
    for tag, d in (("B", diffB), ("C", diffC)):
        assert set(d) <= hidden | {"Top surface"}, (tag, set(d))
        assert all(zs[0] not in f["layers"] for f in d.values()), (tag, "layer 1 changed")
        assert set(d.get("Top surface", {"layers": []})["layers"]) <= {last_backer}, (tag, d["Top surface"])
    white_top = {"A": uncovered(layers, last_backer, white), "B": uncovered(layersB, last_backer, white),
                 "C": uncovered(layersC, last_backer, white)}
    assert max(white_top.values()) - min(white_top.values()) < 0.1, white_top
    # C: the object key's side effect (recipe step 5) sits in hidden layers only (checked above); in the white top-shell
    # layers under the visible white top it does not lose coverage, so no concentric modifier is added
    shell = [z for z in zs if last_backer - 4 * G["layer"] < z <= last_backer and any(z in f["layers"] for f in diffC.values())]
    side = [dict(z=z, uncovered_mm2_key_on=uncovered(layers, z, white), uncovered_mm2_key_off=uncovered(layersC, z, white)) for z in shell]
    assert all(r["uncovered_mm2_key_on"] <= r["uncovered_mm2_key_off"] + 0.1 for r in side), side
    assert fmA["visible_mm2"] <= min(fmB["visible_mm2"], fmC["visible_mm2"]), (fmA["visible_mm2"], fmB["visible_mm2"], fmC["visible_mm2"])
    return {"face_strokes_A": fmA, "top_fill_directions_last5": dirs, "hair_top_line_width": sorted(hair_top),
            "white_top_uncovered_mm2": white_top,
            "B_no_modifier": {"time": B["time"], "diff_outside_face_zone": diffB,
                              "face_visible_mm2": fmB["visible_mm2"], "face_top": fmB["layers"][-1]},
            "C_no_object_key": {"time": C["time"], "diff_outside_face_zone": diffC, "white_shell_layers_uncovered": side,
                                "face_visible_mm2": fmC["visible_mm2"], "face_top": fmC["layers"][-1]}}


def verify():
    cfg = check_file(OUT, "authored")
    fm.cli(["--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", OUT], BUILD, "round trip")
    check_file(f"{BUILD}/roundtrip.3mf", "CLI round trip")
    report = {"round_trip": "pass: 3 plates, plate names and membership, colours, per-part filaments, part and object names, "
                            "modifiers + keys, object keys (fill-core key on plates 1-2, all BASE_KEYS with their values on plate 3), "
                            "per-plate tower vectors, diff lists, per-plate placement",
              "flush_matrix": cfg["flush_volumes_matrix"], "plates": {}}
    variants = {"B": variant("B", strip_modifier=True), "C": variant("C", strip_key=True)}
    for n, p in enumerate(PLATES, 1):
        A = slice_plate(OUT, f"A{n}", n)
        row, layers, zs = verify_plate(n, p, A)
        row["grams_by_feature"] = grams_by_feature(A["g"])
        if p["fillcore"]:
            B, C = (slice_plate(variants[t], f"{t}{n}", n) for t in ("B", "C"))
            row["fill_core"] = verify_fillcore(p, A, B, C, layers, zs)
        report["plates"][f"{n} {p['plate']}"] = row
        print(f"plate {n} {p['plate']}: {row['time_estimate']}, {row['grams']}, {row['layers']} layers at {row['layer_mm']} mm, "
              f"changes {row['filament_changes']}, tower {row['tower'] and row['tower']['wipe_tower_xy']}", flush=True)
    rows = report["plates"].values()
    report["total"] = {"minutes": round(sum(r["prediction_s"] for r in rows) / 60, 1),
                       "grams": round(sum(r["grams_total"] for r in rows), 2)}
    return report


PROCESS_CFG = flatten("process", PROCESS)
for _p in PLATES:
    _p["anchor"] = trimesh.load(f"{PROJECT}/{_p['parts'][0]['stl']}")
    _p["anchor_center"] = _p["anchor"].bounds.mean(axis=0)
    _p["pos"] = (CENTER[0] - float(_p["anchor_center"][0]), CENTER[1] - float(_p["anchor_center"][1]))
    _p["footprint_plate"] = translate(footprint(_p["anchor"]), *_p["pos"])
    _p["tower"] = tower_spot(_p["footprint_plate"])
    if _p["fillcore"]:
        _p["geo"] = geometry(_p)
        assert _p["geo"]["n_layers"] == 33 and _p["geo"]["direction"] == 0, (_p["plate"], _p["geo"]["n_layers"], _p["geo"]["direction"])


def main():
    for p in PLATES:
        print(f"plate {p['plate']}: tower {p['tower']} clearance {check_tower(p['tower'], p['footprint_plate'])}"
              + (" (unused: one filament)" if not p["fillcore"] else ""))
        if p["fillcore"]:
            G = p["geo"]
            print(f"  face strokes narrower than {NARROW} mm: hair {G['narrow'][0]:.1%}, face " + ", ".join(f"{v:.0%}" for v in G["narrow"][1:]))
            print(f"  direction: share of face-stroke length within 30 deg of each candidate {G['along']} -> {G['direction']}")
            print(f"  modifier z {G['z0']:.2f}..{G['z1']:.2f} over ink layer centers {G['tier']}; {G['n_layers']} layers")
    build()
    report = verify()
    G = PLATES[0]["geo"]
    report.update({"presets": {"machine": MACHINE, "process": PROCESS, "filament": FILAMENT, "colours": COLOURS},
                   "object_keys": {p["plate"]: p["keys"] for p in PLATES},
                   "geometry": {"narrow_share": {"hair": round(G["narrow"][0], 3), "face": [round(v, 3) for v in G["narrow"][1:]]},
                                "along_share": G["along"], "infill_direction": G["direction"],
                                "modifier": {"buffer": fm.MOD_BUFFER, "z": [round(G["z0"], 3), round(G["z1"], 3)],
                                             "layers": G["tier"], "keys": G["mod_keys"]}}})
    with open(OUT.replace(".3mf", "-slice.json"), "w") as f:
        json.dump(report, f, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("fill_core", "grams_by_feature")} for k, v in report["plates"].items()}, indent=1))
    print(OUT, report["total"])


if __name__ == "__main__":
    main()
