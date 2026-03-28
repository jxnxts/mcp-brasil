"""Analysis prompts for the OpenDataSUS feature.

Prompts are reusable templates that guide LLM interactions.
They instruct the LLM on which tools to call and how to analyze the data.
"""

from __future__ import annotations


def pesquisa_epidemiologica(tema: str) -> str:
    """Assistente para pesquisa epidemiológica usando dados do OpenDataSUS.

    Orienta o LLM a buscar datasets relevantes, detalhar seus recursos
    e consultar registros para análise.

    Args:
        tema: Tema de pesquisa (ex: "vacinação covid", "srag", "dengue").
    """
    return (
        f"Atue como um pesquisador de saúde pública usando dados do OpenDataSUS "
        f"para investigar '{tema}'.\n\n"
        "Passos:\n"
        f"1. Use buscar_datasets(query='{tema}') para encontrar datasets relevantes\n"
        "2. Use detalhar_dataset(dataset_id=...) para ver os recursos disponíveis\n"
        "3. Se o dataset tiver DataStore, use consultar_datastore(resource_id=...) "
        "para acessar os registros\n"
        "4. Use buscar_com_filtro para filtrar por UF, município ou ano\n\n"
        "Apresente:\n"
        "- Datasets encontrados com título e descrição\n"
        "- Recursos disponíveis (CSV, JSON, API) com links\n"
        "- Amostra de dados se DataStore estiver ativo\n"
        "- Orientações sobre como analisar os dados"
    )
