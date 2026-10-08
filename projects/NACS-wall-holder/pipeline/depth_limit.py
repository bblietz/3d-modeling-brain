"""How deep can the wand cavity go inside the drum?  Exports the raw cavity (part="cavity") at several cleat_depth
values and measures its far reach across the drum (max radius of the vertices past the drum's centre line) and
its Z extent (mouth_z = 0, so z is relative to the mouth centre)."""
import math, os, re, subprocess, sys, tempfile
import numpy as np, trimesh

PROJECT = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/NACS-wall-holder"
O = os.path.expanduser("~/.local/bin/openscad")
# args: cleat depths, plus name=value overrides passed to OpenSCAD (e.g. tip_gap=4 drum_r=46); drum_r here follows the override
over = [a for a in sys.argv[1:] if "=" in a]
drum_r = float(dict(o.split("=") for o in over).get("drum_r", 45.0))   # 40 until 2026-10-08
depths = [float(a) for a in sys.argv[1:] if "=" not in a] or [31.75, 38.1, 44.45, 50.8, 57.15]
for cd in depths:
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([O, "--backend=Manifold", "-D", "display=false", "-D", "show_nose=false", "-D", "show_wall=false",
                            "-D", 'part="cavity"', "-D", "mouth_z=0", "-D", f"cleat_depth={cd}"] + sum([["-D", o] for o in over], []) + ["-o", f"{tmp}/c.stl", f"{PROJECT}/holder.scad"],
                           capture_output=True, text=True)
        m = trimesh.load(f"{tmp}/c.stl")
        mouth = float(re.search(r"mouth depth=([-0-9.]+)", r.stderr + r.stdout).group(1))
    V = m.vertices
    far = V[(V[:, 0] - V[:, 1]) < 0]                       # past the drum's centre line, toward the cavity's end
    rad = np.hypot(far[:, 0], far[:, 1])
    i = rad.argmax()
    # also the reach of the end-wall region only (within 10 mm of the end wall along the wand), to see which corner limits
    z = V[:, 2]
    print(f"cleat_depth {cd:6.2f} ({cd / 25.4:.2f} in): mouth depth {mouth:5.1f}; far reach r = {rad.max():5.2f} -> wall {drum_r - rad.max():5.2f} mm "
          f"at xyz ({far[i, 0]:.1f}, {far[i, 1]:.1f}, {far[i, 2]:.1f}); cavity z from {z.min():6.2f} to {z.max():5.2f} (rel. mouth centre)")
