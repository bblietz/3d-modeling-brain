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
FIXTURE_ORDERS = ["site-default", "sample-roots-1x12"]
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
    assert f["swatch_finish"] == "![Fender Style Black](images/fender-black.jpg)"
    assert f["swatch_cloth"] == "![British Small Weave Cane](images/cane.jpg)"
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
    assert "![Fender Style Black](images/fender-black.jpg)\nno swatch on file" in proposal
    assert cabreport.swatch("fender style TWEED") == "![fender style TWEED](images/fender-tweed.jpg)"
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
