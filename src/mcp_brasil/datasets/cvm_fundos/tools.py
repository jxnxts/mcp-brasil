"""Canned SQL tools for cvm_fundos dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status, refresh_dataset
from mcp_brasil._shared.formatting import format_brl, format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE
from .constants import COLUNAS_DISTINCT_PERMITIDAS


async def info_cvm_fundos(ctx: Context) -> str:
    """Estado do cache local do cadastro de fundos CVM."""
    await ctx.info("Consultando cache CVM Fundos...")
    st = await get_status(DATASET_SPEC)
    return "\n".join(
        [
            "**CVM Fundos — estado do cache**",
            "",
            f"- Cached: {'sim' if st['cached'] else 'não'}",
            f"- Linhas: {format_number_br(st['row_count'], 0) if st['cached'] else '—'}",
            f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB",
            "- Idade: "
            + (f"{st['age_days']:.2f} dias" if st.get("age_days") is not None else "—"),
        ]
    )


async def refrescar_cvm_fundos(ctx: Context) -> str:
    """Força re-download do cadastro CVM."""
    await ctx.info("Re-baixando CVM Fundos...")
    m = await refresh_dataset(DATASET_SPEC)
    return (
        f"**CVM Fundos atualizado** — {format_number_br(m.row_count, 0)} fundos, "
        f"{m.size_bytes / 1024 / 1024:.1f} MB"
    )


async def valores_distintos_cvm(coluna: str, limite: int = 100) -> str:
    """Valores distintos de uma coluna categórica.

    Args:
        coluna: Uma de TP_FUNDO, SIT, CLASSE, CLASSE_ANBIMA, CONDOM, PUBLICO_ALVO, etc.
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
        return "Sem valores."
    return markdown_table(
        [coluna, "ocorrencias"],
        [(r["valor"], format_number_br(int(r["total"]), 0)) for r in rows],
    )


async def buscar_fundo(
    ctx: Context,
    termo: str,
    classe: str | None = None,
    limite: int = 30,
) -> str:
    """Busca fundos pelo nome (denominação social) ou CNPJ.

    Args:
        termo: Nome (substring accent-insensitive) ou CNPJ.
        classe: Filtra por classe (ex: 'Renda Fixa', 'Ações', 'Multimercado').
        limite: Padrão 30, máx 200.
    """
    limite = max(1, min(limite, 200))
    where = ["strip_accents(DENOM_SOCIAL) ILIKE strip_accents(?) OR CNPJ_FUNDO LIKE ?"]
    params: list[Any] = [f"%{termo}%", f"%{termo}%"]
    if classe:
        where.append("strip_accents(CLASSE) ILIKE strip_accents(?)")
        params.append(f"%{classe}%")
    sql = (
        "SELECT CNPJ_FUNDO, DENOM_SOCIAL, CLASSE, SIT, VL_PATRIM_LIQ, ADMIN, GESTOR "
        f'FROM "{DATASET_TABLE}" WHERE {" AND ".join(where)} LIMIT {limite}'
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return f"Nenhum fundo encontrado para '{termo}'."
    table = [
        (
            r.get("CNPJ_FUNDO") or "—",
            (r.get("DENOM_SOCIAL") or "—")[:50],
            (r.get("CLASSE") or "—")[:20],
            (r.get("SIT") or "—")[:12],
            format_brl(float(r.get("VL_PATRIM_LIQ") or 0)) if r.get("VL_PATRIM_LIQ") else "—",
        )
        for r in rows
    ]
    return f"**{len(rows)} fundos encontrados**\n\n" + markdown_table(
        ["CNPJ", "Denominação", "Classe", "Situação", "PL"], table
    )


async def detalhe_fundo(ctx: Context, cnpj: str) -> str:
    """Detalhe completo de um fundo pelo CNPJ.

    Args:
        cnpj: CNPJ do fundo (com ou sem pontuação).
    """
    # Normaliza: tenta com e sem pontuação via LIKE
    sql = (
        "SELECT * "
        f'FROM "{DATASET_TABLE}" '
        "WHERE CNPJ_FUNDO = ? OR "
        "REPLACE(REPLACE(REPLACE(CNPJ_FUNDO, '.', ''), '/', ''), '-', '') = ? "
        "LIMIT 1"
    )
    clean = "".join(ch for ch in cnpj if ch.isdigit())
    rows = await executar_query(DATASET_SPEC, sql, [cnpj, clean])
    if not rows:
        return f"Fundo '{cnpj}' não encontrado."
    r = rows[0]
    pl = float(r.get("VL_PATRIM_LIQ") or 0)
    return "\n".join(
        [
            f"**{r.get('DENOM_SOCIAL')}** ({r.get('CNPJ_FUNDO')})",
            "",
            f"- **Classe:** {r.get('CLASSE') or '—'}",
            f"- **Classe ANBIMA:** {r.get('CLASSE_ANBIMA') or '—'}",
            f"- **Situação:** {r.get('SIT') or '—'}",
            f"- **Patrimônio líquido:** {format_brl(pl) if pl else '—'}",
            f"- **Data PL:** {r.get('DT_PATRIM_LIQ') or '—'}",
            f"- **Tipo fundo:** {r.get('TP_FUNDO') or '—'}",
            f"- **Condomínio:** {r.get('CONDOM') or '—'}",
            f"- **Fundo de cotas:** {r.get('FUNDO_COTAS') or '—'}",
            f"- **Taxa adm (%):** {r.get('TAXA_ADM') or '—'}",
            f"- **Taxa performance (%):** {r.get('TAXA_PERFM') or '—'}",
            "",
            "**Prestadores de serviço:**",
            f"- Administrador: {r.get('ADMIN') or '—'} ({r.get('CNPJ_ADMIN') or '—'})",
            f"- Gestor: {r.get('GESTOR') or '—'}",
            f"- Custodiante: {r.get('CUSTODIANTE') or '—'}",
            f"- Auditor: {r.get('AUDITOR') or '—'}",
        ]
    )


async def top_fundos_por_pl(
    ctx: Context,
    classe: str | None = None,
    limite: int = 20,
) -> str:
    """Ranking de fundos pelo patrimônio líquido.

    Args:
        classe: Filtra classe (ex: 'Ações', 'Renda Fixa').
        limite: Top N (padrão 20, máx 100).
    """
    limite = max(1, min(limite, 100))
    where = ["SIT = 'EM FUNCIONAMENTO NORMAL'", "VL_PATRIM_LIQ IS NOT NULL"]
    params: list[Any] = []
    if classe:
        where.append("strip_accents(CLASSE) ILIKE strip_accents(?)")
        params.append(f"%{classe}%")
    sql = (
        "SELECT DENOM_SOCIAL, CLASSE, VL_PATRIM_LIQ, ADMIN "
        f'FROM "{DATASET_TABLE}" WHERE {" AND ".join(where)} '
        f"ORDER BY VL_PATRIM_LIQ DESC LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, params)
    if not rows:
        return "Nenhum fundo encontrado."
    table = [
        (
            (r.get("DENOM_SOCIAL") or "—")[:50],
            (r.get("CLASSE") or "—")[:20],
            format_brl(float(r.get("VL_PATRIM_LIQ") or 0)),
        )
        for r in rows
    ]
    header = f"**Top {len(rows)} fundos por PL" + (f" — {classe}" if classe else "") + "**\n\n"
    return header + markdown_table(["Fundo", "Classe", "PL"], table)
