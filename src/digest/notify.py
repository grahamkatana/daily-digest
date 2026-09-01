"""Push notifications via ntfy.sh — no account, no keys, just a topic name."""

import requests

from .config import NTFY_TOPIC


def send(title: str, message: str, click_url: str | None = None) -> None:
    # ntfy's Title header must be ASCII/Latin-1 (HTTP header rules) — emoji go in the body instead.
    headers = {"Title": title.encode("ascii", "ignore").decode("ascii").strip() or "Research Digest"}
    if click_url:
        headers["Click"] = click_url
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=15,
        )
    except Exception as e:
        print(f"  ⚠️  ntfy send failed: {e}")
