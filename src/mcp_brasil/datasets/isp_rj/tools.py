"""Canned SQL tools for ISP-RJ dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status, refresh_dataset
from mcp_brasil._shared.formatting import format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE
from .constants import COLUNAS_DISTINCT_PERMITIDAS, INDICADORES_PRINCIPAIS


async def info_isp_rj(ctx: Context) -> str:
    """Estado do cache local do ISP-RJ."""
    await ctx.info("Consultando cache ISP-RJ...")
    st = await get_status(DATASET_SPEC)
    return "\n".join(
        [
            "**ISP-RJ — estado do cache**",
            "",
            f"- Cached: {'sim' if st['cached'] else 'não'}",
            f"- Linhas: {format_number_br(st['row_count'], 0) if st['cached'] else '—'}",
            f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB",
            "- Idade: "
            + (f"{st['age_days']:.2f} dias" if st.get("age_days") is not None else "—"),
        ]
    )


async def refrescar_isp_rj(ctx: Context) -> str:
    """Força re-download da base ISP-RJ."""
    await ctx.info("Re-baixando ISP-RJ...")
    m = await refresh_dataset(DATASET_SPEC)
    return (
        f"**ISP-RJ atualizado** — {format_number_br(m.row_count, 0)} linhas, "
        f"{m.size_bytes / 1024 / 1024:.1f} MB"
    )


async def valores_distintos_isp(coluna: str, limite: int = 100) -> str:
    """Valores distintos de uma coluna categórica.

    Args:
        coluna: Uma de cisp, aisp, risp, munic, mcirc, regiao, ano, mes.
        limite: Padrão 100, máx 500.
    """
    if coluna not in COLUNAS_DISTINCT_PERMITIDAS:
        return f"Coluna '{coluna}' não permitida. Use: {sorted(COLUNAS_DISTINCT_PERMITIDAS)}"
    limite = max(1, min(limite, 500))
    sql = (
        f'SELECT "{coluna}" AS valor, COUNT(*) AS total '
        f'FROM "{DATASET_TABLE}" WHERE "{coluna}" IS NOT NULL '
        f'GROUP BY "{coluna}" ORDER BY total DESC LIMIT {limite}'
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return "Nenhum valor."
    return markdown_table(
        [coluna, "ocorrencias"],
        [(r["valor"], format_number_br(int(r["total"]), 0)) for r in rows],
    )


async def indicadores_municipio(
    ctx: Context,
    municipio: str,
    ano: int,
    mes: int | None = None,
) -> str:
    """Indicadores principais de um município no RJ em um período.

    Args:
        municipio: Nome do município (substring, accent-insensitive).
        ano: Ano de referência (ex: 2024).
        mes: Mês (1-12). Omita para ano inteiro (somado).
    """
    # Query only columns that actually exist (ISP schema evolves over time).
    schema = await executar_query(DATASET_SPEC, f'DESCRIBE "{DATASET_TABLE}"')
    existing = {str(r.get("column_name") or r.get("name") or "").lower() for r in schema}
    usable = [c for c in INDICADORES_PRINCIPAIS if c in existing]
    if not usable:
        return "Dataset não contém nenhum dos indicadores curados."
    cols_sum = ", ".join(f"SUM({c}) AS {c}" for c in usable)
    where = ["strip_accents(munic) ILIKE strip_accents(?)", "ano = ?"]
    params: list[Any] = [f"%{municipio}%", ano]
    if mes is not None:
        where.append("mes = ?")
        params.append(mes)
    sql = (
        f"SELECT munic, {cols_sum} "
        f'FROM "{DATASET_TABLE}" WHERE {" AND ".join(where)} '
        "GROUP BY munic"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return f"Sem dados para '{municipio}' em {ano}."
    r = rows[0]
    periodo = f"{mes:02d}/{ano}" if mes else str(ano)
    lines = [f"**{r.get('munic')} — {periodo}**", ""]
    for ind in INDICADORES_PRINCIPAIS:
        v = r.get(ind)
        if v is None:
            continue
        try:
            n = int(v)
        except (TypeError, ValueError):
            n = 0
        if n > 0:
            lines.append(f"- **{ind}**: {format_number_br(n, 0)}")
    return "\n".join(lines)


async def ranking_municipios(
    ctx: Context,
    indicador: str,
    ano: int,
    limite: int = 15,
) -> str:
    """Ranking de municípios do RJ por um indicador criminal em um ano.

    Args:
        indicador: Nome da coluna (ex: 'hom_doloso', 'feminicidio', 'total_roubos').
        ano: Ano.
        limite: Top N (padrão 15, máx 92 — número de municípios do RJ).
    """
    if indicador not in INDICADORES_PRINCIPAIS:
        return (
            f"Indicador '{indicador}' não está na curadoria. "
            f"Válidos: {list(INDICADORES_PRINCIPAIS)}"
        )
    limite = max(1, min(limite, 92))
    sql = (
        f"SELECT munic, SUM({indicador}) AS total "
        f'FROM "{DATASET_TABLE}" WHERE ano = ? '
        f"GROUP BY munic ORDER BY total DESC LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, [ano])
    if not rows:
        return f"Sem dados para {ano}."
    table = [
        (
            (r.get("munic") or "—")[:30],
            format_number_br(int(r.get("total") or 0), 0),
        )
        for r in rows
    ]
    return f"**Ranking — {indicador} ({ano})**\n\n" + markdown_table(["Município", "Total"], table)


async def serie_temporal(
    ctx: Context,
    indicador: str,
    municipio: str | None = None,
    ano_inicio: int = 2020,
) -> str:
    """Série mensal de um indicador (estado todo ou município específico).

    Args:
        indicador: Nome do indicador (ex: 'hom_doloso').
        municipio: Filtra município (opcional — omita p/ RJ todo).
        ano_inicio: Ponto de partida (padrão 2020).
    """
    if indicador not in INDICADORES_PRINCIPAIS:
        return f"Indicador '{indicador}' não está na curadoria."
    where = ["ano >= ?"]
    params: list[Any] = [ano_inicio]
    if municipio:
        where.append("strip_accents(munic) ILIKE strip_accents(?)")
        params.append(f"%{municipio}%")
    sql = (
        f"SELECT ano, mes, SUM({indicador}) AS total "
        f'FROM "{DATASET_TABLE}" WHERE {" AND ".join(where)} '
        "GROUP BY ano, mes ORDER BY ano, mes"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return "Sem dados."
    table = [
        (
            f"{int(r.get('ano') or 0)}-{int(r.get('mes') or 0):02d}",
            format_number_br(int(r.get("total") or 0), 0),
        )
        for r in rows
    ]
    escopo = f"município '{municipio}'" if municipio else "RJ estado"
    return f"**{indicador} mensal — {escopo} (desde {ano_inicio})**\n\n" + markdown_table(
        ["Mês", indicador], table
    )
