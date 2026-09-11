"""Embed mirror code into a plan document (Plan 2 by default).

The plan carries marker pairs; everything between a pair is regenerated from
the mirror directory so the plan's code blocks are byte-identical to the
tested mirror files:

    <!-- code: cablayout.py unit 4 -->          unit between "# === TASK 4 ===" and the next marker
    <!-- code: cabvoice.py symbols a,b,c -->     top-level defs, classes, or CONST blocks by name
    <!-- code: fixtures/site-default/cab.py all -->
    <!-- /code -->
    <!-- include: task1.md -->                   a markdown fragment inserted verbatim
    <!-- /include -->

Paths are relative to the mirror directory: plan2-mirror by default, or the
directory under pipeline/ named by --mirror (Plan 3 uses --mirror plan3-mirror).
Usage, from the vault root:
    .venv/bin/python projects/Speaker-cab-system/pipeline/embed_plan_code.py [--check] [--plan PATH] [--mirror NAME]
--check exits 1 when the plan would change (the plan is out of sync with the mirror).
"""
import re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sync_plan_code import units  # noqa: E402  (same unit splitter as Plan 1's sync tool)

MIRROR = HERE / "plan2-mirror"
PLAN = HERE.parent / "plan-2-generator.md"
OPEN = re.compile(r"^<!-- (code|include): (\S+)(?: (unit \d+|symbols \S+|all))? -->$")
FENCE = {".py": "python", ".json": "json", ".md": "markdown", ".sh": "bash", ".csv": "text", ".txt": "text"}
TASK_RE = re.compile(r"^# === TASK (\d+) ===\s*$")


def unit_text(path: pathlib.Path, n: int) -> str:
    lines = path.read_text().splitlines()
    starts = [(i, int(TASK_RE.match(l).group(1))) for i, l in enumerate(lines) if TASK_RE.match(l)]
    for k, (i, num) in enumerate(starts):
        if num == n:
            j = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
            # the first unit of a file carries the file preamble (docstring, imports);
            # every unit keeps its marker line so the landed file has the same markers
            body = (lines[:i] if k == 0 else []) + [lines[i]] + lines[i + 1:j]
            while body and not body[0].strip():
                body.pop(0)
            while body and not body[-1].strip():
                body.pop()
            return "\n".join(body) + "\n"
    raise SystemExit(f"{path}: no '# === TASK {n} ===' marker")


def symbols_text(path: pathlib.Path, names: list[str]) -> str:
    found = dict(units(path.read_text()))
    missing = [n for n in names if n not in found]
    if missing:
        raise SystemExit(f"{path}: symbols not found: {', '.join(missing)}")
    return "\n\n".join(found[n].rstrip("\n") for n in names) + "\n"


def render(kind: str, target: str, mode: str | None) -> list[str]:
    path = MIRROR / target
    if not path.exists():
        raise SystemExit(f"missing mirror file: {path}")
    if kind == "include":
        return path.read_text().rstrip("\n").splitlines()
    if mode is None or mode == "all":
        body = path.read_text().rstrip("\n") + "\n"
    elif mode.startswith("unit "):
        body = unit_text(path, int(mode.split()[1]))
    else:
        body = symbols_text(path, mode.split()[1].split(","))
    fence = "````" if path.suffix == ".md" else "```"
    return [f"{fence}{FENCE.get(path.suffix, 'text')}"] + body.rstrip("\n").splitlines() + [fence]


def embed(text: str) -> str:
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        m = OPEN.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        kind, target, mode = m.groups()
        close = f"<!-- /{kind} -->"
        try:
            j = lines.index(close, i + 1)
        except ValueError:
            raise SystemExit(f"line {i + 1}: '{lines[i]}' has no closing {close}")
        out.append(lines[i]); out.extend(render(kind, target, mode)); out.append(close)
        i = j + 1
    return "\n".join(out) + "\n"


def main(argv):
    global MIRROR
    check = "--check" in argv
    plan = PLAN
    if "--mirror" in argv:
        MIRROR = HERE / argv[argv.index("--mirror") + 1]
    if "--plan" in argv:
        plan = pathlib.Path(argv[argv.index("--plan") + 1])
    old = plan.read_text()
    new = embed(old)
    if new == old:
        print(f"{plan.name}: in sync"); return 0
    if check:
        print(f"{plan.name}: OUT OF SYNC with the mirror"); return 1
    plan.write_text(new); print(f"{plan.name}: embedded"); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
