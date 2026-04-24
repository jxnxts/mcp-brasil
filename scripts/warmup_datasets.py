"""Pre-populate the local dataset cache for all enabled datasets.

Reads ``MCP_BRASIL_DATASETS`` from the environment and runs
``ensure_loaded`` for each registered dataset **in a separate subprocess**.
Running each dataset in its own process means that if one dataset is
SIGKILL'd (OOM, Azure cgroup limit, etc.) the remaining datasets still
run instead of the whole warmup dying.

Usage:
    python -m scripts.warmup_datasets
    python scripts/warmup_datasets.py --single <dataset_id>  (internal)
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import subprocess
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("warmup")


async def warmup_single(dataset_id: str) -> int:
    """Worker entry point — warmup a single dataset (intended for subprocess).

    Returns exit code (0=ok, 1=failure, 2=dataset not found).
    """
    from mcp_brasil._shared.datasets import ensure_loaded, get_registry

    reg = get_registry()
    spec = reg.get(dataset_id)
    if spec is None:
        log.error("Dataset %r not registered", dataset_id)
        return 2
    t0 = time.monotonic()
    try:
        manifest = await ensure_loaded(spec)
    except Exception as exc:
        log.exception(
            "[%s] FAIL in %.1fs — %s: %s",
            dataset_id,
            time.monotonic() - t0,
            type(exc).__name__,
            exc,
        )
        return 1
    dt = time.monotonic() - t0
    log.info(
        "[%s] ok in %.1fs — %d rows, %.1f MB",
        dataset_id,
        dt,
        manifest.row_count,
        manifest.size_bytes / 1024 / 1024,
    )
    return 0


def run_supervisor() -> int:
    """Orchestrator — spawns one subprocess per enabled dataset.

    Subprocess isolation guarantees that a SIGKILL (OOM) on one dataset
    does not affect the others. Each subprocess runs this same script
    with ``--single <id>``.
    """
    from mcp_brasil import settings
    from mcp_brasil._shared.datasets import get_registry

    enabled = list(settings.DATASETS_ENABLED)
    if not enabled:
        log.warning("MCP_BRASIL_DATASETS is empty — nothing to warm up")
        return 0

    reg = get_registry()
    specs = reg.enabled_specs()
    log.info(
        "Warmup plan: %d datasets (%s)",
        len(specs),
        ", ".join(s.id for s in specs),
    )
    log.info("Cache dir: %s", settings.DATASET_CACHE_DIR)

    ok: list[str] = []
    failed: list[str] = []
    total_start = time.monotonic()

    for spec in specs:
        log.info("[%s] launching subprocess (approx %d MB)...", spec.id, spec.approx_size_mb)
        cmd = [sys.executable, __file__, "--single", spec.id]
        t0 = time.monotonic()
        try:
            proc = subprocess.run(cmd, check=False)
            rc = proc.returncode
        except Exception as exc:
            log.exception("[%s] subprocess launch failed: %s", spec.id, exc)
            failed.append(spec.id)
            continue
        dt = time.monotonic() - t0
        if rc == 0:
            ok.append(spec.id)
            log.info("[%s] subprocess ok in %.1fs", spec.id, dt)
        else:
            failed.append(spec.id)
            signed_rc = rc if rc < 128 else rc - 128  # signal if > 128
            log.error(
                "[%s] subprocess rc=%d (signal=%s) after %.1fs — continuing to next dataset",
                spec.id,
                rc,
                signed_rc if rc >= 128 else "n/a",
                dt,
            )

    total = time.monotonic() - total_start
    log.info(
        "Warmup complete: %d ok, %d failed, total %.1fs",
        len(ok),
        len(failed),
        total,
    )
    if failed:
        log.warning("Failed datasets (will lazy-load on demand): %s", ", ".join(failed))
    return 0  # Always return 0 so entrypoint proceeds to server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--single",
        metavar="DATASET_ID",
        help="Worker mode — warm up a single dataset (used internally by supervisor)",
    )
    args = parser.parse_args()

    if args.single:
        return asyncio.run(warmup_single(args.single))
    return run_supervisor()


if __name__ == "__main__":
    sys.exit(main())
