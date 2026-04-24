"""tse_bens feature server — registers canned SQL tools."""

from fastmcp import FastMCP

from .prompts import comparar_patrimonio_cargo
from .resources import info_dataset, schema_tabela
from .tools import (
    buscar_bens_candidato,
    info_tse_bens,
    resumo_patrimonio_partido,
    resumo_tipos_bens,
    top_patrimonios_cargo,
)

mcp: FastMCP = FastMCP("mcp-brasil-tse_bens")

mcp.tool(info_tse_bens)
mcp.tool(buscar_bens_candidato)
mcp.tool(top_patrimonios_cargo)
mcp.tool(resumo_patrimonio_partido)
mcp.tool(resumo_tipos_bens)

mcp.resource("data://info", mime_type="application/json")(info_dataset)
mcp.resource("data://schema", mime_type="application/json")(schema_tabela)

mcp.prompt(comparar_patrimonio_cargo)
