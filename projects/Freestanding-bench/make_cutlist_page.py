#!/usr/bin/env python
"""Build cutlist.html, the shop page, from cutlist.csv and the part drawings.

Re-run after every `EXPORT=1 freestanding_bench.py`, `part_drawings.py` and
`hero_shot.py` (viewer open), then republish the page (same URL) with the
part PNGs and images/hero.png. The page starts with a full image of the
bench from the CAD viewer (Brian, 2026-09-28: always), then a case section
and a drawer section, each grouped by material in cutting order, then the
hardware and the build notes; every row
shows inches to the nearest 1/32 (no metric: Brian, 2026-09-28), the
machining notes, its shop drawing (tap to zoom), and a tick box (per
device, localStorage). Missing images (hero, nook picture, assembly
captures) are warnings, not errors, so the page can be built before the
viewer captures exist and rebuilt once they do.

Usage: .venv/bin/python projects/Freestanding-bench/make_cutlist_page.py
"""
import csv
import html
import os
import sys
from datetime import date

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Freestanding-bench"
sys.path.insert(0, f"{VAULT}/scripts")
from cutlist import inch_frac  # noqa: E402

BUILT_IN_URL = "https://claude.ai/artifact/YQFcx4g5x64K83yhDHvGMf"   # the built-in design's shop page, kept
OPTIONS_URL = "https://claude.ai/artifact/QLCHadrNJZDeDjqka9yond"                                                      # the base options page (legs, blades, gables); filled when published

CASE_ORDER = ["hard maple", "3/4 maple ply", "1/4 maple ply"]
DRAWER_ORDER = ["hard maple", "1/2 paint-grade panel", "1/2 Baltic birch"]
CASE_LABEL = {
    "hard maple": "Hard maple: top, nailer, legs and base rails (bare, Osmo Natural)",
    "3/4 maple ply": "3/4 in maple plywood (measure the sheet): ends (show faces, painted white, edges banded), bottom, partition",
    "1/4 maple ply": "1/4 in maple plywood (measure the sheet): back",
}
DRAWER_LABEL = {
    "hard maple": "Drawer front frames, hard maple, painted white: stiles and rails",
    "1/2 paint-grade panel": "Drawer front panels, 1/2 in MDF or paint-grade plywood (measure the sheet), painted white with the frames",
    "1/2 Baltic birch": "Drawer boxes: sides, fronts, backs and bottoms, 1/2 in 9-ply Baltic birch (measure the sheet)",
}
TEMPLATE_TAG = "not a plain rectangular blank"
sys.path.insert(0, PROJ)
from assembly_shots import STEPS  # noqa: E402  (file stem, title, prefixes, text); runs the model's checks once
import freestanding_bench as M  # noqa: E402


def fi(mm):
    return inch_frac(mm, 32)


HARDWARE = [
    ("2 pair", "Blum TANDEM plus BLUMOTION 563H, 21 in (563H5330B)",
     "one pair per drawer; 90 lb dynamic; runner front 3/32 behind the case front edge; no rear brackets in a frameless case"),
    ("2 pair", "Blum locking devices T51.1901 R and L",
     "front corners under the drawer bottom, screwed into the 1/2 box front with #6 x 1/2"),
    ("2", "Brass bar pull, 8 in",
     "centered on each front; break-away machine screws through the 1/2 panel plus the 1/2 box front"),
    ("4", "Figure-8 tabletop fasteners", "nailer to top; recess centered 1/4 in from the front face so it opens through"),
    ("6", "Pocket screws #8 x 1-1/4 fine", "ends and partition to the top, near the front"),
    ("20", "Pocket screws #8 x 1-1/4 fine", "base rails into the legs (2 per joint, 12) and up into the case bottom (10)"),
    ("8", "Wood screws #8 x 2", "down through the case bottom into the leg tops, two per leg, under the drawer boxes"),
    ("8", "Wood screws #8 x 7/8", "fronts to the box fronts, through oversize holes, pre-drilled"),
    ("1 roll", "Iron-on maple edge banding, 13/16",
     f"the ends' front and bottom edges, about {fi(2 * ((M.TOP_Z0 - M.END_Z0) + (M.CASE_D - M.CASE_Y0)))} in all, painted with them"),
    ("1", "Bench cushion", f"about {fi(M.TOP_W - 0.5 * M.IN)} x {fi(M.TOP_D)} x {fi(M.CUSHION_H)}, boxed, the full depth of the top"),
]
# the numbers that moved from the built-in design, read from the model so they cannot drift from the cut list
MOVED = [
    ("Clear floor under the case", f"{fi(M.CLEAR)} in (the tallest current Roomba is under 4 in)"),
    ("Drawer box", f"{fi(M.BOX_H)} in tall, {fi(M.BOX_H - M.UM_RECESS - M.T12)} in inside (was 8-1/2 in)"),
    ("Drawer fronts", f"{fi(M.FRONT_W)} x {fi(M.FRONT_H)} in (were 31-3/32 x 10-1/8)"),
    ("Top", f"{fi(M.TOP_W)} x {fi(M.TOP_D)} in, {fi(M.SIDE_AIR)} in of air to each wall (was 66 x 24-5/8, wall to wall)"),
    ("Case", f"{fi(M.CASE_W)} x {fi(M.CASE_D - M.CASE_Y0)} x {fi(M.TOP_Z0 - M.BOT_Z0)} in, back {fi(M.WALL_GAP)} in off the wall"),
    ("Legs", f"{fi(M.LEG_SQ)} x {fi(M.LEG_SQ)} x {fi(M.CLEAR)} in, outer faces {fi(M.LEG_IN_X)} in from the case ends, "
             f"{fi(M.LEG_IN_FRONT)} in behind the case front edge and {fi(M.LEG_IN_BACK)} in inside the case back"),
    ("Overall", f"{fi(M.TOP_W)} x {fi(M.TOP_D)} x {fi(M.SEAT_Z + M.CUSHION_H)} in with the cushion; wood top at {fi(M.SEAT_Z)} in, seat {fi(M.SEAT_Z + M.CUSHION_H)} in, unchanged"),
]
ASSEMBLY_DIR = "images/assembly"
EXPLODED = f"{ASSEMBLY_DIR}/exploded.png"
SUBS = {
    "step-05": ("base-exploded.png", "the base frame, pulled apart: four 2 in square legs, two end rails and the back rail"),
    "step-07": ("drawer-exploded.png", "one drawer box, pulled apart: sides, front, back and bottom, all 1/2 Baltic birch"),
    "step-08": ("front-exploded.png", "one drawer front, pulled apart: maple stiles and rails around the inset panel, all painted white"),
}


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
NOOK = "images/bench-in-nook-guided-web.jpg"    # photo_match.py overlay made photoreal by Gemini (render_in_room.py guided); the styled picture with the dogs follows the base pick
NOOK_ALT = ("the freestanding bench in the alcove: all-white drawer fronts with brass pulls, maple top, cushion, four maple legs "
            "with clear floor under the case, the baseboard behind it, three maple shelves above, a dropped soffit with two downlights")
NOOK_CAPTION = ("the freestanding bench in the alcove at true size: the CAD model projected into the photo of the alcove through a "
                "camera matched to it, then given its materials by AI (white ends, frames and panels, maple top, legs and rails, "
                f"cushion). {fi(M.CLEAR)} in of clear floor under the case, the alcove's baseboard left in place, {fi(M.SIDE_AIR)} in of "
                f"air to each wall. Wood top {fi(M.SEAT_Z)} in, seat {fi(M.SEAT_Z + M.CUSHION_H)} in with the cushion. No dogs or "
                "props yet: the styled picture with Maizy, Franco and the client's accessories follows once the base is picked. The "
                "three maple shelves and the 12 in dropped soffit with two 4 in recessed lights are picture-only ideas from the "
                "client's reference picture; none of that is in this cut list. Tap to zoom")


def sub_figure(fname, caption):
    return (f'<figure class="dwg sfig sub" tabindex="0"><img src="{ASSEMBLY_DIR}/{fname}" alt="{html.escape(caption)}">'
            f'<figcaption>{html.escape(caption)}; tap to zoom</figcaption></figure>')


def build():
    if not os.path.exists(f"{PROJ}/{HERO}"):
        print(f"WARNING: {HERO} missing: run hero_shot.py with the CAD viewer open (the page opens with it)")
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
    moved = "".join(f'<li><b>{html.escape(k)}</b> {html.escape(v)}</li>' for k, v in MOVED)
    steps = []
    for stem, title, _prefixes, text in STEPS:
        img = f"{ASSEMBLY_DIR}/{stem}.png"
        if not os.path.exists(f"{PROJ}/{img}"):
            print(f"WARNING: {img} missing (run assembly_shots.py with the CAD viewer open)")
        extra = ""
        if stem in SUBS:
            if not os.path.exists(f"{PROJ}/{ASSEMBLY_DIR}/{SUBS[stem][0]}"):
                print(f"WARNING: {ASSEMBLY_DIR}/{SUBS[stem][0]} missing (run assembly_shots.py with the CAD viewer open)")
            extra = sub_figure(*SUBS[stem])
        steps.append(
            f'<li class="step"><div class="stext"><h3>{html.escape(title)}</h3><p>{html.escape(text)}</p></div>'
            f'<figure class="dwg sfig" tabindex="0"><img src="{img}" alt="{html.escape(title)}: parts added in this step in wood colors, the rest grey">'
            f'<figcaption>new parts in wood colors; tap to zoom</figcaption></figure>{extra}</li>')
    notes = "".join(steps)
    if not os.path.exists(f"{PROJ}/{EXPLODED}"):
        print(f"WARNING: {EXPLODED} missing (run assembly_shots.py with the CAD viewer open)")
    if os.path.exists(f"{PROJ}/{NOOK}"):
        nook = (f'<figure class="dwg nook" tabindex="0"><img src="{NOOK}" alt="{html.escape(NOOK_ALT)}">'
                f'<figcaption>{html.escape(NOOK_CAPTION)}</figcaption></figure>')
    else:
        print(f"WARNING: {NOOK} missing (photo_match.py, then render_in_room.py guided, then the web jpg); figure skipped")
        nook = ""
    options = (f'<a href="{OPTIONS_URL}">base options page</a>' if OPTIONS_URL else "base options page")
    today = date.today().isoformat()
    return PAGE.format(case=case_html, drawers=drawer_html, hardware=hw, notes=notes, total=total_pieces, today=today,
                       n_case=sum(r["qty"] for r in case), n_drawers=sum(r["qty"] for r in drawers), hero=HERO, nook=nook,
                       moved=moved, options=options, built_in=BUILT_IN_URL, exploded=EXPLODED, n_steps=len(STEPS),
                       clear=fi(M.CLEAR), top_w=fi(M.TOP_W), top_d=fi(M.TOP_D), air=fi(M.SIDE_AIR), seat=fi(M.SEAT_Z),
                       seat_c=fi(M.SEAT_Z + M.CUSHION_H), box_h=fi(M.BOX_H), case_w=fi(M.CASE_W), wall_gap=fi(M.WALL_GAP),
                       leg=fi(M.LEG_SQ), rail_t=fi(M.RAIL_T), rail_h=fi(M.RAIL_H), leg_in_back=fi(M.LEG_IN_BACK),
                       min_open=fi(M.TOP_W + 2 * M.SIDE_AIR))


PAGE = """<title>Freestanding Bench Cut List</title>
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
  header p + p {{ margin-top: 10px; }}
  header a, .foot a {{ color: var(--accent-ink); }}
  .status {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; margin-top: 14px; font-size: 14px; }}
  .status .count {{ font-weight: 600; }}
  button.reset {{ font: inherit; font-size: 13px; color: var(--accent-ink); background: none; border: 1px solid var(--line); border-radius: 999px; padding: 4px 12px; cursor: pointer; }}
  button.reset:focus-visible, .tick:focus-visible + .body, .dwg:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
  .flag {{ background: var(--warn-bg); color: var(--warn-ink); border-radius: 8px; padding: 10px 14px; font-size: 14.5px; max-width: 72ch; }}
  .flag b {{ font-weight: 600; }}
  .moved {{ background: var(--note-bg); color: var(--note-ink); border-radius: 8px; padding: 12px 16px; max-width: 72ch; }}
  .moved h2 {{ font-size: 15px; margin: 0 0 6px; letter-spacing: .04em; text-transform: uppercase; }}
  .moved ul {{ margin: 0; padding-left: 18px; font-size: 14.5px; display: flex; flex-direction: column; gap: 3px; }}
  .moved b {{ font-weight: 600; color: var(--ink); }}
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
  @media print {{
    @page {{ size: letter; margin: 0.5in 0.5in 0.6in; }}
    html, body {{ background: #fff; color: #000; font-size: 11pt; }}
    .wrap {{ max-width: none; padding: 0; margin: 0; gap: 14px; }}
    .tick, .status, figcaption, #lightbox, .reset {{ display: none !important; }}
    header p {{ max-width: none; }}
    .flag {{ border: 1px solid #c8782a; background: #fff3e6; break-inside: avoid; }}
    .moved {{ border: 1px solid #ccc; background: #f6f6f6; break-inside: avoid; }}
    .big {{ break-before: page; gap: 10px; }}
    .big > h2 {{ font-size: 20px; }}
    .keep {{ break-inside: avoid; }}
    .screen-only {{ display: none; }}
    .part {{ grid-template-columns: 1fr; gap: 6px; padding: 8px 0; break-inside: avoid; }}
    .part label {{ cursor: default; }}
    .dwg {{ border: 1px solid #ccc; padding: 4px; background: #fff; break-inside: avoid; cursor: default; }}
    .dwg img {{ max-height: 3.6in; width: auto; max-width: 100%; margin: 0 auto; }}
    .hero img {{ max-height: 5in; }}
    .nook {{ break-before: page; }}
    .nook img {{ max-height: 7.5in; }}
    .hw li {{ break-inside: avoid; }}
    .step {{ grid-template-columns: 1fr 1.3fr; break-inside: avoid; padding: 10px 0; }}
    .step .sfig img {{ max-height: 2.8in; }}
    .step .sub img {{ max-height: 3.6in; }}
    .foot {{ font-size: 9pt; }}
  }}
</style>

<div class="wrap">
  <figure class="dwg hero" tabindex="0"><img src="{hero}" alt="the whole bench on its legs, front-left view from the CAD viewer"><figcaption>the whole bench, from the CAD viewer; tap to zoom</figcaption></figure>
  <header>
    <p class="eyebrow">Freestanding bench &middot; {top_w} x {top_d} in &middot; {clear} in clear floor</p>
    <h1>Freestanding Bench Cut List</h1>
    <p>The client's change of 2026-10-26: the bench is now a freestanding piece with {clear} in of clear floor under it for the robot vacuum. The alcove's baseboard stays, the bench slides in with {air} in of air to each wall and its back {wall_gap} in off the wall. Kept from the built-in: all-white frame-and-panel fronts with brass pulls, the solid maple top at {seat} in (seat {seat_c} in with the cushion), two drawers on 21 in Blum 563H undermounts, 1/2 in Baltic birch boxes, Osmo Natural on the bare maple.</p>
    <p>Changed: a {top_w} x {top_d} in top over a {case_w} in case, the case ends are show faces (painted white, edges banded), four {leg} in square maple legs on a C-frame of {rail_t} x {rail_h} in maple rails with no front rail, drawers {box_h} in tall instead of 8-1/2 (the {clear} in of floor come out of the drawers), no plinth, no scribe strips, no wall screws. The base style (legs, blades or gables) is Brian's pick on the {options}; this page documents the legs. The built-in design stays on <a href="{built_in}">its own shop page</a> in case the client goes back.</p>
    <p>{total} pieces: the case first, then the drawers, each grouped by material in cutting order. Inches to the nearest 1/32. Every part has a shop drawing with its grooves, rabbets, notches and bores located from the blank's own edges.<span class="screen-only"> Tap a drawing to zoom. Tap a row to tick it off; ticks stay on this phone only.</span></p>
    <div class="status"><span class="count" id="count"></span><button class="reset" id="reset" type="button">Clear ticks</button></div>
  </header>
  {nook}

  <div class="moved"><h2>Numbers that moved</h2><ul>{moved}</ul></div>

  <div class="flag"><b>Measure the alcove at the floor, 16 in and 36 in, at the back wall and the pilaster faces, before cutting.</b> The piece is {top_w} in wide; if the opening is under {min_open} in anywhere, narrow the top. The baseboard stays: the back legs sit {leg_in_back} in inside the case back, so confirm the baseboard and shoe stand no more than 1-1/4 in off the wall. The low receptacle seen in the photo ends up behind the case; nothing can stay plugged into it.</div>

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
    <figure class="dwg hero" tabindex="0"><img src="{exploded}" alt="the whole bench pulled apart: base frame, case, back, partition, nailer, slides, drawer boxes, fronts, top, cushion"><figcaption>everything pulled apart along its assembly direction; tap to zoom</figcaption></figure>
    <ol class="steps">{notes}</ol>
  </div>

  <p class="foot">Generated {today} from <span class="mono">projects/Freestanding-bench/cutlist.csv</span> and <span class="mono">images/parts/</span>, which <span class="mono">freestanding_bench.py</span> and <span class="mono">part_drawings.py</span> write on every export; every drawn cut is probed against the CAD solid before its sheet is written. The bench image at the top and the assembly pictures are screenshots of the CAD viewer (<span class="mono">hero_shot.py</span>, <span class="mono">assembly_shots.py</span>). Part names match the CAD viewer. The built-in version of this bench is at <a href="{built_in}">its own page</a>.</p>
</div>

<div id="lightbox" role="dialog" aria-label="Enlarged drawing" aria-hidden="true"><img id="lightbox-img" alt=""></div>

<script>
  (function () {{
    var KEY = 'freestanding-bench-cutlist-ticks';
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
