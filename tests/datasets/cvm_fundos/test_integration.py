"""Integration tests for cvm_fundos."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastmcp import Client

from mcp_brasil import settings

_CVM_FIXTURE = (
    "TP_FUNDO;CNPJ_FUNDO;DENOM_SOCIAL;DT_REG;SIT;CLASSE;CLASSE_ANBIMA;"
    "CONDOM;FUNDO_COTAS;FUNDO_EXCLUSIVO;TAXA_PERFM;TAXA_ADM;"
    "VL_PATRIM_LIQ;DT_PATRIM_LIQ;ADMIN;CNPJ_ADMIN;GESTOR;CUSTODIANTE;AUDITOR\n"
    "FIF;11.111.111/0001-00;FUNDO ALPHA RENDA FIXA;2020-01-01;"
    "EM FUNCIONAMENTO NORMAL;Renda Fixa;Renda Fixa;Fechado;N;N;0;1,5;"
    "100000000,00;2024-12-31;BANCO A;99.999.999/0001-11;GESTORA X;"
    "BANCO B;AUDITORIA Y\n"
    "FIF;22.222.222/0001-00;FUNDO BETA AÇÕES;2021-05-10;"
    "EM FUNCIONAMENTO NORMAL;Ações;Ações Livre;Aberto;N;N;20;2,0;"
    "50000000,00;2024-12-31;BANCO A;99.999.999/0001-11;GESTORA Y;"
    "BANCO B;AUDITORIA Y\n"
    "FIF;33.333.333/0001-00;FUNDO GAMMA MULTI;2019-03-15;"
    "CANCELADA;Multimercado;Multimercado Macro;Aberto;S;N;20;2,5;"
    "10000000,00;2024-01-15;BANCO C;88.888.888/0001-22;GESTORA Z;"
    "BANCO D;AUDITORIA W\n"
)


@pytest.fixture
def tmp_cache(monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tempfile.mkdtemp(prefix="mcp-brasil-cvm-test-")
    monkeypatch.setattr(settings, "DATASET_CACHE_DIR", d)
    monkeypatch.setattr(settings, "DATASETS_ENABLED", ["cvm_fundos"])
    return Path(d)


@pytest.fixture
def patch_download(tmp_cache: Path):
    def fake(url: str, dest: Path, timeout: float, source_encoding: str = "utf-8") -> int:
        dest.write_text(_CVM_FIXTURE, encoding="utf-8")
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
    from mcp_brasil.datasets.cvm_fundos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("info_cvm_fundos", {})
    assert "Cached: não" in _text(r)


@pytest.mark.asyncio
async def test_buscar_fundo_por_nome(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.cvm_fundos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("buscar_fundo", {"termo": "ALPHA"})
    text = _text(r)
    assert "FUNDO ALPHA" in text


@pytest.mark.asyncio
async def test_top_fundos_por_pl(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.cvm_fundos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("top_fundos_por_pl", {"limite": 5})
    text = _text(r)
    # ALPHA (100M) > BETA (50M); GAMMA cancelado filtrado
    assert text.find("ALPHA") < text.find("BETA")
    assert "GAMMA" not in text


@pytest.mark.asyncio
async def test_top_por_classe(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.cvm_fundos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("top_fundos_por_pl", {"classe": "Ações"})
    text = _text(r)
    assert "BETA" in text
    assert "ALPHA" not in text


@pytest.mark.asyncio
async def test_detalhe_fundo(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.cvm_fundos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("detalhe_fundo", {"cnpj": "11.111.111/0001-00"})
    text = _text(r)
    assert "FUNDO ALPHA" in text
    assert "BANCO A" in text


@pytest.mark.asyncio
async def test_valores_distintos_classe(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.cvm_fundos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("valores_distintos_cvm", {"coluna": "CLASSE"})
    text = _text(r)
    assert "Renda Fixa" in text
    assert "Ações" in text
