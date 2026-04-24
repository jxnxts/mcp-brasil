"""Pre-populate the local dataset cache for all enabled datasets.

Reads ``MCP_BRASIL_DATASETS`` from the environment and runs
``ensure_loaded`` for each registered dataset. Intended to be executed at
container boot (before serving traffic) or as a one-shot job via
``az containerapp exec``.

Usage:
    python -m scripts.warmup_datasets
    uv run python scripts/warmup_datasets.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("warmup")


async def warmup_one(spec) -> tuple[str, bool, float, str]:
    from mcp_brasil._shared.datasets import ensure_loaded

    t0 = time.monotonic()
    try:
        manifest = await ensure_loaded(spec)
        dt = time.monotonic() - t0
        return (
            spec.id,
            True,
            dt,
            f"{manifest.row_count:,} rows, "
            f"{manifest.size_bytes / 1024 / 1024:.1f} MB",
        )
    except Exception as exc:  # noqa: BLE001
        dt = time.monotonic() - t0
        return (spec.id, False, dt, f"{type(exc).__name__}: {exc}")


async def main() -> int:
    from mcp_brasil import settings
    from mcp_brasil._shared.datasets import get_registry

    enabled = list(settings.DATASETS_ENABLED)
    if not enabled:
        log.warning("MCP_BRASIL_DATASETS is empty — nothing to warm up")
        return 0

    reg = get_registry()
    specs = reg.enabled_specs()
    log.info("Warmup plan: %d datasets (%s)", len(specs), ", ".join(s.id for s in specs))
    log.info("Cache dir: %s", settings.DATASET_CACHE_DIR)

    results = []
    for spec in specs:
        log.info("[%s] starting (approx %d MB)...", spec.id, spec.approx_size_mb)
        result = await warmup_one(spec)
        results.append(result)
        label = "ok" if result[1] else "FAIL"
        log.info("[%s] %s in %.1fs — %s", result[0], label, result[2], result[3])

    failed = [r for r in results if not r[1]]
    total = sum(r[2] for r in results)
    log.info(
        "Warmup complete: %d ok, %d failed, total %.1fs",
        len(results) - len(failed),
        len(failed),
        total,
    )
    if failed:
        log.error("Failed: %s", ", ".join(r[0] for r in failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
