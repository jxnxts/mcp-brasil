"""Constants for ANTT feature."""

from __future__ import annotations

ANTT_CKAN_BASE = "https://dados.antt.gov.br/api/3/action"

DATASETS_CHAVE: dict[str, str] = {
    "acidentes-rodovias": "Acidentes em rodovias federais concedidas",
    "acidentes-quilometro-rodovias": "Acidentes por quilômetro de rodovia",
    "acessos-das-rodovias-concedidas": "Acessos (entradas/saídas) das rodovias concedidas",
    "transporte-rodoviario-de-cargas": "RNTRC — transportadoras autônomas e empresas de carga",
    "alcas": "Alças de rodovias concedidas",
    "area-escape": "Áreas de escape em rodovias",
    "atendimento-medico-mecanico": "Atendimento médico/mecânico nas rodovias",
    "pracas-de-pedagio": "Praças de pedágio das rodovias concedidas",
    "tarifas-de-pedagio": "Tarifas de pedágio históricas",
    "frota-rntrc": "Frota do Registro Nacional de Transportadores",
}
