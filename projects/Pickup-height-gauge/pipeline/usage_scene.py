#!/usr/bin/env python
"""Render the gauge in use: the 2.8 mm arm slid across under the E string of a
mock P-Bass bass-side pickup half, resting on the two pole pieces that flank
the string. Geometry of the half from StewMac / Amplified Parts spec sheets
(cover 55.5 x 27 x 14.3 mm, 4.95 mm poles flush with the cover, pole pairs
9.5 mm apart, string pairs 19 mm apart, outer string 18.25 mm from the cover
end). Strings sit at the gauge thickness above the poles, as they would once
the pickup is set.

Usage: usage_scene.py <out-prefix>   (writes <out-prefix>-iso.png and <out-prefix>-end.png)
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from build123d import Align, Axis, Box, Cylinder, Pos, Rot, export_stl
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
import pickup_height_gauge as g  # noqa: E402

COVER = (55.5, 27.0, 14.3)
POLE_D, PAIR, STRINGS = 4.95, 9.5, 19.0
POLE_PROUD = 0.5                  # poles drawn standing proud of the cover so they are visible (many are flush)
OUTER_STRING_FROM_END = 18.25
E_DIA, A_DIA = 2.65, 2.1          # 0.105 and 0.085 in roundwounds
ARM = "W"                         # the 2.8 mm arm (standard P, bass side)
PAST_STRING = 8.0                 # how far the arm tip goes past the E string


def build():
    # cover along X (across the strings), top face at z 0, pickguard below
    cover = Pos(0, 0, -COVER[2]) * Box(COVER[0], COVER[1], COVER[2] - POLE_PROUD, align=(Align.CENTER, Align.CENTER, Align.MIN))
    e_x = -COVER[0] / 2 + OUTER_STRING_FROM_END          # E string, bass side of the half
    a_x = e_x + STRINGS
    poles = None
    for sx in (e_x, a_x):
        for dx in (-PAIR / 2, PAIR / 2):
            p = Pos(sx + dx, 0, -COVER[2]) * Cylinder(POLE_D / 2, COVER[2], align=(Align.CENTER, Align.CENTER, Align.MIN))
            poles = p if poles is None else poles + p
    t = g.ARM_T[ARM]
    strings = (Pos(e_x, 0, t + E_DIA / 2) * Rot(90, 0, 0) * Cylinder(E_DIA / 2, 80)) + \
              (Pos(a_x, 0, t + A_DIA / 2) * Rot(90, 0, 0) * Cylinder(A_DIA / 2, 80))
    gauge = Rot(0, 0, 180) * g.build()        # turned so the W (2.8) arm points to +X, into the pickup from the bass end
    tip_x = g.HUB / 2 + g.ARM_LEN
    gauge = Pos(e_x + PAST_STRING - tip_x, 0, 0) * gauge
    assert gauge.bounding_box().min.X + g.HUB / 2 + g.ARM_LEN - g.ARM_LEN < -COVER[0] / 2, "hub must sit outside the cover end"
    return {"cover": cover, "poles": poles, "strings": strings, "gauge": gauge}


def mesh_of(shape, tmp):
    export_stl(shape, tmp, tolerance=0.02, angular_tolerance=0.2)
    m = trimesh.load_mesh(tmp)
    # matplotlib sorts whole triangles by depth: split the big flat faces so small parts (the poles) sort above them
    v, f = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=4.0)
    return trimesh.Trimesh(v, f, process=False)


def render(meshes, out, elev, azim, window, zoom=1.0):
    colors = {"cover": (0.12, 0.12, 0.13), "poles": (0.75, 0.75, 0.78), "strings": (0.85, 0.72, 0.45), "gauge": (0.95, 0.62, 0.15)}
    light = np.array([0.3, -0.5, 0.8])
    light /= np.linalg.norm(light)
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    for name, m in meshes.items():
        tris, normals = m.triangles, m.face_normals
        shade = 0.4 + 0.6 * np.clip(normals @ light, 0, 1)
        col = np.outer(shade, np.array(colors[name]))
        ax.add_collection3d(Poly3DCollection(tris, facecolors=col, edgecolors=col, linewidths=0.4))
    cx, cy = (window[0] + window[1]) / 2, (window[2] + window[3]) / 2
    r = max(window[1] - window[0], window[3] - window[2]) / 2 / zoom
    ax.set_proj_type("ortho")
    ax.set_xlim(cx - r, cx + r)
    ax.set_ylim(cy - r, cy + r)
    ax.set_zlim(-r + 4, r + 4)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print("wrote", out)


def main():
    prefix = sys.argv[1]
    shapes = build()
    tmpdir = os.environ.get("TMPDIR", "/tmp")
    meshes = {k: mesh_of(v, os.path.join(tmpdir, f"scene-{k}.stl")) for k, v in shapes.items()}
    # the E string sits on the arm: check the string bottom is at the arm top, with the arm resting on the poles
    t = g.ARM_T[ARM]
    assert abs(meshes["strings"].bounds[0][2] - t) < 0.01, meshes["strings"].bounds
    assert abs(meshes["gauge"].bounds[0][2]) < 0.01 and abs(meshes["poles"].bounds[1][2]) < 0.01
    render(meshes, prefix + "-iso.png", 28, -55, (-85, 35, -45, 45))
    render(meshes, prefix + "-end.png", 0, -90, (-45, 15, -25, 25), zoom=1.5)


if __name__ == "__main__":
    main()
