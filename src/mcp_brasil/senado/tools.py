"""Tool functions for the Senado Federal feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

from mcp_brasil._shared.formatting import markdown_table

from . import client
from .constants import DEFAULT_PAGE_SIZE


def _pagination_hint(count: int, page_size: int = DEFAULT_PAGE_SIZE) -> str:
    """Hint when there may be more results."""
    if count >= page_size:
        return "\n\n> Há mais resultados. Refine os filtros para resultados mais específicos."
    return ""


# --- Senadores (4 tools) ---------------------------------------------------


async def listar_senadores() -> str:
    """Lista todos os senadores em exercício no Senado Federal.

    Retorna a lista completa de senadores da legislatura atual com partido e UF.

    Returns:
        Tabela com senadores em exercício.
    """
    senadores = await client.listar_senadores()
    if not senadores:
        return "Nenhum senador em exercício encontrado."

    rows = [
        (
            s.codigo or "—",
            (s.nome or "—")[:40],
            s.partido or "—",
            s.uf or "—",
        )
        for s in senadores
    ]
    header = f"Senadores em exercício ({len(senadores)} senadores):\n\n"
    return header + markdown_table(["Código", "Nome", "Partido", "UF"], rows)


async def buscar_senador(codigo: str) -> str:
    """Busca detalhes de um senador pelo código.

    Retorna perfil completo com nome, partido, UF, contato e mandato.

    Args:
        codigo: Código do senador na API do Senado.

    Returns:
        Perfil detalhado do senador.
    """
    sen = await client.obter_senador(codigo)
    if not sen:
        return f"Senador com código {codigo} não encontrado."

    lines = [
        f"**{sen.nome_completo or sen.nome or '—'}**",
        f"- Partido: {sen.partido or '—'}",
        f"- UF: {sen.uf or '—'}",
        f"- Email: {sen.email or '—'}",
        f"- Telefone: {sen.telefone or '—'}",
    ]
    if sen.mandato_inicio or sen.mandato_fim:
        lines.append(f"- Mandato: {sen.mandato_inicio or '—'} a {sen.mandato_fim or '—'}")
    if sen.foto:
        lines.append(f"- Foto: {sen.foto}")
    return "\n".join(lines)


async def buscar_senador_por_nome(nome: str) -> str:
    """Busca senadores em exercício pelo nome.

    Pesquisa parcial no nome dos senadores da legislatura atual.

    Args:
        nome: Nome ou parte do nome do senador.

    Returns:
        Tabela com senadores encontrados.
    """
    senadores = await client.buscar_senador_por_nome(nome)
    if not senadores:
        return f"Nenhum senador encontrado com o nome '{nome}'."

    rows = [
        (
            s.codigo or "—",
            (s.nome or "—")[:40],
            s.partido or "—",
            s.uf or "—",
        )
        for s in senadores
    ]
    header = f"Senadores encontrados para '{nome}':\n\n"
    return header + markdown_table(["Código", "Nome", "Partido", "UF"], rows)


async def votacoes_senador(codigo: str) -> str:
    """Consulta votações em que um senador participou.

    Args:
        codigo: Código do senador na API do Senado.

    Returns:
        Lista de votações com datas e resultados.
    """
    votacoes = await client.votacoes_senador(codigo)
    if not votacoes:
        return f"Nenhuma votação encontrada para o senador {codigo}."

    rows = [
        (
            v.codigo or "—",
            v.data or "—",
            (v.descricao or "—")[:60],
            v.resultado or "—",
        )
        for v in votacoes[:50]
    ]
    header = f"Votações do senador {codigo} ({len(votacoes)} votações):\n\n"
    table = header + markdown_table(["Código", "Data", "Descrição", "Resultado"], rows)
    if len(votacoes) > 50:
        table += f"\n\n... e mais {len(votacoes) - 50} votações."
    return table


# --- Matérias (5 tools) ----------------------------------------------------


async def buscar_materia(
    sigla_tipo: str | None = None,
    numero: str | None = None,
    ano: str | None = None,
    keywords: str | None = None,
    tramitando: bool = False,
) -> str:
    """Busca matérias legislativas no Senado (PEC, PLS, PLC, MPV, etc.).

    Permite filtrar por tipo, número, ano ou palavras-chave na ementa.

    Args:
        sigla_tipo: Tipo da matéria (ex: PEC, PLS, PLC, MPV, PLP).
        numero: Número da matéria.
        ano: Ano da matéria.
        keywords: Palavras-chave para busca na ementa.
        tramitando: Se True, retorna apenas matérias em tramitação.

    Returns:
        Tabela com matérias encontradas.
    """
    materias = await client.buscar_materias(
        sigla_tipo=sigla_tipo,
        numero=numero,
        ano=ano,
        keywords=keywords,
        tramitando=tramitando,
    )
    if not materias:
        return "Nenhuma matéria encontrada para os filtros informados."

    rows = [
        (
            f"{m.sigla_tipo or '—'} {m.numero or '—'}/{m.ano or '—'}",
            (m.ementa or "—")[:80],
            m.data_apresentacao or "—",
            (m.situacao or "—")[:30],
        )
        for m in materias[:DEFAULT_PAGE_SIZE]
    ]
    header = f"Matérias encontradas ({len(materias)} resultado(s)):\n\n"
    table = header + markdown_table(["Matéria", "Ementa", "Apresentação", "Situação"], rows)
    return table + _pagination_hint(len(materias))


async def detalhe_materia(codigo: str) -> str:
    """Obtém detalhes de uma matéria legislativa pelo código.

    Retorna ementa completa, autor, situação e casa de origem.

    Args:
        codigo: Código da matéria na API do Senado.

    Returns:
        Detalhes completos da matéria.
    """
    materia = await client.obter_materia(codigo)
    if not materia:
        return f"Matéria com código {codigo} não encontrada."

    ident = f"{materia.sigla_tipo or '—'} {materia.numero or '—'}/{materia.ano or '—'}"
    lines = [
        f"**{ident}**",
        f"- Ementa: {materia.ementa or '—'}",
    ]
    if materia.ementa_completa:
        lines.append(f"- Explicação: {materia.ementa_completa}")
    lines.extend(
        [
            f"- Autor: {materia.autor or '—'}",
            f"- Data de apresentação: {materia.data_apresentacao or '—'}",
            f"- Situação: {materia.situacao or '—'}",
            f"- Casa de origem: {materia.casa_origem or '—'}",
        ]
    )
    return "\n".join(lines)


async def consultar_tramitacao_materia(codigo: str) -> str:
    """Consulta a tramitação de uma matéria legislativa no Senado.

    Mostra o histórico de tramitação com datas, locais e situações.

    Args:
        codigo: Código da matéria na API do Senado.

    Returns:
        Lista de eventos de tramitação.
    """
    tramitacoes = await client.tramitacao_materia(codigo)
    if not tramitacoes:
        return f"Nenhuma tramitação encontrada para a matéria {codigo}."

    rows = [
        (
            t.data or "—",
            (t.descricao or "—")[:60],
            t.local or "—",
            (t.situacao or "—")[:30],
        )
        for t in tramitacoes[:50]
    ]
    header = f"Tramitação da matéria {codigo}:\n\n"
    table = header + markdown_table(["Data", "Descrição", "Local", "Situação"], rows)
    if len(tramitacoes) > 50:
        table += f"\n\n... e mais {len(tramitacoes) - 50} eventos de tramitação."
    return table


async def textos_materia(codigo: str) -> str:
    """Lista textos e documentos de uma matéria legislativa.

    Retorna links para os documentos oficiais (texto original, emendas, pareceres, etc.).

    Args:
        codigo: Código da matéria na API do Senado.

    Returns:
        Lista de documentos com URLs.
    """
    textos = await client.textos_materia(codigo)
    if not textos:
        return f"Nenhum texto encontrado para a matéria {codigo}."

    rows = [
        (
            t.get("tipo") or "—",
            t.get("data") or "—",
            t.get("url") or "—",
        )
        for t in textos
    ]
    header = f"Textos da matéria {codigo}:\n\n"
    return header + markdown_table(["Tipo", "Data", "URL"], rows)


async def votos_materia(codigo: str) -> str:
    """Consulta votações de uma matéria legislativa no Senado.

    Mostra resultados com placar (Sim/Não/Abstenção).

    Args:
        codigo: Código da matéria na API do Senado.

    Returns:
        Lista de votações com resultados.
    """
    votacoes = await client.votos_materia(codigo)
    if not votacoes:
        return f"Nenhuma votação encontrada para a matéria {codigo}."

    rows = [
        (
            v.codigo or "—",
            v.data or "—",
            (v.descricao or "—")[:50],
            v.resultado or "—",
            f"S:{v.sim or 0} N:{v.nao or 0} A:{v.abstencao or 0}",
        )
        for v in votacoes
    ]
    header = f"Votações da matéria {codigo}:\n\n"
    return header + markdown_table(["Código", "Data", "Descrição", "Resultado", "Placar"], rows)


# --- Votações (3 tools) ----------------------------------------------------


async def listar_votacoes(ano: str) -> str:
    """Lista votações do plenário do Senado em um ano.

    Args:
        ano: Ano das votações (ex: 2024).

    Returns:
        Tabela com votações do ano.
    """
    votacoes = await client.listar_votacoes(ano)
    if not votacoes:
        return f"Nenhuma votação encontrada para o ano {ano}."

    rows = [
        (
            v.codigo or "—",
            v.data or "—",
            (v.descricao or "—")[:60],
            v.resultado or "—",
        )
        for v in votacoes[:DEFAULT_PAGE_SIZE]
    ]
    header = f"Votações do plenário em {ano} ({len(votacoes)} votações):\n\n"
    table = header + markdown_table(["Código", "Data", "Descrição", "Resultado"], rows)
    return table + _pagination_hint(len(votacoes))


async def detalhe_votacao(codigo_sessao: str) -> str:
    """Obtém detalhes de uma votação do Senado, incluindo placar.

    Args:
        codigo_sessao: Código da sessão de votação.

    Returns:
        Detalhes da votação com placar.
    """
    votacao = await client.obter_votacao(codigo_sessao)
    if not votacao:
        return f"Votação com código {codigo_sessao} não encontrada."

    lines = [
        f"**Votação {votacao.codigo or '—'}**",
        f"- Data: {votacao.data or '—'}",
        f"- Descrição: {votacao.descricao or '—'}",
        f"- Resultado: {votacao.resultado or '—'}",
        f"- Placar: Sim={votacao.sim or 0}, Não={votacao.nao or 0}, "
        f"Abstenção={votacao.abstencao or 0}",
    ]
    if votacao.materia_descricao:
        lines.append(f"- Matéria: {votacao.materia_descricao}")
    return "\n".join(lines)


async def votacoes_recentes(data: str) -> str:
    """Lista votações do Senado em uma data específica.

    Args:
        data: Data no formato AAAAMMDD (ex: 20240315).

    Returns:
        Tabela com votações da data.
    """
    votacoes = await client.votacoes_recentes(data)
    if not votacoes:
        return f"Nenhuma votação encontrada para a data {data}."

    rows = [
        (
            v.codigo or "—",
            v.data or "—",
            (v.descricao or "—")[:60],
            v.resultado or "—",
        )
        for v in votacoes
    ]
    header = f"Votações em {data}:\n\n"
    return header + markdown_table(["Código", "Data", "Descrição", "Resultado"], rows)


# --- Comissões (4 tools) ---------------------------------------------------


async def listar_comissoes() -> str:
    """Lista comissões do Senado Federal.

    Inclui comissões permanentes, temporárias, CPIs e subcomissões.

    Returns:
        Tabela com comissões do Senado.
    """
    comissoes = await client.listar_comissoes()
    if not comissoes:
        return "Nenhuma comissão encontrada."

    rows = [
        (
            c.codigo or "—",
            c.sigla or "—",
            (c.nome or "—")[:60],
            c.tipo or "—",
        )
        for c in comissoes
    ]
    header = f"Comissões do Senado ({len(comissoes)} comissões):\n\n"
    return header + markdown_table(["Código", "Sigla", "Nome", "Tipo"], rows)


async def detalhe_comissao(codigo: str) -> str:
    """Obtém detalhes de uma comissão do Senado.

    Args:
        codigo: Código da comissão na API do Senado.

    Returns:
        Detalhes da comissão.
    """
    comissao = await client.obter_comissao(codigo)
    if not comissao:
        return f"Comissão com código {codigo} não encontrada."

    lines = [
        f"**{comissao.nome or '—'}** ({comissao.sigla or '—'})",
        f"- Tipo: {comissao.tipo or '—'}",
        f"- Data de criação: {comissao.data_criacao or '—'}",
    ]
    if comissao.data_extincao:
        lines.append(f"- Data de extinção: {comissao.data_extincao}")
    if comissao.finalidade:
        lines.append(f"- Finalidade: {comissao.finalidade}")
    return "\n".join(lines)


async def membros_comissao(codigo: str) -> str:
    """Lista membros de uma comissão do Senado.

    Args:
        codigo: Código da comissão na API do Senado.

    Returns:
        Tabela com membros da comissão.
    """
    membros = await client.membros_comissao(codigo)
    if not membros:
        return f"Nenhum membro encontrado para a comissão {codigo}."

    rows = [
        (
            (m.nome or "—")[:40],
            m.partido or "—",
            m.uf or "—",
            m.cargo or "—",
        )
        for m in membros
    ]
    header = f"Membros da comissão {codigo}:\n\n"
    return header + markdown_table(["Nome", "Partido", "UF", "Cargo"], rows)


async def reunioes_comissao(codigo: str) -> str:
    """Lista reuniões de uma comissão do Senado.

    Args:
        codigo: Código da comissão na API do Senado.

    Returns:
        Tabela com reuniões da comissão.
    """
    reunioes = await client.reunioes_comissao(codigo)
    if not reunioes:
        return f"Nenhuma reunião encontrada para a comissão {codigo}."

    rows = [
        (
            r.data or "—",
            r.tipo or "—",
            (r.pauta or "—")[:60],
            r.local or "—",
        )
        for r in reunioes[:DEFAULT_PAGE_SIZE]
    ]
    header = f"Reuniões da comissão {codigo}:\n\n"
    table = header + markdown_table(["Data", "Tipo", "Pauta", "Local"], rows)
    return table + _pagination_hint(len(reunioes))


# --- Agenda (2 tools) ------------------------------------------------------


async def agenda_plenario(ano: str, mes: str) -> str:
    """Consulta a agenda do plenário do Senado para um mês.

    Args:
        ano: Ano (ex: 2024).
        mes: Mês (01-12).

    Returns:
        Tabela com sessões plenárias do mês.
    """
    sessoes = await client.agenda_plenario(ano, mes)
    if not sessoes:
        return f"Nenhuma sessão encontrada para {mes}/{ano}."

    rows = [
        (
            s.data or "—",
            s.tipo or "—",
            s.numero or "—",
            s.situacao or "—",
        )
        for s in sessoes
    ]
    header = f"Agenda do plenário — {mes}/{ano}:\n\n"
    return header + markdown_table(["Data", "Tipo", "Número", "Situação"], rows)


async def agenda_comissoes(data: str) -> str:
    """Consulta a agenda de comissões do Senado para uma data.

    Args:
        data: Data no formato AAAAMMDD (ex: 20240315).

    Returns:
        Tabela com reuniões de comissões na data.
    """
    reunioes = await client.agenda_comissoes(data)
    if not reunioes:
        return f"Nenhuma reunião de comissão encontrada para a data {data}."

    rows = [
        (
            r.data or "—",
            r.comissao or "—",
            r.tipo or "—",
            (r.pauta or "—")[:60],
        )
        for r in reunioes
    ]
    header = f"Reuniões de comissões em {data}:\n\n"
    return header + markdown_table(["Data", "Comissão", "Tipo", "Pauta"], rows)


# --- Auxiliares (2 tools) --------------------------------------------------


async def legislatura_atual() -> str:
    """Consulta informações da legislatura atual do Senado.

    Returns:
        Dados da legislatura (número, período).
    """
    leg = await client.legislatura_atual()
    if not leg:
        return "Informação da legislatura não disponível."

    return (
        f"**Legislatura {leg.numero or '—'}**\n"
        f"- Início: {leg.data_inicio or '—'}\n"
        f"- Fim: {leg.data_fim or '—'}"
    )


async def partidos_senado() -> str:
    """Lista partidos com representação no Senado Federal.

    Retorna os partidos ordenados pelo número de senadores em exercício.

    Returns:
        Tabela com partidos e quantidade de senadores.
    """
    senadores = await client.listar_senadores()
    if not senadores:
        return "Nenhum senador encontrado."

    contagem: dict[str, int] = {}
    for s in senadores:
        partido = s.partido or "S/Partido"
        contagem[partido] = contagem.get(partido, 0) + 1

    rows = [(partido, str(qtd)) for partido, qtd in sorted(contagem.items(), key=lambda x: -x[1])]
    header = f"Partidos no Senado ({len(contagem)} partidos, {len(senadores)} senadores):\n\n"
    return header + markdown_table(["Partido", "Senadores"], rows)


async def ufs_senado() -> str:
    """Lista unidades federativas com representação no Senado Federal.

    Retorna os estados ordenados pela sigla com o número de senadores em exercício.

    Returns:
        Tabela com UFs e quantidade de senadores.
    """
    senadores = await client.listar_senadores()
    if not senadores:
        return "Nenhum senador encontrado."

    contagem: dict[str, int] = {}
    for s in senadores:
        uf = s.uf or "N/A"
        contagem[uf] = contagem.get(uf, 0) + 1

    rows = [(uf, str(qtd)) for uf, qtd in sorted(contagem.items())]
    header = f"UFs no Senado ({len(contagem)} UFs, {len(senadores)} senadores):\n\n"
    return header + markdown_table(["UF", "Senadores"], rows)


async def tipos_materia() -> str:
    """Lista os tipos de matéria legislativa do Senado.

    Retorna as siglas e descrições dos principais tipos de proposição.

    Returns:
        Tabela com tipos de matéria.
    """
    tipos = await client.tipos_materia_api()
    rows = [(sigla, descricao) for sigla, descricao in sorted(tipos.items())]
    return "Tipos de matéria do Senado:\n\n" + markdown_table(["Sigla", "Descrição"], rows)
