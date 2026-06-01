# Diário de Bordo — BI de Suprimentos

Registro técnico de todas as alterações do projeto, ordenado do mais recente ao mais antigo.

**Regras:**
- Atualizar este diário a cada alteração relevante, sempre com data e detalhes técnicos.
- Atualizar o README somente quando a estrutura geral ou o uso do projeto mudar.
- Nunca deixar uma sessão de trabalho sem registrar o que foi feito.

---

## [2026-06-01] Fundação do projeto bi-supply

### O que foi feito

Projeto criado do zero na pasta `bi-supply`, substituindo a estrutura anterior em `supply` que tinha problemas de organização e arquitetura.

### Motivação

O projeto anterior (`supply`) foi desenvolvido com outra ferramenta e não respeitou os princípios de design definidos no `BI Design System.html` e no mock `BI Suprimentos v4.html`. A organização de pastas era confusa, os scripts misturavam responsabilidades e a documentação era inconsistente.

### Estrutura criada

```
bi-supply/
├── README.md
├── DIARIO.md
├── zoho/zoho.env          ← credenciais existentes
├── zoho/zoho.env.example  ← template
├── pipeline/              ← pasta para extract, transform, build
├── data/raw/              ← dados brutos do Zoho
├── data/processed/        ← métricas calculadas
├── dashboard/tabs/        ← configs YAML por aba
├── dashboard/templates/   ← templates HTML por tipo
├── dashboard/static/      ← CSS e JS
├── nlsql/                 ← módulo NL-SQL
├── tests/zoho/
├── tests/pipeline/
├── tests/nlsql/
├── tests/dashboard/
├── docs/projeto/
├── docs/dados/
├── docs/design/
├── docs/zoho/
└── dist/
```

### Arquivos de design preservados

- `design/BI Design System.html` — fonte da verdade visual (não modificar)
- `design/BI Suprimentos v4.html` — mock de referência com as 15 abas definitivas

### Abas definidas (v4)

Lidas diretamente do HTML do mock v4:

| data-page | Label |
|---|---|
| resumo | Resumo |
| oportunidades | Oportunidades |
| categorias | Categorias |
| filiais | Filiais |
| estoque | Estoque |
| forn360 | Fornecedor |
| produtos | Produtos |
| cotacoes | Cotações |
| impacto | Impacto |
| inflacao | Inflação |
| fiscal | Fiscal |
| financeiro | Financeiro |
| adiantamentos | Adiantamentos |
| servicos | Serviços |
| qualidade | Dados |

### Docs migrados do projeto supply

| Origem | Destino |
|---|---|
| `supply/docs/ESTUDO_ZOHO_ANALYTICS_API.md` | `docs/zoho/ESTUDO_API.md` |
| `supply/docs/INVENTARIO_ZOHO_ANALYTICS_WORKSPACES.md` | `docs/zoho/INVENTARIO_WORKSPACES.md` |
| `supply/docs/PERFIL_DADOS_SUPRIMENTOS.md` | `docs/dados/PERFIL_FONTES.md` |
| `supply/docs/ESTUDO_SUPRIMENTOS_BI_E_FERRAMENTAS.md` | `docs/dados/ESTUDO_DOMINIOS.md` |
| `supply/docs/claude_design/01_BRIEFING.md` | `docs/projeto/BRIEFING.md` |
| `supply/docs/claude_design/05_DADOS_E_DOMINIOS.md` | `docs/dados/DOMINIOS_NEGOCIO.md` |
| `CATEGORIAS_I_D_ORDENADAS.md` + `CATEGORIAS_I_D_A_ORDENADAS.md` | `docs/dados/CATEGORIAS.md` (merge) |
| `ANALISE_AUDITORIA_BI_SUPRIMENTOS_V3.md` | `docs/design/COBERTURA_ABAS.md` |
| `PROMPT_CORRECAO_V3_CLAUDE_DESIGN.md` | `docs/design/ESPECIFICACAO_ABAS.md` |

### Docs descartados do supply

Não migrados por serem prompts para Claude Design (não são documentação do projeto), versões desatualizadas, ou ponteiros para arquivos que não existem mais.

### Docs criados do zero

- `docs/projeto/ARQUITETURA.md` — arquitetura técnica atual (3 camadas + NL-SQL)
- `docs/design/MAPA_ABAS.md` — mapa das 15 abas baseado no v4.html
- `docs/design/CRITERIOS_ACEITACAO.md` — critérios para validar o dashboard

### Decisões técnicas registradas

1. **Dados embutidos no HTML**: os dados processados são embutidos como JSON dentro do `dist/index.html`. O dashboard funciona offline e pode ser distribuído sem arquivos externos.

2. **Pipeline separado em 3 etapas**: extract → transform → build. Cada etapa tem responsabilidade única e pode rodar independentemente.

3. **Snapshot local**: os dados são exportados do Zoho periodicamente (não em tempo real). A execução de `extract.py` atualiza os snapshots em `data/raw/`.

4. **YAML simples por aba**: cada aba tem um `.yml` em `dashboard/tabs/` que declara fontes, filtros e elementos. O YAML não reinventa o CSS — os estilos vêm do Design System.

5. **Módulo NL-SQL**: baseado no padrão de tool calls com LLM (guia `GUIA_IMPLEMENTACAO_MODO_RELATORIO_NL_SQL.md`). Permite fazer perguntas em português que viram SQL executado no Zoho. Ficará em `nlsql/`.

### Fase 0 concluída — Próximos passos

- [x] Reescrever `zoho/client.py`
- [ ] Criar `zoho/catalog.py`
- [ ] Criar testes de catalog

---

## [2026-06-01] Fase 1 — Passo 1: zoho/client.py

**Commit:** `f94ecaf`

### O que foi feito

Reescrita limpa do cliente Zoho Analytics API v2, portado de `supply/scripts/zoho_analytics_client.py` para `bi-supply/zoho/client.py`.

### Arquivo: `zoho/client.py` (≈270 linhas)

**Estruturas principais:**

```
load_env_file(path)         ← lê .env e injeta em os.environ
ZohoConfig                  ← dataclass frozen com credenciais
  .from_env(require_workspace=True)
ZohoClient(config, session, timeout)
  .refresh_token()          ← POST /oauth/v2/token → access_token
  .exchange_code(...)       ← troca authorization code por refresh_token (static)
  .get_orgs(token)          ← GET /restapi/v2/orgs
  .get_workspaces(token)    ← GET /restapi/v2/workspaces
  .get_views(token, keyword)← GET /restapi/v2/workspaces/{ws}/views
  .export_view(...)         ← exportação síncrona (views pequenas)
  .create_job_view(...)     ← cria job bulk assíncrono por view_id
  .create_job_sql(...)      ← cria job bulk assíncrono por SQL SELECT
  .job_status(job_id, token)← consulta status do job
  .wait_job(job_id, token, interval, max_attempts) ← polling com progresso
  .download_job(job_id, out, token) ← baixa o arquivo do job concluído
ZohoError(RuntimeError)     ← erro da API ou resposta inesperada
```

**Melhorias em relação ao código anterior:**

| Antes | Depois |
|---|---|
| `from_env()` + `from_env_for_discovery()` (dois métodos) | `from_env(require_workspace=False)` (um método com flag) |
| `session.request("GET", ...)` para tudo | `session.get(...)` / `session.post(...)` — mais idiomático |
| Nenhum feedback durante polling | Imprime progresso: `Aguardando job ... tentativa N/60` |
| `views` mostrava só primeiros 20 | `--limit N` (padrão 50, `--limit 0` = todas) |
| Nome `ZohoAnalyticsError` | `ZohoError` — mais curto |

**CLI disponível:**

```powershell
python zoho/client.py --env-file zoho/zoho.env token
python zoho/client.py --env-file zoho/zoho.env orgs
python zoho/client.py --env-file zoho/zoho.env workspaces
python zoho/client.py --env-file zoho/zoho.env views [--keyword NFE] [--limit 0]
python zoho/client.py --env-file zoho/zoho.env exchange-code --code CODIGO
python zoho/client.py --env-file zoho/zoho.env export-view --view-id ID --out arquivo.csv [--async --wait]
python zoho/client.py --env-file zoho/zoho.env export-sql --sql "select..." --out arquivo.csv --wait
python zoho/client.py --env-file zoho/zoho.env job-status --job-id ID
python zoho/client.py --env-file zoho/zoho.env download-job --job-id ID --out arquivo.csv
```

### Arquivo: `tests/zoho/test_client.py` (≈230 linhas)

**23 testes unitários — todos passando — sem chamadas reais à API.**

Organização:

| Classe | Testes | O que cobre |
|---|---|---|
| `TestZohoConfig` | 5 | `load_env_file`, `from_env` com e sem workspace, URLs customizadas |
| `TestZohoClientAuth` | 3 | `refresh_token`, `exchange_code`, erro sem access_token |
| `TestZohoClientDiscovery` | 4 | `get_orgs`, `get_workspaces`, `get_views` com e sem keyword |
| `TestZohoClientBulk` | 8 | `create_job_view`, `create_job_sql`, `job_status`, `wait_job` (sucesso/falha/timeout), `download_job` |
| `TestZohoClientErros` | 3 | failure response, HTTP 4xx, jobId ausente |

**Infraestrutura de teste:**
- `FakeResponse` — simula `requests.Response` com `status_code`, `content`, `json()`
- `FakeSession` — devolve respostas pré-configuradas em sequência, registra todas as chamadas em `session.calls` para assertivas de URL e headers

### Próximos passos

- [ ] Criar `zoho/catalog.py`
- [ ] Criar testes de catalog
