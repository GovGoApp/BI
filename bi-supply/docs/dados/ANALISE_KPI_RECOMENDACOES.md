# Análise de Dados e Recomendações de KPIs — BI de Suprimentos

Gerado em: 2026-06-01 | Base: dados reais extraídos do Zoho (Jun/2026)

---

## Contexto dos dados

| Métrica | Valor |
|---|---:|
| Total de compras no período | R$ 1.037.722.004 |
| Período coberto | 2024, 2025, 2026 (parcial) |
| Linhas de NFE | 239.904 |
| Fornecedores com compras | 3.326 |
| Empresas | RC (92%), SU (4,5%), ME (3,5%) |

---

## Descobertas críticas nos dados

### 1. D5 Serviços distorce o total

D5 - SERVIÇOS representa **44,9% do gasto total (R$ 465M)**. No entanto, ao detalhar os produtos, os maiores valores são:
- `DEVOLUCAO DE EMPRESTIMO` → R$ 87,6M
- `MUTUO` → R$ 79,1M
- `MUTUO MM` → R$ 35,4M
- `ADIANTAMENTO COMPRA A VISTA` → R$ 50,5M
- `ICMS A PAGAR` → R$ 13,6M
- `PARCELAMENTO ESTADUAL/FEDERAL` → R$ 24,9M

**Esses são lançamentos financeiros e fiscais dentro do sistema de suprimentos**, não compras operacionais. O gasto real de suprimentos (insumos + materiais + serviços operacionais) é mais próximo de **R$ 550-600M**.

**Implicação para o BI:** criar filtro que separa "Suprimentos Operacional" de "Lançamentos Financeiros/Fiscais" nos KPIs principais.

### 2. Cobertura de cotação crítica

**64,3% das linhas de compra não têm cotação registrada** (PRE_MIN_COT = 0). Apenas 35,7% das compras passaram por processo de cotação. E dentre as que têm cotação:
- 57,2% têm apenas **1 cotação** (sem concorrência real)
- 32,2% têm 2-3 cotações
- 10,7% têm 4 ou mais

**Média geral: 1,9 cotações por produto/mês** — muito abaixo do ideal (mínimo 3).

### 3. Oportunidade real de R$ 17,9M

Em compras que tinham cotação disponível, o sistema comprou **acima do menor preço cotado** em 16,3% das linhas, gerando R$ 17,9M de "impacto positivo" — dinheiro que poderia ter sido poupado comprando no menor preço disponível.

Os produtos com maior oportunidade concentram-se em **proteínas** (carnes, frango) e **panificação** — alta frequência de compra, alta variação de preço.

### 4. Cauda longa de fornecedores

- **76 fornecedores** (A+ curva) = **53,6% do spend**
- **2.483 fornecedores CCC** = apenas **7,3% do spend** — enorme complexidade operacional para pouco valor

Oportunidade de consolidação: reduzir fornecedores CCC sem impacto relevante no abastecimento.

### 5. CP com R$ 23,6M acima de 120 dias

R$ 106,3M em títulos em aberto. O aging mostra R$ 23,6M com mais de 120 dias de atraso — risco de relacionamento com fornecedores críticos.

---

## Recomendações de KPIs por aba

---

### ABA: RESUMO

Visão executiva. Responde: "como estamos em suprimentos hoje?"

#### KPIs principais (barra de topo)

| KPI | Fórmula | Valor atual | Alerta |
|---|---|---|---|
| Total Comprado (operacional) | sum(TOTAL) excl. D5 financeiro | ~R$ 572M | — |
| Crescimento YoY | (2025 - 2024) / 2024 | +36,8% | Verde |
| Fornecedores Ativos | count distinct CDFORNECED com TOTAL > 0 | 3.326 | — |
| % Compras com Cotação | linhas com PRE_MIN_COT > 0 / total | 35,7% | Vermelho |
| Oportunidade IMP_COT | sum(IMP_COT) onde IMP_COT > 0 | R$ 17,9M | Amarelo |
| CP em Aberto | sum(VRATUAPAG) status ABERTO | R$ 106,3M | — |
| AD Pendente | sum(VALOR_FINAL) status != CONCILIADO | R$ 44M | Amarelo |
| CP Crítico +120d | sum(VRATUAPAG) faixa VE+120 | R$ 23,6M | Vermelho |

#### Gráficos e tabelas

| Elemento | Tipo | Fonte | Insight |
|---|---|---|---|
| Evolução de compras mensal | Linha | NFE por MESANO | Sazonalidade: pico em Mai/25 (R$ 63M vs Jan/25 R$ 22M) |
| Spend por CAT1 | Donut | NFE por CAT1 (filtrar financeiro) | I vs D vs A |
| Spend por tipo de negócio | Barra horizontal | NFE por FI.NEGOCIO | MERENDA 20%, CD 16%, HOSPITAL 16% |
| Top 5 UFs | Barra | NFE por UF | SP 52%, PE 22%, MA 11% |
| Top 10 fornecedores | Tabela | NFE + CURVA_FORN | Com curva ABC e % spend |
| Alertas executivos | Lista | Regras | Ver seção alertas abaixo |

#### Alertas recomendados

- 🔴 "64,3% das compras sem cotação"
- 🔴 "R$ 23,6M em CP com +120 dias de atraso"
- 🟡 "R$ 17,9M de oportunidade de cotação identificada"
- 🟡 "R$ 44M em adiantamentos sem status definido"
- 🟡 "Maio/25 com volume 2,8x acima de Janeiro/25"

---

### ABA: OPORTUNIDADES

Responde: "onde podemos economizar comprando melhor?"

#### KPIs

| KPI | Valor atual | Prioridade |
|---|---|---|
| Oportunidade total (IMP_COT > 0) | R$ 17,9M | Alta |
| % linhas compradas acima do mínimo | 16,3% | Alta |
| % linhas com apenas 1 cotação | 57,2% | Alta |
| Média de cotações por produto | 1,9 | Média |
| Fornecedores que mais ganham por não ser o mais barato | calcular de COT_MIN_FORN | Alta |

#### Top oportunidades reais (dados reais)

| ID | Produto | Oportunidade |
|---|---|---:|
| RCPEI201104000 | CARNE MOIDA 1ª | R$ 1.454.625 |
| RCPEI201203000 | FILE PEITO FRANGO | R$ 1.172.193 |
| RCPEI104113000 | PAO SEDINHA 50GR | R$ 1.116.411 |
| RCPEI104202040 | BOLO INGLES BACIA 50GR | R$ 623.264 |
| RCSPI201104020 | PATINHO MOIDO | R$ 502.722 |

**Padrão:** proteínas (carnes, frango) + panificação dominam as oportunidades. Alta frequência de compra + alta variação de preço entre fornecedores.

#### Elementos da aba

- Tabela principal: ID × produto × UF × fornecedor atual × fornecedor mais barato × oportunidade R$ × curva ID
- Gráfico: oportunidade por CAT2
- Gráfico: oportunidade por UF
- Filtro: curva ID (focar em AAA/AA/A)
- KPI: "se comprar sempre no mais barato" → economia estimada

---

### ABA: COTAÇÕES

Responde: "como está nosso processo de cotação?"

#### KPIs

| KPI | Valor | Benchmark mercado |
|---|---|---|
| % produtos com cotação | 35,7% | > 80% ideal |
| Média cotações/produto | 1,9 | ≥ 3 recomendado |
| % com monopolio (1 cot) | 57,2% | < 20% ideal |
| % comprado no menor preço | 83,7% das cotadas | > 95% ideal |

#### Elementos

- Gráfico: distribuição 0 / 1 / 2-3 / 4+ cotações ao longo dos meses
- Gráfico: cobertura de cotação por curva ABC (AAA sem cotação = risco máximo)
- Tabela: produtos curva A sem cotação nos últimos 3 meses
- Tabela: RELATÓRIO DE COTAÇÕES (produto × fornecedor × preço por mês)
- Tabela: MIN COTAÇÃO por fornecedor (quem é o mais barato e com que frequência)
- Alerta: produtos AAA/AA com apenas 1 cotação

---

### ABA: IMPACTO

Responde: "quanto perdemos por comprar acima do menor preço?"

#### KPIs

| KPI | Valor |
|---|---|
| Impacto positivo acumulado (oportunidade perdida) | R$ 17,9M |
| Impacto negativo acumulado (economizado) | R$ 33,0M |
| Saldo líquido | -R$ 15,1M (economizamos mais do que perdemos) |
| % linhas acima do mínimo | 16,3% |

**Observação importante:** o saldo negativo de R$ 33M significa que em muitos casos compramos ABAIXO da média histórica. Isso é positivo — mas os R$ 17,9M de oportunidade identificada ainda é relevante.

---

### ABA: INFLAÇÃO

Responde: "quais categorias e produtos estão subindo de preço?"

**Nota sobre os dados:** as variações percentuais extremas em D2 (+10.852%) e D5 (+6.180%) são artefatos — serviços e despesas financeiras não têm PMP estável. Focar em INSUMOS para análise de inflação real.

#### Inflação real relevante

| CAT2 | Variação PMP | Relevância |
|---|---|---|
| I3 - HORTIFRUTI | +201% | Alta — volume R$ 96M |
| I5 - LIMPEZA | +74,5% | Média — volume R$ 9M |
| I0 - NUTRICIONAIS | +340% | Verificar — pode ser mix |
| I6 - GÁS | -102,6% | Deflação ou mudança de fornecedor |

#### Elementos

- Gráfico: variação % PMP por categoria ao longo de 12 meses
- Gráfico: top 10 produtos com maior inflação (curva A)
- Gráfico: top 10 produtos com deflação (oportunidade de renegociação)
- Tabela: produto × PMP mês a mês × variação % × curva ID

---

### ABA: FORNECEDOR (360)

Responde: "quem são nossos fornecedores e qual é o risco de cada um?"

#### KPIs de cabeçalho

| KPI | Valor |
|---|---|
| Fornecedores ativos | 3.326 |
| Fornecedores AAA+AA+A (críticos) | 76 |
| % spend nos críticos | 53,6% |
| Fornecedores CCC (cauda) | 2.483 |
| % spend na cauda CCC | 7,3% |

#### Painel por fornecedor (ao selecionar)

- Total comprado (histórico + YTD)
- Curva ABC + posição no ranking
- Categorias fornecidas (CAT2)
- UFs atendidas
- Série histórica de PMP (12 meses)
- Impacto de cotação (comprou pelo mais barato deste fornecedor?)
- Títulos CP em aberto + aging
- Status adiantamentos

#### Elementos gerais

- Tabela ranking: fornecedor × curva × spend × % total × UFs × categorias
- Gráfico: spend por fornecedor (treemap ou barra, top 20)
- Filtro curva ABC
- Alerta: fornecedores AAA com CP vencido +30 dias

---

### ABA: PRODUTOS

Responde: "o que compramos e como evoluem os preços?"

**Nota:** os "produtos" com maior spend são lançamentos financeiros (MUTUO, DEVOLUCAO DE EMPRESTIMO). Filtrar categoria ≠ D5 financeiro para análise real.

#### Top produtos operacionais reais

| Produto | Spend | Categoria |
|---|---|---|
| FILE PEITO FRANGO | R$ 34,5M | I2 - PERECÍVEIS |
| CARNE MOIDA 1ª | R$ 23,5M | I2 - PERECÍVEIS |
| LEITE EM PO INTEGRAL | R$ 20,3M | I1 - ESTOCÁVEIS |
| MAO DE OBRA TERCEIRIZADO | R$ 24,4M | D5 - SERVIÇOS |
| TRANSPORTE DE INSUMOS | R$ 22,5M | D5 - SERVIÇOS |

#### KPIs

- Total de IDs únicos: 13.059
- IDs curva AAA+AA+A: 279 (2,1% dos IDs = concentração de valor)
- IDs curva CCC: 10.020 (76,7% dos IDs)

#### Elementos

- Tabela: produto × IDs × curva × PMP atual × variação 12m × cotações
- Gráfico: PMP de um produto ao longo de 12 meses (série temporal)
- Gráfico: top produtos por inflação

---

### ABA: FINANCEIRO (CP)

Responde: "qual nossa exposição financeira em contas a pagar?"

#### KPIs

| KPI | Valor |
|---|---|
| CP em aberto total | R$ 106,3M |
| Títulos em aberto | 5.835 |
| CP crítico (+120 dias) | R$ 23,6M |
| CP a vencer em 15 dias | R$ 17M |
| CP 7 dias vencido | R$ 15M |

#### Aging (dados reais)

| Faixa | Valor |
|---|---:|
| Vencido +120 dias | R$ 23.631.395 |
| A vencer em 15 dias | R$ 16.956.094 |
| Vencido 7 dias | R$ 15.083.796 |
| Vencido 120 dias | R$ 9.304.667 |
| A vencer hoje | R$ 8.962.879 |
| A vencer em 7 dias | R$ 8.705.668 |
| Vencido 60 dias | R$ 7.815.116 |

#### Elementos

- Gráfico aging: barras por faixa (cor: verde/amarelo/vermelho)
- Tabela: fornecedor × CP em aberto × maior título × dias vencido × curva ABC
- Alerta: fornecedores AAA com títulos vencidos +30 dias

---

### ABA: ADIANTAMENTOS

Responde: "quais adiantamentos precisam ser conciliados?"

#### KPIs

| KPI | Valor |
|---|---|
| AD com status indeterminado | R$ 44,0M (3.455 reg.) |
| AD conciliados | R$ 16,3M (1.572 reg.) |
| Total sob gestão | R$ 60,3M |

**Alerta crítico:** R$ 44M em adiantamentos sem STATUS_CONCILIACAO definido ("?") — precisam ser investigados. Representa 73% do total de adiantamentos.

---

### ABA: CATEGORIAS

Responde: "como se distribuem as compras por categoria?"

#### Elementos

- Filtros em cascata: CAT1 → CAT2 → CAT3 → CAT4 → CAT5 (ordem I→D→A)
- KPI: total comprado na seleção
- KPI: fornecedores na categoria
- KPI: % com cotação
- Gráfico: evolução mensal da categoria selecionada
- Tabela: top produtos da categoria × spend × variação de preço

---

### ABA: FILIAIS

Responde: "como se distribuem as compras por filial e tipo de negócio?"

#### Por tipo de negócio (dados reais)

| Negócio | Spend | % |
|---|---:|---|
| MATRIZ | R$ 410,9M | 39,6% |
| MERENDA | R$ 205,2M | 19,8% |
| CD | R$ 170,1M | 16,4% |
| HOSPITAL | R$ 161,2M | 15,5% |
| COZINHA | R$ 22,4M | 2,2% |

**Nota:** MATRIZ com 39,6% provavelmente inclui as transações financeiras e lançamentos centralizados.

---

### ABA: FISCAL

Responde: "qual é o risco fiscal por fornecedor em relação à Reforma 2027?"

Dados vêm do projeto de fornecedores (não do Zoho), cruzados com spend do NFE.

#### KPIs a construir (após integração)

- % spend com fornecedores Simples Nacional / MEI
- % spend com fornecedores com regime indeterminado
- Impacto estimado de perda de crédito CBS/IBS por fornecedor/categoria

---

## Resumo das prioridades de implementação

### Alta prioridade (dados disponíveis, impacto alto)

1. **Oportunidade de cotação**: R$17,9M identificados, lista exata de produtos e fornecedores
2. **Cobertura de cotação**: 64,3% sem cotação — KPI mais crítico do processo de compras
3. **CP aging**: R$23,6M +120 dias — risco financeiro imediato
4. **Concentração de fornecedores**: 76 fornecedores = 53,6% do spend

### Média prioridade (dados disponíveis, análise adicional necessária)

5. **Inflação em hortifruti** (+201%) e nutricionais — necessita validação do cálculo
6. **Adiantamentos R$44M** sem status — investigar com área financeira
7. **Separação D5 financeiro** do spend operacional — filtro crítico para KPIs

### Para discussão com o negócio

8. **MATRIZ 39,6%**: o que são esses lançamentos centralizados?
9. **Pico de Maio/25 (R$63M)**: qual foi o evento?
10. **Sazonalidade**: por que Janeiro é sempre o mês mais baixo?
