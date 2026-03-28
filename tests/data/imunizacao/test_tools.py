"""Tests for the Imunização tool functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_brasil.data.imunizacao import tools
from mcp_brasil.data.imunizacao.schemas import (
    AgregacaoVacinacao,
    DatasetPNI,
    RecursoPNI,
    RegistroVacinacao,
)

CLIENT_MODULE = "mcp_brasil.data.imunizacao.client"


def _mock_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    return ctx


# ---------------------------------------------------------------------------
# buscar_vacinacao
# ---------------------------------------------------------------------------


class TestBuscarVacinacao:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            RegistroVacinacao(
                municipio="Teresina",
                uf="PI",
                vacina_nome="Covid-19",
                dose="1ª Dose",
                fabricante="AstraZeneca",
                data_aplicacao="2021-06-15",
            ),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_vacinacao_es",
            new_callable=AsyncMock,
            return_value=(mock_data, 1),
        ):
            result = await tools.buscar_vacinacao(ctx, uf="PI")
        assert "Covid-19" in result
        assert "Teresina" in result
        assert "AstraZeneca" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_vacinacao_es",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            result = await tools.buscar_vacinacao(ctx, uf="XX")
        assert "Nenhum registro" in result


# ---------------------------------------------------------------------------
# estatisticas_por_vacina
# ---------------------------------------------------------------------------


class TestEstatisticasPorVacina:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            AgregacaoVacinacao(nome="Covid-19", total=50000),
            AgregacaoVacinacao(nome="Influenza", total=30000),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.agregar_vacinacao_es",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.estatisticas_por_vacina(ctx, uf="PI")
        assert "Covid-19" in result
        assert "Influenza" in result
        assert "Doses aplicadas" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.agregar_vacinacao_es",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await tools.estatisticas_por_vacina(ctx)
        assert "Nenhuma estatística" in result


# ---------------------------------------------------------------------------
# estatisticas_por_faixa_etaria
# ---------------------------------------------------------------------------


class TestEstatisticasPorFaixaEtaria:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            AgregacaoVacinacao(nome="M", total=25000),
            AgregacaoVacinacao(nome="F", total=30000),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.agregar_vacinacao_es",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.estatisticas_por_faixa_etaria(ctx, uf="SP")
        assert "sexo biológico" in result.lower()

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.agregar_vacinacao_es",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await tools.estatisticas_por_faixa_etaria(ctx)
        assert "Nenhuma estatística" in result


# ---------------------------------------------------------------------------
# buscar_datasets_pni
# ---------------------------------------------------------------------------


class TestBuscarDatasetsPni:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            DatasetPNI(
                id="abc",
                nome="doses-pni-2025",
                titulo="Doses PNI 2025",
                organizacao="MS",
                total_recursos=3,
            ),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_datasets_pni",
            new_callable=AsyncMock,
            return_value=(mock_data, 1),
        ):
            result = await tools.buscar_datasets_pni(ctx, query="PNI")
        assert "Doses PNI" in result
        assert "Datasets PNI" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_datasets_pni",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            result = await tools.buscar_datasets_pni(ctx, query="xyz")
        assert "Nenhum dataset" in result


# ---------------------------------------------------------------------------
# consultar_doses_dataset
# ---------------------------------------------------------------------------


class TestConsultarDosesDataset:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_ds = DatasetPNI(id="abc", nome="doses-pni", titulo="Doses PNI 2025")
        mock_recursos = [RecursoPNI(id="r1", nome="dados.csv", formato="CSV")]
        mock_records = [{"uf": "SP", "vacina": "BCG", "doses": 5000}]
        ctx = _mock_ctx()
        with (
            patch(
                f"{CLIENT_MODULE}.detalhar_dataset_pni",
                new_callable=AsyncMock,
                return_value=(mock_ds, mock_recursos),
            ),
            patch(
                f"{CLIENT_MODULE}.consultar_datastore_pni",
                new_callable=AsyncMock,
                return_value=(mock_records, 100),
            ),
        ):
            result = await tools.consultar_doses_dataset(ctx, dataset_id="doses-pni")
        assert "Doses PNI" in result
        assert "SP" in result

    @pytest.mark.asyncio
    async def test_dataset_not_found(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.detalhar_dataset_pni",
            new_callable=AsyncMock,
            return_value=(None, []),
        ):
            result = await tools.consultar_doses_dataset(ctx, dataset_id="inexistente")
        assert "não encontrado" in result

    @pytest.mark.asyncio
    async def test_no_records(self) -> None:
        mock_ds = DatasetPNI(id="abc", nome="doses-pni", titulo="Doses PNI")
        mock_recursos = [RecursoPNI(id="r1")]
        ctx = _mock_ctx()
        with (
            patch(
                f"{CLIENT_MODULE}.detalhar_dataset_pni",
                new_callable=AsyncMock,
                return_value=(mock_ds, mock_recursos),
            ),
            patch(
                f"{CLIENT_MODULE}.consultar_datastore_pni",
                new_callable=AsyncMock,
                return_value=([], 0),
            ),
        ):
            result = await tools.consultar_doses_dataset(ctx, dataset_id="doses-pni")
        assert "Nenhum registro" in result


# ---------------------------------------------------------------------------
# calendario_vacinacao
# ---------------------------------------------------------------------------


class TestCalendarioVacinacao:
    @pytest.mark.asyncio
    async def test_returns_calendar(self) -> None:
        ctx = _mock_ctx()
        result = await tools.calendario_vacinacao(ctx)
        assert "Calendário Nacional" in result
        assert "BCG" in result
        assert "Penta" in result
        assert "HPV" in result


# ---------------------------------------------------------------------------
# listar_vacinas_sus
# ---------------------------------------------------------------------------


class TestListarVacinasSus:
    @pytest.mark.asyncio
    async def test_returns_all(self) -> None:
        ctx = _mock_ctx()
        result = await tools.listar_vacinas_sus(ctx)
        assert "Vacinas do SUS" in result
        assert "BCG" in result
        assert "imunobiológicos" in result


# ---------------------------------------------------------------------------
# consultar_vacina
# ---------------------------------------------------------------------------


class TestConsultarVacina:
    @pytest.mark.asyncio
    async def test_found_by_sigla(self) -> None:
        ctx = _mock_ctx()
        result = await tools.consultar_vacina(ctx, nome="BCG")
        assert "BCG" in result
        assert "Tuberculose" in result

    @pytest.mark.asyncio
    async def test_found_by_name(self) -> None:
        ctx = _mock_ctx()
        result = await tools.consultar_vacina(ctx, nome="hepatite")
        assert "Hepatite" in result

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        ctx = _mock_ctx()
        result = await tools.consultar_vacina(ctx, nome="xyzinexistente")
        assert "não encontrada" in result


# ---------------------------------------------------------------------------
# verificar_esquema_vacinal
# ---------------------------------------------------------------------------


class TestVerificarEsquemaVacinal:
    @pytest.mark.asyncio
    async def test_child_4_years(self) -> None:
        ctx = _mock_ctx()
        result = await tools.verificar_esquema_vacinal(ctx, idade=4)
        assert "4 anos" in result
        assert "BCG" in result
        assert "Varicela" in result
        assert "UBS" in result

    @pytest.mark.asyncio
    async def test_baby(self) -> None:
        ctx = _mock_ctx()
        result = await tools.verificar_esquema_vacinal(ctx, idade=0)
        assert "BCG" in result
        assert "HepB" in result

    @pytest.mark.asyncio
    async def test_elderly(self) -> None:
        ctx = _mock_ctx()
        result = await tools.verificar_esquema_vacinal(ctx, idade=65)
        assert "Influenza" in result


# ---------------------------------------------------------------------------
# metas_cobertura
# ---------------------------------------------------------------------------


class TestMetasCobertura:
    @pytest.mark.asyncio
    async def test_returns_targets(self) -> None:
        ctx = _mock_ctx()
        result = await tools.metas_cobertura(ctx)
        assert "Metas de cobertura" in result
        assert "95" in result
        assert "BCG" in result
