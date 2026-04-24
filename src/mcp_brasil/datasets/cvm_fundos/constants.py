"""Constants for CVM fundos dataset."""

from __future__ import annotations

CVM_CAD_URL = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"

COLUNAS_DISTINCT_PERMITIDAS: frozenset[str] = frozenset(
    {
        "TP_FUNDO",
        "SIT",
        "CLASSE",
        "CLASSE_ANBIMA",
        "CONDOM",
        "FUNDO_COTAS",
        "FUNDO_EXCLUSIVO",
        "TRIB_LPRAZO",
        "PUBLICO_ALVO",
        "ENTID_INVEST",
    }
)
