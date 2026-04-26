"""Constants for the DENASUS feature.

DENASUS — Departamento Nacional de Auditoria do SUS.
Source: gov.br/saude/pt-br/composicao/denasus (public pages, Plone CMS).
"""

BASE_URL = "https://www.gov.br/saude/pt-br/composicao/denasus"

ATIVIDADES_URL = f"{BASE_URL}/criacao-de-atividades-de-auditoria"
RELATORIOS_URL = f"{BASE_URL}/relatorio-anual-de-auditoria"
PLANOS_URL = f"{BASE_URL}/planos-anuais-de-auditoria-interna"

# Portal de consulta de auditorias do SUS (sistema externo)
CONSULTA_AUDITORIA_URL = "https://consultaauditoria.saude.gov.br"

RATE_LIMIT_DELAY = 3.0  # seconds between scraping requests

USER_AGENT = "mcp-brasil/0.6 (+https://github.com/Mcp-Brasil/mcp-brasil)"

HEADERS: dict[str, str] = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml",
}

# Brazilian states (UFs) for extraction from titles
UFS_BRASIL: set[str] = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}

# Audit activity types
TIPOS_ATIVIDADE: list[str] = [
    "Auditoria",
    "Verificação",
    "Monitoramento",
    "Inspeção",
    "Outro",
]

# Information about the DENASUS / SNA
INFO_SNA: dict[str, str] = {
    "nome": "Sistema Nacional de Auditoria do SUS (SNA)",
    "orgao": "Departamento Nacional de Auditoria do SUS (DENASUS)",
    "vinculacao": "Secretaria de Gestão Estratégica e Participativa (SGEP) / Ministério da Saúde",
    "base_legal": "Lei nº 8.080/1990 (Art. 33) e Decreto nº 1.651/1995",
    "competencia": (
        "Avaliação técnico-científica, contábil, financeira e patrimonial do SUS, "
        "realizada de forma descentralizada. Controle da regularidade dos procedimentos "
        "praticados por pessoas naturais e jurídicas mediante exame analítico e pericial."
    ),
    "componentes": (
        "Federal (DENASUS), Estadual (Componentes Estaduais de Auditoria), "
        "Municipal (Componentes Municipais de Auditoria)"
    ),
    "portal": "https://www.gov.br/saude/pt-br/composicao/denasus",
    "contato": "denasus@saude.gov.br",
}
