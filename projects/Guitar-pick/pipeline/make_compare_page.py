"""Build the HTML page that shows Brian the traced Dunlop outline against the
generic 351 and the CAD model, so he can sign off against pictures.

    .venv/bin/python projects/Guitar-pick/pipeline/make_compare_page.py <out.html>

Reads outline-dunlop.csv, outline-351.csv and the PNGs in images/ (run
trace_photo.py and guitar_pick.py + render_stl.py first).
"""
import base64
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
IMG = PROJECT / "images"
WIDTH, LENGTH, THICK = 26.19, 30.38, 1.0


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


def main(out):
    dun = np.loadtxt(PROJECT / "outline-dunlop.csv", delimiter=",")
    gen = np.loadtxt(PROJECT / "outline-351.csv", delimiter=",")
    gen[:, 0] *= WIDTH / (gen[:, 0].max() - gen[:, 0].min())
    gen[:, 1] *= LENGTH / (gen[:, 1].max() - gen[:, 1].min())
    dcx, dcy, dr = tip_circle(dun)
    gcx, gcy, gr = tip_circle(gen)
    wy = dun[np.argmax(dun[:, 0]), 1]          # y of the widest point

    photo = data_uri(IMG / "trace-1657.png", 700, "JPEG")
    photo2 = data_uri(IMG / "trace-1656.png", 700, "JPEG")
    render = data_uri(IMG / "pick-v3.png", 1000, "JPEG")

    html = f"""<title>Tortex Pick Trace</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500&display=swap">
<style>
/* Layout: one column of figures, each figure a bordered sheet like a drawing; numbers in tabular type */
:root {{
  --bg: #f6f4ef; --fg: #1d1b17; --muted: #6b665c; --rule: #d9d4c8; --sheet: #ffffff;
  --accent: #1f5fb8;           /* the Tortex blue of the pick, used for the generic outline */
  --measured: #1d1b17;         /* the measured outline */
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
.pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
@media (max-width: 640px) {{ .pair {{ grid-template-columns: 1fr; }} }}
.pair > div {{ min-width: 0; }}
svg {{ width: 100%; height: auto; display: block; }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--rule); vertical-align: top; }}
th {{ font-weight: 500; color: var(--muted); font-size: 13px; letter-spacing: .04em; text-transform: uppercase; }}
td.num {{ text-align: right; white-space: nowrap; }}
.legend {{ display: flex; gap: 20px; flex-wrap: wrap; font-size: 14px; }}
.legend span::before {{ content: ""; display: inline-block; width: 26px; height: 0; border-top: 3px solid currentColor; vertical-align: middle; margin-right: 8px; }}
.legend .gen {{ color: var(--accent); }} .legend .gen::before {{ border-top-style: dashed; }}
.legend .mea {{ color: var(--measured); }}
.ask {{ border-left: 4px solid var(--warn); padding: 4px 0 4px 14px; display: grid; gap: 8px; }}
.ask li {{ margin: 0; }}
ol {{ margin: 0; padding-left: 20px; display: grid; gap: 6px; max-width: 66ch; }}
</style>
<main>
<header>
  <div class="kicker">Guitar pick, Dunlop Tortex Standard 1.0 mm</div>
  <h1>Traced from your calipers: {WIDTH} x {LENGTH} mm, 4.5 mm tip</h1>
</header>
<p class="lede">The outline below comes from the second caliper photo (the whole pick visible), scaled to the two readings. The generic 351 from the SVG pack is shown for comparison: same width and length, but its tip is sharper (3.4 mm radius against 4.5 mm on your pick) and its lower sides are about 0.9 mm narrower per side. The model is built from the measured outline.</p>

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
  <img src="{render}" alt="Four rendered views of the modelled pick">
  <figcaption>The CAD model built from the measured outline: {WIDTH} x {LENGTH} x {THICK} mm, flat on the bed. The streaks in the iso view are a shading artifact of the renderer on the flat faces, not geometry.</figcaption>
</figure>

<section>
  <h2>Numbers</h2>
  <table>
    <tr><th>Item</th><th>Measured pick</th><th>Generic 351</th><th>Source</th></tr>
    <tr><td>Width</td><td class="num">{WIDTH} mm</td><td class="num">scaled to match</td><td>your calipers, IMG_1656</td></tr>
    <tr><td>Length</td><td class="num">{LENGTH} mm</td><td class="num">scaled to match</td><td>your calipers, IMG_1657</td></tr>
    <tr><td>Tip radius</td><td class="num">{dr:.1f} mm</td><td class="num">{gr:.1f} mm</td><td>circle fit on the traced edge, both photos agree within 0.15 mm</td></tr>
    <tr><td>Widest point</td><td class="num">{-wy:.1f} mm below the top</td><td class="num">8.7 mm</td><td>trace</td></tr>
    <tr><td>Thickness</td><td class="num">{THICK} mm assumed</td><td class="num"></td><td>not measured yet</td></tr>
    <tr><td>Material, nozzle</td><td colspan="2">PETG, 0.4 mm nozzle, flat on the bed, about 0.74 g</td><td>your picks</td></tr>
  </table>
</section>

<section class="ask">
  <h2>What I need from you</h2>
  <ol>
    <li>One more caliper reading: the pick's thickness, anywhere on the flat. Tortex 1.0 picks usually measure 0.95 to 1.05 mm and the print will be set to that number.</li>
    <li>Look at the black outline against your pick. If a region looks off, say where (tip, lower sides, shoulders, top) and I will re-trace there.</li>
    <li>If it looks right, say go and I build the Bambu 3MF: one pick, PETG, 0.4 mm nozzle, skirt on.</li>
  </ol>
</section>
</main>
"""
    Path(out).write_text(html)
    print("wrote", out, f"{Path(out).stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main(sys.argv[1])
