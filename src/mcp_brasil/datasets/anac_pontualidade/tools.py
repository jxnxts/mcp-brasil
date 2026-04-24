"""Canned SQL query tools for anac_pontualidade dataset."""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status
from mcp_brasil._shared.formatting import format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE

# Converte string "9,68" ou "12.5" em DOUBLE
_PCT = "TRY_CAST(REPLACE(REPLACE({col}, '.', ''), ',', '.') AS DOUBLE)"


async def info_anac_pontualidade(ctx: Context) -> str:
    """Estado do cache local do dataset ANAC Pontualidade.

    Returns:
        Métricas do cache (linhas, tamanho, frescor).
    """
    await ctx.info("Consultando estado do cache ANAC Pontualidade...")
    st = await get_status(DATASET_SPEC)
    return (
        "**ANAC Pontualidade (Res. 218) — cache**\n\n"
        f"- Cached: {'sim' if st['cached'] else 'não'}\n"
        f"- Linhas: {format_number_br(st['row_count'], 0) if st['cached'] else '—'}\n"
        f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB\n"
        f"- Fresh (TTL={st['ttl_days']}d): {'sim' if st['fresh'] else 'não'}\n"
    )


async def ranking_empresas_atraso(ctx: Context, top: int = 20) -> str:
    """Ranking de empresas com maior % médio de atrasos (>30min).

    Args:
        top: Quantidade (padrão 20, máximo 50).

    Returns:
        Tabela empresa x voos x % cancelamento médio x % atraso 30min x 60min.
    """
    top = max(1, min(top, 50))
    await ctx.info(f"Top {top} empresas por atraso...")
    sql = (
        "SELECT empresa_aerea AS empresa, "
        "SUM(TRY_CAST(etapas_previstas AS BIGINT)) AS voos, "
        f"AVG({_PCT.format(col='percentuais_de_cancelamentos')}) AS pct_canc, "
        f"AVG({_PCT.format(col='percentuais_de_atrasos_superiores_a_30_minutos')}) "
        "AS pct_30m, "
        f"AVG({_PCT.format(col='percentuais_de_atrasos_superiores_a_60_minutos')}) "
        "AS pct_60m "
        f'FROM "{DATASET_TABLE}" '
        "WHERE empresa_aerea IS NOT NULL "
        "GROUP BY empresa "
        "HAVING voos > 100 "
        "ORDER BY pct_30m DESC NULLS LAST "
        f"LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return "Sem dados."
    body = []
    for r in rows:
        body.append(
            (
                (r.get("empresa") or "—")[:40],
                format_number_br(int(r.get("voos") or 0), 0),
                f"{r.get('pct_canc') or 0:.2f}%",
                f"{r.get('pct_30m') or 0:.2f}%",
                f"{r.get('pct_60m') or 0:.2f}%",
            )
        )
    return f"**ANAC — Top {len(rows)} empresas por atraso médio (>30min)**\n\n" + markdown_table(
        ["Empresa", "Etapas", "% Canc.", "% >30min", "% >60min"], body
    )


async def rotas_mais_atrasadas(ctx: Context, top: int = 25, min_voos: int = 50) -> str:
    """Rotas com maior % de atraso >30min.

    Args:
        top: Quantidade (padrão 25, máximo 100).
        min_voos: Mínimo de etapas previstas para incluir a rota (filtra rotas raras).

    Returns:
        Tabela origem→destino x voos x % atraso x % cancelamento.
    """
    top = max(1, min(top, 100))
    min_voos = max(1, min_voos)
    await ctx.info(f"Top {top} rotas mais atrasadas...")
    sql = (
        "SELECT aeroporto_origem_designador_oaci AS orig, "
        "aeroporto_destino_designador_oaci AS dest, "
        "SUM(TRY_CAST(etapas_previstas AS BIGINT)) AS voos, "
        f"AVG({_PCT.format(col='percentuais_de_atrasos_superiores_a_30_minutos')}) "
        "AS pct_30m, "
        f"AVG({_PCT.format(col='percentuais_de_cancelamentos')}) AS pct_canc "
        f'FROM "{DATASET_TABLE}" '
        "WHERE aeroporto_origem_designador_oaci IS NOT NULL "
        "AND aeroporto_destino_designador_oaci IS NOT NULL "
        "GROUP BY orig, dest "
        f"HAVING voos >= {min_voos} "
        "ORDER BY pct_30m DESC NULLS LAST "
        f"LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return "Sem dados."
    body = [
        (
            r.get("orig") or "—",
            r.get("dest") or "—",
            format_number_br(int(r.get("voos") or 0), 0),
            f"{r.get('pct_30m') or 0:.2f}%",
            f"{r.get('pct_canc') or 0:.2f}%",
        )
        for r in rows
    ]
    return (
        f"**ANAC — Top {len(rows)} rotas mais atrasadas** "
        f"(mínimo {min_voos} etapas)\n\n"
        + markdown_table(["Origem", "Destino", "Voos", "% >30min", "% Canc."], body)
    )


async def pontualidade_aeroporto_partida(
    ctx: Context,
    icao_aerodromo: str,
    top: int = 20,
) -> str:
    """Pontualidade das partidas de um aeroporto, agregada por destino.

    Args:
        icao_aerodromo: ICAO do aeroporto de origem (ex: SBGR, SBGL, SBBR).
        top: Máx destinos (padrão 20).

    Returns:
        Tabela destino x voos x % atraso x % cancelamento.
    """
    top = max(1, min(top, 50))
    needle = icao_aerodromo.upper().strip()
    await ctx.info(f"Partidas de {needle} — pontualidade...")
    sql = (
        "SELECT aeroporto_destino_designador_oaci AS dest, "
        "SUM(TRY_CAST(etapas_previstas AS BIGINT)) AS voos, "
        f"AVG({_PCT.format(col='percentuais_de_atrasos_superiores_a_30_minutos')}) "
        "AS pct_30m, "
        f"AVG({_PCT.format(col='percentuais_de_atrasos_superiores_a_60_minutos')}) "
        "AS pct_60m, "
        f"AVG({_PCT.format(col='percentuais_de_cancelamentos')}) AS pct_canc "
        f'FROM "{DATASET_TABLE}" '
        "WHERE UPPER(aeroporto_origem_designador_oaci) = ? "
        "GROUP BY dest "
        "ORDER BY voos DESC NULLS LAST "
        f"LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql, [needle])
    if not rows:
        return f"Sem partidas de {icao_aerodromo}."
    body = [
        (
            r.get("dest") or "—",
            format_number_br(int(r.get("voos") or 0), 0),
            f"{r.get('pct_30m') or 0:.2f}%",
            f"{r.get('pct_60m') or 0:.2f}%",
            f"{r.get('pct_canc') or 0:.2f}%",
        )
        for r in rows
    ]
    return f"**Partidas de {icao_aerodromo}** — pontualidade por destino\n\n" + markdown_table(
        ["Destino", "Voos", "% >30min", "% >60min", "% Canc."], body
    )


async def consultar_voo_pontualidade(
    ctx: Context,
    empresa_prefix: str,
    numero_voo: str,
) -> str:
    """Pontualidade de um voo específico (empresa + número) em todas as rotas.

    Args:
        empresa_prefix: Código ICAO ou parte do nome da empresa (ex: "GLO", "LATAM", "AZUL").
        numero_voo: Número do voo (ex: "0963").

    Returns:
        Tabela rota x voos x % atraso x % cancelamento.
    """
    await ctx.info(f"Voo {empresa_prefix} {numero_voo}...")
    sql = (
        "SELECT empresa_aerea AS empresa, "
        "aeroporto_origem_designador_oaci AS orig, "
        "aeroporto_destino_designador_oaci AS dest, "
        "etapas_previstas AS voos, "
        "percentuais_de_cancelamentos AS canc, "
        "percentuais_de_atrasos_superiores_a_30_minutos AS atr30, "
        "percentuais_de_atrasos_superiores_a_60_minutos AS atr60 "
        f'FROM "{DATASET_TABLE}" '
        "WHERE UPPER(empresa_aerea) LIKE ? "
        "AND TRIM(n_voo) = ? "
        "LIMIT 100"
    )
    rows = await executar_query(
        DATASET_SPEC,
        sql,
        [f"%{empresa_prefix.upper()}%", numero_voo.strip()],
    )
    if not rows:
        return (
            f"Voo '{empresa_prefix} {numero_voo}' não encontrado. "
            "Confira o código ICAO da empresa (ex: GLO, TAM, AZU)."
        )
    body = [
        (
            (r.get("empresa") or "—")[:28],
            r.get("orig") or "—",
            r.get("dest") or "—",
            r.get("voos") or "—",
            f"{r.get('canc') or '—'}%",
            f"{r.get('atr30') or '—'}%",
            f"{r.get('atr60') or '—'}%",
        )
        for r in rows
    ]
    return (
        f"**Voo {empresa_prefix} {numero_voo}** — {len(rows)} rota(s) listada(s)\n\n"
        + markdown_table(
            ["Empresa", "Origem", "Destino", "Voos", "% Canc.", "% >30min", "% >60min"],
            body,
        )
    )
