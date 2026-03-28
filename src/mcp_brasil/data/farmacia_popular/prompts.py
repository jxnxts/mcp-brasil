"""Analysis prompts for the Farmácia Popular feature.

Prompts are reusable templates that guide LLM interactions.
They instruct the LLM on which tools to call and how to analyze the data.

In Claude Desktop, prompts appear as selectable options (similar to slash commands).
"""

from __future__ import annotations


def assistente_farmacia_popular(indicacao: str) -> str:
    """Assistente para encontrar medicamentos gratuitos e farmácias próximas.

    Orienta o LLM a consultar medicamentos gratuitos para uma condição
    e encontrar farmácias credenciadas para retirada.

    Args:
        indicacao: Condição de saúde (ex: "hipertensão", "diabetes", "asma").
    """
    return (
        f"Atue como um assistente de saúde para ajudar a encontrar medicamentos "
        f"gratuitos para '{indicacao}' no Programa Farmácia Popular.\n\n"
        "Passos:\n"
        f"1. Use buscar_por_indicacao(indicacao='{indicacao}') para listar "
        "os medicamentos gratuitos disponíveis\n"
        "2. Use verificar_elegibilidade() para informar os requisitos de retirada\n"
        "3. Pergunte ao usuário seu município ou UF para buscar farmácias\n"
        "4. Use buscar_farmacias(codigo_municipio=...) para encontrar farmácias próximas\n\n"
        "Apresente:\n"
        "- Lista de medicamentos gratuitos para a condição\n"
        "- Documentos necessários para retirada\n"
        "- Farmácias mais próximas do usuário\n"
        "- Orientações sobre validade da receita e quantidade dispensada"
    )
