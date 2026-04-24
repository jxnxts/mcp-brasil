"""Tests for the datasets infrastructure (ADR-004).

The loader hits real DuckDB (embedded) but we serve the CSV from a local
file URL via mocking ``_download_to_file``. No network required.
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from mcp_brasil import settings
from mcp_brasil._shared.datasets import (
    DatasetSpec,
    ensure_loaded,
    executar_query,
    get_registry,
    get_status,
    mask_value,
    redact_rows,
    refresh_dataset,
)
from mcp_brasil._shared.datasets.cache import (
    Manifest,
    db_path,
    load_manifest,
    save_manifest,
)
from mcp_brasil._shared.datasets.registry import reset_registry

_SMALL_CSV = (
    "orgao;uf;municipio;valor\n"
    "MEC;SP;Sao Paulo;1000,50\n"
    "MD;DF;Brasilia;200,00\n"
    "MGI;RJ;Rio de Janeiro;50,25\n"
)


@pytest.fixture
def tmp_cache(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate the dataset cache dir per-test."""
    d = tempfile.mkdtemp(prefix="mcp-brasil-test-")
    monkeypatch.setattr(settings, "DATASET_CACHE_DIR", d)
    return Path(d)


@pytest.fixture
def small_spec() -> DatasetSpec:
    return DatasetSpec(
        id="test_small",
        url="https://example.invalid/small.csv",
        table="small",
        ttl_days=7,
        csv_options={"delim": ";", "header": True, "decimal_separator": ","},
        source="unit test",
    )


def _mock_download(csv_text: str):
    """Monkeypatches _download_to_file to write the given CSV locally."""

    def _fake(url: str, dest: Path, timeout: float, source_encoding: str = "utf-8") -> int:
        dest.write_text(csv_text, encoding="utf-8")
        return dest.stat().st_size

    return _fake


# ---------------------------------------------------------------------------
# DatasetSpec validation
# ---------------------------------------------------------------------------


def test_dataset_spec_rejects_bad_id() -> None:
    with pytest.raises(ValueError):
        DatasetSpec(id="bad id!", url="https://x.test/y", table="t")


def test_dataset_spec_rejects_bad_url() -> None:
    with pytest.raises(ValueError):
        DatasetSpec(id="ok", url="ftp://x/y", table="t")


# ---------------------------------------------------------------------------
# Cache/manifest IO
# ---------------------------------------------------------------------------


def test_manifest_roundtrip(tmp_cache: Path) -> None:
    m = Manifest(
        id="foo",
        url="https://ex/",
        table="t",
        fetched_at=12345.0,
        row_count=42,
        size_bytes=99,
        schema_hash="abcd",
        source="src",
    )
    save_manifest(m)
    loaded = load_manifest("foo")
    assert loaded is not None
    assert loaded.row_count == 42
    assert loaded.schema_hash == "abcd"


def test_load_manifest_returns_none_when_missing(tmp_cache: Path) -> None:
    assert load_manifest("nonexistent") is None


# ---------------------------------------------------------------------------
# Loader — ensure_loaded / executar_query
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ensure_loaded_downloads_and_caches(
    tmp_cache: Path, small_spec: DatasetSpec
) -> None:
    with patch(
        "mcp_brasil._shared.datasets.loader._download_to_file",
        side_effect=_mock_download(_SMALL_CSV),
    ) as mock:
        m = await ensure_loaded(small_spec)
        # Second call should not re-download
        m2 = await ensure_loaded(small_spec)

    assert mock.call_count == 1
    assert m.row_count == 3
    assert m2.fetched_at == m.fetched_at
    assert db_path("test_small").exists()


@pytest.mark.asyncio
async def test_executar_query_returns_dicts(tmp_cache: Path, small_spec: DatasetSpec) -> None:
    with patch(
        "mcp_brasil._shared.datasets.loader._download_to_file",
        side_effect=_mock_download(_SMALL_CSV),
    ):
        rows = await executar_query(
            small_spec,
            "SELECT orgao, uf FROM small WHERE uf = ? ORDER BY orgao",
            ["SP"],
        )

    assert rows == [{"orgao": "MEC", "uf": "SP"}]


@pytest.mark.asyncio
async def test_executar_query_read_only(tmp_cache: Path, small_spec: DatasetSpec) -> None:
    import duckdb

    with patch(
        "mcp_brasil._shared.datasets.loader._download_to_file",
        side_effect=_mock_download(_SMALL_CSV),
    ):
        await ensure_loaded(small_spec)
        with pytest.raises(duckdb.Error):
            await executar_query(small_spec, "DROP TABLE small")


@pytest.mark.asyncio
async def test_refresh_dataset_ignores_ttl(tmp_cache: Path, small_spec: DatasetSpec) -> None:
    with patch(
        "mcp_brasil._shared.datasets.loader._download_to_file",
        side_effect=_mock_download(_SMALL_CSV),
    ) as mock:
        await ensure_loaded(small_spec)
        await refresh_dataset(small_spec)
    assert mock.call_count == 2


@pytest.mark.asyncio
async def test_ttl_refresh_when_expired(tmp_cache: Path, small_spec: DatasetSpec) -> None:
    with patch(
        "mcp_brasil._shared.datasets.loader._download_to_file",
        side_effect=_mock_download(_SMALL_CSV),
    ) as mock:
        await ensure_loaded(small_spec)
        # Age the manifest: fake fetched_at 30 days ago (ttl_days=7 → stale)
        m = load_manifest(small_spec.id)
        assert m is not None
        m.fetched_at = time.time() - 30 * 86400
        save_manifest(m)
        await ensure_loaded(small_spec)
    assert mock.call_count == 2


@pytest.mark.asyncio
async def test_refresh_never_uses_stale_cache(
    tmp_cache: Path,
    small_spec: DatasetSpec,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with patch(
        "mcp_brasil._shared.datasets.loader._download_to_file",
        side_effect=_mock_download(_SMALL_CSV),
    ):
        await ensure_loaded(small_spec)

    monkeypatch.setattr(settings, "DATASET_REFRESH_MODE", "never")
    # Even very old, should return without re-downloading
    m = load_manifest(small_spec.id)
    assert m is not None
    m.fetched_at = 0  # super stale
    save_manifest(m)
    m2 = await ensure_loaded(small_spec)
    assert m2.url == small_spec.url


@pytest.mark.asyncio
async def test_refresh_never_without_cache_raises(
    tmp_cache: Path,
    small_spec: DatasetSpec,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "DATASET_REFRESH_MODE", "never")
    with pytest.raises(RuntimeError, match="refresh=never"):
        await ensure_loaded(small_spec)


@pytest.mark.asyncio
async def test_get_status_reflects_cache(tmp_cache: Path, small_spec: DatasetSpec) -> None:
    before = await get_status(small_spec)
    assert before["cached"] is False
    with patch(
        "mcp_brasil._shared.datasets.loader._download_to_file",
        side_effect=_mock_download(_SMALL_CSV),
    ):
        await ensure_loaded(small_spec)
    after = await get_status(small_spec)
    assert after["cached"] is True
    assert after["row_count"] == 3
    assert after["fresh"] is True


# ---------------------------------------------------------------------------
# LGPD — mask_value / redact_rows
# ---------------------------------------------------------------------------


def test_mask_value_cpf() -> None:
    assert mask_value("123.456.789-00") == "***.***.789-**"
    assert mask_value("12345678900") == "***.***.789-**"


def test_mask_value_cnpj() -> None:
    assert mask_value("12.345.678/0001-99") == "**.***.***/0001-**"


def test_mask_value_none_and_empty() -> None:
    assert mask_value(None) == ""
    assert mask_value("") == ""
    assert mask_value("   ") == ""


def test_redact_rows_leaves_non_pii_alone() -> None:
    spec = DatasetSpec(
        id="x",
        url="https://x.test/y",
        table="t",
        pii_columns=frozenset({"cpf"}),
    )
    rows = [{"nome": "Fulano", "cpf": "12345678900"}]
    out = redact_rows(rows, spec)
    assert out[0]["nome"] == "Fulano"
    assert out[0]["cpf"] == "***.***.789-**"


def test_redact_rows_passes_through_when_allowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "DATASETS_ALLOW_PII", ["x"])
    spec = DatasetSpec(
        id="x",
        url="https://x.test/y",
        table="t",
        pii_columns=frozenset({"cpf"}),
    )
    rows = [{"cpf": "12345678900"}]
    out = redact_rows(rows, spec)
    assert out[0]["cpf"] == "12345678900"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_registry_filters_by_env(monkeypatch: pytest.MonkeyPatch) -> None:
    reset_registry()
    monkeypatch.setattr(settings, "DATASETS_ENABLED", ["spu_siapa"])
    reg = get_registry()
    ids_all = {s.id for s in reg.all_specs()}
    ids_enabled = {s.id for s in reg.enabled_specs()}
    # spu_siapa is a real feature and should be discovered
    assert "spu_siapa" in ids_all
    assert ids_enabled == {"spu_siapa"} & ids_all


def test_registry_empty_enabled_returns_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reset_registry()
    monkeypatch.setattr(settings, "DATASETS_ENABLED", [])
    reg = get_registry()
    assert reg.enabled_specs() == []


# ---------------------------------------------------------------------------
# CSV options rendering
# ---------------------------------------------------------------------------


def test_render_csv_options_handles_scalars_and_containers() -> None:
    from mcp_brasil._shared.datasets.loader import _render_csv_options

    out = _render_csv_options(
        {
            "delim": ";",
            "header": True,
            "skip": 1,
            "nullstr": ["-", ""],
            "dtypes": {"area": "DOUBLE", "valor": "DOUBLE"},
        }
    )
    assert "delim=';'" in out
    assert "header=true" in out
    assert "skip=1" in out
    assert "nullstr=['-','']" in out
    assert "dtypes={" in out and "'area': 'DOUBLE'" in out


# Final cleanup
def test_registry_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    reset_registry()
    assert get_registry() is not None
