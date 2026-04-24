"""tse_candidatos feature server — registers canned SQL tools."""

from fastmcp import FastMCP

from .prompts import analise_partido_2024, perfil_demografico_cargo
from .resources import catalogo_valores, info_dataset, schema_tabela
from .tools import (
    buscar_candidatos,
    info_tse_candidatos,
    refrescar_tse_candidatos,
    resumo_cargo_partido,
    resumo_perfil_eleitos,
    top_municipios_candidatos,
    valores_distintos_candidatos,
)

mcp: FastMCP = FastMCP("mcp-brasil-tse_candidatos")

mcp.tool(info_tse_candidatos)
mcp.tool(valores_distintos_candidatos)
mcp.tool(buscar_candidatos)
mcp.tool(resumo_cargo_partido)
mcp.tool(resumo_perfil_eleitos)
mcp.tool(top_municipios_candidatos)
mcp.tool(refrescar_tse_candidatos)

mcp.resource("data://info", mime_type="application/json")(info_dataset)
mcp.resource("data://valores", mime_type="application/json")(catalogo_valores)
mcp.resource("data://schema", mime_type="application/json")(schema_tabela)

mcp.prompt(analise_partido_2024)
mcp.prompt(perfil_demografico_cargo)
