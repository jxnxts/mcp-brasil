"""Constants for governadores."""

from __future__ import annotations

GOV_JSON_URL = (
    "https://raw.githubusercontent.com/GusFurtado/dab_assets/main/data/governadores.json"
)

UF_NOME: dict[str, str] = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AM": "Amazonas",
    "AP": "Amapá",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SP": "São Paulo",
    "SC": "Santa Catarina",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

NOME_UF: dict[str, str] = {v: k for k, v in UF_NOME.items()}
