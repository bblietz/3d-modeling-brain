"""Per-feature filament split and A/B layer comparison of a Bambu plate G-code.

Split: filament (mm of 1.75 mm filament, grams from the header density) per
`; FEATURE:` and per tool (T0..T2 = filament 1..3), cross-checked against
the header's `; total filament weight [g]` line.

Compare (--baseline): the letter-tier recipe (fillcore_mod.py) must change
nothing outside the SANTA CRUZ letters. Layers whose top z <= --split-z
(the banner top, 3.96 on the tag) must have identical per-feature totals
(E, path length, segment count); on the layers above, the extrusion
segments with both ends outside the letter outlines buffered by
--zone-buffer must be the same set (feature, coordinates 1e-3, E 1e-5).

Usage: gcode_features.py <sliced.3mf | plate_1.gcode>
         [--baseline <other.3mf | gcode>] [--split-z 3.96] [--zone-buffer 1.0]
         [--x 128 --y 128]    (tag origin on the plate for the letter zone)
"""
import argparse
import math
import os
import re
import sys

from shapely.affinity import translate
from shapely.ops import unary_union

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)
import fillcore_mod as fm  # noqa: E402
from toolpath_voids import load_gcode  # noqa: E402


def header(gcode):
    h = gcode[:6000]
    g = re.search(r"; total filament weight \[g\] : ([^\n]+)", h)
    d = re.search(r"; filament_density: ([^\n]+)", h)
    dia = re.search(r"; filament_diameter: ([^\n]+)", h)
    t = re.search(r"; total estimated time: ([^;\n]+)", h)
    n = re.search(r"; total layer number: (\d+)", h)
    return dict(weights=[float(v) for v in g.group(1).split(",")] if g else None,
                density=[float(v) for v in d.group(1).split(",")], diameter=[float(v) for v in dia.group(1).split(",")],
                time=t.group(1).strip() if t else None, layers=int(n.group(1)) if n else None)


def parse_moves(gcode):
    """Extrusion moves: (z, feature, tool, x0, y0, x1, y1, e). Relative E
    (M83); arcs are taken chord-wise (E is what matters here). The signed
    E of pure-E moves (filament-change flushes, retract/de-retract) and of
    wipe retractions (XY moves with E < 0) is netted into the pseudo
    feature "Flush + retract net"; the purge line before the first layer
    is "Start purge"; so the grand total matches the header weight."""
    moves = []
    x = y = 0.0
    z = None
    feat = "?"
    tool = 0
    for line in gcode.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = round(float(line.split(":")[1]), 3)
        elif line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif re.match(r"T\d+$", line):
            t = int(line[1:])
            if t < 16:
                tool = t
        elif line[:3] in ("G1 ", "G0 ", "G2 ", "G3 "):
            vals = {}
            for p in line.split(";")[0].split()[1:]:
                if p[0] in "XYZE" and len(p) > 1:
                    try:
                        vals[p[0]] = float(p[1:])
                    except ValueError:
                        pass
            nx, ny = vals.get("X", x), vals.get("Y", y)
            e = vals.get("E", 0.0)
            if e > 0 and ("X" in vals or "Y" in vals):
                moves.append((z if z is not None else 0.0, feat if z is not None else "Start purge", tool, x, y, nx, ny, e))
            elif e != 0:
                moves.append((z if z is not None else 0.0, "Flush + retract net", tool, x, y, x, y, e))
            x, y = nx, ny
    return moves


def grams(e_mm, hdr, tool):
    return e_mm * math.pi * (hdr["diameter"][tool] / 2) ** 2 * hdr["density"][tool] / 1000.0


def feature_split(moves, hdr):
    per_feat, per_tool, per_feat_tool = {}, {}, {}
    for z, f, t, x0, y0, x1, y1, e in moves:
        g = grams(e, hdr, t)
        per_feat[f] = per_feat.get(f, 0.0) + g
        per_tool[t] = per_tool.get(t, 0.0) + g
        per_feat_tool[(f, t)] = per_feat_tool.get((f, t), 0.0) + g
    return per_feat, per_tool, per_feat_tool


PSEUDO = ("Flush + retract net", "Start purge")


def layer_totals(moves):
    out = {}
    for z, f, t, x0, y0, x1, y1, e in moves:
        if f in PSEUDO:
            continue
        d = out.setdefault(z, {}).setdefault(f, [0.0, 0.0, 0])
        d[0] += e
        d[1] += math.hypot(x1 - x0, y1 - y0)
        d[2] += 1
    return out


def compare(moves_a, moves_b, split_z, zone):
    """Returns (below_diffs, tier_report). below_diffs: list of (z, feature,
    dE, dLen, dN) for layers with z <= split_z. tier_report: per layer above,
    (z, n_only_a, n_only_b, dE_outside) for segments outside the zone."""
    ta, tb = layer_totals(moves_a), layer_totals(moves_b)
    below = []
    for z in sorted(set(ta) | set(tb)):
        if z > split_z + 1e-6:
            continue
        for f in sorted(set(ta.get(z, {})) | set(tb.get(z, {}))):
            a, b = ta.get(z, {}).get(f, [0, 0, 0]), tb.get(z, {}).get(f, [0, 0, 0])
            if abs(a[0] - b[0]) > 1e-5 or abs(a[1] - b[1]) > 1e-3 or a[2] != b[2]:
                below.append((z, f, a[0] - b[0], a[1] - b[1], a[2] - b[2]))
    from shapely.geometry import Point

    def outside(m):
        return not (zone.intersects(Point(m[3], m[4])) or zone.intersects(Point(m[5], m[6])))

    def key(m):
        return (m[1], m[2], round(m[3], 3), round(m[4], 3), round(m[5], 3), round(m[6], 3), round(m[7], 5))
    tier = []
    for z in sorted(set(ta) | set(tb)):
        if z <= split_z + 1e-6:
            continue
        sa = {}
        sb = {}
        for src, dst in ((moves_a, sa), (moves_b, sb)):
            for m in src:
                if m[0] == z and m[1] not in PSEUDO and outside(m):
                    dst[key(m)] = dst.get(key(m), 0) + 1
        only_a = sum(max(0, n - sb.get(k, 0)) for k, n in sa.items())
        only_b = sum(max(0, n - sa.get(k, 0)) for k, n in sb.items())
        de = sum(k[6] * n for k, n in sa.items()) - sum(k[6] * n for k, n in sb.items())
        tier.append((z, only_a, only_b, de, len(sa), len(sb)))
    return below, tier


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--baseline")
    ap.add_argument("--split-z", type=float, default=3.96)
    ap.add_argument("--zone-buffer", type=float, default=1.0)
    ap.add_argument("--x", type=float, default=128.0)
    ap.add_argument("--y", type=float, default=128.0)
    a = ap.parse_args()
    g = load_gcode(a.path)
    hdr = header(g)
    moves = parse_moves(g)
    per_feat, per_tool, per_ft = feature_split(moves, hdr)
    total = sum(per_feat.values())
    print(f"{os.path.basename(a.path)}: {hdr['layers']} layers, {hdr['time']}, header weight {hdr['weights']} g "
          f"= {sum(hdr['weights']):.2f}; parsed extrusion {total:.2f} g (white {per_tool.get(0, 0):.2f}, "
          f"navy {per_tool.get(1, 0):.2f}, cyan {per_tool.get(2, 0):.2f})")
    print(f"{'feature':26} {'g':>7} {'share':>6}   white / navy / cyan g")
    for f, gr in sorted(per_feat.items(), key=lambda kv: -kv[1]):
        print(f"{f:26} {gr:7.2f} {gr / total * 100:5.1f}%   "
              + " / ".join(f"{per_ft.get((f, t), 0):.2f}" for t in (0, 1, 2)))
    if a.baseline:
        gb = load_gcode(a.baseline)
        hb = header(gb)
        mb = parse_moves(gb)
        print(f"\nbaseline {os.path.basename(a.baseline)}: {hb['layers']} layers, {hb['time']}, header weight {hb['weights']} g")
        G = fm.letter_geometry(fm.BANNER_BOX, 9, window_checks=False)
        zone = translate(unary_union(G["letters"]).buffer(a.zone_buffer), a.x, a.y)
        below, tier = compare(moves, mb, a.split_z, zone)
        nb = len({z for z, *_ in below})
        print(f"layers with top z <= {a.split_z}: {'IDENTICAL per-feature totals' if not below else f'{nb} layers differ'}")
        for z, f, de, dl, dn in below[:40]:
            print(f"    z {z:.2f} {f:24} dE {de:+.4f} mm  dLen {dl:+.2f} mm  dN {dn:+d}")
        if len(below) > 40:
            print(f"    ... {len(below) - 40} more")
        print(f"layers above (letter tier), segments outside the letters + {a.zone_buffer} mm:")
        for z, oa, ob, de, na, nb_ in tier:
            print(f"    z {z:.2f}: {na} vs {nb_} segments, only in A {oa}, only in B {ob}, dE {de:+.4f} mm")


if __name__ == "__main__":
    main()
