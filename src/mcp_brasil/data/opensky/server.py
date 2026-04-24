"""OpenSky feature server — registers tools."""

from fastmcp import FastMCP

from .tools import (
    chegadas_aeroporto,
    info_opensky,
    partidas_aeroporto,
    rastrear_aeronave,
    voos_aeronave,
    voos_ao_vivo_brasil,
)

mcp: FastMCP = FastMCP("mcp-brasil-opensky")

mcp.tool(info_opensky, tags={"info", "opensky"})
mcp.tool(voos_ao_vivo_brasil, tags={"live", "opensky", "voos"})
mcp.tool(rastrear_aeronave, tags={"opensky", "rastreamento"})
mcp.tool(partidas_aeroporto, tags={"opensky", "partidas"})
mcp.tool(chegadas_aeroporto, tags={"opensky", "chegadas"})
mcp.tool(voos_aeronave, tags={"opensky", "historico"})
