"""Tests for the Farmácia Popular HTTP client."""

import httpx
import pytest
import respx

from mcp_brasil.data.farmacia_popular import client
from mcp_brasil.data.farmacia_popular.constants import ESTABELECIMENTOS_URL

# ---------------------------------------------------------------------------
# buscar_farmacias (HTTP)
# ---------------------------------------------------------------------------


class TestBuscarFarmacias:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_pharmacies(self) -> None:
        respx.get(ESTABELECIMENTOS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "codigo_cnes": "3456789",
                        "nome_fantasia": "Farmácia Central",
                        "nome_razao_social": "Farmácia Central Ltda",
                        "tipo_gestao": "Privado",
                        "codigo_municipio": "355030",
                        "codigo_uf": "35",
                        "endereco": "Rua das Flores, 100",
                    }
                ],
            )
        )
        result = await client.buscar_farmacias(codigo_municipio="355030")
        assert len(result) == 1
        assert result[0].codigo_cnes == "3456789"
        assert result[0].nome_fantasia == "Farmácia Central"

    @pytest.mark.asyncio
    @respx.mock
    async def test_sends_tipo_farmacia_param(self) -> None:
        route = respx.get(ESTABELECIMENTOS_URL).mock(return_value=httpx.Response(200, json=[]))
        await client.buscar_farmacias(codigo_municipio="355030")
        req_url = str(route.calls[0].request.url)
        assert "codigo_tipo_estabelecimento=43" in req_url
        assert "status=1" in req_url
        assert "codigo_municipio=355030" in req_url

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(ESTABELECIMENTOS_URL).mock(return_value=httpx.Response(200, json=[]))
        result = await client.buscar_farmacias()
        assert result == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_limit_capped_at_max(self) -> None:
        route = respx.get(ESTABELECIMENTOS_URL).mock(return_value=httpx.Response(200, json=[]))
        await client.buscar_farmacias(limit=999)
        req_url = str(route.calls[0].request.url)
        assert "limit=100" in req_url


# ---------------------------------------------------------------------------
# listar_medicamentos (static)
# ---------------------------------------------------------------------------


class TestListarMedicamentos:
    def test_returns_all_medications(self) -> None:
        result = client.listar_medicamentos()
        assert len(result) >= 30  # At least 30 medications
        assert all(m.gratuito for m in result)

    def test_medications_have_all_fields(self) -> None:
        result = client.listar_medicamentos()
        for med in result:
            assert med.nome
            assert med.principio_ativo
            assert med.apresentacao
            assert med.indicacao


# ---------------------------------------------------------------------------
# buscar_medicamento_por_nome
# ---------------------------------------------------------------------------


class TestBuscarMedicamentoPorNome:
    def test_finds_by_name(self) -> None:
        result = client.buscar_medicamento_por_nome("losartana")
        assert len(result) >= 1
        assert any("Losartana" in m.nome for m in result)

    def test_finds_by_principio_ativo(self) -> None:
        result = client.buscar_medicamento_por_nome("metformina")
        assert len(result) >= 2  # 500mg, 500mg AP, 850mg

    def test_case_insensitive(self) -> None:
        result = client.buscar_medicamento_por_nome("LOSARTANA")
        assert len(result) >= 1

    def test_not_found(self) -> None:
        result = client.buscar_medicamento_por_nome("remédio_inexistente_xyz")
        assert result == []


# ---------------------------------------------------------------------------
# buscar_por_indicacao
# ---------------------------------------------------------------------------


class TestBuscarPorIndicacao:
    def test_finds_diabetes(self) -> None:
        result = client.buscar_por_indicacao("diabetes")
        assert len(result) >= 5  # Metformina variants + Glibenclamida + Insulins
        assert all(m.indicacao == "Diabetes" for m in result)

    def test_finds_hipertensao(self) -> None:
        result = client.buscar_por_indicacao("hipertensão")
        assert len(result) >= 7

    def test_not_found(self) -> None:
        result = client.buscar_por_indicacao("indicacao_inexistente")
        assert result == []


# ---------------------------------------------------------------------------
# obter_estatisticas
# ---------------------------------------------------------------------------


class TestObterEstatisticas:
    def test_returns_valid_stats(self) -> None:
        stats = client.obter_estatisticas()
        assert stats.total_medicamentos >= 30
        assert stats.total_indicacoes >= 9
        assert stats.todos_gratuitos is True
        assert len(stats.indicacoes) >= 9
        assert sum(stats.medicamentos_por_indicacao.values()) == stats.total_medicamentos


# ---------------------------------------------------------------------------
# _parse_farmacia
# ---------------------------------------------------------------------------


class TestParseFarmacia:
    def test_handles_missing_fields(self) -> None:
        result = client._parse_farmacia({})
        assert result.codigo_cnes == ""
        assert result.nome_fantasia is None

    def test_converts_numeric_codes(self) -> None:
        result = client._parse_farmacia({"codigo_cnes": 1234567, "codigo_municipio": 355030})
        assert result.codigo_cnes == "1234567"
        assert result.codigo_municipio == "355030"
