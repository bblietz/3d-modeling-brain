---
title: iPhone 15 Pro Max mechanical dimensions (Apple dimensional drawing + ADG R30)
type: reference
project: iPhone-15-Pro-Max-case
date: 2026-09-20
source: https://developer.apple.com/download/files/accessories/dimensional-drawings/iphone-15-pro-max.pdf
source_index: https://developer.apple.com/accessories/dimensional-drawings/
source_guidelines: https://developer.apple.com/accessories/Accessory-Design-Guidelines.pdf
adg_release: R30 (dated 2026-06-08, 401 pages)
drawing_revision: drawing number and REV fields are blank; sheet footer date 2023-10-10; PDF built 2026-06-02
drawing_pages: PDF p1 cover and terms, p2 = SHT 1 of 3, p3 = SHT 2 of 3, p4 = SHT 3 of 3
adg_pages_used: 18, 24, 27-28, 32-46, 49-50, 68-70, 268-273, 283, 384
cross_check: https://support.apple.com/en-us/111828 (76.7 x 159.9 x 8.25 mm, 221 g)
tags: [iphone-15-pro-max, phone-case, tpu, reference, apple-adg]
---

# iPhone 15 Pro Max mechanical dimensions

Reference for the form-fitting TPU case. Printer rules: [[printer-x2d]].

## Sources and confidence

- PRIMARY: Apple "iPhone 15 Pro Max Dimensional Drawings" PDF (3 drawing sheets). Since ADG R30 the drawings are no longer inside the Accessory Design Guidelines PDF; ADG section 1.1 (p18) points to the separate download page.
- RULES: Apple "Accessory Design Guidelines for Apple Devices", Release R30, 2026-06-08.
- Confidence labels used below:
  - **A** = number printed on Apple's drawing. Sheets 2 and 3 have a text layer and every value was matched against it. Sheet 1 has no text layer (stroked CAD text), so every sheet 1 value was read at 600 to 2400 dpi AND checked against the PDF's vector geometry (scaled via known dimensions). All agreed within 0.02 mm.
  - **V** = not dimensioned by Apple; measured by me from the drawing's vector geometry. The method reproduces Apple's printed values within 0.02 mm, but the drawing says DO NOT SCALE, so treat as +/- 0.05 mm.
  - **D** = derived by arithmetic or trigonometry from A values.
- Cross-check: Apple tech specs 76.7 x 159.9 x 8.25 mm vs drawing 76.73 x 159.86 x 8.25. Agrees.
- No fallback (third party) sources were needed. Nothing in this note comes from GrabCAD, iFixit, or case makers.

## Tolerances and drawing conventions (A)

- Units mm. X.X +/- 0.2, X.XX +/- 0.10, X.XXX +/- 0.050, angles +/- 0.5 deg. Nearly every dimension is X.XX, so +/- 0.10.
- Third angle projection. Scale NONE. "Do not scale drawings".

## Coordinate frames used in this note

- **FRONT frame**: looking at the display. X_f from the LEFT edge (the Action and volume button side). Y from the TOP edge, positive downward (Apple prints these as negative ordinates).
- **REAR frame**: looking at the back. X_r from the LEFT edge of the rear view, which is the SIDE BUTTON side. Convert with X_f = 76.73 - X_r. Camera is top left in this frame.
- **Z**: through the thickness. Back glass plane Z = 0, front glass plane Z = 8.25, mid plane 4.125 (Apple prints 4.12 or 4.13).
- **h**: height above the back glass plane (h = -Z direction outward from the back), used for camera features.

## 1. Overall body (A, sheet 1)

| Item | Value | Datum |
|---|---|---|
| Product length | 159.86 | top edge to bottom edge |
| Product width | 76.73 | housing side to side, excludes buttons |
| Product thickness | 8.25 | front glass to back glass, excludes camera |
| Product center | X 38.37, Y 79.93 | from side edge, from top edge |
| Button protrusion beyond housing | 0.45 (all four buttons) | from housing side surface |
| Width over buttons | 77.63 (D) | 76.73 + 2 x 0.45 |

## 2. Plan-view corner, Detail D "corner profile (all four corners)" (A)

Apple gives NO single radius. The corner is a curvature-continuous spline defined by ordinate points, symmetric about the diagonal. a = distance along one edge from the sharp virtual corner, b = inset from the other edge:

| a | 17.24 | 12.36 | 7.58 | 3.48 | 0.90 | 0.05 | 0.00 |
|---|---|---|---|---|---|---|---|
| b | 0.00 | 0.05 | 0.90 | 3.48 | 7.58 | 12.36 | 17.24 |

Tangent points are 17.24 from the virtual corner. Diagonal point (3.48, 3.48).

Extra points on the same curve (V, +/- 0.02): a=5: 2.23, a=6: 1.63, a=7: 1.15, a=8: 0.78, a=9: 0.50, a=10: 0.30, a=11: 0.16, a=12: 0.08, a=13: 0.03, a=14: 0.01.

Single-arc approximation (D): R about 11.9 matches the diagonal point but sits up to about 0.15 mm outside the true curve around a = 9 to 10. Spline through the points instead.

## 3. Edge cross-section, Detail B "profile (all sides)" (A)

Same profile on all four sides and symmetric front to back. Z here is measured from the MID plane; inset is measured inward from the outermost side surface.

| Z from mid plane | +/- 1.84 | +/- 2.46 | +/- 3.07 | +/- 3.62 | +/- 3.99 |
|---|---|---|---|---|---|
| Inset from side surface | 0.00 | 0.00 | 0.06 | 0.32 | 0.81 |

- The side wall is flat (inset 0.00) at least out to Z = +/- 2.46, then curves in with increasing curvature.
- Front face: "2.41 all around, exterior of housing to start of flat area on top side of product". So from the 0.81 inset point (Z = 3.99) the surface keeps rising gently to the full half thickness 4.125 at 2.41 inset. The same 2.41 line is drawn on the back glass in Detail A.
- Glass edge (seam to the titanium band): front glass is inset 1.00 (D, from 76.73 vs 74.73). Back glass edge is inset 1.04 (A, Detail A).
- The lines at Z = +/- 1.84 and +/- 3.99 run the full length of the view; what they represent (finish break, band to glass seam) is NOT labeled.

## 4. Front (A, sheet 1 front view, Detail D; sheet 2 Detail E)

| Item | Value | Datum |
|---|---|---|
| Cover glass outline | 74.73 x 157.86 | centered; 1.00 inset all around (D) |
| Display active area | 71.21 x 154.34 | centered |
| Housing exterior to active area | 2.76 all around | includes corners ("all around") |
| Housing exterior to start of flat glass | 2.41 all around | |
| Receiver (earpiece) slot | 14.54 wide x 0.45 tall | center X 38.37, center Y 1.17 from top |
| Receiver keepout (sheet 2) | 14.40 wide x 0.75 tall | top of keepout 0.85 from top edge, so Y 0.85 to 1.60 |
| Front camera + sensors keepout base | 20.03 x 5.41 stadium, 2X R2.69 | center Y 7.67 from top, on centerline; cone 94 deg |
| ALS keepout base | 9.98 wide, 2X R2.08 | center X 38.79 (datum edge not shown in Detail E; 0.42 off the centerline), Y 12.82 from top; cone 120 deg |
| Dynamic Island pill (Detail D) | 20.69 x 6.07 | center Y 7.67, center X 38.37 |

Drawing note 6 is flagged on the cover glass: DO NOT TOUCH GLASS. Note 4: do not obstruct forward facing sensors. Note 1 is flagged on the receiver and front mic: ports, no metal contact; note 2: do not obstruct ports.

## 5. Left side, viewed from the front: Action, Volume up, Volume down, SIM (A, sheet 1)

Centers measured from the TOP edge. "Length" is along the phone's long axis; "width" is across the band thickness. Apple dimensions each button as a half length from its center.

| Feature | Center from top | Half length | Length (D) | Width | Z of centerline from back glass | Protrusion |
|---|---|---|---|---|---|---|
| Action button | 31.67 | 3.02 | 6.04 | 2.66 | 4.12 | 0.45 |
| Volume up (+) | 45.22 | 5.60 | 11.20 | 2.66 | 4.13 | 0.45 |
| Volume down (-) | 59.42 | 5.60 | 11.20 | 2.66 | 4.13 | 0.45 |
| SIM tray (flush) | 91.07 | 8.07 | 16.14 | 2.76 | 4.12 | none |

- Spans (D): Action 28.65 to 34.69; Vol up 39.62 to 50.82; Vol down 53.82 to 65.02; gap between the volume buttons 3.00; gap Action to Vol up 4.93.
- Buttons are stadium shaped (full round ends, R 1.33 implied, not dimensioned).
- Unlabeled outer outline drawn around each button, probably the housing recess or gap (V): Action 6.40 x 2.90; each volume button 11.80 x 3.26.
- SIM tray: the drawing shows one, so it depicts the physical-SIM variant. US models are eSIM only and have no tray (not stated on the drawing; from Apple's model lineup). The tray is flush, so it does not affect a case either way.

## 6. Right side, viewed from the front: Side button, antenna window (A)

| Feature | Center from top | Half length | Length (D) | Width | Z of centerline from back glass | Protrusion |
|---|---|---|---|---|---|---|
| Side (power) button | 56.17 | 8.85 | 17.70 | 2.66 | 4.12 | 0.45 |
| Side antenna window keepout (sheet 2) | 100.65 | 12.55 | 25.10 | 5.01 | 4.12 | flush |

- Side button span (D): 47.32 to 65.02. Unlabeled outer outline (V): 18.30 x 3.26.
- Antenna window note (A): "Do not obstruct this area with metal or other conductive material. Non-conductive material to be uniform thickness." Span Y 88.10 to 113.20 (D). The drawing does not name it; position matches the US mmWave window (my inference). For TPU: no ribs, texture, logos, or cutouts across this zone.

## 7. Bottom (A, sheet 1 bottom view + Detail C)

X_f is measured from the LEFT edge in the front frame (volume button side). All features are centered 4.12 from the back glass (mid thickness).

| Feature | X_f | Size |
|---|---|---|
| Left hole group, 4 holes | first 20.40, last 27.17, pitch 2.257 (D): 20.40, 22.66, 24.91, 27.17 | dia 1.35 each |
| Left screw | 31.44 | dia 1.50 |
| USB-C port opening in housing | 33.87 to 42.86, center 38.37 | 8.99 wide (D) x 3.14 tall |
| Right screw | 45.29 | dia 1.50 |
| Right hole group, 6 holes | first 49.56, last 60.84, pitch 2.256 (D): 49.56, 51.82, 54.07, 56.33, 58.58, 60.84 | dia 1.35 each |

- "10X dia 1.35 ports". Callouts: Bottom mic 1 = 2nd hole of the left group (22.66). Speaker = right group holes 2 to 5. Bottom mic 2 = last hole of the right group (60.84). Note 2 applies: do not obstruct ports.
- Hole group extents from the centerline 38.37 (D, hole edges): left group 10.52 to 18.64 to the left; right group 10.52 to 23.15 to the right.
- **USB-C recommended connector keepout (Detail C)**: 12.45 wide x 6.60 tall, 2X R3.25 ends, centered on the port (X 38.37, Z 4.12). "Mating connector keepout area flush to product surface, required outward 14.0 mm". Keepout X span 32.14 to 44.59 (D).

## 8. Top

The drawing has no dimensioned top view and shows no openings on the top edge. The three small top views on sheet 2 only show the receiver keepout and the front sensor cones. Nothing to cut out.

## 9. Rear camera (A unless marked; REAR frame, X_r from the side button edge, Y from top)

### Plateau

| Item | Value |
|---|---|
| Plateau OUTER boundary (base of the ramp, at back glass level) | X_r 1.04 to 45.22, Y 1.04 to 46.54 = 44.18 x 45.50 (D) |
| Plateau TOP FLAT (inner rounded square) | X_r 4.70 to 41.56, Y 4.70 to 42.88 = 36.86 x 38.18 (D) |
| Ramp ring width | 3.66 uniform on all four sides (D) |
| Back glass to camera plateau | 2.05 |
| Back glass to rear camera glass (lens top) | 4.07 (one value for all three lenses) |
| Lens protrusion above plateau | 2.02 (D) |

- The outer boundary's top and left edges coincide with the back glass edge (1.04 from the housing exterior). There is NO flat back glass between the plateau and the top or side-button edge.
- In FRONT frame the outer boundary is X_f 31.51 to 75.69 (D).
- Corner shapes are NOT dimensioned by Apple. From vector geometry (V), both are curvature-continuous like the body corner, all four corners congruent. a = distance along the edge from the sharp virtual corner, b = inset:
  - OUTER boundary corner: tangent at a = 17.47, diagonal point (3.90, 3.90); a=4: 3.80, 5: 2.92, 6: 2.20, 7: 1.62, 8: 1.15, 9: 0.78, 10: 0.49, 11: 0.28, 12: 0.14, 13: 0.06, 14: 0.02. Straight runs between corners are only 9.24 (top, bottom) and 10.56 (sides).
  - TOP FLAT corner: tangent at a = 13.81, diagonal point (2.83, 2.83); a=3: 2.66, 4: 1.84, 5: 1.23, 6: 0.77, 7: 0.44, 8: 0.22, 9: 0.09, 10: 0.03, 11: 0.01.
  - Rough single arcs (V, least squares): outer R about 13.9 (max error 0.39), top flat R about 10.5 (max error 0.43). Use the point tables.
- Ramp cross-section between the two boundaries is a concave fillet; radius not dimensioned.

### Lenses, flash, sensor, mic

| Feature | X_r | Y from top | Size |
|---|---|---|---|
| Rear camera 1 | 14.17 | 14.17 | outer ring dia 16.20 |
| Rear camera 2 | 14.17 | 33.41 | outer ring dia 16.20 |
| Rear camera 3 | 32.16 | 23.79 | outer ring dia 16.20 |
| Flash | 32.16 | 10.22 | dia 6.90 |
| Rear sensor (LiDAR position; Apple labels it only "rear sensor") | 32.16 | 38.22 | keepout base dia 14.62 on the plateau surface |
| Rear mic | 37.95 | 33.86 | dia 0.75 (note 2: do not obstruct) |

- Apple does not say which camera is main, ultra wide, or telephoto.
- Inner lens rings (V, not needed for a case): dia 15.26, 13.85, 13.55, 13.05, 13.00.

### Keepout cones (A, sheet 2 sections G-G, H-H, J-J). Apex distances are measured from the FRONT cover glass.

| Feature | Full cone angle | Apex distance from front cover glass | Apex height h above back glass (D) |
|---|---|---|---|
| Rear camera 1 | 123.00 deg | 8.28 | +0.03 |
| Rear camera 2 | 86.00 deg | 7.73 | -0.52 |
| Rear camera 3 | 24.10 deg | 4.60 IN FRONT of the front glass (apex is outside the display side) | -12.85 |
| Flash inner cone | 112.00 deg | origin 8.35 | +0.10 |
| Flash outer cone | 157.00 deg | starts at the "transition" plane 12.36 | +4.11, starting at the inner cone's radius there |
| Rear sensor | 80.75 deg | base dia 14.62 sits on the plateau surface | base at h = 2.05 |

Keepout radius r around each axis at height h above the back glass (D):

- Camera 1: r = 1.842 x (h - 0.03)
- Camera 2: r = 0.933 x (h + 0.52)
- Camera 3: r = 0.2135 x (h + 12.85)
- Flash: r = 1.483 x (h - 0.10) up to h = 4.11 (r = 5.95 there), then r = 5.95 + 4.915 x (h - 4.11)
- Rear sensor: r = 7.31 + 0.850 x (h - 2.05)

| h above back glass | Cam 1 | Cam 2 | Cam 3 | Flash | Rear sensor |
|---|---|---|---|---|---|
| 4.07 (lens top) | 7.44 | 4.28 | 3.61 | 5.89 | 9.03 |
| 4.57 | 8.36 | 4.75 | 3.72 | 8.21 | 9.45 |
| 5.00 | 9.15 | 5.15 | 3.81 | 10.32 | 9.82 |

Distance from each axis to the nearest straight edge of the plateau OUTER boundary (D): Camera 1 13.13 (top and left); Camera 2 13.13 (left and bottom); Camera 3 13.06 (right); Flash 9.18 (top), 13.06 (right); Rear sensor 8.32 (bottom), 13.06 (right). The rounded corners start close to these features, so the true minimum is slightly smaller: about 9.1 for the flash and about 8.3 for the rear sensor (V).

## 10. Other keepouts on the drawing (only matter for metal, conductive, or magnetic parts; plain TPU is exempt)

- Notes (sheet 1): 1 no metal contact with product (entire surface); 5 relative magnetic permeability of any metal on the case 1.05 max per ASTM A342/A342M-14; 7 no magnets on the rear except MagSafe magnets; 8 case thickness on the backside 2.1 mm MAX to ensure full functionality (flagged "back of product only").
- Antenna zones, full product volume including sidewalls, no metal or conductive material (sheet 2, REAR frame). TOP zone: full-width band from the top edge to Y 16.89, plus a strip X_r 0 to 4.94 continuing down to Y 33.62, plus the block X_r 66.83 to the far edge continuing down to Y 28.55. BOTTOM zone: band from Y 138.68 to the bottom edge between X_r 4.89 and 71.46, plus a strip X_r 0 to 4.89 starting at Y 126.05, plus a strip X_r 71.46 to the far edge starting at Y 131.96.
- MagSafe: centered on product center (X 38.37, Y 79.93). Inside dia 57.50: no metal, conductive, or magnetic material. Full-width band from just below the camera zone (top Y not labeled) down to an arc R 51.89 about the product center, the arc meeting both side edges at Y 114.87: no magnetic or permeable material except MagSafe magnets. Camera zone out to X_r 45.22: no magnetic or permeable material (full product volume including side walls).
- Compass at X_r 58.06, Y 153.94.
- Sheet 3 "Keep out area 1, 2, 3" on the back glass beside the camera, with 100 / 80 / 100 deg cones. REAR frame: area 1 8.40 x 10.10 (4X R1.30) center X_r 56.35, Y 18.35; area 2 6.90 x 10.72 (4X R0.80) center X_r 57.10, Y 29.26; area 3 21.40 x 4.58 (6X R0.99) center X_r 60.07, Y 39.57. **Purpose is not labeled anywhere on the drawing or in the ADG.** Likely antenna related (my inference, unverified). Commercial cases, including Apple's, cover this area with plain non-conductive material. For TPU: keep plain uniform wall here, no metal, no magnets.

## 11. Apple case design rules that apply (ADG R30; "shall" = required, "should" = recommended)

| # | Rule | Number | ADG ref |
|---|---|---|---|
| 1 | Exposed glass shall not come within 0.85 mm of a flat surface in any orientation with the case on; ideally 1.00 mm. Applies to the screen AND the camera lens glass. Verified with a 0.85 mm plastic feeler gauge at each corner and face down. | 0.85 min, 1.00 ideal | 5.1.1 p32; 5.10.2 p68-70 |
| 2 | Protect from a 1 m drop onto hard paved surface, any orientation. | 1 m | 5.1.1 p32 |
| 3 | Bottom of case: example guidance (written for iPhone X): opening not wider than 50 mm; PC at least 1.15 mm thick. | 50 max, 1.15 min | 5.1.1 p32, Fig 5-1 |
| 4 | USB-C keepout shall be at least 12.35 x 6.50; should be at least 12.45 x 6.60 with full radii. Add margin for case material shift. Apple USB-C Digital AV Multiport Adapter must fit. | 12.35 x 6.50 min; 12.45 x 6.60 rec | 5.1.2.3 p36; 5.10.2.2 p68-69; drawing Detail C adds R3.25 and 14.0 mm outward |
| 5 | All buttons accessible and "not too hard to press". **No numeric force or travel guidance exists** for ordinary buttons (numbers exist only for Camera Control, which this phone lacks). | none | 5.1.2.1 p33; 5.10.2.2 p68 |
| 6 | Touchscreen: allow a 120 deg opening along the edges of the active area (measured from the screen plane at the active-area edge, so the lip must stay under a 60 deg line rising outward from that edge). No edges that trap water at a 30 deg tilt. Edge swipes must stay easy. | 120 deg | 5.1.2.6 to 5.1.2.7 p37-38, Fig 5-4 |
| 7 | Cover glass contact: the ADG list of "should not contact the cover glass" models does not include the 15 Pro Max, but drawing note 6 on the cover glass says DO NOT TOUCH GLASS. | | 5.1.2.8 p38; drawing note 6 |
| 8 | Dock compatibility: bottom of device to outside of case should not exceed 1.8 mm. | 1.8 max | 5.1.3 p39 |
| 9 | Acoustics, thin case (wall 2.25 mm or less): openings offset at least 2.0 mm from the edge of any speaker or mic port; case edge at most 1.5 mm thick at the opening's inner diameter; incoming angle at most 45 deg; keep a seal against the housing between ports. Thick case (over 2.25): separate uninterrupted channels for mic and speaker. Never occlude a mic. | 2.0, 1.5, 45 deg, 2.25 | 5.2.3 p40-42, Fig 5-5 |
| 10 | Camera: never block the lens FOV or flash illumination; hold the drawing keepouts at worst-case X-Y placement tolerance; avoid narrow or steep openings; chamfer the trim near the camera; semi-gloss BLACK around camera and flash recommended; matte or diffuse and strongly colored trim degrade images. | | 5.7 p43-45 |
| 11 | MagSafe: a case that CLAIMS MagSafe must integrate the magnet array; uniform back thickness no greater than 2.1 mm, 2.0 recommended; must hold the phone without relying on magnets; no other magnets on the back; no rear card pockets. Accessories must self align within 1.55 mm radial; pull-off 1000 to 1300 gf. Thickness verified at four points on the ring and two on the orientation magnet. | 2.1 max, 2.0 rec | 5.1.4 p39; 42.1 p269-272; 42.4.1.1 p283; drawing note 8 |
| 12 | RF materials to avoid: metals, conductive coatings, high dielectric (permittivity over 5), plastics with ANY carbon or glass content, high carbon black paints, high TiO2 white paints. So no carbon fiber or conductive/ESD TPU. | | 4.9.1 p27-28 |
| 13 | Hold the device securely with easy insertion and removal, no scratching; no color transfer; haptics feel unchanged; no interference with compass, camera AF or OIS. | | 5.4, 5.5 p42; 5.8 p45 |

Magnet-free MagSafe pass-through: the ADG gives NO thickness figure for a case without magnets. The only numbers are the 2.1 mm maximum back thickness (drawing note 8 and 42.1.1).

## 12. Design implications for the TPU case (D, my arithmetic, not Apple's words)

- **Screen lip plan width**: glass starts 1.00 in from the housing edge, the receiver keepout starts 0.85 in at top center, the active area starts 2.76 in. A lip that stops at 0.85 or less from the housing exterior touches neither glass nor receiver. Height above the front glass 0.85 min, 1.00 ideal. The 120 deg rule allows height up to 1.73 x (distance from lip inner edge to the active-area edge), about 3.3 mm for a 0.85 lip, so it is not binding.
- **Camera ring height**: to satisfy rule 1 the ring must reach h = 4.92 min (5.07 ideal) above the back glass, which is 2.82 to 2.97 above a 2.1 mm back.
- **Rear sensor cone is the binding constraint**: a wall on the plateau outer boundary at the bottom edge (8.32 from the sensor axis) may only reach h = 3.24. With 0.5 clearance (8.82 away) h = 3.83. To reach h = 5.0 the wall top must be 9.82 from the axis, so chamfer the ring's inner edge outward at 40.4 deg from vertical or more along the bottom run near X_r 32.16.
- **Flash outer cone is the second constraint**: toward the top edge the plateau boundary is 9.18 from the flash axis, max h = 4.77 there; at the phone's top edge (10.22 away) max h = 4.98; at 11.7 away max h = 5.28. Chamfer the inner top edge of the ring near the flash too.
- Camera cones are not binding for an opening that clears the plateau outer boundary.
- **Camera opening**: clear the OUTER boundary (X_r 1.04 to 45.22, Y 1.04 to 46.54) plus clearance. It runs to within 1.04 of the top and side-button edges, so the ring merges into the case's top and side walls at that corner.
- **Bottom openings** per rule 9 (2.0 offset from hole edges): left slot X_f 17.73 to 29.85, right slot X_f 46.89 to 63.52, each 5.35 tall, centered at Z 4.12. USB-C opening X_f 32.14 to 44.59. That leaves TPU bridges about 2.3 wide on each side of the USB-C opening. Outer span of the three openings 45.8, under the 50 mm guidance even if they were merged.
- **Bottom wall thickness** 1.8 max for docks; wall 2.25 or less keeps the "thin case" acoustic rules in play.
- **Button covers**: button faces stand 0.45 proud; leave relief around 2.66-wide buttons (outer recess outlines 2.90 and 3.26 wide).

## 13. Not found, or not readable with confidence

- Button actuation force and travel: no numeric guidance in ADG R30.
- Magnet-free MagSafe pass-through thickness: not addressed (only 2.1 max).
- Plateau ramp fillet radius: not dimensioned.
- Plateau corner geometry: not dimensioned; V values above.
- Per-lens height: single 4.07 value for all three.
- Button end radii and the outer recess outlines: not dimensioned; V values above.
- Which lens is main, ultra wide, or telephoto: not labeled.
- Purpose of sheet 3 keep out areas 1 to 3: not labeled.
- Meaning of the Z = +/- 1.84 and +/- 3.99 lines in Detail B: not labeled.
- Top edge features: none drawn, no top view dimensions.
- Active-area corner radius: not dimensioned (only "2.76 all around").
- Drawing number and revision: fields blank.
- US eSIM variant and mmWave window: not distinguished on the drawing.
- USB-C keepout spline corner profile exists on ADG p384 (63.4); ordinates NOT transcribed here. The device drawing simplifies it to 2X R3.25.

## 14. Files in this folder

- `Accessory-Design-Guidelines.pdf` (ADG R30, 39 MB)
- `iphone-15-pro-max-dimensional-drawing.pdf` (4 pages)
- `adg-iphone15promax-sheet1.png`, `-sheet2.png`, `-sheet3.png`: full sheets at 300 dpi, numbered to match Apple's SHT 1, 2, 3 (PDF pages 2, 3, 4)
- 600 dpi detail crops: `adg-iphone15promax-sheet1-notes`, `-detailA-camera`, `-detailB-edge-profile`, `-detailC-usbc`, `-detailD-corner-profile`, `-front-view`, `-left-side-buttons`, `-right-side-button`, `-bottom-view`, `-titleblock-tolerances`; `adg-iphone15promax-sheet2-detailE-front-sensors`, `-detailF-rear-sensor`, `-sectionGG-camera12-cones`, `-sectionHH-flash-cones`, `-sectionJJ-camera3-rear-sensor`, `-side-mmwave-window`, `-rear-antenna-keepouts`, `-rear-magsafe-keepouts`; `adg-iphone15promax-sheet3-detailK-keepout-areas` (all `.png`)

## 15. Handling

Apple's title block carries a proprietary notice: keep in confidence, do not reproduce, copy, or publish in whole or part. The PDFs are free public downloads for accessory design, which is this use. Keep the two PDFs and the `adg-*.png` renders local: do not commit them to the GitHub remote and do not embed them in published pages or artifacts. They can be re-downloaded from the source URLs in the frontmatter. The 39 MB ADG PDF would also bloat the repo.
