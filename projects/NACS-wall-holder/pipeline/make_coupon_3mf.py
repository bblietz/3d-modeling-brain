"""Bambu Studio print 3MF for the NACS holder (holder.stl) or its fit coupon (coupon.stl) in PETG, verified by a real slice.

Adapted from projects/NACS-organizer/make_plate.py (same X2D 0.6 nozzle, 0.30mm
Standard, Bambu PETG Basic, Textured PEI, Sharks PETG lessons), plus supports
for the cavity roof: tree supports with Bambu Support For PLA/PETG as the
interface material on the X2D's second (Bowden) nozzle, using Bambu's own
recommended parameters for that pairing (support_recommended_params.json).

Usage:  .venv/bin/python projects/NACS-wall-holder/pipeline/make_coupon_3mf.py [coupon|holder]      (default: coupon)
Reads <stem>.stl; writes <stem>-print.3mf and <stem>-slice.json, and prints real minutes and grams per filament.
The holder gets 3 walls and 20% gyroid (it hangs a wand and an 18 ft cable off a wall), sits left of centre so the
prime tower fits beside it, and gets a modifier part that makes the plate solid for PAD_R around each screw hole
(Brian, 2026-09-18); the slice check reads the G-code to confirm the pads print solid.
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
JOBS = {   # label, bed centre of the part, prime tower corner (the CLI default (165, 236) puts the 35 mm tower off the bed), extra process settings
    "coupon": ("NACS holder fit coupon", (128.0, 128.0), ("175", "100"), {}),
    # the two nozzles share x 20..256 only (CLI log: shared_printable_size 236, centre 138): the 150 mm plate spans 33..183, skirt included it stays clear of 20
    "holder": ("NACS wall holder", (108.0, 128.0), ("192", "180"), {"wall_loops": "3", "sparse_infill_density": "20%", "sparse_infill_pattern": "gyroid"}),
}
LABEL, BED_CENTRE, PRIME_TOWER_XY, EXTRA = JOBS[STEM]
PAD_R = 12.5          # holder only: solid infill this far around each screw hole
PAD_NAME = "MOD screw pads: solid infill"
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
    **EXTRA,
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


def scad_const(name):
    scad = open(f"{PROJECT}/holder.scad").read()
    return float(re.search(rf"(?:^|;)\s*{name}\s*=\s*([-0-9.]+)", scad, re.M).group(1))


def hole_centres():
    off = scad_const("plate_w") / 2 - scad_const("hole_in")
    return [(sx * off, sy * off) for sx in (-1, 1) for sy in (-1, 1)]


def add_screw_pads(path):
    """One modifier part, four cylinders through the plate at the screw holes, sparse_infill_density 100%."""
    import trimesh
    from fillcore_mod import centered, inject_modifier, next_object_id, object_pos
    # clipped to the plate: a modifier that sticks out past the part grows the object's outline, and the skirt with it
    w, r, t = scad_const("plate_w"), scad_const("plate_r"), scad_const("plate_t")
    cyls = " ".join(f"translate([{x}, {y}, 0]) cylinder(r = {PAD_R}, h = {t}, $fn = 64);" for x, y in hole_centres())
    scad = (f"intersection() {{\n  linear_extrude({t}) offset(r = {r}) offset(delta = -{r}) square({w}, center = true);\n"
            f"  union() {{ {cyls} }}\n}}\n")
    with tempfile.TemporaryDirectory() as d:
        with open(f"{d}/pads.scad", "w") as f:
            f.write(scad)
        subprocess.run([os.path.expanduser("~/.local/bin/openscad"), "--backend=Manifold", "-o", f"{d}/pads.stl", f"{d}/pads.scad"],
                       capture_output=True, text=True, check=True)
        pads = trimesh.load(f"{d}/pads.stl")
    assert len(pads.split()) == 4 and pads.is_watertight, "expected four closed pads"
    mesh_c, mc = centered(pads)
    b = trimesh.load(f"{PROJECT}/{STEM}.stl").bounds
    zin = zipfile.ZipFile(path)
    files = {i.filename: zin.read(i.filename) for i in zin.infolist()}
    zin.close()
    model3d = files["3D/3dmodel.model"].decode()
    objfiles = {n: files[n].decode() for n in files if n.startswith("3D/Objects/")}
    settings = files["Metadata/model_settings.config"].decode()
    oid = re.search(r'<object id="(\d+)"', settings).group(1)
    block = re.search(rf'<object id="{oid}">.*?</object>', settings, re.S).group(0)
    pos = object_pos(model3d, oid, (b[0] + b[1]) / 2)
    pid = next_object_id(model3d, objfiles)
    new_block, model3d = inject_modifier(block, model3d, objfiles, oid, pid, PAD_NAME, "screw-pads.stl", mesh_c, mc, pos,
                                         {"sparse_infill_density": "100%"})
    files["Metadata/model_settings.config"] = settings.replace(block, new_block).encode()
    files["3D/3dmodel.model"] = model3d.encode()
    for n, v in objfiles.items():
        files[n] = v.encode()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, v in files.items():
            zout.writestr(n, v)


def check_pads_solid(sliced, gcode_name):
    """Plastic per volume between the plate's skins, from the G-code: each pad must be solid, the plain plate must not be.
    (Bambu keeps the "Sparse infill" label at 100% density, so the label says nothing; gyroid comes as G2/G3 arcs.)"""
    import math
    g = zipfile.ZipFile(sliced).read(gcode_name).decode(errors="replace")
    t = scad_const("plate_t")
    off = scad_const("plate_w") / 2 - scad_const("hole_in")
    windows = {f"pad {i + 1}": (BED_CENTRE[0] + x, BED_CENTRE[1] + y, PAD_R - 3.5, math.pi * (scad_const("hole_d") / 2) ** 2)
               for i, (x, y) in enumerate(hole_centres())}
    windows["plain plate"] = (BED_CENTRE[0] - off, BED_CENTRE[1], 7.0, 0.0)      # midway between two holes, clear of the edge walls
    used, layers = {k: 0.0 for k in windows}, set()
    z, x, y = 0.0, 0.0, 0.0
    for line in g.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":")[1])
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, me = re.search(r" X([-0-9.]+)", line), re.search(r" Y([-0-9.]+)", line), re.search(r" E([-0-9.]+)", line)
            nx, ny = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if me and float(me.group(1)) > 0 and (mx or my) and 1.2 <= z <= t - 1.2:
                layers.add(z)
                for k, (cx, cy, r, _) in windows.items():
                    if ((x + nx) / 2 - cx) ** 2 + ((y + ny) / 2 - cy) ** 2 < r * r:
                        used[k] += float(me.group(1))
            x, y = nx, ny
    zs = sorted(layers)
    height = (zs[1] - zs[0]) * len(zs)
    fill = {k: round(used[k] * math.pi * (1.75 / 2) ** 2 / ((math.pi * r * r - hole) * height), 2) for k, (_, _, r, hole) in windows.items()}
    assert all(v >= 0.8 for k, v in fill.items() if k.startswith("pad")), f"screw pads are not solid: {fill}"
    assert fill["plain plate"] <= 0.4, f"the plain plate is not sparse, the modifier leaked: {fill}"
    return fill


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
    result = {"minutes": round(int(grab("prediction")) / 60), "grams": round(float(grab("weight")), 1),
              "grams_per_filament": {i: round(float(g), 1) for i, g in per}, "layers": res.get("layers")}
    if STEM == "holder":
        assert PAD_NAME in z.read("Metadata/model_settings.config").decode()
        result["screw_pads"] = check_pads_solid(out, res["gcode"])
    return result


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
        if STEM == "holder":
            add_screw_pads(final)
        result = verify(final, tmp)
    with open(f"{PROJECT}/{STEM}-slice.json", "w") as f:
        json.dump(result, f, indent=1)
    print(final, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
