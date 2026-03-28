"""Feature BPS — Banco de Preços em Saúde."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="bps",
    description=(
        "Banco de Preços em Saúde (BPS): preços de medicamentos e "
        "dispositivos médicos comprados pelo governo em todas as esferas."
    ),
    version="0.1.0",
    api_base="https://apidadosabertos.saude.gov.br/economia-da-saude/bps",
    requires_auth=False,
    tags=["saude", "medicamentos", "precos", "bps", "catmat"],
)
