#!/usr/bin/env python3
"""Render the concept scene (concept.scad) for each option and viewpoint.

Viewpoints are real eye positions in inches: standing 5 ft and 10 ft from the front
edge at 62 in eye height and an oblique standing view (the hidden checks), a crouched
reach-in view, an underside view from the front right, and two orthographic cuts.
"""
import subprocess, sys, pathlib, concurrent.futures as cf

HERE = pathlib.Path(__file__).resolve().parent
SCAD = HERE / "concept.scad"
OUT = HERE.parent / "images" / "concepts"
OPENSCAD = pathlib.Path.home() / ".local/bin/openscad"
W, D, HT = 45, 24, 27.5
CX = W / 2
CUT_X = 4 + 1.6 + 4 * 3.4          # outlet 5, matches CUT_X in the scad

def mm(v): return [x * 25.4 for x in v]

VIEWS = {
    # name: (eye, center, projection, scad view mode)
    "stand5":   ((CX, -60, 62),          (CX, 0, 19),           "p", "persp"),
    "stand10":  ((CX, -120, 62),         (CX, 0, 20),           "p", "persp"),
    "oblique":  ((CX + 40, -60, 62),     (CX - 10, 4, 18),      "p", "persp"),
    "crouch":   ((CX - 6, -30, 13),      (CX + 2, 16, 22.5),    "p", "persp"),
    "under":    ((CX + 38, -50, 6),      (CX - 1, 12, 21),      "p", "persp"),
    "section":  ((CUT_X + 50, 12, 17.5), (CUT_X, 12, 17.5),     "o", "section"),
    "front":    ((CX, 8 - 80, 17.5),     (CX, 8, 17.5),         "o", "front"),
}

HIDDEN_CHECKS = ("stand5", "stand10", "oblique")   # also rendered in black, as built

# output name -> (scad option, extra -D overrides). Dhigh is D with its top edge on the
# underside instead of under the plug heads (Brian picked D on 2026-09-26).
VARIANTS = {"Dhigh": ("D", [f"D_TOP={HT - 0.75}"])}

def render(option, view, black=False, size="1400,933"):
    eye, ctr, proj, mode = VIEWS[view]
    scad_opt, extra = VARIANTS.get(option, (option, []))
    cam = ",".join(f"{v:.2f}" for v in mm(eye) + mm(ctr))
    out = OUT / f"{option}-{view}{'-black' if black else ''}.png"
    cmd = [str(OPENSCAD), "--backend=Manifold", "--preview", "--projection=" + proj,
           "--colorscheme=Tomorrow", f"--imgsize={size}", f"--camera={cam}",
           "-D", f'option="{scad_opt}"', "-D", f'view="{mode}"', "-D", f"highlight={'false' if black else 'true'}",
           *[a for e in extra for a in ("-D", e)],
           "-o", str(out), str(SCAD)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0 and out.exists()
    return f"{'ok ' if ok else 'FAIL'} {out.name}" + ("" if ok else "\n" + r.stderr[-800:])

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    options = sys.argv[1:] or ["today", "A", "B", "C", "D", "Dhigh"]
    jobs = [(o, v, False) for o in options for v in VIEWS]
    jobs += [(o, v, True) for o in options if o != "today" for v in HIDDEN_CHECKS]
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for line in ex.map(lambda j: render(*j), jobs):
            print(line)
