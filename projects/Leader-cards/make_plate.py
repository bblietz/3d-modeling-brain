"""Bambu Studio print 3MF for one leader-card part, verified by a real slice.

Adapted from projects/Garmin-943-helm-panel/make_plate.py; see its docstring for
why: the CLI writes "Cool Plate" and leaves the part off the plate, and any key
changed in a project 3MF must be listed in different_settings_to_system or
Studio's GUI resets it on open.
X2D 0.4 nozzle, 0.20mm Standard, Bambu PETG Basic, Textured PEI Plate.

Usage:  .venv/bin/python projects/Leader-cards/make_plate.py coupon|card
Writes: projects/Leader-cards/<name>-print.3mf and prints real minutes and grams.
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

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")

MACHINE = "Bambu Lab X2D 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL X2D"
FILAMENT = "Bambu PETG Basic @BBL X2D 0.4 nozzle"

BED_CENTRE = (128.0, 128.0)
OVERRIDES = {"curr_bed_type": "Textured PEI Plate"}
NAMES = {"coupon": "leader-card-coupon", "card": "leader-card"}


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


def patch(src, dst, label):
    """Centre the single build item on the plate and apply the overrides."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                s = data.decode()
                assert s.count("<item ") == 1, "expected one build item"
                s = re.sub(r'(<item [^>]*?)transform="[^"]*"',
                           r'\1transform="1 0 0 0 1 0 0 0 1 %g %g 0"' % BED_CENTRE, s, count=1)
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
                # the CLI names the object after the input file; keep it readable
                data = re.sub(r'value="[^"]*\.stl"', f'value="{label}"', data.decode()).encode()
            zout.writestr(item, data)
    zin.close()


def verify(path, tmp):
    """Slice it for real; a CLI round trip alone does not prove sliceability."""
    cfg = json.loads(zipfile.ZipFile(path).read("Metadata/project_settings.config"))
    for k, v in OVERRIDES.items():
        assert cfg[k] == v, f"{k} did not stick: {cfg[k]}"
    assert set(OVERRIDES) <= set(cfg["different_settings_to_system"][0].split(";"))
    assert cfg["printer_settings_id"] == MACHINE, cfg["printer_settings_id"]
    assert cfg["filament_settings_id"] == [FILAMENT], cfg["filament_settings_id"]

    # The CLI cannot slice its own project files (rc 156); graft_slice adds the
    # GUI-only keys to a throwaway copy, so the shipped file stays unpatched.
    out = f"{tmp}/sliced.3mf"
    res = graft_slice(path, out)
    assert res.get("rc") == 0 and os.path.exists(out), f"slice failed rc={res.get('rc')}"
    info = zipfile.ZipFile(out).read("Metadata/slice_info.config").decode()
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
    return {"minutes": round(int(grab("prediction")) / 60), "grams": round(float(grab("weight")), 1)}


def main(which):
    name = NAMES[which]
    with tempfile.TemporaryDirectory() as tmp:
        write_presets(tmp)
        shutil.copy(f"{HERE}/{name}.stl", f"{tmp}/{name}.stl")
        # --export-3mf must be a bare filename; an absolute path alongside
        # --outputdir makes the CLI exit 243 without writing anything.
        r = subprocess.run(
            ["bambu-studio", "--arrange", "1",
             "--load-settings", "machine.json;process.json",
             "--load-filaments", "filament.json",
             "--export-3mf", "raw.3mf", "--outputdir", ".", f"{name}.stl"],
            cwd=tmp, capture_output=True, text=True, timeout=600)
        assert os.path.exists(f"{tmp}/raw.3mf"), f"CLI export failed rc={r.returncode}"
        final = f"{HERE}/{name}-print.3mf"
        patch(f"{tmp}/raw.3mf", final, name)
        result = verify(final, tmp)
    print(final, result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
