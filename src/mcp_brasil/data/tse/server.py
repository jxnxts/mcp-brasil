"""TSE feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import analise_candidato, comparativo_eleicao
from .resources import cargos_eleitorais, info_api
from .tools import (
    anos_eleitorais,
    apuracao_status,
    buscar_candidato,
    consultar_prestacao_contas,
    listar_candidatos,
    listar_cargos,
    listar_eleicoes,
    listar_eleicoes_suplementares,
    listar_estados_suplementares,
    listar_municipios_eleitorais,
    mapa_resultado_estados,
    resultado_eleicao,
    resultado_nacional,
    resultado_por_estado,
    resultado_por_municipio,
)

mcp = FastMCP("mcp-brasil-tse")

# Tools — DivulgaCandContas (9)
mcp.tool(anos_eleitorais, tags={"listagem", "eleicoes"})
mcp.tool(listar_eleicoes, tags={"listagem", "eleicoes"})
mcp.tool(listar_eleicoes_suplementares, tags={"listagem", "eleicoes", "suplementares"})
mcp.tool(listar_estados_suplementares, tags={"listagem", "eleicoes", "suplementares"})
mcp.tool(listar_cargos, tags={"listagem", "cargos", "eleicoes"})
mcp.tool(listar_candidatos, tags={"listagem", "candidatos", "eleicoes"})
mcp.tool(buscar_candidato, tags={"detalhe", "candidatos", "eleicoes"})
mcp.tool(resultado_eleicao, tags={"consulta", "resultados", "votos"})
mcp.tool(consultar_prestacao_contas, tags={"consulta", "prestacao-contas", "campanha"})

# Tools — CDN de Resultados (6)
mcp.tool(resultado_nacional, tags={"consulta", "resultados", "votos", "nacional"})
mcp.tool(resultado_por_estado, tags={"consulta", "resultados", "votos", "estados"})
mcp.tool(resultado_por_municipio, tags={"consulta", "resultados", "votos", "municipios"})
mcp.tool(mapa_resultado_estados, tags={"consulta", "resultados", "mapa-eleitoral"})
mcp.tool(apuracao_status, tags={"consulta", "apuracao", "eleicoes"})
mcp.tool(listar_municipios_eleitorais, tags={"listagem", "municipios", "eleicoes"})

# Resources
mcp.resource("data://cargos-eleitorais", mime_type="application/json")(cargos_eleitorais)
mcp.resource("data://info-api", mime_type="application/json")(info_api)

# Prompts
mcp.prompt(analise_candidato)
mcp.prompt(comparativo_eleicao)
