"""HTTP client for governadores — single JSON fetch with in-memory cache."""

from __future__ import annotations

import json
import time
from typing import Any

from mcp_brasil._shared.http_client import http_get

from .constants import GOV_JSON_URL, NOME_UF
from .schemas import Governador

_CACHE: dict[str, Governador] = {}
_CACHE_TS: float = 0.0
_CACHE_TTL = 60 * 60 * 24  # 24h


async def _load() -> dict[str, Governador]:
    """Carrega o JSON (com cache 24h) e indexa por sigla UF."""
    global _CACHE_TS
    now = time.time()
    if _CACHE and (now - _CACHE_TS) < _CACHE_TTL:
        return _CACHE

    raw = await http_get(GOV_JSON_URL)
    # Algumas versões publicam o JSON duplamente codificado (string dentro de string).
    data: Any = raw
    if isinstance(data, str):
        data = json.loads(data)

    parsed: dict[str, Governador] = {}
    if isinstance(data, dict):
        for nome_uf, info in data.items():
            if not isinstance(info, dict):
                continue
            sigla = NOME_UF.get(nome_uf)
            if not sigla:
                continue
            parsed[sigla] = Governador(uf=sigla, **info)
    _CACHE.clear()
    _CACHE.update(parsed)
    _CACHE_TS = now
    return _CACHE


async def listar_todos() -> list[Governador]:
    data = await _load()
    return list(data.values())


async def por_uf(uf: str) -> Governador | None:
    data = await _load()
    return data.get(uf.strip().upper())
