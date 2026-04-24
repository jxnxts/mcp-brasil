"""Resources for isp_rj."""

from __future__ import annotations

import json

from . import DATASET_SPEC
from .constants import INDICADORES_PRINCIPAIS


def info_dataset() -> str:
    return json.dumps(
        {
            "id": DATASET_SPEC.id,
            "fonte": DATASET_SPEC.source,
            "url": DATASET_SPEC.url,
            "atualizacao": "mensal",
            "ativacao": "MCP_BRASIL_DATASETS=isp_rj",
        },
        ensure_ascii=False,
    )


def catalogo_indicadores() -> str:
    return json.dumps({"principais": list(INDICADORES_PRINCIPAIS)}, ensure_ascii=False)
