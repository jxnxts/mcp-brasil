"""Dataset-backed features (ADR-004).

Features in this package expose large public CSV/Parquet data sources via a
local DuckDB cache, gated by the ``MCP_BRASIL_DATASETS`` env var. Unlike
features in ``data/`` (REST passthrough), these require persistent disk
storage and are skipped in serverless deployments.

Each feature exports:
    - FEATURE_META (ADR-002) — for the main feature registry
    - DATASET_SPEC (ADR-004) — for the dataset registry
    - mcp: FastMCP server with canned query tools
"""
