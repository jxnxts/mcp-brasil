"""Feature Farmácia Popular — medicamentos gratuitos e farmácias credenciadas."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="farmacia_popular",
    description=(
        "Farmácia Popular do Brasil: consulta de medicamentos gratuitos, "
        "farmácias credenciadas por município/UF, busca por indicação "
        "terapêutica e informações de elegibilidade do programa."
    ),
    version="0.1.0",
    api_base="https://apidadosabertos.saude.gov.br/cnes",
    requires_auth=False,
    tags=["saude", "farmacia", "medicamentos", "sus", "farmacia-popular"],
)
