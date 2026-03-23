"""Dados Abertos sub-server — registers Compras.gov.br tools.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .tools import (
    buscar_contratos,
    buscar_dispensas,
    buscar_licitacoes,
    buscar_material_catmat,
    buscar_pregoes,
    buscar_servico_catser,
    buscar_uasg,
    consultar_fornecedor,
)

mcp = FastMCP("dadosabertos")

# Tools
mcp.tool(buscar_licitacoes)
mcp.tool(buscar_pregoes)
mcp.tool(buscar_dispensas)
mcp.tool(buscar_contratos)
mcp.tool(consultar_fornecedor)
mcp.tool(buscar_material_catmat)
mcp.tool(buscar_servico_catser)
mcp.tool(buscar_uasg)
