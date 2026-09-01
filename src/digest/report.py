"""Renders the digest as Markdown."""

from datetime import date
from pathlib import Path


def write_markdown(papers: list[dict], filepath: Path) -> None:
    today = date.today().strftime("%d %B %Y")
    lines = [
        f"# Research Digest — {today}",
        "",
        f"**Papers found:** {len(papers)}",
        "",
        "---",
        "",
    ]

    by_source: dict[str, list] = {}
    for p in papers:
        by_source.setdefault(p["source"], []).append(p)

    for source, plist in sorted(by_source.items()):
        lines.append(f"## {source} ({len(plist)})")
        lines.append("")
        for i, p in enumerate(plist, 1):
            lines.append(f"### {i}. {p['title']}")
            if p.get("authors"):
                lines.append(f"**Authors:** {p['authors']}")
            if p.get("venue") and p["venue"] not in source:
                lines.append(f"**Venue:** {p['venue']}")
            if p.get("year"):
                lines.append(f"**Year:** {p['year']}")
            if p.get("abstract"):
                lines.append("")
                lines.append(f"> {p['abstract']}")
            if p.get("url"):
                lines.append("")
                lines.append(f"🔗 {p['url']}")
            lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"📝 Markdown saved: {filepath}")
