#!/usr/bin/env python
"""Close-up render of a region of an STL (top-down or tilted), for checking
small features such as debossed labels and tip chamfers.

Usage: closeup.py <model.stl> <out.png> xmin,xmax,ymin,ymax [elev azim]
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def main():
    stl, png = sys.argv[1], sys.argv[2]
    xmin, xmax, ymin, ymax = map(float, sys.argv[3].split(","))
    elev = float(sys.argv[4]) if len(sys.argv) > 4 else 90
    azim = float(sys.argv[5]) if len(sys.argv) > 5 else -90
    mesh = trimesh.load_mesh(stl)
    # keep only triangles whose centroid is in the window (plus margin)
    c = mesh.triangles_center
    m = 2.0
    keep = (c[:, 0] > xmin - m) & (c[:, 0] < xmax + m) & (c[:, 1] > ymin - m) & (c[:, 1] < ymax + m)
    tris = mesh.triangles[keep]
    normals = mesh.face_normals[keep]
    light = np.array([0.3, -0.4, 0.85])
    light /= np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip(normals @ light, 0, 1)
    colors = np.outer(shade, np.array([0.55, 0.65, 0.85]))
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    pc = Poly3DCollection(tris, facecolors=colors, edgecolors=colors, linewidths=0.5)
    ax.add_collection3d(pc)
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    r = max(xmax - xmin, ymax - ymin) / 2
    zmid = mesh.bounds.mean(axis=0)[2]
    ax.set_xlim(cx - r, cx + r)
    ax.set_ylim(cy - r, cy + r)
    ax.set_zlim(zmid - r, zmid + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(png, dpi=120)
    print("wrote", png)


if __name__ == "__main__":
    main()
