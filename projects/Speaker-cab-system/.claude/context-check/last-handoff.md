Continuing work on 3d-modeling-brain (vault, branch main), project Speaker-cab-system: the custom guitar speaker cabinet capability for MaximoCabs. Done so far:
- Brainstormed and approved the design spec: projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md (intake revised 2026-09-09; data_status amended to five values).
- Researched speaker datasheets: Celestion publishes only Fs and Re (only measured data is Voice Coil's Heritage G12H(55) test); Eminence and Jensen publish full T/S; WGS units are inconsistent. Vented model hand-checked against Eminence designs (3 of 4 within 2 percent).
- Wrote Plan 1 (15 tasks, complete code, 3888 lines): projects/Speaker-cab-system/plan-1-knowledge-engine.md, committed 55502b4 and pushed to origin/main.
- Memory saved: memory/project-speaker-cab-system.md (indexed in memory/MEMORY.md).
- Brian chose subagent-driven execution. superpowers:subagent-driven-development was invoked but NO task has been dispatched yet and no progress ledger exists for this project.

Current state: git clean, main in sync with origin/main at 55502b4. Nothing from Plan 1 is built yet (no scripts/cabvoice.py, no knowledge/speakers/). Existing tests: scripts/test_s3dx.py only. Python venv at .venv (3.12, pyyaml, pytest, numpy).

Files that matter:
- projects/Speaker-cab-system/plan-1-knowledge-engine.md: the plan; single source of requirements for every task, values verbatim.
- projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md: approved spec (Units 1b, catalog, knowledge, testing, error handling bind Plan 1).
- projects/Speaker-cab-system/.claude/context-check/last-handoff.md: project-local handoff with the locked-decisions block (vault convention, committed).
- skills/furniture/SKILL.md, scripts/cutlist.py: patterns Plans 2 and 3 fork later; not needed for Plan 1.

Decisions already locked:
- Range 1x12 and 2x12 (mono, mono with parallel out, stereo with divided chamber), closed-ported and open-back; no 4x12, combos, iso or bass cabs.
- Deliverables: builder package plus customer proposal; no pricing, no site configurator.
- Acoustics: Thiele-Small closed and Small vented model (QL 7), open-back path estimate; box sized by Vas/alpha (1.5, 1.0, 0.65) clamped 30 to 68 L per driver; rule-of-thumb 34/44/56 L; Fb = Fs x 0.9/0.8/0.7 clamped 45 to 90 Hz; port 75 mm start, 17 m/s, 20 mm minimum length, 150 mm max diameter.
- Validation ears only; every prediction labeled "unverified, ears only".
- data_status values: datasheet, third-party, analog, estimated, missing. Celestion: G12H Anniversary and Vintage 30 are analogs of celestion-heritage-g12h55; the other seven are missing. WGS estimated. Eminence and Jensen datasheet. Twenty notes.
- Tests live at scripts/test_cabvoice.py (beside test_s3dx.py), run with .venv/bin/python -m pytest scripts/test_cabvoice.py -v.
- Plans 2 (cabmodel.py generator) and 3 (/speaker-cab skill) are written only after Plan 1 lands.
- Execution mode: subagent-driven, fresh implementer per task, task review after each, final whole-branch review.

Open item for Brian (ask once, first thing): the vault commits straight to main (all prior work, including the spec and plan, landed on main). The SDD skill wants explicit consent to implement on main or a worktree. Get that answer, then proceed.

Next action: run the SDD pre-flight plan scan, then dispatch Task 1 (frontmatter loader and Driver record) with the task brief from
/home/brian/.claude/plugins/cache/superpowers-marketplace/superpowers/6.0.3/skills/subagent-driven-development/scripts/task-brief projects/Speaker-cab-system/plan-1-knowledge-engine.md 1
on the cheapest model tier (the plan contains the complete code), record the base commit before dispatch, review with scripts/review-package BASE HEAD, and keep the ledger at .superpowers/sdd/progress.md (the Drawer-bench precedent kept its ledger under projects/Drawer-bench/.superpowers/sdd/; either location is fine, but check both before re-dispatching anything).
