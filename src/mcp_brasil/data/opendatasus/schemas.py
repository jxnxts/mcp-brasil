"""Pydantic schemas for the OpenDataSUS feature."""

from __future__ import annotations

from pydantic import BaseModel


class RecursoDataset(BaseModel):
    """Recurso (arquivo) dentro de um dataset CKAN."""

    id: str
    nome: str | None = None
    formato: str | None = None
    url: str | None = None
    descricao: str | None = None


class DatasetOpenDataSUS(BaseModel):
    """Dataset do portal OpenDataSUS."""

    id: str
    nome: str
    titulo: str | None = None
    descricao: str | None = None
    organizacao: str | None = None
    tags: list[str] = []
    recursos: list[RecursoDataset] = []
    total_recursos: int = 0
    data_criacao: str | None = None
    data_atualizacao: str | None = None


class RegistroDataStore(BaseModel):
    """Registro genérico de um DataStore CKAN."""

    campos: dict[str, str | int | float | bool | None]
