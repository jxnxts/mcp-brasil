"""Integration tests for B3."""

from __future__ import annotations

import httpx
import pytest
import respx
from fastmcp import Client

from mcp_brasil.data.b3 import FEATURE_META
from mcp_brasil.data.b3.constants import BRAPI_BASE
from mcp_brasil.data.b3.server import mcp


def test_feature_meta() -> None:
    assert FEATURE_META.name == "b3"


@pytest.mark.asyncio
async def test_lists_tools() -> None:
    async with Client(mcp) as c:
        tools = await c.list_tools()
    assert {t.name for t in tools} >= {"cotacao_ativo", "cotacoes_multiplas", "blue_chips"}


@pytest.mark.asyncio
@respx.mock
async def test_cotacao_parses() -> None:
    respx.get(f"{BRAPI_BASE}/quote/PETR4").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "symbol": "PETR4",
                        "longName": "Petrobras PN",
                        "regularMarketPrice": 40.0,
                        "regularMarketChangePercent": -1.5,
                        "regularMarketVolume": 10_000_000,
                        "regularMarketDayHigh": 41.0,
                        "regularMarketDayLow": 39.5,
                        "marketCap": 500_000_000_000,
                    }
                ]
            },
        )
    )
    async with Client(mcp) as c:
        r = await c.call_tool("cotacao_ativo", {"ticker": "PETR4"})
    data = getattr(r, "data", None) or str(r)
    assert "PETR4" in data
    assert "Petrobras" in data
