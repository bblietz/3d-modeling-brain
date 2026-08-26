"""Coupon plate: crop windows of the canonical tag (white/navy/cyan STLs)
onto a thin slab and lay several settings VARIANTS side by side, EACH
VARIANT ITS OWN OBJECT with object-level settings, so one short print
compares recipes.

Why objects, not parts: seam_gap, wall_distribution_count,
wall_transition_*, min_bead_width are PrintObjectConfig keys in Bambu
(src/libslic3r/PrintConfig.hpp); per-PART (volume) metadata only carries
PrintRegionConfig keys (speeds, flow, line widths, ironing, walls), so a
one-object/many-parts plate silently ignores the object-level ones. The
CLI assembler (`--load-assemble-list`, see plates.py) makes one object per
`assemble_index` and applies `assembled_params[].print_params` as that
object's config.

2026-08-23 variants = the "solid white text" candidates (Brian: SANTA
CRUZ, CITY, stars and ball patches show gaps; toolpath analysis via
top_coverage.py: the letter tops are 100% arachne wall beads, so the marks
are loop starts/ends (aligned seams stack at the same corners through all
5 layers), bead transitions and 250 mm/s gap fill, not missing paths):
  O  control: the current recipe, no overrides
  P  seam_gap 0%, small loops (radius < 10 mm) at 30 mm/s, gap fill 40
  Q  P + arachne smoothing (wall_distribution_count 3, transition filter
     deviation 50%)
  R  Q + 3% more flow (print_flow_ratio 1.03)
Windows: W1 = S-A-N-T-A + CITY left + ball bottom + surfer (model x -22..4,
y -17..11); W2 = the 5 top band stars (x -14..14, y 16..26). Slab = 1.0 mm
of white under the art.

Run: `.venv/bin/python projects/Sharks-nametag/pipeline/coupons.py`
-> exports/solid-text-coupons.3mf (CLI round trip verified; exports/ is the
experiments area, recreated on demand, final/ holds the production files). Brian opens
it in Studio, checks O P Q R left to right, slices, prints (~1.5 h).
"""
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
WORK = f"{SCRATCH}/coupon-stl"
OUT = f"{PROJ}/exports/solid-text-coupons.3mf"   # experiments area (recreated on demand); production files live in final/
os.makedirs(os.path.dirname(OUT), exist_ok=True)
COLORS = ["#FFFFFF", "#00395E", "#31BAD6"]
BED_TYPE = "Textured PEI Plate"
TOWER = (12, 203)          # back-left, clear of the coupons (they sit at y 94..141)
SMOOTH_KEYS = ["ironing_type", "top_one_wall_type",   # keep in sync with batch_roster.py
               "top_surface_line_width", "top_shell_layers", "top_surface_speed",
               "sparse_infill_density", "sparse_infill_pattern", "wall_generator",
               "seam_gap", "small_perimeter_speed", "small_perimeter_threshold",
               "gap_infill_speed", "wall_distribution_count", "wall_transition_filter_deviation",
               "min_feature_size", "min_bead_width",
               "skirt_loops", "skirt_distance", "skirt_height", "initial_layer_speed",
               "initial_layer_infill_speed",
               "prime_tower_brim_width"]
UNDER_ART = 1.0   # mm of white slab under the art

P_KEYS = {"seam_gap": "0%", "small_perimeter_speed": "30", "small_perimeter_threshold": "10",
          "gap_infill_speed": "40"}
Q_KEYS = dict(P_KEYS, wall_distribution_count="3", wall_transition_filter_deviation="50%")
R_KEYS = dict(Q_KEYS, print_flow_ratio="1.03")
VARIANTS = [("O", "control current recipe", {}),
            ("P", "seam0 slow-small gap40", P_KEYS),
            ("Q", "P + arachne smooth", Q_KEYS),
            ("R", "Q + flow 1.03", R_KEYS)]
VARIANT_X = {"O": 38.0, "P": 98.0, "Q": 158.0, "R": 218.0}     # plate x of each variant's center
WINDOWS = {"W1": (-22, 4, -17, 11), "W2": (-14, 14, 16, 26)}   # model x0,x1,y0,y1
WINDOW_Y = {"W1": 108.0, "W2": 136.0}                          # plate y of each window's center
COLOR_IDS = {"white": 1, "navy": 2, "cyan": 3}

with open(f"{SCRATCH}/flat-filament.json") as f:
    _fil = json.load(f)
BED_TEMPS = {k: _fil[k][0] for k in ("textured_plate_temp", "textured_plate_temp_initial_layer")}

os.makedirs(WORK, exist_ok=True)
meshes = {c: trimesh.load(f"{PROJ}/sharks-nametag-{c}.stl") for c in COLOR_IDS}
zs = sorted(set(np.round(meshes["white"].vertices[:, 2], 2)))
top = max(zs)
base_top = max(z for z in zs if z < top - 0.5)
z_cut = base_top - UNDER_ART
print(f"canonical STLs: white top {top}, disc top {base_top} -> slab cut at z {z_cut}")

# sanity: W2 must hold stars (navy holes of star size at the band level)
sec = meshes["navy"].section(plane_origin=[0, 0, base_top + 0.3], plane_normal=[0, 0, 1])
p2, _ = sec.to_2D(to_2D=np.eye(4))
stars = [(Polygon(r).centroid.x, Polygon(r).centroid.y) for p in p2.polygons_full for r in p.interiors
         if 2 < Polygon(r).area < 12]
x0, x1, y0, y1 = WINDOWS["W2"]
in_w2 = [s for s in stars if x0 + 1 < s[0] < x1 - 1 and y0 + 1 < s[1] < y1 - 1]
print(f"star-sized navy holes: {len(stars)}, inside W2: {len(in_w2)}")
assert len(in_w2) >= 3, "W2 does not contain enough stars"


def crop(mesh, x0, x1, y0, y1, zc):
    m = mesh.copy()
    # z cut FIRST: slicing the flat bottom last leaves the cap open
    for n, o in (((0, 0, 1), (0, 0, zc)), ((1, 0, 0), (x0, 0, 0)), ((-1, 0, 0), (x1, 0, 0)),
                 ((0, 1, 0), (0, y0, 0)), ((0, -1, 0), (0, y1, 0))):
        m = trimesh.intersections.slice_mesh_plane(m, plane_normal=n, plane_origin=o, cap=True)
        if m is None or m.is_empty:
            return None
    m.merge_vertices()
    m.fix_normals()
    return m


# cropped parts, each centered on its window center at z 0 (positions go
# in the assemble list, plate-relative)
objects, part_names = [], {}       # part_names: stl base -> friendly part name
for idx, (vlabel, vdesc, keys) in enumerate(VARIANTS, start=1):
    for wname, (x0, x1, y0, y1) in WINDOWS.items():
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for color, fid in COLOR_IDS.items():
            m = crop(meshes[color], x0, x1, y0, y1, z_cut)
            if m is None:
                continue
            assert m.is_watertight, f"{vlabel} {wname} {color} not watertight"
            m.apply_translation([-cx, -cy, -z_cut])
            base = f"{vlabel}-{wname}-{color}"
            m.export(f"{WORK}/{base}.stl")
            objects.append({"path": f"{WORK}/{base}.stl", "count": 1, "filaments": [fid], "assemble_index": [idx],
                            "pos_x": [VARIANT_X[vlabel]], "pos_y": [WINDOW_Y[wname]], "pos_z": [0]})
            part_names[base] = f"{vlabel} {wname} {color}"
spec = {"plates": [{"plate_name": "Solid text coupons O P Q R", "need_arrange": False,
                    "plate_params": {"curr_bed_type": BED_TYPE}, "objects": objects,
                    "assembled_params": [{"assemble_index": i, "print_params": keys}
                                         for i, (_, _, keys) in enumerate(VARIANTS, start=1) if keys]}]}
spec_path = f"{SCRATCH}/coupons-assemble.json"
with open(spec_path, "w") as f:
    json.dump(spec, f, indent=1)
print(f"{len(objects)} cropped parts in {len(VARIANTS)} objects")

raw = f"{SCRATCH}/raw-coupons.3mf"
rt = f"{SCRATCH}/rt-coupons.3mf"
for p in (raw, rt):
    if os.path.exists(p):
        os.remove(p)
r = subprocess.run(
    ["bambu-studio", "--arrange", "0", "--load-assemble-list", spec_path,
     "--load-settings", f"{SCRATCH}/flat-machine.json;{SCRATCH}/flat-process.json",
     "--load-filaments", ";".join([f"{SCRATCH}/flat-filament.json"] * 3),
     "--export-3mf", os.path.basename(raw), "--outputdir", SCRATCH],
    capture_output=True, text=True, timeout=900, cwd=SCRATCH)
assert r.returncode == 0, f"CLI assemble rc={r.returncode}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"

with zipfile.ZipFile(raw) as zin:
    cfg = json.loads(zin.read("Metadata/project_settings.config"))
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
    # Flush block in the DUAL-EXTRUDER shape (2026-08-23): our old 16-entry
    # 4-filament placeholder made Studio expand to 2 extruders x 3 filaments
    # by reading uninitialized memory (denormals/NaN in Brian's saves ->
    # "Failed to serialize flush_volumes_matrix, Serializing NaN" on slice).
    # Two 3x3 blocks, 0 diagonal, 280 placeholder; Studio recalculates real
    # values from the colors.
    _m = ["0", "280", "280", "280", "0", "280", "280", "280", "0"]
    cfg["flush_volumes_matrix"] = _m + _m
    cfg["flush_volumes_vector"] = ["140"] * 6
    cfg["flush_multiplier"] = ["1", "1"]
    cfg["flush_multiplier_fast"] = ["1.2", "1.2"]
    cfg["nozzle_flush_dataset"] = ["1", "2", "2", "1", "2", "2"]
    cfg["wipe_tower_x"] = [str(TOWER[0])]
    cfg["wipe_tower_y"] = [str(TOWER[1])]

    model = zin.read("Metadata/model_settings.config").decode()
    # objects come out as "assemble_N": name them by variant; parts "<stl>_1"

    def _rename(block):
        m_ = re.search(r'value="([OPQR])-W\d-[a-z]+_1"', block)
        assert m_, block[:200]
        v = m_.group(1)
        desc = next(d for l, d, _ in VARIANTS if l == v)
        block = re.sub(r'<metadata key="name" value="assemble_\d+"/>',
                       f'<metadata key="name" value="coupon {v} - {desc}"/>', block, count=1)
        for base, friendly in part_names.items():
            block = block.replace(f'value="{base}_1"', f'value="{friendly}"')
        return block
    model, n_obj = re.subn(r"<object id=\"\d+\">.*?</object>", lambda m_: _rename(m_.group(0)), model, flags=re.S)
    assert n_obj == len(VARIANTS), n_obj
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
        assert c.get("ironing_type") == "no ironing" and c.get("top_one_wall_type") == "not apply", label
        assert c.get("curr_bed_type") == BED_TYPE, label
        m = z.read("Metadata/model_settings.config").decode()
        objs = re.findall(r'<object id="(\d+)">(.*?)</object>', m, re.S)
        assert len(objs) == len(VARIANTS), f"{label}: {len(objs)} objects"
        for oid, body in objs:
            nm = re.search(r'<metadata key="name" value="([^"]*)"', body).group(1)
            v = nm.split()[1]
            keys = next(k for l, _, k in VARIANTS if l == v)
            head = body.split("<part ", 1)[0]          # object-level metadata only
            for k, val in keys.items():
                assert f'<metadata key="{k}" value="{val}"/>' in head, f"{label}: object {nm} lost {k}"
            if not keys:
                assert "seam_gap" not in head and "small_perimeter_speed" not in head, f"{label}: control has overrides"
            parts = re.findall(r"<part .*?</part>", body, re.S)
            assert len(parts) == 6, f"{label}: {nm} has {len(parts)} parts"
            ext = sorted(set(re.search(r'"extruder" value="(\d)"', pb).group(1) for pb in parts))
            assert ext == ["1", "2", "3"], f"{label}: {nm} extruders {ext}"
        assert len(re.findall(r"<model_instance>", m)) == len(VARIANTS), f"{label}: plate instance list"
os.remove(rt)
os.remove(raw)
print(f"OK  {os.path.basename(OUT)}: {len(VARIANTS)} objects (left to right " +
      " ".join(l for l, _, _ in VARIANTS) + f"), tower {TOWER}, bed {BED_TYPE}")
for l, d, keys in VARIANTS:
    print(f"    {l}: {d}" + (f"  {keys}" if keys else ""))
