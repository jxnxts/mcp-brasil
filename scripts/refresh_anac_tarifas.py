"""Refresh anac_tarifas dataset — Playwright scraper for SAS ANAC portal.

Runs only during dev/CI refresh. Not invoked at runtime. Writes the
resulting ``anac_tarifas.duckdb`` directly to the cache dir so that
``ensure_loaded()`` will find a valid manifest and skip re-download.

Usage:
    uv sync --group dev
    uv run playwright install chromium
    uv run python scripts/refresh_anac_tarifas.py --ano 2024
    uv run python scripts/refresh_anac_tarifas.py --ano 2024 --ano 2023 --ano 2022

Output:
    {cache_dir}/datasets/anac_tarifas.duckdb
    {cache_dir}/datasets/anac_tarifas.manifest.json
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import shutil
import tempfile
import time
import zipfile
from pathlib import Path

from playwright.async_api import async_playwright

from mcp_brasil import settings

log = logging.getLogger("refresh_anac_tarifas")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SAS_URL = "https://sas.anac.gov.br/sas/downloads/view/frmDownload.aspx"
TEMA_TARIFAS_DOMESTICAS = "14"


async def download_zip(ano: int, dest_dir: Path) -> Path:
    """Drive the SAS ASP.NET form via Chromium and save the yearly ZIP."""
    log.info(f"[{ano}] opening SAS portal")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            ctx = await browser.new_context(accept_downloads=True)
            page = await ctx.new_page()
            await page.goto(SAS_URL)
            await page.wait_for_load_state("networkidle")

            await page.select_option(
                "select[name='ctl00$MainContent$listTema']", TEMA_TARIFAS_DOMESTICAS
            )
            await page.wait_for_timeout(400)
            await page.select_option("select[name='ctl00$MainContent$listAno']", str(ano))
            await page.wait_for_timeout(400)

            log.info(f"[{ano}] submit 'Buscar Arquivos'")
            await page.click("input[name='ctl00$MainContent$btnListaArquivos']")
            await page.wait_for_load_state("networkidle")

            log.info(f"[{ano}] submit 'Marcar Todos'")
            await page.click("input[name='ctl00$MainContent$btnMarcar']")
            await page.wait_for_load_state("networkidle")

            log.info(f"[{ano}] submit 'Baixar Marcados' (may take a minute)")
            async with page.expect_download(timeout=120_000) as dl_info:
                await page.click("input[name='ctl00$MainContent$btnBaixar']")
            dl = await dl_info.value
            dest = dest_dir / f"anac_tarifas_{ano}.zip"
            await dl.save_as(str(dest))
            size_mb = dest.stat().st_size / 1024 / 1024
            log.info(f"[{ano}] saved {dest.name} ({size_mb:.1f} MB)")
            return dest
        finally:
            await browser.close()


def build_duckdb(zip_paths: list[Path], out_duckdb: Path, table: str = "tarifas") -> dict:
    """Extract CSVs and ingest all rows into a single DuckDB table.

    Uses DuckDB's ``read_csv`` with explicit schema (CP1252, delim=';').
    """
    import duckdb

    log.info(f"building {out_duckdb} from {len(zip_paths)} ZIP(s)")
    extract_dir = out_duckdb.parent / "_anac_tarifas_extract"
    extract_dir.mkdir(parents=True, exist_ok=True)

    csv_files: list[Path] = []
    for zp in zip_paths:
        with zipfile.ZipFile(zp) as z:
            for name in z.namelist():
                if not name.upper().endswith(".CSV"):
                    continue
                target = extract_dir / name
                target.write_bytes(z.read(name))
                csv_files.append(target)

    log.info(f"extracted {len(csv_files)} CSVs to {extract_dir}")

    # DuckDB doesn't read CP1252 directly — transcode each CSV to UTF-8.
    utf8_dir = extract_dir / "utf8"
    utf8_dir.mkdir(exist_ok=True)
    for csv in csv_files:
        raw = csv.read_bytes()
        text = raw.decode("cp1252", errors="replace")
        (utf8_dir / csv.name).write_text(text, encoding="utf-8")

    glob = str(utf8_dir / "*.CSV")
    con = duckdb.connect(str(out_duckdb))
    try:
        con.execute(f'DROP TABLE IF EXISTS "{table}"')
        con.execute(
            f"""
            CREATE TABLE "{table}" AS
            SELECT
                CAST(ANO AS INTEGER)     AS ano,
                CAST(MES AS INTEGER)     AS mes,
                TRIM(EMPRESA)            AS empresa,
                TRIM(ORIGEM)             AS origem,
                TRIM(DESTINO)            AS destino,
                TRY_CAST(REPLACE(TARIFA, ',', '.') AS DOUBLE) AS tarifa,
                TRY_CAST(ASSENTOS AS INTEGER) AS assentos
            FROM read_csv('{glob}',
                delim=';', header=true, quote='"',
                ignore_errors=true, sample_size=-1,
                columns={{
                    'ANO':'VARCHAR', 'MES':'VARCHAR', 'EMPRESA':'VARCHAR',
                    'ORIGEM':'VARCHAR', 'DESTINO':'VARCHAR',
                    'TARIFA':'VARCHAR', 'ASSENTOS':'VARCHAR'
                }})
            """
        )
        row_count = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        con.execute("CHECKPOINT")
    finally:
        con.close()

    shutil.rmtree(extract_dir, ignore_errors=True)
    size_bytes = out_duckdb.stat().st_size
    log.info(f"built {out_duckdb.name}: {row_count:,} rows, {size_bytes / 1024 / 1024:.1f} MB")
    return {"row_count": row_count, "size_bytes": size_bytes}


def write_manifest(dataset_id: str, url: str, table: str, stats: dict) -> None:
    cache_dir = Path(settings.DATASET_CACHE_DIR).expanduser() / "datasets"
    cache_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": dataset_id,
        "url": url,
        "table": table,
        "fetched_at": time.time(),
        "row_count": stats["row_count"],
        "size_bytes": stats["size_bytes"],
        "schema_hash": hashlib.sha1(
            f"{dataset_id}:{table}:{stats['row_count']}".encode()
        ).hexdigest(),
        "source": "ANAC SAS — Tarifas Aéreas Domésticas (scraped via Playwright)",
    }
    manifest_path = cache_dir / f"{dataset_id}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    log.info(f"wrote manifest: {manifest_path}")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ano", type=int, action="append", required=True)
    args = parser.parse_args()

    cache_dir = Path(settings.DATASET_CACHE_DIR).expanduser() / "datasets"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_duckdb = cache_dir / "anac_tarifas.duckdb"

    tmp = Path(tempfile.mkdtemp(prefix="anac_tarifas_"))
    try:
        zips: list[Path] = []
        for ano in args.ano:
            zip_path = await download_zip(ano, tmp)
            zips.append(zip_path)

        stats = build_duckdb(zips, out_duckdb)
        write_manifest(
            dataset_id="anac_tarifas",
            url=SAS_URL,
            table="tarifas",
            stats=stats,
        )
        log.info(f"✓ cache ready at {out_duckdb}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
