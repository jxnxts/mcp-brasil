"""anac_pontualidade feature server."""

from fastmcp import FastMCP

from .tools import (
    consultar_voo_pontualidade,
    info_anac_pontualidade,
    pontualidade_aeroporto_partida,
    ranking_empresas_atraso,
    rotas_mais_atrasadas,
)

mcp: FastMCP = FastMCP("mcp-brasil-anac_pontualidade")

mcp.tool(info_anac_pontualidade)
mcp.tool(ranking_empresas_atraso)
mcp.tool(rotas_mais_atrasadas)
mcp.tool(pontualidade_aeroporto_partida)
mcp.tool(consultar_voo_pontualidade)
