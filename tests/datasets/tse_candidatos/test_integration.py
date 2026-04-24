"""End-to-end tests for tse_candidatos with a small CSV fixture."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastmcp import Client

from mcp_brasil import settings

# 4-row mini-CSV with 50 columns following the real schema
_HEADERS = (
    '"DT_GERACAO";"HH_GERACAO";"ANO_ELEICAO";"CD_TIPO_ELEICAO";"NM_TIPO_ELEICAO";'
    '"NR_TURNO";"CD_ELEICAO";"DS_ELEICAO";"DT_ELEICAO";"TP_ABRANGENCIA";"SG_UF";'
    '"SG_UE";"NM_UE";"CD_CARGO";"DS_CARGO";"SQ_CANDIDATO";"NR_CANDIDATO";'
    '"NM_CANDIDATO";"NM_URNA_CANDIDATO";"NM_SOCIAL_CANDIDATO";"NR_CPF_CANDIDATO";'
    '"DS_EMAIL";"CD_SITUACAO_CANDIDATURA";"DS_SITUACAO_CANDIDATURA";'
    '"TP_AGREMIACAO";"NR_PARTIDO";"SG_PARTIDO";"NM_PARTIDO";"NR_FEDERACAO";'
    '"NM_FEDERACAO";"SG_FEDERACAO";"DS_COMPOSICAO_FEDERACAO";"SQ_COLIGACAO";'
    '"NM_COLIGACAO";"DS_COMPOSICAO_COLIGACAO";"SG_UF_NASCIMENTO";"DT_NASCIMENTO";'
    '"NR_TITULO_ELEITORAL_CANDIDATO";"CD_GENERO";"DS_GENERO";"CD_GRAU_INSTRUCAO";'
    '"DS_GRAU_INSTRUCAO";"CD_ESTADO_CIVIL";"DS_ESTADO_CIVIL";"CD_COR_RACA";'
    '"DS_COR_RACA";"CD_OCUPACAO";"DS_OCUPACAO";"CD_SIT_TOT_TURNO";"DS_SIT_TOT_TURNO"'
)


def _row(**overrides: str) -> str:
    defaults = {
        "sg_uf": "SP",
        "nm_ue": "São Paulo",
        "ds_cargo": "PREFEITO",
        "sq_candidato": "1",
        "nr_candidato": "13",
        "nm_candidato": "FULANO DA SILVA",
        "nm_urna_candidato": "FULANO",
        "cpf": "12345678900",
        "email": "fulano@example.com",
        "sg_partido": "PT",
        "nm_partido": "PARTIDO DOS TRABALHADORES",
        "genero": "MASCULINO",
        "instrucao": "SUPERIOR COMPLETO",
        "estado_civil": "CASADO(A)",
        "raca": "BRANCA",
        "ocupacao": "ADVOGADO",
        "resultado": "ELEITO",
    }
    defaults.update(overrides)
    d = defaults
    return (
        f'"01/01/2024";"00:00:00";2024;2;"Eleição Ordinária";1;619;'
        f'"Eleições Municipais 2024";"06/10/2024";"MUNICIPAL";"{d["sg_uf"]}";'
        f'"00001";"{d["nm_ue"]}";11;"{d["ds_cargo"]}";{d["sq_candidato"]};'
        f"{d['nr_candidato']};"
        f'"{d["nm_candidato"]}";"{d["nm_urna_candidato"]}";"#NULO";'
        f'"{d["cpf"]}";"{d["email"]}";2;"DEFERIDO";"PARTIDO ISOLADO";13;'
        f'"{d["sg_partido"]}";"{d["nm_partido"]}";-1;"#NULO";"#NULO";"#NULO";'
        f'-1;"PARTIDO ISOLADO";"PT";"SP";"01/01/1970";"123456789012";2;'
        f'"{d["genero"]}";8;"{d["instrucao"]}";3;"{d["estado_civil"]}";"01";'
        f'"{d["raca"]}";1;"{d["ocupacao"]}";1;"{d["resultado"]}"'
    )


_FIXTURE = (
    _HEADERS
    + "\n"
    + _row(sq_candidato="1", nm_urna_candidato="FULANO", sg_partido="PT", sg_uf="SP")
    + "\n"
    + _row(
        sq_candidato="2",
        nm_urna_candidato="BELTRANA",
        nm_candidato="BELTRANA DE SOUZA",
        sg_partido="PL",
        genero="FEMININO",
        resultado="NÃO ELEITO",
        sg_uf="RJ",
        nm_ue="Rio de Janeiro",
    )
    + "\n"
    + _row(
        sq_candidato="3",
        nm_urna_candidato="CICRANO",
        ds_cargo="VEREADOR",
        sg_partido="MDB",
        sg_uf="MG",
        nm_ue="Belo Horizonte",
    )
    + "\n"
)


@pytest.fixture
def tmp_cache(monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tempfile.mkdtemp(prefix="mcp-brasil-tse-test-")
    monkeypatch.setattr(settings, "DATASET_CACHE_DIR", d)
    monkeypatch.setattr(settings, "DATASETS_ENABLED", ["tse_candidatos"])
    return Path(d)


@pytest.fixture
def patch_download(tmp_cache: Path):
    """Write the fixture only for 2024; other years stage an empty CSV."""

    def fake_extract(
        url: str,
        dest: Path,
        *,
        zip_member: str,
        timeout: float,
        source_encoding: str = "utf-8",
    ) -> int:
        if "2024" in zip_member or "2024" in url:
            dest.write_text(_FIXTURE, encoding="utf-8")
        else:
            dest.write_text(_HEADERS + "\n", encoding="utf-8")
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
async def test_resumo_cargo_partido(tmp_cache, patch_download) -> None:
    from mcp_brasil.datasets.tse_candidatos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("resumo_cargo_partido", {"cargo": "PREFEITO"})
    t = _text(r)
    assert "PT" in t
    assert "PL" in t
    assert "MDB" not in t  # MDB é VEREADOR, não PREFEITO


@pytest.mark.asyncio
async def test_buscar_candidatos_pii_masked(tmp_cache, patch_download) -> None:
    from mcp_brasil.datasets.tse_candidatos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("buscar_candidatos", {"partido": "PT", "limite": 5})
    t = _text(r)
    assert "FULANO" in t
    # CPF e e-mail não aparecem na tabela rendered, mas também não devem vazar
    # raw no corpo da string (estão mascarados em redact_rows).
    assert "12345678900" not in t
    assert "fulano@example.com" not in t


@pytest.mark.asyncio
async def test_buscar_candidatos_accent_insensitive(tmp_cache, patch_download) -> None:
    from mcp_brasil.datasets.tse_candidatos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("buscar_candidatos", {"municipio": "São Paulo", "limite": 5})
    t = _text(r)
    assert "FULANO" in t


@pytest.mark.asyncio
async def test_valores_distintos_candidatos(tmp_cache, patch_download) -> None:
    from mcp_brasil.datasets.tse_candidatos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("valores_distintos_candidatos", {"coluna": "sg_partido"})
    t = _text(r)
    assert "PT" in t and "PL" in t and "MDB" in t


@pytest.mark.asyncio
async def test_valores_distintos_invalid_column(tmp_cache) -> None:
    from mcp_brasil.datasets.tse_candidatos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("valores_distintos_candidatos", {"coluna": "senha_secreta"})
    assert "não permitida" in _text(r)


@pytest.mark.asyncio
async def test_top_municipios(tmp_cache, patch_download) -> None:
    from mcp_brasil.datasets.tse_candidatos.server import mcp

    async with Client(mcp) as c:
        r = await c.call_tool("top_municipios_candidatos", {"uf": "SP", "top": 5})
    t = _text(r)
    assert "São Paulo" in t or "Sao Paulo" in t


@pytest.mark.asyncio
async def test_tools_and_resources_registered(tmp_cache) -> None:
    from mcp_brasil.datasets.tse_candidatos.server import mcp

    async with Client(mcp) as c:
        tools = {t.name for t in await c.list_tools()}
        resources = {str(x.uri) for x in await c.list_resources()}
    assert {
        "info_tse_candidatos",
        "buscar_candidatos",
        "valores_distintos_candidatos",
        "resumo_cargo_partido",
        "resumo_perfil_eleitos",
        "top_municipios_candidatos",
        "refrescar_tse_candidatos",
    }.issubset(tools)
    assert {"data://info", "data://valores", "data://schema"}.issubset(resources)
