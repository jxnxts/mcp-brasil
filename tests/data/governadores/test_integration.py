"""Integration tests for governadores."""

from __future__ import annotations

import httpx
import pytest
import respx
from fastmcp import Client

from mcp_brasil.data.governadores import FEATURE_META
from mcp_brasil.data.governadores import client as gclient
from mcp_brasil.data.governadores.constants import GOV_JSON_URL
from mcp_brasil.data.governadores.server import mcp

_FIXTURE_JSON = {
    "São Paulo": {
        "nome": "Tarcísio de Freitas",
        "nome_completo": "Tarcísio Gomes de Freitas",
        "ano_eleicao": 2022,
        "mandato_inicio": "2023-01-01",
        "mandato_fim": "2027-01-06",
        "partido": "Republicanos",
        "partido_sigla": "REPUBLICANOS",
        "vice_governador": "Felício Ramuth",
    },
    "Rio de Janeiro": {
        "nome": "Cláudio Castro",
        "nome_completo": "Cláudio Bomfim de Castro e Silva",
        "ano_eleicao": 2022,
        "mandato_inicio": "2022-04-28",
        "mandato_fim": "2027-01-06",
        "partido": "Partido Liberal",
        "partido_sigla": "PL",
        "vice_governador": "Thiago Pampolha",
    },
    "Bahia": {
        "nome": "Jerônimo Rodrigues",
        "nome_completo": "Jerônimo Rodrigues Souza",
        "ano_eleicao": 2022,
        "mandato_inicio": "2023-01-01",
        "mandato_fim": "2027-01-06",
        "partido": "Partido dos Trabalhadores",
        "partido_sigla": "PT",
        "vice_governador": "Geraldo Júnior",
    },
}


@pytest.fixture(autouse=True)
def clear_cache():
    gclient._CACHE.clear()
    gclient._CACHE_TS = 0.0
    yield


def test_feature_meta() -> None:
    assert FEATURE_META.name == "governadores"


@pytest.mark.asyncio
async def test_lists_tools() -> None:
    async with Client(mcp) as c:
        tools = await c.list_tools()
    names = {t.name for t in tools}
    assert {"listar_governadores", "consultar_governador", "resumo_por_partido"} <= names


@pytest.mark.asyncio
@respx.mock
async def test_listar_governadores_parses() -> None:
    respx.get(GOV_JSON_URL).mock(return_value=httpx.Response(200, json=_FIXTURE_JSON))
    async with Client(mcp) as c:
        r = await c.call_tool("listar_governadores", {})
    data = getattr(r, "data", None) or str(r)
    assert "Tarcísio" in data
    assert "Cláudio Castro" in data


@pytest.mark.asyncio
@respx.mock
async def test_consultar_sp() -> None:
    respx.get(GOV_JSON_URL).mock(return_value=httpx.Response(200, json=_FIXTURE_JSON))
    async with Client(mcp) as c:
        r = await c.call_tool("consultar_governador", {"uf": "SP"})
    data = getattr(r, "data", None) or str(r)
    assert "Tarcísio" in data


@pytest.mark.asyncio
@respx.mock
async def test_por_partido() -> None:
    respx.get(GOV_JSON_URL).mock(return_value=httpx.Response(200, json=_FIXTURE_JSON))
    async with Client(mcp) as c:
        r = await c.call_tool("governadores_por_partido", {"partido_sigla": "PT"})
    data = getattr(r, "data", None) or str(r)
    assert "Jerônimo" in data
    assert "Tarcísio" not in data
