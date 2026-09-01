# Ingesting the digest

Everything below reads the public repo directly — no auth, no extra service.

## Latest digest only

```
https://raw.githubusercontent.com/grahamkatana/daily-digest/main/digests/latest.md
```

Overwritten every run, so this is the one URL to poll if you just want
"what's new today."

## A specific date

```
https://raw.githubusercontent.com/grahamkatana/daily-digest/main/digests/digest_YYYYMMDD.md
```

## Discover all dated files (no need to guess dates)

```
https://api.github.com/repos/grahamkatana/daily-digest/contents/digests
```

Returns JSON, one entry per file, each with a `download_url` pointing at the
raw Markdown.

## Whole archive at once

```
git clone https://github.com/grahamkatana/daily-digest.git
```

Files land in `digests/`, full history via `git log`.

## Not built yet

Auto-POSTing the digest *to* a webhook on every run (push instead of pull).
`src/digest/notify.py` is the intended place to add that — right next to the
existing ntfy call.
