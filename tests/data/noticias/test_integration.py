"""Integration tests for noticias."""

from __future__ import annotations

import httpx
import pytest
import respx
from fastmcp import Client

from mcp_brasil.data.noticias import FEATURE_META
from mcp_brasil.data.noticias.constants import TODAS_FONTES
from mcp_brasil.data.noticias.server import mcp


def test_feature_meta() -> None:
    assert FEATURE_META.name == "noticias"


@pytest.mark.asyncio
async def test_lists_tools() -> None:
    async with Client(mcp) as c:
        tools = await c.list_tools()
    assert {t.name for t in tools} >= {"listar_fontes", "ultimas_noticias", "resumo_politica"}


@pytest.mark.asyncio
async def test_listar_fontes_offline() -> None:
    async with Client(mcp) as c:
        r = await c.call_tool("listar_fontes", {})
    data = getattr(r, "data", None) or str(r)
    assert "camara_ultimas" in data
    assert "senado_ultimas" in data


_RSS_FIXTURE = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>Test</title>
<item>
  <title>Congresso aprova medida provisória</title>
  <link>https://example.com/1</link>
  <pubDate>Fri, 24 Apr 2026 10:00:00 -0300</pubDate>
  <description>Votação unânime no plenário</description>
</item>
<item>
  <title>Reforma tributária avança</title>
  <link>https://example.com/2</link>
  <pubDate>Fri, 24 Apr 2026 09:00:00 -0300</pubDate>
  <description>Relator apresenta parecer</description>
</item>
</channel>
</rss>"""


@pytest.mark.asyncio
@respx.mock
async def test_ultimas_noticias_parses_rss() -> None:
    url = TODAS_FONTES["camara_ultimas"]
    respx.get(url).mock(return_value=httpx.Response(200, text=_RSS_FIXTURE))
    async with Client(mcp) as c:
        r = await c.call_tool("ultimas_noticias", {"fonte": "camara_ultimas"})
    data = getattr(r, "data", None) or str(r)
    assert "Congresso aprova" in data
    assert "Reforma tributária" in data


@pytest.mark.asyncio
@respx.mock
async def test_buscar_noticias_filtra() -> None:
    url = TODAS_FONTES["camara_ultimas"]
    respx.get(url).mock(return_value=httpx.Response(200, text=_RSS_FIXTURE))
    async with Client(mcp) as c:
        r = await c.call_tool(
            "buscar_noticias", {"fonte": "camara_ultimas", "termo": "tributária"}
        )
    data = getattr(r, "data", None) or str(r)
    assert "Reforma tributária" in data
    assert "medida provisória" not in data


@pytest.mark.asyncio
async def test_fonte_invalida() -> None:
    async with Client(mcp) as c:
        r = await c.call_tool("ultimas_noticias", {"fonte": "inexistente"})
    data = getattr(r, "data", None) or str(r)
    assert "não registrada" in data
