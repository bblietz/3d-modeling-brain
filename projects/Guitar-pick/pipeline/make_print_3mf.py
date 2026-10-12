"""Bambu Studio print 3MF for the guitar pick (guitar-pick.stl) in PETG on the 0.2 mm nozzle, verified by a real slice.

Copied from projects/Skateboard-wall-holder/pipeline/make_print_3mf.py (single PETG part, include-merging preset
flattener, graft_slice for the verification slice), with the screw-pad modifier dropped and:
  0.2 mm nozzle presets        Brian's call 2026-10-11, the smoothest edge and faces
  layer_height 0.06            the stock 0.08 does not divide the 1.0 mm pick (0.1 + 11 x 0.08 = 0.98); 0.1 + 15 x 0.06 = 1.0
  sparse_infill_density 100%   a solid plate whatever the shell counts are
  seam_position back           the seam sits at the top centre of the pick, under the thumb, away from the tip
  wall_generator arachne       the vault's choice for fine features on the 0.2 (Sharks nametag)
  no ironing                   the vault's PETG rule until a coupon says otherwise; this pick is that coupon
  skirt 2 loops / 3 mm / 1     memory/feedback-keep-skirt.md

Usage:  .venv/bin/python projects/Guitar-pick/pipeline/make_print_3mf.py
Reads guitar-pick-sym.stl; writes guitar-pick-flat.3mf and guitar-pick-sym-slice.json. Superseded by make_standup_3mf.py
(Brian 2026-10-12: print standing); kept for the flat variants.
"""
import json
import math
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

MACHINE = "Bambu Lab X2D 0.2 nozzle"
PROCESS = "0.08mm High Quality @BBL X2D 0.2 nozzle"
FILAMENT = "Bambu PETG Basic @BBL X2D 0.2 nozzle"
FILAMENT_COLOUR = "#000000"      # display only; any PETG Basic slot in the AMS prints it

STEM = "guitar-pick-sym"           # the flat-printable variant; the shipped 3MF is the standing one (make_standup_3mf.py)
OUT = "guitar-pick-flat.3mf"
LABEL = "Guitar pick, Tortex 1.0 copy, flat"
BED = 256.0
BED_CENTRE = (128.0, 128.0)
BED_TYPE = "Textured PEI Plate"
LAYER = 0.06
SCALARS = {
    "curr_bed_type": BED_TYPE,
    "brim_type": "no_brim",
    "skirt_loops": "2",
    "skirt_distance": "3",
    "skirt_height": "1",
    "layer_height": f"{LAYER:g}",
    "sparse_infill_density": "100%",
    "sparse_infill_pattern": "zig-zag",     # the preset's gyroid is refused at 100% ("doesn't work at 100% density")
    "wall_generator": "arachne",
    "seam_position": "back",
    # PETG lessons from knowledge/learnings/sharks-nametag.md: no ironing, two top walls, closed seams
    "ironing_type": "no ironing",
    "top_one_wall_type": "not apply",
    "seam_gap": "0%",
    # the rounded underside already stands in for the foot; shrinking layer 1 another 0.15 would leave layer 2's
    # wall hanging 0.26 mm past it (more than a 0.22 line), so the compensation is off for this part
    "elefant_foot_compensation": "0",
}
LISTS = {   # one value per extruder variant
    "top_surface_speed": "60",
    "initial_layer_speed": "30",
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
    """(lo, hi) of the one build item in world mm, from the meshes and transforms in the 3MF itself."""
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
                # the arranger may turn the part; keep only its z (the model's +Y, the top of the pick, stays at bed rear)
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


def recenter(path):
    """The CLI does not always store the mesh centred: read the file's own world bounds and move the one build
    item so the part is centred on the bed with its floor on z 0."""
    z = zipfile.ZipFile(path)
    lo, hi = world_bounds(z)
    entries = [(item, z.read(item.filename)) for item in z.infolist()]
    z.close()
    dx, dy, dz = BED_CENTRE[0] - (lo[0] + hi[0]) / 2, BED_CENTRE[1] - (lo[1] + hi[1]) / 2, -lo[2]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item, data in entries:
            if item.filename == "3D/3dmodel.model":
                def shift(m):
                    t = [float(v) for v in m.group(2).split()]
                    t[9], t[10], t[11] = t[9] + dx, t[10] + dy, t[11] + dz
                    return m.group(1) + " ".join("%g" % v for v in t)
                data = re.sub(r'(<item [^>]*?transform=")([^"]*)', shift, data.decode(), count=1).encode()
            zout.writestr(item, data)


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
    assert cfg["nozzle_diameter"][0] == "0.2" and cfg["layer_height"] == f"{LAYER:g}", (cfg["nozzle_diameter"], cfg["layer_height"])
    assert cfg["initial_layer_print_height"] == "0.1", cfg["initial_layer_print_height"]
    assert cfg["elefant_foot_compensation"] == "0", cfg["elefant_foot_compensation"]
    assert float(cfg["min_layer_height"][0]) <= LAYER <= float(cfg["max_layer_height"][0]), (cfg["min_layer_height"], cfg["max_layer_height"])
    assert cfg["textured_plate_temp"] == flatten("filament", FILAMENT)["textured_plate_temp"], cfg["textured_plate_temp"]
    assert cfg["filament_map_mode"] == "Manual" and cfg["filament_map"] == ["1"] and cfg["filament_nozzle_map"] == ["1"], \
        f"{what}: not pinned to extruder 1: {cfg['filament_map_mode']}, {cfg['filament_map']}, {cfg['filament_nozzle_map']}"
    assert cfg["filament_colour"] == [FILAMENT_COLOUR], cfg["filament_colour"]
    ms = z.read("Metadata/model_settings.config").decode()
    assert f'key="name" value="{LABEL}"' in ms and 'key="filament_map_mode" value="Manual"' in ms, f"{what}: model_settings"
    assert len(re.findall(r"<model_instance>", ms)) == 1, f"{what}: the part is not on plate 1"
    return z


def check_placement(z, what):
    """The part lies unrotated, centred, floor on the bed and inside 0..256 in x and y, by the 3MF's own geometry."""
    lo, hi = world_bounds(z)
    stl = trimesh.load(f"{PROJECT}/{STEM}.stl").extents
    assert np.allclose(hi - lo, stl, atol=0.01), f"{what}: world extents {hi - lo} differ from the STL's {stl}: the part is rotated"
    assert abs((lo[0] + hi[0]) / 2 - BED_CENTRE[0]) < 0.01 and abs((lo[1] + hi[1]) / 2 - BED_CENTRE[1]) < 0.01, f"{what}: not centred: {lo} {hi}"
    assert abs(lo[2]) < 0.01, f"{what}: floor at z {lo[2]:.3f}"
    assert lo[0] >= 0 and lo[1] >= 0 and hi[0] <= BED and hi[1] <= BED, f"{what}: off the {BED:g} mm bed: {lo} {hi}"
    return {"min": [round(float(v), 2) for v in lo], "max": [round(float(v), 2) for v in hi]}


def arc_min_y(line, x, y, nx, ny):
    """Lowest y a move reaches: the endpoints for a G1, the bottom of the circle if a G2/G3 arc sweeps through it
    (arc fitting is on in the preset, so the pick's tip is drawn as arcs whose endpoints sit above the real tip)."""
    mi, mj = re.search(r" I([-0-9.]+)", line), re.search(r" J([-0-9.]+)", line)
    if line[:3] not in ("G2 ", "G3 ") or not (mi and mj):
        return min(y, ny)
    cx, cy = x + float(mi.group(1)), y + float(mj.group(1))
    r = math.hypot(x - cx, y - cy)
    a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
    if line.startswith("G2"):       # clockwise: angles decrease from a0 to a1
        sweep, off = (a0 - a1) % (2 * math.pi), (a0 + math.pi / 2) % (2 * math.pi)
    else:
        sweep, off = (a1 - a0) % (2 * math.pi), (-math.pi / 2 - a0) % (2 * math.pi)
    return cy - r if off <= sweep else min(y, ny)


def gcode_stats(gcode):
    """Extruded filament (mm) and the xy extent per G-code feature, the top Z, and where each outer wall loop starts
    (the seam)."""
    used, box, feat, x, y, z_top, seams, new_loop = {}, {}, "", 0.0, 0.0, 0.0, [], False
    tip_y = {}        # per layer: the lowest y any outer wall reaches (the pick's tip points to the front of the bed)
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
            new_loop = feat == "Outer wall"
        elif line.startswith("; Z_HEIGHT:"):
            z_top = max(z_top, float(line.split(":")[1]))
            layer_z = float(line.split(":")[1])
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, me = re.search(r" X([-0-9.]+)", line), re.search(r" Y([-0-9.]+)", line), re.search(r" E([-0-9.]+)", line)
            nx, ny = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if feat and me and float(me.group(1)) > 0 and (mx or my):
                if new_loop:
                    seams.append((x, y))        # the loop starts where the travel left the nozzle
                    new_loop = False
                used[feat] = used.get(feat, 0.0) + float(me.group(1))
                if feat == "Outer wall":
                    tip_y[layer_z] = min(tip_y.get(layer_z, ny), arc_min_y(line, x, y, nx, ny))
                b = box.setdefault(feat, [nx, ny, nx, ny])
                b[0], b[1], b[2], b[3] = min(b[0], nx), min(b[1], ny), max(b[2], nx), max(b[3], ny)
            x, y = nx, ny
    return ({k: round(v, 1) for k, v in sorted(used.items(), key=lambda kv: -kv[1])},
            {k: [round(v, 2) for v in b] for k, b in box.items()}, z_top, seams, tip_y)


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
    complaints = [l for l in log.splitlines() if re.search(r"exceed|outside|out of|too large|not fit", l, re.I)]
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
    for k in ("layer_height", "seam_position", "wall_generator", "sparse_infill_density", "sparse_infill_pattern", "ironing_type"):
        assert re.search(rf"^; {k} = {re.escape(SCALARS[k])}$", gcode, re.M), f"{k} = {SCALARS[k]} is not in the sliced G-code"

    height = trimesh.load(f"{PROJECT}/{STEM}.stl").extents[2]
    layers_expected = 1 + round((height - 0.1) / LAYER)         # 0.1 first layer, then LAYER
    assert abs(0.1 + (layers_expected - 1) * LAYER - height) < 1e-6, f"{LAYER} layers do not sum to the {height} mm pick"
    assert res["layers"] == layers_expected, f"{res['layers']} layers sliced, {layers_expected} expected"
    feature_mm, feature_box, z_top, seams, tip_y = gcode_stats(gcode)
    assert abs(z_top - height) < 1e-3, f"the sliced top is at z {z_top}, the pick is {height} mm"
    assert "Brim" not in feature_mm and "Skirt" in feature_mm, f"expected a skirt and no brim: {feature_mm}"
    assert "Sparse infill" not in feature_mm, f"the pick is not solid: {feature_mm}"
    lo, hi = world_bounds(z)
    assert len(seams) >= layers_expected, f"only {len(seams)} outer wall loops found"
    # seam on the top edge, aligned: every outer wall loop starts within 3 mm of the pick's rear-most point and on the
    # top edge's span (about 9 mm either side of centre before the shoulders turn down), and all loops within 2 mm of
    # each other. The slicer's "back" seam lands at the top centre on some profiles and at a shoulder on others.
    far = [s for s in seams if s[1] < hi[1] - 3.0 or abs(s[0] - BED_CENTRE[0]) > 9.0]
    assert not far, f"{len(far)} of {len(seams)} outer wall loops start away from the top edge, e.g. {far[:3]} (top edge y {hi[1]:.2f})"
    spread = max(max(s[i] for s in seams) - min(s[i] for s in seams) for i in (0, 1))
    assert spread <= 2.0, f"the seam wanders {spread:.2f} mm between layers"
    xy = [min(b[0] for b in feature_box.values()), min(b[1] for b in feature_box.values()),
          max(b[2] for b in feature_box.values()), max(b[3] for b in feature_box.values())]
    assert xy[0] >= 0 and xy[1] >= 0 and xy[2] <= BED and xy[3] <= BED, f"toolpaths leave the bed: {xy}"
    # underside overhang: how far each layer's outer wall at the tip sits past the layer below. The rounded edge grows
    # outward for the bottom half; every step must fit on the line below it (0.22 mm wide, so at most ~0.13 mm)
    zs = sorted(tip_y)
    steps = [(round(z, 2), round(tip_y[z0] - tip_y[z], 3)) for z0, z in zip(zs, zs[1:])]
    worst = max(steps[:len(steps) // 2], key=lambda s: s[1])
    assert worst[1] <= 0.13, f"the underside wall at z {worst[0]} hangs {worst[1]} mm past the layer below"
    result_steps = steps[:len(steps) // 2]
    grams = float(grab("weight"))
    result.update({"time": res["time"], "minutes": round(int(grab("prediction")) / 60), "grams": round(grams, 2),
                   "metres": round(used_m, 2), "used_g_per_filament": round(used_g, 2), "layers": res["layers"],
                   "top_z": z_top, "nozzle_C": int(temp), "bed_C": int(bed), "seam_xy_mm": [round(v, 2) for v in seams[0]],
                   "toolpath_xy_mm": [round(v, 2) for v in xy], "feature_mm": feature_mm,
                   "underside_steps_mm": result_steps})
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
        recenter(final)
        result = verify(final, tmp)
    with open(f"{PROJECT}/{STEM}-slice.json", "w") as f:
        json.dump(result, f, indent=1)
    print(final)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
