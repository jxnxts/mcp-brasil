"""Bacen feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import analise_economica, comparar_indicadores
from .resources import catalogo_series, categorias_series, indicadores_chave
from .tools import (
    buscar_serie,
    calcular_variacao,
    comparar_series,
    consultar_serie,
    expectativas_focus,
    indicadores_atuais,
    metadados_serie,
    series_populares,
    ultimos_valores,
)

mcp = FastMCP("mcp-brasil-bacen")

# Tools
mcp.tool(consultar_serie, tags={"consulta", "series-temporais", "indicadores"})
mcp.tool(ultimos_valores, tags={"consulta", "series-temporais", "indicadores"})
mcp.tool(metadados_serie, tags={"detalhe", "series-temporais", "metadados"})
mcp.tool(series_populares, tags={"listagem", "series-temporais", "catalogo"})
mcp.tool(buscar_serie, tags={"busca", "series-temporais", "catalogo"})
mcp.tool(indicadores_atuais, tags={"consulta", "indicadores", "selic", "ipca", "cambio"})
mcp.tool(calcular_variacao, tags={"calculo", "series-temporais", "variacao"})
mcp.tool(comparar_series, tags={"comparacao", "series-temporais", "indicadores"})
mcp.tool(expectativas_focus, tags={"consulta", "expectativas", "focus", "projecoes"})

# Resources (URIs without namespace prefix — mount adds "bacen/" automatically)
mcp.resource("data://catalogo", mime_type="application/json")(catalogo_series)
mcp.resource("data://categorias", mime_type="application/json")(categorias_series)
mcp.resource("data://indicadores-chave", mime_type="application/json")(indicadores_chave)

# Prompts
mcp.prompt(analise_economica)
mcp.prompt(comparar_indicadores)
