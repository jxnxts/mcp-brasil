"""Canned SQL query tools for tse_votacao dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status
from mcp_brasil._shared.formatting import format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE

_VOTOS_INT = "TRY_CAST(qt_votos_nominais AS BIGINT)"


async def info_tse_votacao(ctx: Context) -> str:
    """Estado do cache local do dataset TSE votação.

    Returns:
        Métricas do cache local.
    """
    await ctx.info("Consultando estado do cache TSE votação...")
    st = await get_status(DATASET_SPEC)
    return (
        "**TSE votação 2014-2024 — cache**\n\n"
        f"- Cached: {'sim' if st['cached'] else 'não'}\n"
        f"- Linhas: {format_number_br(st['row_count'], 0) if st['cached'] else '—'}\n"
        f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB\n"
        f"- Fresh (TTL={st['ttl_days']}d): {'sim' if st['fresh'] else 'não'}\n"
    )


async def votos_candidato(
    ctx: Context,
    sq_candidato: str,
) -> str:
    """Retorna os votos recebidos por um candidato em todos os municípios.

    Args:
        sq_candidato: ID do candidato (sq_candidato de tse_candidatos).

    Returns:
        Tabela com ano, UF, município, zona, votos, resultado.
    """
    await ctx.info(f"Buscando votos do candidato {sq_candidato}...")
    sql = (
        "SELECT ano_eleicao, sg_uf, nm_municipio, nr_zona, "
        f"{_VOTOS_INT} AS votos, ds_sit_tot_turno "
        f'FROM "{DATASET_TABLE}" '
        "WHERE CAST(sq_candidato AS VARCHAR) = ? "
        "ORDER BY ano_eleicao DESC, votos DESC NULLS LAST"
    )
    rows = await executar_query(DATASET_SPEC, sql, [str(sq_candidato).strip()])
    if not rows:
        return f"Nenhum voto encontrado para sq_candidato={sq_candidato!r}."

    total = sum(int(r.get("votos") or 0) for r in rows)
    table = [
        (
            str(r.get("ano_eleicao") or "—"),
            r.get("sg_uf") or "—",
            (r.get("nm_municipio") or "—")[:25],
            str(r.get("nr_zona") or "—"),
            format_number_br(int(r.get("votos") or 0), 0),
            (r.get("ds_sit_tot_turno") or "—")[:18],
        )
        for r in rows[:100]
    ]
    extra = f"\n\n(mostrando 100 de {len(rows)} linhas)" if len(rows) > 100 else ""
    return (
        f"**Votos do candidato {sq_candidato}** — "
        f"{format_number_br(total, 0)} votos no total{extra}\n\n"
        + markdown_table(["Ano", "UF", "Município", "Zona", "Votos", "Resultado"], table)
    )


async def top_votados_cargo(
    ctx: Context,
    cargo: str = "PRESIDENTE",
    ano: int | None = None,
    uf: str | None = None,
    limite: int = 20,
) -> str:
    """Ranking dos mais votados num cargo.

    Args:
        cargo: Cargo (ex: 'PRESIDENTE', 'GOVERNADOR', 'DEPUTADO FEDERAL',
            'PREFEITO').
        ano: Ano eleitoral (2014, 2016, 2018, 2020, 2022, 2024). Padrão: todos.
        uf: UF opcional.
        limite: Máx. (padrão 20, máx 100).

    Returns:
        Tabela com ano, nome, partido, UF/município, total de votos.
    """
    limite = max(1, min(limite, 100))
    await ctx.info(f"Top {limite} votados — {cargo} {ano or ''} {uf or ''}...")
    where: list[str] = ["strip_accents(ds_cargo) ILIKE strip_accents(?)"]
    params: list[Any] = [f"%{cargo}%"]
    if ano is not None:
        where.append("CAST(ano_eleicao AS INTEGER) = ?")
        params.append(int(ano))
    if uf:
        where.append("TRIM(sg_uf) = ?")
        params.append(uf.strip().upper())
    sql = (
        "SELECT ano_eleicao, nm_urna_candidato, sg_partido, sg_uf, nm_ue, "
        f"SUM({_VOTOS_INT}) AS votos "
        f'FROM "{DATASET_TABLE}" WHERE {" AND ".join(where)} '
        "GROUP BY ano_eleicao, nm_urna_candidato, sg_partido, sg_uf, nm_ue "
        f"ORDER BY votos DESC NULLS LAST LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return f"Sem votos encontrados para {cargo} (ano={ano}, uf={uf})."
    table = [
        (
            str(r.get("ano_eleicao") or "—"),
            (r.get("nm_urna_candidato") or "—")[:28],
            r.get("sg_partido") or "—",
            r.get("sg_uf") or "—",
            (r.get("nm_ue") or "—")[:18],
            format_number_br(int(r.get("votos") or 0), 0),
        )
        for r in rows
    ]
    titulo = f"{cargo} — {ano or 'todos'} / {uf or 'BR'}"
    return f"**TSE votação — Top {len(rows)} votados ({titulo})**\n\n" + markdown_table(
        ["Ano", "Nome", "Partido", "UF", "Município", "Votos"], table
    )


async def ranking_municipio(
    ctx: Context,
    municipio: str,
    uf: str,
    cargo: str = "PREFEITO",
    ano: int | None = None,
    limite: int = 15,
) -> str:
    """Ranking de candidatos num município específico.

    Args:
        municipio: Nome do município.
        uf: UF (obrigatório para desambiguar).
        cargo: Cargo (default PREFEITO).
        ano: Ano eleitoral (default: todos).
        limite: Máx candidatos (padrão 15).

    Returns:
        Tabela ano x nome x partido x votos x resultado.
    """
    limite = max(1, min(limite, 50))
    await ctx.info(f"Ranking {municipio}/{uf} — {cargo} {ano or 'todos'}...")
    where: list[str] = [
        "strip_accents(nm_municipio) ILIKE strip_accents(?)",
        "TRIM(sg_uf) = ?",
        "strip_accents(ds_cargo) ILIKE strip_accents(?)",
    ]
    params: list[Any] = [f"%{municipio}%", uf.strip().upper(), f"%{cargo}%"]
    if ano is not None:
        where.append("CAST(ano_eleicao AS INTEGER) = ?")
        params.append(int(ano))
    sql = (
        "SELECT ano_eleicao, nm_urna_candidato, sg_partido, "
        f"SUM({_VOTOS_INT}) AS votos, "
        "ANY_VALUE(ds_sit_tot_turno) AS resultado "
        f'FROM "{DATASET_TABLE}" WHERE {" AND ".join(where)} '
        "GROUP BY ano_eleicao, nm_urna_candidato, sg_partido "
        f"ORDER BY ano_eleicao DESC, votos DESC NULLS LAST LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return f"Sem votos em {municipio}/{uf} para {cargo}."
    table = [
        (
            str(r.get("ano_eleicao") or "—"),
            (r.get("nm_urna_candidato") or "—")[:28],
            r.get("sg_partido") or "—",
            format_number_br(int(r.get("votos") or 0), 0),
            (r.get("resultado") or "—")[:18],
        )
        for r in rows
    ]
    return f"**{municipio}/{uf} — {cargo} {ano or '(todos os anos)'}**\n\n" + markdown_table(
        ["Ano", "Nome", "Partido", "Votos", "Resultado"], table
    )


async def evolucao_partido(
    ctx: Context,
    partido: str,
    cargo: str = "DEPUTADO FEDERAL",
) -> str:
    """Evolução histórica de votos de um partido por cargo.

    Args:
        partido: Sigla (ex: 'PT', 'PL', 'MDB').
        cargo: Cargo comparável cross-year (ex: 'DEPUTADO FEDERAL', 'PREFEITO').

    Returns:
        Tabela com ano x candidatos x votos totais x eleitos.
    """
    await ctx.info(f"Evolução {partido} — {cargo}...")
    sql = (
        "SELECT CAST(ano_eleicao AS INTEGER) AS ano, "
        "COUNT(DISTINCT sq_candidato) AS candidatos, "
        f"SUM({_VOTOS_INT}) AS votos, "
        "SUM(CASE WHEN UPPER(ds_sit_tot_turno) LIKE 'ELEITO%' THEN 1 ELSE 0 END) "
        "AS linhas_eleitas "
        f'FROM "{DATASET_TABLE}" '
        "WHERE UPPER(sg_partido) = ? "
        "AND strip_accents(ds_cargo) ILIKE strip_accents(?) "
        "AND ano_eleicao IS NOT NULL "
        "GROUP BY CAST(ano_eleicao AS INTEGER) ORDER BY ano DESC"
    )
    rows = await executar_query(DATASET_SPEC, sql, [partido.strip().upper(), f"%{cargo}%"])
    if not rows:
        return f"Sem dados para {partido} / {cargo}."
    table = [
        (
            str(r.get("ano") or "—"),
            format_number_br(int(r.get("candidatos") or 0), 0),
            format_number_br(int(r.get("votos") or 0), 0),
            format_number_br(int(r.get("linhas_eleitas") or 0), 0),
        )
        for r in rows
    ]
    return (
        f"**TSE votação — evolução {partido} / {cargo}**\n\n"
        + markdown_table(["Ano", "Candidatos", "Total de votos", "Linhas eleitas"], table)
        + "\n\n*Linhas eleitas = contagem de combinações (candidato x município x zona) "
        "rotuladas ELEITO. Para candidatos distintos eleitos, use `buscar_candidatos`.*"
    )


async def soma_votos_uf(
    ctx: Context,
    ano: int,
    cargo: str = "DEPUTADO FEDERAL",
) -> str:
    """Votos totais por UF num cargo e ano.

    Args:
        ano: Ano eleitoral (obrigatório).
        cargo: Cargo (default DEPUTADO FEDERAL).

    Returns:
        Tabela UF x votos totais x candidatos.
    """
    await ctx.info(f"Soma de votos por UF — {cargo} {ano}...")
    sql = (
        "SELECT sg_uf, COUNT(DISTINCT sq_candidato) AS cand, "
        f"SUM({_VOTOS_INT}) AS votos "
        f'FROM "{DATASET_TABLE}" '
        "WHERE CAST(ano_eleicao AS INTEGER) = ? "
        "AND strip_accents(ds_cargo) ILIKE strip_accents(?) "
        "GROUP BY sg_uf ORDER BY votos DESC NULLS LAST"
    )
    rows = await executar_query(DATASET_SPEC, sql, [int(ano), f"%{cargo}%"])
    if not rows:
        return f"Sem votos para {cargo} em {ano}."
    table = [
        (
            r.get("sg_uf") or "—",
            format_number_br(int(r.get("cand") or 0), 0),
            format_number_br(int(r.get("votos") or 0), 0),
        )
        for r in rows
    ]
    return f"**{cargo} {ano} — votos por UF**\n\n" + markdown_table(
        ["UF", "Candidatos", "Votos totais"], table
    )
