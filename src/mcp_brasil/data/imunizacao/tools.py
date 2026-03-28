"""Tool functions for the Imunização (PNI) feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
    - Uses Context for structured logging and progress reporting
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import format_number_br, markdown_table

from . import client
from .constants import (
    ESQUEMA_POR_IDADE,
    GRUPOS_IMUNOBIOLOGICOS,
    METAS_COBERTURA,
)

# ---------------------------------------------------------------------------
# Group 1 — Elasticsearch (vaccination records)
# ---------------------------------------------------------------------------


async def buscar_vacinacao(
    ctx: Context,
    uf: str | None = None,
    municipio: str | None = None,
    vacina: str | None = None,
    dose: str | None = None,
    limite: int = 20,
) -> str:
    """Busca registros individuais de vacinação no Elasticsearch público do PNI.

    Acessa o índice público de imunização do Ministério da Saúde com dados
    anonimizados de vacinação (principalmente Covid-19 e rotina).

    Args:
        uf: Sigla da UF (ex: "SP", "PI"). Opcional.
        municipio: Nome do município. Opcional.
        vacina: Nome da vacina (ex: "Covid-19", "Influenza"). Opcional.
        dose: Descrição da dose (ex: "1ª Dose", "Reforço"). Opcional.
        limite: Número máximo de registros (padrão: 20).

    Returns:
        Tabela com registros de vacinação encontrados.
    """
    filtro = uf or municipio or vacina or "Brasil"
    await ctx.info(f"Buscando registros de vacinação: {filtro}...")

    records, total = await client.buscar_vacinacao_es(
        uf=uf,
        municipio=municipio,
        vacina=vacina,
        dose=dose,
        limit=limite,
    )

    if not records:
        return (
            "Nenhum registro de vacinação encontrado para os filtros informados. "
            "Tente buscar por UF (ex: 'SP') ou vacina (ex: 'Covid-19')."
        )

    rows = [
        (
            r.vacina_nome or "—",
            r.dose or "—",
            r.municipio or "—",
            r.uf or "—",
            (r.data_aplicacao or "—")[:10],
            r.fabricante or "—",
        )
        for r in records
    ]

    header = (
        f"**Registros de vacinação** ({len(records)} de "
        f"{format_number_br(float(total), 0)} registros)\n\n"
    )
    return header + markdown_table(
        ["Vacina", "Dose", "Município", "UF", "Data", "Fabricante"], rows
    )


async def estatisticas_por_vacina(
    ctx: Context,
    uf: str | None = None,
    municipio_ibge: str | None = None,
) -> str:
    """Estatísticas de doses aplicadas por tipo de vacina em uma localidade.

    Usa agregação do Elasticsearch para contar doses por vacina.
    Filtros por UF e/ou código IBGE do município.

    Args:
        uf: Sigla da UF (ex: "SP", "RJ"). Opcional.
        municipio_ibge: Código IBGE do município (ex: "220040"). Opcional.

    Returns:
        Tabela com total de doses por vacina.
    """
    filtro = uf or municipio_ibge or "Brasil"
    await ctx.info(f"Calculando estatísticas por vacina: {filtro}...")

    resultados = await client.agregar_vacinacao_es(
        uf=uf,
        municipio_ibge=municipio_ibge,
        campo_agregacao="vacina_nome.keyword",
    )

    if not resultados:
        return "Nenhuma estatística disponível para os filtros informados."

    rows = [
        (r.nome, format_number_br(float(r.total), 0))
        for r in sorted(resultados, key=lambda x: -x.total)
    ]

    total = sum(r.total for r in resultados)
    header = (
        f"**Doses aplicadas por vacina** — {filtro} "
        f"(total: {format_number_br(float(total), 0)})\n\n"
    )
    return header + markdown_table(["Vacina", "Doses Aplicadas"], rows)


async def estatisticas_por_faixa_etaria(
    ctx: Context,
    uf: str | None = None,
    municipio_ibge: str | None = None,
) -> str:
    """Estatísticas de vacinação por faixa etária em uma localidade.

    Agrega registros de vacinação pelo sexo biológico do paciente
    como proxy para distribuição demográfica.

    Args:
        uf: Sigla da UF (ex: "SP"). Opcional.
        municipio_ibge: Código IBGE do município. Opcional.

    Returns:
        Tabela com total de doses por faixa etária.
    """
    filtro = uf or municipio_ibge or "Brasil"
    await ctx.info(f"Calculando estatísticas por faixa etária: {filtro}...")

    resultados = await client.agregar_vacinacao_es(
        uf=uf,
        municipio_ibge=municipio_ibge,
        campo_agregacao="paciente_enumSexoBiologico.keyword",
    )

    if not resultados:
        return "Nenhuma estatística disponível para os filtros informados."

    rows = [
        (r.nome, format_number_br(float(r.total), 0))
        for r in sorted(resultados, key=lambda x: -x.total)
    ]

    total = sum(r.total for r in resultados)
    header = (
        f"**Vacinação por sexo biológico** — {filtro} "
        f"(total: {format_number_br(float(total), 0)})\n\n"
    )
    return header + markdown_table(["Sexo", "Doses"], rows)


# ---------------------------------------------------------------------------
# Group 2 — CKAN (OpenDataSUS PNI datasets)
# ---------------------------------------------------------------------------


async def buscar_datasets_pni(
    ctx: Context,
    query: str = "imunização PNI",
    limite: int = 10,
) -> str:
    """Busca datasets do Programa Nacional de Imunizações no OpenDataSUS.

    Pesquisa no portal CKAN por datasets de vacinação, doses aplicadas,
    cobertura vacinal e outros dados do PNI.

    Args:
        query: Palavra-chave (ex: "imunização", "doses aplicadas", "PNI").
        limite: Número máximo de resultados (padrão: 10).

    Returns:
        Tabela com datasets encontrados.
    """
    await ctx.info(f"Buscando datasets PNI: '{query}'...")

    datasets, total = await client.buscar_datasets_pni(query=query, limite=limite)

    if not datasets:
        return (
            f"Nenhum dataset PNI encontrado para '{query}'. "
            "Tente: 'imunização', 'doses aplicadas', 'vacina', 'PNI'."
        )

    rows = [
        (
            d.nome,
            (d.titulo or "—")[:50],
            d.organizacao or "—",
            str(d.total_recursos),
            (d.data_atualizacao or "—")[:10],
        )
        for d in datasets
    ]

    header = f"**Datasets PNI** ({len(datasets)} de {total} resultados)\n\n"
    return header + markdown_table(
        ["ID/Nome", "Título", "Organização", "Recursos", "Atualização"], rows
    )


async def consultar_doses_dataset(
    ctx: Context,
    dataset_id: str,
    query: str | None = None,
    limite: int = 20,
) -> str:
    """Consulta dados de um dataset PNI específico no OpenDataSUS.

    Primeiro obtém os recursos do dataset, depois consulta o DataStore
    do primeiro recurso disponível.

    Args:
        dataset_id: Nome (slug) do dataset PNI (ex: do output de buscar_datasets_pni).
        query: Busca textual nos registros. Opcional.
        limite: Número máximo de registros (padrão: 20).

    Returns:
        Tabela com registros do dataset.
    """
    await ctx.info(f"Consultando dataset '{dataset_id}'...")

    ds, recursos = await client.detalhar_dataset_pni(dataset_id)

    if not ds or not recursos:
        return (
            f"Dataset '{dataset_id}' não encontrado ou sem recursos. "
            "Use buscar_datasets_pni() para listar datasets disponíveis."
        )

    resource_id = recursos[0].id
    records, total = await client.consultar_datastore_pni(
        resource_id=resource_id,
        query=query,
        limite=limite,
    )

    if not records:
        return f"Nenhum registro encontrado no dataset '{ds.titulo or ds.nome}'."

    cols = list(records[0].keys())[:8]
    data_rows = [tuple(str(r.get(c, "—"))[:40] for c in cols) for r in records[:50]]

    header = f"**{ds.titulo or ds.nome}** — {len(records)} registros (total: {total})\n\n"
    return header + markdown_table(cols, data_rows)


# ---------------------------------------------------------------------------
# Group 3 — Static reference (vaccination calendar)
# ---------------------------------------------------------------------------


async def calendario_vacinacao(ctx: Context) -> str:
    """Retorna o Calendário Nacional de Vacinação do SUS completo.

    Mostra todas as vacinas organizadas por grupo (criança, adolescente,
    adulto/idoso, gestante), com doses, idades e doenças prevenidas.

    Returns:
        Calendário completo com todas as vacinas do SUS.
    """
    await ctx.info("Consultando Calendário Nacional de Vacinação...")

    lines = ["**Calendário Nacional de Vacinação — SUS**\n"]

    for _grupo_key, grupo in GRUPOS_IMUNOBIOLOGICOS.items():
        grupo_nome = grupo["nome"]
        vacinas = grupo["vacinas"]  # type: ignore[index]
        lines.append(f"\n### {grupo_nome}\n")

        rows = [
            (
                v["sigla"],  # type: ignore[index]
                v["nome"],  # type: ignore[index]
                str(v["doses"]),  # type: ignore[index]
                v["idade"],  # type: ignore[index]
                ", ".join(v.get("doencas", [])),  # type: ignore[union-attr]
            )
            for v in vacinas  # type: ignore[union-attr]
        ]
        lines.append(markdown_table(["Sigla", "Vacina", "Doses", "Idade", "Previne"], rows))

    lines.append("\n**Fonte:** Ministério da Saúde — PNI (2024)")
    return "\n".join(lines)


async def listar_vacinas_sus(ctx: Context) -> str:
    """Lista todas as vacinas disponíveis no SUS pelo Programa Nacional de Imunizações.

    Retorna a lista completa de vacinas do calendário nacional, incluindo
    sigla, nome, número de doses e via de administração.

    Returns:
        Tabela com todas as vacinas do SUS.
    """
    await ctx.info("Listando vacinas do SUS...")

    vacinas = client.listar_todas_vacinas()

    rows = [
        (v["sigla"], v["nome"], str(v["doses"]), v.get("via", "—"), v.get("grupo", "—"))
        for v in vacinas
    ]

    header = f"**Vacinas do SUS — PNI** ({len(vacinas)} imunobiológicos)\n\n"
    return header + markdown_table(["Sigla", "Vacina", "Doses", "Via", "Grupo"], rows)


async def consultar_vacina(ctx: Context, nome: str) -> str:
    """Consulta detalhes de uma vacina específica do SUS.

    Busca por sigla (ex: "BCG", "Penta") ou nome (ex: "hepatite", "meningocócica").
    Retorna indicação, doses, faixa etária, via de administração e doenças prevenidas.

    Args:
        nome: Sigla ou nome da vacina (ex: "BCG", "tríplice viral", "HPV").

    Returns:
        Detalhes completos da vacina.
    """
    await ctx.info(f"Consultando vacina '{nome}'...")

    # Try exact match by sigla first
    vacina = client.buscar_vacina_por_sigla(nome)

    resultados = [vacina] if vacina else client.buscar_vacina_por_nome(nome)

    if not resultados:
        return (
            f"Vacina '{nome}' não encontrada no calendário do SUS. "
            "Tente a sigla (BCG, VIP, Penta, TV, HPV4) ou parte do nome."
        )

    lines = [f"**Vacina(s) encontrada(s)** ({len(resultados)} resultado(s))\n"]

    for v in resultados:
        doencas = ", ".join(v.get("doencas", []))
        lines.append(f"### {v['nome']} ({v['sigla']})")
        lines.append(f"- **Grupo:** {v.get('grupo', '—')}")
        lines.append(f"- **Doses:** {v['doses']}")
        lines.append(f"- **Idade:** {v['idade']}")
        lines.append(f"- **Via:** {v.get('via', '—')}")
        lines.append(f"- **Previne:** {doencas or '—'}")
        if v["sigla"] in METAS_COBERTURA:
            lines.append(f"- **Meta de cobertura:** {METAS_COBERTURA[v['sigla']]}%")
        # Check by name too
        for meta_nome, meta_pct in METAS_COBERTURA.items():
            if meta_nome == v["nome"]:
                lines.append(f"- **Meta de cobertura:** {meta_pct}%")
                break
        lines.append("")

    return "\n".join(lines)


async def verificar_esquema_vacinal(
    ctx: Context,
    idade: int,
) -> str:
    """Verifica quais vacinas uma pessoa deveria ter tomado conforme sua idade.

    Consulta o calendário nacional e lista todas as vacinas recomendadas
    até a idade informada, com número de doses e detalhes.

    Args:
        idade: Idade em anos completos (ex: 4, 12, 65).

    Returns:
        Lista de vacinas recomendadas para a idade.
    """
    await ctx.info(f"Verificando esquema vacinal para {idade} anos...")

    # Find the closest age key
    age_keys = sorted(int(k) for k in ESQUEMA_POR_IDADE)
    selected_key = "0"
    for k in age_keys:
        if idade >= k:
            selected_key = str(k)
        else:
            break

    siglas = ESQUEMA_POR_IDADE.get(selected_key, [])

    if not siglas:
        return f"Esquema vacinal não definido para {idade} anos."

    all_vacinas = client.listar_todas_vacinas()
    vacinas_map = {v["sigla"]: v for v in all_vacinas}

    lines = [f"**Esquema vacinal para {idade} anos** ({len(siglas)} vacinas recomendadas)\n"]

    rows = []
    for sigla in siglas:
        v = vacinas_map.get(sigla)
        if v:
            rows.append(
                (
                    v["sigla"],
                    v["nome"],
                    str(v["doses"]),
                    v["idade"],
                )
            )
        else:
            rows.append((sigla, "—", "—", "—"))

    lines.append(markdown_table(["Sigla", "Vacina", "Doses", "Idade"], rows))
    lines.append(
        "\n**Importante:** Procure uma Unidade Básica de Saúde (UBS) "
        "para verificar a caderneta de vacinação e atualizar doses em atraso."
    )
    return "\n".join(lines)


async def metas_cobertura(ctx: Context) -> str:
    """Mostra as metas de cobertura vacinal definidas pelo Ministério da Saúde.

    Cada vacina tem uma meta mínima de cobertura (% da população-alvo vacinada).
    Metas abaixo de 95% indicam risco de surtos de doenças prevenidas.

    Returns:
        Tabela com metas de cobertura por vacina.
    """
    await ctx.info("Consultando metas de cobertura vacinal...")

    rows = [
        (vacina, f"{meta}%")
        for vacina, meta in sorted(METAS_COBERTURA.items(), key=lambda x: -x[1])
    ]

    header = (
        f"**Metas de cobertura vacinal** ({len(METAS_COBERTURA)} vacinas) "
        "— Ministério da Saúde\n\n"
    )
    return header + markdown_table(["Vacina", "Meta (%)"], rows)
