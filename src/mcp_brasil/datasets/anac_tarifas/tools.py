"""Canned SQL query tools for anac_tarifas dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status
from mcp_brasil._shared.formatting import format_brl, format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE


async def info_anac_tarifas(ctx: Context) -> str:
    """Estado do cache local do dataset ANAC Tarifas.

    Retorna métricas (linhas, tamanho, frescor). Se o cache não existir,
    sugere rodar scripts/refresh_anac_tarifas.py.

    Returns:
        Métricas do cache ou instruções de popular.
    """
    await ctx.info("Consultando cache ANAC Tarifas...")
    st = await get_status(DATASET_SPEC)
    if not st["cached"]:
        return (
            "**ANAC Tarifas — cache não populado**\n\n"
            "Rode antes de consultar:\n\n"
            "```\n"
            "uv sync --group dev\n"
            "uv run playwright install chromium\n"
            "uv run python scripts/refresh_anac_tarifas.py --ano 2024\n"
            "```\n"
        )
    return (
        "**ANAC Tarifas Aéreas Domésticas — cache**\n\n"
        f"- Cached: sim\n"
        f"- Linhas: {format_number_br(st['row_count'], 0)}\n"
        f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB\n"
        f"- Fresh (TTL={st['ttl_days']}d): {'sim' if st['fresh'] else 'não'}\n"
    )


async def preco_medio_rota(
    ctx: Context,
    origem: str,
    destino: str,
    ano: int | None = None,
) -> str:
    """Preço médio praticado numa rota (origem ICAO → destino ICAO).

    Args:
        origem: ICAO do aeroporto origem (ex: SBGR, SBGL).
        destino: ICAO do aeroporto destino (ex: SBRF, SBBR).
        ano: Ano (opcional — se omitido agrega todos os anos em cache).

    Returns:
        Tabela mês x bilhetes x tarifa média x tarifa mín x máx.
    """
    o = origem.upper().strip()
    d = destino.upper().strip()
    await ctx.info(f"Preço médio {o}→{d} {ano or ''}...")
    where = ["origem = ?", "destino = ?"]
    params: list[Any] = [o, d]
    if ano is not None:
        where.append("ano = ?")
        params.append(int(ano))
    sql = (
        "SELECT ano, mes, COUNT(*) AS n, "
        "AVG(tarifa) AS preco_medio, "
        "MIN(tarifa) AS preco_min, "
        "MAX(tarifa) AS preco_max "
        f'FROM "{DATASET_TABLE}" '
        f"WHERE {' AND '.join(where)} "
        "AND tarifa IS NOT NULL AND tarifa > 0 "
        "GROUP BY ano, mes ORDER BY ano, mes"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return f"Sem tarifas registradas para {o}→{d} (ano={ano or 'todos'})."
    body = [
        (
            str(r.get("ano")),
            f"{int(r.get('mes') or 0):02d}",
            format_number_br(int(r.get("n") or 0), 0),
            format_brl(float(r.get("preco_medio") or 0)),
            format_brl(float(r.get("preco_min") or 0)),
            format_brl(float(r.get("preco_max") or 0)),
        )
        for r in rows
    ]
    return f"**Tarifas {o} → {d}** — {len(rows)} mês(es) em cache\n\n" + markdown_table(
        ["Ano", "Mês", "Bilhetes", "Preço médio", "Min", "Max"], body
    )


async def preco_por_empresa(
    ctx: Context,
    origem: str,
    destino: str,
    ano: int | None = None,
) -> str:
    """Preço médio por companhia numa rota — comparativo concorrencial.

    Args:
        origem: ICAO origem.
        destino: ICAO destino.
        ano: Ano (opcional).

    Returns:
        Tabela empresa x bilhetes x preço médio x min x max.
    """
    o = origem.upper().strip()
    d = destino.upper().strip()
    await ctx.info(f"Preço por empresa na rota {o}→{d} {ano or ''}...")
    where = ["origem = ?", "destino = ?"]
    params: list[Any] = [o, d]
    if ano is not None:
        where.append("ano = ?")
        params.append(int(ano))
    sql = (
        "SELECT empresa, COUNT(*) AS n, "
        "AVG(tarifa) AS preco_medio, "
        "MIN(tarifa) AS preco_min, "
        "MAX(tarifa) AS preco_max "
        f'FROM "{DATASET_TABLE}" '
        f"WHERE {' AND '.join(where)} "
        "AND tarifa IS NOT NULL AND tarifa > 0 "
        "GROUP BY empresa ORDER BY n DESC"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return f"Sem tarifas para {o}→{d}."
    body = [
        (
            r.get("empresa") or "—",
            format_number_br(int(r.get("n") or 0), 0),
            format_brl(float(r.get("preco_medio") or 0)),
            format_brl(float(r.get("preco_min") or 0)),
            format_brl(float(r.get("preco_max") or 0)),
        )
        for r in rows
    ]
    return f"**Companhias na rota {o} → {d}** ({ano or 'todos anos'})\n\n" + markdown_table(
        ["Empresa", "Bilhetes", "Preço médio", "Min", "Max"], body
    )


async def top_rotas_caras(
    ctx: Context,
    ano: int = 2024,
    top: int = 20,
    min_bilhetes: int = 1000,
) -> str:
    """Rotas com maior preço médio de bilhete.

    Args:
        ano: Ano (default 2024).
        top: Quantidade (padrão 20, máx 100).
        min_bilhetes: Mínimo de bilhetes vendidos pra entrar no ranking.

    Returns:
        Tabela rota x bilhetes x preço médio.
    """
    top = max(1, min(top, 100))
    await ctx.info(f"Top {top} rotas mais caras {ano}...")
    sql = (
        "SELECT origem, destino, COUNT(*) AS n, "
        "AVG(tarifa) AS preco_medio "
        f'FROM "{DATASET_TABLE}" '
        "WHERE ano = ? AND tarifa > 0 "
        "GROUP BY origem, destino "
        f"HAVING n >= {min_bilhetes} "
        "ORDER BY preco_medio DESC "
        f"LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql, [int(ano)])
    if not rows:
        return f"Sem dados pra {ano}."
    body = [
        (
            r.get("origem") or "—",
            r.get("destino") or "—",
            format_number_br(int(r.get("n") or 0), 0),
            format_brl(float(r.get("preco_medio") or 0)),
        )
        for r in rows
    ]
    return (
        f"**ANAC Tarifas — Top {len(rows)} rotas mais caras de {ano}** "
        f"(mínimo {min_bilhetes} bilhetes)\n\n"
        + markdown_table(["Origem", "Destino", "Bilhetes", "Preço médio"], body)
    )


async def evolucao_preco_empresa(
    ctx: Context,
    empresa: str,
    ano: int | None = None,
) -> str:
    """Evolução mensal do preço médio de uma companhia.

    Args:
        empresa: ICAO da empresa (ex: GLO=Gol, TAM/LAN=Latam, AZU=Azul).
        ano: Ano (opcional).

    Returns:
        Tabela mês x bilhetes x preço médio.
    """
    e = empresa.upper().strip()
    await ctx.info(f"Evolução preço {e} {ano or ''}...")
    where = ["empresa = ?"]
    params: list[Any] = [e]
    if ano is not None:
        where.append("ano = ?")
        params.append(int(ano))
    sql = (
        "SELECT ano, mes, COUNT(*) AS n, AVG(tarifa) AS preco_medio "
        f'FROM "{DATASET_TABLE}" '
        f"WHERE {' AND '.join(where)} "
        "AND tarifa > 0 "
        "GROUP BY ano, mes ORDER BY ano, mes"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return f"Sem tarifas da empresa {empresa}."
    body = [
        (
            str(r.get("ano")),
            f"{int(r.get('mes') or 0):02d}",
            format_number_br(int(r.get("n") or 0), 0),
            format_brl(float(r.get("preco_medio") or 0)),
        )
        for r in rows
    ]
    return f"**{empresa} — evolução mensal do preço médio**\n\n" + markdown_table(
        ["Ano", "Mês", "Bilhetes", "Preço médio"], body
    )


async def valores_distintos_tarifas(
    ctx: Context,
    coluna: str,
    top: int = 20,
) -> str:
    """Valores distintos (empresa, origem, destino).

    Args:
        coluna: Uma de: empresa, origem, destino, ano.
        top: Máx (padrão 20).

    Returns:
        Tabela valor x ocorrências.
    """
    allow = {"empresa", "origem", "destino", "ano"}
    if coluna not in allow:
        return f"Coluna '{coluna}' não permitida. Use: {sorted(allow)}"
    top = max(1, min(top, 100))
    sql = (
        f'SELECT "{coluna}" AS v, COUNT(*) AS n '
        f'FROM "{DATASET_TABLE}" GROUP BY "{coluna}" '
        f"ORDER BY n DESC LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return f"Sem valores em {coluna}."
    body = [(str(r.get("v") or "(null)"), format_number_br(int(r.get("n") or 0), 0)) for r in rows]
    return f"**ANAC Tarifas — distintos em `{coluna}`**\n\n" + markdown_table(
        ["Valor", "Ocorrências"], body
    )
