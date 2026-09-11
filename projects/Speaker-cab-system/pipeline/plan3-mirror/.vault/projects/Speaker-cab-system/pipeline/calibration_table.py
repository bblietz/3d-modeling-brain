"""Regenerate the calibration table in knowledge/speaker-cab-voicing.md from the engine.

Run from anywhere: .venv/bin/python projects/Speaker-cab-system/pipeline/calibration_table.py
scripts/test_cabvoice.py::test_calibration_table_matches_engine pins the note's
rows to calibration_rows(), so rerun this after any engine change that moves a number.
"""
import datetime
import json
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(VAULT / "scripts"))
import cabvoice as cv  # noqa: E402

NOTE = VAULT / "knowledge/speaker-cab-voicing.md"
TONE = VAULT / "projects/Speaker-cab-system/fixtures/tone-roots.json"
SITE_INTERNAL = (472.0, 421.2, 229.4)
COLUMNS = ("| Speaker | Data | Net L in site box | Closed Qtc | Closed character | Closed F3 Hz | "
           "Proposed ported net L | Fb Hz | Ported character | Notes |")
RULE = "|---|---|---|---|---|---|---|---|---|---|"


def header(date: str) -> str:
    return (f'Calibration table, every number prediction_status "{cv.PREDICTION_STATUS}". '
            f"Generated {date} with `evaluate` (closed, site box 472 x 421.2 x 229.4 mm internal) "
            "and `propose` (closed-ported, low_end balanced), 16 ohm where the note lists it "
            "(voiced with the note's 8 ohm T/S set, see Model limits), amp 40 W.")


def _f(x, nd=2):
    return "" if x is None else f"{x:.{nd}f}"


def calibration_rows() -> list:
    tone = json.loads(TONE.read_text())
    tone["low_end"] = "balanced"
    rows = []
    for slug in cv.list_speakers():
        d = cv.load_speaker(slug)
        z = 16 if 16 in d.impedance_ohm else d.impedance_ohm[0]
        ev = cv.evaluate([d], [z], "closed", tone, SITE_INTERNAL, name=slug)
        pr = cv.propose([d], [z], "closed-ported", tone, name=slug)
        p, q = ev.prediction, pr.prediction
        notes = "; ".join(pr.blockers + [w for w in pr.warnings if "clamped" in w or "boomy" in w])
        rows.append(f"| [[{slug}]] | {d.data_status} | {ev.volumes['net_total_l']:.1f} | "
                    f"{_f(p.get('qtc'), 3)} | {p['character']} | {_f(p.get('f3_hz'), 0)} | "
                    f"{pr.volumes['per_driver_net_l']:.1f} | {_f(q.get('fb_hz'), 0)} | "
                    f"{q['character']} | {notes} |")
    return rows


def note_rows(text: str) -> list:
    section = text.split("## Calibration table", 1)[1].split("\n## ", 1)[0]
    return [line for line in section.splitlines() if line.startswith("| [[")]


def main() -> int:
    text = NOTE.read_text()
    before, rest = text.split("## Calibration table\n", 1)
    after = rest.split("\n## ", 1)[1]
    table = "\n".join([COLUMNS, RULE] + calibration_rows())
    section = f"## Calibration table\n\n{header(datetime.date.today().isoformat())}\n\n{table}\n\n## "
    NOTE.write_text(before + section + after)
    print(f"wrote {len(calibration_rows())} rows to {NOTE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
