"""Feature MJ — Ministério da Justiça e Segurança Pública (CKAN)."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="mj",
    description=(
        "MJSP — SINESP (ocorrências criminais), INFOPEN (prisional), PROCONs (Sindec), "
        "armas e segurança pública nacional"
    ),
    version="0.1.0",
    api_base="https://dados.mj.gov.br/api/3",
    requires_auth=False,
    tags=["mj", "mjsp", "sinesp", "infopen", "seguranca", "criminalidade", "prisional", "procon"],
)
