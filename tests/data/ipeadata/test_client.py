"""Tests for IPEADATA client."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_brasil.data.ipeadata import client
from mcp_brasil.data.ipeadata.constants import IPEADATA_API_BASE


@pytest.mark.asyncio
@respx.mock
async def test_listar_series_parses() -> None:
    respx.get(f"{IPEADATA_API_BASE}/Metadados").mock(
        return_value=httpx.Response(
            200,
            json={
                "value": [{"SERCODIGO": "PRECOS12_IPCA12", "SERNOME": "IPCA", "PERNOME": "Mensal"}]
            },
        )
    )
    series = await client.listar_series(filtro_nome="IPCA")
    assert len(series) == 1
    assert series[0].SERCODIGO == "PRECOS12_IPCA12"


@pytest.mark.asyncio
@respx.mock
async def test_valores_serie() -> None:
    respx.get(f"{IPEADATA_API_BASE}/ValoresSerie(SERCODIGO='X')").mock(
        return_value=httpx.Response(
            200,
            json={
                "value": [
                    {"SERCODIGO": "X", "VALDATA": "2024-01-01", "VALVALOR": 1.5},
                    {"SERCODIGO": "X", "VALDATA": "2024-02-01", "VALVALOR": 2.0},
                ]
            },
        )
    )
    vs = await client.valores_serie("X")
    assert len(vs) == 2
    # Client reverses OData asc order → desc. Most recent first.
    assert vs[0].VALVALOR == 2.0
    assert vs[1].VALVALOR == 1.5


@pytest.mark.asyncio
@respx.mock
async def test_metadados_serie_not_found() -> None:
    respx.get(f"{IPEADATA_API_BASE}/Metadados").mock(
        return_value=httpx.Response(200, json={"value": []})
    )
    m = await client.metadados_serie("INEXISTENTE")
    assert m is None
