"""tse_votacao feature server — registers canned SQL tools."""

from fastmcp import FastMCP

from .prompts import briefing_municipio, evolucao_partido_cargo
from .resources import info_dataset, schema_tabela
from .tools import (
    evolucao_partido,
    info_tse_votacao,
    ranking_municipio,
    soma_votos_uf,
    top_votados_cargo,
    votos_candidato,
)

mcp: FastMCP = FastMCP("mcp-brasil-tse_votacao")

mcp.tool(info_tse_votacao)
mcp.tool(votos_candidato)
mcp.tool(top_votados_cargo)
mcp.tool(ranking_municipio)
mcp.tool(evolucao_partido)
mcp.tool(soma_votos_uf)

mcp.resource("data://info", mime_type="application/json")(info_dataset)
mcp.resource("data://schema", mime_type="application/json")(schema_tabela)

mcp.prompt(evolucao_partido_cargo)
mcp.prompt(briefing_municipio)
