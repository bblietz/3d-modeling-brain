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
