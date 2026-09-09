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
    "displacement_l",
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


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

def _third_octave(f_lo: float, f_hi: float) -> list[float]:
    freqs = []
    f = f_lo
    while f < f_hi * 0.999:
        freqs.append(round(f, 2))
        f *= 2 ** (1 / 3)
    freqs.append(float(f_hi))
    return freqs


RESPONSE_FREQS = _third_octave(20.0, 400.0)


def f3_from_response(response: list[tuple[float, float]]) -> float | None:
    """Lowest frequency where the response crosses -3 dB, by linear
    interpolation between table points. None if never reached."""
    prev_f, prev_db = None, None
    for f, db in response:
        if prev_f is not None and prev_db < -3.0 <= db:
            frac = (-3.0 - prev_db) / (db - prev_db)
            return prev_f + frac * (f - prev_f)
        prev_f, prev_db = f, db
    if response and response[0][1] >= -3.0:
        return response[0][0]
    return None


def _require_ts(driver: Driver) -> None:
    if not driver.has_ts():
        raise ValueError(
            f"{driver.slug}: Thiele-Small data missing (data_status={driver.data_status}); "
            "use the rule-of-thumb path")


# ---------------------------------------------------------------------------
# Closed box
# ---------------------------------------------------------------------------

def closed_response_db(fc_hz: float, qtc: float, f_hz: float) -> float:
    """Second-order high-pass magnitude in dB at f for a box with Fc, Qtc."""
    x = f_hz / fc_hz
    s = complex(0.0, x)
    h = s * s / (s * s + s / qtc + 1.0)
    return 20.0 * math.log10(abs(h))


def closed_character(qtc: float) -> str:
    if qtc < 0.6:
        return "lean"
    if qtc < 0.8:
        return "tight"
    if qtc < 1.0:
        return "balanced"
    if qtc < 1.2:
        return "big"
    return "peaky"


@dataclass
class ClosedResult:
    vb_l: float
    alpha: float
    qtc: float
    fc_hz: float
    f3_hz: float | None
    response: list
    character: str


def closed_box(driver: Driver, vb_l: float) -> ClosedResult:
    _require_ts(driver)
    if vb_l <= 0:
        raise ValueError("vb_l must be positive")
    alpha = driver.vas_l / vb_l
    qtc = driver.qts * math.sqrt(1.0 + alpha)
    fc = driver.fs_hz * math.sqrt(1.0 + alpha)
    response = [(f, closed_response_db(fc, qtc, f)) for f in RESPONSE_FREQS]
    return ClosedResult(vb_l=vb_l, alpha=alpha, qtc=qtc, fc_hz=fc,
                        f3_hz=f3_from_response(response), response=response,
                        character=closed_character(qtc))


def closed_box_for_qtc(driver: Driver, qtc: float) -> float:
    """Net volume in liters that gives the target Qtc."""
    _require_ts(driver)
    if qtc <= driver.qts:
        raise ValueError(f"target Qtc {qtc} must exceed the driver's Qts {driver.qts}")
    return driver.vas_l / ((qtc / driver.qts) ** 2 - 1.0)


# ---------------------------------------------------------------------------
# Ported box (Small 1973 vented-box fourth-order model)
# ---------------------------------------------------------------------------

def vented_coeffs(qts: float, alpha: float, h: float, ql: float = QL) -> tuple:
    """Polynomial coefficients a1, a2, a3 of Small's vented-box response.
    alpha = Vas / Vb, h = Fb / Fs, ql = box loss Q."""
    root_h = math.sqrt(h)
    a1 = (ql + h * qts) / (root_h * ql * qts)
    a2 = (h + (alpha + 1.0 + h * h) * ql * qts) / (h * ql * qts)
    a3 = (h * ql + qts) / (root_h * ql * qts)
    return a1, a2, a3


def vented_response_db(f0_hz: float, coeffs: tuple, f_hz: float) -> float:
    """|G| in dB at f for the fourth-order high-pass with f0 = sqrt(Fs Fb)."""
    a1, a2, a3 = coeffs
    s = complex(0.0, f_hz / f0_hz)
    s2, s3, s4 = s * s, s ** 3, s ** 4
    g = s4 / (s4 + a1 * s3 + a2 * s2 + a3 * s + 1.0)
    return 20.0 * math.log10(abs(g))


def ported_character(peak_db: float) -> str:
    if peak_db < 1.0:
        return "flat"
    if peak_db < 3.0:
        return "punchy"
    return "boomy"


@dataclass
class PortedResult:
    vb_l: float
    fb_hz: float
    alpha: float
    h: float
    f3_hz: float | None
    peak_db: float
    response: list
    character: str


def ported_box(driver: Driver, vb_l: float, fb_hz: float) -> PortedResult:
    _require_ts(driver)
    if vb_l <= 0 or fb_hz <= 0:
        raise ValueError("vb_l and fb_hz must be positive")
    alpha = driver.vas_l / vb_l
    h = fb_hz / driver.fs_hz
    coeffs = vented_coeffs(driver.qts, alpha, h)
    f0 = math.sqrt(driver.fs_hz * fb_hz)
    response = [(f, vented_response_db(f0, coeffs, f)) for f in RESPONSE_FREQS]
    peak = max(db for _, db in response)
    return PortedResult(vb_l=vb_l, fb_hz=fb_hz, alpha=alpha, h=h,
                        f3_hz=f3_from_response(response), peak_db=peak,
                        response=response, character=ported_character(peak))


# ---------------------------------------------------------------------------
# Ports (Helmholtz resonator, one flanged end)
# ---------------------------------------------------------------------------

MIN_PORT_LENGTH_MM = 20.0
MAX_PORT_DIAMETER_MM = 150.0


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


def effective_diameter_m(area_m2: float) -> float:
    return math.sqrt(4.0 * area_m2 / math.pi)


def port_length_m(vb_m3: float, fb_hz: float, area_m2: float) -> float:
    """Physical port length for tuning fb in a box of vb. May be negative
    when the port area is too large for the tuning; callers clamp."""
    d_eff = effective_diameter_m(area_m2)
    return (C_SOUND ** 2 * area_m2) / (4.0 * math.pi ** 2 * fb_hz ** 2 * vb_m3) \
        - PORT_END_CORRECTION * d_eff


def port_tuning_hz(vb_m3: float, area_m2: float, length_m: float) -> float:
    """Tuning frequency of an existing port (evaluate mode)."""
    l_eff = length_m + PORT_END_CORRECTION * effective_diameter_m(area_m2)
    return (C_SOUND / (2.0 * math.pi)) * math.sqrt(area_m2 / (vb_m3 * l_eff))


def _port_area_m2(diameter_mm, slot_mm):
    if (diameter_mm is None) == (slot_mm is None):
        raise ValueError("give exactly one of diameter_mm or slot_mm=(w, h)")
    if diameter_mm is not None:
        return math.pi * (diameter_mm / 2e3) ** 2
    w, h = slot_mm
    return (w / 1e3) * (h / 1e3)


def port_dims(vb_l: float, fb_hz: float, diameter_mm: float | None = None,
              slot_mm: tuple | None = None) -> Port:
    area = _port_area_m2(diameter_mm, slot_mm)
    length_m = port_length_m(vb_l / 1e3, fb_hz, area)
    warnings = []
    if length_m * 1e3 < MIN_PORT_LENGTH_MM:
        warnings.append(
            f"port too short ({length_m * 1e3:.1f} mm) for Fb {fb_hz:.0f} Hz in {vb_l:.1f} L; "
            f"clamped to {MIN_PORT_LENGTH_MM:.0f} mm, reduce port area or lower Fb")
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


def port_air_speed(driver: Driver, fb_hz: float, area_cm2: float) -> float:
    """Worst-case port air speed in m/s: full Xmax excursion at Fb.
    Needs only Sd and Xmax, so it also runs for drivers without full T/S."""
    if driver.sd_cm2 is None or driver.xmax_mm is None:
        raise ValueError(f"{driver.slug}: sd_cm2 and xmax_mm are needed for the air-speed check")
    volume_velocity = driver.sd_m2 * driver.xmax_m * 2.0 * math.pi * fb_hz
    return volume_velocity / (area_cm2 / 1e4)


def size_port(driver: Driver, vb_l: float, fb_hz: float,
              diameter_mm: float = 75.0, slot_mm: tuple | None = None) -> Port:
    """Port for (vb, fb), enlarged in 10 percent area steps until the
    worst-case air speed is under PORT_V_MAX and the physical length is at
    least MIN_PORT_LENGTH_MM. Stops at the MAX_PORT_DIAMETER_MM equivalent
    area and leaves the warnings in place for the caller."""
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
    if port.air_speed_ms > PORT_V_MAX:
        port.warnings.append(f"port air speed {port.air_speed_ms:.1f} m/s still above "
                             f"{PORT_V_MAX} m/s at the maximum port size")
    return port


# ---------------------------------------------------------------------------
# Open back (empirical path-length estimate, not a T/S model)
# ---------------------------------------------------------------------------

OPEN_FRACTION = {"open": 0.40, "semi-open": 0.25}


def open_back_relative_db(f_cancel_hz: float, f_hz: float) -> float:
    """dB relative to the closed box: 0 above f_cancel, -6 dB/octave below."""
    if f_hz >= f_cancel_hz:
        return 0.0
    return 20.0 * math.log10(f_hz / f_cancel_hz)


@dataclass
class OpenBackResult:
    open_fraction: float
    path_m: float
    f_cancel_hz: float
    panel_height_mm: float
    response: list
    character: str


def open_back(internal_w_mm: float, internal_h_mm: float, internal_d_mm: float,
              open_fraction: float) -> OpenBackResult:
    """The open band spans the full width, so the shortest front-to-back
    path from a centered driver runs out the side: depth + width / 2."""
    if not 0.0 < open_fraction < 1.0:
        raise ValueError("open_fraction must be between 0 and 1")
    if min(internal_w_mm, internal_h_mm, internal_d_mm) <= 0:
        raise ValueError("internal dimensions must be positive")
    path_m = (internal_d_mm + internal_w_mm / 2.0) / 1e3
    f_cancel = C_SOUND / (2.0 * path_m)
    panel_height = (1.0 - open_fraction) * internal_h_mm / 2.0
    response = [(f, open_back_relative_db(f_cancel, f)) for f in RESPONSE_FREQS]
    return OpenBackResult(
        open_fraction=open_fraction, path_m=path_m, f_cancel_hz=f_cancel,
        panel_height_mm=panel_height, response=response,
        character=f"open, wide dispersion, 6 dB per octave below {f_cancel:.0f} Hz relative to closed",
    )
