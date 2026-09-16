"""Bambu Studio print 3MF for the NACS organizer in PETG, verified by a real slice.

Adapted from projects/Leader-cards/make_plate.py (the CLI writes "Cool Plate",
and any key changed in a project 3MF must be listed in
different_settings_to_system or Studio's GUI resets it on open).
X2D 0.6 nozzle, 0.30mm Standard, Bambu PETG Basic, Textured PEI Plate, with the
PETG lessons from the Sharks nametag (see SCALARS / LISTS).

Usage:  .venv/bin/python projects/NACS-organizer/make_plate.py
Writes: projects/NACS-organizer/nacs-organizer-v20-print.3mf and prints real minutes and grams.
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
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Sharks-nametag", "pipeline"))
from graft_slice import graft_slice  # noqa: E402

# the live Studio bundle; ~/.config/BambuStudio is a stale 02.07 copy (knowledge/x2d-printer-control.md)
ROOT = os.path.expanduser("~/.config/BambuStudioBeta/system/BBL")

MACHINE = "Bambu Lab X2D 0.6 nozzle"
PROCESS = "0.30mm Standard @BBL X2D 0.6 nozzle"
FILAMENT = "Bambu PETG Basic @BBL X2D"

STEM = "nacs-organizer-v20"
LABEL = "NACS Organizer v20"
BED_CENTRE = (128.0, 128.0)
BED_TYPE = "Textured PEI Plate"  # PETG preset bed is 70 C here, the temp the Sharks tags printed at
# PETG lessons from knowledge/learnings/sharks-nametag.md, minus the lettering,
# multi-color and arachne tuning that only fit small raised text:
# no ironing + two top walls + top 60 (coupon C), closed seams and slow small
# loops (loop start/stop marks), and a 2-loop skirt with a slow first layer
# (an un-primed nozzle wrecked the first PETG island twice).
SCALARS = {
    "curr_bed_type": BED_TYPE,
    "ironing_type": "no ironing",
    "top_one_wall_type": "not apply",
    "seam_gap": "0%",
    "skirt_loops": "2",
    "skirt_distance": "3",
    "skirt_height": "1",
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
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
    """Resolve the inherits chain; the CLI cannot do this for X2D presets."""
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
    for kind, name, fn in (
        ("machine", MACHINE, "machine.json"),
        ("process", PROCESS, "process.json"),
        ("filament", FILAMENT, "filament.json"),
    ):
        with open(f"{d}/{fn}", "w") as f:
            json.dump(flatten(kind, name), f)


def patch(src, dst):
    """Centre the build item in XY and apply the PETG overrides."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                s = data.decode()
                assert s.count("<item ") == 1, "expected one build item"
                # keep the CLI's Z: this mesh is stored centred, so Z 0 would sink it
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
                # Auto For Flush can route the colour to the X2D's Bowden support nozzle
                cfg["filament_map_mode"] = "Manual"
                data = json.dumps(cfg, indent=4).encode()
            elif item.filename == "Metadata/model_settings.config":
                s = re.sub(r'value="[^"]*\.stl"', f'value="{LABEL}"', data.decode())
                s = s.replace('key="filament_map_mode" value="Auto For Flush"', 'key="filament_map_mode" value="Manual"')
                data = s.encode()
            zout.writestr(item, data)
    zin.close()


def verify(path, tmp):
    """Slice it for real; a CLI round trip alone does not prove sliceability."""
    z = zipfile.ZipFile(path)
    cfg = json.loads(z.read("Metadata/project_settings.config"))
    for k, v in SCALARS.items():
        assert cfg[k] == v, f"{k} did not stick: {cfg[k]}"
    for k, v in LISTS.items():
        assert set(cfg[k]) == {v}, f"{k} did not stick: {cfg[k]}"
    assert (set(SCALARS) | set(LISTS)) <= set(cfg["different_settings_to_system"][0].split(";"))
    assert cfg["printer_settings_id"] == MACHINE, cfg["printer_settings_id"]
    assert cfg["filament_settings_id"] == [FILAMENT], cfg["filament_settings_id"]
    assert cfg["textured_plate_temp"] == ["70"], cfg["textured_plate_temp"]
    assert cfg["filament_map_mode"] == "Manual", cfg["filament_map_mode"]
    assert 'key="filament_map_mode" value="Manual"' in z.read("Metadata/model_settings.config").decode()
    t = re.search(r'<item [^>]*transform="([^"]*)"', z.read("3D/3dmodel.model").decode()).group(1).split()
    assert (float(t[9]), float(t[10])) == BED_CENTRE, t

    # The CLI cannot slice its own project files (rc 156); graft_slice adds the
    # GUI-only keys to a throwaway copy, so the shipped file stays unpatched.
    out = f"{tmp}/sliced.3mf"
    res = graft_slice(path, out)
    assert res.get("rc") == 0 and os.path.exists(out), f"slice failed rc={res.get('rc')}"
    info = zipfile.ZipFile(out).read("Metadata/slice_info.config").decode()
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
    return {"minutes": round(int(grab("prediction")) / 60), "grams": round(float(grab("weight")), 1),
            "layers": res.get("layers")}


def main():
    with tempfile.TemporaryDirectory() as tmp:
        write_presets(tmp)
        shutil.copy(f"{HERE}/{STEM}.stl", f"{tmp}/{STEM}.stl")
        # --export-3mf must be a bare filename; an absolute path alongside
        # --outputdir makes the CLI exit 243 without writing anything.
        subprocess.run(
            ["bambu-studio", "--arrange", "1",
             "--load-settings", "machine.json;process.json",
             "--load-filaments", "filament.json",
             "--export-3mf", "raw.3mf", "--outputdir", ".", f"{STEM}.stl"],
            cwd=tmp, capture_output=True, text=True, timeout=600)
        assert os.path.exists(f"{tmp}/raw.3mf"), "CLI export failed"
        final = f"{HERE}/{STEM}-print.3mf"
        patch(f"{tmp}/raw.3mf", final)
        result = verify(final, tmp)
    print(final, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
