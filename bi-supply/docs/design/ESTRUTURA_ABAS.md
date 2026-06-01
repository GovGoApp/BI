# Estrutura das Abas — Elementos, Fontes e Layout

Documento de referência para implementação do dashboard.
Gerado combinando: **C** (painéis Zoho existentes) + **C2** (mock v4.html) + **A** (dados reais) + **B** (benchmarks).

Para cada aba: elementos visuais com tipo, fonte de dados e observações.

---

## Convenções

| Tipo | Símbolo | Descrição |
|---|---|---|
| KPI card | `[K]` | Card com valor principal + delta |
| Tabela expandível | `[TE]` | Linhas com detalhe ao expandir |
| Tabela simples | `[T]` | Tabela estática com ordenação |
| Gráfico de barras | `[GB]` | Barras verticais ou horizontais |
| Gráfico de linhas | `[GL]` | Séries temporais |
| Gráfico empilhado | `[GE]` | Barras empilhadas |
| Hbar list | `[HL]` | Lista com barra proporcional inline |
| Matrix/Heatmap | `[MX]` | Grade com gradiente de cor |
| Spark | `[SP]` | Micro-gráfico inline em tabela |
| Alert list | `[AL]` | Lista de alertas com prioridade |
| Tagbar | `[TB]` | Filtros rápidos por tag |
| Funil | `[FU]` | Estágios progressivos |

Fonte Zoho: `[PV]` Pivot · `[AV]` AnalysisView · `[QT]` QueryTable · `[TB]` Table

---

## ABA: RESUMO

### KPIs (8 cards)

| # | [K] Label | Fonte | Origem Zoho |
|---|---|---|---|
| 1 | Total Comprado (operacional) | NFE sum(TOTAL) excl. D5-financeiro | `[QT] NFE` |
| 2 | Crescimento YoY | NFE comparativo ano anterior | `[QT] NFE` |
| 3 | Fornecedores Ativos | count distinct CDFORNECED | `[QT] CURVA ABC FORN - TOTAL` |
| 4 | % Compras com Cotação | PRE_MIN_COT>0 / total linhas | `[QT] NFE` |
| 5 | Oportunidade IMP_COT | sum(IMP_COT) onde >0 | `[QT] NFE` |
| 6 | CP em Aberto (operacional) | sum VRATUAPAG status=ABERTO filtrado | `[TB] CP` |
| 7 | AD Pendente | sum VALOR_FINAL status≠CONCILIADO | `[QT] AD_v3` |
| 8 | Risco Fiscal 2027 | count fornec. indeterminados × alto valor | base cadastral |

### Gráficos e tabelas

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Evolução de compras mensal | `[GL]` 12 meses | NFE por MESANO | `[QT] NFE` |
| 2 | Compras por tipo de negócio | `[HL]` | NFE por FI.NEGOCIO | `[QT] NFE` |
| 3 | Spend × CMV | `[HL]` | FAT_SUP | `[PV] SUP_x_CMV` |
| 4 | Top categorias (CAT2) | `[T]` Categoria · Valor · % · Inflação · Impacto | NFE + inflação | `[PV] RESUMO CATEGORIAS` |
| 5 | Top fornecedores | `[T]` Forn · Curva · Valor · CP · Alerta | NFE + CP | `[PV] RESUMO - FORN` |
| 6 | SUP por geo N/NE | `[HL]` UFs nordeste | NFE por UF | `[AV] SUP por GEO - N e NE` |
| 7 | SUP por geo S/SE | `[HL]` UFs sul/sudeste | NFE por UF | `[AV] SUP por GEO - S e SE` |
| 8 | Por negócio | `[T]` Negócio · Valor · CP · Impacto | NFE + CP | `[PV] RESUMO NEGOCIOS` |
| 9 | Por filial (top 8) | `[T]` Filial · Negócio · UF · Valor · CP | NFE + filiais | `[PV] RESUMO_FILIAL` |
| 10 | Categoria × UF | `[MX]` heat | NFE | `[AV] CAT por UF` |
| 11 | Alertas executivos | `[AL]` prioridade alta/média | regras | — |

---

## ABA: OPORTUNIDADES

### KPIs (6 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Oportunidade total (IMP_COT>0) | NFE |
| 2 | IDs AAA/AA/A sem cotação | NUM_COT cruzado com CURVA ID |
| 3 | IDs comprados acima do mínimo | NFE IMP_COT>0 |
| 4 | % linhas compradas acima do mínimo | NFE |
| 5 | Itens com ≤ 1 cotação (risco) | NUM_COT |
| 6 | Fornecedores que nunca são o mais barato | COT_MIN_FORN |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Matriz prioridade (Impacto × Esforço) | `[MX]` 3×3 | NFE + NUM_COT | — |
| 2 | Oportunidade por tipo | `[HL]` | NFE categorizado | — |
| 3 | Oportunidade por CAT2 | `[GB]` | NFE | — |
| 4 | Oportunidade por UF | `[HL]` | NFE | `[PV] IMPACTO de COTACAO por UF` |
| 5 | **Tabela principal de oportunidades** | `[TE]` | NFE + NUM_COT | `[PV] IMP_COT_ID` |

**Colunas da tabela principal:**
Tipo · Prioridade · ID · Produto · Fornecedor atual · Menor cotação disponível · Impacto R$ · Evidência · Ação sugerida · Status

**Tags de tipo de oportunidade (da análise de dados reais):**
- Acima da menor cotação disponível
- Produto AAA sem cotação alguma (16 casos)
- Produto AAA/AA/A com monopólio de cotação (97 casos)
- Compra de fornecedor CCC onde existe AAA disponível

---

## ABA: CATEGORIAS

### KPIs (6 cards) — contextuais ao filtro ativo

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Total comprado (seleção) | NFE filtrado |
| 2 | Inflação 12m (seleção) | PMP_ID_INF_12 |
| 3 | Produtos/IDs únicos | NFE |
| 4 | Fornecedores na categoria | NFE |
| 5 | Impacto R$ | NFE |
| 6 | % com cotação | NUM_COT |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | **Drilldown cascata CAT1→CAT5** | `[TB]` + cascata | NFE | — |
| 2 | CAT2 por mês | `[GL]` 4 séries | NFE | `[AV] CAT por MES` |
| 3 | CAT2 por UF | `[MX]` heat | NFE | `[AV] CAT por UF` |
| 4 | Top fornecedores da categoria | `[T]` | NFE | `[PV] FORNECEDORES por CAT` |
| 5 | Top produtos da categoria | `[T]` ID · PMP · Inflação · Impacto | NFE + PMP | `[PV] PRODUTOS por CAT` |
| 6 | Alertas da categoria | `[AL]` | regras | — |

**Filtros em cascata obrigatórios:** CAT1 (I→D→A) → CAT2 → CAT3 → CAT4 → CAT5

---

## ABA: FILIAIS

### KPIs (6 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Total comprado | NFE |
| 2 | Compra média por filial | NFE + FILIAIS |
| 3 | Maior filial | NFE |
| 4 | Maior tipo de negócio | NFE |
| 5 | % Compras com cotação (eficiência) | NFE |
| 6 | Impacto por filial | NFE |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Ranking de filiais | `[HL]` | NFE + FILIAIS | `[PV] SUP por FILIAL` |
| 2 | Filial × Negócio | `[MX]` heat | NFE | `[PV] RESUMO NEGOCIOS` |
| 3 | Geo N/NE | `[HL]` | NFE | `[AV] SUP por GEO - N e NE` |
| 4 | Geo S/SE | `[HL]` | NFE | `[AV] SUP por GEO - S e SE` |
| 5 | **Tabela consolidada de filiais** | `[T]` | NFE + FILIAIS + CP | `[PV] RESUMO_FILIAL` |
| 6 | Filial × Categoria | `[T]` | NFE | `[PV] FORNECEDORES por UF e CAT` |
| 7 | Filial × Mês | `[GL]` top 3 filiais | NFE | — |

**Colunas da tabela consolidada:**
Filial · Negócio · UF · Empresa · Total · % do spend · CMV · Compra/CMV · % cotação · IMP_COT · Status

---

## ABA: ESTOQUE

*Dados do workspace APURAÇÃO DE RESULTADOS (workspace ID `2130260000006068011`)*

### KPIs (8 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Estoque final (R$) | APURAÇÃO DE RESULTADOS |
| 2 | Entradas 12m | — |
| 3 | Saídas/CMV | — |
| 4 | Consumo/dia | — |
| 5 | Dias de estoque médio | EFIN / (CMV / 365) |
| 6 | Filiais com estoque < 15 dias | — |
| 7 | Filiais com estoque > 60 dias | — |
| 8 | Estoque negativo | — |

### Elementos

| # | Elemento | Tipo | Fonte |
|---|---|---|---|
| 1 | Dias de estoque por filial | `[HL]` colorido (ruptura/atenção/ok/excesso) | APURAÇÃO |
| 2 | Entradas × Saídas × Ajustes | `[GB]` agrupado | APURAÇÃO |
| 3 | Movimentação por filial | `[T]` | APURAÇÃO |
| 4 | Compras × Consumo por filial | `[T]` | APURAÇÃO + NFE |
| 5 | Alertas de estoque | `[AL]` | regras |

**Nota:** esta aba depende do workspace APURAÇÃO DE RESULTADOS que ainda não foi extraído. Implementar após integrar essa fonte.

---

## ABA: FORNECEDOR 360

### KPIs (6 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Fornecedores ativos | CURVA ABC FORN |
| 2 | Spend em curva AAA+AA+A | CURVA ABC FORN |
| 3 | Sem CNPJ na base | base cadastral |
| 4 | Com CP vencido + curva alta | CP + CURVA |
| 5 | Com AD pendente | AD_v3 |
| 6 | Alto valor × regime indeterminado | base cadastral |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | `[TB]` Filtros: curva · regime · alerta | tagbar | — | — |
| 2 | **Tabela expandível de fornecedores** | `[TE]` | NFE + CURVA + CP | `[PV] FORNECEDORES TOTAL` |
| 3 | ↳ Identidade e cadastro | detail card | base cadastral | — |
| 4 | ↳ Compras 12m | detail card | NFE | — |
| 5 | ↳ Impacto de cotação | detail card | NFE IMP_COT | `[PV] FORNECEDORES IMPACTO sobre COTACAO` |
| 6 | ↳ Inflação por fornecedor | detail card | INFLAÇÃO + PMP | `[PV] FORNECEDORES INFLACAO` |
| 7 | ↳ PMP por fornecedor | detail card | — | `[PV] PMP_FORN` |
| 8 | ↳ Fiscal 2027 | detail card | base cadastral | — |
| 9 | ↳ CP e adiantamentos | detail card | CP + AD_v3 | `[PV] CP_STATUS` |
| 10 | ↳ Produtos comprados | `[T]` | NFE | `[PV] PRODUTOS por ID e FORN` |

**Colunas da tabela principal:**
Fornecedor · CNPJ · Empresas · Curva · Valor 12m · Regime · Crédito 2027 · Alertas

---

## ABA: PRODUTOS

### KPIs (6 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Produtos analisados (IDs) | CURVA ID |
| 2 | IDs curva AAA+AA (críticos) | CURVA ID |
| 3 | Variação PMP > 10% | PMP_ID_INF_12 |
| 4 | IDs sem cotação 12m | NUM_COT |
| 5 | PMP médio da cesta | PMP_ID_INF_12 |
| 6 | Inflação média da cesta | PMP_ID_INF_12 |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | `[TB]` Filtros: curva · inflação · cotação | tagbar | — | — |
| 2 | **Tabela expandível de produtos** | `[TE]` + spark PMP | NFE + PMP + COT | `[PV] PRODUTOS por ID` |
| 3 | ↳ Série PMP 12 meses | `[SP]` + KV | PMP_ID_INF_12 | `[PV] PMP_ID_INF_12_x` |
| 4 | ↳ Cotações 90d | detail card | COT + COT_MIN_FORN | `[PV] PRODUTOS por ID - MIN COT` |
| 5 | ↳ Compras por UF/filial | detail mini-bars | NFE | — |
| 6 | PMP por CAT | `[T]` + spark | PMP | `[AV] PMP por CAT` |
| 7 | Top inflação | `[HL]` sorted | PMP_ID_INF_12 | `[PV] PMP_PROD_ABC` |
| 8 | Top deflação | `[HL]` sorted verde | PMP_ID_INF_12 | — |

**Colunas da tabela principal:**
Produto · ID · Categoria · Curva ID · Curva Prod. · PMP atual · Var. 12m · Série PMP `[SP]` · Impacto R$

---

## ABA: COTAÇÕES

### KPIs (8 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Produtos cotados | NUM_COT |
| 2 | % cobertura de cotação | NUM_COT / total IDs |
| 3 | Média cotações por produto | NUM_COT |
| 4 | Com 0 cotação | NUM_COT |
| 5 | Com 1 cotação (sem concorrência) | NUM_COT |
| 6 | Com ≤ 3 cotações | NUM_COT |
| 7 | Potencial IMP_COT | NFE |
| 8 | % comprado no menor preço | NFE |

### Elementos (10 blocos obrigatórios)

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Distribuição QTD_COT por mês | `[GE]` empilhado (0/1/2/3/4/5+) | NUM_COT | `[AV] CONTAGEM de COTACOES` |
| 2 | Cobertura por curva ABC do ID | `[MX]` curva × faixas cot. | NUM_COT | `[AV] CONTAGEM de COTACOES por ABC` |
| 3 | Cobertura por categoria × mês | `[GL]` 4 séries | NUM_COT | `[AV] CONTAGEM DE COTACOES por CAT` |
| 4 | Cobertura por UF | `[T]` | NUM_COT | `[AV] CONTAGEM de COTACOES por UF` |
| 5 | Consulta de preços cotados | `[T]` scroll horiz | COT | `[PV] COTACOES DE PRECOS - TODOS` |
| 6 | Cotações por produto | `[T]` | COT + NUM_COT | `[PV] COTACOES por PRODUTO` |
| 7 | Matriz produto × mês (# e MIN) | `[T]` scroll horiz | NUM_COT | `[PV] NUMERO de COTACOES por PRODUTO` |
| 8 | MIN cotação por fornecedor | `[T]` scroll horiz | COT_MIN_FORN | `[PV] MIN COTACAO por FORN` |
| 9 | MIN cotação ≤ 3 concorrentes | `[T]` | COT_MIN_FORN | `[PV] MIN COTACAO por FORN - COTACOES <= 3` |
| 10 | Relatório completo de cotações | `[T]` scroll horiz | COT | `[PV] RELATORIO DE COTACOES` |

---

## ABA: IMPACTO

*IMP = impacto de cotação: diferença entre preço pago e menor preço cotado*

### KPIs (6 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Impacto total (IMP_COT > 0) | NFE |
| 2 | Impacto nacional acumulado | NFE |
| 3 | UF com maior IMP/Spend | NFE |
| 4 | % linhas compradas acima do mínimo | NFE |
| 5 | IDs com impacto positivo | NFE |
| 6 | Top produto por IMP_COT | NFE |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Impacto nacional por mês | `[GB]` vermelho | NFE | `[PV] IMPACTO de COTACAO NACIONAL` |
| 2 | Impacto por UF | `[HL]` | NFE | `[PV] IMPACTO de COTACAO por UF` |
| 3 | **Tabela top IDs por IMP_COT** | `[T]` | NFE | `[PV] IMP_COT_ID` |
| 4 | Fornecedores mais baratos não escolhidos | `[T]` | COT_MIN_FORN | — |
| 5 | Produtos × MIN COT | `[T]` | NFE + COT_MIN_FORN | `[PV] PRODUTOS por ID - MIN COT` |

**Colunas tabela principal:**
ID · Produto · CAT2 · UF · Forn. comprado · Forn. menor preço · PMP pago · Menor cot. · Qtde · IMP_COT · Curva ID · Status

**Status:** `Comprou no menor` / `Acima do menor` / `Sem cotação` / `Baixa concorrência`

---

## ABA: INFLAÇÃO

*INF = variação do PMP (Preço Médio Ponderado) ao longo do tempo*

### KPIs (6 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Inflação média da cesta | INFLAÇÃO |
| 2 | Exposição monetária 12m | INFLAÇÃO |
| 3 | Top inflação (produto/categoria) | INFLAÇÃO |
| 4 | Top deflação | INFLAÇÃO |
| 5 | IDs afetados com inflação > 10% | PMP_ID_INF_12 |
| 6 | CAT2 mais inflada | INFLAÇÃO |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Inflação % por mês por CAT | `[GL]` 4 séries | INFLAÇÃO | `[AV] INFLACAO por MES por CAT - %` |
| 2 | Inflação R$ por mês | `[GB]` amarelo | INFLAÇÃO | `[AV] INFLACAO por MES por CAT - R$` |
| 3 | Top inflação (produtos) | `[HL]` sorted | PMP_ID_INF_12 | `[PV] TOP INFLACAO` |
| 4 | Top deflação (produtos) | `[HL]` verde | PMP_ID_INF_12 | `[PV] TOP DEFLACAO` |
| 5 | Nacional por categoria | `[T]` | INFLAÇÃO | `[PV] INFLACAO NACIONAL por CATEGORIA` |
| 6 | Por UF | `[T]` | INFLAÇÃO | `[PV] INFLACAO por UF` |
| 7 | Produto × categoria (matriz) | `[T]` scroll horiz | INFLAÇÃO | `[PV] INFLACAO por PRODUTO e CAT` |
| 8 | Por fornecedor | `[T]` | INFLAÇÃO | `[PV] FORNECEDORES INFLACAO` |

---

## ABA: FISCAL

*Dados combinam Zoho (spend) + base cadastral de fornecedores (regime fiscal)*

### KPIs (5 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Spend com crédito CBS/IBS (Lucro Real) | NFE + cadastral |
| 2 | Spend condicionado | NFE + cadastral |
| 3 | Spend indeterminado | NFE + cadastral |
| 4 | Fornecedores Simples/MEI (alto valor) | NFE + cadastral |
| 5 | Valor total em risco 2027 | NFE + cadastral |

### Elementos

| # | Elemento | Tipo | Fonte |
|---|---|---|---|
| 1 | Matriz valor × regime | `[MX]` 3 faixas × 4 regimes | NFE + cadastral |
| 2 | Fila priorizada | `[T]` Forn · Curva · Valor · Crédito · Ação | NFE + cadastral |
| 3 | Detalhe fiscal | `[T]` | NFE + cadastral |

---

## ABA: FINANCEIRO

*Separar CP operacional (fornecedores de bens/serviços) de CP financeiro (empréstimos, impostos)*

### KPIs (5 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | CP operacional em aberto | CP filtrado |
| 2 | CP vencido (operacional) | CP filtrado |
| 3 | A vencer 7 dias | CP |
| 4 | CP crítico > 120 dias | CP |
| 5 | Fornecedores AAA/A com CP vencido | CP + CURVA |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Timeline semanal próx. 8 semanas | `[GB]` agrupado | CP_SEMANA | `[PV] CP_STATUS` |
| 2 | Aging detalhado | `[T]` barras inline | CP | `[AV] CP_SALDO_DIVIDA_2026` |
| 3 | CP por fornecedor | `[T]` Forn · Aberto · Vencido · A vencer · Faixa · Curva | CP + CURVA | `[PV] CP_STATUS-TOTAL` |
| 4 | Saldo semanal 2026 | `[T]` | CP_SALDO_2026 | `[PV] CP_SALDO_26` |

---

## ABA: ADIANTAMENTOS

### KPIs (5 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | AD total 12m | AD_v3 |
| 2 | Conciliado | AD_v3 |
| 3 | Pendente / Status indefinido | AD_v3 |
| 4 | Notas vinculadas | AD_v3 + NF COM ITENS |
| 5 | AD pendente > 60 dias | AD_v3 |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Funil de conciliação | `[FU]` 5 estágios | AD_v3 | `[AV] Adiantamento %` |
| 2 | AD por empresa | `[HL]` duplo (conciliado/pendente) | AD_v3 | — |
| 3 | Adiantamento por mês | `[GL]` | AD_v3 | `[AV] Adiantamento por Mes` |
| 4 | AD por UF | `[HL]` | AD_v3 | `[AV] AD por UF` |
| 5 | AD por categoria | `[T]` | AD_v3 | `[AV] AD por CAT` |
| 6 | **Tabela detalhada** | `[T]` | AD_v3 | `[PV] ADIANTAMENTO` |
| 7 | AD por fornecedor | `[T]` | AD_v3 | `[PV] AD por FORNECEDOR` |

**Colunas tabela detalhada:**
Fornecedor · NF vinculada · AD · Valor · Conciliado · Status · Mês entrada · Mês pagamento · Empresa

---

## ABA: SERVIÇOS

### KPIs (5 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Total em serviços (D5 operacional) | NFE filtrado D5 não-financeiro |
| 2 | Fornecedores de serviços | NFE |
| 3 | UFs atendidas | NFE |
| 4 | Variação mensal | NFE |
| 5 | CP em aberto (serviços) | CP filtrado |

### Elementos

| # | Elemento | Tipo | Fonte | Origem Zoho |
|---|---|---|---|---|
| 1 | Por UF | `[HL]` | NFE D5 | `[AV] DESPESAS por UF` |
| 2 | Por mês | `[GB]` | NFE D5 | `[PV] SERVICOS por MES` |
| 3 | Por categoria | `[T]` CAT · Valor · % · Var 12m | NFE D5 | `[AV] SERVICOS` |
| 4 | Fornecedores de serviços | `[T]` | NFE D5 | — |
| 5 | Detalhe por CAT5 | `[T]` scroll horiz | NFE D5 | `[AV] DESPESAS por UF e CAT` |

---

## ABA: DADOS (Qualidade)

### KPIs (6 cards)

| # | [K] Label | Fonte |
|---|---|---|
| 1 | Linhas totais analisadas | manifest.json |
| 2 | Fontes OK / total | manifest.json |
| 3 | Fontes desatualizadas | manifest.json |
| 4 | Fornecedores sem CNPJ | base cadastral |
| 5 | Produtos sem código oficial | NFE |
| 6 | AD sem NF vinculada | AD_v3 |

### Elementos

| # | Elemento | Tipo | Fonte |
|---|---|---|---|
| 1 | Status por workspace/fonte | `[T]` Fonte · Workspace · Linhas · Cobertura · Estado | manifest.json |
| 2 | Fila de saneamento | `[T]` Problema · Campo · Linhas · Impacto · Ação | análise dados |
| 3 | Alertas de qualidade | `[AL]` | regras |

---

## Resumo por aba — contagem de elementos

| Aba | KPIs | Tabelas | Gráficos | Total elementos |
|---|---:|---:|---:|---:|
| Resumo | 8 | 5 | 5 | **18** |
| Oportunidades | 6 | 1 | 3 | **10** |
| Categorias | 6 | 3 | 2 | **11** |
| Filiais | 6 | 3 | 2 | **11** |
| Estoque | 8 | 2 | 2 | **12** |
| Fornecedor 360 | 6 | 7 | — | **13** |
| Produtos | 6 | 4 | 2 | **12** |
| Cotações | 8 | 8 | 2 | **18** |
| Impacto | 6 | 3 | 2 | **11** |
| Inflação | 6 | 4 | 4 | **14** |
| Fiscal | 5 | 3 | — | **8** |
| Financeiro | 5 | 3 | 1 | **9** |
| Adiantamentos | 5 | 4 | 2 | **11** |
| Serviços | 5 | 3 | 2 | **10** |
| Dados | 6 | 2 | — | **8** |
| **TOTAL** | **102** | **59** | **31** | **166** |
