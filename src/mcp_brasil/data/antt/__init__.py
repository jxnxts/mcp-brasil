"""Feature ANTT — transporte terrestre (rodoviário, passageiros, cargas)."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="antt",
    description=(
        "ANTT — rodovias concedidas, acidentes, transporte de cargas e passageiros, pedágios"
    ),
    version="0.1.0",
    api_base="https://dados.antt.gov.br/api/3",
    requires_auth=False,
    tags=["antt", "transporte", "rodovias", "passageiros", "cargas", "pedagio", "acidentes"],
)
