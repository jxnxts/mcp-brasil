"""Tests for the PNCP tool functions.

Tools are tested by mocking client functions (never HTTP).
Context is mocked via MagicMock with async methods.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_brasil.data.compras.pncp import tools
from mcp_brasil.data.compras.pncp.schemas import (
    AtaRegistroPreco,
    AtaResultado,
    Contratacao,
    ContratacaoResultado,
    Contrato,
    ContratoResultado,
    Fornecedor,
    FornecedorResultado,
    InstrumentoCobranca,
    InstrumentoCobrancaResultado,
    OrgaoContratante,
    OrgaoResultado,
    Pca,
    PcaResultado,
)

CLIENT_MODULE = "mcp_brasil.data.compras.pncp.client"

# Common test dates
DATE_INI = "20240101"
DATE_FIM = "20240331"


def _mock_ctx() -> MagicMock:
    """Create a mock Context with async log methods."""
    ctx = MagicMock()
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    return ctx


# ---------------------------------------------------------------------------
# buscar_contratacoes
# ---------------------------------------------------------------------------


class TestBuscarContratacoes:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = ContratacaoResultado(
            total=1,
            contratacoes=[
                Contratacao(
                    orgao_cnpj="00394460000141",
                    orgao_nome="Ministério da Educação",
                    objeto="Aquisição de computadores",
                    modalidade_id=6,
                    modalidade_nome="Pregão - Eletrônico",
                    situacao_nome="Publicada",
                    valor_estimado=500000.0,
                    valor_homologado=480000.0,
                    data_publicacao="2024-03-15",
                    municipio="Brasília",
                    uf="DF",
                    esfera="Federal",
                    link_pncp="https://pncp.gov.br/app/editais/123",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratacoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratacoes(DATE_INI, DATE_FIM, 6, ctx)
        assert "Aquisição de computadores" in result
        assert "Ministério da Educação" in result
        assert "00394460000141" in result
        assert "Pregão - Eletrônico" in result
        assert "Publicada" in result
        assert "R$ 500.000,00" in result
        assert "R$ 480.000,00" in result
        assert "Brasília" in result
        assert "DF" in result
        assert "Federal" in result
        assert "Ver no PNCP" in result
        assert "1 contratações" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = ContratacaoResultado(total=0, contratacoes=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratacoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratacoes(DATE_INI, DATE_FIM, 6, ctx)
        assert "Nenhuma contratação encontrada" in result

    @pytest.mark.asyncio
    async def test_validation_error(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratacoes",
            new_callable=AsyncMock,
            side_effect=ValueError("data_final é anterior a data_inicial"),
        ):
            result = await tools.buscar_contratacoes("20240331", "20240101", 6, ctx)
        assert "Erro de validação" in result


# ---------------------------------------------------------------------------
# buscar_contratos
# ---------------------------------------------------------------------------


class TestBuscarContratos:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = ContratoResultado(
            total=1,
            contratos=[
                Contrato(
                    orgao_cnpj="00394460000141",
                    orgao_nome="Ministério da Saúde",
                    numero_contrato="2024/001",
                    objeto="Fornecimento de medicamentos",
                    fornecedor_cnpj="12345678000199",
                    fornecedor_nome="Empresa Pharma LTDA",
                    valor_inicial=100000.0,
                    valor_final=95000.0,
                    vigencia_inicio="2024-01-01",
                    vigencia_fim="2024-12-31",
                    situacao="Vigente",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratos",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratos(DATE_INI, DATE_FIM, ctx, texto="medicamentos")
        assert "Fornecimento de medicamentos" in result
        assert "Ministério da Saúde" in result
        assert "Empresa Pharma LTDA" in result
        assert "12345678000199" in result
        assert "2024/001" in result
        assert "R$ 95.000,00" in result
        assert "2024-01-01" in result
        assert "2024-12-31" in result
        assert "Vigente" in result
        assert "1 contratos" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = ContratoResultado(total=0, contratos=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratos",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratos(DATE_INI, DATE_FIM, ctx)
        assert "Nenhum contrato encontrado" in result

    @pytest.mark.asyncio
    async def test_validation_error(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratos",
            new_callable=AsyncMock,
            side_effect=ValueError("Período excede o máximo"),
        ):
            result = await tools.buscar_contratos("20240101", "20260101", ctx)
        assert "Erro de validação" in result


# ---------------------------------------------------------------------------
# buscar_atas
# ---------------------------------------------------------------------------


class TestBuscarAtas:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = AtaResultado(
            total=1,
            atas=[
                AtaRegistroPreco(
                    orgao_cnpj="00394460000141",
                    orgao_nome="Universidade Federal",
                    numero_ata="2024/010",
                    objeto="Registro de preços para material de escritório",
                    fornecedor_cnpj="98765432000155",
                    fornecedor_nome="Papelaria Central LTDA",
                    valor_total=250000.0,
                    vigencia_inicio="2024-06-01",
                    vigencia_fim="2025-05-31",
                    situacao="Vigente",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_atas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_atas(DATE_INI, DATE_FIM, ctx, texto="escritório")
        assert "material de escritório" in result
        assert "Universidade Federal" in result
        assert "Papelaria Central LTDA" in result
        assert "98765432000155" in result
        assert "2024/010" in result
        assert "R$ 250.000,00" in result
        assert "2024-06-01" in result
        assert "2025-05-31" in result
        assert "Vigente" in result
        assert "1 atas" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = AtaResultado(total=0, atas=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_atas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_atas(DATE_INI, DATE_FIM, ctx)
        assert "Nenhuma ata de registro de preço encontrada" in result

    @pytest.mark.asyncio
    async def test_validation_error(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_atas",
            new_callable=AsyncMock,
            side_effect=ValueError("data_final é anterior"),
        ):
            result = await tools.buscar_atas("20240331", "20240101", ctx)
        assert "Erro de validação" in result


# ---------------------------------------------------------------------------
# consultar_fornecedor
# ---------------------------------------------------------------------------


class TestConsultarFornecedor:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = FornecedorResultado(
            total=1,
            fornecedores=[
                Fornecedor(
                    cnpj="12345678000199",
                    razao_social="Empresa Teste LTDA",
                    nome_fantasia="Teste Corp",
                    municipio="São Paulo",
                    uf="SP",
                    porte="Médio",
                    data_abertura="2010-05-20",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_fornecedor",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_fornecedor("12345678000199", ctx)
        assert "Empresa Teste LTDA" in result
        assert "12345678000199" in result
        assert "Teste Corp" in result
        assert "São Paulo" in result
        assert "SP" in result
        assert "Médio" in result
        assert "2010-05-20" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = FornecedorResultado(total=0, fornecedores=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_fornecedor",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_fornecedor("00000000000000", ctx)
        assert "Nenhum fornecedor encontrado" in result
        assert "00000000000000" in result


# ---------------------------------------------------------------------------
# consultar_orgao
# ---------------------------------------------------------------------------


class TestConsultarOrgao:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = OrgaoResultado(
            total=1,
            orgaos=[
                OrgaoContratante(
                    cnpj="00394460000141",
                    razao_social="Ministério da Educação",
                    esfera="Federal",
                    poder="Executivo",
                    uf="DF",
                    municipio="Brasília",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_orgao",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_orgao(ctx, texto="educação")
        assert "Ministério da Educação" in result
        assert "00394460000141" in result
        assert "Federal" in result
        assert "Executivo" in result
        assert "DF" in result
        assert "Brasília" in result
        assert "1 órgãos" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = OrgaoResultado(total=0, orgaos=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_orgao",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_orgao(ctx, texto="xyzinexistente")
        assert "Nenhum órgão encontrado" in result
        assert "xyzinexistente" in result

    @pytest.mark.asyncio
    async def test_missing_filter_validation(self) -> None:
        ctx = _mock_ctx()
        result = await tools.consultar_orgao(ctx)
        assert "Informe pelo menos um filtro" in result


# ---------------------------------------------------------------------------
# buscar_contratacoes_abertas
# ---------------------------------------------------------------------------


class TestBuscarContratacoeAbertas:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = ContratacaoResultado(
            total=1,
            contratacoes=[
                Contratacao(
                    orgao_cnpj="00394460000141",
                    orgao_nome="Ministério da Defesa",
                    objeto="Aquisição de uniformes",
                    modalidade_id=6,
                    situacao_nome="Divulgada",
                    valor_estimado=200000.0,
                    data_abertura="2024-04-01",
                    municipio="Brasília",
                    uf="DF",
                    link_pncp="https://pncp.gov.br/app/editais/456",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratacoes_abertas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratacoes_abertas(DATE_FIM, ctx)
        assert "Aquisição de uniformes" in result
        assert "Ministério da Defesa" in result
        assert "R$ 200.000,00" in result
        assert "Ver no PNCP" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = ContratacaoResultado(total=0, contratacoes=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratacoes_abertas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratacoes_abertas(DATE_FIM, ctx)
        assert "Nenhuma contratação com proposta aberta" in result

    @pytest.mark.asyncio
    async def test_validation_error(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratacoes_abertas",
            new_callable=AsyncMock,
            side_effect=ValueError("Formato inválido"),
        ):
            result = await tools.buscar_contratacoes_abertas("invalido", ctx)
        assert "Erro de validação" in result


# ---------------------------------------------------------------------------
# buscar_contratacoes_atualizadas
# ---------------------------------------------------------------------------


class TestBuscarContratacoeAtualizadas:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = ContratacaoResultado(
            total=1,
            contratacoes=[
                Contratacao(
                    orgao_nome="IBAMA",
                    objeto="Serviço de vigilância",
                    modalidade_id=6,
                    situacao_nome="Homologada",
                    valor_estimado=300000.0,
                    valor_homologado=280000.0,
                    data_publicacao="2024-02-10",
                    municipio="Brasília",
                    uf="DF",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratacoes_atualizadas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratacoes_atualizadas(DATE_INI, DATE_FIM, 6, ctx)
        assert "Serviço de vigilância" in result
        assert "IBAMA" in result
        assert "contratações atualizadas" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = ContratacaoResultado(total=0, contratacoes=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratacoes_atualizadas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratacoes_atualizadas(DATE_INI, DATE_FIM, 6, ctx)
        assert "Nenhuma contratação atualizada" in result


# ---------------------------------------------------------------------------
# buscar_contratos_atualizados
# ---------------------------------------------------------------------------


class TestBuscarContratosAtualizados:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = ContratoResultado(
            total=1,
            contratos=[
                Contrato(
                    orgao_nome="INSS",
                    numero_contrato="2024/050",
                    objeto="Manutenção predial",
                    fornecedor_nome="Construtora ABC",
                    fornecedor_cnpj="11222333000144",
                    valor_final=750000.0,
                    vigencia_inicio="2024-01-01",
                    vigencia_fim="2025-12-31",
                    situacao="Vigente",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratos_atualizados",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratos_atualizados(DATE_INI, DATE_FIM, ctx)
        assert "Manutenção predial" in result
        assert "INSS" in result
        assert "Construtora ABC" in result
        assert "contratos atualizados" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = ContratoResultado(total=0, contratos=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_contratos_atualizados",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_contratos_atualizados(DATE_INI, DATE_FIM, ctx)
        assert "Nenhum contrato atualizado" in result


# ---------------------------------------------------------------------------
# buscar_atas_atualizadas
# ---------------------------------------------------------------------------


class TestBuscarAtasAtualizadas:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = AtaResultado(
            total=1,
            atas=[
                AtaRegistroPreco(
                    orgao_cnpj="00394460000141",
                    orgao_nome="IFSP",
                    numero_ata="2024/015",
                    objeto="Material de limpeza",
                    vigencia_inicio="2024-03-01",
                    vigencia_fim="2025-02-28",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_atas_atualizadas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_atas_atualizadas(DATE_INI, DATE_FIM, ctx)
        assert "Material de limpeza" in result
        assert "IFSP" in result
        assert "atas atualizadas" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = AtaResultado(total=0, atas=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_atas_atualizadas",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_atas_atualizadas(DATE_INI, DATE_FIM, ctx)
        assert "Nenhuma ata atualizada" in result


# ---------------------------------------------------------------------------
# consultar_contratacao_detalhe
# ---------------------------------------------------------------------------


class TestConsultarContratacaoDetalhe:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = Contratacao(
            orgao_cnpj="00394460000141",
            orgao_nome="Ministério da Educação",
            numero_controle_pncp="00394460000141-1-000001/2024",
            objeto="Aquisição de mobiliário escolar",
            modalidade_id=6,
            situacao_nome="Homologada",
            valor_estimado=1000000.0,
            valor_homologado=950000.0,
            data_publicacao="2024-01-15",
            data_abertura="2024-02-01",
            municipio="Brasília",
            uf="DF",
            esfera="Federal",
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_contratacao_detalhe",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_contratacao_detalhe("00394460000141", 2024, 1, ctx)
        assert "Aquisição de mobiliário escolar" in result
        assert "R$ 1.000.000,00" in result
        assert "R$ 950.000,00" in result
        assert "Homologada" in result
        assert "00394460000141-1-000001/2024" in result


# ---------------------------------------------------------------------------
# buscar_pca
# ---------------------------------------------------------------------------


class TestBuscarPca:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = PcaResultado(
            total=1,
            pcas=[
                Pca(
                    orgao_cnpj="00394460000141",
                    orgao_nome="Ministério da Educação",
                    ano=2025,
                    unidade_nome="Secretaria de Educação Básica",
                    id_pca="PCA-2025-001",
                    data_publicacao="2024-12-20",
                    itens=[],
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_pca",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_pca(2025, ctx)
        assert "Ministério da Educação" in result
        assert "2025" in result
        assert "Secretaria de Educação Básica" in result
        assert "PCA-2025-001" in result
        assert "PCAs" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = PcaResultado(total=0, pcas=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_pca",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_pca(2030, ctx)
        assert "Nenhum PCA encontrado" in result


# ---------------------------------------------------------------------------
# buscar_pca_atualizacao
# ---------------------------------------------------------------------------


class TestBuscarPcaAtualizacao:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = PcaResultado(
            total=1,
            pcas=[
                Pca(
                    orgao_cnpj="00394460000141",
                    orgao_nome="INSS",
                    ano=2025,
                    unidade_nome="Diretoria",
                    data_publicacao="2025-01-10",
                    itens=[],
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_pca_atualizacao",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_pca_atualizacao(DATE_INI, DATE_FIM, ctx)
        assert "INSS" in result
        assert "PCAs atualizados" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = PcaResultado(total=0, pcas=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_pca_atualizacao",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_pca_atualizacao(DATE_INI, DATE_FIM, ctx)
        assert "Nenhum PCA atualizado" in result


# ---------------------------------------------------------------------------
# buscar_pca_usuario
# ---------------------------------------------------------------------------


class TestBuscarPcaUsuario:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = PcaResultado(
            total=1,
            pcas=[
                Pca(
                    orgao_cnpj="00394460000141",
                    orgao_nome="Universidade Federal",
                    ano=2025,
                    unidade_nome="Reitoria",
                    data_publicacao="2025-02-01",
                    itens=[],
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_pca_usuario",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_pca_usuario(2025, 12345, ctx)
        assert "Universidade Federal" in result
        assert "Reitoria" in result
        assert "PCAs" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = PcaResultado(total=0, pcas=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_pca_usuario",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_pca_usuario(2025, 99999, ctx)
        assert "Nenhum PCA encontrado" in result


# ---------------------------------------------------------------------------
# buscar_instrumentos_cobranca
# ---------------------------------------------------------------------------


class TestBuscarInstrumentosCobranca:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = InstrumentoCobrancaResultado(
            total=1,
            instrumentos=[
                InstrumentoCobranca(
                    cnpj_orgao="00394460000141",
                    ano_contrato=2024,
                    numero_instrumento="NF-001",
                    tipo_nome="Nota Fiscal Eletrônica",
                    data_emissao="2024-03-01",
                    objeto_contrato="Fornecimento de alimentos",
                    fornecedor_nome="Distribuidora XYZ",
                    fornecedor_cnpj="98765432000155",
                    valor_nf="150000.00",
                ),
            ],
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_instrumentos_cobranca",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_instrumentos_cobranca(DATE_INI, DATE_FIM, ctx)
        assert "Fornecimento de alimentos" in result
        assert "Distribuidora XYZ" in result
        assert "98765432000155" in result
        assert "NF-001" in result
        assert "Nota Fiscal Eletrônica" in result
        assert "instrumentos de cobrança" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        mock_data = InstrumentoCobrancaResultado(total=0, instrumentos=[])
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_instrumentos_cobranca",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_instrumentos_cobranca(DATE_INI, DATE_FIM, ctx)
        assert "Nenhum instrumento de cobrança" in result

    @pytest.mark.asyncio
    async def test_validation_error(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.buscar_instrumentos_cobranca",
            new_callable=AsyncMock,
            side_effect=ValueError("Período excede o máximo"),
        ):
            result = await tools.buscar_instrumentos_cobranca("20240101", "20260101", ctx)
        assert "Erro de validação" in result
