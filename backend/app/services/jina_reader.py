"""Jina AI Reader integration.

Reader turns any public URL into clean, LLM-friendly markdown. Voltana uses it
to enrich real charger/EV data: pull a charger-locator or spec-sheet page and
extract stations/connectors/prices that aren't available through any open API.

Docs: https://jina.ai/reader
"""

import httpx
from typing import Optional

from app.core.config import settings

READER_URL = "https://r.jina.ai/"


class JinaReaderError(Exception):
    pass


def fetch_url_as_markdown(
    url: str,
    *,
    target_selector: Optional[str] = None,
    timeout_s: float = 45.0,
) -> str:
    """Fetch a public URL and return its content as clean markdown.

    Optionally pass `target_selector` (a CSS selector) to only keep that part
    of the page, which reduces noise when scraping long locator pages.
    """
    if not settings.JINA_API_KEY:
        raise JinaReaderError("JINA_API_KEY is not configured")

    # The Reader endpoint is https://r.jina.ai/<target-url>
    reader_target = f"{READER_URL}{url}"
    headers = {
        "Authorization": f"Bearer {settings.JINA_API_KEY}",
        "X-Return-Format": "markdown",
        "User-Agent": "VoltanaDev/1.0 (EV charger data enrichment)",
    }
    if target_selector:
        headers["X-Target-Selector"] = target_selector

    try:
        resp = httpx.get(reader_target, headers=headers, timeout=timeout_s, follow_redirects=True)
    except httpx.HTTPError as e:
        raise JinaReaderError(f"Jina Reader request failed: {e}") from e

    if resp.status_code != 200:
        raise JinaReaderError(f"Jina Reader returned HTTP {resp.status_code}: {resp.text[:300]}")

    return resp.text


def extract_rows_from_markdown(markdown: str) -> list[dict]:
    """Best-effort parse of a markdown table (as returned by Reader) into rows.

    Charger locator pages usually come back as one big markdown table with
    columns like name / address / city / connector. We return each row as a
    dict keyed by the header text (lowercased, spaces -> underscores).
    """
    rows: list[dict] = []
    lines = [ln.strip() for ln in markdown.splitlines()]
    header_idx = None

    for i, ln in enumerate(lines):
        if ln.startswith("|") and "-" not in ln and header_idx is None:
            header_idx = i
            headers = [h.strip() for h in ln.strip("|").split("|")]
            # Normalise keys
            headers = [h.lower().replace(" ", "_").replace("#", "no") for h in headers]
            # The next non-empty line should be the separator; rows follow.
            continue
        if header_idx is not None and i > header_idx and ln.startswith("|") and "-" not in ln:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) != len(headers):
                continue
            rows.append(dict(zip(headers, cells)))

    return rows
