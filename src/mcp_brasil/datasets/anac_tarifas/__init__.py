"""Feature anac_tarifas — microdados de tarifas aéreas domésticas.

Cada linha = 1 bilhete vendido: ano, mês, empresa (ICAO), origem (ICAO),
destino (ICAO), tarifa BRL, assentos. ~4,3 milhões de linhas/ano.

**Popular o cache** (antes do primeiro uso):

    uv sync --group dev
    uv run playwright install chromium
    uv run python scripts/refresh_anac_tarifas.py --ano 2024

O script acima usa Playwright pra driveSAS ANAC (form ASP.NET) e gera
o ``anac_tarifas.duckdb`` no cache local. Em produção, o CI roda esse
script e sobe o ``.duckdb`` pro Azure Files, de onde o Container App
lê em read-only.

Ativação: ``MCP_BRASIL_DATASETS=anac_tarifas`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "anac_tarifas"
DATASET_TABLE = "tarifas"

# URL usado só como identificador semântico (ensure_loaded é bypass-ed
# porque o scraper pré-popula o .duckdb diretamente). A URL real do
# scraper está em scripts/refresh_anac_tarifas.py.
DATASET_URL = "https://sas.anac.gov.br/sas/downloads/view/frmDownload.aspx"

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=DATASET_URL,
    table=DATASET_TABLE,
    ttl_days=90,
    approx_size_mb=40,
    source="ANAC SAS — Tarifas Aéreas Domésticas (microdados mensais)",
    description=(
        "Microdados de tarifas: cada linha 1 bilhete vendido. "
        "Campos: ano, mes, empresa, origem, destino, tarifa, assentos."
    ),
    source_encoding="cp1252",
    csv_options={},  # cache é pré-populado por scripts/refresh_anac_tarifas.py
    pii_columns=frozenset(),
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "ANAC Tarifas — ~4,3M linhas/ano de bilhetes vendidos, com "
        "consulta SQL via DuckDB. Preço médio por rota, série histórica, "
        "comparativo entre companhias. Popular cache com "
        "scripts/refresh_anac_tarifas.py. Opt-in: "
        "MCP_BRASIL_DATASETS=anac_tarifas."
    ),
    version="0.1.0",
    api_base="https://sas.anac.gov.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "anac",
        "aviacao",
        "tarifas",
        "precos",
        "passagens",
        "dataset",
        "duckdb",
    ],
)
