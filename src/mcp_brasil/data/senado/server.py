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
    emendas_materia,
    legislatura_atual,
    listar_blocos,
    listar_comissoes,
    listar_liderancas,
    listar_senadores,
    listar_votacoes,
    membros_comissao,
    partidos_senado,
    relatorias_senador,
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
mcp.tool(listar_senadores, tags={"listagem", "senadores", "parlamentares"})
mcp.tool(buscar_senador, tags={"detalhe", "senadores", "parlamentares"})
mcp.tool(buscar_senador_por_nome, tags={"busca", "senadores", "parlamentares"})
mcp.tool(votacoes_senador, tags={"consulta", "senadores", "votacoes"})

# Tools — Matérias (5)
mcp.tool(buscar_materia, tags={"busca", "materias", "legislacao"})
mcp.tool(detalhe_materia, tags={"detalhe", "materias", "legislacao"})
mcp.tool(consultar_tramitacao_materia, tags={"consulta", "tramitacao", "materias"})
mcp.tool(textos_materia, tags={"consulta", "documentos", "materias"})
mcp.tool(votos_materia, tags={"consulta", "votacoes", "materias"})

# Tools — Votações (3)
mcp.tool(listar_votacoes, tags={"listagem", "votacoes", "plenario"})
mcp.tool(detalhe_votacao, tags={"detalhe", "votacoes", "plenario"})
mcp.tool(votacoes_recentes, tags={"listagem", "votacoes", "plenario"})

# Tools — Comissões (4)
mcp.tool(listar_comissoes, tags={"listagem", "comissoes"})
mcp.tool(detalhe_comissao, tags={"detalhe", "comissoes"})
mcp.tool(membros_comissao, tags={"consulta", "comissoes", "parlamentares"})
mcp.tool(reunioes_comissao, tags={"consulta", "comissoes", "agenda"})

# Tools — Agenda (2)
mcp.tool(agenda_plenario, tags={"consulta", "agenda", "plenario"})
mcp.tool(agenda_comissoes, tags={"consulta", "agenda", "comissoes"})

# Tools — Auxiliares (4)
mcp.tool(legislatura_atual, tags={"consulta", "legislatura"})
mcp.tool(tipos_materia_tool, tags={"listagem", "materias", "tipos"})
mcp.tool(partidos_senado, tags={"listagem", "partidos", "parlamentares"})
mcp.tool(ufs_senado, tags={"listagem", "estados", "parlamentares"})

# Tools — Dados Abertos Extras (4)
mcp.tool(emendas_materia, tags={"consulta", "emendas", "materias"})
mcp.tool(listar_blocos, tags={"listagem", "blocos", "coalizoes"})
mcp.tool(listar_liderancas, tags={"listagem", "liderancas", "parlamentares"})
mcp.tool(relatorias_senador, tags={"consulta", "relatorias", "senadores"})

# Resources (URIs without namespace prefix — mount adds "senado/" automatically)
mcp.resource("data://tipos-materia", mime_type="application/json")(tipos_materia)
mcp.resource("data://info-api", mime_type="application/json")(info_api)
mcp.resource("data://comissoes-permanentes", mime_type="application/json")(comissoes_permanentes)

# Prompts
mcp.prompt(acompanhar_materia)
mcp.prompt(perfil_senador)
mcp.prompt(analise_votacao_senado)
