"""LC2 "Leader Card" text proposal: four ways to fill the interior with a two-line
wordmark, drawn to scale from real glyph geometry and checked against the card's
existing cuts. Nothing here is written back into leader_card.py; this only
produces the comparison page for Brian to pick from.

The interior clear zone (no comb slots) is exactly CARD_L - 2*SLOT_D long, which
is exactly 2.25 in (57.15 mm): the fraction Brian asked the text to fill IS the
full gap between the two wrap-edge combs. The LC2 label stays where it is, in
its existing strip, kept for field-test reference.

Run:  .venv/bin/python projects/Leader-cards/prototype/text_options.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import leader_card as lc  # noqa: E402
from build123d import Align, Kind, Pos, Rectangle, Text, offset  # noqa: E402

IN = lc.IN
L, W = lc.CARD_L, lc.CARD_W
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NARROW = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"

X_SAFE = L / 2 - lc.SLOT_D  # interior half-length clear of every comb slot
TARGET_W = 2 * X_SAFE
assert abs(TARGET_W - 2.25 * IN) < 1e-6, TARGET_W  # confirms Brian's 2.25 in IS this clear zone

LABEL_BB = lc.label_sketch().bounding_box()  # the actual "LC2" glyphs, not the wider strip reserved for them
LABEL_MARGIN = 1.0
Y_HARD_TOP = W / 2 - lc.TOP_ROUND - 0.5  # stay off the card's own top edge round
Y_HARD_BOT = -W / 2 + lc.TOP_ROUND + 0.5  # stay off the bottom edge round


def slot_overlap_area(shape):
    """Area of `shape` that falls in a comb or side-slot hole (should be ~0)."""
    return (shape - lc.plan_face()).area


def hits_label(bb):
    return not (bb.max.X < LABEL_BB.min.X - LABEL_MARGIN or bb.min.X > LABEL_BB.max.X + LABEL_MARGIN or
                bb.max.Y < LABEL_BB.min.Y - LABEL_MARGIN or bb.min.Y > LABEL_BB.max.Y + LABEL_MARGIN)


def find_fit(top, bot, total_h):
    """Scan vertical centres for one with no slot overlap and no collision with the LC2 label;
    returns (y0, overlap_area) for the best candidate (lowest overlap, ties broken by centring)."""
    lo, hi = Y_HARD_BOT + total_h / 2, Y_HARD_TOP - total_h / 2
    if lo > hi:
        return None, None
    best = None
    for i in range(41):
        y0 = lo + (hi - lo) * i / 40
        t, b = Pos(0, y0) * top, Pos(0, y0) * bot
        bb = t.bounding_box().add(b.bounding_box())
        if hits_label(bb):
            continue
        overlap = slot_overlap_area(t) + slot_overlap_area(b)
        score = (round(overlap, 4), abs(y0 - (lo + hi) / 2))
        if best is None or score < best[0]:
            best = (score, y0)
    return (best[1], best[0][0]) if best else (None, None)


def sized(word, font, target_w):
    """Font size (mm) that makes `word` in `font` exactly target_w wide, from one probe render."""
    probe = Text(word, 10, font_path=font)
    return 10 * target_w / probe.bounding_box().size.X


def sample(edge):
    n = 2 if edge.geom_type.name == "LINE" else 24
    return [(p.X, p.Y) for p in (edge.position_at(i / (n - 1)) for i in range(n))]


def chain(edges):
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


def outline_path(shape):
    """Card body / slot cuts: outer wire only (no inner holes on this geometry)."""
    d = []
    for face in shape.faces():
        for loop in chain(face.outer_wire().edges()):
            d.append("M" + " L".join(f"{x:.3f},{-y:.3f}" for x, y in loop) + " Z")
    return " ".join(d)


def glyph_path(shape):
    """Text glyphs: outer wire plus every inner wire (letter counters), evenodd fill."""
    d = []
    for face in shape.faces():
        for wire in [face.outer_wire()] + face.inner_wires():
            for loop in chain(wire.edges()):
                d.append("M" + " L".join(f"{x:.3f},{-y:.3f}" for x, y in loop) + " Z")
    return " ".join(d)


def crop_to(shape, view, pad=1.0):
    box = Pos(view[0] - pad, view[1] - pad) * Rectangle(view[2] - view[0] + 2 * pad, view[3] - view[1] + 2 * pad,
                                                        align=(Align.MIN, Align.MIN))
    return shape & box


def vb(view):
    return f"{view[0]:.3f} {-view[3]:.3f} {view[2] - view[0]:.3f} {view[3] - view[1]:.3f}"


def wordmark(top_word, bot_word, font, gap_frac, poster, upper=False, scale=1.0):
    """Two centred, stacked glyph shapes plus their combined bounding height."""
    tw = top_word.upper() if upper else top_word
    bw = bot_word.upper() if upper else bot_word
    fs_top = sized(tw, font, TARGET_W * scale)
    fs_bot = sized(bw, font, TARGET_W * scale) if poster else fs_top
    top = Text(tw, fs_top, font_path=font)
    bot = Text(bw, fs_bot, font_path=font)
    ht, hb = top.bounding_box().size.Y, bot.bounding_box().size.Y
    gap = gap_frac * (ht + hb) / 2
    total_h = ht + gap + hb
    y_top_line = total_h / 2 - ht / 2  # local centre of the top word, block centred on 0
    y_bot_line = -(total_h / 2 - hb / 2)
    top = Pos(-top.bounding_box().center().X, y_top_line - top.bounding_box().center().Y) * top
    bot = Pos(-bot.bounding_box().center().X, y_bot_line - bot.bounding_box().center().Y) * bot
    return top, bot, total_h, (fs_top, fs_bot)


VARIANTS = [
    dict(key="even", title="Even weight", font=DEJAVU, font_name="DejaVu Sans Bold", gap_frac=0.35, poster=False, upper=False,
         desc="“Leader” is sized to fill the full 2.25 in interior; “Card” sits under it at the same letter height, so it comes out narrower. Same bold face as the LC2 label."),
    dict(key="poster", title="Poster fill", font=DEJAVU, font_name="DejaVu Sans Bold", gap_frac=0.30, poster=True, upper=False,
         desc="Both words are scaled independently to each fill the full 2.25 in, so “Card”’s four letters come out taller than “Leader”’s six. A bolder, more graphic wordmark."),
    dict(key="narrow", title="Condensed caps", font=NARROW, font_name="Liberation Sans Narrow Bold", gap_frac=0.35, poster=False, upper=True,
         desc="Same even-weight rule as the first option, but a condensed, all-caps face. The narrower letterforms leave more vertical room, so the block sits smaller in the band."),
    dict(key="tight", title="Tight, maximal scale", font=DEJAVU, font_name="DejaVu Sans Bold", gap_frac=0.08, poster=False, upper=False,
         desc="Same face and sizing rule as the first option, but the lines sit almost touching, using the freed-up height to read as one bold block from across the tackle box."),
]


def build_variant(v):
    """Shrink from TARGET_W only as far as needed to find a vertical position with zero
    real overlap against the actual slot cuts and no collision with the existing LC2 label."""
    scale = 1.0
    for _ in range(30):
        top, bot, total_h, sizes = wordmark("Leader", "Card", v["font"], v["gap_frac"], v["poster"], v["upper"], scale)
        y0, overlap = find_fit(top, bot, total_h)
        if y0 is not None and overlap < 1e-3:
            fill = scale * TARGET_W / (2.25 * IN)
            return Pos(0, y0) * top, Pos(0, y0) * bot, total_h, sizes, fill
        scale *= 0.97
    raise AssertionError((v["key"], "no fit found down to", scale))


def card_svg(face, top_round, glyphs):
    view = (-L / 2 - 4, -W / 2 - 4, L / 2 + 4, W / 2 + 4)
    lb = lc.label_sketch().bounding_box()
    label = (f'<text class="labeltext" x="{lb.center().X:.2f}" y="{-lb.center().Y:.2f}" text-anchor="middle" '
             f'dominant-baseline="central">{lc.VERSION}</text>')
    return (f'<svg viewBox="{vb(view)}" role="img" aria-label="Card with proposed Leader Card text, top view to scale">'
            f'<path class="card" d="{outline_path(crop_to(face, view))}"/>'
            f'<path class="roundline" d="{outline_path(crop_to(top_round, view))}"/>'
            f'<path class="glyph" d="{glyph_path(glyphs)}"/>{label}</svg>')


if __name__ == "__main__":
    face = lc.plan_face()
    top_round = offset(face, -lc.TOP_ROUND, kind=Kind.ARC)
    tpl = open(f"{HERE}/text-options-template.html").read()
    report = {}
    for v in VARIANTS:
        top, bot, total_h, sizes, fill = build_variant(v)
        svg = card_svg(face, top_round, top + bot)
        tpl = tpl.replace(f"<!--SVG:{v['key']}-->", svg)
        tpl = tpl.replace(f"<!--DESC:{v['key']}-->", v["desc"])
        fill_note = "fills the full 2.25 in" if fill > 0.995 else f"fills {fill * 2.25:.2f} in of the 2.25 in target (shrunk to clear the middle side slot and the LC2 label)"
        tpl = tpl.replace(f"<!--META:{v['key']}-->",
                           f'{v["font_name"]} &middot; “Leader” {sizes[0]:.1f} mm cap size, '
                           f'“Card” {sizes[1]:.1f} mm &middot; block {total_h:.1f} mm tall &middot; {fill_note}')
        report[v["key"]] = {"leader_mm": round(sizes[0], 2), "card_mm": round(sizes[1], 2), "block_h": round(total_h, 2), "fill": round(fill, 3)}
    assert "<!--" not in tpl.split("<style>")[1], "unfilled marker"
    open(f"{HERE}/text-options.html", "w").write(tpl)
    print("target width mm", round(TARGET_W, 3), "= 2.25 in interior clear zone")
    print(report)
