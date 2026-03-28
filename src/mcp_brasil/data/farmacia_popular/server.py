"""Farmácia Popular feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import assistente_farmacia_popular
from .resources import catalogo_medicamentos, indicacoes_terapeuticas
from .tools import (
    buscar_farmacias,
    buscar_por_indicacao,
    estatisticas_programa,
    listar_medicamentos,
    verificar_elegibilidade,
    verificar_medicamento,
)

mcp = FastMCP("mcp-brasil-farmacia-popular")

# Tools (6)
mcp.tool(buscar_farmacias, tags={"busca", "farmacias", "estabelecimentos"})
mcp.tool(listar_medicamentos, tags={"listagem", "medicamentos", "gratuitos"})
mcp.tool(verificar_medicamento, tags={"consulta", "medicamento", "verificacao"})
mcp.tool(buscar_por_indicacao, tags={"busca", "medicamentos", "indicacao", "doenca"})
mcp.tool(estatisticas_programa, tags={"estatisticas", "programa", "resumo"})
mcp.tool(verificar_elegibilidade, tags={"elegibilidade", "requisitos", "documentos"})

# Resources (URIs without namespace prefix — mount adds "farmacia_popular/" automatically)
mcp.resource("data://catalogo-medicamentos", mime_type="application/json")(catalogo_medicamentos)
mcp.resource("data://indicacoes-terapeuticas", mime_type="application/json")(
    indicacoes_terapeuticas
)

# Prompts
mcp.prompt(assistente_farmacia_popular)
