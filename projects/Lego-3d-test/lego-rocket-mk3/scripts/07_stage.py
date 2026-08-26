# Lego Rocket Mk3 - Part 7: Stage (white, qty 3) - R2 round brick h9.6
# D15.8 cylinder, cavity D13.0 x 8.4, center tube D6.5, roof 1.2,
# 4 top studs at (+-4,+-4).
#
# DEVIATION from DESIGN.md (geometric necessity): studs at (+-4,+-4) reach
# r8.06 from the axis, but the D13.0 cavity wall sits at r6.5 and the brick
# outer face at r7.9 - the wall annulus would land ON TOP of the stud
# crescents and the joint could never seat. Real Lego round bricks relieve
# the bottom rim; here: 4 notch cylinders r2.45 (stud 2.4 + 0.05 clearance)
# x 2.0 deep cut at (+-4,+-4) BEFORE the center tube is fused, so the tube
# keeps its full D6.5 and still pinches the stud inner edges (r3.25 vs 3.257).
import FreeCAD, Part
from FreeCAD import Vector

DOC = "lego_rocket_mk3"
doc = FreeCAD.listDocuments().get(DOC) or FreeCAD.newDocument(DOC)
FreeCAD.setActiveDocument(DOC)

STUD_R, STUD_H = 2.4, 1.7

def r2_round_brick(height):
    """D15.8 round brick: cavity D13.0 x 8.4, stud notches, center tube D6.5,
    4 studs at (+-4,+-4) on top."""
    body = Part.makeCylinder(7.9, height)
    body = body.cut(Part.makeCylinder(6.5, 8.4))
    for x in (-4, 4):
        for y in (-4, 4):
            body = body.cut(Part.makeCylinder(2.45, 2.0, Vector(x, y, 0)))
    body = body.fuse(Part.makeCylinder(3.25, 8.4))
    studs = [Part.makeCylinder(STUD_R, STUD_H, Vector(x, y, height))
             for x in (-4, 4) for y in (-4, 4)]
    return body.fuse(studs)

shape = r2_round_brick(9.6).removeSplitter()

obj = doc.addObject("Part::Feature", "Stage")
obj.Shape = shape
obj.Placement = FreeCAD.Placement(Vector(45, 80, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0xF2 / 255.0, 0xF2 / 255.0, 0xF2 / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("Stage valid=%s solids=%d vol=%.0f bb=%.1fx%.1fx%.1f" % (
    s.isValid(), len(s.Solids), s.Volume, bb.XLength, bb.YLength, bb.ZLength))
