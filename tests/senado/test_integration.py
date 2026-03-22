"""Integration tests for the Senado feature using fastmcp.Client.

These tests verify the full pipeline: server → tools → client (mocked HTTP).
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_brasil.senado.schemas import (
    ComissaoResumo,
    MateriaResumo,
    SenadorDetalhe,
    SenadorResumo,
)
from mcp_brasil.senado.server import mcp

CLIENT_MODULE = "mcp_brasil.senado.client"


class TestToolsRegistered:
    @pytest.mark.asyncio
    async def test_all_22_tools_registered(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            names = {t.name for t in tool_list}
            expected = {
                # Senadores (4)
                "listar_senadores",
                "buscar_senador",
                "buscar_senador_por_nome",
                "votacoes_senador",
                # Matérias (5)
                "buscar_materia",
                "detalhe_materia",
                "consultar_tramitacao_materia",
                "textos_materia",
                "votos_materia",
                # Votações (3)
                "listar_votacoes",
                "detalhe_votacao",
                "votacoes_recentes",
                # Comissões (4)
                "listar_comissoes",
                "detalhe_comissao",
                "membros_comissao",
                "reunioes_comissao",
                # Agenda (2)
                "agenda_plenario",
                "agenda_comissoes",
                # Auxiliares (4)
                "legislatura_atual",
                "tipos_materia",
                "partidos_senado",
                "ufs_senado",
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
    async def test_all_3_resources_registered(self) -> None:
        async with Client(mcp) as c:
            resources = await c.list_resources()
            uris = {str(r.uri) for r in resources}
            expected = {
                "data://tipos-materia",
                "data://info-api",
                "data://comissoes-permanentes",
            }
            assert expected.issubset(uris), f"Missing: {expected - uris}"


class TestPromptsRegistered:
    @pytest.mark.asyncio
    async def test_all_3_prompts_registered(self) -> None:
        async with Client(mcp) as c:
            prompts = await c.list_prompts()
            names = {p.name for p in prompts}
            expected = {"acompanhar_materia", "perfil_senador", "analise_votacao_senado"}
            assert expected.issubset(names), f"Missing: {expected - names}"


class TestToolExecution:
    @pytest.mark.asyncio
    async def test_listar_senadores_e2e(self) -> None:
        mock_data = [SenadorResumo(codigo="5012", nome="Senador E2E", partido="PT", uf="SP")]
        with patch(
            f"{CLIENT_MODULE}.listar_senadores",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("listar_senadores", {})
                assert "Senador E2E" in result.data

    @pytest.mark.asyncio
    async def test_buscar_senador_e2e(self) -> None:
        mock_data = SenadorDetalhe(
            codigo="5012",
            nome="Sen. E2E",
            nome_completo="Senador E2E da Silva",
            partido="PT",
            uf="SP",
        )
        with patch(
            f"{CLIENT_MODULE}.obter_senador",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("buscar_senador", {"codigo": "5012"})
                assert "Senador E2E da Silva" in result.data

    @pytest.mark.asyncio
    async def test_buscar_materia_e2e(self) -> None:
        mock_data = [
            MateriaResumo(
                sigla_tipo="PEC",
                numero="45",
                ano="2024",
                ementa="Matéria E2E",
            )
        ]
        with patch(
            f"{CLIENT_MODULE}.buscar_materias",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("buscar_materia", {"sigla_tipo": "PEC"})
                assert "Matéria E2E" in result.data

    @pytest.mark.asyncio
    async def test_listar_comissoes_e2e(self) -> None:
        mock_data = [
            ComissaoResumo(codigo="40", sigla="CCJ", nome="Comissão CCJ E2E", tipo="Permanente")
        ]
        with patch(
            f"{CLIENT_MODULE}.listar_comissoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("listar_comissoes", {})
                assert "CCJ" in result.data
