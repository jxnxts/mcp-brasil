"""HTTP client for brapi.dev (B3 data aggregator).

Note: brapi.dev mudou política de auth (abril 2026) — ações (ex: PETR4)
continuam públicas, mas **índices (^BVSP) e histórico pedem token gratuito**
de https://brapi.dev/dashboard. Configure via env var ``BRAPI_TOKEN``.
"""

from __future__ import annotations

import os
from typing import Any

from mcp_brasil._shared.http_client import http_get
from mcp_brasil.exceptions import HttpClientError

from .constants import BRAPI_BASE


def _auth_params() -> dict[str, str]:
    token = os.environ.get("BRAPI_TOKEN", "").strip()
    return {"token": token} if token else {}


async def _get_or_none(url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """GET with graceful handling of 401 (no token configured)."""
    try:
        data = await http_get(url, params={**params, **_auth_params()})
    except HttpClientError as exc:
        if "401" in str(exc) or "MISSING_TOKEN" in str(exc):
            return None
        raise
    return data if isinstance(data, dict) else None


async def cotacao(tickers: str) -> list[dict[str, Any]]:
    """GET /quote/{tickers} — cotações real-time.

    Args:
        tickers: Símbolos separados por vírgula (ex: 'PETR4,VALE3').
    """
    url = f"{BRAPI_BASE}/quote/{tickers}"
    data = await _get_or_none(url, {})
    if data is None:
        return []
    results = data.get("results")
    if isinstance(results, list):
        return [r for r in results if isinstance(r, dict)]
    return []


async def historico(ticker: str, periodo: str = "1mo", intervalo: str = "1d") -> dict[str, Any]:
    """GET /quote/{ticker}?range=...&interval=... — série histórica.

    Requer ``BRAPI_TOKEN`` (histórico é endpoint pago).

    Args:
        ticker: Símbolo único.
        periodo: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'.
        intervalo: '1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'.
    """
    url = f"{BRAPI_BASE}/quote/{ticker}"
    data = await _get_or_none(url, {"range": periodo, "interval": intervalo})
    if data is None:
        return {}
    results = data.get("results") or []
    if results and isinstance(results[0], dict):
        return results[0]
    return {}


async def listar_ativos(tipo: str = "stock") -> list[dict[str, Any]]:
    """GET /quote/list — lista ativos disponíveis (com volume/preço se público).

    Args:
        tipo: 'stock' (ações), 'fund' (FIIs), 'bdr' (BDRs), 'index' (índices).
    """
    url = f"{BRAPI_BASE}/quote/list"
    data = await _get_or_none(url, {"type": tipo, "sortBy": "volume", "sortOrder": "desc"})
    if data is None:
        return []
    stocks = data.get("stocks")
    if isinstance(stocks, list):
        return [s for s in stocks if isinstance(s, dict)]
    return []
