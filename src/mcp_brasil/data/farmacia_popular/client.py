"""HTTP client for the Farmácia Popular feature.

Uses CNES API to search pharmacies. Medication data is static (from constants).

Endpoints:
    - /estabelecimentos (CNES) → buscar_farmacias
"""

from __future__ import annotations

from typing import Any

from mcp_brasil._shared.http_client import http_get

from .constants import (
    DEFAULT_LIMIT,
    ESTABELECIMENTOS_URL,
    INDICACOES,
    MAX_LIMIT,
    MEDICAMENTOS,
    TIPO_FARMACIA,
)
from .schemas import EstatisticasPrograma, FarmaciaEstabelecimento, Medicamento


def _parse_farmacia(raw: dict[str, Any]) -> FarmaciaEstabelecimento:
    """Parse a raw CNES establishment dict into a FarmaciaEstabelecimento model."""
    return FarmaciaEstabelecimento(
        codigo_cnes=str(raw.get("codigo_cnes", "") or ""),
        nome_fantasia=raw.get("nome_fantasia"),
        nome_razao_social=raw.get("nome_razao_social"),
        tipo_gestao=raw.get("tipo_gestao"),
        codigo_municipio=str(raw.get("codigo_municipio", "") or ""),
        codigo_uf=str(raw.get("codigo_uf", "") or ""),
        endereco=raw.get("endereco"),
    )


async def buscar_farmacias(
    *,
    codigo_municipio: str | None = None,
    codigo_uf: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[FarmaciaEstabelecimento]:
    """Search pharmacies from CNES (type 43 = Farmácia).

    API: GET /estabelecimentos?codigo_tipo_estabelecimento=43

    Args:
        codigo_municipio: IBGE municipality code.
        codigo_uf: IBGE state code.
        limit: Max results per page.
        offset: Pagination offset.
    """
    params: dict[str, Any] = {
        "codigo_tipo_estabelecimento": TIPO_FARMACIA,
        "status": 1,
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
    }
    if codigo_municipio:
        params["codigo_municipio"] = codigo_municipio
    if codigo_uf:
        params["codigo_uf"] = codigo_uf

    data: list[dict[str, Any]] = await http_get(ESTABELECIMENTOS_URL, params=params)
    return [_parse_farmacia(item) for item in data]


def _parse_medicamento(raw: dict[str, str | bool]) -> Medicamento:
    """Parse a medication dict from constants into a Medicamento model."""
    return Medicamento(
        nome=str(raw["nome"]),
        principio_ativo=str(raw["principio_ativo"]),
        apresentacao=str(raw["apresentacao"]),
        indicacao=str(raw["indicacao"]),
        gratuito=bool(raw.get("gratuito", True)),
    )


def listar_medicamentos() -> list[Medicamento]:
    """Return all medications from the Farmácia Popular program.

    Data source: static list based on the official Ministério da Saúde catalog.
    """
    return [_parse_medicamento(med) for med in MEDICAMENTOS]


def buscar_medicamento_por_nome(nome: str) -> list[Medicamento]:
    """Search medications by name or active ingredient.

    Args:
        nome: Full or partial name to search (case-insensitive).
    """
    nome_lower = nome.lower()
    return [
        _parse_medicamento(med)
        for med in MEDICAMENTOS
        if nome_lower in str(med["nome"]).lower()
        or nome_lower in str(med["principio_ativo"]).lower()
    ]


def buscar_por_indicacao(indicacao: str) -> list[Medicamento]:
    """Search medications by therapeutic indication.

    Args:
        indicacao: Condition name, e.g. "diabetes", "hipertensão".
    """
    indicacao_lower = indicacao.lower()
    return [
        _parse_medicamento(med)
        for med in MEDICAMENTOS
        if indicacao_lower in str(med["indicacao"]).lower()
    ]


def obter_estatisticas() -> EstatisticasPrograma:
    """Return consolidated statistics about the program."""
    med_por_indicacao: dict[str, int] = {}
    for med in MEDICAMENTOS:
        ind = str(med["indicacao"])
        med_por_indicacao[ind] = med_por_indicacao.get(ind, 0) + 1

    return EstatisticasPrograma(
        total_medicamentos=len(MEDICAMENTOS),
        total_indicacoes=len(INDICACOES),
        todos_gratuitos=True,
        indicacoes=INDICACOES,
        medicamentos_por_indicacao=med_por_indicacao,
    )
