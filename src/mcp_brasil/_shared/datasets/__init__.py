"""Local dataset cache infrastructure (ADR-004).

Provides DuckDB-backed caching of large public CSV datasets with:

- Opt-in via MCP_BRASIL_DATASETS env var
- TTL-based refresh (passive, on next use)
- XDG-compliant cache directory
- LGPD column masking by default
- Read-only SQL query interface via canned tool functions

Features live in ``src/mcp_brasil/datasets/{name}/`` and declare a
``DATASET_SPEC`` alongside the standard ``FEATURE_META`` from ADR-002.
"""

from .dataset import DatasetSpec
from .lgpd import is_pii_allowed, mask_value, redact_rows
from .loader import ensure_loaded, executar_query, get_status, refresh_dataset
from .registry import DatasetRegistry, get_registry

__all__ = [
    "DatasetRegistry",
    "DatasetSpec",
    "ensure_loaded",
    "executar_query",
    "get_registry",
    "get_status",
    "is_pii_allowed",
    "mask_value",
    "redact_rows",
    "refresh_dataset",
]
