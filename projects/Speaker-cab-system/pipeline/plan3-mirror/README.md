# Plan 3 mirror

The tested oracle for `projects/Speaker-cab-system/plan-3-skill.md`, in the
Plan 2 pattern. `.vault/` holds every file Plan 3 lands, in the vault's
directory shape, so the suites run against the mirror on their own:

    ./run_tests.sh              every suite (about 90 s; the CAD suite dominates)
    ./run_tests.sh -k report    one suite's selection

Embed into the plan from the vault root:

    .venv/bin/python projects/Speaker-cab-system/pipeline/embed_plan_code.py --plan projects/Speaker-cab-system/plan-3-skill.md --mirror plan3-mirror [--check]

Rules for the forks that develop here: only `.vault/` files change (never the
landed `scripts/` or `knowledge/`); every new piece of code is a top-level
def, class, or CONST block so the embed tool can address it by name; new tests
go at the end of their file under a `# ---- Plan 3 Task N: ... ----` comment;
no em dashes anywhere; each fork leaves `FORK-<letter>.md` at the mirror root
with what changed, by symbol, and the test counts.
