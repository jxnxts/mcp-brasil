"""anac_rab feature server."""

from fastmcp import FastMCP

from .tools import (
    aeronaves_por_operador,
    aeronaves_por_uf,
    consultar_aeronave,
    info_anac_rab,
    top_fabricantes,
    valores_distintos_rab,
)

mcp: FastMCP = FastMCP("mcp-brasil-anac_rab")

mcp.tool(info_anac_rab)
mcp.tool(consultar_aeronave)
mcp.tool(aeronaves_por_operador)
mcp.tool(top_fabricantes)
mcp.tool(aeronaves_por_uf)
mcp.tool(valores_distintos_rab)
