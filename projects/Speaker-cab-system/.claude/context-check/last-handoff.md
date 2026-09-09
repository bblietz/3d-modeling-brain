# Handoff: Speaker-cab-system (2026-09-08)

## State
Plan 1 written 2026-09-09 (projects/Speaker-cab-system/plan-1-knowledge-engine.md, 15 tasks); awaiting execution choice. Brainstorming complete via /superpowers:brainstorming. Intake fields revised 2026-09-09 (stereo 2x12, placement, impedance, primary amp, climate added; three fields dropped). Design spec written and committed at
projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md. Awaiting Brian's review of the
written spec, then invoke superpowers:writing-plans to produce the implementation plan (three phases:
knowledge base and engine, generator, skill).

## Decisions already locked
- Range: 1x12 and 2x12, closed-back ported and open-back. No 4x12, 1x10, combos, iso or bass cabs.
- Deliverables: builder package (CAD, cut list, voicing sheet) plus customer proposal. No site configurator, no pricing.
- Acoustics: Thiele-Small for closed and ported, empirical open-back rules, no diffraction/FEM.
- Validation: ears only; every prediction labeled unverified; listening notes feed speaker notes.
- Architecture: approach A (fork /furniture + scripts/cabvoice.py + knowledge base with frontmatter speaker catalog).
- Spec location: project directory, matching FreeCAD-setup and Garmin conventions (no docs/ in this vault).

## Files that matter
- MaximoCabs site: ~/ClaudeProjects/MaximoCabs (src/content/cabinets/*.md, src/lib/quote-schema.ts)
- Furniture skill to fork: skills/furniture/SKILL.md; cut list: scripts/cutlist.py

## Next action
Ask Brian to review the spec. On approval: Skill superpowers:writing-plans, plan lives in projects/Speaker-cab-system/plan.md.
