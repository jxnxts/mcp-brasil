"""Feature tse_candidatos — registro de candidatos, eleições 2014-2024.

Agrupa os arquivos ``consulta_cand_{ANO}`` dos anos eleitorais 2014, 2016,
2018, 2020, 2022 e 2024 em uma única view DuckDB. Inclui eleições municipais
e federais/estaduais.

Schema varia entre anos (2016 tem colunas extras; nomes de e-mail mudam
entre NM_EMAIL/DS_EMAIL). A view usa ``UNION ALL BY NAME`` para consolidar
tudo — colunas ausentes em um ano viram NULL.

Ativação: ``MCP_BRASIL_DATASETS=tse_candidatos`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "tse_candidatos"
DATASET_TABLE = "candidatos"

_BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand"
_ANOS = (2014, 2016, 2018, 2020, 2022, 2024)

_SOURCES: tuple[tuple[str, str | None, str], ...] = tuple(
    (
        f"{_BASE_URL}/consulta_cand_{ano}.zip",
        f"consulta_cand_{ano}_BRASIL.csv",
        str(ano),
    )
    for ano in _ANOS
)

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=_SOURCES[-1][0],  # unused when sources is set; kept for manifest
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=290,  # sum of all years combined
    source="TSE — Portal de Dados Abertos (consulta_cand, 2014-2024)",
    description=(
        "Candidatos de todas as eleições 2014-2024 (municipais e federais). "
        "~4M registros consolidados via UNION ALL BY NAME."
    ),
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": True,
        "quote": '"',
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["#NULO", "#NULO#", "#NE", "-4", "-3", "-1"],
        "normalize_names": True,  # lowercase snake_case
        "all_varchar": True,  # avoid type mismatches across years
    },
    pii_columns=frozenset(
        {
            "nr_cpf_candidato",
            "nr_titulo_eleitoral_candidato",
            "ds_email",
            "nm_email",
        }
    ),
    sources=_SOURCES,
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "TSE candidatos 2014-2024 — ~4M candidatos de 6 eleições com consulta "
        "SQL via DuckDB. Inclui prefeitos, vereadores, deputados, senadores, "
        "governadores e presidente. Filtro por ano disponível. "
        "Opt-in: MCP_BRASIL_DATASETS=tse_candidatos."
    ),
    version="0.2.0",
    api_base="https://cdn.tse.jus.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "tse",
        "eleicoes",
        "candidatos",
        "politica",
        "historico",
        "duckdb",
        "dataset",
    ],
)
