"""Inspection renders for the cable bin through OpenSCAD (proper hidden-surface
removal, two colours for the two halves). Writes PNGs to projects/Cable-bin/images/.

Run from the vault root: .venv/bin/python projects/Cable-bin/pipeline/renders.py
Chunks are exported as STLs into the scratchpad and imported by a generated .scad.
"""
import importlib.util
import os
import subprocess

from build123d import Align, Axis, Box, Cylinder, Pos, Rot, export_stl

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = os.path.join(VAULT, "projects", "Cable-bin")
IMAGES = os.path.join(PROJ, "images")
SCRATCH = os.environ.get("SCRATCH", "/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/57f36788-c5ae-4c4a-b01f-4b0e50546282/scratchpad/renders")
OPENSCAD = os.path.expanduser("~/.local/bin/openscad")

COL_A = "#5b8def"   # half A, tails
COL_B = "#e8a33d"   # half B, sockets
COL_U = "#7fc8a9"   # a second bin stacked on top

spec = importlib.util.spec_from_file_location("cable_bin", os.path.join(PROJ, "cable_bin.py"))
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)


def render(name, parts, rot=(55, 0, 25), size=(1400, 1000), proj="p"):
    """parts: list of (shape, colour). Camera: OpenSCAD gimbal rotations, viewall."""
    os.makedirs(IMAGES, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    lines = []
    for i, (shape, colour) in enumerate(parts):
        if shape is None:
            continue
        stl = os.path.join(SCRATCH, f"{name}-{i}.stl")
        export_stl(shape, stl, tolerance=0.02, angular_tolerance=0.1)
        lines.append(f'color("{colour}") import("{stl}");')
    scad = os.path.join(SCRATCH, f"{name}.scad")
    with open(scad, "w") as f:
        f.write("\n".join(lines) + "\n")
    png = os.path.join(IMAGES, f"{name}.png")
    rx, ry, rz = rot
    cmd = [OPENSCAD, "--backend=Manifold", "--preview", "--viewall", "--autocenter",
           f"--camera=0,0,0,{rx},{ry},{rz},0", f"--imgsize={size[0]},{size[1]}",
           f"--projection={proj}", "--colorscheme=Tomorrow", "-o", png, scad]
    subprocess.run(cmd, check=True, capture_output=True)
    print("wrote", png)


def box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN))


def main():
    half_a, half_b, whole, outer = cb.halves()
    H, W, L = cb.H, cb.W, cb.L
    bin_ = half_a + half_b
    up = Pos(0, 0, cb.STACK_PITCH)

    render("bin-assembled", [(half_a, COL_A), (half_b, COL_B)], rot=(60, 0, 30))
    render("bin-exploded", [(Pos(-30, 0, 0) * half_a, COL_A), (Pos(30, 0, 0) * half_b, COL_B)], rot=(60, 0, 30))
    render("bin-top", [(half_a, COL_A), (half_b, COL_B)], rot=(0, 0, 0), proj="o")
    render("bin-end", [(half_a, COL_A), (half_b, COL_B)], rot=(90, 0, 90), proj="o", size=(900, 900))
    render("bin-side", [(half_a, COL_A), (half_b, COL_B)], rot=(90, 0, 0), proj="o", size=(1600, 520))

    # joint close-up at the +y wall, top 50 mm, seen from inside the bin
    zone = box(-30, 30, 14, W / 2 + 1, H - 50, H + 40)
    render("joint-assembled", [(half_a & zone, COL_A), (half_b & zone, COL_B)], rot=(62, 0, 22))
    render("joint-lifted", [((Pos(0, 0, 30) * half_a) & zone, COL_A), (half_b & zone, COL_B)], rot=(62, 0, 22))
    render("joint-plan", [(half_a & zone, COL_A), (half_b & zone, COL_B)], rot=(0, 0, 0), proj="o")
    # horizontal section through the rib zone: a 2 mm slab, looked at from above
    slab = box(-30, 30, 14, W / 2 + 1, H - 12, H - 10)
    render("joint-section-ribs", [(half_a & slab, COL_A), (half_b & slab, COL_B)], rot=(0, 0, 0), proj="o")
    # same slab below the rib zone: plain clearance
    slab2 = box(-30, 30, 14, W / 2 + 1, H - 40, H - 38)
    render("joint-section-plain", [(half_a & slab2, COL_A), (half_b & slab2, COL_B)], rot=(0, 0, 0), proj="o")
    render("tail-ribs", [(cb.tail(+1), COL_A)], rot=(70, 0, 35))

    # stacking: a pair, and a section through the closed end
    render("stack-pair", [(half_a, COL_A), (half_b, COL_B), (up * bin_, COL_U)], rot=(65, 0, 30))
    sect = box(L / 2 - 50, L / 2 + 5, 0, W / 2 + 1, -1, H + cb.STACK_PITCH + 1)
    render("stack-section", [(bin_ & sect, COL_B), ((up * bin_) & sect, COL_U)], rot=(72, 0, 28))
    # the seat itself: a thin vertical slab through both bins at mid-length of the end zone
    seat = box(L / 2 - 30, L / 2 - 28, 0, W / 2 + 1, H - 20, H + 20)
    render("seat-section", [(bin_ & seat, COL_B), ((up * bin_) & seat, COL_U)], rot=(90, 0, 90), proj="o", size=(1200, 700))

    # four bins stacked, for scale
    stack4 = [(Pos(0, 0, i * cb.STACK_PITCH) * bin_, [COL_B, COL_U, COL_A, "#c98bd6"][i]) for i in range(4)]
    render("stack-four", stack4, rot=(70, 0, 30), size=(1000, 1200))

    # fit ladder: four coupon pairs in a row, as on plate 2, pair i with i notches
    pieces = []
    for i, (clr, crush, rib_len) in enumerate(cb.FIT_LADDER, start=1):
        ha, hb, _, _ = cb.halves(clr=clr, proud=clr + crush, rib_len=rib_len)
        ca, cbn = cb.coupon_pieces(ha, hb, notches=i)
        x, y = ((i - 1) % 2) * 62.0, -((i - 1) // 2) * 42.0     # 2 x 2, pairs 1 2 in the back row; A spans x -15..5.5, B 24..40
        pieces += [(Pos(x, y, 0) * ca, COL_A), (Pos(x + 24.0, y, 0) * cbn, COL_B)]
    render("coupons", pieces, rot=(60, 0, 200), size=(1400, 1000))   # from the outer-wall side: the notches show


if __name__ == "__main__":
    main()
