---
name: project-surfboard-shape3d
description: Brian's Shape3d surfboards - parsing proven, Kustom Beak 7'6" rebuilt in FreeCAD, writer not started
metadata:
  type: project
---

Brian designs surfboards in Shape3d X and wants Claude to work with them. Status as of 2026-08-08: his board files live in `projects/Surfboards/`; parsing is proven and his 7'6" Kustom Beak was reconstructed and visually verified in FreeCAD (`projects/Surfboards/kustom-beak-76.FCStd`). Confirmed format semantics and parser gotchas are in `knowledge/shape3d-interop.md`; per-board notes in `projects/Surfboards/brief.md`.

The .s3dx writer is built (`scripts/s3dx.py` + tests, TDD, byte-identical round trip proven). Awaiting acceptance: Brian must open `projects/Surfboards/kustom-beak-test-write.s3dx` in Shape3d to confirm the app accepts written files. Not yet built: domain-level edit helpers (outline is duplicated in-file as Otl + OutlineDef; edits must touch both) and a parametric generator. Goal (full-size boards to cutting centers vs 3D-printable fins/models) still unstated.
