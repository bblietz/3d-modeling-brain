"""Build ONE Bambu project 3MF holding every helm-panel plate.

Why not two plates, one per half: two tiles do fit a 256 mm bed, but only as
DIAGONAL pairs (TL+BR, TR+BL) at 248 x 247 mm, which leaves 4 mm of bed margin
and 0.5 mm between the parts. Top/bottom and left/right pairs do not fit at
all. ASA on a 235 mm flat part needs a brim, and there is no room for one, so
each tile gets its own plate and the keys share the last one.

The CLI cannot author plates, so this rewrites a single-plate export:
  * 3D/3dmodel.model      - each build item moved into its plate's grid cell
  * model_settings.config - one <plate> block per plate, listing its objects

Verified by a CLI round trip AND a real slice of every plate. Opening the file
in Studio is still the ground truth: a hand-authored plate has passed a round
trip before and rendered empty in the GUI.

Usage:  python3 projects/Garmin-943-helm-panel/make_multiplate.py
"""
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_plate import OVERRIDES, cli, write_presets, graft_slice  # noqa: E402

PLATE_STRIDE = 256 * 1.2  # 307.2
PLATE_COLS = 2
# Studio lays plates out in a TWO-COLUMN grid whose rows run in NEGATIVE Y,
# not in a single row along X. Probed 2026-09-09 by round-tripping the same
# four objects under three candidate layouts: a row of four and a +Y grid both
# came back with plates 3 and 4 empty; the -Y grid came back with all four
# populated. A single row is indistinguishable from this for the first two
# plates, which is why the vault had recorded it that way.


def plate_origin(p):
    """Bed origin offset of plate p, 0-indexed."""
    return (p % PLATE_COLS) * PLATE_STRIDE, -(p // PLATE_COLS) * PLATE_STRIDE
BED = 256.0
OUT = f"{HERE}/helm-panel-all-plates.3mf"

TILE_H = 146.05
KEY_W, KEY_H = 35.6, 19.5

# plate -> list of (source stl, label, x, y) in plate-local bed coordinates
def layout():
    plates = []
    for name in ("TL", "TR", "BL"):
        plates.append([(f"helm-panel-tile-{name}.stl", f"tile {name}", 128.0, 128.0)])

    # last plate: tile BR low on the bed, the ten keys in two rows above it
    last = [("helm-panel-tile-BR.stl", "tile BR", 128.0, 10.0 + TILE_H / 2)]
    for i in range(10):
        row, col = divmod(i, 5)
        # 46 mm pitch keeps a 10 mm gap so neighbouring brims never fuse
        last.append(("helm-panel-key.stl", f"key {i + 1}", 36.0 + col * 46.0, 180.0 + row * 35.0))
    plates.append(last)
    return plates


def check_layout(plates):
    """No part off the bed, and nothing closer than a brim's width."""
    boxes = []
    for p, items in enumerate(plates):
        pb = []
        for stl, label, x, y in items:
            w, h = (KEY_W, KEY_H) if "key" in stl else (234.95, TILE_H)
            b = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            assert b[0] > 5 and b[1] > 5 and b[2] < BED - 5 and b[3] < BED - 5, (label, b)
            pb.append((label, b))
        for i in range(len(pb)):
            for j in range(i + 1, len(pb)):
                (la, a), (lb, b) = pb[i], pb[j]
                gap_x = max(a[0] - b[2], b[0] - a[2])
                gap_y = max(a[1] - b[3], b[1] - a[3])
                assert max(gap_x, gap_y) >= 10.0, f"plate {p+1}: {la} and {lb} only {max(gap_x,gap_y):.1f} mm apart"
        boxes.append(pb)
    return boxes


def author(raw, dst, plates):
    zin = zipfile.ZipFile(raw)
    model = zin.read("3D/3dmodel.model").decode()
    msc = zin.read("Metadata/model_settings.config").decode()

    flat = [it for pl in plates for it in pl]

    # The CLI does not keep objects in input order, so map each object id by
    # the copyNN_ prefix baked into its source filename rather than by
    # document position. Getting this wrong silently scatters parts across
    # the wrong plates.
    pairs = re.findall(r'<object id="(\d+)">.*?value="copy(\d+)_[^"]*"', msc, re.S)
    assert len(pairs) == len(flat), (len(pairs), len(flat))
    by_index = {int(idx): oid for oid, idx in pairs}
    assert sorted(by_index) == list(range(len(flat))), sorted(by_index)
    obj_ids = [by_index[i] for i in range(len(flat))]

    # place every build item: plate offset in X, layout position on the bed
    pos = {}
    n = 0
    for p, items in enumerate(plates):
        ox, oy = plate_origin(p)
        for _, label, x, y in items:
            pos[obj_ids[n]] = (ox + x, oy + y, label)
            n += 1

    def move(m):
        head, tr = m.group(1), m.group(2).split()
        oid = re.search(r'objectid="(\d+)"', head).group(1)
        x, y, _ = pos[oid]
        tr[9], tr[10] = "%g" % x, "%g" % y
        return '%stransform="%s"' % (head, " ".join(tr))

    model, moved = re.subn(r'(<item [^>]*?)transform="([^"]*)"', move, model)
    assert moved == len(flat), (moved, len(flat))

    # rename objects, then replace the single plate block with one per plate
    for oid, (_, _, label) in pos.items():
        msc = re.sub(
            r'(<object id="%s">\s*<metadata key="name" value=")[^"]*(")' % oid,
            r"\g<1>%s\g<2>" % label, msc, count=1,
        )

    tpl = re.search(r"  <plate>.*?</plate>\n", msc, re.S).group(0)
    keep = [l for l in tpl.splitlines() if "<metadata" in l and "plater_id" not in l]
    ident = 1000
    blocks = []
    n = 0
    for p, items in enumerate(plates):
        b = ["  <plate>", '    <metadata key="plater_id" value="%d"/>' % (p + 1), *keep]
        for _ in items:
            ident += 11
            b += [
                "    <model_instance>",
                '      <metadata key="object_id" value="%s"/>' % obj_ids[n],
                '      <metadata key="instance_id" value="0"/>',
                '      <metadata key="identify_id" value="%d"/>' % ident,
                "    </model_instance>",
            ]
            n += 1
        b.append("  </plate>")
        blocks.append("\n".join(b) + "\n")
    msc = msc.replace(tpl, "".join(blocks))

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                data = model.encode()
            elif item.filename == "Metadata/model_settings.config":
                data = msc.encode()
            elif item.filename == "Metadata/project_settings.config":
                cfg = json.loads(data)
                cfg.update(OVERRIDES)
                diff = cfg.get("different_settings_to_system") or [""]
                diff[0] = ";".join(sorted(set(x for x in diff[0].split(";") if x) | set(OVERRIDES)))
                cfg["different_settings_to_system"] = diff
                data = json.dumps(cfg, indent=4).encode()
            zout.writestr(item, data)
    zin.close()


def main():
    plates = layout()
    boxes = check_layout(plates)
    for i, pb in enumerate(boxes):
        print("plate %d: %s" % (i + 1, ", ".join(l for l, _ in pb)))

    flat = [it for pl in plates for it in pl]
    with tempfile.TemporaryDirectory() as tmp:
        write_presets(tmp)
        names = []
        for i, (stl, label, _, _) in enumerate(flat):
            dup = "copy%02d_%s" % (i, stl)
            shutil.copy(f"{HERE}/{stl}", f"{tmp}/{dup}")
            names.append(dup)

        r = cli(["--arrange", "0",
                 "--load-settings", "machine.json;process.json",
                 "--load-filaments", "filament.json",
                 "--export-3mf", "raw.3mf", "--outputdir", ".", *names], tmp)
        assert os.path.exists(f"{tmp}/raw.3mf"), f"CLI export failed rc={r.returncode}"

        author(f"{tmp}/raw.3mf", OUT, plates)

        # round trip: does Studio's own reader keep every plate?
        rt = cli(["--arrange", "0", "--export-3mf", "rt.3mf", "--outputdir", ".", OUT], tmp)
        assert os.path.exists(f"{tmp}/rt.3mf"), f"round trip failed rc={rt.returncode}"
        got = zipfile.ZipFile(f"{tmp}/rt.3mf").read("Metadata/model_settings.config").decode()
        filled = [len(re.findall(r"object_id", m.group(1)))
                  for m in re.finditer(r"<plate>(.*?)</plate>", got, re.S)]
        want = [len(pl) for pl in plates]
        print("\nStudio reads objects per plate as %s, expected %s" % (filled, want))
        # an empty plate here is the documented failure mode: the file round
        # trips cleanly and then renders blank in the GUI
        assert filled == want, "Studio did not put the objects on the plates we authored"

        # and does every plate actually slice?
        total_min = total_g = 0
        for p in range(1, len(plates) + 1):
            out = f"{tmp}/s{p}.3mf"
            res = graft_slice(OUT, out, plate=p)
            assert res.get("rc") == 0 and os.path.exists(out), f"plate {p} will not slice: {res}"
            info = zipfile.ZipFile(out).read("Metadata/slice_info.config").decode()
            grab = lambda k: re.search(rf'key="{k}" value="([^"]*)"', info).group(1)
            mins, g = round(int(grab("prediction")) / 60), round(float(grab("weight")))
            total_min += mins
            total_g += g
            print("  plate %d slices: %d min, %d g" % (p, mins, g))

    print("\n%s" % OUT)
    print("total %d h %02d min, %d g" % (*divmod(total_min, 60), total_g))
    return 0


if __name__ == "__main__":
    sys.exit(main())
