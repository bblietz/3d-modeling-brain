"""Headless colored scene renders of exported STLs (OpenSCAD preview, Manifold).

Pattern from projects/Logodude/pipeline/options.py: write a .scad that imports
the real exported meshes with color(), render it with `openscad --preview`.

render(png, parts, camera, imgsize=(1400, 1200), wrap="", clip="", viewall=False, projection="perspective")
    parts: list of (stl_path, "#rrggbb", alpha or None)
    camera: "ex,ey,ez,cx,cy,cz" (eye and center) in the scene's coordinates after `wrap`
    wrap: OpenSCAD transform applied to every part, e.g. "rotate([90,0,0])" to turn a y-up design frame
          into OpenSCAD's z-up (x stays, design y becomes z, design z becomes -y)
    clip: an OpenSCAD solid to subtract from every part (section views); cut faces show in a darker shade
"""
import pathlib
import subprocess

OPENSCAD = "/home/brian/.local/bin/openscad"


def render(png, parts, camera, imgsize=(1400, 1200), wrap="", clip="", viewall=False, projection="perspective"):
    png = pathlib.Path(png)
    png.parent.mkdir(parents=True, exist_ok=True)
    lines = ["$fn=64;"]
    for stl, col, alpha in parts:
        a = "" if alpha is None else f", {alpha}"
        body = f'{wrap} import("{pathlib.Path(stl).resolve()}");'
        if clip:   # a difference keeps each part's color in preview and paints the cut face a darker shade
            dark = "#" + "".join(f"{int(int(col[i:i+2], 16) * 0.72):02x}" for i in (1, 3, 5))
            lines.append(f'difference(){{ color("{col}"{a}) {body} color("{dark}") {clip} }}')
        else:
            lines.append(f'color("{col}"{a}) {body}')
    scad = png.with_suffix(".scad")
    scad.write_text("\n".join(lines) + "\n")
    cmd = [OPENSCAD, "--backend=Manifold", "--preview", "--autocenter",
           "--colorscheme=Tomorrow", f"--camera={camera}", f"--projection={projection}",
           f"--imgsize={imgsize[0]},{imgsize[1]}", "-o", str(png), str(scad)]
    if viewall:
        cmd.insert(3, "--viewall")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not (png.exists() and r.returncode == 0):
        raise RuntimeError(f"openscad failed for {png.name}: {r.stderr[-600:]}")
    return png
