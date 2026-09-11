"""cablayout.py: numeric layout kernel for MaximoCabs guitar speaker cabinets.

Reads an approved voicing.json (scripts/cabvoice.py output) plus an
aesthetics block and computes every part blank with its position, joinery
schedule, cutouts, ports, hardware positions, speaker envelopes, chamber
volumes, mass, center of mass, and tolex yardage. No CAD here:
scripts/cabmodel.py builds build123d solids from the Layout this returns.

Coordinate frame: X width centered at 0, Y depth with the external front
face at 0 and positive toward the back, Z height with the floor at 0.
Dimension tuples copied from voicing.json are (width, height, depth);
blank positions and sizes are (x, y, z) in the cab frame.

Every number below is a starting value recorded in
knowledge/speaker-cab-construction.md unless the design marks it locked.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import cabvoice  # noqa: E402  (sibling module: constants and port_dims)

# === TASK 4 ===
MM_PER_INCH = 25.4
PANEL_MM = {"tolex": 18.0, "hardwood": 19.0}   # shell thickness per line
BACK_MM = 12.0
BAFFLE_MM = 18.0
RECESS_MM = 20.0          # baffle front face behind the front edge (locked)
CLEAT_MM = 18.0
GRILL_STRIP_T_MM = 12.0
GRILL_STRIP_W_MM = 40.0
GRILL_CLEARANCE_MM = 2.0
FLANGE_T_MM = 5.0
SPACER_MM = 5.0
SHELL_MARGIN_MM = 44.0    # cutout edge to shell inner face
CUTOUT_MARGIN_MM = 25.0   # cutout edge to brace or divider
CUTOUT_GAP_MM = 68.0      # between the two cutouts of a 2x12 (18 + 2 x 25)
BRACE_MM = (18.0, 60.0)
DIVIDER_MM = 18.0
STIFFENER_MM = (18.0, 40.0)
SPAN_MAX_MM = 450.0
BOLT_HOLE_MM = 6.5
DADO_MM = 6.0
BASKET_LEN_MM = 100.0
COVER_MM = 12.0
GENERIC_MAGNET_MM = 185.0
CLEARANCE_MM = 25.0
HARDWARE_KG = 1.0
TOLEX_WASTE = 1.15
ROLL_MM = {54: 1371.6, 32: 812.8}
STOCK_SHEET_MM = (2440.0, 1220.0)
STOCK_HARDWOOD_MM = (3050.0, 600.0)
FLANGE_RING_T_MM = 12.0
FLANGE_RING_EXTRA_MM = 60.0
BIRCH_DENSITY = 680.0
PVC_DENSITY = 1400.0
SPECIES_DENSITY = {"black walnut": 610.0, "black cherry": 560.0,
                   "hard maple": 705.0, "sapele": 670.0}
PORT_TUBE_OD_MM = {52.0: 60.3, 77.3: 88.9, 101.5: 114.3, 153.2: 168.3}
PORT_TUBE_NOMINAL = {52.0: "2 in", 77.3: "3 in", 101.5: "4 in", 153.2: "6 in"}
TUBE_WALL_FALLBACK_MM = 5.5
JACK_CLEAR_MM = 25.0
BAFFLE_CLEARANCE_MM = 1.0     # floating baffle side clearance
BRACE_SETBACK_MM = 2.0        # brace front face behind the baffle back face
FOOT_DEFAULT_INSET_MM = 32.0
GRILL_FRONT_MM = 3.0          # grill frame face behind the front edge
YARD_M = 0.9144

assert RECESS_MM == cabvoice.RECESS_MM
assert BAFFLE_MM == cabvoice.BAFFLE_MM
assert BACK_MM == cabvoice.BACK_MM
assert CUTOUT_MARGIN_MM == cabvoice.CUTOUT_MARGIN_MM
assert MM_PER_INCH == cabvoice.MM_PER_INCH

JOINTS = ("finger", "dovetail")
BAFFLE_MOUNTS = ("floating", "fixed")
HANDLES = ("strap", "recessed-side")
CORNERS = ("black", "chrome", "none")
FEET = ("rubber", "tilt-back")


@dataclass
class Aesthetics:
    corner_joint: str = "finger"
    finger_width_mm: float | None = None
    dovetail_slope: float = 8.0
    dovetail_pin_mm: float | None = None
    dovetail_tail_mm: float = 30.0
    baffle_mount: str = "floating"
    handle: str = "strap"
    handle_screw_spacing_mm: float = 228.6
    recessed_handle_cutout_mm: tuple = (140.0, 90.0)
    jack_plate_cutout_mm: tuple = (110.0, 70.0)
    corners: str | None = None
    corner_allowance_mm: float = 50.0
    piping: bool = False
    feet: str = "rubber"
    foot_diameter_mm: float = 40.0
    foot_inset_mm: float = 32.0
    tolex_roll_in: int = 54
    head_width_mm: float | None = None
    tolex_color: str = ""
    grill_cloth: str = ""
    finish: str = ""

    def validate(self) -> list:
        errors = []
        if self.corner_joint not in JOINTS:
            errors.append(f"corner_joint must be one of {', '.join(JOINTS)}")
        if self.baffle_mount not in BAFFLE_MOUNTS:
            errors.append(f"baffle_mount must be one of {', '.join(BAFFLE_MOUNTS)}")
        if self.handle not in HANDLES:
            errors.append(f"handle must be one of {', '.join(HANDLES)}")
        if self.corners is not None and self.corners not in CORNERS:
            errors.append(f"corners must be one of {', '.join(CORNERS)}")
        if self.feet not in FEET:
            errors.append(f"feet must be one of {', '.join(FEET)}")
        if self.tolex_roll_in not in ROLL_MM:
            errors.append("tolex_roll_in must be 54 or 32")
        for name in ("finger_width_mm", "dovetail_pin_mm", "head_width_mm"):
            v = getattr(self, name)
            if v is not None and not v > 0:
                errors.append(f"{name} must be positive or None")
        for name in ("dovetail_slope", "dovetail_tail_mm", "handle_screw_spacing_mm",
                     "foot_diameter_mm"):
            if not getattr(self, name) > 0:
                errors.append(f"{name} must be positive")
        for name in ("corner_allowance_mm", "foot_inset_mm"):
            if getattr(self, name) < 0:
                errors.append(f"{name} must not be negative")
        for name in ("recessed_handle_cutout_mm", "jack_plate_cutout_mm"):
            v = getattr(self, name)
            if len(v) != 2 or not all(x > 0 for x in v):
                errors.append(f"{name} must be (width, height) in mm, both positive")
        return errors


@dataclass
class Speaker:
    slug: str
    cutout_mm: float
    bolt_circle_mm: float
    bolt_count: int
    depth_mm: float
    weight_kg: float
    displacement_l: float
    frame_diameter_mm: float
    magnet_diameter_mm: float | None
    magnet_diameter_estimated: bool


@dataclass
class PortSpec:
    shape: str
    diameter_mm: float | None
    slot_w_mm: float | None
    slot_h_mm: float | None
    length_mm: float
    location: str
    count: int


@dataclass
class CabSpec:
    name: str
    line: str
    species: str | None
    wall_material: str
    external_mm: tuple
    internal_mm: tuple
    panel_mm: float
    back_mm: float
    baffle_mm: float
    recess_mm: float
    enclosure_type: str
    driver_count: int
    chambers: int
    jack_config: str
    open_fraction: float | None
    speakers: list
    port: PortSpec | None
    net_total_l: float
    per_chamber_net_l: float
    prediction_status: str
    aesthetics: Aesthetics
    sheet_inside_parts_l: float | None = None   # the sheet's allowance for cleats, stiffeners, shelf, ring

    @property
    def shell_mm(self) -> float:
        return PANEL_MM[self.line]

    @property
    def closed(self) -> bool:
        return self.enclosure_type in ("closed", "closed-ported")


@dataclass
class Blank:
    name: str
    qty: int
    material: str
    density: float
    shape: str = "box"
    pos: tuple = (0.0, 0.0, 0.0)
    size: tuple = (0.0, 0.0, 0.0)
    blank_mm: tuple = (0.0, 0.0, 0.0)
    features: list = field(default_factory=list)
    notes: str = ""
    chamber: int | None = None
    length_axis: str | None = None

    @property
    def box(self) -> tuple:
        """((x0, y0, z0), (x1, y1, z1)) for box blanks; the enclosing box for tubes."""
        if self.shape == "box":
            x0, y0, z0 = self.pos
            dx, dy, dz = self.size
            return ((x0, y0, z0), (x0 + dx, y0 + dy, z0 + dz))
        cx, y0, cz = self.pos
        od, length, _ = self.size
        r = od / 2.0
        return ((cx - r, y0, cz - r), (cx + r, y0 + length, cz + r))


@dataclass
class Cutout:
    speaker: int
    chamber: int
    center: tuple
    diameter: float
    bolt_circle: float
    bolt_count: int
    bolt_centers: list


@dataclass
class RoundPort:
    chamber: int
    center: tuple
    id_mm: float
    od_mm: float
    length_mm: float
    ring_od_mm: float
    y0: float
    y1: float


@dataclass
class SlotPort:
    chamber: int
    x0: float
    x1: float
    slot_h_mm: float
    shelf_depth_mm: float
    cheek_w_mm: float


@dataclass
class Hardware:
    item: str
    position: tuple
    cutout: tuple | None
    panel: str
    notes: str


@dataclass
class Envelope:
    speaker: int
    chamber: int
    center: tuple
    y0: float
    basket_d: float
    basket_len: float
    magnet_d: float
    magnet_len: float
    flange_d: float
    flange_t: float


@dataclass
class Chamber:
    index: int
    box: tuple
    port_air: list
    gross_l: float
    net_l: float
    displacement_l: float
    sheet_net_l: float


@dataclass
class Check:
    name: str
    level: str
    message: str


@dataclass
class Layout:
    spec: CabSpec
    parts: list
    cutouts: list
    round_ports: list
    slot_ports: list
    hardware: list
    envelopes: list
    chambers: list
    gross_l: float
    net_l: list
    mass_kg: dict
    com_mm: tuple
    tolex: dict | None
    part_count: int
    notes: list

    def to_dict(self) -> dict:
        from dataclasses import asdict
        d = asdict(self)
        d["spec"]["aesthetics"] = asdict(self.spec.aesthetics)
        return _plain(d)


def _plain(obj):
    """Tuples to lists, recursively, so json.dumps output is stable."""
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    return obj


@dataclass
class Frame:
    """Derived frame numbers every builder needs (internal helper)."""
    W: float
    H: float
    D: float
    t: float
    x0: float
    x1: float
    z0: float
    z1: float
    y_bf: float          # baffle front face
    y_bb: float          # baffle back face
    y_bi: float          # back panel inner face (open backs too: the engine's internal depth)
    closed: bool
    slot_h: float        # 0 without a slot port
    shelf_depth: float   # 0 without a slot port
    chambers: list       # [(xa, xb), ...] chamber x ranges
    z_vis0: float        # visible baffle bottom (shelf top with a slot)
    x_b0: float          # baffle blank extents
    x_b1: float
    z_b0: float
    z_b1: float

    @property
    def chamber_centers(self) -> list:
        return [(a + b) / 2.0 for a, b in self.chambers]

    @property
    def shelf_top(self) -> float:
        return self.z0 + self.slot_h + BAFFLE_MM


def species_density(name) -> float | None:
    if not name:
        return None
    key = str(name).strip().lower()
    if key in SPECIES_DENSITY:
        return SPECIES_DENSITY[key]
    for word, canonical in (("walnut", "black walnut"), ("cherry", "black cherry"),
                            ("maple", "hard maple"), ("sapele", "sapele")):
        if word in key:
            return SPECIES_DENSITY[canonical]
    return None


def species_name(name) -> str:
    key = str(name).strip().lower()
    for word, canonical in (("walnut", "black walnut"), ("cherry", "black cherry"),
                            ("maple", "hard maple"), ("sapele", "sapele")):
        if word in key:
            return canonical
    return key


def load_voicing(path) -> dict:
    return json.loads(Path(path).read_text())


def _speaker_from(s: dict) -> Speaker:
    return Speaker(
        slug=s["slug"], cutout_mm=float(s["cutout_mm"]),
        bolt_circle_mm=float(s["bolt_circle_mm"]), bolt_count=int(s["bolt_count"]),
        depth_mm=float(s["depth_mm"]), weight_kg=float(s["weight_kg"]),
        displacement_l=float(s["displacement_l"]),
        frame_diameter_mm=float(s["frame_diameter_mm"]),
        magnet_diameter_mm=(None if s["magnet_diameter_mm"] is None
                            else float(s["magnet_diameter_mm"])),
        magnet_diameter_estimated=bool(s["magnet_diameter_estimated"]))


def _port_from(p: dict) -> PortSpec:
    return PortSpec(
        shape=p["shape"],
        diameter_mm=None if p["diameter_mm"] is None else float(p["diameter_mm"]),
        slot_w_mm=None if p["slot_w_mm"] is None else float(p["slot_w_mm"]),
        slot_h_mm=None if p["slot_h_mm"] is None else float(p["slot_h_mm"]),
        length_mm=float(p["length_mm"]), location=p["location"],
        count=int(p["count"]))


def order_from(voicing: dict, aesthetics: Aesthetics) -> CabSpec:
    """CabSpec from a voicing.json dict and the aesthetics block.
    ValueError on sheet blockers, missing keys, a dovetail on the tolex line,
    or invalid aesthetics. Never reads warning text."""
    errors = aesthetics.validate()
    if errors:
        raise ValueError("aesthetics: " + "; ".join(errors))
    try:
        blockers = voicing["blockers"]
        status = voicing["prediction_status"]
        enc = voicing["enclosure"]
        box = voicing["box"]
        con = voicing["construction"]
        vols = voicing["volumes"]
        line, species, wall = con["line"], con["species"], con["wall_material"]
        external = tuple(float(v) for v in box["external_mm"])
        internal = tuple(float(v) for v in box["internal_mm"])
        speakers = [_speaker_from(s) for s in voicing["speakers"]]
        driver_count = int(enc["driver_count"])
        chambers = int(enc["chambers"])
        enclosure_type = enc["type"]
        jack_config = enc["jack_config"]
        open_fraction = enc["open_fraction"]
        port = voicing["port"]
        port_spec = None if port is None else _port_from(port)
        net_total = float(vols["net_total_l"])
        per_chamber = float(vols["per_chamber_net_l"])
        inside = vols.get("inside_parts_l")
        inside = None if inside is None else float(inside)
        name = voicing["name"]
        panel_mm, back_mm = float(con["panel_mm"]), float(con["back_mm"])
        baffle_mm, recess_mm = float(con["baffle_mm"]), float(con["recess_mm"])
    except KeyError as e:
        raise ValueError(f"voicing.json lacks {e.args[0]}") from None
    if blockers:
        raise ValueError("voicing sheet has blockers: " + "; ".join(blockers))
    if line not in PANEL_MM:
        raise ValueError(f"line must be tolex or hardwood, not {line!r}")
    if aesthetics.corner_joint == "dovetail" and line != "hardwood":
        raise ValueError("dovetail corners are a hardwood line option")
    if len(speakers) != driver_count:
        raise ValueError(f"{len(speakers)} speaker entries for {driver_count} drivers")
    if enclosure_type not in cabvoice.ENCLOSURE_TYPES:
        raise ValueError(f"unknown enclosure type {enclosure_type!r}")
    if (back_mm, baffle_mm, recess_mm) != (BACK_MM, BAFFLE_MM, RECESS_MM):
        raise ValueError("sheet construction thicknesses differ from the layout constants")
    if port_spec is not None:
        if port_spec.shape == "slot" and (port_spec.slot_w_mm is None or port_spec.slot_h_mm is None):
            raise ValueError("slot port without slot dimensions")
        if port_spec.shape == "round" and port_spec.diameter_mm is None:
            raise ValueError("round port without a diameter")
    return CabSpec(
        name=name, line=line, species=species, wall_material=wall,
        external_mm=external, internal_mm=internal, panel_mm=panel_mm,
        back_mm=back_mm, baffle_mm=baffle_mm, recess_mm=recess_mm,
        enclosure_type=enclosure_type, driver_count=driver_count, chambers=chambers,
        jack_config=jack_config, open_fraction=open_fraction, speakers=speakers,
        port=port_spec, net_total_l=net_total, per_chamber_net_l=per_chamber,
        prediction_status=status, aesthetics=aesthetics, sheet_inside_parts_l=inside)


def frame(spec: CabSpec) -> Frame:
    W, H, D = spec.external_mm
    t = spec.shell_mm
    x0, x1, z0, z1 = -W / 2 + t, W / 2 - t, t, H - t
    y_bf, y_bb = RECESS_MM, RECESS_MM + BAFFLE_MM
    y_bi = D - BACK_MM      # open-back panels sit in the same plane; the air box stops there
    slot_h = shelf_depth = 0.0
    if spec.port is not None and spec.port.shape == "slot":
        slot_h, shelf_depth = spec.port.slot_h_mm, spec.port.length_mm
    if spec.chambers == 2:
        chambers = [(x0, -DIVIDER_MM / 2), (DIVIDER_MM / 2, x1)]
    else:
        chambers = [(x0, x1)]
    z_vis0 = z0 + slot_h + BAFFLE_MM if slot_h else z0
    if spec.aesthetics.baffle_mount == "floating":
        x_b0, x_b1 = x0 + BAFFLE_CLEARANCE_MM, x1 - BAFFLE_CLEARANCE_MM
        z_b0 = z_vis0 if slot_h else z0 + BAFFLE_CLEARANCE_MM
        z_b1 = z1 - BAFFLE_CLEARANCE_MM
    else:
        x_b0, x_b1 = x0 - DADO_MM, x1 + DADO_MM
        z_b0 = z_vis0 if slot_h else z0 - DADO_MM
        z_b1 = z1 + DADO_MM
    return Frame(W, H, D, t, x0, x1, z0, z1, y_bf, y_bb, y_bi, spec.closed,
                 slot_h, shelf_depth, chambers, z_vis0, x_b0, x_b1, z_b0, z_b1)


def finger_schedule(depth_mm: float, thickness_mm: float,
                    width_hint_mm: float | None = None) -> tuple:
    """(count, width): an odd count nearest depth / hint so both ends are full
    fingers; hint defaults to half the thickness. Count is at least 3."""
    hint = width_hint_mm or thickness_mm / 2.0
    raw = depth_mm / hint
    n = int(round(raw))
    if n % 2 == 0:
        n = n - 1 if abs(raw - (n - 1)) <= abs(raw - (n + 1)) else n + 1
    n = max(3, n)
    return n, depth_mm / n


def dovetail_schedule(depth_mm: float, t_top_mm: float, pin_mm: float,
                      tail_target_mm: float, slope: float) -> dict:
    """Through dovetail along one edge of length depth_mm. Tails on the side
    panel, pins on the top or bottom panel, half-pins at both ends. Widths
    are at the outer face; every pin widens by 2 * flare toward the
    shoulder (half-pins by one flare, inward only) and every tail narrows
    by the same."""
    flare = t_top_mm / slope
    n = max(2, int(round((depth_mm - pin_mm) / (tail_target_mm + pin_mm))))
    while n >= 2:
        tail_w = (depth_mm - (n + 1) * pin_mm) / n
        if tail_w - 2 * flare > 5.0:
            break
        n -= 1
    if n < 2:
        raise ValueError(f"no dovetail layout fits a {depth_mm:g} mm edge with {pin_mm:g} mm pins")
    tails, pins = [], []
    y = pin_mm
    for i in range(n):
        tails.append((y, y + tail_w))
        y += tail_w
        if i < n - 1:
            pins.append((y, y + pin_mm))
            y += pin_mm
    return {"count": n, "tail_w": tail_w, "pin_w": pin_mm, "flare": flare,
            "slope": slope, "tails": tails, "pins": pins,
            "half_pins": [(0.0, pin_mm), (depth_mm - pin_mm, depth_mm)]}


def _rect(y0, y1, z_out, z_sh) -> list:
    return [(y0, z_out), (y1, z_out), (y1, z_sh), (y0, z_sh)]


def _finger_polys(depth, n, z_out, z_sh, gaps_even: bool) -> list:
    w = depth / n
    ks = range(0, n, 2) if gaps_even else range(1, n, 2)
    return [_rect(k * w, (k + 1) * w, z_out, z_sh) for k in ks]


def _dovetail_polys(sch: dict, depth, z_out, z_sh, role: str) -> list:
    """Removal quads in the YZ plane for one corner. role 'tails' removes the
    pin shapes (the side panel keeps its tails); role 'pins' removes the tail
    shapes (the top or bottom panel keeps its pins)."""
    d = sch["flare"]
    polys = []
    if role == "tails":
        a, b = sch["half_pins"][0]
        polys.append([(a, z_out), (b, z_out), (b + d, z_sh), (a, z_sh)])
        for (y0, y1) in sch["pins"]:
            polys.append([(y0, z_out), (y1, z_out), (y1 + d, z_sh), (y0 - d, z_sh)])
        a, b = sch["half_pins"][1]
        polys.append([(a, z_out), (b, z_out), (b, z_sh), (a - d, z_sh)])
    else:
        for (y0, y1) in sch["tails"]:
            polys.append([(y0, z_out), (y1, z_out), (y1 - d, z_sh), (y0 + d, z_sh)])
    return polys


def shell_material(spec: CabSpec) -> tuple:
    """(material name, density) for the shell panels."""
    if spec.line == "tolex":
        return f"baltic birch {PANEL_MM['tolex']:g} mm", BIRCH_DENSITY
    dens = species_density(spec.species)
    name = species_name(spec.species) if spec.species else "hardwood, species not set"
    return f"{name} {PANEL_MM['hardwood']:g} mm", (dens if dens is not None else BIRCH_DENSITY)


HARDWOOD_GRAIN_NOTE = "grain front to back on all four panels, book-matched, show face out"
HARDWOOD_CLEAT_NOTE = "screwed through slotted holes, glued at the center 100 mm only"


def birch(t: float) -> str:
    return f"baltic birch {t:g} mm"


def shell_blanks(spec: CabSpec) -> list:
    """Top, bottom, and two sides as full-size blanks with the comb removals
    at the four corner blocks as edge_cuts features."""
    fr = frame(spec)
    W, H, D, t = fr.W, fr.H, fr.D, fr.t
    a = spec.aesthetics
    material, density = shell_material(spec)
    if a.corner_joint == "finger":
        n, w = finger_schedule(D, t, a.finger_width_mm)
        note = (f"finger joint, {n} fingers of {w:.1f} mm, both ends full, "
                "front finger on top and bottom")
        side_top = _finger_polys(D, n, H, H - t, True)
        side_bot = _finger_polys(D, n, 0.0, t, True)
        top_polys = _finger_polys(D, n, H, H - t, False)
        bot_polys = _finger_polys(D, n, 0.0, t, False)
    else:
        sch = dovetail_schedule(D, t, a.dovetail_pin_mm or t / 2.0, a.dovetail_tail_mm,
                                a.dovetail_slope)
        note = (f"through dovetail, {sch['count']} tails of {sch['tail_w']:.1f} mm, "
                f"pins {sch['pin_w']:.1f} mm, slope 1:{sch['slope']:g}, half-pins both ends, "
                "tails on the sides")
        side_top = _dovetail_polys(sch, D, H, H - t, "tails")
        side_bot = _dovetail_polys(sch, D, 0.0, t, "tails")
        top_polys = _dovetail_polys(sch, D, H, H - t, "pins")
        bot_polys = _dovetail_polys(sch, D, 0.0, t, "pins")
    if spec.line == "hardwood":
        note += "; " + HARDWOOD_GRAIN_NOTE
    left = (-W / 2, -W / 2 + t)
    right = (W / 2 - t, W / 2)
    parts = [
        Blank("side_left", 1, material, density, pos=(-W / 2, 0.0, 0.0), size=(t, D, H),
              blank_mm=(t, H, D), length_axis="Y", notes=note,
              features=[{"type": "edge_cuts", "x": left, "polys": side_top},
                        {"type": "edge_cuts", "x": left, "polys": side_bot}]),
        Blank("side_right", 1, material, density, pos=(W / 2 - t, 0.0, 0.0), size=(t, D, H),
              blank_mm=(t, H, D), length_axis="Y", notes=note,
              features=[{"type": "edge_cuts", "x": right, "polys": side_top},
                        {"type": "edge_cuts", "x": right, "polys": side_bot}]),
        Blank("top", 1, material, density, pos=(-W / 2, 0.0, H - t), size=(W, D, t),
              blank_mm=(t, W, D), length_axis="Y", notes=note,
              features=[{"type": "edge_cuts", "x": left, "polys": top_polys},
                        {"type": "edge_cuts", "x": right, "polys": top_polys}]),
        Blank("bottom", 1, material, density, pos=(-W / 2, 0.0, 0.0), size=(W, D, t),
              blank_mm=(t, W, D), length_axis="Y", notes=note,
              features=[{"type": "edge_cuts", "x": left, "polys": bot_polys},
                        {"type": "edge_cuts", "x": right, "polys": bot_polys}]),
    ]
    return parts


# === TASK 5 ===
def _suffix(spec: CabSpec, c: int) -> str:
    return f"_{c}" if spec.chambers == 2 else ""


def _blank_dims(t: float, a: float, b: float) -> tuple:
    return (t, min(a, b), max(a, b))


def cutout_centers(spec: CabSpec, fr: Frame) -> list:
    """[(x, chamber)] per driver. 1x12 at the chamber center; mono 2x12 at
    +-(cutout + 68) / 2; stereo 44 mm outboard and 25 mm inboard of the
    divider at the minimum width, the surplus split evenly beyond that."""
    if spec.driver_count == 1:
        return [(fr.chamber_centers[0], 0)]
    if spec.chambers == 2:
        out = []
        for i, (xa, xb) in enumerate(fr.chambers):
            cut = spec.speakers[i].cutout_mm
            surplus = (xb - xa) - (cut + SHELL_MARGIN_MM + CUTOUT_MARGIN_MM)
            off = DIVIDER_MM / 2.0 + CUTOUT_MARGIN_MM + cut / 2.0 + surplus / 2.0
            out.append((-off if i == 0 else off, i))
        return out
    c0, c1 = spec.speakers[0].cutout_mm, spec.speakers[1].cutout_mm
    return [(-(c0 / 2.0 + CUTOUT_GAP_MM / 2.0), 0), (c1 / 2.0 + CUTOUT_GAP_MM / 2.0, 0)]


def baffle_and_cutouts(spec: CabSpec, fr: Frame) -> tuple:
    """(baffle Blank, cutouts, dados) where dados maps a shell blank name to
    the notch feature a fixed baffle needs on that panel."""
    a = spec.aesthetics
    dx, dz = fr.x_b1 - fr.x_b0, fr.z_b1 - fr.z_b0
    zc = (fr.z_vis0 + fr.z1) / 2.0
    centers = cutout_centers(spec, fr)
    cutouts, features = [], []
    for i, (xc, chamber) in enumerate(centers):
        s = spec.speakers[i]
        r = s.bolt_circle_mm / 2.0
        bolts = []
        for k in range(s.bolt_count):
            ang = math.radians(90.0 - k * 360.0 / s.bolt_count)
            bolts.append((xc + r * math.cos(ang), zc + r * math.sin(ang)))
        cutouts.append(Cutout(i, chamber, (xc, zc), s.cutout_mm, s.bolt_circle_mm,
                              s.bolt_count, bolts))
        features.append({"type": "cutout", "center": (xc, zc), "d": s.cutout_mm})
        features.append({"type": "holes", "centers": bolts, "d": BOLT_HOLE_MM})
    if a.baffle_mount == "floating":
        note = ("floating baffle: 1 mm clearance per side, felt strips on the cleats, "
                "screwed through the cleats, removable")
    else:
        note = "fixed baffle: glued into 6 mm dados, blank 12 mm oversize"
        if spec.line == "hardwood":
            note += "; glued in the front 100 mm of each dado only (cross-grain rule)"
    if fr.slot_h:
        note += "; bottom edge rests on the slot port shelf"
    mounts = ", ".join(f"{s.bolt_count} bolts on a {s.bolt_circle_mm:g} mm circle"
                       for s in spec.speakers)
    note += f"; speakers front-mounted on T-nuts, {mounts}"
    baffle = Blank("baffle", 1, birch(BAFFLE_MM), BIRCH_DENSITY,
                   pos=(fr.x_b0, fr.y_bf, fr.z_b0), size=(dx, BAFFLE_MM, dz),
                   blank_mm=_blank_dims(BAFFLE_MM, dz, dx), features=features, notes=note)
    dados = {}
    if a.baffle_mount == "fixed":
        y0, y1 = fr.y_bf, fr.y_bb
        zlo = fr.z_b0
        dados["side_left"] = {"type": "notch", "box": ((fr.x0 - DADO_MM, y0, zlo), (fr.x0, y1, fr.z1 + DADO_MM))}
        dados["side_right"] = {"type": "notch", "box": ((fr.x1, y0, zlo), (fr.x1 + DADO_MM, y1, fr.z1 + DADO_MM))}
        dados["top"] = {"type": "notch", "box": ((fr.x0 - DADO_MM, y0, fr.z1), (fr.x1 + DADO_MM, y1, fr.z1 + DADO_MM))}
        if not fr.slot_h:
            dados["bottom"] = {"type": "notch", "box": ((fr.x0 - DADO_MM, y0, fr.z0 - DADO_MM), (fr.x1 + DADO_MM, y1, fr.z0))}
    return baffle, cutouts, dados


def _cleat(name, pos, size, axis, chamber, note) -> Blank:
    length = {"X": size[0], "Y": size[1], "Z": size[2]}[axis]
    return Blank(name, 1, birch(CLEAT_MM), BIRCH_DENSITY, pos=pos, size=size,
                 blank_mm=(CLEAT_MM, CLEAT_MM, length), notes=note, chamber=chamber,
                 length_axis=axis)


def cleat_blanks(spec: CabSpec, fr: Frame) -> list:
    """Baffle cleats (floating baffle only) and back cleats, per chamber, on
    the shell faces. The divider carries no cleats: the baffle and the back
    screw into its edges."""
    parts = []
    base = "18 x 18 birch cleat, screws every 150 mm"
    if spec.line == "hardwood":
        base += "; " + HARDWOOD_CLEAT_NOTE
    bnote = base + "; felt strip between cleat and baffle"
    y_cleat = fr.D - BACK_MM - CLEAT_MM
    for c, (xa, xb) in enumerate(fr.chambers):
        sfx = _suffix(spec, c)
        if spec.aesthetics.baffle_mount == "floating":
            zlo = fr.z_vis0 if fr.slot_h else fr.z0 + CLEAT_MM
            parts.append(_cleat(f"cleat_baffle_top{sfx}", (xa, fr.y_bb, fr.z1 - CLEAT_MM),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, bnote))
            if not fr.slot_h:
                parts.append(_cleat(f"cleat_baffle_bottom{sfx}", (xa, fr.y_bb, fr.z0),
                                    (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, bnote))
            if xa == fr.x0:
                parts.append(_cleat(f"cleat_baffle_left{sfx}", (xa, fr.y_bb, zlo),
                                    (CLEAT_MM, CLEAT_MM, fr.z1 - CLEAT_MM - zlo), "Z", c, bnote))
            if xb == fr.x1:
                parts.append(_cleat(f"cleat_baffle_right{sfx}", (xb - CLEAT_MM, fr.y_bb, zlo),
                                    (CLEAT_MM, CLEAT_MM, fr.z1 - CLEAT_MM - zlo), "Z", c, bnote))
        if spec.closed:
            parts.append(_cleat(f"cleat_back_top{sfx}", (xa, y_cleat, fr.z1 - CLEAT_MM),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, base))
            parts.append(_cleat(f"cleat_back_bottom{sfx}", (xa, y_cleat, fr.z0),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, base))
            if xa == fr.x0:
                parts.append(_cleat(f"cleat_back_left{sfx}", (xa, y_cleat, fr.z0 + CLEAT_MM),
                                    (CLEAT_MM, CLEAT_MM, fr.z1 - fr.z0 - 2 * CLEAT_MM), "Z", c, base))
            if xb == fr.x1:
                parts.append(_cleat(f"cleat_back_right{sfx}", (xb - CLEAT_MM, y_cleat, fr.z0 + CLEAT_MM),
                                    (CLEAT_MM, CLEAT_MM, fr.z1 - fr.z0 - 2 * CLEAT_MM), "Z", c, base))
        else:
            h_p = open_panel_height(spec, fr)
            parts.append(_cleat(f"cleat_back_top{sfx}", (xa, y_cleat, fr.z1 - CLEAT_MM),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, base))
            parts.append(_cleat(f"cleat_back_bottom{sfx}", (xa, y_cleat, fr.z0),
                                (xb - xa, CLEAT_MM, CLEAT_MM), "X", c, base))
            for side, x_c in (("left", xa), ("right", xb - CLEAT_MM)):
                if (side == "left" and xa != fr.x0) or (side == "right" and xb != fr.x1):
                    continue
                parts.append(_cleat(f"cleat_back_{side}_upper{sfx}", (x_c, y_cleat, fr.z1 - h_p),
                                    (CLEAT_MM, CLEAT_MM, h_p - CLEAT_MM), "Z", c, base))
                parts.append(_cleat(f"cleat_back_{side}_lower{sfx}", (x_c, y_cleat, fr.z0 + CLEAT_MM),
                                    (CLEAT_MM, CLEAT_MM, h_p - CLEAT_MM), "Z", c, base))
    return parts


def open_panel_height(spec: CabSpec, fr: Frame) -> float:
    f = spec.open_fraction if spec.open_fraction is not None else cabvoice.OPEN_FRACTION.get(spec.enclosure_type, 0.4)
    return (1.0 - f) * (fr.z1 - fr.z0) / 2.0


def grill_frame_blanks(spec: CabSpec, fr: Frame) -> list:
    """Four 12 x 40 strips with half-lap corners, 2 mm inside the opening,
    face 3 mm behind the front edge, resting on the flanges and 5 mm felt
    corner spacers. Covers only the baffle above the shelf with a slot port."""
    t, w = GRILL_STRIP_T_MM, GRILL_STRIP_W_MM
    xg0, xg1 = fr.x0 + GRILL_CLEARANCE_MM, fr.x1 - GRILL_CLEARANCE_MM
    zg0, zg1 = fr.z_vis0 + GRILL_CLEARANCE_MM, fr.z1 - GRILL_CLEARANCE_MM
    y0, ym, y1 = GRILL_FRONT_MM, GRILL_FRONT_MM + t / 2.0, GRILL_FRONT_MM + t
    note = ("grill frame strip 12 x 40 birch, half-lap corners, cloth wrapped and stapled "
            "at the back, rests on the speaker flanges and 5 mm felt corner spacers, "
            "hook and loop to the baffle")
    mat = birch(GRILL_STRIP_T_MM)
    corners_x = ((xg0, xg0 + w), (xg1 - w, xg1))
    corners_z = ((zg0, zg0 + w), (zg1 - w, zg1))
    horiz_notches = [{"type": "notch", "box": ((cx[0], y0, cz[0]), (cx[1], ym, cz[1]))}
                     for cx in corners_x for cz in corners_z]
    vert_notches = [{"type": "notch", "box": ((cx[0], ym, cz[0]), (cx[1], y1, cz[1]))}
                    for cx in corners_x for cz in corners_z]
    top = Blank("grill_top", 1, mat, BIRCH_DENSITY, pos=(xg0, y0, zg1 - w), size=(xg1 - xg0, t, w),
                blank_mm=(t, w, xg1 - xg0), length_axis="X", notes=note,
                features=[n for n in horiz_notches if n["box"][0][2] == zg1 - w])
    bottom = Blank("grill_bottom", 1, mat, BIRCH_DENSITY, pos=(xg0, y0, zg0), size=(xg1 - xg0, t, w),
                   blank_mm=(t, w, xg1 - xg0), length_axis="X", notes=note,
                   features=[n for n in horiz_notches if n["box"][0][2] == zg0])
    left = Blank("grill_left", 1, mat, BIRCH_DENSITY, pos=(xg0, y0, zg0), size=(w, t, zg1 - zg0),
                 blank_mm=(t, w, zg1 - zg0), length_axis="Z", notes=note,
                 features=[n for n in vert_notches if n["box"][0][0] == xg0])
    right = Blank("grill_right", 1, mat, BIRCH_DENSITY, pos=(xg1 - w, y0, zg0), size=(w, t, zg1 - zg0),
                  blank_mm=(t, w, zg1 - zg0), length_axis="Z", notes=note,
                  features=[n for n in vert_notches if n["box"][0][0] == xg1 - w])
    return [top, bottom, left, right]


def brace_blank(spec: CabSpec, fr: Frame) -> list:
    """Center brace 18 x 60 on a mono 2x12, 2 mm behind the baffle, between
    the bottom (or the shelf) and the top, notched around the baffle cleats."""
    if not (spec.driver_count == 2 and spec.chambers == 1):
        return []
    bw, bd = BRACE_MM
    zb0 = fr.z_vis0 if fr.slot_h else fr.z0
    y0 = fr.y_bb + BRACE_SETBACK_MM
    features = []
    if spec.aesthetics.baffle_mount == "floating":
        features.append({"type": "notch", "box": ((-bw / 2, y0, fr.z1 - CLEAT_MM), (bw / 2, fr.y_bb + CLEAT_MM, fr.z1))})
        if not fr.slot_h:
            features.append({"type": "notch", "box": ((-bw / 2, y0, fr.z0), (bw / 2, fr.y_bb + CLEAT_MM, fr.z0 + CLEAT_MM))})
    note = ("center brace 18 x 60 birch, glued to top and bottom"
            + (" (bottom end on the slot shelf)" if fr.slot_h else "")
            + (", notched around the baffle cleats" if features else ""))
    return [Blank("brace", 1, birch(bw), BIRCH_DENSITY, pos=(-bw / 2, y0, zb0),
                  size=(bw, bd, fr.z1 - zb0), blank_mm=(bw, bd, fr.z1 - zb0),
                  features=features, notes=note, chamber=0, length_axis="Z")]


def divider_blank(spec: CabSpec, fr: Frame) -> list:
    if spec.chambers != 2:
        return []
    note = ("full-height divider 18 mm birch glued to top, bottom, and back; the baffle "
            "screws into its front edge over a felt strip and the back panel into its "
            "rear edge; two sealed chambers")
    return [Blank("divider", 1, birch(DIVIDER_MM), BIRCH_DENSITY,
                  pos=(-DIVIDER_MM / 2, fr.y_bb, fr.z0),
                  size=(DIVIDER_MM, fr.y_bi - fr.y_bb, fr.z1 - fr.z0),
                  blank_mm=_blank_dims(DIVIDER_MM, fr.y_bi - fr.y_bb, fr.z1 - fr.z0),
                  notes=note, chamber=None)]


def _chamber_of(fr: Frame, x: float) -> int:
    for c, (xa, xb) in enumerate(fr.chambers):
        if xa <= x <= xb:
            return c
    return 0


def stiffener_blanks(spec: CabSpec, fr: Frame) -> tuple:
    """(blanks, span notes): one 18 x 40 stiffener glued flat across the
    middle of any shell or back panel span over 450 mm between glued members.
    Open-back panels are left alone (short and removable)."""
    sw, sd = STIFFENER_MM       # 18 proud, 40 flat on the panel
    floating = spec.aesthetics.baffle_mount == "floating"
    y_cleat = fr.D - BACK_MM - CLEAT_MM
    ya_default = fr.y_bb + (CLEAT_MM if floating else 0.0)
    if spec.chambers == 2:
        segs = list(fr.chambers)
    elif spec.driver_count == 2:
        segs = [(fr.x0, -BRACE_MM[0] / 2), (BRACE_MM[0] / 2, fr.x1)]
    else:
        segs = [(fr.x0, fr.x1)]
    parts, notes = [], []
    note = "stiffener 18 x 40 birch glued flat across the middle of a span over 450 mm"
    mat = birch(sw)
    for (xa, xb) in segs:
        span = xb - xa
        if span <= SPAN_MAX_MM:
            continue
        xc = (xa + xb) / 2.0
        c = _chamber_of(fr, xc)
        sfx = _suffix(spec, c)
        ya, yb = ya_default, y_cleat
        if yb - ya > 50.0:
            parts.append(Blank(f"stiffener_top{sfx}", 1, mat, BIRCH_DENSITY,
                               pos=(xc - sd / 2, ya, fr.z1 - sw), size=(sd, yb - ya, sw),
                               blank_mm=(sw, sd, yb - ya), notes=note, chamber=c, length_axis="Y"))
            notes.append(f"top panel span {span:.0f} mm over {SPAN_MAX_MM:.0f}: stiffener added")
        yab = max(ya_default, fr.y_bf + fr.shelf_depth) if fr.slot_h else ya_default
        if yb - yab > 50.0:
            parts.append(Blank(f"stiffener_bottom{sfx}", 1, mat, BIRCH_DENSITY,
                               pos=(xc - sd / 2, yab, fr.z0), size=(sd, yb - yab, sw),
                               blank_mm=(sw, sd, yb - yab), notes=note, chamber=c, length_axis="Y"))
            notes.append(f"bottom panel span {span:.0f} mm over {SPAN_MAX_MM:.0f}: stiffener added")
    # back panel: spans split by the divider only
    if spec.closed:
        back_segs = list(fr.chambers)
        h_plate = spec.aesthetics.jack_plate_cutout_mm[1]
        for (xa, xb) in back_segs:
            span = xb - xa
            if span <= SPAN_MAX_MM:
                continue
            xc = (xa + xb) / 2.0
            c = _chamber_of(fr, xc)
            sfx = _suffix(spec, c)
            za = fr.z0 + CLEAT_MM + JACK_CLEAR_MM + h_plate + CLEARANCE_MM
            zb = fr.z1 - CLEAT_MM
            if zb - za > 50.0:
                parts.append(Blank(f"stiffener_back{sfx}", 1, mat, BIRCH_DENSITY,
                                   pos=(xc - sd / 2, fr.y_bi - sw, za), size=(sd, sw, zb - za),
                                   blank_mm=(sw, sd, zb - za), notes=note + "; stops above the jack plate",
                                   chamber=c, length_axis="Z"))
                notes.append(f"back panel span {span:.0f} mm over {SPAN_MAX_MM:.0f}: stiffener added")
    # side panels: span along z, split by the shelf with a slot port
    side_span = max(fr.slot_h, fr.z1 - fr.z_vis0) if fr.slot_h else fr.z1 - fr.z0
    if side_span > SPAN_MAX_MM:
        zc = (fr.z_vis0 + fr.z1) / 2.0 if fr.slot_h else (fr.z0 + fr.z1) / 2.0
        ya, yb = ya_default, y_cleat
        for side, x_c, c in (("left", fr.x0, 0), ("right", fr.x1 - sw, len(fr.chambers) - 1)):
            parts.append(Blank(f"stiffener_side_{side}", 1, mat, BIRCH_DENSITY,
                               pos=(x_c, ya, zc - sd / 2), size=(sw, yb - ya, sd),
                               blank_mm=(sw, sd, yb - ya), notes=note, chamber=c, length_axis="Y"))
        notes.append(f"side panel span {side_span:.0f} mm over {SPAN_MAX_MM:.0f}: stiffeners added")
    return parts, notes


# === TASK 6 ===
def back_blanks(spec: CabSpec, fr: Frame) -> list:
    """Closed: one 12 mm back flush with the rear edge. Open and semi-open:
    two 12 mm panels top and bottom sized from the open fraction."""
    mat = birch(BACK_MM)
    w = fr.x1 - fr.x0
    if spec.closed:
        note = "12 mm birch back, removable, screwed to the cleats every 150 mm"
        if spec.chambers == 2:
            note += " and into the divider's rear edge"
        return [Blank("back", 1, mat, BIRCH_DENSITY, pos=(fr.x0, fr.D - BACK_MM, fr.z0),
                      size=(w, BACK_MM, fr.z1 - fr.z0),
                      blank_mm=_blank_dims(BACK_MM, fr.z1 - fr.z0, w), notes=note)]
    h_p = open_panel_height(spec, fr)
    f = 1.0 - 2.0 * h_p / (fr.z1 - fr.z0)
    note = (f"open back panel 12 mm birch, {h_p:.0f} mm tall "
            f"((1 - {f:.2f}) x internal height / 2), screwed to the cleats")
    return [Blank("back_upper", 1, mat, BIRCH_DENSITY, pos=(fr.x0, fr.D - BACK_MM, fr.z1 - h_p),
                  size=(w, BACK_MM, h_p), blank_mm=_blank_dims(BACK_MM, h_p, w), notes=note),
            Blank("back_lower", 1, mat, BIRCH_DENSITY, pos=(fr.x0, fr.D - BACK_MM, fr.z0),
                  size=(w, BACK_MM, h_p), blank_mm=_blank_dims(BACK_MM, h_p, w),
                  notes=note + "; carries the jack plate")]


def _attach(parts: list, name: str, features: list) -> None:
    for p in parts:
        if p.name == name:
            p.features.extend(features)
            return
    raise KeyError(f"no blank named {name}")


def jack_plates(spec: CabSpec, fr: Frame) -> tuple:
    """(hardware, features by panel name, warnings): one recessed plate per
    chamber at the bottom center of the back (or the lower open panel),
    25 mm above the cleat."""
    w, h = spec.aesthetics.jack_plate_cutout_mm
    panel = "back" if spec.closed else "back_lower"
    z_p = fr.z0 + CLEAT_MM + JACK_CLEAR_MM + h / 2.0
    text = {"mono": "one 1/4 in jack",
            "mono-parallel-out": "two 1/4 in jacks wired in parallel on one plate",
            "stereo": "one 1/4 in jack per chamber plate"}.get(spec.jack_config, spec.jack_config)
    finish = "brass" if spec.line == "hardwood" else "metal"
    hardware, features, warnings = [], {panel: []}, []
    for c, xc in enumerate(fr.chamber_centers):
        hardware.append(Hardware("jack plate", (xc, fr.D, z_p), (w, h), panel,
                                 f"recessed {finish} plate, cutout {w:g} x {h:g} mm, {text}"))
        features[panel].append({"type": "rect_hole", "axis": "y", "center": (xc, z_p), "w": w, "h": h})
    if not spec.closed:
        top = fr.z0 + open_panel_height(spec, fr)
        if z_p + h / 2.0 + 10.0 > top:
            warnings.append(f"jack plate cutout {h:g} mm tall does not fit the "
                            f"{top - fr.z0:.0f} mm lower open-back panel with 25 mm above the cleat")
    return hardware, features, warnings


def speaker_envelopes(spec: CabSpec, fr: Frame, cutouts: list) -> list:
    out = []
    for co in cutouts:
        s = spec.speakers[co.speaker]
        basket_len = min(BASKET_LEN_MM, s.depth_mm)
        magnet_len = max(0.0, s.depth_mm - BASKET_LEN_MM)
        magnet_d = (s.magnet_diameter_mm + COVER_MM if s.magnet_diameter_mm is not None
                    else GENERIC_MAGNET_MM)
        out.append(Envelope(co.speaker, co.chamber, co.center, fr.y_bf, s.cutout_mm, basket_len,
                            magnet_d, magnet_len, s.frame_diameter_mm, FLANGE_T_MM))
    return out


def _overlap(a0, a1, b0, b1) -> bool:
    return min(a1, b1) - max(a0, b0) > 1e-9


def _circle_box_gap(cx, cz, r, box) -> float:
    (x0, _, z0), (x1, _, z1) = box
    dx = max(x0 - cx, 0.0, cx - x1)
    dz = max(z0 - cz, 0.0, cz - z1)
    return math.hypot(dx, dz) - r


def _envelope_segments(env: Envelope) -> list:
    """[(y_front, y_rear, radius)] steps of the envelope: basket, then magnet
    when there is one. The rearmost face is pushed back by CLEARANCE_MM (an
    axial standoff) so a tube ending within that distance behind the driver
    must also clear it radially. Only the rearmost face carries it: the basket
    cylinder is a bounding model of a frame that really tapers, so a standoff
    on the basket's rear annulus would raise false blockers against a modeling
    artifact, while the magnet rear is the real flat face."""
    segs = [(env.y0, env.y0 + env.basket_len, env.basket_d / 2.0)]
    if env.magnet_len > 0:
        segs.append((env.y0 + env.basket_len, env.y0 + env.basket_len + env.magnet_len,
                     env.magnet_d / 2.0))
    s0, s1, er = segs[-1]
    segs[-1] = (s0, s1 + CLEARANCE_MM, er)
    return segs


def _tube_clear(center, r, ya, yb, chamber, fr, obstacles, envelopes, tubes) -> bool:
    """True when a tube of radius r along y in [ya, yb] at center (x, z)
    keeps CLEARANCE_MM from every obstacle box, envelope segment, other tube,
    and the chamber walls."""
    cx, cz = center
    xa, xb = fr.chambers[chamber]
    need = CLEARANCE_MM - 1e-6
    if cx - r - xa < need or xb - (cx + r) < need:
        return False
    if cz - r - fr.z0 < need or fr.z1 - (cz + r) < need:
        return False
    for box in obstacles:
        if _overlap(ya, yb, box[0][1], box[1][1]) and _circle_box_gap(cx, cz, r, box) < need:
            return False
    for env in envelopes:
        ex, ez = env.center
        for (s0, s1, er) in _envelope_segments(env):
            if _overlap(ya, yb, s0, s1) and math.hypot(cx - ex, cz - ez) - r - er < need:
                return False
    for (tx, tz, tr, ty0, ty1, _) in tubes:
        if _overlap(ya, yb, ty0, ty1) and math.hypot(cx - tx, cz - tz) - r - tr < need:
            return False
    return True


def _ring_clear(center, rr, yb, chamber, fr, obstacles, tubes) -> bool:
    """The flange ring (radius rr, glued to the back over [yb - 12, yb]) must
    not overlap a cleat, stiffener, plate keep-out, another tube or its ring,
    or a wall."""
    if rr <= 0:
        return True
    cx, cz = center
    xa, xb = fr.chambers[chamber]
    ya = yb - FLANGE_RING_T_MM
    if cx - rr < xa - 1e-6 or cx + rr > xb + 1e-6 or cz - rr < fr.z0 - 1e-6 or cz + rr > fr.z1 + 1e-6:
        return False
    for box in obstacles:
        if _overlap(ya, yb, box[0][1], box[1][1]) and _circle_box_gap(cx, cz, rr, box) < -1e-6:
            return False
    for (tx, tz, tr, ty0, ty1, trr) in tubes:
        d = math.hypot(cx - tx, cz - tz)
        if _overlap(ya, yb, ty0, ty1) and d - rr - tr < -1e-6:
            return False
        if d - rr - trr < -1e-6:        # every ring sits on the back, so rings share the y span
            return False
    return True


def _radial_requirement(env: Envelope, ya, yb, r) -> float:
    need = 0.0
    for (s0, s1, er) in _envelope_segments(env):
        if _overlap(ya, yb, s0, s1):
            need = max(need, er)
    return need + CLEARANCE_MM + r


PLACE_STEP_MM = 5.0


def _place_tube(env: Envelope, sign: float, r, ya, yb, fr, obstacles, envelopes, tubes, ring_r=0.0):
    """First clear spot for a tube of radius r beside its driver: outboard at
    driver height, below, lower outboard diagonal, above, each direction
    scanned outward from the radial requirement in 5 mm steps until the
    chamber wall stops it."""
    xd, zd = env.center
    req = _radial_requirement(env, ya, yb, r)
    xa, xb = fr.chambers[env.chamber]
    inv = 1.0 / math.sqrt(2.0)
    for (ux, uz) in ((sign, 0.0), (0.0, -1.0), (sign * inv, -inv), (0.0, 1.0)):
        dist = req
        while True:
            cand = (xd + ux * dist, zd + uz * dist)
            if not (xa <= cand[0] <= xb and fr.z0 <= cand[1] <= fr.z1):
                break
            if (_tube_clear(cand, r, ya, yb, env.chamber, fr, obstacles, envelopes, tubes)
                    and _ring_clear(cand, ring_r, yb, env.chamber, fr, obstacles, tubes)):
                return cand
            dist += PLACE_STEP_MM
    return None


def tube_geometry(id_mm: float) -> tuple:
    """(od, material, note) for a tube inside diameter."""
    if id_mm in PORT_TUBE_OD_MM:
        return PORT_TUBE_OD_MM[id_mm], f"PVC {PORT_TUBE_NOMINAL[id_mm]} sch 40", ""
    od = id_mm + 2 * TUBE_WALL_FALLBACK_MM
    return od, f"tube {id_mm:.1f} mm ID", "not a stock tube size; wall assumed 5.5 mm"


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
                Lf = L - 5.0
                while Lf >= 2 * BACK_MM:
                    if (fr.D - Lf >= fr.y_bb - 1e-6
                            and _place_tube(env, sign, r, fr.D - Lf, yb, fr, obstacles, envelopes, tubes, rr)):
                        fit = Lf
                        break
                    Lf -= 5.0
                why = ("reaches the baffle" if reaches
                       else f"finds no spot with {CLEARANCE_MM:.0f} mm clearance")
                if fit is None:
                    blockers.append(f"port fit: chamber {c} port {j}: no round port of "
                                    f"{id_mm:.1f} mm fits with {CLEARANCE_MM:.0f} mm clearance; use a front slot")
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
                                    blank_mm=(0.0, od, L), chamber=c,
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
                                      + ("" if has_tube else f"; the ring is the port ({ring_t:.0f} mm beyond the panel), no tube")))
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
        blockers.append(f"port fit: slot shelf {L:.0f} mm deep leaves {free:.0f} mm behind it, "
                        f"under the {max(CLEARANCE_MM, s_h):.0f} mm the slot needs to breathe; "
                        "lower the slot height or use a round port")
        return slots, blanks, blockers
    mat18 = birch(BAFFLE_MM)
    for c, (xa, xb) in enumerate(fr.chambers):
        n = port.count
        avail = (xb - xa) - (n - 1) * DIVIDER_MM
        if n * s_w > avail + 1e-6:
            blockers.append(f"port fit: chamber {c}: {n} slot{'s' if n > 1 else ''} of {s_w:.0f} mm "
                            f"do not fit the {xb - xa:.0f} mm chamber"
                            + (" with the 18 mm center cheek" if n > 1 else "")
                            + "; narrow the slot or widen the box")
            continue
        cheek = (avail - n * s_w) / 2.0
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
                                    chamber=c, notes="slot cheek, fills the slot end, glued"))
        x = xa + cheek
        for j in range(n):
            slots.append(SlotPort(c, x, x + s_w, s_h, L, cheek))
            x += s_w
            if j < n - 1:
                blanks.append(Blank(f"cheek_center{sfx}_{j}", 1, mat18, BIRCH_DENSITY,
                                    pos=(x, fr.y_bf, fr.z0), size=(DIVIDER_MM, L, s_h),
                                    blank_mm=_blank_dims(DIVIDER_MM, L, s_h), chamber=c,
                                    notes="center cheek between the two slots, in line with the brace"))
                x += DIVIDER_MM
    return slots, blanks, blockers


def handle_hardware(spec: CabSpec, fr: Frame, com: tuple) -> tuple:
    """(hardware, features by panel, warnings). Strap: screw pair on the top
    at the loaded center of mass. Recessed side handles: one per side at the
    depth center of mass, upper third, between the cleats."""
    a = spec.aesthetics
    xm, ym, zm = com
    hardware, features, warnings = [], {}, []
    allow = a.corner_allowance_mm
    if a.handle == "strap":
        y_h = min(max(ym, allow), fr.D - allow)
        half = a.handle_screw_spacing_mm / 2.0
        if abs(xm) + half > fr.W / 2.0 - allow:
            warnings.append("strap handle screws fall inside the corner allowance; shorten the spacing")
        hardware.append(Hardware("strap handle", (xm, y_h, fr.H), None, "top",
                                 f"screw pair {a.handle_screw_spacing_mm:g} mm apart on the width axis, "
                                 "centered on the loaded center of mass, T-nuts inside"))
        return hardware, features, warnings
    w, h = a.recessed_handle_cutout_mm
    y_lo = fr.y_bb + CLEAT_MM + CLEARANCE_MM + w / 2.0
    y_hi = fr.D - BACK_MM - CLEAT_MM - CLEARANCE_MM - w / 2.0
    z_h = fr.z0 + (fr.z1 - fr.z0) * 2.0 / 3.0
    z_lo = fr.z0 + CLEAT_MM + CLEARANCE_MM + h / 2.0
    z_hi = fr.z1 - CLEAT_MM - CLEARANCE_MM - h / 2.0
    if y_lo > y_hi or z_lo > z_hi:
        warnings.append("recessed handle does not fit between the baffle and back cleats; use a strap handle")
        y_h = (y_lo + y_hi) / 2.0
    else:
        y_h = min(max(ym, y_lo), y_hi)
    z_h = min(max(z_h, z_lo), z_hi) if z_lo <= z_hi else z_h
    for side, x_c, panel in (("left", -fr.W / 2.0, "side_left"), ("right", fr.W / 2.0, "side_right")):
        hardware.append(Hardware("recessed handle", (x_c, y_h, z_h), (w, h), panel,
                                 f"recessed side handle, cutout {w:g} x {h:g} mm, at the depth center of mass"))
        features[panel] = [{"type": "rect_hole", "axis": "x", "center": (y_h, z_h), "w": w, "h": h}]
    return hardware, features, warnings


def trim_hardware(spec: CabSpec, fr: Frame) -> list:
    a = spec.aesthetics
    out = []
    if a.feet == "rubber":
        inset = a.foot_inset_mm + a.foot_diameter_mm / 2.0
        for sx in (-1.0, 1.0):
            for y in (inset, fr.D - inset):
                out.append(Hardware("foot", (sx * (fr.W / 2.0 - inset), y, 0.0), None, "bottom",
                                    f"rubber foot {a.foot_diameter_mm:g} mm, one central screw"))
    else:
        for sx in (-1.0, 1.0):
            out.append(Hardware("tilt-back leg", (sx * fr.W / 2.0, 100.0, 100.0), None,
                                "side_left" if sx < 0 else "side_right",
                                "tilt-back leg pivot screws 100 mm from the front and bottom edges; "
                                "legs not modeled"))
    corners = a.corners if a.corners is not None else ("black" if spec.line == "tolex" else "none")
    if corners != "none":
        for sx in (-1.0, 1.0):
            for y in (0.0, fr.D):
                for z in (0.0, fr.H):
                    out.append(Hardware("corner", (sx * fr.W / 2.0, y, z), None, "",
                                        f"metal corner, {corners}; keep-out {a.corner_allowance_mm:g} mm "
                                        "for every cutout"))
    if a.piping:
        out.append(Hardware("piping", (0.0, 0.0, fr.H / 2.0), None, "",
                            "piping glued into the corner between grill frame and shell"))
    out.append(Hardware("grill cloth", (0.0, GRILL_FRONT_MM, fr.H / 2.0), None, "grill frame",
                        a.grill_cloth or "grill cloth not chosen"))
    return out


# === TASK 7 ===
def _clip(box, cb):
    """Intersection of two ((x0,y0,z0),(x1,y1,z1)) boxes, or None."""
    lo = tuple(max(a, b) for a, b in zip(box[0], cb[0]))
    hi = tuple(min(a, b) for a, b in zip(box[1], cb[1]))
    if any(h - l <= 0 for l, h in zip(lo, hi)):
        return None
    return (lo, hi)


def _vol(box) -> float:
    if box is None:
        return 0.0
    return math.prod(h - l for l, h in zip(box[0], box[1]))


def _poly_area(poly) -> float:
    s = 0.0
    for i in range(len(poly)):
        y0, z0 = poly[i]
        y1, z1 = poly[(i + 1) % len(poly)]
        s += y0 * z1 - y1 * z0
    return abs(s) / 2.0


def feature_volume_mm3(blank: Blank, feat: dict, clip_to=None) -> float:
    """Material a feature removes from a box blank (clipped to a box when given)."""
    box = blank.box if clip_to is None else _clip(blank.box, clip_to)
    if box is None:
        return 0.0
    dx, dy, dz = (h - l for l, h in zip(box[0], box[1]))
    kind = feat["type"]
    if kind == "edge_cuts":
        x0, x1 = feat["x"]
        return sum(_poly_area(p) for p in feat["polys"]) * (x1 - x0)
    if kind == "cutout":
        return math.pi / 4.0 * feat["d"] ** 2 * dy
    if kind == "holes":
        return len(feat["centers"]) * math.pi / 4.0 * feat["d"] ** 2 * dy
    if kind == "rect_hole":
        return feat["w"] * feat["h"] * (dy if feat["axis"] == "y" else dx)
    if kind == "notch":
        return _vol(_clip(feat["box"], box))
    return 0.0


def blank_volume_mm3(blank: Blank, clip_to=None) -> float:
    """Solid volume of a blank after its features, optionally clipped to a box."""
    if blank.shape == "box":
        box = blank.box if clip_to is None else _clip(blank.box, clip_to)
        if box is None:
            return 0.0
        return _vol(box) - sum(feature_volume_mm3(blank, f, clip_to) for f in blank.features)
    cx, y0, cz = blank.pos
    od, length, id_mm = blank.size
    ya, yb = y0, y0 + length
    if clip_to is not None:
        ya, yb = max(ya, clip_to[0][1]), min(yb, clip_to[1][1])
        if yb <= ya:
            return 0.0
    return math.pi / 4.0 * (od ** 2 - id_mm ** 2) * (yb - ya)


def chamber_volumes(spec: CabSpec, fr: Frame, parts: list, rports: list, slots: list) -> list:
    out = []
    for c, (xa, xb) in enumerate(fr.chambers):
        cb = ((xa, fr.y_bb, fr.z0), (xb, fr.y_bi, fr.z1))
        gross = _vol(cb)
        inside = sum(blank_volume_mm3(p, cb) for p in parts if p.chamber == c)
        port_air, air = [], 0.0
        for s in slots:
            if s.chamber != c:
                continue
            box = ((s.x0, fr.y_bf, fr.z0), (s.x1, fr.y_bf + s.shelf_depth_mm, fr.z0 + s.slot_h_mm))
            port_air.append({"type": "box", "box": box})
            air += _vol(_clip(box, cb))
        for rp in rports:
            if rp.chamber != c:
                continue
            y0, y1 = max(rp.y0, fr.y_bb), fr.y_bi
            port_air.append({"type": "cylinder", "center": rp.center, "d": rp.id_mm, "y": (y0, y1)})
            air += math.pi / 4.0 * rp.id_mm ** 2 * max(0.0, y1 - y0)
        disp = sum(spec.speakers[i].displacement_l for i in range(spec.driver_count)
                   if _chamber_of(fr, _cutout_x(spec, fr, i)) == c)
        net = (gross - inside - air) / 1e6 - disp
        out.append(Chamber(c, cb, port_air, gross / 1e6, net, disp, spec.per_chamber_net_l))
    return out


def _cutout_x(spec: CabSpec, fr: Frame, i: int) -> float:
    return cutout_centers(spec, fr)[i][0]


def mass_and_com(spec: CabSpec, fr: Frame, parts: list, cutouts: list) -> tuple:
    """(mass dict, center of mass): blank volumes times density, speakers at
    the baffle at the cutout centers, 1 kg of hardware at the cab center."""
    total, mx, my, mz = 0.0, 0.0, 0.0, 0.0
    parts_kg = 0.0
    for p in parts:
        m = blank_volume_mm3(p) * p.density / 1e9
        (x0, y0, z0), (x1, y1, z1) = p.box
        cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
        parts_kg += m
        total += m
        mx, my, mz = mx + m * cx, my + m * cy, mz + m * cz
    speakers_kg = 0.0
    for co in cutouts:
        m = spec.speakers[co.speaker].weight_kg
        speakers_kg += m
        total += m
        mx += m * co.center[0]
        my += m * (fr.y_bf + BAFFLE_MM / 2.0)
        mz += m * co.center[1]
    total += HARDWARE_KG
    my += HARDWARE_KG * fr.D / 2.0
    mz += HARDWARE_KG * fr.H / 2.0
    com = (mx / total, my / total, mz / total)
    return {"parts": parts_kg, "speakers": speakers_kg, "hardware": HARDWARE_KG, "total": total}, com


def tolex_yardage(spec: CabSpec) -> dict | None:
    if spec.line != "tolex":
        return None
    W, H, D = spec.external_mm
    area = 2.0 * (W * H + W * D + H * D) / 1e6
    roll = ROLL_MM[spec.aesthetics.tolex_roll_in] / 1e3
    length = area * TOLEX_WASTE / roll
    return {"roll_in": spec.aesthetics.tolex_roll_in, "area_m2": area,
            "length_m": length, "length_yd": length / YARD_M}


def layout(spec: CabSpec) -> Layout:
    fr = frame(spec)
    parts = shell_blanks(spec)
    baffle, cutouts, dados = baffle_and_cutouts(spec, fr)
    for name, feat in dados.items():
        _attach(parts, name, [feat])
    parts.append(baffle)
    parts += cleat_blanks(spec, fr)
    parts += grill_frame_blanks(spec, fr)
    parts += brace_blank(spec, fr)
    parts += divider_blank(spec, fr)
    stiff, span_notes = stiffener_blanks(spec, fr)
    parts += stiff
    parts += back_blanks(spec, fr)
    envelopes = speaker_envelopes(spec, fr, cutouts)
    plates, plate_feats, plate_warn = jack_plates(spec, fr)
    for panel, feats in plate_feats.items():
        _attach(parts, panel, feats)
    slots, slot_blanks, slot_blockers = slot_ports(spec, fr)
    parts += slot_blanks
    obstacles = [p.box for p in parts
                 if p.shape == "box" and (p.chamber is not None or p.name == "divider")]
    for hw in plates:
        w, h = hw.cutout
        x, _, z = hw.position
        obstacles.append(((x - w / 2, fr.D - 40.0, z - h / 2), (x + w / 2, fr.D, z + h / 2)))
    rports, port_blanks, back_feats, port_blockers = round_ports(spec, fr, envelopes, obstacles)
    parts += port_blanks
    if back_feats:
        _attach(parts, "back", back_feats)
    chambers = chamber_volumes(spec, fr, parts, rports, slots)
    mass, com = mass_and_com(spec, fr, parts, cutouts)
    handles, handle_feats, handle_warn = handle_hardware(spec, fr, com)
    for panel, feats in handle_feats.items():
        _attach(parts, panel, feats)
    hardware = plates + handles + trim_hardware(spec, fr)
    tolex = tolex_yardage(spec)
    if tolex is not None:
        hardware.append(Hardware("tolex", (0.0, fr.D / 2.0, fr.H / 2.0), None, "",
                                 f"{spec.aesthetics.tolex_color or 'tolex color not chosen'}, "
                                 f"{tolex['roll_in']} in roll: {tolex['length_m']:.2f} m "
                                 f"({tolex['length_yd']:.2f} yd), six faces x 1.15"))
    notes = ([f"blocker: {b}" for b in slot_blockers + port_blockers]
             + [f"warn: {w}" for w in plate_warn + handle_warn]
             + [f"span: {s}" for s in span_notes])
    return Layout(spec=spec, parts=parts, cutouts=cutouts, round_ports=rports, slot_ports=slots,
                  hardware=hardware, envelopes=envelopes, chambers=chambers,
                  gross_l=sum(ch.gross_l for ch in chambers), net_l=[ch.net_l for ch in chambers],
                  mass_kg=mass, com_mm=com, tolex=tolex, part_count=len(parts), notes=notes)


def layout_inside_parts_l(lay: Layout) -> float:
    """Cleats, stiffeners, shelf, cheeks, brace, tube and ring inside the air
    boxes: gross minus net minus displacement minus port air, all chambers."""
    total = 0.0
    for ch in lay.chambers:
        air = 0.0
        for pa in ch.port_air:
            if pa["type"] == "box":
                air += _vol(_clip(pa["box"], ch.box))
            else:
                y0, y1 = pa["y"]
                air += math.pi / 4.0 * pa["d"] ** 2 * max(0.0, y1 - y0)
        total += ch.gross_l - ch.net_l - ch.displacement_l - air / 1e6
    return total


def _stock_fits(blank: Blank, spec: CabSpec) -> bool:
    if blank.shape != "box":
        return True
    t, w, l = blank.blank_mm
    limit = STOCK_HARDWOOD_MM if (spec.line == "hardwood" and "birch" not in blank.material
                                  and "PVC" not in blank.material) else STOCK_SHEET_MM
    long_, short = max(limit), min(limit)
    a, b = max(w, l), min(w, l)
    return a <= long_ + 1e-6 and b <= short + 1e-6


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
                        "; ".join(problems) if problems else "strip inner edges clear every cutout by 2 mm"))
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
    checks.append(Check("jack plate", "warn" if plate_warn else "pass",
                        "; ".join(plate_warn) if plate_warn else "plates fit above the cleat"))
    # stock
    over = [p.name for p in lay.parts if not _stock_fits(p, spec)]
    checks.append(Check("stock", "warn" if over else "pass",
                        "over stock: " + ", ".join(over) if over else "every blank fits the stock limits"))
    checks.append(Check("part count", "pass", f"{lay.part_count} parts"))
    spans = [n[len("span: "):] for n in lay.notes if n.startswith("span: ")]
    checks.append(Check("spans", "warn" if spans else "pass",
                        "; ".join(spans) if spans else f"no panel span over {SPAN_MAX_MM:.0f} mm"))
    return checks


def layout_report(lay: Layout, checks: list) -> dict:
    spec = lay.spec
    fr = frame(spec)
    W, H, D = spec.external_mm
    return {
        "name": spec.name,
        "generated": date.today().isoformat(),
        "line": spec.line, "species": spec.species,
        "corner_joint": spec.aesthetics.corner_joint,
        "baffle_mount": spec.aesthetics.baffle_mount,
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
    }
