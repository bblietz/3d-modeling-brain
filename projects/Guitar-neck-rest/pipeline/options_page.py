#!/usr/bin/env python
"""Build the neck rest options page, drawn from the concept solids, with real slice numbers.

Top of the page: the design Brian kept on 2026-11-22 (round 2's C1, the open-frame rocker) with the rounded edges he asked
for on 2026-11-23 (the solid c1r), what is settled, pad and tread, and what gets checked before it prints.
Folded away below: round 3 (longer cradles, not taken), round 2 (the other rocker bodies), round 1 (six base shapes, research).

Reads   concepts-report.json (concepts.py), concepts-slice-pla.json, rocker-slice-pla.json, long-slice-pla.json and
        design-slice-pla.json (slice_stls.py), images/concepts/*.png
Writes  options.html, one self-contained file (images inlined), published as a private Artifact.

Run from the vault root, after concepts.py and the slices:
  .venv/bin/python projects/Guitar-neck-rest/pipeline/options_page.py
"""
import base64
import json
import math
from fractions import Fraction
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
IMAGES = PROJECT / "images" / "concepts"
REPORT = json.loads((PROJECT / "concepts-report.json").read_text())
SLICE = json.loads((PROJECT / "concepts-slice-pla.json").read_text())
SLICE2 = json.loads((PROJECT / "rocker-slice-pla.json").read_text())
SLICE3 = json.loads((PROJECT / "long-slice-pla.json").read_text())
SLICE4 = json.loads((PROJECT / "design-slice-pla.json").read_text())   # the kept body with its edges rounded over (c1r)
BUILD = json.loads((PROJECT / "build-report.json").read_text())        # the real model (neck_rest.scad, pipeline/build.py)
PRINT3MF = json.loads((PROJECT / "3mf-report.json").read_text())       # its 3MF and slice (pipeline/make_print_3mf.py)
OUT = PROJECT / "options.html"
VERSION = "Version 6"
DATE = "2026-11-23"
IN = 25.4
D = REPORT["derived_mm"]
H = REPORT["heights_in"]
USE = REPORT["use"]


def img(name, alt):
    data = base64.b64encode((IMAGES / name).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{alt}">'


def frac(x_in, den=8):
    """Inches as a mixed fraction to the nearest 1/den: 3.75 -> 3-3/4."""
    f = Fraction(round(x_in * den), den)
    whole, rest = divmod(f, 1)
    if rest == 0:
        return f"{whole}"
    return f"{whole}-{rest}" if whole else f"{rest}"


def mm(x):
    return frac(x / IN)


def quote(*parts, table=SLICE):
    g = sum(table[f"{p}.stl"]["grams"] for p in parts)
    m = sum(table[f"{p}.stl"]["minutes"] for p in parts)
    return round(g), f"{m // 60} h {m % 60:02d} min"


LOW, HIGH, TALL, FLAT = (frac(H[k]) for k in ("low", "high", "tall", "flat"))
PED_MIN, PED_MAX = frac(REPORT["pedestal_in"]["min"]), frac(REPORT["pedestal_in"]["max"])
TILT_LOW, TILT_HIGH = REPORT["tilt_deg"]["low"], REPORT["tilt_deg"]["high"]
CW_MM = REPORT["cradle"]["width_mm"]
GUITAR_TAIL = REPORT["rocker"]["guitar_tail_to_nut_in"]

SHAPES = [
    dict(
        key="a", parts=("a",), name="Two-height block", tag="Lightest, fastest",
        line=f"One hollow frame with a cradle on top and another on its side. Stand it up for {HIGH} in, lay it down for {LOW} in.",
        heights=f"{LOW} and {HIGH} in", follows="No", pieces="1",
        size=f"{mm(D['XA'])} x {mm(D['YA'])} x {mm(D['ZA'])} in",
        like="Harley Benton GuitarTech (4.9 of 5 from 2,318 buyers), StewMac Hi-Lo, and the most downloaded printable rest (Bukken, 3,330 downloads).",
        good=["Two heights from one print, nothing to assemble or lose.",
              "The window is a handle and cuts the plastic.",
              "Prints standing on end; both cradles and the window are vertical, so no supports are planned."],
        watch=[f"The cradle stays level while the neck slopes {TILT_LOW:.0f} to {TILT_HIGH:.0f} degrees, so the neck bears on one end of the pad. Fixable: build the slope into each cradle.",
               f"Standing tall it is {mm(D['YA'])} in wide under a {mm(D['ZA'])} in block. Makers call narrow printed rests tippy."],
        views=[("a-shape.png", f"Standing: cradle at {HIGH} in", "Two-height block standing on a 1 inch grid"),
               ("a-use.png", "P-Bass neck stand-in on the tall cradle", "Two-height block with a bass neck resting on it"),
               ("a-extra.png", f"Lying down: cradle at {LOW} in", "Two-height block on its side with a bass neck on the low cradle")],
    ),
    dict(
        key="b", parts=("b",), name="Three-height block", tag="Only shape that reaches an acoustic",
        line=f"A solid block with a cradle on three faces. Whichever face is down sets the height: {LOW}, {HIGH} or {TALL} in.",
        heights=f"{LOW}, {HIGH} and {TALL} in", follows="No", pieces="1",
        size=f"{mm(D['BA'])} x {mm(D['BB'])} x {mm(D['BC'])} in",
        like="MusicNomad Cradle Cube ($20, five positions).",
        good=[f"The {TALL} in face is acoustic height (commercial acoustic rests are 5 to 6-1/4 in).",
              "Long cradles: 5-1/2 in of pad at the two lower heights.",
              "No moving parts, no supports planned."],
        watch=["Heaviest and slowest of the six.",
               "Same level cradle as A, so the neck bears on one end of the pad.",
               "The low and tall cradles run into each other around one edge. It works, but it is the least tidy shape."],
        views=[("b-shape.png", f"Middle face up: cradle at {HIGH} in", "Three-height block on a 1 inch grid"),
               ("b-use.png", "P-Bass neck stand-in on the middle cradle", "Three-height block with a bass neck resting on it"),
               ("b-extra.png", f"The three ways up: {LOW}, {HIGH}, {TALL} in", "The same block shown on each of its three faces")],
    ),
    dict(
        key="c", parts=("c",), name="Rocker", tag="My pick to start from",
        line="A boat-shaped block on a curved bottom. It rolls until the cradle lies along the neck, whatever the slope.",
        heights=f"{HIGH} in (one)", follows="Yes, it rolls", pieces="1",
        size=f"{mm(D['C_CHORD'])} x {mm(D['YC'])} x {mm(D['ZC'])} in",
        like="StewMac Rock-n-Roller ($52 to $89, the luthier standard), Widara ServiceCradle, Crimson Rockin' Neck Rest.",
        good=["The pad bears along its whole length instead of on one edge.",
              f"Rights itself: the bottom curve's radius ({mm(130)} in) is larger than the cradle height, so weight on top pushes it back to level.",
              "One piece. Prints on its side, so the rocking curve is drawn by the nozzle in one clean arc and nothing needs support."],
        watch=["One height. A second height means a second rocker, or a hybrid with A.",
               "Printed rockers slide on a smooth bench; makers glue cork underneath. A cork or rubber strip on the curve fixes it.",
               "Second heaviest. The window can grow to cut that."],
        views=[("c-shape.png", f"Level: cradle at {HIGH} in", "Rocker on a 1 inch grid"),
               ("c-use.png", f"Rolled {TILT_HIGH:.1f} degrees to meet the neck", "Rocker rolled to match a sloping bass neck")],
    ),
    dict(
        key="d", parts=("d_base", "d_cradle"), name="Hanging cradle on a yoke", tag="Follows the neck, base stays put",
        line="A flat base with two uprights. The cradle hangs between them on two pins and swings to match the neck.",
        heights=f"{HIGH} in (one)", follows="Yes, it swings", pieces="2",
        size=f"{mm(D['XD'])} x {mm(D['YD'])} x {mm(D['D_ZU'])} in",
        like="Dunlop System 65 Neck Cradle ($42), Hosco, G&amp;W Pivoting Neck Rest ($110).",
        good=["Full-length pad contact like the rocker, on a base that sits flat and does not creep.",
              "The pins sit just above the line the neck bears on, so the cradle hangs level by itself. Buyers say Dunlop's cradle flips to its flat side when the guitar comes off.",
              "The cradle lifts out. A second cradle (wider for a 5-string, or flat for headstock work) drops into the same base."],
        watch=["Two parts and a pin fit to get right: loose enough to swing, tight enough not to rattle.",
               "One height as drawn. A second pair of sockets lower on the uprights would add another.",
               "Tallest uprights of the six; the base wants solid infill where they meet the plate."],
        views=[("d-shape.png", f"Assembled: cradle at {HIGH} in", "Yoke base with the cradle hanging between two uprights"),
               ("d-use.png", f"Cradle swung {TILT_HIGH:.1f} degrees under the neck", "Hanging cradle tilted to match a sloping bass neck"),
               ("d-extra.png", "Cradle lifted out of its open sockets", "Cradle raised above the yoke to show the pins and sockets")],
    ),
    dict(
        key="e", parts=("e",), name="Long low trough", tag="The fretwork one",
        line=f"A 9 in trough that sits under the neck while the instrument lies flat. The neck stays level and is held along its length.",
        heights=f"{FLAT} in (to be measured)", follows="Not needed, neck is level", pieces="1",
        size=f"{mm(D['XE'])} x {mm(D['E_FOOT'])} x {mm(D['ZE'])} in",
        like="StewMac Neck Support Caul ($59, 12 in long, cork lined, clamps to the bench).",
        good=["The only shape that supports a length of neck. StewMac warns that tapping frets over a point support dents the neck.",
              "The body lies flat, so nothing rocks or tips, and the flanges take bench clamps.",
              "Holds a bolt-on neck by itself once it is off the body."],
        watch=[f"Its height has to match where your neck sits when the instrument lies flat. {FLAT} in is my estimate from Fender body and pocket sizes, not a measurement, and the guitar and bass may differ.",
               "No extra room under the headstock, so less space to work the tuners. An angled headstock (Gibson style) touches the bench when flat.",
               "For hammering it would get more walls and infill than this quote, so more plastic."],
        views=[("e-shape.png", f"9 in long, cradle at {FLAT} in", "Long low trough with clamp flanges on a 1 inch grid"),
               ("e-use.png", "P-Bass neck stand-in lying level in the trough", "Bass neck lying along the trough")],
    ),
    dict(
        key="f", parts=("f_base", "f_head"), name="Screw pedestal", tag="Any height in between",
        line=f"A round base with a fat printed screw. Spin the head to set any height from {PED_MIN} to {PED_MAX} in.",
        heights=f"{PED_MIN} to {PED_MAX} in", follows="No", pieces="2",
        size=f"{mm(D['F_DISC_D'])} in round base, {mm(D['XF'])} x {mm(D['YF'])} in head",
        like="PSG's adjustable rest on MakerWorld (5.0 stars, needs an M5 x 105 bolt), Hercules HA206 folding stand (four heights).",
        good=["One rest fits both instruments exactly; a half turn is 5/32 in.",
              "No hardware: the thread is printed, with a 45 degree flank so it needs no supports.",
              "Once a neck is in the cradle the head cannot turn, so it holds its height without a lock."],
        watch=["A printed thread has some play, so the head wobbles a little. Fine for string changes, wrong for fretwork.",
               "Level cradle like A and B, so the neck bears on one end of the pad.",
               f"At full height the head stands on a {mm(D['F_DISC_D'])} in disc with only 5/8 in of thread engaged."],
        views=[("f-shape.png", f"Drawn at {frac(REPORT['pedestal_in']['drawn'], 4)} in", "Screw pedestal with a round base on a 1 inch grid"),
               ("f-use.png", "P-Bass neck stand-in on the pedestal", "Screw pedestal with a bass neck resting on it"),
               ("f-extra.png", f"Lowest ({PED_MIN} in) and highest ({PED_MAX} in)", "Two pedestals side by side at the lowest and highest settings")],
    ),
]

for s in SHAPES:
    s["grams"], s["time"] = quote(*s["parts"])

CSS = """
<style>
/* Layout: one column; each shape is a full-width block with its pictures in a row, then a comparison table. Print blue accent, cork for the pad. */
:root {
  --bg: #f4f5f7; --surface: #ffffff; --fg: #1b2430; --muted: #5d6675; --line: #d9dde3;
  --accent: #2f6fe4; --accent-ink: #1f4fa8; --cork: #a9793f; --warn: #b4410f; --tag: #e3ecfc; --good: #1f7a4d;
  --display: "Barlow Condensed", "Arial Narrow", sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #11161d; --surface: #1a212b; --fg: #e7ebf1; --muted: #a2acba; --line: #2c3640;
    --accent: #78a4ff; --accent-ink: #a9c4ff; --cork: #d2a56c; --warn: #ff8a5b; --tag: #22304a; --good: #5fcf95; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #11161d; --surface: #1a212b; --fg: #e7ebf1; --muted: #a2acba; --line: #2c3640;
  --accent: #78a4ff; --accent-ink: #a9c4ff; --cork: #d2a56c; --warn: #ff8a5b; --tag: #22304a; --good: #5fcf95; color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 16px; line-height: 1.5;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 0 48px; }
main { max-width: 1120px; margin: 0 auto; }
h1, h2, h3 { font-family: var(--display); text-wrap: balance; letter-spacing: 0.01em; margin: 0; }
h1 { font-size: clamp(40px, 7vw, 64px); line-height: 1; font-weight: 700; }
h2 { font-size: 30px; font-weight: 600; margin-top: 56px; margin-bottom: 8px; }
h3 { font-size: 28px; font-weight: 600; line-height: 1.1; }
h4 { font-family: var(--mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); font-weight: 500; margin: 0 0 4px; }
.eyebrow { font-family: var(--mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
header { padding-block: 40px 16px; border-bottom: 1px solid var(--line); display: grid; gap: 10px; }
header p { max-width: 68ch; margin: 0; color: var(--muted); }
p { max-width: 68ch; }
a { color: var(--accent-ink); }
figure { margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 8px; min-width: 0; }
figure img { display: block; width: 100%; height: auto; max-width: 100%; border-radius: 3px; }
figcaption { font-size: 14px; color: var(--muted); padding: 8px 4px 2px; }
.wide { margin-top: 16px; }
.jump { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.jump a { font-family: var(--mono); font-size: 13px; text-decoration: none; border: 1px solid var(--line); background: var(--surface); border-radius: 4px; padding: 6px 10px; }
.jump a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.shape { margin-top: 40px; padding-top: 24px; border-top: 1px solid var(--line); display: grid; gap: 14px; }
.shape.pick { border-top: 3px solid var(--accent); }
.shape .head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px; }
.shape .letter { font-family: var(--display); font-weight: 700; font-size: 28px; color: var(--accent-ink); }
.shape .line { margin: 0; font-size: 17px; }
.views { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }
.facts div { padding: 10px 14px; border-right: 1px solid var(--line); min-width: 0; }
.facts div:last-child { border-right: 0; }
.facts .v { font-family: var(--display); font-size: 24px; font-weight: 600; line-height: 1.15; font-variant-numeric: tabular-nums; }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px 32px; }
.two > div { min-width: 0; }
.two h4.good { color: var(--good); }
.two h4.watch { color: var(--warn); }
ul { padding-left: 20px; margin: 4px 0 0; }
li { margin: 4px 0; max-width: 70ch; }
.like { font-size: 15px; color: var(--muted); margin: 0; max-width: 90ch; }
.tag { display: inline-block; font-family: var(--mono); font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; background: var(--tag); color: var(--accent-ink); padding: 2px 8px; border-radius: 3px; }
.tag.unv { background: transparent; color: var(--warn); border: 1px solid var(--warn); }
table { border-collapse: collapse; width: 100%; font-size: 15px; margin-top: 12px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); font-weight: 500; }
td.num { white-space: nowrap; font-variant-numeric: tabular-nums; }
tr.pick td { background: var(--tag); }
.tablewrap { overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 0 6px 6px; margin-top: 12px; }
.ask { margin-top: 16px; background: var(--surface); border: 1px solid var(--accent); border-radius: 6px; padding: 18px 22px; }
.ask ol { margin: 8px 0 0; padding-left: 22px; }
.ask li { margin: 8px 0; }
.assumed { margin-top: 16px; background: var(--surface); border: 1px solid var(--warn); border-radius: 6px; padding: 14px 20px; }
.assumed .eyebrow { color: var(--warn); }
footer { margin-top: 56px; font-size: 14px; color: var(--muted); border-top: 1px solid var(--line); padding-top: 16px; }
footer p { max-width: 90ch; }
code { font-family: var(--mono); font-size: 0.92em; }
.trio { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 16px; }
.settled { margin-top: 12px; }
.settled li strong { font-weight: 600; }
details.fold { margin-top: 64px; border-top: 3px solid var(--line); padding-top: 20px; }
details.fold > summary { cursor: pointer; font-family: var(--display); font-size: 30px; font-weight: 600; letter-spacing: 0.01em; }
details.fold > summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px; }
details.fold > summary span { font-family: var(--body); font-size: 15px; font-weight: 400; color: var(--muted); margin-left: 8px; }
details.fold + details.fold { margin-top: 28px; }
@media (max-width: 640px) { h2 { margin-top: 40px; } .facts div { border-right: 0; border-bottom: 1px solid var(--line); } .facts div:last-child { border-bottom: 0; } .facts div.span { grid-column: 1 / -1; } }
</style>
"""


def shape_block(s):
    letter = s["key"].upper()
    views = "\n".join(f'<figure>{img(f, alt)}<figcaption>{cap}</figcaption></figure>' for f, cap, alt in s["views"])
    pick = " pick" if s["key"] == "c" else ""
    return f"""
<section class="shape{pick}" id="shape-{s['key']}">
  <div class="head"><span class="letter">{letter}</span><h3>{s['name']}</h3><span class="tag">{s['tag']}</span></div>
  <p class="line">{s['line']}</p>
  <div class="views">
{views}
  </div>
  <div class="facts">
    <div><h4>Neck height</h4><span class="v">{s['heights']}</span></div>
    <div><h4>Follows the neck slope</h4><span class="v">{s['follows']}</span></div>
    <div><h4>Size</h4><span class="v">{s['size']}</span></div>
    <div><h4>Plastic</h4><span class="v">{s['grams']} g</span></div>
    <div><h4>Print time</h4><span class="v">{s['time']}</span></div>
    <div><h4>Pieces</h4><span class="v">{s['pieces']}</span></div>
  </div>
  <div class="two">
    <div><h4 class="good">Going for it</h4><ul>{''.join(f'<li>{x}</li>' for x in s['good'])}</ul></div>
    <div><h4 class="watch">Watch out</h4><ul>{''.join(f'<li>{x}</li>' for x in s['watch'])}</ul></div>
  </div>
  <p class="like"><strong>Already sold or printed like this:</strong> {s['like']}</p>
</section>"""


def compare_rows():
    rows = []
    for s in SHAPES:
        cls = ' class="pick"' if s["key"] == "c" else ""
        rows.append(f'<tr{cls}><td><a href="#shape-{s["key"]}"><strong>{s["key"].upper()}</strong> · {s["name"]}</a></td>'
                    f'<td>{s["heights"]}</td><td>{s["follows"]}</td><td class="num">{s["pieces"]}</td>'
                    f'<td class="num">{s["grams"]} g</td><td class="num">{s["time"]}</td></tr>')
    return "\n".join(rows)


SOLD = [
    ("MusicNomad Cradle Cube", "Cube, a cradle on each face", "3-1/2 to 5 in", "$20", "B", "https://www.guitarcenter.com/MusicNomad/Cradle-Cube-Neck-Support-for-All-Stringed-Instruments-1418660057080.gc", "Stable and grippy. Hollow shell, and its corners get in the way of fretwork."),
    ("Harley Benton GuitarTech", "Two-height cork block", "2-1/2 and 4 in", "$10", "A", "https://www.thomannmusic.com/harley_benton_guitartech_neck_rest.htm", "4.9 of 5 from 2,318 buyers. One buyer shims the body because it is tall."),
    ("StewMac Rock-n-Roller", "Hardwood rocker, cork cradle", "3-3/4 in (5 in acoustic)", "$52 to $89", "C", "https://www.stewmac.com/gifts/rock-n-roller-neck-rest", "Levels itself to the neck. Leaves the fingerboard edges open."),
    ("Dunlop System 65 Neck Cradle", "Pivoting cradle, one side flat", "4-1/2 x 5 x 5-1/2 in overall", "$42", "D", "https://www.jimdunlop.com/system-65-neck-cradle/", "Grips and self-aligns. Flips flat when unloaded; neoprene is not for long contact with nitro."),
    ("StewMac Neck Support Caul", "Long clampable trough", "1 in, or 3-1/2 in tall version", "$59", "E", "https://www.stewmac.com/luthier-tools-and-supplies/tools-by-job/tall-neck-support-caul", "Made for pressing and leveling frets. The tall one lets angled headstocks clear the bench."),
    ("StewMac Hi-Lo Featherweight", "Two-height foam block", "3 in block, 2-3/8 in cradle", "$43", "A", "https://www.stewmac.com/gifts/gifts-under-$50/hi-lo-featherweight-neck-rest", "Foam sold as safe on nitro and shellac."),
    ("Benedetto Neck Rest", "Two-tier plywood tower", "4-3/16 and 6-3/16 in", "$115", "B", "https://www.stewmac.com/shop-by-brand/benedetto/benedetto-neck-rest", "Felt lined, archtop heights."),
    ("D'Addario Headstand", "Folding stand", "5 in standing", "$13", "", "https://www.thomann.ae/planet_waves_gitarrenhalter_pwhds_reviews.htm", "Portable, but buyers say it is not firm and can fold up. No shape here copies it."),
]

PRINTED = [
    ("Bukken, Printables", "Curved two-height block", "3,330 downloads, 38 makes", "https://www.printables.com/model/527764-guitar-neck-rest", "All positive. Everyone adds leather, cork or foam."),
    ("heapstar, MakerWorld", "Small U block", "1,366 prints, 4.67 stars", "https://makerworld.com/en/models/151081", "Too small and too low. Makers scale it to 130 to 170 percent."),
    ("Doppelgang311, MakerWorld", "Upright block, glued TPU pads", "633 prints, 4.93 stars", "https://makerworld.com/en/models/562023", "Stable. Many skip the TPU for foam tape."),
    ("vidision 3-position, MakerWorld", "One piece: tall, short or rocker", "712 prints, 4.97 stars", "https://makerworld.com/en/models/1646072", "Rocker mode is the favourite. Needs supports."),
    ("PSG, MakerWorld", "Adjustable head on an M5 bolt", "248 prints, 5.0 stars", "https://makerworld.com/en/models/1261960", "The bolt is hard to find."),
    ("TroyDL rocker, Thingiverse", "Rocker, cork top and bottom", "322 likes", "https://www.thingiverse.com/thing:3085226", "Too low for acoustics. Slides on a smooth bench."),
]

sold_rows = "\n".join(
    f'<tr><td><a href="{u}">{n}</a></td><td>{sh}</td><td class="num">{h}</td><td class="num">{p}</td><td class="num">{c or "none"}</td><td>{note}</td></tr>'
    for n, sh, h, p, c, u, note in SOLD)
printed_rows = "\n".join(
    f'<tr><td><a href="{u}">{n}</a></td><td>{sh}</td><td>{pop}</td><td>{note}</td></tr>' for n, sh, pop, u, note in PRINTED)


# ---------------------------------------------------------------- round 2: the rocker
RK = REPORT["rocker"]
PARTS = REPORT["parts"]
BASS, GUITAR = RK["instruments"]["bass"], RK["instruments"]["guitar"]
FIX = RK["fixed_side"]
BAL = RK["ballast"]
R_IN = frac(RK["radius_mm"] / IN)
DZ_IN = frac(RK["neck_line_below_centre_mm"] / IN)
LOAD_LB = frac(RK["neck_load_kg"] * 2.2046, 2)
FIX_H = frac(FIX["height_in"])


def weight(g):
    """Grams with the same weight in ounces or pounds."""
    return f"{round(g)} g ({frac(g / 28.35, 2)} oz)" if g < 440 else f"{round(g)} g ({frac(g / 453.6, 4)} lb)"


def push_off_mm(part, ballast_g=0.0):
    """How far from the middle of the pad the neck's push lands with the rocker rolled under the bass.

    Statics of a rocker on a flat bench: the push passes through the bench contact, shifted by the rocker's
    own weight and any ballast, both of which hang below the centre of the bottom curve."""
    t = math.radians(BASS["roll_deg"])
    load = RK["neck_load_kg"] * 1000
    own = sum(SLICE2[f"{q}.stl"]["grams"] for q in ((part, "c2_lid") if part == "c2" else (part,)))
    arm = RK["neck_line_below_centre_mm"] + own / load * (RK["radius_mm"] - PARTS[part]["cm_height_mm"]) \
        + ballast_g / load * (RK["radius_mm"] - BAL["centre_height_mm"])
    return arm * math.sin(t)


C1_G, C1_T = quote("c1", table=SLICE2)
C2_G, C2_T = quote("c2", "c2_lid", table=SLICE2)
C3_G, C3_T = quote("c3", table=SLICE2)
ROUND1_G = SHAPES[2]["grams"]
BODY_SIZE = f"{mm(PARTS['c1']['size_mm'][0])} x {mm(PARTS['c1']['size_mm'][2])} x {mm(PARTS['c1']['size_mm'][1])} in"
MAPLE_LB = frac((PARTS["c3"]["volume_cm3"] + 100) * 0.70 / 453.6, 2)     # the closed body, its side cradle filled back in, in hard maple
OFF1 = frac(push_off_mm("c1") / IN, 16)
OFF2 = frac(push_off_mm("c2", BAL["steel_bb_g"]) / IN, 16)

ROCKERS = [
    dict(
        key="c1", name="Open frame", tag="Your pick",
        line=f"A frame about {mm(D['C_FR'])} in thick around one big opening. The same rocker as round 1 with a quarter less plastic.",
        heights=f"{HIGH} in, rocking", grams=C1_G, time=C1_T, inuse=weight(C1_G), pieces="1",
        good=[f"Lightest and fastest of the three: {C1_G} g against {ROUND1_G} g for the round 1 block.",
              "The opening is a handle, and it hangs on a peg.",
              "Nothing to fill, fit or glue except the pad and the tread."],
        watch=[f"Light. A hardwood rocker this size would weigh about {MAPLE_LB} lb (my estimate from maple's density). The tread stops it sliding, but a knock still moves it.",
               "One height."],
        views=[("c1-shape.png", f"Level: cradle at {HIGH} in", "Open-frame rocker on a 1 inch grid"),
               ("c1-use.png", f"Rolled {BASS['roll_deg']:.1f} degrees under the P-Bass neck stand-in", "Open-frame rocker rolled to match a sloping bass neck"),
               ("c1-extra.png", "Upside down: the two tread strips on the curve", "Open-frame rocker upside down, showing two strips on its curved bottom")],
    ),
    dict(
        key="c2", name="Weighted", tag="Stays where you put it",
        line="A closed body with a pocket low in the belly for ballast, shut by a press-in lid. A hang slot sits above it.",
        heights=f"{HIGH} in, rocking", grams=C2_G, time=C2_T,
        inuse=f"{frac((C2_G + BAL['sand_g']) / 453.6, 4)} lb with sand, {frac((C2_G + BAL['steel_bb_g']) / 453.6, 4)} lb with steel BBs", pieces="2, plus ballast",
        good=["Weighs about what a hardwood rocker this size would, so it stays put when you lower a neck onto it one-handed.",
              f"The weight sits {mm(BAL['centre_height_mm'])} in above the bench, far below the centre of the curve, so it swings back to level firmly.",
              "None of the rests surveyed has a weighted base."],
        watch=["A lid fit to get right. It would press in on crush ribs, the recipe from the cable bin.",
               "Loose BBs rattle unless they are bedded in glue. Sand does not.",
               f"The weight pulls the rocker toward level, so it follows the neck a little less freely: the neck's push lands about {OFF2} in from the middle of the pad with a full load of BBs, against {OFF1} in for the open frame. Still well inside the pad.",
               "Most plastic and the longest print of the three."],
        views=[("c2-shape.png", "Lid in. Hang slot above, ballast below", "Closed rocker with a slot and an oval lid on its side face"),
               ("c2-use.png", f"Rolled {BASS['roll_deg']:.1f} degrees under the neck", "Weighted rocker rolled to match a sloping bass neck"),
               ("c2-extra.png", f"Lid out: the pocket holds {frac(BAL['pocket_cm3'] / 16.387, 1)} cu in", "Weighted rocker with its lid removed and grey ballast in the pocket")],
    ),
    dict(
        key="c3", name="Two-way", tag="A second, fixed height",
        line=f"A closed body with a second cradle on one side. Standing, it rocks at {HIGH} in. Laid on its side it is a fixed block at {FIX_H} in.",
        heights=f"{HIGH} in rocking, {FIX_H} in fixed", heights_facts=f"{HIGH} in rocking<br>{FIX_H} in fixed", grams=C3_G, time=C3_T, inuse=weight(C3_G), pieces="1",
        good=["Two heights from one print, which answers the rocker's one-height limit.",
              f"On its side it stands on a {mm(PARTS['c3']['size_mm'][0])} x {mm(PARTS['c3']['size_mm'][1])} in face and cannot roll.",
              f"The fixed cradle has the slope built in: {FIX['slope_deg']:.1f} degrees, midway between the bass ({FIX['pitch_deg']['bass']:.1f}) and a Strat-size guitar ({FIX['pitch_deg']['guitar']:.1f}), so the pad bears along its length there too."],
        watch=["The fixed side works one way round only, low end toward the body. It would get an arrow.",
               f"No window: no handle, no hang hole, and {C3_G - C1_G} g more plastic than the open frame.",
               f"At {FIX_H} in the headstock has about {frac(FIX['under_headstock_in'])} in under it, against {frac(USE['3.75']['under_headstock_in'])} in at {HIGH} in.",
               "That built-in slope depends on the lying-flat measurement I do not have yet."],
        views=[("c3-shape.png", "Standing: rocking cradle on top, fixed cradle on the side", "Closed rocker with a second padded cradle scooped into its side face"),
               ("c3-use.png", f"Standing, rolled {BASS['roll_deg']:.1f} degrees under the neck", "Two-way rocker standing, rolled to match a sloping bass neck"),
               ("c3-extra.png", f"On its side: neck at {FIX_H} in on the fixed cradle", "Two-way rocker lying on its side with a bass neck on the side cradle")],
    ),
]


def rocker_block(s):
    views = "\n".join(f'<figure>{img(f, alt)}<figcaption>{cap}</figcaption></figure>' for f, cap, alt in s["views"])
    pick = " pick" if s["key"] == "c1" else ""
    return f"""
<section class="shape{pick}" id="body-{s['key']}">
  <div class="head"><span class="letter">{s['key'].upper()}</span><h3>{s['name']}</h3><span class="tag">{s['tag']}</span></div>
  <p class="line">{s['line']}</p>
  <div class="views">
{views}
  </div>
  <div class="facts">
    <div><h4>Neck height</h4><span class="v">{s.get('heights_facts', s['heights'])}</span></div>
    <div><h4>Plastic</h4><span class="v">{s['grams']} g</span></div>
    <div><h4>Print time</h4><span class="v">{s['time']}</span></div>
    <div><h4>Weight in use</h4><span class="v">{s['inuse']}</span></div>
    <div><h4>Pieces</h4><span class="v">{s['pieces']}</span></div>
  </div>
  <div class="two">
    <div><h4 class="good">Going for it</h4><ul>{''.join(f'<li>{x}</li>' for x in s['good'])}</ul></div>
    <div><h4 class="watch">Watch out</h4><ul>{''.join(f'<li>{x}</li>' for x in s['watch'])}</ul></div>
  </div>
</section>"""


def rocker_rows():
    rows = []
    for s in ROCKERS:
        cls = ' class="pick"' if s["key"] == "c1" else ""
        rows.append(f'<tr{cls}><td><a href="#body-{s["key"]}"><strong>{s["key"].upper()}</strong> · {s["name"]}</a></td>'
                    f'<td>{s["heights"]}</td><td class="num">{s["grams"]} g</td><td class="num">{s["time"]}</td>'
                    f'<td>{s["inuse"]}</td><td>{s["pieces"]}</td></tr>')
    return "\n".join(rows)


# ---------------------------------------------------------------- round 3: a longer cradle
LONG = REPORT["long"]["variants"]
L2 = REPORT["long"]["round2"]
PICK3 = "c1b"
START_IN = frac(LONG[PICK3]["cradle_start_from_nut_mm"] / IN)
C1_LEN = mm(L2["cradle_mm"])


def push_off_long(k):
    """The same statics as push_off_mm(), for a longer-cradle body rolled under the bass."""
    v = LONG[k]
    t = math.radians(v["instruments"]["bass"]["roll_deg"])
    own = SLICE3[f"{k}.stl"]["grams"]
    arm = RK["neck_line_below_centre_mm"] + own / (RK["neck_load_kg"] * 1000) * (RK["radius_mm"] - PARTS[k]["cm_height_mm"])
    return arm * math.sin(t)


def tread_in(v):
    """Length of each tread strip along the curve: it stops 4 degrees short of each end of the arc (concepts.scad, tread)."""
    return mm(2 * math.radians(v["roll_limit_deg"] - 4) * RK["radius_mm"])


def nth(n):
    return f"{n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'}"


for k, v in LONG.items():
    v["grams"], v["time"] = quote(k, table=SLICE3)
    v["cradle"], v["rocker"] = mm(v["cradle_mm"]), mm(v["rocker_chord_mm"])
    v["bass"], v["guitar"] = v["instruments"]["bass"], v["instruments"]["guitar"]
    v["size"] = f"{mm(PARTS[k]['size_mm'][0])} x {mm(PARTS[k]['size_mm'][2])} x {mm(PARTS[k]['size_mm'][1])} in"
    v["reserve"] = round(v["roll_limit_deg"])
LA, LB, LC = LONG["c1a"], LONG["c1b"], LONG["c1c"]
EXTRA_MIN = SLICE3[f"{PICK3}.stl"]["minutes"] - SLICE2["c1.stl"]["minutes"]
OFF3 = frac(push_off_long(PICK3) / IN, 16)
NEED = round(max(LB["bass"]["roll_deg"], LB["guitar"]["roll_deg"]))

LENGTHS = [
    dict(
        key="c1a", name=f"{LA['cradle']} in cradle, same rocker", tag="Least plastic",
        line=f"The round 2 body with its cradle stretched from {C1_LEN} to {LA['cradle']} in. The sides stand almost straight.",
        good=[f"{frac((LA['cradle_mm'] - L2['cradle_mm']) / IN)} in more cradle than round 2 for {LA['grams'] - C1_G} g more plastic and {SLICE3['c1a.stl']['minutes'] - SLICE2['c1.stl']['minutes']} minutes.",
              "Takes about the same bench as round 2: the cradle is as long as the rocker under it.",
              f"Rolls {LA['bass']['roll_deg']:.1f} degrees under the bass, as before, with about {LA['reserve']} degrees of curve in reserve each way."],
        watch=[f"The shortest of the three. On the bass it stops short of the {nth(LA['bass']['last_fret_over_cradle'] + 1)} fret.",
               "If the point is more surface, this is the small step."],
    ),
    dict(
        key="c1b", name=f"{LB['cradle']} in cradle, same rocker", tag="My pick",
        line=f"An {LB['cradle']} in cradle on the round 2 rocker. The legs lean out from the curve to carry the ends of the cradle.",
        good=[f"Nearly twice the surface of round 2: {LB['cradle']} in against {C1_LEN}.",
              f"On the bass it carries the neck from {START_IN} in past the nut to the {nth(LB['bass']['last_fret_over_cradle'])} fret; on a Strat-size guitar, to the {nth(LB['guitar']['last_fret_over_cradle'])}.",
              f"Keeps the whole rocker: about {LB['reserve']} degrees of curve each way, where the neck asks for about {NEED}."],
        watch=[f"The most plastic and the longest print of the three, by a little: {LB['grams'] - C1_G} g and {EXTRA_MIN} minutes over round 2.",
               f"It has to sit clear of the headstock and the tuners, so its middle ends up {mm(LB['rest_centre_from_nut_mm'])} in from the nut."],
    ),
    dict(
        key="c1c", name=f"{LC['cradle']} in cradle, {LC['rocker']} in rocker", tag="Smaller rocker",
        line=f"The same {LC['cradle']} in cradle on a rocker a third shorter. The legs lean out further to reach the ends.",
        good=["The same cradle and the same support under the neck as C1b.",
              f"Still about {LC['reserve']} degrees of curve each way, where the neck asks for about {NEED}.",
              "The lighter-looking of the two: a long deck on a small foot."],
        watch=[f"The smaller rocker saves almost nothing: {LB['grams'] - LC['grams']} g and {SLICE3['c1b.stl']['minutes'] - SLICE3['c1c.stl']['minutes']} minutes. The legs grow by about what the curve loses.",
               f"Less in reserve than C1b: {LC['reserve']} degrees each way against {LB['reserve']}, and tread strips {tread_in(LC)} in long against {tread_in(LB)}.",
               f"An {LC['cradle']} in top on a {LC['rocker']} in foot. Under a neck that changes nothing; empty, a push on one end reaches the end of the curve sooner."],
    ),
]


def length_block(s):
    v = LONG[s["key"]]
    k = s["key"]
    name = f"C1{k[-1]}"
    views = [(f"{k}-shape.png", f"Level: {v['cradle']} in cradle at {HIGH} in", f"Open-frame rocker with its cradle {v['cradle']} inches long, on a 1 inch grid"),
             (f"{k}-use.png", f"Rolled {v['bass']['roll_deg']:.1f} degrees under the P-Bass neck stand-in, starting {START_IN} in from the nut",
              f"The rocker with the {v['cradle']} inch cradle rolled under a sloping bass neck, the nut just past its end"),
             (f"side-{k}.png", "Cut through the middle, to scale. Dashed: the round 2 body.",
              f"Side view: cradle {v['cradle']} inches long on a rocker {v['rocker']} inches long, with the shorter round 2 outline dashed over it")]
    figs = "\n".join(f'<figure>{img(f, alt)}<figcaption>{cap}</figcaption></figure>' for f, cap, alt in views)
    pick = " pick" if k == PICK3 else ""
    return f"""
<section class="shape{pick}" id="len-{k}">
  <div class="head"><span class="letter">{name}</span><h3>{s['name']}</h3><span class="tag">{s['tag']}</span></div>
  <p class="line">{s['line']}</p>
  <div class="views">
{figs}
  </div>
  <div class="facts">
    <div><h4>Cradle</h4><span class="v">{v['cradle']} in</span></div>
    <div><h4>Rocker</h4><span class="v">{v['rocker']} in</span></div>
    <div><h4>Plastic</h4><span class="v">{v['grams']} g</span></div>
    <div><h4>Print time</h4><span class="v">{v['time']}</span></div>
    <div class="span"><h4>Size</h4><span class="v">{v['size']}</span></div>
  </div>
  <div class="two">
    <div><h4 class="good">Going for it</h4><ul>{''.join(f'<li>{x}</li>' for x in s['good'])}</ul></div>
    <div><h4 class="watch">Watch out</h4><ul>{''.join(f'<li>{x}</li>' for x in s['watch'])}</ul></div>
  </div>
</section>"""


def length_rows():
    rows = [f'<tr><td class="num">C1, round 2</td><td class="num">{C1_LEN} in</td><td class="num">{mm(L2["rocker_chord_mm"])} in</td>'
            f'<td class="num">{round(L2["roll_limit_deg"])} degrees</td>'
            f'<td class="num">{C1_G} g</td><td class="num">{C1_T}</td></tr>']
    for s in LENGTHS:
        v = LONG[s["key"]]
        cls = ' class="pick"' if s["key"] == PICK3 else ""
        rows.append(f'<tr{cls}><td class="num"><a href="#len-{s["key"]}"><strong>C1{s["key"][-1]}</strong></a></td>'
                    f'<td class="num">{v["cradle"]} in</td><td class="num">{v["rocker"]} in</td>'
                    f'<td class="num">{v["reserve"]} degrees</td>'
                    f'<td class="num">{v["grams"]} g</td><td class="num">{v["time"]}</td></tr>')
    return "\n".join(rows)


# The design: round 2's C1 with the edges rounded over (Brian, 2026-11-23). Solid c1r, sliced on its own.
RO = REPORT["roundover"]
CONCEPT_G = quote("c1r", table=SLICE4)[0]
DES_G, DES_T = round(PRINT3MF["slice"]["grams"]), PRINT3MF["slice"]["time"]
DES_SIZE = BUILD["solid"]["size_in"] + " in"
CH, PADFIT, OVER, SEAMS = BUILD["channel"], BUILD["pad"], BUILD["overhangs"], PRINT3MF["slice"]["seams"]
TAPE_CUT, PAD_CUT = CH["tape_cut_in"], PADFIT["cut_in"]
R_END_IN = frac(RO["cradle_ends_mm"] / IN, 16)
R_EDGE_IN = frac(RO["other_edges_mm"] / IN, 16)
EDGE_STEPS = round(RO["other_edges_mm"] / 0.30)     # layers in one small roundover at the 0.30 mm the quotes are sliced at
DES_VIEWS = [("../neck-rest-hero.png", f"The model: cradle at {HIGH} in, cork pad in place", "Open-frame rocker with rounded edges and a cork pad"),
             ("c1r-use.png", f"Rolled {BASS['roll_deg']:.1f} degrees under the P-Bass neck stand-in", "The rocker rolled to match a sloping bass neck"),
             ("../neck-rest-under.png", "Upside down: your 2 in grip tape in its channel", "The rocker upside down, showing one wide strip of black tape recessed in its curved bottom")]
C1_FIGS = "\n".join(f'<figure>{img(f, alt)}<figcaption>{cap}</figcaption></figure>' for f, cap, alt in DES_VIEWS)

html = f"""<title>Neck Rest Shapes</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
{CSS}
<main>
<header>
  <span class="eyebrow">Guitar neck rest · the design · {VERSION} · {DATE}</span>
  <h1>Neck Rest: the Design</h1>
  <p>You kept round 2's C1, the open-frame rocker with the {C1_LEN} in cradle, and said build it. This version shows the real model: the rounded edges you asked for, and one recessed channel in the bottom for your 2 in grip tape in place of the two tread strips. The 3MF is made and sliced; plastic and time below are from that slice on the X2D.</p>
  <nav class="jump" aria-label="Sections">
    <a href="#body-c1">The body</a><a href="#edges">Edges</a><a href="#tape">Grip tape</a><a href="#does">What it does</a><a href="#settled">What is settled</a><a href="#pad">Pad</a><a href="#ask">Where it stands</a><a href="#round3">Round 3</a><a href="#round2">Round 2</a><a href="#round1">Round 1</a>
  </nav>
</header>

<h2 id="body-c1">The body</h2>
<p>An open frame about {mm(D['C_FR'])} in thick around one opening, on a curved bottom. One piece, printed on its side. The opening is the handle, and it hangs on a peg.</p>
<div class="views wide">
{C1_FIGS}
</div>
<div class="facts wide">
  <div><h4>Neck height</h4><span class="v">{HIGH} in</span></div>
  <div><h4>Cradle</h4><span class="v">{C1_LEN} in long</span></div>
  <div><h4>Plastic</h4><span class="v">{DES_G} g</span></div>
  <div><h4>Print time</h4><span class="v">{DES_T}</span></div>
  <div><h4>Weight</h4><span class="v">{frac(DES_G / 28.35, 2)} oz</span></div>
</div>

<h2 id="edges">Edges</h2>
<p>New on 2026-11-23, from your two notes. The body is otherwise the one you kept.</p>
<div class="views wide">
<figure>{img("c1r-end.png", "Close view of one end of the cradle: the end rolls off in a curve below the cork pad, and the other edges are slightly rounded")}<figcaption>One cradle end, close up.</figcaption></figure>
<figure>{img("end-section.png", "Side view cut through the middle of one cradle end, to scale: a quarter inch roundover where the square end was, with the pad stopping where the roundover starts")}<figcaption>The same end cut through the middle, to scale.</figcaption></figure>
</div>
<ul class="settled">
  <li><strong>The two cradle ends, {R_END_IN} in:</strong> the edge the neck passes over at each end now rolls off instead of ending square. The roundover runs the full width of the end, across the cradle and the shoulder on each side of it.</li>
  <li><strong>Every other outside edge, {R_EDGE_IN} in:</strong> both faces all the way round, the edge of the opening on both faces, and the two long rims of the cradle.</li>
  <li><strong>Left square:</strong> the edges of the grip tape channel on the bottom, because the tape seats against them.</li>
  <li><strong>What it costs:</strong> very little. The pad is the size it was, the cradle floor stays level for {frac(RO['level_floor_mm'] / IN)} in between the two roundovers, and the concept slice was {CONCEPT_G} g against {C1_G} g with square edges.</li>
  <li><strong>How it prints:</strong> the body prints on its side, so the nozzle draws each cradle end as a smooth curve on every layer. The {R_EDGE_IN} in roundover around the two faces is built from layers instead: about {EDGE_STEPS} steps on the top face, and on the bottom face it starts on the plate, where the first layers can come out a little rough. The plate side can become a small bevel if it looks poor in Studio's preview.</li>
</ul>

<h2 id="tape">Grip tape channel</h2>
<p>New on 2026-11-23: one channel in the bottom for your 2 in rubber grip tape, in place of the two cork strips.</p>
<div class="views wide">
<figure>{img("../neck-rest-under.png", "The rocker upside down with a 2 inch strip of black grip tape recessed along its curved bottom")}<figcaption>Upside down, tape in.</figcaption></figure>
<figure>{img("../neck-rest-section-across.png", "The model cut across the neck, to scale: bass neck on the cork pad at the top, grip tape in a shallow channel at the bottom")}<figcaption>Cut across the neck, to scale. The blue line is the model itself.</figcaption></figure>
</div>
<ul class="settled">
  <li><strong>Size:</strong> 2 in wide plus 1/64 in each side, centred, with {frac(CH['lip_each_side_mm'] / IN, 16)} in of plastic left either side. It runs along the curve and stops short of both ends, so the tape ends are boxed in.</li>
  <li><strong>Tape:</strong> cut one piece {TAPE_CUT} in.</li>
  <li><strong>Depth, my call:</strong> {CH['depth_mm']:g} mm, about 1/64 in. I do not know how thick your tape is, so the channel is shallower than any grip tape I know of: the rest then stands on rubber, not on the plastic either side. If your tape is thinner than 1/32 in, tell me and I will make it shallower still.</li>
</ul>

<h2 id="does">What it does</h2>
<p>The bottom is one arc of a circle with a {R_IN} in radius. Lay a neck on it and the rocker rolls until the pad lies along the neck: {BASS['roll_deg']:.1f} degrees under the bass at this height, about {GUITAR['roll_deg']:.1f} under a Strat-size guitar. A level cradle of the same length would touch at one end and stand {frac(BASS['level_cradle_gap_mm'] / IN, 16)} in clear at the other.</p>
<div class="views wide">
<figure>{img("roll-empty.png", "Side view cut through the middle of the open rocker, sitting level on the bench with nothing on it")}<figcaption>Cut through the middle, to scale.</figcaption></figure>
<figure>{img("roll-bass.png", "The same rocker rolled 4.4 degrees with a bass neck lying along its pad")}<figcaption>The pad lies along the neck.</figcaption></figure>
</div>
<p>The cross marks the centre of the bottom curve, {DZ_IN} in above the line the neck bears on. Because the neck sits below that centre, weight on the pad steadies the rocker instead of sending it rolling, and it swings back to level when the instrument comes off.</p>
<p><strong>Why that radius.</strong> A flatter curve resists the neck and loads one end of the pad; a tighter one rolls too freely. At {R_IN} in my statics put the neck's push within {OFF1} in of the middle of the {mm(D['XC_TOP'])} in cradle. That assumes about {LOAD_LB} lb on the rest, which is an estimate, not a weighing.</p>

<h2 id="settled">What is settled</h2>
<p>The body is as drawn in round 2, with the rounded edges added on 2026-11-23. Two lines are my calls that you have not confirmed, and they say so.</p>
<ul class="settled">
  <li><strong>Size:</strong> {DES_SIZE} (long, wide, tall).</li>
  <li><strong>Edges:</strong> a {R_END_IN} in roundover on the two cradle ends and {R_EDGE_IN} in on every other outside edge. You asked for both; the sizes are mine.</li>
  <li><strong>Height:</strong> the neck sits {HIGH} in above the bench, the height of StewMac's solid-body Rock-n-Roller. Because the rest rolls to meet the neck, it does not need the lying-flat measurement I asked for earlier. That measurement only changes how far it rolls.</li>
  <li><strong>Cradle:</strong> {mm(CW_MM)} in wide, {mm(D['XC_TOP'])} in long, about {mm(D['CD'])} in deep, with room left for a pad.</li>
  <li><strong>Curve:</strong> one arc with a {R_IN} in radius, {mm(D['C_CHORD'])} in from end to end.</li>
  <li><strong>Grip:</strong> one recessed channel on the curve for your 2 in rubber grip tape, so it does not slide on a smooth bench. The recess keeps the tape's edges from peeling.</li>
  <li><strong>Printing:</strong> on its side, so the nozzle draws the rocking curve as one smooth line per layer, and the cradle's 45 degree rim needs no supports.</li>
  <li><strong>Strength, my call:</strong> PLA, 2 walls, 15% infill, for string changes, setups and cleaning. If you level, tap or press frets on it, say so and it gets more walls and infill.</li>
  <li><strong>Pad, my call:</strong> 1/16 in self-adhesive cork, one piece {PAD_CUT} in. The other two choices are below.</li>
</ul>

<h2 id="pad">Pad</h2>
<p>What lines the cradle. The model is cut for 1/16 in cork unless you say otherwise. I have not suggested your rubber tape here: rubber is one of the materials sellers warn about against a nitro finish.</p>
<div class="trio">
<figure>{img("c1r-pad-cork.png", "Open-frame rocker with a tan cork pad")}<figcaption>Cork</figcaption></figure>
<figure>{img("c1r-pad-felt.png", "Open-frame rocker with a green felt pad")}<figcaption>Felt</figcaption></figure>
<figure>{img("c1r-pad-tpu.png", "Open-frame rocker with a black printed TPU pad")}<figcaption>Printed TPU</figcaption></figure>
</div>
<div class="tablewrap"><table>
<thead><tr><th>Material</th><th>How it goes on</th><th>Finish safety</th><th>Note</th></tr></thead>
<tbody>
<tr><td><strong>Cork sheet, 1/16 in</strong></td><td>Self-adhesive sheet, cut with scissors</td><td>The luthier standard, but reviewers of one cork-lined rest caution about nitro</td><td>What StewMac, Hosco and Harley Benton use. My pick unless the guitar is nitro.</td></tr>
<tr><td><strong>Felt, 1/16 to 1/8 in</strong></td><td>Self-adhesive sheet</td><td>Sold as finish-safe (Benedetto)</td><td>Less grip than cork under the tread, by my reckoning; not tested.</td></tr>
<tr><td><strong>Printed TPU</strong></td><td>A pad and two strips printed as extra parts, glued in</td><td>No data found for TPU on nitro</td><td>No shopping if you have the spool. Makers of one popular printed rest often swap its TPU pads for foam tape.</td></tr>
</tbody></table></div>
<p>Nitro lacquer is the finish that reacts: Fender warns against vinyl, plastic and rubber tubing touching it. As far as I know your Mexican P-Bass is polyester, which does not care. It matters if the guitar is nitro.</p>

<h2 id="prove">Checked on the real model</h2>
<p>Each of these was measured on the exported model or read from the sliced file, not taken from the drawing.</p>
<ul class="settled">
  <li><strong>The solid:</strong> one closed body, {DES_SIZE}.</li>
  <li><strong>Cradle ends:</strong> the floor is level for {frac(BUILD['cradle_mm_got_want']['level_floor_mm'] / IN)} in, then follows the {R_END_IN} in curve. Both measured to within 0.05 mm of the design.</li>
  <li><strong>Pad:</strong> a {PAD_CUT} in piece fits its seat with {PADFIT['end_margin_mm']:.1f} mm to spare at each end and {PADFIT['side_margin_mm']:.1f} mm each side, and puts the top of the cork at {HIGH} in.</li>
  <li><strong>Necks:</strong> with the bass and guitar stand-ins lying on the pad, nothing printed comes closer to the neck than the pad's thickness.</li>
  <li><strong>Overhangs:</strong> the cradle's upper rim is {OVER['cradle_upper_rim_deg']:.0f} degrees from upright at its worst, and the slicer made no supports. The only steeper surfaces are the {R_EDGE_IN} in roundover on the plate-side face and the channel's {OVER['channel_wall_ledge_mm']:g} mm side wall.</li>
  <li><strong>Seam:</strong> all {SEAMS['loops']} outer loops start on the cradle side or inside the top of the opening. None is on the rocking curve.</li>
  <li><strong>Settings in the sliced file:</strong> 2 walls, 15% infill, 2-loop skirt, no brim, textured plate at {PRINT3MF['slice']['bed_C']} C.</li>
</ul>
<p><strong>Not proven by any of that:</strong> how the {R_EDGE_IN} in roundover looks on the plate-side face. Look at the first few layers in Studio's preview. If it looks rough I change that side to a small bevel.</p>

<section class="assumed">
  <span class="eyebrow">Assumed, not confirmed</span>
  <ul>
    <li>No guitar is on file. The guitar roll angle uses a Strat-size stand-in, {frac(GUITAR_TAIL)} in from the tail of the body to the nut.</li>
    <li>The {FLAT} in lying-flat neck height is worked out from Fender body sizes, not measured. The roll angles follow from it; the shape does not.</li>
    <li>About {LOAD_LB} lb on the rest is an estimate, not a weighing. The load figures follow from it.</li>
  </ul>
</section>

<h2 id="ask">Where it stands</h2>
<section class="ask">
  <p><strong>Built on 2026-11-23, not printed.</strong> The file is <code>guitar-neck-rest.3mf</code>: one plate, one part, lying on its side, {DES_G} g and {DES_T} in PLA. Open it in Bambu Studio, pick the colour, and look at the sliced preview before you print.</p>
  <p>Still yours to change:</p>
  <ol>
    <li><strong>Tape thickness:</strong> the channel is {CH['depth_mm']:g} mm deep. Tell me if your tape is thinner than 1/32 in.</li>
    <li><strong>The roundovers:</strong> {R_END_IN} in on the cradle ends and {R_EDGE_IN} in elsewhere are my sizes. Say bigger or smaller.</li>
    <li><strong>Pad:</strong> cork unless you say felt or printed TPU. Tell me if the guitar has a nitro finish; that is the one case where I would not use cork.</li>
    <li><strong>Fret work:</strong> tell me if you level, tap or press frets on it.</li>
  </ol>
</section>

<details class="fold" id="round3">
<summary>Round 3: longer cradles <span>not taken</span></summary>

<p>You asked for a longer surface under the neck, on a rocker the same size or smaller. I drew three, and you kept round 2's C1. They stay here for reference.</p>

<h2>What a longer cradle changes</h2>
<p>Round 2's cradle was {C1_LEN} in long. Everything else carries over: the {R_IN} in curve, the {HIGH} in height, the {mm(D['YC'])} in width, the cradle's cross-section, the {mm(D['C_FR'])} in frame, the two tread strips, and printing on its side.</p>
<ul class="settled">
  <li><strong>The ends.</strong> The cradle is now a straight beam with square ends, and the legs run out to its corners, so the pad is carried along its whole length.</li>
  <li><strong>Where it sits.</strong> A long cradle has to stay clear of the headstock and the tuners, so I drew it starting {START_IN} in from the nut. Its middle is then further up the neck, and the {LB['cradle']} in bodies roll {LB['bass']['roll_deg']:.1f} degrees under the bass, against {L2['instruments']['bass']['roll_deg']:.1f} degrees in round 2.</li>
  <li><strong>Rolling matters more.</strong> A level {LB['cradle']} in cradle would touch at one end and stand {frac(LB['bass']['level_cradle_gap_mm'] / IN, 16)} in clear at the other under the bass. Rolled, my statics put the neck's push within {OFF3} in of the middle of the pad, as in round 2. That still assumes about {LOAD_LB} lb on the rest.</li>
  <li><strong>The smaller rocker.</strong> The curve keeps its {R_IN} in radius, which is what sets how it rolls; only its length changes. Under either instrument the line of contact moves {frac(LB['bass']['bench_contact_moves_mm'] / IN)} to {frac(LB['guitar']['bench_contact_moves_mm'] / IN)} in from the middle, so a {LC['rocker']} in rocker still has far more curve than it uses. I expected it to save plastic. It does not: the two {LB['cradle']} in bodies slice {LB['grams'] - LC['grams']} g apart.</li>
</ul>

<h2>Three lengths</h2>
<p>Same frame, same cradle section, same curve. What differs is how long the cradle is and how much curve sits under it.</p>
{''.join(length_block(s) for s in LENGTHS)}

<h2>Side by side</h2>
<div class="tablewrap"><table>
<thead><tr><th>Body</th><th>Cradle</th><th>Rocker</th><th>Curve each way</th><th>Plastic</th><th>Print time</th></tr></thead>
<tbody>
{length_rows()}
</tbody></table></div>
<p><strong>Why C1b was my pick.</strong> You asked for more surface, and {LB['cradle']} in is nearly twice round 2's for {LB['grams'] - C1_G} g more plastic and {EXTRA_MIN} minutes. Between the two {LB['cradle']} in bodies the slices are a wash, so I would keep the whole rocker: the extra curve costs nothing and leaves more in reserve. C1c works just as well under a neck; choosing it is a call on looks, and that one is yours. C1a is the one if {LA['cradle']} in is enough.</p>
<p>These three are not the only lengths. Any cradle up to about 9 in fits the printer on its side, on either rocker.</p>

</details>

<details class="fold" id="round2">
<summary>Round 2: the other rocker bodies <span>you picked C1</span></summary>

<h2>Three bodies</h2>
<p>Same outline, same cradle, same curve. What differs is what fills the middle. C1, the one you picked, is at the top of this page.</p>
{''.join(rocker_block(s) for s in ROCKERS[1:])}

<h2 id="compare">Side by side</h2>
<div class="tablewrap"><table>
<thead><tr><th>Body</th><th>Neck height</th><th>Plastic</th><th>Print time</th><th>Weight in use</th><th>Pieces</th></tr></thead>
<tbody>
{rocker_rows()}
</tbody></table></div>
<p><strong>Why C1 was my pick.</strong> It is the simplest thing that does the job: one piece, the least plastic, and the tread already answers the sliding complaint. Take C3 if a second, lower height is worth {C3_G - C1_G} g and losing the handle. Take C2 if you want it to feel like the wooden ones. C3 can also carry ballast, in a pocket on the face it lies on; C1 cannot.</p>

</details>

<details class="fold" id="round1">
<summary>Round 1: the six base shapes and the research <span>for reference</span></summary>

<h2>What the height does</h2>
<p>With the body on the bench, a rest lifts the neck and the whole instrument pitches up a few degrees, riding on the tail edge of the body. More height means more room under the headstock for the tuners and a string winder, and a steeper slope across the cradle.</p>
<figure class="wide">{img("use.png", "Side view of a bass lying on a bench at three neck heights: flat with a long trough, on a 2-1/2 inch rest, and on a 3-3/4 inch rest")}
<figcaption>Bass stand-in, to scale. Lying flat the neck back is about {FLAT} in up and {USE['1.25']['under_headstock_in']:.1f} in clears under the headstock. A {LOW} in rest pitches it {TILT_LOW:.1f} degrees ({USE['2.5']['under_headstock_in']:.1f} in under the headstock); {HIGH} in pitches it {TILT_HIGH:.1f} degrees ({USE['3.75']['under_headstock_in']:.1f} in). Rests sold for solid bodies run 2-1/2 to 4-1/4 in; acoustic ones 5 to 6-1/4 in.</figcaption></figure>

<h2>Six base shapes</h2>
<p>A, B and F hold the cradle level. C and D turn to meet the neck. E keeps the instrument flat instead. Slices here are PLA, 2 walls, 15% infill, like round 2.</p>
{''.join(shape_block(s) for s in SHAPES)}

<h2>Side by side</h2>
<div class="tablewrap"><table>
<thead><tr><th>Shape</th><th>Neck height</th><th>Follows the slope</th><th>Pieces</th><th>Plastic</th><th>Print time</th></tr></thead>
<tbody>
{compare_rows()}
</tbody></table></div>

<h2>The cradle</h2>
<p>Wide and shallow, like the ones sold: 2-1/2 in across, about 1/2 in deep, on a 1-3/4 in radius. Both necks sit on the bottom of the curve with room at the sides, from the nut to the 12th fret. The rim angle is 45 degrees so the groove prints on a vertical wall without supports.</p>
<figure class="wide">{img("fit.png", "Cross-sections of the cradle with a bass neck and a guitar neck sitting in it, each also shown dashed at its 12th fret width")}
<figcaption>Cross-section at the rest, to scale. Solid: the neck where the rest sits, between the 2nd and 3rd frets. Dashed: the same neck at the 12th fret. The bass's 12th fret width is worked out from its nut and heel widths, not a published figure.</figcaption></figure>

<h2>What is already out there</h2>
<p>Seventeen rests on sale and about twenty printable ones were surveyed. The ones that shaped the six:</p>
<div class="tablewrap"><table>
<thead><tr><th>Sold</th><th>Shape</th><th>Neck height</th><th>Price</th><th>Shape here</th><th>What buyers say</th></tr></thead>
<tbody>
{sold_rows}
</tbody></table></div>
<div class="tablewrap"><table>
<thead><tr><th>Printable</th><th>Shape</th><th>Popularity</th><th>What makers say</th></tr></thead>
<tbody>
{printed_rows}
</tbody></table></div>
<p><strong>Lessons the printable designs teach.</strong> Too low and too small is the most common complaint. Narrow bases tip. Bare plastic slides, so makers add cork or rubber underneath. A design scaled up for an acoustic gets a cradle that is too big; acoustics need height, not width. None of the designs surveyed has a weighted base or built-in non-slip feet, so both are open to add.</p>
</details>

<footer>
  <p>Built by <code>projects/Guitar-neck-rest/pipeline/concepts.py</code> (parameters, drawings), <code>concepts.scad</code> (solids, renders) and <code>options_page.py</code> (this page). Slices: Bambu Studio CLI, X2D 0.6 nozzle, 0.30 mm Standard, Bambu PLA Basic, 2 walls, 15% infill.</p>
  <p>Not verified in the research: retailer pages for several products blocked reading, so some review notes are thin; the Hosco and Crimson entries came from search snippets; printable designs were read from their text, not their pictures.</p>
</footer>
</main>
"""

OUT.write_text(html)
print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)")
for s in ROCKERS:
    print(s["key"].upper(), s["name"], s["heights"], s["grams"], "g", s["time"], "|", s["inuse"])
for k, v in LONG.items():
    print(k, "cradle", v["cradle"], "rocker", v["rocker"], v["grams"], "g", v["time"], "| roll", v["bass"]["roll_deg"], v["guitar"]["roll_deg"],
          "| reserve", v["reserve"], "| push off pad middle (mm)", round(push_off_long(k), 2), "| tread", tread_in(v))
print("push off pad middle (mm): c1", round(push_off_mm("c1"), 2), "c2 sand", round(push_off_mm("c2", BAL["sand_g"]), 2),
      "c2 BBs", round(push_off_mm("c2", BAL["steel_bb_g"]), 2), "c3", round(push_off_mm("c3"), 2))
