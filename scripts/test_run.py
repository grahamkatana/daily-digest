"""Local trigger: run the digest right now and always send a notification,
so you can confirm scraping + ntfy work before trusting the schedule.

Usage:  uv run python scripts/test_run.py
"""

from digest.main import run

if __name__ == "__main__":
    path = run(force=True, dry_run=False)
    print(f"\nDone. {'Report: ' + str(path) if path else 'No matching papers found, but a notification was sent.'}")
