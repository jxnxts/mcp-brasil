"""Noticias feature server."""

from fastmcp import FastMCP

from .prompts import panorama_dia
from .resources import catalogo_fontes
from .tools import buscar_noticias, listar_fontes, resumo_politica, ultimas_noticias

mcp = FastMCP("mcp-brasil-noticias")

mcp.tool(listar_fontes, tags={"listagem", "rss", "catalogo"})
mcp.tool(ultimas_noticias, tags={"rss", "noticias"})
mcp.tool(buscar_noticias, tags={"rss", "busca"})
mcp.tool(resumo_politica, tags={"rss", "politica", "resumo"})

mcp.resource("data://fontes", mime_type="application/json")(catalogo_fontes)

mcp.prompt(panorama_dia)
