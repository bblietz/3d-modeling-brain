#!/usr/bin/env python3
"""Slice STLs with the Bambu Studio CLI and report filament grams and print time per file, for quoting real numbers.

    .venv/bin/python projects/Fishing-rod-holder/pipeline/slice_stls.py [--walls 2] [--infill 15] [--material petg|pla|asa]
        [--out slice-results.json] [--scratch DIR] part1.stl part2.stl ...

Writes --out as {"<basename>.stl": {"grams", "minutes", "time_text", "material", "walls", "infill"}, ...} and prints one
line per file. Plumbing only: nothing here is a design decision.

The recipe is the vault's, not a new one (memory/feedback-stl-to-bambu-3mf.md, memory/reference-x2d-preset-includes.md):
  presets   the include-merging flattener of projects/Cable-bin/pipeline/make_print_3mf.py over the installed BBL bundle:
            machine "Bambu Lab X2D 0.6 nozzle", process "0.30mm Standard @BBL X2D 0.6 nozzle" (the Skateboard, NACS and
            Cable-bin quotes), filament per --material (the X2D 0.6 presets carry no "0.6 nozzle" suffix except PLA)
  export    bambu-studio --arrange 1 --load-settings machine.json;process.json --load-filaments filament.json
            --export-3mf raw.3mf --outputdir . part.stl      (bare output name: an absolute path exits 243 and writes nothing)
  slice     the CLI cannot slice its own export (rc 156, the live X2D extruder keys are GUI-only), so
            projects/Sharks-nametag/pipeline/graft_slice.py adds them to a throwaway copy and runs --slice 1 --export-3mf
  numbers   Metadata/slice_info.config of the sliced 3MF, key "prediction" (seconds) and "weight" (grams), read the way the
            NACS, Skateboard and Cable-bin pipelines read them; the sliced G-code is checked for the X2D start G-code (the
            include merge) and for the wall and infill values actually used
Process overrides, written into the flattened copy before --load-settings: wall_loops and sparse_infill_density from the
command line, the vault's skirt (2 loops, 3 mm, 1 layer; memory/feedback-keep-skirt.md, the Bambu default is none), no brim,
Textured PEI plate. Everything else is the preset default (grid infill, arachne walls).
Slices run one at a time, and the whole batch re-executes itself inside a memory-capped systemd scope (CLAUDE.md, heavy
local jobs) so an overrun kills only this batch.
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
sys.path.insert(0, str(VAULT / "projects" / "Sharks-nametag" / "pipeline"))
from graft_slice import graft_slice  # noqa: E402

ROOT = Path.home() / ".config/BambuStudio/system/BBL"   # the preset bundle of the installed Studio
MACHINE = "Bambu Lab X2D 0.6 nozzle"
PROCESS = "0.30mm Standard @BBL X2D 0.6 nozzle"
MATERIALS = {
    "petg": "Bambu PETG Basic @BBL X2D",       # what every PETG quote in the vault was sliced with
    "pla": "Bambu PLA Basic @BBL X2D 0.6 nozzle",
    "asa": "Bambu ASA @BBL X2D",
}
FIXED = {   # process scope, the vault's print recipe that is not a design choice
    "skirt_loops": "2",
    "skirt_distance": "3",
    "skirt_height": "1",
    "brim_type": "no_brim",
    "curr_bed_type": "Textured PEI Plate",
}
SCOPE = ["systemd-run", "--user", "--scope", "-p", "MemoryMax=44G", "-p", "MemoryHigh=40G",
         "-p", "MemorySwapMax=2G", "-p", "OOMPolicy=continue", "--"]
SCOPE_MARK = "SLICE_STLS_IN_SCOPE"


def load(kind, name):
    with open(ROOT / kind / f"{name}.json") as f:
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


def write_presets(d, walls, infill, material):
    process = flatten("process", PROCESS)
    process.update(FIXED)
    process["wall_loops"] = str(walls)
    process["sparse_infill_density"] = f"{infill}%"
    for name, preset in (("machine.json", flatten("machine", MACHINE)), ("process.json", process),
                         ("filament.json", flatten("filament", MATERIALS[material]))):
        with open(d / name, "w") as f:
            json.dump(preset, f)


def slice_stl(stl, d, walls, infill):
    """Export the STL to a raw 3MF with the presets in d, slice it through the graft, return (seconds, grams)."""
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(stl, d / stl.name)
    r = subprocess.run(
        ["bambu-studio", "--arrange", "1",
         "--load-settings", "machine.json;process.json",
         "--load-filaments", "filament.json",
         "--export-3mf", "raw.3mf", "--outputdir", ".", stl.name],
        cwd=d, capture_output=True, text=True, timeout=600)
    assert (d / "raw.3mf").exists(), f"{stl.name}: CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"

    res = graft_slice(str(d / "raw.3mf"), str(d / "sliced.3mf"))
    log = Path(res["log"]).read_text() if res.get("log") and os.path.exists(res["log"]) else ""
    assert res.get("rc") == 0 and res.get("gcode"), f"{stl.name}: slice failed rc={res.get('rc')}\n{log[-2000:]}"

    with zipfile.ZipFile(d / "sliced.3mf") as z:
        info = z.read("Metadata/slice_info.config").decode()
        gcode = z.read(res["gcode"]).decode(errors="replace")
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
    seconds, grams = int(grab("prediction")), float(grab("weight"))
    assert "X2D start gcode" in gcode, f"{stl.name}: the X2D start G-code is missing: the machine include templates did not merge"
    for k, v in (("wall_loops", str(walls)), ("sparse_infill_density", f"{infill}%")):
        assert re.search(rf"^; {k} = {re.escape(v)}$", gcode, re.M), f"{stl.name}: {k} = {v} is not in the sliced G-code"
    return seconds, grams


def time_text(minutes):
    return f"{minutes // 60}h {minutes % 60}m"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("stls", nargs="+", type=Path)
    ap.add_argument("--walls", type=int, default=2)
    ap.add_argument("--infill", type=int, default=15, help="sparse infill density in percent")
    ap.add_argument("--material", choices=sorted(MATERIALS), default="petg")
    ap.add_argument("--out", type=Path, default=Path("slice-results.json"))
    ap.add_argument("--scratch", type=Path, default=None, help="work dir, one subdir per STL (default: a fresh temp dir)")
    args = ap.parse_args()

    os.environ["PATH"] = f"{Path.home() / '.local/bin'}:{os.environ.get('PATH', '')}"   # graft_slice calls bambu-studio by name
    if SCOPE_MARK not in os.environ and shutil.which("systemd-run"):
        probe = subprocess.run(SCOPE + ["true"], capture_output=True, text=True)
        if probe.returncode == 0:
            # Re-run this exact command inside the memory-capped scope; the CLAUDE.md rule for slicer batches.
            os.environ[SCOPE_MARK] = "1"
            os.execvp(SCOPE[0], SCOPE + [sys.executable] + sys.argv)
        print(f"warning: systemd-run scope unavailable ({probe.stderr.strip()}); slicing without a memory cap", file=sys.stderr)

    names = [p.name for p in args.stls]
    assert len(set(names)) == len(names), f"duplicate STL basenames: {names}"
    for p in args.stls:
        assert p.is_file(), f"not a file: {p}"
    scratch = args.scratch or Path(tempfile.mkdtemp(prefix="slice_stls-"))
    scratch.mkdir(parents=True, exist_ok=True)
    presets = scratch / "presets"
    presets.mkdir(exist_ok=True)
    write_presets(presets, args.walls, args.infill, args.material)
    print(f"{MACHINE} | {PROCESS} | {MATERIALS[args.material]} | {args.walls} walls, {args.infill}% infill | scratch {scratch}")

    results = {}
    for stl in args.stls:   # one slice at a time (CLAUDE.md heavy-jobs rule)
        d = scratch / stl.stem
        d.mkdir(parents=True, exist_ok=True)
        for name in ("machine.json", "process.json", "filament.json"):
            shutil.copy(presets / name, d / name)
        seconds, grams = slice_stl(stl.resolve(), d, args.walls, args.infill)
        minutes = round(seconds / 60)
        results[stl.name] = {"grams": round(grams, 1), "minutes": minutes, "time_text": time_text(minutes),
                             "material": args.material, "walls": args.walls, "infill": args.infill}
        print(f"{stl.name}: {grams:.1f} g, {time_text(minutes)} ({args.material}, {args.walls} walls, {args.infill}% infill)")

    with open(args.out, "w") as f:
        json.dump(results, f, indent=1)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
