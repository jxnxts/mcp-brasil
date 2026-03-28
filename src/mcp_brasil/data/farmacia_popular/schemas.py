"""Pydantic schemas for the Farmácia Popular feature."""

from __future__ import annotations

from pydantic import BaseModel


class Medicamento(BaseModel):
    """Medicamento do Programa Farmácia Popular."""

    nome: str
    principio_ativo: str
    apresentacao: str
    indicacao: str
    gratuito: bool = True


class FarmaciaEstabelecimento(BaseModel):
    """Farmácia credenciada ao programa (dados CNES)."""

    codigo_cnes: str | None = None
    nome_fantasia: str | None = None
    nome_razao_social: str | None = None
    tipo_gestao: str | None = None
    codigo_municipio: str | None = None
    codigo_uf: str | None = None
    endereco: str | None = None


class EstatisticasPrograma(BaseModel):
    """Estatísticas consolidadas do Programa Farmácia Popular."""

    total_medicamentos: int
    total_indicacoes: int
    todos_gratuitos: bool = True
    indicacoes: list[str]
    medicamentos_por_indicacao: dict[str, int]
