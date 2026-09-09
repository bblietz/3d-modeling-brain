"""Guitar speaker cabinet voicing engine (see skills/speaker-cab and
projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md).

Pure functions over a Driver record loaded from the YAML frontmatter of
knowledge/speakers/<slug>.md. All internal math is SI. Every prediction is
unverified until listening notes say otherwise.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict, replace
from pathlib import Path

import yaml

VAULT = Path(__file__).resolve().parent.parent
SPEAKERS_DIR = VAULT / "knowledge" / "speakers"

C_SOUND = 343.0            # m/s
QL = 7.0                   # box loss Q for the vented model
PORT_END_CORRECTION = 0.85 # times effective port diameter, one flanged end
PORT_V_MAX = 17.0          # m/s worst-case port air speed limit
DEFAULT_DISPLACEMENT_L = 1.5
PREDICTION_STATUS = "unverified, ears only"

DATA_STATUS_VALUES = ("datasheet", "third-party", "analog", "estimated", "missing")
MAGNET_VALUES = ("alnico", "ceramic", "neodymium")

REQUIRED_FIELDS = (
    "name", "type", "brand", "model", "diameter_in", "impedance_ohm",
    "power_w", "sensitivity_db", "magnet", "fs_hz", "re_ohm",
    "cutout_mm", "bolt_circle_mm", "bolt_count", "depth_mm", "weight_kg",
    "data_status", "sources", "status",
)
# May be null only when data_status is "missing".
TS_FIELDS = ("qts", "qes", "qms", "vas_l", "xmax_mm", "sd_cm2")
# le_mh is optional (unused by the engine, rarely published).
POSITIVE_FIELDS = (
    "diameter_in", "power_w", "sensitivity_db", "fs_hz", "re_ohm",
    "cutout_mm", "bolt_circle_mm", "bolt_count", "depth_mm", "weight_kg", "le_mh",
) + TS_FIELDS


def parse_frontmatter(text: str) -> dict:
    """Return the YAML frontmatter of an Obsidian note as a dict."""
    if not text.startswith("---"):
        raise ValueError("note has no YAML frontmatter block")
    parts = text.split("\n---", 2)
    if len(parts) < 2:
        raise ValueError("frontmatter block is not closed")
    block = parts[0][3:]
    meta = yaml.safe_load(block)
    if not isinstance(meta, dict):
        raise ValueError("frontmatter did not parse to a mapping")
    return meta


def validate_speaker(meta: dict) -> list[str]:
    """Return a list of problems with a speaker note's frontmatter (empty = ok)."""
    errors = []
    for key in REQUIRED_FIELDS:
        if key not in meta or meta[key] is None:
            errors.append(f"missing required field {key}")
    if meta.get("type") != "speaker":
        errors.append("type must be 'speaker'")
    status = meta.get("data_status")
    if status not in DATA_STATUS_VALUES:
        errors.append(f"data_status must be one of {DATA_STATUS_VALUES}, got {status!r}")
    if meta.get("magnet") not in MAGNET_VALUES:
        errors.append(f"magnet must be one of {MAGNET_VALUES}")
    imps = meta.get("impedance_ohm")
    if not isinstance(imps, list) or not imps or not all(isinstance(z, (int, float)) and z > 0 for z in imps):
        errors.append("impedance_ohm must be a non-empty list of positive numbers")
    if not isinstance(meta.get("sources"), list) or not meta.get("sources"):
        errors.append("sources must be a non-empty list of URLs")
    for key in TS_FIELDS:
        if meta.get(key) is None and status != "missing":
            errors.append(f"{key} is required unless data_status is 'missing'")
    for key in POSITIVE_FIELDS:
        val = meta.get(key)
        if val is not None and (not isinstance(val, (int, float)) or val <= 0):
            errors.append(f"{key} must be a positive number, got {val!r}")
    if status == "analog" and not meta.get("analog_of"):
        errors.append("analog_of is required when data_status is 'analog'")
    return errors


@dataclass
class Driver:
    slug: str
    brand: str
    model: str
    diameter_in: float
    impedance_ohm: list
    power_w: float
    sensitivity_db: float
    magnet: str
    fs_hz: float
    re_ohm: float
    qts: float | None
    qes: float | None
    qms: float | None
    vas_l: float | None
    xmax_mm: float | None
    sd_cm2: float | None
    le_mh: float | None
    cutout_mm: float
    bolt_circle_mm: float
    bolt_count: int
    depth_mm: float
    weight_kg: float
    displacement_l: float
    displacement_estimated: bool
    data_status: str
    analog_of: str | None
    sources: list = field(default_factory=list)

    def has_ts(self) -> bool:
        return all(v is not None for v in (self.qts, self.vas_l, self.fs_hz))

    @property
    def sd_m2(self) -> float:
        return self.sd_cm2 / 1e4

    @property
    def vas_m3(self) -> float:
        return self.vas_l / 1e3

    @property
    def xmax_m(self) -> float:
        return self.xmax_mm / 1e3


def driver_from_meta(meta: dict) -> Driver:
    errors = validate_speaker(meta)
    if errors:
        raise ValueError(f"{meta.get('name')}: " + "; ".join(errors))
    disp = meta.get("displacement_l")
    return Driver(
        slug=meta["name"], brand=meta["brand"], model=meta["model"],
        diameter_in=meta["diameter_in"], impedance_ohm=list(meta["impedance_ohm"]),
        power_w=meta["power_w"], sensitivity_db=meta["sensitivity_db"],
        magnet=meta["magnet"], fs_hz=meta["fs_hz"], re_ohm=meta["re_ohm"],
        qts=meta.get("qts"), qes=meta.get("qes"), qms=meta.get("qms"),
        vas_l=meta.get("vas_l"), xmax_mm=meta.get("xmax_mm"),
        sd_cm2=meta.get("sd_cm2"), le_mh=meta.get("le_mh"),
        cutout_mm=meta["cutout_mm"], bolt_circle_mm=meta["bolt_circle_mm"],
        bolt_count=meta["bolt_count"], depth_mm=meta["depth_mm"],
        weight_kg=meta["weight_kg"],
        displacement_l=disp if disp is not None else DEFAULT_DISPLACEMENT_L,
        displacement_estimated=disp is None,
        data_status=meta["data_status"], analog_of=meta.get("analog_of"),
        sources=list(meta["sources"]),
    )


def load_speaker(slug: str, speakers_dir: Path = SPEAKERS_DIR) -> Driver:
    path = Path(speakers_dir) / f"{slug}.md"
    if not path.exists():
        raise FileNotFoundError(f"no speaker note {path}")
    return driver_from_meta(parse_frontmatter(path.read_text()))


def list_speakers(speakers_dir: Path = SPEAKERS_DIR) -> list[str]:
    return sorted(p.stem for p in Path(speakers_dir).glob("*.md"))
