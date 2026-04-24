"""Canned SQL query tools for tse_bens dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status
from mcp_brasil._shared.formatting import format_brl, format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE

# DuckDB SQL expression that parses a BR-locale numeric VARCHAR to DOUBLE.
# "1.200.000,00" -> 1200000.0, "500000,00" -> 500000.0
# Column is VARCHAR because csv_options has all_varchar=true.
_VR_PARSE = "TRY_CAST(REPLACE(REPLACE(vr_bem_candidato, '.', ''), ',', '.') AS DOUBLE)"


def _parse_br_number(v: Any) -> float:
    """Parse BR-locale numeric string ('1.200.000,00' → 1200000.0)."""
    if v is None:
        return 0.0
    if isinstance(v, int | float):
        return float(v)
    s = str(v).strip()
    if not s or s in {"-", "#NULO", "#NE"}:
        return 0.0
    # Heurística: se tem vírgula como decimal (BR), remove pontos de milhar
    if "," in s and s.rfind(",") > s.rfind("."):
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


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
        "SELECT ano_eleicao, nr_ordem_bem_candidato, ds_tipo_bem_candidato, "
        f"ds_bem_candidato, {_VR_PARSE} AS vr_num "
        f'FROM "{DATASET_TABLE}" WHERE CAST(sq_candidato AS VARCHAR) = ? '
        "ORDER BY vr_num DESC NULLS LAST "
        f"LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, [str(sq_candidato).strip()])
    if not rows:
        return f"Nenhum bem declarado para sq_candidato={sq_candidato!r}."

    total = sum(_parse_br_number(r.get("vr_num")) for r in rows)
    table = [
        (
            str(r.get("ano_eleicao") or "—"),
            str(r.get("nr_ordem_bem_candidato") or "—"),
            (r.get("ds_tipo_bem_candidato") or "—")[:28],
            (r.get("ds_bem_candidato") or "—")[:45],
            format_brl(_parse_br_number(r.get("vr_num"))),
        )
        for r in rows
    ]
    return (
        f"**Bens do candidato {sq_candidato}** — {len(rows)} bem(ns), "
        f"total declarado: {format_brl(total)}\n\n"
        + markdown_table(["Ano", "#", "Tipo", "Descrição", "Valor"], table)
    )


async def top_patrimonios_cargo(
    ctx: Context,
    cargo: str = "PREFEITO",
    uf: str | None = None,
    ano: int | None = None,
    limite: int = 20,
) -> str:
    """Ranking dos candidatos com maior patrimônio declarado num cargo.

    **Requer o dataset tse_candidatos também ativo** — faz join para
    recuperar nome, partido, UF e município.

    Args:
        cargo: Cargo a filtrar (ex: 'PREFEITO', 'DEPUTADO FEDERAL').
        uf: UF opcional.
        ano: Ano eleitoral (2014-2024). Se omitido, usa todos os anos.
        limite: Quantidade de candidatos (padrão 20, máx 100).

    Returns:
        Tabela com ano, nome, partido, UF, município, patrimônio total.
    """
    limite = max(1, min(limite, 100))
    await ctx.info(f"Top {limite} patrimônios — {cargo} ({uf or 'BR'}, {ano or 'todos'})...")

    # The bens table has column ano_eleicao too (from CSV). Use b.ano_eleicao.
    clauses: list[str] = []
    params: list[Any] = [f"%{cargo}%"]
    if uf:
        clauses.append("AND TRIM(c.sg_uf) = ?")
        params.append(uf.strip().upper())
    if ano is not None:
        clauses.append("AND CAST(b.ano_eleicao AS INTEGER) = ?")
        params.append(int(ano))
    clauses.append(f"LIMIT {limite}")

    sql = (
        "SELECT b.ano_eleicao, c.sq_candidato, c.nm_urna_candidato, c.ds_cargo, "
        "c.sg_partido, c.sg_uf, c.nm_ue, "
        f"SUM({_VR_PARSE}) AS total "
        f'FROM "{DATASET_TABLE}" b '
        'JOIN "candidatos" c USING (sq_candidato) '
        "WHERE strip_accents(c.ds_cargo) ILIKE strip_accents(?) "
        f"{' '.join(clauses[:-1])} "
        "GROUP BY b.ano_eleicao, c.sq_candidato, c.nm_urna_candidato, "
        "c.ds_cargo, c.sg_partido, c.sg_uf, c.nm_ue "
        f"ORDER BY total DESC NULLS LAST {clauses[-1]}"
    )

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
            str(r.get("ano_eleicao") or "—"),
            (r.get("nm_urna_candidato") or "—")[:26],
            (r.get("ds_cargo") or "—")[:14],
            r.get("sg_partido") or "—",
            r.get("sg_uf") or "—",
            (r.get("nm_ue") or "—")[:16],
            format_brl(_parse_br_number(r.get("total"))),
        )
        for r in rows
    ]
    titulo = f"{cargo}{' / ' + uf if uf else ''} — {ano or 'todos os anos'}"
    return f"**Top {len(rows)} patrimônios declarados — {titulo}**\n\n" + markdown_table(
        ["Ano", "Nome urna", "Cargo", "Partido", "UF", "Município", "Patrimônio"],
        table,
    )


async def resumo_patrimonio_partido(
    ctx: Context,
    cargo: str = "PREFEITO",
    ano: int | None = None,
) -> str:
    """Patrimônio total declarado por partido num cargo.

    Requer tse_candidatos ativo.

    Args:
        cargo: Cargo filtrado.
        ano: Ano eleitoral opcional.

    Returns:
        Tabela com partido, candidatos com bens, valor total e médio.
    """
    await ctx.info(f"Agregando patrimônio por partido — {cargo} (ano={ano})...")
    extra = ""
    extra_params: list[Any] = []
    if ano is not None:
        extra = " AND CAST(b.ano_eleicao AS INTEGER) = ?"
        extra_params = [int(ano)]
    sql = (
        "SELECT c.sg_partido, COUNT(DISTINCT c.sq_candidato) AS candidatos_c_bens, "
        f"SUM({_VR_PARSE}) AS total, "
        f"AVG({_VR_PARSE}) AS media_bem "
        f'FROM "{DATASET_TABLE}" b '
        'JOIN "candidatos" c USING (sq_candidato) '
        "WHERE strip_accents(c.ds_cargo) ILIKE strip_accents(?) "
        f"{extra} "
        "GROUP BY c.sg_partido ORDER BY total DESC NULLS LAST LIMIT 30"
    )
    try:
        rows = await _execute_with_candidatos_attached(sql, [f"%{cargo}%", *extra_params])
    except Exception as exc:
        return f"ERRO ao juntar com tse_candidatos ({type(exc).__name__}): {exc}"

    if not rows:
        return "Sem resultados."

    table = [
        (
            r.get("sg_partido") or "—",
            format_number_br(int(r.get("candidatos_c_bens") or 0), 0),
            format_brl(_parse_br_number(r.get("total"))),
            format_brl(_parse_br_number(r.get("media_bem"))),
        )
        for r in rows
    ]
    titulo = f"{cargo} — {ano or 'todos os anos'}"
    return f"**Patrimônio por partido — {titulo}**\n\n" + markdown_table(
        ["Partido", "Candidatos c/ bens", "Patrimônio total", "Média por bem"],
        table,
    )


async def resumo_tipos_bens(
    ctx: Context,
    ano: int | None = None,
    top: int = 20,
) -> str:
    """Distribuição de bens declarados por tipo (imóvel, veículo, etc.).

    Args:
        ano: Ano eleitoral opcional (2014-2024). Default: todos.
        top: Número de tipos no ranking.

    Returns:
        Tabela ordenada por valor total declarado.
    """
    top = max(1, min(top, 50))
    await ctx.info(f"Agregando por tipo de bem (ano={ano})...")
    where = "1=1"
    params: list[Any] = []
    if ano is not None:
        where = "CAST(ano_eleicao AS INTEGER) = ?"
        params.append(int(ano))
    sql = (
        "SELECT ds_tipo_bem_candidato, COUNT(*) AS n, "
        f"SUM({_VR_PARSE}) AS total, "
        f"AVG({_VR_PARSE}) AS media "
        f'FROM "{DATASET_TABLE}" WHERE {where} '
        "GROUP BY ds_tipo_bem_candidato ORDER BY total DESC NULLS LAST "
        f"LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return "Sem dados."
    table = [
        (
            (r.get("ds_tipo_bem_candidato") or "—")[:40],
            format_number_br(int(r.get("n") or 0), 0),
            format_brl(_parse_br_number(r.get("total"))),
            format_brl(_parse_br_number(r.get("media"))),
        )
        for r in rows
    ]
    titulo = f"bens por tipo — {ano or 'todos os anos'}"
    return f"**TSE — {titulo} (top {len(rows)})**\n\n" + markdown_table(
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
            # Rewrite bare view refs to include the attached DB schema
            # (since the view `candidatos` lives in the attached DB)
            sql_rewritten = sql.replace('"candidatos"', 'cand."candidatos"')
            cursor = con.execute(sql_rewritten, params)
            cols = [c[0] for c in cursor.description] if cursor.description else []
            return [dict(zip(cols, row, strict=False)) for row in cursor.fetchall()]
        finally:
            con.close()

    return await asyncio.to_thread(_run)
