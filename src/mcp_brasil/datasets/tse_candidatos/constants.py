"""Constants for the tse_candidatos feature."""

# Cargos das eleições municipais 2024
CARGOS_MUNICIPAIS: tuple[str, ...] = ("PREFEITO", "VICE-PREFEITO", "VEREADOR")

# Situação de totalização do turno (resultado) — valores de DS_SIT_TOT_TURNO
SIT_TOTALIZACAO: tuple[str, ...] = (
    "ELEITO",
    "ELEITO POR QP",  # QP = Quociente Partidário
    "ELEITO POR MÉDIA",
    "NÃO ELEITO",
    "SUPLENTE",
    "2º TURNO",
    "RENÚNCIA",
    "FALECIDO",
    "CASSADO",
    "INDEFERIDO",
)

# Colunas permitidas para valores_distintos_candidatos
COLUNAS_DISTINCT_PERMITIDAS: frozenset[str] = frozenset(
    {
        "sg_uf",
        "ds_cargo",
        "sg_partido",
        "ds_genero",
        "ds_grau_instrucao",
        "ds_estado_civil",
        "ds_cor_raca",
        "ds_ocupacao",
        "ds_situacao_candidatura",
        "ds_sit_tot_turno",
        "ds_eleicao",
        "nm_tipo_eleicao",
        "tp_agremiacao",
    }
)
