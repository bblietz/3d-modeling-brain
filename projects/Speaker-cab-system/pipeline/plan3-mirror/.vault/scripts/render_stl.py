#!/usr/bin/env python
"""Headless STL screenshot for visual verification.

Usage: render_stl.py <model.stl> <out.png> [elev,azim ...]

Renders shaded views with matplotlib (no GPU or display needed).
Default views: isometric, front, top, right.
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

DEFAULT_VIEWS = [("iso", 30, -60), ("front", 0, -90), ("top", 90, -90), ("right", 0, 0)]


def main():
    stl_path, png_path = sys.argv[1], sys.argv[2]
    if len(sys.argv) > 3:
        views = [(f"view{i}", *map(float, arg.split(","))) for i, arg in enumerate(sys.argv[3:])]
    else:
        views = DEFAULT_VIEWS

    mesh = trimesh.load_mesh(stl_path)
    tris = mesh.vertices[mesh.faces]

    # Simple directional shading per facet
    light = np.array([0.4, -0.5, 0.75])
    light = light / np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip(mesh.face_normals @ light, 0, 1)
    colors = np.outer(shade, np.array([0.55, 0.65, 0.85]))

    lo, hi = mesh.bounds
    center, radius = (lo + hi) / 2, (hi - lo).max() / 2 * 1.05

    n = len(views)
    ncols = min(n, 2)
    nrows = (n + ncols - 1) // ncols
    fig = plt.figure(figsize=(6 * ncols, 5.5 * nrows))
    for i, (name, elev, azim) in enumerate(views):
        ax = fig.add_subplot(nrows, ncols, i + 1, projection="3d")
        pc = Poly3DCollection(tris, facecolors=colors, edgecolor="none")
        ax.add_collection3d(pc)
        ax.set_xlim(center[0] - radius, center[0] + radius)
        ax.set_ylim(center[1] - radius, center[1] + radius)
        ax.set_zlim(center[2] - radius, center[2] + radius)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(f"{name} (elev={elev}, azim={azim})")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
    fig.tight_layout()
    fig.savefig(png_path, dpi=110)
    print(f"rendered {n} views -> {png_path}")


if __name__ == "__main__":
    main()
