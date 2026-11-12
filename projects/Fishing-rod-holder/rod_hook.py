#!/usr/bin/env python
"""Rod hooks: printed deep hooks that screw to the face of a 1x4, three versions in one file.

Brian's picks, 2026-11-07: "use the deep hook design ... make individual deep
hooks that can be screwed into a 1x4 piece of wood." Then: "make the bottom
resting part of the hook have a slot that is angled to help keep the rod there
better" and "remove the top most part of the device that is not over the wood."
Then: "you did the opposite angle for the slot. The slot should angle away from
the wood." And: "5 holders should fit in the 20 in. There should be no space
between each hook as it sits on the wood." So a hook is 4 in tall and five of
them, butted, fill the board's 20 in hang. And: "can you print these vertically
so there can be much more in a single print": the print STLs stand the hook on
its 4 in bottom edge (face vertical, holes horizontal).

2026-11-09: "There should be 2 versions of the holder. One that we already have
is for the rod tip end. The rod butt end should be able to accommodate a 2 in
rod handle. The rods I have are 1 7/8 in or so. Make it a 2 in opening." And:
"make both versions in the same file, vertical." And: "the holders will stack on
top of each other, make sure there is 2 in of room to get the butt in." So:

  TIP   7/8 slot leaning 35 degrees for the blank (1/4 to 5/8 in), as built 2026-11-07.
  BUTT  2 in slot for the grip. The height budget rules it: the grip has to pass between
        the lip tip and the hook butted above (4 in up), so the tip sits at 1-3/4 (a
        2-1/4 in gap), the floor is 5/16 and the lean is 10 degrees, the most that still
        leaves the lip a straight inner face above its R 1/8 corner. Hold: about 1-7/16 in
        of lift (the tip hook: 1-9/16).

Later that day: "all edges should have a very slight roundover", then "do not add a round
over to the back of the part. Use this flat surface to print the part vertically." So the
front face's outline and the countersink rims are rounded EDGE_R (1/32); the back face
(against the board) and the bottom strip the standing print sits on stay flat and square.
The outline is built from lines and true arcs so the kernel can roll that fillet around
it, and the overhang check reads the standing print layer by layer, as the slicer does.

2026-11-11: "The 2" version is fine. Let's create a 1.5" version. But with the 1.5" make
sure to incorporate the angled slot like in the original design." And: "the 3MF file
should have all 3 versions in it." So a third hook:

  SLIM  1-1/2 in slot leaning 35 degrees, the tip hook's lean, for slimmer grips (about 1 to
        1-3/8 in). The same budget, and here it leaves room for the lean: the lip is the tip
        hook's (top at 1-7/8 climbing to a 2-1/4 tip, a 1-3/4 in gap under the hook above),
        the floor is the 2 in hook's 5/16, and the 1-1/2 in bottom still has a straight
        leaning wall above it on both sides. Hold: about 1-7/8 in of lift.

Each hook is an open J: a tab that screws to the board face (two #8), and a jaw
that reaches past the board edge carrying a slot that leans away from the wood
as it goes down (SLOT_LEAN from vertical). The rod drops in at the top, slides
down the ramp away from the board and comes to rest at the bottom; to leave it
has to come back up the ramp toward the board and then over the lip tip, under
the hook above. The lip top slopes up toward its tip so a rod set on it rolls
in. The rod lies beside the wood in the slot and never touches the board. The
board hangs from the joist the way the wooden combs do.

Coordinates (inches in the constants, mm in the CAD): x along the board width,
x = 0 at the board edge the jaw reaches past, positive onto the board; y up,
y = 0 at the hook's bottom edge; z the hook thickness, z = 0 against the board.
The rod runs along z. `<stem>-model.stl` is this frame (for the scene renders);
`<stem>.stl` is the print frame: standing on the bottom edge, x along the bed
from the jaw tip, y the thickness, z up. Stems: rod-hook (tip), rod-hook-butt (2 in),
rod-hook-slim (1-1/2 in).

Run from the vault root:
  .venv/bin/python projects/Fishing-rod-holder/rod_hook.py          # build, check, export all three
  SHOW=reset .venv/bin/python projects/Fishing-rod-holder/rod_hook.py  # also push all three to the OCP viewer
"""
import json
import math
import os
from pathlib import Path

from build123d import Axis, Box, Cone, Cylinder, Line, Location, Pos, ThreePointArc, Wire, export_stl, extrude, fillet, make_face
from shapely.affinity import translate as stranslate
from shapely.geometry import Point, Polygon as SPoly, box as sbox
from shapely.ops import unary_union

PROJECT = Path(__file__).resolve().parent
IN = 25.4

# ---- the board (a 1x4 on edge, as Brian's combs) -------------------------------
BOARD_W = 3.5
BOARD_T = 0.75

# ---- shared by all the hooks -------------------------------------------------------
T = 0.375          # hook thickness (3/8)
TAB = 1.75         # how far the tab reaches onto the board face (screws live here)
HANG = 20.0        # the board's hang below the joist (Brian's combs)
HOOKS_PER_BOARD = 5
H = HANG / HOOKS_PER_BOARD   # tab height: five hooks butted fill the hang, 4 in each
WEB = 0.125        # the tab's outer edge past the board edge, so the rod never rubs the wood
LIP_MIN = 0.5      # lip thickness at its thinnest, beside the slot's bottom
CORNER_R = 0.25    # top corners of the tab
FOOT_R = 0.0       # bottom corners square: the bottom strip is the flat surface the standing print sits on (Brian 2026-11-09)
TIP_R = 0.125      # lip tip and the slot's top edges
RAMP_R = 0.125     # where the tab edge turns into the slot's ramp
EDGE_R = 1 / 32    # the roundover on the front face's edges (Brian 2026-11-09: "very slight"); the back face and the bottom
                   # strip stay square ("do not add a round over to the back of the part. Use this flat surface to print
                   # the part vertically")
LAYER_H = 0.3      # mm, the layers the 3MF prints with (0.30mm Standard); the overhang check reads the print at this pitch
MAX_OVERHANG = 45.0  # degrees from vertical the printer manages without support
EXIT_MARGIN = 0.25   # room past the biggest rod between the lip tip and the hook butted above

# ---- screws: two #8, countersunk, 1 in from the board edge --------------------------
SCREW_X = 1.0
SCREW_Y = (0.5625, H - 0.5625)         # 9/16 up from the bottom, 9/16 down from the top
HOLE_D = 5.0                           # mm, #8 clearance
CSK_D = 10.0                           # mm, 90 degree countersink at the front face
CSK_DEPTH = (CSK_D - HOLE_D) / 2       # 2.5 mm


class Hook:
    """One version of the hook: the slot and lip numbers, and everything derived from them."""

    def __init__(self, name, stem, holds, slot_w, slot_lean, below, y_lip, lip_slope, rod_dias, slot_margin, min_lift, min_exit_gap, label=None):
        self.name, self.stem, self.holds = name, stem, holds
        self.label = label or name      # what Brian calls it: "<label> hook" in the plate names, the page and the viewer
        self.MIN_EXIT_GAP = min_exit_gap  # room between the lip tip and the hook butted above, Brian's floor
        self.SLOT_W = slot_w            # slot width, measured across the slot
        self.SLOT_LEAN = slot_lean      # degrees from vertical; the slot's bottom sits away from the wood
        self.BELOW = below              # material under the slot's lowest point
        self.Y_LIP = y_lip              # lip top at its inner edge (where the slot opens)
        self.LIP_SLOPE = lip_slope      # lip top climbs this much toward its tip: a rod set on the lip rolls in
        self.ROD_DIAS = rod_dias        # what the slot must hold and release
        self.SLOT_MARGIN = slot_margin  # slot width over the biggest of those
        self.MIN_LIFT = min_lift        # the hold check: no escape below this rise (the plain deep hook gave 1.00)

        self.X_BACK = -WEB                                  # the tab's outer edge
        self.R_SLOT = slot_w / 2
        self.PHI = math.radians(slot_lean)
        self.Y_C = below + self.R_SLOT                      # centre of the slot's rounded bottom
        R, PHI, Y_C = self.R_SLOT, self.PHI, self.Y_C
        # the slot's inner wall (the ramp) leaves the tab edge at Y_LIP and leans outward going down
        self.S_IN = (y_lip - Y_C + R * math.sin(PHI)) / math.cos(PHI)        # ramp length from the bottom tangent to the tab edge
        self.X_C = self.X_BACK - R * math.cos(PHI) - self.S_IN * math.sin(PHI)  # slot bottom centre, x
        self.S_OUT = (y_lip - Y_C - R * math.sin(PHI)) / math.cos(PHI)       # outer wall length to the lip top
        assert self.S_OUT >= 0, f"{name}: the lip has no straight inner face (lean {slot_lean} too steep for the height)"
        self.X_LIP_TOP = self.X_C + self.S_OUT * math.sin(PHI) - R * math.cos(PHI)  # lip's inner top edge
        self.CANT = math.ceil((-(self.X_C - R) + LIP_MIN) * 8) / 8          # jaw reach past the board edge, to the next 1/8
        self.W = self.CANT + TAB                            # overall width
        self.Y_REST = below                                 # the rod's lowest contact
        self.Y_TIP = y_lip + lip_slope                      # lip top at the tip: the lift to leave is about Y_TIP - rest
        self.HOOD = self.X_LIP_TOP - self.X_C               # how far the lip's top edge reaches inboard of the resting rod's centre

    # ---- outline ------------------------------------------------------------------------
    def outline_items(self):
        """The sharp outline (inches, y up), counterclockwise from the jaw's bottom tip: each corner with
        the fillet radius to apply at it, and the slot's rounded bottom as the arc it is, from the ramp's
        tangent point (the inner one, at -PHI from +x) around the low point to the outer wall's."""
        return [("corner", (-self.CANT, 0.0), FOOT_R), ("corner", (TAB, 0.0), FOOT_R),
                ("corner", (TAB, H), CORNER_R), ("corner", (self.X_BACK, H), CORNER_R),
                ("corner", (self.X_BACK, self.Y_LIP), RAMP_R),
                ("arc", (self.X_C, self.Y_C), self.R_SLOT, -self.PHI, -math.pi, 32),
                ("corner", (self.X_LIP_TOP, self.Y_LIP), TIP_R), ("corner", (-self.CANT, self.Y_TIP), TIP_R)]

    def path(self):
        """The outline with its corners rounded: points and true arcs, what the CAD builds and the checks sample."""
        return rounded_path(self.outline_items())

    def final_outline(self):
        """The outline as points (every arc sampled, tangent points exact), for the 2D checks and the drawings."""
        return path_points(self.path())

    # ---- solids -------------------------------------------------------------------------
    def build(self):
        hook = extrude(path_face(self.path()), T * IN, dir=(0, 0, 1))
        for y in SCREW_Y:
            hook -= Pos(SCREW_X * IN, y * IN, T * IN / 2) * Cylinder(HOLE_D / 2, T * IN + 2)
            cone_h = CSK_D / 2 + 0.3
            hook -= Pos(SCREW_X * IN, y * IN, T * IN + 0.3 - cone_h / 2) * Cone(0.0, cone_h, cone_h)
        return self.round_edges(hook)

    def round_edges(self, hook):
        """The front face's outline and the countersink rims rounded over EDGE_R, less the stretch along the
        bottom: the back face (z = 0, against the board) and the bottom strip (y = 0, the bed of the standing
        print) stay flat and square, so their edges and the two bottom corners are left alone. The outline's
        other corners are already arcs, so their vertical edges are smooth and are not filleted."""
        front = [e for e in hook.edges().group_by(Axis.Z)[-1] if e.center().Y > 1e-6]
        rounded = fillet(front, EDGE_R * IN)
        assert len(rounded.solids()) == 1, f"{self.name}: the roundover broke the hook into {len(rounded.solids())} solids"
        assert hook.volume - rounded.volume > 0, f"{self.name}: the roundover removed nothing"
        # the two flat surfaces: the back face keeps its full outline; the bottom strip stays one flat face and loses only
        # the two slivers where the front side edges' rounds run out across its front corners
        back0, back1 = hook.faces().group_by(Axis.Z)[0], rounded.faces().group_by(Axis.Z)[0]
        assert len(back1) == 1 and abs(back1[0].area - back0[0].area) < 1e-6, f"{self.name}: the roundover touched the back face"
        foot0, foot1 = hook.faces().group_by(Axis.Y)[0], rounded.faces().group_by(Axis.Y)[0]
        sliver = (1 - math.pi / 4) * (EDGE_R * IN) ** 2
        assert len(foot1) == 1 and 0 <= foot0[0].area - foot1[0].area <= 2 * sliver + 1e-6, f"{self.name}: the roundover touched the bottom strip"
        return rounded

    def standing(self, hook):
        """The print frame: stand the hook on its bottom edge. Model y (up) becomes z,
        the thickness lies along y, the jaw tip is at x = 0."""
        return hook.rotate(Axis.X, 90).moved(Location((self.CANT * IN, T * IN, 0)))

    def overhang_report(self, stl_path):
        """Steepest overhang of the standing print, in degrees from vertical, read layer by layer the way the
        slicer sees it: each LAYER_H layer's outline against the one below, the step between them being the
        overhang (facet normals overstate a small round: a quarter-round inside two layers faces straight down
        yet prints as a 40 degree step). The first layer sits on the bed and the screw holes are 5 mm horizontal
        bridges, so neither counts."""
        import numpy as np
        import trimesh
        m = trimesh.load(str(stl_path))
        n_layers = int(round(H * IN / LAYER_H))
        heights = [(k + 0.5) * LAYER_H for k in range(n_layers)]
        sections = m.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=heights)
        layers = [unary_union(s.polygons_full) if s is not None else SPoly() for s in sections]
        lo, hi = m.bounds
        assert np.allclose(unary_union(layers).bounds, [lo[0], lo[1], hi[0], hi[1]], atol=1.0), "the sections are not in the STL's x, y"
        holes = [((self.CANT + SCREW_X) * IN, y * IN) for y in SCREW_Y]   # hole axes along y at (x, z) in the print frame
        worst = 0.0
        for k in range(1, n_layers):
            z, below, cur = heights[k], layers[k - 1], layers[k]
            over = cur.difference(below.buffer(0.02))
            for hx, hz in holes:
                if abs(z - hz) < CSK_D / 2 + 2 * LAYER_H:
                    over = over.difference(sbox(hx - CSK_D / 2 - 1, -1, hx + CSK_D / 2 + 1, T * IN + 1))
            pieces = [g for g in getattr(over, "geoms", [over]) if g.geom_type == "Polygon" and not g.is_empty]
            if pieces:
                worst = max(worst, max(below.distance(Point(p)) for g in pieces for p in g.exterior.coords))
        return math.degrees(math.atan2(worst, LAYER_H))

    def rod_probe(self, d, length=6.0):
        """A rod seated at the lowest point of the slot, running along z through the hook and past the board."""
        sx, sy = self.seat_point(d)
        return Pos(sx * IN, sy * IN, 0) * Cylinder(d / 2 * IN, length * IN)

    # ---- 2D geometry for the checks and the drawings --------------------------------------
    def solid_2d(self):
        """The hook outline as a shapely polygon: the very points the CAD extrudes."""
        return SPoly(self.final_outline()).buffer(0)

    def obstacles(self, neighbour=None):
        """What a rod must not pass through: this hook, the hooks butted above and below it (the top
        hook has the joist above instead, the same ceiling), and the board. The neighbours are this
        hook's own kind unless another is named: the hooks share the height, the tab and the screws,
        so one board can carry a mix."""
        s = self.solid_2d()
        n = (neighbour or self).solid_2d()
        board = sbox(0, -H - 4, BOARD_W + 4, 2 * H + 4)
        return unary_union([s, stranslate(n, 0, H), stranslate(n, 0, -H), board])

    def free_space(self, r, neighbour=None):
        big = sbox(-self.CANT - 4, -4, TAB + 4, H + 4)
        return big.difference(self.obstacles(neighbour)).buffer(-r)

    def seat_point(self, d):
        """Lowest position of the centre of a rod of diameter d anywhere inside the slot."""
        r = d / 2
        free = self.free_space(r)
        slot = sbox(-self.CANT, 0, self.X_BACK, self.Y_LIP)
        inside = free.intersection(slot)
        assert not inside.is_empty, f"{self.name}: a {d} in rod does not fit the slot"
        lowest = None
        for g in getattr(inside, "geoms", [inside]):
            for x, y in g.exterior.coords:
                if lowest is None or y < lowest[1]:
                    lowest = (x, y)
        return lowest

    def escape_lift(self, d, neighbour=None):
        """Smallest rise of the rod centre that lets a rod of diameter d reach the outside.
        The centre of a disc of radius r can be anywhere the free space survives an erosion by r.
        Binary-search the ceiling on the centre's height."""
        r = d / 2
        free = self.free_space(r, neighbour)
        sx, sy = self.seat_point(d)
        seat = Point(sx, sy + 0.002)
        outside = Point(-self.CANT - 2.5, sy)

        def connected(limit):
            region = free.intersection(sbox(-self.CANT - 4, -4, TAB + 4, limit))
            for g in getattr(region, "geoms", [region]):
                if g.contains(seat) and g.contains(outside):
                    return True
            return False

        assert connected(H + 4), f"{self.name}: a {d} in rod cannot get out of the slot past the hook above"
        lo, hi = 0.0, 4.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if connected(seat.y + mid):
                hi = mid
            else:
                lo = mid
        return hi

    # ---- checks and export ---------------------------------------------------------------
    def checks(self, hook):
        report = {"variant": self.name, "label": self.label, "holds": self.holds}
        assert len(hook.solids()) == 1, f"{self.name}: hook is not one solid"
        bb = hook.bounding_box()
        size = (bb.size.X / IN, bb.size.Y / IN, bb.size.Z / IN)
        assert abs(size[0] - self.W) < 0.01 and abs(size[1] - H) < 0.01 and abs(size[2] - T) < 0.01, size
        report["size_in"] = [round(s, 3) for s in size]
        report["volume_cm3"] = round(hook.volume / 1000, 1)
        report["slot_w_in"] = self.SLOT_W
        report["jaw_height_in"] = {"at the lip": round(self.Y_LIP, 4), "at the tip": round(self.Y_TIP, 4)}
        report["jaw_reach_in"] = self.CANT
        report["slot_lean_deg"] = self.SLOT_LEAN
        report["floor_in"] = self.BELOW
        report["hood_in"] = round(self.HOOD, 3)
        lip_min = self.CANT + (self.X_C - self.R_SLOT)
        report["lip_min_in"] = round(lip_min, 3)
        assert lip_min >= LIP_MIN - 1e-6
        # the rod touches nothing: not the hook when seated (beyond a hair of contact), never the board
        board = board_stub()
        report["seat_in"] = {}
        for d in self.ROD_DIAS:
            rod = self.rod_probe(d)
            overlap = (rod & hook).volume
            assert overlap < 2.0, f"{self.name}: {d} in rod intersects the hook when seated ({overlap:.2f} mm3)"
            assert (rod & board).volume < 1e-3, f"{self.name}: {d} in rod touches the board"
            report["seat_in"][str(d)] = [round(v, 3) for v in self.seat_point(d)]
        assert (hook & board).volume < 1e-3, f"{self.name}: hook intersects the board"
        # slot takes the biggest rod with room
        assert self.SLOT_W >= max(self.ROD_DIAS) + self.SLOT_MARGIN - 1e-9, f"{self.name}: slot too narrow"
        # the way in and out: between the lip tip and the hook butted above
        exit_gap = H - self.Y_TIP
        report["exit_gap_in"] = round(exit_gap, 3)
        report["exit_gap_asked_in"] = self.MIN_EXIT_GAP
        assert exit_gap >= max(self.ROD_DIAS) + EXIT_MARGIN - 1e-9, f"{self.name}: only {exit_gap:.3f} in between the lip tip and the hook above"
        # Brian, 2026-11-09: "the holders will stack on top of each other, make sure there is 2 in of room to get the butt in"
        # (each hook carries its own floor: 2 in is the 2 in hook's; the 1-1/2 in hook's is its opening)
        assert exit_gap >= self.MIN_EXIT_GAP - 1e-9, f"{self.name}: {exit_gap:.3f} in between the lip tip and the hook above, asked {self.MIN_EXIT_GAP}"
        # pose-space hold: every rod needs at least MIN_LIFT of rise before it can leave, and every rod can leave
        report["escape_lift_in"] = {}
        for d in self.ROD_DIAS:
            lift = self.escape_lift(d)
            report["escape_lift_in"][str(d)] = round(lift, 3)
            assert lift >= self.MIN_LIFT, f"{self.name}: {d} in rod escapes with only {lift:.2f} in of lift"
        # the same with each of the other hooks butted above and below, since one board can carry a mix
        report["escape_lift_mixed_in"] = {}
        for other in VARIANTS.values():
            if other is not self:
                lift = min(self.escape_lift(d, other) for d in self.ROD_DIAS)
                report["escape_lift_mixed_in"][other.label] = round(lift, 3)
                assert lift >= self.MIN_LIFT, f"{self.name}: only {lift:.2f} in of lift with {other.label} hooks above and below"
        # wall minimums for the 0.6 nozzle (2 perimeters = 1.24 mm)
        assert WEB * IN >= 1.24 and LIP_MIN * IN >= 1.24 and self.BELOW * IN >= 1.24
        report["lift_to_leave_in"] = round(self.Y_TIP - self.Y_REST, 3)
        report["screws_mm"] = {"hole": HOLE_D, "countersink": CSK_D, "depth": CSK_DEPTH,
                               "positions_in": [[SCREW_X, y] for y in SCREW_Y]}
        return report

    def export(self):
        """Build, check and export this hook: the model-frame STL, the standing print STL and the report."""
        hook = self.build()
        report = self.checks(hook)
        model_stl = PROJECT / f"{self.stem}-model.stl"
        export_stl(hook, str(model_stl))
        clean_stl(model_stl)
        stl = PROJECT / f"{self.stem}.stl"
        up = self.standing(hook)
        bb = up.bounding_box()
        assert abs(bb.min.Z) < 1e-6 and abs(bb.min.X) < 1e-6 and abs(bb.min.Y) < 1e-6, f"{self.name}: standing hook is not on the bed at the origin"
        assert abs(bb.size.Z - H * IN) < 0.01 and abs(bb.size.Y - T * IN) < 0.01, f"{self.name}: standing hook has the wrong footprint"
        export_stl(up, str(stl))
        m = clean_stl(stl)
        assert m.is_watertight, f"{self.name}: exported STL is not watertight"
        report["stl"] = str(stl)
        report["model_stl"] = str(model_stl)
        report["print_orientation"] = "standing on the 4 in bottom edge, face vertical, holes horizontal"
        report["footprint_mm"] = [round(bb.size.X, 1), round(bb.size.Y, 1)]
        report["height_mm"] = round(bb.size.Z, 1)
        report["stl_volume_cm3"] = round(m.volume / 1000, 1)
        overhang = self.overhang_report(stl)
        report["max_overhang_deg_from_vertical"] = round(overhang, 1)
        report["overhang_check"] = f"layer by layer at {LAYER_H} mm, holes and the first layer left out"
        report["edge_round_in"] = EDGE_R
        report["flat_faces"] = "the back face (against the board) and the bottom strip (the bed of the standing print)"
        assert overhang <= MAX_OVERHANG, f"{self.name}: standing print overhangs {overhang:.1f} degrees from vertical"
        (PROJECT / f"{self.stem}-report.json").write_text(json.dumps(report, indent=1))
        return hook, report


TIP = Hook("tip", "rod-hook", "the blank, 1/4 to 5/8 in",
           slot_w=0.875, slot_lean=35.0, below=0.625, y_lip=1.875, lip_slope=0.375,
           rod_dias=(0.25, 0.375, 0.625), slot_margin=0.25, min_lift=1.4, min_exit_gap=1.0)
BUTT = Hook("butt", "rod-hook-butt", "the grip, about 1-7/8 in (2 in opening)",
            slot_w=2.0, slot_lean=10.0, below=0.3125, y_lip=1.625, lip_slope=0.125,
            rod_dias=(1.5, 1.75, 1.875), slot_margin=0.125, min_lift=1.25, min_exit_gap=2.0, label="2 in")
# the 1-1/2 in hook (Brian 2026-11-11): the tip hook's lean and lip heights around a 1-1/2 in bottom on the 2 in hook's
# floor. The exit gap floor is the opening itself (Brian gave no number for this one); 1-3/4 is what it gets.
SLIM = Hook("slim", "rod-hook-slim", "a slimmer grip, about 1 to 1-3/8 in (1-1/2 in opening)",
            slot_w=1.5, slot_lean=35.0, below=0.3125, y_lip=1.875, lip_slope=0.375,
            rod_dias=(1.0, 1.25, 1.375), slot_margin=0.125, min_lift=1.5, min_exit_gap=1.5, label="1.5 in")   # his word for it; no slash, it goes into the plate name
VARIANTS = {"tip": TIP, "butt": BUTT, "slim": SLIM}
SHOW_ROD = {"tip": 0.375, "butt": 1.875, "slim": 1.25}   # what each hook is drawn holding
SHOW_NAME = {"tip": "rod 3/8", "butt": "grip 1-7/8", "slim": "grip 1-1/4"}


def arc_point(c, r, a):
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def rounded_path(items, n=24):
    """Items are ("corner", point, radius) and ("arc", centre, radius, start angle, sweep, points). Every
    corner with a radius becomes its fillet arc (tangent points and centre worked out here, convex or concave
    alike), so the CAD builds the outline from lines and true arcs and the 2D checks sample those same arcs:
    one geometry. Returns the closed path as ("pt", point) and ("arc", ...) items in order."""
    base = [("pt", it[1]) if it[0] == "corner" else it for it in items]
    first = lambda it: it[1] if it[0] == "pt" else arc_point(it[1], it[2], it[3])
    last = lambda it: it[1] if it[0] == "pt" else arc_point(it[1], it[2], it[3] + it[4])
    out = []
    count = len(items)
    for i, it in enumerate(items):
        r = it[2] if it[0] == "corner" else 0.0
        if r <= 0:
            out.append(base[i])
            continue
        p = it[1]
        p0, p1 = last(base[i - 1]), first(base[(i + 1) % count])
        v0 = (p0[0] - p[0], p0[1] - p[1])
        v1 = (p1[0] - p[0], p1[1] - p[1])
        l0, l1 = math.hypot(*v0), math.hypot(*v1)
        v0 = (v0[0] / l0, v0[1] / l0)
        v1 = (v1[0] / l1, v1[1] / l1)
        alpha = math.acos(max(-1.0, min(1.0, v0[0] * v1[0] + v0[1] * v1[1])))
        t = r / math.tan(alpha / 2)
        assert t < l0 and t < l1, f"fillet {r} too big at vertex {i}"
        a = (p[0] + v0[0] * t, p[1] + v0[1] * t)
        b = (p[0] + v1[0] * t, p[1] + v1[1] * t)
        bis = (v0[0] + v1[0], v0[1] + v1[1])
        lb = math.hypot(*bis)
        c = (p[0] + bis[0] / lb * r / math.sin(alpha / 2), p[1] + bis[1] / lb * r / math.sin(alpha / 2))
        ang_a = math.atan2(a[1] - c[1], a[0] - c[0])
        ang_b = math.atan2(b[1] - c[1], b[0] - c[0])
        delta = (ang_b - ang_a + math.pi) % (2 * math.pi) - math.pi
        out.append(("arc", c, r, ang_a, delta, n))
    return out


def path_points(path):
    """The path as a polygon: each arc sampled at its number of points, the tangent points exact."""
    pts = []
    for it in path:
        if it[0] == "pt":
            pts.append(it[1])
        else:
            c, r, a0, delta, n = it[1:]
            pts += [arc_point(c, r, a0 + delta * k / n) for k in range(n + 1)]
    return pts


def path_face(path):
    """The path as a build123d face in mm: a line between neighbouring items, a true arc for each arc."""
    edges = []
    for i, it in enumerate(path):
        nxt = path[(i + 1) % len(path)]
        if it[0] == "arc":
            c, r, a0, delta, _ = it[1:]
            a, mid, b = (arc_point(c, r, a0 + delta * f) for f in (0.0, 0.5, 1.0))
            edges.append(ThreePointArc(*mm([a, mid, b])))
            end = b
        else:
            end = it[1]
        start = nxt[1] if nxt[0] == "pt" else arc_point(nxt[1], nxt[2], nxt[3])
        if math.dist(end, start) > 1e-9:
            edges.append(Line(*mm([end, start])))
    return make_face(Wire(edges))


def clean_stl(path):
    """Re-save an exported STL without degenerate triangles: the spherical corner blends of the roundover
    tessellate with a zero-area triangle at each pole, which reads as an open edge. Returns the clean mesh."""
    import trimesh
    m = trimesh.load(str(path))
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    m.export(str(path))
    return m


def mm(pts):
    return [(x * IN, y * IN) for x, y in pts]


def board_stub(length=6.0):
    """A piece of the 1x4 behind the hook: x from 0 to BOARD_W, z from -BOARD_T to 0."""
    return Pos(BOARD_W / 2 * IN, H / 2 * IN, -BOARD_T / 2 * IN) * Box(BOARD_W * IN, length * IN, BOARD_T * IN)


if __name__ == "__main__":
    hooks, reports = {}, {}
    for name, v in VARIANTS.items():
        hooks[name], reports[name] = v.export()
        r = reports[name]
        print(f"{name}: {r['size_in']} in, {r['volume_cm3']} cm3, slot {v.SLOT_W} in leaning {v.SLOT_LEAN} deg, "
              f"lift {min(r['escape_lift_in'].values())} in, exit gap {r['exit_gap_in']} in, lip {r['lip_min_in']} in, "
              f"overhang {r['max_overhang_deg_from_vertical']} deg, footprint {r['footprint_mm']} mm")
    if os.environ.get("SHOW"):
        from ocp_vscode import Camera, show
        parts, names, colors = [], [], []
        for i, (name, v) in enumerate(VARIANTS.items()):   # each hook on its own board stub, 8 in apart
            off = Pos(8.0 * i * IN, 0, 0)
            parts += [off * hooks[name], off * board_stub(), off * v.rod_probe(SHOW_ROD[name])]
            names += [f"{v.label} hook", f"1x4 ({v.label})", SHOW_NAME[name]]
            colors += ["#2f6fe4", "#c9a46e", "#333333" if name == "tip" else "#8b5a2b"]
        show(*parts, names=names, colors=colors,
             reset_camera=Camera.RESET if os.environ["SHOW"] == "reset" else Camera.KEEP)
