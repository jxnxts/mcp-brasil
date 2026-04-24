"""Feature tse_bens — declaração de bens dos candidatos em 2024.

Dataset TSE (bem_candidato_2024) com todos os bens declarados pelos candidatos
no ato do registro — imóveis, veículos, ações, poupança etc.
~46MB ZIP → ~223MB CSV descompactado.

Para cruzar com candidatos, use ``sq_candidato`` como join key (também
presente em ``tse_candidatos``).

Ativação: ``MCP_BRASIL_DATASETS=tse_bens`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "tse_bens"
DATASET_TABLE = "bens_candidatos_2024"

DATASET_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato/bem_candidato_2024.zip"
ZIP_MEMBER = "bem_candidato_2024_BRASIL.csv"

_COLUMN_NAMES: list[str] = [
    "dt_geracao",
    "hh_geracao",
    "ano_eleicao",
    "cd_tipo_eleicao",
    "nm_tipo_eleicao",
    "cd_eleicao",
    "ds_eleicao",
    "dt_eleicao",
    "sg_uf",
    "sg_ue",
    "nm_ue",
    "sq_candidato",
    "nr_ordem_bem_candidato",
    "cd_tipo_bem_candidato",
    "ds_tipo_bem_candidato",
    "ds_bem_candidato",
    "vr_bem_candidato",
    "dt_ult_atual_bem_candidato",
    "hh_ult_atual_bem_candidato",
]


DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=DATASET_URL,
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=46,
    source="TSE — Portal de Dados Abertos (bem_candidato_2024)",
    description=(
        "Bens declarados por candidatos nas eleições municipais 2024 — "
        "imóveis, veículos, ações, poupança com valor declarado."
    ),
    zip_member=ZIP_MEMBER,
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": False,
        "skip": 1,
        "quote": '"',
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["#NULO", "#NE", "-4", "-3", "-1"],
        "names": _COLUMN_NAMES,
        "decimal_separator": ",",
        "thousands": ".",
        "dtypes": {
            "ano_eleicao": "INTEGER",
            "vr_bem_candidato": "DOUBLE",
            "nr_ordem_bem_candidato": "INTEGER",
            "cd_tipo_bem_candidato": "INTEGER",
        },
    },
    pii_columns=frozenset(),  # dataset institucional; nomes/bens são públicos
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "TSE bens declarados 2024 — patrimônio de candidatos com consulta SQL "
        "via DuckDB. Join key: sq_candidato (presente em tse_candidatos). "
        "Opt-in: MCP_BRASIL_DATASETS=tse_bens."
    ),
    version="0.1.0",
    api_base="https://cdn.tse.jus.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "tse",
        "eleicoes",
        "candidatos",
        "patrimonio",
        "bens",
        "2024",
        "duckdb",
        "dataset",
    ],
)
