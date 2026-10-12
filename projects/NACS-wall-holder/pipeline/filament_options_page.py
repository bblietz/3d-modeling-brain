#!/usr/bin/env python
"""Builds options-2026-10-12.html, the filament budget for the holder (Brian, 2026-10-12: keep the body PETG under 500 g so two
holders print from one 1000 g spool), from the sliced variants in filament-variants.json (pipeline/filament_budget.py) and the
figures in images/filament-2026-10-12/ (pipeline/filament_figures.py). Published as the "Holder Filament Budget" artifact."""
import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
IMG = f"{PROJECT}/images/filament-2026-10-12"
R = json.load(open(f"{PROJECT}/filament-variants.json"))
NOW = R["base"]


def img(name):
    with open(f"{IMG}/{name}.png", "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def fig(name, title, text, cls=""):
    return f'<figure class="{cls}"><img src="{img(name)}" alt="{title}"><figcaption><b>{title}</b>{text}</figcaption></figure>'


def body_g(v):
    return R[v]["slice_info_g"]["1"]


def hm(v):
    m = R[v]["minutes"]
    return f"{m // 60} h {m % 60:02d} min"


def saves(v):
    return body_g(NOW["name"]) - body_g(v)


def reg(v, k):
    return R[v]["regions"].get(k, R[v]["regions"].get("drum core, 20%" if k == "drum core" else k, 0.0))


def option_row(v, letter):
    b = body_g(v)
    return (f"<tr><td><b>{letter}</b></td><td>{b:.0f} g</td><td>{sum(R[v]['slice_info_g'].values()):.0f} g</td><td>{hm(v)}</td>"
            f"<td>{2 * b:.0f} g</td><td>{1000 - 2 * b:.0f} g</td></tr>")


def lever(v, what, verdict):
    return f"<tr><td>{what}</td><td>{body_g(v):.0f} g ({body_g(v) - body_g('base'):+.0f})</td><td>{hm(v)}</td><td>{verdict}</td></tr>"


part = sum(reg("base", k) for k in ("solid base", "solid face", "drum core", "walls", "shells and solid layers", "other"))
sup = sum(reg("base", k) for k in ("support: under the lip", "support: under the flange ring", "support: in the cavity", "support: elsewhere"))
tower = reg("base", "prime tower")

page = f"""<title>Holder Filament Budget</title>
<style>
/* the same reading column and palette as the base options page: the holder's teal, the recess gold */
:root {{ --bg: #f6f4ee; --fg: #1f2a2c; --muted: #5d6b6e; --accent: #1f7a7c; --gold: #b8860b; --line: #d9d4c7; --card: #ffffff; --pick: #e6f1ef; --warn: #b4452a; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #15191a; --fg: #e8e6df; --muted: #a2adaf; --accent: #5cc3c4; --gold: #e0b040; --line: #2e3637; --card: #1d2324; --pick: #1d2f2e; --warn: #e8835f; color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg: #15191a; --fg: #e8e6df; --muted: #a2adaf; --accent: #5cc3c4; --gold: #e0b040; --line: #2e3637; --card: #1d2324; --pick: #1d2f2e; --warn: #e8835f; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 16px/1.5 Georgia, 'Times New Roman', serif; }}
main {{ max-width: 1100px; margin: 0 auto; padding-block: 24px 64px; padding-inline: 16px; }}
h1 {{ font-size: 1.9rem; line-height: 1.15; margin: 0 0 4px; text-wrap: balance; }}
h2 {{ font-size: 1.3rem; margin: 40px 0 8px; color: var(--accent); text-wrap: balance; }}
h2 .tag {{ display: inline-block; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--gold); font-weight: 700; margin-left: 10px; vertical-align: middle; }}
p, li {{ max-width: 70ch; }}
p {{ margin: 8px 0; }}
.lead {{ color: var(--muted); }}
.q {{ font-family: ui-sans-serif, system-ui, sans-serif; font-weight: 600; background: var(--pick); border-left: 4px solid var(--accent); padding: 10px 14px; max-width: 70ch; margin: 14px 0; }}
.row {{ display: flex; flex-wrap: wrap; gap: 16px; margin: 12px 0; }}
figure {{ flex: 1 1 300px; min-width: 0; margin: 0; background: var(--card); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }}
figure.wide {{ flex-basis: 100%; }}
figure.rec {{ border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent); }}
figure img {{ display: block; width: 100%; max-width: 100%; height: auto; }}
figcaption {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.86rem; line-height: 1.4; padding: 10px 12px 12px; border-top: 1px solid var(--line); }}
figcaption b {{ display: block; font-size: 0.95rem; margin-bottom: 2px; }}
table {{ border-collapse: collapse; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.9rem; font-variant-numeric: tabular-nums; margin: 10px 0; }}
td, th {{ text-align: left; padding: 5px 14px 5px 0; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-weight: 600; color: var(--muted); font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase; }}
.wrap {{ overflow-x: auto; }}
.no {{ color: var(--warn); }}
</style>
<main>
<h1>Under 500 g: two holders from one spool</h1>
<p class="lead">Brian, October 12: keep the filament below 500 g so two holders print from one 1000 g spool. The October 11 file takes {body_g('base'):.0f} g of body PETG ({sum(NOW['slice_info_g'].values()):.0f} g with the support interface and the inlay colour, which come off other spools). Every number on this page is from a real slice of the print file with the X2D's own settings, read back from its G-code.</p>

<h2>Where the {body_g('base'):.0f} g goes</h2>
<p>The holder itself is {part:.0f} g: the solid base and face you asked for ({reg('base', 'solid base'):.0f} and {reg('base', 'solid face'):.0f} g), the drum's 20% gyroid core ({reg('base', 'drum core'):.0f} g), three walls everywhere ({reg('base', 'walls'):.0f} g) and the solid layers under the skins ({reg('base', 'shells and solid layers'):.0f} g). The other {sup + tower:.0f} g, a third of the spool, is thrown away after the print: {sup:.0f} g of tree and block supports in body PETG and the {tower:.0f} g prime tower the two nozzles swap on. The lip is the big one. Printed plate down, it is a flat shelf 1-1/2 in deep and 4 in across hanging 3-7/8 in above the bed, and the slicer stands a dense comb block under the whole of it ({reg('base', 'support: under the lip'):.0f} g). The cove under the flange gets a ring of trees ({reg('base', 'support: under the flange ring'):.0f} g) and the cavity's roof its own ({reg('base', 'support: in the cavity'):.0f} g).</p>
<div class="row">
{fig("section-now", "The print cut down its middle", "Every toolpath within half a millimetre of the centre plane, coloured by where the plastic goes. The lip is at the right, the orange column under it is its support block, the dark blue is the solid base and face.", "wide")}
</div>
<div class="row">
{fig("layer-now", "Under the lip, halfway up", "One layer at 50 mm from above: the comb block under the lip (lines 2.5 mm apart inside a two-wall perimeter) and the two-wall tree trunks beside the drum.")}
{fig("layer-now-top", "Just under the lip", "The block's top: dense support lines, then two layers of support interface in the second nozzle's filament, then the lip prints on that.")}
</div>

<h2>The levers, each sliced</h2>
<p>Everything tried, one change at a time against the October 11 file. The solid base and face stay as they are in every row, and so does the part's shape.</p>
<div class="wrap">
<table>
<tr><th>Change</th><th>Body PETG (and the change)</th><th>Print time</th><th>Verdict</th></tr>
{lever("spacing5", "Comb under the lip at 5 mm instead of 2.5 mm", "Yes. Same block, half the comb; the interface spans 5 mm easily.")}
{lever("hyb_w1", "Tree branches with one wall instead of two", "Yes. The ring and cavity trees get one 0.62 mm wall, what a 0.4 nozzle prints anyway.")}
{lever("inf15", "Drum core 15% gyroid instead of 20%", "Yes if you accept it: the only lever that touches the part. The skins and the solid ends carry a drop, the core ties them.")}
{lever("inf10", "Drum core 10% gyroid", "Same, further.")}
{lever("walls2", "Two walls instead of three", "<span class='no'>No.</span> Little gain, and the drum's skin is the drop protection.")}
{lever("tree_slim", "Slim trees everywhere", "<span class='no'>Not alone.</span> The lip block becomes a few thin columns 3-5/8 in tall, below.")}
{lever("tree_strong", "Strong trees everywhere", "<span class='no'>No.</span> Heavier under the ring than the hybrid.")}
{lever("hyb_hollow", "Hollow block under the lip", "<span class='no'>No.</span> A two-wall box, then dense lines bridging 1-5/16 in just under the lip.")}
{lever("hyb_lightning", "Lightning block under the lip", "<span class='no'>No.</span> Hollow for most of its height, same bridge at the top.")}
{lever("tower12", "Prime tower 12 mm wide instead of 35", "<span class='no'>Nothing.</span> The tower's size is set by the purge, not the width. Skipping its sparse layers would save about 12 g, but the X2D refuses it unless the tower sits in front of the whole part, and this part fills the bed's depth.")}
{lever("iface1", "One interface layer instead of two", "<span class='no'>Nothing.</span> The interface is the other spool anyway.")}
</table>
</div>
<div class="row">
{fig("bars", "Every slice side by side", "Body PETG by region. The red line is 500 g.", "wide")}
</div>
<div class="row">
{fig("layer-spacing5", "The 5 mm comb", "The same block under the lip with the comb lines 5 mm apart: 26 g less, and the interface lines above it only have to span 5 mm.")}
{fig("layer-strong_w1", "Strong trees, one wall", "What the lip would stand on with tree supports instead of the block: single-wall shells 1-1/4 to 2 in across and 3-5/8 in tall. Not for this lip.")}
{fig("layer-C", "Slim trees, one wall", "The slim style: a handful of 10 mm columns under the lip at this height, branching out only near the top.")}
{fig("layer-hyb_hollow-top", "The hollow block's top", "The layer just under the lip when the block is hollow: dense lines laid across a 1-5/16 in void. That is a bridge, not a support.")}
</div>

<h2>The options</h2>
<p>A and B keep Bambu's recommended hybrid supports for this PETG and interface pairing, with the two cheap support changes and a lighter core. C is the lightest file and the one I would not print: slim trees under a shelf 3-7/8 in up.</p>
<div class="wrap">
<table>
<tr><th>Option</th><th>Body PETG</th><th>All filament</th><th>Print time</th><th>Two holders</th><th>Left on a 1000 g spool</th></tr>
<tr><td><b>Now</b></td><td>{body_g('base'):.0f} g</td><td>{sum(NOW['slice_info_g'].values()):.0f} g</td><td>{hm('base')}</td><td>{2 * body_g('base'):.0f} g</td><td class="no">{1000 - 2 * body_g('base'):.0f} g</td></tr>
{option_row("hyb_sp5_w1_inf15", "A: comb at 5 mm, one-wall trees, 15% core")}
{option_row("hyb_sp5_w1_inf10", "B: as A with a 10% core")}
{option_row("slimw1_inf15", "C: slim one-wall trees, 15% core")}
</table>
</div>

<h2>A: the two support changes and a 15% core<span class="tag">recommended</span></h2>
<p>The part is unchanged except the drum's core, 15% gyroid instead of 20%. The lip's block keeps its two-wall perimeter and dense top with the comb at 5 mm, the trees get one wall. {body_g('hyb_sp5_w1_inf15'):.0f} g of body PETG, {hm('hyb_sp5_w1_inf15')}. Two holders take {2 * body_g('hyb_sp5_w1_inf15'):.0f} g: it fits, with {1000 - 2 * body_g('hyb_sp5_w1_inf15'):.0f} g to spare for the purge line at the start of each print and the spool's own variance. If you want more cushion than that, B.</p>
<div class="row">
{fig("section-A", "A, cut down the middle", "The block under the lip is lighter, the ring trees thinner, the core a little more open.", "wide rec")}
</div>
<div class="row">
{fig("layer-hyb_sp5_w1", "A, halfway up", "The 5 mm comb and the single-wall tree trunks.", "rec")}
{fig("layer-A-top", "A, just under the lip", "The block's dense top is the same as now: the lip prints on the same interface.", "rec")}
</div>

<h2>B: the same with a 10% core</h2>
<p>{body_g('hyb_sp5_w1_inf10'):.0f} g and {hm('hyb_sp5_w1_inf10')}: {1000 - 2 * body_g('hyb_sp5_w1_inf10'):.0f} g left after two holders. The drum's core at 10% is still a gyroid every 6 mm or so between the cavity's walls and the outer skin; the plate, the face and the skins are what take a drop.</p>
<div class="row">
{fig("section-B", "B, cut down the middle", "Same supports as A, the core opened further.", "wide")}
</div>

<h2>C: slim trees, the lightest file</h2>
<p>{body_g('slimw1_inf15'):.0f} g and {hm('slimw1_inf15')}, the lip standing on single-wall slim trees instead of the block. Bambu rates slim trees for small overhangs; this one is a 4 in shelf 3-7/8 in up, in PETG. If a column wobbles or the nozzle catches a branch at hour eight, the lip's underside fails on the spot. Shown because it is the lightest; not recommended.</p>
<div class="row">
{fig("section-C", "C, cut down the middle", "The slim trees under the lip and the ring.", "wide")}
</div>

<h2>Not done: the part's shape</h2>
<p>The cove under the flange is what the ring of trees holds up, {reg('base', 'support: under the flange ring'):.0f} g of it. A flange underside that climbs at 45 degrees instead of curving to flat would print with no ring at all, but it changes the roll from the drum into the face that you asked the base to match. Left alone unless you want it.</p>

<div class="q">Which one: A, B or C?</div>
</main>
"""

with open(f"{PROJECT}/options-2026-10-12.html", "w") as f:
    f.write(page)
print("wrote options-2026-10-12.html", round(len(page) / 1024), "KB")
