"""Static reference data for the spu_siapa feature."""

from __future__ import annotations

import json

from . import DATASET_SPEC
from .constants import CLASSES, CONCEITUACOES, REGIMES_COMUNS


def schema_tabela() -> str:
    """Schema da tabela imoveis_siapa (após normalização em DuckDB)."""
    cols = [
        {"name": "classe", "tipo": "VARCHAR", "desc": "Dominial ou Uso Especial"},
        {"name": "rip_imovel", "tipo": "BIGINT", "desc": "RIP do imóvel (13 dígitos)"},
        {"name": "rip_utilizacao", "tipo": "VARCHAR", "desc": "Nº de utilização/subitem"},
        {
            "name": "data_cadastro",
            "tipo": "VARCHAR",
            "desc": "Data de cadastro (mascarada com ###)",
        },
        {"name": "uf", "tipo": "VARCHAR", "desc": "Sigla UF"},
        {"name": "municipio", "tipo": "VARCHAR", "desc": "Município"},
        {"name": "endereco", "tipo": "VARCHAR", "desc": "Endereço completo"},
        {"name": "bairro", "tipo": "VARCHAR", "desc": "Bairro"},
        {"name": "latitude", "tipo": "DOUBLE", "desc": "Latitude (graus decimais)"},
        {"name": "longitude", "tipo": "DOUBLE", "desc": "Longitude"},
        {"name": "nivel_precisao", "tipo": "VARCHAR", "desc": "Fonte da geolocalização"},
        {
            "name": "conceituacao_terreno",
            "tipo": "VARCHAR",
            "desc": "Marinha / Marginal / Interior / Ilha",
        },
        {"name": "tipo_imovel", "tipo": "VARCHAR", "desc": "Categoria do imóvel"},
        {
            "name": "regime_utilizacao",
            "tipo": "VARCHAR",
            "desc": "Aforamento / Ocupação / Uso em Serviço Público / Cessão",
        },
        {
            "name": "proprietario_oficial",
            "tipo": "VARCHAR",
            "desc": "Entidade federal titular (União, autarquia, etc.)",
        },
        {"name": "data_inicio_utilizacao", "tipo": "VARCHAR", "desc": "Início da utilização"},
        {"name": "area_terreno_m2", "tipo": "DOUBLE", "desc": "Área do terreno total (m²)"},
        {"name": "area_uniao_m2", "tipo": "DOUBLE", "desc": "Área da União no imóvel (m²)"},
    ]
    return json.dumps(
        {
            "tabela": DATASET_SPEC.table,
            "colunas": cols,
            "total_linhas_esperado": "~787.000",
            "origem": DATASET_SPEC.source,
        },
        ensure_ascii=False,
        indent=2,
    )


def catalogo_valores() -> str:
    """Valores comuns nos campos categóricos (regime, conceituação, classe)."""
    return json.dumps(
        {
            "regimes_comuns": list(REGIMES_COMUNS),
            "conceituacoes": list(CONCEITUACOES),
            "classes": list(CLASSES),
        },
        ensure_ascii=False,
        indent=2,
    )


def info_dataset() -> str:
    """Metadados do dataset e orientações de uso."""
    info = {
        "id": DATASET_SPEC.id,
        "url": DATASET_SPEC.url,
        "tamanho_aproximado": f"{DATASET_SPEC.approx_size_mb} MB",
        "ttl_dias": DATASET_SPEC.ttl_days,
        "fonte": DATASET_SPEC.source,
        "ativacao": "Defina MCP_BRASIL_DATASETS=spu_siapa no seu .env",
        "primeira_consulta": (
            "A primeira tool executada dispara download (~1-3 min). "
            "Subsequentes usam cache local DuckDB em ms."
        ),
        "cobertura": (
            "~787k imóveis da União — Dominiais (aforamento/ocupação com "
            "particulares) + Uso Especial (órgãos federais). Cobertura "
            "superior ao feature spu_imoveis (Raio-X APF, 54k imóveis)."
        ),
        "lgpd": "Dataset não contém CPF/CNPJ (endereços e RIPs apenas).",
    }
    return json.dumps(info, ensure_ascii=False, indent=2)
