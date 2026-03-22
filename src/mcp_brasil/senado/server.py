"""Senado feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import acompanhar_materia, analise_votacao_senado, perfil_senador
from .resources import comissoes_permanentes, info_api, tipos_materia
from .tools import (
    agenda_comissoes,
    agenda_plenario,
    buscar_materia,
    buscar_senador,
    buscar_senador_por_nome,
    consultar_tramitacao_materia,
    detalhe_comissao,
    detalhe_materia,
    detalhe_votacao,
    legislatura_atual,
    listar_comissoes,
    listar_senadores,
    listar_votacoes,
    membros_comissao,
    partidos_senado,
    reunioes_comissao,
    textos_materia,
    ufs_senado,
    votacoes_recentes,
    votacoes_senador,
    votos_materia,
)
from .tools import (
    tipos_materia as tipos_materia_tool,
)

mcp = FastMCP("mcp-brasil-senado")

# Tools — Senadores (4)
mcp.tool(listar_senadores)
mcp.tool(buscar_senador)
mcp.tool(buscar_senador_por_nome)
mcp.tool(votacoes_senador)

# Tools — Matérias (5)
mcp.tool(buscar_materia)
mcp.tool(detalhe_materia)
mcp.tool(consultar_tramitacao_materia)
mcp.tool(textos_materia)
mcp.tool(votos_materia)

# Tools — Votações (3)
mcp.tool(listar_votacoes)
mcp.tool(detalhe_votacao)
mcp.tool(votacoes_recentes)

# Tools — Comissões (4)
mcp.tool(listar_comissoes)
mcp.tool(detalhe_comissao)
mcp.tool(membros_comissao)
mcp.tool(reunioes_comissao)

# Tools — Agenda (2)
mcp.tool(agenda_plenario)
mcp.tool(agenda_comissoes)

# Tools — Auxiliares (4)
mcp.tool(legislatura_atual)
mcp.tool(tipos_materia_tool)
mcp.tool(partidos_senado)
mcp.tool(ufs_senado)

# Resources (URIs without namespace prefix — mount adds "senado/" automatically)
mcp.resource("data://tipos-materia", mime_type="application/json")(tipos_materia)
mcp.resource("data://info-api", mime_type="application/json")(info_api)
mcp.resource("data://comissoes-permanentes", mime_type="application/json")(comissoes_permanentes)

# Prompts
mcp.prompt(acompanhar_materia)
mcp.prompt(perfil_senador)
mcp.prompt(analise_votacao_senado)
