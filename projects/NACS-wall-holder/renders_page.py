#!/usr/bin/env python3
"""Write plan.html: the OpenSCAD renders of holder.scad with captions and the design constants.

    ./render.sh && python3 renders_page.py
"""
import base64
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SCAD = open(os.path.join(HERE, "holder.scad")).read()


def const(name):
    return float(re.search(rf"(?:^|;)\s*{name}\s*=\s*([-0-9.]+)", SCAD, re.M).group(1))


def img(name):
    data = base64.b64encode(open(os.path.join(HERE, "images", "scad", name + ".png"), "rb").read()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{name}">'


plate_w, plate_t, drum_r, drum_l = const("plate_w"), const("plate_t"), const("drum_r"), const("drum_l")
flange_r, flange_t, flare_h, mouth_z = const("flange_r"), const("flange_t"), const("flare_h"), const("mouth_z")
wand_down, wand_lean, clear = const("wand_down"), const("wand_lean"), const("clear")
cleat_proud, cleat_w, roof_relief = const("cleat_proud"), const("cleat_w"), const("roof_relief")

views = [
    ("iso", "From the front right. The wand comes out of the drum's right side, 45&#176; down, and leans 20&#176; off the wall."),
    ("front", "Facing the wall. The flange hides the drum; the four screw holes sit outside it."),
    ("right", "From the right. The wand leans away from the wall, so the grip and cable boot clear it."),
    ("below", "From below. The mouth in the drum's side, and the flange's 45&#176; flare underneath (prints without support)."),
    ("section-cleat", "Cut along the wand, seen from the front left. The nose (blue ghost) hangs in the cavity with the notch side down; the roof steps up 4 mm toward the mouth so the nose can be lifted over the cleat on the way in."),
    ("section-notch", "Cut across the notch, seen from the grip end. The cleat sits in the connector's own lock notch with room on both sides."),
]
figs = "".join(f'<figure>{img(n)}<figcaption>{c}</figcaption></figure>' for n, c in views)

html = f"""<title>NACS Holster Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{{--bg:#f6f4ef;--ink:#1f2a33;--muted:#5d6b76;--rule:#d7d2c7;--card:#fbfaf7;--accent:#b8541c}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#171a1d;--ink:#e8e4dc;--muted:#a19b90;--rule:#3a3f45;--card:#1f2327;--accent:#e8863a}}}}
:root[data-theme="dark"]{{--bg:#171a1d;--ink:#e8e4dc;--muted:#a19b90;--rule:#3a3f45;--card:#1f2327;--accent:#e8863a}}
body{{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.5;margin:0;padding-block:24px 48px;padding-inline:20px}}
main{{max-width:1100px;margin:0 auto}}
h1{{font-size:1.9rem;font-weight:600;margin:0 0 4px}} h2{{font-size:1.15rem;font-weight:600;margin:32px 0 10px;padding-top:14px;border-top:1px solid var(--rule)}}
p,li{{max-width:70ch}} .lead{{color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}}
figure{{margin:0;background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:8px}}
figure img{{width:100%;height:auto;border-radius:4px;background:#f8f8f8}}
figcaption{{font-size:.88rem;color:var(--muted);margin-top:6px}}
ul{{padding-left:20px}} li{{margin:4px 0}} .k{{color:var(--accent);font-weight:500}}
</style>
<main>
<h1>NACS Holster Plan</h1>
<p class="lead">OpenSCAD model of the wall holder for the Tesla Gen 3 Wall Connector handle: a drum on a square plate, the wand out of the drum's right side at {wand_down:.0f}&#176; down, hanging on a fixed cleat in the connector's own lock notch. Rendered from <code>holder.scad</code>; the nose profile is Tesla's, from their NACS STEP file.</p>
<div class="grid">{figs}</div>

<h2>What is set</h2>
<ul>
<li>Plate <span class="k">{plate_w:.0f} &#215; {plate_w:.0f} &#215; {plate_t:.0f} mm</span>, four countersunk holes for #8 screws, 10 mm in from the corners.</li>
<li>Drum <span class="k">&#216;{2 * drum_r:.0f}</span>, <span class="k">{drum_l:.0f} mm</span> out from the plate; teardrop flange &#216;{2 * flange_r:.0f} with its point along the wand, on a {flare_h:.0f} mm 45&#176; flare.</li>
<li>Wand <span class="k">{wand_down:.0f}&#176; down</span> and <span class="k">{wand_lean:.0f}&#176; off the wall</span>; the mouth is {mouth_z:.0f} mm out from the wall, so the grip end is about 65 mm off the wall.</li>
<li>Cavity: the connector profile plus {clear:.1f} mm; notch side down, button side up. Cleat {cleat_w:.0f} mm wide, {cleat_proud:.1f} mm proud, on the lower wall, with a 10&#176; hook face so the hanging weight pulls the nose down onto it. Roof relieved {roof_relief:.0f} mm for insertion, tight over the tip so the handle's weight cannot lever the tip up.</li>
<li>Cable: wraps the outer {drum_l - flange_t - flare_h - 57:.0f} mm of drum beside the wand, one turn per layer; the rest hangs in a loop off the flange, as on the sample.</li>
</ul>

<h2>Open</h2>
<ul>
<li>The 20&#176; lean and the 100 mm drum length are my choices; say if the grip should sit further off the wall or you want more cable on the drum.</li>
<li>Printing: plate down on the bed. The cavity roof needs support material inside (the X2D's support nozzle); everything else prints clean.</li>
<li>Logo on the flange: not yet; a recessed Tesla T from the official artwork if you want it.</li>
<li>Next: a coupon print of the cavity and cleat to check the fit on your handle, then the full part.</li>
</ul>
</main>
"""
open(os.path.join(HERE, "plan.html"), "w").write(html)
print("plan.html", len(html) // 1024, "KB")
