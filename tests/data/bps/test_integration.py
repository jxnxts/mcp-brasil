"""Integration tests for the BPS feature via fastmcp.Client."""

import pytest
from fastmcp import Client

from mcp_brasil.data.bps.server import mcp


@pytest.mark.asyncio
async def test_server_lists_tools() -> None:
    """All BPS tools should be registered."""
    async with Client(mcp) as c:
        tools = await c.list_tools()
    names = {t.name for t in tools}
    expected = {
        "consultar_precos_saude",
        "buscar_medicamento_bps",
        "buscar_catmat_bps",
    }
    assert expected.issubset(names), f"Missing tools: {expected - names}"
