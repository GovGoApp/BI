# Inventário Zoho Analytics — Workspaces e Views

Gerado em: 2026-05-27.

Todos os workspaces e views acessíveis pelo token configurado em `zoho/zoho.env`.

---

## Resumo geral

| Métrica | Valor |
|---|---:|
| Organizações acessíveis | 2 |
| Workspaces acessíveis | 10 |
| Views totais | 561 |

## Organizações

| Org ID | Organização | Papel |
|---|---|---|
| 803942150 | hdalazoana | Account Admin |
| 703842975 | BI - Business Intelligence | Organization Admin |

---

## Workspaces

| Workspace | Workspace ID | Views | Tables | QueryTable | Pivot | AnalysisView | Dashboard |
|---|---:|---:|---:|---:|---:|---:|---:|
| APURAÇÃO DE RESULTADOS | 2130260000006068011 | 129 | 27 | 16 | 46 | 32 | 7 |
| FECHAMENTO 2021 | 2130260000004803019 | 1 | 1 | 0 | 0 | 0 | 0 |
| FINANCEIRO | 2130260000001506557 | 60 | 17 | 7 | 23 | 10 | 3 |
| HORTCLEAN | 2130260000010574886 | 66 | 16 | 16 | 18 | 14 | 2 |
| OTMA | 2130260000010747001 | 96 | 20 | 28 | 33 | 14 | 1 |
| PLANEJAMENTO | 2130260000000004001 | 0 | 0 | 0 | 0 | 0 | 0 |
| RH | 2130260000018297462 | 34 | 9 | 0 | 3 | 20 | 2 |
| **SUPRIMENTOS** | **2130260000001511306** | **165** | **21** | **32** | **72** | **31** | **8** |
| UNIFARMA | 2130260000013168005 | 7 | 4 | 1 | 1 | 1 | 0 |
| Zoho Analytics Audits | 2130260000001157852 | 3 | 2 | 0 | 1 | 0 | 0 |

---

## Workspace SUPRIMENTOS — detalhamento

**Workspace ID:** `2130260000001511306`
**Org ID:** `703842975` (BI - Business Intelligence)

### Dashboards (8)

| Dashboard ID | Nome |
|---:|---|
| 2130260000025999353 | PAINEL RESUMO |
| 2130260000026190795 | PAINEL FORNECEDOR |
| 2130260000026094095 | PAINEL COTAÇÃO |
| 2130260000026129868 | PAINEL INFLAÇÃO |
| 2130260000026467294 | PAINEL ADIANTAMENTO |
| 2130260000026628642 | PAINEL CP |
| 2130260000027116081 | PAINEL PRODUTOS |
| 2130260000026058741 | PAINEL SERVIÇOS |

### QueryTables principais (32)

| View ID | Nome | Linhas |
|---:|---|---:|
| 2130260000025181862 | NFE | 239.694 |
| 2130260000025494206 | ENTRADA DE NOTAS - [TODAS] | 238.866 |
| 2130260000025185218 | COT | 159.886 |
| 2130260000027214968 | NF COM ITENS - CONSOLIDADO | 118.176 |
| 2130260000026132374 | INFLAÇÃO | 115.190 |
| 2130260000025577131 | PMP_ID | 115.190 |
| 2130260000025808066 | PMP_ID_INF | 115.190 |
| 2130260000025675146 | COT_MIN_FORN | 66.311 |
| 2130260000026094963 | NUM_COT | 66.491 |
| 2130260000025577012 | PMP_PROD | — |
| 2130260000025859008 | PMP_ID_INF_12 | — |
| 2130260000025859434 | PMP_PROD_INF_12 | — |
| 2130260000025494002 | CURVA FORN - TODAS | 1.642 |
| 2130260000025185715 | CURVA ID - TODAS | — |
| 2130260000025423006 | CURVA PROD - TODAS | — |
| 2130260000028973002 | CURVA ABC FORN - TOTAL | — |
| 2130260000026747005 | CP_MOV | — |
| 2130260000026747561 | CP_SALDO_2026 | — |
| 2130260000026727012 | CP_SEMANA | — |
| 2130260000026349219 | ADIANTAMENTO_NFE | — |
| 2130260000026362009 | AD_v3 | — |
| 2130260000025890015 | FAT_SUP | — |

### Tables principais (21)

| View ID | Nome | Linhas |
|---:|---|---:|
| 2130260000026616007 | CP | 116.933 |
| 2130260000025183360 | COT - IDEAL | 113.960 |
| 2130260000025181004 | NFE - IDEAL | 163.759 |
| 2130260000027214002 | NF COM ITENS - IDEAL | 78.466 |
| 2130260000026457002 | NF ADT - IDEAL | 81.666 |
| 2130260000025580155 | FILIAIS | — |
| 2130260000025580003 | FILIAIS_SUPPLY | — |
| 2130260000026003056 | FILIAIS_DRO | — |
| 2130260000026003474 | FILIAIS_NEW | — |
| 2130260000026610007 | TODAS - CONTAS A PAGAR | — |

### AnalysisViews (31) — seleção

| View ID | Nome |
|---:|---|
| 2130260000026255087 | IMPACTO |
| 2130260000026086907 | IMPACTO por COTAÇÃO |
| 2130260000026108622 | CONTAGEM de COTAÇÕES |
| 2130260000027193227 | CONTAGEM de COTAÇÕES por ABC |
| 2130260000026108070 | CONTAGEM DE COTAÇÕES por CAT |
| 2130260000027193061 | CONTAGEM de COTAÇÕES por UF |
| 2130260000026142820 | INFLAÇÃO POR CAT |
| 2130260000026256880 | INFLAÇÃO por MES por CAT - % |
| 2130260000026255116 | INFLAÇÃO por MES por CAT - R$ |
| 2130260000026062330 | SERVIÇOS |
| 2130260000026072712 | DESPESAS FIN |

---

## Workspace APURAÇÃO DE RESULTADOS

**Workspace ID:** `2130260000006068011`

Contém dados de estoque por filial. Usado na aba **Estoque** do BI.

Dashboards relevantes:
- `PAINEL REUNIÃO 2026` (2130260000014795772)
- `ANALÍTICO` (2130260000007085384)

Pivots de estoque: `ANALISE DE ESTOQUE - IDEAL`, `ANALISE DE ESTOQUE - MELHOR`, `ANALISE DE ESTOQUE - POMME VITA`

---

## Como usar o inventário

Para descobrir o `view_id` de uma fonte desconhecida:

```powershell
python zoho/client.py --env-file zoho/zoho.env views
```

Para exportar uma view específica:

```powershell
python zoho/client.py --env-file zoho/zoho.env export-view --view-id VIEW_ID --out data/raw/nome.csv
```
