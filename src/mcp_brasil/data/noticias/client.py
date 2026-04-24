"""RSS parsing client for noticias feature.

Uses stdlib xml.etree — no external dep needed.
"""

from __future__ import annotations

import logging
from typing import Any
from xml.etree import ElementTree as ET

import httpx

from mcp_brasil.exceptions import HttpClientError
from mcp_brasil.settings import USER_AGENT

from .constants import TODAS_FONTES

logger = logging.getLogger(__name__)


async def fetch_feed(fonte: str) -> list[dict[str, Any]]:
    """Busca um feed RSS e retorna itens parseados (title, link, pubDate, description)."""
    url = TODAS_FONTES.get(fonte)
    if not url:
        raise HttpClientError(f"Fonte '{fonte}' não registrada.")
    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=15.0, headers={"User-Agent": USER_AGENT}
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            body = resp.text
    except Exception as exc:
        raise HttpClientError(f"RSS {fonte} falhou: {exc}") from exc
    return _parse_rss(body)


def _parse_rss(xml_text: str) -> list[dict[str, Any]]:
    """Parse XML RSS 2.0 e Atom, retorna lista de itens normalizados."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    items: list[dict[str, Any]] = []
    # RSS 2.0
    for item in root.iter("item"):
        items.append(
            {
                "title": _text(item.find("title")),
                "link": _text(item.find("link")),
                "pubDate": _text(item.find("pubDate")),
                "description": _text(item.find("description")),
                "author": _text(item.find("{http://purl.org/dc/elements/1.1/}creator"))
                or _text(item.find("author")),
                "category": _text(item.find("category")),
            }
        )
    # Atom
    if not items:
        ns = "{http://www.w3.org/2005/Atom}"
        for entry in root.iter(f"{ns}entry"):
            link_el = entry.find(f"{ns}link")
            items.append(
                {
                    "title": _text(entry.find(f"{ns}title")),
                    "link": link_el.get("href") if link_el is not None else "",
                    "pubDate": _text(entry.find(f"{ns}updated"))
                    or _text(entry.find(f"{ns}published")),
                    "description": _text(entry.find(f"{ns}summary")),
                    "author": _text(entry.find(f"{ns}author/{ns}name")),
                    "category": "",
                }
            )
    return items


def _text(el: Any) -> str:
    if el is None:
        return ""
    return (el.text or "").strip()
