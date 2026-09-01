# Digest Pipeline

```mermaid
flowchart TD
    OA[OpenAlex]
    CR[CrossRef]
    RSS[RSS Feeds x11]
    GS[Google Scholar via Apify]

    CRON[GitHub Actions cron 07:30 SAST]
    TEST[test_run.py local --force]

    ORCH["main.run()\nmerge + dedupe(title)"]

    OA --> ORCH
    CR --> ORCH
    RSS --> ORCH
    GS --> ORCH
    CRON -->|daily| ORCH
    TEST -->|--force| ORCH

    ORCH --> DECIDE{title in\ndata/seen.json?}

    DECIDE -->|yes| DROP[discarded\nalready reported]
    DECIDE -->|no - new| REPORT["report.write_markdown()\n-> digests/digest_YYYYMMDD.md + latest.md"]
    DECIDE -->|no - new| NOTIFY["notify.send()\n-> ntfy.sh/...986712"]
    DROP -.->|--force includes these too| REPORT

    REPORT --> STORE["seen_store.save_seen()\n-> data/seen.json"]
    NOTIFY --> STORE

    STORE -.->|read at start of next run| DECIDE
    STORE -.->|CI only| COMMIT["git commit + push\ndata/seen.json + digests/"]
```

Every source funnels into `main.run()`, which dedupes by title and checks
each one against `data/seen.json`. Only new titles reach the report and the
ntfy push; already-seen ones are dropped — except when `test_run.py` runs
with `--force`, which reroutes them back in too, so you always get a
notification while testing. The state file is rewritten every run, which is
what tomorrow's check reads against.
