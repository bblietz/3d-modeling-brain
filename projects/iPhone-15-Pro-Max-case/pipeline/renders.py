"""Coloured renders for review.html: OpenSCAD previews of the exported meshes (z-buffered, a third of a second each).

Usage:  .venv/bin/python projects/iPhone-15-Pro-Max-case/pipeline/renders.py
Reads iphone-15-pro-max-case.stl, camera-guard-ring.stl and build/{ring-seated,phone-proxy}.stl; writes images/render-*.png.
"""
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
OPENSCAD = os.path.expanduser("~/.local/bin/openscad")
CASE, RING, PHONE = "#2f6f4f", "#c9772b", "#b9bec5"          # the viewer's and the sections' colours


def part(colour, stl, lift=0.0):
    return f'color("{colour}") translate([0, 0, {lift}]) import("{PROJECT}/{stl}");\n'


SEATED = part(CASE, "iphone-15-pro-max-case.stl") + part(RING, "build/ring-seated.stl")
JOBS = {   # picture: (scene, camera = look-at x, y, z, rotation x, y, z, distance). The back of the case faces -z: rotation x > 180 looks at it.
    "render-back": (SEATED, "15,56,0,215,0,25,170"),
    "render-exploded": (part(CASE, "iphone-15-pro-max-case.stl") + part(RING, "build/ring-seated.stl", -12), "15,56,-5,235,0,25,190"),
    "render-inside": (SEATED, "15,56,0,35,0,25,150"),
    "render-ring-print": (part(RING, "camera-guard-ring.stl"), "15,56,2,62,0,30,120"),
    "render-whole": (SEATED + part(PHONE, "build/phone-proxy.stl"), "0,0,0,215,0,25,480"),
}
with tempfile.TemporaryDirectory() as tmp:
    for name, (scene, camera) in JOBS.items():
        with open(f"{tmp}/{name}.scad", "w") as f:
            f.write(scene)
        subprocess.run([OPENSCAD, "--backend=Manifold", "--preview", "--imgsize=1400,1000", "--projection=p", f"--camera={camera}",
                        "--colorscheme=Tomorrow", "-o", f"{PROJECT}/images/{name}.png", f"{tmp}/{name}.scad"], check=True, capture_output=True)
        print("wrote", name)
