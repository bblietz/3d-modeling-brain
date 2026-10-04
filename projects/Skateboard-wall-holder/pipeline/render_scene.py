"""Headless colored scene renders of exported STLs (OpenSCAD preview, Manifold).

Pattern from projects/Logodude/pipeline/options.py: write a .scad that imports
the real exported meshes with color(), render it with `openscad --preview`.
Used by skateboard_holder.py for the options page and the check figures.

render(png, parts, camera, imgsize=(1400, 1200), extra_scad="")
    parts: list of (stl_path, "#rrggbb" or "#rrggbbaa", alpha or None)
    camera: "ex,ey,ez,cx,cy,cz" (eye and center) or "tx,ty,tz,rx,ry,rz,dist"
    extra_scad: raw OpenSCAD appended to the scene (section cutters, planes)
"""
import pathlib
import subprocess

OPENSCAD = "/home/brian/.local/bin/openscad"


def render(png, parts, camera, imgsize=(1400, 1200), extra_scad="", viewall=False,
           projection="perspective"):
    png = pathlib.Path(png)
    png.parent.mkdir(parents=True, exist_ok=True)
    lines = ["$fn=64;"]
    for stl, col, alpha in parts:
        a = "" if alpha is None else f", {alpha}"
        lines.append(f'color("{col}"{a}) import("{pathlib.Path(stl).resolve()}");')
    lines.append(extra_scad)
    scad = png.with_suffix(".scad")
    scad.write_text("\n".join(lines) + "\n")
    cmd = [OPENSCAD, "--backend=Manifold", "--preview", "--autocenter",
           "--colorscheme=Tomorrow", f"--camera={camera}", f"--projection={projection}",
           f"--imgsize={imgsize[0]},{imgsize[1]}", "-o", str(png), str(scad)]
    if viewall:
        cmd.insert(3, "--viewall")
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = png.exists() and r.returncode == 0
    if not ok:
        raise RuntimeError(f"openscad failed for {png.name}: {r.stderr[-600:]}")
    return png
