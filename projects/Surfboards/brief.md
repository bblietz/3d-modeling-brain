---
name: surfboards-brief
description: Shape3d surfboard project - parsing Brian's boards and rebuilding them in FreeCAD
date: 2026-08-08
---

# Surfboards

Working with Brian's existing Shape3d X designs. Format research and confirmed geometry semantics live in [[shape3d-interop]].

## Boards

### Kustom Beak 7'6" (`7-6-22_7_8-3-Kustom-Beak.s3dx`)

7'6" x 22 7/8" x 3" midlength (227.1 x 58.1 x 7.6 cm), volume about 60.4 L, nose rocker 12.4 cm, tail rocker 5.7 cm, beak nose. Shape3d X file version 9.1.0.4, designed by Brian.

- Parsed 2026-08-08: full curve set extracted (outline, StrBot/StrDeck stringer profiles, 8 slices). Slice z is bottom-relative in this file (see [[shape3d-interop]]).
- Verified: slice max half-width equals outline at every station, and slice thickness plus StrBot equals StrDeck, all to 4 decimals.
- Reconstructed in FreeCAD: `kustom-beak-76.FCStd` - curve skeleton (outline, stringers, slice wires) plus a skinned BSpline surface built by blending slices 1-4 in normalized shape space and rescaling to local width/thickness at ~110 stations. Bounding box matches the spec sheet to the millimeter. Tail edge (2.06 cm) and nose beak edge (1.52 cm) close correctly from outline plus stringer scaling alone.
- Known approximations: linear shape blend between stations (Shape3d uses a Catmull-Rom-style Hermite); the 3 authored nose-cap slices (last 1.5 mm) are replaced by outline/stringer-driven closure; x treated as Cartesian though the file may use developed (tape-measure) x, about 0.7% on this board. All invisible at visualization scale; revisit for CNC or .s3dx write-back.

## Tooling

- `scripts/s3dx.py` (built TDD 2026-08-08, tests in `scripts/test_s3dx.py`, run with `.venv/bin/python -m pytest scripts/test_s3dx.py`): formatting-preserving .s3dx reader/writer. Tokenizes the raw text (no XML parser, so the quirks need no sanitizing), keeps every original byte, and edits replace only the changed values (`%.6f`). Unmodified round trip of the Kustom Beak file is byte-identical. API: `s3dx.load(path)` then `doc.root.find(...)/findall("Couples_*")`, `.text`/`.set_text()`, `.float`/`.set_float()`, `doc.save(path)`.
- Gotcha found while testing: the outline is stored TWICE per file (`Otl` and an `OutlineDef` BezierDef copy); geometry edits must update both. See [[shape3d-interop]].
- Acceptance pending: `kustom-beak-test-write.s3dx` (identical to the original except board name = "Kustom Claude Test") needs to be opened in Shape3d by Brian to confirm the app accepts written files.

## Next steps (not started)

- Domain-level edit helpers (e.g. change width/rocker consistently across Otl, OutlineDef, slices, definition curves) once the acceptance test passes.
- Parametric board generator emitting .s3dx (clone-and-mutate a template file) and/or FreeCAD solids.
