"""Static reference data for tse_votacao."""

from __future__ import annotations

import json

from . import DATASET_SPEC


def info_dataset() -> str:
    return json.dumps(
        {
            "id": DATASET_SPEC.id,
            "fonte": DATASET_SPEC.source,
            "anos_disponiveis": [int(s[2]) for s in DATASET_SPEC.sources],
            "tamanho_aproximado_total": f"{DATASET_SPEC.approx_size_mb} MB",
            "ttl_dias": DATASET_SPEC.ttl_days,
            "join_key": "sq_candidato (presente em tse_candidatos, tse_bens)",
            "aviso": (
                "Primeira carga baixa ~1.6GB; reserve 5-10 minutos "
                "dependendo de rede. Queries subsequentes rodam em ms."
            ),
        },
        ensure_ascii=False,
        indent=2,
    )


def schema_tabela() -> str:
    cols = [
        ("ano_eleicao", "VARCHAR", "Ano eleitoral (string, parse para int)"),
        ("nr_turno", "VARCHAR", "1 ou 2"),
        ("sg_uf", "VARCHAR", "UF"),
        ("cd_municipio", "VARCHAR", "Código IBGE do município"),
        ("nm_municipio", "VARCHAR", "Nome do município"),
        ("nr_zona", "VARCHAR", "Zona eleitoral"),
        ("ds_cargo", "VARCHAR", "Cargo disputado"),
        ("sq_candidato", "VARCHAR", "ID do candidato (join)"),
        ("nm_candidato", "VARCHAR", "Nome completo"),
        ("nm_urna_candidato", "VARCHAR", "Nome de urna"),
        ("sg_partido", "VARCHAR", "Sigla do partido"),
        ("qt_votos_nominais", "VARCHAR", "Votos nominais (parse para BIGINT)"),
        (
            "qt_votos_nominais_validos",
            "VARCHAR",
            "Votos nominais válidos (descarta brancos/nulos)",
        ),
        ("ds_sit_tot_turno", "VARCHAR", "Resultado (ELEITO/NÃO ELEITO/…)"),
        ("st_voto_em_transito", "VARCHAR", "Flag de voto em trânsito"),
    ]
    return json.dumps(
        {
            "tabela": DATASET_SPEC.table,
            "observacao": (
                "Todas as colunas são VARCHAR porque o CSV tem all_varchar=true "
                "(schema varia entre anos). Queries usam TRY_CAST/parse on-the-fly."
            ),
            "colunas_principais": [{"name": c, "tipo": t, "desc": d} for c, t, d in cols],
        },
        ensure_ascii=False,
        indent=2,
    )
