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
grip_flare, floor_knee, hole_in = const("grip_flare"), const("floor_knee"), const("hole_in")
cut_top, plate_r, edge_r = const("cut_top"), const("plate_r"), 25.4 / 16
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
    ("iso", f"From the front right. The wand comes out of the drum's right side, 45&#176; down, and leans {wand_lean:.0f}&#176; off the wall; the Tesla T, the TESLA wordmark bent along the crest and a frame line are recessed in the face."),
    ("front", "Facing the wall. The crest lip rises 1-1/2 in above the round flange, full width, its sides tapering under an arched top. The bottom screw holes sit just outside the flange; the top two are behind the lip, 6 mm inside its edge, so a driver reaches them at about a 6&#176; tilt."),
    ("right", "From the right. The wand leans away from the wall, so the grip and cable boot clear it."),
    ("below", "From below. The mouth in the drum's side, and the curved blend under the flange."),
    ("section-cleat", f"Cut along the wand, seen from the front. The handle (grey) hangs with its lock notch on the cleat, whose holding wall is {cleat_depth:.2f} mm (1.75 in) in from the opening along the lower wall. The housing behind the nose sits inside too, in a cavity cut to Tesla's own sections. The roof is the connector's size over the tip and opens {dock_tilt:.0f}&#176; toward the mouth; the end wall leans back by the same angle."),
    ("cleat-detail", f"The cleat, close up, in the same cut. A ramp rises from the mouth side (lower right) to a sharp edge at the back, {cleat_h:.2f} mm above the floor, and the back face overhangs by {undercut:.0f}&#176;. The lock pocket's wall hangs on that edge, up near the pocket's base, so the pull of the hanging handle cannot ride it up and off."),
    ("section-notch", f"Cut across the cleat, seen from the grip end. The cleat (green) is the lock pocket's own shape less {cleat_clear:.2f} mm: {cleat_w_base:.1f} mm wide at the floor, leaning in with the pocket's walls, domed on top like the pocket's base. The band above the handle is the room the wand needs while it pivots in; at this station, 17 mm from the tip, it is about 4 mm."),
]
entry_views = [
    ("entry-before", "Before: looking into the mouth from the grip end. Past the end of Tesla's housing CAD the cavity jumped 1.5 mm wider (3 mm at the roof) in one step, which showed as a ledge running round the opening."),
    ("entry", f"Now: the sides and roof open steadily from the nose shoulder to the outer edge, {grip_flare * 100:.0f} mm per 100 mm on each side, and reach the same size at the rim as before. No ledge."),
]
edge_views = [
    ("edges", f"The mouth's rim, the flange's two rims and the plate's top edge, all rounded {edge_r:.1f} mm (1/16 in). The rim's roundover is a rolling ball, so it keeps that radius from the thin roof lip to the blunt floor lip."),
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
<p class="k" style="display:block;font-size:1.1em;margin-bottom:8px">Revision of 2026-10-08: 1 in deeper, a crest lip with the TESLA wordmark, the cavity 1/2 in deeper on a &#216;90 drum. The 2026-09-19 holder is on the wall and working great.</p>
<p class="lead">OpenSCAD model of the wall holder for the Tesla Gen 3 Wall Connector handle: a drum on a square plate, the wand out of the drum's right side at {wand_down:.0f}&#176; down, hanging on a fixed cleat in the connector's own lock notch. Rendered from <code>holder.scad</code>; the nose profile is Tesla's, from their NACS STEP file.</p>
<div class="grid">{figs(holder_views)}</div>

<h2>The October revision (2026-10-08)</h2>
<p>The holder on the wall (printed 2026-09-19, Brian: "charger holder is on the wall and working great") gets four changes, picked from rendered options: the drum <span class="k">1 in deeper</span> ({drum_l:.0f} mm, the holder {drum_l + plate_t:.0f} mm off the wall) and <span class="k">&#216;{2 * drum_r:.0f}</span>; a <span class="k">crest lip</span> on the flange, full width, 1-1/2 in above the flange's top, the shield's tapering sides under the arch's crowned top, 1/2 in corners; the <span class="k">cavity 1/2 in deeper</span> (cleat wall {cleat_depth / 25.4:.2f} in from the opening); and on the face the <span class="k">Tesla T, the TESLA wordmark bent along the crest, and a frame line</span> round the whole outline, all 1 mm recesses. The nose cavity, cleat, docking motion and wand angles are the validated ones. Files: <code>holder.stl</code> and <code>holder-print.3mf</code>.</p>
<ul>
<li>Print: <span class="k">{hs['minutes'] // 60} h {hs['minutes'] % 60:02d} min, {hs['grams']:.0f} g</span> ({hg.get('1', 0):.0f} g PETG, {hg.get('2', 0):.0f} g support interface), {hs['layers']} layers, from a real slice. Same recipe as the coupon (X2D 0.6 nozzle, 0.30 mm, Bambu PETG Basic, textured PEI, tree supports with Support For PLA/PETG on the second nozzle), plus <span class="k">3 walls and 20% gyroid</span> because it hangs a wand and an 18 ft cable off the wall.</li>
<li>Orientation: plate down on the bed, face up, as before. Supports go in the cavity, under the flange ring and under the lip, which is a horizontal slab {drum_l + plate_t - flange_t:.0f} mm above the bed; the T, wordmark and frame line are recesses in the top face and need none.</li>
<li>Size on the bed: 104 &#215; 142 &#215; {drum_l + plate_t:.0f} mm; the part sits left of centre and the prime tower at the lower right, <span class="k">{hs['tower_gap_mm']:.0f} mm</span> from it, tree supports included (the lip's supports root further out than the flange's did, so the tower moved from beside the lip to beside the plate). The two nozzles only share the bed from x = 20 mm, so the part is placed clear of that.</li>
<li>Base: <span class="k">4 in square ({plate_w:.1f} mm)</span>, unchanged, same screw pattern. Drum &#216;80 to <span class="k">&#216;{2 * drum_r:.0f}</span> for the deeper cavity: the cavity crosses the drum at 45&#176;, and 1/2 in more depth left 0.1 mm of wall at its far corner on &#216;80; &#216;{2 * drum_r:.0f} leaves 5 mm. The flange stays &#216;{2 * flange_r:.0f}, so its blend is R{fillet_flange:.0f} now (was 12) and the plate's R{fillet_plate:.0f} (was 8), which keeps the screw heads 0.7 mm clear of both. Docking and hold check on the new cavity: way in with the wand grown 0.2 mm (0 to 9&#176; of tilt), hanging tip-up 3&#176; with 1.87 of the 3.57 mm edge engaged, 19.6 mm of lift to come off: the v7 numbers.</li>
<li><span class="k">Solid around every screw hole</span>: a &#216;25 region through the plate at each hole prints at 100% infill. Measured in the sliced G-code between the plate's skins: {min(v for k, v in hs['screw_pads'].items() if k.startswith('pad')) * 100:.0f}% plastic in the pads, {hs['screw_pads']['plain plate'] * 100:.0f}% in the plain plate.</li>
<li>Mounting: the same four #8 countersunk screws, {hole_in:.0f} mm in from the corners, plain holes (Brian, 2026-10-08, over keyhole slots or driver holes through the lip). The bottom two clear the flange by 0.7 mm. The top two are behind the lip: their centres are 6 mm inside the crest's edge at that height, so the driver goes in past the lip at about a 6&#176; tilt (a long bit helps). The lower-right screw is behind the docked wand: mount the holder with the wand off.</li>
<li>Not yet proven: the first 1/2 in of the grip now sits inside the opening (48 to 61 mm from the tip). Tesla's CAD ends at 48 mm; the cavity there is the housing's last section widened {grip_flare * 100:.0f} mm per 100 mm on the sides and roof (about 2 mm per side at the rim) and the floor on Tesla's line. If the grip or the top button is bigger than that, it will not dock; measuring the handle 1/2 in and 1 in behind the glossy housing's end would settle it before the print.</li>
<li>The flange and the blend under it stay whole: the cavity cut stops {cut_top:.1f} mm out from the wall, the height its top reaches inside the drum. Above that the docking room's flared top corner used to run on outside the drum as a narrow groove up to the flange's rim, where no wand goes. The way in is unchanged by that.</li>
</ul>

<h2>A smooth entry (2026-09-18)</h2>
<p>You said the entry is rough and steps in. The step was mine: where Tesla's housing CAD ends, 48 mm from the nose tip, the cavity jumped 1.5 mm wider all round for the grip, which is not in the CAD. That jump sat just inside the mouth. It is gone: the sides and roof now widen steadily from the nose shoulder to the outer edge and arrive at the same size at the rim.</p>
<div class="grid">{figs(entry_views)}</div>
<ul>
<li>The floor is the one wall left alone. The hanging wand rests on it, and letting it fall away with the others changed how the wand hangs in the check (5.5&#176; of droop instead of 3&#176;). It keeps Tesla's line to the end of the housing CAD, exactly as printed, and the old ledge beyond that, right at the lip, is now a {floor_knee:.0f} mm ramp.</li>
<li>Against the cavity you called perfect, the new one only adds room, except for that ramp filling the ledge's corner (29 mm&#179;, under the start of the grip). Docking and hold check: same way in with the wand grown 0.2 mm, same hanging pose (tip up 3&#176;, 1.9 mm of the edge engaged), same 20 mm lift to come off. The rounded floor lip, below, then shifts the hang slightly. Docked clash: 0 mm&#179;.</li>
</ul>

<h2>Rounded edges (2026-09-18)</h2>
<p>You asked for at least 1/16 in of roundover on every edge except the back of the wall plate and the screw holes.</p>
<div class="grid">{figs(edge_views)}</div>
<ul>
<li><span class="k">Plate</span>: top edge rounded all round. The corner radius went from 8 to {plate_r:.0f} mm, so each countersink sits centred in its corner; at 8 the countersink would have broken through the rounded edge.</li>
<li><span class="k">Flange</span>: front and back rims rounded. The back rim's arc runs tangent into the blend under the flange.</li>
<li><span class="k">Mouth</span>: a rolling-ball roundover right round the opening (<code>pipeline/rim_round.py</code>). Measured on the finished mesh, the rounded surface sits within 0.04 mm of a {edge_r:.2f} mm ball all the way round, with no sharp remnant.</li>
<li><span class="k">Effect on the hang</span>: rounding the floor lip moves the point the hanging wand rests on about 1.7 mm inward. In the check the wand now hangs tip-up 3.5&#176; instead of 3.0&#176;, with 1.75 mm of the cleat's edge engaged instead of 1.87, and the lift needed to come off goes from 19.6 to 20.4 mm. The way in is unchanged.</li>
<li><span class="k">Left sharp on purpose</span>: the cleat's holding edge (it is what catches the wand) and the Tesla T's outline (a 1 mm recess; rounding it would blur the emblem). Edges inside the cavity are inside corners, not outside edges.</li>
</ul>

<h2>What is set</h2>
<ul>
<li>Plate <span class="k">{plate_w:.1f} &#215; {plate_w:.1f} &#215; {plate_t:.0f} mm</span> (4 in square), four countersunk holes for #8 screws, {hole_in:.0f} mm in from the corners.</li>
<li>Drum <span class="k">&#216;{2 * drum_r:.0f}</span>, <span class="k">{drum_l:.0f} mm</span> out from the plate (75 until 2026-10-08); <span class="k">round flange &#216;{2 * flange_r:.0f}</span>, blended into the drum with an R{fillet_flange:.0f} curve (R{fillet_plate:.0f} at the plate).</li>
<li>Lip (2026-10-08): a crest in the flange plane, {flange_t:.0f} mm thick, the full {2 * flange_r:.0f} mm wide where it leaves the flange tangentially, tapering to 84 mm at the top, which is an arc crowned 10 mm, 1/2 in corners, 1-1/2 in above the flange's top; every edge rounded 1/16 in like the rest.</li>
<li>Face: Tesla T recessed <span class="k">{logo_depth:.0f} mm</span>, <span class="k">{logo_h:.0f} mm</span> tall, centred on the drum axis; the TESLA wordmark, 62 mm along the arc, bent round the crest's own curve 2 mm under the frame line; a 2.5 mm frame line 6 mm in from the edge following the whole outline. The T and wordmark are the official emblem artwork (Wikimedia <code>Tesla_Motors.svg</code>, split into <code>reference/tesla-t.svg</code> and <code>reference/tesla-wordmark.svg</code>), never rebuilt.</li>
<li>Wand <span class="k">{wand_down:.0f}&#176; down</span> and <span class="k">{wand_lean:.0f}&#176; off the wall</span>; the mouth is {mouth_z:.0f} mm out from the wall, so the wand is hooked in last, outside the cable. The grip clears the wall by about 50 mm where it starts, 62 mm at its middle and 77 mm at its end.</li>
<li>Cleat depth: the cleat's holding wall is <span class="k">{cleat_depth:.2f} mm (1.75 in)</span> from the opening, measured along the cleat's wall (1.25 in on the printed holder; Brian, 2026-10-08: 1/2 in deeper). That seats the whole nose, the glossy housing and the first 1/2 in of the grip inside the drum; the cavity's deepest corner is 23 mm off the wall, and the top of the mouth runs 3.4 mm up the blend under the flange, 3.6 mm short of the flange itself, as before.</li>
<li>Cavity: the connector profile plus {clear:.1f} mm on the sides, the floor and, over the tip, the roof; notch side down, button side up. From the tip outward the roof opens at <span class="k">{dock_tilt:.0f}&#176;</span> and the end wall leans back {dock_tilt:.0f}&#176;: exactly the room a wand pivoting on its tip sweeps, and no more. Behind the nose shoulder the sides and roof open a further {grip_flare * 100:.0f} mm per 100 mm out to the rim; the floor does not.</li>
<li>Cleat: a wedge cut to Tesla's lock pocket (spec: 9.71 &#177;0.2 wide and 6.2 &#177;0.2 long at its base, 4 &#177;0.2 deep; in Tesla's CAD it opens to 11.6 wide at the mouth and has a domed base). <span class="k">{cleat_w_base:.1f} mm wide</span> at the floor narrowing to {cleat_w_top:.1f}, <span class="k">{cleat_h:.2f} mm tall</span>, ramp at 31&#176; from the mouth side up to a sharp edge at the back, back face overhanging {undercut:.0f}&#176;. The nose stops {tip_gap:.1f} mm short of the cavity's end wall when hanging; that is the travel for pushing the pocket past the edge so the nose drops onto the cleat.</li>
<li>Cable: hangs in loops over the top of the drum, as on the sample; {drum_straight:.0f} mm of straight drum between the two blends (47 before), room for {int(drum_straight // 14.5)} &#216;14.5 loops side by side, and the lip keeps them from sliding off the front.</li>
</ul>

<h2>How it docks, and why it now holds (2026-09-18)</h2>
<p>You asked for the snug size at the end of the cavity to run further out. Checking that against Tesla's CAD turned up the reason the cleat has not been catching. The old roof was snug for 5 mm and then stepped up 5 mm so the nose could be lifted over the cleat. The hanging weight acts far out on the grip, so it levers the wand about the mouth's lower lip: tip up, pocket up. That is the same motion as lifting the nose over the cleat, run backwards. A path search over slide, lift and tilt (<code>pipeline/insertion.py</code>) gave: with the snug roof shorter than <span class="k">3.9 mm</span> the wand gets in, and its own weight takes it back out (the load has to rise only 0.2 mm); longer than that it holds, and cannot get in. At 5 mm the cavity was on the wrong side by 1.1 mm: it would have held, but the wand could not get in. No length of step roof does both.</p>
<p>So the snug part does have to reach further, as you said, and the wand has to dock by a motion the weight cannot undo: <span class="k">grip up, nose in, grip down</span>. The roof is now the connector's size over the tip and opens only as far as that pivot sweeps. Compared with the old step it is closer to the wand for the first 25 mm (0.5 mm over the tip, 1.6 at 10 mm, 3.7 at 20 mm, where the step was 5.5 throughout) and wider beyond. With the wand grown 0.2 mm all round there is still a way in. Hanging, the weight turns the tip up 3&#176; into the roof and stops: <span class="k">1.87 mm of the 3.6 mm edge</span> stays engaged, and the load would have to be raised <span class="k">19.6 mm</span> against gravity before the wand could come off (with the 1.25 in cavity the rounded floor lip bore on the housing and gave 3.5&#176;, 1.75 mm and 20.4 mm; with the mouth 1/2 in further out the lip is under the grip, which the check does not model, and the numbers are v7's).</p>
<div class="grid">{figs(dock_views)}</div>
<figure style="margin-top:16px">{img("docking/docking-path")}<figcaption>The check itself: Tesla's real connector section (grey) against the holder's section (teal) at the centre plane, eight poses from outside to docked along the path the search found, then the pose it settles into under load. The search also runs six more sections across the wand.</figcaption></figure>
<p>The 50% longer cleat is retired: it is in the repository's history (commit f0ea071) and its files are removed. Tesla's pocket only takes the present cleat, and the catching problem was the roof, not the cleat's size.</p>

<h2>Fit coupon</h2>
<p>The coupon is the holder's nose cavity and the new cleat, cut off just past the nose shoulder, printed the way the holder prints (plate on the bed, tree supports in the cavity roof with Bambu Support For PLA/PETG on the second nozzle). Print time <span class="k">{coupon_time}</span></p>
<p><span class="k">Result: it fits and holds.</span> It proves the nose profile and its 0.5 mm clearance, the cleat in the lock pocket, docking grip-up over the cleat, and the hold: once docked, pulling the wand straight out or pressing the grip down should not free it; only raising the grip does. The deeper opening gets no coupon of its own (Brian, 2026-09-17) and is first tried on the full part.</p>
<div class="grid">{figs(coupon_views)}</div>

<h2>Open</h2>
<ul>
<li>The grip past the end of Tesla's housing CAD (48 mm from the tip) is not modelled, and the deeper cavity now encloses 1/2 in of it. The sides and roof have 1.6 mm extra room at 48 mm and keep widening ({grip_flare * 100:.0f} mm per 100 mm); the floor has 0.5 mm there and ramps to the same within {floor_knee:.0f} mm. A measurement of the real grip 1/2 in and 1 in behind the housing (width, height, button) would confirm the fit before printing.</li>
<li>Top screws: behind the lip, driven at a tilt. If that proves awkward in practice, the model still has keyhole slots (<code>top_mount = "keyhole"</code>) and driver holes through the lip (<code>"holes"</code>) ready to switch on.</li>
<li>Printing: plate down on the bed. The cavity roof, the ring under the flange and the lip need support material (the X2D's support nozzle); everything else prints clean.</li>
<li>Next: print <code>holder-print.3mf</code>, swap it for the holder on the wall, and try the wand with the cable on the drum.</li>
</ul>
</main>
"""
open(os.path.join(HERE, "plan.html"), "w").write(html)
print("plan.html", len(html) // 1024, "KB")
