"""Canned SQL query tools for tse_candidatos dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import (
    executar_query,
    get_status,
    redact_rows,
    refresh_dataset,
)
from mcp_brasil._shared.formatting import format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE
from .constants import COLUNAS_DISTINCT_PERMITIDAS


async def info_tse_candidatos(ctx: Context) -> str:
    """Estado do cache local do dataset TSE candidatos 2024.

    Returns:
        Tamanho, linhas, idade e fonte do cache.
    """
    await ctx.info("Consultando estado do cache TSE candidatos...")
    st = await get_status(DATASET_SPEC)
    return (
        "**TSE candidatos 2024 — cache**\n\n"
        f"- Cached: {'sim' if st['cached'] else 'não'}\n"
        f"- Linhas: {format_number_br(st['row_count'], 0) if st['cached'] else '—'}\n"
        f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB\n"
        f"- Idade: "
        + (f"{st['age_days']:.2f} dias" if st.get("age_days") is not None else "—")
        + f"\n- Fresh (TTL={st['ttl_days']}d): {'sim' if st['fresh'] else 'não'}\n"
        f"- Fonte: {st['source']}\n"
        f"- URL: {st['url']}\n"
    )


async def refrescar_tse_candidatos(ctx: Context) -> str:
    """Força re-download do dataset TSE candidatos (ignora TTL).

    Returns:
        Confirmação com contagem de linhas.
    """
    await ctx.info("Re-baixando TSE candidatos...")
    m = await refresh_dataset(DATASET_SPEC)
    return (
        f"**TSE candidatos atualizado** — "
        f"{format_number_br(m.row_count, 0)} linhas, "
        f"{m.size_bytes / 1024 / 1024:.1f} MB."
    )


async def valores_distintos_candidatos(
    ctx: Context,
    coluna: str,
    top: int = 30,
) -> str:
    """Descobre valores reais de uma coluna categórica de candidatos.

    Use antes de `buscar_candidatos` quando não souber os valores exatos
    de cargo / partido / grau_instrucao / situação etc.

    Args:
        coluna: Nome da coluna. Permitidas: sg_uf, ds_cargo, sg_partido,
            ds_genero, ds_grau_instrucao, ds_estado_civil, ds_cor_raca,
            ds_ocupacao, ds_situacao_candidatura, ds_sit_tot_turno,
            ds_eleicao, nm_tipo_eleicao, tp_agremiacao.
        top: Máximo de valores (padrão 30).

    Returns:
        Tabela com valor e contagem.
    """
    if coluna not in COLUNAS_DISTINCT_PERMITIDAS:
        return f"Coluna '{coluna}' não permitida. Use: " + ", ".join(
            sorted(COLUNAS_DISTINCT_PERMITIDAS)
        )
    top = max(1, min(top, 200))
    await ctx.info(f"Listando valores distintos de {coluna}...")
    sql = (
        f'SELECT "{coluna}" AS valor, COUNT(*) AS total '
        f'FROM "{DATASET_TABLE}" GROUP BY "{coluna}" '
        f"ORDER BY total DESC LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return f"Nenhum valor em '{coluna}'."
    body = [
        (
            str(r.get("valor")) if r.get("valor") is not None else "(null)",
            format_number_br(int(r.get("total") or 0), 0),
        )
        for r in rows
    ]
    return (
        f"**TSE candidatos — distintos em `{coluna}`** ({len(rows)} valores)\n\n"
        + markdown_table(["Valor", "Ocorrências"], body)
    )


async def buscar_candidatos(
    ctx: Context,
    nome: str | None = None,
    uf: str | None = None,
    municipio: str | None = None,
    cargo: str | None = None,
    partido: str | None = None,
    situacao_turno: str | None = None,
    genero: str | None = None,
    limite: int = 30,
) -> str:
    """Busca candidatos das eleições 2024 por filtros combinados.

    Pelo menos um filtro é recomendado. Todos os filtros de texto são
    case/accent-insensitive. CPF, título eleitoral e e-mail são
    **mascarados por padrão** — liberação via `MCP_BRASIL_LGPD_ALLOW_PII`.

    Args:
        nome: Nome do candidato (urna ou completo, substring).
        uf: Sigla UF (ex: 'SP', 'RJ').
        municipio: Nome do município (NM_UE no SIAPA é a unidade eleitoral).
        cargo: 'PREFEITO', 'VICE-PREFEITO', 'VEREADOR'.
        partido: Sigla do partido (ex: 'PT', 'PL', 'MDB').
        situacao_turno: Resultado — ex: 'ELEITO', 'NÃO ELEITO', 'SUPLENTE'.
        genero: 'MASCULINO' / 'FEMININO'.
        limite: Máximo de linhas (padrão 30, máx 200).

    Returns:
        Tabela com nome urna, cargo, partido, UF/município, gênero, resultado.
    """
    limite = max(1, min(limite, 200))
    await ctx.info(
        f"Buscando candidatos (nome={nome}, uf={uf}, municipio={municipio}, "
        f"cargo={cargo}, partido={partido}, situacao={situacao_turno})..."
    )

    where: list[str] = []
    params: list[Any] = []
    if nome:
        where.append(
            "(strip_accents(nm_candidato) ILIKE strip_accents(?) OR "
            "strip_accents(nm_urna_candidato) ILIKE strip_accents(?))"
        )
        params.extend([f"%{nome}%", f"%{nome}%"])
    if uf:
        where.append("TRIM(sg_uf) = ?")
        params.append(uf.strip().upper())
    if municipio:
        where.append("strip_accents(nm_ue) ILIKE strip_accents(?)")
        params.append(f"%{municipio}%")
    if cargo:
        where.append("strip_accents(ds_cargo) ILIKE strip_accents(?)")
        params.append(f"%{cargo}%")
    if partido:
        where.append("UPPER(sg_partido) = ?")
        params.append(partido.strip().upper())
    if situacao_turno:
        where.append("strip_accents(ds_sit_tot_turno) ILIKE strip_accents(?)")
        params.append(f"%{situacao_turno}%")
    if genero:
        where.append("strip_accents(ds_genero) ILIKE strip_accents(?)")
        params.append(f"%{genero}%")

    where_sql = " AND ".join(where) if where else "1=1"
    sql = (
        "SELECT sq_candidato, nm_candidato, nm_urna_candidato, ds_cargo, "
        "sg_partido, sg_uf, nm_ue, ds_genero, ds_grau_instrucao, "
        "ds_ocupacao, ds_sit_tot_turno, nr_cpf_candidato, ds_email "
        f'FROM "{DATASET_TABLE}" WHERE {where_sql} '
        f"ORDER BY sg_uf, ds_cargo, nm_urna_candidato LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    rows = redact_rows(rows, DATASET_SPEC)

    if not rows:
        return (
            "Nenhum candidato encontrado. Dica: use "
            "`valores_distintos_candidatos(coluna='ds_cargo')` ou similar "
            "para ver os valores válidos."
        )

    table = [
        (
            (r.get("nm_urna_candidato") or r.get("nm_candidato") or "—")[:30],
            (r.get("ds_cargo") or "—")[:15],
            r.get("sg_partido") or "—",
            r.get("sg_uf") or "—",
            (r.get("nm_ue") or "—")[:20],
            (r.get("ds_genero") or "—")[:10],
            (r.get("ds_sit_tot_turno") or "—")[:18],
        )
        for r in rows
    ]
    return f"**TSE candidatos 2024 — {len(rows)} resultado(s)**\n\n" + markdown_table(
        ["Nome", "Cargo", "Partido", "UF", "Município", "Gênero", "Resultado"],
        table,
    )


async def resumo_cargo_partido(
    ctx: Context,
    cargo: str = "PREFEITO",
    limite: int = 20,
) -> str:
    """Agrega candidatos de um cargo por partido (eleitos vs total).

    Args:
        cargo: 'PREFEITO', 'VICE-PREFEITO' ou 'VEREADOR'.
        limite: Quantidade de partidos no ranking (padrão 20).

    Returns:
        Tabela com partido, total de candidatos e eleitos, ordenada por eleitos.
    """
    limite = max(1, min(limite, 50))
    await ctx.info(f"Agregando {cargo} por partido...")
    sql = (
        "SELECT sg_partido, COUNT(*) AS total, "
        "SUM(CASE WHEN UPPER(ds_sit_tot_turno) LIKE 'ELEITO%' THEN 1 ELSE 0 END) "
        "AS eleitos "
        f'FROM "{DATASET_TABLE}" '
        "WHERE strip_accents(ds_cargo) ILIKE strip_accents(?) "
        "GROUP BY sg_partido ORDER BY eleitos DESC, total DESC "
        f"LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, [f"%{cargo}%"])
    if not rows:
        return f"Nenhum candidato para cargo {cargo!r}."
    body = [
        (
            r.get("sg_partido") or "—",
            format_number_br(int(r.get("total") or 0), 0),
            format_number_br(int(r.get("eleitos") or 0), 0),
        )
        for r in rows
    ]
    return f"**TSE 2024 — {cargo} por partido (top {len(rows)})**\n\n" + markdown_table(
        ["Partido", "Candidatos", "Eleitos"], body
    )


async def resumo_perfil_eleitos(
    ctx: Context,
    cargo: str = "PREFEITO",
) -> str:
    """Perfil demográfico dos eleitos num cargo (gênero, raça, escolaridade).

    Args:
        cargo: 'PREFEITO', 'VICE-PREFEITO' ou 'VEREADOR'.

    Returns:
        Três tabelas: por gênero, por raça, por grau de instrução.
    """
    await ctx.info(f"Montando perfil dos eleitos — {cargo}...")

    sections: list[str] = [f"**Perfil dos eleitos — {cargo}**\n"]
    for coluna, titulo in [
        ("ds_genero", "Gênero"),
        ("ds_cor_raca", "Raça/Cor"),
        ("ds_grau_instrucao", "Escolaridade"),
    ]:
        sql = (
            f'SELECT "{coluna}" AS v, COUNT(*) AS n '
            f'FROM "{DATASET_TABLE}" '
            "WHERE strip_accents(ds_cargo) ILIKE strip_accents(?) "
            "AND UPPER(ds_sit_tot_turno) LIKE 'ELEITO%' "
            f'GROUP BY "{coluna}" ORDER BY n DESC'
        )
        rows = await executar_query(DATASET_SPEC, sql, [f"%{cargo}%"])
        body = [
            (
                str(r.get("v")) if r.get("v") is not None else "(null)",
                format_number_br(int(r.get("n") or 0), 0),
            )
            for r in rows
        ]
        sections.append(f"\n### {titulo}\n\n" + markdown_table([titulo, "Eleitos"], body))
    return "\n".join(sections)


async def top_municipios_candidatos(
    ctx: Context,
    uf: str,
    top: int = 20,
) -> str:
    """Top municípios de uma UF por número de candidatos.

    Args:
        uf: Sigla UF.
        top: Quantidade (padrão 20).

    Returns:
        Tabela com município, total de candidatos e eleitos.
    """
    top = max(1, min(top, 100))
    await ctx.info(f"Top {top} municípios de {uf}...")
    sql = (
        "SELECT nm_ue, COUNT(*) AS total, "
        "SUM(CASE WHEN UPPER(ds_sit_tot_turno) LIKE 'ELEITO%' THEN 1 ELSE 0 END) "
        "AS eleitos "
        f'FROM "{DATASET_TABLE}" WHERE TRIM(sg_uf) = ? '
        f"GROUP BY nm_ue ORDER BY total DESC LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql, [uf.strip().upper()])
    if not rows:
        return f"Nenhum candidato em {uf}."
    body = [
        (
            r.get("nm_ue") or "—",
            format_number_br(int(r.get("total") or 0), 0),
            format_number_br(int(r.get("eleitos") or 0), 0),
        )
        for r in rows
    ]
    return f"**TSE 2024 — Top {len(rows)} municípios de {uf}**\n\n" + markdown_table(
        ["Município", "Candidatos", "Eleitos"], body
    )
