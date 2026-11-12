#!/usr/bin/env python
"""OpenSCAD scene renders of the real hook STLs (the model frame, y up), all three versions:
each hook on a 1x4 with its rod, the tip board and the butt board hanging from two
joists with five rods spanning them (the butt board carries a mix of the two grip
hooks), and orthographic face-on close-ups of each pocket for the retention check.
Plus a to-scale matplotlib drilling guide, a board per hook.

Run from the vault root after rod_hook.py:
  .venv/bin/python projects/Fishing-rod-holder/pipeline/renders.py
"""
import subprocess
import sys
from pathlib import Path

from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rod_hook as rh  # noqa: E402

PROJECT = Path(__file__).resolve().parents[1]
IMAGES = PROJECT / "images"
SCRATCH = Path("/tmp/claude-1000/-home-brian--claude-spares-spare-OJ6Ifx/3f3590ae-4308-446d-b672-0d51f52c10fb/scratchpad/hook")
OPENSCAD = Path.home() / ".local/bin/openscad"
IN = rh.IN
TIP, BUTT, SLIM = rh.TIP, rh.BUTT, rh.SLIM
# the model frame (y up); <stem>.stl is the standing print frame, never used for a scene
STL = {v.name: PROJECT / f"{v.stem}-model.stl" for v in rh.VARIANTS.values()}
BLANK_D, GRIP_D, SLIM_D = rh.SHOW_ROD["tip"], rh.SHOW_ROD["butt"], rh.SHOW_ROD["slim"]   # 3/8 blank in the tip hook, 1-7/8 grip in the 2 in hook, 1-1/4 grip in the 1.5 in hook
HOOK_COLOR, ROD_COLOR, GRIP_COLOR = "#2f6fe4", "#333333", "#b98b5a"   # the grip is cork

JOIST_D, JOIST_T, PLY = 7.25, 1.5, 0.75
BOARD_LEN, BOARD_ABOVE = 27.0, 7.0      # Brian's comb: 27 in overall, 7 in up the joist
JOIST_GAP = 32.0                         # tip joist to butt joist along the rod: illustrative only, the real spacing is whatever the garage has
GRIP_LEN = 10.0                          # of grip drawn in the two-board scene
N_HOOKS = rh.HOOKS_PER_BOARD             # five hooks butted fill the hang
PITCH = rh.H                             # no gap between hooks: pitch is the hook height
BOTTOM_FIRST = rh.H                      # the top hook starts at the joist bottom
GRIP_BOARD = [BUTT] * 3 + [SLIM] * 2     # the butt board's hooks from the top: an example mix, they butt alike (same height, tab and screws)
assert len(GRIP_BOARD) == N_HOOKS
SEAT_TIP = TIP.seat_point(BLANK_D)       # where a 3/8 blank rests, in hook coordinates (x, y up from the hook bottom)
FIRST_TIP = BOTTOM_FIRST - SEAT_TIP[1]   # the top blank's depth below the joist
GAP_COLOR = "#d7263d"                    # the dimension bar for the gap between a grip hook's lip tip and the hook butted above


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


def hook(variant, alpha=None, dy=0.0, dz=0.0):
    """The hook STL in the model frame, moved up dy and along the rod dz (inches); alpha makes it translucent."""
    col = f'"{HOOK_COLOR}"' if alpha is None else f'"{HOOK_COLOR}", {alpha}'
    return f'color({col}) translate([0, {dy * IN}, {dz * IN}]) import("{STL[variant.name]}");'


def rod(variant, d, length=8.0, x=None, y=None, z=0.0, color=ROD_COLOR):
    """A rod of diameter d along z, centred on z, at the variant's seat unless x, y (inches) are given."""
    sx, sy = variant.seat_point(d)
    x = sx if x is None else x
    y = sy if y is None else y
    return f'color("{color}") translate([{x * IN}, {y * IN}, {(z - length / 2) * IN}]) cylinder(h={length * IN}, d={d * IN}, $fn=48);'


def board(length_in, y0_in, z0=0.0):
    """1x4 on edge behind the hooks: x 0..3.5, z z0-0.75..z0, y from y0 up by length."""
    return f'color("#d8b98a") translate([0, {y0_in * IN}, {(z0 - rh.BOARD_T) * IN}]) cube([{rh.BOARD_W * IN}, {length_in * IN}, {rh.BOARD_T * IN}]);'


def pt(p):
    return f"[{p[0] * IN}, {p[1] * IN}, {p[2] * IN}]"


def hook_on_board(variant, d, color, name):
    """1. one hook on a 6 in board stub with its rod seated.
    Model y (up) becomes world z so the board stands and the rod lies horizontal."""
    scene = f"""
rotate([90, 0, 0]) {{
  {board(6.0, -1.5)}
  {hook(variant)}
  {rod(variant, d, color=color)}
}}
"""
    render(name, scene, "0,0,0,75,0,-40,0", size=(1200, 900))


def boards_in_place():
    """2. the tip board and the butt board hanging from two joists, five hooks butted on each
    (tip hooks on one, GRIP_BOARD's mix on the other), and five rods spanning them: a blank
    seated in the tip hook running back to a grip seated in the hook it is in. The tip board
    is nearer the camera."""
    z_tip, z_butt = 0.0, -JOIST_GAP
    parts = []
    for z0 in (z_tip, z_butt):
        parts.append(board(BOARD_LEN, BOARD_ABOVE - BOARD_LEN, z0))
        parts.append(f'color("#c9a46e") translate([-{4 * IN}, 0, {(z0 - rh.BOARD_T - JOIST_T) * IN}]) cube([{12 * IN}, {JOIST_D * IN}, {JOIST_T * IN}]);')
    parts.append(f'color("#e8d6b3") translate([-{4 * IN}, {JOIST_D * IN}, {(z_butt - 8) * IN}]) cube([{12 * IN}, {PLY * IN}, {(JOIST_GAP + 16) * IN}]);')
    grip_near = z_butt + rh.T / 2 + GRIP_LEN / 2      # the grip is centred on the butt hook; this is its end toward the tip board
    for i, grip_hook in enumerate(GRIP_BOARD):
        hook_y = -(BOTTOM_FIRST + PITCH * i)            # hook bottom edge below the joist bottom, the same on both boards
        d = rh.SHOW_ROD[grip_hook.name]
        seat = grip_hook.seat_point(d)                  # where this hook's grip rests: each of the three hooks has its own seat
        parts.append(hook(TIP, dy=hook_y, dz=z_tip))
        parts.append(hook(grip_hook, dy=hook_y, dz=z_butt))
        # the blank: from 4 in past the tip hook back to the grip's end, tilted by the difference between the two seats
        a = (SEAT_TIP[0], hook_y + SEAT_TIP[1], z_tip + rh.T + 4.0)
        b = (seat[0], hook_y + seat[1], grip_near)
        parts.append(f'color("{ROD_COLOR}") hull() {{ translate({pt(a)}) sphere(d={BLANK_D * IN}, $fn=24); translate({pt(b)}) sphere(d={BLANK_D * IN}, $fn=24); }}')
        parts.append(rod(grip_hook, d, length=GRIP_LEN, y=hook_y + seat[1], z=z_butt + rh.T / 2, color=GRIP_COLOR))
    scene = f"""
rotate([90, 0, 0]) {{
{chr(10).join(parts)}
}}
"""
    # from the front left, a touch below: -35 stacks the boards, -50 and beyond flattens the hooks to slivers
    render("board-in-place", scene, "0,0,0,100,0,-42,0", size=(1600, 1200))


def main():
    IMAGES.mkdir(exist_ok=True)
    hook_on_board(TIP, BLANK_D, ROD_COLOR, "hook-on-board")
    hook_on_board(BUTT, GRIP_D, GRIP_COLOR, "butt-hook-on-board")
    hook_on_board(SLIM, SLIM_D, GRIP_COLOR, "slim-hook-on-board")
    boards_in_place()
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
    """To-scale drilling guide: three 27 in boards side by side at one scale, a board per hook, five hooks
    butted on each, screw positions, a 3/8 blank in the tip hooks, a 1-7/8 grip in the 2 in hooks and a
    1-1/4 grip in the 1.5 in hooks."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon as MplPolygon, Rectangle

    DX = 14.0   # from one board to the next on the page: the tip board, then the butt board twice, once per grip hook
    X_END = 2 * DX + rh.BOARD_W   # the last board's far edge
    fig, ax = plt.subplots(figsize=(16.2, 11.5), dpi=150)   # 11 in wide held two boards; the same scale for three
    # depth below the joist bottom grows downward on the page
    ink = dict(fontsize=8.5, color="#1f2430")

    def panel(x0, variant, d, rod_color, subtitle):
        ax.add_patch(Rectangle((x0 - 3.5, -JOIST_D - PLY), 10.5, PLY, fc="#e8d6b3", ec="#8a6a3c", lw=0.8, hatch="//", zorder=0))
        ax.add_patch(Rectangle((x0 - 3.5, -JOIST_D), 10.5, JOIST_D, fc="#d8b98a", ec="#8a6a3c", lw=1.0, zorder=0))
        ax.add_patch(Rectangle((x0, -BOARD_ABOVE), rh.BOARD_W, BOARD_LEN, fc="#e9d4ad", ec="#8a6a3c", lw=1.2, zorder=1))
        solid = variant.solid_2d()  # hook outline in hook coords (y up, bottom at 0)
        seat = variant.seat_point(d)
        for i in range(N_HOOKS):
            bottom_depth = BOTTOM_FIRST + PITCH * i
            pts = [(x0 + x, bottom_depth - y) for x, y in solid.exterior.coords]
            ax.add_patch(MplPolygon(pts, closed=True, fc="#5b8def", ec="#2b4f9e", lw=1.0, zorder=3))
            ax.add_patch(Circle((x0 + seat[0], bottom_depth - seat[1]), d / 2, fc=rod_color, ec="black", lw=0.8, zorder=5))
            for sy in rh.SCREW_Y:
                ax.add_patch(Circle((x0 + rh.SCREW_X, bottom_depth - sy), 0.2, fc="#e5e7eb", ec="#1f2430", lw=0.8, zorder=6))
                ax.add_patch(Circle((x0 + rh.SCREW_X, bottom_depth - sy), 0.1, fc="#1f2430", ec="#1f2430", zorder=6.1))
            # hook bottom edge callout
            ax.annotate(frac(bottom_depth), xy=(x0 + rh.BOARD_W + 0.1, bottom_depth), xytext=(x0 + rh.BOARD_W + 0.7, bottom_depth),
                        va="center", arrowprops=dict(arrowstyle="-", color="#1f2430", lw=0.7), zorder=8, **ink)
        ax.text(x0 + 0.1, -BOARD_ABOVE + 0.9, "1x4, 27 in,\n7 in up the joist", fontsize=8.5, color="#8a6a3c")
        ax.text(x0 + rh.BOARD_W + 0.7, -JOIST_D / 2, "2x8 joist", fontsize=8.5, color="#8a6a3c", va="center")
        ax.text(x0 + 1.75, -JOIST_D - PLY - 0.4, subtitle, fontsize=9.5, ha="center", va="bottom", color="#1f2430", fontweight="bold")
        ax.text(x0 - variant.CANT - 0.1, BOTTOM_FIRST + (N_HOOKS - 1) * PITCH - 2.4, f"jaws reach\n{frac(variant.CANT)} past\nthe edge",
                fontsize=8, ha="right", va="top", color="#2b4f9e")

    panel(0.0, TIP, BLANK_D, ROD_COLOR, f"Tip board: {TIP.label} hooks,\n{frac(BLANK_D)} blank drawn at its seat")
    panel(DX, BUTT, GRIP_D, GRIP_COLOR, f"Butt board: {BUTT.label} hooks,\n{frac(GRIP_D)} grip drawn at its seat")
    panel(2 * DX, SLIM, SLIM_D, GRIP_COLOR, f"Butt board: {SLIM.label} hooks,\n{frac(SLIM_D)} grip drawn at its seat")
    # dimensions, once each
    ax.annotate("", xy=(X_END + 5.2, 0), xytext=(X_END + 5.2, BOARD_LEN - BOARD_ABOVE), arrowprops=dict(arrowstyle="<->", lw=0.9), zorder=8)
    ax.text(X_END + 5.05, (BOARD_LEN - BOARD_ABOVE) * 0.8, "20 in hang,\nas now", fontsize=8.5, va="center", ha="right")
    ax.annotate("", xy=(-2.9, BOTTOM_FIRST), xytext=(-2.9, BOTTOM_FIRST + PITCH), arrowprops=dict(arrowstyle="<->", lw=0.9), zorder=8)
    ax.text(-3.05, BOTTOM_FIRST + PITCH / 2, f"{PITCH:g} in\npitch", fontsize=8.5, va="center", ha="right")
    ax.annotate("", xy=(-2.9, 0), xytext=(-2.9, BOTTOM_FIRST), arrowprops=dict(arrowstyle="<->", lw=0.9), zorder=8)
    ax.text(-3.05, BOTTOM_FIRST / 2, f"{frac(BOTTOM_FIRST)}: the top\nhook starts\nat the joist", fontsize=8.5, va="center", ha="right")
    # on each grip board: the room to get the grip in, between the second hook's lip tip and the hook above it (Brian asked
    # 2 in for the 2 in hook and gave no number for the 1.5 in hook), and where the grips rest
    for x0, v, d, note in ((DX, BUTT, GRIP_D, f"(asked {BUTT.MIN_EXIT_GAP:g})"), (2 * DX, SLIM, SLIM_D, f"(grips to {frac(max(SLIM.ROD_DIAS))})")):
        gx = x0 - v.CANT - 0.35
        lip_depth, above_depth = BOTTOM_FIRST + PITCH - v.Y_TIP, BOTTOM_FIRST
        ax.annotate("", xy=(gx, above_depth), xytext=(gx, lip_depth), arrowprops=dict(arrowstyle="<->", lw=0.9, color=GAP_COLOR), zorder=8)
        for depth in (lip_depth, above_depth):
            ax.plot([gx - 0.15, x0 - v.CANT + 0.05], [depth, depth], color=GAP_COLOR, lw=0.6, zorder=8)
        ax.text(gx - 0.2, (lip_depth + above_depth) / 2, f"{frac(rh.H - v.Y_TIP)} in to get\nthe grip in\n{note}",
                fontsize=8, va="center", ha="right", color=GAP_COLOR)
        ax.text(x0 + rh.BOARD_W + 0.7, BOTTOM_FIRST + 2 * PITCH + 0.5,
                f"grip centres rest about\n{frac(BOTTOM_FIRST - v.seat_point(d)[1])} in down,\nthen every {frac(PITCH)}",
                fontsize=7.5, va="top", color="#1f2430")
    # callouts, once, in the gap between the first two boards
    gap_x = rh.BOARD_W + 0.7
    ax.text(gap_x, BOTTOM_FIRST - rh.SCREW_Y[1] - 0.05,
            f"two #8 x 1 screws per hook,\n{frac(rh.SCREW_X)} in from the board edge,\n{frac(rh.SCREW_Y[0])} and {frac(rh.SCREW_Y[1])} up from\nthe hook's bottom edge,\nsame for all three hooks",
            fontsize=7.5, va="top", color="#1f2430")
    ax.text(gap_x, BOTTOM_FIRST + 2 * PITCH + 0.5,
            "hook bottoms at\n" + ", ".join(frac(BOTTOM_FIRST + PITCH * i) for i in range(N_HOOKS)) + "\nbelow the joist, no gaps,\non every board",
            fontsize=7.5, va="top", color="#1f2430")
    ax.text(gap_x, BOTTOM_FIRST + 3 * PITCH + 0.5,
            f"blanks rest about\n{frac(FIRST_TIP)} in down,\nthen every {frac(PITCH)}",
            fontsize=7.5, va="top", color="#1f2430")
    ax.set_xlim(-6.2, X_END + 5.9)
    ax.set_ylim(BOARD_LEN - BOARD_ABOVE + 1.0, -JOIST_D - PLY - 1.9)
    ax.set_aspect("equal")
    ax.axis("off")
    n_words = {4: "four", 5: "five", 6: "six"}.get(N_HOOKS, str(N_HOOKS))
    ax.set_title(f"Where the hooks go: {n_words} hooks butted on each board, {frac(PITCH)} in pitch, same screw layout for all three hooks", fontsize=10.5, loc="left")
    fig.tight_layout()
    out = IMAGES / "board-layout.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print("drew", out)


def pocket_face_on():
    """3. retention close-up: the tip hook face on, orthographic, with a 5/8 and a 3/8 rod in the pocket."""
    s3 = TIP.seat_point(0.375)
    scene3 = f"""
{hook(TIP)}
{rod(TIP, 0.625, length=1.0)}
color("#888888") translate([{s3[0] * IN}, {s3[1] * IN}, {rh.T * IN}]) cylinder(h={0.3 * IN}, d={0.375 * IN}, $fn=48);
"""
    render("pocket-face-on", scene3, "0,0,0,0,0,0,0", size=(1200, 1000), projection="o")


def grip_pocket_face_on(variant, d, ey, name):
    """A grip hook face on, orthographic: a grip of diameter d seated (solid cork), the same grip on
    its way out (translucent, centre over the lip tip at height ey) and the hook butted above
    (translucent, only its lower part drawn) so the gap the grip leaves through shows."""
    sx, sy = variant.seat_point(d)
    ex = -variant.CANT                         # on its way out: centre over the lip tip
    # neither grip cuts plastic: both centres lie where a rod this size can be, with the hooks butted above and below in the way
    free = variant.free_space(d / 2)
    assert free.distance(Point(sx, sy)) < 1e-6, f"{name}: the seated grip is {free.distance(Point(sx, sy)):.4f} in out of the free space"   # the seat is on its boundary
    assert free.contains(Point(ex, ey)), f"{name}: the grip on its way out at ({ex:.3f}, {ey:.3f}) cuts into a hook"
    gap = rh.H - variant.Y_TIP                 # between the lip tip and the hook butted above
    upper_show = variant.Y_TIP + 0.25          # inches of the hook above to draw: its whole lip
    # the gap as a bar beside the lifted grip, from the lip tip's height to the hook above, with ticks back to the tip
    bx, bw, bz = -variant.CANT - d / 2 - 0.3, 0.06, rh.T + 0.3
    scene = f"""
{hook(variant)}
{rod(variant, d, length=1.0, color=GRIP_COLOR)}
color("{GAP_COLOR}") translate([{(bx - bw / 2) * IN}, {variant.Y_TIP * IN}, {bz * IN}]) cube([{bw * IN}, {gap * IN}, 1]);
color("{GAP_COLOR}") translate([{(bx - bw / 2) * IN}, {(variant.Y_TIP - bw / 2) * IN}, {bz * IN}]) cube([{(-variant.CANT - bx + bw) * IN}, {bw * IN}, 1]);
color("{GAP_COLOR}") translate([{(bx - bw / 2) * IN}, {(rh.H - bw / 2) * IN}, {bz * IN}]) cube([{(-variant.CANT - bx + bw) * IN}, {bw * IN}, 1]);
color("{GRIP_COLOR}", 0.4) translate([{ex * IN}, {ey * IN}, {-0.5 * IN}]) cylinder(h={1.0 * IN}, d={d * IN}, $fn=96);
color("{HOOK_COLOR}", 0.35) intersection() {{
  translate([0, {rh.H * IN}, 0]) import("{STL[variant.name]}");
  translate([{-10 * IN}, {rh.H * IN - 0.01}, -10]) cube([{20 * IN}, {upper_show * IN}, 20]);
}}
"""
    render(name, scene, "0,0,0,0,0,0,0", size=(1100, 1200), projection="o")


if __name__ == "__main__":
    main()
    pocket_face_on()
    # the 2 in hook: its 1-7/8 grip at the escape pose, risen from its seat by the escape lift
    grip_pocket_face_on(BUTT, GRIP_D, BUTT.seat_point(GRIP_D)[1] + BUTT.escape_lift(GRIP_D), "butt-pocket-face-on")
    # the 1.5 in hook: its biggest grip (1-3/8), up the lean and over the lip, in the middle of the gap under the hook above
    grip_pocket_face_on(SLIM, max(SLIM.ROD_DIAS), (SLIM.Y_TIP + rh.H) / 2, "slim-pocket-face-on")
