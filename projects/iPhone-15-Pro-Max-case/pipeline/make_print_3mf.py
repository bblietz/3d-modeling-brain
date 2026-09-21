"""Bambu Studio print 3MF for the iPhone 15 Pro Max case: TWO plates, one per material, each verified by a real slice.

  plate 1  the case, Bambu TPU 95A HF (filament 1)
  plate 2  the camera guard ring, Bambu PETG Basic (filament 2; rim face on the bed, plug and barb up)

Brian, 2026-09-20: "the guard should be petg and snap into place. The 3mf file should be 2 plates, one for the guard and one
for the case". Route: the CLI's own multi-plate assembler (--load-assemble-list), as in projects/Sharks-nametag/pipeline/plates.py:
it authors the plates, places the parts and sets the per-part filament itself, so none of that is hand-written. Then the usual
post-patch (overrides, extruder map, names, colours) and graft_slice per plate.

X2D 0.4 nozzle, 0.20mm Standard, Textured PEI. Both filaments on extruder 1, the direct-drive main nozzle (TPU needs the direct
drive; extruder 2 is the low-accuracy Bowden one, not for a snap fit). Overrides, all listed in different_settings_to_system so
the GUI keeps them; process settings are project-wide, so both plates get them, and each is right for both parts:
  wall_generator arachne    the case's 1.5 mm walls and the ring's tapering plug print as solid variable-width lines, no gap fill
  reduce_crossing_wall 1    travels follow the wall instead of stringing across the open cavity
  wall_loops 4              the 1.5 mm walls, their roots, the lip and the 3 mm ring are all concentric walls
  sparse_infill_density 100%, zig-zag    whatever the walls do not fill prints solid. Checked by weight, not by G-code label
                            (Bambu keeps the "Sparse infill" label at 100%)
  skirt 2 loops at 3 mm, first layer 30 mm/s    the vault's PETG rule (NACS-organizer/make_plate.py): an un-primed nozzle wrecked
                            the first PETG island twice, and the ring's first layer is its visible face. Harmless on the TPU plate.

Usage:  .venv/bin/python projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py
Reads iphone-15-pro-max-case.stl and camera-guard-ring.stl (both already in print orientation); writes
iphone-15-pro-max-case-print.3mf and iphone-15-pro-max-case-print-slice.json (per plate: real minutes, grams, layers, G-code features).
Brian opening the 3MF in Bambu Studio is the ground truth for the plates and the settings.
"""
import json
import os
import re
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

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")

MACHINE = "Bambu Lab X2D 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL X2D"          # the unsuffixed X2D process presets are the 0.4 nozzle ones
PLATES = [   # one plate per material; filament n = position in this list
    {"plate": "Case TPU 95A HF", "stl": "iphone-15-pro-max-case.stl", "label": "iPhone 15 Pro Max case (TPU 95A HF)",
     "filament": "Bambu TPU 95A HF @BBL X2D 0.4 nozzle", "colour": "#2F6F4F"},
    {"plate": "Camera guard PETG", "stl": "camera-guard-ring.stl", "label": "Camera guard ring (PETG, rim down, barb up)",
     "filament": "Bambu PETG Basic @BBL X2D 0.4 nozzle", "colour": "#C9772B"},      # the PETG preset Brian has printed with (Leader cards, Sharks tags)
]
OUT = "iphone-15-pro-max-case-print.3mf"
BED_CENTRE = (128.0, 128.0)
PLATE_STRIDE = 307.2          # plate 2's origin in world x (256 x 1.2)
BED_TYPE = "Textured PEI Plate"

SCALARS = {
    "curr_bed_type": BED_TYPE,
    "wall_generator": "arachne",
    "reduce_crossing_wall": "1",
    "wall_loops": "4",
    "sparse_infill_density": "100%",
    "sparse_infill_pattern": "zig-zag",
    "skirt_loops": "2",
    "skirt_distance": "3",
    "skirt_height": "1",
}
LISTS = {"initial_layer_speed": "30", "initial_layer_infill_speed": "50"}      # one value per extruder variant
FILAMENT_MAP = ["1", "1"]     # extruder per filament: both on 1, the direct drive


def load(kind, name):
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
    """Resolve the inherits chain and each preset's include templates; the CLI cannot do this for X2D presets.
    The X2D machine presets keep all their G-code in include templates (without them the CLI slices with a
    generic start G-code), and the X2D filament presets include the six-variant filament template."""
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


def matrix(transform):
    """3MF transform (12 numbers, row-major 3x3 then the translation) as a 4x4 that acts on column vectors."""
    t = [float(v) for v in transform.split()] if transform else [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    m = np.eye(4)
    m[:3, :3] = np.array(t[:9]).reshape(3, 3).T
    m[:3, 3] = t[9:]
    return m


def world_bounds(z):
    """{build item's object id: (lo, hi)} in world mm, from the meshes and transforms in the 3MF itself. Where a part
    stands on a plate is item transform x component transform x the mesh's own coordinates; none of the three is reliably zero."""
    main = z.read("3D/3dmodel.model").decode()
    comps = {}
    for oid, body in re.findall(r'<object id="(\d+)"[^>]*>(.*?)</object>', main, re.S):
        comps[oid] = re.findall(r'<component p:path="([^"]+)" objectid="(\d+)"(?: [^>]*?transform="([^"]*)")?', body)
    out = {}
    for oid, transform in re.findall(r'<item objectid="(\d+)"[^>]*?transform="([^"]*)"', main):
        pts = []
        for path, sub_id, comp_t in comps[oid]:
            sub = z.read(path.lstrip("/")).decode()
            mesh = re.search(rf'<object id="{sub_id}"[^>]*>(.*?)</object>', sub, re.S).group(1)
            v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', mesh), dtype=float)
            pts.append((matrix(transform) @ matrix(comp_t) @ np.c_[v, np.ones(len(v))].T).T[:, :3])
        pts = np.vstack(pts)
        out[oid] = (pts.min(axis=0), pts.max(axis=0))
    return out


def plate_members(model_settings):
    """[(plate name, [object names])] from model_settings.config."""
    names = dict(re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]*)"', model_settings))
    out = []
    for block in re.findall(r"<plate>(.*?)</plate>", model_settings, re.S):
        pname = re.search(r'key="plater_name" value="([^"]*)"', block).group(1)
        out.append((pname, [names[i] for i in re.findall(r'key="object_id" value="(\d+)"', block)]))
    return out


def patch(src, dst):
    """Apply the overrides, put both filaments on extruder 1, name and colour things. The plates, the parts' places on them
    and the per-part filament are the CLI's own work and stay as written."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "Metadata/project_settings.config":
                cfg = json.loads(data)
                cfg.update(SCALARS)
                for k, v in LISTS.items():
                    assert isinstance(cfg[k], list), f"{k} is not a per-variant list: {cfg[k]!r}"
                    cfg[k] = [v] * len(cfg[k])
                diff = cfg.get("different_settings_to_system") or [""]
                diff[0] = ";".join(sorted(set(x for x in diff[0].split(";") if x) | set(SCALARS) | set(LISTS)))
                cfg["different_settings_to_system"] = diff
                # the CLI writes these per-filament vectors with one entry; every one needs an entry per filament
                cfg["filament_map_mode"], cfg["filament_map"], cfg["filament_nozzle_map"] = "Manual", FILAMENT_MAP, FILAMENT_MAP
                cfg["filament_colour"] = cfg["filament_multi_colour"] = [p["colour"] for p in PLATES]
                # the slicer wants filaments^2 x len(flush_multiplier) matrix entries, one multiplier per extruder (the CLI leaves a
                # 4 x 4 matrix and one multiplier: "Flush volumes matrix do not match"). No plate ever changes filament; Studio's defaults.
                ne, nf = len(cfg["nozzle_diameter"]), len(PLATES)
                cfg["flush_multiplier"], cfg["flush_multiplier_fast"] = ["1"] * ne, ["1.2"] * ne
                cfg["flush_volumes_matrix"] = ["0" if a == b else "280" for _ in range(ne) for a in range(nf) for b in range(nf)]
                cfg["flush_volumes_vector"] = ["140"] * (ne * nf)
                data = json.dumps(cfg, indent=4).encode()
            elif item.filename == "Metadata/model_settings.config":
                def name(m):   # the assembler calls every object assemble_1: name object and part after the part, filament at both levels
                    n, p = next((n, p) for n, p in enumerate(PLATES, 1) if f'key="source_file" value="{p["stl"]}"' in m.group(0))
                    block = re.sub(r'(<metadata key="name" value=")[^"]*"', lambda k: k.group(1) + p["label"] + '"', m.group(0))
                    return re.sub(r'(<object id="\d+">\s*<metadata key="name" value="[^"]*"/>)', rf'\1\n    <metadata key="extruder" value="{n}"/>', block, count=1)
                ms = re.sub(r"<object id=.*?</object>", name, data.decode(), flags=re.S)
                maps = " ".join(FILAMENT_MAP)
                ms = re.sub(r'( *)<metadata key="filament_map_mode" value="[^"]*"/>',
                            lambda m: f'{m.group(1)}<metadata key="filament_map_mode" value="Manual"/>\n{m.group(1)}<metadata key="filament_maps" value="{maps}"/>', ms)
                data = ms.encode()
            zout.writestr(item, data)
    zin.close()


def gcode_features(gcode):
    """Extruded filament length (mm) per G-code feature, to see bridges, overhang walls and any sparse infill."""
    used, feat = {}, ""
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line[:3] in ("G1 ", "G2 ", "G3 "):
            me = re.search(r" E([-0-9.]+)", line)
            if me and float(me.group(1)) > 0 and (" X" in line or " Y" in line):
                used[feat] = used.get(feat, 0.0) + float(me.group(1))
    return {k: round(v, 1) for k, v in sorted(used.items(), key=lambda kv: -kv[1])}


def check_structure(path, what):
    z = zipfile.ZipFile(path)
    got = plate_members(z.read("Metadata/model_settings.config").decode())
    want = [(p["plate"], [p["label"]]) for p in PLATES]
    assert got == want, f"{what}: plates are {got}, wanted {want}"
    ms = z.read("Metadata/model_settings.config").decode()
    for n, p in enumerate(PLATES, 1):
        block = re.search(rf'<object id="\d+">\s*<metadata key="name" value="{re.escape(p["label"])}"/>(.*?)</object>', ms, re.S).group(1)
        assert set(re.findall(r'key="extruder" value="(\d+)"', block)) == {str(n)}, f'{what}: {p["label"]} is not on filament {n}'
    return z


def verify(path, tmp):
    """Structure, a CLI round trip, then a real slice of each plate. A round trip alone does not prove sliceability."""
    z = check_structure(path, "authored file")
    cfg = json.loads(z.read("Metadata/project_settings.config"))
    for k, v in SCALARS.items():
        assert cfg[k] == v, f"{k} did not stick: {cfg[k]}"
    for k, v in LISTS.items():
        assert set(cfg[k]) == {v}, f"{k} did not stick: {cfg[k]}"
    assert set(SCALARS) | set(LISTS) <= set(cfg["different_settings_to_system"][0].split(";"))
    assert cfg["printer_settings_id"] == MACHINE, cfg["printer_settings_id"]
    assert cfg["filament_settings_id"] == [p["filament"] for p in PLATES], cfg["filament_settings_id"]
    assert cfg["filament_type"] == ["TPU", "PETG"] and cfg["filament_map"] == FILAMENT_MAP and cfg["filament_map_mode"] == "Manual", (cfg["filament_type"], cfg["filament_map"])
    assert cfg["nozzle_diameter"][0] == "0.4" and cfg["layer_height"] == "0.2", (cfg["nozzle_diameter"], cfg["layer_height"])
    for k in ("filament_colour", "filament_type", "filament_density", "filament_ids", "filament_is_support", "textured_plate_temp"):
        assert len(cfg[k]) == len(PLATES), f"{k} has {len(cfg[k])} entries for {len(PLATES)} filaments"

    r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", path], cwd=tmp, capture_output=True, text=True, timeout=600)
    assert os.path.exists(f"{tmp}/roundtrip.3mf"), f"round trip failed rc={r.returncode}\n{r.stdout[-1500:]}"
    check_structure(f"{tmp}/roundtrip.3mf", "CLI round trip")

    result = {}
    for n, p in enumerate(PLATES, 1):
        out = f"{tmp}/sliced{n}.3mf"
        res = graft_slice(path, out, plate=n)
        assert res.get("rc") == 0 and os.path.exists(out) and res.get("gcode"), f"plate {n} slice failed rc={res.get('rc')}, log {res.get('log')}"
        zs = zipfile.ZipFile(out)
        info = zs.read("Metadata/slice_info.config").decode()
        grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
        used = {fid: float(g) for fid, g in re.findall(r'<filament id="(\d+)"[^>]*?used_g="([^"]*)"', info)}
        assert set(used) == {str(n)}, f"plate {n} uses filaments {used}, wanted only filament {n}"
        gcode = zs.read(res["gcode"]).decode(errors="replace")
        assert "X2D start gcode" in gcode, "the X2D start G-code is missing: the machine include templates did not merge"
        preset = flatten("filament", p["filament"])
        temp, bed = preset["nozzle_temperature"][0], preset["textured_plate_temp"][0]
        assert re.search(rf"^\s*M10[49] S{temp}\b", gcode, re.M), f"plate {n}: nozzle temperature {temp} of {p['filament']} is not in the G-code"
        assert re.search(rf"^\s*M1[49]0 S{bed}\b", gcode, re.M), f"plate {n}: bed temperature {bed} of {p['filament']} is not in the G-code"
        # extruder 1 = nozzle group 0 in slice_info (a T command in Bambu G-code picks the filament, not the extruder)
        group = re.search(rf'<filament id="{n}"[^>]*?group_id="(\d+)"', info).group(1)
        assert re.search(r"^; filament_map = 1,1$", gcode, re.M) and group == "0", f"plate {n} does not print from extruder 1 (nozzle group {group})"
        # the slicer weighs what it extrudes, and PETG Basic extrudes at a flow ratio of 0.95 (TPU 95A HF at 1.0)
        solid_g = trimesh.load(f"{PROJECT}/{p['stl']}").volume / 1000 * float(cfg["filament_density"][n - 1]) * float(preset["filament_flow_ratio"][0])
        grams = used[str(n)]
        # the skirt is a few hundredths of a gram; solid means the sliced weight is the mesh volume's weight
        assert 0.97 * solid_g <= grams <= 1.06 * solid_g, f"plate {n} is not solid: {grams:.2f} g sliced, {solid_g:.2f} g if solid"
        lo, hi = world_bounds(zs)[re.search(rf'<object id="(\d+)">\s*<metadata key="name" value="{re.escape(p["label"])}"', zs.read("Metadata/model_settings.config").decode()).group(1)]
        cx, cy = (lo[0] + hi[0]) / 2 - (n - 1) * PLATE_STRIDE, (lo[1] + hi[1]) / 2
        assert abs(cx - BED_CENTRE[0]) < 1 and abs(cy - BED_CENTRE[1]) < 1 and abs(lo[2]) < 0.01, f"plate {n}: part centre {cx:.1f}, {cy:.1f}, bottom z {lo[2]:.3f}"
        result[f"plate {n}"] = {"part": p["label"], "filament": p["filament"], "nozzle_C": int(temp), "bed_C": int(bed), "minutes": round(int(grab("prediction")) / 60),
                                "grams": round(grams, 2), "grams_if_solid": round(float(solid_g), 2), "layers": res["layers"], "feature_mm": gcode_features(gcode)}
    result["minutes"] = sum(v["minutes"] for v in result.values())
    result["grams"] = round(sum(v["grams"] for k, v in result.items() if k.startswith("plate")), 1)
    return result


def main():
    final = f"{PROJECT}/{OUT}"
    with tempfile.TemporaryDirectory() as tmp:
        for kind, name in (("machine", MACHINE), ("process", PROCESS)):
            with open(f"{tmp}/{kind}.json", "w") as f:
                json.dump(flatten(kind, name), f)
        for n, p in enumerate(PLATES, 1):
            with open(f"{tmp}/filament{n}.json", "w") as f:
                json.dump(flatten("filament", p["filament"]), f)
        # pos is where the STL's own origin goes on the plate (plate-relative; the CLI adds the plate's origin), so take off
        # the part's own centre: the ring's STL sits 15 x 56 mm off its origin
        centre = {n: trimesh.load(f"{PROJECT}/{p['stl']}").bounds.mean(axis=0) for n, p in enumerate(PLATES, 1)}
        spec = {"plates": [{"plate_name": p["plate"], "need_arrange": False, "plate_params": {"curr_bed_type": BED_TYPE},
                            "objects": [{"path": f"{PROJECT}/{p['stl']}", "count": 1, "filaments": [n], "assemble_index": [1],
                                         "pos_x": [float(BED_CENTRE[0] - centre[n][0])], "pos_y": [float(BED_CENTRE[1] - centre[n][1])], "pos_z": [0]}],
                            "assembled_params": [{"assemble_index": 1, "print_params": {}}]}
                           for n, p in enumerate(PLATES, 1)]}
        with open(f"{tmp}/assemble.json", "w") as f:
            json.dump(spec, f, indent=1)
        # --export-3mf must be a bare filename; an absolute path alongside --outputdir makes the CLI exit 243.
        # No input files alongside an assemble list, and no --load-filament-ids (the filaments come from the list).
        r = subprocess.run(
            ["bambu-studio", "--arrange", "0", "--load-assemble-list", "assemble.json", "--load-settings", "machine.json;process.json",
             "--load-filaments", ";".join(f"filament{n}.json" for n in range(1, len(PLATES) + 1)), "--export-3mf", "raw.3mf", "--outputdir", "."],
            cwd=tmp, capture_output=True, text=True, timeout=600)
        assert os.path.exists(f"{tmp}/raw.3mf"), f"CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
        patch(f"{tmp}/raw.3mf", final)
        result = verify(final, tmp)
    with open(final.replace(".3mf", "-slice.json"), "w") as f:
        json.dump(result, f, indent=1)
    print(final)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
