"""Feature tse_candidatos — registro completo de candidatos das eleições de 2024.

Dataset consolidado do TSE (consulta_cand_2024) com todos os candidatos que
pediram registro na Justiça Eleitoral em 2024 — eleições municipais (prefeito,
vice-prefeito, vereador) mais suplementares. ~500k linhas, ~63MB ZIP → ~243MB
CSV descompactado.

Ativação: ``MCP_BRASIL_DATASETS=tse_candidatos`` no ``.env``.
"""

from mcp_brasil import settings
from mcp_brasil._shared.datasets import DatasetSpec
from mcp_brasil._shared.feature import FeatureMeta

DATASET_ID = "tse_candidatos"
DATASET_TABLE = "candidatos_2024"

DATASET_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2024.zip"
ZIP_MEMBER = "consulta_cand_2024_BRASIL.csv"

# Nomes normalizados (snake_case, sem prefixos TSE). A ordem segue o header.
_COLUMN_NAMES: list[str] = [
    "dt_geracao",
    "hh_geracao",
    "ano_eleicao",
    "cd_tipo_eleicao",
    "nm_tipo_eleicao",
    "nr_turno",
    "cd_eleicao",
    "ds_eleicao",
    "dt_eleicao",
    "tp_abrangencia",
    "sg_uf",
    "sg_ue",
    "nm_ue",
    "cd_cargo",
    "ds_cargo",
    "sq_candidato",
    "nr_candidato",
    "nm_candidato",
    "nm_urna_candidato",
    "nm_social_candidato",
    "nr_cpf_candidato",
    "ds_email",
    "cd_situacao_candidatura",
    "ds_situacao_candidatura",
    "tp_agremiacao",
    "nr_partido",
    "sg_partido",
    "nm_partido",
    "nr_federacao",
    "nm_federacao",
    "sg_federacao",
    "ds_composicao_federacao",
    "sq_coligacao",
    "nm_coligacao",
    "ds_composicao_coligacao",
    "sg_uf_nascimento",
    "dt_nascimento",
    "nr_titulo_eleitoral_candidato",
    "cd_genero",
    "ds_genero",
    "cd_grau_instrucao",
    "ds_grau_instrucao",
    "cd_estado_civil",
    "ds_estado_civil",
    "cd_cor_raca",
    "ds_cor_raca",
    "cd_ocupacao",
    "ds_ocupacao",
    "cd_sit_tot_turno",
    "ds_sit_tot_turno",
]


DATASET_SPEC = DatasetSpec(
    id=DATASET_ID,
    url=DATASET_URL,
    table=DATASET_TABLE,
    ttl_days=30,
    approx_size_mb=63,
    source="TSE — Portal de Dados Abertos (consulta_cand_2024)",
    description=(
        "Candidatos das eleições municipais 2024 (prefeito, vice, vereador) — "
        "dados cadastrais, partido, resultado, gênero, escolaridade, ocupação."
    ),
    zip_member=ZIP_MEMBER,
    source_encoding="cp1252",
    csv_options={
        "delim": ";",
        "header": False,
        "skip": 1,
        "quote": '"',
        "ignore_errors": True,
        "sample_size": -1,
        "nullstr": ["#NULO", "#NE", "-4", "-3", "-1"],
        "names": _COLUMN_NAMES,
        "dtypes": {
            "ano_eleicao": "INTEGER",
            "nr_turno": "INTEGER",
            "nr_candidato": "INTEGER",
            "cd_cargo": "INTEGER",
            "nr_partido": "INTEGER",
        },
    },
    # PII: CPF + título eleitoral + email são sensíveis
    pii_columns=frozenset({"nr_cpf_candidato", "nr_titulo_eleitoral_candidato", "ds_email"}),
)

FEATURE_META = FeatureMeta(
    name=DATASET_ID,
    description=(
        "TSE candidatos 2024 — ~500k registros com consulta SQL via DuckDB. "
        "Inclui prefeitos, vereadores, coligações, federações e resultados. "
        "Opt-in: MCP_BRASIL_DATASETS=tse_candidatos."
    ),
    version="0.1.0",
    api_base="https://cdn.tse.jus.br",
    requires_auth=False,
    enabled=DATASET_ID in settings.DATASETS_ENABLED,
    tags=[
        "tse",
        "eleicoes",
        "candidatos",
        "politica",
        "2024",
        "duckdb",
        "dataset",
    ],
)
