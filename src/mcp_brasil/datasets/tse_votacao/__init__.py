"""Feature tse_votacao — votos por candidato x município x zona, 2014-2024.

Agrupa ``votacao_candidato_munzona_{ANO}`` dos anos 2014, 2016, 2018, 2020,
2022 e 2024. Permite análises de ranking municipal, evolução histórica,
soma por UF/partido.

**Dataset pesado**: ~1.6GB ZIP total (mais pesado entre os TSE). Primeira
carga pode levar 5-10 minutos dependendo de rede.

Ativação: ``MCP_BRASIL_DATASETS=tse_votacao`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "tse_votacao"
DATASET_TABLE = "votacao"

_BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona"
_ANOS = (2014, 2016, 2018, 2020, 2022, 2024)

_SOURCES: tuple[tuple[str, str | None, str], ...] = tuple(
    (
        f"{_BASE_URL}/votacao_candidato_munzona_{ano}.zip",
        f"votacao_candidato_munzona_{ano}_BRASIL.csv",
        str(ano),
    )
    for ano in _ANOS
)

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=_SOURCES[-1][0],
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=1600,
    source="TSE — Portal de Dados Abertos (votacao_candidato_munzona, 2014-2024)",
    description=(
        "Votos por candidato x município x zona em 6 ciclos eleitorais. "
        "Federais: 2014, 2018, 2022. Municipais: 2016, 2020, 2024."
    ),
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": True,
        "quote": '"',
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["#NULO", "#NULO#", "#NE", "-4", "-3", "-1"],
        "normalize_names": True,
        "all_varchar": True,
    },
    pii_columns=frozenset(),
    sources=_SOURCES,
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "TSE votação por candidato x município x zona (2014-2024) com "
        "consulta SQL via DuckDB. Tools: votos_candidato, top_votados_ano, "
        "ranking_municipio, evolucao_partido_ano. "
        "Opt-in: MCP_BRASIL_DATASETS=tse_votacao (~1.6GB, 5-10min primeira carga)."
    ),
    version="0.1.0",
    api_base="https://cdn.tse.jus.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=["tse", "eleicoes", "votacao", "votos", "historico", "duckdb", "dataset"],
)
