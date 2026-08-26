# Lego Rocket Mk3 - Part 9: BoosterBody (white, qty 4) - R2 round brick h19.2
# Same round 2x2 module as the Stage but double height: cavity D13.0 x 8.4 at
# the bottom (with stud-relief notches), center tube D6.5, solid above the
# cavity roof, 4 studs at (+-4,+-4) on top.
import FreeCAD, Part
from FreeCAD import Vector

DOC = "lego_rocket_mk3"
doc = FreeCAD.listDocuments().get(DOC) or FreeCAD.newDocument(DOC)
FreeCAD.setActiveDocument(DOC)

STUD_R, STUD_H = 2.4, 1.7

def r2_round_brick(height):
    body = Part.makeCylinder(7.9, height)
    body = body.cut(Part.makeCylinder(6.5, 8.4))
    for x in (-4, 4):
        for y in (-4, 4):
            body = body.cut(Part.makeCylinder(2.45, 2.0, Vector(x, y, 0)))
    body = body.fuse(Part.makeCylinder(3.25, 8.4))
    studs = [Part.makeCylinder(STUD_R, STUD_H, Vector(x, y, height))
             for x in (-4, 4) for y in (-4, 4)]
    return body.fuse(studs)

shape = r2_round_brick(19.2).removeSplitter()

obj = doc.addObject("Part::Feature", "BoosterBody")
obj.Shape = shape
obj.Placement = FreeCAD.Placement(Vector(155, 80, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0xF2 / 255.0, 0xF2 / 255.0, 0xF2 / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("BoosterBody valid=%s solids=%d vol=%.0f bb=%.1fx%.1fx%.1f" % (
    s.isValid(), len(s.Solids), s.Volume, bb.XLength, bb.YLength, bb.ZLength))
