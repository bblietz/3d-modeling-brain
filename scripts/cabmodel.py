"""cabmodel.py: build123d CAD layer for MaximoCabs guitar speaker cabinets.

Places one named solid per blank from a cablayout.Layout, proves the solids
agree with the layout (measured air volume, boolean interference, part
count), and exports STEP, renders, the cut list with the tolex line, and
cab.json. The numbers all live in cablayout.py; nothing here decides a
dimension.

Coordinate frame as in cablayout: X width centered at 0, Y depth with the
external front face at 0 and positive toward the back, Z height from the
floor. Algebra mode throughout; every cutting tool is grown 1 mm past a
blank face it coincides with.

Per-feature renders during a build: scripts/cabmodel.py --render shell
--demo site-box --out /tmp/cab-shell.png (also interior, rear, assembly,
exploded; demos site-box, 2x12-mono-slot, 2x12-stereo-dovetail, open-1x12).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from build123d import (Align, Box, Compound, Cylinder, Plane, Polygon, Pos, Rot,
                       export_step, export_stl, extrude)

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import cablayout as L  # noqa: E402
import cabvoice  # noqa: E402
import cutlist  # noqa: E402

# === TASK 8 ===
TOOL_EXTRA_MM = 1.0                     # cutting tools grow past coincident faces
RENDER_SCRIPT = HERE / "render_stl.py"
RENDER_VIEWS = {"iso": (30, -60), "front": (0, -90), "top": (90, -90), "right": (0, 0)}
MIN_ALIGN = (Align.MIN, Align.MIN, Align.MIN)
SHELL_NAMES = ("side_left", "side_right", "top", "bottom")
INTERIOR_PREFIXES = ("baffle", "cleat_", "grill_", "brace", "divider", "stiffener_", "shelf", "cheek_")
BACK_PREFIX = "back"
PORT_PREFIXES = ("port_tube", "port_ring")


def _box(x0, y0, z0, x1, y1, z1):
    """Axis-aligned box between two corners."""
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN_ALIGN)


def _cyl_y(cx, cz, d, y0, y1):
    """Cylinder of diameter d along +Y from y0 to y1, axis through (cx, cz)."""
    return Pos(cx, y0, cz) * Rot(X=-90) * Cylinder(d / 2.0, y1 - y0,
                                                    align=(Align.CENTER, Align.CENTER, Align.MIN))


def _ccw(poly):
    """Counter-clockwise vertex order, so the extrusion follows the plane normal."""
    area = 0.0
    for i in range(len(poly)):
        y0, z0 = poly[i]
        y1, z1 = poly[(i + 1) % len(poly)]
        area += y0 * z1 - y1 * z0
    return list(poly) if area > 0 else list(reversed(poly))


def _prism_x(polys, x0, x1):
    """Union of prisms along X over [x0, x1] from quadrilaterals in the YZ plane."""
    tool = None
    for poly in polys:
        p = Pos(x0, 0.0, 0.0) * extrude(Plane.YZ * Polygon(*_ccw(poly), align=None), amount=x1 - x0)
        tool = p if tool is None else tool + p
    return tool


def _grown(lo, hi, blank_lo, blank_hi):
    """Extend a tool range 1 mm past every blank face it reaches."""
    eps = 1e-6
    lo2 = lo - TOOL_EXTRA_MM if lo <= blank_lo + eps else lo
    hi2 = hi + TOOL_EXTRA_MM if hi >= blank_hi - eps else hi
    return lo2, hi2


def _grow_polys(polys, blank):
    """Push each quad's outer-face vertices 1 mm past the blank's z faces,
    following the slope of the edge that leads to the shoulder (so a dovetail
    pin keeps its flare), and its end vertices 1 mm past the blank's y faces."""
    (_, y0, z0), (_, y1, z1) = blank.box
    eps = 1e-6
    out = []
    for poly in polys:
        n = len(poly)
        q = []
        for i, (y, z) in enumerate(poly):
            y2, z2 = y, z
            outer = z <= z0 + eps or z >= z1 - eps
            if outer:
                # the neighbor at the shoulder sets the direction to extend along
                for j in (i - 1, i + 1):
                    ny, nz = poly[j % n]
                    if abs(nz - z) > eps:
                        dz = -TOOL_EXTRA_MM if z <= z0 + eps else TOOL_EXTRA_MM
                        y2 = y + (y - ny) / (z - nz) * dz
                        z2 = z + dz
                        break
            if y <= y0 + eps:
                y2 = y2 - TOOL_EXTRA_MM
            elif y >= y1 - eps:
                y2 = y2 + TOOL_EXTRA_MM
            q.append((y2, z2))
        out.append(q)
    return out


def feature_tool(blank, feat):
    """The build123d solid a feature removes from a box blank."""
    (bx0, by0, bz0), (bx1, by1, bz1) = blank.box
    kind = feat["type"]
    if kind == "edge_cuts":
        x0, x1 = _grown(feat["x"][0], feat["x"][1], bx0, bx1)
        return _prism_x(_grow_polys(feat["polys"], blank), x0, x1)
    if kind == "cutout":
        cx, cz = feat["center"]
        return _cyl_y(cx, cz, feat["d"], by0 - TOOL_EXTRA_MM, by1 + TOOL_EXTRA_MM)
    if kind == "holes":
        tool = None
        for (cx, cz) in feat["centers"]:
            h = _cyl_y(cx, cz, feat["d"], by0 - TOOL_EXTRA_MM, by1 + TOOL_EXTRA_MM)
            tool = h if tool is None else tool + h
        return tool
    if kind == "rect_hole":
        w, h = feat["w"], feat["h"]
        if feat["axis"] == "y":
            cx, cz = feat["center"]
            return _box(cx - w / 2, by0 - TOOL_EXTRA_MM, cz - h / 2, cx + w / 2, by1 + TOOL_EXTRA_MM, cz + h / 2)
        cy, cz = feat["center"]
        return _box(bx0 - TOOL_EXTRA_MM, cy - w / 2, cz - h / 2, bx1 + TOOL_EXTRA_MM, cy + w / 2, cz + h / 2)
    if kind == "notch":
        (x0, y0, z0), (x1, y1, z1) = feat["box"]
        x0, x1 = _grown(x0, x1, bx0, bx1)
        y0, y1 = _grown(y0, y1, by0, by1)
        z0, z1 = _grown(z0, z1, bz0, bz1)
        return _box(x0, y0, z0, x1, y1, z1)
    raise ValueError(f"unknown feature type {kind!r} on {blank.name}")


def _largest_solid(shape):
    solids = shape.solids()
    if not solids:
        raise ValueError("boolean left no solid")
    return max(solids, key=lambda s: s.volume)


def blank_solid(blank):
    """One build123d solid for a cablayout.Blank (box, tube, or ring) with
    every feature subtracted; keeps the largest solid after the booleans."""
    if blank.shape == "box":
        (x0, y0, z0), (x1, y1, z1) = blank.box
        solid = _box(x0, y0, z0, x1, y1, z1)
        for feat in blank.features:
            solid = solid - feature_tool(blank, feat)
    else:
        cx, y0, cz = blank.pos
        od, length, id_mm = blank.size
        solid = _cyl_y(cx, cz, od, y0, y0 + length)
        if id_mm > 0:
            solid = solid - _cyl_y(cx, cz, id_mm, y0 - TOOL_EXTRA_MM, y0 + length + TOOL_EXTRA_MM)
    out = _largest_solid(solid)
    out.label = blank.name
    return out


def part_entry(blank, solid):
    """Furniture PARTS registry entry: the cut list reads dims (the rectangular
    blank), the assembly and STEP read the solid."""
    entry = {"name": blank.name, "solid": solid, "dims": tuple(blank.blank_mm),
             "qty": blank.qty, "material": blank.material, "notes": blank.notes}
    if blank.length_axis:
        entry["length_axis"] = blank.length_axis
    return entry


def compound_of(solids):
    return Compound(children=list(solids))


def render(solids, png_path, views=None):
    """Write a temporary STL of the solids and render it with render_stl.py.
    views: list of (elev, azim); None renders the script's four default views."""
    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        stl = Path(tmp) / "render.stl"
        export_stl(compound_of(solids), str(stl))
        cmd = [sys.executable, str(RENDER_SCRIPT), str(stl), str(png_path)]
        if views:
            cmd += [f"{e},{a}" for e, a in views]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    return png_path


def _vault_root() -> Path:
    """First ancestor holding the speaker cab fixtures (the vault root; in the
    Plan 2 mirror the mirror's own .vault copy)."""
    rel = Path("projects/Speaker-cab-system/fixtures/tone-roots.json")
    for base in (HERE / ".vault", HERE, *HERE.parents):
        if (base / rel).exists():
            return base
    raise FileNotFoundError(f"no {rel} above {HERE}")


DEMO_SPEAKER = "eminence-cannabis-rex"
DEMO_AMP_W = 30.0


def _tone() -> dict:
    tone = json.loads((_vault_root() / "projects/Speaker-cab-system/fixtures/tone-roots.json").read_text())
    tone["min_power_w"] = DEMO_AMP_W       # a 30 W amp: the demo speaker passes the power check clean
    return tone


def demo(name: str):
    """A cablayout.Layout for a named demo configuration, voiced live by the
    engine on the Cannabis Rex: site-box (evaluate, 1x12 closed-ported round
    101.5 x 40 mm), 2x12-mono-slot, 2x12-stereo-dovetail, open-1x12."""
    tone = _tone()
    drv = cabvoice.load_speaker(DEMO_SPEAKER)
    z = drv.impedance_ohm[0]
    aest = L.Aesthetics(tolex_color="Fender Style Black", grill_cloth="British Small Weave Cane")
    if name == "site-box":
        port = cabvoice.port_dims(1.0, 1.0, diameter_mm=101.5)
        port.length_mm, port.warnings = 40.0, []
        v = cabvoice.evaluate([drv], [z], "closed-ported", tone, (472.0, 421.2, 229.4), "mono",
                              port, cabvoice.Constraints(line="tolex"), "site-box")
    elif name == "2x12-mono-slot":
        c = cabvoice.Constraints(line="tolex", port_slot_mm=(300.0, 40.0))
        first = cabvoice.propose([drv, drv], [z, z], "closed-ported", tone, "mono", c, name)
        w_int = first.to_dict()["box"]["internal_mm"][0]
        c.port_slot_mm = ((w_int - L.DIVIDER_MM) / 2.0 - 1.0, 40.0)
        v = cabvoice.propose([drv, drv], [z, z], "closed-ported", tone, "mono", c, name)
    elif name == "2x12-stereo-dovetail":
        c = cabvoice.Constraints(line="hardwood", species="black walnut")
        v = cabvoice.propose([drv, drv], [z, z], "closed", tone, "stereo", c, name)
        aest = L.Aesthetics(corner_joint="dovetail", finish="oil")
    elif name == "open-1x12":
        v = cabvoice.propose([drv], [z], "open", tone, "mono", cabvoice.Constraints(line="tolex"), name)
    else:
        raise ValueError(f"unknown demo {name!r}; use site-box, 2x12-mono-slot, 2x12-stereo-dovetail, open-1x12")
    return L.layout(L.order_from(v.to_dict(), aest))


RENDER_KINDS = ("shell", "interior", "rear", "assembly", "exploded")


def render_kind(kind: str, layout, png_path):
    """Per-feature renders for the build loop; later kinds need the later
    task units (interior_solids, back_solids, build, exploded)."""
    g = globals()
    if kind == "shell":
        solids = [blank_solid(b) for b in layout.parts if b.name in SHELL_NAMES]
        return render(solids, png_path, views=[(30, -60), (20, -150)])
    if kind == "interior":
        return render(list(g["interior_solids"](layout).values()), png_path, views=[(25, -60), (15, 120)])
    if kind == "rear":
        solids = list(g["back_solids"](layout).values()) + list(g["port_solids"](layout).values())
        comps = g["component_solids"](layout)
        solids += [v for k, v in comps.items() if k.startswith("speaker_") or k.startswith("jack_plate_")]
        solids += [blank_solid(b) for b in layout.parts if b.name in ("brace", "divider")]
        return render(solids, png_path, views=[(20, 140), (0, 90)])
    if kind == "assembly":
        cab = g["build"](layout)
        return render([e["solid"] for e in cab.parts] + list(cab.components.values()), png_path)
    if kind == "exploded":
        cab = g["build"](layout)
        return render([g["exploded"](cab)], png_path, views=[(30, -60)])
    raise ValueError(f"unknown render kind {kind!r}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Per-feature renders of a demo cabinet")
    ap.add_argument("--render", choices=RENDER_KINDS, required=True)
    ap.add_argument("--demo", default="site-box")
    ap.add_argument("--out", required=True, help="PNG path")
    args = ap.parse_args(argv)
    png = render_kind(args.render, demo(args.demo), args.out)
    print(f"rendered {args.render} of {args.demo} -> {png}")
    return 0
