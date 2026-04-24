"""Feature anac_pontualidade — % de atrasos e cancelamentos mensais (Resolução 218/ANAC).

Agrega CSVs mensais "Anexo I" com, por empresa+voo+rota: número de etapas
previstas, % cancelamentos, % atrasos >30min, % atrasos >60min.

Cobertura inicial: 12 meses de 2024.

Ativação: ``MCP_BRASIL_DATASETS=anac_pontualidade`` no ``.env``.
"""

from urllib.parse import quote

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "anac_pontualidade"
DATASET_TABLE = "pontualidade"

_BASE_URL = (
    "https://sistemas.anac.gov.br/dadosabertos/"
    "Voos e operações aéreas/Percentuais de atrasos e cancelamentos"
)

# Meses usam nome em minúsculas no path (divergência vs VRA)
_MESES_LOWER = [
    (1, "janeiro"),
    (2, "fevereiro"),
    (3, "março"),
    (4, "abril"),
    (5, "maio"),
    (6, "junho"),
    (7, "julho"),
    (8, "agosto"),
    (9, "setembro"),
    (10, "outubro"),
    (11, "novembro"),
    (12, "dezembro"),
]

_ANOS = [2024]


def _build_sources() -> tuple[tuple[str, str | None, str], ...]:
    out: list[tuple[str, str | None, str]] = []
    for ano in _ANOS:
        for mes_num, mes_nome in _MESES_LOWER:
            pasta = f"{mes_num:02d} - {mes_nome}"
            arquivo = "Anexo I.csv"
            url = f"{_BASE_URL}/{ano}/{pasta}/{arquivo}"
            encoded = (
                url.replace(" ", "%20")
                .replace("ç", quote("ç"))
                .replace("é", quote("é"))
                .replace("á", quote("á"))
            )
            suffix = f"{ano}{mes_num:02d}"
            out.append((encoded, None, suffix))
    return tuple(out)


_SOURCES = _build_sources()

DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=_SOURCES[-1][0],
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=25,  # ~2 MB x 12 meses
    source="ANAC — Resolução 218 (Percentuais de Atrasos e Cancelamentos)",
    description=(
        "% de atrasos (>30min, >60min) e cancelamentos por empresa+rota, "
        "mensal. Anexo I da Resolução 218 (2024)."
    ),
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": True,
        "skip": 1,  # pula 'Atualizado em: YYYY-MM-DD'
        "quote": '"',
        "ignore_errors": True,
        "sample_size": -1,
        "all_varchar": True,
        "normalize_names": True,
    },
    pii_columns=frozenset(),
    sources=_SOURCES,
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "ANAC Pontualidade — % atrasos/cancelamentos mensais (Res. 218) "
        "com consulta SQL via DuckDB. Opt-in: "
        "MCP_BRASIL_DATASETS=anac_pontualidade."
    ),
    version="0.1.0",
    api_base="https://sistemas.anac.gov.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "anac",
        "aviacao",
        "pontualidade",
        "atrasos",
        "cancelamentos",
        "dataset",
        "duckdb",
    ],
)
