"""Tests for the SINESP/MJSP CKAN HTTP client (respx-mocked)."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_brasil.data.sinesp import client
from mcp_brasil.data.sinesp.constants import (
    GROUP_SHOW_URL,
    ORGANIZATION_LIST_URL,
    ORGANIZATION_SHOW_URL,
    PACKAGE_LIST_URL,
    PACKAGE_SEARCH_URL,
    PACKAGE_SHOW_URL,
)


class TestListarDatasets:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_list(self) -> None:
        respx.get(PACKAGE_LIST_URL).mock(
            return_value=httpx.Response(
                200,
                json={"success": True, "result": ["sinesp", "infopen"]},
            )
        )
        nomes = await client.listar_datasets()
        assert nomes == ["sinesp", "infopen"]


class TestBuscarDatasets:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_results(self) -> None:
        respx.get(PACKAGE_SEARCH_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "count": 1,
                        "results": [
                            {
                                "id": "abc123",
                                "name": "sinesp",
                                "title": "Ocorrências Criminais",
                                "notes": "Dados SINESP",
                                "organization": {"name": "senasp", "title": "SENASP"},
                                "tags": [{"name": "seguranca", "display_name": "segurança"}],
                                "resources": [
                                    {"id": "r1", "name": "dados.xlsx", "format": "XLSX"}
                                ],
                            }
                        ],
                    },
                },
            )
        )
        total, datasets = await client.buscar_datasets("segurança")
        assert total == 1
        assert datasets[0].nome == "sinesp"
        assert datasets[0].organizacao == "SENASP"
        assert datasets[0].num_recursos == 1


class TestDetalharDataset:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_details(self) -> None:
        respx.get(PACKAGE_SHOW_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "id": "abc123",
                        "name": "sinesp",
                        "title": "Ocorrências Criminais",
                        "notes": "Descrição detalhada",
                        "license_title": "CC-BY",
                        "organization": {"title": "SENASP"},
                        "tags": [],
                        "resources": [
                            {
                                "id": "r1",
                                "name": "dados_uf.xlsx",
                                "format": "XLSX",
                                "url": "http://dados.mj.gov.br/download/dados_uf.xlsx",
                            }
                        ],
                    },
                },
            )
        )
        dataset = await client.detalhar_dataset("sinesp")
        assert dataset is not None
        assert dataset.titulo == "Ocorrências Criminais"
        assert dataset.licenca == "CC-BY"
        assert len(dataset.recursos) == 1
        assert dataset.recursos[0].formato == "XLSX"

    @pytest.mark.asyncio
    @respx.mock
    async def test_not_found(self) -> None:
        respx.get(PACKAGE_SHOW_URL).mock(return_value=httpx.Response(200, json={"success": False}))
        dataset = await client.detalhar_dataset("nao-existe")
        assert dataset is None


class TestListarOrganizacoes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_orgs(self) -> None:
        respx.get(ORGANIZATION_LIST_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": True,
                    "result": [
                        {
                            "id": "org1",
                            "name": "senasp",
                            "title": "SENASP",
                            "description": "Segurança Pública",
                            "package_count": 6,
                        }
                    ],
                },
            )
        )
        orgs = await client.listar_organizacoes()
        assert len(orgs) == 1
        assert orgs[0].nome == "senasp"
        assert orgs[0].num_datasets == 6


class TestDetalharOrganizacao:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_org_with_datasets(self) -> None:
        respx.get(ORGANIZATION_SHOW_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "id": "org1",
                        "name": "senasp",
                        "title": "SENASP",
                        "package_count": 1,
                        "packages": [
                            {
                                "id": "d1",
                                "name": "sinesp",
                                "title": "SINESP",
                                "organization": {"title": "SENASP"},
                                "tags": [],
                                "resources": [],
                            }
                        ],
                    },
                },
            )
        )
        org, datasets = await client.detalhar_organizacao("senasp")
        assert org is not None
        assert org.titulo == "SENASP"
        assert len(datasets) == 1


class TestListarDatasetsGrupo:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_group_datasets(self) -> None:
        respx.get(GROUP_SHOW_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "title": "Segurança Pública",
                        "packages": [
                            {
                                "id": "d1",
                                "name": "sinesp",
                                "title": "SINESP",
                                "organization": {},
                                "tags": [],
                                "resources": [],
                            }
                        ],
                    },
                },
            )
        )
        titulo, datasets = await client.listar_datasets_grupo("seguranca-publica")
        assert titulo == "Segurança Pública"
        assert len(datasets) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_not_found(self) -> None:
        respx.get(GROUP_SHOW_URL).mock(return_value=httpx.Response(200, json={"success": False}))
        titulo, datasets = await client.listar_datasets_grupo("nao-existe")
        assert titulo is None
        assert datasets == []
