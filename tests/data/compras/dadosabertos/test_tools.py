"""Tests for the Dados Abertos tool functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_brasil.data.compras.dadosabertos import tools
from mcp_brasil.data.compras.dadosabertos.schemas import (
    ContratoDA,
    ContratoDAResultado,
    FornecedorDA,
    FornecedorDAResultado,
    ItemMaterial,
    ItemMaterialResultado,
    ItemServico,
    ItemServicoResultado,
    Licitacao,
    LicitacaoResultado,
    Uasg,
    UasgResultado,
)

CLIENT_MODULE = "mcp_brasil.data.compras.dadosabertos.client"


def _mock_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    return ctx


# ---------------------------------------------------------------------------
# buscar_licitacoes
# ---------------------------------------------------------------------------


class TestBuscarLicitacoes:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = LicitacaoResultado(
            total=1,
            licitacoes=[
                Licitacao(
                    uasg=154047,
                    nome_modalidade="PREGÃO",
                    objeto="Aquisição de computadores",
                    situacao_aviso="Publicado",
                    valor_estimado_total=50000.0,
                    valor_homologado_total=45000.0,
                    data_publicacao="2020-01-02",
                    numero_itens=10,
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_licitacoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_licitacoes("2020-01-01", "2020-01-31", ctx)
        assert "Aquisição de computadores" in result
        assert "PREGÃO" in result
        assert "154047" in result
        assert "R$ 50.000,00" in result
        assert "R$ 45.000,00" in result
        assert "1 licitações" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = LicitacaoResultado(total=0, licitacoes=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_licitacoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_licitacoes("2020-01-01", "2020-01-31", ctx)
        assert "Nenhuma licitação encontrada" in result


# ---------------------------------------------------------------------------
# buscar_pregoes
# ---------------------------------------------------------------------------


class TestBuscarPregoes:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = LicitacaoResultado(
            total=1,
            licitacoes=[
                Licitacao(
                    uasg=200000,
                    tipo_pregao="eletronico",
                    objeto="Serviço de limpeza",
                    situacao_aviso="Homologado",
                    valor_estimado_total=50000.0,
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_pregoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_pregoes("2020-01-01", "2020-06-30", ctx)
        assert "Serviço de limpeza" in result
        assert "eletronico" in result


# ---------------------------------------------------------------------------
# buscar_dispensas
# ---------------------------------------------------------------------------


class TestBuscarDispensas:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = LicitacaoResultado(
            total=1,
            licitacoes=[
                Licitacao(
                    uasg=300000,
                    nome_modalidade="DISPENSA",
                    objeto="Aquisição emergencial",
                    valor_estimado_total=8000.0,
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_dispensas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_dispensas(2020, ctx)
        assert "Aquisição emergencial" in result
        assert "DISPENSA" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = LicitacaoResultado(total=0, licitacoes=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_dispensas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_dispensas(2020, ctx)
        assert "Nenhuma dispensa encontrada" in result


# ---------------------------------------------------------------------------
# buscar_contratos
# ---------------------------------------------------------------------------


class TestBuscarContratos:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = ContratoDAResultado(
            total=1,
            contratos=[
                ContratoDA(
                    nome_orgao="IFNMG",
                    nome_fornecedor="KM JUNIOR LTDA",
                    ni_fornecedor="13225851000184",
                    numero_contrato="12024/2024",
                    nome_modalidade_compra="Pregão",
                    nome_tipo="Contrato",
                    objeto="AQUISIÇÃO DE ESTUFA",
                    valor_global=118800.0,
                    data_vigencia_inicial="2024-01-08",
                    data_vigencia_final="2025-01-08",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratos",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratos("2024-01-01", "2024-01-31", ctx)
        assert "AQUISIÇÃO DE ESTUFA" in result
        assert "IFNMG" in result
        assert "KM JUNIOR LTDA" in result
        assert "R$ 118.800,00" in result
        assert "1 contratos" in result


# ---------------------------------------------------------------------------
# consultar_fornecedor
# ---------------------------------------------------------------------------


class TestConsultarFornecedor:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = FornecedorDAResultado(
            total=1,
            fornecedores=[
                FornecedorDA(
                    cnpj="33000167000101",
                    nome_razao_social="PETROBRAS",
                    uf_sigla="RJ",
                    nome_municipio="Rio de Janeiro",
                    porte_empresa_nome="DEMAIS",
                    nome_cnae="EXTRAÇÃO DE PETRÓLEO",
                    ativo=True,
                    habilitado_licitar=True,
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_fornecedor",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_fornecedor(ctx, cnpj="33000167000101")
        assert "PETROBRAS" in result
        assert "33000167000101" in result
        assert "RJ" in result
        assert "EXTRAÇÃO DE PETRÓLEO" in result

    @pytest.mark.asyncio
    async def test_missing_filter(self) -> None:
        ctx = _mock_ctx()
        result = await tools.consultar_fornecedor(ctx)
        assert "Informe pelo menos um filtro" in result


# ---------------------------------------------------------------------------
# buscar_material_catmat
# ---------------------------------------------------------------------------


class TestBuscarMaterialCatmat:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = ItemMaterialResultado(
            total=1,
            itens=[
                ItemMaterial(
                    codigo_item=123456,
                    descricao_item="Computador desktop Intel i7",
                    codigo_grupo=70,
                    codigo_classe=7010,
                    codigo_pdm=1234,
                    status_item=True,
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_material",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_material_catmat(ctx, descricao="computador")
        assert "Computador desktop Intel i7" in result
        assert "123456" in result
        assert "70" in result

    @pytest.mark.asyncio
    async def test_missing_filter(self) -> None:
        ctx = _mock_ctx()
        result = await tools.buscar_material_catmat(ctx)
        assert "Informe pelo menos um filtro" in result


# ---------------------------------------------------------------------------
# buscar_servico_catser
# ---------------------------------------------------------------------------


class TestBuscarServicoCatser:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = ItemServicoResultado(
            total=1,
            itens=[
                ItemServico(
                    codigo_servico=5380,
                    nome_servico="SERVIÇO DE LIMPEZA",
                    codigo_grupo=74,
                    codigo_classe=7462,
                    status_servico=True,
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_servico",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_servico_catser(ctx, codigo_grupo=74)
        assert "SERVIÇO DE LIMPEZA" in result
        assert "5380" in result

    @pytest.mark.asyncio
    async def test_missing_filter(self) -> None:
        ctx = _mock_ctx()
        result = await tools.buscar_servico_catser(ctx)
        assert "Informe pelo menos um filtro" in result


# ---------------------------------------------------------------------------
# buscar_uasg
# ---------------------------------------------------------------------------


class TestBuscarUasg:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = UasgResultado(
            total=1,
            uasgs=[
                Uasg(
                    codigo_uasg="154047",
                    nome_uasg="UNIVERSIDADE FEDERAL DE PELOTAS",
                    cnpj_cpf_orgao="92242080000182",
                    sigla_uf="RS",
                    nome_municipio="PELOTAS",
                    uso_sisg=True,
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_uasg",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_uasg(ctx, sigla_uf="RS")
        assert "UNIVERSIDADE FEDERAL DE PELOTAS" in result
        assert "154047" in result
        assert "RS" in result

    @pytest.mark.asyncio
    async def test_missing_filter(self) -> None:
        ctx = _mock_ctx()
        result = await tools.buscar_uasg(ctx)
        assert "Informe pelo menos um filtro" in result
