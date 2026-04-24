"""Prompts for governadores."""

from __future__ import annotations


def panorama_executivo_estadual() -> str:
    """Panorama do executivo estadual brasileiro."""
    return (
        "Dê um panorama do executivo estadual brasileiro.\n\n"
        "1. resumo_por_partido() — distribuição partidária\n"
        "2. listar_governadores() — lista completa com mandatos\n\n"
        "Apresente: partido com mais governadores, anos de eleição, próximas sucessões."
    )
