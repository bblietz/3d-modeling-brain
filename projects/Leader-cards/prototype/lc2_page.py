"""LC2 page: to-scale plan drawings of the leader card, straight from leader_card.py.

All geometry comes from ../leader_card.py (plan_face, comb_ys, stop_depth,
label_sketch), so the drawings cannot drift from the model. Fills
lc2-template.html -> lc2.html.

Run:  .venv/bin/python projects/Leader-cards/prototype/lc2_page.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import leader_card as lc  # noqa: E402
from build123d import Align, Kind, Pos, Rectangle, Rot, offset  # noqa: E402

IN = lc.IN
L, W = lc.CARD_L, lc.CARD_W
LINES = [(name, dia, f"l{name.split()[0]}") for name, dia in lc.LINES.items()]


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


def crop_to(shape, view, pad=1.0):
    box = Pos(view[0] - pad, view[1] - pad) * Rectangle(view[2] - view[0] + 2 * pad, view[3] - view[1] + 2 * pad,
                                                        align=(Align.MIN, Align.MIN))
    return shape & box


def vb(view):
    return f"{view[0]:.3f} {-view[3]:.3f} {view[2] - view[0]:.3f} {view[3] - view[1]:.3f}"


def full_svg(face, top):
    view = (-L / 2 - 5, -W / 2 - 4, L / 2 + 8, W / 2 + 7)
    d25 = lc.stop_depth(lc.LINES["25 lb"])
    ys = lc.comb_ys()
    # example wraps lying in comb slots on both wrap edges
    wraps = "".join(f'<line class="wrap" x1="{-L / 2 + d25:.2f}" y1="{-y:.2f}" x2="{L / 2 - d25:.2f}" y2="{-y:.2f}"/>'
                    for y in ys[1:7])
    t = 0.9  # tick half length
    dims = (
        f'<line class="dim" x1="{-L / 2}" y1="{-(W / 2 + 3.5)}" x2="{L / 2}" y2="{-(W / 2 + 3.5)}"/>'
        f'<line class="dim" x1="{-L / 2}" y1="{-(W / 2 + 3.5 - t)}" x2="{-L / 2}" y2="{-(W / 2 + 3.5 + t)}"/>'
        f'<line class="dim" x1="{L / 2}" y1="{-(W / 2 + 3.5 - t)}" x2="{L / 2}" y2="{-(W / 2 + 3.5 + t)}"/>'
        f'<text class="dimtext" x="0" y="{-(W / 2 + 4.6):.2f}" text-anchor="middle">{L / IN:g} in ({L:.1f} mm)</text>'
        f'<line class="dim" x1="{L / 2 + 4}" y1="{-W / 2}" x2="{L / 2 + 4}" y2="{W / 2}"/>'
        f'<line class="dim" x1="{L / 2 + 4 - t}" y1="{-W / 2}" x2="{L / 2 + 4 + t}" y2="{-W / 2}"/>'
        f'<line class="dim" x1="{L / 2 + 4 - t}" y1="{W / 2}" x2="{L / 2 + 4 + t}" y2="{W / 2}"/>'
        f'<text class="dimtext" x="{L / 2 + 6.2:.2f}" y="0" text-anchor="middle" transform="rotate(90 {L / 2 + 6.2:.2f} 0)">{W / IN:g} in ({W:.1f} mm)</text>'
    )
    dims += "".join(f'<text class="dimtext" x="{-L / 2 + f * L:.2f}" y="{-(W / 2 + 1.1):.2f}" text-anchor="middle">{f:.0%}</text>'
                    for f in lc.SIDE_SLOTS)
    lb = lc.label_sketch().bounding_box()
    label = (f'<text class="labeltext" x="{lb.center().X:.2f}" y="{-lb.center().Y:.2f}" text-anchor="middle" '
             f'dominant-baseline="central">{lc.VERSION}</text>')
    return (f'<svg viewBox="{vb(view)}" role="img" aria-label="{lc.VERSION} card, top view to scale">'
            f'<path class="card" d="{path(crop_to(face, view))}"/><path class="roundline" d="{path(crop_to(top, view))}"/>'
            f'{label}{wraps}{dims}</svg>')


def detail_svg(face, top):
    """The middle comb slot on the +X wrap edge, turned so its mouth faces down, with its neighbours."""
    turn = Rot(0, 0, -90)  # (x, y) -> (y, -x): the +X edge becomes the bottom edge
    face, top = turn * face, turn * top
    x0, e = 0.0, -L / 2
    view = (x0 - 5.5, e - 2.2, x0 + 9.5, e + lc.SLOT_D + 2.2)
    dots, notes = "", ""
    for name, dia, cls in LINES:
        s = lc.stop_depth(dia)
        dots += f'<circle class="{cls}" cx="{x0:.3f}" cy="{-(e + s):.3f}" r="{dia / 2:.3f}"/>'
        ty = -(e + s)
        notes += (f'<line class="tick" x1="{x0 + 0.9:.2f}" y1="{ty:.2f}" x2="{x0 + 2.2:.2f}" y2="{ty:.2f}"/>'
                  f'<text class="note" x="{x0 + 2.4:.2f}" y="{ty + 0.16:.2f}">{name}, {s:.1f} mm deep</text>')
    d = lc.SLOT_D
    depth = (
        f'<line class="dim" x1="{x0 - 4.4:.2f}" y1="{-e:.2f}" x2="{x0 - 4.4:.2f}" y2="{-(e + d):.2f}"/>'
        f'<line class="dim" x1="{x0 - 4.8:.2f}" y1="{-e:.2f}" x2="{x0 - 4.0:.2f}" y2="{-e:.2f}"/>'
        f'<line class="dim" x1="{x0 - 4.8:.2f}" y1="{-(e + d):.2f}" x2="{x0 - 4.0:.2f}" y2="{-(e + d):.2f}"/>'
        f'<text class="note" x="{x0 - 4.7:.2f}" y="{-(e + d / 2):.2f}" text-anchor="middle" '
        f'transform="rotate(-90 {x0 - 4.7:.2f} {-(e + d / 2):.2f})">3/8 in ({d:.1f} mm)</text>'
        f'<text class="note" x="{x0:.2f}" y="{-e + 1.5:.2f}" text-anchor="middle">{lc.SLOT_W:g} mm mouth, slots {lc.COMB_PITCH:g} mm apart</text>'
    )
    return (f'<svg viewBox="{vb(view)}" role="img" aria-label="Comb slots with line stop depths, to scale">'
            f'<path class="card" d="{path(crop_to(face, view))}"/><path class="roundline" d="{path(crop_to(top, view))}"/>'
            f'{dots}{notes}{depth}</svg>')


if __name__ == "__main__":
    face = lc.plan_face()
    assert len(face.faces()) == 1, "outline should be one face"
    top = offset(face, -lc.TOP_ROUND, kind=Kind.ARC)
    tpl = open(f"{HERE}/lc2-template.html").read()
    tpl = tpl.replace("<!--FULL-->", full_svg(face, top)).replace("<!--DETAIL-->", detail_svg(face, top))
    assert "<!--" not in tpl.split("<style>")[1], "unfilled marker"
    open(f"{HERE}/lc2.html", "w").write(tpl)
    print("stops", {n: round(lc.stop_depth(d), 2) for n, d, _ in LINES},
          "taper deg", round(2 * math.degrees(math.atan(lc.SLOT_W / 2 / lc.SLOT_D)), 1), "bytes", len(tpl))
