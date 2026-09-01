"""Journal RSS feeds — no rate limits, catches items before they're indexed elsewhere."""

import time

import feedparser
from bs4 import BeautifulSoup

from ..config import STRICT_YEAR
from ..paper import extract_year, make_paper, matches_topic


def scrape(feeds: dict) -> list[dict]:
    results = []
    for name, url in feeds.items():
        print(f"  📡 RSS: {name}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                published = entry.get("published") or entry.get("updated") or entry.get("dc_date", "")
                link = entry.get("link", "")
                authors = entry.get("author", "") or ", ".join(
                    a.get("name", "") for a in entry.get("authors", []) if isinstance(a, dict)
                )
                year = extract_year(published)

                if year and year >= STRICT_YEAR and matches_topic(title, summary):
                    results.append(make_paper(
                        name, title, authors, name, year,
                        BeautifulSoup(summary, "html.parser").get_text(),
                        link,
                    ))
        except Exception as e:
            print(f"    ⚠️  RSS error: {e}")
        time.sleep(1)
    return results
