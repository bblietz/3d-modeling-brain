"""Figures for the filament budget: a true section of a sliced holder's toolpaths coloured by where the plastic goes, and a bar
chart of the body filament per region across the sliced variants (pipeline/filament_budget.py).

Usage:  filament_figures.py section <sliced.3mf> <out.png> [title]      toolpaths within 0.5 mm of the x = 0 plane (through the lip and the cavity)
        filament_figures.py bars <out.png> <name=label> ...              stacked bars from filament-variants.json, in the order given
        filament_figures.py layer <sliced.3mf> <out.png> <z> [title]     one layer from above, model frame, the lip's support block in view
"""
import json
import os
import sys
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import filament_budget as fb  # noqa: E402

COLOURS = {
    "solid base": "#1f4e79", "solid face": "#2e75b6", "drum core": "#9dc3e6", "walls": "#5b6b7a", "shells and solid layers": "#8497a8",
    "support: under the lip": "#c55a11", "support: under the flange ring": "#ed7d31", "support: in the cavity": "#f4b183",
    "support: elsewhere": "#f8cbad", "prime tower": "#bfbfbf", "other": "#d9d9d9", "interface (filament 2)": "#70ad47", "inlay (filament 3)": "#ffd966",
}
ORDER = list(COLOURS)


def section(sliced, out, title=""):
    tot, segs, mid, e, feat, where = fb.regions(sliced)
    back = fb.to_model(sliced)
    rows, cols = [], []
    def keep(s, colour):
        p0, p1 = back(s[0], s[1]), back(s[2], s[3])
        if abs((p0[0] + p1[0]) / 2) <= 0.5:
            z = s[4] - 0.15
            rows.append([(p0[1], z), (p1[1], z)])
            cols.append(colour)
    for s, w in zip(segs, where):
        keep(s, COLOURS.get(w, "#d9d9d9"))
    for s in fb.segments(sliced):
        if s[6] == 2:
            keep(s, COLOURS["interface (filament 2)"])
        elif s[6] == 3:
            keep(s, COLOURS["inlay (filament 3)"])
    fig, ax = plt.subplots(figsize=(11, 8.2), dpi=110)
    ax.add_collection(LineCollection(rows, colors=cols, linewidths=1.4))
    m = trimesh.load(f"{PROJECT}/holder.stl")
    sec = m.section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
    if sec is not None:
        for ent in sec.discrete:
            ax.plot(ent[:, 1], ent[:, 2], color="black", lw=0.6, alpha=0.8)
    ax.set_aspect("equal")
    ax.set_xlim(-70, 100)
    ax.set_ylim(-3, 112)
    ax.set_xlabel("across the holder (mm), the lip to the right; wall plate at the bottom, face at the top: the print orientation")
    ax.set_ylabel("height above the bed (mm)")
    density = json.loads(zipfile.ZipFile(sliced).read("Metadata/project_settings.config"))["sparse_infill_density"]
    name = lambda k: f"drum core, {density} gyroid" if k == "drum core" else k
    handles = [plt.Line2D([], [], color=COLOURS[k], lw=6, label=f"{name(k)}  {tot[k]:.0f} g") for k in ORDER if k in tot and tot[k] >= 0.5]
    handles += [plt.Line2D([], [], color=COLOURS[k], lw=6, label=k) for k in ("interface (filament 2)", "inlay (filament 3)")]
    ax.legend(handles=handles, loc="upper left", fontsize=8.5, frameon=True, title="body PETG by where it goes", title_fontsize=9)
    ax.set_title(title or os.path.basename(os.path.dirname(sliced)), fontsize=11)
    fig.tight_layout()
    fig.savefig(out)
    print(out)


def bars(out, picks):
    allr = json.load(open(fb.RESULTS))
    names = [p.split("=", 1)[0] for p in picks]
    labels = [p.split("=", 1)[1] for p in picks]
    fig, ax = plt.subplots(figsize=(11, 0.75 * len(names) + 2.6), dpi=110)
    y = np.arange(len(names))[::-1]
    lefts = np.zeros(len(names))
    for k in ORDER:
        vals = np.array([sum(v for kk, v in allr[n].get("regions", {}).items() if kk.replace("drum core, 20%", "drum core") == k) for n in names])
        if vals.sum() < 0.5:
            continue
        ax.barh(y, vals, left=lefts, color=COLOURS[k], label=k, height=0.6)
        lefts += vals
    for yi, n, l in zip(y, names, lefts):
        ax.text(l + 4, yi, f"{allr[n]['slice_info_g']['1']:.0f} g", va="center", fontsize=9, fontweight="bold")
    ax.axvline(500, color="#c00000", lw=1.2, ls="--")
    ax.text(501, y.max() + 0.55, "500 g", color="#c00000", fontsize=9)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("body PETG, grams (from the sliced G-code)")
    ax.set_xlim(0, max(lefts) * 1.12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), fontsize=8, ncol=4, frameon=False)
    fig.tight_layout()
    fig.savefig(out)
    print(out)


def layer(sliced, out, z_want, title="", window=(-60, 60, 30, 95)):
    """One layer's toolpaths seen from above (model frame), coloured by region: how the supports under the lip and round the flange are built."""
    tot, segs, mid, e, feat, where = fb.regions(sliced)
    back = fb.to_model(sliced)
    zs = sorted({round(s[4], 2) for s in segs})
    z = min(zs, key=lambda v: abs(v - z_want))
    rows, cols = [], []
    for s, w in zip(segs, where):
        if abs(s[4] - z) > 0.01:
            continue
        p0, p1 = back(s[0], s[1]), back(s[2], s[3])
        rows.append([p0, p1])
        cols.append(COLOURS.get(w, "#d9d9d9"))
    for s in fb.segments(sliced):
        if s[6] != 1 and abs(s[4] - z) <= 0.01:
            rows.append([back(s[0], s[1]), back(s[2], s[3])])
            cols.append(COLOURS["interface (filament 2)"] if s[6] == 2 else COLOURS["inlay (filament 3)"])
    x0, x1, y0, y1 = window
    fig, ax = plt.subplots(figsize=(10, 10 * (y1 - y0) / (x1 - x0) + 0.9), dpi=110)
    ax.add_collection(LineCollection(rows, colors=cols, linewidths=1.6))
    ax.set_aspect("equal")
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_xlabel("mm across; the lip's underside spans the top of this window")
    ax.set_title(f"{title or os.path.basename(os.path.dirname(sliced))}: layer at z = {z} mm from above", fontsize=11)
    fig.tight_layout()
    fig.savefig(out)
    print(out)


if __name__ == "__main__":
    if sys.argv[1] == "section":
        section(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    elif sys.argv[1] == "bars":
        bars(sys.argv[2], sys.argv[3:])
    elif sys.argv[1] == "layer":
        layer(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else "")
