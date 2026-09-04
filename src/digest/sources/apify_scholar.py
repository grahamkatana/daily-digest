"""Google Scholar via Apify's johnvc/google-scholar-api actor, sorted by date (scisbd=2)
so genuinely new papers surface instead of the same relevance-ranked top results every day."""

import requests

from ..config import APIFY_API_TOKEN, STRICT_YEAR
from ..paper import extract_year, make_paper, matches_topic

ACTOR = "johnvc~google-scholar-api"
RUN_SYNC_URL = f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"


def scrape(queries: list[str], num_per_search: int = 20) -> list[dict]:
    if not APIFY_API_TOKEN:
        print("  ⚠️  APIFY_API_TOKEN not set — skipping Google Scholar")
        return []

    print(f"  🎓 Google Scholar (Apify): {len(queries)} quer(y/ies)")
    results = []
    for query in queries:
        try:
            resp = requests.post(
                RUN_SYNC_URL,
                params={"token": APIFY_API_TOKEN},
                json={
                    "mode": "search",
                    "q": query,
                    "as_ylo": STRICT_YEAR,
                    "scisbd": "2",  # sort by date instead of relevance/citations
                    "num": num_per_search,
                    "max_pages": 1,
                },
                timeout=60,
            )
            resp.raise_for_status()
            items = resp.json()
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
            continue

        for item in items:
            if item.get("error"):
                continue
            title = item.get("paper_title", "")
            snippet = item.get("snippet", "")
            pub_info = item.get("publication_info") or {}
            summary = pub_info.get("summary", "")
            authors = ", ".join(a.get("name", "") for a in pub_info.get("authors") or [])
            year = extract_year(summary) or extract_year(item.get("year"))
            url = item.get("link", "")

            if (not year or year >= STRICT_YEAR) and matches_topic(title, snippet):
                results.append(make_paper("Google Scholar", title, authors, summary, year or "", snippet, url))
    return results
