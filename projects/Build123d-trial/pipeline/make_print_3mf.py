#!/usr/bin/env python3
"""Build the print-ready project 3MF for the Build123d-trial project box.

project_box.py exports geometry only (box.stl, lid.stl, project-box.3mf).
This turns that geometry into a file that carries the X2D presets, the bed
type and temperatures, the PLA smooth-top ironing package and a Manual
filament map, so nothing depends on remembering to set them in the GUI.

    .venv/bin/python projects/Build123d-trial/pipeline/make_print_3mf.py

Idempotent: re-running rebuilds the output from the STLs and the settings
template, never from its own previous output.

Why it is built this way
------------------------
- Geometry comes from the Bambu Studio CLI (`--export-3mf`), which writes
  the plate model_instance entries a project 3MF needs.
- Settings do NOT come from scripts/flatten_presets.py. That script still
  reads the stale 02.07.00.08 preset bundle and never merges the machine
  preset's `include` gcode templates. Instead the settings template
  x2d-pla-0.6-settings.json is the project_settings.config Bambu Studio
  02.08.02.61 itself wrote for this project, so every resolved value and
  every GUI-only extruder key is real. This script patches that template.
- Any key changed inside a project 3MF must ALSO be listed in
  different_settings_to_system or the GUI silently resets it to the named
  system preset on open. The list is positional:
  [0] = process, [1..N] = the N filaments, [N+1] = machine. Bed temps are
  filament-scope, so they go in slot 1, not slot 0. This is the trap that
  scripts/apply_smooth_top.py does not cover: it only handles slot 0.

Verification
------------
The checks at the bottom re-open the finished file and assert every patch
landed. They are not a substitute for opening it in Bambu Studio: a
hand-patched 3MF has passed a CLI round trip and still rendered EMPTY in
the GUI, so a GUI open is the mandatory ground truth. CLI slicing is not
available as a check either - it only succeeds on Studio-SAVED projects,
and fails on CLI-composed ones with "No valid nozzle found".
"""
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
BAMBU = Path.home() / ".local/bin/bambu-studio"
TEMPLATE = Path(__file__).parent / "x2d-pla-0.6-settings.json"
OUTPUT = PROJECT / "project-box-print.3mf"
PARTS = {"box.stl": "Box", "lid.stl": "Lid"}

CFG = "Metadata/project_settings.config"
MODEL_CFG = "Metadata/model_settings.config"
MODEL = "3D/3dmodel.model"
NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
BED = 256.0  # X2D build plate, single nozzle

# --- process scope: the PLA smooth-top package (knowledge/smooth-surfaces-x2d.md)
# These are 0.6-nozzle numbers. The 2026-08-22 "do not iron" finding is scoped
# to PETG with small raised top art; a flat PLA lid top still wants ironing.
PROCESS = {
    "ironing_type": "top",
    "ironing_pattern": "zig-zag",
    "ironing_flow": "10%",
    "ironing_spacing": "0.15",
    "ironing_speed": "30",
    "top_surface_line_width": "0.55",
    "top_shell_layers": "5",
}
PROCESS_LIST = {"top_surface_speed": "120"}  # per-extruder lists

# --- filament scope: bed temperature
# The flattened X2D preset carries 55 C for the textured plate. Bambu stock
# PLA on textured PEI wants 65 C; 55 is ~10 C of lost adhesion margin, and
# the Cool Plate / 35 C version of this same bug peeled a Sharks print off
# the bed mid-print on 2026-08-07.
FILAMENT_LIST = {
    "textured_plate_temp": "65",
    "textured_plate_temp_initial_layer": "65",
}

# --- plate scope
# CLI exports leave the filament map on "Auto For Flush". On the dual-nozzle
# X2D profile that lets the GUI route a colour to the Bowden support nozzle.
BED_TYPE = "Textured PEI Plate"
MAP_MODE = "Manual"


def compose_geometry(workdir):
    """Lay the two STLs out on one plate with the Studio CLI."""
    assert BAMBU.exists(), f"bambu-studio CLI not found at {BAMBU}"
    for stl in PARTS:
        assert (PROJECT / stl).exists(), f"missing {stl}; run project_box.py first"
        shutil.copy(PROJECT / stl, workdir / stl)
    # --export-3mf takes a BARE filename when --outputdir is set; an absolute
    # path makes it exit 243 and write nothing.
    subprocess.run(
        [str(BAMBU), "--export-3mf", "compose.3mf", "--outputdir", str(workdir),
         "--arrange", "1", *[str(workdir / stl) for stl in PARTS]],
        check=True, capture_output=True, text=True,
    )
    out = workdir / "compose.3mf"
    assert out.exists(), "CLI produced no 3MF"
    return out


def patch_settings(cfg):
    """Apply the print profile to a project_settings.config dict, in place."""
    n_filaments = len(cfg["filament_settings_id"])

    cfg.update(PROCESS)
    for key, value in PROCESS_LIST.items():
        cfg[key] = [value] * len(cfg[key])
    for key, value in FILAMENT_LIST.items():
        cfg[key] = [value] * len(cfg[key])
    cfg["curr_bed_type"] = BED_TYPE
    cfg["filament_map_mode"] = MAP_MODE

    # different_settings_to_system, or the GUI resets all of the above
    slots = cfg.get("different_settings_to_system") or []
    slots += [""] * (n_filaments + 2 - len(slots))

    def merge(slot, keys):
        have = [k for k in slots[slot].split(";") if k]
        return ";".join(have + [k for k in keys if k not in have])

    slots[0] = merge(0, list(PROCESS) + list(PROCESS_LIST))
    for i in range(1, n_filaments + 1):
        slots[i] = merge(i, list(FILAMENT_LIST))
    cfg["different_settings_to_system"] = slots
    return cfg


def patch_model_settings(text):
    """Friendly object names, and Manual filament map on the plate."""
    for stl, friendly in PARTS.items():
        text = text.replace(f'value="{stl}"', f'value="{friendly}"')
    return text.replace(
        'key="filament_map_mode" value="Auto For Flush"',
        f'key="filament_map_mode" value="{MAP_MODE}"',
    )


def center_on_plate(text):
    """Move the arranged group to the middle of the bed.

    The CLI's --arrange packs the parts against one side of the plate. Centring
    the group keeps both parts away from the plate edges; a CLI compose without
    --arrange is worse still, leaving the build item at the identity transform,
    which puts the part on the plate's front-left corner, three quarters off
    the bed.
    """
    root = ET.fromstring(text)
    items = root.findall(".//m:build/m:item", NS)
    xs, ys = [], []
    for item in items:
        t = item.get("transform").split()
        xs.append(float(t[9]))
        ys.append(float(t[10]))
    dx = BED / 2 - (min(xs) + max(xs)) / 2
    dy = BED / 2 - (min(ys) + max(ys)) / 2
    for item in items:
        t = item.get("transform").split()
        t[9] = f"{float(t[9]) + dx:.5f}"
        t[10] = f"{float(t[10]) + dy:.5f}"
        item.set("transform", " ".join(t))
    ET.register_namespace("", NS["m"])
    for prefix, uri in (
        ("BambuStudio", "http://schemas.bambulab.com/package/2021"),
        ("p", "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"),
    ):
        ET.register_namespace(prefix, uri)
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def build(workdir):
    composed = compose_geometry(workdir)
    cfg = patch_settings(json.loads(TEMPLATE.read_text()))

    with zipfile.ZipFile(composed) as zin, zipfile.ZipFile(
        OUTPUT, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == CFG:
                data = json.dumps(cfg, indent=4).encode()
            elif item.filename == MODEL_CFG:
                data = patch_model_settings(data.decode()).encode()
            elif item.filename == MODEL:
                data = center_on_plate(data.decode()).encode()
            zout.writestr(item.filename, data)


def verify():
    """Re-open the finished file and assert every patch survived the write."""
    with zipfile.ZipFile(OUTPUT) as zf:
        cfg = json.loads(zf.read(CFG))
        model_cfg = zf.read(MODEL_CFG).decode()
        root = ET.fromstring(zf.read(MODEL))

    for key, want in PROCESS.items():
        assert cfg[key] == want, f"{key} = {cfg[key]!r}, expected {want!r}"
    for key, want in {**PROCESS_LIST, **FILAMENT_LIST}.items():
        assert set(cfg[key]) == {want}, f"{key} = {cfg[key]!r}, expected all {want!r}"
    assert cfg["curr_bed_type"] == BED_TYPE, cfg["curr_bed_type"]
    assert cfg["filament_map_mode"] == MAP_MODE, cfg["filament_map_mode"]

    # The patched keys must be declared in the right scope slot or the GUI
    # silently reverts them, and a CLI round trip cannot catch that.
    slots = cfg["different_settings_to_system"]
    n_filaments = len(cfg["filament_settings_id"])
    assert len(slots) == n_filaments + 2, f"diff list has {len(slots)} slots"
    process_declared = set(slots[0].split(";"))
    for key in list(PROCESS) + list(PROCESS_LIST):
        assert key in process_declared, f"{key} missing from process diff slot"
    for i in range(1, n_filaments + 1):
        declared = set(slots[i].split(";"))
        for key in FILAMENT_LIST:
            assert key in declared, f"{key} missing from filament diff slot {i}"

    # Nozzle: the settings template and the design must agree, and the parts
    # must be nowhere near the plate edges.
    assert cfg["printer_variant"] == "0.6", cfg["printer_variant"]
    assert set(cfg["nozzle_diameter"]) == {"0.6"}, cfg["nozzle_diameter"]

    for friendly in PARTS.values():
        assert f'value="{friendly}"' in model_cfg, f"object {friendly} not named"
    assert model_cfg.count("<model_instance>") == len(PARTS), "plate instance count"

    items = root.findall(".//m:build/m:item", NS)
    assert len(items) == len(PARTS), f"{len(items)} build items"
    placements = []
    for item in items:
        t = item.get("transform").split()
        x, y = float(t[9]), float(t[10])
        assert 20 < x < BED - 20 and 20 < y < BED - 20, f"item at ({x}, {y})"
        placements.append((x, y))

    print(f"built {OUTPUT.relative_to(PROJECT.parent.parent)}")
    print(f"  {cfg['printer_settings_id']} | {cfg['print_settings_id']}")
    print(f"  {cfg['filament_settings_id'][0]}")
    print(f"  bed {cfg['curr_bed_type']} at {cfg['textured_plate_temp'][0]} C "
          f"(first layer {cfg['textured_plate_temp_initial_layer'][0]} C)")
    print(f"  ironing {cfg['ironing_type']} / {cfg['ironing_pattern']}, "
          f"flow {cfg['ironing_flow']}, spacing {cfg['ironing_spacing']} mm, "
          f"{cfg['top_shell_layers']} top shells")
    print(f"  filament map {cfg['filament_map_mode']} {cfg['filament_map']}")
    print(f"  parts at {', '.join(f'({x:.1f}, {y:.1f})' for x, y in placements)}")
    print()
    print("NOT yet verified - open it in Bambu Studio and check the plate "
          "renders both parts before printing. Select the 0.6 nozzle printer "
          "preset BEFORE opening, and swap the resident 0.2 nozzle.")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        build(Path(tmp))
    verify()
    sys.exit(0)
