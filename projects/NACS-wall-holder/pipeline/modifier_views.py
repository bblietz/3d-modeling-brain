#!/usr/bin/env python
"""Draws the solid-base modifier against the body, before (the squared-off ring of 2026-10-10, commit 6bbc44c) and after
(the ring following the blend, 2026-10-11): the view Bambu Studio gives (a modifier drawn translucent over the body) and a
true section along the plate's diagonal. Writes images/modifier-ring.png and prints each modifier's volume outside the body
(what Studio shows as an added shape) and inside it (what goes solid).   Usage: modifier_views.py [body.stl]"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from make_coupon_3mf import BASE_INSET, scad_const, solid_base_scad  # noqa: E402

OPENSCAD = os.path.expanduser("~/.local/bin/openscad")
SCRATCH = os.environ.get("SCRATCH", "/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/612fec58-43f6-4bff-a4e8-46ee5353df03/scratchpad")
BODY = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else f"{PROJECT}/holder.stl"
CAMERA = "150,-230,135,-6,6,12"      # eye and centre: low over the plate, the drum's foot in the middle, as Studio shows the part on the bed
ACCENT = "#1f7a7c"


def before_scad():
    """The first solid-base modifier: the plate slab up to its top face, and a squared-off ring r 42..51 from t-0.5 to t+fp."""
    w, r, t = scad_const("plate_w"), scad_const("plate_r"), scad_const("plate_t")
    dr, fp = scad_const("drum_r"), scad_const("fillet_plate")
    return (f"union() {{\n  linear_extrude({t}) offset(r = {r - BASE_INSET}) offset(delta = -{r}) square({w}, center = true);\n"
            f"  translate([0, 0, {t} - 0.5]) difference() {{ cylinder(r = {dr + fp - BASE_INSET}, h = {fp} + 0.5, $fn = 180);"
            f" translate([0, 0, -1]) cylinder(r = {dr - 3}, h = {fp} + 3, $fn = 180); }}\n}}\n")


def openscad(scad, out, *args):
    src = out.rsplit(".", 1)[0] + ".scad"
    with open(src, "w") as f:
        f.write(scad)
    res = subprocess.run([OPENSCAD, "--backend=Manifold", *args, "-o", out, src], capture_output=True, text=True)
    assert res.returncode == 0 or "empty" in res.stderr, res.stderr[-1200:]
    return out


def volume(path):
    """cm3 of the STL, 0 for the empty result OpenSCAD leaves behind an empty boolean."""
    try:
        m = trimesh.load(path, force="mesh")
        return 0.0 if m.is_empty else abs(m.volume) / 1000
    except Exception:
        return 0.0


def section(mesh):
    """Shapely polygons of the mesh cut by the plane through the drum axis and the plate's diagonal, in (u, z): u along the diagonal."""
    n = np.array([1.0, -1.0, 0.0]) / math.sqrt(2)
    path = mesh.section(plane_origin=[0, 0, 0], plane_normal=n)
    if path is None:
        return []
    to2d = np.eye(4)
    to2d[0, :3], to2d[1, :3], to2d[2, :3] = [1, 1, 0] / np.sqrt(2), [0, 0, 1], n
    p2, _ = path.to_2D(to_2D=to2d)
    return list(p2.polygons_full)


def draw_section(ax, body_polys, mod_polys, title):
    for p in mod_polys:
        ax.fill(*p.exterior.xy, color=ACCENT, alpha=0.4, lw=0)
        for i in p.interiors:
            ax.fill(*i.xy, color="white", lw=0)
    for p in mod_polys:
        ax.plot(*p.exterior.xy, color=ACCENT, lw=0.9)
        for i in p.interiors:
            ax.plot(*i.xy, color=ACCENT, lw=0.9)
    for p in body_polys:
        ax.plot(*p.exterior.xy, color="#222", lw=1.4)
        for i in p.interiors:
            ax.plot(*i.xy, color="#222", lw=1.4)
    ax.set_xlim(28, 76)
    ax.set_ylim(-2, 24)
    ax.set_aspect("equal")
    ax.set_xlabel("along the plate's diagonal, mm from the drum axis")
    ax.set_ylabel("off the wall, mm")
    ax.set_title(title, fontsize=11)


def main():
    d = f"{SCRATCH}/modifier-views"
    os.makedirs(d, exist_ok=True)
    body = trimesh.load(BODY)
    body_polys = section(body)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10.5), gridspec_kw={"height_ratios": [1.15, 1]})
    for col, (tag, scad) in enumerate((("before", before_scad()), ("after", solid_base_scad()))):
        mod = openscad(scad, f"{d}/{tag}.stl")
        m = trimesh.load(mod)
        assert len(m.split()) == 1 and m.is_watertight, f"{tag}: expected one closed modifier"
        both = f'import("{BODY}");\n'
        outside = volume(openscad(f'difference() {{ import("{mod}"); {both} }}', f"{d}/{tag}-outside.stl"))
        inside = volume(openscad(f'intersection() {{ import("{mod}"); {both} }}', f"{d}/{tag}-inside.stl"))
        print(f"{tag}: modifier {abs(m.volume) / 1000:.1f} cm3, {outside:.2f} cm3 outside the body (shows in Studio), {inside:.1f} cm3 inside (goes solid)")
        png = openscad(f'{both}%import("{mod}");\n', f"{d}/{tag}.png", "--preview", "--projection=p", f"--camera={CAMERA}", "--imgsize=1400,900")
        ax = axes[0][col]
        ax.imshow(plt.imread(png))
        ax.axis("off")
        ax.set_title(("Before" if tag == "before" else "After") + ": the modifier (translucent) over the body, the way Studio draws it", fontsize=11)
        draw_section(axes[1][col], body_polys, section(m), ("Before" if tag == "before" else "After") + ": true section along the plate's diagonal, modifier shaded")
    fig.tight_layout()
    out = f"{PROJECT}/images/modifier-ring.png"
    fig.savefig(out, dpi=120)
    print("wrote", out)


if __name__ == "__main__":
    main()
