"""Luggage tag options page: to-scale SVG of the real geometry, front and back,
for each variant (size x eyelet), plus the text sizes and stroke widths.
Writes projects/Logodude/tag-options.html. Each variant runs logodude_tag.py
in a subprocess with TAG_IN / EYELET set and reads the 2D geometry it dumps."""
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
PY = HERE.parent.parent / ".venv/bin/python"
DUMP = pathlib.Path(os.environ.get("DUMP_DIR", HERE / "pipeline/build-tag/options"))
DUMP.mkdir(parents=True, exist_ok=True)

VARIANTS = [  # (key, TAG_IN, EYELET, caption)
    ("A", "3.0", "hole", "A: 3 in, round eyelet (built, 0.4 nozzle)"),
    ("B", "3.0", "slot", "B: 3 in, strap slot"),
    ("C", "3.0", "punch", "C: 3 in, hole punched through the forehead"),
    ("D", "3.5", "hole", "D: 3.5 in, round eyelet (the 0.6 nozzle size)"),
]


def run(key, tag_in, eyelet):
    out = DUMP / f"{key}.json"
    if not out.exists():
        env = dict(os.environ, TAG_IN=tag_in, EYELET=eyelet, DUMP_2D=str(out), NOZZLE="0.6" if tag_in == "3.5" else "0.4")
        env.pop("SHOW", None); env.pop("EXPORT", None)
        subprocess.run([str(PY), str(HERE / "logodude_tag.py")], env=env, check=True, capture_output=True)
    return json.loads(out.read_text())


def path(rings):
    d = ""
    for r in rings:
        d += "M" + " L".join(f"{x:.2f},{-y:.2f}" for x, y in r) + " Z "
    return d


def poly_path(polys):
    return path([ring for p in polys for ring in [p["outer"]] + p["holes"]])


def svg(g, back, w=92, h=100):
    """One tag, to scale (1 mm = 1 unit), front or back view."""
    x0, y0, x1, y1 = g["bounds"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    flip = "scale(-1,1) " if back else ""
    body = (f'<path d="{poly_path(g["backer"])}" fill="#f4f4f2" stroke="#9a9a96" stroke-width="0.3" fill-rule="evenodd"/>')
    if back:
        body += f'<path d="{poly_path(g["text"])}" fill="#1d1d1f" fill-rule="evenodd"/>'
    else:
        body += f'<path d="{poly_path(g["ink"])}" fill="#1d1d1f" fill-rule="evenodd"/>'
    return (f'<svg viewBox="{-w/2:.1f} {-h/2:.1f} {w} {h}" width="{w*3.2:.0f}" height="{h*3.2:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg"><g transform="{flip}translate({-cx:.2f},{cy:.2f})">{body}</g></svg>')


def card(g, caption):
    x0, y0, x1, y1 = g["bounds"]
    lines = "".join(f"<tr><td>{t}</td><td>{c:.1f} mm caps</td><td>{wd:.1f} mm wide</td><td>{sw:.2f} mm strokes</td></tr>"
                    for t, c, wd, sw in g["lines"])
    return f'''<section class="card">
  <h2>{caption}</h2>
  <div class="views">
    <figure>{svg(g, False)}<figcaption>front, ink up</figcaption></figure>
    <figure>{svg(g, True)}<figcaption>back, as you read it (flipped over)</figcaption></figure>
  </div>
  <p class="dims">{(x1-x0)/25.4:.2f} x {(y1-y0)/25.4:.2f} in overall ({x1-x0:.0f} x {y1-y0:.0f} mm), {g["thick"]:.2f} mm thick, hole {g["hole"]}.
  Face strokes {g["face_strokes"][0]:.2f} to {g["face_strokes"][1]:.2f} mm.</p>
  <table>{lines}</table>
</section>'''


def main():
    cards = []
    for key, tag_in, eyelet, caption in VARIANTS:
        g = run(key, tag_in, eyelet)
        cards.append(card(g, caption))
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Logo Dude tag options</title>
<style>
:root{{--bg:#f7f7f5;--fg:#1d1d1f;--muted:#6b6b68;--card:#fff;--line:#e2e2df}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#161616;--fg:#f0f0ee;--muted:#a4a4a0;--card:#202020;--line:#333}}}}
:root[data-theme="dark"]{{--bg:#161616;--fg:#f0f0ee;--muted:#a4a4a0;--card:#202020;--line:#333}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
h1{{font-size:22px;margin:0 0 4px}} .lead{{color:var(--muted);margin:0 0 20px;max-width:70ch}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:0 0 20px}}
h2{{font-size:17px;margin:0 0 8px}}
.views{{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start}}
figure{{margin:0}} figcaption{{color:var(--muted);font-size:13px;text-align:center}}
svg{{max-width:100%;height:auto;background:#eceae6;border-radius:8px}}
.dims{{margin:10px 0 6px}} table{{border-collapse:collapse;font-size:13px}} td{{padding:2px 12px 2px 0;color:var(--muted)}} td:first-child{{color:var(--fg);font-weight:600}}
.scale{{color:var(--muted);font-size:13px}}
</style></head><body>
<h1>Logo Dude luggage tag: options</h1>
<p class="lead">All drawings are to one scale from the CAD geometry (1 mm = 3.2 px). Front shows the raised black ink; back shows the text the way you read it after flipping the tag over, inlaid flush in black. Built default: A, for the 0.4 nozzle. D is what the 0.6 nozzle needs: a 3.5 in tag with 5 to 6 mm letters.</p>
{"".join(cards)}
</body></html>'''
    (HERE / "tag-options.html").write_text(html)
    print("wrote", HERE / "tag-options.html")


if __name__ == "__main__":
    main()
