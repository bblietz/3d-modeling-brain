"""Helm panel for the Garmin GPSMAP 943xsv, cut from black King Starboard.

Replaces the hinged clear cover behind the wheel. The 943xsv flush mounts
through the window; the window and its pilot holes come from garmin_9x3.py,
the same numbers the router template uses.

PROVISIONAL: PANEL_W and PANEL_H are Brian's 2026-09-09 estimate (18.5 x 11.5
in). Exact measurements and photos to follow. Change those two constants and
everything below regenerates.

NOT PRINTABLE: 469.9 mm is 1.8x the X2D bed. This part is routed from sheet.
The exports are for viewing, layout and CAD interop only.

Run:  .venv/bin/python projects/Garmin-943-helm-panel/helm-panel.py
Env:  STAGE=n builds only the first n features (1..5) and exports a scratch
      STL for the per-feature render. SHOW=1|reset pushes to the OCP viewer.
"""
import os
import sys

from build123d import *

from garmin_9x3 import (
    BEZEL_OVER_BOTTOM,
    BEZEL_OVER_SIDE,
    BEZEL_OVER_TOP,
    CUTOUT_H,
    CUTOUT_W,
    HOLE_PITCH_X,
    HOLE_Y,
    PILOT_DRILL,
    UNIT_H,
    UNIT_W,
)

IN = 25.4

# ---- Panel, provisional until Brian measures ----
PANEL_W = 18.5 * IN  # 469.9
PANEL_H = 11.5 * IN  # 292.1
# brief.md rule: 3/8 in stock unless the span exceeds 450 mm, then 1/2 in.
# 469.9 > 450, so 1/2 in.
PANEL_T = 0.5 * IN  # 12.7
CORNER_R = 0.5 * IN  # 12.7, ASSUMPTION: confirm against the old cover
EDGE_ROUND = 0.125 * IN  # 3.175, 1/8 in roundover on the outside face only

# ---- Window ----
CUTOUT_R = 0.25 * IN / 2  # 3.175, the radius a 1/4 in bit leaves; Garmin draws 3.7
CUTOUT_DY = 0.0  # positive moves the window toward the panel top; set at layout
PILOT_DEPTH = 10.0  # blind in 12.7 stock, so nothing pokes through the back

PROJECT = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Garmin-943-helm-panel"
NAME = "helm-panel"

ON_BED = (Align.CENTER, Align.CENTER, Align.MIN)


def build(upto=5):
    # 1. blank
    part = Box(PANEL_W, PANEL_H, PANEL_T, align=ON_BED)
    if upto < 2:
        return part

    # 2. rounded corners
    part = fillet(part.edges().filter_by(Axis.Z), CORNER_R)
    if upto < 3:
        return part

    # 3. window, corners radiused as the router bit leaves them
    window = extrude(RectangleRounded(CUTOUT_W, CUTOUT_H, CUTOUT_R), PANEL_T + 2)
    part -= Pos(0, CUTOUT_DY, -1) * window
    if upto < 4:
        return part

    # 4. four blind pilots, on Garmin's offset pattern
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * HOLE_PITCH_X / 2, HOLE_Y[sy] + CUTOUT_DY
            part -= Pos(x, y, PANEL_T - PILOT_DEPTH) * Cylinder(
                PILOT_DRILL / 2, PILOT_DEPTH + 1, align=ON_BED
            )
    if upto < 5:
        return part

    # 5. roundover on the outside face perimeter only; the window edge stays
    #    sharp and flat so the bezel gasket seats
    outer_top = part.faces().sort_by(Axis.Z)[-1].outer_wire().edges()
    part = fillet(outer_top, EDGE_ROUND)
    return part


def probe_volume(part, solid):
    hit = part & solid
    return hit.volume if hit and hit.volume else 0.0


def check(part):
    size = part.bounding_box().size
    assert abs(size.X - PANEL_W) < 1e-3 and abs(size.Y - PANEL_H) < 1e-3, size
    assert abs(size.Z - PANEL_T) < 1e-3, size
    assert len(part.solids()) == 1, len(part.solids())

    # window is the Garmin cutout, at the chosen vertical offset. Probes are
    # round-cornered like the window itself, or their corners would read as
    # material and the check would fail on correct geometry.
    small = Pos(0, CUTOUT_DY, 1) * extrude(
        RectangleRounded(CUTOUT_W - 0.1, CUTOUT_H - 0.1, CUTOUT_R), PANEL_T - 2
    )
    assert probe_volume(part, small) < 1e-6, "window undersize"
    big = Pos(0, CUTOUT_DY, 1) * extrude(
        RectangleRounded(CUTOUT_W + 0.1, CUTOUT_H + 0.1, CUTOUT_R), PANEL_T - 2
    )
    assert probe_volume(part, big) > 1.0, "window oversize"
    # and the window corners are radiused, not square
    sq = Pos(
        CUTOUT_W / 2 - 0.4, CUTOUT_DY + CUTOUT_H / 2 - 0.4, PANEL_T / 2
    ) * Box(0.5, 0.5, 1, align=(Align.CENTER,) * 3)
    assert probe_volume(part, sq) > 0.2, "window corner not radiused"

    # corners really are radiused: the square corner point is air, inboard is material
    for sx in (-1, 1):
        for sy in (-1, 1):
            tip = Pos(sx * (PANEL_W / 2 - 1), sy * (PANEL_H / 2 - 1), PANEL_T / 2) * Box(
                1, 1, 1, align=(Align.CENTER,) * 3
            )
            assert probe_volume(part, tip) < 1e-6, "corner not rounded"
    inboard = Pos(
        PANEL_W / 2 - CORNER_R - 2, PANEL_H / 2 - CORNER_R - 2, PANEL_T / 2
    ) * Box(1, 1, 1, align=(Align.CENTER,) * 3)
    assert probe_volume(part, inboard) > 0.9, "corner radius too large"

    # pilots: open at the face, blind at the back
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * HOLE_PITCH_X / 2, HOLE_Y[sy] + CUTOUT_DY
            bore = Pos(x, y, PANEL_T - PILOT_DEPTH + 0.05) * Cylinder(
                PILOT_DRILL / 2 - 0.05, PILOT_DEPTH - 0.05, align=ON_BED
            )
            assert probe_volume(part, bore) < 1e-6, "pilot blocked"
            behind = Pos(x, y, 0) * Cylinder(PILOT_DRILL / 2, PANEL_T - PILOT_DEPTH - 0.1, align=ON_BED)
            assert probe_volume(part, behind) > 1e-3, "pilot breaks through the back"

    # the bezel, sitting where the trim caps land, must clear the panel edges
    bezel_l = CUTOUT_W / 2 + BEZEL_OVER_SIDE
    bezel_t = CUTOUT_DY + CUTOUT_H / 2 + BEZEL_OVER_TOP
    bezel_b = CUTOUT_DY - CUTOUT_H / 2 - BEZEL_OVER_BOTTOM
    margins = {
        "side": PANEL_W / 2 - bezel_l,
        "top": PANEL_H / 2 - bezel_t,
        "bottom": PANEL_H / 2 + bezel_b,
    }
    for k, v in margins.items():
        assert v > 20.0, f"only {v:.1f} mm of panel beyond the bezel at {k}"

    # material left between the window and the panel edge, the real strength question
    web = {"side": PANEL_W / 2 - CUTOUT_W / 2, "top": PANEL_H / 2 - CUTOUT_DY - CUTOUT_H / 2,
           "bottom": PANEL_H / 2 + CUTOUT_DY - CUTOUT_H / 2}
    assert min(web.values()) > 25.0, web

    return {
        "panel_mm": (round(PANEL_W, 1), round(PANEL_H, 1), round(PANEL_T, 2)),
        "panel_in": (round(PANEL_W / IN, 3), round(PANEL_H / IN, 3), round(PANEL_T / IN, 3)),
        "volume_cm3": round(part.volume / 1000, 1),
        "mass_hdpe_kg": round(part.volume / 1000 * 0.96 / 1000, 2),
        "bezel_margin_mm": {k: round(v, 1) for k, v in margins.items()},
        "web_mm": {k: round(v, 1) for k, v in web.items()},
    }


def export(part):
    stl = f"{PROJECT}/{NAME}.stl"
    step = f"{PROJECT}/{NAME}.step"
    export_stl(part, stl)
    export_step(part, step)

    import trimesh

    mesh = trimesh.load_mesh(stl)
    assert mesh.is_watertight, "STL not watertight"
    ext = mesh.bounds[1] - mesh.bounds[0]
    assert abs(ext[0] - PANEL_W) < 0.05 and abs(ext[1] - PANEL_H) < 0.05, ext
    return stl, step


if __name__ == "__main__":
    stage = int(os.environ.get("STAGE", "5"))
    part = build(stage)
    if stage < 5:
        out = sys.argv[1] if len(sys.argv) > 1 else f"/tmp/{NAME}-stage{stage}.stl"
        export_stl(part, out)
        print("stage", stage, "->", out, "bbox", part.bounding_box().size)
    else:
        report = check(part)
        stl, step = export(part)
        print("checks passed")
        for k, v in report.items():
            print(f"  {k}: {v}")
        print("exported", stl, step)

    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show

        show(part, names=[NAME], reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
