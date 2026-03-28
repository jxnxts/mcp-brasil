"""Integration tests for the composed compras server.

Verifies that sub-servers are mounted with correct namespacing.
"""

import pytest
from fastmcp import Client

from mcp_brasil.data.compras.server import mcp


class TestComposedServer:
    @pytest.mark.asyncio
    async def test_pncp_tools_namespaced(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            names = {t.name for t in tool_list}
            expected = {
                "pncp_buscar_contratacoes",
                "pncp_buscar_contratos",
                "pncp_buscar_atas",
                "pncp_consultar_fornecedor",
                "pncp_consultar_orgao",
                "pncp_buscar_contratacoes_abertas",
                "pncp_buscar_contratacoes_atualizadas",
                "pncp_buscar_contratos_atualizados",
                "pncp_buscar_atas_atualizadas",
                "pncp_consultar_contratacao_detalhe",
                "pncp_buscar_pca",
                "pncp_buscar_pca_atualizacao",
                "pncp_buscar_pca_usuario",
                "pncp_buscar_instrumentos_cobranca",
            }
            assert expected.issubset(names), f"Missing: {expected - names}"

    @pytest.mark.asyncio
    async def test_pncp_resources_namespaced(self) -> None:
        async with Client(mcp) as c:
            resources = await c.list_resources()
            uris = {str(r.uri) for r in resources}
            assert "data://pncp/modalidades" in uris, f"URIs: {uris}"

    @pytest.mark.asyncio
    async def test_pncp_prompts_namespaced(self) -> None:
        async with Client(mcp) as c:
            prompts = await c.list_prompts()
            names = {p.name for p in prompts}
            assert "pncp_investigar_fornecedor" in names, f"Prompts: {names}"

    @pytest.mark.asyncio
    async def test_dadosabertos_tools_namespaced(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            names = {t.name for t in tool_list}
            expected = {
                "dadosabertos_buscar_licitacoes",
                "dadosabertos_buscar_pregoes",
                "dadosabertos_buscar_dispensas",
                "dadosabertos_buscar_contratos",
                "dadosabertos_consultar_fornecedor",
                "dadosabertos_buscar_material_catmat",
                "dadosabertos_buscar_servico_catser",
                "dadosabertos_buscar_uasg",
            }
            assert expected.issubset(names), f"Missing: {expected - names}"

    @pytest.mark.asyncio
    async def test_total_tools_count(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            assert len(tool_list) == 29, f"Expected 29 tools, got {len(tool_list)}"
