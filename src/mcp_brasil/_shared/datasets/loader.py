"""DuckDB-based dataset loader and query executor (ADR-004).

Contract:
    - load_into_duckdb() downloads the source CSV and materializes it as a
      table inside a persistent .duckdb file.
    - ensure_loaded() is idempotent: uses the cache if fresh, refreshes if
      expired/missing based on DATASET_REFRESH_MODE.
    - executar_query() opens the DuckDB file in read-only mode and runs a
      parameterized SELECT, returning rows as list[dict].
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from pathlib import Path
from typing import Any

import duckdb

from mcp_brasil import settings

from .cache import (
    Manifest,
    db_path,
    load_manifest,
    save_manifest,
)
from .dataset import DatasetSpec

logger = logging.getLogger(__name__)

# Per-dataset locks prevent concurrent loads of the same dataset
_LOAD_LOCKS: dict[str, asyncio.Lock] = {}


def _lock_for(dataset_id: str) -> asyncio.Lock:
    lock = _LOAD_LOCKS.get(dataset_id)
    if lock is None:
        lock = _LOAD_LOCKS[dataset_id] = asyncio.Lock()
    return lock


def _is_fresh(manifest: Manifest | None, spec: DatasetSpec) -> bool:
    """Return True if the cached data is within TTL."""
    if manifest is None or manifest.fetched_at <= 0:
        return False
    if settings.DATASET_REFRESH_MODE == "force":
        return False
    if settings.DATASET_REFRESH_MODE == "never":
        return True  # trust cache even if stale
    age_days = (time.time() - manifest.fetched_at) / 86400.0
    return age_days < spec.ttl_days


def _render_csv_options(opts: dict[str, Any]) -> str:
    """Serialize duckdb.read_csv_auto options into SQL-safe kwargs."""
    parts: list[str] = []
    for key, val in opts.items():
        if isinstance(val, bool):
            parts.append(f"{key}={str(val).lower()}")
        elif isinstance(val, int | float):
            parts.append(f"{key}={val}")
        elif isinstance(val, str):
            escaped = val.replace("'", "''")
            parts.append(f"{key}='{escaped}'")
        elif isinstance(val, list):
            inner = ",".join(f"'{str(x).replace(chr(39), chr(39) * 2)}'" for x in val)
            parts.append(f"{key}=[{inner}]")
        elif isinstance(val, dict):
            # dtypes / column_types / types — STRUCT-literal form
            struct_parts = []
            for col_name, col_type in val.items():
                col_escaped = str(col_name).replace("'", "''")
                type_escaped = str(col_type).replace("'", "''")
                struct_parts.append(f"'{col_escaped}': '{type_escaped}'")
            parts.append(f"{key}={{{', '.join(struct_parts)}}}")
        else:
            raise TypeError(f"Unsupported CSV option type for {key}: {type(val)}")
    return ", ".join(parts)


_DUCKDB_ENCODINGS = {"utf-8", "utf8", "latin-1", "latin1", "utf-16", "utf16"}


def _download_to_file(
    url: str,
    dest: Path,
    timeout: float,
    source_encoding: str = "utf-8",
) -> int:
    """Stream a remote file to disk via httpx (follows redirects).

    If the declared ``source_encoding`` is not one that DuckDB supports,
    the stream is transcoded to UTF-8 on the fly (common for Windows-1252
    Brazilian gov files with smart quotes/en-dashes).

    Returns size in bytes written to disk.
    """
    import codecs

    import httpx

    normalized = source_encoding.lower().replace("_", "-")
    needs_transcode = normalized not in _DUCKDB_ENCODINGS

    total = 0
    with (
        httpx.Client(follow_redirects=True, timeout=timeout) as client,
        client.stream("GET", url) as resp,
        dest.open("wb") as f,
    ):
        resp.raise_for_status()
        if not needs_transcode:
            for chunk in resp.iter_bytes(chunk_size=1_048_576):
                f.write(chunk)
                total += len(chunk)
        else:
            decoder = codecs.getincrementaldecoder(source_encoding)(errors="replace")
            for chunk in resp.iter_bytes(chunk_size=1_048_576):
                text = decoder.decode(chunk)
                if text:
                    encoded = text.encode("utf-8")
                    f.write(encoded)
                    total += len(encoded)
            tail = decoder.decode(b"", final=True)
            if tail:
                encoded = tail.encode("utf-8")
                f.write(encoded)
                total += len(encoded)
    return total


def _load_into_duckdb(spec: DatasetSpec) -> Manifest:
    """Download the source CSV into a fresh DuckDB file.

    Strategy:
        1. Stream the CSV to a local temp file via httpx (reliable with
           redirects/cookies/slow servers).
        2. Load the local file into DuckDB (avoids httpfs encoding/redirect
           quirks for non-utf-8 sources).

    Runs synchronously — caller is responsible for off-loading to a thread
    via ``asyncio.to_thread`` when called from async context.
    """
    from mcp_brasil import settings as _settings

    path = db_path(spec.id)
    tmp_path = path.with_suffix(".duckdb.part")
    if tmp_path.exists():
        tmp_path.unlink()
    csv_tmp = path.with_suffix(".source.tmp")
    if csv_tmp.exists():
        csv_tmp.unlink()

    logger.info("Loading dataset %s from %s", spec.id, spec.url)
    logger.info("Downloading source to %s (encoding=%s) ...", csv_tmp, spec.source_encoding)
    downloaded = _download_to_file(
        spec.url,
        csv_tmp,
        timeout=_settings.DATASET_DOWNLOAD_TIMEOUT,
        source_encoding=spec.source_encoding,
    )
    logger.info("Downloaded %d bytes; loading into DuckDB", downloaded)

    # After transcode, the file on disk is always UTF-8. Any encoding option
    # declared by the spec for DuckDB must be overridden accordingly.
    csv_kwargs = dict(spec.csv_options)
    csv_kwargs["encoding"] = "utf-8"

    con = duckdb.connect(str(tmp_path), read_only=False)
    try:
        url_escaped = str(csv_tmp).replace("'", "''")
        kwargs = _render_csv_options(csv_kwargs)
        kwargs_part = f", {kwargs}" if kwargs else ""
        sql = (
            f'CREATE OR REPLACE TABLE "{spec.table}" AS '
            f"SELECT * FROM read_csv_auto('{url_escaped}'{kwargs_part})"
        )
        con.execute(sql)

        row = con.execute(f'SELECT COUNT(*) FROM "{spec.table}"').fetchone()
        row_count = int(row[0]) if row else 0

        schema_rows = con.execute(f'DESCRIBE "{spec.table}"').fetchall()
        schema_repr = "|".join(f"{r[0]}:{r[1]}" for r in schema_rows)
    finally:
        con.close()

    # Swap into place and discard the source CSV.
    tmp_path.replace(path)
    with contextlib.suppress(FileNotFoundError):
        csv_tmp.unlink()
    size_bytes = path.stat().st_size

    manifest = Manifest(
        id=spec.id,
        url=spec.url,
        table=spec.table,
        fetched_at=time.time(),
        row_count=row_count,
        size_bytes=size_bytes,
        schema_hash=_hash_text(schema_repr),
        source=spec.source,
    )
    save_manifest(manifest)
    logger.info("Dataset %s ready: %d rows, %d bytes", spec.id, row_count, size_bytes)
    return manifest


def _hash_text(text: str) -> str:
    """Short, stable hash for schema drift detection."""
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


async def ensure_loaded(spec: DatasetSpec) -> Manifest:
    """Idempotent: load the dataset if missing/stale; return current manifest.

    Respects MCP_BRASIL_DATASET_REFRESH:
        - auto (default): refresh when age > ttl_days
        - never: use cache regardless of age; error if cache missing
        - force: always re-download
    """
    lock = _lock_for(spec.id)
    async with lock:
        manifest = load_manifest(spec.id)
        if _is_fresh(manifest, spec) and db_path(spec.id).exists():
            assert manifest is not None
            return manifest
        if settings.DATASET_REFRESH_MODE == "never":
            if manifest is None or not db_path(spec.id).exists():
                raise RuntimeError(f"Dataset {spec.id!r} has no cache and refresh=never")
            return manifest
        # Download in a worker thread so we don't block the event loop.
        return await asyncio.to_thread(_load_into_duckdb, spec)


async def refresh_dataset(spec: DatasetSpec) -> Manifest:
    """Force a re-download and return the new manifest."""
    lock = _lock_for(spec.id)
    async with lock:
        return await asyncio.to_thread(_load_into_duckdb, spec)


async def executar_query(
    spec: DatasetSpec,
    sql: str,
    params: list[Any] | tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    """Run a parameterized read-only query against a loaded dataset.

    Ensures the dataset is loaded first (may trigger download). Opens
    DuckDB in read-only mode — DDL/DML raise ``duckdb.Error``.
    """
    await ensure_loaded(spec)
    return await asyncio.to_thread(_execute_sync, spec, sql, list(params))


def _execute_sync(spec: DatasetSpec, sql: str, params: list[Any]) -> list[dict[str, Any]]:
    path = db_path(spec.id)
    con = duckdb.connect(str(path), read_only=True)
    try:
        cursor = con.execute(sql, params) if params else con.execute(sql)
        cols = [c[0] for c in cursor.description] if cursor.description else []
        return [dict(zip(cols, row, strict=False)) for row in cursor.fetchall()]
    finally:
        con.close()


async def get_status(spec: DatasetSpec) -> dict[str, Any]:
    """Introspect current cache state for a dataset (no network)."""
    manifest = load_manifest(spec.id)
    path = db_path(spec.id)
    exists = path.exists()
    age_days: float | None = None
    if manifest and manifest.fetched_at > 0:
        age_days = (time.time() - manifest.fetched_at) / 86400.0
    return {
        "id": spec.id,
        "cached": exists,
        "row_count": manifest.row_count if manifest else 0,
        "size_bytes": manifest.size_bytes if manifest else 0,
        "fetched_at": manifest.fetched_at if manifest else 0.0,
        "age_days": age_days,
        "fresh": _is_fresh(manifest, spec),
        "ttl_days": spec.ttl_days,
        "url": spec.url,
        "table": spec.table,
        "source": spec.source,
    }
