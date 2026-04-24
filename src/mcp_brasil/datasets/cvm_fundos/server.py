"""cvm_fundos feature server."""

from fastmcp import FastMCP

from .prompts import panorama_fundos
from .resources import info_dataset
from .tools import (
    buscar_fundo,
    detalhe_fundo,
    info_cvm_fundos,
    refrescar_cvm_fundos,
    top_fundos_por_pl,
    valores_distintos_cvm,
)

mcp: FastMCP = FastMCP("mcp-brasil-cvm_fundos")

mcp.tool(info_cvm_fundos)
mcp.tool(valores_distintos_cvm)
mcp.tool(buscar_fundo)
mcp.tool(detalhe_fundo)
mcp.tool(top_fundos_por_pl)
mcp.tool(refrescar_cvm_fundos)

mcp.resource("data://info", mime_type="application/json")(info_dataset)

mcp.prompt(panorama_fundos)
