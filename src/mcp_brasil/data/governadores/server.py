"""Governadores feature server."""

from fastmcp import FastMCP

from .prompts import panorama_executivo_estadual
from .resources import catalogo_ufs
from .tools import (
    consultar_governador,
    governadores_por_partido,
    listar_governadores,
    resumo_por_partido,
)

mcp = FastMCP("mcp-brasil-governadores")

mcp.tool(listar_governadores, tags={"listagem", "governadores"})
mcp.tool(consultar_governador, tags={"detalhe", "governadores"})
mcp.tool(governadores_por_partido, tags={"filtro", "partido"})
mcp.tool(resumo_por_partido, tags={"agregado", "partidos"})

mcp.resource("data://ufs", mime_type="application/json")(catalogo_ufs)

mcp.prompt(panorama_executivo_estadual)
