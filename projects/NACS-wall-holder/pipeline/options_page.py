"""Build the options page for Brian's 2026-10-08 revision (deeper drum, taller top lip, deeper cavity) from the
option renders in images/options-2026-10-08/ (made by pipeline/render_options.sh). Writes options-2026-10-08.html
next to holder.scad; published as the "NACS Holder Revision" artifact.

    .venv/bin/python projects/NACS-wall-holder/pipeline/options_page.py
"""
import base64
import io
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
IMG = f"{PROJECT}/images/options-2026-10-08"


def img(name, box=None):
    im = Image.open(f"{IMG}/{name}.png")
    if box:
        im = im.crop(box)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


FRONT = (390, 240, 760, 640)     # the same crop on every front view, so the lips compare at one scale
SIDE = (300, 200, 800, 720)
PLATE = (330, 150, 770, 640)
FACE = (260, 40, 840, 820)       # the face close-ups


def fig(name, box, title, text, cls="", tag=""):
    t = f'<span class="tag">{tag}</span>' if tag else ""
    return f'<figure class="{cls}"><img src="{img(name, box)}" alt="{title}"><figcaption>{t}<b>{title}</b>{text}</figcaption></figure>'


html = f"""<title>NACS Holder Revision</title>
<style>
/* layout: one reading column, figures in rows that stack on a phone; the holder's own teal and the recess gold as the palette */
:root {{ --bg: #f6f4ee; --fg: #1f2a2c; --muted: #5d6b6e; --accent: #1f7a7c; --gold: #b8860b; --line: #d9d4c7; --card: #ffffff; --pick: #e6f1ef; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #15191a; --fg: #e8e6df; --muted: #a2adaf; --accent: #5cc3c4; --gold: #e0b040; --line: #2e3637; --card: #1d2324; --pick: #1d2f2e; color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg: #15191a; --fg: #e8e6df; --muted: #a2adaf; --accent: #5cc3c4; --gold: #e0b040; --line: #2e3637; --card: #1d2324; --pick: #1d2f2e; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 16px/1.5 Georgia, 'Times New Roman', serif; }}
main {{ max-width: 980px; margin: 0 auto; padding-block: 24px 64px; padding-inline: 16px; }}
h1 {{ font-size: 1.9rem; line-height: 1.15; margin: 0 0 4px; text-wrap: balance; }}
h2 {{ font-size: 1.3rem; margin: 40px 0 8px; color: var(--accent); text-wrap: balance; }}
h3 {{ font-size: 1.05rem; margin: 20px 0 4px; }}
p {{ max-width: 68ch; margin: 8px 0; }}
.lead {{ color: var(--muted); }}
.done {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.9rem; color: var(--muted); }}
.q {{ font-family: ui-sans-serif, system-ui, sans-serif; font-weight: 600; background: var(--pick); border-left: 4px solid var(--accent); padding: 10px 14px; max-width: 68ch; margin: 14px 0; }}
.row {{ display: flex; flex-wrap: wrap; gap: 16px; margin: 12px 0; }}
figure {{ flex: 1 1 200px; min-width: 0; margin: 0; background: var(--card); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }}
figure.rec {{ border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent); }}
figure.wide {{ flex-basis: 300px; }}
figure img {{ display: block; width: 100%; max-width: 100%; height: auto; }}
figcaption {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.86rem; line-height: 1.4; padding: 10px 12px 12px; border-top: 1px solid var(--line); }}
figcaption b {{ display: block; font-size: 0.95rem; margin-bottom: 2px; }}
.tag {{ display: inline-block; font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin-right: 6px; }}
table {{ border-collapse: collapse; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.9rem; font-variant-numeric: tabular-nums; margin: 10px 0; }}
td, th {{ padding: 5px 12px 5px 0; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
th {{ color: var(--muted); font-weight: 600; }}
ol, ul {{ max-width: 68ch; padding-left: 20px; }}
</style>
<main>
<h1>NACS wall holder: the October revision</h1>
<p class="lead">Rendered from <code>holder.scad</code> so you can pick against the real model. Everything that was validated stays as it is: the nose cavity and cleat, the grip-up docking, the 45&#176; down and 15&#176; out wand angles, the 4 in base and its screw pattern.</p>

<h2>1. Drum 1 in deeper</h2>
<p class="done">Settled: drum 75 mm (3 in) becomes 100 mm (4 in), the holder stands 105 mm (4-1/8 in) off the wall, the wand stays at the far end. The straight part of the drum, where the cable loops sit, goes from 47 mm to 72 mm: room for five loops of the 14.5 mm cable side by side (they take 73 mm), up from three.</p>
<div class="row">
{fig('drum-right', SIDE, 'From the right', 'Wall at the right, 100 mm drum, the lip rising from the far end. The wand ghost hangs where it does today relative to the flange.')}
{fig('drum-iso', SIDE, 'Three-quarter view', 'The cavity, cleat and mouth are the validated ones, moved out 1 in with the flange.')}
</div>

<h2>2. The lip: a crest</h2>
<p class="done">Settled: full width (104 mm), 1-1/2 in (38 mm) above today's flange top, 8 mm thick, every edge rounded 1/16 in. The outline is the shield's sides (tapering to 84 mm at the top, tangent to the round flange) under the arch's crowned top (10 mm rise), with 1/2 in corners.</p>
<div class="row">
{fig('crest-front', FRONT, 'Crest, from the front', 'Shield sides, arched top. No emblem shown here.')}
{fig('crest-iso', SIDE, 'Crest, three-quarter view', 'The lip stands in the flange plane, 4 in off the wall.')}
{fig('crest-frame-front', FRONT, 'Optional: frame line', 'A 2.5 mm recessed line, 1 mm deep, following the whole face 6 mm in from the edge, round the flange and up over the crest.')}
</div>
<p class="q">Frame line: yes or no?</p>

<h2>3. The emblem: something generic in place of the T</h2>
<p>All four are recessed 1 mm into the flange face where the T was, 59 mm tall, centred on the drum axis. None is a brand mark.</p>
<div class="row">
{fig('emblem-bolt', FACE, 'Lightning bolt', 'The plain charge symbol. Crisp, prints clean.')}
{fig('emblem-plug', FACE, 'Plug', 'A two-prong plug with its cord: the universal charging pictogram.')}
{fig('emblem-nacs', FACE, 'The connector&#39;s own face', 'The NACS plug face: its outline as a band, its pin holes as discs, traced from the connector&#39;s official CAD (the shape the holder is built around).', tag='my pick')}
{fig('emblem-ev', FACE, 'EV', 'The letters EV in a bold sans face.')}
</div>
<p class="q">Pick an emblem: bolt, plug, connector face, EV, or none.</p>

<h2>4. Reaching the top two screws</h2>
<p>The full-width lip sits 4 in in front of the plate and covers the top two screw holes, so a driver cannot go straight at them. Two ways round it.</p>
<div class="row">
{fig('access-keyhole-front', PLATE, 'Keyhole slots (lip hidden to show them)', 'The top two holes become slots open at the plate&#39;s top edge, countersink and all. Mounting: back the top two screws out until the head stands about 3/16 in off the wall, slide the holder down onto them, then drive the bottom two screws home. Nothing shows from the front; the existing wall screws stay where they are.', cls='rec', tag='recommended')}
{fig('access-keyhole-corner', None, 'The slot, close up', 'Open at the plate&#39;s top edge; the screw head seats in the countersink groove and carries the hanging load in shear, the bottom screws clamp the plate flat.')}
{fig('access-holes-front', FRONT, 'Driver holes through the lip', 'Two 12 mm holes in the lip in line with the top screws. All four screws drive normally, but through a hole 4 in in front, so it takes a long bit or an extension, and the holes stay visible.')}
</div>
<p class="q">Keyhole slots, or driver holes?</p>

<h2>5. The wand cavity: deeper, but the drum sets the limit</h2>
<p>The cavity crosses the 80 mm drum at 45&#176;, and its tip end is already 15 mm past the drum's centre. Each 1/4 in of depth takes about 5.5 mm off the wall on the far side. The sections below are cut along the wand through the drum, looking at the cut face; the ghost is the connector hanging on the cleat.</p>
<div class="row">
{fig('depth-now', None, 'Today: cleat wall 1-1/4 in from the opening', '11.4 mm of wall left between the cavity&#39;s far corner and the drum&#39;s surface.', cls='wide')}
{fig('depth-quarter', None, '1/4 in deeper: cleat wall 1-1/2 in from the opening', '5.9 mm of wall left on the far side (4 to 5 perimeters with the 0.6 nozzle). The opening moves 1/4 in out along the grip and gets 0.6 mm wider per side from the flare.', cls='rec wide', tag='recommended')}
</div>
<table>
<tr><th>Cavity deeper by</th><th>Cleat wall from the opening</th><th>Wall left at the far side</th><th>What it needs</th></tr>
<tr><td>0 (today)</td><td>1-1/4 in</td><td>11.4 mm</td><td>nothing</td></tr>
<tr><td>1/4 in</td><td>1-1/2 in</td><td>5.9 mm</td><td>fits the 80 mm drum</td></tr>
<tr><td>1/2 in</td><td>1-3/4 in</td><td>0.1 mm</td><td>drum 90 mm (base stays 4 in, blends 7 mm so the screw heads stay clear of the flange)</td></tr>
<tr><td>3/4 in</td><td>2 in</td><td>none</td><td>drum 102 mm: wider than the 4 in base, so no</td></tr>
</table>
<p class="q">How much deeper: 1/4 in on the 80 mm drum, or 1/2 in with the drum grown to 90 mm?</p>

<h2>What the print pays for the lip</h2>
<ul>
<li>Print orientation stays plate down, emblem up. The lip is then a horizontal slab 97 mm above the bed, so it prints on tree supports (support interface on the second nozzle, as the flange ring does today). I will quote the time and grams from a real slice once the picks are in.</li>
<li>Height 105 mm, footprint 104 x 142 mm with the lip: fits the bed with room for the prime tower.</li>
</ul>
</main>
"""

out = f"{PROJECT}/options-2026-10-08.html"
open(out, "w").write(html)
print(out, len(html) // 1024, "KB")
