"""MCP tools for governadores."""

from __future__ import annotations

from mcp_brasil._shared.formatting import markdown_table

from . import client


async def listar_governadores() -> str:
    """Lista todos os 27 governadores em exercício (26 estados + DF)."""
    govs = await client.listar_todos()
    if not govs:
        return "Nenhum dado disponível."
    govs_sorted = sorted(govs, key=lambda g: g.uf)
    rows = [
        (
            g.uf,
            g.nome,
            f"{g.partido_sigla or '—'} ({g.partido or '—'})",
            g.mandato_inicio or "—",
            g.mandato_fim or "—",
        )
        for g in govs_sorted
    ]
    return "**27 governadores em exercício**\n\n" + markdown_table(
        ["UF", "Nome", "Partido", "Mandato início", "Mandato fim"], rows
    )


async def consultar_governador(uf: str) -> str:
    """Detalhe do governador de uma UF.

    Args:
        uf: Sigla da UF (ex: 'SP', 'RJ', 'DF').
    """
    g = await client.por_uf(uf)
    if g is None:
        return f"UF '{uf}' não encontrada."
    return "\n".join(
        [
            f"**{g.nome}** — Governador de {g.uf}",
            "",
            f"- **Nome completo:** {g.nome_completo or '—'}",
            f"- **Partido:** {g.partido or '—'} ({g.partido_sigla or '—'})",
            f"- **Eleito em:** {g.ano_eleicao or '—'}",
            f"- **Mandato:** {g.mandato_inicio or '—'} a {g.mandato_fim or '—'}",
            f"- **Vice-governador:** {g.vice_governador or '—'}",
        ]
    )


async def governadores_por_partido(partido_sigla: str) -> str:
    """Lista governadores filtrados por sigla partidária.

    Args:
        partido_sigla: Sigla do partido (ex: 'PT', 'PL', 'PP', 'MDB').
    """
    target = partido_sigla.strip().upper()
    govs = await client.listar_todos()
    filtered = [g for g in govs if (g.partido_sigla or "").upper() == target]
    if not filtered:
        return f"Nenhum governador com partido '{target}'."
    filtered_sorted = sorted(filtered, key=lambda g: g.uf)
    rows = [(g.uf, g.nome, g.partido or "—") for g in filtered_sorted]
    return f"**{len(filtered)} governadores do {target}**\n\n" + markdown_table(
        ["UF", "Nome", "Partido"], rows
    )


async def resumo_por_partido() -> str:
    """Distribuição dos 27 governadores por partido (contagem)."""
    govs = await client.listar_todos()
    contagem: dict[str, int] = {}
    for g in govs:
        k = g.partido_sigla or "—"
        contagem[k] = contagem.get(k, 0) + 1
    rows = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
    return f"**Governadores por partido ({sum(contagem.values())} total)**\n\n" + markdown_table(
        ["Partido", "Governadores"], rows
    )
