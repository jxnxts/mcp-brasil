"""Analysis prompts for tse_candidatos."""

from __future__ import annotations


def analise_partido_2024(partido: str) -> str:
    """Análise do desempenho eleitoral de um partido em 2024.

    Args:
        partido: Sigla do partido (ex: 'PT', 'PL', 'MDB').
    """
    return (
        f"Analise o desempenho do partido {partido} nas eleições municipais 2024:\n\n"
        f"1. `buscar_candidatos(partido='{partido}', situacao_turno='ELEITO', limite=100)` "
        "— lista os eleitos.\n"
        f"2. Distribuição por cargo: compare com `resumo_cargo_partido('PREFEITO')` e "
        "`resumo_cargo_partido('VEREADOR')`.\n"
        f"3. Perfil demográfico: `resumo_perfil_eleitos('PREFEITO')` e destacar a fatia "
        f"de {partido}.\n"
        "4. Destaque (a) total de prefeitos eleitos; (b) vereadores eleitos; "
        "(c) UFs onde o partido foi mais forte; (d) comparação com adversários."
    )


def perfil_demografico_cargo(cargo: str = "PREFEITO") -> str:
    """Perfil demográfico dos eleitos para um cargo.

    Args:
        cargo: 'PREFEITO', 'VICE-PREFEITO' ou 'VEREADOR'.
    """
    return (
        f"Monte um perfil demográfico dos eleitos para {cargo} em 2024:\n\n"
        f"1. `resumo_perfil_eleitos('{cargo}')` — três tabelas (gênero, raça, escolaridade).\n"
        "2. Comente a representatividade: proporção de mulheres, de negros/pardos, "
        "grau de instrução modal.\n"
        "3. Compare com a participação geral de candidatos (use "
        "`valores_distintos_candidatos('ds_genero')`) e identifique gaps entre "
        "candidaturas e eleitos."
    )
