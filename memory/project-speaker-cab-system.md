---
name: project-speaker-cab-system
description: Custom guitar speaker cab capability for MaximoCabs; spec approved 2026-09-09, implementation plan next (knowledge base + cabvoice.py, cabmodel.py generator, /speaker-cab skill)
metadata:
  type: project
---

Brian is adding a guitar speaker cabinet design capability to the vault for his MaximoCabs custom cab business (site repo at ~/ClaudeProjects/MaximoCabs, quote-only Astro site, dormant since 2026-07-26). Spec approved 2026-09-09 at projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md. Locked: 1x12 and 2x12 (mono or stereo), closed-ported and open-back; Thiele-Small voicing in scripts/cabvoice.py plus tone rules; ears-only validation with listening notes feeding knowledge/speakers/ notes; builder package plus customer proposal; no pricing, no site configurator.

**Why:** the site promises rig-specific volume, port, and baffle design but nothing acoustic exists anywhere yet. Every number in the new knowledge notes starts as unverified-starting-values.

**How to apply:** for any cab order, use the /speaker-cab skill once built (fork of [[feedback-agentic-os-conventions]] furniture workflow). Plan lives in projects/Speaker-cab-system/plan.md. Confirm the construction defaults with Brian before trusting them. See [[reference-vault-github-repo]] for commit and push habits.
