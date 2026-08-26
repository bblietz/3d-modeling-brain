import FreeCAD as App
import Part

doc = App.getDocument("kelkom_button")
obj = doc.Button
solid = obj.Shape.copy()

L2 = 12.54
LEG_L = 14.0     # user-measured
LEG_W = 6.0      # user-measured
LEG_T = 2.6      # estimated from photos
BARB = 1.0       # barb protrusion, estimated
xo = L2 / 2.0    # leg outer face, flush with layer 2
xi = xo - LEG_T  # leg inner face

# Build one leg (+x side), tips at z=0
leg = Part.makeBox(LEG_T, LEG_W, LEG_L, App.Vector(xi, -LEG_W / 2, 0))

# Insertion lead chamfer: big 45 on the outer bottom edge
e_out = [e for e in leg.Edges
         if e.CenterOfMass.z < 1e-6 and abs(e.CenterOfMass.x - xo) < 1e-6]
assert len(e_out) == 1, len(e_out)
leg = leg.makeChamfer(1.4, e_out)

# 0.7 chamfer on inner + side bottom edges only (NOT the new chamfer-face edge)
e_rest = [e for e in leg.Edges
          if e.BoundBox.ZLength < 1e-6 and e.CenterOfMass.z < 1e-6
          and (abs(e.CenterOfMass.x - xi) < 1e-6
               or abs(abs(e.CenterOfMass.y) - LEG_W / 2) < 1e-6)]
assert len(e_rest) == 3, len(e_rest)
leg = leg.makeChamfer(0.7, e_rest)

# Barb: triangular ridge on the outer face near the tip.
# Ramp rises from flush at z=1.5 to BARB proud at z=4.0; flat catch face on top.
tri = Part.Face(Part.makePolygon([
    App.Vector(xo - 0.2, -LEG_W / 2, 1.5),
    App.Vector(xo + BARB, -LEG_W / 2, 4.0),
    App.Vector(xo - 0.2, -LEG_W / 2, 4.0),
    App.Vector(xo - 0.2, -LEG_W / 2, 1.5)]))
barb = tri.extrude(App.Vector(0, LEG_W, 0))
leg = leg.fuse(barb)

legs = leg.fuse(leg.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0)))
solid = solid.fuse(legs).removeSplitter()

obj.Shape = solid
doc.recompute()
import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
print("OK legs; valid:", solid.isValid(), "bbox:", solid.BoundBox)
