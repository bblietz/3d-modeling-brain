# Lego Rocket Mk3 - Assembly document: 22 placed copies, named in build order.
# Placements per DESIGN.md (world z of part origin):
# Pad 0; Bells (+-4,+-4) z5.2; Tail 11.2; Body A 20.8; Porthole 30.4;
# Body B 40.0; Taper 49.6; Stages 68.8/78.4/88.0; Nose 97.6 (apex ~125.6);
# BoosterBodies (+-24,+-24) z3.2; BoosterCones (+-24,+-24) z22.4.
import FreeCAD
from FreeCAD import Vector

PARTS_DOC = "lego_rocket_mk3"
ASM_DOC = "lego_rocket_mk3_assembly"

RED = (0xD3 / 255.0, 0x2F / 255.0, 0x2F / 255.0)
WHITE = (0xF2 / 255.0, 0xF2 / 255.0, 0xF2 / 255.0)
GRAY = (0x55 / 255.0, 0x55 / 255.0, 0x55 / 255.0)

parts = FreeCAD.getDocument(PARTS_DOC)
asm = FreeCAD.listDocuments().get(ASM_DOC) or FreeCAD.newDocument(ASM_DOC)
FreeCAD.setActiveDocument(ASM_DOC)
for o in list(asm.Objects):
    asm.removeObject(o.Name)

diag = [(-4, -4), (-4, 4), (4, -4), (4, 4)]
corner = [(-24, -24), (-24, 24), (24, -24), (24, 24)]

steps = [("Step01_Pad", "Pad", (0, 0, 0), GRAY)]
steps += [("Step%02d_Bell%d" % (2 + i, 1 + i), "Bell", (x, y, 5.2), GRAY)
          for i, (x, y) in enumerate(diag)]
steps += [("Step06_Tail", "Tail", (0, 0, 11.2), RED),
          ("Step07_BodyA", "Body", (0, 0, 20.8), WHITE),
          ("Step08_Porthole", "Porthole", (0, 0, 30.4), WHITE),
          ("Step09_BodyB", "Body", (0, 0, 40.0), WHITE),
          ("Step10_Taper", "Taper", (0, 0, 49.6), RED),
          ("Step11_Stage1", "Stage", (0, 0, 68.8), WHITE),
          ("Step12_Stage2", "Stage", (0, 0, 78.4), WHITE),
          ("Step13_Stage3", "Stage", (0, 0, 88.0), WHITE),
          ("Step14_Nose", "Nose", (0, 0, 97.6), RED)]
steps += [("Step%02d_BoosterBody%d" % (15 + i, 1 + i), "BoosterBody",
           (x, y, 3.2), WHITE) for i, (x, y) in enumerate(corner)]
steps += [("Step%02d_BoosterCone%d" % (19 + i, 1 + i), "BoosterCone",
           (x, y, 22.4), RED) for i, (x, y) in enumerate(corner)]

for name, src, pos, color in steps:
    sh = parts.getObject(src).Shape.copy()
    sh.Placement = FreeCAD.Placement()  # back to origin, then place
    o = asm.addObject("Part::Feature", name)
    o.Shape = sh
    o.Placement = FreeCAD.Placement(Vector(*pos), FreeCAD.Rotation())
    o.ViewObject.ShapeColor = color
asm.recompute()

import FreeCADGui as Gui
Gui.SendMsgToActiveView("ViewFit")

bb = None
allvalid = True
for o in asm.Objects:
    allvalid = allvalid and o.Shape.isValid()
    if bb is None:
        bb = FreeCAD.BoundBox(o.Shape.BoundBox)
    else:
        bb.add(o.Shape.BoundBox)
print("Assembly objects=%d allvalid=%s" % (len(asm.Objects), allvalid))
print("bb x %.1f..%.1f  y %.1f..%.1f  z %.2f..%.2f  height=%.2f" % (
    bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, bb.ZLength))
