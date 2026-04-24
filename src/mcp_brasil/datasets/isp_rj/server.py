"""isp_rj feature server."""

from fastmcp import FastMCP

from .prompts import panorama_criminalidade_rj
from .resources import catalogo_indicadores, info_dataset
from .tools import (
    indicadores_municipio,
    info_isp_rj,
    ranking_municipios,
    refrescar_isp_rj,
    serie_temporal,
    valores_distintos_isp,
)

mcp: FastMCP = FastMCP("mcp-brasil-isp_rj")

mcp.tool(info_isp_rj)
mcp.tool(valores_distintos_isp)
mcp.tool(indicadores_municipio)
mcp.tool(ranking_municipios)
mcp.tool(serie_temporal)
mcp.tool(refrescar_isp_rj)

mcp.resource("data://info", mime_type="application/json")(info_dataset)
mcp.resource("data://indicadores", mime_type="application/json")(catalogo_indicadores)

mcp.prompt(panorama_criminalidade_rj)
