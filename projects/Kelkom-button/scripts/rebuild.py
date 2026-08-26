import FreeCAD as App
import Part
import math

for d in list(App.listDocuments()):
    App.closeDocument(d)
doc = App.newDocument("kelkom_button")

# --- User-measured dimensions ---
L1, L2 = 13.6, 12.54          # layer 1 / layer 2 squares
T1, T2 = 2.0, 4.0             # layer thicknesses
LEG_L, LEG_W, LEG_T = 14.0, 6.0, 1.3
Z_L2 = LEG_L                  # 14: layer 2 bottom
Z_L1 = LEG_L + T2             # 18
Z_TOP = LEG_L + T2 + T1       # 20

# ---------- Cap stack ----------
solid = Part.makeBox(L1, L1, T1, App.Vector(-L1/2, -L1/2, Z_L1)).fuse(
        Part.makeBox(L2, L2, T2, App.Vector(-L2/2, -L2/2, Z_L2))).removeSplitter()

# ---------- Top recess (45 deg, print-friendly) ----------
RIM, DEPTH = 1.1, 1.2
def sq_wire(size, z):
    h = size / 2.0
    pts = [App.Vector(-h, -h, z), App.Vector(h, -h, z),
           App.Vector(h, h, z), App.Vector(-h, h, z), App.Vector(-h, -h, z)]
    return Part.makePolygon(pts)
top_sq = L1 - 2 * RIM
pocket = Part.makeLoft([sq_wire(top_sq + 0.2, Z_TOP + 0.1),
                        sq_wire(top_sq - 2 * DEPTH, Z_TOP - DEPTH)], True)
solid = solid.cut(pocket).removeSplitter()

# Chamfer 0.5 on outer top edges
edges = [e for e in solid.Edges
         if abs(e.CenterOfMass.z - Z_TOP) < 1e-6
         and max(abs(e.CenterOfMass.x), abs(e.CenterOfMass.y)) > 6.7]
assert len(edges) == 4, len(edges)
solid = solid.makeChamfer(0.5, edges)

# ---------- Center through-hole ----------
H, R = 6.5, 0.8
hh = H / 2.0
z0, hz = 10.0, 15.0
hole = Part.makeBox(H, H - 2*R, hz, App.Vector(-hh, -(hh - R), z0))
hole = hole.fuse(Part.makeBox(H - 2*R, H, hz, App.Vector(-(hh - R), -hh, z0)))
for sx in (1, -1):
    for sy in (1, -1):
        hole = hole.fuse(Part.makeCylinder(R, hz, App.Vector(sx*(hh-R), sy*(hh-R), z0)))
solid = solid.cut(hole).removeSplitter()

# ---------- Corner snap legs (arc cross-section) ----------
SQ2 = math.sqrt(2.0)
u = App.Vector(1, 1, 0).normalize()      # diagonal toward +x,+y corner
half_diag = L2 * SQ2 / 2.0               # 8.867
Ro = 6.0                                 # outer face radius ("slight" curve)
Ri = Ro - LEG_T
th = math.asin((LEG_W / 2.0) / Ro)       # 30 deg half-angle -> 6mm chord
a_end = half_diag - LEG_W / 2.0          # 5.867: strip ends land on the edges
O_a = a_end - Ro * math.cos(th)          # arc center along diagonal
O = App.Vector(O_a / SQ2, O_a / SQ2, 0)
BARB = 1.0

# Annular shell intersected with a +-30deg sector around the diagonal
ring = Part.makeCylinder(Ro, LEG_L, O, App.Vector(0, 0, 1)).cut(
       Part.makeCylinder(Ri, LEG_L + 1.0, O - App.Vector(0, 0, 0.5), App.Vector(0, 0, 1)))
Rbig = 20.0
def rot_u(ang):
    return App.Vector(math.cos(math.pi/4 + ang), math.sin(math.pi/4 + ang), 0)
tri = Part.Face(Part.makePolygon([O, O + rot_u(th)*Rbig, O + rot_u(-th)*Rbig, O]))
sector = tri.extrude(App.Vector(0, 0, LEG_L + 1.0))
sector.translate(App.Vector(0, 0, -0.5))
leg = ring.common(sector)

def bottom_arc_edge(shape, radius):
    out = []
    for e in shape.Edges:
        if e.BoundBox.ZLength < 1e-6 and e.CenterOfMass.z < 1e-6:
            if all(abs(math.hypot(v.X - O.x, v.Y - O.y) - radius) < 0.05
                   for v in e.Vertexes):
                out.append(e)
    return out

# Tip chamfers: 0.8 lead-in on the outer arc, 0.4 on the inner arc
eo = bottom_arc_edge(leg, Ro)
assert len(eo) == 1, len(eo)
leg = leg.makeChamfer(0.8, eo)
ei = bottom_arc_edge(leg, Ri)
assert len(ei) == 1, len(ei)
leg = leg.makeChamfer(0.4, ei)

# Barb: triangular ridge revolved along the outer face near the tip.
# Flush at z=1.5, BARB proud at z=4.0, flat catch face on top.
prof = Part.Face(Part.makePolygon([
    O + u * (Ro - 0.2) + App.Vector(0, 0, 1.5),
    O + u * (Ro + BARB) + App.Vector(0, 0, 4.0),
    O + u * (Ro - 0.2) + App.Vector(0, 0, 4.0),
    O + u * (Ro - 0.2) + App.Vector(0, 0, 1.5)]))
barb = prof.revolve(O, App.Vector(0, 0, 1), math.degrees(2 * th))
barb.rotate(O, App.Vector(0, 0, 1), -math.degrees(th))
leg = leg.fuse(barb)

# Second leg at the opposite corner (180 deg about z)
leg2 = leg.copy()
leg2.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 180)
solid = solid.fuse(leg).fuse(leg2).removeSplitter()

obj = doc.addObject("Part::Feature", "Button")
obj.Shape = solid
doc.recompute()
import FreeCADGui as Gui
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")
print("OK rebuild; valid:", solid.isValid(), "solids:", len(solid.Solids),
      "bbox:", solid.BoundBox)
