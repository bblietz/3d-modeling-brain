# FreeCAD 3D Model Generation System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up a system where Claude generates 3D models in FreeCAD via the neka-nat/freecad-mcp MCP server, iterating feature-by-feature with screenshot verification, and exports STL+3MF for a Bambu Lab X2D.

**Architecture:** A FreeCAD GUI addon (`FreeCADMCP`) hosts an XML-RPC server on `localhost:9875`, auto-started via a pre-seeded settings file. Claude reaches it through the `freecad-mcp` MCP bridge (registered at user scope via `uvx`). A personal `/3d-model` skill encodes the modeling workflow; a launcher script and smoke-test script make the system self-serve and verifiable.

**Tech Stack:** FreeCAD 1.1.3 (AppImage), neka-nat/freecad-mcp (addon + PyPI package via `uvx`), Python 3 `xmlrpc.client` for direct verification, bash, git.

## Global Constraints

- FreeCAD AppImage path: `/home/brian/Applications/FreeCAD_1.1.3-Linux-x86_64-py311.appimage` (symlinked as `~/.local/bin/freecad`)
- FreeCAD user data dir (expected): `/home/brian/.local/share/FreeCAD/v1-1/` — Task 2 verifies; all later tasks use the verified value
- RPC server: `http://127.0.0.1:9875`, localhost only — `remote_enabled` must stay `false`
- MCP registration: user scope, command `uvx freecad-mcp`, screenshots enabled (NO `--only-text-feedback` flag)
- Project root: `/home/brian/ClaudeProjects/FreeCAD` (git repo, already initialized with `docs/`)
- Skill location: `~/.claude/skills/3d-model/SKILL.md`, version-controlled inside the project repo at `skills/3d-model/SKILL.md` with a symlink from `~/.claude/skills/`
- Bambu Lab X2D limits (from official spec sheet): build volume 256×256×260mm (main nozzle), 235.5×256×256mm (auxiliary/dual nozzle); stock 0.4mm nozzle (0.2/0.6/0.8 supported)
- All temporary/test artifacts go to a `mktemp -d` dir or the session scratchpad, never into `models/`

---

### Task 1: Project scaffolding

**Files:**
- Create: `/home/brian/ClaudeProjects/FreeCAD/.gitignore`
- Create: `/home/brian/ClaudeProjects/FreeCAD/models/.gitkeep`
- Create: `/home/brian/ClaudeProjects/FreeCAD/scripts/.gitkeep`
- Create: `/home/brian/ClaudeProjects/FreeCAD/skills/.gitkeep`

**Interfaces:**
- Consumes: nothing (repo already exists with `docs/`)
- Produces: directory layout `models/`, `scripts/`, `skills/`, `vendor/` (gitignored) that Tasks 2–7 write into

- [ ] **Step 1: Create directories and .gitignore**

```bash
cd /home/brian/ClaudeProjects/FreeCAD
mkdir -p models scripts skills vendor
touch models/.gitkeep scripts/.gitkeep skills/.gitkeep
cat > .gitignore <<'EOF'
# Cloned third-party repos (addon source lives upstream)
vendor/

# FreeCAD backup/autosave files
*.FCStd1
*.FCBak
*.fcstd1
**/backup/

# Python
__pycache__/
EOF
```

- [ ] **Step 2: Verify layout**

Run: `ls /home/brian/ClaudeProjects/FreeCAD`
Expected: `docs  models  scripts  skills  vendor`

- [ ] **Step 3: Commit**

```bash
cd /home/brian/ClaudeProjects/FreeCAD
git add .gitignore models/.gitkeep scripts/.gitkeep skills/.gitkeep
git commit -m "chore: project scaffolding for 3D model system"
```

---

### Task 2: Install the FreeCAD MCP addon with auto-start pre-seeded

**Files:**
- Create: `/home/brian/ClaudeProjects/FreeCAD/vendor/freecad-mcp/` (git clone, not committed)
- Create: `<UserAppDataDir>/Mod/FreeCADMCP/` (copy of `vendor/freecad-mcp/addon/FreeCADMCP`)
- Create: `<UserAppDataDir>/freecad_mcp_settings.json`

**Interfaces:**
- Consumes: `vendor/` dir from Task 1
- Produces: installed addon whose RPC server auto-starts on FreeCAD launch (port 9875). The verified `<UserAppDataDir>` value (expected `/home/brian/.local/share/FreeCAD/v1-1/`). Task 3 relies on auto-start; Task 5 relies on the RPC methods.

Background facts (verified from addon source, 2026-07-26):
- Addon folder to install: `addon/FreeCADMCP` (contains `Init.py`, `InitGui.py`, `rpc_server/`)
- Workbench label in FreeCAD: "MCP Addon"; commands include `Start_RPC_Server`, `Toggle_Auto_Start`
- Auto-start: `InitGui.py` runs `_auto_start_mcp()` via `QtCore.QTimer.singleShot(0, ...)` at GUI startup, gated on settings key `auto_start_rpc`
- Settings file: `os.path.join(FreeCAD.getUserAppDataDir(), "freecad_mcp_settings.json")`, JSON, defaults `{"remote_enabled": false, "allowed_ips": "127.0.0.1", "auto_start_rpc": false}`

- [ ] **Step 1: Clone the addon repo**

```bash
git clone --depth 1 https://github.com/neka-nat/freecad-mcp.git /home/brian/ClaudeProjects/FreeCAD/vendor/freecad-mcp
ls /home/brian/ClaudeProjects/FreeCAD/vendor/freecad-mcp/addon/FreeCADMCP
```
Expected: listing includes `Init.py  InitGui.py  rpc_server`

- [ ] **Step 2: Determine FreeCAD's UserAppDataDir (headless)**

```bash
SCRATCH=$(mktemp -d)
cat > "$SCRATCH/print_dirs.py" <<'EOF'
import FreeCAD
print("USERAPPDATA:" + FreeCAD.getUserAppDataDir())
exit(0)
EOF
timeout 300 freecad -c "$SCRATCH/print_dirs.py" 2>/dev/null | grep USERAPPDATA
```
Expected: `USERAPPDATA:/home/brian/.local/share/FreeCAD/v1-1/`

Fallback if the command hangs or prints nothing (AppImage console-mode quirk): use `/home/brian/.local/share/FreeCAD/v1-1/` — this dir was confirmed to exist during design exploration. Record whichever value you got as `$FCDATA` for the next steps.

- [ ] **Step 3: Copy the addon into the Mod directory**

```bash
FCDATA=/home/brian/.local/share/FreeCAD/v1-1/   # value from Step 2
mkdir -p "$FCDATA/Mod"
cp -r /home/brian/ClaudeProjects/FreeCAD/vendor/freecad-mcp/addon/FreeCADMCP "$FCDATA/Mod/"
ls "$FCDATA/Mod/FreeCADMCP"
```
Expected: `Init.py  InitGui.py  rpc_server` (assets dir may also appear)

- [ ] **Step 4: Pre-seed settings with auto-start enabled**

```bash
FCDATA=/home/brian/.local/share/FreeCAD/v1-1/   # value from Step 2
if [ -f "$FCDATA/freecad_mcp_settings.json" ]; then
  python3 - "$FCDATA/freecad_mcp_settings.json" <<'EOF'
import json, sys
p = sys.argv[1]
s = json.load(open(p))
s["auto_start_rpc"] = True
s["remote_enabled"] = False
json.dump(s, open(p, "w"), indent=2)
EOF
else
  cat > "$FCDATA/freecad_mcp_settings.json" <<'EOF'
{
  "remote_enabled": false,
  "allowed_ips": "127.0.0.1",
  "auto_start_rpc": true
}
EOF
fi
cat "$FCDATA/freecad_mcp_settings.json"
```
Expected: JSON with `"auto_start_rpc": true` and `"remote_enabled": false`

- [ ] **Step 5: Verify install completeness**

```bash
FCDATA=/home/brian/.local/share/FreeCAD/v1-1/
test -f "$FCDATA/Mod/FreeCADMCP/InitGui.py" && \
test -f "$FCDATA/Mod/FreeCADMCP/rpc_server/rpc_server.py" && \
test -f "$FCDATA/freecad_mcp_settings.json" && echo INSTALL_OK
```
Expected: `INSTALL_OK`

(No commit — nothing in this task touches the repo besides gitignored `vendor/`.)

---

### Task 3: Launcher script + first launch + RPC verification

**Files:**
- Create: `/home/brian/ClaudeProjects/FreeCAD/scripts/start-freecad-mcp.sh`

**Interfaces:**
- Consumes: installed addon + auto-start settings from Task 2
- Produces: `scripts/start-freecad-mcp.sh` — idempotent; exits 0 with RPC reachable on `http://127.0.0.1:9875`, exits 1 after 120s otherwise. Used by Task 5's smoke test and referenced by the Task 6 skill.

- [ ] **Step 1: Write the launcher script**

```bash
cat > /home/brian/ClaudeProjects/FreeCAD/scripts/start-freecad-mcp.sh <<'EOF'
#!/usr/bin/env bash
# Start FreeCAD (AppImage) if not running, then wait until the FreeCAD MCP
# RPC server (addon, auto-started via freecad_mcp_settings.json) answers ping.
set -uo pipefail

APPIMAGE="$HOME/Applications/FreeCAD_1.1.3-Linux-x86_64-py311.appimage"
RPC_URL="http://127.0.0.1:9875"

ping_rpc() {
  python3 - "$RPC_URL" <<'PYEOF'
import sys, xmlrpc.client
try:
    s = xmlrpc.client.ServerProxy(sys.argv[1], allow_none=True)
    sys.exit(0 if s.ping() else 1)
except Exception:
    sys.exit(1)
PYEOF
}

if ping_rpc; then
  echo "RPC server already up on $RPC_URL."
  exit 0
fi

if ! pgrep -f "FreeCAD_1.1.3-Linux" > /dev/null; then
  nohup "$APPIMAGE" > /dev/null 2>&1 &
  disown
  echo "FreeCAD launched."
else
  echo "FreeCAD process exists; waiting for RPC..."
fi

for _ in $(seq 1 60); do
  if ping_rpc; then
    echo "RPC server ready on $RPC_URL."
    exit 0
  fi
  sleep 2
done

echo "ERROR: RPC server not reachable after 120s." >&2
echo "If FreeCAD is open: check auto_start_rpc in freecad_mcp_settings.json," >&2
echo "or start it manually: workbench 'MCP Addon' -> 'Start RPC Server'." >&2
exit 1
EOF
chmod +x /home/brian/ClaudeProjects/FreeCAD/scripts/start-freecad-mcp.sh
```

- [ ] **Step 2: Run the launcher (first real launch)**

Run: `/home/brian/ClaudeProjects/FreeCAD/scripts/start-freecad-mcp.sh`
Expected: `FreeCAD launched.` then, within ~120s, `RPC server ready on http://127.0.0.1:9875.` (exit code 0). First AppImage start can be slow.

If it exits 1: FreeCAD may show a first-run dialog blocking startup, or the addon didn't load. Diagnose: `pgrep -af FreeCAD` to confirm the process; ask the user to look at the FreeCAD window and dismiss any first-run dialog; check `ss -tln | grep 9875`. Do NOT proceed until ping succeeds.

- [ ] **Step 3: Verify idempotency**

Run: `/home/brian/ClaudeProjects/FreeCAD/scripts/start-freecad-mcp.sh`
Expected: `RPC server already up on http://127.0.0.1:9875.` (immediate, exit 0)

- [ ] **Step 4: Commit**

```bash
cd /home/brian/ClaudeProjects/FreeCAD
git add scripts/start-freecad-mcp.sh
git commit -m "feat: FreeCAD launcher with RPC readiness wait"
```

---

### Task 4: Register the MCP server with Claude Code

**Files:**
- Modify: `~/.claude.json` (via `claude mcp add`, not edited by hand)

**Interfaces:**
- Consumes: nothing local (server package comes from PyPI via uvx at runtime)
- Produces: MCP server named `freecad` available in all future Claude Code sessions (tools: `execute_code`, `get_view`, `create_object`, etc.)

- [ ] **Step 1: Verify the server package runs**

Run: `timeout 120 uvx freecad-mcp --help`
Expected: exit 0 with usage/help text (first run downloads the package). If it errors, capture output — do not register a broken command.

- [ ] **Step 2: Register at user scope**

```bash
claude mcp add --scope user freecad -- uvx freecad-mcp
```
Expected: confirmation message that `freecad` was added with user scope.

- [ ] **Step 3: Verify registration**

Run: `claude mcp list`
Expected: a line for `freecad` showing command `uvx freecad-mcp`. (Connection status may show connected since FreeCAD is running from Task 3.)

Note: MCP tools do NOT appear in the *current* Claude session; they load on the next session start. This is why Task 5 verifies via XML-RPC directly. The handoff (Task 7) tells the user to restart.

---

### Task 5: Smoke test script + run (end-to-end verification)

**Files:**
- Create: `/home/brian/ClaudeProjects/FreeCAD/scripts/smoke-test.py`

**Interfaces:**
- Consumes: RPC server up (Task 3). RPC methods verified from addon source: `ping()`, `execute_code(code) -> {"success": bool, "message"|"error": str}`, `get_active_screenshot(view_name, width, height) -> base64 PNG str`, `list_documents()`.
- Produces: `scripts/smoke-test.py` — reusable health check; exit 0 = system healthy. Prints the path of a saved screenshot PNG for visual inspection.

- [ ] **Step 1: Write the smoke test**

```bash
cat > /home/brian/ClaudeProjects/FreeCAD/scripts/smoke-test.py <<'EOF'
#!/usr/bin/env python3
"""End-to-end smoke test for the FreeCAD MCP system.

Talks directly to the addon's XML-RPC server (same backend the MCP bridge
uses): creates a 10mm cube, captures a screenshot, exports an STL, validates
both, then cleans up. Exit 0 = healthy.
"""
import base64
import os
import struct
import sys
import tempfile
import xmlrpc.client

RPC_URL = "http://127.0.0.1:9875"
DOC = "SmokeTest"


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def rpc_code(srv, code, what):
    res = srv.execute_code(code)
    if not res.get("success"):
        fail(f"{what}: {res.get('error', res)}")
    return res


def main():
    out = tempfile.mkdtemp(prefix="freecad-smoke-")
    try:
        srv = xmlrpc.client.ServerProxy(RPC_URL, allow_none=True)
        if not srv.ping():
            fail("ping returned falsy")
    except Exception as e:
        fail(f"cannot reach RPC server at {RPC_URL}: {e}")
    print("ok: ping")

    rpc_code(srv, (
        "import FreeCAD\n"
        f"doc = FreeCAD.newDocument('{DOC}')\n"
        "box = doc.addObject('Part::Box', 'TestCube')\n"
        "box.Length = 10\nbox.Width = 10\nbox.Height = 10\n"
        "doc.recompute()\n"
        "FreeCAD.Gui.ActiveDocument.ActiveView.fitAll()\n"
    ), "create cube")
    print("ok: cube created")

    b64 = srv.get_active_screenshot("Isometric", 800, 600)
    if not b64:
        fail("get_active_screenshot returned empty")
    png = base64.b64decode(b64)
    if png[:4] != b"\x89PNG":
        fail("screenshot is not a PNG")
    shot = os.path.join(out, "smoke_screenshot.png")
    with open(shot, "wb") as f:
        f.write(png)
    print(f"ok: screenshot ({len(png)} bytes) -> {shot}")

    stl = os.path.join(out, "test_cube.stl")
    rpc_code(srv, (
        "import FreeCAD, Mesh\n"
        f"doc = FreeCAD.getDocument('{DOC}')\n"
        f"Mesh.export([doc.getObject('TestCube')], '{stl}')\n"
    ), "export STL")
    if not os.path.exists(stl):
        fail("STL file not written")
    data = open(stl, "rb").read()
    if data[:5] == b"solid":
        if b"facet" not in data:
            fail("ASCII STL has no facets")
    else:
        if len(data) < 84:
            fail(f"binary STL too small ({len(data)} bytes)")
        (n,) = struct.unpack("<I", data[80:84])
        if n < 12 or len(data) != 84 + 50 * n:
            fail(f"binary STL malformed: {n} triangles, {len(data)} bytes")
    print(f"ok: STL valid ({len(data)} bytes) -> {stl}")

    rpc_code(srv, f"import FreeCAD\nFreeCAD.closeDocument('{DOC}')\n", "cleanup")
    print("ok: cleanup")
    print(f"SMOKE TEST PASSED (artifacts in {out})")


if __name__ == "__main__":
    main()
EOF
chmod +x /home/brian/ClaudeProjects/FreeCAD/scripts/smoke-test.py
```

- [ ] **Step 2: Run it — expect failure-free pass**

Run: `python3 /home/brian/ClaudeProjects/FreeCAD/scripts/smoke-test.py`
Expected output (paths vary):
```
ok: ping
ok: cube created
ok: screenshot (NNNNN bytes) -> /tmp/freecad-smoke-XXXX/smoke_screenshot.png
ok: STL valid (684 bytes) -> /tmp/freecad-smoke-XXXX/test_cube.stl
ok: cleanup
SMOKE TEST PASSED
```
(684 bytes = binary STL of a 12-triangle cube; ASCII output is also accepted by the validator.)

- [ ] **Step 3: Visually inspect the screenshot**

Read (view) the printed `smoke_screenshot.png` path with the file-reading tool.
Expected: a gray/white cube visible in FreeCAD's 3D view. If the image is blank, the FreeCAD window is likely fully occluded/minimized — surface this to the user (known limitation noted in the design spec) and re-run.

- [ ] **Step 4: Commit**

```bash
cd /home/brian/ClaudeProjects/FreeCAD
git add scripts/smoke-test.py
git commit -m "feat: end-to-end smoke test for FreeCAD MCP system"
```

---

### Task 6: The /3d-model skill

**Files:**
- Create: `/home/brian/ClaudeProjects/FreeCAD/skills/3d-model/SKILL.md`
- Create: symlink `~/.claude/skills/3d-model` → `/home/brian/ClaudeProjects/FreeCAD/skills/3d-model`

**Interfaces:**
- Consumes: launcher path from Task 3, smoke-test path from Task 5, MCP server name `freecad` from Task 4
- Produces: personal skill `/3d-model` available in all sessions

- [ ] **Step 1: Write SKILL.md with the complete workflow**

Write the file `/home/brian/ClaudeProjects/FreeCAD/skills/3d-model/SKILL.md` with exactly this content:

````markdown
---
name: 3d-model
description: Use when the user asks to design, generate, create, or modify a 3D model or 3D-printable part — including recreating a part from photos, drawings, or sketches. Drives FreeCAD via the freecad MCP server with screenshot verification at every step; exports STL + 3MF for a Bambu Lab X2D printer.
---

# Generate 3D Models in FreeCAD (Bambu Lab X2D)

Build models feature-by-feature in FreeCAD, visually verifying each step via
screenshots, then export STL + 3MF for slicing in Bambu Studio.

## Prerequisites (check before modeling)

1. **FreeCAD running + RPC up:** run
   `/home/brian/ClaudeProjects/FreeCAD/scripts/start-freecad-mcp.sh`
   (idempotent; exit 0 means ready).
2. **MCP tools available:** the `freecad` MCP server provides `execute_code`,
   `get_view`, `create_object`, `edit_object`, `get_objects`, etc. If these
   tools are NOT in the session, either ask the user to restart the session,
   or fall back to direct XML-RPC from Bash (same backend):
   ```python
   import xmlrpc.client
   srv = xmlrpc.client.ServerProxy("http://127.0.0.1:9875", allow_none=True)
   srv.execute_code("...")                          # {"success":..., "message"/"error":...}
   b64 = srv.get_active_screenshot("Isometric", 800, 600)  # base64 PNG; decode, save, then view the file
   ```
3. **Health doubt?** run `python3 /home/brian/ClaudeProjects/FreeCAD/scripts/smoke-test.py`.

## Phase 1 — Brief

Ask ONLY load-bearing questions (batch them; don't interrogate):
- Critical dimensions; what the part attaches to / must fit
- Orientation or strength concerns; aesthetic preferences for decorative parts
State every assumption you make instead of asking about it.

## Phase 1b — Recreating from images

When the user provides photos/drawings/sketches:
- **Scale first:** a photo has no absolute scale. Require at least one known
  dimension ("80mm wide", "fits a 608 bearing"). If none, ask the user to
  measure ONE feature; estimate the rest proportionally from the image.
- **Analyze before building:** write out your geometry interpretation —
  primitive decomposition, symmetries, hole patterns, estimated dimension
  table — and get the user's corrections BEFORE any FreeCAD work.
- **During the build:** match `get_view` angles to the photo's viewpoint and
  compare side by side; course-correct proportions.
- Copy reference images into `models/<name>/reference/`.
- Set expectations: flat-faced functional geometry reproduces well; organic
  shapes reproduce approximately. Measured dimensions ALWAYS override
  apparent photo proportions.

## Phase 2 — Plan

- Decompose into an ordered feature list (base solid → bosses/pockets →
  holes → fillets/chamfers). Present it briefly.
- State intended PRINT ORIENTATION up front — it drives overhang and
  strength decisions (layer lines are the weak direction).

## Phase 3 — Build loop (the core discipline)

For each feature:
1. Execute it (`execute_code` with a batched, self-contained Python block —
   one feature per call, not one line per call; each mutating MCP call
   returns a screenshot automatically).
2. **Inspect the returned screenshot before continuing.** Wrong geometry is
   fixed NOW, not later. Never stack features on broken geometry — delete
   the failed feature and rebuild it differently.
3. At ambiguity points, grab extra views: `get_view` with `Front`, `Top`,
   `Right`, `Isometric`. Blank screenshot → FreeCAD window is occluded; ask
   the user to un-minimize it, then re-request.

Workbench choice:
- **PartDesign** (Body → Sketch → Pad/Pocket/...) for functional parametric
  parts — produces an editable feature tree the user can tweak in the GUI.
- **Part** primitives + booleans for quick composed shapes.
- Lofts/sweeps/surfacing for organic forms.
- Always `doc.recompute()` after mutations; check for recompute errors in
  the returned message.

## Phase 4 — Printability check (X2D, before export)

| Check | Rule (0.4mm nozzle; adapt if user runs 0.2/0.6/0.8) |
|---|---|
| Wall thickness | ≥ 0.84mm (2 perimeters × ~0.42mm line width) |
| Overhangs | flag > 45° unsupported; suggest chamfer/orientation fix |
| Small holes | note shrinkage; suggest +0.1–0.2mm compensation or drilling |
| Build volume | ≤ 256×256×260mm (main nozzle); ≤ 235.5×256×256mm if dual-nozzle/multi-material print |
| Mating clearance | ~0.2mm snug fit, ~0.3mm free fit |
| First layer | prefer a flat face on the bed; note elephant-foot on precision bores |

Report anything unfixable without changing requirements — don't silently
alter user-specified dimensions.

## Phase 5 — Export & handoff

```python
# via execute_code — <name> = kebab-case model name
import FreeCAD, Mesh
doc = FreeCAD.ActiveDocument
doc.saveAs("/home/brian/ClaudeProjects/FreeCAD/models/<name>/<name>.FCStd")
objs = [o for o in doc.Objects if o.TypeId.startswith(("Part::", "PartDesign::")) and o.Visibility]
Mesh.export(objs, "/home/brian/ClaudeProjects/FreeCAD/models/<name>/<name>.stl")
Mesh.export(objs, "/home/brian/ClaudeProjects/FreeCAD/models/<name>/<name>.3mf")
```
- `mkdir -p` the model dir first; verify both export files exist and are
  plausibly sized afterwards.
- Commit the model dir to git (repo: `/home/brian/ClaudeProjects/FreeCAD`).
- Hand the user both file paths + suggested print orientation. The user
  slices in Bambu Studio — never claim the part was sent to the printer.

## Error handling

- `execute_code` returns `{"success": false, "error": ...}` → diagnose from
  the error plus a fresh screenshot; simplify the operation; never retry the
  identical failing call blindly.
- RPC unreachable → run the launcher script; if still down, tell the user to
  open FreeCAD and check the "MCP Addon" workbench → Start RPC Server.
- Boolean/sketch failures: reduce to simpler primitives, or rebuild the
  sketch fully-constrained; over-constrained sketches must be fixed, not
  ignored.
````

- [ ] **Step 2: Symlink into personal skills**

```bash
mkdir -p ~/.claude/skills
ln -sfn /home/brian/ClaudeProjects/FreeCAD/skills/3d-model ~/.claude/skills/3d-model
ls -la ~/.claude/skills/3d-model/
```
Expected: symlink resolves; listing shows `SKILL.md`

- [ ] **Step 3: Verify the skill loads in a fresh session**

Run: `cd /tmp && claude -p "Do you have a skill named 3d-model available? Answer only yes or no." --max-turns 1`
Expected: output containing `yes`. If `no`, the skill loader may not follow symlinks — replace the symlink with a real copy (`rm ~/.claude/skills/3d-model && cp -r /home/brian/ClaudeProjects/FreeCAD/skills/3d-model ~/.claude/skills/3d-model`) and note in CLAUDE.md (Task 7) that edits must be synced to both copies.

- [ ] **Step 4: Commit**

```bash
cd /home/brian/ClaudeProjects/FreeCAD
git add skills/3d-model/SKILL.md
git commit -m "feat: /3d-model skill encoding the modeling workflow"
```

---

### Task 7: Project CLAUDE.md + handoff

**Files:**
- Create: `/home/brian/ClaudeProjects/FreeCAD/CLAUDE.md`

**Interfaces:**
- Consumes: everything above
- Produces: in-repo quick reference for future sessions started in this directory

- [ ] **Step 1: Write CLAUDE.md**

```bash
cat > /home/brian/ClaudeProjects/FreeCAD/CLAUDE.md <<'EOF'
# FreeCAD 3D Model Generation Project

Claude generates 3D models here for Brian's Bambu Lab X2D printer.

## How it works
- The `/3d-model` skill (`skills/3d-model/SKILL.md`, symlinked into
  `~/.claude/skills/`) holds the full modeling workflow — use it for any
  model request.
- FreeCAD 1.1.3 AppImage + `FreeCADMCP` addon (RPC on localhost:9875,
  auto-starts with FreeCAD). MCP server `freecad` registered at user scope
  (`uvx freecad-mcp`).
- Start/ensure FreeCAD: `scripts/start-freecad-mcp.sh`
- Health check: `python3 scripts/smoke-test.py`

## Layout
- `models/<name>/` — `<name>.FCStd` + `<name>.stl` + `<name>.3mf`
  (+ `reference/` images when recreated from photos)
- `vendor/freecad-mcp/` — gitignored clone; to update the addon:
  `git -C vendor/freecad-mcp pull` then re-copy `addon/FreeCADMCP` to
  `~/.local/share/FreeCAD/v1-1/Mod/` and restart FreeCAD.
- `docs/superpowers/` — design spec and implementation plan.

## Printer constraints (X2D)
Build volume 256×256×260mm (main nozzle) / 235.5×256×256mm (dual-nozzle
prints); stock 0.4mm nozzle. Full printability rules live in the skill.
EOF
```

- [ ] **Step 2: Commit**

```bash
cd /home/brian/ClaudeProjects/FreeCAD
git add CLAUDE.md
git commit -m "docs: project CLAUDE.md quick reference"
```

- [ ] **Step 3: Handoff message to the user**

Tell the user, verbatim in substance:
1. Setup is complete and smoke-tested (cube built, screenshotted, exported, verified).
2. **Restart Claude Code once** so the `freecad` MCP tools load; verify with `/mcp` (should list `freecad` as connected while FreeCAD is running).
3. From then on: ask for a model in plain language (optionally `/3d-model`), from any directory; attach photos to recreate a real part.
4. Exports land in `~/ClaudeProjects/FreeCAD/models/<name>/` as STL + 3MF, ready for Bambu Studio.

---

## Self-review notes (completed)

- **Spec coverage:** MCP selection → Tasks 2/4; addon auto-start → Task 2; launcher → Task 3; skill with all five phases + image recreation + printability + error handling → Task 6; folder structure + git → Tasks 1/7; smoke test → Task 5; handoff/restart caveat → Tasks 4/7. Out-of-scope items (slicing, AMS, FEM) correctly absent.
- **Placeholder scan:** clean — every step has exact commands/content; the two documented fallbacks (Step 2 of Task 2, Step 3 of Task 6) specify the exact alternative action.
- **Type consistency:** RPC method names/signatures in Tasks 3/5/6 all match the addon source (`ping`, `execute_code`, `get_active_screenshot(view_name, width, height)`); launcher and smoke-test paths consistent across Tasks 3/5/6/7.
