import FreeCAD as App
import Part

doc = App.getDocument("kelkom_button")
obj = doc.Button
solid = obj.Shape.copy()

# Square through-hole with rounded corners (estimated from photos)
H = 6.5      # hole edge
R = 0.8      # corner radius
hh = H / 2.0
z0, hz = 10.0, 15.0   # spans 10..25, well past both faces (13..20 material)

hole = Part.makeBox(H, H - 2 * R, hz, App.Vector(-hh, -(hh - R), z0))
hole = hole.fuse(Part.makeBox(H - 2 * R, H, hz, App.Vector(-(hh - R), -hh, z0)))
for sx in (1, -1):
    for sy in (1, -1):
        hole = hole.fuse(Part.makeCylinder(R, hz, App.Vector(sx * (hh - R), sy * (hh - R), z0)))

solid = solid.cut(hole).removeSplitter()
obj.Shape = solid
doc.recompute()
import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
print("OK hole; solids:", len(solid.Solids), "valid:", solid.isValid())
