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

if [ ! -x "$APPIMAGE" ]; then
  echo "ERROR: FreeCAD AppImage not found or not executable: $APPIMAGE" >&2
  exit 1
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
