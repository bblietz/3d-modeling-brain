"""LC2 proposal page: to-scale plan drawings of the straight tapered slot layout.

Builds the LC2 plan outline (the face the model will extrude): a 3 x 1.5 in card,
one straight tapered 3/8 in slot on each long edge 1 in from its wrap edge, and
a comb of the same tapered slots along both wrap edges. No hook, entry channel,
funnel, exit ramps, wave or corner lugs. Fills lc2-template.html -> lc2.html.

Run:  .venv/bin/python projects/Leader-cards/prototype/lc2_page.py
"""
import math
import os

from build123d import Align, Kind, Polygon, Pos, Rectangle, RectangleRounded, Rot, offset

HERE = os.path.dirname(os.path.abspath(__file__))
IN = 25.4

L, W = 3 * IN, 1.5 * IN
CORNER_R = 2.9
TOP_ROUND = 0.6  # face-edge round on every slot wall, drawn as the dashed line
R_PLAN = 0.8  # plan round on slot mouths and tooth tips
TIP_ROUND = 0.1  # slot ends in a 0.2 mm gap, narrower than 10 lb line

SLOT_D = 3 / 8 * IN  # every slot, long edge and comb
SLOT_W = 1.2  # mouth width, tapering to closed at SLOT_D
SLOT_FROM_WRAP = L / 3  # long-edge slot centreline to its wrap edge
COMB_PITCH = 4.0
COMB_N = 7  # as many as fit between the two label strips at this pitch
LABEL_STRIP = 5.9  # clear band along each long edge, outside the comb

LINES = [("10 lb", 0.28, "l10"), ("25 lb", 0.50, "l25"), ("40 lb", 0.70, "l40")]
VERSION = "LC2"
LABEL_X, LABEL_Y = -12.0, -W / 2 + (TOP_ROUND + 0.5 + LABEL_STRIP - 0.5) / 2


def taper():
    """Slot in its own frame: mouth on the X axis, running +Y into the card, closed at SLOT_D."""
    h = SLOT_W / 2
    return Polygon((-h, -1), (h, -1), (h, 0), (0, SLOT_D), (-h, 0), align=None)


def stop_depth(dia):
    return SLOT_D * (1 - dia / SLOT_W)


def comb_ys():
    return [(i - (COMB_N - 1) / 2) * COMB_PITCH for i in range(COMB_N)]


def slot_places():
    """(mouth x, mouth y, rotation) for every slot; rotation turns local +Y into the card."""
    places = [(L / 2 - SLOT_FROM_WRAP, -W / 2, 0), (-(L / 2 - SLOT_FROM_WRAP), W / 2, 180)]
    places += [(L / 2, y, 90) for y in comb_ys()] + [(-L / 2, y, -90) for y in comb_ys()]
    return places


def plan_face():
    face = RectangleRounded(L, W, CORNER_R)
    for x, y, r in slot_places():
        face -= Pos(x, y) * Rot(0, 0, r) * taper()
    face = offset(offset(face, TIP_ROUND, kind=Kind.ARC), -TIP_ROUND, kind=Kind.ARC)
    return offset(offset(face, -R_PLAN, kind=Kind.ARC), R_PLAN, kind=Kind.ARC)


def check():
    x0 = L / 2 - SLOT_FROM_WRAP
    assert COMB_PITCH - SLOT_W >= 2 * R_PLAN + 0.5, "comb teeth too thin"
    assert max(comb_ys()) + SLOT_W / 2 <= W / 2 - LABEL_STRIP, "comb runs into the label strip"
    assert x0 + SLOT_W / 2 + R_PLAN <= L / 2 - SLOT_D - 2.0, "long-edge slot too close to the comb"
    assert LABEL_X + 5 <= x0 - SLOT_W / 2 - R_PLAN - 2.0, "label too close to the slot"
    assert stop_depth(LINES[0][1]) <= SLOT_D - 2 * TIP_ROUND / (SLOT_W / SLOT_D) - 0.3, "10 lb stops past the slot end"


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
    view = (-L / 2 - 5, -W / 2 - 7.5, L / 2 + 8, W / 2 + 7)
    x0 = L / 2 - SLOT_FROM_WRAP
    d25 = stop_depth(0.50)
    ys = comb_ys()
    # sample wraps: start in the long-edge slot, run to the +X comb, then lie in comb slots across the face
    wraps = f'<path class="wrap" d="M{x0:.2f},{W / 2 - d25:.2f} L{L / 2 - d25:.2f},{-ys[1]:.2f}"/>'
    wraps += "".join(f'<line class="wrap" x1="{-L / 2 + d25:.2f}" y1="{-y:.2f}" x2="{L / 2 - d25:.2f}" y2="{-y:.2f}"/>'
                     for y in ys[2:])
    t = 0.9  # tick half length
    dims = (
        f'<line class="dim" x1="{-L / 2}" y1="{-(W / 2 + 3.5)}" x2="{L / 2}" y2="{-(W / 2 + 3.5)}"/>'
        f'<line class="dim" x1="{-L / 2}" y1="{-(W / 2 + 3.5 - t)}" x2="{-L / 2}" y2="{-(W / 2 + 3.5 + t)}"/>'
        f'<line class="dim" x1="{L / 2}" y1="{-(W / 2 + 3.5 - t)}" x2="{L / 2}" y2="{-(W / 2 + 3.5 + t)}"/>'
        f'<text class="dimtext" x="0" y="{-(W / 2 + 4.6):.2f}" text-anchor="middle">3 in (76.2 mm)</text>'
        f'<line class="dim" x1="{L / 2 + 4}" y1="{-W / 2}" x2="{L / 2 + 4}" y2="{W / 2}"/>'
        f'<line class="dim" x1="{L / 2 + 4 - t}" y1="{-W / 2}" x2="{L / 2 + 4 + t}" y2="{-W / 2}"/>'
        f'<line class="dim" x1="{L / 2 + 4 - t}" y1="{W / 2}" x2="{L / 2 + 4 + t}" y2="{W / 2}"/>'
        f'<text class="dimtext" x="{L / 2 + 6.2:.2f}" y="0" text-anchor="middle" transform="rotate(90 {L / 2 + 6.2:.2f} 0)">{W / IN:g} in ({W:.1f} mm)</text>'
        f'<line class="dim" x1="{x0:.2f}" y1="{W / 2 + 3.5}" x2="{L / 2}" y2="{W / 2 + 3.5}"/>'
        f'<line class="dim" x1="{x0:.2f}" y1="{W / 2 + 3.5 - t}" x2="{x0:.2f}" y2="{W / 2 + 3.5 + t}"/>'
        f'<line class="dim" x1="{L / 2}" y1="{W / 2 + 3.5 - t}" x2="{L / 2}" y2="{W / 2 + 3.5 + t}"/>'
        f'<text class="dimtext" x="{(x0 + L / 2) / 2:.2f}" y="{W / 2 + 6.2:.2f}" text-anchor="middle">1 in to the wrap edge</text>'
    )
    label = (f'<text class="labeltext" x="{LABEL_X}" y="{-LABEL_Y:.2f}" text-anchor="middle" '
             f'dominant-baseline="central">{VERSION}</text>')
    return (f'<svg viewBox="{vb(view)}" role="img" aria-label="LC2 card, top view to scale">'
            f'<path class="card" d="{path(crop_to(face, view))}"/><path class="roundline" d="{path(crop_to(top, view))}"/>'
            f'{label}{wraps}{dims}</svg>')


def detail_svg(face, top):
    x0 = L / 2 - SLOT_FROM_WRAP
    e = -W / 2
    view = (x0 - 5.5, e - 2.2, x0 + 9.5, e + SLOT_D + 2.2)
    dots, notes = "", ""
    for i, (name, dia, cls) in enumerate(LINES):
        s = stop_depth(dia)
        dots += f'<circle class="{cls}" cx="{x0:.3f}" cy="{-(e + s):.3f}" r="{dia / 2:.3f}"/>'
        ty = -(e + s)
        notes += (f'<line class="tick" x1="{x0 + 0.9:.2f}" y1="{ty:.2f}" x2="{x0 + 2.2:.2f}" y2="{ty:.2f}"/>'
                  f'<text class="note" x="{x0 + 2.4:.2f}" y="{ty + 0.16:.2f}">{name}, {s:.1f} mm deep</text>')
    depth = (
        f'<line class="dim" x1="{x0 - 3.2:.2f}" y1="{-e:.2f}" x2="{x0 - 3.2:.2f}" y2="{-(e + SLOT_D):.2f}"/>'
        f'<line class="dim" x1="{x0 - 3.6:.2f}" y1="{-e:.2f}" x2="{x0 - 2.8:.2f}" y2="{-e:.2f}"/>'
        f'<line class="dim" x1="{x0 - 3.6:.2f}" y1="{-(e + SLOT_D):.2f}" x2="{x0 - 2.8:.2f}" y2="{-(e + SLOT_D):.2f}"/>'
        f'<text class="note" x="{x0 - 3.5:.2f}" y="{-(e + SLOT_D / 2):.2f}" text-anchor="middle" '
        f'transform="rotate(-90 {x0 - 3.5:.2f} {-(e + SLOT_D / 2):.2f})">3/8 in (9.5 mm)</text>'
        f'<text class="note" x="{x0:.2f}" y="{-e + 1.5:.2f}" text-anchor="middle">1.2 mm mouth, closes at 3/8 in</text>'
    )
    return (f'<svg viewBox="{vb(view)}" role="img" aria-label="One tapered slot with line stop depths, to scale">'
            f'<path class="card" d="{path(crop_to(face, view))}"/><path class="roundline" d="{path(crop_to(top, view))}"/>'
            f'{dots}{notes}{depth}</svg>')


if __name__ == "__main__":
    check()
    face = plan_face()
    assert len(face.faces()) == 1, "outline should be one face"
    top = offset(face, -TOP_ROUND, kind=Kind.ARC)
    tpl = open(f"{HERE}/lc2-template.html").read()
    tpl = tpl.replace("<!--FULL-->", full_svg(face, top)).replace("<!--DETAIL-->", detail_svg(face, top))
    assert "<!--" not in tpl.split("<style>")[1], "unfilled marker"
    open(f"{HERE}/lc2.html", "w").write(tpl)
    print("stops", {n: round(stop_depth(d), 2) for n, d, _ in LINES},
          "taper deg", round(2 * math.degrees(math.atan(SLOT_W / 2 / SLOT_D)), 1), "bytes", len(tpl))
