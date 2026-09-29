"""Final colored renders of the exported STLs (OpenSCAD, Manifold) -> images/final-*.png."""
import pathlib
import subprocess

PROJ = pathlib.Path(__file__).resolve().parent.parent
OUT = PROJ / "images"
SCAD = OUT / "final-view.scad"
SCAD.write_text(f'color("#eeeeea") import("{PROJ}/logodude-backer.stl");\n'
                f'color("#1d1d1f") import("{PROJ}/logodude-ink.stl");\n')
VIEWS = {"iso": "0,-120,150,0,0,2", "top": "0,0,210,0,0,0",
         "front": "0,-230,4,0,0,2", "face-closeup": "10,-55,50,8,-30,3"}
for name, cam in VIEWS.items():
    png = OUT / f"final-{name}.png"
    frame = [] if name == "face-closeup" else ["--viewall", "--autocenter"]
    subprocess.run(["openscad", "--backend=Manifold", "--preview", "--colorscheme=Tomorrow", *frame,
                    f"--camera={cam}", "--imgsize=1400,1100", "-o", str(png), str(SCAD)],
                   check=True, capture_output=True)
    print(png.name)
SCAD.unlink()
