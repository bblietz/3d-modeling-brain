#!/usr/bin/env python
"""Build cutlist.html, the shop page, from cutlist.csv and the part drawings.

Re-run after every `EXPORT=1 drawer_bench.py`, `part_drawings.py`,
`hero_shot.py` and `assembly_shots.py` (both with the viewer open), then
`make_pdf.py` and republish the page (same URL) with the part PNGs,
images/hero.png, images/assembly/*.png and cutlist.pdf. The page starts
with a full image of the bench from the CAD viewer (Brian, 2026-09-28:
always), then a case section and a drawer section, each grouped by
material in cutting order; every row shows inches to the nearest 1/32 (no
metric: Brian, 2026-09-28), the machining notes, its shop drawing (tap to
zoom), and a tick box (per device, localStorage). After the hardware list
comes the assembly section (Brian, 2026-10-07): an exploded view, then one
numbered step per row with its text and a viewer image of the parts going
in, plus sub-assembly explosions where a step builds one.

Usage: .venv/bin/python projects/Drawer-bench/make_cutlist_page.py
"""
import csv
import html
import os
import sys
from datetime import date

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Drawer-bench"
sys.path.insert(0, f"{VAULT}/scripts")
sys.path.insert(0, PROJ)
from cutlist import inch_frac  # noqa: E402
from assembly_shots import STEPS  # noqa: E402  (file stem, title, prefixes, text); runs the model's checks once

ASSEMBLY_DIR = "images/assembly"
EXPLODED = f"{ASSEMBLY_DIR}/exploded.png"
SUBS = {   # step stem -> (file, caption) of the sub-assembly built in that step
    "step-01": ("side-exploded.png", "one side frame pulled apart, seen from inside: the panel's housed edges "
                                     "and notched bottom corners, the posts' stopped grooves and dowel bores"),
    "step-02": ("rear-exploded.png", "the back with its cleat lifted off the top edge and the bottom pulled "
                                     "out of the back's groove"),
    "step-05": ("drawer-exploded.png", "one drawer box pulled apart: sides, front and back, 1/4 bottom"),
}
PDF = "cutlist.pdf"

ORDER = ["soft maple", "3/4 ply", "1/2 ply", "1/4 ply", "maple butcherblock (Boos match)"]
CASE_LABEL = {
    "soft maple": "Soft maple: posts, rails, cleat",
    "3/4 ply": "3/4 in plywood (measure the sheet): sides and back",
    "1/2 ply": "1/2 in plywood (measure the sheet): case bottom",
    "maple butcherblock (Boos match)": "Butcherblock top (purchased, Boos match)",
}
DRAWER_LABEL = {
    "soft maple": "Drawer fronts, soft maple",
    "1/2 ply": "Drawer boxes, 1/2 in plywood (measure the sheet)",
    "1/4 ply": "Drawer bottoms, 1/4 in plywood (measure the sheet)",
}
TEMPLATE_TAG = "not a plain rectangular blank"
HARDWARE = [
    ("2 pairs", "Blum TANDEM plus BLUMOTION 563H4570B undermount slides, 18 in class",
     "confirm the purchased spec against the 563H sheet before boring the boxes"),
    ("2 pairs", "Blum rear mounting brackets 295.3750.02", "on the back panel, at runner height"),
    ("2 sets", "Blum locking devices for the box fronts", "bored with the T65.1600.01 template"),
    ("6", "3/8 in dowels, 2 in long", "front rails to front posts, one each end, 1 in into each part"),
    ("6", "figure-8 desktop fasteners with #8 x 5/8 in screws (12)",
     "three on rail_top, three on cleat_rear, in the offset 5/8 in recesses"),
    ("4 to 5", "#8 x 1-1/4 in screws, countersunk", "cleat_rear to the inside of the back, from the cleat side"),
    ("as needed", "screws for the drawer fronts, through slotted holes from inside the boxes", "pulls undecided"),
]


def is_drawer(part):
    return part.startswith("drawer_") or part in ("front_bot", "front_top")


def load_rows():
    with open(f"{PROJ}/cutlist.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("thickness_mm", "width_mm", "length_mm"):
            r[k] = float(r[k])
        r["qty"] = int(r["qty"])
        note = r["notes"]
        r["template"] = TEMPLATE_TAG in note
        if r["template"]:
            note = note.split(" ; " + TEMPLATE_TAG)[0].strip()
        r["note"] = note
        r["drawing"] = f"images/parts/{r['part'].split('/')[0]}.png"
        r["has_drawing"] = os.path.exists(f"{PROJ}/{r['drawing']}")
    return rows


def dims(r):
    return " x ".join(inch_frac(r[k], 32) for k in ("thickness_mm", "width_mm", "length_mm"))


def part_li(r):
    pid = "cut-" + r["part"].replace("/", "-")
    din = dims(r)
    chip = '<span class="chip warn">see drawing: not a plain rectangle</span>' if r["template"] else ""
    fig = (f'<figure class="dwg" tabindex="0"><img src="{r["drawing"]}" alt="shop drawing of {html.escape(r["part"])}" loading="lazy">'
           f'<figcaption>tap to zoom</figcaption></figure>') if r["has_drawing"] else ""
    return f"""
      <li class="part">
        <input type="checkbox" id="{pid}" class="tick">
        <div class="body">
          <label for="{pid}">
            <div class="line1"><span class="qty mono">{r['qty']}&times;</span><span class="name mono">{html.escape(r['part'])}</span>{chip}</div>
            <div class="dims mono"><b>{html.escape(din)}</b></div>
            <p class="note">{html.escape(r['note'])}</p>
          </label>{fig}
        </div>
      </li>"""


def group_section(label, rows):
    n_parts = sum(r["qty"] for r in rows)
    area = sum(r["qty"] * r["width_mm"] * r["length_mm"] for r in rows) / 1e6 * 10.7639
    first = part_li(rows[0])
    rest = "".join(part_li(r) for r in rows[1:])
    rest_html = f"\n      <ul class=\"parts\">{rest}\n      </ul>" if rest else ""
    # the heading and the first row share one block so a page break can never strand the heading
    return f"""
    <section class="group">
      <div class="keep">
        <div class="ghead">
          <h3>{html.escape(label)}</h3>
          <span class="gsum mono">{n_parts} pieces &middot; {area:.1f} sq ft face, no kerf or waste</span>
        </div>
        <ul class="parts">{first}
        </ul>
      </div>{rest_html}
    </section>"""


HERO = "images/hero.png"


def sub_figure(fname, caption):
    return (f'<figure class="dwg sfig sub" tabindex="0"><img src="{ASSEMBLY_DIR}/{fname}" alt="{html.escape(caption)}" loading="lazy">'
            f'<figcaption>{html.escape(caption)}; tap to zoom</figcaption></figure>')


def step_li(stem, title, text):
    img = f"{ASSEMBLY_DIR}/{stem}.png"
    assert os.path.exists(f"{PROJ}/{img}"), f"{img} missing: run assembly_shots.py with the CAD viewer open"
    extra = sub_figure(*SUBS[stem]) if stem in SUBS else ""
    return (f'<li class="step"><div class="stext"><h3>{html.escape(title)}</h3><p>{html.escape(text)}</p></div>'
            f'<figure class="dwg sfig" tabindex="0"><img src="{img}" alt="{html.escape(title)}: parts added in this step in wood colors, the rest grey" loading="lazy">'
            f'<figcaption>new parts in wood colors; tap to zoom</figcaption></figure>{extra}</li>')


def build():
    assert os.path.exists(f"{PROJ}/{HERO}"), f"{HERO} missing: run hero_shot.py with the CAD viewer open"
    assert os.path.exists(f"{PROJ}/{EXPLODED}"), f"{EXPLODED} missing: run assembly_shots.py with the CAD viewer open"
    rows = load_rows()
    case = [r for r in rows if not is_drawer(r["part"])]
    drawers = [r for r in rows if is_drawer(r["part"])]
    case_html = "".join(group_section(CASE_LABEL.get(m, m), [r for r in case if r["material"] == m])
                        for m in ORDER if any(r["material"] == m for r in case))
    drawer_html = "".join(group_section(DRAWER_LABEL.get(m, m), [r for r in drawers if r["material"] == m])
                          for m in ORDER if any(r["material"] == m for r in drawers))
    total_pieces = sum(r["qty"] for r in rows)
    hw = "".join(
        f'<li><span class="hqty mono">{html.escape(q)}</span><div><b>{html.escape(what)}</b><span class="hnote">{html.escape(note)}</span></div></li>'
        for q, what, note in HARDWARE)
    steps = "".join(step_li(stem, title, text) for stem, title, _prefixes, text in STEPS)
    today = date.today().isoformat()
    return PAGE.format(case=case_html, drawers=drawer_html, hardware=hw, steps=steps, total=total_pieces, today=today,
                       n_case=sum(r["qty"] for r in case), n_drawers=sum(r["qty"] for r in drawers), hero=HERO,
                       exploded=EXPLODED, n_steps=len(STEPS), pdf=PDF)


PAGE = """<title>Drawer Bench Cut List</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
  :root {{
    --bg: #f7f4ee; --surface: #fffdf9; --ink: #24201b; --muted: #6d655a; --line: #e3dccf;
    --accent: #d96a12; --accent-ink: #8a4108;
    --warn-bg: #fbe9d7; --warn-ink: #8a4108; --note-bg: #ece7dd; --note-ink: #4d463c;
    --done: #9a9184; --paper: #f6f1e8;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      color-scheme: dark;
      --bg: #1b1916; --surface: #24211d; --ink: #ece6dc; --muted: #a79e91; --line: #3a352e;
      --accent: #f08a3a; --accent-ink: #f6b27e;
      --warn-bg: #46301c; --warn-ink: #f4c79c; --note-bg: #302c26; --note-ink: #cfc6b8;
      --done: #6f675c;
    }}
  }}
  :root[data-theme="dark"] {{
    color-scheme: dark;
    --bg: #1b1916; --surface: #24211d; --ink: #ece6dc; --muted: #a79e91; --line: #3a352e;
    --accent: #f08a3a; --accent-ink: #f6b27e;
    --warn-bg: #46301c; --warn-ink: #f4c79c; --note-bg: #302c26; --note-ink: #cfc6b8;
    --done: #6f675c;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Archivo, "Helvetica Neue", Arial, sans-serif;
         font-size: 16px; line-height: 1.45; padding-inline: 16px; padding-block: 24px 72px; }}
  .wrap {{ max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 30px; }}
  .mono {{ font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace; font-variant-numeric: tabular-nums; }}
  .eyebrow {{ font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--accent-ink); font-weight: 600; margin: 0 0 6px; }}
  h1 {{ font-size: clamp(28px, 5vw, 38px); line-height: 1.08; margin: 0 0 10px; letter-spacing: -.01em; text-wrap: balance; }}
  header p {{ margin: 0; max-width: 62ch; color: var(--muted); font-size: 15px; }}
  .status {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; margin-top: 14px; font-size: 14px; }}
  .status .count {{ font-weight: 600; }}
  button.reset {{ font: inherit; font-size: 13px; color: var(--accent-ink); background: none; border: 1px solid var(--line); border-radius: 999px; padding: 4px 12px; cursor: pointer; }}
  button.reset:focus-visible, .tick:focus-visible + .body, .dwg:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
  .flag {{ background: var(--warn-bg); color: var(--warn-ink); border-radius: 8px; padding: 10px 14px; font-size: 14.5px; max-width: 72ch; }}
  .flag b {{ font-weight: 600; }}
  .big {{ display: flex; flex-direction: column; gap: 18px; }}
  .big > h2 {{ font-size: 24px; margin: 0; padding-bottom: 8px; border-bottom: 3px solid var(--accent); }}
  .big > h2 small {{ font-size: 14px; font-weight: 500; color: var(--muted); margin-left: 10px; }}
  .group {{ display: flex; flex-direction: column; gap: 4px; }}
  .ghead {{ display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 4px 16px; border-bottom: 2px solid var(--ink); padding-bottom: 6px; }}
  h3 {{ font-size: 18px; margin: 0; }}
  .gsum {{ font-size: 12.5px; color: var(--muted); }}
  ul.parts {{ list-style: none; margin: 0; padding: 0; }}
  .part {{ display: grid; grid-template-columns: 28px 1fr; gap: 12px; padding: 14px 0; border-bottom: 1px solid var(--line); align-items: start; }}
  .tick {{ width: 22px; height: 22px; margin: 4px 0 0 2px; accent-color: var(--accent); cursor: pointer; }}
  .body {{ display: flex; flex-direction: column; gap: 10px; min-width: 0; }}
  .part label {{ display: flex; flex-direction: column; gap: 4px; cursor: pointer; min-width: 0; }}
  .line1 {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }}
  .qty {{ font-weight: 600; color: var(--accent-ink); }}
  .name {{ font-weight: 600; font-size: 15px; }}
  .chip {{ font-size: 11.5px; padding: 2px 8px; border-radius: 999px; background: var(--note-bg); color: var(--note-ink); }}
  .chip.warn {{ background: var(--warn-bg); color: var(--warn-ink); }}
  .dims {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; }}
  .dims b {{ font-size: 21px; font-weight: 600; letter-spacing: -.01em; }}
  .note {{ margin: 0; font-size: 13.5px; color: var(--note-ink); overflow-wrap: anywhere; }}
  .dwg {{ margin: 0; background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 6px; cursor: zoom-in; display: flex; flex-direction: column; gap: 4px; }}
  .dwg img {{ width: 100%; height: auto; display: block; }}
  .dwg figcaption {{ font-size: 11.5px; color: var(--muted); text-align: right; }}
  .hero {{ background: #fff; }}
  .hero img {{ border-radius: 4px; }}
  .tick:checked + .body {{ color: var(--done); }}
  .tick:checked + .body .name, .tick:checked + .body .dims b {{ text-decoration: line-through; text-decoration-thickness: 2px; }}
  .tick:checked + .body .qty, .tick:checked + .body .note {{ color: var(--done); }}
  .tick:checked + .body .dwg {{ opacity: .55; }}
  .hw {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }}
  .hw li {{ display: grid; grid-template-columns: 72px 1fr; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--line); font-size: 14.5px; }}
  .hw li div {{ display: flex; flex-direction: column; gap: 2px; }}
  .hqty {{ font-weight: 600; color: var(--accent-ink); }}
  .hnote {{ font-size: 13px; color: var(--muted); }}
  .foot {{ font-size: 13px; color: var(--muted); max-width: 72ch; }}
  #lightbox {{ position: fixed; inset: 0; background: rgba(15, 12, 8, .9); display: none; place-items: center; padding: 12px; z-index: 10; cursor: zoom-out; overflow: auto; }}
  #lightbox.open {{ display: grid; }}
  #lightbox img {{ max-width: 100%; max-height: 94vh; background: var(--paper); border-radius: 6px; }}
  a.pdf {{ font-size: 13px; color: var(--accent-ink); border: 1px solid var(--line); border-radius: 999px; padding: 4px 12px; text-decoration: none; }}
  ol.steps {{ margin: 0; padding: 0; list-style: none; counter-reset: step; display: flex; flex-direction: column; }}
  .step {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: 12px 20px; padding: 16px 0; border-bottom: 1px solid var(--line); align-items: start; }}
  .step .stext h3 {{ font-size: 17px; margin: 0 0 6px; }}
  .step .stext h3::before {{ counter-increment: step; content: counter(step) ". "; color: var(--accent-ink); }}
  .step .stext p {{ margin: 0; font-size: 14.5px; line-height: 1.5; }}
  .step .sfig {{ margin: 0; background: #fff; }}
  .step .sub {{ grid-column: 1 / -1; }}
  @media (max-width: 720px) {{ .step {{ grid-template-columns: 1fr; }} }}
  @media (max-width: 420px) {{ .dims b {{ font-size: 19px; }} .hw li {{ grid-template-columns: 60px 1fr; }} }}
  @media print {{
    @page {{ size: letter; margin: 0.5in 0.5in 0.6in; }}
    html, body {{ background: #fff; color: #000; font-size: 11pt; }}
    .wrap {{ max-width: none; padding: 0; margin: 0; gap: 14px; }}
    .tick, .status, figcaption, #lightbox {{ display: none !important; }}
    header p {{ max-width: none; }}
    .flag {{ border: 1px solid #c8782a; background: #fff3e6; break-inside: avoid; }}
    .big {{ break-before: page; gap: 10px; }}
    .big > h2 {{ font-size: 20px; }}
    .group {{ break-inside: auto; }}
    .keep {{ break-inside: avoid; }}
    .part {{ grid-template-columns: 1fr; gap: 6px; padding: 8px 0; break-inside: avoid; }}
    .part label {{ cursor: default; }}
    .dwg {{ border: 1px solid #ccc; padding: 4px; background: #fff; break-inside: avoid; cursor: default; }}
    .dwg img {{ max-height: 4.6in; width: auto; max-width: 100%; margin: 0 auto; }}
    .hero img {{ max-height: 5in; }}
    .hw li {{ break-inside: avoid; }}
    .step {{ grid-template-columns: 1fr 1.3fr; break-inside: avoid; padding: 10px 0; }}
    .step .sfig img {{ max-height: 3.2in; }}
    .step .sub img {{ max-height: 4in; }}
    .foot {{ font-size: 9pt; }}
  }}
</style>

<div class="wrap">
  <figure class="dwg hero" tabindex="0"><img src="{hero}" alt="the whole bench, front-left view from the CAD viewer"><figcaption>the whole bench, from the CAD viewer; tap to zoom</figcaption></figure>
  <header>
    <p class="eyebrow">Drawer bench &middot; 40 x 24 x 19-5/8 in</p>
    <h1>Drawer Bench Cut List</h1>
    <p>{total} pieces: the case first, then the drawers, each grouped by material in cutting order. Inches to the nearest 1/32. Every part has a shop drawing with its grooves, rabbets, notches and bores located from the blank's own edges; tap a drawing to zoom. Tap a row to tick it off; ticks stay on this phone only. The assembly order with a picture per step is at the end.</p>
    <div class="status"><span class="count" id="count"></span><button class="reset" id="reset" type="button">Clear ticks</button><a class="pdf" href="{pdf}">PDF for the shop</a></div>
  </header>

  <div class="flag"><b>Provisional.</b> Every groove, rabbet and dado that takes plywood is sized to the sheet's real thickness and says "measure". Measure the sheets you bought, put the numbers in the model and re-run it before cutting joinery. The top's overhang and edge profile still wait on the island; the slide numbers wait on the purchased sheet.</div>

  <div class="big">
    <h2>Case<small>{n_case} pieces</small></h2>{case}
  </div>

  <div class="big">
    <h2>Drawers<small>{n_drawers} pieces</small></h2>{drawers}
  </div>

  <div class="big">
    <h2>Hardware<small>from the design; not in the cut list</small></h2>
    <ul class="hw">{hardware}</ul>
  </div>

  <div class="big">
    <h2>Assembly<small>{n_steps} steps, in order</small></h2>
    <figure class="dwg hero" tabindex="0"><img src="{exploded}" alt="the whole bench pulled apart: top, side frames, back with its cleat, bottom, rails, drawer boxes and fronts"><figcaption>everything pulled apart along the direction it goes in; tap to zoom</figcaption></figure>
    <ol class="steps">{steps}</ol>
  </div>

  <p class="foot">Generated {today} from <span class="mono">projects/Drawer-bench/cutlist.csv</span> and <span class="mono">images/parts/</span>, which <span class="mono">drawer_bench.py</span> and <span class="mono">part_drawings.py</span> write on every export; every drawn cut is probed against the CAD solid before its sheet is written. The bench image at the top and the assembly pictures are screenshots of the CAD viewer (<span class="mono">hero_shot.py</span>, <span class="mono">assembly_shots.py</span>); the PDF is this page printed by <span class="mono">make_pdf.py</span>. Part names match the CAD viewer.</p>
</div>

<div id="lightbox" role="dialog" aria-label="Enlarged drawing" aria-hidden="true"><img id="lightbox-img" alt=""></div>

<script>
  (function () {{
    var KEY = 'drawer-bench-cutlist-ticks';
    var ticks = document.querySelectorAll('.tick');
    var count = document.getElementById('count');
    function load() {{ try {{ return JSON.parse(localStorage.getItem(KEY) || '[]'); }} catch (e) {{ return []; }} }}
    function save(ids) {{ try {{ localStorage.setItem(KEY, JSON.stringify(ids)); }} catch (e) {{}} }}
    function update() {{
      var ids = [];
      ticks.forEach(function (t) {{ if (t.checked) ids.push(t.id); }});
      count.textContent = ids.length + ' of ' + ticks.length + ' rows cut';
      save(ids);
    }}
    var saved = load();
    ticks.forEach(function (t) {{
      if (saved.indexOf(t.id) !== -1) t.checked = true;
      t.addEventListener('change', update);
    }});
    document.getElementById('reset').addEventListener('click', function () {{
      ticks.forEach(function (t) {{ t.checked = false; }});
      update();
    }});
    update();

    var box = document.getElementById('lightbox');
    var img = document.getElementById('lightbox-img');
    function open(fig) {{
      var src = fig.querySelector('img');
      img.src = src.src; img.alt = src.alt;
      box.classList.add('open'); box.setAttribute('aria-hidden', 'false');
    }}
    function close() {{ box.classList.remove('open'); box.setAttribute('aria-hidden', 'true'); img.removeAttribute('src'); }}
    document.querySelectorAll('.dwg').forEach(function (fig) {{
      fig.addEventListener('click', function (e) {{ e.preventDefault(); open(fig); }});
      fig.addEventListener('keydown', function (e) {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); open(fig); }} }});
    }});
    box.addEventListener('click', close);
    document.addEventListener('keydown', function (e) {{ if (e.key === 'Escape' && box.classList.contains('open')) close(); }});
  }})();
</script>
"""

if __name__ == "__main__":
    out = f"{PROJ}/cutlist.html"
    with open(out, "w") as f:
        f.write(build())
    print("wrote", os.path.relpath(out, VAULT))
