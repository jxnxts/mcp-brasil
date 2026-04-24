# Datasets locais

Além das features de REST passthrough em `data/`, o mcp-brasil suporta
**datasets grandes cacheados localmente** em DuckDB embedded.

Essas features baixam CSVs/ZIPs da casa de centenas de MB até alguns GB,
convertem para DuckDB, e expõem SQL via tools canned. São **opt-in**: só
carregam se você listar o dataset em `MCP_BRASIL_DATASETS`.

## Ativando

```bash
# .env
MCP_BRASIL_DATASETS=tse_candidatos,tse_bens,tse_votacao,spu_siapa
```

Valores permitidos (snake_case, separados por vírgula):

| ID | Fonte | Período | Tamanho ZIP | Features |
|---|---|---|---:|---|
| `spu_siapa` | SPU — SIAPA completo (imóveis da União) | snapshot 2026 | ~220 MB | 8 tools |
| `tse_candidatos` | TSE — candidatos de todas as eleições | 2014-2024 | ~290 MB | 8 tools |
| `tse_bens` | TSE — bens declarados | 2014-2024 | ~205 MB | 5 tools |
| `tse_votacao` | TSE — votos candidato × município × zona | 2014-2024 | ~1.6 GB | 6 tools |
| `tse_redes_sociais` | TSE — URLs Instagram/Facebook/Twitter | 2018-2024 | ~34 MB | 4 tools |
| `tse_fefc` | TSE — Fundo Eleitoral (partido × gênero) | 2020, 2024 | ~5 MB | 4 tools |

## Primeira carga

Na primeira vez que você chamar uma tool de dataset, o loader:

1. Baixa os ZIPs do TSE/SPU (usando `httpx` com follow-redirects)
2. Extrai o CSV interno (ZIP multi-ano pra alguns datasets)
3. Transcodifica cp1252 → utf-8 on-the-fly
4. Cria tabelas DuckDB (uma por ano nos multi-source) + view consolidada
5. Salva em `~/.cache/mcp-brasil/datasets/{id}.duckdb`

Tempo esperado na primeira carga:

- `tse_fefc`: ~10s
- `tse_redes_sociais`, `spu_siapa`: ~30-60s
- `tse_candidatos`, `tse_bens`: 1-3 min
- `tse_votacao`: 5-10 min (maior dataset, 1.6GB)

Queries subsequentes rodam em **ms** (DuckDB local).

## Variáveis de configuração

| Variável | Default | Descrição |
|---|---|---|
| `MCP_BRASIL_DATASETS` | "" | Lista CSV de IDs a ativar |
| `MCP_BRASIL_DATASET_CACHE_DIR` | `~/.cache/mcp-brasil` | Diretório do cache |
| `MCP_BRASIL_DATASET_REFRESH` | `auto` | `auto` (TTL), `never` (só cache), `force` (sempre baixar) |
| `MCP_BRASIL_DATASET_TIMEOUT` | `600` | Timeout do download (seg) |
| `MCP_BRASIL_DATASET_MAX_CACHE_GB` | `20` | Limite soft do cache total |
| `MCP_BRASIL_LGPD_ALLOW_PII` | "" | Datasets com PII liberada |

## LGPD — mascaramento de PII

Por padrão, colunas de PII (CPF, título eleitoral, email) declaradas em
`DatasetSpec.pii_columns` são **mascaradas** (`***.***.123-**`) em todas as
queries. Para liberar a visualização integral num dataset específico:

```bash
MCP_BRASIL_LGPD_ALLOW_PII=tse_candidatos
```

Justifique documentalmente sempre que liberar PII — recomenda-se usar isso
apenas em ambientes de análise offline.

## Tools disponíveis por dataset

### `spu_siapa`

- `info_spu_siapa` — estado do cache
- `valores_distintos_siapa(coluna)` — descobre categorias reais
- `buscar_imoveis_siapa(uf, municipio, regime, conceituacao, classe, rip)`
- `resumo_regime_siapa(uf)`
- `resumo_conceituacao_siapa(uf)`
- `resumo_uf_siapa()` — todas as UFs agregadas
- `top_municipios_siapa(uf, top)`
- `refrescar_spu_siapa()` — força re-download

### `tse_candidatos`

- `info_tse_candidatos`
- `valores_distintos_candidatos(coluna)`
- `buscar_candidatos(nome, uf, municipio, cargo, partido, situacao_turno, genero, ano)`
- `resumo_cargo_partido(cargo, ano)`
- `resumo_perfil_eleitos(cargo, ano)` — gênero, raça, escolaridade dos eleitos
- `top_municipios_candidatos(uf, ano)`
- `ranking_anual_eleitos(cargo)` — série histórica 2014-2024
- `refrescar_tse_candidatos`

### `tse_bens`

- `info_tse_bens`
- `buscar_bens_candidato(sq_candidato)`
- `top_patrimonios_cargo(cargo, uf, ano)` — cross-DB join com candidatos
- `resumo_patrimonio_partido(cargo, ano)`
- `resumo_tipos_bens(ano, top)`

### `tse_votacao`

- `info_tse_votacao`
- `votos_candidato(sq_candidato)` — votos em todos os municípios
- `top_votados_cargo(cargo, ano, uf, limite)`
- `ranking_municipio(municipio, uf, cargo, ano)`
- `evolucao_partido(partido, cargo)` — série histórica
- `soma_votos_uf(ano, cargo)`

### `tse_redes_sociais`

- `info_tse_redes_sociais`
- `redes_do_candidato(sq_candidato)` — Instagram/Facebook/Twitter/etc.
- `redes_por_partido(partido, ano)` — cross-DB join com candidatos
- `top_redes_por_ano(ano)` — distribuição de plataformas

### `tse_fefc`

- `info_tse_fefc`
- `fefc_por_partido(ano, top)` — ranking de recebedores
- `fefc_por_partido_genero(ano)` — **auditoria da cota de 30% feminino**
- `valores_distintos_fefc(coluna)`

## Meta-tool global

O server raiz expõe `listar_datasets_disponiveis` — lista todos os
datasets registrados (ativos ou não) com tamanho, idade do cache e fonte.

## Cross-dataset joins

Datasets TSE compartilham a chave `sq_candidato`. Várias tools
(ex: `top_patrimonios_cargo`, `redes_por_partido`) usam `DuckDB ATTACH`
para juntar com `tse_candidatos` sem duplicar dados. Requer ambos os
datasets estarem ativos simultaneamente:

```bash
MCP_BRASIL_DATASETS=tse_candidatos,tse_bens,tse_redes_sociais
```

## Onde os ZIPs vêm

Todos os ZIPs são buscados direto do CDN do TSE ou SPU:

- TSE: `https://cdn.tse.jus.br/estatistica/sead/odsele/...`
- SPU: `https://drive.spu.gestao.gov.br/index.php/s/{token}/download`

Fontes oficiais:

- [TSE Portal de Dados Abertos](https://dadosabertos.tse.jus.br/)
- [SPU Patrimônio de Todos](https://sistema.patrimoniodetodos.gov.br/)
- [Licença: Lei 12.527/2011 (LAI) + Decreto 8.777/2016](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm)

## Limitações

- **Deploy serverless**: datasets requerem disco persistente — não
  funcionam em Azure Functions, AWS Lambda, etc. O registry pula
  features de dataset em ambientes efêmeros.
- **Schema drift**: TSE muda colunas entre anos (ex: `NM_EMAIL` em 2016
  virou `DS_EMAIL` em 2024). A view usa `UNION ALL BY NAME` e colunas
  ausentes viram NULL — tolerado, mas queries cross-year precisam de
  `COALESCE` quando o nome de campo mudou.
- **Download instável**: servidores TSE/SPU às vezes sofrem timeouts.
  Use `MCP_BRASIL_DATASET_TIMEOUT=900` para datasets grandes.

## Arquitetura interna

Componentes principais em `src/mcp_brasil/_shared/datasets/`:

- `DatasetSpec` — contrato declarativo (url, zip_member, ttl, csv_options, pii_columns, sources)
- `DatasetRegistry` — auto-discovery das features em `datasets/` filtrado por env
- `loader.py` — download com httpx (redirects), transcoding cp1252→utf-8,
  extração ZIP, ingestão em DuckDB, UNION ALL BY NAME para multi-source
- `lgpd.py` — mascaramento de colunas PII por default
- `cache.py` — paths XDG + manifesto JSON por dataset

Queries rodam via conexão read-only, isolando mutations. Cross-DB joins
usam `ATTACH ... (READ_ONLY)` entre arquivos `.duckdb` distintos.
