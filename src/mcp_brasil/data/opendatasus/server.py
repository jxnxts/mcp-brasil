"""OpenDataSUS feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import pesquisa_epidemiologica
from .resources import datasets_conhecidos, tags_comuns
from .tools import (
    buscar_com_filtro,
    buscar_datasets,
    consultar_datastore,
    detalhar_dataset,
    listar_datasets_conhecidos,
)

mcp = FastMCP("mcp-brasil-opendatasus")

# Tools (5)
mcp.tool(buscar_datasets, tags={"busca", "datasets", "opendatasus"})
mcp.tool(detalhar_dataset, tags={"consulta", "dataset", "detalhes"})
mcp.tool(consultar_datastore, tags={"consulta", "datastore", "registros"})
mcp.tool(listar_datasets_conhecidos, tags={"listagem", "datasets", "referencia"})
mcp.tool(buscar_com_filtro, tags={"busca", "filtro", "datastore"})

# Resources (URIs without namespace prefix — mount adds "opendatasus/" automatically)
mcp.resource("data://datasets-conhecidos", mime_type="application/json")(datasets_conhecidos)
mcp.resource("data://tags-comuns", mime_type="application/json")(tags_comuns)

# Prompts
mcp.prompt(pesquisa_epidemiologica)
