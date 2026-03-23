"""Tests for the Dados Abertos HTTP client."""

import httpx
import pytest
import respx

from mcp_brasil.data.compras.dadosabertos import client
from mcp_brasil.data.compras.dadosabertos.constants import (
    COMPRAS_SEM_LICITACAO_URL,
    CONTRATOS_URL,
    FORNECEDOR_URL,
    GRUPO_MATERIAL_URL,
    ITEM_MATERIAL_URL,
    ITEM_SERVICO_URL,
    LICITACOES_URL,
    PREGOES_URL,
    UASG_URL,
)

# ---------------------------------------------------------------------------
# buscar_licitacoes
# ---------------------------------------------------------------------------


class TestBuscarLicitacoes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_licitacoes(self) -> None:
        respx.get(LICITACOES_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "resultado": [
                        {
                            "id_compra": "15404705001542019",
                            "identificador": "154047051542019",
                            "numero_processo": "23110047423201960",
                            "uasg": 154047,
                            "modalidade": 5,
                            "nome_modalidade": "PREGÃO",
                            "numero_aviso": 1542019,
                            "situacao_aviso": "Publicado",
                            "tipo_pregao": "eletronico",
                            "objeto": "Aquisição de material de escritório",
                            "valor_estimado_total": 153.5,
                            "valor_homologado_total": 120.0,
                            "numero_itens": 10,
                            "data_publicacao": "2020-01-02",
                            "data_abertura_proposta": "2020-01-14",
                        }
                    ],
                },
            )
        )
        result = await client.buscar_licitacoes(
            data_publicacao_inicial="2020-01-01",
            data_publicacao_final="2020-01-31",
        )
        assert result.total == 1
        assert len(result.licitacoes) == 1
        lic = result.licitacoes[0]
        assert lic.id_compra == "15404705001542019"
        assert lic.uasg == 154047
        assert lic.nome_modalidade == "PREGÃO"
        assert lic.objeto == "Aquisição de material de escritório"
        assert lic.valor_estimado_total == 153.5
        assert lic.valor_homologado_total == 120.0

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(LICITACOES_URL).mock(
            return_value=httpx.Response(200, json={"totalRegistros": 0, "resultado": []})
        )
        result = await client.buscar_licitacoes(
            data_publicacao_inicial="2020-01-01",
            data_publicacao_final="2020-01-01",
        )
        assert result.total == 0
        assert result.licitacoes == []


# ---------------------------------------------------------------------------
# buscar_pregoes
# ---------------------------------------------------------------------------


class TestBuscarPregoes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_pregoes(self) -> None:
        respx.get(PREGOES_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "resultado": [
                        {
                            "id_compra": "ABC123",
                            "uasg": 200000,
                            "nome_modalidade": "PREGÃO",
                            "tipo_pregao": "eletronico",
                            "objeto": "Serviço de limpeza",
                            "situacao_aviso": "Homologado",
                            "valor_estimado_total": 50000.0,
                        }
                    ],
                },
            )
        )
        result = await client.buscar_pregoes(
            data_edital_inicial="2020-01-01",
            data_edital_final="2020-06-30",
        )
        assert result.total == 1
        assert result.licitacoes[0].objeto == "Serviço de limpeza"


# ---------------------------------------------------------------------------
# buscar_dispensas
# ---------------------------------------------------------------------------


class TestBuscarDispensas:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_dispensas(self) -> None:
        respx.get(COMPRAS_SEM_LICITACAO_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "resultado": [
                        {
                            "id_compra": "DISP001",
                            "uasg": 300000,
                            "nome_modalidade": "DISPENSA",
                            "objeto": "Aquisição emergencial",
                            "valor_estimado_total": 8000.0,
                        }
                    ],
                },
            )
        )
        result = await client.buscar_dispensas(ano_aviso=2020)
        assert result.total == 1
        assert result.licitacoes[0].objeto == "Aquisição emergencial"


# ---------------------------------------------------------------------------
# buscar_contratos
# ---------------------------------------------------------------------------


class TestBuscarContratos:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_contratos(self) -> None:
        respx.get(CONTRATOS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "resultado": [
                        {
                            "codigoOrgao": "26410",
                            "nomeOrgao": "IFNMG",
                            "codigoUnidadeGestora": "158439",
                            "nomeUnidadeGestora": "IFNMG Campus Almenara",
                            "numeroContrato": "12024/2024",
                            "nomeModalidadeCompra": "Pregão",
                            "nomeTipo": "Contrato",
                            "nomeCategoria": "Compras",
                            "niFornecedor": "13225851000184",
                            "nomeRazaoSocialFornecedor": "KM JUNIOR LTDA",
                            "processo": "23390.001121/2023-22",
                            "objeto": "AQUISIÇÃO DE ESTUFA AGRÍCOLA",
                            "dataVigenciaInicial": "2024-01-08T00:00:00",
                            "dataVigenciaFinal": "2025-01-08T00:00:00",
                            "valorGlobal": 118800.0,
                            "valorParcela": 118800.0,
                            "valorAcumulado": 118800.0,
                        }
                    ],
                },
            )
        )
        result = await client.buscar_contratos(
            data_vigencia_inicial_min="2024-01-01",
            data_vigencia_inicial_max="2024-01-31",
        )
        assert result.total == 1
        c = result.contratos[0]
        assert c.codigo_orgao == "26410"
        assert c.nome_orgao == "IFNMG"
        assert c.ni_fornecedor == "13225851000184"
        assert c.nome_fornecedor == "KM JUNIOR LTDA"
        assert c.objeto == "AQUISIÇÃO DE ESTUFA AGRÍCOLA"
        assert c.valor_global == 118800.0

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(CONTRATOS_URL).mock(
            return_value=httpx.Response(200, json={"totalRegistros": 0, "resultado": []})
        )
        result = await client.buscar_contratos(
            data_vigencia_inicial_min="2024-01-01",
            data_vigencia_inicial_max="2024-01-01",
        )
        assert result.total == 0
        assert result.contratos == []


# ---------------------------------------------------------------------------
# consultar_fornecedor
# ---------------------------------------------------------------------------


class TestConsultarFornecedor:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_fornecedor(self) -> None:
        respx.get(FORNECEDOR_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "resultado": [
                        {
                            "cnpj": "33000167000101",
                            "cpf": None,
                            "nomeRazaoSocialFornecedor": "PETROBRAS",
                            "ufSigla": "RJ",
                            "nomeMunicipio": "Rio de Janeiro",
                            "porteEmpresaNome": "DEMAIS",
                            "naturezaJuridicaNome": "SOCIEDADE DE ECONOMIA MISTA",
                            "nomeCnae": "EXTRAÇÃO DE PETRÓLEO",
                            "ativo": True,
                            "habilitadoLicitar": True,
                        }
                    ],
                },
            )
        )
        result = await client.consultar_fornecedor(cnpj="33000167000101")
        assert result.total == 1
        f = result.fornecedores[0]
        assert f.cnpj == "33000167000101"
        assert f.nome_razao_social == "PETROBRAS"
        assert f.uf_sigla == "RJ"
        assert f.ativo is True


# ---------------------------------------------------------------------------
# listar_grupos_material
# ---------------------------------------------------------------------------


class TestListarGruposMaterial:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_grupos(self) -> None:
        respx.get(GRUPO_MATERIAL_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 2,
                    "resultado": [
                        {
                            "codigoGrupo": 70,
                            "nomeGrupo": "INFORMÁTICA - TIC",
                            "statusGrupo": True,
                        },
                        {
                            "codigoGrupo": 71,
                            "nomeGrupo": "MOBILIÁRIOS",
                            "statusGrupo": True,
                        },
                    ],
                },
            )
        )
        result = await client.listar_grupos_material()
        assert result.total == 2
        assert result.grupos[0].codigo_grupo == 70
        assert result.grupos[0].nome_grupo == "INFORMÁTICA - TIC"


# ---------------------------------------------------------------------------
# buscar_material
# ---------------------------------------------------------------------------


class TestBuscarMaterial:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_itens(self) -> None:
        respx.get(ITEM_MATERIAL_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "resultado": [
                        {
                            "codigoItem": 123456,
                            "descricaoItem": "Computador desktop Intel i7",
                            "codigoGrupo": 70,
                            "codigoClasse": 7010,
                            "codigoPdm": 1234,
                            "statusItem": True,
                        }
                    ],
                },
            )
        )
        result = await client.buscar_material(descricao="computador")
        assert result.total == 1
        item = result.itens[0]
        assert item.codigo_item == 123456
        assert item.descricao_item == "Computador desktop Intel i7"
        assert item.codigo_grupo == 70


# ---------------------------------------------------------------------------
# buscar_servico
# ---------------------------------------------------------------------------


class TestBuscarServico:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_servicos(self) -> None:
        respx.get(ITEM_SERVICO_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "resultado": [
                        {
                            "codigoServico": 5380,
                            "nomeServico": "SERVIÇO DE LIMPEZA E CONSERVAÇÃO",
                            "codigoSecao": 1,
                            "codigoDivisao": 7,
                            "codigoGrupo": 74,
                            "codigoClasse": 7462,
                            "statusServico": True,
                        }
                    ],
                },
            )
        )
        result = await client.buscar_servico(codigo_grupo=74)
        assert result.total == 1
        assert result.itens[0].nome_servico == "SERVIÇO DE LIMPEZA E CONSERVAÇÃO"


# ---------------------------------------------------------------------------
# buscar_uasg
# ---------------------------------------------------------------------------


class TestBuscarUasg:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_uasgs(self) -> None:
        respx.get(UASG_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "resultado": [
                        {
                            "codigoUasg": "154047",
                            "nomeUasg": "UNIVERSIDADE FEDERAL DE PELOTAS",
                            "cnpjCpfOrgao": "92242080000182",
                            "siglaUf": "RS",
                            "nomeMunicipio": "PELOTAS",
                            "usoSisg": True,
                            "statusUasg": True,
                        }
                    ],
                },
            )
        )
        result = await client.buscar_uasg(sigla_uf="RS")
        assert result.total == 1
        u = result.uasgs[0]
        assert u.codigo_uasg == "154047"
        assert u.nome_uasg == "UNIVERSIDADE FEDERAL DE PELOTAS"
        assert u.sigla_uf == "RS"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(UASG_URL).mock(
            return_value=httpx.Response(200, json={"totalRegistros": 0, "resultado": []})
        )
        result = await client.buscar_uasg(codigo_uasg="999999")
        assert result.total == 0
        assert result.uasgs == []
