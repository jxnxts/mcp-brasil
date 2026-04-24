"""ANTT feature server."""

from fastmcp import FastMCP

from .prompts import analise_acidentes_rodovias
from .resources import catalogo_datasets_chave
from .tools import (
    buscar_datasets_antt,
    datasets_chave_antt,
    detalhe_dataset_antt,
    listar_datasets_antt,
)

mcp = FastMCP("mcp-brasil-antt")

mcp.tool(listar_datasets_antt, tags={"listagem", "catalogo"})
mcp.tool(buscar_datasets_antt, tags={"busca", "catalogo"})
mcp.tool(detalhe_dataset_antt, tags={"detalhe", "recursos"})
mcp.tool(datasets_chave_antt, tags={"listagem", "referencia"})

mcp.resource("data://datasets-chave", mime_type="application/json")(catalogo_datasets_chave)

mcp.prompt(analise_acidentes_rodovias)
