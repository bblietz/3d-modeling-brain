"""Edge profile options for the pick: build each variant from guitar_pick.build(), cut the tip cross-section,
work out how far each 0.06 mm layer of the underside hangs past the one below it (the pick prints flat, so the
underside profile is limited by that), and render a close-up of the tip. Feeds make_compare_page.py.

    .venv/bin/python projects/Guitar-pick/pipeline/edge_options.py <scratch dir>

Writes <scratch>/<variant>.stl, images/edge-<variant>.png (OpenSCAD close-ups, above and below) and edge-options.json
(tip sections as ordered polylines, per-layer underside overhang).
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageChops
from build123d import export_stl

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))
import guitar_pick  # noqa: E402

VARIANTS = ["sym", "mirror", "soft", "bevel", "round", "chamfer", "square"]
FIRST_LAYER, LAYER = 0.1, 0.06            # as in make_print_3mf.py
LINE = 0.22                               # outer wall line width, 0.2 nozzle preset
TIP_WINDOW = 3.0                          # mm of the tip shown in the section


def slice_heights(thick):
    """Where Bambu Studio samples each layer: the middle of the layer (print_z - h/2)."""
    zs, top = [FIRST_LAYER / 2], FIRST_LAYER
    while top + LAYER <= thick + 1e-9:
        zs.append(top + LAYER / 2)
        top += LAYER
    return zs


def tip_section(mesh):
    """The closed outline of the x = 0 section (y, z), tip end only, as an ordered polyline."""
    sec = mesh.section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
    loops = sec.discrete
    loop = max(loops, key=len)[:, 1:]                   # (y, z); the pick axis runs top edge (y 0) to tip (y -30.38)
    ymin = loop[:, 0].min()
    return loop, ymin


def tip_y_at(loop, z):
    """The outline's tip (min y) where the horizontal plane z cuts the section loop."""
    ys = []
    for (y0, z0), (y1, z1) in zip(loop, np.roll(loop, -1, 0)):
        if (z0 - z) * (z1 - z) <= 0 and z0 != z1:
            ys.append(y0 + (z - z0) * (y1 - y0) / (z1 - z0))
    return min(ys) if ys else None


def overhang_table(loop, thick):
    rows, prev = [], None
    for i, z in enumerate(slice_heights(thick)):
        y = tip_y_at(loop, z)
        step = (prev - y) if prev is not None else 0.0     # how far this layer's edge sits past the one below (mm)
        h = FIRST_LAYER if i == 0 else LAYER
        rows.append({"layer": i + 1, "z": round(z, 3), "inset": round(y - loop[:, 0].min(), 3),
                     "step": round(step, 3), "angle": round(math.degrees(math.atan2(step, h)), 1)})
        prev = y
    return rows


def render_tip(stl, png, scratch):
    """Close-up of the last 6 mm of the tip from above and from below, rendered by OpenSCAD (real z-buffer, so the
    fillet band reads cleanly), each view cropped to its content and the two stacked into one PNG."""
    m = trimesh.load(stl)
    clip = m.slice_plane([0, m.bounds[0][1] + 6.0, 0], [0, -1, 0], cap=True)
    tip = scratch / (png.stem + ".tip.stl")
    clip.export(tip)
    scad = scratch / (png.stem + ".scad")
    scad.write_text(f'color("#5b7fb5") import("{tip.name}");\n')
    views = []
    for name, eye in (("above", "-9,-48,9"), ("below", "-9,-48,-9")):
        out = scratch / f"{png.stem}-{name}.png"
        subprocess.run([str(Path.home() / ".local/bin/openscad"), "--backend=Manifold", "--preview", "--viewall", "--autocenter",
                        "--projection=o", "--imgsize=1400,800", "--colorscheme=Tomorrow", f"--camera={eye},0,-28,0.5",
                        "-o", str(out), str(scad)], check=True, capture_output=True, cwd=scratch)
        im = Image.open(out).convert("RGB")
        bg = im.getpixel((0, 0))
        diff = ImageChops.difference(im, Image.new("RGB", im.size, bg))
        box = diff.getbbox()
        views.append(im.crop((box[0] - 30, box[1] - 30, box[2] + 30, box[3] + 30)))
    w = max(v.width for v in views)
    sheet = Image.new("RGB", (w, sum(v.height for v in views) + 10), views[0].getpixel((0, 0)))
    y = 0
    for v in views:
        sheet.paste(v, ((w - v.width) // 2, y))
        y += v.height + 10
    sheet.save(png, optimize=True)


def main(scratch):
    scratch = Path(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    out = {"first_layer": FIRST_LAYER, "layer": LAYER, "line": LINE, "variants": {}}
    for v in VARIANTS:
        part = guitar_pick.build(v)
        stl = scratch / f"{v}.stl"
        export_stl(part, str(stl))
        m = trimesh.load(stl)
        assert m.is_watertight
        loop, ymin = tip_section(m)
        loop = np.roll(loop, -int(np.argmax(loop[:, 0])), axis=0)       # start at the far end so the tip run is contiguous
        tip = loop[loop[:, 0] < ymin + TIP_WINDOW]
        rows = overhang_table(loop, guitar_pick.THICK)
        spec = guitar_pick.EDGES[v]
        rim = guitar_pick.THICK - (0 if not spec else 2 * spec["r"] if spec["kind"] == "fillet" else spec["top"][1] + spec["bottom"][1])
        out["variants"][v] = {
            "section": [[round(float(y - ymin), 4), round(float(z), 4)] for y, z in tip],   # ordered: top face in, round the tip, bottom face out
            "overhang": rows,
            "worst_bottom": max(rows[1:len(rows) // 2], key=lambda r: r["step"]),
            "rim_mm": round(rim, 2),
            "volume_mm3": round(part.volume, 1),
            "spec": spec,
        }
        render_tip(stl, PROJECT / "images" / f"edge-{v}.png", scratch)
        w = out["variants"][v]["worst_bottom"]
        print(f"{v:8s} rim {out['variants'][v]['rim_mm']:.2f} mm  worst underside step layer {w['layer']}: {w['step']:.3f} mm ({w['angle']:.0f} deg from vertical, {w['step'] / LINE:.0%} of a line)")
    (scratch / "edge-options.json").write_text(json.dumps(out, indent=1))
    (PROJECT / "edge-options.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
