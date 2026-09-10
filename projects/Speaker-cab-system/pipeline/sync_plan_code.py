"""Sync the plan's code blocks to the landed code after review fixes.

ORIGINAL text of each top-level unit (def, class, CONST block) is taken from the
first commit that landed it (implementers transcribed the plan verbatim), LANDED
text from the working tree. Units whose landed text is already in the plan are
skipped; changed units are replaced; new test functions are inserted after their
predecessor. Also bumps the per-task expected pass counts.

Usage, from the vault root: .venv/bin/python projects/Speaker-cab-system/pipeline/sync_plan_code.py [--apply]
"""
import re, subprocess, sys, pathlib
PLAN = pathlib.Path("projects/Speaker-cab-system/plan-1-knowledge-engine.md")
FIRST_COMMITS = ["3d028a7", "961be2d", "b43502e", "89ad8be", "cc23f9e", "b2d11a3", "1d96f80", "278d6a8", "f09fbc5", "d2ae7c9"]
UNIT_RE = re.compile(r"^(def |class |[A-Z_][A-Z0-9_]* *=|@)", re.M)

def git_show(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True, check=True).stdout

def units(text):
    lines = text.splitlines(keepends=True)
    starts = [i for i, l in enumerate(lines) if UNIT_RE.match(l)]
    merged = []
    for i in starts:
        if merged and lines[merged[-1]].startswith("@") and all(
                lines[j].startswith("@") or lines[j].startswith(" ") or lines[j].strip() == "" for j in range(merged[-1], i)):
            continue
        merged.append(i)
    out = []
    for k, i in enumerate(merged):
        j = merged[k + 1] if k + 1 < len(merged) else len(lines)
        chunk = lines[i:j]
        while chunk and (chunk[-1].strip() == "" or chunk[-1].startswith("#")):
            chunk.pop()
        name = None
        for l in chunk:
            m = re.match(r"^(?:def|class) (\w+)|^([A-Z_][A-Z0-9_]*) *=", l)
            if m:
                name = m.group(1) or m.group(2); break
        if name:
            out.append((name, "".join(chunk).rstrip("\n") + "\n"))
    return out

def originals(path):
    """name -> text as first landed (the plan's verbatim version)."""
    seen = {}
    for rev in FIRST_COMMITS:
        try:
            for name, body in units(git_show(rev, path)):
                seen.setdefault(name, body)
        except subprocess.CalledProcessError:
            pass
    return seen

def sync(kind, path, plan):
    orig = originals(path); landed = units(pathlib.Path(path).read_text())
    for idx, (name, body) in enumerate(landed):
        if plan.count(body) == 1:
            continue
        if name in orig and plan.count(orig[name]) == 1:
            plan = plan.replace(orig[name], body); print(f"{kind} replace {name}: ok")
        elif name in orig and plan.count(orig[name]) > 1:
            print(f"{kind} replace {name}: !! original found {plan.count(orig[name])}x")
        else:
            pred = landed[idx - 1][1]; n = plan.count(pred)
            if n == 1:
                plan = plan.replace(pred, pred + "\n\n" + body.rstrip("\n") + "\n"); print(f"{kind} insert {name}: ok")
            else:
                print(f"{kind} insert {name}: !! predecessor found {n}x")
    return plan

def fix_counts(plan):
    heads = [(m.start(), int(m.group(1))) for m in re.finditer(r"^### Task (\d+):", plan, re.M)]
    def task_at(pos):
        t = None
        for start, n in heads:
            if start <= pos: t = n
        return t
    edits = [(1, "Expected: 9 passed", "Expected: 10 passed"),
             (2, "(9 from Task 1 plus 14 here)", "(10 from Task 1 plus 14 here)"),
             (4, "Expected: all passed (8 new)", "Expected: all passed (9 new)"),
             (5, "Expected: all passed (4 new)", "Expected: all passed (5 new)"),
             (6, "Expected: all passed (9 new)", "Expected: all passed (10 new)"),
             (7, "Expected: all passed (8 new)", "Expected: all passed (11 new)")]
    for task, old, new in edits:
        hits = [m.start() for m in re.finditer(re.escape(old), plan) if task_at(m.start()) == task]
        if len(hits) == 1:
            i = hits[0]; plan = plan[:i] + new + plan[i + len(old):]; print(f"count fix task {task}: ok")
        elif len(hits) == 0 and plan.count(new) >= 1:
            print(f"count fix task {task}: already applied")
        else:
            print(f"count fix task {task}: !! {len(hits)} hits")
    return plan

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    plan = PLAN.read_text()
    plan = sync("code", "scripts/cabvoice.py", plan)
    plan = sync("test", "scripts/test_cabvoice.py", plan)
    plan = fix_counts(plan)
    if apply:
        PLAN.write_text(plan); print("plan written")
    else:
        print("dry run only (nothing written)")
