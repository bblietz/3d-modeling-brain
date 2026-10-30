"""Speaker-cab logo options page: the Logo Dude at three widths on the front of
Brian's walnut 1x12 (Cab-Blietz-1x12-hardwood), true scale, with the grille
frame band and the speaker cutout drawn through the cloth, and the screw
spots each mounting option can use. Writes projects/Logodude/cab-logo-options.html.

Front geometry comes from logodude.py (traced, cleaned, smoothed ink) rescaled
so the backer is W wide; the margin scales with the artwork."""
import json
import math
import pathlib
import sys

import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import logodude as L  # noqa: E402  (builds the 4 in badge on import)

BADGE_W = 104.2                    # mm, the 4 in badge's width, the margin reference
WIDTHS_IN = [3.0, 3.5, 4.0]   # amp-logo sizes (Brian 2026-10-28: 5 to 7 in was 'WAY too big')
BACKER_T = 3.0                     # mm, as the badge
INK_H = 1.0

# Cab front (cab.json, 2026-09-13 order): external 508 x 457.2, walnut 19 mm, 1/2 in roundover,
# grill frame 462 x 411.2 from 12 x 40 mm strips, 4 mm clear of the 470 x 419.2 recess,
# cutout 281 mm centered in the chamber, Cannabis Rex flange about 310 mm.
CAB_W, CAB_H = 508.0, 457.2
SHELL = 19.0
FRAME_W, FRAME_H = 462.0, 411.2
STRIP = 40.0
CUTOUT_D, FLANGE_D = 281.0, 310.0
LOGO_INSET = 10.0                  # mm from the frame's top-left corner to the logo's bounding box

HEAD_D = 5.5                       # #4 flat head, black oxide (a #6's 7 mm head is wider than the hair at these sizes)
SHANK_D = 2.8                      # #4 shank
BOSS_D = 10.0                      # printed boss around an M3 heat-set insert, seen from behind
SPOT_CLEAR = 1.0                   # extra material past a head or boss
SHANK_IN = 6.0                     # mm, screw shank kept inside the strip's edges (wood on both sides)


def rings(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        p = p.simplify(0.04)   # drawing only; the CAD keeps the full spline knots
        out.append([list(p.exterior.coords)] + [list(h.coords) for h in p.interiors])
    return out


def scaled(w_in):
    """Ink and backer polygons, backer w_in wide, the margin scaled with the art."""
    W = w_in * 25.4
    s = W / BADGE_W
    L.MARGIN, L.MARGIN_GROW, L.MIN_MARGIN, L.SMOOTH_OUTLINE_MM = 3.5 * s, 5.0 * s, 2.5 * s, 2.5 * s
    K = L.K * s
    for _ in range(4):
        ink, backer = L.build_2d(K)
        x0, y0, x1, y1 = backer.bounds
        K *= W / (x1 - x0)
    ink, backer = L.build_2d(K)
    return ink, backer, K, s


def farthest_pair(region):
    """Two points of a region as far apart as possible (on its boundary)."""
    pts = []
    for p in getattr(region, "geoms", [region]):
        pts += list(p.exterior.coords)[::3]
    pts = np.array(pts)
    if len(pts) < 2:
        return []
    d = ((pts[:, None, :] - pts[None, :, :]) ** 2).sum(-1)
    i, j = np.unravel_index(d.argmax(), d.shape)
    return [tuple(map(float, pts[i])), tuple(map(float, pts[j]))]


def layout(w_in):
    ink, backer, K, s = scaled(w_in)
    x0, y0, x1, y1 = backer.bounds
    # frame coordinates: origin at the frame's top-left corner, y down
    ox, oy = LOGO_INSET - x0, LOGO_INSET + y1
    def to_frame(g):
        from shapely.affinity import affine_transform
        return affine_transform(g, [1, 0, 0, -1, ox, oy])
    ink_f, backer_f = to_frame(ink), to_frame(backer)
    band = box(0, 0, FRAME_W, FRAME_H).difference(box(STRIP, STRIP, FRAME_W - STRIP, FRAME_H - STRIP))
    band = band.buffer(-SHANK_IN)   # the shank stays this far inside the strip's edges
    cutout = Point(FRAME_W / 2, FRAME_H / 2).buffer(CUTOUT_D / 2)
    flange = Point(FRAME_W / 2, FRAME_H / 2).buffer(FLANGE_D / 2)
    hair = max(ink_f.geoms, key=lambda p: p.area)
    # A: hidden, screwed from behind the frame strip into bosses on the logo's back
    a_region = backer_f.buffer(-(BOSS_D / 2 + SPOT_CLEAR)).intersection(band)
    # B: black flat heads countersunk in the hair strokes, into the frame strip
    # the shank stays in the black; the head may stand past a stroke narrower than it (drawn true size)
    b_region = hair.buffer(-(SHANK_D / 2 + SPOT_CLEAR)).intersection(band)
    # C: through the cloth to the baffle, anywhere off the flange; same hidden-in-the-hair heads
    c_region = hair.buffer(-(SHANK_D / 2 + SPOT_CLEAR)).difference(flange.buffer(5))
    bx0, by0, bx1, by1 = backer_f.bounds
    face = (1.2 * s, 1.5 * s)   # the badge's 1.2 to 1.5 mm face strokes, scaled
    nozzle = "0.6" if face[0] >= 1.05 else "0.4"   # the 3.5 in tag sliced at 1.07 mm strokes on the 0.6; under that it is the 0.4
    grams = (backer.area * BACKER_T + ink.area * INK_H) / 1000 * 1.27
    return dict(
        w_in=w_in, K=K, s=s, size_mm=(bx1 - bx0, by1 - by0), face=face, grams=grams, nozzle=nozzle,
        hair_mm=5.8 * s * 0.82,
        ink=rings(ink_f), backer=rings(backer_f),
        over_cutout=backer_f.intersection(flange).area / backer_f.area,
        A=farthest_pair(a_region), B=farthest_pair(b_region), C=farthest_pair(c_region),
        a_area=a_region.area, b_area=b_region.area, c_area=c_region.area,
    )


# ------------------------------------------------------------------ drawing
def path(rr):
    d = ""
    for poly in rr:
        for r in poly:
            d += "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in r) + " Z "
    return d


def cab_svg(lay, spots=(), px=0.9, scale_only=False):
    """The cab front, frame coordinates mapped onto the shell (frame origin at shell inset)."""
    fx, fy = (CAB_W - FRAME_W) / 2, (CAB_H - FRAME_H) / 2
    W, H = CAB_W, CAB_H
    g = f'<g transform="translate({fx:.1f},{fy:.1f})">'
    g += f'<rect x="0" y="0" width="{FRAME_W}" height="{FRAME_H}" fill="url(#cloth)"/>'
    g += (f'<path d="M0,0 H{FRAME_W} V{FRAME_H} H0 Z M{STRIP},{STRIP} H{FRAME_W - STRIP} V{FRAME_H - STRIP} H{STRIP} Z" '
          f'fill="var(--band)" fill-rule="evenodd"/>')
    g += (f'<circle cx="{FRAME_W / 2}" cy="{FRAME_H / 2}" r="{CUTOUT_D / 2}" fill="none" stroke="var(--ghost)" '
          f'stroke-width="1.2" stroke-dasharray="6 5"/>')
    g += (f'<circle cx="{FRAME_W / 2}" cy="{FRAME_H / 2}" r="{FLANGE_D / 2}" fill="none" stroke="var(--ghost)" '
          f'stroke-width="0.8" stroke-dasharray="2 4"/>')
    g += f'<path d="{path(lay["backer"])}" fill="#f4f4f2" stroke="#8a8a86" stroke-width="0.6" fill-rule="evenodd"/>'
    g += f'<path d="{path(lay["ink"])}" fill="#1d1d1f" fill-rule="evenodd"/>'
    for kind, (x, y) in spots:
        if kind == "boss":
            g += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{BOSS_D / 2}" fill="none" stroke="var(--accent)" '
                  f'stroke-width="1.4" stroke-dasharray="3 2"/>')
        else:
            g += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{HEAD_D / 2}" fill="#101012" stroke="#5a5a5e" stroke-width="0.6"/>'
            g += (f'<line x1="{x - 2.2:.1f}" y1="{y:.1f}" x2="{x + 2.2:.1f}" y2="{y:.1f}" stroke="#6a6a6e" stroke-width="0.7"/>'
                  f'<line x1="{x:.1f}" y1="{y - 2.2:.1f}" x2="{x:.1f}" y2="{y + 2.2:.1f}" stroke="#6a6a6e" stroke-width="0.7"/>')
    g += "</g>"
    return (f'<svg viewBox="-4 -4 {W + 8} {H + 8}" width="{(W + 8) * px:.0f}" height="{(H + 8) * px:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg" role="img">'
            f'<rect x="0" y="0" width="{W}" height="{H}" rx="12.7" fill="url(#walnut)"/>'
            f'<rect x="{SHELL}" y="{SHELL}" width="{W - 2 * SHELL}" height="{H - 2 * SHELL}" fill="#2a2420"/>'
            f"{g}</svg>")


def closeup_svg(lay, spots, px=3.4, pad=10):
    """The logo region only, same frame coordinates, with the band and the cloth."""
    xs = [x for poly in lay["backer"] for r in poly for x, y in r]
    ys = [y for poly in lay["backer"] for r in poly for x, y in r]
    x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
    x0, y0 = max(x0, -6), max(y0, -6)
    W, H = x1 - x0, y1 - y0
    g = f'<rect x="0" y="0" width="{FRAME_W}" height="{FRAME_H}" fill="url(#cloth)"/>'
    g += (f'<path d="M0,0 H{FRAME_W} V{FRAME_H} H0 Z M{STRIP},{STRIP} H{FRAME_W - STRIP} V{FRAME_H - STRIP} H{STRIP} Z" '
          f'fill="var(--band)" fill-rule="evenodd"/>')
    g += (f'<circle cx="{FRAME_W / 2}" cy="{FRAME_H / 2}" r="{FLANGE_D / 2}" fill="none" stroke="var(--ghost)" '
          f'stroke-width="0.8" stroke-dasharray="2 4"/>')
    g += f'<path d="{path(lay["backer"])}" fill="#f4f4f2" stroke="#8a8a86" stroke-width="0.5" fill-rule="evenodd"/>'
    g += f'<path d="{path(lay["ink"])}" fill="#1d1d1f" fill-rule="evenodd"/>'
    for kind, (x, y) in spots:
        if kind == "boss":
            g += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{BOSS_D / 2}" fill="none" stroke="var(--accent)" '
                  f'stroke-width="1.2" stroke-dasharray="3 2"/>'
                  f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="var(--accent)"/>')
        else:
            g += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{HEAD_D / 2}" fill="#101012" stroke="#5a5a5e" stroke-width="0.5"/>'
            g += (f'<line x1="{x - 2.2:.1f}" y1="{y:.1f}" x2="{x + 2.2:.1f}" y2="{y:.1f}" stroke="#6a6a6e" stroke-width="0.6"/>'
                  f'<line x1="{x:.1f}" y1="{y - 2.2:.1f}" x2="{x:.1f}" y2="{y + 2.2:.1f}" stroke="#6a6a6e" stroke-width="0.6"/>')
    return (f'<svg viewBox="{x0:.1f} {y0:.1f} {W:.1f} {H:.1f}" width="{W * px:.0f}" height="{H * px:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg" role="img">'
            f'<rect x="-8" y="-8" width="{FRAME_W + 16}" height="{FRAME_H + 16}" fill="#2a2420"/>{g}</svg>')


DEFS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<pattern id="cloth" width="3" height="3" patternUnits="userSpaceOnUse">
  <rect width="3" height="3" fill="#8f8c84"/>
  <rect width="1.5" height="1.5" fill="#d9d6cc"/><rect x="1.5" y="1.5" width="1.5" height="1.5" fill="#3b3a37"/>
  <rect x="1.5" width="1.5" height="1.5" fill="#6c6a64"/><rect y="1.5" width="1.5" height="1.5" fill="#b8b4aa"/>
</pattern>
<linearGradient id="walnut" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#5a3b28"/><stop offset="0.5" stop-color="#4a2f1f"/><stop offset="1" stop-color="#3b2416"/>
</linearGradient>
</defs></svg>'''


def spot_list(kind, pts):
    return [(kind, p) for p in pts]


def main():
    lays = [layout(w) for w in WIDTHS_IN]
    size_cards = ""
    for lay in lays:
        w, h = lay["size_mm"]
        size_cards += f'''<figure class="size">
  {cab_svg(lay, px=0.62)}
  <figcaption><b>{lay["w_in"]:g} in wide</b> ({w / 25.4:.2f} x {h / 25.4:.2f} in, {w:.0f} x {h:.0f} mm).
  Face lines {lay["face"][0]:.1f} to {lay["face"][1]:.1f} mm, hair about {lay["hair_mm"]:.1f} mm: the {lay["nozzle"]} nozzle.
  About {lay["grams"]:.0f} g PETG, {lay["grams"] * 2 / 60:.1f} h (estimate; the real slice comes with the build).
  {"Hangs " + f"{lay['over_cutout'] * 100:.0f}" + "% over the speaker flange." if lay["over_cutout"] > 0.01 else "Clear of the speaker flange."}</figcaption>
</figure>'''

    ref = lays[1]   # the 3.5 in one carries the mounting close-ups
    mounts = [
        ("A", "Hidden: screwed from behind the frame", spot_list("boss", ref["A"]),
         "Two M3 machine screws come through the 12 mm frame strip and the cloth from the back into brass heat-set "
         "inserts in 10 mm bosses on the logo's back (dashed). Nothing shows on the front. Only the band over the "
         "frame strip can carry a boss, so the two sit where the logo overlaps it: this far apart on the 3.5 in logo. "
         "The grille lifts off with the logo on it (hook-and-loop)."),
        ("B", "Front screws hidden in the hair", spot_list("head", ref["B"]),
         "Two #4 black flat-head wood screws countersunk flush into the black hair strokes, through the cloth into the "
         "frame strip, drawn true size: the 5.5 mm head is a touch wider than the hair here, so a sliver of head shows "
         "on the white. Same band rule: the spots are where the hair crosses the strip. No tools behind the grille."),
        ("C", "Front screws to the baffle, anywhere", spot_list("head", ref["C"]),
         "Same black heads in the hair, but longer screws through the cloth and the 5 mm gap into the baffle, with a "
         "5 mm standoff on the logo's back at each screw so the plate does not crush the cloth. Any spot off the "
         "speaker flange works, so the screws can spread wide. The cloth dimples 5 mm under each standoff, "
         "hidden under the logo, and the logo stays on when the grille comes off only if the screws are backed out."),
    ]
    mount_cards = ""
    for key, title, spots, text in mounts:
        d = math.dist(spots[0][1], spots[1][1]) if len(spots) == 2 else 0
        mount_cards += f'''<section class="mount">
  <h3><span class="key">{key}</span>{title}</h3>
  {closeup_svg(ref, spots)}
  <p>{text} Screw spread {d:.0f} mm.</p>
</section>'''

    html = f'''<title>Logo Dude cab logo</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* layout: one column of to-scale drawings, the cab front at one scale for every size, close-ups larger */
:root{{--bg:#f3f1ec;--fg:#1f1d1a;--muted:#6a655c;--card:#fbfaf7;--line:#dcd7cc;--accent:#b5541c;--band:rgba(255,225,140,0.42);--ghost:#e8e2d2;
  --display:"Alfa Slab One","Rockwell",Georgia,serif;--body:"Source Sans 3","Segoe UI",system-ui,sans-serif}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#17161a;--fg:#ece9e3;--muted:#a39d92;--card:#201f24;--line:#36343a;--accent:#e08a4a;--band:rgba(255,225,140,0.42);--ghost:#cfc8b6;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#17161a;--fg:#ece9e3;--muted:#a39d92;--card:#201f24;--line:#36343a;--accent:#e08a4a;--band:rgba(255,225,140,0.42);--ghost:#cfc8b6;color-scheme:dark}}
body{{margin:0;padding-block:28px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  background:var(--bg);color:var(--fg);font:16px/1.5 var(--body)}}
main{{max-width:1100px;margin:0 auto}}
h1{{font:400 34px/1.1 var(--display);margin:0 0 6px;text-wrap:balance}}
h2{{font:400 22px/1.2 var(--display);margin:36px 0 10px}}
h3{{font:600 17px/1.3 var(--body);margin:0 0 8px}}
.lead{{color:var(--muted);max-width:68ch;margin:0 0 8px}}
.facts{{display:flex;flex-wrap:wrap;gap:8px 20px;color:var(--muted);font-size:14px;margin:0 0 20px;padding:0;list-style:none}}
.sizes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}}
figure.size{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;min-width:0}}
figure.size svg{{width:100%;height:auto;display:block}}
figcaption{{font-size:14px;color:var(--muted);margin-top:8px}} figcaption b{{color:var(--fg);font-size:16px}}
.mounts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}}
.mount{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;min-width:0}}
.mount svg{{width:100%;height:auto;display:block;border-radius:6px}}
.mount p{{font-size:14px;color:var(--muted);margin:8px 0 0}}
.key{{display:inline-block;font:400 15px/1 var(--display);background:var(--accent);color:#fff;border-radius:6px;padding:5px 8px;margin-right:8px}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:14px;color:var(--muted);margin:10px 0 0}}
.sw{{display:inline-block;width:14px;height:14px;vertical-align:-2px;margin-right:6px;border-radius:3px}}
.pick{{margin-top:32px;padding:14px 16px;border-left:4px solid var(--accent);background:var(--card)}}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Source+Sans+3:wght@400;600&display=swap">
{DEFS}
<main>
<h1>Logo Dude on the cab</h1>
<p class="lead">The badge artwork on the front of the walnut 1x12 (20 x 18 in, Salt and Pepper cloth), drawn to scale from the CAD geometry. The logo sits in the top-left corner, 10 mm in from the grille edge, the way an amp logo does; say if you want it elsewhere.</p>
<ul class="facts">
<li><span class="sw" style="background:rgba(255,235,170,0.6);border:1px solid #c9b86a"></span>the 40 mm grille frame strip behind the cloth (the only wood right behind it)</li>
<li><span class="sw" style="border:1.5px dashed #9a9484"></span>speaker cutout and flange (nothing to screw into, and no gap to reach the baffle)</li>
<li>cloth to baffle gap behind the open part of the frame: 5 mm</li>
</ul>

<h2>Size</h2>
<div class="sizes">{size_cards}</div>

<h2>How it screws on (shown on the 3.5 in logo)</h2>
<div class="mounts">{mount_cards}</div>
<p class="legend"><span><span class="sw" style="background:#101012"></span>#4 black flat head, 5.5 mm, flush</span><span><span class="sw" style="border:1.5px dashed var(--accent)"></span>10 mm boss with an M3 heat-set insert, on the back</span></p>

<section class="pick">
<p><b>My pick:</b> 3.5 in wide with mount A, if you have M3 heat-set inserts (I'll add them to the build if not). It is the classic look, no screw heads, and the grille still comes off as one piece. 3.5 in means the 0.4 nozzle (face lines 1.0 to 1.3 mm, the badge's own recipe); 4 in is the first size the 0.6 that is in the printer handles. B shows a sliver of each head past the hair at this size. C only if you want the logo lower on the grille, off the frame band.</p>
<p>Both A and B leave the chin resting on the cloth with nothing behind it but tension; the plate is stiff, so it should not buzz, and a felt dot under the chin ends it if it does.</p>
</section>
</main>'''
    out = HERE / "cab-logo-options.html"
    out.write_text(html)
    (HERE / "pipeline/build-cab/options.json").parent.mkdir(exist_ok=True)
    (HERE / "pipeline/build-cab/options.json").write_text(json.dumps(
        [{k: v for k, v in lay.items() if k not in ("ink", "backer")} for lay in lays], indent=1, default=float))
    for lay in lays:
        print(f'{lay["w_in"]:.0f} in: {lay["size_mm"][0]:.1f} x {lay["size_mm"][1]:.1f} mm, {lay["grams"]:.0f} g, '
              f'face {lay["face"][0]:.2f}-{lay["face"][1]:.2f}, over flange {lay["over_cutout"]:.2f}, '
              f'A {lay["A"]} B {lay["B"]} C {lay["C"]} areas {lay["a_area"]:.0f}/{lay["b_area"]:.0f}/{lay["c_area"]:.0f}')
    print("wrote", out)


if __name__ == "__main__":
    main()
