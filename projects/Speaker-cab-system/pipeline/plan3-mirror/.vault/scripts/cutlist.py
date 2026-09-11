"""Cut list generation for furniture models (see skills/furniture).

Measures each part's stock blank from its geometry (build123d) and writes
a markdown cut list, optionally CSV. Import from the end of a model file:

    import sys
    sys.path.insert(0, "/home/brian/ClaudeProjects/3d-modeling-brain/scripts")
    from cutlist import write_cut_list

    PARTS = [
        {"name": "side", "solid": side, "qty": 2, "material": "18mm birch ply"},
        {"name": "shelf", "solid": shelf, "qty": 3, "material": "18mm birch ply",
         "length_axis": "X",          # optional: force the length/grain axis
         "notes": "adjustable"},      # optional free text
        {"name": "leg", "dims": (38, 38, 700), "qty": 4,
         "material": "2x2 pine"},     # explicit (t, w, l) mm, e.g. FreeCAD path
    ]
    write_cut_list(PARTS, ".../projects/<Name>/cutlist.md", title="Bookshelf")

Rows with identical rounded dims + material + notes merge into one line
(names joined with "/"); parts that differ only in machining stay apart. Parts whose solid volume is under RECT_RATIO_MIN of
their bounding-box volume get flagged as needing a drawing/template.
"""

import csv as _csv
from math import gcd

MM_PER_INCH = 25.4
RECT_RATIO_MIN = 0.98  # solid volume / bbox volume below this = not a plain blank


def inch_frac(mm, denom=16):
    """25.4 -> '1', 19 -> '3/4', 600 -> '23-5/8' (nearest 1/denom inch)."""
    total = round(mm / MM_PER_INCH * denom)
    whole, frac = divmod(total, denom)
    if frac == 0:
        return str(whole)
    g = gcd(frac, denom)
    frac_s = f"{frac // g}/{denom // g}"
    return f"{whole}-{frac_s}" if whole else frac_s


def _measure(entry):
    """Return (thickness, width, length, geometry_note) in mm for one entry."""
    if "dims" in entry:
        t, w, l = (float(d) for d in entry["dims"])
        return t, w, l, ""
    solid = entry["solid"]
    size = solid.bounding_box().size
    by_axis = {"X": size.X, "Y": size.Y, "Z": size.Z}
    if "length_axis" in entry:
        length = by_axis.pop(entry["length_axis"].upper())
        t, w = sorted(by_axis.values())
    else:
        t, w, length = sorted(by_axis.values())
    note = ""
    bbox_vol = size.X * size.Y * size.Z
    ratio = solid.volume / bbox_vol if bbox_vol > 0 else 1.0
    if ratio < RECT_RATIO_MIN:
        note = (f"not a plain rectangular blank ({ratio:.0%} of bounding box); "
                "needs a drawing or template")
    return t, w, length, note


def cut_list_rows(parts):
    """Measure all entries; merge rows with identical dims + material + notes."""
    merged = {}
    for entry in parts:
        t, w, l, geo_note = _measure(entry)
        notes = " ; ".join(n for n in (entry.get("notes", ""), geo_note) if n)
        key = (round(t, 1), round(w, 1), round(l, 1), entry.get("material", ""), notes)
        row = merged.get(key)
        if row:
            row["qty"] += entry.get("qty", 1)
            if entry["name"] not in row["name"].split("/"):
                row["name"] += "/" + entry["name"]
            if notes and notes not in row["notes"]:
                row["notes"] = " ; ".join(n for n in (row["notes"], notes) if n)
        else:
            merged[key] = {"name": entry["name"], "qty": entry.get("qty", 1),
                           "t": t, "w": w, "l": l,
                           "material": entry.get("material", ""), "notes": notes}
    return sorted(merged.values(), key=lambda r: (r["material"], -r["l"], -r["w"]))


def _fmt(mm):
    return f"{round(mm, 1):g}"


def write_cut_list(parts, md_path, csv_path=None, title="Cut list", extra_lines=None):
    """Write the cut list markdown (and optional CSV); return the rows.

    extra_lines: optional materials that are not cut parts (tolex yardage,
    grill cloth), each {"part", "qty", "unit", "material", "notes"}; they
    appear under "Materials not cut" in the markdown and as CSV rows with
    empty dimensions."""
    rows = cut_list_rows(parts)
    lines = ["---", "type: cutlist", f"project: {title}", "---", "",
             f"# Cut list - {title}", "",
             "| Qty | Part | T x W x L (mm) | T x W x L (in) | Material | Notes |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        mm = f"{_fmt(r['t'])} x {_fmt(r['w'])} x {_fmt(r['l'])}"
        inch = f"{inch_frac(r['t'])} x {inch_frac(r['w'])} x {inch_frac(r['l'])}"
        lines.append(f"| {r['qty']} | {r['name']} | {mm} | {inch} "
                     f"| {r['material']} | {r['notes']} |")
    lines += ["", "Inches rounded to the nearest 1/16.", "",
              "## Totals by material", ""]
    totals = {}
    for r in rows:
        mat = r["material"] or "(unspecified)"
        qty, area = totals.get(mat, (0, 0.0))
        totals[mat] = (qty + r["qty"], area + r["qty"] * r["w"] * r["l"] / 1e6)
    for mat, (qty, area) in sorted(totals.items()):
        unit = "part" if qty == 1 else "parts"
        lines.append(f"- {mat}: {qty} {unit}, {area:.2f} m2 face area "
                     "(no kerf/waste allowance)")
    if extra_lines:
        lines += ["", "## Materials not cut", ""]
        for x in extra_lines:
            lines.append(f"- {x['qty']:g} {x['unit']} {x['part']}: {x['material']}. {x['notes']}")
    with open(md_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    if csv_path:
        with open(csv_path, "w", newline="") as f:
            writer = _csv.writer(f)
            writer.writerow(["qty", "part", "thickness_mm", "width_mm",
                             "length_mm", "material", "notes"])
            for r in rows:
                writer.writerow([r["qty"], r["name"], _fmt(r["t"]), _fmt(r["w"]),
                                 _fmt(r["l"]), r["material"], r["notes"]])
            for x in extra_lines or ():
                writer.writerow([x["qty"], x["part"], "", "", "", x["material"], x["notes"]])
    return rows
