"""tse_redes_sociais feature server."""

from fastmcp import FastMCP

from .tools import (
    info_tse_redes_sociais,
    redes_do_candidato,
    redes_por_partido,
    top_redes_por_ano,
)

mcp: FastMCP = FastMCP("mcp-brasil-tse_redes_sociais")

mcp.tool(info_tse_redes_sociais)
mcp.tool(redes_do_candidato)
mcp.tool(redes_por_partido)
mcp.tool(top_redes_por_ano)
