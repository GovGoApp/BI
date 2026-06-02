# Relatório de Cobertura de Dados — BI Suprimentos

**Data:** 2026-06-01  
**Base:** Cruzamento entre `data/processed/` e `design/BI Suprimentos v4.html`  
**Objetivo:** Identificar o que está pronto, o que falta e o que precisa de ação para o dashboard

---

## Resumo Executivo

| Métrica | Valor |
|---|---|
| Abas com cobertura ≥ 80% | 4 (resumo, impacto, financeiro, adiantamento) |
| Abas com cobertura 60–79% | 7 |
| Abas bloqueadas por dependência externa | 2 (estoque, fiscal) |
| Datasets faltando | 14 |
| KPIs faltando | 13 |
| Fontes não extraídas que desbloqueiam dados | 2 (FAT_SUP, APURAÇÃO DE RESULTADOS) |

---

## 1. Cobertura por Aba

| # | Aba | Cobertura | Situação |
|---|---|---|---|
| 01 | resumo | **80%** | CMV e alertas faltam |
| 02 | oportunidade | **70%** | Matriz prioridade e HL por tipo faltam |
| 03 | categoria | **60%** | T fornecedores e T produtos por categoria faltam |
| 04 | filial | **65%** | CMV, filial×fornecedor e 3 KPIs faltam |
| 05 | estoque | **0%** | BLOQUEADO — workspace APURAÇÃO não extraído |
| 06 | fornecedor | **55%** | Sub-datasets do detail row faltam |
| 07 | produto | **70%** | Cotações e UF por produto faltam, 4 KPIs faltam |
| 08 | cotacao | **65%** | 4 dos 10 blocos obrigatórios faltam |
| 09 | impacto | **90%** | Falta apenas PRODUTOS × MIN COT |
| 10 | inflacao | **75%** | produto×categoria e por fornecedor faltam |
| 11 | fiscal | **0%** | BLOQUEADO — dados cadastrais externos |
| 12 | financeiro | **90%** | Falta "Em negociação" |
| 13 | adiantamento | **85%** | Tabela detalhada (ADIANTAMENTO_NFE falhou no sampling) |
| 14 | servico | **60%** | 3 KPIs e detalhe por CAT5 faltam |
| 15 | dados | **80%** | Alertas e workspace APURAÇÃO faltam |

---

## 2. Datasets Faltando — Ação no transform.py

Todos os datasets abaixo podem ser gerados com os dados já disponíveis em `data/raw/`. Requerem apenas adicionar funções ao `pipeline/transform.py`.

| Prioridade | Dataset | Aba | Arquivo a criar | Fonte em raw/ |
|---|---|---|---|---|
| 🔴 Alta | Consulta de preços cotados | 08_cotacao | `08_cotacao_r07_consulta_precos.csv` | cot.csv |
| 🔴 Alta | Cotações por produto (individual) | 08_cotacao | `08_cotacao_r08_cotacao_por_produto.csv` | cot.csv + num_cot.csv |
| 🔴 Alta | Matriz produto × mês (# e MIN) | 08_cotacao | `08_cotacao_r09_matriz_produto_mes.csv` | num_cot.csv |
| 🔴 Alta | MIN cotação ≤ 3 concorrentes | 08_cotacao | `08_cotacao_r10_min_cot_baixa_concorrencia.csv` | cot_min_forn.csv |
| 🔴 Alta | Matriz prioridade (impacto × esforço) | 02_oportunidade | `02_oportunidade_r04_matriz_prioridade.json` | nfe.csv + num_cot.csv |
| 🔴 Alta | Oportunidade por tipo (6 tipos) | 02_oportunidade | `02_oportunidade_r05_por_tipo.csv` | nfe.csv + num_cot.csv |
| 🔴 Alta | Top fornecedores por categoria | 03_categoria | `03_categoria_r04_top_fornecedor.csv` | nfe.csv |
| 🔴 Alta | Top produtos por categoria (com PMP+inflação) | 03_categoria | `03_categoria_r05_top_produto.csv` | nfe.csv + pmp12 |
| 🟡 Média | Produtos × MIN COT | 09_impacto | `09_impacto_r05_produto_min_cot.csv` | nfe.csv + cot_min_forn.csv |
| 🟡 Média | Inflação por fornecedor | 10_inflacao | `10_inflacao_r07_por_fornecedor.csv` | inflacao.csv + nfe.csv |
| 🟡 Média | Produto × categoria (matriz inflação) | 10_inflacao | `10_inflacao_r08_produto_por_cat.csv` | inflacao.csv |
| 🟡 Média | Filial × Fornecedor | 04_filial | `04_filial_r05_por_fornecedor.csv` | nfe.csv |
| 🟡 Média | Detalhe por CAT5 (serviços) | 14_servico | `14_servico_r05_por_cat5.csv` | nfe.csv |
| 🟢 Baixa | Produtos comprados por fornecedor | 06_fornecedor | `06_fornecedor_r03_produto_por_forn.csv` | nfe.csv |

---

## 3. KPIs Faltando — Ação no transform.py

| Prioridade | KPI | Aba | Chave | Como calcular |
|---|---|---|---|---|
| 🔴 Alta | Produtos/IDs únicos no período | 01_resumo | `ids_unicos` | `COUNT(DISTINCT ID)` em nfe.csv |
| 🔴 Alta | IDs sem cotação 12m | 07_produto | `ids_sem_cotacao_12m` | IDs em nfe que não estão em num_cot |
| 🔴 Alta | Variação PMP > 10% | 07_produto | `ids_variacao_pmp_gt10pct` | Calc da série PMP em pmp12 |
| 🔴 Alta | PMP médio da cesta | 07_produto | `pmp_medio_cesta` | `AVG(PMP_0)` em pmp12 |
| 🔴 Alta | Inflação média da cesta | 07_produto | `inflacao_media_cesta` | `AVG(PERC_INF_ID_PMP)` em inflacao |
| 🔴 Alta | Fornecedores que nunca são o mais barato | 02_oportunidade | `forn_nunca_mais_barato` | Fornecedores que não aparecem em COT_MIN_FORN |
| 🟡 Média | Maior UF por spend | 04_filial | `maior_uf` | `MAX` em resumo_por_uf |
| 🟡 Média | Maior tipo de negócio | 04_filial | `maior_negocio` | `MAX` em por_negocio |
| 🟡 Média | Compra/CMV médio | 04_filial | `compra_cmv_medio` | Requer FAT_SUP |
| 🟡 Média | Variação mensal serviços | 14_servico | `variacao_mensal_pct` | Comparativo mês atual vs anterior |
| 🟡 Média | Maior categoria de serviços | 14_servico | `maior_categoria` | `MAX` em por_categoria D5 |
| 🟡 Média | CP em aberto (serviços) | 14_servico | `cp_aberto_servicos` | CP cruzado com CDTPCTPAGAR de serviços |
| 🟢 Baixa | Risco Fiscal 2027 (qtde fornecedores) | 01_resumo | `risco_fiscal_forn` | Requer base cadastral |

---

## 4. Fontes não Extraídas — Ação no extract.py / sources.yml

### 4.1. FAT_SUP — Desbloqueio de Alta Prioridade

**Impacto:** habilita CMV e ratio Compra/CMV em resumo e filiais.

**Ação:** Adicionar ao `pipeline/sources.yml`:
```yaml
- id: fat_sup
  zoho_name: "FAT_SUP"
  max_age_hours: 24
  description: "Faturamento vs suprimentos — SUP, CMV, FAT por empresa e período"
  abas: [resumo, filial]
```

**Datasets habilitados após extração:**
- `01_resumo`: coluna `compra_cmv` e elemento "Spend × CMV"
- `04_filial`: coluna `cmv` e ratio `compra_cmv` na tabela consolidada
- KPI `compra_cmv_medio` em filial

---

### 4.2. APURAÇÃO DE RESULTADOS — Workspace Estoque

**Workspace ID:** `2130260000006068011`  
**Impacto:** habilita a aba inteira `05_estoque` (8 KPIs + 5 elementos).

**Ação:** Adicionar as fontes do workspace APURAÇÃO ao `sources.yml`. As fontes relevantes são:
- `ANALISE DE ESTOQUE - IDEAL` (Pivot, workspace APURAÇÃO)
- `ANALISE DE ESTOQUE - MELHOR` (Pivot, workspace APURAÇÃO)
- `ANALISE DE ESTOQUE - POMME VITA` (Pivot, workspace APURAÇÃO)
- `MOV. DE ESTOQUE ANALITICO - IDEAL` (Pivot)

**Nota técnica:** O `zoho/client.py` já suporta multi-workspace via `get_views(workspace_id=...)`. O `extract.py` precisa de um parâmetro adicional para fontes de workspaces diferentes.

---

### 4.3. ADIANTAMENTO_NFE — Investigar Erro de Sampling

**Situação:** A fonte `ADIANTAMENTO_NFE` falhou no profiling (amostra vazia).  
**Impacto:** Falta a tabela detalhada em `13_adiantamento` com colunas: Fornecedor · NF vinculada · AD · Valor · Conciliado · Status · Mês entrada · Mês pagamento.

**Ação de investigação:** Testar diretamente:
```powershell
python zoho/client.py --env-file zoho/zoho.env export-sql --sql "select * from \"ADIANTAMENTO_NFE\" limit 5" --out data/raw/test_adiantamento_nfe.csv --wait
```
Se funcionar, adicionar ao `sources.yml`. Se falhar, usar `AD_v3` como substituto (já extraído).

---

## 5. Casos Especiais — Tratamento Diferente

### 5.1. Detail Row do Fornecedor 360

O v4 tem detail rows expansíveis com 9 sub-cards por fornecedor. Os dados (cotações alternativas, produtos comprados, inflação por fornecedor) **não devem ficar em CSV estático** — seriam 3.326 sub-datasets.

**Solução correta:** Usar o **módulo NL-SQL** (`nlsql/`) para buscar dados on-demand quando o usuário expande um fornecedor. O dashboard chama o NL-SQL com o CDFORNECED do fornecedor selecionado.

**Dados estáticos suficientes:** O `06_fornecedor_r01_tabela_principal.csv` já tem os campos da linha principal (curva, spend, CP, AD). O detail row buscará on-demand.

---

### 5.2. Alertas Executivos (AL)

Os alertas não são dados estáticos — são regras aplicadas sobre os dados processados. Precisam ser implementados no `pipeline/build.py` como lógica de regras.

**Regras a implementar:**
1. 🔴 `"X% das compras sem cotação"` → quando `pct_com_cotacao < 50%`
2. 🔴 `"R$ X em CP com +120 dias"` → quando `cp_critico_120d > 0`
3. 🟡 `"R$ X de oportunidade de cotação"` → sempre mostrar
4. 🟡 `"R$ X em adiantamentos sem status"` → quando `ad_pendente > 0`
5. 🟡 `"Maio/25 com volume X acima da média"` → desvio padrão de `por_mes`
6. 🔵 `"16 produtos AAA sem cotação"` → contar de `oportunidade_tabela_principal` onde tipo="Sem cotação AAA/A"

---

### 5.3. Gráficos — Formato dos Dados

Os CSVs estão em **formato longo** (uma linha por observação). Gráficos de múltiplas séries (GL com 4 linhas, GE empilhado) precisam de **pivotagem no dashboard JS**.

| Tipo de gráfico | Situação dos dados | Ação no dashboard JS |
|---|---|---|
| GL múltiplas séries | Longo (cat2+mesano+valor) | `pivot` → colunas por cat2 |
| GE empilhado cotação | ✓ Já wide (colunas por faixa) | Nenhuma |
| MX heatmap | Longo (cat2+uf+valor) | `pivot` → grade 2D |
| SP sparkline | ✓ JSON array inline em CSV | Parsear array |
| GB barras simples | ✓ Longo (mesano+valor) | Nenhuma |
| HL hbar | ✓ Longo (label+valor) | Nenhuma |

---

## 6. Plano de Ação — Sequência Recomendada

### Fase A — Completar transform.py (2–3h de implementação)

**Objetivo:** Elevar cobertura geral de ~70% para ~90%

1. Adicionar datasets de cotação faltantes (r07 a r10 da aba 08_cotacao)
2. Adicionar matriz prioridade e por tipo em oportunidade
3. Adicionar top fornecedor e top produto por categoria
4. Corrigir KPIs de produto (adicionar 4 faltantes)
5. Adicionar filial×fornecedor e detalhe CAT5 serviços
6. Adicionar inflação por fornecedor e produto×categoria

### Fase B — Adicionar FAT_SUP ao pipeline (1h)

1. Adicionar `fat_sup` ao `sources.yml`
2. Extrair: `python pipeline/extract.py --env-file zoho/zoho.env --source fat_sup`
3. Criar função `aba_resumo_cmv()` no transform.py para gerar Spend × CMV

### Fase C — Investigar e resolver fontes pendentes (variável)

1. Testar `ADIANTAMENTO_NFE` diretamente via client.py
2. Planejar extração do workspace APURAÇÃO para aba estoque
3. Integrar base cadastral fiscal para aba fiscal (fase futura)

### Fase D — Implementar alertas no build.py

1. Criar módulo de regras `pipeline/alerts.py`
2. Integrar alertas no build do dashboard

---

## 7. O que NÃO faz sentido / Anomalias nos dados

| Anomalia | Onde | Ação |
|---|---|---|
| D5 SERVIÇOS inclui lançamentos financeiros (MUTUO R$87M, DEVOLUCAO R$79M) | resumo, servico | Filtro já aplicado no transform, mas KPI "Total Comprado" ainda inclui. Criar KPI separado "Total Operacional" |
| CMV histórico pago em CP: R$18,8 bilhões | 12_financeiro | CP inclui obrigações financeiras históricas — filtrar por CDTPCTPAGAR para CP operacional |
| INFLAÇÃO: D2 ESCRITÓRIO +10.852%, D5 SERVIÇOS +6.180% | 10_inflacao | Serviços e despesas não têm PMP estável — filtrar INF por CAT1 = 'I - INSUMOS' para análise real |
| Pico de Maio/25: R$63,5M (vs média R$38M) | 01_resumo | Investigar com negócio: evento específico? Compra de estoque? |
| CURVA_ID vazia em ~566 linhas de NUM_COT | 08_cotacao | Registros sem curva classificada — tratar como "Sem curva" |

---

## 8. Arquivos Atuais em data/processed/

```
data/processed/
├── 01_resumo/          11 arquivos — 16 KB
│   ├── 01_resumo_00_index.json
│   ├── 01_resumo_k00_kpis.json
│   ├── 01_resumo_r01_por_mes.csv         ← GL tendência mensal ✓
│   ├── 01_resumo_r02_por_negocio.csv     ← HL por negócio ✓
│   ├── 01_resumo_r03_top_categoria.csv   ← T top CAT2 ✓
│   ├── 01_resumo_r04_top_fornecedor.csv  ← T top fornecedores ✓
│   ├── 01_resumo_r05_por_uf.csv          ← HL por UF ✓
│   ├── 01_resumo_r06_geo_nne.csv         ← HL geo N/NE ✓
│   ├── 01_resumo_r07_geo_sse.csv         ← HL geo S/SE ✓
│   ├── 01_resumo_r08_por_filial.csv      ← T por filial ✓ (sem CMV)
│   └── 01_resumo_r09_cat2_por_uf.csv    ← MX heatmap ✓
│
├── 02_oportunidade/    5 arquivos — 47 KB
│   ├── 02_oportunidade_r01_tabela_principal.csv  ← TE priorizada ✓
│   ├── 02_oportunidade_r02_por_categoria.csv     ← GB por CAT2 ✓
│   └── 02_oportunidade_r03_por_uf.csv            ← HL por UF ✓
│   [FALTA: r04 matriz prioridade, r05 por tipo]
│
├── 03_categoria/       4 arquivos — 169 KB
│   ├── 03_categoria_r01_hierarquia.csv      ← drilldown CAT1-5 ✓
│   ├── 03_categoria_r02_cat2_por_mes.csv    ← GL séries ✓
│   └── 03_categoria_r03_cat2_por_uf.csv    ← MX heatmap ✓
│   [FALTA: r04 top fornecedor, r05 top produto por cat]
│
├── 04_filial/          6 arquivos — 43 KB
│   ├── 04_filial_r01_ranking.csv              ← HL ranking ✓ (sem CMV)
│   ├── 04_filial_r02_filial_negocio.csv       ← MX heatmap ✓
│   ├── 04_filial_r03_top3_por_mes.csv         ← GL top 3 ✓
│   └── 04_filial_r04_por_categoria.csv        ← T filial×cat ✓
│   [FALTA: r05 por fornecedor, CMV em r01, 3 KPIs]
│
├── 05_estoque/         1 arquivo — BLOQUEADO
│
├── 06_fornecedor/      4 arquivos — 371 KB
│   ├── 06_fornecedor_r01_tabela_principal.csv  ← TE principal ✓
│   └── 06_fornecedor_r02_por_categoria.csv     ← T por cat ✓
│   [FALTA: detail rows on-demand via NL-SQL]
│
├── 07_produto/         4 arquivos — 20 KB
│   ├── 07_produto_r01_tabela_principal.csv  ← TE com PMP série ✓
│   ├── 07_produto_r02_pmp_por_categoria.csv ← T PMP por cat ✓
│   ├── 07_produto_r03_top_inflacao.csv      ← HL top inflação ✓
│   └── 07_produto_r04_top_deflacao.csv      ← HL top deflação ✓
│   [FALTA: 4 KPIs, cotações por produto, UF por produto]
│
├── 08_cotacao/         8 arquivos — 101 KB
│   ├── 08_cotacao_r01_cobertura_por_mes.csv      ← GE empilhado ✓
│   ├── 08_cotacao_r02_cobertura_por_curva.csv    ← MX curva×cot ✓
│   ├── 08_cotacao_r03_cobertura_por_cat_mes.csv  ← GL cat×mês ✓
│   ├── 08_cotacao_r04_cobertura_por_uf.csv       ← T por UF ✓
│   ├── 08_cotacao_r05_min_cotacao_fornecedor.csv ← T MIN forn ✓
│   └── 08_cotacao_r06_relatorio.csv              ← T relatório ✓
│   [FALTA: r07 consulta preços, r08 por produto, r09 matriz mes, r10 ≤3 concorrentes]
│
├── 09_impacto/         6 arquivos — 21 KB
│   ├── 09_impacto_r01_por_mes.csv                     ← GB por mês ✓
│   ├── 09_impacto_r02_por_uf.csv                      ← HL por UF ✓
│   ├── 09_impacto_r03_top_id.csv                      ← T top IDs ✓
│   └── 09_impacto_r04_forn_mais_barato_nao_escolhido.csv ← T ✓
│   [FALTA: r05 produto×MIN COT]
│
├── 10_inflacao/        6 arquivos — 24 KB
│   ├── 10_inflacao_r01_por_cat_mes.csv   ← GL cat×mês% ✓
│   ├── 10_inflacao_r02_por_mes_rs.csv    ← GB mês R$ ✓
│   ├── 10_inflacao_r03_por_uf.csv        ← T por UF ✓
│   ├── 10_inflacao_r04_por_categoria.csv ← T nacional ✓
│   ├── 10_inflacao_r05_top_produto.csv   ← HL top inflação ✓
│   └── 10_inflacao_r06_top_deflacao.csv  ← HL top deflação ✓
│   [FALTA: r07 por fornecedor, r08 produto×categoria]
│
├── 11_fiscal/          1 arquivo — BLOQUEADO
│
├── 12_financeiro/      6 arquivos — 84 KB
│   ├── 12_financeiro_r01_aging.csv              ← T aging ✓
│   ├── 12_financeiro_r02_por_fornecedor.csv     ← T por forn ✓
│   ├── 12_financeiro_r03_timeline_semanal.csv   ← GB semanal ✓
│   └── 12_financeiro_r04_saldo_semanal_2026.csv ← T saldo ✓
│   [QUASE COMPLETO — falta "Em negociação"]
│
├── 13_adiantamento/    8 arquivos — 10 KB
│   ├── 13_adiantamento_r01_funil.csv          ← FU funil ✓
│   ├── 13_adiantamento_r02_por_empresa.csv    ← HL empresa ✓
│   ├── 13_adiantamento_r03_por_mes.csv        ← GL por mês ✓
│   ├── 13_adiantamento_r04_por_uf.csv         ← HL por UF ✓
│   ├── 13_adiantamento_r05_por_categoria.csv  ← T por cat ✓
│   └── 13_adiantamento_r06_por_fornecedor.csv ← T por forn ✓
│   [FALTA: tabela detalhada com nota vinculada — ADIANTAMENTO_NFE]
│
├── 14_servico/         6 arquivos — 7 KB
│   ├── 14_servico_r01_por_uf.csv        ← HL por UF ✓
│   ├── 14_servico_r02_por_mes.csv       ← GB por mês ✓
│   ├── 14_servico_r03_por_categoria.csv ← T por cat ✓
│   └── 14_servico_r04_por_fornecedor.csv ← T fornecedores ✓
│   [FALTA: r05 por CAT5, 3 KPIs]
│
└── 15_dados/           4 arquivos — 2 KB
    ├── 15_dados_r01_status_fontes.csv    ← T status ✓
    └── 15_dados_r02_fila_saneamento.csv  ← T saneamento ✓
    [FALTA: alertas e workspace APURAÇÃO no inventário]
```

---

## 9. Decisões de Arquitetura Confirmadas

1. **Detail row Fornecedor 360** → dados on-demand via módulo NL-SQL (não CSV estático)
2. **Alertas executivos (AL)** → lógica de regras no `pipeline/build.py` (não dados)
3. **Pivotagem de gráficos multi-série** → responsabilidade do dashboard JS (não do transform)
4. **Dados em formato longo** → padrão adotado; dashboard JS faz pivot quando necessário
5. **05_estoque e 11_fiscal** → implementar na próxima fase após resolver dependências

---

*Documento gerado em 2026-06-01. Atualizar após cada ciclo de melhorias no transform.py.*
