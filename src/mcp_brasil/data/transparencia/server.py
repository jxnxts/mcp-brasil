"""Transparência feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import analise_despesas, auditoria_fornecedor, verificacao_compliance
from .resources import bases_sancoes, categorias_beneficios, endpoints_disponiveis, info_api
from .tools import (
    buscar_acordos_leniencia,
    buscar_cartoes_pagamento,
    buscar_contratos,
    buscar_convenios,
    buscar_emendas,
    buscar_licitacoes,
    buscar_notas_fiscais,
    buscar_pep,
    buscar_sancoes,
    buscar_servidores,
    consultar_beneficio_social,
    consultar_bolsa_familia,
    consultar_cnpj,
    consultar_cpf,
    consultar_despesas,
    consultar_viagens,
    detalhar_contrato,
    detalhar_servidor,
)

mcp = FastMCP("mcp-brasil-transparencia")

# Tools
mcp.tool(buscar_contratos, tags={"busca", "contratos", "fornecedores"})
mcp.tool(consultar_despesas, tags={"consulta", "despesas", "orcamento"})
mcp.tool(buscar_servidores, tags={"busca", "servidores", "funcionalismo"})
mcp.tool(buscar_licitacoes, tags={"busca", "licitacoes", "compras"})
mcp.tool(consultar_bolsa_familia, tags={"consulta", "bolsa-familia", "beneficios-sociais"})
mcp.tool(buscar_sancoes, tags={"busca", "sancoes", "compliance", "anticorrupcao"})
mcp.tool(buscar_emendas, tags={"busca", "emendas", "orcamento"})
mcp.tool(consultar_viagens, tags={"consulta", "viagens", "diarias"})
mcp.tool(buscar_convenios, tags={"busca", "convenios", "transferencias"})
mcp.tool(buscar_cartoes_pagamento, tags={"busca", "cartao-corporativo", "despesas"})
mcp.tool(buscar_pep, tags={"busca", "pep", "compliance"})
mcp.tool(buscar_acordos_leniencia, tags={"busca", "leniencia", "anticorrupcao"})
mcp.tool(buscar_notas_fiscais, tags={"busca", "notas-fiscais", "despesas"})
mcp.tool(consultar_beneficio_social, tags={"consulta", "beneficios-sociais", "bpc"})
mcp.tool(consultar_cpf, tags={"consulta", "cpf", "pessoa-fisica"})
mcp.tool(consultar_cnpj, tags={"consulta", "cnpj", "pessoa-juridica"})
mcp.tool(detalhar_contrato, tags={"detalhe", "contratos"})
mcp.tool(detalhar_servidor, tags={"detalhe", "servidores", "remuneracao"})

# Resources (URIs without namespace prefix — mount adds "transparencia/" automatically)
mcp.resource("data://endpoints", mime_type="application/json")(endpoints_disponiveis)
mcp.resource("data://bases-sancoes", mime_type="application/json")(bases_sancoes)
mcp.resource("data://info-api", mime_type="application/json")(info_api)
mcp.resource("data://categorias-beneficios", mime_type="application/json")(categorias_beneficios)

# Prompts
mcp.prompt(auditoria_fornecedor)
mcp.prompt(analise_despesas)
mcp.prompt(verificacao_compliance)
