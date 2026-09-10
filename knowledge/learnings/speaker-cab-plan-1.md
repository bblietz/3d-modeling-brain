---
name: speaker-cab-plan-1-retrospective
description: What worked and what failed while executing Plan 1 of the speaker cab system (voicing engine, knowledge notes, twenty-speaker catalog) by subagent-driven development on 2026-09-09
type: learning
created: 2026-09-09
tags: [learning, speaker-cab, process, sdd]
---

# Speaker cab Plan 1 retrospective

Plan 1 of [[speaker-cab-system-design]] landed on 2026-09-09: `scripts/cabvoice.py` with 351 tests, [[speaker-cab-construction]], [[speaker-cab-voicing]] with its calibration table, and twenty notes in `knowledge/speakers/`. Fifteen tasks, each implemented by a fresh Sonnet 5 subagent from a task brief and reviewed by a Fable 5.1 subagent, then a Fable 5.1 whole-branch review and one fix wave. The ledger of every review, fix, and ruling is `.superpowers/sdd/progress.md` (git-ignored, vault root).

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
- **Concurrent sessions in one repository.** Another session committed Garmin work to main mid-run, and its staging swept this very file into two of its commits while it was an untracked draft. Explicit-path commits on this side kept the engine's history clean, but every review range had to be recorded by SHA rather than taken from HEAD, and drafts in a shared working tree are not private.

## Starting values set during execution (revisit with listening notes)

- Ranking: 1 point for a match in the amp-family row, 1 for a Best with genre match; active pickups prefer speakers with 25 percent more handling than `min_power_w`.
- WGS Vas rescaled by (530 / 366.1)^2 = 2.096 (Veteran 30 38.8 L, ET65 35.8 L, Green Beret 22.0 L).
- Port diameter is a hard 150 mm maximum; stereo minimum width includes the 18 mm divider.
- The calibration table on the site box is the first evaluation set; nothing has met a microphone.

## Open items carried to Plans 2 and 3

- **Plan 2 (generator):** read `construction` (which since Task 16 on 2026-09-10 also carries `line`, `species`, and `wall_material`), `port.location`, `port.count`, and each speaker's `displacement_estimated` from voicing.json rather than parsing warning text; assert the cutout fits the baffle height (the engine enforces only a minimum width); model the hardwood line's 19 mm shell and corner posts and compare with the 18 mm voicing (1 to 2 percent of volume); round port diameters to purchasable tube sizes and re-solve the length with `port_dims`.
- **Plan 3 (skill):** treat CLI exit 1 as an input error and exit 2 as blockers (argparse also exits 2); present the impossible-box trade-off from the blocker text; the ranking needs the canonical keys the fix wave introduced plus a stated precedence (amp-family table over a note's own list); "lowest tuning in range" for low-end shifters needs an Fb override in `Constraints`; the plain-language reading the spec asks for belongs in the skill's template, not the engine. Also from the fix-wave re-review: a pinned or driver-count minimum width over the size limit still raises rather than presenting a trade-off; there is no `--port-count` CLI flag; the matrix test runs one tone target (tight) and the label test's genre check is a substring match.
- **Catalog schema:** one Thiele-Small set per note; 16 ohm Eminence variants (Texas Heat, Swamp Thang) differ enough to be a different cabinet, so add a per-impedance set before the first 16 ohm Eminence order.
- **Engine refinements to weigh with Brian:** peak height is read off a 14-point third-octave grid (up to 0.3 dB low; a finer internal grid would move borderline punchy/boomy words); an unconstrained proposal always carries the 2:1 width-to-depth advisory because the site box is 2.06:1; PyYAML is imported but declared nowhere in the vault.
- **Process:** put a propose-versus-evaluate matrix test in every engine plan from the start; the two whole-branch findings that no task review could see (the clamped-port tuning and the unportable mono 2x12) fell out of running the two modes against each other across every configuration.
