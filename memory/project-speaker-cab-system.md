---
name: project-speaker-cab-system
description: Custom guitar speaker cab capability for MaximoCabs; plan 1 (knowledge base + cabvoice.py) built 2026-09-09, plan 2 (cablayout.py + cabmodel.py generator, engine and catalog touches, site-default fixture) built 2026-09-11; plan 3 (the /speaker-cab skill) designed and planned 2026-09-11, execution next
metadata:
  type: project
---

Brian is adding a guitar speaker cabinet design capability to the vault for his MaximoCabs custom cab business (site repo at ~/ClaudeProjects/MaximoCabs, quote-only Astro site, dormant since 2026-07-26). Spec approved 2026-09-09 at projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md, amended for Unit 2 by projects/Speaker-cab-system/2026-09-10-plan-2-generator-design.md. Locked: 1x12 and 2x12 (mono or stereo), closed, closed-ported and open-back; Thiele-Small voicing in scripts/cabvoice.py; finger joints on both lines with a through-dovetail option on hardwood (no corner posts; the site copy still says corner posts and is wrong); ears-only validation; builder package plus customer proposal; no pricing, no site configurator.

Plan 1 done 2026-09-09: cabvoice.py propose/evaluate, knowledge notes, twenty speaker notes. Plan 2 done 2026-09-11: scripts/cablayout.py (numeric layout kernel, 42 tests with a 1200-case matrix on live proposals), scripts/cabmodel.py (build123d layer, 23 tests, CAD matrix 12 default and 60 full), engine touches (tube-snapped ports, 44 mm shell margin, 68 mm 2x12 cutout gap, height floor, hardwood floors plus 2 mm, inside-parts allowance, frame and magnet diameters), cutlist extra lines, fixture order projects/Speaker-cab-system/fixtures/site-default/ (0 mm off the site box). Full suite 465 tests. Retrospectives at knowledge/learnings/speaker-cab-plan-1.md and speaker-cab-plan-2.md.

**Why:** the site promises rig-specific volume, port, and baffle design; Plans 1 and 2 give it the acoustics and the geometry. Every construction number is a starting value (status unverified-starting-values) until a build measures it.

**How to apply:** for any cab order, use the /speaker-cab skill once Plan 3 builds it; until then run cabvoice.py, copy the fixture's cab.py into projects/Cab-<Customer>-<NxS>-<line>/ (any depth under the vault root; cab.py walks up to scripts/cablayout.py), edit its aesthetics constants, and run it with EXPORT=1 (exit 0 pass or warn, 1 input error, 2 blocker). Plan documents live in projects/Speaker-cab-system/; the Plan 2 mirror in its pipeline/plan2-mirror/ is the oracle the plan's code came from: fix landed code, copy into the mirror, re-run pipeline/embed_plan_code.py. Confirm construction defaults with Brian before trusting them. See [[reference-vault-github-repo]] for commit and push habits.
