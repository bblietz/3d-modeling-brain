"""Press-fit test eyes + socket coupon for the Clawd mascot.

All dimensions measured from the print-proven meshes
(anthropic-mascot-eyes.stl / anthropic-mascot-body.stl), not from docs.
Self-verifying: run end to end with
  .venv/bin/python projects/Clawd-mascot/eye_fit.py
"""
import os

from build123d import (
    Align,
    Axis,
    Box,
    Compound,
    Pos,
    Sphere,
    export_stl,
    fillet,
)

# ---------------------------------------------------------------- measured ground truth
# Flush redesign 2026-08-04: width cut by 1/3 from the wide 6.2488,
# anchored on each eye's INSIDE edge (sockets recut in the FCStd as
# BodyFlushEyes, verified 4.1659 x 9.9058 from
# anthropic-mascot-body-flush.stl section loops).
EYE_X = 4.1659  # mm, footprint width (socket nominal)
EYE_Y = 9.9057  # mm, footprint length (unchanged from the wide eye)
EYE_Z = 3.0123  # mm, height = SOCKET_DEPTH: eye tops sit FLUSH with the 24.4 body top (was 4.0257, 1.013 proud)
ROUND_R = 0.2  # mm, small top-rim edge break (the 0.79 roundover suited proud eyes only)
SOCKET_DEPTH = 3.0123  # mm, body top z 24.4000 - socket floor z 21.3877
EYE_VOL_MEASURED = 121.0776  # mm^3, trimesh volume of one original eye

# ---------------------------------------------------------------- printed-fit compensation
# Coupon v1 calipers (2026-07-31): pocket printed 6.23 x 9.84 (nominal
# 6.2488 x 9.9057); the 0.05-clearance eye printed 6.09 x 9.89 (nominal
# 6.1488 x 9.8057). Deviations: pocket X -0.019, Y -0.066; eye X -0.059,
# Y +0.084 (Y includes first-layer flare on the inserted end). The eye
# size that measures FLUSH with the printed pocket is
# pocket_nom + pocket_dev - eye_dev, per axis. Deviations are treated as
# ABSOLUTE offsets (coupons were measured at the 6.25-wide size; X is
# transferred to the narrow eye, Y is unchanged):
FIT_X = 4.2059  # mm, zero-effective-fit eye width (EYE_X + 0.04)
FIT_Y = 9.7557  # mm, zero-effective-fit eye length

# ---------------------------------------------------------------- design constants
INTERFERENCES = (-0.04, 0.02, 0.08)  # mm TOTAL per axis, dots 1..3; re-centered 2026-08-04 for the new filament (negative = clearance)
FINAL_INTERFERENCE = -0.04  # relaxed one 0.06 step from the +0.02 coupon-v2 winner: the new filament printed +0.02 smash-tight (2026-08-04)
DOT_DIA = 0.8  # mm, identification dot base diameter
DOT_PROUD = 0.3  # mm, dot height above the top face
DOT_PITCH = 1.6  # mm, dot center-to-center spacing along Y
COUPON_MARGIN = 6.0  # mm added to eye footprint per axis
COUPON_Z = 6.0  # mm coupon height
GAP = 6.0  # mm between parts on a plate

SCRATCH = ("/tmp/claude-1000/-home-brian-ClaudeProjects-3d-modeling-brain/"
           "b0bb31e9-e046-41c2-9c57-5bc3574fe25f/scratchpad")


def eye(interference: float) -> Box:
    """Eye at TOTAL per-axis `interference` over the measured zero-fit
    basis (FIT_X/FIT_Y), sitting on Z=0, top face up."""
    part = Box(
        FIT_X + interference,
        FIT_Y + interference,
        EYE_Z,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    top_rim = part.edges().group_by(Axis.Z)[-1]
    return fillet(top_rim, ROUND_R)


def test_eye(interference: float, n_dots: int) -> Compound:
    """Test eye with `n_dots` identification dots on the top face.

    Dots are spherical caps: base diameter DOT_DIA at the top face,
    DOT_PROUD tall. Cap sphere radius R from a=DOT_DIA/2, h=DOT_PROUD.
    """
    a, h = DOT_DIA / 2, DOT_PROUD
    r_cap = (a * a + h * h) / (2 * h)
    part = eye(interference)
    for i in range(n_dots):
        y = (i - (n_dots - 1) / 2) * DOT_PITCH
        part += Pos(0, y, EYE_Z - (r_cap - h)) * Sphere(r_cap)
    return part


# ---------------------------------------------------------------- parts
master_eye = eye(0.0)  # zero-effective-fit basis eye
assert len(master_eye.solids()) == 1
bb = master_eye.bounding_box()
assert abs(bb.size.X - FIT_X) < 1e-6, bb.size
assert abs(bb.size.Y - FIT_Y) < 1e-6, bb.size
assert abs(bb.size.Z - EYE_Z) < 1e-6, bb.size
print(f"basis eye: bbox {bb.size.X:.4f} x {bb.size.Y:.4f} x {bb.size.Z:.4f}")

test_eyes = [test_eye(i, n + 1) for n, i in enumerate(INTERFERENCES)]
for i, t in zip(INTERFERENCES, test_eyes):
    assert len(t.solids()) == 1
    tb = t.bounding_box()
    assert abs(tb.size.X - (FIT_X + i)) < 1e-4, (i, tb.size)
    assert abs(tb.size.Y - (FIT_Y + i)) < 1e-4, (i, tb.size)
    assert abs(tb.size.Z - (EYE_Z + DOT_PROUD)) < 1e-4, (i, tb.size)
    print(f"test eye interference={i:.2f}: bbox {tb.size.X:.4f} x {tb.size.Y:.4f} x {tb.size.Z:.4f}")

# Coupon: block with ONE zero-clearance socket pocket in the top face,
# replicating the body socket (square corners, SOCKET_DEPTH deep).
COUPON_X = EYE_X + COUPON_MARGIN
COUPON_Y = EYE_Y + COUPON_MARGIN
coupon = Box(COUPON_X, COUPON_Y, COUPON_Z,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
pocket_cutter = Pos(0, 0, COUPON_Z - SOCKET_DEPTH) * Box(
    EYE_X, EYE_Y, SOCKET_DEPTH + 1.0,  # extend 1 mm past the top face
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
coupon -= pocket_cutter

assert len(coupon.solids()) == 1
cb = coupon.bounding_box()
assert abs(cb.size.X - COUPON_X) < 1e-6, cb.size
assert abs(cb.size.Y - COUPON_Y) < 1e-6, cb.size
assert abs(cb.size.Z - COUPON_Z) < 1e-6, cb.size

# Measure the pocket geometrically with a probe solid: fill the top
# SOCKET_DEPTH slab of the coupon's bbox, subtract the coupon, and keep
# the largest resulting solid (the cavity).
probe = Pos(0, 0, COUPON_Z - SOCKET_DEPTH) * Box(
    COUPON_X, COUPON_Y, SOCKET_DEPTH,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
cavity = max((probe - coupon).solids(), key=lambda s: s.volume)
pb = cavity.bounding_box()
assert abs(pb.size.X - EYE_X) < 1e-4, pb.size  # pocket == zero-clearance eye footprint
assert abs(pb.size.Y - EYE_Y) < 1e-4, pb.size
assert abs(pb.size.Z - SOCKET_DEPTH) < 1e-4, pb.size
assert abs(cavity.volume - EYE_X * EYE_Y * SOCKET_DEPTH) < 1e-3, cavity.volume
print(f"coupon: bbox {cb.size.X:.4f} x {cb.size.Y:.4f} x {cb.size.Z:.4f}; "
      f"pocket cavity {pb.size.X:.4f} x {pb.size.Y:.4f} x {pb.size.Z:.4f}")

# Model-level delta of each test eye vs the CAD pocket (informational;
# the EFFECTIVE fit is vs the PRINTED pocket via the FIT basis).
for i, t in zip(INTERFERENCES, test_eyes):
    tb = t.bounding_box()
    dx = tb.size.X - pb.size.X
    dy = tb.size.Y - pb.size.Y
    assert abs(dx - (FIT_X - EYE_X + i)) < 0.005, (i, dx)
    assert abs(dy - (FIT_Y - EYE_Y + i)) < 0.005, (i, dy)
    print(f"test eye interference={i:.2f}: model delta vs CAD pocket X={dx:+.4f} Y={dy:+.4f}")

# Final production eyes: two identical, no dots, FINAL_INTERFERENCE.
final_eye = eye(FINAL_INTERFERENCE)
assert len(final_eye.solids()) == 1
fb = final_eye.bounding_box()
assert abs(fb.size.X - (FIT_X + FINAL_INTERFERENCE)) < 1e-4, fb.size
assert abs(fb.size.Y - (FIT_Y + FINAL_INTERFERENCE)) < 1e-4, fb.size
assert abs(fb.size.Z - EYE_Z) < 1e-4, fb.size
print(f"final eye interference={FINAL_INTERFERENCE:.2f}: bbox {fb.size.X:.4f} x {fb.size.Y:.4f} x {fb.size.Z:.4f}")

# ---------------------------------------------------------------- plate layouts (Z=0)
# Coupon plate: coupon then the three dotted test eyes in a row along X, GAP apart.
plate_parts = [coupon]
x_edge = COUPON_X / 2
for t in test_eyes:
    w = t.bounding_box().size.X
    plate_parts.append(Pos(x_edge + GAP + w / 2, 0, 0) * t)
    x_edge += GAP + w
coupon_plate = Compound(children=plate_parts)

# Final plate: two production eyes, GAP apart along X.
half = fb.size.X / 2 + GAP / 2
final_plate = Compound(children=[Pos(-half, 0, 0) * final_eye,
                                 Pos(+half, 0, 0) * final_eye])

assert len(coupon_plate.solids()) == 4
assert len(final_plate.solids()) == 2
for plate in (coupon_plate, final_plate):
    pbb = plate.bounding_box()
    assert abs(pbb.min.Z) < 1e-6, pbb.min  # everything sits on Z=0

# ---------------------------------------------------------------- export + mesh verify
PROJ = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Clawd-mascot"
COUPON_STL = os.path.join(PROJ, "eye-fit-coupon.stl")
FINAL_STL = os.path.join(PROJ, "eyes-final.stl")


def _mesh_loops(mesh, z):
    """XY extents of the section loops of `mesh` at height z (no shapely)."""
    import numpy as np
    from trimesh.intersections import mesh_plane

    segs = mesh_plane(mesh, plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
    pts = segs.reshape(-1, 3)[:, :2]
    ids = {}
    idx = [ids.setdefault(tuple(k), len(ids))
           for k in np.round(pts / 1e-4).astype(np.int64)]
    parent = list(range(len(ids)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(0, len(idx), 2):
        parent[find(idx[i])] = find(idx[i + 1])
    roots = np.array([find(i) for i in idx])
    return [pts[roots == r].max(axis=0) - pts[roots == r].min(axis=0)
            for r in np.unique(roots)]


def clean_stl(path, expected_parts):
    """Drop tessellation-artifact sliver shells (OCCT sphere-seam hair
    triangles at the dot seams). A closed solid needs >= 4 triangles;
    anything smaller is an artifact. Guard: dropped area must be negligible."""
    import trimesh

    m = trimesh.load_mesh(path)
    comps = m.split(only_watertight=False)
    keep = [c for c in comps if len(c.faces) >= 4]
    dropped = [c for c in comps if len(c.faces) < 4]
    assert sum(c.area for c in dropped) < 0.01, [c.area for c in dropped]
    assert len(keep) == expected_parts, (len(keep), expected_parts)
    trimesh.util.concatenate(keep).export(path)


def verify_exports():
    import numpy as np
    import trimesh

    # Coupon plate: 4 watertight solids, one is the coupon.
    plate = trimesh.load_mesh(COUPON_STL)
    comps = sorted(plate.split(only_watertight=False),
                   key=lambda c: c.bounds[0][0])
    assert len(comps) == 4, len(comps)
    assert all(c.is_watertight for c in comps)
    cpn, eyes = comps[0], comps[1:]
    assert np.allclose(cpn.bounds[1] - cpn.bounds[0],
                       [COUPON_X, COUPON_Y, COUPON_Z], atol=1e-3)

    # Pocket opening measured from the exported mesh (inner section loop).
    loops = _mesh_loops(cpn, COUPON_Z - 1.5)
    pocket = min(loops, key=lambda e: e[0])
    assert abs(pocket[0] - EYE_X) < 1e-3 and abs(pocket[1] - EYE_Y) < 1e-3, pocket
    # ...and it must match the FLUSH body socket opening (4.1659 x 9.9058,
    # measured from anthropic-mascot-body-flush.stl section loops).
    assert abs(pocket[0] - 4.1659) < 0.02 and abs(pocket[1] - 9.9057) < 0.02, pocket

    # Test eyes: mesh-measured dims must equal the FIT basis + interference.
    for i, e in zip(INTERFERENCES, eyes):
        dims = e.bounds[1] - e.bounds[0]
        assert abs(dims[0] - (FIT_X + i)) < 1e-3, (i, dims)
        assert abs(dims[1] - (FIT_Y + i)) < 1e-3, (i, dims)
        assert abs(dims[2] - (EYE_Z + DOT_PROUD)) < 1e-3, dims
        print(f"  STL test eye interference={i:.2f}: {dims[0]:.4f} x {dims[1]:.4f} "
              f"(CAD pocket {pocket[0]:.4f} x {pocket[1]:.4f})")

    # Final plate: 2 identical watertight eyes at FINAL_INTERFERENCE.
    fin = trimesh.load_mesh(FINAL_STL)
    fcomps = fin.split(only_watertight=False)
    assert len(fcomps) == 2, len(fcomps)
    assert all(c.is_watertight for c in fcomps)
    for c in fcomps:
        dims = c.bounds[1] - c.bounds[0]
        assert np.allclose(dims, [FIT_X + FINAL_INTERFERENCE,
                                  FIT_Y + FINAL_INTERFERENCE, EYE_Z], atol=1e-3), dims
    d01 = np.abs((fcomps[0].bounds[1] - fcomps[0].bounds[0])
                 - (fcomps[1].bounds[1] - fcomps[1].bounds[0]))
    assert d01.max() < 1e-6, d01
    print("  STL final eyes: 2 identical watertight solids, "
          f"{fcomps[0].bounds[1][0]-fcomps[0].bounds[0][0]:.4f} x "
          f"{fcomps[0].bounds[1][1]-fcomps[0].bounds[0][1]:.4f} x "
          f"{fcomps[0].bounds[1][2]-fcomps[0].bounds[0][2]:.4f}")


if __name__ == "__main__":
    export_stl(coupon_plate, COUPON_STL)
    export_stl(final_plate, FINAL_STL)
    clean_stl(COUPON_STL, 4)
    clean_stl(FINAL_STL, 2)
    verify_exports()
    print("all assertions passed")

if os.environ.get("SHOW"):
    from ocp_vscode import Camera, show
    show(coupon_plate, final_plate, names=["fit-coupon-plate", "final-eyes"],
         reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
