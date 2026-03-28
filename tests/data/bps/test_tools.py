"""Tests for the BPS tool functions."""

from unittest.mock import AsyncMock

import pytest

from mcp_brasil.data.bps import tools
from mcp_brasil.data.bps.schemas import BPSResultado, ComprasBPS


def _make_ctx() -> AsyncMock:
    ctx = AsyncMock()
    ctx.info = AsyncMock()
    return ctx


SAMPLE = ComprasBPS(
    ano_da_compra="2025",
    data_da_compra="2025-01-02",
    nome_da_instituicao="HOSPITAL MUNICIPAL",
    uf_da_instituicao="SP",
    codigo_br="267311",
    descricao_catmat="PARACETAMOL 500MG COMPRIMIDO",
    generico="S",
    modalidade_da_compra="Pregão",
    fornecedor="PHARMA LTDA",
    quantidade_itens_comprados=1000.0,
    preco_unitario=0.15,
    preco_total=150.0,
)


class TestConsultarPrecosSaude:
    @pytest.mark.asyncio
    async def test_returns_formatted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "mcp_brasil.data.bps.tools.client.consultar_precos",
            AsyncMock(return_value=BPSResultado(total_retornado=1, registros=[SAMPLE])),
        )
        result = await tools.consultar_precos_saude(_make_ctx())
        assert "PARACETAMOL" in result
        assert "HOSPITAL MUNICIPAL" in result
        assert "PHARMA LTDA" in result
        assert "267311" in result

    @pytest.mark.asyncio
    async def test_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "mcp_brasil.data.bps.tools.client.consultar_precos",
            AsyncMock(return_value=BPSResultado()),
        )
        result = await tools.consultar_precos_saude(_make_ctx())
        assert "Nenhum registro" in result


class TestBuscarMedicamentoBps:
    @pytest.mark.asyncio
    async def test_returns_formatted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "mcp_brasil.data.bps.tools.client.buscar_por_descricao",
            AsyncMock(return_value=BPSResultado(total_retornado=1, registros=[SAMPLE])),
        )
        result = await tools.buscar_medicamento_bps("paracetamol", _make_ctx())
        assert "PARACETAMOL" in result
        assert "Genérico" in result

    @pytest.mark.asyncio
    async def test_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "mcp_brasil.data.bps.tools.client.buscar_por_descricao",
            AsyncMock(return_value=BPSResultado()),
        )
        result = await tools.buscar_medicamento_bps("xyz", _make_ctx())
        assert "Nenhum registro" in result


class TestBuscarCatmatBps:
    @pytest.mark.asyncio
    async def test_returns_formatted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "mcp_brasil.data.bps.tools.client.buscar_por_catmat",
            AsyncMock(return_value=BPSResultado(total_retornado=1, registros=[SAMPLE])),
        )
        result = await tools.buscar_catmat_bps("267311", _make_ctx())
        assert "267311" in result
        assert "PARACETAMOL" in result
