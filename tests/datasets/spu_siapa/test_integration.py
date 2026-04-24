"""End-to-end tests for spu_siapa with a small CSV fixture.

We inject a tiny CSV via the same transcoding pipeline the real feature
uses, so schema detection, BR-locale number parsing, and DuckDB queries
all exercise the production path.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastmcp import Client

from mcp_brasil import settings

# Minimal 5-row SIAPA-shaped CSV — same columns as the real dataset,
# already in latin-1 encoding to match the real source.
_SIAPA_FIXTURE = (
    # Header — will be skipped by spec.csv_options.skip=1
    "Classe;Rip Imóvel;Nº/RIP Utilização;Data do Cadastro do Imóvel;"
    "UF;Município;Endereço;Bairro;Latitude;Longitude;Nível de Precisão;"
    "Conceituação do Terreno;Tipo de Imóvel;Regime de Utilização;"
    "Proprietário Oficial;Data Início da Utilização;"
    "Área do Terreno (m²);Área da União (m²)\n"
    # 1. Rio aforamento marinha
    "Dominial;6001013067401;004;###;RJ;Rio de Janeiro;R PRESIDENTE BARROSO 82;"
    "CIDADE NOVA;-22,91;-43,19;Manual;Marinha;Dominial;Aforamento;"
    "União;-;543,25;543,25\n"
    # 2. Rio ocupação marinha
    "Dominial;6001012010180;001;###;RJ;Rio de Janeiro;AV JOAO LUIS ALVES 56;"
    "URCA;-22,94;-43,16;Manual;Marinha;Dominial;Ocupação;"
    "União;-;341,09;341,09\n"
    # 3. Brasília uso especial
    "Uso Especial;5300108001;100;###;DF;Brasília;ESPL MINISTERIOS BL L;"
    "PLANO PILOTO;-15,79;-47,88;Manual;Interior;Edifício;Uso em Serviço Público;"
    "União;-;1.200,00;1.200,00\n"
    # 4. Salvador aforamento marinha
    "Dominial;2927408001;002;###;BA;Salvador;R CHILE 25;"
    "CENTRO;-12,97;-38,51;Manual;Marinha;Dominial;Aforamento;"
    "União;-;220,50;220,50\n"
    # 5. Recife cessão com valor faltante
    "Dominial;2611606001;003;###;PE;Recife;AV BOA VIAGEM 1000;"
    "BOA VIAGEM;-8,12;-34,89;Manual;Marinha;Dominial;Cessão;"
    "União;-;-;-\n"
)


@pytest.fixture
def tmp_cache(monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tempfile.mkdtemp(prefix="mcp-brasil-siapa-test-")
    monkeypatch.setattr(settings, "DATASET_CACHE_DIR", d)
    monkeypatch.setattr(settings, "DATASETS_ENABLED", ["spu_siapa"])
    return Path(d)


@pytest.fixture
def patch_download(tmp_cache: Path):
    """Replace the downloader so SPU endpoint is never hit."""

    def fake(url: str, dest: Path, timeout: float, source_encoding: str = "utf-8") -> int:
        # Simulate the real path: source is cp1252, loader transcodes to utf-8.
        import codecs

        if source_encoding.lower().replace("_", "-") in {
            "utf-8",
            "utf8",
            "latin-1",
            "latin1",
        }:
            dest.write_text(_SIAPA_FIXTURE, encoding="utf-8")
        else:
            raw = _SIAPA_FIXTURE.encode("cp1252", errors="replace")
            decoded = codecs.decode(raw, source_encoding)
            dest.write_text(decoded, encoding="utf-8")
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
        first = content[0]
        t = getattr(first, "text", None)
        if isinstance(t, str):
            return t
    return str(result)


@pytest.mark.asyncio
async def test_info_spu_siapa_before_load(tmp_cache: Path) -> None:
    from mcp_brasil.datasets.spu_siapa.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("info_spu_siapa", {})
    text = _text(r)
    assert "Cached localmente:** não" in text


@pytest.mark.asyncio
async def test_resumo_uf_siapa_end_to_end(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.spu_siapa.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("resumo_uf_siapa", {})
    text = _text(r)
    assert "RJ" in text
    assert "DF" in text
    assert "BA" in text
    # 2 RJ rows, 1 DF, 1 BA, 1 PE
    assert "Dominiais" in text
    assert "Uso Especial" in text


@pytest.mark.asyncio
async def test_buscar_imoveis_siapa_filter_by_uf_and_regime(
    tmp_cache: Path, patch_download
) -> None:
    from mcp_brasil.datasets.spu_siapa.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool(
            "buscar_imoveis_siapa",
            {"uf": "RJ", "regime": "Aforamento"},
        )
    text = _text(r)
    # RIP of the aforamento row
    assert "6001013067401" in text
    # Rio row with Ocupação should not appear when filtering by Aforamento
    assert "6001012010180" not in text
    assert "Aforamento" in text


@pytest.mark.asyncio
async def test_buscar_imoveis_siapa_filter_by_rip(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.spu_siapa.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("buscar_imoveis_siapa", {"rip": "6001013"})
    text = _text(r)
    assert "6001013067401" in text


@pytest.mark.asyncio
async def test_resumo_regime_siapa(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.spu_siapa.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("resumo_regime_siapa", {})
    text = _text(r)
    assert "Aforamento" in text
    assert "Ocupação" in text
    assert "Cessão" in text


@pytest.mark.asyncio
async def test_top_municipios_siapa(tmp_cache: Path, patch_download) -> None:
    from mcp_brasil.datasets.spu_siapa.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("top_municipios_siapa", {"uf": "RJ", "top": 5})
    text = _text(r)
    assert "Rio de Janeiro" in text


@pytest.mark.asyncio
async def test_tools_and_resources_registered(tmp_cache: Path) -> None:
    from mcp_brasil.datasets.spu_siapa.server import mcp

    async with Client(mcp) as c:
        tools = {t.name for t in await c.list_tools()}
        resources = {str(r.uri) for r in await c.list_resources()}
        prompts = {p.name for p in await c.list_prompts()}

    assert "info_spu_siapa" in tools
    assert "buscar_imoveis_siapa" in tools
    assert "resumo_regime_siapa" in tools
    assert "resumo_conceituacao_siapa" in tools
    assert "resumo_uf_siapa" in tools
    assert "top_municipios_siapa" in tools
    assert "refrescar_spu_siapa" in tools
    assert {"data://schema", "data://valores", "data://info"}.issubset(resources)
    assert {"auditoria_patrimonio_uf", "imoveis_aforamento_rio"}.issubset(prompts)


def test_dataset_spec_gating(monkeypatch: pytest.MonkeyPatch) -> None:
    """When MCP_BRASIL_DATASETS is unset, FEATURE_META.enabled is False."""
    # The module was already imported with current env; we just verify the
    # logic by reloading.
    import importlib

    monkeypatch.setattr(settings, "DATASETS_ENABLED", [])
    import mcp_brasil.datasets.spu_siapa as mod

    importlib.reload(mod)
    assert mod.FEATURE_META.enabled is False

    monkeypatch.setattr(settings, "DATASETS_ENABLED", ["spu_siapa"])
    importlib.reload(mod)
    assert mod.FEATURE_META.enabled is True
