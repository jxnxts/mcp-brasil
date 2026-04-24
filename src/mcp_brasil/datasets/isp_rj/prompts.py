"""Prompts for isp_rj."""

from __future__ import annotations


def panorama_criminalidade_rj(ano: int = 2024) -> str:
    """Panorama da criminalidade no RJ em um ano."""
    return (
        f"Faça um panorama da criminalidade no RJ em {ano}.\n\n"
        f"1. indicadores_municipio('Rio de Janeiro', {ano}) — capital\n"
        f"2. ranking_municipios('hom_doloso', {ano}, limite=10) — cidades mais violentas\n"
        f"3. ranking_municipios('feminicidio', {ano}, limite=10)\n"
        f"4. serie_temporal('letalidade_violenta', ano_inicio={ano - 4})\n\n"
        "Destaque tendências, municípios críticos e evolução recente."
    )
