"""Resources for cvm_fundos."""

from __future__ import annotations

import json

from . import DATASET_SPEC


def info_dataset() -> str:
    return json.dumps(
        {
            "id": DATASET_SPEC.id,
            "fonte": DATASET_SPEC.source,
            "url": DATASET_SPEC.url,
            "atualizacao": "diária",
            "ativacao": "MCP_BRASIL_DATASETS=cvm_fundos",
        },
        ensure_ascii=False,
    )
