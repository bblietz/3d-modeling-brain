#!/usr/bin/env python3
"""To-scale 'measure these' drawing of the closet desk, from the photo-derived numbers in
concept.scad. Output: images/design/measure.png. Every callout is a tape-measure span
Brian can read off and type back."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "images" / "design" / "measure.png"
# photo-derived geometry, inches
W, OPN, D, HT, T = 45, 32, 24, 27.5, 0.75
U = HT - T
JL = (W - OPN) / 2
CLW, CLH = 1.5, 0.75
SX0, SL, SY0, SW, ST = 4, 34, 12, 2.0, 1.9
PW, PT, PH = 1.4, 0.9, 1.5
PZ = U - ST - PH
TODAY = [1, 2, 3, 4, 7]
ox = lambda i: SX0 + 1.6 + i * 3.4
# D as decided: 250 mm wide, 6 in front to back, 6 in deep, top edge 1/2 in under the plug heads
DL, DD, DH = 250 / 25.4, 6, 6
DX0 = W / 2 - DL / 2
DTOP = PZ - 0.5

ORANGE, INK, TAN, DARK, WALL = "#e2711d", "#1d1d1f", "#d9b57a", "#2b2b2e", "#c9c2b4"

def dim_h(ax, x0, x1, y, text, above=True, color=INK):
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", color=color, lw=1.4, shrinkA=0, shrinkB=0))
    ax.plot([x0, x0], [y - 0.4, y + 0.4], color=color, lw=1); ax.plot([x1, x1], [y - 0.4, y + 0.4], color=color, lw=1)
    ax.text((x0 + x1) / 2, y + (0.45 if above else -0.45), text, ha="center", va="bottom" if above else "top",
            fontsize=10.5, color=color, fontweight="bold", bbox=dict(fc="white", ec="none", pad=1.5))

def dim_v(ax, y0, y1, x, text, left=True, color=INK):
    ax.annotate("", xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle="<->", color=color, lw=1.4, shrinkA=0, shrinkB=0))
    ax.plot([x - 0.4, x + 0.4], [y0, y0], color=color, lw=1); ax.plot([x - 0.4, x + 0.4], [y1, y1], color=color, lw=1)
    ax.text(x - (0.5 if left else -0.5), (y0 + y1) / 2, text, ha="right" if left else "left", va="center",
            fontsize=10.5, color=color, fontweight="bold", rotation=90, bbox=dict(fc="white", ec="none", pad=1.5))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 13), gridspec_kw=dict(height_ratios=[1, 1.05]))
fig.patch.set_facecolor("white")

# ---------- side section ----------
ax = ax1
ax.set_title("Side section through the closet (seen from the right)   .   photo-derived numbers, plus or minus 10 percent", fontsize=12, loc="left", pad=10)
ax.add_patch(Rectangle((-8, -1.5), 36, 1.5, fc=WALL, ec="none"))                        # floor
ax.add_patch(Rectangle((D, -1.5), 3, 36, fc=WALL, ec="none", hatch="///"))             # back wall
ax.add_patch(Rectangle((0, U), D, T, fc=TAN, ec=INK, lw=1))                             # slab
ax.add_patch(Rectangle((0, U - CLH), D, CLH, fc="#a3773f", ec=INK, lw=0.8))            # side cleat, behind the section
ax.add_patch(Rectangle((SY0, U - ST), SW, ST, fc=DARK, ec="none"))                      # strip
ax.add_patch(Rectangle((SY0 + SW/2 - PT/2, PZ), PT, PH, fc="black", ec="none"))         # plug head
ax.plot([SY0 + SW/2, SY0 + SW/2 + 0.5, SY0 + 4], [PZ, PZ - 3, PZ - 6], color="black", lw=1.6)   # cord
ax.add_patch(Rectangle((D - DD, DTOP - DH), DD, DH, fc="none", ec=ORANGE, lw=2, ls="--"))  # D decided
ax.add_patch(Rectangle((D - DD, DTOP - DH), 0.16, DH * 0.75, fc=ORANGE, ec="none"))
ax.text(D - DD / 2, DTOP - DH / 2, "D\n(decided)", ha="center", va="center", fontsize=10, color=ORANGE, fontweight="bold")
ax.add_patch(Rectangle((D - 1.5, U - 0.75), 1.5, 0.75, fc="none", ec="#8a2be2", lw=1.5, ls=":"))
ax.annotate("M7: is there a cleat\nalong the back wall?", xy=(D - 0.75, U - 0.4), xytext=(D - 4.5, U - 13.5), fontsize=9.5, color="#8a2be2", fontweight="bold", ha="center", arrowprops=dict(arrowstyle="->", color="#8a2be2", lw=1.2))
ax.text(1.5, U + T + 0.4, "front edge", fontsize=9, color=INK, va="bottom")
ax.text(SY0 - 0.4, U - ST - 0.3, "strip + plug", fontsize=9, color=INK, ha="right", va="top")
dim_v(ax, 0, U, -4.5, "M1  floor to underside")
dim_v(ax, U, HT, -1.5, "M2  slab", left=True)
dim_h(ax, 0, D, HT + 3.2, "M3  front edge to back wall")
dim_h(ax, 0, SY0, U - ST - PH - 3.0, "M4  front edge to strip front", above=False)
dim_h(ax, SY0 + SW, D, U - ST - PH - 6.0, "M5  strip back to wall", above=False)
dim_v(ax, U - ST, U, SY0 + SW + 1.2, "M6  strip height", left=False)
ax.set_xlim(-8, 28); ax.set_ylim(-1.5, HT + 5.5); ax.set_aspect("equal"); ax.axis("off")

# ---------- front view ----------
ax = ax2
ax.set_title("Front view, cut 8 in behind the front edge (jambs shown dashed)", fontsize=12, loc="left", pad=10)
ax.add_patch(Rectangle((-4, -1.5), W + 8, 1.5, fc=WALL, ec="none"))                    # floor
ax.add_patch(Rectangle((-3, -1.5), 3, 36, fc=WALL, ec="none", hatch="///"))            # side walls
ax.add_patch(Rectangle((W, -1.5), 3, 36, fc=WALL, ec="none", hatch="///"))
ax.add_patch(Rectangle((0, U), W, T, fc=TAN, ec=INK, lw=1))                             # slab
ax.add_patch(Rectangle((0, U - CLH), CLW, CLH, fc="#a3773f", ec=INK, lw=0.8))          # cleats
ax.add_patch(Rectangle((W - CLW, U - CLH), CLW, CLH, fc="#a3773f", ec=INK, lw=0.8))
for xj in (JL, W - JL):
    ax.plot([xj, xj], [-1.5, HT + 2], color=INK, lw=1, ls="--")
ax.text(W / 2, HT + 2.2, "door opening (32 in)", ha="center", fontsize=9, color=INK)
ax.add_patch(Rectangle((JL + 2.5, 0), 7.5, 15, fc="#b9b9bd", ec="none"))               # PC (front left)
ax.text(JL + 2.5 + 3.75, 7.5, "PC", ha="center", va="center", fontsize=9)
ax.add_patch(Rectangle((W - JL - 1.5 - 11, 0), 11, 11, fc="#b9b9bd", ec="none"))       # shredder (back right)
ax.text(W - JL - 1.5 - 5.5, 5.5, "shredder", ha="center", va="center", fontsize=9)
ax.add_patch(Rectangle((SX0, U - ST), SL, ST, fc=DARK, ec="none"))                      # strip
for i in range(9):
    x = ox(i)
    ax.add_patch(Rectangle((x - 0.6, U - ST - 0.05), 1.2, 0.05, fc="#777", ec="none"))
    if i in TODAY:
        ax.add_patch(Rectangle((x - PW / 2, PZ), PW, PH, fc="black", ec="none"))
        ax.plot([x, x], [PZ, PZ - 2.5], color="black", lw=1.5)
    ax.text(x, U - ST - PH - 3.4, str(i + 1), ha="center", va="top", fontsize=10, fontweight="bold",
            color=INK if i in TODAY else "#999")
ax.text(SX0 + SL / 2, U - ST - PH - 5.2, "outlets 1 to 9, black = plugged in today.  Which of these cords need their slack stored?",
        ha="center", va="top", fontsize=9.5, color=INK)
ax.add_patch(Rectangle((DX0, DTOP - DH), DL, DH, fc="none", ec=ORANGE, lw=2, ls="--"))     # D decided
ax.text(DX0 + DL / 2, DTOP - DH - 0.4, "D (decided, 250 mm wide)", ha="center", va="top", fontsize=10, color=ORANGE, fontweight="bold")
dim_h(ax, 0, W, HT + 4.5, "M8  closet width, side wall to side wall (behind the jambs)")
dim_h(ax, 0, SX0, U - ST - 1.2, "M9  wall to strip end", above=False)
dim_h(ax, SX0 + SL, W, U - ST - 1.2, "M10  strip end to wall", above=False)
ax.set_xlim(-4, W + 4); ax.set_ylim(-1.5, HT + 7); ax.set_aspect("equal"); ax.axis("off")

fig.tight_layout()
fig.savefig(OUT, dpi=105, facecolor="white")
print(OUT)
