# Contributing to mcp-brasil

Obrigado pelo interesse em contribuir!

## Getting Started

```bash
git clone https://github.com/jxnxts/mcp-brasil.git
cd mcp-brasil
make dev        # Instala dependências de dev
make ci         # Roda lint + mypy + testes
```

## Estrutura do Projeto

```
src/mcp_brasil/
├── server.py           # Server raiz (auto-registry, nunca editado manualmente)
├── _shared/            # Código compartilhado (http_client, formatting, cache, rate_limiter)
├── data/               # Features de consulta a APIs
│   ├── ibge/           # Feature IBGE
│   ├── transparencia/  # Feature Portal da Transparência
│   └── {nova_feature}/ # Sua nova feature de dados aqui
└── agentes/            # Features de agentes inteligentes
    └── redator/        # Feature Redator Oficial
```

## Como Adicionar uma Nova Feature

1. Crie o diretório `src/mcp_brasil/data/{feature}/` (APIs) ou `src/mcp_brasil/agentes/{feature}/` (agentes) com os arquivos obrigatórios:

```
src/mcp_brasil/data/{feature}/      # ou agentes/{feature}/
├── __init__.py     # FEATURE_META (obrigatório para auto-discovery)
├── server.py       # mcp: FastMCP (obrigatório)
├── tools.py        # Funções das tools
├── client.py       # HTTP async para a API
├── schemas.py      # Pydantic models
└── constants.py    # URLs, enums, códigos
```

2. Em `__init__.py`, defina `FEATURE_META`:

```python
from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="minha-feature",
    description="Descrição curta da API",
    version="0.1.0",
    api_base="https://api.exemplo.gov.br",
    requires_auth=False,
)
```

3. Em `server.py`, crie e registre as tools:

```python
from fastmcp import FastMCP
from .tools import minha_tool

mcp = FastMCP("mcp-brasil-minha-feature")

mcp.tool(minha_tool)
```

4. Crie testes em `tests/data/{feature}/` (ou `tests/agentes/{feature}/`):

```
tests/data/{feature}/         # ou tests/agentes/{feature}/
├── test_tools.py             # Mock client, testa lógica
├── test_client.py            # respx mock HTTP
└── test_integration.py       # fastmcp.Client e2e
```

5. Rode `make ci` para verificar que tudo passa.

## Fluxo de Dependência

Dentro de cada feature, o fluxo é unidirecional:

```
server.py → tools.py → client.py → schemas.py
  registra    orquestra   faz HTTP     dados puros
```

- **`tools.py` nunca faz HTTP** — delega para `client.py`
- **`client.py` nunca formata para LLM** — retorna Pydantic models
- **`schemas.py` zero lógica** — apenas BaseModel com Field
- **`server.py` apenas registra** — zero lógica de negócio
- **`constants.py` zero imports** de outros módulos do projeto

## Convenções de Código

| Escopo | Convenção | Exemplo |
|--------|-----------|---------|
| Módulos | snake_case | `client.py` |
| Classes | PascalCase | `class Estado(BaseModel)` |
| Funções/tools | snake_case, verbo | `buscar_localidades()` |
| Constantes | UPPER_SNAKE | `IBGE_API_BASE` |
| Privados | `_prefixo` | `_shared/`, `_cache` |

### Regras Invioláveis

1. `server.py` raiz nunca muda — auto-registry cuida de tudo
2. `tools.py` nunca faz HTTP — delega para `client.py`
3. `client.py` nunca formata para LLM — retorna Pydantic models
4. `schemas.py` zero lógica — apenas BaseModel
5. `server.py` da feature apenas registra — zero lógica de negócio
6. `constants.py` zero imports de outros módulos
7. Toda tool tem docstring — usada pelo LLM para decidir quando chamar
8. Async everywhere — `async def` em tools e clients
9. Type hints completos em todas as funções

## Stack

- **Python 3.10+** — linguagem base
- **FastMCP v3** — framework MCP (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`)
- **httpx** — HTTP async
- **Pydantic v2** — schemas e validação
- **uv** — package manager
- **ruff** — lint + format (line-length 99)
- **mypy** — type checking (strict)
- **pytest + pytest-asyncio + respx** — testes

## Testes

```bash
make test                 # Todos os testes
make test-feature F=ibge  # Testes de uma feature
make lint                 # ruff check + format check
make types                # mypy strict
make ci                   # lint + types + test
```

Testes usam:
- **pytest** + **pytest-asyncio** para async
- **respx** para mock HTTP em `test_client.py`
- **unittest.mock** para mock de client em `test_tools.py`
- **fastmcp.Client** para testes de integração e2e

### Padrões de Teste

#### `test_tools.py` — Mock no client

```python
from unittest.mock import AsyncMock, patch
import pytest
from mcp_brasil.data.{feature}.tools import buscar_{feature}

@pytest.mark.asyncio
async def test_buscar_retorna_formatado():
    with patch("mcp_brasil.data.{feature}.tools.buscar_exemplo", new_callable=AsyncMock) as mock:
        mock.return_value = [...]
        resultado = await buscar_{feature}("query")
        assert "esperado" in resultado
```

#### `test_client.py` — Mock HTTP com respx

```python
import httpx
import pytest
import respx
from mcp_brasil.data.{feature}.client import buscar_exemplo

@pytest.mark.asyncio
@respx.mock
async def test_buscar_sucesso():
    respx.get("https://api.exemplo.gov.br/endpoint").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "nome": "Teste"}])
    )
    resultado = await buscar_exemplo("query")
    assert len(resultado) == 1
```

#### `test_integration.py` — End-to-end com fastmcp.Client

```python
import pytest
from fastmcp import Client
from mcp_brasil.data.{feature}.server import mcp

@pytest.mark.asyncio
async def test_tool_via_mcp_client():
    async with Client(mcp) as client:
        result = await client.call_tool("buscar_{feature}", {"query": "teste"})
        assert result is not None
```

## Commits

Use **Conventional Commits** (em português ou inglês):

```
feat(ibge): add tool consultar_populacao
fix(bacen): handle empty response from SGS
test(transparencia): add edge-case tests for client
docs: update README with new feature
refactor(camara): simplify pagination logic
```

- Garanta que `make ci` passa antes de commitar
- Não acumule múltiplas mudanças sem commitar

## Releases

Releases seguem **Semantic Versioning** e são gerenciados pelo Tech Lead.

### Tipos de bump

| Situação | Bump | Exemplo |
|----------|------|---------|
| Nova feature (nova API, novo agente) | **minor** | `feat(saude): add 5 tools` |
| Bug fix, ajuste de endpoint | **patch** | `fix(bacen): handle timeout` |
| Breaking change (renomear tools, mudar API) | **major** | refactor que quebra clientes |
| Apenas docs, testes, refactor interno | **nenhum** | Não precisa de release |

### Como fazer release

```bash
make version          # Ver versão atual
make release-patch    # Bump patch (roda CI antes)
make release-minor    # Bump minor
make release-major    # Bump major
make changelog        # Gerar CHANGELOG.md manualmente
make build            # Build do pacote (sdist + wheel)
```

### CI/CD

- **CI** (`.github/workflows/ci.yml`): roda em todo push/PR para `main` — lint + types + testes (Python 3.10-3.13)
- **Release** (`.github/workflows/release.yml`): dispara com tag `v*` — CI + build + publish no PyPI (trusted publishing) + GitHub Release

### Infraestrutura

- Versão definida em `pyproject.toml` (source of truth)
- `__init__.py` usa `importlib.metadata` para ler a versão (sem duplicação)
- CHANGELOG.md gerado automaticamente via `git-cliff` (`cliff.toml`)
- Config de semantic-release em `pyproject.toml` (`[tool.semantic_release]`)

## Pull Requests

- Use **Conventional Commits** no título do PR
- Garanta que `make ci` passa antes de abrir o PR
- Descreva o que mudou e por quê no corpo do PR
- Se adicionou feature nova, inclua testes (`test_tools.py`, `test_client.py`, `test_integration.py`)
- Se encontrou débito técnico, registre em `TECH_DEBT.md`
