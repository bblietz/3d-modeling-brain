"""Round the mouth's rim: the edge where the wand cavity breaks out through the holder's skin.

The rim is a 3D curve across the drum and the blend under the flange, and its wedge angle runs from about 20 degrees
(roof lip) to over 110 (floor lip), so it gets a true rolling-ball roundover: a ball of edge_r touching both the skin
and the cavity wall.  This script finds the curve the ball's centre follows (the rim of "body shrunk by edge_r minus
cavity grown by edge_r", cut by OpenSCAD itself), and at stations along it the two points where the ball touches and
the sharp edge point between them.  holder.scad cuts the kite edge-touch-centre-touch away between stations and puts
the balls back (rim_round.scad: rim_O centres, rim_E edge points, rim_TB / rim_TC touch points on the skin / the cavity
wall, rim_next the following station or -1 at the end of a run).

Rerun after any change to the cavity, the drum, the blends or edge_r:
    .venv/bin/python projects/NACS-wall-holder/pipeline/rim_round.py
"""
import os
import re
import subprocess
import tempfile

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
OPENSCAD = os.path.expanduser("~/.local/bin/openscad")
SRC = open(f"{PROJECT}/holder.scad").read()
const = lambda k: float(re.search(rf"(?:^|;)\s*{k}\s*=\s*([-0-9.]+)", SRC, re.M).group(1))
FN = int(const(r"\$fn"))
STEP = 0.8          # station spacing along the rim, mm
FLAT = 170.0        # wedges opener than this are not edges (the solve below also runs out of leverage there)
PUSH = 0.4          # the cut's touch-point corners go this far out into the air, so no cut face lies in a surface
PUSH_E = 3.0        # and its edge corner this far: the walls are creased, so the real edge is not exactly where two flat faces would meet


def scad(tmp, name, body):
    with open(f"{tmp}/{name}.scad", "w") as f:
        f.write(f"use <{PROJECT}/holder.scad>\n$fn = {FN};\n{body}\n")      # `use` does not bring holder.scad's $fn along, and the facets must match
    r = subprocess.run([OPENSCAD, "--backend=Manifold", "-o", f"{tmp}/{name}.stl", f"{tmp}/{name}.scad"], capture_output=True, text=True)
    assert os.path.exists(f"{tmp}/{name}.stl"), r.stderr[-2000:]
    return trimesh.load(f"{tmp}/{name}.stl")


def rim_loops(solid, skin, wall):
    """Edges of `solid` between a face lying on `skin` and one lying on `wall`, chained into polylines."""
    c = solid.triangles_center
    on_wall = trimesh.proximity.closest_point(wall, c)[1] < trimesh.proximity.closest_point(skin, c)[1]
    pairs, edges = solid.face_adjacency, solid.face_adjacency_edges
    rim = edges[on_wall[pairs[:, 0]] != on_wall[pairs[:, 1]]]
    nbr = {}
    for a, b in rim:
        nbr.setdefault(a, []).append(b)
        nbr.setdefault(b, []).append(a)
    loops, seen = [], set()
    for start in nbr:
        if start in seen:
            continue
        loop, prev, cur = [start], None, start
        seen.add(start)
        while True:
            nxt = [n for n in nbr[cur] if n != prev and (n not in seen or (n == start and len(loop) > 2))]
            if not nxt or nxt[0] == start:
                break
            prev, cur = cur, nxt[0]
            seen.add(cur)
            loop.append(cur)
        loops.append(solid.vertices[loop])
    return loops


def resample(loop, step):
    p = np.vstack([loop, loop[:1]])
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    n = max(8, int(round(s[-1] / step)))
    t = np.linspace(0, s[-1], n, endpoint=False)
    q = np.column_stack([np.interp(t, s, p[:, k]) for k in range(3)])
    return (np.roll(q, 1, axis=0) + 2 * q + np.roll(q, -1, axis=0)) / 4        # light smoothing of the mesh's facet noise


def main():
    plate_t = const("plate_t")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([OPENSCAD, "-o", f"{tmp}/h.echo", f"{PROJECT}/holder.scad"], capture_output=True, text=True)
        rho = float(re.search(r"edge_r=([-0-9.]+)", open(f"{tmp}/h.echo").read()).group(1))
        body = scad(tmp, "body", "body();")
        cav = scad(tmp, "cav", "cavity_cut();")
        cav_g = scad(tmp, "cav_g", f"cavity_cut({rho});")
        # the body shrunk by rho: the turned profile with the plate as a disc carried on down past the wall, so only the mouth shows up
        inset = (f"rotate_extrude() intersection() {{ offset(r = -{rho}) for (m = [0, 1]) mirror([m, 0]) "
                 f"{{ drum_profile(); translate([0, -20]) square([70, 20 + {plate_t}]); }} translate([0, -50]) square([200, 300]); }}")
        body_g = scad(tmp, "body_g", inset)
        core = scad(tmp, "core", f"difference() {{ {inset} cavity_cut({rho}); }}")
    O, E, TB, TC, nxt, angles, err = [], [], [], [], [], [], []
    for loop in rim_loops(core, body_g, cav_g):
        if len(loop) < 8:
            continue
        o = resample(loop, STEP)
        for _ in range(4):                                                     # settle each centre at rho from the skin and rho from the wall
            tb, db, _ = trimesh.proximity.closest_point(body, o)
            tc, dc, _ = trimesh.proximity.closest_point(cav, o)
            mb, mc = (o - tb) / db[:, None], (o - tc) / dc[:, None]
            c = np.clip(np.einsum("ij,ij->i", mb, mc), -0.98, 0.98)
            x = ((rho - db) - c * (rho - dc)) / (1 - c * c)
            y = ((rho - dc) - c * (rho - db)) / (1 - c * c)
            o = o + x[:, None] * mb + y[:, None] * mc
        tb, db, _ = trimesh.proximity.closest_point(body, o)
        tc, dc, _ = trimesh.proximity.closest_point(cav, o)
        mb, mc = (o - tb) / db[:, None], (o - tc) / dc[:, None]
        c = np.einsum("ij,ij->i", mb, mc)
        wedge = 180 - np.degrees(np.arccos(np.clip(c, -1, 1)))                  # the material's angle at the edge
        ok = wedge < FLAT
        e = o - rho * (mb + mc) / (1 + c)[:, None]
        bis = (mb + mc) / np.linalg.norm(mb + mc, axis=1)[:, None]
        base = len(O)
        n = len(o)
        for i in range(n):
            j = (i + 1) % n
            O.append(o[i]); E.append(e[i] - PUSH_E * bis[i]); TB.append(tb[i] - PUSH * mb[i]); TC.append(tc[i] - PUSH * mc[i])
            nxt.append(base + j if ok[i] and ok[j] else -1)
        angles += list(wedge[ok]); err += list(np.abs(db[ok] - rho)) + list(np.abs(dc[ok] - rho))
        print(f"loop: {n} stations, {ok.sum()} rounded, length {n * STEP:.0f} mm, z {o[:, 2].min():.1f}..{o[:, 2].max():.1f}")
    fmt = lambda a: "[" + ", ".join("[%.3f, %.3f, %.3f]" % tuple(p) for p in a) + "]"
    with open(f"{PROJECT}/rim_round.scad", "w") as f:
        f.write("// Rolling-ball roundover of the mouth's rim, generated by pipeline/rim_round.py: do not edit.\n")
        f.write(f"// edge_r {rho:.4f}; ball centres, edge points (pushed {PUSH_E} mm out into the air) and touch points (pushed {PUSH}), world frame.\n")
        f.write(f"rim_O = {fmt(O)};\nrim_E = {fmt(E)};\nrim_TB = {fmt(TB)};\nrim_TC = {fmt(TC)};\nrim_next = {list(map(int, nxt))};\n")
    print(f"{len(O)} stations, {sum(1 for k in nxt if k >= 0)} links; wedge angle {min(angles):.0f}..{max(angles):.0f} deg; "
          f"ball off its two surfaces by at most {max(err):.3f} mm")


if __name__ == "__main__":
    main()
