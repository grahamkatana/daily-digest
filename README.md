# Daily Research Digest

Scrapes OpenAlex, CrossRef, journal RSS feeds, and Google Scholar (via Apify)
for new papers matching your topic, then pushes an [ntfy](https://ntfy.sh)
notification for anything not already sent. Runs daily at 07:30 SAST via
GitHub Actions.

## Layout

```
config/
  Keywords.md      search queries + topic filter groups
  Venues.md         reputable venue allowlist
  RSS.md            journal RSS feeds as [Name](url) bullets
src/digest/
  config.py        loads config/*.md; also holds the year window and secrets
  paper.py         shared helpers (clean, filter, dedupe, venue match)
  seen_store.py     tracks which papers were already reported (data/seen.json)
  notify.py         ntfy push
  report.py         Markdown report writer
  main.py           orchestrator + CLI
  sources/          one scraper per source (openalex, crossref, rss, apify_scholar)
digests/             generated Markdown reports, committed by the workflow
digests/latest.md    always overwritten with the newest digest — stable URL for scraping/webhooks
data/seen.json       dedupe state, committed by the workflow
.github/workflows/   the daily schedule
scripts/test_run.py  local trigger for immediate testing
docs/architecture.html  architecture diagram + GitHub Actions secrets guide
docs/architecture.md    same diagram as a Mermaid flowchart
```

## Retuning what it searches for

Everything editable without touching code lives under `config/` as plain
Markdown — `config.py` re-reads all three on every run:

- **`Keywords.md`** — search queries, and keyword groups under `## Topic Filter`
  (a paper must match at least one keyword from every group to be kept)
- **`Venues.md`** — reputable venues, one per line (lowercase substring match;
  short acronyms like `icse` are automatically matched as whole words)
- **`RSS.md`** — journal feeds as `- [Name](url)` bullets

The year window is code, not a file, but it's relative rather than a
hardcoded literal: `STRICT_YEAR` is always `current year − 2` (set
`DIGEST_YEARS_BACK` to change the offset), so it never goes stale.

## Setup

```
uv sync
cp .env.example .env   # already has your APIFY_API_TOKEN + NTFY_TOPIC filled in locally
```

Get notified: install the [ntfy app](https://ntfy.sh/app) (or open
`https://ntfy.sh/graham_katana_research_digest_986712` in a browser) and
subscribe to topic `graham_katana_research_digest_986712`.

## Run it now (local test)

```
uv run python scripts/test_run.py
```

This always sends a notification (bypassing the "already seen" filter), so
you can confirm scraping and ntfy delivery work immediately.

## Run it for real

```
uv run python -m digest.main
```

Only sends new papers, and updates `data/seen.json` so they aren't repeated
tomorrow.

## GitHub Actions setup

1. Push this repo to GitHub.
2. Add repo secrets (Settings → Secrets and variables → Actions):
   - `APIFY_API_TOKEN`
   - `NTFY_TOPIC` (optional — defaults to `graham_katana_research_digest_986712` if unset)
3. The workflow needs write access to commit `data/seen.json` and `digests/`
   back to the repo — this is already granted via `permissions: contents: write`
   in the workflow, but if your org restricts default token permissions,
   enable "Read and write permissions" under Settings → Actions → General.
4. Trigger a manual run from the Actions tab (`workflow_dispatch`) to test
   the schedule end-to-end before waiting for 07:30.

## Pulling the digest yourself (instead of / alongside ntfy)

Every run commits `digests/digest_YYYYMMDD.md` and overwrites
`digests/latest.md`, so once this is pushed to GitHub, the digest is a plain
file in the repo — no extra hosting needed. Fetch the latest one from:

```
https://raw.githubusercontent.com/<you>/<repo>/main/digests/latest.md
```

That's a stable URL you (or a webhook) can poll daily after the Action runs.
Sending it *to* a webhook automatically (instead of just being pollable) isn't
wired up yet — when you're ready for that, `notify.py` is the natural place to
add an HTTP POST of the same Markdown, right next to the ntfy call.

## Note on the Apify token

The Apify token lives in this repo's local `.env` (gitignored, not
committed). Since it was shared in plaintext at one point, consider rotating
it in the Apify console once this is set up.
