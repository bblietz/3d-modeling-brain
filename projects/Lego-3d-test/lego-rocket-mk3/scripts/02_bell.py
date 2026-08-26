# Lego Rocket Mk3 - Part 2: Bell (gray, qty 4) - engine bell
# Cone r3.6 -> r2.6 x 6.0 tall, exhaust recess D5.0 x 2.5 deep from bottom,
# grip stud D4.8 x 1.7 on top.
import FreeCAD, Part
from FreeCAD import Vector

DOC = "lego_rocket_mk3"
doc = FreeCAD.listDocuments().get(DOC) or FreeCAD.newDocument(DOC)
FreeCAD.setActiveDocument(DOC)

bell = Part.makeCone(3.6, 2.6, 6.0)
recess = Part.makeCylinder(2.5, 2.5, Vector(0, 0, 0))
bell = bell.cut(recess)
grip = Part.makeCylinder(2.4, 1.7, Vector(0, 0, 6.0))
bell = bell.fuse(grip).removeSplitter()

obj = doc.addObject("Part::Feature", "Bell")
obj.Shape = bell
obj.Placement = FreeCAD.Placement(Vector(120, 80, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0x55 / 255.0, 0x55 / 255.0, 0x55 / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("Bell valid=%s solids=%d vol=%.0f bb=%.1fx%.1fx%.1f" % (
    s.isValid(), len(s.Solids), s.Volume, bb.XLength, bb.YLength, bb.ZLength))
