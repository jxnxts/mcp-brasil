"""Feature noticias — agregador de RSS de notícias políticas e de mercado.

Consolida feeds RSS oficiais e confiáveis:
- Câmara dos Deputados (Agência Câmara)
- Senado Federal (Senado Notícias)
- Agência Brasil (EBC)
- Banco Central (comunicados)
- Planalto (atos oficiais)
"""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="noticias",
    description=(
        "Notícias via RSS — Câmara, Senado, Agência Brasil, BCB (política, economia, governo)"
    ),
    version="0.1.0",
    api_base="https://agenciabrasil.ebc.com.br",
    requires_auth=False,
    tags=["noticias", "rss", "politica", "economia", "camara", "senado", "agencia-brasil"],
)
