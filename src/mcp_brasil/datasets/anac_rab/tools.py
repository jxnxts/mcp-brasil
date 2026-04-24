"""Canned SQL query tools for anac_rab dataset."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from mcp_brasil._shared.datasets import executar_query, get_status
from mcp_brasil._shared.formatting import format_number_br, markdown_table

from . import DATASET_SPEC, DATASET_TABLE


async def info_anac_rab(ctx: Context) -> str:
    """Estado do cache local do dataset ANAC RAB.

    Returns:
        Métricas do cache (linhas, tamanho, frescor).
    """
    await ctx.info("Consultando estado do cache ANAC RAB...")
    st = await get_status(DATASET_SPEC)
    return (
        "**ANAC RAB — Registro Aeronáutico Brasileiro — cache**\n\n"
        f"- Cached: {'sim' if st['cached'] else 'não'}\n"
        f"- Linhas: {format_number_br(st['row_count'], 0) if st['cached'] else '—'}\n"
        f"- Tamanho: {st['size_bytes'] / 1024 / 1024:.1f} MB\n"
        f"- Fresh (TTL={st['ttl_days']}d): {'sim' if st['fresh'] else 'não'}\n"
    )


async def consultar_aeronave(ctx: Context, matricula: str) -> str:
    """Consulta uma aeronave pelo prefixo/matrícula (ex: PR-ABC, PT-XYZ).

    Args:
        matricula: Matrícula brasileira (com ou sem hífen, case-insensitive).

    Returns:
        Dados completos da aeronave (proprietário, operador, modelo, motor,
        capacidade, validade CA).
    """
    needle = matricula.replace("-", "").replace(" ", "").upper().strip()
    await ctx.info(f"Consultando aeronave {needle}...")
    sql = (
        "SELECT marcas, proprietarios, operadores, ds_modelo, nm_fabricante, "
        "nr_ano_fabricacao, nr_assentos, tp_motor, qt_motor, "
        "dt_validade_ca, cd_interdicao, ds_categoria_homologacao, tp_operacao "
        f'FROM "{DATASET_TABLE}" '
        "WHERE UPPER(TRIM(marcas)) = ?"
    )
    rows = await executar_query(DATASET_SPEC, sql, [needle])
    if not rows:
        return f"Aeronave '{matricula}' não encontrada no RAB."
    r = rows[0]
    prop = (r.get("proprietarios") or "—").split("|")[0]
    oper = (r.get("operadores") or "—").split("|")[0]
    return (
        f"**Aeronave {r.get('marcas')}**\n\n"
        f"- **Proprietário**: {prop}\n"
        f"- **Operador**: {oper}\n"
        f"- **Fabricante**: {r.get('nm_fabricante') or '—'}\n"
        f"- **Modelo**: {r.get('ds_modelo') or '—'}\n"
        f"- **Ano fabricação**: {r.get('nr_ano_fabricacao') or '—'}\n"
        f"- **Assentos**: {r.get('nr_assentos') or '—'}\n"
        f"- **Motor**: {r.get('tp_motor') or '—'} (qtd {r.get('qt_motor') or '—'})\n"
        f"- **Validade CA**: {r.get('dt_validade_ca') or '—'}\n"
        f"- **Interdição**: {r.get('cd_interdicao') or '—'}\n"
        f"- **Categoria homologação**: {r.get('ds_categoria_homologacao') or '—'}\n"
        f"- **Tipo operação**: {r.get('tp_operacao') or '—'}\n"
    )


async def aeronaves_por_operador(
    ctx: Context,
    operador: str,
    limite: int = 30,
) -> str:
    """Lista aeronaves registradas sob um operador (por nome ou CNPJ).

    Args:
        operador: Nome (ou parte) do operador ou CNPJ (só dígitos).
        limite: Máx linhas (padrão 30, máximo 200).

    Returns:
        Tabela com matrícula, modelo, ano, assentos e tipo de operação.
    """
    limite = max(1, min(limite, 200))
    needle = operador.upper().strip()
    await ctx.info(f"Buscando aeronaves do operador '{needle}' (limite {limite})...")
    sql = (
        "SELECT marcas, ds_modelo, nm_fabricante, nr_ano_fabricacao, "
        "nr_assentos, tp_operacao, operadores "
        f'FROM "{DATASET_TABLE}" '
        "WHERE UPPER(operadores) LIKE ? "
        f"LIMIT {limite}"
    )
    rows = await executar_query(DATASET_SPEC, sql, [f"%{needle}%"])
    if not rows:
        return f"Nenhuma aeronave para o operador '{operador}'."
    table = [
        (
            r.get("marcas") or "—",
            (r.get("nm_fabricante") or "—")[:20],
            (r.get("ds_modelo") or "—")[:25],
            str(r.get("nr_ano_fabricacao") or "—"),
            str(r.get("nr_assentos") or "—"),
            (r.get("tp_operacao") or "—")[:18],
        )
        for r in rows
    ]
    return (
        f"**Aeronaves do operador '{operador}'** — {len(rows)} encontrada(s)\n\n"
        + markdown_table(
            ["Matrícula", "Fabricante", "Modelo", "Ano", "Assentos", "Operação"], table
        )
    )


async def top_fabricantes(ctx: Context, top: int = 20) -> str:
    """Ranking de fabricantes com mais aeronaves ativas no Brasil.

    Args:
        top: Quantidade (padrão 20, máximo 50).

    Returns:
        Tabela fabricante x número de aeronaves.
    """
    top = max(1, min(top, 50))
    await ctx.info(f"Top {top} fabricantes...")
    sql = (
        "SELECT nm_fabricante AS fab, COUNT(*) AS n "
        f'FROM "{DATASET_TABLE}" '
        "WHERE nm_fabricante IS NOT NULL "
        "GROUP BY nm_fabricante "
        f"ORDER BY n DESC LIMIT {top}"
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return "Sem dados."
    body = [
        ((r.get("fab") or "—")[:40], format_number_br(int(r.get("n") or 0), 0))
        for r in rows
    ]
    return f"**ANAC RAB — Top {len(rows)} fabricantes**\n\n" + markdown_table(
        ["Fabricante", "Aeronaves"], body
    )


async def aeronaves_por_uf(ctx: Context) -> str:
    """Distribuição de aeronaves por UF do operador.

    Extrai a UF do campo composto `operadores` (formato `NOME|CNPJ|PCT|UF`).

    Returns:
        Tabela UF x aeronaves ordenada desc.
    """
    await ctx.info("Agrupando aeronaves por UF do operador...")
    sql = (
        "SELECT CASE "
        "  WHEN POSITION('|' IN operadores) > 0 "
        "  THEN TRIM(SPLIT_PART(operadores, '|', 4)) "
        "  ELSE NULL END AS uf, "
        "COUNT(*) AS n "
        f'FROM "{DATASET_TABLE}" '
        "WHERE operadores IS NOT NULL "
        "GROUP BY uf "
        "HAVING uf IS NOT NULL AND LENGTH(uf) = 2 "
        "ORDER BY n DESC"
    )
    rows = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return "Sem dados."
    body = [(r.get("uf") or "—", format_number_br(int(r.get("n") or 0), 0)) for r in rows]
    return "**ANAC RAB — aeronaves por UF do operador**\n\n" + markdown_table(
        ["UF", "Aeronaves"], body
    )


async def valores_distintos_rab(ctx: Context, coluna: str, top: int = 30) -> str:
    """Valores distintos de uma coluna do dataset RAB.

    Args:
        coluna: Uma de: tp_motor, tp_operacao, ds_categoria_homologacao,
            cd_interdicao, cd_cls, tp_pouso, cf_operacional.
        top: Máx (padrão 30).

    Returns:
        Tabela valor x ocorrências.
    """
    allow = {
        "tp_motor",
        "tp_operacao",
        "ds_categoria_homologacao",
        "cd_interdicao",
        "cd_cls",
        "tp_pouso",
        "cf_operacional",
        "cd_tipo_icao",
    }
    if coluna not in allow:
        return f"Coluna '{coluna}' não permitida. Use: {sorted(allow)}"
    top = max(1, min(top, 100))
    sql = (
        f'SELECT "{coluna}" AS v, COUNT(*) AS n '
        f'FROM "{DATASET_TABLE}" GROUP BY "{coluna}" '
        f"ORDER BY n DESC LIMIT {top}"
    )
    rows: list[dict[str, Any]] = await executar_query(DATASET_SPEC, sql)
    if not rows:
        return f"Sem valores em {coluna}."
    body = [
        (str(r.get("v") or "(null)"), format_number_br(int(r.get("n") or 0), 0)) for r in rows
    ]
    return f"**ANAC RAB — distintos em `{coluna}`**\n\n" + markdown_table(
        ["Valor", "Ocorrências"], body
    )
