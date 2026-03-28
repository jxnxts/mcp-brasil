"""Integration tests for the SINESP/MJSP feature using fastmcp.Client."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_brasil.data.sinesp.schemas import DatasetCKAN
from mcp_brasil.data.sinesp.server import mcp

CLIENT_MODULE = "mcp_brasil.data.sinesp.client"


class TestToolsRegistered:
    @pytest.mark.asyncio
    async def test_all_6_tools_registered(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            names = {t.name for t in tool_list}
            expected = {
                "listar_datasets_mjsp",
                "buscar_datasets_mjsp",
                "detalhar_dataset_mjsp",
                "listar_organizacoes_mjsp",
                "listar_datasets_organizacao",
                "listar_datasets_grupo_seguranca",
            }
            assert expected.issubset(names), f"Missing: {expected - names}"

    @pytest.mark.asyncio
    async def test_tools_have_docstrings(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            for tool in tool_list:
                assert tool.description, f"Tool {tool.name} has no description"


class TestResourcesRegistered:
    @pytest.mark.asyncio
    async def test_all_2_resources_registered(self) -> None:
        async with Client(mcp) as c:
            resources = await c.list_resources()
            uris = {str(r.uri) for r in resources}
            expected = {
                "data://orgs-seguranca-mjsp",
                "data://grupos-tematicos-mjsp",
            }
            assert expected.issubset(uris), f"Missing: {expected - uris}"


class TestToolExecution:
    @pytest.mark.asyncio
    async def test_buscar_datasets_e2e(self) -> None:
        mock_data = [
            DatasetCKAN(
                id="abc",
                nome="sinesp",
                titulo="Ocorrências Criminais",
                organizacao="SENASP",
                num_recursos=5,
            )
        ]
        with patch(
            f"{CLIENT_MODULE}.buscar_datasets",
            new_callable=AsyncMock,
            return_value=(1, mock_data),
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("buscar_datasets_mjsp", {"texto": "segurança"})
                assert "Ocorrências Criminais" in result.data

    @pytest.mark.asyncio
    async def test_listar_datasets_e2e(self) -> None:
        with patch(
            f"{CLIENT_MODULE}.listar_datasets",
            new_callable=AsyncMock,
            return_value=["sinesp", "infopen"],
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("listar_datasets_mjsp", {})
                assert "sinesp" in result.data
                assert "infopen" in result.data
