---
name: project-speaker-cab-system
description: Custom guitar speaker cab capability for MaximoCabs; spec approved 2026-09-09, plan 1 (knowledge base + cabvoice.py, 351 tests) built and reviewed 2026-09-09; plan 2 generator next
metadata:
  type: project
---

Brian is adding a guitar speaker cabinet design capability to the vault for his MaximoCabs custom cab business (site repo at ~/ClaudeProjects/MaximoCabs, quote-only Astro site, dormant since 2026-07-26). Spec approved 2026-09-09 at projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md. Locked: 1x12 and 2x12 (mono or stereo), closed-ported and open-back; Thiele-Small voicing in scripts/cabvoice.py plus tone rules; ears-only validation with listening notes feeding knowledge/speakers/ notes; builder package plus customer proposal; no pricing, no site configurator.

Plan 1 done 2026-09-09: cabvoice.py propose/evaluate with voicing.json and voicing.md, 351 tests, two knowledge notes with a calibration table, twenty speaker notes (Celestion missing or analog, Eminence and Jensen datasheet, WGS estimated). Every number is a starting value until listening notes exist. Executed as subagent-driven development with a Fable 5.1 review per task and a whole-branch review; retrospective at knowledge/learnings/speaker-cab-plan-1.md.

**Why:** the site promises rig-specific volume, port, and baffle design but nothing acoustic existed before Plan 1. Every number in the knowledge notes starts as unverified-starting-values.

**How to apply:** for any cab order, use the /speaker-cab skill once built (fork of [[feedback-agentic-os-conventions]] furniture workflow). Plan 1 lives at projects/Speaker-cab-system/plan-1-knowledge-engine.md; Plan 2 (scripts/cabmodel.py generator from voicing.json) is next, then Plan 3 (the skill); the open items for both are in the retrospective. Confirm the construction defaults with Brian before trusting them. See [[reference-vault-github-repo]] for commit and push habits.
