"""Static reference data for tse_candidatos."""

from __future__ import annotations

import json

from . import DATASET_SPEC
from .constants import CARGOS_MUNICIPAIS, SIT_TOTALIZACAO


def info_dataset() -> str:
    """Metadados do dataset."""
    return json.dumps(
        {
            "id": DATASET_SPEC.id,
            "fonte": DATASET_SPEC.source,
            "url": DATASET_SPEC.url,
            "tamanho_zip": f"{DATASET_SPEC.approx_size_mb} MB",
            "tamanho_csv_descompactado": "~243 MB",
            "membro_zip": DATASET_SPEC.zip_member,
            "ttl_dias": DATASET_SPEC.ttl_days,
            "encoding_origem": DATASET_SPEC.source_encoding,
            "pii": sorted(DATASET_SPEC.pii_columns),
            "ativacao": "MCP_BRASIL_DATASETS=tse_candidatos no .env",
            "lgpd": (
                "CPF, título eleitoral e email são mascarados por padrão. "
                "Liberação via MCP_BRASIL_LGPD_ALLOW_PII=tse_candidatos."
            ),
        },
        ensure_ascii=False,
        indent=2,
    )


def catalogo_valores() -> str:
    """Valores comuns dos campos categóricos principais."""
    return json.dumps(
        {
            "cargos_municipais_2024": list(CARGOS_MUNICIPAIS),
            "situacao_totalizacao": list(SIT_TOTALIZACAO),
            "nota": (
                "Para valores atualizados em runtime use valores_distintos_candidatos(coluna=...)."
            ),
        },
        ensure_ascii=False,
        indent=2,
    )


def schema_tabela() -> str:
    """Schema da tabela candidatos_2024."""
    cols_descr = [
        ("ano_eleicao", "INTEGER", "Ano (2024)"),
        ("ds_eleicao", "VARCHAR", "Descrição da eleição"),
        ("nr_turno", "INTEGER", "1 ou 2 (2º turno em capitais)"),
        ("sg_uf", "VARCHAR", "UF (SP, RJ…)"),
        ("sg_ue", "VARCHAR", "Código IBGE da unidade eleitoral (município)"),
        ("nm_ue", "VARCHAR", "Nome do município"),
        ("ds_cargo", "VARCHAR", "PREFEITO / VICE-PREFEITO / VEREADOR"),
        ("sq_candidato", "VARCHAR", "ID único do candidato (use para joins)"),
        ("nr_candidato", "INTEGER", "Número na urna"),
        ("nm_candidato", "VARCHAR", "Nome completo"),
        ("nm_urna_candidato", "VARCHAR", "Nome de urna"),
        ("nr_cpf_candidato", "VARCHAR", "CPF (PII — mascarado por padrão)"),
        ("ds_email", "VARCHAR", "E-mail (PII — mascarado)"),
        ("sg_partido", "VARCHAR", "Sigla do partido"),
        ("nm_partido", "VARCHAR", "Nome completo do partido"),
        ("ds_sit_tot_turno", "VARCHAR", "ELEITO / NÃO ELEITO / SUPLENTE etc."),
        ("ds_genero", "VARCHAR", "MASCULINO / FEMININO"),
        ("ds_grau_instrucao", "VARCHAR", "Escolaridade"),
        ("ds_cor_raca", "VARCHAR", "Raça/cor declarada"),
        ("ds_ocupacao", "VARCHAR", "Ocupação declarada"),
        ("ds_estado_civil", "VARCHAR", "Estado civil"),
    ]
    return json.dumps(
        {
            "tabela": DATASET_SPEC.table,
            "colunas_principais": [{"name": c, "tipo": t, "desc": d} for c, t, d in cols_descr],
            "observacao": "Existem 50 colunas no total; use DESCRIBE na query para ver todas.",
        },
        ensure_ascii=False,
        indent=2,
    )
