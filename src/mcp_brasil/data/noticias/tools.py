"""MCP tools for noticias."""

from __future__ import annotations

from mcp_brasil._shared.formatting import markdown_table

from . import client
from .constants import FEEDS_ECONOMIA, FEEDS_POLITICA, FEEDS_TEMAS_CAMARA, TODAS_FONTES


async def listar_fontes() -> str:
    """Lista todas as fontes RSS disponíveis, agrupadas por categoria."""
    lines = ["**Fontes RSS disponíveis**\n", "### Política (Congresso e Agência Brasil)"]
    for k, url in FEEDS_POLITICA.items():
        lines.append(f"- `{k}` — {url}")
    lines.append("\n### Economia")
    for k, url in FEEDS_ECONOMIA.items():
        lines.append(f"- `{k}` — {url}")
    lines.append("\n### Temas Câmara")
    for k, url in FEEDS_TEMAS_CAMARA.items():
        lines.append(f"- `{k}` — {url}")
    return "\n".join(lines)


async def ultimas_noticias(fonte: str, limite: int = 20) -> str:
    """Últimas notícias de uma fonte RSS.

    Args:
        fonte: Chave da fonte (veja ``listar_fontes``). Ex: 'camara_ultimas',
            'senado_ultimas', 'agencia_brasil_politica'.
        limite: Máximo de itens (padrão 20, máx 100).
    """
    if fonte not in TODAS_FONTES:
        return f"Fonte '{fonte}' não registrada. Use listar_fontes() para ver opções."
    limite = max(1, min(limite, 100))
    items = await client.fetch_feed(fonte)
    if not items:
        return f"Nenhuma notícia retornada de '{fonte}'."
    items = items[:limite]
    rows = [
        (
            (i.get("pubDate") or "")[:25],
            (i.get("title") or "—")[:80],
            i.get("link") or "",
        )
        for i in items
    ]
    return f"**{len(items)} notícias de `{fonte}`**\n\n" + markdown_table(
        ["data", "título", "link"], rows
    )


async def buscar_noticias(fonte: str, termo: str, limite: int = 20) -> str:
    """Filtra notícias de uma fonte por termo no título ou descrição.

    Args:
        fonte: Chave da fonte.
        termo: Palavra-chave a buscar (case-insensitive).
        limite: Máximo (padrão 20).
    """
    if fonte not in TODAS_FONTES:
        return f"Fonte '{fonte}' não registrada."
    limite = max(1, min(limite, 100))
    items = await client.fetch_feed(fonte)
    t = termo.lower()
    filtered = [
        i
        for i in items
        if t in (i.get("title") or "").lower() or t in (i.get("description") or "").lower()
    ]
    if not filtered:
        return f"Nenhuma notícia de '{fonte}' menciona '{termo}'."
    filtered = filtered[:limite]
    rows = [
        ((i.get("pubDate") or "")[:25], (i.get("title") or "—")[:80], i.get("link") or "")
        for i in filtered
    ]
    return f"**{len(filtered)} notícias de `{fonte}` com '{termo}'**\n\n" + markdown_table(
        ["data", "título", "link"], rows
    )


async def resumo_politica(limite_por_fonte: int = 5) -> str:
    """Resumo consolidado das últimas notícias políticas (Câmara + Senado + Agência Brasil).

    Args:
        limite_por_fonte: Itens por fonte (padrão 5, máx 20).
    """
    limite_por_fonte = max(1, min(limite_por_fonte, 20))
    out: list[str] = ["**Resumo — Política**\n"]
    for fonte in ("camara_ultimas", "senado_ultimas", "agencia_brasil_politica"):
        try:
            items = await client.fetch_feed(fonte)
        except Exception as exc:
            out.append(f"\n### {fonte} — erro: {exc}")
            continue
        out.append(f"\n### {fonte}")
        for i in items[:limite_por_fonte]:
            title = (i.get("title") or "—")[:120]
            link = i.get("link") or ""
            out.append(f"- **{title}** — {link}")
    return "\n".join(out)
