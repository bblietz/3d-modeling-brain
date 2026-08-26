---
name: shape3d-interop
description: How to programmatically read, write, and exchange Shape3d surfboard files, and the alternatives (researched 2026-08-08)
date: 2026-08-08
---

# Shape3d interop

Distilled from deep research on 2026-08-08 into whether Claude can "talk to" Shape3d X.

## The app itself: not scriptable

- Shape3d X has no API, SDK, scripting, plugin system, CLI, or batch mode. No developer docs exist at all. Support is FAQ/manual/email; there is no official forum.
- Windows and macOS only, and the Mac build is itself a Wine port, so the binary is Wine-compatible. PlayOnLinux has an approved install script (Wine 1.4.1 + gdiplus) but real-world Linux reports are sparse. Not installed on this machine; no Wine prefix here.
- The only official web surface is Shape3d Cloud / Board Builder: iframe embeds with URL parameters and postMessage, not a REST API.

## The file format: the real integration point

- Both `.s3dx` (current) and `.s3d` (V8) are XML. Structure: root `Shape3d_design` > `Board`, with outline (XY) and bottom/deck profile (XZ) Bezier curves, numbered `Couples_N` cross-section slices, control points as `Point3d` with `x/y/z` plus `Tangents_1`/`Tangents_2` and continuity flags. Fin boxes/plugs are also in the file.
- Known quirks (both confirmed 2026-08-08 in Brian's real file, `projects/Surfboards/7-6-22_7_8-3-Kustom-Beak.s3dx`, v9.1.0.4): (1) a malformed tag containing a space, `<Ref. point>`, which breaks strict XML parsers; sanitize to `<Ref.point>` before parsing. (2) A raw unescaped `&` inside the `<License>` element text, an invalid entity reference; escape bare `&` not followed by a valid entity. Files are iso-8859-1 with CRLF line endings. After sanitizing both, Python ElementTree parses the file cleanly (working script: exploratory `s3dx_inspect.py`, see [[project-surfboard-shape3d]]).
- Confirmed structure of a real v9 file: `Board` header holds name/author, dims in cm (Length/Width/Thickness, Tail_rocker/Nose_rocker), volume in deciliters, then `Otl` (outline Bezier), `StrBot`/`StrDeck` (bottom and deck stringer profiles), rail definition curves (`curveDefTop0..4`, `curveDefSide0/3/4`), `Couples_N` slice cross-sections (each a degree-3 Bezier, position encoded in the point x-coordinates), `Stringer_N`, `Box_N` (fin boxes), plus display/color/deco settings. Brian's 7'6" file: 4521 elements, 523 `Point3d`, 8 slices of 24 points each.
- No official spec; everything is reverse-engineered. Pre-V8 `.s3d` files differ and may not parse. The Design tier "file protection" feature may produce non-parseable files.
- Open-source reference implementations to crib from:
  - [Super Shaper 9000](https://github.com/garthtrickett/super-shaper-9000) (Rust/WASM browser CAD, AGPLv3, active 2026): the only project that both reads and writes `.s3dx` (and `.brd`).
  - [S3DtoFusion](https://github.com/0xhexdec/S3DtoFusion) (Python, MIT): cleanest small `.s3dx` reader (`s3dModel/s3dx.py`, xml.dom.minidom).
  - BoardCAD `S3dReader.java`/`S3DWriter.java` (Java, GPL): reads and writes V8 `.s3d` only, chokes on `.s3dx` (the Ref. point bug, hornstein/boardcad-java issue #6). Fork [BoardCAD LE](https://github.com/HavardNJ/boardcad-LE) is actively maintained, adds an S3dxReader and STL export, drops STEP and Jython.
  - [s3dx-viewer](https://github.com/jfpardy/s3dx-viewer) (TypeScript/Three.js, early-stage).

## Geometry semantics (confirmed 2026-08-08 against three reference parsers plus Brian's file)

- Cubic segment i of any `Bezier3d` uses poles `[CP[i], T2[i], T1[i+1], CP[i+1]]`. Tangents are ABSOLUTE coordinates, not offsets; `Tangents_1` = incoming handle, `Tangents_2` = outgoing. Endpoint and corner handles may coincide with their anchor; that encodes corners, do not repair. `Tangents_m` is an all-zeros placeholder. A `u` value other than -1 on a point means a rational weight (rare).
- Frames, all in cm: x runs tail (0) to nose (= Length), y is lateral half-width from the stringer, z is up with 0 at the lowest point of the bottom rocker. Outline `Plan 1` (xy), stringers `Plan 2` (xz), slices `Plan 3` (yz) with the station duplicated into every point's x.
- Slice z datum VARIES by file: the community FISH fixture stores absolute z (bottom anchor = StrBot at the station); Brian's v9.1.0.4 file stores bottom-relative z (add StrBot(station)). Detect by testing which identity holds; slice deck-center plus StrBot equals StrDeck in the relative variant.
- Slices are exact at their own stations: slice max y equals outline half-width there, and the z span equals StrDeck minus StrBot (verified to 4 decimals on all 8 slices of Brian's board). The surface between stations = blend of neighboring slice shapes (Shape3d uses a Catmull-Rom-style Hermite, not linear) rescaled to the local outline width and stringer heights.
- Nose-cap slices (the 2-3 clustered at x near Length) can carry deck-side control points with large NEGATIVE y that mirror values in the `curveDefTop` definition curves; they are construction data for the tip cap, not literal cross-sections. Reconstruct the tip from outline plus stringers instead.
- x may be a tape-measure (developed) coordinate along the bottom rocker rather than Cartesian (`LengthDev` vs `Length`, about 0.7% on Brian's board; possibly governed by `StringerMeasurement`). Only Super Shaper 9000 corrects for this; ignore for visualization, revisit for CNC fidelity.
- Parser gotchas beyond the two sanitization quirks: the FIRST `Point3d` under every `Polygone3d` is the `Symmetry_center`, skip it; `Couples_N` also appear NESTED inside `Calque_N` 3D layers (swallow tails, channels), so parse direct children of `Board` only; a thickness-curve `<Thickness>` element can collide with the scalar `<Thickness>` when `DeckComputed` is set; honor iso-8859-1; `Control/Tangent_type_point_i` ints have leading spaces; slices may be open (missing the deck-center point, synthesize from StrDeck); outline x is NOT monotonic on swallow tails, so never bisect it globally by x.
- The outline is stored twice per file: `Otl` and an `OutlineDef` (BezierDef) copy with identical anchor coordinates. Geometry edits must update both, and likely the related `curveDefTop/Side` projections for curves they mirror.
- Working reconstruction: `projects/Surfboards/kustom-beak-76.FCStd` (parse, curve skeleton, skinned surface; see the project note there).
- Working writer: `scripts/s3dx.py` - formatting-preserving tokenizer (no XML parser, quirks kept verbatim), byte-identical unmodified round trip proven against Brian's file, surgical `%.6f` value edits. Tests: `scripts/test_s3dx.py`.

## Getting designs INTO Shape3d

Best first: write native `.s3dx` (or V8 `.s3d`) directly; the free Lite tier opens all native formats and can send files to ~400 cutting centers. AkuShaper (SaaS, $13+/mo) also exports `.s3dx` officially. Mesh routes are poor: STL/IGES import needs the paid Import/Scan option and does a lossy curve fit; IGES must be simple untrimmed NURBS. Shape3d has no STEP support in either direction (FAQ-confirmed).

## Getting designs OUT of Shape3d

Reading `.s3dx` directly bypasses all license gating and is lossless at the curve level. Via the app: 2D exports (TXT/DXF/IGES/PDF) need Design Pro; 3D mesh export (STL/OBJ/DXF/IGES/VRML, spline surfaces IGES-only) needs the paid 3D Export option; G-code needs the CNC option.

## FreeCAD route

No surfboard workbench or macro exists anywhere. A parametric generator is very feasible in FreeCAD Python (already wired via MCP): define outline, rocker, foil thickness, and rail profile as BSplines; compute closed station sections; loft. Hard parts: closing nose/tail without degenerate sections, rail tangency continuity. Curves workbench (tomate44/CurvesWB, active, Gordon surface tool) is the escape hatch for loft quality. Export STL/STEP/3MF natively for printing. See [[printer-x2d]] for print-side constraints.

## Bottom line

You cannot drive the Shape3d application, but you do not need to: the format is sanitizable XML with four open parsers to reference. Read the user's existing boards directly; write `.s3dx` for anything that must land back in Shape3d; use FreeCAD for anything headed to the printer.
