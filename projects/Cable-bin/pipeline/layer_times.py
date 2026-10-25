"""Per-layer print time of one plate of a Bambu project 3MF, from the M73 remaining-time marks in a real slice.

Usage:  .venv/bin/python projects/Cable-bin/pipeline/layer_times.py <project.3mf> <plate> <outdir> [z edges ...]
Slices the plate through graft_slice into <outdir>, then reads the first "M73 P.. R.." after every "; Z_HEIGHT:"
in the G-code: R is the remaining time in whole minutes, so single layers are coarse but bands of layers are
good. Prints seconds and layers per z band (default edges 18 and 82) and writes <outdir>/layers.csv.
"""
import os
import re
import sys
import zipfile

sys.path.insert(0, "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Sharks-nametag/pipeline")
from graft_slice import graft_slice  # noqa: E402


def main():
    src, plate, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    edges = [float(e) for e in sys.argv[4:]] or [18.0, 82.0]
    os.makedirs(out, exist_ok=True)
    res = graft_slice(src, f"{out}/sliced.3mf", plate=plate)
    assert res["rc"] == 0 and res.get("gcode"), res
    g = zipfile.ZipFile(f"{out}/sliced.3mf").read(res["gcode"]).decode(errors="replace")
    layers = []                       # [z, remaining minutes at the layer's first M73]
    for line in g.splitlines():
        m = re.match(r"; Z_HEIGHT: ([\d.]+)", line)
        if m:
            layers.append([float(m.group(1)), None])
            continue
        m = re.match(r"M73 P\d+ R(\d+)", line)
        if m and layers and layers[-1][1] is None:
            layers[-1][1] = int(m.group(1))
    layers = [l for l in layers if l[1] is not None]
    assert len(layers) > 10, "no layer marks found"
    rows = []
    for i, (z, r) in enumerate(layers):
        nxt = layers[i + 1][1] if i + 1 < len(layers) else 0
        rows.append((z, 60 * (r - nxt)))
    with open(f"{out}/layers.csv", "w") as f:
        f.write("z_mm,seconds\n" + "".join(f"{z:.2f},{s}\n" for z, s in rows))
    bands = [(-1.0, edges[0])] + [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)] + [(edges[-1], 1e9)]
    total = sum(s for _, s in rows)
    print(f"{os.path.basename(src)} plate {plate}: {len(rows)} layers, {total/3600:.2f} h from the M73 marks "
          f"(header says {res.get('time')})")
    for lo, hi in bands:
        sel = [s for z, s in rows if lo < z <= hi]
        if sel:
            print(f"  z {max(lo,0):5.1f} to {min(hi, rows[-1][0]):5.1f}: {len(sel):3d} layers, {sum(sel)/60:6.1f} min, "
                  f"{sum(sel)/len(sel):5.1f} s per layer")


if __name__ == "__main__":
    main()
