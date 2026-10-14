"""Where the holder's filament goes, and what each saving lever is worth, from real slices.

Brian, 2026-10-12: keep the holder under 500 g so two print from one 1000 g spool. The 2026-10-11 file slices at 564 g of
body PETG. This tool (1) breaks a sliced G-code down by filament and feature (walls, sparse infill, solid infill, supports,
prime tower, flush), and (2) slices variants of holder-print.3mf with changed process settings or modifier settings, so
every option Brian sees carries a real number.

Usage (from anywhere, vault venv):
  filament_budget.py breakdown <sliced.3mf>                  grams per filament and feature
  filament_budget.py variant <name> key=value ...            copy holder-print.3mf with the settings changed, slice, report
      prefix a key with mod: to change both solid modifiers' settings (e.g. mod:sparse_infill_density=100%),
      with base: or face: for one of them; everything else is a process setting (e.g. wall_loops=2 sparse_infill_density=10%)
  filament_budget.py table                                   all variants sliced so far, one line each
Variants live in $SCRATCH/fil/<name>/ (print.3mf, sliced.3mf, result.json); `table` merges them into filament-variants.json.
  filament_budget.py regions <sliced.3mf> [--store]         body grams by region (solid face/base, drum core, supports by what they hold); --store writes it to result.json
"""
import json
import math
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(PROJECT), "Sharks-nametag", "pipeline"))
SCRATCH = os.environ.get("SCRATCH", "/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/612fec58-43f6-4bff-a4e8-46ee5353df03/scratchpad")
FIL = f"{SCRATCH}/fil"
RESULTS = f"{PROJECT}/filament-variants.json"
AREA = math.pi * 0.875 ** 2   # mm2 of 1.75 filament


def gcode_of(sliced):
    z = zipfile.ZipFile(sliced)
    name = [n for n in z.namelist() if n.endswith(".gcode")][0]
    return z.read(name).decode(errors="replace")


def densities(sliced):
    cfg = json.loads(zipfile.ZipFile(sliced).read("Metadata/project_settings.config"))
    return [float(d) for d in cfg["filament_density"]]


def segments(sliced):
    """Every extruding move (G1/G2/G3, relative E) as (x0, y0, x1, y1, z, e_mm, filament 1.., feature); flushes are 'Flush'."""
    g = gcode_of(sliced)
    tool, feat, flushing, z = 0, "Start", False, 0.0
    x = y = debt = 0.0   # debt: retractions, paid back by the next extrusion so deretractions do not count as plastic
    out = []
    for line in g.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line.startswith("; FLUSH_START"):
            flushing = True
        elif line.startswith("; FLUSH_END"):
            flushing = False
        elif re.match(r"T\d+\b", line):
            tool = int(line[1:].split()[0])
        elif line.startswith(("G1 ", "G2 ", "G3 ", "G0 ")):
            mx, my, mz, me = (re.search(rf" {a}(-?[0-9.]+)", line) for a in "XYZE")
            x1 = float(mx.group(1)) if mx else x
            y1 = float(my.group(1)) if my else y
            if mz:
                z = float(mz.group(1))
            if me:
                e = float(me.group(1)) + debt
                if e > 0:
                    out.append((x, y, x1, y1, z, e, tool + 1, "Flush" if flushing else feat))
                    debt = 0.0
                else:
                    debt = e
            x, y = x1, y1
    return out


def breakdown(sliced):
    """{(filament index 1.., feature): grams}."""
    dens = densities(sliced)
    mm = {}
    for x0, y0, x1, y1, z, e, f, feat in segments(sliced):
        mm[(f, feat)] = mm.get((f, feat), 0.0) + e
    return {k: v * AREA / 1000 * dens[k[0] - 1] for k, v in mm.items()}


def to_model(sliced):
    """Bed to model coordinates from the object's item transform (the CLI's arrange turns the part on the bed)."""
    m = re.search(r'<item [^>]*transform="([^"]+)"', zipfile.ZipFile(sliced).read("3D/3dmodel.model").decode()).group(1).split()
    m00, m01, m10, m11, tx, ty = (float(m[i]) for i in (0, 1, 3, 4, 9, 10))
    det = m00 * m11 - m01 * m10
    return lambda x, y: (((x - tx) * m11 - (y - ty) * m10) / det, ((y - ty) * m00 - (x - tx) * m01) / det)


def modifier_meshes(sliced):
    """{'base': mesh, 'face': mesh} of the solid modifiers, in model coordinates. Read from the UNSLICED print file next to the
    slice (or the project's), whose meshes are centred with the offset in the part matrix; the sliced file bakes the offset in."""
    import numpy as np
    import trimesh
    src = os.path.join(os.path.dirname(sliced), "print.3mf")
    z = zipfile.ZipFile(src if os.path.exists(src) else f"{PROJECT}/holder-print.3mf")
    model = z.read("3D/Objects/object_1.model").decode()
    ms = z.read("Metadata/model_settings.config").decode()
    out = {}
    for pid, name, mat in re.findall(r'<part id="(\d+)" subtype="modifier_part"[^>]*>\s*<metadata key="name" value="MOD solid (\w+)[^"]*"/>\s*<metadata key="matrix" value="([^"]+)"', ms):
        off = [float(v) for v in mat.split()][3::4][:3]
        body = re.search(rf'<object id="{pid}"[^>]*>\s*<mesh>(.*?)</mesh>', model, re.S).group(1)
        v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', body), float) + off
        f = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body), int)
        out[name] = trimesh.Trimesh(v, f, process=False)
    return out


def contains(mesh, pts, chunk=2000):
    """Point-in-mesh test a chunk at a time, with near-vertical rays. trimesh without embree expands every call to roughly
    60 to 150 KB per point: one pass over the holder's 314k sparse-infill points peaked at 9.7 GB (nine in parallel
    OOM-killed the box on 2026-10-12). 2000 points per call keeps a pass under 1 GB, and a near-vertical ray (not exactly
    +Z, so it never runs along a layer edge) shrinks each ray's candidate box, halving the time again: 0.5 GB, 12 s,
    same result as mesh.contains() on every variant checked."""
    import numpy as np
    from trimesh.ray import ray_util
    if len(pts) == 0:
        return np.zeros(0, bool)
    d = np.array([0.01, 0.013, 1.0])
    d /= np.linalg.norm(d)
    return np.concatenate([ray_util.contains_points(mesh.ray, c, check_direction=d) for c in np.array_split(pts, max(1, len(pts) // chunk))])


def regions(sliced):
    """Body filament by where it is: the solid regions, the drum's sparse core, and the supports by what they hold up."""
    import numpy as np
    dens = densities(sliced)
    back = to_model(sliced)
    mods = modifier_meshes(sliced)
    segs = [s for s in segments(sliced) if s[6] == 1]
    mid = np.array([back((s[0] + s[2]) / 2, (s[1] + s[3]) / 2) + (s[4] - 0.15,) for s in segs])   # mid-layer z
    e = np.array([s[5] for s in segs]) * AREA / 1000 * dens[0]
    feat = np.array([s[7] for s in segs])
    flange_r, drum_r = 52.0, 45.0
    r = np.hypot(mid[:, 0], mid[:, 1])
    where = np.array(["other"] * len(segs), dtype=object)
    for name, mesh in mods.items():
        sel = feat == "Sparse infill"
        inside = contains(mesh, mid[sel])
        idx = np.flatnonzero(sel)[inside]
        where[idx] = f"solid {name}"
    core = (feat == "Sparse infill") & (where == "other")
    where[core] = "drum core"
    sup = np.isin(feat, ["Support", "Support transition"])
    where[sup & (mid[:, 1] > flange_r + 1)] = "support: under the lip"
    where[sup & (mid[:, 1] <= flange_r + 1) & (r > drum_r - 1)] = "support: under the flange ring"
    where[sup & (r <= drum_r - 1) & (mid[:, 2] > 13)] = "support: in the cavity"
    where[sup & (where == "other")] = "support: elsewhere"
    walls = np.isin(feat, ["Outer wall", "Inner wall", "Overhang wall"])
    where[walls] = "walls"
    shells = np.isin(feat, ["Top surface", "Bottom surface", "Internal solid infill", "Floating vertical shell", "Bridge", "Gap infill"])
    where[shells] = "shells and solid layers"
    where[feat == "Prime tower"] = "prime tower"
    tot = {}
    for w, g in zip(where, e):
        tot[w] = tot.get(w, 0.0) + g
    return dict(sorted(tot.items(), key=lambda kv: -kv[1])), segs, mid, e, feat, where


def report(sliced):
    b = breakdown(sliced)
    info = zipfile.ZipFile(sliced).read("Metadata/slice_info.config").decode()
    per = {int(i): float(g) for i, g in re.findall(r'<filament id="(\d+)"[^>]*used_g="([^"]*)"', info)}
    secs = int(re.search(r'key="prediction" value="([^"]*)"', info).group(1))
    out = {"minutes": round(secs / 60), "slice_info_g": per, "features": {}}
    for f in sorted({k[0] for k in b}):
        rows = sorted(((k[1], v) for k, v in b.items() if k[0] == f), key=lambda kv: -kv[1])
        out["features"][f] = {n: round(v, 1) for n, v in rows}
    return out


def print_report(r):
    print(f"{r['minutes'] // 60} h {r['minutes'] % 60:02d} min; slice_info grams per filament: " + ", ".join(f"{i}: {g:.1f}" for i, g in sorted(r["slice_info_g"].items())))
    for f, rows in r["features"].items():
        print(f"filament {f}: {sum(rows.values()):.1f} g from the moves")
        for n, v in rows.items():
            print(f"    {n:24s} {v:7.1f} g")


def patch_variant(src, dst, process, mods):
    """Copy a print 3MF with process settings and per-modifier settings changed."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "Metadata/project_settings.config" and process:
                cfg = json.loads(data)
                for k, v in process.items():
                    cfg[k] = [v] * len(cfg[k]) if isinstance(cfg.get(k), list) else v   # vector keys (wipe_tower_x, per-filament ones) stay vectors
                diff = set(cfg["different_settings_to_system"][0].split(";")) | set(process)
                cfg["different_settings_to_system"][0] = ";".join(sorted(x for x in diff if x))
                data = json.dumps(cfg, indent=4).encode()
            if item.filename == "Metadata/model_settings.config" and mods:
                ms = data.decode()
                for which, settings in mods.items():
                    for k, v in settings.items():
                        def sub(m):
                            block = m.group(0)
                            if v is None:
                                return re.sub(rf'\s*<metadata key="{k}" value="[^"]*"/>', "", block)
                            if f'key="{k}"' in block:
                                return re.sub(rf'(<metadata key="{k}" value=")[^"]*(")', rf"\g<1>{v}\2", block)
                            return block.replace("<mesh_stat", f'<metadata key="{k}" value="{v}"/>\n      <mesh_stat')
                        ms = re.sub(rf'<part id="\d+" subtype="modifier_part"[^>]*>\s*<metadata key="name" value="MOD solid {which}[^"]*"/>.*?</part>', sub, ms, flags=re.S)
                data = ms.encode()
            zout.writestr(item, data)


def variant(name, assignments, src=f"{PROJECT}/holder-print.3mf"):
    from graft_slice import graft_slice
    process, mods = {}, {}
    for a in assignments:
        k, v = a.split("=", 1)
        if ":" in k:
            scope, key = k.split(":", 1)
            for w in (("base", "face") if scope == "mod" else (scope,)):
                mods.setdefault(w, {})[key] = None if v == "-" else v
        else:
            process[k] = v
    d = f"{FIL}/{name}"
    os.makedirs(d, exist_ok=True)
    patch_variant(src, f"{d}/print.3mf", process, mods)
    res = graft_slice(f"{d}/print.3mf", f"{d}/sliced.3mf")
    assert res.get("rc") == 0 and os.path.exists(f"{d}/sliced.3mf"), res
    r = report(f"{d}/sliced.3mf")
    r["name"], r["settings"] = name, assignments
    r["regions"] = {k: round(v, 1) for k, v in regions(f"{d}/sliced.3mf")[0].items()}
    with open(f"{d}/result.json", "w") as f:
        json.dump(r, f, indent=1)
    return r


def collect():
    """Every variant's result.json (variants slice in parallel, so each keeps its own file), merged into filament-variants.json."""
    allr = {}
    for name in sorted(os.listdir(FIL)):
        f = f"{FIL}/{name}/result.json"
        if os.path.exists(f):
            r = json.load(open(f))
            if "minutes" in r:   # the CLI drops its own result.json in the same directory when a slice fails
                allr[r.get("name", name)] = r
    with open(RESULTS, "w") as f:
        json.dump(allr, f, indent=1)
    return allr


def table():
    allr = collect()
    print(f"{'variant':28s} {'time':>9s} {'body g':>7s} {'all g':>7s}  settings")
    for name, r in allr.items():
        print(f"{name:28s} {r['minutes'] // 60:2d} h {r['minutes'] % 60:02d} {r['slice_info_g'].get('1', r['slice_info_g'].get(1, 0)):7.1f} {sum(r['slice_info_g'].values()):7.1f}  {' '.join(r.get('settings', []))}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "breakdown":
        print_report(report(sys.argv[2]))
    elif cmd == "variant":
        print_report(variant(sys.argv[2], sys.argv[3:]))
    elif cmd == "table":
        table()
    elif cmd == "regions":
        tot = regions(sys.argv[2])[0]
        print(f"body filament {sum(tot.values()):.1f} g by region:")
        for k, v in tot.items():
            print(f"    {k:32s} {v:7.1f} g")
        if "--store" in sys.argv:
            f = os.path.join(os.path.dirname(sys.argv[2]), "result.json")
            r = json.load(open(f)) if os.path.exists(f) else report(sys.argv[2]) | {"name": os.path.basename(os.path.dirname(sys.argv[2])), "settings": []}
            r["regions"] = {k: round(v, 1) for k, v in tot.items()}
            with open(f, "w") as out:
                json.dump(r, out, indent=1)
