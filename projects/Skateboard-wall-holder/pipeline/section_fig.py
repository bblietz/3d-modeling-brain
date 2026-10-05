"""True section figures of the docked scene from the exported meshes (trimesh slices, matplotlib fills).

images/section-side.png     the whole hook with the truck docked, cut at the holder's center plane (z = 0)
images/section-cradle.png   close-up of the cradle with the hanger's half-round, same cut
images/section-across.png   cut across the width through the cradle bottom (x = cradle center): the saddle
images/section-lip.png      cut across the width through the lip toward the room: the same dip, cradling the dome

Usage: .venv/bin/python projects/Skateboard-wall-holder/pipeline/section_fig.py   (run skateboard_holder.py first)
"""
import pathlib
import sys

import matplotlib
import numpy as np
import trimesh

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MplPolygon  # noqa: E402

PROJ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJ))
import skateboard_holder as M  # noqa: E402  (rebuilds the model and its checks)

B, IMG = PROJ / "build", PROJ / "images"
PARTS = [("deck", "#c9a06a"), ("wheels", "#e9e4d6"), ("truck", "#aab2bc"), ("nut", "#f6c453"), ("holder-design", "#f28c28")]


def polys(mesh, origin, normal):
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    if s is None:
        return []
    p2, T = (s.to_2D if hasattr(s, "to_2D") else s.to_planar)()
    out = []
    for p in p2.polygons_full:
        ring = np.c_[np.array(p.exterior.coords), np.zeros(len(p.exterior.coords)), np.ones(len(p.exterior.coords))]
        out.append((T @ ring.T).T[:, :3])          # back to 3D world coordinates
    return out


def draw(ax, origin, normal, axes):
    """axes: which world coordinates become the figure's (horizontal, vertical)."""
    for name, col in PARTS:
        for ring in polys(trimesh.load(B / f"{name}.stl"), origin, normal):
            ax.add_patch(MplPolygon(ring[:, list(axes)], closed=True, facecolor=col, edgecolor="#333", lw=0.6))


def figure(path, origin, normal, axes, xlim, ylim, title, labels=()):
    fig, ax = plt.subplots(figsize=(7, 7 * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])), dpi=160)
    draw(ax, origin, normal, axes)
    if axes[0] == 0:
        ax.axvspan(-30, 0, color="#d8d4cc", zorder=0)      # the wall, only in views from the side
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    ax.set_xlabel("mm from the wall" if axes[0] == 0 else "mm across the board")
    ax.set_ylabel("mm along the deck, up")
    ax.set_title(title, fontsize=10)
    ax.grid(True, lw=0.3, alpha=0.5)
    for x, y, text in labels:
        ax.annotate(text, (x, y), fontsize=8, ha="left", va="bottom")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    print("wrote", pathlib.Path(path).relative_to(PROJ))


cx, cy = M.CRADLE_C[0], M.y_top(M.CRADLE_C[0])
figure(IMG / "section-side.png", [0, 0, 0], [0, 0, 1], (0, 1), (-25, 100), (-125, 40),
       "Section at the holder's center plane: top truck docked, wall at left",
       [(2, -6, "plate"), (M.REACH + 2, -48, "tongue end"), (cx - 4, cy - 10, "cradle"), (M.AXLE_X - 8, 30, "wheel")])
figure(IMG / "section-cradle.png", [0, 0, 0], [0, 0, 1], (0, 1), (30, 80), (-60, -10),
       f"Cradle close-up: R{M.CRADLE_R:g} arc, hanger rests at ({cx:.0f}, {cy:.0f}); room rim {M.HOLD_ROOM:.1f} mm above it, wall rim {M.HOLD_WALL:.1f} mm",
       [(M.X_RIM_ROOM - 1, M.Y_RIM_ROOM + 0.5, "rim"), (M.X_RIM_WALL - 9, M.Y_ROOT + 0.5, "rim"), (cx + 1, cy - 5, "contact")])
figure(IMG / "section-across.png", [cx, 0, 0], [1, 0, 0], (2, 1), (-40, 40), (-62, -18),
       f"Section across the width at the cradle bottom: R{M.SADDLE_R:g} saddle, rims {M.SAG:.1f} mm up",
       [(-14, cy + M.SAG + 0.5, "rim"), (0.5, cy - 4, "contact")])
figure(IMG / "section-lip.png", [M.REACH - 1.0, 0, 0], [1, 0, 0], (2, 1), (-40, 40), (-50, -6),
       f"Section across the lip toward the room (x = {M.REACH - 1:.0f}): the dip follows the cradle, rims {M.SAG:.1f} mm up",
       [(-14, M.Y_RIM_ROOM + M.SAG + 0.5, "rim"), (0.5, M.Y_RIM_ROOM - 4, "lip floor")])
