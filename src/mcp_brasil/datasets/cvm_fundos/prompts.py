"""Prompts for cvm_fundos."""

from __future__ import annotations


def panorama_fundos(classe: str = "Ações") -> str:
    """Panorama dos fundos de uma classe.

    Args:
        classe: Classe CVM (ex: 'Ações', 'Renda Fixa', 'Multimercado').
    """
    return (
        f"Faça um panorama dos fundos {classe}.\n\n"
        f"1. top_fundos_por_pl(classe='{classe}', limite=15)\n"
        f"2. Para cada top: detalhe_fundo(cnpj) para ver administrador/gestor/taxas\n"
        "3. Compare tamanhos relativos, concentração por gestora."
    )
