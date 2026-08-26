import json, os, sys

ROOT = os.path.expanduser("~/.config/BambuStudio/system/BBL")

def load(kind, name):
    path = os.path.join(ROOT, kind, name + ".json")
    with open(path) as f:
        return json.load(f)

def flatten(kind, name):
    chain = []
    cur = load(kind, name)
    chain.append(cur)
    while "inherits" in cur:
        cur = load(kind, cur["inherits"])
        chain.append(cur)
    merged = {}
    for layer in reversed(chain):  # base first, children override
        merged.update(layer)
    merged.pop("inherits", None)
    merged["name"] = name
    return merged

# Smooth-top defaults, always injected into process presets
# (decision + rationale: knowledge/smooth-surfaces-x2d.md)
SMOOTH_TOP_OVERRIDES = {
    "ironing_type": "top",
    "ironing_pattern": "zig-zag",
    "ironing_flow": "10%",
    "ironing_spacing": "0.15",
    "ironing_speed": "30",
    "top_surface_line_width": "0.55",
    "top_shell_layers": "5",
    "top_surface_speed": ["120", "120", "120", "120"],
}

out_dir = sys.argv[1]
presets = [
    ("machine", "Bambu Lab X2D 0.6 nozzle", "flat-machine.json"),
    ("process", "0.18mm Balanced Quality @BBL X2D 0.6 nozzle", "flat-process.json"),
    ("filament", "Bambu PLA Basic @BBL X2D", "flat-filament.json"),
]
for kind, name, fname in presets:
    merged = flatten(kind, name)
    if kind == "process":
        merged.update(SMOOTH_TOP_OVERRIDES)
    with open(os.path.join(out_dir, fname), "w") as f:
        json.dump(merged, f, indent=1)
    print(fname, "<-", name, "| layer_height:", merged.get("layer_height"),
          "| nozzle:", merged.get("nozzle_diameter"),
          "| ironing:", merged.get("ironing_type"))
