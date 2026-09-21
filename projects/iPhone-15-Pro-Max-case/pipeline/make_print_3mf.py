"""Bambu Studio print 3MF for the iPhone 15 Pro Max case in TPU 95A HF, verified by a real slice.

Adapted from projects/Garmin-943-helm-panel/make_plate.py (single filament: flatten the X2D
presets, CLI export, patch, graft slice). X2D 0.4 nozzle, 0.20mm Standard, Bambu TPU 95A HF,
Textured PEI. Overrides, all listed in different_settings_to_system so the GUI keeps them:
  wall_generator arachne    the 1.5 mm walls print as solid variable-width lines, no gap fill
  reduce_crossing_wall 1    travels follow the wall instead of stringing TPU across the open cavity
  wall_loops 4              the 1.5 mm walls, their roots and the lip are all concentric walls
  sparse_infill_density 100%, zig-zag    whatever the walls do not fill prints solid: at the stock 15% the 5 mm guard ring
                            gets a sparse core, a soft spot in TPU. Checked by weight, not by G-code label (Bambu keeps the
                            "Sparse infill" label at 100%)

Usage:  .venv/bin/python projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py
Reads iphone-15-pro-max-case.stl and camera-guard-ring.stl (both already in print orientation); writes
iphone-15-pro-max-case-print.3mf with both on one plate, and iphone-15-pro-max-case-print-slice.json with
real minutes, grams, layers and the G-code feature list.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline"))
from graft_slice import graft_slice  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")

MACHINE = "Bambu Lab X2D 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL X2D"          # the unsuffixed X2D process presets are the 0.4 nozzle ones
FILAMENT = "Bambu TPU 95A HF @BBL X2D 0.4 nozzle"
PARTS = {"case.stl": ("iphone-15-pro-max-case.stl", "iPhone 15 Pro Max case"),          # name on the plate: (source STL, label in Studio)
         "guard-ring.stl": ("camera-guard-ring.stl", "Camera guard ring (rim down, plug up)")}
OUT = "iphone-15-pro-max-case-print.3mf"
BED_CENTRE = (128.0, 128.0)

OVERRIDES = {
    "curr_bed_type": "Textured PEI Plate",
    "wall_generator": "arachne",
    "reduce_crossing_wall": "1",
    "wall_loops": "4",
    "sparse_infill_density": "100%",
    "sparse_infill_pattern": "zig-zag",
}


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


def patch(src, dst):
    """Keep the CLI's arrangement but move its middle to the bed centre, apply the overrides, name the objects."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                s = data.decode()
                items = [t.split() for t in re.findall(r'<item [^>]*?transform="([^"]*)"', s)]
                assert len(items) == len(PARTS), (len(items), len(PARTS))
                # the CLI keeps each mesh where its STL put it and arranges with the item transform, so a part's
                # place on the bed is transform + the STL's own bounds (the ring's STL is 15 x 56 mm off its origin)
                lo, hi = [], []
                for t, (stl, _) in zip(items, PARTS.values()):
                    b = trimesh.load(f"{PROJECT}/{stl}").bounds
                    lo.append((float(t[9]) + b[0][0], float(t[10]) + b[0][1]))
                    hi.append((float(t[9]) + b[1][0], float(t[10]) + b[1][1]))
                dx = BED_CENTRE[0] - (min(p[0] for p in lo) + max(p[0] for p in hi)) / 2
                dy = BED_CENTRE[1] - (min(p[1] for p in lo) + max(p[1] for p in hi)) / 2

                def shift(m):
                    t = m.group(2).split()
                    t[9], t[10] = "%g" % (float(t[9]) + dx), "%g" % (float(t[10]) + dy)
                    return '%stransform="%s"' % (m.group(1), " ".join(t))

                s = re.sub(r'(<item [^>]*?)transform="([^"]*)"', shift, s)
                data = s.encode()
            elif item.filename == "Metadata/project_settings.config":
                cfg = json.loads(data)
                cfg.update(OVERRIDES)
                diff = cfg.get("different_settings_to_system") or [""]
                existing = [x for x in diff[0].split(";") if x]
                diff[0] = ";".join(sorted(set(existing) | set(OVERRIDES)))
                cfg["different_settings_to_system"] = diff
                data = json.dumps(cfg, indent=4).encode()
            elif item.filename == "Metadata/model_settings.config":
                s = data.decode()
                for plate_name, (_, label) in PARTS.items():
                    s = s.replace(f'value="{plate_name}"', f'value="{label}"')
                data = s.encode()
            zout.writestr(item, data)
    zin.close()


def gcode_features(gcode):
    """Extruded filament length (mm) per G-code feature, to see bridges and any sparse infill."""
    used, feat = {}, ""
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line[:3] in ("G1 ", "G2 ", "G3 "):
            me = re.search(r" E([-0-9.]+)", line)
            if me and float(me.group(1)) > 0 and (" X" in line or " Y" in line):
                used[feat] = used.get(feat, 0.0) + float(me.group(1))
    return {k: round(v, 1) for k, v in sorted(used.items(), key=lambda kv: -kv[1])}


def verify(path, tmp):
    """Slice it for real. A CLI round trip alone does not prove sliceability."""
    z = zipfile.ZipFile(path)
    cfg = json.loads(z.read("Metadata/project_settings.config"))
    for k, v in OVERRIDES.items():
        assert cfg[k] == v, f"{k} did not stick: {cfg[k]}"
    assert set(OVERRIDES) <= set(cfg["different_settings_to_system"][0].split(";"))
    assert cfg["printer_settings_id"] == MACHINE, cfg["printer_settings_id"]
    assert cfg["filament_settings_id"] == [FILAMENT], cfg["filament_settings_id"]
    assert cfg["nozzle_diameter"][0] == "0.4" and cfg["layer_height"] == "0.2", (cfg["nozzle_diameter"], cfg["layer_height"])
    assert set(cfg["nozzle_temperature"]) == {"230"}, cfg["nozzle_temperature"]      # the TPU 95A HF preset, not a fallback

    out = f"{tmp}/sliced.3mf"
    res = graft_slice(path, out)
    assert res.get("rc") == 0 and os.path.exists(out), f"slice failed rc={res.get('rc')}, log {res.get('log')}"
    zs = zipfile.ZipFile(out)
    info = zs.read("Metadata/slice_info.config").decode()
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
    gcode = zs.read(res["gcode"]).decode(errors="replace")
    assert "X2D start gcode" in gcode, "the X2D start G-code is missing: the machine include templates did not merge"
    assert re.search(r"^M10[49] S230", gcode, re.M), "the TPU 95A HF nozzle temperature (230) is not in the G-code"
    features = gcode_features(gcode)
    solid_g = sum(trimesh.load(f"{PROJECT}/{stl}").volume for stl, _ in PARTS.values()) / 1000 * float(cfg["filament_density"][0])
    grams = float(grab("weight"))
    assert grams >= 0.97 * solid_g, f"the print is not solid TPU: {grams:.1f} g sliced, {solid_g:.1f} g if solid"
    # the slicer re-centres each mesh, so its item transforms are the parts' real centres: both on the bed, plate centred
    items = [t.split() for t in re.findall(r'<item [^>]*?transform="([^"]*)"', zs.read("3D/3dmodel.model").decode())]
    ext = [trimesh.load(f"{PROJECT}/{stl}").extents for stl, _ in PARTS.values()]
    x0 = min(float(t[9]) - e[0] / 2 for t, e in zip(items, ext)); x1 = max(float(t[9]) + e[0] / 2 for t, e in zip(items, ext))
    y0 = min(float(t[10]) - e[1] / 2 for t, e in zip(items, ext)); y1 = max(float(t[10]) + e[1] / 2 for t, e in zip(items, ext))
    assert abs((x0 + x1) / 2 - BED_CENTRE[0]) < 1 and abs((y0 + y1) / 2 - BED_CENTRE[1]) < 1, (x0, x1, y0, y1)
    return {"minutes": round(int(grab("prediction")) / 60), "grams": round(grams, 1), "grams_if_solid": round(float(solid_g), 1), "layers": res["layers"],
            "plate_bbox": [round(float(v), 1) for v in (x0, x1, y0, y1)], "feature_mm": features}


def main():
    final = f"{PROJECT}/{OUT}"
    with tempfile.TemporaryDirectory() as tmp:
        for kind, name in (("machine", MACHINE), ("process", PROCESS), ("filament", FILAMENT)):
            with open(f"{tmp}/{kind}.json", "w") as f:
                json.dump(flatten(kind, name), f)
        for plate_name, (stl, _) in PARTS.items():
            shutil.copy(f"{PROJECT}/{stl}", f"{tmp}/{plate_name}")
        # --export-3mf must be a bare filename; an absolute path alongside --outputdir makes the CLI exit 243
        r = subprocess.run(
            ["bambu-studio", "--arrange", "1", "--load-settings", "machine.json;process.json",
             "--load-filaments", "filament.json", "--export-3mf", "raw.3mf", "--outputdir", ".", *PARTS],
            cwd=tmp, capture_output=True, text=True, timeout=600)
        assert os.path.exists(f"{tmp}/raw.3mf"), f"CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
        patch(f"{tmp}/raw.3mf", final)
        result = verify(final, tmp)
    with open(final.replace(".3mf", "-slice.json"), "w") as f:
        json.dump(result, f, indent=1)
    print(final, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
