# Lego Rocket Mk3 - Save FCStd documents + export one STL per unique part.
# STLs are exported from ORIGIN placement (kit parts print separately).
import FreeCAD, MeshPart
import os

MODEL_DIR = "/home/brian/ClaudeProjects/FreeCAD/models/lego-rocket-mk3"
PARTS_DOC = "lego_rocket_mk3"
ASM_DOC = "lego_rocket_mk3_assembly"

parts = FreeCAD.getDocument(PARTS_DOC)
asm = FreeCAD.getDocument(ASM_DOC)
parts.saveAs(os.path.join(MODEL_DIR, "lego_rocket_mk3.FCStd"))
asm.saveAs(os.path.join(MODEL_DIR, "lego_rocket_mk3_assembly.FCStd"))
print("saved FCStd docs")

STLS = [("Pad", "pad.stl"), ("Bell", "bell.stl"), ("Tail", "tail.stl"),
        ("Body", "body.stl"), ("Porthole", "porthole.stl"),
        ("Taper", "taper.stl"), ("Stage", "stage.stl"), ("Nose", "nose.stl"),
        ("BoosterBody", "boosterbody.stl"), ("BoosterCone", "boostercone.stl")]

for objname, fname in STLS:
    obj = parts.getObject(objname)
    sh = obj.Shape.copy()
    sh.Placement = FreeCAD.Placement()  # translate back to origin for export
    mesh = MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.02,
                                  AngularDeflection=0.35, Relative=False)
    path = os.path.join(MODEL_DIR, fname)
    mesh.write(path)
    mb = mesh.BoundBox
    print("%s -> %s facets=%d bb=%.1fx%.1fx%.1f" % (
        objname, fname, mesh.CountFacets, mb.XLength, mb.YLength, mb.ZLength))
