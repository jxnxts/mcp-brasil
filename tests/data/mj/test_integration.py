"""Integration tests for MJ."""

from __future__ import annotations

import httpx
import pytest
import respx
from fastmcp import Client

from mcp_brasil.data.mj import FEATURE_META
from mcp_brasil.data.mj.constants import MJ_CKAN_BASE
from mcp_brasil.data.mj.server import mcp


def test_feature_meta() -> None:
    assert FEATURE_META.name == "mj"


@pytest.mark.asyncio
async def test_lists_tools() -> None:
    async with Client(mcp) as c:
        tools = await c.list_tools()
    assert {t.name for t in tools} >= {
        "listar_datasets_mj",
        "buscar_datasets_mj",
        "detalhe_dataset_mj",
        "datasets_chave_mj",
    }


@pytest.mark.asyncio
@respx.mock
async def test_buscar_sinesp() -> None:
    respx.get(f"{MJ_CKAN_BASE}/package_search").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "result": {
                    "count": 1,
                    "results": [
                        {
                            "name": "sistema-nacional-de-estatisticas-de-seguranca-publica",
                            "title": "SINESP",
                            "resources": [{"name": "ocorrencias-2024.csv"}],
                        }
                    ],
                },
            },
        )
    )
    async with Client(mcp) as c:
        r = await c.call_tool("buscar_datasets_mj", {"termo": "sinesp"})
    data = getattr(r, "data", None) or str(r)
    assert "sistema-nacional" in data


@pytest.mark.asyncio
async def test_datasets_chave_offline() -> None:
    async with Client(mcp) as c:
        r = await c.call_tool("datasets_chave_mj", {})
    data = getattr(r, "data", None) or str(r)
    assert "SINESP" in data
    assert "INFOPEN" in data
