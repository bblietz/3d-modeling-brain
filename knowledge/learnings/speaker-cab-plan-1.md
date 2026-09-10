---
name: speaker-cab-plan-1-retrospective
description: What worked and what failed while executing Plan 1 of the speaker cab system (voicing engine, knowledge notes, twenty-speaker catalog) by subagent-driven development on 2026-09-09
type: learning
created: 2026-09-09
tags: [learning, speaker-cab, process, sdd]
---

# Speaker cab Plan 1 retrospective

Plan 1 of [[speaker-cab-system-design]] landed on 2026-09-09: `scripts/cabvoice.py` with __TESTS__ tests, [[speaker-cab-construction]], [[speaker-cab-voicing]] with its calibration table, and twenty notes in `knowledge/speakers/`. Fifteen tasks, each implemented by a fresh Sonnet 5 subagent from a task brief and reviewed by a Fable 5.1 subagent, then a Fable 5.1 whole-branch review and one fix wave. The ledger of every review, fix, and ruling is `.superpowers/sdd/progress.md` (git-ignored, vault root).

## What worked

- **Pre-flight transcription run.** Before any task was dispatched, a subagent transcribed every code block in the plan into a scratch mirror and ran it. That caught the one hard blocker (three archive URLs with `?model=` that PyYAML cannot parse unquoted) and six text contradictions, all fixed in one plan amendment before Task 1. Every later task then transcribed cleanly on the first try.
- **Complete code in the plan plus verbatim transcription.** Fifteen Sonnet 5 implementers produced byte-identical files every time; not one transcription error across the code, tests, and notes. Reviews could concentrate on the plan's own defects.
- **A review per task on the most capable model.** Fable 5.1 reviewers found real plan gaps that the tests as written would not have caught: `displacement_l` unvalidated; the port cap overshooting 150 mm; `open_back`, `power_check`, and `dims_for_volume` accepting non-positive inputs; width conflicts resolved silently; stereo chambers narrower than a 12 inch cutout; a stale port volume of 183,826 L in voicing.json. Each fix was a few lines plus a test, proven on the mirror against every later task before dispatch.
- **Reviewers who fetch primary sources.** The catalog reviews fetched all ten Celestion pages, nine Eminence documents, the Jensen spec sheets and drawings, and the WGS pages, and checked every value. That is how the WGS Vas inconsistency (printed Vas computed with a 366 cm2 cone) and a false "Celestion does not publish the bolt circle" claim were found.
- **The mirror as an oracle.** Keeping the pre-flight mirror patched in step with the fixes let every fix be proven against the whole 15-task suite before an implementer touched the vault.

## What failed or cost time

- **Trusting a reviewer's factual claim without a fetch.** One reviewer said Celestion does not publish the bolt circle; the citation pass wrote that into ten notes; the next reviewer fetched the pages and found "Mounting hole PCD: 297mm" on every one. Rule: a claim about an external source gets fetched before it is written into a note.
- **Amendments that introduced new defects.** The first voicing-note amendment made two rules deterministic in a way that broke them (a genre point aimed at a table that names no speakers; a power step that moved the engine's hard stop). Both were caught on re-review, but a rule change deserves the same check as code: trace what consumes it before writing it.
- **Prose numbers drifting from the code.** "12 to 13 percent low", "19 seed notes", "three of four designs", and the stereo per-channel wording were all wrong in ways the code was not. Prose that quotes a computed number should be generated or checked by running the code.
- **The scratchpad is wiped by a restart.** The mirror, the sync tool, and three drafts vanished when the session process restarted mid-review. Tools and drafts belong in the vault (`projects/<Name>/pipeline/`), as [[project-keep-tools-in-vault]] already says.
- **Concurrent sessions in one repository.** Another session committed Garmin work to main mid-run. Explicit-path commits kept the histories clean, but every review range had to be recorded by SHA rather than taken from HEAD.

## Starting values set during execution (revisit with listening notes)

- Ranking: 1 point for a match in the amp-family row, 1 for a Best with genre match; active pickups prefer speakers with 25 percent more handling than `min_power_w`.
- WGS Vas rescaled by (530 / 366.1)^2 = 2.096 (Veteran 30 38.8 L, ET65 35.8 L, Green Beret 22.0 L).
- Port diameter is a hard 150 mm maximum; stereo minimum width includes the 18 mm divider.
- The calibration table on the site box is the first evaluation set; nothing has met a microphone.

## Open items carried to Plans 2 and 3

__OPEN_ITEMS__
