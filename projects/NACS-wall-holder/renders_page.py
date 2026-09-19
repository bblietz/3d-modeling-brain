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
    path = os.path.join(HERE, "images", name + ".png") if "/" in name else os.path.join(HERE, "images", "scad", name + ".png")
    data = base64.b64encode(open(path, "rb").read()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{name}">'


def figs(views):
    return "".join(f'<figure>{img(n)}<figcaption>{c}</figcaption></figure>' for n, c in views)


plate_w, plate_t, drum_r, drum_l = const("plate_w"), const("plate_t"), const("drum_r"), const("drum_l")
flange_t, fillet_flange, fillet_plate = const("flange_t"), const("fillet_flange"), const("fillet_plate")
flange_r = drum_r + fillet_flange
wand_down, wand_lean, clear = const("wand_down"), const("wand_lean"), const("clear")
dock_tilt, pocket_h, cleat_clear, undercut, tip_gap = const("dock_tilt"), const("pocket_h"), const("cleat_clear"), const("undercut"), const("tip_gap")
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
hs = json.load(open(os.path.join(HERE, "holder-slice.json")))
hg = hs["grams_per_filament"]

holder_views = [
    ("iso", f"From the front right. The wand comes out of the drum's right side, 45&#176; down, and leans {wand_lean:.0f}&#176; off the wall; the Tesla T is recessed in the flange face."),
    ("front", "Facing the wall. The flange hides the drum; the four screw holes sit outside it."),
    ("right", "From the right. The wand leans away from the wall, so the grip and cable boot clear it."),
    ("below", "From below. The mouth in the drum's side, and the curved blend under the flange."),
    ("section-cleat", f"Cut along the wand, seen from the front. The handle (grey) hangs with its lock notch on the cleat, whose holding wall is {cleat_depth:.2f} mm (1.25 in) in from the opening along the lower wall. The housing behind the nose sits inside too, in a cavity cut to Tesla's own sections. The roof is the connector's size over the tip and opens {dock_tilt:.0f}&#176; toward the mouth; the end wall leans back by the same angle."),
    ("cleat-detail", f"The cleat, close up, in the same cut. A ramp rises from the mouth side (lower right) to a sharp edge at the back, {cleat_h:.2f} mm above the floor, and the back face overhangs by {undercut:.0f}&#176;. The lock pocket's wall hangs on that edge, up near the pocket's base, so the pull of the hanging handle cannot ride it up and off."),
    ("section-notch", f"Cut across the cleat, seen from the grip end. The cleat (green) is the lock pocket's own shape less {cleat_clear:.2f} mm: {cleat_w_base:.1f} mm wide at the floor, leaning in with the pocket's walls, domed on top like the pocket's base. The band above the handle is the room the wand needs while it pivots in; at this station, 17 mm from the tip, it is about 4 mm."),
]
dock_views = [
    ("dock-1-in", f"1. Nose in with the grip raised about {dock_tilt:.0f}&#176;. The nose's lower front edge rides up the cleat's ramp and over its edge."),
    ("dock-2-stop", "2. Push to the stop. The tip's lower corner is on the floor at the end wall, the top corner has swung into the leaning end wall, and the lock pocket is over the cleat."),
    ("section-cleat", "3. Lower the grip. The nose pivots on its tip and the pocket comes down over the cleat. Let go: the wand slides back a fraction of a millimetre onto the cleat's edge and hangs. To take it out: push in, raise the grip, pull."),
]
coupon_views = [
    ("coupon-iso", "The coupon as it prints, with the handle docked: the nose cavity and cleat with 3 mm of body around them, carried down to a thin base."),
    ("coupon-mouth", "The open end is a flat cut just past the nose shoulder."),
    ("coupon-section", "Cut along the wand: the same nose cavity, roof, leaning end wall and cleat as the holder, ending past the shoulder."),
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

<h2>The full part: ready to print</h2>
<p>The v7 fit coupon printed and the wand docks and holds on it (Brian, 2026-09-18: "the last coupon printed great. This is the one."). The full holder is the same cavity and cleat in the whole drum, exported and sliced: <code>holder.stl</code> and <code>holder-print.3mf</code>.</p>
<ul>
<li>Print: <span class="k">{hs['minutes'] // 60} h {hs['minutes'] % 60:02d} min, {hs['grams']:.0f} g</span> ({hg.get('1', 0):.0f} g PETG, {hg.get('2', 0):.0f} g support interface), {hs['layers']} layers, from a real slice. Same recipe as the coupon (X2D 0.6 nozzle, 0.30 mm, Bambu PETG Basic, textured PEI, tree supports with Support For PLA/PETG on the second nozzle), plus <span class="k">3 walls and 20% gyroid</span> because it hangs a wand and an 18 ft cable off the wall.</li>
<li>Orientation: plate down on the bed, flange and Tesla T up, as the coupon printed. Supports go in the cavity and under the flange ring; the T is a recess in the top face and needs none.</li>
<li>Size on the bed: {plate_w:.0f} &#215; {plate_w:.0f} &#215; 80 mm; the part sits left of centre and the prime tower to its right. The two nozzles only share the bed from x = 20 mm, so the part is placed clear of that.</li>
<li>Base: <span class="k">{plate_w:.0f} mm square</span>, up from 120 (Brian, 2026-09-18: 125%). <span class="k">Solid around every screw hole</span>: a &#216;25 region through the plate at each hole prints at 100% infill. Measured in the sliced G-code between the plate's skins: {min(v for k, v in hs['screw_pads'].items() if k.startswith('pad')) * 100:.0f}% plastic in the pads, {hs['screw_pads']['plain plate'] * 100:.0f}% in the plain plate.</li>
<li>Mounting: four #8 countersunk screws, all four visible from the front on the wider base (on the 120 mm base the lower-left one was hidden behind the flange's point). The lower-left hole's centre is 1.9 mm outside the point, so a slim screwdriver shaft goes straight on and a 1/4 in bit holder comes in at a slight angle. The lower-right one is behind the docked wand: mount the holder with the wand off.</li>
<li>Not covered by the coupon, first tried on this part: the housing and the start of the grip inside the deep opening. The housing room is cut from Tesla's CAD like the nose was; the grip past the end of that CAD has 1.5 mm extra room and flares.</li>
<li>The flange stays whole: the docking room's top corner would have nicked 1.7 mm into its underside at the rim, so the cut stops at the flange. The docking and hold check is unchanged by that.</li>
</ul>

<h2>What is set</h2>
<ul>
<li>Plate <span class="k">{plate_w:.0f} &#215; {plate_w:.0f} &#215; {plate_t:.0f} mm</span>, four countersunk holes for #8 screws, 10 mm in from the corners.</li>
<li>Drum <span class="k">&#216;{2 * drum_r:.0f}</span>, <span class="k">{drum_l:.0f} mm</span> out from the plate; teardrop flange &#216;{2 * flange_r:.0f} with its point to the lower left, blended into the drum with an R{fillet_flange:.0f} curve (R{fillet_plate:.0f} at the plate).</li>
<li>Tesla T recessed <span class="k">{logo_depth:.0f} mm</span> into the flange face, <span class="k">{logo_h:.0f} mm</span> tall (57% of the round part, as on the sample), centred on the drum axis, from the official emblem artwork.</li>
<li>Wand <span class="k">{wand_down:.0f}&#176; down</span> and <span class="k">{wand_lean:.0f}&#176; off the wall</span>; the mouth is {mouth_z:.0f} mm out from the wall, so the wand is hooked in last, outside the cable. The grip clears the wall by about 26 mm where it starts, 38 mm at its middle and 53 mm at its end.</li>
<li>Cleat depth: the cleat's holding wall is <span class="k">{cleat_depth:.2f} mm (1.25 in)</span> from the opening, measured along the cleat's wall. That seats the whole nose and the glossy housing behind it inside the drum; the cavity's deepest corner comes within {behind:.0f} mm of the wall, into the {plate_t:.0f} mm plate, and the top of the mouth runs about 8 mm up the blend under the flange, 3.6 mm short of the flange itself.</li>
<li>Cavity: the connector profile plus {clear:.1f} mm on the sides, the floor and, over the tip, the roof; notch side down, button side up. From the tip outward the roof opens at <span class="k">{dock_tilt:.0f}&#176;</span> and the end wall leans back {dock_tilt:.0f}&#176;: exactly the room a wand pivoting on its tip sweeps, and no more.</li>
<li>Cleat: a wedge cut to Tesla's lock pocket (spec: 9.71 &#177;0.2 wide and 6.2 &#177;0.2 long at its base, 4 &#177;0.2 deep; in Tesla's CAD it opens to 11.6 wide at the mouth and has a domed base). <span class="k">{cleat_w_base:.1f} mm wide</span> at the floor narrowing to {cleat_w_top:.1f}, <span class="k">{cleat_h:.2f} mm tall</span>, ramp at 31&#176; from the mouth side up to a sharp edge at the back, back face overhanging {undercut:.0f}&#176;. The nose stops {tip_gap:.1f} mm short of the cavity's end wall when hanging; that is the travel for pushing the pocket past the edge so the nose drops onto the cleat.</li>
<li>Cable: hangs in loops over the top of the drum, as on the sample; {drum_straight:.0f} mm of straight drum between the two blends, room for three &#216;14.5 loops side by side, so the 18 ft cable (about six loops) stacks two deep.</li>
</ul>

<h2>How it docks, and why it now holds (2026-09-18)</h2>
<p>You asked for the snug size at the end of the cavity to run further out. Checking that against Tesla's CAD turned up the reason the cleat has not been catching. The old roof was snug for 5 mm and then stepped up 5 mm so the nose could be lifted over the cleat. The hanging weight acts far out on the grip, so it levers the wand about the mouth's lower lip: tip up, pocket up. That is the same motion as lifting the nose over the cleat, run backwards. A path search over slide, lift and tilt (<code>pipeline/insertion.py</code>) gave: with the snug roof shorter than <span class="k">3.9 mm</span> the wand gets in, and its own weight takes it back out (the load has to rise only 0.2 mm); longer than that it holds, and cannot get in. At 5 mm the cavity was on the wrong side by 1.1 mm: it would have held, but the wand could not get in. No length of step roof does both.</p>
<p>So the snug part does have to reach further, as you said, and the wand has to dock by a motion the weight cannot undo: <span class="k">grip up, nose in, grip down</span>. The roof is now the connector's size over the tip and opens only as far as that pivot sweeps. Compared with the old step it is closer to the wand for the first 25 mm (0.5 mm over the tip, 1.6 at 10 mm, 3.7 at 20 mm, where the step was 5.5 throughout) and wider beyond. With the wand grown 0.2 mm all round there is still a way in. Hanging, the weight turns the tip up 3&#176; into the roof and stops: <span class="k">1.9 mm of the 3.6 mm edge</span> stays engaged, and the load would have to be raised <span class="k">20 mm</span> against gravity before the wand could come off.</p>
<div class="grid">{figs(dock_views)}</div>
<figure style="margin-top:16px">{img("docking/docking-path")}<figcaption>The check itself: Tesla's real connector section (grey) against the holder's section (teal) at the centre plane, eight poses from outside to docked along the path the search found, then the pose it settles into under load. The search also runs six more sections across the wand.</figcaption></figure>
<p>The 50% longer cleat is retired: it is in the repository's history (commit f0ea071) and its files are removed. Tesla's pocket only takes the present cleat, and the catching problem was the roof, not the cleat's size.</p>

<h2>Fit coupon</h2>
<p>The coupon is the holder's nose cavity and the new cleat, cut off just past the nose shoulder, printed the way the holder prints (plate on the bed, tree supports in the cavity roof with Bambu Support For PLA/PETG on the second nozzle). Print time <span class="k">{coupon_time}</span></p>
<p><span class="k">Result: it fits and holds.</span> It proves the nose profile and its 0.5 mm clearance, the cleat in the lock pocket, docking grip-up over the cleat, and the hold: once docked, pulling the wand straight out or pressing the grip down should not free it; only raising the grip does. The deeper opening gets no coupon of its own (Brian, 2026-09-17) and is first tried on the full part.</p>
<div class="grid">{figs(coupon_views)}</div>

<h2>Open</h2>
<ul>
<li>Lean: 15&#176;, down from 20&#176;. With the cleat 1.25 in deep the cavity is 65 mm tall inside the drum at 15&#176; and 73 mm at 20&#176;; at 20&#176; its top would come out through the flange of the 75 mm drum.</li>
<li>Past the end of Tesla's housing CAD (48 mm from the tip) the grip is not modelled; the cavity there has 1.5 mm extra room and flares. The coupon will show whether your grip clears it.</li>
<li>Printing: plate down on the bed. The cavity roof and the ring under the flange need support material (the X2D's support nozzle); everything else prints clean.</li>
<li>Next: print the full part (<code>holder-print.3mf</code>), mount it, and try the wand in the deep opening with the cable on the drum.</li>
</ul>
</main>
"""
open(os.path.join(HERE, "plan.html"), "w").write(html)
print("plan.html", len(html) // 1024, "KB")
