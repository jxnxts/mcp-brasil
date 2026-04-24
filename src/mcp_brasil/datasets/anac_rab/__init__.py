"""Feature anac_rab — Registro Aeronáutico Brasileiro (RAB).

Aeronaves civis registradas no Brasil (matrícula, proprietário, operador,
fabricante, modelo, motor, capacidade, validade do CA).

Fonte: ANAC — dados abertos, atualização semanal.
URL estável: ``sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv``

Ativação: ``MCP_BRASIL_DATASETS=anac_rab`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "anac_rab"
DATASET_TABLE = "rab"

DATASET_URL = "https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv"

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=DATASET_URL,
    table=DATASET_TABLE,
    ttl_days=7,  # atualização semanal
    approx_size_mb=13,
    source="ANAC — dados abertos do Registro Aeronáutico Brasileiro",
    description=(
        "Aeronaves civis brasileiras: matrícula, proprietários, operadores, "
        "fabricante, modelo, tipo de motor, capacidade, validade CA."
    ),
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": True,
        "skip": 1,  # pula linha "Atualizado em: YYYY-MM-DD"
        "quote": '"',
        "ignore_errors": True,
        "sample_size": -1,
        "all_varchar": True,
        "normalize_names": True,
    },
    pii_columns=frozenset(),  # CPFs aparecem nos campos compostos; tool expõe redacted por default
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "ANAC RAB — Registro Aeronáutico Brasileiro (~75k aeronaves) com "
        "consulta SQL via DuckDB. Busca por matrícula, operador, fabricante, "
        "UF. Opt-in: MCP_BRASIL_DATASETS=anac_rab."
    ),
    version="0.1.0",
    api_base="https://sistemas.anac.gov.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "anac",
        "aviacao",
        "aeronaves",
        "rab",
        "dataset",
        "duckdb",
    ],
)
