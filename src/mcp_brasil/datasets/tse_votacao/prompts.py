"""Analysis prompts for tse_votacao."""

from __future__ import annotations


def evolucao_partido_cargo(partido: str, cargo: str = "DEPUTADO FEDERAL") -> str:
    """Analisa a evolução eleitoral de um partido num cargo.

    Args:
        partido: Sigla.
        cargo: Cargo comparável cross-year.
    """
    return (
        f"Análise a evolução do partido {partido} para {cargo} nos últimos 10 anos:\n\n"
        f"1. `evolucao_partido('{partido}', '{cargo}')` — série histórica ano a ano.\n"
        "2. Identifique o ciclo de maior votação + compare com eleições municipais "
        "(use `ranking_anual_eleitos` em tse_candidatos).\n"
        f"3. Para o ano com pior performance, descubra quais UFs mais prejudicaram — "
        f"use `soma_votos_uf(ano=X, cargo='{cargo}')` e compare com total do partido.\n"
        "4. Reporte: ciclo de alta, ciclo de baixa, tendência (crescimento ou declínio)."
    )


def briefing_municipio(municipio: str, uf: str) -> str:
    """Briefing eleitoral histórico de um município.

    Args:
        municipio: Nome do município.
        uf: UF.
    """
    return (
        f"Monte um briefing eleitoral histórico para {municipio}/{uf}:\n\n"
        f"1. Prefeitos desde 2016: `ranking_municipio('{municipio}', '{uf}', "
        "'PREFEITO', ano=X)` para cada ano 2016/2020/2024.\n"
        f"2. Vereadores mais votados em 2024: `ranking_municipio('{municipio}', "
        f"'{uf}', 'VEREADOR', ano=2024, limite=20)`.\n"
        "3. Se houver deputados federais eleitos citados na imprensa local, use "
        "`votos_candidato(sq_candidato=X)` para ver a geografia do voto.\n"
        "4. Sintetize: alternância partidária, principais famílias políticas, "
        "partido dominante."
    )
