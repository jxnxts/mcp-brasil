"""Pydantic schemas for governadores."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Governador(BaseModel):
    """Governador em exercício de uma UF."""

    model_config = ConfigDict(extra="allow")

    uf: str
    nome: str
    nome_completo: str | None = None
    ano_eleicao: int | None = None
    mandato_inicio: str | None = None
    mandato_fim: str | None = None
    partido: str | None = None
    partido_sigla: str | None = None
    vice_governador: str | None = None
