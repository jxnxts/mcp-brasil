"""Tests for the Imunização HTTP client."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_brasil.data.imunizacao import client

HTTP_MODULE = "mcp_brasil.data.imunizacao.client"


# ---------------------------------------------------------------------------
# Elasticsearch — buscar_vacinacao_es
# ---------------------------------------------------------------------------


class TestBuscarVacinacaoEs:
    @pytest.mark.asyncio
    async def test_returns_parsed_records(self) -> None:
        mock_response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "paciente_endereco_nmMunicipio": "Teresina",
                            "estabelecimento_uf": "PI",
                            "vacina_nome": "Covid-19",
                            "vacina_descricao_dose": "1ª Dose",
                            "vacina_fabricante_nome": "AstraZeneca",
                            "paciente_idade": "45",
                            "paciente_enumSexoBiologico": "M",
                            "vacina_dataAplicacao": "2021-06-15",
                            "estabelecimento_razaoSocial": "UBS Centro",
                        }
                    }
                ],
            }
        }
        with patch(f"{HTTP_MODULE}.http_post", new_callable=AsyncMock, return_value=mock_response):
            records, total = await client.buscar_vacinacao_es(uf="PI", vacina="Covid-19")
        assert len(records) == 1
        assert records[0].vacina_nome == "Covid-19"
        assert records[0].uf == "PI"
        assert records[0].municipio == "Teresina"
        assert total == 1

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_response = {"hits": {"total": {"value": 0}, "hits": []}}
        with patch(f"{HTTP_MODULE}.http_post", new_callable=AsyncMock, return_value=mock_response):
            records, total = await client.buscar_vacinacao_es(uf="XX")
        assert records == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_builds_query_with_filters(self) -> None:
        mock_response = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_post = AsyncMock(return_value=mock_response)
        with patch(f"{HTTP_MODULE}.http_post", mock_post):
            await client.buscar_vacinacao_es(
                uf="SP", municipio="São Paulo", vacina="Influenza", dose="Dose Única"
            )
        call_args = mock_post.call_args
        body = call_args.kwargs.get("json_body") or call_args[1].get("json_body")
        must = body["query"]["bool"]["must"]
        assert len(must) == 4


# ---------------------------------------------------------------------------
# Elasticsearch — agregar_vacinacao_es
# ---------------------------------------------------------------------------


class TestAgregarVacinacaoEs:
    @pytest.mark.asyncio
    async def test_returns_aggregations(self) -> None:
        mock_response = {
            "aggregations": {
                "por_campo": {
                    "buckets": [
                        {"key": "Covid-19", "doc_count": 50000},
                        {"key": "Influenza", "doc_count": 30000},
                    ]
                }
            }
        }
        with patch(f"{HTTP_MODULE}.http_post", new_callable=AsyncMock, return_value=mock_response):
            result = await client.agregar_vacinacao_es(uf="PI")
        assert len(result) == 2
        assert result[0].nome == "Covid-19"
        assert result[0].total == 50000

    @pytest.mark.asyncio
    async def test_empty_aggregation(self) -> None:
        mock_response = {"aggregations": {"por_campo": {"buckets": []}}}
        with patch(f"{HTTP_MODULE}.http_post", new_callable=AsyncMock, return_value=mock_response):
            result = await client.agregar_vacinacao_es()
        assert result == []


# ---------------------------------------------------------------------------
# CKAN — buscar_datasets_pni
# ---------------------------------------------------------------------------


class TestBuscarDatasetsPni:
    @pytest.mark.asyncio
    async def test_returns_datasets(self) -> None:
        mock_response = {
            "result": {
                "count": 1,
                "results": [
                    {
                        "id": "abc-123",
                        "name": "doses-pni-2025",
                        "title": "Doses PNI 2025",
                        "notes": "Doses aplicadas",
                        "organization": {"title": "MS"},
                        "resources": [{"id": "r1"}],
                        "metadata_modified": "2025-01-01",
                    }
                ],
            }
        }
        with patch(f"{HTTP_MODULE}.http_get", new_callable=AsyncMock, return_value=mock_response):
            datasets, total = await client.buscar_datasets_pni("PNI")
        assert len(datasets) == 1
        assert datasets[0].nome == "doses-pni-2025"
        assert total == 1

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_response = {"result": {"count": 0, "results": []}}
        with patch(f"{HTTP_MODULE}.http_get", new_callable=AsyncMock, return_value=mock_response):
            datasets, _total = await client.buscar_datasets_pni("inexistente")
        assert datasets == []


# ---------------------------------------------------------------------------
# CKAN — detalhar_dataset_pni
# ---------------------------------------------------------------------------


class TestDetalharDatasetPni:
    @pytest.mark.asyncio
    async def test_returns_dataset_and_resources(self) -> None:
        mock_response = {
            "result": {
                "id": "abc-123",
                "name": "doses-pni-2025",
                "title": "Doses PNI 2025",
                "organization": {"title": "MS"},
                "resources": [
                    {"id": "r1", "name": "dados.csv", "format": "CSV", "url": "https://ex.com"}
                ],
            }
        }
        with patch(f"{HTTP_MODULE}.http_get", new_callable=AsyncMock, return_value=mock_response):
            ds, recursos = await client.detalhar_dataset_pni("doses-pni-2025")
        assert ds is not None
        assert ds.nome == "doses-pni-2025"
        assert len(recursos) == 1
        assert recursos[0].formato == "CSV"

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        mock_response = {"result": {}}
        with patch(f"{HTTP_MODULE}.http_get", new_callable=AsyncMock, return_value=mock_response):
            ds, recursos = await client.detalhar_dataset_pni("inexistente")
        assert ds is None
        assert recursos == []


# ---------------------------------------------------------------------------
# CKAN — consultar_datastore_pni
# ---------------------------------------------------------------------------


class TestConsultarDatastorePni:
    @pytest.mark.asyncio
    async def test_returns_records(self) -> None:
        mock_response = {
            "result": {
                "total": 100,
                "records": [{"_id": 1, "uf": "SP", "vacina": "BCG", "doses": 5000}],
            }
        }
        with patch(f"{HTTP_MODULE}.http_get", new_callable=AsyncMock, return_value=mock_response):
            records, total = await client.consultar_datastore_pni("r1")
        assert len(records) == 1
        assert "_id" not in records[0]
        assert records[0]["uf"] == "SP"
        assert total == 100

    @pytest.mark.asyncio
    async def test_empty_datastore(self) -> None:
        mock_response = {"result": {"total": 0, "records": []}}
        with patch(f"{HTTP_MODULE}.http_get", new_callable=AsyncMock, return_value=mock_response):
            records, _total = await client.consultar_datastore_pni("r1")
        assert records == []


# ---------------------------------------------------------------------------
# Static reference helpers
# ---------------------------------------------------------------------------


class TestListarTodasVacinas:
    def test_returns_all_vaccines(self) -> None:
        vacinas = client.listar_todas_vacinas()
        assert len(vacinas) > 10
        siglas = {v["sigla"] for v in vacinas}
        assert "BCG" in siglas
        assert "Penta" in siglas

    def test_each_has_grupo(self) -> None:
        for v in client.listar_todas_vacinas():
            assert "grupo" in v


class TestBuscarVacinaPorSigla:
    def test_finds_bcg(self) -> None:
        result = client.buscar_vacina_por_sigla("BCG")
        assert result is not None
        assert result["nome"] == "BCG"

    def test_case_insensitive(self) -> None:
        result = client.buscar_vacina_por_sigla("bcg")
        assert result is not None

    def test_not_found(self) -> None:
        result = client.buscar_vacina_por_sigla("INEXISTENTE")
        assert result is None


class TestBuscarVacinaPorNome:
    def test_finds_by_partial_name(self) -> None:
        result = client.buscar_vacina_por_nome("hepatite")
        assert len(result) >= 2  # HepB + HepA

    def test_finds_by_sigla(self) -> None:
        result = client.buscar_vacina_por_nome("BCG")
        assert len(result) >= 1

    def test_not_found(self) -> None:
        result = client.buscar_vacina_por_nome("xyzinexistente")
        assert result == []
