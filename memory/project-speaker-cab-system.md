---
name: project-speaker-cab-system
description: Custom guitar speaker cab capability for MaximoCabs; plan 1 (knowledge base + cabvoice.py) built 2026-09-09, plan 2 (cablayout.py + cabmodel.py generator) built 2026-09-11, plan 3 (the /speaker-cab skill, cabreport.py, two fixture orders) built 2026-09-11; next is the first real order
metadata:
  type: project
---

Brian is adding a guitar speaker cabinet design capability to the vault for his MaximoCabs custom cab business (site repo at ~/ClaudeProjects/MaximoCabs, quote-only Astro site). Spec approved 2026-09-09 at projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md, amended for Unit 2 by 2026-09-10-plan-2-generator-design.md and for Unit 3 by 2026-09-11-plan-3-skill-design.md. Locked: 1x12 and 2x12 (mono or stereo), closed, closed-ported and open-back; Thiele-Small voicing in scripts/cabvoice.py; finger joints on both lines with a through-dovetail option on hardwood; ears-only validation; builder package plus customer proposal; no pricing, no site configurator; judgment in prose, numbers in code.

Plan 1 done 2026-09-09 (engine, notes, twenty speaker notes). Plan 2 done 2026-09-11 (layout kernel, CAD layer, site-default fixture). Plan 3 done 2026-09-11: skills/speaker-cab/ (SKILL.md plus brief, proposal, and listening-notes templates), scripts/cabreport.py (checks.md and the proposal's facts from voicing.json and cab.json), engine flags --port-tube, --fb, --port-count, --accept-impedance-mismatch with size-limit blockers and a 24 mm port minimum, the layout's port mouth warn and port fit naming the tube that fits, canonical genre keys in the voicing note and every catalog note, and two fixture orders (projects/Speaker-cab-system/fixtures/sample-roots-1x12/ and rex-roots-1x12/) produced by dry runs of the skill. Retrospectives at knowledge/learnings/speaker-cab-plan-1.md, -plan-2.md, -plan-3.md.

**Why:** the site promises rig-specific volume, port, and baffle design; Plans 1 and 2 give it the acoustics and the geometry, Plan 3 the operator workflow with two stops for Brian (voicing approval, package review).

**How to apply:** for any cab order, use the /speaker-cab skill from the quote email; the two fixture orders are the golden examples of a finished order and the port loop. Plan documents live in projects/Speaker-cab-system/; the Plan 3 mirror in its pipeline/plan3-mirror/ is the oracle the plan's code came from, and a fix to landed code is copied there and re-embedded. Every construction number is a starting value until a build measures it; confirm with Brian before trusting one. See [[reference-vault-github-repo]] for commit and push habits.
