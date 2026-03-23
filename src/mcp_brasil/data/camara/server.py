"""Câmara feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import acompanhar_proposicao, analise_votacao, perfil_deputado
from .resources import info_api, legislaturas_recentes, tipos_proposicao
from .tools import (
    agenda_legislativa,
    buscar_comissoes,
    buscar_deputado,
    buscar_proposicao,
    buscar_votacao,
    consultar_tramitacao,
    despesas_deputado,
    frentes_parlamentares,
    listar_deputados,
    votos_nominais,
)

mcp = FastMCP("mcp-brasil-camara")

# Tools (10)
mcp.tool(listar_deputados, tags={"listagem", "deputados", "parlamentares"})
mcp.tool(buscar_deputado, tags={"detalhe", "deputados", "parlamentares"})
mcp.tool(buscar_proposicao, tags={"busca", "proposicoes", "legislacao"})
mcp.tool(consultar_tramitacao, tags={"consulta", "tramitacao", "proposicoes"})
mcp.tool(buscar_votacao, tags={"busca", "votacoes", "plenario"})
mcp.tool(votos_nominais, tags={"detalhe", "votacoes", "plenario"})
mcp.tool(despesas_deputado, tags={"consulta", "despesas", "cota-parlamentar"})
mcp.tool(agenda_legislativa, tags={"consulta", "agenda", "sessoes"})
mcp.tool(buscar_comissoes, tags={"busca", "comissoes", "cpi"})
mcp.tool(frentes_parlamentares, tags={"listagem", "frentes", "parlamentares"})

# Resources (URIs without namespace prefix — mount adds "camara/" automatically)
mcp.resource("data://tipos-proposicao", mime_type="application/json")(tipos_proposicao)
mcp.resource("data://legislaturas", mime_type="application/json")(legislaturas_recentes)
mcp.resource("data://info-api", mime_type="application/json")(info_api)

# Prompts
mcp.prompt(acompanhar_proposicao)
mcp.prompt(perfil_deputado)
mcp.prompt(analise_votacao)
