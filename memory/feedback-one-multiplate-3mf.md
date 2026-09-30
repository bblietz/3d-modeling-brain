---
name: feedback-one-multiplate-3mf
description: Deliver each project's prints as ONE multi-plate Bambu 3MF (one plate per part or part group), never several separate 3MF files
metadata:
  type: feedback
---

Every project ships ONE Bambu Studio project 3MF with a plate per part (or per group printed together), not a separate 3MF per part. Brian, 2026-09-29, after the Logodude badge, stand figure and stand base came as three files: "always create a multiple plate 3mf file for projects instead of multiple files".

**Why:** one file per project is what he opens in Studio; he picks the plate to print there. Separate files scatter one project across the folder.

**How to apply:** when a project has more than one printable part, build them onto plates of a single `<project>.3mf` (per-plate filaments, prime tower only on multi-color plates, per-object overrides where a part needs different settings), and remove superseded per-part 3MFs. Keep per-part STLs as fallbacks. Plates cannot be assigned by the CLI directly; see the multi-plate notes in the 3d-model skill and [[reference-two-material-two-plate-3mf]]. The GUI open is the only ground truth for plates (a hand-authored plate once rendered empty). Proven route: the CLI's own multi-plate assembler (`--load-assemble-list`), as in projects/Logodude/pipeline/make_print_3mf.py; Brian confirmed all three Logodude plates in the GUI 2026-09-29. Related: [[project-logodude]].
