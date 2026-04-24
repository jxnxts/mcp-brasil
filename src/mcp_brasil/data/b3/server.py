"""B3 feature server."""

from fastmcp import FastMCP

from .prompts import panorama_bolsa
from .resources import catalogo_blue_chips, catalogo_indices
from .tools import (
    blue_chips,
    cotacao_ativo,
    cotacoes_multiplas,
    historico_ativo,
    indices_b3,
    top_ativos_volume,
)

mcp = FastMCP("mcp-brasil-b3")

mcp.tool(cotacao_ativo, tags={"cotacao", "realtime", "acoes"})
mcp.tool(cotacoes_multiplas, tags={"cotacao", "multiplo", "acoes"})
mcp.tool(historico_ativo, tags={"historico", "series-temporais", "acoes"})
mcp.tool(top_ativos_volume, tags={"listagem", "volume", "ranking"})
mcp.tool(indices_b3, tags={"indices", "ibovespa", "ifix"})
mcp.tool(blue_chips, tags={"blue-chips", "acoes-principais"})

mcp.resource("data://indices", mime_type="application/json")(catalogo_indices)
mcp.resource("data://blue-chips", mime_type="application/json")(catalogo_blue_chips)

mcp.prompt(panorama_bolsa)
