"""Feature isp_rj — Estatísticas de Segurança Pública do Rio de Janeiro.

Base histórica mensal por CISP e município desde 1991, mantida pelo Instituto
de Segurança Pública. Inclui homicídios, roubos, furtos, feminicídios,
letalidade policial e dezenas de outros indicadores.

Fonte: ISP-RJ — ``www.ispdados.rj.gov.br``
Ativação: ``MCP_BRASIL_DATASETS=isp_rj``
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

from .constants import ISP_CSV_URL

DATASET_ID = "isp_rj"
DATASET_TABLE = "isp_rj_cisp_mensal"

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=ISP_CSV_URL,
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=3,
    source="ISP-RJ — Instituto de Segurança Pública (RJ)",
    description=(
        "Série histórica mensal de indicadores criminais por CISP/município "
        "no Rio de Janeiro, desde 1991."
    ),
    source_encoding="utf-8",
    csv_options={
        "delim": ";",
        "header": True,
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["", " ", "-"],
    },
    pii_columns=frozenset(),
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "ISP-RJ — estatísticas criminais mensais por CISP do RJ desde 1991. "
        "Consulta SQL via DuckDB local. Opt-in: MCP_BRASIL_DATASETS=isp_rj."
    ),
    version="0.1.0",
    api_base="https://www.ispdados.rj.gov.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "isp",
        "seguranca-publica",
        "criminalidade",
        "rj",
        "rio-de-janeiro",
        "homicidios",
        "roubos",
        "dataset",
        "duckdb",
    ],
)
