"""Integration tests for the Dados Abertos sub-feature using fastmcp.Client."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_brasil.data.compras.dadosabertos.schemas import (
    Licitacao,
    LicitacaoResultado,
)
from mcp_brasil.data.compras.dadosabertos.server import mcp

CLIENT_MODULE = "mcp_brasil.data.compras.dadosabertos.client"


class TestToolsRegistered:
    @pytest.mark.asyncio
    async def test_all_8_tools_registered(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            names = {t.name for t in tool_list}
            expected = {
                "buscar_licitacoes",
                "buscar_pregoes",
                "buscar_dispensas",
                "buscar_contratos",
                "consultar_fornecedor",
                "buscar_material_catmat",
                "buscar_servico_catser",
                "buscar_uasg",
            }
            assert expected.issubset(names), f"Missing: {expected - names}"

    @pytest.mark.asyncio
    async def test_tools_have_docstrings(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            for tool in tool_list:
                assert tool.description, f"Tool {tool.name} has no description"


class TestToolExecution:
    @pytest.mark.asyncio
    async def test_buscar_licitacoes_e2e(self) -> None:
        mock_data = LicitacaoResultado(
            total=1,
            licitacoes=[
                Licitacao(
                    uasg=154047,
                    nome_modalidade="PREGÃO",
                    objeto="Computadores",
                    valor_estimado_total=50000.0,
                ),
            ],
        )
        with patch(
            f"{CLIENT_MODULE}.buscar_licitacoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            async with Client(mcp) as c:
                result = await c.call_tool(
                    "buscar_licitacoes",
                    {
                        "data_publicacao_inicial": "2020-01-01",
                        "data_publicacao_final": "2020-01-31",
                    },
                )
                assert "Computadores" in result.data

    @pytest.mark.asyncio
    async def test_consultar_fornecedor_no_filter(self) -> None:
        async with Client(mcp) as c:
            result = await c.call_tool("consultar_fornecedor", {})
            assert "Informe pelo menos um filtro" in result.data
