# Análise de KPIs — BI de Suprimentos
## Metodologia A (dados reais) + Metodologia B (benchmarks de mercado)

Gerado em: 2026-06-01 | Base: 239.904 linhas de NFE + 17 fontes Zoho

---

## CONTEXTO: O QUE OS DADOS REPRESENTAM

**Total no período (2024–2026 parcial):** R$ 1.037.722.004

| Empresa | Spend | % |
|---|---:|---|
| RC | R$ 954.674.892 | 92% |
| SU | R$ 46.958.763 | 4,5% |
| ME | R$ 36.088.350 | 3,5% |

**Alerta de dados crítico:** D5 SERVIÇOS (R$ 465M, 44,9%) inclui lançamentos financeiros — MUTUO (R$ 79M), DEVOLUCAO DE EMPRESTIMO (R$ 87M), ICMS A PAGAR (R$ 13M), PARCELAMENTOS (R$ 24M). O spend **operacional real** de suprimentos é ~R$ 572M. Qualquer KPI de spend total precisa filtrar esses lançamentos.

---

## ACHADOS CRÍTICOS — DADOS REAIS

### ACHADO 1 — Hortifruti e Perecíveis: o processo de cotação não funciona

**I3 Hortifruti: 63,1% das compras COM cotação são realizadas ACIMA do menor preço disponível.**
**I2 Perecíveis: 60,3% acima do mínimo cotado.**

Isso significa: quando existe cotação, ainda assim compramos do mais caro na maioria das vezes nessas categorias.

| CAT2 | % acima do mínimo | Perda apurada |
|---|---:|---:|
| I3 - HORTIFRUTI | 63,1% | R$ 1.486.617 |
| I2 - PERECÍVEIS | 60,3% | R$ 9.067.236 |
| I1 - ESTOCÁVEIS | 49,3% | R$ 5.465.726 |
| I4 - DESCARTÁVEIS | 33,0% | R$ 1.337.637 |
| I5 - LIMPEZA | 27,5% | R$ 321.566 |

**Hipótese:** perecíveis têm urgência de entrega, logística regional e disponibilidade limitada — o preço perde para a conveniência. Isso precisa de decisão de negócio: aceitar ou criar processo de cotação prévia com compromisso de entrega.

---

### ACHADO 2 — 16 produtos AAA comprados sem nenhuma cotação

Esses produtos estão na curva AAA (top de spend) e nunca apareceram no sistema de cotações:

| Produto | UF | Spend anual est. |
|---|---|---:|
| BANANA NANICA T.120 | MA | R$ 3.577.240 |
| MACA NACIONAL T.180 | PE | R$ 3.446.039 |
| MELAO | PE | R$ 3.402.910 |
| BANANA PRATA | PE | R$ 2.826.299 |
| GAS GLP BOTIJAO P45 | SP | R$ 2.511.393 |
| MELANCIA | PE | R$ 2.415.338 |
| ABACAXI PEROLA | PE | R$ 1.876.981 |
| TANGERINA CRAVO T.10 | PE | R$ 1.633.781 |
| OVO DE GALINHA BRANCO MED | PE | R$ 1.626.336 |
| LARANJA PERA T.10 | PE | R$ 1.533.453 |

**R$ 25M+** em produtos AAA sem nenhuma cotação registrada. Todos são frutas/hortifrutis ou gás — compras recorrentes e de alto volume tratadas como se fossem compras emergenciais.

---

### ACHADO 3 — 97 produtos AAA/AA/A com apenas 1 cotação (R$ 123M em risco)

Produtos de alto valor onde só existe 1 fornecedor cotando. Sem concorrência = sem pressão de preço:

| CAT2 | IDs afetados | Spend em risco |
|---|---:|---:|
| I2 - PERECÍVEIS | 24 | R$ 55.379.275 |
| I1 - ESTOCÁVEIS | 47 | R$ 47.942.841 |
| I3 - HORTIFRUTI | 8 | R$ 6.191.734 |
| I0 - NUTRICIONAIS | 6 | R$ 5.539.021 |
| I4 - DESCARTÁVEIS | 10 | R$ 4.508.763 |
| I6 - GÁS | 2 | R$ 3.356.873 |

---

### ACHADO 4 — Eficiência de cotação varia fortemente por UF

MA tem cobertura de cotação de apenas 19,3% — quase metade do que SP (35,3%). PI tem o maior percentual de compras acima do mínimo (6,56% do spend vs 1,27% em SP):

| UF | Spend | % com cotação | IMP_COT | IMP/Spend |
|---|---:|---:|---:|---:|
| SP | R$ 540M | 35,3% | R$ 6,9M | 1,27% |
| PE | R$ 229M | 36,0% | R$ 6,6M | **2,89%** |
| MA | R$ 117M | **19,3%** | R$ 1,2M | 1,01% |
| ES | R$ 46M | 34,5% | R$ 816K | 1,77% |
| RN | R$ 40M | 34,1% | R$ 185K | 0,46% |
| PI | R$ 12M | 44,3% | R$ 845K | **6,56%** |

PI tem pouco volume mas a pior eficiência proporcional — compras bem acima do mínimo com cotação disponível. PE compra proporcionalmente 2x pior que SP.

---

### ACHADO 5 — PE concentra produtos exclusivos sem alternativa geográfica

PE compra R$ 8,7M em sucos néctar de um único fornecedor local. Nenhuma outra UF compra esses produtos:

| Produto | Spend PE |
|---|---:|
| SUCO NECTAR CAJU | R$ 2.116.581 |
| SUCO NECTAR MANGA | R$ 1.561.285 |
| SUCO NECTAR ACEROLA | R$ 1.448.890 |
| SUCO NECTAR TANGERINA | R$ 1.312.283 |
| SUCO NECTAR GOIABA | R$ 1.268.331 |

Além disso: BISCOITO COOKIES FONTE FIBRAS CACAU (R$ 1,2M) — produto regional específico. Risco de abastecimento e preço sem benchmark comparativo.

---

### ACHADO 6 — Alta rotatividade de fornecedores (41% ao ano)

| Ano | Fornecedores ativos |
|---|---:|
| 2024 | 1.689 |
| 2025 | 2.088 (+24%) |
| 2026 | 1.709 |

**1.106 novos fornecedores** entraram em 2025 que não existiam em 2024.
**707 fornecedores** de 2024 não aparecem mais em 2025.

Rotatividade de 41% na base ativa. Isso indica instabilidade na base de fornecedores ou processo de homologação fraco. Do ponto de vista de procurement: alta rotatividade → perda de poder de negociação, falta de relacionamento de longo prazo, risco de qualidade.

---

### ACHADO 7 — Variação de preço do mesmo produto entre unidades de negócio

Produtos idênticos sendo comprados a preços completamente diferentes por tipo de negócio:

| Produto | Variação | Negócios |
|---|---|---|
| SACO BOBINA PICOTADA 40X60 | 76.785% | COZINHA: R$15,71 | ESCOLA: R$65,93 | _MATRIZ: R$40,31 |
| PAPEL TOALHA INTERFOLHA | 35.907% | ESCOLA: R$5,21/un | HOSPITAL: R$0,02/un |
| ASSISTÊNCIA MÉDICA | 12.240% | MERENDA: R$18.080/item | COZINHA: R$233/item |

As variações extremas podem ter explicação de unidade de medida (compra por caixa vs unidade), mas precisam de investigação. O produto "ASSISTÊNCIA MÉDICA" com preço 78x maior em MERENDA vs COZINHA é especialmente suspeito.

---

### ACHADO 8 — Oportunidade de consolidação: CCC comprando onde existe AAA/A

Produtos que compramos de fornecedores CCC, mas para os quais já existem fornecedores AAA/A ativos:

| Produto | Spend CCC | Spend AAA/A disponível |
|---|---:|---:|
| MACA NACIONAL T.180 | R$ 159.601 | R$ 3.659.491 |
| ABACAXI PEROLA | R$ 116.435 | R$ 2.314.097 |
| QUEIJO MUSSARELA FATIADO | R$ 89.664 | R$ 1.564.133 |
| CENOURA | R$ 152.842 | R$ 1.333.012 |
| CEBOLA | R$ 181.275 | R$ 967.328 |
| ÁGUA MINERAL | R$ 188.775 | R$ 432.184 |

---

### ACHADO 9 — CP mistura obrigações financeiras com fornecedores reais

Os maiores "CP vencidos" nos fornecedores de curva AAA são instituições financeiras e obrigações fiscais, não fornecedores de suprimentos:

- LANA CRED: R$ 345M "vencido" (empréstimos/mútuo)
- SPERO PARTICIPACOES: R$ 68M
- C6 BANK: R$ 66M
- SECRETARIA DA RECEITA FEDERAL: R$ 16M

O CP precisa ser filtrado por tipo de conta (`CDTPCTPAGAR`) para separar:
- **CP operacional** (fornecedores de bens e serviços)
- **CP financeiro** (empréstimos, parcelamentos, impostos)

Misturar os dois distorce completamente o aging e o risco de relacionamento com fornecedores.

---

## BENCHMARKS DE MERCADO — O QUE OS DADOS INDICAM

| KPI | Nossa realidade | Benchmark mínimo | World-class | Situação |
|---|---|---|---|---|
| **Spend com cotação (SUM proxy)** | 35,7% | 70% | 91,5% | 🔴 Crítico |
| **Cotações por produto** | 1,9 média | 3+ | 3-5 | 🔴 Abaixo |
| **% comprado no menor preço** | 83,7% das cotadas | 95% | 98%+ | 🟡 Atenção |
| **Maverick spend proxy** | 64,3% sem cotação | <10% | <5% | 🔴 Crítico |
| **Rotatividade de fornecedores** | 41%/ano | <15% | <10% | 🔴 Muito alta |
| **I2/I3 compra acima do mínimo** | 60-63% | <20% | <10% | 🔴 Crítico |

---

## KPIs RECOMENDADOS POR ABA

### RESUMO (nível executivo)

**KPIs de topo — 8 cards:**

| KPI | Fórmula | Valor atual |
|---|---|---|
| Spend Operacional | sum(TOTAL) excl. D5 financeiro | ~R$ 572M |
| Crescimento YoY | (2025/2024) - 1 | +36,8% |
| SUM % | linhas com PRE_MIN_COT > 0 / total | 35,7% 🔴 |
| Oportunidade cotação | sum(IMP_COT > 0) | R$ 17,9M |
| Fornecedores críticos sem cotação | IDs AAA/AA/A com QTD_COT = 0 | 16 |
| CP operacional em aberto | CP filtrado por tipo operacional | a calcular |
| AD pendente | sum VALOR_FINAL onde status = '?' | R$ 44M |
| Novos fornecedores YTD | distinct CDFORNECED 2026 não vistos antes | calcular |

**Gráficos:**
- Evolução mensal de spend (com destaque em picos anormais)
- Spend por CAT1 — excluindo D5 financeiro
- Top 5 UFs com eficiência de cotação (% com cotação + IMP/Spend)
- Distribuição fornecedores por curva ABC
- Alertas críticos: IDs AAA sem cotação, CP crítico +30d operacional

---

### OPORTUNIDADES

**KPIs focados:**
- Oportunidade total IMP_COT: R$ 17,9M
- Top 3 categorias para focar: I2 Perecíveis (R$ 9M), I1 Estocáveis (R$ 5,5M), I3 Hortifruti (R$ 1,5M)
- 97 produtos AAA/AA/A com apenas 1 cotação → R$ 123M sem competição
- 16 produtos AAA com zero cotação → R$ 25M+ sem qualquer processo

**Tabela principal:**
ID × produto × CAT2 × UF × fornecedor atual × fornecedor mais barato × % acima do mínimo × oportunidade R$ × curva ID × situação (SEM COT / MONO-COT / ACIMA DO MÍNIMO)

---

### COTAÇÕES

**KPIs específicos:**
- % cobertura por CAT2 (gráfico de calor: categoria × mês)
- % mono-cotação por CAT2 — focar I1 e I2
- Eficiência por UF (tabela A4 acima)
- Série temporal: cobertura de cotação mensal (está melhorando ou piorando?)
- Produtos AAA/AA com 0 cotação nos últimos 3 meses (lista acionável)

---

### IMPACTO

**Separado de inflação:**
- IMP_COT: diferença entre preço pago e menor preço cotado
- Ranqueado por CAT2, por UF, por produto
- Série temporal: oportunidade está crescendo ou diminuindo?
- Quais fornecedores aparecem mais como "mais barato não escolhido"?

---

### INFLAÇÃO

**Focar em INSUMOS (excluir D5 e D6 que distorcem):**
- I3 Hortifruti: +201% variação de PMP — real e relevante
- I5 Limpeza: +74,5%
- Série 12 meses por produto (PMP_ID_INF_12)
- Top 10 com inflação positiva × Top 10 com deflação (oportunidade de renegociação)
- Alerta: produtos AAA com inflação > 15% no último trimestre

---

### FORNECEDOR 360

**KPIs específicos do achado:**
- Separar fornecedores operacionais de financeiros/fiscais (filtro por tipo)
- Rotatividade: quantos fornecedores entraram/saíram por categoria
- Dependência: IDs com apenas 1 fornecedor ativo (sem backup de abastecimento)
- Fornecedores CCC ativos onde existe alternativa AAA/A para o mesmo produto

---

### FINANCEIRO (CP)

**Separar CP operacional de financeiro/fiscal:**
- Criar filtro por CDTPCTPAGAR para isolar fornecedores de bens/serviços
- Aging só do CP operacional
- Fornecedores AAA/AA/A de suprimentos com CP vencido > 30 dias (risco de ruptura)
- CP a vencer nos próximos 7, 15, 30 dias (mapa de caixa)

---

### ADIANTAMENTOS

- R$ 44M com STATUS_CONCILIACAO indefinido ('?') → lista para ação imediata
- Por fornecedor: quem tem mais AD pendente
- Por categoria: onde AD é mais comum
- Tempo médio entre pagamento do AD e entrada da nota

---

### CATEGORIAS

**Filtros em cascata + análises específicas:**
- Ao selecionar uma categoria: mostrar IMP_COT, cobertura de cotação, inflação, top fornecedores
- Alertas por categoria: "I2 tem 60% de compras acima do mínimo" aparece ao abrir Perecíveis
- Comparativo de preço entre UFs para o mesmo produto na categoria

---

### FILIAIS

**Além do óbvio:**
- % de spend com cotação por filial (quais filiais têm processo melhor)
- IMP_COT por filial (quais filiais pagam mais caro proporcionalmente)
- Produtos comprados por uma única filial sem benchmark comparativo
- Rotatividade de fornecedores por tipo de negócio

---

## PERGUNTAS PARA O NEGÓCIO (a responder antes de definir filtros)

1. **D5 financeiro:** como separar D5 operacional (serviços prestados) de D5 financeiro (MUTUO, DEVOLUÇÃO)? Existe um campo `CDTPCTPAGAR` ou `CAT3` que faça essa distinção?

2. **CP:** qual o critério para separar CP de fornecedor de bens/serviços de CP de obrigações financeiras (empréstimos, impostos)?

3. **Pico de Maio/25 (R$ 63M):** foi um evento específico? Compra sazonal? Estoque?

4. **MATRIZ 39,6%:** o que compõe esse tipo de negócio — são lançamentos consolidados ou uma unidade operacional?

5. **Variação de preço entre negócios:** os preços extremamente diferentes para o mesmo produto são questões de unidade de medida ou refletem pagamentos reais diferentes?
