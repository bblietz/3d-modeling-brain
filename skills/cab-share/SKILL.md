---
name: cab-share
description: Use to build or rebuild a MaximoCabs order's client-facing 3D model page and publish it live on maximocabs.pages.dev. Runs automatically as part of the speaker-cab skill's Phase 6 for every new order; call it directly to republish an order after a later edit (a construction change, a new accent-stripe option, a share-viewer template fix).
---

# Publish a cab order's 3D preview

One command instead of the old build-then-copy-then-git-push-by-hand
procedure: `projects/Speaker-cab-system/pipeline/share-viewer/publish.py`
builds the order's page (`build_share.py`), copies it into the MaximoCabs
repo, checks it against the site's CSP, and (if there's an actual change)
runs the site's own tests, commits, pushes, and waits for the Cloudflare
Pages deploy to confirm the link is live. Say the resulting link back to
Brian in chat every time - that is the point of automating this.

## Defaults (Brian, 2026-09-16, from Cab-ElShaieb-1x12-hardwood's page)

Nothing to configure here - these are just always true of every page this
tool builds, because they live in `viewer.html`/`build_share.py`
themselves, not in a flag:

- The grill (frame and cloth) is always shown; there is no take-off-the-
  grill control.
- The page has a proper `<!DOCTYPE html>` and
  `<meta name="viewport" content="width=device-width, initial-scale=1">`,
  so it renders correctly on a phone instead of shrunk to fit a desktop-
  width virtual viewport.
- An order with `Aesthetics.accent_stripes` gets a with/without-stripe
  selector automatically; an order with more than one stripe design to
  compare needs `--stripe-option` (below) - see
  [[speaker-cab-construction]], "Accent stripes."

## Running it

```bash
cd /home/brian/ClaudeProjects/3d-modeling-brain
/home/brian/ClaudeProjects/3d-modeling-brain/.venv/bin/python \
  projects/Speaker-cab-system/pipeline/share-viewer/publish.py \
  projects/Cab-<...> \
  --message "$(cat <<'EOF'
Cab <Customer>: 3D model preview

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <this session's own URL>
EOF
)"
```

`--message` is not optional in practice: the script does not know this
session's own attribution trailer, so build the message yourself (this
repo's usual commit message plus the session's trailers) and pass it
every time real work is being published. Add `--customer NAME` when the
brief's frontmatter customer line is missing or wrong, and repeat
`--stripe-option "Label=none|primary|PATH"` (in display order) for an
order comparing more than one accent-stripe design - see `build_share.py
--help` for the exact syntax. `--slug` overrides the URL slug (default:
the order directory's own name, lowercased). `--no-wait` pushes and
returns immediately instead of polling the GitHub Actions run.

Exit codes:

| Exit | Meaning |
|---|---|
| 0 | published, or already up to date (nothing to push) |
| 1 | input error: the order is missing `cab.step`/`cab.json`/`voicing.json`, or `build_share.py` itself failed |
| 2 | `viewer.html`'s inline scripts are not yet allowed by MaximoCabs' CSP - see below, a real-browser fix, not one this tool can make safely |
| 3 | a local `npm test` or `npm run check` failed in MaximoCabs; nothing was pushed |
| 4 | the git push or the GitHub Actions deploy failed or timed out - the script prints which |

## Exit 2: the CSP hash is stale

This only happens after `viewer.html`'s own `<script type="importmap">`
or `<script type="module">` block changes (a template edit, not a normal
per-order run.) The tool refuses to guess a new hash - a wrong one would
silently break every order's page, stuck forever on "Loading your
cabinet..." with no fallback, since CSP blocks the whole script as one
unit. Fix it from a real browser, then re-run this tool:

1. `cd ~/ClaudeProjects/MaximoCabs && npm run build`
2. `npx wrangler pages dev dist` and open the order's `/share/<slug>/`
   page in a real browser (chrome-devtools MCP's `new_page`/
   `navigate_page` work for this).
3. Read the exact hash from the "Executing inline script violates CSP"
   console message (`list_console_messages`) - never compute it by hand.
4. Add it to **both** `public/_headers` and `src/lib/security-headers.ts`
   (a CI test enforces they stay identical); `npm test && npm run check`
   to confirm.
5. Re-run `publish.py`.

## Relationship to /speaker-cab

Phase 6 step 4 of the `speaker-cab` skill calls this tool for every new
order - that is what makes it automatic; no separate ask is needed.
Invoke it directly (this skill) to republish an existing order without
re-running the whole order workflow: after fixing a bug in `viewer.html`
or `build_share.py`, after adding a comparison stripe design like
`cherry-maple-stripe/`, or after any other change to files under an
order's directory that the live page should reflect.
