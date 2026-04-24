"""Integration tests for ISP-RJ."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastmcp import Client

from mcp_brasil import settings

_ISP_FIXTURE = (
    "cisp;mes;ano;mes_ano;aisp;risp;munic;mcirc;regiao;"
    "hom_doloso;latrocinio;feminicidio;letalidade_violenta;"
    "total_roubos;roubo_veiculo;total_furtos;furto_veiculos\n"
    "001;1;2024;01/2024;1;1;Rio de Janeiro;1;Capital;10;2;1;15;500;100;300;80\n"
    "002;1;2024;01/2024;1;1;Rio de Janeiro;1;Capital;8;1;0;10;400;80;250;60\n"
    "003;2;2024;02/2024;1;1;Rio de Janeiro;1;Capital;12;1;2;18;550;110;320;90\n"
    "100;1;2024;01/2024;2;2;Niterói;2;Metropolitana;3;0;0;3;200;40;100;30\n"
    "100;2;2024;02/2024;2;2;Niterói;2;Metropolitana;4;1;0;5;210;45;110;35\n"
    "200;1;2024;01/2024;3;3;Duque de Caxias;3;Baixada;7;2;1;10;300;70;150;50\n"
)


@pytest.fixture
def tmp_cache(monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tempfile.mkdtemp(prefix="mcp-brasil-isp-test-")
    monkeypatch.setattr(settings, "DATASET_CACHE_DIR", d)
    monkeypatch.setattr(settings, "DATASETS_ENABLED", ["isp_rj"])
    return Path(d)


@pytest.fixture
def patch_download(tmp_cache: Path):
    def fake(url: str, dest: Path, timeout: float, source_encoding: str = "utf-8") -> int:
        dest.write_text(_ISP_FIXTURE, encoding="utf-8")
        return dest.stat().st_size

    with patch(
        "mcp_brasil._shared.datasets.loader._download_to_file",
        side_effect=fake,
    ) as m:
        yield m


def _text(result) -> str:
    data = getattr(result, "data", None)
    if isinstance(data, str):
        return data
    content = getattr(result, "content", None)
    if content:
        t = getattr(content[0], "text", None)
        if isinstance(t, str):
            return t
    return str(result)


@pytest.mark.asyncio
async def test_info_before_load(tmp_cache: Path) -> None:
    from mcp_brasil.datasets.isp_rj.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("info_isp_rj", {})
    assert "Cached: não" in _text(r)


@pytest.mark.asyncio
async def test_indicadores_municipio(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.isp_rj.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool(
            "indicadores_municipio",
            {"municipio": "Rio de Janeiro", "ano": 2024},
        )
    text = _text(r)
    # Somatório: hom_doloso RJ capital = 10+8+12 = 30
    assert "Rio de Janeiro" in text
    assert "30" in text


@pytest.mark.asyncio
async def test_ranking_municipios_hom_doloso(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.isp_rj.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool(
            "ranking_municipios",
            {"indicador": "hom_doloso", "ano": 2024, "limite": 5},
        )
    text = _text(r)
    assert "Rio de Janeiro" in text
    # RJ capital tem mais homicídios que Niterói
    assert text.find("Rio de Janeiro") < text.find("Niterói")


@pytest.mark.asyncio
async def test_serie_temporal(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.isp_rj.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool(
            "serie_temporal",
            {"indicador": "hom_doloso", "ano_inicio": 2023},
        )
    text = _text(r)
    assert "2024-01" in text
    assert "2024-02" in text


@pytest.mark.asyncio
async def test_valores_distintos_munic(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.isp_rj.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("valores_distintos_isp", {"coluna": "munic"})
    text = _text(r)
    assert "Rio de Janeiro" in text
    assert "Niterói" in text
