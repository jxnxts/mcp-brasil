"""Analysis prompts for tse_bens."""

from __future__ import annotations


def comparar_patrimonio_cargo(cargo: str = "PREFEITO", uf: str = "SP") -> str:
    """Investiga concentração de patrimônio entre candidatos de um cargo/UF.

    Args:
        cargo: Cargo alvo.
        uf: UF opcional.
    """
    return (
        f"Investigue concentração patrimonial entre candidatos a {cargo} em {uf}:\n\n"
        f"1. `top_patrimonios_cargo('{cargo}', uf='{uf}', limite=20)` — rank.\n"
        f"2. `resumo_patrimonio_partido('{cargo}')` — partido vs patrimônio.\n"
        "3. `resumo_tipos_bens(top=15)` — mix de categorias (imóvel vs financeiro).\n"
        "4. Para o candidato #1: `buscar_bens_candidato(sq_candidato=...)` para o "
        "detalhamento.\n"
        "5. Comente disparidade: mediana vs top 5, e se algum tipo de bem "
        "concentra anomalia (ex: criptomoeda, cotas empresariais)."
    )
