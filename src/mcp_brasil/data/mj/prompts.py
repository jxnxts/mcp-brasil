"""Prompts for MJ."""

from __future__ import annotations


def analise_criminalidade_nacional() -> str:
    """Análise nacional de criminalidade via SINESP."""
    return (
        "Analise criminalidade no Brasil via SINESP.\n\n"
        "1. buscar_datasets_mj('sinesp') para achar o package\n"
        "2. detalhe_dataset_mj(package_id) para URLs dos CSVs\n"
        "3. Baixe e agregue por UF, tipo criminal e ano\n\n"
        "Apresente: ranking de UFs mais violentas, tendência histórica, crimes com maior evolução."
    )


def analise_sistema_prisional() -> str:
    """Análise do sistema prisional via INFOPEN/SISDEPEN."""
    return (
        "Analise o sistema prisional brasileiro via INFOPEN.\n\n"
        "1. buscar_datasets_mj('infopen') ou buscar_datasets_mj('prisional')\n"
        "2. detalhe_dataset_mj(package_id)\n"
        "3. Baixe XLSX/CSV e analise capacidade vs. população, déficit, perfil dos presos\n\n"
        "Apresente: taxa de ocupação por UF, déficit nacional, composição demográfica."
    )
