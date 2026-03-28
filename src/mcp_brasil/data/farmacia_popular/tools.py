"""Tool functions for the Farmácia Popular feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
    - Uses Context for structured logging and progress reporting
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import format_number_br, markdown_table

from . import client
from .constants import DOCUMENTOS_RETIRADA, INDICACOES, REGRAS_ELEGIBILIDADE


async def buscar_farmacias(
    ctx: Context,
    codigo_municipio: str | None = None,
    codigo_uf: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> str:
    """Busca farmácias credenciadas ao Programa Farmácia Popular por município ou UF.

    Retorna farmácias ativas cadastradas no CNES que podem participar do programa.
    Use o código IBGE do município ou da UF para filtrar.

    Args:
        codigo_municipio: Código IBGE do município (ex: "355030" para São Paulo).
        codigo_uf: Código IBGE do estado (ex: "35" para SP).
        limit: Número máximo de resultados (padrão: 20, máximo: 100).
        offset: Deslocamento para paginação (padrão: 0).

    Returns:
        Tabela com farmácias encontradas.
    """
    filtro = codigo_municipio or codigo_uf or "Brasil"
    await ctx.info(f"Buscando farmácias credenciadas em {filtro}...")

    resultados = await client.buscar_farmacias(
        codigo_municipio=codigo_municipio,
        codigo_uf=codigo_uf,
        limit=limit,
        offset=offset,
    )

    if not resultados:
        return "Nenhuma farmácia encontrada para os filtros informados."

    rows = [
        (
            f.codigo_cnes or "—",
            f.nome_fantasia or f.nome_razao_social or "—",
            f.endereco or "—",
            f.tipo_gestao or "—",
        )
        for f in resultados
    ]

    header = f"**Farmácias credenciadas** ({len(resultados)} resultados)\n\n"
    return header + markdown_table(["CNES", "Nome", "Endereço", "Gestão"], rows)


async def listar_medicamentos(ctx: Context) -> str:
    """Lista todos os medicamentos disponíveis no Programa Farmácia Popular.

    Retorna a lista completa de medicamentos gratuitos organizados por indicação
    terapêutica. Desde fevereiro de 2023, todos os medicamentos do programa são
    100% gratuitos.

    Returns:
        Tabela com todos os medicamentos do programa.
    """
    await ctx.info("Listando medicamentos do Farmácia Popular...")

    medicamentos = client.listar_medicamentos()

    rows = [
        (m.nome, m.principio_ativo, m.apresentacao, m.indicacao, "Sim" if m.gratuito else "Não")
        for m in medicamentos
    ]

    header = (
        f"**Medicamentos do Farmácia Popular** ({len(medicamentos)} itens)\n"
        "Todos os medicamentos são 100% gratuitos desde fevereiro de 2023.\n\n"
    )
    return header + markdown_table(
        ["Nome", "Princípio Ativo", "Apresentação", "Indicação", "Gratuito"], rows
    )


async def verificar_medicamento(ctx: Context, nome: str) -> str:
    """Verifica se um medicamento está disponível no Programa Farmácia Popular.

    Busca pelo nome comercial ou princípio ativo. Se encontrado, mostra detalhes
    como apresentação, indicação terapêutica e se é gratuito.

    Args:
        nome: Nome do medicamento ou princípio ativo (ex: "losartana", "metformina").

    Returns:
        Informações do medicamento ou aviso de que não está na lista.
    """
    await ctx.info(f"Verificando '{nome}' no Farmácia Popular...")

    resultados = client.buscar_medicamento_por_nome(nome)

    if not resultados:
        return (
            f"O medicamento '{nome}' **não foi encontrado** na lista do "
            "Programa Farmácia Popular. Isso não significa que não existe — "
            "apenas que não está coberto pelo programa."
        )

    rows = [
        (m.nome, m.principio_ativo, m.apresentacao, m.indicacao, "Sim" if m.gratuito else "Não")
        for m in resultados
    ]

    header = f"**Medicamento encontrado no Farmácia Popular** ({len(resultados)} resultado(s))\n\n"
    return header + markdown_table(
        ["Nome", "Princípio Ativo", "Apresentação", "Indicação", "Gratuito"], rows
    )


async def buscar_por_indicacao(ctx: Context, indicacao: str) -> str:
    """Busca medicamentos gratuitos por indicação terapêutica (doença/condição).

    Exemplos de indicações: "hipertensão", "diabetes", "asma", "glaucoma",
    "contracepção", "osteoporose", "parkinson", "rinite", "dislipidemia".

    Args:
        indicacao: Nome da doença ou condição (ex: "diabetes", "hipertensão").

    Returns:
        Tabela com medicamentos gratuitos para a indicação informada.
    """
    await ctx.info(f"Buscando medicamentos para '{indicacao}'...")

    resultados = client.buscar_por_indicacao(indicacao)

    if not resultados:
        indicacoes_str = ", ".join(INDICACOES)
        return (
            f"Nenhum medicamento encontrado para '{indicacao}'. "
            f"Indicações disponíveis: {indicacoes_str}."
        )

    rows = [
        (m.nome, m.principio_ativo, m.apresentacao, "Sim" if m.gratuito else "Não")
        for m in resultados
    ]

    header = (
        f"**Medicamentos para {resultados[0].indicacao}** "
        f"({len(resultados)} medicamento(s)) — todos gratuitos\n\n"
    )
    return header + markdown_table(["Nome", "Princípio Ativo", "Apresentação", "Gratuito"], rows)


async def estatisticas_programa(ctx: Context) -> str:
    """Retorna estatísticas consolidadas do Programa Farmácia Popular.

    Mostra o total de medicamentos, indicações terapêuticas cobertas e
    a distribuição de medicamentos por indicação.

    Returns:
        Resumo estatístico do programa.
    """
    await ctx.info("Calculando estatísticas do Farmácia Popular...")

    stats = client.obter_estatisticas()

    lines = [
        "**Estatísticas do Programa Farmácia Popular**\n",
        f"- **Total de medicamentos:** {format_number_br(float(stats.total_medicamentos), 0)}",
        f"- **Indicações cobertas:** {format_number_br(float(stats.total_indicacoes), 0)}",
        f"- **Todos gratuitos:** {'Sim' if stats.todos_gratuitos else 'Não'}",
        "",
        "**Medicamentos por indicação:**\n",
    ]

    tipo_rows = [
        (ind, str(stats.medicamentos_por_indicacao.get(ind, 0))) for ind in stats.indicacoes
    ]
    lines.append(markdown_table(["Indicação", "Medicamentos"], tipo_rows))

    return "\n".join(lines)


async def verificar_elegibilidade(ctx: Context) -> str:
    """Informa os requisitos para retirar medicamentos no Farmácia Popular.

    Retorna os documentos necessários, regras de elegibilidade e informações
    sobre validade da receita. Útil para orientar cidadãos sobre como acessar
    o programa.

    Returns:
        Informações sobre elegibilidade e documentação necessária.
    """
    await ctx.info("Consultando requisitos de elegibilidade...")

    docs_list = "\n".join(f"- {doc}" for doc in DOCUMENTOS_RETIRADA)

    return (
        "**Requisitos para retirada no Farmácia Popular**\n\n"
        f"{REGRAS_ELEGIBILIDADE}\n\n"
        "**Documentos necessários:**\n"
        f"{docs_list}\n\n"
        "**Observações importantes:**\n"
        "- A receita pode ser do SUS ou de médico particular\n"
        "- Validade da receita: 120 dias a partir da data de emissão\n"
        "- Quantidade dispensada conforme prescrição médica\n"
        "- Programa disponível em farmácias credenciadas em todo o Brasil"
    )
