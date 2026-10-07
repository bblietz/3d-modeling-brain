#!/usr/bin/env python
"""Build cutlist.html, the shop page, from cutlist.csv and the part drawings.

Re-run after every `EXPORT=1 built_in_bench.py`, `part_drawings.py` and
`hero_shot.py` (viewer open), then republish the page (same URL) with the
part PNGs and images/hero.png. The page starts with a full image of the
bench from the CAD viewer (Brian, 2026-09-28: always), then a case section
and a drawer section, each grouped by material in cutting order, then the
hardware and the build notes; every row
shows inches to the nearest 1/32 (no metric: Brian, 2026-09-28), the
machining notes, its shop drawing (tap to zoom), and a tick box (per
device, localStorage).

Usage: .venv/bin/python projects/Built-in-bench/make_cutlist_page.py
"""
import csv
import html
import os
import sys
from datetime import date

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
sys.path.insert(0, f"{VAULT}/scripts")
from cutlist import inch_frac  # noqa: E402

CASE_ORDER = ["hard maple", "3/4 maple ply", "1/4 maple ply", "3/4 ply (any, hidden)"]
DRAWER_ORDER = ["hard maple", "3/4 walnut ply", "3/4 maple ply", "1/2 Baltic birch"]
CASE_LABEL = {
    "hard maple": "Hard maple: top, plinth, nailer, scribe strips",
    "3/4 maple ply": "3/4 in maple plywood (measure the sheet): ends, bottom, partition",
    "1/4 maple ply": "1/4 in maple plywood (measure the sheet): back",
    "3/4 ply (any, hidden)": "3/4 in plywood, any grade (hidden): base ladder",
}
DRAWER_LABEL = {
    "hard maple": "Drawer front frames, hard maple: stiles and rails",
    "3/4 walnut ply": "Drawer front panels, 3/4 in walnut plywood (measure the sheet)",
    "3/4 maple ply": "Drawer box fronts and backs, 3/4 in maple plywood (measure the sheet)",
    "1/2 Baltic birch": "Drawer sides and bottoms, 1/2 in Baltic birch (measure the sheet)",
}
TEMPLATE_TAG = "not a plain rectangular blank"
HARDWARE = [
    ("2 pair", "Blum TANDEM plus BLUMOTION 563H, 21 in (563H5330B)",
     "one pair per drawer; 90 lb dynamic; runner front 3/32 behind the case front edge; no rear brackets in a frameless case"),
    ("2 pair", "Blum locking devices T51.1901 R and L",
     "front corners under the drawer bottom, screwed into the 3/4 box front with #6 x 5/8"),
    ("2", "Brass bar pull, 8 in",
     "centered on each front; break-away machine screws through 3/4 front plus 3/4 box front"),
    ("4", "Figure-8 tabletop fasteners", "nailer to top; recess centered 1/4 in from the front face so it opens through"),
    ("6", "Pocket screws #8 x 1-1/4 fine", "ends and partition to the top, near the front"),
    ("8", "Wood screws #8 x 1-1/4", "walnut fronts to the box fronts, through oversize holes"),
    ("1", "Bench cushion", "about 65-1/2 x 25 x 3, boxed, full depth to the wall"),
]
sys.path.insert(0, PROJ)
from assembly_shots import STEPS  # noqa: E402  (file stem, title, prefixes, text); runs the model's checks once
ASSEMBLY_DIR = "images/assembly"
EXPLODED = f"{ASSEMBLY_DIR}/exploded.png"
SUBS = [("drawer-exploded.png", "one drawer box, pulled apart: sides, 3/4 front and back, 1/2 bottom"),
        ("front-exploded.png", "one drawer front, pulled apart: maple stiles and rails around the walnut panel")]


def is_drawer(part):
    return part.startswith("drawer_") or part.startswith("front_")


def load_rows():
    with open(f"{PROJ}/cutlist.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    # hardware and soft goods rows have no dimensions; the page lists them from HARDWARE
    rows = [r for r in rows if r["thickness_mm"]]
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
    items = "".join(part_li(r) for r in rows)
    return f"""
    <section class="group">
      <div class="ghead">
        <h3>{html.escape(label)}</h3>
        <span class="gsum mono">{n_parts} pieces &middot; {area:.1f} sq ft face, no kerf or waste</span>
      </div>
      <ul class="parts">{items}
      </ul>
    </section>"""


HERO = "images/hero.png"


def sub_figure(fname, caption):
    return (f'<figure class="dwg sfig sub" tabindex="0"><img src="{ASSEMBLY_DIR}/{fname}" alt="{html.escape(caption)}">'
            f'<figcaption>{html.escape(caption)}; tap to zoom</figcaption></figure>')


def build():
    assert os.path.exists(f"{PROJ}/{HERO}"), f"{HERO} missing: run hero_shot.py with the CAD viewer open"
    rows = load_rows()
    missing = sorted({r["drawing"] for r in rows if not r["has_drawing"]})
    if missing:
        print(f"WARNING: {len(missing)} part drawings missing (rows shown without a drawing): " + ", ".join(missing))
    case = [r for r in rows if not is_drawer(r["part"])]
    drawers = [r for r in rows if is_drawer(r["part"])]
    stray = {r["material"] for r in case} - set(CASE_ORDER) | {r["material"] for r in drawers} - set(DRAWER_ORDER)
    assert not stray, f"materials not in CASE_ORDER/DRAWER_ORDER, rows would be dropped: {stray}"
    case_html = "".join(group_section(CASE_LABEL.get(m, m), [r for r in case if r["material"] == m])
                        for m in CASE_ORDER if any(r["material"] == m for r in case))
    drawer_html = "".join(group_section(DRAWER_LABEL.get(m, m), [r for r in drawers if r["material"] == m])
                          for m in DRAWER_ORDER if any(r["material"] == m for r in drawers))
    total_pieces = sum(r["qty"] for r in rows)
    hw = "".join(
        f'<li><span class="hqty mono">{html.escape(q)}</span><div><b>{html.escape(what)}</b><span class="hnote">{html.escape(note)}</span></div></li>'
        for q, what, note in HARDWARE)
    steps = []
    for stem, title, _prefixes, text in STEPS:
        img = f"{ASSEMBLY_DIR}/{stem}.png"
        if not os.path.exists(f"{PROJ}/{img}"):
            print(f"WARNING: {img} missing (run assembly_shots.py with the CAD viewer open)")
        extra = ""
        if stem == "step-08":
            extra = sub_figure(*SUBS[0])
        if stem == "step-09":
            extra = sub_figure(*SUBS[1])
        steps.append(
            f'<li class="step"><div class="stext"><h3>{html.escape(title)}</h3><p>{html.escape(text)}</p></div>'
            f'<figure class="dwg sfig" tabindex="0"><img src="{img}" alt="{html.escape(title)}: parts added in this step in wood colors, the rest grey">'
            f'<figcaption>new parts in wood colors; tap to zoom</figcaption></figure>{extra}</li>')
    notes = "".join(steps)
    if not os.path.exists(f"{PROJ}/{EXPLODED}"):
        print(f"WARNING: {EXPLODED} missing (run assembly_shots.py with the CAD viewer open)")
    today = date.today().isoformat()
    return PAGE.format(case=case_html, drawers=drawer_html, hardware=hw, notes=notes, total=total_pieces, today=today,
                       n_case=sum(r["qty"] for r in case), n_drawers=sum(r["qty"] for r in drawers), hero=HERO,
                       exploded=EXPLODED, n_steps=len(STEPS))


PAGE = """<title>Built-in Bench Cut List</title>
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
  ol.steps {{ margin: 0; padding: 0; list-style: none; counter-reset: step; display: flex; flex-direction: column; }}
  .step {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: 12px 20px; padding: 16px 0; border-bottom: 1px solid var(--line); align-items: start; }}
  .step .stext h3 {{ font-size: 17px; margin: 0 0 6px; }}
  .step .stext h3::before {{ counter-increment: step; content: counter(step) ". "; color: var(--accent-ink); }}
  .step .stext p {{ margin: 0; font-size: 14.5px; line-height: 1.5; }}
  .step .sfig {{ margin: 0; }}
  .step .sub {{ grid-column: 1 / -1; }}
  @media (max-width: 720px) {{ .step {{ grid-template-columns: 1fr; }} }}
  .foot {{ font-size: 13px; color: var(--muted); max-width: 72ch; }}
  #lightbox {{ position: fixed; inset: 0; background: rgba(15, 12, 8, .9); display: none; place-items: center; padding: 12px; z-index: 10; cursor: zoom-out; overflow: auto; }}
  #lightbox.open {{ display: grid; }}
  #lightbox img {{ max-width: 100%; max-height: 94vh; background: var(--paper); border-radius: 6px; }}
  @media (max-width: 420px) {{ .dims b {{ font-size: 19px; }} .hw li {{ grid-template-columns: 60px 1fr; }} }}
</style>

<div class="wrap">
  <figure class="dwg hero" tabindex="0"><img src="{hero}" alt="the whole bench, front-left view from the CAD viewer"><figcaption>the whole bench, from the CAD viewer; tap to zoom</figcaption></figure>
  <header>
    <p class="eyebrow">Built-in bench &middot; 66 x 28 in alcove</p>
    <h1>Built-in Bench Cut List</h1>
    <p>Two drawers on Blum undermounts, maple frame-and-walnut-panel fronts, solid maple top. {total} pieces: the case first, then the drawers, each grouped by material in cutting order. Inches to the nearest 1/32. Every part has a shop drawing with its grooves, rabbets, notches and bores located from the blank's own edges; tap a drawing to zoom. Tap a row to tick it off; ticks stay on this phone only.</p>
    <div class="status"><span class="count" id="count"></span><button class="reset" id="reset" type="button">Clear ticks</button></div>
  </header>

  <div class="flag"><b>Measure the alcove at the floor, 16 in and 36 in, at the back wall and the pilaster faces, before cutting.</b> Cut the top, plinth and scribe strips long and scribe them. Confirm the low receptacle seen in the photo before cutting the back.</div>

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
    <figure class="dwg hero" tabindex="0"><img src="{exploded}" alt="the whole bench pulled apart: base, case, back, partition, nailer, strips and plinth, slides, drawer boxes, fronts, top, cushion"><figcaption>everything pulled apart along its assembly direction; tap to zoom</figcaption></figure>
    <ol class="steps">{notes}</ol>
  </div>

  <p class="foot">Generated {today} from <span class="mono">projects/Built-in-bench/cutlist.csv</span> and <span class="mono">images/parts/</span>, which <span class="mono">built_in_bench.py</span> and <span class="mono">part_drawings.py</span> write on every export; every drawn cut is probed against the CAD solid before its sheet is written. The bench image at the top and the assembly pictures are screenshots of the CAD viewer (<span class="mono">hero_shot.py</span>, <span class="mono">assembly_shots.py</span>). Part names match the CAD viewer.</p>
</div>

<div id="lightbox" role="dialog" aria-label="Enlarged drawing" aria-hidden="true"><img id="lightbox-img" alt=""></div>

<script>
  (function () {{
    var KEY = 'built-in-bench-cutlist-ticks';
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
