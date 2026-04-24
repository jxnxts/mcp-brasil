"""Constants for ISP-RJ dataset."""

from __future__ import annotations

# ISP-RJ publica CSV mensalmente atualizado, histórico desde 1991.
# Fonte: https://www.ispdados.rj.gov.br/estatistica.html
ISP_CSV_URL = "https://www.ispdados.rj.gov.br/arquivos/BaseDPEvolucaoMensalCisp.csv"

COLUNAS_DISTINCT_PERMITIDAS: frozenset[str] = frozenset(
    {"cisp", "aisp", "risp", "munic", "mcirc", "regiao", "ano", "mes"}
)

# Indicadores destacados (não exaustivo — a base tem 60+ colunas)
INDICADORES_PRINCIPAIS: tuple[str, ...] = (
    "hom_doloso",
    "lesao_corp_morte",
    "latrocinio",
    "cvli",
    "hom_por_interv_policial",
    "feminicidio",
    "letalidade_violenta",
    "tentat_hom",
    "lesao_corp_dolosa",
    "estupro",
    "hom_culposo",
    "lesao_corp_culposa",
    "total_roubos",
    "roubo_veiculo",
    "roubo_carga",
    "roubo_comercio",
    "roubo_residencia",
    "total_furtos",
    "furto_veiculos",
    "sequestro",
    "extorsao",
    "apreensao_drogas",
    "apreensao_drogas_sem_autor",
    "recuperacao_veiculos",
)
