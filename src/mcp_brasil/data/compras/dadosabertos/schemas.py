"""Pydantic schemas for the Dados Abertos Compras.gov.br API."""

from __future__ import annotations

from pydantic import BaseModel


class Licitacao(BaseModel):
    """Licitação do sistema legado SIASG/ComprasNet."""

    id_compra: str | None = None
    identificador: str | None = None
    numero_processo: str | None = None
    uasg: int | None = None
    modalidade: int | None = None
    nome_modalidade: str | None = None
    numero_aviso: int | None = None
    situacao_aviso: str | None = None
    tipo_pregao: str | None = None
    objeto: str | None = None
    valor_estimado_total: float | None = None
    valor_homologado_total: float | None = None
    numero_itens: int | None = None
    data_publicacao: str | None = None
    data_abertura_proposta: str | None = None
    nome_responsavel: str | None = None
    funcao_responsavel: str | None = None
    endereco_entrega_edital: str | None = None


class LicitacaoResultado(BaseModel):
    """Resultado paginado de busca de licitações."""

    total: int = 0
    licitacoes: list[Licitacao] = []


class ContratoDA(BaseModel):
    """Contrato do Compras.gov.br (Dados Abertos)."""

    codigo_orgao: str | None = None
    nome_orgao: str | None = None
    codigo_unidade_gestora: str | None = None
    nome_unidade_gestora: str | None = None
    numero_contrato: str | None = None
    nome_modalidade_compra: str | None = None
    nome_tipo: str | None = None
    nome_categoria: str | None = None
    ni_fornecedor: str | None = None
    nome_fornecedor: str | None = None
    processo: str | None = None
    objeto: str | None = None
    data_vigencia_inicial: str | None = None
    data_vigencia_final: str | None = None
    valor_global: float | None = None
    valor_parcela: float | None = None
    valor_acumulado: float | None = None


class ContratoDAResultado(BaseModel):
    """Resultado paginado de busca de contratos."""

    total: int = 0
    contratos: list[ContratoDA] = []


class FornecedorDA(BaseModel):
    """Fornecedor cadastrado no Compras.gov.br."""

    cnpj: str | None = None
    cpf: str | None = None
    nome_razao_social: str | None = None
    uf_sigla: str | None = None
    nome_municipio: str | None = None
    porte_empresa_nome: str | None = None
    natureza_juridica_nome: str | None = None
    nome_cnae: str | None = None
    ativo: bool | None = None
    habilitado_licitar: bool | None = None


class FornecedorDAResultado(BaseModel):
    """Resultado paginado de busca de fornecedores."""

    total: int = 0
    fornecedores: list[FornecedorDA] = []


class GrupoMaterial(BaseModel):
    """Grupo de material CATMAT."""

    codigo_grupo: int | None = None
    nome_grupo: str | None = None
    status_grupo: bool | None = None


class GrupoMaterialResultado(BaseModel):
    """Resultado de busca de grupos de material."""

    total: int = 0
    grupos: list[GrupoMaterial] = []


class ItemMaterial(BaseModel):
    """Item de material CATMAT."""

    codigo_item: int | None = None
    descricao_item: str | None = None
    codigo_grupo: int | None = None
    codigo_classe: int | None = None
    codigo_pdm: int | None = None
    status_item: bool | None = None


class ItemMaterialResultado(BaseModel):
    """Resultado paginado de busca de itens de material."""

    total: int = 0
    itens: list[ItemMaterial] = []


class ItemServico(BaseModel):
    """Item de serviço CATSER."""

    codigo_servico: int | None = None
    nome_servico: str | None = None
    codigo_secao: int | None = None
    codigo_divisao: int | None = None
    codigo_grupo: int | None = None
    codigo_classe: int | None = None
    status_servico: bool | None = None


class ItemServicoResultado(BaseModel):
    """Resultado paginado de busca de itens de serviço."""

    total: int = 0
    itens: list[ItemServico] = []


class Uasg(BaseModel):
    """Unidade Administrativa de Serviços Gerais."""

    codigo_uasg: str | None = None
    nome_uasg: str | None = None
    cnpj_cpf_orgao: str | None = None
    sigla_uf: str | None = None
    nome_municipio: str | None = None
    uso_sisg: bool | None = None
    status_uasg: bool | None = None


class UasgResultado(BaseModel):
    """Resultado paginado de busca de UASGs."""

    total: int = 0
    uasgs: list[Uasg] = []
