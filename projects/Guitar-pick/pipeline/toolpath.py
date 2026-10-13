"""Bambu G-code toolpaths, per layer, with path starts and ends, for checks that need to know where the nozzle
stopped and started (the first standing print showed that the slicer began and ended a path on the pick's edge
at every shoulder layer). Arcs (G2/G3) are sampled; the pipeline's other parser only keeps their end points.

    parse(gcode_text) -> {z: [[x0, y0, x1, y1, width, feature, feed_mm_min, starts_path, ends_path], ...]}
    tip_path_ends(layers, cx, cy, z_lo, z_hi, feats, tol) -> [(z, "R"|"L", x_from_centre), ...]
"""
import math
import re

_NUM = re.compile(r"([XYZEIJF])([-0-9.]+)")


def parse(text):
    x = y = z = 0.0
    feat, width, f = "", 0.0, 0.0
    layers = {0.0: []}
    last = None            # the last extrusion segment of the layer, to flag the path end when a travel follows
    after_travel = True
    for line in text.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":")[1])
        elif line.startswith("; Z_HEIGHT:"):
            z = round(float(line.split(":")[1]), 3)
            layers.setdefault(z, [])
            after_travel, last = True, None
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            vals = {k: float(v) for k, v in _NUM.findall(line.split(";")[0])}
            nx, ny = vals.get("X", x), vals.get("Y", y)
            f = vals.get("F", f)
            e = vals.get("E", 0.0)
            moved = nx != x or ny != y
            if e > 0 and moved and line[:3] in ("G2 ", "G3 "):
                i, j = vals.get("I", 0.0), vals.get("J", 0.0)
                cxa, cya, r = x + i, y + j, math.hypot(i, j)
                a0, a1 = math.atan2(y - cya, x - cxa), math.atan2(ny - cya, nx - cxa)
                da = a1 - a0
                if line[:3] == "G2 " and da > 0:
                    da -= 2 * math.pi
                if line[:3] == "G3 " and da < 0:
                    da += 2 * math.pi
                n = max(2, int(abs(da) * r / 0.05))
                px, py = x, y
                for k in range(1, n + 1):
                    a = a0 + da * k / n
                    qx, qy = cxa + r * math.cos(a), cya + r * math.sin(a)
                    layers[z].append([px, py, qx, qy, width, feat, f, after_travel and k == 1, False])
                    px, py = qx, qy
                last, after_travel = layers[z][-1], False
            elif e > 0 and moved:
                layers[z].append([x, y, nx, ny, width, feat, f, after_travel, False])
                last, after_travel = layers[z][-1], False
            elif moved or e < 0:            # a travel, or a retract on the spot: the path ends here
                if last is not None and not after_travel:
                    last[8] = True
                after_travel = True
            x, y = nx, ny
    return layers


def tip_path_ends(layers, cx, cy, z_lo, z_hi, feats=("Outer wall",), tol=0.6):
    """Path starts and ends within `tol` of either end point of the pick's cross-section (its two edges on the
    mid-plane: the extreme x of the outer wall within 1 mm of the mid-plane, at y = cy), for the layers z_lo..z_hi.
    `feats` None means every extrusion feature. Distance is to the point, not the x alone: in the neck layers the
    block's rear corner shares the junction's x and carries the loop's painted seam, 3.4 mm away."""
    out = []
    for z in sorted(layers):
        if z < z_lo or z > z_hi:
            continue
        ow = [s for s in layers[z] if s[5] == "Outer wall" and abs(s[0] - cx) < 15 and abs(s[1] - cy) < 1.0]
        if not ow:
            continue
        xs = [v for s in ow for v in (s[0], s[2])]
        xr, xl = max(xs), min(xs)
        for s in layers[z]:
            if feats is not None and s[5] not in feats:
                continue
            for flag, px, py in ((s[7], s[0], s[1]), (s[8], s[2], s[3])):
                if flag and math.hypot(px - xr, py - cy) < tol:
                    out.append((z, "R", round(px - cx, 2)))
                elif flag and math.hypot(px - xl, py - cy) < tol:
                    out.append((z, "L", round(px - cx, 2)))
    return out
