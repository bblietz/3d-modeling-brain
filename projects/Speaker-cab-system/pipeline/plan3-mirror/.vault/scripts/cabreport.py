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
import cutlist

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


def _fmt_mm(x: float) -> str:
    """The stored figure as it is, never rounded to a whole mm (Brian, 2026-09-19)."""
    return f"{x:.10g}"


def _external(cab: dict) -> tuple:
    """('20 x 18 x 11 in', '508 x 457.2 x 279.4 mm') for W x H x D: shop fractions in
    inches (the cut list's own nearest-16th format), exact mm, no decimal inches."""
    inches = " x ".join(cutlist.inch_frac(v) for v in cab["external_mm"]) + " in"
    mm = " x ".join(_fmt_mm(v) for v in cab["external_mm"]) + " mm"
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
