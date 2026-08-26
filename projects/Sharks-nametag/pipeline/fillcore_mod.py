"""Shared fill-core letter-tier tooling (Sharks nametag, 0.4 nozzle C7 recipe).

Brian's verdict on the thin 0.4 coupon plate (2026-08-25): C7 is the best.
The recipe, baked into batch_roster.py and plates.py from here:
  MODIFIER PART per tag object over the raised white banner letters
  (S-A-N-T-A C-R-U-Z; not CITY, not the YSC micro-text, not the bars):
  letter outlines from the white STL cross-section in the letter tier,
  buffered MOD_BUFFER, extruded over the letter-only layers, carrying the
  region keys C7_MOD_KEYS (written BEFORE <mesh_stat/>), plus the OBJECT
  key C7_OBJECT_KEYS injected through the CLI assemble list print_params.
fillcore_coupons.py (the coupon builder Brian judged) uses the same
functions with the five-letter SANTA_BOX.

Coordinates: "tag mm" = the canonical STLs (origin-centered disc, z 0 at
the bottom). The CLI stores every part mesh centered on its bbox and puts
the center in the component transform, so an object's plate position is
(first component transform) - (white mesh bbox center); a modifier mesh
centered the same way goes in at position + its own center.
"""
import json
import os
import re
import subprocess

import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Sharks-nametag"
PIPE = os.path.dirname(os.path.abspath(__file__))
COLORS = ["#FFFFFF", "#00395E", "#31BAD6"]
BED_TYPE = "Textured PEI Plate"
# process keys the flattened presets override (flatten_04.py SMOOTH_TOP);
# they must be listed in different_settings_to_system[0] or Studio resets
# them to the system preset on load
SMOOTH_KEYS = ["ironing_type", "top_one_wall_type",   # coupon C recipe (2026-08-22)
               "top_surface_line_width", "top_shell_layers", "top_surface_speed",
               "sparse_infill_density", "sparse_infill_pattern", "wall_generator",
               "seam_gap", "small_perimeter_speed", "small_perimeter_threshold",
               "gap_infill_speed", "wall_distribution_count", "wall_transition_filter_deviation",
               "min_feature_size", "min_bead_width",
               "skirt_loops", "skirt_distance", "skirt_height", "initial_layer_speed",
               "initial_layer_infill_speed",
               "prime_tower_brim_width", "prime_tower_rib_wall", "prime_tower_fillet_wall"]
SANTA_BOX = (-26.0, -12.5, 1.0, -4.5)     # tag mm: the five SANTA glyphs (coupons; C of CRUZ starts at x 4.6)
BANNER_BOX = (-26.0, -12.5, 26.0, -4.5)   # tag mm: all nine SANTA CRUZ glyphs (CITY sits below y -12.7)
MOD_BUFFER = 0.3   # modifier = letter outlines grown by this
MOD_BELOW = 0.04   # modifier bottom under the banner top: between the last navy-layer center and the first letter-only center
MOD_ABOVE = 0.08   # modifier top over the letter top
C7_MOD_KEYS = {"wall_loops": "1", "top_one_wall_type": "all top", "top_surface_line_width": "0.3",
               "internal_solid_infill_line_width": "0.3", "infill_direction": "90"}
C7_OBJECT_KEYS = {"detect_narrow_internal_solid_infill": "0"}
# Back-text modifier (2026-08-25, gate print: the OBJECT key C7_OBJECT_KEYS turns
# every internal-solid island narrower than 6 mm rectilinear, Fill.cpp
# NARROW_INFILL_AREA_THRESHOLD 3 mm, and the check reads the OBJECT config, so
# the navy inlay strokes on the back (name, number, season line; 1.2-5.9 mm
# wide) lose their concentric fill in layers 2-4. A second modifier part over
# the back text restores it with the REGION key internal_solid_infill_pattern
# (an enum in Studio 2.08; the gate carries "zig-zag"). Band z 0.16..0.56 touches
# only the slice centers 0.26/0.38/0.50 (layer 1 = the visible face and layer
# 5 = white stay byte-identical); buffer 0.5 mm lies inside the white's two
# walls (>= 0.87 mm), so no white fill is touched. Measured MAX 18 gate:
# MAX layers 2-4 uncovered 2.03 -> 0.91 mm2, "18" 3.04 -> 2.53, front tier unchanged.
BACK_MOD_KEYS = {"internal_solid_infill_pattern": "concentric"}
BACK_MOD_NAME = "MOD back text: internal_solid_infill_pattern concentric"
BACK_BUFFER = 0.5
BACK_SECTION_Z = 0.3   # inside the 0.6 mm inlay
BACK_INLAY = 0.6
BACK_Z0, BACK_Z1 = 0.16, 0.56
LAYERS_04 = dict(first=0.2, layer=0.12)   # 0.12mm High Quality @BBL X2D (0.4 nozzle)
# Wipe tower footprint on the 0.4 presets (3 colors, prime_tower_width 60,
# rib + fillet wall, 5 mm brim), measured on the MAX 18 graft slice
# 2026-08-25 with wipe_tower_x/y (30, 180): the layer-1 brim spans
# x 26.26..77.79, y 174.97..227.55 (51.5 x 52.6 mm, extrusion centerlines),
# i.e. these offsets from wipe_tower_x/y; the rib wall tapers from
# 47.5 mm (layer 2) to the 43.3 x 42.8 core whose lower-left corner is
# wipe_tower_x/y. Placement rule (Brian 2026-08-25): tags keep their slots,
# the tower goes to the free spot closest to the bed center, never within
# TOWER_EDGE_MIN of a bed edge, at least TOWER_DISC_MIN (brim edge to disc
# edge) from every tag.
BRIM_OFFSETS = (-3.74, -5.03, 47.79, 47.55)   # brim x0, y0, x1, y1 relative to wipe_tower_x/y
BED = 256.0
DISC_R = 76.2 / 2
TOWER_DISC_MIN = 12.0
TOWER_EDGE_MIN = 15.0
FLUSH_3X3 = ["0", "280", "280", "280", "0", "280", "280", "280", "0"]


# ----------------------------------------------------------------- geometry
def section_polys(mesh, z):
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return []
    p2, _ = sec.to_2D(to_2D=np.eye(4))
    return [Polygon(np.asarray(p.exterior.coords)[:, :2], [np.asarray(i.coords)[:, :2] for i in p.interiors])
            for p in p2.polygons_full]


def letter_geometry(letter_box=SANTA_BOX, n_letters=5, margin=1.5, window_checks=True):
    """Tag-mm geometry of the banner letter tier from the canonical STLs.

    Returns dict: letters (n_letters shapely polygons, left to right), frame
    (the 0.6 mm banner bars polygon), window (x0, y0, x1, y1) = letter bbox
    + margin, wbox, center, disc_top, banner_top, letter_top, and for the
    coupons 'excluded' (other white polygons intersecting the window, with
    areas) and 'navy_mid'. window_checks asserts nothing white or navy
    changes shape inside the window above the disc (coupon crop = extruded
    cross-sections); the nine-letter window catches the raised navy ball
    geometry at its top edge, so the batch passes window_checks=False."""
    white = trimesh.load(f"{PROJ}/sharks-nametag-white.stl")
    navy = trimesh.load(f"{PROJ}/sharks-nametag-navy.stl")
    zs = sorted(set(np.round(white.vertices[:, 2], 3)))
    letter_top = max(zs)
    disc_top = max(z for z in zs if z < letter_top - 0.5)
    sb = box(*letter_box)
    nv = navy.vertices
    sel = (nv[:, 0] > letter_box[0]) & (nv[:, 0] < letter_box[2]) & (nv[:, 1] > letter_box[1]) & (nv[:, 1] < letter_box[3])
    banner_top = float(np.round(nv[sel, 2].max(), 3))
    assert disc_top < banner_top < letter_top, (disc_top, banner_top, letter_top)
    z_mid = (banner_top + letter_top) / 2
    w_mid = section_polys(white, z_mid)
    letters = sorted([p for p in w_mid if sb.contains(p) and (p.bounds[2] - p.bounds[0]) < 10],
                     key=lambda p: p.bounds[0])
    assert len(letters) == n_letters, [p.bounds for p in letters]
    frame = [p for p in w_mid if (p.bounds[2] - p.bounds[0]) > 40]   # the banner bars, 53.75 mm wide
    assert len(frame) == 1, len(frame)
    frame = frame[0]
    # the letters are full-height prisms: same outlines just above the disc
    low = {round(p.area, 4) for p in section_polys(white, disc_top + 0.1) if sb.contains(p) and (p.bounds[2] - p.bounds[0]) < 10}
    assert low == {round(p.area, 4) for p in letters}, "letters are not simple prisms"
    lb = unary_union(letters).bounds
    window = (lb[0] - margin, lb[1] - margin, lb[2] + margin, lb[3] + margin)
    wbox = box(*window)
    if window_checks:
        for m, name, lo, hi in ((white, "white", disc_top, letter_top), (navy, "navy", disc_top, banner_top)):
            v = m.vertices
            s = ((v[:, 0] > window[0] - 1e-6) & (v[:, 0] < window[2] + 1e-6) & (v[:, 1] > window[1] - 1e-6)
                 & (v[:, 1] < window[3] + 1e-6) & (v[:, 2] > lo - 1e-3))
            lv = set(np.round(v[s, 2], 3))
            assert lv == {round(lo, 3), round(hi, 3)}, (name, lv)
    excluded = [(p.intersection(wbox).area, p.bounds) for p in w_mid
                if p.intersects(wbox) and p is not frame and not any(p.equals(l) for l in letters)]
    navy_mid = [p for p in section_polys(navy, (disc_top + banner_top) / 2) if p.intersects(wbox)]
    return dict(letters=letters, frame=frame, window=window, wbox=wbox,
                center=((window[0] + window[2]) / 2, (window[1] + window[3]) / 2),
                disc_top=disc_top, banner_top=banner_top, letter_top=letter_top,
                excluded=excluded, navy_mid=navy_mid)


def geoms(g):
    if g.is_empty:
        return []
    return [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.area > 1e-6]


def extrude(g, z0, z1, dx=0.0, dy=0.0):
    parts = [trimesh.creation.extrude_polygon(p, z1 - z0) for p in geoms(g)]
    m = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
    m.apply_translation([dx, dy, z0])
    return m


def modifier_2d(letters, buffer=MOD_BUFFER):
    return unary_union([l.buffer(buffer) for l in letters])


def centered(mesh):
    """Copy of mesh translated to its bbox center (how the CLI stores parts) and that center."""
    m = mesh.copy()
    b = m.bounds
    mc = (b[0] + b[1]) / 2
    m.apply_translation(-mc)
    return m, mc


def layer_centers(first, layer, height):
    """Slice centers of the layer grid up to an object of this height."""
    centers = [first / 2]
    while True:
        c = first + layer * (len(centers) - 0.5)
        if c >= height:
            return centers
        centers.append(round(c, 6))


def modifier_z_band(banner_top, letter_top, first, layer, below=MOD_BELOW, above=MOD_ABOVE):
    """(z0, z1, n_layers, tier) for the letter-tier modifier: asserts the band
    covers exactly the letter-only layers (slice centers above the banner
    top, like the judged coupon) with >= 0.03 mm clearance from every center."""
    z0, z1 = banner_top - below, letter_top + above
    centers = layer_centers(first, layer, letter_top)
    tier = [c for c in centers if c > banner_top]
    touched = [c for c in centers if z0 < c < z1]
    assert touched == tier, (touched, tier)
    for c in centers:
        assert min(abs(c - z0), abs(c - z1)) > 0.03, (c, z0, z1)
    return z0, z1, len(centers), tier


def back_geometry(navy_mesh):
    """Tag-mm outlines of the back inlay: every navy polygon in the
    BACK_SECTION_Z section (MAX 18 gate: 14 polygons). Asserts nothing navy
    sits just above the inlay and the footprint stays well inside the disc."""
    polys = section_polys(navy_mesh, BACK_SECTION_Z)
    assert 8 <= len(polys) <= 40, len(polys)
    assert not section_polys(navy_mesh, BACK_INLAY + 0.1), "navy above the back inlay"
    b = unary_union(polys).bounds
    assert max(abs(v) for v in b) < DISC_R - 5, b
    return polys


def check_back_band(first, layer, z0=BACK_Z0, z1=BACK_Z1, inlay=BACK_INLAY):
    """The back band must touch exactly the inlay slice centers above the
    visible layer 1, with >= 0.03 mm clearance from every center."""
    centers = layer_centers(first, layer, inlay + 2 * layer)
    touched = [c for c in centers if z0 < c < z1]
    assert touched == [c for c in centers if c < inlay][1:], (touched, centers)
    for c in centers:
        assert min(abs(c - z0), abs(c - z1)) > 0.03, (c, z0, z1)
    return touched


def tower_brim(tower):
    """Layer-1 brim rectangle (x0, y0, x1, y1) of the wipe tower at wipe_tower_x/y = tower."""
    return (tower[0] + BRIM_OFFSETS[0], tower[1] + BRIM_OFFSETS[1],
            tower[0] + BRIM_OFFSETS[2], tower[1] + BRIM_OFFSETS[3])


def check_tower(tower, discs, label=""):
    """Asserts the tower brim clears every disc center in `discs` by
    TOWER_DISC_MIN and the bed edges by TOWER_EDGE_MIN; returns
    (min disc clearance, min edge clearance)."""
    import math
    x0, y0, x1, y1 = tower_brim(tower)
    edge = min(x0, y0, BED - x1, BED - y1)
    assert edge >= TOWER_EDGE_MIN, f"{label}: tower {tower} brim {edge:.2f} mm from a bed edge (< {TOWER_EDGE_MIN})"
    disc = None
    for cx, cy in discs:
        d = math.hypot(max(x0 - cx, 0, cx - x1), max(y0 - cy, 0, cy - y1)) - DISC_R
        assert d >= TOWER_DISC_MIN, f"{label}: tower {tower} brim {d:.2f} mm from the disc at ({cx}, {cy}) (< {TOWER_DISC_MIN})"
        disc = d if disc is None else min(disc, d)
    return disc, edge


def _tower_vectors(tower, n_plates):
    """wipe_tower_x / wipe_tower_y vectors: `tower` is one (x, y) for every
    plate or a list with one (x, y) per plate."""
    towers = list(tower) if isinstance(tower[0], (tuple, list)) else [tower] * n_plates
    assert len(towers) == n_plates, (towers, n_plates)
    return [str(t[0]) for t in towers], [str(t[1]) for t in towers]


# ------------------------------------------------------------------- config
def read_bed_temps(filament_json):
    with open(filament_json) as f:
        fil = json.load(f)
    return {k: fil[k][0] for k in ("textured_plate_temp", "textured_plate_temp_initial_layer")}


def patch_config(cfg, bed_temps, tower, n_plates=1):
    """The common post-patch of a CLI-assembled project_settings.config:
    colors, SMOOTH_KEYS in the process diff list, textured PEI + the
    filament preset's stock temps (filament-scope keys go in diff slots
    1..3 or the GUI silently resets them), the dual-extruder flush block
    (2026-08-23: the 16-entry 4-filament placeholder made Studio read
    uninitialized memory, NaN on slice), the wipe tower position."""
    cfg["filament_colour"] = COLORS
    dsts = cfg.get("different_settings_to_system") or [""]
    assert len(dsts) == 5, dsts
    listed = [k for k in dsts[0].split(";") if k]
    for k in SMOOTH_KEYS:
        if k not in listed:
            listed.append(k)
    dsts[0] = ";".join(listed)
    cfg["curr_bed_type"] = BED_TYPE
    for k, v in bed_temps.items():
        cfg[k] = [v] * 3
    for fi in (1, 2, 3):
        fl = [x for x in dsts[fi].split(";") if x]
        for k in bed_temps:
            if k not in fl:
                fl.append(k)
        dsts[fi] = ";".join(fl)
    cfg["different_settings_to_system"] = dsts
    cfg["flush_volumes_matrix"] = FLUSH_3X3 + FLUSH_3X3
    cfg["flush_volumes_vector"] = ["140"] * 6
    cfg["flush_multiplier"] = ["1", "1"]
    cfg["flush_multiplier_fast"] = ["1.2", "1.2"]
    cfg["nozzle_flush_dataset"] = ["1", "2", "2", "1", "2", "2"]
    cfg["wipe_tower_x"], cfg["wipe_tower_y"] = _tower_vectors(tower, n_plates)
    return cfg


def check_config(c, bed_temps, tower, n_plates=1, label=""):
    assert c.get("filament_colour") == COLORS, f"{label}: colors"
    assert c.get("ironing_type") == "no ironing" and c.get("top_one_wall_type") == "not apply" \
        and c.get("top_surface_speed", [""])[0] == "60", f"{label}: coupon C recipe lost"
    assert c.get("wall_generator") == "arachne" and c.get("skirt_loops") == "2" \
        and c.get("initial_layer_speed", [""])[0] == "30", f"{label}: arachne/skirt/first layer lost"
    d0 = c["different_settings_to_system"][0].split(";")
    for k in SMOOTH_KEYS:
        assert k in d0, f"{label}: {k} not in diff list"
    assert c.get("curr_bed_type") == BED_TYPE, f"{label}: bed type"
    assert c.get("textured_plate_temp") == [bed_temps["textured_plate_temp"]] * 3, f"{label}: bed temp"
    assert (c.get("wipe_tower_x"), c.get("wipe_tower_y")) == _tower_vectors(tower, n_plates), \
        f"{label}: wipe tower {c.get('wipe_tower_x')} {c.get('wipe_tower_y')}"
    assert str(c.get("prime_tower_brim_width")) == "5", f"{label}: tower brim {c.get('prime_tower_brim_width')}"
    assert (str(c.get("prime_tower_rib_wall")), str(c.get("prime_tower_fillet_wall"))) == ("1", "1"), \
        f"{label}: tower rib/fillet wall {c.get('prime_tower_rib_wall')} {c.get('prime_tower_fillet_wall')}"
    assert (str(c.get("skirt_loops")), str(c.get("skirt_distance")), str(c.get("skirt_height"))) == ("2", "3", "1"), f"{label}: skirt"
    assert c.get("print_sequence") == "by layer", f"{label}: {c.get('print_sequence')}"
    assert len(c.get("flush_volumes_matrix")) == 18, f"{label}: flush block"


# ---------------------------------------------------------------- 3MF patch
def mesh_xml(oid, uuid, mesh):
    lines = [f'  <object id="{oid}" p:UUID="{uuid}" type="model">', "   <mesh>", "    <vertices>"]
    for x, y, z in mesh.vertices:
        lines.append(f'     <vertex x="{x:.6g}" y="{y:.6g}" z="{z:.6g}"/>')
    lines += ["    </vertices>", "    <triangles>"]
    for a, b, c in mesh.faces:
        lines.append(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>')
    lines += ["    </triangles>", "   </mesh>", "  </object>"]
    return "\n".join(lines) + "\n"


def modifier_part_xml(pid, name, src, tx, ty, tz, dx, dy, keys, nfaces):
    """A modifier_part block for model_settings.config; the region keys go
    BEFORE <mesh_stat/> (Studio drops keys after it)."""
    s = (f'    <part id="{pid}" subtype="modifier_part" uuid="7f0a1d2e-0000-4000-8000-{pid:012d}">\n'
         f'      <metadata key="name" value="{name}"/>\n'
         f'      <metadata key="matrix" value="1 0 0 {tx:.8g} 0 1 0 {ty:.8g} 0 0 1 {tz:.8g} 0 0 0 1"/>\n'
         f'      <metadata key="source_file" value="{src}"/>\n'
         '      <metadata key="source_object_id" value="0"/>\n'
         '      <metadata key="source_volume_id" value="0"/>\n'
         f'      <metadata key="source_offset_x" value="{dx:.8g}"/>\n'
         f'      <metadata key="source_offset_y" value="{dy:.8g}"/>\n'
         f'      <metadata key="source_offset_z" value="{tz:.8g}"/>\n')
    for k, v in keys.items():
        s += f'      <metadata key="{k}" value="{v}"/>\n'
    s += (f'      <mesh_stat face_count="{nfaces}" edges_fixed="0" degenerate_facets="0" facets_removed="0" '
          'facets_reversed="0" backwards_edges="0"/>\n    </part>\n')
    return s


def next_object_id(model3d, objfiles):
    return max(int(i) for i in re.findall(r'<object id="(\d+)"', model3d + "".join(objfiles.values()))) + 1


def object_pos(model3d, oid, anchor_center):
    """Plate position of an object's origin: its first component transform
    (the anchor part, listed first) minus the anchor mesh's bbox center."""
    om = re.search(rf'<object id="{oid}" [^>]*>\s*<components>(.*?)</components>', model3d, re.S)
    assert om, oid
    t = re.search(r'<component [^>]*transform="([^"]*)"', om.group(1)).group(1).split()
    return tuple(round(float(t[9 + i]) - anchor_center[i], 6) for i in range(3))


def inject_modifier(block, model3d, objfiles, oid, pid, name, src, mesh_c, mc, pos, keys):
    """Add one modifier part to object `oid`: the <part> at the end of its
    model_settings block, a <component> in 3dmodel.model and the mesh in the
    object's 3D/Objects file. mesh_c is the centered mesh, mc its original
    center in object mm, pos the object's plate position (object_pos)."""
    tx, ty, tz = pos[0] + mc[0], pos[1] + mc[1], pos[2] + mc[2]
    part = modifier_part_xml(pid, name, src, tx, ty, tz, mc[0], mc[1], keys, len(mesh_c.faces))
    block = block[:-len("</object>")] + part + "</object>"
    om = re.search(rf'<object id="{oid}" [^>]*>\s*<components>(.*?)</components>', model3d, re.S)
    assert om, oid
    path = re.search(r'p:path="([^"]+)"', om.group(1)).group(1)
    comp = (f'    <component p:path="{path}" objectid="{pid}" p:UUID="{pid:08x}-b206-40ff-9872-83e8017abed1" '
            f'transform="1 0 0 0 1 0 0 0 1 {tx:.8g} {ty:.8g} {tz:.8g}"/>\n')
    model3d = model3d[:om.end() - len("</components>")] + comp + model3d[om.end() - len("</components>"):]
    fname = path.lstrip("/")
    objfiles[fname] = objfiles[fname].replace(" </resources>",
                                              mesh_xml(pid, f"{pid:08x}-81cb-4c03-9d28-80fed5dfa1dc", mesh_c) + " </resources>", 1)
    return block, model3d


def check_object(body, okeys, mkeys, extruders, label=""):
    """Asserts on one model_settings object block: object keys in the head
    (before the first part), modifier keys before mesh_stat, normal-part
    extruders. Returns (n_normal, n_modifier)."""
    nm = re.search(r'<metadata key="name" value="([^"]*)"', body).group(1)
    head = body.split("<part ", 1)[0]
    for k, v in okeys.items():
        assert f'<metadata key="{k}" value="{v}"/>' in head, f"{label}: object {nm} lost {k}"
    if not okeys:
        assert "detect_narrow_internal_solid_infill" not in head, f"{label}: {nm} has an object key"
    parts = re.findall(r"<part .*?</part>", body, re.S)
    normal = [p for p in parts if 'subtype="normal_part"' in p]
    modp = [p for p in parts if 'subtype="modifier_part"' in p]
    ext = [re.search(r'"extruder" value="(\d)"', pb).group(1) for pb in normal]
    assert ext == extruders, f"{label}: {nm} part extruders {ext}"
    if mkeys:
        expected = mkeys if isinstance(mkeys, list) else [mkeys]
        assert len(modp) == len(expected), f"{label}: {nm} modifier parts {len(modp)}"
        for keys, mp in zip(expected, modp):          # injection order: letters, then back text
            pre = mp.split("<mesh_stat", 1)[0]
            for k, v in keys.items():
                assert f'<metadata key="{k}" value="{v}"/>' in pre, f"{label}: {nm} modifier lost {k} before mesh_stat"
            assert "<mesh_stat" in mp, (label, nm)
    else:
        assert not modp, f"{label}: {nm} has a modifier"
    return len(normal), len(modp)


def strip_recipe(src, dst, keep_object_key=False):
    """A/B helper: copy a built 3MF without the letter-tier modifier parts
    (and, unless keep_object_key, without the object keys), everything else
    byte-identical. Used to prove the recipe changes nothing outside the
    letter tier (gcode_features.py --baseline)."""
    import zipfile
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        model = zin.read("Metadata/model_settings.config").decode()
        model3d = zin.read("3D/3dmodel.model").decode()
        objfiles = {n: zin.read(n).decode() for n in zin.namelist() if n.startswith("3D/Objects/")}
        pids = re.findall(r'<part id="(\d+)" subtype="modifier_part"', model)
        assert pids, "no modifier parts to strip"
        model, n = re.subn(r'\s*<part id="\d+" subtype="modifier_part".*?</part>\n?', "\n", model, flags=re.S)
        assert n == len(pids)
        if not keep_object_key:
            model = re.sub(r'\s*<metadata key="detect_narrow_internal_solid_infill" value="0"/>', "", model)
        for pid in pids:
            model3d, n = re.subn(rf'\s*<component [^>]*objectid="{pid}"[^>]*/>', "", model3d)
            assert n == 1, (pid, n)
            for fname in objfiles:
                objfiles[fname], n = re.subn(rf'  <object id="{pid}" .*?</object>\n', "", objfiles[fname], flags=re.S)
                if n:
                    break
            else:
                raise AssertionError(f"mesh {pid} not found")
        for item in zin.infolist():
            if item.filename == "Metadata/model_settings.config":
                zout.writestr(item, model)
            elif item.filename == "3D/3dmodel.model":
                zout.writestr(item, model3d)
            elif item.filename in objfiles:
                zout.writestr(item, objfiles[item.filename])
            else:
                zout.writestr(item, zin.read(item.filename))


def cli(args, cwd, what):
    r = subprocess.run(["bambu-studio"] + args, capture_output=True, text=True, timeout=900, cwd=cwd)
    assert r.returncode == 0, f"CLI {what} rc={r.returncode}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    return r
