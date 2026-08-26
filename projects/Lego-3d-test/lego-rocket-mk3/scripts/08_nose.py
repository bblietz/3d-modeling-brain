# Lego Rocket Mk3 - Part 8: Nose (red)
# Round skirt D15.8 x 3.2 with shallow grip cavity D13.0 x 2.0 (+ stud-relief
# notches, same necessity as the R2 brick), cone r7.9 -> r2.6 over 17.8,
# collar r2.6 x 2.0, mast r1.5 with sphere-r1.5 rounded tip, apex z 28.0.
# Interpretation: DESIGN.md's "mast r1.5 x 5.0 + sphere tip r1.5, apex ~28"
# is read as mast cylinder z23..26.5 + spherical cap centered z26.5, so the
# mast-plus-tip is 5.0 tall and the apex lands at exactly 28.0
# (97.6 + 28.0 = 125.6, the stated total height).
import FreeCAD, Part
from FreeCAD import Vector

DOC = "lego_rocket_mk3"
doc = FreeCAD.listDocuments().get(DOC) or FreeCAD.newDocument(DOC)
FreeCAD.setActiveDocument(DOC)

def round_skirt():
    """D15.8 x 3.2 skirt with D13.0 x 2.0 grip cavity + 4 stud notches."""
    sk = Part.makeCylinder(7.9, 3.2)
    sk = sk.cut(Part.makeCylinder(6.5, 2.0))
    for x in (-4, 4):
        for y in (-4, 4):
            sk = sk.cut(Part.makeCylinder(2.45, 2.0, Vector(x, y, 0)))
    return sk

nose = round_skirt()
nose = nose.fuse(Part.makeCone(7.9, 2.6, 17.8, Vector(0, 0, 3.2)))
nose = nose.fuse(Part.makeCylinder(2.6, 2.0, Vector(0, 0, 21.0)))
nose = nose.fuse(Part.makeCylinder(1.5, 3.5, Vector(0, 0, 23.0)))
nose = nose.fuse(Part.makeSphere(1.5, Vector(0, 0, 26.5)))
nose = nose.removeSplitter()

# restore visibility of previously isolated parts
for o in doc.Objects:
    o.ViewObject.Visibility = True

obj = doc.addObject("Part::Feature", "Nose")
obj.Shape = nose
obj.Placement = FreeCAD.Placement(Vector(85, 80, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0xD3 / 255.0, 0x2F / 255.0, 0x2F / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("Nose valid=%s solids=%d vol=%.0f bb=%.1fx%.1fx%.1f zmax=%.2f" % (
    s.isValid(), len(s.Solids), s.Volume,
    bb.XLength, bb.YLength, bb.ZLength, bb.ZMax))
