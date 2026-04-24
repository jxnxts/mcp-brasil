"""Resources for noticias."""

from __future__ import annotations

import json

from .constants import FEEDS_ECONOMIA, FEEDS_POLITICA, FEEDS_TEMAS_CAMARA


def catalogo_fontes() -> str:
    """Catálogo completo de feeds RSS disponíveis."""
    return json.dumps(
        {
            "politica": FEEDS_POLITICA,
            "economia": FEEDS_ECONOMIA,
            "temas_camara": FEEDS_TEMAS_CAMARA,
        },
        ensure_ascii=False,
    )
