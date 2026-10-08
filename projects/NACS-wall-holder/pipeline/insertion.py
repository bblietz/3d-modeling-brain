"""Does the wand dock over the fixed cleat, and does it stay there?

Side-view kinematics: slide along the wand, lift toward the roof, tilt about the across axis.  The holder
(holder.scad, as modelled, plus any name=value overrides) and Tesla's real connector housing are cut in side view at
several offsets across the wand; a pose is free when no slice collides.  Two questions:

  WAY IN  a collision-free path from outside to the docked pose, with the wand grown by --margin (default 0.2 mm)
          so a path that only exists on paper does not count.
  HOLD    let the wand settle from the docked pose under its load (grip and cable, taken at LOAD mm from the tip),
          then find the lowest pass out: how far the load has to be RAISED against gravity before the wand can come
          off the cleat by itself.  0 means it works its way out on its own.  No friction, so this is the safe side.

    .venv/bin/python projects/NACS-wall-holder/pipeline/insertion.py [name=value ...] [--margin 0.2] [--png out.png]

Background (2026-09-18): with a step roof and the wand docked by lifting it over the cleat, the docking motion is the
load's own lever-off motion in reverse, so no tight-roof length both lets the wand in and holds it.
"""
import heapq
import itertools
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import shapely
import trimesh
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.ops import polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
SCAD = open(f"{PROJECT}/holder.scad").read()
OPENSCAD = os.path.expanduser("~/.local/bin/openscad")
TIP_X, CY, CZ = -1.99, 4.0, 4.25          # Tesla housing STL: nose tip in X, nose centre in Y (across) and Z (button side up)
HOUSING_END = 48.2                        # beyond this the grip is holder.scad's own taper
W = [0, 2.5, 4.5, 8, 12, 16, 19]          # side-view slices, mm across the wand from the centre plane (the wand is symmetric)
REF = (17.03, -17.76)                     # pose reference on the wand: the pocket's tip-side corner at the nose's lowest line
DA, DY, DT = 0.25, 0.125, 0.5             # grid: along, lift (mm), tilt (deg)
SKIN = 0.05                               # contact closer than this is not a collision (HOLD uses the bare wand less this)
GOAL_TIP = 72.0                           # nose tip this far from the end wall: the wand is out (past the mouth: 69.1 mm deep since the 1.75 in cleat depth of 2026-10-08; was 45 for the 1.25 in cavity)
LOAD = (150.0, 0.0)                       # where the hanging weight acts on the wand: along from the tip, up from the nose centre
J_RANGE, K_RANGE = (-8, 160), (-36, 44)   # lift -1..20 mm, tilt -18..22 deg


def const(name, over):
    if name in over:
        return float(over[name])
    return float(re.search(rf"(?:^|;)\s*{name}\s*=\s*([-0-9.]+)", SCAD, re.M).group(1))


def loops_xor(section, to_ay):
    region = Polygon()
    for ent in section.discrete:
        p = Polygon([to_ay(q) for q in ent])
        if p.area > 1e-4:
            region = region.symmetric_difference(p if p.is_valid else p.buffer(0))
    return region


def holder_slices(over, tmp):
    defs = {"display": "false", "show_nose": "false", "show_wall": "false", "show_logo": "false", **over}
    cmd = [OPENSCAD, "--backend=Manifold"] + [x for k, val in defs.items() for x in ("-D", f"{k}={val}")] + ["-o", f"{tmp}/h.stl", f"{PROJECT}/holder.scad"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    echo = r.stderr + r.stdout
    vec = lambda k: np.array([float(x) for x in re.search(k + r"=\[([^\]]*)\]", echo).group(1).split(",")])
    d, v, w, T = vec(" d"), vec(" v"), vec(" w"), vec(" T")
    mesh = trimesh.load(f"{tmp}/h.stl")
    mesh.vertices = (mesh.vertices - T) @ np.array([w, v, d]).T      # world -> cavity frame (across, up, along)
    window = box(-25, -70, 150, 70)
    return {wv: loops_xor(mesh.section(plane_origin=[wv, 0, 0], plane_normal=[1, 0, 0]), lambda q: (q[2], q[1])).intersection(window) for wv in W}


def handle_slices(tmp):
    """Tesla's housing to HOUSING_END, then holder.scad's grip taper; wand frame: tip at a=0, nose centre y=0."""
    mesh = trimesh.load(f"{PROJECT}/reference/nacs-500v-connector-housing.stl")
    with open(f"{tmp}/handle.scad", "w") as f:
        f.write(f"use <{PROJECT}/holder.scad>\nhandle();\n")
    subprocess.run([OPENSCAD, "--backend=Manifold", "-o", f"{tmp}/handle.stl", f"{tmp}/handle.scad"], capture_output=True, text=True, check=True)
    model = trimesh.load(f"{tmp}/handle.stl")
    tip_gap0, clear0 = const("tip_gap", {}), const("clear", {})
    out = {}
    for wv in W:
        sec = mesh.section(plane_origin=[0, CY + wv, 0], plane_normal=[0, 1, 0])
        lines = [LineString([(x - TIP_X, z - CZ) for x, _, z in ent]) for ent in sec.discrete if len(ent) > 1]
        u = unary_union([p for p in polygonize(unary_union(lines)) if p.area > 0.05])
        real = unary_union([Polygon(g.exterior) for g in (u.geoms if isinstance(u, MultiPolygon) else [u])])
        msec = model.section(plane_origin=[wv, 0, 0], plane_normal=[1, 0, 0])
        grip = Polygon() if msec is None else loops_xor(msec, lambda q: (q[2] - tip_gap0, q[1] + clear0)).intersection(box(HOUSING_END, -80, 400, 80))
        out[wv] = unary_union([real, grip]).simplify(0.02)
    return out


class Docking:
    def __init__(self, over, tmp, margin):
        self.tip_gap, self.clear = const("tip_gap", over), const("clear", over)
        down, lean = math.radians(const("wand_down", over)), math.radians(const("wand_lean", over))
        self.up_d = -math.cos(lean) * math.sin(down)             # world up along the wand (tip to grip runs downhill)
        self.up_v = math.sqrt(1 - self.up_d ** 2)                # and along the cavity's up
        self.cleat_top = -(const("nose_h", over) / 2 + self.clear) + const("pocket_h", over) - const("cleat_clear", over)
        self.solid = holder_slices(over, tmp)
        for g in self.solid.values():
            shapely.prepare(g)
        self.handle = handle_slices(tmp)
        pocket = box(15.0, -20, 26.0, -12)                        # the lock pocket keeps its real size: the cleat's own clearance is the margin there
        self.bodies = {"in": {wv: unary_union([g, g.buffer(margin).difference(pocket)]) for wv, g in self.handle.items()},   # docking: the wand grown by the margin
                       "hold": {wv: g.buffer(-SKIN) for wv, g in self.handle.items()}}    # holding: the bare wand, the safe side
        self.seat = (self.tip_gap + REF[0], REF[1] - self.clear + max(0.25, margin + 0.125))
        self.cache = {"in": {}, "hold": {}}
        self.i_min = -int((self.tip_gap + 0.5) / DA)

    def pose(self, node):
        return self.seat[0] + node[0] * DA, self.seat[1] + node[1] * DY, node[2] * DT

    def matrix(self, node):
        ar, yr, th = self.pose(node)
        c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
        return [c, -s, s, c, ar - c * REF[0] + s * REF[1], yr - s * REF[0] - c * REF[1]]

    def point(self, node, p):
        m = self.matrix(node)
        return m[0] * p[0] + m[1] * p[1] + m[4], m[2] * p[0] + m[3] * p[1] + m[5]

    def tip_a(self, node):
        return self.point(node, (0, 0))[0]

    def height(self, node):
        a, y = self.point(node, LOAD)
        return self.up_d * a + self.up_v * y

    def free(self, node, mode):
        c = self.cache[mode]
        if node not in c:
            m = self.matrix(node)
            c[node] = not any(self.solid[wv].intersects(affinity.affine_transform(self.bodies[mode][wv], m)) for wv in W)
        return c[node]

    def neighbours(self, node, mode, steps):
        for q in steps:
            n = (node[0] + q[0], node[1] + q[1], node[2] + q[2])
            if n[0] >= self.i_min and J_RANGE[0] <= n[1] <= J_RANGE[1] and K_RANGE[0] <= n[2] <= K_RANGE[1] and self.free(n, mode):
                yield n

    AXIS = [q for q in itertools.product((-1, 0, 1), repeat=3) if sum(map(abs, q)) == 1]
    ALL = [q for q in itertools.product((-1, 0, 1), repeat=3) if any(q)]

    def way_in(self):
        """A free path from the docked pose to outside (docking is the same path backwards), preferring small tilts and lifts."""
        start = (0, 0, 0)
        if not self.free(start, "in"):
            return "docked pose collides", []
        cost, prev, heap = {start: 0.0}, {}, [(0.0, start)]
        while heap:
            c, node = heapq.heappop(heap)
            if c > cost.get(node, 1e18):
                continue
            if self.tip_a(node) >= GOAL_TIP:
                path = [node]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                return None, path[::-1]
            for n in self.neighbours(node, "in", self.AXIS):
                nc = c + 1 + 0.02 * abs(n[2])                     # a mild preference for the least-tilted way
                if nc < cost.get(n, 1e18):
                    cost[n], prev[n] = nc, node
                    heapq.heappush(heap, (nc, n))
        return "no way in", []

    def hold(self):
        start = (0, 0, 0)
        while not self.free(start, "hold"):
            start = (start[0], start[1] + 1, start[2])
        # where the wand settles: the lowest pose it can reach from the docked pose without the load rising more than 0.3 mm
        cap = self.height(start) + 0.3
        basin, todo = {start}, [start]
        while todo and len(basin) < 300000:
            node = todo.pop()
            for n in self.neighbours(node, "hold", self.AXIS):
                if n not in basin and self.height(n) <= cap:
                    basin.add(n)
                    todo.append(n)
        if any(self.tip_a(n) >= GOAL_TIP for n in basin):
            return 0.0, start, 0.0
        rest = min(basin, key=self.height)
        overlap = self.cleat_top - self.point(rest, REF)[1]
        level, seen, heap = {rest: self.height(rest)}, set(), [(self.height(rest), rest)]
        while heap:
            lv, node = heapq.heappop(heap)
            if node in seen:
                continue
            seen.add(node)
            if self.tip_a(node) >= GOAL_TIP:
                return lv - self.height(rest), rest, overlap
            for n in self.neighbours(node, "hold", self.AXIS):
                nl = max(lv, self.height(n))
                if n not in seen and nl < level.get(n, 1e18):
                    level[n] = nl
                    heapq.heappush(heap, (nl, n))
        return None, rest, overlap


def draw(dock, path, rest, png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    picks = [path[round(q * (len(path) - 1))] for q in (1, 0.75, 0.55, 0.4, 0.28, 0.17, 0.08, 0)] + [rest]   # from outside to docked, then hanging
    fig, axs = plt.subplots(3, 3, figsize=(21, 19))
    for k, (ax, node) in enumerate(zip(axs.flat, picks)):
        g = dock.solid[0]
        for p in (g.geoms if isinstance(g, MultiPolygon) else [g]):
            ax.fill(*p.exterior.xy, color="#2f7a80")
        h = affinity.affine_transform(dock.handle[0], dock.matrix(node))
        for p in (h.geoms if isinstance(h, MultiPolygon) else [h]):
            ax.fill(*p.exterior.xy, color="0.82", ec="k", lw=0.5)
        ax.set_xlim(-12, 62); ax.set_ylim(-30, 38); ax.set_aspect("equal"); ax.axis("off")
        th = dock.pose(node)[2]
        ax.set_title(("HANGING under load: " if k == 8 else f"{k + 1}: ") + f"tip {dock.tip_a(node):.1f} mm from the end wall, tilt {th:+.1f} deg", fontsize=13)
    fig.tight_layout()
    fig.savefig(png, dpi=60)


def main():
    args = sys.argv[1:]
    png = args[args.index("--png") + 1] if "--png" in args else None
    margin = float(args[args.index("--margin") + 1]) if "--margin" in args else 0.2
    over = dict(a.split("=", 1) for a in args if "=" in a and not a.startswith("--"))
    with tempfile.TemporaryDirectory() as tmp:
        dock = Docking(over, tmp, margin)
    print("overrides:", over or "none", "| wand grown by", margin, "mm for the way in")
    problem, path = dock.way_in()
    if problem:
        print("WAY IN: NONE (" + problem + ")")
    else:
        tilts = [dock.pose(n)[2] for n in path]
        lifts = [dock.pose(n)[1] - dock.pose(path[0])[1] for n in path]
        print(f"WAY IN: yes; tilt {min(tilts):+.1f} to {max(tilts):+.1f} deg (+ = grip toward the roof), pocket corner lifted up to {max(lifts):.2f} mm")
    rise, rest, overlap = dock.hold()
    if png and not problem:
        draw(dock, path, rest, png)
        print("wrote", png)
    th = dock.pose(rest)[2]
    if rise == 0:
        print("HOLD: NONE. Left alone, the wand works its way off the cleat and out, downhill all the way")
    else:
        print(f"hanging: tip {dock.tip_a(rest):.2f} mm from the end wall, tilt {th:+.1f} deg, hook overlap {overlap:.2f} of {dock.cleat_top + const('nose_h', over) / 2 + dock.clear:.2f} mm")
        print("HOLD: " + ("locked, no motion takes it off" if rise is None else f"the load must be raised {rise:.1f} mm before the wand can come off"))


if __name__ == "__main__":
    main()
