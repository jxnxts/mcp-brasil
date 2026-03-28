"""Imunização (PNI) — Programa Nacional de Imunizações.

Dados de vacinação via OpenDataSUS (CKAN) e Elasticsearch público.
Inclui calendário nacional, vacinas do SUS, metas de cobertura e
registros de vacinação (Covid-19 e rotina).
"""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="imunizacao",
    description=(
        "SI-PNI / Programa Nacional de Imunizações: registros de vacinação, "
        "calendário nacional, vacinas do SUS, metas de cobertura vacinal. "
        "Dados do OpenDataSUS (CKAN) e Elasticsearch público."
    ),
    version="0.1.0",
    api_base="https://opendatasus.saude.gov.br/api/3/action",
    requires_auth=False,
    tags=["saude", "vacinacao", "pni", "imunizacao", "cobertura", "sus"],
)
