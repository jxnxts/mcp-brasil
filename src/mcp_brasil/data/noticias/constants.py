"""Constants for noticias feature — catálogo de feeds RSS."""

from __future__ import annotations

# Fontes agrupadas por categoria
FEEDS_POLITICA: dict[str, str] = {
    "camara_ultimas": "https://www.camara.leg.br/noticias/rss/ultimas-noticias",
    "senado_ultimas": "https://www12.senado.leg.br/noticias/rss.xml",
    "agencia_brasil_politica": "https://agenciabrasil.ebc.com.br/rss/politica/feed.xml",
    "agencia_brasil_geral": "https://agenciabrasil.ebc.com.br/rss/geral/feed.xml",
    "agencia_brasil_justica": "https://agenciabrasil.ebc.com.br/rss/justica/feed.xml",
}

FEEDS_ECONOMIA: dict[str, str] = {
    "agencia_brasil_economia": "https://agenciabrasil.ebc.com.br/rss/economia/feed.xml",
    "bcb_noticias": "https://www.bcb.gov.br/api/feed/app/conteudo/ultimasnoticias/pt-br",
}

FEEDS_TEMAS_CAMARA: dict[str, str] = {
    "eleicoes": "https://www.camara.leg.br/noticias/rss/dinamico/ELEICOES",
    "administracao_publica": (
        "https://www.camara.leg.br/noticias/rss/dinamico/ADMINISTRACAO-PUBLICA"
    ),
    "economia": "https://www.camara.leg.br/noticias/rss/dinamico/ECONOMIA",
    "educacao": "https://www.camara.leg.br/noticias/rss/dinamico/EDUCACAO-CULTURA-E-ESPORTES",
    "seguranca": "https://www.camara.leg.br/noticias/rss/dinamico/SEGURANCA",
    "saude": "https://www.camara.leg.br/noticias/rss/dinamico/SAUDE",
    "meio_ambiente": "https://www.camara.leg.br/noticias/rss/dinamico/MEIO-AMBIENTE",
}

# Consolidado — usado por listar_fontes
TODAS_FONTES = {**FEEDS_POLITICA, **FEEDS_ECONOMIA, **FEEDS_TEMAS_CAMARA}
