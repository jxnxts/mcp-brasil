"""Feature OpenDataSUS — Portal de dados abertos do SUS."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="opendatasus",
    description=(
        "OpenDataSUS: portal de dados abertos do SUS (CKAN API). "
        "Busca e consulta de datasets de saúde pública — hospitais, leitos, "
        "vacinação, SRAG, qualidade da água e agravos de notificação."
    ),
    version="0.1.0",
    api_base="https://opendatasus.saude.gov.br/api/3/action",
    requires_auth=False,
    tags=["saude", "sus", "datasus", "opendatasus", "ckan", "dados-abertos"],
)
