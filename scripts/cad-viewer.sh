#!/usr/bin/env bash
# Open OCP CAD Viewer in a Chrome whose WebGL works in this Chrome Remote
# Desktop session. The regular desktop Chrome cannot create a WebGL context
# here (llvmpipe GL fails with "BindToCurrentSequence failed"), so this
# launches a separate-profile instance that routes WebGL to the RTX 3060
# via ANGLE-on-Vulkan (works on the CRD virtual display, where GLX is
# software-only). Do NOT add --enable-features=Vulkan,... - that breaks
# context creation. Previous SwiftShader fallback worked but rendered on
# the CPU and was extremely slow.
# Idempotent: also starts the viewer server if port 3939 is not answering.
set -euo pipefail

VAULT="$(cd "$(dirname "$0")/.." && pwd)"
URL="http://localhost:3939/viewer"

if ! curl -sf -o /dev/null "$URL"; then
    nohup "$VAULT/.venv/bin/python" -m ocp_vscode --port 3939 \
        >/tmp/ocp-viewer.log 2>&1 &
    for _ in $(seq 1 20); do
        curl -sf -o /dev/null "$URL" && break
        sleep 0.5
    done
fi

# --gtk-version=4: Chrome 151 (2026-08-25) segfaults at startup on this desktop
# without it (the session's own Chrome runs with the same flag).
nohup google-chrome --gtk-version=4 \
    --user-data-dir="$HOME/.cache/cad-viewer-chrome" \
    --use-gl=angle --use-angle=vulkan \
    --ignore-gpu-blocklist \
    --no-first-run --no-default-browser-check \
    --new-window "$URL" >/dev/null 2>&1 &

echo "viewer: $URL (push models with SHOW=reset first, SHOW=1 for iterations)"
