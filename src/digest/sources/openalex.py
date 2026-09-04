"""OpenAlex — open scholarly graph, no API key needed."""

import time
from datetime import date, timedelta

import requests

from ..config import HEADERS, STRICT_YEAR
from ..paper import is_reputable_venue, make_paper, matches_topic

BASE = "https://api.openalex.org/works"
LOOKBACK_DAYS = 4  # catches papers newly indexed since the last run, not just newly published


def scrape(queries: list[str]) -> list[dict]:
    results = []
    cutoff = (date.today() - timedelta(days=LOOKBACK_DAYS)).isoformat()
    base_filter = f"publication_year:{STRICT_YEAR}-,type:journal-article,from_created_date:{cutoff}"

    for query in queries:
        print(f"  🔬 OpenAlex: '{query}'")
        try:
            resp = requests.get(
                BASE,
                params={
                    "search": query,
                    "filter": base_filter,
                    "per_page": 25,
                    "select": "title,authorships,publication_year,abstract_inverted_index,primary_location,doi,open_access",
                    "mailto": "graykatanakenny@gmail.com",
                },
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
            for p in resp.json().get("results", []):
                title = p.get("title", "") or ""
                year = p.get("publication_year") or 0
                doi = p.get("doi") or ""
                url = (p.get("open_access") or {}).get("oa_url", "") or (f"https://doi.org/{doi}" if doi else "")

                inv = p.get("abstract_inverted_index") or {}
                abstract = ""
                if inv:
                    words = sorted(
                        ((pos, word) for word, positions in inv.items() for pos in positions),
                        key=lambda x: x[0],
                    )
                    abstract = " ".join(w for _, w in words)

                loc = p.get("primary_location") or {}
                source = loc.get("source") or {}
                venue = source.get("display_name", "") or ""

                authors = ", ".join(
                    (a.get("author") or {}).get("display_name", "")
                    for a in (p.get("authorships") or [])[:6]
                )

                if year >= STRICT_YEAR and is_reputable_venue(venue) and matches_topic(title, abstract):
                    results.append(make_paper(f"OpenAlex → {venue}", title, authors, venue, year, abstract, url))
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
        time.sleep(1.5)
    return results
