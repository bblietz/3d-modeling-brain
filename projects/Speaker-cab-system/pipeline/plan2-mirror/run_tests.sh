#!/usr/bin/env bash
# Plan 2 mirror: the engine and cut list suites (Tasks 1 to 3), run against the
# mirror engine and the patched mirror catalog. Layout and CAD suites (fork A
# and C) run from the mirror root.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python
cd "$HERE/.vault/scripts" && "$PY" -m pytest test_cabvoice.py test_cutlist.py -q "$@"
