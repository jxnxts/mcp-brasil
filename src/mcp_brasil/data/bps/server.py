"""BPS feature server — registers tools.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .tools import (
    buscar_catmat_bps,
    buscar_medicamento_bps,
    consultar_precos_saude,
)

mcp = FastMCP("mcp-brasil-bps")

# Tools
mcp.tool(consultar_precos_saude, tags={"bps", "saude", "precos"})
mcp.tool(buscar_medicamento_bps, tags={"bps", "medicamentos", "busca"})
mcp.tool(buscar_catmat_bps, tags={"bps", "catmat", "busca"})
