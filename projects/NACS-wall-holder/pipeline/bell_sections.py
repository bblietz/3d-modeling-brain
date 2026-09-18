"""Cut Tesla's connector housing (reference/nacs-500v-connector-housing.stl, STEP body 8) behind the nose
shoulder and write bell_sections.scad: the outer outline at stations along the wand, in the same frame as
nose_outline.scad ([across, button side up], nose centre origin, notch side -Y).

    .venv/bin/python projects/NACS-wall-holder/pipeline/bell_sections.py
"""
import os

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
TIP_X = -1.99            # nose tip in the STL's X; s = x - TIP_X is the distance from the tip
CY, CZ = 4.0, 4.25       # nose centre in the STL's Y, Z (same centring as nose_outline.scad)
STATIONS = [32.5, 34, 36, 38, 40, 42, 43, 44, 45, 46, 47, 48.2]   # mm from the tip; the housing ends at 48.36


def outline(mesh, s):
    sec = mesh.section(plane_origin=[TIP_X + s, 0, 0], plane_normal=[1, 0, 0])
    polys = []
    for ent in sec.discrete:
        p = Polygon([(y - CY, z - CZ) for _, y, z in ent])
        if p.is_valid and p.area > 1:
            polys.append(p)
    outer = unary_union(polys).convex_hull          # the cavity only has to clear the handle: a hull is safe
    return outer.simplify(0.02)


def main():
    mesh = trimesh.load(f"{PROJECT}/reference/nacs-500v-connector-housing.stl")
    rows = []
    for s in STATIONS:
        o = outline(mesh, s)
        x0, y0, x1, y1 = o.bounds
        print(f"s={s:5.1f}  across {x0:7.2f}..{x1:6.2f}  notch side {y0:7.2f}  button side {y1:6.2f}  pts {len(o.exterior.coords) - 1}")
        pts = ", ".join(f"[{x:.3f}, {y:.3f}]" for x, y in list(o.exterior.coords)[:-1])
        rows.append(f"    [{s}, [{pts}]]")
    with open(f"{PROJECT}/bell_sections.scad", "w") as f:
        f.write("// Handle housing behind the nose shoulder, from Tesla's STEP (pipeline/bell_sections.py).\n"
                "// [distance from the nose tip, outline [[across, button side up], ...]], convex hulls of the real sections.\n"
                "bell_sections = [\n" + ",\n".join(rows) + "\n];\n")
    print("wrote bell_sections.scad")


if __name__ == "__main__":
    main()
