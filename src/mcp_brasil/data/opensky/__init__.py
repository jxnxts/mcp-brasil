"""Feature OpenSky — rastreamento de voos ao vivo (ADS-B).

Fonte: OpenSky Network (rede colaborativa de receptores ADS-B).
API pública: ``opensky-network.org/api``.
"""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="opensky",
    description="OpenSky Network — voos ao vivo sobre o Brasil via ADS-B (rede colaborativa)",
    version="0.1.0",
    api_base="https://opensky-network.org/api",
    requires_auth=False,
    tags=["opensky", "voos", "ads-b", "aviacao", "rastreamento"],
)
