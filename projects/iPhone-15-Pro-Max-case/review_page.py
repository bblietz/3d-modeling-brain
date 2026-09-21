#!/usr/bin/env python3
"""Write review.html: renders and section close-ups of the case and guard ring, cut from the real meshes, with the slice numbers.

    .venv/bin/python projects/iPhone-15-Pro-Max-case/iphone-15-pro-max-case.py
    .venv/bin/python projects/iPhone-15-Pro-Max-case/pipeline/sections.py
    .venv/bin/python projects/iPhone-15-Pro-Max-case/pipeline/make_print_3mf.py
    python3 projects/iPhone-15-Pro-Max-case/review_page.py

Only our own renders go in the page. Apple's drawings stay in reference/ (their title block says do not reproduce).
"""
import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sl = json.load(open(os.path.join(HERE, "iphone-15-pro-max-case-print-slice.json")))


def img(name):
    data = base64.b64encode(open(os.path.join(HERE, "images", name + ".png"), "rb").read()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{name}">'


def figs(views):
    return "".join(f"<figure>{img(n)}<figcaption>{c}</figcaption></figure>" for n, c in views)


fit = [
    ("section-lip", "The screen lip, with the phone docked. The holding face is the 45&#176; underside: it leans IN over the phone, so it is a hook, not a draft. "
     "It sits 0.05 mm off the phone's shoulder at the one point where Apple's edge profile is also at 45&#176;, about 0.3 mm in from the side. "
     "The tip stops 0.85 mm in from the housing edge; the glass starts at 1.00, so the lip never touches glass. It stands 0.95 mm proud of the screen."),
    ("section-full", "Full cross-section at mid length. Side walls 1.5 mm, back 1.6 mm (8 layers), cavity 0.10 mm larger than the phone per side."),
    ("section-volume-window", "Through the volume-up button. The button stands 0.45 mm proud inside its window. The window is 5.0 mm tall at the inside of the wall and flares at "
     "45&#176; to 6.5 mm outside: finger room, and only the inner 0.75 mm of the window's roof prints as a bridge."),
    ("section-usb", "USB-C window on the centreline, 13.0 x 7.0 mm. Apple's recommended connector keepout (12.45 x 6.60, red) passes through untouched."),
]
guard = [
    ("section-camera", "Cut through the flash, camera 3 and the rear sensor (LiDAR), guard ring glued on. The case has a plain square-edged cutout at the base of the glass ramp "
     "that surrounds the camera island; nothing inside the case is bevelled. The guard ring's rim is 3.0 mm wide with a 1.5 mm 45&#176; bevel on its inside, and hugs the raised island, "
     "1.56 mm off its flat top. A square plug under the rim (1.6 mm wall, 0.6 mm tall) drops into the cutout: it locates the ring for gluing and carries the snug rim over the glass ramp. "
     "The rim's top is 5.0 mm above the back glass; the lens glass is at 4.07, so the lenses sit 0.93 mm off a table (Apple: 0.85 minimum, 1.00 ideal). "
     "Dashed: Apple's flash and LiDAR keepout cones. A snug plain ring crosses both, as most commercial cases do (Brian's call: no cutaways); the bevel keeps the crossing small."),
    ("render-assembly-back", "From the back. Camera top-left seen from the back, side button on the same side, Action and volume opposite: as on the phone."),
    ("render-ring-print", "The guard ring as it prints: rim face on the bed, plug on top. The only overhangs are the rim's two 45&#176; faces; no supports."),
]
magsafe = [
    ("section-magsafe", "MagSafe pocket in the phone side of the back, centred on the phone's centre (Apple's position, within 0.30). Brian's ring is the standard size, 0.4 mm thick. "
     "The pocket locates the ring by its 46 mm inside edge and takes any outside diameter from 54 to 56.5 mm. It is 0.8 mm deep, so the ring sits below the floor's surface, "
     "off the phone's glass, held in by the phone, with 0.8 mm (4 layers) of back between it and a MagSafe accessory (Apple allows at most 0.85)."),
    ("plan-magsafe", "Plan view, looking into the empty case from the screen side. The alignment-piece pocket is at Apple's position, 6.00 x 19.31 toward the bottom edge; "
     "leave it empty if the kit has no alignment piece. The pocket clears the camera guard by 4.5 mm."),
]
whole = [("render-assembly-phone", "Case, ring and the phone proxy built from Apple's drawing (grey in the viewer).")]

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>iPhone 15 Pro Max case: review</title>
<style>
  :root {{ --bg: #f6f5f1; --fg: #1d1f21; --muted: #5d646b; --card: #ffffff; --line: #d9d6cf; --accent: #2f6f4f; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg: #16181a; --fg: #e8e6e1; --muted: #9aa0a6; --card: #1f2225; --line: #33383d; --accent: #6fbf95; }} }}
  body {{ margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.55 system-ui, sans-serif; }}
  main {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px 64px; }}
  h1 {{ font-size: 1.7rem; margin: 0 0 4px; }} h2 {{ font-size: 1.2rem; margin: 36px 0 10px; color: var(--accent); }}
  p.lead {{ color: var(--muted); margin: 0 0 18px; }}
  .facts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }}
  .facts div {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; }}
  .facts b {{ display: block; font-size: 1.25rem; }} .facts span {{ color: var(--muted); font-size: 0.85rem; }}
  figure {{ margin: 0 0 18px; background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 10px; }}
  figure img {{ width: 100%; height: auto; display: block; background: #fff; border-radius: 4px; }}
  figcaption {{ padding: 8px 4px 2px; font-size: 0.92rem; }}
  li {{ margin: 4px 0; }} code {{ font-size: 0.88em; }}
</style></head><body><main>
<h1>iPhone 15 Pro Max case</h1>
<p class="lead">Slim TPU 95A HF case with open button windows and a glue-on camera guard ring. Every phone dimension is from Apple's dimensional drawing. All pictures are cut or rendered from the exported meshes.</p>
<div class="facts">
  <div><b>1.5 mm</b><span>side walls; back 1.6 mm (8 layers)</span></div>
  <div><b>79.9 x 163.1 x 10.8</b><span>case size, mm</span></div>
  <div><b>0.93 mm</b><span>lens glass off a table, ring on</span></div>
  <div><b>0.95 mm</b><span>lip proud of the screen</span></div>
  <div><b>{sl['minutes']} min, {sl['grams']:.0f} g</b><span>real slice, case + ring on one plate, {sl['layers']} layers</span></div>
  <div><b>no supports</b><span>only overhangs: six window roofs</span></div>
</div>
<h2>Fit and hold</h2>{figs(fit)}
<h2>Camera guard</h2>{figs(guard)}
<h2>MagSafe pocket</h2>{figs(magsafe)}
<h2>Whole assembly</h2>{figs(whole)}
<h2>Print</h2>
<ul>
  <li><code>iphone-15-pro-max-case-print.3mf</code>: X2D 0.4 nozzle, 0.20 mm Standard, Bambu TPU 95A HF, Textured PEI, both parts on one plate, back of the case and rim face of the ring on the bed.</li>
  <li>Changed from the stock profile: Arachne walls (the 1.5 mm walls print as solid lines, no gap fill), 4 wall loops (the ring and wall roots print solid, no sparse core), avoid crossing walls (less stringing across the open cavity).</li>
  <li>Feed the TPU from the external spool, not the AMS, and dry it first.</li>
  <li>Known risk on the first print: the volume window's roof is a 22 mm TPU bridge (side button 15 mm, speaker slot 11 mm). Some sag there is cosmetic and inside the wall.</li>
</ul>
<h2>Gluing the ring</h2>
<ul>
  <li>Flexible (rubber-toughened) CA glue, gel if you have it. Take the phone out first.</li>
  <li>The plug under the ring drops into the case's camera cutout from the outside, so the ring locates itself; the cutout is 1.3 mm taller than wide, so it only goes in one way.</li>
  <li>Glue on the underside of the rim's overlap and on the plug's outside wall. Press the rim down flat against the back of the case.</li>
</ul>
</main></body></html>
"""
open(os.path.join(HERE, "review.html"), "w").write(html)
print("wrote review.html", round(len(html) / 1e6, 2), "MB")
