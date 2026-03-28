"""Static reference data for the Farmácia Popular feature.

Resources are read-only data sources that clients can pull.
They provide context to LLMs without requiring tool calls.

Resources are registered with data:// URIs (without the feature namespace —
mount() adds the namespace prefix automatically).
"""

from __future__ import annotations

import json

from .constants import INDICACOES, MEDICAMENTOS


def catalogo_medicamentos() -> str:
    """Catálogo completo dos medicamentos do Programa Farmácia Popular.

    Todos os medicamentos com nome, princípio ativo, apresentação,
    indicação terapêutica e se é gratuito.
    """
    return json.dumps(MEDICAMENTOS, ensure_ascii=False, indent=2)


def indicacoes_terapeuticas() -> str:
    """Lista de indicações terapêuticas cobertas pelo Farmácia Popular."""
    return json.dumps(INDICACOES, ensure_ascii=False, indent=2)
