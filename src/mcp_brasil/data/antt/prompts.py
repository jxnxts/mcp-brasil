"""Prompts for ANTT."""

from __future__ import annotations


def analise_acidentes_rodovias() -> str:
    """Análise de acidentes em rodovias federais concedidas."""
    return (
        "Analise acidentes em rodovias concedidas da ANTT.\n\n"
        "1. buscar_datasets_antt('acidente') para achar o package atualizado\n"
        "2. detalhe_dataset_antt(package_id) para obter URL do CSV\n"
        "3. Baixe e agregue por concessionária, UF e tipo\n\n"
        "Apresente: top rodovias mais perigosas, tendência anual, fatalidades."
    )
