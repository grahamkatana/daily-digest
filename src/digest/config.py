"""Everything you'd want to tune: search terms, topic filter, venues, feeds, secrets.

Queries, keyword groups, venues, and RSS feeds live as Markdown files under
config/ at the repo root — edit those, no code changes needed.
"""

import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"


def _load_dotenv() -> None:
    """Minimal .env loader so local runs pick up secrets without extra deps."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

# Papers must be from this year or later. Stays current automatically instead
# of going stale — override with DIGEST_YEARS_BACK if 2 years isn't right.
YEARS_BACK = int(os.getenv("DIGEST_YEARS_BACK", "2"))
STRICT_YEAR = date.today().year - YEARS_BACK
MIN_YEAR = STRICT_YEAR - 2  # broader fetch window for sources that support a range


def _bullets(block: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^-\s+(.+)$", block, re.MULTILINE)]


def _parse_keywords_md() -> tuple[list[str], list[list[str]]]:
    """'## Search Queries' bullets -> QUERIES; each '###' under
    '## Topic Filter' -> one keyword group."""
    text = (CONFIG_DIR / "Keywords.md").read_text(encoding="utf-8")

    queries: list[str] = []
    groups: list[list[str]] = []
    for section in re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]:
        title, _, body = section.partition("\n")
        if title.strip() == "Search Queries":
            queries = _bullets(body)
        elif title.strip() == "Topic Filter":
            for sub in re.split(r"^###\s+", body, flags=re.MULTILINE)[1:]:
                _, _, subbody = sub.partition("\n")
                kws = _bullets(subbody)
                if kws:
                    groups.append(kws)
    return queries, groups


def _parse_venues_md() -> set[str]:
    text = (CONFIG_DIR / "Venues.md").read_text(encoding="utf-8")
    return {v.lower() for v in _bullets(text)}


def _parse_rss_md() -> dict[str, str]:
    """'- [Name](url)' bullets -> {Name: url}."""
    text = (CONFIG_DIR / "RSS.md").read_text(encoding="utf-8")
    return {
        m.group(1).strip(): m.group(2).strip()
        for m in re.finditer(r"^-\s+\[(.+?)\]\((.+?)\)\s*$", text, re.MULTILINE)
    }


# A paper must match at least one keyword from EVERY group in KEYWORD_GROUPS.
QUERIES, KEYWORD_GROUPS = _parse_keywords_md()
REPUTABLE_VENUES = _parse_venues_md()
RSS_FEEDS = _parse_rss_md()

HEADERS = {"User-Agent": "ResearchDigestBot/1.0 (personal research digest)"}

# Secrets / per-environment settings — set via .env locally, GitHub Actions secrets in CI.
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "graham_katana_research_digest_986712")
