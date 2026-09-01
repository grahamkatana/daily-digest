"""Orchestrator: scrape all sources, filter to new papers, write a report, notify."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from .config import QUERIES, RSS_FEEDS
from .notify import send as notify
from .paper import dedupe
from .report import write_markdown
from .seen_store import save_seen, split_new
from .sources import apify_scholar, crossref, openalex, rss

ROOT = Path(__file__).resolve().parents[2]
DIGESTS_DIR = ROOT / "digests"


def run(force: bool = False, dry_run: bool = False) -> Path | None:
    all_papers: list[dict] = []
    for name, scraper, args in [
        ("OpenAlex", openalex.scrape, (QUERIES,)),
        ("CrossRef", crossref.scrape, (QUERIES,)),
        ("Google Scholar", apify_scholar.scrape, (QUERIES,)),
        ("RSS Feeds", rss.scrape, (RSS_FEEDS,)),
    ]:
        print(f"\n── {name} ───────────────────────────")
        papers = scraper(*args)
        print(f"   → {len(papers)} papers")
        all_papers.extend(papers)

    all_papers = dedupe(all_papers)
    new_papers, all_keys = split_new(all_papers)
    to_report = all_papers if force else new_papers

    print(f"\n✅ {len(all_papers)} unique papers, {len(new_papers)} new")

    if not to_report:
        print("Nothing new today.")
        if not dry_run:
            notify("Research Digest", "No new papers today.")
        save_seen(all_keys)
        return None

    DIGESTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d")
    md_path = DIGESTS_DIR / f"digest_{stamp}.md"
    write_markdown(to_report, md_path)
    write_markdown(to_report, DIGESTS_DIR / "latest.md")  # stable filename for polling/webhook use

    if not dry_run:
        titles = "\n".join(f"• {p['title']}" for p in to_report[:5])
        more = f"\n…and {len(to_report) - 5} more" if len(to_report) > 5 else ""
        notify(f"Research Digest — {len(to_report)} new paper(s)", f"{titles}{more}")

    save_seen(all_keys)
    return md_path


def _demo() -> None:
    """Self-check: paper.dedupe/matches_topic/extract_year behave as expected."""
    from .paper import dedupe, extract_year, matches_topic

    assert extract_year("Published 2026-03-01") == 2026
    assert extract_year("") is None
    assert matches_topic(
        "LLM code generation quality verification governance",
        "study of AI coding tools compliance",
    )
    assert not matches_topic("unrelated biology paper", "")
    papers = [
        {"title": "Same Paper!!"},
        {"title": "same paper"},
        {"title": "Different Paper"},
    ]
    assert len(dedupe(papers)) == 2
    print("self-check OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="include already-seen papers (for testing)")
    parser.add_argument("--dry-run", action="store_true", help="skip sending the ntfy notification")
    parser.add_argument("--selfcheck", action="store_true", help="run the internal self-check and exit")
    args = parser.parse_args()

    if args.selfcheck:
        _demo()
    else:
        run(force=args.force, dry_run=args.dry_run)
