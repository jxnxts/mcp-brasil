"""Prompts for noticias."""

from __future__ import annotations


def panorama_dia() -> str:
    """Panorama das principais notícias do dia (política + economia)."""
    return (
        "Dê um panorama das principais notícias brasileiras hoje.\n\n"
        "1. resumo_politica(limite_por_fonte=5) — Câmara, Senado, Agência Brasil\n"
        "2. ultimas_noticias('agencia_brasil_economia', limite=8)\n"
        "3. ultimas_noticias('bcb_noticias', limite=5)\n\n"
        "Sintetize destaques de política, economia e mercado em 3-5 bullets."
    )
