"""Tracks which papers were already reported so the digest only surfaces new ones."""

import json
import re
from pathlib import Path

STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "seen.json"


def _key(paper: dict) -> str:
    return re.sub(r"\W+", "", paper.get("title", "").lower())[:80]


def load_seen() -> set[str]:
    if STORE_PATH.exists():
        return set(json.loads(STORE_PATH.read_text(encoding="utf-8")))
    return set()


def save_seen(keys: set[str]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(sorted(keys), indent=2), encoding="utf-8")


def split_new(papers: list[dict]) -> tuple[list[dict], set[str]]:
    """Returns (papers not seen before, full set of keys seen as of this run)."""
    seen = load_seen()
    all_keys = set(seen)
    new = []
    for p in papers:
        key = _key(p)
        if not key:
            continue
        if key not in seen:
            new.append(p)
        all_keys.add(key)
    return new, all_keys
