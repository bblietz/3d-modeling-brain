# Fork E report: skill prose in the Plan 3 mirror

Task: write SKILL.md, the brief and listening-notes templates, and the exact skill edits for the plan, under `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/`. Nothing outside the mirror was touched; nothing committed.

## Files written

| File | Lines |
|---|---|
| `.vault/skills/speaker-cab/SKILL.md` | 342 |
| `.vault/skills/speaker-cab/templates/brief.md` | 145 |
| `.vault/skills/speaker-cab/templates/listening-notes.md` | 53 |
| `.vault/plan/skill-edits.md` | 84 |

Checks run: zero em dashes in all four files; the three frontmatters parse with PyYAML (SKILL.md has only `name` and `description`); the description sentence is verbatim from design 3.1; every "old line" in skill-edits.md was grepped against the landed `skills/furniture/SKILL.md`, `skills/3d-model/SKILL.md`, and `CLAUDE.md` and matches byte for byte; the spec's Unit 3 heading matches the insertion anchor. SKILL.md headings are exactly the eleven the design names, plain hyphens.

## Gaps the design left and the choice made

1. **Evaluate-first on a ported standard-size box needs a port.** `evaluate` requires a port for closed-ported, so the skill evaluates the site box with the site port (the 101.5 mm tube at 40 mm, the calibration port; box and port fix Fb, the speaker sets the character). Command in Phase 2 step 4: `--internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40`. Fork D's evaluate-first paragraph in the voicing note should state the same port.
2. **The acceptance rule points at the note's bridge**, not a mapping of its own: "accept the site box when the sheet's character is the bridge word for the target's low_end in the note's Enclosure type rules". Fork D writes the bridge; nothing in SKILL.md will contradict it.
3. **cab.step for real orders stays out of git.** SKILL.md says the vault ignores `projects/Cab-*/*.step`; skill-edits.md section 5 gives the two `.gitignore` lines the plan must append (the vault only ignores the fixtures' STEP today). The plan's Task for SKILL.md and carve-outs should carry that edit, or the sentence in Phase 7 must go.
4. **Load-bearing follow-ups** are named concretely (the primary amp's rated power and taps when the model is unknown, a binding size or weight limit, the jack configuration on a 2x12, a supplied speaker's impedance) so "stop only when the batch is not empty" has a definition.
5. **Handoff path** is the project directory's `.claude/context-check/last-handoff.md`, per CLAUDE.md, not the vault root.
6. **Phase 5 operator rows** are the eight from design 3.3 with the furniture buildability table's wording adapted; the row names must match `cabreport.py` exactly: `stock thickness`, `grain and show face`, `joinery fit`, `stock yield`, `wood movement`, `transport`, `weight vs limit`, `size vs limit`, verdict word `operator`.
7. **Phase 2 ranking** cites the note's procedure (2 points per Character word, 1 for the amp-family row, 1 for the genre key) without restating the point values, so a change in the note does not strand the skill; the precedence sentences and the eight keys are in the skill verbatim from design 7.
8. **min_power_w**: the skill computes 1.5 x the highest rated amp and writes it to tone.json; the hard stop and the warning are described as the engine's. `--accept-low-headroom` is presented as the way a `breakup: early` target accepts the warning (spec power rule).
9. **Commit message form** for an order: `Cab <Customer> <NxS> <line>: order package`; the trailers come from the session, not the skill.
10. **Delegations**: two, under the vault's agent policy (catalog read for the ranking in Phase 1's last paragraph; render inspection in Phase 4), as design 3.1 asks; no subagent mechanics in the skill.

## What the plan writer and the other forks must match

- **Fork C (cabreport.py, proposal.md template):** CLI exactly `scripts/cabreport.py <order-dir> [--customer NAME] [--proposal-template PATH] [--verify]`; `checks.md` written every run; `proposal.md` written only when absent; exit 2 on a failed verify listing missing facts and empty slots; slot markers `<!-- slot: name -->` / `<!-- /slot -->` with the four names `rig_and_goals`, `why_this_cabinet`, `designed_to_do`, `alternatives`; a literal `Price:` line; the "no swatch on file" wording; a header comment in the template carrying the site's voice samples; the eight operator row names above and the engine row names `power`, `wiring`, `port air speed`, `alignment`, `engine warning`.
- **Fork A (engine):** flags exactly `--port-tube MM` (52.0, 77.3, 101.5, 153.2), `--fb HZ`, `--port-count N`; a port-fit blocker's remedy text is what the skill quotes, and the pinned re-run's warnings are what step 3 of the loop reads ("no blocker and no port warning").
- **Fork B (layout):** the `port fit` blocker must name the longest tube or the shelf that fits (step 1 of the loop reads it); render file names `cab-iso.png`, `cab-front.png`, `cab-top.png`, `cab-right.png`, `cab-exploded.png` are quoted in Phase 4.
- **Fork D (notes):** the voicing note needs the evaluate-first paragraph with the bridge and the site port, the Genres line form on every catalog note (the skill says "the genre key on the note's Genres line"), the precedence sentences, and the construction note needs "the default front slot" the loop's step 4 refers to.
- **Templates:** `brief.md` sections in the design's order with angle-bracket placeholders; its frontmatter `configuration` values are `1x12 | 2x12-mono | 2x12-parallel-out | 2x12-stereo`. `listening-notes.md` is a `type: learning` note whose heading form `cab-<customer>-<config>` matches the retrospective path in Phase 8.
- **skill-edits.md** holds seven numbered edits: the two carve-outs, the two CLAUDE.md bullets, the gitignore lines, the spec pointer, the symlink command with its expected `ls -la` output.

Out of scope, noted: the site's quote email subject line contains an em dash; SKILL.md describes the email by its body labels only.
