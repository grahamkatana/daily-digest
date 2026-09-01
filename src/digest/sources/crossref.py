"""CrossRef — DOI registry, broad journal coverage."""

import time

import requests

from ..config import HEADERS, STRICT_YEAR
from ..paper import is_reputable_venue, make_paper, matches_topic

BASE = "https://api.crossref.org/works"


def scrape(queries: list[str]) -> list[dict]:
    results = []

    for query in queries:
        print(f"  📖 CrossRef: '{query}'")
        try:
            resp = requests.get(
                BASE,
                params={
                    "query": query,
                    "rows": 20,
                    "filter": f"from-pub-date:{STRICT_YEAR},type:journal-article",
                    "select": "title,author,published,abstract,container-title,DOI,URL",
                    "mailto": "graykatanakenny@gmail.com",
                },
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
            items = resp.json().get("message", {}).get("items", [])
            for p in items:
                titles = p.get("title") or []
                title = titles[0] if titles else ""
                venue_list = p.get("container-title") or []
                venue = venue_list[0] if venue_list else ""
                abstract = p.get("abstract", "") or ""
                doi = p.get("DOI", "")
                url = p.get("URL", "") or (f"https://doi.org/{doi}" if doi else "")

                pub = p.get("published") or {}
                date_parts = pub.get("date-parts") or [[0]]
                year = date_parts[0][0] if date_parts[0] else 0

                authors = ", ".join(
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in (p.get("author") or [])[:6]
                )

                if year >= STRICT_YEAR and is_reputable_venue(venue) and matches_topic(title, abstract):
                    results.append(make_paper(f"CrossRef → {venue}", title, authors, venue, year, abstract, url))
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
        time.sleep(1)
    return results
