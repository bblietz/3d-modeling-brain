"""Exact plan-view drawings of the slot variants, filled into the page template.

Solid outline: the card at mid-thickness (plan_face, the same face the model
extrudes). Shaded band: the exit ramp on the top face, from the pocket wall to
where it meets the face. Dashed line: where the 0.6 mm top round starts.
Every drawing uses the same view size, so all are at one scale.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leader_card as lc  # noqa: E402
from build123d import Align, Kind, Polygon, Pos, Rectangle, offset  # noqa: E402

HERE = sys.argv[1]

X0 = lc.CARD_L / 2 - lc.SLOT_INSET  # slot mouth x, card frame
EDGE = -lc.CARD_W / 2
VIEW = (X0 - 8.6, EDGE - 1.3, lc.CARD_L / 2 + 1.3, EDGE + 10.4)  # xmin, ymin, xmax, ymax (mm)
PAD = 1.0  # crop past the view so crop edges fall outside the drawing


def sample(edge):
    n = 2 if edge.geom_type.name == "LINE" else 24
    return [(p.X, p.Y) for p in (edge.position_at(i / (n - 1)) for i in range(n))]


def chain(edges):
    """Join sampled edges end to end into closed loops (edge order from OCC is not guaranteed)."""
    segs = [sample(e) for e in edges]
    loops = []
    close = lambda a, b: abs(a[0] - b[0]) < 1e-4 and abs(a[1] - b[1]) < 1e-4
    while segs:
        loop = segs.pop(0)
        grew = True
        while grew and not close(loop[0], loop[-1]):
            grew = False
            for i, s in enumerate(segs):
                if close(loop[-1], s[0]):
                    loop += s[1:]
                elif close(loop[-1], s[-1]):
                    loop += s[::-1][1:]
                else:
                    continue
                segs.pop(i)
                grew = True
                break
        loops.append(loop)
    return loops


def path(shape):
    d = []
    for face in shape.faces():
        for loop in chain(face.outer_wire().edges()):
            d.append("M" + " L".join(f"{x:.3f},{-y:.3f}" for x, y in loop) + " Z")
    return " ".join(d)


crop = Pos(VIEW[0] - PAD, VIEW[1] - PAD) * Rectangle(VIEW[2] - VIEW[0] + 2 * PAD, VIEW[3] - VIEW[1] + 2 * PAD,
                                                     align=(Align.MIN, Align.MIN))
vb = f"{VIEW[0]:.3f} {-VIEW[3]:.3f} {VIEW[2] - VIEW[0]:.3f} {VIEW[3] - VIEW[1]:.3f}"
tpl = open(f"{HERE}/slot-variants-template.html").read()

for i, v in enumerate(lc.VARIANTS, 1):
    m = v["exit"]
    face = lc.plan_face(lc.CARD_L, lc.CARD_W, [(X0, 1, v)])
    card = face & crop
    top = offset(face, -lc.TOP_ROUND, kind=Kind.ARC) & crop

    # ramp on the top face: from the exit wall to where it meets the face, flipped for mirrored slots
    wall_x, y_lo, y_hi, run, _ = lc.ramp_geometry(v)
    corners = [(wall_x(y_lo), y_lo), (wall_x(y_lo) + run, y_lo), (wall_x(y_hi) + run, y_hi), (wall_x(y_hi), y_hi)]
    if m < 0:
        corners.reverse()  # keep the polygon counterclockwise after the flip
    ramp = Polygon(*[(X0 + m * x, EDGE + y) for x, y in corners], align=None) & face
    ym = sum(p[1] for p in lc.line_stops(v)) / 2
    gx1, gx2 = X0 + m * wall_x(ym), X0 + m * (wall_x(ym) + run)

    dots = "".join(f'<circle class="l{j}" cx="{X0 + m * x:.3f}" cy="{-(EDGE + y):.3f}" r="{dia / 2:.3f}"/>'
                   for j, ((x, y), dia) in enumerate(zip(lc.line_stops(v), lc.LINE_DIAS)))

    # annotations in drawing units (mm); SVG y is -world y
    ey = -EDGE
    ay = ey - 8.9
    if m > 0:
        arrow = (f'<line class="annline" x1="{X0 - 1.0:.2f}" y1="{ay:.2f}" x2="{X0 + 5.2:.2f}" y2="{ay:.2f}"/>'
                 f'<path class="arrowhead" d="M{X0 + 5.6:.2f},{ay:.2f} L{X0 + 5.0:.2f},{ay - 0.3:.2f} L{X0 + 5.0:.2f},{ay + 0.3:.2f} Z"/>'
                 f'<text class="ann" x="{X0 - 1.0:.2f}" y="{ay - 0.4:.2f}">wrap tension, to this wrap edge</text>')
    else:
        arrow = (f'<line class="annline" x1="{X0 + 4.0:.2f}" y1="{ay:.2f}" x2="{X0 - 7.4:.2f}" y2="{ay:.2f}"/>'
                 f'<path class="arrowhead" d="M{X0 - 7.8:.2f},{ay:.2f} L{X0 - 7.2:.2f},{ay - 0.3:.2f} L{X0 - 7.2:.2f},{ay + 0.3:.2f} Z"/>'
                 f'<text class="ann" x="{X0 - 7.6:.2f}" y="{ay - 0.4:.2f}">wrap tension, to the far wrap edge</text>')
    ann = (
        f'<text class="ann" x="{VIEW[0] + 0.3:.2f}" y="{ey + 0.95:.2f}">LONG EDGE</text>'
        f'<text class="ann" x="{lc.CARD_L / 2 + 0.9:.2f}" y="{ey - 6.5:.2f}" transform="rotate(-90 {lc.CARD_L / 2 + 0.9:.2f} {ey - 6.5:.2f})">WRAP EDGE</text>'
        f'{arrow}'
        f'<line class="scale" x1="{VIEW[0] + 0.4:.2f}" y1="{ey - 2.2:.2f}" x2="{VIEW[0] + 2.4:.2f}" y2="{ey - 2.2:.2f}"/>'
        f'<line class="scale" x1="{VIEW[0] + 0.4:.2f}" y1="{ey - 2.45:.2f}" x2="{VIEW[0] + 0.4:.2f}" y2="{ey - 1.95:.2f}"/>'
        f'<line class="scale" x1="{VIEW[0] + 2.4:.2f}" y1="{ey - 2.45:.2f}" x2="{VIEW[0] + 2.4:.2f}" y2="{ey - 1.95:.2f}"/>'
        f'<text class="scaletext" x="{VIEW[0] + 0.4:.2f}" y="{ey - 2.7:.2f}">2 mm</text>'
    )
    defs = (f'<defs><linearGradient id="ramp{i}" gradientUnits="userSpaceOnUse" x1="{gx1:.3f}" y1="0" x2="{gx2:.3f}" y2="0">'
            f'<stop offset="0" style="stop-color: var(--ramp)"/><stop offset="1" style="stop-color: var(--part)"/>'
            f'</linearGradient></defs>')
    svg = (f'<svg viewBox="{vb}" role="img" aria-label="Slot variant {i}, top view to scale">{defs}'
           f'<path class="card" d="{path(card)}"/><path class="roundline" d="{path(top)}"/>'
           f'<path class="rampedge" fill="url(#ramp{i})" d="{path(ramp)}"/>{dots}{ann}</svg>')
    tpl = tpl.replace(f"<!--SVG{i}-->", svg)

assert "<!--SVG" not in tpl, "unfilled marker"
open(f"{HERE}/slot-variants.html", "w").write(tpl)
print("viewBox", vb, "bytes", len(tpl))
