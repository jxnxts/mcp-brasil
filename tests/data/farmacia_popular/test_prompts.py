"""Tests for the Farmácia Popular prompts."""

import pytest
from fastmcp import Client

from mcp_brasil.data.farmacia_popular.prompts import assistente_farmacia_popular
from mcp_brasil.data.farmacia_popular.server import mcp


class TestAssistenteFarmaciaPopular:
    def test_returns_instructions(self) -> None:
        result = assistente_farmacia_popular(indicacao="diabetes")
        assert "diabetes" in result
        assert "buscar_por_indicacao" in result
        assert "verificar_elegibilidade" in result
        assert "buscar_farmacias" in result

    def test_prompt_with_different_indication(self) -> None:
        result = assistente_farmacia_popular(indicacao="hipertensão")
        assert "hipertensão" in result


class TestPromptsRegistered:
    @pytest.mark.asyncio
    async def test_prompt_registered(self) -> None:
        async with Client(mcp) as c:
            prompts = await c.list_prompts()
            names = {p.name for p in prompts}
            assert "assistente_farmacia_popular" in names
