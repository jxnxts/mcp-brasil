"""Constants for the BPS (Banco de Preços em Saúde) API."""

# API endpoint
BPS_URL = "https://apidadosabertos.saude.gov.br/economia-da-saude/bps"

# Pagination
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000

# Soft-hyphen character in API field name (data quality issue)
SOFT_HYPHEN = "\u00ad"
FIELD_MUNICIPIO = f"nome_do_munica{SOFT_HYPHEN}pio_da_instituicao"
