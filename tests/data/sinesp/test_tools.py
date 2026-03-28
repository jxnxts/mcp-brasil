"""Tests for the SINESP/MJSP CKAN tool functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_brasil.data.sinesp import tools
from mcp_brasil.data.sinesp.schemas import DatasetCKAN, OrganizacaoCKAN, RecursoCKAN

CLIENT_MODULE = "mcp_brasil.data.sinesp.client"


def _mock_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    return ctx


class TestListarDatasetsMjsp:
    @pytest.mark.asyncio
    async def test_formats_list(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.listar_datasets",
            new_callable=AsyncMock,
            return_value=["sinesp", "infopen"],
        ):
            result = await tools.listar_datasets_mjsp(ctx)
        assert "2 datasets" in result
        assert "sinesp" in result
        assert "infopen" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(f"{CLIENT_MODULE}.listar_datasets", new_callable=AsyncMock, return_value=[]):
            result = await tools.listar_datasets_mjsp(ctx)
        assert "Nenhum dataset" in result


class TestBuscarDatasetsMjsp:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = [
            DatasetCKAN(
                id="abc",
                nome="sinesp",
                titulo="Ocorrências Criminais",
                organizacao="SENASP",
                num_recursos=5,
                tags=["segurança"],
            )
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_datasets",
            new_callable=AsyncMock,
            return_value=(1, mock_data),
        ):
            result = await tools.buscar_datasets_mjsp("segurança", ctx)
        assert "Ocorrências Criminais" in result
        assert "SENASP" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_datasets",
            new_callable=AsyncMock,
            return_value=(0, []),
        ):
            result = await tools.buscar_datasets_mjsp("inexistente", ctx)
        assert "Nenhum dataset" in result


class TestDetalharDatasetMjsp:
    @pytest.mark.asyncio
    async def test_formats_details(self) -> None:
        mock_data = DatasetCKAN(
            id="abc",
            nome="sinesp",
            titulo="Ocorrências Criminais",
            descricao="Dados SINESP",
            organizacao="SENASP",
            licenca="CC-BY",
            tags=["segurança"],
            num_recursos=1,
            recursos=[
                RecursoCKAN(
                    id="r1",
                    nome="dados_uf.xlsx",
                    formato="XLSX",
                    url="http://dados.mj.gov.br/download/dados_uf.xlsx",
                )
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.detalhar_dataset",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.detalhar_dataset_mjsp("sinesp", ctx)
        assert "Ocorrências Criminais" in result
        assert "SENASP" in result
        assert "CC-BY" in result
        assert "dados_uf.xlsx" in result
        assert "XLSX" in result

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        ctx = _mock_ctx()
        with patch(f"{CLIENT_MODULE}.detalhar_dataset", new_callable=AsyncMock, return_value=None):
            result = await tools.detalhar_dataset_mjsp("nao-existe", ctx)
        assert "não encontrado" in result


class TestListarOrganizacoesMjsp:
    @pytest.mark.asyncio
    async def test_formats_orgs(self) -> None:
        mock_data = [
            OrganizacaoCKAN(id="o1", nome="senasp", titulo="SENASP", num_datasets=6),
            OrganizacaoCKAN(id="o2", nome="dpf", titulo="DPF", num_datasets=2),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.listar_organizacoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.listar_organizacoes_mjsp(ctx)
        assert "2 organizações" in result
        assert "SENASP" in result
        assert "senasp" in result


class TestListarDatasetsOrganizacao:
    @pytest.mark.asyncio
    async def test_formats_org_datasets(self) -> None:
        mock_org = OrganizacaoCKAN(id="o1", nome="senasp", titulo="SENASP", num_datasets=1)
        mock_datasets = [DatasetCKAN(id="d1", nome="sinesp", titulo="SINESP", num_recursos=5)]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.detalhar_organizacao",
            new_callable=AsyncMock,
            return_value=(mock_org, mock_datasets),
        ):
            result = await tools.listar_datasets_organizacao("senasp", ctx)
        assert "SENASP" in result
        assert "sinesp" in result

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.detalhar_organizacao",
            new_callable=AsyncMock,
            return_value=(None, []),
        ):
            result = await tools.listar_datasets_organizacao("nao-existe", ctx)
        assert "não encontrada" in result


class TestListarDatasetsGrupoSeguranca:
    @pytest.mark.asyncio
    async def test_formats_group(self) -> None:
        mock_datasets = [DatasetCKAN(id="d1", nome="sinesp", titulo="SINESP", num_recursos=5)]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.listar_datasets_grupo",
            new_callable=AsyncMock,
            return_value=("Segurança Pública", mock_datasets),
        ):
            result = await tools.listar_datasets_grupo_seguranca(ctx)
        assert "Segurança Pública" in result
        assert "sinesp" in result

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.listar_datasets_grupo",
            new_callable=AsyncMock,
            return_value=(None, []),
        ):
            result = await tools.listar_datasets_grupo_seguranca(ctx, grupo="nao-existe")
        assert "não encontrado" in result
