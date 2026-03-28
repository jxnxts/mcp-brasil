"""HTTP client for the PNCP API.

Endpoints (verified against OpenAPI spec at /v3/api-docs):
    - /contratacoes/publicacao  → buscar_contratacoes (requires dates + modalidade)
    - /contratos                → buscar_contratos (requires dates)
    - /atas                     → buscar_atas (requires dates)
    - /fornecedores             → consultar_fornecedor
    - /orgaos                   → consultar_orgao

IMPORTANT: The PNCP API has NO text search parameter (`q`).
All text filtering is done client-side after fetching results.
Date format for all endpoints: YYYYMMDD.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from mcp_brasil._shared.http_client import http_get

from .constants import (
    ATAS_ATUALIZACAO_URL,
    ATAS_URL,
    CONTRATACOES_ATUALIZACAO_URL,
    CONTRATACOES_PROPOSTA_URL,
    CONTRATACOES_URL,
    CONTRATOS_ATUALIZACAO_URL,
    CONTRATOS_URL,
    FORNECEDORES_URL,
    INSTRUMENTOS_COBRANCA_URL,
    MAX_DATE_RANGE_DAYS,
    ORGAOS_URL,
    PCA_URL,
)
from .schemas import (
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
    ItemPca,
    OrgaoContratante,
    OrgaoResultado,
    Pca,
    PcaResultado,
)

_DATE_RE = re.compile(r"^\d{8}$")


def normalizar_data(data: str) -> str:
    """Normalize a date string to YYYYMMDD format.

    Accepts: YYYYMMDD, YYYY-MM-DD, DD/MM/YYYY.
    Raises ValueError for invalid formats.
    """
    cleaned = data.strip()

    # Already YYYYMMDD
    if _DATE_RE.match(cleaned):
        datetime.strptime(cleaned, "%Y%m%d")  # validate
        return cleaned

    # YYYY-MM-DD
    if len(cleaned) == 10 and cleaned[4] == "-":
        dt = datetime.strptime(cleaned, "%Y-%m-%d")
        return dt.strftime("%Y%m%d")

    # DD/MM/YYYY
    if len(cleaned) == 10 and cleaned[2] == "/":
        dt = datetime.strptime(cleaned, "%d/%m/%Y")
        return dt.strftime("%Y%m%d")

    msg = f"Formato de data inválido: '{data}'. Use YYYYMMDD, YYYY-MM-DD ou DD/MM/YYYY."
    raise ValueError(msg)


def validar_periodo(data_inicial: str, data_final: str) -> None:
    """Validate that the date range does not exceed MAX_DATE_RANGE_DAYS."""
    dt_ini = datetime.strptime(data_inicial, "%Y%m%d")
    dt_fim = datetime.strptime(data_final, "%Y%m%d")
    if dt_fim < dt_ini:
        msg = f"data_final ({data_final}) é anterior a data_inicial ({data_inicial})."
        raise ValueError(msg)
    diff = (dt_fim - dt_ini).days
    if diff > MAX_DATE_RANGE_DAYS:
        msg = (
            f"Período de {diff} dias excede o máximo de {MAX_DATE_RANGE_DAYS} dias. "
            f"Reduza o intervalo entre data_inicial e data_final."
        )
        raise ValueError(msg)


def _default_data_inicial() -> str:
    """Return 30 days ago in YYYYMMDD format (sensible default)."""
    return (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")


def _default_data_final() -> str:
    """Return today in YYYYMMDD format."""
    return datetime.now().strftime("%Y%m%d")


def _filtrar_por_texto(items: list[dict[str, Any]], texto: str | None) -> list[dict[str, Any]]:
    """Filter API results client-side by text match on relevant fields."""
    if not texto:
        return items
    termo = texto.lower()
    filtered = []
    for item in items:
        searchable = " ".join(
            str(v).lower()
            for v in [
                item.get("objetoCompra"),
                item.get("objetoContrato"),
                item.get("objetoAta"),
                item.get("objetoContratacao"),
                (item.get("orgaoEntidade") or {}).get("razaoSocial"),
                (item.get("fornecedor") or {}).get("razaoSocial"),
                (item.get("fornecedor") or {}).get("nomeRazaoSocial"),
                item.get("nomeRazaoSocialFornecedor"),
            ]
            if v
        )
        if termo in searchable:
            filtered.append(item)
    return filtered


def _parse_contratacao(item: dict[str, Any]) -> Contratacao:
    """Parse a raw API response item into a Contratacao model."""
    orgao = item.get("orgaoEntidade", {}) or {}
    return Contratacao(
        orgao_cnpj=orgao.get("cnpj"),
        orgao_nome=orgao.get("razaoSocial"),
        ano=item.get("anoCompra"),
        numero_sequencial=item.get("sequencialCompra"),
        numero_controle_pncp=item.get("numeroControlePNCP"),
        objeto=item.get("objetoCompra"),
        modalidade_id=item.get("modalidadeId"),
        modalidade_nome=item.get("modalidadeNome"),
        situacao_id=item.get("situacaoCompraId"),
        situacao_nome=item.get("situacaoCompraNome"),
        valor_estimado=item.get("valorTotalEstimado"),
        valor_homologado=item.get("valorTotalHomologado"),
        data_publicacao=item.get("dataPublicacaoPncp"),
        data_abertura=item.get("dataAberturaProposta"),
        uf=orgao.get("ufSigla"),
        municipio=orgao.get("municipioNome"),
        esfera=orgao.get("esferaNome"),
        link_pncp=item.get("linkPncp"),
    )


def _parse_contrato(item: dict[str, Any]) -> Contrato:
    """Parse a raw API response item into a Contrato model."""
    orgao = item.get("orgaoEntidade", {}) or {}
    fornecedor = item.get("fornecedor", {}) or {}
    return Contrato(
        orgao_cnpj=orgao.get("cnpj"),
        orgao_nome=orgao.get("razaoSocial"),
        numero_contrato=item.get("numeroContratoEmpenho"),
        objeto=item.get("objetoContrato"),
        fornecedor_cnpj=fornecedor.get("cnpj") or fornecedor.get("cpfCnpj"),
        fornecedor_nome=fornecedor.get("razaoSocial") or fornecedor.get("nomeRazaoSocial"),
        valor_inicial=item.get("valorInicial"),
        valor_final=item.get("valorFinal"),
        vigencia_inicio=item.get("dataVigenciaInicio"),
        vigencia_fim=item.get("dataVigenciaFim"),
        data_publicacao=item.get("dataPublicacaoPncp"),
        situacao=item.get("nomeStatus"),
    )


def _parse_ata(item: dict[str, Any]) -> AtaRegistroPreco:
    """Parse a raw API response item into an AtaRegistroPreco model."""
    orgao = item.get("orgaoEntidade", {}) or {}
    fornecedor = item.get("fornecedor", {}) or {}
    return AtaRegistroPreco(
        orgao_cnpj=orgao.get("cnpj"),
        orgao_nome=orgao.get("razaoSocial"),
        numero_ata=item.get("numeroAta") or item.get("numeroAtaRegistroPreco"),
        objeto=(
            item.get("objetoAta") or item.get("objetoContrato") or item.get("objetoContratacao")
        ),
        fornecedor_cnpj=fornecedor.get("cnpj") or fornecedor.get("cpfCnpj"),
        fornecedor_nome=fornecedor.get("razaoSocial") or fornecedor.get("nomeRazaoSocial"),
        valor_total=item.get("valorTotal") or item.get("valorInicial"),
        vigencia_inicio=item.get("dataVigenciaInicio") or item.get("vigenciaInicio"),
        vigencia_fim=item.get("dataVigenciaFim") or item.get("vigenciaFim"),
        situacao=item.get("nomeStatus"),
    )


async def buscar_contratacoes(
    data_inicial: str,
    data_final: str,
    modalidade: int,
    *,
    texto: str | None = None,
    uf: str | None = None,
    cnpj_orgao: str | None = None,
    modo_disputa: int | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> ContratacaoResultado:
    """Search published procurement processes.

    Required by the API: dataInicial, dataFinal, codigoModalidadeContratacao.
    Text filtering is done client-side (API has no text search).
    """
    data_ini = normalizar_data(data_inicial)
    data_fim = normalizar_data(data_final)
    validar_periodo(data_ini, data_fim)

    params: dict[str, str] = {
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "codigoModalidadeContratacao": str(modalidade),
        "pagina": str(pagina),
        "tamanhoPagina": str(min(tamanho, 50)),
    }
    if uf:
        params["uf"] = uf
    if cnpj_orgao:
        params["cnpj"] = cnpj_orgao
    if modo_disputa:
        params["codigoModoDisputa"] = str(modo_disputa)

    data: dict[str, Any] = await http_get(CONTRATACOES_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []

    # Client-side text filtering
    items = _filtrar_por_texto(items, texto)

    contratacoes = [_parse_contratacao(item) for item in items]
    return ContratacaoResultado(
        total=len(contratacoes) if texto else data.get("totalRegistros", len(contratacoes)),
        contratacoes=contratacoes,
    )


async def buscar_contratos(
    data_inicial: str,
    data_final: str,
    *,
    texto: str | None = None,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> ContratoResultado:
    """Search public contracts.

    Required by the API: dataInicial, dataFinal.
    Text filtering is done client-side (API has no text search).
    """
    data_ini = normalizar_data(data_inicial)
    data_fim = normalizar_data(data_final)
    validar_periodo(data_ini, data_fim)

    params: dict[str, str] = {
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "pagina": str(pagina),
        "tamanhoPagina": str(min(tamanho, 500)),
    }
    if cnpj_orgao:
        params["cnpjOrgao"] = cnpj_orgao

    data: dict[str, Any] = await http_get(CONTRATOS_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []

    # Client-side text filtering
    items = _filtrar_por_texto(items, texto)

    contratos = [_parse_contrato(item) for item in items]
    return ContratoResultado(
        total=len(contratos) if texto else data.get("totalRegistros", len(contratos)),
        contratos=contratos,
    )


async def buscar_atas(
    data_inicial: str,
    data_final: str,
    *,
    texto: str | None = None,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> AtaResultado:
    """Search price record minutes (atas de registro de preço).

    Required by the API: dataInicial, dataFinal.
    Filters by validity period (vigência), not publication date.
    Text filtering is done client-side (API has no text search).
    """
    data_ini = normalizar_data(data_inicial)
    data_fim = normalizar_data(data_final)
    validar_periodo(data_ini, data_fim)

    params: dict[str, str] = {
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "pagina": str(pagina),
        "tamanhoPagina": str(min(tamanho, 500)),
    }
    if cnpj_orgao:
        params["cnpj"] = cnpj_orgao

    data: dict[str, Any] = await http_get(ATAS_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []

    # Client-side text filtering
    items = _filtrar_por_texto(items, texto)

    atas = [_parse_ata(item) for item in items]
    return AtaResultado(
        total=len(atas) if texto else data.get("totalRegistros", len(atas)),
        atas=atas,
    )


def _parse_fornecedor(item: dict[str, Any]) -> Fornecedor:
    """Parse a raw API response item into a Fornecedor model."""
    return Fornecedor(
        cnpj=item.get("cnpj") or item.get("cpfCnpj"),
        razao_social=item.get("razaoSocial") or item.get("nomeRazaoSocial"),
        nome_fantasia=item.get("nomeFantasia"),
        municipio=(
            item.get("municipio", {}).get("nome")
            if isinstance(item.get("municipio"), dict)
            else item.get("municipioNome")
        ),
        uf=(
            item.get("uf", {}).get("sigla")
            if isinstance(item.get("uf"), dict)
            else item.get("ufSigla")
        ),
        porte=item.get("porte") or item.get("porteEmpresa"),
        data_abertura=item.get("dataAbertura"),
    )


def _parse_orgao(item: dict[str, Any]) -> OrgaoContratante:
    """Parse a raw API response item into an OrgaoContratante model."""
    return OrgaoContratante(
        cnpj=item.get("cnpj"),
        razao_social=item.get("razaoSocial"),
        esfera=item.get("esferaNome") or item.get("esferaId"),
        poder=item.get("poderNome") or item.get("poderId"),
        uf=item.get("ufSigla") or item.get("ufNome"),
        municipio=item.get("municipioNome"),
    )


async def consultar_fornecedor(cnpj: str) -> FornecedorResultado:
    """Search supplier by CNPJ."""
    params: dict[str, str] = {"cnpj": cnpj}
    data: dict[str, Any] = await http_get(FORNECEDORES_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    fornecedores = [_parse_fornecedor(item) for item in items] if isinstance(items, list) else []
    return FornecedorResultado(
        total=data.get("totalRegistros", data.get("count", len(fornecedores))),
        fornecedores=fornecedores,
    )


async def consultar_orgao(
    query: str | None = None,
    uf: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> OrgaoResultado:
    """Search contracting bodies."""
    params: dict[str, str] = {"pagina": str(pagina), "tamanhoPagina": str(tamanho)}
    if query:
        params["q"] = query
    if uf:
        params["uf"] = uf
    data: dict[str, Any] = await http_get(ORGAOS_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    orgaos = [_parse_orgao(item) for item in items] if isinstance(items, list) else []
    return OrgaoResultado(
        total=data.get("totalRegistros", data.get("count", len(orgaos))),
        orgaos=orgaos,
    )


async def buscar_contratacoes_abertas(
    data_final: str,
    *,
    texto: str | None = None,
    modalidade: int | None = None,
    uf: str | None = None,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> ContratacaoResultado:
    """Search procurement processes with open proposal submission.

    API: GET /v1/contratacoes/proposta
    Required: dataFinal, pagina.
    """
    data_fim = normalizar_data(data_final)
    params: dict[str, str] = {
        "dataFinal": data_fim,
        "pagina": str(pagina),
        "tamanhoPagina": str(min(max(tamanho, 10), 50)),
    }
    if modalidade:
        params["codigoModalidadeContratacao"] = str(modalidade)
    if uf:
        params["uf"] = uf
    if cnpj_orgao:
        params["cnpj"] = cnpj_orgao

    data: dict[str, Any] = await http_get(CONTRATACOES_PROPOSTA_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []
    items = _filtrar_por_texto(items, texto)
    contratacoes = [_parse_contratacao(item) for item in items]
    return ContratacaoResultado(
        total=len(contratacoes) if texto else data.get("totalRegistros", len(contratacoes)),
        contratacoes=contratacoes,
    )


async def buscar_contratacoes_atualizadas(
    data_inicial: str,
    data_final: str,
    modalidade: int,
    *,
    texto: str | None = None,
    uf: str | None = None,
    cnpj_orgao: str | None = None,
    modo_disputa: int | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> ContratacaoResultado:
    """Search procurement processes by global update date.

    API: GET /v1/contratacoes/atualizacao
    Required: dataInicial, dataFinal, codigoModalidadeContratacao, pagina.
    """
    data_ini = normalizar_data(data_inicial)
    data_fim = normalizar_data(data_final)
    validar_periodo(data_ini, data_fim)

    params: dict[str, str] = {
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "codigoModalidadeContratacao": str(modalidade),
        "pagina": str(pagina),
        "tamanhoPagina": str(min(max(tamanho, 10), 50)),
    }
    if uf:
        params["uf"] = uf
    if cnpj_orgao:
        params["cnpj"] = cnpj_orgao
    if modo_disputa:
        params["codigoModoDisputa"] = str(modo_disputa)

    data: dict[str, Any] = await http_get(CONTRATACOES_ATUALIZACAO_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []
    items = _filtrar_por_texto(items, texto)
    contratacoes = [_parse_contratacao(item) for item in items]
    return ContratacaoResultado(
        total=len(contratacoes) if texto else data.get("totalRegistros", len(contratacoes)),
        contratacoes=contratacoes,
    )


async def buscar_contratos_atualizados(
    data_inicial: str,
    data_final: str,
    *,
    texto: str | None = None,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> ContratoResultado:
    """Search contracts by global update date.

    API: GET /v1/contratos/atualizacao
    Required: dataInicial, dataFinal, pagina.
    """
    data_ini = normalizar_data(data_inicial)
    data_fim = normalizar_data(data_final)
    validar_periodo(data_ini, data_fim)

    params: dict[str, str] = {
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "pagina": str(pagina),
        "tamanhoPagina": str(min(max(tamanho, 10), 500)),
    }
    if cnpj_orgao:
        params["cnpjOrgao"] = cnpj_orgao

    data: dict[str, Any] = await http_get(CONTRATOS_ATUALIZACAO_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []
    items = _filtrar_por_texto(items, texto)
    contratos = [_parse_contrato(item) for item in items]
    return ContratoResultado(
        total=len(contratos) if texto else data.get("totalRegistros", len(contratos)),
        contratos=contratos,
    )


async def buscar_atas_atualizadas(
    data_inicial: str,
    data_final: str,
    *,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> AtaResultado:
    """Search price record minutes by global update date.

    API: GET /v1/atas/atualizacao
    Required: dataInicial, dataFinal, pagina.
    """
    data_ini = normalizar_data(data_inicial)
    data_fim = normalizar_data(data_final)
    validar_periodo(data_ini, data_fim)

    params: dict[str, str] = {
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "pagina": str(pagina),
        "tamanhoPagina": str(min(max(tamanho, 10), 500)),
    }
    if cnpj_orgao:
        params["cnpj"] = cnpj_orgao

    data: dict[str, Any] = await http_get(ATAS_ATUALIZACAO_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []

    atas: list[AtaRegistroPreco] = []
    for item in items:
        atas.append(
            AtaRegistroPreco(
                orgao_cnpj=item.get("cnpjOrgao"),
                orgao_nome=item.get("nomeOrgao"),
                numero_ata=item.get("numeroAtaRegistroPreco"),
                objeto=item.get("objetoContratacao"),
                vigencia_inicio=item.get("vigenciaInicio"),
                vigencia_fim=item.get("vigenciaFim"),
            )
        )
    return AtaResultado(
        total=data.get("totalRegistros", len(atas)),
        atas=atas,
    )


async def consultar_contratacao_detalhe(
    cnpj: str,
    ano: int,
    sequencial: int,
) -> Contratacao:
    """Fetch a specific procurement process detail.

    API: GET /v1/orgaos/{cnpj}/compras/{ano}/{sequencial}
    """
    url = f"{ORGAOS_URL}/{cnpj}/compras/{ano}/{sequencial}"
    data: dict[str, Any] = await http_get(url)
    return _parse_contratacao(data)


def _parse_item_pca(item: dict[str, Any]) -> ItemPca:
    """Parse a PCA item from API response."""
    return ItemPca(
        numero_item=item.get("numeroItem"),
        descricao=item.get("descricaoItem"),
        quantidade_estimada=item.get("quantidadeEstimada"),
        valor_unitario=item.get("valorUnitario"),
        valor_total=item.get("valorTotal"),
        unidade_fornecimento=item.get("unidadeFornecimento"),
        categoria=item.get("categoriaItemPcaNome") or item.get("nomeClassificacaoCatalogo"),
        data_desejada=item.get("dataDesejada"),
    )


def _parse_pca(item: dict[str, Any]) -> Pca:
    """Parse a PCA from API response."""
    raw_itens = item.get("itens", [])
    return Pca(
        orgao_cnpj=item.get("orgaoEntidadeCnpj"),
        orgao_nome=item.get("orgaoEntidadeRazaoSocial"),
        ano=item.get("anoPca"),
        unidade_nome=item.get("nomeUnidade"),
        id_pca=item.get("idPcaPncp"),
        data_publicacao=item.get("dataPublicacaoPNCP"),
        itens=[_parse_item_pca(i) for i in raw_itens] if isinstance(raw_itens, list) else [],
    )


async def buscar_pca(
    ano: int,
    codigo_classificacao: str = "0",
    *,
    pagina: int = 1,
    tamanho: int = 10,
) -> PcaResultado:
    """Search Annual Procurement Plans (PCA) by year.

    API: GET /v1/pca/
    Required: anoPca, codigoClassificacaoSuperior, pagina.
    """
    params: dict[str, str] = {
        "anoPca": str(ano),
        "codigoClassificacaoSuperior": codigo_classificacao,
        "pagina": str(pagina),
        "tamanhoPagina": str(min(max(tamanho, 10), 500)),
    }
    data: dict[str, Any] = await http_get(PCA_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []
    pcas = [_parse_pca(item) for item in items]
    return PcaResultado(
        total=data.get("totalRegistros", len(pcas)),
        pcas=pcas,
    )


async def buscar_pca_atualizacao(
    data_inicio: str,
    data_fim: str,
    *,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> PcaResultado:
    """Search PCA by global update date.

    API: GET /v1/pca/atualizacao
    Required: dataInicio, dataFim, pagina.
    """
    dt_ini = normalizar_data(data_inicio)
    dt_fim = normalizar_data(data_fim)
    validar_periodo(dt_ini, dt_fim)

    params: dict[str, str] = {
        "dataInicio": dt_ini,
        "dataFim": dt_fim,
        "pagina": str(pagina),
        "tamanhoPagina": str(min(max(tamanho, 10), 500)),
    }
    if cnpj_orgao:
        params["cnpj"] = cnpj_orgao

    data: dict[str, Any] = await http_get(f"{PCA_URL}/atualizacao", params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []
    pcas = [_parse_pca(item) for item in items]
    return PcaResultado(
        total=data.get("totalRegistros", len(pcas)),
        pcas=pcas,
    )


async def buscar_pca_usuario(
    ano: int,
    id_usuario: int,
    *,
    cnpj_orgao: str | None = None,
    codigo_classificacao: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> PcaResultado:
    """Search PCA items by year and user ID.

    API: GET /v1/pca/usuario
    Required: anoPca, idUsuario, pagina.
    """
    params: dict[str, str] = {
        "anoPca": str(ano),
        "idUsuario": str(id_usuario),
        "pagina": str(pagina),
        "tamanhoPagina": str(min(max(tamanho, 10), 500)),
    }
    if cnpj_orgao:
        params["cnpj"] = cnpj_orgao
    if codigo_classificacao:
        params["codigoClassificacaoSuperior"] = codigo_classificacao

    data: dict[str, Any] = await http_get(f"{PCA_URL}/usuario", params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []
    pcas = [_parse_pca(item) for item in items]
    return PcaResultado(
        total=data.get("totalRegistros", len(pcas)),
        pcas=pcas,
    )


def _parse_instrumento_cobranca(item: dict[str, Any]) -> InstrumentoCobranca:
    """Parse an instrument of billing from API response."""
    contrato = item.get("recuperarContratoDTO", {}) or {}
    tipo = item.get("tipoInstrumentoCobranca", {}) or {}
    nfe = item.get("notaFiscalEletronica", {}) or {}
    return InstrumentoCobranca(
        cnpj_orgao=item.get("cnpj"),
        ano_contrato=contrato.get("anoContrato"),
        numero_instrumento=item.get("numeroInstrumentoCobranca"),
        tipo_nome=tipo.get("nome"),
        data_emissao=item.get("dataEmissaoDocumento"),
        objeto_contrato=contrato.get("objetoContrato"),
        fornecedor_nome=nfe.get("nomeEmitente") or contrato.get("nomeRazaoSocialFornecedor"),
        fornecedor_cnpj=nfe.get("niEmitente") or contrato.get("niFornecedor"),
        valor_nf=nfe.get("valorNotaFiscal"),
        chave_nfe=item.get("chaveNFe"),
    )


async def buscar_instrumentos_cobranca(
    data_inicial: str,
    data_final: str,
    *,
    tipo: int | None = None,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
    tamanho: int = 10,
) -> InstrumentoCobrancaResultado:
    """Search billing instruments (invoices) by inclusion date.

    API: GET /v1/instrumentoscobranca/inclusao
    Required: dataInicial, dataFinal, pagina.
    """
    data_ini = normalizar_data(data_inicial)
    data_fim = normalizar_data(data_final)
    validar_periodo(data_ini, data_fim)

    params: dict[str, str] = {
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "pagina": str(pagina),
        "tamanhoPagina": str(min(max(tamanho, 10), 100)),
    }
    if tipo:
        params["tipoInstrumentoCobranca"] = str(tipo)
    if cnpj_orgao:
        params["cnpjOrgao"] = cnpj_orgao

    data: dict[str, Any] = await http_get(INSTRUMENTOS_COBRANCA_URL, params=params)
    items = data.get("data", data.get("resultado", []))
    if not isinstance(items, list):
        items = []
    instrumentos = [_parse_instrumento_cobranca(item) for item in items]
    return InstrumentoCobrancaResultado(
        total=data.get("totalRegistros", len(instrumentos)),
        instrumentos=instrumentos,
    )
