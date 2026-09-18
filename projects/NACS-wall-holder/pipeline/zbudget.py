"""Does the wand cavity fit between the plate and the flange?  Measures the real cavity (holder.scad, part="probe")
inside the drum radius and reports the room behind its deepest corner, how far the mouth runs into the flange
blend, and the gap between the grip and the wall.  Use it to set mouth_z after changing wand_lean, cleat_depth or drum_l.

    .venv/bin/python projects/NACS-wall-holder/pipeline/zbudget.py [wand_lean ...]
"""
import math
import os
import re
import subprocess
import sys
import tempfile

import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
SCAD = open(f"{PROJECT}/holder.scad").read()
GRIP_HALF = 22.0  # half width of the grip across the wand


def const(name):
    return float(re.search(rf"(?:^|;)\s*{name}\s*=\s*([-0-9.]+)", SCAD, re.M).group(1))


def probe(lean):
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([os.path.expanduser("~/.local/bin/openscad"), "--backend=Manifold", "-D", "display=false",
                            "-D", "show_nose=false", "-D", "show_wall=false", "-D", 'part="probe"', "-D", f"wand_lean={lean}",
                            "-D", "mouth_z=0", "-o", f"{tmp}/p.stl", f"{PROJECT}/holder.scad"], capture_output=True, text=True)
        z = trimesh.load(f"{tmp}/p.stl").vertices[:, 2]
        mouth = float(re.search(r"mouth depth=([-0-9.]+)", r.stderr + r.stdout).group(1))
    return z.min(), z.max(), mouth


def main():
    BEHIND = const("behind")   # solid left behind the cavity's deepest corner (the plate is 5 mm)
    drum_l, plate_t, flange_t, fillet = const("drum_l"), const("plate_t"), const("flange_t"), const("fillet_flange")
    blend_z = plate_t + drum_l - flange_t - fillet       # the flange blend starts here on the drum surface
    leans = [float(a) for a in sys.argv[1:]] or [const("wand_lean")]
    print(f"drum {drum_l:.0f}: plate front at {plate_t:.0f}, flange blend from {blend_z:.0f}, flange underside at {blend_z + fillet:.0f}; mouth_z now {const('mouth_z')}")
    for lean in leans:
        lo, hi, mouth = probe(lean)
        mouth_z = BEHIND - lo
        top = mouth_z + hi
        wz = math.cos(math.radians(lean)) / math.sqrt(2) / math.sqrt(1 - math.cos(math.radians(lean)) ** 2 / 2)
        gap = lambda q: mouth_z + q * math.sin(math.radians(lean)) - GRIP_HALF * wz
        print(f"lean {lean:4.1f}: cavity {hi - lo:5.1f} tall, mouth depth {mouth:5.1f}; mouth_z = {mouth_z:5.2f} leaves {BEHIND:.0f} mm behind the deepest corner; "
              f"mouth top at {top:5.1f} = {top - blend_z:+5.1f} into the blend, {blend_z + fillet - top:4.1f} under the flange; "
              f"grip to wall {gap(35):4.1f} / {gap(80):4.1f} / {gap(140):4.1f} mm (grip start / middle / end)")


if __name__ == "__main__":
    main()
