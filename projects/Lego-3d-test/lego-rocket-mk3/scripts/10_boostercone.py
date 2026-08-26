# Lego Rocket Mk3 - Part 10: BoosterCone (red, qty 4)
# Round skirt D15.8 x 3.2 with grip cavity D13.0 x 2.0 (+ stud-relief notches),
# cone r7.9 -> r2.0 with sphere-r2.0 rounded tip, apex z 13.2.
# Interpretation: DESIGN.md's "cone over 10.0 + sphere tip r2.0, apex ~13.2"
# is read as cone z3.2..11.2 + spherical cap centered z11.2, so cone-plus-tip
# spans the stated 10.0 and the apex lands at exactly 13.2.
import FreeCAD, Part
from FreeCAD import Vector

DOC = "lego_rocket_mk3"
doc = FreeCAD.listDocuments().get(DOC) or FreeCAD.newDocument(DOC)
FreeCAD.setActiveDocument(DOC)

def round_skirt():
    sk = Part.makeCylinder(7.9, 3.2)
    sk = sk.cut(Part.makeCylinder(6.5, 2.0))
    for x in (-4, 4):
        for y in (-4, 4):
            sk = sk.cut(Part.makeCylinder(2.45, 2.0, Vector(x, y, 0)))
    return sk

cone = round_skirt()
cone = cone.fuse(Part.makeCone(7.9, 2.0, 8.0, Vector(0, 0, 3.2)))
cone = cone.fuse(Part.makeSphere(2.0, Vector(0, 0, 11.2)))
cone = cone.removeSplitter()

obj = doc.addObject("Part::Feature", "BoosterCone")
obj.Shape = cone
obj.Placement = FreeCAD.Placement(Vector(195, 80, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0xD3 / 255.0, 0x2F / 255.0, 0x2F / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("BoosterCone valid=%s solids=%d vol=%.0f bb=%.1fx%.1fx%.1f zmax=%.2f" % (
    s.isValid(), len(s.Solids), s.Volume,
    bb.XLength, bb.YLength, bb.ZLength, bb.ZMax))
