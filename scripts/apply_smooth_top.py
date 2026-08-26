#!/usr/bin/env python3
"""Apply the smooth-top defaults to Bambu project 3MFs, in place. Idempotent.

Sets the 8 setting keys from knowledge/smooth-surfaces-x2d.md inside
Metadata/project_settings.config AND lists them in the process entry of
different_settings_to_system. Bambu Studio's GUI resolves an opened project
as "named system preset + diff list", so values not in the diff list are
silently reset to the system preset; patching values alone is not enough.

Usage: apply_smooth_top.py <file.3mf> [...]
"""
import json
import shutil
import sys
import zipfile

CFG = "Metadata/project_settings.config"
OVERRIDES = {
    "ironing_type": "top",
    "ironing_pattern": "zig-zag",
    "ironing_flow": "10%",
    "ironing_spacing": "0.15",
    "ironing_speed": "30",
    "top_surface_line_width": "0.55",
    "top_shell_layers": "5",
}
SPEED_KEY = "top_surface_speed"

for path in sys.argv[1:]:
    with zipfile.ZipFile(path) as zin:
        cfg = json.loads(zin.read(CFG))
        cfg.update(OVERRIDES)
        old_speed = cfg.get(SPEED_KEY)
        cfg[SPEED_KEY] = (
            ["120"] * len(old_speed) if isinstance(old_speed, list) else "120"
        )

        # Mark the keys as differing from the named system preset, or the
        # GUI resets them on open. Entry 0 of the list is the process preset.
        dsts = cfg.get("different_settings_to_system") or [""]
        listed = [k for k in dsts[0].split(";") if k]
        for key in list(OVERRIDES) + [SPEED_KEY]:
            if key not in listed:
                listed.append(key)
        dsts[0] = ";".join(listed)
        cfg["different_settings_to_system"] = dsts

        tmp = path + ".new"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == CFG:
                    data = json.dumps(cfg, indent=4).encode()
                zout.writestr(item, data)
    with zipfile.ZipFile(tmp) as zchk:
        patched = json.loads(zchk.read(CFG))
        assert patched["ironing_type"] == "top", path
        assert "ironing_type" in patched["different_settings_to_system"][0], path
    shutil.move(tmp, path)
    print(f"{path}: values set, diff list = {dsts[0]}")
