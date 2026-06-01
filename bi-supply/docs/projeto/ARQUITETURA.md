# Arquitetura Técnica — BI de Suprimentos

## Visão geral

O sistema tem três camadas separadas com responsabilidade única cada:

```
Zoho Analytics API (workspace SUPRIMENTOS)
          │
          ▼ pipeline/extract.py
    data/raw/                  ← CSVs brutos, um arquivo por fonte Zoho
          │
          ▼ pipeline/transform.py
    data/processed/            ← métricas calculadas, prontas para o dashboard
          │
          ▼ pipeline/build.py
    dist/index.html            ← dashboard HTML auto-contido
```

Cada etapa pode rodar independentemente. O dashboard funciona offline — os dados ficam embutidos como JSON dentro do HTML.

---

## Camada 1 — Extração (pipeline/extract.py)

**Responsabilidade:** baixar dados do Zoho para `data/raw/`.

- Lê `zoho/zoho.env` para autenticação
- Renova o `access_token` automaticamente via `refresh_token`
- Para cada fonte definida em `pipeline/sources.yml`:
  - Executa a query SQL correspondente via Zoho Bulk API
  - Aguarda o job de exportação assíncrono
  - Salva o CSV em `data/raw/{source_id}.csv`
- Grava um manifesto `data/raw/manifest.json` com timestamp e status de cada fonte

**Nunca transforma dados.** Salva exatamente o que veio do Zoho.

---

## Camada 2 — Transformação (pipeline/transform.py)

**Responsabilidade:** calcular métricas e preparar tabelas para o dashboard.

- Lê os CSVs de `data/raw/`
- Executa transformações por domínio:
  - Normaliza chaves (fornecedor, produto, filial, tempo, categoria)
  - Calcula métricas derivadas (IMP_COT, INF, curva ABC, etc.)
  - Cria tabelas consolidadas por aba
- Salva em `data/processed/{dataset_id}.csv`

**Nunca acessa o Zoho.** Trabalha apenas com os arquivos de `data/raw/`.

---

## Camada 3 — Build (pipeline/build.py)

**Responsabilidade:** gerar o dashboard HTML final.

- Lê os dados de `data/processed/`
- Para cada aba definida em `dashboard/tabs/`:
  - Lê o arquivo `.yml` da aba
  - Renderiza os elementos com os templates de `dashboard/templates/`
  - Aplica os estilos de `dashboard/static/`
- Embute todos os dados como JSON dentro do HTML
- Grava `dist/index.html`

**Nunca calcula métricas.** Apenas renderiza dados já prontos.

---

## Módulo NL-SQL (nlsql/)

Módulo auxiliar que permite fazer perguntas em linguagem natural que se transformam em SQL executado no Zoho.

**Uso:** alimentar o BI com perguntas ad-hoc e gerar novos elementos.

```
Pergunta em PT → search_schema → describe_tables → SQL → run_readonly_query → tabela/gráfico
```

Componentes:

| Arquivo | Responsabilidade |
|---|---|
| `catalog.py` | Catálogo das 53+ fontes do workspace SUPRIMENTOS |
| `adapter.py` | Executa SQL no Zoho via client.py |
| `guard.py` | Valida que o SQL é apenas `SELECT` ou `WITH ... SELECT` |
| `orchestrator.py` | Loop de tool calls com o LLM (Claude API) |
| `renderer.py` | Formata o resultado como tabela, KPI ou série para o BI |

O modelo de linguagem **nunca recebe credenciais** e **nunca abre conexões diretas**. Toda execução passa pelo `guard.py` e `adapter.py`.

---

## Dashboard — configuração por aba

Cada aba tem um arquivo `dashboard/tabs/{aba}.yml`:

```yaml
id: cotacoes
title: Cotações
source: data/processed/cotacoes.csv

filters:
  - field: UF
  - field: CAT2
  - field: MESANO

elements:
  - id: kpi_produtos_cotados
    type: kpi
    metric: count_distinct_id
    label: Produtos cotados

  - id: chart_cobertura_abc
    type: chart
    metric: qtd_cot_por_curva
    label: Cobertura por ABC
    zoho_origin: CONTAGEM de COTACOES por ABC

  - id: table_relatorio_cotacoes
    type: table
    source: relatorio_cotacoes
    label: Relatório de Cotações
    zoho_origin: RELATORIO DE COTACOES
```

**Regra:** o YAML define *o quê* mostrar. O Design System define *como* parece. O template define *como* montar o HTML. Os três nunca se misturam.

---

## Design System — fonte da verdade visual

O arquivo `design/BI Design System.html` define:

- Tokens de cor (`--bg`, `--ink`, `--blue`, `--green`, `--red`, etc.)
- Tipografia: Segoe UI, 13px base
- Componentes: KPI card, tabela, pill/badge, barra, spark
- Grid: 8 colunas para KPIs, tabelas compactas

**Nenhum CSS novo é inventado.** Os templates em `dashboard/templates/` usam apenas as classes do Design System.

---

## Zoho Client (zoho/client.py)

Cliente para a Zoho Analytics API v2.

Funcionalidades:
- `refresh_access_token()` — renova o token via refresh_token
- `get_orgs()`, `get_workspaces()`, `get_views()` — descoberta
- `export_view_data()` — exportação síncrona (views pequenas)
- `create_export_job()` — cria job de exportação assíncrona
- `wait_for_export_job()` — aguarda o job terminar
- `download_export_job()` — baixa o resultado

Lê credenciais de `zoho/zoho.env` via `--env-file` ou variáveis de ambiente.

---

## Fontes de dados por aba

| Aba | Fontes Zoho principais |
|---|---|
| Resumo | `NFE`, `FAT_SUP`, `CURVA FORN`, `INFLAÇÃO` |
| Oportunidades | `NFE`, `COT`, `COT_MIN_FORN`, `NUM_COT` |
| Categorias | `NFE`, `CAT_UF` |
| Filiais | `NFE`, `FILIAIS_SUPPLY`, `RESUMO_FILIAL` |
| Estoque | workspace APURAÇÃO DE RESULTADOS |
| Fornecedor 360 | `NFE`, `CURVA FORN - TODAS`, `CP`, `AD_v3` |
| Produtos | `NFE`, `PMP_ID_INF_12`, `PMP_PROD_INF_12`, `COT_MIN_FORN` |
| Cotações | `COT`, `NUM_COT`, `COT_MIN_FORN`, views de contagem/relatório |
| Impacto | `NFE` (IMP_COT), `COT_MIN_FORN`, views de impacto |
| Inflação | `INFLAÇÃO`, `PMP_*`, views de inflação |
| Fiscal | Base de fornecedores do projeto (não Zoho) |
| Financeiro | `CP`, `CP_MOV`, `CP_SEMANA`, `CP_SALDO_*` |
| Adiantamentos | `AD_v3`, `ADIANTAMENTO_NFE`, `NF ADT - *` |
| Serviços | `DESPESAS`, views de serviços |
| Dados | Todos (monitor de qualidade) |

---

## Testes

```
tests/
├── zoho/         ← testa zoho/client.py com HTTP mockado
├── pipeline/     ← testa transformações e cálculo de métricas
├── nlsql/        ← testa catalog, guard, SQL validation
└── dashboard/    ← testa que YAML + dados produzem HTML válido
```

---

## Regras de desenvolvimento

1. Cada script tem uma única responsabilidade.
2. Nenhum script acessa o Zoho exceto `extract.py` e `zoho/client.py`.
3. Nenhum CSS é inventado fora do Design System.
4. Todo componente que vem do Zoho deve ter `zoho_origin` registrado no YAML.
5. IMP e INF nunca ficam na mesma aba sem identificação clara.
6. Dados brutos nunca ficam em `dist/` — só dados processados embutidos.
