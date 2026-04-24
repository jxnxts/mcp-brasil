"""tse_fefc feature server."""

from fastmcp import FastMCP

from .tools import (
    fefc_por_partido,
    fefc_por_partido_genero,
    info_tse_fefc,
    valores_distintos_fefc,
)

mcp: FastMCP = FastMCP("mcp-brasil-tse_fefc")

mcp.tool(info_tse_fefc)
mcp.tool(fefc_por_partido)
mcp.tool(fefc_por_partido_genero)
mcp.tool(valores_distintos_fefc)
