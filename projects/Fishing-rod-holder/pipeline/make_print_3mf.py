#!/usr/bin/env python3
"""Bambu Studio print 3MF for the rod hook: ONE project file, N copies (default 8) of rod-hook.stl, four to a plate,
every copy with its own two 100% infill modifier pads at the screw holes, verified by a real slice of every plate.

    .venv/bin/python projects/Fishing-rod-holder/pipeline/make_print_3mf.py [--copies 8] [--scratch DIR]

Writes rod-hook.3mf and rod-hook-3mf-report.json beside the STL. Plumbing only: the STL is not touched.

The recipe is the vault's (memory/feedback-stl-to-bambu-3mf.md), not a new one:
  presets     the include-merging flattener of projects/Cable-bin/pipeline/make_print_3mf.py over the installed BBL bundle;
              machine "Bambu Lab X2D 0.6 nozzle", process "0.30mm Standard @BBL X2D 0.6 nozzle", "Bambu PETG Basic @BBL X2D"
              (the three slice_stls.py quotes with). The overrides are written into the flattened process copy before the
              export AND into the 3MF's project_settings plus different_settings_to_system[0], or Studio's GUI resets them
  export      bambu-studio --arrange 1 ... --export-3mf raw.3mf rod-hook-1.stl ... rod-hook-N.stl: one object per copy (a
              modifier belongs to an object, instances would share one). The CLI opens a new plate every four hooks by
              itself (measured 2026-11-07: two plates of four, unrotated, but packed 2 mm apart), so its plate blocks and
              plate assignment are kept and only the item transforms are rewritten
  placement   every item transform is written here from the file's own geometry, a 2 x 2 grid per plate, GAP apart,
              centred on the bed (the Cable-bin pattern: the arranger is not trusted)
  screw pads  projects/Skateboard-wall-holder/pipeline/make_print_3mf.py's modifier parts through the Sharks helpers
              (fillcore_mod.inject_modifier): per copy two cylinders PAD_D across, PAD_INSET under the back and front
              faces, the screw hole and its countersink cleared by HOLE_CLEAR, sparse_infill_density 100%. Proven wholly
              inside the body twice, build123d against the CAD and OpenSCAD against the STL
              (memory/feedback-modifiers-inside-the-body.md), then proven solid in the sliced G-code by plastic per volume
              against a plain window of the same size (knowledge/learnings/nacs-wall-holder.md)
  slice       the CLI cannot slice its own export (rc 156), so projects/Sharks-nametag/pipeline/graft_slice.py adds the
              GUI-only keys to a throwaway copy; one plate at a time, the whole run re-executed inside the memory-capped
              systemd scope (CLAUDE.md, heavy local jobs)
Opening rod-hook.3mf in Bambu Studio is still the ground truth for the plates and for how the modifiers look.
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

STEM = "rod-hook"
OUT = f"{STEM}.3mf"
REPORT = f"{STEM}-3mf-report.json"
COPIES = 8
LAYER = 0.3
BED = 256.0
BED_CENTRE = (128.0, 128.0)
BED_TYPE = "Textured PEI Plate"
PLATE_STRIDE = BED * 1.2         # 307.2: Studio's plate grid, two columns, rows in negative Y (knowledge/printer-x2d.md)
PLATE_COLS = 2
GRID = (2, 2)                    # hooks per plate: columns along x, rows along y
GAP = 20.0                       # between neighbouring hooks (the arranger's 2 mm leaves no room for the skirts)

PAD_D = 22.0                     # solid infill this wide around each screw hole
PAD_INSET = 0.2                  # the pad stops this far inside the back and front faces
HOLE_CLEAR = 0.6                 # the hole and countersink are cleared by one 0.6 line, so nothing shows through the hole in Studio
PAD_NAMES = ("pad-bottom", "pad-top")      # by the hook's own y: the lower screw, the upper screw
PAD_KEYS = {"sparse_infill_density": "100%"}
WIN = 6.0                        # G-code density window, mm square
WIN_DX = 7.0                     # window centre this far from the hole centre toward the tab's edge: off the hole's walls, inside the pad
BAND = 1.5                       # layers within this of the hook's mid-height

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
def hook_geometry():
    """The hook's constants and CAD from rod_hook.py (the STL is exported in that same frame): thickness, the hole
    centres (lower screw first), hole and countersink diameters, and the CAD solid."""
    import rod_hook as M
    holes = sorted(((M.SCREW_X * M.IN, y * M.IN) for y in M.SCREW_Y), key=lambda h: h[1])
    return {"T": M.T * M.IN, "holes": holes, "hole_d": M.HOLE_D, "csk_d": M.CSK_D, "cad": M.build_hook()}


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
    """One pad per screw hole: a PAD_D cylinder from PAD_INSET over the back face to PAD_INSET under the front face,
    the hole and its 90 degree countersink cleared by HOLE_CLEAR. Each is proven wholly inside the CAD body (volume
    outside 0), exported to STL, and the pair is proven again against rod-hook.stl with OpenSCAD."""
    from build123d import Cone, Cylinder, Pos, export_stl
    T, hook = geo["T"], geo["cad"]
    pads = []
    for name, (hx, hy) in zip(PAD_NAMES, geo["holes"]):
        pad = Pos(hx, hy, T / 2) * Cylinder(PAD_D / 2, T - 2 * PAD_INSET)
        pad -= Pos(hx, hy, T / 2) * Cylinder(geo["hole_d"] / 2 + HOLE_CLEAR, T + 2)
        # rod_hook.py's countersink is a 90 degree cone with its apex csk_d / 2 under the front face; the same cone pushed
        # HOLE_CLEAR along its surface normal has its apex HOLE_CLEAR * sqrt(2) lower
        apex = T - geo["csk_d"] / 2 - HOLE_CLEAR * math.sqrt(2)
        h = T - apex + 1.0
        pad -= Pos(hx, hy, apex + h / 2) * Cone(0.0, h, h)
        inside = (pad & hook).volume
        outside = pad.volume - inside
        assert abs(outside) < 1e-3, f"{name}: {outside:.4f} mm3 of the pad lies outside the CAD body"
        path = f"{d}/{name}.stl"
        export_stl(pad, path)
        m = trimesh.load(path)
        assert m.is_watertight and len(m.split()) == 1, f"{name}: the pad mesh is not one closed body"
        lo, hi = m.bounds
        assert abs(lo[2] - PAD_INSET) < 1e-3 and abs(hi[2] - (T - PAD_INSET)) < 1e-3, m.bounds
        assert np.allclose((lo + hi) / 2, [hx, hy, T / 2], atol=0.02), m.bounds
        pads.append({"name": name, "path": path, "centre_stl_mm": [round(hx, 3), round(hy, 3), round(T / 2, 4)],
                     "volume_mm3": round(float(m.volume), 1), "outside_cad_mm3": round(float(abs(outside)), 6)})
    body = f"{PROJECT}/{STEM}.stl"
    both = " ".join(f'import("{p["path"]}");' for p in pads)
    outside = scad_volume(f'difference() {{ union() {{ {both} }} import("{body}"); }}', f"{d}/pads-outside.stl")
    inside = scad_volume(f'intersection() {{ union() {{ {both} }} import("{body}"); }}', f"{d}/pads-inside.stl")
    total = sum(p["volume_mm3"] for p in pads)
    assert outside < 1e-3, f"{outside:.3f} mm3 of the pads lie outside rod-hook.stl"
    assert abs(inside - total) < 0.002 * total, f"pads inside the STL {inside:.1f} mm3 vs the pads' {total:.1f} mm3: an import failed"
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


def world_components(files):
    """{object id: [(sub id, lo, hi), ...]}: every component of every build item in world mm, from the meshes and
    transforms in the 3MF itself (item transform x component transform x the mesh's own coordinates)."""
    main = files["3D/3dmodel.model"].decode()
    comps = {oid: re.findall(r'<component p:path="([^"]+)" objectid="(\d+)"(?: [^>]*?transform="([^"]*)")?', body)
             for oid, body in re.findall(r'<object id="(\d+)"[^>]*>(.*?)</object>', main, re.S)}
    out = {}
    for oid, tr in re.findall(r'<item objectid="(\d+)"[^>]*?transform="([^"]*)"', main):
        parts = []
        for path, sub_id, comp_t in comps[oid]:
            sub = files[path.lstrip("/")].decode()
            mesh = re.search(rf'<object id="{sub_id}"[^>]*>(.*?)</object>', sub, re.S).group(1)
            v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', mesh), dtype=float)
            w = (matrix(tr) @ matrix(comp_t) @ np.c_[v, np.ones(len(v))].T).T[:, :3]
            parts.append((sub_id, w.min(axis=0), w.max(axis=0)))
        out[oid] = parts
    return out


def world_bounds(files):
    """{object id: (lo, hi)} over all of an object's components."""
    return {oid: (np.min([lo for _, lo, _ in parts], axis=0), np.max([hi for _, _, hi in parts], axis=0))
            for oid, parts in world_components(files).items()}


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


def hook_number(name):
    return int(re.search(r"-(\d+)(?:\.stl)?$", name).group(1))


def label(i):
    return f"{STEM}-{i}"


def plate_name(numbers):
    n = sorted(numbers)
    return f"Hooks {n[0]}-{n[-1]}" if n == list(range(n[0], n[-1] + 1)) else "Hooks " + ", ".join(map(str, n))


def plate_origin(p):
    """Bed origin of plate p, 0-indexed, in the 3MF's world frame."""
    return (p % PLATE_COLS) * PLATE_STRIDE, -(p // PLATE_COLS) * PLATE_STRIDE


def slot_centre(slot, ext):
    """Plate-local bed (x, y) of the footprint centre of grid slot `slot`: columns along x, rows from the back."""
    col, row = slot % GRID[0], slot // GRID[0]
    return (BED_CENTRE[0] + (col - (GRID[0] - 1) / 2) * (ext[0] + GAP),
            BED_CENTRE[1] + ((GRID[1] - 1) / 2 - row) * (ext[1] + GAP))


def expected_targets(names, plates, ext):
    """{object id: (plate 0-indexed, slot, bed x, bed y)} from the plate membership and the hooks' numbers."""
    by_id = {oid: name for name, oid in names.items()}
    out = {}
    for p, (_, members) in enumerate(plates):
        assert len(members) <= GRID[0] * GRID[1], f"plate {p + 1} carries {len(members)} hooks, the {GRID[0]} x {GRID[1]} grid holds {GRID[0] * GRID[1]}"
        for slot, oid in enumerate(sorted(members, key=lambda o: hook_number(by_id[o]))):
            out[oid] = (p, slot, *slot_centre(slot, ext))
    return out


# ------------------------------------------------------------------------------------------------------------ author
def author(src, dst, n):
    """Keep the CLI's plates, re-place every copy in its plate's grid, name the objects and plates, apply the overrides,
    pin the filament to extruder 1, colour it."""
    entries = read_all(src)
    files = {i.filename: data for i, data in entries}
    model = files["3D/3dmodel.model"].decode()
    msc = files["Metadata/model_settings.config"].decode()
    names = object_names(msc)
    assert set(names) == {f"{label(i)}.stl" for i in range(1, n + 1)}, f"objects in the export: {sorted(names)}"
    plates = plate_members(msc)
    assert [pid for pid, _ in plates] == list(range(1, len(plates) + 1)), plates
    assert sorted(o for _, m in plates for o in m) == sorted(names.values()), "every object must sit on exactly one plate"
    ext = trimesh.load(f"{PROJECT}/{STEM}.stl").extents
    targets = expected_targets(names, plates, ext)

    # item transforms: identity rotation, translation chosen so the object's own bounds land on target with floor on z 0
    bounds = world_bounds(files)
    def move(m):
        oid = re.search(r'objectid="(\d+)"', m.group(1)).group(1)
        p, _, cx, cy = targets[oid]
        ox, oy = plate_origin(p)
        lo, hi = bounds[oid]
        t = [float(v) for v in m.group(2).split()]
        assert np.allclose(t[:9], [1, 0, 0, 0, 1, 0, 0, 0, 1]), f"the export rotated object {oid}: {t[:9]}"
        shift = (ox + cx - (lo[0] + hi[0]) / 2, oy + cy - (lo[1] + hi[1]) / 2, -lo[2])
        return m.group(1) + 'transform="1 0 0 0 1 0 0 0 1 %.6g %.6g %.6g"' % tuple(t[9 + i] + shift[i] for i in range(3))
    model, moved = re.subn(r'(<item [^>]*?)transform="([^"]*)"', move, model)
    assert moved == n, (moved, n)

    for src_name in names:
        msc = msc.replace(f'key="name" value="{src_name}"', f'key="name" value="{src_name[:-4]}"')
    msc = msc.replace('key="filament_map_mode" value="Auto For Flush"', 'key="filament_map_mode" value="Manual"')
    by_id = {oid: name for name, oid in names.items()}
    pnames = {pid: plate_name([hook_number(by_id[o]) for o in members]) for pid, members in plates}
    def rename_plate(m):
        pid = int(re.search(r'<metadata key="plater_id" value="(\d+)"/>', m.group(0)).group(1))
        return m.group(0).replace('key="plater_name" value=""', f'key="plater_name" value="{pnames[pid]}"')
    msc = re.sub(r"<plate>.*?</plate>", rename_plate, msc, flags=re.S)

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
                             "Metadata/project_settings.config": json.dumps(cfg, indent=4).encode()})


def add_screw_pads(path, pads):
    """Two modifier parts per object, sparse_infill_density 100%: each pad mesh stored centred the way the CLI stores
    parts and placed in the object's frame where the STL frame puts it (the object's first component transform minus
    the stored body mesh's centre tells where the STL origin sits in that frame)."""
    entries = read_all(path)
    files = {i.filename: data for i, data in entries}
    model3d = files["3D/3dmodel.model"].decode()
    objfiles = {n: files[n].decode() for n in files if n.startswith("3D/Objects/")}
    settings = files["Metadata/model_settings.config"].decode()
    stl_c = trimesh.load(f"{PROJECT}/{STEM}.stl").bounds.mean(axis=0)
    meshes = [(p["name"], *centered(trimesh.load(p["path"]))) for p in pads]
    oids = re.findall(r'<object id="(\d+)">', settings)
    for oid in oids:
        block = re.search(rf'<object id="{oid}">.*?</object>', settings, re.S).group(0)
        comp = re.search(rf'<object id="{oid}" [^>]*>\s*<components>\s*<component p:path="([^"]+)" objectid="(\d+)"', model3d, re.S)
        body = re.search(rf'<object id="{comp.group(2)}"[^>]*>(.*?)</object>', objfiles[comp.group(1).lstrip("/")], re.S).group(1)
        v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', body), dtype=float)
        stored_c = (v.min(axis=0) + v.max(axis=0)) / 2
        pos = object_pos(model3d, oid, stl_c - stored_c)
        new_block = block
        for name, mesh_c, mc in meshes:
            pid = next_object_id(model3d, objfiles)
            new_block, model3d = inject_modifier(new_block, model3d, objfiles, oid, pid, name, f"{name}.stl", mesh_c, mc, pos, PAD_KEYS)
        settings = settings.replace(block, new_block)
    replace = {n: val.encode() for n, val in objfiles.items()}
    replace["3D/3dmodel.model"] = model3d.encode()
    replace["Metadata/model_settings.config"] = settings.encode()
    write_all(path, entries, replace)
    return len(oids) * len(meshes)


# ------------------------------------------------------------------------------------------------------------ checks
def check_settings(path, what, n):
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
    assert set(names) == {label(i) for i in range(1, n + 1)}, f"{what}: object names {sorted(names)}"
    plates = plate_members(msc)
    assert [pid for pid, _ in plates] == list(range(1, len(plates) + 1)), f"{what}: plate ids {[pid for pid, _ in plates]}"
    assert sorted(o for _, m in plates for o in m) == sorted(names.values()), f"{what}: objects and plate membership disagree"
    for blk in re.findall(r"<plate>(.*?)</plate>", msc, re.S):
        assert 'key="filament_map_mode" value="Manual"' in blk, f"{what}: a plate block is not in Manual filament map mode"
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


def check_placement(files, names, plates, ext, what):
    """Every hook unrotated, floor on z 0, footprint centred on its grid slot inside its plate's cell, neighbours exactly
    GAP apart, by the 3MF's own geometry. Returns the per-hook world boxes."""
    comps = world_components(files)
    targets = expected_targets(names, plates, ext)
    by_id = {oid: name for name, oid in names.items()}
    assert set(comps) == set(by_id), f"{what}: build items {sorted(comps)} vs objects {sorted(by_id)}"
    result, boxes = {}, {}
    for oid, parts in comps.items():
        body = [c for c in parts if np.allclose(c[2] - c[1], ext, atol=0.01)]
        assert len(body) == 1, f"{what}: {by_id[oid]} has no component with the STL's extents {ext}: rotated?"
        lo, hi = body[0][1], body[0][2]
        p, slot, cx, cy = targets[oid]
        ox, oy = plate_origin(p)
        assert abs((lo[0] + hi[0]) / 2 - (ox + cx)) < 0.01 and abs((lo[1] + hi[1]) / 2 - (oy + cy)) < 0.01, f"{what}: {by_id[oid]} not at {(ox + cx, oy + cy)}: {lo} {hi}"
        assert abs(lo[2]) < 0.01, f"{what}: {by_id[oid]} floor at z {lo[2]:.3f}"
        assert lo[0] >= ox + 5 and lo[1] >= oy + 5 and hi[0] <= ox + BED - 5 and hi[1] <= oy + BED - 5, f"{what}: {by_id[oid]} within 5 mm of plate {p + 1}'s edge: {lo} {hi}"
        boxes[(p, slot)] = (lo, hi)
        result[by_id[oid]] = {"plate": p + 1, "slot": slot, "min_mm": [round(float(v), 2) for v in lo], "max_mm": [round(float(v), 2) for v in hi]}
    for (p, slot), (lo, hi) in boxes.items():
        if slot % GRID[0] != GRID[0] - 1 and (p, slot + 1) in boxes:
            got = boxes[(p, slot + 1)][0][0] - hi[0]
            assert abs(got - GAP) < 0.01, f"{what}: plate {p + 1} slots {slot} and {slot + 1} are {got:.2f} mm apart in x, expected {GAP}"
        if (p, slot + GRID[0]) in boxes:
            got = lo[1] - boxes[(p, slot + GRID[0])][1][1]
            assert abs(got - GAP) < 0.01, f"{what}: plate {p + 1} slots {slot} and {slot + GRID[0]} are {got:.2f} mm apart in y, expected {GAP}"
    return result


def check_modifiers(files, names, geo, ext, what):
    """Every object carries exactly two extra components whose world boxes are the two pads: centred on the hook's screw
    holes, PAD_D square, PAD_INSET inside the body's back and front faces and well inside its outline (the 3MF's own geometry)."""
    comps = world_components(files)
    stl_lo = trimesh.load(f"{PROJECT}/{STEM}.stl").bounds[0]
    T = geo["T"]
    for name, oid in names.items():
        parts = comps[oid]
        body = [c for c in parts if np.allclose(c[2] - c[1], ext, atol=0.01)]
        pads = [c for c in parts if not np.allclose(c[2] - c[1], ext, atol=0.01)]
        assert len(body) == 1 and len(pads) == len(PAD_NAMES), f"{what}: {name} has {len(parts)} components"
        blo, bhi = body[0][1], body[0][2]
        origin = blo - stl_lo
        for pname, (hx, hy) in zip(PAD_NAMES, geo["holes"]):
            want = origin + [hx, hy, T / 2]
            hit = [c for c in pads if np.allclose((c[1] + c[2]) / 2, want, atol=0.05)]
            assert len(hit) == 1, f"{what}: {name}: no modifier centred on its {pname} hole at {want}"
            lo, hi = hit[0][1], hit[0][2]
            assert np.allclose(hi - lo, [PAD_D, PAD_D, T - 2 * PAD_INSET], atol=0.1), f"{what}: {name} {pname} box {hi - lo}"
            assert lo[2] >= blo[2] + PAD_INSET - 1e-3 and hi[2] <= bhi[2] - PAD_INSET + 1e-3, f"{what}: {name} {pname} reaches a face: z {lo[2]:.3f}..{hi[2]:.3f}"
            assert (lo[:2] >= blo[:2] + 1).all() and (hi[:2] <= bhi[:2] - 1).all(), f"{what}: {name} {pname} reaches the outline"


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


def plastic_density(gcode, windows, z_lo, z_hi):
    """Plastic per volume (mm3 of filament per mm3 of window) in each (x0, y0, x1, y1) window over the layers whose
    height lies in [z_lo, z_hi]. Every extrusion move (G1, and G2/G3 as its chord) is clipped to the window and its E
    split by the clipped fraction: midpoint tests fail on long solid lines (knowledge/learnings/nacs-wall-holder.md)."""
    assert re.search(r"^; use_relative_e_distances = 1$", gcode, re.M), "E is not relative, the per-move E sums are meaningless"
    area = math.pi * (1.75 / 2) ** 2
    used, layers = {k: 0.0 for k in windows}, set()
    z, x, y, inband = 0.0, 0.0, 0.0, False
    for line in gcode.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":")[1])
            inband = z_lo <= z <= z_hi
            if inband:
                layers.add(round(z, 3))
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            mx, my, me = re.search(r" X([-0-9.]+)", line), re.search(r" Y([-0-9.]+)", line), re.search(r" E([-0-9.]+)", line)
            nx, ny = (float(mx.group(1)) if mx else x), (float(my.group(1)) if my else y)
            if inband and me and float(me.group(1)) > 0 and (mx or my):
                e = float(me.group(1))
                for k, w in windows.items():
                    f = clip_fraction(x, y, nx, ny, w)
                    if f:
                        used[k] += e * f
            x, y = nx, ny
    assert layers, f"no layers between z {z_lo} and {z_hi}"
    return {k: round(used[k] * area / ((w[2] - w[0]) * (w[3] - w[1]) * LAYER * len(layers)), 3) for k, w in windows.items()}, len(layers)


def hhmm(seconds):
    return "%d:%02d" % divmod(round(seconds / 60), 60)


def slice_plate(path, tmp, p, geo, ext, placement):
    """A real slice of plate p (1-indexed) through graft_slice: grams and time from slice_info.config, the settings that
    matter read back from the G-code, and the pads proven solid against a plain window of the same size in every hook."""
    hooks = sorted((name for name, box in placement.items() if box["plate"] == p), key=hook_number)
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
    assert abs(z_top - geo["T"]) <= LAYER + 1e-6, f"plate {p}: the sliced top is at z {z_top}, the hook is {geo['T']} mm"

    # the pads: plastic per volume in a WIN square beside each screw hole (inside the pad, off the hole's walls) against
    # the same square midway between the screws, over the layers within BAND of mid-height; G-code is plate-local
    ox, oy = plate_origin(p - 1)
    stl_lo = trimesh.load(f"{PROJECT}/{STEM}.stl").bounds[0]
    windows = {}
    for name in hooks:
        origin = np.array(placement[name]["min_mm"]) - stl_lo          # the STL frame's origin on the bed
        for pname, (hx, hy) in zip(PAD_NAMES, geo["holes"]):
            cx, cy = origin[0] + hx + WIN_DX - ox, origin[1] + hy - oy
            windows[f"{name}/{pname}"] = (cx - WIN / 2, cy - WIN / 2, cx + WIN / 2, cy + WIN / 2)
        cx, cy = origin[0] + geo["holes"][0][0] - ox, origin[1] + (geo["holes"][0][1] + geo["holes"][1][1]) / 2 - oy
        windows[f"{name}/plain"] = (cx - WIN / 2, cy - WIN / 2, cx + WIN / 2, cy + WIN / 2)
    fill, n_layers = plastic_density(gcode, windows, geo["T"] / 2 - BAND, geo["T"] / 2 + BAND)
    pad_fill = {k: v for k, v in fill.items() if not k.endswith("/plain")}
    plain_fill = {k: v for k, v in fill.items() if k.endswith("/plain")}
    assert min(pad_fill.values()) >= 0.7, f"plate {p}: a screw pad is not solid: {fill}"
    assert max(plain_fill.values()) <= 0.4, f"plate {p}: a hook is not sparse between the pads, a modifier leaked: {fill}"
    assert min(pad_fill.values()) >= 3 * max(plain_fill.values()), f"plate {p}: pads barely denser than the plain hook: {fill}"
    return {"plate": p, "hooks": hooks, "time": hhmm(seconds), "minutes": round(seconds / 60), "seconds": seconds,
            "gcode_estimate": res["time"], "grams": round(grams, 1), "metres": round(used_m, 2), "used_g_per_filament": round(used_g, 1),
            "layers": res["layers"], "top_z": z_top, "nozzle_C": int(temp), "bed_C": int(bed), "toolpath_xy_mm": xy,
            "feature_mm": feature_mm,
            "pad_fill": {"window_mm": WIN, "layers": n_layers, "z_band": [round(geo["T"] / 2 - BAND, 3), round(geo["T"] / 2 + BAND, 3)],
                         "pads_min": min(pad_fill.values()), "pads_max": max(pad_fill.values()),
                         "plain_min": min(plain_fill.values()), "plain_max": max(plain_fill.values()), "per_window": fill}}


def verify(path, tmp, geo, n):
    """Settings, placement and modifiers in the file, the same after a CLI round trip, then a real slice of every plate,
    one at a time. A round trip alone does not prove sliceability."""
    ext = trimesh.load(f"{PROJECT}/{STEM}.stl").extents
    files, names, plates = check_settings(path, "authored file", n)
    placement = check_placement(files, names, plates, ext, "authored file")
    check_modifiers(files, names, geo, ext, "authored file")
    result = {"plates": len(plates), "hooks_per_plate": [len(m) for _, m in plates], "placement_mm": placement}

    r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", path],
                       cwd=tmp, capture_output=True, text=True, timeout=600)
    assert os.path.exists(f"{tmp}/roundtrip.3mf"), f"round trip failed rc={r.returncode}\n{r.stdout[-1500:]}"
    rt_files, rt_names, rt_plates = check_settings(f"{tmp}/roundtrip.3mf", "CLI round trip", n)
    members = lambda nm, pl: [sorted(k for k, v in nm.items() if v in m) for _, m in pl]   # by name: the CLI renumbers ids
    assert members(rt_names, rt_plates) == members(names, plates), f"the round trip changed the plates: {members(rt_names, rt_plates)}"
    check_placement(rt_files, rt_names, rt_plates, ext, "CLI round trip")
    check_modifiers(rt_files, rt_names, geo, ext, "CLI round trip")
    result["roundtrip"] = (f"{len(rt_plates)} plates, {n} objects with {2 * n} modifier parts, overrides, "
                           f"different_settings_to_system and placement survive bambu-studio --arrange 0 --export-3mf")

    result["plates_sliced"] = [slice_plate(path, tmp, p, geo, ext, placement) for p in range(1, len(plates) + 1)]
    secs = sum(pl["seconds"] for pl in result["plates_sliced"])
    grams = sum(pl["grams"] for pl in result["plates_sliced"])
    result.update({"total_time": hhmm(secs), "total_minutes": round(secs / 60), "total_grams": round(grams, 1),
                   "pad_fill_min": min(pl["pad_fill"]["pads_min"] for pl in result["plates_sliced"]),
                   "plain_fill_max": max(pl["pad_fill"]["plain_max"] for pl in result["plates_sliced"])})
    return result


# -------------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--copies", type=int, default=COPIES, help="how many hooks (default 8)")
    ap.add_argument("--scratch", default=None, help="work dir for presets, STL copies, pads and the slices (default: a fresh temp dir)")
    args = ap.parse_args()
    n = args.copies
    assert n >= 1, n

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
    copies = [f"{label(i)}.stl" for i in range(1, n + 1)]
    for c in copies:
        shutil.copy(f"{PROJECT}/{STEM}.stl", f"{scratch}/{c}")
    # --export-3mf must be a bare filename; an absolute path alongside --outputdir makes the CLI exit 243 without writing.
    # --arrange 1 makes the CLI open plates and write their blocks; its transforms are overwritten in author().
    cmd = ["bambu-studio", "--arrange", "1", "--load-settings", "machine.json;process.json", "--load-filaments", "filament.json",
           "--export-3mf", "raw.3mf", "--outputdir", ".", *copies]
    r = subprocess.run(cmd, cwd=scratch, capture_output=True, text=True, timeout=600)
    assert os.path.exists(f"{scratch}/raw.3mf"), f"CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"

    geo = hook_geometry()
    pads, mesh_proof = build_pads(scratch, geo)
    author(f"{scratch}/raw.3mf", final, n)
    n_mods = add_screw_pads(final, pads)
    result = {"file": final, "copies": n, "command": " ".join(cmd) + f"   (cwd {scratch})",
              "presets": {"machine": MACHINE, "process": PROCESS, "filament": FILAMENT}, "overrides": SCALARS,
              "filament_colour": FILAMENT_COLOUR,
              "screw_pads": {"per_hook": len(pads), "total": n_mods, "diameter_mm": PAD_D, "z_mm": [PAD_INSET, round(geo["T"] - PAD_INSET, 4)],
                             "hole_clearance_mm": HOLE_CLEAR, "keys": PAD_KEYS, "pads": pads, "proof_vs_stl": mesh_proof}}
    result.update(verify(final, scratch, geo, n))
    with open(f"{PROJECT}/{REPORT}", "w") as f:
        json.dump(result, f, indent=1)
    print(final)
    print(json.dumps({k: v for k, v in result.items() if k not in ("placement_mm", "plates_sliced")}, indent=1))
    for pl in result["plates_sliced"]:
        print(f"plate {pl['plate']}: {', '.join(pl['hooks'])}: {pl['grams']} g, {pl['time']} ({pl['minutes']} min), "
              f"pads {pl['pad_fill']['pads_min']}..{pl['pad_fill']['pads_max']} vs plain {pl['pad_fill']['plain_min']}..{pl['pad_fill']['plain_max']}")
    print(f"total {result['total_grams']} g, {result['total_time']} ({result['total_minutes']} min); report {PROJECT}/{REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
