---
name: 2026-09-10-plan-2-generator-design
description: Design addendum for Unit 2, the parametric cabinet generator (cablayout.py plus cabmodel.py), from the 2026-09-10 brainstorm with Brian; supersedes the Unit 2 construction defaults it names
type: design
status: approved
created: 2026-09-10
approved: 2026-09-10
tags: [project, speaker-cab, maximocabs, design, generator, cad, woodworking]
---

# Plan 2 generator design (Unit 2 addendum)

Addendum to Unit 2 of [[2026-09-08-speaker-cab-system-design]]. Everything in the spec's Unit 2 that this document does not override still holds. Plan 2 is written from this document in the Plan 1 format ([[plan-1-knowledge-engine]]) and consumes the open items in [[speaker-cab-plan-1]]. The research behind the decisions is in [[guitar-cab-joinery-survey]] and [[speaker-envelopes-and-port-stock]].

**Goal.** From an approved `voicing.json` and an aesthetics block, produce the builder package for one cabinet: STEP assembly, renders, cut list with tolex yardage, and a machine-readable report with every check verdict, for 1x12 and 2x12 cabinets in the tolex and hardwood lines, closed, closed-ported (round rear or front slot), open, and semi-open.

## 1. What changes against the spec's Unit 2

| Spec said | Now |
|---|---|
| Hardwood line: 38 x 38 mm corner posts, panels tenoned through, glued and pinned | Finger joints at all four corners on both lines; through dovetail as the hardwood option. No posts. |
| Default finger width 18 mm | Half the panel thickness (9 mm birch, 9.5 mm hardwood), count forced odd |
| Single library `scripts/cabmodel.py` | Numeric kernel `scripts/cablayout.py` plus CAD layer `scripts/cabmodel.py` |
| Grill frame 18 x 40 mm strips in the 20 mm recess | Frame rests on the speaker flanges and on 5 mm felt corner spacers; strips 12 x 40 mm; recess stays 20 mm |
| Cutout margin 25 mm everywhere (engine) | 44 mm cutout to shell, 68 mm between the two cutouts of a 2x12 (brace or divider plus 25 mm each side); the engine gains a height floor |
| Floating baffle only | Baffle mount parameter: floating (default) or fixed in a dado |
| Handle: strap on tolex, recessed side handles on hardwood | Handle type is an aesthetics parameter; strap top center is the default on both lines (what the site shows) |
| Port diameter as solved | Snapped to purchasable tube inside diameters in the engine |

Site copy mismatch to fix on the MaximoCabs site (out of scope here): `src/content/cabinets/hardwood-1x12.md` says "Through-tenon corner posts, glued + pinned" while the site's own renders show finger joints. Both cabinet pages say "closed-back, ported" while the rear renders show an open back.

## 2. Decisions from the brainstorm (2026-09-10)

1. Corners: finger joints only on the tolex line; finger joints or through dovetails on the hardwood line. The survey found finger joints the plurality at the top of the market and the through dovetail the only structural peer for solid wood.
2. Finger width: half the panel thickness. Both ends full fingers; top and bottom carry the front full finger.
3. Dovetail defaults: tails on the side panels (a lift by the top handle loads the joint in its locked direction), pins on top and bottom, half-pins at both ends, slope 1:8, pin width half the thickness, tails about 30 mm.
4. Port tubes: not settled in the shop. Starting table of Schedule 40 inside diameters 52.0, 77.3, 101.5, 153.2 mm, flagged.
5. Plan 2 carries the shared-code touches the generator needs (engine and cut list emitter), reviewed the Plan 1 way. The port-count CLI flag and the Fb override stay in Plan 3.
6. Library shape: layout kernel plus CAD layer.
7. Grill frame on the flanges (Marshall practice) with a 44 mm shell margin and a 68 mm gap between the cutouts of a 2x12 (brace or divider plus 25 mm each side). Brian approved the rule against a stated 31 mm shell margin and a 25 mm gap; both figures were corrected while writing this document and reported with it.
8. Baffle mount: floating by default, fixed in a dado as the option.
9. Speaker envelope: two-step behind the baffle (basket cylinder at the cutout diameter, then the magnet cylinder from a new catalog field); the frame diameter, also new, sizes the flange disc in front of the baffle.

## 3. Modules and contracts

### 3.1 `scripts/cablayout.py` (numeric, imports only the standard library and `cabvoice`)

- `Aesthetics` dataclass with defaults: `corner_joint` ("finger" | "dovetail"), `finger_width_mm` (None = panel / 2), `dovetail_slope` (8), `dovetail_pin_mm` (None = panel / 2), `dovetail_tail_mm` (30.0), `baffle_mount` ("floating" | "fixed"), `handle` ("strap" | "recessed-side"), `handle_screw_spacing_mm` (228.6), `recessed_handle_cutout_mm` ((140.0, 90.0)), `jack_plate_cutout_mm` ((110.0, 70.0)), `corners` ("black" | "chrome" | "none"; default black on tolex, none on hardwood), `corner_allowance_mm` (50.0), `piping` (bool), `feet` ("rubber" | "tilt-back"), `foot_diameter_mm` (40.0), `foot_inset_mm` (32.0), `tolex_roll_in` (54 | 32), `head_width_mm` (None), and pass-through strings `tolex_color`, `grill_cloth`, `finish`.
- `load_voicing(path) -> dict` and `order_from(voicing: dict, aesthetics: Aesthetics) -> CabSpec`. Reads `box.external_mm`, `box.internal_mm`, `enclosure` (type, driver_count, chambers, jack_config, open_fraction), `speakers[]` (slug, cutout_mm, bolt_circle_mm, bolt_count, depth_mm, weight_kg, displacement_l, frame_diameter_mm, magnet_diameter_mm, magnet_diameter_estimated), `port` (shape, diameter_mm, slot_w_mm, slot_h_mm, length_mm, location, count) or null, `volumes` (net_total_l, per_chamber_net_l), `construction` (panel_mm, back_mm, baffle_mm, recess_mm, line, species, wall_material), `prediction_status`, `blockers`. A sheet with blockers, a missing key, or a dovetail on the tolex line raises `ValueError` (exit 1). Never parses warning text.
- `layout(spec) -> Layout`: `parts` (list of `Blank`: name, qty, dims t x w x l, position and orientation in the cab frame, material, density, notes, joinery schedule), `cutouts` (centers, diameter, bolt pattern), `port` (tube axis, inside and outside diameter, length, flange ring; or slot with shelf and cheeks), `hardware` (jack plates, handle, feet or tilt-back legs, corners, with positions and cutouts), `envelopes` (per speaker, stepped cylinder), `chambers` (air boxes), and derived numbers: `gross_l` and `net_l` per chamber, `mass_kg` split into parts, speakers, hardware, `com_mm`, `tolex` (area, roll length in m and yd) or None, `part_count`.
- `check_layout(layout, spec) -> list[Check]` where `Check` is (name, level in pass | warn | blocker, message). Rules in section 5.
- `finger_schedule(depth_mm, thickness_mm, width_hint_mm) -> (count, width_mm)` and `dovetail_schedule(depth_mm, thickness_mm, pin_mm, tail_mm, slope) -> schedule` are public so the plan can test them alone.

### 3.2 `scripts/cabmodel.py` (build123d)

- `build(layout) -> CabBuild`: `parts` registry in the furniture shape (`name`, `solid`, `dims`, `qty`, `material`, `notes`), one named solid per part; `components` (speaker envelopes, jack plates, handle, feet) for renders and interference only; `assembly` compound; `air` (one solid per chamber).
- `check_build(cab, layout) -> list[Check]`: boolean interference between every pair that must not touch (envelope against port, brace, divider, back, cleats, shelf; flange against grill frame opening is analytic), measured air volume within 1 percent of the layout's net, part count equals the layout's, each blank's solid-to-bounding-box ratio recorded.
- `export(cab, layout, out_dir)`: `cab.step`, temporary STLs for `scripts/render_stl.py` (iso, front, top, right, plus an exploded view built by translating each part away from the assembly center along its centroid direction), `cutlist.md` and `cutlist.csv` with the tolex line, `cab.json`.
- Algebra mode, `align=(Align.CENTER, Align.CENTER, Align.MIN)` idiom, cutting tools extended 1 mm past coincident faces, per the furniture rules. Two identical build123d failures on one feature escalate to FreeCAD per the spec.

### 3.3 `projects/Cab-<...>/cab.py` (per order, thin)

Aesthetics constants at the top, `load_voicing("voicing.json")`, `order_from`, `layout`, `check_layout`, `build`, `check_build`, `export`, behind the furniture gates `TMP_STL`, `EXPORT`, `SHOW`. Prints every check line. Exit 0 all pass or warn, 1 input error with nothing written, 2 any blocker with files still written. The skill writes this file in Plan 3; Plan 2 ships the fixture's copy as the template.

### 3.4 `cab.json`

Keys: `name`, `generated`, `line`, `species`, `corner_joint`, `baffle_mount`, `external_mm`, `external_in`, `internal_mm`, `enclosure`, `speakers` (slugs), `volumes` (gross and net per chamber, sheet net, delta percent), `mass` (total, parts, speakers, hardware, `com_mm`), `hardware` (item, position, cutout, note), `tolex` (roll_in, area_m2, length_m, length_yd) or null, `parts` (name, qty, blank_mm, material, notes), `checks` (name, level, message), `files`, `prediction_status` copied from the sheet. Plan 3 templates `proposal.md` from this and `voicing.json`.

## 4. Geometry rules

All numbers are starting values recorded in [[speaker-cab-construction]] with `status: unverified-starting-values` unless marked locked.

- **Frame.** X width, Y depth with the external front face at 0 and positive toward the back, Z height with the floor at 0. 2x12 is side by side only.
- **Shell.** Top, bottom, two sides. 18 mm Baltic birch on tolex, 19 mm species on hardwood. The engine keeps voicing both lines at 18 mm (locked); the layout reports the true internals and the volume check absorbs the difference.
- **Corners.** Comb on the four depth-axis edges. Fingers: width hint half the thickness, count the nearest odd integer to depth / hint, width depth / count, top and bottom start with a full finger at the front edge, sides with a gap. Dovetails (hardwood only): tails on the sides, pins on top and bottom, half-pins both ends, slope 1:8, pin narrow width half the thickness, tail count from a 30 mm tail target. Cut list rows are rectangular blanks with the schedule in the note ("finger joint, 31 fingers of 9.0 mm, both ends full, front finger on top and bottom"). Hardwood rows carry "grain front to back on all four panels, book-matched, show face out".
- **Baffle.** 18 mm birch both lines. Front face 20 mm behind the front edge (locked). Floating: 1 mm side clearance, on 18 x 18 cleats top, bottom, and sides with felt between cleat and baffle, screwed through the cleats. Fixed: glued into a 6 mm dado in all four shell panels, blank 12 mm larger in width and height, no baffle cleats, dado noted on the shell rows. On the hardwood line every cleat runs across the panel grain, so cleats (baffle and back) are screwed through slotted holes and glued only at their center 100 mm, and a fixed baffle is glued in the front 100 mm of each dado only; the cut list rows carry the note. Cutouts at the note's diameter; 1x12 centered on the baffle; 2x12 centers spaced cutout plus 68 mm about the center (brace or divider plus 25 mm each side); bolt holes 6.5 mm at the note's count on its circle, first hole at twelve o'clock. Speakers front-mounted on T-nuts.
- **Grill frame.** Four 12 x 40 mm birch strips, half-lap corners, outer size the recess opening minus 2 mm per side, resting on the speaker flanges (5 mm starting flange thickness) and on 5 mm felt spacers at the corners, so the frame face sits 3 mm behind the front edge. A strip may cover a flange but must clear every cutout by 2 mm. With a slot port the frame covers only the baffle above the shelf.
- **Margins.** Cutout edge to shell inner face at least 44 mm (strip 40 plus 2 clearance plus 2); cutout edge to brace or divider 25 mm, so the two cutouts of a 2x12 sit 68 mm apart (18 plus 2 x 25). The engine's width floor becomes n x cutout + (n - 1) x 68 + 2 x 44, the same for mono and stereo because the divider replaces the brace (2x12: 722 mm internal, 758 mm external, 29.8 in, the Marshall 1936 width; 1x12: 371 mm, below the site box), and it gains a height floor of cutout + 88, plus slot height + 18 for a slot port (a slot-ported 1x12 on the site box grows from 18.0 to 18.3 in tall). The flange then clears the shell inner face by 44 minus its overhang, 31 mm on a Celestion.
- **Brace and divider.** Mono 2x12: one 18 x 60 mm birch brace, vertical at X 0, front face 2 mm behind the baffle back, notched at both ends around the baffle cleats (no notch with a fixed baffle). Stereo: 18 mm divider from the baffle back to the back panel inner face, cleats on both faces at the baffle and at the back; chamber width (internal minus 18) / 2. The layout measures each shell and back panel's longest span between glued members and adds one 18 x 40 stiffener across the middle of any span over 450 mm (construction note rule; on a mono 2x12 that is the back panel).
- **Backs.** Closed: 12 mm birch flush with the rear edge on 18 x 18 cleats, removable. Open and semi-open: two 12 mm panels, each (1 - open fraction) x internal height / 2, on cleats; lower panel carries the jack plate. Stereo open-back keeps the divider and one plate per chamber.
- **Round rear port.** Inside diameter from the sheet (already snapped by the engine), Schedule 40 outside diameter from the table, physical length the sheet's `length_mm` measured through the back panel, a 12 mm plywood flange ring (outside diameter tube plus 60) glued to the inside face. Count per chamber from `port.count`. Axis placement tries in order: outboard of the driver at driver height, below the driver, lower outboard corner, above the driver; the first spot with 25 mm radial clearance to the envelope over their axial overlap and 25 mm to walls, cleats, brace, divider, and jack plate wins. None: blocker naming the longest tube that fits at that diameter.
- **Front slot.** Baffle shortened by slot height plus an 18 mm shelf. The shelf's front edge is flush with the baffle face, its depth equals the sheet's port length, and it doubles as the bottom cleat (glued with a fixed baffle). Slot narrower than the chamber: two cheeks. Mono 2x12: two slots split by an 18 mm center cheek in line with the brace, blocker if the two do not fit. Shelf depth must leave at least max(25, slot height) of free depth behind it.
- **Speaker envelope.** Behind the baffle: a basket cylinder at `cutout_mm` for the first 100 mm measured from the baffle front face, then a cylinder at `magnet_diameter_mm` + 12 (185 mm when None), total length `depth_mm`. In front of the baffle: a flange disc at `frame_diameter_mm`, 5 mm thick, for the grill rule and the render. Clearances: 25 mm from any envelope part to port, back, cleats, shelf, stiffeners, brace, and divider; envelopes never overlap each other. Mass placed at the baffle at the cutout center (construction note rule).
- **Hardware.** Jack plate cutout `jack_plate_cutout_mm`, one per chamber, bottom center of the back panel or lower panel, 25 mm above the cleat. Strap handle: screw pair at `handle_screw_spacing_mm` on the top panel at the center of mass in X and Y, Y clamped `corner_allowance_mm` inside the edges. Recessed side handles: one per side at the depth center of mass, upper third of the height, cutout `recessed_handle_cutout_mm`. Feet: four, `foot_diameter_mm`, inset `foot_inset_mm`. Tilt-back legs: a hardware line with pivot screw positions (100 mm from the front and bottom edges), no geometry. Corners: hardware line, keep-out `corner_allowance_mm` for every cutout.
- **Derived.** Net volume per chamber = air box minus brace, divider, cleats, shelf, tube and flange ring, minus port air, minus the note's `displacement_l` per driver. Mass = sum of blank volumes x density (birch 680 kg/m3, species from the construction note) + speakers + 1 kg hardware. Tolex: six external faces x 1.15 / roll width, in m and yd.

## 5. Checks

| Check | Level | Rule |
|---|---|---|
| sheet | layout | `blockers` empty and `prediction_status` present, else input error |
| site default | fixture test | external dimensions within 1 mm of 508 x 457.2 x 279.4 |
| net volume | layout and CAD | each chamber within 5 percent of the sheet's per-chamber net; CAD measured air within 1 percent of the layout |
| stereo balance | layout | chamber volumes equal within 1 percent |
| cutout | layout | diameter equals the note; 44 mm to the shell, 25 mm to brace or divider, 68 mm between 2x12 cutouts; fits the baffle height |
| grill opening | layout | strip inner edge clears every cutout by 2 mm |
| port fit | layout and CAD | tube or shelf clearances as in section 4; blocker names the longest tube or shelf that fits |
| magnet to back | layout | envelope end to back panel inner face at least 25 mm |
| interference | CAD | no boolean overlap between any pair that must not touch |
| handle | layout | handle center within 15 mm of the center of mass on X |
| head match | layout | external width = head width + 0 to 10 mm when `head_width_mm` is given |
| line | layout | dovetail only on hardwood; species density known |
| stock | layout | ply blanks within 2440 x 1220; hardwood panels within 3050 x 600 glued-up (flagged) |
| part count | CAD | equals the layout's table |
| rectangularity | CAD | ratio recorded per blank; comb panels list by blank dims, non-rectangular parts get the emitter's drawing note |

## 6. Shared-code touches

- **`scripts/cabvoice.py`.** `PORT_TUBE_ID_MM = (52.0, 77.3, 101.5, 153.2)`; `size_port` snaps a round port to the smallest table diameter not below the solved one, re-solves length and air speed, keeps the existing warnings; `MAX_PORT_DIAMETER_MM` becomes 153.2 (the largest tube) and the `--port-diameter` default 77.3, both flagged as changes to Plan 1 starting values. `SHELL_MARGIN_MM = 44.0` and `CUTOUT_GAP_MM = 68.0` beside `CUTOUT_MARGIN_MM = 25.0`; `min_internal_width_mm(driver_count, cutout_mm)` becomes n x cutout + (n - 1) x 68 + 2 x 44 and the stereo caller stops adding the divider separately because the 68 already holds it; new `min_internal_height_mm(cutout_mm, slot_h_mm)`; `dims_for_volume` gains `min_internal_height_mm` with the same conflict handling as width; `propose` passes both floors. `Driver` gains `frame_diameter_mm` (required), `magnet_diameter_mm` (optional), `magnet_diameter_estimated` (bool); validator and `to_dict` follow. The 351 tests are updated and the calibration table regenerated; the matrix test proves propose and evaluate still agree.
- **`scripts/cutlist.py`.** `write_cut_list(..., extra_lines=None)` appends a "## Materials not cut" section to the markdown and one CSV row per line. The emitter already prefers `dims` over `solid`, so comb panels pass both.
- **Catalog notes.** All 20 notes gain `frame_diameter_mm`, `magnet_diameter_mm`, `magnet_diameter_estimated` from [[speaker-envelopes-and-port-stock]] with a flagged Data notes sentence where estimated, plus the two Celestion corrections (G12H-75 magnet 168 not 188; the 141.pdf source is Voice Coil magazine).

## 7. Tests

- `scripts/test_cablayout.py`: unit tests per rule (finger parity and front-edge rule, dovetail schedule, margins and floors, port placement order and blocker text, slot cheeks, open-back panel heights, volumes against hand-computed cases, center of mass, yardage on both roll widths, Aesthetics validation). Matrix: every catalog speaker x five enclosures x four driver and jack configurations (1x12, 2x12 mono, mono-parallel-out, stereo) x three line and joint pairs (tolex finger, hardwood finger, hardwood dovetail), each on a live `cabvoice.propose` with the fixture tone (`fixtures/tone-roots.json`): about 1200 cases, each either lays out clean or returns a named blocker, and every clean layout's net volume agrees with its sheet within 5 percent.
- `scripts/test_cabmodel.py`: twelve representative CAD builds by default (all sixty behind `CAB_FULL_MATRIX=1`), each proving measured air within 1 percent of the layout, no interference, part count, STEP written; the fixture build and its 1 mm test; renders written to a temporary directory.
- Engine: `scripts/test_cabvoice.py` updated for the tube snap, floors, and new fields; the calibration table test pinned to the regenerated table.

## 8. Deliverables and files

```
scripts/cablayout.py
scripts/cabmodel.py
scripts/test_cablayout.py
scripts/test_cabmodel.py
projects/Speaker-cab-system/fixtures/site-default/   (voicing.json, cab.py, cab.json, cutlist.md, cutlist.csv, images/; STEP and STL not committed)
projects/Cab-<Customer>-<NxS>-<line>/                 (per order: cab.py, cab.step, cab.json, cutlist.md, cutlist.csv, images/)
```

Renders: iso, front, top, right, exploded, through `scripts/render_stl.py`. No photoreal finishes.

## 9. Vault updates the plan carries

- [[speaker-cab-construction]]: shell per line rewritten (finger joints both lines, dovetail option, no posts; corner post row dropped from Materials), finger and dovetail conventions, grill frame on flanges with 12 x 40 strips, margins 44 to the shell, 25 to brace and divider, 68 between 2x12 cutouts, hardwood cross-grain cleat rule, baffle mount option, tube table, Schedule 40 outside diameters, envelope rule, hardware starting values from the research, wood-movement rule for the hardwood shell, site copy mismatch.
- Spec Unit 2: one pointer line to this addendum.
- [[speaker-cab-plan-1]]: the Plan 2 open item on corner posts marked superseded.
- Catalog notes as in section 6.
- Retrospective `knowledge/learnings/speaker-cab-plan-2.md`, handoff, memory.

## 10. Process for Plan 2

Plan document `projects/Speaker-cab-system/plan-2-generator.md` in the Plan 1 format with complete code per task, Global Constraints, File Structure, a pre-flight transcription run of every code block before Task 1. About thirteen tasks: catalog fields; engine touches; cut list hook; four layout tasks (spec and shell schedules; baffle, cutouts, grill, cleats, brace, divider; backs, ports, hardware, envelopes; derived numbers, checks, report, matrix); four CAD tasks (shell comb and dovetails; baffle, brace, divider, cleats, grill; backs, ports, envelopes, plates; assembly, air volume, interference, exploded view, exports, CAD matrix); fixture order; vault updates. Implementers Sonnet 5, every review Fable 5.1, controller Fable 5.1; the engine task goes to Fable 5.1 as implementer because it changes shared cross-mode logic. Every CAD task renders its feature and both implementer and reviewer view the PNG. Ledger at `.superpowers/sdd/progress.md`, attribution trailers on every commit, explicit-path commits, the other session's files never staged.

## 11. Deferred

- Plan 3: `--port-count` CLI flag, Fb override, the skill's build loop that re-runs voicing when the generator returns a port blocker, proposal template from `cab.json`.
- Later: per-impedance catalog sets; measured finger width, flange thickness, corner leg length, and jack plate cutout from purchased parts; a vertical 2x12; a tolex-line dovetail if ever asked.

## 12. Decisions locked

- Finger joints on both lines; through dovetail as the hardwood option; no corner posts.
- Finger width half the panel thickness, odd count, full fingers both ends, front finger on top and bottom.
- Dovetail: tails on the sides, pins on top and bottom, half-pins, 1:8, pin half thickness, tail 30 mm target.
- Layout kernel plus CAD layer; cab.py thin; cab.json is Plan 3's input.
- Grill frame on the flanges, 12 x 40 strips, 20 mm recess kept, 44 mm shell margin, 25 mm brace and divider margin, 68 mm between 2x12 cutouts, engine floors follow (2x12 minimum 29.8 in external).
- Baffle mount parameter, floating default, fixed in a 6 mm dado.
- Strap handle default on both lines; handle type a parameter.
- Tube table 52.0, 77.3, 101.5, 153.2 mm snapped in the engine; hard maximum 153.2; default start 77.3.
- Two-step speaker envelope (basket at the cutout diameter, then the magnet from the catalog field); 12 mm cover allowance; 185 mm fallback; flange disc from the frame field.
- Plan 2 carries the engine, cut list, and catalog touches; Plan 3 keeps the CLI flag and Fb override.
