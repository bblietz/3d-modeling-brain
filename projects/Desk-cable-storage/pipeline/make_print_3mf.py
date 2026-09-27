"""Bambu Studio print 3MF for the desk cable trough (trough.stl) in PETG, verified by a real slice.

Adapted from projects/NACS-organizer/make_plate.py (single PETG part: X2D 0.6 nozzle, 0.30mm Standard,
Bambu PETG Basic, Textured PEI, the Sharks PETG lessons, graft_slice for the verification slice) with the
include-merging flattener and world_bounds() from projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py
(memory/reference-x2d-preset-includes.md: the X2D machine presets keep their G-code in include templates).

The trough is 254 x 152.4 x 152.4 mm on the X2D's 256 x 256 bed, 1 mm to spare each side in X, so:
  no brim, no skirt          either would run off the plate (the recipe's 2-loop PETG skirt is dropped)
  extruder 1, Manual map     only the main nozzle's area is the full bed; the second (Bowden) nozzle's starts at
                             x 20.5, and in Auto mode the CLI's arranger rotates the part 90 degrees to fit their
                             shared area. The item transform is written outright: no rotation, centred at 128, 128.
The STL is already in print orientation (floor on z 0, open top up, no overhangs, no supports).

Usage:  .venv/bin/python projects/Desk-cable-storage/pipeline/make_print_3mf.py
Reads trough.stl; writes trough-print.3mf and trough-slice.json (real minutes, grams, metres, layers, placement).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline"))
from graft_slice import graft_slice  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")   # the 02.08.00.06 bundle of the installed 02.08.02.61 Studio

MACHINE = "Bambu Lab X2D 0.6 nozzle"
PROCESS = "0.30mm Standard @BBL X2D 0.6 nozzle"
FILAMENT = "Bambu PETG Basic @BBL X2D"
FILAMENT_COLOUR = "#000000"

STEM = "trough"
OUT = f"{STEM}-print.3mf"
LABEL = "Desk cable trough"
BED = 256.0
BED_CENTRE = (128.0, 128.0)
BED_TYPE = "Textured PEI Plate"
SCALARS = {
    "curr_bed_type": BED_TYPE,
    "brim_type": "no_brim",
    "skirt_loops": "0",
    # PETG lessons from knowledge/learnings/sharks-nametag.md, as in NACS-organizer/make_plate.py: no ironing,
    # two top walls, closed seams (a seam runs up every corner of this 152 mm box); the skirt lesson cannot apply
    "ironing_type": "no ironing",
    "top_one_wall_type": "not apply",
    "seam_gap": "0%",
}
LISTS = {   # one value per extruder variant; slow small loops and a slow first layer (a 254 x 152 mm PETG first layer)
    "top_surface_speed": "60",
    "small_perimeter_speed": "30",
    "small_perimeter_threshold": "10",
    "gap_infill_speed": "40",
    "initial_layer_speed": "30",
    "initial_layer_infill_speed": "50",
}


def load(kind, name):
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
    """Resolve the inherits chain and each preset's include templates; the CLI cannot do this for X2D presets."""
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


def write_presets(d):
    for kind, name, fn in (("machine", MACHINE, "machine.json"), ("process", PROCESS, "process.json"), ("filament", FILAMENT, "filament.json")):
        with open(f"{d}/{fn}", "w") as f:
            json.dump(flatten(kind, name), f)


def matrix(transform):
    """3MF transform (12 numbers, row-major 3x3 then the translation) as a 4x4 that acts on column vectors."""
    t = [float(v) for v in transform.split()] if transform else [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    m = np.eye(4)
    m[:3, :3] = np.array(t[:9]).reshape(3, 3).T
    m[:3, 3] = t[9:]
    return m


def world_bounds(z):
    """(lo, hi) of the one build item in world mm, from the meshes and transforms in the 3MF itself
    (item transform x component transform x the mesh's own coordinates; the CLI stores the mesh centred)."""
    main = z.read("3D/3dmodel.model").decode()
    comps = {oid: re.findall(r'<component p:path="([^"]+)" objectid="(\d+)"(?: [^>]*?transform="([^"]*)")?', body)
             for oid, body in re.findall(r'<object id="(\d+)"[^>]*>(.*?)</object>', main, re.S)}
    items = re.findall(r'<item objectid="(\d+)"[^>]*?transform="([^"]*)"', main)
    assert len(items) == 1, f"expected one build item, found {len(items)}"
    pts = []
    for path, sub_id, comp_t in comps[items[0][0]]:
        sub = z.read(path.lstrip("/")).decode()
        mesh = re.search(rf'<object id="{sub_id}"[^>]*>(.*?)</object>', sub, re.S).group(1)
        v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', mesh), dtype=float)
        pts.append((matrix(items[0][1]) @ matrix(comp_t) @ np.c_[v, np.ones(len(v))].T).T[:, :3])
    pts = np.vstack(pts)
    return pts.min(axis=0), pts.max(axis=0)


def patch(src, dst):
    """Place the part unrotated at the bed centre, apply the overrides, pin the filament to extruder 1, name and colour it."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                s = data.decode()
                assert s.count("<item ") == 1, "expected one build item"
                # the arranger's transform carries a 90 degree turn; keep only its z (the mesh is stored centred)
                s = re.sub(r'(<item [^>]*?transform=")([^"]*)',
                           lambda m: m.group(1) + "1 0 0 0 1 0 0 0 1 %g %g %s" % (*BED_CENTRE, m.group(2).split()[11]), s, count=1)
                data = s.encode()
            elif item.filename == "Metadata/project_settings.config":
                cfg = json.loads(data)
                cfg.update(SCALARS)
                for k, v in LISTS.items():
                    assert isinstance(cfg[k], list), f"{k} is not a per-variant list: {cfg[k]!r}"
                    cfg[k] = [v] * len(cfg[k])
                # any key changed in a project 3MF must be listed here or Studio's GUI resets it on open
                diff = cfg.get("different_settings_to_system") or [""]
                diff[0] = ";".join(sorted(set(x for x in diff[0].split(";") if x) | set(SCALARS) | set(LISTS)))
                cfg["different_settings_to_system"] = diff
                cfg["filament_map_mode"], cfg["filament_map"], cfg["filament_nozzle_map"] = "Manual", ["1"], ["1"]
                cfg["filament_colour"] = cfg["filament_multi_colour"] = [FILAMENT_COLOUR]
                data = json.dumps(cfg, indent=4).encode()
            elif item.filename == "Metadata/model_settings.config":
                s = data.decode().replace(f'key="name" value="{STEM}.stl"', f'key="name" value="{LABEL}"')
                s = s.replace('key="filament_map_mode" value="Auto For Flush"', 'key="filament_map_mode" value="Manual"')
                data = s.encode()
            zout.writestr(item, data)
    zin.close()


def check_settings(path, what):
    z = zipfile.ZipFile(path)
    cfg = json.loads(z.read("Metadata/project_settings.config"))
    for k, v in SCALARS.items():
        assert cfg[k] == v, f"{what}: {k} did not stick: {cfg[k]}"
    for k, v in LISTS.items():
        assert set(cfg[k]) == {v}, f"{what}: {k} did not stick: {cfg[k]}"
    assert set(SCALARS) | set(LISTS) <= set(cfg["different_settings_to_system"][0].split(";")), f"{what}: different_settings_to_system"
    assert cfg["printer_settings_id"] == MACHINE and cfg["print_settings_id"] == PROCESS and cfg["filament_settings_id"] == [FILAMENT], \
        (cfg["printer_settings_id"], cfg["print_settings_id"], cfg["filament_settings_id"])
    assert cfg["nozzle_diameter"][0] == "0.6" and cfg["layer_height"] == "0.3", (cfg["nozzle_diameter"], cfg["layer_height"])
    assert cfg["textured_plate_temp"] == ["70"], cfg["textured_plate_temp"]
    assert cfg["filament_map_mode"] == "Manual" and cfg["filament_map"] == ["1"] and cfg["filament_nozzle_map"] == ["1"], \
        f"{what}: not pinned to extruder 1: {cfg['filament_map_mode']}, {cfg['filament_map']}, {cfg['filament_nozzle_map']}"
    assert cfg["filament_colour"] == [FILAMENT_COLOUR], cfg["filament_colour"]
    ms = z.read("Metadata/model_settings.config").decode()
    assert f'key="name" value="{LABEL}"' in ms and 'key="filament_map_mode" value="Manual"' in ms, f"{what}: model_settings"
    assert len(re.findall(r"<model_instance>", ms)) == 1, f"{what}: the part is not on plate 1"
    return z


def check_placement(z, what):
    """The part stands unrotated, centred, floor on the bed and inside 0..256 in x and y, by the 3MF's own geometry."""
    lo, hi = world_bounds(z)
    stl = trimesh.load(f"{PROJECT}/{STEM}.stl").extents
    assert np.allclose(hi - lo, stl, atol=0.01), f"{what}: world extents {hi - lo} differ from the STL's {stl}: the part is rotated"
    assert abs((lo[0] + hi[0]) / 2 - BED_CENTRE[0]) < 0.01 and abs((lo[1] + hi[1]) / 2 - BED_CENTRE[1]) < 0.01, f"{what}: not centred: {lo} {hi}"
    assert abs(lo[2]) < 0.01, f"{what}: floor at z {lo[2]:.3f}"
    assert lo[0] >= 0 and lo[1] >= 0 and hi[0] <= BED and hi[1] <= BED, f"{what}: off the {BED:g} mm bed: {lo} {hi}"
    return {"min": [round(float(v), 2) for v in lo], "max": [round(float(v), 2) for v in hi]}


def gcode_stats(gcode):
    """Extruded filament (mm) and the xy extent of the extrusion moves per G-code feature."""
    used, box, feat, x, y = {}, {}, "", 0.0, 0.0
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, me = re.search(r" X([-0-9.]+)", line), re.search(r" Y([-0-9.]+)", line), re.search(r" E([-0-9.]+)", line)
            x, y = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if feat and me and float(me.group(1)) > 0 and (mx or my):
                used[feat] = used.get(feat, 0.0) + float(me.group(1))
                b = box.setdefault(feat, [x, y, x, y])
                b[0], b[1], b[2], b[3] = min(b[0], x), min(b[1], y), max(b[2], x), max(b[3], y)
    return ({k: round(v, 1) for k, v in sorted(used.items(), key=lambda kv: -kv[1])},
            {k: [round(v, 2) for v in b] for k, b in box.items()})


def verify(path, tmp):
    """Settings and placement in the file, a CLI round trip, then a real slice. A round trip alone does not prove sliceability."""
    z = check_settings(path, "authored file")
    result = {"placement_mm": check_placement(z, "authored file")}

    r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", path],
                       cwd=tmp, capture_output=True, text=True, timeout=600)
    assert os.path.exists(f"{tmp}/roundtrip.3mf"), f"round trip failed rc={r.returncode}\n{r.stdout[-1500:]}"
    check_placement(check_settings(f"{tmp}/roundtrip.3mf", "CLI round trip"), "CLI round trip")
    result["roundtrip"] = "settings and placement survive bambu-studio --arrange 0 --export-3mf"

    # The CLI cannot slice its own project files (rc 156); graft_slice adds the GUI-only keys to a throwaway copy
    out = f"{tmp}/sliced.3mf"
    res = graft_slice(path, out)
    log = open(res["log"]).read() if res.get("log") and os.path.exists(res["log"]) else ""
    complaints = [l for l in log.splitlines() if re.search(r"exceed|outside|out of|too large|not fit|Wayland", l, re.I) and "Wayland" not in l]
    assert res.get("rc") == 0 and os.path.exists(out) and res.get("gcode"), f"slice failed rc={res.get('rc')}: {complaints or log[-2000:]}"
    assert not complaints, f"the slicer complained: {complaints}"
    zs = zipfile.ZipFile(out)
    info = zs.read("Metadata/slice_info.config").decode()
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
    fil = re.search(r'<filament id="1"[^>]*/>', info).group(0)
    used_m, used_g = (float(re.search(rf'{k}="([^"]*)"', fil).group(1)) for k in ("used_m", "used_g"))
    gcode = zs.read(res["gcode"]).decode(errors="replace")
    assert "X2D start gcode" in gcode, "the X2D start G-code is missing: the machine include templates did not merge"
    preset = flatten("filament", FILAMENT)
    temp, bed = preset["nozzle_temperature"][0], preset["textured_plate_temp"][0]
    assert re.search(rf"^\s*M10[49] S{temp}\b", gcode, re.M), f"nozzle temperature {temp} is not in the G-code"
    assert re.search(rf"^\s*M1[49]0 S{bed}\b", gcode, re.M), f"bed temperature {bed} is not in the G-code"
    assert re.search(r"^; filament_map = 1$", gcode, re.M), "the G-code does not print from extruder 1"
    layers_expected = round(trimesh.load(f"{PROJECT}/{STEM}.stl").extents[2] / float(json.loads(z.read("Metadata/project_settings.config"))["layer_height"]))
    assert res["layers"] == layers_expected, f"{res['layers']} layers sliced, {layers_expected} expected"
    feature_mm, feature_box = gcode_stats(gcode)
    assert not {"Brim", "Skirt"} & set(feature_mm), f"a brim or skirt was sliced: {feature_mm}"
    xy = [min(b[0] for b in feature_box.values()), min(b[1] for b in feature_box.values()),
          max(b[2] for b in feature_box.values()), max(b[3] for b in feature_box.values())]
    assert xy[0] >= 0 and xy[1] >= 0 and xy[2] <= BED and xy[3] <= BED, f"toolpaths leave the bed: {xy}"
    grams = float(grab("weight"))
    result.update({"time": res["time"], "minutes": round(int(grab("prediction")) / 60), "grams": round(grams, 1),
                   "metres": round(used_m, 2), "used_g_per_filament": round(used_g, 1), "layers": res["layers"],
                   "nozzle_C": int(temp), "bed_C": int(bed), "toolpath_xy_mm": [round(v, 2) for v in xy], "feature_mm": feature_mm})
    return result


def main():
    final = f"{PROJECT}/{OUT}"
    with tempfile.TemporaryDirectory() as tmp:
        write_presets(tmp)
        shutil.copy(f"{PROJECT}/{STEM}.stl", f"{tmp}/{STEM}.stl")
        # --export-3mf must be a bare filename; an absolute path alongside --outputdir makes the CLI exit 243 without writing.
        # --arrange 1 keeps the plate's model_instance (--arrange 0 writes none); its rotation is overwritten in patch().
        r = subprocess.run(
            ["bambu-studio", "--arrange", "1",
             "--load-settings", "machine.json;process.json",
             "--load-filaments", "filament.json",
             "--export-3mf", "raw.3mf", "--outputdir", ".", f"{STEM}.stl"],
            cwd=tmp, capture_output=True, text=True, timeout=600)
        assert os.path.exists(f"{tmp}/raw.3mf"), f"CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
        patch(f"{tmp}/raw.3mf", final)
        result = verify(final, tmp)
    with open(f"{PROJECT}/{STEM}-slice.json", "w") as f:
        json.dump(result, f, indent=1)
    print(final)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
