"""Shared helpers every source uses to build/filter/dedupe paper records."""

import re

from bs4 import BeautifulSoup

from .config import KEYWORD_GROUPS, REPUTABLE_VENUES


def clean(text: str) -> str:
    stripped = BeautifulSoup(text or "", "html.parser").get_text()
    return re.sub(r"\s+", " ", stripped).strip()


def normalise(text: str) -> str:
    return clean(text).lower()


def matches_topic(title: str, abstract: str = "") -> bool:
    combined = normalise(title + " " + abstract)
    return all(any(kw in combined for kw in group) for group in KEYWORD_GROUPS)


def extract_year(val) -> int | None:
    if not val:
        return None
    match = re.search(r"(20\d{2})", str(val))
    return int(match.group(1)) if match else None


def is_reputable_venue(venue: str) -> bool:
    v = venue.lower()
    for rv in REPUTABLE_VENUES:
        # short acronyms (icse, fse, msr...) need word boundaries or they'd
        # match inside unrelated words like "phase" or "database"
        if len(rv) <= 6 and rv.isalpha():
            if re.search(rf"\b{re.escape(rv)}\b", v):
                return True
        elif rv in v:
            return True
    return False


def make_paper(source, title, authors, venue, year, abstract, url) -> dict:
    abstract_clean = clean(abstract)
    return {
        "source": source,
        "title": clean(title),
        "authors": clean(authors),
        "venue": clean(venue),
        "year": str(year) if year else "",
        "abstract": abstract_clean[:500] + ("…" if len(abstract_clean) > 500 else ""),
        "url": url or "",
    }


def dedupe(papers: list[dict]) -> list[dict]:
    seen, out = set(), []
    for p in papers:
        key = re.sub(r"\W+", "", normalise(p.get("title", "")))[:80]
        if key and key not in seen:
            seen.add(key)
            out.append(p)
    return out
