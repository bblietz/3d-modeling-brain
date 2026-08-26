"""Batch: one Bambu project 3MF per kid from roster.md (locked v3.14 design).

2026-08-25, C7 letter-tier recipe baked in (Brian's verdict on the thin 0.4
coupon plate; helpers in fillcore_mod.py): every tag object carries
  - a MODIFIER PART over the nine raised SANTA CRUZ banner letters
    (outlines + 0.3 mm, z over the five letter-only layers) with
    fm.C7_MOD_KEYS (wall_loops 1, top_one_wall_type all top, top and
    internal solid fill lines 0.3, infill_direction 90), and
  - the OBJECT key fm.C7_OBJECT_KEYS (detect_narrow_internal_solid_infill 0),
    injected through the CLI assemble list's assembled_params.print_params,
  - a second MODIFIER PART over the back inlay text (this kid's navy
    outlines + 0.5 mm, z 0.16..0.56 = layers 2-4) with fm.BACK_MOD_KEYS
    (internal_solid_infill_pattern concentric), which gives the name and
    number strokes back the concentric fill the object key takes away
    (F1a2, 2026-08-25; see fillcore_mod.py),
so the export goes through `--load-assemble-list` (pos_x/pos_y put the tag
at plate center) instead of `--assemble` + a build-item transform patch.
The wipe tower moves from the preset's (15, 220) to TOWER: with the 5 mm
brim the corner slot did not slice (see brief 2026-08-24 late), and since
2026-08-25 it sits beside the tag on the tag's own row (fm.check_tower:
closest free spot to the bed center, brim >= 12 mm from the disc, >= 15 mm
from the bed edges).

Output: projects/Sharks-nametag/final/sharks-nametag-<slug>.3mf (production,
since 2026-08-26; exports/ is only for coupons and experiments).
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
EXPORTS = f"{PROJ}/final"   # production output (2026-08-26); exports/ is the experiments area
PY = f"{VAULT}/.venv/bin/python"

ONLY = os.environ.get("ONLY")   # optional slug filter, e.g. ONLY=max-18 for the test file
CENTER = (128.0, 128.0)         # tag at plate center (bed 256 x 256, disc 76.2)
# Wipe tower (lower-left corner of the 43 x 43 mm rib-wall tower core; the
# 5 mm brim spans fm.BRIM_OFFSETS around it, 51.5 x 52.6 mm): left of the
# tag on its own row, brim x 26.3..77.8 / y 101.5..154.1, 12.1 mm from the
# disc edge (x 89.9) and 26 mm from the left bed edge. The preset's
# (15, 220) failed the offline slice with the brim; (105, 160) collides
# with the centered tag; (30, 180) (until 2026-08-25) sat in the back-left
# quadrant, the worst adhesion spot on this printer.
TOWER = (30, 106.5)
fm.check_tower(TOWER, [CENTER], "single")
N_LAYERS = 37                   # 0.12 mm layers, 0.2 mm first layer, tag 4.56 mm tall

# Bed temps follow the flattened filament preset (PETG Basic since
# 2026-08-08, flattens to the correct stock 70C). Caveat on any swap back
# to PLA: its flatten carried 55C and needed a hand-patch to 65 - verify
# the flattened temps against Bambu stock before trusting them.
BED_TEMPS = fm.read_bed_temps(f"{SCRATCH}/flat-filament.json")

os.makedirs(EXPORTS, exist_ok=True)

roster = []
with open(f"{PROJ}/roster.md") as f:
    for line in f:
        m = re.match(r"\s*([A-Za-z]+)\s*,\s*(\d+)", line)
        if m:
            roster.append((m.group(1), m.group(2)))
print(f"roster: {len(roster)} kids", flush=True)
ROSTER_N = 14   # 2026-08-24: Callan 17 added (was 13)
assert len(roster) == ROSTER_N, f"roster parse dropped kids: got {len(roster)}, expected {ROSTER_N}"
assert len({num for _, num in roster}) == len(roster), "duplicate jersey number in roster"
assert len({f"{n.lower()}-{num}" for n, num in roster}) == len(roster), "duplicate slug in roster"

# Letter-tier modifier (tag mm, shared by every kid: the banner text is
# constant, only the name and number change elsewhere on the disc).
G = fm.letter_geometry(fm.BANNER_BOX, 9, window_checks=False)
MOD_Z0, MOD_Z1, _n, TIER = fm.modifier_z_band(G["banner_top"], G["letter_top"], **fm.LAYERS_04)
assert _n == N_LAYERS and len(TIER) == 5, (_n, TIER)
MOD_C, MOD_CENTER = fm.centered(fm.extrude(fm.modifier_2d(G["letters"]), MOD_Z0, MOD_Z1))
assert MOD_C.is_watertight
MOD_NAME = "MOD banner letters C7: " + ", ".join(f"{k} {v}" for k, v in fm.C7_MOD_KEYS.items())
BACK_TIER = fm.check_back_band(**fm.LAYERS_04)   # back-text modifier band = inlay layers 2-4
LETTER_AREAS = sorted(round(p.area, 3) for p in G["letters"])
Z_MID = (G["banner_top"] + G["letter_top"]) / 2
print(f"modifier: 9 letters, z {MOD_Z0:.2f}..{MOD_Z1:.2f} over layer centers {TIER[0]:.2f}..{TIER[-1]:.2f} "
      f"({len(TIER)} of {N_LAYERS} layers), {len(MOD_C.faces)} faces; back text z {fm.BACK_Z0:.2f}..{fm.BACK_Z1:.2f} "
      f"over layer centers {BACK_TIER[0]:.2f}..{BACK_TIER[-1]:.2f} ({len(BACK_TIER)} layers); tower {TOWER}", flush=True)

failed = []
for name, num in roster:
    slug = f"{name.lower()}-{num}"
    if ONLY and slug != ONLY:
        continue
    out3mf = f"{EXPORTS}/sharks-nametag-{slug}.3mf"
    try:
        # pre-clean: a failed earlier run must never leave intermediates
        # this run could silently repackage
        for p in [f"{SCRATCH}/raw-{slug}.3mf", f"{SCRATCH}/rt-{slug}.3mf", f"{SCRATCH}/{slug}-assemble.json"] + \
                 [f"{SCRATCH}/{slug}-{c}.stl" for c in ("white", "navy", "cyan")]:
            if os.path.exists(p):
                os.remove(p)

        # pin the build env: DETAIL forced to crisp, SHOW/FINAL must not
        # leak in from the user's shell (viewer windows / canonical-STL
        # overwrites / full-detail geometry)
        env = dict(os.environ, KID_NAME=name.upper(), KID_NUMBER=num, SCRATCH=SCRATCH,
                   DETAIL="crisp")
        for k in ("SHOW", "FINAL"):
            env.pop(k, None)
        r = subprocess.run([PY, f"{PROJ}/sharks-nametag.py"], env=env,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, f"model build failed:\n{r.stdout}\n{r.stderr}"
        assert "all checks passed" in r.stdout and "(crisp)" in r.stdout

        stls = []
        for c in ("white", "navy", "cyan"):
            dst = f"{SCRATCH}/{slug}-{c}.stl"
            shutil.copy(f"{SCRATCH}/wip-{c}.stl", dst)
            stls.append(dst)
        # this kid's banner letters must be the canonical ones the modifier was cut from
        kid_white = trimesh.load(stls[0])
        _, white_c = fm.centered(kid_white)
        kid_letters = sorted(round(p.area, 3) for p in fm.section_polys(kid_white, Z_MID)
                             if box(*fm.BANNER_BOX).contains(p) and (p.bounds[2] - p.bounds[0]) < 10)
        assert kid_letters == LETTER_AREAS, f"banner letters differ from canonical: {kid_letters}"
        # back-text modifier from THIS kid's navy STL (name and number differ per kid)
        back_c, back_center = fm.centered(fm.extrude(fm.modifier_2d(fm.back_geometry(trimesh.load(stls[1])), fm.BACK_BUFFER),
                                                     fm.BACK_Z0, fm.BACK_Z1))
        assert back_c.is_watertight

        spec ={"plates": [{"plate_name": f"{name.upper()} {num}", "need_arrange": False,
                            "plate_params": {"curr_bed_type": BED_TYPE},
                            "objects": [{"path": p, "count": 1, "filaments": [fid], "assemble_index": [1],
                                         "pos_x": [CENTER[0]], "pos_y": [CENTER[1]], "pos_z": [0]}
                                        for p, fid in zip(stls, (1, 2, 3))],
                            "assembled_params": [{"assemble_index": 1, "print_params": fm.C7_OBJECT_KEYS}]}]}
        spec_path = f"{SCRATCH}/{slug}-assemble.json"
        with open(spec_path, "w") as f:
            json.dump(spec, f, indent=1)
        r = subprocess.run(
            ["bambu-studio", "--arrange", "0", "--load-assemble-list", spec_path,
             "--load-settings", f"{SCRATCH}/flat-machine.json;{SCRATCH}/flat-process.json",
             "--load-filaments", ";".join([f"{SCRATCH}/flat-filament.json"] * 3),
             "--export-3mf", f"raw-{slug}.3mf", "--outputdir", SCRATCH],
            capture_output=True, text=True, timeout=600, cwd=SCRATCH)
        assert r.returncode == 0, f"CLI compose rc={r.returncode}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
        raw = f"{SCRATCH}/raw-{slug}.3mf"
        assert os.path.exists(raw), f"CLI export missing:\n{r.stdout[-2000:]}"

        with zipfile.ZipFile(raw) as zin:
            cfg = json.loads(zin.read("Metadata/project_settings.config"))
            assert str(cfg.get("layer_height")) == "0.12"
            # Bed plate: the CLI defaults curr_bed_type to "Cool Plate"
            # (35C bed) - the 2026-08-07 test print peeled off the bed
            # mid-print. patch_config forces textured PEI + the filament
            # preset's stock temps, the dual-extruder flush block, the tower.
            fm.patch_config(cfg, BED_TEMPS, TOWER)
            model = zin.read("Metadata/model_settings.config").decode()
            model3d = zin.read("3D/3dmodel.model").decode()
            objfiles = {n: zin.read(n).decode() for n in zin.namelist() if n.startswith("3D/Objects/")}
            objs = re.findall(r'<object id="(\d+)">', model)
            assert len(objs) == 1, f"expected 1 object, got {objs}"
            oid = objs[0]
            model = model.replace('<metadata key="name" value="assemble_1"/>',
                                  f'<metadata key="name" value="{name.upper()} {num}"/>', 1) \
                         .replace(f'value="{slug}-white_1"', f'value="Sharks Nametag {name.upper()} {num}"') \
                         .replace(f'value="{slug}-navy_1"', 'value="navy artwork"') \
                         .replace(f'value="{slug}-cyan_1"', 'value="cyan artwork"')
            assert "assemble_" not in model and "_1\"" not in model
            opos = fm.object_pos(model3d, oid, white_c)
            assert opos == (CENTER[0], CENTER[1], 0.0), f"object not at plate center: {opos}"
            m_ = re.search(rf'<object id="{oid}">.*?</object>', model, re.S)
            block, model3d = fm.inject_modifier(m_.group(0), model3d, objfiles, oid, fm.next_object_id(model3d, objfiles),
                                                MOD_NAME, "mod-banner-letters-C7.stl", MOD_C, MOD_CENTER, opos, fm.C7_MOD_KEYS)
            block, model3d = fm.inject_modifier(block, model3d, objfiles, oid, fm.next_object_id(model3d, objfiles),
                                                fm.BACK_MOD_NAME, "mod-back-text.stl", back_c, back_center, opos, fm.BACK_MOD_KEYS)
            model = model[:m_.start()] + block + model[m_.end():]
            with zipfile.ZipFile(out3mf, "w", zipfile.ZIP_DEFLATED) as zout:
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

        rt = f"{SCRATCH}/rt-{slug}.3mf"
        r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", rt, out3mf],
                           capture_output=True, text=True, timeout=600, cwd=SCRATCH)
        assert r.returncode == 0, f"CLI round trip rc={r.returncode}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
        for path, label in ((out3mf, "out"), (rt, "round trip")):
            with zipfile.ZipFile(path) as z:
                c2 = json.loads(z.read("Metadata/project_settings.config"))
                assert c2.get("filament_colour") == COLORS, f"{label}: colors lost"
                assert "ironing_type" in c2.get("different_settings_to_system", [""])[0]
                # coupon C recipe (2026-08-22)
                assert c2.get("ironing_type") == "no ironing", f"ironing back on: {c2.get('ironing_type')}"
                assert c2.get("top_one_wall_type") == "not apply", "2 top walls lost"
                assert c2.get("top_surface_speed", [""])[0] == "60", "top speed lost"
                assert "top_one_wall_type" in c2["different_settings_to_system"][0], "top_one_wall_type not in diff list"
                assert c2.get("wall_generator") == "arachne", "wall generator lost"
                assert c2.get("skirt_loops") == "2" and c2.get("initial_layer_speed", [""])[0] == "30", "first-layer fixes lost"
                assert "skirt_loops" in c2["different_settings_to_system"][0], "skirt not in diff list"
                assert "wall_generator" in c2["different_settings_to_system"][0], "wall_generator not in diff list"
                assert c2.get("curr_bed_type") == BED_TYPE, "bed type lost"
                assert c2.get("textured_plate_temp") == [BED_TEMPS["textured_plate_temp"]] * 3, "bed temp lost"
                fm.check_config(c2, BED_TEMPS, TOWER, label=label)
                for k in SMOOTH_KEYS:
                    assert k in c2["different_settings_to_system"][0].split(";"), f"{label}: {k} not in diff list"
                m2 = z.read("Metadata/model_settings.config").decode()
                assert set(re.findall(r'"extruder" value="(\d)"', m2)) >= {"1", "2", "3"}
                objs2 = re.findall(r'<object id="(\d+)">(.*?)</object>', m2, re.S)
                assert len(objs2) == 1, f"{label}: {len(objs2)} objects"
                nn, nmod = fm.check_object(objs2[0][1], fm.C7_OBJECT_KEYS, [fm.C7_MOD_KEYS, fm.BACK_MOD_KEYS], ["1", "2", "3"], label)
                assert (nn, nmod) == (3, 2), (label, nn, nmod)
                m3 = z.read("3D/3dmodel.model").decode()
                assert len(re.findall(r"<component ", m3)) == 5, f"{label}: components"
                tf = re.search(r'<item [^>]*transform="([^"]*)"', m3).group(1).split()
                pos2 = fm.object_pos(m3, objs2[0][0], white_c)
                got = (round(float(tf[9]) + pos2[0], 4), round(float(tf[10]) + pos2[1], 4))
                assert got == CENTER, f"{label}: centering lost: {got}"
        for p in stls + [raw, rt, spec_path]:
            os.remove(p)
        print(f"OK  {name.upper()} {num} -> {os.path.basename(out3mf)}", flush=True)
    except Exception as e:
        failed.append(slug)
        print(f"FAIL {slug}: {e}", flush=True)

_n = len([1 for n_, k_ in roster if not ONLY or f"{n_.lower()}-{k_}" == ONLY])
print(f"done: {_n - len(failed)}/{_n} ok" + (f", FAILED: {failed}" if failed else ""), flush=True)
sys.exit(1 if failed else 0)
