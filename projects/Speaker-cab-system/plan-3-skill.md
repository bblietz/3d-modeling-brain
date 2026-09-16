---
name: plan-3-skill
description: Plan 3 implementation plan for the /speaker-cab skill (SKILL.md and templates, scripts/cabreport.py, engine and layout touches, voicing note keys and catalog normalization, two dry-run fixture orders, vault updates); complete code and note text per task, embedded from the tested mirror
type: plan
status: ready
created: 2026-09-11
tags: [project, speaker-cab, plan, skill, workflow]
---

# Speaker Cab Plan 3: The /speaker-cab Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run one MaximoCabs order end to end with Brian as the operator, from a pasted quote email to a committed order directory holding the brief, the approved voicing, the CAD package, the check table, and the customer proposal, with two stops, and prove it on two dry-run fixture orders.

**Architecture:** Judgment stays in prose and notes (the skill's intake, tone target, ranking, approvals, port-loop trade-offs, proposal wording, listening notes); numbers stay in code. The engine gains three flags and two blockers so the loop can pin a tube, override Fb, and present a size-limit trade-off; the layout gains a port mouth warning, a port-fit blocker that names the tube that fits, and an aesthetics block in `cab.json`; a new report module turns `voicing.json` and `cab.json` into `checks.md` and the proposal's facts; the voicing note gains canonical genre keys and the catalog's Best with sections are normalized to them; `SKILL.md` and three templates run the order; two fixture orders produced by dry runs are the golden examples and the skill's acceptance test.

**Tech Stack:** Python 3.12 at `.venv/bin/python` (build123d, trimesh, matplotlib, PyYAML installed), pytest, `scripts/cabvoice.py`, `scripts/cablayout.py`, `scripts/cabmodel.py`, `scripts/cutlist.py`, `scripts/render_stl.py`; Claude Code skills under `skills/` symlinked from `~/.claude/skills/`.

**Spec:** [[2026-09-11-plan-3-skill-design]] (sections 3 to 12), which amends Unit 3 of [[2026-09-08-speaker-cab-system-design]]; open items from [[speaker-cab-plan-1]] and [[speaker-cab-plan-2]] and the ledger.

## Global Constraints

- Millimetres everywhere; inches where the customer or the builder reads them. Sheet tuples are (width, height, depth) as in `voicing.json`; `cab.json` lists are the same order.
- Exit codes shared by every tool the skill runs: 0 written or pass; 1 input error, nothing written; 2 blockers or a failed verify, files still written (argparse usage errors also 2).
- Engine flags this plan adds (Task 1): `--port-tube MM` (one of `PORT_TUBE_ID_MM` 52.0, 77.3, 101.5, 153.2; propose pins the tube with no growth and no snap; evaluate treats it as a validated `--port-diameter`), `--fb HZ` (propose only; recorded as `port.fb_override_hz`), `--port-count {1,2}` (both modes). `MIN_PORT_LENGTH_MM` is 24.0. Sheet keys added: `port.pinned` (bool) and `port.fb_override_hz` (float or null). A pinned port that clamps warns `port clamped at the 24 mm minimum with the pinned {tube} mm tube: tuned {fb_actual} Hz, target {fb} Hz; a larger tube, a lower Fb, or a smaller box lengthens it`; a pinned port over the air-speed limit warns with the existing `port air speed {v} m/s above 17.0 m/s` line instead of growing. A width or height floor over the size limit is a blocker on the written sheet (exit 2) of the form `width floor {w} mm internal (the driver-count minimum) exceeds the size limit {max} mm internal` (also `(pinned width {p} mm external)` and `height floor {h} mm internal (the cutout minimum)`). The Task 7 fix wave adds `--accept-impedance-mismatch` (both modes, the `--accept-low-headroom` pattern): when no wiring option matches the taps it replaces the blocker with the warning `impedance mismatch accepted: {ohm} ohm cabinet on amp taps {taps}` beside the existing `no wiring option matches amp taps {taps}` line, and the sheet key `wiring.mismatch_accepted` (bool, always present) records it; `wiring.recommended` stays null and `voicing.md` reads `Recommended: none matches the amp taps (mismatch accepted)`.
- Layout checks after Task 2, in this order (19): sheet, net volume, stereo balance, cutout, grill opening, port fit, port mouth, magnet to back, handle, head match, line, jack plate, stock, part count, spans, then the CAD layer's interference, air volume, solid count, rectangularity. Plain `cab.py` prints the first 15. `port mouth` warns under one effective diameter and never blocks; its warn reads `chamber 0 port 0: mouth {d} mm from the {obstruction} ({c} percent of the mouth), under one diameter ({D} mm)`. `port fit` names the longest table tube that fits at the 24 mm minimum, or says no table tube fits. A slot up to `SLOT_TRIM_MM` (1.0 mm) wider than its chamber is trimmed to the chamber, not blocked; on the slot re-run the skill pins the external width to the last sheet's so the chamber does not move. `cab.json` carries an `aesthetics` block (the `Aesthetics` dataclass as a dict, 21 keys) beside the existing top-level `corner_joint` and `baffle_mount`.
- Report module (Task 5): `.venv/bin/python scripts/cabreport.py <order-dir> [--customer NAME] [--proposal-template PATH] [--verify]`; `checks.md` written every run with columns Check, Value, Verdict; verdict words pass, warn, blocker, info, operator; operator rows named `stock thickness`, `grain and show face`, `joinery fit`, `stock yield`, `wood movement`, `transport`, `weight vs limit`, `size vs limit`; engine rows named `power`, `wiring`, `port air speed`, `alignment`, `engine warning`; `proposal.md` written only when absent, slots `<!-- slot: name -->` to `<!-- /slot -->` named `rig_and_goals`, `why_this_cabinet`, `designed_to_do`, `alternatives`; the literal `Price:` line; the text `no swatch on file` for an unknown finish or cloth.
- Canonical genre keys (Task 3): `roots-country`, `blues`, `classic-rock`, `indie-alternative`, `jazz`, `metal-high-gain`, `worship-pop`, `funk-rnb`. Every catalog note's Best with section is two lines, `Amp families: ...` and `Genres: key, key`.
- Skill files: `skills/speaker-cab/SKILL.md` with only `name` and `description` in its frontmatter and plain-hyphen headings; templates under `skills/speaker-cab/templates/`; the per-order `cab.py` template is `projects/Speaker-cab-system/fixtures/site-default/cab.py`; orders live at `projects/Cab-<Customer>-<NxS>-<line>/`; the skill is installed by the symlink `~/.claude/skills/speaker-cab -> /home/brian/ClaudeProjects/3d-modeling-brain/skills/speaker-cab`.
- Vault conventions: notes have YAML frontmatter, wikilinks, no em dashes, English, mm. Every command in the skill and in this plan is written with the absolute interpreter `/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python` and runs from the vault root unless a step says otherwise.
- Tests live at `scripts/test_cabvoice.py`, `scripts/test_cablayout.py`, `scripts/test_cabmodel.py`, `scripts/test_cutlist.py`, `scripts/test_cabreport.py`. Full run from the vault root: `.venv/bin/python -m pytest scripts/test_cabvoice.py scripts/test_cutlist.py scripts/test_cablayout.py scripts/test_cabmodel.py scripts/test_cabreport.py -q` (about 90 s; the CAD suite dominates). Baseline before Task 1: 465 passed.
- The mirror `projects/Speaker-cab-system/pipeline/plan3-mirror/` is the tested oracle every code block and note text was embedded from (`.venv/bin/python projects/Speaker-cab-system/pipeline/embed_plan_code.py --plan projects/Speaker-cab-system/plan-3-skill.md --mirror plan3-mirror --check` proves the plan matches it). Transcribe from the plan; when a block fails, diff against the mirror before changing anything, and report every deviation to the reviewer. A fix landed during execution is copied into the mirror file and the plan is re-embedded, so the three stay identical.
- Commit after every task with explicit paths and the attribution trailers from the session; never stage files outside the task's list (another session shares this tree and has its own uncommitted files, currently `projects/Build123d-trial/project-box.3mf`). Ledger: append one line per event to `.superpowers/sdd/progress.md`.
- Model dispatch: implementers Sonnet 5 for Tasks 1 to 6; the two dry runs (Tasks 7 and 8) on Fable 5.1 following `SKILL.md` with the controller answering the stops from the answer sheet; every review Fable 5.1; controller Fable 5.1 (Task 9).

## File Structure

| File | Responsibility |
|---|---|
| `scripts/cabvoice.py`, `scripts/test_cabvoice.py` | Task 1: `--port-tube`, `--fb`, `--port-count`, `MIN_PORT_LENGTH_MM` 24, size-limit blockers, sheet keys; Task 3: the genre-key test appended |
| `knowledge/speaker-cab-voicing.md` | Task 1: calibration table regenerated (one row moves); Task 3: genre keys, ranking precedence, enclosure precedence, power rule, evaluate-first paragraph and bridge, Fb range, model limits |
| `scripts/cablayout.py`, `scripts/test_cablayout.py` | Task 2: `port mouth` check, `port fit` naming the tube that fits, `aesthetics` block in `layout_report` |
| `scripts/test_cabmodel.py` | Task 2: check-name mirror at 19, `FIXTURE_ORDERS` list with the fixture helper and parametrized test; Tasks 7 and 8 add their fixture names |
| `projects/Speaker-cab-system/fixtures/site-default/` | Task 2: outputs regenerated (19 checks, aesthetics block) |
| `knowledge/speakers/<slug>.md` (20 notes), `projects/Speaker-cab-system/pipeline/catalog_genres.py` | Task 3: Best with sections normalized to the canonical keys by the idempotent script |
| `knowledge/speaker-cab-construction.md`, `projects/Speaker-cab-system/site-copy-notes.md`, `projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md` | Task 4: port mouth rule, 24 mm minimum, default front slot, remedy order; the site copy note; the Unit 3 pointer line |
| `scripts/cabreport.py`, `scripts/test_cabreport.py`, `skills/speaker-cab/templates/proposal.md` | Task 5: the report module, its tests, the proposal template it fills |
| `skills/speaker-cab/SKILL.md`, `skills/speaker-cab/templates/brief.md`, `skills/speaker-cab/templates/listening-notes.md`, `skills/furniture/SKILL.md`, `skills/3d-model/SKILL.md`, `CLAUDE.md`, `.gitignore`, `~/.claude/skills/speaker-cab` | Task 6: the skill, its two prose templates, the carve-outs, the vault instructions, the order STEP ignore lines, the symlink |
| `projects/Speaker-cab-system/fixtures/sample-roots-1x12/` | Task 7: the golden order from the site's sample intake, produced by a dry run of the skill |
| `projects/Speaker-cab-system/fixtures/rex-roots-1x12/` | Task 8: the port-loop order (Cannabis Rex, roots tone), produced by a dry run of the skill |
| `knowledge/learnings/speaker-cab-plan-3.md`, `memory/project-speaker-cab-system.md`, `memory/MEMORY.md`, `projects/Speaker-cab-system/.claude/context-check/last-handoff.md` | Task 9: whole-branch review, fix wave, retrospective, memory, handoff, push |

---

### Task 1: Engine flags, port minimum, size-limit blockers

**Files:**
- Modify: `scripts/cabvoice.py` (`MIN_PORT_LENGTH_MM`, `Port`, new `tube_from_table`, `port_dims`, `size_port`, `dims_for_volume`, `Constraints`, `propose`, `render_markdown`, `_build_parser`, `main`)
- Modify: `scripts/test_cabvoice.py` (`test_size_port_grows_when_too_short`, `_matrix_params`, `test_evaluate_reproduces_propose` replaced; fifteen new tests appended)
- Modify: `knowledge/speaker-cab-voicing.md` (calibration table regenerated: the header date and one row)
- Mirror source (byte-identical, for transcription): `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/scripts/cabvoice.py`, `.vault/scripts/test_cabvoice.py`, `.vault/knowledge/speaker-cab-voicing.md` (calibration block)

**Interfaces:**
- Consumes: the Plan 2 engine as landed (`PORT_TUBE_ID_MM`, `snap_tube_id`, `size_port`, `dims_for_volume(..., strict=True)`, `Constraints`, `propose`, `evaluate`, `_build_parser`, `main`).
- Produces: `MIN_PORT_LENGTH_MM = 24.0`; `tube_from_table(diameter_mm) -> float` (raises `ValueError` naming the table); `Port.pinned: bool = False` and `Port.fb_override_hz: float | None = None`; `size_port(..., pinned_mm=None)` (a pinned tube is built once, no growth, no snap); `Constraints.port_tube_mm` and `Constraints.fb_hz` (validated in `__post_init__`); `dims_for_volume` non-strict mode that records "width floor" and "height floor" conflicts and fixes the axis at the floor; sheet keys `port.pinned` and `port.fb_override_hz`; CLI flags `--port-tube MM` (both modes), `--fb HZ` (propose), `--port-count {1,2}` (both modes); the warning and blocker texts listed in Global Constraints. Task 2 reads sheets carrying the two new keys; Task 5 reads `warnings`; Tasks 6 to 8 quote the messages.

Behavior in one paragraph. A pinned tube goes through `size_port` untouched: the length is solved for its area at the target Fb; under 24 mm it is clamped and the sheet warns `port clamped at the 24 mm minimum with the pinned {tube} mm tube: tuned {fb_actual} Hz, target {fb} Hz; a larger tube, a lower Fb, or a smaller box lengthens it` (the free clamp keeps its `port clamped at the size cap` line, and both cases also carry `port_dims`'s `port too short ... clamped to 24 mm` line); over the air-speed limit the sheet warns `port air speed {v} m/s above 17.0 m/s` instead of growing. `--fb` replaces the engine's target after `ported_targets` and is recorded as `port.fb_override_hz`. A width floor (driver-count minimum or pinned width) or a height floor above the `--max-external` limit no longer raises: propose finishes the sheet at the floor and adds a blocker of the form `width floor {w} mm internal (the driver-count minimum) exceeds the size limit {max} mm internal`, so the CLI exits 2 with the sheet written and the skill presents the trade-off; the floor lines are taken from the final box after the settle loop, since a slot that grows inside the loop moves the height floor and an earlier pass's line would contradict the final one. Input errors (exit 1, nothing written): `port tube must be one of 52, 77.3, 101.5, 153.2 mm, not {x}`; `give a slot or a pinned tube, not both`; `give --port-tube or --port-diameter, not both`; `evaluate closed-ported needs --port-length and --port-tube, --port-diameter, or --port-slot`; `fb_hz must be positive`. One Plan 2 remedy sentence was wrong and is corrected here: `port_dims` said "reduce port area or lower Fb" for a too-short port, but length is proportional to area, so the line now reads "a larger port, a lower Fb, or a smaller box lengthens it".

- [ ] **Step 1: Write the failing tests**

In `scripts/test_cabvoice.py` replace these three (the `tube` parameter joins the matrix, one pinned 101.5 mm row per speaker, and the too-short case moves to the 153.2 mm tube because a 24 mm minimum solves 104.7 mm and the locked snap-up rule takes it there):

<!-- code: .vault/scripts/test_cabvoice.py symbols test_size_port_grows_when_too_short,_matrix_params,test_evaluate_reproduces_propose -->
```python
def test_size_port_grows_when_too_short(drv):
    # 60 L at 60 Hz: a 75 mm port needs a negative length; the port grows until its
    # length reaches the 24 mm minimum (104.7 mm across), which snaps up to the
    # 153.2 mm (6 inch) tube (the 20 mm minimum stopped at 100 mm and the 101.5 tube)
    p = cabvoice.size_port(drv, 60.0, 60.0, diameter_mm=75.0)
    assert p.diameter_mm == 153.2
    assert p.length_mm >= cabvoice.MIN_PORT_LENGTH_MM
    assert not any("too short" in w for w in p.warnings)
    assert any(w.startswith("port diameter snapped to the 153.2 mm tube (from 104.7 mm)") for w in p.warnings)

def _matrix_params():
    rows = [(enclosure, jack, n, None, None) for enclosure in cabvoice.ENCLOSURE_TYPES
            for jack, n in (("mono", 1), ("mono", 2), ("stereo", 2))]
    rows.append(("closed-ported", "mono", 1, (352.0, 40.0), None))   # a slot port, evaluated as built
    rows.append(("closed-ported", "mono", 1, None, 101.5))           # a pinned tube, clamped or not
    return [pytest.param(slug, enclosure, jack, n, slot, tube,
                         id=f"{slug}-{enclosure}-{jack}-{n}" + ("-slot" if slot else "")
                         + ("-pinned" if tube else ""))
            for slug in cabvoice.list_speakers(CATALOG)
            for enclosure, jack, n, slot, tube in rows]

@pytest.mark.parametrize("slug,enclosure,jack,n,slot,tube", _matrix_params())
def test_evaluate_reproduces_propose(tone, slug, enclosure, jack, n, slot, tube):
    d = cabvoice.load_speaker(slug, CATALOG)
    z = 16 if 16 in d.impedance_ohm else d.impedance_ohm[0]
    c = cabvoice.Constraints(port_slot_mm=slot, port_tube_mm=tube)
    p = cabvoice.propose([d] * n, [z] * n, enclosure, tone, jack_config=jack, constraints=c,
                         name=slug)
    e = cabvoice.evaluate([d] * n, [z] * n, enclosure, tone, p.box["internal_mm"],
                          jack_config=jack, port=_port_from_json(p.port), constraints=c, name=slug)
    for key, tol in (("fb_hz", 0.05), ("f3_hz", 0.05), ("peak_db", 0.01), ("qtc", 0.01)):
        a, b = p.prediction.get(key), e.prediction.get(key)
        assert (a is None) == (b is None), key
        if a is not None:
            assert a == pytest.approx(b, abs=tol), key
    assert p.prediction["character"] == e.prediction["character"]
    assert p.volumes["per_driver_net_l"] == pytest.approx(e.volumes["per_driver_net_l"], abs=0.05)
    for vol in (p.volumes, e.volumes):
        parts = (vol["net_total_l"] + vol["displacement_l"] + vol["brace_l"] + vol["port_l"]
                 + vol["divider_l"] + vol["inside_parts_l"])
        assert vol["gross_l"] == pytest.approx(parts, abs=0.05)
```
<!-- /code -->

Append at the end of the file, after one comment line `# ---- Plan 3 Task 1: engine flags, port minimum, size-limit blockers ----`:

<!-- code: .vault/scripts/test_cabvoice.py symbols test_min_port_length_is_the_back_panel_plus_the_flange_ring,test_tube_from_table,test_constraints_validate_the_pinned_tube_and_fb,test_size_port_pinned_tube_neither_grows_nor_snaps,test_size_port_pinned_tube_clamps_a_short_port,test_propose_pinned_tube_sheet_and_clamp_warning,test_propose_pinned_tube_air_speed_warns_instead_of_growing,test_propose_fb_override_is_applied_and_recorded,test_propose_width_floor_over_the_limit_is_a_blocker,test_propose_height_floor_over_the_limit_is_a_blocker,test_cli_port_tube_fb_and_port_count,test_cli_evaluate_port_tube_is_a_validated_diameter,test_cli_width_floor_blocker_exits_2_with_the_sheet,test_cannabis_rex_roots_port_loop_cases,test_propose_height_floor_blocker_reports_the_final_height_once -->
```python
def test_min_port_length_is_the_back_panel_plus_the_flange_ring():
    assert cabvoice.MIN_PORT_LENGTH_MM == 24.0
    p = cabvoice.port_dims(40.0, 68.0, diameter_mm=77.3)
    assert p.length_mm == 24.0
    assert any("clamped to 24 mm; a larger port, a lower Fb, or a smaller box lengthens it" in w
               for w in p.warnings)

def test_tube_from_table():
    assert cabvoice.tube_from_table(101.5) == 101.5
    assert cabvoice.tube_from_table(101.5 + 1e-9) == 101.5
    with pytest.raises(ValueError, match="port tube must be one of 52, 77.3, 101.5, 153.2 mm, not 100"):
        cabvoice.tube_from_table(100.0)

def test_constraints_validate_the_pinned_tube_and_fb():
    assert cabvoice.Constraints(port_tube_mm=77.3).port_tube_mm == 77.3
    with pytest.raises(ValueError, match="port tube"):
        cabvoice.Constraints(port_tube_mm=100.0)
    with pytest.raises(ValueError, match="fb_hz"):
        cabvoice.Constraints(fb_hz=0.0)
    assert cabvoice.Constraints().port_tube_mm is None and cabvoice.Constraints().fb_hz is None

def test_size_port_pinned_tube_neither_grows_nor_snaps(drv):
    drv.xmax_mm = 10.0                      # fast enough that the free port grows past 77.3
    free = cabvoice.size_port(drv, 40.0, 60.0, diameter_mm=77.3)
    assert free.diameter_mm > 77.3 and not free.pinned
    p = cabvoice.size_port(drv, 40.0, 60.0, pinned_mm=77.3)
    assert p.pinned and p.diameter_mm == 77.3
    assert p.air_speed_ms > cabvoice.PORT_V_MAX
    assert not any("snapped" in w or "still above" in w for w in p.warnings)
    with pytest.raises(ValueError, match="not both"):
        cabvoice.size_port(drv, 40.0, 60.0, slot_mm=(200.0, 40.0), pinned_mm=77.3)
    with pytest.raises(ValueError, match="port tube"):
        cabvoice.size_port(drv, 40.0, 60.0, pinned_mm=100.0)

def test_size_port_pinned_tube_clamps_a_short_port(drv):
    p = cabvoice.size_port(drv, 60.0, 60.0, pinned_mm=77.3)   # the free port grows to 153.2 here
    assert p.pinned and p.diameter_mm == 77.3
    assert p.length_mm == cabvoice.MIN_PORT_LENGTH_MM
    assert any("too short" in w for w in p.warnings)

def test_propose_pinned_tube_sheet_and_clamp_warning(drv, tone):
    free = cabvoice.propose([drv], [16], "closed-ported", tone)
    assert free.port["diameter_mm"] == 101.5 and free.port["pinned"] is False
    assert free.port["fb_override_hz"] is None
    v = cabvoice.propose([drv], [16], "closed-ported", tone,
                         constraints=cabvoice.Constraints(port_tube_mm=77.3))
    assert v.port["pinned"] is True and v.port["diameter_mm"] == 77.3
    assert v.port["length_mm"] == cabvoice.MIN_PORT_LENGTH_MM
    tuned = cabvoice.port_tuning_hz(v.volumes["per_chamber_net_l"] / 1e3,
                                    v.port["area_cm2"] / 1e4, v.port["length_mm"] / 1e3)
    assert v.prediction["fb_hz"] == pytest.approx(tuned, abs=1e-9)
    assert tuned == pytest.approx(62.4, abs=0.1)
    clamp = next(w for w in v.warnings if w.startswith("port clamped at the 24 mm minimum"))
    assert clamp == ("port clamped at the 24 mm minimum with the pinned 77.3 mm tube: tuned 62.4 Hz, "
                     "target 67.5 Hz; a larger tube, a lower Fb, or a smaller box lengthens it")
    assert not any("snapped" in w or "size cap" in w for w in v.warnings)
    assert "(pinned 77.3 mm tube)" in cabvoice.render_markdown(v)
    same = cabvoice.propose([drv], [16], "closed-ported", tone,
                            constraints=cabvoice.Constraints(port_tube_mm=101.5))
    assert same.port["pinned"] is True
    assert same.port["length_mm"] == pytest.approx(free.port["length_mm"])
    assert not any("clamped" in w for w in same.warnings)

def test_propose_pinned_tube_air_speed_warns_instead_of_growing(drv, tone):
    drv.xmax_mm = 10.0
    free = cabvoice.propose([drv], [16], "closed-ported", tone)
    assert free.port["diameter_mm"] == 153.2                  # grown and snapped
    v = cabvoice.propose([drv], [16], "closed-ported", tone,
                         constraints=cabvoice.Constraints(port_tube_mm=52.0))
    assert v.port["diameter_mm"] == 52.0 and v.port["pinned"] is True
    assert v.port["air_speed_ms"] > cabvoice.PORT_V_MAX
    speed = next(w for w in v.warnings if w.startswith("port air speed"))
    assert speed == f"port air speed {v.port['air_speed_ms']:.1f} m/s above 17.0 m/s"
    assert not any("still above" in w for w in v.warnings)
    assert v.blockers == []

def test_propose_fb_override_is_applied_and_recorded(drv, tone):
    v = cabvoice.propose([drv], [16], "closed-ported", tone,
                         constraints=cabvoice.Constraints(fb_hz=55.0))
    assert v.port["fb_override_hz"] == 55.0
    assert v.prediction["fb_hz"] == pytest.approx(55.0, abs=1e-6)
    assert v.port["diameter_mm"] == 77.3 and v.port["length_mm"] > cabvoice.MIN_PORT_LENGTH_MM
    assert not any("clamped" in w for w in v.warnings)
    assert "- Fb override: 55.0 Hz in place of the engine's target" in cabvoice.render_markdown(v)
    # the box volume is the alignment's, not re-solved for the override
    free = cabvoice.propose([drv], [16], "closed-ported", tone)
    assert v.volumes["per_driver_net_l"] == pytest.approx(free.volumes["per_driver_net_l"], abs=1e-6)
    closed = cabvoice.propose([drv], [16], "closed", tone, constraints=cabvoice.Constraints(fb_hz=55.0))
    assert closed.port is None   # no port, nothing to record

def test_propose_width_floor_over_the_limit_is_a_blocker(drv, tone):
    limit = cabvoice.Constraints(max_external_mm=(600.0, 457.2, 400.0))
    two = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="mono", constraints=limit)
    assert two.box["internal_mm"][0] == pytest.approx(730.0)
    assert ("width floor 730.0 mm internal (the driver-count minimum) exceeds the size limit "
            "564.0 mm internal") in two.blockers
    pinned = cabvoice.Constraints(pinned_external_width_mm=700.0, max_external_mm=(600.0, 457.2, 400.0))
    one = cabvoice.propose([drv], [16], "closed", tone, constraints=pinned)
    assert one.box["external_mm"][0] == pytest.approx(700.0)
    assert ("width floor 664.0 mm internal (pinned width 700 mm external) exceeds the size limit "
            "564.0 mm internal") in one.blockers
    assert not any("floor" in w for w in one.warnings + two.warnings)
    with pytest.raises(ValueError, match="width floor"):     # the direct call stays strict
        cabvoice.dims_for_volume(90.0, min_internal_width_mm=730.0, max_external_mm=(600.0, 457.2, 400.0))

def test_propose_height_floor_over_the_limit_is_a_blocker(drv, tone):
    c = cabvoice.Constraints(port_slot_mm=(352.0, 40.0), max_external_mm=(600.0, 400.0, 400.0))
    v = cabvoice.propose([drv], [16], "closed-ported", tone, constraints=c)
    assert v.box["internal_mm"][1] == pytest.approx(437.0)
    assert ("height floor 437.0 mm internal (the cutout minimum) exceeds the size limit "
            "364.0 mm internal") in v.blockers
    assert v.blockers.count(v.blockers[0]) == 1      # one line: the floor is read from the final box, not every settle pass

def test_cli_port_tube_fb_and_port_count(speakers_dir, tmp_path):
    base = [sys.executable, str(Path(cabvoice.__file__)), "propose",
            "--speakers-dir", str(speakers_dir), "--impedance", "16",
            "--enclosure", "closed-ported", "--tone", str(TONE_FIXTURE)]
    out = tmp_path / "pinned"
    run = subprocess.run(base + ["--speaker", "test-driver", "--port-tube", "101.5", "--fb", "60",
                                 "--out", str(out)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    data = json.loads((out / "voicing.json").read_text())
    assert data["port"]["pinned"] is True and data["port"]["diameter_mm"] == 101.5
    assert data["port"]["fb_override_hz"] == 60.0
    assert data["prediction"]["fb_hz"] == pytest.approx(60.0, abs=1e-6)
    bad = tmp_path / "bad"
    run = subprocess.run(base + ["--speaker", "test-driver", "--port-tube", "100",
                                 "--out", str(bad)], capture_output=True, text=True)
    assert run.returncode == 1 and "port tube must be one of" in run.stderr
    assert not bad.exists()
    run = subprocess.run(base + ["--speaker", "test-driver", "--port-tube", "77.3",
                                 "--port-slot", "352", "40", "--out", str(bad)],
                         capture_output=True, text=True)
    assert run.returncode == 1 and "not both" in run.stderr
    assert not bad.exists()
    two = tmp_path / "two"
    run = subprocess.run(base + ["--speaker", "test-driver", "--speaker", "test-driver",
                                 "--impedance", "16", "--port-count", "1", "--out", str(two)],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    data = json.loads((two / "voicing.json").read_text())
    assert data["port"]["count"] == 1 and data["construction"]["port_count"] == 1
    run = subprocess.run(base + ["--speaker", "test-driver", "--port-count", "3",
                                 "--out", str(tmp_path / "three")], capture_output=True, text=True)
    assert run.returncode == 2 and "invalid choice" in run.stderr      # argparse usage error

def test_cli_evaluate_port_tube_is_a_validated_diameter(speakers_dir, tmp_path):
    base = [sys.executable, str(Path(cabvoice.__file__)), "evaluate",
            "--speakers-dir", str(speakers_dir), "--speaker", "test-driver",
            "--impedance", "16", "--enclosure", "closed-ported", "--tone", str(TONE_FIXTURE),
            "--internal", "472", "421.2", "229.4", "--port-length", "40"]
    out = tmp_path / "out"
    run = subprocess.run(base + ["--port-tube", "101.5", "--port-count", "1", "--out", str(out)],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    data = json.loads((out / "voicing.json").read_text())
    assert data["port"]["diameter_mm"] == 101.5 and data["port"]["pinned"] is True
    assert data["port"]["fb_override_hz"] is None and data["port"]["count"] == 1
    assert "(pinned 101.5 mm tube)" in (out / "voicing.md").read_text()
    for extra, text in ((["--port-tube", "100"], "port tube must be one of"),
                        (["--port-tube", "101.5", "--port-diameter", "101.5"], "not both"),
                        (["--port-tube", "101.5", "--port-slot", "400", "40"], "--port-slot, not both")):
        run = subprocess.run(base + extra + ["--out", str(tmp_path / "bad")],
                             capture_output=True, text=True)
        assert run.returncode == 1 and text in run.stderr
    assert not (tmp_path / "bad").exists()

def test_cli_width_floor_blocker_exits_2_with_the_sheet(speakers_dir, tmp_path):
    out = tmp_path / "out"
    cmd = [sys.executable, str(Path(cabvoice.__file__)), "propose",
           "--speakers-dir", str(speakers_dir), "--speaker", "test-driver", "--speaker", "test-driver",
           "--impedance", "16", "--impedance", "16", "--enclosure", "closed", "--tone", str(TONE_FIXTURE),
           "--max-external", "600", "457.2", "400", "--out", str(out)]
    run = subprocess.run(cmd, capture_output=True, text=True)
    assert run.returncode == 2
    data = json.loads((out / "voicing.json").read_text())
    assert data["blockers"][0].startswith("width floor 730.0 mm internal (the driver-count minimum)")
    assert data["box"]["internal_mm"][0] == pytest.approx(730.0)

def test_cannabis_rex_roots_port_loop_cases(tone):
    # The Plan 2 review's case: under the roots tone the Cannabis Rex solves a 113 mm port that
    # snaps to the 153.2 mm tube; the next tube down clamps at 24 mm and detunes; the slot is clean.
    rex = cabvoice.load_speaker("eminence-cannabis-rex", CATALOG)
    roots = dict(tone, min_power_w=30)
    free = cabvoice.propose([rex], [8], "closed-ported", roots, name="rex")
    assert free.port["diameter_mm"] == 153.2 and free.blockers == []
    assert any(w.startswith("port diameter snapped to the 153.2 mm tube (from 113.2 mm)")
               for w in free.warnings)
    pinned = cabvoice.propose([rex], [8], "closed-ported", roots, name="rex",
                              constraints=cabvoice.Constraints(port_tube_mm=101.5))
    assert pinned.port["length_mm"] == cabvoice.MIN_PORT_LENGTH_MM
    assert any(w.startswith("port clamped at the 24 mm minimum with the pinned 101.5 mm tube: "
                            "tuned 81.0 Hz, target 86.4 Hz") for w in pinned.warnings)
    assert pinned.prediction["fb_hz"] == pytest.approx(81.0, abs=0.05)
    slot = cabvoice.propose([rex], [8], "closed-ported", roots, name="rex",
                            constraints=cabvoice.Constraints(port_slot_mm=(352.0, 40.0)))
    assert slot.port["shape"] == "slot" and slot.blockers == []
    assert not any("clamped" in w or "too short" in w for w in slot.warnings)
    assert slot.prediction["fb_hz"] == pytest.approx(free.prediction["fb_hz"], abs=0.05)

def test_propose_height_floor_blocker_reports_the_final_height_once(drv, tone):
    # A 20 mm slot that must grow under the air-speed rule moves the height floor between
    # settle passes; the sheet reports the final box's floor once, not each pass's.
    drv.xmax_mm = 10.0
    c = cabvoice.Constraints(port_slot_mm=(200.0, 20.0), max_external_mm=(600.0, 400.0, 400.0))
    v = cabvoice.propose([drv], [16], "closed-ported", tone, constraints=c)
    assert v.port["shape"] == "slot" and v.port["slot_h_mm"] > 20.0
    assert v.box["internal_mm"][1] == pytest.approx(466.0, abs=0.1)
    floors = [b for b in v.blockers if b.startswith("height floor")]
    assert floors == [f"height floor {v.box['internal_mm'][1]:.1f} mm internal (the cutout minimum) "
                      "exceeds the size limit 364.0 mm internal"]
```
<!-- /code -->

Two comment lines inside existing tests still state the old minimum; change `# even a 150 mm port needs less than 20 mm and is clamped, so the port tunes lower.` to read `24 mm`, and `# drivers, so it is clamped at 20 mm, tunes low, and moves more air per area` to read `24 mm` (comments only; the tests around them are unchanged).

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q -k "port_tube or pinned or fb_override or floor_over or tube_from_table or min_port_length or port_loop_cases or port_count or too_short"`
Expected: FAIL (`tube_from_table` undefined, `Port` has no `pinned`, `MIN_PORT_LENGTH_MM` still 20).

- [ ] **Step 3: Engine changes**

In `scripts/cabvoice.py` replace each of these with the version below (full text; `tube_from_table` is new and goes directly above `snap_tube_id`; everything else keeps its place).

`MIN_PORT_LENGTH_MM`:

<!-- code: .vault/scripts/cabvoice.py symbols MIN_PORT_LENGTH_MM -->
```python
MIN_PORT_LENGTH_MM = 24.0   # the 12 mm back panel plus the 12 mm flange ring; nothing shorter can be built
```
<!-- /code -->

`Port`:

<!-- code: .vault/scripts/cabvoice.py symbols Port -->
```python
@dataclass
class Port:
    shape: str
    diameter_mm: float | None
    slot_w_mm: float | None
    slot_h_mm: float | None
    area_cm2: float
    length_mm: float
    volume_l: float
    air_speed_ms: float | None = None
    warnings: list = field(default_factory=list)
    pinned: bool = False                  # a purchasable tube pinned by the caller: no growth, no snap
    fb_override_hz: float | None = None   # propose: the caller's tuning in place of the engine's target
```
<!-- /code -->

`port_dims`:

<!-- code: .vault/scripts/cabvoice.py symbols port_dims -->
```python
def port_dims(vb_l: float, fb_hz: float, diameter_mm: float | None = None,
              slot_mm: tuple | None = None) -> Port:
    area = _port_area_m2(diameter_mm, slot_mm)
    length_m = port_length_m(vb_l / 1e3, fb_hz, area)
    warnings = []
    if length_m * 1e3 < MIN_PORT_LENGTH_MM:
        warnings.append(
            f"port too short ({length_m * 1e3:.1f} mm) for Fb {fb_hz:.0f} Hz in {vb_l:.1f} L; "
            f"clamped to {MIN_PORT_LENGTH_MM:.0f} mm; a larger port, a lower Fb, or a smaller box "
            f"lengthens it")
        length_m = MIN_PORT_LENGTH_MM / 1e3
    return Port(
        shape="round" if diameter_mm is not None else "slot",
        diameter_mm=diameter_mm,
        slot_w_mm=None if slot_mm is None else slot_mm[0],
        slot_h_mm=None if slot_mm is None else slot_mm[1],
        area_cm2=area * 1e4,
        length_mm=length_m * 1e3,
        volume_l=area * length_m * 1e3,
        warnings=warnings,
    )
```
<!-- /code -->

`tube_from_table` (new, directly above `snap_tube_id`) and `size_port`:

<!-- code: .vault/scripts/cabvoice.py symbols tube_from_table,size_port -->
```python
def tube_from_table(diameter_mm: float) -> float:
    """The PORT_TUBE_ID_MM entry equal to diameter_mm (float noise tolerated), else ValueError."""
    for tube in PORT_TUBE_ID_MM:
        if abs(diameter_mm - tube) < 1e-6:
            return tube
    raise ValueError(f"port tube must be one of {', '.join(f'{t:g}' for t in PORT_TUBE_ID_MM)} mm, "
                     f"not {diameter_mm:g}")

def size_port(driver: Driver, vb_l: float, fb_hz: float,
              diameter_mm: float = DEFAULT_PORT_DIAMETER_MM,
              slot_mm: tuple | None = None, pinned_mm: float | None = None) -> Port:
    """Port for (vb, fb), enlarged in 10 percent area steps until the
    worst-case air speed is under PORT_V_MAX and the physical length is at
    least MIN_PORT_LENGTH_MM. A round start above MAX_PORT_DIAMETER_MM is
    clamped to it first. Stops at the MAX_PORT_DIAMETER_MM equivalent area
    and leaves the warnings in place for the caller. A round port is then
    snapped up to the next purchasable tube (PORT_TUBE_ID_MM) and re-solved,
    so the sheet describes a tube that can be bought. A pinned tube
    (pinned_mm, one of PORT_TUBE_ID_MM) is built once at that size instead:
    no growth, no snap; a clamped length keeps its warning and the caller
    reports the air speed against the limit."""
    max_area_cm2 = math.pi * (MAX_PORT_DIAMETER_MM / 20.0) ** 2
    if not slot_mm:
        diameter_mm = min(diameter_mm, MAX_PORT_DIAMETER_MM)

    def build(dia, slot):
        p = port_dims(vb_l, fb_hz, diameter_mm=None if slot else dia, slot_mm=slot)
        p.air_speed_ms = port_air_speed(driver, fb_hz, p.area_cm2)
        return p

    if pinned_mm is not None:
        if slot_mm:
            raise ValueError("give a slot or a pinned tube, not both")
        port = build(tube_from_table(pinned_mm), None)
        port.pinned = True
        return port
    port = build(diameter_mm, slot_mm)
    for _ in range(60):
        too_fast = port.air_speed_ms > PORT_V_MAX
        too_short = any("too short" in w for w in port.warnings)
        if not (too_fast or too_short) or port.area_cm2 >= max_area_cm2 - 1e-9:
            break
        if slot_mm:
            slot_mm = (slot_mm[0], min(slot_mm[1] * 1.1, max_area_cm2 * 100.0 / slot_mm[0]))
        else:
            diameter_mm = min(diameter_mm * math.sqrt(1.1), MAX_PORT_DIAMETER_MM)
        port = build(diameter_mm, slot_mm)
    if not slot_mm:
        solved = port.diameter_mm
        tube = snap_tube_id(solved)
        port = build(tube, None)
        if abs(tube - solved) > 0.05:
            port.warnings.append(f"port diameter snapped to the {tube:g} mm tube "
                                 f"(from {solved:.1f} mm)")
    if port.air_speed_ms > PORT_V_MAX:
        port.warnings.append(f"port air speed {port.air_speed_ms:.1f} m/s still above "
                             f"{PORT_V_MAX} m/s at the maximum port size")
    return port
```
<!-- /code -->

`dims_for_volume`:

<!-- code: .vault/scripts/cabvoice.py symbols dims_for_volume -->
```python
def dims_for_volume(gross_l: float, pinned_external_width_mm: float | None = None,
                    min_internal_width_mm: float | None = None,
                    max_external_mm: tuple | None = None,
                    min_internal_height_mm: float | None = None, strict: bool = True,
                    pinned_external_height_mm: float | None = None,
                    **panel_kwargs) -> Box:
    """Internal dimensions for a gross volume, starting from the site box
    proportions. Fixed axes come from a pinned width, a pinned height, the
    driver minimum width, the minimum height, or external limits; free axes
    scale together to hit the volume (pinning both width and height leaves
    depth as the sole free axis, solved for the target volume). When the
    limits cannot hold the volume, strict raises; otherwise the largest box
    that fits comes back with a "cannot reach" warning."""
    if gross_l <= 0:
        raise ValueError("gross_l must be positive")
    target = gross_l * 1e6
    base = list(site_default_box(**panel_kwargs).internal_mm)
    scale = (target / (base[0] * base[1] * base[2])) ** (1.0 / 3.0)
    dims = [x * scale for x in base]
    fixed = [False, False, False]
    conflicts = []
    if pinned_external_width_mm is not None:
        dims[0] = internal_from_external((pinned_external_width_mm, 0, 0), **panel_kwargs)[0]
        fixed[0] = True
    if min_internal_width_mm is not None and dims[0] < min_internal_width_mm:
        if fixed[0]:
            conflicts.append(
                f"pinned width {pinned_external_width_mm:g} mm external is below the "
                f"{min_internal_width_mm:g} mm internal minimum for the driver count; using the minimum")
        dims[0] = min_internal_width_mm
        fixed[0] = True
    if pinned_external_height_mm is not None:
        dims[1] = internal_from_external((0, pinned_external_height_mm, 0), **panel_kwargs)[1]
        fixed[1] = True
    if min_internal_height_mm is not None and dims[1] < min_internal_height_mm:
        if fixed[1]:
            conflicts.append(
                f"pinned height {pinned_external_height_mm:g} mm external is below the "
                f"{min_internal_height_mm:g} mm internal minimum for the port or cutout; using the minimum")
        dims[1] = min_internal_height_mm
        fixed[1] = True
    max_internal = None
    if max_external_mm is not None:
        max_internal = internal_from_external(max_external_mm, **panel_kwargs)
        # A floor over the limit: strict raises; otherwise the floor holds, the axis is
        # fixed over the limit, and the message comes back as a "width floor" or
        # "height floor" warning for the caller to present as a blocker.
        over = []
        if fixed[0] and dims[0] > max_internal[0] + 1e-9:
            cause = ("the driver-count minimum"
                     if min_internal_width_mm is not None and dims[0] == min_internal_width_mm
                     else f"pinned width {pinned_external_width_mm:g} mm external")
            over.append(f"width floor {dims[0]:.1f} mm internal ({cause}) exceeds the size limit "
                        f"{max_internal[0]:.1f} mm internal")
        elif min_internal_width_mm is not None and min_internal_width_mm > max_internal[0] + 1e-9:
            over.append(f"width floor {min_internal_width_mm:.1f} mm internal (the driver-count "
                        f"minimum) exceeds the size limit {max_internal[0]:.1f} mm internal")
            dims[0] = min_internal_width_mm
            fixed[0] = True
        if fixed[1] and dims[1] > max_internal[1] + 1e-9:
            cause = ("the cutout minimum"
                     if min_internal_height_mm is not None and dims[1] == min_internal_height_mm
                     else f"pinned height {pinned_external_height_mm:g} mm external")
            over.append(f"height floor {dims[1]:.1f} mm internal ({cause}) exceeds the size limit "
                        f"{max_internal[1]:.1f} mm internal")
        elif min_internal_height_mm is not None and min_internal_height_mm > max_internal[1] + 1e-9:
            over.append(f"height floor {min_internal_height_mm:.1f} mm internal (the cutout minimum) "
                        f"exceeds the size limit {max_internal[1]:.1f} mm internal")
            dims[1] = min_internal_height_mm
            fixed[1] = True
        if over and strict:
            raise ValueError("; ".join(over))
        conflicts.extend(over)

    def rescale():
        free = [i for i in range(3) if not fixed[i]]
        if not free:
            return
        fixed_prod = 1.0
        for i in range(3):
            if fixed[i]:
                fixed_prod *= dims[i]
        free_prod = 1.0
        for i in free:
            free_prod *= dims[i]
        k = (target / fixed_prod / free_prod) ** (1.0 / len(free))
        for i in free:
            dims[i] *= k

    def apply_floors() -> bool:
        """Lift any free axis that fell under its floor; True when one moved."""
        moved = False
        for i, floor in ((0, min_internal_width_mm), (1, min_internal_height_mm)):
            if floor is not None and not fixed[i] and dims[i] < floor - 1e-9:
                dims[i] = floor
                fixed[i] = True
                moved = True
        return moved

    for _ in range(3):   # a floor on one axis shrinks the others on rescale; settle both
        rescale()
        if not apply_floors():
            break
    for _ in range(3):
        if max_internal is None:
            break
        changed = False
        for i in range(3):
            if not fixed[i] and dims[i] > max_internal[i]:
                dims[i] = max_internal[i]
                fixed[i] = True
                changed = True
        if not changed:
            break
        rescale()
    achieved = dims[0] * dims[1] * dims[2]
    if abs(achieved - target) / target > 0.001:
        message = (f"cannot reach {gross_l:.1f} L within the internal size limit; "
                   f"achievable {achieved / 1e6:.1f} L")
        if strict:
            raise ValueError(message)
        conflicts.append(message)
    box = make_box(tuple(dims), **panel_kwargs)
    box.warnings = conflicts + box.warnings
    return box
```
<!-- /code -->

`Constraints`:

<!-- code: .vault/scripts/cabvoice.py symbols Constraints -->
```python
@dataclass
class Constraints:
    pinned_external_width_mm: float | None = None
    pinned_external_height_mm: float | None = None
    max_external_mm: tuple | None = None
    panel_mm: float = PANEL_MM
    back_mm: float = BACK_MM
    baffle_mm: float = BAFFLE_MM
    recess_mm: float = RECESS_MM
    brace_l: float = 0.0               # extra bracing beyond the modeled mono 2x12 center brace
    port_diameter_mm: float = DEFAULT_PORT_DIAMETER_MM
    port_slot_mm: tuple | None = None
    port_count: int | None = None      # None: one port per driver in the chamber
    port_tube_mm: float | None = None  # pin one tube of PORT_TUBE_ID_MM: no growth, no snap
    fb_hz: float | None = None         # propose: tuning override in place of the engine's target
    line: str = "tolex"
    species: str | None = None
    accept_low_headroom: bool = False
    accept_impedance_mismatch: bool = False   # no tap matches: warn instead of block

    def __post_init__(self):
        if self.line not in LINES:
            raise ValueError(f"line must be one of {', '.join(LINES)}")
        if self.species is not None:
            self.species = self.species.strip() or None
        if self.port_tube_mm is not None:
            self.port_tube_mm = tube_from_table(self.port_tube_mm)
        if self.fb_hz is not None and self.fb_hz <= 0:
            raise ValueError("fb_hz must be positive")

    def panel_kwargs(self) -> dict:
        return dict(panel_mm=self.panel_mm, back_mm=self.back_mm,
                    baffle_mm=self.baffle_mm, recess_mm=self.recess_mm)
```
<!-- /code -->

`propose`:

<!-- code: .vault/scripts/cabvoice.py symbols propose -->
```python
def propose(drivers: list, impedances: list, enclosure: str, tone: dict,
            jack_config: str = "mono", constraints: Constraints | None = None,
            name: str = "cab") -> Voicing:
    c = constraints or Constraints()
    lead, count, chambers, per_chamber_drivers, warnings = _setup(
        drivers, impedances, enclosure, tone, jack_config)
    blockers = []
    low_end = tone["low_end"]
    per_driver_net, method, w = per_driver_net_l(lead, enclosure, low_end)
    warnings.extend(w)
    fb = None
    if enclosure == "closed-ported":
        per_driver_net, fb, _, w = ported_targets(lead, per_driver_net, low_end)
        warnings.extend(w)
        if c.fb_hz is not None:
            fb = c.fb_hz   # the caller's tuning; the box volume stays the alignment's
    chamber_net = per_driver_net * per_chamber_drivers
    net_total = chamber_net * chambers
    displacement = _displacement(drivers, warnings)
    cutout = max(d.cutout_mm for d in drivers)
    floor_extra = HARDWOOD_FLOOR_EXTRA_MM if c.line == "hardwood" else 0.0
    min_w = min_internal_width_mm(count, cutout) + floor_extra
    pk = c.panel_kwargs()
    port_count = c.port_count or per_chamber_drivers
    net_target = net_total
    port, port_l, divider_l, inside_l, box, limited = None, 0.0, 0.0, 0.0, None, False
    last = None   # (gross, parts) of the previous pass
    for _ in range(10):   # until the box and its parts settle: port, divider, and inside parts
                          # depend on the box, and the net follows them when the size limit wins
        gross = net_total + displacement + c.brace_l + port_l * chambers + divider_l + inside_l
        slot_h = None
        if enclosure == "closed-ported" and c.port_slot_mm:
            slot_h = port.slot_h_mm if port is not None else c.port_slot_mm[1]
        box = dims_for_volume(gross, c.pinned_external_width_mm, min_w, c.max_external_mm,
                              min_internal_height_mm=min_internal_height_mm(cutout, slot_h) + floor_extra,
                              strict=False, pinned_external_height_mm=c.pinned_external_height_mm, **pk)
        w_int, h_int, d_int = box.internal_mm
        divider_l = _divider_l(chambers, h_int, d_int, c)
        if any(w.startswith("cannot reach") for w in box.warnings):
            # The size limit wins: voice the box that fits and present the trade-off.
            limited = True
        # A floor over the size limit is a blocker on the sheet, not an exception: the box
        # is voiced at the floor and the skill presents the trade-off. Each pass overwrites
        # the list: the height floor follows a slot port that grows, so the sheet reports
        # the final box's floors only, once, after the loop.
        floor_blockers = [w for w in box.warnings if w.startswith(("width floor", "height floor"))]
        box.warnings = [w for w in box.warnings
                        if not w.startswith(("cannot reach", "width floor", "height floor"))]
        if abs(box.gross_l - gross) > 0.001:
            # The net is what the box holds when the limit pins it under the request
            # (dims_for_volume passes a shortfall under 0.1 percent without the warning).
            net_total = (box.gross_l - displacement - c.brace_l - port_l * chambers - divider_l
                         - inside_l)
            chamber_net = net_total / chambers
            per_driver_net = chamber_net / per_chamber_drivers
        if enclosure == "closed-ported":
            port = size_port(_air_speed_driver(lead, per_chamber_drivers / port_count, warnings),
                             chamber_net / port_count, fb, diameter_mm=c.port_diameter_mm,
                             slot_mm=c.port_slot_mm, pinned_mm=c.port_tube_mm)
            port.fb_override_hz = c.fb_hz
            port_l = _port_inside_l(port) * port_count
        inside_l = inside_parts_l(box.internal_mm, enclosure, count, chambers, jack_config, port,
                                  c.line, port_count, panel_mm=c.panel_mm)
        parts = port_l * chambers + divider_l + inside_l
        floor_held = slot_h is None or abs(port.slot_h_mm - slot_h) < 1e-9
        if (last is not None and floor_held and abs(box.gross_l - last[0]) < 0.001
                and abs(parts - last[1]) < 0.001):
            break
        last = (box.gross_l, parts)
    warnings.extend(box.warnings)
    blockers.extend(floor_blockers)
    chamber_w = _chamber_w(chambers, w_int, c)
    port_dict = None
    if port is not None:
        fb_actual, port_dict = _port_report(lead, per_chamber_drivers, chamber_net, port,
                                            port_count, warnings)
        if abs(fb_actual - fb) > 0.5 and port.pinned:
            warnings.append(f"port clamped at the {MIN_PORT_LENGTH_MM:.0f} mm minimum with the pinned "
                            f"{port.diameter_mm:g} mm tube: tuned {fb_actual:.1f} Hz, target "
                            f"{fb:.1f} Hz; a larger tube, a lower Fb, or a smaller box lengthens it")
        elif abs(fb_actual - fb) > 0.5:
            warnings.append(f"port clamped at the size cap: tuned {fb_actual:.1f} Hz, target "
                            f"{fb:.1f} Hz; lower Fb or use a smaller box")
        fb = fb_actual   # the prediction follows the port as built
    prediction = _predict(lead, enclosure, per_driver_net, fb, chamber_w, h_int, d_int)
    if limited:
        target_gross = (net_target + displacement + c.brace_l + port_l * chambers + divider_l
                        + inside_l)
        blockers.append(f"target {target_gross:.1f} L cannot fit the size limit; achievable "
                        f"{box.gross_l:.1f} L gives {_prediction_summary(prediction)}")
    wiring_dict, power_dict = _electrical(drivers, impedances, tone, jack_config, c,
                                          warnings, blockers)
    volumes = _volumes(method, per_driver_net, per_chamber_drivers, chambers, displacement,
                       c.brace_l, port_l * chambers, divider_l, inside_l, box.gross_l)
    return _assemble(name, "propose", tone, drivers, impedances, enclosure, jack_config, chambers,
                     count, volumes, box, chamber_w, port_dict, prediction, wiring_dict,
                     power_dict, warnings, blockers, c)
```
<!-- /code -->

`render_markdown`:

<!-- code: .vault/scripts/cabvoice.py symbols render_markdown -->
```python
def render_markdown(v: Voicing) -> str:
    import datetime as _dt
    slug = v.name.lower().replace(" ", "-")
    lines = [
        "---",
        f"name: {slug}-voicing",
        "type: voicing-sheet",
        f"project: {v.name}",
        f"created: {_dt.date.today().isoformat()}",
        "status: unverified-prediction",
        "tags: [speaker-cab, voicing]",
        "---",
        "",
        f"# Voicing sheet: {v.name}",
        "",
        f"Mode: {v.mode}. Every number here is a prediction: {v.prediction_status}.",
        "",
        "## Summary",
        "",
    ]
    spk = ", ".join(f"{s['brand']} {s['model']} {s['impedance_ohm']:g} ohm ({s['data_status']})"
                    for s in v.speakers)
    e = v.enclosure
    lines += [f"- Drivers: {e['driver_count']} x {spk}"]
    lines += [f"- {s['brand']} {s['model']}: cutout {s['cutout_mm']:.0f} mm, {s['bolt_count']} bolts "
              f"on {s['bolt_circle_mm']:.1f} mm, depth {s['depth_mm']:.0f} mm, {s['weight_kg']:.1f} kg"
              for s in v.speakers]
    lines += [
        f"- Enclosure: {e['type']}, {e['chambers']} chamber(s), jack configuration {e['jack_config']}",
        f"- Character: {v.prediction.get('character')}",
        f"- Volume method: {v.volumes['method']}",
        "",
        "## Tone target",
        "",
    ]
    lines += [f"- {k}: {val}" for k, val in v.tone_target.items()]
    vol = v.volumes
    lines += [
        "",
        "## Volumes",
        "",
        "| Quantity | Value |",
        "|---|---|",
        f"| Net per driver | {_liters(vol['per_driver_net_l'])} |",
        f"| Net per chamber | {_liters(vol['per_chamber_net_l'])} |",
        f"| Net total | {_liters(vol['net_total_l'])} |",
        f"| Driver displacement | {vol['displacement_l']:.2f} L |",
        f"| Brace | {vol['brace_l']:.2f} L |",
        f"| Port air inside the box | {vol['port_l']:.2f} L |",
        f"| Divider | {vol['divider_l']:.2f} L |",
        f"| Inside parts (cleats, stiffeners, shelf, ring) | {vol['inside_parts_l']:.2f} L |",
        f"| Gross internal | {_liters(vol['gross_l'])} |",
        "",
        "## Dimensions",
        "",
        f"- Internal: {_fmt_dims(v.box['internal_mm'], v.box['internal_in'])}",
        f"- External: {_fmt_dims(v.box['external_mm'], v.box['external_in'])}",
        f"- Chamber internal width: {v.box['chamber_internal_width_mm']:.0f} mm",
        f"- Construction: {v.construction['line']} line, walls {v.construction['wall_material']}; "
        f"voiced with {v.construction['panel_mm']:g} mm walls",
    ]
    if v.prediction.get("panel_height_mm") is not None:
        lines.append(f"- Open-back panels: two, top and bottom, each "
                     f"{v.prediction['panel_height_mm']:.0f} mm tall")
    lines += ["", "## Port", ""]
    if v.port is None:
        lines.append("No port (closed or open back).")
    else:
        p = v.port
        size = (f"round {p['diameter_mm']:g} mm" if p['shape'] == "round"
                else f"slot {p['slot_w_mm']:.0f} x {p['slot_h_mm']:.0f} mm")
        if p.get("pinned"):
            size += f" (pinned {p['diameter_mm']:g} mm tube)"
        lines += [
            f"- {size}, area {p['area_cm2']:.0f} cm2, length {p['length_mm']:.0f} mm, "
            f"{p['location']}, {p['count']} per chamber",
            f"- Worst-case air speed {p['air_speed_ms']:.1f} m/s (limit {PORT_V_MAX:.0f} m/s)",
        ]
        if p.get("fb_override_hz") is not None:
            lines.append(f"- Fb override: {p['fb_override_hz']:.1f} Hz in place of the engine's target")
    pr = v.prediction
    lines += ["", "## Prediction", "", f"- Model: {pr['model']}", f"- Character: {pr['character']}"]
    for key, label in (("qtc", "Qtc"), ("fc_hz", "Fc"), ("fb_hz", "Fb"), ("f3_hz", "F3"),
                       ("peak_db", "Peak"), ("f_cancel_hz", "Cancellation frequency"),
                       ("panel_height_mm", "Open-back panel height")):
        if pr.get(key) is not None:
            unit = {"qtc": "", "peak_db": " dB", "panel_height_mm": " mm"}.get(key, " Hz")
            lines.append(f"- {label}: {pr[key]:.2f}{unit}")
    table = pr.get("response_db") or pr.get("response_relative_db")
    if table:
        title = "relative to closed" if "response_relative_db" in pr else "relative to passband"
        lines += ["", f"| Hz | dB ({title}) |", "|---|---|"]
        lines += [f"| {f:.0f} | {db:+.1f} |" for f, db in table if f >= 50.0]
    lines += ["", "## Wiring", ""]
    rec = v.wiring["recommended"]
    none_text = "none matches the amp taps" + (" (mismatch accepted)"
                                               if v.wiring.get("mismatch_accepted") else "")
    lines.append("- Recommended: " + (f"{rec['name']}, {rec['impedance_ohm']:g} ohm. {rec['jack_text']}"
                                       if rec else none_text))
    for o in v.wiring["options"]:
        lines.append(f"- Option {o['name']}: {o['impedance_ohm']:g} ohm, "
                     f"{'matches' if o['matches_tap'] else 'no'} tap")
    pw = v.power
    lines += ["", "## Power", "",
              f"- Amp {pw['amp_power_w']:g} W, handling {pw['total_handling_w']:g} W, "
              f"target {pw['min_power_w']:g} W: {pw['status']}. {pw['message']}"]
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in v.warnings] or ["- none"]
    lines += ["", "## Blockers", ""]
    lines += [f"- {b}" for b in v.blockers] or ["- none"]
    lines += ["", f"Prediction status: {v.prediction_status}.", ""]
    return "\n".join(lines)
```
<!-- /code -->

`_build_parser` and `main`:

<!-- code: .vault/scripts/cabvoice.py symbols _build_parser,main -->
```python
def _build_parser():
    import argparse
    ap = argparse.ArgumentParser(description="Guitar speaker cabinet voicing engine")
    sub = ap.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--speakers-dir", default=str(SPEAKERS_DIR))
        p.add_argument("--speaker", action="append", required=True, help="slug, repeat for two drivers")
        p.add_argument("--impedance", action="append", type=float, required=True)
        p.add_argument("--enclosure", choices=ENCLOSURE_TYPES, required=True)
        p.add_argument("--tone", required=True, help="tone target JSON file")
        p.add_argument("--jack", choices=JACK_CONFIGS, default="mono")
        p.add_argument("--brace-l", type=float, default=0.0,
                       help="liters of extra bracing beyond the modeled mono 2x12 center brace, "
                            "which the inside parts already carry")
        p.add_argument("--port-count", type=int, choices=(1, 2), default=None,
                       help="ports per chamber (default one per driver in the chamber)")
        p.add_argument("--line", choices=LINES, default="tolex")
        p.add_argument("--species", default=None)
        p.add_argument("--accept-low-headroom", action="store_true")
        p.add_argument("--accept-impedance-mismatch", action="store_true",
                       help="warn instead of block when no wiring option matches the amp's taps")
        p.add_argument("--name", default="cab")
        p.add_argument("--out", required=True, help="directory for voicing.json and voicing.md")

    pp = sub.add_parser("propose")
    common(pp)
    pp.add_argument("--pinned-width", type=float, help="external width mm")
    pp.add_argument("--pinned-height", type=float, help="external height mm")
    pp.add_argument("--max-external", type=float, nargs=3, metavar=("W", "H", "D"))
    pp.add_argument("--port-diameter", type=float, default=DEFAULT_PORT_DIAMETER_MM,
                    help="round port start in mm, snapped up to the tube table")
    pp.add_argument("--port-slot", type=float, nargs=2, metavar=("W", "H"))
    pp.add_argument("--port-tube", type=float, default=None, metavar="MM",
                    help="pin one purchasable tube inside diameter (52, 77.3, 101.5, or 153.2 mm): "
                         "no growth, no snap; a clamped length or a high air speed becomes a warning")
    pp.add_argument("--fb", type=float, default=None, metavar="HZ",
                    help="tuning override in Hz in place of the engine's target (recorded on the sheet)")

    pe = sub.add_parser("evaluate")
    common(pe)
    pe.add_argument("--internal", type=float, nargs=3, required=True, metavar=("W", "H", "D"))
    pe.add_argument("--port-diameter", type=float)
    pe.add_argument("--port-slot", type=float, nargs=2, metavar=("W", "H"))
    pe.add_argument("--port-length", type=float)
    pe.add_argument("--port-tube", type=float, default=None, metavar="MM",
                    help="the port's tube inside diameter from the table (52, 77.3, 101.5, or 153.2 mm), "
                         "a validated --port-diameter")

    pl = sub.add_parser("list")
    pl.add_argument("--speakers-dir", default=str(SPEAKERS_DIR))
    return ap

def main(argv=None) -> int:
    import sys
    args = _build_parser().parse_args(argv)
    if args.command == "list":
        print("\n".join(list_speakers(Path(args.speakers_dir))))
        return 0
    try:
        drivers = [load_speaker(s, Path(args.speakers_dir)) for s in args.speaker]
        tone = json.loads(Path(args.tone).read_text())
        c = Constraints(brace_l=args.brace_l, accept_low_headroom=args.accept_low_headroom,
                        accept_impedance_mismatch=args.accept_impedance_mismatch,
                        line=args.line, species=args.species, port_count=args.port_count,
                        port_tube_mm=args.port_tube, fb_hz=getattr(args, "fb", None))
        if args.command == "propose":
            c.pinned_external_width_mm = args.pinned_width
            c.pinned_external_height_mm = args.pinned_height
            c.max_external_mm = tuple(args.max_external) if args.max_external else None
            c.port_diameter_mm = args.port_diameter
            c.port_slot_mm = tuple(args.port_slot) if args.port_slot else None
            v = propose(drivers, args.impedance, args.enclosure, tone, args.jack, c, args.name)
        else:
            port = None
            if args.enclosure == "closed-ported":
                diameter = args.port_diameter
                if args.port_tube is not None:
                    if diameter is not None:
                        raise ValueError("give --port-tube or --port-diameter, not both")
                    diameter = c.port_tube_mm
                if args.port_tube is not None and args.port_slot:
                    raise ValueError("give --port-tube or --port-slot, not both")
                if args.port_length is None or (diameter is None and args.port_slot is None):
                    raise ValueError("evaluate closed-ported needs --port-length and --port-tube, "
                                     "--port-diameter, or --port-slot")
                port = port_dims(1.0, 1.0, diameter_mm=diameter,
                                 slot_mm=tuple(args.port_slot) if args.port_slot else None)
                port.length_mm = args.port_length
                port.warnings = []
                port.pinned = args.port_tube is not None
            v = evaluate(drivers, args.impedance, args.enclosure, tone, tuple(args.internal),
                         args.jack, port, c, args.name)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    json_path, md_path = write_voicing(v, Path(args.out))
    print(f"wrote {json_path} and {md_path}")
    if v.blockers:
        print("blocked: " + "; ".join(v.blockers), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
<!-- /code -->

- [ ] **Step 4: Run the tests (the calibration test still fails)**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q`
Expected: 431 passed, 1 failed (`test_calibration_table_matches_engine`: the note still holds the 20 mm row).

- [ ] **Step 5: Regenerate the calibration table**

Run from the vault root: `.venv/bin/python projects/Speaker-cab-system/pipeline/calibration_table.py`
Expected: `wrote 20 rows to .../knowledge/speaker-cab-voicing.md`. Only two lines of the note change: the block's first line now says `Generated 2026-09-11` (the run date), and the Eminence Red White and Blues row moves from Fb 74 to 73 Hz with its notes reading `port too short (6.5 mm) for Fb 78 Hz in 66.0 L; clamped to 24 mm; a larger port, a lower Fb, or a smaller box lengthens it; port clamped at the size cap: tuned 73.5 Hz, target 78.0 Hz; lower Fb or use a smaller box`. Every other row is unchanged (`git diff knowledge/speaker-cab-voicing.md` shows exactly those two lines).

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q`
Expected: 432 passed (397 from Plan 2 plus 15 functions plus 20 matrix cases).

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cabvoice.py scripts/test_cabvoice.py knowledge/speaker-cab-voicing.md
git commit -m "Speaker cab plan 3 task 1: port tube pin, Fb override, port count, 24 mm minimum, size-limit blockers"
```

---

### Task 2: Layout: port mouth check, port fit naming the tube that fits, aesthetics block, fixture list

**Files:**
- Modify: `scripts/cablayout.py` (new `SLOT_TRIM_MM` after `GRILL_FRONT_MM`; new `largest_tube_at_minimum` above `round_ports`; `round_ports` and `slot_ports` replaced; new `_mouth_rect_overlaps`, `MOUTH_GRID`, `_mouth_coverage`, `_box_inside`, `_circle_inside`, `port_mouth_clearances` above `check_layout`; `check_layout` and `layout_report` replaced)
- Modify: `scripts/test_cablayout.py` (`CHECK_NAMES` and `test_matrix_every_configuration_lays_out_or_names_its_blocker` replaced; ten new tests appended)
- Modify: `scripts/test_cabmodel.py` (`CHECK_LINES` and `test_cab_py_finds_the_vault_from_an_order_directory` replaced; the `# === TASK 12 ===` unit replaced through the end of the file)
- Modify: `projects/Speaker-cab-system/fixtures/site-default/cab.json`, `cutlist.md`, `cutlist.csv`, `images/*.png` (regenerated)
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/scripts/cablayout.py`, `.vault/scripts/test_cablayout.py`, `.vault/scripts/test_cabmodel.py`, `.vault/projects/Speaker-cab-system/fixtures/site-default/`

**Interfaces:**
- Consumes: Task 1's engine (`PORT_TUBE_ID_MM`, `MIN_PORT_LENGTH_MM` 24, sheets with `port.pinned` and `port.fb_override_hz`, which the layout ignores); the Plan 2 layout (`_place_tube`, `round_ports`, `slot_ports`, `check_layout`, `layout_report`, the `Aesthetics` dataclass) and CAD tests (`CHECK_LINES`, the Task 12 fixture test).
- Produces: `SLOT_TRIM_MM = 1.0` (a slot up to that much wider than its chamber is trimmed to the chamber, not blocked, so a slot re-run converges); `largest_tube_at_minimum(env, sign, fr, obstacles, envelopes, tubes, below_id_mm) -> float | None`; `port_mouth_clearances(lay) -> list[tuple]` of `(chamber, index, free_mm, obstruction, coverage, effective_diameter_mm)`; the `port mouth` check between `port fit` and `magnet to back` (19 checks in the order given in Global Constraints); `port fit` blocker texts that name the largest table tube that fits at the 24 mm minimum or the deepest shelf that fits; `cab.json["aesthetics"]` (`asdict(Aesthetics)`, 21 keys, tuples as lists); in `test_cabmodel.py` the list `FIXTURE_ORDERS`, `DELIVERABLES`, `_fixture_dir(name)`, `_run_fixture(name, out) -> (proc, report)`, and `test_fixture_order_runs_clean_with_every_deliverable` parametrized over the list. Tasks 7 and 8 append their fixture names to `FIXTURE_ORDERS`; Task 5 reads the aesthetics block and the 19 verdicts; Task 6 quotes the messages.

The `port mouth` rule as built: the free air along the port axis from the inner mouth to the first solid whose projection overlaps the mouth's cross-section, among the chamber's parts plus the divider and the basket and magnet envelope steps, else the baffle's back face (rear round port) or the back panel's inner face (front slot). Effective diameter: the tube inside diameter, or the diameter of a circle with the slot's area. Warn under one diameter, never a blocker; the coverage fraction (a 24 x 24 grid sample of the mouth) is reported for information and does not gate the warn. Messages: `no port`; `no port placed (see port fit)`; pass `port mouth(s) clear: chamber 0 port 0: mouth 84 mm from the speaker 0 magnet (29 percent of the mouth), one diameter is 77.3 mm` (entries joined by `; `; the terminal faces `baffle` and `back panel` carry no coverage); warn `chamber 0 port 0: mouth 84 mm from the speaker 0 magnet (18 percent of the mouth), under one diameter (101.5 mm)`. Obstruction names are blank names with spaces (`stiffener bottom`, `cleat back bottom`, `cleat back bottom 0` in a stereo chamber), `speaker N magnet` or `speaker N basket`, `baffle`, `back panel`. Three consequences the reviewer should expect: the site default now warns (its 101.5 mm tube's mouth sits 84.4 mm behind the magnet with 18 percent of the mouth facing it), a 1x12 front slot warns on the bottom stiffener at 0 mm because Plan 2 starts that stiffener at the shelf's rear edge (about 8 percent coverage), and slots in shallow boxes warn on the floor-level back cleat. All three are the rule as approved; Task 4 records them in the construction note.

`port fit` texts: `chamber 0 port 0: no round port of 153.2 mm fits with 25 mm clearance; the longest table tube that fits at the 24 mm minimum is 101.5 mm; raise Fb, use a smaller tube or a larger box, or a front slot`; `chamber 0 port 0: no round port of 101.5 mm fits with 25 mm clearance; no table tube fits; use a front slot or a larger box`; the shorter-length form is unchanged (`tube 77.3 x 250 mm reaches the baffle; longest tube that fits at this diameter is 155 mm; ...`), and the same-diameter length probe now ends at exactly 24 mm; slots: `slot shelf 220 mm deep leaves 27 mm behind it, under the 40 mm the slot needs to breathe; the deepest shelf that fits is 207 mm; lower the slot height or use a round port` and `...; no shelf fits; lower the slot height or use a round port`.

- [ ] **Step 1: Write the failing tests**

In `scripts/test_cablayout.py` replace these two:

<!-- code: .vault/scripts/test_cablayout.py symbols CHECK_NAMES,test_matrix_every_configuration_lays_out_or_names_its_blocker -->
```python
CHECK_NAMES = ["sheet", "net volume", "stereo balance", "cutout", "grill opening", "port fit",
               "port mouth", "magnet to back", "handle", "head match", "line", "jack plate", "stock",
               "part count", "spans"]

def test_matrix_every_configuration_lays_out_or_names_its_blocker():
    t0 = time.time()
    slugs = cabvoice.list_speakers()
    assert len(slugs) == 20
    stats = {"cases": 0, "engine_blocked": 0, "clean": 0, "blocked": 0, "port_mouth_warn": 0}
    reasons = {}
    worst = (0.0, None)
    for slug in slugs:
        drv = cabvoice.load_speaker(slug)
        z = drv.impedance_ohm[0]
        for enclosure, slot in ENCLOSURES:
            for n, jack in CONFIGS:
                for line, species, joint in LINES:
                    stats["cases"] += 1
                    c = cabvoice.Constraints(line=line, species=species, port_slot_mm=slot)
                    v = cabvoice.propose([drv] * n, [z] * n, enclosure, TONE, jack, c, "matrix").to_dict()
                    aest = L.Aesthetics(corner_joint=joint)
                    if v["blockers"]:
                        stats["engine_blocked"] += 1
                        with pytest.raises(ValueError):
                            L.order_from(v, aest)
                        continue
                    # the engine must hold its own floors (hardwood floors carry the 2 mm extra)
                    w_int, h_int, _ = v["box"]["internal_mm"]
                    cut = max(s["cutout_mm"] for s in v["speakers"])
                    slot_h = v["port"]["slot_h_mm"] if (v["port"] and v["port"]["shape"] == "slot") else None
                    extra = cabvoice.HARDWOOD_FLOOR_EXTRA_MM if line == "hardwood" else 0.0
                    assert w_int >= cabvoice.min_internal_width_mm(n, cut) + extra - 1e-6, (slug, enclosure, n, jack, line)
                    assert h_int >= cabvoice.min_internal_height_mm(cut, slot_h) + extra - 1e-6, (slug, enclosure, n, jack, line)
                    spec = L.order_from(v, aest)
                    assert spec.sheet_inside_parts_l is not None
                    lay = L.layout(spec)
                    checks = L.check_layout(lay, spec)
                    blockers = [ch for ch in checks if ch.level == "blocker"]
                    by = {ch.name: ch for ch in checks}
                    if by["port mouth"].level == "warn":
                        stats["port_mouth_warn"] += 1
                    # the engine's floors and the layout's margins agree everywhere, both lines
                    assert by["cutout"].level == "pass", (slug, enclosure, n, jack, line, by["cutout"].message)
                    assert by["grill opening"].level == "pass", (slug, enclosure, n, jack, line)
                    assert by["stereo balance"].level == "pass", (slug, enclosure, n, jack, line)
                    assert by["line"].level == "pass"
                    if blockers:
                        stats["blocked"] += 1
                        for b in blockers:
                            assert b.name in ALLOWED_BLOCKERS, (slug, enclosure, n, jack, line, b.name, b.message)
                            reasons[b.name] = reasons.get(b.name, 0) + 1
                    else:
                        stats["clean"] += 1
                        assert by["net volume"].level == "pass"
                        for ch in lay.chambers:
                            delta = (ch.net_l - ch.sheet_net_l) / ch.sheet_net_l * 100.0
                            assert abs(delta) <= 5.0
                            if abs(delta) > abs(worst[0]):
                                worst = (delta, (slug, enclosure, slot is not None, n, jack, line))
    print(f"\nmatrix {stats} reasons {reasons} worst net delta {worst[0]:+.2f} percent at {worst[1]} in {time.time() - t0:.1f} s")
    assert stats["cases"] == 1200
    assert stats["clean"] > 0
```
<!-- /code -->

Append at the end of the file, after one comment line `# ---- Plan 3 Task 2: port mouth check, aesthetics block, fixture list ----`:

<!-- code: .vault/scripts/test_cablayout.py symbols test_port_mouth_round_pass_and_warn,test_port_mouth_slot_no_port_and_unbuilt,test_port_mouth_site_default_fixture_warns_behind_the_magnet,test_report_carries_the_aesthetics_block,test_order_from_ignores_unknown_port_keys,test_port_fit_blocker_names_the_largest_table_tube_at_the_minimum,test_port_fit_blocker_says_no_table_tube_fits,test_slot_shelf_blocker_names_the_deepest_shelf,test_slot_a_hair_wider_than_the_chamber_is_trimmed_to_full_width,test_slot_over_the_trim_tolerance_still_blocks -->
```python
def test_port_mouth_round_pass_and_warn():
    # 77.3 tube, 40 mm long: the mouth sits 84.4 mm behind the magnet's rear face (y 155)
    # with a 29 percent slice of it facing the magnet: over one diameter, pass
    spec = spec_for(port="round", net=42.5)
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port mouth"].level == "pass"
    assert by["port mouth"].message == ("port mouth(s) clear: chamber 0 port 0: mouth 84 mm from the "
                                        "speaker 0 magnet (29 percent of the mouth), one diameter is 77.3 mm")
    # the 101.5 tube at the same length: 84 mm is under one diameter
    s = sheet(port="round", net=42.5)
    s["port"]["diameter_mm"] = 101.5
    spec = L.order_from(s, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port mouth"].level == "warn"
    assert by["port mouth"].message == ("chamber 0 port 0: mouth 84 mm from the speaker 0 magnet "
                                        "(18 percent of the mouth), under one diameter (101.5 mm)")
    # a tube ending at the 25 mm axial standoff, inside the magnet footprint: warns and names the magnet
    s = sheet(port="round", net=42.5)
    s["port"]["length_mm"] = 99.0
    spec = L.order_from(s, L.Aesthetics())
    lay = L.layout(spec)
    (c, j, free, what, cover, d_eff), = L.port_mouth_clearances(lay)
    assert (c, j, what, d_eff) == (0, 0, "speaker 0 magnet", 77.3)
    assert free == pytest.approx(25.4) and 0.25 < cover < 0.33
    by = {ch.name: ch for ch in L.check_layout(lay, spec)}
    assert by["port mouth"].level == "warn"
    assert by["port mouth"].message.startswith("chamber 0 port 0: mouth 25 mm from the speaker 0 magnet")

def test_port_mouth_slot_no_port_and_unbuilt():
    # 1x12 slot: the bottom stiffener starts at the shelf's rear edge, so it faces the mouth at 0 mm
    spec = spec_for(port="slot", net=42.5)
    lay = L.layout(spec)
    (c, j, free, what, cover, d_eff), = L.port_mouth_clearances(lay)
    assert (c, j, free, what) == (0, 0, 0.0, "stiffener bottom")
    assert d_eff == pytest.approx(math.sqrt(4 * 300 * 40 / math.pi)) and 0.05 < cover < 0.1
    by = {ch.name: ch for ch in L.check_layout(lay, spec)}
    assert by["port mouth"].level == "warn"
    assert by["port mouth"].message == ("chamber 0 port 0: mouth 0 mm from the stiffener bottom "
                                        "(8 percent of the mouth), under one diameter (123.6 mm)")
    # a mono 2x12 with two slots: the brace splits the bottom span so there is no stiffener; the back
    # cleat is the first solid behind the mouth, 169 mm away (shelf rear edge y 80, cleat at y 249.4)
    s = sheet(external=(760.0, 457.2, 279.4), drivers=2, port="slot", net=80.0)
    s["port"]["slot_w_mm"] = 340.0
    spec = L.order_from(s, L.Aesthetics())
    by = {ch.name: ch for ch in L.check_layout(L.layout(spec), spec)}
    assert by["port mouth"].level == "pass"
    assert by["port mouth"].message.startswith(
        "port mouth(s) clear: chamber 0 port 0: mouth 169 mm from the cleat back bottom "
        "(46 percent of the mouth), one diameter is 131.6 mm; chamber 0 port 1: mouth 169 mm")
    # no port at all, and a port the layout could not place
    closed = spec_for(enclosure="closed", net=42.5)
    assert {c.name: c for c in L.check_layout(L.layout(closed), closed)}["port mouth"].message == "no port"
    s = sheet(port="round", net=42.5)
    s["port"]["length_mm"] = 250.0
    spec = L.order_from(s, L.Aesthetics())
    by = {ch.name: ch for ch in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "blocker"
    assert by["port mouth"].level == "pass" and by["port mouth"].message == "no port placed (see port fit)"

def test_port_mouth_site_default_fixture_warns_behind_the_magnet():
    path = SITE_DEFAULT / "voicing.json"
    assert path.exists(), f"fixture sheet missing: {path}"
    spec = L.order_from(L.load_voicing(path), L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "pass"
    assert by["port mouth"].level == "warn"
    assert by["port mouth"].message == ("chamber 0 port 0: mouth 84 mm from the speaker 0 magnet "
                                        "(18 percent of the mouth), under one diameter (101.5 mm)")

def test_report_carries_the_aesthetics_block():
    aest = L.Aesthetics(corner_joint="dovetail", baffle_mount="fixed", handle="recessed-side", corners="none",
                        piping=True, feet="tilt-back", tolex_roll_in=32, tolex_color="Fender Style Tweed",
                        grill_cloth="Fender Style Oxblood", head_width_mm=500.0)
    spec = spec_for(line="hardwood", species="black walnut", port="round", net=42.5, aesthetics=aest)
    lay = L.layout(spec)
    rep = L.layout_report(lay, L.check_layout(lay, spec))
    json.dumps(rep)
    block = rep["aesthetics"]
    assert len(block) == 24
    assert {k: block[k] for k in ("corner_joint", "baffle_mount", "handle", "corners", "piping", "feet",
                                  "tolex_roll_in", "tolex_color", "grill_cloth", "head_width_mm")} == {
        "corner_joint": "dovetail", "baffle_mount": "fixed", "handle": "recessed-side", "corners": "none",
        "piping": True, "feet": "tilt-back", "tolex_roll_in": 32, "tolex_color": "Fender Style Tweed",
        "grill_cloth": "Fender Style Oxblood", "head_width_mm": 500.0}
    assert block["jack_plate_cutout_mm"] == [110.0, 70.0]      # every Aesthetics field travels, tuples as lists
    assert rep["corner_joint"] == "dovetail" and rep["baffle_mount"] == "fixed"

def test_order_from_ignores_unknown_port_keys():
    plain = sheet(port="round", net=42.5)
    extra = copy.deepcopy(plain)
    extra["port"]["pinned"] = True
    extra["port"]["fb_override_hz"] = 70.0
    a, b = L.order_from(plain, L.Aesthetics()), L.order_from(extra, L.Aesthetics())
    assert a == b
    ra = L.layout_report(L.layout(a), L.check_layout(L.layout(a), a))
    rb = L.layout_report(L.layout(b), L.check_layout(L.layout(b), b))
    assert ra == rb

def test_port_fit_blocker_names_the_largest_table_tube_at_the_minimum():
    # the Cannabis Rex under the roots tone: the default proposal snaps to the 153.2 mm tube, which
    # seats nowhere in its box; the blocker names the largest table tube that fits at 24 mm
    drv = cabvoice.load_speaker("eminence-cannabis-rex")
    z = drv.impedance_ohm[0]
    v = cabvoice.propose([drv], [z], "closed-ported", TONE, "mono", cabvoice.Constraints(line="tolex"), "rex").to_dict()
    assert v["blockers"] == [] and v["port"]["diameter_mm"] == 153.2
    spec = L.order_from(v, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "blocker"
    assert by["port fit"].message == (
        "port fit: chamber 0 port 0: no round port of 153.2 mm fits with 25 mm clearance; "
        "the longest table tube that fits at the 24 mm minimum is 101.5 mm; "
        "raise Fb, use a smaller tube or a larger box, or a front slot")
    assert by["port mouth"].message == "no port placed (see port fit)"
    # the skill's next step: pin the named tube and read the next run's verdicts
    pinned = cabvoice.propose([drv], [z], "closed-ported", TONE, "mono",
                              cabvoice.Constraints(line="tolex", port_tube_mm=101.5), "rex").to_dict()
    assert pinned["port"]["pinned"] is True and pinned["port"]["length_mm"] == 24.0
    spec = L.order_from(pinned, L.Aesthetics())
    lay = L.layout(spec)
    by = {c.name: c for c in L.check_layout(lay, spec)}
    assert by["port fit"].level == "pass" and lay.round_ports[0].id_mm == 101.5
    assert by["port mouth"].level == "warn" and "under one diameter (101.5 mm)" in by["port mouth"].message

def test_port_fit_blocker_says_no_table_tube_fits():
    # a narrow, shallow box: the 24 mm tube's span overlaps the magnet's axial standoff, so every
    # direction of the scan runs into a wall or a cleat before the radial requirement is met
    s = sheet(external=(360.0, 457.2, 192.0), port="round", net=15.0)
    s["port"]["diameter_mm"] = 101.5
    spec = L.order_from(s, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["magnet to back"].level == "pass"
    assert by["port fit"].message == (
        "port fit: chamber 0 port 0: no round port of 101.5 mm fits with 25 mm clearance; "
        "no table tube fits; use a front slot or a larger box")

def test_slot_shelf_blocker_names_the_deepest_shelf():
    s = sheet(port="slot", net=42.5)
    s["port"]["length_mm"] = 220.0            # the site box: 267.4 - 20 - 40 leaves a 207 mm shelf at most
    spec = L.order_from(s, L.Aesthetics())
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].message == (
        "port fit: slot shelf 220 mm deep leaves 27 mm behind it, under the 40 mm the slot needs to "
        "breathe; the deepest shelf that fits is 207 mm; lower the slot height or use a round port")
    shallow = sheet(external=(508.0, 457.2, 90.0), port="slot", net=10.0)     # 40 mm of internal depth
    spec = L.order_from(shallow, L.Aesthetics())
    _, _, blockers = L.slot_ports(spec, L.frame(spec))
    assert blockers == ["port fit: slot shelf 60 mm deep leaves -2 mm behind it, under the 40 mm the slot "
                        "needs to breathe; no shelf fits; lower the slot height or use a round port"]

def test_slot_a_hair_wider_than_the_chamber_is_trimmed_to_full_width():
    # the skill's slot re-run pins the width, so a slot can land a hair over its chamber from
    # rounding; up to SLOT_TRIM_MM over, the layout trims it to the full width instead of blocking
    s = sheet(port="slot", net=42.5)                       # 472 mm chamber, one slot: avail is the chamber
    s["port"]["slot_w_mm"] = 472.0 + 0.5
    spec = L.order_from(s, L.Aesthetics())
    fr = L.frame(spec)
    slots, blanks, blockers = L.slot_ports(spec, fr)
    assert blockers == [] and len(slots) == 1
    assert (slots[0].x0, slots[0].x1) == pytest.approx((-236.0, 236.0))
    assert slots[0].cheek_w_mm == pytest.approx(0.0)
    assert [b.name for b in blanks] == ["shelf"]                    # no side cheek parts
    assert blanks[0].size == (472.0, 60.0, 18.0)                    # the shelf spans the full chamber
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "pass"
    assert by["port fit"].message == "slot port(s) built: chamber 0 slot 472 x 40 mm, shelf 60 mm"

def test_slot_over_the_trim_tolerance_still_blocks():
    s = sheet(port="slot", net=42.5)
    s["port"]["slot_w_mm"] = 472.0 + 1.5
    spec = L.order_from(s, L.Aesthetics())
    _, blanks, blockers = L.slot_ports(spec, L.frame(spec))
    assert blockers == ["port fit: chamber 0: 1 slot of 474 mm do not fit the 472 mm chamber; "
                        "narrow the slot or widen the box"]
    assert blanks == []
    by = {c.name: c for c in L.check_layout(L.layout(spec), spec)}
    assert by["port fit"].level == "blocker"
```
<!-- /code -->

In `scripts/test_cabmodel.py` replace these two:

<!-- code: .vault/scripts/test_cabmodel.py symbols CHECK_LINES,test_cab_py_finds_the_vault_from_an_order_directory -->
```python
CHECK_LINES = ["sheet", "net volume", "stereo balance", "cutout", "grill opening", "port fit", "port mouth",
               "magnet to back", "handle", "head match", "line", "jack plate", "stock", "part count", "spans",
               "interference", "air volume", "solid count", "rectangularity"]

def test_cab_py_finds_the_vault_from_an_order_directory(tmp_path):
    order = _order_dir(tmp_path)
    env = {k: v for k, v in os.environ.items() if k not in ("EXPORT", "TMP_STL", "SHOW", "PYTHONPATH")}
    proc = subprocess.run([sys.executable, "cab.py"], cwd=order, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    printed = [line[:16].strip() for line in proc.stdout.splitlines()]
    assert printed == CHECK_LINES[:15] and not (order / "cab.json").exists()
    proc = subprocess.run([sys.executable, str(order / "cab.py")], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
```
<!-- /code -->

Then replace everything from the line `# === TASK 12 ===` to the end of the file with:

<!-- code: .vault/scripts/test_cabmodel.py unit 12 -->
```python
# === TASK 12 ===
FIXTURE_ORDERS = ["site-default", "sample-roots-1x12", "rex-roots-1x12"]
DELIVERABLES = ["cab.json", "cab.step", "cutlist.md", "cutlist.csv", "images/cab-iso.png", "images/cab-front.png",
                "images/cab-top.png", "images/cab-right.png", "images/cab-exploded.png"]


def _fixture_dir(name: str) -> Path:
    return SITE_DEFAULT if name == "site-default" else FIXTURES / name


def _run_fixture(name: str, out: Path) -> tuple:
    """Run a fixture order's cab.py with EXPORT=1 into out; (process, cab.json dict or None)."""
    env = dict(os.environ, EXPORT="1", CAB_OUT=str(out))
    if (HERE / "cabvoice.py").exists():          # mirror run: the template's sys.path points at scripts/
        env["PYTHONPATH"] = str(HERE)
    proc = subprocess.run([sys.executable, str(_fixture_dir(name) / "cab.py")], env=env,
                          capture_output=True, text=True)
    report = json.loads((out / "cab.json").read_text()) if (out / "cab.json").exists() else None
    return proc, report


def test_site_default_fixture(tmp_path):
    proc, report = _run_fixture("site-default", tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    for got, want in zip(report["external_mm"], (508.0, 457.2, 279.4)):
        assert abs(got - want) <= 1.0
    assert (tmp_path / "cab.step").exists() and (tmp_path / "images" / "cab-exploded.png").exists()
    assert all(c["level"] != "blocker" for c in report["checks"])
    assert "interference" in proc.stdout and "exported" in proc.stdout


CHECK_LINES = ["sheet", "net volume", "stereo balance", "cutout", "grill opening", "port fit", "port mouth",
               "magnet to back", "handle", "head match", "line", "jack plate", "stock", "part count", "spans",
               "interference", "air volume", "solid count", "rectangularity"]


def _order_dir(tmp_path):
    """The template copied to the design's per-order depth, projects/Cab-<order>/,
    in a scratch vault whose scripts/ is this suite's module directory."""
    vault = tmp_path / "vault"
    order = vault / "projects" / "Cab-probe"
    order.mkdir(parents=True)
    (vault / "scripts").symlink_to(HERE, target_is_directory=True)
    for name in ("cab.py", "voicing.json"):
        (order / name).write_bytes((SITE_DEFAULT / name).read_bytes())
    return order


def test_cab_py_finds_the_vault_from_an_order_directory(tmp_path):
    order = _order_dir(tmp_path)
    env = {k: v for k, v in os.environ.items() if k not in ("EXPORT", "TMP_STL", "SHOW", "PYTHONPATH")}
    proc = subprocess.run([sys.executable, "cab.py"], cwd=order, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    printed = [line[:16].strip() for line in proc.stdout.splitlines()]
    assert printed == CHECK_LINES[:15] and not (order / "cab.json").exists()
    proc = subprocess.run([sys.executable, str(order / "cab.py")], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_cab_py_exits_2_on_a_blocker_and_still_exports(tmp_path):
    order = _order_dir(tmp_path)
    v = json.loads((order / "voicing.json").read_text())
    v["volumes"]["net_total_l"] *= 1.3
    v["volumes"]["per_chamber_net_l"] *= 1.3
    (order / "voicing.json").write_text(json.dumps(v, indent=2))
    out = tmp_path / "out"
    env = dict(os.environ, EXPORT="1", CAB_OUT=str(out))
    env.pop("PYTHONPATH", None)
    proc = subprocess.run([sys.executable, str(order / "cab.py")], env=env, capture_output=True, text=True)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    lines = proc.stdout.splitlines()
    assert [line[:16].strip() for line in lines if not line.startswith("exported")] == CHECK_LINES
    assert any(line.startswith("net volume") and " blocker " in line for line in lines)
    report = json.loads((out / "cab.json").read_text())
    assert report["files"]["cab_json"] == "cab.json" and (out / "cab.step").exists()
    assert [c["level"] for c in report["checks"] if c["name"] == "net volume"] == ["blocker"]


# ---- Plan 3 Task 2: port mouth check, aesthetics block, fixture list ----
@pytest.mark.parametrize("name", FIXTURE_ORDERS)
def test_fixture_order_runs_clean_with_every_deliverable(name, tmp_path):
    proc, report = _run_fixture(name, tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    blockers = [c for c in report["checks"] if c["level"] == "blocker"]
    assert blockers == [], blockers
    assert [c["name"] for c in report["checks"]] == CHECK_LINES
    assert set(report["aesthetics"]) >= {"corner_joint", "baffle_mount", "handle", "corners", "piping", "feet",
                                         "tolex_roll_in", "tolex_color", "grill_cloth", "head_width_mm"}
    missing = [d for d in DELIVERABLES if not (tmp_path / d).exists()]
    assert missing == [], missing


# ---- shell roundover option ----
ROUNDOVER_MM = 12.7
SITE_INTERNAL_MM = (472.0, 421.2, 229.4)


def _site_box(enclosure, line, species, roundover_mm, joint="finger"):
    """Layout of the site box voiced live from internal 472 x 421.2 x 229.4 mm on the matrix speaker."""
    drv = cabvoice.load_speaker(MATRIX_SPEAKER)
    c = cabvoice.Constraints(line=line, species=species)
    v = cabvoice.evaluate([drv], [drv.impedance_ohm[0]], enclosure, TONE, SITE_INTERNAL_MM, constraints=c).to_dict()
    assert not v["blockers"], v["blockers"]
    return L.layout(L.order_from(v, L.Aesthetics(corner_joint=joint, roundover_mm=roundover_mm)))


def _rounded_box_removed_mm3(W, D, H, r):
    """A W x D x H box's volume minus the same box with all 12 edges filleted at r."""
    a, b, c = W - 2 * r, D - 2 * r, H - 2 * r
    kept = a * b * c + 2 * r * (a * b + a * c + b * c) + math.pi * r * r * (a + b + c) + 4.0 / 3.0 * math.pi * r ** 3
    return W * D * H - kept


def _corner_probes(W, D, H):
    """A point 1 mm in from each outer face at each of the box's eight corners."""
    return [(sx * (W / 2 - 1.0), y, z) for sx in (-1, 1) for y in (1.0, D - 1.0) for z in (1.0, H - 1.0)]


def test_roundover_rounds_the_hardwood_open_back_site_box_shell_and_nothing_else():
    plain_lay = _site_box("open", "hardwood", "black walnut", 0)
    lay = _site_box("open", "hardwood", "black walnut", ROUNDOVER_MM)
    fr = L.frame(lay.spec)
    W, H, D, t, r = fr.W, fr.H, fr.D, fr.t, ROUNDOVER_MM
    assert (W, H, D, t) == (508.0, 457.2, 279.4, 19.0)
    assert M.roundover_envelope(plain_lay) is None
    plain, cab = M.build(plain_lay), M.build(lay)
    before = {e["name"]: e["solid"] for e in plain.parts}
    after = {e["name"]: e["solid"] for e in cab.parts}
    edge_area = (1.0 - math.pi / 4.0) * r * r          # the cross-section a roundover removes along a straight edge
    # every point within r of at most one outer face: the only material a roundover may not touch
    skin_and_core = (M._box(-W / 2, r, r, W / 2, D - r, H - r) + M._box(-W / 2 + r, 0.0, r, W / 2 - r, D, H - r)
                     + M._box(-W / 2 + r, r, 0.0, W / 2 - r, D - r, H))
    drops = {}
    for name in M.SHELL_NAMES:
        s0, s1 = before[name], after[name]
        assert len(s1.solids()) == 1 and s1.is_valid and s1.label == name, name
        b0, b1 = s0.bounding_box(), s1.bounding_box()
        assert (b1.min - b0.min).length < 1e-6 and (b1.max - b0.max).length < 1e-6, name
        assert abs((s0 & skin_and_core).volume - (s1 & skin_and_core).volume) < 1.0, name   # inside faces untouched
        drops[name] = s0.volume - s1.volume
        run = W if name in ("top", "bottom") else H      # the length of the panel's front and back edges
        # at least those two edges less the corner blocks; at most both whole plus both front-to-back corner edges
        assert 2 * (run - 2 * t) * edge_area < drops[name] < 2 * (run + D) * edge_area, (name, drops[name])
    assert abs(sum(drops.values()) - _rounded_box_removed_mm3(W, D, H, r)) < 1.0
    for p in _corner_probes(W, D, H):
        assert any(before[n].is_inside(p) for n in M.SHELL_NAMES), p
        assert not any(after[n].is_inside(p) for n in M.SHELL_NAMES), p
    for name, p in (("top", (0.0, D / 2, H - 1.0)), ("bottom", (0.0, D / 2, 1.0)),
                    ("side_left", (-W / 2 + 1.0, D / 2, H / 2)), ("side_right", (W / 2 - 1.0, D / 2, H / 2))):
        assert after[name].is_inside(p), name
    for name, solid in after.items():
        if name not in M.SHELL_NAMES:
            assert abs(solid.volume - before[name].volume) < 1e-6, name
    assert {k: v.volume for k, v in cab.components.items()} == {k: v.volume for k, v in plain.components.items()}
    assert [c.level for c in L.check_layout(lay, lay.spec)] == [c.level for c in L.check_layout(plain_lay, plain_lay.spec)]
    by0 = {c.name: c for c in M.check_build(plain, plain_lay)}
    by1 = {c.name: c for c in M.check_build(cab, lay)}
    assert [c.level for c in by1.values()] == ["pass"] * 4, [c.message for c in by1.values()]
    assert by1["air volume"].message == by0["air volume"].message
    assert abs(cab.air[0].volume - plain.air[0].volume) < 1.0


def test_roundover_cuts_through_the_dovetail_combs():
    lay = _site_box("open", "hardwood", "black walnut", ROUNDOVER_MM, joint="dovetail")
    W, H, D = lay.spec.external_mm
    envelope = M.roundover_envelope(lay)
    removed = 0.0
    for b in lay.parts:
        if b.name in M.SHELL_NAMES:
            plain = M.blank_solid(b)
            rounded = M.shell_solid(b, envelope)
            assert len((plain & envelope).solids()) == 1 and rounded.is_valid, b.name
            assert not any(rounded.is_inside(p) for p in _corner_probes(W, D, H)), b.name
            removed += plain.volume - rounded.volume
    assert abs(removed - _rounded_box_removed_mm3(W, D, H, ROUNDOVER_MM)) < 1.0


def test_roundover_on_a_tolex_closed_site_box_builds_clean():
    lay = _site_box("closed", "tolex", None, ROUNDOVER_MM)
    assert [c.message for c in L.check_layout(lay, lay.spec) if c.level == "blocker"] == []
    cab = M.build(lay)
    checks = M.check_build(cab, lay)
    assert [c.level for c in checks] == ["pass"] * 4, [c.message for c in checks]
    W, H, D = lay.spec.external_mm
    removed = sum(M.blank_solid(b).volume - e["solid"].volume
                  for b, e in zip(lay.parts, cab.parts) if b.name in M.SHELL_NAMES)
    assert abs(removed - _rounded_box_removed_mm3(W, D, H, ROUNDOVER_MM)) < 1.0


# ---- strap handle: a leather strap arched between two end caps ----
STRAP_HANDLE_LABELS = ("strap_handle_cap_0", "strap_handle_cap_1", "strap_handle")


def test_strap_handle_is_a_leather_strap_between_two_end_caps(tmp_path):
    lay = _site_layout()
    assert lay.spec.aesthetics.handle == "strap"
    x, y, z = next(h for h in lay.hardware if h.item == "strap handle").position
    comps = M.component_solids(lay)
    assert [k for k in comps if k.startswith("strap_handle")] == list(STRAP_HANDLE_LABELS)
    for name in STRAP_HANDLE_LABELS:
        assert comps[name].label == name and len(comps[name].solids()) == 1 and comps[name].is_valid, name
    caps, strap = [comps[n] for n in STRAP_HANDLE_LABELS[:2]], comps["strap_handle"]
    cap_x, cap_y, cap_h = M.STRAP_CAP_MM
    boxes = [c.bounding_box() for c in caps]
    centers = [b.center() for b in boxes]
    # caps on the top panel's outer face, centered on the two screws
    assert centers[1].X - centers[0].X == pytest.approx(lay.spec.aesthetics.handle_screw_spacing_mm, abs=1e-6)
    assert (centers[0].X + centers[1].X) / 2.0 == pytest.approx(x, abs=1e-6)
    for b, c in zip(boxes, centers):
        assert c.Y == pytest.approx(y, abs=1e-6)
        assert (b.max.X - b.min.X, b.max.Y - b.min.Y) == pytest.approx((cap_x, cap_y), abs=1e-6)
        assert (b.min.Z, b.max.Z) == pytest.approx((z, z + cap_h), abs=1e-6)
    assert all(c.volume < cap_x * cap_y * cap_h - 100.0 for c in caps)      # top edges rounded
    # the strap: ends at cap height a gap off each cap face, apex above the cap tops
    cap_top = z + cap_h
    sb = strap.bounding_box()
    assert sb.min.X == pytest.approx(boxes[0].max.X + M.STRAP_GAP_MM, abs=1e-6)
    assert sb.max.X == pytest.approx(boxes[1].min.X - M.STRAP_GAP_MM, abs=1e-6)
    assert sb.max.Y - sb.min.Y == pytest.approx(M.STRAP_W_MM, abs=1e-6)
    assert z < sb.min.Z < cap_top and sb.max.Z > cap_top
    lower = cap_top + M.STRAP_RISE_MM                 # the lower face at mid-span, the leather above it
    assert not strap.is_inside((x, y, lower - 0.3)) and strap.is_inside((x, y, lower + 0.3))
    assert strap.is_inside((x, y, lower + M.STRAP_T_MM - 0.3)) and not strap.is_inside((x, y, lower + M.STRAP_T_MM + 0.3))
    shell = [M.blank_solid(b) for b in lay.parts if b.name in M.SHELL_NAMES]
    handle = caps + [strap]
    for i, a in enumerate(handle):
        for b in handle[i + 1:] + shell:
            assert M.overlap_volume(a, b) < 1e-3, (a.label, b.label)
    step = tmp_path / "handle.step"
    M.export_step(M.compound_of(handle), str(step))
    text = step.read_text(errors="ignore")
    assert all(f"'{name}'" in text for name in STRAP_HANDLE_LABELS)


# ---- the hardwood roundover default through the CAD path ----
def test_hardwood_default_rounds_the_panels_and_zero_leaves_them_sharp():
    default = _site_box("open", "hardwood", "black walnut", None)
    sharp = _site_box("open", "hardwood", "black walnut", 0)
    assert default.spec.aesthetics.roundover_mm == 12.7 and sharp.spec.aesthetics.roundover_mm == 0
    envelope = M.roundover_envelope(default)
    assert envelope is not None and M.roundover_envelope(sharp) is None
    W, H, D = default.spec.external_mm
    removed = 0.0
    for b in default.parts:
        if b.name in M.SHELL_NAMES:
            plain = M.blank_solid(b)
            removed += plain.volume - M.shell_solid(b, envelope).volume
            assert M.shell_solid(b, None).volume == plain.volume, b.name
    assert abs(removed - _rounded_box_removed_mm3(W, D, H, 12.7)) < 1.0
    cab = M.build(sharp)                       # 0 builds the plain blanks
    for e, b in zip(cab.parts, sharp.parts):
        if b.name in M.SHELL_NAMES:
            assert abs(e["solid"].volume - L.blank_volume_mm3(b)) < 1.0, b.name
    assert [c.level for c in M.check_build(cab, sharp)] == ["pass"] * 4
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cablayout.py -q -k "port_mouth or aesthetics or unknown_port_keys or table_tube or deepest_shelf or CHECK or matrix"`
Expected: FAIL (`port_mouth_clearances` undefined, 14 names in `CHECK_NAMES` against 15 in the report, the old blocker text).

- [ ] **Step 3: Layout changes**

In `scripts/cablayout.py` insert `SLOT_TRIM_MM` directly after the `GRILL_FRONT_MM` line among the layout constants:

<!-- code: .vault/scripts/cablayout.py symbols SLOT_TRIM_MM -->
```python
SLOT_TRIM_MM = 1.0            # a slot up to this much wider than its chamber is trimmed to it, not blocked
```
<!-- /code -->

Insert `largest_tube_at_minimum` directly above `round_ports` and replace `round_ports` and `slot_ports`:

<!-- code: .vault/scripts/cablayout.py symbols largest_tube_at_minimum,round_ports,slot_ports -->
```python
def largest_tube_at_minimum(env: Envelope, sign: float, fr: Frame, obstacles: list, envelopes: list,
                            tubes: list, below_id_mm: float):
    """The longest table tube inside diameter under below_id_mm that the
    placement scan seats at the engine's minimum port length, or None. A tube
    that does not fit at the minimum cannot fit at any length, so this is the
    necessary-condition hint the port fit blocker names for the skill's loop:
    pin that tube once and read the next run's verdicts."""
    ya, yb = fr.D - cabvoice.MIN_PORT_LENGTH_MM, fr.D - BACK_MM
    for tid in sorted(cabvoice.PORT_TUBE_ID_MM, reverse=True):
        if tid >= below_id_mm - 1e-6:
            continue
        od, _, _ = tube_geometry(tid)
        rr = (od + FLANGE_RING_EXTRA_MM) / 2.0
        if _place_tube(env, sign, od / 2.0, ya, yb, fr, obstacles, envelopes, tubes, rr) is not None:
            return tid
    return None

def round_ports(spec: CabSpec, fr: Frame, envelopes: list, obstacles: list) -> tuple:
    """(RoundPorts, blanks, back features, blockers). One port per driver in
    the chamber (spec.port.count per chamber), each beside its driver."""
    port = spec.port
    if port is None or port.shape != "round":
        return [], [], [], []
    id_mm, L = port.diameter_mm, port.length_mm
    od, mat, tube_note = tube_geometry(id_mm)
    r = od / 2.0
    ring_od = od + FLANGE_RING_EXTRA_MM
    ports, blanks, feats, blockers = [], [], [], []
    tubes = []
    by_chamber = {}
    for env in envelopes:
        by_chamber.setdefault(env.chamber, []).append(env)
    for c in range(len(fr.chambers)):
        envs = by_chamber.get(c, [])
        count = port.count
        for j in range(count):
            env = envs[min(j, len(envs) - 1)] if envs else None
            if env is None:
                blockers.append(f"port fit: chamber {c} has no driver to place a port beside")
                continue
            sign = -1.0 if env.center[0] < 0 else 1.0
            ya, yb = fr.D - L, fr.D - BACK_MM
            rr = ring_od / 2.0
            reaches = ya < fr.y_bb - 1e-6      # the tube must stay behind the baffle
            spot = None if reaches else _place_tube(env, sign, r, ya, yb, fr, obstacles, envelopes, tubes, rr)
            if spot is None:
                fit = None
                lengths, Lf = [], L - 5.0
                while Lf > cabvoice.MIN_PORT_LENGTH_MM:
                    lengths.append(Lf)
                    Lf -= 5.0
                lengths.append(cabvoice.MIN_PORT_LENGTH_MM)   # the shortest port that can be built
                for Lf in lengths:
                    if (fr.D - Lf >= fr.y_bb - 1e-6
                            and _place_tube(env, sign, r, fr.D - Lf, yb, fr, obstacles, envelopes, tubes, rr)):
                        fit = Lf
                        break
                why = ("reaches the baffle" if reaches
                       else f"finds no spot with {CLEARANCE_MM:.0f} mm clearance")
                if fit is None:
                    smaller = largest_tube_at_minimum(env, sign, fr, obstacles, envelopes, tubes, id_mm)
                    hint = (f"the longest table tube that fits at the {cabvoice.MIN_PORT_LENGTH_MM:.0f} mm "
                            f"minimum is {smaller:g} mm; raise Fb, use a smaller tube or a larger box, or a front slot"
                            if smaller is not None else "no table tube fits; use a front slot or a larger box")
                    blockers.append(f"port fit: chamber {c} port {j}: no round port of "
                                    f"{id_mm:.1f} mm fits with {CLEARANCE_MM:.0f} mm clearance; {hint}")
                else:
                    blockers.append(f"port fit: chamber {c} port {j}: tube {id_mm:.1f} x {L:.0f} mm "
                                    f"{why}; longest tube that fits at this diameter is {fit:.0f} mm; "
                                    "raise Fb, use a smaller tube or a larger box, or a front slot")
                continue
            cx, cz = spot
            tubes.append((cx, cz, r, ya, yb, rr))
            sfx = f"_{c}_{j}"
            has_tube = L > 2 * BACK_MM
            if has_tube:
                blanks.append(Blank(f"port_tube{sfx}", 1, mat, PVC_DENSITY, shape="tube",
                                    pos=(cx, fr.D - L, cz), size=(od, L, id_mm),
                                    blank_mm=((od - id_mm) / 2.0, od, L), chamber=c,   # wall x OD x length
                                    notes=f"cut to {L:.0f} mm, {id_mm:.1f} mm inside diameter, glued "
                                          "through the back panel and the flange ring"
                                          + ("; " + tube_note if tube_note else "")))
                ring_t, ring_id = FLANGE_RING_T_MM, od
                hole = od
            else:
                ring_t, ring_id = L - BACK_MM, id_mm
                hole = id_mm
            blanks.append(Blank(f"port_ring{sfx}", 1, birch(BACK_MM), BIRCH_DENSITY, shape="ring",
                                pos=(cx, fr.D - BACK_MM - ring_t, cz), size=(ring_od, ring_t, ring_id),
                                blank_mm=(ring_t, ring_od, ring_od), chamber=c,
                                notes="flange ring cut from 12 mm ply, glued to the inside face of the back"
                                      + ("" if has_tube else f"; the ring is the port ({ring_t:.0f} mm beyond the panel), no tube")
                                      + (f"; planed to {ring_t:g} mm" if ring_t < FLANGE_RING_T_MM - 1e-6 else "")))
            feats.append({"type": "cutout", "center": (cx, cz), "d": hole})
            ports.append(RoundPort(c, (cx, cz), id_mm, od, L, ring_od, fr.D - L, fr.D))
    return ports, blanks, feats, blockers

def slot_ports(spec: CabSpec, fr: Frame) -> tuple:
    """(SlotPorts, blanks, blockers): full-chamber-width slot under the
    baffle, an 18 mm shelf sets the port length, cheeks fill a narrower slot,
    a mono 2x12 gets two slots split by an 18 mm center cheek."""
    port = spec.port
    if port is None or port.shape != "slot":
        return [], [], []
    s_w, s_h, L = port.slot_w_mm, port.slot_h_mm, port.length_mm
    slots, blanks, blockers = [], [], []
    free = fr.y_bi - (fr.y_bf + L)
    if free < max(CLEARANCE_MM, s_h):
        deepest = math.floor(fr.y_bi - fr.y_bf - max(CLEARANCE_MM, s_h))
        hint = (f"the deepest shelf that fits is {deepest:.0f} mm" if deepest >= cabvoice.MIN_PORT_LENGTH_MM
                else "no shelf fits")
        blockers.append(f"port fit: slot shelf {L:.0f} mm deep leaves {free:.0f} mm behind it, "
                        f"under the {max(CLEARANCE_MM, s_h):.0f} mm the slot needs to breathe; {hint}; "
                        "lower the slot height or use a round port")
        return slots, blanks, blockers
    mat18 = birch(BAFFLE_MM)
    for c, (xa, xb) in enumerate(fr.chambers):
        n = port.count
        avail = (xb - xa) - (n - 1) * DIVIDER_MM
        if n * s_w > avail + SLOT_TRIM_MM + 1e-6:
            blockers.append(f"port fit: chamber {c}: {n} slot{'s' if n > 1 else ''} of {s_w:.0f} mm "
                            f"do not fit the {xb - xa:.0f} mm chamber"
                            + (" with the 18 mm center cheek" if n > 1 else "")
                            + "; narrow the slot or widen the box")
            continue
        w = min(s_w, avail / n)      # up to SLOT_TRIM_MM over the chamber: the full width, no side cheeks
        cheek = max((avail - n * w) / 2.0, 0.0)
        sfx = _suffix(spec, c)
        blanks.append(Blank(f"shelf{sfx}", 1, mat18, BIRCH_DENSITY, pos=(xa, fr.y_bf, fr.z0 + s_h),
                            size=(xb - xa, L, BAFFLE_MM), blank_mm=(BAFFLE_MM, L, xb - xa),
                            chamber=c, length_axis="X",
                            notes="slot port shelf 18 mm birch: front edge flush with the baffle face, "
                                  f"depth {L:.0f} mm equals the port length, doubles as the bottom "
                                  "cleat, glued to the sides"))
        if cheek > 0.5:
            for side, x_c in (("left", xa), ("right", xb - cheek)):
                blanks.append(Blank(f"cheek_{side}{sfx}", 1, mat18, BIRCH_DENSITY, pos=(x_c, fr.y_bf, fr.z0),
                                    size=(cheek, L, s_h), blank_mm=_blank_dims(cheek, L, s_h),
                                    chamber=c, notes="slot cheek, fills the slot end, glued" + _glue_up(cheek)))
        x = xa + cheek
        for j in range(n):
            slots.append(SlotPort(c, x, x + w, s_h, L, cheek))
            x += w
            if j < n - 1:
                blanks.append(Blank(f"cheek_center{sfx}_{j}", 1, mat18, BIRCH_DENSITY,
                                    pos=(x, fr.y_bf, fr.z0), size=(DIVIDER_MM, L, s_h),
                                    blank_mm=_blank_dims(DIVIDER_MM, L, s_h), chamber=c,
                                    notes="center cheek between the two slots, in line with the brace"
                                          + _glue_up(DIVIDER_MM)))
                x += DIVIDER_MM
    return slots, blanks, blockers
```
<!-- /code -->

Insert these six directly above `check_layout`:

<!-- code: .vault/scripts/cablayout.py symbols _mouth_rect_overlaps,MOUTH_GRID,_mouth_coverage,_box_inside,_circle_inside,port_mouth_clearances -->
```python
def _mouth_rect_overlaps(box, x0, x1, z0, z1) -> bool:
    (bx0, _, bz0), (bx1, _, bz1) = box
    return _overlap(x0, x1, bx0, bx1) and _overlap(z0, z1, bz0, bz1)

MOUTH_GRID = 24

def _mouth_coverage(points: list, inside) -> float:
    """Fraction (0 to 1) of the mouth's sample points inside an obstruction's projection."""
    return sum(1 for (x, z) in points if inside(x, z)) / float(len(points))

def _box_inside(box):
    (bx0, _, bz0), (bx1, _, bz1) = box
    return lambda x, z: bx0 <= x <= bx1 and bz0 <= z <= bz1

def _circle_inside(cx, cz, r):
    return lambda x, z: math.hypot(x - cx, z - cz) <= r

def port_mouth_clearances(lay: Layout) -> list:
    """(chamber, index, free_mm, obstruction, coverage, effective_diameter_mm)
    per built port: the free air along the port axis from the inner mouth to
    the first solid whose projection overlaps the mouth's cross-section
    (basket and magnet envelopes, cleats, brace, divider, stiffeners), else the
    baffle's back face for a rear round port or the back panel's inner face
    for a front slot (coverage None). Coverage is the fraction of the mouth
    the obstruction faces, sampled on a MOUTH_GRID x MOUTH_GRID grid. The
    effective diameter is the tube inside diameter, or the diameter of a
    circle with the slot's area. Common practice keeps one diameter clear; the
    check warns below it and never blocks."""
    fr = frame(lay.spec)
    out, per_chamber = [], {}
    grid = [(i + 0.5) / MOUTH_GRID for i in range(MOUTH_GRID)]

    def nearest(candidates, terminal, points):
        best = (terminal[0], terminal[1], None)
        for (d, name, inside) in candidates:
            if d < best[0] - 1e-9:
                best = (d, name, inside)
        d, name, inside = best
        return d, name, (None if inside is None else _mouth_coverage(points, inside))

    def envelope_faces(env):
        faces = [(env.y0, env.y0 + env.basket_len, env.basket_d / 2.0, "basket")]
        if env.magnet_len > 0:
            faces.append((env.y0 + env.basket_len, env.y0 + env.basket_len + env.magnet_len,
                          env.magnet_d / 2.0, "magnet"))
        return faces

    for rp in lay.round_ports:                      # mouth faces the front
        c = rp.chamber
        j = per_chamber.get(c, 0)
        per_chamber[c] = j + 1
        cx, cz = rp.center
        r, y_m = rp.id_mm / 2.0, rp.y0
        points = [(cx - r + 2 * r * u, cz - r + 2 * r * v) for u in grid for v in grid
                  if math.hypot(2 * r * u - r, 2 * r * v - r) <= r]
        cands = []
        for p in lay.parts:
            if p.shape != "box" or not (p.chamber == c or p.name == "divider"):
                continue
            (_, by0, _), (_, by1, _) = p.box
            if by0 >= y_m - 1e-6 or _circle_box_gap(cx, cz, r, p.box) >= -1e-6:
                continue                            # behind the mouth, or beside it
            cands.append((max(0.0, y_m - by1), p.name.replace("_", " "), _box_inside(p.box)))
        for env in lay.envelopes:
            if env.chamber != c:
                continue
            ex, ez = env.center
            for (y_front, y_rear, er, part) in envelope_faces(env):
                if y_front < y_m - 1e-6 and math.hypot(cx - ex, cz - ez) < r + er - 1e-6:
                    cands.append((max(0.0, y_m - y_rear), f"speaker {env.speaker} {part}",
                                  _circle_inside(ex, ez, er)))
        d, what, cover = nearest(cands, (y_m - fr.y_bb, "baffle"), points)
        out.append((c, j, d, what, cover, rp.id_mm))
    for sp in lay.slot_ports:                       # mouth faces the back
        c = sp.chamber
        j = per_chamber.get(c, 0)
        per_chamber[c] = j + 1
        x0, x1, z0, z1 = sp.x0, sp.x1, fr.z0, fr.z0 + sp.slot_h_mm
        y_m = fr.y_bf + sp.shelf_depth_mm
        d_eff = math.sqrt(4.0 * (x1 - x0) * sp.slot_h_mm / math.pi)
        points = [(x0 + (x1 - x0) * u, z0 + (z1 - z0) * v) for u in grid for v in grid]
        cands = []
        for p in lay.parts:
            if p.shape != "box" or not (p.chamber == c or p.name == "divider"):
                continue
            (_, by0, _), (_, by1, _) = p.box
            if by1 <= y_m + 1e-6 or not _mouth_rect_overlaps(p.box, x0, x1, z0, z1):
                continue                            # in front of the mouth, or beside it
            cands.append((max(0.0, by0 - y_m), p.name.replace("_", " "), _box_inside(p.box)))
        for env in lay.envelopes:
            if env.chamber != c:
                continue
            ex, ez = env.center
            for (y_front, y_rear, er, part) in envelope_faces(env):
                if y_rear > y_m + 1e-6 and _circle_box_gap(ex, ez, er, ((x0, 0.0, z0), (x1, 0.0, z1))) < -1e-6:
                    cands.append((max(0.0, y_front - y_m), f"speaker {env.speaker} {part}",
                                  _circle_inside(ex, ez, er)))
        d, what, cover = nearest(cands, (fr.y_bi - y_m, "back panel"), points)
        out.append((c, j, d, what, cover, d_eff))
    return out
```
<!-- /code -->

Replace `check_layout` and `layout_report`:

<!-- code: .vault/scripts/cablayout.py symbols check_layout,layout_report -->
```python
def check_layout(lay: Layout, spec: CabSpec) -> list:
    fr = frame(spec)
    checks = []
    if spec.prediction_status == cabvoice.PREDICTION_STATUS:
        checks.append(Check("sheet", "pass", f"prediction {spec.prediction_status}; no blockers on the sheet"))
    else:
        checks.append(Check("sheet", "warn", f"sheet prediction_status '{spec.prediction_status}' differs "
                                             f"from the engine's '{cabvoice.PREDICTION_STATUS}'"))
    # net volume
    msgs, level = [], "pass"
    for ch in lay.chambers:
        delta = (ch.net_l - ch.sheet_net_l) / ch.sheet_net_l * 100.0
        msgs.append(f"chamber {ch.index} net {ch.net_l:.1f} L vs sheet {ch.sheet_net_l:.1f} L ({delta:+.1f} percent)")
        if abs(delta) > 5.0:
            level = "blocker"
    inside = layout_inside_parts_l(lay)
    if spec.sheet_inside_parts_l is not None:
        msgs.append(f"inside parts {inside:.2f} L vs sheet allowance {spec.sheet_inside_parts_l:.2f} L")
    else:
        msgs.append(f"inside parts {inside:.2f} L (sheet carries no allowance)")
    if any(n.startswith("blocker: port fit") for n in lay.notes):
        msgs.append("port not built, so its tube and ring are missing from the inside parts")
    checks.append(Check("net volume", level, "; ".join(msgs)))
    if len(lay.chambers) == 2:
        n0, n1 = lay.chambers[0].net_l, lay.chambers[1].net_l
        diff = abs(n0 - n1) / ((n0 + n1) / 2.0) * 100.0
        checks.append(Check("stereo balance", "pass" if diff <= 1.0 else "blocker",
                            f"chambers {n0:.2f} and {n1:.2f} L differ by {diff:.2f} percent"))
    else:
        checks.append(Check("stereo balance", "pass", "single chamber"))
    # cutout margins
    problems = []
    brace = spec.driver_count == 2 and spec.chambers == 1
    for co in lay.cutouts:
        xa, xb = fr.chambers[co.chamber]
        xc, zc = co.center
        r = co.diameter / 2.0
        s = spec.speakers[co.speaker]
        if abs(co.diameter - s.cutout_mm) > 1e-6:
            problems.append(f"cutout {co.speaker} diameter {co.diameter:g} differs from the note")
        for side, gap, wall in (("left", xc - r - xa, xa == fr.x0), ("right", xb - (xc + r), xb == fr.x1)):
            need = SHELL_MARGIN_MM if wall else CUTOUT_MARGIN_MM
            what = "shell" if wall else "divider"
            if gap < need - 1e-6:
                problems.append(f"cutout {co.speaker}: {gap:.1f} mm to the {side} {what}, {need:g} needed")
        if brace:
            gap = abs(xc) - r - BRACE_MM[0] / 2.0
            if gap < CUTOUT_MARGIN_MM - 1e-6:
                problems.append(f"cutout {co.speaker}: {gap:.1f} mm to the brace, {CUTOUT_MARGIN_MM:g} needed")
        low, high = zc - r - fr.z_vis0, fr.z1 - (zc + r)
        if low < SHELL_MARGIN_MM - 1e-6:
            problems.append(f"cutout {co.speaker}: {low:.1f} mm to the baffle bottom, {SHELL_MARGIN_MM:g} needed")
        if high < SHELL_MARGIN_MM - 1e-6:
            problems.append(f"cutout {co.speaker}: {high:.1f} mm to the top, {SHELL_MARGIN_MM:g} needed")
    if len(lay.cutouts) == 2 and spec.chambers == 1:
        a, b = lay.cutouts
        gap = (b.center[0] - b.diameter / 2.0) - (a.center[0] + a.diameter / 2.0)
        if gap < CUTOUT_GAP_MM - 1e-6:
            problems.append(f"cutouts {gap:.1f} mm apart, {CUTOUT_GAP_MM:g} needed")
    checks.append(Check("cutout", "blocker" if problems else "pass",
                        "; ".join(problems) if problems else
                        f"{len(lay.cutouts)} cutout(s) at the note diameter with {SHELL_MARGIN_MM:g} mm shell margins"))
    # grill opening
    inner_x0, inner_x1 = fr.x0 + GRILL_CLEARANCE_MM + GRILL_STRIP_W_MM, fr.x1 - GRILL_CLEARANCE_MM - GRILL_STRIP_W_MM
    inner_z0, inner_z1 = fr.z_vis0 + GRILL_CLEARANCE_MM + GRILL_STRIP_W_MM, fr.z1 - GRILL_CLEARANCE_MM - GRILL_STRIP_W_MM
    problems = []
    for co in lay.cutouts:
        xc, zc = co.center
        r = co.diameter / 2.0
        if (xc - r - inner_x0 < GRILL_CLEARANCE_MM - 1e-6 or inner_x1 - (xc + r) < GRILL_CLEARANCE_MM - 1e-6
                or zc - r - inner_z0 < GRILL_CLEARANCE_MM - 1e-6 or inner_z1 - (zc + r) < GRILL_CLEARANCE_MM - 1e-6):
            problems.append(f"grill strip covers cutout {co.speaker}")
    checks.append(Check("grill opening", "blocker" if problems else "pass",
                        "; ".join(problems) if problems else
                        f"strip inner edges clear every cutout by {GRILL_CLEARANCE_MM:g} mm"))
    # port fit
    port_blockers = [n[len("blocker: "):] for n in lay.notes if n.startswith("blocker: port fit")]
    if spec.port is None:
        checks.append(Check("port fit", "pass", "no port"))
    elif port_blockers:
        checks.append(Check("port fit", "blocker", "; ".join(port_blockers)))
    elif spec.port.shape == "round":
        pos = ", ".join(f"chamber {p.chamber} at x {p.center[0]:.0f} z {p.center[1]:.0f} ({p.id_mm:g} x {p.length_mm:.0f} mm)"
                        for p in lay.round_ports)
        checks.append(Check("port fit", "pass", f"round port(s) placed with {CLEARANCE_MM:g} mm clearance: {pos}"))
    else:
        pos = ", ".join(f"chamber {s.chamber} slot {s.x1 - s.x0:.0f} x {s.slot_h_mm:g} mm, shelf {s.shelf_depth_mm:.0f} mm"
                        for s in lay.slot_ports)
        checks.append(Check("port fit", "pass", f"slot port(s) built: {pos}"))
    # port mouth
    if spec.port is None:
        checks.append(Check("port mouth", "pass", "no port"))
    elif not lay.round_ports and not lay.slot_ports:
        checks.append(Check("port mouth", "pass", "no port placed (see port fit)"))
    else:
        entries, short = [], False
        for (c, j, free, what, cover, d_eff) in port_mouth_clearances(lay):
            under = free < d_eff - 1e-6
            short = short or under
            entries.append(f"chamber {c} port {j}: mouth {free:.0f} mm from the {what}"
                           + ("" if cover is None else f" ({cover * 100:.0f} percent of the mouth)")
                           + (f", under one diameter ({d_eff:.1f} mm)" if under
                              else f", one diameter is {d_eff:.1f} mm"))
        checks.append(Check("port mouth", "warn" if short else "pass",
                            ("" if short else "port mouth(s) clear: ") + "; ".join(entries)))
    # magnet to back
    if spec.closed:
        problems, best = [], None
        for env in lay.envelopes:
            gap = fr.y_bi - (env.y0 + env.basket_len + env.magnet_len)
            best = gap if best is None else min(best, gap)
            if gap < CLEARANCE_MM - 1e-6:
                problems.append(f"speaker {env.speaker} magnet {gap:.1f} mm from the back, {CLEARANCE_MM:g} needed")
        checks.append(Check("magnet to back", "blocker" if problems else "pass",
                            "; ".join(problems) if problems else f"at least {best:.1f} mm behind every magnet"))
    else:
        checks.append(Check("magnet to back", "pass", "open back"))
    # handle
    handle_warn = [n[len("warn: "):] for n in lay.notes if n.startswith("warn: ") and "handle" in n]
    straps = [h for h in lay.hardware if h.item == "strap handle"]
    if straps:
        off = abs(straps[0].position[0] - lay.com_mm[0])
        level = "pass" if off <= 15.0 and not handle_warn else "warn"
        checks.append(Check("handle", level, f"strap handle {off:.1f} mm from the center of mass on the width axis"
                            + ("; " + "; ".join(handle_warn) if handle_warn else "")))
    else:
        checks.append(Check("handle", "warn" if handle_warn else "pass",
                            "; ".join(handle_warn) if handle_warn else "recessed side handles at the depth center of mass"))
    # head match
    head = spec.aesthetics.head_width_mm
    if head is None:
        checks.append(Check("head match", "pass", "no head width given"))
    else:
        d = fr.W - head
        checks.append(Check("head match", "pass" if 0.0 <= d <= 10.0 else "warn",
                            f"external width {fr.W:.0f} mm is head width {head:g} mm {d:+.0f} mm"))
    # line
    problems = []
    if spec.aesthetics.corner_joint == "dovetail" and spec.line != "hardwood":
        problems.append("dovetail corners are a hardwood option")
    if spec.line == "hardwood" and species_density(spec.species) is None:
        problems.append(f"species density unknown for {spec.species!r}")
    checks.append(Check("line", "blocker" if problems else "pass",
                        "; ".join(problems) if problems else f"{spec.line} line, {spec.wall_material}"))
    # jack plate fit
    plate_warn = [n[len("warn: "):] for n in lay.notes if n.startswith("warn: jack plate")]
    side = "below" if spec.aesthetics.jack_plate_position == "top" and not spec.closed else "above"
    checks.append(Check("jack plate", "warn" if plate_warn else "pass",
                        "; ".join(plate_warn) if plate_warn else f"plates fit {side} the cleat"))
    # stock
    over = [p.name for p in lay.parts if not _stock_fits(p, spec)]
    checks.append(Check("stock", "warn" if over else "pass",
                        "over stock: " + ", ".join(over) if over else "every blank fits the stock limits"))
    checks.append(Check("part count", "pass", f"{lay.part_count} parts"))
    spans = [n[len("span: "):] for n in lay.notes if n.startswith("span: ")]
    unstiffened = unstiffened_shell_spans(spec, fr)
    words = ([unstiffened] if unstiffened else []) + spans
    checks.append(Check("spans", "warn" if spans else "pass",
                        "; ".join(words) if words else f"no panel span over {SPAN_MAX_MM:.0f} mm"))
    return checks

def layout_report(lay: Layout, checks: list) -> dict:
    from dataclasses import asdict
    spec = lay.spec
    fr = frame(spec)
    W, H, D = spec.external_mm
    return _round3({
        "name": spec.name,
        "generated": date.today().isoformat(),
        "line": spec.line, "species": spec.species,
        "corner_joint": spec.aesthetics.corner_joint,
        "baffle_mount": spec.aesthetics.baffle_mount,
        "aesthetics": asdict(spec.aesthetics),
        "external_mm": [W, H, D],
        "external_in": [round(v / MM_PER_INCH, 2) for v in (W, H, D)],
        "internal_mm": [fr.x1 - fr.x0, fr.z1 - fr.z0, fr.y_bi - fr.y_bb],
        "enclosure": {"type": spec.enclosure_type, "driver_count": spec.driver_count,
                      "chambers": spec.chambers, "jack_config": spec.jack_config,
                      "open_fraction": spec.open_fraction},
        "speakers": [s.slug for s in spec.speakers],
        "volumes": {"gross_l": [ch.gross_l for ch in lay.chambers],
                    "net_l": [ch.net_l for ch in lay.chambers],
                    "sheet_net_l": [ch.sheet_net_l for ch in lay.chambers],
                    "delta_pct": [(ch.net_l - ch.sheet_net_l) / ch.sheet_net_l * 100.0 for ch in lay.chambers],
                    "inside_parts_l": layout_inside_parts_l(lay),
                    "sheet_inside_parts_l": spec.sheet_inside_parts_l},
        "mass": {"total_kg": lay.mass_kg["total"], "parts_kg": lay.mass_kg["parts"],
                 "speakers_kg": lay.mass_kg["speakers"], "hardware_kg": lay.mass_kg["hardware"],
                 "com_mm": list(lay.com_mm)},
        "hardware": [{"item": h.item, "position_mm": list(h.position),
                      "cutout_mm": None if h.cutout is None else list(h.cutout),
                      "panel": h.panel, "notes": h.notes} for h in lay.hardware],
        "tolex": lay.tolex,
        "parts": [{"name": p.name, "qty": p.qty, "blank_mm": list(p.blank_mm),
                   "material": p.material, "notes": p.notes} for p in lay.parts],
        "checks": [{"name": c.name, "level": c.level, "message": c.message} for c in checks],
        "prediction_status": spec.prediction_status,
    })
```
<!-- /code -->

- [ ] **Step 4: Run the layout tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cablayout.py -q -s`
Expected: 52 passed. The matrix line prints 1200 cases: 150 engine power stops, 1026 clean, 24 blocked (port fit 24, net volume 22; every port-fit blocker is a Cannabis Rex or Swamp Thang round proposal and every one names the 101.5 mm tube), worst clean net delta -1.10 percent, and 194 cases carrying a port mouth warn.

- [ ] **Step 5: Regenerate the site-default fixture**

Run: `EXPORT=1 .venv/bin/python projects/Speaker-cab-system/fixtures/site-default/cab.py; echo "exit $?"`
Expected: 19 check lines, all `pass` except `port mouth warn chamber 0 port 0: mouth 84 mm from the speaker 0 magnet (18 percent of the mouth), under one diameter (101.5 mm)` and the existing `spans warn`; `exit 0`; `cab.json` now holds 19 checks and an `aesthetics` block with 21 keys; `cutlist.md`, `cutlist.csv`, and the five renders rewritten (the geometry is unchanged, so the cut list rows and the images match the Plan 2 ones). View `images/cab-iso.png` with the Read tool.

- [ ] **Step 6: Run the CAD tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabmodel.py -q`
Expected: 24 passed in about 70 s (the site default's `cab.py` runs twice, once for the 1 mm reproduction test and once for the parametrized fixture test).

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cablayout.py scripts/test_cablayout.py scripts/test_cabmodel.py projects/Speaker-cab-system/fixtures/site-default/cab.json projects/Speaker-cab-system/fixtures/site-default/cutlist.md projects/Speaker-cab-system/fixtures/site-default/cutlist.csv projects/Speaker-cab-system/fixtures/site-default/images
git commit -m "Speaker cab plan 3 task 2: port mouth check, port fit names the tube that fits, aesthetics in cab.json, fixture list"
```

---

### Task 3: Canonical genre keys: voicing note, catalog normalization, genre test

**Files:**
- Modify: `knowledge/speaker-cab-voicing.md` (full replacement: the Key column and its sentence, the ranking precedence, the enclosure precedence with the Fb range, the evaluate-first bullet and the bridge table, the power rule, the port bullet on the landed engine values and the three flags, the low-end-shifter rule, the model-limits pointer, `updated: 2026-09-11`; the calibration block is Task 1's regenerated block)
- Create: `projects/Speaker-cab-system/pipeline/catalog_genres.py`
- Modify: `knowledge/speakers/*.md` (all 20 notes, through the script)
- Modify: `scripts/test_cabvoice.py` (`test_catalog_best_with_uses_table_labels` replaced; `GENRE_KEYS` and `test_catalog_genres_lines_use_canonical_keys` appended)
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/knowledge/speaker-cab-voicing.md`, `.vault/projects/Speaker-cab-system/pipeline/catalog_genres.py`, `.vault/scripts/test_cabvoice.py`, `.vault/knowledge/speakers/*.md`

**Interfaces:**
- Consumes: Task 1's engine and its regenerated calibration block; the twenty catalog notes as landed by Plan 2 (a `## Best with` section holding one line that names amp families and the genre table's row labels).
- Produces: the canonical keys `roots-country`, `blues`, `classic-rock`, `indie-alternative`, `jazz`, `metal-high-gain`, `worship-pop`, `funk-rnb` as a backticked Key column of the voicing note's genre table; every catalog note's Best with section as three bullets, `- Amp families: ...` (unchanged text), `- Genres: key, key` (keys only), and a third bullet holding the note's qualifier sentences and the `[[speaker-cab-voicing]]` link; the ranking precedence and the evaluate-first rule with the bridge table that Task 6's skill cites; `GENRE_KEYS` in the test file (the engine gets no constant).

Every string on the twenty notes' Best with lines matched a table row exactly (the one qualifier, celestion-blue's "Worship and pop at low volume", becomes `worship-pop` plus a kept sentence), so the script's mapping is one to one and idempotent. The voicing note's port bullet drops the stale Plan 1 numbers (75 mm start, 150 mm cap, 20 mm minimum) for the landed engine's (77.3 mm start, the tube table, 153.2 mm cap, 24 mm minimum, the corrected clamp remedy) and describes `--port-tube`, `--fb`, and `--port-count`. The bridge is strict on ported boxes: flat serves tight, punchy serves balanced, boomy serves big only; the reviewer should know that the site box reads punchy with every catalog speaker, so a tight target always proposes.

- [ ] **Step 1: Write the failing tests**

In `scripts/test_cabvoice.py` replace `test_catalog_best_with_uses_table_labels` (it encoded the single-line form):

<!-- code: .vault/scripts/test_cabvoice.py symbols test_catalog_best_with_uses_table_labels -->
```python
def test_catalog_best_with_uses_table_labels():
    voicing = (Path(__file__).parent.parent / "knowledge/speaker-cab-voicing.md").read_text()
    for label in AMP_FAMILIES + GENRES:
        assert f"| {label} |" in voicing, label
    for slug in cabvoice.list_speakers(CATALOG):
        text = (CATALOG / f"{slug}.md").read_text()
        best_with = text.split("## Best with", 1)[1].split("\n## ", 1)[0]
        line = next(l for l in best_with.splitlines() if l.startswith("- Amp families:"))
        assert any(f in line for f in AMP_FAMILIES), slug
        assert "[[speaker-cab-voicing]]" in best_with, slug
```
<!-- /code -->

Append at the end of the file, after one comment line `# ---- Plan 3 Task 3: canonical genre keys ----`, a blank line, and these two comment lines directly above `GENRE_KEYS`:

```python
# Mirrors the Key column of the genre table in knowledge/speaker-cab-voicing.md and
# projects/Speaker-cab-system/pipeline/catalog_genres.py.
```

<!-- code: .vault/scripts/test_cabvoice.py symbols GENRE_KEYS,test_catalog_genres_lines_use_canonical_keys -->
```python
GENRE_KEYS = ("roots-country", "blues", "classic-rock", "indie-alternative", "jazz",
              "metal-high-gain", "worship-pop", "funk-rnb")

def test_catalog_genres_lines_use_canonical_keys():
    voicing = (Path(__file__).parent.parent / "knowledge/speaker-cab-voicing.md").read_text()
    for key in GENRE_KEYS:
        assert f"| `{key}` |" in voicing, key
    for slug in cabvoice.list_speakers(CATALOG):
        text = (CATALOG / f"{slug}.md").read_text()
        best_with = text.split("## Best with", 1)[1].split("\n## ", 1)[0]
        lines = best_with.splitlines()
        assert sum(l.startswith("- Amp families: ") for l in lines) == 1, slug
        genres = [l for l in lines if l.startswith("- Genres: ")]
        assert len(genres) == 1, slug
        tokens = genres[0][len("- Genres: "):].split(", ")
        assert tokens and all(t in GENRE_KEYS for t in tokens), (slug, tokens)
        assert len(set(tokens)) == len(tokens), slug
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q -k catalog`
Expected: 1 failed (`test_catalog_genres_lines_use_canonical_keys`: no Genres line in any note and no backticked key in the voicing note), 5 passed (the replaced label test passes on both forms of the section).

- [ ] **Step 3: Replace the voicing note**

Write `knowledge/speaker-cab-voicing.md` with exactly this content (its calibration block is the one Task 1 regenerated; the date in that block is prose only, keep the mirror's):

<!-- code: .vault/knowledge/speaker-cab-voicing.md all -->
````markdown
---
name: speaker-cab-voicing
description: How a customer's rig and tonal goals become a tone target, a speaker choice, an enclosure type, and a box alignment; rules, thresholds, and model limits for the cabvoice engine
type: reference
status: unverified-starting-values
created: 2026-09-09
updated: 2026-09-11
tags: [knowledge, speaker-cab, acoustics, reference]
---

# Speaker cabinet voicing

Rules for phase 2 of the `/speaker-cab` skill. Layer 1 (this note plus
judgment) turns the intake into a tone target and a ranked speaker list.
Layer 2 (`scripts/cabvoice.py`) turns the tone target into volumes, port,
wiring, and predictions. Every value is a starting value: unverified until
listening notes from real builds say otherwise. Construction rules live in
[[speaker-cab-construction]]; per-speaker data in `knowledge/speakers/`.

## Tone target vocabulary

| Field | Values | Meaning |
|---|---|---|
| low_end | tight, balanced, big | tight = smaller box, faster and drier low mids; big = larger box, more weight and bloom under 150 Hz |
| mids | scooped, neutral, forward | how much 400 Hz to 1.5 kHz presence the speaker should add |
| top | chimey, smooth, dark | 2 kHz to 5 kHz character: bell-like and bright, rounded, or rolled off |
| breakup | early, moderate, clean | whether the speaker itself should compress and distort at gig volume |
| dispersion | focused, wide | closed back beams and projects; open back spreads and fills |
| placement | floor, raised, tilted | where the cab sits; the floor adds low end by boundary gain |

Plus `min_power_w` (1.5 x the highest rated amp power in the rig) and `impedance_options_ohm` (the amp's taps).

The customer's own tonal words (the email's `Notes:`) are read before the genre row. A word that names a vocabulary value (tight, big, dark, chimey, scooped, forward, early, clean, focused, wide) sets that field outright; a word that only leans (for example "rolled highs" against `top`) keeps the genre row's value and is recorded as the reason in the brief's tone-target table.

## Enclosure type rules

- **closed-ported** (the product default): focused dispersion, tight to balanced low end with a low-mid lift from the port, best for mic'd stages and high gain. The port tuning sits below the speaker's Fs so it adds weight rather than a boom.
- **closed**: like closed-ported with less low-mid lift; use when the customer wants the driest, punchiest response or when the port would need to be too large.
- **open**: wide dispersion, airy top, less low end (the back wave cancels the front wave below the cancellation frequency, about 370 Hz for the site's box, 6 dB per octave). Best for clean and edge-of-breakup players in rooms the cab must fill by itself.
- **semi-open**: between the two: more low end than open, still wide. Open fraction 0.25 versus 0.40.
- Choice rule: dispersion wide plus low_end not tight leads to open or semi-open; dispersion focused or low_end tight or approach high gain leads to closed-ported. Mic'd cabs prefer closed-ported. Drivers with Qts above 0.9 (the Jensen C12N at 1.02, the WGS ET65 at 0.91, and the WGS Green Beret at 1.18, as printed; the Jensen P12N sits at 0.77) prefer open or semi-open because any practical closed box makes them peaky.
- Precedence when the rules disagree: a tight low end beats wide dispersion (closed or closed-ported over open-back); a low-end shifter (baritone, 7-string, drop tunings, bass VI) beats wide and takes closed-ported at the lowest tuning in range, applied with the engine's `--fb` flag. The override may take any value in the engine's own tuning range, 45 to 90 Hz (`FB_MIN_HZ` to `FB_MAX_HZ`, the range every proposed Fb is clamped to); the engine does not check the flag, so the skill keeps it in that range. The low-end-shifter rule starts at 45 Hz, the bottom of the range, and raises it in 5 Hz steps while the port does not fit the box (a higher tuning needs a shorter port). Raising Fb does not cure a boomy sheet, and a low-end-shifter sheet needs no cure: the shifter sets `low_end` big, and boomy serves a big target whether the customer asked for big or a shifter set it (the bridge table below), so judge that sheet by its character word, which should read boomy or punchy, not by a warning. For any other target the engine's own remedy grows the box in 10 percent steps to 68 L, then lowers Fb in 5 Hz steps to 45 Hz, and the sheet warns when it still reads boomy; that warning is what step 4 of the ranking reacts to. Starting values; listening notes decide.
- Evaluate first: a standard-size order (the site's 20 x 18 x 11 in box, one driver, no size limit, no head to match) is evaluated before anything is proposed, with the site port on a ported box: `cabvoice.py evaluate --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40` (the site port of the calibration table; box and port fix Fb, the speaker sets the character) plus the order's speaker, impedance, enclosure, tone, and line. The site box is accepted when the sheet's character is the bridge word for the target's `low_end` in the table below; otherwise, or when a size limit, a pinned width, a second driver, or a low-end shifter applies, the skill runs `propose`. Open and semi-open boxes carry no character word (the estimate reports the cancellation frequency, about 370 Hz for any box near the site depth), so an open-back site box is accepted whenever the rules above chose open or semi-open; only a size limit, a pinned width, or a second driver makes it propose.

| Predicted character | Enclosure | Serves `low_end` |
|---|---|---|
| lean (Qtc below 0.6) | closed | none: propose a smaller box or a ported one |
| tight (Qtc 0.6 to 0.8) | closed | tight |
| balanced (Qtc 0.8 to 1.0) | closed | balanced |
| big (Qtc 1.0 to 1.2) | closed | big |
| peaky (Qtc above 1.2) | closed | none: open or semi-open, or a lower-Qts driver |
| flat (peak below 1 dB) | closed-ported | tight |
| punchy (peak 1 to 3 dB) | closed-ported | balanced |
| boomy (peak above 3 dB) | closed-ported | big only; for any other target the engine grows the box, then lowers Fb, and warns when it still reads boomy |
| open, cancellation frequency reported | open, semi-open | balanced with open panels, big with semi-open panels (the panel choice, not the box, sets the low end) |

## Amp families

| Family | Examples | Tendency | Speakers that suit |
|---|---|---|---|
| Blackface Fender | Deluxe Reverb, Twin, Princeton | scooped mids, bright, clean headroom | Cannabis Rex, Jensen C12N, Celestion Gold, G12H-75 Creamback |
| Tweed Fender | Deluxe 5E3, Bassman | forward mids, early amp breakup | Jensen P12N, G12H Anniversary, G12M-25 Greenback |
| Marshall | Plexi, JCM800, JTM45 | forward mids, EL34 grind | G12M-25 Greenback, G12M-65 Creamback, G12H Anniversary, Vintage 30 |
| Vox | AC15, AC30 | chime, EL84 compression | Celestion Blue, Gold, Cream, G12M-25 Greenback |
| Modern high gain | Mesa Rectifier, 5150, Friedman | tight low end, saturated | Vintage 30, G12H-75 Creamback, Swamp Thang, Veteran 30 |
| Boutique clean | Dr Z, Two-Rock, Carr | full range, dynamic | Celestion Gold, Cream, Cannabis Rex, Vintage 30 |
| Modeling and solid state | Kemper, Helix, Quilter, Tone Master | flat power section, high headroom | Tonker, Swamp Thang, Red White and Blues, G12H-75 Creamback |

Speaker names in the table are the canonical short forms used by the ranking and by every note's Amp families line; each maps to one catalog note by slug (Celestion Blue, Gold, and Cream are celestion-blue, celestion-gold, celestion-cream; G12M-25 Greenback is celestion-g12m-25-greenback; G12H Anniversary is celestion-g12h-30-anniversary; the rest match their note's `model` field). Amp type (tube, solid state, modeling) is derived from the model; ask only when the model is unknown. A combo used with an extension cab has its own speaker in parallel with the cabinet, so the combined impedance is what the amp sees; the Impedance bullet under Power and impedance carries the load rule and the taps.

## Genre and approach

| Genre or approach | Key | low_end | mids | top | breakup | dispersion |
|---|---|---|---|---|---|---|
| Roots, country, alt-country | `roots-country` | tight | neutral | smooth | moderate | focused (mic'd) or wide (unmic'd) |
| Blues | `blues` | balanced | forward | smooth | early | wide |
| Classic rock | `classic-rock` | balanced | forward | smooth | moderate | focused |
| Indie and alternative | `indie-alternative` | balanced | neutral | chimey | moderate | wide |
| Jazz | `jazz` | balanced | neutral | dark | clean | wide |
| Metal and modern high gain | `metal-high-gain` | tight | scooped | smooth | clean | focused |
| Worship and pop | `worship-pop` | balanced | neutral | chimey | clean | focused |
| Funk and R&B | `funk-rnb` | tight | neutral | chimey | clean | focused |

Approach overrides genre: clean sets breakup clean; edge of breakup sets moderate; high gain sets tight and focused.

The Key column holds the canonical genre keys: every catalog note's Genres line lists them, the skill's ranking matches the intake's genre to them, and a genre outside the table earns no genre point (map it to the nearest row by ear and say so in the brief).

## Rig adjustments

- **Pickups**: single coils push top toward smooth and mids toward neutral (they are bright already). Humbuckers push mids toward scooped and allow chimey. P90s sit between. Active pickups set breakup clean and, in the ranking, prefer speakers whose handling is at least 25 percent above `min_power_w` (a starting value; they hit the amp harder). `min_power_w` itself stays 1.5 x the rated power, so the engine's hard stop does not move.
- **Low-end shifters**: baritone, 7-string, drop tunings, and bass VI set low_end big and take closed-ported at the lowest tuning in range (`--fb 45`, raised in 5 Hz steps only while the port does not fit; see Enclosure type rules), and a 2x12 over a 1x12 when weight allows.
- **Dirt pedals**: fuzz sets top dark or smooth (fuzz fizz needs a rolled top). Overdrive is neutral. Distortion and high-gain pedals set low_end tight and dispersion focused. Boosts and EQ pedals do not change the target. A pedal-platform amp favors clean headroom and higher power handling; an amp used as the drive source favors early or moderate breakup.
- **Venue and volume**: bedroom and studio allow early breakup and low-power speakers; small club unmic'd sets dispersion wide or a 2x12; mic'd stage sets focused; large stage sets closed-ported and clean.
- **Placement**: on the floor shifts low_end one step toward tight (boundary gain adds low end). Tilted counts as raised. Raised keeps the target.
- **Jack configuration**: mono for one amp; mono with parallel out when the customer daisy-chains a second cab; stereo on a 2x12 for stereo rigs and wet-dry, which divides the box into two chambers each voiced as a 1x12.
- **Cabs loved or disliked**: a named cab tells you a speaker and an enclosure. Start the ranking from the loved cab's speaker (plus 2 in the score); the disliked cab's speaker takes minus 2 and stays in the list.

## Power and impedance

- `min_power_w` = 1.5 x the highest rated amp power among the customer's amps (`POWER_SAFETY_FACTOR`), computed by the skill and written into `tone.json`; the voicing serves the primary amp, the power rule guards against the strongest amp. The engine reads that amp's rating back as `min_power_w` / 1.5 and stops hard when total handling is below it. Warning below the target; an early-breakup target may accept it explicitly (`--accept-low-headroom`) and the acceptance goes into "Decisions locked".
- Stereo: check each side against the amp's per-channel power. For a stereo amp the intake records the per-channel rating as its rated power, so `min_power_w` / 1.5 is already the per-channel figure the engine checks each side against.
- Two drivers: parallel first, then series, whichever matches a tap. Unequal impedances get a warning (the spec's rule; the engine still lists any option that matches a tap). Sensitivity more than 2 dB apart gets a warning.
- Impedance: `impedance_options_ohm` is the amp's taps (the winding). A single driver whose impedance matches no tap is a sheet blocker; a 2:1 mismatch on a tube amp is within tolerance and is accepted with `--accept-impedance-mismatch`, recorded on the sheet as `wiring.mismatch_accepted` and in "Decisions locked"; the taps in `tone.json` are never edited to make a sheet pass. A combo used with an extension cab has its own speaker in parallel with the cabinet, so the combined parallel load (8 || 16 = 5.3 ohm) is what the amp sees; the brief's Rig block and the proposal's rig and goals state that load.
- Vintage-style 15 W to 30 W speakers are for amps up to 20 W or for two-speaker cabs; the classic AC30 into two Blues is exactly the accepted early-breakup case.

## Box alignment (Layer 2 values)

- Per-driver net volume from Thiele-Small data: Vb = Vas / alpha with alpha 1.5 (tight), 1.0 (balanced), 0.65 (big), clamped to 30 to 68 L per 12 inch driver. The clamp exists because hi-fi Qtc targets give absurd sizes for guitar drivers, which Celestion also warns about (https://celestion.com/blog/thinking-of-using-thiele-small-parameters-to-design-a-guitar-speaker-cab-think/).
- Rule-of-thumb per-driver net volume when there is no T/S data, and for every open back: 34 L (tight), 44 L (balanced), 56 L (big). The site's default box is 44 L net, so it is "balanced".
- When a speaker note lacks Qts, Vas, or Fs (only allowed with `data_status: missing`), the engine uses the rule-of-thumb volume, predicts no response, and prints the character as "unpredicted (no Thiele-Small data)" with a warning; sizes the port for air speed with an assumed Sd of 530 cm2 and Xmax of 0.8 mm (`FALLBACK_SD_CM2`, `FALLBACK_XMAX_MM`, starting values for a 12 inch guitar driver), and assumes 1.5 L of driver displacement flagged `estimated` when the note gives none (that default applies to any note without a displacement). The ranking step that reacts to a boomy warning cannot fire for these speakers; judge them by their note's Character section and the rule-of-thumb volume alone.
- Ported tuning: Fb = Fs x 0.9 (tight), 0.8 (balanced), 0.7 (big), clamped to 45 to 90 Hz. If the predicted alignment is boomy and "big" was not asked, the box grows in 10 percent steps to 68 L, then Fb drops in 5 Hz steps to 45 Hz.
- Port: one round rear port per driver in the chamber (a mono 2x12 gets two identical ports, each sized as a 1x12 port in half the chamber; `Constraints.port_count` and the `--port-count` flag, 1 or 2, override), 77.3 mm starting diameter (the 3 inch tube), one flanged end, end correction 0.85 x diameter, grown in 10 percent area steps until the worst-case air speed (full Xmax at Fb) is under 17 m/s, then snapped up to the next purchasable tube inside diameter (52.0, 77.3, 101.5, 153.2 mm, `PORT_TUBE_ID_MM`) and re-solved; the physical length is at least 24 mm (`MIN_PORT_LENGTH_MM`, the 12 mm back panel plus the 12 mm flange ring). Maximum 153.2 mm diameter (the largest tube), and a slot is capped at the same area; a port that still needs less than 24 mm at that size is clamped to 24 mm, the prediction then follows the tuning the clamped port actually gives, and the sheet warns; a larger port, a lower Fb, or a smaller box lengthens it. `--port-tube` pins one tube instead (no growth, no snap; a clamped length or an air speed over the limit becomes a warning, and the sheet records `port.pinned`); on `evaluate` the same flag is a validated `--port-diameter` (the engine treats it as the port's tube inside diameter from the table; give one or the other, not both). `--fb` exists on `propose` only; it overrides the tuning target and the sheet records `port.fb_override_hz`.
- Closed-box character by Qtc: below 0.6 lean, 0.6 to 0.8 tight, 0.8 to 1.0 balanced, 1.0 to 1.2 big, above 1.2 peaky. Ported character by peak height: below 1 dB flat, 1 to 3 dB punchy, above 3 dB boomy. Both scales are half-open intervals: a value on a boundary takes the upper word (Qtc 0.8 is balanced, 1.2 is peaky, a 3.0 dB peak is boomy).
- Open fraction of the back area: 0.40 open, 0.25 semi-open, as two horizontal panels top and bottom.
- Internal dimension advisory: no two internal dimensions within 5 percent of 1:1, 2:1, or 3:1. The site's default box trips the 2:1 width-to-depth advisory; noted, not changed.

## Speaker ranking procedure

1. Hard filters: impedance available for a matching wiring option; power rule not a hard stop; customer-supplied or chosen speaker fixed if given.
2. Score each remaining catalog speaker against the tone target using the Character and Best with sections of its note: 2 points per matching low_end, mids, top, breakup word, 1 point if the speaker is named in the rig's amp-family row above, and 1 point if the customer's genre key (the Key column of the genre table) appears on the note's Genres line (starting values), minus 2 for a disliked-cab speaker, plus 2 for a loved-cab speaker. Precedence: the amp-family table wins over a note's own Amp families line when they disagree (the line earns nothing on its own); genre points count only on canonical keys matched between the intake's genre and the note's Genres line, so a genre outside the table earns nothing.
3. Present the top three with one reason line each and the data status of each (datasheet, third-party, analog, estimated, missing). At equal score prefer, first, with active pickups, the speaker whose handling is at least 25 percent above `min_power_w`; then the one with better data.
4. Run the engine for the top choice (`evaluate` on the site box first for a standard-size order, else `propose`; see Enclosure type rules); if the sheet has blockers, or carries the engine's boomy warning (`propose` says the alignment stays boomy at the practical limits after its remedy has grown the box to 68 L and lowered Fb to 45 Hz; a big target never carries it, because boomy serves big), show the trade-off and try the next.

## Model limits

- Celestion publishes only Fs and Re for its guitar speakers. The only measured Celestion data is Voice Coil magazine's test of the Heritage G12H(55), 16 ohm (https://celestion.com/wp-content/uploads/2019/10/141.pdf): Qts 0.37 to 0.46, Vas 53 to 71 L, Xmax 0.7 mm across two samples. The Heritage G12H(55) note carries that measurement as `data_status: third-party`; the G12H Anniversary and Vintage 30 notes carry values scaled from it (`analog`); the other seven Celestion notes are `missing` and use the rule-of-thumb volumes.
- WGS publishes T/S values with inconsistent units (Vas labeled in cubic feet at values that can only be liters, Sd of 366 with no unit). Those notes are `estimated` and say what was assumed.
- The vented model (Small 1973, QL = 7) reproduces Eminence Designer's F3 within about 2 percent for three of five published designs (Beta-12A-2 at 1.75 and 1.25 cu ft, Delta-12A at 0.75 cu ft) and is 6 to 10 percent low for the two larger Delta-12A designs (2.75 cu ft at Fb 55 Hz: 56 Hz against Eminence's 61.9; 1.35 cu ft at Fb 70 Hz: 74 Hz against 78.9). Cause not identified on 2026-09-09. The closed-box check against Eminence's sealed Beta-12A-2 design (0.904 cu ft, Qtc 1.10) reads 6.6 percent low (86 Hz against 92.1). Ported peak height is read off the third-octave grid, so a design within a few tenths of a dB of a threshold can flip words (the Beta-12A-2 1.25 cu ft, 60 Hz design lands at 3.10 dB, boomy by 0.1 dB).
- The open-back estimate is a path-length cancellation frequency with a 6 dB per octave roll-off, not a dipole model. It ranks options; it does not predict a curve. Under this formula open and semi-open share the same cancellation frequency and roll-off and differ only in panel height, so the estimate cannot rank one above the other on low end; the enclosure rule above is builder lore, unverified.
- The schema holds one Thiele-Small set per note, the 8 ohm one. Eminence's 16 ohm variants differ: Texas Heat 16 ohm Fs 91 Hz, Qts 0.81, Vas 44.5 L against the note's 8 ohm 79 Hz, 0.65, 50.9 L (https://eminence.com/products/texas_heat_16) and Swamp Thang 16 ohm Fs 113 Hz, Qts 0.62, Vas 26.4 L against 97 Hz, 0.53, 41.3 L (https://eminence.com/products/swamp_thang_16), so a 16 ohm choice of either is voiced with the 8 ohm data until a per-impedance schema lands (deferred past Plan 3, see [[2026-09-11-plan-3-skill-design]] section 13). The calibration table below voices those rows the same way.
- Wall material and stiffness are not in the model. The Thiele-Small math treats the panels as rigid, so a hardwood cab and a tolex cab with the same internal volume predict identically; the engine carries the line and species in voicing.json's construction block for the generator and the sheet but uses them in no calculation. Species changes weight (densities in [[speaker-cab-construction]]), wood movement (the hardwood-line grain rule), and panel resonance, which only ears can judge; bracing is the lever, not species.
- Nothing here has been checked with a microphone. Listening notes go into the speaker notes' Field notes sections after each build.

## Calibration table

Calibration table, every number prediction_status "unverified, ears only". Generated 2026-09-11 with `evaluate` (closed, site box 472 x 421.2 x 229.4 mm internal) and `propose` (closed-ported, low_end balanced), 16 ohm where the note lists it (voiced with the note's 8 ohm T/S set, see Model limits), amp 40 W.

| Speaker | Data | Net L in site box | Closed Qtc | Closed character | Closed F3 Hz | Proposed ported net L | Fb Hz | Ported character | Notes |
|---|---|---|---|---|---|---|---|---|---|
| [[celestion-blue]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) | speaker handling 15 W is below the amp's 40 W |
| [[celestion-cream]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12-65-heritage]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 68 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12h-30-anniversary]] | analog | 42.5 | 0.755 | tight | 105 | 30.0 | 68 | punchy | speaker handling 30 W is below the amp's 40 W; celestion-g12h-30-anniversary: Thiele-Small volume 29.5 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L |
| [[celestion-g12h-75-creamback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-g12m-25-greenback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) | speaker handling 25 W is below the amp's 40 W |
| [[celestion-g12m-65-creamback]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-gold]] | missing | 42.5 |  | unpredicted (no Thiele-Small data) |  | 44.0 | 60 | unpredicted (no Thiele-Small data) |  |
| [[celestion-heritage-g12h55]] | third-party | 42.5 | 0.605 | tight | 109 | 68.0 | 45 | flat | speaker handling 30 W is below the amp's 40 W; celestion-heritage-g12h55: Thiele-Small volume 71.3 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 68.0 L |
| [[celestion-vintage-30]] | analog | 42.5 | 0.701 | tight | 105 | 37.9 | 60 | flat |  |
| [[eminence-cannabis-rex]] | datasheet | 42.0 | 0.924 | balanced | 115 | 45.5 | 77 | punchy |  |
| [[eminence-red-white-and-blues]] | datasheet | 42.0 | 1.040 | big | 114 | 66.0 | 73 | punchy | port too short (6.5 mm) for Fb 78 Hz in 66.0 L; clamped to 24 mm; a larger port, a lower Fb, or a smaller box lengthens it; port clamped at the size cap: tuned 73.5 Hz, target 78.0 Hz; lower Fb or use a smaller box |
| [[eminence-swamp-thang]] | datasheet | 41.8 | 0.747 | tight | 131 | 41.3 | 78 | flat |  |
| [[eminence-texas-heat]] | datasheet | 42.0 | 0.967 | balanced | 95 | 50.9 | 63 | punchy |  |
| [[eminence-tonker]] | datasheet | 41.8 | 0.633 | tight | 138 | 34.1 | 71 | flat |  |
| [[jensen-c12n]] | datasheet | 42.5 | 1.262 | peaky | 102 | 64.3 | 45 | boomy | jensen-c12n: Thiele-Small volume 22.6 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L; ported alignment stays boomy at the practical limits; consider a closed back or a lower-Qts driver |
| [[jensen-p12n]] | datasheet | 42.5 | 1.037 | big | 95 | 67.4 | 62 | punchy |  |
| [[wgs-et65]] | estimated | 42.5 | 1.235 | peaky | 98 | 63.4 | 49 | punchy |  |
| [[wgs-green-beret]] | estimated | 42.5 | 1.454 | peaky | 109 | 64.3 | 45 | boomy | speaker handling 25 W is below the amp's 40 W; wgs-green-beret: Thiele-Small volume 22.0 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L; ported alignment stays boomy at the practical limits; consider a closed back or a lower-Qts driver |
| [[wgs-veteran-30]] | estimated | 42.5 | 1.023 | big | 103 | 62.5 | 71 | punchy |  |

## Sources

- MaximoCabs site content: `~/ClaudeProjects/MaximoCabs/src/content/cabinets/tolex-1x12.md` and `hardwood-1x12.md`, `src/lib/quote-schema.ts`.
- Small, R. H., "Vented-Box Loudspeaker Systems", JAES 1973 (the fourth-order response and its coefficients).
- Eminence cabinet designs: https://cdn.shopify.com/s/files/1/0270/8665/1462/files/Beta_12A-2_cab.pdf and https://cdn.shopify.com/s/files/1/0270/8665/1462/files/Delta_12A_cab.pdf.
- Celestion on T/S for guitar cabs: https://celestion.com/blog/thinking-of-using-thiele-small-parameters-to-design-a-guitar-speaker-cab-think/.
- Amp family, genre, and rig tables: builder lore, unverified.
````
<!-- /code -->

- [ ] **Step 4: The catalog script**

Create `projects/Speaker-cab-system/pipeline/catalog_genres.py`:

<!-- code: .vault/projects/Speaker-cab-system/pipeline/catalog_genres.py all -->
```python
"""Rewrite each speaker note's Best with section onto canonical genre keys (Plan 3, Task 3).

The Plan 1 notes carry one bullet, "Amp families: ... Genres: <table labels>; ...
Families and genres per [[speaker-cab-voicing]]." This script splits it into
three bullets: the Amp families line (unchanged text), a Genres line holding
only the canonical keys from the voicing note's genre table, and a line with
any qualifier sentences plus the wikilink. Idempotent: a note that already
has a Genres line is left alone.

Run from the vault root:
  .venv/bin/python projects/Speaker-cab-system/pipeline/catalog_genres.py            (dry run)
  .venv/bin/python projects/Speaker-cab-system/pipeline/catalog_genres.py --apply
"""
import argparse
import re
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
DEFAULT_SPEAKERS_DIR = VAULT / "knowledge" / "speakers"
SEE = "Families and genres per [[speaker-cab-voicing]]."
GENRE_KEYS = ("roots-country", "blues", "classic-rock", "indie-alternative", "jazz",
              "metal-high-gain", "worship-pop", "funk-rnb")
# Genre table row label (knowledge/speaker-cab-voicing.md) to its key.
LABEL_TO_KEY = {
    "Roots, country, alt-country": "roots-country",
    "Blues": "blues",
    "Classic rock": "classic-rock",
    "Indie and alternative": "indie-alternative",
    "Jazz": "jazz",
    "Metal and modern high gain": "metal-high-gain",
    "Worship and pop": "worship-pop",
    "Funk and R&B": "funk-rnb",
}
FAMILIES_PREFIX = "- Amp families: "


def genre_items(text: str) -> tuple:
    """(keys, qualifier sentences) from 'Label; Label qualifier; Label'."""
    keys, qualifiers = [], []
    for item in (s.strip() for s in text.split(";")):
        label = max((l for l in LABEL_TO_KEY if item == l or item.startswith(l + " ")),
                    key=len, default=None)
        if label is None:
            raise ValueError(f"genre {item!r} matches no row of the genre table")
        key = LABEL_TO_KEY[label]
        if key not in keys:
            keys.append(key)
        rest = item[len(label):].strip()
        if rest:
            qualifiers.append(f"{key} {rest}.")
    return keys, qualifiers


def patch_section(section: str) -> str:
    lines = section.split("\n")
    if any(l.startswith("- Genres: ") for l in lines):
        return section
    idx = next(i for i, l in enumerate(lines) if l.startswith(FAMILIES_PREFIX))
    body = lines[idx][len(FAMILIES_PREFIX):]
    families, rest = body.split(" Genres: ", 1)
    m = re.match(r"(.*?)\.(?: |$)(.*)", rest, re.S)
    keys, qualifiers = genre_items(m.group(1))
    tail = m.group(2).replace(SEE, "").strip()
    third = " ".join(s for s in ([tail] + qualifiers + [SEE]) if s)
    lines[idx:idx + 1] = [FAMILIES_PREFIX + families, "- Genres: " + ", ".join(keys), "- " + third]
    return "\n".join(lines)


def patch_note(text: str) -> str:
    head, section, rest = _split(text)
    return head + patch_section(section) + rest


def _split(text: str) -> tuple:
    marker = "\n## Best with\n"
    i = text.index(marker) + len(marker)
    j = text.find("\n## ", i)
    j = len(text) if j == -1 else j
    return text[:i], text[i:j], text[j:]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--speakers-dir", default=str(DEFAULT_SPEAKERS_DIR))
    ap.add_argument("--apply", action="store_true", help="write the notes (default: dry run)")
    args = ap.parse_args(argv)
    changed = 0
    for path in sorted(Path(args.speakers_dir).glob("*.md")):
        old = path.read_text()
        new = patch_note(old)
        keys = next(l for l in new.split("\n") if l.startswith("- Genres: "))[len("- Genres: "):]
        print(f"{path.stem}: {'unchanged' if new == old else 'patched'}, genres {keys}")
        if new != old:
            changed += 1
            if args.apply:
                path.write_text(new)
    print(f"{changed} note(s) {'written' if args.apply else 'would change'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
<!-- /code -->

- [ ] **Step 5: Apply it to the catalog**

Run from the vault root:

```bash
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_genres.py
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_genres.py --apply
.venv/bin/python projects/Speaker-cab-system/pipeline/catalog_genres.py --apply
```

Expected: the first run lists every note as `patched, genres ...` and ends `20 note(s) would change`; the second writes them (`20 note(s) written`); the third prints every note `unchanged` and ends `0 note(s) written`. Check `knowledge/speakers/celestion-blue.md`: its Best with section now reads

```
- Amp families: Vox, Boutique clean up to 15 W, or two Blues under a 30 W amp (the accepted early-breakup case).
- Genres: indie-alternative, blues, worship-pop
- worship-pop at low volume. Families and genres per [[speaker-cab-voicing]].
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q`
Expected: 433 passed (432 from Task 1 plus 1).

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add knowledge/speaker-cab-voicing.md projects/Speaker-cab-system/pipeline/catalog_genres.py knowledge/speakers/*.md scripts/test_cabvoice.py
git commit -m "Speaker cab plan 3 task 3: canonical genre keys in the voicing note and every catalog note"
```


---

### Task 4: Construction note, site copy note, spec pointer

**Files:**
- Modify: `knowledge/speaker-cab-construction.md` (full replacement)
- Create: `projects/Speaker-cab-system/site-copy-notes.md`
- Modify: `projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md` (one pointer line under the Unit 3 heading)
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/knowledge/speaker-cab-construction.md`, `.vault/projects/Speaker-cab-system/site-copy-notes.md`

**Interfaces:**
- Consumes: Task 1's messages and the 24 mm minimum; Task 2's `port fit` and `port mouth` texts; the layout's slot rules (`slot_ports`, `min_internal_height_mm`).
- Produces: the construction note the skill's Phase 4 loop reads for the default slot (`--port-slot <chamber width> 40`, the width from the last sheet's `box.chamber_internal_width_mm`, two slots of (width minus 18) / 2 on a mono 2x12) and the remedy order (front slot, accept the pinned tube's clamped tuning, raise Fb with the larger tube, a larger box); the three expected `port mouth` warns (the site box's rear tube at 84 mm behind the magnet; a 1x12 front slot on the floor stiffener at 0 mm; a slot in a shallow box on the back cleat) with the per-order remedies; the site copy note for Brian; the spec's Unit 3 pointer.

- [ ] **Step 1: Replace the construction note**

Write `knowledge/speaker-cab-construction.md` with exactly this content:

<!-- code: .vault/knowledge/speaker-cab-construction.md all -->
````markdown
---
name: speaker-cab-construction
description: Construction rules and starting values for MaximoCabs guitar speaker cabinets (tolex and hardwood lines, 1x12 and 2x12, closed, closed-ported and open-back)
type: reference
status: unverified-starting-values
created: 2026-09-09
updated: 2026-09-11
tags: [knowledge, speaker-cab, woodworking, reference]
---

# Speaker cabinet construction

Starting values for the `/speaker-cab` skill and the cabinet generator, in
the same locked-constants spirit as [[woodworking-stock]]: change only with
evidence from a build, then record the change in the retrospective. Nothing
here has been verified against Brian's shop practice yet. Product facts come
from the MaximoCabs site content (`~/ClaudeProjects/MaximoCabs/src/content/cabinets/`);
everything else is general builder practice unless a source is given. The
2026-09-10 revision follows [[2026-09-10-plan-2-generator-design]]: finger
joints on both lines, a dovetail option on hardwood, no corner posts, the
grill frame on the speaker flanges, and margins the generator can assert. The 2026-09-11 revision follows [[2026-09-11-plan-3-skill-design]]: the 24 mm
minimum port length, the port mouth rule, the default front slot, and the
remedy order of the skill's port loop.

## Materials

| Material | Use | Thickness | Density | Source |
|---|---|---|---|---|
| Baltic birch plywood, 13-ply | Tolex line shell, baffle, cleats, brace, divider, shelf | 18 mm (3/4 in nominal) | 680 kg/m3 | site content; density is the common trade figure, unverified |
| Baltic birch plywood | Back panels, open-back panels, grill frame strips, port flange rings | 12 mm (1/2 in nominal) | 680 kg/m3 | starting value |
| Black walnut, resawn | Hardwood line shell | 19 mm | 610 kg/m3 | https://www.wood-database.com/black-walnut/ |
| Black cherry, resawn | Hardwood line shell | 19 mm | 560 kg/m3 | https://www.wood-database.com/black-cherry/ |
| Hard maple, resawn | Hardwood line shell | 19 mm | 705 kg/m3 | https://www.wood-database.com/hard-maple/ |
| Sapele, resawn | Hardwood line shell | 19 mm | 670 kg/m3 | https://www.wood-database.com/sapele/ |
| PVC or ABS pipe, Schedule 40 | Rear round port tubes | inside 52.0, 77.3, 101.5, 153.2 mm (outside 60.3, 88.9, 114.3, 168.3) | 1400 kg/m3 (in the mass) | [[speaker-envelopes-and-port-stock]]; which size Brian buys is not settled |

Sheet stock is 2440 x 1220 mm with a 3 mm kerf for yield, as in [[woodworking-stock]]. Hardwood shell panels are glued up from resawn boards; the generator's stock check uses 3050 x 600 mm per panel as a starting limit.

## Shell per line

- **Both lines**: top, bottom, and two sides joined at the four front-to-back corner edges. The tolex line gets finger joints; the hardwood line gets finger joints by default or through dovetails as the option. The generator models the joint so renders and STEP are truthful; the cut list keeps each panel as a rectangular blank with the joint schedule in the note.
- **Tolex line**: 18 mm birch. Recessed metal jack plate. Metal corners, black or chrome, or none. Site: "13-ply void-free Baltic birch, hand-cut finger joints".
- **Hardwood line**: 19 mm resawn, show face out; no book-matching, since the corners join on end grain and book-matching is a long-grain glue-up (Brian, 2026-09-14). A 12.7 mm (1/2 in) roundover on every outside edge by default (see Roundover). Recessed brass jack plate. No metal corners by default. Oil finish.
- **Joinery survey**: finger joints are the plurality at the top of the market and the vintage-correct choice; the through dovetail is the only structural peer for solid wood; miters and rabbets are styling or budget choices. Details and sources in [[guitar-cab-joinery-survey]].
- **Roundover**: the hardwood line's default is a 12.7 mm (1/2 in) radius on every outside edge of the shell, routed after the carcass is glued up (Brian, 2026-09-13); the tolex line has none by default. Aesthetics.roundover_mm left at None takes the line default, 0 gives sharp edges, and any other value sets the radius, which must stay under the shell thickness. The internal volume is unchanged either way.

## Joinery conventions

- **Fingers**: width half the panel thickness (9 mm on 18 mm birch, 9.5 mm on 19 mm hardwood), count the nearest odd integer to depth / width so both ends are full fingers, width recomputed as depth / count. The top and bottom panels carry a full finger at the front edge; the sides start with a gap. Trade practice runs 1/4 in fingers; the width is a parameter.
- **Dovetails** (hardwood only): tails on the side panels so a lift by the top handle loads the joint in its locked direction, pins on top and bottom, half-pins at both ends, slope 1:8, pin width half the panel thickness at the outer face, tails about 30 mm.
- **Wood movement (hardwood line)**: grain wraps around the box on all four shell panels (left to right on the top and bottom, vertical on the sides), so the corner joints are cut in end grain and every panel moves along the depth axis together; never run hardwood grain front to back, which puts the corners in long grain and sets the panels moving in different directions (Brian, 2026-09-13); expect roughly 2.6 mm (cherry), 2.8 (sapele), 2.9 (walnut), 3.7 mm (hard maple) of depth change per 4-point moisture swing flatsawn, about half quartersawn. With the grain wrapping, every cleat and a fixed baffle's dados run with the grain, so hardwood cleats are glued and screwed like the tolex line's and a fixed baffle is glued along its full dado (Brian, 2026-09-13; the earlier slotted-cleat and front-100-mm glue rules came from the front-to-back grain wording). The intake's "where it lives" answer sets the expected humidity swing.

## Baffle

- 18 mm birch on both lines. Front face 20 mm behind the front edge of the shell (the recess that holds the grill frame). Driver mounts from the front of the baffle onto T-nuts fitted from the back. Bolts M6 or 1/4-20, 6.5 mm holes on the note's bolt circle, first hole at twelve o'clock.
- **Floating (default)**: 1 mm clearance to each side, on 18 x 18 mm cleats glued to the shell, felt strip between cleat and baffle, held with screws through the cleats, removable. Site: "floating 3/4 in birch with felt isolation". Which edges carry cleats is the Aesthetics.baffle_cleat_edges option, and None takes the enclosure default: all four on a closed or closed-ported box, where the perimeter cleats hold the seal the volume model assumes, and top and bottom only on an open or semi-open box, which has no sealed volume to protect, so it takes fewer parts and leaves the baffle free at its sides. Unverified starting value pending listening notes (Brian, 2026-09-13).
- **Fixed (option)**: glued into a 6 mm deep dado in all four shell panels (three with a front slot port, where the shelf carries the baffle's bottom edge), blank 12 mm larger in width and height, no baffle cleats. On hardwood it is glued along the full dado too, since the dados run with the grain (see Wood movement).
- Driver cutout, bolt circle, bolt count, frame diameter, and magnet diameter come from the speaker note. Typical: Celestion 283 mm cutout on a 297 mm circle, Eminence 281 mm on 294 mm, Jensen 277 mm on 293.5 mm; frames 306 to 310 mm, so the flange overhangs the cutout by 11 to 15 mm; flange thickness 5 mm starting value.
- **Margins**: at least 48 mm from a cutout edge to any shell panel (grill strip 40 plus 2 x the 4 mm grill clearance below), 25 mm from a cutout edge to the brace or divider, so the two cutouts of a 2x12 sit 68 mm apart (18 plus 2 x 25). Minimum internal width = n x cutout + (n - 1) x 68 + 2 x 48, the same for mono and stereo since the divider replaces the brace (2x12 with 283 mm cutouts: 730 mm internal, 766 mm external, 30.2 in). Minimum internal height = cutout + 96, plus slot height + 18 with a front slot port.
- **Speaker envelope** (for clearance checks): behind the baffle a basket cylinder at the cutout diameter for the first 100 mm from the baffle front face, then the magnet cylinder at the note's magnet diameter plus 12 mm cover allowance (185 mm when the note has none), total length the note's depth. At least 25 mm from any envelope part to the back panel, a port tube, a cleat, a shelf, a stiffener, the brace, or the divider.

## Bracing and dividers

- Mono 2x12: one vertical 18 x 60 mm birch brace between top and bottom at the center of the baffle span, its front face 2 mm behind the baffle back, glued to top and bottom, notched around the baffle cleats (no notch with a fixed baffle).
- Stereo 2x12: a full-height 18 mm birch divider from the baffle back face to the back panel inner face replaces the brace and splits the box into two equal chambers, sealed with glue on top and bottom. The divider carries no cleats: the baffle and the back screw into its front and rear edges (cleats on its faces would crowd the 25 mm cutout margin). Each chamber's cutout sits 48 mm from the shell and 25 mm from the divider at the minimum width, any surplus split evenly. Each chamber gets its own jack plate and, when ported, its own port.
- Any shell or back panel span over 450 mm between glued members gets one 18 x 40 mm stiffener across its middle, glued flat to the panel (on a mono 2x12 that is the back panel). Hardwood shell panels get none: solid 19 mm stock needs no stiffener at these spans, and a birch stiffener glued flat would cross the grain (Brian, 2026-09-13).

## Backs and ports

- **Closed**: 12 mm birch back panel, flush with the rear edge, screwed to 18 x 18 mm cleats every 150 mm, removable. The jack plate sits in the back panel.
- **Closed-ported, rear round port**: a Schedule 40 PVC or ABS tube through the back panel with a 12 mm plywood flange ring (outside diameter tube plus 60 mm) glued to the inside face; inside diameter snapped by the voicing engine to the tube table above, length from the voicing sheet measured through the back panel and never under 24 mm (the 12 mm back panel plus the 12 mm flange ring, the engine's `MIN_PORT_LENGTH_MM`), one per driver in the chamber (a mono 2x12 gets two identical ports, each sized as a 1x12 port in half the chamber; the sheet's `port.count` and `construction.port_count` say how many). Placement order: outboard of the driver at driver height, below the driver, lower outboard corner, above the driver; the first spot with 25 mm clearance to the speaker envelope, walls, cleats, brace, divider, and jack plate wins. When no spot fits, the layout's `port fit` blocker names the tube to try next (`port fit: chamber 0 port 0: no round port of 153.2 mm fits with 25 mm clearance; the longest table tube that fits at the 24 mm minimum is 101.5 mm; raise Fb, use a smaller tube or a larger box, or a front slot`, or `...; no table tube fits; use a front slot or a larger box`; a tube of the right diameter whose port is too long reads `port fit: chamber 0 port 0: tube 101.5 x 250 mm reaches the baffle; longest tube that fits at this diameter is 155 mm; ...`) and the skill's port loop re-runs the voicing once with the named tube pinned (`--port-tube`; when only a length is named, the next tube down the table, whose smaller area needs a shorter port); when that run warns (a clamped length, an air speed over the limit) or blocks again, the remedies go to Brian in this order: the front slot below, accepting the pinned tube's clamped tuning as the sheet reports it, raising Fb with the larger tube, a larger box.
- **Closed-ported, front slot port**: the baffle stops short of the bottom panel by the slot height plus an 18 mm shelf; the shelf's front edge is flush with the baffle face, its depth equals the port length, and it doubles as the bottom baffle cleat. A slot narrower than the chamber gets two cheeks; a mono 2x12 gets two slots split by an 18 mm center cheek in line with the brace. The shelf must leave at least max(25 mm, slot height) of free depth behind it. Round rear tubes are a bass-cab convention; the published vented guitar cabs (EV TL806, Mesa Thiele) use the front slot. Default slot for the port loop (starting values): height 40 mm; width the chamber's full internal width, read from the last sheet's `box.chamber_internal_width_mm`, for a 1x12 and for each stereo chamber (no cheeks), and for a mono 2x12 two slots of (chamber width minus 18) / 2 each, split by the center cheek; so `--port-slot <width> 40`, with the external width pinned to the last sheet's (`--pinned-width <box.external_mm[0]>`) so the chamber width holds and the slot fits it exactly. The engine adds the slot's 58 mm to the height floor (40 plus the 18 mm shelf); left free, it would also re-proportion the width to hold the volume, and that never settles, since the slot width sets the port area, the port length, the shelf depth among the inside parts, the gross volume, and so the width again (the Cannabis Rex roots order: a 438.9 mm chamber rescales to 427.2, then 426.5, then 426.4, and the slot blocks every time at the layout's former 1e-6 mm tolerance). The layout trims a slot up to 1 mm wider than its chamber to the full width (`SLOT_TRIM_MM`, no cheeks); wider than that it blocks (`port fit: chamber 0: 1 slot of 439 mm do not fit the 427 mm chamber; narrow the slot or widen the box`; a mono 2x12 reads `port fit: chamber 0: 2 slots of 352 mm do not fit the 704 mm chamber with the 18 mm center cheek; narrow the slot or widen the box`), which with the width pinned happens only when a floor moved the chamber by more than 1 mm, and the skill then re-runs once more with the new chamber width; a narrower slot only gains thin cheeks. A shelf deeper than the box allows blocks with the deepest shelf that fits named (`port fit: slot shelf 220 mm deep leaves 27 mm behind it, under the 40 mm the slot needs to breathe; the deepest shelf that fits is 207 mm; lower the slot height or use a round port`, or `no shelf fits` when even 24 mm does not), so the skill lowers the slot height or takes a round port. A 40 mm slot across a 352 mm chamber is 141 cm2, above the 101.5 mm tube's 81 cm2, so the air speed stays low.
- **Port mouth**: one effective port diameter of free air in front of the inner mouth, along the port axis, to the first part that faces it (basket or magnet envelope, brace, divider, stiffener, cleat, shelf, cheek; the baffle's back face for a rear tube, the back panel's inner face for a slot); a slot's effective diameter is that of a circle with its area. The layout's `port mouth` check warns under one diameter and never blocks (`chamber 0 port 0: mouth 84 mm from the speaker 0 magnet (18 percent of the mouth), under one diameter (101.5 mm)`; the percentage is how much of the mouth the part faces, information only). Three warns are expected today, and the builder accepts or resolves each per order: the site box's own rear tube (its 101.5 mm mouth sits 84 mm behind the magnet with 18 percent of the mouth facing it: accept, or a smaller tube); every 1x12 front slot whose bottom panel needs a stiffener (the generator starts that stiffener at the shelf's rear edge flat on the floor, so it reads as a 0 mm obstruction covering about 8 percent of the mouth: move the stiffener back, or accept); and the floor-level back cleat behind a slot shelf sitting under one effective diameter of the mouth, which fires on most 2x12 slot boxes at their default depth and on shallow 1x12 ones (a deeper box, or accept). The coverage percentage is information only and never gates the warn. The choice goes into Decisions locked. The 25 mm standoff from the magnet's rear face stays the hard rule.
- **Open-back**: two horizontal 12 mm panels, top and bottom, each (1 - open fraction) x internal height / 2 tall, screwed to cleats. Open fraction 0.40 for open, 0.25 for semi-open (from [[speaker-cab-voicing]]). The jack plate sits in the upper panel by default (see Hardware, Jack plate). Stereo keeps the divider and one plate per chamber.

## Grill

- Frame from 12 x 40 mm birch strips with half-lap corners, outer size the recess opening minus 4 mm per side (room for the cloth folded double at the stapled wrap; 2 mm was not enough, Brian from experience, 2026-09-14), cloth wrapped around the frame and stapled at the back. The frame rests on the speaker flanges and on 5 mm felt spacers at its corners, so its face sits 3 mm behind the front edge; a strip may cover a flange but must clear every cutout by 4 mm. With a front slot port the frame covers only the baffle above the shelf.
- Retained with hook-and-loop strips to the baffle. Piping (optional) is glued into the corner between grill frame and shell.

## Hardware

- **Jack plate**: recessed dish plate, metal on the tolex line, brass on the hardwood line. Cutout is measured from the plate purchased; starting value 110 x 70 mm (the Marshall-style CJP-1 dish cuts 76.2 x 87.3 mm, so reconcile against the part bought). Position is Aesthetics.jack_plate_position, 25 mm clear of the nearest cleat, one per chamber; the default is the top of the upper open-back panel on an open or semi-open back, easier to reach without bending down when the cab sits on the floor, and the bottom of the back panel on a closed or closed-ported back, unchanged (Brian, 2026-09-14). Mono: one 1/4 in jack. Mono with parallel out: two jacks on one plate wired in parallel. Stereo: one plate per chamber.
- **Handle**: top-center strap handle by default on both lines (the site shows a strap on the hardwood cab too), screw pair 228.6 mm apart (Marshall style; Fender style 203.2 mm), centered on the top panel in width and depth (Brian, 2026-09-13), kept 50 mm inside the edges. The speaker pulls the loaded center of mass forward, so a cab carried by the strap hangs slightly nose-down. Recessed side handles as the option, one per side at the depth center of mass in the upper third, cutout 140 x 90 mm starting value (Penn Elcom H7154Z flange 161 x 107 mm, dish 8.5 mm). The handle check: within 15 mm of the loaded center of mass on the width axis.
- **Feet**: four rubber feet, 40 mm, inset 32 mm from the bottom corners. Tilt-back legs on the tolex line when the intake says placement is tilted: pivot screws 100 mm from the front and bottom edges, a hardware line only.
- **Corners**: metal corners on the tolex line by default (black or chrome), none on hardwood. Leg length is unpublished by every supplier, so every cutout keeps 50 mm from the external corners.
- Hardware dimensions and sources: [[speaker-envelopes-and-port-stock]].

## Tolex

- Roll widths from the site's material list: 54 in (1371.6 mm) for the British and Fender black styles, 32 in (812.8 mm) for tweed.
- Yardage = external surface area (all six faces) x 1.15 for wrap and waste, divided by the roll width, reported in metres and yards. The cut list carries this as a line item under "Materials not cut", not a part.
- Seams run along the bottom panel. Contact cement.

## Weight and center of mass

- Cabinet mass = sum over parts of volume x density (table above; the four shared corner blocks counted once) + speaker mass from the note + 1 kg hardware allowance.
- Center of mass = mass-weighted mean of part centroids, with the speaker mass placed at the baffle at the cutout center. The handle check compares its center to this point on the width axis (15 mm tolerance).
- Site reference: tolex 1x12 about 32 lb (14.5 kg) loaded, hardwood 1x12 about 38 lb (17.2 kg).

## Site defaults (calibration)

- External 20 x 18 x 11 in (508 x 457.2 x 279.4 mm), 1x12 closed-ported.
- Internal with the rules above: 472 x 421.2 x 229.4 mm, gross 45.6 L, net about 42.5 L closed and 42.1 L ported after one driver and the inside parts.
- The engine voices both lines with the tolex line's 18 mm walls; the hardwood line's 19 mm panels take about 1 percent more of the same external size, inside the model's error, so no separate voicing. The line and species travel in voicing.json's construction block so the generator picks the density and joinery.
- A slot-ported 1x12 on the site box grows from 18.0 to 18.6 in tall through the engine's height floor; a 2x12 starts at 30.2 in wide.
````
<!-- /code -->

- [ ] **Step 2: Write the site copy note**

Create `projects/Speaker-cab-system/site-copy-notes.md`:

<!-- code: .vault/projects/Speaker-cab-system/site-copy-notes.md all -->
````markdown
---
name: site-copy-notes
description: Sentences on the MaximoCabs site that the speaker cab system has overtaken or that need a check (hardwood joinery, closed-back wording, loaded weights); a note for Brian, the site itself is out of scope in this vault
type: note
created: 2026-09-11
tags: [project, speaker-cab, maximocabs, site]
---

# MaximoCabs site copy: notes for Brian

The vault does not change the site (`~/ClaudeProjects/MaximoCabs`); this note records what the Plan 2 and Plan 3 work found, per [[2026-09-11-plan-3-skill-design]] section 11. Line numbers are as of 2026-09-11.

## Wrong: hardwood joinery

`src/content/cabinets/hardwood-1x12.md`, line 33:

    joinery: "Through-tenon corner posts, glued + pinned"

The hardwood line is built with finger joints by default and through dovetails as the option, with no corner posts, since [[2026-09-10-plan-2-generator-design]] (see [[speaker-cab-construction]], Shell per line). The tolex page already reads `joinery: "Hand-cut finger joints"` (`tolex-1x12.md`, line 33) and the homepage says "Hand-cut joinery." (`src/pages/index.astro`, line 28). A row that matches the build: `joinery: "Hand-cut finger joints (through dovetails on request)"`.

## A default, not the only option: closed-back wording

Both cabinet pages, line 30:

    configuration: "1x12 closed-back, ported"

and the tolex description (`tolex-1x12.md`, line 39): "Closed-back for focused low end."

The system voices closed-ported, closed, open, and semi-open boxes and 2x12 cabinets ([[speaker-cab-voicing]], Enclosure type rules), and the homepage already promises the volume, port, and baffle designed around the rig (`index.astro`, line 24). The wording can stay as the default if the pages say so, for example `configuration: "1x12 closed-back, ported (open-back and 2x12 on request)"`.

## Verify before changing: loaded weights

`tolex-1x12.md`, line 37: `weightApprox: "~32 lb loaded"`. `hardwood-1x12.md`, line 37: `weightApprox: "~38 lb loaded (varies by species)"`.

The site-default fixture (`projects/Speaker-cab-system/fixtures/site-default/`, the 20 x 18 x 11 in tolex box with a G12H Anniversary at 4.7 kg) computes 17.0 kg, 37.5 lb, loaded: 11.3 kg of birch parts, the 4.7 kg speaker, and a 1 kg hardware allowance. That is a starting-value calculation ([[speaker-cab-construction]], Weight and center of mass), not a measurement: weigh a built tolex cab before touching the page. If the model holds, the tolex figure reads about 5.5 lb light and the hardwood figure needs its own check against the species densities.
````
<!-- /code -->

- [ ] **Step 3: Point the spec's Unit 3 at the addendum**

In `projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md`, directly after the line `## Unit 3: The `/speaker-cab` skill`, insert a blank line and then:

```markdown
> Amended 2026-09-11 by [[2026-09-11-plan-3-skill-design]]: a report module (`scripts/cabreport.py`) writes the check table and the proposal's facts, the skill keeps judgment in prose with two stops, standard-size orders are evaluated on the site box first, the port loop pins the longest fitting tube once before the trade-off stop, and there is no FreeCAD path. Where this section and the addendum differ, the addendum governs.
```

- [ ] **Step 4: Verify the notes**

Run from the vault root:

```bash
grep -cP '\x{2014}' knowledge/speaker-cab-construction.md projects/Speaker-cab-system/site-copy-notes.md
grep -c 'the longest table tube that fits at the 24 mm minimum' knowledge/speaker-cab-construction.md
grep -c 'Amended 2026-09-11' projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md
cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q -k "construction or wording"
```

Expected: `0` for both files, then `1`, then `1`, and every selected test passing (the wording tests read the notes).

- [ ] **Step 5: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add knowledge/speaker-cab-construction.md projects/Speaker-cab-system/site-copy-notes.md projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md
git commit -m "Speaker cab plan 3 task 4: construction note (port mouth, 24 mm minimum, default slot, remedy order), site copy note, spec pointer"
```


---

### Task 5: Report module, its tests, the proposal template

**Files:**
- Create: `scripts/cabreport.py`, `scripts/test_cabreport.py`, `skills/speaker-cab/templates/proposal.md`
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/scripts/cabreport.py`, `.vault/scripts/test_cabreport.py`, `.vault/skills/speaker-cab/templates/proposal.md`

**Interfaces:**
- Consumes: `cabvoice.PORT_V_MAX` (the status line reads `prediction_status` from `cab.json`, which the engine copied from `cabvoice.PREDICTION_STATUS`); a `voicing.json` and a `cab.json` as Tasks 1 and 2 write them (19 checks, the `aesthetics` block, `warnings`, `power`, `wiring`, `prediction`, `port`, `mass`, `external_in`, `external_mm`, `parts`, `hardware`); the site-default fixture for the tests.
- Produces: the CLI `scripts/cabreport.py <order-dir> [--customer NAME] [--proposal-template PATH] [--verify]`; `checks.md` with 34 rows for the site default (19 verdicts, `power`, `wiring`, `port air speed`, `alignment`, one `engine warning` per sheet warning, then the eight operator rows) and a closing line counting the rows that still read `operator`; `proposal.md` rendered from the template with the 17 facts in `FACT_KEYS` and the four slots in `SLOTS`; `--verify` exit 2 listing every missing fact and empty slot; `FIXTURE_ORDERS = ["site-default"]` in the test file, which Tasks 7 and 8 extend. Module symbols in file order: `SCRIPTS`, `VAULT`, `DEFAULT_TEMPLATE`, `KG_TO_LB`, `STOCK_SHEET_MM`, `STOCK_HARDWOOD_MM`, `NOT_CUT_STOCK`, `LEAD_TIME`, `SWATCHES`, `NO_SWATCH`, `OPERATOR_ROWS`, `OPERATOR`, `POWER_VERDICT`, `BACK_TYPE`, `CONFIGURATION`, `SLOTS`, `FACT_KEYS`, `SLOT_RE`, `TOKEN_RE`, `Row`, `load_order`, `_fmt_in`, `_external`, `_mass`, `_thickness`, `_stock_yield`, `check_rows`, `write_checks`, `swatch`, `_speaker_label`, `_hardware`, `facts`, `render_proposal`, `verify_proposal`, `main`.

Three rules the implementer and the reviewer should hold in mind: a `--verify` run writes nothing (a verify that rewrote `checks.md` would clobber the operator's judged verdicts), and `--customer` is required for a verify because the customer's name is a verified fact; every non-verify run rewrites `checks.md`; `proposal.md` is written only when absent and the run prints `left alone (delete it to regenerate)` otherwise. `power` maps the engine's `ok`, `warning`, `stop` to pass, warn, blocker; `alignment` shows the character with Fb and F3 on a ported box, F3 on a closed one, the cancellation frequency on an open one; on the hardwood line `grain and show face` is an operator row and `stock yield` counts 3050 x 600 mm glue-ups; the yield excludes tube blanks; a `|` inside a message is written as `/`. The proposal carries no predicted frequency (a test asserts it).

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_cabreport.py`:

<!-- code: .vault/scripts/test_cabreport.py all -->
```python
"""Tests for the order report module (checks.md and the proposal's facts).

Runs on the committed fixture orders' voicing.json and cab.json, copied into a
temporary order directory, so no CAD is needed.
"""
import copy
import json
import shutil
from pathlib import Path

import pytest

import cabreport

HERE = Path(__file__).resolve().parent
VAULT = HERE.parent
FIXTURES = VAULT / "projects" / "Speaker-cab-system" / "fixtures"
TEMPLATE = VAULT / "skills" / "speaker-cab" / "templates" / "proposal.md"
FIXTURE_ORDERS = ["site-default", "sample-roots-1x12", "rex-roots-1x12"]
CUSTOMER = "Site Default"


def _order(name: str, tmp_path: Path) -> Path:
    """A temporary order directory holding the fixture's two JSON files."""
    out = tmp_path / name
    out.mkdir()
    for f in ("voicing.json", "cab.json"):
        shutil.copy(FIXTURES / name / f, out / f)
    return out


def _load(order: Path) -> tuple:
    return (json.loads((order / "voicing.json").read_text()),
            json.loads((order / "cab.json").read_text()))


def _fill_slots(text: str, body: str = "Filled by the skill.") -> str:
    for name in cabreport.SLOTS:
        text = text.replace(f"<!-- slot: {name} -->\n<!-- /slot -->",
                            f"<!-- slot: {name} -->\n{body}\n<!-- /slot -->")
    return text


@pytest.mark.parametrize("name", FIXTURE_ORDERS)
def test_check_rows_follow_the_files_in_order(name, tmp_path):
    voicing, cab = _load(_order(name, tmp_path))
    rows = cabreport.check_rows(voicing, cab)
    names = [r.name for r in rows]
    n = len(cab["checks"])
    assert names[:n] == [c["name"] for c in cab["checks"]]
    assert [(r.value, r.verdict) for r in rows[:n]] == [(c["message"], c["level"]) for c in cab["checks"]]
    engine = names[n:n + 4]
    assert engine == ["power", "wiring", "port air speed", "alignment"]
    warnings = len(voicing["warnings"])
    assert names[n + 4:n + 4 + warnings] == ["engine warning"] * warnings
    assert tuple(names[n + 4 + warnings:]) == cabreport.OPERATOR_ROWS
    assert len(rows) == n + 4 + warnings + len(cabreport.OPERATOR_ROWS)
    by_name = {r.name: r for r in rows}
    assert by_name["power"].verdict == cabreport.POWER_VERDICT[voicing["power"]["status"]]
    assert by_name["power"].value == voicing["power"]["message"]
    assert by_name["alignment"].verdict == "info"
    assert voicing["prediction"]["character"] in by_name["alignment"].value
    assert all(r.verdict == "warn" and r.value in voicing["warnings"] for r in rows if r.name == "engine warning")
    operator = [r for r in rows if r.verdict == cabreport.OPERATOR]
    assert {r.name for r in operator} <= set(cabreport.OPERATOR_ROWS)
    assert by_name["weight vs limit"].value.startswith(f"{cab['mass']['total_kg']:.1f} kg")


def test_site_default_rows_are_the_expected_verdicts(tmp_path):
    voicing, cab = _load(_order("site-default", tmp_path))
    rows = {r.name: r for r in cabreport.check_rows(voicing, cab)}
    assert (rows["wiring"].value, rows["wiring"].verdict) == ("single, 16 ohm: Single driver, 16 ohm", "pass")
    assert rows["power"].verdict == "warn"
    assert rows["port air speed"].value == "2.0 m/s against the 17 m/s limit"
    assert rows["port air speed"].verdict == "pass"
    assert rows["alignment"].value == "punchy; Fb 67 Hz, F3 69 Hz"
    assert rows["stock thickness"].value == "tolex line: shell 18 mm, baffle 18 mm, back 12 mm"
    assert (rows["grain and show face"].value, rows["grain and show face"].verdict) == ("n/a, tolex line", "pass")
    assert rows["joinery fit"].value == "finger corners, floating baffle"
    assert rows["stock yield"].value.startswith("22 blanks, ")
    assert "sheets of 2440 x 1220 mm at 100 percent without nesting" in rows["stock yield"].value
    assert rows["wood movement"].value == "n/a; the climate comes from the brief"
    assert rows["transport"].value == "20 x 18 x 11 in W x H x D, 37.5 lb; the vehicle and doorway come from the brief"
    assert rows["weight vs limit"].value == "17.0 kg (37.5 lb); the limit comes from the brief"
    assert rows["size vs limit"].value == "508 x 457 x 279 mm (20 x 18 x 11 in) W x H x D; the limits come from the brief"
    assert sum(1 for r in rows.values() if r.verdict == cabreport.OPERATOR) == 7


def test_site_default_facts(tmp_path):
    voicing, cab = _load(_order("site-default", tmp_path))
    f = cabreport.facts(voicing, cab, CUSTOMER)
    assert set(cabreport.FACT_KEYS) <= set(f)
    assert f["customer"] == CUSTOMER
    assert f["order"] == "site-default"
    assert f["line_label"] == "Tolex 1x12"
    assert f["configuration"] == "1x12"
    assert f["back_type"] == "closed-back, ported"
    assert f["speaker_label"] == "Celestion G12H Anniversary"
    assert f["wiring"] == "Single driver, 16 ohm"
    assert f["external_in"] == "20 x 18 x 11 in"
    assert f["external_mm"] == "508 x 457 x 279 mm"
    assert (f["mass_kg"], f["mass_lb"]) == ("17.0", "37.5")
    assert f["finish"] == "Fender Style Black"
    assert f["grill_cloth"] == "British Small Weave Cane"
    assert f["hardware"] == "Black corners, strap handle, recessed metal jack plate, no piping, rubber feet."
    assert f["swatch_finish"] == "![Fender Style Black](images/tolex-fender-black.jpg)"
    assert f["swatch_cloth"] == "![British Small Weave Cane](images/british-small-weave-cane.jpg)"
    assert f["lead_time"] == "8 to 12 weeks from confirmed order"
    assert f["status_line"] == ("Every figure in this proposal is a design target, not a measurement. "
                                "Prediction status: unverified, ears only.")
    for key in ("f3_hz", "fb_hz", "peak_db"):
        assert f"{voicing['prediction'][key]:.0f} Hz" not in " ".join(f.values())


def test_hardwood_two_driver_open_back_labels(tmp_path):
    voicing, cab = _load(_order("site-default", tmp_path))
    cab = copy.deepcopy(cab)
    voicing = copy.deepcopy(voicing)
    cab["line"], cab["species"] = "hardwood", "black walnut"
    for d in (cab["enclosure"], voicing["enclosure"]):
        d.update(type="open", driver_count=2, chambers=2, jack_config="stereo", open_fraction=0.4)
    voicing["prediction"] = {"model": "open-back path estimate", "f_cancel_hz": 78.4,
                             "character": "open, wide dispersion, 6 dB per octave below 78 Hz relative to closed"}
    voicing.pop("port")
    voicing["warnings"] = []
    cab["aesthetics"].update(corners=None, handle="recessed-side", piping=True, feet="tilt-back")
    cab["hardware"] = [h for h in cab["hardware"] if h["item"] != "corner"]   # hardwood default: the layout emits none
    f = cabreport.facts(voicing, cab, "Pat Player")
    assert f["line_label"] == "Hardwood 2x12"
    assert f["configuration"] == "2x12 stereo"
    assert f["back_type"] == "open-back"
    assert f["speaker_label"] == "2 x Celestion G12H Anniversary"
    assert f["finish"] == "Black Walnut"
    assert f["swatch_finish"] == "![Black Walnut](images/walnut.jpg)"
    assert f["lead_time"] == "10 to 14 weeks from confirmed order"
    assert f["hardware"] == "No metal corners, recessed side handles, recessed metal jack plate, with piping, tilt-back legs."
    rows = {r.name: r for r in cabreport.check_rows(voicing, cab)}
    assert (rows["port air speed"].value, rows["port air speed"].verdict) == ("n/a", "pass")
    assert rows["alignment"].value.endswith("; cancellation frequency 78 Hz")
    assert rows["grain and show face"].verdict == cabreport.OPERATOR
    assert rows["grain and show face"].value.startswith("black walnut: ")
    assert "glue-ups of 3050 x 600 mm" in rows["stock yield"].value
    assert rows["wood movement"].value.startswith("black walnut;")
    assert "engine warning" not in rows
    voicing["enclosure"]["jack_config"] = "mono-parallel-out"
    cab["enclosure"]["jack_config"] = "mono-parallel-out"
    assert cabreport.facts(voicing, cab, "x")["configuration"] == "2x12 with parallel out"


@pytest.mark.parametrize("name", FIXTURE_ORDERS)
def test_main_writes_checks_and_proposal_then_verifies(name, tmp_path, capsys):
    order = _order(name, tmp_path)
    voicing, cab = _load(order)
    assert cabreport.main([str(order), "--customer", CUSTOMER]) == 0
    checks = (order / "checks.md").read_text()
    rows = cabreport.check_rows(voicing, cab)
    table = [l for l in checks.splitlines() if l.startswith("| ") and not l.startswith("| Check")]
    assert len(table) == len(rows)
    assert table[0].startswith("| sheet | ")
    assert checks.startswith(f"---\ntype: checks\norder: {cab['name']}\n")
    pending = sum(1 for r in rows if r.verdict == cabreport.OPERATOR)
    assert f"{pending} row(s) still read `operator`" in checks
    proposal = (order / "proposal.md").read_text()
    f = cabreport.facts(voicing, cab, CUSTOMER)
    assert all(f[k] in proposal for k in cabreport.FACT_KEYS)
    assert "\n- Price:\n" in proposal
    assert proposal.startswith("---\ntype: proposal\n")
    assert "{{" not in proposal
    for slot in cabreport.SLOTS:
        assert f"<!-- slot: {slot} -->\n<!-- /slot -->" in proposal
    # verify: fresh render fails only on the four empty slots
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--verify"]) == 2
    out = capsys.readouterr().out
    assert [l for l in out.splitlines() if l.startswith("slot ")] == [f"slot {s} empty" for s in cabreport.SLOTS]
    assert "missing fact" not in out
    (order / "proposal.md").write_text(_fill_slots(proposal))
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--verify"]) == 0
    assert "verified" in capsys.readouterr().out


def test_proposal_is_written_once_and_verify_writes_nothing(tmp_path, capsys):
    order = _order("site-default", tmp_path)
    assert cabreport.main([str(order), "--customer", CUSTOMER]) == 0
    filled = _fill_slots((order / "proposal.md").read_text(), "Custom text the skill wrote.")
    (order / "proposal.md").write_text(filled)
    judged = (order / "checks.md").read_text().replace("| operator |", "| pass: judged |")
    (order / "checks.md").write_text(judged)
    assert cabreport.main([str(order)]) == 0          # no --customer needed once the proposal exists
    out = capsys.readouterr().out
    assert "left alone" in out
    assert (order / "proposal.md").read_text() == filled
    assert "| operator |" in (order / "checks.md").read_text()   # checks.md is regenerated every run
    (order / "checks.md").write_text(judged)
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--verify"]) == 0
    assert (order / "checks.md").read_text() == judged          # verify runs write nothing
    assert (order / "proposal.md").read_text() == filled


def test_verify_fails_on_an_edited_fact_and_an_emptied_slot(tmp_path, capsys):
    order = _order("site-default", tmp_path)
    assert cabreport.main([str(order), "--customer", CUSTOMER]) == 0
    good = _fill_slots((order / "proposal.md").read_text())
    (order / "proposal.md").write_text(good.replace("20 x 18 x 11 in", "21 x 18 x 11 in"))
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--verify"]) == 2
    out = capsys.readouterr().out
    assert "missing fact external_in: 20 x 18 x 11 in" in out
    assert "1 problem(s)" in out
    emptied = good.replace("<!-- slot: alternatives -->\nFilled by the skill.\n", "<!-- slot: alternatives -->\n   \n")
    (order / "proposal.md").write_text(emptied)
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--verify"]) == 2
    assert "slot alternatives empty" in capsys.readouterr().out
    (order / "proposal.md").write_text(good.replace("<!-- slot: designed_to_do -->", "").replace("<!-- /slot -->", "", 1))
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--verify"]) == 2
    assert "slot designed_to_do missing" in capsys.readouterr().out
    problems = cabreport.verify_proposal("nothing here", cabreport.facts(*_load(order), CUSTOMER))
    assert len(problems) == len(cabreport.FACT_KEYS) + len(cabreport.SLOTS)


def test_no_swatch_on_file_warns_and_still_writes(tmp_path, capsys):
    order = _order("site-default", tmp_path)
    cab = json.loads((order / "cab.json").read_text())
    cab["aesthetics"]["grill_cloth"] = "Salt-and-pepper"
    (order / "cab.json").write_text(json.dumps(cab))
    assert cabreport.main([str(order), "--customer", "Pat Player"]) == 0
    captured = capsys.readouterr()
    assert "warning: no swatch on file for the grill cloth" in captured.err
    proposal = (order / "proposal.md").read_text()
    assert "- Grill cloth: Salt-and-pepper" in proposal
    assert "![Fender Style Black](images/tolex-fender-black.jpg)\nno swatch on file" in proposal
    assert cabreport.swatch("fender style TWEED") == "![fender style TWEED](images/fender-tweed-olive-stripe.jpg)"
    assert cabreport.swatch(None) == cabreport.NO_SWATCH
    (order / "proposal.md").write_text(_fill_slots(proposal))
    assert cabreport.main([str(order), "--customer", "Pat Player", "--verify"]) == 0


def test_input_errors_exit_1_and_write_nothing(tmp_path, capsys):
    order = _order("site-default", tmp_path)
    assert cabreport.main([str(order)]) == 1                      # proposal due, no customer
    assert "--customer is required" in capsys.readouterr().out
    assert not (order / "checks.md").exists() and not (order / "proposal.md").exists()
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--proposal-template", str(tmp_path / "none.md")]) == 1
    assert "not found" in capsys.readouterr().out
    assert not (order / "checks.md").exists()
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--verify"]) == 1   # no proposal to verify
    assert "proposal.md not found" in capsys.readouterr().out
    (order / "cab.json").unlink()
    assert cabreport.main([str(order), "--customer", CUSTOMER]) == 1
    assert "cab.json not found" in capsys.readouterr().out
    assert not (order / "checks.md").exists()
    (order / "cab.json").write_text("{not json")
    assert cabreport.main([str(order), "--customer", CUSTOMER]) == 1
    assert "unreadable" in capsys.readouterr().out
    shutil.copy(FIXTURES / "site-default" / "cab.json", order / "cab.json")
    assert cabreport.main([str(order), "--customer", CUSTOMER]) == 0
    assert cabreport.main([str(order), "--verify"]) == 1          # verify needs the customer fact
    assert "--customer is required" in capsys.readouterr().out
    with pytest.raises(ValueError, match="voicing.json not found"):
        cabreport.load_order(tmp_path / "missing")


def test_template_tokens_all_have_facts(tmp_path):
    voicing, cab = _load(_order("site-default", tmp_path))
    f = cabreport.facts(voicing, cab, CUSTOMER)
    text = cabreport.render_proposal(TEMPLATE.read_text(), f)
    assert "{{" not in text and "}}" not in text
    with pytest.raises(ValueError, match="template tokens with no fact: nope"):
        cabreport.render_proposal("{{customer}} {{nope}}", f)
    tokens = set(cabreport.TOKEN_RE.findall(TEMPLATE.read_text()))
    assert tokens == set(cabreport.FACT_KEYS) | {"order", "generated"}


def test_hardware_corners_come_from_the_hardware_list(tmp_path):
    voicing, cab = _load(_order("site-default", tmp_path))
    cab["aesthetics"]["corners"] = None       # cab.py omitted corners; the layout still built black ones
    assert cabreport.facts(voicing, cab, CUSTOMER)["hardware"].startswith("Black corners, ")
    for h in cab["hardware"]:
        if h["item"] == "corner":
            h["notes"] = h["notes"].replace("black", "chrome")
    assert cabreport.facts(voicing, cab, CUSTOMER)["hardware"].startswith("Chrome corners, ")
    cab["hardware"] = [h for h in cab["hardware"] if h["item"] != "corner"]
    assert cabreport.facts(voicing, cab, CUSTOMER)["hardware"] == (
        "No metal corners, strap handle, recessed metal jack plate, no piping, rubber feet.")


def test_accepted_impedance_mismatch_is_a_warn_wiring_row(tmp_path):
    order = _order("site-default", tmp_path)
    voicing, cab = _load(order)
    voicing["wiring"]["recommended"] = None
    voicing["wiring"]["mismatch_accepted"] = True
    voicing["wiring"]["options"][0]["matches_tap"] = False
    voicing["warnings"] += ["no wiring option matches amp taps [8]",
                            "impedance mismatch accepted: 16 ohm cabinet on amp taps [8]"]
    rows = {r.name: r for r in cabreport.check_rows(voicing, cab)}
    assert rows["wiring"].verdict == "warn"
    assert rows["wiring"].value == "single 16 ohm: no tap matches, impedance mismatch accepted"
    assert cabreport.facts(voicing, cab, CUSTOMER)["wiring"] == "Single driver, 16 ohm"
    (order / "voicing.json").write_text(json.dumps(voicing))
    assert cabreport.main([str(order), "--customer", CUSTOMER]) == 0
    assert "| wiring | single 16 ohm: no tap matches, impedance mismatch accepted | warn |" in (order / "checks.md").read_text()
    proposal = order / "proposal.md"
    assert "Single driver, 16 ohm" in proposal.read_text()
    proposal.write_text(_fill_slots(proposal.read_text()))
    assert cabreport.main([str(order), "--customer", CUSTOMER, "--verify"]) == 0
    voicing["wiring"]["mismatch_accepted"] = False
    rows = {r.name: r for r in cabreport.check_rows(voicing, cab)}
    assert (rows["wiring"].value, rows["wiring"].verdict) == ("no recommended wiring on the sheet", "warn")
    assert cabreport.facts(voicing, cab, CUSTOMER)["wiring"] == "wiring to be confirmed"


# ---- swatch table: the site's current option names and photos ----
MAXIMOCABS = Path.home() / "ClaudeProjects" / "MaximoCabs"


def test_swatches_resolve_every_site_option():
    if not MAXIMOCABS.exists():
        pytest.skip(f"{MAXIMOCABS} is absent")
    materials = MAXIMOCABS / "public" / "materials"
    assert [f for f in cabreport.SWATCHES.values() if not (materials / f).is_file()] == []
    options = []
    for page in ("tolex-1x12.md", "hardwood-1x12.md"):
        meta = cabreport.cabvoice.parse_frontmatter((MAXIMOCABS / "src" / "content" / "cabinets" / page).read_text())
        options += meta["finishOptions"] + meta["grillOptions"]
    assert options
    for o in options:
        name, path = o["name"], o["swatch"]
        assert cabreport.swatch(name) == f"![{name}](images/{cabreport.swatch_image(path.removeprefix('/materials/'))})", name
        assert cabreport.SWATCHES[name.lower()] == path.removeprefix("/materials/"), name


# ---- swatch image names: a shared basename takes its folder ----
def test_swatch_image_prefixes_a_shared_basename_with_its_folder():
    assert cabreport.swatch_image("tolex/fender-black.jpg") == "tolex-fender-black.jpg"
    assert cabreport.swatch_image("grill-cloth/fender-black.jpg") == "grill-cloth-fender-black.jpg"
    assert cabreport.swatch("Fender Style Black") == "![Fender Style Black](images/tolex-fender-black.jpg)"
    assert cabreport.swatch('Fender Style Black, 36"') == '![Fender Style Black, 36"](images/grill-cloth-fender-black.jpg)'
    assert cabreport.swatch("Black Walnut") == "![Black Walnut](images/walnut.jpg)"
    assert cabreport.swatch('Salt and Pepper, 32"') == '![Salt and Pepper, 32"](images/salt-and-pepper.jpg)'
    files = set(cabreport.SWATCHES.values())
    images = {cabreport.swatch_image(f) for f in files}
    assert len(images) == len(files)
    assert images - {Path(f).name for f in files} == {"tolex-fender-black.jpg", "grill-cloth-fender-black.jpg"}
```
<!-- /code -->

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabreport.py -q`
Expected: collection error, `ModuleNotFoundError: No module named 'cabreport'`.

- [ ] **Step 3: The proposal template**

Create `skills/speaker-cab/templates/proposal.md` (this creates the `templates/` directory Task 6 fills):

<!-- code: .vault/skills/speaker-cab/templates/proposal.md all -->
````markdown
---
type: proposal
customer: {{customer}}
order: {{order}}
generated: {{generated}}
---
<!--
MaximoCabs voice, from the site on 2026-09-11. Write the four slots in this register:
  "Custom cabinets, built to your sound"
  "We treat every order as an acoustic brief. Two 1x12 cabinets, one in tolex, one in hardwood, each tuned to the amp you actually play and the rooms you actually play in."
  "Tailored, not configured."
  "Tell us your amplifier, the style you play, and the rooms you work in. We design the internal volume, port, and baffle around it. Defaults exist; specs do not."
  "Void-free Baltic birch ply in the Tolex, solid resawn hardwood in the Hardwood. Hand-cut joinery. Felt-isolated floating baffles. Nothing decorative."
  "Every cabinet is built start-to-finish by one builder. Lead times reflect that."
Rule: nothing in this proposal is a measured claim. Say what the cabinet is designed for; never quote a frequency, a decibel, or a test result.
Edit only between the slot markers. Every line outside them is a fact from cab.json and voicing.json that `cabreport.py --verify` checks.
-->

# Your MaximoCabs {{line_label}}

Prepared for {{customer}}.

## 1. Your rig and goals

<!-- slot: rig_and_goals -->
<!-- /slot -->

## 2. The recommended cabinet

- Cabinet: {{line_label}}, {{back_type}}
- Configuration: {{configuration}}
- Speaker: {{speaker_label}}
- Impedance and wiring: {{wiring}}
- External size, width x height x depth: {{external_in}} ({{external_mm}})
- Estimated weight, loaded: {{mass_lb}} lb ({{mass_kg}} kg)

<!-- slot: why_this_cabinet -->
<!-- /slot -->

## 3. What it is designed to do

<!-- slot: designed_to_do -->
<!-- /slot -->

## 4. Alternatives considered

<!-- slot: alternatives -->
<!-- /slot -->

## 5. Finishes

- Finish: {{finish}}
- Grill cloth: {{grill_cloth}}
- Hardware: {{hardware}}

<!-- Swatches: copy the files named below from ~/ClaudeProjects/MaximoCabs/public/materials/ (tolex/, grill-cloth/, wood/) into this order's images/ folder. A name prefixed with its folder is the file <folder>/<rest of the name> copied under the prefixed name: images/tolex-fender-black.jpg is tolex/fender-black.jpg. -->
{{swatch_finish}}
{{swatch_cloth}}

## 6. Lead time and price

- Lead time: {{lead_time}}
- Price:

{{status_line}}
````
<!-- /code -->

- [ ] **Step 4: The module**

Create `scripts/cabreport.py`:

<!-- code: .vault/scripts/cabreport.py all -->
```python
"""Order report for the /speaker-cab skill: the check table and the proposal's
facts from an order's voicing.json and cab.json.

The skill's judgment lives in prose; every number a deliverable quotes is
written here from the two files the engine and the generator produced, so
nothing in checks.md or proposal.md restates a number by hand.

    .venv/bin/python scripts/cabreport.py <order-dir> [--customer NAME]
                                          [--proposal-template PATH] [--verify]

Without --verify a run writes checks.md (always) and proposal.md (only when
the file does not exist; delete it to regenerate). With --verify a run
writes nothing: it checks that every fact string is still present in
proposal.md and that every prose slot holds text.

Exit 0 written or verified; 1 input error, nothing written (a missing or
unreadable file, a missing key, a missing --customer when proposal.md is to
be written or verified); 2 the proposal failed --verify, every missing fact
and empty slot listed on stdout.
"""
import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import cabvoice

SCRIPTS = Path(__file__).resolve().parent
VAULT = SCRIPTS.parent
DEFAULT_TEMPLATE = VAULT / "skills" / "speaker-cab" / "templates" / "proposal.md"
KG_TO_LB = 2.20462
STOCK_SHEET_MM = (2440.0, 1220.0)      # mirrors cablayout.STOCK_SHEET_MM (ply)
STOCK_HARDWOOD_MM = (3050.0, 600.0)    # mirrors cablayout.STOCK_HARDWOOD_MM (glue-ups)
NOT_CUT_STOCK = ("pvc", "abs")         # materials that are not sheet or board stock

# Lead times copied from the MaximoCabs site content on 2026-09-11
# (~/ClaudeProjects/MaximoCabs/src/content/cabinets/*.md); change with the site.
LEAD_TIME = {
    "tolex": "8 to 12 weeks from confirmed order",
    "hardwood": "10 to 14 weeks from confirmed order",
}

# Site option name (lower case) to the swatch file under the MaximoCabs repo's
# public/materials/ tree; the proposal references images/<swatch_image> and
# the skill copies the file there. The full names are the finishOptions and
# grillOptions of the site's src/content/cabinets/tolex-1x12.md and
# hardwood-1x12.md as of 2026-09-13, roll widths and quotes included; the short
# legacy keys stay only where the same material still has a photo. The species
# keys are the layout's.
SWATCHES = {
    'fender style black vinyl tolex, 54"': "tolex/fender-black.jpg",
    'fender style smooth blonde vinyl tolex, 54"': "tolex/fender-smooth-blonde.jpg",
    'fender style smooth brown vinyl tolex, 54"': "tolex/fender-smooth-brown.jpg",
    'fender style tweed olive stripe, 32"': "tolex/fender-tweed-olive-stripe.jpg",
    'british style black levant vinyl tolex, 54"': "tolex/british-black-levant.jpg",
    'british red garnet levant, 54"': "tolex/british-red-garnet-levant.jpg",
    'british style white levant vinyl tolex, 54"': "tolex/british-white-levant.jpg",
    'vox-hiwatt style black vinyl tolex, 54"': "tolex/vox-hiwatt-black.jpg",
    'fender style black, 36"': "grill-cloth/fender-black.jpg",
    'fender style oxblood, 36"': "grill-cloth/fender-oxblood.jpg",
    'fender style black/white/silver, 36"': "grill-cloth/fender-black-white-silver.jpg",
    'fender style beige brown (wheat), 36"': "grill-cloth/fender-wheat.jpg",
    'british style small weave cane, 32"': "grill-cloth/british-small-weave-cane.jpg",
    'british style black, 48" (marshall replacement)': "grill-cloth/british-black.jpg",
    'british brown diamond, 30"x36"': "grill-cloth/british-brown-diamond.jpg",
    'salt and pepper, 32"': "grill-cloth/salt-and-pepper.jpg",
    "fender style black": "tolex/fender-black.jpg",
    "fender style tweed": "tolex/fender-tweed-olive-stripe.jpg",
    "british style red": "tolex/british-red-garnet-levant.jpg",
    "fender style oxblood": "grill-cloth/fender-oxblood.jpg",
    "fender style beige": "grill-cloth/fender-wheat.jpg",
    "british small weave cane": "grill-cloth/british-small-weave-cane.jpg",
    "british brown diamond": "grill-cloth/british-brown-diamond.jpg",
    "walnut": "wood/walnut.jpg",
    "black walnut": "wood/walnut.jpg",
    "cherry": "wood/cherry.jpg",
    "black cherry": "wood/cherry.jpg",
    "hard maple": "wood/maple.jpg",
    "sapele": "wood/sapele.jpg",
}
NO_SWATCH = "no swatch on file"

OPERATOR_ROWS = ("stock thickness", "grain and show face", "joinery fit", "stock yield",
                 "wood movement", "transport", "weight vs limit", "size vs limit")
OPERATOR = "operator"
POWER_VERDICT = {"ok": "pass", "warning": "warn", "stop": "blocker"}
BACK_TYPE = {"closed-ported": "closed-back, ported", "closed": "closed-back",
             "open": "open-back", "semi-open": "semi-open"}
CONFIGURATION = {"mono": "2x12 mono", "mono-parallel-out": "2x12 with parallel out",
                 "stereo": "2x12 stereo"}
SLOTS = ("rig_and_goals", "why_this_cabinet", "designed_to_do", "alternatives")
FACT_KEYS = ("customer", "line_label", "configuration", "back_type", "speaker_label", "wiring",
             "external_in", "external_mm", "mass_kg", "mass_lb", "finish", "grill_cloth",
             "hardware", "swatch_finish", "swatch_cloth", "lead_time", "status_line")
SLOT_RE = re.compile(r"<!-- slot: (\w+) -->(.*?)<!-- /slot -->", re.S)
TOKEN_RE = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class Row:
    name: str
    value: str
    verdict: str


def load_order(order_dir) -> tuple:
    """(voicing, cab) from <order-dir>/voicing.json and cab.json; ValueError when either is missing or unreadable."""
    order_dir = Path(order_dir)
    out = []
    for name in ("voicing.json", "cab.json"):
        path = order_dir / name
        if not path.is_file():
            raise ValueError(f"{path} not found")
        try:
            out.append(json.loads(path.read_text()))
        except (OSError, ValueError) as e:
            raise ValueError(f"{path} unreadable: {e}") from e
    return out[0], out[1]


def _fmt_in(x: float) -> str:
    s = f"{x:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _external(cab: dict) -> tuple:
    """('20 x 18 x 11 in', '508 x 457 x 279 mm') for W x H x D."""
    inches = " x ".join(_fmt_in(v) for v in cab["external_in"]) + " in"
    mm = " x ".join(f"{v:.0f}" for v in cab["external_mm"]) + " mm"
    return inches, mm


def _mass(cab: dict) -> tuple:
    kg = float(cab["mass"]["total_kg"])
    return kg, kg * KG_TO_LB


def _thickness(parts: list, names) -> str:
    for p in parts:
        if any(p["name"] == n or p["name"].startswith(n + "_") for n in names):
            return f"{p['blank_mm'][0]:g} mm"
    return "n/a"


def _stock_yield(cab: dict) -> str:
    parts = [p for p in cab["parts"]
             if not any(m in p["material"].lower() for m in NOT_CUT_STOCK)]
    blanks = sum(p["qty"] for p in parts)
    area = sum(p["qty"] * p["blank_mm"][1] * p["blank_mm"][2] for p in parts) / 1e6
    if cab["line"] == "hardwood":
        w, l = STOCK_HARDWOOD_MM
        stock = f"glue-ups of {w:.0f} x {l:.0f} mm"
    else:
        w, l = STOCK_SHEET_MM
        stock = f"sheets of {w:.0f} x {l:.0f} mm"
    sheets = area / (w * l / 1e6)
    return (f"{blanks} blanks, {area:.2f} m2 of blanks, {sheets:.1f} {stock} "
            "at 100 percent without nesting")


def check_rows(voicing: dict, cab: dict) -> list:
    """The check table: cab.json verdicts, then the engine rows, then the operator rows."""
    rows = [Row(c["name"], c["message"], c["level"]) for c in cab["checks"]]
    power = voicing["power"]
    rows.append(Row("power", power["message"], POWER_VERDICT.get(power["status"], "warn")))
    rec = voicing["wiring"].get("recommended")
    if rec:
        rows.append(Row("wiring", f"{rec['name']}, {rec['impedance_ohm']:g} ohm: {rec['jack_text']}",
                        "pass" if rec.get("matches_tap") else "warn"))
    elif voicing["wiring"].get("mismatch_accepted"):
        options = ", ".join(f"{o['name']} {o['impedance_ohm']:g} ohm" for o in voicing["wiring"]["options"])
        rows.append(Row("wiring", f"{options}: no tap matches, impedance mismatch accepted", "warn"))
    else:
        rows.append(Row("wiring", "no recommended wiring on the sheet", "warn"))
    port = voicing.get("port") or {}
    speed = port.get("air_speed_ms")
    if speed is None:
        rows.append(Row("port air speed", "n/a", "pass"))
    else:
        rows.append(Row("port air speed", f"{speed:.1f} m/s against the {cabvoice.PORT_V_MAX:g} m/s limit",
                        "pass" if speed <= cabvoice.PORT_V_MAX else "warn"))
    pred = voicing["prediction"]
    character = pred.get("character", "unpredicted")
    if "f3_hz" in pred:
        tuned = f"Fb {pred['fb_hz']:.0f} Hz, " if "fb_hz" in pred else ""
        value = f"{character}; {tuned}F3 {pred['f3_hz']:.0f} Hz"
    elif "f_cancel_hz" in pred:
        value = f"{character}; cancellation frequency {pred['f_cancel_hz']:.0f} Hz"
    elif "fb_hz" in pred:
        value = f"{character}; Fb {pred['fb_hz']:.0f} Hz"
    else:
        value = character
    rows.append(Row("alignment", value, "info"))
    for w in voicing.get("warnings", []):
        rows.append(Row("engine warning", w, "warn"))
    line, species = cab["line"], cab.get("species")
    parts, aes = cab["parts"], cab["aesthetics"]
    inches, mm = _external(cab)
    kg, lb = _mass(cab)
    rows.append(Row("stock thickness", f"{line} line: shell {_thickness(parts, ('side_left', 'side_right', 'top', 'bottom'))}, "
                    f"baffle {_thickness(parts, ('baffle',))}, back {_thickness(parts, ('back',))}", OPERATOR))
    if line == "hardwood":
        rows.append(Row("grain and show face", f"{species}: show face out, "
                        "grain wrapping around the box on every shell panel, never front to back (see the plan)", OPERATOR))
    else:
        rows.append(Row("grain and show face", "n/a, tolex line", "pass"))
    rows.append(Row("joinery fit", f"{aes['corner_joint']} corners, {aes['baffle_mount']} baffle", OPERATOR))
    rows.append(Row("stock yield", _stock_yield(cab), OPERATOR))
    rows.append(Row("wood movement", f"{species if species else 'n/a'}; the climate comes from the brief", OPERATOR))
    rows.append(Row("transport", f"{inches} W x H x D, {lb:.1f} lb; the vehicle and doorway come from the brief", OPERATOR))
    rows.append(Row("weight vs limit", f"{kg:.1f} kg ({lb:.1f} lb); the limit comes from the brief", OPERATOR))
    rows.append(Row("size vs limit", f"{mm} ({inches}) W x H x D; the limits come from the brief", OPERATOR))
    return rows


def write_checks(rows: list, path, name: str) -> int:
    """Write checks.md; return how many rows still read `operator`."""
    pending = sum(1 for r in rows if r.verdict == OPERATOR)
    lines = ["---", "type: checks", f"order: {name}", f"generated: {datetime.date.today().isoformat()}",
             "---", "", f"# Check table - {name}", "",
             "| Check | Value | Verdict |", "|---|---|---|"]
    for r in rows:
        lines.append(f"| {r.name} | {r.value.replace('|', '/')} | {r.verdict} |")
    lines += ["", f"{pending} row(s) still read `{OPERATOR}`: replace each with a verdict line judged "
                  "against the brief; the file is final when none remains.", ""]
    Path(path).write_text("\n".join(lines))
    return pending


def swatch_image(file: str) -> str:
    """The images/ name for a SWATCHES file: its basename, or its folder and
    basename joined by a hyphen when another SWATCHES file shares the
    basename (tolex/fender-black.jpg is images/tolex-fender-black.jpg, since
    grill-cloth/fender-black.jpg exists too)."""
    path = Path(file)
    shared = {f for f in SWATCHES.values() if Path(f).name == path.name}
    return f"{path.parent.name}-{path.name}" if len(shared) > 1 else path.name


def swatch(name) -> str:
    """A markdown image line for a site option name, or the no-swatch text."""
    file = SWATCHES.get((name or "").strip().lower())
    return f"![{name}](images/{swatch_image(file)})" if file else NO_SWATCH


def _speaker_label(voicing: dict) -> str:
    labels = [f"{s['brand']} {s['model']}" for s in voicing["speakers"]]
    count = voicing["enclosure"]["driver_count"]
    if count == 1 or not labels:
        return labels[0] if labels else "speaker to be confirmed"
    if len(set(labels)) == 1:
        return f"{count} x {labels[0]}"
    return " and ".join(labels)


def _hardware(cab: dict) -> str:
    aes = cab["aesthetics"]
    corner = next((h for h in cab["hardware"] if h["item"] == "corner"), None)
    finish = corner["notes"].split(";")[0].split(", ")[1] if corner else None    # "metal corner, black; keep-out ..."
    items = [f"{finish} corners" if finish else "no metal corners",
             "strap handle" if aes["handle"] == "strap" else "recessed side handles"]
    plate = next((h for h in cab["hardware"] if h["item"] == "jack plate"), None)
    if plate:
        items.append(plate["notes"].split(",")[0].replace(" plate", " jack plate"))
    items.append("with piping" if aes.get("piping") else "no piping")
    items.append("rubber feet" if aes["feet"] == "rubber" else "tilt-back legs")
    text = ", ".join(items)
    return text[0].upper() + text[1:] + "."


def facts(voicing: dict, cab: dict, customer: str) -> dict:
    """Every fact the proposal template carries, as strings."""
    enc = cab["enclosure"]
    line = cab["line"]
    inches, mm = _external(cab)
    kg, lb = _mass(cab)
    finish = (cab["aesthetics"]["tolex_color"] if line == "tolex"
              else (cab.get("species") or "").title()) or "finish to be confirmed"
    cloth = cab["aesthetics"]["grill_cloth"] or "grill cloth to be confirmed"
    rec = voicing["wiring"].get("recommended")
    options = voicing["wiring"]["options"]
    if not rec and voicing["wiring"].get("mismatch_accepted") and len(options) == 1:
        rec = options[0]        # an accepted mismatch on a single driver: the one way to wire it
    return {
        "customer": customer,
        "order": cab["name"],
        "generated": datetime.date.today().isoformat(),
        "line_label": f"{line.title()} {enc['driver_count']}x12",
        "configuration": "1x12" if enc["driver_count"] == 1 else CONFIGURATION[enc["jack_config"]],
        "back_type": BACK_TYPE[enc["type"]],
        "speaker_label": _speaker_label(voicing),
        "wiring": rec["jack_text"] if rec else "wiring to be confirmed",
        "external_in": inches,
        "external_mm": mm,
        "mass_kg": f"{kg:.1f}",
        "mass_lb": f"{lb:.1f}",
        "finish": finish,
        "grill_cloth": cloth,
        "hardware": _hardware(cab),
        "swatch_finish": swatch(finish),
        "swatch_cloth": swatch(cloth),
        "lead_time": LEAD_TIME[line],
        "status_line": "Every figure in this proposal is a design target, not a measurement. "
                       f"Prediction status: {cab['prediction_status']}.",
    }


def render_proposal(template_text: str, facts: dict) -> str:
    """Fill every {{token}} in the template; ValueError on a token with no fact."""
    unknown = sorted({m.group(1) for m in TOKEN_RE.finditer(template_text)} - set(facts))
    if unknown:
        raise ValueError(f"template tokens with no fact: {', '.join(unknown)}")
    return TOKEN_RE.sub(lambda m: str(facts[m.group(1)]), template_text)


def verify_proposal(text: str, facts: dict) -> list:
    """Problems with a proposal: missing fact strings and missing or empty slots."""
    problems = [f"missing fact {k}: {facts[k]}" for k in FACT_KEYS if facts[k] not in text]
    found = {m.group(1): m.group(2) for m in SLOT_RE.finditer(text)}
    for name in SLOTS:
        if name not in found:
            problems.append(f"slot {name} missing")
        elif not found[name].strip():
            problems.append(f"slot {name} empty")
    return problems


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Check table and proposal facts for a speaker cab order.")
    ap.add_argument("order_dir", help="order directory holding voicing.json and cab.json")
    ap.add_argument("--customer", metavar="NAME", help="customer name for the proposal (required to write or verify it)")
    ap.add_argument("--proposal-template", metavar="PATH", default=str(DEFAULT_TEMPLATE),
                    help="proposal template (default skills/speaker-cab/templates/proposal.md)")
    ap.add_argument("--verify", action="store_true",
                    help="verify the existing proposal.md instead of writing; exit 2 on a failure")
    args = ap.parse_args(argv)
    order = Path(args.order_dir)
    try:
        voicing, cab = load_order(order)
        rows = check_rows(voicing, cab)
        proposal = order / "proposal.md"
        if args.verify:
            if not args.customer:
                raise ValueError("--customer is required to verify the proposal")
            if not proposal.is_file():
                raise ValueError(f"{proposal} not found")
            problems = verify_proposal(proposal.read_text(), facts(voicing, cab, args.customer))
            for p in problems:
                print(p)
            print(f"{proposal}: {'verified' if not problems else f'{len(problems)} problem(s)'}")
            return 2 if problems else 0
        due = not proposal.exists()
        if due and not args.customer:
            raise ValueError("--customer is required to write proposal.md")
        template = Path(args.proposal_template)
        if due and not template.is_file():
            raise ValueError(f"proposal template {template} not found")
        f = facts(voicing, cab, args.customer) if due else None
        text = render_proposal(template.read_text(), f) if due else None
    except KeyError as e:
        print(f"input error: missing key {e} in voicing.json or cab.json (regenerate them with the Plan 3 engine and cab.py)")
        return 1
    except (ValueError, TypeError, OSError) as e:
        print(f"input error: {e}")
        return 1
    try:
        pending = write_checks(rows, order / "checks.md", cab["name"])
        print(f"{order / 'checks.md'}: {len(rows)} rows, {pending} still read {OPERATOR}")
        if due:
            proposal.write_text(text)
            for label, key in (("finish", "swatch_finish"), ("grill cloth", "swatch_cloth")):
                if f[key] == NO_SWATCH:
                    print(f"warning: {NO_SWATCH} for the {label}", file=sys.stderr)
            print(f"{proposal}: written")
        else:
            print(f"{proposal}: left alone (delete it to regenerate)")
    except OSError as e:
        print(f"input error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```
<!-- /code -->

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabreport.py -q`
Expected: 11 passed.

- [ ] **Step 6: Run it on the site default and read the output**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
.venv/bin/python scripts/cabreport.py projects/Speaker-cab-system/fixtures/site-default --customer "Site Default"; echo "exit $?"
.venv/bin/python scripts/cabreport.py projects/Speaker-cab-system/fixtures/site-default --customer "Site Default" --verify; echo "exit $?"
```

Expected: `projects/Speaker-cab-system/fixtures/site-default/checks.md: 34 rows, 7 still read operator`, `.../proposal.md: written`, `exit 0`; then four problems (the four empty slots) and `exit 2`, since no prose has been written. Read `checks.md`: the `port mouth` row warns, `spans` warns, `power` warns with `handling 30 W is under the 45 W target (1.5 x amp power)`, `wiring` passes with `single, 16 ohm: Single driver, 16 ohm`, `alignment` reads `punchy; Fb 67 Hz, F3 69 Hz`, and the operator rows carry their measured values. Then remove the two files, since the site-default fixture ships without them (the dry-run fixtures are the orders that carry judged and filled ones):

```bash
rm projects/Speaker-cab-system/fixtures/site-default/checks.md projects/Speaker-cab-system/fixtures/site-default/proposal.md
git status --short projects/Speaker-cab-system/fixtures/site-default
```

Expected: nothing listed.

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cabreport.py scripts/test_cabreport.py skills/speaker-cab/templates/proposal.md
git commit -m "Speaker cab plan 3 task 5: cabreport.py writes the check table and the proposal's facts"
```


---

### Task 6: The skill: SKILL.md, the brief and listening-notes templates, carve-outs, vault instructions, order STEP ignore lines, symlink

**Files:**
- Create: `skills/speaker-cab/SKILL.md`, `skills/speaker-cab/templates/brief.md`, `skills/speaker-cab/templates/listening-notes.md`
- Modify: `skills/furniture/SKILL.md` (the `description` line), `skills/3d-model/SKILL.md` (the `description` line), `CLAUDE.md` (two bullets), `.gitignore` (two lines appended)
- Create outside the repository: the symlink `~/.claude/skills/speaker-cab`
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/skills/speaker-cab/SKILL.md`, `.vault/skills/speaker-cab/templates/brief.md`, `.vault/skills/speaker-cab/templates/listening-notes.md`; the edit pairs below are recorded in `.vault/plan/skill-edits.md`

**Interfaces:**
- Consumes: Tasks 1 and 2 (the flags, check order, and messages the skill quotes), Task 3 (the canonical keys and the ranking precedence it cites), Task 4 (the default front slot its loop step 4 passes to `--port-slot`, the port mouth warns it expects), Task 5 (`scripts/cabreport.py` and `skills/speaker-cab/templates/proposal.md`, which this task does not create).
- Produces: the installed `/speaker-cab` skill that Tasks 7 and 8 run; the two prose templates; the carve-outs that route guitar cabinets here; the ignore lines that keep an order's STEP out of git.

- [ ] **Step 1: Create the skill**

Create `skills/speaker-cab/SKILL.md` with exactly this content:

<!-- code: .vault/skills/speaker-cab/SKILL.md all -->
````markdown
---
name: speaker-cab
description: Use when the user asks to design, voice, quote, or build a guitar speaker cabinet (guitar cab, 1x12, 2x12, extension cab, voicing a cab, a MaximoCabs order). For other furniture or woodworking use the furniture skill; for 3D-printable parts use the 3d-model skill.
---

# Design a Guitar Speaker Cabinet (MaximoCabs order workflow)

Run one MaximoCabs order end to end with Brian as the operator: intake
from a quote email or an interview, a voiced enclosure Brian approves,
the CAD package from the generator, a check table, a customer proposal,
and after the build the listening-notes retrospective. Forked from the
furniture skill (same brief, plan, build, check, export discipline)
with a voicing phase in front. Judgment (intake, tone target, ranking,
trade-offs, proposal wording) is prose here and in
[[speaker-cab-voicing]] and [[speaker-cab-construction]]; every number
in a deliverable is written by `scripts/cabvoice.py`, the order's
`cab.py`, or `scripts/cabreport.py`. All modeling in mm; the customer
sees inches beside mm.

## Backend choice

build123d through `scripts/cabmodel.py`, always, driven by the order's
`cab.py`. There is no FreeCAD path for a cabinet: a CAD-layer failure
that repeats identically is a defect in `scripts/cabmodel.py` or
`scripts/cablayout.py`, fixed in the landed file and its mirror under
`projects/Speaker-cab-system/pipeline/` with a test, never worked
around inside an order.

## Prerequisites (check before an order)

- Interpreter: `/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python`
  (the vault venv). Every command below runs from the vault root
  `/home/brian/ClaudeProjects/3d-modeling-brain`. No GUI, no MCP tools.
- Tools in `scripts/`: `cabvoice.py` (`propose`, `evaluate`, `list`),
  `cablayout.py` and `cabmodel.py` (driven by the order's `cab.py`),
  `cabreport.py` (check table and proposal facts), `render_stl.py`.
- Knowledge: [[speaker-cab-voicing]] (tone vocabulary, enclosure
  rules, amp families, genre table with its canonical keys, ranking
  procedure, calibration table), [[speaker-cab-construction]]
  (materials, joinery, margins, ports, the default front slot, the port
  remedy order, hardware), `knowledge/speakers/<slug>.md` (the catalog;
  `/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py list`
  prints the slugs).
- Templates: `skills/speaker-cab/templates/brief.md`, `proposal.md`,
  `listening-notes.md`; the per-order `cab.py` template is
  `projects/Speaker-cab-system/fixtures/site-default/cab.py`.
- Swatches (optional): `~/ClaudeProjects/MaximoCabs/public/materials/`
  (`tolex`, `grill-cloth`, `wood`). Without the repo the proposal
  carries "no swatch on file" lines and still verifies.

Exit codes, shared by `cabvoice.py`, `cab.py`, and `cabreport.py`:

| Exit | Meaning |
|---|---|
| 0 | written, or every check passes or warns |
| 1 | input error, nothing written: fix the input (a tone value, a slug, a tube size, a missing file or flag) |
| 2 | blockers, files still written (`cabvoice.py`, `cab.py`); the proposal failed `--verify` (`cabreport.py`); argparse usage errors also exit 2 |

## Phase 1 - Intake

Source: a pasted MaximoCabs quote email or a conversation. The site's
quote wizard sends plain text: the first line carries the customer's
name, email, and any phone, then one block per brief section in the
brief's order (Order, Amps, Guitars, Pedals, Music and use, Tonal goals,
Physical, Connections, Aesthetics, Speaker). Each row is one brief field
under the brief's name for it (the brief leaves amps unlabeled, so they
arrive as `Amp 1`, `Amp 2`, with `(primary)` after the primary; the
finish row is labeled `Tolex color` or `Wood species` to match the
line); a brief line holding several fields (Cabs loved / disliked;
Piping, corners, logo, notes) arrives as one row per field,
so filling the brief is transcription (a multi-line answer continues on
lines indented deeper than its row, never at heading level). Driver
count reads `1x12` or `2x12` where the brief wants 1 or 2. `(not asked)`
means the customer left it blank: state the assumption exactly as for a
missing answer. On a 1x12's Jack configuration row and a tolex cab's
Where it lives row, `(not asked)` means the field does not apply.
`Not sure (assume mic'd)` records the mic'd assumption. The Genre line
is the customer's words; match its canonical key here. An email from
before the wizard uses fixed labels instead: `Cabinet:` (tolex-1x12 or
hardwood-1x12), `Finish:`, `Grill:`, `Speaker:`, `Hardware:` (corners,
handle, jack plate, piping), then `--- Use case ---` with `Amps:`,
`Style:`, `Venue:`, `Notes:`, where `Notes:` usually holds the tonal
goals.

1. Create `projects/Cab-<Customer>-<NxS>-<line>/` (example
   `Cab-Smith-1x12-tolex`; Brian may substitute a code for the surname)
   and copy `skills/speaker-cab/templates/brief.md` there as `brief.md`,
   its frontmatter `status` set to `intake`.
2. Fill the Rig block. Every field stays present even when empty, so a
   missing answer is visible. Amp type (tube, solid state, modeling) is
   derived from the model; ask only when the model is unknown. The
   primary amp is the one the voicing serves; the others are checked
   for compatibility.
3. State every assumption instead of asking about it. Ask ONLY
   load-bearing follow-ups, in one batch: the primary amp's rated power
   and taps when the model is unknown, a size or weight limit that
   would bind, the jack configuration on a 2x12, a customer-supplied
   speaker's impedance. Stop for the batch only when it is not empty.
4. Fill the Site-form gaps line: what this intake needed that the quote
   form does not ask. The wizard asks every Rig block group, so this is
   usually "none"; an old-format email still lacks guitars, pedals, jack
   configuration, and placement. Changing the site is out of scope.

Under the vault's agent policy a subagent may read the catalog for the
Phase 2 ranking and return the scored table; only conclusions enter the
brief.

## Phase 2 - Voicing

No CAD before Brian approves this phase.

1. **Tone target.** Derive the eight fields from the Rig block with the
   rules in [[speaker-cab-voicing]] (the customer's own tonal words
   first, then amp family, genre and approach, pickups, dirt pedals,
   venue and mic'd or not, placement: on the floor shifts `low_end` one
   step toward tight, tilted counts as raised). A customer word that
   names a vocabulary value sets that field outright; a word that only
   leans keeps the genre row's value and becomes the field's reason line
   (the note's Tone target vocabulary section). Write the table in the
   brief with one reason line per field, then `tone.json` in the order
   directory:

   ```json
   {"low_end": "tight", "mids": "neutral", "top": "smooth",
    "breakup": "moderate", "dispersion": "focused", "placement": "floor",
    "min_power_w": 33, "impedance_options_ohm": [8]}
   ```

   `min_power_w` is 1.5 x the highest rated amp in the rig, computed
   here; the engine stops hard when speaker handling is under that
   amp's rated power and warns under `min_power_w`. A `breakup: early`
   target may accept the warning with `--accept-low-headroom`; write
   the acceptance into Decisions locked. `impedance_options_ohm` stays
   the amp's taps (the winding); for a combo's extension jack the brief's
   Rig block states the combined load the amp sees (its own speaker in
   parallel with the cabinet, 8 || 16 = 5.3 ohm) and the proposal's
   `rig_and_goals` slot repeats it. The engine's mismatch check reads
   the cabinet alone, so the combined load (8 || 8 = 4 ohm on an 8 ohm
   winding) is not an engine event: record it in the Rig block and in
   Decisions locked, and raise a combined load beyond 2:1 on a tube amp
   at stop one.
2. **Ranking.** Score the catalog by the note's Speaker ranking
   procedure: Character words against the target, the amp-family row
   (the table wins over a note's own Amp families line), the genre key
   on the note's Genres line. Keys are exactly `roots-country`, `blues`,
   `classic-rock`, `indie-alternative`, `jazz`, `metal-high-gain`,
   `worship-pop`, `funk-rnb`; a genre outside the table earns nothing.
   Present the top three with points, matched keys, one reason line,
   and each note's data status. A customer-chosen or supplied speaker
   is fixed; a supplied speaker without a datasheet gets the nearest
   catalog analog and a warning that reaches the sheet and the proposal.
3. **Back type.** From the note's choice rule: a tight low end beats
   wide dispersion (closed or ported over open-back); a low-end shifter
   (baritone, 7-string, drop tunings, bass VI) beats wide and takes the
   lowest tuning in range through `--fb` (45 Hz, raised in 5 Hz steps
   only while the port does not fit; the engine's range is 45 to 90 Hz).
   Write the choice and reason.
4. **Engine run.** A standard-size order (the site's 20 x 18 x 11 in box
   and no size limit) is evaluated first; on a ported box the site port
   (the 101.5 mm tube at 40 mm, the calibration port) goes with it:

   ```bash
   cd /home/brian/ClaudeProjects/3d-modeling-brain
   /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py evaluate --speaker <slug> --impedance <ohm> \
     --enclosure closed-ported --tone projects/Cab-<...>/tone.json --line <line> [--species <species>] \
     --internal 472 421.2 229.4 --port-diameter 101.5 --port-length 40 \
     --name Cab-<...> --out projects/Cab-<...>/ [--accept-impedance-mismatch]
   ```

   The evaluate command carries no `--jack` and runs mono (the flag's
   default; a 2x12 adds `--jack` as in propose). `--name` is the order
   directory's basename. Exit 2 here means blockers, handled as under
   propose below; the impedance blocker (`no wiring option matches the
   amp's impedance taps`, a 16 ohm driver against taps `[8]`) fires on
   this first run and presents three options: accept the mismatch with
   `--accept-impedance-mismatch` when it is 2:1 on a tube amp (the sheet
   then warns and records `wiring.mismatch_accepted`), the
   matching-impedance variant of the same speaker, or a different
   speaker; record the choice in Decisions locked and re-run the same
   command with the flag. Never edit the taps in `tone.json` to make a
   sheet pass.

   Write the evaluate result (character, Fb, F3, peak, warnings) into
   the brief's evaluate-first paragraph under Voicing decision before
   propose runs, because propose overwrites `voicing.json` and
   `voicing.md`. Accept the site box when the sheet's character is the
   bridge word for the target's `low_end` in the note's Enclosure type
   rules. Otherwise, or when a size limit, a head to match, a 2x12, or a
   low-end shifter applies, propose:

   ```bash
   cd /home/brian/ClaudeProjects/3d-modeling-brain
   /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabvoice.py propose --speaker <slug> --impedance <ohm> \
     --enclosure closed-ported --tone projects/Cab-<...>/tone.json \
     --jack mono --line <line> --name Cab-<...> --out projects/Cab-<...>/ \
     [--species <species>] [--pinned-width <mm>] [--max-external W H D] \
     [--port-diameter <mm>] [--port-slot W H] [--port-tube <mm>] [--fb <hz>] \
     [--port-count <n>] [--accept-low-headroom] [--accept-impedance-mismatch]
   ```

   `--speaker` repeats for two drivers; `--jack stereo` splits the box
   into two chambers; `--pinned-width` matches a head (external width =
   head width + 0 to 10 mm); `--max-external` is the customer's limit;
   `--port-tube` pins one of the 52.0, 77.3, 101.5, 153.2 mm tubes;
   `--fb` overrides the tuning; `--port-count` sets ports per chamber.
   Exit 2 means blockers: present the trade-off the sheet names (a
   smaller box raises Qtc toward big or peaky, a different speaker,
   different wiring, a relaxed limit) and record Brian's choice before
   re-running; the impedance blocker takes the three options given under
   the evaluate command. Record the final command verbatim in the brief.

   When the proposal's character also misses the bridge word, whether
   or not a warning says why, present it at stop one as the closest this
   driver reaches, with the reading and the warning when there is one
   (the 30 L floor clamped the volume), beside the alternatives:
   the closed box, run as the same propose command with `--enclosure
   closed` and a scratch `--out` outside the order directory so its
   character reads from its own sheet and the proposal's sheet stays,
   and, only when the customer has not fixed the speaker (step 2's rule
   governs), the next-ranked speaker; Brian chooses at stop one.
5. **Reading.** Write the plain-language reading of `voicing.md` into
   the brief: what the alignment character, F3 or cancellation
   frequency, wiring, power result, and each warning mean for this
   player. Never write into `voicing.md`; every engine run regenerates
   it. Every predicted number is unverified, ears only; say so.
6. **Stop one.** Present the tone target, the ranking, the back type,
   and the reading. Brian approves or redirects; write the approval as
   a dated line in Decisions locked and set the brief's `status` to
   `voicing-approved`.

## Phase 3 - Plan

- Parts in build order: shell (top, bottom, two sides), baffle, cleats,
  brace or divider, back panel or open-back panels, port tube and
  flange ring or slot shelf and cheeks, grill frame, hardware. The
  layout kernel produces them; list them so Brian can object first.
- Joinery per connection from [[speaker-cab-construction]]: finger
  joints on both lines, through dovetails as the hardwood option; the
  baffle floating on cleats (default) or fixed in a 6 mm dado; the
  divider without cleats.
- Grain and show faces on the hardwood line: grain wrapping around the
  box on all four shell panels (left to right on top and bottom,
  vertical on the sides, never front to back), the species; no
  book-matching (the corners join on end grain, and book-matching is a
  long-grain glue-up).
- Hardware positions: one jack plate per chamber, the strap handle
  centered on the top panel (or recessed side handles), corners, feet
  or tilt-back legs, piping. Port location from the sheet; the port
  lines and the box size are provisional until the Phase 4 port loop
  closes.
- Aesthetics block: copy
  `projects/Speaker-cab-system/fixtures/site-default/cab.py` into the
  order directory as `cab.py` and edit its `AESTHETICS` constants
  (`corner_joint`, `baffle_mount`, `baffle_cleat_edges`,
  `jack_plate_position`, `handle`, `corners`, `piping`, `feet`,
  `tolex_roll_in`, `tolex_color`, `grill_cloth`, `head_width_mm`,
  `roundover_mm`; left at None, `baffle_cleat_edges` is all four
  baffle cleats on a closed or closed-ported box and top and bottom
  only on an open or semi-open one, `jack_plate_position` is the top
  of the upper open-back panel on an open or semi-open box and the
  bottom of the back on a closed or closed-ported one, and
  `roundover_mm` is a 1/2 in roundover on hardwood and none on
  tolex, with 0 turning it off). `handle` and `jack_plate_position`
  are Brian's picks every order, the defaults above being a starting
  point rather than something read from the customer's answers:
  confirm both with him before locking the layout. Reduce the module
  docstring to one line naming the order (the template's copy
  instructions are dropped). Everything below the docstring stays
  unchanged; a hardware qualifier the constants cannot hold survives
  in the brief only (its `notes` row, or Brian's own words).

Write the plan into the brief and present it briefly; no stop.

## Phase 4 - Build loop

Run the layout first, then the CAD; read every verdict line.

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-<...>/cab.py            # layout verdicts only, nothing written
EXPORT=1 /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-<...>/cab.py   # CAD verdicts, cab.step, images/, cutlist, cab.json
```

`EXPORT=1` writes `cab.json`, `cab.step`, `cutlist.md`, `cutlist.csv`,
and `images/cab-iso.png`, `cab-front.png`, `cab-top.png`,
`cab-right.png`, `cab-exploded.png` next to `cab.py` (`CAB_OUT=<dir>`
redirects); when it exits 0 with that package on disk, set the brief's
`status` to `built`. View each render with the Read tool before
continuing; a subagent may inspect them and report. `TMP_STL=<path>`
writes an STL for `scripts/render_stl.py <stl> <png> [elev,azim ...]`
when another angle is needed. None of the five renders shows the back
face, which carries the jack plate and, on a rear-ported cabinet, the
port, so on every closed-back cabinet add the STL to the export run
(written into the order directory; the vault ignores
`projects/Cab-*/*.stl` as it does the STEP) and render a rear view
(`0,90`; the front is `0,-90`), then view it with the other five:

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
TMP_STL=projects/Cab-<...>/cab.stl EXPORT=1 /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python projects/Cab-<...>/cab.py
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/render_stl.py projects/Cab-<...>/cab.stl projects/Cab-<...>/images/cab-rear.png 0,90
```

The port loop, on a `port fit` blocker from the plain `cab.py` run. The
blocker's message takes one of five forms, and each names the next step:

1. `port fit: chamber 0 port 0: no round port of 153.2 mm fits with 25 mm
   clearance; the longest table tube that fits at the 24 mm minimum is
   101.5 mm; raise Fb, use a smaller tube or a larger box, or a front
   slot`: re-run the same engine command with `--port-tube 101.5` (the
   named tube) added, then `cab.py` again.
2. `port fit: chamber 0 port 0: tube 101.5 x 250 mm reaches the baffle;
   longest tube that fits at this diameter is 155 mm; ...` (or `finds no
   spot with 25 mm clearance`): the tube seats but its port is too long
   for the box; re-run with the next tube down the table pinned
   (`--port-tube`; a smaller area needs a shorter port at the same
   tuning), then `cab.py` again.
3. `port fit: chamber 0 port 0: no round port of 101.5 mm fits with 25 mm
   clearance; no table tube fits; use a front slot or a larger box`: no
   automatic re-run; go to the stop below with the front slot and a
   larger box.
4. `port fit: slot shelf 220 mm deep leaves 27 mm behind it, under the
   40 mm the slot needs to breathe; the deepest shelf that fits is 207 mm;
   lower the slot height or use a round port` (or `no shelf fits`): no
   automatic re-run; the stop offers a lower slot height (`--port-slot W
   <h>`), a round port, or a deeper box.
5. `port fit: chamber 0: 1 slot of 472 mm do not fit the 352 mm chamber;
   narrow the slot or widen the box` (a mono 2x12 reads `2 slots of ...
   with the 18 mm center cheek`): the chamber moved by more than the 1 mm
   the layout trims (a floor lifted it; the slot run's `--pinned-width`
   holds the width itself); re-run once with `--pinned-width` kept and
   the slot width recomputed from the new sheet's
   `box.chamber_internal_width_mm` (the full width for one slot, (width
   minus 18) / 2 each for two), then `cab.py` again.

After an automatic re-run (forms 1, 2, and 5): when the new plain `cab.py`
run has no blocker and the sheet carries no port warning (one or two
lines for a clamped length, `port too short ... clamped to 24 mm` and
`port clamped at the 24 mm minimum with the pinned ... tube` for the one
event; an air speed over the limit), continue to the CAD run. Otherwise
stop and present these remedies, in this order:

1. The front slot, `--port-slot <width> 40 --pinned-width <external width>`:
   the width the sheet's `box.chamber_internal_width_mm`, or two slots
   of (width minus 18) / 2 on a mono 2x12, and the external width the
   sheet's `box.external_mm[0]`, the construction note's default, each
   rounded to 0.1 mm (the JSON holds unrounded floats; the layout's 1 mm
   trim means the rounding never blocks). The pin holds the chamber so
   the slot fits it exactly, since a free width re-proportions under the
   slot's shelf and never settles; a slot up to 1 mm over the chamber is
   trimmed to the full width by the layout.
2. The pinned tube's clamped tuning, accepted as the sheet reports it.
3. Fb raised with the larger tube (`--port-tube` and `--fb`, within the
   engine's 45 to 90 Hz), listed only when the port-fit line was form 2
   (the larger tube seats at some length) and the target Fb has headroom
   under 90 Hz; otherwise the stop lists three remedies.
4. A larger box: where `--max-external` or a pinned width limited it,
   relax that flag. On an unconstrained order no propose flag grows the
   box (the engine sizes it from Vas and the alignment), so it grows only
   with `low_end` one step toward big in `tone.json` and a propose
   re-run, which changes the voicing and goes back through stop one.

Brian picks; run that command, record the trade-off and the choice in
the brief, and continue. Each form gets one automatic re-run per order;
a blocker after it is a stop. When the loop changes the port type or the
box after stop one, record it in Trade-offs presented and Decisions
locked, rewrite the plan's port line, and re-present the changed box at
stop two, the package review, not at a third stop.

Any other blocker (net volume off the sheet, an impossible box, a power
stop, a width floor over a limit, magnet to back, interference) stops
with the trade-off its message names; Brian's choice goes into
Trade-offs presented and Decisions locked, then the engine and `cab.py`
run again. The exception is a `net volume` blocker beside a `port fit`
blocker whose message says the port was not built: it is consequential,
clears with the port, and the port loop runs alone on that pair. Exit 1
is an input error: fix the input, never the tool. A
build123d exception that repeats identically is a library defect (see
Backend choice), not something to route around.

## Phase 5 - Check table

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabreport.py projects/Cab-<...>/ --customer "<Customer>"
```

writes `checks.md` on every run from `voicing.json` and `cab.json`: the
layout and CAD verdicts verbatim, the engine rows (power, wiring, port
air speed, alignment, each warning), then the operator rows with their
measured values and the verdict `operator`. Replace every `operator`
with a verdict line judged against the brief:

| Row | Judge against |
|---|---|
| stock thickness | [[speaker-cab-construction]]; nominal is not actual, Brian measures the stock before cutting joinery sized to it |
| grain and show face | the Phase 3 plan; hardwood line only (on tolex the tool writes `pass`, n/a, so a tolex order has 7 operator rows and a hardwood order 8) |
| joinery fit | fingers and dovetails cut to measured thickness, test cut first |
| stock yield | the blank count and area against the sheets Brian has, 3 mm kerf, no nesting assumed |
| wood movement | hardwood plus the brief's "where it lives" answer: the grain wrapping around the box, cleats and a fixed baffle glued full length with the grain |
| transport | the brief's vehicle and doorway against the external size and the mass in lb |
| weight vs limit | the brief's weight limit against the mass in kg and lb |
| size vs limit | the brief's size limits and the head to match against the external size |

The file is final when no `operator` remains; rewrite the tool's footer
line to say so: ``0 row(s) still read `operator`: every operator row
judged against the brief on <date>; the file is final.`` (`--verify` reads
`proposal.md` only, never that line). Report anything unfixable
without changing the customer's requirements; never silently alter a
limit or a dimension Brian or the customer set.

Every `cabreport.py` run without `--verify` rewrites `checks.md` from the
two JSON files (a `--verify` run writes nothing), so judge the operator
rows only after the last engine and `cab.py` run, and judge them again
after any regeneration. Warn rows are not operator rows: each warn the
order keeps (a `port mouth` warn is expected on the site box's rear tube,
on a 1x12 front slot, and on the floor-level back cleat behind a slot
shelf, which fires on most 2x12 slot boxes at their default depth and on
shallow 1x12 ones, see [[speaker-cab-construction]]; `spans`, `power`,
and engine warnings likewise) gets a dated acceptance line in Decisions
locked, or a re-run that removes it. One accepted event may produce
several warn rows (an accepted impedance mismatch gives the `wiring` row
plus two `engine warning` rows); one dated acceptance line in Decisions
locked covers all of them.

## Phase 6 - Export and proposal

The package is on disk from Phase 4. The Phase 5 `cabreport.py` run also
writes `proposal.md` from `skills/speaker-cab/templates/proposal.md` when
the file is absent and never overwrites one. To regenerate it after a
re-run, delete `proposal.md` and run `cabreport.py` again; that run
rewrites `checks.md` too, so the operator rows are judged again. The
module fills the facts (customer, line, configuration, back type,
speaker, wiring, external size in inches and mm, mass in kg and lb,
finish, grill cloth, hardware, swatches, lead time, status line);
predicted frequencies never enter the proposal.

1. Fill the four prose slots between their `<!-- slot: name -->` and
   `<!-- /slot -->` markers, nothing outside them: `rig_and_goals` (the
   rig and goals in the customer's words; for a combo's extension jack
   it names the combined parallel load the amp sees, as the brief's Rig
   block states it), `why_this_cabinet` (speaker
   and back type, one reason each), `designed_to_do` (plain language,
   "designed for" wording only, never a measured claim), `alternatives`
   (the speaker lines from the ranking, one each, plus one line for a
   construction alternative the port loop presented, when there was
   one). Use the site's voice; the
   template's header comment carries the samples. Leave the `Price:`
   line for Brian.
2. Copy the swatches the proposal names from the `tolex/`,
   `grill-cloth/`, or `wood/` subfolder of
   `~/ClaudeProjects/MaximoCabs/public/materials/` into
   `projects/Cab-<...>/images/`. A name prefixed with its folder is the
   file `<folder>/<rest of the name>` copied under the prefixed name:
   `images/tolex-fender-black.jpg` is `tolex/fender-black.jpg` (the
   `grill-cloth/` folder has a `fender-black.jpg` too).
3. Verify; exit 2 lists every missing fact string and every empty slot,
   fixed inside the slots, never in the facts:

   ```bash
   cd /home/brian/ClaudeProjects/3d-modeling-brain
   /home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python scripts/cabreport.py projects/Cab-<...>/ --customer "<Customer>" --verify
   ```

## Phase 7 - Handoff

- Update the brief: Artifacts (every path), Decisions locked (dated
  lines for the voicing approval and each trade-off), Outcome.
- Write `projects/Cab-<...>/.claude/context-check/last-handoff.md` with
  the order's state, the exact commands run, and a "Decisions already
  locked" block.
- Commit with explicit paths (never `git add -A`; another session may
  share the tree) and push. `cab.step` is regenerated by `cab.py` and
  stays out of git (the vault ignores `projects/Cab-*/*.step`).

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  git add projects/Cab-<...>/brief.md projects/Cab-<...>/tone.json projects/Cab-<...>/voicing.json projects/Cab-<...>/voicing.md projects/Cab-<...>/cab.py projects/Cab-<...>/cab.json projects/Cab-<...>/checks.md projects/Cab-<...>/cutlist.md projects/Cab-<...>/cutlist.csv projects/Cab-<...>/proposal.md projects/Cab-<...>/images projects/Cab-<...>/.claude/context-check/last-handoff.md
  git commit -m "Cab <Customer> <NxS> <line>: order package" -m "<the session's attribution trailers>"
  git push origin main
  ```

- **Stop two.** Brian reviews `checks.md`, the renders, and
  `proposal.md`, fills the `Price:` line, and sends the proposal.
  Record his edits in Decisions locked, set the brief's `status` to
  `proposed`, and commit and push again.

## Phase 8 - After the build

- Copy `skills/speaker-cab/templates/listening-notes.md` to
  `knowledge/learnings/cab-<customer>-<config>.md` and fill it with
  Brian: amp and settings, guitar, pedals in use, volume level, room;
  low end, mids, top, breakup onset, dispersion; the customer's words;
  Brian's words; whether the prediction held (agree, partly, disagree)
  with one reason.
- Append the same notes, dated, to the Field notes section of the
  speaker's note in `knowledge/speakers/`.
- Promote any corrected construction default into
  [[speaker-cab-construction]] and any voicing rule that moved into
  [[speaker-cab-voicing]]; update memory when a rule changes.
- Fill the brief's Outcome and the retrospective's site-form gaps; once
  the cabinet has shipped and the listening notes are written, set the
  brief's `status` to `delivered`.
- Commit the retrospective, the speaker note, any promoted rule, the
  memory file, and the brief with explicit paths, the message ending
  with the session's attribution trailers, and push:

  ```bash
  cd /home/brian/ClaudeProjects/3d-modeling-brain
  git add knowledge/learnings/cab-<customer>-<config>.md knowledge/speakers/<slug>.md knowledge/speaker-cab-construction.md knowledge/speaker-cab-voicing.md memory/project-speaker-cab-system.md projects/Cab-<...>/brief.md
  git commit -m "Cab <Customer> <NxS> <line>: listening notes and retrospective" -m "<the session's attribution trailers>"
  git push origin main
  ```

## Error handling

- Exit 1 from any tool is an input error (a tone value outside the
  vocabulary, an unknown slug, a tube outside the table, a missing
  file, a missing `--customer`): fix the input; never patch a tool for
  an order.
- Exit 2 from `cabvoice.py` or `cab.py` is a blocker whose message
  names the trade-off: present it, record the choice, re-run. Never
  retry the identical failing command blindly.
- Exit 2 from `cabreport.py --verify`: edit the proposal inside its
  slots until the listed facts are back and no slot is empty.
- A `cabreport.py` run without `--verify` overwrites a judged
  `checks.md`; judge the operator rows again from the brief rather than
  restoring the old file, since the values may have moved.
- A build123d exception from `cab.py`: reproduce it with the order's
  `voicing.json`, fix `scripts/cabmodel.py` or `scripts/cablayout.py`
  with a test through the mirror discipline, re-run. No FreeCAD.
- Missing Thiele-Small data (`data_status: missing`): the engine
  degrades to rule-of-thumb volumes and labels every number; say so in
  the reading and in the proposal's alternatives.
````
<!-- /code -->

- [ ] **Step 2: Create the brief template**

Create `skills/speaker-cab/templates/brief.md`:

<!-- code: .vault/skills/speaker-cab/templates/brief.md all -->
````markdown
---
name: <cab-customer-nxs-line>
description: MaximoCabs order brief for <Customer>, a <NxS> <line> cabinet, <back type>, <speaker>
type: order
status: intake | voicing-approved | built | proposed | delivered
created: <YYYY-MM-DD>
customer: <Customer>
line: tolex | hardwood
configuration: 1x12 | 2x12-mono | 2x12-parallel-out | 2x12-stereo
tags: [order, speaker-cab, maximocabs]
---

# Order: <Customer>, <NxS> <line>

Source: <pasted quote email dated YYYY-MM-DD | interview on YYYY-MM-DD>.
Design rules: [[speaker-cab-voicing]], [[speaker-cab-construction]].

## Order

- Customer: <name>
- Contact: <email, phone>
- Line: <tolex | hardwood>
- Driver count: <1 | 2>
- Back type asked: <closed-ported | open | semi-open | recommend>

## Rig block

Every field stays in this list even when empty; an empty value means the customer was not asked or did not say.

- **Amps** (one line per amp; the primary amp is the one the voicing serves)
  - <model>: rated <W> W, taps <ohm list>, <head | combo>, primary: <yes | no>, type <tube | solid state | modeling> (derived from the model), family <blackface Fender | tweed Fender | Marshall | Vox | modern high gain | boutique clean | modeling>
- **Guitars**
  - Pickups and output: <single coil | P90 | humbucker | active>
  - Low-end shifters: <none | baritone | 7-string | drop tunings | bass VI>
- **Pedals**
  - Dirt: <fuzz | overdrive | distortion, models>
  - Boosts and EQ: <>
  - Drive source: <pedal platform | amp drive>
- **Music and use**
  - Genre: <customer's words> (canonical key: <roots-country | blues | classic-rock | indie-alternative | jazz | metal-high-gain | worship-pop | funk-rnb | none>)
  - Approach: <clean | edge of breakup | high gain>
  - Typical venue: <>
  - Typical volume: <>
  - Mic'd or filling the room: <mic'd | room>
  - Placement: <floor | raised | tilted>
- **Tonal goals**
  - Customer's words: <verbatim>
  - Reference records or players: <>
  - Cabs loved: <> / disliked: <>
- **Physical**
  - Weight limit: <kg / lb | none>
  - Size limits: <W x H x D | none> (vehicle: <>)
  - Dimensions to match: <head width and depth | existing cabs | none>
  - Where it lives (hardwood line, wood movement): <climate, heated or not>
- **Connections**
  - Jack configuration: <mono | mono with parallel out | stereo (2x12 only)>
- **Aesthetics**
  - Wood species or tolex color: <>
  - Grill cloth: <>
  - Piping: <yes | no>; corners: <black | chrome | none>; handle: <strap | recessed side>; jack plate: <recessed | flush>; logo: <>
- **Speaker**
  - <catalog slug at <8 | 16> ohm | customer supplied: <model, impedance, datasheet link> | recommend>

## Assumptions stated

- <one line per assumption, with the reason>

## Follow-ups asked

- <one line per load-bearing question, with the answer and date; "none" when the batch was empty>

## Tone target

| Field | Value | Reason |
|---|---|---|
| low_end | <tight / balanced / big> | <> |
| mids | <scooped / neutral / forward> | <> |
| top | <chimey / smooth / dark> | <> |
| breakup | <early / moderate / clean> | <> |
| dispersion | <focused / wide> | <> |
| placement | <floor / raised / tilted> | <> |
| min_power_w | <1.5 x the highest rated amp> | <amp, rated W> |
| impedance_options_ohm | <taps> | <primary amp's taps> |

Written to `tone.json` on <date>.

## Speaker ranking

| Candidate | Points | Matched keys | Data status | Reason |
|---|---|---|---|---|
| <slug> | <n> | <low_end, mids, family, genre ...> | <datasheet / third-party / analog / estimated / missing> | <one line> |
| <slug> | <n> | <> | <> | <> |
| <slug> | <n> | <> | <> | <> |

Chosen: <slug> at <ohm> ohm. <one line why; "fixed by the customer" when chosen or supplied>

## Back type

<closed-ported | closed | open | semi-open>: <reason from the choice rule; note the precedence used when rules conflicted>

## Voicing decision

- Mode: <evaluate on the site box | propose>
- Engine command (verbatim):

  ```bash
  <the exact cabvoice.py command that produced voicing.json>
  ```

- Reading: <plain-language reading of voicing.md for this player: alignment character, F3 or cancellation frequency, wiring, power result, each warning; every number unverified, ears only>
- Approved by Brian on <date>: <yes | redirected: what changed>

## Plan

- Parts in build order: <>
- Joinery per connection: <finger | dovetail; baffle floating | fixed; divider>
- Grain and show faces (hardwood): <>
- Hardware positions: <jack plate(s), handle, corners, feet or tilt-back legs, piping>
- Port location: <rear round | front slot>
- Aesthetics block written into `cab.py` on <date>

## Trade-offs presented

- <date>: <blocker or warning> presented with <options shown>; Brian chose <choice>; command re-run: <verbatim>

## Decisions locked

- <date>: voicing approved (<speaker>, <back type>, <mode>)
- <date>: <each trade-off choice, each accepted warning>

## Artifacts

- `projects/<Cab-...>/tone.json`, `voicing.json`, `voicing.md`
- `projects/<Cab-...>/cab.py`, `cab.json`, `cab.step` (regenerated, not committed)
- `projects/<Cab-...>/checks.md`, `cutlist.md`, `cutlist.csv`
- `projects/<Cab-...>/proposal.md`, `images/`
- Retrospective: `knowledge/learnings/cab-<customer>-<config>.md` (after the build)

## Site-form gaps

- <what this intake needed that the quote form does not ask; "none" if nothing>

## Outcome

- <date>: <proposal sent | cabinet built | delivered; price line filled by Brian; what changed after stop two>
````
<!-- /code -->

- [ ] **Step 3: Create the listening-notes template**

Create `skills/speaker-cab/templates/listening-notes.md`:

<!-- code: .vault/skills/speaker-cab/templates/listening-notes.md all -->
````markdown
---
name: cab-<customer>-<config>
description: Listening notes and retrospective for the <Customer> <NxS> <line> cabinet (<speaker>, <back type>), what the prediction said, what the ears heard, what to promote
type: learning
created: <YYYY-MM-DD>
tags: [learning, speaker-cab, listening-notes, maximocabs]
---

# Cab <Customer> <NxS> <line>: listening notes

Order: [[<cab-customer-nxs-line>]]. Prediction: `voicing.md` in the order directory (every number unverified, ears only). Rules that may move: [[speaker-cab-voicing]], [[speaker-cab-construction]].

## Session

- Date and place: <YYYY-MM-DD, shop | rehearsal room | stage>
- Amp and settings: <model, channel, volume, tone controls>
- Guitar: <model, pickups>
- Pedals in use: <>
- Volume level: <bedroom | rehearsal | gig>
- Room: <size, hard or soft, cab on the floor | raised | tilted>

## What we heard

| Aspect | Predicted | Heard | Notes |
|---|---|---|---|
| Low end | <alignment character from voicing.md> | <tight / balanced / big / boomy> | <> |
| Mids | <tone target> | <scooped / neutral / forward> | <> |
| Top | <tone target> | <chimey / smooth / dark> | <> |
| Breakup onset | <tone target> | <early / moderate / clean> | <> |
| Dispersion | <tone target> | <focused / wide> | <> |

- Customer's words: <verbatim>
- Brian's words: <verbatim>

## Prediction held

<agree | partly | disagree>: <one line reason>

## Corrected construction defaults to promote

- <measured value or failed clearance, the starting value it replaces, where it lands in [[speaker-cab-construction]]; "none" if nothing moved>

## Voicing rules to revisit

- <rule in [[speaker-cab-voicing]] that the ears contradicted, with the evidence; "none" if nothing moved>

## Site-form gaps

- <what the intake needed that the quote form does not ask; "none" if nothing>

## Speaker note updated

- <slug>: Field notes appended on <date>
````
<!-- /code -->

- [ ] **Step 4: Carve-outs in the two existing skills**

In `skills/furniture/SKILL.md` replace the frontmatter `description` line

```
description: Use when the user asks to design furniture or a woodworking project (shelf, bookcase, table, cabinet, bench, desk, workbench), modify such a design, or produce a cut list, lumber list, or shop drawings from one. For 3D-printable parts, use the 3d-model skill instead.
```

with

```
description: Use when the user asks to design furniture or a woodworking project (shelf, bookcase, table, cabinet, bench, desk, workbench), modify such a design, or produce a cut list, lumber list, or shop drawings from one. For 3D-printable parts, use the 3d-model skill instead. For guitar speaker cabinets, use the speaker-cab skill.
```

In `skills/3d-model/SKILL.md` replace the frontmatter `description` line

```
description: Use when the user asks to design, generate, create, or modify a 3D model or 3D-printable part, including recreating a part from photos, drawings, or sketches, for the Bambu Lab X2D printer.
```

with

```
description: Use when the user asks to design, generate, create, or modify a 3D model or 3D-printable part, including recreating a part from photos, drawings, or sketches, for the Bambu Lab X2D printer. For guitar speaker cabinets, use the speaker-cab skill.
```

- [ ] **Step 5: Vault instructions**

In `CLAUDE.md` replace the Layout bullet

```
- `skills/` - the `/3d-model` and `/furniture` skill sources, symlinked from `~/.claude/skills/`.
```

with

```
- `skills/` - the `/3d-model`, `/furniture`, and `/speaker-cab` skill sources, symlinked from `~/.claude/skills/`.
```

and the first Modeling workflow bullet

```
- Always use the `/3d-model` skill for 3D-printing work (visual verification per feature, printability check, STL + 3MF export) and the `/furniture` skill for furniture/woodworking work (same build discipline; buildability check and cut list via `scripts/cutlist.py` instead of printability and 3MF).
```

with

```
- Always use the `/3d-model` skill for 3D-printing work (visual verification per feature, printability check, STL + 3MF export), the `/furniture` skill for furniture/woodworking work (same build discipline; buildability check and cut list via `scripts/cutlist.py` instead of printability and 3MF), and the `/speaker-cab` skill for guitar speaker cabinet orders (voicing engine, generator, check table, and customer proposal, with two stops for Brian).
```

- [ ] **Step 6: Ignore an order's STEP and STL**

Append to `.gitignore`, directly after the speaker cab fixture lines:

```
# Speaker cab orders: STEP is regenerated by the order's cab.py
projects/Cab-*/*.step
projects/Cab-*/*.stl
```

- [ ] **Step 7: Install the skill**

```bash
ln -s /home/brian/ClaudeProjects/3d-modeling-brain/skills/speaker-cab ~/.claude/skills/speaker-cab
ls -la ~/.claude/skills/speaker-cab
```

Expected: `~/.claude/skills/speaker-cab -> /home/brian/ClaudeProjects/3d-modeling-brain/skills/speaker-cab`, the same shape as the `3d-model` and `furniture` links.

- [ ] **Step 8: Verify the files**

Run from the vault root:

```bash
grep -cP '\x{2014}' skills/speaker-cab/SKILL.md skills/speaker-cab/templates/brief.md skills/speaker-cab/templates/listening-notes.md
.venv/bin/python -c "import yaml, pathlib; [print(p, sorted(yaml.safe_load(pathlib.Path(p).read_text().split('---')[1]).keys())) for p in ('skills/speaker-cab/SKILL.md', 'skills/speaker-cab/templates/brief.md', 'skills/speaker-cab/templates/listening-notes.md')]"
grep -c 'speaker-cab' skills/furniture/SKILL.md skills/3d-model/SKILL.md CLAUDE.md
```

Expected: `0` for each of the three files on the first command; the second prints `['description', 'name']` for SKILL.md and the template keys for the other two; the third prints 1, 1, and 2.

- [ ] **Step 9: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add skills/speaker-cab/SKILL.md skills/speaker-cab/templates/brief.md skills/speaker-cab/templates/listening-notes.md skills/furniture/SKILL.md skills/3d-model/SKILL.md CLAUDE.md .gitignore
git commit -m "Speaker cab plan 3 task 6: the /speaker-cab skill, brief and listening-notes templates, carve-outs, symlink"
```

---

### Task 7: Dry run 1: the golden order `sample-roots-1x12`

**Files:**
- Create: `projects/Speaker-cab-system/fixtures/sample-roots-1x12/` (`brief.md`, `tone.json`, `voicing.json`, `voicing.md`, `cab.py`, `cab.json`, `checks.md`, `cutlist.md`, `cutlist.csv`, `proposal.md`, `images/`; `cab.step` git-ignored)
- Modify: `scripts/test_cabmodel.py` (`FIXTURE_ORDERS`), `scripts/test_cabreport.py` (`FIXTURE_ORDERS`)

**Interfaces:**
- Consumes: the installed skill (Task 6), the report module (Task 5), the notes (Tasks 3 and 4), the engine and layout (Tasks 1 and 2).
- Produces: the golden order every future order can be compared with; the fixture name in both `FIXTURE_ORDERS` lists.

The controller runs this task: it dispatches one Fable 5.1 subagent to run the skill, answers the stops from the answer sheet below, then verifies the end state and adds the fixture to the two test lists. Anything the run needed beyond the answer sheet is a finding against the skill text: fix `SKILL.md` (and its mirror twin) before the fixture is committed, and record the finding in the ledger.

- [ ] **Step 1: Dispatch the dry run**

Prompt for the subagent (verbatim, then the email and the answer sheet):

> Use the /speaker-cab skill on the quote email below. This is a dry run that produces a committed fixture order: the order directory is `projects/Speaker-cab-system/fixtures/sample-roots-1x12/` instead of `projects/Cab-<...>/`, the customer is the site's test persona, and at every stop take the answer from the answer sheet instead of asking; if the sheet has no answer for a stop, choose the first option the skill lists and report it. Do not commit. Report every place the skill text was unclear, wrong, or missing a step, with the phase and the sentence.

The quote email body (the site's quote template, filled from its test fixture):

```
New quote request from Pat Player <pat@example.com>

Cabinet:    tolex-1x12
Finish:     Black tolex
Grill:      Salt-and-pepper
Speaker:    Celestion G12H Greenback (16 ohm)
Hardware:   Black corners, Leather strap handle, Recessed jack plate, no piping

--- Use case ---
Amps:       1965 Fender Deluxe Reverb reissue
Style:      Roots, alt-country, low-volume gigs
Venue:      Small clubs, 150 cap max
Notes:      Want a tight low end and rolled highs.

Reply directly to this email to reach Pat Player.
```

The answer sheet:

- Follow-ups: none. Every assumption stands: the 1965 Fender Deluxe Reverb reissue is a 22 W tube combo whose extension jack puts this cabinet in parallel with its own 8 ohm speaker; no weight or size limit; no head to match; mono jack; on the floor; lives in a house; "Black tolex" is the site's Fender Style Black on the 54 in roll; "Salt-and-pepper" is not a site cloth (no swatch on file); "Celestion G12H Greenback (16 ohm)" is the catalog note celestion-g12h-30-anniversary at 16 ohm.
- Stop one (voicing): approve as presented. The site box reads punchy against a tight target, so expect the skill to propose a tone-driven box rather than keep the site box.
- The impedance blocker on the sheet (the 16 ohm driver against taps `[8]`, exit 2): accept it with `--accept-impedance-mismatch` (a 2:1 mismatch on a tube amp is within tolerance), re-run the same command with the flag, and record it in Decisions locked; the taps in `tone.json` stay `[8]`.
- A `port mouth` warn: accept and record it in Decisions locked.
- Operator rows: judge from the brief. No limit stated makes `weight vs limit` and `size vs limit` pass with "no limit stated"; `transport` passes with "no vehicle stated, a one-hand carry"; `wood movement` is n/a on tolex; `joinery fit` and `stock thickness` pass on the construction note's defaults; `stock yield` passes with the sheet count.
- Stop two (package review): approved; leave the `Price:` line empty.

- [ ] **Step 2: Verify the end state**

Run from the vault root:

```bash
D=projects/Speaker-cab-system/fixtures/sample-roots-1x12
ls $D $D/images
grep -c 'operator' $D/checks.md
.venv/bin/python scripts/cabreport.py $D --customer "Pat Player" --verify; echo "verify exit $?"
EXPORT=1 .venv/bin/python $D/cab.py; echo "cab exit $?"
grep -n 'Decisions locked' -A 12 $D/brief.md
```

Expected: every file of the Files list present plus the five renders and `fender-black.jpg` in `images/` (no cloth swatch: the proposal's cloth line reads `no swatch on file`); `0` rows still read operator; `verify exit 0`; `cab exit 0` with 19 check lines and no blocker (a `port mouth` warn and the `spans` warn are expected); the brief's Decisions locked holds the dated voicing approval, the accepted warns, and the package approval. The brief records the evaluate-first result (the site box with the calibration port reads punchy, target tight) and the proposal it approved instead; the layout must have passed without a port-fit blocker (the 1200-case matrix blocks only Cannabis Rex and Swamp Thang round proposals). Read `proposal.md` once for voice: designed-for wording, no predicted frequency, the `Price:` line empty.

- [ ] **Step 3: Add the fixture to the test lists**

In `scripts/test_cabmodel.py` and in `scripts/test_cabreport.py` replace the line

```python
FIXTURE_ORDERS = ["site-default"]
```

with

```python
FIXTURE_ORDERS = ["site-default", "sample-roots-1x12"]
```

- [ ] **Step 4: Run the CAD and report suites**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabmodel.py scripts/test_cabreport.py -q`
Expected: 38 passed (25 CAD, 13 report) in about 90 s.

- [ ] **Step 5: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/test_cabmodel.py scripts/test_cabreport.py projects/Speaker-cab-system/fixtures/sample-roots-1x12/brief.md projects/Speaker-cab-system/fixtures/sample-roots-1x12/tone.json projects/Speaker-cab-system/fixtures/sample-roots-1x12/voicing.json projects/Speaker-cab-system/fixtures/sample-roots-1x12/voicing.md projects/Speaker-cab-system/fixtures/sample-roots-1x12/cab.py projects/Speaker-cab-system/fixtures/sample-roots-1x12/cab.json projects/Speaker-cab-system/fixtures/sample-roots-1x12/checks.md projects/Speaker-cab-system/fixtures/sample-roots-1x12/cutlist.md projects/Speaker-cab-system/fixtures/sample-roots-1x12/cutlist.csv projects/Speaker-cab-system/fixtures/sample-roots-1x12/proposal.md projects/Speaker-cab-system/fixtures/sample-roots-1x12/images
git commit -m "Speaker cab plan 3 task 7: dry-run fixture sample-roots-1x12"
```


---

### Task 8: Dry run 2: the port-loop order `rex-roots-1x12`

**Files:**
- Create: `projects/Speaker-cab-system/fixtures/rex-roots-1x12/` (`brief.md`, `tone.json`, `voicing.json`, `voicing.md`, `cab.py`, `cab.json`, `checks.md`, `cutlist.md`, `cutlist.csv`, `proposal.md`, `images/`; `cab.step` git-ignored)
- Modify: `scripts/test_cabmodel.py` (`FIXTURE_ORDERS`), `scripts/test_cabreport.py` (`FIXTURE_ORDERS`)

**Interfaces:**
- Consumes: the installed skill (Task 6), the report module (Task 5), the notes (Tasks 3 and 4), the engine and layout (Tasks 1 and 2).
- Produces: the order that proves the port loop end to end: the port-fit blocker naming the tube, the pinned re-run, the trade-off stop, the front slot; the fixture name in both `FIXTURE_ORDERS` lists.

The controller runs this task: it dispatches one Fable 5.1 subagent to run the skill, answers the stops from the answer sheet below, then verifies the end state and adds the fixture to the two test lists. Anything the run needed beyond the answer sheet is a finding against the skill text: fix `SKILL.md` (and its mirror twin) before the fixture is committed, and record the finding in the ledger.

- [ ] **Step 1: Dispatch the dry run**

Prompt for the subagent (verbatim, then the email and the answer sheet):

> Use the /speaker-cab skill on the quote email below. This is a dry run that produces a committed fixture order: the order directory is `projects/Speaker-cab-system/fixtures/rex-roots-1x12/` instead of `projects/Cab-<...>/`, the customer is the site's test persona, and at every stop take the answer from the answer sheet instead of asking; if the sheet has no answer for a stop, choose the first option the skill lists and report it. Do not commit. Report every place the skill text was unclear, wrong, or missing a step, with the phase and the sentence.

The quote email body (the site's quote template, filled from its test fixture):

```
New quote request from Pat Player <pat@example.com>

Cabinet:    tolex-1x12
Finish:     Black tolex
Grill:      Salt-and-pepper
Speaker:    Eminence Cannabis Rex (8 ohm)
Hardware:   Black corners, Leather strap handle, Recessed jack plate, no piping

--- Use case ---
Amps:       1965 Fender Deluxe Reverb reissue
Style:      Roots, alt-country, low-volume gigs
Venue:      Small clubs, 150 cap max
Notes:      Want a tight low end and rolled highs.

Reply directly to this email to reach Pat Player.
```

The answer sheet:

- Follow-ups: none. Every assumption stands: the 1965 Fender Deluxe Reverb reissue is a 22 W tube combo whose extension jack puts this cabinet in parallel with its own 8 ohm speaker; no weight or size limit; no head to match; mono jack; on the floor; lives in a house; "Black tolex" is the site's Fender Style Black on the 54 in roll; "Salt-and-pepper" is not a site cloth (no swatch on file); "Eminence Cannabis Rex (8 ohm)" is the catalog note eminence-cannabis-rex at 8 ohm.
- Stop one (voicing): approve as presented. The site box reads punchy against a tight target, so expect the skill to propose a tone-driven box rather than keep the site box.
- A tap or impedance warning on the wiring row: accept (a 2:1 mismatch on a tube amp is within tolerance) and record it in Decisions locked.
- A `port mouth` warn: accept and record it in Decisions locked.
- The port-loop trade-off stop: choose the front slot (the first remedy listed) and record the choice.
- Operator rows: judge from the brief. No limit stated makes `weight vs limit` and `size vs limit` pass with "no limit stated"; `transport` passes with "no vehicle stated, a one-hand carry"; `wood movement` is n/a on tolex; `joinery fit` and `stock thickness` pass on the construction note's defaults; `stock yield` passes with the sheet count.
- Stop two (package review): approved; leave the `Price:` line empty.

- [ ] **Step 2: Verify the end state**

Run from the vault root:

```bash
D=projects/Speaker-cab-system/fixtures/rex-roots-1x12
ls $D $D/images
grep -c 'operator' $D/checks.md
.venv/bin/python scripts/cabreport.py $D --customer "Pat Player" --verify; echo "verify exit $?"
EXPORT=1 .venv/bin/python $D/cab.py; echo "cab exit $?"
grep -n 'Decisions locked' -A 12 $D/brief.md
```

Expected: every file of the Files list present plus the five renders and `fender-black.jpg` in `images/` (no cloth swatch: the proposal's cloth line reads `no swatch on file`); `0` rows still read operator; `verify exit 0`; `cab exit 0` with 19 check lines and no blocker (a `port mouth` warn and the `spans` warn are expected); the brief's Decisions locked holds the dated voicing approval, the port-loop trade-off and the front slot choice, the accepted warns, and the package approval. The Trade-offs presented section of the brief records, in order: the first proposal snapping to the 153.2 mm tube and the layout's `port fit` blocker naming the 101.5 mm tube; the pinned re-run (`--port-tube 101.5`) with its `port clamped at the 24 mm minimum` warning and the layout passing port fit; the stop with the four remedies and the front slot chosen; the slot re-run (`--port-slot <chamber width> 40` per the construction note) laying out clean. The final sheet has `port.shape` `slot`. Read `proposal.md` once for voice: designed-for wording, no predicted frequency, the `Price:` line empty.

- [ ] **Step 3: Add the fixture to the test lists**

In `scripts/test_cabmodel.py` and in `scripts/test_cabreport.py` replace the line

```python
FIXTURE_ORDERS = ["site-default", "sample-roots-1x12"]
```

with

```python
FIXTURE_ORDERS = ["site-default", "sample-roots-1x12", "rex-roots-1x12"]
```

- [ ] **Step 4: Run the CAD and report suites**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabmodel.py scripts/test_cabreport.py -q`
Expected: 41 passed (26 CAD, 15 report) in about 110 s.

- [ ] **Step 5: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/test_cabmodel.py scripts/test_cabreport.py projects/Speaker-cab-system/fixtures/rex-roots-1x12/brief.md projects/Speaker-cab-system/fixtures/rex-roots-1x12/tone.json projects/Speaker-cab-system/fixtures/rex-roots-1x12/voicing.json projects/Speaker-cab-system/fixtures/rex-roots-1x12/voicing.md projects/Speaker-cab-system/fixtures/rex-roots-1x12/cab.py projects/Speaker-cab-system/fixtures/rex-roots-1x12/cab.json projects/Speaker-cab-system/fixtures/rex-roots-1x12/checks.md projects/Speaker-cab-system/fixtures/rex-roots-1x12/cutlist.md projects/Speaker-cab-system/fixtures/rex-roots-1x12/cutlist.csv projects/Speaker-cab-system/fixtures/rex-roots-1x12/proposal.md projects/Speaker-cab-system/fixtures/rex-roots-1x12/images
git commit -m "Speaker cab plan 3 task 8: dry-run fixture rex-roots-1x12"
```


---

### Task 9: Whole-branch review, fix wave, mirror sync, retrospective, memory, handoff, push

**Files:**
- Modify (fix wave, as the review dictates): any file landed by Tasks 1 to 8, with the same fix copied into its mirror twin under `projects/Speaker-cab-system/pipeline/plan3-mirror/.vault/`, and this plan re-embedded
- Create: `knowledge/learnings/speaker-cab-plan-3.md`
- Modify: `knowledge/learnings/speaker-cab-plan-2.md` (the Plan 3 open-items bullet), `memory/project-speaker-cab-system.md`, `memory/MEMORY.md`
- Create: `projects/Speaker-cab-system/.claude/context-check/last-handoff.md` (git-ignored)

**Interfaces:**
- Consumes: everything landed; the ledger `.superpowers/sdd/progress.md` for the facts (commit hashes, test counts, review findings, dry-run findings).
- Produces: the vault state the first real order starts from.

The controller runs this task, not an implementer.

- [ ] **Step 1: Whole-branch review**

Package the diff of the range from Task 1's commit to Task 8's commit on the landed paths (`git diff <task1-parent>..HEAD -- scripts/ knowledge/ skills/ CLAUDE.md .gitignore projects/Speaker-cab-system/fixtures/ projects/Speaker-cab-system/site-copy-notes.md projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md projects/Speaker-cab-system/pipeline/catalog_genres.py > .superpowers/sdd/review-plan3.diff`) and dispatch one Fable 5.1 reviewer with the design addendum, this plan, the two dry-run fixtures, and the diff. The reviewer answers: does every check verdict, engine warning, and proposal fact in the two fixtures trace to code; does `SKILL.md` quote the landed messages, flags, row names, and file names exactly; would a builder cut anything wrong from either fixture's cut list; is any design requirement unmet. Verdict: ready to merge, with fixes, or blocked. Record the verdict in the ledger.

- [ ] **Step 2: Fix wave**

For every Critical and Important finding: fix the landed file, copy the fix into the mirror twin, re-embed the plan, prove sync, run the full suite, commit with explicit paths.

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
.venv/bin/python projects/Speaker-cab-system/pipeline/embed_plan_code.py --plan projects/Speaker-cab-system/plan-3-skill.md --mirror plan3-mirror
.venv/bin/python projects/Speaker-cab-system/pipeline/embed_plan_code.py --plan projects/Speaker-cab-system/plan-3-skill.md --mirror plan3-mirror --check
.venv/bin/python -m pytest scripts/test_cabvoice.py scripts/test_cutlist.py scripts/test_cablayout.py scripts/test_cabmodel.py scripts/test_cabreport.py -q
```

Expected: `plan-3-skill.md: in sync` and every test passing. Re-dispatch the reviewer on the fix wave's range; a clean re-review ends the wave. Minor findings are triaged in the ledger: fixed in the same wave when a line or two, otherwise listed as open items in the retrospective.

- [ ] **Step 3: Write the retrospective**

Create `knowledge/learnings/speaker-cab-plan-3.md` from this skeleton, replacing every bracketed field from the ledger:

````markdown
---
name: speaker-cab-plan-3
description: Retrospective for Plan 3 of the speaker cab system (the /speaker-cab skill, cabreport.py, engine and layout touches, canonical genre keys, two dry-run fixture orders), with the open items for the first real order
type: learning
status: complete
created: [date]
tags: [learning, speaker-cab, skill, retrospective]
---

# Speaker cab Plan 3 retrospective

Plan: [[plan-3-skill]]. Design: [[2026-09-11-plan-3-skill-design]] (approved 2026-09-11). Range [first commit]..[last commit] on main, subagent-driven: implementers Sonnet 5, the two dry runs and every review Fable 5.1, controller Fable 5.1.

## What was built

- [engine flags and blockers, test counts; layout port mouth and port fit naming, aesthetics block; canonical genre keys and the catalog script; construction and voicing note revisions; scripts/cabreport.py with its tests; skills/speaker-cab/ with three templates; the two fixture orders and what each recorded (box, port, warns, trade-off); full suite count]

## Process: plan first as tested code, dry runs as acceptance

- [what the mirror-first process did this time; how the dry runs went, every place the skill text was unclear and how it was fixed]

## What the reviews caught

- [every finding and its fix, by task]

## Starting values set during execution

- [any number or wording chosen while building that the design did not fix]

## Deviations from the design

- [each, with the reason; the port mouth warns on the site default and on 1x12 slots belong here if they were accepted as built]

## Open items

- **First real order:** [what the dry runs suggest watching]
- **Later:** [carried from the Plan 2 retrospective's Later list plus anything new: machine-readable Best with fields and ranking as code; per-impedance catalog sets; a proposal regeneration flag; a coverage threshold on the port mouth warn if Brian wants fewer warns]

## Decisions already locked

[copy the Decisions locked block from the design addendum's section 14, plus anything ruled during execution]
````

In `knowledge/learnings/speaker-cab-plan-2.md`, replace the bullet that begins `- **Plan 3 (skill):**` with `- **Plan 3 (skill):** done, see [[speaker-cab-plan-3]].`

- [ ] **Step 4: Update memory**

Rewrite `memory/project-speaker-cab-system.md` with this content, correcting the bracketed facts from the ledger:

```markdown
---
name: project-speaker-cab-system
description: Custom guitar speaker cab capability for MaximoCabs; plan 1 (knowledge base + cabvoice.py) built 2026-09-09, plan 2 (cablayout.py + cabmodel.py generator) built 2026-09-11, plan 3 (the /speaker-cab skill, cabreport.py, two fixture orders) built [date]; next is the first real order
metadata:
  type: project
---

Brian is adding a guitar speaker cabinet design capability to the vault for his MaximoCabs custom cab business (site repo at ~/ClaudeProjects/MaximoCabs, quote-only Astro site). Spec approved 2026-09-09 at projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md, amended for Unit 2 by 2026-09-10-plan-2-generator-design.md and for Unit 3 by 2026-09-11-plan-3-skill-design.md. Locked: 1x12 and 2x12 (mono or stereo), closed, closed-ported and open-back; Thiele-Small voicing in scripts/cabvoice.py; finger joints on both lines with a through-dovetail option on hardwood; ears-only validation; builder package plus customer proposal; no pricing, no site configurator; judgment in prose, numbers in code.

Plan 1 done 2026-09-09 (engine, notes, twenty speaker notes). Plan 2 done 2026-09-11 (layout kernel, CAD layer, site-default fixture). Plan 3 done [date]: skills/speaker-cab/ (SKILL.md plus brief, proposal, and listening-notes templates), scripts/cabreport.py (checks.md and the proposal's facts from voicing.json and cab.json), engine flags --port-tube, --fb, --port-count with size-limit blockers and a 24 mm port minimum, the layout's port mouth warn and port fit naming the tube that fits, canonical genre keys in the voicing note and every catalog note, and two fixture orders (projects/Speaker-cab-system/fixtures/sample-roots-1x12/ and rex-roots-1x12/) produced by dry runs of the skill. Retrospectives at knowledge/learnings/speaker-cab-plan-1.md, -plan-2.md, -plan-3.md.

**Why:** the site promises rig-specific volume, port, and baffle design; Plans 1 and 2 give it the acoustics and the geometry, Plan 3 the operator workflow with two stops for Brian (voicing approval, package review).

**How to apply:** for any cab order, use the /speaker-cab skill from the quote email; the two fixture orders are the golden examples of a finished order and the port loop. Plan documents live in projects/Speaker-cab-system/; the Plan 3 mirror in its pipeline/plan3-mirror/ is the oracle the plan's code came from, and a fix to landed code is copied there and re-embedded. Every construction number is a starting value until a build measures it; confirm with Brian before trusting one. See [[reference-vault-github-repo]] for commit and push habits.
```

In `memory/MEMORY.md`, replace the Speaker cab system line with:

```markdown
- [Speaker cab system](project-speaker-cab-system.md) - MaximoCabs guitar cab capability; plans 1 to 3 built (engine, generator, /speaker-cab skill with two fixture orders); next is the first real order, open items in knowledge/learnings/speaker-cab-plan-3.md
```

- [ ] **Step 5: Handoff, commit, push**

Write `projects/Speaker-cab-system/.claude/context-check/last-handoff.md` in the form of the Plan 2 handoff (what is done, current state with the last commit hash and the exact test command, files that matter, a Decisions already locked block copied from the retrospective, and the next action: run the first real order with the `/speaker-cab` skill, or the design's "Later" items). Then:

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add knowledge/learnings/speaker-cab-plan-3.md knowledge/learnings/speaker-cab-plan-2.md memory/project-speaker-cab-system.md memory/MEMORY.md projects/Speaker-cab-system/plan-3-skill.md projects/Speaker-cab-system/pipeline/plan3-mirror
git commit -m "Speaker cab plan 3 complete: retrospective, memory, plan and mirror synced"
git push origin main
```

Expected: push accepted; `git status --short` shows only the other session's files.

---

## Self-review notes (written with the plan)

- **Spec coverage.** Design section 3.1 (`SKILL.md`) is Task 6; 3.2 (templates) Tasks 5 and 6; 3.3 (`cabreport.py`) Task 5; 3.4 (the per-order directory) `SKILL.md` Phases 1 and 7; 4 (phases and stops) `SKILL.md`; 5 (the port loop) `SKILL.md` Phase 4 reading the blocker forms Task 2 builds; 6 (engine and layout touches) Tasks 1 and 2; 7 (voicing note, catalog, construction note) Tasks 3 and 4; 8 (fixtures and dry runs) Tasks 7 and 8; 9 (tests) the per-task tests; 10 (files) the File Structure table; 11 (vault updates) Tasks 4, 6, and 9; 12 (process) the Global Constraints; 13 and 14 stand. Section 15 of the design addendum records the amendments found while this plan was written.
- **Pre-flight, done by construction.** Every code block and note text was embedded by `projects/Speaker-cab-system/pipeline/embed_plan_code.py --mirror plan3-mirror` from the mirror, where the suites run green: engine 433, cut list 3, layout 52 (the 1200-case matrix: 150 engine power stops, 1026 clean, 24 port-fit blockers, every one naming the 101.5 mm tube, 194 cases with a port mouth warn), CAD 24 (12 builds in 23 s; all 60 in 97 s with `CAB_FULL_MATRIX=1`), report 11; 523 in about 70 s. `--check` reports the plan in sync. Before embedding, a Fable 5.1 reviewer read the whole mirror against the design (`plan3-mirror/REVIEW.md`): its prose fixes are in the mirror (the loop now names what to do for each of the five `port fit` texts the layout emits; Phases 5 and 6 say when the operator rows are judged), and three of its minor code items were fixed in the mirror before embedding (a null finish or cloth renders "to be confirmed", a missing key and an unreadable template are named input errors, the site-default port mouth test asserts the fixture exists instead of skipping). The expected counts per task come from those runs and from two temp-copy experiments (the landed voicing note against the mirror tests: every test passing except the calibration row and the not-yet-added genre test; the landed notes against the catalog tests: 1 failed, 5 passed).
- **Placeholder scan.** No TBD, TODO, "similar to Task", or unfilled token remains; every code and note step shows its content; the two retrospective and memory skeletons in Task 9 carry bracketed fields for the controller to fill from the ledger, as Plan 2's did.
- **Type consistency.** Every symbol named in an Interfaces block was resolved by the embed tool from the mirror (a missing name stops the tool); the five test files and the module import and test as a whole, so names agree across tasks by construction.
- **Deviations from the design, recorded in the addendum's section 15.** A `--verify` run writes nothing and needs `--customer`; every non-verify run rewrites `checks.md`; `alignment` shows Fb and F3 on a ported box; the proposal template puts the configuration on its own line; the port loop handles five blocker forms and gives the too-long-port form one automatic re-run with the next tube down the table; the height floor over the limit is a blocker like the width floor; `port_dims`'s remedy sentence corrected; the site default and every 1x12 front slot carry a `port mouth` warn under the rule as approved; the catalog's Best with section is three bullets, not two; one calibration row moves with the 24 mm minimum (Eminence Red White and Blues, Fb 74 to 73 Hz); a slot up to 1 mm wider than its chamber is trimmed and the slot re-run pins the external width (found by the Task 4 review, which traced the Rex loop and showed a floating-width slot re-run never converges); `SKILL.md` is 417 lines (absolute interpreter and a cd line per command block, the handoff in the order commit, status transitions, a Phase 8 commit step).
- **Design-level findings for Brian, not encoded.** The bridge is strict on ported boxes (punchy serves balanced, not tight) and the site box reads punchy with every catalog speaker, so a tight target always proposes a tone-driven box; both dry-run fixtures will be smaller than the site box. The `port mouth` warn fires on the site box's own rear tube (84 mm behind the magnet), on every 1x12 front slot whose floor needs a stiffener, and on slots in shallow boxes; coverage is reported for information and no threshold gates the warn. `--fb` is unbounded in code; the voicing note binds the skill to the engine's 45 to 90 Hz range.
- **Warnings for implementers.** Task 1's warning texts are quoted in Tasks 2, 4, 6, and 8 and in both notes, so a wording change ripples. The CAD suite takes about 70 s and each dry-run fixture adds about 20 s. The two dry runs are long subagent sessions that follow `SKILL.md` end to end; their stops are answered from the answer sheets, and anything they needed beyond the sheets is a skill-text finding to fix before the fixture is committed. `checks.md` is rewritten by every non-verify `cabreport.py` run, so the operator rows are judged last. The site-default fixture ships without `checks.md` and `proposal.md`; the dry-run fixtures ship with both. Never stage the other session's file.
- **Open minor items from the mirror review, left as recorded for the retrospective.** `verify_proposal` is a presence check (a deleted Configuration line still verifies because "1x12" appears in the line label); `slot_ports` says "1 slot of W mm do not fit"; `--fb` has no cap in code; `wood movement` stays an operator row on the tolex line.
- **After execution.** Copy any fix landed in `scripts/`, `knowledge/`, or `skills/` into its mirror twin under `plan3-mirror/.vault/` and re-embed with `--check`, so the plan and the mirror stay the record of what shipped; Task 9's fix wave does this.


