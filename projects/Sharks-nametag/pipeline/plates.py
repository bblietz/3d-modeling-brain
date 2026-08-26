"""Two-plate roster project: all 14 tags in ONE Bambu project 3MF, 6 on
plate 1 and the other 8 on plate 2 (Brian 2026-08-22, "create a project
file with roster using 2 plates").

Route: the Bambu CLI's own multi-plate assembler (`--load-assemble-list`,
schema from src/BambuStudio.hpp: plates[] -> plate_name, need_arrange,
plate_params, objects[] -> path, count, filaments, assemble_index,
pos_x/y/z, assembled_params[] -> assemble_index, print_params). With
need_arrange false the CLI translates each plate's objects by that plate's
origin itself (plate 2 sits at x = 307.2), so positions below are
plate-relative mm. No input files may be passed with the assemble list,
and --load-filament-ids is per input file, so it is omitted (filaments
come from the JSON). Everything else (colors, diff list, bed type + temps,
names, the C7 letter-tier modifier + object key + the per-kid back-text
modifier from fillcore_mod.py, 2026-08-25) is the same post-patch as
batch_roster.py.

Layout (bed 256 x 256, disc 76.2): a 3 x 3 grid with centers 46/128/210
(7.9 mm edge margin for the 3 mm skirt, 5.8 mm between discs). The
back-left slot stays EMPTY on both plates for the wipe tower. Tower
placement (Brian 2026-08-25, "the part takes priority"): tags keep their
slots, the tower goes to the free spot closest to the bed center with its
5 mm brim >= 12 mm from every disc and >= 15 mm from the bed edges
(fm.check_tower, footprint from the MAX 18 graft slice: 43 x 43 mm core,
51.5 x 52.6 mm brim). Plate A (whole back row free): behind the middle
disc, TOWERS[0]. Plate B: the back-left cell, pushed toward the center,
TOWERS[1]. The old corner pin (12, 203) put the tower on the plate edge
where a brimless one peeled (2026-08-24).

Run: `.venv/bin/python projects/Sharks-nametag/pipeline/plates.py`
(env REUSE_STL=1 to reuse pipeline/plates-stl/*.stl from a previous run
instead of rebuilding the 14 models, ~6 min; OUT=<path.3mf> to write
somewhere other than final/sharks-nametag-roster-plates.3mf, the
production file since 2026-08-26, e.g. a dry run; exports/ is only for
coupons and experiments).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

import trimesh
from shapely.geometry import box

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fillcore_mod as fm  # noqa: E402
from fillcore_mod import VAULT, PROJ, COLORS, BED_TYPE, SMOOTH_KEYS  # noqa: E402

SCRATCH = os.path.dirname(os.path.abspath(__file__))
STL_DIR = f"{SCRATCH}/plates-stl"
OUT = os.environ.get("OUT", f"{PROJ}/final/sharks-nametag-roster-plates.3mf")   # production output (2026-08-26); exports/ is the experiments area
PY = f"{VAULT}/.venv/bin/python"
REUSE_STL = os.environ.get("REUSE_STL") == "1"

GRID = [46, 128, 210]
SLOTS6 = [(x, y) for y in GRID[:2] for x in GRID]          # front + middle rows
SLOTS7 = SLOTS6 + [(GRID[1], GRID[2])]                       # + back-middle
SLOTS8 = SLOTS7 + [(GRID[2], GRID[2])]                       # + back-right (back-left stays free for the tower)
TOWERS = [(106, 183.5),                                      # plate A: back-middle cell, brim 12.4 mm behind the center disc
          (30, 183.5)]                                       # plate B: back-left cell, brim 12.1 / 12.4 mm from the back-middle / middle-left discs
PLATE2_X = 307.2                                             # CLI plate stride (256 * 1.2)
COLOR_PARTS = (("white", 1), ("navy", 2), ("cyan", 3))
N_LAYERS = 37

BED_TEMPS = fm.read_bed_temps(f"{SCRATCH}/flat-filament.json")

roster = []
with open(f"{PROJ}/roster.md") as f:
    for line in f:
        m = re.match(r"\s*([A-Za-z]+)\s*,\s*(\d+)", line)
        if m:
            roster.append((m.group(1), m.group(2)))
ROSTER_N = 14   # 2026-08-24: Callan 17 added (was 13); plate A keeps 6, plate B takes the rest (max 8: the back-left slot is the tower)
assert len(roster) == ROSTER_N, f"roster parse dropped kids: got {len(roster)}, expected {ROSTER_N}"
assert len({f"{n.lower()}-{num}" for n, num in roster}) == ROSTER_N, "duplicate slug in roster"
slug_of = {(n, num): f"{n.lower()}-{num}" for n, num in roster}
plates = [("A", roster[:6], SLOTS6), ("B", roster[6:], SLOTS8)]
for _lbl, _kids, _slots in plates:
    assert len(_kids) <= len(_slots), f"plate {_lbl}: {len(_kids)} tags for {len(_slots)} slots"
assert len(plates[1][1]) == 8
for (_lbl, _kids, _slots), _tw in zip(plates, TOWERS):
    fm.check_tower(_tw, _slots[:len(_kids)], f"plate {_lbl}")

# Letter-tier modifier (tag mm, shared by every kid: the banner text is constant)
G = fm.letter_geometry(fm.BANNER_BOX, 9, window_checks=False)
MOD_Z0, MOD_Z1, _n, TIER = fm.modifier_z_band(G["banner_top"], G["letter_top"], **fm.LAYERS_04)
assert _n == N_LAYERS and len(TIER) == 5, (_n, TIER)
MOD_C, MOD_CENTER = fm.centered(fm.extrude(fm.modifier_2d(G["letters"]), MOD_Z0, MOD_Z1))
assert MOD_C.is_watertight
MOD_NAME = "MOD banner letters C7: " + ", ".join(f"{k} {v}" for k, v in fm.C7_MOD_KEYS.items())
fm.check_back_band(**fm.LAYERS_04)   # back-text modifier band = inlay layers 2-4
LETTER_AREAS = sorted(round(p.area, 3) for p in G["letters"])
Z_MID = (G["banner_top"] + G["letter_top"]) / 2

# ---------------------------------------------------------------- STLs
os.makedirs(STL_DIR, exist_ok=True)
for name, num in roster:
    slug = slug_of[(name, num)]
    paths = [f"{STL_DIR}/{slug}-{c}.stl" for c, _ in COLOR_PARTS]
    if REUSE_STL and all(os.path.exists(p) for p in paths):
        continue
    env = dict(os.environ, KID_NAME=name.upper(), KID_NUMBER=num, SCRATCH=SCRATCH,
               DETAIL="crisp")
    for k in ("SHOW", "FINAL"):
        env.pop(k, None)
    r = subprocess.run([PY, f"{PROJ}/sharks-nametag.py"], env=env,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, f"model build failed for {slug}:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
    assert "all checks passed" in r.stdout and "(crisp)" in r.stdout
    for (c, _), dst in zip(COLOR_PARTS, paths):
        shutil.copy(f"{SCRATCH}/wip-{c}.stl", dst)
    print(f"STL  {name.upper()} {num}", flush=True)

# per kid: the white part's bbox center (the object-position anchor), the
# banner letters must be the canonical ones the modifier was cut from, and
# the back-text modifier mesh from this kid's navy STL (name and number differ)
white_center, back_mod = {}, {}
for name, num in roster:
    slug = slug_of[(name, num)]
    w = trimesh.load(f"{STL_DIR}/{slug}-white.stl")
    _, white_center[slug] = fm.centered(w)
    areas = sorted(round(p.area, 3) for p in fm.section_polys(w, Z_MID)
                   if box(*fm.BANNER_BOX).contains(p) and (p.bounds[2] - p.bounds[0]) < 10)
    assert areas == LETTER_AREAS, f"{slug}: banner letters differ from canonical: {areas}"
    back_mod[slug] = fm.centered(fm.extrude(fm.modifier_2d(fm.back_geometry(trimesh.load(f"{STL_DIR}/{slug}-navy.stl")), fm.BACK_BUFFER),
                                            fm.BACK_Z0, fm.BACK_Z1))
    assert back_mod[slug][0].is_watertight, slug

# ------------------------------------------------------- assemble list
spec = {"plates": []}
for label, kids, slots in plates:
    objects = []
    for idx, ((name, num), (x, y)) in enumerate(zip(kids, slots), start=1):
        slug = slug_of[(name, num)]
        for c, fil in COLOR_PARTS:
            objects.append({"path": f"{STL_DIR}/{slug}-{c}.stl", "count": 1,
                            "filaments": [fil], "assemble_index": [idx],
                            "pos_x": [x], "pos_y": [y], "pos_z": [0]})
    spec["plates"].append({
        # letters and spaces only: a ":" in the name made the CLI write an
        # empty plater_name (2026-08-22)
        "plate_name": f"Plate {label} " + " ".join(n.capitalize() for n, _ in kids),
        "need_arrange": False,
        "plate_params": {"curr_bed_type": BED_TYPE},
        "objects": objects,
        "assembled_params": [{"assemble_index": i, "print_params": fm.C7_OBJECT_KEYS}
                             for i in range(1, len(kids) + 1)]})
os.makedirs(os.path.dirname(OUT), exist_ok=True)
spec_path = f"{SCRATCH}/plates-assemble.json"
with open(spec_path, "w") as f:
    json.dump(spec, f, indent=1)

raw = f"{SCRATCH}/raw-plates.3mf"
rt = f"{SCRATCH}/rt-plates.3mf"
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
assert os.path.exists(raw), f"CLI export missing:\n{r.stdout[-2000:]}"

# ----------------------------------------------------------- post-patch
with zipfile.ZipFile(raw) as zin:
    cfg = json.loads(zin.read("Metadata/project_settings.config"))
    assert str(cfg.get("layer_height")) == "0.12"
    fm.patch_config(cfg, BED_TEMPS, TOWERS, n_plates=2)

    model = zin.read("Metadata/model_settings.config").decode()
    model3d = zin.read("3D/3dmodel.model").decode()
    objfiles = {n: zin.read(n).decode() for n in zin.namelist() if n.startswith("3D/Objects/")}
    next_id = fm.next_object_id(model3d, objfiles)

    # object "assemble_N" -> "NAME NUM" (what the printer lists for skip
    # object), parts -> the same friendly names as the per-kid files,
    # plus the letter-tier modifier part per object
    def _rename(block):
        m = re.search(r'value="([a-z]+-\d+)-white_1"', block)
        assert m, block[:300]
        slug = m.group(1)
        name, num = slug.rsplit("-", 1)
        block = re.sub(r'<metadata key="name" value="assemble_\d+"/>',
                       f'<metadata key="name" value="{name.upper()} {num}"/>', block, count=1)
        block = block.replace(f'value="{slug}-white_1"', f'value="Sharks Nametag {name.upper()} {num}"') \
                     .replace(f'value="{slug}-navy_1"', 'value="navy artwork"') \
                     .replace(f'value="{slug}-cyan_1"', 'value="cyan artwork"')
        return block, slug
    out_blocks, pos, n_obj = [], 0, 0
    for m_ in re.finditer(r'<object id="(\d+)">.*?</object>', model, re.S):
        out_blocks.append(model[pos:m_.start()])
        block, slug = _rename(m_.group(0))
        oid = m_.group(1)
        opos = fm.object_pos(model3d, oid, white_center[slug])
        assert opos[2] == 0.0 and (opos[0], opos[1]) in {(float(x), float(y)) for x, y in SLOTS8}, (slug, opos)
        block, model3d = fm.inject_modifier(block, model3d, objfiles, oid, next_id, MOD_NAME, "mod-banner-letters-C7.stl",
                                            MOD_C, MOD_CENTER, opos, fm.C7_MOD_KEYS)
        next_id += 1
        block, model3d = fm.inject_modifier(block, model3d, objfiles, oid, next_id, fm.BACK_MOD_NAME, "mod-back-text.stl",
                                            back_mod[slug][0], back_mod[slug][1], opos, fm.BACK_MOD_KEYS)
        next_id += 1
        out_blocks.append(block)
        pos = m_.end()
        n_obj += 1
    out_blocks.append(model[pos:])
    model = "".join(out_blocks)
    assert n_obj == ROSTER_N, f"expected {ROSTER_N} objects in model_settings, got {n_obj}"
    assert "assemble_" not in model and "_1\"" not in model

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "Metadata/project_settings.config":
                zout.writestr(item, json.dumps(cfg, indent=4))
            elif item.filename == "Metadata/model_settings.config":
                zout.writestr(item, model)
            elif item.filename == "3D/3dmodel.model":
                zout.writestr(item, model3d)
            elif item.filename in objfiles:
                zout.writestr(item, objfiles[item.filename])
            else:
                zout.writestr(item, zin.read(item.filename))

# --------------------------------------------------------------- verify
r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", rt, OUT],
                   capture_output=True, text=True, timeout=900, cwd=SCRATCH)
assert r.returncode == 0, f"CLI round trip rc={r.returncode}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"


def check(path, label):
    with zipfile.ZipFile(path) as z:
        c = json.loads(z.read("Metadata/project_settings.config"))
        fm.check_config(c, BED_TEMPS, TOWERS, n_plates=2, label=label)
        m = z.read("Metadata/model_settings.config").decode()
        objs = re.findall(r'<object id="(\d+)">(.*?)</object>', m, re.S)
        assert len(objs) == ROSTER_N, f"{label}: {len(objs)} objects"
        names = {}
        for oid, body in objs:
            nm = re.search(r'<metadata key="name" value="([^"]*)"', body).group(1)
            # part-level extruders (the CLI round trip also adds an
            # object-level default extruder 1, which is fine), the object
            # key in the head, 3 normal parts + the letter and back-text modifiers
            nn, nmod = fm.check_object(body, fm.C7_OBJECT_KEYS, [fm.C7_MOD_KEYS, fm.BACK_MOD_KEYS], ["1", "2", "3"], label)
            assert (nn, nmod) == (3, 2), f"{label}: {nm} parts {nn} + {nmod} modifiers"
            names[oid] = nm
        assert sorted(names.values()) == sorted(f"{n.upper()} {num}" for n, num in roster), f"{label}: names {names}"
        plate_blocks = re.findall(r"<plate>(.*?)</plate>", m, re.S)
        assert len(plate_blocks) == 2, f"{label}: {len(plate_blocks)} plates"
        pnames = [re.search(r'"plater_name" value="([^"]*)"', pb).group(1) for pb in plate_blocks]
        assert pnames == [p["plate_name"] for p in spec["plates"]], f"{label}: plate names {pnames}"
        assert all('"bed_type" value="Textured PEI Plate"' in pb for pb in plate_blocks), f"{label}: per-plate bed type"
        per_plate = []
        for pb in plate_blocks:
            ids = re.findall(r'"object_id" value="(\d+)"', pb)
            per_plate.append(sorted(names[i] for i in ids))
        assert [len(p) for p in per_plate] == [6, 8], f"{label}: plate membership {per_plate}"
        want = [sorted(f"{n.upper()} {num}" for n, num in kids) for _, kids, _ in plates]
        assert per_plate == want, f"{label}: plate membership {per_plate}"
        # Geometry = build item transform x component transform in
        # 3D/3dmodel.model (bbs_3mf.cpp: the component transform becomes the
        # volume transformation; the model_settings part "matrix" is only
        # stored as source.transform bookkeeping and the exporter writes
        # volume x source back, so a CLI round trip doubles it - ignore it).
        # Plate 1 items sit at x 0, plate 2 at the CLI stride.
        main = z.read("3D/3dmodel.model").decode()
        items = re.findall(r'<item objectid="(\d+)"[^>]*transform="([^"]*)"', main)
        assert len(items) == ROSTER_N, f"{label}: {len(items)} build items"
        comps = dict(re.findall(r'<object id="(\d+)"[^>]*>\s*<components>(.*?)</components>', main, re.S))
        pos_by_name = {}
        for oid, tf in items:
            it = tf.split()
            nm = names[oid]
            slug = f"{nm.split()[0].lower()}-{nm.split()[1]}"
            assert len(re.findall(r"<component ", comps[oid])) == 5, f"{label}: object {oid} components"
            op = fm.object_pos(main, oid, white_center[slug])
            pos_by_name[nm] = (float(it[9]) + op[0], float(it[10]) + op[1])
        for (label_, kids, slots), base_x in zip(plates, (0.0, PLATE2_X)):
            for (n, num), (x, y) in zip(kids, slots):
                got = pos_by_name[f"{n.upper()} {num}"]
                assert abs(got[0] - (base_x + x)) < 0.01 and abs(got[1] - y) < 0.01, \
                    f"{label}: {n} {num} at {got}, wanted ({base_x + x}, {y})"
        return per_plate


check(OUT, "out")
per_plate = check(rt, "round trip")
os.remove(rt)
os.remove(raw)
print(f"OK  {OUT}")
for (label, kids, slots), members in zip(plates, per_plate):
    print(f"    plate {label}: {len(members)} tags (3 parts + 2 modifiers, letters and back text, each): "
          + ", ".join(f"{n.upper()} {num}@({x},{y})" for (n, num), (x, y) in zip(kids, slots)))
print(f"    wipe tower plate A {TOWERS[0]}, plate B {TOWERS[1]}; bed {BED_TYPE} {BED_TEMPS['textured_plate_temp']}C; colors {COLORS}; "
      f"letter modifier z {MOD_Z0:.2f}..{MOD_Z1:.2f} + object key {fm.C7_OBJECT_KEYS} "
      f"+ back-text modifier z {fm.BACK_Z0:.2f}..{fm.BACK_Z1:.2f} {fm.BACK_MOD_KEYS}")
