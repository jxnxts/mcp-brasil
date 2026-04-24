"""Resources for governadores."""

from __future__ import annotations

import json

from .constants import UF_NOME


def catalogo_ufs() -> str:
    """Mapeamento sigla → nome das 27 UFs."""
    return json.dumps(UF_NOME, ensure_ascii=False)
