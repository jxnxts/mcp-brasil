"""Client for the Imunização (PNI) feature.

Two data sources:
    1. OpenDataSUS CKAN API — PNI datasets (doses aplicadas, etc.)
    2. Elasticsearch público — registros individuais de vacinação

Auth: Elasticsearch uses publicly available credentials (published on OpenDataSUS).
"""

from __future__ import annotations

import base64
import json
from typing import Any

from mcp_brasil._shared.http_client import http_get, http_post

from .constants import (
    CKAN_DATASTORE_SEARCH_URL,
    CKAN_PACKAGE_SEARCH_URL,
    CKAN_PACKAGE_SHOW_URL,
    DEFAULT_LIMIT,
    ES_PASSWORD,
    ES_SEARCH_URL,
    ES_USER,
    MAX_LIMIT,
)
from .schemas import AgregacaoVacinacao, DatasetPNI, RecursoPNI, RegistroVacinacao


def _es_auth_header() -> dict[str, str]:
    """Build Basic auth header for the public Elasticsearch endpoint."""
    credentials = f"{ES_USER}:{ES_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


# ---------------------------------------------------------------------------
# Elasticsearch — registros individuais de vacinação
# ---------------------------------------------------------------------------


def _parse_registro(hit: dict[str, Any]) -> RegistroVacinacao:
    """Parse an Elasticsearch hit into a RegistroVacinacao."""
    src = hit.get("_source", hit)
    return RegistroVacinacao(
        municipio=src.get("paciente_endereco_nmMunicipio"),
        uf=src.get("estabelecimento_uf") or src.get("paciente_endereco_uf"),
        vacina_nome=src.get("vacina_nome"),
        dose=src.get("vacina_descricao_dose"),
        fabricante=src.get("vacina_fabricante_nome"),
        faixa_etaria=str(src.get("paciente_idade", "")) or None,
        sexo=src.get("paciente_enumSexoBiologico"),
        data_aplicacao=src.get("vacina_dataAplicacao"),
        estabelecimento=src.get("estabelecimento_razaoSocial"),
        grupo_atendimento=src.get("vacina_grupoAtendimento_nome"),
    )


async def buscar_vacinacao_es(
    *,
    uf: str | None = None,
    municipio: str | None = None,
    vacina: str | None = None,
    dose: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[RegistroVacinacao], int]:
    """Search individual vaccination records via Elasticsearch.

    Args:
        uf: State abbreviation (e.g., "PI", "SP").
        municipio: Municipality name.
        vacina: Vaccine name (e.g., "Covid-19").
        dose: Dose description (e.g., "1ª Dose").
        limit: Max records (default 20).

    Returns:
        Tuple of (records, total_hits).
    """
    must_clauses: list[dict[str, Any]] = []
    if uf:
        must_clauses.append({"match": {"estabelecimento_uf": uf.upper()}})
    if municipio:
        must_clauses.append({"match": {"paciente_endereco_nmMunicipio": municipio}})
    if vacina:
        must_clauses.append({"match": {"vacina_nome": vacina}})
    if dose:
        must_clauses.append({"match": {"vacina_descricao_dose": dose}})

    query_body: dict[str, Any] = {
        "size": min(limit, MAX_LIMIT),
    }
    if must_clauses:
        query_body["query"] = {"bool": {"must": must_clauses}}
    else:
        query_body["query"] = {"match_all": {}}

    data = await http_post(
        ES_SEARCH_URL,
        json_body=query_body,
        headers=_es_auth_header(),
        timeout=30.0,
    )

    hits = data.get("hits", {})
    total = hits.get("total", {})
    total_count = total.get("value", 0) if isinstance(total, dict) else int(total)
    records = [_parse_registro(h) for h in hits.get("hits", [])]
    return records, total_count


async def agregar_vacinacao_es(
    *,
    uf: str | None = None,
    municipio_ibge: str | None = None,
    campo_agregacao: str = "vacina_nome.keyword",
    tamanho: int = 50,
) -> list[AgregacaoVacinacao]:
    """Aggregate vaccination records by a field (e.g., vaccine name).

    Args:
        uf: State abbreviation filter.
        municipio_ibge: IBGE municipality code filter.
        campo_agregacao: Elasticsearch field for aggregation.
        tamanho: Max buckets.

    Returns:
        List of aggregation results.
    """
    filters: list[dict[str, Any]] = []
    if uf:
        filters.append({"term": {"estabelecimento_uf.keyword": uf.upper()}})
    if municipio_ibge:
        filters.append({"term": {"paciente_endereco_coIbgeMunicipio.keyword": municipio_ibge}})

    query_body: dict[str, Any] = {
        "size": 0,
        "aggs": {"por_campo": {"terms": {"field": campo_agregacao, "size": tamanho}}},
    }
    if filters:
        query_body["query"] = {"bool": {"filter": filters}}
    else:
        query_body["query"] = {"match_all": {}}

    data = await http_post(
        ES_SEARCH_URL,
        json_body=query_body,
        headers=_es_auth_header(),
        timeout=30.0,
    )

    buckets = data.get("aggregations", {}).get("por_campo", {}).get("buckets", [])
    return [AgregacaoVacinacao(nome=b["key"], total=b["doc_count"]) for b in buckets]


# ---------------------------------------------------------------------------
# CKAN — datasets do PNI no OpenDataSUS
# ---------------------------------------------------------------------------


def _parse_dataset(raw: dict[str, Any]) -> DatasetPNI:
    """Parse a CKAN package dict into a DatasetPNI."""
    org = raw.get("organization")
    org_name = org.get("title", org.get("name", "")) if isinstance(org, dict) else None
    recursos = raw.get("resources", [])
    return DatasetPNI(
        id=str(raw.get("id", "")),
        nome=raw.get("name", ""),
        titulo=raw.get("title"),
        descricao=raw.get("notes"),
        organizacao=org_name,
        total_recursos=len(recursos),
        data_atualizacao=raw.get("metadata_modified"),
    )


def _parse_recurso(raw: dict[str, Any]) -> RecursoPNI:
    """Parse a CKAN resource dict."""
    return RecursoPNI(
        id=str(raw.get("id", "")),
        nome=raw.get("name") or raw.get("title"),
        formato=raw.get("format"),
        url=raw.get("url"),
    )


async def buscar_datasets_pni(
    query: str = "imunização PNI",
    limite: int = DEFAULT_LIMIT,
) -> tuple[list[DatasetPNI], int]:
    """Search PNI-related datasets on OpenDataSUS.

    Args:
        query: Search keyword.
        limite: Max results.

    Returns:
        Tuple of (datasets, total_count).
    """
    rows = min(limite, MAX_LIMIT)
    data = await http_get(CKAN_PACKAGE_SEARCH_URL, params={"q": query, "rows": str(rows)})
    result = data.get("result", {}) if isinstance(data, dict) else {}
    datasets = [_parse_dataset(d) for d in result.get("results", [])]
    total = result.get("count", len(datasets))
    return datasets, total


async def detalhar_dataset_pni(
    dataset_id: str,
) -> tuple[DatasetPNI | None, list[RecursoPNI]]:
    """Get details and resources of a PNI dataset.

    Args:
        dataset_id: Dataset name (slug) or UUID.

    Returns:
        Tuple of (dataset, resources).
    """
    data = await http_get(CKAN_PACKAGE_SHOW_URL, params={"id": dataset_id})
    result = data.get("result", {}) if isinstance(data, dict) else {}
    if not result or not result.get("id"):
        return None, []
    ds = _parse_dataset(result)
    recursos = [_parse_recurso(r) for r in result.get("resources", [])]
    return ds, recursos


async def consultar_datastore_pni(
    resource_id: str,
    query: str | None = None,
    filtros: dict[str, str] | None = None,
    limite: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    """Query records from a PNI DataStore resource.

    Args:
        resource_id: UUID of the CKAN resource.
        query: Full-text search.
        filtros: Field-value exact filters.
        limite: Max records.
        offset: Pagination offset.

    Returns:
        Tuple of (records as dicts, total_count).
    """
    rows = min(limite, MAX_LIMIT)
    params: dict[str, str] = {
        "resource_id": resource_id,
        "limit": str(rows),
        "offset": str(offset),
    }
    if query:
        params["q"] = query
    if filtros:
        params["filters"] = json.dumps(filtros)

    data = await http_get(CKAN_DATASTORE_SEARCH_URL, params=params)
    result = data.get("result", {}) if isinstance(data, dict) else {}
    records = result.get("records", [])
    # Remove _id key from records
    clean = [{k: v for k, v in r.items() if k != "_id"} for r in records]
    total = result.get("total", len(clean))
    return clean, total


# ---------------------------------------------------------------------------
# Static reference helpers
# ---------------------------------------------------------------------------


def listar_todas_vacinas() -> list[dict[str, Any]]:
    """Return all vaccines from the vaccination calendar as flat dicts."""
    from .constants import GRUPOS_IMUNOBIOLOGICOS

    vacinas: list[dict[str, Any]] = []
    for grupo_key, grupo in GRUPOS_IMUNOBIOLOGICOS.items():
        grupo_nome = grupo["nome"]
        for v in grupo["vacinas"]:  # type: ignore[union-attr]
            entry = dict(v)  # type: ignore[arg-type]
            entry["grupo"] = str(grupo_nome)
            entry["grupo_key"] = grupo_key
            vacinas.append(entry)
    return vacinas


def buscar_vacina_por_sigla(sigla: str) -> dict[str, Any] | None:
    """Find a vaccine by its abbreviation (case-insensitive)."""
    sigla_lower = sigla.lower()
    for v in listar_todas_vacinas():
        if v["sigla"].lower() == sigla_lower:
            return v
    return None


def buscar_vacina_por_nome(nome: str) -> list[dict[str, Any]]:
    """Find vaccines matching a name substring (case-insensitive)."""
    nome_lower = nome.lower()
    return [
        v
        for v in listar_todas_vacinas()
        if nome_lower in v["nome"].lower() or nome_lower in v["sigla"].lower()
    ]
