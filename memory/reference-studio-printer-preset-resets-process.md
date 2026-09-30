---
name: reference-studio-printer-preset-resets-process
description: In Bambu Studio, selecting a printer preset on an open project 3MF resets the process preset to that printer's default and silently drops tuned process settings
metadata:
  type: reference
---

Selecting (or re-selecting) the printer preset in the Bambu Studio GUI on an open project 3MF resets the process preset to the printer's default (for the X2D 0.4 nozzle: `0.20mm Standard @BBL X2D`). Every tuned process key goes with it: layer height, shells, speeds, recipe keys. Seen 2026-09-29 on Logodude: I told Brian to "select the 0.4 nozzle preset first", and his GUI save came back at 0.2 mm layers with the lettering recipe gone. He did not change it on purpose.

**How to apply:** the project 3MF already carries the machine and nozzle, so never tell Brian to select a printer preset on a pipeline-built file. Tell him to keep the project's settings if Studio offers to switch, and to check that the process name still reads what the pipeline wrote. When a GUI-saved file comes back, diff `print_settings_id` and `layer_height` against the committed file before editing on top of it. Related: [[reference-x2d-preset-includes]], [[feedback-raised-letters-recipe]], [[project-logodude]].
