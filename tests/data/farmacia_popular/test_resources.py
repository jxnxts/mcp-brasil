"""Tests for the Farmácia Popular resources."""

import json

import pytest
from fastmcp import Client

from mcp_brasil.data.farmacia_popular.resources import (
    catalogo_medicamentos,
    indicacoes_terapeuticas,
)
from mcp_brasil.data.farmacia_popular.server import mcp


class TestCatalogoMedicamentos:
    def test_returns_valid_json(self) -> None:
        result = catalogo_medicamentos()
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) >= 30

    def test_medications_have_fields(self) -> None:
        result = catalogo_medicamentos()
        data = json.loads(result)
        for med in data:
            assert "nome" in med
            assert "principio_ativo" in med
            assert "indicacao" in med


class TestIndicacoesTerapeuticas:
    def test_returns_valid_json(self) -> None:
        result = indicacoes_terapeuticas()
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) >= 9

    def test_contains_main_indications(self) -> None:
        result = indicacoes_terapeuticas()
        data = json.loads(result)
        assert "Hipertensão" in data
        assert "Diabetes" in data
        assert "Asma" in data


class TestResourcesRegistered:
    @pytest.mark.asyncio
    async def test_resources_registered(self) -> None:
        async with Client(mcp) as c:
            resources = await c.list_resources()
            uris = {str(r.uri) for r in resources}
            assert "data://catalogo-medicamentos" in uris
            assert "data://indicacoes-terapeuticas" in uris
