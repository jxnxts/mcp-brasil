"""HTTP client for the BPS (Banco de Preços em Saúde) API.

Endpoint: https://apidadosabertos.saude.gov.br/economia-da-saude/bps
Auth: None required
Pagination: limit (max 1000) + offset
Filtering: Client-side only (API has no filter params)
"""

from __future__ import annotations

from typing import Any

from mcp_brasil._shared.http_client import http_get

from .constants import BPS_URL, DEFAULT_LIMIT, FIELD_MUNICIPIO, MAX_LIMIT
from .schemas import BPSResultado, ComprasBPS


def _parse_compra(item: dict[str, Any]) -> ComprasBPS:
    """Parse a BPS purchase record, handling soft-hyphen in field name."""
    return ComprasBPS(
        ano_da_compra=item.get("ano_da_compra"),
        data_da_compra=item.get("data_da_compra"),
        nome_da_instituicao=item.get("nome_da_instituicao"),
        cnpj_da_instituicao=item.get("cnpj_da_instituicao"),
        municipio_da_instituicao=item.get(FIELD_MUNICIPIO),
        uf_da_instituicao=item.get("uf_da_instituicao"),
        codigo_br=item.get("codigo_br"),
        descricao_catmat=item.get("descricao_catmat"),
        unidade_de_fornecimento=item.get("unidade_de_fornecimento"),
        generico=item.get("generico"),
        anvisa=item.get("anvisa"),
        modalidade_da_compra=item.get("modalidade_da_compra"),
        tipo_da_compra=item.get("tipo_da_compra"),
        fornecedor=item.get("fornecedor"),
        cnpj_do_fornecedor=item.get("cnpj_do_fornecedor"),
        fabricante=item.get("fabricante"),
        quantidade_itens_comprados=item.get("quantidade_itens_comprados"),
        preco_unitario=item.get("preco_unitario"),
        preco_total=item.get("preco_total"),
    )


async def consultar_precos(
    limite: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> BPSResultado:
    """Fetch BPS purchase records with pagination."""
    limite = min(limite, MAX_LIMIT)
    params: dict[str, str] = {
        "limit": str(limite),
        "offset": str(offset),
    }
    raw: Any = await http_get(BPS_URL, params=params)
    # API returns {"bps": [...]} wrapper
    items: list[dict[str, Any]] = []
    if isinstance(raw, dict):
        items = raw.get("bps", [])
    elif isinstance(raw, list):
        items = raw
    if not items:
        return BPSResultado()
    registros = [_parse_compra(i) for i in items]
    return BPSResultado(
        total_retornado=len(registros),
        registros=registros,
    )


async def buscar_por_catmat(
    codigo_catmat: str,
    limite: int = MAX_LIMIT,
    offset: int = 0,
) -> BPSResultado:
    """Fetch records and filter by CATMAT code client-side.

    The API has no server-side filter, so we fetch a batch and filter.
    """
    resultado = await consultar_precos(limite=limite, offset=offset)
    filtrados = [r for r in resultado.registros if r.codigo_br and r.codigo_br == codigo_catmat]
    return BPSResultado(
        total_retornado=len(filtrados),
        registros=filtrados,
    )


async def buscar_por_descricao(
    descricao: str,
    limite: int = MAX_LIMIT,
    offset: int = 0,
) -> BPSResultado:
    """Fetch records and filter by description keyword client-side."""
    resultado = await consultar_precos(limite=limite, offset=offset)
    termo = descricao.upper()
    filtrados = [
        r
        for r in resultado.registros
        if r.descricao_catmat and termo in r.descricao_catmat.upper()
    ]
    return BPSResultado(
        total_retornado=len(filtrados),
        registros=filtrados,
    )
