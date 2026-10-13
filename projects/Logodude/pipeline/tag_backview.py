"""Front and back of one dumped variant as a PNG (agent-side check of the text mirroring)."""
import json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path

g = json.load(open(sys.argv[1]))
def patch(polys, color, flip):
    verts, codes = [], []
    for p in polys:
        for i, ring in enumerate([p["outer"]] + p["holes"]):
            pts = [((-x if flip else x), y) for x, y in ring]
            if (i > 0) == flip: pts = pts[::-1]     # holes wind against the outer ring (nonzero fill rule)
            verts += pts + [pts[0]]; codes += [Path.MOVETO] + [Path.LINETO] * (len(pts) - 1) + [Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), facecolor=color, edgecolor="none")
fig, axes = plt.subplots(1, 2, figsize=(12, 7), dpi=110)
for ax, flip, title in ((axes[0], False, "front (ink up)"), (axes[1], True, "back, as read after flipping over")):
    ax.add_patch(patch(g["backer"], "#f4f4f2", flip)); ax.add_patch(patch(g["ink"] if not flip else g["text"], "#1d1d1f", flip))
    x0, y0, x1, y1 = g["bounds"]; ax.set_xlim(-48, 48); ax.set_ylim(y0 - 3, y1 + 3); ax.set_aspect("equal"); ax.set_facecolor("#d9d7d2"); ax.set_title(title); ax.grid(True, lw=0.3)
fig.tight_layout(); fig.savefig(sys.argv[2]); print("wrote", sys.argv[2])
