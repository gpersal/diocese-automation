#!/usr/bin/env python3

"""
Scraper: CEC (Conferencia Episcopal de Colombia) - "Evangelio diario".

Fuente:
- RSS: https://www.cec.org.co/taxonomy/term/8097/feed
- Articulo diario: /evangelio-diario/<slug>

Salida:
- JSON con items por fecha (YYYY-MM-DD) incluyendo cita, evangelio segun, y contenido (HTML y texto).

Uso:
  python3 scripts/cec_evangelio_scraper.py --start-date 2026-02-07 --days-ahead 3 --out /tmp/cec.json
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import ssl

try:
    import certifi  # type: ignore
except Exception:  # pragma: no cover
    certifi = None

CEC_RSS_URL = "https://www.cec.org.co/taxonomy/term/8097/feed"


MONTHS_ES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


BOOK_ABBR = {
    "mt": ("Mateo", "San Mateo"),
    "mc": ("Marcos", "San Marcos"),
    "lc": ("Lucas", "San Lucas"),
    "jn": ("Juan", "San Juan"),
}


@dataclass(frozen=True)
class CECItem:
    iso_date: str
    title: str
    link: str
    citation_raw: str
    book_abbr: str
    book_name: str
    according_to: str
    content_html: str
    content_text: str


def _parse_iso(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def _http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "diocese-automation/1.0 (+https://github.com/)",
            "Accept": "*/*",
        },
    )
    # macOS Python installs sometimes lack a working system CA bundle; prefer certifi when present.
    ctx = None
    if certifi is not None:
        try:
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = None
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()


def _parse_rfc2822(dt: str) -> datetime:
    # Example: "Fri, 06 Feb 2026 23:00:00 +0000"
    return datetime.strptime(dt, "%a, %d %b %Y %H:%M:%S %z")


def _extract_target_date_from_title(title: str, year: int) -> Optional[str]:
    # Example:
    # "07 de Febrero | Lectura del Santo Evangelio según San Marcos Mc 6, 30-34"
    m = re.search(r"\b(\d{1,2})\s+de\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)\b", title)
    if not m:
        return None
    day = int(m.group(1))
    month_name = m.group(2).strip().casefold()
    month = MONTHS_ES.get(month_name)
    if not month:
        return None
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _extract_abbr_and_ref(title: str) -> tuple[str, str]:
    # Try to capture "Mt 5, 13-16" / "Mc 6, 30-34" etc.
    m = re.search(r"\b(Mt|Mc|Lc|Jn)\s+(\d+,\s*\d+(?:-\d+)?)\b", title)
    if not m:
        # Fallback: maybe without space
        m = re.search(r"\b(Mt|Mc|Lc|Jn)\s*(\d+,\s*\d+(?:-\d+)?)\b", title)
    if not m:
        return ("", "")
    return (m.group(1), f"{m.group(1)} {m.group(2)}")


def _extract_schema_text_div(html_bytes: bytes) -> str:
    # Extract inner HTML of <div property="schema:text"> ... </div>
    # Use regex for robustness (the page is Drupal; the block is stable in current HTML).
    text = html_bytes.decode("utf-8", errors="ignore")
    m = re.search(r'<div[^>]+property="schema:text"[^>]*>(.*?)</div>', text, re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    return m.group(1).strip()


def _html_to_text(block_html: str) -> str:
    # Minimal HTML to text, preserving line breaks.
    s = block_html
    s = re.sub(r"<\s*br\s*/?\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</\s*p\s*>", "\n\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<\s*p[^>]*>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s


def _infer_according_to(text: str) -> str:
    # Detect "según san Marcos" etc. in text.
    low = text.casefold()
    if "según san mateo" in low:
        return "San Mateo"
    if "según san marcos" in low:
        return "San Marcos"
    if "según san lucas" in low:
        return "San Lucas"
    if "según san juan" in low:
        return "San Juan"
    return ""


def _book_name_from_abbr(abbr: str) -> tuple[str, str]:
    if not abbr:
        return ("", "")
    key = abbr.strip().casefold()
    full = BOOK_ABBR.get(key)
    if not full:
        return ("", "")
    return full


def fetch_cec_items(start_iso: str, days_ahead: int) -> list[CECItem]:
    start = _parse_iso(start_iso)
    end = start + timedelta(days=days_ahead)

    rss_bytes = _http_get(CEC_RSS_URL)
    root = ET.fromstring(rss_bytes)

    channel = root.find("channel")
    if channel is None:
        # Some feeds use namespaces; fallback search.
        channel = root.find("{*}channel")
    if channel is None:
        raise RuntimeError("No se encontro <channel> en el RSS de CEC.")

    items: list[CECItem] = []
    for it in channel.findall("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        if not title or not link or not pub:
            continue

        pub_dt = _parse_rfc2822(pub)
        year = pub_dt.year
        target_iso = _extract_target_date_from_title(title, year)
        if not target_iso:
            continue
        target_date = _parse_iso(target_iso)
        if target_date < start or target_date > end:
            continue

        abbr, citation_raw = _extract_abbr_and_ref(title)
        book_name, according_to = _book_name_from_abbr(abbr)

        html_bytes = _http_get(link)
        content_html = _extract_schema_text_div(html_bytes)
        content_text = _html_to_text(content_html)

        # Prefer "segun san X" from content, because title might differ in formatting.
        according_to_from_text = _infer_according_to(content_text)
        if according_to_from_text:
            according_to = according_to_from_text

        items.append(
            CECItem(
                iso_date=target_iso,
                title=title,
                link=link,
                citation_raw=citation_raw,
                book_abbr=abbr,
                book_name=book_name,
                according_to=according_to,
                content_html=content_html,
                content_text=content_text,
            )
        )

    # Ensure stable order.
    items.sort(key=lambda x: x.iso_date)
    return items


def main() -> int:
    ap = argparse.ArgumentParser(description="Scraper CEC: Evangelio diario (RSS + HTML).")
    ap.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--days-ahead", type=int, default=3, help="Ventana (incluye start-date)")
    ap.add_argument("--out", default=None, help="Ruta JSON salida (default stdout)")
    args = ap.parse_args()

    items = fetch_cec_items(args.start_date, max(0, int(args.days_ahead)))
    payload = {
        "source": "cec",
        "rss": CEC_RSS_URL,
        "start_date": args.start_date,
        "days_ahead": int(args.days_ahead),
        "items": [
            {
                "date": it.iso_date,
                "title": it.title,
                "link": it.link,
                "citation_raw": it.citation_raw,
                "book_abbr": it.book_abbr,
                "book_name": it.book_name,
                "according_to": it.according_to,
                "content_html": it.content_html,
                "content_text": it.content_text,
            }
            for it in items
        ],
    }
    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
            f.write("\n")
    else:
        sys.stdout.write(out + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
