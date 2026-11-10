#!/usr/bin/env python3
"""Bambu Studio print 3MF for the rod hooks: ONE project file, ONE plate, N copies (default 5: Brian 2026-11-09, "there
should only be 5 pairs") of each hook standing on its 4 in bottom edge in one row, the tip hooks (rod-hook.stl) at the
back of the row and the butt hooks (rod-hook-butt.stl) in front, every copy with its own two 100% infill modifier pads at
the screw holes, verified by a real slice of the plate. PLATES says which plate each variant prints on; a variant per
plate (the 2026-11-09 two-plate file) is the same script with {"tip": 1, "butt": 2}.

    .venv/bin/python projects/Fishing-rod-holder/pipeline/make_print_3mf.py [--copies 5] [--scratch DIR]

Writes rod-hook.3mf and rod-hook-3mf-report.json beside the STLs. Plumbing only: the STLs are not touched. --copies is
per variant: 5 puts five tip hooks and five butt hooks on the plate.

<stem>.stl is the PRINT frame (Hook.standing): x along the bed from the jaw tip (0 to W), y the thickness (0 to T, the
countersinks open at y 0), z up (0 to H); the screw holes run along y at x = (CANT + SCREW_X) in, z = SCREW_Y in, with
each variant's own CANT (the butt hook's jaw reaches further). <stem>-model.stl is the flat model frame for the renders
and is never sliced. Every number here is read from rod_hook.py's VARIANTS at run time (CANT, W and H are derived there).

The recipe is the vault's (memory/feedback-stl-to-bambu-3mf.md), not a new one:
  presets     the include-merging flattener of projects/Cable-bin/pipeline/make_print_3mf.py over the installed BBL bundle;
              machine "Bambu Lab X2D 0.6 nozzle", process "0.30mm Standard @BBL X2D 0.6 nozzle", "Bambu PETG Basic @BBL X2D"
              (the three slice_stls.py quotes with). The overrides are written into the flattened process copy before the
              export AND into the 3MF's project_settings plus different_settings_to_system[0], or Studio's GUI resets them
  export      bambu-studio --arrange 1 ... --export-3mf raw.3mf rod-hook-1.stl ... rod-hook-butt-N.stl: one object per copy
              (a modifier belongs to an object, instances would share one). --arrange 1 makes the CLI write a plate block
              with a model_instance (and identify_id) per object; whatever plates its arranger opened (it packs 2 mm apart
              and may open plates of its own), they are read only for that metadata and rewritten as the plates PLATES
              names, in Studio's plate grid: plate p's bed origin is (p - 1) * 307.2 mm along x (knowledge/printer-x2d.md)
  placement   every item transform is written here from the file's own geometry: one row along y per plate, the variants
              in PLATES order from the back, GAP between the faces of neighbours, centred on its plate, nothing rotated
              (the Cable-bin pattern: the arranger is not trusted)
  screw pads  projects/Skateboard-wall-holder/pipeline/make_print_3mf.py's modifier parts through the Sharks helpers
              (fillcore_mod.inject_modifier): per copy two discs PAD_D across with their axis along y, PAD_INSET inside
              both faces, the screw hole and its countersink cleared by HOLE_CLEAR, sparse_infill_density 100%. Built per
              variant in the model frame, stood up with its Hook.standing like the STL, proven wholly inside the body
              twice, build123d against the CAD and OpenSCAD against the STL (memory/feedback-modifiers-inside-the-body.md),
              then proven solid in the sliced G-code by plastic per volume against a plain window of the same size
              (knowledge/learnings/nacs-wall-holder.md)
  slice       the CLI cannot slice its own export (rc 156), so projects/Sharks-nametag/pipeline/graft_slice.py adds the
              GUI-only keys to a throwaway copy; one plate at a time (the G-code of each plate is plate-local), the whole
              run re-executed inside the memory-capped systemd scope (CLAUDE.md, heavy local jobs)
Opening rod-hook.3mf in Bambu Studio is still the ground truth for how the plate and the modifiers look.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
VAULT = os.path.dirname(os.path.dirname(PROJECT))
sys.path.insert(0, os.path.join(VAULT, "projects", "Sharks-nametag", "pipeline"))
sys.path.insert(0, PROJECT)
from fillcore_mod import centered, inject_modifier, next_object_id, object_pos  # noqa: E402
from graft_slice import graft_slice  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")   # the preset bundle of the installed Studio
OPENSCAD = os.path.expanduser("~/.local/bin/openscad")

MACHINE = "Bambu Lab X2D 0.6 nozzle"
PROCESS = "0.30mm Standard @BBL X2D 0.6 nozzle"
FILAMENT = "Bambu PETG Basic @BBL X2D"
FILAMENT_COLOUR = "#2F6FE4"

OUT = "rod-hook.3mf"
REPORT = "rod-hook-3mf-report.json"
PLATES = {"tip": 1, "butt": 1}   # rod_hook.VARIANTS in row order and the plate each prints on: one plate, tip hooks at the back
COPIES = 5                       # per variant: five pairs (Brian 2026-11-09)
LAYER = 0.3
BED = 256.0
BED_CENTRE = (128.0, 128.0)
BED_TYPE = "Textured PEI Plate"
PLATE_STRIDE = BED * 1.2         # 307.2: Studio's plate grid, two columns, rows in negative y (knowledge/printer-x2d.md)
PLATE_COLS = 2
GRID = (1, 10)                   # hooks per plate: columns along x, rows along y (a standing hook is W x T on the bed)
GAP = 13.5                       # between the faces of neighbouring hooks (asked: at least 12); pitch GAP + T

PAD_D = 22.0                     # solid infill this wide around each screw hole
PAD_INSET = 0.2                  # the pad stops this far inside the two faces (y 0 and y T in the print frame)
HOLE_CLEAR = 0.6                 # the hole and countersink are cleared by one 0.6 line, so nothing shows through the hole in Studio
PAD_NAMES = ("pad-bottom", "pad-top")      # the lower screw, the upper screw (z in the print frame)
PAD_KEYS = {"sparse_infill_density": "100%"}
WALL = 2 * 0.62                  # two 0.62 mm lines: the hook's walls on both faces
# G-code density windows: x within WIN_X of the hole centre, the core of the thickness (CORE_INSET inside both faces,
# so no wall lines), layers from WIN_DZ[0] to WIN_DZ[1] below and above the hole centre (off the hole, its countersink
# and their walls, inside the PAD_D / 2 disc), against the same window at the height midway between the holes
WIN_X = 4.0
CORE_INSET = WALL + 0.26
WIN_DZ = (5.0, 9.5)

SCALARS = {   # process scope, different_settings_to_system[0]
    "curr_bed_type": BED_TYPE,
    "brim_type": "no_brim",
    "skirt_loops": "2",          # memory/feedback-keep-skirt.md, never 0
    "skirt_distance": "3",
    "skirt_height": "1",
    "wall_loops": "2",
    "sparse_infill_density": "15%",
    "sparse_infill_pattern": "gyroid",
}
SCOPE = ["systemd-run", "--user", "--scope", "-p", "MemoryMax=44G", "-p", "MemoryHigh=40G",
         "-p", "MemorySwapMax=2G", "-p", "OOMPolicy=continue", "--"]
SCOPE_MARK = "ROD_HOOK_3MF_IN_SCOPE"
NOTE = ("Open rod-hook.3mf once in Bambu Studio to confirm the plate shows all ten hooks in one row: five tip hooks at the back, "
        "five butt hooks in front. The GUI is the ground truth for the plate layout and the modifiers.")


# ------------------------------------------------------------------------------------------------------------ presets
def load(kind, name):
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
    """Resolve the inherits chain and each preset's include templates; the CLI cannot do this for X2D presets."""
    chain = [load(kind, name)]
    while "inherits" in chain[-1]:
        chain.append(load(kind, chain[-1]["inherits"]))
    merged = {}
    for layer in reversed(chain):
        for inc in layer.get("include", []):
            merged.update({k: v for k, v in load(kind, inc).items() if k not in ("name", "type", "from", "instantiation")})
        merged.update(layer)
    merged.pop("inherits", None)
    merged.pop("include", None)
    merged["name"] = name
    return merged


def write_presets(d):
    process = flatten("process", PROCESS)
    process.update(SCALARS)
    for fn, preset in (("machine.json", flatten("machine", MACHINE)), ("process.json", process), ("filament.json", flatten("filament", FILAMENT))):
        with open(f"{d}/{fn}", "w") as f:
            json.dump(preset, f)


# --------------------------------------------------------------------------------------------------------- geometry
def hook_geometry(variant, plate, n):
    """One variant of rod_hook.py (rod_hook.VARIANTS[variant]) with the plate it prints on and its copy count: its stem,
    thickness T, width W, height H, the screw holes in the model frame (x, y) and in the print frame (x, z), lower screw
    first, the hole and countersink diameters, the CAD solid (model frame), the standing transform, and its print STL's
    extents, minimum corner and centre."""
    import rod_hook as M
    v = M.VARIANTS[variant]
    ys = sorted(M.SCREW_Y)
    stl = trimesh.load(f"{PROJECT}/{v.stem}.stl")
    assert M.LAYER_H == LAYER, f"rod_hook.py checks the standing print at {M.LAYER_H} mm layers, this file slices at {LAYER}"
    geo = {"variant": variant, "stem": v.stem, "plate": plate, "n": n, "T": M.T * M.IN, "W": v.W * M.IN, "H": M.H * M.IN,
           "model_holes": [(M.SCREW_X * M.IN, y * M.IN) for y in ys],
           "holes": [((v.CANT + M.SCREW_X) * M.IN, y * M.IN) for y in ys],
           "hole_d": M.HOLE_D, "csk_d": M.CSK_D, "cad": v.build(), "standing": v.standing,
           "ext": stl.extents, "stl_lo": stl.bounds[0], "stl_c": stl.bounds.mean(axis=0)}
    assert np.allclose(stl.extents, [geo["W"], geo["T"], geo["H"]], atol=0.01), f"{v.stem}.stl {stl.extents} is not the standing print frame W x T x H"
    return geo


def scad_volume(scad, out):
    """mm3 of an OpenSCAD (Manifold) boolean over STL meshes; 0 for the empty result an empty boolean leaves behind."""
    src = out[:-4] + ".scad"
    with open(src, "w") as f:
        f.write(scad + "\n")
    r = subprocess.run([OPENSCAD, "--backend=Manifold", "-o", out, src], capture_output=True, text=True, timeout=600)
    assert r.returncode == 0 or "empty" in (r.stderr + r.stdout), r.stderr[-1500:]
    try:
        m = trimesh.load(out, force="mesh")
        return 0.0 if m.is_empty else abs(float(m.volume))
    except Exception:
        return 0.0


def build_pads(d, geo):
    """One pad per screw hole of one variant, built in the model frame like the hook: a PAD_D cylinder along the hole's
    axis from PAD_INSET over the back face to PAD_INSET under the front face, the hole and its 90 degree countersink
    cleared by HOLE_CLEAR. Proven wholly inside the CAD body (volume outside 0), stood up with the variant's standing
    transform, exported to <stem>-<pad>.stl, and the pair proven again against <stem>.stl with OpenSCAD."""
    from build123d import Cone, Cylinder, Pos, export_stl
    T, hook, stem = geo["T"], geo["cad"], geo["stem"]
    pads = []
    for name, (hx, hy), (px, pz) in zip(PAD_NAMES, geo["model_holes"], geo["holes"]):
        pad = Pos(hx, hy, T / 2) * Cylinder(PAD_D / 2, T - 2 * PAD_INSET)
        pad -= Pos(hx, hy, T / 2) * Cylinder(geo["hole_d"] / 2 + HOLE_CLEAR, T + 2)
        # rod_hook.py's countersink is a 90 degree cone with its apex csk_d / 2 under the front face; the same cone pushed
        # HOLE_CLEAR along its surface normal has its apex HOLE_CLEAR * sqrt(2) lower
        apex = T - geo["csk_d"] / 2 - HOLE_CLEAR * math.sqrt(2)
        h = T - apex + 1.0
        pad -= Pos(hx, hy, apex + h / 2) * Cone(0.0, h, h)
        inside = (pad & hook).volume
        outside = pad.volume - inside
        assert abs(outside) < 1e-3, f"{stem} {name}: {outside:.4f} mm3 of the pad lies outside the CAD body"
        fname = f"{stem}-{name}.stl"
        path = f"{d}/{fname}"
        export_stl(geo["standing"](pad), path)
        m = trimesh.load(path)
        assert m.is_watertight and len(m.split()) == 1, f"{stem} {name}: the pad mesh is not one closed body"
        lo, hi = m.bounds
        assert abs(lo[1] - PAD_INSET) < 1e-3 and abs(hi[1] - (T - PAD_INSET)) < 1e-3, f"{stem} {name}: y span {lo[1]:.3f}..{hi[1]:.3f}"
        assert np.allclose((lo + hi) / 2, [px, T / 2, pz], atol=0.02), f"{stem} {name}: centre {(lo + hi) / 2}, hole at {(px, pz)}"
        pads.append({"name": name, "file": fname, "path": path, "centre_print_mm": [round(px, 4), round(T / 2, 4), round(pz, 4)],
                     "volume_mm3": round(float(m.volume), 1), "outside_cad_mm3": round(float(abs(outside)), 6)})
    body = f"{PROJECT}/{stem}.stl"
    both = " ".join(f'import("{p["path"]}");' for p in pads)
    outside = scad_volume(f'difference() {{ union() {{ {both} }} import("{body}"); }}', f"{d}/{stem}-pads-outside.stl")
    inside = scad_volume(f'intersection() {{ union() {{ {both} }} import("{body}"); }}', f"{d}/{stem}-pads-inside.stl")
    total = sum(p["volume_mm3"] for p in pads)
    assert outside < 1e-3, f"{outside:.3f} mm3 of the pads lie outside {stem}.stl"
    assert abs(inside - total) < 0.002 * total, f"{stem}: pads inside the STL {inside:.1f} mm3 vs the pads' {total:.1f} mm3: an import failed"
    return pads, {"outside_stl_mm3": round(outside, 4), "inside_stl_mm3": round(inside, 1), "pads_mm3": round(total, 1)}


# -------------------------------------------------------------------------------------------------------- 3MF reading
def read_all(path):
    with zipfile.ZipFile(path) as z:
        return [(i, z.read(i.filename)) for i in z.infolist()]


def write_all(path, entries, replace):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item, data in entries:
            zout.writestr(item, replace.get(item.filename, data))


def matrix(transform):
    """3MF transform (12 numbers, row-major 3x3 then the translation) as a 4x4 that acts on column vectors."""
    t = [float(v) for v in transform.split()] if transform else [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    m = np.eye(4)
    m[:3, :3] = np.array(t[:9]).reshape(3, 3).T
    m[:3, 3] = t[9:]
    return m


def components(files):
    """{object id: (item transform, [(sub id, component transform, vertices), ...])} for every build item."""
    main = files["3D/3dmodel.model"].decode()
    comps = {oid: re.findall(r'<component p:path="([^"]+)" objectid="(\d+)"(?: [^>]*?transform="([^"]*)")?', body)
             for oid, body in re.findall(r'<object id="(\d+)"[^>]*>(.*?)</object>', main, re.S)}
    out = {}
    for oid, tr in re.findall(r'<item objectid="(\d+)"[^>]*?transform="([^"]*)"', main):
        parts = []
        for path, sub_id, comp_t in comps[oid]:
            sub = files[path.lstrip("/")].decode()
            mesh = re.search(rf'<object id="{sub_id}"[^>]*>(.*?)</object>', sub, re.S).group(1)
            parts.append((sub_id, comp_t, np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', mesh), dtype=float)))
        out[oid] = (tr, parts)
    return out


def world_components(files):
    """{object id: [(sub id, lo, hi), ...]}: every component of every build item in world mm, from the meshes and
    transforms in the 3MF itself (item transform x component transform x the mesh's own coordinates)."""
    out = {}
    for oid, (tr, parts) in components(files).items():
        boxes = []
        for sub_id, comp_t, v in parts:
            w = (matrix(tr) @ matrix(comp_t) @ np.c_[v, np.ones(len(v))].T).T[:, :3]
            boxes.append((sub_id, w.min(axis=0), w.max(axis=0)))
        out[oid] = boxes
    return out


def object_bounds(files):
    """{object id: (lo, hi)} in the object's own frame (component transforms only, no item transform); asserts the
    component transforms carry no rotation, so an identity item rotation prints the mesh as the STL has it."""
    out = {}
    for oid, (_, parts) in components(files).items():
        pts = []
        for sub_id, comp_t, v in parts:
            m = matrix(comp_t)
            assert np.allclose(m[:3, :3], np.eye(3)), f"component {sub_id} of object {oid} is rotated: {m[:3, :3]}"
            pts.append((m @ np.c_[v, np.ones(len(v))].T).T[:, :3])
        pts = np.vstack(pts)
        out[oid] = (pts.min(axis=0), pts.max(axis=0))
    return out


def object_names(msc):
    """{object name: object id} from model_settings.config; the CLI does not keep objects in input order."""
    return dict((name, oid) for oid, name in re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', msc))


def plate_members(msc):
    """[(plater_id, [object ids])] from the plate blocks of model_settings.config."""
    out = []
    for blk in re.findall(r"<plate>(.*?)</plate>", msc, re.S):
        pid = int(re.search(r'<metadata key="plater_id" value="(\d+)"/>', blk).group(1))
        out.append((pid, re.findall(r'<metadata key="object_id" value="(\d+)"/>', blk)))
    return out


def label(stem, i):
    return f"{stem}-{i}"


def variant_of(name, geos):
    """(variant, hook number) of an object or STL file name such as rod-hook-butt-3 or rod-hook-3.stl, by its stem."""
    stem, num = re.match(r"^(.+)-(\d+)(?:\.stl)?$", name).groups()
    hits = [v for v, g in geos.items() if g["stem"] == stem]
    assert len(hits) == 1, f"{name}: stem {stem} is none of {[g['stem'] for g in geos.values()]}"
    return hits[0], int(num)


def roster(names, geos):
    """{object id: (variant, hook number)} from the object names of model_settings.config."""
    return {oid: variant_of(name, geos) for name, oid in names.items()}


def plate_rows(who, geos):
    """{plate: [(variant, hook number, object id), ...]} in row order: the variants in PLATES order from the back of
    the plate, each variant's hooks in number order."""
    rows = {}
    for v, g in geos.items():
        mine = sorted((num, oid) for oid, (vv, num) in who.items() if vv == v)
        rows.setdefault(g["plate"], []).extend((v, num, oid) for num, oid in mine)
    return rows


def plate_name(row):
    """'tip hooks 1-5, butt hooks 1-5': each variant on the plate with its hook numbers, in row order."""
    parts = []
    for v in dict.fromkeys(v for v, _, _ in row):
        n = sorted(num for vv, num, _ in row if vv == v)
        span = str(n[0]) if len(n) == 1 else f"{n[0]}-{n[-1]}" if n == list(range(n[0], n[-1] + 1)) else ", ".join(map(str, n))
        parts.append(f"{v} hooks {span}")
    return ", ".join(parts)


def plate_origin(p):
    """World (x, y) of the bed origin of plate p (1-indexed): Studio's two-column plate grid, rows in negative y."""
    return ((p - 1) % PLATE_COLS) * PLATE_STRIDE, -((p - 1) // PLATE_COLS) * PLATE_STRIDE


def slot_centre(slot, ext):
    """Plate-local bed (x, y) of the footprint centre of grid slot `slot`: columns along x, rows from the back."""
    col, row = slot % GRID[0], slot // GRID[0]
    return (BED_CENTRE[0] + (col - (GRID[0] - 1) / 2) * (ext[0] + GAP),
            BED_CENTRE[1] + ((GRID[1] - 1) / 2 - row) * (ext[1] + GAP))


def expected_targets(names, geos):
    """{object id: (plate, slot, world x, world y)}: each plate's row from the back, the variants in PLATES order and
    each variant's hooks in number order; every hook centred in x on its plate (the two hooks differ in width)."""
    assert len({round(g["T"], 3) for g in geos.values()}) == 1, "the variants differ in thickness, the row pitch would not be uniform"
    out = {}
    for p, row in plate_rows(roster(names, geos), geos).items():
        assert len(row) <= GRID[0] * GRID[1], f"{len(row)} hooks on plate {p}, the {GRID[0]} x {GRID[1]} grid holds {GRID[0] * GRID[1]}"
        ox, oy = plate_origin(p)
        for slot, (v, _, oid) in enumerate(row):
            cx, cy = slot_centre(slot, geos[v]["ext"])
            out[oid] = (p, slot, ox + cx, oy + cy)
    return out


# ------------------------------------------------------------------------------------------------------------ author
def author(src, dst, geos):
    """The plates PLATES names: the CLI's first plate block lends its metadata to every plate, each object goes on its
    variant's plate (the arranger's own plates and transforms are discarded) and is placed in that plate's row from its
    own geometry; the objects and the plates are named, the overrides applied, the filament pinned to extruder 1 and
    coloured. Returns how many plates the CLI's arranger had opened."""
    entries = read_all(src)
    files = {i.filename: data for i, data in entries}
    model = files["3D/3dmodel.model"].decode()
    msc = files["Metadata/model_settings.config"].decode()
    names = object_names(msc)
    assert set(names) == {f"{label(g['stem'], i)}.stl" for g in geos.values() for i in range(1, g["n"] + 1)}, f"objects in the export: {sorted(names)}"
    who = roster(names, geos)
    targets = expected_targets(names, geos)

    # item transforms: identity rotation, translation chosen so the object's own bounds land on target with floor on z 0
    bounds = object_bounds(files)
    def move(m):
        oid = re.search(r'objectid="(\d+)"', m.group(1)).group(1)
        _, _, cx, cy = targets[oid]
        lo, hi = bounds[oid]
        return m.group(1) + 'transform="1 0 0 0 1 0 0 0 1 %.6g %.6g %.6g"' % (cx - (lo[0] + hi[0]) / 2, cy - (lo[1] + hi[1]) / 2, -lo[2])
    model, moved = re.subn(r'(<item [^>]*?)transform="([^"]*)"', move, model)
    assert moved == len(names), (moved, len(names))

    # plate blocks: the first CLI block's own metadata for every plate (plater_id rewritten), a model_instance per object
    # with the CLI's identify_id (or a fresh one for any object the arranger left off its plates)
    blocks = re.findall(r"  <plate>.*?</plate>\n", msc, re.S)
    assert blocks and "".join(blocks) in msc, "plate blocks missing or not contiguous"
    inst = dict(re.findall(r'<metadata key="object_id" value="(\d+)"/>\s*<metadata key="instance_id" value="0"/>\s*'
                           r'<metadata key="identify_id" value="(\d+)"/>', msc))
    head = [l for l in blocks[0].split("<model_instance>")[0].splitlines() if "<metadata" in l]
    assert any('key="plater_id" value="1"' in l for l in head), blocks[0]
    ident = max([int(v) for v in inst.values()] + [100])
    plates = []
    rows = plate_rows(who, geos)
    for p, row in rows.items():
        plate = ["  <plate>"]
        for l in head:
            l = re.sub(r'key="plater_id" value="\d+"', f'key="plater_id" value="{p}"', l)
            l = l.replace('key="plater_name" value=""', f'key="plater_name" value="{plate_name(row)}"')
            plate.append(l.replace('key="filament_map_mode" value="Auto For Flush"', 'key="filament_map_mode" value="Manual"'))
        for _, _, oid in row:
            if oid not in inst:
                ident += 11
                inst[oid] = str(ident)
            plate += ["    <model_instance>", f'      <metadata key="object_id" value="{oid}"/>', '      <metadata key="instance_id" value="0"/>',
                      f'      <metadata key="identify_id" value="{inst[oid]}"/>', "    </model_instance>"]
        plate.append("  </plate>")
        plates.append("\n".join(plate) + "\n")
    msc = msc.replace("".join(blocks), "".join(plates))
    for src_name in names:
        msc = msc.replace(f'key="name" value="{src_name}"', f'key="name" value="{src_name[:-4]}"')
    seq = json.loads(files["Metadata/filament_sequence.json"])
    seq = {f"plate_{p}": seq.get(f"plate_{p}", {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []}) for p in rows}

    cfg = json.loads(files["Metadata/project_settings.config"])
    cfg.update(SCALARS)
    # any key changed in a project 3MF must be listed here or Studio's GUI resets it on open;
    # the list is positional: [0] process, [1..N] the N filaments, [N+1] machine
    n_fil = len(cfg["filament_settings_id"])
    assert n_fil == 1, cfg["filament_settings_id"]
    diff = cfg.get("different_settings_to_system") or []
    diff += [""] * (n_fil + 2 - len(diff))
    diff[0] = ";".join(sorted(set(x for x in diff[0].split(";") if x) | set(SCALARS)))
    cfg["different_settings_to_system"] = diff
    cfg["filament_map_mode"], cfg["filament_map"], cfg["filament_nozzle_map"] = "Manual", ["1"], ["1"]
    cfg["filament_colour"] = cfg["filament_multi_colour"] = [FILAMENT_COLOUR]
    write_all(dst, entries, {"3D/3dmodel.model": model.encode(), "Metadata/model_settings.config": msc.encode(),
                             "Metadata/project_settings.config": json.dumps(cfg, indent=4).encode(),
                             "Metadata/filament_sequence.json": json.dumps(seq).encode()})
    return len(blocks)


def add_screw_pads(path, pads, geos):
    """Two modifier parts per object, sparse_infill_density 100%, the pads of the object's own variant: each pad mesh
    stored centred the way the CLI stores parts and placed in the object's frame where the STL frame puts it (the
    object's first component transform minus the stored body mesh's centre tells where the STL origin sits in that frame)."""
    entries = read_all(path)
    files = {i.filename: data for i, data in entries}
    model3d = files["3D/3dmodel.model"].decode()
    objfiles = {n: files[n].decode() for n in files if n.startswith("3D/Objects/")}
    settings = files["Metadata/model_settings.config"].decode()
    meshes = {v: [(p["name"], p["file"], *centered(trimesh.load(p["path"]))) for p in pads[v]] for v in geos}
    names = object_names(settings)
    count = 0
    for name, oid in names.items():
        v, _ = variant_of(name, geos)
        block = re.search(rf'<object id="{oid}">.*?</object>', settings, re.S).group(0)
        comp = re.search(rf'<object id="{oid}" [^>]*>\s*<components>\s*<component p:path="([^"]+)" objectid="(\d+)"', model3d, re.S)
        body = re.search(rf'<object id="{comp.group(2)}"[^>]*>(.*?)</object>', objfiles[comp.group(1).lstrip("/")], re.S).group(1)
        vtx = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', body), dtype=float)
        stored_c = (vtx.min(axis=0) + vtx.max(axis=0)) / 2
        pos = object_pos(model3d, oid, geos[v]["stl_c"] - stored_c)
        new_block = block
        for pname, fname, mesh_c, mc in meshes[v]:
            pid = next_object_id(model3d, objfiles)
            new_block, model3d = inject_modifier(new_block, model3d, objfiles, oid, pid, pname, fname, mesh_c, mc, pos, PAD_KEYS)
            count += 1
        settings = settings.replace(block, new_block)
    replace = {n: val.encode() for n, val in objfiles.items()}
    replace["3D/3dmodel.model"] = model3d.encode()
    replace["Metadata/model_settings.config"] = settings.encode()
    write_all(path, entries, replace)
    return count


# ------------------------------------------------------------------------------------------------------------ checks
def check_settings(path, what, geos):
    files = dict((i.filename, d) for i, d in read_all(path))
    cfg = json.loads(files["Metadata/project_settings.config"])
    for k, v in SCALARS.items():
        assert cfg[k] == v, f"{what}: {k} did not stick: {cfg[k]}"
    diff = cfg["different_settings_to_system"]
    assert len(diff) == 3, f"{what}: different_settings_to_system has {len(diff)} slots, expected process, filament, machine"
    assert set(SCALARS) <= set(diff[0].split(";")), f"{what}: process keys missing from different_settings_to_system[0]: {diff[0]}"
    assert cfg["printer_settings_id"] == MACHINE and cfg["print_settings_id"] == PROCESS and cfg["filament_settings_id"] == [FILAMENT], \
        (cfg["printer_settings_id"], cfg["print_settings_id"], cfg["filament_settings_id"])
    assert cfg["nozzle_diameter"][0] == "0.6" and cfg["layer_height"] == f"{LAYER:g}", (cfg["nozzle_diameter"], cfg["layer_height"])
    assert cfg["textured_plate_temp"] == ["70"], cfg["textured_plate_temp"]
    assert cfg["filament_map_mode"] == "Manual" and cfg["filament_map"] == ["1"] and cfg["filament_nozzle_map"] == ["1"], \
        f"{what}: not pinned to extruder 1: {cfg['filament_map_mode']}, {cfg['filament_map']}, {cfg['filament_nozzle_map']}"
    assert cfg["filament_colour"] == [FILAMENT_COLOUR], cfg["filament_colour"]

    msc = files["Metadata/model_settings.config"].decode()
    names = object_names(msc)
    assert set(names) == {label(g["stem"], i) for g in geos.values() for i in range(1, g["n"] + 1)}, f"{what}: object names {sorted(names)}"
    who = roster(names, geos)
    plates = plate_members(msc)
    rows = plate_rows(who, geos)
    assert [pid for pid, _ in plates] == list(rows), f"{what}: plate ids {[pid for pid, _ in plates]}, expected {list(rows)}"
    blocks = re.findall(r"<plate>(.*?)</plate>", msc, re.S)
    for (pid, members), blk in zip(plates, blocks):
        mine = sorted(oid for _, _, oid in rows[pid])
        assert sorted(members) == mine, f"{what}: plate {pid} lists {sorted(members)}, expected {mine}"
        assert 'key="filament_map_mode" value="Manual"' in blk, f"{what}: plate {pid} filament map mode"
        want = plate_name(rows[pid])
        got = re.search(r'key="plater_name" value="([^"]*)"', blk).group(1)
        assert got == want, f"{what}: plate {pid} is named {got!r}, expected {want!r}"
    for name, oid in names.items():
        block = re.search(rf'<object id="{oid}">.*?</object>', msc, re.S).group(0)
        assert len(re.findall(r'<part [^>]*subtype="normal_part"', block)) == 1, f"{what}: {name} normal parts"
        mods = re.findall(r'<part [^>]*subtype="modifier_part".*?</part>', block, re.S)
        got = []
        for mp in mods:
            nm = re.search(r'<metadata key="name" value="([^"]*)"', mp).group(1)
            pre = mp.split("<mesh_stat", 1)[0]
            for k, v in PAD_KEYS.items():
                assert f'<metadata key="{k}" value="{v}"/>' in pre, f"{what}: {name} {nm} lost {k} = {v} before mesh_stat"
            got.append(nm)
        assert sorted(got) == sorted(PAD_NAMES), f"{what}: {name} modifier parts {got}"
    return files, names, plates


def check_placement(files, names, geos, what):
    """Every hook unrotated, floor on z 0, footprint centred on its slot of its plate's row inside that plate's bed,
    neighbours exactly GAP apart, by the 3MF's own geometry. Returns the per-hook world boxes."""
    comps = world_components(files)
    targets = expected_targets(names, geos)
    who = roster(names, geos)
    by_id = {oid: name for name, oid in names.items()}
    assert set(comps) == set(by_id), f"{what}: build items {sorted(comps)} vs objects {sorted(by_id)}"
    result, boxes = {}, {}
    for oid, parts in comps.items():
        v = who[oid][0]
        ext = geos[v]["ext"]
        body = [c for c in parts if np.allclose(c[2] - c[1], ext, atol=0.01)]
        assert len(body) == 1, f"{what}: {by_id[oid]} has no component with the STL's extents {ext}: rotated?"
        lo, hi = body[0][1], body[0][2]
        p, slot, cx, cy = targets[oid]
        ox, oy = plate_origin(p)
        assert abs((lo[0] + hi[0]) / 2 - cx) < 0.01 and abs((lo[1] + hi[1]) / 2 - cy) < 0.01, f"{what}: {by_id[oid]} not at {(cx, cy)}: {lo} {hi}"
        assert abs(lo[2]) < 0.01, f"{what}: {by_id[oid]} floor at z {lo[2]:.3f}"
        assert lo[0] >= ox + 5 and lo[1] >= oy + 5 and hi[0] <= ox + BED - 5 and hi[1] <= oy + BED - 5, \
            f"{what}: {by_id[oid]} within 5 mm of plate {p}'s edge: {lo} {hi}"
        boxes[(p, slot)] = (lo, hi)
        result[by_id[oid]] = {"variant": v, "plate": p, "slot": slot, "min_mm": [round(float(x), 2) for x in lo], "max_mm": [round(float(x), 2) for x in hi]}
    for (p, slot), (lo, hi) in boxes.items():
        if slot % GRID[0] != GRID[0] - 1 and (p, slot + 1) in boxes:
            got = boxes[(p, slot + 1)][0][0] - hi[0]
            assert abs(got - GAP) < 0.01, f"{what}: plate {p} slots {slot} and {slot + 1} are {got:.2f} mm apart in x, expected {GAP}"
        if (p, slot + GRID[0]) in boxes:
            got = lo[1] - boxes[(p, slot + GRID[0])][1][1]
            assert abs(got - GAP) < 0.01, f"{what}: plate {p} slots {slot} and {slot + GRID[0]} are {got:.2f} mm apart in y, expected {GAP}"
    return result


def check_modifiers(files, names, geos, what):
    """Every object carries exactly two extra components whose world boxes are the two pads of its variant: centred on
    the hook's screw holes, PAD_D across in x and z, PAD_INSET inside both faces in y and well inside the outline (the
    3MF's own geometry)."""
    comps = world_components(files)
    who = roster(names, geos)
    for name, oid in names.items():
        g = geos[who[oid][0]]
        T, ext = g["T"], g["ext"]
        parts = comps[oid]
        body = [c for c in parts if np.allclose(c[2] - c[1], ext, atol=0.01)]
        pads = [c for c in parts if not np.allclose(c[2] - c[1], ext, atol=0.01)]
        assert len(body) == 1 and len(pads) == len(PAD_NAMES), f"{what}: {name} has {len(parts)} components"
        blo, bhi = body[0][1], body[0][2]
        origin = blo - g["stl_lo"]
        for pname, (hx, hz) in zip(PAD_NAMES, g["holes"]):
            want = origin + [hx, T / 2, hz]
            hit = [c for c in pads if np.allclose((c[1] + c[2]) / 2, want, atol=0.05)]
            assert len(hit) == 1, f"{what}: {name}: no modifier centred on its {pname} hole at {want}"
            lo, hi = hit[0][1], hit[0][2]
            assert np.allclose(hi - lo, [PAD_D, T - 2 * PAD_INSET, PAD_D], atol=0.1), f"{what}: {name} {pname} box {hi - lo}"
            assert lo[1] >= blo[1] + PAD_INSET - 1e-3 and hi[1] <= bhi[1] - PAD_INSET + 1e-3, f"{what}: {name} {pname} reaches a face: y {lo[1]:.3f}..{hi[1]:.3f}"
            assert lo[0] >= blo[0] + 1 and hi[0] <= bhi[0] - 1 and lo[2] >= blo[2] + 1 and hi[2] <= bhi[2] - 1, f"{what}: {name} {pname} reaches the outline"


# ------------------------------------------------------------------------------------------------------------- G-code
def gcode_stats(gcode):
    """Extruded filament (mm) per G-code feature, the xy extent of all extrusion moves, and the top layer height."""
    used, feat, x, y, z_top, box = {}, "", 0.0, 0.0, 0.0, [1e9, 1e9, -1e9, -1e9]
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line.startswith("; Z_HEIGHT:"):
            z_top = max(z_top, float(line.split(":")[1]))
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, me = re.search(r" X([-0-9.]+)", line), re.search(r" Y([-0-9.]+)", line), re.search(r" E([-0-9.]+)", line)
            x, y = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if feat and me and float(me.group(1)) > 0 and (mx or my):
                used[feat] = used.get(feat, 0.0) + float(me.group(1))
                box[0], box[1], box[2], box[3] = min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y)
    return {k: round(v, 1) for k, v in sorted(used.items(), key=lambda kv: -kv[1])}, [round(v, 2) for v in box], z_top


def clip_fraction(x0, y0, x1, y1, w):
    """Fraction of the segment inside the window (x0, y0, x1, y1) = w, by Liang-Barsky."""
    dx, dy = x1 - x0, y1 - y0
    if dx == 0 and dy == 0:
        return 1.0 if w[0] <= x0 <= w[2] and w[1] <= y0 <= w[3] else 0.0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - w[0]), (dx, w[2] - x0), (-dy, y0 - w[1]), (dy, w[3] - y0)):
        if p == 0:
            if q < 0:
                return 0.0
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    return max(0.0, t1 - t0)


def plastic_density(gcode, windows):
    """Plastic per volume (mm3 of filament per mm3 of window) in each window (x0, y0, x1, y1, z0, z1) over the layers
    whose height lies in [z0, z1]. Every extrusion move (G1, and G2/G3 as its chord) is clipped to the window and its E
    split by the clipped fraction: midpoint tests fail on long solid lines (knowledge/learnings/nacs-wall-holder.md)."""
    assert re.search(r"^; use_relative_e_distances = 1$", gcode, re.M), "E is not relative, the per-move E sums are meaningless"
    area = math.pi * (1.75 / 2) ** 2
    used, layers = {k: 0.0 for k in windows}, {k: 0 for k in windows}
    active, x, y = [], 0.0, 0.0
    for line in gcode.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":")[1])
            active = [(k, w) for k, w in windows.items() if w[4] <= z <= w[5]]
            for k, _ in active:
                layers[k] += 1
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, me = re.search(r" X([-0-9.]+)", line), re.search(r" Y([-0-9.]+)", line), re.search(r" E([-0-9.]+)", line)
            nx, ny = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if active and me and float(me.group(1)) > 0 and (mx or my):
                e = float(me.group(1))
                for k, w in active:
                    if max(x, nx) < w[0] or min(x, nx) > w[2] or max(y, ny) < w[1] or min(y, ny) > w[3]:
                        continue
                    f = clip_fraction(x, y, nx, ny, w)
                    if f:
                        used[k] += e * f
            x, y = nx, ny
    assert all(layers.values()), f"a window has no layers: {layers}"
    return ({k: round(used[k] * area / ((w[2] - w[0]) * (w[3] - w[1]) * LAYER * layers[k]), 3) for k, w in windows.items()}, layers)


def hhmm(seconds):
    return "%d:%02d" % divmod(round(seconds / 60), 60)


def slice_plate(path, tmp, p, geos, placement):
    """A real slice of plate p (1-indexed) through graft_slice: grams and time from slice_info.config, the settings that
    matter read back from the G-code, and the pads proven solid against a plain window of the same size in every hook,
    each hook's windows from its own variant's holes. The G-code of a plate is plate-local, so the windows drop the
    plate's world origin."""
    hooks = sorted((name for name, box in placement.items() if box["plate"] == p), key=lambda nm: placement[nm]["slot"])
    assert hooks, f"plate {p} is empty"
    by_variant = {v: [nm for nm in hooks if placement[nm]["variant"] == v] for v in geos if any(placement[nm]["variant"] == v for nm in hooks)}
    out = f"{tmp}/sliced-plate{p}.3mf"
    res = graft_slice(path, out, plate=p)
    log = open(res["log"]).read() if res.get("log") and os.path.exists(res["log"]) else ""
    complaints = [l for l in log.splitlines() if re.search(r"exceed|outside|out of|too large|not fit", l, re.I)]
    assert res.get("rc") == 0 and os.path.exists(out) and res.get("gcode"), f"plate {p} slice failed rc={res.get('rc')}: {complaints or log[-2000:]}"
    assert not complaints, f"plate {p}: the slicer complained: {complaints}"
    assert res["instances_added"] == 0, f"plate {p}: graft_slice had to add {res['instances_added']} model_instance entries"
    zs = zipfile.ZipFile(out)
    info = zs.read("Metadata/slice_info.config").decode()
    blk = [b for b in re.findall(r"<plate>(.*?)</plate>", info, re.S) if f'key="index" value="{p}"' in b]
    assert len(blk) == 1, f"plate {p}: slice_info.config has no plate block with index {p}"
    grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', blk[0]).group(1)
    fils = re.findall(r'<filament id="(\d+)"[^>]*/>', blk[0])
    assert fils == ["1"], f"plate {p}: filaments used {fils}, expected extruder 1 only"
    fil = re.search(r'<filament id="1"[^>]*/>', blk[0]).group(0)
    used_m, used_g = (float(re.search(rf'{k}="([^"]*)"', fil).group(1)) for k in ("used_m", "used_g"))
    seconds, grams = int(grab("prediction")), float(grab("weight"))

    gcode = zs.read(res["gcode"]).decode(errors="replace")
    assert "X2D start gcode" in gcode, f"plate {p}: the X2D start G-code is missing: the machine include templates did not merge"
    preset = flatten("filament", FILAMENT)
    temp, bed = preset["nozzle_temperature"][0], preset["textured_plate_temp"][0]
    assert re.search(rf"^\s*M10[49] S{temp}\b", gcode, re.M), f"plate {p}: nozzle temperature {temp} is not in the G-code"
    assert re.search(rf"^\s*M1[49]0 S{bed}\b", gcode, re.M), f"plate {p}: bed temperature {bed} is not in the G-code"
    assert re.search(r"^; filament_map = 1$", gcode, re.M), f"plate {p}: the G-code does not print from extruder 1"
    assert re.search(r"^; nozzle_diameter = 0\.6(,0\.6)*$", gcode, re.M), f"plate {p}: nozzle_diameter is not 0.6 in the G-code"
    for k in ("layer_height", "wall_loops", "sparse_infill_density", "sparse_infill_pattern", "skirt_loops", "skirt_distance",
              "skirt_height", "brim_type", "curr_bed_type"):
        v = SCALARS.get(k, f"{LAYER:g}")
        assert re.search(rf"^; {k} = {re.escape(v)}$", gcode, re.M), f"plate {p}: {k} = {v} is not in the sliced G-code"
    feature_mm, xy, z_top = gcode_stats(gcode)
    assert "Brim" not in feature_mm and "Skirt" in feature_mm, f"plate {p}: expected a skirt and no brim: {feature_mm}"
    assert xy[0] >= 0 and xy[1] >= 0 and xy[2] <= BED and xy[3] <= BED, f"plate {p}: toolpaths leave the bed: {xy}"
    tallest = max(geos[v]["H"] for v in by_variant)
    assert abs(z_top - tallest) <= LAYER + 1e-6, f"plate {p}: the sliced top is at z {z_top}, the hooks are {tallest} mm tall"

    # the pads: plastic per volume beside each hole (x within WIN_X of its centre, the core of the thickness, the layers
    # WIN_DZ below and above the hole's centre) against the same window at the height midway between the holes
    ox, oy = plate_origin(p)
    T, half = geos[next(iter(by_variant))]["T"], (WIN_DZ[1] - WIN_DZ[0]) / 2
    z_plain = {v: sum(hz for _, hz in geos[v]["holes"]) / len(geos[v]["holes"]) for v in by_variant}
    windows = {}
    for name in hooks:
        g = geos[placement[name]["variant"]]
        origin = np.array(placement[name]["min_mm"]) - g["stl_lo"] - [ox, oy, 0.0]      # the STL frame's origin on the plate's bed
        for pname, (hx, hz) in zip(PAD_NAMES, g["holes"]):
            xy_box = (origin[0] + hx - WIN_X, origin[1] + CORE_INSET, origin[0] + hx + WIN_X, origin[1] + T - CORE_INSET)
            windows[f"{name}/{pname}/below"] = (*xy_box, origin[2] + hz - WIN_DZ[1], origin[2] + hz - WIN_DZ[0])
            windows[f"{name}/{pname}/above"] = (*xy_box, origin[2] + hz + WIN_DZ[0], origin[2] + hz + WIN_DZ[1])
        hx, zp = g["holes"][0][0], z_plain[g["variant"]]
        windows[f"{name}/plain"] = (origin[0] + hx - WIN_X, origin[1] + CORE_INSET, origin[0] + hx + WIN_X, origin[1] + T - CORE_INSET,
                                    origin[2] + zp - half, origin[2] + zp + half)
    fill, n_layers = plastic_density(gcode, windows)
    pad_fill = {k: v for k, v in fill.items() if not k.endswith("/plain")}
    plain_fill = {k: v for k, v in fill.items() if k.endswith("/plain")}
    assert min(pad_fill.values()) >= 0.7, f"plate {p}: a screw pad is not solid: {fill}"
    assert max(plain_fill.values()) <= 0.4, f"plate {p}: a hook is not sparse between the pads, a modifier leaked: {fill}"
    assert min(pad_fill.values()) >= 3 * max(plain_fill.values()), f"plate {p}: pads barely denser than the plain hook: {fill}"
    return {"plate": p, "variants": {v: len(nms) for v, nms in by_variant.items()}, "hooks": hooks,
            "time": hhmm(seconds), "minutes": round(seconds / 60), "seconds": seconds,
            "gcode_estimate": res["time"], "grams": round(grams, 1), "metres": round(used_m, 2), "used_g_per_filament": round(used_g, 1),
            "grams_per_hook": round(grams / len(hooks), 1), "minutes_per_hook": round(seconds / 60 / len(hooks)),
            "layers": res["layers"], "top_z": z_top, "nozzle_C": int(temp), "bed_C": int(bed), "toolpath_xy_mm": xy,
            "feature_mm": feature_mm,
            "pad_fill": {"window": f"x within {WIN_X} mm of the hole, y {CORE_INSET} to {round(T - CORE_INSET, 3)} (the core between the walls), "
                                   f"layers {WIN_DZ[0]} to {WIN_DZ[1]} mm below and above the hole centre; plain: the same at z {z_plain} +/- {half}",
                         "layers_per_window": {k: n_layers[k] for k in list(n_layers)[:5]},
                         "pads_min": min(pad_fill.values()), "pads_max": max(pad_fill.values()),
                         "plain_min": min(plain_fill.values()), "plain_max": max(plain_fill.values()), "per_window": fill}}


def verify(path, tmp, geos):
    """Settings, placement and modifiers in the file, the same after a CLI round trip, then a real slice of every plate,
    one at a time. A round trip alone does not prove sliceability."""
    files, names, plates = check_settings(path, "authored file", geos)
    placement = check_placement(files, names, geos, "authored file")
    check_modifiers(files, names, geos, "authored file")
    n_obj = len(names)
    rows = {}
    for v, g in geos.items():
        ox, oy = plate_origin(g["plate"])
        mine = [b for b in placement.values() if b["variant"] == v]
        rows[v] = {"plate": g["plate"], "hooks": len(mine), "pitch_mm": round(g["T"] + GAP, 3),
                   "x_mm": [round(min(b["min_mm"][0] for b in mine) - ox, 2), round(max(b["max_mm"][0] for b in mine) - ox, 2)],
                   "y_mm": [round(min(b["min_mm"][1] for b in mine) - oy, 2), round(max(b["max_mm"][1] for b in mine) - oy, 2)]}
    result = {"plates": len(plates), "hooks_per_plate": [len(m) for _, m in plates], "rows_mm": rows, "placement_mm": placement}

    r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", path],
                       cwd=tmp, capture_output=True, text=True, timeout=600)
    assert os.path.exists(f"{tmp}/roundtrip.3mf"), f"round trip failed rc={r.returncode}\n{r.stdout[-1500:]}"
    rt_files, rt_names, rt_plates = check_settings(f"{tmp}/roundtrip.3mf", "CLI round trip", geos)
    members = lambda nm, pl: [sorted(k for k, v in nm.items() if v in m) for _, m in pl]   # by name: the CLI renumbers ids
    assert members(rt_names, rt_plates) == members(names, plates), f"the round trip changed the plates: {members(rt_names, rt_plates)}"
    check_placement(rt_files, rt_names, geos, "CLI round trip")
    check_modifiers(rt_files, rt_names, geos, "CLI round trip")
    result["roundtrip"] = (f"{len(rt_plates)} plates, {n_obj} objects with {2 * n_obj} modifier parts, overrides, "
                           f"different_settings_to_system, plate names and placement survive bambu-studio --arrange 0 --export-3mf")

    result["plates_sliced"] = [slice_plate(path, tmp, p, geos, placement) for p, _ in plates]
    secs = sum(pl["seconds"] for pl in result["plates_sliced"])
    grams = sum(pl["grams"] for pl in result["plates_sliced"])
    result.update({"total_time": hhmm(secs), "total_minutes": round(secs / 60), "total_grams": round(grams, 1),
                   "pad_fill_min": min(pl["pad_fill"]["pads_min"] for pl in result["plates_sliced"]),
                   "plain_fill_max": max(pl["pad_fill"]["plain_max"] for pl in result["plates_sliced"]),
                   "variants": {v: {"plate": g["plate"], "hooks": g["n"]} for v, g in geos.items()}})
    return result


# -------------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--copies", type=int, default=COPIES, help=f"hooks per variant (default {COPIES}, at most {GRID[0] * GRID[1]} on a plate)")
    ap.add_argument("--scratch", default=None, help="work dir for presets, STL copies, pads and the slices (default: a fresh temp dir)")
    args = ap.parse_args()
    n = args.copies
    assert 1 <= n <= GRID[0] * GRID[1], n

    os.environ["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{os.environ.get('PATH', '')}"   # bambu-studio is called by name
    if SCOPE_MARK not in os.environ and shutil.which("systemd-run"):
        probe = subprocess.run(SCOPE + ["true"], capture_output=True, text=True)
        if probe.returncode == 0:
            # Re-run this exact command inside the memory-capped scope; the CLAUDE.md rule for slicer batches.
            os.environ[SCOPE_MARK] = "1"
            os.execvp(SCOPE[0], SCOPE + [sys.executable] + sys.argv)
        print(f"warning: systemd-run scope unavailable ({probe.stderr.strip()}); slicing without a memory cap", file=sys.stderr)

    scratch = os.path.abspath(args.scratch) if args.scratch else tempfile.mkdtemp(prefix="rod-hook-3mf-")
    os.makedirs(scratch, exist_ok=True)
    final = f"{PROJECT}/{OUT}"
    write_presets(scratch)
    geos = {v: hook_geometry(v, p, n) for v, p in PLATES.items()}
    copies = []
    for g in geos.values():
        for i in range(1, n + 1):
            copies.append(f"{label(g['stem'], i)}.stl")
            shutil.copy(f"{PROJECT}/{g['stem']}.stl", f"{scratch}/{copies[-1]}")
    # --export-3mf must be a bare filename; an absolute path alongside --outputdir makes the CLI exit 243 without writing.
    # --arrange 1 makes the CLI write plate blocks with a model_instance per object; its plates and transforms are rewritten in author().
    cmd = ["bambu-studio", "--arrange", "1", "--load-settings", "machine.json;process.json", "--load-filaments", "filament.json",
           "--export-3mf", "raw.3mf", "--outputdir", ".", *copies]
    r = subprocess.run(cmd, cwd=scratch, capture_output=True, text=True, timeout=600)
    assert os.path.exists(f"{scratch}/raw.3mf"), f"CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"

    pads, proof = {}, {}
    for v, g in geos.items():
        pads[v], proof[v] = build_pads(scratch, g)
    cli_plates = author(f"{scratch}/raw.3mf", final, geos)
    n_mods = add_screw_pads(final, pads, geos)
    T = next(iter(geos.values()))["T"]
    result = {"file": final, "copies": n, "copies_are": "per variant", "objects": len(copies), "command": " ".join(cmd) + f"   (cwd {scratch})",
              "cli_arranged_plates": cli_plates, "plates_authored": {v: g["plate"] for v, g in geos.items()},
              "presets": {"machine": MACHINE, "process": PROCESS, "filament": FILAMENT}, "overrides": SCALARS,
              "filament_colour": FILAMENT_COLOUR, "row_pitch_mm": round(T + GAP, 3), "gap_mm": GAP, "plate_stride_mm": PLATE_STRIDE,
              "screw_pads": {"per_hook": len(PAD_NAMES), "total": n_mods, "axis": "y, through the thickness", "diameter_mm": PAD_D,
                             "span_y_mm": [PAD_INSET, round(T - PAD_INSET, 4)], "hole_clearance_mm": HOLE_CLEAR,
                             "keys": PAD_KEYS, "pads": pads, "proof_vs_stl": proof},
              "note": NOTE}
    result.update(verify(final, scratch, geos))
    with open(f"{PROJECT}/{REPORT}", "w") as f:
        json.dump(result, f, indent=1)
    print(final)
    print(json.dumps({k: v for k, v in result.items() if k not in ("placement_mm", "plates_sliced", "screw_pads")}, indent=1))
    for pl in result["plates_sliced"]:
        kinds = ", ".join(f"{k} {v}" for v, k in pl["variants"].items())
        print(f"plate {pl['plate']} ({kinds}): {len(pl['hooks'])} hooks: {pl['grams']} g, {pl['time']} ({pl['minutes']} min), "
              f"pads {pl['pad_fill']['pads_min']}..{pl['pad_fill']['pads_max']} vs plain {pl['pad_fill']['plain_min']}..{pl['pad_fill']['plain_max']}")
    print(f"total {result['total_grams']} g, {result['total_time']} ({result['total_minutes']} min); report {PROJECT}/{REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
