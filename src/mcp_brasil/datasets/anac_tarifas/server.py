"""anac_tarifas feature server."""

from fastmcp import FastMCP

from .tools import (
    evolucao_preco_empresa,
    info_anac_tarifas,
    preco_medio_rota,
    preco_por_empresa,
    top_rotas_caras,
    valores_distintos_tarifas,
)

mcp: FastMCP = FastMCP("mcp-brasil-anac_tarifas")

mcp.tool(info_anac_tarifas)
mcp.tool(preco_medio_rota)
mcp.tool(preco_por_empresa)
mcp.tool(top_rotas_caras)
mcp.tool(evolucao_preco_empresa)
mcp.tool(valores_distintos_tarifas)
