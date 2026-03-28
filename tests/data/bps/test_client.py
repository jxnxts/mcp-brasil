"""Tests for the BPS HTTP client."""

import httpx
import pytest
import respx

from mcp_brasil.data.bps import client
from mcp_brasil.data.bps.constants import BPS_URL, FIELD_MUNICIPIO

SAMPLE_RECORD = {
    "ano_da_compra": "2025",
    "data_da_compra": "2025-01-02",
    "nome_da_instituicao": "MUNICIPIO DE DOURADOQUARA",
    "cnpj_da_instituicao": "18158261000108",
    FIELD_MUNICIPIO: "DOURADOQUARA",
    "uf_da_instituicao": "MG",
    "codigo_br": "267311",
    "descricao_catmat": "METOCLOPRAMIDA CLORIDRATO, DOSAGEM:4 MG/ML",
    "unidade_de_fornecimento": "FRASCO",
    "generico": "S",
    "anvisa": "1057101650018",
    "modalidade_da_compra": "Registro de Precos",
    "tipo_da_compra": "ADMINISTRATIVA",
    "fornecedor": "SOMA/MG PRODUTOS HOSPITALARES LTDA",
    "cnpj_do_fornecedor": "12927876000167",
    "fabricante": "BELFAR LTDA",
    "quantidade_itens_comprados": 100.0,
    "preco_unitario": 1.4659,
    "preco_total": 146.59,
}


class TestConsultarPrecos:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_records(self) -> None:
        respx.get(BPS_URL).mock(return_value=httpx.Response(200, json={"bps": [SAMPLE_RECORD]}))
        result = await client.consultar_precos(limite=10)
        assert result.total_retornado == 1
        assert len(result.registros) == 1
        r = result.registros[0]
        assert r.codigo_br == "267311"
        assert r.descricao_catmat == "METOCLOPRAMIDA CLORIDRATO, DOSAGEM:4 MG/ML"
        assert r.preco_unitario == 1.4659
        assert r.municipio_da_instituicao == "DOURADOQUARA"
        assert r.uf_da_instituicao == "MG"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(BPS_URL).mock(return_value=httpx.Response(200, json={"bps": []}))
        result = await client.consultar_precos()
        assert result.total_retornado == 0
        assert result.registros == []


class TestBuscarPorCatmat:
    @pytest.mark.asyncio
    @respx.mock
    async def test_filters_by_catmat(self) -> None:
        other = {**SAMPLE_RECORD, "codigo_br": "999999"}
        respx.get(BPS_URL).mock(
            return_value=httpx.Response(200, json={"bps": [SAMPLE_RECORD, other]})
        )
        result = await client.buscar_por_catmat("267311")
        assert result.total_retornado == 1
        assert result.registros[0].codigo_br == "267311"

    @pytest.mark.asyncio
    @respx.mock
    async def test_no_match(self) -> None:
        respx.get(BPS_URL).mock(return_value=httpx.Response(200, json={"bps": [SAMPLE_RECORD]}))
        result = await client.buscar_por_catmat("000000")
        assert result.total_retornado == 0


class TestBuscarPorDescricao:
    @pytest.mark.asyncio
    @respx.mock
    async def test_filters_by_description(self) -> None:
        respx.get(BPS_URL).mock(return_value=httpx.Response(200, json={"bps": [SAMPLE_RECORD]}))
        result = await client.buscar_por_descricao("metoclopramida")
        assert result.total_retornado == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_case_insensitive(self) -> None:
        respx.get(BPS_URL).mock(return_value=httpx.Response(200, json={"bps": [SAMPLE_RECORD]}))
        result = await client.buscar_por_descricao("METOCLOPRAMIDA")
        assert result.total_retornado == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_no_match(self) -> None:
        respx.get(BPS_URL).mock(return_value=httpx.Response(200, json={"bps": [SAMPLE_RECORD]}))
        result = await client.buscar_por_descricao("aspirina")
        assert result.total_retornado == 0
