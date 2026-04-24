"""Constants for the spu_siapa feature."""

# Regime de utilização — valores comuns no SIAPA
REGIMES_COMUNS: tuple[str, ...] = (
    "Aforamento",
    "Ocupação",
    "Uso em Serviço Público",
    "Cessão",
    "Locação",
    "Irregular",
    "Dominial",
)

# Conceituação do terreno — valores comuns
CONCEITUACOES: tuple[str, ...] = (
    "Marinha",
    "Acrescido de Marinha",
    "Marginal",
    "Acrescido Marginal",
    "Interior",
    "Ilha",
    "Outros",
)

# Classe — "Dominial" (imóveis da União com terceiros) ou "Uso Especial"
CLASSES: tuple[str, ...] = ("Dominial", "Uso Especial")
