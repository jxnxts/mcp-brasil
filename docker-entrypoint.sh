#!/usr/bin/env bash
# Boot sequence: warmup datasets then launch MCP server.
set -euo pipefail

cd /app

# Only run warmup when opt-in datasets are enabled.
if [ -n "${MCP_BRASIL_DATASETS:-}" ]; then
    echo "[entrypoint] MCP_BRASIL_DATASETS=${MCP_BRASIL_DATASETS}"
    echo "[entrypoint] Cache dir: ${MCP_BRASIL_DATASET_CACHE_DIR:-~/.cache/mcp-brasil}"
    echo "[entrypoint] Running warmup — this may take several minutes on first boot."
    uv run python scripts/warmup_datasets.py || {
        echo "[entrypoint] WARNING: warmup script failed; proceeding to server."
        echo "[entrypoint] Datasets will lazy-load on first tool call."
    }
else
    echo "[entrypoint] MCP_BRASIL_DATASETS not set; skipping dataset warmup."
fi

echo "[entrypoint] Starting MCP server on :8061"
exec uv run python -c "from mcp_brasil.server import mcp; mcp.run(transport='streamable-http', host='0.0.0.0', port=8061)"
