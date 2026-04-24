"""Feature tse_fefc — Fundo Eleitoral Especial / Fundo Partidário (FEFC/FP).

Relatórios TSE de distribuição do Fundo Especial de Financiamento de
Campanha (FEFC, criado em 2017 pela Lei 13.487) e do Fundo Partidário,
agregados por partido x UF x gênero x cor/raça.

Anos disponíveis: 2020, 2024 (TSE pulou 2022).

Ativação: ``MCP_BRASIL_DATASETS=tse_fefc``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "tse_fefc"
DATASET_TABLE = "fefc_genero"

_BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/fefc_fp"
_ANOS = (2020, 2024)

# fefc_genero_YYYY.csv é o arquivo agregado partido x gênero dentro de cada ZIP.
_SOURCES: tuple[tuple[str, str | None, str], ...] = tuple(
    (
        f"{_BASE_URL}/fefc_fp_{ano}.zip",
        f"fefc_genero_{ano}.csv",
        str(ano),
    )
    for ano in _ANOS
)

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=_SOURCES[-1][0],
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=5,
    source="TSE — Portal de Dados Abertos (fefc_fp 2020/2024)",
    description=(
        "Distribuição do Fundo Especial de Financiamento de Campanha (FEFC) "
        "por partido x gênero, eleições 2020 e 2024."
    ),
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": True,
        "quote": '"',
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["#NULO", "#NE"],
        "normalize_names": True,
        "all_varchar": True,
    },
    pii_columns=frozenset(),
    sources=_SOURCES,
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "TSE FEFC 2020/2024 — distribuição do Fundo Eleitoral por partido "
        "e gênero com consulta SQL via DuckDB. Opt-in: MCP_BRASIL_DATASETS=tse_fefc."
    ),
    version="0.1.0",
    api_base="https://cdn.tse.jus.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "tse",
        "eleicoes",
        "financiamento",
        "fundo-eleitoral",
        "fefc",
        "duckdb",
        "dataset",
    ],
)
