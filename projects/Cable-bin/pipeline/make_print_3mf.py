"""Bambu Studio print 3MF for the cable bin: ONE project file, TWO plates, each verified by a real slice.

  plate 1 "Bin"           cable-bin-half-a.stl and cable-bin-half-b.stl, side by side along Y, 15 mm apart, centred
  plate 2 "Joint coupon"  cable-bin-coupon-a.stl and cable-bin-coupon-b.stl, side by side along X, 20 mm apart, centred

Copied from projects/Skateboard-wall-holder/pipeline/make_print_3mf.py (X2D 0.6 nozzle, 0.30mm Standard, Bambu PETG
Basic, Textured PEI, include-merging preset flattener, graft_slice for the verification slice, wall_loops 3, 20% gyroid,
skirt and no brim, the PETG seam and top settings) with:
  several objects      the PARTS pattern of projects/Build123d-trial/pipeline/make_print_3mf.py: objects are matched by
                       the source filename carried in Metadata/model_settings.config, never by position, and every item
                       transform is written here from the file's own geometry (the arranger is not trusted)
  two plates           projects/Garmin-943-helm-panel/make_multiplate.py and knowledge/printer-x2d.md: plate p (0-indexed)
                       sits at ((p % 2) * 307.2, -(p // 2) * 307.2); one <plate> block per plate with a <model_instance>
                       per object; each build item's transform carries its plate's offset
  skirt per project    skirt_per_object 0 (the preset's 1 would draw a skirt around each half), skirt 2 / 3 mm / 1 layer
  bed temps            filament-scope keys live in the filament diff slot (different_settings_to_system[1]), as the
                       Build123d-trial script does; process keys in slot 0
STLs are already in print orientation with their floor on z 0; nothing here rotates them.

Usage:  .venv/bin/python projects/Cable-bin/pipeline/make_print_3mf.py
Reads the four STLs; writes cable-bin.3mf and cable-bin-slice.json beside them. The slices run one at a time.
Opening cable-bin.3mf in Bambu Studio is still the ground truth for the plates: a hand-authored plate has passed a CLI
round trip before and rendered empty in the GUI.
"""
import json
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
sys.path.insert(0, os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline"))
from graft_slice import graft_slice  # noqa: E402

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")   # the 02.08.00.06 bundle of the installed 02.08.02.61 Studio

MACHINE = "Bambu Lab X2D 0.6 nozzle"
PROCESS = "0.30mm Standard @BBL X2D 0.6 nozzle"
FILAMENT = "Bambu PETG Basic @BBL X2D"
FILAMENT_COLOUR = "#000000"      # display only; any PETG Basic slot in the AMS prints it

STEM = "cable-bin"
OUT = f"{STEM}.3mf"
BED = 256.0
BED_CENTRE = (128.0, 128.0)
BED_TYPE = "Textured PEI Plate"
PLATE_STRIDE = BED * 1.2         # 307.2: Studio's plate grid, two columns, rows in negative Y
PLATE_COLS = 2
LAYER = 0.3

# plate name, axis the parts line up along, gap between neighbours (mm), [(source stl, object name), ...]
PLATES = [
    ("Bin", "y", 15.0, [("cable-bin-half-a.stl", "Half A (tails)"), ("cable-bin-half-b.stl", "Half B (sockets)")]),
    ("Joint coupon", "x", 20.0, [("cable-bin-coupon-a.stl", "Coupon A"), ("cable-bin-coupon-b.stl", "Coupon B")]),
]
PARTS = {stl: label for _, _, _, items in PLATES for stl, label in items}

SCALARS = {   # process scope, different_settings_to_system[0]
    "curr_bed_type": BED_TYPE,
    "brim_type": "no_brim",
    "skirt_loops": "2",             # memory/feedback-keep-skirt.md
    "skirt_distance": "3",
    "skirt_height": "1",
    "skirt_per_object": "0",        # one skirt around the plate, not one per half
    "wall_loops": "3",              # the bin's 1.86 mm walls are three 0.62 mm lines
    "wall_generator": "arachne",    # classic turned the exactly-three-line wall into two loops plus slow gap fill
    "sparse_infill_density": "20%",
    "sparse_infill_pattern": "gyroid",
    # PETG lessons from knowledge/learnings/sharks-nametag.md: no ironing, two top walls, closed seams
    "ironing_type": "no ironing",
    "top_one_wall_type": "not apply",
    "seam_gap": "0%",
}
LISTS = {   # process scope, one value per extruder variant; slow small loops and a slow first layer
    "top_surface_speed": "60",
    "small_perimeter_speed": "30",
    "small_perimeter_threshold": "10",
    "gap_infill_speed": "40",
    "initial_layer_speed": "30",
    "initial_layer_infill_speed": "50",
}
FILAMENT_LISTS = {   # filament scope, different_settings_to_system[1]: the PETG preset's textured-plate temperatures, pinned
    "textured_plate_temp": "70",
    "textured_plate_temp_initial_layer": "70",
}


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
    for kind, name, fn in (("machine", MACHINE, "machine.json"), ("process", PROCESS, "process.json"), ("filament", FILAMENT, "filament.json")):
        with open(f"{d}/{fn}", "w") as f:
            json.dump(flatten(kind, name), f)


def plate_origin(p):
    """Bed origin of plate p, 0-indexed, in the 3MF's world frame."""
    return (p % PLATE_COLS) * PLATE_STRIDE, -(p // PLATE_COLS) * PLATE_STRIDE


def layout():
    """Plate-local bed (x, y) of each object's footprint centre, from the STLs' own extents: the parts of a plate
    line up along its axis with the plate's gap between them, and the group is centred on the bed."""
    ext = {stl: trimesh.load(f"{PROJECT}/{stl}").extents for stl in PARTS}
    targets = {}
    for p, (_, axis, gap, items) in enumerate(PLATES):
        a = 0 if axis == "x" else 1
        total = sum(ext[stl][a] for stl, _ in items) + gap * (len(items) - 1)
        cursor = BED_CENTRE[a] - total / 2
        for stl, _ in items:
            c = [BED_CENTRE[0], BED_CENTRE[1]]
            c[a] = cursor + ext[stl][a] / 2
            cursor += ext[stl][a] + gap
            targets[stl] = (p, c[0], c[1])
            assert c[0] - ext[stl][0] / 2 >= 5 and c[0] + ext[stl][0] / 2 <= BED - 5 and \
                c[1] - ext[stl][1] / 2 >= 5 and c[1] + ext[stl][1] / 2 <= BED - 5, f"{stl} is within 5 mm of the bed edge: {c}"
    return targets, ext


def matrix(transform):
    """3MF transform (12 numbers, row-major 3x3 then the translation) as a 4x4 that acts on column vectors."""
    t = [float(v) for v in transform.split()] if transform else [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    m = np.eye(4)
    m[:3, :3] = np.array(t[:9]).reshape(3, 3).T
    m[:3, 3] = t[9:]
    return m


def world_bounds(files):
    """{object id: (lo, hi)} of every build item in world mm, from the meshes and transforms in the 3MF itself
    (item transform x component transform x the mesh's own coordinates). files maps archive names to bytes."""
    main = files["3D/3dmodel.model"].decode()
    comps = {oid: re.findall(r'<component p:path="([^"]+)" objectid="(\d+)"(?: [^>]*?transform="([^"]*)")?', body)
             for oid, body in re.findall(r'<object id="(\d+)"[^>]*>(.*?)</object>', main, re.S)}
    out = {}
    for oid, tr in re.findall(r'<item objectid="(\d+)"[^>]*?transform="([^"]*)"', main):
        pts = []
        for path, sub_id, comp_t in comps[oid]:
            sub = files[path.lstrip("/")].decode()
            mesh = re.search(rf'<object id="{sub_id}"[^>]*>(.*?)</object>', sub, re.S).group(1)
            v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', mesh), dtype=float)
            pts.append((matrix(tr) @ matrix(comp_t) @ np.c_[v, np.ones(len(v))].T).T[:, :3])
        pts = np.vstack(pts)
        out[oid] = (pts.min(axis=0), pts.max(axis=0))
    return out


def read_all(path):
    with zipfile.ZipFile(path) as z:
        return [(i, z.read(i.filename)) for i in z.infolist()]


def objects_by_source(msc):
    """{source stl: object id} from model_settings.config; the CLI does not keep objects in input order."""
    found = dict((name, oid) for oid, name in re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', msc))
    assert set(found) == set(PARTS), f"objects in the export {sorted(found)} are not the parts {sorted(PARTS)}"
    return found


def author(src, dst, targets):
    """Place every object on its plate, write the plate blocks, apply the overrides, pin the filament to extruder 1."""
    entries = read_all(src)
    files = {i.filename: data for i, data in entries}
    model = files["3D/3dmodel.model"].decode()
    msc = files["Metadata/model_settings.config"].decode()
    ids = objects_by_source(msc)
    by_id = {oid: stl for stl, oid in ids.items()}

    # item transforms: identity rotation, translation chosen so the object's own bounds land on target with floor on z 0
    bounds = world_bounds(files)        # under the export's transforms
    def move(m):
        oid = re.search(r'objectid="(\d+)"', m.group(1)).group(1)
        p, cx, cy = targets[by_id[oid]]
        ox, oy = plate_origin(p)
        lo, hi = bounds[oid]
        t = [float(v) for v in m.group(2).split()]
        assert np.allclose(t[:9], [1, 0, 0, 0, 1, 0, 0, 0, 1]), f"the export rotated object {oid}: {t[:9]}"
        shift = (ox + cx - (lo[0] + hi[0]) / 2, oy + cy - (lo[1] + hi[1]) / 2, -lo[2])
        return m.group(1) + 'transform="1 0 0 0 1 0 0 0 1 %.6g %.6g %.6g"' % tuple(t[9 + i] + shift[i] for i in range(3))
    model, moved = re.subn(r'(<item [^>]*?)transform="([^"]*)"', move, model)
    assert moved == len(PARTS), (moved, len(PARTS))

    # object names, then one plate block per plate (the export's single block is the template for the other keys)
    for stl, label in PARTS.items():
        msc = msc.replace(f'key="name" value="{stl}"', f'key="name" value="{label}"')
    tpl = re.search(r"  <plate>.*?</plate>\n", msc, re.S).group(0)
    assert "<model_instance>" not in tpl, "--arrange 0 was expected to write no model_instance"
    keep = [l for l in tpl.splitlines() if "<metadata" in l and not re.search(r'key="(plater_id|plater_name)"', l)]
    keep = [l.replace('key="filament_map_mode" value="Auto For Flush"', 'key="filament_map_mode" value="Manual"') for l in keep]
    assert any('key="filament_map_mode" value="Manual"' in l for l in keep), tpl
    ident, blocks = 1000, []
    for p, (name, _, _, items) in enumerate(PLATES):
        b = ["  <plate>", '    <metadata key="plater_id" value="%d"/>' % (p + 1), '    <metadata key="plater_name" value="%s"/>' % name, *keep]
        for stl, _ in items:
            ident += 11
            b += ["    <model_instance>",
                  '      <metadata key="object_id" value="%s"/>' % ids[stl],
                  '      <metadata key="instance_id" value="0"/>',
                  '      <metadata key="identify_id" value="%d"/>' % ident,
                  "    </model_instance>"]
        b.append("  </plate>")
        blocks.append("\n".join(b) + "\n")
    msc = msc.replace(tpl, "".join(blocks))

    cfg = json.loads(files["Metadata/project_settings.config"])
    cfg.update(SCALARS)
    for k, v in LISTS.items():
        assert isinstance(cfg[k], list), f"{k} is not a per-variant list: {cfg[k]!r}"
        cfg[k] = [v] * len(cfg[k])
    for k, v in FILAMENT_LISTS.items():
        assert isinstance(cfg[k], list), f"{k} is not a per-filament list: {cfg[k]!r}"
        cfg[k] = [v] * len(cfg[k])
    # any key changed in a project 3MF must be listed here or Studio's GUI resets it on open;
    # the list is positional: [0] process, [1..N] the N filaments, [N+1] machine
    n_fil = len(cfg["filament_settings_id"])
    assert n_fil == 1, cfg["filament_settings_id"]
    diff = cfg.get("different_settings_to_system") or []
    diff += [""] * (n_fil + 2 - len(diff))
    diff[0] = ";".join(sorted(set(x for x in diff[0].split(";") if x) | set(SCALARS) | set(LISTS)))
    diff[1] = ";".join(sorted(set(x for x in diff[1].split(";") if x) | set(FILAMENT_LISTS)))
    cfg["different_settings_to_system"] = diff
    cfg["filament_map_mode"], cfg["filament_map"], cfg["filament_nozzle_map"] = "Manual", ["1"], ["1"]
    cfg["filament_colour"] = cfg["filament_multi_colour"] = [FILAMENT_COLOUR]

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item, data in entries:
            if item.filename == "3D/3dmodel.model":
                data = model.encode()
            elif item.filename == "Metadata/model_settings.config":
                data = msc.encode()
            elif item.filename == "Metadata/project_settings.config":
                data = json.dumps(cfg, indent=4).encode()
            zout.writestr(item, data)


def check_settings(path, what):
    files = dict((i.filename, d) for i, d in read_all(path))
    cfg = json.loads(files["Metadata/project_settings.config"])
    for k, v in SCALARS.items():
        assert cfg[k] == v, f"{what}: {k} did not stick: {cfg[k]}"
    for k, v in {**LISTS, **FILAMENT_LISTS}.items():
        assert set(cfg[k]) == {v}, f"{what}: {k} did not stick: {cfg[k]}"
    diff = cfg["different_settings_to_system"]
    assert len(diff) == 3, f"{what}: different_settings_to_system has {len(diff)} slots, expected process, filament, machine"
    assert set(SCALARS) | set(LISTS) <= set(diff[0].split(";")), f"{what}: process keys missing from different_settings_to_system[0]"
    assert set(FILAMENT_LISTS) <= set(diff[1].split(";")), f"{what}: filament keys missing from different_settings_to_system[1]"
    assert cfg["printer_settings_id"] == MACHINE and cfg["print_settings_id"] == PROCESS and cfg["filament_settings_id"] == [FILAMENT], \
        (cfg["printer_settings_id"], cfg["print_settings_id"], cfg["filament_settings_id"])
    assert cfg["nozzle_diameter"][0] == "0.6" and cfg["layer_height"] == f"{LAYER:g}", (cfg["nozzle_diameter"], cfg["layer_height"])
    assert cfg["filament_map_mode"] == "Manual" and cfg["filament_map"] == ["1"] and cfg["filament_nozzle_map"] == ["1"], \
        f"{what}: not pinned to extruder 1: {cfg['filament_map_mode']}, {cfg['filament_map']}, {cfg['filament_nozzle_map']}"
    assert cfg["filament_colour"] == [FILAMENT_COLOUR], cfg["filament_colour"]

    ms = files["Metadata/model_settings.config"].decode()
    names = dict((name, oid) for oid, name in re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', ms))
    assert set(names) == set(PARTS.values()), f"{what}: object names {sorted(names)}"
    plates = re.findall(r"<plate>(.*?)</plate>", ms, re.S)
    assert len(plates) == len(PLATES), f"{what}: {len(plates)} plate blocks"
    for p, (pname, _, _, items) in enumerate(PLATES):
        blk = plates[p]
        assert f'key="plater_id" value="{p + 1}"' in blk, f"{what}: plate {p + 1} id"
        assert f'key="plater_name" value="{pname}"' in blk, f"{what}: plate {p + 1} is not named {pname!r}"
        assert 'key="filament_map_mode" value="Manual"' in blk, f"{what}: plate {p + 1} filament map mode"
        listed = re.findall(r'<metadata key="object_id" value="(\d+)"/>', blk)
        want = [names[label] for _, label in items]
        assert sorted(listed) == sorted(want), f"{what}: plate {p + 1} lists objects {listed}, expected {want} ({[l for _, l in items]})"
    return files, names


def check_placement(files, names, targets, ext, what):
    """Every object unrotated, floor on z 0, footprint centred where layout() put it inside its plate's cell, by the
    3MF's own geometry; neighbours exactly the plate's gap apart."""
    bounds = world_bounds(files)
    by_oid = {names[label]: stl for stl, label in PARTS.items()}
    assert set(bounds) == set(by_oid), f"{what}: build items {sorted(bounds)} vs objects {sorted(by_oid)}"
    result = {}
    for oid, (lo, hi) in bounds.items():
        stl = by_oid[oid]
        p, cx, cy = targets[stl]
        ox, oy = plate_origin(p)
        assert np.allclose(hi - lo, ext[stl], atol=0.01), f"{what}: {stl} world extents {hi - lo} differ from the STL's {ext[stl]}: rotated"
        assert abs((lo[0] + hi[0]) / 2 - (ox + cx)) < 0.01 and abs((lo[1] + hi[1]) / 2 - (oy + cy)) < 0.01, f"{what}: {stl} not at {(ox + cx, oy + cy)}: {lo} {hi}"
        assert abs(lo[2]) < 0.01, f"{what}: {stl} floor at z {lo[2]:.3f}"
        assert lo[0] >= ox and lo[1] >= oy and hi[0] <= ox + BED and hi[1] <= oy + BED, f"{what}: {stl} off plate {p + 1}'s {BED:g} mm bed: {lo} {hi}"
        result[PARTS[stl]] = {"plate": p + 1, "min_mm": [round(float(v), 2) for v in lo], "max_mm": [round(float(v), 2) for v in hi]}
    for p, (_, axis, gap, items) in enumerate(PLATES):
        a = 0 if axis == "x" else 1
        for (s1, _), (s2, _) in zip(items, items[1:]):
            got = bounds[names[PARTS[s2]]][0][a] - bounds[names[PARTS[s1]]][1][a]
            assert abs(got - gap) < 0.01, f"{what}: plate {p + 1}: {s1} and {s2} are {got:.2f} mm apart, expected {gap}"
    return result


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


def hhmm(seconds):
    return "%d:%02d" % divmod(round(seconds / 60), 60)


def slice_plate(path, tmp, p, ext):
    """A real slice of plate p (1-indexed) through graft_slice; the predicted time and grams come from slice_info.config
    and the settings that matter are read back from the sliced G-code."""
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
    temp, bed = preset["nozzle_temperature"][0], FILAMENT_LISTS["textured_plate_temp"]
    assert re.search(rf"^\s*M10[49] S{temp}\b", gcode, re.M), f"plate {p}: nozzle temperature {temp} is not in the G-code"
    assert re.search(rf"^\s*M1[49]0 S{bed}\b", gcode, re.M), f"plate {p}: bed temperature {bed} is not in the G-code"
    assert re.search(r"^; filament_map = 1$", gcode, re.M), f"plate {p}: the G-code does not print from extruder 1"
    assert re.search(r"^; nozzle_diameter = 0\.6(,0\.6)*$", gcode, re.M), f"plate {p}: nozzle_diameter is not 0.6 in the G-code"
    for k in ("layer_height", "wall_loops", "wall_generator", "sparse_infill_density", "sparse_infill_pattern", "skirt_loops",
              "skirt_per_object", "brim_type", "ironing_type", "seam_gap"):
        v = SCALARS.get(k, f"{LAYER:g}")
        assert re.search(rf"^; {k} = {re.escape(v)}$", gcode, re.M), f"plate {p}: {k} = {v} is not in the sliced G-code"
    feature_mm, xy, z_top = gcode_stats(gcode)
    assert "Brim" not in feature_mm and "Skirt" in feature_mm, f"plate {p}: expected a skirt and no brim: {feature_mm}"
    assert xy[0] >= 0 and xy[1] >= 0 and xy[2] <= BED and xy[3] <= BED, f"plate {p}: toolpaths leave the bed: {xy}"
    height = max(ext[stl][2] for stl, _ in PLATES[p - 1][3])
    assert abs(z_top - height) <= LAYER + 1e-6, f"plate {p}: the sliced top is at z {z_top}, the tallest part is {height} mm"
    return {"name": PLATES[p - 1][0], "objects": [label for _, label in PLATES[p - 1][3]],
            "time": hhmm(seconds), "seconds": seconds, "gcode_estimate": res["time"], "grams": round(grams, 1),
            "metres": round(used_m, 2), "used_g_per_filament": round(used_g, 1), "layers": res["layers"], "top_z": z_top,
            "nozzle_C": int(temp), "bed_C": int(bed), "toolpath_xy_mm": xy, "feature_mm": feature_mm}


def verify(path, tmp, targets, ext):
    """Settings and placement in the file, a CLI round trip, then a real slice of every plate, one at a time.
    A round trip alone does not prove sliceability."""
    files, names = check_settings(path, "authored file")
    result = {"placement_mm": check_placement(files, names, targets, ext, "authored file")}

    r = subprocess.run(["bambu-studio", "--arrange", "0", "--export-3mf", "roundtrip.3mf", "--outputdir", ".", path],
                       cwd=tmp, capture_output=True, text=True, timeout=600)
    assert os.path.exists(f"{tmp}/roundtrip.3mf"), f"round trip failed rc={r.returncode}\n{r.stdout[-1500:]}"
    rt_files, rt_names = check_settings(f"{tmp}/roundtrip.3mf", "CLI round trip")
    check_placement(rt_files, rt_names, targets, ext, "CLI round trip")
    result["roundtrip"] = "2 plates, 4 objects, settings and placement survive bambu-studio --arrange 0 --export-3mf"

    # The CLI cannot slice its own project files (rc 156); graft_slice adds the GUI-only keys to a throwaway copy.
    # One slice process at a time (CLAUDE.md heavy-jobs rule).
    result["plates"] = [slice_plate(path, tmp, p, ext) for p in range(1, len(PLATES) + 1)]
    secs, grams = sum(pl["seconds"] for pl in result["plates"]), sum(pl["grams"] for pl in result["plates"])
    result.update({"total_time": hhmm(secs), "total_seconds": secs, "total_grams": round(grams, 1),
                   "overrides": {"process": {**SCALARS, **LISTS}, "filament": FILAMENT_LISTS},
                   "presets": {"machine": MACHINE, "process": PROCESS, "filament": FILAMENT}})
    return result


def main():
    final = f"{PROJECT}/{OUT}"
    targets, ext = layout()
    with tempfile.TemporaryDirectory() as tmp:
        write_presets(tmp)
        for stl in PARTS:
            shutil.copy(f"{PROJECT}/{stl}", f"{tmp}/{stl}")
        # --export-3mf must be a bare filename; an absolute path alongside --outputdir makes the CLI exit 243 without writing.
        # --arrange 0: every transform and plate block is written in author(), nothing is left to the arranger.
        r = subprocess.run(
            ["bambu-studio", "--arrange", "0",
             "--load-settings", "machine.json;process.json",
             "--load-filaments", "filament.json",
             "--export-3mf", "raw.3mf", "--outputdir", ".", *PARTS],
            cwd=tmp, capture_output=True, text=True, timeout=600)
        assert os.path.exists(f"{tmp}/raw.3mf"), f"CLI export failed rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
        author(f"{tmp}/raw.3mf", final, targets)
        result = verify(final, tmp, targets, ext)
    with open(f"{PROJECT}/{STEM}-slice.json", "w") as f:
        json.dump(result, f, indent=1)
    print(final)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
