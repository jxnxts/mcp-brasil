"""Feature B3 — cotações e dados da bolsa brasileira.

Usa o agregador público ``brapi.dev`` que consolida dados da B3, Yahoo Finance
e outras fontes. REST pública, sem autenticação obrigatória (há plano pago
para históricos longos).
"""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="b3",
    description=(
        "B3/bolsa brasileira — cotações real-time de ações, FIIs, BDRs, criptomoedas via brapi.dev"
    ),
    version="0.1.0",
    api_base="https://brapi.dev/api",
    requires_auth=False,
    tags=["b3", "bolsa", "acoes", "fiis", "bdr", "cotacoes", "mercado", "investimentos"],
)
