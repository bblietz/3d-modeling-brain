# Lego Rocket Mk3 - Part 3: Tail (red) - R4 round brick + 4 swept-back fins
# R4: D34.0 cylinder h9.6, underside cavity D30.2 x 8.4, 9 tubes D6.5 on the
# (-8,0,+8) grid, roof 1.2, 12 top studs at (+-12,+-4),(+-4,+-12),(+-4,+-4).
# Fins: 1.6 thick along +-X/+-Y, base flat z0 to r26, swept-back leading edge,
# above z9.6 inner edge held at r17.15 (0.15 clearance to the D34 brick above).
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
    """D34 round brick, h 9.6: cavity D30.2 x 8.4, 9 tubes D6.5, 12 studs."""
    body = Part.makeCylinder(17.0, 9.6)
    body = body.cut(Part.makeCylinder(15.1, 8.4))
    tubes = [Part.makeCylinder(3.25, 8.4, Vector(x, y, 0))
             for x in (-8, 0, 8) for y in (-8, 0, 8)]
    body = body.fuse(tubes)
    studs = [Part.makeCylinder(STUD_R, STUD_H, Vector(x, y, 9.6))
             for (x, y) in R4_STUDS]
    return body.fuse(studs)

def fin():
    """Swept-back triangular fin in the XZ plane, 1.6 thick, along +X."""
    pts = [(15.5, 0.0), (26.0, 0.0), (17.15, 19.2), (17.15, 9.6), (15.5, 9.6)]
    vecs = [Vector(x, -0.8, z) for (x, z) in pts]
    poly = Part.makePolygon(vecs + [vecs[0]])
    return Part.Face(poly).extrude(Vector(0, 1.6, 0))

tail = r4_round_brick()
for ang in (0, 90, 180, 270):
    f = fin()
    f.rotate(Vector(0, 0, 0), Vector(0, 0, 1), ang)
    tail = tail.fuse(f)
tail = tail.removeSplitter()

obj = doc.addObject("Part::Feature", "Tail")
obj.Shape = tail
obj.Placement = FreeCAD.Placement(Vector(75, 0, 0), FreeCAD.Rotation())
obj.ViewObject.ShapeColor = (0xD3 / 255.0, 0x2F / 255.0, 0x2F / 255.0)
doc.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")
s = obj.Shape
bb = s.BoundBox
print("Tail valid=%s solids=%d vol=%.0f bb=%.1fx%.1fx%.1f" % (
    s.isValid(), len(s.Solids), s.Volume, bb.XLength, bb.YLength, bb.ZLength))
