"""Tool functions for the SINESP/MJSP CKAN feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import markdown_table

from . import client


async def listar_datasets_mjsp(ctx: Context) -> str:
    """Lista todos os datasets do portal de dados do MJSP.

    Retorna os 31 datasets disponíveis no portal dados.mj.gov.br,
    incluindo SINESP (ocorrências criminais), Infopen (sistema
    penitenciário), PRF, PF e outros.

    Returns:
        Lista de datasets disponíveis.
    """
    await ctx.info("Listando datasets do MJSP...")
    nomes = await client.listar_datasets()
    await ctx.info(f"{len(nomes)} datasets encontrados")

    if not nomes:
        return "Nenhum dataset encontrado no portal MJSP."

    rows = [(str(i), n) for i, n in enumerate(nomes, 1)]
    header = f"**{len(nomes)} datasets** no portal dados.mj.gov.br:\n\n"
    return header + markdown_table(["#", "Dataset (slug)"], rows)


async def buscar_datasets_mjsp(
    texto: str,
    ctx: Context,
    limite: int = 10,
) -> str:
    """Busca datasets no portal do MJSP por palavra-chave.

    Pesquisa full-text em título, descrição e tags dos datasets.
    Útil para encontrar dados sobre crimes específicos, sistema
    penitenciário, polícia, etc.

    Args:
        texto: Termo de busca (ex: "homicídio", "penitenciário", "drogas").
        limite: Máximo de resultados (padrão 10).

    Returns:
        Datasets encontrados com descrição e número de arquivos.
    """
    await ctx.info(f"Buscando datasets '{texto}'...")
    total, datasets = await client.buscar_datasets(texto, limite=limite)
    await ctx.info(f"{total} datasets encontrados")

    if not datasets:
        return f"Nenhum dataset encontrado para '{texto}'."

    lines = [f"**{total} datasets** encontrados para '{texto}':\n"]
    for i, d in enumerate(datasets, 1):
        lines.append(f"### {i}. {d.titulo or d.nome}")
        meta = []
        if d.organizacao:
            meta.append(f"**Org:** {d.organizacao}")
        meta.append(f"**Arquivos:** {d.num_recursos}")
        if d.tags:
            meta.append(f"**Tags:** {', '.join(d.tags[:5])}")
        lines.append(" | ".join(meta))
        if d.descricao:
            lines.append(f"\n> {d.descricao[:200]}...")
        lines.append(f"\n`slug: {d.nome}`\n")
    return "\n".join(lines)


async def detalhar_dataset_mjsp(
    dataset_id: str,
    ctx: Context,
) -> str:
    """Exibe detalhes completos de um dataset do MJSP incluindo arquivos.

    Retorna metadados, descrição e lista de recursos (arquivos CSV,
    XLSX, PDF) com URLs de download direto.

    Args:
        dataset_id: Slug do dataset (ex: "sistema-nacional-de-estatisticas-de-seguranca-publica").

    Returns:
        Detalhes do dataset com lista de arquivos para download.
    """
    await ctx.info(f"Detalhando dataset '{dataset_id}'...")
    dataset = await client.detalhar_dataset(dataset_id)

    if not dataset:
        return f"Dataset '{dataset_id}' não encontrado."

    lines = [f"# {dataset.titulo or dataset.nome}\n"]
    if dataset.organizacao:
        lines.append(f"**Organização:** {dataset.organizacao}")
    if dataset.licenca:
        lines.append(f"**Licença:** {dataset.licenca}")
    if dataset.tags:
        lines.append(f"**Tags:** {', '.join(dataset.tags)}")
    if dataset.descricao:
        lines.append(f"\n{dataset.descricao}\n")

    if dataset.recursos:
        lines.append(f"\n## Arquivos ({len(dataset.recursos)})\n")
        rows = [
            (
                r.nome or "Sem nome",
                r.formato or "N/A",
                r.url or "N/A",
            )
            for r in dataset.recursos
        ]
        lines.append(markdown_table(["Nome", "Formato", "URL"], rows))

    return "\n".join(lines)


async def listar_organizacoes_mjsp(ctx: Context) -> str:
    """Lista as organizações do portal de dados do MJSP.

    Retorna SENASP, DEPEN, DPF, DPRF e demais órgãos que publicam
    dados no portal dados.mj.gov.br.

    Returns:
        Lista de organizações com quantidade de datasets.
    """
    await ctx.info("Listando organizações...")
    orgs = await client.listar_organizacoes()
    await ctx.info(f"{len(orgs)} organizações encontradas")

    if not orgs:
        return "Nenhuma organização encontrada."

    rows = [
        (o.nome, o.titulo or "N/A", str(o.num_datasets))
        for o in sorted(orgs, key=lambda x: x.num_datasets, reverse=True)
    ]
    return f"**{len(orgs)} organizações** no portal MJSP:\n\n" + markdown_table(
        ["Slug", "Nome", "Datasets"], rows
    )


async def listar_datasets_organizacao(
    org_id: str,
    ctx: Context,
) -> str:
    """Lista datasets publicados por uma organização do MJSP.

    Use para ver todos os dados publicados pela SENASP, DEPEN, PF, PRF etc.

    Args:
        org_id: Slug da organização (ex: "senasp", "depen", "dpf").

    Returns:
        Lista de datasets da organização.
    """
    await ctx.info(f"Listando datasets da organização '{org_id}'...")
    org, datasets = await client.detalhar_organizacao(org_id)

    if not org:
        return f"Organização '{org_id}' não encontrada."

    lines = [f"## {org.titulo or org.nome}\n"]
    if org.descricao:
        lines.append(f"{org.descricao[:300]}\n")
    lines.append(f"**{org.num_datasets} datasets publicados:**\n")

    if datasets:
        rows = [(d.nome, d.titulo or "N/A", str(d.num_recursos)) for d in datasets]
        lines.append(markdown_table(["Slug", "Título", "Arquivos"], rows))
    else:
        lines.append("Nenhum dataset encontrado.")

    return "\n".join(lines)


async def listar_datasets_grupo_seguranca(
    ctx: Context,
    grupo: str = "seguranca-publica",
) -> str:
    """Lista datasets do grupo de segurança pública no portal MJSP.

    Filtra por grupo temático. O padrão é "seguranca-publica" mas também
    aceita "combate-as-drogas", "justica-e-legislacao", etc.

    Args:
        grupo: Slug do grupo temático (padrão: "seguranca-publica").

    Returns:
        Datasets do grupo temático.
    """
    await ctx.info(f"Listando datasets do grupo '{grupo}'...")
    titulo, datasets = await client.listar_datasets_grupo(grupo)

    if titulo is None:
        return f"Grupo '{grupo}' não encontrado."

    lines = [f"## {titulo}\n"]
    if datasets:
        lines.append(f"**{len(datasets)} datasets:**\n")
        rows = [(d.nome, d.titulo or "N/A", str(d.num_recursos)) for d in datasets]
        lines.append(markdown_table(["Slug", "Título", "Arquivos"], rows))
    else:
        lines.append("Nenhum dataset neste grupo.")

    return "\n".join(lines)
