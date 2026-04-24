"""Resources for B3."""

from __future__ import annotations

import json

from .constants import BLUE_CHIPS, INDICES_POPULARES


def catalogo_indices() -> str:
    return json.dumps(INDICES_POPULARES, ensure_ascii=False)


def catalogo_blue_chips() -> str:
    return json.dumps(list(BLUE_CHIPS), ensure_ascii=False)
