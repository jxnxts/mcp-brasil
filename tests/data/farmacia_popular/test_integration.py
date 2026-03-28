"""Integration tests for the Farmácia Popular feature using fastmcp.Client.

These tests verify the full pipeline: server -> tools -> client (mocked HTTP).
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_brasil.data.farmacia_popular.schemas import (
    FarmaciaEstabelecimento,
    Medicamento,
)
from mcp_brasil.data.farmacia_popular.server import mcp

CLIENT_MODULE = "mcp_brasil.data.farmacia_popular.client"


class TestToolsRegistered:
    @pytest.mark.asyncio
    async def test_all_6_tools_registered(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            names = {t.name for t in tool_list}
            expected = {
                "buscar_farmacias",
                "listar_medicamentos",
                "verificar_medicamento",
                "buscar_por_indicacao",
                "estatisticas_programa",
                "verificar_elegibilidade",
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
    async def test_buscar_farmacias_e2e(self) -> None:
        mock_data = [
            FarmaciaEstabelecimento(
                codigo_cnes="3456789",
                nome_fantasia="Farmácia Central",
                endereco="Rua das Flores, 100",
            )
        ]
        with patch(
            f"{CLIENT_MODULE}.buscar_farmacias",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("buscar_farmacias", {"codigo_municipio": "355030"})
                assert "Farmácia Central" in result.data

    @pytest.mark.asyncio
    async def test_listar_medicamentos_e2e(self) -> None:
        mock_data = [
            Medicamento(
                nome="Losartana",
                principio_ativo="Losartana Potássica",
                apresentacao="Comprimido 50mg",
                indicacao="Hipertensão",
            )
        ]
        with patch(f"{CLIENT_MODULE}.listar_medicamentos", return_value=mock_data):
            async with Client(mcp) as c:
                result = await c.call_tool("listar_medicamentos", {})
                assert "Losartana" in result.data

    @pytest.mark.asyncio
    async def test_verificar_medicamento_e2e(self) -> None:
        mock_data = [
            Medicamento(
                nome="Losartana",
                principio_ativo="Losartana Potássica",
                apresentacao="Comprimido 50mg",
                indicacao="Hipertensão",
            )
        ]
        with patch(f"{CLIENT_MODULE}.buscar_medicamento_por_nome", return_value=mock_data):
            async with Client(mcp) as c:
                result = await c.call_tool("verificar_medicamento", {"nome": "losartana"})
                assert "Losartana" in result.data

    @pytest.mark.asyncio
    async def test_buscar_por_indicacao_e2e(self) -> None:
        mock_data = [
            Medicamento(
                nome="Metformina 500mg",
                principio_ativo="Cloridrato de Metformina",
                apresentacao="Comprimido 500mg",
                indicacao="Diabetes",
            )
        ]
        with patch(f"{CLIENT_MODULE}.buscar_por_indicacao", return_value=mock_data):
            async with Client(mcp) as c:
                result = await c.call_tool("buscar_por_indicacao", {"indicacao": "diabetes"})
                assert "Diabetes" in result.data

    @pytest.mark.asyncio
    async def test_verificar_elegibilidade_e2e(self) -> None:
        async with Client(mcp) as c:
            result = await c.call_tool("verificar_elegibilidade", {})
            assert "Requisitos" in result.data
            assert "CPF" in result.data

    @pytest.mark.asyncio
    async def test_buscar_farmacias_empty(self) -> None:
        with patch(
            f"{CLIENT_MODULE}.buscar_farmacias",
            new_callable=AsyncMock,
            return_value=[],
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("buscar_farmacias", {})
                assert "Nenhuma farmácia" in result.data
