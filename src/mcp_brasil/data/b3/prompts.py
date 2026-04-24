"""Prompts for B3."""

from __future__ import annotations


def panorama_bolsa() -> str:
    """Panorama da bolsa brasileira no dia."""
    return (
        "Dê um panorama da bolsa brasileira hoje.\n\n"
        "1. indices_b3() — principais índices\n"
        "2. blue_chips() — cotações das blue chips\n"
        "3. top_ativos_volume('stock', 10) — mais negociadas\n\n"
        "Apresente: direção do dia (Ibovespa), destaques positivos/negativos, "
        "observações sobre setores (via ativos específicos)."
    )
