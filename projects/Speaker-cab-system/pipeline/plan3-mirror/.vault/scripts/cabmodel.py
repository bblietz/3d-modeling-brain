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
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from build123d import (Align, Axis, Box, Compound, Cylinder, Edge, Face, Plane, Polygon, Pos, Rot,
                       Wire, export_step, export_stl, extrude, fillet)

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


def roundover_envelope(layout):
    """The external box (the layout frame's W x D x H) with all 12 edges
    filleted at the spec's resolved Aesthetics.roundover_mm; None when that
    radius is 0 or None, which both mean no roundover. order_from keeps the
    radius under the shell thickness, so the fillets stay in the outer skin
    and never reach a panel's inside face."""
    r = layout.spec.aesthetics.roundover_mm
    if not r:
        return None
    fr = L.frame(layout.spec)
    return fillet(_box(-fr.W / 2.0, 0.0, 0.0, fr.W / 2.0, fr.D, fr.H).edges(), r)


def shell_solid(blank, envelope):
    """blank_solid for a shell panel, intersected with the roundover envelope
    when there is one: only the material within the radius of two outer faces
    goes, through the finger or dovetail combs."""
    solid = blank_solid(blank)
    if envelope is None:
        return solid
    out = _largest_solid(solid & envelope)
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


def strip_part_entries(blank, solid) -> list:
    """One furniture PARTS entry per blank.strips segment, in place of the one
    part_entry a shell panel would otherwise get: solid is the boolean
    intersection of the panel's finished shell_solid (already joint-cut and
    roundover-clipped) with that segment's Y-axis slab, so a stripe crossing
    a finger or dovetail joint shows the true mixed-species teeth rather than
    an approximation. dims keep the panel's own thickness and wraparound
    length (blank_mm's first two entries); only the depth-wise slot narrows
    to the strip's own width, matching how the strip is actually milled and
    glued into the lamination before the panel outline and joinery are cut."""
    (bx0, by0, bz0), (bx1, by1, bz1) = blank.box
    t, cross, _ = blank.blank_mm
    entries = []
    for i, (y0, y1, mat, dens) in enumerate(blank.strips):
        gy0, gy1 = _grown(y0, y1, by0, by1)
        tool = _box(bx0 - TOOL_EXTRA_MM, gy0, bz0 - TOOL_EXTRA_MM,
                   bx1 + TOOL_EXTRA_MM, gy1, bz1 + TOOL_EXTRA_MM)
        piece = _largest_solid(solid & tool)
        name = f"{blank.name}_strip{i}"
        piece.label = name
        material = mat if mat == blank.material else f"{mat} {t:g} mm"
        entry = {"name": name, "solid": piece, "dims": (t, cross, round(y1 - y0, 3)),
                "qty": blank.qty, "material": material, "notes": blank.notes}
        if blank.length_axis:
            entry["length_axis"] = blank.length_axis
        entries.append(entry)
    return entries


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
        # two slots spanning the chamber, split only by the 18 mm center cheek (no end cheek slivers)
        c.port_slot_mm = ((w_int - L.DIVIDER_MM) / 2.0, 40.0)
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
    """Per-feature renders for the build loop. The later kinds call the later
    task units (interior_solids, back_solids, port_solids, component_solids,
    build, exploded); the names resolve when the kind is rendered."""
    if kind == "shell":
        envelope = roundover_envelope(layout)
        solids = [shell_solid(b, envelope) for b in layout.parts if b.name in SHELL_NAMES]
        return render(solids, png_path, views=[(30, -60), (20, -150)])
    if kind == "interior":
        return render(list(interior_solids(layout).values()), png_path, views=[(25, -60), (15, 120)])
    if kind == "rear":
        solids = list(back_solids(layout).values()) + list(port_solids(layout).values())
        comps = component_solids(layout)
        solids += [v for k, v in comps.items() if k.startswith("speaker_") or k.startswith("jack_plate_")]
        solids += [blank_solid(b) for b in layout.parts if b.name in ("brace", "divider")]
        return render(solids, png_path, views=[(20, 140), (0, 90)])
    if kind == "assembly":
        cab = build(layout)
        return render([e["solid"] for e in cab.parts] + list(cab.components.values()), png_path)
    if kind == "exploded":
        cab = build(layout)
        return render([exploded(cab)], png_path, views=[(30, -60)])
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


# === TASK 9 ===
def is_interior(name: str) -> bool:
    return name.startswith(INTERIOR_PREFIXES)


def is_back(name: str) -> bool:
    return name.startswith(BACK_PREFIX)


def is_port(name: str) -> bool:
    return name.startswith(PORT_PREFIXES)


def _solids_for(layout, keep) -> dict:
    out = {}
    for blank in layout.parts:
        if keep(blank.name):
            out[blank.name] = blank_solid(blank)
    return out


def interior_solids(layout) -> dict:
    """Solids for every interior blank (baffle, cleats, grill strips, brace,
    divider, stiffeners, shelf, cheeks), keyed by blank name."""
    return _solids_for(layout, is_interior)


def overlap_volume(a, b) -> float:
    """Boolean intersection volume of two shapes; 0 when they only touch or
    are apart (build123d answers None, or an empty Compound, for no
    intersection). A boolean that fails raises out of here, so a broken
    intersect can never pass an interference check as a clean 0."""
    cut = a & b
    if cut is None:
        return 0.0
    return float(cut.volume)


def _bbox_overlap(a, b, margin=0.5) -> bool:
    ba, bb = a.bounding_box(), b.bounding_box()
    return (ba.min.X < bb.max.X + margin and bb.min.X < ba.max.X + margin
            and ba.min.Y < bb.max.Y + margin and bb.min.Y < ba.max.Y + margin
            and ba.min.Z < bb.max.Z + margin and bb.min.Z < ba.max.Z + margin)


def _label(shape) -> str:
    return getattr(shape, "label", "") or "unlabeled"


def assert_no_overlap(a, b, tol_mm3=1.0) -> float:
    """Intersection volume of a and b; AssertionError above tol_mm3 (raised
    explicitly, so python -O cannot strip it). Touching faces intersect in a
    zero-volume sliver, so 1 mm3 is the working tolerance."""
    if not _bbox_overlap(a, b):
        return 0.0
    v = overlap_volume(a, b)
    if v > tol_mm3:
        raise AssertionError(f"{_label(a)} overlaps {_label(b)} by {v:.1f} mm3")
    return v


# === TASK 10 ===
FOOT_H_MM = 16.0
PLATE_T_MM = 2.0
STRAP_T_MM = 5.0                        # leather strap thickness
STRAP_W_MM = 25.0                       # leather strap width, across the top (y)
STRAP_RISE_MM = 15.0                    # the strap's lower face above the cap tops at mid-span
STRAP_GAP_MM = 0.2                      # strap end to cap face, so the pair never overlaps
STRAP_CAP_MM = (40.0, 32.0, 9.0)        # strap handle end cap: along the strap (x), across (y), tall (z)
STRAP_CAP_ROUND_MM = 3.0                # radius on the caps' top edges
RECESSED_DEPTH_MM = 12.0


def back_solids(layout) -> dict:
    """Closed back or the two open-back panels, keyed by blank name."""
    return _solids_for(layout, is_back)


def port_solids(layout) -> dict:
    """Port tubes and flange rings, keyed by blank name."""
    return _solids_for(layout, is_port)


def envelope_solid(env) -> object:
    """Stepped cylinder behind the baffle (basket, then magnet with its cover
    allowance) plus the flange disc in front of it."""
    solid = _cyl_y(env.center[0], env.center[1], env.basket_d, env.y0, env.y0 + env.basket_len)
    if env.magnet_len > 0:
        y0 = env.y0 + env.basket_len
        solid = solid + _cyl_y(env.center[0], env.center[1], env.magnet_d, y0, y0 + env.magnet_len)
    solid = solid + _cyl_y(env.center[0], env.center[1], env.flange_d, env.y0 - env.flange_t, env.y0)
    return _largest_solid(solid)


def strap_handle_solids(position, spacing_mm) -> dict:
    """The strap handle as three placeholders keyed by label: two end caps
    on the top panel's outer face, each centered on a screw (the handle
    position plus or minus half the screw spacing along x), and the leather
    strap between them. The strap is a 5 mm thick arch (concentric arcs in
    the XZ plane, extruded 25 mm along y) whose ends sit at mid cap height
    STRAP_GAP_MM off each cap's inner face and whose lower face rises
    STRAP_RISE_MM above the cap tops at mid-span."""
    x, y, z = position
    cap_x, cap_y, cap_h = STRAP_CAP_MM
    half = spacing_mm / 2.0
    out = {}
    for i, xc in enumerate((x - half, x + half)):
        cap = _box(xc - cap_x / 2, y - cap_y / 2, z, xc + cap_x / 2, y + cap_y / 2, z + cap_h)
        cap = fillet(cap.edges().group_by(Axis.Z)[-1], STRAP_CAP_ROUND_MM)
        cap.label = f"strap_handle_cap_{i}"
        out[cap.label] = cap
    xa, xb = x - half + cap_x / 2 + STRAP_GAP_MM, x + half - cap_x / 2 - STRAP_GAP_MM
    z_end, z_mid = z + (cap_h - STRAP_T_MM) / 2.0, z + cap_h + STRAP_RISE_MM
    c, s = (xb - xa) / 2.0, z_mid - z_end              # half chord and rise of the lower face
    r = (c * c + s * s) / (2.0 * s)
    z_top = z_mid - r + ((r + STRAP_T_MM) ** 2 - c * c) ** 0.5   # the upper face where it meets each end
    y0 = y - STRAP_W_MM / 2.0
    wire = Wire([Edge.make_three_point_arc((xa, y0, z_end), (x, y0, z_mid), (xb, y0, z_end)),
                 Edge.make_line((xb, y0, z_end), (xb, y0, z_top)),
                 Edge.make_three_point_arc((xb, y0, z_top), (x, y0, z_mid + STRAP_T_MM), (xa, y0, z_top)),
                 Edge.make_line((xa, y0, z_top), (xa, y0, z_end))])
    strap = extrude(Face(wire), amount=STRAP_W_MM, dir=(0, 1, 0))
    strap.label = "strap_handle"
    out[strap.label] = strap
    return out


def component_solids(layout) -> dict:
    """Placeholders for the render and the interference checks, never in the
    cut list: speaker envelopes, jack plates, the handle, the feet."""
    spec = layout.spec
    fr = L.frame(spec)
    out = {}
    for env in layout.envelopes:
        s = envelope_solid(env)
        s.label = f"speaker_{env.speaker}"
        out[s.label] = s
    n_plate = 0
    for hw in layout.hardware:
        if hw.item == "jack plate":
            w, h = hw.cutout
            x, _, z = hw.position
            s = _box(x - w / 2, fr.D - PLATE_T_MM, z - h / 2, x + w / 2, fr.D, z + h / 2)
            s.label = f"jack_plate_{n_plate}"
            out[s.label] = s
            n_plate += 1
        elif hw.item == "strap handle":
            out.update(strap_handle_solids(hw.position, spec.aesthetics.handle_screw_spacing_mm))
        elif hw.item == "recessed handle":
            w, h = hw.cutout
            x, y, z = hw.position
            if x < 0:
                s = _box(x, y - w / 2, z - h / 2, x + RECESSED_DEPTH_MM, y + w / 2, z + h / 2)
                s.label = "recessed_handle_left"
            else:
                s = _box(x - RECESSED_DEPTH_MM, y - w / 2, z - h / 2, x, y + w / 2, z + h / 2)
                s.label = "recessed_handle_right"
            out[s.label] = s
        elif hw.item == "foot":
            x, y, _ = hw.position
            s = Pos(x, y, -FOOT_H_MM) * Cylinder(spec.aesthetics.foot_diameter_mm / 2.0, FOOT_H_MM,
                                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
            s.label = f"foot_{len([k for k in out if k.startswith('foot_')])}"
            out[s.label] = s
    return out


# === TASK 11 ===
AIR_TOL_PCT = 1.0
OVERLAP_TOL_MM3 = 1.0
RECT_RATIO_MIN = 0.98
EXPLODE_FACTOR = 0.6


@dataclass
class CabBuild:
    layout: object
    parts: list                      # furniture PARTS entries, one per blank, in layout order
    components: dict                 # placeholders: speakers, plates, handle, feet
    assembly: object                 # Compound of the part solids
    air: list = field(default_factory=list)   # one shape per chamber (air with the parts removed)

    def solids(self) -> list:
        return [e["solid"] for e in self.parts]


def _port_air_tool(entry: dict):
    if entry["type"] == "box":
        (x0, y0, z0), (x1, y1, z1) = entry["box"]
        return _box(x0, y0, z0, x1, y1, z1)
    cx, cz = entry["center"]
    y0, y1 = entry["y"]
    return _cyl_y(cx, cz, entry["d"], y0, y1)


def build(layout) -> CabBuild:
    """Every blank as one named solid (the shell panels rounded when
    Aesthetics.roundover_mm is set; a shell panel with accent_stripes splits
    into one solid per strip instead), the component placeholders, the
    assembly, and one air shape per chamber (the chamber box minus every
    solid the layout puts inside it minus its port air)."""
    envelope = roundover_envelope(layout)
    parts = []
    owners = []      # (blank, solid) per emitted part, since a striped blank emits several
    for b in layout.parts:
        solid = shell_solid(b, envelope) if b.name in SHELL_NAMES else blank_solid(b)
        entries = strip_part_entries(b, solid) if b.strips else [part_entry(b, solid)]
        parts.extend(entries)
        owners.extend((b, e["solid"]) for e in entries)
    components = component_solids(layout)
    assembly = compound_of(e["solid"] for e in parts)
    air = []
    for ch in layout.chambers:
        (x0, y0, z0), (x1, y1, z1) = ch.box
        shape = _box(x0, y0, z0, x1, y1, z1)
        for blank, solid in owners:
            if blank.chamber == ch.index:
                shape = shape - solid
        for pa in ch.port_air:
            shape = shape - _port_air_tool(pa)
        air.append(shape)
    return CabBuild(layout=layout, parts=parts, components=components, assembly=assembly, air=air)


def check_build(cab: CabBuild, layout) -> list:
    """What only CAD can prove: interference, measured air volume, solid
    count, rectangularity. Same Check shape as cablayout.check_layout."""
    checks = []
    named = [(e["name"], e["solid"]) for e in cab.parts] + list(cab.components.items())
    worst, worst_pair, collisions = 0.0, None, []
    for i, (na, a) in enumerate(named):
        for nb, b in named[i + 1:]:
            if not _bbox_overlap(a, b):
                continue
            v = overlap_volume(a, b)
            if v > worst:
                worst, worst_pair = v, (na, nb)
            if v > OVERLAP_TOL_MM3:
                collisions.append(f"{na} x {nb} {v:.0f} mm3")
    if collisions:
        checks.append(L.Check("interference", "blocker", "; ".join(collisions)))
    else:
        checks.append(L.Check("interference", "pass",
                              f"{len(named)} solids, no pair overlaps by more than {OVERLAP_TOL_MM3:g} mm3"
                              + (f" (worst {worst_pair[0]} x {worst_pair[1]} {worst:.2f} mm3)" if worst_pair else "")))
    msgs, level = [], "pass"
    for ch, shape in zip(layout.chambers, cab.air):
        measured = shape.volume / 1e6 - ch.displacement_l
        delta = (measured - ch.net_l) / ch.net_l * 100.0
        msgs.append(f"chamber {ch.index} measured {measured:.2f} L vs layout {ch.net_l:.2f} L ({delta:+.2f} percent)")
        if abs(delta) > AIR_TOL_PCT:
            level = "blocker"
    checks.append(L.Check("air volume", level, "; ".join(msgs)))
    n_cad, n_lay = len(cab.parts), len(layout.parts)
    n_expected = sum(len(b.strips) or 1 for b in layout.parts)
    msg = f"{n_cad} solids for {n_lay} blanks"
    if n_expected != n_lay:
        msg += f" ({n_expected} solids expected: accent stripes split some shell panels)"
    checks.append(L.Check("solid count", "pass" if n_cad == n_expected else "blocker", msg))
    shaped = []
    for e in cab.parts:
        bb = e["solid"].bounding_box()
        bbox = (bb.max.X - bb.min.X) * (bb.max.Y - bb.min.Y) * (bb.max.Z - bb.min.Z)
        ratio = e["solid"].volume / bbox if bbox > 0 else 1.0
        if ratio < RECT_RATIO_MIN:
            shaped.append(f"{e['name']} {ratio:.0%}")
    checks.append(L.Check("rectangularity", "pass",
                          ("blanks below 98 percent of their bounding box (cut list uses the blank dims): "
                           + ", ".join(shaped)) if shaped else "every part is a plain rectangular blank"))
    return checks


def exploded(cab: CabBuild, factor: float = EXPLODE_FACTOR):
    """Every part and component moved away from the assembly center along
    its own centroid offset, 2 x factor x that offset, so the outer parts
    travel about factor times the external dimension on each axis."""
    bb = cab.assembly.bounding_box()
    cx, cy, cz = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2
    moved = []
    for solid in cab.solids() + list(cab.components.values()):
        sb = solid.bounding_box()
        ox, oy, oz = (sb.min.X + sb.max.X) / 2 - cx, (sb.min.Y + sb.max.Y) / 2 - cy, (sb.min.Z + sb.max.Z) / 2 - cz
        m = Pos(2 * factor * ox, 2 * factor * oy, 2 * factor * oz) * solid
        m.label = getattr(solid, "label", "")
        moved.append(m)
    return compound_of(moved)


def tolex_line(layout) -> dict | None:
    t = layout.tolex
    if t is None:
        return None
    color = layout.spec.aesthetics.tolex_color or "color not chosen"
    return {"part": "tolex wrap", "qty": round(t["length_yd"], 2), "unit": "yd",
            "material": f"tolex {color}, {t['roll_in']} in roll",
            "notes": f"{t['area_m2']:.2f} m2 external area x 1.15; {t['length_m']:.2f} m"}


def export(cab: CabBuild, layout, checks: list, out_dir) -> dict:
    """cab.step, four renders plus the exploded view under images/, the cut
    list with the tolex line, and cab.json. Returns the files dict, every
    path relative to out_dir; cab.json carries the same dict."""
    out_dir = Path(out_dir)
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    files = {"step": "cab.step", "images": [f"images/cab-{view}.png" for view in RENDER_VIEWS] + ["images/cab-exploded.png"],
             "cutlist_md": "cutlist.md", "cutlist_csv": "cutlist.csv", "cab_json": "cab.json"}
    everything = cab.solids() + list(cab.components.values())
    export_step(compound_of(everything), str(out_dir / files["step"]))
    for (elev, azim), png in zip(RENDER_VIEWS.values(), files["images"]):
        render(everything, out_dir / png, views=[(elev, azim)])
    render([exploded(cab)], out_dir / files["images"][-1], views=[(30, -60)])
    extra = [tolex_line(layout)] if layout.tolex else None
    cutlist.write_cut_list(cab.parts, str(out_dir / files["cutlist_md"]), csv_path=str(out_dir / files["cutlist_csv"]),
                           title=layout.spec.name, extra_lines=extra)
    report = L.layout_report(layout, checks)
    report["files"] = files
    (out_dir / files["cab_json"]).write_text(json.dumps(report, indent=2) + "\n")
    return files


if __name__ == "__main__":
    sys.exit(main())
