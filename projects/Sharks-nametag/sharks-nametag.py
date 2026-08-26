"""Santa Cruz Sharks backpack nametag v3 - build123d, Bambu X2D, 0.4 mm nozzle.

Front: club logo elements vector-traced 1:1 from the club PNG
(679 px = 76.2 mm): soccer ball art (cyan in the real asset), 4 beveled
stars, SANTA CRUZ letterforms, surfer silhouette. Parametric only where
crispness demands: disc, swoosh circles, thin navy ball circle, banner
rounded-rect + border, hang hole, debossed back name/number.

Overlay rules (from the v2 FreeCAD build): stars cut the swoosh; white
banner art cuts all navy; navy cuts cyan at traced boundaries.

Print: back on bed, logo face up, ironed top. White / navy #00395e /
cyan #31bad6 = AMS slots 1-3.
"""

import json
import math
import os

from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.environ.get("SCRATCH", "/tmp")

# ------------------------------------------------------------- scale & layout
S = 76.2 / 679.0          # 1:1 logo mapping
CX, CY = 339.5, 338.5     # image center, y-up px

DISC_D = 76.2
DISC_R = DISC_D / 2
BASE_T = 3.36             # v3.26: 4.2 x 0.8 (Brian 2026-08-23, "reduce thickness by 20%"); 28 x 0.12 layers (was 2.4 -> 4.2 on 2026-08-06)
TIER1_T = 0.6             # graphic fields
TIER2_T = 0.6             # foreground (surfer, banner border + letters)
Z1 = BASE_T + TIER1_T
Z2 = Z1 + TIER2_T

HOLE_D = 5.2              # 5 mm + shrinkage compensation
HOLE_POS = (0, 32.4)      # ON the star arc: the hole takes the center slot
                          # of 5 even positions (star star HOLE star star),
                          # rim 3.1 mm from the disc edge (Brian 2026-08-01)

KID_NAME = os.environ.get("KID_NAME", "MAX")
KID_NUMBER = os.environ.get("KID_NUMBER", "18")
TEAM_YEARS = os.environ.get("TEAM_YEARS", "2015-2016")

# DETAIL=crisp (default) adapts what is too fine to print crisply on the
# 0.4 nozzle: the YOUTH SOCCER CLUB line becomes an inlay keyed into the
# disc instead of a raised tier. DETAIL=full keeps the raised original
# for the 0.2 mm nozzle (ordered 2026-08-06). SCCYSC dropped entirely per
# Brian (2026-08-06): band stars continue across the top arc instead, so
# the modes now differ only in the YSC treatment.
# v3.20: the v3.19 printability redesigns (0.9 border + grown banner,
# CITY polarity flip, swoosh tip widening) were REVERTED per Brian after
# viewing - the source look wins; sub-0.9 raised art is knowingly dropped
# by the slicer (see brief.md and pipeline/audit_widths.py).
# v3.21: crisp YSC raised YSC_RAISE proud of the disc top per Brian
# (2026-08-08); the inlay keying below the surface stays.
# v3.22: crisp ball web rebuilt as clean pentagons + uniform seam strokes
# (Brian 2026-08-20, "the soccer ball is messy"); see the crisp block.
# v3.23: ball seams + cyan rim ring 0.6 mm, navy ball circle + pinstripe
# back to 0.65, for ARACHNE slicing (Brian 2026-08-20, "closer to
# hairline"); the crisp project 3MF sets wall_generator arachne.
# v3.24: YOUTH SOCCER CLUB back to (near) the source size on its source
# arc: YSC_LAYOUT "arc", YSC_K 1.2 (1.0 = the logo exactly; Brian
# 2026-08-21, "a bit bigger, raised preferred"); the v3.17 flat arch
# stays one constant away (YSC_LAYOUT "arch").
# v3.25: crisp YSC back to a FLUSH inlay (YSC_RAISE 0) for the 13-kid
# batch: print 6 showed the raised 0.5 mm single-bead bars blobby and
# YOUTH partly filled, and a raised hairline on a backpack tag is the
# first thing to get knocked off. Raised stays one constant away.
# v3.26 (Brian 2026-08-23): YSC RAISED again ("keep it raised as
# before", YSC_RAISE 0.5) and the base slab 20% thinner, BASE_T 4.2 ->
# 3.36 (28 x 0.12 layers; tag 5.4 -> 4.56 mm total).
# v3.27 (Brian 2026-08-23, gate print IMG_1530 still gappy, staying
# PETG): SANTA CRUZ + CITY white get FILLET_R junction micro-fillets
# (morphological closing+opening in final mm space) so arachne can seat
# beads through junctions/apexes - the remaining pinholes are geometric
# voids no setting touches (locked). A corner sharper than the 0.2 mm
# bead radius never printed sharp anyway, so the visual delta is nil.
# OUTCOME (same day, offline toolpath sweep): REFUTED. r 0.15/0.25/0.35
# redistribute the junction voids along the rounded arc instead of
# removing them (banner-letter visible voids 0.24 -> 0.29-0.37 mm2): the
# voids sit where wall beads COLLIDE (medial axis), not at the outline
# corner. FILLET_R stays 0; the 0.2 mm nozzle is the zero-void path
# (offline 0.2 slice: banner+CITY effectively 0).
DETAIL = os.environ.get("DETAIL", "crisp")
assert DETAIL in ("crisp", "full"), DETAIL

# ------------------------------------------------------------------- helpers


def signed_area(pts):
    return 0.5 * sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))


def ccw(pts):
    return pts if signed_area(pts) > 0 else pts[::-1]


def px2mm(pts):
    return [((x - CX) * S, (y - CY) * S) for x, y in pts]


def sketch_from_polys(polys, min_hole_area=0.5):
    sk = Sketch()
    for p in polys:
        f = Polygon(*ccw(px2mm(p["outer"])))
        for h in p.get("holes", []):
            hm = px2mm(h)
            if abs(signed_area(hm)) > min_hole_area:
                f -= Polygon(*ccw(hm))
        sk += f
    return sk


with open(f"{HERE}/images/logo-layers.json") as f:
    LAYERS = json.load(f)
with open(f"{HERE}/images/surfer-outline.json") as f:
    SURFER = json.load(f)
with open(f"{HERE}/images/city-oval.json") as f:
    CITY = json.load(f)
with open(f"{HERE}/images/youth-soccer-club.json") as f:
    YSC = json.load(f)

# ------------------------------------------------------- parametric elements
# Composition symmetrized per Brian (2026-08-01): swoosh gap straight up,
# stars evenly spaced about the centerline, no star/swoosh overlap, central
# art groups on the exact centerline. Shapes stay traced; layout is ours.


def polar(r, deg):
    return (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)))


# Crescent fitted to the SOURCE width profile (radial scan of the PNG,
# symmetrized): ~5.1 mm at the bottom, ~3.1 mm at the sides, tapering to
# fine points at 57/123 deg. Outer boundary = lens of two circles (the
# second accelerates the taper near the tips, matching the scan within
# ~0.1 mm at every sampled angle); wedge removes the sub-0.3 mm tip
# slivers that would otherwise crawl into the star zone.
swoosh_2d = (
    (Pos(0, -1.46) * Circle(35.69)) & (Pos(0, -2.90) * Circle(35.84))
    - Pos(0, 0.575) * Circle(32.51)
) - Polygon((0, 0), *[polar(50, a) for a in range(57, 124, 3)])

bc = LAYERS["ball_circle"]
BALL_DX = -(bc["cx"] - CX) * S            # shift ball group onto x=0
BALL_C = (0.0, (bc["cy"] - CY) * S)
BALL_R = bc["r"] * S
# Inner circle and outer pinstripe, equal per Brian; source width 0.65.
# v3.16: the first 0.4-nozzle test print dropped every ball line - the
# classic wall generator prints nothing under 2 perimeters (0.84 mm at
# 0.42 line width), so crisp widened all ball lines to MIN_LINE_W.
# v3.23 (2026-08-20, Brian: "make them closer to hairline"): the crisp
# project 3MF now slices with the ARACHNE wall generator, which prints a
# single variable-width bead down to ~0.45 mm, so the ball lines drop
# back toward the source: seams + cyan rim ring SEAM_W 0.6, navy ball
# circle + crest pinstripe back to the v3.12 value 0.65 in both modes.
# MIN_LINE_W stays as the classic-wall reference for audit_widths.py.
MIN_LINE_W = 0.9
SEAM_W = 0.6
WEB_FLOOR = 0.5     # arachne single-bead floor used by the crisp web audit
RING_LINE_W = 0.65
ballring_2d = Pos(*BALL_C) * (Circle(BALL_R + RING_LINE_W) - Circle(BALL_R))

bb = LAYERS["banner_bbox"]
BAN_W = (bb[2] - bb[0]) * S
BAN_H = (bb[3] - bb[1]) * S
BAN_DX = -((bb[0] + bb[2]) / 2 - CX) * S  # shift banner group onto x=0
BAN_C = (0.0, ((bb[1] + bb[3]) / 2 - CY) * S)
BAN_R = 1.2
BORDER_INSET, BORDER_W = 0.9, 0.6

banner_2d = Pos(*BAN_C) * RectangleRounded(BAN_W, BAN_H, BAN_R)
border_2d = Pos(*BAN_C) * (
    offset(RectangleRounded(BAN_W, BAN_H, BAN_R), -BORDER_INSET)
    - offset(RectangleRounded(BAN_W, BAN_H, BAN_R), -BORDER_INSET - BORDER_W)
)

# ---------------------------------------------------------------- traced art
# --- trace refit: raster wobble -> exact lines and arcs (Brian 2026-08-02:
# "pentagon edges are not smooth"). Corner-delimited runs become straight
# Lines when they hug their chord, ThreePointArcs when a circle fits.
def _dist_to_chord(pts, a, b):
    ab = (b[0] - a[0], b[1] - a[1])
    L = math.hypot(*ab) or 1e-9
    return max(abs((p[0] - a[0]) * ab[1] - (p[1] - a[1]) * ab[0]) / L for p in pts)


def _fit_circle(pts):
    import numpy as np
    A = np.array([[p[0], p[1], 1.0] for p in pts])
    b = np.array([p[0] ** 2 + p[1] ** 2 for p in pts])
    (cx2, cy2, c), *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = cx2 / 2, cy2 / 2
    r = math.sqrt(c + cx ** 2 + cy ** 2)
    rms = math.sqrt(sum((math.hypot(p[0] - cx, p[1] - cy) - r) ** 2 for p in pts) / len(pts))
    return (cx, cy), r, rms


def _refined_edges(ring_pts, corner_deg=25.0, line_tol=0.8, arc_tol=0.5):
    n = len(ring_pts)
    corners = []
    for i in range(n):
        a = ring_pts[(i - 2) % n]
        b = ring_pts[i]
        c = ring_pts[(i + 2) % n]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        L1, L2 = math.hypot(*v1) or 1e-9, math.hypot(*v2) or 1e-9
        cosang = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (L1 * L2)))
        if math.degrees(math.acos(cosang)) > corner_deg:
            corners.append(i)
    if len(corners) < 2:
        corners = [0, n // 2]
    edges = []
    for k in range(len(corners)):
        i0, i1 = corners[k], corners[(k + 1) % len(corners)]
        run = ring_pts[i0:i1 + 1] if i1 > i0 else ring_pts[i0:] + ring_pts[:i1 + 1]
        p0, p1 = run[0], run[-1]
        if len(run) <= 2 or _dist_to_chord(run[1:-1], p0, p1) < line_tol:
            edges.append(("line", p0, p1))
            continue
        (cx, cy), r, rms = _fit_circle(run)
        if rms < arc_tol:
            pm = run[len(run) // 2]
            th = math.atan2(pm[1] - cy, pm[0] - cx)
            edges.append(("arc", p0, (cx + r * math.cos(th), cy + r * math.sin(th)), p1))
        else:
            for a, b in zip(run, run[1:]):
                edges.append(("line", a, b))
    return edges


def refined_face(poly, shift):
    def T(p):
        x, y = (p[0] - CX) * S + shift, (p[1] - CY) * S
        return (x, y)

    def ring_face(pts):
        segs = []
        for e in _refined_edges(ccw(pts)):
            if e[0] == "line":
                segs.append(Line(T(e[1]), T(e[2])))
            else:
                segs.append(ThreePointArc(T(e[1]), T(e[2]), T(e[3])))
        return make_face(segs)

    f = ring_face(poly["outer"])
    for h in poly.get("holes", []):
        if abs(signed_area(px2mm(h))) > 0.5:
            f -= ring_face(h)
    return f


ball_cyan_2d = Sketch()
for _poly in LAYERS["ball_cyan"]:
    _ref = refined_face(_poly, BALL_DX)
    _raw = abs(signed_area(px2mm(_poly["outer"]))) - sum(
        abs(signed_area(px2mm(h))) for h in _poly.get("holes", []) if abs(signed_area(px2mm(h))) > 0.5)
    assert abs(_ref.area - _raw) / _raw < 0.04, f"refit changed area {(_ref.area - _raw) / _raw:+.1%}"
    ball_cyan_2d += _ref


# Letters keep their SOURCE heights (T, second A, C are drawn short and the
# C notched because the CITY oval tucks into that space - reverted to source
# per Brian 2026-08-01). Horizontally the line is centered and scaled so the
# S/Z-to-frame gap equals the frame's own margin; the CITY group gets the
# SAME transform so the letter/oval interlock is preserved exactly.
LETTER_FRAME_GAP = BORDER_INSET
_letters_avail = BAN_W - 2 * (BORDER_INSET + BORDER_W + LETTER_FRAME_GAP)
_line_x = [p[0] for poly in LAYERS["banner_text"] for p in poly["outer"]]
LINE_CX = (min(_line_x) + max(_line_x)) / 2
LINE_KX = min(1.0, (_letters_avail / S) / (max(_line_x) - min(_line_x)))


def line_tf(pts):
    """Banner-line horizontal transform (center + fit), source y kept."""
    return [((x - LINE_CX) * LINE_KX + CX, y) for x, y in pts]


def line_sketch(polys, min_hole_area=0.5):
    sk = Sketch()
    for poly in polys:
        f = Polygon(*ccw(px2mm(line_tf(poly["outer"]))))
        for h in poly.get("holes", []):
            hm = px2mm(line_tf(h))
            if abs(signed_area(hm)) > min_hole_area:
                f -= Polygon(*ccw(hm))
        sk += f
    return sk


FILLET_R = float(os.environ.get("FILLET_R", "0"))   # v3.27 experiment, REFUTED - keep 0 (see header)
_FILLET_DEBUG = []
_FILLET_RUNGS = {}


def fillet_line_sketch(polys, r, min_hole_area=0.5):
    """line_sketch plus r-mm corner rounding (closing then opening) done
    in the final mm space; r=0 is line_sketch exactly. Asserts each
    letter piece survives with its counters and near-identical area."""
    if not r:
        return line_sketch(polys, min_hole_area)
    from shapely.geometry import Polygon as _FP
    from shapely import simplify as _fsimp
    sk = Sketch()
    for poly in polys:
        holes = [px2mm(line_tf(h)) for h in poly.get("holes", [])]
        holes = [h for h in holes if abs(signed_area(h)) > min_hole_area]
        sp = _FP(px2mm(line_tf(poly["outer"])), holes)
        assert sp.is_valid, "letter piece invalid before fillet"

        def _ok(g):
            return (g.geom_type == "Polygon" and not g.is_empty
                    and len(g.interiors) == len(sp.interiors)
                    and abs(g.area - sp.area) / sp.area < 0.05)

        # adaptive ladder: closing fills concave junction notches (never
        # removes material); opening rounds convex tips but erodes thin
        # members (the CITY oval ring loses 35%), so it only applies
        # where the piece survives it.
        closed = sp.buffer(r, quad_segs=8).buffer(-r, quad_segs=8)
        opened = closed.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)
        if _ok(opened):
            sm, rung = opened, "full"
        elif _ok(closed):
            sm, rung = closed, "close-only"
        else:
            sm, rung = sp, "raw"
        _FILLET_RUNGS[rung] = _FILLET_RUNGS.get(rung, 0) + 1
        sm = _fsimp(sm, 0.004, preserve_topology=True)
        assert _ok(sm), (f"fillet r={r} broke a piece at "
                         f"({sp.centroid.x:.1f},{sp.centroid.y:.1f}) even on rung {rung}")
        if os.environ.get("FILLET_DEBUG"):
            _FILLET_DEBUG.append((sp, sm))
        f = Polygon(*ccw([(x, y) for x, y in sm.exterior.coords[:-1]]))
        for h in sm.interiors:
            f -= Polygon(*ccw([(x, y) for x, y in h.coords[:-1]]))
        sk += f
    return sk


letters_2d = fillet_line_sketch(LAYERS["banner_text"], FILLET_R)
if FILLET_R:
    print(f"letter fillet r={FILLET_R} rungs: {_FILLET_RUNGS}")
# surfer: organic silhouette -> periodic spline through a resampled,
# lightly smoothed outline (Brian 2026-08-02: "smooth the edges")
def smoothed_ring_mm(pts_px, shift, spacing_px=2.5, passes=2):
    closed = pts_px + [pts_px[0]]
    seglens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(closed, closed[1:])]
    total = sum(seglens)
    n = max(24, int(total / spacing_px))
    samples, acc, si = [], 0.0, 0
    for k in range(n):
        target = total * k / n
        while acc + seglens[si] < target:
            acc += seglens[si]
            si += 1
        t = (target - acc) / (seglens[si] or 1e-9)
        a, b = closed[si], closed[si + 1]
        samples.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    for _ in range(passes):
        samples = [((samples[i - 1][0] + 2 * x + samples[(i + 1) % n][0]) / 4,
                    (samples[i - 1][1] + 2 * y + samples[(i + 1) % n][1]) / 4)
                   for i, (x, y) in enumerate(samples)]
    return [((x - CX) * S + shift, (y - CY) * S) for x, y in ccw(samples)]


def spline_ring_face(pts_px, shift, spacing_px=2.5, passes=2):
    mm = smoothed_ring_mm(pts_px, shift, spacing_px, passes)
    return make_face([Spline(*mm, periodic=True)])


surfer_2d = spline_ring_face(SURFER["outer"], BALL_DX)
for _h in SURFER["holes"]:
    if abs(signed_area(px2mm(_h))) > 1.0:
        surfer_2d -= spline_ring_face(_h, BALL_DX, spacing_px=1.5, passes=1)

_raw_surf = abs(signed_area(px2mm(SURFER["outer"]))) - sum(
    abs(signed_area(px2mm(h))) for h in SURFER["holes"] if abs(signed_area(px2mm(h))) > 1.0)
assert abs(surfer_2d.area - _raw_surf) / _raw_surf < 0.04, "surfer smoothing changed area"

# stars: ONE traced star shape, placed 4x symmetrically about the centerline;
# the hang hole occupies the 5th (center) slot of the even 13-deg spacing
STAR_ARC_R = 32.4
STAR_ANGLES = [65, 77.5, 102.5, 115]   # even 12.5 deg; hole holds the 90 slot
_tpl_raw = px2mm(LAYERS["stars"][2]["outer"])
_txs = [p[0] for p in _tpl_raw]
_tys = [p[1] for p in _tpl_raw]
_tc = ((min(_txs) + max(_txs)) / 2, (min(_tys) + max(_tys)) / 2)
_tpl = [(x - _tc[0], y - _tc[1]) for x, y in _tpl_raw]
_tpl_ang = math.degrees(math.atan2(_tc[1], _tc[0]))
STAR_HALF_W = max(max(abs(x) for x, _ in _tpl), max(abs(y) for _, y in _tpl))

def star_pts_at(center, arc_r, ang, k=1.0):
    """Traced star template, scaled k, tilted with the arc, at center+polar."""
    th = math.radians(ang - _tpl_ang)
    ca, sa = math.cos(th), math.sin(th)
    cx, cy = center[0] + arc_r * math.cos(math.radians(ang)), center[1] + arc_r * math.sin(math.radians(ang))
    return [((x * ca - y * sa) * k + cx, (x * sa + y * ca) * k + cy) for x, y in _tpl]


placed_stars = [star_pts_at((0, 0), STAR_ARC_R, a) for a in STAR_ANGLES]
stars_2d = Sketch()
for _pts in placed_stars:
    stars_2d += Polygon(*ccw(_pts))

# ---------------------------------- crest ring band: star cutouts (source)
# Band measured 16.15..21.7 mm from the ball center. 8 side stars at the
# source angles - enlarged to 3.4 mm (Brian: "bigger"), recentered on the
# band midline. SCCYSC dropped per Brian (2026-08-06): 3 more stars at
# 69.5/90/110.5 continue the rhythm evenly across the top arc (the 82-deg
# gap splits into 4 x 20.5, mirror-symmetric like the source angles).
# Banner/CITY hide the bottom arc.
# Fine profile of the source (Brian caught this 2026-08-02): the ring is
# main band 16.15..20.7, then a WHITE LINE 20.7..21.3, then a NAVY
# PINSTRIPE 21.3..21.77 - not one solid block out to 21.7.
BAND_R_IN, BAND_R_OUT = 16.15, 20.7
PIN_R_IN = 21.3
PIN_R_OUT = PIN_R_IN + RING_LINE_W   # matches the inner circle width
SMALL_STAR_ARC_R = 18.43                     # band midline
SMALL_STAR_K = 1.7 / STAR_HALF_W             # 3.4 mm across
SMALL_STAR_ANGLES = [343.5, 5, 27, 49, 69.5, 90, 110.5, 131, 153, 175, 196.5]

small_stars_2d = Sketch()
for _a in SMALL_STAR_ANGLES:
    small_stars_2d += Polygon(*ccw(star_pts_at(BALL_C, SMALL_STAR_ARC_R, _a, SMALL_STAR_K)))

band_2d = (
    Pos(*BALL_C) * (Circle(BAND_R_OUT) - Circle(BAND_R_IN))
    + Pos(*BALL_C) * (Circle(PIN_R_OUT) - Circle(PIN_R_IN))   # outer pinstripe
) - small_stars_2d

# ------------------- YOUTH SOCCER CLUB: 1.5x glyphs on a wide flat arch
# Traced glyphs at 1.5x (bars 0.68 mm; 1.3x until Brian asked for bigger
# 2026-08-06). v3.17 (Brian 2026-08-07 "more separation"): at 1.5x the
# letters could only fit the source ball-concentric arc by overlapping
# (they need ~110 deg of arc, ~85 exist under the banner), so the line
# moves to a wide flat arch across the crest bottom, Brian-approved:
# each letter scales about its own center, tilts to the arch's local
# radial, and is ink-kerned along the arch to a uniform gap by bisection
# on its arch angle; the line is then recentered on x=0. Clearances at
# the frozen constants: banner 0.72, pill 0.63, swoosh 0.60 mm (the
# >= 0.3 asserts below still guard them). full: raised navy tier.
# crisp: flush inlay.
YSC_K = 1.2                          # v3.24 (Brian 2026-08-21): back toward the SOURCE size (1.0 = the logo exactly; was 1.5 since v3.15); 1.2 keeps the raised bars >= ~0.54 mm
YSC_LAYOUT = "arc"                   # "arc": the source arc (circle fitted to the traced glyph centers, r ~40); 1.0 = the logo exactly, >1 re-kerned along it; "arch": the v3.17 wide flat arch + kerning (the 1.5x look)
YSC_ARC_DROP = 0.6                   # mm the re-kerned line (YSC_K > 1) is lowered: the longer line's ends climb the arc ~1.6 mm at 1.2x and would touch the banner; 0 at YSC_K 1.0
YSC_GAP = 0.45                       # uniform ink gap between letters, mm
YSC_WORD_MULT = 2.2                  # word breaks = YSC_WORD_MULT * YSC_GAP
YSC_WORD_BREAK_AFTER = {4, 10}       # YOUTH | SOCCER | CLUB
YSC_ARCH_Y_BOT, YSC_ARCH_R = -21.4, 72.0
_ARCH_A = (0.0, YSC_ARCH_Y_BOT + YSC_ARCH_R)   # arch center (letter centers)

from shapely.geometry import Polygon as _SPoly
from shapely.ops import unary_union as _sunion
from shapely.affinity import rotate as _srot, translate as _strans

_ysc_base = []   # per letter: 1.5x-about-own-center rings + kerning shape
for _L in YSC["letters"]:
    _xs = [p[0] for p in _L["outer"]]
    _ys = [p[1] for p in _L["outer"]]
    _c = (((min(_xs) + max(_xs)) / 2 - CX) * S + BALL_DX,
          ((min(_ys) + max(_ys)) / 2 - CY) * S)

    def _scaled(pts):
        return [(_c[0] + ((x - CX) * S + BALL_DX - _c[0]) * YSC_K,
                 _c[1] + ((y - CY) * S - _c[1]) * YSC_K) for x, y in pts]

    _rings = []
    for _part in [_L] + _L.get("extra_parts", []):
        _holes = [_scaled(_h) for _h in _part.get("holes", [])
                  if abs(signed_area(px2mm(_h))) * YSC_K ** 2 > 0.1]
        _rings.append((_scaled(_part["outer"]), _holes))
    _ysc_base.append({
        "rings": _rings, "c": _c,
        "th": math.atan2(_c[1] - BALL_C[1], _c[0] - BALL_C[0]),
        "shape": _sunion([_SPoly(r[0]).buffer(0) for r in _rings]),
    })


def _ysc_place(letter, phi):
    """Letter tilted to the arch radial, center moved onto the arch."""
    g = _srot(letter["shape"], math.degrees(phi - letter["th"]), origin=letter["c"])
    return _strans(g, _ARCH_A[0] + YSC_ARCH_R * math.cos(phi) - letter["c"][0],
                   _ARCH_A[1] + YSC_ARCH_R * math.sin(phi) - letter["c"][1])


_phis = [math.radians(-115)]   # seed; the whole line is recentered below
_placed = [_ysc_place(_ysc_base[0], _phis[0])]
for _i in range(1, len(_ysc_base)):
    _want = YSC_GAP * (YSC_WORD_MULT if (_i - 1) in YSC_WORD_BREAK_AFTER else 1.0)
    _lo, _hi = _phis[-1], _phis[-1] + 0.25
    while _placed[-1].distance(_ysc_place(_ysc_base[_i], _hi)) < _want:
        _hi += 0.10
    for _ in range(36):
        _mid = (_lo + _hi) / 2
        if _placed[-1].distance(_ysc_place(_ysc_base[_i], _mid)) < _want:
            _lo = _mid
        else:
            _hi = _mid
    _phis.append((_lo + _hi) / 2)
    _placed.append(_ysc_place(_ysc_base[_i], _phis[-1]))


def _arch_ang(p):
    return math.atan2(p[1] - _ARCH_A[1], p[0] - _ARCH_A[0])


_e0 = min(_arch_ang(p) for p in _placed[0].convex_hull.exterior.coords)
_e1 = max(_arch_ang(p) for p in _placed[-1].convex_hull.exterior.coords)
_dphi = math.radians(-90) - (_e0 + _e1) / 2   # ink-extent midpoint -> bottom

ysc_2d = Sketch()
for _letter, _phi in zip(_ysc_base, _phis):
    _ca, _sa = math.cos(_phi - _letter["th"]), math.sin(_phi - _letter["th"])
    _cb, _sb = math.cos(_dphi), math.sin(_dphi)
    _cx0, _cy0 = _letter["c"]
    _tx = _ARCH_A[0] + YSC_ARCH_R * math.cos(_phi) - _cx0
    _ty = _ARCH_A[1] + YSC_ARCH_R * math.sin(_phi) - _cy0

    def _T(pts):
        out = []
        for x, y in pts:
            x1 = _cx0 + (x - _cx0) * _ca - (y - _cy0) * _sa + _tx
            y1 = _cy0 + (x - _cx0) * _sa + (y - _cy0) * _ca + _ty
            out.append((_ARCH_A[0] + (x1 - _ARCH_A[0]) * _cb - (y1 - _ARCH_A[1]) * _sb,
                        _ARCH_A[1] + (x1 - _ARCH_A[0]) * _sb + (y1 - _ARCH_A[1]) * _cb))
        return out

    for _outer, _holes in _letter["rings"]:
        _f = Polygon(*ccw(_T(_outer)))
        for _h in _holes:
            _f -= Polygon(*ccw(_T(_h)))
        ysc_2d += _f

# v3.24 (Brian 2026-08-21, "return YOUTH SOCCER CLUB to its original size",
# then "a bit bigger, raised preferred"): YSC_LAYOUT "arc" keeps the SOURCE
# arc (a circle fitted to the traced glyph centers; it is a little flatter
# than ball-concentric). YSC_K 1.0 reproduces the logo exactly (source
# positions, line recentered on x=0). For YSC_K > 1 the glyphs (already
# scaled about their own centers in _ysc_base) are re-kerned along that
# same circle to a uniform YSC_GAP (word breaks YSC_WORD_MULT x) and the
# line is recentered on the source line's own mid-angle, so the ends stay
# where the logo's ends are and the banner/pill clearances hold; growing
# the angular spread instead climbs the ends into the banner corners (the
# v3.17 finding). "arch" keeps the v3.17 flat-arch kerning above.
if YSC_LAYOUT == "arc":
    _AC, _AR, _arc_rms = _fit_circle([_L["c"] for _L in _ysc_base])
    _ang = lambda pt: math.atan2(pt[1] - _AC[1], pt[0] - _AC[0])
    _src_shapes = [_L["shape"] for _L in _ysc_base]
    _src_mid = (min(_ang(p) for p in _src_shapes[0].convex_hull.exterior.coords)
                + max(_ang(p) for p in _src_shapes[-1].convex_hull.exterior.coords)) / 2

    def _arc_place(letter, phi):
        """Letter tilted to the fitted-circle radial at phi, center on the circle (own source radius kept)."""
        th = _ang(letter["c"])
        r = math.hypot(letter["c"][0] - _AC[0], letter["c"][1] - _AC[1])
        g = _srot(letter["shape"], math.degrees(phi - th), origin=letter["c"])
        return _strans(g, _AC[0] + r * math.cos(phi) - letter["c"][0],
                       _AC[1] + r * math.sin(phi) - letter["c"][1]), (th, r)

    if YSC_K == 1.0:
        _phis_arc = [_ang(_L["c"]) for _L in _ysc_base]
    else:
        _phis_arc = [_ang(_ysc_base[0]["c"])]
        _prev = _arc_place(_ysc_base[0], _phis_arc[0])[0]
        for _i in range(1, len(_ysc_base)):
            _want = YSC_GAP * (YSC_WORD_MULT if (_i - 1) in YSC_WORD_BREAK_AFTER else 1.0)
            _lo, _hi = _phis_arc[-1], _phis_arc[-1] + 0.25
            while _prev.distance(_arc_place(_ysc_base[_i], _hi)[0]) < _want:
                _hi += 0.10
            for _ in range(36):
                _mid = (_lo + _hi) / 2
                if _prev.distance(_arc_place(_ysc_base[_i], _mid)[0]) < _want:
                    _lo = _mid
                else:
                    _hi = _mid
            _phis_arc.append((_lo + _hi) / 2)
            _prev = _arc_place(_ysc_base[_i], _phis_arc[-1])[0]
    _placed_arc = [_arc_place(_L, _p)[0] for _L, _p in zip(_ysc_base, _phis_arc)]
    _e0 = min(_ang(p) for p in _placed_arc[0].convex_hull.exterior.coords)
    _e1 = max(_ang(p) for p in _placed_arc[-1].convex_hull.exterior.coords)
    _dphi = _src_mid - (_e0 + _e1) / 2      # line mid-angle back onto the source's
    ysc_2d = Sketch()
    _arc_shapes = []
    for _letter, _phi in zip(_ysc_base, _phis_arc):
        _th, _r = _ang(_letter["c"]), math.hypot(_letter["c"][0] - _AC[0], _letter["c"][1] - _AC[1])
        _rot = _phi + _dphi - _th
        _ca, _sa = math.cos(_rot), math.sin(_rot)
        _cx0, _cy0 = _letter["c"]
        _cx1, _cy1 = _AC[0] + _r * math.cos(_phi + _dphi), _AC[1] + _r * math.sin(_phi + _dphi)

        def _TA(pts):
            return [(_cx1 + (x - _cx0) * _ca - (y - _cy0) * _sa,
                     _cy1 + (x - _cx0) * _sa + (y - _cy0) * _ca) for x, y in pts]

        for _outer, _holes in _letter["rings"]:
            _f = Polygon(*ccw(_TA(_outer)))
            for _h in _holes:
                _f -= Polygon(*ccw(_TA(_h)))
            ysc_2d += _f
        _arc_shapes.append(_strans(_srot(_letter["shape"], math.degrees(_rot), origin=_letter["c"]),
                                   _cx1 - _cx0, _cy1 - _cy0))
    _bx = [g.bounds for g in _arc_shapes]
    _dx = -(min(b[0] for b in _bx) + max(b[2] for b in _bx)) / 2
    _dy = -YSC_ARC_DROP if YSC_K != 1.0 else 0.0
    ysc_2d = Pos(_dx, _dy) * ysc_2d
    _arc_shapes = [_strans(g, _dx, _dy) for g in _arc_shapes]
    _arc_gaps = [_arc_shapes[i].distance(_arc_shapes[i + 1]) for i in range(len(_arc_shapes) - 1)]
    _arc_union = _sunion(_arc_shapes)
    _ub = _arc_union.bounds
    print(f"YSC arc layout x{YSC_K}: fitted arc r {_AR:.1f} (rms {_arc_rms:.2f}), {len(_ysc_base)} glyphs, "
          f"line {_ub[2] - _ub[0]:.1f} x {_ub[3] - _ub[1]:.1f} mm, y {_ub[1]:.1f}..{_ub[3]:.1f}, "
          f"span {math.degrees(_e1 - _e0):.1f} deg, ink gaps min {min(_arc_gaps):.2f} max {max(_arc_gaps):.2f} mm, "
          f"mean stroke 2A/P {2 * _arc_union.area / _arc_union.length:.2f} mm")


# ------------------------------- CITY oval (restored per Brian, 2026-08-01)
# Source position and size, transformed with the banner line so the pill
# stays interlocked with the short/notched T, A, C exactly as drawn. The
# pill top merges invisibly into the banner navy; white ring/letters/dots
# punch through all navy via subtraction.
city_pill_2d = line_sketch(CITY["pill"])
city_white_2d = fillet_line_sketch(CITY["white"], FILLET_R, min_hole_area=0.1)
if FILLET_R:
    print(f"letter+CITY fillet r={FILLET_R} rungs: {_FILLET_RUNGS}")
if _FILLET_DEBUG and os.environ.get("FILLET_DEBUG"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _fig, _ax = plt.subplots(figsize=(18, 8), dpi=220)
    for _sp, _sm in _FILLET_DEBUG:
        for _g, _c, _lw in ((_sp, "0.6", 1.1), (_sm, "crimson", 0.55)):
            _ax.plot(*zip(*_g.exterior.coords), color=_c, lw=_lw)
            for _h in _g.interiors:
                _ax.plot(*zip(*_h.coords), color=_c, lw=_lw)
    _ax.set_aspect("equal")
    _ax.set_title(f"letter micro-fillet r={FILLET_R} (gray = source, red = filleted)")
    _fig.savefig(f"{SCRATCH}/fillet-debug-r{FILLET_R}.png", bbox_inches="tight")
    plt.close(_fig)

# ---------------------------- crisp: 0.4-nozzle rebuild of the ball web
# The traced seam/rim lines of the ball run 0.17-0.45 mm and vanished in
# the first 0.4 test print (classic walls drop anything under 2
# perimeters). v3.16 grew every thin member morphologically to
# MIN_LINE_W; Brian (2026-08-20): "the soccer ball is messy" - the grown
# seams came out lumpy with knobby ends. v3.22 rebuilds the web from
# clean parts instead: the solid pentagons and rim lenses keep their
# traced outlines, the rim hairline becomes an exact annulus, and every
# seam hairline becomes a uniform STROKE_W stroke on a line or arc
# fitted through the hairline, run into its pentagon, the rim, or the
# surfer/navy clip (a protected 0.42 mm white halo surrounds the surfer;
# the source margin is 0.137 mm, which would fuse at print). Done in
# shapely on the refined lines/arcs sampled at 0.1 mm - OCC wire offsets
# return null on this concave web. full keeps the source trace for the
# 0.2 nozzles.
SURFER_HALO = 0.42

if DETAIL == "crisp":
    from shapely.geometry import Polygon as ShapelyPoly, Point as ShapelyPoint, box as shapely_box
    from shapely.ops import unary_union
    from shapely import simplify as shapely_simplify

    def _sampled_ring(pts_px, shift, step=0.1):
        """One trace ring as its refined lines/arcs, sampled every step mm."""
        def T(p):
            return ((p[0] - CX) * S + shift, (p[1] - CY) * S)

        out = []
        for e in _refined_edges(ccw(pts_px)):
            if e[0] == "line":
                a, b = T(e[1]), T(e[2])
                n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
                out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                        for k in range(n)]
            else:
                a, m, b = T(e[1]), T(e[2]), T(e[3])
                (cx, cy), r, _ = _fit_circle([a, m, b])
                th0 = math.atan2(a[1] - cy, a[0] - cx)
                thm = math.atan2(m[1] - cy, m[0] - cx)
                th1 = math.atan2(b[1] - cy, b[0] - cx)

                def unwrap(frm, to):
                    while to < frm - 1e-12:
                        to += 2 * math.pi
                    return to

                f1 = unwrap(th0, thm)
                f2 = unwrap(f1, th1)
                if f2 - th0 > 2 * math.pi:  # arc runs clockwise instead
                    f1 = thm if thm < th0 else thm - 2 * math.pi
                    f2 = th1 if th1 < f1 else th1 - 2 * math.pi
                n = max(2, int(abs(f2 - th0) * r / step))
                out += [(cx + r * math.cos(th0 + (f2 - th0) * k / n),
                         cy + r * math.sin(th0 + (f2 - th0) * k / n)) for k in range(n)]
        return out

    _web_faces = []
    for _poly in LAYERS["ball_cyan"]:
        _holes = [_sampled_ring(h, BALL_DX) for h in _poly.get("holes", [])
                  if abs(signed_area(px2mm(h))) > 0.5]
        _web_faces.append(ShapelyPoly(_sampled_ring(_poly["outer"], BALL_DX), _holes))
    _web = unary_union([f.buffer(0) for f in _web_faces])
    assert abs(_web.area - ball_cyan_2d.area) / ball_cyan_2d.area < 0.01, \
        "shapely web sampling diverged from the refined faces"

    def _ann(r0, r1):
        return ShapelyPoint(BALL_C).buffer(r1, quad_segs=256).difference(
            ShapelyPoint(BALL_C).buffer(r0, quad_segs=256))

    _banner = shapely_box(BAN_C[0] - BAN_W / 2 + BAN_R, BAN_C[1] - BAN_H / 2 + BAN_R,
                          BAN_C[0] + BAN_W / 2 - BAN_R, BAN_C[1] + BAN_H / 2 - BAN_R
                          ).buffer(BAN_R, quad_segs=32)
    _surfer = ShapelyPoly(smoothed_ring_mm(SURFER["outer"], BALL_DX))
    _clip = unary_union([_ann(BALL_R, BALL_R + RING_LINE_W), _ann(BAND_R_IN, BAND_R_OUT),
                         _banner, _surfer.buffer(SURFER_HALO, quad_segs=16)])

    def _opening(g, r):
        return g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)

    def _eff_w(p):
        return 2 * p.area / p.length if p.length > 0 else 0.0

    def _thin_members(g, min_area=0.30, min_eff=0.15):
        """Sub-WEB_FLOOR members (arachne single-bead floor since v3.23);
        hairline opening artifacts and junction wedges filtered out (they
        print as slight blunting, not breaks)."""
        thin = g.difference(_opening(g, WEB_FLOOR / 2))
        return [p for p in getattr(thin, "geoms", [thin])
                if p.area >= min_area and _eff_w(p) >= min_eff]

    # v3.22 (2026-08-20): clean rebuild. Pieces of the web:
    #  (1) pentagons + rim lenses: a 0.35 mm opening finds their cores
    #      (no hairlines), the intersection with the web restores the
    #      ORIGINAL traced outline with sharp corners;
    #  (2) rim hairline: exact annulus STROKE_W wide inside the navy ring;
    #  (3) seams: each remaining hairline member (>= SEAM_MIN_AREA,
    #      >= SEAM_MIN_LEN) gets a centerline from cross-section
    #      centroids along its principal axis, fitted to a line or a
    #      gentle arc, each end run into a hiding region (pentagon core,
    #      rim ring, or clip) so no cap shows, then buffered to STROKE_W.
    # Sub-floor stubs left on the pentagons (clipped corner tips, seam
    # stubs too short for a stroke) are TRIMMED to a clean edge rather
    # than grown; a CLOSE_R closing fillets the acute white wedges where
    # strokes meet pentagon sides, as the source art does. Layout,
    # pentagon outlines, and seam positions stay traced.
    STROKE_W = SEAM_W   # v3.23: 0.6 mm hairline-look seams (arachne single bead); WEB_FLOOR leaves a 0.05 audit margin
    SEAM_MIN_AREA, SEAM_MIN_LEN = 0.25, 1.5   # hairline members worth a stroke; shorter stubs are invisible at this scale
    ARC_MIN_R, ARC_SAG = 4.0, 0.06            # arc fit only for gentle curves; flatter than ARC_SAG -> straight line
    CAP_MAX, CAP_MARGIN = 1.5, 0.15           # end-cap hiding: march up to CAP_MAX until both cap corners are hidden
    CLOSE_R = 0.15                            # junction fillet radius (fills white wedges narrower than 2 * CLOSE_R)
    import numpy as _np
    from shapely.geometry import LineString as ShapelyLine

    _opened = _opening(_web, 0.35)                                     # pentagon + lens cores
    _patches = _web.intersection(_opened.buffer(0.35, quad_segs=16))    # ... with their traced outlines
    _rim = _ann(BALL_R - STROKE_W, BALL_R)
    _hair = _web.difference(_opened.buffer(0.2, quad_segs=16)).difference(_ann(BALL_R - 0.8, BALL_R + 1.0))
    _hide = unary_union([_opened, _rim, _clip])   # regions that hide a stroke end cap

    def _seam_centerline(m):
        """Cross-section centroids along the member's principal axis, fitted to a line or a gentle arc."""
        pts = _np.array(m.exterior.coords)[:-1]
        c = pts.mean(0)
        ax = _np.linalg.svd(pts - c, full_matrices=False)[2][0]
        nrm = _np.array([-ax[1], ax[0]])
        t = (pts - c) @ ax
        t0, L = t.min(), t.max() - t.min()
        centers = []
        for f in _np.linspace(0.03, 0.97, max(9, int(L / 0.25))):
            base = c + (t0 + f * L) * ax
            cut = ShapelyLine([base - nrm * 3, base + nrm * 3]).intersection(m)
            if not cut.is_empty:
                centers.append((cut.centroid.x, cut.centroid.y))
        if len(centers) < 4:
            return None
        P = _np.array(centers)
        k = len(centers) // 5
        Pm = P[k:len(centers) - k] if k else P           # middle 60 %: junction flare excluded from the fit
        cm = Pm.mean(0)
        d = _np.linalg.svd(Pm - cm, full_matrices=False)[2][0]
        n = _np.array([-d[1], d[0]])
        proj = (P - cm) @ d
        A, B = cm + proj.min() * d, cm + proj.max() * d
        sag = max(abs((q - cm) @ n) for q in P)
        (cx, cy), r, rms = _fit_circle(centers)
        if sag < ARC_SAG or r < ARC_MIN_R or rms > 0.05:
            return [tuple(A), tuple(B)]
        a0, a1 = math.atan2(A[1] - cy, A[0] - cx), math.atan2(B[1] - cy, B[0] - cx)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        nn = max(4, int(abs(da) * r / 0.1))
        return [(cx + r * math.cos(a0 + da * j / nn), cy + r * math.sin(a0 + da * j / nn)) for j in range(nn + 1)]

    def _seam_end(line, at_end):
        """Run one stroke end into its pentagon, the rim, or the clip so no cap shows."""
        e, prev = (_np.array(line[-1]), _np.array(line[-2])) if at_end else (_np.array(line[0]), _np.array(line[1]))
        d = e - prev
        d = d / _np.linalg.norm(d)
        half = _np.array([-d[1], d[0]]) * STROKE_W / 2
        s = 0.0
        if _patches.distance(ShapelyPoint(e)) < 0.5:
            kind = "patch"
            while s < CAP_MAX and not (_hide.contains(ShapelyPoint(e + d * s + half))
                                       and _hide.contains(ShapelyPoint(e + d * s - half))):
                s += 0.05
            s += CAP_MARGIN
        elif math.hypot(e[0] - BALL_C[0], e[1] - BALL_C[1]) > BALL_R - 1.2:
            kind = "rim"
            while s < 3.0 and math.hypot(*(e + d * s - _np.array(BALL_C))) < BALL_R + 0.3:
                s += 0.05
        elif _clip.distance(ShapelyPoint(e)) < 0.6:
            kind = "clip"
            while s < 1.2 and not _clip.contains(ShapelyPoint(e + d * s)):
                s += 0.05
            s += 0.4
        else:
            kind = "free"
        p = tuple(e + d * s)
        return (line + [p] if at_end else [p] + line), kind

    _strokes, _seam_log = [], []
    for _m in getattr(_hair, "geoms", [_hair]):
        if _m.is_empty or _m.area < SEAM_MIN_AREA:
            continue
        _pts = _np.array(_m.exterior.coords)
        _len = math.sqrt(((_pts[:, None, :] - _pts[None, :, :]) ** 2).sum(-1).max())
        if _len < SEAM_MIN_LEN:
            continue
        _cl = _seam_centerline(_m)
        if _cl is None:
            continue
        _cl, _ka = _seam_end(_cl, False)
        _cl, _kb = _seam_end(_cl, True)
        _ls = ShapelyLine(_cl)
        _strokes.append(_ls.buffer(STROKE_W / 2, cap_style=2, join_style=1))
        _seam_log.append((_ka, _kb, round(_ls.length, 2)))
    assert 8 <= len(_strokes) <= 14, f"ball seam count off: {len(_strokes)} {_seam_log}"
    assert all(k != "free" for ka, kb, _ in _seam_log for k in (ka, kb)), f"free-floating seam end: {_seam_log}"
    for _st, _lg in zip(_strokes, _seam_log):
        assert abs(_st.area / _lg[2] - STROKE_W) < 0.03, f"seam stroke width off: {_st.area / _lg[2]:.3f}"

    _wide = unary_union([_patches, _rim] + _strokes)
    _wide = _wide.buffer(CLOSE_R, quad_segs=16).buffer(-CLOSE_R, quad_segs=16).difference(_clip)
    for _rnd in range(4):   # trim sub-floor stubs on the pentagons to a clean edge
        _stubs = [p for p in _thin_members(_wide, 0.05, 0.10) if p.intersects(_opened)]
        if not _stubs:
            break
        _wide = _wide.difference(unary_union([p.buffer(0.01, quad_segs=8) for p in _stubs]))
    # members pinned against the clip can never reach min width by
    # growing: remove them so the line ends cleanly at the clip instead
    # of leaving a strand that breaks mid-print (v3.19 review caught a
    # 1 mm 0.25-wide seam break at the surfer halo, area 0.28 - detect
    # these with a finer filter than the assert uses)
    _pinned = [p for p in _thin_members(_wide, 0.05, 0.10)
               if p.buffer(0.03).intersects(_clip)]
    if _pinned:
        _wide = _wide.difference(unary_union([p.buffer(0.02) for p in _pinned]))
    _wide = shapely_simplify(_wide.buffer(0), 0.02)
    assert not _thin_members(_wide), "ball web still has sub-min-width members"
    assert 1.0 < _wide.area / _web.area < 1.5, \
        f"ball web widening area ratio off: {_wide.area / _web.area:.2f}"
    assert all(_wide.contains(ShapelyPoint(BALL_C[0] + (BALL_R - STROKE_W / 2) * math.cos(math.radians(_a)),
                                           BALL_C[1] + (BALL_R - STROKE_W / 2) * math.sin(math.radians(_a))))
               for _a in range(-25, 206, 5)), "cyan rim ring broken"
    print(f"ball web v3.22: {len(_strokes)} seams {_seam_log}, area ratio {_wide.area / _web.area:.2f}")

    ball_cyan_2d = Sketch()
    for _g in getattr(_wide, "geoms", [_wide]):
        _f = Polygon(*ccw(list(_g.exterior.coords)[:-1]))
        for _i in _g.interiors:
            _f -= Polygon(*ccw(list(_i.coords)[:-1]))
        ball_cyan_2d += _f

# ------------------------------------------------------------ color assembly
white_t2_2d = (border_2d - city_pill_2d) + letters_2d + city_white_2d
navy_parts_2d = (swoosh_2d - stars_2d) + ballring_2d + band_2d + banner_2d + city_pill_2d
if DETAIL == "full":
    navy_parts_2d += ysc_2d
navy_t1_2d = navy_parts_2d - white_t2_2d
cyan_t1_2d = (ball_cyan_2d + stars_2d) - navy_t1_2d

# ------------------------------------- back: debossed name + number (mirror)
DEBOSS_T = 0.6


def fitted_text(s, cap_h, max_w, y):
    t = Text(s, font_size=10, font="DejaVu Sans", font_style=FontStyle.BOLD)
    tb = t.bounding_box()
    k = min(cap_h / tb.size.Y, max_w / tb.size.X)
    return Pos(0, y) * scale(t, (k, k, 1))


# Number dead-center on the disc (Brian 2026-08-07); name above and
# years below with matching 3 mm gaps to the number's 24 mm cap band.
back_2d = (
    fitted_text(KID_NAME.upper(), 9.0, 56.0, 19.5)
    + fitted_text(KID_NUMBER, 24.0, 40.0, 0.0)
    + fitted_text(TEAM_YEARS, 6.0, 40.0, -18.0)
)
back_cut = extrude(mirror(back_2d, Plane.YZ), DEBOSS_T)

# ------------------------------------------------------------------- solids
disc = Cylinder(DISC_R, BASE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
hole = Pos(*HOLE_POS) * Cylinder(HOLE_D / 2, 20)

navy_body = (
    extrude(Pos(0, 0, BASE_T) * navy_t1_2d, TIER1_T)
    + extrude(Pos(0, 0, BASE_T) * surfer_2d, TIER1_T + TIER2_T)
    + back_cut   # back text inlaid flush in navy (Brian 2026-08-01)
)
cyan_body = extrude(Pos(0, 0, BASE_T) * cyan_t1_2d, TIER1_T)
white_art_body = extrude(Pos(0, 0, BASE_T) * white_t2_2d, TIER1_T + TIER2_T)
white_body = disc - hole - back_cut + white_art_body

# Front micro-text (crisp/0.4): strokes keyed INLAY_T into the disc so
# they anchor like the back name inlay, raised YSC_RAISE proud of the
# disc top (v3.21, Brian 2026-08-08; flush before that). The raised
# portion's 0.68 mm bars sit under the 0.84 mm classic-wall floor, so
# the slicer may drop them back to flush - flagged, not adapted, per
# the source-fidelity rule. DETAIL=full keeps the raised original.
INLAY_T = 0.24   # 2 layers at 0.12
YSC_RAISE = 0.5  # v3.26: raised again per Brian (0.0 = the v3.25 flush inlay)
if DETAIL == "crisp":
    ysc_inlay = extrude(Pos(0, 0, BASE_T - INLAY_T) * ysc_2d, INLAY_T + YSC_RAISE)
    navy_body = navy_body + ysc_inlay   # navy letters keyed into the disc top
    white_body = white_body - ysc_inlay

# ------------------------------------------------------------------- checks
assert len(white_body.solids()) == 1, \
    f"white body: {len(white_body.solids())} solids, expected 1"
wb = white_body.bounding_box()
assert abs(wb.size.X - DISC_D) < 0.01 and abs(wb.max.Z - Z2) < 0.01

for a, b, lbl in ((navy_body, cyan_body, "navy/cyan"),
                  (navy_body, white_body, "navy/white"),
                  (cyan_body, white_body, "cyan/white")):
    inter = a & b
    assert inter.volume < 1e-6, f"{lbl} overlap: {inter.volume:.4f} mm^3"

hole_probe = Pos(*HOLE_POS) * Cylinder(HOLE_D / 2 + 0.8, 20)
for body, lbl in ((navy_body, "navy"), (cyan_body, "cyan")):
    assert (body & hole_probe).volume < 1e-6, f"{lbl} artwork crowds the hang hole"

star_pts = [pt for pts in placed_stars for pt in pts]
d_star = min(math.hypot(x - HOLE_POS[0], y - HOLE_POS[1]) for x, y in star_pts) - HOLE_D / 2
assert d_star >= 1.0, f"hole too close to stars: {d_star:.2f} mm"

# hole rim must keep a printable wall to the disc edge
_rim = DISC_R - (HOLE_POS[1] + HOLE_D / 2)
assert _rim >= 3.0, f"hole rim wall too thin: {_rim:.2f} mm"

# adjacent stars must not touch each other
for _a, _b in zip(placed_stars, placed_stars[1:]):
    assert (Polygon(*ccw(_a)) & Polygon(*ccw(_b))).area < 1e-6, "adjacent stars overlap"

# CITY pill: source position must still overlap the banner bottom edge
assert (city_pill_2d & banner_2d).area > 5.0, "CITY pill no longer overlaps the banner"

# YOUTH SOCCER CLUB must stay clear of pill, banner, and swoosh (0.3 mm)
_ysc_probe = offset(ysc_2d, 0.3)
for _other, _lbl in ((city_pill_2d, "CITY pill"), (banner_2d, "banner"), (swoosh_2d, "swoosh")):
    inter = _ysc_probe & _other
    assert inter.area < 1e-6, f"YOUTH SOCCER CLUB within 0.3 mm of {_lbl}: {inter.area:.3f} mm2 at x {inter.bounding_box().min.X:.1f}..{inter.bounding_box().max.X:.1f} y {inter.bounding_box().min.Y:.1f}..{inter.bounding_box().max.Y:.1f}"

# S and Z must sit one frame-margin away from the frame on both sides
_frame_inner_x = BAN_W / 2 - BORDER_INSET - BORDER_W
_lbb = letters_2d.bounding_box()
for _gap in (_frame_inner_x - _lbb.max.X, _lbb.min.X - (-_frame_inner_x)):
    assert abs(_gap - LETTER_FRAME_GAP) < 0.1, f"letter-frame gap {_gap:.2f} != {LETTER_FRAME_GAP}"

# stars must stay clear of the swoosh (>=1.0 mm gap, exact silhouette check)
for _pts, _ang in zip(placed_stars, STAR_ANGLES):
    inter = swoosh_2d & offset(Polygon(*ccw(_pts)), 1.0)
    assert inter.area < 1e-6, f"swoosh within 1.0 mm of star at {_ang} deg: {inter.area:.3f} mm^2"

# ------------------------------------------------------------------- export
export_stl(white_body, f"{SCRATCH}/wip-white.stl")
export_stl(navy_body, f"{SCRATCH}/wip-navy.stl")
export_stl(cyan_body, f"{SCRATCH}/wip-cyan.stl")

import trimesh

for stem in ("white", "navy", "cyan"):
    m = trimesh.load_mesh(f"{SCRATCH}/wip-{stem}.stl")
    assert m.is_watertight, f"{stem} STL not watertight"
    assert m.volume > 100, f"{stem} STL implausibly small"

if os.environ.get("FINAL"):
    _sfx = "-full" if DETAIL == "full" else ""
    export_stl(white_body, f"{HERE}/sharks-nametag-white{_sfx}.stl")
    export_stl(navy_body, f"{HERE}/sharks-nametag-navy{_sfx}.stl")
    export_stl(cyan_body, f"{HERE}/sharks-nametag-cyan{_sfx}.stl")

print("all checks passed:", KID_NAME, KID_NUMBER, f"({DETAIL}) | star clearance {d_star:.2f} mm")

if os.environ.get("SHOW"):
    from ocp_vscode import show, Camera
    show(white_body, navy_body, cyan_body, names=["white", "navy", "cyan"],
         colors=["#f2f2f2", "#00395e", "#31bad6"],
         reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
