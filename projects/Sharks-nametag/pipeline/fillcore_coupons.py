"""Thin letters-only fill-core coupons (2026-08-24 late): print ONLY what is
judged, the raised white SANTA letters and the minimum substrate under
them. The earlier fillcore-coupons-02/04 plates reprinted the whole W1
window (1.0 mm slab + full 0.6 mm navy banner + CITY, ball bottom, surfer),
so ~20 of 27 layers lay below the letters.

Coupon (tag mm -> coupon mm, slab bottom at z 0):
  window  = bounding box of the five SANTA glyphs + MARGIN (1.5 mm)
  slab    = white, footprint = window, SLAB thick: 0.30 at 0.4 (9 layers),
            0.40 at 0.2 (15 layers; 0.30 would put the slab top AND the
            banner top exactly on 0.08-layer centers, and 0.32 gives 14
            layers = the wrong top-layer parity, see below)
  parity  = the solid/top fill direction alternates 90 deg per layer, so
            the top layer's fill direction depends on the layer count
            parity: the coupon keeps the parity of the real tag (57 layers
            at 0.2, 37 at 0.4; the earlier W1 plates had 27 and 18, so the
            0.4 plate's C7/C8 directions were swapped vs the real tag)
  stub    = the top STUB (0.24 mm) of the navy banner inside the window,
            with the white letters and the banner bars passing through it
  letters = the white SANTA prisms + the 0.6 mm banner bars inside the
            window, untouched, standing on the untouched navy top
  excluded on purpose: CITY tops, ball-ring arc, surfer, cyan (they are
            islands in the letter-tier layers of the real tag; see report)
All geometry is prismatic in this z range (white 3.36-4.56, navy 3.36-3.96
in the canonical STLs), so the coupon is built by extruding the STL
cross-sections: same outlines the slicer would see from a mesh crop.

Variants (per nozzle) = the fill-core sweep winners, same construction as
exports/fillcore-coupons-02.3mf / -04.3mf: a MODIFIER PART (letter
outlines buffered 0.3 mm, banner top .. letter top + 0.1) carrying region
keys, plus the OBJECT key detect_narrow_internal_solid_infill 0 where the
sweep used it (CLI assemble print_params). The geometry, modifier and 3MF
patch helpers live in fillcore_mod.py (shared with batch_roster.py and
plates.py since the C7 bake, 2026-08-25).

Run:  NOZZLE=0.2 .venv/bin/python projects/Sharks-nametag/pipeline/fillcore_coupons.py
      NOZZLE=0.4 ...   (SCRATCH=<dir> for the intermediate files,
                        OUT_DIR=<dir> to write the plate somewhere other
                        than exports/, e.g. for a dry run; exports/ is the
                        experiments area, recreated on demand, final/ holds
                        the production files)
-> exports/fillcore-coupons-02-thin.3mf | exports/fillcore-coupons-04.3mf,
   CLI round trip + graft slice (graft_slice.py) asserted; also a
   single-coupon plate in SCRATCH for the per-coupon time.
"""
import json
import os
import re
import sys
import zipfile

import trimesh
from shapely.ops import unary_union

import fillcore_mod as fm
from fillcore_mod import (PROJ, PIPE, COLORS, BED_TYPE, SMOOTH_KEYS, SANTA_BOX,  # noqa: F401 (re-exported)
                          letter_geometry, section_polys as _polys, geoms as _geoms, cli)

SCRATCH = os.environ.get("SCRATCH", "/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/"
                         "744ff3b5-47ea-4284-a4c0-57fb6e3fdbcb/scratchpad/fillcore-thin")
OUT_DIR = os.environ.get("OUT_DIR", f"{PROJ}/exports")
TOWER = (105, 160)
MARGIN = 1.5      # mm around the SANTA bounding box
SLAB = {"0.2": 0.40, "0.4": 0.30}   # white slab, per nozzle (tag layer parity + no boundary on a layer center)
STUB = 0.24       # navy banner kept under the letters
MOD_BUFFER = fm.MOD_BUFFER  # modifier = letter outlines grown by this
MOD_ABOVE = 0.1   # modifier top above the letter top
VARIANT_X = [58.0, 128.0, 198.0]
PLATE_Y = 128.0
COLOR_IDS = {"white": 1, "navy": 2}

NOZZLES = {
    "0.2": dict(
        presets=("flat-machine-02.json", "flat-process-02.json", "flat-filament-02.json"),
        layer=0.08, first=0.1, layer_height="0.08", nozzle=["0.2", "0.2"],
        out="fillcore-coupons-02-thin.3mf",
        plate_name="fill-core letter coupons 0.2 thin",
        variants=[
            ("V0", "coupon V0 control - locked recipe, letters 4 arachne walls", None, {}),
            ("V7o", "coupon V7o - letters 1 wall + monotonicline fill, raster core",
             {"wall_loops": "1", "top_one_wall_type": "all top"},
             {"detect_narrow_internal_solid_infill": "0"}),
            ("V3", "coupon V3 - letters 1 wall + monotonic (connected) fill, modifier only",
             {"wall_loops": "1", "top_one_wall_type": "all top", "top_surface_pattern": "monotonic"},
             {}),
        ],
        timing_single="V7o"),
    "0.4": dict(
        presets=("flat-machine.json", "flat-process.json", "flat-filament.json"),
        layer=0.12, first=0.2, layer_height="0.12", nozzle=["0.4", "0.4"],
        out="fillcore-coupons-04.3mf",
        plate_name="fill-core letter coupons 0.4 thin",
        variants=[
            ("C0", "coupon C0 - control - locked recipe, letters 2 arachne walls", None, {}),
            ("C7", "coupon C7 - letters 1 wall + 0.30 fill lines + infill_direction 90, raster core",
             fm.C7_MOD_KEYS, fm.C7_OBJECT_KEYS),
            ("C8", "coupon C8 - letters 1 wall + 0.30 fill lines + infill_direction 0, raster core",
             dict(fm.C7_MOD_KEYS, infill_direction="0"), fm.C7_OBJECT_KEYS),
        ],
        timing_single="C7"),
}


# ----------------------------------------------------------------- geometry
def _extrude(g, z0, z1, dx, dy):
    return fm.extrude(g, z0, z1, dx, dy)


def build_meshes(G, slab):
    """Coupon meshes in coupon mm (window center at xy 0, slab bottom at z 0)."""
    cx, cy = G["center"]
    z_shift = G["banner_top"] - STUB - slab          # tag z -> coupon z: subtract this
    bars = G["frame"].intersection(G["wbox"])
    white_top = unary_union(G["letters"] + _geoms(bars))
    navy2d = G["wbox"].difference(white_top)
    slab_m = _extrude(G["wbox"], 0.0, slab, -cx, -cy)
    tops = _extrude(white_top, slab, G["letter_top"] - z_shift, -cx, -cy)
    white = trimesh.util.concatenate([slab_m, tops])
    navy = _extrude(navy2d, slab, slab + STUB, -cx, -cy)
    mod2d = fm.modifier_2d(G["letters"], MOD_BUFFER)
    mod = _extrude(mod2d, slab + STUB, G["letter_top"] - z_shift + MOD_ABOVE, -cx, -cy)
    for m, n in ((white, "white"), (navy, "navy"), (mod, "modifier")):
        m.merge_vertices()
        m.fix_normals()
        assert m.is_watertight, f"{n} not watertight"
    info = dict(z_shift=z_shift, banner_top=G["banner_top"] - z_shift, letter_top=G["letter_top"] - z_shift,
                height=G["letter_top"] - z_shift, bars=bars, white_top=white_top, navy2d=navy2d, mod2d=mod2d,
                navy_filled=(unary_union(G["navy_mid"]).intersection(G["wbox"]).area, navy2d.area))
    return white, navy, mod, info


def n_layers(nz, height):
    centers = fm.layer_centers(nz["first"], nz["layer"], height)
    return len(centers), centers


def layer_check(nz, boundaries, tag_height):
    """No geometry boundary may sit on a layer slice center (ambiguous
    slice), and the coupon's layer count must have the parity of the real
    tag's (the solid/top fill direction alternates 90 deg per layer)."""
    n, centers = n_layers(nz, boundaries[-1])
    for b in boundaries:
        d = min(abs(b - c) for c in centers)
        assert d > 0.005, f"boundary z {b} on a layer center (d={d:.4f})"
    n_tag, _ = n_layers(nz, tag_height)
    assert n % 2 == n_tag % 2, f"coupon {n} layers vs tag {n_tag}: top-layer fill direction would be swapped"
    return n, n_tag


# ---------------------------------------------------------------- 3MF patch
def assemble(nz, variants, xs, out, tag, work):
    """CLI-assemble the coupons (one object per variant at plate x in xs),
    patch configs + modifier parts, write `out`. Returns the part name map."""
    os.makedirs(work, exist_ok=True)
    G = letter_geometry()
    white, navy, mod, info = build_meshes(G, SLAB[nz["key"]])
    meshes = {"white": white, "navy": navy}
    objects, part_names, mods = [], {}, {}
    for idx, ((label, oname, mkeys, okeys), x) in enumerate(zip(variants, xs), start=1):
        for color, fid in COLOR_IDS.items():
            base = f"{label}-{color}"
            meshes[color].export(f"{work}/{base}.stl")
            objects.append({"path": f"{work}/{base}.stl", "count": 1, "filaments": [fid], "assemble_index": [idx],
                            "pos_x": [x], "pos_y": [PLATE_Y], "pos_z": [0]})
            part_names[base] = f"{label} letters {color}"
        if mkeys:
            mods[label] = (mkeys, x)
    spec = {"plates": [{"plate_name": nz["plate_name"], "need_arrange": False,
                        "plate_params": {"curr_bed_type": BED_TYPE}, "objects": objects,
                        "assembled_params": [{"assemble_index": i, "print_params": okeys}
                                             for i, (_, _, _, okeys) in enumerate(variants, start=1) if okeys]}]}
    spec_path = f"{work}/{tag}-assemble.json"
    with open(spec_path, "w") as f:
        json.dump(spec, f, indent=1)
    raw = f"{work}/{tag}-raw.3mf"
    if os.path.exists(raw):
        os.remove(raw)
    mach, proc, fil = (f"{PIPE}/{p}" for p in nz["presets"])
    cli(["--arrange", "0", "--load-assemble-list", spec_path, "--load-settings", f"{mach};{proc}",
         "--load-filaments", ";".join([fil] * 3), "--export-3mf", os.path.basename(raw), "--outputdir", work],
        work, "assemble")

    bed_temps = fm.read_bed_temps(fil)
    with zipfile.ZipFile(raw) as zin:
        cfg = json.loads(zin.read("Metadata/project_settings.config"))
        assert str(cfg.get("layer_height")) == nz["layer_height"], cfg.get("layer_height")
        assert cfg.get("nozzle_diameter") == nz["nozzle"], cfg.get("nozzle_diameter")
        fm.patch_config(cfg, bed_temps, TOWER)
        assert str(cfg.get("prime_tower_brim_width")) == "5", cfg.get("prime_tower_brim_width")
        assert (str(cfg.get("skirt_loops")), str(cfg.get("skirt_distance")), str(cfg.get("skirt_height"))) == ("2", "3", "1")
        assert cfg.get("print_sequence") == "by layer", cfg.get("print_sequence")

        model = zin.read("Metadata/model_settings.config").decode()
        model3d = zin.read("3D/3dmodel.model").decode()
        objfiles = {n: zin.read(n).decode() for n in zin.namelist() if n.startswith("3D/Objects/")}
        next_id = fm.next_object_id(model3d, objfiles)
        mod_c, mc = fm.centered(mod)             # centered mesh, like the CLI stores parts
        _, white_c = fm.centered(white)          # anchor: the white part is listed first

        def _rename(block):
            m_ = re.search(r'value="([A-Za-z0-9]+)-white_1"', block)
            assert m_, block[:300]
            label = m_.group(1)
            oname = next(o for l, o, _, _ in variants if l == label)
            block = re.sub(r'<metadata key="name" value="assemble_\d+"/>',
                           f'<metadata key="name" value="{oname}"/>', block, count=1)
            for base, friendly in part_names.items():
                block = block.replace(f'value="{base}_1"', f'value="{friendly}"')
            return block, label
        out_blocks = []
        pos = 0
        for m_ in re.finditer(r'<object id="(\d+)">.*?</object>', model, re.S):
            out_blocks.append(model[pos:m_.start()])
            block, label = _rename(m_.group(0))
            oid = m_.group(1)
            if label in mods:
                mkeys, x = mods[label]
                pid = next_id
                next_id += 1
                opos = fm.object_pos(model3d, oid, white_c)
                assert opos == (x, PLATE_Y, 0.0), (label, opos)
                name = f"MOD letters {label}: " + ", ".join(f"{k} {v}" for k, v in mkeys.items())
                block, model3d = fm.inject_modifier(block, model3d, objfiles, oid, pid, name, f"mod-letters-{label}.stl",
                                                    mod_c, mc, opos, mkeys)
                mod_c.export(f"{work}/mod-letters-{label}.stl")
            out_blocks.append(block)
            pos = m_.end()
        out_blocks.append(model[pos:])
        model = "".join(out_blocks)
        assert "assemble_" not in model
        model = model.replace('<metadata key="plater_name" value=""/>', f'<metadata key="plater_name" value="{nz["plate_name"]}"/>')
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "Metadata/project_settings.config":
                    zout.writestr(item, json.dumps(cfg, indent=4))
                elif item.filename == "Metadata/model_settings.config":
                    zout.writestr(item, model)
                elif item.filename == "3D/3dmodel.model":
                    zout.writestr(item, model3d)
                elif item.filename in objfiles:
                    zout.writestr(item, objfiles[item.filename])
                else:
                    zout.writestr(item, zin.read(item.filename))
    os.remove(raw)
    return G, info, part_names


def check_3mf(path, nz, variants, label):
    """Structural asserts on a written/round-tripped plate."""
    with zipfile.ZipFile(path) as z:
        c = json.loads(z.read("Metadata/project_settings.config"))
        assert str(c.get("layer_height")) == nz["layer_height"], (label, c.get("layer_height"))
        assert c.get("nozzle_diameter") == nz["nozzle"], label
        assert c.get("textured_plate_temp") == ["70", "70", "70"], (label, c.get("textured_plate_temp"))
        fm.check_config(c, {"textured_plate_temp": "70"}, TOWER, label=label)
        for k in ("seam_gap", "min_bead_width", "wall_generator", "top_one_wall_type", "skirt_loops", "prime_tower_brim_width"):
            assert k in c["different_settings_to_system"][0], (label, k)
        m = z.read("Metadata/model_settings.config").decode()
        objs = re.findall(r'<object id="(\d+)">(.*?)</object>', m, re.S)
        assert len(objs) == len(variants), f"{label}: {len(objs)} objects"
        summary = []
        for oid, body in objs:
            nm = re.search(r'<metadata key="name" value="([^"]*)"', body).group(1)
            vlabel = nm.split()[1]
            _, oname, mkeys, okeys = next(v for v in variants if v[0] == vlabel)
            assert nm == oname, (label, nm)
            nn, nmod = fm.check_object(body, okeys, mkeys, ["1", "2"], label)
            summary.append((nm, nn, nmod, dict(okeys)))
        assert len(re.findall(r"<model_instance>", m)) == len(variants), f"{label}: plate instance list"
        return summary


def main():
    sys.path.insert(0, PIPE)
    from graft_slice import graft_slice
    nkey = os.environ.get("NOZZLE", "0.2")
    nz = dict(NOZZLES[nkey], key=nkey)
    slab = SLAB[nkey]
    tag = f"thin-{nkey.replace('.', '')}"
    work = f"{SCRATCH}/{tag}"
    os.makedirs(OUT_DIR, exist_ok=True)   # exports/ = experiments area, recreated on demand
    out = f"{OUT_DIR}/{nz['out']}"
    G, info, part_names = assemble(nz, nz["variants"], VARIANT_X, out, tag, work)
    w = G["window"]
    print(f"canonical STLs: disc top {G['disc_top']}, banner top {G['banner_top']}, letter top {G['letter_top']}")
    print("SANTA glyph bboxes (tag mm): " + "; ".join(f"[{b[0]:.3f},{b[1]:.3f},{b[2]:.3f},{b[3]:.3f}]" for b in (l.bounds for l in G["letters"])))
    print(f"crop window (tag mm) x {w[0]:.3f}..{w[2]:.3f}  y {w[1]:.3f}..{w[3]:.3f}  = {w[2]-w[0]:.2f} x {w[3]-w[1]:.2f} mm, center ({G['center'][0]:.4f}, {G['center'][1]:.4f})")
    print(f"excluded white inside the window (area mm2, bbox): " + "; ".join(f"{a:.2f} [{b[0]:.1f},{b[1]:.1f},{b[2]:.1f},{b[3]:.1f}]" for a, b in G["excluded"] if a > 1e-6))
    print(f"bars kept: {sum(p.area for p in _geoms(info['bars'])):.2f} mm2; navy stub {info['navy_filled'][1]:.2f} mm2 "
          f"(real-tag navy in window {info['navy_filled'][0]:.2f} mm2; the difference is the excluded white filled with navy)")
    nl, n_tag = layer_check(nz, [slab, info["banner_top"], info["letter_top"]], G["letter_top"])
    print(f"coupon z (mm): slab 0..{slab}, navy stub ..{info['banner_top']:.2f}, letters ..{info['letter_top']:.2f} = height {info['height']:.2f}; "
          f"{nkey} nozzle grid -> {nl} layers (real tag {n_tag}: same top-layer parity); modifier z {info['banner_top']:.2f}..{info['letter_top']+MOD_ABOVE:.2f}")
    rt = f"{work}/{tag}-rt.3mf"
    if os.path.exists(rt):
        os.remove(rt)
    cli(["--arrange", "0", "--export-3mf", rt, out], work, "round trip")
    for path, label in ((out, "out"), (rt, "round trip")):
        summ = check_3mf(path, nz, nz["variants"], label)
    os.remove(rt)
    print(f"OK  {out}: round trip green; objects:")
    for nm, nn, nm_, ok in summ:
        print(f"    {nm}: {nn} parts + {nm_} modifier, object keys {ok or '-'}")
    res = graft_slice(out, f"{work}/{tag}-sliced.3mf")
    assert res["rc"] == 0 and res["gcode"], res
    assert res["layers"] == nl, (res["layers"], nl)
    print(f"graft slice: rc 0, {res['layers']} layers, total estimated time {res['time']} ({res['seconds']} s); sliced -> {res['out']}")
    # single coupon for the per-coupon time
    sv = next(v for v in nz["variants"] if v[0] == nz["timing_single"])
    single = f"{work}/{tag}-single-{sv[0]}.3mf"
    assemble(nz, [sv], [128.0], single, f"{tag}-single", work)
    check_3mf(single, nz, [sv], "single")
    res1 = graft_slice(single, f"{work}/{tag}-single-sliced.3mf")
    assert res1["rc"] == 0 and res1["gcode"], res1
    print(f"single coupon {sv[0]}: {res1['layers']} layers, total estimated time {res1['time']} ({res1['seconds']} s)")


if __name__ == "__main__":
    main()
