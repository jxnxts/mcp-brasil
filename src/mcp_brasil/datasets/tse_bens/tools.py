"""Canned SQL query tools for tse_bens dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status
from mcp_brasil._shared.formatting import format_brl, format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE


async def info_tse_bens(ctx: Context) -> str:
    """Estado do cache local do dataset TSE bens 2024.

    Returns:
        Métricas básicas do cache.
    """
    await ctx.info("Consultando estado do cache TSE bens...")
    st = await get_status(DATASET_SPEC)
    return (
        "**TSE bens 2024 — cache**\n\n"
        f"- Cached: {'sim' if st['cached'] else 'não'}\n"
        f"- Linhas: {format_number_br(st['row_count'], 0) if st['cached'] else '—'}\n"
        f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB\n"
        f"- Fresh (TTL={st['ttl_days']}d): {'sim' if st['fresh'] else 'não'}\n"
        f"- Fonte: {st['source']}\n"
    )


async def buscar_bens_candidato(
    ctx: Context,
    sq_candidato: str,
    limite: int = 100,
) -> str:
    """Lista todos os bens declarados por um candidato.

    Args:
        sq_candidato: ID do candidato (obtido via `buscar_candidatos` do
            feature tse_candidatos).
        limite: Máx. bens (padrão 100, máx 300).

    Returns:
        Tabela com ordem, tipo, descrição e valor de cada bem.
    """
    limite = max(1, min(limite, 300))
    await ctx.info(f"Buscando bens do candidato {sq_candidato}...")
    sql = (
        "SELECT nr_ordem_bem_candidato, ds_tipo_bem_candidato, ds_bem_candidato, "
        "vr_bem_candidato "
        f'FROM "{DATASET_TABLE}" WHERE CAST(sq_candidato AS VARCHAR) = ? '
        f"ORDER BY vr_bem_candidato DESC LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, [str(sq_candidato).strip()])
    if not rows:
        return f"Nenhum bem declarado para sq_candidato={sq_candidato!r}."

    total = sum(float(r.get("vr_bem_candidato") or 0) for r in rows)
    table = [
        (
            str(r.get("nr_ordem_bem_candidato") or "—"),
            (r.get("ds_tipo_bem_candidato") or "—")[:30],
            (r.get("ds_bem_candidato") or "—")[:50],
            format_brl(float(r.get("vr_bem_candidato") or 0)),
        )
        for r in rows
    ]
    return (
        f"**Bens do candidato {sq_candidato}** — {len(rows)} bem(ns), "
        f"total declarado: {format_brl(total)}\n\n"
        + markdown_table(["#", "Tipo", "Descrição", "Valor"], table)
    )


async def top_patrimonios_cargo(
    ctx: Context,
    cargo: str = "PREFEITO",
    uf: str | None = None,
    limite: int = 20,
) -> str:
    """Ranking dos candidatos com maior patrimônio declarado num cargo.

    **Requer o dataset tse_candidatos também ativo** — faz join para
    recuperar nome, partido, UF e município.

    Args:
        cargo: Cargo a filtrar — 'PREFEITO', 'VICE-PREFEITO', 'VEREADOR'.
        uf: UF opcional.
        limite: Quantidade de candidatos (padrão 20, máx 100).

    Returns:
        Tabela com nome, partido, UF, município, patrimônio total.
    """
    limite = max(1, min(limite, 100))
    await ctx.info(f"Top {limite} patrimônios — {cargo} ({uf or 'BR'})...")

    uf_clause = "AND TRIM(c.sg_uf) = ?" if uf else ""
    params: list[Any] = [f"%{cargo}%"]
    if uf:
        params.append(uf.strip().upper())
    params.append(limite)

    sql = (
        "SELECT c.sq_candidato, c.nm_urna_candidato, c.ds_cargo, c.sg_partido, "
        "c.sg_uf, c.nm_ue, SUM(b.vr_bem_candidato) AS total "
        f'FROM "{DATASET_TABLE}" b '
        'JOIN "candidatos_2024" c USING (sq_candidato) '
        "WHERE strip_accents(c.ds_cargo) ILIKE strip_accents(?) "
        f"{uf_clause} "
        "GROUP BY c.sq_candidato, c.nm_urna_candidato, c.ds_cargo, "
        "c.sg_partido, c.sg_uf, c.nm_ue "
        "ORDER BY total DESC LIMIT ?"
    )

    # Requires attaching candidatos DB; do a cross-DB ATTACH
    try:
        rows = await _execute_with_candidatos_attached(sql, params)
    except Exception as exc:
        return (
            f"ERRO ao juntar com tse_candidatos ({type(exc).__name__}): {exc}\n\n"
            "Certifique-se que `tse_candidatos` também está em MCP_BRASIL_DATASETS."
        )

    if not rows:
        return "Sem resultados para o filtro."

    table = [
        (
            (r.get("nm_urna_candidato") or "—")[:28],
            (r.get("ds_cargo") or "—")[:15],
            r.get("sg_partido") or "—",
            r.get("sg_uf") or "—",
            (r.get("nm_ue") or "—")[:18],
            format_brl(float(r.get("total") or 0)),
        )
        for r in rows
    ]
    return (
        f"**Top {len(rows)} patrimônios declarados — {cargo}"
        f"{' / ' + uf if uf else ''}**\n\n"
        + markdown_table(
            ["Nome urna", "Cargo", "Partido", "UF", "Município", "Patrimônio"],
            table,
        )
    )


async def resumo_patrimonio_partido(
    ctx: Context,
    cargo: str = "PREFEITO",
) -> str:
    """Patrimônio total declarado por partido num cargo.

    Requer tse_candidatos ativo.

    Args:
        cargo: Cargo filtrado.

    Returns:
        Tabela com partido, candidatos com bens, valor total e médio.
    """
    await ctx.info(f"Agregando patrimônio por partido — {cargo}...")
    sql = (
        "SELECT c.sg_partido, COUNT(DISTINCT c.sq_candidato) AS candidatos_c_bens, "
        "SUM(b.vr_bem_candidato) AS total, "
        "AVG(b.vr_bem_candidato) AS media_bem "
        f'FROM "{DATASET_TABLE}" b '
        'JOIN "candidatos_2024" c USING (sq_candidato) '
        "WHERE strip_accents(c.ds_cargo) ILIKE strip_accents(?) "
        "GROUP BY c.sg_partido ORDER BY total DESC LIMIT 30"
    )
    try:
        rows = await _execute_with_candidatos_attached(sql, [f"%{cargo}%"])
    except Exception as exc:
        return f"ERRO ao juntar com tse_candidatos ({type(exc).__name__}): {exc}"

    if not rows:
        return "Sem resultados."

    table = [
        (
            r.get("sg_partido") or "—",
            format_number_br(int(r.get("candidatos_c_bens") or 0), 0),
            format_brl(float(r.get("total") or 0)),
            format_brl(float(r.get("media_bem") or 0)),
        )
        for r in rows
    ]
    return f"**Patrimônio por partido — {cargo}**\n\n" + markdown_table(
        ["Partido", "Candidatos c/ bens", "Patrimônio total", "Média por bem"],
        table,
    )


async def resumo_tipos_bens(ctx: Context, top: int = 20) -> str:
    """Distribuição de bens declarados por tipo (imóvel, veículo, etc.).

    Args:
        top: Número de tipos no ranking.

    Returns:
        Tabela ordenada por valor total declarado.
    """
    top = max(1, min(top, 50))
    await ctx.info("Agregando por tipo de bem...")
    sql = (
        "SELECT ds_tipo_bem_candidato, COUNT(*) AS n, "
        "SUM(vr_bem_candidato) AS total, "
        "AVG(vr_bem_candidato) AS media "
        f'FROM "{DATASET_TABLE}" '
        "GROUP BY ds_tipo_bem_candidato ORDER BY total DESC "
        f"LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return "Sem dados."
    table = [
        (
            (r.get("ds_tipo_bem_candidato") or "—")[:40],
            format_number_br(int(r.get("n") or 0), 0),
            format_brl(float(r.get("total") or 0)),
            format_brl(float(r.get("media") or 0)),
        )
        for r in rows
    ]
    return f"**TSE 2024 — bens por tipo (top {len(rows)})**\n\n" + markdown_table(
        ["Tipo", "Qtd", "Valor total", "Média"],
        table,
    )


async def _execute_with_candidatos_attached(sql: str, params: list[Any]) -> list[dict[str, Any]]:
    """Execute a query that joins tse_bens with tse_candidatos via ATTACH.

    DuckDB read-only ATTACH is safe. Returns [] if the candidatos DB is missing.
    """
    import duckdb

    from mcp_brasil._shared.datasets.cache import db_path
    from mcp_brasil._shared.datasets.loader import ensure_loaded

    # Ensure both datasets are loaded
    await ensure_loaded(DATASET_SPEC)

    from mcp_brasil.datasets.tse_candidatos import (
        DATASET_SPEC as CAND_SPEC,
    )

    try:
        await ensure_loaded(CAND_SPEC)
    except Exception as exc:
        raise RuntimeError(f"tse_candidatos não disponível: {exc}") from exc

    bens_path = str(db_path(DATASET_SPEC.id))
    cand_path = str(db_path(CAND_SPEC.id))

    import asyncio

    def _run() -> list[dict[str, Any]]:
        con = duckdb.connect(bens_path, read_only=True)
        try:
            con.execute(f"ATTACH '{cand_path}' AS cand (READ_ONLY)")
            # Rewrite bare table refs to include the attached DB schema
            # (since candidatos_2024 is in the attached DB)
            sql_rewritten = sql.replace('"candidatos_2024"', 'cand."candidatos_2024"')
            cursor = con.execute(sql_rewritten, params)
            cols = [c[0] for c in cursor.description] if cursor.description else []
            return [dict(zip(cols, row, strict=False)) for row in cursor.fetchall()]
        finally:
            con.close()

    return await asyncio.to_thread(_run)
