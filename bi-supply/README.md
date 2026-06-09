# BI de Suprimentos

Sistema de Business Intelligence para análise de compras, fornecedores, produtos, cotações, inflação, contas a pagar, adiantamentos e riscos fiscais.

Os dados vêm do Zoho Analytics (workspace `SUPRIMENTOS`). Um pipeline Python extrai, transforma e gera um dashboard HTML que pode ser aberto no navegador sem internet.

---

## Para quem é este BI

- **Diretoria**: visão executiva de compras, concentração de gastos, alertas
- **Compras e Suprimentos**: cotações, impacto, oportunidades de negociação
- **Fiscal**: risco fiscal por fornecedor, preparação para Reforma Tributária 2027
- **Financeiro**: contas a pagar, adiantamentos, saldo por fornecedor
- **Analistas de BI**: todas as camadas de dados com detalhe operacional

---

## O que o BI mostra

O dashboard tem 15 abas:

| Aba | O que responde |
|---|---|
| **Resumo** | Visão executiva: total comprado, categorias, fornecedores, alertas |
| **Oportunidades** | Onde compramos acima do menor preço cotado |
| **Categorias** | Análise por hierarquia I→D→A com filtros em cascata até CAT5 |
| **Filiais** | Compras por filial, negócio e região |
| **Estoque** | Estoque por filial (workspace APURAÇÃO DE RESULTADOS) |
| **Fornecedor** | Painel 360 por CNPJ: volume, ABC, cotações, CP, risco fiscal |
| **Produtos** | Produtos e preços: PMP, série histórica 12 meses |
| **Cotações** | Contagem de cotações, cobertura ABC/CAT/UF, tabela de preços |
| **Impacto** | IMP: impacto de comprar acima do menor preço cotado |
| **Inflação** | INF: variação do PMP ao longo do tempo por produto/categoria |
| **Fiscal** | Regime tributário, potencial de crédito CBS/IBS 2027 |
| **Financeiro** | Contas a pagar, aging, saldo por fornecedor |
| **Adiantamentos** | Conciliação adiantamento x nota fiscal |
| **Serviços** | Despesas de serviços por UF e categoria |
| **Dados** | Qualidade dos dados: completude, inconsistências, cobertura |

> **IMP ≠ INF**: Impacto de cotação (IMP) é a diferença entre o preço comprado e o menor preço cotado. Inflação (INF) é a variação do Preço Médio Ponderado ao longo do tempo. São conceitos distintos e ficam em abas separadas.

---

## Como os dados chegam aqui

```
Zoho Analytics (workspace SUPRIMENTOS)
          ↓
   nlsql/refresh_elements.py  → nlsql/elements.json  (139 SQL queries → snapshots)
          ↓
   pipeline/generate_indexes.py → posicionamento no grid
          ↓
   pipeline/build.py           → dist/index.html  (dashboard completo)
```

O dashboard HTML final é **auto-contido**: todos os dados ficam embutidos dentro do arquivo. Pode ser aberto offline, enviado por e-mail ou copiado para outra máquina.

> **Nota:** o pipeline antigo (`extract.py` + `transform.py`) foi aposentado em 2026-06-09.
> O Zoho Analytics já calcula Curva ABC, PMP, Inflação e Impacto nas suas próprias views.
> Recovery: `git checkout v-pre-migration -- pipeline/extract.py pipeline/transform.py`

### Aba Relatório (NL-SQL)

A aba **Relatório** permite fazer perguntas em português que são convertidas em SQL e executadas no Zoho:

```
Pergunta em PT-BR → nlsql/server.py → SQL → Zoho API → resultado
```

Para usar a aba Relatório:
```powershell
python nlsql/server.py   # iniciar servidor na porta 5001
# abrir dist/index.html → aba Relatório
```

O servidor usa o prompt em `nlsql/prompts/bi_suprimentos_sql_v3.md` (versão ativa configurável pelo Assistente).

---

## Pré-requisitos

- Python 3.10+
- Credenciais Zoho Analytics em `zoho/zoho.env` (ver `zoho/zoho.env.example`)

Instalar dependências:

```powershell
pip install requests pyyaml
```

---

## Configuração inicial

1. Copiar o template de credenciais:

```powershell
copy zoho\zoho.env.example zoho\zoho.env
```

2. Preencher `zoho/zoho.env` com as credenciais reais (ver `docs/zoho/ESTUDO_API.md` para o passo a passo de criação das chaves).

---

## Como usar

**Atualizar e gerar o dashboard** (3 passos via BAT na área de trabalho):

```
Atualizar BI Suprimentos.lnk  ← duplo clique
```

Ou manualmente:

```powershell
python nlsql/refresh_elements.py    # executa 139 SQLs no Zoho → elements.json
python pipeline/generate_indexes.py # gera posicionamento do grid
python pipeline/build.py            # gera dashboard → dist/index.html
```

Abrir o resultado:

```powershell
start dist\index.html
```

---

## Estrutura de pastas

```
bi-supply/
├── README.md               ← este arquivo
├── DIARIO.md               ← log técnico de todas as alterações
├── run.bat                 ← executa o pipeline completo
├── zoho/
│   ├── zoho.env            ← credenciais (não commitar)
│   ├── zoho.env.example    ← template sem secrets
│   └── client.py           ← cliente Zoho Analytics API
├── pipeline/
│   ├── extract.py          ← Zoho → data/raw/
│   ├── transform.py        ← data/raw/ → data/processed/
│   └── build.py            ← gera dist/index.html
├── nlsql/                  ← módulo de perguntas em linguagem natural (Aba Relatório)
│   ├── server.py           ← Flask API na porta 5001
│   ├── orchestrator.py     ← converte NL → SQL via LLM
│   ├── adapter.py          ← executa SQL no Zoho
│   ├── guard.py            ← valida que SQL é somente leitura
│   ├── history.json        ← histórico de queries (não commitar)
│   ├── chats.json          ← histórico de chats (não commitar)
│   ├── elements.json       ← elementos salvos via "Adicionar ao BI"
│   ├── active_version.txt  ← versão ativa do prompt (v1/v2/v3)
│   └── prompts/
│       ├── bi_suprimentos_sql_v1.md  ← prompt original
│       ├── bi_suprimentos_sql_v2.md  ← prompt melhorado (JOINs, CTEs)
│       └── bi_suprimentos_sql_v3.md  ← prompt completo (dados reais, 39KB)
├── dashboard/
│   ├── tabs/               ← um .yml por aba (15 arquivos)
│   ├── templates/          ← templates HTML por tipo de elemento
│   └── static/             ← CSS e JS compartilhados
├── data/
│   ├── raw/                ← CSVs brutos do Zoho (não commitar)
│   └── processed/          ← métricas prontas (não commitar)
├── design/
│   ├── BI Design System.html   ← fonte da verdade visual (não modificar)
│   └── BI Suprimentos v4.html  ← mock de referência (não modificar)
├── docs/
│   ├── projeto/            ← briefing, objetivos, arquitetura
│   ├── dados/              ← domínios, dicionário, perfil das fontes
│   ├── design/             ← mapa de abas, critérios, cobertura Zoho
│   └── zoho/               ← estudo da API, inventário de workspaces
├── tests/
│   ├── zoho/               ← testes do client.py
│   ├── pipeline/           ← testes de transformações e métricas
│   ├── nlsql/              ← testes do módulo NL-SQL
│   └── dashboard/          ← testes de geração de HTML
└── dist/
    └── index.html          ← dashboard gerado (não commitar)
```

---

## Documentação

| Documento | O que contém |
|---|---|
| [docs/projeto/ARQUITETURA.md](docs/projeto/ARQUITETURA.md) | Arquitetura técnica do sistema |
| [docs/projeto/BRIEFING.md](docs/projeto/BRIEFING.md) | Contexto do produto e público-alvo |
| [docs/dados/DOMINIOS_NEGOCIO.md](docs/dados/DOMINIOS_NEGOCIO.md) | Dicionário de domínios e campos |
| [docs/dados/CATEGORIAS.md](docs/dados/CATEGORIAS.md) | Hierarquia de categorias I→D→A |
| [docs/dados/ESTUDO_DOMINIOS.md](docs/dados/ESTUDO_DOMINIOS.md) | Análise das fontes Zoho por domínio |
| [docs/zoho/ESTUDO_API.md](docs/zoho/ESTUDO_API.md) | Passo a passo de acesso à API Zoho |
| [docs/zoho/INVENTARIO_WORKSPACES.md](docs/zoho/INVENTARIO_WORKSPACES.md) | Todos os workspaces e views acessíveis |
| [docs/design/MAPA_ABAS.md](docs/design/MAPA_ABAS.md) | Mapa das 15 abas e seus componentes |
| [docs/design/ESPECIFICACAO_ABAS.md](docs/design/ESPECIFICACAO_ABAS.md) | Especificação detalhada de cada aba |
| [docs/design/COBERTURA_ABAS.md](docs/design/COBERTURA_ABAS.md) | Auditoria do mock contra Zoho real |
| [docs/design/ELEMENTOS_BI.md](docs/design/ELEMENTOS_BI.md) | Guia dos 11 tipos de elemento (KPI, GL, HL, etc.) |
| [docs/dados/ANALISE_DADOS_REAIS.md](docs/dados/ANALISE_DADOS_REAIS.md) | Perfil das 18 fontes Zoho com campos e filtros reais |
| [docs/zoho/MAPA_PAINEIS.md](docs/zoho/MAPA_PAINEIS.md) | 72 pivots + 31 analysis views + Design System |
