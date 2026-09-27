"""Build a self-contained share page for the four cable-storage concepts.

Every render is embedded as a data URI so the page works on a phone, away from
the machine that made it. Output: projects/Desk-cable-storage/share.html
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CONCEPTS = os.path.join(PROJ, "images", "concepts")
OUT = os.path.join(PROJ, "share.html")

def uri(path, mime="image/png"):
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())

def render(opt, view):
    return uri(os.path.join(CONCEPTS, "%s-%s.png" % (opt, view)))

# view key -> (tab label, caption)
DESIGN = [
    ("crouch", "Crouched", "Crouched at the front, looking under the slab"),
    ("under", "Underside", "From below, at the front right"),
    ("section", "Section", "Side cut through one outlet: plug, cord, part, wall"),
]
CHECKS = [
    ("stand5-black", "From 5 ft", "Standing 5 ft away, part shown as it would print"),
    ("stand10-black", "From 10 ft", "Standing 10 ft away"),
    ("oblique-black", "Angled", "5 ft away, off to the right, looking into the left corner"),
]
TODAY_VIEWS = [
    ("crouch", "Crouched", "Crouched at the front: five cords and the brick hang from the strip"),
    ("under", "Underside", "From below at the front right"),
    ("section", "Section", "Side cut through an outlet"),
    ("stand5", "From 5 ft", "Standing 5 ft away: the loops and the brick show under the edge"),
    ("stand10", "From 10 ft", "Standing 10 ft away"),
]

OPTIONS = [
    dict(
        key="A", name="Wedge shelf behind the strip",
        verdict="Hidden to 14 ft", tone="good",
        lede="The 10 inches of underside between the strip and the back wall is dead space that "
             "the strip already screens. A shallow trough hangs there, open at the top against the "
             "plywood and open at the back against the wall. The floor slopes toward the wall so "
             "coils and the brick slide back and stay put behind a short lip.",
        specs=[("Size", "16 x 9.5 in, 3 to 5.5 in tall"),
               ("Hidden", "From any standing spot out to about 14 ft"),
               ("Reach", "Crouch at the front, reach 15 in under the plug heads"),
               ("Attach", "Four screws up into the plywood through cast ears"),
               ("Print", "Two 8 in halves keyed together, or one piece at 10 in")],
        note="This was the pick of the session that drew them. It uses space that is already "
             "invisible, needs four screws into wood, and the sloped floor makes it self-tidying.",
    ),
    dict(
        key="B", name="Box in the pocket behind the jamb",
        verdict="Edge shows at an angle", tone="warn",
        lede="The closet is wider than its opening, so there is a 6.5 inch pocket behind each jamb "
             "that the room cannot look into. A tall box hangs from the slab in the left pocket, "
             "open on its inboard side above a lip. Cords tuck into a shallow raceway behind the "
             "strip and drop into the box. You reach it from the doorway, not from under the desk.",
        specs=[("Size", "Box 4.25 x 20 x 7 in, raceway 32 in long"),
               ("Hidden", "Never straight on, but the inboard face shows edge-on beside the jamb"),
               ("Reach", "Kneel at the left of the doorway and reach around the jamb. Easiest of the four"),
               ("Attach", "Box: two screws into the plywood. Raceway: screws or adhesive clips"),
               ("Print", "Box in two 10 in halves plus raceway in 8 in segments. Most parts")],
        note="Best to reach and the most invisible straight on, at the cost of a raceway and a "
             "face that has to be printed black.",
    ),
    dict(
        key="C", name="Rail of coil hooks",
        verdict="Hidden to 14 ft", tone="good",
        lede="No box at all. A flat rail screws to the underside just in front of the back wall "
             "with one hook per outlet. Each cord's slack is coiled onto its own hook, so any one "
             "cord comes off without disturbing the rest. The brick does not fit this scheme and "
             "goes on the desk with its lead fed down through a grommet, which was your suggestion.",
        specs=[("Size", "Rail 28 x 1.2 in, nine hooks, coils about 3 in across"),
               ("Hidden", "From any standing spot to about 14 ft"),
               ("Reach", "Crouch at the front, reach 20 in, lift a coil off"),
               ("Attach", "Rail screws, one per segment"),
               ("Print", "Rail in three or four segments plus hooks. Every part small")],
        note="Tidiest per cord, and the only one where pulling one cord does not disturb the "
             "others. It needs a 2 in hole drilled in the desktop for the brick lead.",
    ),
    dict(
        key="D", name="Trough on the back wall", pick=True,
        verdict="Visible from 10 ft", tone="bad",
        lede="The obvious version: a trough screwed to the drywall under the plug heads so the "
             "cords fall into it. It is the easiest to load, but it has to sit below the plugs, "
             "and that puts its front face under the slab's sightline as soon as you step back.",
        specs=[("Size", "16 x 6 x 4.5 in, top edge 4 in below the underside"),
               ("Hidden", "Only to about 6 ft. From 10 ft the whole front face shows"),
               ("Reach", "Crouch, reach 18 in, under the plugs"),
               ("Attach", "Four drywall anchors"),
               ("Print", "Two halves plus a wall plate")],
        note="Your pick. At the assumed dimensions its front face clears the slab's sightline "
             "only inside about 6 ft; step back further and it shows. The version below is the "
             "same part moved up 4 in, which fixes that.",
    ),
    dict(
        key="Dhigh", badge="D+", name="Same trough, raised to the underside",
        verdict="Hidden to 12 ft", tone="good",
        lede="Identical trough, identical wall mount, but its top edge sits against the plywood "
             "instead of 4 inches below it. The plugs are 10 inches in front of the back wall, so "
             "nothing needs the trough to be below them. Cords leave their plugs and run back, "
             "nearly level, into the open front.",
        specs=[("Size", "16 x 6 x 4.5 in, top edge on the underside"),
               ("Hidden", "To about 12 ft. Its bottom edge is 4.5 in below the slab, 6 in off the wall"),
               ("Reach", "Crouch, reach 18 in, over the plug heads and into the front"),
               ("Attach", "Four drywall anchors, same as D"),
               ("Print", "Two halves plus a wall plate, same as D")],
        note="Loading changes slightly: a coil gets tucked in rather than dropped in. Raised this "
             "far, it is close to A's geometry attached to the wall instead of the slab.",
    ),
]
PICKED = [o for o in OPTIONS if o["key"] in ("D", "Dhigh")]
OTHERS = [o for o in OPTIONS if o["key"] not in ("D", "Dhigh")]

ASSUMPTIONS = [
    ("Closet width behind the opening", "45 in", "32 in opening, centred, so 6.5 in pockets each side"),
    ("Depth, front edge to back wall", "24 in", "Photo scaled off the printer's known width"),
    ("Underside height off the floor", "26.75 in", "Weakly constrained, the least certain number"),
    ("Slab thickness", "0.75 in", "You said 3/4 in; the photo reads closer to 5/8"),
    ("Power strip", "34 in, 9 outlets", "Front face 12 in behind the edge, outlets facing down"),
    ("Strip setback behind the edge", "12 in", "Inferred from perspective, not observed"),
    ("Load", "9 cords plus one brick", "Brick is 6 x 2.4 x 1.2 in"),
]

def tabs_html(opt_key, views, prefix):
    btns, panes = [], []
    for i, (v, label, cap) in enumerate(views):
        sel = " aria-selected=\"true\"" if i == 0 else ""
        btns.append(
            '<button class="tab" role="tab" id="%s-t%d" aria-controls="%s-p%d"%s '
            'data-target="%s-p%d">%s</button>' % (prefix, i, prefix, i, sel, prefix, i, label))
        panes.append(
            '<figure class="pane" id="%s-p%d" role="tabpanel" aria-labelledby="%s-t%d"%s>'
            '<img src="%s" alt="%s" loading="lazy" decoding="async">'
            '<figcaption>%s</figcaption></figure>'
            % (prefix, i, prefix, i, "" if i == 0 else " hidden", render(opt_key, v), cap, cap))
    return ('<div class="tabs" role="tablist">%s</div><div class="panes">%s</div>'
            % ("".join(btns), "".join(panes)))

def option_html(o):
    specs = "".join('<div class="k">%s</div><div class="v">%s</div>' % (k, v) for k, v in o["specs"])
    return """
<section class="card opt" id="opt-%(key)s">
  <header class="opt-head">
    <span class="badge">%(badge)s</span>
    <div>
      <h2>%(name)s</h2>
      %(pickchip)s<span class="chip %(tone)s">%(verdict)s</span>
    </div>
  </header>
  <p class="lede">%(lede)s</p>
  %(design)s
  <dl class="specs">%(specs)s</dl>
  <p class="note">%(note)s</p>
</section>""" % dict(
        key=o["key"], badge=o.get("badge", o["key"]), name=o["name"], tone=o["tone"],
        verdict=o["verdict"],
        pickchip='<span class="chip pick">Your pick</span> ' if o.get("pick") else "",
        lede=o["lede"], specs=specs, note=o["note"],
        design=tabs_html(o["key"], DESIGN + CHECKS, "o" + o["key"]))

rows = "".join(
    '<tr><td>%s</td><td class="num">%s</td><td class="src">%s</td></tr>' % r for r in ASSUMPTIONS)

HTML = """<title>Desk Cable Storage</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --bg:#EFF1F3; --surface:#FFFFFF; --sunk:#F5F6F8;
  --ink:#14171A; --muted:#5B6169; --line:#DCE0E4;
  --accent:#D96A12; --accent-soft:#FBEEE2;
  --good:#1F6B47; --good-bg:#E4F0EA;
  --warn:#8A5A12; --warn-bg:#F7EEDC;
  --bad:#9E3517; --bad-bg:#F8E7E1;
  --radius:14px;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --bg:#121417; --surface:#1B1E22; --sunk:#232730;
    --ink:#ECEEF1; --muted:#98A0A9; --line:#2C3139;
    --accent:#F08A33; --accent-soft:#33231480;
    --good:#7FD3A8; --good-bg:#16311F;
    --warn:#E8BB6B; --warn-bg:#332713;
    --bad:#F0A08A; --bad-bg:#3A1E16;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#121417; --surface:#1B1E22; --sunk:#232730;
  --ink:#ECEEF1; --muted:#98A0A9; --line:#2C3139;
  --accent:#F08A33; --accent-soft:#33231480;
  --good:#7FD3A8; --good-bg:#16311F;
  --warn:#E8BB6B; --warn-bg:#332713;
  --bad:#F0A08A; --bad-bg:#3A1E16;
}
*{box-sizing:border-box}
body{background:var(--bg); color:var(--ink);
  font-family:Archivo,"Helvetica Neue",Arial,sans-serif; line-height:1.55;
  -webkit-text-size-adjust:100%%;}
.wrap{max-width:780px; margin:0 auto; padding-inline:16px; padding-block:28px 64px;
  display:flex; flex-direction:column; gap:22px;}
h1{font-size:clamp(26px,7vw,40px); line-height:1.08; margin:0; font-weight:700;
  letter-spacing:-0.02em; text-wrap:balance;}
h2{font-size:19px; margin:0 0 6px; font-weight:600; letter-spacing:-0.01em; text-wrap:balance;}
h3{font-size:13px; margin:0 0 10px; font-weight:600; text-transform:uppercase;
  letter-spacing:.09em; color:var(--muted);}
p{margin:0 0 10px}
p:last-child{margin-bottom:0}
.eyebrow{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12px;
  letter-spacing:.14em; text-transform:uppercase; color:var(--accent); margin:0 0 10px;}
.sub{color:var(--muted); font-size:15.5px; max-width:60ch;}
.card{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  padding:18px;}
.flag{border-left:3px solid var(--accent); background:var(--accent-soft);
  border-radius:0 var(--radius) var(--radius) 0; padding:14px 16px;}
.flag p{font-size:14.5px}
.flag strong{color:var(--accent)}
.opt-head{display:flex; gap:13px; align-items:flex-start; margin-bottom:10px;}
.badge{flex:none; width:38px; height:38px; border-radius:10px; background:var(--accent);
  color:#fff; font-weight:700; font-size:19px; display:grid; place-items:center;}
.chip{display:inline-block; font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11.5px;
  padding:3px 9px; border-radius:999px; letter-spacing:.03em;}
.chip.good{background:var(--good-bg); color:var(--good)}
.chip.warn{background:var(--warn-bg); color:var(--warn)}
.chip.bad{background:var(--bad-bg); color:var(--bad)}
.chip.pick{background:var(--accent); color:#fff}
.lede{font-size:15px; color:var(--ink); margin-bottom:14px;}
.tabs{display:flex; gap:6px; overflow-x:auto; padding-bottom:8px; margin-bottom:2px;
  scrollbar-width:thin;}
.tab{flex:none; font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12px;
  padding:6px 11px; border-radius:999px; border:1px solid var(--line);
  background:var(--sunk); color:var(--muted); cursor:pointer;}
.tab[aria-selected="true"]{background:var(--ink); color:var(--surface); border-color:var(--ink);}
.tab:focus-visible,.lb-close:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.pane{margin:0}
.pane img{width:100%%; max-width:100%%; display:block; border-radius:9px; background:var(--sunk);
  border:1px solid var(--line); cursor:zoom-in;}
figcaption{font-size:12.5px; color:var(--muted); margin-top:7px;}
.specs{display:grid; grid-template-columns:auto 1fr; gap:6px 14px; margin:15px 0 0;
  font-size:14px; align-items:baseline;}
.specs .k{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11.5px;
  text-transform:uppercase; letter-spacing:.07em; color:var(--muted); white-space:nowrap;}
.specs .v{margin:0}
.note{margin-top:14px; padding-top:13px; border-top:1px solid var(--line);
  font-size:14px; color:var(--muted);}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse; width:100%%; font-size:13.5px; min-width:420px}
th,td{text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top}
th{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11px; text-transform:uppercase;
  letter-spacing:.07em; color:var(--muted); font-weight:500;}
td.num{font-family:"IBM Plex Mono",ui-monospace,monospace; font-variant-numeric:tabular-nums;
  white-space:nowrap;}
td.src{color:var(--muted)}
ul{margin:0; padding-left:19px} li{margin-bottom:7px; font-size:14.5px}
li:last-child{margin-bottom:0}
.lb{position:fixed; inset:0; background:#0B0D0FF2; display:grid; place-items:center;
  padding:16px; z-index:50;}
.lb img{max-width:100%%; max-height:88vh; border-radius:8px}
.lb-close{position:absolute; top:calc(12px + env(safe-area-inset-top,0px)); right:14px;
  background:#FFFFFF1F; color:#fff; border:0; border-radius:999px; width:40px; height:40px;
  font-size:21px; cursor:pointer;}
@media (prefers-reduced-motion:no-preference){.pane{animation:fade .18s ease}}
@keyframes fade{from{opacity:.4}to{opacity:1}}
</style>

<div class="wrap">
  <header>
    <p class="eyebrow">Closet desk / printer bench</p>
    <h1>Four ways to hide the cords</h1>
    <p class="sub">You picked the trough on the back wall. It is shown first in two versions,
    as first drawn and raised to the underside, because the 10 ft view is the whole difference
    between them. The other three stay below for reference. Orange is the new part. Black is the
    same part as it would actually print, used to check what shows from the room. Tap any picture
    to enlarge it.</p>
  </header>

  <div class="flag">
    <p><strong>Nothing here has been measured yet.</strong> Every dimension was read off your two
    photos and is good to about plus or minus 10 percent. Option A in particular only exists
    because the strip appears to sit about 12 inches back from the front edge, and that setback was
    inferred from perspective rather than seen. Six tape measurements would settle all of it.</p>
  </div>

  <section class="card">
    <h3>What it looks like today</h3>
    <p class="lede">Five cords and a power brick hang in mid air under the slab, held up by nothing
    but their own plugs.</p>
    %(today)s
  </section>

  %(picked)s

  <h3 style="margin:6px 0 -8px">The other three, for reference</h3>
  %(others)s

  <section class="card">
    <h3>What the model assumed</h3>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Dimension</th><th>Assumed</th><th>Where it came from</th></tr></thead>
        <tbody>%(rows)s</tbody>
      </table>
    </div>
  </section>

  <section class="card">
    <h3>Already decided</h3>
    <ul>
      <li>A trough on the back wall, option D. Picked 2026-09-26.</li>
      <li>The power strip stays where it is, screwed to the underside.</li>
      <li>It holds cord slack and the power brick. Not the floor bundle, not spools or tools.</li>
      <li>Open front, reach in. No lid, no drawer, no hinge, no latch.</li>
      <li>Sized for about ten cords, not the full 34 inch length of the strip.</li>
      <li>If the brick will not fit, it goes on the desk with its lead fed down through the plywood.</li>
    </ul>
  </section>

  <section class="card">
    <h3>What I need from you</h3>
    <ul>
      <li>D as first drawn, or D raised to the underside? Flip both to the 10 ft tab.</li>
      <li>Are all nine cords worth storing slack for, or are the PC and shredder permanent and
      never moved? Fewer cords means a shorter trough.</li>
      <li>The six measurements: closet width, front edge to back wall, underside height, slab
      thickness, how far the strip sits behind the front edge, and the clear depth behind it.</li>
    </ul>
  </section>
</div>

<script>
document.querySelectorAll(".tabs").forEach(function(strip){
  strip.addEventListener("click", function(e){
    var btn = e.target.closest(".tab");
    if(!btn) return;
    strip.querySelectorAll(".tab").forEach(function(b){ b.setAttribute("aria-selected","false"); });
    btn.setAttribute("aria-selected","true");
    var panes = strip.parentNode.querySelector(".panes");
    panes.querySelectorAll(".pane").forEach(function(p){ p.hidden = true; });
    var t = document.getElementById(btn.dataset.target);
    if(t) t.hidden = false;
  });
});
document.addEventListener("click", function(e){
  var img = e.target.closest(".pane img");
  if(!img) return;
  var lb = document.createElement("div");
  lb.className = "lb";
  lb.innerHTML = '<button class="lb-close" aria-label="Close">&#215;</button>';
  var big = document.createElement("img");
  big.src = img.src; big.alt = img.alt;
  lb.appendChild(big);
  lb.addEventListener("click", function(){ lb.remove(); });
  document.body.appendChild(lb);
});
document.addEventListener("keydown", function(e){
  if(e.key === "Escape"){ var lb = document.querySelector(".lb"); if(lb) lb.remove(); }
});
</script>
""" % dict(
    today=tabs_html("today", TODAY_VIEWS, "today"),
    picked="".join(option_html(o) for o in PICKED),
    others="".join(option_html(o) for o in OTHERS),
    rows=rows,
)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote %s  (%.2f MB)" % (OUT, os.path.getsize(OUT) / 1e6))
