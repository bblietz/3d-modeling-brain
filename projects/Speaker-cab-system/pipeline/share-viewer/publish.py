#!/usr/bin/env python3
"""Build and publish a speaker-cab order's client-facing 3D preview to the live
MaximoCabs site: one command instead of chaining build_share.py, a manual copy,
and the git commands by hand. Defaults match Cab-ElShaieb-1x12-hardwood's page
(Brian, 2026-09-16): build_share.py/viewer.html already always show the grill
and render correctly on a phone, so this tool adds no flags for either - it
only automates getting a build_share.py run onto the live site and back.

    .venv/bin/python projects/Speaker-cab-system/pipeline/share-viewer/publish.py \
      projects/Cab-<...> --message "$(cat <<'EOF'
Cab <Customer>: 3D model preview

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <this session's URL>
EOF
)" [--customer NAME] [--stripe-option LABEL=none|primary|PATH ...] [--slug SLUG] [--no-wait]

`--message` should carry the session's own attribution trailer (this script
does not know it); a plain default is used if omitted, which is fine for a
dry run but not for a real publish - always pass one for real work.

Exit codes: 0 published, or already up to date, nothing to push; 1 input
error (order files missing, build_share.py failed); 2 viewer.html's inline
scripts are not yet allowed by MaximoCabs' CSP (its content changed since the
hash was last updated - see SKILL.md Phase 6 step 4, a real-browser fix, not
one this tool can make safely); 3 a local npm test or npm run check failed;
4 the git push or the GitHub Actions deploy failed or timed out.
"""
import argparse
import base64
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_share  # noqa: E402

MAXIMOCABS = Path.home() / "ClaudeProjects" / "MaximoCabs"
HEADERS_FILE = MAXIMOCABS / "public" / "_headers"
SITE_URL = "https://maximocabs.pages.dev"
DEPLOY_TIMEOUT_S = 300
DEPLOY_POLL_S = 8


def script_hashes(html_text: str) -> list[str]:
    """sha256-<base64> for every inline <script> block CSP must allow: the
    importmap and the module script, both byte-identical across every order
    since build_share.py only ever substitutes into the separate JSON data
    island, never these two."""
    out = []
    for m in re.finditer(r'<script type="(?:importmap|module)">(.*?)</script>', html_text, re.S):
        digest = hashlib.sha256(m.group(1).encode("utf-8")).digest()
        out.append("sha256-" + base64.b64encode(digest).decode("ascii"))
    return out


def run(cmd, cwd=None):
    print("$ " + " ".join(cmd if len(cmd) < 4 else [*cmd[:3], "..."]))
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("order", type=Path, help="order directory holding cab.step, cab.json, voicing.json")
    ap.add_argument("--customer", help="customer name (default: the brief's frontmatter)")
    ap.add_argument("--stripe-option", action="append", metavar="LABEL=none|primary|PATH",
                     help="see build_share.py --help; only needed when this order offers more than one accent-stripe design")
    ap.add_argument("--slug", help="override the <order-slug> in the URL (default: the order directory name, lowercased)")
    ap.add_argument("--message", help="commit message, trailers included (a plain default is used if omitted)")
    ap.add_argument("--no-wait", action="store_true", help="push and return without waiting for the GitHub Actions deploy")
    args = ap.parse_args(argv)

    for name in ("cab.step", "cab.json", "voicing.json"):
        if not (args.order / name).exists():
            print(f"input error: {args.order / name} not found")
            return 1
    try:
        out = build_share.build(args.order, args.customer, args.stripe_option)
    except Exception as e:  # noqa: BLE001 - surfaced to the operator, not handled here
        print(f"input error: build_share.py failed: {e}")
        return 1
    print(f"built {out} ({out.stat().st_size / 1e6:.2f} MB)")

    slug = args.slug or args.order.name.lower()
    dest = MAXIMOCABS / "public" / "share" / slug / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(out, dest)
    url = f"{SITE_URL}/share/{slug}/"

    need = script_hashes(dest.read_text())
    have = set(re.findall(r"sha256-[A-Za-z0-9+/=]+", HEADERS_FILE.read_text()))
    missing = [h for h in need if h not in have]
    if missing:
        print("blocker: viewer.html's own script content is not yet allowed by MaximoCabs' CSP")
        print("(it changed since the hash in public/_headers was last updated). Missing:")
        for h in missing:
            print(f"  '{h}'")
        print("Fix (SKILL.md Phase 6 step 4): npm run build in MaximoCabs, serve it locally")
        print("(npx wrangler pages dev dist), reload this order's page in a real browser,")
        print("read the exact hash from the CSP violation console message, and add it to")
        print("both public/_headers and src/lib/security-headers.ts. Then run this again.")
        return 2

    rel = f"public/share/{slug}/index.html"
    status = run(["git", "status", "--porcelain", "--", rel], cwd=MAXIMOCABS)
    if not status.stdout.strip():
        print(f"up to date: {rel} already matches what's committed.")
        print(f"live: {url}")
        return 0

    for label, cmd in (("npm test", ["npm", "test"]), ("npm run check", ["npm", "run", "check"])):
        r = run(cmd, cwd=MAXIMOCABS)
        if r.returncode != 0:
            print(r.stdout[-4000:])
            print(r.stderr[-2000:])
            print(f"blocker: {label} failed in MaximoCabs; not pushing.")
            return 3

    add = run(["git", "add", rel], cwd=MAXIMOCABS)
    if add.returncode != 0:
        print(add.stderr)
        return 4
    message = args.message or f"share-viewer: publish {slug}"
    commit = run(["git", "commit", "-m", message], cwd=MAXIMOCABS)
    if commit.returncode != 0:
        print(commit.stdout, commit.stderr)
        return 4
    push = run(["git", "push", "origin", "main"], cwd=MAXIMOCABS)
    if push.returncode != 0:
        print(push.stdout, push.stderr)
        print("blocker: git push failed; the commit is local only.")
        return 4

    if args.no_wait:
        print(f"pushed; deploy in progress. live once it finishes: {url}")
        return 0

    print("waiting for the GitHub Actions deploy...")
    deadline = time.time() + DEPLOY_TIMEOUT_S
    while time.time() < deadline:
        r = run(["gh", "run", "list", "--limit", "1", "--json", "status,conclusion"], cwd=MAXIMOCABS)
        if r.returncode != 0:
            print(r.stderr)
            return 4
        row = json.loads(r.stdout)[0]
        if row["status"] == "completed":
            if row["conclusion"] == "success":
                print(f"deploy succeeded.\nlive: {url}")
                return 0
            print(f"blocker: deploy finished with conclusion {row['conclusion']!r}; "
                  f"see `gh run view` in {MAXIMOCABS}. Pushed but not confirmed live: {url}")
            return 4
        time.sleep(DEPLOY_POLL_S)
    print(f"blocker: deploy did not finish within {DEPLOY_TIMEOUT_S}s; "
          f"check `gh run list` in {MAXIMOCABS}. Pushed but not confirmed live: {url}")
    return 4


if __name__ == "__main__":
    sys.exit(main())
