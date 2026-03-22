"""Tests for the Senado tool functions.

Tools are tested by mocking client functions (never HTTP).
"""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_brasil.senado import tools
from mcp_brasil.senado.schemas import (
    ComissaoDetalhe,
    ComissaoResumo,
    LegislaturaInfo,
    MateriaDetalhe,
    MateriaResumo,
    MembroComissao,
    ReuniaoComissao,
    SenadorDetalhe,
    SenadorResumo,
    SessaoPlenario,
    Tramitacao,
    VotacaoDetalhe,
    VotacaoResumo,
)

MODULE = "mcp_brasil.senado.client"


# ---------------------------------------------------------------------------
# Senadores (4)
# ---------------------------------------------------------------------------


class TestListarSenadores:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [SenadorResumo(codigo="5012", nome="Senador Teste", partido="PT", uf="SP")]
        with patch(f"{MODULE}.listar_senadores", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.listar_senadores()
        assert "Senador Teste" in result
        assert "PT" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.listar_senadores", new_callable=AsyncMock, return_value=[]):
            result = await tools.listar_senadores()
        assert "Nenhum senador" in result


class TestBuscarSenador:
    @pytest.mark.asyncio
    async def test_formats_profile(self) -> None:
        mock_data = SenadorDetalhe(
            codigo="5012",
            nome="Sen. Teste",
            nome_completo="Senador Teste da Silva",
            partido="PT",
            uf="SP",
            email="teste@senado.leg.br",
            mandato_inicio="2023-02-01",
            mandato_fim="2031-01-31",
        )
        with patch(f"{MODULE}.obter_senador", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.buscar_senador("5012")
        assert "Senador Teste da Silva" in result
        assert "PT" in result
        assert "2023-02-01" in result

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        with patch(f"{MODULE}.obter_senador", new_callable=AsyncMock, return_value=None):
            result = await tools.buscar_senador("99999")
        assert "não encontrado" in result


class TestBuscarSenadorPorNome:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [SenadorResumo(codigo="5012", nome="Maria", partido="PT", uf="SP")]
        with patch(
            f"{MODULE}.buscar_senador_por_nome",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.buscar_senador_por_nome("Maria")
        assert "Maria" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(
            f"{MODULE}.buscar_senador_por_nome",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await tools.buscar_senador_por_nome("Inexistente")
        assert "Nenhum senador" in result


class TestVotacoesSenador:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            VotacaoResumo(
                codigo="VOT-1", data="2024-06-01", descricao="PEC da reforma", resultado="Aprovada"
            )
        ]
        with patch(f"{MODULE}.votacoes_senador", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.votacoes_senador("5012")
        assert "PEC da reforma" in result
        assert "Aprovada" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.votacoes_senador", new_callable=AsyncMock, return_value=[]):
            result = await tools.votacoes_senador("5012")
        assert "Nenhuma votação" in result


# ---------------------------------------------------------------------------
# Matérias (5)
# ---------------------------------------------------------------------------


class TestBuscarMateria:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            MateriaResumo(
                sigla_tipo="PEC",
                numero="45",
                ano="2024",
                ementa="Altera a Constituição",
                data_apresentacao="2024-03-15",
            )
        ]
        with patch(f"{MODULE}.buscar_materias", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.buscar_materia(sigla_tipo="PEC")
        assert "PEC" in result
        assert "Constituição" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.buscar_materias", new_callable=AsyncMock, return_value=[]):
            result = await tools.buscar_materia()
        assert "Nenhuma matéria" in result


class TestDetalheMateria:
    @pytest.mark.asyncio
    async def test_formats_detail(self) -> None:
        mock_data = MateriaDetalhe(
            sigla_tipo="PEC",
            numero="45",
            ano="2024",
            ementa="Altera a Constituição",
            autor="Sen. Fulano",
            situacao="Tramitando",
            casa_origem="Senado Federal",
        )
        with patch(f"{MODULE}.obter_materia", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.detalhe_materia("150001")
        assert "PEC 45/2024" in result
        assert "Sen. Fulano" in result
        assert "Senado Federal" in result

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        with patch(f"{MODULE}.obter_materia", new_callable=AsyncMock, return_value=None):
            result = await tools.detalhe_materia("99999")
        assert "não encontrada" in result


class TestConsultarTramitacaoMateria:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            Tramitacao(data="2024-03-15", descricao="Recebida", local="CCJ", situacao="Tramitando")
        ]
        with patch(f"{MODULE}.tramitacao_materia", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.consultar_tramitacao_materia("150001")
        assert "Recebida" in result
        assert "CCJ" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.tramitacao_materia", new_callable=AsyncMock, return_value=[]):
            result = await tools.consultar_tramitacao_materia("99999")
        assert "Nenhuma tramitação" in result


class TestTextosMateria:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            {"tipo": "Texto Original", "data": "2024-03-15", "url": "https://senado.leg.br/doc"}
        ]
        with patch(f"{MODULE}.textos_materia", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.textos_materia("150001")
        assert "Texto Original" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.textos_materia", new_callable=AsyncMock, return_value=[]):
            result = await tools.textos_materia("99999")
        assert "Nenhum texto" in result


class TestVotosMateria:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            VotacaoDetalhe(
                codigo="VOT-001",
                data="2024-06-01",
                descricao="Votação em turno único",
                resultado="Aprovada",
                sim=50,
                nao=20,
                abstencao=3,
            )
        ]
        with patch(f"{MODULE}.votos_materia", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.votos_materia("150001")
        assert "Aprovada" in result
        assert "S:50" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.votos_materia", new_callable=AsyncMock, return_value=[]):
            result = await tools.votos_materia("99999")
        assert "Nenhuma votação" in result


# ---------------------------------------------------------------------------
# Votações (3)
# ---------------------------------------------------------------------------


class TestListarVotacoes:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            VotacaoResumo(
                codigo="VOT-2", data="2024-03-15", descricao="PEC da reforma", resultado="Aprovada"
            )
        ]
        with patch(f"{MODULE}.listar_votacoes", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.listar_votacoes("2024")
        assert "PEC da reforma" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.listar_votacoes", new_callable=AsyncMock, return_value=[]):
            result = await tools.listar_votacoes("2024")
        assert "Nenhuma votação" in result


class TestDetalheVotacao:
    @pytest.mark.asyncio
    async def test_formats_detail(self) -> None:
        mock_data = VotacaoDetalhe(
            codigo="VOT-001",
            data="2024-06-01",
            descricao="PEC da reforma",
            resultado="Aprovada",
            sim=50,
            nao=20,
            abstencao=3,
            materia_descricao="PEC 45/2024",
        )
        with patch(f"{MODULE}.obter_votacao", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.detalhe_votacao("VOT-001")
        assert "Aprovada" in result
        assert "Sim=50" in result
        assert "PEC 45/2024" in result

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        with patch(f"{MODULE}.obter_votacao", new_callable=AsyncMock, return_value=None):
            result = await tools.detalhe_votacao("VOT-999")
        assert "não encontrada" in result


class TestVotacoesRecentes:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            VotacaoResumo(
                codigo="VOT-3",
                data="2024-03-15",
                descricao="Votação recente",
                resultado="Rejeitada",
            )
        ]
        with patch(f"{MODULE}.votacoes_recentes", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.votacoes_recentes("20240315")
        assert "Votação recente" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.votacoes_recentes", new_callable=AsyncMock, return_value=[]):
            result = await tools.votacoes_recentes("20240315")
        assert "Nenhuma votação" in result


# ---------------------------------------------------------------------------
# Comissões (4)
# ---------------------------------------------------------------------------


class TestListarComissoes:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            ComissaoResumo(
                codigo="40",
                sigla="CCJ",
                nome="Comissão de Constituição e Justiça",
                tipo="Permanente",
            )
        ]
        with patch(f"{MODULE}.listar_comissoes", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.listar_comissoes()
        assert "CCJ" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.listar_comissoes", new_callable=AsyncMock, return_value=[]):
            result = await tools.listar_comissoes()
        assert "Nenhuma comissão" in result


class TestDetalheComissao:
    @pytest.mark.asyncio
    async def test_formats_detail(self) -> None:
        mock_data = ComissaoDetalhe(
            codigo="40",
            sigla="CCJ",
            nome="Comissão de Constituição e Justiça",
            tipo="Permanente",
            data_criacao="1826-05-07",
        )
        with patch(f"{MODULE}.obter_comissao", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.detalhe_comissao("40")
        assert "CCJ" in result
        assert "1826-05-07" in result

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        with patch(f"{MODULE}.obter_comissao", new_callable=AsyncMock, return_value=None):
            result = await tools.detalhe_comissao("99999")
        assert "não encontrada" in result


class TestMembrosComissao:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            MembroComissao(nome="Senador Membro", partido="PT", uf="SP", cargo="Presidente")
        ]
        with patch(f"{MODULE}.membros_comissao", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.membros_comissao("40")
        assert "Senador Membro" in result
        assert "Presidente" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.membros_comissao", new_callable=AsyncMock, return_value=[]):
            result = await tools.membros_comissao("40")
        assert "Nenhum membro" in result


class TestReunioesComissao:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            ReuniaoComissao(
                data="2024-03-15", tipo="Ordinária", pauta="Discussão de PEC", local="Plenário 5"
            )
        ]
        with patch(f"{MODULE}.reunioes_comissao", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.reunioes_comissao("40")
        assert "Ordinária" in result
        assert "Plenário 5" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.reunioes_comissao", new_callable=AsyncMock, return_value=[]):
            result = await tools.reunioes_comissao("40")
        assert "Nenhuma reunião" in result


# ---------------------------------------------------------------------------
# Agenda (2)
# ---------------------------------------------------------------------------


class TestAgendaPlenario:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            SessaoPlenario(
                data="2024-03-15", tipo="Deliberativa", numero="42", situacao="Encerrada"
            )
        ]
        with patch(f"{MODULE}.agenda_plenario", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.agenda_plenario("2024", "03")
        assert "Deliberativa" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.agenda_plenario", new_callable=AsyncMock, return_value=[]):
            result = await tools.agenda_plenario("2024", "03")
        assert "Nenhuma sessão" in result


class TestAgendaComissoes:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            ReuniaoComissao(data="2024-03-15", comissao="CCJ", tipo="Ordinária", pauta="Discussão")
        ]
        with patch(f"{MODULE}.agenda_comissoes", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.agenda_comissoes("20240315")
        assert "CCJ" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.agenda_comissoes", new_callable=AsyncMock, return_value=[]):
            result = await tools.agenda_comissoes("20240315")
        assert "Nenhuma reunião" in result


# ---------------------------------------------------------------------------
# Auxiliares (2)
# ---------------------------------------------------------------------------


class TestLegislaturaAtual:
    @pytest.mark.asyncio
    async def test_formats_info(self) -> None:
        mock_data = LegislaturaInfo(numero=57, data_inicio="2023-02-01", data_fim="2027-01-31")
        with patch(f"{MODULE}.legislatura_atual", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.legislatura_atual()
        assert "57" in result
        assert "2023-02-01" in result

    @pytest.mark.asyncio
    async def test_not_available(self) -> None:
        with patch(f"{MODULE}.legislatura_atual", new_callable=AsyncMock, return_value=None):
            result = await tools.legislatura_atual()
        assert "não disponível" in result


class TestPartidosSenado:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            SenadorResumo(codigo="1", nome="Sen A", partido="PT", uf="SP"),
            SenadorResumo(codigo="2", nome="Sen B", partido="PT", uf="RJ"),
            SenadorResumo(codigo="3", nome="Sen C", partido="PL", uf="MG"),
        ]
        with patch(f"{MODULE}.listar_senadores", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.partidos_senado()
        assert "PT" in result
        assert "PL" in result
        assert "2 partidos" in result
        assert "3 senadores" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.listar_senadores", new_callable=AsyncMock, return_value=[]):
            result = await tools.partidos_senado()
        assert "Nenhum senador" in result


class TestUfsSenado:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            SenadorResumo(codigo="1", nome="Sen A", partido="PT", uf="SP"),
            SenadorResumo(codigo="2", nome="Sen B", partido="PL", uf="SP"),
            SenadorResumo(codigo="3", nome="Sen C", partido="PT", uf="RJ"),
        ]
        with patch(f"{MODULE}.listar_senadores", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.ufs_senado()
        assert "SP" in result
        assert "RJ" in result
        assert "2 UFs" in result
        assert "3 senadores" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.listar_senadores", new_callable=AsyncMock, return_value=[]):
            result = await tools.ufs_senado()
        assert "Nenhum senador" in result


class TestTiposMateria:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = {"PEC": "Proposta de Emenda à Constituição", "PLS": "Projeto de Lei do Senado"}
        with patch(f"{MODULE}.tipos_materia_api", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.tipos_materia()
        assert "PEC" in result
        assert "PLS" in result
