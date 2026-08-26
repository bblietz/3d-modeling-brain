"""Flatten X2D 0.4-nozzle presets for the Bambu CLI (sharks nametag)."""
import json
import os
import sys

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")


def load(kind, name):
    with open(os.path.join(ROOT, kind, name + ".json")) as f:
        return json.load(f)


def flatten(kind, name):
    chain = [load(kind, name)]
    while "inherits" in chain[-1]:
        chain.append(load(kind, chain[-1]["inherits"]))
    merged = {}
    for layer in reversed(chain):
        merged.update(layer)
    merged.pop("inherits", None)
    merged["name"] = name
    return merged


# smooth ironed top, adjusted for the 0.4 nozzle (line width 0.42, not 0.55)
SMOOTH_TOP = {
    # Top-surface recipe = coupon C (2026-08-22, Brian's coupon plate
    # photo, IMG_1527): no ironing, TWO top walls, top_surface_speed 60.
    # The PLA-era ironing package (top / zig-zag / 10% / 0.15 / 30 at
    # top speed 120) pitted the white letter tops and scuffed the cyan on
    # PETG (print 6); the PETG-tuned ironing coupon B (15% / 20 / 0.1)
    # still smeared. Coupon A (no ironing, 1 top wall) showed fill lines
    # to the edge; C's extra top loop hides the fill ends.
    "ironing_type": "no ironing",
    "top_one_wall_type": "not apply",   # 2 walls on every top surface
    # Solid-text package (2026-08-23, coupon O/P/Q/R print + offline toolpath
    # sweep): the white letter marks were (a) loop start/stop defects, fixed
    # by closing the seam gap and slowing small loops/gap fill (print: Q
    # clearly better than O, R's +3% flow made strings/fuzz, dropped), and
    # (b) geometric arachne voids at junctions/dot centers, halved by
    # letting arachne place beads down to 50%/features to 10% of line width
    # (visible-void metric 1.92 -> 0.97 mm2; walls 0.30 would cut to 0.72
    # but is unproven bead quality - the 0.2 nozzle is the true zero-hole
    # path if ever needed).
    "seam_gap": "0%",
    "small_perimeter_speed": ["30", "30", "30", "30"],
    "small_perimeter_threshold": ["10", "10", "10", "10"],
    "gap_infill_speed": ["40", "40", "40", "40"],
    "wall_distribution_count": "3",
    "wall_transition_filter_deviation": "50%",
    "min_feature_size": "10%",
    "min_bead_width": "50%",
    "prime_tower_brim_width": "5",   # 2026-08-24: the brimless tower peeled at the plate corner on the 0.2 coupon (0.1 mm first layer, 0.25 mm lines); a 5 mm brim anchors it everywhere
    # 2026-08-25 anti-peel: the ribbed tower with rounded corners (Studio
    # 2.08 defaults, so no toolpath change) is pinned here and in the diff
    # list so Studio cannot reset it to a plain square tower
    "prime_tower_rib_wall": "1",
    "prime_tower_fillet_wall": "1",
    "top_surface_line_width": "0.42",
    "top_shell_layers": "5",
    "top_surface_speed": ["60", "60", "60", "60"],
    "sparse_infill_density": "50%",    # was 100% "solid tag" (Brian
    # 2026-08-06); dropped to 50% after the 2026-08-07 bed peel to cut
    # shrinkage stress (Brian 2026-08-07)
    # First-layer fixes after prints 4 and 5 (2026-08-20): the job's very
    # first extrusion was the M of MAX (un-primed nozzle after a 1000 mm/s
    # travel, thinnest arachne bead of the layer) and it went to spaghetti
    # both times. A 2-loop skirt primes and wipes before any letter; the
    # slower first layer helps the small PETG islands bond.
    "skirt_loops": "2",
    "skirt_distance": "3",
    "skirt_height": "1",
    "initial_layer_speed": ["30", "30", "30", "30"],
    "initial_layer_infill_speed": ["50", "50", "50", "50"],
    "wall_generator": "arachne",  # v3.23 (Brian 2026-08-20, hairline ball
    # seams): arachne prints single variable-width beads down to ~0.45 mm,
    # so the 0.6 mm seams, banner border, CITY ring and the raised YSC bars
    # all print; the stock classic generator silently dropped them
    "sparse_infill_pattern": "zig-zag",  # Bambu's serialized name for
    # Rectilinear ("rectilinear" is NOT a valid enum and silently falls
    # back to cubic; the preset's gyroid was invalid at 100%)
}

out = sys.argv[1]
for kind, name, fname in [
    ("machine", "Bambu Lab X2D 0.4 nozzle", "flat-machine.json"),
    ("process", "0.12mm High Quality @BBL X2D", "flat-process.json"),
    # PETG Basic since 2026-08-08 (Brian ordered PETG); was Bambu PLA Basic
    ("filament", "Bambu PETG Basic @BBL X2D 0.4 nozzle", "flat-filament.json"),
]:
    merged = flatten(kind, name)
    if kind == "process":
        merged.update(SMOOTH_TOP)
    with open(os.path.join(out, fname), "w") as f:
        json.dump(merged, f, indent=1)
    print(fname, "<-", name, "| layer_height:", merged.get("layer_height"),
          "| nozzle:", merged.get("nozzle_diameter"), "| ironing:", merged.get("ironing_type"))
