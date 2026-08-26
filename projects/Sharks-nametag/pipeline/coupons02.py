"""0.2-nozzle letter coupon: W1 only (S-A-N-T-A + CITY left + ball
bottom + surfer) cropped from the canonical v3.26 STLs onto a
1.0 mm slab, ONE object, with the flattened 0.2 presets (flatten_02.py:
machine X2D 0.2, process 0.08mm High Quality 0.2, PETG Basic 0.2) and
the SAME locked solid-text recipe as the failed 0.4 gate - the only
variable is the nozzle. Physical test of the offline zero-void
prediction (see brief.md 2026-08-23 late night).

Run: `.venv/bin/python projects/Sharks-nametag/pipeline/coupons02.py`
-> exports/solid-text-coupons-02.3mf (exports/ is the experiments area,
recreated on demand; final/ holds the production files). Brian: swap the 0.2 nozzle in the
printer AND set Studio's machine to X2D 0.2 (print-1 lesson), slice,
print."""
import json
import os
import re
import subprocess
import zipfile

import numpy as np
import trimesh
from shapely.geometry import Polygon

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Sharks-nametag"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
WORK = f"{SCRATCH}/coupon-stl-02"
OUT = f"{PROJ}/exports/solid-text-coupons-02.3mf"   # experiments area (recreated on demand); production files live in final/
os.makedirs(os.path.dirname(OUT), exist_ok=True)
COLORS = ["#FFFFFF", "#00395E", "#31BAD6"]
BED_TYPE = "Textured PEI Plate"
TOWER = (105, 160)   # 2026-08-24: was (12, 203), the plate corner, where the brimless tower peeled; now centered behind the coupon (footprint ~x 105-150, y 160-200, 18 mm clear of the coupon)
SMOOTH_KEYS = ["ironing_type", "top_one_wall_type",   # keep in sync with batch_roster.py
               "top_surface_line_width", "top_shell_layers", "top_surface_speed",
               "sparse_infill_density", "sparse_infill_pattern", "wall_generator",
               "seam_gap", "small_perimeter_speed", "small_perimeter_threshold",
               "gap_infill_speed", "wall_distribution_count", "wall_transition_filter_deviation",
               "min_feature_size", "min_bead_width",
               "skirt_loops", "skirt_distance", "skirt_height", "initial_layer_speed",
               "initial_layer_infill_speed",
               "prime_tower_brim_width"]
UNDER_ART = 1.0
# W2 (band stars) dropped per Brian 2026-08-23: the band-star cutouts
# have always printed fine, and the 4 cyan top-arc stars that once
# voided were fine on IMG_1530 - the 0.2 full-tag gate covers them.
WINDOWS = {"W1": (-22, 4, -17, 11)}
WINDOW_Y = {"W1": 128.0}
X = 128.0
COLOR_IDS = {"white": 1, "navy": 2, "cyan": 3}

with open(f"{SCRATCH}/flat-filament-02.json") as f:
    _fil = json.load(f)
BED_TEMPS = {k: _fil[k][0] for k in ("textured_plate_temp", "textured_plate_temp_initial_layer")}

os.makedirs(WORK, exist_ok=True)
meshes = {c: trimesh.load(f"{PROJ}/sharks-nametag-{c}.stl") for c in COLOR_IDS}
zs = sorted(set(np.round(meshes["white"].vertices[:, 2], 2)))
top = max(zs)
base_top = max(z for z in zs if z < top - 0.5)
z_cut = base_top - UNDER_ART
print(f"canonical STLs: white top {top}, disc top {base_top} -> slab cut at z {z_cut}")

def crop(mesh, x0, x1, y0, y1, zc):
    m = mesh.copy()
    for n, o in (((0, 0, 1), (0, 0, zc)), ((1, 0, 0), (x0, 0, 0)), ((-1, 0, 0), (x1, 0, 0)),
                 ((0, 1, 0), (0, y0, 0)), ((0, -1, 0), (0, y1, 0))):
        m = trimesh.intersections.slice_mesh_plane(m, plane_normal=n, plane_origin=o, cap=True)
        if m is None or m.is_empty:
            return None
    m.merge_vertices()
    m.fix_normals()
    return m


objects, part_names = [], {}
for wname, (x0, x1, y0, y1) in WINDOWS.items():
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for color, fid in COLOR_IDS.items():
        m = crop(meshes[color], x0, x1, y0, y1, z_cut)
        if m is None:
            continue
        assert m.is_watertight, f"{wname} {color} not watertight"
        m.apply_translation([-cx, -cy, -z_cut])
        base = f"N2-{wname}-{color}"
        m.export(f"{WORK}/{base}.stl")
        objects.append({"path": f"{WORK}/{base}.stl", "count": 1, "filaments": [fid],
                        "assemble_index": [1], "pos_x": [X], "pos_y": [WINDOW_Y[wname]], "pos_z": [0]})
        part_names[base] = f"0.2 {wname} {color}"
assert len(objects) == 3, len(objects)
spec = {"plates": [{"plate_name": "0.2 nozzle letter coupon", "need_arrange": False,
                    "plate_params": {"curr_bed_type": BED_TYPE}, "objects": objects,
                    "assembled_params": []}]}
spec_path = f"{SCRATCH}/coupons02-assemble.json"
with open(spec_path, "w") as f:
    json.dump(spec, f, indent=1)

raw = f"{SCRATCH}/raw-coupons02.3mf"
rt = f"{SCRATCH}/rt-coupons02.3mf"
for p in (raw, rt):
    if os.path.exists(p):
        os.remove(p)
r = subprocess.run(
    ["bambu-studio", "--arrange", "0", "--load-assemble-list", spec_path,
     "--load-settings", f"{SCRATCH}/flat-machine-02.json;{SCRATCH}/flat-process-02.json",
     "--load-filaments", ";".join([f"{SCRATCH}/flat-filament-02.json"] * 3),
     "--export-3mf", os.path.basename(raw), "--outputdir", SCRATCH],
    capture_output=True, text=True, timeout=900, cwd=SCRATCH)
assert r.returncode == 0, f"CLI assemble rc={r.returncode}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"

with zipfile.ZipFile(raw) as zin:
    cfg = json.loads(zin.read("Metadata/project_settings.config"))
    assert str(cfg.get("layer_height")) == "0.08", cfg.get("layer_height")
    assert cfg.get("nozzle_diameter") == ["0.2", "0.2"], cfg.get("nozzle_diameter")
    cfg["filament_colour"] = COLORS
    dsts = cfg.get("different_settings_to_system") or [""]
    assert len(dsts) == 5, dsts
    listed = [k for k in dsts[0].split(";") if k]
    for k in SMOOTH_KEYS:
        if k not in listed:
            listed.append(k)
    dsts[0] = ";".join(listed)
    cfg["curr_bed_type"] = BED_TYPE
    for k, v in BED_TEMPS.items():
        cfg[k] = [v] * 3
    for fi in (1, 2, 3):
        fl = [x for x in dsts[fi].split(";") if x]
        for k in BED_TEMPS:
            if k not in fl:
                fl.append(k)
        dsts[fi] = ";".join(fl)
    cfg["different_settings_to_system"] = dsts
    # dual-extruder flush block (2026-08-23; 16-entry placeholder = Studio
    # reads uninitialized memory -> NaN on slice)
    _m = ["0", "280", "280", "280", "0", "280", "280", "280", "0"]
    cfg["flush_volumes_matrix"] = _m + _m
    cfg["flush_volumes_vector"] = ["140"] * 6
    cfg["flush_multiplier"] = ["1", "1"]
    cfg["flush_multiplier_fast"] = ["1.2", "1.2"]
    cfg["nozzle_flush_dataset"] = ["1", "2", "2", "1", "2", "2"]
    cfg["wipe_tower_x"] = [str(TOWER[0])]
    cfg["wipe_tower_y"] = [str(TOWER[1])]

    model = zin.read("Metadata/model_settings.config").decode()
    model = model.replace('<metadata key="name" value="assemble_1"/>',
                          '<metadata key="name" value="coupon 0.2 letters"/>')
    for base, friendly in part_names.items():
        model = model.replace(f'value="{base}_1"', f'value="{friendly}"')
    assert "assemble_" not in model
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "Metadata/project_settings.config":
                zout.writestr(item, json.dumps(cfg, indent=4))
            elif item.filename == "Metadata/model_settings.config":
                zout.writestr(item, model)
            else:
                zout.writestr(item, zin.read(item.filename))

r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", rt, OUT],
                   capture_output=True, text=True, timeout=900, cwd=SCRATCH)
assert r.returncode == 0, f"CLI round trip rc={r.returncode}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
for path, label in ((OUT, "out"), (rt, "round trip")):
    with zipfile.ZipFile(path) as z:
        c = json.loads(z.read("Metadata/project_settings.config"))
        assert c.get("filament_colour") == COLORS, label
        assert str(c.get("layer_height")) == "0.08", (label, c.get("layer_height"))
        assert c.get("nozzle_diameter") == ["0.2", "0.2"], label
        assert c.get("ironing_type") == "no ironing" and c.get("top_one_wall_type") == "not apply", label
        assert c.get("wall_generator") == "arachne", label
        assert c.get("seam_gap") == "0%" and c.get("min_bead_width") == "50%", label
        assert c.get("top_surface_line_width") == "0.22", (label, c.get("top_surface_line_width"))
        assert c.get("top_surface_speed", [""])[0] == "60", label
        assert c.get("skirt_loops") == "2" and c.get("initial_layer_speed", [""])[0] == "30", label
        assert c.get("curr_bed_type") == BED_TYPE, label
        assert c.get("textured_plate_temp") == [BED_TEMPS["textured_plate_temp"]] * 3, label
        for k in ("seam_gap", "min_bead_width", "wall_generator", "top_one_wall_type", "skirt_loops"):
            assert k in c["different_settings_to_system"][0], (label, k)
        m = z.read("Metadata/model_settings.config").decode()
        objs = re.findall(r'<object id="(\d+)">(.*?)</object>', m, re.S)
        assert len(objs) == 1, f"{label}: {len(objs)} objects"
        parts = re.findall(r"<part .*?</part>", objs[0][1], re.S)
        assert len(parts) == 3, f"{label}: {len(parts)} parts"
        ext = sorted(set(re.search(r'"extruder" value="(\d)"', pb).group(1) for pb in parts))
        assert ext == ["1", "2", "3"], f"{label}: extruders {ext}"
        assert len(re.findall(r"<model_instance>", m)) == 1, f"{label}: plate instance list"
os.remove(rt)
os.remove(raw)
print(f"OK  {os.path.basename(OUT)}: 1 object (W1 letters, plate center), "
      f"0.2 nozzle / 0.08 mm layers, locked recipe, tower {TOWER}, bed {BED_TYPE}")
