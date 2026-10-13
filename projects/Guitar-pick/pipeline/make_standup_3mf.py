"""Bambu Studio print 3MF for the guitar pick STANDING on its snap-off base (guitar-pick.stl from standup.py) in PETG
on the 0.2 mm nozzle, verified by a real slice. Brian 2026-10-12: the mirrored 1.5 mm bevel on both faces, no
support material, printed standing for the smoothest PETG surfaces.

Copied from make_print_3mf.py (the flat pipeline, kept for the flat variants) with:
  0.2 mm nozzle, 0.06 layers   Brian's call 2026-10-11; 577 layers to the 34.66 mm tip (standup.py lands it on a layer)
  seam painted                 a seam enforcer strip (paint_seam) down the centre of the +y face keeps the seam off the rim
                               and in one line; seam_position back alone put it at the end of the face, walking inward
  sparse_infill_density 100%   solid; the 1.0 mm body is four 0.25 mm walls anyway
  wall_generator arachne       the vault's choice for fine features on the 0.2 (Sharks nametag)
  no ironing                   nothing to iron on a standing pick
  skirt 2 loops / 3 mm / 1     memory/feedback-keep-skirt.md
  elephant foot                left at the preset's 0.15: only the base block touches the bed

Checks beyond the flat pipeline: the neck prints as two lines on the mid-plane, every pick loop's seam sits on
one face and stays aligned, nothing is classed as overhang beyond the shoulders, and (since the first print,
2026-10-13) no wall path starts or ends on the pick's edge anywhere above the base: with the one-line neck the
slicer printed the neck as a separate bead ending on the shoulder's edge and seamed the wall loop there, and the
shoulders came out with chunks missing. The parser with path ends is toolpath.py.

Usage:  .venv/bin/python projects/Guitar-pick/pipeline/make_standup_3mf.py
Reads guitar-pick.stl and standup.json; writes guitar-pick.3mf and guitar-pick-slice.json.
"""
import hashlib
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
sys.path.insert(0, HERE)
from graft_slice import graft_slice  # noqa: E402
import toolpath  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")   # the 02.08.00.06 bundle of the installed 02.08.02.61 Studio

MACHINE = "Bambu Lab X2D 0.2 nozzle"
PROCESS = "0.08mm High Quality @BBL X2D 0.2 nozzle"
FILAMENT = "Bambu PETG Basic @BBL X2D 0.2 nozzle"
FILAMENT_COLOUR = "#000000"      # display only; any PETG Basic slot in the AMS prints it

STEM = "guitar-pick"
OUT = f"{STEM}.3mf"
LABEL = "Guitar pick, Tortex 1.0 copy, standing on its base"
STANDUP = json.load(open(f"{PROJECT}/standup.json"))     # written by standup.py: height, base_h, neck, tower
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
    # no scarf seam: seam_slope_type external produced zero ramp moves in the CLI slice of this file and of the flat
    # pick, so it is left at the preset's "none" rather than shipped unverified
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


def paint_seam_strip(xml):
    """Mark the triangles of the seam strip (the 2 micron recess down the +y face, standup.py) as seam enforcers:
    paint_seam="4" is one unsplit triangle in the enforcer state, the encoding Studio writes for its own seam
    painting. The strip floor is the only surface at its y, so it is picked by y alone. The block's rear face
    (y = +3.5, the only surface at that y) is painted too: in the neck layers the pick, neck and block are one wall
    loop, and without this the slicer seamed it in the inside corner where the neck meets the block."""
    verts = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', xml), dtype=float)
    floor_y = 0.5 - STANDUP["seam_depth"]           # the strip floor is the only surface at this y (the mesh is centred in y)
    block_y = STANDUP["block"][1] / 2               # the block's rear face
    n = [0, 0]

    def mark(m):
        tri = verts[[int(m.group(i)) for i in (1, 2, 3)]]
        for k, y in enumerate((floor_y, block_y)):
            if np.all(np.abs(tri[:, 1] - y) < 0.0005):
                n[k] += 1
                return m.group(0)[:-2] + ' paint_seam="4"/>'
        return m.group(0)
    xml = re.sub(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"/>', mark, xml)
    assert n[0] >= 2, f"only {n[0]} seam strip triangles found on the face"
    assert n[1] >= 2, f"only {n[1]} triangles found on the block's rear face"
    print(f"seam strip: {n[0]} triangles painted on the face, {n[1]} on the block's rear face")
    return xml


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
            elif item.filename.startswith("3D/Objects/") and item.filename.endswith(".model"):
                data = paint_seam_strip(data.decode()).encode()
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


def gcode_stats(gcode):
    """Extruded filament (mm) and the xy extent per G-code feature, the top Z, and where each outer wall loop starts
    (the seam)."""
    used, box, feat, x, y, z_top, layer_z, new_loop = {}, {}, "", 0.0, 0.0, 0.0, 0.0, False
    loops = []        # every outer wall loop: [layer z, start x, start y, scarf ramp seen]
    pts = {}          # per layer: the outer wall's (x, y) points
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
            new_loop = feat == "Outer wall"
        elif line.startswith("; Z_HEIGHT:"):
            layer_z = float(line.split(":")[1])
            z_top = max(z_top, layer_z)
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, mz, me = (re.search(rf" {a}([-0-9.]+)", line) for a in "XYZE")
            nx, ny = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if feat and me and float(me.group(1)) > 0 and (mx or my):
                if new_loop:
                    loops.append([layer_z, x, y, False])        # the loop starts where the travel left the nozzle
                    new_loop = False
                if feat == "Outer wall":
                    if mz and loops and abs(float(mz.group(1)) - layer_z) > 1e-6:
                        loops[-1][3] = True                     # extruding below the layer top: the scarf ramp
                    pts.setdefault(layer_z, []).append((nx, ny))
                used[feat] = used.get(feat, 0.0) + float(me.group(1))
                b = box.setdefault(feat, [nx, ny, nx, ny])
                b[0], b[1], b[2], b[3] = min(b[0], nx), min(b[1], ny), max(b[2], nx), max(b[3], ny)
            x, y = nx, ny
    return ({k: round(v, 1) for k, v in sorted(used.items(), key=lambda kv: -kv[1])},
            {k: [round(v, 2) for v in b] for k, b in box.items()}, z_top, loops, pts)


def verify(path, tmp):
    """Settings and placement in the file, a CLI round trip, then a real slice. A round trip alone does not prove sliceability."""
    z = check_settings(path, "authored file")
    result = {"placement_mm": check_placement(z, "authored file")}

    r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", path],
                       cwd=tmp, capture_output=True, text=True, timeout=600)
    assert os.path.exists(f"{tmp}/roundtrip.3mf"), f"round trip failed rc={r.returncode}\n{r.stdout[-1500:]}"
    rt = check_settings(f"{tmp}/roundtrip.3mf", "CLI round trip")
    check_placement(rt, "CLI round trip")
    painted = sum(rt.read(n).decode().count('paint_seam="4"') for n in rt.namelist() if n.startswith("3D/Objects/"))
    assert painted >= 2, f"the seam paint did not survive the CLI round trip ({painted} triangles)"
    result["roundtrip"] = "settings and placement survive bambu-studio --arrange 0 --export-3mf"

    # The CLI cannot slice its own project files (rc 156); graft_slice adds the GUI-only keys to a throwaway copy
    out = f"{tmp}/sliced.3mf"
    cache = os.environ.get("SLICE_CACHE")      # a directory: the slice of an unchanged authored file is reused from it
    key = hashlib.md5(open(path, "rb").read()).hexdigest()[:12] if cache else None
    if cache and os.path.exists(f"{cache}/{key}.3mf"):
        shutil.copy(f"{cache}/{key}.3mf", out)
        res = json.load(open(f"{cache}/{key}.json"))
        res["log"] = f"{cache}/{key}.log"
    else:
        res = graft_slice(path, out)
        if cache and res.get("rc") == 0:
            os.makedirs(cache, exist_ok=True)
            shutil.copy(out, f"{cache}/{key}.3mf")
            if res.get("log") and os.path.exists(res["log"]):
                shutil.copy(res["log"], f"{cache}/{key}.log")
            json.dump(res, open(f"{cache}/{key}.json", "w"))
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

    mesh = trimesh.load(f"{PROJECT}/{STEM}.stl")
    height = mesh.extents[2]
    layers_expected = 1 + round((height - 0.1) / LAYER)         # 0.1 first layer, then LAYER
    assert abs(0.1 + (layers_expected - 1) * LAYER - height) < 1e-4, f"{LAYER} layers do not sum to the {height} mm part"
    assert res["layers"] == layers_expected, f"{res['layers']} layers sliced, {layers_expected} expected"
    feature_mm, feature_box, z_top, loops, pts = gcode_stats(gcode)
    assert abs(z_top - height) < 1e-3, f"the sliced top is at z {z_top}, the part is {height} mm"
    assert "Brim" not in feature_mm and "Skirt" in feature_mm, f"expected a skirt and no brim: {feature_mm}"
    # 100% zig-zag is still labelled "Sparse infill" by the slicer inside the column and block; the density is
    # proven by the "; sparse_infill_density = 100%" line checked above
    assert not any("upport" in k for k in feature_mm), f"the slicer added support: {feature_mm}"
    overhang = sum(v for k, v in feature_mm.items() if "verhang" in k) / feature_mm["Outer wall"]
    assert overhang < 0.08, f"overhang walls are {overhang:.0%} of the outer walls; only the shoulders should be"
    xy = [min(b[0] for b in feature_box.values()), min(b[1] for b in feature_box.values()),
          max(b[2] for b in feature_box.values()), max(b[3] for b in feature_box.values())]
    assert xy[0] >= 0 and xy[1] >= 0 and xy[2] <= BED and xy[3] <= BED, f"toolpaths leave the bed: {xy}"

    # where the pick is on the bed: the model's x 0 (the pick's centre) and y 0 (its mid-plane) after centring
    lo, hi = mesh.bounds
    cx, cy = BED_CENTRE[0] - (lo[0] + hi[0]) / 2, BED_CENTRE[1] - (lo[1] + hi[1]) / 2
    base_top, neck_h, tower_x = STANDUP["base_h"], STANDUP["neck"][1], cx + STANDUP["tower"][1]
    if os.environ.get("SEAM_DUMP"):      # diagnostics for tuning the checks: every loop start, before any assert
        with open(os.environ["SEAM_DUMP"], "w") as f:
            json.dump({"cx": cx, "cy": cy, "tower_x": tower_x, "neck": {str(z): pts[z] for z in pts if base_top < z < base_top + neck_h + 0.1},
                       "loops": [[round(v, 3) if isinstance(v, float) else v for v in l] for l in loops]}, f)
    # the neck: in its layers the outer wall near the pick's centre is two lines either side of the mid-plane
    # (segments, not just their end points: a bead can cross the centre in one long move)
    tp = toolpath.parse(gcode)
    neck_layers = [z for z in tp if base_top + 0.08 < z <= base_top + neck_h + 0.001]
    assert len(neck_layers) >= 3, f"no neck layers found around z {base_top:.2f}..{base_top + neck_h:.2f}"
    # within 1 mm of the centre only: at the top of the neck the block's saddle edges sit 1.8 mm out and are 7 mm wide
    neck_ys = [(s[1] + s[3]) / 2 - cy for z in neck_layers for s in tp[z]
               if s[5] == "Outer wall" and min(s[0], s[2]) < cx + 1.0 and max(s[0], s[2]) > cx - 1.0 and abs(s[1] - cy) < 1.0]
    neck_y = max(abs(v) for v in neck_ys)
    assert neck_y < 0.25, f"the neck's wall wanders {neck_y:.2f} mm off the mid-plane: wider than two lines"
    assert min(neck_ys) < -0.05 < 0.05 < max(neck_ys), f"the neck is not two lines: wall y from {min(neck_ys):.2f} to {max(neck_ys):.2f}"
    # the pick's edges: no wall path may start or end on them (the first print's shoulder damage, toolpath.py). In the
    # neck layers the strip's ends are where the neck meets the block, and nothing may end there either (the seam of
    # that combined loop is painted onto the block's rear face). Above the neck the slicer occasionally splits the
    # loop at the rounded tip for one layer (2 of 450 in the 2026-10-13 slice, a one-layer seam point on the edge);
    # up to three such layers are tolerated, none within 0.1 mm of the neck's top (the 2026-10-13 slice has one 0.4 mm
    # above it, at the same height as before the neck was lengthened: it follows the mesh, not the neck).
    apex, neck_top = base_top + neck_h, base_top + STANDUP["held_drop"] + neck_h
    neck_ends = toolpath.tip_path_ends(tp, cx, cy, apex + 0.05, neck_top + 0.1, feats=("Outer wall",), tol=0.6)
    assert not neck_ends, f"{len(neck_ends)} outer wall path ends on the pick's edge or the neck junction, e.g. {neck_ends[:5]}"
    edge_ends = toolpath.tip_path_ends(tp, cx, cy, neck_top + 0.1, height - 1.0, feats=("Outer wall",), tol=0.6)
    stray_layers = sorted({e[0] for e in edge_ends})
    assert len(stray_layers) <= 3, f"the wall loop splits at the pick's edge in {len(stray_layers)} layers: {stray_layers[:8]}"
    near_ends = toolpath.tip_path_ends(tp, cx, cy, apex + 0.05, neck_top + 0.1, feats=None, tol=0.3)
    assert not near_ends, f"{len(near_ends)} path ends within 0.3 mm of the pick's edge, e.g. {near_ends[:5]}"
    # the pick's loops (not the column, not the block, not the lead-in zones): seam on one face, aligned, scarfed
    block_top = base_top + STANDUP["held_drop"]
    pick_loops = [l for l in loops if block_top + 1.0 < l[0] < height - 2.0 and abs(l[1] - tower_x) > 6.0]
    assert len(pick_loops) > 350, f"only {len(pick_loops)} pick loops found"
    off_face = [l for l in pick_loops if abs(l[2] - cy) < 0.3]
    assert not off_face, f"{len(off_face)} of {len(pick_loops)} seams sit at the rim, e.g. {[(round(l[0], 2), round(l[1], 2), round(l[2], 2)) for l in off_face[:3]]}"
    sides = {1 if l[2] > cy else -1 for l in pick_loops}
    assert len(sides) == 1, "the seam flips between the two faces"
    seam_x = [l[1] for l in pick_loops]
    strip = STANDUP["seam_strip"] + 0.3
    astray = [l for l in pick_loops if abs(l[1] - cx) > strip]
    assert not astray, f"{len(astray)} of {len(pick_loops)} seams sit outside the painted strip, e.g. {[(round(l[0], 2), round(l[1] - cx, 2)) for l in astray[:4]]}"
    assert not any(l[3] for l in pick_loops), "unexpected z ramps inside the pick's outer walls"
    face = "+y (bed rear)" if sides == {1} else "-y (bed front)"
    grams = float(grab("weight"))
    result.update({"time": res["time"], "minutes": round(int(grab("prediction")) / 60), "grams": round(grams, 2),
                   "metres": round(used_m, 2), "used_g_per_filament": round(used_g, 2), "layers": res["layers"],
                   "top_z": z_top, "nozzle_C": int(temp), "bed_C": int(bed),
                   "seam": {"face": face, "x_from_pick_centre_mm": [round(min(seam_x) - cx, 2), round(max(seam_x) - cx, 2)],
                            "pick_loops": len(pick_loops)},
                   "neck_wall_off_midplane_mm": round(neck_y, 3), "neck_lines": 2,
                   "edge_path_ends": {"neck_zone_outer_wall": len(neck_ends), "neck_zone_any_within_0.3": len(near_ends),
                                      "neck_zone_z": [round(apex + 0.05, 2), round(neck_top + 0.1, 2)],
                                      "stray_split_layers_above": [round(z, 2) for z in stray_layers],
                                      "layers_checked_to_z": round(height - 1.0, 2)},
                   "overhang_fraction_of_outer_wall": round(overhang, 3),
                   "toolpath_xy_mm": [round(v, 2) for v in xy], "feature_mm": feature_mm})
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
