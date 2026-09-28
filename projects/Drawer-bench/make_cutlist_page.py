#!/usr/bin/env python
"""Build cutlist.html, the shop page, from cutlist.csv and the part drawings.

Re-run after every `EXPORT=1 drawer_bench.py` and `part_drawings.py`, then
republish the page (same URL). The page has a case section and a drawer
section, each grouped by material in cutting order; every row shows inches
large with mm beside, the machining notes, its shop drawing (tap to zoom),
and a tick box (per device, localStorage).

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
from cutlist import inch_frac  # noqa: E402

ORDER = ["soft maple", "ply 18mm", "ply 12mm", "ply 6mm", "maple butcherblock (Boos match)"]
CASE_LABEL = {
    "soft maple": "Soft maple: posts, rails, cleat",
    "ply 18mm": "3/4 in plywood (18 mm nominal, measure): sides and back",
    "ply 12mm": "1/2 in plywood (12 mm nominal, measure): case bottom",
    "maple butcherblock (Boos match)": "Butcherblock top (purchased, Boos match)",
}
DRAWER_LABEL = {
    "soft maple": "Drawer fronts, soft maple",
    "ply 12mm": "Drawer boxes, 1/2 in plywood (12 mm nominal, measure)",
    "ply 6mm": "Drawer bottoms, 1/4 in plywood (6 mm nominal, measure)",
}
TEMPLATE_TAG = "not a plain rectangular blank"
HARDWARE = [
    ("2 pairs", "Blum TANDEM plus BLUMOTION 563H4570B undermount slides, 18 in class (471 mm runner)",
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
    t, w, l = r["thickness_mm"], r["width_mm"], r["length_mm"]
    return (f"{inch_frac(t)} x {inch_frac(w)} x {inch_frac(l)}", f"{t:g} x {w:g} x {l:g} mm")


def part_li(r):
    pid = "cut-" + r["part"].replace("/", "-")
    din, dmm = dims(r)
    chip = '<span class="chip warn">see drawing: not a plain rectangle</span>' if r["template"] else ""
    fig = (f'<figure class="dwg" tabindex="0"><img src="{r["drawing"]}" alt="shop drawing of {html.escape(r["part"])}" loading="lazy">'
           f'<figcaption>tap to zoom</figcaption></figure>') if r["has_drawing"] else ""
    return f"""
      <li class="part">
        <input type="checkbox" id="{pid}" class="tick">
        <div class="body">
          <label for="{pid}">
            <div class="line1"><span class="qty mono">{r['qty']}&times;</span><span class="name mono">{html.escape(r['part'])}</span>{chip}</div>
            <div class="dims mono"><b>{html.escape(din)}</b><span class="mm">{html.escape(dmm)}</span></div>
            <p class="note">{html.escape(r['note'])}</p>
          </label>{fig}
        </div>
      </li>"""


def group_section(label, rows):
    n_parts = sum(r["qty"] for r in rows)
    area = sum(r["qty"] * r["width_mm"] * r["length_mm"] for r in rows) / 1e6
    items = "".join(part_li(r) for r in rows)
    return f"""
    <section class="group">
      <div class="ghead">
        <h3>{html.escape(label)}</h3>
        <span class="gsum mono">{n_parts} pieces &middot; {area:.2f} m&sup2; face, no kerf or waste</span>
      </div>
      <ul class="parts">{items}
      </ul>
    </section>"""


def build():
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
    today = date.today().isoformat()
    return PAGE.format(case=case_html, drawers=drawer_html, hardware=hw, total=total_pieces, today=today,
                       n_case=sum(r["qty"] for r in case), n_drawers=sum(r["qty"] for r in drawers))


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
  .dims .mm {{ font-size: 12.5px; color: var(--muted); }}
  .note {{ margin: 0; font-size: 13.5px; color: var(--note-ink); overflow-wrap: anywhere; }}
  .dwg {{ margin: 0; background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 6px; cursor: zoom-in; display: flex; flex-direction: column; gap: 4px; }}
  .dwg img {{ width: 100%; height: auto; display: block; }}
  .dwg figcaption {{ font-size: 11.5px; color: var(--muted); text-align: right; }}
  .tick:checked + .body {{ color: var(--done); }}
  .tick:checked + .body .name, .tick:checked + .body .dims b {{ text-decoration: line-through; text-decoration-thickness: 2px; }}
  .tick:checked + .body .qty, .tick:checked + .body .note, .tick:checked + .body .mm {{ color: var(--done); }}
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
  @media (max-width: 420px) {{ .dims b {{ font-size: 19px; }} .hw li {{ grid-template-columns: 60px 1fr; }} }}
</style>

<div class="wrap">
  <header>
    <p class="eyebrow">Drawer bench &middot; 40 x 24 x 19-5/8 in</p>
    <h1>Drawer Bench Cut List</h1>
    <p>{total} pieces: the case first, then the drawers, each grouped by material in cutting order. Inches to the nearest 1/16, mm exact from the CAD. Every part has a shop drawing with its grooves, rabbets, notches and bores located from the blank's own edges; tap a drawing to zoom. Tap a row to tick it off; ticks stay on this phone only.</p>
    <div class="status"><span class="count" id="count"></span><button class="reset" id="reset" type="button">Clear ticks</button></div>
  </header>

  <div class="flag"><b>Provisional.</b> Every groove, rabbet and dado is sized to 18 / 12 / 6 mm plywood. Measure the sheets you bought and re-run the model before cutting joinery. The top's overhang and edge profile still wait on the island; the slide numbers wait on the purchased sheet.</div>

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

  <p class="foot">Generated {today} from <span class="mono">projects/Drawer-bench/cutlist.csv</span> and <span class="mono">images/parts/</span>, which <span class="mono">drawer_bench.py</span> and <span class="mono">part_drawings.py</span> write on every export; every drawn cut is probed against the CAD solid before its sheet is written. Part names match the CAD viewer.</p>
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
