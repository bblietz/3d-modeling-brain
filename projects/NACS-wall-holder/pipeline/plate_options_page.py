#!/usr/bin/env python
"""Builds options-2026-10-11.html, the base options for the drum's foot and flange running past the 4 in plate (Brian, 2026-10-11:
"the center cylinder extends past the edge of the base on all 4 sides"), from the renders in images/options-2026-10-11/
(pipeline/render_plate_options.sh). Published as the "Holder Base Options" artifact."""
import base64
import io
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
IMG = f"{PROJECT}/images/options-2026-10-11"


def img(name, box=None):
    im = Image.open(f"{IMG}/{name}.png")
    if box:
        im = im.crop(box)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


BASE = (0, 60, 1100, 850)
FOOT = (0, 150, 1100, 760)
FRONT = (360, 160, 740, 600)


def fig(name, box, title, text, cls=""):
    return f'<figure class="{cls}"><img src="{img(name, box)}" alt="{title}"><figcaption><b>{title}</b>{text}</figcaption></figure>'


def row(key, cls=""):
    return ('<div class="row">'
            + fig(f"{key}-base", BASE, "Over the plate's corner", "The drum's foot and blend on the plate, from the print's point of view (plate down).", cls)
            + fig(f"{key}-foot", FOOT, "Close on the left edge", "Where the blend meets the plate, at the middle of a side.", cls)
            + fig(f"{key}-front", FRONT, "From the front", "The flange and lip against the plate behind them.", cls)
            + "</div>")


page = f"""<title>Holder Base Options</title>
<style>
/* layout: one reading column, a three-picture row per option; the holder's teal and the recess gold as the palette */
:root {{ --bg: #f6f4ee; --fg: #1f2a2c; --muted: #5d6b6e; --accent: #1f7a7c; --gold: #b8860b; --line: #d9d4c7; --card: #ffffff; --pick: #e6f1ef; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #15191a; --fg: #e8e6df; --muted: #a2adaf; --accent: #5cc3c4; --gold: #e0b040; --line: #2e3637; --card: #1d2324; --pick: #1d2f2e; color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg: #15191a; --fg: #e8e6df; --muted: #a2adaf; --accent: #5cc3c4; --gold: #e0b040; --line: #2e3637; --card: #1d2324; --pick: #1d2f2e; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 16px/1.5 Georgia, 'Times New Roman', serif; }}
main {{ max-width: 1100px; margin: 0 auto; padding-block: 24px 64px; padding-inline: 16px; }}
h1 {{ font-size: 1.9rem; line-height: 1.15; margin: 0 0 4px; text-wrap: balance; }}
h2 {{ font-size: 1.3rem; margin: 40px 0 8px; color: var(--accent); text-wrap: balance; }}
h2 .tag {{ display: inline-block; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--gold); font-weight: 700; margin-left: 10px; vertical-align: middle; }}
p {{ max-width: 70ch; margin: 8px 0; }}
.lead {{ color: var(--muted); }}
.q {{ font-family: ui-sans-serif, system-ui, sans-serif; font-weight: 600; background: var(--pick); border-left: 4px solid var(--accent); padding: 10px 14px; max-width: 70ch; margin: 14px 0; }}
.row {{ display: flex; flex-wrap: wrap; gap: 16px; margin: 12px 0; }}
figure {{ flex: 1 1 260px; min-width: 0; margin: 0; background: var(--card); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }}
figure.rec {{ border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent); }}
figure img {{ display: block; width: 100%; max-width: 100%; height: auto; }}
figcaption {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.86rem; line-height: 1.4; padding: 10px 12px 12px; border-top: 1px solid var(--line); }}
figcaption b {{ display: block; font-size: 0.95rem; margin-bottom: 2px; }}
table {{ border-collapse: collapse; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.9rem; font-variant-numeric: tabular-nums; margin: 10px 0; }}
td, th {{ text-align: left; padding: 5px 14px 5px 0; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-weight: 600; color: var(--muted); font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase; }}
.wrap {{ overflow-x: auto; }}
</style>
<main>
<h1>The drum runs past the 4 in base</h1>
<p class="lead">Brian, October 11: the center cylinder extends past the edge of the base on all 4 sides. True, and it dates from the October 8 revision, not the plate fix: the drum went from 3-1/8 to 3-9/16 in across so the deeper cavity would fit, and the drum's blend lands 9/32 in outside it. The blend's foot is now 2-3/64 in from the axis and the plate's edge 2 in, so at the middle of each side the blend runs 3/64 in off the edge, and the flange (the drum plus its blend, 4-3/32 in across) is 3/32 in wider than the plate. The September print had a smaller drum and the foot sat 1/8 in inside the edge.</p>

<h2>As built</h2>
{row("now")}
<p>Every option below keeps the screw pattern (holes 3-7/32 in apart), so the anchors already in the wall are reused. Print cost is estimated from the plate's extra plastic; the real slice follows the pick.</p>

<h2>A: base 4-1/2 in<span class="tag">recommended</span></h2>
<p>The plate grows 1/4 in each side. The blend's foot lands on 9/64 in of flat plate at the middle of each side, the flange sits 3/16 in inside the plate all round, and the corner rounds grow to about 5/8 in so each countersink stays centred in its corner. About 3/4 oz and 25 minutes more to print.</p>
{row("a45", "rec")}

<h2>B: base 4-1/4 in</h2>
<p>The plate grows 1/8 in each side: the least change that puts everything inside the edge. The foot lands right where the plate's edge round begins, with no flat plate outside it, and the flange sits 5/64 in inside the plate. Corner rounds about 1/2 in. About 3/8 oz and 12 minutes more.</p>
{row("d425")}

<h2>C: base stays 4 in, smaller blends</h2>
<p>The drum keeps its size but both blends shrink from 9/32 to 5/32 in, so the foot lands 1/64 in inside the plate's flat top. The flange is the drum plus its blend, so the face shrinks with it: 3-7/8 in across instead of 4-3/32, the lip the same, the T a touch smaller. The blends at both ends are tighter curves. No extra cost.</p>
{row("c4")}

<div class="wrap">
<table>
<tr><th></th><th>As built</th><th>A: 4-1/2 in</th><th>B: 4-1/4 in</th><th>C: 4 in, blends 5/32</th></tr>
<tr><td>Flat plate outside the foot, middle of a side</td><td>none, 3/64 in past the edge</td><td>9/64 in</td><td>none, on the edge round</td><td>1/64 in</td></tr>
<tr><td>Flange against the plate's side</td><td>3/32 in wider than the plate</td><td>3/16 in inside</td><td>5/64 in inside</td><td>1/16 in inside</td></tr>
<tr><td>Face across</td><td>4-3/32 in</td><td>4-3/32 in</td><td>4-3/32 in</td><td>3-7/8 in</td></tr>
<tr><td>Blends</td><td>9/32 in</td><td>9/32 in</td><td>9/32 in</td><td>5/32 in</td></tr>
<tr><td>Extra plastic and time</td><td></td><td>about 3/4 oz, 25 min</td><td>about 3/8 oz, 12 min</td><td>none</td></tr>
</table>
</div>

<div class="q">Which base: A, B or C? The face is being made solid like the base in any case, and that goes into the same print file once the base is picked.</div>
<p><b>Picked: A, the 4-1/2 in base</b> (Brian, October 11). Built, sliced and checked in the print file.</p>
</main>
"""

with open(f"{PROJECT}/options-2026-10-11.html", "w") as f:
    f.write(page)
print("wrote options-2026-10-11.html", round(len(page) / 1024), "KB")
