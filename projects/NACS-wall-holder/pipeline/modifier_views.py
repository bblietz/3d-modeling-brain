#!/usr/bin/env python
"""Draws the print file's solid modifiers against the body: the view Bambu Studio gives (a modifier drawn translucent over the
body) and a true section with the modifier shaded. images/modifier-ring.png: the solid-base modifier before (the squared-off
ring of 2026-10-10, commit 6bbc44c) and after (the ring following the blend, 2026-10-11). images/modifier-face.png: the
solid-face modifier (flange, lip and blend behind the flange, 2026-10-11). Prints each modifier's volume outside the body
(what Studio shows as an added shape; 0 for the current ones) and inside it (what goes solid).   Usage: modifier_views.py [body.stl]"""
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
from make_coupon_3mf import BASE_INSET, export_facemod, scad_const, solid_base_scad  # noqa: E402

OPENSCAD = os.path.expanduser("~/.local/bin/openscad")
SCRATCH = os.environ.get("SCRATCH", "/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/612fec58-43f6-4bff-a4e8-46ee5353df03/scratchpad")
BODY = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else f"{PROJECT}/holder.stl"
CAM_BASE = "150,-230,135,-6,6,12"      # eye and centre: low over the plate, the drum's foot in the middle, as Studio shows the part on the bed
CAM_FACE = "120,-250,300,0,22,98"      # from the front and above: the face, the lip and the flange's rim
ACCENT = "#1f7a7c"
SQ2 = math.sqrt(2)
DIAGONAL = ([1, -1, 0] / np.sqrt(2), [1, 1, 0] / np.sqrt(2), "along the plate's diagonal, mm from the drum axis")   # normal, u axis, label
MIDPLANE = ([1, 0, 0], [0, 1, 0], "across the face through the drum axis, mm (the lip is to the right)")


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


def section(mesh, plane):
    """Shapely polygons of the mesh cut by the plane through the origin, in (u, z)."""
    n, u, _ = plane
    path = mesh.section(plane_origin=[0, 0, 0], plane_normal=n)
    if path is None:
        return []
    to2d = np.eye(4)
    to2d[0, :3], to2d[1, :3], to2d[2, :3] = u, [0, 0, 1], n
    p2, _ = path.to_2D(to_2D=to2d)
    return list(p2.polygons_full)


def draw_section(ax, body_polys, mod_polys, title, plane, xlim, ylim):
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
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_xlabel(plane[2])
    ax.set_ylabel("off the wall, mm")
    ax.set_title(title, fontsize=11)


def measure(tag, mod, d):
    """The modifier's volume outside and inside the body, by OpenSCAD booleans on the meshes."""
    m = trimesh.load(mod)
    assert len(m.split()) == 1 and m.is_watertight, f"{tag}: expected one closed modifier"
    outside = volume(openscad(f'difference() {{ import("{mod}"); import("{BODY}"); }}', f"{d}/{tag}-outside.stl"))
    inside = volume(openscad(f'intersection() {{ import("{mod}"); import("{BODY}"); }}', f"{d}/{tag}-inside.stl"))
    print(f"{tag}: modifier {abs(m.volume) / 1000:.1f} cm3, {outside:.2f} cm3 outside the body (shows in Studio), {inside:.1f} cm3 inside (goes solid)")
    return m


def studio_view(ax, mod, png, camera, title):
    openscad(f'import("{BODY}");\n%import("{mod}");\n', png, "--preview", "--projection=p", f"--camera={camera}", "--imgsize=1400,900")
    ax.imshow(plt.imread(png))
    ax.axis("off")
    ax.set_title(title, fontsize=11)


def main():
    d = f"{SCRATCH}/modifier-views"
    os.makedirs(d, exist_ok=True)
    body = trimesh.load(BODY)
    # the base: before and after
    body_polys = section(body, DIAGONAL)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10.5), gridspec_kw={"height_ratios": [1.15, 1]})
    for col, (tag, scad) in enumerate((("before", before_scad()), ("after", solid_base_scad()))):
        mod = openscad(scad, f"{d}/{tag}.stl")
        m = measure(tag, mod, d)
        label = "Before" if tag == "before" else "After"
        studio_view(axes[0][col], mod, f"{d}/{tag}.png", CAM_BASE, f"{label}: the modifier (translucent) over the body, the way Studio draws it")
        draw_section(axes[1][col], body_polys, section(m, DIAGONAL), f"{label}: true section along the plate's diagonal, modifier shaded", DIAGONAL, (28, 76), (-2, 24))
    fig.tight_layout()
    fig.savefig(f"{PROJECT}/images/modifier-ring.png", dpi=120)
    # the face
    mod = f"{d}/face.stl"
    export_facemod(mod)
    m = measure("face", mod, d)
    fig, axes = plt.subplots(2, 1, figsize=(14, 11.5), gridspec_kw={"height_ratios": [1.5, 1]})
    studio_view(axes[0], mod, f"{d}/face.png", CAM_FACE, "The solid-face modifier (translucent) over the body, the way Studio draws it: nothing of it shows")
    draw_section(axes[1], section(body, MIDPLANE), section(m, MIDPLANE), "True section through the drum axis and the lip's centreline, modifier shaded", MIDPLANE, (-58, 94), (84, 110))
    fig.tight_layout()
    fig.savefig(f"{PROJECT}/images/modifier-face.png", dpi=120)
    print("wrote images/modifier-ring.png and images/modifier-face.png")


if __name__ == "__main__":
    main()
