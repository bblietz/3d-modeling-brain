"""Build Bambu Studio project 3MFs for the helm panel tiles and keys.

Why this exists: `bambu-studio --export-3mf` writes a project whose
`curr_bed_type` is "Cool Plate". For ASA that resolves to a 0 C bed and the
print will not stick at all (for PLA it is 30 C too cold and the edges peel,
which is the Sharks-nametag failure recorded in knowledge/printer-x2d.md).
The CLI also leaves the object wherever --arrange put it, which for a part
this size lands off the plate and makes the slicer report an empty plate.

So each plate is built, then patched, then verified by an actual slice.
Any key changed inside a project 3MF must also appear in
`different_settings_to_system`, or Studio's GUI silently resets it on open.

Usage:  python3 projects/Garmin-943-helm-panel/make_plate.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Sharks-nametag", "pipeline"))
from graft_slice import graft_slice  # noqa: E402
ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")
OUT = HERE

MACHINE = "Bambu Lab X2D 0.6 nozzle"
PROCESS = "0.30mm Standard @BBL X2D 0.6 nozzle"
FILAMENT = "Bambu ASA @BBL X2D"

BED_CENTRE = (128.0, 128.0)

# what we override, and the diff slot each key belongs in (0 = process)
OVERRIDES = {
    "curr_bed_type": "Textured PEI Plate",
    "brim_type": "outer_only",
    "brim_width": "5",
}

JOBS = {
    "helm-panel-tile-TL": ["helm-panel-tile-TL.stl"],
    "helm-panel-tile-TR": ["helm-panel-tile-TR.stl"],
    "helm-panel-tile-BL": ["helm-panel-tile-BL.stl"],
    "helm-panel-tile-BR": ["helm-panel-tile-BR.stl"],
    "helm-panel-keys": ["helm-panel-key.stl"] * 10,
}


def load(kind, name):
    with open(f"{ROOT}/{kind}/{name}.json") as f:
        return json.load(f)


def flatten(kind, name):
    """Resolve the inherits chain; the CLI cannot do this for X2D presets."""
    chain = [load(kind, name)]
    while "inherits" in chain[-1]:
        chain.append(load(kind, chain[-1]["inherits"]))
    merged = {}
    for layer in reversed(chain):
        merged.update(layer)
    merged.pop("inherits", None)
    merged["name"] = name
    return merged


def write_presets(d):
    for kind, name, fn in (
        ("machine", MACHINE, "machine.json"),
        ("process", PROCESS, "process.json"),
        ("filament", FILAMENT, "filament.json"),
    ):
        with open(f"{d}/{fn}", "w") as f:
            json.dump(flatten(kind, name), f)


def cli(args, cwd):
    return subprocess.run(
        ["bambu-studio", *args], cwd=cwd, capture_output=True, text=True, timeout=1800
    )


def patch(src, dst, n_objects, label=None):
    """Centre the build items on the plate and apply the overrides."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)

            if item.filename == "3D/3dmodel.model":
                s = data.decode()
                items = re.findall(r'<item [^>]*?transform="([^"]*)"', s)
                assert len(items) == n_objects, (len(items), n_objects)
                if n_objects == 1:
                    s = re.sub(
                        r'(<item [^>]*?)transform="[^"]*"',
                        r'\1transform="1 0 0 0 1 0 0 0 1 %g %g 0"' % BED_CENTRE,
                        s,
                        count=1,
                    )
                else:
                    # keep the CLI's relative layout, shift its centroid to the middle
                    xs = [float(t.split()[9]) for t in items]
                    ys = [float(t.split()[10]) for t in items]
                    dx = BED_CENTRE[0] - (min(xs) + max(xs)) / 2
                    dy = BED_CENTRE[1] - (min(ys) + max(ys)) / 2

                    def shift(m):
                        p = m.group(2).split()
                        p[9] = "%g" % (float(p[9]) + dx)
                        p[10] = "%g" % (float(p[10]) + dy)
                        return '%stransform="%s"' % (m.group(1), " ".join(p))

                    s = re.sub(r'(<item [^>]*?)transform="([^"]*)"', shift, s)
                data = s.encode()

            elif item.filename == "Metadata/project_settings.config":
                cfg = json.loads(data)
                for k, v in OVERRIDES.items():
                    cfg[k] = v
                diff = cfg.get("different_settings_to_system") or [""]
                existing = [x for x in diff[0].split(";") if x]
                diff[0] = ";".join(sorted(set(existing) | set(OVERRIDES)))
                cfg["different_settings_to_system"] = diff
                data = json.dumps(cfg, indent=4).encode()

            elif item.filename == "Metadata/model_settings.config" and label:
                # the CLI names objects after the input file; ours are temp
                # copies, so give Studio something readable instead
                s = data.decode()
                s = re.sub(r'value="copy(\d+)_[^"]*\.stl"',
                           lambda m: 'value="%s%s"' % (label, "" if n_objects == 1 else " %d" % (int(m.group(1)) + 1)),
                           s)
                data = s.encode()

            zout.writestr(item, data)
    zin.close()


def verify(path, tmp):
    """Slice it for real. A CLI round trip alone does not prove sliceability."""
    z = zipfile.ZipFile(path)
    cfg = json.loads(z.read("Metadata/project_settings.config"))
    for k, v in OVERRIDES.items():
        assert cfg[k] == v, f"{k} did not stick: {cfg[k]}"
    assert set(OVERRIDES) <= set(cfg["different_settings_to_system"][0].split(";"))

    # The CLI cannot slice its own project files: the live X2D extruder and
    # variant keys are only written by the GUI, so a bare --slice returns 156.
    # graft_slice adds just those missing keys to a throwaway copy. Studio
    # itself resolves them on open, so the shipped file stays unpatched.
    out = f"{tmp}/sliced.3mf"
    res = graft_slice(path, out)
    if res.get("rc") != 0 or not os.path.exists(out):
        return {"sliced": False, "rc": res.get("rc"), "log": res.get("log")}
    info = zipfile.ZipFile(out).read("Metadata/slice_info.config").decode()
    grab = lambda k: (re.search(rf'key="{k}" value="([^"]*)"', info) or [None, "?"])[1]
    return {
        "sliced": True,
        "minutes": round(int(grab("prediction")) / 60),
        "grams": round(float(grab("weight"))),
    }


def main():
    results = {}
    for name, parts in JOBS.items():
        with tempfile.TemporaryDirectory() as tmp:
            write_presets(tmp)
            stls = []
            for i, p in enumerate(parts):
                # one physical file per bed instance: filament ids map per input
                dup = f"copy{i}_{p}"
                shutil.copy(f"{HERE}/{p}", f"{tmp}/{dup}")
                stls.append(dup)

            # --export-3mf must be a bare filename; an absolute path alongside
            # --outputdir makes the CLI exit 243 without writing anything.
            raw = f"{tmp}/raw.3mf"
            r = cli(
                ["--arrange", "1",
                 "--load-settings", "machine.json;process.json",
                 "--load-filaments", "filament.json",
                 "--export-3mf", "raw.3mf", "--outputdir", ".", *stls],
                tmp,
            )
            assert os.path.exists(raw), f"{name}: CLI export failed rc={r.returncode}"

            final = f"{OUT}/{name}.3mf"
            patch(raw, final, len(parts), label=name.replace("helm-panel-", "").replace("-", " "))
            results[name] = verify(final, tmp)
            print(f"{name}: {results[name]}")

    ok = all(v.get("sliced") for v in results.values())
    print("\nall plates slice:", ok)
    if ok:
        print("total print time: %d h %d min" % divmod(sum(v["minutes"] for v in results.values()), 60))
        print("total filament: %d g" % sum(v["grams"] for v in results.values()))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
