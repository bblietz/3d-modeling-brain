#!/usr/bin/env python3
"""Bambu Studio project 3MF for the guitar neck rest: one plate, one object, proven by a real slice.

    .venv/bin/python projects/Guitar-neck-rest/pipeline/make_print_3mf.py [--scratch DIR]

Reads guitar-neck-rest.stl (build.py; print frame, lying on one face with the cradle toward the back of the plate).
Writes guitar-neck-rest.3mf and 3mf-report.json beside it. Plumbing only: the STL is not touched.

The recipe is the vault's (memory/feedback-stl-to-bambu-3mf.md, memory/reference-x2d-preset-includes.md), not a new one:
  presets   slice_stls.py's include-merging flattener over the installed BBL bundle: machine "Bambu Lab X2D 0.6 nozzle",
            process "0.30mm Standard @BBL X2D 0.6 nozzle", filament "Bambu PLA Basic @BBL X2D 0.6 nozzle"
  overrides written into the flattened presets before the export AND into the 3MF's project_settings with their
            different_settings_to_system entries, or Studio's GUI resets them on open: process slot [0], filament slot [1]
  bed       Textured PEI Plate at 65 C for PLA (knowledge/printer-x2d.md: the preset's 55 C let edges peel)
  seam      "back": the part lies with its cradle toward the back of the plate, so the outline's seam lands on the
            cradle side, under the pad or on a shoulder, and never on the rocking curve. Proven from the G-code.
  slice     projects/Sharks-nametag/pipeline/graft_slice.py (the CLI cannot slice its own export), one slice, inside the
            memory-capped systemd scope (CLAUDE.md, heavy local jobs)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
PROJECT = VAULT / "projects" / "Guitar-neck-rest"
sys.path.insert(0, str(VAULT / "projects" / "Fishing-rod-holder" / "pipeline"))
sys.path.insert(0, str(VAULT / "projects" / "Sharks-nametag" / "pipeline"))
from graft_slice import graft_slice  # noqa: E402
from slice_stls import MACHINE, MATERIALS, PROCESS, SCOPE, flatten  # noqa: E402

STL = PROJECT / "guitar-neck-rest.stl"
OUT = PROJECT / "guitar-neck-rest.3mf"
FILAMENT = MATERIALS["pla"]
NAME = "Guitar neck rest"
LAYER = "0.3"
BED_C = "65"
SIZE = (148.7, 108.5, 80.0)      # print frame, from build-report.json's solid
PROCESS_KEYS = {
    "curr_bed_type": "Textured PEI Plate",
    "brim_type": "no_brim",
    "skirt_loops": "2",          # memory/feedback-keep-skirt.md, never 0
    "skirt_distance": "3",
    "skirt_height": "1",
    "wall_loops": "2",
    "sparse_infill_density": "15%",
    "seam_position": "back",
    "enable_support": "0",
}
FILAMENT_KEYS = {"textured_plate_temp": [BED_C], "textured_plate_temp_initial_layer": [BED_C]}
SCOPE_MARK = "NECK_REST_3MF_IN_SCOPE"
NOTE = ("Open guitar-neck-rest.3mf once in Bambu Studio and look at the sliced preview: the GUI is the ground truth. "
        "Pick the filament colour there.")


def write_presets(d):
    process = flatten("process", PROCESS) | PROCESS_KEYS
    filament = flatten("filament", FILAMENT) | FILAMENT_KEYS
    for fn, preset in (("machine.json", flatten("machine", MACHINE)), ("process.json", process), ("filament.json", filament)):
        (d / fn).write_text(json.dumps(preset))


def author(src, dst):
    """The CLI export with the overrides recorded where Studio's GUI looks for them, and a friendly object name."""
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "Metadata/project_settings.config":
                cfg = json.loads(data)
                cfg.update(PROCESS_KEYS)
                cfg.update(FILAMENT_KEYS)
                n_fil = len(cfg["filament_settings_id"])
                assert n_fil == 1, cfg["filament_settings_id"]
                diff = cfg.get("different_settings_to_system") or []
                diff += [""] * (n_fil + 2 - len(diff))       # positional: [0] process, [1] the filament, [2] machine
                for slot, keys in ((0, PROCESS_KEYS), (1, FILAMENT_KEYS)):
                    diff[slot] = ";".join(sorted(set(x for x in diff[slot].split(";") if x) | set(keys)))
                cfg["different_settings_to_system"] = diff
                cfg["filament_map_mode"], cfg["filament_map"], cfg["filament_nozzle_map"] = "Manual", ["1"], ["1"]
                data = json.dumps(cfg, indent=4).encode()
            elif item.filename == "Metadata/model_settings.config":
                text = data.decode()
                assert f'key="name" value="{STL.name}"' in text, "object name not found in model_settings.config"
                data = text.replace(f'key="name" value="{STL.name}"', f'key="name" value="{NAME}"').encode()
            zout.writestr(item, data)


def check_settings(path, what):
    with zipfile.ZipFile(path) as z:
        cfg = json.loads(z.read("Metadata/project_settings.config"))
        msc = z.read("Metadata/model_settings.config").decode()
        model_files = [n for n in z.namelist() if n.endswith(".model")]
    for k, v in (PROCESS_KEYS | FILAMENT_KEYS).items():
        assert cfg[k] == v, f"{what}: {k} did not stick: {cfg[k]}"
    diff = cfg["different_settings_to_system"]
    assert len(diff) == 3, f"{what}: different_settings_to_system has {len(diff)} slots"
    assert set(PROCESS_KEYS) <= set(diff[0].split(";")), f"{what}: process keys missing from slot 0: {diff[0]}"
    assert set(FILAMENT_KEYS) <= set(diff[1].split(";")), f"{what}: filament keys missing from slot 1: {diff[1]}"
    assert cfg["printer_settings_id"] == MACHINE and cfg["print_settings_id"] == PROCESS and cfg["filament_settings_id"] == [FILAMENT], \
        (cfg["printer_settings_id"], cfg["print_settings_id"], cfg["filament_settings_id"])
    assert cfg["nozzle_diameter"][0] == "0.6" and cfg["layer_height"] == LAYER, (cfg["nozzle_diameter"], cfg["layer_height"])
    objects = re.findall(r'<object id="(\d+)">', msc)
    plates = re.findall(r"<plate>", msc)
    assert len(objects) == 1 and len(plates) == 1, f"{what}: {len(objects)} objects on {len(plates)} plates"
    assert f'key="name" value="{NAME}"' in msc, f"{what}: the object is not named {NAME}"
    return {"objects": len(objects), "plates": len(plates), "model_files": len(model_files)}


def gcode_facts(gcode):
    """Top layer height, extruded length per feature, where every outer wall loop starts (the seam), and the xy box of
    the outer walls (where the part sits on the plate)."""
    feat, x, y, z_top, used = "", 0.0, 0.0, 0.0, {}
    seams, pending, box = [], False, [1e9, 1e9, -1e9, -1e9]
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
            pending = feat == "Outer wall"
        elif line.startswith("; Z_HEIGHT:"):
            z_top = max(z_top, float(line.split(":")[1]))
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, me = re.search(r" X([-0-9.]+)", line), re.search(r" Y([-0-9.]+)", line), re.search(r" E([-0-9.]+)", line)
            x0, y0 = x, y
            x, y = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if feat and me and float(me.group(1)) > 0 and (mx or my):
                used[feat] = used.get(feat, 0.0) + float(me.group(1))
                if feat == "Outer wall":
                    box = [min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y)]
                    if pending:
                        seams.append((x0, y0, z_top))
                        pending = False
    return z_top, {k: round(v, 1) for k, v in sorted(used.items(), key=lambda kv: -kv[1])}, seams, box


def slice_check(path, tmp):
    out = tmp / "sliced.3mf"
    res = graft_slice(str(path), str(out))
    log = Path(res["log"]).read_text() if res.get("log") and os.path.exists(res["log"]) else ""
    assert res.get("rc") == 0 and res.get("gcode"), f"slice failed rc={res.get('rc')}\n{log[-2000:]}"
    with zipfile.ZipFile(out) as z:
        info = z.read("Metadata/slice_info.config").decode()
        gcode = z.read(res["gcode"]).decode(errors="replace")
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
    seconds, grams = int(grab("prediction")), float(grab("weight"))
    assert "X2D start gcode" in gcode, "the X2D start G-code is missing: the machine include templates did not merge"
    for k, v in (PROCESS_KEYS | {"layer_height": LAYER}).items():
        assert re.search(rf"^; {k} = {re.escape(v)}$", gcode, re.M), f"{k} = {v} is not in the sliced G-code"
    assert re.search(rf"^\s*M1[49]0 S{BED_C}\b", gcode, re.M), f"bed temperature {BED_C} is not in the G-code"
    assert re.search(r"^; nozzle_diameter = 0\.6(,0\.6)*$", gcode, re.M), "nozzle_diameter is not 0.6 in the G-code"
    z_top, feature_mm, seams, box = gcode_facts(gcode)
    assert "Skirt" in feature_mm and "Brim" not in feature_mm, f"expected a skirt and no brim: {feature_mm}"
    assert "Support" not in " ".join(feature_mm), f"supports were generated: {feature_mm}"
    assert abs(z_top - SIZE[2]) <= float(LAYER) + 1e-6, f"the sliced top is at z {z_top}, the part is {SIZE[2]} mm"
    dx, dy = box[2] - box[0], box[3] - box[1]
    assert abs(dx - SIZE[0]) < 1.5 and abs(dy - SIZE[1]) < 1.5, f"the part is not lying as exported: outer walls span {dx:.1f} x {dy:.1f}"
    # Seams: height up the standing rocker = distance from the front of the part. The rocking curve is the front
    # (0 to about 24 mm up); the opening's top is at about 82, the cradle floor at 93.7, the shoulders at 108.5.
    ups = [y - box[1] for _, y, _ in seams]
    assert min(ups) > 60, f"a seam sits {min(ups):.1f} mm up the rocker, off the cradle side"
    outline = [u for u in ups if u > 90]
    return {"time": f"{seconds // 3600} h {seconds % 3600 // 60:02d} min", "minutes": round(seconds / 60), "seconds": seconds,
            "grams": round(grams, 1), "layers": res["layers"], "top_z": z_top, "bed_C": int(BED_C),
            "outer_walls_span_mm": [round(dx, 1), round(dy, 1)], "feature_mm": feature_mm,
            "seams": {"loops": len(seams), "lowest_mm_up_the_rocker": round(min(ups), 1), "on_the_cradle_side": len(outline),
                      "inside_the_opening_top": len(ups) - len(outline)}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scratch", type=Path, default=None)
    args = ap.parse_args()
    os.environ["PATH"] = f"{Path.home() / '.local/bin'}:{os.environ.get('PATH', '')}"
    if SCOPE_MARK not in os.environ and shutil.which("systemd-run"):
        if subprocess.run(SCOPE + ["true"], capture_output=True).returncode == 0:
            os.environ[SCOPE_MARK] = "1"
            os.execvp(SCOPE[0], SCOPE + [sys.executable] + sys.argv)
        print("warning: systemd-run scope unavailable; slicing without a memory cap", file=sys.stderr)

    tmp = args.scratch or Path(tempfile.mkdtemp(prefix="neck-rest-3mf-"))
    tmp.mkdir(parents=True, exist_ok=True)
    write_presets(tmp)
    shutil.copy(STL, tmp / STL.name)
    r = subprocess.run(["bambu-studio", "--arrange", "1", "--load-settings", "machine.json;process.json",
                        "--load-filaments", "filament.json", "--export-3mf", "raw.3mf", "--outputdir", ".", STL.name],
                       cwd=tmp, capture_output=True, text=True, timeout=600)
    assert (tmp / "raw.3mf").exists(), f"CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    author(tmp / "raw.3mf", tmp / OUT.name)
    report = {"file": OUT.name, "machine": MACHINE, "process": PROCESS, "filament": FILAMENT,
              "overrides": PROCESS_KEYS | {k: v[0] for k, v in FILAMENT_KEYS.items()},
              "authored": check_settings(tmp / OUT.name, "authored file")}
    r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", OUT.name],
                       cwd=tmp, capture_output=True, text=True, timeout=600)
    assert (tmp / "roundtrip.3mf").exists(), f"round trip failed rc={r.returncode}\n{r.stdout[-1500:]}"
    report["roundtrip"] = check_settings(tmp / "roundtrip.3mf", "CLI round trip")
    report["slice"] = slice_check(tmp / OUT.name, tmp)
    report["note"] = NOTE
    shutil.copy(tmp / OUT.name, OUT)
    (PROJECT / "3mf-report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
