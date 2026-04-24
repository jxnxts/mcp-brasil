"""Feature spu_siapa — imóveis da União completos (SIAPA/SPIUNET via SPU).

Dataset grande (~220MB, 787k+ linhas) consolidado pela Secretaria do Patrimônio
da União e republicado no Nextcloud público. Cobre imóveis DOMINIAIS (em
aforamento/ocupação com particulares) além dos de uso especial — o que o
feature ``spu_imoveis`` (Raio-X APF) NÃO cobre.

Ativação: ``MCP_BRASIL_DATASETS=spu_siapa`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "spu_siapa"
DATASET_TABLE = "imoveis_siapa"

# Source: painel de transparência ativa do SPU — link estável Nextcloud
# (~220MB, latim-1 / Windows-1252, separador ';', decimal ',' BR-locale).
DATASET_URL = "https://drive.spu.gestao.gov.br/index.php/s/fMLLrXK5FFjteaj/download"

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=DATASET_URL,
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=220,
    source="SPU/MGI — painel patrimoniodetodos.gov.br via Nextcloud",
    description=(
        "Imóveis da União (SIAPA consolidado): dominiais com foreiros/ocupantes "
        "e de uso especial dos órgãos federais."
    ),
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": False,
        "skip": 1,
        "decimal_separator": ",",
        "thousands": ".",
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["-"],
        "dtypes": {
            "area_terreno_m2": "DOUBLE",
            "area_uniao_m2": "DOUBLE",
            "latitude": "DOUBLE",
            "longitude": "DOUBLE",
        },
        "names": [
            "classe",
            "rip_imovel",
            "rip_utilizacao",
            "data_cadastro",
            "uf",
            "municipio",
            "endereco",
            "bairro",
            "latitude",
            "longitude",
            "nivel_precisao",
            "conceituacao_terreno",
            "tipo_imovel",
            "regime_utilizacao",
            "proprietario_oficial",
            "data_inicio_utilizacao",
            "area_terreno_m2",
            "area_uniao_m2",
        ],
    },
    # CPF/CNPJ columns in the "responsáveis" slice would go here. The
    # primary imoveis file is institutional but keep the field ready.
    pii_columns=frozenset(),
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "SIAPA/SPIUNET consolidado: ~787k imóveis da União com consulta SQL "
        "via DuckDB local. Inclui dominiais (aforamento/ocupação) e uso especial. "
        "Opt-in: MCP_BRASIL_DATASETS=spu_siapa."
    ),
    version="0.1.0",
    api_base="https://drive.spu.gestao.gov.br",
    requires_auth=False,
    # Gate: feature só monta se o usuário ativou explicitamente
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "spu",
        "siapa",
        "imoveis-uniao",
        "dataset",
        "duckdb",
        "aforamento",
        "dominiais",
    ],
)
