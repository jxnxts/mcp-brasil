"""Constants for MJ feature."""

from __future__ import annotations

MJ_CKAN_BASE = "https://dados.mj.gov.br/api/3/action"

DATASETS_CHAVE: dict[str, str] = {
    "sistema-nacional-de-estatisticas-de-seguranca-publica": (
        "SINESP VDE — ocorrências criminais agregadas por UF (homicídios, roubos, etc.)"
    ),
    "infopen-levantamento-nacional-de-informacoes-penitenciarias": (
        "INFOPEN/SISDEPEN — sistema prisional, capacidade, população carcerária"
    ),
    "cadastro-nacional-de-reclamacoes-fundamentadas-procons-sindec": (
        "PROCONs/Sindec — reclamações fundamentadas por empresa/assunto"
    ),
    "atendimentos-de-consumidores-nos-procons-sindec": (
        "PROCONs/Sindec — todos atendimentos registrados"
    ),
    "registros-de-armas-de-fogo": "Registros de armas de fogo (Polícia Federal)",
    "boletim-epidemiologico-do-consumo-de-drogas": "Boletim epidemiológico — drogas",
}
