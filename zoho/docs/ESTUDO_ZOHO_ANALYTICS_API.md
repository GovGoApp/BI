# Estudo - acesso aos dados do Zoho Analytics

## Objetivo

Montar uma primeira camada de acesso aos dados que hoje alimentam o BI no Zoho Analytics, para depois construir um BI de suprimentos com a mesma identidade visual do painel de fornecedores.

## Caminho recomendado

Usar a API v2 do Zoho Analytics com OAuth2.

Em portugues simples: vamos criar uma "chave de aplicativo" no Zoho, pedir permissao para esse aplicativo ler o Zoho Analytics e guardar um `refresh_token`. Depois disso, o script consegue gerar sozinho os access tokens temporarios sempre que precisar buscar dados.

O que cada nome significa:

- `Client ID`: identificacao do aplicativo criado no Zoho API Console.
- `Client Secret`: senha do aplicativo criado no Zoho API Console.
- `Authorization code`: codigo temporario, gerado manualmente no Zoho, que expira rapido.
- `Refresh token`: chave duradoura. E o valor mais importante para automacao.
- `Access token`: chave temporaria, valida por cerca de 1 hora. O script gera automaticamente usando o `refresh_token`.
- `Org ID`: identificador da organizacao Zoho Analytics.
- `Workspace ID`: identificador do workspace onde estao as tabelas/views do BI.

Fluxo completo:

1. Criar um `Self Client` no Zoho API Console.
2. Gerar um authorization code com os escopos necessarios.
3. Trocar o authorization code por `access_token` e `refresh_token`.
4. Guardar o `refresh_token` fora do codigo.
5. Usar o `refresh_token` para descobrir `org_id` e `workspace_id`.
6. Listar as views/tabelas do workspace.
7. Exportar os dados por `viewId` ou por SQL.

## Passo a passo inicial

## A partir da tela inicial do Zoho Analytics

Pelo print, voce esta em:

```text
https://analytics.zoho.com/ZDBHome.cc
```

Essa e a home do Zoho Analytics, onde ficam organizacoes, workspaces, tabelas, relatorios e dashboards. Ela nao e o lugar onde se cria a chave OAuth.

Nesta tela, fazer primeiro:

1. No canto superior esquerdo, clicar no nome da organizacao atual.
2. Selecionar a organizacao onde o BI atual existe. No print, provavelmente e `BI - Business Int...`, porque a organizacao `hdalazoana` aparece sem painel.
3. Depois de selecionar a organizacao correta, verificar se aparecem workspaces, tabelas, relatorios ou dashboards.
4. Se nao aparecer nada, pode ser que:
   - o usuario atual nao tenha permissao no workspace do BI;
   - o BI esteja em outra organizacao;
   - o BI esteja compartilhado por outro usuario;
   - a conta esteja numa edicao/plano com restricao.

Depois disso, abrir outra aba do navegador para criar o acesso de API:

```text
https://api-console.zoho.com/
```

Resumo mental:

- `analytics.zoho.com`: onde voce ve o BI e escolhe a organizacao/workspace.
- `api-console.zoho.com`: onde voce cria a chave tecnica para o script acessar os dados.

### 1. Criar o Self Client

1. Abrir https://api-console.zoho.com/
2. Entrar com o mesmo usuario que acessa o Zoho Analytics.
3. Clicar em `Get Started`, se aparecer.
4. Escolher `Self Client`.
5. Clicar em `Create Now`.
6. Abrir a aba `Client Secret`.
7. Copiar:
   - `Client ID`
   - `Client Secret`

No PowerShell, preencher:

```powershell
$env:ZOHO_ANALYTICS_CLIENT_ID="cole_aqui_o_client_id"
$env:ZOHO_ANALYTICS_CLIENT_SECRET="cole_aqui_o_client_secret"
```

Alternativa usando o arquivo local `zoho/zoho.env`:

```text
ZOHO_ANALYTICS_CLIENT_ID=cole_aqui_o_client_id
ZOHO_ANALYTICS_CLIENT_SECRET=cole_aqui_o_client_secret
```

### 2. Gerar o authorization code

Dentro do mesmo Self Client:

1. Abrir a aba `Generate Code`.
2. Em `Scope`, colar exatamente:

```text
ZohoAnalytics.metadata.read,ZohoAnalytics.data.read
```

3. Escolher um tempo de expiracao curto, por exemplo 10 minutos.
4. Em descricao, escrever algo como `Leitura BI suprimentos`.
5. Clicar em `Create`.
6. Copiar o codigo gerado.

Esse codigo expira rapido. Se expirar, basta gerar outro.

### 3. Trocar o authorization code por refresh token

Com `Client ID` e `Client Secret` ja definidos no PowerShell, rodar:

```powershell
python zoho/scripts/zoho_analytics_client.py exchange-code --code "cole_aqui_o_codigo_temporario"
```

Ou, usando o arquivo `zoho/zoho.env`:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env exchange-code --code "cole_aqui_o_codigo_temporario"
```

O Zoho deve responder um JSON com `access_token` e `refresh_token`.

Copiar o valor de `refresh_token` e definir:

```powershell
$env:ZOHO_ANALYTICS_REFRESH_TOKEN="cole_aqui_o_refresh_token"
```

Ou adicionar no arquivo `zoho/zoho.env`:

```text
ZOHO_ANALYTICS_REFRESH_TOKEN=cole_aqui_o_refresh_token
```

Depois desse passo, o authorization code temporario nao sera mais necessario.

### 4. Descobrir org_id

Rodar:

```powershell
python zoho/scripts/zoho_analytics_client.py orgs
```

Ou, usando o arquivo local:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env orgs
```

O comando lista as organizacoes acessiveis. Copiar o `orgId` correto e definir:

```powershell
$env:ZOHO_ANALYTICS_ORG_ID="cole_aqui_o_org_id"
```

### 5. Descobrir workspace_id

Rodar:

```powershell
python zoho/scripts/zoho_analytics_client.py workspaces
```

Ou, usando o arquivo local:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env workspaces
```

O comando lista os workspaces acessiveis e mostra `workspaceId`, `orgId` e nome. Copiar o workspace do BI de suprimentos/BI atual e definir:

```powershell
$env:ZOHO_ANALYTICS_WORKSPACE_ID="cole_aqui_o_workspace_id"
```

### 6. Validar que tudo funciona

Validar token:

```powershell
python zoho/scripts/zoho_analytics_client.py token
```

Listar tabelas/views do workspace:

```powershell
python zoho/scripts/zoho_analytics_client.py views
```

Ou, usando o arquivo local:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env token
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env views
```

Se esse comando listar views, o acesso aos dados esta pronto para o primeiro download.

## Escopos OAuth

Escopos minimos para o primeiro teste:

- `ZohoAnalytics.metadata.read`: listar workspaces/views.
- `ZohoAnalytics.data.read`: exportar dados.

Se depois formos gravar dados de volta no Zoho Analytics, avaliar `ZohoAnalytics.data.create` ou escopos de update, mas isso nao faz parte desta primeira etapa.

## Endpoints principais

Listar views do workspace:

```text
GET https://<ZohoAnalytics_Server_URI>/restapi/v2/workspaces/<workspace-id>/views
Headers:
  Authorization: Zoho-oauthtoken <access_token>
  ZANALYTICS-ORGID: <org-id>
```

Exportacao sincronizada de uma view:

```text
GET https://<ZohoAnalytics_Server_URI>/restapi/v2/workspaces/<workspace-id>/views/<view-id>/data?CONFIG=<json_url_encoded>
```

Uso indicado para tabelas menores. A documentacao orienta usar exportacao assincrona para tabelas acima de 1 milhao de linhas, live connect workspaces, dashboards e query tables.

Exportacao assincrona por view:

```text
GET https://<ZohoAnalytics_Server_URI>/restapi/v2/bulk/workspaces/<workspace-id>/views/<view-id>/data?CONFIG=<json_url_encoded>
```

Exportacao assincrona por SQL:

```text
GET https://<ZohoAnalytics_Server_URI>/restapi/v2/bulk/workspaces/<workspace-id>/data?CONFIG=<json_url_encoded>
```

Status do job:

```text
GET https://<ZohoAnalytics_Server_URI>/restapi/v2/bulk/workspaces/<workspace-id>/exportjobs/<job-id>
```

Download do job:

```text
GET https://<ZohoAnalytics_Server_URI>/restapi/v2/bulk/workspaces/<workspace-id>/exportjobs/<job-id>/data
```

## Variaveis de ambiente

No PowerShell:

```powershell
$env:ZOHO_ANALYTICS_CLIENT_ID="1000.xxxxx"
$env:ZOHO_ANALYTICS_CLIENT_SECRET="xxxxx"
$env:ZOHO_ANALYTICS_REFRESH_TOKEN="1000.xxxxx.xxxxx"
$env:ZOHO_ANALYTICS_ORG_ID="123456789"
$env:ZOHO_ANALYTICS_WORKSPACE_ID="987654321"
```

Ou em `zoho/zoho.env`:

```text
ZOHO_ANALYTICS_CLIENT_ID=1000.xxxxx
ZOHO_ANALYTICS_CLIENT_SECRET=xxxxx
ZOHO_ANALYTICS_REFRESH_TOKEN=1000.xxxxx.xxxxx
ZOHO_ANALYTICS_ORG_ID=123456789
ZOHO_ANALYTICS_WORKSPACE_ID=987654321
```

O padrao do script usa:

```powershell
$env:ZOHO_ANALYTICS_ACCOUNTS_URL="https://accounts.zoho.com"
$env:ZOHO_ANALYTICS_API_URL="https://analyticsapi.zoho.com"
```

Se a conta estiver em outro data center, ajustar esses dois dominios conforme o data center do Zoho.

## Como testar localmente

Testes unitarios, sem chamar Zoho:

```powershell
python -m unittest discover -s zoho/tests
```

Validar credenciais e renovacao do token:

```powershell
python zoho/scripts/zoho_analytics_client.py token
```

Com arquivo local:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env token
```

Listar organizacoes:

```powershell
python zoho/scripts/zoho_analytics_client.py orgs
```

Com arquivo local:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env orgs
```

Listar workspaces:

```powershell
python zoho/scripts/zoho_analytics_client.py workspaces
```

Com arquivo local:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env workspaces
```

Listar views acessiveis no workspace:

```powershell
python zoho/scripts/zoho_analytics_client.py views
```

Exportar uma view pequena diretamente:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env export-view --view-id 123456789 --out zoho/output/amostra_view.csv
```

Criar exportacao assincrona de uma view maior e baixar quando concluir:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env export-view --view-id 123456789 --async-export --wait --out zoho/output/amostra_view.csv
```

Exportar via SQL:

```powershell
python zoho/scripts/zoho_analytics_client.py --env-file zoho/zoho.env export-sql --sql "select * from Compras" --wait --out zoho/output/compras.csv
```

## Links oficiais usados

- Self Client OAuth: https://www.zoho.com/accounts/protocol/oauth/self-client/overview.html
- Authorization code flow: https://www.zoho.com/accounts/protocol/oauth/self-client/authorization-code-flow.html
- Get Views: https://www.zoho.com/analytics/api/v2/metadata-api/get-views.html
- Export Data: https://www.zoho.com/analytics/api/v2/bulk-api/export-data.html
- Export Data assinc.: https://www.zoho.com/analytics/api/v2/bulk-api/export-data-async.html
- Criar job por View ID: https://www.zoho.com/analytics/api/v2/bulk-api/export-data-async/create-export/view-id.html
- Criar job por SQL: https://www.zoho.com/analytics/api/v2/bulk-api/export-data-async/create-export/sql-query.html
- Status do job: https://www.zoho.com/analytics/api/v2/bulk-api/export-data-async/get-export.html
- Download do job: https://www.zoho.com/analytics/api/v2/bulk-api/export-data-async/download-export.html
