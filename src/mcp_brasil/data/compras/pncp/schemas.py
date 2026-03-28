"""Pydantic schemas for the Compras feature."""

from __future__ import annotations

from pydantic import BaseModel


class Contratacao(BaseModel):
    """Contratação pública retornada pelo PNCP."""

    orgao_cnpj: str | None = None
    orgao_nome: str | None = None
    ano: int | None = None
    numero_sequencial: int | None = None
    numero_controle_pncp: str | None = None
    objeto: str | None = None
    modalidade_id: int | None = None
    modalidade_nome: str | None = None
    situacao_id: int | None = None
    situacao_nome: str | None = None
    valor_estimado: float | None = None
    valor_homologado: float | None = None
    data_publicacao: str | None = None
    data_abertura: str | None = None
    uf: str | None = None
    municipio: str | None = None
    esfera: str | None = None
    link_pncp: str | None = None


class ContratacaoResultado(BaseModel):
    """Resultado paginado de busca de contratações."""

    total: int = 0
    contratacoes: list[Contratacao] = []


class Contrato(BaseModel):
    """Contrato público."""

    orgao_cnpj: str | None = None
    orgao_nome: str | None = None
    numero_contrato: str | None = None
    objeto: str | None = None
    fornecedor_cnpj: str | None = None
    fornecedor_nome: str | None = None
    valor_inicial: float | None = None
    valor_final: float | None = None
    vigencia_inicio: str | None = None
    vigencia_fim: str | None = None
    data_publicacao: str | None = None
    situacao: str | None = None


class ContratoResultado(BaseModel):
    """Resultado paginado de busca de contratos."""

    total: int = 0
    contratos: list[Contrato] = []


class AtaRegistroPreco(BaseModel):
    """Ata de registro de preço."""

    orgao_cnpj: str | None = None
    orgao_nome: str | None = None
    numero_ata: str | None = None
    objeto: str | None = None
    fornecedor_cnpj: str | None = None
    fornecedor_nome: str | None = None
    valor_total: float | None = None
    vigencia_inicio: str | None = None
    vigencia_fim: str | None = None
    situacao: str | None = None


class AtaResultado(BaseModel):
    """Resultado paginado de busca de atas."""

    total: int = 0
    atas: list[AtaRegistroPreco] = []


class Fornecedor(BaseModel):
    """Fornecedor de contratações públicas."""

    cnpj: str | None = None
    razao_social: str | None = None
    nome_fantasia: str | None = None
    municipio: str | None = None
    uf: str | None = None
    porte: str | None = None
    data_abertura: str | None = None


class FornecedorResultado(BaseModel):
    """Resultado paginado de busca de fornecedores."""

    total: int = 0
    fornecedores: list[Fornecedor] = []


class OrgaoContratante(BaseModel):
    """Órgão contratante no PNCP."""

    cnpj: str | None = None
    razao_social: str | None = None
    esfera: str | None = None
    poder: str | None = None
    uf: str | None = None
    municipio: str | None = None


class OrgaoResultado(BaseModel):
    """Resultado paginado de busca de órgãos."""

    total: int = 0
    orgaos: list[OrgaoContratante] = []


class ItemPca(BaseModel):
    """Item do Plano de Contratações Anual."""

    numero_item: int | None = None
    descricao: str | None = None
    quantidade_estimada: float | None = None
    valor_unitario: float | None = None
    valor_total: float | None = None
    unidade_fornecimento: str | None = None
    categoria: str | None = None
    data_desejada: str | None = None


class Pca(BaseModel):
    """Plano de Contratações Anual."""

    orgao_cnpj: str | None = None
    orgao_nome: str | None = None
    ano: int | None = None
    unidade_nome: str | None = None
    id_pca: str | None = None
    data_publicacao: str | None = None
    itens: list[ItemPca] = []


class PcaResultado(BaseModel):
    """Resultado paginado de busca de PCAs."""

    total: int = 0
    pcas: list[Pca] = []


class InstrumentoCobranca(BaseModel):
    """Instrumento de cobrança (nota fiscal) vinculado a contrato."""

    cnpj_orgao: str | None = None
    ano_contrato: int | None = None
    numero_instrumento: str | None = None
    tipo_nome: str | None = None
    data_emissao: str | None = None
    objeto_contrato: str | None = None
    fornecedor_nome: str | None = None
    fornecedor_cnpj: str | None = None
    valor_nf: str | None = None
    chave_nfe: str | None = None


class InstrumentoCobrancaResultado(BaseModel):
    """Resultado paginado de busca de instrumentos de cobrança."""

    total: int = 0
    instrumentos: list[InstrumentoCobranca] = []
