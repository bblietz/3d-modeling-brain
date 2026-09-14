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


def facet_shade(mesh: trimesh.Trimesh, shade: np.ndarray) -> np.ndarray:
    """Flatten shading within each coplanar facet group to its mean value.

    A flat panel is exported as many small triangles; per-triangle shading
    from face_normals carries tiny floating-point variance across an
    otherwise-flat surface, and matplotlib's Poly3DCollection has no true
    z-buffer, so that variance (plus its own z-sort ambiguity on many
    near-coplanar triangles) shows up as visible hatching. Curved surfaces
    (the roundover fillets) are not part of a multi-triangle facet and are
    left to vertex_shade() below.
    """
    shade = shade.copy()
    for group in mesh.facets:
        shade[group] = shade[group].mean()
    return shade


def vertex_shade(mesh: trimesh.Trimesh, light: np.ndarray) -> np.ndarray:
    """Per-face shade from vertex normals instead of the face's own normal
    (Gouraud-style shading, approximated: matplotlib flat-shades each
    triangle, so this feeds it an already-smoothed value rather than
    smoothing after the fact). A roundover fillet exports as a narrow band
    of many thin triangles sweeping quickly through a wide range of
    normals; trimesh's vertex normals are already the area-weighted
    average of every face touching that vertex, so averaging a triangle's
    three vertex shades washes out the sharp per-triangle swing across the
    band without blurring real edges (a flat panel's own vertices already
    share its exact normal, since every face touching them agrees)."""
    vshade = 0.35 + 0.65 * np.clip(mesh.vertex_normals @ light, 0, 1)
    return vshade[mesh.faces].mean(axis=1)


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
    shade = vertex_shade(mesh, light)
    shade = facet_shade(mesh, shade)
    colors = np.outer(shade, np.array([0.55, 0.65, 0.85]))

    lo, hi = mesh.bounds
    center, radius = (lo + hi) / 2, (hi - lo).max() / 2 * 1.05

    n = len(views)
    ncols = min(n, 2)
    nrows = (n + ncols - 1) // ncols
    fig = plt.figure(figsize=(6 * ncols, 5.5 * nrows))
    for i, (name, elev, azim) in enumerate(views):
        ax = fig.add_subplot(nrows, ncols, i + 1, projection="3d")
        # A panel viewed near edge-on still hatches even with uniform shading: many
        # thin triangles project to almost the same on-screen sliver, and matplotlib's
        # painter's-algorithm sort (no real z-buffer) flickers their draw order. A
        # thick edge stroke in the triangle's own fill color caulks that flicker shut;
        # edgecolor "none" (no stroke) is what let it show through.
        pc = Poly3DCollection(tris, facecolors=colors, edgecolors=colors, linewidths=3.0, antialiased=True)
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
