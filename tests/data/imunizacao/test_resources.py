"""Tests for the Imunização resources."""

import json

import pytest

from mcp_brasil.data.imunizacao import resources


class TestCalendarioNacional:
    @pytest.mark.asyncio
    async def test_returns_valid_json(self) -> None:
        result = await resources.calendario_nacional()
        data = json.loads(result)
        assert isinstance(data, dict)
        assert "basicas_crianca" in data
        assert "adolescente" in data

    @pytest.mark.asyncio
    async def test_has_vaccines(self) -> None:
        result = await resources.calendario_nacional()
        data = json.loads(result)
        crianca = data["basicas_crianca"]
        assert "vacinas" in crianca
        siglas = {v["sigla"] for v in crianca["vacinas"]}
        assert "BCG" in siglas


class TestMetasCobertura:
    @pytest.mark.asyncio
    async def test_returns_valid_json(self) -> None:
        result = await resources.metas_cobertura_vacinal()
        data = json.loads(result)
        assert isinstance(data, dict)
        assert len(data) > 5

    @pytest.mark.asyncio
    async def test_has_known_vaccines(self) -> None:
        result = await resources.metas_cobertura_vacinal()
        data = json.loads(result)
        assert "BCG" in data
        assert data["BCG"] == 90.0
