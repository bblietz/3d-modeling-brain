### Task 2: Engine touches: tube table, shell margins, height floor

**Files:**
- Modify: `scripts/cabvoice.py` (port constants, `snap_tube_id`, `size_port`, box and inside-part constants, `min_internal_width_mm`, `min_internal_height_mm`, `dims_for_volume`, `_port_inside_l`, `inside_parts_l`, `Constraints`, `_volumes`, `propose`, `evaluate`, `render_markdown`, `_build_parser`)
- Modify: `scripts/test_cabvoice.py` (ten existing tests, new Task 2 tests)
- Modify: `knowledge/speaker-cab-voicing.md` (calibration table regenerated)
- Mirror source (byte-identical): `projects/Speaker-cab-system/pipeline/plan2-mirror/.vault/scripts/cabvoice.py`, `.vault/scripts/test_cabvoice.py`, `plan2-mirror/.vault/plan/calibration_table.md`

**Interfaces:**
- Consumes: Task 1's engine (frame and magnet fields present).
- Produces: `PORT_TUBE_ID_MM = (52.0, 77.3, 101.5, 153.2)`, `PORT_TUBE_OD_MM` dict, `MAX_PORT_DIAMETER_MM = 153.2`, `DEFAULT_PORT_DIAMETER_MM = 77.3`, `snap_tube_id(diameter_mm) -> float`, `SHELL_MARGIN_MM = 44.0`, `CUTOUT_GAP_MM = 68.0`, `CUTOUT_MARGIN_MM = 25.0` (kept), `HARDWOOD_FLOOR_EXTRA_MM = 2.0`, the inside-part constants (`CLEAT_MM`, `STIFFENER_MM`, `SPAN_MAX_MM`, `BRACE_MM`, `JACK_PLATE_H_MM`, `JACK_CLEAR_MM`, `FLANGE_RING_T_MM`, `FLANGE_RING_EXTRA_MM`, `TUBE_WALL_FALLBACK_MM`), `min_internal_width_mm(driver_count, cutout_mm)`, `min_internal_height_mm(cutout_mm, slot_h_mm=None)`, `dims_for_volume(..., max_external_mm=None, min_internal_height_mm=None, strict=True, ...)`, `inside_parts_l(internal_mm, enclosure, driver_count, chambers, jack_config, port, line, port_count=None) -> float`, and a `volumes.inside_parts_l` key in every sheet with the identity gross = net + displacement + brace + port + divider + inside_parts, where `volumes.port_l` is the port air inside the box (a tube's length through the back panel and a slot's through the baffle are outside it; `port.volume_l` stays the whole port). Every round port in a `voicing.json` has `port.diameter_mm` in the tube table; `cablayout` (Task 4) imports the constants and `PORT_TUBE_OD_MM` for the tube outside diameter, and its measured net must land within 1.5 percent of `volumes.net_total_l`.

Changes to Plan 1 starting values, all recorded in the construction and voicing notes by Task 13: `MAX_PORT_DIAMETER_MM` 150 to 153.2 (the 6 inch tube), the round port start 75 to 77.3 mm (the 3 inch tube), the shell margin 25 to 44 mm, the 2x12 cutout gap 25 to 68 mm (so the 2x12 width floor moves from 641 to 722 mm internal, and the stereo floor no longer adds the divider separately), a new height floor, and 2 mm on both floors for the hardwood line (its 19 mm panels take 1 mm per side from the 18 mm voicing box). A round port is snapped up to the next tube after the air-speed loop and re-solved, the sheet's prediction follows the tube (the fix-wave rule), and a warning names the snap. `dims_for_volume` re-applies the floors after every rescale (before this a width floor could shrink the height under its own floor on rescale), and both floors are checked against the size limit (a floor above the limit raises, as the pinned width already did). The volumes identity gains `inside_parts_l`, the cleats, stiffeners, mono 2x12 brace, slot shelf and cheeks, tube wall and flange ring that the generator builds inside the air box, estimated the way `scripts/cablayout.py` lays them out, and `port_l` becomes the port air inside the box; both change every sheet's net (the site box drops from 44.1 to 42.5 L closed) so the whole calibration table moves.

- [ ] **Step 1: Write the failing tests**

In `scripts/test_cabvoice.py` replace these four tests with the versions below:

```python
def test_size_port_grows_when_too_short(drv):
    # 60 L at 60 Hz: a 75 mm port needs a negative length, about 100 mm works,
    # which snaps up to the 101.5 mm (4 inch) tube
    p = cabvoice.size_port(drv, 60.0, 60.0, diameter_mm=75.0)
    assert p.diameter_mm == 101.5
    assert p.length_mm >= cabvoice.MIN_PORT_LENGTH_MM
    assert not any("too short" in w for w in p.warnings)
    assert any(w.startswith("port diameter snapped to the 101.5 mm tube") for w in p.warnings)
```

```python
def test_dims_for_volume_min_width_for_two_drivers():
    min_w = cabvoice.min_internal_width_mm(2, 283.0)
    assert min_w == pytest.approx(722.0)
    box = cabvoice.dims_for_volume(90.0, min_internal_width_mm=min_w)
    assert box.internal_mm[0] == pytest.approx(722.0)
    assert box.gross_l == pytest.approx(90.0, abs=0.01)
```

```python
def test_propose_closed_ported_1x12(drv, tone):
    tone["low_end"] = "balanced"
    tone["min_power_w"] = 90              # a 60 W amp
    v = cabvoice.propose([drv], [16], "closed-ported", tone, name="test-1x12")
    assert v.mode == "propose" and v.name == "test-1x12"
    assert v.volumes["method"] == "thiele-small"
    assert v.volumes["per_driver_net_l"] == pytest.approx(60.0)
    assert v.port is not None and v.port["shape"] == "round"
    assert v.prediction["model"] == "thiele-small vented"
    assert v.prediction["fb_hz"] == pytest.approx(60.0)
    assert v.wiring["recommended"]["impedance_ohm"] == 16
    assert v.blockers == []
    assert v.power["status"] == "warning"          # 60 W handling under the 90 W target
    assert v.box["external_mm"][0] > v.box["internal_mm"][0]
    assert v.volumes["gross_l"] == pytest.approx(
        v.volumes["net_total_l"] + v.volumes["displacement_l"] + v.volumes["port_l"]
        + v.volumes["inside_parts_l"], abs=0.05)
    assert v.volumes["inside_parts_l"] > 1.0        # cleats and stiffeners of a 1x12
    assert v.prediction_status == "unverified, ears only"
```

```python
def test_propose_stereo_2x12_closed(drv, tone):
    tone["impedance_options_ohm"] = [16]
    v = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="stereo")
    assert v.enclosure["chambers"] == 2
    assert v.volumes["divider_l"] > 0
    assert len(v.wiring["options"]) == 2
    assert len(v.power["per_side"]) == 2
    assert v.prediction["model"] == "thiele-small closed"
    # each chamber: 44 mm to its shell wall, the cutout, 25 mm to the divider
    assert v.box["chamber_internal_width_mm"] >= (
        drv.cutout_mm + cabvoice.SHELL_MARGIN_MM + cabvoice.CUTOUT_MARGIN_MM - 1e-6)
```

```python
def test_propose_stereo_volumes_reconcile(drv, tone):
    tone["impedance_options_ohm"] = [16]
    v = cabvoice.propose([drv, drv], [16, 16], "closed-ported", tone, jack_config="stereo")
    vol = v.volumes
    parts = (vol["net_total_l"] + vol["displacement_l"] + vol["brace_l"] + vol["port_l"]
             + vol["divider_l"] + vol["inside_parts_l"])
    assert vol["gross_l"] == pytest.approx(parts, abs=0.01)
    # port_l is the air inside the box: the tube's length through the back panel is outside
    inside = v.port["area_cm2"] / 1e4 * (v.port["length_mm"] - cabvoice.BACK_MM)
    assert vol["port_l"] == pytest.approx(2 * inside, abs=1e-6)
    assert vol["port_l"] < 2 * v.port["volume_l"]
```

```python
def test_propose_impossible_box_presents_tradeoff(drv, tone, speakers_dir, tmp_path):
    tone["low_end"] = "big"                  # 68 L per driver against the site's 45.6 L box
    c = cabvoice.Constraints(max_external_mm=(508.0, 457.2, 279.4))
    v = cabvoice.propose([drv], [16], "closed", tone, constraints=c)
    assert v.volumes["gross_l"] == pytest.approx(45.6, abs=0.05)
    assert v.prediction["qtc"] == pytest.approx(cabvoice.closed_box(drv, v.volumes["per_driver_net_l"]).qtc)
    blocker = next(b for b in v.blockers if "cannot fit the size limit" in b)
    assert "71.1 L" in blocker and "45.6 L" in blocker and "Qtc" in blocker
    assert not any("cannot reach" in w for w in v.warnings)
    big_tone = tmp_path / "tone.json"
    big_tone.write_text(json.dumps(tone))
    out = tmp_path / "out"
    rc = cabvoice.main(["propose", "--speakers-dir", str(speakers_dir), "--speaker", "test-driver",
                        "--impedance", "16", "--enclosure", "closed", "--tone", str(big_tone),
                        "--max-external", "508", "457.2", "279.4", "--out", str(out)])
    assert rc == 2
    assert "cannot fit the size limit" in json.loads((out / "voicing.json").read_text())["blockers"][0]
```

```python
def test_evaluate_site_default_closed(drv, tone):
    v = cabvoice.evaluate([drv], [16], "closed", tone, SITE_INTERNAL, name="site-closed")
    assert v.mode == "evaluate"
    assert v.volumes["gross_l"] == pytest.approx(45.6, abs=0.05)
    # 45.6 gross, 1.5 L driver, 1.58 L of cleats and stiffeners (inside_parts_l)
    assert v.volumes["inside_parts_l"] == pytest.approx(1.58, abs=0.01)
    assert v.volumes["net_total_l"] == pytest.approx(42.5, abs=0.05)
    # alpha = 60 / 42.5 = 1.41, Qtc = 0.4 * sqrt(2.41) = 0.621
    assert v.prediction["qtc"] == pytest.approx(0.621, abs=0.005)
    assert v.prediction["character"] == "tight"
    assert v.box["external_in"] == pytest.approx((20.0, 18.0, 11.0), abs=0.01)
```

```python
def test_evaluate_ported_reports_tuning_from_port(drv, tone):
    port = cabvoice.port_dims(44.0, 70.0, diameter_mm=100.0)
    port.length_mm = 23.0
    v = cabvoice.evaluate([drv], [16], "closed-ported", tone, SITE_INTERNAL, port=port)
    assert 65.0 < v.prediction["fb_hz"] < 75.0
    assert v.port["volume_l"] == pytest.approx(0.18, abs=0.01)      # the whole 23 mm tube
    assert v.volumes["port_l"] == pytest.approx(0.086, abs=0.005)   # the 11 mm inside the box
    assert v.port["length_mm"] == 23.0
    assert v.port["air_speed_ms"] > 0
```

```python
@pytest.mark.parametrize("slug,enclosure,jack,n", _matrix_params())
def test_evaluate_reproduces_propose(tone, slug, enclosure, jack, n):
    d = cabvoice.load_speaker(slug, CATALOG)
    z = 16 if 16 in d.impedance_ohm else d.impedance_ohm[0]
    p = cabvoice.propose([d] * n, [z] * n, enclosure, tone, jack_config=jack, name=slug)
    e = cabvoice.evaluate([d] * n, [z] * n, enclosure, tone, p.box["internal_mm"],
                          jack_config=jack, port=_port_from_json(p.port), name=slug)
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

```python
def test_propose_mono_2x12_uses_one_port_per_driver(tone):
    d = _driver(**CANNABIS_REX)
    one = cabvoice.propose([d], [16], "closed-ported", tone)
    two = cabvoice.propose([d, d], [16, 16], "closed-ported", tone, jack_config="mono")
    assert two.port["count"] == 2 and one.port["count"] == 1
    assert two.construction["port_count"] == 2
    assert not any("too short" in w or "port clamped" in w for w in two.warnings)
    assert two.port["diameter_mm"] == pytest.approx(one.port["diameter_mm"])
    assert two.port["length_mm"] == pytest.approx(one.port["length_mm"])
    assert two.port["air_speed_ms"] == pytest.approx(one.port["air_speed_ms"])
    assert two.volumes["port_l"] == pytest.approx(2 * one.volumes["port_l"])
    assert two.prediction["fb_hz"] == pytest.approx(one.prediction["fb_hz"], abs=1e-6)
    single = cabvoice.propose([d, d], [16, 16], "closed-ported", tone, jack_config="mono",
                              constraints=cabvoice.Constraints(port_count=1))
    # one shared port: the same largest tube cannot be long enough for twice the
    # drivers, so it is clamped at 20 mm, tunes low, and moves more air per area
    assert single.port["count"] == 1
    assert single.port["diameter_mm"] >= two.port["diameter_mm"]
    assert single.port["air_speed_ms"] > two.port["air_speed_ms"]
    assert any("port clamped at the size cap" in w for w in single.warnings)
```


Append at the end of the file:

```python
# ---- Plan 2 Task 2: tube table, margins, floors -------------------------

def test_snap_tube_id_table():
    assert cabvoice.PORT_TUBE_ID_MM == (52.0, 77.3, 101.5, 153.2)
    assert set(cabvoice.PORT_TUBE_OD_MM) == set(cabvoice.PORT_TUBE_ID_MM)
    assert cabvoice.MAX_PORT_DIAMETER_MM == 153.2
    assert cabvoice.DEFAULT_PORT_DIAMETER_MM == 77.3
    for solved, tube in ((40.0, 52.0), (52.0, 52.0), (75.0, 77.3), (77.3, 77.3),
                         (100.0, 101.5), (120.0, 153.2), (200.0, 153.2)):
        assert cabvoice.snap_tube_id(solved) == tube, solved


def test_size_port_snaps_round_ports_and_leaves_slots(drv):
    p = cabvoice.size_port(drv, 40.0, 60.0, diameter_mm=75.0)
    assert p.diameter_mm == 77.3
    assert any(w == "port diameter snapped to the 77.3 mm tube (from 75.0 mm)" for w in p.warnings)
    q = cabvoice.size_port(drv, 40.0, 60.0, diameter_mm=77.3)
    assert q.diameter_mm == 77.3 and not any("snapped" in w for w in q.warnings)
    s = cabvoice.size_port(drv, 40.0, 60.0, slot_mm=(200.0, 30.0))
    assert s.shape == "slot" and s.slot_w_mm == 200.0
    assert not any("snapped" in w for w in s.warnings)


def test_propose_port_is_a_purchasable_tube(drv, tone):
    v = cabvoice.propose([drv], [16], "closed-ported", tone)
    assert v.port["diameter_mm"] in cabvoice.PORT_TUBE_ID_MM
    tuned = cabvoice.port_tuning_hz(v.volumes["per_chamber_net_l"] / 1e3,
                                    v.port["area_cm2"] / 1e4, v.port["length_mm"] / 1e3)
    assert v.prediction["fb_hz"] == pytest.approx(tuned, abs=1e-9)


def test_cli_port_diameter_default_is_the_tube_start():
    args = cabvoice._build_parser().parse_args(
        ["propose", "--speaker", "x", "--impedance", "8", "--enclosure", "closed",
         "--tone", "t.json", "--out", "o"])
    assert args.port_diameter == cabvoice.DEFAULT_PORT_DIAMETER_MM
    assert cabvoice.Constraints().port_diameter_mm == cabvoice.DEFAULT_PORT_DIAMETER_MM


def test_min_internal_width_and_height():
    assert cabvoice.SHELL_MARGIN_MM == 44.0 and cabvoice.CUTOUT_GAP_MM == 68.0
    assert cabvoice.CUTOUT_MARGIN_MM == 25.0
    assert cabvoice.min_internal_width_mm(1, 283.0) == pytest.approx(371.0)
    assert cabvoice.min_internal_width_mm(2, 283.0) == pytest.approx(722.0)
    assert cabvoice.min_internal_height_mm(283.0) == pytest.approx(371.0)
    assert cabvoice.min_internal_height_mm(283.0, None) == pytest.approx(371.0)
    assert cabvoice.min_internal_height_mm(283.0, 40.0) == pytest.approx(429.0)


def test_dims_for_volume_height_floor():
    box = cabvoice.dims_for_volume(30.0, min_internal_height_mm=429.0)
    assert box.internal_mm[1] == pytest.approx(429.0)
    assert box.gross_l == pytest.approx(30.0, abs=0.01)
    free = cabvoice.dims_for_volume(30.0)
    assert box.internal_mm[0] < free.internal_mm[0] and box.internal_mm[2] < free.internal_mm[2]
    with pytest.raises(ValueError, match="height"):
        cabvoice.dims_for_volume(60.0, min_internal_height_mm=429.0,
                                 max_external_mm=(600.0, 457.2, 400.0))
    with pytest.raises(ValueError, match="width"):      # the width floor gets the same guard
        cabvoice.dims_for_volume(90.0, min_internal_width_mm=722.0,
                                 max_external_mm=(700.0, 600.0, 400.0))


def test_propose_stereo_and_mono_2x12_share_the_width_floor(drv, tone):
    tone["impedance_options_ohm"] = [16]
    floor = cabvoice.min_internal_width_mm(2, drv.cutout_mm)
    mono = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="mono")
    stereo = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="stereo")
    assert mono.box["internal_mm"][0] == pytest.approx(floor)
    assert stereo.box["internal_mm"][0] == pytest.approx(floor)
    assert stereo.box["chamber_internal_width_mm"] == pytest.approx((floor - cabvoice.PANEL_MM) / 2)


def test_propose_slot_port_raises_the_height_floor(drv, tone):
    c = cabvoice.Constraints(port_slot_mm=(472.0, 40.0), pinned_external_width_mm=508.0)
    v = cabvoice.propose([drv], [16], "closed-ported", tone, constraints=c)
    assert v.port["shape"] == "slot"
    floor = cabvoice.min_internal_height_mm(drv.cutout_mm, v.port["slot_h_mm"])
    assert floor >= 429.0
    assert v.box["internal_mm"][1] >= floor - 1e-6
    plain = cabvoice.propose([drv], [16], "closed", tone,
                             constraints=cabvoice.Constraints(pinned_external_width_mm=508.0))
    assert plain.box["internal_mm"][1] < 429.0


def test_propose_hardwood_floors_add_two_mm(drv, tone):
    tone["impedance_options_ohm"] = [16]
    floor_w = cabvoice.min_internal_width_mm(2, drv.cutout_mm)
    for line, extra in (("tolex", 0.0), ("hardwood", cabvoice.HARDWOOD_FLOOR_EXTRA_MM)):
        v = cabvoice.propose([drv, drv], [16, 16], "closed", tone, jack_config="mono",
                             constraints=cabvoice.Constraints(line=line))
        assert v.box["internal_mm"][0] == pytest.approx(floor_w + extra)
    # a 30 L box pinned 700 mm wide would scale to about 300 mm tall: the height floor holds it
    small = _driver(vas_l=20.0)
    for line, extra in (("tolex", 0.0), ("hardwood", cabvoice.HARDWOOD_FLOOR_EXTRA_MM)):
        v = cabvoice.propose([small], [16], "closed", tone,
                             constraints=cabvoice.Constraints(line=line, pinned_external_width_mm=700.0))
        assert v.box["internal_mm"][1] == pytest.approx(cabvoice.min_internal_height_mm(283.0) + extra)
        assert v.box["internal_mm"][1] >= 371.0 + extra - 1e-6


def test_propose_2x12_slot_holds_both_floors(drv, tone):
    tone["impedance_options_ohm"] = [16]
    for line, extra in (("tolex", 0.0), ("hardwood", cabvoice.HARDWOOD_FLOOR_EXTRA_MM)):
        for jack in ("mono", "stereo"):
            c = cabvoice.Constraints(port_slot_mm=(352.0, 40.0), line=line)
            v = cabvoice.propose([drv, drv], [16, 16], "closed-ported", tone, jack_config=jack,
                                 constraints=c)
            w, h, _ = v.box["internal_mm"]
            assert w >= cabvoice.min_internal_width_mm(2, drv.cutout_mm) + extra - 1e-6, (line, jack)
            floor_h = cabvoice.min_internal_height_mm(drv.cutout_mm, v.port["slot_h_mm"]) + extra
            assert h >= floor_h - 1e-6, (line, jack, h, floor_h)
            assert v.volumes["gross_l"] == pytest.approx(
                v.volumes["net_total_l"] + v.volumes["displacement_l"] + v.volumes["port_l"]
                + v.volumes["divider_l"] + v.volumes["inside_parts_l"], abs=0.01)


def test_inside_parts_site_box_by_hand():
    site = (472.0, 421.2, 229.4)
    # 1x12 closed: baffle cleats 2 x 472 x 18 x 18 + 2 x (421.2 - 36) x 18 x 18 = 0.555 L,
    # the same again at the back = 0.555 L, top and bottom stiffeners (472 > 450)
    # 2 x 18 x 40 x (229.4 - 36) = 0.278 L, back stiffener 18 x 40 x (421.2 - 156) = 0.191 L
    closed = cabvoice.inside_parts_l(site, "closed", 1, 1, "mono", None, "tolex")
    assert closed == pytest.approx(0.555 + 0.555 + 0.278 + 0.191, rel=0.05)
    # a 101.5 mm tube 40 mm long adds its wall inside the box (28 mm) and the ring:
    # pi/4 (114.3^2 - 101.5^2) x 28 = 0.061 L, pi/4 (174.3^2 - 114.3^2) x 12 = 0.163 L
    port = cabvoice.port_dims(1.0, 1.0, diameter_mm=101.5)
    port.length_mm = 40.0
    ported = cabvoice.inside_parts_l(site, "closed-ported", 1, 1, "mono", port, "tolex")
    assert ported == pytest.approx(closed + 0.061 + 0.163, rel=0.05)
    assert ported == pytest.approx(1.80, rel=0.05)
    # a mono 2x12 at the floor width adds the brace and loses the top and bottom stiffeners
    wide = (722.0, 421.2, 229.4)
    two = cabvoice.inside_parts_l(wide, "closed", 2, 1, "mono", None, "tolex")
    one_wide = cabvoice.inside_parts_l(wide, "closed", 1, 1, "mono", None, "tolex")
    assert two - one_wide == pytest.approx(18 * 60 * 421.2 / 1e6 - 2 * 18 * 40 * 193.4 / 1e6, abs=0.01)
    # a slot: shelf full width x length x 18, no bottom baffle cleat, shorter side cleats
    slot = cabvoice.port_dims(1.0, 1.0, slot_mm=(472.0, 40.0))
    slot.length_mm = 120.0
    slotted = cabvoice.inside_parts_l(site, "closed-ported", 1, 1, "mono", slot, "tolex")
    shelf = 472 * 120 * 18 / 1e6
    lost_cleats = (472 * 18 * 18 + 2 * 40 * 18 * 18) / 1e6      # bottom cleat, 40 mm off each side cleat
    lost_bottom_stiffener = 18 * 40 * (193.4 - (229.4 - 120.0)) / 1e6
    assert slotted == pytest.approx(closed + shelf - lost_cleats - lost_bottom_stiffener, abs=0.01)


def test_evaluate_site_box_reports_inside_parts(drv, tone):
    port = cabvoice.port_dims(1.0, 1.0, diameter_mm=101.5)
    port.length_mm = 40.0
    v = cabvoice.evaluate([drv], [16], "closed-ported", tone, SITE_INTERNAL, port=port)
    assert v.volumes["inside_parts_l"] == pytest.approx(1.80, abs=0.02)
    assert v.volumes["port_l"] == pytest.approx(0.008091 * 28.0, abs=0.002)
    assert v.volumes["net_total_l"] == pytest.approx(42.1, abs=0.05)
    md = cabvoice.render_markdown(v)
    assert "| Inside parts (cleats, stiffeners, shelf, ring) | 1.80 L |" in md
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q -k "snap or floor or height or purchasable or tube_start or min_internal or too_short or two_drivers or stereo_2x12 or one_port_per_driver"`
Expected: FAIL (`snap_tube_id` undefined, old constants).

- [ ] **Step 3: Engine changes**

In `scripts/cabvoice.py` replace each of these with the version below (full text).

port constants (replace the two lines `MIN_PORT_LENGTH_MM = 20.0` and `MAX_PORT_DIAMETER_MM = 150.0`):

```python
MIN_PORT_LENGTH_MM = 20.0
# Purchasable round port tubes: Schedule 40 PVC or ABS inside diameters for
# 2, 3, 4, and 6 inch nominal pipe, with their outside diameters. Starting
# values (see speaker-cab-construction); the hard maximum is the largest tube.
PORT_TUBE_ID_MM = (52.0, 77.3, 101.5, 153.2)
PORT_TUBE_OD_MM = {52.0: 60.3, 77.3: 88.9, 101.5: 114.3, 153.2: 168.3}
MAX_PORT_DIAMETER_MM = 153.2
DEFAULT_PORT_DIAMETER_MM = 77.3
```

`snap_tube_id` (new, directly above `size_port`):

```python
def snap_tube_id(diameter_mm: float) -> float:
    """Smallest purchasable tube inside diameter not below diameter_mm, else the largest."""
    for tube in PORT_TUBE_ID_MM:
        if tube >= diameter_mm - 1e-9:
            return tube
    return PORT_TUBE_ID_MM[-1]
```

`size_port`:

```python
def size_port(driver: Driver, vb_l: float, fb_hz: float,
              diameter_mm: float = DEFAULT_PORT_DIAMETER_MM,
              slot_mm: tuple | None = None) -> Port:
    """Port for (vb, fb), enlarged in 10 percent area steps until the
    worst-case air speed is under PORT_V_MAX and the physical length is at
    least MIN_PORT_LENGTH_MM. Stops at the MAX_PORT_DIAMETER_MM equivalent
    area and leaves the warnings in place for the caller. A round port is
    then snapped up to the next purchasable tube (PORT_TUBE_ID_MM) and
    re-solved, so the sheet describes a tube that can be bought."""
    max_area_cm2 = math.pi * (MAX_PORT_DIAMETER_MM / 20.0) ** 2

    def build(dia, slot):
        p = port_dims(vb_l, fb_hz, diameter_mm=None if slot else dia, slot_mm=slot)
        p.air_speed_ms = port_air_speed(driver, fb_hz, p.area_cm2)
        return p

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

box constants (replace the block from `MM_PER_INCH` to `BASE_EXTERNAL_IN`):

```python
MM_PER_INCH = 25.4
PANEL_MM = 18.0
BACK_MM = 12.0
BAFFLE_MM = 18.0
RECESS_MM = 20.0
CUTOUT_MARGIN_MM = 25.0    # cutout edge to brace or divider
SHELL_MARGIN_MM = 44.0     # cutout edge to shell inner face: grill strip 40 + 2 clearance + 2
CUTOUT_GAP_MM = 68.0       # between the two cutouts of a 2x12: brace or divider 18 + 2 x 25
HARDWOOD_FLOOR_EXTRA_MM = 2.0   # the hardwood line's 19 mm panels take 1 mm per side from the 18 mm box
BASE_EXTERNAL_IN = (20.0, 18.0, 11.0)
# Parts the generator builds inside the air box (knowledge/speaker-cab-construction):
CLEAT_MM = 18.0                 # 18 x 18 cleats along the baffle and the back
STIFFENER_MM = (18.0, 40.0)     # 18 proud, 40 flat, across any span over SPAN_MAX_MM
SPAN_MAX_MM = 450.0
BRACE_MM = (18.0, 60.0)         # center brace on a mono 2x12
JACK_PLATE_H_MM = 70.0          # jack plate cutout height; the back stiffener stops above it
JACK_CLEAR_MM = 25.0
FLANGE_RING_T_MM = 12.0         # plywood flange ring on the inside of the back for a round port
FLANGE_RING_EXTRA_MM = 60.0     # ring outside diameter = tube outside diameter + 60
TUBE_WALL_FALLBACK_MM = 5.5     # wall assumed for a tube diameter outside PORT_TUBE_ID_MM
```

`min_internal_width_mm`:

```python
def min_internal_width_mm(driver_count: int, cutout_mm: float) -> float:
    """Cutouts side by side, 44 mm to each shell wall and a 68 mm gap between
    two (the brace or divider plus 25 mm each side); the same floor for a mono
    and a stereo 2x12 because the divider replaces the brace."""
    return driver_count * cutout_mm + (driver_count - 1) * CUTOUT_GAP_MM + 2 * SHELL_MARGIN_MM
```

`min_internal_height_mm` (new):

```python
def min_internal_height_mm(cutout_mm: float, slot_h_mm: float | None = None) -> float:
    """Cutout plus 44 mm top and bottom; a front slot port adds its height and
    the 18 mm shelf under the baffle."""
    extra = (slot_h_mm + BAFFLE_MM) if slot_h_mm else 0.0
    return cutout_mm + 2 * SHELL_MARGIN_MM + extra
```

`dims_for_volume`:

```python
def dims_for_volume(gross_l: float, pinned_external_width_mm: float | None = None,
                    min_internal_width_mm: float | None = None,
                    max_external_mm: tuple | None = None,
                    min_internal_height_mm: float | None = None, strict: bool = True,
                    **panel_kwargs) -> Box:
    """Internal dimensions for a gross volume, starting from the site box
    proportions. Fixed axes come from a pinned width, the driver minimum
    width, the minimum height, or external limits; free axes scale together
    to hit the volume. When the limits cannot hold the volume, strict raises;
    otherwise the largest box that fits comes back with a "cannot reach" warning."""
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
    max_internal = None
    if max_external_mm is not None:
        max_internal = internal_from_external(max_external_mm, **panel_kwargs)
        if fixed[0] and dims[0] > max_internal[0]:
            raise ValueError(
                f"width {dims[0]:.1f} mm internal (pinned or the driver-count minimum) "
                f"exceeds the size limit {max_internal[0]:.1f} mm internal")
        if min_internal_width_mm is not None and min_internal_width_mm > max_internal[0] + 1e-9:
            raise ValueError(
                f"width {min_internal_width_mm:.1f} mm internal (the driver-count minimum) "
                f"exceeds the size limit {max_internal[0]:.1f} mm internal")
        if min_internal_height_mm is not None and min_internal_height_mm > max_internal[1] + 1e-9:
            raise ValueError(
                f"height {min_internal_height_mm:.1f} mm internal (the cutout minimum) "
                f"exceeds the size limit {max_internal[1]:.1f} mm internal")

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

`_port_inside_l` and `inside_parts_l` (new, directly above the tone target section):

```python
def _port_inside_l(port: Port) -> float:
    """Port air inside the internal box, liters: a round tube's length through
    the back panel and a slot's length through the baffle lie outside the box."""
    panel = BAFFLE_MM if port.shape == "slot" else BACK_MM
    return port.area_cm2 / 1e4 * max(port.length_mm - panel, 0.0)


def inside_parts_l(internal_mm, enclosure: str, driver_count: int, chambers: int,
                   jack_config: str, port: Port | None, line: str,
                   port_count: int | None = None) -> float:
    """Liters taken by the parts the generator builds inside the air box that
    the brace, divider, and port terms do not carry, estimated the way
    scripts/cablayout.py builds them: 18 x 18 cleats along the baffle (top,
    bottom unless a slot port, two outer sides) and the back (closed: a full
    frame; open: top, bottom, and the panel-height side cleats), the mono 2x12
    center brace, 18 x 40 stiffeners across any shell or back span over 450 mm
    between glued members (the back one stops above the jack plate), the slot
    shelf and cheeks, and a round port's tube wall and flange ring. Every part
    is birch on both lines; line is accepted for the call signature."""
    w, h, d = internal_mm
    per_chamber = driver_count // chambers
    count = port_count or per_chamber
    closed = enclosure in ("closed", "closed-ported")
    slot = port is not None and port.shape == "slot"
    slot_h = port.slot_h_mm if slot else 0.0
    shelf = port.length_mm if slot else 0.0
    w_c = (w - PANEL_MM) / 2.0 if chambers == 2 else w
    c2 = CLEAT_MM ** 2
    total = 0.0
    # baffle cleats (floating baffle, the default)
    total += chambers * w_c * c2
    if not slot:
        total += chambers * w_c * c2
    side_len = h - CLEAT_MM - ((slot_h + BAFFLE_MM) if slot else CLEAT_MM)
    total += 2 * side_len * c2
    # back cleats
    total += 2 * chambers * w_c * c2
    if closed:
        total += 2 * (h - 2 * CLEAT_MM) * c2
    else:
        h_p = (1.0 - OPEN_FRACTION[enclosure]) * h / 2.0
        total += 4 * (h_p - CLEAT_MM) * c2
    # center brace, bottom end on the shelf with a slot
    if driver_count == 2 and chambers == 1:
        total += BRACE_MM[0] * BRACE_MM[1] * (h - ((slot_h + BAFFLE_MM) if slot else 0.0))
    # stiffeners
    sw, sd = STIFFENER_MM
    if chambers == 2:
        segs = [w_c, w_c]
    elif driver_count == 2:
        segs = [(w - BRACE_MM[0]) / 2.0] * 2
    else:
        segs = [w]
    top_len = d - 2 * CLEAT_MM
    bot_len = (d - max(shelf, 2 * CLEAT_MM)) if slot else top_len
    for span in segs:
        if span > SPAN_MAX_MM:
            if top_len > 50.0:
                total += sw * sd * top_len
            if bot_len > 50.0:
                total += sw * sd * bot_len
    if closed:
        back_len = h - CLEAT_MM - (CLEAT_MM + JACK_CLEAR_MM + JACK_PLATE_H_MM + CUTOUT_MARGIN_MM)
        if w_c > SPAN_MAX_MM and back_len > 50.0:
            total += chambers * sw * sd * back_len
    side_span = max(slot_h, h - slot_h - BAFFLE_MM) if slot else h
    if side_span > SPAN_MAX_MM:
        total += 2 * sw * sd * top_len
    # slot shelf, end cheeks, center cheeks
    if slot:
        avail = w_c - (count - 1) * PANEL_MM
        cheek = (avail - count * port.slot_w_mm) / 2.0
        per_chamber_parts = w_c * shelf * BAFFLE_MM + (count - 1) * PANEL_MM * shelf * slot_h
        if cheek > 0.5:
            per_chamber_parts += 2 * cheek * shelf * slot_h
        total += chambers * per_chamber_parts
    # round port: tube wall inside the box and the flange ring (the ring is the
    # whole port when the tube would not reach past the back panel)
    if port is not None and port.shape == "round":
        id_mm, length = port.diameter_mm, port.length_mm
        od = PORT_TUBE_OD_MM.get(id_mm, id_mm + 2 * TUBE_WALL_FALLBACK_MM)
        ring_od = od + FLANGE_RING_EXTRA_MM
        if length > 2 * BACK_MM:
            tube = math.pi / 4.0 * (od ** 2 - id_mm ** 2) * (length - BACK_MM)
            ring = math.pi / 4.0 * (ring_od ** 2 - od ** 2) * FLANGE_RING_T_MM
        else:
            tube = 0.0
            ring = math.pi / 4.0 * (ring_od ** 2 - id_mm ** 2) * max(length - BACK_MM, 0.0)
        total += chambers * count * (tube + ring)
    return total / 1e6
```

`Constraints`:

```python
@dataclass
class Constraints:
    pinned_external_width_mm: float | None = None
    max_external_mm: tuple | None = None
    panel_mm: float = PANEL_MM
    back_mm: float = BACK_MM
    baffle_mm: float = BAFFLE_MM
    recess_mm: float = RECESS_MM
    brace_l: float = 0.0
    port_diameter_mm: float = DEFAULT_PORT_DIAMETER_MM
    port_slot_mm: tuple | None = None
    port_count: int | None = None      # None: one port per driver in the chamber
    line: str = "tolex"
    species: str | None = None
    accept_low_headroom: bool = False

    def __post_init__(self):
        if self.line not in LINES:
            raise ValueError(f"line must be one of {', '.join(LINES)}")
        if self.species is not None:
            self.species = self.species.strip() or None

    def panel_kwargs(self) -> dict:
        return dict(panel_mm=self.panel_mm, back_mm=self.back_mm,
                    baffle_mm=self.baffle_mm, recess_mm=self.recess_mm)
```

`_volumes`:

```python
def _volumes(method, per_driver_net, per_chamber_drivers, chambers, displacement, brace_l,
             port_l_total, divider_l, inside_l, gross_l) -> dict:
    """gross = net + displacement + brace + port (air inside the box) + divider
    + inside_parts; port.volume_l on the port dict is the whole port."""
    chamber_net = per_driver_net * per_chamber_drivers
    return {"method": method, "per_driver_net_l": per_driver_net,
            "per_chamber_net_l": chamber_net, "net_total_l": chamber_net * chambers,
            "displacement_l": displacement, "brace_l": brace_l, "port_l": port_l_total,
            "divider_l": divider_l, "inside_parts_l": inside_l, "gross_l": gross_l}
```

`propose`:

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
    last_gross = None
    for _ in range(10):   # until the gross settles: port, divider, and inside parts depend on the box
        gross = net_total + displacement + c.brace_l + port_l * chambers + divider_l + inside_l
        slot_h = None
        if enclosure == "closed-ported" and c.port_slot_mm:
            slot_h = port.slot_h_mm if port is not None else c.port_slot_mm[1]
        box = dims_for_volume(gross, c.pinned_external_width_mm, min_w, c.max_external_mm,
                              min_internal_height_mm=min_internal_height_mm(cutout, slot_h) + floor_extra,
                              strict=False, **pk)
        w_int, h_int, d_int = box.internal_mm
        divider_l = _divider_l(chambers, h_int, d_int, c)
        if any(w.startswith("cannot reach") for w in box.warnings):
            # The size limit wins: voice the box that fits and present the trade-off.
            box.warnings = [w for w in box.warnings if not w.startswith("cannot reach")]
            limited = True
            net_total = (box.gross_l - displacement - c.brace_l - port_l * chambers - divider_l
                         - inside_l)
            chamber_net = net_total / chambers
            per_driver_net = chamber_net / per_chamber_drivers
        if enclosure == "closed-ported":
            port = size_port(_air_speed_driver(lead, per_chamber_drivers / port_count, warnings),
                             chamber_net / port_count, fb, diameter_mm=c.port_diameter_mm,
                             slot_mm=c.port_slot_mm)
            port_l = _port_inside_l(port) * port_count
        inside_l = inside_parts_l(box.internal_mm, enclosure, count, chambers, jack_config, port,
                                  c.line, port_count)
        if last_gross is not None and abs(box.gross_l - last_gross) < 0.001:
            break
        last_gross = box.gross_l
    warnings.extend(box.warnings)
    chamber_w = _chamber_w(chambers, w_int, c)
    port_dict = None
    if port is not None:
        fb_actual, port_dict = _port_report(lead, per_chamber_drivers, chamber_net, port,
                                            port_count, warnings)
        if abs(fb_actual - fb) > 0.5:
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

`evaluate`:

```python
def evaluate(drivers: list, impedances: list, enclosure: str, tone: dict,
             internal_mm: tuple, jack_config: str = "mono", port: Port | None = None,
             constraints: Constraints | None = None, name: str = "cab") -> Voicing:
    """Voicing of an existing box. A supplied port is one of constraints.port_count
    identical ports per chamber (default one per driver, as in propose)."""
    c = constraints or Constraints()
    lead, count, chambers, per_chamber_drivers, warnings = _setup(
        drivers, impedances, enclosure, tone, jack_config)
    if enclosure == "closed-ported" and port is None:
        raise ValueError("closed-ported evaluate needs a port (from port_dims) with its length")
    if enclosure != "closed-ported" and port is not None:
        raise ValueError(f"a port does not apply to a {enclosure} enclosure")
    blockers = []
    box = make_box(tuple(internal_mm), **c.panel_kwargs())
    warnings.extend(box.warnings)
    w_int, h_int, d_int = box.internal_mm
    divider_l = _divider_l(chambers, h_int, d_int, c)
    displacement = _displacement(drivers, warnings)
    port_count = c.port_count or per_chamber_drivers
    port_l = 0.0
    if port is not None:
        port_l = _port_inside_l(port) * port_count
    inside_l = inside_parts_l(box.internal_mm, enclosure, count, chambers, jack_config, port,
                              c.line, port_count)
    net_total = (box.gross_l - displacement - c.brace_l - port_l * chambers - divider_l
                 - inside_l)
    if net_total <= 0:
        raise ValueError("box has no net volume left after displacement, brace, port, divider, "
                         "and inside parts")
    chamber_net = net_total / chambers
    per_driver_net = chamber_net / per_chamber_drivers
    chamber_w = _chamber_w(chambers, w_int, c)
    fb, port_dict = None, None
    if enclosure == "closed-ported":
        fb, port_dict = _port_report(lead, per_chamber_drivers, chamber_net, port, port_count,
                                     warnings)
    if not lead.has_ts() and enclosure in ("closed", "closed-ported"):
        detail = "tuning reported, " if enclosure == "closed-ported" else ""
        warnings.append(f"{lead.slug}: no Thiele-Small data ({lead.data_status}); "
                        f"{detail}no response prediction")
    prediction = _predict(lead, enclosure, per_driver_net, fb, chamber_w, h_int, d_int)
    wiring_dict, power_dict = _electrical(drivers, impedances, tone, jack_config, c,
                                          warnings, blockers)
    volumes = _volumes("evaluate", per_driver_net, per_chamber_drivers, chambers, displacement,
                       c.brace_l, port_l * chambers, divider_l, inside_l, box.gross_l)
    return _assemble(name, "evaluate", tone, drivers, impedances, enclosure, jack_config, chambers,
                     count, volumes, box, chamber_w, port_dict, prediction, wiring_dict,
                     power_dict, warnings, blockers, c)
```

`render_markdown` (two rows in the Volumes table: replace the `| Port |` line and add the inside parts row after `| Divider |`):

```python
        f"| Port air inside the box | {vol['port_l']:.2f} L |",
        f"| Divider | {vol['divider_l']:.2f} L |",
        f"| Inside parts (cleats, stiffeners, shelf, ring) | {vol['inside_parts_l']:.2f} L |",
```

`_build_parser`:

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
        p.add_argument("--brace-l", type=float, default=0.0)
        p.add_argument("--line", choices=LINES, default="tolex")
        p.add_argument("--species", default=None)
        p.add_argument("--accept-low-headroom", action="store_true")
        p.add_argument("--name", default="cab")
        p.add_argument("--out", required=True, help="directory for voicing.json and voicing.md")

    pp = sub.add_parser("propose")
    common(pp)
    pp.add_argument("--pinned-width", type=float, help="external width mm")
    pp.add_argument("--max-external", type=float, nargs=3, metavar=("W", "H", "D"))
    pp.add_argument("--port-diameter", type=float, default=DEFAULT_PORT_DIAMETER_MM,
                    help="round port start in mm, snapped up to the tube table")
    pp.add_argument("--port-slot", type=float, nargs=2, metavar=("W", "H"))

    pe = sub.add_parser("evaluate")
    common(pe)
    pe.add_argument("--internal", type=float, nargs=3, required=True, metavar=("W", "H", "D"))
    pe.add_argument("--port-diameter", type=float)
    pe.add_argument("--port-slot", type=float, nargs=2, metavar=("W", "H"))
    pe.add_argument("--port-length", type=float)

    pl = sub.add_parser("list")
    pl.add_argument("--speakers-dir", default=str(SPEAKERS_DIR))
    return ap
```


- [ ] **Step 4: Run the tests (calibration test still fails)**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q`
Expected: 367 passed, 1 failed (`test_calibration_table_matches_engine`, the note still holds the Plan 1 table).

- [ ] **Step 5: Regenerate the calibration table**

Run from the vault root: `.venv/bin/python projects/Speaker-cab-system/pipeline/calibration_table.py`
Expected: `wrote 20 rows to .../knowledge/speaker-cab-voicing.md`. Every row changes against Plan 1: the site box net drops from 44.1 (43.6, 43.4 on the Eminence rows) to 42.5 (42.0, 41.8) L with the inside parts deducted, every closed Qtc rises by about 0.006 to 0.01 and three closed F3 values by 1 Hz, the Heritage G12H(55) closed character moves from lean to tight (Qtc 0.599 to 0.605 across the 0.6 threshold), and the Eminence Red White and Blues notes read "port too short (6.5 mm)" and "tuned 74.4 Hz" (its clamped port now stops at the 153.2 mm tube). Proposed ported net and Fb columns are unchanged. The section must read (the date is the run date):

```markdown
## Calibration table

Calibration table, every number prediction_status "unverified, ears only". Generated 2026-09-10 with `evaluate` (closed, site box 472 x 421.2 x 229.4 mm internal) and `propose` (closed-ported, low_end balanced), 16 ohm where the note lists it (voiced with the note's 8 ohm T/S set, see Model limits), amp 40 W.

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
| [[eminence-red-white-and-blues]] | datasheet | 42.0 | 1.040 | big | 114 | 66.0 | 74 | punchy | port too short (6.5 mm) for Fb 78 Hz in 66.0 L; clamped to 20 mm, reduce port area or lower Fb; port clamped at the size cap: tuned 74.4 Hz, target 78.0 Hz; lower Fb or use a smaller box |
| [[eminence-swamp-thang]] | datasheet | 41.8 | 0.747 | tight | 131 | 41.3 | 78 | flat |  |
| [[eminence-texas-heat]] | datasheet | 42.0 | 0.967 | balanced | 95 | 50.9 | 63 | punchy |  |
| [[eminence-tonker]] | datasheet | 41.8 | 0.633 | tight | 138 | 34.1 | 71 | flat |  |
| [[jensen-c12n]] | datasheet | 42.5 | 1.262 | peaky | 102 | 64.3 | 45 | boomy | jensen-c12n: Thiele-Small volume 22.6 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L; ported alignment stays boomy at the practical limits; consider a closed back or a lower-Qts driver |
| [[jensen-p12n]] | datasheet | 42.5 | 1.037 | big | 95 | 67.4 | 62 | punchy |  |
| [[wgs-et65]] | estimated | 42.5 | 1.235 | peaky | 98 | 63.4 | 49 | punchy |  |
| [[wgs-green-beret]] | estimated | 42.5 | 1.454 | peaky | 109 | 64.3 | 45 | boomy | speaker handling 25 W is below the amp's 40 W; wgs-green-beret: Thiele-Small volume 22.0 L for 'balanced' is outside the practical range 30 to 68 L; started from the clamped 30.0 L; ported alignment stays boomy at the practical limits; consider a closed back or a lower-Qts driver |
| [[wgs-veteran-30]] | estimated | 42.5 | 1.023 | big | 103 | 62.5 | 71 | punchy |  |
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd /home/brian/ClaudeProjects/3d-modeling-brain && .venv/bin/python -m pytest scripts/test_cabvoice.py -q`
Expected: 368 passed.

- [ ] **Step 7: Commit**

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
git add scripts/cabvoice.py scripts/test_cabvoice.py knowledge/speaker-cab-voicing.md
git commit -m "Speaker cab plan 2 task 2: port tube table, shell margins, height floor"
```
