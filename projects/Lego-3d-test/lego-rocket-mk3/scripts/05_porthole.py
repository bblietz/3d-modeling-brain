# Lego Rocket Mk3 - Part 5: Porthole (white) - R4 + two D8 window cuts
# Windows: D8 horizontal cylinders along Y at (x=-4, z=4.8), wall-only cuts
# spanning y 11.5..18 and y -18..-11.5 (tubes only reach |y| 11.25).
import FreeCAD, Part
from FreeCAD import Vector

DOC = "lego_rocket_mk3"
doc = FreeCAD.listDocuments().get(DOC) or FreeCAD.newDocument(DOC)
FreeCAD.setActiveDocument(DOC)

STUD_R, STUD_H = 2.4, 1.7
R4_STUDS = [(12, 4), (12, -4), (-12, 4), (-12, -4),
            (4, 12), (-4, 12), (4, -12), (-4, -12),
            (4, 4), (4, -4), (-4, 4), (-4, -4)]

def r4_round_brick():
    body = Part.makeCylinder(17.0, 9.6)
    body = body.cut(Part.makeCylinder(15.1, 8.4))
    tubes = [Part.makeCylinder(3.25, 8.4, Vector(x, y, 0))
             for x in (-8, 0, 8) for y in (-8, 0, 8)]
    body = body.fuse(tubes)
    studs = [Part.makeCylinder(STUD_R, STUD_H, Vector(x, y, 9.6))
             for (x, y) in R4_STUDS]
    return body.fuse(studs)

shape = r4_round_brick()
win_plus = Part.makeCylinder(4.0, 6.5, Vector(-4, 11.5, 4.8), Vector(0, 1, 0))
win_minus = Part.makeCylinder(4.0, 6.5, Vector(-4, -18.0, 4.8), Vector(0, 1, 0))
shape = shape.cut(win_plus).cut(win_minus).removeSplitter()

obj = doc.addObject("Part::Feature", "Porthole")
obj.Shape = shape
obj.Placement = FreeCAD.Placement(Vector(185, 0, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0xF2 / 255.0, 0xF2 / 255.0, 0xF2 / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("Porthole valid=%s solids=%d vol=%.0f bb=%.1fx%.1fx%.1f" % (
    s.isValid(), len(s.Solids), s.Volume, bb.XLength, bb.YLength, bb.ZLength))
