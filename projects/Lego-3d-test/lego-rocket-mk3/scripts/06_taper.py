# Lego Rocket Mk3 - Part 6: Taper (red) - solid cone loft D34 -> D15.8 over 19.2
# with R4-style underside clutch and 4 top studs at (+-4,+-4).
#
# DEVIATION from DESIGN.md (geometric necessity): the specced straight cavity
# D30.2 x 8.4 deep cannot coexist with the cone wall - the outer surface
# r(z) = 17.0 - 0.474*z falls below r15.1 at z ~= 4.0, so a full-depth D30.2
# cut severs the bottom skirt from the body (two disconnected solids).
# Fix: keep the full D30.2 clutch band where the studs below actually reach
# (z 0..1.9, stud height 1.7 + 0.2), then chamfer the cavity inward at 45 deg
# to r11.0 at z6.0, and continue r11.0 up to the specced roof depth 8.4.
# The 9 D6.5 tubes and the stud pinch geometry are unchanged.
import FreeCAD, Part
from FreeCAD import Vector

DOC = "lego_rocket_mk3"
doc = FreeCAD.listDocuments().get(DOC) or FreeCAD.newDocument(DOC)
FreeCAD.setActiveDocument(DOC)

STUD_R, STUD_H = 2.4, 1.7

taper = Part.makeCone(17.0, 7.9, 19.2)

cavity = Part.makeCylinder(15.1, 1.9)
cavity = cavity.fuse(Part.makeCone(15.1, 11.0, 4.1, Vector(0, 0, 1.9)))
cavity = cavity.fuse(Part.makeCylinder(11.0, 2.4, Vector(0, 0, 6.0)))
taper = taper.cut(cavity)

tubes = [Part.makeCylinder(3.25, 8.4, Vector(x, y, 0))
         for x in (-8, 0, 8) for y in (-8, 0, 8)]
taper = taper.fuse(tubes)

studs = [Part.makeCylinder(STUD_R, STUD_H, Vector(x, y, 19.2))
         for x in (-4, 4) for y in (-4, 4)]
taper = taper.fuse(studs).removeSplitter()

obj = doc.addObject("Part::Feature", "Taper")
obj.Shape = taper
obj.Placement = FreeCAD.Placement(Vector(0, 80, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0xD3 / 255.0, 0x2F / 255.0, 0x2F / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("Taper valid=%s solids=%d vol=%.0f bb=%.1fx%.1fx%.1f zmax=%.1f" % (
    s.isValid(), len(s.Solids), s.Volume,
    bb.XLength, bb.YLength, bb.ZLength, bb.ZMax))
