#!/usr/bin/env bash
# Plan 3 mirror: every suite runs from .vault/scripts so cabvoice.VAULT, the
# fixture lookups, and cab.py's vault walk all resolve to the mirror's .vault.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python
cd "$HERE/.vault/scripts"
FILES="test_cabvoice.py test_cutlist.py test_cablayout.py test_cabmodel.py"
[ -f test_cabreport.py ] && FILES="$FILES test_cabreport.py"
"$PY" -m pytest $FILES -q "$@"
