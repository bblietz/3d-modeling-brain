#!/usr/bin/env python3
"""Client share page for a speaker-cab order: an interactive 3D model.

Writes <order>/share/index.html, one self-contained page (three.js from jsDelivr,
everything else inline) from the order's cab.step (per-part labeled solids),
cab.json and voicing.json (facts through scripts/cabreport.py), the proposal's
designed_to_do slot, and the site's swatch photos.

    .venv/bin/python projects/Speaker-cab-system/pipeline/share-viewer/build_share.py projects/Cab-<...> [--customer NAME]
"""
import argparse
import base64
import datetime
import html
import io
import json
import re
import sys
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parents[3]
sys.path.insert(0, str(VAULT / "scripts"))
import cabreport  # noqa: E402

TEMPLATE = HERE / "viewer.html"
MATERIALS = Path.home() / "ClaudeProjects" / "MaximoCabs" / "public" / "materials"
STEP_MM = 0.05              # position quantum; int16 covers +/- 1638 mm
TOLERANCE_MM = 0.15
ANGULAR_RAD = 0.12
SHELL = ("top", "bottom", "side_left", "side_right")
WOOD_CROP_LEFT = 0.14      # the site walnut photo carries a pale sapwood strip along its left edge
# Brian's rule (2026-09-13): hardwood grain wraps around the box, left to right on
# the top and bottom (CAD x = 0) and vertical on the sides (CAD z = 2); never front to back.
GRAIN_AXIS = {"top": 0, "bottom": 0, "side_left": 2, "side_right": 2}


def mesh_payload(step_path: Path) -> dict:
    """Every labeled solid in the STEP as quantized int16 positions and indices in one base64 blob."""
    from build123d import import_step
    shape = import_step(str(step_path))
    parts, chunks, offset = [], [], 0

    def put(arr: array) -> int:
        nonlocal offset
        raw = arr.tobytes()
        raw += b"\0" * ((-len(raw)) % 4)        # typed-array views need 4-byte alignment
        chunks.append(raw)
        start, offset = offset, offset + len(raw)
        return start

    for solid in shape.children:
        verts, tris = solid.tessellate(TOLERANCE_MM, ANGULAR_RAD)
        pos = array("h")
        for v in verts:
            for c in (v.X, v.Y, v.Z):
                q = round(c / STEP_MM)
                if not -32768 <= q <= 32767:
                    raise ValueError(f"{solid.label}: coordinate {c:.1f} mm outside the int16 range")
                pos.append(q)
        wide = len(verts) > 65535
        idx = array("I" if wide else "H", [i for t in tris for i in t])
        bb = solid.bounding_box()
        parts.append({"name": solid.label, "vcount": len(verts), "icount": len(idx), "i32": wide,
                      "voff": put(pos), "ioff": put(idx),
                      "min": [round(bb.min.X, 2), round(bb.min.Y, 2), round(bb.min.Z, 2)],
                      "max": [round(bb.max.X, 2), round(bb.max.Y, 2), round(bb.max.Z, 2)]})
    return {"step": STEP_MM, "parts": parts, "data": base64.b64encode(b"".join(chunks)).decode("ascii")}


def jpeg_uri(path, max_side: int, quality: int, crop_left: float = 0.0) -> str:
    if path is None or not Path(path).exists():
        return ""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if crop_left:
        im = im.crop((round(im.width * crop_left), 0, im.width, im.height))
    im.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def swatch_path(name: str):
    rel = cabreport.SWATCHES.get((name or "").strip().lower())
    return MATERIALS / rel if rel else None


def edge_size(mm) -> str:
    """A roundover radius as the shop says it: an eighth-inch fraction when it is one, else millimetres."""
    eighths = mm / 25.4 * 8
    if abs(eighths - round(eighths)) < 0.02 and round(eighths) > 0:
        n, d = round(eighths), 8
        while n % 2 == 0 and d > 1:
            n, d = n // 2, d // 2
        whole, rem = divmod(n, d)
        return (f"{whole} " if whole else "") + (f"{rem}/{d}" if rem else "") + " in" if rem else f"{whole} in"
    return f"{mm:g} mm"


def slot(text: str, name: str) -> str:
    m = re.search(rf"<!-- slot: {name} -->\n(.*?)\n<!-- /slot -->", text, re.S)
    return m.group(1).strip() if m else ""


def build(order: Path, customer: str | None) -> Path:
    voicing = json.loads((order / "voicing.json").read_text())
    cab = json.loads((order / "cab.json").read_text())
    brief = (order / "brief.md").read_text() if (order / "brief.md").exists() else ""
    if not customer:
        m = re.search(r"^customer: (.+)$", brief, re.M)
        customer = m.group(1).strip() if m else "you"
    f = cabreport.facts(voicing, cab, customer)
    hardwood = cab["line"] == "hardwood"
    finish, config = f["finish"], f["configuration"]
    back_words = f["back_type"].replace("-back", " back")
    ohm = f["wiring"].split(",")[-1].strip()
    joint = "dovetail" if cab.get("corner_joint") == "dovetail" else "finger"
    today = datetime.date.today()
    proposal = (order / "proposal.md").read_text() if (order / "proposal.md").exists() else ""

    roundover = cab.get("aesthetics", {}).get("roundover_mm")
    edges = f", {edge_size(roundover)} roundover on every outside edge" if roundover else ""
    shell_text = (f"Solid {finish.lower()}, hand-cut {joint} joints{edges}, grain wrapping around the box"
                  if hardwood else f"Baltic birch covered in {finish}, hand-cut finger joints{edges}")
    rows = [("Speaker", f"{f['speaker_label']}, {ohm}"), ("Shell", shell_text), ("Grill cloth", f["grill_cloth"]),
            ("Hardware", ", ".join(h for h in f["hardware"].rstrip(".").split(", ") if not h.lower().startswith("no ")).capitalize()), ("Weight", f"About {f['mass_lb']} lb loaded ({f['mass_kg']} kg)"),
            ("Lead time", f["lead_time"])]
    spec_rows = "\n".join(f'          <dt class="label">{html.escape(k)}</dt><dd>{html.escape(v)}</dd>' for k, v in rows)

    crop = WOOD_CROP_LEFT if hardwood else 0.0
    finish_chip = jpeg_uri(swatch_path(finish), 160, 82, crop)
    cloth_chip = jpeg_uri(swatch_path(f["grill_cloth"]), 160, 82)
    figures = []
    for chip, name, role in ((finish_chip, finish, "Shell" if hardwood else "Covering"), (cloth_chip, f["grill_cloth"], "Grill cloth")):
        if chip:
            figures.append(f'        <figure><img src="{chip}" alt="{html.escape(name)} swatch" width="56" height="56">'
                           f'<figcaption><span class="label">{role}</span><span>{html.escape(name)}</span></figcaption></figure>')

    first = customer.split()[0]
    values = {
        "title": f"{first}'s {finish} {config}" if hardwood else f"{first}'s Tolex {config}",
        "prepared": f"Prepared for {customer} · {today:%B} {today.day}, {today.year}",
        "eyebrow": f"{f['line_label']} · {back_words}",
        "headline": f"Your {finish.lower()} {config}" if hardwood else f"Your {config} in {finish}",
        "size_in": f["external_in"].replace(" x ", " × "),
        "size_mm": f["external_mm"].replace(" x ", " × "),
        "back_view_label": "Open back" if cab["enclosure"]["type"] in ("open", "semi-open") else "Back",
        "designed": slot(proposal, "designed_to_do"),
        "model_note": ("A design model drawn from your cabinet's plans. The speaker and hardware are simplified"
                       + (f", and your {finish.lower()}'s figure will be its own." if hardwood else ".")
                       + " Every cabinet is built start-to-finish by one builder."),
        "status_line": f["status_line"],
    }
    raw = {
        "spec_rows": spec_rows,
        "finishes": "\n".join(figures),
        "grill_icon": f'<img src="{cloth_chip}" alt="" width="22" height="22">' if cloth_chip else "",
    }
    data = {
        "label": f"3D model of your {finish.lower() if hardwood else finish} {config} {back_words} speaker cabinet",
        "line": cab["line"],
        "grain": GRAIN_AXIS if hardwood else {},
        "shell": list(SHELL),
        "speakerCone": "hemp" if any(w in f["speaker_label"].lower() for w in ("hemp", "cannabis")) else "paper",
        "textures": {"shell": jpeg_uri(swatch_path(finish), 900, 84, crop), "cloth": jpeg_uri(swatch_path(f["grill_cloth"]), 512, 86)},
        "mesh": mesh_payload(order / "cab.step"),
    }

    page = TEMPLATE.read_text()
    for key, value in values.items():
        page = page.replace("{{" + key + "}}", html.escape(value).replace("\u00b7", "&middot;").replace("\u00d7", "&times;"))
    for key, value in raw.items():
        page = page.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{\w+\}\}", page)
    if leftover:
        raise ValueError(f"template placeholders with no value: {', '.join(sorted(set(leftover)))}")
    page = page.replace("/*__CAB_DATA__*/null", json.dumps(data, separators=(",", ":")))
    out = order / "share" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("order", type=Path, help="order directory holding cab.step, cab.json, voicing.json")
    ap.add_argument("--customer", help="customer name (default: the brief's frontmatter)")
    args = ap.parse_args(argv)
    for name in ("cab.step", "cab.json", "voicing.json"):
        if not (args.order / name).exists():
            print(f"input error: {args.order / name} not found")
            return 1
    out = build(args.order, args.customer)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
