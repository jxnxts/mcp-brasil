"""Tests for the Imunização prompts."""

import pytest

from mcp_brasil.data.imunizacao import prompts


class TestAnaliseCobertura:
    @pytest.mark.asyncio
    async def test_includes_municipio(self) -> None:
        result = await prompts.analise_cobertura_vacinal("Teresina")
        assert "Teresina" in result

    @pytest.mark.asyncio
    async def test_includes_tool_names(self) -> None:
        result = await prompts.analise_cobertura_vacinal("São Paulo")
        assert "estatisticas_por_vacina" in result
        assert "metas_cobertura" in result
        assert "buscar_vacinacao" in result

    @pytest.mark.asyncio
    async def test_includes_instructions(self) -> None:
        result = await prompts.analise_cobertura_vacinal("Recife")
        assert "cobertura" in result.lower()
        assert "PNI" in result or "DataSUS" in result
