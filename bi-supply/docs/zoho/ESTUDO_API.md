# Estudo — Acesso à API do Zoho Analytics

## Objetivo

Documentar o caminho completo para acessar os dados do Zoho Analytics via API v2 com OAuth2, desde a criação da chave até a exportação de dados.

## Conceitos

| Termo | O que é |
|---|---|
| `Client ID` | Identificação do aplicativo criado no Zoho API Console |
| `Client Secret` | Senha do aplicativo |
| `Authorization code` | Código temporário, expira em minutos |
| `Refresh token` | Chave duradoura — o valor mais importante para automação |
| `Access token` | Chave temporária, válida ~1 hora, gerada automaticamente pelo script |
| `Org ID` | Identificador da organização Zoho Analytics |
| `Workspace ID` | Identificador do workspace (ex: `SUPRIMENTOS`) |

## Fluxo completo

1. Criar um `Self Client` no Zoho API Console
2. Gerar um authorization code com os escopos necessários
3. Trocar o authorization code por `access_token` e `refresh_token`
4. Guardar o `refresh_token` em `zoho/zoho.env`
5. Descobrir `org_id` e `workspace_id`
6. Listar views/tabelas do workspace
7. Exportar dados por `viewId` ou SQL

## Passo a passo

### 1. Criar o Self Client

1. Abrir https://api-console.zoho.com/
2. Entrar com o mesmo usuário que acessa o Zoho Analytics
3. Escolher `Self Client` → `Create Now`
4. Aba `Client Secret` → copiar `Client ID` e `Client Secret`

Colocar em `zoho/zoho.env`:

```
ZOHO_ANALYTICS_CLIENT_ID=cole_aqui
ZOHO_ANALYTICS_CLIENT_SECRET=cole_aqui
```

### 2. Gerar o authorization code

Dentro do Self Client:

1. Aba `Generate Code`
2. Em `Scope`, colar:

```
ZohoAnalytics.metadata.read,ZohoAnalytics.data.read
```

3. Clicar em `Create` e copiar o código gerado (expira em ~10 minutos)

### 3. Trocar o código pelo refresh token

```powershell
python zoho/client.py --env-file zoho/zoho.env exchange-code --code "CODIGO_AQUI"
```

O Zoho responde um JSON com `access_token` e `refresh_token`. Copiar o `refresh_token` para `zoho/zoho.env`:

```
ZOHO_ANALYTICS_REFRESH_TOKEN=1000.xxxxx.xxxxx
```

Depois disso, o authorization code não é mais necessário.

### 4. Descobrir org_id

```powershell
python zoho/client.py --env-file zoho/zoho.env orgs
```

Copiar o `orgId` correto para `zoho/zoho.env`:

```
ZOHO_ANALYTICS_ORG_ID=703842975
```

### 5. Descobrir workspace_id

```powershell
python zoho/client.py --env-file zoho/zoho.env workspaces
```

O workspace de suprimentos tem ID `2130260000001511306`:

```
ZOHO_ANALYTICS_WORKSPACE_ID=2130260000001511306
```

### 6. Validar acesso

```powershell
python zoho/client.py --env-file zoho/zoho.env token
python zoho/client.py --env-file zoho/zoho.env views
```

### 7. Exportar dados

View pequena (síncrona):

```powershell
python zoho/client.py --env-file zoho/zoho.env export-view --view-id VIEW_ID --out data/raw/nome.csv
```

View grande (assíncrona — espera o job terminar):

```powershell
python zoho/client.py --env-file zoho/zoho.env export-view --view-id VIEW_ID --async-export --wait --out data/raw/nome.csv
```

Via SQL:

```powershell
python zoho/client.py --env-file zoho/zoho.env export-sql --sql "select * from NFE limit 1000" --wait --out data/raw/nfe_amostra.csv
```

## Escopos OAuth

Mínimos para leitura:

- `ZohoAnalytics.metadata.read` — listar workspaces e views
- `ZohoAnalytics.data.read` — exportar dados

## Endpoints principais

| Operação | Endpoint |
|---|---|
| Listar views | `GET /restapi/v2/workspaces/{workspace-id}/views` |
| Exportar view (sync) | `GET /restapi/v2/workspaces/{workspace-id}/views/{view-id}/data?CONFIG=...` |
| Criar job de export (async) | `GET /restapi/v2/bulk/workspaces/{workspace-id}/views/{view-id}/data?CONFIG=...` |
| Exportar por SQL (async) | `GET /restapi/v2/bulk/workspaces/{workspace-id}/data?CONFIG=...` |
| Status do job | `GET /restapi/v2/bulk/workspaces/{workspace-id}/exportjobs/{job-id}` |
| Download do job | `GET /restapi/v2/bulk/workspaces/{workspace-id}/exportjobs/{job-id}/data` |

Header obrigatório em todos os requests:

```
Authorization: Zoho-oauthtoken {access_token}
ZANALYTICS-ORGID: {org_id}
```

## Links oficiais

- Self Client: https://www.zoho.com/accounts/protocol/oauth/self-client/overview.html
- Authorization code flow: https://www.zoho.com/accounts/protocol/oauth/self-client/authorization-code-flow.html
- Get Views: https://www.zoho.com/analytics/api/v2/metadata-api/get-views.html
- Export Data async: https://www.zoho.com/analytics/api/v2/bulk-api/export-data-async.html
