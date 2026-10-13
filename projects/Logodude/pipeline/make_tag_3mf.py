"""Bambu Studio project 3MF for the Logo Dude LUGGAGE TAG (2026-10-13): logodude-tag.3mf, one plate, one object.

A second file next to logodude.3mf on purpose (Brian 2026-10-13: "Create a new 3MF file, preserving the work we have
already done"); the badge file and its pipeline are not touched.

  object "Logo Dude luggage tag", three parts in shared model coordinates (logodude_tag.py):
    backer (white, filament 1, z 0..3.08, the text volumes cut out of its bottom)
    ink (black, filament 2, z 3.08..4.04, the six raised strokes)
    back text (black, filament 2, z 0..0.52, 49 letters inlaid flush in the bottom face)
  Tiers sit on the 0.16 mm grid (0.2 first layer): text = layers 1-3, backer = 1-19, ink = 20-25.

Two nozzle modes, chosen with NOZZLE (default 0.4), sharing every step; each mode has its own STLs, presets, output,
build directory and measured tower-brim constant:
  0.4 (Brian 2026-10-13: "I can go with .4mm, but I need the print to take less than 1.25hrs"): 3 in tag,
      logodude-tag-*.stl, 0.16mm Standard (0.2 first layer): text layers 1-3, backer to 19, ink 20-25 -> logodude-tag.3mf
  0.6 (Brian 2026-10-13, after printing the 0.4 file through the 0.6 nozzle by mistake: a real 0.6 version): 3.5 in tag,
      logodude-tag-06-*.stl, 0.18mm Balanced Quality (0.3 first layer): text 1-3, backer to 16, ink 17-21 -> logodude-tag-06.3mf
PETG Basic white + black, textured PEI 70 C, nozzle 250 C (read from the filament preset). No modifier parts and no
lettering object key: at these sizes every stroke (face lines and letters) is two arachne beads of the nozzle's line,
the clean regime, so the process keys are the proven Sharks/Logodude SMOOTH_TOP set minus the fill-core lettering keys,
plus arachne, a 2-loop skirt (Brian's rule), no brim, a solid tag (100% zig-zag, the eyelet gets yanked) and
elefant_foot_compensation 0 so the flush bottom inlay keeps its first-layer outlines. Prime tower at the free spot
closest to the bed centre (brim >= 12 mm from the part, >= 15 mm from the bed edges); its brim offsets are re-measured
from the file's own slice (one rebuild pass if they moved).

Verification, all offline: authored-file checks, a CLI round trip, then a real CLI slice (graft_slice): rc 0, layer count,
estimated time under TIME_CAP_MIN (hard assert), grams, filament changes by layer, and G-code proofs that black extrusion
in the text layers stays inside the text footprint, black above the backer stays inside the ink footprint, no black in
the backer-only layers and no white above the backer. Writes logodude-tag.3mf and logodude-tag-slice.json.

Usage: .venv/bin/python projects/Logodude/pipeline/make_tag_3mf.py                 (0.4 nozzle: logodude-tag.3mf)
       NOZZLE=0.6 .venv/bin/python projects/Logodude/pipeline/make_tag_3mf.py      (0.6 nozzle: logodude-tag-06.3mf)
       PROCESS="0.20mm Standard @BBL X2D" .venv/bin/python .../make_tag_3mf.py     (time check only, writes <build>/alt.3mf)
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
NOZZLE = os.environ.get("NOZZLE", "0.4")
# Per-nozzle mode: presets (the unsuffixed X2D process names are the 0.4 ones; the unsuffixed PETG preset is the one
# compatible with the 0.6 machine), STL name pattern, output, build dir, and the layer-1 prime tower brim relative to
# wipe_tower_x/y (x0, y0, x1, y1) measured on that mode's own slice (main() re-measures and rebuilds once if it moved).
MODES = {
    "0.4": {"machine": "Bambu Lab X2D 0.4 nozzle", "process": "0.16mm Standard @BBL X2D",
            "filament": "Bambu PETG Basic @BBL X2D 0.4 nozzle", "stl": "logodude-tag-{}.stl",
            "out": "logodude-tag.3mf", "build": "build-tag",
            "brim": (-3.87, -5.0, 30.84, 29.22)},    # measured 2026-10-13 at 0.16 Standard (34.7 x 34.2 mm)
    "0.6": {"machine": "Bambu Lab X2D 0.6 nozzle", "process": "0.18mm Balanced Quality @BBL X2D 0.6 nozzle",
            "filament": "Bambu PETG Basic @BBL X2D", "stl": "logodude-tag-06-{}.stl",
            "out": "logodude-tag-06.3mf", "build": "build-tag-06",
            "brim": (-3.85, -4.79, 30.97, 28.78)},   # measured 2026-10-13 at 0.18 Balanced Quality (34.8 x 33.6 mm)
}
MODE = MODES[NOZZLE]
MACHINE = MODE["machine"]
DEFAULT_PROCESS = MODE["process"]
PROCESS = os.environ.get("PROCESS", DEFAULT_PROCESS)
ALT = PROCESS != DEFAULT_PROCESS                  # a time check with another process: never the deliverable
FILAMENT = MODE["filament"]
BUILD = f"{PIPE}/{MODE['build']}"
COLOURS = ["#FFFFFF", "#000000"]                  # filament n = position in this list
OBJECT = "Logo Dude luggage tag"
PLATE = "Tag"
PARTS = [{"stl": MODE["stl"].format("backer"), "name": "backer (white)", "filament": 1},     # the anchor
         {"stl": MODE["stl"].format("ink"), "name": "ink (black)", "filament": 2},
         {"stl": MODE["stl"].format("text"), "name": "back text (black)", "filament": 2}]
CENTER = (128.0, 128.0)
OUT = f"{BUILD}/alt.3mf" if ALT else f"{PROJECT}/{MODE['out']}"
TIME_CAP_MIN = 75                                 # Brian 2026-10-13: "less than 1.25hrs"
BED_TYPE = "Textured PEI Plate"
BED_KEYS = ("textured_plate_temp", "textured_plate_temp_initial_layer")
FILAMENT_MAP = ["1", "1"]                         # both filaments on extruder 1
# Process keys locked in the file (every one listed in different_settings_to_system[0], or Studio resets it).
# From the Sharks/Logodude SMOOTH_TOP set: what still applies to a part with no fill-core modifier.
LOCKED = {
    "ironing_type": "no ironing",                 # PETG pits and smears under ironing
    "seam_gap": "0%",                             # loop start/stop marks on small loops (letters, eyes)
    "small_perimeter_speed": ["30"], "small_perimeter_threshold": ["10"], "gap_infill_speed": ["40"],
    "wall_distribution_count": "3", "wall_transition_filter_deviation": "50%",
    "min_feature_size": "10%", "min_bead_width": "50%",   # arachne places beads down to half a line
    "wall_generator": "arachne",                  # 0.9 to 1.1 mm strokes = two variable beads; classic drops them
    "prime_tower_brim_width": "5", "prime_tower_rib_wall": "1", "prime_tower_fillet_wall": "1",
    "top_shell_layers": "5", "top_surface_speed": ["60"],
    "skirt_loops": "2", "skirt_distance": "3", "skirt_height": "1",   # Brian's standing rule (feedback-keep-skirt)
    "initial_layer_speed": ["30"], "initial_layer_infill_speed": ["50"],   # small black first-layer islands bond
    # tag-specific
    "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag",   # solid; gyroid/grid refuse 100%
    "brim_type": "no_brim",
    "elefant_foot_compensation": "0",             # keeps the first-layer letter/white outlines where the CAD put them
}
BRIM_OFFSETS = MODE["brim"]
BRIM_TOL = 0.5
NOT_PART = ("Prime tower", "Wipe tower", "Skirt", "Brim", "Flush + retract net", "Start purge", "Custom", "Support",
            "Support interface", "Support transition")
FOOT_PAD = 1.0                                    # mm, allowance around a part's XY bounds for its extrusion


def load(kind, name):
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
    """inherits chain plus include templates (as projects/Logodude/pipeline/make_print_3mf.py)."""
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


# ------------------------------------------------------------------ geometry (from the STLs, whatever they are)
def footprint(mesh):
    """Plan outline of a part standing on z = 0: union of its sections near the bottom, middle and top."""
    h = mesh.bounds[1][2]
    return unary_union([q for z in (0.05, h / 2, h - 0.05) for q in fm.section_polys(mesh, z)])


def tower_spot(part_on_plate, offsets):
    """wipe_tower_x/y of the free spot closest to the bed centre: brim >= fm.TOWER_DISC_MIN from the part,
    >= fm.TOWER_EDGE_MIN from the edges (never the raw back-left corner: the edge rule keeps it off every corner)."""
    cx, cy = (offsets[0] + offsets[2]) / 2, (offsets[1] + offsets[3]) / 2
    grid = [(float(x), float(y)) for x in np.arange(0, fm.BED, 0.5) for y in np.arange(0, fm.BED, 0.5)]
    for t in sorted(grid, key=lambda t: math.hypot(t[0] + cx - CENTER[0], t[1] + cy - CENTER[1])):
        if check_tower(t, part_on_plate, offsets, strict=False):
            return t
    raise AssertionError("no tower spot")


def check_tower(tower, part_on_plate, offsets, strict=True):
    x0, y0, x1, y1 = (tower[0] + offsets[0], tower[1] + offsets[1], tower[0] + offsets[2], tower[1] + offsets[3])
    edge = min(x0, y0, fm.BED - x1, fm.BED - y1)
    part = box(x0, y0, x1, y1).distance(part_on_plate)
    ok = edge >= fm.TOWER_EDGE_MIN and part >= fm.TOWER_DISC_MIN
    assert ok or not strict, f"tower {tower}: brim {part:.2f} mm from the part, {edge:.2f} mm from a bed edge"
    return (round(part, 2), round(edge, 2)) if ok else None


# ------------------------------------------------------------------- build
def build(tower):
    os.makedirs(BUILD, exist_ok=True)
    for f in os.listdir(BUILD):
        if os.path.isfile(f"{BUILD}/{f}"):
            os.remove(f"{BUILD}/{f}")
    proc = dict(PROCESS_CFG)
    for k, v in LOCKED.items():   # list keys: one value per extruder variant, as many as the preset has
        proc[k] = [v[0]] * len(proc[k]) if isinstance(v, list) else v
    for fname, data in (("machine.json", MACHINE_CFG), ("process.json", proc), ("filament.json", FILAMENT_CFG)):
        with open(f"{BUILD}/{fname}", "w") as f:
            json.dump(data, f, indent=1)
    # pos_x/pos_y place the STLs' shared origin so the anchor's bbox centre lands on CENTER; one assemble_index = one object
    spec = {"plates": [{"plate_name": PLATE, "need_arrange": False, "plate_params": {"curr_bed_type": BED_TYPE},
                        "objects": [{"path": f"{PROJECT}/{q['stl']}", "count": 1, "filaments": [q["filament"]],
                                     "assemble_index": [1], "pos_x": [POS[0]], "pos_y": [POS[1]], "pos_z": [0]} for q in PARTS],
                        "assembled_params": [{"assemble_index": 1, "print_params": {}}]}]}
    with open(f"{BUILD}/assemble.json", "w") as f:
        json.dump(spec, f, indent=1)
    fm.cli(["--arrange", "0", "--load-assemble-list", "assemble.json", "--load-settings", "machine.json;process.json",
            "--load-filaments", "filament.json;filament.json", "--export-3mf", "raw.3mf", "--outputdir", "."], BUILD, "assemble")

    with zipfile.ZipFile(f"{BUILD}/raw.3mf") as zin:
        cfg = json.loads(zin.read("Metadata/project_settings.config"))
        patch_config(cfg, tower)
        model = zin.read("Metadata/model_settings.config").decode()
        blocks = list(re.finditer(r'<object id="(\d+)">.*?</object>', model, re.S))
        assert len(blocks) == 1, len(blocks)
        m = blocks[0]
        block = re.sub(r'(<object id="\d+">\s*<metadata key="name" value=")[^"]*"', rf'\g<1>{OBJECT}"', m.group(0), count=1)
        for q in PARTS:   # each part is named after its STL by the CLI
            block, n = re.subn(rf'(<part id="\d+" subtype="normal_part"[^>]*>\s*<metadata key="name" value=")[^"]*("/>(?:(?!</part>).)*?value="{re.escape(q["stl"])}")',
                               rf'\g<1>{q["name"]}\g<2>', block, flags=re.S)
            assert n == 1, (q["stl"], n)
        model = model[:m.start()] + block + model[m.end():]
        model = re.sub(r'( *)<metadata key="filament_map_mode" value="[^"]*"/>',
                       lambda k: f'{k.group(1)}<metadata key="filament_map_mode" value="Manual"/>\n'
                                 f'{k.group(1)}<metadata key="filament_maps" value="{" ".join(FILAMENT_MAP)}"/>', model)
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = {"Metadata/project_settings.config": json.dumps(cfg, indent=4),
                        "Metadata/model_settings.config": model}.get(item.filename)
                zout.writestr(item, data if data is not None else zin.read(item.filename))


def patch_config(cfg, tower):
    """The CLI export's fixes (reference-two-material-two-plate-3mf): colours, Manual map, the flush block
    (extruders x filaments^2, 280 placeholders), bed temps, the tower, and every changed key in different_settings_to_system."""
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
    assert len(diff) == nf + 2, diff    # [process, filament 1..n, machine]
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
    # one plate, one object, three named parts with their filaments, no modifiers, placed at CENTER
    objs = re.findall(r'<object id="(\d+)">(.*?)</object>', ms, re.S)
    assert len(objs) == 1, (label, len(objs))
    oid, body = objs[0]
    assert re.search(r'<metadata key="name" value="([^"]*)"', body).group(1) == OBJECT, label
    plates = re.findall(r"<plate>(.*?)</plate>", ms, re.S)
    assert len(plates) == 1 and f'key="plater_name" value="{PLATE}"' in plates[0], label
    assert re.findall(r'key="object_id" value="(\d+)"', plates[0]) == [oid], label
    assert 'key="filament_map_mode" value="Manual"' in plates[0] and f'key="filament_maps" value="{" ".join(FILAMENT_MAP)}"' in plates[0], label
    assert 'key="bed_type" value="Textured PEI Plate"' in plates[0], label
    assert "modifier_part" not in body and body.count('subtype="normal_part"') == len(PARTS), label
    parts = re.findall(r'<part id="\d+" subtype="normal_part"[^>]*>(.*?)</part>', body, re.S)
    got = [(re.search(r'key="name" value="([^"]*)"', p).group(1), re.search(r'key="extruder" value="(\d+)"', p).group(1)) for p in parts]
    assert got == [(q["name"], str(q["filament"])) for q in PARTS], (label, got)
    comps = re.search(rf'<object id="{oid}" [^>]*>\s*<components>(.*?)</components>', m3, re.S).group(1)
    assert len(re.findall(r"<component ", comps)) == len(PARTS), label
    tf = dict(re.findall(r'<item objectid="(\d+)"[^>]*transform="([^"]*)"', m3))[oid].split()
    opos = fm.object_pos(m3, oid, ANCHOR_CENTER)
    world = [float(tf[9 + i]) + opos[i] + ANCHOR_CENTER[i] for i in range(3)]
    assert abs(world[0] - CENTER[0]) < 0.01 and abs(world[1] - CENTER[1]) < 0.01, (label, world)
    assert abs(world[2] - ANCHOR_CENTER[2]) < 1e-6, (label, world)
    return cfg


def tool_changes(g):
    """(start tool, [(z, tool)] for every filament change after the start G-code, flush lengths)."""
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
    """Every tool select as a bare "T1" line (the X2D writes "  T1 H-1" in the start block and "T1 H-1" in the layers),
    which gf.parse_moves tracks; the T65279-style unload codes are left alone."""
    return re.sub(r"^\s*(T\d{1,2})\b[^\n]*$", lambda m: m.group(1) if int(m.group(1)[1:]) < 16 else m.group(0), g, flags=re.M)


def inside(moves, b):
    """Which moves have both ends inside XY bounds b = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = b
    return [m for m in moves if x0 <= m[3] <= x1 and y0 <= m[4] <= y1 and x0 <= m[5] <= x1 and y0 <= m[6] <= y1]


def verify(tower):
    """Round trip, slice, and the G-code proofs. Returns the report (and the measured brim offsets)."""
    report = {"authored": bool(check_file(OUT, "authored", tower))}
    fm.cli(["--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", OUT], BUILD, "round trip")
    report["round_trip"] = bool(check_file(f"{BUILD}/roundtrip.3mf", "round trip", tower))
    for attempt in range(3):   # the CLI occasionally dies (rc -11) in its thumbnail stage after a good slice; retry
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
    # the layer grid from the preset: layer n tops out at first + (n - 1) h; tier tops from the meshes
    text_top, backer_top, ink_top = (BOUNDS[k][1][2] for k in ("text", "backer", "ink"))
    grid = lambda top: 1 + round((top - first) / h)                     # the layer whose top is nearest this height
    on_grid = {k: bool(abs(first + (grid(v) - 1) * h - v) < 1e-3) for k, v in (("text", text_top), ("backer", backer_top), ("ink", ink_top))}
    assert ALT or all(on_grid.values()), f"tier tops off the {first} + n x {h} layer grid: {on_grid}"
    assert abs(zs[0] - first) < 1e-6 and all(abs(b - a - h) < 1e-6 for a, b in zip(zs, zs[1:])), "layer heights"
    assert len(zs) == grid(ink_top), (len(zs), grid(ink_top))
    feats = {m[1] for m in moves}
    assert "Skirt" in feats and "Brim" not in feats and "Prime tower" in feats, feats
    # toolpaths stay on the bed
    xy = [min(min(m[3], m[5]) for m in moves), min(min(m[4], m[6]) for m in moves),
          max(max(m[3], m[5]) for m in moves), max(max(m[4], m[6]) for m in moves)]
    assert xy[0] >= 0 and xy[1] >= 0 and xy[2] <= fm.BED and xy[3] <= fm.BED, ("toolpaths leave the bed", xy)
    # the prime tower's layer-1 brim, measured, relative to wipe_tower_x/y
    t1 = [m for m in moves if m[1] == "Prime tower" and m[0] == zs[0]]
    assert t1, "no prime tower on layer 1"
    bx = (min(min(m[3], m[5]) for m in t1) - tower[0], min(min(m[4], m[6]) for m in t1) - tower[1],
          max(max(m[3], m[5]) for m in t1) - tower[0], max(max(m[4], m[6]) for m in t1) - tower[1])
    measured = tuple(round(v, 2) for v in bx)
    # tiers: a layer belongs to a tier when its top z is at or under the tier top (half a layer of slack)
    text_layers = [z for z in zs if z <= text_top + h / 2]
    backer_layers = [z for z in zs if z <= backer_top + h / 2]
    ink_layers = [z for z in zs if z > backer_top + h / 2]
    assert ink_layers and abs(zs[-1] - ink_top) < h / 2 + 1e-6, (zs[-1], ink_top)
    assert (len(text_layers), len(backer_layers)) == (grid(text_top), grid(backer_top)), \
        (len(text_layers), len(backer_layers), grid(text_top), grid(backer_top))
    part = [m for m in moves if m[1] not in NOT_PART and m[0] > 0]
    pad = lambda k: (BOUNDS[k][0][0] + POS[0] - FOOT_PAD, BOUNDS[k][0][1] + POS[1] - FOOT_PAD,
                     BOUNDS[k][1][0] + POS[0] + FOOT_PAD, BOUNDS[k][1][1] + POS[1] + FOOT_PAD)
    black_text = [m for m in part if m[2] == 1 and m[0] in text_layers]
    black_mid = [m for m in part if m[2] == 1 and m[0] in backer_layers and m[0] not in text_layers]
    black_ink = [m for m in part if m[2] == 1 and m[0] in ink_layers]
    white_high = [m for m in part if m[2] == 0 and m[0] in ink_layers]
    white_low = [m for m in part if m[2] == 0 and m[0] in backer_layers]
    assert black_text and len(inside(black_text, pad("text"))) == len(black_text), \
        f"black outside the text footprint in the text layers: {len(black_text) - len(inside(black_text, pad('text')))} moves"
    assert not black_mid, f"black extrusion in the backer-only layers: {len(black_mid)} moves"
    assert black_ink and len(inside(black_ink, pad("ink"))) == len(black_ink), \
        f"black outside the ink footprint above the backer: {len(black_ink) - len(inside(black_ink, pad('ink')))} moves"
    assert not white_high, f"white extrusion above the backer: {len(white_high)} moves"
    assert white_low and all(z in {m[0] for m in white_low} for z in backer_layers), "a backer layer without white"
    assert all(z in {m[0] for m in black_text} for z in text_layers), "a text layer without black"
    assert all(z in {m[0] for m in black_ink} for z in ink_layers), "an ink layer without black"
    first_text = len(inside([m for m in black_text if m[0] == zs[0]], pad("text")))
    assert first_text > 200, first_text
    start, changes, flush = tool_changes(g)
    minutes = pred / 60
    per_feature = gf.feature_split(moves, hdr)[0]
    report.update({
        "rc": A["rc"], "layers": A["layers"], "layer_height": h, "first_layer_height": first, "tiers_on_grid": on_grid,
        "time": {"estimate": A["time"], "prediction_s": pred, "minutes": round(minutes, 1),
                 "h_m": f"{int(minutes // 60)} h {int(round(minutes % 60))} min", "cap_min": TIME_CAP_MIN,
                 "under_cap": minutes < TIME_CAP_MIN},
        "grams": {"white (1)": used.get(1), "black (2)": used.get(2), "total": round(sum(used.values()), 2),
                  "header_weights": hdr["weights"]},
        "grams_by_feature": {k: round(v, 2) for k, v in sorted(per_feature.items(), key=lambda kv: -kv[1]) if v >= 0.005},
        "tool_changes": {"start": start, "count": len(changes), "flushes": len(flush),
                         "changes": [{"layer": layer_of.get(z), "z": z, "to": t} for z, t in changes]},
        "tiers": {"text_layers": [layer_of[z] for z in text_layers], "backer_layers": [layer_of[zs[0]], layer_of[backer_layers[-1]]],
                  "ink_layers": [layer_of[ink_layers[0]], layer_of[ink_layers[-1]]],
                  "tops_mm": {"text": round(text_top, 3), "backer": round(backer_top, 3), "ink": round(ink_top, 3)}},
        "gcode_proofs": {"black_text_moves": len(black_text), "black_ink_moves": len(black_ink),
                         "first_layer_black_moves_in_text": first_text, "black_in_backer_only_layers": len(black_mid),
                         "white_above_backer": len(white_high)},
        "tower": {"wipe_tower_xy": list(tower), "brim_offsets_measured": measured, "brim_offsets_used": list(BRIM_OFFSETS),
                  "clearance": check_tower(tower, FOOT_PLATE, measured, strict=False)},   # main() re-places the tower if the measured brim moved
        "bed_xy": [round(v, 1) for v in xy],
    })
    assert minutes < TIME_CAP_MIN, f"{minutes:.1f} min is over Brian's {TIME_CAP_MIN} min cap"
    return report, measured


PROCESS_CFG = flatten("process", PROCESS)
MACHINE_CFG = flatten("machine", MACHINE)
FILAMENT_CFG = flatten("filament", FILAMENT)
BED_TEMP = FILAMENT_CFG["textured_plate_temp"][0]           # PETG Basic on textured PEI: 70
NOZZLE_TEMP = FILAMENT_CFG["nozzle_temperature"][0]         # PETG Basic: 250
assert MACHINE in FILAMENT_CFG.get("compatible_printers", [MACHINE]) and MACHINE in PROCESS_CFG.get("compatible_printers", [MACHINE]), \
    (FILAMENT, PROCESS, "not for", MACHINE)
assert (BED_TEMP, NOZZLE_TEMP) == ("70", "250") and FILAMENT_CFG["filament_type"][0] == "PETG", (BED_TEMP, NOZZLE_TEMP)
assert MACHINE_CFG["nozzle_diameter"][0] == NOZZLE, MACHINE_CFG["nozzle_diameter"]
MESHES = {k: trimesh.load(f"{PROJECT}/{q['stl']}") for k, q in zip(("backer", "ink", "text"), PARTS)}
BOUNDS = {k: m.bounds for k, m in MESHES.items()}
assert all(m.is_watertight for m in MESHES.values())
ANCHOR_CENTER = MESHES["backer"].bounds.mean(axis=0)
POS = (CENTER[0] - float(ANCHOR_CENTER[0]), CENTER[1] - float(ANCHOR_CENTER[1]))
FOOT_PLATE = translate(footprint(MESHES["backer"]), *POS)


def main():
    offsets = BRIM_OFFSETS
    for attempt in (1, 2):
        tower = tower_spot(FOOT_PLATE, offsets)
        print(f"{NOZZLE} nozzle, {PROCESS}: tower {tower}, clearance {check_tower(tower, FOOT_PLATE, offsets)} (brim offsets {offsets})")
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
    if drift > 0 and measured != BRIM_OFFSETS:
        report["tower"]["note"] = f"update MODES['{NOZZLE}']['brim'] in make_tag_3mf.py to {measured}"
    report.update({"file": OUT, "nozzle": NOZZLE, "presets": {"machine": MACHINE, "process": PROCESS, "filament": FILAMENT,
                                                             "colours": COLOURS, "bed": BED_TYPE, "bed_temp": BED_TEMP},
                   "object": OBJECT, "plate": PLATE, "parts": [{k: v for k, v in q.items()} for q in PARTS],
                   "placement": list(CENTER), "locked_process_keys": LOCKED, "deliverable": not ALT})
    with open(OUT.replace(".3mf", "-slice.json"), "w") as f:
        json.dump(report, f, indent=1)
    t, gr, tc = report["time"], report["grams"], report["tool_changes"]
    print(f"{OUT}\n  {NOZZLE} nozzle: {t['h_m']} ({t['minutes']} min, cap {TIME_CAP_MIN}, {'OK' if t['under_cap'] else 'OVER'}); "
          f"{report['layers']} layers ({report['first_layer_height']} + {report['layer_height']}); "
          f"white {gr['white (1)']} g + black {gr['black (2)']} g = {gr['total']} g\n"
          f"  filament changes {tc['count']} (start {tc['start']}): " + ", ".join(f"L{c['layer']}->{c['to']}" for c in tc["changes"])
          + f"\n  tower at {tower}, brim {report['tower']['brim_offsets_measured']}, clearance {report['tower']['clearance']}; "
          f"tiers text L{report['tiers']['text_layers'][0]}-{report['tiers']['text_layers'][-1]}, backer to L{report['tiers']['backer_layers'][1]}, "
          f"ink L{report['tiers']['ink_layers'][0]}-{report['tiers']['ink_layers'][1]}; first-layer letter moves {report['gcode_proofs']['first_layer_black_moves_in_text']}")


if __name__ == "__main__":
    main()
