"""Guitar speaker cabinet voicing engine (see skills/speaker-cab and
projects/Speaker-cab-system/2026-09-08-speaker-cab-system-design.md).

Pure functions over a Driver record loaded from the YAML frontmatter of
knowledge/speakers/<slug>.md. All internal math is SI. Every prediction is
unverified until listening notes say otherwise.

CLI exit codes: 0 sheet written; 1 input error (speaker note, tone target, or an
engine ValueError), nothing written; 2 blockers, sheet still written (argparse
usage errors also exit 2).
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
    "frame_diameter_mm", "data_status", "sources", "status",
)
# May be null only when data_status is "missing".
TS_FIELDS = ("qts", "qes", "qms", "vas_l", "xmax_mm", "sd_cm2")
# le_mh is optional (unused by the engine, rarely published).
POSITIVE_FIELDS = (
    "diameter_in", "power_w", "sensitivity_db", "fs_hz", "re_ohm",
    "cutout_mm", "bolt_circle_mm", "bolt_count", "depth_mm", "weight_kg", "le_mh",
    "displacement_l", "frame_diameter_mm", "magnet_diameter_mm",
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
    est = meta.get("magnet_diameter_estimated")
    if est is not None and not isinstance(est, bool):
        errors.append(f"magnet_diameter_estimated must be true or false, got {est!r}")
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
    frame_diameter_mm: float
    magnet_diameter_mm: float | None
    magnet_diameter_estimated: bool
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
        frame_diameter_mm=meta["frame_diameter_mm"],
        magnet_diameter_mm=meta.get("magnet_diameter_mm"),
        magnet_diameter_estimated=bool(meta.get("magnet_diameter_estimated", False)),
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

MIN_PORT_LENGTH_MM = 24.0   # the 12 mm back panel plus the 12 mm flange ring; nothing shorter can be built
# Purchasable round port tubes: Schedule 40 PVC or ABS inside diameters for
# 2, 3, 4, and 6 inch nominal pipe, with their outside diameters. Starting
# values (see speaker-cab-construction); the hard maximum is the largest tube.
PORT_TUBE_ID_MM = (52.0, 77.3, 101.5, 153.2)
PORT_TUBE_OD_MM = {52.0: 60.3, 77.3: 88.9, 101.5: 114.3, 153.2: 168.3}
MAX_PORT_DIAMETER_MM = 153.2
DEFAULT_PORT_DIAMETER_MM = 77.3


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
        if diameter_mm <= 0:
            raise ValueError("diameter_mm must be positive")
        return math.pi * (diameter_mm / 2e3) ** 2
    w, h = slot_mm
    if w <= 0 or h <= 0:
        raise ValueError("slot_mm must be two positive numbers")
    return (w / 1e3) * (h / 1e3)


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


def port_air_speed(driver: Driver, fb_hz: float, area_cm2: float) -> float:
    """Worst-case port air speed in m/s: full Xmax excursion at Fb.
    Needs only Sd and Xmax, so it also runs for drivers without full T/S."""
    if driver.sd_cm2 is None or driver.xmax_mm is None:
        raise ValueError(f"{driver.slug}: sd_cm2 and xmax_mm are needed for the air-speed check")
    volume_velocity = driver.sd_m2 * driver.xmax_m * 2.0 * math.pi * fb_hz
    return volume_velocity / (area_cm2 / 1e4)


def tube_from_table(diameter_mm: float) -> float:
    """The PORT_TUBE_ID_MM entry equal to diameter_mm (float noise tolerated), else ValueError."""
    for tube in PORT_TUBE_ID_MM:
        if abs(diameter_mm - tube) < 1e-6:
            return tube
    raise ValueError(f"port tube must be one of {', '.join(f'{t:g}' for t in PORT_TUBE_ID_MM)} mm, "
                     f"not {diameter_mm:g}")


def snap_tube_id(diameter_mm: float) -> float:
    """Smallest purchasable tube inside diameter not below diameter_mm, else the largest."""
    for tube in PORT_TUBE_ID_MM:
        if tube >= diameter_mm - 1e-9:
            return tube
    return PORT_TUBE_ID_MM[-1]


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
LINES = ("tolex", "hardwood")
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
            "Parallel out: an external cabinet of the same impedance halves the combined "
            "load; set the amp tap to the combined impedance, not this cabinet's alone.")
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
CUTOUT_MARGIN_MM = 25.0    # cutout edge to brace or divider
SHELL_MARGIN_MM = 48.0     # cutout edge to shell inner face: grill strip 40 + 2 x 4 mm grill clearance
CUTOUT_GAP_MM = 68.0       # between the two cutouts of a 2x12: brace or divider 18 + 2 x 25
HARDWOOD_FLOOR_EXTRA_MM = 2.0   # the hardwood line's 19 mm panels take 1 mm per side from the 18 mm box
BASE_EXTERNAL_IN = (20.0, 18.0, 11.0)
# Parts the generator builds inside the air box (knowledge/speaker-cab-construction):
CLEAT_MM = 18.0                 # 18 x 18 cleats along the baffle and the back
STIFFENER_MM = (18.0, 40.0)     # 18 proud, 40 flat, across any span over SPAN_MAX_MM
SPAN_MAX_MM = 450.0
NO_SHELL_STIFFENER_LINES = ("hardwood",)   # lines whose top, bottom, and sides take no stiffener (as cablayout)
DEFAULT_BAFFLE_CLEAT_EDGES = {"closed": "all", "closed-ported": "all", "open": "top-bottom", "semi-open": "top-bottom"}   # floating baffle cleat edges by enclosure (as cablayout); a cab.py override can still diverge, like the stiffener case above; the layout and air-volume checks are the final authority
BRACE_MM = (18.0, 60.0)         # center brace on a mono 2x12
JACK_PLATE_H_MM = 70.0          # jack plate cutout height; the back stiffener stops above it
JACK_CLEAR_MM = 25.0
FLANGE_RING_T_MM = 12.0         # plywood flange ring on the inside of the back for a round port
FLANGE_RING_EXTRA_MM = 60.0     # ring outside diameter = tube outside diameter + 60
TUBE_WALL_FALLBACK_MM = 5.5     # wall assumed for a tube diameter outside PORT_TUBE_ID_MM


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
    if min(internal_mm) <= 0:
        raise ValueError("internal dimensions must be positive")
    return Box(external_mm=external_from_internal(internal_mm, **panel_kwargs),
               internal_mm=tuple(internal_mm), gross_l=gross_volume_l(internal_mm),
               warnings=dimension_ratio_warnings(internal_mm))


def site_default_box(**panel_kwargs) -> Box:
    external = tuple(x * MM_PER_INCH for x in BASE_EXTERNAL_IN)
    return make_box(internal_from_external(external, **panel_kwargs), **panel_kwargs)


def min_internal_width_mm(driver_count: int, cutout_mm: float) -> float:
    """Cutouts side by side, 44 mm to each shell wall and a 68 mm gap between
    two (the brace or divider plus 25 mm each side); the same floor for a mono
    and a stereo 2x12 because the divider replaces the brace."""
    return driver_count * cutout_mm + (driver_count - 1) * CUTOUT_GAP_MM + 2 * SHELL_MARGIN_MM


def min_internal_height_mm(cutout_mm: float, slot_h_mm: float | None = None) -> float:
    """Cutout plus 44 mm top and bottom; a front slot port adds its height and
    the 18 mm shelf under the baffle."""
    extra = (slot_h_mm + BAFFLE_MM) if slot_h_mm else 0.0
    return cutout_mm + 2 * SHELL_MARGIN_MM + extra


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


def _port_inside_l(port: Port) -> float:
    """Port air inside the internal box, liters: a round tube's length through
    the back panel and a slot's length through the baffle lie outside the box."""
    panel = BAFFLE_MM if port.shape == "slot" else BACK_MM
    return port.area_cm2 / 1e4 * max(port.length_mm - panel, 0.0)


def inside_parts_l(internal_mm, enclosure: str, driver_count: int, chambers: int,
                   jack_config: str, port: Port | None, line: str,
                   port_count: int | None = None, panel_mm: float = PANEL_MM) -> float:
    """Liters taken by the parts the generator builds inside the air box,
    estimated the way scripts/cablayout.py builds them: 18 x 18 cleats along
    the baffle (top, bottom unless a slot port, and the two outer sides only
    when DEFAULT_BAFFLE_CLEAT_EDGES resolves to "all" for the enclosure) and
    the back
    (closed: a full frame; open: top, bottom, and the panel-height side
    cleats), the modeled center brace of a mono 2x12 (Constraints.brace_l and
    --brace-l mean extra bracing beyond it), 18 x 40 stiffeners across any
    shell or back span over 450 mm between glued members (the back one stops
    above the jack plate), the slot shelf and cheeks behind the baffle (the
    shelf starts at the baffle face, so its 18 mm through the baffle lies
    outside the box), and a round port's tube wall and flange ring. The
    divider and the port air have their own volume terms. Every part is birch
    on both lines, and a NO_SHELL_STIFFENER_LINES line (hardwood) has no top,
    bottom, or side stiffener, as in the layout; jack_config is accepted for
    symmetry with the callers and unused. panel_mm is the divider thickness of
    a stereo box. This has no baffle_cleat_edges argument: the sheet's
    allowance is a prediction from the line and enclosure alone, before
    cab.py's aesthetics exist, exactly like the stiffener prediction above."""
    w, h, d = internal_mm
    per_chamber = driver_count // chambers
    count = port_count or per_chamber
    closed = enclosure in ("closed", "closed-ported")
    slot = port is not None and port.shape == "slot"
    slot_h = port.slot_h_mm if slot else 0.0
    shelf = port.length_mm if slot else 0.0
    w_c = (w - panel_mm) / 2.0 if chambers == 2 else w
    c2 = CLEAT_MM ** 2
    total = 0.0
    # baffle cleats (floating baffle, the default)
    total += chambers * w_c * c2
    if not slot:
        total += chambers * w_c * c2
    if DEFAULT_BAFFLE_CLEAT_EDGES[enclosure] == "all":
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
    shell = line not in NO_SHELL_STIFFENER_LINES
    for span in segs:
        if shell and span > SPAN_MAX_MM:
            if top_len > 50.0:
                total += sw * sd * top_len
            if bot_len > 50.0:
                total += sw * sd * bot_len
    if closed:
        back_len = h - CLEAT_MM - (CLEAT_MM + JACK_CLEAR_MM + JACK_PLATE_H_MM + CUTOUT_MARGIN_MM)
        if w_c > SPAN_MAX_MM and back_len > 50.0:
            total += chambers * sw * sd * back_len
    side_span = max(slot_h, h - slot_h - BAFFLE_MM) if slot else h
    if shell and side_span > SPAN_MAX_MM:
        total += 2 * sw * sd * top_len
    # slot shelf, end cheeks, center cheeks
    if slot:
        avail = w_c - (count - 1) * PANEL_MM
        cheek = (avail - count * port.slot_w_mm) / 2.0
        inside = max(shelf - BAFFLE_MM, 0.0)      # the shelf's run through the baffle is outside
        per_chamber_parts = w_c * inside * BAFFLE_MM + (count - 1) * PANEL_MM * inside * slot_h
        if cheek > 0.5:
            per_chamber_parts += 2 * cheek * inside * slot_h
        total += chambers * per_chamber_parts
    # round port: tube wall inside the box and the flange ring (the ring is the
    # whole port when the tube would not reach past the back panel)
    if port is not None and port.shape == "round":
        id_mm, length = port.diameter_mm, port.length_mm
        od = next((od for tube, od in PORT_TUBE_OD_MM.items() if abs(tube - id_mm) < 0.05),
                  id_mm + 2 * TUBE_WALL_FALLBACK_MM)
        ring_od = od + FLANGE_RING_EXTRA_MM
        if length > 2 * BACK_MM:
            tube = math.pi / 4.0 * (od ** 2 - id_mm ** 2) * (length - BACK_MM)
            ring = math.pi / 4.0 * (ring_od ** 2 - od ** 2) * FLANGE_RING_T_MM
        else:
            tube = 0.0
            ring = math.pi / 4.0 * (ring_od ** 2 - id_mm ** 2) * max(length - BACK_MM, 0.0)
        total += chambers * count * (tube + ring)
    return total / 1e6


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
        warnings.append(f"{driver.slug}: Thiele-Small volume {vb:.1f} L for '{low_end}' is "
                        f"outside the practical range {lo:.0f} to {hi:.0f} L; started from the "
                        f"clamped {clamped:.1f} L")
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


def _air_speed_driver(driver: Driver, drivers_per_port: float, warnings: list) -> Driver:
    sd, xmax = driver.sd_cm2, driver.xmax_mm
    assumed = []
    if sd is None:
        sd, assumed = FALLBACK_SD_CM2, assumed + [f"Sd {FALLBACK_SD_CM2:g} cm2"]
    if xmax is None:
        xmax, assumed = FALLBACK_XMAX_MM, assumed + [f"Xmax {FALLBACK_XMAX_MM:g} mm"]
    if assumed:
        warnings.append(f"{driver.slug}: port air speed uses assumed " + " and ".join(assumed))
    return replace(driver, sd_cm2=sd * drivers_per_port, xmax_mm=xmax)


def _speaker_summary(driver: Driver, impedance) -> dict:
    return {"slug": driver.slug, "brand": driver.brand, "model": driver.model,
            "impedance_ohm": impedance, "power_w": driver.power_w,
            "sensitivity_db": driver.sensitivity_db, "data_status": driver.data_status,
            "analog_of": driver.analog_of, "cutout_mm": driver.cutout_mm,
            "bolt_circle_mm": driver.bolt_circle_mm, "bolt_count": driver.bolt_count,
            "depth_mm": driver.depth_mm, "weight_kg": driver.weight_kg,
            "displacement_l": driver.displacement_l,
            "displacement_estimated": driver.displacement_estimated,
            "frame_diameter_mm": driver.frame_diameter_mm,
            "magnet_diameter_mm": driver.magnet_diameter_mm,
            "magnet_diameter_estimated": driver.magnet_diameter_estimated}


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
    mismatch_accepted = wr.recommended is None and c.accept_impedance_mismatch
    if mismatch_accepted:
        cabinet_ohm = " or ".join(dict.fromkeys(f"{o.impedance_ohm:g}" for o in wr.options))
        warnings.append(f"impedance mismatch accepted: {cabinet_ohm} ohm cabinet on amp taps "
                        f"{list(tone['impedance_options_ohm'])}")
    elif wr.recommended is None:
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
                   "options": [asdict(o) for o in wr.options],
                   "mismatch_accepted": mismatch_accepted}
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


def _port_report(lead, per_chamber_drivers, chamber_net, port, count, warnings) -> tuple:
    """The port as built in its chamber: (actual tuning Hz, port dict). count
    identical ports in a chamber tune like one port in 1/count of the chamber
    and each carries 1/count of the drivers' volume velocity."""
    warnings.extend(port.warnings)
    area_m2 = port.area_cm2 / 1e4
    fb = port_tuning_hz(chamber_net / count / 1e3, area_m2, port.length_mm / 1e3)
    speed_driver = _air_speed_driver(lead, per_chamber_drivers / count, warnings)
    port.air_speed_ms = port_air_speed(speed_driver, fb, port.area_cm2)
    if port.air_speed_ms > PORT_V_MAX and not any("still above" in w for w in port.warnings):
        warnings.append(f"port air speed {port.air_speed_ms:.1f} m/s above {PORT_V_MAX} m/s")
    port.volume_l = area_m2 * port.length_mm   # m2 x mm is liters
    port_dict = {**asdict(port), "location": "front" if port.shape == "slot" else "rear",
                 "per_chamber": True, "count": count}
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


def _prediction_summary(prediction: dict) -> str:
    if "qtc" in prediction:
        return f"Qtc {prediction['qtc']:.2f}, {prediction['character']}"
    if "peak_db" in prediction:
        return (f"Fb {prediction['fb_hz']:.0f} Hz, peak {prediction['peak_db']:.1f} dB, "
                f"{prediction['character']}")
    return prediction["character"]


def _volumes(method, per_driver_net, per_chamber_drivers, chambers, displacement, brace_l,
             port_l_total, divider_l, inside_l, gross_l) -> dict:
    """gross = net + displacement + brace + port (air inside the box) + divider
    + inside_parts; port.volume_l on the port dict is the whole port."""
    chamber_net = per_driver_net * per_chamber_drivers
    return {"method": method, "per_driver_net_l": per_driver_net,
            "per_chamber_net_l": chamber_net, "net_total_l": chamber_net * chambers,
            "displacement_l": displacement, "brace_l": brace_l, "port_l": port_l_total,
            "divider_l": divider_l, "inside_parts_l": inside_l, "gross_l": gross_l}


def _wall_material(c: Constraints) -> str:
    if c.line == "tolex":
        return "baltic birch plywood"
    return c.species or "hardwood, species not set"


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
                      "pinned_external_height_mm": c.pinned_external_height_mm,
                      "max_external_mm": c.max_external_mm,
                      "port_count": None if port_dict is None else port_dict["count"],
                      "line": c.line, "species": c.species,
                      "wall_material": _wall_material(c)},
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


# ---------------------------------------------------------------------------
# Evaluate an existing box
# ---------------------------------------------------------------------------

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
                              c.line, port_count, panel_mm=c.panel_mm)
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
