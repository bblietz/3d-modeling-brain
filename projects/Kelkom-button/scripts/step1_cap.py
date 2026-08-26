import FreeCAD as App
import Part

# Fresh document
for d in list(App.listDocuments()):
    App.closeDocument(d)
doc = App.newDocument("kelkom_button")

# --- Dimensions (user-measured) ---
L1 = 13.6    # layer 1 (top cap) square
L2 = 12.54   # layer 2 square
T1 = 2.0     # layer 1 thickness
T2 = 4.0     # layer 2 thickness
LEG_L = 14.0
# z=0 at leg tips; layer 2 spans 14..18; layer 1 spans 18..20
Z_L2 = LEG_L
Z_L1 = LEG_L + T2
Z_TOP = LEG_L + T2 + T1

cap1 = Part.makeBox(L1, L1, T1, App.Vector(-L1/2, -L1/2, Z_L1))
cap2 = Part.makeBox(L2, L2, T2, App.Vector(-L2/2, -L2/2, Z_L2))
solid = cap1.fuse(cap2).removeSplitter()

obj = doc.addObject("Part::Feature", "Button")
obj.Shape = solid
doc.recompute()

import FreeCADGui as Gui
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")
print("OK cap stack, bbox:", obj.Shape.BoundBox)
