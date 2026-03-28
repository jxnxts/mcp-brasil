"""Static reference data for the OpenDataSUS feature.

Resources are read-only data sources that clients can pull.
They provide context to LLMs without requiring tool calls.
"""

from __future__ import annotations

import json

from .constants import DATASETS_CONHECIDOS, TAGS_COMUNS


def datasets_conhecidos() -> str:
    """Lista curada dos principais datasets do OpenDataSUS."""
    return json.dumps(DATASETS_CONHECIDOS, ensure_ascii=False, indent=2)


def tags_comuns() -> str:
    """Tags mais usadas nos datasets do OpenDataSUS."""
    return json.dumps(TAGS_COMUNS, ensure_ascii=False, indent=2)
