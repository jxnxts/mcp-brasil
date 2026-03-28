"""Pydantic schemas for the Imunização (PNI) feature."""

from __future__ import annotations

from pydantic import BaseModel


class RegistroVacinacao(BaseModel):
    """Registro individual de vacinação do Elasticsearch público."""

    municipio: str | None = None
    uf: str | None = None
    vacina_nome: str | None = None
    dose: str | None = None
    fabricante: str | None = None
    faixa_etaria: str | None = None
    sexo: str | None = None
    data_aplicacao: str | None = None
    estabelecimento: str | None = None
    grupo_atendimento: str | None = None


class AgregacaoVacinacao(BaseModel):
    """Resultado de agregação do Elasticsearch (ex: total por vacina)."""

    nome: str
    total: int


class DatasetPNI(BaseModel):
    """Dataset do PNI no OpenDataSUS (CKAN)."""

    id: str
    nome: str
    titulo: str | None = None
    descricao: str | None = None
    organizacao: str | None = None
    total_recursos: int = 0
    data_atualizacao: str | None = None


class RecursoPNI(BaseModel):
    """Recurso (arquivo) dentro de um dataset PNI."""

    id: str
    nome: str | None = None
    formato: str | None = None
    url: str | None = None


class VacinaSUS(BaseModel):
    """Vacina disponível no SUS (referência estática)."""

    sigla: str
    nome: str
    doses: int
    idade: str
    doencas: list[str] = []
    via: str | None = None
    grupo: str | None = None


class MetaCobertura(BaseModel):
    """Meta de cobertura vacinal definida pelo Ministério da Saúde."""

    vacina: str
    meta_pct: float
