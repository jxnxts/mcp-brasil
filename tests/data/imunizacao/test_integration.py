"""Integration tests for the Imunização feature using fastmcp.Client."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_brasil.data.imunizacao.schemas import RegistroVacinacao
from mcp_brasil.data.imunizacao.server import mcp

CLIENT_MODULE = "mcp_brasil.data.imunizacao.client"


@pytest.fixture
def imunizacao_client() -> Client:
    return Client(mcp)


class TestToolsRegistered:
    @pytest.mark.asyncio
    async def test_all_10_tools_registered(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            tool_list = await imunizacao_client.list_tools()
            names = {t.name for t in tool_list}
            expected = {
                "buscar_vacinacao",
                "estatisticas_por_vacina",
                "estatisticas_por_faixa_etaria",
                "buscar_datasets_pni",
                "consultar_doses_dataset",
                "calendario_vacinacao",
                "listar_vacinas_sus",
                "consultar_vacina",
                "verificar_esquema_vacinal",
                "metas_cobertura",
            }
            assert expected.issubset(names), f"Missing: {expected - names}"
            assert len(tool_list) == 10

    @pytest.mark.asyncio
    async def test_tools_have_docstrings(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            tool_list = await imunizacao_client.list_tools()
            for tool in tool_list:
                assert tool.description, f"Tool {tool.name} has no description"


class TestResourcesRegistered:
    @pytest.mark.asyncio
    async def test_has_2_resources(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            resources = await imunizacao_client.list_resources()
            assert len(resources) == 2

    @pytest.mark.asyncio
    async def test_read_calendario(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            resources = await imunizacao_client.list_resources()
            cal_uri = next(r for r in resources if "calendario" in str(r.uri)).uri
            content = await imunizacao_client.read_resource(cal_uri)
            text = content[0].text if hasattr(content[0], "text") else str(content[0])
            assert "BCG" in text


class TestPromptsRegistered:
    @pytest.mark.asyncio
    async def test_has_1_prompt(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            prompts = await imunizacao_client.list_prompts()
            assert len(prompts) == 1
            assert prompts[0].name == "analise_cobertura_vacinal"


class TestToolExecution:
    @pytest.mark.asyncio
    async def test_buscar_vacinacao_e2e(self, imunizacao_client: Client) -> None:
        mock_data = [
            RegistroVacinacao(
                municipio="Teresina",
                uf="PI",
                vacina_nome="Covid-19",
                dose="1ª Dose",
            )
        ]
        with patch(
            f"{CLIENT_MODULE}.buscar_vacinacao_es",
            new_callable=AsyncMock,
            return_value=(mock_data, 1),
        ):
            async with imunizacao_client:
                result = await imunizacao_client.call_tool("buscar_vacinacao", {"uf": "PI"})
                assert "Covid-19" in result.data

    @pytest.mark.asyncio
    async def test_calendario_vacinacao_e2e(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            result = await imunizacao_client.call_tool("calendario_vacinacao", {})
            assert "BCG" in result.data
            assert "Calendário" in result.data

    @pytest.mark.asyncio
    async def test_consultar_vacina_e2e(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            result = await imunizacao_client.call_tool("consultar_vacina", {"nome": "BCG"})
            assert "Tuberculose" in result.data

    @pytest.mark.asyncio
    async def test_verificar_esquema_e2e(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            result = await imunizacao_client.call_tool("verificar_esquema_vacinal", {"idade": 4})
            assert "BCG" in result.data
            assert "Varicela" in result.data

    @pytest.mark.asyncio
    async def test_metas_cobertura_e2e(self, imunizacao_client: Client) -> None:
        async with imunizacao_client:
            result = await imunizacao_client.call_tool("metas_cobertura", {})
            assert "Metas" in result.data
