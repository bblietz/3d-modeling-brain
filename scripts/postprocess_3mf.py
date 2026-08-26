"""Post-process a Bambu Studio project 3MF.

Sets filament_colour in Metadata/project_settings.config and replaces STL
filenames with friendly object names in Metadata/model_settings.config.

Usage:
  postprocess_3mf.py <path.3mf> <colors> <stl=name> [<stl=name> ...]

  <colors>     comma-separated hex colors for filaments 1..N, e.g.
               "#D32F2F,#F2F2F2,#555555"
  <stl=name>   mapping from STL filename to friendly name, e.g.
               "pad.stl=Pad" "bell_1.stl=Bell 1"
"""
import json, re, shutil, sys, zipfile, os

path = sys.argv[1]
colors = sys.argv[2].split(",")
names = dict(arg.split("=", 1) for arg in sys.argv[3:])
tmp = path + ".tmp"

with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "Metadata/project_settings.config":
            cfg = json.loads(data)
            cfg["filament_colour"] = colors
            print("layer_height:", cfg.get("layer_height"))
            print("nozzle_diameter:", cfg.get("nozzle_diameter"))
            data = json.dumps(cfg, indent=4).encode()
        elif item.filename == "Metadata/model_settings.config":
            text = data.decode()
            for stl, friendly in names.items():
                text = text.replace(stl, friendly)
            print("extruders in model_settings:",
                  re.findall(r'key="extruder" value="(\d+)"', text))
            data = text.encode()
        zout.writestr(item, data)

shutil.move(tmp, path)
print("post-processed:", os.path.getsize(path), "bytes")
