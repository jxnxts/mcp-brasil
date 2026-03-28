"""PNCP sub-server — registers PNCP tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import investigar_fornecedor
from .resources import modalidades_licitacao
from .tools import (
    buscar_atas,
    buscar_atas_atualizadas,
    buscar_contratacoes,
    buscar_contratacoes_abertas,
    buscar_contratacoes_atualizadas,
    buscar_contratos,
    buscar_contratos_atualizados,
    buscar_instrumentos_cobranca,
    buscar_pca,
    buscar_pca_atualizacao,
    buscar_pca_usuario,
    consultar_contratacao_detalhe,
    consultar_fornecedor,
    consultar_orgao,
)

mcp = FastMCP("pncp")

# Tools — publicação
mcp.tool(buscar_contratacoes, tags={"busca", "contratacoes", "licitacoes"})
mcp.tool(buscar_contratos, tags={"busca", "contratos", "compras"})
mcp.tool(buscar_atas, tags={"busca", "atas", "registro-preco"})
mcp.tool(consultar_fornecedor, tags={"consulta", "fornecedores", "compras"})
mcp.tool(consultar_orgao, tags={"consulta", "orgaos", "compras"})

# Tools — propostas abertas e atualizações
mcp.tool(buscar_contratacoes_abertas, tags={"busca", "contratacoes", "propostas"})
mcp.tool(buscar_contratacoes_atualizadas, tags={"busca", "contratacoes", "atualizacao"})
mcp.tool(buscar_contratos_atualizados, tags={"busca", "contratos", "atualizacao"})
mcp.tool(buscar_atas_atualizadas, tags={"busca", "atas", "atualizacao"})
mcp.tool(consultar_contratacao_detalhe, tags={"consulta", "contratacoes", "detalhe"})

# Tools — PCA (Plano de Contratações Anual)
mcp.tool(buscar_pca, tags={"busca", "pca", "planejamento"})
mcp.tool(buscar_pca_atualizacao, tags={"busca", "pca", "atualizacao"})
mcp.tool(buscar_pca_usuario, tags={"busca", "pca", "usuario"})

# Tools — instrumentos de cobrança
mcp.tool(buscar_instrumentos_cobranca, tags={"busca", "notas-fiscais", "cobranca"})

# Resources
mcp.resource("data://modalidades", mime_type="application/json")(modalidades_licitacao)

# Prompts
mcp.prompt(investigar_fornecedor)
