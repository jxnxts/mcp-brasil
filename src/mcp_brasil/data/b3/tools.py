"""MCP tools for B3."""

from __future__ import annotations

from typing import Any

from mcp_brasil._shared.formatting import format_brl, format_number_br, markdown_table

from . import client
from .constants import BLUE_CHIPS, INDICES_POPULARES


def _fmt_pct(v: Any) -> str:
    try:
        return f"{float(v):+.2f}%"
    except (TypeError, ValueError):
        return "—"


async def cotacao_ativo(ticker: str) -> str:
    """Cotação real-time de uma ação/FII/BDR na B3.

    Args:
        ticker: Símbolo (ex: 'PETR4', 'VALE3', 'MXRF11').
    """
    results = await client.cotacao(ticker.strip().upper())
    if not results:
        return f"Ativo '{ticker}' não encontrado."
    r = results[0]
    preco = r.get("regularMarketPrice") or 0
    return "\n".join(
        [
            f"**{r.get('symbol')}** — {r.get('longName') or r.get('shortName') or '—'}",
            "",
            f"- **Preço:** {format_brl(float(preco)) if preco else '—'}",
            f"- **Variação:** {_fmt_pct(r.get('regularMarketChangePercent'))}",
            f"- **Volume:** {format_number_br(int(r.get('regularMarketVolume') or 0), 0)}",
            f"- **Máx dia:** {format_brl(float(r.get('regularMarketDayHigh') or 0))}",
            f"- **Mín dia:** {format_brl(float(r.get('regularMarketDayLow') or 0))}",
            f"- **Market cap:** {format_brl(float(r.get('marketCap') or 0))}",
            f"- **Atualizado:** {r.get('regularMarketTime') or '—'}",
        ]
    )


async def cotacoes_multiplas(tickers: str) -> str:
    """Cotações de múltiplos ativos em uma tabela.

    Limite do tier gratuito brapi.dev: **até 3 tickers por chamada** sem token.
    Para mais que 3, configure ``BRAPI_TOKEN``.

    Args:
        tickers: Símbolos separados por vírgula (ex: 'PETR4,VALE3,ITUB4').
    """
    clean = ",".join(t.strip().upper() for t in tickers.split(","))
    results = await client.cotacao(clean)
    if not results:
        return (
            "Nenhum ativo encontrado. Nota: tier gratuito brapi.dev aceita "
            "até 3 tickers. Configure BRAPI_TOKEN para mais."
        )
    rows = [
        (
            r.get("symbol") or "—",
            format_brl(float(r.get("regularMarketPrice") or 0)),
            _fmt_pct(r.get("regularMarketChangePercent")),
            format_number_br(int(r.get("regularMarketVolume") or 0), 0),
        )
        for r in results
    ]
    return f"**Cotações — {len(results)} ativo(s)**\n\n" + markdown_table(
        ["Ticker", "Preço", "Var.%", "Volume"], rows
    )


async def historico_ativo(ticker: str, periodo: str = "1mo", intervalo: str = "1d") -> str:
    """Histórico de cotações de um ativo.

    Args:
        ticker: Símbolo (ex: 'PETR4').
        periodo: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'.
        intervalo: '1d' (diário), '1wk' (semanal), '1mo' (mensal).
    """
    data = await client.historico(ticker.strip().upper(), periodo, intervalo)
    pontos = data.get("historicalDataPrice") or []
    if not pontos:
        return f"Sem histórico para '{ticker}'."
    import datetime as _dt

    rows = []
    for p in pontos[-30:]:
        ts = p.get("date")
        dt = _dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "—"
        rows.append(
            (
                dt,
                format_brl(float(p.get("open") or 0)),
                format_brl(float(p.get("high") or 0)),
                format_brl(float(p.get("low") or 0)),
                format_brl(float(p.get("close") or 0)),
                format_number_br(int(p.get("volume") or 0), 0),
            )
        )
    header = f"**Histórico {ticker.upper()} — {periodo} / {intervalo} (últimos {len(rows)})**\n\n"
    return header + markdown_table(["Data", "Open", "High", "Low", "Close", "Volume"], rows)


async def top_ativos_volume(tipo: str = "stock", limite: int = 15) -> str:
    """Lista ativos da B3 ordenados por volume (desc).

    Args:
        tipo: 'stock' (ações), 'fund' (FIIs), 'bdr'.
        limite: Top N (padrão 15, máx 100).
    """
    limite = max(1, min(limite, 100))
    ativos = await client.listar_ativos(tipo)
    if not ativos:
        return "Sem dados."
    ativos = ativos[:limite]
    rows = [
        (
            a.get("stock") or "—",
            (a.get("name") or "—")[:40],
            format_brl(float(a.get("close") or 0)),
            _fmt_pct(a.get("change")),
            format_number_br(int(a.get("volume") or 0), 0),
        )
        for a in ativos
    ]
    return f"**Top {len(ativos)} {tipo} por volume**\n\n" + markdown_table(
        ["Ticker", "Nome", "Preço", "Var.%", "Volume"], rows
    )


async def indices_b3() -> str:
    """Cotações dos principais índices da B3 (Ibovespa, IFIX, etc.).

    **Requer BRAPI_TOKEN** (índices são endpoint restrito). Sem token,
    retorna apenas o catálogo dos índices disponíveis.
    """
    rows_out: list[tuple[Any, ...]] = []
    for symbol in ("^BVSP", "^IBRX", "^SMLL", "^IFIX"):
        results = await client.cotacao(symbol)
        if results:
            r = results[0]
            rows_out.append(
                (
                    r.get("symbol") or symbol,
                    INDICES_POPULARES.get(symbol, ""),
                    format_number_br(float(r.get("regularMarketPrice") or 0), 0),
                    _fmt_pct(r.get("regularMarketChangePercent")),
                )
            )
    if not rows_out:
        return (
            "**Índices B3** — não foi possível buscar cotações.\n\n"
            "Índices requerem token gratuito do brapi.dev. "
            "Configure `BRAPI_TOKEN` no `.env` ou consulte "
            "https://brapi.dev/dashboard para obter.\n\n"
            "**Catálogo disponível:**\n"
            + "\n".join(f"- `{k}` — {v}" for k, v in INDICES_POPULARES.items())
        )
    return "**Índices B3**\n\n" + markdown_table(
        ["Símbolo", "Descrição", "Pontos", "Var.%"], rows_out
    )


async def blue_chips() -> str:
    """Cotações das principais blue chips da B3."""
    tickers = ",".join(BLUE_CHIPS)
    return await cotacoes_multiplas(tickers)
