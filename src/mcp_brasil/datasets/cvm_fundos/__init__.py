"""Feature cvm_fundos — Cadastro de Fundos de Investimento (CVM).

Base cadastral de todos os fundos de investimento registrados na CVM,
com administrador, gestor, patrimônio líquido, classe, taxa de adm, etc.

Fonte: CVM — ``dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv``
Atualização: diária.

Ativação: ``MCP_BRASIL_DATASETS=cvm_fundos`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

from .constants import CVM_CAD_URL

DATASET_ID = "cvm_fundos"
DATASET_TABLE = "cad_fi"

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=CVM_CAD_URL,
    table=DATASET_TABLE,
    ttl_days=7,
    approx_size_mb=60,
    source="CVM — Cadastro de Fundos de Investimento",
    description=(
        "Cadastro de fundos de investimento da CVM: CNPJ, denominação, classe, "
        "administrador, gestor, PL, taxa de adm/performance, situação."
    ),
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": True,
        "decimal_separator": ",",
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["", " "],
        "dtypes": {"VL_PATRIM_LIQ": "DOUBLE", "TAXA_ADM": "DOUBLE", "TAXA_PERFM": "DOUBLE"},
    },
    # CNPJ_FUNDO e CPF_CNPJ_GESTOR são institucionais (PJ) — não PII sensível
    pii_columns=frozenset(),
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "CVM — cadastro de fundos de investimento (~40k fundos, todos registrados na CVM). "
        "Consulta SQL via DuckDB. Opt-in: MCP_BRASIL_DATASETS=cvm_fundos."
    ),
    version="0.1.0",
    api_base="https://dados.cvm.gov.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=["cvm", "fundos", "investimento", "cadastro", "dataset", "duckdb"],
)
