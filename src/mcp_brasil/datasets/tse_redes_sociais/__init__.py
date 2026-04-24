"""Feature tse_redes_sociais — URLs de redes sociais de candidatos, 2018-2024.

URLs declaradas pelos candidatos no ato do registro (Instagram, Facebook,
Twitter/X, Kwai, TikTok, site pessoal, etc.). Join com tse_candidatos via
sq_candidato.

Anos disponíveis: 2018, 2020, 2022, 2024 (TSE não publicou antes de 2018).

Ativação: ``MCP_BRASIL_DATASETS=tse_redes_sociais``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "tse_redes_sociais"
DATASET_TABLE = "redes_sociais"

_BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand"
_ANOS = (2018, 2020, 2022, 2024)

_SOURCES: tuple[tuple[str, str | None, str], ...] = tuple(
    (
        f"{_BASE_URL}/rede_social_candidato_{ano}.zip",
        f"rede_social_candidato_{ano}_BRASIL.csv",
        str(ano),
    )
    for ano in _ANOS
)

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=_SOURCES[-1][0],
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=34,
    source="TSE — Portal de Dados Abertos (rede_social_candidato, 2018-2024)",
    description=(
        "URLs de redes sociais declaradas por candidatos nas eleições 2018, 2020, 2022 e 2024."
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
        "TSE redes sociais 2018-2024 — Instagram/Facebook/Twitter dos "
        "candidatos com consulta SQL via DuckDB. Join com tse_candidatos "
        "via sq_candidato. Opt-in: MCP_BRASIL_DATASETS=tse_redes_sociais."
    ),
    version="0.1.0",
    api_base="https://cdn.tse.jus.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "tse",
        "eleicoes",
        "redes-sociais",
        "instagram",
        "facebook",
        "twitter",
        "duckdb",
        "dataset",
    ],
)
