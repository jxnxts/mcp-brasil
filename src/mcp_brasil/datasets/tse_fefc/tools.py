"""Canned SQL query tools for tse_fefc dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status
from mcp_brasil._shared.formatting import format_brl, format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE


def _parse_brl(v: Any) -> float:
    if v is None:
        return 0.0
    s = str(v).strip()
    if not s or s in {"-", "#NULO", "#NE"}:
        return 0.0
    if "," in s and s.rfind(",") > s.rfind("."):
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


_VR_FEFC = "TRY_CAST(REPLACE(REPLACE(vr_total_recebido_fefc, '.', ''), ',', '.') AS DOUBLE)"


async def info_tse_fefc(ctx: Context) -> str:
    """Estado do cache local do dataset TSE FEFC.

    Returns:
        Métricas do cache.
    """
    await ctx.info("Consultando estado do cache TSE FEFC...")
    st = await get_status(DATASET_SPEC)
    return (
        "**TSE FEFC 2020/2024 — cache**\n\n"
        f"- Cached: {'sim' if st['cached'] else 'não'}\n"
        f"- Linhas: {format_number_br(st['row_count'], 0) if st['cached'] else '—'}\n"
        f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB\n"
    )


async def fefc_por_partido(
    ctx: Context,
    ano: int | None = None,
    top: int = 30,
) -> str:
    """Recebimento do Fundo Eleitoral por partido.

    Args:
        ano: Ano eleitoral (2020 ou 2024). Default: todos.
        top: Máx partidos no ranking (padrão 30).

    Returns:
        Tabela com partido x total recebido x quota_genero x candidatos.
    """
    top = max(1, min(top, 50))
    await ctx.info(f"FEFC por partido {ano or ''}...")
    where = "1=1"
    params: list[Any] = []
    if ano is not None:
        where = "CAST(aa_eleicao AS INTEGER) = ?"
        params.append(int(ano))
    sql = (
        "SELECT sg_partido, "
        f"SUM({_VR_FEFC}) AS total, "
        "SUM(TRY_CAST(qt_candidato AS BIGINT)) AS candidatos "
        f'FROM "{DATASET_TABLE}" WHERE {where} '
        "GROUP BY sg_partido ORDER BY total DESC NULLS LAST "
        f"LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return "Sem dados FEFC."
    body = [
        (
            r.get("sg_partido") or "—",
            format_brl(_parse_brl(r.get("total"))),
            format_number_br(int(r.get("candidatos") or 0), 0),
        )
        for r in rows
    ]
    return (
        f"**FEFC — partidos (top {len(rows)}) — {ano or 'todos os anos'}**\n\n"
        + markdown_table(["Partido", "Total FEFC recebido", "Candidatos"], body)
    )


async def fefc_por_partido_genero(
    ctx: Context,
    ano: int = 2024,
) -> str:
    """Distribuição do FEFC por partido x gênero (obrigatoriedade de cota).

    Lei exige que partidos destinem no mínimo 30% do FEFC a candidatas
    mulheres. Esta tool expõe quanto efetivamente foi destinado.

    Args:
        ano: Ano eleitoral (2020 ou 2024).

    Returns:
        Tabela partido x feminino x masculino x % feminino.
    """
    await ctx.info(f"FEFC partido x gênero — {ano}...")
    sql = (
        "SELECT sg_partido, ds_genero, "
        f"SUM({_VR_FEFC}) AS total "
        f'FROM "{DATASET_TABLE}" '
        "WHERE CAST(aa_eleicao AS INTEGER) = ? "
        "GROUP BY sg_partido, ds_genero"
    )
    rows = await executar_query(DATASET_SPEC, sql, [int(ano)])
    if not rows:
        return f"Sem dados FEFC para {ano}."
    # pivot: partido -> (fem, masc)
    agg: dict[str, dict[str, float]] = {}
    for r in rows:
        p = r.get("sg_partido") or "—"
        g = (r.get("ds_genero") or "").upper()
        v = _parse_brl(r.get("total"))
        agg.setdefault(p, {"FEMININO": 0.0, "MASCULINO": 0.0})
        if "FEM" in g:
            agg[p]["FEMININO"] += v
        elif "MASC" in g:
            agg[p]["MASCULINO"] += v
    ordered = sorted(
        agg.items(),
        key=lambda x: x[1]["FEMININO"] + x[1]["MASCULINO"],
        reverse=True,
    )[:30]
    body = []
    for partido, g in ordered:
        total = g["FEMININO"] + g["MASCULINO"]
        pct_fem = (100.0 * g["FEMININO"] / total) if total else 0.0
        body.append(
            (
                partido,
                format_brl(g["FEMININO"]),
                format_brl(g["MASCULINO"]),
                f"{pct_fem:.1f}%",
            )
        )
    return (
        f"**FEFC {ano} — distribuição por gênero**\n\n"
        "*Lei exige >=30% do FEFC a candidatas mulheres.*\n\n"
        + markdown_table(
            ["Partido", "Feminino", "Masculino", "% Feminino"],
            body,
        )
    )


async def valores_distintos_fefc(ctx: Context, coluna: str, top: int = 20) -> str:
    """Valores distintos de uma coluna do dataset FEFC.

    Args:
        coluna: Nome da coluna (sg_partido, ds_genero, aa_eleicao, etc.).
        top: Máx (padrão 20).

    Returns:
        Tabela valor x ocorrências.
    """
    allow = {"sg_partido", "ds_genero", "aa_eleicao"}
    if coluna not in allow:
        return f"Coluna '{coluna}' não permitida. Use: {sorted(allow)}"
    top = max(1, min(top, 50))
    sql = (
        f'SELECT "{coluna}" AS v, COUNT(*) AS n '
        f'FROM "{DATASET_TABLE}" GROUP BY "{coluna}" '
        f"ORDER BY n DESC LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return f"Sem valores em {coluna}."
    body = [(str(r.get("v") or "(null)"), format_number_br(int(r.get("n") or 0), 0)) for r in rows]
    return f"**FEFC — distintos em `{coluna}`**\n\n" + markdown_table(
        ["Valor", "Ocorrências"], body
    )
