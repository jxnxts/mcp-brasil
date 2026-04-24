"""MJ feature server."""

from fastmcp import FastMCP

from .prompts import analise_criminalidade_nacional, analise_sistema_prisional
from .resources import catalogo_datasets_chave
from .tools import (
    buscar_datasets_mj,
    datasets_chave_mj,
    detalhe_dataset_mj,
    listar_datasets_mj,
)

mcp = FastMCP("mcp-brasil-mj")

mcp.tool(listar_datasets_mj, tags={"listagem", "catalogo"})
mcp.tool(buscar_datasets_mj, tags={"busca", "catalogo"})
mcp.tool(detalhe_dataset_mj, tags={"detalhe", "recursos"})
mcp.tool(datasets_chave_mj, tags={"listagem", "referencia"})

mcp.resource("data://datasets-chave", mime_type="application/json")(catalogo_datasets_chave)

mcp.prompt(analise_criminalidade_nacional)
mcp.prompt(analise_sistema_prisional)
