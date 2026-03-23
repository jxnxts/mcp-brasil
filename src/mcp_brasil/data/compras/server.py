"""Compras feature server — composes sub-servers for each procurement source.

Uses FastMCP mount() to namespace tools from each data source:
- pncp: Portal Nacional de Contratações Públicas (Lei 14.133/2021)
- dadosabertos: Dados Abertos Compras.gov.br (SIASG/ComprasNet)

This file only composes sub-servers. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .dadosabertos.server import mcp as dadosabertos_mcp
from .pncp.server import mcp as pncp_mcp

mcp = FastMCP("mcp-brasil-compras")

# Mount sub-sources with namespace
mcp.mount(pncp_mcp, namespace="pncp")
mcp.mount(dadosabertos_mcp, namespace="dadosabertos")
