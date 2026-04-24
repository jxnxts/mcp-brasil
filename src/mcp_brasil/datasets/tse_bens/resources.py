"""Static reference data for tse_bens."""

from __future__ import annotations

import json

from . import DATASET_SPEC


def info_dataset() -> str:
    return json.dumps(
        {
            "id": DATASET_SPEC.id,
            "fonte": DATASET_SPEC.source,
            "url": DATASET_SPEC.url,
            "tamanho_zip": f"{DATASET_SPEC.approx_size_mb} MB",
            "membro_zip": DATASET_SPEC.zip_member,
            "ttl_dias": DATASET_SPEC.ttl_days,
            "ativacao": "MCP_BRASIL_DATASETS=tse_bens no .env",
            "join_key": "sq_candidato (presente em tse_candidatos)",
            "observacao": (
                "Tools top_patrimonios_cargo e resumo_patrimonio_partido requerem "
                "tse_candidatos também ativo (join via ATTACH em DuckDB)."
            ),
        },
        ensure_ascii=False,
        indent=2,
    )


def schema_tabela() -> str:
    cols = [
        ("sq_candidato", "VARCHAR", "ID do candidato (join com candidatos_2024)"),
        ("nr_ordem_bem_candidato", "INTEGER", "Ordem do bem na declaração"),
        ("ds_tipo_bem_candidato", "VARCHAR", "Categoria — imóvel, veículo, ação…"),
        ("ds_bem_candidato", "VARCHAR", "Descrição livre do bem"),
        ("vr_bem_candidato", "DOUBLE", "Valor declarado em R$"),
        ("sg_uf", "VARCHAR", "UF da eleição"),
        ("nm_ue", "VARCHAR", "Município"),
    ]
    return json.dumps(
        {
            "tabela": DATASET_SPEC.table,
            "colunas_principais": [{"name": c, "tipo": t, "desc": d} for c, t, d in cols],
        },
        ensure_ascii=False,
        indent=2,
    )
