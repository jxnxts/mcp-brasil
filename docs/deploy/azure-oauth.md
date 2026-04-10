# Deploy — OAuth com Azure Entra ID

Guia passo a passo para habilitar autenticação OAuth 2.0 no `mcp-brasil`
usando Azure Entra ID como Identity Provider. Essa é a configuração
necessária para usar o server como Custom Connector no **Claude.ai web**,
já que a UI de Connectors aceita apenas OAuth (não aceita Bearer token
estático via header customizado).

## Pré-requisitos

- Um Azure Container App (ou qualquer host público) rodando o `mcp-brasil`
  com URL pública acessível via HTTPS (ex:
  `https://mcp-brasil.example.com`). Chame essa URL de `$BASE_URL`.
- Uma subscription Azure com permissão de criar App Registrations no tenant.
- Azure CLI (`az`) instalado e autenticado (`az login`).
- `mcp-brasil` na versão que suporta `MCP_BRASIL_AUTH_MODE=oauth`.

## 1. Criar o App Registration

Portal → **Microsoft Entra ID** → **App registrations** → **New registration**.

- **Name:** `mcp-brasil`
- **Supported account types:** _Accounts in this organizational directory only (Single tenant)_
  Escolha multi-tenant apenas se precisar permitir login de contas externas.
- **Redirect URI:**
  - **Platform:** `Web`
  - **URL:** `{BASE_URL}/auth/callback`
    Ex: `https://mcp-brasil.example.com/auth/callback`

Clique **Register**.

Na página do App Registration, anote:

- **Application (client) ID** → será `AZURE_CLIENT_ID`
- **Directory (tenant) ID** → será `AZURE_TENANT_ID`

## 2. Expose an API — criar o scope `read`

No menu esquerdo do App Registration: **Expose an API**.

1. Clique **Add** ao lado de **Application ID URI** e aceite o default
   (`api://<client-id>`).
2. Clique **Add a scope**:
   - **Scope name:** `read`
   - **Who can consent:** _Admins and users_
   - **Admin consent display name:** `Read mcp-brasil data`
   - **Admin consent description:** `Allows the app to query mcp-brasil tools`
   - **User consent display name:** `Read mcp-brasil data`
   - **User consent description:** `Allows the app to query mcp-brasil tools on your behalf`
   - **State:** `Enabled`
3. Clique **Add scope**.

## 3. Manifest — `requestedAccessTokenVersion: 2`

No menu esquerdo: **Manifest**. Encontre a chave
`requestedAccessTokenVersion` e altere para `2`:

```json
{
  "requestedAccessTokenVersion": 2
}
```

Clique **Save**. Sem isso, o token emitido é v1.0 e o FastMCP não consegue
validar.

## 4. Criar o Client Secret

Menu esquerdo: **Certificates & secrets** → **Client secrets** → **New client secret**.

- **Description:** `mcp-brasil production`
- **Expires:** 24 meses (ou menos, conforme política)

Clique **Add**. Copie o valor **Value** (não o Secret ID) imediatamente —
ele só aparece uma vez. Será `AZURE_CLIENT_SECRET`.

## 5. Anotar credenciais

Ao final do passo 4 você deve ter:

| Variável              | De onde veio                        |
| --------------------- | ----------------------------------- |
| `AZURE_CLIENT_ID`     | Overview → Application (client) ID  |
| `AZURE_TENANT_ID`     | Overview → Directory (tenant) ID    |
| `AZURE_CLIENT_SECRET` | Certificates & secrets → Value      |

## 6. Atualizar o Container App

Armazene as credenciais como secrets do Container App (nunca em texto puro
no `--set-env-vars`):

```bash
RESOURCE_GROUP=rg-mcp-brasil
APP_NAME=mcp-brasil
BASE_URL=https://mcp-brasil.example.com

az containerapp secret set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --secrets \
    azure-client-id=<AZURE_CLIENT_ID> \
    azure-client-secret=<AZURE_CLIENT_SECRET> \
    azure-tenant-id=<AZURE_TENANT_ID>
```

Agora configure as env vars (as três OAuth puxam dos secrets via
`secretref:`):

```bash
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    MCP_BRASIL_AUTH_MODE=oauth \
    MCP_BRASIL_OAUTH_PROVIDER=azure \
    MCP_BRASIL_BASE_URL=$BASE_URL \
    AZURE_REQUIRED_SCOPES=read \
    AZURE_CLIENT_ID=secretref:azure-client-id \
    AZURE_CLIENT_SECRET=secretref:azure-client-secret \
    AZURE_TENANT_ID=secretref:azure-tenant-id
```

Durante a transição, você pode manter o `MCP_BRASIL_API_TOKEN` como fallback,
mas o `AUTH_MODE=oauth` tem precedência. Para remover o token antigo:

```bash
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --remove-env-vars MCP_BRASIL_API_TOKEN
```

## 7. Verificar o deploy

```bash
# OAuth discovery endpoint deve retornar metadata
curl -sS $BASE_URL/.well-known/oauth-protected-resource | jq

# Chamada sem token deve retornar 401 com www-authenticate apontando pro
# authorization server
curl -sS -i -X POST $BASE_URL/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{}}'
# -> HTTP/2 401
# -> www-authenticate: Bearer resource_metadata=...

# Logs devem confirmar o provider escolhido
az containerapp logs show -n $APP_NAME -g $RESOURCE_GROUP --tail 30 | grep -i auth
# -> "Auth enabled: AzureProvider (Entra ID)"
```

## 8. Testar no Claude.ai web

1. **Settings** → **Connectors** → **Add custom connector**
2. **Name:** `mcp-brasil`
3. **URL:** `{BASE_URL}/mcp`
4. Deixe os campos ID/Secret em branco — o Claude vai descobrir via DCR
   (Dynamic Client Registration) ao passar pelo proxy OAuth do FastMCP.
5. Clique **Add**. Você deve ser redirecionado para o login Microsoft.
6. Autentique com uma conta do tenant e conceda o scope `read`.
7. Volte ao Claude — o conector deve aparecer como **Connected** (verde) e
   as tools do `mcp-brasil` ficam disponíveis.

> Se quiser forçar um `client_id` específico (por exemplo, para pular DCR e
> usar o próprio App Registration como client), cole o `AZURE_CLIENT_ID` no
> campo Client ID e o `AZURE_CLIENT_SECRET` no campo Client Secret.

## Troubleshooting

### 401 mesmo após o login

- Verifique que `requestedAccessTokenVersion: 2` está no manifest. Sem isso,
  o token é v1.0 e o FastMCP rejeita.
- Verifique que `AZURE_REQUIRED_SCOPES=read` bate com o scope criado no
  passo 2.

### `AADSTS50011: redirect URI mismatch`

O redirect URI registrado no App Registration precisa ser exatamente
`{BASE_URL}/auth/callback`. Sem barra final, com o host exato (incluindo
`https://`).

### `invalid_scope` ou `AADSTS65001: consent required`

- O scope precisa existir em **Expose an API** com status `Enabled`.
- Se for multi-tenant, rode um **admin consent** no tenant do usuário antes
  do primeiro login.

### Claude.ai mostra "Failed to load connector"

- Verifique `$BASE_URL/.well-known/oauth-protected-resource` — deve
  retornar JSON válido.
- Verifique que o `BASE_URL` está acessível publicamente (não é um domínio
  interno).

### Voltar para Bearer token estático

Se precisar reverter rapidamente sem mexer no App Registration:

```bash
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    MCP_BRASIL_AUTH_MODE=static \
    MCP_BRASIL_API_TOKEN=<seu-token>
```

Isso volta o server ao comportamento anterior (`StaticTokenVerifier`)
sem precisar recompilar imagem.
