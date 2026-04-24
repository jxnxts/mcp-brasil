"""Integration tests for ANTT."""

from __future__ import annotations

import httpx
import pytest
import respx
from fastmcp import Client

from mcp_brasil.data.antt import FEATURE_META
from mcp_brasil.data.antt.constants import ANTT_CKAN_BASE
from mcp_brasil.data.antt.server import mcp


def test_feature_meta() -> None:
    assert FEATURE_META.name == "antt"


@pytest.mark.asyncio
async def test_lists_tools() -> None:
    async with Client(mcp) as c:
        tools = await c.list_tools()
    assert {t.name for t in tools} >= {"listar_datasets_antt", "buscar_datasets_antt"}


@pytest.mark.asyncio
@respx.mock
async def test_buscar() -> None:
    respx.get(f"{ANTT_CKAN_BASE}/package_search").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "result": {
                    "count": 1,
                    "results": [
                        {
                            "name": "acidentes-rodovias",
                            "title": "Acidentes em rodovias",
                            "resources": [{"name": "acidentes-2024.csv"}],
                        }
                    ],
                },
            },
        )
    )
    async with Client(mcp) as c:
        r = await c.call_tool("buscar_datasets_antt", {"termo": "acidente"})
    data = getattr(r, "data", None) or str(r)
    assert "acidentes-rodovias" in data
