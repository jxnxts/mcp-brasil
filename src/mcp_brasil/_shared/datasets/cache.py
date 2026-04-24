"""Cache directory and manifest IO for datasets (ADR-004)."""

from __future__ import annotations

import contextlib
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from mcp_brasil import settings


@dataclass
class Manifest:
    """Persisted metadata next to a cached .duckdb file."""

    id: str
    url: str
    table: str
    fetched_at: float = 0.0  # unix timestamp
    row_count: int = 0
    size_bytes: int = 0
    schema_hash: str = ""
    source: str = ""
    extra: dict[str, object] = field(default_factory=dict)


def cache_root() -> Path:
    """Return the (possibly lazy-created) cache root."""
    root = Path(settings.DATASET_CACHE_DIR).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    (root / "datasets").mkdir(parents=True, exist_ok=True)
    return root


def db_path(dataset_id: str) -> Path:
    """Path to the DuckDB file for a dataset."""
    return cache_root() / "datasets" / f"{dataset_id}.duckdb"


def manifest_path(dataset_id: str) -> Path:
    """Path to the JSON manifest sidecar file."""
    return cache_root() / "datasets" / f"{dataset_id}.manifest.json"


def load_manifest(dataset_id: str) -> Manifest | None:
    """Return the persisted manifest, or None if missing/corrupt."""
    p = manifest_path(dataset_id)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return Manifest(
            id=data["id"],
            url=data["url"],
            table=data["table"],
            fetched_at=float(data.get("fetched_at", 0.0)),
            row_count=int(data.get("row_count", 0)),
            size_bytes=int(data.get("size_bytes", 0)),
            schema_hash=str(data.get("schema_hash", "")),
            source=str(data.get("source", "")),
            extra=dict(data.get("extra", {})),
        )
    except (OSError, ValueError, KeyError):
        return None


def save_manifest(manifest: Manifest) -> None:
    """Persist a manifest next to the DuckDB file."""
    p = manifest_path(manifest.id)
    p.write_text(
        json.dumps(asdict(manifest), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def clear_dataset(dataset_id: str) -> None:
    """Remove cached files for a dataset (used by refrescar_dataset)."""
    for p in (db_path(dataset_id), manifest_path(dataset_id)):
        with contextlib.suppress(FileNotFoundError):
            p.unlink()


def total_cache_size_bytes() -> int:
    """Sum of all cached dataset files."""
    root = cache_root() / "datasets"
    if not root.exists():
        return 0
    return sum(f.stat().st_size for f in root.iterdir() if f.is_file())


def format_bytes(n: int) -> str:
    """Human-readable byte size (1.2 GB, 456 KB, ...)."""
    value: float = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024.0 or unit == "TB":
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


# Re-export for os-agnostic testing
__all__ = [
    "Manifest",
    "cache_root",
    "clear_dataset",
    "db_path",
    "format_bytes",
    "load_manifest",
    "manifest_path",
    "save_manifest",
    "total_cache_size_bytes",
]


def _join(*parts: str) -> str:
    return os.path.join(*parts)
