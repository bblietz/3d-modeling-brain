"""Concept renders of print styles from the 1:1 trace (options page only).

A plaque: rounded rectangle, art raised on top
B die-cut: backer follows the art outline, art raised on top
C desk stand: die-cut standing in a slotted base
"""
import json
import pathlib
import subprocess
import sys

from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = pathlib.Path(__file__).resolve().parent
PROJ = HERE.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else PROJ / "images" / "options"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH_MM = 100.0
PLATE_T, ART_H = 3.0, 1.0
d = json.loads((PROJ / "traced.json").read_text())
polys = [Polygon(p["outer"], p["holes"]) for p in d["polys"]]
art_px = unary_union(polys)
x0, y0, x1, y1 = art_px.bounds
k = WIDTH_MM / (x1 - x0)


def to_mm(g):
    from shapely.affinity import affine_transform
    # px (y down) -> mm (y up), art centered on the origin
    return affine_transform(g, [k, 0, 0, -k, -k * (x0 + x1) / 2, k * (y0 + y1) / 2])


art = to_mm(art_px).simplify(0.02)
ax0, ay0, ax1, ay1 = art.bounds


def scad_poly(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        rings = [list(p.exterior.coords)[:-1]] + [list(h.coords)[:-1] for h in p.interiors]
        pts, paths, i = [], [], 0
        for r in rings:
            pts += r
            paths.append(list(range(i, i + len(r))))
            i += len(r)
        out.append("polygon(points=%s, paths=%s);" % (
            [[round(x, 3), round(y, 3)] for x, y in pts], paths))
    return "union(){" + "".join(out) + "}"


ART = scad_poly(art)
M = 7.0
rect = f"offset(r=6) square([{ax1 - ax0 + 2 * M - 12:.2f},{ay1 - ay0 + 2 * M - 12:.2f}], center=true);"
_grown = art.buffer(5.0, quad_segs=24).buffer(-1.5, quad_segs=24)   # 3.5 mm margin
assert _grown.geom_type == "Polygon", "die-cut outline is not one piece"
outline = Polygon(_grown.exterior)                                   # sticker: interior filled
DIE = scad_poly(outline.simplify(0.05))

WHITE, BLACK = '"#f4f1ea"', '"#1d1d1f"'
scenes = {
    "A-plaque": f"""
color({WHITE}) linear_extrude({PLATE_T}) {rect}
color({BLACK}) translate([0,0,{PLATE_T}]) linear_extrude({ART_H}) {ART}
""",
    "B-diecut": f"""
color({WHITE}) linear_extrude({PLATE_T}) {DIE}
color({BLACK}) translate([0,0,{PLATE_T}]) linear_extrude({ART_H}) {ART}
""",
    "C-stand": f"""
BY = {ay0 - 5:.2f};
color({WHITE}) translate([0,-4,0]) linear_extrude(8) offset(r=4) square([{(ax1 - ax0) * 0.55:.1f}, 16], center=true);
translate([0,0,8 - BY + 0]) rotate([90,0,0]) translate([0,0,-2]) {{
  color({WHITE}) linear_extrude(4) {DIE}
  color({BLACK}) translate([0,0,4]) linear_extrude({ART_H}) {ART}
}}
""",
}
cams = {"A-plaque": "0,-150,230,0,0,0", "B-diecut": "0,-150,230,0,0,0",
        "C-stand": "60,-220,120,0,0,55"}
for name, body in scenes.items():
    f = OUT / f"{name}.scad"
    f.write_text("$fn=48;\n" + body)
    png = OUT / f"{name}.png"
    r = subprocess.run(["openscad", "--backend=Manifold", "--preview", "--viewall",
                        "--autocenter", "--colorscheme=Tomorrow", f"--camera={cams[name]}",
                        "--imgsize=1400,1200", "-o", str(png), str(f)],
                       capture_output=True, text=True)
    print(name, "ok" if png.exists() and r.returncode == 0 else r.stderr[-400:])
print(f"art {ax1 - ax0:.1f} x {ay1 - ay0:.1f} mm; plaque {ax1 - ax0 + 2 * M:.1f} x {ay1 - ay0 + 2 * M:.1f}; "
      f"die-cut {outline.bounds[2] - outline.bounds[0]:.1f} x {outline.bounds[3] - outline.bounds[1]:.1f}")
