"""Pydantic schemas for the BPS API."""

from __future__ import annotations

from pydantic import BaseModel


class ComprasBPS(BaseModel):
    """Registro de compra no Banco de Preços em Saúde."""

    ano_da_compra: str | None = None
    data_da_compra: str | None = None
    nome_da_instituicao: str | None = None
    cnpj_da_instituicao: str | None = None
    municipio_da_instituicao: str | None = None
    uf_da_instituicao: str | None = None
    codigo_br: str | None = None
    descricao_catmat: str | None = None
    unidade_de_fornecimento: str | None = None
    generico: str | None = None
    anvisa: str | None = None
    modalidade_da_compra: str | None = None
    tipo_da_compra: str | None = None
    fornecedor: str | None = None
    cnpj_do_fornecedor: str | None = None
    fabricante: str | None = None
    quantidade_itens_comprados: float | None = None
    preco_unitario: float | None = None
    preco_total: float | None = None


class BPSResultado(BaseModel):
    """Resultado paginado de busca no BPS."""

    total_retornado: int = 0
    registros: list[ComprasBPS] = []
