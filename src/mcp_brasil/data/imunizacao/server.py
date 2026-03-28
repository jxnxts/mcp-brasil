"""Imunização (PNI) feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import analise_cobertura_vacinal
from .resources import calendario_nacional, metas_cobertura_vacinal
from .tools import (
    buscar_datasets_pni,
    buscar_vacinacao,
    calendario_vacinacao,
    consultar_doses_dataset,
    consultar_vacina,
    estatisticas_por_faixa_etaria,
    estatisticas_por_vacina,
    listar_vacinas_sus,
    metas_cobertura,
    verificar_esquema_vacinal,
)

mcp = FastMCP("mcp-brasil-imunizacao")

# Tools (10)
mcp.tool(buscar_vacinacao, tags={"busca", "vacinacao", "registros", "elasticsearch"})
mcp.tool(estatisticas_por_vacina, tags={"estatisticas", "vacinacao", "agregacao"})
mcp.tool(estatisticas_por_faixa_etaria, tags={"estatisticas", "faixa_etaria", "agregacao"})
mcp.tool(buscar_datasets_pni, tags={"busca", "datasets", "pni", "opendatasus"})
mcp.tool(consultar_doses_dataset, tags={"consulta", "doses", "dataset", "pni"})
mcp.tool(calendario_vacinacao, tags={"calendario", "vacinacao", "referencia"})
mcp.tool(listar_vacinas_sus, tags={"listagem", "vacinas", "sus"})
mcp.tool(consultar_vacina, tags={"consulta", "vacina", "detalhes"})
mcp.tool(verificar_esquema_vacinal, tags={"verificacao", "esquema", "idade"})
mcp.tool(metas_cobertura, tags={"metas", "cobertura", "ministerio_saude"})

# Resources (URIs without namespace — mount adds "imunizacao/" automatically)
mcp.resource("data://calendario-nacional", mime_type="application/json")(calendario_nacional)
mcp.resource("data://metas-cobertura", mime_type="application/json")(metas_cobertura_vacinal)

# Prompts
mcp.prompt(analise_cobertura_vacinal)
