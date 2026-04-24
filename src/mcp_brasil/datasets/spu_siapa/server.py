"""spu_siapa feature server — registers canned SQL tools backed by DuckDB."""

from fastmcp import FastMCP

from .prompts import auditoria_patrimonio_uf, imoveis_aforamento_rio
from .resources import catalogo_valores, info_dataset, schema_tabela
from .tools import (
    buscar_imoveis_siapa,
    info_spu_siapa,
    refrescar_spu_siapa,
    resumo_conceituacao_siapa,
    resumo_regime_siapa,
    resumo_uf_siapa,
    top_municipios_siapa,
)

mcp: FastMCP = FastMCP("mcp-brasil-spu_siapa")

mcp.tool(info_spu_siapa)
mcp.tool(buscar_imoveis_siapa)
mcp.tool(resumo_regime_siapa)
mcp.tool(resumo_conceituacao_siapa)
mcp.tool(resumo_uf_siapa)
mcp.tool(top_municipios_siapa)
mcp.tool(refrescar_spu_siapa)

mcp.resource("data://schema", mime_type="application/json")(schema_tabela)
mcp.resource("data://valores", mime_type="application/json")(catalogo_valores)
mcp.resource("data://info", mime_type="application/json")(info_dataset)

mcp.prompt(auditoria_patrimonio_uf)
mcp.prompt(imoveis_aforamento_rio)
