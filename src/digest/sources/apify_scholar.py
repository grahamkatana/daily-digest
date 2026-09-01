"""Google Scholar via Apify's johnvc/google-scholar-lite-api actor (replaces Semantic Scholar)."""

import requests

from ..config import APIFY_API_TOKEN, APIFY_SCHOLAR_ACTOR, STRICT_YEAR
from ..paper import make_paper, matches_topic

RUN_SYNC_URL = f"https://api.apify.com/v2/acts/{APIFY_SCHOLAR_ACTOR}/run-sync-get-dataset-items"


def scrape(queries: list[str], max_per_search: int = 25) -> list[dict]:
    if not APIFY_API_TOKEN:
        print("  ⚠️  APIFY_API_TOKEN not set — skipping Google Scholar")
        return []

    print(f"  🎓 Google Scholar (Apify): {len(queries)} quer(y/ies)")
    try:
        resp = requests.post(
            RUN_SYNC_URL,
            params={"token": APIFY_API_TOKEN},
            json={
                "searchTerms": queries,
                "yearFrom": STRICT_YEAR,
                "maxResultsPerSearch": max_per_search,
            },
            timeout=180,
        )
        resp.raise_for_status()
        items = resp.json()
    except Exception as e:
        print(f"    ⚠️  Error: {e}")
        return []

    results = []
    for item in items:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        year = item.get("year") or 0
        info = item.get("publicationInfo", "")
        parts = [p.strip() for p in info.split(" - ")]
        authors = parts[0] if parts else ""
        venue = parts[-1] if len(parts) > 1 else ""
        url = item.get("link", "")

        if year and year >= STRICT_YEAR and matches_topic(title, snippet):
            results.append(make_paper("Google Scholar", title, authors, venue, year, snippet, url))
    return results
