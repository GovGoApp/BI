# Mapa de Painéis Zoho Analytics — Workspace SUPRIMENTOS

Inventário completo dos painéis existentes no Zoho. Base para definição de elementos do BI e enriquecimento do prompt NL-SQL.

**Workspace:** SUPRIMENTOS | **Total views:** 165 | **Gerado em:** 2026-06-03

---

## 1. Dashboards (8)

| Nome | Foco | Uso no BI |
|---|---|---|
| PAINEL RESUMO | Overview executivo | Aba Resumo |
| PAINEL FORNECEDOR | 360° do fornecedor | Aba Fornecedor |
| PAINEL COTAÇÃO | Gestão de cotações | Aba Cotações |
| PAINEL PRODUTOS | Catálogo e impacto | Aba Produtos |
| PAINEL INFLAÇÃO | Variação de preços 12m | Aba Inflação |
| PAINEL CP | Contas a pagar | Aba Financeiro |
| PAINEL ADIANTAMENTO | Rastreamento de ADs | Aba Adiantamentos |
| PAINEL SERVIÇOS | Serviços terceirizados | Aba Serviços |

---

## 2. Pivots (72) — por Domínio

### A. Fornecedor (12)
- FORNECEDORES TOTAL
- FORNECEDORES TOTAL - POR ANO
- FORNECEDORES por CAT
- FORNECEDORES por CAT 2
- FORNECEDORES por UF e CAT
- FORNECEDORES_25_26
- MIN COTAÇÃO por FORN
- MIN COTAÇÃO por FORN - COTAÇÕES <= 3
- AD por FORNECEDOR
- AD por FORNECEDOR e UF
- FORNECEDORES IMPACTO sobre COTAÇÃO
- FORNECEDORES INFLAÇÃO

### B. Cotação (6)
- COTAÇÕES DE PREÇOS - TODOS (CONSULTA PREÇO COTAÇÃO)
- COTAÇÕES por PRODUTO
- NUMERO de COTAÇÕES por PRODUTO
- CONTAGEM de COTAÇÕES
- CONTAGEM de COTAÇÕES por ABC
- CONTAGEM de COTAÇÕES por UF

### C. Impacto (6)
- IMPACTO de COTAÇÃO NACIONAL
- IMPACTO de COTAÇÃO por UF
- IMP_COT_ID
- IMP_ID
- IMP_PROD / IMP_PROD_2
- FORNECEDORES e PRODUTOS - IMPACTO

### D. Inflação (10)
- INFLAÇÃO NACIONAL
- INFLAÇÃO NACIONAL por CATEGORIA
- INFLAÇÃO por PRODUTO e CAT
- INFLAÇÃO por RESUMO de UF
- INFLAÇÃO por UF
- INFLAÇÃO por UF e por CAT
- INFLAÇÃO total
- INF_ID / INF_ID_PMP
- INF_PROD_PMP
- TOP INFLAÇÃO / TOP DEFL

### E. PMP — Preço Médio Ponderado (6)
- PMP_FORN
- PMP_ID_INF_12_x
- PMP_PROD_ABC
- PMP_PROD_ID
- PMP_PROD_INF_12_x
- PMP_UF

### F. Contas a Pagar (4)
- CP_SALDO_26
- CP_STATUS
- CP_STATUS-TOTAL
- RELATÓRIO CONTAS A VENCER/VENCIDAS

### G. Adiantamentos (4)
- ADIANTAMENTO
- ADIANTAMENTO por CAT
- ADIANTAMENTO_CONC
- ADIANTAMENTO_CONC-Copiar

### H. Produtos (6)
- PRODUTOS por CAT
- PRODUTOS por ID
- PRODUTOS por ID - MIN COT
- PRODUTOS por ID e FORN
- PRODUTOS por PROD
- PRODUTOS por UF

### I. Categoria (2)
- CAT_UF
- RESUMO CATEGORIAS

### J. Resultado / Resumo (6)
- RESUMO - FORN
- RESUMO NEGOCIOS
- RESUMO_FILIAL
- Resumo CAT
- SUP por FILIAL
- SUP_x_CMV

### K. Serviços / Despesas (4)
- DESPESAS
- Despesas_2v2v2
- SERVIÇOS por MES
- RELATÓRIO DE COTAÇÕES

### L. Diversos (6)
- CONCILIAÇÃO_UF
- PADRONIZAÇÃO PRODUTOS
- TOP DEFLAÇÃO
- FISCAL (regime tributário)
- QUALIDADE DADOS

---

## 3. Analysis Views (31) — por Tipo

### KPIs e Resumos (6)
- TOTAL POR CAT — spend por categoria macro
- TOTAL por PROD — spend por produto
- IMPACTO — impacto total de cotação
- IMPACTO por COTAÇÃO — por produto/fornecedor
- CAT por UF — categoria × UF
- CAT por MES — série temporal por categoria

### Análises Temporais (3)
- Adiantamento por Mês
- INFLAÇÃO por MES por CAT - %
- INFLAÇÃO por MES por CAT - R$

### Análises Geográficas (5)
- AD por UF
- Adiantamento por UF
- CAT por UF
- DESPESAS por UF
- DESPESAS por UF e CAT

### Preço e Produto (5)
- PMP por CAT
- PMP por PROD
- PMP por UF
- INFLAÇÃO POR CAT
- INFLAÇÃO por MES por CAT

### Cotações (3)
- CONTAGEM DE COTAÇÕES por CAT
- CONTAGEM de COTAÇÕES
- CONTAGEM de COTAÇÕES por ABC

### Financeiro e Geo (5)
- CP_SALDO_DIVIDA_2026
- SUP por GEO - N e NE
- SUP por GEO - S e SE
- Adiantamento %
- CONCILIAÇÃO_AD

### Serviços (2)
- SERVIÇOS
- AD por CAT / AD por MES e CAT

---

## 4. KPIs Identificados nos Painéis (para implementar no BI)

### Existentes nos painéis Zoho — prontos para implementar

| KPI | Painel Zoho | Aba destino |
|---|---|---|
| Total spend nacional | RESUMO | Resumo |
| Spend por empresa (RC/ME/SU) | RESUMO NEGOCIOS | Resumo |
| Fornecedores ativos | FORNECEDORES TOTAL | Resumo / Fornecedor |
| Fornecedores curva AAA+AA | FORNECEDORES TOTAL | Fornecedor |
| Cotações realizadas no período | CONTAGEM de COTAÇÕES | Cotações |
| % produtos com ≥3 cotações | NUMERO de COTAÇÕES | Cotações |
| Impacto total de cotação R$ | IMPACTO NACIONAL | Impacto |
| Impacto % sobre spend | IMPACTO NACIONAL | Impacto |
| Inflação média % 12m | INFLAÇÃO NACIONAL | Inflação |
| Produtos com inflação > 10% | TOP INFLAÇÃO | Inflação |
| CP em aberto total R$ | CP_STATUS | Financeiro |
| CP vencido R$ | CP_STATUS | Financeiro |
| CP a vencer 30 dias | CP_SALDO_26 | Financeiro |
| AD pendentes R$ | ADIANTAMENTO | Adiantamentos |
| AD conciliados % | ADIANTAMENTO_CONC | Adiantamentos |
| Spend serviços R$ | SERVIÇOS por MES | Serviços |

### KPIs adicionais identificados (não nos painéis Zoho atuais)

| KPI | Definição | Fórmula |
|---|---|---|
| Taxa cobertura cotação | % produtos com ≥3 cotações | (Prod ≥3 cot / Total prod) × 100 |
| Spread de cotação | Variação % entre min e max cota | ((Max - Min) / Min) × 100 |
| Aceitação menor preço | % compras no menor preço | (Compras menor / Total cotadas) × 100 |
| DMP (Dias Médio Pago) | Dias emissão → pagamento | Σ(DtPgto - DtNF) / Qtde pagas |
| Taxa inadimplência | % saldo vencido sobre total | (Vencido / Total aberto) × 100 |
| Economia não realizada | Impacto deixado na mesa | Σ(Preço pago - Menor cotado) × Qtde |
| Concentração de gasto | Índice HHI de fornecedores | Σ((Val forn / Val total)²) × 10000 |
| Rotação de fornecedores | Novos fornecedores % | (Novos / Total) × 100 |
| Score cadastro fornecedor | Completude do cadastro | (Campos preenchidos / Obrigatórios) × 100 |
| Potencial CBS/IBS 2027 | Crédito estimado reforma tributária | Σ(Spend × Alíquota regime) |

---

## 5. Design System — Tokens e Componentes

### Cores (CSS Variables)

```css
/* Neutros */
--bg: #f3f6fa         /* Fundo página */
--card: #ffffff       /* Superfície principal */
--head: #e9eff7       /* Cabeçalho de tabela */
--line: #d8e0ea       /* Bordas */
--muted: #64748b      /* Texto secundário */
--ink: #0f172a        /* Texto principal */

/* Status — cada cor tem variante soft */
--blue: #2563eb       --blue-soft: #eff6ff
--green: #16a34a      --green-soft: #ecfdf5
--yellow: #a16207     --yellow-soft: #fef9c3
--red: #b91c1c        --red-soft: #fee2e2
```

### Curva ABC — Cores por nível
```
AAA → green  (#16a34a / #ecfdf5)   ← top 50% gasto
AA  → green-soft
A   → blue   (#2563eb / #eff6ff)   ← 65-80%
B   → yellow (#a16207 / #fef9c3)   ← 80-90%
BB  → yellow-soft
C   → red    (#b91c1c / #fee2e2)   ← 95-100%
CC/CCC → red-soft
```

### Empresas — Badges
```
RC  → .badge.rc → preto       (Ideal — empresa principal)
ME  → .badge.me → azul
SU  → .badge.su → ciano/turquesa
```

### KPI — Estados visuais
```
.kpi        → neutro (sem tarja)
.kpi.ok     → tarja verde + fundo verde-soft (bom resultado)
.kpi.warn   → tarja amarela (atenção)
.kpi.alert  → tarja vermelha (crítico)
```

### Pills e Chips disponíveis
```css
.pill.b    /* Azul */
.pill.g    /* Verde */
.pill.y    /* Amarelo */
.pill.r    /* Vermelho */
.pill.k    /* Preto */
.pill.ghost /* Contorno sem fundo */

.curva.A .curva.AA .curva.AAA  /* Verde */
.curva.B .curva.BB             /* Amarelo */
.curva.C .curva.CC .curva.CCC  /* Vermelho */

.badge.rc .badge.me .badge.su  /* Empresas */
```

### Formatação numérica (FMT)
```javascript
FMT.brl(n)   // "R$ 1.234.567"      inteiros monetários
FMT.brl2(n)  // "R$ 1.234,56"       com 2 decimais
FMT.mi(n)    // "R$ 12,4 mi"        acima de 1M
FMT.mil(n)   // "1.234 mil"         acima de 1K
FMT.pct(n)   // "+3,5%"             percentual com sinal
FMT.num(n)   // "1.234.567"         inteiro formatado
FMT.dec(n)   // "1.234,56"          decimal
FMT.auto(n)  // formato automático por magnitude
```

---

## 6. Gap Analysis — Mock v4 vs Implementação Dev

### Abas completamente ausentes
- **Estoque** — heatmap de dias de estoque por produto × mês (requer workspace Apuração de Resultados)
- **Fiscal** — análise de regime tributário e crédito CBS/IBS 2027

### Elementos visuais não implementados

| Elemento | Onde aparece no mock | Status dev |
|---|---|---|
| Sparkline PMP 12 meses | Produtos, Inflação | Ausente |
| Heatmap matriz cotações | Cotações (produto × mês) | Ausente |
| Timeline fluxo CP | Financeiro | Ausente |
| Drilldown Filial → Cat → Forn | Filiais | Ausente |
| Cascata 5 níveis dinâmica | Categorias | Parcial |
| Alert list estruturada | Fiscal, Dados | Ausente |
| Tag bar quick filter | Dados (qualidade) | Ausente |
| Sub-abas fornecedor 360 | Fornecedor | Parcial |
| Delta KPI (▲▼ vs período ant.) | Todos os KPIs | Parcial |
| Multi-série em gráficos de linha | Resumo, Inflação | Ausente |
| Cores por categoria nos gráficos | Todos os gráficos | Ausente |
| Pills ABC nas tabelas | Produtos, Fornecedor | Ausente |
| Badges empresa (RC/ME/SU) | Filiais, Resumo | Ausente |

### Detalhes de KPI não implementados no dev
- **Delta:** valor comparativo vs período anterior (▲ +12% vs mês ant.)
- **Estado visual:** cor de fundo e tarja por threshold (ok/warn/alert)
- **Subtítulo contextual:** ex. "excluindo D5 Serviços", "curva A", "últimos 12m"
- **Valor secundário:** ex. "682 fornecedores | 3.518 ativos"
