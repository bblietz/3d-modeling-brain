#!/usr/bin/env python
"""OpenSCAD scene renders of the real hook STL: on a 1x4 with a rod, and four of
them on a 27 in board hanging from a 2x8 joist. Plus a close-up section through
the pocket with a 3/8 and a 5/8 rod for the retention check.

Run from the vault root after rod_hook.py:
  .venv/bin/python projects/Fishing-rod-holder/pipeline/renders.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rod_hook as rh  # noqa: E402

PROJECT = Path(__file__).resolve().parents[1]
IMAGES = PROJECT / "images"
SCRATCH = Path("/tmp/claude-1000/-home-brian--claude-spares-spare-OJ6Ifx/3f3590ae-4308-446d-b672-0d51f52c10fb/scratchpad/hook")
OPENSCAD = Path.home() / ".local/bin/openscad"
IN = rh.IN
STL = PROJECT / "rod-hook.stl"

JOIST_D, JOIST_T, PLY = 7.25, 1.5, 0.75
BOARD_LEN, BOARD_ABOVE = 27.0, 7.0      # Brian's comb: 27 in overall, 7 in up the joist
N_HOOKS = rh.HOOKS_PER_BOARD             # five hooks butted fill the hang
PITCH = rh.H                             # no gap between hooks: pitch is the hook height
BOTTOM_FIRST = rh.H                      # the top hook starts at the joist bottom
SEAT = rh.seat_point(0.375)              # where a 3/8 blank rests, in hook coordinates (x, y up from the hook bottom)
FIRST = BOTTOM_FIRST - SEAT[1]           # that rod's depth below the joist


def render(name, body, camera, size=(1400, 1000), projection="p"):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    scad = SCRATCH / f"{name}.scad"
    scad.write_text(body)
    out = IMAGES / f"{name}.png"
    cmd = [str(OPENSCAD), "--backend=Manifold", "--preview", "--viewall", "--autocenter",
           f"--camera={camera}", "--colorscheme=Tomorrow", f"--imgsize={size[0]},{size[1]}",
           f"--projection={projection}", "-o", str(out), str(scad)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(f"openscad failed on {name}")
    print("rendered", out)


HOOK = f'color("#2f6fe4") import("{STL}");'


def rod(d, length=8.0, x=None, y=None, color="#333333"):
    sx, sy = rh.seat_point(d)
    x = sx if x is None else x
    y = sy if y is None else y
    return f'color("{color}") translate([{x * IN}, {y * IN}, {-length * IN / 2}]) cylinder(h={length * IN}, d={d * IN}, $fn=48);'


def board(length_in, y0_in):
    """1x4 on edge behind the hooks: x 0..3.5, z -0.75..0, y from y0 up by length."""
    return f'color("#d8b98a") translate([0, {y0_in * IN}, {-rh.BOARD_T * IN}]) cube([{rh.BOARD_W * IN}, {length_in * IN}, {rh.BOARD_T * IN}]);'


def main():
    IMAGES.mkdir(exist_ok=True)
    # 1. one hook on its board with a 3/8 rod seated
    # model y (up) becomes world z so the board stands and the rod lies horizontal
    scene1 = f"""
rotate([90, 0, 0]) {{
  {board(6.0, -1.5)}
  {HOOK}
  {rod(0.375)}
}}
"""
    render("hook-on-board", scene1, "0,0,0,75,0,-40,0", size=(1200, 900))
    # 2. four hooks on a 27 in board hanging from the joist, rods seated, from below
    hooks = []
    board_top = BOARD_ABOVE                                  # y of the board top, joist bottom at y = 0
    for i in range(N_HOOKS):
        hook_y = -(BOTTOM_FIRST + PITCH * i)                 # hook bottom edge below the joist bottom
        hooks.append(f'translate([0, {hook_y * IN}, 0]) {HOOK}')
        hooks.append(rod(0.375, length=14.0, y=hook_y + SEAT[1]))
    scene2 = f"""
rotate([90, 0, 0]) {{
{board(BOARD_LEN, BOARD_ABOVE - BOARD_LEN)}
color("#c9a46e") translate([-{4 * IN}, 0, -{(rh.BOARD_T + JOIST_T) * IN}]) cube([{12 * IN}, {JOIST_D * IN}, {JOIST_T * IN}]);
color("#e8d6b3") translate([-{4 * IN}, {JOIST_D * IN}, -{8 * IN}]) cube([{12 * IN}, {PLY * IN}, {16 * IN}]);
{chr(10).join(hooks)}
}}
"""
    render("board-in-place", scene2, "0,0,0,100,0,-35,0", size=(1200, 1400))
    layout_figure()


def frac(x):
    """Inches to the nearest 1/16 as a fraction string."""
    whole = int(x + 1e-9)
    n = round((x - whole) * 16)
    if n == 16:
        whole, n = whole + 1, 0
    if n == 0:
        return str(whole)
    d = 16
    while n % 2 == 0:
        n, d = n // 2, d // 2
    return f"{whole}-{n}/{d}" if whole else f"{n}/{d}"


def layout_figure():
    """To-scale drilling guide: the 27 in board with four hooks, screw positions, rods."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon as MplPolygon, Rectangle
    from shapely.geometry import box as sbox

    fig, ax = plt.subplots(figsize=(6.5, 10.5), dpi=160)
    # depth below the joist bottom grows downward on the page
    ax.add_patch(Rectangle((-3.5, -JOIST_D - PLY), 10.5, PLY, fc="#e8d6b3", ec="#8a6a3c", lw=0.8, hatch="//", zorder=0))
    ax.add_patch(Rectangle((-3.5, -JOIST_D), 10.5, JOIST_D, fc="#d8b98a", ec="#8a6a3c", lw=1.0, zorder=0))
    ax.add_patch(Rectangle((0, -BOARD_ABOVE), rh.BOARD_W, BOARD_LEN, fc="#e9d4ad", ec="#8a6a3c", lw=1.2, zorder=1))
    solid = rh.solid_2d()  # hook outline in hook coords (y up, bottom at 0)
    for i in range(N_HOOKS):
        bottom_depth = BOTTOM_FIRST + PITCH * i
        pts = [(x, bottom_depth - y) for x, y in solid.exterior.coords]
        ax.add_patch(MplPolygon(pts, closed=True, fc="#5b8def", ec="#2b4f9e", lw=1.0, zorder=3))
        ax.add_patch(Circle((SEAT[0], bottom_depth - SEAT[1]), 0.375 / 2, fc="#333333", ec="black", lw=0.8, zorder=5))
        for sy in rh.SCREW_Y:
            ax.add_patch(Circle((rh.SCREW_X, bottom_depth - sy), 0.2, fc="#e5e7eb", ec="#1f2430", lw=0.8, zorder=6))
            ax.add_patch(Circle((rh.SCREW_X, bottom_depth - sy), 0.1, fc="#1f2430", ec="#1f2430", zorder=6.1))
        # hook bottom edge callout
        ax.annotate(frac(bottom_depth), xy=(rh.BOARD_W + 0.1, bottom_depth), xytext=(rh.BOARD_W + 0.7, bottom_depth),
                    fontsize=8.5, va="center", color="#1f2430", arrowprops=dict(arrowstyle="-", color="#1f2430", lw=0.7), zorder=8)
    # dimensions
    ax.annotate("", xy=(rh.BOARD_W + 5.2, 0), xytext=(rh.BOARD_W + 5.2, BOARD_LEN - BOARD_ABOVE), arrowprops=dict(arrowstyle="<->", lw=0.9), zorder=8)
    ax.text(rh.BOARD_W + 5.05, (BOARD_LEN - BOARD_ABOVE) * 0.8, "20 in hang,\nas now", fontsize=8.5, va="center", ha="right")
    ax.annotate("", xy=(-2.9, BOTTOM_FIRST), xytext=(-2.9, BOTTOM_FIRST + PITCH), arrowprops=dict(arrowstyle="<->", lw=0.9), zorder=8)
    ax.text(-3.05, BOTTOM_FIRST + PITCH / 2, f"{PITCH:g} in\npitch", fontsize=8.5, va="center", ha="right")
    ax.annotate("", xy=(-2.9, 0), xytext=(-2.9, BOTTOM_FIRST), arrowprops=dict(arrowstyle="<->", lw=0.9), zorder=8)
    ax.text(-3.05, BOTTOM_FIRST / 2, f"{frac(BOTTOM_FIRST)}: the top\nhook starts\nat the joist", fontsize=8.5, va="center", ha="right")
    ax.text(0.1, -BOARD_ABOVE + 0.9, "1x4, 27 in,\n7 in up the joist", fontsize=8.5, color="#8a6a3c")
    ax.text(rh.BOARD_W + 0.7, -JOIST_D / 2, "2x8 joist", fontsize=8.5, color="#8a6a3c", va="center")
    ax.text(rh.BOARD_W + 0.7, BOTTOM_FIRST - rh.SCREW_Y[1] - 0.05, f"two #8 x 1 screws per hook,\n{frac(rh.SCREW_X)} in from the board edge,\n{frac(rh.SCREW_Y[0])} and {frac(rh.SCREW_Y[1])} up from\nthe hook's bottom edge", fontsize=7.5, va="top", color="#1f2430")
    ax.text(-rh.CANT - 0.1, BOTTOM_FIRST + (N_HOOKS - 1) * PITCH - 2.4, f"jaws reach\n{frac(rh.CANT)} past\nthe edge", fontsize=8, ha="right", va="top", color="#2b4f9e")
    ax.text(rh.BOARD_W + 0.7, BOTTOM_FIRST + PITCH + 0.5, "hook bottoms at\n" + ", ".join(frac(BOTTOM_FIRST + PITCH * i) for i in range(N_HOOKS)) + "\nbelow the joist, no gaps;\nrods rest about\n" + frac(FIRST) + " in down, then\nevery " + frac(PITCH), fontsize=7.5, va="top", color="#1f2430")
    ax.set_xlim(-6.2, rh.BOARD_W + 5.9)
    ax.set_ylim(BOARD_LEN - BOARD_ABOVE + 1.0, -JOIST_D - PLY - 0.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Where the hooks go: {N_HOOKS} hooks butted, {frac(PITCH)} in each, filling the {frac(rh.HANG)} in hang", fontsize=10.5, loc="left")
    fig.tight_layout()
    out = IMAGES / "board-layout.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print("drew", out)


def pocket_face_on():
    """3. retention close-up: the hook face on, orthographic, with a 5/8 and a 3/8 rod in the pocket."""
    s3 = rh.seat_point(0.375)
    scene3 = f"""
{HOOK}
{rod(0.625, length=1.0)}
color("#888888") translate([{s3[0] * IN}, {s3[1] * IN}, {rh.T * IN}]) cylinder(h={0.3 * IN}, d={0.375 * IN}, $fn=48);
"""
    render("pocket-face-on", scene3, "0,0,0,0,0,0,0", size=(1200, 1000), projection="o")


if __name__ == "__main__":
    main()
    pocket_face_on()
