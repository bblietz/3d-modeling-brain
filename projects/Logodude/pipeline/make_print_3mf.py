"""Bambu Studio project 3MF for the Logo Dude badge: one object, two parts, one color change at z = 3 mm.

  backer (white)  logodude-backer.stl, z 0..3, filament 1, Bambu PETG Basic #FFFFFF
  ink (black)     logodude-ink.stl,    z 3..4, filament 2, Bambu PETG Basic #000000

X2D 0.4 nozzle, 0.12 mm layers, textured PEI, both filaments on extruder 1 (direct drive). Built on the validated
small-lettering recipe (knowledge/lettering-x2d.md) with the Sharks-nametag tooling (fillcore_mod, graft_slice,
gcode_features, toolpath_voids), imported unchanged:
  - process: the locked SMOOTH_TOP keys of Sharks flatten_04.py (no ironing, 2 top walls, arachne, skirt, tower brim ...),
    every one listed in different_settings_to_system[0]
  - filament: PETG Basic's own preset (250 C, 245 C first layer); bed textured PEI 70 C, the preset's own value and
    the Sharks PETG setting, still written and listed in the filament diff slots (Brian 2026-09-29: PETG, not PLA)
  - fill-core MODIFIER over the five thin face strokes only (outline + 0.3 mm, z band = the ink-only layers) with the
    recipe's region keys; infill_direction chosen from the strokes' own direction (they run mostly along x, the Sharks
    stems ran along y); the hair (about 5 mm wide) keeps the normal process
  - OBJECT key detect_narrow_internal_solid_infill 0 through the CLI assemble list print_params
  - prime tower at the free spot closest to the bed center: brim >= 12 mm from the backer, >= 15 mm from the bed edges

Verification (all offline): authored-file and CLI round-trip checks, then real CLI slices of the file (A), of the file
without the modifier (B, proves the modifier changes nothing outside the face strokes) and of the file without the
object key (C, recipe step 5 side effect). Writes logodude.3mf and logodude-slice.json next to the STLs.

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
import subprocess
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
PARTS = [  # filament n = position in this list
    {"stl": "logodude-backer.stl", "name": "backer (white)", "colour": "#FFFFFF"},
    {"stl": "logodude-ink.stl", "name": "ink (black)", "colour": "#000000"},
]
OBJECT_NAME = "Logo Dude badge"
OUT = f"{PROJECT}/logodude.3mf"
CENTER = (128.0, 128.0)
BED_TYPE = "Textured PEI Plate"
BED_TEMP = "70"                  # PETG Basic on textured PEI (preset value; Sharks tags printed at 70)
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


# ------------------------------------------------------------------ geometry
def geometry():
    """Ink footprint split into the hair and the five face strokes, the backer outline, the fill direction, the z band."""
    backer = trimesh.load(f"{PROJECT}/{PARTS[0]['stl']}")
    ink = trimesh.load(f"{PROJECT}/{PARTS[1]['stl']}")
    assert backer.is_watertight and ink.is_watertight
    assert abs(backer.bounds[0][2]) < 1e-6 and abs(backer.bounds[1][2] - BACKER_TOP) < 1e-6
    assert abs(ink.bounds[0][2] - BACKER_TOP) < 1e-6 and abs(ink.bounds[1][2] - INK_TOP) < 1e-6
    polys = sorted(fm.section_polys(ink, (BACKER_TOP + INK_TOP) / 2), key=lambda p: -p.area)
    assert len(polys) == 6, len(polys)
    for z in (BACKER_TOP + 0.05, INK_TOP - 0.05):   # straight prisms: same outline over the whole ink height
        assert abs(sum(p.area for p in fm.section_polys(ink, z)) - sum(p.area for p in polys)) < 0.5, z
    # share of each shape narrower than NARROW (what an opening at NARROW / 2 removes)
    narrow = [1 - p.buffer(-NARROW / 2).buffer(NARROW / 2).intersection(p).area / p.area for p in polys]
    hair, face = polys[0], polys[1:]
    assert narrow[0] < 0.02 and min(narrow[1:]) > 0.5, narrow      # the hair is wide, every face shape is mostly narrow
    assert min(hair.distance(f) for f in face) > 2 * fm.MOD_BUFFER + 1, "the face modifier would reach the hair"
    # infill_direction: the candidate the face strokes run along most (length-weighted outline edges; for a thin
    # stroke the outline runs along the stroke)
    edges = np.vstack([np.diff(np.asarray(r.coords)[:, :2], axis=0) for p in face for r in (p.exterior, *p.interiors)])
    length, angle = np.hypot(edges[:, 0], edges[:, 1]), np.degrees(np.arctan2(edges[:, 1], edges[:, 0]))
    along = {d: float((length * (np.abs((angle - d + 90) % 180 - 90) <= 30)).sum() / length.sum()) for d in DIRECTIONS}
    direction = max(along, key=along.get)
    bsec = fm.section_polys(backer, BACKER_TOP / 2)
    assert len(bsec) == 1
    first = float(PROCESS_CFG["initial_layer_print_height"])
    layer = float(PROCESS_CFG["layer_height"])
    z0, z1, n_layers, tier = fm.modifier_z_band(BACKER_TOP, INK_TOP, first, layer)
    return dict(backer=bsec[0], backer_mesh=backer, hair=hair, face=face, narrow=narrow, along=along,
                direction=direction, z0=z0, z1=z1, n_layers=n_layers, tier=tier, first=first, layer=layer)


def tower_spot(backer_on_plate):
    """wipe_tower_x/y of the free spot closest to the bed center (the Sharks rule, with the real backer outline in
    place of fm.check_tower's disc): brim >= fm.TOWER_DISC_MIN from the backer, >= fm.TOWER_EDGE_MIN from the edges."""
    cx, cy = (BRIM_OFFSETS[0] + BRIM_OFFSETS[2]) / 2, (BRIM_OFFSETS[1] + BRIM_OFFSETS[3]) / 2
    grid = [(float(x), float(y)) for x in np.arange(0, fm.BED, 0.5) for y in np.arange(0, fm.BED, 0.5)]
    for t in sorted(grid, key=lambda t: math.hypot(t[0] + cx - CENTER[0], t[1] + cy - CENTER[1])):
        if check_tower(t, backer_on_plate, strict=False):
            return t
    raise AssertionError("no tower spot")


def check_tower(tower, backer_on_plate, strict=True):
    x0, y0, x1, y1 = (tower[0] + BRIM_OFFSETS[0], tower[1] + BRIM_OFFSETS[1],
                      tower[0] + BRIM_OFFSETS[2], tower[1] + BRIM_OFFSETS[3])
    edge = min(x0, y0, fm.BED - x1, fm.BED - y1)
    part = box(x0, y0, x1, y1).distance(backer_on_plate)
    ok = edge >= fm.TOWER_EDGE_MIN and part >= fm.TOWER_DISC_MIN
    assert ok or not strict, f"tower {tower}: brim {part:.2f} mm from the badge, {edge:.2f} mm from a bed edge"
    return (round(part, 2), round(edge, 2)) if ok else None


# ------------------------------------------------------------------- build
def build(G):
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
    center = G["backer_mesh"].bounds.mean(axis=0)   # pos_x/pos_y place the STLs' shared origin
    pos = (CENTER[0] - float(center[0]), CENTER[1] - float(center[1]))
    spec = {"plates": [{"plate_name": OBJECT_NAME, "need_arrange": False, "plate_params": {"curr_bed_type": BED_TYPE},
                        "objects": [{"path": f"{PROJECT}/{p['stl']}", "count": 1, "filaments": [n], "assemble_index": [1],
                                     "pos_x": [pos[0]], "pos_y": [pos[1]], "pos_z": [0]} for n, p in enumerate(PARTS, 1)],
                        "assembled_params": [{"assemble_index": 1, "print_params": fm.C7_OBJECT_KEYS}]}]}
    with open(f"{BUILD}/assemble.json", "w") as f:
        json.dump(spec, f, indent=1)
    fm.cli(["--arrange", "0", "--load-assemble-list", "assemble.json", "--load-settings", "machine.json;process.json",
            "--load-filaments", "filament.json;filament.json", "--export-3mf", "raw.3mf", "--outputdir", "."], BUILD, "assemble")

    backer_c = fm.centered(G["backer_mesh"])[1]
    mod_c, mod_center = fm.centered(fm.extrude(fm.modifier_2d(G["face"]), G["z0"], G["z1"]))
    assert mod_c.is_watertight
    with zipfile.ZipFile(f"{BUILD}/raw.3mf") as zin:
        cfg = json.loads(zin.read("Metadata/project_settings.config"))
        patch_config(cfg)
        model = zin.read("Metadata/model_settings.config").decode()
        model3d = zin.read("3D/3dmodel.model").decode()
        objfiles = {n: zin.read(n).decode() for n in zin.namelist() if n.startswith("3D/Objects/")}
        objs = re.findall(r'<object id="(\d+)">', model)
        assert len(objs) == 1, objs
        oid = objs[0]
        m = re.search(rf'<object id="{oid}">.*?</object>', model, re.S)
        block = re.sub(r'(<object id="\d+">\s*<metadata key="name" value=")[^"]*"', rf'\g<1>{OBJECT_NAME}"', m.group(0), count=1)
        for p in PARTS:   # each part is named after its STL by the CLI
            block, n = re.subn(rf'(<part id="\d+" subtype="normal_part"[^>]*>\s*<metadata key="name" value=")[^"]*("/>(?:(?!</part>).)*?value="{re.escape(p["stl"])}")',
                               rf'\g<1>{p["name"]}\g<2>', block, flags=re.S)
            assert n == 1, (p["stl"], n)
        opos = fm.object_pos(model3d, oid, backer_c)
        name = "MOD face strokes fill-core: " + ", ".join(f"{k} {v}" for k, v in MOD_KEYS.items())
        block, model3d = fm.inject_modifier(block, model3d, objfiles, oid, fm.next_object_id(model3d, objfiles), name,
                                            "mod-face-strokes.stl", mod_c, mod_center, opos, MOD_KEYS)
        model = model[:m.start()] + block + model[m.end():]
        model = re.sub(r'( *)<metadata key="filament_map_mode" value="[^"]*"/>',
                       lambda k: f'{k.group(1)}<metadata key="filament_map_mode" value="Manual"/>\n'
                                 f'{k.group(1)}<metadata key="filament_maps" value="{" ".join(FILAMENT_MAP)}"/>', model)
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = {"Metadata/project_settings.config": json.dumps(cfg, indent=4), "Metadata/model_settings.config": model,
                        "3D/3dmodel.model": model3d}.get(item.filename, objfiles.get(item.filename))
                zout.writestr(item, data if data is not None else zin.read(item.filename))
    return opos


def patch_config(cfg):
    """The CLI export's fixes (reference-two-material-two-plate-3mf): colours, per-filament vectors, the flush block
    (extruders x filaments^2), extruder map; plus bed, tower and every changed key in different_settings_to_system."""
    nf, ne = len(PARTS), len(cfg["nozzle_diameter"])
    cfg["filament_colour"] = cfg["filament_multi_colour"] = [p["colour"] for p in PARTS]
    cfg["filament_map_mode"], cfg["filament_map"], cfg["filament_nozzle_map"] = "Manual", FILAMENT_MAP, FILAMENT_MAP
    cfg["flush_multiplier"], cfg["flush_multiplier_fast"] = ["1"] * ne, ["1.2"] * ne
    # 280 mm3 placeholder (as every vault CLI build); Studio's "Re-calculate" sets the colour-based value
    cfg["flush_volumes_matrix"] = ["0" if a == b else "280" for _ in range(ne) for a in range(nf) for b in range(nf)]
    cfg["flush_volumes_vector"] = ["140"] * (ne * nf)
    cfg["curr_bed_type"] = BED_TYPE
    for k in BED_KEYS:
        cfg[k] = [BED_TEMP] * nf
    cfg["wipe_tower_x"], cfg["wipe_tower_y"] = [f"{TOWER[0]:g}"], [f"{TOWER[1]:g}"]
    diff = cfg["different_settings_to_system"]
    assert len(diff) == nf + 2, diff    # [process, filament 1..n, machine]
    diff[0] = ";".join(sorted(set(x for x in diff[0].split(";") if x) | set(SMOOTH_TOP)))
    for i in range(1, nf + 1):
        diff[i] = ";".join(sorted(set(x for x in diff[i].split(";") if x) | set(BED_KEYS)))
    return cfg


# ------------------------------------------------------------------ checks
def check_file(path, label):
    with zipfile.ZipFile(path) as z:
        cfg = json.loads(z.read("Metadata/project_settings.config"))
        ms = z.read("Metadata/model_settings.config").decode()
        m3 = z.read("3D/3dmodel.model").decode()
    assert cfg["printer_settings_id"] == MACHINE and cfg["print_settings_id"] == PROCESS, label
    assert cfg["filament_settings_id"] == [FILAMENT] * 2 and cfg["filament_type"] == ["PETG", "PETG"], label
    assert cfg["nozzle_diameter"][0] == "0.4" and cfg["layer_height"] == "0.12", (label, cfg["layer_height"])
    assert cfg["filament_colour"] == [p["colour"] for p in PARTS], (label, cfg["filament_colour"])
    assert cfg["filament_map"] == FILAMENT_MAP and cfg["filament_map_mode"] == "Manual", label
    assert cfg["curr_bed_type"] == BED_TYPE and all(cfg[k] == [BED_TEMP] * 2 for k in BED_KEYS), label
    for k, v in SMOOTH_TOP.items():
        got = cfg[k]
        assert (set(got) == {v[0]} if isinstance(v, list) else got == v), f"{label}: {k} = {got}"
    diff = cfg["different_settings_to_system"]
    assert set(SMOOTH_TOP) <= set(diff[0].split(";")), f"{label}: process keys missing from the diff list"
    assert all(set(BED_KEYS) <= set(diff[i].split(";")) for i in (1, 2)), f"{label}: bed keys missing from the filament diff slots"
    assert (cfg["wipe_tower_x"], cfg["wipe_tower_y"]) == ([f"{TOWER[0]:g}"], [f"{TOWER[1]:g}"]), label
    ne = len(cfg["nozzle_diameter"])
    assert len(cfg["flush_volumes_matrix"]) == ne * 4 and cfg["flush_volumes_matrix"][:4] == ["0", "280", "280", "0"], label
    assert cfg["print_sequence"] == "by layer" and cfg["enable_prime_tower"] == "1", label
    objs = re.findall(r'<object id="(\d+)">(.*?)</object>', ms, re.S)
    assert len(objs) == 1, (label, len(objs))
    body = objs[0][1]
    assert re.search(rf'<metadata key="name" value="{OBJECT_NAME}"/>', body.split("<part ", 1)[0]), label
    assert fm.check_object(body, fm.C7_OBJECT_KEYS, MOD_KEYS, ["1", "2"], label) == (2, 1)
    names = re.findall(r'<part id="\d+" subtype="normal_part"[^>]*>\s*<metadata key="name" value="([^"]*)"', body)
    assert names == [p["name"] for p in PARTS], (label, names)
    assert len(re.findall(r"<component ", m3)) == 3, label
    tf = re.search(r'<item [^>]*transform="([^"]*)"', m3).group(1).split()
    pos = fm.object_pos(m3, objs[0][0], fm.centered(GEO["backer_mesh"])[1])
    got = (round(float(tf[9]) + pos[0], 3), round(float(tf[10]) + pos[1], 3))
    bc = GEO["backer_mesh"].bounds.mean(axis=0)
    assert abs(got[0] + bc[0] - CENTER[0]) < 0.01 and abs(got[1] + bc[1] - CENTER[1]) < 0.01, (label, got)
    return cfg


def slice_file(src, tag):
    res = graft_slice(src, f"{BUILD}/sliced-{tag}.3mf")
    assert res["rc"] == 0 and res["gcode"], f"slice {tag} failed rc={res['rc']}, log {res['log']}"
    with zipfile.ZipFile(res["out"]) as z:
        info = z.read("Metadata/slice_info.config").decode()
        gcode = z.read(res["gcode"]).decode(errors="ignore")
    res["info"] = info
    res["g"] = gcode
    return res


def variant(tag, strip_modifier=False, strip_key=False):
    """The authored file without the modifier (B) or without the object key (C), everything else identical."""
    dst = f"{BUILD}/variant-{tag}.3mf"
    if strip_modifier:
        fm.strip_recipe(OUT, dst, keep_object_key=True)
        return dst
    with zipfile.ZipFile(OUT) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "Metadata/model_settings.config" and strip_key:
                data, n = re.subn(rb'\s*<metadata key="detect_narrow_internal_solid_infill" value="0"/>', b"", data)
                assert n == 1, n
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


def verify(opos):
    cfg = check_file(OUT, "authored")
    fm.cli(["--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", OUT], BUILD, "round trip")
    check_file(f"{BUILD}/roundtrip.3mf", "CLI round trip")
    report = {"round_trip": "pass: colours, per-part extruders, names, modifier + keys, object key, diff lists, centering"}

    A = slice_file(OUT, "A")
    g = A["g"]
    info = A["info"]
    used = {int(i): float(v) for i, v in re.findall(r'<filament id="(\d+)"[^>]*?used_g="([^"]*)"', info)}
    groups = set(re.findall(r'<filament id="\d+"[^>]*?group_id="(\d+)"', info))
    pred = int(re.search(r'key="prediction" value="(\d+)"', info).group(1))
    assert set(used) == {1, 2} and groups == {"0"}, (used, groups)
    assert "X2D start gcode" in g, "machine include templates did not merge"
    assert re.search(r"^; filament_map = 1,1$", g, re.M)
    assert re.search(rf"^\s*M1[49]0 S{BED_TEMP}\b", g, re.M), "bed temperature"
    assert re.search(r"^\s*M10[49] S250\b", g, re.M), "nozzle temperature (PETG Basic 250)"
    layers = tv.parse_layers(g)
    zs = sorted(layers)
    steps = sorted({round(b - a, 3) for a, b in zip(zs, zs[1:])})
    assert A["layers"] == GEO["n_layers"] == len(zs) and zs[0] == GEO["first"] and steps == [GEO["layer"]], (A["layers"], zs[:3], steps)
    # exactly one filament change, white -> black, at the first ink layer
    body = g[g.index("; Z_HEIGHT:"):]
    tools, z_now, changes = [], None, []
    for line in body.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z_now = round(float(line.split(":")[1]), 3)
        elif re.match(r"\s*T\d+( |$)", line) and int(line.split()[0][1:]) < 16:   # "T1 H-1"; T65279 etc. are unloads
            t = line.split()[0]
            if not tools or tools[-1] != t:
                changes.append((z_now, t))
            tools.append(t)
    first_ink = min(z for z in zs if z - GEO["layer"] / 2 > BACKER_TOP)
    assert [t for _, t in changes] == ["T1"] and changes[0][0] == first_ink, changes   # T0 comes from the start G-code
    flush = [float(v) for v in re.findall(r"^M620\.10 A1 \S+ L([0-9.]+)", body, re.M)]
    assert len(flush) == 1, flush
    # the tower: layer-1 brim inside the predicted rectangle, clear of the badge
    tw = [s for s in layers[zs[0]] if s[5] in ("Prime tower", "Wipe tower")]
    assert tw, "no tower on layer 1"
    tb = (min(min(s[0], s[2]) for s in tw), min(min(s[1], s[3]) for s in tw), max(max(s[0], s[2]) for s in tw), max(max(s[1], s[3]) for s in tw))
    meas = tuple(round(v - TOWER[i % 2], 2) for i, v in enumerate(tb))
    pred_brim = (TOWER[0] + BRIM_OFFSETS[0], TOWER[1] + BRIM_OFFSETS[1], TOWER[0] + BRIM_OFFSETS[2], TOWER[1] + BRIM_OFFSETS[3])
    assert all(tb[i] >= pred_brim[i] - 0.5 for i in (0, 1)) and all(tb[i] <= pred_brim[i] + 0.5 for i in (2, 3)), (meas, BRIM_OFFSETS)
    part = box(*tb).distance(BACKER_PLATE)
    edge = min(tb[0], tb[1], fm.BED - tb[2], fm.BED - tb[3])
    assert part >= fm.TOWER_DISC_MIN and edge >= fm.TOWER_EDGE_MIN, (part, edge)
    # the badge sits where it should
    walls = [s for s in layers[zs[0]] if s[5] == "Outer wall"]
    wb = (min(s[0] for s in walls), min(s[1] for s in walls), max(s[0] for s in walls), max(s[1] for s in walls))
    assert abs((wb[0] + wb[2]) / 2 - CENTER[0]) < 0.5 and abs((wb[1] + wb[3]) / 2 - CENTER[1]) < 0.5, wb

    ink_layers = [z for z in zs if z - GEO["layer"] / 2 > BACKER_TOP]
    face_plate = translate(unary_union(GEO["face"]), *opos[:2])
    hair_plate = translate(GEO["hair"], *opos[:2])
    fmA = face_metrics(layers, face_plate, ink_layers)
    top = fmA["layers"][-1]
    # modifier keys in effect inside the face strokes: 0.3 top / internal solid lines, one wall, fill along the strokes
    for row in fmA["layers"]:
        for f, ws in row["widths"].items():
            assert all(abs(w - 0.3) <= 0.03 for w in ws), (row["z"], f, ws)   # 0.3 lines (Studio adjusts spacing a little)
        assert row["inner_wall_mm"] < 1.0, (row["z"], row["inner_wall_mm"])
    assert top["fill_deg"] is not None and min(abs(top["fill_deg"] - GEO["direction"]), 180 - abs(top["fill_deg"] - GEO["direction"])) <= 15, top
    dirs = [r["fill_deg"] for r in fmA["layers"][-5:]]
    hair_top = {round(s[4], 2) for s in layers[zs[-1]] if s[5] == "Top surface" and hair_plate.contains(Point((s[0] + s[2]) / 2, (s[1] + s[3]) / 2))}
    assert hair_top == {0.42}, hair_top

    # B: without the modifier; C: without the object key (recipe step 5). Every extrusion segment outside the face
    # strokes + 1 mm is compared, per layer and feature.
    zone = face_plate.buffer(1.0)
    mA = gf.parse_moves(g)
    B = slice_file(variant("B", strip_modifier=True), "B")
    C = slice_file(variant("C", strip_key=True), "C")
    diffB, diffC = outside_diff(mA, gf.parse_moves(B["g"]), zone), outside_diff(mA, gf.parse_moves(C["g"]), zone)
    fmB = face_metrics(tv.parse_layers(B["g"]), face_plate, ink_layers)
    layersC = tv.parse_layers(C["g"])
    fmC = face_metrics(layersC, face_plate, ink_layers)
    # B: the modifier leaves every visible surface outside the face strokes alone. Layer 1 and all walls are identical;
    # the white top layer (last backer layer) only re-phases its lines, because without the modifier Studio also runs
    # top surface under the black strokes; the rest is hidden infill.
    last_backer = max(z for z in zs if z < first_ink)
    white = translate(GEO["backer"].buffer(-0.5), *opos[:2]).difference(translate(unary_union(GEO["face"] + [GEO["hair"]]), *opos[:2]).buffer(0.5))
    hidden = {"Internal solid infill", "Sparse infill", "Bridge", "Gap infill", "Floating vertical shell"}
    for tag, d in (("B", diffB), ("C", diffC)):
        assert set(d) <= hidden | {"Top surface"}, (tag, set(d))
        assert all(zs[0] not in f["layers"] for f in d.values()), (tag, "layer 1 changed")
        assert set(d.get("Top surface", {"layers": []})["layers"]) <= {last_backer}, (tag, d["Top surface"])
    white_top = {"A": uncovered(layers, last_backer, white), "B": uncovered(tv.parse_layers(B["g"]), last_backer, white),
                 "C": uncovered(layersC, last_backer, white)}
    assert max(white_top.values()) - min(white_top.values()) < 0.1, white_top
    # C: the object key's side effect (recipe step 5) sits in hidden layers only (checked above); in the white top-shell
    # layers under the visible white top it does not lose coverage, so no concentric modifier is added
    shell = [z for z in zs if last_backer - 4 * GEO["layer"] < z <= last_backer and any(z in f["layers"] for f in diffC.values())]
    side = [dict(z=z, uncovered_mm2_key_on=uncovered(layers, z, white), uncovered_mm2_key_off=uncovered(layersC, z, white)) for z in shell]
    assert all(r["uncovered_mm2_key_on"] <= r["uncovered_mm2_key_off"] + 0.1 for r in side), side
    assert fmA["visible_mm2"] <= min(fmB["visible_mm2"], fmC["visible_mm2"]), (fmA["visible_mm2"], fmB["visible_mm2"], fmC["visible_mm2"])

    def grams(res):
        per = gf.feature_split(gf.parse_moves(res["g"]), gf.header(res["g"]))[0]
        return {k: round(v, 2) for k, v in sorted(per.items(), key=lambda kv: -kv[1]) if v >= 0.005}

    report.update({
        "slice": {"rc": A["rc"], "layers": A["layers"], "first_layer_mm": zs[0], "layer_mm": GEO["layer"],
                  "time_estimate": A["time"], "prediction_s": pred, "minutes": round(pred / 60, 1),
                  "grams": {PARTS[i - 1]["name"]: used[i] for i in sorted(used)}, "grams_total": round(sum(used.values()), 2),
                  "filament_change": {"z": changes[0][0], "tool": changes[0][1], "flush_mm": flush[0],
                                      "flush_mm3": round(flush[0] * math.pi * 0.875 ** 2), "matrix": cfg["flush_volumes_matrix"]},
                  "bed_C": BED_TEMP, "nozzle_C": 250, "grams_by_feature": grams(A)},
        "tower": {"wipe_tower_xy": TOWER, "layer1_bbox": [round(v, 2) for v in tb], "bbox_minus_xy": meas,
                  "clear_of_badge_mm": round(part, 2), "clear_of_bed_edge_mm": round(edge, 2)},
        "face_strokes_A": fmA, "top_fill_directions_last5": dirs,
        "hair_top_line_width": sorted(hair_top),
        "white_top_uncovered_mm2": white_top,
        "B_no_modifier": {"time": B["time"], "diff_outside_face_zone": diffB,
                          "face_visible_mm2": fmB["visible_mm2"], "face_top": fmB["layers"][-1]},
        "C_no_object_key": {"time": C["time"], "diff_outside_face_zone": diffC, "white_shell_layers_uncovered": side,
                            "face_visible_mm2": fmC["visible_mm2"], "face_top": fmC["layers"][-1]},
    })
    return report


PROCESS_CFG = flatten("process", PROCESS)
GEO = geometry()
MOD_KEYS = dict(fm.C7_MOD_KEYS, infill_direction=str(GEO["direction"]))
_bc = GEO["backer_mesh"].bounds.mean(axis=0)
BACKER_PLATE = translate(GEO["backer"], CENTER[0] - _bc[0], CENTER[1] - _bc[1])
TOWER = tower_spot(BACKER_PLATE)


def main():
    print(f"face strokes narrower than {NARROW} mm: hair {GEO['narrow'][0]:.1%}, face " +
          ", ".join(f"{v:.0%}" for v in GEO["narrow"][1:]))
    print(f"direction: share of face-stroke length within 30 deg of each candidate {GEO['along']} -> {GEO['direction']}")
    print(f"modifier z {GEO['z0']:.2f}..{GEO['z1']:.2f} over ink layer centers {GEO['tier']}; {GEO['n_layers']} layers; "
          f"tower {TOWER} clearance {check_tower(TOWER, BACKER_PLATE)}")
    opos = build(GEO)
    report = verify(opos)
    report.update({"presets": {"machine": MACHINE, "process": PROCESS, "filament": FILAMENT},
                   "geometry": {"narrow_share": {"hair": round(GEO["narrow"][0], 3), "face": [round(v, 3) for v in GEO["narrow"][1:]]},
                                "along_share": GEO["along"], "infill_direction": GEO["direction"],
                                "modifier": {"buffer": fm.MOD_BUFFER, "z": [round(GEO["z0"], 3), round(GEO["z1"], 3)],
                                             "layers": GEO["tier"], "keys": MOD_KEYS}}})
    with open(OUT.replace(".3mf", "-slice.json"), "w") as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
