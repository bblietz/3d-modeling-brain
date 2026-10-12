#!/usr/bin/env python
"""Writes corner-break-2026-10-10.html: the evidence page for the dropped holder's broken plate corner.
Needs images/corner-layer.png and images/corner-section.png from corner_check.py."""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)


def img(name):
    with open(f"{PROJECT}/images/{name}", "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


import json
hs = json.load(open(f"{PROJECT}/holder-slice.json"))
sb = hs["solid_base"]
SPARSE = ("drum above", "under flange")
solid_min = min(v for k, v in sb.items() if k not in SPARSE) * 100
solid_max = max(v for k, v in sb.items() if k not in SPARSE) * 100
above = sb["drum above"] * 100
under = sb.get("under flange", 0) * 100
face = {k: sb.get(k, 0) * 100 for k in ("flange", "lip", "flange blend")}
hours, mins, grams = hs["minutes"] // 60, hs["minutes"] % 60, hs["grams"]

page = f"""<title>Plate Corner Break</title>
<style>
/* layout: one reading column, two full-width figures, a facts table, one question box; same palette as the revision's options page */
:root {{ --bg: #f6f4ee; --fg: #1f2a2c; --muted: #5d6b6e; --accent: #1f7a7c; --gold: #b8860b; --line: #d9d4c7; --card: #ffffff; --pick: #e6f1ef; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #16191a; --fg: #e8e4da; --muted: #a2aba9; --accent: #5fc1be; --gold: #d8a93a; --line: #333a3b; --card: #1f2425; --pick: #1d3334; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --bg: #16191a; --fg: #e8e4da; --muted: #a2aba9; --accent: #5fc1be; --gold: #d8a93a; --line: #333a3b; --card: #1f2425; --pick: #1d3334; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font-family: Georgia, "Times New Roman", serif; font-size: 1.02rem; line-height: 1.5; padding-block: 28px 48px; padding-inline: 16px; }}
main {{ max-width: 1120px; margin: 0 auto; }}
h1 {{ font-size: 1.9rem; line-height: 1.15; margin: 0 0 6px; text-wrap: balance; }}
h2 {{ font-size: 1.25rem; margin: 30px 0 8px; text-wrap: balance; }}
p {{ max-width: 68ch; margin: 8px 0; }}
.sub {{ font-family: ui-sans-serif, system-ui, sans-serif; color: var(--muted); font-size: 0.92rem; }}
figure {{ margin: 14px 0; background: var(--card); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }}
figure img {{ display: block; width: 100%; height: auto; }}
figcaption {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.88rem; line-height: 1.45; padding: 10px 12px 12px; border-top: 1px solid var(--line); max-width: none; }}
table {{ border-collapse: collapse; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.92rem; font-variant-numeric: tabular-nums; margin: 10px 0; }}
td, th {{ text-align: left; padding: 5px 14px 5px 0; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-weight: 600; color: var(--muted); font-size: 0.8rem; letter-spacing: 0.04em; text-transform: uppercase; }}
.wrap {{ overflow-x: auto; }}
.q {{ font-family: ui-sans-serif, system-ui, sans-serif; background: var(--pick); border-left: 4px solid var(--accent); padding: 12px 16px; max-width: 68ch; margin: 16px 0; }}
.q strong {{ display: block; margin-bottom: 6px; }}
.q ol {{ margin: 6px 0 0; padding-left: 22px; }}
.q li {{ margin: 4px 0; }}
ul {{ max-width: 68ch; padding-left: 22px; }}
li {{ margin: 5px 0; }}
.gold {{ color: var(--gold); }}
</style>
<main>
<h1>Why the plate corner broke off</h1>
<p class="sub">NACS wall holder, the print of September 19, dropped on the floor on October 10. The first two pictures come from the print file as it was (the revision used the same plate, pads and slicer recipe), not from a sketch; the last two from the fixed file.</p>

<p>The base plate is 3/16 in thick, but it is not solid. The slicer prints it as two skins of three layers (about 1/32 in each) over a 20% gyroid core, with three walls around the edge. The only solid plastic is the pad around each screw, 1/2 in in radius. Everything else inside the plate is open lattice, so a corner that hits the floor is a thin hollow flap with a half-depth countersink through it.</p>

<figure>
<img src="{img('corner-layer.png')}" alt="Toolpaths of the layer at mid plate height: dense gyroid inside the four screw pads, open 20% gyroid everywhere else, three wall loops at the edge">
<figcaption>The layer at mid plate height, straight from the sliced G-code. Dense orange discs are the screw pads (100% gyroid, dashed circles are the pad modifier). The rest of the plate is 20% gyroid: lines about 1/8 in apart with air between. The dotted red circle is where the drum's blend meets the plate, so each corner is the flap outside that circle. Right: the upper right corner. Between the pad and where the blend reaches the edge, the flap is three walls, two skins and air.</figcaption>
</figure>

<figure>
<img src="{img('corner-section.png')}" alt="True section through a screw hole along the plate's diagonal: 5 mm plate, countersink taking half its thickness, drum blend landing at the countersink's edge, solid pad band">
<figcaption>A true section of holder.stl through a screw hole, along the plate's diagonal. The countersink takes half the plate's thickness, and the drum's blend lands right at the countersink's edge, so along the diagonal there is no flat plate at all between drum and screw. Outside the shaded pad band the 3.2 mm between the skins is the open lattice from the picture above.</figcaption>
</figure>

<h2>The numbers</h2>
<div class="wrap">
<table>
<tr><th>Feature</th><th>As printed</th><th>Why it matters</th></tr>
<tr><td>Plate thickness</td><td>3/16 in</td><td>Two 1/32 in skins carry all the bending; the core only spaces them</td></tr>
<tr><td>Core between the skins</td><td>20% gyroid, 1/8 in thick</td><td>Shears and crushes under a corner hit; a break face here looks hollow</td></tr>
<tr><td>Walls at the plate edge</td><td>3 loops, about 5/64 in</td><td>The only solid plastic along the edge outside the pads</td></tr>
<tr><td>Solid pad around each screw</td><td>1/2 in radius</td><td>Protects the ring around the hole, not the flap's root along the edge (about 7/8 in of edge per corner is unprotected)</td></tr>
<tr><td>Countersink</td><td>3/32 in deep, half the plate</td><td>Halves the section at the hole, and the drum blend lands on its edge</td></tr>
<tr><td>Material and layers</td><td>PETG Basic, 0.30 mm layers, plate down</td><td>Layers lie in the plate's plane; a drop bends the corner across them, which the skins resist well but the lattice does not</td></tr>
</table>
</div>

<h2>What that means</h2>
<p>A drop onto a corner puts the whole holder's momentum into one flap of plate. The two thin skins have to take the bending on their own, with a half-depth countersink and the drum's blend both landing on the same line. Once the skins crack, the lattice core has nothing to offer, so the corner comes away clean. The screw pads kept the ring around the hole solid, and nothing else.</p>

<div class="q">
<strong>Where it broke, and the fix</strong>
Brian: it broke along the contour of the main cylinder, so the flap came off at its root around the drum's blend. His pick: both fixes, a solid plate and a thicker one.
</div>

<h2>After the fix</h2>
<p>The plate is now 1/4 in thick, and the print file makes the whole plate solid, plus a ring up through the drum's blend, so the flap's root is solid plastic from the wall to above the blend. Same slicer recipe otherwise. Both pictures below come from the new print file and the new STL.</p>

<figure>
<img src="{img('corner-layer-fixed.png')}" alt="Toolpaths of the fixed plate's mid layer: solid infill across the whole plate, walls at the edge">
<figcaption>The fixed plate's layer at mid height, from the sliced G-code. Solid everywhere between the walls; the dashed circles only mark where the old pads were. Measured in the G-code: {solid_min:.0f} to {solid_max:.0f}% plastic in the plate and blend windows, {above:.0f}% in the drum's core above the blend, which stays sparse.</figcaption>
</figure>

<figure>
<img src="{img('corner-section-fixed.png')}" alt="True section of the fixed holder through a screw hole: 1/4 in plate, solid through, blend ring solid">
<figcaption>The same section through a screw hole on the new STL. The countersink now takes 2.5 mm of a 6.35 mm plate instead of half of it, and the drum blend lands on 3.85 mm of solid plate instead of 2.5 mm of skins and lattice.</figcaption>
</figure>

<h2>The ring Studio shows</h2>
<p>Brian, October 11: the added ring is squared off, it should round into the wall plate the way the drum rounds into the flange. That ring is not plastic. It is the slicer's modifier, the region told to print solid, and Bambu Studio draws a modifier translucent over the part. The first version was a squared-off ring that poked out of the blend, and it showed through the screw holes and on the plate's top too. The printed part was always the body on the right, blend and all. The modifier now follows the blend's arc from 0.6 mm inside it, stops a layer under the plate's top, and stays clear of the screw holes, so it sits wholly inside the body and Studio shows the part as it prints.</p>

<figure>
<img src="{img('modifier-ring.png')}" alt="Before and after: the modifier drawn translucent over the body as Studio shows it, and true sections along the plate's diagonal with the modifier shaded">
<figcaption>Top: the body with the modifier drawn translucent, the way Studio draws it; before, the squared-off collar and the tint through the holes; after, only the part. Bottom: true sections along the plate's diagonal with the modifier shaded. Before, 10.4 cm3 of the modifier sat outside the body; after, none. Re-sliced and measured again in the G-code: {solid_min:.0f} to {solid_max:.0f}% plastic in the plate and blend windows, including a new window at the blend's foot where the arc meets the walls, and {above:.0f}% in the drum's core above the blend.</figcaption>
</figure>

<h2>The face, solid too</h2>
<p>Brian, October 11: the face should also be solid infill, like the base; it will also break if dropped. A second modifier now makes the flange, the lip and the blend behind the flange print solid. The model builds it itself, so it follows the lip's rounded edges, keeps 0.6 mm inside every face, stays 0.6 mm under the floors of the T, the wordmark and the frame line, and clears the mouth and its rounded rim. None of it lies outside the body.</p>

<figure>
<img src="{img('modifier-face.png')}" alt="The face modifier drawn translucent over the body as Studio shows it, and a true section through the drum axis and the lip with the modifier shaded">
<figcaption>Top: the body with the face modifier drawn translucent, the way Studio draws it: nothing of it shows. Bottom: a true section through the drum axis and the lip's centreline, the modifier shaded. The notches along the top are the recesses for the T's stem, the frame line and the wordmark, each with the modifier held 0.6 mm under its floor; the modifier runs down the blend behind the flange on both sides. Measured in the G-code: {face['flange']:.0f}% plastic in the flange, {face['lip']:.0f}% in the lip, {face['flange blend']:.0f}% in the blend behind the flange, and {under:.0f}% in the drum's core just under the flange, which stays sparse.</figcaption>
</figure>

<h2>What it costs</h2>
<div class="wrap">
<table>
<tr><th></th><th>Before</th><th>Plate fix, October 10</th><th>Plus the solid face, October 11</th><th>Plus the 4-1/2 in base, October 11</th></tr>
<tr><td>Plate</td><td>4 in, 3/16 in thick, two skins over 20% lattice</td><td>4 in, 1/4 in, solid through, blend ring solid</td><td>same</td><td>4-1/2 in, the blend on flat plate, flange inside the edge</td></tr>
<tr><td>Face</td><td>two skins over 20% lattice</td><td>same</td><td>flange, lip and blend solid</td><td>same</td></tr>
<tr><td>Print time</td><td>8 h 47 min</td><td>9 h 22 min</td><td>10 h 11 min</td><td>{hours} h {mins:02d} min</td></tr>
<tr><td>Filament</td><td>442 g</td><td>498 g</td><td>575 g</td><td>{grams:.0f} g</td></tr>
<tr><td>Holder off the wall</td><td>105.4 mm</td><td>106.75 mm (the flange and lip move out with the plate's front; the wand's place is unchanged)</td><td>106.75 mm</td><td>106.75 mm</td></tr>
</table>
</div>
<p>Docking and hold were rerun on the new model and are unchanged. The file is <code>holder-print.3mf</code>, not yet printed. The drum's foot and flange ran past the 4 in plate's sides; Brian picked the 4-1/2 in plate from the options page, and the numbers above are from that file.</p>
</main>
"""

with open(f"{PROJECT}/corner-break-2026-10-10.html", "w") as f:
    f.write(page)
print("wrote corner-break-2026-10-10.html", round(len(page) / 1024), "KB")
