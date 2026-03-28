"""Static resources for the Imunização (PNI) feature.

Returns reference data as JSON strings for LLM consumption.
"""

from __future__ import annotations

import json

from .constants import GRUPOS_IMUNOBIOLOGICOS, METAS_COBERTURA


async def calendario_nacional() -> str:
    """Calendário Nacional de Vacinação — dados estruturados."""
    calendario = {}
    for grupo_key, grupo in GRUPOS_IMUNOBIOLOGICOS.items():
        calendario[grupo_key] = {
            "nome": grupo["nome"],
            "vacinas": grupo["vacinas"],
        }
    return json.dumps(calendario, ensure_ascii=False, indent=2)


async def metas_cobertura_vacinal() -> str:
    """Metas de cobertura vacinal por vacina (Ministério da Saúde)."""
    return json.dumps(METAS_COBERTURA, ensure_ascii=False, indent=2)
