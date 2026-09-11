# Plan 3 mirror review (Fable 5.1, 2026-09-11)

Scope: the whole mirror under `.vault/` against the approved design (`2026-09-11-plan-3-skill-design.md`), after Forks A to E. Prose defects were fixed in the mirror; code was not edited. Suite after the fixes: `./run_tests.sh` 519 passed in 66 s (432 engine, 3 cut list, 50 layout, 24 CAD, 10 report).

## 1. Prose fixes applied

| File | What changed | Why |
|---|---|---|
| `skills/speaker-cab/SKILL.md` Phase 4 | The port loop now lists the five `port fit` blocker forms the layout emits, quoted, each with its next step: (1) "the longest table tube that fits at the 24 mm minimum is N mm" pins N; (2) "tube X x L mm reaches the baffle (or finds no spot); longest tube that fits at this diameter is L' mm" pins the next tube down the table (a smaller area needs a shorter port at the same tuning); (3) "no table tube fits" goes to the stop; (4) the slot shelf forms ("the deepest shelf that fits is N mm", "no shelf fits") go to the stop with a lower slot height, a round port, or a deeper box; (5) "N slot(s) of W mm do not fit the C mm chamber" re-runs once with the width from the new sheet's `box.chamber_internal_width_mm`. The stop's front slot is now spelled out (`--port-slot <width> 40`, two slots of (width minus 18) / 2 on a mono 2x12) and the Fb remedy carries the engine's 45 to 90 Hz range. One automatic re-run per form per order. | The design's step 1 ("take the tube the blocker names") had no next step for three of the five texts the layout produces; a dry run would have stalled on the same-diameter or slot forms. |
| `SKILL.md` Phase 2 step 3 | The low-end-shifter `--fb` rule states the start (45 Hz), the step (5 Hz while the port does not fit), and the engine's range. | Matches the voicing note; the skill had "the lowest tuning in range" with no number. |
| `SKILL.md` Phase 5 | Two sentences: every `cabreport.py` run without `--verify` rewrites `checks.md` (a `--verify` run writes nothing), so the operator rows are judged after the last engine and `cab.py` run and again after any regeneration; warn rows are not operator rows and each kept warn (the expected `port mouth` warns, `spans`, `power`, engine warnings) gets a dated acceptance line in Decisions locked or a re-run. | Fork C's module rewrites `checks.md` on every non-verify run; the skill said "on every run" without the verify exception or the consequence for judged rows. The design's port mouth acceptance into Decisions locked had no home in the skill. |
| `SKILL.md` Phase 6 | Regenerating the proposal (delete `proposal.md`, run again) is stated to rewrite `checks.md` too, so the operator rows are judged again. | Same rewrite semantics. |
| `SKILL.md` Error handling | One bullet: a non-verify run that overwrote a judged `checks.md` means judging again from the brief, not restoring the old file. | Same. |
| `knowledge/speaker-cab-voicing.md` Precedence bullet and Rig adjustments | "raises it in 5 Hz steps while the sheet reads boomy or the port does not fit" became "while the port does not fit the box (a higher tuning needs a shorter port)", plus one sentence that raising Fb does not cure boomy (the engine's own remedy grows the box, then lowers Fb). | `ported_targets` lowers Fb to cure boomy; the note had the direction backwards. |
| `speaker-cab-voicing.md` Speaker ranking procedure step 4 | "Run the engine for the top choice (`evaluate` on the site box first for a standard-size order, else `propose`)". | The step predated the evaluate-first rule the same note now carries. |
| `knowledge/speaker-cab-construction.md` rear round port bullet | The quoted blockers carry their `port fit: ` prefix as the check message does; the too-long form is quoted in full; the loop sentence says what is pinned when only a length is named. | The skill and the plan quote the check message verbatim; the note's quotes were the message minus its prefix. |

No em dashes in any edited file; the eleven headings and the two-key frontmatter of `SKILL.md` are intact (381 lines after the fixes, 342 before).

## 2. Code defects (no edits made)

Critical: none. Important: none that would put a wrong number in a deliverable; the three Important items were prose and are fixed above.

Minor, in file order:

1. `scripts/cabreport.py` `facts`: a tolex order whose `aesthetics.tolex_color` is null renders the finish as `None` and `--verify` passes on the string "None". Scenario: an order whose `cab.py` aesthetics block lost `tolex_color`. Fix: `finish = (... ) or "finish to be confirmed"` and the same guard on `grill_cloth`.
2. `scripts/cabreport.py` `main`: `except (ValueError, KeyError, TypeError)` prints a bare quoted key for a `KeyError` (`input error: 'aesthetics'`), which is what a Plan 2-era `cab.json` without the aesthetics block produces; an `OSError` from an unreadable template is not caught (traceback, exit 1, nothing written, so the contract holds by accident). Fix: name the missing key and file in the message; add `OSError` to the tuple.
3. `scripts/cabreport.py` `verify_proposal`: a presence-only substring check. `configuration` "1x12" is satisfied by "Tolex 1x12" in `line_label`, so a deleted Configuration line still verifies. Fix if wanted: verify the templated line forms (`- Configuration: {configuration}`) rather than bare values; otherwise accept, since the fact strings are still present.
4. `scripts/cablayout.py` `slot_ports`: "1 slot of 472 mm do not fit" (grammar). The skill now quotes it as is; change both or neither.
5. `scripts/cabvoice.py` `--fb`: unbounded in code; the note binds the skill to 45 to 90 Hz (design: "No other rule"). Leave unless Brian wants the cap in the engine.
6. `scripts/test_cablayout.py` `test_port_mouth_site_default_fixture_warns_behind_the_magnet`: `pytest.skip` when the fixture sheet is missing would hide a lost fixture; in the vault and the mirror the sheet exists, so it never skips. Fix: assert the path exists.
7. `scripts/cabreport.py` `check_rows` requires Task 2's `cab.json` (`aesthetics` block, 19 checks). The plan's task order (Task 2 regenerates the fixture before Task 5) satisfies it; a Task 5 implementer running against a stale fixture sees item 2's message.

Read and found sound: `largest_tube_at_minimum` (probes every smaller table tube at the 24 mm minimum with the same obstacles, envelopes, and placed tubes), the `round_ports` no-fit branch (the length probe now ends at exactly 24 mm), `port_mouth_clearances` (mouth plane, straddling parts at 0 mm, terminal faces without coverage, slot effective diameter), the `port mouth` block, `size_port`'s pinned path, `propose`'s override, pinned clamp warning, and floor blockers (deduped in `_assemble`), `dims_for_volume`'s non-strict floors, `tube_from_table`, `_build_parser`, `main`'s evaluate path, `catalog_genres.py` (idempotent by the Genres-line guard), and the new tests (assertions are specific; the CLI tests assert exit codes, stderr text, and that nothing is written on exit 1).

## 3. Design coverage

| Design item | Delivered by | Note |
|---|---|---|
| 3.1 `SKILL.md`: description verbatim, eleven sections, hyphen headings, absolute interpreter, exit table under Prerequisites, swatch source, loop verbatim, two delegations, no FreeCAD | `.vault/skills/speaker-cab/SKILL.md`, plan Task 6 | Loop now more precise than the design's five steps (five blocker forms); 381 lines |
| 3.2 `brief.md`, `proposal.md`, `listening-notes.md` | `.vault/skills/speaker-cab/templates/`, Tasks 6 and 5 | Sections and keys as listed; slot markers and `Price:` line present |
| 3.3 `cabreport.py` contract | `.vault/scripts/cabreport.py`, Task 5 | Deviations: a `--verify` run writes nothing (the design said `checks.md` every run); `--customer` also required to verify; `alignment` shows Fb and F3 on a ported box |
| 3.4 per-order directory | `SKILL.md` Phases 1 and 7 | |
| 4 phases and stops | `SKILL.md` | Evaluate-first, reading in the brief, stop one, stop two |
| 5 port loop | `SKILL.md` Phase 4; `cablayout.round_ports`, `slot_ports`, `largest_tube_at_minimum` (Task 2) | The layout names the tube (Fork B's extension); form 2's automatic step (pin the next tube down when only a length is named) is the reviewer's addition, see item 2 below |
| 6 engine touches: `--port-tube`, `--fb`, `--port-count`, 24 mm, width and height blockers | `cabvoice.py`, Task 1 | |
| 6 layout touches: `port mouth`, check order 19, `aesthetics` block | `cablayout.py`, `test_cabmodel.py`, Task 2 | |
| 7 voicing note: keys, precedence, enclosure precedence, power rule, evaluate-first and bridge, model limits | `.vault/knowledge/speaker-cab-voicing.md`, Task 3 | |
| 7 catalog Best with | 20 notes via `catalog_genres.py`, Task 3 | Three bullets, not two: qualifiers and the wikilink kept on a third line; the test asserts one Amp families line and one Genres line |
| 7 construction note: port mouth, 24 mm, default slot, remedy order | `.vault/knowledge/speaker-cab-construction.md`, Task 4 | |
| 8 fixtures and dry runs | plan Tasks 7 and 8 | Not in the mirror by design; see item 1 below |
| 9 tests | all five test files, 519 in the mirror | The site default warns on `port mouth` (the rule as approved), where the design expected a pass; the test asserts the warn |
| 11 carve-outs, `CLAUDE.md`, spec pointer, site copy note, retrospective and memory | `.vault/plan/skill-edits.md`, `.vault/projects/Speaker-cab-system/site-copy-notes.md`, plan Tasks 6, 4, 9 | |

Gaps for the plan writer:

1. The dry-run answer sheet (design 8) must expect a `port mouth` warn on both fixtures and record its acceptance in Decisions locked; the skill's Phase 5 now says where such an acceptance goes.
2. Form 2 of the loop (a tube that seats but whose port is too long) gets one automatic re-run with the next tube down the table. The design pinned only "the tube the blocker names"; either keep this as a stated amendment to design section 5 or change the skill's form 2 to a stop.
3. Design section 3.3's "written on every run" should read "every run without `--verify`" when the design is amended; the plan's Global Constraints already describe the module correctly.

## 4. Verdict

Ready to embed. The prose fixes are in the mirror; the seven Minor code items are the plan writer's call (items 1, 2, and 6 are one-line fixes worth folding into the plan before it is written; 3 to 5 and 7 can stay as recorded).
