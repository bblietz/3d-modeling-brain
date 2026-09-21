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

## 16. MagSafe case magnet array (ADG R30 chapter 42)

Added 2026-09-20 for the MagSafe ring pocket. Sources: ADG R30 chapter 42, p268 to 287 (case array figures on p269, p271, p272; accessory-side cross-checks p274 to 282; verification p283 to 285), general rules on p26, p29, p39, p42, p49 to 50, p76 to 77, plus drawing sheet 2 (PDF p3) and the sheet 1 notes. These ADG pages are in addition to the `adg_pages_used` list in the frontmatter. ADG PDF page index equals the printed page number.

Confidence labels as defined at the top of this note, with two additions for this section:

- **A** also covers numbers printed inside the ADG figures. Those figures are stroked CAD text with no text layer, so each was rendered at 400 to 1200 dpi, and every value closes arithmetically against its neighbors (for example 2.900 + 1.150 = 4.05 = (54.10 - 46.00) / 2, and 50.49 - 31.18 = 19.31).
- **I** = my inference. Not Apple's words.
- **V** values here come from the sheet 2 vector paths. Scale 1.3828 pt/mm, agreeing three ways (product width, product length, the dia 57.50 circle) within 0.02 percent.

Apple calls the ring the "ARRAY MAGNET" and the orientation magnet the "CLOCKING MAGNET".

### 16.1 Ring, Fig 42-2 "MagSafe magnet array dimensions" p271 and Fig 42-3 "Section C-C" p272

| Item | Value | Conf | Source |
|---|---|---|---|
| Outer diameter | dia 54.10 (this surface is datum B) | A | Fig 42-2 p271 |
| Inner diameter | dia 46.00, with control frame "single circle symbol, 0.05, B" | A | Fig 42-2 p271 |
| Radial width | 4.05 | A | Fig 42-3 p272 |
| Mean diameter | 50.05 | D | |
| Magnet thickness | 0.55, no tolerance printed | A | Fig 42-3 p272 |
| Gap in the ring | none. Drawn as a complete closed annulus in both Fig 42-1 (p269, isometric) and Fig 42-2 | A, by absence | |
| Number and shape of segments | not given. No segment lines, count, or arc angles are drawn for the case ring | unknown | |
| Radial pole layout, outer edge to inner edge | outer pole 1.150, then a non-magnetized zone "abs(Bz) < 80 mT" 1.750 wide (D, 2.900 - 1.150), then inner pole "(1.150)" reference. Apple prints 1.150, 2.900, 4.05 | A | Fig 42-3 p272 |
| Pole radii from the ring center | outer pole r 25.90 to 27.05, dead zone r 24.15 to 25.90, inner pole r 23.00 to 24.15 | D | |
| Polarity | outer pole: N faces the device, S faces the accessory. Inner pole: S faces the device, N faces the accessory | A | Fig 42-3 p272 |

- Control frame reading (I): a single circle is the circularity symbol, which takes no datum. Because datum B is referenced, the intent is probably concentricity of the inner diameter to the outer diameter within 0.05.
- Do not confuse this with the ACCESSORY ring (Fig 42-7 and 42-8, p276 to 277): same dia 54.10 and 46.00, but with a gap (2X 10.00 deg max array magnet gap, 8.25 max opening), magnets 1.10 thick, and a 0.70 low carbon steel DC shield behind them. The gap and the steel shield belong to chargers and wallets, not to cases.

### 16.2 Orientation magnet, Fig 42-2 p271 and Fig 42-4 "Section D-D" p272

Coordinates are from the ring center (boxed basic 0.00 / 0.00 origin at the center of datum B).

| Item | Value | Conf |
|---|---|---|
| Width | X -3.00 to 3.00, "(6.00)" reference. 6.00 is printed again in Fig 42-4 | A |
| Length | Y -31.18 to -50.49, "(19.31)" reference | A |
| Thickness | 0.55, no tolerance printed | A, Fig 42-4 |
| Corner radii | none given. Drawn as a sharp-cornered rectangle in Fig 42-1 and Fig 42-2 | unknown |
| Center distance from the ring center | 40.835 along the long axis, 0.00 sideways | D, (31.18 + 50.49) / 2 |
| Gap from the ring OD to the magnet's near end | 4.13 | D, 31.18 - 27.05 |
| Farthest corner from the ring center | 50.58 | D |
| Pole layout across the 6.00 width | three stripes of 1.167 separated by two non-magnetized zones "abs(Bz) < 80 mT" of 1.250 (D). Apple prints 1.167, 2.417, 3.583, 4.833, 6.00 measured from one long edge | A |
| Polarity | the two outer stripes: N faces the device. Center stripe: S faces the device | A |
| Cross-check on the accessory side | Fig 42-11 p280 prints the identical -31.18, -50.49, -3.00, 3.00, (19.31) | A |

**Direction: toward the BOTTOM edge of the phone, along the long axis (D, high confidence).** Apple never writes this in words anywhere in chapter 42. It follows from three independent facts:

1. Fig 42-2 places the magnet at negative Y, and Apple's device drawing uses negative Y ordinates running down from the top edge (-79.93, -114.87, -153.94).
2. On sheet 2 the only zone whose callout says "EXCEPT MAGSAFE MAGNETS" extends below the product center out to R 51.89. That encloses the magnet's farthest corner (50.58) with 1.31 to spare. The same magnet placed above the center would reach Y 29.44, inside the camera zone, which has no MagSafe exception.
3. ADG 42.2.2.1 p274 limits an oriented accessory to 30 mm from the ring center "towards the top edge of the device", so oriented accessories hang downward.

The stripes run along the 19.31 length (I). The Section D-D cut line is not drawn on Fig 42-2, but its 6.00 total equals the magnet width, and the accessory's equivalent Section G-G (p280) is drawn across the width.

### 16.3 Position on the iPhone 15 Pro Max

| Item | Value | Conf |
|---|---|---|
| Ring center requirement | "DATUM B CENTER TO BE PLACED WITHIN +/-0.30MM TO INTEGRATED PRODUCT CENTER" | A, Fig 42-2 p271 |
| Product center | X 38.37 from the side edge, Y 79.93 from the top edge. Both are labeled "PRODUCT CENTER" on the MagSafe view | A, sheet 2 |
| dia 57.50 zone | fitted center X 38.364, Y 79.933, fitted dia 57.51. Section 10 is confirmed: centered on the product center | V |
| R 51.89 arc | fitted center X 38.362, Y 79.956, fitted R 51.87. Arc exists on the lower side only and bulges toward the bottom edge; lowest point Y 131.82 (D) | V |
| Arc meets the side edges | Y 114.86 by arithmetic from R 51.89 about the product center, vs Apple's "2X 114.87" | D |
| Top of the MagSafe band = bottom of the camera no-magnetic zone | Y 46.76, full width. Apple does not label it. Same method returns 45.217 for the printed 45.22 | V |
| Ring footprint on the phone | X 11.32 to 65.42, Y 52.88 to 106.98 | D |
| Orientation magnet footprint | X 35.37 to 41.37 (FRONT and REAR frames agree within 0.01), Y 111.11 to 130.42, center Y 120.77 | D |
| Self alignment | accessories shall "magnetically self align within a 1.55 mm radial maximum" | A, 42.1.2 p270 |
| Coplanarity | "Magnets in the MagSafe case magnet array shall be positioned in the same plane" | A, 42.1.2 p270 |

"Integrated product center" is read as the phone's product center with the case fitted (I, supported by sheet 2 centering every MagSafe zone on the labeled product center).

### 16.4 Through-thickness stack, Fig 42-3 and Fig 42-4 p272 (both print the same three numbers)

| Layer, from the phone outward | Value | Conf |
|---|---|---|
| Case inner surface ("SURFACE TOWARD DEVICE - MEASUREMENT PLANE") to the magnet's device-side face | 0.55 +/-0.05 | A |
| Magnet | 0.55 | A |
| Magnet's accessory-side face to the case outer surface ("SURFACE TOWARD ACCESSORY - MEASUREMENT PLANE") | "0.85MM MAXIMUM" | A |
| Sum | 1.95 at maximum outer cover; 1.90 to 2.00 across the +/-0.05 | D |
| Back thickness | "uniform thickness no greater than 2.1 mm; Apple recommends 2.0 mm" | A, 42.1.1 p269; drawing note 8 also says 2.1 mm MAX |
| Thickness check | 2.1 or less at four points along the ring and two points along the orientation magnet, digital thickness gauge | A, 42.4.1.1 p283 |

- Apple does NOT put the magnet against the phone. 0.50 to 0.60 of case material sits between the back glass and the magnet, and at most 0.85 sits between the magnet and the accessory.
- No minimum outer cover is given. No adhesive layer, pocket clearance, or magnet thickness tolerance is shown for the case array (the accessory figures show a "(0.05)" adhesive layer; the case figures show none).
- Status of the figures: 42.1.2.2 p270 says the magnets "shall be positioned in the case following the dimensions and polarity shown in" Fig 42-2, 42-3, 42-4. 42.1.2.1 p270 also calls Fig 42-3 "a reference design ... for how to achieve the desired retention force".

### 16.5 Magnet material and force (A)

- N45SH NdFeB with an 8 to 16 um epoxy coating "(or similar non-metallic coating)". Table 42-1 p270: Br 13.2 to 13.6 kGs, Hcb 12.75 kOe min, Hcj 20.50 kOe min, BHmax 43 to 46 MGOe.
- Surface field shall not exceed 0.215 T on either the interior or the exterior surface of the case (p270).
- Pull-off normal to the back: "nominal target between 1000 gf and 1300 gf" with the case on the device (42.1.2.3 p272). The verification procedure (42.4.1.3.3 p285) instead requires the average of 5 pulls on an Apple MagSafe Charger to be 800 gf to 1100 gf "when removing the mass of the Apple MagSafe Charger and eyelet assembly". Apple prints both ranges; section 11 row 11 above quotes only the first.
- Must work with the Apple MagSafe Charger and the iPhone FineWoven Wallet (wallet animation appears; low coercivity stripe cards survive 10 s), and an Apple MagSafe Battery Pack must seat with "only the mating surface" in contact (p269, p283 to 286).
- Shall not interfere with inductive charging (42.1.3 p273).
- Apple's recommended array vendors (p269): Baotou INST Magnetic New Materials, Ningbo Sanhuan Magsound, Quadrant Solutions.

### 16.6 Cases without magnets, and steel attach rings

What Apple prints (A, verbatim):

- ADG 5.1.4 p39: cases "claiming compatibility with MagSafe or Qi wireless power 2.0 or later ... shall: Integrate a MagSafe Case Magnet Array" and shall not have rear pockets or holders for cards.
- ADG 42.1.1 p269: shall "Firmly attach to the device without relying on the magnets" and "Not integrate magnets on the back of the case other than the MagSafe magnets".
- ADG 4.8 p26: "Unless otherwise specified, Apple recommends avoiding the use of magnets and metal components in accessories."
- Drawing note 1: "NO METAL CONTACT WITH PRODUCT."
- Drawing note 5: "RELATIVE MAGNETIC PERMEABILITY OF ANY METAL USED ON CASE: 1.05 MAX, PER ASTM A342/A342M-14."
- Drawing note 7: "NO MAGNETS ON REAR OF PRODUCT EXCEPT MAGSAFE MAGNETS."
- Sheet 2, dia 57.50 disc, flag 5: "DO NOT OBSTRUCT THIS AREA WITH METAL, CONDUCTIVE MATERIAL, OR MAGNETIC MATERIAL".
- Sheet 2, band down to R 51.89, flags 5 and 7: "DO NOT OBSTRUCT THIS AREA WITH MAGNETIC OR PERMEABLE MATERIAL EXCEPT MAGSAFE MAGNETS".
- Sheet 2, camera zone out to X_r 45.22: "DO NOT OBSTRUCT THIS AREA WITH MAGNETIC OR PERMEABLE MATERIAL (FULL PRODUCT VOLUME INCLUDING SIDE WALLS)".

What Apple does NOT print: any guidance for a magnet-free MagSafe pass-through case; any thickness figure for one beyond the general 2.1 mm MAX of note 8; any mention of steel or ferrous attach rings in a case. In chapter 42 the word steel appears only for the ACCESSORY DC shield ("low carbon steel (1010, DT4 or similar)", 42.2.2.7 p281). Chapter 37 (inductive power, p257 to 258) has no case guidance either.

Reading (I): Apple's documents do not permit a steel attach ring. The only exception written into the MagSafe zones is for "MAGSAFE MAGNETS", and a steel ring is metal, conductive, and permeable, sitting inside the dia 57.50 disc. Note 5's 1.05 ceiling excludes carbon steel and 400 series stainless, whose relative permeability runs to the hundreds or more (general engineering knowledge, not from Apple). This binds only a case sold as compliant. For a personal print it is a functional risk call: a metal ring over the charging coil (heating, charging efficiency) and the compass.

Inconsistency to be aware of (facts A, conclusion I): the Apple-spec ring (dia 46.00 to 54.10) lies entirely INSIDE the dia 57.50 disc, and that disc's own callout carries only flag 5 with no "except MagSafe magnets" wording. Only the orientation magnet (31.18 to 50.49 out) sits in the band that carries the exception. Note 7 and ADG 42.1 make clear the MagSafe magnets belong there, so I read the disc callout as "nothing else in this area".

### 16.7 Keepouts near the pocket, for a plain TPU pocket

- Plain non-conductive TPU is unrestricted by every magnetic and metal zone above. Avoid carbon filled, glass filled, or conductive TPU (section 11 rule 12).
- NFC: no NFC antenna location or NFC keepout is drawn for this phone. ADG 4.9.5 p29 says only that accessories shall not degrade NFC and that risk rises if they intrude on the antenna keep-out zones. The pocket clears both antenna zones (D): the top zone ends at Y 16.89 (side strips to 33.62 and 28.55) vs ring top Y 52.88; the bottom zone starts at Y 138.68 between X_r 4.89 and 71.46 vs the magnet's far end at Y 130.42, a margin of 8.26. The R 51.89 arc itself stops 6.86 short of that band.
- Compass: X_r 58.06, Y 153.94 (A). Marker dia 6.40 (V; not dimensioned, may be symbolic). Distances (D): 76.58 from the ring center, 49.53 from the ring OD, 28.84 from the nearest corner of the orientation magnet. Apple gives no numeric compass keepout. ADG 5.5 p42: cases shall not interfere with the magnetic compass. The compass test (5.10.8 p77) is NOT in the iPhone 15 Pro Max case testing matrix (Table 5-12, p49 to 50), which lists NFC (p76) and "MagSafe Case Magnet Array (page 283) ... Cases supporting MagSafe only".
- Camera: no magnetic or permeable material in the camera zone (X_r 0 to 45.22, Y 0 to 46.76 V). The ring's top edge is 6.12 below that zone and 6.34 below the plateau outer boundary at Y 46.54 (D). ADG 4.8 p26 and 5.5 p42: no effect on autofocus or OIS.
- Side clearance (D): the ring OD is 11.32 from each side edge; the dia 57.50 disc is 9.62 from each side edge.
- Uniform back: 42.1.1 requires uniform thickness, and the 2.1 max is checked ON the ring and ON the orientation magnet, so a pocket must not raise a bump over 2.1 there.
- Accessory seating, accessory-side rules that shape the case back (A for the numbers, I for applying them to a case): accessory faces are flat only out to 27.20 from the array center and fall away by 0.92 at radius 30.00 (42.3 p282). Accessories may reach 30 mm from the ring center toward the top edge and need 6 mm clearance beyond that (42.2.2.1 p274). 30 mm above the center is Y 49.93, which is 3.39 below the plateau outer boundary (D). So keep the case back flat out to at least 30 mm radius, and keep any raised camera guard above Y 49.93.

### 16.8 Not found in either source

- Ring segment count, segment shape, and segment joint gaps for the CASE array.
- Orientation magnet corner radii.
- Tolerances on magnet thickness (0.55), ring diameters (beyond the 0.05 control frame), and orientation magnet length and width (given only as basic ordinates with reference sizes).
- A minimum for the outer cover over the magnet (only "0.85MM MAXIMUM").
- Adhesive thickness, pocket clearance, or retention method for the case array.
- The words "toward the bottom" or any stated direction for the orientation magnet (derived in 16.2).
- Any rule or number for a magnet-free case or for a steel or ferrous attach ring.
- Any NFC antenna location or numeric NFC or compass keepout distance.
- The Section C-C and Section D-D cut lines on Fig 42-2 (only datum flags B and C are drawn).
