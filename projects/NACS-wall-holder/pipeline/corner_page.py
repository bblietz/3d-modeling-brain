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
<p class="sub">NACS wall holder, the print of September 19, dropped on the floor on October 10. Both pictures come from the real print file (the revision uses the same plate, pads and slicer recipe), not from a sketch.</p>

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
<strong>One question before I draw the fix: where did it break?</strong>
<ol>
<li>A crescent outside the screw hole came off and the hole is half gone (the break ran through the hole).</li>
<li>The whole corner, hole included, came off along the drum (the break ran around the drum's blend).</li>
</ol>
A photo of the break face would settle it, and show whether the core looks hollow.
</div>

<h2>Where this points</h2>
<ul>
<li><span class="gold">Make the plate solid.</span> A 100% infill modifier over the whole plate, no CAD change. Roughly 40 g and 25 to 30 min more on the revision print, to be confirmed by a slice. This is the cheapest change and fixes the hollow core in every corner.</li>
<li><span class="gold">Thicken the plate.</span> 1/4 in instead of 3/16 in gives the countersink a full plate under it and moves the drum blend off the countersink's edge. The drum and everything on it move out 1/16 in, so the CAD exports, the docking check and the slice rerun.</li>
<li>Both together is the belt and braces version. Either way the revision stays unprinted until you pick.</li>
</ul>
</main>
"""

with open(f"{PROJECT}/corner-break-2026-10-10.html", "w") as f:
    f.write(page)
print("wrote corner-break-2026-10-10.html", round(len(page) / 1024), "KB")
