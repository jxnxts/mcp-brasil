"""Analysis prompts for the spu_siapa dataset feature."""

from __future__ import annotations


def auditoria_patrimonio_uf(uf: str) -> str:
    """Auditoria do patrimônio da União em uma UF via SIAPA.

    Args:
        uf: Sigla da UF (ex: 'RJ', 'SP', 'DF').
    """
    return (
        f"Faça uma auditoria do patrimônio da União em {uf} usando o dataset SIAPA:\n\n"
        "1. **Estado do cache:** `info_spu_siapa()` — confirme que o dataset está local.\n"
        f"2. **Panorama por UF:** `resumo_uf_siapa()` e destaque a linha de {uf}.\n"
        f"3. **Distribuição de regimes:** `resumo_regime_siapa(uf='{uf}')` — "
        "separe aforamento (foreiros privados), ocupação (precária), uso em serviço "
        "público (órgãos federais) e cessão.\n"
        f"4. **Conceituação do terreno:** `resumo_conceituacao_siapa(uf='{uf}')` — "
        "proporção de marinha vs marginal vs interior.\n"
        f"5. **Concentração municipal:** `top_municipios_siapa('{uf}', top=10)`.\n"
        "6. Consolide achados destacando anomalias (regimes raros, concentrações "
        "geográficas inesperadas, áreas desproporcionais)."
    )


def imoveis_aforamento_rio(municipio: str = "Rio de Janeiro") -> str:
    """Investiga imóveis em aforamento (foreiros privados) num município costeiro.

    Args:
        municipio: Nome do município litorâneo a investigar.
    """
    return (
        f"Investigue imóveis em aforamento em {municipio} (foreiros privados "
        "pagando foro anual à União):\n\n"
        "1. Chame `buscar_imoveis_siapa(uf='RJ', "
        f"municipio='{municipio}', regime='Aforamento', limite=50)` para "
        "listar os imóveis.\n"
        "2. Filtre mentalmente por conceituação 'Marinha' — esses são os "
        "clássicos imóveis em terreno de marinha com foro 0,6% do valor de "
        "domínio pleno.\n"
        "3. Agrupe por endereço/bairro e destaque áreas significativas.\n"
        "4. Para imóveis com coordenadas, opcionalmente cruze com "
        "`spu_geo_consultar_ponto_spu` para validação geoespacial da "
        "demarcação de marinha.\n"
        "5. Reporte: (a) total de imóveis em aforamento; (b) área total da "
        "União comprometida; (c) distribuição por bairro."
    )
