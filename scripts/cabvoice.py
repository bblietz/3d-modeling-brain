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


# ---------------------------------------------------------------------------
# Wiring and power
# ---------------------------------------------------------------------------

JACK_CONFIGS = ("mono", "mono-parallel-out", "stereo")
POWER_SAFETY_FACTOR = 1.5


@dataclass
class WiringOption:
    name: str
    impedance_ohm: float
    matches_tap: bool
    jack_text: str


@dataclass
class WiringResult:
    jack_config: str
    options: list
    recommended: WiringOption | None
    warnings: list


def _matches_tap(z: float, taps: list) -> bool:
    return any(abs(z - t) / t <= 0.01 for t in taps)


def wiring(impedances: list, taps: list, jack_config: str = "mono",
           sensitivities: list | None = None) -> WiringResult:
    if jack_config not in JACK_CONFIGS:
        raise ValueError(f"jack_config must be one of {JACK_CONFIGS}")
    n = len(impedances)
    if n not in (1, 2):
        raise ValueError("wiring supports one or two drivers")
    if jack_config == "stereo" and n != 2:
        raise ValueError("stereo needs two drivers")
    warnings, options = [], []
    if sensitivities and n == 2 and abs(sensitivities[0] - sensitivities[1]) > 2.0:
        warnings.append(
            f"sensitivity mismatch {sensitivities[0]:g} vs {sensitivities[1]:g} dB: "
            "the louder driver will dominate")
    if jack_config == "stereo":
        for i, z in enumerate(impedances, start=1):
            options.append(WiringOption(
                f"stereo side {i}", float(z), _matches_tap(z, taps),
                f"Jack {i}: driver {i} alone, {z:g} ohm"))
        recommended = options[0] if all(o.matches_tap for o in options) else None
    elif n == 1:
        z = float(impedances[0])
        options.append(WiringOption("single", z, _matches_tap(z, taps),
                                    f"Single driver, {z:g} ohm"))
        recommended = options[0] if options[0].matches_tap else None
    else:
        z1, z2 = (float(z) for z in impedances)
        if z1 != z2:
            warnings.append(
                f"unequal impedances {z1:g} and {z2:g} ohm split power unevenly; "
                "use matching drivers")
        par = 1.0 / (1.0 / z1 + 1.0 / z2)
        ser = z1 + z2
        options.append(WiringOption(
            "parallel", par, _matches_tap(par, taps),
            f"Parallel: jack + to both driver +, jack - to both driver -, {par:g} ohm"))
        options.append(WiringOption(
            "series", ser, _matches_tap(ser, taps),
            "Series: jack + to driver 1 +, driver 1 - to driver 2 +, "
            f"driver 2 - to jack -, {ser:g} ohm"))
        recommended = next((o for o in options if o.matches_tap), None)
    if jack_config == "mono-parallel-out":
        warnings.append(
            "Parallel out: an external cabinet halves the combined load; set the amp tap "
            "to the combined impedance, not this cabinet's alone.")
    if recommended is None:
        warnings.append(f"no wiring option matches amp taps {list(taps)}")
    return WiringResult(jack_config, options, recommended, warnings)


@dataclass
class PowerCheck:
    total_handling_w: float
    amp_power_w: float
    min_power_w: float
    status: str
    message: str


def power_check(handling_w: list, amp_power_w: float, breakup: str = "moderate",
                accept_low_headroom: bool = False) -> PowerCheck:
    """Hard stop below the amp's rated power, warning below 1.5 times it.
    An early-breakup target may accept the warning explicitly."""
    if amp_power_w <= 0:
        raise ValueError("amp_power_w must be positive")
    total = float(sum(handling_w))
    minimum = POWER_SAFETY_FACTOR * amp_power_w
    if total < amp_power_w:
        return PowerCheck(total, amp_power_w, minimum, "stop",
                          f"speaker handling {total:g} W is below the amp's {amp_power_w:g} W")
    if total < minimum:
        if breakup == "early" and accept_low_headroom:
            return PowerCheck(total, amp_power_w, minimum, "ok",
                              f"handling {total:g} W is under the {minimum:g} W target; "
                              "accepted for early breakup")
        return PowerCheck(total, amp_power_w, minimum, "warning",
                          f"handling {total:g} W is under the {minimum:g} W target "
                          f"({POWER_SAFETY_FACTOR} x amp power)")
    return PowerCheck(total, amp_power_w, minimum, "ok",
                      f"handling {total:g} W clears the {minimum:g} W target")


# ---------------------------------------------------------------------------
# Box geometry (mm, tuples are width, height, depth)
# ---------------------------------------------------------------------------

MM_PER_INCH = 25.4
PANEL_MM = 18.0
BACK_MM = 12.0
BAFFLE_MM = 18.0
RECESS_MM = 20.0
CUTOUT_MARGIN_MM = 25.0
BASE_EXTERNAL_IN = (20.0, 18.0, 11.0)


@dataclass
class Box:
    external_mm: tuple
    internal_mm: tuple
    gross_l: float
    warnings: list = field(default_factory=list)


def internal_from_external(external_mm, panel_mm=PANEL_MM, back_mm=BACK_MM,
                           baffle_mm=BAFFLE_MM, recess_mm=RECESS_MM) -> tuple:
    w, h, d = external_mm
    return (w - 2 * panel_mm, h - 2 * panel_mm, d - recess_mm - baffle_mm - back_mm)


def external_from_internal(internal_mm, panel_mm=PANEL_MM, back_mm=BACK_MM,
                           baffle_mm=BAFFLE_MM, recess_mm=RECESS_MM) -> tuple:
    w, h, d = internal_mm
    return (w + 2 * panel_mm, h + 2 * panel_mm, d + recess_mm + baffle_mm + back_mm)


def gross_volume_l(internal_mm) -> float:
    w, h, d = internal_mm
    return w * h * d / 1e6


def dimension_ratio_warnings(internal_mm) -> list:
    """Advisory: flag internal dimensions within 5 percent of 1:1, 2:1, or 3:1."""
    names = ("width", "height", "depth")
    out = []
    for i in range(3):
        for j in range(i + 1, 3):
            a, b = internal_mm[i], internal_mm[j]
            big, small = max(a, b), min(a, b)
            r = big / small
            for n in (1, 2, 3):
                if abs(r - n) / n < 0.05:
                    out.append(f"{names[i]} and {names[j]} are within 5 percent of {n}:1 "
                               f"({r:.2f}); coincident standing waves")
    return out


def make_box(internal_mm, **panel_kwargs) -> Box:
    return Box(external_mm=external_from_internal(internal_mm, **panel_kwargs),
               internal_mm=tuple(internal_mm), gross_l=gross_volume_l(internal_mm),
               warnings=dimension_ratio_warnings(internal_mm))


def site_default_box(**panel_kwargs) -> Box:
    external = tuple(x * MM_PER_INCH for x in BASE_EXTERNAL_IN)
    return make_box(internal_from_external(external, **panel_kwargs), **panel_kwargs)


def min_internal_width_mm(driver_count: int, cutout_mm: float) -> float:
    return driver_count * cutout_mm + (driver_count + 1) * CUTOUT_MARGIN_MM


def dims_for_volume(gross_l: float, pinned_external_width_mm: float | None = None,
                    min_internal_width_mm: float | None = None,
                    max_external_mm: tuple | None = None, **panel_kwargs) -> Box:
    """Internal dimensions for a gross volume, starting from the site box
    proportions. Fixed axes come from a pinned width, the two-driver minimum
    width, or external limits; free axes scale together to hit the volume."""
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
                f"width {dims[0]:.0f} mm internal (pinned or the driver-count minimum) "
                f"exceeds the size limit {max_internal[0]:.0f} mm")

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

    rescale()
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
        raise ValueError(
            f"cannot reach {gross_l:.1f} L within the limits; "
            f"achievable {achieved / 1e6:.1f} L")
    box = make_box(tuple(dims), **panel_kwargs)
    box.warnings = conflicts + box.warnings
    return box


# ---------------------------------------------------------------------------
# Tone target, volume targets, propose
# ---------------------------------------------------------------------------

ENCLOSURE_TYPES = ("closed", "closed-ported", "open", "semi-open")
TONE_VALUES = {
    "low_end": ("tight", "balanced", "big"),
    "mids": ("scooped", "neutral", "forward"),
    "top": ("chimey", "smooth", "dark"),
    "breakup": ("early", "moderate", "clean"),
    "dispersion": ("focused", "wide"),
    "placement": ("floor", "raised", "tilted"),
}
# Box size relative to Vas by low-end target (Vb = Vas / alpha), clamped to
# the practical per-driver range. Starting values, see speaker-cab-voicing.
ALPHA_TARGET = {"tight": 1.5, "balanced": 1.0, "big": 0.65}
NET_L_RANGE = (30.0, 68.0)
# Per 12 inch driver, net liters, when no T/S data or for open backs. The
# site's default box (about 44 L net) is "balanced".
RULE_OF_THUMB_NET_L = {"tight": 34.0, "balanced": 44.0, "big": 56.0}
FB_FACTOR = {"tight": 0.9, "balanced": 0.8, "big": 0.7}
FB_MIN_HZ, FB_MAX_HZ = 45.0, 90.0
FALLBACK_SD_CM2, FALLBACK_XMAX_MM = 530.0, 0.8


def validate_tone_target(tone: dict) -> list:
    errors = []
    for key, allowed in TONE_VALUES.items():
        if tone.get(key) not in allowed:
            errors.append(f"{key} must be one of {allowed}, got {tone.get(key)!r}")
    mp = tone.get("min_power_w")
    if not isinstance(mp, (int, float)) or mp <= 0:
        errors.append("min_power_w must be a positive number (1.5 x amp power)")
    taps = tone.get("impedance_options_ohm")
    if (not isinstance(taps, list) or not taps
            or not all(isinstance(t, (int, float)) and t > 0 for t in taps)):
        errors.append("impedance_options_ohm must be a non-empty list of positive numbers")
    return errors


@dataclass
class Constraints:
    pinned_external_width_mm: float | None = None
    max_external_mm: tuple | None = None
    panel_mm: float = PANEL_MM
    back_mm: float = BACK_MM
    baffle_mm: float = BAFFLE_MM
    recess_mm: float = RECESS_MM
    brace_l: float = 0.0
    port_diameter_mm: float = 75.0
    port_slot_mm: tuple | None = None
    accept_low_headroom: bool = False

    def panel_kwargs(self) -> dict:
        return dict(panel_mm=self.panel_mm, back_mm=self.back_mm,
                    baffle_mm=self.baffle_mm, recess_mm=self.recess_mm)


def per_driver_net_l(driver: Driver, enclosure: str, low_end: str) -> tuple:
    """(net liters per driver, method, warnings)."""
    warnings = []
    lo, hi = NET_L_RANGE
    if enclosure in ("open", "semi-open"):
        return RULE_OF_THUMB_NET_L[low_end], "rule-of-thumb", warnings
    if not driver.has_ts():
        warnings.append(f"{driver.slug}: no Thiele-Small data ({driver.data_status}); "
                        "rule-of-thumb volume, no response prediction")
        return RULE_OF_THUMB_NET_L[low_end], "rule-of-thumb", warnings
    vb = driver.vas_l / ALPHA_TARGET[low_end]
    if vb < lo or vb > hi:
        clamped = min(max(vb, lo), hi)
        warnings.append(f"{driver.slug}: Thiele-Small volume {vb:.1f} L for '{low_end}' "
                        f"clamped to the practical range {lo:.0f} to {hi:.0f} L ({clamped:.1f} L)")
        vb = clamped
    return vb, "thiele-small", warnings


def ported_targets(driver: Driver, net_l: float, low_end: str) -> tuple:
    """Tuning for a ported box: Fb at a fraction of Fs, then grow the box or
    lower Fb until the alignment is not boomy (unless 'big' was asked)."""
    fb = min(max(driver.fs_hz * FB_FACTOR[low_end], FB_MIN_HZ), FB_MAX_HZ)
    if not driver.has_ts():
        return net_l, fb, None, []
    vb, warnings = net_l, []
    res = ported_box(driver, vb, fb)
    while res.character == "boomy" and low_end != "big":
        if vb * 1.1 <= NET_L_RANGE[1]:
            vb *= 1.1
        elif fb - 5.0 >= FB_MIN_HZ:
            fb -= 5.0
        else:
            warnings.append("ported alignment stays boomy at the practical limits; "
                            "consider a closed back or a lower-Qts driver")
            break
        res = ported_box(driver, vb, fb)
    return vb, fb, res, warnings


def _air_speed_driver(driver: Driver, count_in_chamber: int, warnings: list) -> Driver:
    sd, xmax = driver.sd_cm2, driver.xmax_mm
    if sd is None or xmax is None:
        warnings.append(f"{driver.slug}: port air speed uses assumed Sd {FALLBACK_SD_CM2:g} cm2 "
                        f"and Xmax {FALLBACK_XMAX_MM:g} mm")
        sd = sd if sd is not None else FALLBACK_SD_CM2
        xmax = xmax if xmax is not None else FALLBACK_XMAX_MM
    return replace(driver, sd_cm2=sd * count_in_chamber, xmax_mm=xmax)


def _speaker_summary(driver: Driver, impedance) -> dict:
    return {"slug": driver.slug, "brand": driver.brand, "model": driver.model,
            "impedance_ohm": impedance, "power_w": driver.power_w,
            "sensitivity_db": driver.sensitivity_db, "data_status": driver.data_status,
            "analog_of": driver.analog_of, "cutout_mm": driver.cutout_mm,
            "bolt_circle_mm": driver.bolt_circle_mm, "bolt_count": driver.bolt_count,
            "depth_mm": driver.depth_mm, "weight_kg": driver.weight_kg,
            "displacement_l": driver.displacement_l}


def _mm_to_in(dims) -> tuple:
    return tuple(round(x / MM_PER_INCH, 2) for x in dims)


def _dedupe(items: list) -> list:
    return list(dict.fromkeys(items))


@dataclass
class Voicing:
    name: str
    mode: str
    tone_target: dict
    speakers: list
    enclosure: dict
    volumes: dict
    box: dict
    port: dict | None
    prediction: dict
    wiring: dict
    power: dict
    construction: dict
    warnings: list
    blockers: list
    prediction_status: str = PREDICTION_STATUS

    def to_dict(self) -> dict:
        return asdict(self)


def _check_inputs(drivers, impedances, enclosure, tone, jack_config):
    errors = validate_tone_target(tone)
    if errors:
        raise ValueError("tone target: " + "; ".join(errors))
    if enclosure not in ENCLOSURE_TYPES:
        raise ValueError(f"enclosure must be one of {ENCLOSURE_TYPES}")
    if jack_config not in JACK_CONFIGS:
        raise ValueError(f"jack_config must be one of {JACK_CONFIGS}")
    if len(drivers) not in (1, 2) or len(impedances) != len(drivers):
        raise ValueError("one or two drivers, with one impedance each")
    if jack_config == "stereo" and len(drivers) != 2:
        raise ValueError("stereo needs two drivers")


def _electrical(drivers, impedances, tone, jack_config, c, warnings, blockers):
    wr = wiring(impedances, tone["impedance_options_ohm"], jack_config,
                [d.sensitivity_db for d in drivers])
    warnings.extend(wr.warnings)
    if wr.recommended is None:
        blockers.append("no wiring option matches the amp's impedance taps")
    amp_power = tone["min_power_w"] / POWER_SAFETY_FACTOR
    if jack_config == "stereo":
        checks = [power_check([d.power_w], amp_power, tone["breakup"], c.accept_low_headroom)
                  for d in drivers]
    else:
        checks = [power_check([d.power_w for d in drivers], amp_power, tone["breakup"],
                              c.accept_low_headroom)]
    order = ("ok", "warning", "stop")
    worst = max(checks, key=lambda p: order.index(p.status))
    if worst.status == "stop":
        blockers.append(worst.message)
    elif worst.status == "warning":
        warnings.append(worst.message)
    wiring_dict = {"jack_config": jack_config,
                   "recommended": None if wr.recommended is None else asdict(wr.recommended),
                   "options": [asdict(o) for o in wr.options]}
    power_dict = {"amp_power_w": amp_power, **asdict(worst),
                  "per_side": [asdict(p) for p in checks]}
    return wiring_dict, power_dict


# Shared by propose and evaluate.

def _setup(drivers, impedances, enclosure, tone, jack_config) -> tuple:
    """Validated inputs: (lead, count, chambers, per_chamber_drivers, warnings)."""
    _check_inputs(drivers, impedances, enclosure, tone, jack_config)
    warnings = []
    lead = drivers[0]
    count = len(drivers)
    if count == 2 and drivers[1].slug != lead.slug:
        warnings.append("mixed drivers: the alignment uses the first driver's parameters")
    chambers = 2 if jack_config == "stereo" else 1
    return lead, count, chambers, count // chambers, warnings


def _displacement(drivers, warnings) -> float:
    if any(d.displacement_estimated for d in drivers):
        warnings.append(f"driver displacement assumed {DEFAULT_DISPLACEMENT_L} L per driver")
    return sum(d.displacement_l for d in drivers)


def _divider_l(chambers, h_int, d_int, c) -> float:
    return (c.panel_mm * h_int * d_int / 1e6) if chambers == 2 else 0.0


def _chamber_w(chambers, w_int, c) -> float:
    return (w_int - c.panel_mm) / 2.0 if chambers == 2 else w_int


def _port_report(lead, per_chamber_drivers, chamber_net, port, warnings) -> tuple:
    """The port as built in its chamber: (actual tuning Hz, port dict)."""
    warnings.extend(port.warnings)
    area_m2 = port.area_cm2 / 1e4
    fb = port_tuning_hz(chamber_net / 1e3, area_m2, port.length_mm / 1e3)
    speed_driver = _air_speed_driver(lead, per_chamber_drivers, warnings)
    port.air_speed_ms = port_air_speed(speed_driver, fb, port.area_cm2)
    if port.air_speed_ms > PORT_V_MAX and not any("still above" in w for w in port.warnings):
        warnings.append(f"port air speed {port.air_speed_ms:.1f} m/s above {PORT_V_MAX} m/s")
    port.volume_l = area_m2 * port.length_mm   # m2 x mm is liters
    port_dict = {**asdict(port), "location": "front" if port.shape == "slot" else "rear",
                 "per_chamber": True}
    return fb, port_dict


NO_TS_CHARACTER = "unpredicted (no Thiele-Small data)"


def _predict(lead, enclosure, per_driver_net, fb, chamber_w, h_int, d_int) -> dict:
    if enclosure in ("open", "semi-open"):
        ob = open_back(chamber_w, h_int, d_int, OPEN_FRACTION[enclosure])
        return {"model": "open-back path estimate", "f_cancel_hz": ob.f_cancel_hz,
                "path_m": ob.path_m, "panel_height_mm": ob.panel_height_mm,
                "character": ob.character, "response_relative_db": ob.response}
    if enclosure == "closed-ported":
        if not lead.has_ts():
            return {"model": "rule-of-thumb", "fb_hz": fb, "character": NO_TS_CHARACTER}
        pb = ported_box(lead, per_driver_net, fb)
        return {"model": "thiele-small vented", "fb_hz": fb, "alpha": pb.alpha, "h": pb.h,
                "f3_hz": pb.f3_hz, "peak_db": pb.peak_db, "character": pb.character,
                "response_db": pb.response}
    if not lead.has_ts():
        return {"model": "rule-of-thumb", "character": NO_TS_CHARACTER}
    cb = closed_box(lead, per_driver_net)
    return {"model": "thiele-small closed", "qtc": cb.qtc, "fc_hz": cb.fc_hz, "f3_hz": cb.f3_hz,
            "character": cb.character, "response_db": cb.response}


def _volumes(method, per_driver_net, per_chamber_drivers, chambers, displacement, brace_l,
             port_l_total, divider_l, gross_l) -> dict:
    chamber_net = per_driver_net * per_chamber_drivers
    return {"method": method, "per_driver_net_l": per_driver_net,
            "per_chamber_net_l": chamber_net, "net_total_l": chamber_net * chambers,
            "displacement_l": displacement, "brace_l": brace_l, "port_l": port_l_total,
            "divider_l": divider_l, "gross_l": gross_l}


def _assemble(name, mode, tone, drivers, impedances, enclosure, jack_config, chambers, count,
              volumes, box, chamber_w, port_dict, prediction, wiring_dict, power_dict,
              warnings, blockers, c) -> Voicing:
    return Voicing(
        name=name, mode=mode, tone_target=dict(tone),
        speakers=[_speaker_summary(d, z) for d, z in zip(drivers, impedances)],
        enclosure={"type": enclosure, "driver_count": count, "chambers": chambers,
                   "jack_config": jack_config, "open_fraction": OPEN_FRACTION.get(enclosure)},
        volumes=volumes,
        box={"internal_mm": box.internal_mm, "external_mm": box.external_mm,
             "internal_in": _mm_to_in(box.internal_mm), "external_in": _mm_to_in(box.external_mm),
             "chamber_internal_width_mm": chamber_w},
        port=port_dict, prediction=prediction, wiring=wiring_dict, power=power_dict,
        construction={"panel_mm": c.panel_mm, "back_mm": c.back_mm, "baffle_mm": c.baffle_mm,
                      "recess_mm": c.recess_mm, "brace_l": c.brace_l,
                      "pinned_external_width_mm": c.pinned_external_width_mm,
                      "max_external_mm": c.max_external_mm,
                      "port_count": None if port_dict is None else port_dict.get("count", 1)},
        warnings=_dedupe(warnings), blockers=_dedupe(blockers),
    )


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
    min_w = (chambers * min_internal_width_mm(per_chamber_drivers, max(d.cutout_mm for d in drivers))
             + (chambers - 1) * c.panel_mm)
    pk = c.panel_kwargs()
    port, port_l, divider_l, box = None, 0.0, 0.0, None
    for _ in range(2):
        gross = net_total + displacement + c.brace_l + port_l * chambers + divider_l
        box = dims_for_volume(gross, c.pinned_external_width_mm, min_w, c.max_external_mm, **pk)
        w_int, h_int, d_int = box.internal_mm
        divider_l = _divider_l(chambers, h_int, d_int, c)
        if enclosure == "closed-ported":
            port = size_port(_air_speed_driver(lead, per_chamber_drivers, warnings),
                             chamber_net, fb, diameter_mm=c.port_diameter_mm,
                             slot_mm=c.port_slot_mm)
            port_l = port.volume_l
    warnings.extend(box.warnings)
    chamber_w = _chamber_w(chambers, w_int, c)
    port_dict = None
    if port is not None:
        fb_actual, port_dict = _port_report(lead, per_chamber_drivers, chamber_net, port, warnings)
        if abs(fb_actual - fb) > 0.5:
            warnings.append(f"port clamped at the size cap: tuned {fb_actual:.1f} Hz, target "
                            f"{fb:.1f} Hz; lower Fb or use a smaller box")
        fb = fb_actual   # the prediction follows the port as built
    prediction = _predict(lead, enclosure, per_driver_net, fb, chamber_w, h_int, d_int)
    wiring_dict, power_dict = _electrical(drivers, impedances, tone, jack_config, c,
                                          warnings, blockers)
    volumes = _volumes(method, per_driver_net, per_chamber_drivers, chambers, displacement,
                       c.brace_l, port_l * chambers, divider_l, box.gross_l)
    return _assemble(name, "propose", tone, drivers, impedances, enclosure, jack_config, chambers,
                     count, volumes, box, chamber_w, port_dict, prediction, wiring_dict,
                     power_dict, warnings, blockers, c)


# ---------------------------------------------------------------------------
# Evaluate an existing box
# ---------------------------------------------------------------------------

def evaluate(drivers: list, impedances: list, enclosure: str, tone: dict,
             internal_mm: tuple, jack_config: str = "mono", port: Port | None = None,
             constraints: Constraints | None = None, name: str = "cab") -> Voicing:
    c = constraints or Constraints()
    lead, count, chambers, per_chamber_drivers, warnings = _setup(
        drivers, impedances, enclosure, tone, jack_config)
    if enclosure == "closed-ported" and port is None:
        raise ValueError("closed-ported evaluate needs a port (from port_dims) with its length")
    blockers = []
    box = make_box(tuple(internal_mm), **c.panel_kwargs())
    warnings.extend(box.warnings)
    w_int, h_int, d_int = box.internal_mm
    divider_l = _divider_l(chambers, h_int, d_int, c)
    displacement = _displacement(drivers, warnings)
    port_l = 0.0
    if port is not None:
        port_l = port.area_cm2 / 1e4 * port.length_mm
    net_total = box.gross_l - displacement - c.brace_l - port_l * chambers - divider_l
    if net_total <= 0:
        raise ValueError("box has no net volume left after displacement, brace, port, and divider")
    chamber_net = net_total / chambers
    per_driver_net = chamber_net / per_chamber_drivers
    chamber_w = _chamber_w(chambers, w_int, c)
    fb, port_dict = None, None
    if enclosure == "closed-ported":
        fb, port_dict = _port_report(lead, per_chamber_drivers, chamber_net, port, warnings)
    if not lead.has_ts() and enclosure in ("closed", "closed-ported"):
        detail = "tuning reported, " if enclosure == "closed-ported" else ""
        warnings.append(f"{lead.slug}: no Thiele-Small data ({lead.data_status}); "
                        f"{detail}no response prediction")
    prediction = _predict(lead, enclosure, per_driver_net, fb, chamber_w, h_int, d_int)
    wiring_dict, power_dict = _electrical(drivers, impedances, tone, jack_config, c,
                                          warnings, blockers)
    volumes = _volumes("evaluate", per_driver_net, per_chamber_drivers, chambers, displacement,
                       c.brace_l, port_l * chambers, divider_l, box.gross_l)
    return _assemble(name, "evaluate", tone, drivers, impedances, enclosure, jack_config, chambers,
                     count, volumes, box, chamber_w, port_dict, prediction, wiring_dict,
                     power_dict, warnings, blockers, c)


# ---------------------------------------------------------------------------
# Output: voicing.json and voicing.md
# ---------------------------------------------------------------------------

def _fmt_dims(mm, inches) -> str:
    return (f"{mm[0]:.0f} x {mm[1]:.0f} x {mm[2]:.0f} mm "
            f"({inches[0]:.2f} x {inches[1]:.2f} x {inches[2]:.2f} in, W x H x D)")


def _liters(l: float) -> str:
    return f"{l:.1f} L ({l / 28.3168:.2f} cu ft)"


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
    spk = ", ".join(f"{s['brand']} {s['model']} {s['impedance_ohm']} ohm ({s['data_status']})"
                    for s in v.speakers)
    e = v.enclosure
    lines += [
        f"- Drivers: {e['driver_count']} x {spk}",
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
        f"| Port | {vol['port_l']:.2f} L |",
        f"| Divider | {vol['divider_l']:.2f} L |",
        f"| Gross internal | {_liters(vol['gross_l'])} |",
        "",
        "## Dimensions",
        "",
        f"- Internal: {_fmt_dims(v.box['internal_mm'], v.box['internal_in'])}",
        f"- External: {_fmt_dims(v.box['external_mm'], v.box['external_in'])}",
        f"- Chamber internal width: {v.box['chamber_internal_width_mm']:.0f} mm",
        "",
        "## Port",
        "",
    ]
    if v.port is None:
        lines.append("No port (closed or open back).")
    else:
        p = v.port
        size = (f"round {p['diameter_mm']:.0f} mm" if p['shape'] == "round"
                else f"slot {p['slot_w_mm']:.0f} x {p['slot_h_mm']:.0f} mm")
        lines += [
            f"- {size}, area {p['area_cm2']:.0f} cm2, length {p['length_mm']:.0f} mm, "
            f"{p['location']}, one per chamber",
            f"- Worst-case air speed {p['air_speed_ms']:.1f} m/s (limit {PORT_V_MAX:.0f} m/s)",
        ]
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
    lines.append("- Recommended: " + (f"{rec['name']}, {rec['impedance_ohm']:g} ohm. {rec['jack_text']}"
                                       if rec else "none matches the amp taps"))
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


def write_voicing(v: Voicing, out_dir: Path) -> tuple:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "voicing.json"
    md_path = out_dir / "voicing.md"
    json_path.write_text(json.dumps(v.to_dict(), indent=2))
    md_path.write_text(render_markdown(v))
    return json_path, md_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
        p.add_argument("--accept-low-headroom", action="store_true")
        p.add_argument("--name", default="cab")
        p.add_argument("--out", required=True, help="directory for voicing.json and voicing.md")

    pp = sub.add_parser("propose")
    common(pp)
    pp.add_argument("--pinned-width", type=float, help="external width mm")
    pp.add_argument("--max-external", type=float, nargs=3, metavar=("W", "H", "D"))
    pp.add_argument("--port-diameter", type=float, default=75.0)
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


def main(argv=None) -> int:
    import sys
    args = _build_parser().parse_args(argv)
    if args.command == "list":
        print("\n".join(list_speakers(Path(args.speakers_dir))))
        return 0
    try:
        drivers = [load_speaker(s, Path(args.speakers_dir)) for s in args.speaker]
        tone = json.loads(Path(args.tone).read_text())
        c = Constraints(brace_l=args.brace_l, accept_low_headroom=args.accept_low_headroom)
        if args.command == "propose":
            c.pinned_external_width_mm = args.pinned_width
            c.max_external_mm = tuple(args.max_external) if args.max_external else None
            c.port_diameter_mm = args.port_diameter
            c.port_slot_mm = tuple(args.port_slot) if args.port_slot else None
            v = propose(drivers, args.impedance, args.enclosure, tone, args.jack, c, args.name)
        else:
            port = None
            if args.enclosure == "closed-ported":
                if args.port_length is None or (args.port_diameter is None and args.port_slot is None):
                    raise ValueError("evaluate closed-ported needs --port-length and --port-diameter or --port-slot")
                port = port_dims(1.0, 1.0, diameter_mm=args.port_diameter,
                                 slot_mm=tuple(args.port_slot) if args.port_slot else None)
                port.length_mm = args.port_length
                port.warnings = []
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
