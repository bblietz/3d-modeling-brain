"""Back-text probe: does the C7 OBJECT key (detect_narrow_internal_solid_infill 0)
open gaps in the mirrored MAX 18 inlay on the back (bottom) face, and what
region-level fix on a second modifier part closes them again.

Standalone post-processor of a COPY of the gate file (never touches the
batch builders): build a variant 3MF (drop the object key and/or add a
modifier part over the back text), graft-slice it, measure the first
layers inside the navy inlay outlines, compare with the as-is gate slice.

Mechanism (BambuStudio src/libslic3r/Fill/Fill.cpp, group_fills): with the
object key ON, every stInternalSolid island that vanishes under a 3 mm
inset (NARROW_INFILL_AREA_THRESHOLD, i.e. anything < 6 mm wide) is filled
ipConcentricInternal; with it OFF the island keeps the region's
internal_solid_infill_pattern (gate: zig-zag = rectilinear at
infill_direction 45). The check reads layer.object()->config(), so no
region key can re-enable it; a modifier CAN set internal_solid_infill_pattern
(region key, PrintObject.cpp posInfill list) to concentric on the back.

Usage (all output under --out, default the session scratchpad):
  backfix_probe.py build <name> [--drop-key] [--mod k=v,k=v] [--buffer 0.5] [--z0 0] [--z1 0.56]
  backfix_probe.py slice <name>            # graft-slice <out>/<name>.3mf -> <out>/<name>-sliced.3mf
  backfix_probe.py measure <name> [<name>...]   # back layers 1-5 table (+ front tier check)
  backfix_probe.py compare <ref> <name>    # per-layer segment identity, inside/outside the back zone
  backfix_probe.py render <png> <name> [<name>...]   # layers 1-4 of the back text, one column per variant
"""
import argparse
import json
import math
import os
import re
import sys
import time
import zipfile
from collections import Counter

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.affinity import translate
from shapely.ops import unary_union

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)
import fillcore_mod as fm  # noqa: E402
import toolpath_voids as tv  # noqa: E402
from graft_slice import graft_slice  # noqa: E402

GATE = f"{fm.PROJ}/final/sharks-nametag-max-18.3mf"   # production dir since 2026-08-26
OUT = ("/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/"
       "744ff3b5-47ea-4284-a4c0-57fb6e3fdbcb/scratchpad/backfix")
ORIGIN = (128.0, 128.0)   # tag origin on the plate (single-tag gate file)
BACK_Z = 0.3              # navy STL section inside the 0.6 mm back inlay
PX = tv.PX
INSET = 0.30
GROUPS = {"MAX": lambda b: b[1] > 14.0, "18": lambda b: -13.0 < b[1] < 13.0, "2015-2016": lambda b: b[3] < -14.0}
OBJ_KEY = '<metadata key="detect_narrow_internal_solid_infill" value="0"/>'


def back_geometry():
    """Tag-mm navy inlay outlines on the back face: list of polygons and
    the per-group unions (MAX, 18, 2015-2016, ALL)."""
    navy = trimesh.load(f"{fm.PROJ}/sharks-nametag-navy.stl")
    polys = fm.section_polys(navy, BACK_Z)
    assert len(polys) == 14, len(polys)
    groups = {k: unary_union([p for p in polys if f(p.bounds)]) for k, f in GROUPS.items()}
    assert sum(len(fm.geoms(g)) for g in groups.values()) == 14, {k: len(fm.geoms(g)) for k, g in groups.items()}
    groups["ALL"] = unary_union(polys)
    return polys, groups


def build(name, drop_key=False, mod_keys=None, buffer=0.5, z0=0.0, z1=0.56, out=OUT):
    """<out>/<name>.3mf = the gate file, optionally without the object key
    and/or with a modifier part over the back text (navy outlines buffered
    `buffer`, z0..z1 tag mm) carrying the region keys mod_keys."""
    dst = f"{out}/{name}.3mf"
    with zipfile.ZipFile(GATE) as zin:
        model = zin.read("Metadata/model_settings.config").decode()
        model3d = zin.read("3D/3dmodel.model").decode()
        objfiles = {n: zin.read(n).decode() for n in zin.namelist() if n.startswith("3D/Objects/")}
        assert model.count(OBJ_KEY) == 1, "gate file has no object key"
        if drop_key:
            model = re.sub(r"\s*" + re.escape(OBJ_KEY), "", model)
        if mod_keys:
            polys, _ = back_geometry()
            mesh = fm.extrude(unary_union([p.buffer(buffer) for p in polys]), z0, z1)
            mesh_c, mc = fm.centered(mesh)
            _, white_c = fm.centered(trimesh.load(f"{fm.PROJ}/sharks-nametag-white.stl"))
            om = re.search(r'<object id="(\d+)">.*?</object>', model, re.S)
            oid = om.group(1)
            pos = fm.object_pos(model3d, oid, white_c)
            pid = fm.next_object_id(model3d, objfiles)
            label = "MOD back text: " + ", ".join(f"{k} {v}" for k, v in mod_keys.items())
            block, model3d = fm.inject_modifier(om.group(0), model3d, objfiles, oid, pid, label, "mod-back-text.stl",
                                                mesh_c, mc, pos, mod_keys)
            model = model[:om.start()] + block + model[om.end():]
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "Metadata/model_settings.config":
                    zout.writestr(item, model)
                elif item.filename == "3D/3dmodel.model":
                    zout.writestr(item, model3d)
                elif item.filename in objfiles:
                    zout.writestr(item, objfiles[item.filename])
                else:
                    zout.writestr(item, zin.read(item.filename))
    return dst


def slice_variant(name, out=OUT):
    t0 = time.time()
    res = graft_slice(f"{out}/{name}.3mf", f"{out}/{name}-sliced.3mf")
    res["wall_seconds"] = round(time.time() - t0, 1)
    with open(f"{out}/{name}-slice.json", "w") as f:
        json.dump(res, f, indent=1)
    return res


def gcode_of(name, out=OUT):
    return tv.load_gcode(f"{out}/{name}-sliced.3mf")


# ---------------------------------------------------------------- measuring
def window(groups):
    b = translate(groups["ALL"], *ORIGIN).bounds
    x0, y1 = b[0] - 1.0, b[3] + 1.0
    return x0, y1, int((b[2] - b[0] + 2.0) / PX), int((b[3] - b[1] + 2.0) / PX)


def measure_back(gcode, n_layers=5):
    """Per layer (first n_layers) and per group: features present (length
    mm each), extrusion length, path starts, uncovered area inside the
    INSET-inset strokes. Returns (rows, layers, window)."""
    layers = tv.parse_layers(gcode)
    zs = sorted(layers)[:n_layers]
    _, groups = back_geometry()
    x0, y1, W, H = window(groups)
    masks, insets = {}, {}
    for k, g in groups.items():
        gp = translate(g, *ORIGIN)
        masks[k] = ndimage.binary_dilation(tv.poly_mask(gp, x0, y1, W, H), iterations=3)   # +0.06 mm
        gi = gp.buffer(-INSET)
        insets[k] = tv.poly_mask(gi, x0, y1, W, H) if not gi.is_empty else np.zeros((H, W), bool)

    def inside(mask, x, y):
        px, py = int((x - x0) / PX), int((y1 - y) / PX)
        return 0 <= px < W and 0 <= py < H and mask[py, px]

    rows = {}
    uncs = {}
    for z in zs:
        segs = layers[z]
        cov, _ = tv.rasterize(segs, x0, y1, W, H, mask_only=True)
        uncs[z] = ~cov
        rows[z] = {}
        for k in groups:
            feats = Counter()
            starts = 0
            for sx, sy, ex, ey, w, f, st in segs:
                if inside(masks[k], (sx + ex) / 2, (sy + ey) / 2):
                    feats[f] += math.hypot(ex - sx, ey - sy)
                    if st and inside(masks[k], sx, sy):
                        starts += 1
            ang, frac, _ = tv.fill_direction(segs, masks[k], x0, y1, W, H)
            rows[z][k] = dict(feats={f: round(v, 2) for f, v in feats.items()}, length=round(sum(feats.values()), 2),
                              starts=starts, uncovered=round(float((insets[k] & ~cov).sum()) * PX * PX, 3),
                              fill_dir=None if ang is None else round(ang, 1), along=round(frac, 2))
    # stacked voids: pixels uncovered on every one of layers 2-4 (the navy
    # shell layers over the visible face) and on layers 1-4 (a hole from the
    # visible face up to the white), opened with the 0.13 mm disk
    stack = {}
    for label, zsel in (("2-4", zs[1:4]), ("1-4", zs[0:4])):
        m = np.ones((H, W), bool)
        for z in zsel:
            m &= uncs[z]
        m = ndimage.binary_opening(m, structure=tv.disk(tv.OPEN_DISK))
        stack[label] = {k: round(float((m & insets[k]).sum()) * PX * PX, 3) for k in groups}
    return rows, layers, (x0, y1, W, H), stack


def seg_key(s):
    """Geometry key of a segment, independent of the travel direction (a
    loop printed from another seam or in reverse is the same toolpath)."""
    a, b = (round(s[0], 3), round(s[1], 3)), (round(s[2], 3), round(s[3], 3))
    if b < a:
        a, b = b, a
    return a + b + (round(s[4], 3), s[5])


def compare_layers(gcode_a, gcode_b, zone_buffer=1.0):
    """Per layer: (n_a, n_b, only_a, only_b, only_a_outside, only_b_outside)
    on the extrusion-segment sets; 'outside' = both ends outside the back
    text outlines buffered zone_buffer."""
    la, lb = tv.parse_layers(gcode_a), tv.parse_layers(gcode_b)
    _, groups = back_geometry()
    zone = translate(groups["ALL"].buffer(zone_buffer), *ORIGIN)
    x0, y1, W, H = window(groups)
    x0 -= zone_buffer
    y1 += zone_buffer
    W += int(2 * zone_buffer / PX)
    H += int(2 * zone_buffer / PX)
    zmask = tv.poly_mask(zone, x0, y1, W, H)

    def outside(s):
        for x, y in ((s[0], s[1]), (s[2], s[3])):
            px, py = int((x - x0) / PX), int((y1 - y) / PX)
            if 0 <= px < W and 0 <= py < H and zmask[py, px]:
                return False
        return True

    out = {}
    for z in sorted(set(la) | set(lb)):
        ca, cb = Counter(seg_key(s) for s in la.get(z, [])), Counter(seg_key(s) for s in lb.get(z, []))
        oa, ob = ca - cb, cb - ca
        out[z] = (sum(ca.values()), sum(cb.values()), sum(oa.values()), sum(ob.values()),
                  sum(n for k, n in oa.items() if outside(k)), sum(n for k, n in ob.items() if outside(k)))
    return out


def front_check(gcode):
    r = tv.measure(gcode, "tag", [ORIGIN[0]], "0.4", labels=["tag"])
    c = r["results"][0]
    return dict(visible=round(c["visible"], 3), top_interior=round(c["top_interior"], 3), starts_top=c["starts_top"],
                starts_mean=round(c["starts_mean"], 1), angle_top=None if c["angle_top"] is None else round(c["angle_top"], 1),
                along_frac_top=round(c["along_frac_top"], 3), n_layers=r["n_layers"],
                per_layer=[(z, round(u, 3), s, None if a is None else round(a, 1)) for z, u, s, a, _, _ in c["per_layer"]])


# ---------------------------------------------------------------- rendering
UNCOVERED_RGB = (255, 255, 0)


def render(png, names, n_layers=4, scale=2, out=OUT, crop=None):
    """crop = (x0, y0, x1, y1) tag mm to zoom (scale 1); default the whole back text at scale 2."""
    _, groups = back_geometry()
    if crop:
        x0, y1 = crop[0] + ORIGIN[0], crop[3] + ORIGIN[1]
        W, H = int((crop[2] - crop[0]) / PX), int((crop[3] - crop[1]) / PX)
    else:
        x0, y1, W, H = window(groups)
    allp = translate(groups["ALL"], *ORIGIN)
    gi = allp.buffer(-INSET)
    imask = tv.poly_mask(gi, x0, y1, W, H)
    cols = []
    for name in names:
        layers = tv.parse_layers(gcode_of(name, out))
        zs = sorted(layers)[:n_layers]
        panels = []
        for z in zs:
            segs = layers[z]
            cov, img = tv.rasterize(segs, x0, y1, W, H)
            dr = ImageDraw.Draw(img)
            tv.poly_mask(allp, x0, y1, W, H, draw_outline=dr)
            arr = np.asarray(img).copy()
            unc = imask & ~cov
            arr[unc] = UNCOVERED_RGB
            im = Image.fromarray(arr).resize((W // scale, H // scale), Image.BOX)
            d = ImageDraw.Draw(im)
            feats = Counter(s[5] for s in segs if imask[min(H - 1, max(0, int((y1 - (s[1] + s[3]) / 2) / PX))),
                                                        min(W - 1, max(0, int(((s[0] + s[2]) / 2 - x0) / PX)))])
            d.rectangle([0, 0, im.width, 14], fill=(0, 0, 0))
            d.text((4, 2), f"{name}  z {z:.2f}  uncovered(inset {INSET}) {unc.sum() * PX * PX:.2f} mm2  "
                   + " ".join(f"{f}:{n}" for f, n in feats.most_common(4)), fill=(255, 255, 255))
            panels.append(im)
        col = Image.new("RGB", (panels[0].width, sum(p.height for p in panels) + 4 * (len(panels) - 1)), (0, 0, 0))
        yy = 0
        for p in panels:
            col.paste(p, (0, yy))
            yy += p.height + 4
        cols.append(col)
    sheet = Image.new("RGB", (sum(c.width for c in cols) + 6 * (len(cols) - 1), max(c.height for c in cols)), (0, 0, 0))
    xx = 0
    for c in cols:
        sheet.paste(c, (xx, 0))
        xx += c.width + 6
    sheet.save(png)
    return png


# ---------------------------------------------------------------------- CLI
def parse_keys(s):
    return dict(kv.split("=", 1) for kv in s.split(",")) if s else None


def print_table(name, rows):
    print(f"\n== {name}: back text, layers 1-{len(rows)} (length mm inside the outlines; uncovered mm2 inside the {INSET} mm inset)")
    print(f"{'z':>5} {'group':10} {'len':>8} {'starts':>6} {'uncov':>7}  features (mm)")
    for z, groups in rows.items():
        for k, r in groups.items():
            feats = ", ".join(f"{f} {v:.1f}" for f, v in sorted(r["feats"].items(), key=lambda kv: -kv[1]))
            fd = f"fill {r['fill_dir']:.0f} deg {r['along']*100:.0f}%" if r["fill_dir"] is not None else ""
            print(f"{z:5.2f} {k:10} {r['length']:8.1f} {r['starts']:6d} {r['uncovered']:7.3f}  {feats}  {fd}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "slice", "measure", "compare", "render", "front"])
    ap.add_argument("names", nargs="+")
    ap.add_argument("--drop-key", action="store_true")
    ap.add_argument("--mod", default=None, help="k=v,k=v region keys for a back-text modifier part")
    ap.add_argument("--buffer", type=float, default=0.5)
    ap.add_argument("--z0", type=float, default=0.0)
    ap.add_argument("--z1", type=float, default=0.56)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--crop", default=None, help="render zoom: x0,y0,x1,y1 tag mm at full 0.02 mm/px")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.cmd == "build":
        for n in a.names:
            print(build(n, a.drop_key, parse_keys(a.mod), a.buffer, a.z0, a.z1, a.out))
    elif a.cmd == "slice":
        for n in a.names:
            r = slice_variant(n, a.out)
            print(f"{n}: rc {r['rc']} layers {r['layers']} time {r['time']} wall {r['wall_seconds']} s log {r['log']}")
    elif a.cmd == "measure":
        for n in a.names:
            rows, _, _, stack = measure_back(gcode_of(n, a.out))
            print_table(n, rows)
            print("   stacked voids (opened 0.13 mm) uncovered on all of layers 2-4 / 1-4: "
                  + "  ".join(f"{k} {stack['2-4'][k]:.3f}/{stack['1-4'][k]:.3f}" for k in stack["2-4"]))
            with open(f"{a.out}/{n}-back.json", "w") as f:
                json.dump({str(z): r for z, r in rows.items()}, f, indent=1)
    elif a.cmd == "front":
        for n in a.names:
            print(n, json.dumps(front_check(gcode_of(n, a.out))))
    elif a.cmd == "compare":
        ref, others = a.names[0], a.names[1:]
        ga = gcode_of(ref, a.out)
        for n in others:
            res = compare_layers(ga, gcode_of(n, a.out))
            diff = {z: v for z, v in res.items() if v[2] or v[3]}
            print(f"\n== {n} vs {ref}: {len(diff)} of {len(res)} layers differ")
            for z, (na, nb, oa, ob, oao, obo) in diff.items():
                print(f"  z {z:5.2f}: {na} vs {nb} segs, only in {ref} {oa} (outside back zone {oao}), only in {n} {ob} (outside {obo})")
    elif a.cmd == "render":
        crop = [float(v) for v in a.crop.split(",")] if a.crop else None
        print(render(a.names[0], a.names[1:], out=a.out, crop=crop, scale=1 if crop else 2))


if __name__ == "__main__":
    main()
