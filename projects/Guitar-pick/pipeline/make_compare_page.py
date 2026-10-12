"""Build the HTML sign-off page: the edge profile options (2026-10-12) on top, the
traced Dunlop outline against the generic 351 and the CAD model (approved
2026-10-11) below, so Brian decides against pictures.

    .venv/bin/python projects/Guitar-pick/pipeline/make_compare_page.py <out.html>

Reads outline-dunlop.csv, outline-351.csv, edge-options.json and the PNGs in
images/ (run trace_photo.py, guitar_pick.py, edge_options.py and
render_stl.py first).
"""
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
IMG = PROJECT / "images"
WIDTH, LENGTH, THICK = 26.19, 30.38, 1.0

EDGE_LABELS = {
    "sym": ("Mirrored bevel, printable", "the widest bevel the underside can carry without support, on both faces: 0.45 mm wide dropping 0.35 (38 degrees), creases blended R 0.35, 0.30 mm rim. In the 3MF now."),
    "mirror": ("Mirrored 1.5 mm bevel", "the top bevel with its 5 mm lead-in copied underneath. Red layers hang more than a whole line past the one below: printed in air."),
    "soft": ("1.5 mm bevel on top only", "the blended bevel on top, a 45 degree flat underneath. Not mirrored."),
    "square": ("Square (the first model)", "the outline extruded as is, 90 degree edge."),
    "round": ("Round", "fillet R 0.45 on both faces, 0.10 mm rim."),
    "chamfer": ("Chamfer", "45 degree flat, 0.45 mm, on both faces, 0.10 mm rim."),
    "bevel": ("Bevel with a crease", "1.5 mm wide taper on top dropping 0.35 mm; 45 degree flat underneath; 0.30 mm rim. The line you want gone."),
}


def data_uri(path, max_w=None, fmt="PNG"):
    im = Image.open(path).convert("RGB")
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, fmt, **({"quality": 88} if fmt == "JPEG" else {"optimize": True}))
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()


def svg_path(pts):
    return "M " + " L ".join(f"{x:.2f} {-y:.2f}" for x, y in pts) + " Z"   # SVG y runs down


def tip_circle(pts, band=2.5):
    p = pts[pts[:, 1] < pts[:, 1].min() + band]
    A = np.column_stack([2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))])
    (cx, cy, c), *_ = np.linalg.lstsq(A, (p ** 2).sum(axis=1), rcond=None)
    return cx, cy, np.sqrt(c + cx ** 2 + cy ** 2)


def profile_svg(var, first_layer, layer, window=3.0, limit=0.13):
    """The tip cross-section at scale: the CAD profile as a line over the stair of layers the slicer makes of it
    (each layer's wall reaches from its inset to the right). Tip at the left, bed at the bottom."""
    rects, bounds = [], [0.0]
    for r in var["overhang"]:
        z0 = 0.0 if r["layer"] == 1 else first_layer + (r["layer"] - 2) * layer
        z1 = first_layer if r["layer"] == 1 else z0 + layer
        bad = r["layer"] > 1 and r["step"] > limit and z0 < 0.5      # an underside layer hanging past what the one below can carry
        rects.append(f'<rect x="{r["inset"]:.3f}" y="{-z1:.3f}" width="{window + 0.3 - r["inset"]:.3f}" height="{z1 - z0:.3f}"'
                     + (' fill="var(--warn)" fill-opacity="0.55"' if bad else '') + '/>')
        bounds.append(z1)
    lines = "".join(f'<line x1="-0.15" y1="{-z:.3f}" x2="{window + 0.3}" y2="{-z:.3f}"/>' for z in bounds)
    path = "M " + " L ".join(f"{x:.3f} {-z:.3f}" for x, z in var["section"])      # open: the window edge is not a wall
    return f"""<svg viewBox="-0.3 -1.22 3.6 1.5" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="tip cross-section">
      <g stroke="var(--rule)" stroke-width="0.012">{lines}</g>
      <g fill="var(--accent)" fill-opacity="0.22" stroke="none">{"".join(rects)}</g>
      <path d="{path}" fill="none" stroke="var(--measured)" stroke-width="0.03" stroke-linejoin="round"/>
      <line x1="-0.15" y1="0" x2="{window + 0.3}" y2="0" stroke="var(--fg)" stroke-width="0.02"/>
      <g stroke="var(--muted)" stroke-width="0.015"><line x1="2.0" y1="0.12" x2="3.0" y2="0.12"/><line x1="2.0" y1="0.06" x2="2.0" y2="0.18"/><line x1="3.0" y1="0.06" x2="3.0" y2="0.18"/></g>
      <text x="2.5" y="0.26" font-family="Barlow, Arial, sans-serif" font-size="0.12" fill="var(--muted)" text-anchor="middle">1 mm</text>
    </svg>"""


def main(out):
    dun = np.loadtxt(PROJECT / "outline-dunlop.csv", delimiter=",")
    gen = np.loadtxt(PROJECT / "outline-351.csv", delimiter=",")
    gen[:, 0] *= WIDTH / (gen[:, 0].max() - gen[:, 0].min())
    gen[:, 1] *= LENGTH / (gen[:, 1].max() - gen[:, 1].min())
    dcx, dcy, dr = tip_circle(dun)
    gcx, gcy, gr = tip_circle(gen)
    wy = dun[np.argmax(dun[:, 0]), 1]          # y of the widest point
    edge = json.loads((PROJECT / "edge-options.json").read_text())
    V = edge["variants"]
    order = ("soft", "bevel", "round", "chamfer")

    photo = data_uri(IMG / "trace-1657.png", 700, "JPEG")
    photo2 = data_uri(IMG / "trace-1656.png", 700, "JPEG")
    render = data_uri(IMG / "pick-v6.png", 1000, "JPEG")
    closeups = {v: data_uri(IMG / f"edge-{v}.png", 700) for v in V}

    panels = "".join(f"""
    <figure class="panel">
      {profile_svg(V[v], edge["first_layer"], edge["layer"])}
      <figcaption><b>{EDGE_LABELS[v][0]}.</b> {EDGE_LABELS[v][1]}</figcaption>
    </figure>""" for v in order)
    shots = "".join(f"""
    <figure class="panel">
      <img src="{closeups[v]}" alt="close-up render of the {v} edge at the tip, from above and from below">
      <figcaption><b>{EDGE_LABELS[v][0]}.</b> Tip seen from above (top) and from underneath (bottom).</figcaption>
    </figure>""" for v in ("sym", "mirror", "soft", "round"))
    chosen = "".join(f"""
    <figure class="panel">
      {profile_svg(V[v], edge["first_layer"], edge["layer"])}
      <figcaption><b>{EDGE_LABELS[v][0]}.</b> {EDGE_LABELS[v][1]}</figcaption>
    </figure>""" for v in ("mirror", "sym"))

    def worst(v):
        w = V[v]["worst_bottom"]
        return f'layer {w["layer"]}: {w["step"]:.2f} mm, {w["angle"]:.0f} degrees off vertical' if w["step"] > 0.005 else "none, the walls stack straight up"

    def grams(v):
        return f'{V[v]["volume_mm3"] * 1.27e-3:.2f} g'

    html = f"""<title>Tortex Pick Trace</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<style>
/* Layout: one column of figures, each figure a bordered sheet like a drawing; numbers in tabular type */
:root {{
  --bg: #f6f4ef; --fg: #1d1b17; --muted: #6b665c; --rule: #d9d4c8; --sheet: #ffffff;
  --accent: #1f5fb8;           /* the Tortex blue of the pick */
  --measured: #1d1b17;         /* the measured outline and the CAD profile */
  --warn: #b4502a;
  --display: "Barlow Condensed", "Arial Narrow", sans-serif;
  --body: "Barlow", "Helvetica Neue", Arial, sans-serif;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #17181b; --fg: #ece8df; --muted: #9b968b; --rule: #34363b; --sheet: #202227;
  --accent: #6aa3ef; --measured: #ece8df; --warn: #e5885e; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #17181b; --fg: #ece8df; --muted: #9b968b; --rule: #34363b; --sheet: #202227;
  --accent: #6aa3ef; --measured: #ece8df; --warn: #e5885e; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font-family: var(--body); line-height: 1.45; }}
main {{ max-width: 980px; margin: 0 auto; padding-block: 28px 56px; padding-inline: 16px; display: grid; gap: 28px; }}
h1 {{ font-family: var(--display); font-weight: 700; font-size: clamp(32px, 6vw, 48px); line-height: 1; margin: 0; text-wrap: balance; }}
h2 {{ font-family: var(--display); font-weight: 600; font-size: 24px; margin: 0 0 8px; text-wrap: balance; }}
p {{ margin: 0; max-width: 66ch; }}
.lede {{ font-size: 17px; }}
.kicker {{ font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }}
figure {{ margin: 0; background: var(--sheet); border: 1px solid var(--rule); padding: 16px; display: grid; gap: 12px; }}
figure img {{ max-width: 100%; display: block; }}
figcaption {{ color: var(--muted); font-size: 14px; max-width: 70ch; }}
figcaption b {{ color: var(--fg); font-weight: 600; }}
.pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
@media (max-width: 640px) {{ .pair {{ grid-template-columns: 1fr; }} }}
.pair > div, .pair > figure {{ min-width: 0; }}
.panel {{ padding: 12px; background: var(--bg); }}
.panel img {{ margin: 0 auto; max-height: 340px; }}
svg {{ width: 100%; height: auto; display: block; }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--rule); vertical-align: top; }}
th {{ font-weight: 500; color: var(--muted); font-size: 13px; letter-spacing: .04em; text-transform: uppercase; }}
td.num {{ text-align: right; white-space: nowrap; }}
.scroll {{ overflow-x: auto; }}
.legend {{ display: flex; gap: 20px; flex-wrap: wrap; font-size: 14px; }}
.legend span::before {{ content: ""; display: inline-block; width: 26px; height: 0; border-top: 3px solid currentColor; vertical-align: middle; margin-right: 8px; }}
.legend .gen {{ color: var(--accent); }} .legend .gen::before {{ border-top-style: dashed; }}
.legend .mea {{ color: var(--measured); }}
.legend .stair::before {{ border-top: 10px solid var(--accent); opacity: .25; }}
.legend .bad::before {{ border-top: 10px solid var(--warn); opacity: .6; }}
.ask {{ border-left: 4px solid var(--warn); padding: 4px 0 4px 14px; display: grid; gap: 8px; }}
.ask li {{ margin: 0; }}
ol {{ margin: 0; padding-left: 20px; display: grid; gap: 6px; max-width: 66ch; }}
.done {{ border-top: 1px solid var(--rule); padding-top: 24px; display: grid; gap: 28px; }}
.note {{ margin-top: 10px; }}
</style>
<main>
<header>
  <div class="kicker">Guitar pick, Dunlop Tortex Standard 1.0 mm</div>
  <h1>The edge, mirrored: what a flat print can carry without support</h1>
</header>
<p class="lede">Mirroring the 1.5 mm bevel underneath runs into the print. The pick lies on the bed, so the underside is built upward layer by layer, and each 0.06 mm layer can only reach about half a 0.22 mm line past the one below it. A 13 degree slope asks for 0.26 mm per layer, more than a whole line, so every layer of that band would be laid in air (the red stair, left). The steepest slope the underside carries is about 38 degrees, which makes the band 0.45 mm wide for the same 0.35 mm drop. That bevel, on both faces with the creases softened, is in the 3MF (right). The only way to get the full 1.5 mm on both faces is to print the pick standing on a snap-off base, which is support by another name, so I have not built it.</p>

<figure>
  <div class="legend"><span class="mea">CAD profile</span><span class="stair">What the printer makes of it, layer by layer (0.1 mm first layer, then 0.06)</span><span class="bad">Layer laid in air</span></div>
  <div class="pair">{chosen}
  </div>
  <figcaption>Cross-section through the tip, first 3 mm from the edge, bed at the bottom, both at the same scale. The stair is the real printed edge: the slicer samples the profile at the middle of each layer. On the printable one, the second layer sits 0.11 mm past the first (half a line, the same as the round profile had) and the band's layers a third of a line.</figcaption>
</figure>

<figure>
  <div class="pair">{panels}
  </div>
  <figcaption>The earlier options at the same scale, for comparison. The 1.5 mm bevel on top only is still a printable choice if you would rather keep that feel on one face.</figcaption>
</figure>

<figure>
  <div class="pair">{shots}
  </div>
  <figcaption>The last 6 mm of the tip, rendered from the STL. Same scale in every panel.</figcaption>
</figure>

<section>
  <h2>Numbers</h2>
  <div class="scroll"><table>
    <tr><th>Profile</th><th>Top face</th><th>Underside</th><th>Rim</th><th>Worst underside overhang</th><th>Weight</th></tr>
    <tr><td>Mirrored bevel, printable <b>(in the 3MF)</b></td><td>0.45 mm wide, drops 0.35 mm (38 degrees), R 0.35 blend</td><td>the same</td><td class="num">{V["sym"]["rim_mm"]:.2f} mm</td><td>{worst("sym")}</td><td class="num">{grams("sym")}</td></tr>
    <tr><td>Mirrored 1.5 mm bevel</td><td>1.5 mm wide, drops 0.35 mm, 5 mm blend</td><td>the same</td><td class="num">{V["mirror"]["rim_mm"]:.2f} mm</td><td>{worst("mirror")}: in air, cannot print flat</td><td class="num">{grams("mirror")}</td></tr>
    <tr><td>1.5 mm bevel on top only</td><td>1.5 mm wide, drops 0.35 mm, 5 mm blend into the face</td><td>45 degrees, 0.35 mm, 0.35 mm blend into the face</td><td class="num">{V["soft"]["rim_mm"]:.2f} mm</td><td>{worst("soft")}</td><td class="num">{grams("soft")}</td></tr>
    <tr><td>Bevel with a crease</td><td>1.5 mm wide, drops 0.35 mm (13 degrees)</td><td>45 degrees, 0.35 mm</td><td class="num">{V["bevel"]["rim_mm"]:.2f} mm</td><td>{worst("bevel")}</td><td class="num">{grams("bevel")}</td></tr>
    <tr><td>Round</td><td>fillet R 0.45</td><td>fillet R 0.45</td><td class="num">{V["round"]["rim_mm"]:.2f} mm</td><td>{worst("round")}</td><td class="num">{grams("round")}</td></tr>
    <tr><td>Chamfer</td><td>45 degrees, 0.45 mm</td><td>45 degrees, 0.45 mm</td><td class="num">{V["chamfer"]["rim_mm"]:.2f} mm</td><td>{worst("chamfer")}</td><td class="num">{grams("chamfer")}</td></tr>
    <tr><td>Square</td><td>flat to the edge</td><td>flat to the edge</td><td class="num">1.00 mm</td><td>{worst("square")}</td><td class="num">{grams("square")}</td></tr>
  </table></div>
  <p class="note">Worst underside overhang is how far one layer's outer wall sits past the layer below, read from the geometry at the slicer's sampling heights; the sliced G-code runs about 0.01 mm higher. Half a line (0.11 mm) is the most the first pick's profiles asked of any layer. Wider symmetric bands were measured too: 0.52 mm (34 degrees) puts the band at 0.089 mm per layer and the second layer at 0.121; 0.60 mm (30 degrees) at 0.103 and 0.137. The 0.45 band keeps every layer under half a line.</p>
</section>

<section class="ask">
  <h2>What I need from you</h2>
  <ol>
    <li>Print the mirrored 0.45 mm bevel as it is in the 3MF, or keep the 1.5 mm bevel on the top face only with the steeper underside. Say which.</li>
    <li>If you want the full 1.5 mm on both faces, the pick has to print standing on a snap-off base along its top edge (a mark to sand under the thumb). That is a base, not support filament, but it is still support. Only on your say-so.</li>
  </ol>
</section>

<div class="done">
<header>
  <div class="kicker">Approved 2026-10-11</div>
  <h2>The outline: traced from your calipers, {WIDTH} x {LENGTH} mm, 4.5 mm tip</h2>
</header>
<p>The outline comes from the second caliper photo (the whole pick visible), scaled to the two readings. The generic 351 from the SVG pack is shown for comparison: same width and length, but its tip is sharper (3.4 mm radius against 4.5 mm on your pick) and its lower sides are about 0.9 mm narrower per side. The model is built from the measured outline, now as a smooth curve rather than a 52-sided polygon.</p>

<figure>
  <div class="pair">
    <div><img src="{photo}" alt="IMG_1657 with the traced outline in red"></div>
    <div><img src="{photo2}" alt="IMG_1656 with the traced outline in red; the top of the pick is hidden under the caliper beam"></div>
  </div>
  <figcaption>Red is the traced edge. Left: IMG_1657, used for the shape (jaws give the {LENGTH} mm length). Right: IMG_1656, where the top of the pick sits under the caliper beam, so it only served to cross-check the tip (4.47 mm there, 4.60 mm on the left photo).</figcaption>
</figure>

<figure>
  <div class="legend"><span class="mea">Measured Dunlop outline (used)</span><span class="gen">Generic 351, scaled to the same size</span></div>
  <svg viewBox="-19 -3 38 37" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Measured outline over the generic 351 outline">
    <g stroke-width="0.12" fill="none">
      <path d="{svg_path(gen)}" stroke="var(--accent)" stroke-dasharray="0.6 0.4"/>
      <path d="{svg_path(dun)}" stroke="var(--measured)" stroke-width="0.25"/>
      <circle cx="{dcx:.2f}" cy="{-dcy:.2f}" r="{dr:.2f}" stroke="var(--measured)" stroke-dasharray="0.25 0.25" stroke-width="0.08"/>
      <circle cx="{gcx:.2f}" cy="{-gcy:.2f}" r="{gr:.2f}" stroke="var(--accent)" stroke-dasharray="0.25 0.25" stroke-width="0.08"/>
      <!-- width at the widest point -->
      <line x1="{-WIDTH/2:.2f}" y1="{-wy:.2f}" x2="{WIDTH/2:.2f}" y2="{-wy:.2f}" stroke="var(--muted)" stroke-width="0.08"/>
      <line x1="{-WIDTH/2:.2f}" y1="{-wy-1.5:.2f}" x2="{-WIDTH/2:.2f}" y2="{-wy+1.5:.2f}" stroke="var(--muted)" stroke-width="0.08"/>
      <line x1="{WIDTH/2:.2f}" y1="{-wy-1.5:.2f}" x2="{WIDTH/2:.2f}" y2="{-wy+1.5:.2f}" stroke="var(--muted)" stroke-width="0.08"/>
      <!-- length -->
      <line x1="16" y1="0" x2="16" y2="{LENGTH:.2f}" stroke="var(--muted)" stroke-width="0.08"/>
      <line x1="15" y1="0" x2="17" y2="0" stroke="var(--muted)" stroke-width="0.08"/>
      <line x1="15" y1="{LENGTH:.2f}" x2="17" y2="{LENGTH:.2f}" stroke="var(--muted)" stroke-width="0.08"/>
    </g>
    <g font-family="Barlow, Arial, sans-serif" font-size="1.4" fill="var(--muted)">
      <text x="0" y="{-wy-0.6:.2f}" text-anchor="middle">{WIDTH} mm</text>
      <text x="16.6" y="{LENGTH/2:.2f}" text-anchor="middle" transform="rotate(-90 16.6 {LENGTH/2:.2f})">{LENGTH} mm</text>
      <text x="{dcx+dr+0.8:.2f}" y="{-dcy+0.5:.2f}" fill="var(--measured)">tip R {dr:.1f}</text>
      <text x="{gcx-gr-0.8:.2f}" y="{-gcy+0.5:.2f}" text-anchor="end" fill="var(--accent)">tip R {gr:.1f}</text>
    </g>
  </svg>
  <figcaption>Both outlines drawn to the same scale. The dotted circles are the best-fit tip radius of each. Where the black line sits outside the blue, your pick is fuller than the generic shape.</figcaption>
</figure>

<figure>
  <img src="{render}" alt="Four rendered views of the modelled pick with the rounded edge">
  <figcaption>The CAD model with the mirrored bevel: {WIDTH} x {LENGTH} x {THICK} mm, flat on the bed. The streaks in the iso view are a shading artifact of the renderer on the flat faces, not geometry.</figcaption>
</figure>

<section>
  <h2>Numbers</h2>
  <div class="scroll"><table>
    <tr><th>Item</th><th>Measured pick</th><th>Generic 351</th><th>Source</th></tr>
    <tr><td>Width</td><td class="num">{WIDTH} mm</td><td class="num">scaled to match</td><td>your calipers, IMG_1656</td></tr>
    <tr><td>Length</td><td class="num">{LENGTH} mm</td><td class="num">scaled to match</td><td>your calipers, IMG_1657</td></tr>
    <tr><td>Tip radius</td><td class="num">{dr:.1f} mm</td><td class="num">{gr:.1f} mm</td><td>circle fit on the traced edge, both photos agree within 0.15 mm</td></tr>
    <tr><td>Widest point</td><td class="num">{-wy:.1f} mm below the top</td><td class="num">8.7 mm</td><td>trace</td></tr>
    <tr><td>Thickness</td><td class="num">{THICK} mm</td><td class="num"></td><td>your calipers</td></tr>
    <tr><td>Material, nozzle</td><td colspan="2">PETG, 0.2 mm nozzle, 0.06 mm layers, flat on the bed, about 0.7 g, 13 min sliced (expect about 20)</td><td>your call, for the smoothest edge</td></tr>
  </table></div>
</section>
</div>
</main>
"""
    Path(out).write_text(html)
    print("wrote", out, round(len(html) / 1024), "KB")


if __name__ == "__main__":
    main(sys.argv[1])
