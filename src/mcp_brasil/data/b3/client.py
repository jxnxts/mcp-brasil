"""HTTP client for brapi.dev (B3 data aggregator)."""

from __future__ import annotations

from typing import Any

from mcp_brasil._shared.http_client import http_get

from .constants import BRAPI_BASE


async def cotacao(tickers: str) -> list[dict[str, Any]]:
    """GET /quote/{tickers} — cotações real-time.

    Args:
        tickers: Símbolos separados por vírgula (ex: 'PETR4,VALE3').
    """
    url = f"{BRAPI_BASE}/quote/{tickers}"
    data = await http_get(url, params={})
    if isinstance(data, dict):
        results = data.get("results")
        if isinstance(results, list):
            return [r for r in results if isinstance(r, dict)]
    return []


async def historico(ticker: str, periodo: str = "1mo", intervalo: str = "1d") -> dict[str, Any]:
    """GET /quote/{ticker}?range=...&interval=... — série histórica de cotações.

    Args:
        ticker: Símbolo único (ex: 'PETR4').
        periodo: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
        intervalo: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo'.
    """
    url = f"{BRAPI_BASE}/quote/{ticker}"
    params = {"range": periodo, "interval": intervalo}
    data = await http_get(url, params=params)
    if isinstance(data, dict):
        results = data.get("results") or []
        if results and isinstance(results[0], dict):
            return results[0]
    return {}


async def listar_ativos(tipo: str = "stock") -> list[dict[str, Any]]:
    """GET /quote/list — lista todos ativos disponíveis.

    Args:
        tipo: 'stock' (ações), 'fund' (FIIs), 'bdr' (BDRs).
    """
    url = f"{BRAPI_BASE}/quote/list"
    data = await http_get(url, params={"type": tipo, "sortBy": "volume", "sortOrder": "desc"})
    if isinstance(data, dict):
        stocks = data.get("stocks")
        if isinstance(stocks, list):
            return [s for s in stocks if isinstance(s, dict)]
    return []


async def listar_indices() -> list[dict[str, Any]]:
    """GET /quote/list?type=index — índices da B3 e internacionais."""
    url = f"{BRAPI_BASE}/quote/list"
    data = await http_get(url, params={"type": "index"})
    if isinstance(data, dict):
        stocks = data.get("stocks")
        if isinstance(stocks, list):
            return [s for s in stocks if isinstance(s, dict)]
    return []
