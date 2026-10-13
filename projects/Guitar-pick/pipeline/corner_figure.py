"""Draw one layer's wall toolpaths at the pick's right shoulder as an SVG: the beads as strokes of their real width,
path starts and ends as dots. Used to show what the slicer did at the corner in the first standing print (a
separate neck bead and the loop's seam on the pick's edge) against the two-line version.

    .venv/bin/python corner_figure.py <plate_1.gcode> <z> <out.svg> [title] [edge_x]

edge_x: where the pick's designed outline is at that height, mm from the pick's centre (shoulders.py's x_outline);
without it the dashed line sits at the furthest x-running outer wall, which in the neck layers is the block's wall.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toolpath  # noqa: E402

WIN = (3.0, 2.2)        # mm shown: 3.0 along the pick (x), 2.2 across (y), centred on the strip's end
SCALE = 200             # px per mm


def centre(layers):
    zs = sorted(layers)
    zmid = min(zs, key=lambda v: abs(v - 20.0))
    ow = [s for s in layers[zmid] if s[5] == "Outer wall"]
    xs = [v for s in ow for v in (s[0], s[2])]
    cx0 = (min(xs) + max(xs)) / 2
    xs_p = [v for v in xs if v < cx0 + 10]
    cx = (min(xs_p) + max(xs_p)) / 2
    ys_p = [s[1] for s in ow if abs(s[0] - cx) < 10]
    return cx, (min(ys_p) + max(ys_p)) / 2


def figure(gcode_path, z_want, out, title="", edge_x=None):
    layers = toolpath.parse(open(gcode_path, errors="replace").read())
    cx, cy = centre(layers)
    z = min(layers, key=lambda v: abs(v - z_want))
    walls = [s for s in layers[z] if s[5] in ("Outer wall", "Inner wall") and abs(s[1] - cy) < 1.5 and s[0] - cx > 2]
    # the strip's end: the furthest outer-wall point within 0.5 mm of the mid-plane that is still part of the pick's
    # faces (x running), not the block's inner face (y running)
    tip = max(max(s[0], s[2]) for s in walls if s[5] == "Outer wall" and abs(s[1] - cy) < 0.5 and abs(s[2] - s[0]) >= abs(s[3] - s[1]))
    edge = cx + edge_x if edge_x is not None else tip
    x0, y0 = edge - WIN[0] * 0.55, -WIN[1] / 2
    w, h = WIN[0] * SCALE, WIN[1] * SCALE

    def px(x, y):
        return (x - x0) * SCALE, (-(y - cy) - y0) * SCALE
    colour = {"Outer wall": "#2a5d9f", "Inner wall": "#8fb0d8"}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" font-family="system-ui, sans-serif">',
             f'<rect width="{w:.0f}" height="{h:.0f}" fill="#f6f4ef"/>']
    # 0.5 mm grid
    for i in range(0, int(WIN[0] / 0.5) + 1):
        parts.append(f'<line x1="{i * 0.5 * SCALE:.0f}" y1="0" x2="{i * 0.5 * SCALE:.0f}" y2="{h:.0f}" stroke="#e2ddd2" stroke-width="1"/>')
    for i in range(0, int(WIN[1] / 0.5) + 1):
        parts.append(f'<line x1="0" y1="{i * 0.5 * SCALE:.0f}" x2="{w:.0f}" y2="{i * 0.5 * SCALE:.0f}" stroke="#e2ddd2" stroke-width="1"/>')
    for s in walls:
        if s[5] == "Inner wall":
            (ax, ay), (bx, by) = px(s[0], s[1]), px(s[2], s[3])
            parts.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{colour[s[5]]}" stroke-width="{s[4] * SCALE:.1f}" stroke-linecap="round" opacity="0.9"/>')
    for s in walls:
        if s[5] == "Outer wall":
            (ax, ay), (bx, by) = px(s[0], s[1]), px(s[2], s[3])
            parts.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{colour[s[5]]}" stroke-width="{s[4] * SCALE:.1f}" stroke-linecap="round" opacity="0.9"/>')
    n_ends = 0
    for s in walls:
        for flag, x, y, kind in ((s[7], s[0], s[1], "start"), (s[8], s[2], s[3], "end")):
            if flag:
                ax, ay = px(x, y)
                if not (0 <= ax <= w and 0 <= ay <= h):
                    continue
                n_ends += 1
                fill = "#d9480f" if kind == "start" else "#1b1b1b"
                parts.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="9" fill="{fill}" stroke="#fff" stroke-width="2"/>')
    ex, ey = px(edge, cy)
    parts.append(f'<line x1="{ex:.1f}" y1="{ey - 110:.1f}" x2="{ex:.1f}" y2="{ey + 110:.1f}" stroke="#1b1b1b" stroke-width="1.5" stroke-dasharray="6 5"/>')
    parts.append(f'<text x="{ex + 8:.1f}" y="{ey - 95:.1f}" font-size="22" fill="#1b1b1b">pick edge</text>')
    parts.append(f'<text x="14" y="30" font-size="24" fill="#1b1b1b" font-weight="600">{title}</text>')
    parts.append(f'<text x="14" y="{h - 16:.0f}" font-size="18" fill="#5a5a5a">z {z:.2f} mm, 0.5 mm grid, {n_ends} path starts or ends in view</text>')
    parts.append("</svg>")
    Path(out).write_text("\n".join(parts))
    print(out, "z", z, "tip", round(tip - cx, 2), "ends", n_ends)


if __name__ == "__main__":
    figure(sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "",
           float(sys.argv[5]) if len(sys.argv) > 5 else None)
