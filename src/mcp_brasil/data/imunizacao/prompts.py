"""Prompt templates for the Imunização (PNI) feature."""

from __future__ import annotations


async def analise_cobertura_vacinal(municipio: str) -> str:
    """Gera instruções para análise de cobertura vacinal de um município.

    Args:
        municipio: Nome do município ou código IBGE.
    """
    return (
        f"Você é um analista de saúde pública especializado em imunização.\n\n"
        f"Analise a situação vacinal do município **{municipio}** seguindo estes passos:\n\n"
        "1. Use `estatisticas_por_vacina` para ver o total de doses por vacina\n"
        "2. Use `metas_cobertura` para consultar as metas do Ministério da Saúde\n"
        "3. Use `buscar_vacinacao` para ver registros recentes\n"
        "4. Use `buscar_datasets_pni` para encontrar datasets com dados detalhados\n\n"
        "Na análise, destaque:\n"
        "- Vacinas com cobertura abaixo da meta\n"
        "- Risco de surtos de doenças prevenidas por vacinação\n"
        "- Comparação com médias estaduais/nacionais quando disponível\n"
        "- Recomendações práticas para gestores de saúde\n\n"
        "Use linguagem acessível e cite as fontes (PNI/DataSUS)."
    )
