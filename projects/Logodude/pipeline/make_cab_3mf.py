"""Bambu Studio project 3MF for the Logo Dude CAB LOGO size samples (2026-10-30): logodude-cab.3mf, one plate,
three objects (2.5, 3 and 3.5 in wide), so one print gives Brian all three to hold against the walnut 1x12.

Adapted from make_tag_3mf.py (the luggage tag, 0.4 nozzle mode), which is left untouched. Each object:
    backer (white, filament 1, z 0..3.08)        layers 1-19 on the 0.16 grid (0.2 first layer)
    ink (black, filament 2, z 3.08..4.04)        layers 20-25
Plain backs (the mount goes onto the size Brian picks). PETG Basic white + black, textured PEI 70 C, 250 C.
Same locked process keys as the tag (arachne, 2-loop skirt, no brim, 100% zig-zag, elefant_foot 0). One filament
change, at layer 20. Prime tower at the free spot closest to the bed centre, brim re-measured from the slice.

Verification, offline: authored-file checks, a CLI round trip, a real CLI slice (graft_slice) with G-code proofs:
no black in the backer layers, black above the backer only inside the three ink footprints, no white above the
backer, every layer of each tier present. Writes logodude-cab.3mf and logodude-cab-slice.json.

Usage: .venv/bin/python projects/Logodude/pipeline/make_cab_3mf.py
"""
import json
import math
import os
import re
import sys
import zipfile

import numpy as np
import trimesh
from shapely.affinity import translate
from shapely.geometry import box
from shapely.ops import unary_union

PIPE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(PIPE)
SHARKS = os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline")
sys.path.insert(0, SHARKS)
import fillcore_mod as fm  # noqa: E402  section_polys, cli, BED, tower minimums
import gcode_features as gf  # noqa: E402
from graft_slice import graft_slice  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")
NOZZLE = "0.4"
MACHINE = "Bambu Lab X2D 0.4 nozzle"
PROCESS = "0.16mm Standard @BBL X2D"
FILAMENT = "Bambu PETG Basic @BBL X2D 0.4 nozzle"
BUILD = f"{PIPE}/build-cab"
COLOURS = ["#FFFFFF", "#000000"]                  # filament n = position in this list
PLATE = "Size samples"
# the three objects: (name, STL tag, bed centre of the backer's bounding box); 3.5 and 3 across the top, 2.5 below
OBJECTS = [{"name": "Logo Dude 3.5 in", "tag": "35", "center": (62.0, 178.0)},
           {"name": "Logo Dude 3 in", "tag": "3", "center": (170.0, 178.0)},
           {"name": "Logo Dude 2.5 in", "tag": "25", "center": (62.0, 78.0)}]
PARTS = [("backer", "backer (white)", 1), ("ink", "ink (black)", 2)]     # (key, part name, filament); backer = anchor
OUT = f"{PROJECT}/logodude-cab.3mf"
BED_TYPE = "Textured PEI Plate"
BED_KEYS = ("textured_plate_temp", "textured_plate_temp_initial_layer")
FILAMENT_MAP = ["1", "1"]                         # both filaments on extruder 1
LOCKED = {                                        # the tag's set (make_tag_3mf.py), unchanged
    "ironing_type": "no ironing",
    "seam_gap": "0%",
    "small_perimeter_speed": ["30"], "small_perimeter_threshold": ["10"], "gap_infill_speed": ["40"],
    "wall_distribution_count": "3", "wall_transition_filter_deviation": "50%",
    "min_feature_size": "10%", "min_bead_width": "50%",
    "wall_generator": "arachne",
    "prime_tower_brim_width": "5", "prime_tower_rib_wall": "1", "prime_tower_fillet_wall": "1",
    "top_shell_layers": "5", "top_surface_speed": ["60"],
    "skirt_loops": "2", "skirt_distance": "3", "skirt_height": "1",
    "initial_layer_speed": ["30"], "initial_layer_infill_speed": ["50"],
    "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag",
    "brim_type": "no_brim",
    "elefant_foot_compensation": "0",
}
BRIM_OFFSETS = (-3.87, -5.0, 30.84, 29.22)       # the tag's measured layer-1 tower brim at 0.16 Standard; re-measured below
BRIM_TOL = 0.5
NOT_PART = ("Prime tower", "Wipe tower", "Skirt", "Brim", "Flush + retract net", "Start purge", "Custom", "Support",
            "Support interface", "Support transition")
FOOT_PAD = 1.0
PART_GAP_MIN = 12.0                               # mm between the samples' footprints (skirts stay apart)


def load(kind, name):
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
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


def stl(o, key):
    return f"logodude-cab-{o['tag']}-{key}.stl"


def footprint(mesh):
    h = mesh.bounds[1][2]
    return unary_union([q for z in (0.05, h / 2, h - 0.05) for q in fm.section_polys(mesh, z)])


def tower_spot(parts_on_plate, offsets):
    cx, cy = (offsets[0] + offsets[2]) / 2, (offsets[1] + offsets[3]) / 2
    grid = [(float(x), float(y)) for x in np.arange(0, fm.BED, 0.5) for y in np.arange(0, fm.BED, 0.5)]
    for t in sorted(grid, key=lambda t: math.hypot(t[0] + cx - fm.BED / 2, t[1] + cy - fm.BED / 2)):
        if check_tower(t, parts_on_plate, offsets, strict=False):
            return t
    raise AssertionError("no tower spot")


def check_tower(tower, parts_on_plate, offsets, strict=True):
    x0, y0, x1, y1 = (tower[0] + offsets[0], tower[1] + offsets[1], tower[0] + offsets[2], tower[1] + offsets[3])
    edge = min(x0, y0, fm.BED - x1, fm.BED - y1)
    part = box(x0, y0, x1, y1).distance(parts_on_plate)
    ok = edge >= fm.TOWER_EDGE_MIN and part >= fm.TOWER_DISC_MIN
    assert ok or not strict, f"tower {tower}: brim {part:.2f} mm from a part, {edge:.2f} mm from a bed edge"
    return (round(part, 2), round(edge, 2)) if ok else None


# ------------------------------------------------------------------- build
def build(tower):
    os.makedirs(BUILD, exist_ok=True)
    for f in os.listdir(BUILD):
        if os.path.isfile(f"{BUILD}/{f}"):
            os.remove(f"{BUILD}/{f}")
    proc = dict(PROCESS_CFG)
    for k, v in LOCKED.items():
        proc[k] = [v[0]] * len(proc[k]) if isinstance(v, list) else v
    for fname, data in (("machine.json", MACHINE_CFG), ("process.json", proc), ("filament.json", FILAMENT_CFG)):
        with open(f"{BUILD}/{fname}", "w") as f:
            json.dump(data, f, indent=1)
    # one assemble_index per object; each object's STLs share model coordinates, placed by the object's own POS
    objs = []
    for i, o in enumerate(OBJECTS, start=1):
        for key, _, fil in PARTS:
            objs.append({"path": f"{PROJECT}/{stl(o, key)}", "count": 1, "filaments": [fil], "assemble_index": [i],
                         "pos_x": [POS[o["tag"]][0]], "pos_y": [POS[o["tag"]][1]], "pos_z": [0]})
    spec = {"plates": [{"plate_name": PLATE, "need_arrange": False, "plate_params": {"curr_bed_type": BED_TYPE},
                        "objects": objs,
                        "assembled_params": [{"assemble_index": i, "print_params": {}} for i in range(1, len(OBJECTS) + 1)]}]}
    with open(f"{BUILD}/assemble.json", "w") as f:
        json.dump(spec, f, indent=1)
    fm.cli(["--arrange", "0", "--load-assemble-list", "assemble.json", "--load-settings", "machine.json;process.json",
            "--load-filaments", "filament.json;filament.json", "--export-3mf", "raw.3mf", "--outputdir", "."], BUILD, "assemble")

    with zipfile.ZipFile(f"{BUILD}/raw.3mf") as zin:
        cfg = json.loads(zin.read("Metadata/project_settings.config"))
        patch_config(cfg, tower)
        model = zin.read("Metadata/model_settings.config").decode()
        blocks = list(re.finditer(r'<object id="(\d+)">.*?</object>', model, re.S))
        assert len(blocks) == len(OBJECTS), len(blocks)
        out = model[:blocks[0].start()]
        for m, nxt in zip(blocks, blocks[1:] + [None]):
            block = m.group(0)
            o = next(o for o in OBJECTS if any(f'value="{stl(o, key)}"' in block for key, _, _ in PARTS))
            block = re.sub(r'(<object id="\d+">\s*<metadata key="name" value=")[^"]*"', rf'\g<1>{o["name"]}"', block, count=1)
            for key, pname, _ in PARTS:
                block, n = re.subn(rf'(<part id="\d+" subtype="normal_part"[^>]*>\s*<metadata key="name" value=")[^"]*("/>(?:(?!</part>).)*?value="{re.escape(stl(o, key))}")',
                                   rf'\g<1>{pname}\g<2>', block, flags=re.S)
                assert n == 1, (stl(o, key), n)
            out += block + (model[m.end():nxt.start()] if nxt else model[m.end():])
        model = re.sub(r'( *)<metadata key="filament_map_mode" value="[^"]*"/>',
                       lambda k: f'{k.group(1)}<metadata key="filament_map_mode" value="Manual"/>\n'
                                 f'{k.group(1)}<metadata key="filament_maps" value="{" ".join(FILAMENT_MAP)}"/>', out)
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = {"Metadata/project_settings.config": json.dumps(cfg, indent=4),
                        "Metadata/model_settings.config": model}.get(item.filename)
                zout.writestr(item, data if data is not None else zin.read(item.filename))


def patch_config(cfg, tower):
    nf, ne = len(COLOURS), len(cfg["nozzle_diameter"])
    cfg["filament_colour"] = cfg["filament_multi_colour"] = list(COLOURS)
    cfg["filament_map_mode"], cfg["filament_map"], cfg["filament_nozzle_map"] = "Manual", FILAMENT_MAP, FILAMENT_MAP
    cfg["flush_multiplier"], cfg["flush_multiplier_fast"] = ["1"] * ne, ["1.2"] * ne
    cfg["flush_volumes_matrix"] = ["0" if a == b else "280" for _ in range(ne) for a in range(nf) for b in range(nf)]
    cfg["flush_volumes_vector"] = ["140"] * (ne * nf)
    cfg["curr_bed_type"] = BED_TYPE
    for k in BED_KEYS:
        cfg[k] = [BED_TEMP] * nf
    cfg["wipe_tower_x"], cfg["wipe_tower_y"] = [f"{tower[0]:g}"], [f"{tower[1]:g}"]
    diff = cfg["different_settings_to_system"]
    assert len(diff) == nf + 2, diff
    diff[0] = ";".join(sorted(set(x for x in diff[0].split(";") if x) | set(LOCKED)))
    for i in range(1, nf + 1):
        diff[i] = ";".join(sorted(set(x for x in diff[i].split(";") if x) | set(BED_KEYS)))
    return cfg


# ------------------------------------------------------------------ checks
def check_file(path, label, tower):
    with zipfile.ZipFile(path) as z:
        cfg = json.loads(z.read("Metadata/project_settings.config"))
        ms = z.read("Metadata/model_settings.config").decode()
        m3 = z.read("3D/3dmodel.model").decode()
    assert cfg["printer_settings_id"] == MACHINE and cfg["print_settings_id"] == PROCESS, label
    assert cfg["filament_settings_id"] == [FILAMENT] * 2 and cfg["filament_type"] == ["PETG", "PETG"], label
    assert cfg["nozzle_diameter"][0] == NOZZLE and cfg["layer_height"] == PROCESS_CFG["layer_height"], (label, cfg["nozzle_diameter"], cfg["layer_height"])
    assert cfg["filament_colour"] == COLOURS, (label, cfg["filament_colour"])
    assert cfg["filament_map"] == FILAMENT_MAP and cfg["filament_map_mode"] == "Manual", label
    assert cfg["curr_bed_type"] == BED_TYPE and all(cfg[k] == [BED_TEMP] * 2 for k in BED_KEYS), label
    for k, v in LOCKED.items():
        got = cfg[k]
        assert (set(got) == {v[0]} if isinstance(v, list) else got == v), f"{label}: {k} = {got}"
    diff = cfg["different_settings_to_system"]
    assert set(LOCKED) <= set(diff[0].split(";")), f"{label}: process keys missing from the diff list"
    assert all(set(BED_KEYS) <= set(diff[i].split(";")) for i in (1, 2)), f"{label}: bed keys missing from the filament diff slots"
    assert (cfg["wipe_tower_x"], cfg["wipe_tower_y"]) == ([f"{tower[0]:g}"], [f"{tower[1]:g}"]), (label, cfg["wipe_tower_x"], cfg["wipe_tower_y"])
    ne = len(cfg["nozzle_diameter"])
    assert len(cfg["flush_volumes_matrix"]) == ne * 4 and cfg["flush_volumes_matrix"][:4] == ["0", "280", "280", "0"], label
    assert cfg["print_sequence"] == "by layer" and cfg["enable_prime_tower"] == "1", label
    # one plate, three named objects with two named parts each, no modifiers, each at its centre
    objs = re.findall(r'<object id="(\d+)">(.*?)</object>', ms, re.S)
    assert len(objs) == len(OBJECTS), (label, len(objs))
    names = {re.search(r'<metadata key="name" value="([^"]*)"', body).group(1): oid for oid, body in objs}
    assert set(names) == {o["name"] for o in OBJECTS}, (label, names)
    plates = re.findall(r"<plate>(.*?)</plate>", ms, re.S)
    assert len(plates) == 1 and f'key="plater_name" value="{PLATE}"' in plates[0], label
    assert sorted(re.findall(r'key="object_id" value="(\d+)"', plates[0])) == sorted(names.values()), label
    assert 'key="filament_map_mode" value="Manual"' in plates[0] and f'key="filament_maps" value="{" ".join(FILAMENT_MAP)}"' in plates[0], label
    assert 'key="bed_type" value="Textured PEI Plate"' in plates[0], label
    items = dict(re.findall(r'<item objectid="(\d+)"[^>]*transform="([^"]*)"', m3))
    for oid, body in objs:
        name = next(n for n in names if names[n] == oid)
        o = next(o for o in OBJECTS if o["name"] == name)
        assert "modifier_part" not in body and body.count('subtype="normal_part"') == len(PARTS), label
        parts = re.findall(r'<part id="\d+" subtype="normal_part"[^>]*>(.*?)</part>', body, re.S)
        got = [(re.search(r'key="name" value="([^"]*)"', p).group(1), re.search(r'key="extruder" value="(\d+)"', p).group(1)) for p in parts]
        assert got == [(pname, str(fil)) for _, pname, fil in PARTS], (label, o["name"], got)
        comps = re.search(rf'<object id="{oid}" [^>]*>\s*<components>(.*?)</components>', m3, re.S).group(1)
        assert len(re.findall(r"<component ", comps)) == len(PARTS), label
        tf = items[oid].split()
        anchor = ANCHOR[o["tag"]]
        opos = fm.object_pos(m3, oid, anchor)
        world = [float(tf[9 + i]) + opos[i] + anchor[i] for i in range(3)]
        assert abs(world[0] - o["center"][0]) < 0.01 and abs(world[1] - o["center"][1]) < 0.01, (label, o["name"], world)
        assert abs(world[2] - anchor[2]) < 1e-6, (label, world)
    return cfg


def tool_changes(g):
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


def norm_tools(g):
    return re.sub(r"^\s*(T\d{1,2})\b[^\n]*$", lambda m: m.group(1) if int(m.group(1)[1:]) < 16 else m.group(0), g, flags=re.M)


def inside(moves, boxes):
    """Which moves have both ends inside any of the XY bounds in boxes."""
    def ok(m):
        return any(x0 <= m[3] <= x1 and y0 <= m[4] <= y1 and x0 <= m[5] <= x1 and y0 <= m[6] <= y1 for x0, y0, x1, y1 in boxes)
    return [m for m in moves if ok(m)]


def verify(tower):
    report = {"authored": bool(check_file(OUT, "authored", tower))}
    fm.cli(["--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", OUT], BUILD, "round trip")
    report["round_trip"] = bool(check_file(f"{BUILD}/roundtrip.3mf", "round trip", tower))
    for attempt in range(3):
        A = graft_slice(OUT, f"{BUILD}/sliced.3mf", plate=1)
        if A["rc"] == 0 and A["gcode"]:
            break
        print(f"  slice attempt {attempt + 1} failed rc {A['rc']} ({A['log']})")
    assert A["rc"] == 0 and A["gcode"], (A["rc"], A["log"])
    with zipfile.ZipFile(A["out"]) as z:
        g = z.read(A["gcode"]).decode(errors="ignore")
        info = z.read("Metadata/slice_info.config").decode()
    hdr = gf.header(g)
    used = {int(i): float(v) for i, v in re.findall(r'<filament id="(\d+)"[^>]*?used_g="([^"]*)"', info)}
    pred = int(re.search(r'key="prediction" value="(\d+)"', info).group(1))
    assert "X2D start gcode" in g, "machine include templates did not merge"
    assert re.search(r"^; filament_map = 1,1$", g, re.M)
    assert re.search(rf"^\s*M1[49]0 S{BED_TEMP}\b", g, re.M), "bed temperature"
    assert re.search(rf"^\s*M10[49] S{NOZZLE_TEMP}\b", g, re.M), "nozzle temperature (PETG Basic 250)"
    assert re.search(r"^; print_sequence = by layer$", g, re.M)
    assert re.search(r"^; wall_generator = arachne$", g, re.M) and re.search(r"^; sparse_infill_density = 100%$", g, re.M)
    assert re.search(r"^; skirt_loops = 2$", g, re.M) and re.search(r"^; brim_type = no_brim$", g, re.M)
    h, first = float(PROCESS_CFG["layer_height"]), float(PROCESS_CFG["initial_layer_print_height"])
    moves = gf.parse_moves(norm_tools(g))
    zs = sorted({m[0] for m in moves if m[0] > 0})
    layer_of = {z: i + 1 for i, z in enumerate(zs)}
    assert hdr["layers"] == len(zs) == A["layers"], (hdr["layers"], len(zs), A["layers"])
    backer_top = max(BOUNDS[(o["tag"], "backer")][1][2] for o in OBJECTS)
    ink_top = max(BOUNDS[(o["tag"], "ink")][1][2] for o in OBJECTS)
    assert all(abs(BOUNDS[(o["tag"], "backer")][1][2] - backer_top) < 1e-6 and abs(BOUNDS[(o["tag"], "ink")][1][2] - ink_top) < 1e-6
               for o in OBJECTS), "the samples' tiers differ"
    grid = lambda top: 1 + round((top - first) / h)
    on_grid = {k: bool(abs(first + (grid(v) - 1) * h - v) < 1e-3) for k, v in (("backer", backer_top), ("ink", ink_top))}
    assert all(on_grid.values()), f"tier tops off the {first} + n x {h} layer grid: {on_grid}"
    assert abs(zs[0] - first) < 1e-6 and all(abs(b - a - h) < 1e-6 for a, b in zip(zs, zs[1:])), "layer heights"
    assert len(zs) == grid(ink_top), (len(zs), grid(ink_top))
    feats = {m[1] for m in moves}
    assert "Skirt" in feats and "Brim" not in feats and "Prime tower" in feats, feats
    xy = [min(min(m[3], m[5]) for m in moves), min(min(m[4], m[6]) for m in moves),
          max(max(m[3], m[5]) for m in moves), max(max(m[4], m[6]) for m in moves)]
    assert xy[0] >= 0 and xy[1] >= 0 and xy[2] <= fm.BED and xy[3] <= fm.BED, ("toolpaths leave the bed", xy)
    t1 = [m for m in moves if m[1] == "Prime tower" and m[0] == zs[0]]
    assert t1, "no prime tower on layer 1"
    bx = (min(min(m[3], m[5]) for m in t1) - tower[0], min(min(m[4], m[6]) for m in t1) - tower[1],
          max(max(m[3], m[5]) for m in t1) - tower[0], max(max(m[4], m[6]) for m in t1) - tower[1])
    measured = tuple(round(v, 2) for v in bx)
    backer_layers = [z for z in zs if z <= backer_top + h / 2]
    ink_layers = [z for z in zs if z > backer_top + h / 2]
    assert ink_layers and abs(zs[-1] - ink_top) < h / 2 + 1e-6, (zs[-1], ink_top)
    assert len(backer_layers) == grid(backer_top), (len(backer_layers), grid(backer_top))
    part = [m for m in moves if m[1] not in NOT_PART and m[0] > 0]
    def pads(key):
        return [(BOUNDS[(o["tag"], key)][0][0] + POS[o["tag"]][0] - FOOT_PAD, BOUNDS[(o["tag"], key)][0][1] + POS[o["tag"]][1] - FOOT_PAD,
                 BOUNDS[(o["tag"], key)][1][0] + POS[o["tag"]][0] + FOOT_PAD, BOUNDS[(o["tag"], key)][1][1] + POS[o["tag"]][1] + FOOT_PAD)
                for o in OBJECTS]
    black_low = [m for m in part if m[2] == 1 and m[0] in backer_layers]
    black_ink = [m for m in part if m[2] == 1 and m[0] in ink_layers]
    white_high = [m for m in part if m[2] == 0 and m[0] in ink_layers]
    white_low = [m for m in part if m[2] == 0 and m[0] in backer_layers]
    assert not black_low, f"black extrusion in the backer layers: {len(black_low)} moves"
    assert black_ink and len(inside(black_ink, pads("ink"))) == len(black_ink), \
        f"black outside the ink footprints above the backer: {len(black_ink) - len(inside(black_ink, pads('ink')))} moves"
    assert not white_high, f"white extrusion above the backer: {len(white_high)} moves"
    assert white_low and all(z in {m[0] for m in white_low} for z in backer_layers), "a backer layer without white"
    assert all(z in {m[0] for m in black_ink} for z in ink_layers), "an ink layer without black"
    # every sample gets ink on every ink layer (the 2.5 in eyes are the thinnest strokes in the file)
    per_sample = {o["name"]: len(inside(black_ink, pads("ink")[i:i + 1])) for i, o in enumerate(OBJECTS)}
    for i, o in enumerate(OBJECTS):
        zs_here = {m[0] for m in inside(black_ink, pads("ink")[i:i + 1])}
        assert zs_here == set(ink_layers), f"{o['name']}: ink layers missing black: {sorted(set(ink_layers) - zs_here)}"
    # and every single stroke (hair, face outline, two eyes, nose, mouth) of every sample: the thinnest ones are the
    # 2.5 in eyes at about 0.75 mm, under two 0.42 beads, so arachne must still lay something there on every layer
    thin = {}
    for o in OBJECTS:
        pieces = MESHES[(o["tag"], "ink")].split(only_watertight=True)
        assert len(pieces) == 6, (o["name"], len(pieces))
        for p in pieces:
            b = (p.bounds[0][0] + POS[o["tag"]][0] - FOOT_PAD, p.bounds[0][1] + POS[o["tag"]][1] - FOOT_PAD,
                 p.bounds[1][0] + POS[o["tag"]][0] + FOOT_PAD, p.bounds[1][1] + POS[o["tag"]][1] + FOOT_PAD)
            here = inside(black_ink, [b])
            missing = sorted(set(ink_layers) - {m[0] for m in here})
            assert not missing, f"{o['name']}: a stroke of {p.area / 2:.0f} mm2 gets no black on layers {missing}"
            thin.setdefault(o["name"], []).append(len(here))
    per_sample = {k: {"moves": per_sample[k], "moves_per_stroke": sorted(v)} for k, v in thin.items()}
    start, changes, flush = tool_changes(g)
    minutes = pred / 60
    per_feature = gf.feature_split(moves, hdr)[0]
    report.update({
        "rc": A["rc"], "layers": A["layers"], "layer_height": h, "first_layer_height": first, "tiers_on_grid": on_grid,
        "time": {"estimate": A["time"], "prediction_s": pred, "minutes": round(minutes, 1),
                 "h_m": f"{int(minutes // 60)} h {int(round(minutes % 60))} min"},
        "grams": {"white (1)": used.get(1), "black (2)": used.get(2), "total": round(sum(used.values()), 2),
                  "header_weights": hdr["weights"]},
        "grams_by_feature": {k: round(v, 2) for k, v in sorted(per_feature.items(), key=lambda kv: -kv[1]) if v >= 0.005},
        "tool_changes": {"start": start, "count": len(changes), "flushes": len(flush),
                         "changes": [{"layer": layer_of.get(z), "z": z, "to": t} for z, t in changes]},
        "tiers": {"backer_layers": [layer_of[zs[0]], layer_of[backer_layers[-1]]],
                  "ink_layers": [layer_of[ink_layers[0]], layer_of[ink_layers[-1]]],
                  "tops_mm": {"backer": round(backer_top, 3), "ink": round(ink_top, 3)}},
        "gcode_proofs": {"black_ink_moves": len(black_ink), "black_ink_moves_per_sample": per_sample,
                         "black_in_backer_layers": len(black_low), "white_above_backer": len(white_high)},
        "tower": {"wipe_tower_xy": list(tower), "brim_offsets_measured": measured, "brim_offsets_used": list(BRIM_OFFSETS),
                  "clearance": check_tower(tower, FOOT_PLATE, measured, strict=False)},
        "bed_xy": [round(v, 1) for v in xy],
    })
    return report, measured


PROCESS_CFG = flatten("process", PROCESS)
MACHINE_CFG = flatten("machine", MACHINE)
FILAMENT_CFG = flatten("filament", FILAMENT)
BED_TEMP = FILAMENT_CFG["textured_plate_temp"][0]
NOZZLE_TEMP = FILAMENT_CFG["nozzle_temperature"][0]
assert MACHINE in FILAMENT_CFG.get("compatible_printers", [MACHINE]) and MACHINE in PROCESS_CFG.get("compatible_printers", [MACHINE]), \
    (FILAMENT, PROCESS, "not for", MACHINE)
assert (BED_TEMP, NOZZLE_TEMP) == ("70", "250") and FILAMENT_CFG["filament_type"][0] == "PETG", (BED_TEMP, NOZZLE_TEMP)
assert MACHINE_CFG["nozzle_diameter"][0] == NOZZLE, MACHINE_CFG["nozzle_diameter"]
MESHES = {(o["tag"], key): trimesh.load(f"{PROJECT}/{stl(o, key)}") for o in OBJECTS for key, _, _ in PARTS}
BOUNDS = {k: m.bounds for k, m in MESHES.items()}
assert all(m.is_watertight for m in MESHES.values())
ANCHOR = {o["tag"]: MESHES[(o["tag"], "backer")].bounds.mean(axis=0) for o in OBJECTS}
POS = {o["tag"]: (o["center"][0] - float(ANCHOR[o["tag"]][0]), o["center"][1] - float(ANCHOR[o["tag"]][1])) for o in OBJECTS}
FEET = {o["tag"]: translate(footprint(MESHES[(o["tag"], "backer")]), *POS[o["tag"]]) for o in OBJECTS}
FOOT_PLATE = unary_union(list(FEET.values()))
for a in OBJECTS:                      # samples apart and on the bed with room for their skirts
    fa = FEET[a["tag"]]
    x0, y0, x1, y1 = fa.bounds
    assert min(x0, y0, fm.BED - x1, fm.BED - y1) >= 8, (a["name"], fa.bounds)
    for b in OBJECTS:
        if a is not b:
            assert fa.distance(FEET[b["tag"]]) >= PART_GAP_MIN, (a["name"], b["name"], fa.distance(FEET[b["tag"]]))


def main():
    offsets = BRIM_OFFSETS
    for attempt in (1, 2):
        tower = tower_spot(FOOT_PLATE, offsets)
        print(f"tower {tower}, clearance {check_tower(tower, FOOT_PLATE, offsets)} (brim offsets {offsets})")
        build(tower)
        report, measured = verify(tower)
        drift = max(abs(a - b) for a, b in zip(measured, offsets))
        if drift <= BRIM_TOL and check_tower(tower, FOOT_PLATE, measured, strict=False):
            break
        print(f"  tower brim measured {measured}, off by {drift:.2f} mm: rebuilding with the measured offsets")
        offsets = measured
    else:
        raise AssertionError(f"tower brim offsets still drifting: {measured}")
    report["tower"]["clearance"] = check_tower(tower, FOOT_PLATE, measured)
    report.update({"file": OUT, "nozzle": NOZZLE, "presets": {"machine": MACHINE, "process": PROCESS, "filament": FILAMENT,
                                                             "colours": COLOURS, "bed": BED_TYPE, "bed_temp": BED_TEMP},
                   "plate": PLATE, "objects": [{"name": o["name"], "center": list(o["center"]),
                                                "parts": [{"stl": stl(o, k), "name": n, "filament": f} for k, n, f in PARTS]} for o in OBJECTS],
                   "locked_process_keys": LOCKED})
    with open(OUT.replace(".3mf", "-slice.json"), "w") as f:
        json.dump(report, f, indent=1)
    t, gr, tc = report["time"], report["grams"], report["tool_changes"]
    print(f"{OUT}\n  {t['h_m']} ({t['minutes']} min); {report['layers']} layers ({report['first_layer_height']} + {report['layer_height']}); "
          f"white {gr['white (1)']} g + black {gr['black (2)']} g = {gr['total']} g\n"
          f"  filament changes {tc['count']} (start {tc['start']}): " + ", ".join(f"L{c['layer']}->{c['to']}" for c in tc["changes"])
          + f"\n  tower at {tower}, brim {report['tower']['brim_offsets_measured']}, clearance {report['tower']['clearance']}; "
          f"backer L1-{report['tiers']['backer_layers'][1]}, ink L{report['tiers']['ink_layers'][0]}-{report['tiers']['ink_layers'][1]}; "
          f"ink moves per sample {report['gcode_proofs']['black_ink_moves_per_sample']}")


if __name__ == "__main__":
    main()
