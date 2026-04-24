"""Feature tse_bens — bens declarados por candidatos, eleições 2014-2024.

Agrupa ``bem_candidato_{ANO}`` de todos os anos eleitorais. Join key:
``sq_candidato`` (presente também em tse_candidatos).

Ativação: ``MCP_BRASIL_DATASETS=tse_bens`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "tse_bens"
DATASET_TABLE = "bens_candidatos"

_BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato"
_ANOS = (2014, 2016, 2018, 2020, 2022, 2024)

_SOURCES: tuple[tuple[str, str | None, str], ...] = tuple(
    (
        f"{_BASE_URL}/bem_candidato_{ano}.zip",
        f"bem_candidato_{ano}_BRASIL.csv",
        str(ano),
    )
    for ano in _ANOS
)

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=_SOURCES[-1][0],
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=205,
    source="TSE — Portal de Dados Abertos (bem_candidato, 2014-2024)",
    description=(
        "Bens declarados por candidatos em todas as eleições 2014-2024 — "
        "imóveis, veículos, ações, poupança. Join com tse_candidatos via sq_candidato."
    ),
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": True,
        "quote": '"',
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["#NULO", "#NE", "-4", "-3", "-1"],
        "normalize_names": True,
        "all_varchar": True,
    },
    pii_columns=frozenset(),
    sources=_SOURCES,
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "TSE bens declarados 2014-2024 — histórico de patrimônio de candidatos "
        "com consulta SQL via DuckDB. Join key: sq_candidato. "
        "Opt-in: MCP_BRASIL_DATASETS=tse_bens."
    ),
    version="0.2.0",
    api_base="https://cdn.tse.jus.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "tse",
        "eleicoes",
        "patrimonio",
        "bens",
        "historico",
        "duckdb",
        "dataset",
    ],
)
