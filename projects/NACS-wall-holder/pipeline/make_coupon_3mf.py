"""Bambu Studio print 3MF for the NACS holder fit coupon (coupon.stl) in PETG, verified by a real slice.

Adapted from projects/NACS-organizer/make_plate.py (same X2D 0.6 nozzle, 0.30mm
Standard, Bambu PETG Basic, Textured PEI, Sharks PETG lessons), plus supports
for the cavity roof: tree supports with Bambu Support For PLA/PETG as the
interface material on the X2D's second (Bowden) nozzle, using Bambu's own
recommended parameters for that pairing (support_recommended_params.json).

Usage:  .venv/bin/python projects/NACS-wall-holder/pipeline/make_coupon_3mf.py [stem]      (default stem: coupon)
Reads <stem>.stl; writes <stem>-print.3mf and <stem>-slice.json, and prints real minutes and grams per filament.
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
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline"))
from graft_slice import graft_slice  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudioBeta/system/BBL")

MACHINE = "Bambu Lab X2D 0.6 nozzle"
PROCESS = "0.30mm Standard @BBL X2D 0.6 nozzle"
FILAMENTS = ["Bambu PETG Basic @BBL X2D", "Bambu Support For PLA/PETG @BBL X2D"]   # 1 = model, 2 = support interface
FILAMENT_MAP = ["1", "2"]   # extruder per filament: 1 = direct drive (main), 2 = Bowden (support)
FILAMENT_COLOUR = ["#00AE42", "#FFFFFF"]   # preview only; the AMS sync replaces these on open
FILAMENT_NOZZLE_MAP = ["1", "2"]
# Filament keys Studio stores once per (filament, extruder variant): a GUI-saved X2D config has
# filaments x 6 entries for these, in the machine's printer_extruder_variant order. The CLI writes
# only the first variant per filament, and the slicer then cannot find the Bowden variant of a
# filament mapped to extruder 2 ("could not found extruder_type Bowden ... filament_index 2").
PER_VARIANT_KEYS = [
    "filament_adaptive_volumetric_speed", "filament_bridge_speed", "filament_cooling_before_tower",
    "filament_deretraction_speed", "filament_enable_overhang_speed", "filament_flow_ratio", "filament_flush_temp",
    "filament_flush_volumetric_speed", "filament_long_retractions_when_cut", "filament_max_volumetric_speed",
    "filament_overhang_1_4_speed", "filament_overhang_2_4_speed", "filament_overhang_3_4_speed",
    "filament_overhang_4_4_speed", "filament_overhang_totally_speed", "filament_pre_cooling_temperature",
    "filament_pre_cooling_temperature_nc", "filament_preheat_temperature_delta", "filament_ramming_travel_time",
    "filament_ramming_travel_time_nc", "filament_ramming_volumetric_speed", "filament_ramming_volumetric_speed_nc",
    "filament_retract_before_wipe", "filament_retract_length_nc", "filament_retract_restart_extra",
    "filament_retract_when_changing_layer", "filament_retraction_distances_when_cut", "filament_retraction_length",
    "filament_retraction_minimum_travel", "filament_retraction_speed", "filament_wipe", "filament_wipe_distance",
    "filament_z_hop", "filament_z_hop_types", "long_retractions_when_ec", "nozzle_temperature",
    "nozzle_temperature_initial_layer", "override_process_overhang_speed", "retraction_distances_when_ec",
    "slow_down_min_speed", "volumetric_speed_coefficients",
]

STEM = sys.argv[1] if len(sys.argv) > 1 else "coupon"
OUT = f"{STEM}-print.3mf"
LABEL = "NACS holder fit coupon"
BED_CENTRE = (128.0, 128.0)
PRIME_TOWER_XY = ("175", "100")   # beside the coupon; the CLI default (165, 236) puts the 35 mm tower off the bed
BED_TYPE = "Textured PEI Plate"
SCALARS = {
    "curr_bed_type": BED_TYPE,
    "ironing_type": "no ironing",
    "top_one_wall_type": "not apply",
    "seam_gap": "0%",
    "skirt_loops": "2",
    "skirt_distance": "3",
    "skirt_height": "1",
    # supports: Bambu's recommended params for PETG + Support For PLA/PETG
    "enable_support": "1",
    "support_type": "tree(auto)",
    "support_style": "tree_hybrid",
    "support_threshold_angle": "35",
    "support_on_build_plate_only": "0",
    "support_top_z_distance": "0",
    "support_interface_pattern": "rectilinear_interlaced",
    "support_interface_spacing": "0",
    "tree_support_branch_diameter": "3",
    "tree_support_branch_diameter_angle": "7",
    "support_interface_filament": "2",
    "support_filament": "0",
}
LISTS = {
    "top_surface_speed": "60",
    "small_perimeter_speed": "30",
    "small_perimeter_threshold": "10",
    "gap_infill_speed": "40",
    "initial_layer_speed": "30",
    "initial_layer_infill_speed": "50",
}


def load(kind, name):
    with open(f"{ROOT}/{kind}/{name.replace('/', '-')}.json") as f:   # "PLA/PETG" presets are stored as PLA-PETG
        return json.load(f)


def flatten(kind, name):
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
    with open(f"{d}/machine.json", "w") as f:
        json.dump(flatten("machine", MACHINE), f)
    with open(f"{d}/process.json", "w") as f:
        json.dump(flatten("process", PROCESS), f)
    for i, name in enumerate(FILAMENTS, 1):
        with open(f"{d}/filament{i}.json", "w") as f:
            json.dump(flatten("filament", name), f)


def expand_variants(cfg):
    """Lay the per-variant filament keys out as Studio does: every machine variant for every filament."""
    variants = flatten("machine", MACHINE)["printer_extruder_variant"]
    presets = [flatten("filament", n) for n in FILAMENTS]
    nv, nf = len(variants), len(FILAMENTS)
    for k in PER_VARIANT_KEYS:
        if k not in cfg:
            continue
        cur = cfg[k]
        assert isinstance(cur, list) and len(cur) == nf, (k, cur)
        out = []
        for i, pre in enumerate(presets):
            pv = pre.get(k)
            out += pv if isinstance(pv, list) and len(pv) == nv else [cur[i]] * nv
        cfg[k] = out
    cfg["filament_extruder_variant"] = variants * nf
    cfg["filament_self_index"] = [str(i) for i in range(1, nf + 1) for _ in range(nv)]
    ne = len(cfg["nozzle_diameter"])
    # GCode.cpp checks filaments^2 x len(flush_multiplier) == len(flush_volumes_matrix): one multiplier per extruder
    cfg["flush_multiplier"] = ["1"] * ne
    cfg["flush_multiplier_fast"] = ["1.2"] * ne
    cfg["flush_volumes_matrix"] = ["0" if a == b else "280" for _ in range(ne) for a in range(nf) for b in range(nf)]
    cfg["flush_volumes_vector"] = ["140"] * (ne * nf)
    cfg["filament_colour_type"] = ["1"] * nf
    cfg["filament_multi_colour"] = list(FILAMENT_COLOUR)


def patch(src, dst):
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                s = data.decode()
                assert s.count("<item ") == 1, "expected one build item"
                s = re.sub(r'(<item [^>]*?transform="(?:\S+ ){9})\S+ \S+',
                           r'\g<1>%g %g' % BED_CENTRE, s, count=1)
                data = s.encode()
            elif item.filename == "Metadata/project_settings.config":
                cfg = json.loads(data)
                cfg.update(SCALARS)
                for k, v in LISTS.items():
                    assert isinstance(cfg[k], list), f"{k} is not a per-variant list: {cfg[k]!r}"
                    cfg[k] = [v] * len(cfg[k])
                diff = cfg.get("different_settings_to_system") or [""]
                existing = [x for x in diff[0].split(";") if x]
                diff[0] = ";".join(sorted(set(existing) | set(SCALARS) | set(LISTS)))
                cfg["different_settings_to_system"] = diff
                cfg["filament_map_mode"] = "Manual"
                cfg["filament_map"] = FILAMENT_MAP
                # the CLI writes one colour for a one-STL plate even with two filaments loaded; every
                # per-filament vector must have one entry per filament or the slicer reads a garbage extruder
                cfg["filament_colour"] = FILAMENT_COLOUR
                cfg["filament_nozzle_map"] = FILAMENT_NOZZLE_MAP
                expand_variants(cfg)
                cfg["wipe_tower_x"], cfg["wipe_tower_y"] = [PRIME_TOWER_XY[0]], [PRIME_TOWER_XY[1]]
                data = json.dumps(cfg, indent=4).encode()
            elif item.filename == "Metadata/model_settings.config":
                s = re.sub(r'value="[^"]*\.stl"', f'value="{LABEL}"', data.decode())
                s = s.replace('key="filament_map_mode" value="Auto For Flush"', 'key="filament_map_mode" value="Manual"')
                data = s.encode()
            zout.writestr(item, data)
    zin.close()


def verify(path, tmp):
    z = zipfile.ZipFile(path)
    cfg = json.loads(z.read("Metadata/project_settings.config"))
    for k, v in SCALARS.items():
        assert cfg[k] == v, f"{k} did not stick: {cfg[k]}"
    for k, v in LISTS.items():
        assert set(cfg[k]) == {v}, f"{k} did not stick: {cfg[k]}"
    assert (set(SCALARS) | set(LISTS)) <= set(cfg["different_settings_to_system"][0].split(";"))
    assert cfg["printer_settings_id"] == MACHINE, cfg["printer_settings_id"]
    assert cfg["filament_settings_id"] == FILAMENTS, cfg["filament_settings_id"]
    assert cfg["textured_plate_temp"][0] == "70", cfg["textured_plate_temp"]
    assert cfg["filament_map_mode"] == "Manual" and cfg["filament_map"] == FILAMENT_MAP, (cfg["filament_map_mode"], cfg["filament_map"])
    assert cfg["filament_colour"] == FILAMENT_COLOUR and cfg["filament_nozzle_map"] == FILAMENT_NOZZLE_MAP
    assert (cfg["wipe_tower_x"], cfg["wipe_tower_y"]) == ([PRIME_TOWER_XY[0]], [PRIME_TOWER_XY[1]])
    nv = len(cfg["printer_extruder_variant"])
    assert len(cfg["filament_extruder_variant"]) == len(cfg["nozzle_temperature"]) == nv * len(FILAMENTS)
    assert "Bowden Standard" in cfg["filament_extruder_variant"][nv:]
    assert len(cfg["flush_volumes_matrix"]) == len(cfg["flush_multiplier"]) * len(FILAMENTS) ** 2 == len(cfg["nozzle_diameter"]) * len(FILAMENTS) ** 2
    assert 'key="filament_map_mode" value="Manual"' in z.read("Metadata/model_settings.config").decode()
    t = re.search(r'<item [^>]*transform="([^"]*)"', z.read("3D/3dmodel.model").decode()).group(1).split()
    assert (float(t[9]), float(t[10])) == BED_CENTRE, t

    out = f"{tmp}/sliced.3mf"
    res = graft_slice(path, out)
    assert res.get("rc") == 0 and os.path.exists(out), f"slice failed rc={res.get('rc')}: {res}"
    info = zipfile.ZipFile(out).read("Metadata/slice_info.config").decode()
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
    per = re.findall(r'<filament id="(\d+)"[^>]*used_g="([^"]*)"', info)
    return {"minutes": round(int(grab("prediction")) / 60), "grams": round(float(grab("weight")), 1),
            "grams_per_filament": {i: round(float(g), 1) for i, g in per}, "layers": res.get("layers")}


def main():
    with tempfile.TemporaryDirectory() as tmp:
        write_presets(tmp)
        shutil.copy(f"{PROJECT}/{STEM}.stl", f"{tmp}/{STEM}.stl")
        r = subprocess.run(
            ["bambu-studio", "--arrange", "1",
             "--load-settings", "machine.json;process.json",
             "--load-filaments", ";".join(f"filament{i}.json" for i in range(1, len(FILAMENTS) + 1)),
             "--load-filament-ids", "1",
             "--export-3mf", "raw.3mf", "--outputdir", ".", f"{STEM}.stl"],
            cwd=tmp, capture_output=True, text=True, timeout=600)
        assert os.path.exists(f"{tmp}/raw.3mf"), f"CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
        final = f"{PROJECT}/{OUT}"
        patch(f"{tmp}/raw.3mf", final)
        result = verify(final, tmp)
    with open(f"{PROJECT}/{STEM}-slice.json", "w") as f:
        json.dump(result, f, indent=1)
    print(final, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
