"""IBGE feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import comparativo_regional, resumo_estado
from .resources import estados_brasileiros, niveis_territoriais, regioes_brasileiras
from .tools import (
    buscar_cnae,
    buscar_municipios,
    consultar_agregado,
    consultar_nome,
    listar_estados,
    listar_pesquisas,
    listar_regioes,
    obter_malha,
    ranking_nomes,
)

mcp = FastMCP("mcp-brasil-ibge")

# Tools
mcp.tool(listar_estados, tags={"listagem", "estados", "geografia"})
mcp.tool(buscar_municipios, tags={"busca", "municipios", "geografia"})
mcp.tool(listar_regioes, tags={"listagem", "regioes", "geografia"})
mcp.tool(consultar_nome, tags={"consulta", "nomes", "censo", "demografia"})
mcp.tool(ranking_nomes, tags={"listagem", "nomes", "censo", "demografia"})
mcp.tool(consultar_agregado, tags={"consulta", "indicadores", "populacao", "pib"})
mcp.tool(listar_pesquisas, tags={"listagem", "pesquisas", "agregados"})
mcp.tool(obter_malha, tags={"consulta", "malha", "geografia", "geojson"})
mcp.tool(buscar_cnae, tags={"busca", "cnae", "atividade-economica"})

# Resources (URIs without namespace prefix — mount adds "ibge/" automatically)
mcp.resource("data://estados", mime_type="application/json")(estados_brasileiros)
mcp.resource("data://regioes", mime_type="application/json")(regioes_brasileiras)
mcp.resource("data://niveis-territoriais", mime_type="application/json")(niveis_territoriais)

# Prompts
mcp.prompt(resumo_estado)
mcp.prompt(comparativo_regional)
