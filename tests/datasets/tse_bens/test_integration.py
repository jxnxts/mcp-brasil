"""End-to-end tests for tse_bens with a small CSV fixture."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastmcp import Client

from mcp_brasil import settings

_HEADERS = (
    '"DT_GERACAO";"HH_GERACAO";"ANO_ELEICAO";"CD_TIPO_ELEICAO";"NM_TIPO_ELEICAO";'
    '"CD_ELEICAO";"DS_ELEICAO";"DT_ELEICAO";"SG_UF";"SG_UE";"NM_UE";'
    '"SQ_CANDIDATO";"NR_ORDEM_BEM_CANDIDATO";"CD_TIPO_BEM_CANDIDATO";'
    '"DS_TIPO_BEM_CANDIDATO";"DS_BEM_CANDIDATO";"VR_BEM_CANDIDATO";'
    '"DT_ULT_ATUAL_BEM_CANDIDATO";"HH_ULT_ATUAL_BEM_CANDIDATO"'
)


def _bem(sq: str, ordem: int, tipo: str, desc: str, valor: str) -> str:
    return (
        f'"01/01/2024";"00:00:00";2024;2;"Eleição Ordinária";619;'
        f'"Eleições Municipais 2024";"06/10/2024";"SP";"00001";"São Paulo";'
        f"{sq};{ordem};1;"
        f'"{tipo}";"{desc}";"{valor}";"01/01/2024";"00:00:00"'
    )


_FIXTURE = "\n".join(
    [
        _HEADERS,
        _bem("1", 1, "Casa", "Residência principal", "500000,00"),
        _bem("1", 2, "Veículo automotor terrestre", "Carro 2020", "80000,00"),
        _bem("2", 1, "Apartamento", "Cobertura", "1.200.000,00"),
        _bem("2", 2, "Ações", "Petrobras", "50.000,00"),
        _bem("3", 1, "Terreno", "Lote urbano", "150000,00"),
    ]
)


@pytest.fixture
def tmp_cache(monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tempfile.mkdtemp(prefix="mcp-brasil-tse-bens-test-")
    monkeypatch.setattr(settings, "DATASET_CACHE_DIR", d)
    monkeypatch.setattr(settings, "DATASETS_ENABLED", ["tse_bens"])
    return Path(d)


@pytest.fixture
def patch_download(tmp_cache: Path):
    def fake_extract(
        url: str,
        dest: Path,
        *,
        zip_member: str,
        timeout: float,
        source_encoding: str = "utf-8",
    ) -> int:
        dest.write_text(_FIXTURE, encoding="utf-8")
        return dest.stat().st_size

    with patch(
        "mcp_brasil._shared.datasets.loader._download_and_extract_zip",
        side_effect=fake_extract,
    ) as m:
        yield m


def _text(r) -> str:
    data = getattr(r, "data", None)
    if isinstance(data, str):
        return data
    content = getattr(r, "content", None)
    if content:
        return content[0].text
    return str(r)


@pytest.mark.asyncio
async def test_buscar_bens_candidato(tmp_cache, patch_download) -> None:
    from mcp_brasil.datasets.tse_bens.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("buscar_bens_candidato", {"sq_candidato": "1"})
    t = _text(r)
    assert "Residência principal" in t
    assert "Carro 2020" in t
    # total: 500000 + 80000 = 580000
    assert "580" in t


@pytest.mark.asyncio
async def test_resumo_tipos_bens(tmp_cache, patch_download) -> None:
    from mcp_brasil.datasets.tse_bens.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("resumo_tipos_bens", {"top": 10})
    t = _text(r)
    assert "Apartamento" in t
    assert "Terreno" in t


@pytest.mark.asyncio
async def test_top_patrimonios_requires_candidatos_dataset(tmp_cache, patch_download) -> None:
    from mcp_brasil.datasets.tse_bens.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool(
            "top_patrimonios_cargo",
            {"cargo": "PREFEITO", "limite": 5},
        )
    # tse_candidatos not in fixture; expected to error cleanly.
    t = _text(r)
    assert "ERRO" in t or "candidatos" in t.lower()


@pytest.mark.asyncio
async def test_tools_registered(tmp_cache) -> None:
    from mcp_brasil.datasets.tse_bens.server import mcp

    async with Client(mcp) as c:
        tools = {t.name for t in await c.list_tools()}
    assert {
        "info_tse_bens",
        "buscar_bens_candidato",
        "top_patrimonios_cargo",
        "resumo_patrimonio_partido",
        "resumo_tipos_bens",
    }.issubset(tools)
