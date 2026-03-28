"""Tool functions for the BPS (Banco de Preços em Saúde) feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
    - Uses Context for structured logging and progress reporting
"""

from __future__ import annotations

from collections.abc import Sequence

from fastmcp import Context

from mcp_brasil._shared.formatting import format_brl

from . import client
from .schemas import ComprasBPS


async def consultar_precos_saude(
    ctx: Context,
    limite: int = 100,
    offset: int = 0,
) -> str:
    """Consulta compras registradas no Banco de Preços em Saúde (BPS).

    O BPS registra preços de medicamentos e dispositivos médicos comprados
    pelo governo em todas as esferas (federal, estadual, municipal).
    Retorna dados de compras com preço unitário, fornecedor e instituição.

    Args:
        limite: Máximo de registros (padrão 100, máximo 1000).
        offset: Deslocamento para paginação (padrão 0).

    Returns:
        Lista de compras com produto, preço, fornecedor e instituição.
    """
    await ctx.info("Consultando Banco de Preços em Saúde...")
    resultado = await client.consultar_precos(limite=limite, offset=offset)

    if not resultado.registros:
        return "Nenhum registro encontrado no BPS."

    return _format_resultado(resultado.registros, resultado.total_retornado, offset)


async def buscar_medicamento_bps(
    descricao: str,
    ctx: Context,
    limite: int = 1000,
    offset: int = 0,
) -> str:
    """Busca preços de medicamentos por descrição no BPS.

    Pesquisa por palavra-chave na descrição CATMAT. Útil para comparar
    preços de um medicamento entre diferentes instituições e fornecedores.

    Args:
        descricao: Termo de busca na descrição do medicamento
            (ex: 'paracetamol', 'insulina', 'dipirona').
        limite: Máximo de registros a buscar (padrão 1000).
        offset: Deslocamento para paginação.

    Returns:
        Compras encontradas para o medicamento com preços comparativos.
    """
    await ctx.info(f"Buscando '{descricao}' no BPS...")
    resultado = await client.buscar_por_descricao(
        descricao,
        limite=limite,
        offset=offset,
    )
    await ctx.info(f"{resultado.total_retornado} registros encontrados")

    if not resultado.registros:
        return (
            f"Nenhum registro encontrado para '{descricao}' neste lote. "
            f"Tente offset={offset + limite} para buscar no próximo lote."
        )

    return _format_resultado(resultado.registros, resultado.total_retornado, offset)


async def buscar_catmat_bps(
    codigo_catmat: str,
    ctx: Context,
    limite: int = 1000,
    offset: int = 0,
) -> str:
    """Busca preços por código CATMAT no BPS.

    O CATMAT (Catálogo de Materiais) é o código usado pelo governo para
    classificar materiais. Use este código para buscar preços específicos.

    Args:
        codigo_catmat: Código CATMAT do produto (ex: '267311', '269730').
        limite: Máximo de registros a buscar (padrão 1000).
        offset: Deslocamento para paginação.

    Returns:
        Compras do produto CATMAT com preços e fornecedores.
    """
    await ctx.info(f"Buscando CATMAT {codigo_catmat} no BPS...")
    resultado = await client.buscar_por_catmat(
        codigo_catmat,
        limite=limite,
        offset=offset,
    )
    await ctx.info(f"{resultado.total_retornado} registros encontrados")

    if not resultado.registros:
        return (
            f"Nenhum registro para CATMAT {codigo_catmat} neste lote. "
            f"Tente offset={offset + limite} para buscar no próximo lote."
        )

    return _format_resultado(resultado.registros, resultado.total_retornado, offset)


def _format_resultado(
    registros: Sequence[ComprasBPS],
    total: int,
    offset: int,
) -> str:
    """Format BPS records for LLM consumption."""
    lines = [f"**{total} registros encontrados**\n"]
    for i, rec in enumerate(registros[:50], 1):  # cap display at 50
        preco = format_brl(rec.preco_unitario) if rec.preco_unitario else "N/A"
        total_val = format_brl(rec.preco_total) if rec.preco_total else "N/A"
        desc = (rec.descricao_catmat or "N/A")[:100]
        gen = "Genérico" if rec.generico == "S" else "Referência"
        lines.extend(
            [
                f"### {i}. {desc}",
                f"**CATMAT:** {rec.codigo_br or 'N/A'} | **{gen}**",
                f"**Preço unit.:** {preco}"
                f" | **Qtd:** {rec.quantidade_itens_comprados or 'N/A'}"
                f" | **Total:** {total_val}",
                f"**Instituição:** {rec.nome_da_instituicao or 'N/A'}"
                f" ({rec.uf_da_instituicao or 'N/A'})",
                f"**Fornecedor:** {rec.fornecedor or 'N/A'}",
                f"**Data:** {rec.data_da_compra or 'N/A'}"
                f" | **Modalidade:** {rec.modalidade_da_compra or 'N/A'}",
                "",
            ]
        )

    if total > 50:
        lines.append(f"*(mostrando 50 de {total})*")
    return "\n".join(lines)
