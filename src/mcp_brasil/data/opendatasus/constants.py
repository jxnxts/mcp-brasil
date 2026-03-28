"""Constants for the OpenDataSUS feature.

API: CKAN standard at https://opendatasus.saude.gov.br/api/3/action
"""

API_BASE = "https://opendatasus.saude.gov.br/api/3/action"

PACKAGE_LIST_URL = f"{API_BASE}/package_list"
PACKAGE_SEARCH_URL = f"{API_BASE}/package_search"
PACKAGE_SHOW_URL = f"{API_BASE}/package_show"
DATASTORE_SEARCH_URL = f"{API_BASE}/datastore_search"

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# Well-known datasets on OpenDataSUS
DATASETS_CONHECIDOS: list[dict[str, str]] = [
    {
        "nome": "hospitais-leitos",
        "titulo": "Hospitais e Leitos",
        "descricao": "Dados consolidados de hospitais e leitos no Brasil.",
    },
    {
        "nome": "covid-19-vacinacao",
        "titulo": "Campanha Nacional de Vacinação contra Covid-19",
        "descricao": "Registro de vacinação contra Covid-19 por município e UF.",
    },
    {
        "nome": "srag",
        "titulo": "SRAG - Síndrome Respiratória Aguda Grave",
        "descricao": "Dados de vigilância de SRAG hospitalizados e óbitos.",
    },
    {
        "nome": "sisagua",
        "titulo": "SISAGUA - Qualidade da Água",
        "descricao": "Monitoramento da qualidade da água para consumo humano.",
    },
    {
        "nome": "sinan",
        "titulo": "SINAN - Agravos de Notificação",
        "descricao": "Doenças e agravos de notificação compulsória.",
    },
]

# Common tags used in OpenDataSUS
TAGS_COMUNS: list[str] = [
    "covid-19",
    "vacinação",
    "srag",
    "leitos",
    "hospitais",
    "datasus",
    "sinan",
    "sisagua",
    "vigilância",
    "epidemiologia",
    "sus",
    "saúde",
]
