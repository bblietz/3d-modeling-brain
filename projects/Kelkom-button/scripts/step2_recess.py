import FreeCAD as App
import Part

doc = App.getDocument("kelkom_button")
obj = doc.Button
solid = obj.Shape.copy()

Z_TOP = 20.0
RIM = 1.1          # flat rim width around the recess
DEPTH = 1.2        # recess depth, 45 deg slope (print-friendly face-down)

def sq_wire(size, z):
    h = size / 2.0
    pts = [App.Vector(-h, -h, z), App.Vector(h, -h, z),
           App.Vector(h, h, z), App.Vector(-h, h, z), App.Vector(-h, -h, z)]
    return Part.makePolygon(pts)

# Truncated-pyramid pocket, 45 deg walls, extended 0.1 above the top face
top_sq = 13.6 - 2 * RIM          # 11.4 at the top face
w_hi = sq_wire(top_sq + 0.2, Z_TOP + 0.1)
w_lo = sq_wire(top_sq - 2 * DEPTH, Z_TOP - DEPTH)
pocket = Part.makeLoft([w_hi, w_lo], True)
solid = solid.cut(pocket).removeSplitter()

# Chamfer 0.5 on the outer top edges (rim outline at z=20, |x| or |y| = 6.8)
edges = []
for e in solid.Edges:
    c = e.CenterOfMass
    if abs(c.z - Z_TOP) < 1e-6 and max(abs(c.x), abs(c.y)) > 6.7:
        edges.append(e)
assert len(edges) == 4, f"expected 4 outer top edges, got {len(edges)}"
solid = solid.makeChamfer(0.5, edges)

obj.Shape = solid
doc.recompute()
import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
print("OK recess; faces:", len(solid.Faces))
