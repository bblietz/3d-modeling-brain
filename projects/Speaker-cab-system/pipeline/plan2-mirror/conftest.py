"""Mirror-only pytest setup (not part of the plan).

The mirror keeps the landed files under .vault/ with the vault's directory
shape, so cabvoice.VAULT and cabvoice.SPEAKERS_DIR resolve to the mirror on
their own. This file makes `import cabvoice` from the mirror root pick the
mirror engine through the top-level symlink and checks the resolution.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cabvoice  # noqa: E402

assert cabvoice.SPEAKERS_DIR.resolve() == (HERE / ".vault" / "knowledge" / "speakers").resolve(), cabvoice.SPEAKERS_DIR
assert Path(cabvoice.__file__).resolve().parent == (HERE / ".vault/scripts").resolve()
