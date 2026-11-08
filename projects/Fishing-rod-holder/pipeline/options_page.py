#!/usr/bin/env python
"""Build projects/Fishing-rod-holder/options.html from the concept drawings and
the PETG slice numbers. Self-contained page (images inlined), published as a
private claude.ai Artifact.

Run from the vault root after concepts.py and slice_stls.py:
  .venv/bin/python projects/Fishing-rod-holder/pipeline/options_page.py
"""
import base64
import json
from pathlib import Path

PROJECT = Path("/home/brian/ClaudeProjects/3d-modeling-brain/projects/Fishing-rod-holder")
IMAGES = PROJECT / "images" / "concepts"
BUILT_IMAGES = PROJECT / "images"
SLICE = json.loads((PROJECT / "concepts-slice-petg.json").read_text())
HOOK = json.loads((PROJECT / "rod-hook-report.json").read_text())
HOOK_SLICE = json.loads((PROJECT / "rod-hook-slice-petg.json").read_text())["rod-hook.stl"]
THREE_MF = PROJECT / "rod-hook-3mf-report.json"
THREE_MF = json.loads(THREE_MF.read_text()) if THREE_MF.exists() else None
OUT = PROJECT / "options.html"

PETG_RHO, PLA_RHO, ASA_RHO = 1.27, 1.24, 1.07


def img(name, alt, folder=IMAGES):
    data = base64.b64encode((folder / name).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{alt}">'


def built_img(name, alt):
    return img(name, alt, BUILT_IMAGES)


def hm(minutes):
    return f"{minutes // 60} h {minutes % 60:02d} min" if minutes >= 60 else f"{minutes} min"


mount, module, end, cap = (SLICE[k] for k in ("comb-mount.stl", "comb-module.stl", "comb-end-module.stl", "cap.stl"))
comb_g = mount["grams"] + module["grams"] + end["grams"]
comb_min = mount["minutes"] + module["minutes"] + end["minutes"]
pair_g, pair_min = 2 * comb_g, 2 * comb_min
caps7_g, caps7_min = 7 * cap["grams"], 7 * cap["minutes"]
caps8_g, caps8_min = 8 * cap["grams"], 8 * cap["minutes"]
two_rod_g = mount["grams"] + end["grams"]
two_rod_min = mount["minutes"] + end["minutes"]


def g(x):
    return f"{x:.0f} g"


hook_g, hook_min = HOOK_SLICE["grams"], HOOK_SLICE["minutes"]
lifts = HOOK["escape_lift_in"]
if THREE_MF:
    plates = THREE_MF.get("plates", [])
    plate_rows = "".join(
        f'<tr><td>Plate {p["plate"]}</td><td class="num">{p["hooks"]}</td><td class="num">{g(p["grams"])}</td><td class="num">{hm(int(p["minutes"]))}</td></tr>'
        for p in plates)
    total_row = f'<tr><td><strong>Total</strong></td><td class="num">{THREE_MF.get("hooks", "")}</td><td class="num"><strong>{g(THREE_MF.get("grams", 0))}</strong></td><td class="num"><strong>{hm(int(THREE_MF.get("minutes", 0)))}</strong></td></tr>'
    pad = THREE_MF.get("pad_density", {})
    pad_line = (f'Solid pads proven in the sliced G-code: {pad.get("pad", "?")} plastic fraction inside a pad against {pad.get("plain", "?")} in the plain plate.'
                if pad else "")
    three_mf_html = f"""
  <div class="tablewrap"><table>
  <tr><th>Print file</th><th>Hooks</th><th>Grams</th><th>Time</th></tr>
  {plate_rows}{total_row}
  </table></div>
  <p style="font-size:14px;color:var(--muted)"><code>rod-hook.3mf</code>, one project file, {len(plates)} plate{"s" if len(plates) != 1 else ""}. PETG, 2 walls, 15% gyroid, 0.30 mm layers, 2-loop skirt. {pad_line} Open it in Bambu Studio once to confirm the plates show.</p>"""
else:
    three_mf_html = '<p style="font-size:14px;color:var(--muted)">The print file (<code>rod-hook.3mf</code>, 8 hooks with solid screw pads) is being built; numbers land here when it is sliced.</p>'

BANNER = f"""
<section class="decided">
  <div class="eyebrow">Decided 2026-11-07</div>
  <p><strong>Deep hook pocket, as individual printed hooks screwed to a 1x4.</strong> Brian's words: "use the deep hook design ... make individual deep hooks, that can be screwed into a 1x4 piece of wood." PETG. The hook is built and checked below; the concept rounds are kept underneath for the record.</p>
</section>"""

BUILT = f"""
<h2>Built · the rod hook</h2>
<p>One printed part, {HOOK["size_in"][0]:g} x {HOOK["size_in"][1]:g} x {HOOK["size_in"][2]:g} in (3-1/2 x 3-1/4 x 3/8). It screws to the face of a 1x4 with two #8 x 1 in screws, 1 in from the board edge, and reaches 1-3/4 in past the edge. The rod lies in the pocket beside the wood and never touches it. The board hangs from the joist exactly as your combs do.</p>
<div class="row">
  <figure>{built_img("hook-on-board.png", "One hook screwed to the face of a 1x4, a 3/8 in rod seated in the deep pocket")}<figcaption>The hook on its board, 3/8 in rod seated. Mouth away from the board; the rod rolls down into the pocket.</figcaption></figure>
  <figure>{built_img("board-in-place.png", "Four hooks on a 27 in 1x4 hanging from a 2x8 joist, four rods seated")}<figcaption>Four hooks on your 27 in board, 7 in up the joist, 20 in hang as now.</figcaption></figure>
</div>
<div class="row">
  <figure>{built_img("pocket-face-on.png", "Face-on view of the hook with a 5/8 in and a 3/8 in rod in the pocket and two countersunk screw holes")}<figcaption>Face on, from the real part: a 5/8 in blank (dark) and a 3/8 in blank (grey) in the same pocket, two countersunk holes.</figcaption></figure>
  <div class="card">
    <h3>Checks baked into the script</h3>
    <ul>
      <li><strong>Hold.</strong> Pose-space check: the rod centre must rise <span class="num">{lifts["0.25"]:.2f}</span> in (1/4 blank), <span class="num">{lifts["0.375"]:.2f}</span> in (3/8) and <span class="num">{lifts["0.625"]:.2f}</span> in (5/8) before any path to the outside opens. A bump moves a rod millimetres.</li>
      <li><strong>Way in.</strong> Every blank size reaches the pocket from outside with no limit on height, so nothing is trapped either way.</li>
      <li><strong>Clearances.</strong> Seated rods of all three sizes intersect neither the hook nor the board; the hook sits flat on the board face.</li>
      <li><strong>Printable.</strong> Flat on the bed, no overhangs; thinnest wall 1/8 in (3.2 mm) against the 1.24 mm minimum; countersinks open upward at 45 degrees.</li>
      <li><strong>Exported STL</strong> is watertight, one solid, {HOOK["stl_volume_cm3"]} cm3.</li>
    </ul>
  </div>
</div>
<figure>{built_img("board-layout.png", "Drilling guide: a 27 in 1x4 with four hooks at 4 in pitch, screw positions and hook bottoms dimensioned")}<figcaption>Drilling guide for the board: hooks at 4 in, bottoms at 4-5/8, 8-5/8, 12-5/8 and 16-5/8 in below the joist; screws 1 in from the edge, 9/16 and 2-11/16 in up from each hook's bottom. Use 5 in if reels stay on and line up.</figcaption></figure>
<div class="cards">
  <div class="card pick"><span class="tag">Per hook</span><h3>{g(hook_g)} · {hm(hook_min)}</h3>
    <ul><li>PETG, 2 walls, 15% infill, 0.30 mm layers, real slice.</li><li>Eight hooks (two boards of four): {g(8 * hook_g)}, {hm(8 * hook_min)}.</li><li>Your seven notches' worth: {g(7 * hook_g)}.</li></ul></div>
  <div class="card"><span class="tag">Lighter</span><h3>Not worth it</h3>
    <ul><li>The part is already 3/8 in; thinner loses the countersink depth.</li><li>PLA would save {g(hook_g - hook_g * PLA_RHO / PETG_RHO)} per hook and creep on a hot ceiling.</li></ul></div>
</div>
{three_mf_html}
<h3 style="margin-top:24px">Files</h3>
<ul>
  <li><code>projects/Fishing-rod-holder/rod_hook.py</code>: the parametric CAD with the checks; <code>rod-hook-report.json</code> is its output.</li>
  <li><code>rod-hook.stl</code>: one hook in print orientation (back face down).</li>
  <li><code>rod-hook.3mf</code>: the Bambu project file with solid pads at every screw hole.</li>
  <li>Mirror image: not needed for one board edge; say so if a board needs hooks on both edges.</li>
</ul>
"""

html = f"""<title>Rafter Rod Holder</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
/* Layout: one column of sections, decision cards in a wrapping grid; print blue is the accent, wood tones for the garage. */
:root {{
  --bg: #f4f5f7; --surface: #ffffff; --fg: #1b2430; --muted: #5d6675; --line: #d9dde3;
  --accent: #2f6fe4; --accent-ink: #1f4fa8; --wood: #c9a46e; --warn: #c2410c; --tag: #e3ecfc;
  --display: "Barlow Condensed", "Arial Narrow", sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #11161d; --surface: #1a212b; --fg: #e7ebf1; --muted: #a2acba; --line: #2c3640;
    --accent: #78a4ff; --accent-ink: #a9c4ff; --wood: #b48a52; --warn: #ff8a5b; --tag: #22304a; color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #11161d; --surface: #1a212b; --fg: #e7ebf1; --muted: #a2acba; --line: #2c3640;
  --accent: #78a4ff; --accent-ink: #a9c4ff; --wood: #b48a52; --warn: #ff8a5b; --tag: #22304a; color-scheme: dark;
}}
body {{ background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 16px; line-height: 1.5;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 0 48px; }}
main {{ max-width: 1080px; margin: 0 auto; }}
h1, h2, h3 {{ font-family: var(--display); text-wrap: balance; letter-spacing: 0.01em; margin: 0; }}
h1 {{ font-size: clamp(40px, 7vw, 64px); line-height: 1; font-weight: 700; }}
h2 {{ font-size: 30px; font-weight: 600; margin-top: 56px; margin-bottom: 8px; }}
h3 {{ font-size: 22px; font-weight: 600; }}
.eyebrow {{ font-family: var(--mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }}
header {{ padding-block: 40px 8px; border-bottom: 1px solid var(--line); display: grid; gap: 10px; }}
header p {{ max-width: 68ch; margin: 0; color: var(--muted); }}
p {{ max-width: 68ch; }}
figure {{ margin: 16px 0 0; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 8px; }}
figure img {{ display: block; width: 100%; height: auto; max-width: 100%; border-radius: 3px; }}
figcaption {{ font-size: 14px; color: var(--muted); padding: 8px 4px 2px; }}
.row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; align-items: start; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 16px; }}
.card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px 18px; display: grid; gap: 8px; align-content: start; min-width: 0; }}
.card.pick {{ border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }}
.tag {{ display: inline-block; font-family: var(--mono); font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; background: var(--tag); color: var(--accent-ink); padding: 2px 8px; border-radius: 3px; }}
.tag.warn {{ background: transparent; color: var(--warn); border: 1px solid var(--warn); }}
.num {{ font-family: var(--mono); font-variant-numeric: tabular-nums; }}
.big {{ font-family: var(--display); font-size: 34px; line-height: 1; font-weight: 700; }}
.big small {{ font-family: var(--body); font-size: 14px; font-weight: 400; color: var(--muted); margin-left: 6px; }}
ul {{ padding-left: 20px; margin: 8px 0 0; }}
li {{ margin: 4px 0; }}
.card ul {{ font-size: 15px; color: var(--fg); }}
table {{ border-collapse: collapse; width: 100%; font-size: 15px; margin-top: 12px; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); font-weight: 500; }}
td.num {{ white-space: nowrap; }}
.tablewrap {{ overflow-x: auto; }}
.picks {{ background: var(--surface); border: 1px solid var(--accent); border-radius: 6px; padding: 18px 20px; margin-top: 16px; }}
fieldset {{ border: 0; padding: 0; margin: 12px 0 0; display: grid; gap: 6px; }}
legend {{ font-family: var(--display); font-size: 20px; font-weight: 600; padding: 0; margin-bottom: 4px; }}
label.opt {{ display: flex; gap: 10px; align-items: baseline; cursor: pointer; }}
label.opt input {{ accent-color: var(--accent); }}
button {{ font: inherit; font-weight: 600; background: var(--accent); color: #fff; border: 0; border-radius: 4px; padding: 10px 16px; cursor: pointer; }}
button.ghost {{ background: transparent; color: var(--accent-ink); border: 1px solid var(--accent); }}
button:focus-visible, input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
#out {{ margin-top: 12px; font-family: var(--mono); font-size: 14px; white-space: pre-wrap; background: var(--bg); border: 1px dashed var(--line); padding: 10px 12px; border-radius: 4px; }}
.assume {{ columns: 2; column-gap: 32px; font-size: 15px; }}
.decided {{ margin-top: 24px; background: var(--tag); border-left: 4px solid var(--accent); border-radius: 4px; padding: 14px 18px; }}
.decided p {{ margin: 6px 0 0; max-width: 80ch; }}
.history {{ margin-top: 64px; border-top: 1px solid var(--line); padding-top: 8px; }}
.history .eyebrow {{ margin-top: 16px; }}
@media (max-width: 640px) {{ .assume {{ columns: 1; }} h2 {{ margin-top: 40px; }} }}
footer {{ margin-top: 56px; font-size: 14px; color: var(--muted); border-top: 1px solid var(--line); padding-top: 16px; }}
code {{ font-family: var(--mono); font-size: 0.92em; }}
</style>

<main>
<header>
  <div class="eyebrow">Options · 2026-11-07 · Bambu X2D, 0.6 nozzle</div>
  <h1>Rafter Rod Holder</h1>
  <p>A printed replacement for the two notched 1x4 combs on your garage joists. Your rods stay put until you pull a neighbour, then any bump drops one. Everything below is drawn to scale from one parameter file; the grams and times are from real slices (PETG, 2 walls, 15% infill, 0.30 mm layers).</p>
</header>
{BANNER}
{BUILT}

<div class="history">
<div class="eyebrow">How we got here · the concept round, 2026-11-07</div>
</div>

<h2>Why they fall out</h2>
<p>A half-round cut into a vertical edge has its lowest point at the edge. The rod rolls down the arc and rests at the mouth with nothing in front of it. A hook pocket puts the floor inside the plate behind a lip, so a rod has to rise over the lip before it can leave.</p>
<figure>{img("why.png", "Left: the rod resting at the mouth of a half-round notch. Right: a hook pocket with the rod seated behind a 5/8 in lip")}
<figcaption>Left: your notch, rod at the mouth. Right: the hook pocket. Both drawn at the same scale.</figcaption></figure>

<h2>The comb in place</h2>
<p>Same idea as your boards: a plate screwed to the side face of the joist, hanging straight down, rods lying across two of them. It is 2-1/2 in wide and 1/2 in thick, hangs 17 in below the joist (yours hang 20), and holds four rods 4 in apart. The mouths face the same way your notches do.</p>
<div class="row">
  <figure>{img("render-comb.png", "Shaded view of the printed comb on a 2x8 joist with four rods seated")}<figcaption>Looking up from the garage floor: the comb on its joist, four rods seated.</figcaption></figure>
  <figure>{img("scene-a.png", "Elevation of option A on the joist with dimensions")}<figcaption>Face on, to scale: three #8 screws into the joist, two half-laps with M4 bolts, pockets every 4 in.</figcaption></figure>
</div>
<figure>{img("render-pocket.png", "Close-up of one hook pocket with a rod seated behind the lip")}<figcaption>One pocket, close up. The rod sits on the pocket floor; the lip in front is 5/8 in above it, with a chamfer so the rod rides in.</figcaption></figure>

<h2>Decision 1 · Pocket shape</h2>
<figure>{img("pockets.png", "Three pocket shapes at one scale: hook pocket, deep hook, snap clip")}</figure>
<div class="cards">
  <div class="card"><h3>A · Hook pocket</h3>
    <div class="big">5/8 in<small>lift to leave</small></div>
    <ul><li>Level mouth: slide the rod in, let it drop.</li><li>Any blank from 1/4 to 5/8 in sits in the 7/8 in pocket.</li><li>No moving parts, nothing to relax over the years.</li></ul></div>
  <div class="card pick"><span class="tag">Picked</span><h3>B · Deep hook</h3>
    <div class="big">1 in<small>lift to leave</small></div>
    <ul><li>Mouth higher than the lip: the rod rolls into the pocket by itself.</li><li>Harder to lift out overhead; each pocket is 3/8 in taller, so the comb grows or the pitch does.</li></ul></div>
  <div class="card"><span class="tag warn">Fit per rod size</span><h3>C · Snap clip</h3>
    <div class="big">Grips<small>every direction</small></div>
    <ul><li>PETG spring fingers close over the blank.</li><li>Fits 5/16 to 7/16 in blanks only; thinner rods rattle, thicker ones will not go in.</li><li>Springs relax in a hot garage.</li></ul></div>
</div>

<h2>Decision 2 · What gets printed</h2>
<p><span class="tag">Picked: a blend</span> Individual printed hooks on a plain 1x4: B's wood backbone and screw-on pieces, without the old notches, and A's pocket in every hook.</p>
<figure>{img("build.png", "Left: the printed comb exploded into mount, module and end module. Right: printed caps screwed over the notches of the existing wood comb")}</figure>
<div class="cards">
  <div class="card"><h3>A · Printed comb, three pieces</h3>
    <div class="big num">{g(comb_g)}<small>per comb, {hm(comb_min)}</small></div>
    <div class="num" style="color:var(--muted)">pair: {g(pair_g)}, {hm(pair_min)}</div>
    <ul><li>Mount {g(mount["grams"])}, module {g(module["grams"])}, end module {g(end["grams"])}; every piece lies flat on the bed.</li>
        <li>Half-laps with two M4 bolts; the mount takes three #8 x 1-1/2 wood screws.</li>
        <li>Two rods: mount plus end module, {g(two_rod_g)}, hang 9 in. Six rods would hang 25 in, so a second pair instead.</li></ul></div>
  <div class="card"><span class="tag">Cheapest fix</span><h3>B · Caps on your wood combs</h3>
    <div class="big num">{g(cap["grams"])}<small>per cap, {hm(cap["minutes"])}</small></div>
    <div class="num" style="color:var(--muted)">your 7 notches: {g(caps7_g)}, {hm(caps7_min)}</div>
    <ul><li>One cap per notch, 2-3/4 x 3-1/4 x 3/8 in, two #8 screws into the board, mouth 1 in proud of the edge.</li>
        <li>The boards, their 20 in hang and the 5 in spacing stay as they are.</li>
        <li>Same hook pocket; the rod ends up inside the old notch.</li></ul>
    <figure style="margin-top:4px">{img("render-cap.png", "A cap screwed to the face of the wood comb, rod seated")}</figure></div>
</div>

<h2>Decision 3 · Material</h2>
<div class="tablewrap"><table>
<tr><th>Material</th><th>One comb</th><th>Pair</th><th>7 caps</th><th>Verdict</th></tr>
<tr><td><strong>PETG</strong> <span class="tag">Recommended</span></td><td class="num">{g(comb_g)}, {hm(comb_min)}</td><td class="num">{g(pair_g)}</td><td class="num">{g(caps7_g)}</td><td>Holds its shape in a hot garage under a load that never comes off. Same spool as the NACS and skateboard holders.</td></tr>
<tr><td>PLA</td><td class="num">{g(comb_g * PLA_RHO / PETG_RHO)}, {hm(comb_min)}</td><td class="num">{g(pair_g * PLA_RHO / PETG_RHO)}</td><td class="num">{g(caps7_g * PLA_RHO / PETG_RHO)}</td><td>Saves nothing worth having and creeps when a summer ceiling goes past 45 C with rods hanging on it.</td></tr>
<tr><td>ASA</td><td class="num">{g(comb_g * ASA_RHO / PETG_RHO)}, {hm(comb_min)}</td><td class="num">{g(pair_g * ASA_RHO / PETG_RHO)}</td><td class="num">{g(caps7_g * ASA_RHO / PETG_RHO)}</td><td>Only if that ceiling bakes above 70 C. Needs the chamber in heat mode.</td></tr>
</table></div>
<p style="font-size:14px;color:var(--muted)">PLA and ASA grams are the PETG slice scaled by density; times carry over. Rods are light: four with reels are under 3 lb per comb.</p>

<h2>What I assumed, and what the side view asks</h2>
<figure>{img("side.png", "Side view along the joists: two combs on joists 16 in on centre, four 7 ft rods, spinning reels at the handle end, comb spacing marked unknown")}
<figcaption>Looking across the rods. Reels and comb spacing are the two things the picture cannot settle on its own.</figcaption></figure>
<ul class="assume">
  <li><strong>Joists</strong> 2x8 at 16 in on centre (the 7 in of board above the joist bottom matched a 2x8).</li>
  <li><strong>Rods per comb</strong> 4, like your longer board. Modules add two at a time.</li>
  <li><strong>Pitch</strong> 4 in, first rod 4 in below the joist. If reels stay on and line up, go 5 in or stagger the handles.</li>
  <li><strong>Blank at the comb</strong> 1/4 to 5/8 in; pocket 7/8 in, mouth 1-1/4 in tall.</li>
  <li><strong>Hang</strong> 17 in clears the open door the way your 20 in does.</li>
  <li><strong>Mouth</strong> faces the same way as your notches; say so if it should flip.</li>
  <li><strong>Screws</strong> three #8 x 1-1/2 into the joist, solid pads around every hole in the 3MF.</li>
  <li><strong>Comb spacing</strong> unknown; it only matters for the rods, not the print.</li>
</ul>

<h2>Your picks</h2>
<p style="font-size:14px;color:var(--muted)">Pocket and build are decided (above). The buttons stay for the open items: material, rods per comb, reels.</p>
<div class="picks">
  <fieldset><legend>Pocket shape</legend>
    <label class="opt"><input type="radio" name="pocket" id="pocket-a" value="A hook pocket"> A · Hook pocket, 5/8 in lift</label>
    <label class="opt"><input type="radio" name="pocket" id="pocket-b" value="B deep hook" checked> B · Deep hook, 1 in lift (decided)</label>
    <label class="opt"><input type="radio" name="pocket" id="pocket-c" value="C snap clip"> C · Snap clip</label></fieldset>
  <fieldset><legend>What gets printed</legend>
    <label class="opt"><input type="radio" name="build" id="build-a" value="A printed comb"> A · Printed comb in three pieces</label>
    <label class="opt"><input type="radio" name="build" id="build-b" value="B caps on the wood combs"> B · Caps on the wood combs</label>
    <label class="opt"><input type="radio" name="build" id="build-c" value="individual hooks on a 1x4" checked> Individual hooks on a 1x4 (decided)</label></fieldset>
  <fieldset><legend>Material</legend>
    <label class="opt"><input type="radio" name="material" id="mat-petg" value="PETG" checked> PETG</label>
    <label class="opt"><input type="radio" name="material" id="mat-pla" value="PLA"> PLA</label>
    <label class="opt"><input type="radio" name="material" id="mat-asa" value="ASA"> ASA</label></fieldset>
  <fieldset><legend>Rods per comb</legend>
    <label class="opt"><input type="radio" name="rods" id="rods-2" value="2"> 2 (mount + end module, hang 9 in)</label>
    <label class="opt"><input type="radio" name="rods" id="rods-4" value="4" checked> 4 (hang 17 in)</label>
    <label class="opt"><input type="radio" name="rods" id="rods-6" value="6"> 6 (hang 25 in, or a second pair)</label></fieldset>
  <fieldset><legend>Reels</legend>
    <label class="opt"><input type="radio" name="reels" id="reels-off" value="reels come off" checked> Reels come off, 4 in pitch</label>
    <label class="opt"><input type="radio" name="reels" id="reels-on" value="reels stay on, 5 in pitch"> Reels stay on, 5 in pitch</label></fieldset>
  <p style="margin-top:16px"><button id="copy">Copy picks</button> <button class="ghost" id="show">Show</button></p>
  <div id="out" hidden></div>
</div>

<footer>Source: <code>projects/Fishing-rod-holder/pipeline/concepts.py</code> (geometry and drawings), <code>slice_stls.py</code> (quotes), <code>options_page.py</code> (this page). Slice: <code>concepts-slice-petg.json</code>.</footer>
</main>

<script>
(function () {{
  function v(n) {{ var el = document.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : '?'; }}
  function picks() {{ return 'Rod holder picks: pocket ' + v('pocket') + '; build ' + v('build') + '; material ' + v('material') + '; rods per comb ' + v('rods') + '; ' + v('reels') + '.'; }}
  var out = document.getElementById('out');
  function show() {{ out.textContent = picks(); out.hidden = false; }}
  function select() {{ var r = document.createRange(); r.selectNodeContents(out); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }}
  document.getElementById('show').addEventListener('click', show);
  document.getElementById('copy').addEventListener('click', function () {{
    var t = picks(); show();
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(t).then(function () {{ out.textContent = t + '\\n(copied)'; }}, select);
    }} else {{ select(); }}
  }});
}})();
</script>
"""

OUT.write_text(html)
print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")
print(f"comb {comb_g:.1f} g {hm(comb_min)}; pair {pair_g:.1f} g {hm(pair_min)}; cap {cap['grams']} g {hm(cap['minutes'])}; 7 caps {caps7_g:.1f} g {hm(caps7_min)}")
