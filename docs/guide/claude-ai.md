<div align="center">

<img src="../assets/logo.png" alt="mcp-brasil logo" width="100">

# mcp-brasil no Claude.ai Web

**Conecte o mcp-brasil como Custom Connector no Claude.ai**

363 tools · 87 resources · 62 prompts · 41 APIs governamentais brasileiras

Acesse dados do IBGE, Banco Central, Câmara, Senado, Portal da Transparência, TSE, DataJud e mais — direto no chat do Claude.ai, sem instalar nada.

</div>

---

## Como funciona

O `mcp-brasil` roda como server MCP público com autenticação OAuth 2.0 (Azure Entra ID). O Claude.ai conecta automaticamente via **Dynamic Client Registration (DCR)** — você só precisa colar a URL e autorizar.

```
Claude.ai  →  OAuth (Azure Entra ID)  →  mcp-brasil server  →  41 APIs públicas
```

## Configurar em 3 passos

### 1. Abrir configurações

No Claude.ai web, vá em **Settings** → **Connectors** → **Add custom connector**.

### 2. Adicionar o connector

| Campo | Valor |
|-------|-------|
| **Name** | `mcp-brasil` |
| **URL** | `https://<seu-fqdn>/mcp` |
| **Client ID** | _(deixar vazio)_ |
| **Client Secret** | _(deixar vazio)_ |

> Deixe Client ID e Client Secret vazios — o Claude.ai usa DCR (Dynamic Client Registration) automaticamente.

### 3. Autorizar acesso

1. Clique **Add**
2. Na tela de consent, clique **Allow Access**
3. Faça login com sua conta Microsoft (qualquer tenant)
4. O connector aparece como **Connected** (verde)

Pronto! As 363 tools do mcp-brasil estão disponíveis no seu chat.

## Testar

Abra um novo chat no Claude.ai e pergunte:

> "Qual a taxa Selic atual segundo o Banco Central?"

> "Quais os deputados federais de São Paulo? Liste os 10 com mais despesas em 2024."

> "Busque processos sobre licitação irregular no DataJud."

> "Qual a população de cada estado brasileiro segundo o IBGE?"

> "Quais os maiores contratos do governo federal em 2024?"

## Fontes de dados disponíveis

| Área | APIs | Exemplos |
|------|:----:|----------|
| Economia e Finanças | 2 | Banco Central (Selic, IPCA, câmbio), BNDES |
| Geografia e Estatística | 1 | IBGE (estados, municípios, agregados) |
| Legislativo | 2 | Câmara dos Deputados, Senado Federal |
| Transparência e Fiscalização | 12 | Portal da Transparência, TCU, 9 TCEs estaduais |
| Judiciário | 2 | DataJud/CNJ, STF/STJ/TST |
| Eleitoral | 2 | TSE, Anúncios Eleitorais (Meta) |
| Meio Ambiente | 2 | INPE (queimadas/desmatamento), ANA (hidrologia) |
| Saúde | 8 | CNES/DataSUS, ANVISA, Farmácia Popular, RENAME |
| Segurança Pública | 3 | Atlas da Violência, SINESP, Fórum de Segurança |
| Compras Públicas | 2 | PNCP/ComprasNet, TransfereGov |
| Dados Abertos e Utilidades | 4 | BrasilAPI, dados.gov.br, Diário Oficial, Tábua de Marés |

> 38 APIs não requerem chave. 3 usam chaves gratuitas (Transparência, DataJud, Meta).

## Troubleshooting

### "Couldn't reach the MCP server"

- Verifique se a URL termina com `/mcp` (não apenas o domínio)
- O server pode estar reiniciando — aguarde 30 segundos e tente novamente

### "Authorization with the MCP server failed"

- Remova o connector e adicione novamente (tokens expirados são renovados automaticamente, mas em caso de erro persistente, reconectar resolve)
- Certifique-se de que clicou **Allow Access** na tela de consent

### Connector aparece mas tools não funcionam

- Tente perguntar algo específico, como "Use o mcp-brasil para consultar a taxa Selic"
- O Claude.ai usa discovery automático — perguntas mais específicas ativam as tools certas

### Ícone da Microsoft aparece no connector

- Isso é normal — o Claude.ai mostra o ícone do provider OAuth (Azure/Microsoft)
- Não afeta o funcionamento

## Sobre

O `mcp-brasil` é um projeto open-source que conecta AI agents a dados governamentais do Brasil via [Model Context Protocol (MCP)](https://modelcontextprotocol.io).

- **GitHub:** [github.com/mcp-brasil](https://github.com/Mcp-Brasil/mcp-brasil)
- **PyPI:** [pypi.org/project/mcp-brasil](https://pypi.org/project/mcp-brasil)
- **Licença:** MIT

---

<div align="center">

**Todos os dados vêm de APIs oficiais do governo brasileiro.**

O server não gera, modifica ou editorializa nenhum dado.

</div>
