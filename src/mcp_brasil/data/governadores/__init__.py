"""Feature governadores — governadores de estados brasileiros em exercício.

Fonte: dataset público mantido por GusFurtado em
``github.com/GusFurtado/dab_assets``, consumido também pelo pacote
``DadosAbertosBrasil``. Atualizado manualmente a cada eleição/sucessão.
"""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="governadores",
    description=(
        "Governadores de todos os estados e DF em exercício — nome, partido, mandato, vice"
    ),
    version="0.1.0",
    api_base="https://raw.githubusercontent.com/GusFurtado/dab_assets",
    requires_auth=False,
    tags=["governadores", "ufs", "executivo", "estados", "politica"],
)
