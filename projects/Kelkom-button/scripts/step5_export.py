import FreeCAD as App
import Mesh

doc = App.getDocument("kelkom_button")
base = "/home/brian/ClaudeProjects/3d-modeling-brain/projects/Kelkom-button/kelkom-intercom-button"
doc.saveAs(base + ".FCStd")
objs = [o for o in doc.Objects
        if o.TypeId.startswith(("Part::", "PartDesign::")) and o.Visibility]
Mesh.export(objs, base + ".stl")
Mesh.export(objs, base + ".3mf")
print("exported", len(objs), "object(s)")
