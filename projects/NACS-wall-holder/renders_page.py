#!/usr/bin/env python3
"""Write plan.html: the OpenSCAD renders of holder.scad with captions and the design constants.

    ./render.sh && python3 renders_page.py      (coupon numbers come from coupon-slice.json, written by pipeline/make_coupon_3mf.py)
"""
import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SCAD = open(os.path.join(HERE, "holder.scad")).read()


def const(name):
    return float(re.search(rf"(?:^|;)\s*{name}\s*=\s*([-0-9.]+)", SCAD, re.M).group(1))


def img(name):
    data = base64.b64encode(open(os.path.join(HERE, "images", "scad", name + ".png"), "rb").read()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{name}">'


def figs(views):
    return "".join(f'<figure>{img(n)}<figcaption>{c}</figcaption></figure>' for n, c in views)


plate_w, plate_t, drum_r, drum_l = const("plate_w"), const("plate_t"), const("drum_r"), const("drum_l")
flange_t, fillet_flange, fillet_plate = const("flange_t"), const("fillet_flange"), const("fillet_plate")
flange_r = drum_r + fillet_flange
wand_down, wand_lean, clear = const("wand_down"), const("wand_lean"), const("clear")
roof_relief, pocket_h, cleat_clear, undercut, tip_gap = const("roof_relief"), const("pocket_h"), const("cleat_clear"), const("undercut"), const("tip_gap")
cleat_h = pocket_h - cleat_clear
cleat_w_base, cleat_w_top = 2 * (5.78 - cleat_clear / 0.951), 2 * (5.10 - cleat_clear / 0.951)   # pocket half widths at the mouth and 3 mm up, less the clearance square to its 18 degree walls
logo_h, logo_depth, coupon_wall = const("logo_h"), const("logo_depth"), const("coupon_wall")
mouth_z, cleat_depth, behind = const("mouth_z"), const("cleat_depth"), const("behind")
drum_straight = drum_l - fillet_plate - fillet_flange - flange_t
try:
    sl = json.load(open(os.path.join(HERE, "coupon-slice.json")))
    g = sl["grams_per_filament"]
    coupon_time = f"{sl['minutes'] // 60} h {sl['minutes'] % 60:02d} min, {sl['grams']:.0f} g in all: {g.get('1', 0):.0f} g PETG and {g.get('2', 0):.0f} g support material, from a real slice of <code>coupon-print.3mf</code>."
except FileNotFoundError:
    coupon_time = "not sliced yet."

holder_views = [
    ("iso", f"From the front right. The wand comes out of the drum's right side, 45&#176; down, and leans {wand_lean:.0f}&#176; off the wall; the Tesla T is recessed in the flange face."),
    ("front", "Facing the wall. The flange hides the drum; the four screw holes sit outside it."),
    ("right", "From the right. The wand leans away from the wall, so the grip and cable boot clear it."),
    ("below", "From below. The mouth in the drum's side, and the curved blend under the flange."),
    ("section-cleat", f"Cut along the wand, seen from the front. The handle (grey) hangs with its lock notch on the cleat, whose holding wall is {cleat_depth:.2f} mm (1.25 in) in from the opening along the lower wall. The housing behind the nose sits inside too, in a cavity cut to Tesla's own sections. The roof steps up so the nose can be lifted over the cleat on the way in."),
    ("cleat-detail", f"The cleat, close up, in the same cut. A ramp rises from the mouth side (lower right) to a sharp edge at the back, {cleat_h:.2f} mm above the floor, and the back face overhangs by {undercut:.0f}&#176;. The lock pocket's wall hangs on that edge, up near the pocket's base, so the pull of the hanging handle cannot ride it up and off."),
    ("section-notch", f"Cut across the cleat, seen from the grip end. The cleat (green) is the lock pocket's own shape less {cleat_clear:.2f} mm: {cleat_w_base:.1f} mm wide at the floor, leaning in with the pocket's walls, domed on top like the pocket's base. The band above the handle is the roof relief."),
]
long = json.load(open(os.path.join(HERE, "coupon-long-slice.json")))
cleat_views = [
    ("cleat-detail", f"As modelled: {(6.54 - 0.11 - cleat_clear - 0.1):.1f} mm long, {cleat_h:.2f} mm tall. The wedge sits inside the lock pocket with a gap at each end and under the pocket's base (dark band). Overlap with the wand: none."),
    ("cleat-detail-long", f"50% longer at the same 31&#176; angle: {1.5 * (6.54 - 0.11 - cleat_clear - 0.1):.1f} mm long, {1.5 * cleat_h:.2f} mm tall. The tip goes {1.5 * cleat_h - pocket_h:.1f} mm through the pocket's base and the ramp runs 2.4 mm past the pocket's far wall, under the wand. Overlap with the wand: 31 mm&#179;."),
]
coupon_views = [
    ("coupon-iso", "The coupon as it prints, with the handle docked: the nose cavity and cleat with 3 mm of body around them, carried down to a thin base."),
    ("coupon-mouth", "The open end is a flat cut just past the nose shoulder."),
    ("coupon-section", "Cut along the wand: the same nose cavity, tight roof, roof relief and cleat as the holder, ending past the shoulder."),
]

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
code{{font-size:.9em}}
</style>
<main>
<h1>NACS Holster Plan</h1>
<p class="lead">OpenSCAD model of the wall holder for the Tesla Gen 3 Wall Connector handle: a drum on a square plate, the wand out of the drum's right side at {wand_down:.0f}&#176; down, hanging on a fixed cleat in the connector's own lock notch. Rendered from <code>holder.scad</code>; the nose profile is Tesla's, from their NACS STEP file.</p>
<div class="grid">{figs(holder_views)}</div>

<h2>What is set</h2>
<ul>
<li>Plate <span class="k">{plate_w:.0f} &#215; {plate_w:.0f} &#215; {plate_t:.0f} mm</span>, four countersunk holes for #8 screws, 10 mm in from the corners.</li>
<li>Drum <span class="k">&#216;{2 * drum_r:.0f}</span>, <span class="k">{drum_l:.0f} mm</span> out from the plate; teardrop flange &#216;{2 * flange_r:.0f} with its point to the lower left, blended into the drum with an R{fillet_flange:.0f} curve (R{fillet_plate:.0f} at the plate).</li>
<li>Tesla T recessed <span class="k">{logo_depth:.0f} mm</span> into the flange face, <span class="k">{logo_h:.0f} mm</span> tall (57% of the round part, as on the sample), centred on the drum axis, from the official emblem artwork.</li>
<li>Wand <span class="k">{wand_down:.0f}&#176; down</span> and <span class="k">{wand_lean:.0f}&#176; off the wall</span>; the mouth is {mouth_z:.0f} mm out from the wall, so the wand is hooked in last, outside the cable. The grip clears the wall by about 25 mm where it starts, 36 mm at its middle and 52 mm at its end.</li>
<li>Cleat depth: the cleat's holding wall is <span class="k">{cleat_depth:.2f} mm (1.25 in)</span> from the opening, measured along the cleat's wall. That seats the whole nose and the glossy housing behind it inside the drum; the cavity's deepest corner comes within {behind:.0f} mm of the wall, into the {plate_t:.0f} mm plate, and the top of the mouth runs about 5 mm up the blend under the flange.</li>
<li>Cavity: the connector profile plus {clear:.1f} mm; notch side down, button side up. Roof relieved {roof_relief:.0f} mm for insertion, tight over the tip so the handle's weight cannot lever the tip up.</li>
<li>Cleat: a wedge cut to Tesla's lock pocket (spec: 9.71 &#177;0.2 wide and 6.2 &#177;0.2 long at its base, 4 &#177;0.2 deep; in Tesla's CAD it opens to 11.6 wide at the mouth and has a domed base). <span class="k">{cleat_w_base:.1f} mm wide</span> at the floor narrowing to {cleat_w_top:.1f}, <span class="k">{cleat_h:.2f} mm tall</span>, ramp at 31&#176; from the mouth side up to a sharp edge at the back, back face overhanging {undercut:.0f}&#176;. The nose stops {tip_gap:.1f} mm short of the cavity's end wall when hanging; that is the travel for pushing the pocket past the edge so the nose drops onto the cleat.</li>
<li>Cable: hangs in loops over the top of the drum, as on the sample; {drum_straight:.0f} mm of straight drum between the two blends, room for three &#216;14.5 loops side by side, so the 18 ft cable (about six loops) stacks two deep.</li>
</ul>

<h2>Cleat size: 50% longer, asked 2026-09-18</h2>
<p>Tesla's drawing and CAD give a lock pocket <span class="k">6.5 mm long at its mouth and 4.0 mm deep</span>. The cleat as modelled already fills it to within {cleat_clear:.2f} mm. Half as long again at the same angle is also half as tall again, and that does not go into the pocket in Tesla's CAD: the wand would sit on top of the wedge and not latch.</p>
<div class="grid">{figs(cleat_views)}</div>
<p>Both are ready to print. <code>coupon-print.3mf</code> has the cleat that fits Tesla's pocket. <code>coupon-long-print.3mf</code> has the 50% longer one, {long['minutes'] // 60} h {long['minutes'] % 60:02d} min and {long['grams']:.0f} g. A caliper on the wand's pocket settles which: if it measures near 6.5 long and 4 deep, only the first can work.</p>

<h2>Fit coupon</h2>
<p>The coupon is the holder's nose cavity and the new cleat, cut off just past the nose shoulder, printed the way the holder prints (plate on the bed, tree supports in the cavity roof with Bambu Support For PLA/PETG on the second nozzle). Print time <span class="k">{coupon_time}</span></p>
<p>It proves the nose profile and its 0.5 mm clearance, the cleat in the lock pocket, the tight roof over the tip, and lifting the nose over the cleat. The deeper opening gets no coupon of its own (Brian, 2026-09-17) and is first tried on the full part.</p>
<div class="grid">{figs(coupon_views)}</div>

<h2>Open</h2>
<ul>
<li>Lean: 15&#176;, down from 20&#176;. With the cleat 1.25 in deep the cavity is 62 mm tall inside the drum at 15&#176; and 69 mm at 20&#176;, and the 75 mm drum has 62 mm between the plate and the flange. Keeping 20&#176; would need a drum of about 83 mm.</li>
<li>Past the end of Tesla's housing CAD (48 mm from the tip) the grip is not modelled; the cavity there has 1.5 mm extra room and flares. The coupon will show whether your grip clears it.</li>
<li>Printing: plate down on the bed. The cavity roof and the ring under the flange need support material (the X2D's support nozzle); everything else prints clean.</li>
<li>Next: print the coupon, try the handle on it (insertion over the cleat, hanging, lift-off), then the full part with the deep opening.</li>
</ul>
</main>
"""
open(os.path.join(HERE, "plan.html"), "w").write(html)
print("plan.html", len(html) // 1024, "KB")
