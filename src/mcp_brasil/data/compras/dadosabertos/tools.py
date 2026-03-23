"""Tool functions for the Dados Abertos Compras.gov.br feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import format_brl

from . import client


async def buscar_licitacoes(
    data_publicacao_inicial: str,
    data_publicacao_final: str,
    ctx: Context,
    uasg: int | None = None,
    modalidade: int | None = None,
    pagina: int = 1,
) -> str:
    """Busca licitações no sistema legado SIASG/ComprasNet (até 2020).

    Pesquisa licitações federais por período de publicação. Dados históricos
    do SIASG (Sistema Integrado de Administração de Serviços Gerais).

    Args:
        data_publicacao_inicial: Data início YYYY-MM-DD (obrigatório).
        data_publicacao_final: Data fim YYYY-MM-DD (obrigatório).
        uasg: Código UASG do órgão (opcional).
        modalidade: Código da modalidade (1=Convite, 2=Tomada de preço,
            3=Concorrência, 5=Pregão, 6=Dispensa, 7=Inexigibilidade).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de licitações encontradas com objeto, valor e situação.
    """
    await ctx.info(
        f"Buscando licitações de {data_publicacao_inicial} a {data_publicacao_final}..."
    )
    resultado = await client.buscar_licitacoes(
        data_publicacao_inicial=data_publicacao_inicial,
        data_publicacao_final=data_publicacao_final,
        uasg=uasg,
        modalidade=modalidade,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} licitações encontradas")

    if not resultado.licitacoes:
        return "Nenhuma licitação encontrada no período informado."

    lines = [f"**Total:** {resultado.total} licitações\n"]
    for i, lic in enumerate(resultado.licitacoes, 1):
        val_est = format_brl(lic.valor_estimado_total) if lic.valor_estimado_total else "N/A"
        val_hom = format_brl(lic.valor_homologado_total) if lic.valor_homologado_total else "N/A"
        lines.extend(
            [
                f"### {i}. {lic.objeto or 'Sem descrição'}",
                f"**UASG:** {lic.uasg or 'N/A'} | **Modalidade:** {lic.nome_modalidade or 'N/A'}",
                f"**Situação:** {lic.situacao_aviso or 'N/A'}",
                f"**Valor estimado:** {val_est} | **Homologado:** {val_hom}",
                f"**Publicação:** {lic.data_publicacao or 'N/A'}",
                f"**Itens:** {lic.numero_itens or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.licitacoes):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_pregoes(
    data_edital_inicial: str,
    data_edital_final: str,
    ctx: Context,
    co_uasg: int | None = None,
    pagina: int = 1,
) -> str:
    """Busca pregões eletrônicos no SIASG/ComprasNet.

    Pregões são a modalidade mais utilizada para aquisição de bens e
    serviços comuns pelo governo federal.

    Args:
        data_edital_inicial: Data início do edital YYYY-MM-DD (obrigatório).
        data_edital_final: Data fim do edital YYYY-MM-DD (obrigatório).
        co_uasg: Código UASG do órgão (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de pregões encontrados.
    """
    await ctx.info(f"Buscando pregões de {data_edital_inicial} a {data_edital_final}...")
    resultado = await client.buscar_pregoes(
        data_edital_inicial=data_edital_inicial,
        data_edital_final=data_edital_final,
        co_uasg=co_uasg,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} pregões encontrados")

    if not resultado.licitacoes:
        return "Nenhum pregão encontrado no período informado."

    lines = [f"**Total:** {resultado.total} pregões\n"]
    for i, lic in enumerate(resultado.licitacoes, 1):
        val_est = format_brl(lic.valor_estimado_total) if lic.valor_estimado_total else "N/A"
        val_hom = format_brl(lic.valor_homologado_total) if lic.valor_homologado_total else "N/A"
        lines.extend(
            [
                f"### {i}. {lic.objeto or 'Sem descrição'}",
                f"**UASG:** {lic.uasg or 'N/A'} | **Tipo:** {lic.tipo_pregao or 'N/A'}",
                f"**Situação:** {lic.situacao_aviso or 'N/A'}",
                f"**Valor estimado:** {val_est} | **Homologado:** {val_hom}",
                f"**Publicação:** {lic.data_publicacao or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.licitacoes):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_dispensas(
    ano_aviso: int,
    ctx: Context,
    co_uasg: int | None = None,
    pagina: int = 1,
) -> str:
    """Busca compras sem licitação (dispensas e inexigibilidades).

    Dispensas são compras realizadas sem processo licitatório, conforme
    previsão legal (art. 24 da Lei 8.666/93 ou art. 75 da Lei 14.133/2021).

    Args:
        ano_aviso: Ano do aviso de dispensa (obrigatório, ex: 2020).
        co_uasg: Código UASG do órgão (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de compras sem licitação encontradas.
    """
    await ctx.info(f"Buscando dispensas do ano {ano_aviso}...")
    resultado = await client.buscar_dispensas(
        ano_aviso=ano_aviso,
        co_uasg=co_uasg,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} dispensas encontradas")

    if not resultado.licitacoes:
        return f"Nenhuma dispensa encontrada para o ano {ano_aviso}."

    lines = [f"**Total:** {resultado.total} dispensas\n"]
    for i, lic in enumerate(resultado.licitacoes, 1):
        val_est = format_brl(lic.valor_estimado_total) if lic.valor_estimado_total else "N/A"
        lines.extend(
            [
                f"### {i}. {lic.objeto or 'Sem descrição'}",
                f"**UASG:** {lic.uasg or 'N/A'} | **Modalidade:** {lic.nome_modalidade or 'N/A'}",
                f"**Valor estimado:** {val_est}",
                f"**Publicação:** {lic.data_publicacao or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.licitacoes):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_contratos(
    data_vigencia_inicial_min: str,
    data_vigencia_inicial_max: str,
    ctx: Context,
    codigo_orgao: str | None = None,
    ni_fornecedor: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca contratos no Compras.gov.br (Dados Abertos).

    Consulta contratos federais por período de vigência. Inclui dados
    completos: órgão, fornecedor, objeto, valor e prazo.

    Args:
        data_vigencia_inicial_min: Início da vigência mínima YYYY-MM-DD (obrigatório).
        data_vigencia_inicial_max: Início da vigência máxima YYYY-MM-DD (obrigatório).
        codigo_orgao: Código do órgão (opcional).
        ni_fornecedor: CNPJ/CPF do fornecedor (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de contratos encontrados.
    """
    await ctx.info("Buscando contratos...")
    resultado = await client.buscar_contratos(
        data_vigencia_inicial_min=data_vigencia_inicial_min,
        data_vigencia_inicial_max=data_vigencia_inicial_max,
        codigo_orgao=codigo_orgao,
        ni_fornecedor=ni_fornecedor,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} contratos encontrados")

    if not resultado.contratos:
        return "Nenhum contrato encontrado no período informado."

    lines = [f"**Total:** {resultado.total} contratos\n"]
    for i, c in enumerate(resultado.contratos, 1):
        valor = format_brl(c.valor_global) if c.valor_global else "N/A"
        lines.extend(
            [
                f"### {i}. {c.objeto or 'Sem descrição'}",
                f"**Órgão:** {c.nome_orgao or 'N/A'}",
                f"**Fornecedor:** {c.nome_fornecedor or 'N/A'} ({c.ni_fornecedor or 'N/A'})",
                f"**Contrato nº:** {c.numero_contrato or 'N/A'}",
                f"**Modalidade:** {c.nome_modalidade_compra or 'N/A'}"
                f" | **Tipo:** {c.nome_tipo or 'N/A'}",
                f"**Valor global:** {valor}",
                f"**Vigência:** {c.data_vigencia_inicial or 'N/A'}"
                f" a {c.data_vigencia_final or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.contratos):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def consultar_fornecedor(
    ctx: Context,
    cnpj: str | None = None,
    cpf: str | None = None,
    pagina: int = 1,
) -> str:
    """Consulta fornecedores cadastrados no Compras.gov.br.

    Busca dados de fornecedores que participam de licitações federais.
    Pelo menos um filtro (CNPJ ou CPF) deve ser informado.

    Args:
        cnpj: CNPJ do fornecedor (opcional).
        cpf: CPF do fornecedor pessoa física (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Dados do fornecedor encontrado.
    """
    if not any([cnpj, cpf]):
        return "Informe pelo menos um filtro: cnpj ou cpf."

    desc = cnpj or cpf or "fornecedor"
    await ctx.info(f"Consultando fornecedor {desc}...")
    resultado = await client.consultar_fornecedor(cnpj=cnpj, cpf=cpf, pagina=pagina)
    await ctx.info(f"{resultado.total} fornecedor(es) encontrado(s)")

    if not resultado.fornecedores:
        return f"Nenhum fornecedor encontrado para {desc}."

    lines: list[str] = []
    for f in resultado.fornecedores:
        ident = f.cnpj or f.cpf or "N/A"
        lines.extend(
            [
                f"**{f.nome_razao_social or 'N/A'}**",
                f"**CNPJ/CPF:** {ident}",
                f"**Local:** {f.nome_municipio or 'N/A'}/{f.uf_sigla or 'N/A'}",
                f"**Porte:** {f.porte_empresa_nome or 'N/A'}",
                f"**CNAE:** {f.nome_cnae or 'N/A'}",
                f"**Ativo:** {'Sim' if f.ativo else 'Não'}"
                f" | **Habilitado:** {'Sim' if f.habilitado_licitar else 'Não'}",
                "",
            ]
        )
    return "\n".join(lines)


async def buscar_material_catmat(
    ctx: Context,
    descricao: str | None = None,
    codigo_grupo: int | None = None,
    codigo_classe: int | None = None,
    pagina: int = 1,
) -> str:
    """Busca itens no catálogo CATMAT (materiais do governo federal).

    O CATMAT é o Catálogo de Materiais usado pelo governo federal para
    classificar e padronizar a aquisição de materiais (bens).

    Args:
        descricao: Descrição do material (opcional).
        codigo_grupo: Código do grupo CATMAT (opcional, ex: 70=TIC, 65=Saúde).
        codigo_classe: Código da classe CATMAT (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de materiais encontrados no catálogo.
    """
    if not any([descricao, codigo_grupo, codigo_classe]):
        return "Informe pelo menos um filtro: descricao, codigo_grupo ou codigo_classe."

    desc = descricao or f"grupo {codigo_grupo}" if codigo_grupo else "material"
    await ctx.info(f"Buscando material CATMAT '{desc}'...")
    resultado = await client.buscar_material(
        descricao=descricao,
        codigo_grupo=codigo_grupo,
        codigo_classe=codigo_classe,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} materiais encontrados")

    if not resultado.itens:
        return f"Nenhum material encontrado para '{desc}'."

    lines = [f"**Total:** {resultado.total} materiais\n"]
    for i, item in enumerate(resultado.itens, 1):
        status = "Ativo" if item.status_item else "Inativo"
        lines.extend(
            [
                f"### {i}. {item.descricao_item or 'Sem descrição'}",
                f"**Código:** {item.codigo_item or 'N/A'}",
                f"**Grupo:** {item.codigo_grupo or 'N/A'}"
                f" | **Classe:** {item.codigo_classe or 'N/A'}"
                f" | **PDM:** {item.codigo_pdm or 'N/A'}",
                f"**Status:** {status}",
                "",
            ]
        )

    if resultado.total > len(resultado.itens):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_servico_catser(
    ctx: Context,
    codigo_servico: int | None = None,
    codigo_grupo: int | None = None,
    pagina: int = 1,
) -> str:
    """Busca itens no catálogo CATSER (serviços do governo federal).

    O CATSER é o Catálogo de Serviços usado pelo governo federal para
    classificar e padronizar a contratação de serviços.

    Args:
        codigo_servico: Código do serviço CATSER (opcional).
        codigo_grupo: Código do grupo CATSER (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de serviços encontrados no catálogo.
    """
    if not any([codigo_servico, codigo_grupo]):
        return "Informe pelo menos um filtro: codigo_servico ou codigo_grupo."

    await ctx.info("Buscando serviço CATSER...")
    resultado = await client.buscar_servico(
        codigo_servico=codigo_servico,
        codigo_grupo=codigo_grupo,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} serviços encontrados")

    if not resultado.itens:
        return "Nenhum serviço encontrado."

    lines = [f"**Total:** {resultado.total} serviços\n"]
    for i, item in enumerate(resultado.itens, 1):
        status = "Ativo" if item.status_servico else "Inativo"
        lines.extend(
            [
                f"### {i}. {item.nome_servico or 'Sem descrição'}",
                f"**Código:** {item.codigo_servico or 'N/A'}",
                f"**Grupo:** {item.codigo_grupo or 'N/A'}"
                f" | **Classe:** {item.codigo_classe or 'N/A'}",
                f"**Status:** {status}",
                "",
            ]
        )

    if resultado.total > len(resultado.itens):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_uasg(
    ctx: Context,
    codigo_uasg: str | None = None,
    sigla_uf: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca UASGs (Unidades Administrativas de Serviços Gerais).

    UASGs são as unidades do governo federal que realizam compras. Use esta
    ferramenta para encontrar o código UASG de um órgão e filtrar buscas.

    Args:
        codigo_uasg: Código da UASG (opcional).
        sigla_uf: Sigla da UF (ex: SP, RJ, DF) (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de UASGs encontradas.
    """
    if not any([codigo_uasg, sigla_uf]):
        return "Informe pelo menos um filtro: codigo_uasg ou sigla_uf."

    desc = codigo_uasg or sigla_uf or "UASG"
    await ctx.info(f"Buscando UASG '{desc}'...")
    resultado = await client.buscar_uasg(
        codigo_uasg=codigo_uasg,
        sigla_uf=sigla_uf,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} UASGs encontradas")

    if not resultado.uasgs:
        return f"Nenhuma UASG encontrada para '{desc}'."

    lines = [f"**Total:** {resultado.total} UASGs\n"]
    for i, u in enumerate(resultado.uasgs, 1):
        lines.extend(
            [
                f"### {i}. {u.nome_uasg or 'N/A'}",
                f"**Código:** {u.codigo_uasg or 'N/A'}",
                f"**CNPJ:** {u.cnpj_cpf_orgao or 'N/A'}",
                f"**Local:** {u.nome_municipio or 'N/A'}/{u.sigla_uf or 'N/A'}",
                f"**SISG:** {'Sim' if u.uso_sisg else 'Não'}",
                "",
            ]
        )

    if resultado.total > len(resultado.uasgs):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)
