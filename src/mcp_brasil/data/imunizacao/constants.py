"""Constants for the Imunização (PNI) feature.

Sources:
    - OpenDataSUS CKAN: https://opendatasus.saude.gov.br/api/3/action/
    - Elasticsearch PNI: https://imunizacao.saude.gov.br (public credentials)
    - Calendário Nacional de Vacinação (Ministério da Saúde)
"""

# ---------------------------------------------------------------------------
# CKAN API (OpenDataSUS)
# ---------------------------------------------------------------------------

CKAN_API_BASE = "https://opendatasus.saude.gov.br/api/3/action"
CKAN_PACKAGE_SEARCH_URL = f"{CKAN_API_BASE}/package_search"
CKAN_PACKAGE_SHOW_URL = f"{CKAN_API_BASE}/package_show"
CKAN_DATASTORE_SEARCH_URL = f"{CKAN_API_BASE}/datastore_search"

# Well-known PNI datasets on OpenDataSUS
DATASETS_PNI: dict[str, str] = {
    "doses_2025": "doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2025",
    "doses_2024": "doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2024",
    "covid": "covid-19-vacinacao",
}

# ---------------------------------------------------------------------------
# Elasticsearch (public credentials — published on OpenDataSUS portal)
# ---------------------------------------------------------------------------

ES_BASE_URL = "https://imunizacao.saude.gov.br"
ES_INDEX = "desc-imunizacao"
ES_SEARCH_URL = f"{ES_BASE_URL}/{ES_INDEX}/_search"
ES_USER = "imunizacao_public"
ES_PASSWORD = "qlto5t&7r_@+#Tlstigi"

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# ---------------------------------------------------------------------------
# Calendário Nacional de Vacinação (Ministério da Saúde, 2024)
# ---------------------------------------------------------------------------

GRUPOS_IMUNOBIOLOGICOS: dict[str, dict[str, object]] = {
    "basicas_crianca": {
        "nome": "Vacinas Básicas da Criança",
        "vacinas": [
            {
                "sigla": "BCG",
                "nome": "BCG",
                "doses": 1,
                "idade": "Ao nascer",
                "doencas": ["Tuberculose (formas graves)"],
                "via": "Intradérmica",
            },
            {
                "sigla": "HepB",
                "nome": "Hepatite B",
                "doses": 3,
                "idade": "Ao nascer, 2m, 6m",
                "doencas": ["Hepatite B"],
                "via": "Intramuscular",
            },
            {
                "sigla": "VIP/VOP",
                "nome": "Poliomielite",
                "doses": 5,
                "idade": "2m, 4m, 6m + reforços 15m e 4a",
                "doencas": ["Poliomielite"],
                "via": "Intramuscular/Oral",
            },
            {
                "sigla": "Penta",
                "nome": "Pentavalente (DTP+HB+Hib)",
                "doses": 3,
                "idade": "2m, 4m, 6m",
                "doencas": [
                    "Difteria",
                    "Tétano",
                    "Coqueluche",
                    "Hepatite B",
                    "Haemophilus influenzae b",
                ],
                "via": "Intramuscular",
            },
            {
                "sigla": "Pneumo10",
                "nome": "Pneumocócica 10-valente",
                "doses": 3,
                "idade": "2m, 4m + reforço 12m",
                "doencas": ["Pneumonia", "Meningite", "Otite"],
                "via": "Intramuscular",
            },
            {
                "sigla": "Rotavírus",
                "nome": "Rotavírus Humano",
                "doses": 2,
                "idade": "2m, 4m",
                "doencas": ["Diarreia por rotavírus"],
                "via": "Oral",
            },
            {
                "sigla": "MeningoC",
                "nome": "Meningocócica C",
                "doses": 3,
                "idade": "3m, 5m + reforço 12m",
                "doencas": ["Meningite meningocócica C"],
                "via": "Intramuscular",
            },
            {
                "sigla": "FA",
                "nome": "Febre Amarela",
                "doses": 1,
                "idade": "9m",
                "doencas": ["Febre amarela"],
                "via": "Subcutânea",
            },
            {
                "sigla": "TV",
                "nome": "Tríplice Viral (SCR)",
                "doses": 2,
                "idade": "12m, 15m",
                "doencas": ["Sarampo", "Caxumba", "Rubéola"],
                "via": "Subcutânea",
            },
            {
                "sigla": "HepA",
                "nome": "Hepatite A",
                "doses": 1,
                "idade": "15m",
                "doencas": ["Hepatite A"],
                "via": "Intramuscular",
            },
            {
                "sigla": "DTP",
                "nome": "Tríplice Bacteriana",
                "doses": 2,
                "idade": "15m, 4 anos (reforços)",
                "doencas": ["Difteria", "Tétano", "Coqueluche"],
                "via": "Intramuscular",
            },
            {
                "sigla": "Varicela",
                "nome": "Varicela",
                "doses": 1,
                "idade": "4 anos (tetra viral)",
                "doencas": ["Varicela (catapora)"],
                "via": "Subcutânea",
            },
        ],
    },
    "adolescente": {
        "nome": "Vacinas do Adolescente",
        "vacinas": [
            {
                "sigla": "HPV4",
                "nome": "HPV Quadrivalente",
                "doses": 2,
                "idade": "9-14 anos",
                "doencas": ["HPV (câncer de colo de útero, verrugas genitais)"],
                "via": "Intramuscular",
            },
            {
                "sigla": "MeningoACWY",
                "nome": "Meningocócica ACWY",
                "doses": 1,
                "idade": "11-12 anos",
                "doencas": ["Meningite meningocócica A, C, W, Y"],
                "via": "Intramuscular",
            },
            {
                "sigla": "dT",
                "nome": "Dupla Adulto (dT)",
                "doses": 3,
                "idade": "A partir de 7 anos + reforço 10/10 anos",
                "doencas": ["Difteria", "Tétano"],
                "via": "Intramuscular",
            },
        ],
    },
    "adulto_idoso": {
        "nome": "Vacinas do Adulto e Idoso",
        "vacinas": [
            {
                "sigla": "dT",
                "nome": "Dupla Adulto (dT)",
                "doses": 0,
                "idade": "Reforço a cada 10 anos",
                "doencas": ["Difteria", "Tétano"],
                "via": "Intramuscular",
            },
            {
                "sigla": "Influenza",
                "nome": "Influenza (gripe)",
                "doses": 1,
                "idade": "Anual — 60+ e grupos prioritários",
                "doencas": ["Influenza (gripe)"],
                "via": "Intramuscular",
            },
            {
                "sigla": "Pneumo23",
                "nome": "Pneumocócica 23-valente",
                "doses": 1,
                "idade": "60+ anos",
                "doencas": ["Pneumonia", "Meningite pneumocócica"],
                "via": "Intramuscular",
            },
            {
                "sigla": "Covid-19",
                "nome": "Covid-19",
                "doses": 0,
                "idade": "Conforme campanha vigente",
                "doencas": ["Covid-19"],
                "via": "Intramuscular",
            },
        ],
    },
    "gestante": {
        "nome": "Vacinas da Gestante",
        "vacinas": [
            {
                "sigla": "dTpa",
                "nome": "Tríplice Bacteriana Acelular",
                "doses": 1,
                "idade": "A partir da 20ª semana de gestação",
                "doencas": ["Difteria", "Tétano", "Coqueluche"],
                "via": "Intramuscular",
            },
            {
                "sigla": "Influenza",
                "nome": "Influenza",
                "doses": 1,
                "idade": "Durante a campanha",
                "doencas": ["Influenza (gripe)"],
                "via": "Intramuscular",
            },
            {
                "sigla": "Covid-19",
                "nome": "Covid-19",
                "doses": 0,
                "idade": "Conforme recomendação vigente",
                "doencas": ["Covid-19"],
                "via": "Intramuscular",
            },
        ],
    },
}

# Faixas etárias padrão do PNI
FAIXAS_ETARIAS_PNI: list[str] = [
    "Menor de 1 ano",
    "1 ano",
    "2 anos",
    "3 anos",
    "4 anos",
    "5 a 6 anos",
    "7 a 14 anos",
    "15 a 19 anos",
    "20 a 59 anos",
    "60 ou mais",
]

# Metas de cobertura vacinal (Ministério da Saúde, %)
METAS_COBERTURA: dict[str, float] = {
    "BCG": 90.0,
    "Hepatite B": 95.0,
    "Poliomielite": 95.0,
    "Pentavalente": 95.0,
    "Pneumocócica 10-valente": 95.0,
    "Rotavírus Humano": 90.0,
    "Meningocócica C": 95.0,
    "Febre Amarela": 95.0,
    "Tríplice Viral (SCR)": 95.0,
    "Hepatite A": 95.0,
    "Varicela": 80.0,
    "HPV Quadrivalente": 80.0,
    "Influenza (gripe)": 90.0,
}

# Esquema vacinal por faixa de idade (anos completos)
# Mapeia idade -> lista de siglas que devem estar completas
ESQUEMA_POR_IDADE: dict[str, list[str]] = {
    "0": ["BCG", "HepB"],
    "1": ["BCG", "HepB", "Penta", "VIP/VOP", "Pneumo10", "Rotavírus", "MeningoC", "FA", "TV"],
    "2": [
        "BCG",
        "HepB",
        "Penta",
        "VIP/VOP",
        "Pneumo10",
        "Rotavírus",
        "MeningoC",
        "FA",
        "TV",
        "HepA",
        "DTP",
    ],
    "4": [
        "BCG",
        "HepB",
        "Penta",
        "VIP/VOP",
        "Pneumo10",
        "Rotavírus",
        "MeningoC",
        "FA",
        "TV",
        "HepA",
        "DTP",
        "Varicela",
    ],
    "9": [
        "BCG",
        "HepB",
        "Penta",
        "VIP/VOP",
        "Pneumo10",
        "Rotavírus",
        "MeningoC",
        "FA",
        "TV",
        "HepA",
        "DTP",
        "Varicela",
        "HPV4",
    ],
    "11": [
        "BCG",
        "HepB",
        "Penta",
        "VIP/VOP",
        "Pneumo10",
        "Rotavírus",
        "MeningoC",
        "FA",
        "TV",
        "HepA",
        "DTP",
        "Varicela",
        "HPV4",
        "MeningoACWY",
    ],
    "15": [
        "BCG",
        "HepB",
        "Penta",
        "VIP/VOP",
        "Pneumo10",
        "Rotavírus",
        "MeningoC",
        "FA",
        "TV",
        "HepA",
        "DTP",
        "Varicela",
        "HPV4",
        "MeningoACWY",
        "dT",
    ],
    "60": ["dT", "Influenza", "Pneumo23", "Covid-19"],
}
