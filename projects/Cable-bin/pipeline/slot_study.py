"""Slot-pattern study (2026-10-25). The built 13 x 6 mm slots per wall cut 45 g but added 1 h 43 min per bin; this
sliced fewer, wider slots (7 x 10 mm at 24 mm pitch, 6 x 14 mm at 32 mm pitch) to test the island-count theory.
Result: 6 h 16 min and 6 h 14 min against 6 h 41 min, so islands were not the cause. layer_times.py then showed the
slot band at 232 min against 129 min solid, and the G-code showed 1147 mm per layer at 30 mm/s: the PETG recipe's
small_perimeter_threshold 10 is a RADIUS (loops under 63 mm), so every web loop printed at small_perimeter_speed.
Kept as the variant-build recipe: copies of cable_bin.py and make_print_3mf.py under <outdir>/<name>/ with
constants patched, each model run (its asserts), a side elevation rendered, then the variants sliced two at a time.

Usage (from the vault root, inside a memory-capped scope):
  .venv/bin/python projects/Cable-bin/pipeline/slot_study.py <outdir>
"""
import json
import os
import re
import subprocess
import sys

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Cable-bin"
PY = f"{VAULT}/.venv/bin/python"
OPENSCAD = os.path.expanduser("~/.local/bin/openscad")
OUT = sys.argv[1]
VARIANTS = {
    "s10p24": {"SLOT_W": 10.0, "SLOT_PITCH": 24.0},   # 14 mm webs
    "s14p32": {"SLOT_W": 14.0, "SLOT_PITCH": 32.0},   # 18 mm webs
}


def setconst(src, name, val):
    new, n = re.subn(rf"^{name} = [0-9.]+", f"{name} = {val}", src, count=1, flags=re.M)
    assert n == 1, name
    return new


def main():
    for name, consts in VARIANTS.items():
        d = f"{OUT}/{name}"
        os.makedirs(f"{d}/pipeline", exist_ok=True)
        src = open(f"{PROJ}/cable_bin.py").read()
        for k, v in consts.items():
            src = setconst(src, k, v)
        open(f"{d}/cable_bin.py", "w").write(src)
        m = open(f"{PROJ}/pipeline/make_print_3mf.py").read()
        old = 'sys.path.insert(0, os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline"))'
        assert m.count(old) == 1
        m = m.replace(old, f'sys.path.insert(0, "{VAULT}/projects/Sharks-nametag/pipeline")')
        open(f"{d}/pipeline/make_print_3mf.py", "w").write(m)
        r = subprocess.run([PY, f"{d}/cable_bin.py"], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
        print(name, [l for l in r.stdout.splitlines() if "slots per wall" in l][0])
        scad = f"{d}/side.scad"
        with open(scad, "w") as f:
            f.write(f'color("#5b8def") import("{d}/cable-bin-half-a.stl");\ncolor("#e8a33d") import("{d}/cable-bin-half-b.stl");\n')
        subprocess.run([OPENSCAD, "--backend=Manifold", "--preview", "--viewall", "--autocenter", "--projection=o",
                        "--camera=0,0,0,90,0,0,0", "--imgsize=1600,520", "-o", f"{d}/side.png", scad],
                       check=True, capture_output=True)
    procs = [(n, subprocess.Popen([PY, f"{OUT}/{n}/pipeline/make_print_3mf.py"],
                                  stdout=open(f"{OUT}/{n}/slice.log", "w"), stderr=subprocess.STDOUT)) for n in VARIANTS]
    for name, p in procs:
        p.wait()
        assert p.returncode == 0, f"{name}: see {OUT}/{name}/slice.log"
        b = json.load(open(f"{OUT}/{name}/cable-bin-slice.json"))["plates"][0]
        print(name, VARIANTS[name], b["time"], b["grams"], "g")


if __name__ == "__main__":
    main()
