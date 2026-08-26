# Lego Rocket Mk3 - Part 1: Pad (gray) - 8x8 plate + raised platform + through-well
# 63.8 x 63.8 x 3.2 plate, 31.8 x 31.8 platform to z 11.2, 19 x 19 x 14 through-well.
# 48 outer plate studs (grid {+-4,+-12,+-20,+-28}, max(|x|,|y|) >= 20).
# Platform ring: 8 studs at (+-12,+-4) and (+-4,+-12) only (corner studs dropped).
import FreeCAD, Part
from FreeCAD import Vector

DOC = "lego_rocket_mk3"
doc = FreeCAD.listDocuments().get(DOC) or FreeCAD.newDocument(DOC)
FreeCAD.setActiveDocument(DOC)

STUD_R, STUD_H = 2.4, 1.7

def stud(x, y, z):
    return Part.makeCylinder(STUD_R, STUD_H, Vector(x, y, z))

plate = Part.makeBox(63.8, 63.8, 3.2, Vector(-31.9, -31.9, 0))
platform = Part.makeBox(31.8, 31.8, 11.2, Vector(-15.9, -15.9, 0))
pad = plate.fuse(platform)
well = Part.makeBox(19.0, 19.0, 14.0, Vector(-9.5, -9.5, -1.0))
pad = pad.cut(well)

coords = [-28, -20, -12, -4, 4, 12, 20, 28]
studs = [stud(x, y, 3.2) for x in coords for y in coords
         if max(abs(x), abs(y)) >= 20]
ring = [(12, 4), (12, -4), (-12, 4), (-12, -4),
        (4, 12), (-4, 12), (4, -12), (-4, -12)]
studs += [stud(x, y, 11.2) for (x, y) in ring]
pad = pad.fuse(studs).removeSplitter()

obj = doc.addObject("Part::Feature", "Pad")
obj.Shape = pad
obj.Placement = FreeCAD.Placement(Vector(0, 0, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0x55 / 255.0, 0x55 / 255.0, 0x55 / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("Pad valid=%s solids=%d studs=%d vol=%.0f bb=%.1fx%.1fx%.1f zmax=%.1f" % (
    s.isValid(), len(s.Solids), len(studs), s.Volume,
    bb.XLength, bb.YLength, bb.ZLength, bb.ZMax))
